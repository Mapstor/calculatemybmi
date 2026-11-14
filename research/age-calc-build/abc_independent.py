#!/usr/bin/env python3
"""CMB-045: an independent check of /age-bmi-calculator/'s numbers, written apart from abc_stats.py and gen_abc.py and
sharing no code with them. It reads CDC's raw files and the page as served, and compares what the page prints:
  - the percentile tables (5th to 95th, women and men aged 20-39, 40-59, 60+), the decade table (median, middle half),
    the averages tables (BMI, weight lb and kg, waist in and cm), the healthy shares and medians quoted in the text;
  - weights from BMXWT (kg; lb = kg x 2.2046 as NCHS converts), waists from BMXWAIST (cm; in = cm / 2.54), BMI from BMXBMI;
  - quantiles by its own weighted-CDF code (a loop over the sorted distinct values, no np.interp);
  - the page script's rank, read off its embedded curves, against the exact weighted share of each group with a strictly
    lower BMI, at every BMI from 15.0 to 50.0: it prints the largest gap (the curve is linear between percentiles).
usage: python3 research/age-calc-build/abc_independent.py RAW_DIR BASE_URL"""
import html
import json
import re
import sys
import urllib.request

import pandas as pd

raw, base = sys.argv[1], sys.argv[2].rstrip('/')
demo = pd.read_sas(f'{raw}/DEMO_L.xpt', format='xport')
bmx = pd.read_sas(f'{raw}/BMX_L.xpt', format='xport')
d = demo.merge(bmx, on='SEQN', how='left')
d = d[(d.RIDAGEYR >= 20) & (d.WTMEC2YR > 0) & d.BMXBMI.notna()]
d = d[~((d.RIAGENDR == 2) & (d.RIDEXPRG == 1))]
SEX = {'women': d[d.RIAGENDR == 2], 'men': d[d.RIAGENDR == 1]}
print('n women', len(SEX['women']), 'men', len(SEX['men']))
page = urllib.request.urlopen(base + '/age-bmi-calculator/').read().decode('utf-8')
problems = []


def hu(x, nd=1):                                                   # half up at nd decimals, on the decimal string
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def wq(df, col, p):
    """Weighted quantile: cumulative weight share over the distinct values, straight line between them."""
    g = df.groupby(df[col].round(6)).WTMEC2YR.sum().sort_index()
    xs, ws = list(g.index), list(g.values)
    tot = sum(ws)
    cum, run = [], 0.0
    for w in ws:
        run += w
        cum.append(run / tot)
    if p <= cum[0]:
        return xs[0]
    for i in range(1, len(xs)):
        if cum[i] >= p:
            return xs[i - 1] + (p - cum[i - 1]) * (xs[i] - xs[i - 1]) / (cum[i] - cum[i - 1])
    return xs[-1]


def wmean(df, col):
    m = df[df[col].notna()]
    return (m[col] * m.WTMEC2YR).sum() / m.WTMEC2YR.sum()


def share(df, lo, hi):
    return 100 * df[(df.BMXBMI >= lo) & (df.BMXBMI < hi)].WTMEC2YR.sum() / df.WTMEC2YR.sum()


def cells(caption):
    t = re.search(r'(?s)<caption>' + re.escape(caption) + r'</caption>.*?<tbody>(.*?)</tbody>', page)
    rows = re.findall(r'(?s)<tr>(.*?)</tr>', t.group(1))
    out = []
    for r in rows:
        out.append([html.unescape(re.sub(r'<[^>]+>', '|', c)).replace(' ', ' ').strip('|')
                    for c in re.findall(r'(?s)<t[hd][^>]*>(.*?)</t[hd]>', r)])
    return out


GRP = {'20–39': (20, 39), '40–59': (40, 59), '60+': (60, 200)}
DECS = {'20–29': (20, 29), '30–39': (30, 39), '40–49': (40, 49), '50–59': (50, 59), '60–69': (60, 69), '70–79': (70, 79),
        '80+': (80, 200)}
