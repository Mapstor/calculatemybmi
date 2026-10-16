#!/usr/bin/env python3
"""US women on the BMI chart, CDC NHANES August 2021-August 2023 (CMB-014, /blog/bmi-chart-women/).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: women aged 20 and over with a measured BMI and an exam weight; pregnant women excluded, as NCHS excludes them.
Weights: MEC exam weights (WTMEC2YR). BMI as CDC records it (one decimal); waist BMXWAIST and height BMXHT in cm.

Three results:
1. The share of US women in each CDC BMI category, for all ages and for ages 20-39, 40-59 and 60+, each with a 95%
   confidence interval (Taylor linearisation, strata SDMVSTRA x PSUs SDMVPSU, 15 design df, as in CMB-013).
2. Waist at the same BMI: the share of women whose waist is 88 cm (35 in) or more, and whose waist-to-height ratio is
   0.5 or more, in each BMI category (women with a measured waist).
3. The 2026 American Diabetes Association obesity thresholds applied to the same women: obesity when BMI >= 30, or
   BMI >= 25 with a waist-to-height ratio >= 0.5 or a waist >= 88 cm; for women of Asian background (NHANES: non-Hispanic
   Asian, RIDRETH3 = 6) BMI >= 27.5, or BMI >= 23 with a ratio >= 0.5 or a waist >= 80 cm (Standards of Care in
   Overweight and Obesity-2026, recommendations 3.3a and 3.3b). Women whose class depends on a waist that was not
   measured are left out of this comparison, and the BMI-only share is computed on the same women.

The script stops unless the women's shares reproduce NCHS's published crude rates (Data Brief 508: obesity 41.3%, and
36.8% / 47.4% / 39.6% at ages 20-39 / 40-59 / 60+; severe obesity 12.1%, and 13.0% / 14.7% / 8.4%) and the healthy
shares CMB-013 published (healthy_stats.json: 28.1% / 33.8% / 23.9% / 26.5%). It also tests the age differences the
page could state (95% CI of each difference; the page states only those that exclude 0).

usage: python3 bcw_stats.py RAW_DIR HEALTHY_STATS_JSON OUT_JSON
"""
import sys, json
import pandas as pd

raw, hs_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
WAIST = D.BMXWAIST
WHTR = D.BMXWAIST / D.BMXHT
women = (D.RIDAGEYR >= 20) & (W > 0) & B.notna() & (D.RIAGENDR == 2) & ~(D.RIDEXPRG == 1)
AGES = {"20-39": (D.RIDAGEYR >= 20) & (D.RIDAGEYR <= 39), "40-59": (D.RIDAGEYR >= 40) & (D.RIDAGEYR <= 59),
        "60+": D.RIDAGEYR >= 60}
CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30),
        "class_1": (B >= 30) & (B < 35), "class_2": (B >= 35) & (B < 40), "class_3": B >= 40, "obesity": B >= 30}

# Sampling error: all exam-sample records stay in the design; a domain is a 0/1 weight multiplier.
assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314                                   # t quantile, 0.975, 15 df


def z_of(dom, cond):
    x = float(W[dom].sum()); p = float(W[dom & cond].sum()) / x
    return (W * dom * (cond.astype(float) - p) / x), p


def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5


def est(dom, cond):
    z, p = z_of(dom, cond); se = se_of(z)
    return {"pct": round(100 * p, 1), "ci95": [round(100 * (p - T975 * se), 1), round(100 * (p + T975 * se), 1)],
            "n": int(dom.sum())}


def diff(dom, cond_a, cond_b):
    """Paired difference of two shares in the same women (a - b), with its 95% CI."""
    za, pa = z_of(dom, cond_a); zb, pb = z_of(dom, cond_b); se = se_of(za - zb)
    return {"diff": round(100 * (pa - pb), 1),
            "ci95": [round(100 * (pa - pb - T975 * se), 1), round(100 * (pa - pb + T975 * se), 1)]}


def diff_dom(dom_a, dom_b, cond):
    """Difference of one share between two groups of women (a - b), with its 95% CI (same design, CMB-013 method)."""
    za, pa = z_of(dom_a, cond); zb, pb = z_of(dom_b, cond); se = se_of(za - zb)
    return {"diff": round(100 * (pa - pb), 1),
            "ci95": [round(100 * (pa - pb - T975 * se), 1), round(100 * (pa - pb + T975 * se), 1)]}


res = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); women aged 20+, pregnant women excluded",
       "method": "WTMEC2YR-weighted shares; 95% CI by Taylor linearisation (SDMVSTRA x SDMVPSU, 15 df, t = 2.1314)",
       "design": {"strata": 15, "psus": 30, "df": 15, "t975": T975}}

# 1. Categories, all ages and by age group.
res["categories"] = {}
for a, am in [("all_ages", women)] + [(k, women & v) for k, v in AGES.items()]:
    dom = am if a == "all_ages" else am
    res["categories"][a] = {c: est(dom, m) for c, m in CATS.items()}
    res["categories"][a]["n"] = int(dom.sum())

# Differences by age the page could state (it states only those whose 95% CI excludes 0).
Y, M_, O = women & AGES["20-39"], women & AGES["40-59"], women & AGES["60+"]
res["age_differences"] = {
    "healthy_20_39_minus_40_59": diff_dom(Y, M_, CATS["healthy"]),
    "healthy_20_39_minus_60_plus": diff_dom(Y, O, CATS["healthy"]),
    "healthy_60_plus_minus_40_59": diff_dom(O, M_, CATS["healthy"]),
    "obesity_40_59_minus_20_39": diff_dom(M_, Y, CATS["obesity"]),
    "obesity_40_59_minus_60_plus": diff_dom(M_, O, CATS["obesity"]),
    "class_3_20_39_minus_60_plus": diff_dom(Y, O, CATS["class_3"]),
    "class_3_40_59_minus_60_plus": diff_dom(M_, O, CATS["class_3"]),
}

