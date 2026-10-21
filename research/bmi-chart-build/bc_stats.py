#!/usr/bin/env python3
"""US adults on the BMI chart, CDC NHANES August 2021-August 2023 (CMB-015, /bmi-chart/).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: adults aged 20 and over with a measured BMI and an exam weight; pregnant women excluded, as NCHS excludes them.
Weights: MEC exam weights (WTMEC2YR). BMI as CDC records it (one decimal); waist BMXWAIST and height BMXHT in cm.

Results:
1. The share of US adults in each CDC BMI category, for all adults, men and women, each with a 95% confidence interval
   (Taylor linearisation, strata SDMVSTRA x PSUs SDMVPSU, 15 design df, as in CMB-013 and CMB-014).
2. The share with a BMI under 20 (FAQ "Is 20 BMI too skinny?").
3. The share whose measured height rounds to a whole inch from 4'10" to 6'6" (the chart's rows).
4. The 2026 American Diabetes Association obesity thresholds applied to the same adults (Standards of Care in
   Overweight and Obesity-2026, recommendations 3.3a and 3.3b): non-Asian background, obesity at BMI >= 30, or BMI >= 25
   with a waist-to-height ratio >= 0.5 or a waist >= 88 cm (women) / 102 cm (men); Asian background (NHANES: non-Hispanic
   Asian, RIDRETH3 = 6), BMI >= 27.5, or BMI >= 23 with a ratio >= 0.5 or a waist >= 80 cm (women) / 90 cm (men).
   Adults whose class depends on a waist that was not measured are left out of the comparison, and the BMI-only share is
   computed on the same adults. Also: the share of adults with a BMI of 25 to 29.9 whose waist is at least half their
   height.
5. The dots on the page's "US adults on the chart" figure: 600 adults drawn with probability proportional to their exam
   weight (systematic sampling on a shuffled list, fixed seed), so the cloud stands for the US adult population.

The script stops unless it reproduces NCHS's published crude rates (Data Brief 508: obesity 40.3%, men 39.2%, women
41.3%; severe obesity 9.4%, 6.7%, 12.1%; Health E-Stat 119 / CMB-012: underweight 1.6%, overweight 32.1%), the healthy
shares CMB-013 published (26.0% / 24.0% / 28.1%) and the women's 2026 ADA result CMB-014 published (69.4% vs 41.8%).

usage: python3 bc_stats.py RAW_DIR HEALTHY_STATS_JSON WOMEN_STATS_JSON OUT_JSON
"""
import sys, json
import numpy as np
import pandas as pd

raw, hs_path, ws_path, out = sys.argv[1:5]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
WAIST = D.BMXWAIST
WHTR = D.BMXWAIST / D.BMXHT
adults = (D.RIDAGEYR >= 20) & (W > 0) & B.notna() & ~(D.RIDEXPRG == 1)
MEN, WOMEN = D.RIAGENDR == 1, D.RIAGENDR == 2
GROUPS = {"all": adults, "men": adults & MEN, "women": adults & WOMEN}
CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30),
        "class_1": (B >= 30) & (B < 35), "class_2": (B >= 35) & (B < 40), "class_3": B >= 40, "obesity": B >= 30}

assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314                                   # t quantile, 0.975, 15 df


def z_of(dom, cond):
    x = float(W[dom].sum()); p = float(W[dom & cond].sum()) / x
    return (W * dom * (cond.astype(float) - p) / x), p


def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5


def est(dom, cond):
    cond = cond.fillna(False).astype(bool)
    z, p = z_of(dom, cond); se = se_of(z)
    return {"pct": round(100 * p, 1), "ci95": [round(100 * (p - T975 * se), 1), round(100 * (p + T975 * se), 1)],
            "n": int(dom.sum())}


def diff(dom, cond_a, cond_b):
    """Paired difference of two shares in the same adults (a - b), with its 95% CI."""
    za, pa = z_of(dom, cond_a); zb, pb = z_of(dom, cond_b); se = se_of(za - zb)
    return {"diff": round(100 * (pa - pb), 1),
            "ci95": [round(100 * (pa - pb - T975 * se), 1), round(100 * (pa - pb + T975 * se), 1)]}


