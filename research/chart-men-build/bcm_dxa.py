#!/usr/bin/env python3
"""CMB-018 CHART-MEN: body fat of US men at the same BMI (our calculation from CDC NHANES 2011-2018 whole-body DXA).

Sample and method as research/body-fat-chart-build/bfpc_stats.py (CMB-016): NHANES 2011-2012 to 2017-2018 DEMO, DXX and
BMX files pooled with WTMEC2YR / 4; valid whole-body percent fat (DXDTOPF); men aged 20 to 59 (CDC scanned ages 8-59);
BMI as recorded; categories healthy 18.5-24.99, overweight 25-29.99, obesity 30 and over. Weighted quantiles by the
midpoint rule over distinct values (as bfpc_stats.py, since CMB-039). Variance by Taylor linearization (SDMVSTRA x SDMVPSU), t with the design df (PSUs minus strata).

1. Body fat in each BMI category: 10th, 25th, 50th, 75th and 90th percentiles (asserted equal to bfpc_stats.json).
2. How often BMI and body fat disagree, both ways:
   - men with an overweight BMI (and with obesity) whose body fat is no higher than the median man with a healthy BMI;
   - men with a healthy BMI whose body fat is at least the median of men with an overweight BMI.
   Each a weighted share with its 95% CI. Readings are recorded to 0.1, so each reading is compared with the median as
   the page prints it (to 0.1): a man whose reading equals the printed median carries as much body fat (CMB-039; over
   distinct values the unrounded overweight median is 26.90, just above the 26.9 readings, and would drop them all).
3. Men without a valid scan in each BMI category (weighted share), which the page's method states.

Round once: keep() stores 4 decimals and stops if that changes a printed figure.

usage: python3 bcm_dxa.py RAW_DIR BFPC_STATS_JSON OUT_JSON
  RAW_DIR  folder with DEMO_G..J.xpt, DXX_G..J.xpt, BMX_G..J.xpt (wwwn.cdc.gov/Nchs/Data/Nhanes/Public/...); the DXA
           files are not kept in the repo
"""
import sys, os, json, math
import numpy as np, pandas as pd
from scipy.stats import t as tdist

RAW, BFPC, OUT = sys.argv[1:4]


def cyc(s):
    d = pd.read_sas(os.path.join(RAW, f'DEMO_{s}.xpt'), format='xport')[
        ['SEQN', 'RIAGENDR', 'RIDAGEYR', 'RIDEXPRG', 'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA']]
    x = pd.read_sas(os.path.join(RAW, f'DXX_{s}.xpt'), format='xport')[['SEQN', 'DXDTOPF']]
    b = pd.read_sas(os.path.join(RAW, f'BMX_{s}.xpt'), format='xport')[['SEQN', 'BMXBMI']]
    return d.merge(x, on='SEQN', how='left').merge(b, on='SEQN', how='left')


D = pd.concat([cyc(s) for s in 'GHIJ'], ignore_index=True)
D['W'] = D.WTMEC2YR.fillna(0) / 4.0
D['pf'] = D.DXDTOPF
OK = (D.W > 0) & (D.RIDEXPRG != 1) & D.pf.notna()
design = D.loc[D.W > 0, ['SDMVSTRA', 'SDMVPSU']].drop_duplicates()
DF = len(design) - design.SDMVSTRA.nunique()
TQ = float(tdist.ppf(0.975, DF))
MEN = (D.RIAGENDR == 1) & D.RIDAGEYR.between(20, 59) & D.BMXBMI.notna()
CATS = {'healthy': (18.5, 24.99), 'over': (25, 29.99), 'obese': (30, 200)}


