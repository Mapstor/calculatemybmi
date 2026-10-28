#!/usr/bin/env python3
"""CMB-020 BODY-FAT-CALC — how close the height-and-weight and waist-and-height formulas come to a DXA scan, on CDC's
own scans of US adults (our calculation from NHANES 2011-2018 whole-body DXA; the same sample, weights and design as
research/body-fat-chart-build/bfpc_stats.py, whose counts and means this script asserts equal).

Formulas (registry body-fat-equations, rfm-woolcott-2018):
  Deurenberg 1991, adults: body fat % = 1.20 x BMI + 0.23 x age - 10.8 x sex - 5.4   (sex 1 = men, 0 = women)
  Relative fat mass (RFM), Woolcott & Bergman 2018: 64 - 20 x height / waist + 12 x sex   (sex 0 = men, 1 = women;
    waist at the top of the hip bone, the uppermost lateral border of the ilium, as NHANES measures it)
The tape (Navy) and skinfold (Jackson-Pollock) methods can't be checked here: NHANES 2011-2018 measured neither the neck
nor skinfolds (BMX_G to BMX_J).

Sample: NHANES 2011-2012 to 2017-2018 (DEMO, DXX, BMX), weights WTMEC2YR / 4, adults 20-59 (CDC scanned ages 8-59),
pregnant women out, valid whole-body percent fat (DXDTOPF), and the measurements a formula needs (BMI for Deurenberg;
height and waist for RFM). Error = formula minus scan, in percentage points. Variance: Taylor linearization over the
masked strata and PSUs; 95% CIs use t with PSUs minus strata degrees of freedom. A comparison is stated only when its
95% CI excludes 0 (DEVLOG section 4).
Exact ties: BMI and DXA percent fat are recorded to 0.1 and age in whole years, so a Deurenberg estimate is an exact
multiple of 0.01 and its error an exact multiple of 0.01. Both are rounded to 0.01 (relative fat mass and its error to 10
decimals, which only removes float noise: with waists recorded to 0.1 cm and heights to 0.1 cm (12 in 2013-2014 to
0.01 cm), a non-tie lies at least 0.000009 from any boundary). So an error of exactly 3.00 counts as within 3 points, and an estimate of exactly 13.00 falls in the
windows that start or end at 13, as the arithmetic says (fact-check CMB-020: float noise had decided 39 such ties).
Percentiles: the weighted midpoint rule of research/body-fat-chart-build/bfpc_stats.py (each reading's weight centred
on it, linear in between), the rule behind the page's US comparison, here taken over distinct values so the order of
tied readings can't matter (see 0b). For readings recorded to 0.1 it doesn't run low, as a CDF interpolated between
distinct values does (by about 0.07; fact-check CMB-020).
Medians of the error get a 95% CI by Woodruff's method (CI of the share at or below the median, mapped back through the
percentile rule), to compare with the authors' validation medians (Woolcott & Bergman 2018, Table 2).
Round once: keep() stores 4 decimals, more only where 4 would change a printed figure.

usage: bfc_stats.py RAW_DIR BFPC_STATS_JSON OUT_JSON
  RAW_DIR          folder with DEMO_G..J.xpt, DXX_G..J.xpt, BMX_G..J.xpt (wwwn.cdc.gov/Nchs/Data/Nhanes/Public/...)
  BFPC_STATS_JSON  research/body-fat-chart-build/bfpc_stats.json (asserted equal where the samples overlap)
"""
import sys, os, json, math
import numpy as np, pandas as pd
from scipy.stats import t as tdist

RAW, BFPC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def cyc(s, label):
    d = pd.read_sas(os.path.join(RAW, f'DEMO_{s}.xpt'), format='xport')[
        ['SEQN', 'RIAGENDR', 'RIDAGEYR', 'RIDEXPRG', 'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA']]
    x = pd.read_sas(os.path.join(RAW, f'DXX_{s}.xpt'), format='xport')[['SEQN', 'DXDTOPF']]
    b = pd.read_sas(os.path.join(RAW, f'BMX_{s}.xpt'), format='xport')[['SEQN', 'BMXBMI', 'BMXHT', 'BMXWT', 'BMXWAIST']]
    m = d.merge(x, on='SEQN', how='left').merge(b, on='SEQN', how='left')
    m['cycle'] = label
    return m


D = pd.concat([cyc('G', '2011-12'), cyc('H', '2013-14'), cyc('I', '2015-16'), cyc('J', '2017-18')], ignore_index=True)
D['W'] = D.WTMEC2YR.fillna(0) / 4.0
D['pf'] = D.DXDTOPF
ADULT = (D.W > 0) & (D.RIDEXPRG != 1) & D.pf.notna() & D.RIDAGEYR.between(20, 59)
STR, PSU = D.SDMVSTRA, D.SDMVPSU
design = D.loc[D.W > 0, ['SDMVSTRA', 'SDMVPSU']].drop_duplicates()
N_STRATA, N_PSU = design.SDMVSTRA.nunique(), len(design)
DF = N_PSU - N_STRATA
TQ = float(tdist.ppf(0.975, DF))
MEN = D.RIAGENDR == 1
WOMEN = D.RIAGENDR == 2

