#!/usr/bin/env python3
"""Average weight, height, BMI and waist of US adults (CDC NHANES August 2021-August 2023), for /average-weight/ and the
pages that quote it (/blog/bmi-chart-men/, /bmi-chart/, /blog/bmi-chart-women/, /women-bmi-calculator/).

Rebuilt in CMB-019 so that every figure NCHS publishes for the same files comes out exactly as published:
  - weights in pounds use NCHS's factor, 2.2046 lb per kg (with the exact 2.2046226218, 3 of the 160 weight cells in
    Series 3 No. 50 Table 4 print 0.1 lb higher, e.g. men 40-49: 210.2 against the published 210.1);
  - percentiles read the weighted cumulative distribution over the distinct measured values with linear interpolation
    (the homepage's method, home_stats.py), so tied values can't move a result. The earlier midpoint rule over sorted
    records gave tie-order-dependent quartiles (the CMB-018 fact-check) and missed most of Table 4's percentiles.
The script stops unless it reproduces Series 3 No. 50 Table 4 in full (weight, men and women 20+ and every decade: 16
means and 144 percentiles), the adult (20+) rows of Table 8 (height: 2 means and 18 percentiles; NCHS keeps pregnant
women in the height table) and Table 12 (waist in cm: 2 means and 18 percentiles), and the adult BMI means and medians of
Table 10 (4 values): 204 values, with the number examined in every row checked too. (The CMB-019 fact-check reproduced
all 478 means and percentiles of Tables 4, 8 and 12 and the adult rows of Table 10 with this method.)

Population: adults 20 and over with an MEC exam weight; pregnant women excluded (as NCHS does). Weights: WTMEC2YR.
Standard errors: Taylor linearization over the 15 strata x 2 PSUs; 95% intervals use t with 15 df (2.1314).
Heights: measured height rounded to the nearest inch for the by-height tables (a height is shown with 30+ people).
Round once: keep() stores 4 decimals and stops if storing would change a printed figure.

usage: python3 compute.py RAW_DIR OUT_JSON      (RAW_DIR holds DEMO_L.xpt and BMX_L.xpt, research/average-weight/raw)
"""
import sys, json, math
import numpy as np, pandas as pd
from scipy.stats import t as tdist

RAW, OUT = sys.argv[1], sys.argv[2]
LB = 2.2046                                                   # NCHS's pounds per kilogram (see the docstring)
D = pd.read_sas(f'{RAW}/DEMO_L.xpt', format='xport').merge(pd.read_sas(f'{RAW}/BMX_L.xpt', format='xport'),
                                                            on='SEQN', how='left')
W = D.WTMEC2YR.fillna(0.0)
W = W.where(W > 1e-6, 0.0)                                    # zero weights read back from SAS as 5e-79
D['wt_lb'] = D.BMXWT * LB
D['ht_in'] = D.BMXHT / 2.54
D['waist_in'] = D.BMXWAIST / 2.54
D['hin'] = np.floor(D.ht_in + 0.5)                            # nearest whole inch
ADULT = (D.RIDAGEYR >= 20) & (W > 0) & (D.RIDEXPRG != 1)        # weight, BMI, waist: pregnant women excluded
HADULT = (D.RIDAGEYR >= 20) & (W > 0)                              # height: NCHS's Table 8 keeps pregnant women
STR, PSU = D.SDMVSTRA, D.SDMVPSU
assert STR[W > 0].nunique() == 15 and set(D[W > 0].groupby('SDMVSTRA').SDMVPSU.nunique()) == {2}
DF = 15
TQ = float(tdist.ppf(0.975, DF))
AGES = (('20–29', 20, 29), ('30–39', 30, 39), ('40–49', 40, 49), ('50–59', 50, 59), ('60–69', 60, 69),
        ('70–79', 70, 79), ('80+', 80, 200))


def shown(x):
    return (f'{x:.1f}', f'{x:.0f}', int(x + 0.5), x >= 99.5, x <= 0.5)


def keep(x, nd=4):
    x = float(x); r = round(x, nd)
    assert shown(r) == shown(x), ('stored value would print differently', x, r)
    return r


def var_of(z):
    v = 0.0
    for _, g in pd.DataFrame({'z': z, 's': STR, 'p': PSU}).groupby('s'):
        zj = g.groupby('p').z.sum(); nh = len(zj)
        if nh > 1:
            v += nh / (nh - 1) * ((zj - zj.mean()) ** 2).sum()
    return v


