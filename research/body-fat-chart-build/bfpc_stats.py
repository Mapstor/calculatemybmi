#!/usr/bin/env python3
"""CMB-016 BODY-FAT-CHART — the numbers behind /body-fat-percentage-chart/ (our calculation from CDC NHANES
2011-2018 whole-body DXA scans, the same sample and method as research/body-fat/compute_bf.py, which built the page
in B1 and reproduces Liu et al., BMJ 2021;372:n365 Table 3).

Sample: NHANES 2011-2012, 2013-2014, 2015-2016 and 2017-2018 (DEMO, DXX, BMX files), pooled with the exam weight
WTMEC2YR / 4 (NHANES analytic guidelines for combining four cycles). Valid whole-body percent fat (DXDTOPF) present,
pregnant women excluded (RIDEXPRG = 1). CDC scanned ages 8-59 in these cycles.
Variance: Taylor linearization with the masked strata and PSUs (SDMVSTRA x SDMVPSU); 95% CIs use t with the design's
degrees of freedom (PSUs minus strata). A difference between groups is stated only when its 95% CI excludes 0
(DEVLOG section 4, the NHANES comparison rule).
Quantiles: weighted, midpoint rule (as compute_bf.py), so the rank tool's curves stay identical.
Rounding: values the page prints are rounded once, from the unrounded estimate. The JSON stores them at 4 decimals (the
rank tool's shares at 2 or 3) and keep() stops the run if storing would change any figure the page prints (a 1-decimal
value, or a whole-percent share with its "more than 99%" / "under 1%" tails). 'mean' stays at 2 decimals (the record
that research/body-fat/bf_results.json holds); 'mean4' is the one the page prints. Fact-check of 2026-10-21: rounding
twice had put men 50-59 at 28.4 (unrounded 28.347) and four table shares one point high.

Output (JSON): by-age summaries with CIs, differences (sex, age), the share above and below every whole percent from
5 to 60, Gallagher-band shares, body fat inside each BMI category and each 1-unit BMI bin, the 5'4"/140 lb example,
and adults with a healthy BMI whose body fat is above the provisional healthy range.

usage: bfpc_stats.py RAW_DIR BF_RESULTS_JSON OUT_JSON
  RAW_DIR          folder with DEMO_G..J.xpt, DXX_G..J.xpt, BMX_G..J.xpt (wwwn.cdc.gov/Nchs/Data/Nhanes/Public/...)
  BF_RESULTS_JSON  research/body-fat/bf_results.json (the live page's numbers; asserted equal where they overlap)
"""
import sys, os, json, math
import numpy as np, pandas as pd

RAW, BFR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

def cyc(s, label):
    d = pd.read_sas(os.path.join(RAW, f'DEMO_{s}.xpt'), format='xport')[
        ['SEQN', 'RIAGENDR', 'RIDAGEYR', 'RIDEXPRG', 'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA', 'RIDRETH3']]
    x = pd.read_sas(os.path.join(RAW, f'DXX_{s}.xpt'), format='xport')[['SEQN', 'DXDTOPF']]
    b = pd.read_sas(os.path.join(RAW, f'BMX_{s}.xpt'), format='xport')[['SEQN', 'BMXBMI']]
    m = d.merge(x, on='SEQN', how='left').merge(b, on='SEQN', how='left')
    m['cycle'] = label
    return m

D = pd.concat([cyc('G', '2011-12'), cyc('H', '2013-14'), cyc('I', '2015-16'), cyc('J', '2017-18')], ignore_index=True)
D['W'] = D.WTMEC2YR.fillna(0) / 4.0
D['pf'] = D.DXDTOPF
OK = (D.W > 0) & (D.RIDEXPRG != 1) & D.pf.notna()
STR, PSU = D.SDMVSTRA, D.SDMVPSU
design = D.loc[D.W > 0, ['SDMVSTRA', 'SDMVPSU']].drop_duplicates()
N_STRATA = design.SDMVSTRA.nunique()
N_PSU = len(design)
DF = N_PSU - N_STRATA
from scipy.stats import t as tdist
TQ = float(tdist.ppf(0.975, DF))
SEX = {'m': 1, 'f': 2}