def diff_dom(dom_a, dom_b, cond):
    za, pa = z_of(dom_a, cond); zb, pb = z_of(dom_b, cond); se = se_of(za - zb)
    return {"diff": round(100 * (pa - pb), 1),
            "ci95": [round(100 * (pa - pb - T975 * se), 1), round(100 * (pa - pb + T975 * se), 1)]}


res = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); adults aged 20+, pregnant women excluded",
       "method": "WTMEC2YR-weighted shares; 95% CI by Taylor linearisation (SDMVSTRA x SDMVPSU, 15 df, t = 2.1314)",
       "design": {"strata": 15, "psus": 30, "df": 15, "t975": T975}}

# 1. Categories for all adults, men and women.
res["categories"] = {}
for g, dom in GROUPS.items():
    res["categories"][g] = {c: est(dom, m) for c, m in CATS.items()}
    res["categories"][g]["n"] = int(dom.sum())
res["sex_differences"] = {"obesity_women_minus_men": diff_dom(GROUPS["women"], GROUPS["men"], CATS["obesity"]),
                          "class_3_women_minus_men": diff_dom(GROUPS["women"], GROUPS["men"], CATS["class_3"]),
                          "healthy_women_minus_men": diff_dom(GROUPS["women"], GROUPS["men"], CATS["healthy"])}

# 2. BMI under 20.
res["bmi_under_20"] = {g: est(dom, B < 20) for g, dom in GROUPS.items()}

# 3. Heights the chart covers: measured height that rounds to a whole inch from 58 (4'10") to 78 (6'6").
HIN = D.BMXHT / 2.54
res["height_on_chart"] = {g: est(dom, (HIN >= 57.5) & (HIN < 78.5)) for g, dom in GROUPS.items()}
res["height_below_chart"] = {g: est(dom, HIN < 57.5) for g, dom in GROUPS.items()}
res["height_above_chart"] = {g: est(dom, HIN >= 78.5) for g, dom in GROUPS.items()}

# 4. ADA 2026 thresholds against BMI alone, same adults.
asian = D.RIDRETH3 == 6
cut_na = np.where(WOMEN, 88.0, 102.0)          # non-Asian waist line, cm
cut_as = np.where(WOMEN, 80.0, 90.0)           # Asian waist line, cm
central_na = (WHTR >= 0.5) | (WAIST >= cut_na)
central_as = (WHTR >= 0.5) | (WAIST >= cut_as)
known_w = WAIST.notna()
ada_ob = ((~asian & ((B >= 30) | ((B >= 25) & central_na))) | (asian & ((B >= 27.5) | ((B >= 23) & central_as))))
ada_ob = ada_ob.fillna(False).astype(bool)
decided_by_bmi = (~asian & ((B >= 30) | (B < 25))) | (asian & ((B >= 27.5) | (B < 23)))
res["ada2026"] = {"rule": "non-Asian: BMI>=30, or BMI>=25 and (WHtR>=0.5 or waist>=88 cm women / 102 cm men); Asian "
                          "(RIDRETH3=6): BMI>=27.5, or BMI>=23 and (WHtR>=0.5 or waist>=80 cm women / 90 cm men). Adults "
                          "whose class needs an unmeasured waist are left out."}
for g, dom in GROUPS.items():
    known = dom & (decided_by_bmi | known_w)
    moved = known & ada_ob & ~(B >= 30)
    assert not (known & ~ada_ob & (B >= 30)).any()              # nobody leaves obesity under the 2026 rule
    res["ada2026"][g] = {
        "n": int(known.sum()), "n_left_out": int((dom & ~known).sum()),
        "obesity_ada": est(known, ada_ob), "obesity_bmi_only": est(known, B >= 30),
        "difference": diff(known, ada_ob, B >= 30),
        "parts_pts": {"nonasian_25_29_9": round(100 * float(W[moved & ~asian].sum() / W[known].sum()), 1),
                      "asian": round(100 * float(W[moved & asian].sum() / W[known].sum()), 1)},
        # adults with a BMI of 25-29.9 and a measured waist: waist at least half the height
        "bmi25_30_whtr_05": est(dom & (B >= 25) & (B < 30) & known_w, WHTR >= 0.5),
    }

