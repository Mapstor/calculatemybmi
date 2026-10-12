#!/usr/bin/env python3
"""US men aged 20+: BMI percentiles and waist shares, CDC NHANES August 2021-August 2023 (cycle L).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files, kept in the repo).
Weights: MEC exam weights (WTMEC2YR). Percentiles: weighted cumulative distribution over the
distinct measured values, linear interpolation. The same method reproduces NCHS Series 3 No. 50:
median BMI 28.2 (men) / 28.3 (women), 95th-percentile weight 290.6 lb (men) / 262.7 lb (women);
the script stops if any of the four differs.

usage: python3 men_stats.py RAW_DIR OUT_JSON
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
    w = W[dom]
    return float(w[cond[dom]].sum() / w.sum())

adult = (D.RIDAGEYR >= 20) & (D.WTMEC2YR > 0)
men = adult & (D.RIAGENDR == 1)
women = adult & (D.RIAGENDR == 2) & (D.RIDEXPRG != 1)

checks = {
    "men_bmi_median": round(quantiles("BMXBMI", men, [0.5])[0][0], 1),
    "women_bmi_median": round(quantiles("BMXBMI", women, [0.5])[0][0], 1),
    "men_wt_p95_lb": round(quantiles("wt_lb", men, [0.95])[0][0], 1),
    "women_wt_p95_lb": round(quantiles("wt_lb", women, [0.95])[0][0], 1),
}
published = {"men_bmi_median": 28.2, "women_bmi_median": 28.3, "men_wt_p95_lb": 290.6, "women_wt_p95_lb": 262.7}
for k, v in checks.items():
    assert v == published[k], f"{k}: {v} != NCHS Series 3 No. 50 value {published[k]}"

q99, n = quantiles("BMXBMI", men, [i / 100 for i in range(1, 100)])
assert all(b > a for a, b in zip(q99, q99[1:])), "percentile curve must rise strictly"
qtab, _ = quantiles("BMXBMI", men, [0.05, 0.10, 0.15, 0.25, 0.50, 0.75, 0.85, 0.90, 0.95])

mw = men & D.BMXWAIST.notna()
mwb = mw & D.BMXBMI.notna()
over = D.BMXWAIST > 102
res = {
    "source": "CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); men aged 20+",
    "method": "WTMEC2YR-weighted cumulative distribution over distinct values, linear interpolation",
    "reproduces_series3": checks,
    "bmi_n": n,
    "p1_p99": [round(x, 2) for x in q99],
    "table": dict(zip(["p5", "p10", "p15", "p25", "p50", "p75", "p85", "p90", "p95"], [round(x, 1) for x in qtab])),
    "waist_n": int(mw.sum()),
    "waist_mean_in": round(float((W[mw] * D.BMXWAIST[mw]).sum() / W[mw].sum()) / 2.54, 1),
    "share_waist_over_102cm": round(100 * share(mw, over), 1),
    "share_waist_over_102cm_bmi_25_29_9": round(100 * share(mwb & (D.BMXBMI >= 25) & (D.BMXBMI < 30), over), 1),
    "n_bmi_25_29_9_with_waist": int((mwb & (D.BMXBMI >= 25) & (D.BMXBMI < 30)).sum()),
}
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "p1_p99"}, indent=1))