def var_of(z):
    """Taylor variance of a linearized total: sum over strata of n_h/(n_h-1) * sum_i (z_hi - zbar_h)^2."""
    v = 0.0
    for h, g in pd.DataFrame({'z': z, 's': STR, 'p': PSU}).groupby('s'):
        zj = g.groupby('p').z.sum()
        nh = len(zj)
        if nh > 1:
            v += nh / (nh - 1) * ((zj - zj.mean()) ** 2).sum()
    return v


def lin(var_series, dom):
    """(mean, linearized z) of a domain mean."""
    m = dom & OK & var_series.notna()
    w = D.W.where(m, 0.0)
    y = var_series.where(m, 0.0)
    Wt = w.sum()
    mean = (w * y).sum() / Wt
    z = (w * (y - mean) / Wt).where(m, 0.0)
    return mean, z, int(m.sum())


def shown(x):
    """Every way the page prints a number: 1 decimal, and as a whole-percent share (halves up, tails written out)."""
    return (f'{x:.1f}', int(x + 0.5), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    """x stored at nd decimals; stops if that changes anything the page prints (no double rounding)."""
    x = float(x)
    r = round(x, nd)
    assert shown(r) == shown(x), ('stored value would print differently', x, r)
    return r


def keep_tool(x):
    """The rank tool's shares: 2 decimals where that prints the same whole percent, else 3 or 4."""
    for nd in (2, 3, 4):
        r = round(float(x), nd)
        if shown(r)[1:] == shown(float(x))[1:]:
            return r
    raise SystemExit(f'tool share {x} needs more than 4 decimals')


def est(var_series, dom, digits=2):
    mean, z, n = lin(var_series, dom)
    se = math.sqrt(var_of(z))
    return {'mean': round(float(mean), digits), 'mean4': keep(mean), 'se': round(se, 3),
            'ci95': [round(float(mean - TQ * se), digits), round(float(mean + TQ * se), digits)], 'n': n}


def diff(var_series, dom1, dom2, digits=1):
    """mean(dom1) - mean(dom2) with its 95% CI (same PSUs, so the covariance is in z)."""
    m1, z1, n1 = lin(var_series, dom1)
    m2, z2, n2 = lin(var_series, dom2)
    se = math.sqrt(var_of(z1 - z2))
    d = m1 - m2
    lo, hi = d - TQ * se, d + TQ * se
    return {'diff': round(float(d), digits), 'ci95': [round(float(lo), digits), round(float(hi), digits)],
            'excludes_0': bool(lo > 0 or hi < 0), 'n': [n1, n2]}


def share(dom, cond, digits=1):
    """Weighted percent of the domain meeting cond, with its CI (a mean of an indicator)."""
    ind = cond.astype(float).where(dom & OK, np.nan)
    e = est(ind * 100.0, dom, digits)
    return {'pct': e['mean'], 'ci95': e['ci95'], 'n': e['n']}


def wq_raw(dom, qs, var='pf'):
    m = dom & OK & D[var].notna()
    x = D.loc[m, var].values
    w = D.W[m].values
    o = np.argsort(x)                       # same call as compute_bf.py, so the curves match it
    x, w = x[o], w[o]
    c = (np.cumsum(w) - w / 2) / w.sum()
    return [float(np.interp(q, c, x)) for q in qs]


def wq(dom, qs, var='pf'):
    """Weighted quantiles as stored for the page (4 decimals, checked by keep)."""
    return [keep(v) for v in wq_raw(dom, qs, var)]


def wq2(dom, qs, var='pf'):
    """The same quantiles at 2 decimals, as compute_bf.py stores them (for the equality asserts)."""
    return [round(v, 2) for v in wq_raw(dom, qs, var)]


def age(a0, a1): return D.RIDAGEYR.between(a0, a1)
def sexdom(k): return D.RIAGENDR == SEX[k]


BF = json.load(open(BFR))
AG = [('8-11', 8, 11), ('12-15', 12, 15), ('16-19', 16, 19), ('20-29', 20, 29), ('30-39', 30, 39), ('40-49', 40, 49),
      ('50-59', 50, 59), ('20-39', 20, 39), ('40-59', 40, 59), ('20-59', 20, 59)]
QS = {'p1': .01, 'p5': .05, 'p10': .10, 'p25': .25, 'p50': .50, 'p75': .75, 'p90': .90, 'p95': .95, 'p99': .99}
R = {'meta': {'cycles': '2011-2012 to 2017-2018', 'weights': 'WTMEC2YR/4', 'strata': N_STRATA, 'psus': N_PSU,
              'df': DF, 't975': round(TQ, 4),
              'n_adults_20_59': int((OK & age(20, 59)).sum()),
              'n_men_20_59': int((OK & age(20, 59) & sexdom('m')).sum()),
              'n_women_20_59': int((OK & age(20, 59) & sexdom('f')).sum())}}

# ---- 1. by sex and age: mean (CI), quantiles, the tool's 1%-step curve (must equal bf_results.json)
R['by_age'] = {}
for k in ('m', 'f'):
    R['by_age'][k] = {}
    for lab, a0, a1 in AG:
        dom = sexdom(k) & age(a0, a1)
        e = est(D.pf, dom)
        q = dict(zip(QS, wq(dom, list(QS.values()))))
        cdf = wq2(dom, [i / 100 for i in range(1, 100)])           # the record, as bf_results.json holds it
        old = BF[k][lab]
        assert e['mean'] == old['mean'] and e['n'] == old['n'], (k, lab, e, old['mean'], old['n'])
        assert cdf == old['cdf'], (k, lab)
        assert wq2(dom, [i / 20 for i in range(1, 20)]) == old['p'], (k, lab)
        R['by_age'][k][lab] = {**e, **q, 'cdf': cdf}

# ---- 2. differences (stated only where the CI excludes 0)
R['diff'] = {'women_minus_men': {}, 'age': {}}
for lab, a0, a1 in AG:
    R['diff']['women_minus_men'][lab] = diff(D.pf, sexdom('f') & age(a0, a1), sexdom('m') & age(a0, a1))
for k in ('m', 'f'):
    R['diff']['age'][k] = {
        '50s_minus_20s': diff(D.pf, sexdom(k) & age(50, 59), sexdom(k) & age(20, 29)),
        '40_59_minus_20_39': diff(D.pf, sexdom(k) & age(40, 59), sexdom(k) & age(20, 39)),
        '16_19_minus_8_11': diff(D.pf, sexdom(k) & age(16, 19), sexdom(k) & age(8, 11)),
        '20s_minus_16_19': diff(D.pf, sexdom(k) & age(20, 29), sexdom(k) & age(16, 19))}

# ---- 3. every whole percent from 5 to 60: share with more and with less body fat (equal readings count on neither side)
LK = [('20-39', 20, 39), ('40-59', 40, 59), ('20-59', 20, 59)]
R['lookup'] = {}
for k in ('m', 'f'):
    R['lookup'][k] = {}
    for lab, a0, a1 in LK:
        dom = sexdom(k) & age(a0, a1) & OK
        w = D.W.where(dom, 0.0)
        Wt = w.sum()
        R['lookup'][k][lab] = {str(p): {'more': keep(w[D.pf > p].sum() / Wt * 100),
                                         'less': keep(w[D.pf < p].sum() / Wt * 100),
                                         'at_or_below': keep(w[D.pf <= p].sum() / Wt * 100)}
                               for p in range(5, 61)}

# ---- 3b. the rank tool's data: share with more body fat at every whole percent from 3 to 65, each age group of the
#          tool (8-11 ... 50-59). The page interpolates between whole percents for a reading like 27.5.
TP = list(range(3, 66))
R['tool'] = {'percents': [TP[0], TP[-1]], 'more': {}}
for k in ('m', 'f'):
    R['tool']['more'][k] = {}
    for lab, a0, a1 in AG[:7]:
        dom = sexdom(k) & age(a0, a1) & OK
        w = D.W.where(dom, 0.0)
        Wt = w.sum()
        R['tool']['more'][k][lab] = [keep_tool(w[D.pf > p].sum() / Wt * 100) for p in TP]

# ---- 4. provisional healthy ranges (Gallagher et al. 2000, as tabulated in J Public Health Afr 2016 Table 1;
#         registry gallagher-2000-bf-ranges): low < a <= healthy < b <= high < c <= very high
GAL = {'f': {'20-39': (21, 33, 39), '40-59': (23, 34, 40), '60-79': (24, 36, 42)},
       'm': {'20-39': (8, 20, 25), '40-59': (11, 22, 28), '60-79': (13, 25, 30)}}
R['gallagher'] = {'cuts': GAL, 'shares': {}}
for k in ('m', 'f'):
    R['gallagher']['shares'][k] = {}
    for lab, a0, a1 in (('20-39', 20, 39), ('40-59', 40, 59)):
        a, b, c = GAL[k][lab]
        dom = sexdom(k) & age(a0, a1)
        R['gallagher']['shares'][k][lab] = {'low': share(dom, D.pf < a), 'healthy': share(dom, (D.pf >= a) & (D.pf < b)),
                                            'high': share(dom, (D.pf >= b) & (D.pf < c)), 'very_high': share(dom, D.pf >= c),
                                            'above_healthy': share(dom, D.pf >= b)}
        bf = BF[k][lab]['gal']
        for band in ('low', 'normal', 'high', 'very_high'):
            mine = R['gallagher']['shares'][k][lab]['healthy' if band == 'normal' else band]['pct']
            assert abs(mine - bf[band]) < 0.051, (k, lab, band, mine, bf[band])

# ---- 5. body fat and BMI (adults 20-59 with BMI measured)
def cut_for(k, which):
    i = {'high': 1, 'very_high': 2}[which]
    return np.where(D.RIDAGEYR <= 39, GAL[k]['20-39'][i], GAL[k]['40-59'][i])

R['bmi'] = {'by_cat': {}, 'by_bin': {}, 'healthy_bmi_above': {}}
CATS = [('under', 0, 18.49), ('healthy', 18.5, 24.99), ('over', 25, 29.99), ('obese', 30, 200)]
for k in ('m', 'f'):
    ad = sexdom(k) & age(20, 59) & D.BMXBMI.notna()
    R['bmi']['by_cat'][k] = {}
    for lab, lo, hi in CATS:
        dom = ad & D.BMXBMI.between(lo, hi)
        n = int((dom & OK).sum())
        R['bmi']['by_cat'][k][lab] = {'n': n, **dict(zip(('p10', 'p25', 'p50', 'p75', 'p90'), wq(dom, [.1, .25, .5, .75, .9]))),
                                      'mean': est(D.pf, dom)}
    for lab, lo, hi in CATS[1:]:
        old = BF[k]['by_bmi'][{'healthy': '18.5–24.9', 'over': '25–29.9', 'obese': '30+'}[lab]]
        dom = ad & D.BMXBMI.between(lo, hi)
        assert wq2(dom, [.1, .25, .5, .75, .9]) == old['q'], (k, lab)
    R['bmi']['by_bin'][k] = {}
    for b in range(17, 46):
        lo, hi = (b, b + 0.99) if b < 45 else (45, 200)
        dom = ad & D.BMXBMI.between(lo, hi)
        n = int((dom & OK).sum())
        R['bmi']['by_bin'][k][str(b)] = {'n': n, **dict(zip(('p10', 'p25', 'p50', 'p75', 'p90'), wq(dom, [.1, .25, .5, .75, .9])))} if n >= 30 else {'n': n}
    nb = ad & D.BMXBMI.between(18.5, 24.99)
    R['bmi']['healthy_bmi_above'][k] = {'above_healthy': share(nb, D.pf >= cut_for(k, 'high')),
                                        'very_high': share(nb, D.pf >= cut_for(k, 'very_high'))}

# ---- 5b. body fat right at the BMI lines (adults whose BMI is within half a point of 18.5, 25 and 30): what the
#          provisional ranges' edges look like on CDC's scanner. Means with CIs (Gallagher's values are predicted means).
R['bmi']['at_lines'] = {}
for k in ('m', 'f'):
    R['bmi']['at_lines'][k] = {}
    for line, lo, hi in (('18.5', 18.0, 18.99), ('25', 24.5, 25.49), ('30', 29.5, 30.49)):
        R['bmi']['at_lines'][k][line] = {}
        for lab, a0, a1 in (('20-39', 20, 39), ('40-59', 40, 59), ('20-59', 20, 59)):
            dom = sexdom(k) & age(a0, a1) & D.BMXBMI.between(lo, hi)
            e = est(D.pf, dom, 1)
            R['bmi']['at_lines'][k][line][lab] = {**e, 'p50': wq(dom, [.5])[0], 'window': [lo, hi]}

# ---- 6. the PAA example "Is 140 pounds fat for a 5'4" female?": 703 * 140 / 64^2 = 24.03 -> BMI 24.0.
#         US women 20-59 whose measured BMI rounds to 23.5-24.4 (one point around it).
ex = sexdom('f') & age(20, 59) & D.BMXBMI.between(23.5, 24.49)
R['example_5_4_140'] = {'bmi': round(703.0 * 140 / 64 ** 2, 1), 'n': int((ex & OK).sum()),
                        **dict(zip(('p10', 'p25', 'p50', 'p75', 'p90'), wq(ex, [.1, .25, .5, .75, .9]))),
                        'above_healthy': share(ex, D.pf >= cut_for('f', 'high'))}

json.dump(R, open(OUT, 'w'), indent=1)
print('design: strata', N_STRATA, 'psus', N_PSU, 'df', DF, 't', round(TQ, 4))
for k in ('m', 'f'):
    a = R['by_age'][k]['20-59']
    print(k, '20-59 mean', a['mean'], a['ci95'], 'n', a['n'], '| p1/p5/p50', a['p1'], a['p5'], a['p50'])
    print('   decades', {g: R['by_age'][k][g]['mean'] for g in ('20-29', '30-39', '40-49', '50-59')},
          '| 50s-20s', R['diff']['age'][k]['50s_minus_20s'])
    print('   kids', {g: R['by_age'][k][g]['mean'] for g in ('8-11', '12-15', '16-19')}, '| 16-19 vs 8-11', R['diff']['age'][k]['16_19_minus_8_11'])
    print('   healthy BMI above healthy fat', R['bmi']['healthy_bmi_above'][k])
    print('   by cat', {c: (v['p50'] if 'p50' in v else None, v['n']) for c, v in R['bmi']['by_cat'][k].items()})
print('women-men', {g: (v['diff'], v['ci95']) for g, v in R['diff']['women_minus_men'].items()})
print('example', R['example_5_4_140'])
for k, ps in (('m', (10, 12, 15, 18, 20, 25, 30)), ('f', (18, 20, 25, 30, 35, 40))):
    print(k, {p: (R['lookup'][k]['20-39'][str(p)]['more'], R['lookup'][k]['40-59'][str(p)]['more']) for p in ps})
