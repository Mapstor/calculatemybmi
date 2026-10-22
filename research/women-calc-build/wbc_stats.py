#!/usr/bin/env python3
"""CMB-017 WOMEN-CALC: the numbers behind /women-bmi-calculator/ (our calculation from CDC NHANES August 2021-August 2023).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: women aged 20 and over with a measured BMI and an exam weight; pregnant women excluded, as NCHS excludes
them (3,249 women). Weights: MEC exam weights (WTMEC2YR). BMI as CDC records it (one decimal).

1. The rank curves (1st to 99th percentile of BMI) for all women and for ages 20-39, 40-59 and 60+, by the homepage's
   method (research/home-build/home_stats.py: weighted cumulative distribution over the distinct measured values, linear
   interpolation), stored at 2 decimals as the page script reads them. The all-women curve must equal the homepage's
   women-only curve, so both pages rank a woman the same way.
2. The percentile table (5th to 95th) for the same four groups, and BMI by decade of age (10th to 90th percentile,
   mean, n) for the figure; the decade means must equal research/average-weight/avgw_results.json (which reproduces
   NCHS Series 3 No. 50).
3. The share of women in each CDC category by decade, with 95% confidence intervals (Taylor linearization, strata
   SDMVSTRA x PSUs SDMVPSU, 15 design df, t = 2.1314, as research/chart-women-build/bcw_stats.py). The page prints no
   difference between decades unless its interval excludes 0; the age-group shares stay those of bcw_stats.json.
Round once (DEVLOG section 4): printed figures come from the unrounded estimate; keep() stores 4 decimals and stops if
that would change a printed figure.

usage: python3 wbc_stats.py RAW_DIR HOME_STATS_JSON AVGW_RESULTS_JSON BCW_STATS_JSON OUT_JSON
"""
import sys, json
import numpy as np, pandas as pd

raw, home_p, avgw_p, bcw_p, out = sys.argv[1:6]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
A = D.RIDAGEYR
women = (A >= 20) & (W > 0) & B.notna() & (D.RIAGENDR == 2) & ~(D.RIDEXPRG == 1)
GROUPS = {"all": women, "20-39": women & A.between(20, 39), "40-59": women & A.between(40, 59), "60+": women & (A >= 60)}
DECADES = {"20-29": (20, 29), "30-39": (30, 39), "40-49": (40, 49), "50-59": (50, 59), "60-69": (60, 69),
           "70-79": (70, 79), "80+": (80, 200)}                    # NHANES top-codes age at 80


def shown(x):
    return (f"{x:.1f}", int(x + 0.5), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    x = float(x); r = round(x, nd)
    assert shown(r) == shown(x), ("stored value would print differently", x, r)
    return r


def quantiles(dom, qs):
    """The homepage's method: weighted cumulative distribution over distinct BMIs, linear interpolation."""
    m = dom & B.notna() & (W > 0)
    s = pd.DataFrame({"x": B[m].round(6), "w": W[m]}).groupby("x").w.sum().sort_index()
    F = np.cumsum(s.values) / s.values.sum()
    return [float(np.interp(q, F, s.index.values)) for q in qs], int(m.sum())


def mean(dom):
    m = dom & B.notna() & (W > 0)
    return float((W[m] * B[m]).sum() / W[m].sum())


assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314


def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5


def est(dom, cond):
    x = float(W[dom].sum()); p = float(W[dom & cond].sum()) / x
    se = se_of(W * dom * (cond.astype(float) - p) / x)
    return {"pct": keep(100 * p), "ci95": [keep(100 * (p - T975 * se)), keep(100 * (p + T975 * se))], "n": int(dom.sum())}


QS = [i / 100 for i in range(1, 100)]
TAB = {"p5": .05, "p10": .10, "p25": .25, "p50": .50, "p75": .75, "p90": .90, "p95": .95}
HOME = json.load(open(home_p))
AVGW = json.load(open(avgw_p))["women"]["age"]
BCW = json.load(open(bcw_p))

R = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); women aged 20+, pregnant women excluded",
     "method": "WTMEC2YR-weighted cumulative distribution over distinct BMIs, linear interpolation (home_stats.py); "
               "shares with 95% CI by Taylor linearization (15 df, t = 2.1314)",
     "curves": {}, "table": {}, "decades": {}}