def shown(x):
    return (f'{x:.1f}', int(x + 0.5), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    x = float(x); r = round(x, nd)
    assert shown(r) == shown(x), ('stored value would print differently', x, r)
    return r


def var_of(z):
    v = 0.0
    for _, g in pd.DataFrame({'z': z, 's': D.SDMVSTRA, 'p': D.SDMVPSU}).groupby('s'):
        zj = g.groupby('p').z.sum(); nh = len(zj)
        if nh > 1:
            v += nh / (nh - 1) * ((zj - zj.mean()) ** 2).sum()
    return v


def share(dom, cond):
    m = dom & OK
    w = D.W.where(m, 0.0); y = cond.astype(float).where(m, 0.0); Wt = w.sum()
    p = (w * y).sum() / Wt
    z = (w * (y - p) / Wt).where(m, 0.0)
    se = math.sqrt(var_of(z))
    return {'pct': keep(100 * p), 'ci95': [keep(100 * (p - TQ * se)), keep(100 * (p + TQ * se))], 'n': int(m.sum())}


def wq(dom, qs):
    m = dom & OK
    s = pd.DataFrame({'x': D.loc[m, 'pf'].round(6), 'w': D.W[m]}).groupby('x').w.sum().sort_index()
    c = (np.cumsum(s.values) - s.values / 2) / s.values.sum()
    return [float(np.interp(q, c, s.index.values)) for q in qs]


R = {'source': 'CDC NHANES 2011-2018 whole-body DXA (DXX_G-J) with DEMO_G-J and BMX_G-J; men aged 20 to 59',
     'method': f'WTMEC2YR/4; midpoint weighted quantiles over distinct values; Taylor linearization, df {DF}, t = {TQ:.4f}',
     'by_cat': {}}
BF = json.load(open(BFPC))['bmi']['by_cat']['m']
dom_of = {}
for c, (lo, hi) in CATS.items():
    dom = MEN & D.BMXBMI.between(lo, hi)
    dom_of[c] = dom
    q = wq(dom, [.1, .25, .5, .75, .9])
    R['by_cat'][c] = {'n': int((dom & OK).sum()), **{k: keep(v) for k, v in zip(('p10', 'p25', 'p50', 'p75', 'p90'), q)}}
    for k in ('p10', 'p25', 'p50', 'p75', 'p90', 'n'):
        assert R['by_cat'][c][k] == BF[c][k], (c, k, R['by_cat'][c][k], BF[c][k])
MED_H = wq(dom_of['healthy'], [.5])[0]
MED_O = wq(dom_of['over'], [.5])[0]
PF10 = (D.pf * 10).round()                 # readings in tenths of a point (CDC records DXDTOPF to 0.1)
B_H, B_O = round(MED_H * 10), round(MED_O * 10)  # the medians as printed, in tenths
R['benchmarks'] = {'median_healthy': keep(MED_H), 'median_over': keep(MED_O), 'compared_at': [B_H / 10, B_O / 10]}
R['disagree'] = {
    'over_at_or_below_healthy_median': share(dom_of['over'], PF10 <= B_H),
    'obese_at_or_below_healthy_median': share(dom_of['obese'], PF10 <= B_H),
    'healthy_at_or_above_over_median': share(dom_of['healthy'], PF10 >= B_O),
}
# Men without a valid whole-body scan (no DXDTOPF), by BMI category, weighted: the page's method names them.
R['missing_scan'] = {}
for c in CATS:
    dom = dom_of[c] & (D.W > 0) & (D.RIDEXPRG != 1)
    w = D.W[dom]; miss = D.pf[dom].isna()
    R['missing_scan'][c] = {'pct': keep(100 * float((w * miss).sum() / w.sum())), 'n_missing': int(miss.sum()), 'n': int(dom.sum())}
    assert int(dom.sum()) - int(miss.sum()) == R['by_cat'][c]['n'], c
json.dump(R, open(OUT, 'w'), indent=1)
print('df', DF, 't', round(TQ, 4))
for c, v in R['by_cat'].items():
    print(c, v['n'], [f"{v[k]:.1f}" for k in ('p10', 'p25', 'p50', 'p75', 'p90')])
print('benchmarks', {k: f'{v:.2f}' for k, v in R['benchmarks'].items() if k != 'compared_at'}, 'compared at', R['benchmarks']['compared_at'])
for k, v in R['disagree'].items():
    print(k, f"{v['pct']:.1f}", [f'{x:.1f}' for x in v['ci95']], 'n', v['n'])
print('missing scan', {c: f"{v['pct']:.1f}% ({v['n_missing']} of {v['n']})" for c, v in R['missing_scan'].items()})