PC = {'5th': .05, '10th': .10, '25th': .25, 'Median': .50, '75th': .75, '90th': .90, '95th': .95}
n_checked = 0
for s, df in SEX.items():
    for row in cells(f'BMI of US {s} by percentile and age group'):
        for (g, (lo, hi)), v in zip(GRP.items(), row[1:]):
            n_checked += 1
            want = hu(wq(df[df.RIDAGEYR.between(lo, hi)], 'BMXBMI', PC[row[0]]))
            if want != v:
                problems.append(f'{s} {g} {row[0]}: page {v}, raw {want}')
    for row in cells(f'US {s}: average BMI, weight and waist by age, 2021–2023'):
        lo, hi = DECS[row[0]]
        sub = df[df.RIDAGEYR.between(lo, hi)]
        # weights and waists: everyone in the decade with a measured value (pregnant women out), as NCHS tabulates them
        dd = demo.merge(bmx, on='SEQN', how='left')
        dd = dd[(dd.RIDAGEYR.between(lo, hi)) & (dd.WTMEC2YR > 0) & (dd.RIAGENDR == (2 if s == 'women' else 1))]
        dd = dd[~((dd.RIAGENDR == 2) & (dd.RIDEXPRG == 1))]
        kg, cm = wmean(dd, 'BMXWT'), wmean(dd, 'BMXWAIST')
        want = [row[0], hu(wmean(sub, 'BMXBMI')), f'{hu(kg * 2.2046)} lb|{hu(kg)} kg', f'{hu(cm / 2.54)} in|{hu(cm)} cm']
        n_checked += 4
        if row != want:
            problems.append(f'{s} averages {row[0]}: page {row}, raw {want}')
dec = cells('Median BMI of US adults by decade of age, with the middle half')
for row in dec:
    lo, hi = DECS[row[0]]
    for s, v in zip(('women', 'men'), row[1:]):
        sub = SEX[s][SEX[s].RIDAGEYR.between(lo, hi)]
        want = f'{hu(wq(sub, "BMXBMI", .5))}|{hu(wq(sub, "BMXBMI", .25))}–{hu(wq(sub, "BMXBMI", .75))}'
        n_checked += 1
        if v != want:
            problems.append(f'decade {s} {row[0]}: page {v}, raw {want}')
text = html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'(?s)<script.*?</script>|<svg.*?</svg>', '', page))).replace(' ', ' ')
for s, dec_, want_txt in (('women', '20-29', 'of women'), ('men', '20-29', 'of men')):
    pass
h = {s: {k: hu(share(SEX[s][SEX[s].RIDAGEYR.between(*v)], 18.5, 25)) for k, v in DECS.items()} for s in SEX}
need = [f"In their 20s, {h['women']['20–29']}% of women and {h['men']['20–29']}% of men have a BMI in the healthy range; in "
        f"their 50s, {h['women']['50–59']}% and {h['men']['50–59']}%",
        f"and {h['women']['70–79']}% of the women and {h['men']['70–79']}% of the men have a BMI of 18.5 to 24.9",
        f"measured {len(SEX['women']) + len(SEX['men']):,} adults"]
for k in need:
    n_checked += 1
    if k not in text:
        problems.append(f'text: {k!r} not on the page')
# The page script's rank against the exact weighted share with a strictly lower BMI.
Q = json.loads(re.sub(r'([{,])(\w+):', r'\1"\2":', re.search(r'var Q=(\{.*?\}\}),T=', page).group(1)))


def pct(q, b):
    if b <= q[0]:
        return 0.0
    if b >= q[98]:
        return 100.0
    for i in range(98):
        if b < q[i + 1]:
            return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0


worst = (0, None)
for s, key in (('women', 'y'), ('women', 'm'), ('women', 'o'), ('men', 'y'), ('men', 'm'), ('men', 'o')):
    lo, hi = {'y': (20, 39), 'm': (40, 59), 'o': (60, 200)}[key]
    sub = SEX[s][SEX[s].RIDAGEYR.between(lo, hi)]
    tot = sub.WTMEC2YR.sum()
    for t in range(150, 501):
        b = t / 10
        exact = 100 * sub[sub.BMXBMI < b - 1e-9].WTMEC2YR.sum() / tot
        curve = pct(Q[s][key], round(b * 10 - 1) / 10)
        if abs(curve - exact) > worst[0]:
            worst = (abs(curve - exact), f'{s} {key} BMI {b}: curve {curve:.2f}, exact {exact:.2f}')
print(f'{n_checked} printed values and sentences checked against the raw files; {len(problems)} problems')
for p in problems:
    print('  PROBLEM', p)
print(f'largest gap between the page script\'s rank (before rounding) and the exact share with a lower BMI, BMI 15.0-50.0: '
      f'{worst[0]:.2f} points ({worst[1]})')
sys.exit(1 if problems else 0)
