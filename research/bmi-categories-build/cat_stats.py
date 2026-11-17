#!/usr/bin/env python3
"""US adults in each of the six adult BMI categories, the 1998 line move, and the Asian action points: CDC NHANES
August 2021-August 2023 (CMB-067, the /blog/bmi-categories/ D-14 rebuild).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: adults aged 20 and over with a measured BMI and an exam weight; pregnant women excluded, as NCHS excludes them
(the healthy_stats.py and home_stats.py population, 5,929 adults).
Weights: MEC exam weights (WTMEC2YR). BMI as recorded (one decimal). Shares are crude (not age-adjusted), as NCHS's crude rates.
Sampling error: Taylor linearisation with strata SDMVSTRA and PSUs SDMVPSU (15 strata x 2 PSUs, 15 design df); 95% CI =
p +/- t(0.975, 15) x SE; subgroup shares are domain estimates over the whole exam sample. Cells under 30 adults are suppressed.
Checks: the script stops unless it reproduces NCHS's published crude rates for the cycle (Data Brief 508: obesity 40.3 / 39.2 /
41.3 and 35.5 / 46.4 / 38.9 by age, severe obesity 9.4 / 6.7 / 12.1; Health E-Stat 111 overweight 32.1; Health E-Stat 119
underweight 1.6) and the homepage's six shares (research/home-build/home_stats.json).
  - categories: the six CDC categories by sex (all, men, women) and age (all, 20-39, 40-59, 60+), share, 95% CI, n;
  - line_1998: before NIH's 1998 guidelines, US surveys counted adults as overweight from a BMI of 27.8 (men) or 27.3
    (women) (NHLBI 1998; nhlbi-1998-obesity-guidelines). Share of today's adults with a BMI of 25 up to those old lines,
    i.e. overweight now and not before 1998, and the shares at or above each set of lines;
  - asian: non-Hispanic Asian adults (RIDRETH3 = 6): shares at BMI 23+, 25+, 27.5+ and 30+ (the WHO 2004 action points 23
    and 27.5, which NICE NG246 and CDC's National DPP use), and the bands 23-24.9 and 27.5-29.9 the lower lines add;
  - differences: those the page might state, each with its 95% CI; the page states only those whose interval excludes 0.
usage: python3 cat_stats.py RAW_DIR OUT_JSON"""
import json
import sys

import pandas as pd

raw, out = sys.argv[1], sys.argv[2]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
adult = (D.RIDAGEYR >= 20) & (W > 0) & B.notna() & ~((D.RIAGENDR == 2) & (D.RIDEXPRG == 1))
assert int(adult.sum()) == 5929, int(adult.sum())
men, women = adult & (D.RIAGENDR == 1), adult & (D.RIAGENDR == 2)

CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30),
        "class_1": (B >= 30) & (B < 35), "class_2": (B >= 35) & (B < 40), "class_3": B >= 40}
GROUPS = {"all": adult, "men": men, "women": women}
AGES = {"all_ages": adult, "20-39": (D.RIDAGEYR >= 20) & (D.RIDAGEYR <= 39),
        "40-59": (D.RIDAGEYR >= 40) & (D.RIDAGEYR <= 59), "60+": D.RIDAGEYR >= 60}

assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314                                    # t quantile, 0.975, 15 df


def z_of(dom, cond):
    x = float(W[dom].sum())
    p = float(W[dom & cond].sum()) / x
    return W * dom * (cond.astype(float) - p) / x, p


def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5


def est(dom, cond):
    n = int(dom.sum())
    assert n >= 30, n
    z, p = z_of(dom, cond)
    se = se_of(z)
    return {"pct": round(100 * p, 1), "ci95": [round(100 * (p - T975 * se), 1), round(100 * (p + T975 * se), 1)], "n": n}


def diff(dom_a, cond_a, dom_b, cond_b):
    za, pa = z_of(dom_a, cond_a)
    zb, pb = z_of(dom_b, cond_b)
    se = se_of(za - zb)
    d = pa - pb
    lo, hi = d - T975 * se, d + T975 * se
    return {"diff": round(100 * d, 1), "ci95": [round(100 * lo, 1), round(100 * hi, 1)], "excludes_0": bool(lo > 0 or hi < 0)}


res = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); adults aged 20+, pregnant women excluded",
       "method": "WTMEC2YR-weighted crude shares; 95% CI by Taylor linearisation (SDMVSTRA, SDMVPSU), 15 design df",
       "categories": {}}
for g, gm in GROUPS.items():
    res["categories"][g] = {}
    for a, am in AGES.items():
        dom = gm & am
        res["categories"][g][a] = {c: est(dom, m) for c, m in CATS.items()}

# Before 1998: overweight from 27.8 (men) / 27.3 (women). BMI is recorded to one decimal, so "below the old line" is <= 27.7 / 27.2.
old_line = ((D.RIAGENDR == 1) & (B >= 27.8)) | ((D.RIAGENDR == 2) & (B >= 27.3))
moved = (B >= 25) & ~old_line
res["line_1998"] = {
    "moved": {g: est(gm, moved) for g, gm in GROUPS.items()},
    "at_or_above_25": {g: est(gm, B >= 25) for g, gm in GROUPS.items()},
    "at_or_above_old_line": {g: est(gm, old_line) for g, gm in GROUPS.items()},
}