# 1. Rank curves at 2 decimals (the page script's arrays) and the percentile table.
for g, dom in GROUPS.items():
    q99, n = quantiles(dom, QS)
    c = [round(x, 2) for x in q99]
    assert all(b > a for a, b in zip(c, c[1:])), f"{g}: the curve must rise strictly"
    qt, _ = quantiles(dom, list(TAB.values()))
    R["curves"][g] = c
    R["table"][g] = {"n": n, "mean": keep(mean(dom)), **{k: keep(v) for k, v in zip(TAB, qt)}}
assert R["curves"]["all"] == HOME["women"]["p1_p99"], "the all-women curve must equal the homepage's women-only curve"
assert R["table"]["all"]["n"] == HOME["women"]["bmi_n"] == 3249
for k in TAB:
    assert f"{R['table']['all'][k]:.1f}" == f"{HOME['women']['table'][k]:.1f}", (k, R["table"]["all"][k])

# 2. By decade: percentiles for the figure, the mean (must equal avgw_results.json) and the category shares.
CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30), "obesity": B >= 30}
for d, (lo, hi) in DECADES.items():
    dom = women & A.between(lo, hi)
    q, n = quantiles(dom, [.10, .25, .50, .75, .90])
    ref = AVGW[d.replace("-", "–")]["bmi"]
    assert n == ref["n"] and abs(mean(dom) - ref["mean"]) < 1e-9, (d, n, ref)
    R["decades"][d] = {"n": n, "mean": keep(mean(dom)), **{k: keep(v) for k, v in zip(("p10", "p25", "p50", "p75", "p90"), q)},
                       **{c: est(dom, m) for c, m in CATS.items()}}

# 2b. Differences between decades the page could state (NHANES comparison rule: only when the 95% CI excludes 0).
def zmean(dom):
    m = dom & B.notna() & (W > 0); x = float(W[m].sum()); mu = float((W[m] * B[m]).sum()) / x
    return (W * m * (B.fillna(0) - mu) / x), mu


def zshare(dom, cond):
    x = float(W[dom].sum()); p = float(W[dom & cond].sum()) / x
    return (W * dom * (cond.astype(float) - p) / x), p


def dec(d):
    lo, hi = DECADES[d]
    return women & A.between(lo, hi)


def diff(z1, v1, z2, v2, scale=1.0):
    se = se_of(z1 - z2) * scale; d = (v1 - v2) * scale
    lo, hi = d - T975 * se, d + T975 * se
    return {"diff": keep(d), "ci95": [keep(lo), keep(hi)], "excludes_0": bool(lo > 0 or hi < 0)}


R["decade_differences"] = {}
for a, b in (("50-59", "20-29"), ("80+", "50-59"), ("70-79", "50-59"), ("80+", "70-79"), ("80+", "60-69")):
    za, ma = zmean(dec(a)); zb, mb = zmean(dec(b))
    R["decade_differences"][f"mean_{a}_minus_{b}"] = diff(za, ma, zb, mb)
for a, b in (("20-29", "50-59"), ("80+", "50-59")):
    za, pa = zshare(dec(a), CATS["healthy"]); zb, pb = zshare(dec(b), CATS["healthy"])
    R["decade_differences"][f"healthy_{a}_minus_{b}"] = diff(za, pa, zb, pb, 100.0)

# 3. The age-group shares the page prints are bcw_stats.json's; recomputed here, they must agree.
for g in ("20-39", "40-59", "60+"):
    for c in ("healthy", "obesity"):
        mine = est(GROUPS[g], CATS[c])["pct"]
        assert f"{mine:.1f}" == f"{BCW['categories'][g][c]['pct']:.1f}", (g, c, mine)
mine = est(women, CATS["healthy"])["pct"]
assert f"{mine:.1f}" == f"{BCW['categories']['all_ages']['healthy']['pct']:.1f}"

json.dump(R, open(out, "w"), indent=1)
for g, t in R["table"].items():
    print(g, {k: (f"{v:.1f}" if isinstance(v, float) else v) for k, v in t.items()})
for d, t in R["decades"].items():
    print(d, t["n"], "median", f"{t['p50']:.1f}", "mean", f"{t['mean']:.1f}", "healthy", f"{t['healthy']['pct']:.1f}",
          t["healthy"]["ci95"], "obesity", f"{t['obesity']['pct']:.1f}", t["obesity"]["ci95"])
for k, v in R["decade_differences"].items():
    print(k, f"{v['diff']:.1f}", [f"{x:.1f}" for x in v["ci95"]], "excludes 0" if v["excludes_0"] else "INCLUDES 0")