# 2. Waist at the same BMI (women with a measured waist).
hasw = women & WAIST.notna()
res["waist"] = {"n_measured": int(hasw.sum()), "n_missing": int((women & WAIST.isna()).sum()), "by_bmi": {}}
for c in ("healthy", "overweight", "obesity"):
    dom = hasw & CATS[c]
    res["waist"]["by_bmi"][c] = {"waist_88_plus": est(dom, WAIST >= 88), "whtr_05_plus": est(dom, WHTR >= 0.5),
                                 "n": int(dom.sum())}
res["waist"]["all"] = {"waist_88_plus": est(hasw, WAIST >= 88), "whtr_05_plus": est(hasw, WHTR >= 0.5)}

# 3. ADA 2026 thresholds against BMI alone, same women.
asian = D.RIDRETH3 == 6
central_na = (WHTR >= 0.5) | (WAIST >= 88)          # non-Asian women: WHtR >= 0.5 or waist >= 88 cm
central_as = (WHTR >= 0.5) | (WAIST >= 80)          # Asian women: WHtR >= 0.5 or waist >= 80 cm
known_w = WAIST.notna()
ada_ob = (~asian & ((B >= 30) | ((B >= 25) & central_na))) | (asian & ((B >= 27.5) | ((B >= 23) & central_as)))
# A woman's ADA class is known when her BMI alone decides it, or her waist was measured.
decided_by_bmi = (~asian & ((B >= 30) | (B < 25))) | (asian & ((B >= 27.5) | (B < 23)))
known = women & (decided_by_bmi | known_w)
ada_ob = ada_ob.fillna(False).astype(bool)
res["ada2026"] = {
    "rule": "non-Asian: BMI>=30, or BMI>=25 and (WHtR>=0.5 or waist>=88 cm); Asian (RIDRETH3=6): BMI>=27.5, or BMI>=23 and "
            "(WHtR>=0.5 or waist>=80 cm). Women whose class needs an unmeasured waist are left out.",
    "n": int(known.sum()), "n_left_out": int((women & ~known).sum()),
    "obesity_ada": est(known, ada_ob), "obesity_bmi_only": est(known, B >= 30),
    "difference": diff(known, ada_ob, B >= 30),
    # women 25-29.9 (non-Asian) who meet the central-adiposity part: overweight by BMI, obesity by the 2026 rule
    "bmi25_30_nonasian_central": est(women & ~asian & (B >= 25) & (B < 30) & known_w, central_na),
}
# Where the difference comes from: percentage points of the same women moved into obesity by the 2026 rule.
moved = known & ada_ob & ~(B >= 30)
res["ada2026"]["difference_parts_pts"] = {
    "nonasian_25_29_9": round(100 * float(W[moved & ~asian].sum() / W[known].sum()), 1),
    "asian": round(100 * float(W[moved & asian].sum() / W[known].sum()), 1)}
assert not (known & ~ada_ob & (B >= 30)).any()                     # nobody leaves obesity under the 2026 rule

# Checks: NCHS crude rates for women (Data Brief 508) and the CMB-013 healthy shares.
C = res["categories"]
HS = json.load(open(hs_path))["groups"]["women"]
checks = {"obesity_women": (C["all_ages"]["obesity"]["pct"], 41.3), "class3_women": (C["all_ages"]["class_3"]["pct"], 12.1),
          # Data Brief 508, Figures 1 and 3 data tables (women by age, checked 2026-10-15)
          "obesity_women_20_39": (C["20-39"]["obesity"]["pct"], 36.8), "obesity_women_40_59": (C["40-59"]["obesity"]["pct"], 47.4),
          "obesity_women_60_plus": (C["60+"]["obesity"]["pct"], 39.6), "class3_women_20_39": (C["20-39"]["class_3"]["pct"], 13.0),
          "class3_women_40_59": (C["40-59"]["class_3"]["pct"], 14.7), "class3_women_60_plus": (C["60+"]["class_3"]["pct"], 8.4)}
for a in ("all_ages", "20-39", "40-59", "60+"):
    checks[f"healthy_{a}"] = (C[a]["healthy"]["pct"], HS[a]["healthy"])
    assert C[a]["n"] == HS[a]["n"], (a, C[a]["n"], HS[a]["n"])
for k, (ours, ref) in checks.items():
    assert abs(ours - ref) <= 0.1 if k.startswith(("obesity", "class3")) else ours == ref, f"{k}: ours {ours} vs {ref}"
for a in C:
    s = sum(C[a][c]["pct"] for c in ("underweight", "healthy", "overweight", "class_1", "class_2", "class_3"))
    assert abs(s - 100) <= 0.3, (a, s)
res["checks"] = {k: {"ours": o, "reference": r} for k, (o, r) in checks.items()}
json.dump(res, open(out, "w"), indent=1)
for a in C:
    print(a, {c: C[a][c]["pct"] for c in CATS}, "n", C[a]["n"])
print("ci", {a: {c: C[a][c]["ci95"] for c in CATS} for a in C})
print("age differences", json.dumps(res["age_differences"]))
print("waist", json.dumps(res["waist"]["by_bmi"]))
print("ada", json.dumps(res["ada2026"]))