# Non-Hispanic Asian adults (RIDRETH3 = 6), the WHO 2004 action points 23 and 27.5.
asian = adult & (D.RIDRETH3 == 6)
res["asian"] = {"n": int(asian.sum()),
                "bmi_23_plus": est(asian, B >= 23), "bmi_25_plus": est(asian, B >= 25),
                "bmi_27_5_plus": est(asian, B >= 27.5), "bmi_30_plus": est(asian, B >= 30),
                "band_23_24_9": est(asian, (B >= 23) & (B < 25)), "band_27_5_29_9": est(asian, (B >= 27.5) & (B < 30))}

C = res["categories"]
A3 = {a: AGES[a] for a in ("20-39", "40-59", "60+")}
res["differences"] = {
    "class_3_women_minus_men": diff(women, CATS["class_3"], men, CATS["class_3"]),
    "class_2_women_minus_men": diff(women, CATS["class_2"], men, CATS["class_2"]),
    "class_1_men_minus_women": diff(men, CATS["class_1"], women, CATS["class_1"]),
    "overweight_men_minus_women": diff(men, CATS["overweight"], women, CATS["overweight"]),
    "underweight_women_minus_men": diff(women, CATS["underweight"], men, CATS["underweight"]),
    "class_3_40_59_minus_20_39": diff(adult & A3["40-59"], CATS["class_3"], adult & A3["20-39"], CATS["class_3"]),
    "class_3_40_59_minus_60_plus": diff(adult & A3["40-59"], CATS["class_3"], adult & A3["60+"], CATS["class_3"]),
    "class_1_60_plus_minus_20_39": diff(adult & A3["60+"], CATS["class_1"], adult & A3["20-39"], CATS["class_1"]),
    "healthy_20_39_minus_40_59": diff(adult & A3["20-39"], CATS["healthy"], adult & A3["40-59"], CATS["healthy"]),
    "underweight_20_39_minus_40_59": diff(adult & A3["20-39"], CATS["underweight"], adult & A3["40-59"], CATS["underweight"]),
    "moved_men_minus_women": diff(men, moved, women, moved),
    "asian_23_plus_minus_25_plus": diff(asian, B >= 23, asian, B >= 25),
    "asian_27_5_plus_minus_30_plus": diff(asian, B >= 27.5, asian, B >= 30),
}
res["design"] = {"strata": 15, "psus": 30, "df": 15, "t975": T975}

# Reproduce NCHS's published crude rates and the homepage's six shares.
ob = lambda g, a: round(sum(C[g][a][k]["pct"] for k in ("class_1", "class_2", "class_3")), 1)
checks = {"obesity_all": (ob("all", "all_ages"), 40.3), "obesity_men": (ob("men", "all_ages"), 39.2),
          "obesity_women": (ob("women", "all_ages"), 41.3), "obesity_20_39": (ob("all", "20-39"), 35.5),
          "obesity_40_59": (ob("all", "40-59"), 46.4), "obesity_60_plus": (ob("all", "60+"), 38.9),
          "class3_all": (C["all"]["all_ages"]["class_3"]["pct"], 9.4), "class3_men": (C["men"]["all_ages"]["class_3"]["pct"], 6.7),
          "class3_women": (C["women"]["all_ages"]["class_3"]["pct"], 12.1),
          "overweight_all": (C["all"]["all_ages"]["overweight"]["pct"], 32.1),
          "underweight_all": (C["all"]["all_ages"]["underweight"]["pct"], 1.6)}
for k, (ours, nchs) in checks.items():
    assert abs(ours - nchs) <= 0.15, f"{k}: ours {ours} vs NCHS {nchs}"
home = json.load(open("research/home-build/home_stats.json"))["category_shares_pct"]
for k_home, k_ours in (("underweight", "underweight"), ("healthy", "healthy"), ("overweight", "overweight"),
                       ("obesity_class_1", "class_1"), ("obesity_class_2", "class_2"), ("obesity_class_3", "class_3")):
    assert C["all"]["all_ages"][k_ours]["pct"] == home[k_home], (k_ours, C["all"]["all_ages"][k_ours]["pct"], home[k_home])
res["reproduces_nchs"] = {k: {"ours": o, "nchs": n} for k, (o, n) in checks.items()}
json.dump(res, open(out, "w"), indent=1)

for g in GROUPS:
    for a in AGES:
        print(g.ljust(6), a.ljust(9), {k: v["pct"] for k, v in C[g][a].items()}, "n", C[g][a]["healthy"]["n"])
print("1998:", {k: {g: v["pct"] for g, v in d.items()} for k, d in res["line_1998"].items()})
print("asian n", res["asian"]["n"], {k: v["pct"] for k, v in res["asian"].items() if k != "n"})
for k, v in res["differences"].items():
    print(k.ljust(34), v)
