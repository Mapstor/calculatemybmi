#!/usr/bin/env python3
"""CMB-018 CHART-MEN: US men on the BMI chart (our calculation from CDC NHANES August 2021-August 2023).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: men aged 20 and over with a measured BMI and an exam weight (2,680 men). Weights: MEC exam weights (WTMEC2YR).
BMI as CDC records it (one decimal); waist BMXWAIST and height BMXHT in cm.

1. The share of men in each CDC category, all men and by age (20-39, 40-59, 60+), each with a 95% confidence interval
   (Taylor linearization, strata SDMVSTRA x PSUs SDMVPSU, 15 design df, t = 2.1314, as research/bmi-chart-build/
   bc_stats.py). The script stops unless it reproduces NCHS Data Brief 508 for men (obesity 39.2%; 34.3 / 45.4 / 38.0 at
   20-39 / 40-59 / 60+; severe obesity 6.7%; 6.1 / 9.2 / 4.3), the men's shares CMB-013 published
   (research/healthy-range-build/healthy_stats.json) and the men's figures on /bmi-chart/ (bc_stats.json).
2. Differences between age groups. The page states one only when its 95% CI excludes 0 (NHANES comparison rule).
3. Waist at the same BMI: the share of men with a waist of 102 cm (40.2 in) or more and with a waist at least half their
   height, in each BMI category (men with a measured waist and height).
4. The 2026 American Diabetes Association obesity thresholds applied to the same men, by bc_stats.py's rule (non-Asian:
   BMI >= 30, or >= 25 with waist-to-height >= 0.5 or waist >= 102 cm; Asian background, RIDRETH3 = 6: BMI >= 27.5, or >= 23
   with the ratio >= 0.5 or waist >= 90 cm; men whose class needs an unmeasured waist left out). Must equal bc_stats.json.
5. By measured height rounded to the nearest inch, 5'4" to 6'2" (the heights where 76 or more men were measured): the share
   with a BMI of 25 or more (asserted equal to compute.py's), and the weight quartiles compute.py published (asserted
   equal; since CMB-019 both use NCHS's 2.2046 lb per kg and the weighted CDF over distinct values). At 5'10" also the
   share in each category.

Round once (DEVLOG section 4): every printed figure comes from the unrounded estimate; keep() stores 4 decimals and stops if
storing would change a printed figure.

usage: python3 bcm_stats.py RAW_DIR HEALTHY_STATS_JSON BC_STATS_JSON AVGW_RESULTS_JSON OUT_JSON
"""
import sys, json
import numpy as np, pandas as pd

raw, hs_p, bc_p, avgw_p, out = sys.argv[1:6]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
A = D.RIDAGEYR
WAIST, HT = D.BMXWAIST, D.BMXHT
WHTR = WAIST / HT
LB = 2.2046                                  # NCHS's pounds per kilogram, as research/average-weight/compute.py (CMB-019)
D["wt_lb"] = D.BMXWT * LB
HIN = np.floor(HT / 2.54 + 0.5)                                    # nearest whole inch, as compute.py
men = (A >= 20) & (W > 0) & B.notna() & (D.RIAGENDR == 1)
GROUPS = {"all": men, "20-39": men & A.between(20, 39), "40-59": men & A.between(40, 59), "60+": men & (A >= 60)}
CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30),
        "class_1": (B >= 30) & (B < 35), "class_2": (B >= 35) & (B < 40), "class_3": B >= 40, "obesity": B >= 30}
assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314


def shown(x):
    return (f"{x:.1f}", int(x + 0.5), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    x = float(x); r = round(x, nd)
    assert shown(r) == shown(x), ("stored value would print differently", x, r)
    return r


def z_of(dom, cond):
    cond = cond.fillna(False).astype(bool)
    x = float(W[dom].sum()); p = float(W[dom & cond].sum()) / x
    return (W * dom * (cond.astype(float) - p) / x), p


def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5


def est(dom, cond):
    z, p = z_of(dom, cond); se = se_of(z)
    return {"pct": keep(100 * p), "ci95": [keep(100 * (p - T975 * se)), keep(100 * (p + T975 * se))], "n": int(dom.sum())}


def diff_dom(dom_a, dom_b, cond):
    za, pa = z_of(dom_a, cond); zb, pb = z_of(dom_b, cond); se = se_of(za - zb)
    d = 100 * (pa - pb); lo, hi = d - 100 * T975 * se, d + 100 * T975 * se
    return {"diff": keep(d), "ci95": [keep(lo), keep(hi)], "excludes_0": bool(lo > 0 or hi < 0)}


def diff_same(dom, cond_a, cond_b):
    """Paired difference of two shares in the same men (a - b)."""
    za, pa = z_of(dom, cond_a); zb, pb = z_of(dom, cond_b); se = se_of(za - zb)
    d = 100 * (pa - pb); lo, hi = d - 100 * T975 * se, d + 100 * T975 * se
    return {"diff": keep(d), "ci95": [keep(lo), keep(hi)], "excludes_0": bool(lo > 0 or hi < 0)}


def wq(var, dom, qs):
    """research/average-weight/compute.py's weighted quantiles since CMB-019: the weighted CDF over distinct values with
    linear interpolation (the homepage's method), which reproduces NCHS Series 3 No. 50 and doesn't depend on tie order."""
    m = dom & D[var].notna() & (W > 0)
    s = pd.DataFrame({"x": D.loc[m, var].round(6), "w": W[m]}).groupby("x").w.sum().sort_index()
    F = np.cumsum(s.values) / s.values.sum()
    return [float(np.interp(q, F, s.index.values)) for q in qs]


R = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); men aged 20 and over",
     "method": "WTMEC2YR-weighted shares; 95% CI by Taylor linearization (SDMVSTRA x SDMVPSU, 15 df, t = 2.1314)"}