def lin(var, dom):
    """Weighted domain mean and its linearized variable."""
    m = dom & D[var].notna() & (W > 0)
    w = W.where(m, 0.0); y = D[var].where(m, 0.0); Wt = w.sum()
    mean = float((w * y).sum() / Wt)
    return mean, (w * (y - mean) / Wt).where(m, 0.0), int(m.sum())


def est(var, dom):
    m = dom & D[var].notna() & (W > 0)
    if m.sum() == 0:
        return None
    mean, z, n = lin(var, dom)
    se = math.sqrt(var_of(z))
    return {'mean': keep(mean), 'se': keep(se), 'ci95': [keep(mean - TQ * se), keep(mean + TQ * se)], 'n': n}


def diff(var, a, b):
    """Difference of two disjoint domain means (a - b) with a 95% CI."""
    ma, za, _ = lin(var, a); mb, zb, _ = lin(var, b)
    se = math.sqrt(var_of(za - zb)); d = ma - mb
    lo, hi = d - TQ * se, d + TQ * se
    return {'diff': keep(d), 'ci95': [keep(lo), keep(hi)], 'excludes_0': bool(lo > 0 or hi < 0)}


def share(dom, cond, var='BMXBMI'):
    m = dom & D[var].notna() & (W > 0)
    w = W.where(m, 0.0); y = cond.astype(float).where(m, 0.0); Wt = w.sum()
    p = float((w * y).sum() / Wt)
    se = math.sqrt(var_of((w * (y - p) / Wt).where(m, 0.0)))
    return {'pct': keep(100 * p), 'ci95': [keep(100 * (p - TQ * se)), keep(100 * (p + TQ * se))], 'n': int(m.sum())}


def quantiles(var, dom, qs):
    """Weighted CDF over distinct values, linear interpolation (home_stats.py; reproduces NCHS Series 3 No. 50)."""
    m = dom & D[var].notna() & (W > 0)
    s = pd.DataFrame({'x': D.loc[m, var].round(6), 'w': W[m]}).groupby('x').w.sum().sort_index()
    F = np.cumsum(s.values) / s.values.sum()
    return [float(np.interp(q, F, s.index.values)) for q in qs]


# ---- 1. NCHS Series 3 No. 50 (registry nhanes-anthropometric-reference; Table 4 read 2026-10-22 in chat)
T4Q = (.05, .10, .15, .25, .50, .75, .85, .90, .95)
T4 = {'men': {'20+': (2688, 199.0, (134.2, 146.8, 154.3, 166.3, 191.0, 221.9, 244.8, 261.8, 290.6)),
              '20–29': (287, 191.3, (125.6, 133.4, 141.6, 159.1, 184.5, 216.6, 238.3, 252.9, 282.9)),
              '30–39': (385, 201.5, (140.3, 153.8, 156.7, 169.9, 192.0, 223.8, 242.5, 266.8, 292.0)),
              '40–49': (347, 210.1, (145.4, 153.7, 161.3, 173.1, 195.0, 237.5, 263.8, 275.7, 312.8)),
              '50–59': (415, 203.0, (134.4, 150.1, 157.0, 169.3, 193.5, 225.0, 250.5, 264.1, 305.9)),
              '60–69': (651, 196.7, (138.0, 148.0, 154.2, 167.5, 191.7, 218.2, 238.7, 251.3, 273.2)),
              '70–79': (446, 193.4, (134.0, 145.8, 151.7, 164.3, 190.9, 212.8, 235.5, 246.3, 267.5)),
              '80+': (157, 180.1, (127.9, 139.5, 147.0, 156.1, 176.2, 198.4, 212.7, 219.6, 239.2))},
      'women': {'20+': (3254, 171.8, (111.8, 120.6, 127.4, 138.0, 162.0, 196.7, 220.1, 236.3, 262.7)),
                '20–29': (337, 164.9, (105.0, 116.5, 120.9, 130.9, 151.9, 182.7, 216.5, 236.5, 267.4)),
                '30–39': (491, 178.3, (113.4, 122.1, 129.9, 139.2, 165.3, 205.7, 237.9, 252.7, 277.5)),
                '40–49': (442, 177.3, (116.4, 123.4, 129.5, 140.9, 164.8, 199.8, 222.9, 245.8, 272.7)),
                '50–59': (506, 180.0, (117.1, 127.7, 132.8, 143.7, 173.0, 210.6, 231.5, 245.8, 267.5)),
                '60–69': (810, 171.0, (113.7, 122.3, 129.9, 139.5, 163.8, 198.1, 216.8, 230.3, 241.0)),
                '70–79': (494, 162.8, (109.9, 120.3, 125.1, 136.6, 158.0, 181.6, 201.4, 212.2, 228.2)),
                '80+': (174, 149.7, (103.1, 111.6, 116.6, 127.6, 144.8, 165.7, 182.9, 192.4, 207.8))}}
