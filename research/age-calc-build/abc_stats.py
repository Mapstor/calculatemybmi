#!/usr/bin/env python3
"""CMB-045 AGE-CALC: the numbers behind /age-bmi-calculator/ (our calculation from CDC NHANES August 2021-August 2023).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: adults aged 20 and over with a measured BMI and an exam weight; pregnant women excluded, as NCHS excludes
them (2,680 men and 3,249 women). Weights: MEC exam weights (WTMEC2YR). BMI as CDC records it (one decimal).

1. The rank curves (1st to 99th percentile of BMI) for women and men aged 20 and over and for ages 20-39, 40-59 and 60+,
   by the method of research/rank-curves/curves.py (weighted cumulative distribution over the distinct measured values,
   linear interpolation), stored at 4 decimals as the page script reads them. The women's curves and the two all-ages
   curves must equal research/rank-curves/curves.json, so this page ranks a woman as /women-bmi-calculator/ does and
   anyone as the homepage's women-only and men-only lines do. The men's age-group curves are new here.
2. The percentile table (5th to 95th) and mean for the same eight groups.
3. BMI by decade of age for each sex: n, mean (must equal research/average-weight/avgw_results.json, which reproduces
   NCHS Series 3 No. 50), 10th to 90th percentile, and the share in each CDC category with a 95% confidence interval
   (Taylor linearization, strata SDMVSTRA x PSUs SDMVPSU, 15 design df, t = 2.1314); the women's decades must equal
   research/women-calc-build/wbc_stats.json. The mean's interval is stored too: the page says the average is 25 or more
   in every decade only if every interval's low end is.
4. The differences the page states, each with its 95% interval (NHANES comparison rule: stated only when it excludes 0).
Round once (DEVLOG section 4): printed figures come from the unrounded estimate; keep() stores 4 decimals and stops if
that would change a printed figure.

usage: python3 research/age-calc-build/abc_stats.py RAW_DIR OUT_JSON
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

raw, out = sys.argv[1], sys.argv[2]
REPO = Path(__file__).resolve().parent.parent.parent
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
A = D.RIDAGEYR
adult = (A >= 20) & (W > 0) & B.notna()
SEX = {"women": adult & (D.RIAGENDR == 2) & ~(D.RIDEXPRG == 1), "men": adult & (D.RIAGENDR == 1)}
AGEGROUPS = {"20-39": (20, 39), "40-59": (40, 59), "60+": (60, 200)}
DECADES = {"20-29": (20, 29), "30-39": (30, 39), "40-49": (40, 49), "50-59": (50, 59), "60-69": (60, 69),
           "70-79": (70, 79), "80+": (80, 200)}                    # NHANES top-codes age at 80


def shown(x):
    return (f"{x:.1f}", int(x + 0.5), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    x = float(x)
    r = round(x, nd)
    assert shown(r) == shown(x), ("stored value would print differently", x, r)
    return r


def quantiles(dom, qs):
    m = dom & B.notna() & (W > 0)
    s = pd.DataFrame({"x": B[m].round(6), "w": W[m]}).groupby("x").w.sum().sort_index()
    F = np.cumsum(s.values) / s.values.sum()
    return [float(np.interp(q, F, s.index.values)) for q in qs], int(m.sum())


assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314


def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5


def zmean(dom):
    x = float(W[dom].sum())
    mu = float((W[dom] * B[dom]).sum()) / x
    return W * dom * (B.fillna(0) - mu) / x, mu


def zshare(dom, cond):
    x = float(W[dom].sum())
    p = float(W[dom & cond].sum()) / x
    return W * dom * (cond.astype(float) - p) / x, p


def est_share(dom, cond):
    z, p = zshare(dom, cond)
    se = se_of(z)
    return {"pct": keep(100 * p), "ci95": [keep(100 * (p - T975 * se)), keep(100 * (p + T975 * se))], "n": int(dom.sum())}


def est_mean(dom):
    z, mu = zmean(dom)
    se = se_of(z)
    return {"mean": keep(mu), "ci95": [keep(mu - T975 * se), keep(mu + T975 * se)]}


def diff(z1, v1, z2, v2, scale=1.0):
    se = se_of(z1 - z2) * scale
    d = (v1 - v2) * scale
    lo, hi = d - T975 * se, d + T975 * se
    return {"diff": keep(d), "ci95": [keep(lo), keep(hi)], "excludes_0": bool(lo > 0 or hi < 0)}


QS = [i / 100 for i in range(1, 100)]
TAB = {"p5": .05, "p10": .10, "p25": .25, "p50": .50, "p75": .75, "p90": .90, "p95": .95}
CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30), "obesity": B >= 30}
CURVES = json.loads((REPO / "research/rank-curves/curves.json").read_text())
AVGW = json.loads((REPO / "research/average-weight/avgw_results.json").read_text())
WBC = json.loads((REPO / "research/women-calc-build/wbc_stats.json").read_text())

R = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); adults aged 20+, pregnant women excluded",
     "method": "WTMEC2YR-weighted cumulative distribution over distinct BMIs, linear interpolation (curves.py); "
               "shares, means and differences with 95% CI by Taylor linearization (15 df, t = 2.1314)",
     "curves": {}, "groups": {}, "decades": {}, "differences": {}}


def group_doms():
    for sex, dom in SEX.items():
        yield f"{sex}", dom
        for g, (lo, hi) in AGEGROUPS.items():
            yield f"{sex}_{g}", dom & A.between(lo, hi)


def pct(q, b):                              # the page script's pct(): position on the curve, linear between percentiles
    if b <= q[0]:
        return 0.0
    if b >= q[98]:
        return 100.0
    for i in range(98):
        if b < q[i + 1]:
            return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0


def rank_shown(q, b):                       # the displayed rank: strictly lower (curve at b - 0.1), strictly higher
    lo, hi = pct(q, round(b * 10 - 1) / 10), 100 - pct(q, b)
    r = lambda x: 99 if x > 99 else int(x + 0.5)
    return r(lo), r(hi)


# 1-2. Curves and percentile tables; storing 4 decimals must change no displayed rank (BMI 10.0 to 80.0), as in curves.py.
for name, dom in group_doms():
    q99, n = quantiles(dom, QS)
    c = [round(x, 4) for x in q99]
    assert all(b > a for a, b in zip(c, c[1:])), f"{name}: the curve must rise strictly"
    moved = [b / 10 for b in range(100, 801) if rank_shown(q99, b / 10) != rank_shown(c, b / 10)]
    assert not moved, f"{name}: storing 4 decimals changes a displayed rank at BMI {moved[:5]}"
    qt, _ = quantiles(dom, list(TAB.values()))
    R["curves"][name] = c
    R["groups"][name] = {"n": n, **est_mean(dom), **{k: keep(v) for k, v in zip(TAB, qt)},
                         **{k: est_share(dom, m) for k, m in CATS.items()}}

OLD = {"women": "women", "men": "men", "women_20-39": "women_20_39", "women_40-59": "women_40_59", "women_60+": "women_60plus"}
for mine, theirs in OLD.items():
    assert R["curves"][mine] == CURVES[theirs]["p1_p99"], f"{mine}: differs from curves.json {theirs}"
    assert R["groups"][mine]["n"] == CURVES[theirs]["n"], mine
assert R["groups"]["women"]["n"] == 3249 and R["groups"]["men"]["n"] == 2680
for g in AGEGROUPS:
    w = WBC["table"][g]
    assert R["groups"][f"women_{g}"]["n"] == w["n"] and all(abs(R["groups"][f"women_{g}"][k] - w[k]) < 1e-9 for k in TAB), g
# Obesity by age group reproduces NCHS Data Brief 508 (registry nhanes-adult-obesity-2021-2023, Figure 1 data tables):
# women 36.8 / 47.4 / 39.6, men 34.3 / 45.4 / 38.0, all adults 35.5 / 46.4 / 38.9 at 20-39 / 40-59 / 60+.
DB508 = {"women": (36.8, 47.4, 39.6), "men": (34.3, 45.4, 38.0), "adults": (35.5, 46.4, 38.9)}
R["db508"] = {}
for sex, pub in DB508.items():
    base = SEX["women"] | SEX["men"] if sex == "adults" else SEX[sex]
    for (g, (lo, hi)), p in zip(AGEGROUPS.items(), pub):
        mine = est_share(base & A.between(lo, hi), CATS["obesity"])
        assert f"{mine['pct']:.1f}" == f"{p:.1f}", (sex, g, mine["pct"], p)
        R["db508"][f"{sex}_{g}"] = mine
assert int((SEX["women"] | SEX["men"]).sum()) == 5929             # Data Brief 508: "5,929 adults age 20 and older"

# 3. Decades.
for sex, dom0 in SEX.items():
    R["decades"][sex] = {}
    for d, (lo, hi) in DECADES.items():
        dom = dom0 & A.between(lo, hi)
        q, n = quantiles(dom, [.10, .25, .50, .75, .90])
        ref = AVGW[sex]["age"][d.replace("-", "–")]["bmi"]
        m = est_mean(dom)
        assert n == ref["n"] and abs(m["mean"] - ref["mean"]) < 1e-3, (sex, d, n, ref)
        R["decades"][sex][d] = {"n": n, **m, **{k: keep(v) for k, v in zip(("p10", "p25", "p50", "p75", "p90"), q)},
                                **{c: est_share(dom, mm) for c, mm in CATS.items()}}
for d, v in WBC["decades"].items():
    mine = R["decades"]["women"][d]
    assert mine["n"] == v["n"] and all(abs(mine[k] - v[k]) < 1e-9 for k in ("p10", "p25", "p50", "p75", "p90")), d
    for c in CATS:
        assert abs(mine[c]["pct"] - v[c]["pct"]) < 1e-9 and mine[c]["ci95"] == v[c]["ci95"], (d, c)


# 4. Differences the page states.
def dom_of(sex, d):
    lo, hi = DECADES[d]
    return SEX[sex] & A.between(lo, hi)


def dom_grp(sex, g):
    lo, hi = AGEGROUPS[g]
    return SEX[sex] & A.between(lo, hi)


for sex in SEX:
    for a, b in (("50-59", "20-29"), ("40-49", "20-29"), ("80+", "50-59"), ("80+", "40-49"), ("80+", "70-79")):
        za, ma = zmean(dom_of(sex, a))
        zb, mb = zmean(dom_of(sex, b))
        R["differences"][f"{sex}_mean_{a}_minus_{b}"] = diff(za, ma, zb, mb)
    for a, b in (("20-29", "50-59"), ("20-29", "40-49")):
        za, pa = zshare(dom_of(sex, a), CATS["healthy"])
        zb, pb = zshare(dom_of(sex, b), CATS["healthy"])
        R["differences"][f"{sex}_healthy_{a}_minus_{b}"] = diff(za, pa, zb, pb, 100.0)
    # median by age group: the page states only the medians, so it needs no difference test; the mean by age group
    # (40-59 against 20-39) is recorded for the method note
    za, ma = zmean(dom_grp(sex, "40-59"))
    zb, mb = zmean(dom_grp(sex, "20-39"))
    R["differences"][f"{sex}_mean_40-59_minus_20-39"] = diff(za, ma, zb, mb)
# women against men in the same decade (the page compares their averages only where the interval excludes 0)
for d in DECADES:
    za, ma = zmean(dom_of("women", d))
    zb, mb = zmean(dom_of("men", d))
    R["differences"][f"women_minus_men_mean_{d}"] = diff(za, ma, zb, mb)

json.dump(R, open(out, "w"), indent=1)
for g, t in R["groups"].items():
    print(g, t["n"], "median", f"{t['p50']:.1f}", "p25-p75", f"{t['p25']:.1f}-{t['p75']:.1f}", "mean", f"{t['mean']:.1f}",
          "healthy", f"{t['healthy']['pct']:.1f}", "obesity", f"{t['obesity']['pct']:.1f}")
for sex in SEX:
    for d, t in R["decades"][sex].items():
        print(sex, d, t["n"], "mean", f"{t['mean']:.1f}", [f"{x:.2f}" for x in t["ci95"]], "median", f"{t['p50']:.1f}",
              "mid", f"{t['p25']:.1f}-{t['p75']:.1f}", "healthy", f"{t['healthy']['pct']:.1f}", "obesity",
              f"{t['obesity']['pct']:.1f}")
for k, v in R["differences"].items():
    print(k, f"{v['diff']:.2f}", [f"{x:.2f}" for x in v["ci95"]], "excludes 0" if v["excludes_0"] else "INCLUDES 0")