# 1. Categories, all men and by age.
R["categories"] = {}
for g, dom in GROUPS.items():
    R["categories"][g] = {c: est(dom, m) for c, m in CATS.items()}
    R["categories"][g]["n"] = int(dom.sum())
C = R["categories"]
assert [C[g]["n"] for g in GROUPS] == [2680, 672, 762, 1246]
DB508 = {"obesity": {"all": 39.2, "20-39": 34.3, "40-59": 45.4, "60+": 38.0},
         "class_3": {"all": 6.7, "20-39": 6.1, "40-59": 9.2, "60+": 4.3}}
for c, ref in DB508.items():
    for g, v in ref.items():
        assert f"{C[g][c]['pct']:.1f}" == f"{v:.1f}", (c, g, C[g][c]["pct"], v)
HS = json.load(open(hs_p))["groups"]["men"]
for g, k in (("all", "all_ages"), ("20-39", "20-39"), ("40-59", "40-59"), ("60+", "60+")):
    for c in ("underweight", "healthy", "overweight", "obesity", "class_3"):
        assert f"{C[g][c]['pct']:.1f}" == f"{HS[k][c]:.1f}", (g, c)
    assert C[g]["n"] == HS[k]["n"]
    assert [f"{x:.1f}" for x in C[g]["healthy"]["ci95"]] == [f"{x:.1f}" for x in HS[k]["healthy_ci95"]], g
BC = json.load(open(bc_p))
for c in CATS:
    assert f"{C['all'][c]['pct']:.1f}" == f"{BC['categories']['men'][c]['pct']:.1f}", c
    assert [f"{x:.1f}" for x in C["all"][c]["ci95"]] == [f"{x:.1f}" for x in BC["categories"]["men"][c]["ci95"]], c

# 2. Differences between age groups (a - b).
R["age_differences"] = {}
PAIRS = {"obesity": (("40-59", "20-39"), ("40-59", "60+"), ("60+", "20-39")),
         "class_3": (("40-59", "20-39"), ("40-59", "60+"), ("20-39", "60+")),
         "healthy": (("20-39", "40-59"), ("20-39", "60+"), ("60+", "40-59")),
         "overweight": (("60+", "40-59"), ("60+", "20-39"), ("20-39", "40-59"))}
for c, pairs in PAIRS.items():
    for a, b in pairs:
        R["age_differences"][f"{c}_{a}_minus_{b}"] = diff_dom(GROUPS[a], GROUPS[b], CATS[c])

# 3. Waist at the same BMI category.
measured = men & WAIST.notna() & HT.notna()
R["waist"] = {"n_measured": int(measured.sum()), "by_bmi": {}}
for c in ("healthy", "overweight", "obesity"):
    dom = measured & CATS[c].fillna(False).astype(bool)
    R["waist"]["by_bmi"][c] = {"waist_102_plus": est(dom, WAIST >= 102), "whtr_05_plus": est(dom, WHTR >= 0.5)}
R["waist"]["all"] = {"waist_102_plus": est(measured, WAIST >= 102), "whtr_05_plus": est(measured, WHTR >= 0.5)}