T8 = {'men': (2690, 68.9, (63.9, 65.0, 65.9, 66.9, 69.0, 70.9, 72.1, 72.7, 73.7)),         # height (in): NCHS keeps
      'women': (3307, 63.5, (58.9, 59.8, 60.6, 61.6, 63.5, 65.4, 66.4, 67.1, 67.9))}       # pregnant women in it
T12 = {'men': (2605, 103.0, (79.3, 83.5, 86.8, 91.4, 100.9, 112.3, 119.8, 124.3, 133.2)),   # waist (cm)
       'women': (3121, 97.9, (73.8, 77.0, 80.0, 84.9, 95.7, 109.2, 116.9, 121.5, 129.2))}
BMI_PUB = {'men': (29.4, 28.2), 'women': (30.0, 28.3)}               # Table 10, adults 20+: BMI mean and median
D['waist_cm'] = D.BMXWAIST
cells = 0
for lab, code in (('men', 1), ('women', 2)):
    sx = ADULT & (D.RIAGENDR == code)
    for g, a0, a1 in (('20+', 20, 200),) + AGES:
        dom = sx & D.RIDAGEYR.between(a0, a1)
        n, mean, qs = T4[lab][g]
        e = est('wt_lb', dom)
        assert (e['n'], f"{e['mean']:.1f}") == (n, f'{mean:.1f}'), (lab, g, e['n'], e['mean'], n, mean)
        got = quantiles('wt_lb', dom, T4Q)
        assert [f'{x:.1f}' for x in got] == [f'{x:.1f}' for x in qs], (lab, g, got, qs)
        cells += 1 + len(qs)
    hx = HADULT & (D.RIAGENDR == code); n, mean, qs = T8[lab]; h = est('ht_in', hx)
    assert (h['n'], f"{h['mean']:.1f}") == (n, f'{mean:.1f}'), (lab, h)
    assert [f'{x:.1f}' for x in quantiles('ht_in', hx, T4Q)] == [f'{x:.1f}' for x in qs], (lab, 'height')
    n, mean, qs = T12[lab]; e = est('waist_cm', sx)
    assert (e['n'], f"{e['mean']:.1f}") == (n, f'{mean:.1f}'), (lab, e)
    assert [f'{x:.1f}' for x in quantiles('waist_cm', sx, T4Q)] == [f'{x:.1f}' for x in qs], lab
    b = est('BMXBMI', sx); bm = quantiles('BMXBMI', sx, [.5])[0]
    assert (f"{b['mean']:.1f}", f'{bm:.1f}') == tuple(f'{x:.1f}' for x in BMI_PUB[lab]), (lab, b['mean'], bm)
    cells += 1 + 9 + 1 + len(qs) + 2
assert cells == 2 * (8 * 10 + 10 + 10 + 2), cells

# ---- 2. The results
PCT = dict(zip(('p5', 'p10', 'p15', 'p25', 'p50', 'p75', 'p85', 'p90', 'p95'), T4Q))
R = {'source': 'CDC NHANES August 2021-August 2023, DEMO_L + BMX_L; adults 20+, pregnant women excluded',
     'method': f'WTMEC2YR; lb = kg x {LB} (NCHS); percentiles from the weighted CDF over distinct values, linear '
               f'interpolation; Taylor linearization, 15 strata x 2 PSUs, t({DF}) = {TQ:.4f}',
     'checks': f'reproduces Series 3 No. 50 Table 4 (16 means, 144 percentiles) and the adult rows of Table 8 (height '
               f'mean and 9 percentiles), Table 10 (BMI mean and median) and Table 12 (waist mean and 9 percentiles, cm) '
               f'exactly at 0.1 ({cells} values); heights keep pregnant women, as Table 8 does'}
