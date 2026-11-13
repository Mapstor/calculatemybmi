#!/usr/bin/env python3
"""CMB-033: the US adult BMI rank curves (1st to 99th percentile) at 4 decimals.

The rank lines on /, /men-bmi-calculator/, /women-bmi-calculator/ and the 5'10" rank column of /blog/bmi-chart-men/
read a percentile curve by linear interpolation (DEVLOG section 4, US rank rule). The curves were stored at 2 decimals,
which moved a few whole-percent ranks by one point (chat's count on CMB-017: 8 of 3,204 women's results). This script
computes the same curves by the same method at 4 decimals:
  CDC NHANES August 2021-August 2023 (research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt), adults aged 20 and over with
  a measured BMI and an exam weight, pregnant women excluded; MEC exam weights (WTMEC2YR); weighted cumulative
  distribution over the distinct measured values, linear interpolation (research/home-build/home_stats.py quantiles()).
It stops unless every new curve rounded to 2 decimals equals the curve the pages carried (same sample, same method),
and unless storing 4 decimals changes no displayed rank against the unrounded curve (BMI 10.0 to 80.0), and prints how
many displayed ranks the 2-decimal curves had wrong.

usage: python3 research/rank-curves/curves.py RAW_DIR OUT_JSON
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
A = D.RIDAGEYR
QS = [i / 100 for i in range(1, 100)]


def quantiles(dom):
    m = dom & D.BMXBMI.notna() & (W > 0)
    s = pd.DataFrame({"x": D.loc[m, "BMXBMI"].round(6), "w": W[m]}).groupby("x").w.sum().sort_index()
    F = np.cumsum(s.values) / s.values.sum()
    return [float(np.interp(q, F, s.index.values)) for q in QS], int(m.sum())


adult = (A >= 20) & (D.WTMEC2YR > 0)
men = adult & (D.RIAGENDR == 1)
women = adult & (D.RIAGENDR == 2) & (D.RIDEXPRG != 1)
GROUPS = {"adults": men | women, "men": men, "women": women,
          "women_20_39": women & A.between(20, 39), "women_40_59": women & A.between(40, 59), "women_60plus": women & (A >= 60)}

# The 2-decimal curves the pages carried until CMB-033 (from home_stats.json and wbc_stats.json before this change).
OLD = json.loads((REPO / "research/rank-curves/curves_2dec.json").read_text())

res, FULL = {}, {}
for name, dom in GROUPS.items():
    q, n = quantiles(dom)
    assert all(b > a for a, b in zip(q, q[1:])), f"{name}: the curve must rise strictly"
    old = OLD[name]
    two = [round(x, 2) for x in q]
    assert two == old, f"{name}: the curve at 2 decimals differs from the one the pages carry"
    res[name] = {"n": n, "p1_p99": [round(x, 4) for x in q]}
    FULL[name] = q


def pct(q, b):                              # the pages' pct(): position on the curve, linear between percentiles
    if b <= q[0]:
        return 0.0
    if b >= q[98]:
        return 100.0
    for i in range(98):
        if b < q[i + 1]:
            return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0


def shown(q, b):                            # the pages' rank: lower = strictly lower BMI (curve at b - 0.1), higher = 100 - pct(b)
    lo, hi = pct(q, round(b * 10 - 1) / 10), 100 - pct(q, b)
    r = lambda x: 99 if x > 99 else int(x + 0.5)   # Math.round for positive values
    return r(lo), r(hi)


changes = {}
for name in GROUPS:
    old, new = OLD[name], res[name]["p1_p99"]
    diff = [round(b / 10, 1) for b in range(100, 801) if shown(old, b / 10) != shown(new, b / 10)]
    changes[name] = diff
    exact = [b / 10 for b in range(100, 801) if shown(FULL[name], b / 10) != shown(new, b / 10)]
    assert not exact, f"{name}: storing 4 decimals changes a displayed rank at BMI {exact[:5]}"
    print(f"{name}: n {res[name]['n']}, displayed ranks that change at BMI 10.0-80.0: {len(diff)} {diff[:12]}")
res["changed_ranks"] = changes
Path(out).write_text(json.dumps(res, indent=1))
