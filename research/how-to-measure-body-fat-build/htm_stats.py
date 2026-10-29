#!/usr/bin/env python3
"""CMB-021 HOW-TO-MEASURE — what CDC's own scans add to a guide on measuring body fat at home (our calculation from
NHANES 2011-2018 whole-body DXA; the same sample, weights, design, exact-tie rounding and percentile rule as
research/body-fat-calculator-build/bfc_stats.py, whose counts and shares this script asserts equal).

Three things the published studies don't give for US adults:
  1. the two at-home formulas' average miss, in points (mean |formula - scan|) and in the unit Burns et al. (2019) used
     for seven methods, the mean absolute percentage error (MAPE = average of |formula - scan| / scan x 100), with the
     average scan reading, which MAPE depends on (CMB-021 fact-check: CDC's scans average higher than Burns's students');
  2. how far the two formulas land from each other for the same person (waist and height against height and weight);
  3. how much a measuring slip moves each formula for US adults as CDC measured them: 1 inch on the waist (relative fat
     mass), 5 lb on the scale and 1 inch on the height (the BMI formula), from each person's own measurements.
Formulas (registry body-fat-equations, rfm-woolcott-2018): Deurenberg 1991 1.20 x BMI + 0.23 x age - 10.8 x sex - 5.4
(sex 1 = men); relative fat mass 64 - 20 x height / waist + 12 x sex (sex 1 = women).
Sample: NHANES 2011-2012 to 2017-2018 (DEMO, DXX, BMX), weights WTMEC2YR / 4, adults 20-59, not pregnant, valid DXDTOPF.
Variance: Taylor linearization over the masked strata and PSUs (df = PSUs - strata); 95% CIs with t.
Percentiles: weighted midpoint rule over distinct values (bfc_stats.py). Round once: keep() as bfc_stats.py.

usage: htm_stats.py RAW_DIR BFC_STATS_JSON OUT_JSON
  RAW_DIR         folder with DEMO_G..J.xpt, DXX_G..J.xpt, BMX_G..J.xpt (wwwn.cdc.gov/Nchs/Data/Nhanes/Public/...)
  BFC_STATS_JSON  research/body-fat-calculator-build/bfc_stats.json (asserted equal where the two overlap)
"""
import sys, os, json, math
import numpy as np, pandas as pd
from scipy.stats import t as tdist

RAW, BFC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def cyc(s):
    d = pd.read_sas(os.path.join(RAW, f'DEMO_{s}.xpt'), format='xport')[
        ['SEQN', 'RIAGENDR', 'RIDAGEYR', 'RIDEXPRG', 'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA']]
    x = pd.read_sas(os.path.join(RAW, f'DXX_{s}.xpt'), format='xport')[['SEQN', 'DXDTOPF']]
    b = pd.read_sas(os.path.join(RAW, f'BMX_{s}.xpt'), format='xport')[['SEQN', 'BMXBMI', 'BMXHT', 'BMXWT', 'BMXWAIST']]
    return d.merge(x, on='SEQN', how='left').merge(b, on='SEQN', how='left')


D = pd.concat([cyc(s) for s in 'GHIJ'], ignore_index=True)
D['W'] = D.WTMEC2YR.fillna(0) / 4.0
D['pf'] = D.DXDTOPF
ADULT = (D.W > 0) & (D.RIDEXPRG != 1) & D.pf.notna() & D.RIDAGEYR.between(20, 59)
STR, PSU = D.SDMVSTRA, D.SDMVPSU
design = D.loc[D.W > 0, ['SDMVSTRA', 'SDMVPSU']].drop_duplicates()
DF = len(design) - design.SDMVSTRA.nunique()
TQ = float(tdist.ppf(0.975, DF))
MEN, WOMEN = D.RIAGENDR == 1, D.RIAGENDR == 2
SEXES = (('women', WOMEN), ('men', MEN))