# The recorded precision the exact-tie rounding relies on (adults 20-59 with a scan)
for col, step in (('BMXBMI', 10), ('DXDTOPF', 10), ('BMXHT', 100), ('BMXWAIST', 10), ('RIDAGEYR', 1)):   # 12 heights in 2013-14 carry 0.01 cm
    v = D.loc[ADULT, col].dropna() * step
    assert ((v - v.round()).abs() < 1e-6).all(), col

# The formulas, as the page's calculator computes them, without float noise (see "Exact ties" above)
D['deur'] = (1.20 * D.BMXBMI + 0.23 * D.RIDAGEYR - 10.8 * MEN.astype(float) - 5.4).round(2)
D['rfm'] = (64 - 20 * D.BMXHT / D.BMXWAIST + 12 * WOMEN.astype(float)).round(10)
for f, nd in (('deur', 2), ('rfm', 10)):
    D[f'e_{f}'] = (D[f] - D.pf).round(nd)
    D[f'a_{f}'] = D[f'e_{f}'].abs()


def shown(x):
    """Every way the page prints a number: 1 decimal, whole points or percent (halves up), and the tails."""
    return (f'{x:.1f}', int(math.floor(x + 0.5)), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    """Store 4 decimals, or the fewest decimals past 4 that print exactly as the unrounded value does."""
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


def lin(y, dom):
    m = dom & y.notna()
    w = D.W.where(m, 0.0)
    yy = y.where(m, 0.0)
    Wt = w.sum()
    mean = (w * yy).sum() / Wt
    z = (w * (yy - mean) / Wt).where(m, 0.0)
    return float(mean), z, int(m.sum())


def est(y, dom):
    mean, z, n = lin(y, dom)
    se = math.sqrt(var_of(z))
    return {'mean': keep(mean), 'se': round(se, 4), 'ci95': [keep(mean - TQ * se), keep(mean + TQ * se)], 'n': n}


def diff(y1, y2, dom):
    """mean(y1) - mean(y2) in the same people (paired), with its 95% CI."""
    m = dom & y1.notna() & y2.notna()
    return est(y1.where(m) - y2.where(m), m)


def share(dom, cond):
    ind = (cond.astype(float) * 100.0).where(dom)
    e = est(ind, dom)
    return {'pct': e['mean'], 'ci95': e['ci95'], 'n': e['n']}


def wq_raw(y, dom, qs):
    """Weighted midpoint rule over distinct values: each value's weight centred on it, linear in between."""
    m = dom & y.notna() & (D.W > 0)
    s = pd.DataFrame({'x': y[m].round(6), 'w': D.W[m]}).groupby('x').w.sum().sort_index()
    c = (np.cumsum(s.values) - s.values / 2) / s.values.sum()
    return [float(np.interp(q, c, s.index.values)) for q in qs]


def wq(y, dom, qs):
    return [keep(v) for v in wq_raw(y, dom, qs)]


def median_ci(y, dom):
    """Woodruff: the 95% CI of the weighted share at or below the median, mapped back through the percentile rule."""
    med = wq_raw(y, dom, [.5])[0]
    m = dom & y.notna()
    e = est((y <= med).astype(float).where(m), m)
    se = e['se']
    lo, hi = wq_raw(y, dom, [.5 - TQ * se, .5 + TQ * se])
    return [keep(lo), keep(hi)]


# ---- 0. the sample equals the body fat chart's (bfpc_stats.json, adults 20-59)
P = json.load(open(BFPC))
for k, sx in (('m', MEN), ('f', WOMEN)):
    e = est(D.pf, ADULT & sx)
    old = P['by_age'][k]['20-59']
    assert e['n'] == old['n'] and f"{e['mean']:.2f}" == f"{old['mean']:.2f}", (k, e, old['n'], old['mean'])
assert int(ADULT.sum()) == P['meta']['n_adults_20_59'] == 10864, int(ADULT.sum())

SEXES = (('women', WOMEN), ('men', MEN))
QS = (.10, .25, .50, .75, .90)

# ---- 0b. one percentile rule on the page. bfpc_stats.py applies the midpoint rule reading by reading after an unstable
# sort, so the order of tied readings can move its percentiles by up to 0.07; over distinct values the same rule can't
# depend on that order. On the 50 quartiles the page prints from bfpc_stats.json (5 percentiles, 5 age groups, both
# sexes) the two agree within 0.08 points; a stable sort alone already moves 5 of them by 0.1 when printed.
OKP = (D.W > 0) & (D.RIDEXPRG != 1) & D.pf.notna()                    # bfpc_stats.py's sample mask
GAP = 0.0
for k, sx in (('m', MEN), ('f', WOMEN)):
    for g, a0, a1 in (('16-19', 16, 19), ('20-29', 20, 29), ('30-39', 30, 39), ('40-49', 40, 49), ('50-59', 50, 59)):
        mine = wq_raw(D.pf, OKP & sx & D.RIDAGEYR.between(a0, a1), QS)
        theirs = [P['by_age'][k][g][p] for p in ('p10', 'p25', 'p50', 'p75', 'p90')]
        GAP = max(GAP, max(abs(a - b) for a, b in zip(mine, theirs)))
assert GAP < 0.08, GAP
R = {'meta': {'cycles': '2011-2012 to 2017-2018', 'weights': 'WTMEC2YR/4', 'ages': '20-59', 'strata': N_STRATA,
              'psus': N_PSU, 'df': DF, 't975': round(TQ, 4), 'n_scanned_20_59': int(ADULT.sum())},
     'formulas': {}}
NEED = {'deur': D.BMXBMI.notna(), 'rfm': D.BMXHT.notna() & D.BMXWAIST.notna()}
BMI_CATS = (('healthy', 18.5, 24.99), ('over', 25, 29.99), ('obese', 30, 200))
for f in ('deur', 'rfm'):
    R['formulas'][f] = {}
    for lab, sx in SEXES:
        dom = ADULT & sx & NEED[f]
        e, a = D[f'e_{f}'], D[f'a_{f}']
        r = {'n': int(dom.sum()), 'bias': est(e, dom), 'mae': est(a, dom),
             'within3': share(dom, a <= 3), 'within5': share(dom, a <= 5),
             'err_q': dict(zip(('p10', 'p25', 'p50', 'p75', 'p90'), wq(e, dom, QS))),
             'err_median_ci95': median_ci(e, dom),
             'scan_mean': est(D.pf, dom), 'formula_mean': est(D[f], dom)}
        r['by_bmi'] = {c: {'bias': est(e, dom & D.BMXBMI.between(lo, hi)), 'mae': est(a, dom & D.BMXBMI.between(lo, hi))}
                       for c, lo, hi in BMI_CATS}
        r['by_age'] = {g: {'bias': est(e, dom & D.RIDAGEYR.between(a0, a1))} for g, a0, a1 in (('20-39', 20, 39), ('40-59', 40, 59))}
        # calibration for the calculator: CDC's scan readings of people whose formula gave about the same estimate
        # (within a point of each whole percent, so each window is two points wide); n >= 30 per window
        cal = {}
        for b in range(5, 66):
            w = dom & D[f].between(b - 1, b + 1, inclusive='left')
            n = int(w.sum())
            if n >= 30:
                cal[str(b)] = {'n': n, 'q': wq(D.pf, w, (.25, .50, .75))}
        r['calib'] = cal
        R['formulas'][f][lab] = r
# The two formulas in the same people (everyone with BMI, height and waist): which came closer?
R['paired'] = {}
for lab, sx in SEXES:
    dom = ADULT & sx & NEED['deur'] & NEED['rfm']
    R['paired'][lab] = {'n': int(dom.sum()), 'mae_rfm_minus_deur': diff(D.a_rfm, D.a_deur, dom),
                        'within5_rfm_minus_deur': diff((D.a_rfm <= 5).astype(float) * 100, (D.a_deur <= 5).astype(float) * 100, dom)}

json.dump(R, open(OUT, 'w'), indent=1)
print('design: strata', N_STRATA, 'psus', N_PSU, 'df', DF, 't', round(TQ, 4), '| adults 20-59 scanned', int(ADULT.sum()))
for f in ('deur', 'rfm'):
    for lab, _ in SEXES:
        r = R['formulas'][f][lab]
        print(f, lab, 'n', r['n'], '| bias', f"{r['bias']['mean']:.2f}", r['bias']['ci95'], '| MAE', f"{r['mae']['mean']:.2f}",
              '| within3', f"{r['within3']['pct']:.1f}", '| within5', f"{r['within5']['pct']:.1f}", '| err q', r['err_q'],
              '| scan', f"{r['scan_mean']['mean']:.2f}", 'formula', f"{r['formula_mean']['mean']:.2f}")
        print('    by BMI bias', {c: f"{v['bias']['mean']:.2f}" for c, v in r['by_bmi'].items()},
              'MAE', {c: f"{v['mae']['mean']:.2f}" for c, v in r['by_bmi'].items()},
              '| by age bias', {g: f"{v['bias']['mean']:.2f}" for g, v in r['by_age'].items()},
              '| calib', min(map(int, r['calib'])), '-', max(map(int, r['calib'])))
for lab in ('women', 'men'):
    p = R['paired'][lab]
    print('paired', lab, p['n'], 'MAE rfm-deur', p['mae_rfm_minus_deur']['mean'], p['mae_rfm_minus_deur']['ci95'],
          '| within5 rfm-deur', p['within5_rfm_minus_deur']['mean'], p['within5_rfm_minus_deur']['ci95'])
