#!/usr/bin/env python3
"""US adults aged 20+: BMI percentiles and category shares, CDC NHANES August 2021-August 2023 (cycle L).

Feeds the homepage (CMB-012): the "Compared with US adults" rank in the calculator results, the
percentile table and the category-share table.

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Population: adults aged 20 and over with a measured BMI and an exam weight; pregnant women are
excluded, as NCHS excludes them. Weights: MEC exam weights (WTMEC2YR).
Percentiles: weighted cumulative distribution over the distinct measured values, linear
interpolation -- the method of research/men-pilot/men_stats.py, which reproduces NCHS Series 3
No. 50 (median BMI 28.2 men / 28.3 women; 95th-percentile weight 290.6 lb / 262.7 lb).
Category shares: weighted share of adults in each CDC category, using the measured BMI as recorded
(one decimal). The script stops unless the shares reproduce the crude prevalences NCHS published for
the same cycle: underweight 1.6% (Health E-Stat 119), overweight 32.1% (Health E-Stat 111),
obesity 40.3% and severe obesity 9.4% (NCHS Data Brief 508).

usage: python3 home_stats.py RAW_DIR OUT_JSON
"""
import sys, json
import numpy as np, pandas as pd

raw, out = sys.argv[1], sys.argv[2]
D = pd.read_sas(f"{raw}/DEMO_L.xpt", format="xport").merge(
    pd.read_sas(f"{raw}/BMX_L.xpt", format="xport"), on="SEQN", how="left")
W = D.WTMEC2YR.fillna(0)
D["wt_lb"] = D.BMXWT * 2.2046226218


def quantiles(var, dom, qs):
    m = dom & D[var].notna() & (W > 0)
    s = pd.DataFrame({"x": D.loc[m, var].round(6), "w": W[m]}).groupby("x").w.sum().sort_index()
    F = np.cumsum(s.values) / s.values.sum()
    return [float(np.interp(q, F, s.index.values)) for q in qs], int(m.sum())


def share(dom, cond):
    m = dom & D.BMXBMI.notna() & (W > 0)
    return float(W[m & cond].sum() / W[m].sum())


def mean(var, dom):
    m = dom & D[var].notna() & (W > 0)
    return float((W[m] * D.loc[m, var]).sum() / W[m].sum())


adult = (D.RIDAGEYR >= 20) & (D.WTMEC2YR > 0)
men = adult & (D.RIAGENDR == 1)
women = adult & (D.RIAGENDR == 2) & (D.RIDEXPRG != 1)
adults = men | women

# 1. The percentile method reproduces NCHS Series 3 No. 50 (same checks as men_stats.py).
checks = {
    "men_bmi_median": round(quantiles("BMXBMI", men, [0.5])[0][0], 1),
    "women_bmi_median": round(quantiles("BMXBMI", women, [0.5])[0][0], 1),
    "men_wt_p95_lb": round(quantiles("wt_lb", men, [0.95])[0][0], 1),
    "women_wt_p95_lb": round(quantiles("wt_lb", women, [0.95])[0][0], 1),
    "men_bmi_mean": round(mean("BMXBMI", men), 1),
    "women_bmi_mean": round(mean("BMXBMI", women), 1),
}
published = {"men_bmi_median": 28.2, "women_bmi_median": 28.3, "men_wt_p95_lb": 290.6,
             "women_wt_p95_lb": 262.7, "men_bmi_mean": 29.4, "women_bmi_mean": 30.0}
for k, v in checks.items():
    assert v == published[k], f"{k}: {v} != NCHS Series 3 No. 50 value {published[k]}"

# 2. Category shares reproduce the crude NCHS prevalences for adults 20+.
B = D.BMXBMI
cats = {
    "underweight": B < 18.5,
    "healthy": (B >= 18.5) & (B < 25),
    "overweight": (B >= 25) & (B < 30),
    "obesity_class_1": (B >= 30) & (B < 35),
    "obesity_class_2": (B >= 35) & (B < 40),
    "obesity_class_3": B >= 40,
}
shares = {k: round(100 * share(adults, c), 1) for k, c in cats.items()}
obesity = round(100 * share(adults, B >= 30), 1)
nchs = {"underweight": 1.6, "overweight": 32.1, "obesity": 40.3, "obesity_class_3": 9.4}
got = {"underweight": shares["underweight"], "overweight": shares["overweight"],
       "obesity": obesity, "obesity_class_3": shares["obesity_class_3"]}
for k, v in got.items():
    assert abs(v - nchs[k]) <= 0.1, f"{k}: {v} vs NCHS crude {nchs[k]}"

# 3. Percentile curves for the rank (1st..99th), the visible tables, and the example BMIs.
QS = [i / 100 for i in range(1, 100)]
TAB = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
res = {
    "source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); adults aged 20+, pregnant women excluded",
    "method": "WTMEC2YR-weighted cumulative distribution over distinct values, linear interpolation",
    "reproduces_series3": checks,
    "reproduces_nchs_crude_prevalence": {"ours": got, "nchs": nchs},
    "category_shares_pct": shares,
    "obesity_pct": obesity,
    "share_bmi_25_plus_pct": round(100 * share(adults, B >= 25), 1),
}
for name, dom in (("adults", adults), ("men", men), ("women", women)):
    q99, n = quantiles("BMXBMI", dom, QS)
    assert all(b > a for a, b in zip(q99, q99[1:])), f"{name}: percentile curve must rise strictly"
    qt, _ = quantiles("BMXBMI", dom, TAB)
    res[name] = {
        "bmi_n": n,
        "mean": round(mean("BMXBMI", dom), 1),
        "table": dict(zip(["p5", "p10", "p25", "p50", "p75", "p90", "p95"], [round(x, 1) for x in qt])),
        "p1_p99": [round(x, 2) for x in q99],
    }


def pct_of(bmi, q):
    """The rank the page script computes: percent of adults with a lower BMI (1st..99th curve)."""
    if bmi <= q[0]:
        return 0.0
    if bmi >= q[98]:
        return 100.0
    for i in range(98):
        if bmi < q[i + 1]:
            return i + 1 + (bmi - q[i]) / (q[i + 1] - q[i])
    return 100.0


res["examples"] = {}
for b in (18.5, 23.0, 24.2, 25.0, 25.1, 30.0, 40.0):
    res["examples"][str(b)] = {k: round(pct_of(b, res[k]["p1_p99"]), 1) for k in ("adults", "men", "women")}
res["share_below_23_pct"] = round(100 * share(adults, B < 23), 1)

json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: (v if k not in ("adults", "men", "women") else {kk: vv for kk, vv in v.items() if kk != "p1_p99"})
                  for k, v in res.items()}, indent=1))