# the formulas exactly as bfc_stats.py computes them (exact ties: Deurenberg to 0.01, RFM to 10 decimals)
D['deur'] = (1.20 * D.BMXBMI + 0.23 * D.RIDAGEYR - 10.8 * MEN.astype(float) - 5.4).round(2)
D['rfm'] = (64 - 20 * D.BMXHT / D.BMXWAIST + 12 * WOMEN.astype(float)).round(10)
for f, nd in (('deur', 2), ('rfm', 10)):
    D[f'e_{f}'] = (D[f] - D.pf).round(nd)
    D[f'a_{f}'] = D[f'e_{f}'].abs()
    D[f'ape_{f}'] = D[f'a_{f}'] / D.pf * 100                      # absolute error as a share of the scan's reading
NEED = {'deur': D.BMXBMI.notna(), 'rfm': D.BMXHT.notna() & D.BMXWAIST.notna()}
BOTH = NEED['deur'] & NEED['rfm']
D['gap'] = (D.rfm - D.deur).round(10)                              # the two formulas for the same person
D['agap'] = D.gap.abs()
# a measuring slip, from each person's own measurements (CDC measures in cm and kg; the slip is in inches and pounds)
IN, LB = 2.54, 0.45359237
D['rfm_waist_in'] = 20 * D.BMXHT / D.BMXWAIST - 20 * D.BMXHT / (D.BMXWAIST + IN)   # +1 inch on the waist
D['deur_5lb'] = 1.20 * (5 * LB) / (D.BMXHT / 100) ** 2                             # +5 lb on the scale
D['deur_height_in'] = 1.20 * (D.BMXWT / ((D.BMXHT - IN) / 100) ** 2 - D.BMXWT / (D.BMXHT / 100) ** 2)  # height entered 1 in short