# 5. The figure's dots: 600 adults, probability proportional to exam weight (systematic PPS on a shuffled list).
rng = np.random.default_rng(20261016)
pool = D[adults & D.BMXHT.notna() & D.BMXWT.notna()].copy()
pool = pool.iloc[rng.permutation(len(pool))]
cw = pool.WTMEC2YR.cumsum().to_numpy(); total = cw[-1]; k = 600
assert pool.WTMEC2YR.max() < total / k                         # every adult's chance stays below 1
start = rng.uniform(0, total / k)
picks = np.searchsorted(cw, start + np.arange(k) * total / k)
dots = pool.iloc[picks]
assert dots.SEQN.nunique() == k
res["dots"] = {"n": k, "seed": 20261016, "method": "systematic PPS by WTMEC2YR on a shuffled list",
               "points": [[round(float(h) / 2.54, 1), round(float(w) * 2.2046226218), int(s)]
                          for h, w, s in zip(dots.BMXHT, dots.BMXWT, dots.RIAGENDR)]}

# Checks: NCHS crude rates, the CMB-013 healthy shares and the CMB-014 women's ADA result.
C = res["categories"]
HS = json.load(open(hs_path))["groups"]
WS = json.load(open(ws_path))["ada2026"]
checks = {"obesity_all": (C["all"]["obesity"]["pct"], 40.3), "obesity_men": (C["men"]["obesity"]["pct"], 39.2),
          "obesity_women": (C["women"]["obesity"]["pct"], 41.3), "class3_all": (C["all"]["class_3"]["pct"], 9.4),
          "class3_men": (C["men"]["class_3"]["pct"], 6.7), "class3_women": (C["women"]["class_3"]["pct"], 12.1),
          "underweight_all": (C["all"]["underweight"]["pct"], 1.6), "overweight_all": (C["all"]["overweight"]["pct"], 32.1),
          "ada_women_n": (res["ada2026"]["women"]["n"], WS["n"]),
          "ada_women_ada": (res["ada2026"]["women"]["obesity_ada"]["pct"], WS["obesity_ada"]["pct"]),
          "ada_women_bmi": (res["ada2026"]["women"]["obesity_bmi_only"]["pct"], WS["obesity_bmi_only"]["pct"])}
for g in ("all", "men", "women"):
    checks[f"healthy_{g}"] = (C[g]["healthy"]["pct"], HS[g]["all_ages"]["healthy"])
    assert C[g]["n"] == HS[g]["all_ages"]["n"], (g, C[g]["n"], HS[g]["all_ages"]["n"])
for k_, (ours, ref) in checks.items():
    assert ours == ref, f"{k_}: ours {ours} vs {ref}"
for g in C:
    s = sum(C[g][c]["pct"] for c in ("underweight", "healthy", "overweight", "class_1", "class_2", "class_3"))
    assert abs(s - 100) <= 0.3, (g, s)
res["checks"] = {k_: {"ours": o, "reference": r} for k_, (o, r) in checks.items()}
json.dump(res, open(out, "w"), indent=1)
for g in C:
    print(g, {c: C[g][c]["pct"] for c in CATS}, "n", C[g]["n"])
print("ci", {g: {c: C[g][c]["ci95"] for c in CATS} for g in C})
print("sex differences", json.dumps(res["sex_differences"]))
print("bmi<20", json.dumps(res["bmi_under_20"]))
print("height on chart", json.dumps(res["height_on_chart"]), json.dumps(res["height_below_chart"]), json.dumps(res["height_above_chart"]))
print("ada", json.dumps({g: {k_: v for k_, v in res["ada2026"][g].items()} for g in GROUPS}))
