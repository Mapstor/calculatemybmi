#!/usr/bin/env python3
"""Share of US adults in each BMI category by sex and age group, CDC NHANES August 2021-August 2023 (CMB-013).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: adults aged 20 and over with a measured BMI and an exam weight; pregnant women excluded, as NCHS excludes them.
Weights: MEC exam weights (WTMEC2YR). Shares: weighted share in each CDC category, using measured BMI as recorded (one decimal).
Each share in the healthy range also gets a 95% confidence interval (Taylor linearisation, 15 design df), and five
differences the page could state get theirs; the page states only those whose interval excludes 0.
The script stops unless it reproduces the crude prevalences NCHS published for the same cycle (Data Brief 508): obesity
40.3% overall, 39.2% men, 41.3% women, 35.5% / 46.4% / 38.9% at ages 20-39 / 40-59 / 60+; severe obesity 9.4% overall,
6.7% men, 12.1% women; and the Health E-Stat 111 / 119 crude rates (overweight 32.1%, underweight 1.6%).

usage: python3 healthy_stats.py RAW_DIR OUT_JSON
"""
import sys, json
import pandas as pd

raw, out = sys.argv[1], sys.argv[2]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
B = D.BMXBMI
adult = (D.RIDAGEYR >= 20) & (W > 0) & B.notna() & ~((D.RIAGENDR == 2) & (D.RIDEXPRG == 1))

def share(dom, cond):
    return round(100 * float(W[dom & cond].sum() / W[dom].sum()), 1)

CATS = {"underweight": B < 18.5, "healthy": (B >= 18.5) & (B < 25), "overweight": (B >= 25) & (B < 30),
        "obesity": B >= 30, "class_3": B >= 40}
GROUPS = {"all": adult, "men": adult & (D.RIAGENDR == 1), "women": adult & (D.RIAGENDR == 2)}
AGES = {"20-39": (D.RIDAGEYR >= 20) & (D.RIDAGEYR <= 39), "40-59": (D.RIDAGEYR >= 40) & (D.RIDAGEYR <= 59),
        "60+": D.RIDAGEYR >= 60}

res = {"source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); adults aged 20+, pregnant women excluded",
       "method": "WTMEC2YR-weighted share of adults in each CDC BMI category (measured BMI, one decimal)", "groups": {}}
for g, gm in GROUPS.items():
    res["groups"][g] = {"all_ages": {**{c: share(gm, m) for c, m in CATS.items()}, "n": int(gm.sum())}}
    for a, am in AGES.items():
        dom = gm & am
        res["groups"][g][a] = {**{c: share(dom, m) for c, m in CATS.items()}, "n": int(dom.sum())}

# Sampling error (Taylor linearisation): strata SDMVSTRA, PSUs SDMVPSU, all exam-sample records kept so the design stays
# whole; 95% CI = p +/- t(0.975, 15 df) x SE. The 2021-2023 file has 15 strata with 2 PSUs each, so 15 design df.
assert D.SDMVSTRA.nunique() == 15 and set(D.groupby("SDMVSTRA").SDMVPSU.nunique()) == {2}
T975 = 2.1314                                   # t quantile, 0.975, 15 df
def z_of(dom, cond):
    x = float(W[dom].sum()); p = float(W[dom & cond].sum()) / x
    return (W * dom * (cond.astype(float) - p) / x), p
def se_of(z):
    t = pd.DataFrame({"h": D.SDMVSTRA, "j": D.SDMVPSU, "z": z}).groupby(["h", "j"]).z.sum().reset_index()
    return float(sum(len(g) / (len(g) - 1) * ((g.z - g.z.mean()) ** 2).sum() for _, g in t.groupby("h"))) ** 0.5
def ci(dom, cond):
    z, p = z_of(dom, cond); se = se_of(z)
    return [round(100 * (p - T975 * se), 1), round(100 * (p + T975 * se), 1)]
def diff_ci(dom_a, dom_b, cond):
    za, pa = z_of(dom_a, cond); zb, pb = z_of(dom_b, cond); se = se_of(za - zb)
    return {"diff": round(100 * (pa - pb), 1), "ci95": [round(100 * (pa - pb - T975 * se), 1), round(100 * (pa - pb + T975 * se), 1)]}
H = CATS["healthy"]
for g, gm in GROUPS.items():
    res["groups"][g]["all_ages"]["healthy_ci95"] = ci(gm, H)
    for a, am in AGES.items():
        res["groups"][g][a]["healthy_ci95"] = ci(gm & am, H)
W2039 = GROUPS["women"] & AGES["20-39"]
res["healthy_differences"] = {
    "women_minus_men": diff_ci(GROUPS["women"], GROUPS["men"], H),
    "women_20_39_minus_men_20_39": diff_ci(W2039, GROUPS["men"] & AGES["20-39"], H),
    "women_20_39_minus_women_60_plus": diff_ci(W2039, GROUPS["women"] & AGES["60+"], H),
    "men_60_plus_minus_men_40_59": diff_ci(GROUPS["men"] & AGES["60+"], GROUPS["men"] & AGES["40-59"], H),
    "women_60_plus_minus_women_40_59": diff_ci(GROUPS["women"] & AGES["60+"], GROUPS["women"] & AGES["40-59"], H)}
res["design"] = {"strata": 15, "psus": 30, "df": 15, "t975": T975}

G = res["groups"]
checks = {"obesity_all": (G["all"]["all_ages"]["obesity"], 40.3), "obesity_men": (G["men"]["all_ages"]["obesity"], 39.2),
          "obesity_women": (G["women"]["all_ages"]["obesity"], 41.3), "obesity_40_59": (G["all"]["40-59"]["obesity"], 46.4),
          "obesity_20_39": (G["all"]["20-39"]["obesity"], 35.5), "obesity_60_plus": (G["all"]["60+"]["obesity"], 38.9),
          "class3_all": (G["all"]["all_ages"]["class_3"], 9.4), "class3_men": (G["men"]["all_ages"]["class_3"], 6.7),
          "class3_women": (G["women"]["all_ages"]["class_3"], 12.1), "overweight_all": (G["all"]["all_ages"]["overweight"], 32.1),
          "underweight_all": (G["all"]["all_ages"]["underweight"], 1.6)}
for k, (ours, nchs) in checks.items():
    assert abs(ours - nchs) <= 0.1, f"{k}: ours {ours} vs NCHS {nchs}"
res["reproduces_nchs"] = {k: {"ours": o, "nchs": n} for k, (o, n) in checks.items()}
json.dump(res, open(out, "w"), indent=1)
for g in G:
    print(g, {a: (v["healthy"], v["overweight"], v["obesity"], v["underweight"], v["n"]) for a, v in G[g].items()})