# 4. The 2026 ADA thresholds against BMI alone, the same men (bc_stats.py's rule).
asian = D.RIDRETH3 == 6
central_na = (WHTR >= 0.5) | (WAIST >= 102.0)
central_as = (WHTR >= 0.5) | (WAIST >= 90.0)
ada_ob = ((~asian & ((B >= 30) | ((B >= 25) & central_na))) | (asian & ((B >= 27.5) | ((B >= 23) & central_as))))
ada_ob = ada_ob.fillna(False).astype(bool)
decided_by_bmi = (~asian & ((B >= 30) | (B < 25))) | (asian & ((B >= 27.5) | (B < 23)))
known = men & (decided_by_bmi | WAIST.notna())
moved = known & ada_ob & ~(B >= 30)
assert not (known & ~ada_ob & (B >= 30)).any()
R["ada2026"] = {"n": int(known.sum()), "n_left_out": int((men & ~known).sum()),
                "obesity_ada": est(known, ada_ob), "obesity_bmi_only": est(known, B >= 30),
                "difference": diff_same(known, ada_ob, B >= 30),
                "parts_pts": {"nonasian_25_29_9": keep(100 * float(W[moved & ~asian].sum() / W[known].sum())),
                              "asian": keep(100 * float(W[moved & asian].sum() / W[known].sum()))},
                "bmi25_30_whtr_05": est(men & (B >= 25) & (B < 30) & WAIST.notna(), WHTR >= 0.5),
                "bmi25_30_nonasian_central": est(men & ~asian & (B >= 25) & (B < 30) & WAIST.notna(), central_na)}
BA = BC["ada2026"]["men"]
A_ = R["ada2026"]
assert (A_["n"], A_["n_left_out"]) == (BA["n"], BA["n_left_out"])
for k in ("obesity_ada", "obesity_bmi_only", "bmi25_30_whtr_05"):
    assert f"{A_[k]['pct']:.1f}" == f"{BA[k]['pct']:.1f}", k
assert f"{A_['difference']['diff']:.1f}" == f"{BA['difference']['diff']:.1f}"
for k in ("nonasian_25_29_9", "asian"):
    assert f"{A_['parts_pts'][k]:.1f}" == f"{BA['parts_pts'][k]:.1f}", k

# 5. By measured height: men whose BMI is 25 or more, and the weight quartiles compute.py published.
AV = json.load(open(avgw_p))["men"]["height"]
ad_w = (A >= 20) & (W > 0) & ~(D.RIDEXPRG == 1) & (D.RIAGENDR == 1)  # compute.py's domain (weight, not BMI)
R["by_height"] = {}
for h in range(64, 75):
    dom = men & (HIN == h)
    q = wq("wt_lb", ad_w & (HIN == h), [.25, .5, .75])
    assert all(abs(a - b) < 6e-5 for a, b in zip(q, AV[str(h)]["q"])), (h, q, AV[str(h)]["q"])   # stored to 4 decimals
    b25 = est(dom, B >= 25)
    assert b25["n"] == AV[str(h)]["bmi25_plus"]["n"] and abs(b25["pct"] - AV[str(h)]["bmi25_plus"]["pct"]) < 6e-5, h
    R["by_height"][str(h)] = {"n": int(dom.sum()), "bmi25_plus": b25,
                              "weight_q": [keep(x) for x in q], "weight_mean": keep(AV[str(h)]["wt"]["mean"]),
                              "weight_n": AV[str(h)]["wt"]["n"]}
d70 = men & (HIN == 70)
R["at_70in"] = {c: est(d70, CATS[c]) for c in ("underweight", "healthy", "overweight", "obesity")}

json.dump(R, open(out, "w"), indent=1)
for g in GROUPS:
    print(g, {c: f"{C[g][c]['pct']:.1f}" for c in CATS}, "n", C[g]["n"])
for k, v in R["age_differences"].items():
    print(k, f"{v['diff']:.1f}", [f"{x:.1f}" for x in v["ci95"]], "excludes 0" if v["excludes_0"] else "INCLUDES 0")
print("waist", R["waist"]["n_measured"], {c: (f"{v['waist_102_plus']['pct']:.1f}", f"{v['whtr_05_plus']['pct']:.1f}")
                                           for c, v in R["waist"]["by_bmi"].items()})
print("ada", A_["n"], f"{A_['obesity_ada']['pct']:.1f}", f"{A_['obesity_bmi_only']['pct']:.1f}",
      f"{A_['difference']['diff']:.1f}", A_["parts_pts"], f"{A_['bmi25_30_nonasian_central']['pct']:.1f}")
for h, v in R["by_height"].items():
    print(h, v["n"], "BMI 25+", f"{v['bmi25_plus']['pct']:.1f}", [f"{x:.1f}" for x in v["bmi25_plus"]["ci95"]],
          "weight q", [f"{x:.1f}" for x in v["weight_q"]], "mean", f"{v['weight_mean']:.1f}")
print("5'10\"", {c: (f"{v['pct']:.1f}", [f"{x:.1f}" for x in v["ci95"]]) for c, v in R["at_70in"].items()})