for lab, code in (('men', 1), ('women', 2)):
    dom = ADULT & (D.RIAGENDR == code)
    hx = HADULT & (D.RIAGENDR == code)
    r = {v: est(v, dom) for v in ('wt_lb', 'BMXBMI', 'waist_in')}
    r['ht_in'] = est('ht_in', hx)
    r['wt_pct'] = {k: keep(x) for k, x in zip(PCT, quantiles('wt_lb', dom, T4Q))}
    r['waist_pct'] = {k: keep(x) for k, x in zip(('p25', 'p50', 'p75'), quantiles('waist_in', dom, [.25, .5, .75]))}
    r['bmi_p50'] = keep(quantiles('BMXBMI', dom, [.5])[0])
    r['ht_q'] = [round(x, 2) for x in quantiles('ht_in', hx, [i / 100 for i in range(1, 100)])]    # for the tool
    # NHLBI's lines: waist over 102 cm (men) or over 88 cm (women)
    r['waist_over_line'] = share(dom, D.BMXWAIST > (102 if code == 1 else 88), var='BMXWAIST')
    # ages 20-74, the age range of CDC's 1960-1962 and 1999-2002 means (Advance Data No. 347)
    r['wt_20_74'] = est('wt_lb', dom & D.RIDAGEYR.between(20, 74))
    ages = {}
    for g, a0, a1 in AGES:
        dd = dom & D.RIDAGEYR.between(a0, a1)
        ages[g] = {'wt': est('wt_lb', dd), 'waist': est('waist_in', dd), 'bmi': est('BMXBMI', dd),
                   'ht': est('ht_in', hx & D.RIDAGEYR.between(a0, a1))}
    r['age'] = ages
    steps = {}
    for (g0, a0, a1), (g1, b0, b1) in zip(AGES, AGES[1:]):                # next decade minus this one
        A = dom & D.RIDAGEYR.between(b0, b1); B = dom & D.RIDAGEYR.between(a0, a1)
        steps[f'{g1} minus {g0}'] = {v: diff(v, A, B) for v in ('wt_lb', 'BMXBMI', 'waist_in')}
    r['age_steps'] = steps
    # 30 to 59: every pair, so "not statistically different" covers the 30s against the 50s too
    pairs = {}
    for (g0, a0, a1), (g1, b0, b1) in ((AGES[1], AGES[2]), (AGES[2], AGES[3]), (AGES[1], AGES[3])):
        A = dom & D.RIDAGEYR.between(b0, b1); B = dom & D.RIDAGEYR.between(a0, a1)
        pairs[f'{g1} minus {g0}'] = {v: diff(v, A, B) for v in ('wt_lb',)}
    r['age_pairs_30_59'] = pairs
    hts = {}
    for h in range(55, 80):
        dd = dom & (D.hin == h); e = est('wt_lb', dd)
        if e is None or e['n'] < 30:
            continue
        win = dom & D.hin.between(h - 1, h + 1)                   # the tool's group: rounded heights h-1 to h+1
        hts[h] = {'wt': e, 'q': [keep(x) for x in quantiles('wt_lb', dd, [.25, .5, .75])],
                  'p10_p90': [keep(x) for x in quantiles('wt_lb', dd, [.10, .90])],
                  'cdf': [keep(x) for x in quantiles('wt_lb', win, [i / 100 for i in range(1, 100)])],
                  'nwin': int((win & D.wt_lb.notna()).sum()), 'bmi': est('BMXBMI', dd),
                  'bmi25_plus': share(dd, D.BMXBMI >= 25)}
    r['height'] = hts
    R[lab] = r

json.dump(R, open(OUT, 'w'), indent=1, ensure_ascii=False)
for lab in ('men', 'women'):
    r = R[lab]
    print(f"{lab}: wt {r['wt_lb']['mean']:.1f} (n {r['wt_lb']['n']}) median {r['wt_pct']['p50']:.1f} | ht {r['ht_in']['mean']:.1f}"
          f" | BMI {r['BMXBMI']['mean']:.1f} | waist {r['waist_in']['mean']:.1f} in, over line {r['waist_over_line']['pct']:.1f}%"
          f" | 20-74 wt {r['wt_20_74']['mean']:.1f}")
    print('   ages:', {k: f"{v['wt']['mean']:.1f}" for k, v in r['age'].items()})
    print('   steps (wt):', {k: (f"{v['wt_lb']['diff']:+.1f}", v['wt_lb']['excludes_0']) for k, v in r['age_steps'].items()})
    print('   heights:', {f"{h // 12}'{h % 12}\"": (f"{v['wt']['mean']:.1f}", v['wt']['n'], f"{v['bmi25_plus']['pct']:.0f}%") for h, v in r['height'].items()})
print(f'checks: {cells} published NCHS values reproduced')