def shown(x):
    return (f'{x:.1f}', int(math.floor(x + 0.5)), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    x = float(x)
    for d in range(nd, 13):
        r = round(x, d)
        if shown(r) == shown(x):
            return r
    raise AssertionError(('stored value would print differently', x))


def var_of(z):
    v = 0.0
    for h, g in pd.DataFrame({'z': z, 's': STR, 'p': PSU}).groupby('s'):
        zj = g.groupby('p').z.sum()
        nh = len(zj)
        if nh > 1:
            v += nh / (nh - 1) * ((zj - zj.mean()) ** 2).sum()
    return v


def est(y, dom):
    m = dom & y.notna()
    w = D.W.where(m, 0.0)
    yy = y.where(m, 0.0)
    Wt = w.sum()
    mean = (w * yy).sum() / Wt
    z = (w * (yy - mean) / Wt).where(m, 0.0)
    se = math.sqrt(var_of(z))
    return {'mean': keep(mean), 'ci95': [keep(mean - TQ * se), keep(mean + TQ * se)], 'n': int(m.sum())}


def share(dom, cond):
    e = est((cond.astype(float) * 100.0).where(dom), dom)
    return {'pct': e['mean'], 'ci95': e['ci95'], 'n': e['n']}


def wq(y, dom, qs):
    m = dom & y.notna() & (D.W > 0)
    s = pd.DataFrame({'x': y[m].round(6), 'w': D.W[m]}).groupby('x').w.sum().sort_index()
    c = (np.cumsum(s.values) - s.values / 2) / s.values.sum()
    return [keep(float(np.interp(q, c, s.index.values))) for q in qs]


# ---- 0. the same sample and the same check as the calculator page (bfc_stats.json)
B = json.load(open(BFC))
assert int(ADULT.sum()) == B['meta']['n_scanned_20_59'] == 10864
for f in ('deur', 'rfm'):
    for lab, sx in SEXES:
        dom = ADULT & sx & NEED[f]
        b = B['formulas'][f][lab]
        assert int(dom.sum()) == b['n'], (f, lab)
        for k, cond in (('within5', D[f'a_{f}'] <= 5), ('within3', D[f'a_{f}'] <= 3)):
            assert f"{share(dom, cond)['pct']:.4f}" == f"{b[k]['pct']:.4f}", (f, lab, k)
        assert f"{est(D[f'a_{f}'], dom)['mean']:.4f}" == f"{b['mae']['mean']:.4f}", (f, lab)

R = {'meta': {'cycles': '2011-2012 to 2017-2018', 'weights': 'WTMEC2YR/4', 'ages': '20-59', 'df': DF,
              't975': round(TQ, 4), 'n_scanned_20_59': int(ADULT.sum())},
     'mape': {}, 'mae': {}, 'scan_mean': {}, 'gap': {}, 'slip': {}}
# ---- 1. average miss as a share of the scan's reading (Burns et al.'s MAPE), women, men and everyone
for f in ('deur', 'rfm'):
    R['mape'][f] = {}
    for lab, sx in SEXES + (('all', WOMEN | MEN),):
        for ages, a0, a1 in (('20-59', 20, 59), ('20-29', 20, 29)):
            dom = ADULT & sx & NEED[f] & D.RIDAGEYR.between(a0, a1)
            R['mape'][f].setdefault(lab, {})[ages] = est(D[f'ape_{f}'], dom)
# ---- 1b. the average miss in points and the average scan reading (MAPE divides by the reading)
for f in ('deur', 'rfm'):
    R['mae'][f] = {lab: est(D[f'a_{f}'], ADULT & sx & NEED[f]) for lab, sx in SEXES + (('all', WOMEN | MEN),)}
    for lab, _ in SEXES:
        assert f"{R['mae'][f][lab]['mean']:.4f}" == f"{B['formulas'][f][lab]['mae']['mean']:.4f}", (f, lab)
R['scan_mean'] = {lab: est(D.pf, ADULT & sx) for lab, sx in SEXES + (('all', WOMEN | MEN),)}
# ---- 2. the two formulas for the same person
for lab, sx in SEXES:
    dom = ADULT & sx & BOTH
    R['gap'][lab] = {'n': int(dom.sum()), 'median_abs': wq(D.agap, dom, [.5])[0],
                     'over3': share(dom, D.agap > 3), 'over5': share(dom, D.agap > 5),
                     'rfm_higher': share(dom, D.gap > 0), 'mean_gap': est(D.gap, dom)}
# ---- 3. a measuring slip: the median effect across US adults as CDC measured them
for lab, sx in SEXES:
    dom = ADULT & sx
    R['slip'][lab] = {k: dict(zip(('p25', 'p50', 'p75'), wq(D[k], dom & D[k].notna(), [.25, .5, .75])))
                      for k in ('rfm_waist_in', 'deur_5lb', 'deur_height_in')}
    R['slip'][lab]['n'] = {k: int((dom & D[k].notna()).sum()) for k in ('rfm_waist_in', 'deur_5lb', 'deur_height_in')}

json.dump(R, open(OUT, 'w'), indent=1)
print('design df', DF, '| adults 20-59', int(ADULT.sum()))
print('MAE', {f: {lab: f"{v['mean']:.2f} {v['ci95']}" for lab, v in R['mae'][f].items()} for f in ('deur', 'rfm')})
print('scan mean', {lab: f"{v['mean']:.2f} {v['ci95']}" for lab, v in R['scan_mean'].items()})
for f in ('deur', 'rfm'):
    print('MAPE', f, {lab: {a: f"{v['mean']:.2f} {v['ci95']}" for a, v in d.items()} for lab, d in R['mape'][f].items()})
for lab in ('women', 'men'):
    g = R['gap'][lab]
    print('gap', lab, g['n'], 'median |RFM-Deur|', g['median_abs'], '| over 3', f"{g['over3']['pct']:.1f}", '| over 5',
          f"{g['over5']['pct']:.1f}", g['over5']['ci95'], '| RFM higher', f"{g['rfm_higher']['pct']:.1f}", '| mean gap', g['mean_gap'])
    print('slip', lab, R['slip'][lab])
