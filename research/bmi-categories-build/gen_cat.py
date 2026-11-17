#!/usr/bin/env python3
"""CMB-067 CATEGORIES — rebuilds /blog/bmi-categories/ to the D-14 guide pattern (DESIGN.md "Guide pages"): intro,
answer block and key takeaways, a hero figure, contents chips, real tables and charts, a flat FAQ whose JSON-LD equals
the visible answers, sources and method, one related block, one 680 px reading column, no <article> wrapper (D-16).
Title, H1 and URL stay (D-28: the page has Search Console impressions).

Wedge (SPEC.md): CDC NHANES August 2021-August 2023, our calculation in cat_stats.py (reproduces NCHS's crude rates):
the six categories by age group, what the 1998 move of the overweight line to 25 did to today's adults, and the WHO 2004
action points applied to non-Hispanic Asian US adults.

Every number comes from cat_stats.json, the calculator's whole-unit weight rule (scripts/check_weight_tables.py), the BMI
formula, or a verified registry row (research/data-sources.csv; links are read from the registry, verified rows only).
usage: python3 gen_cat.py REPO_ROOT STATS_JSON   (CMB_TODAY=YYYY-MM-DD sets the date fields; default: today)"""
import csv
import datetime
import html
import json
import math
import os
import re
import sys

ROOT, STATS = sys.argv[1], sys.argv[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds, table_problems   # the CMB-008 gate's own whole-unit rule

S = json.load(open(STATS))
C, L98, AS, DF = S['categories'], S['line_1998'], S['asian'], S['differences']
PAGE = os.path.join(ROOT, 'blog/bmi-categories/index.html')
src = open(PAGE, encoding='utf-8').read()
REG = {r['domain']: r for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}


def reg(d):
    r = REG[d]
    assert r['status'] == 'verified', d
    return r


def rtext(d):
    r = reg(d)
    return ' '.join((r['source'], r['coverage'], r['sample_note'], r['notes']))


U = {k: reg(d)['url'] for k, d in {
    'cdc_cat': 'cdc-adult-bmi-categories', 'cdc_child': 'cdc-child-bmi-categories', 'cdc_about': 'cdc-about-bmi',
    'cdc_formula': 'cdc-calculating-bmi', 'nhlbi98': 'nhlbi-1998-obesity-guidelines', 'who1995': 'who-trs-854',
    'who2000': 'who-trs-894-obesity', 'who2004': 'who-2004-asian-bmi', 'nice': 'nice-ng246-ethnicity-thresholds',
    'ndpp': 'cdc-ndpp-eligibility', 'gbmc': 'gbmc-2016-bmi-mortality', 'db508': 'nhanes-adult-obesity-2021-2023',
    'he111': 'nhanes-adult-weight-trends', 'he119': 'nhanes-underweight', 'bmx': 'nhanes-2021-2023-exam-files',
    'winter': 'winter-2014-bmi-mortality-65'}.items()}

# ---------------------------------------------------------------- numbers: US adults (our calculation, cat_stats.json)
A0 = 'all_ages'
KEYS = ('underweight', 'healthy', 'overweight', 'class_1', 'class_2', 'class_3')
def P(g, a, c): return C[g][a][c]['pct']
CS = {c: P('all', A0, c) for c in KEYS}
OB = round(CS['class_1'] + CS['class_2'] + CS['class_3'], 1)
assert (CS['underweight'], CS['healthy'], CS['overweight'], CS['class_1'], CS['class_2'], CS['class_3'], OB) == \
    (1.6, 26.0, 32.1, 20.6, 10.3, 9.4, 40.3), (CS, OB)
N_ALL, N_MEN, N_WOM = (C[g][A0]['healthy']['n'] for g in ('all', 'men', 'women'))
assert (N_ALL, N_MEN, N_WOM) == (5929, 2680, 3249)
REPRO = S['reproduces_nchs']
for k, v in REPRO.items():
    assert abs(v['ours'] - v['nchs']) <= 0.15, k
# NCHS publishes the class 3 split by sex (Data Brief 508: 6.7% men, 12.1% women); our calculation matches it.
assert (P('men', A0, 'class_3'), P('women', A0, 'class_3')) == (6.7, 12.1)
assert '(men 6.7, women 12.1)' in rtext('nhanes-adult-obesity-2021-2023')
# Differences the page states: only those whose 95% CI excludes 0.
SAY = ('class_2_women_minus_men', 'class_1_men_minus_women', 'overweight_men_minus_women', 'class_3_40_59_minus_60_plus',
       'class_1_60_plus_minus_20_39', 'healthy_20_39_minus_40_59', 'moved_men_minus_women', 'asian_23_plus_minus_25_plus',
       'asian_27_5_plus_minus_30_plus')
for k in SAY:
    assert DF[k]['excludes_0'] and DF[k]['ci95'][0] > 0, k
assert DF['class_3_40_59_minus_20_39']['ci95'][0] <= 0.05      # touches 0 at one decimal: not stated
MV = {g: L98['moved'][g]['pct'] for g in ('all', 'men', 'women')}
AB25 = {g: L98['at_or_above_25'][g]['pct'] for g in ('all', 'men', 'women')}
OLD = {g: L98['at_or_above_old_line'][g]['pct'] for g in ('all', 'men', 'women')}
assert (MV['all'], MV['men'], MV['women'], AB25['all'], OLD['all']) == (17.5, 21.6, 13.7, 72.4, 54.8), (MV, AB25, OLD)
AN = AS['n']
A23, A25, A275, A30 = (AS[k]['pct'] for k in ('bmi_23_plus', 'bmi_25_plus', 'bmi_27_5_plus', 'bmi_30_plus'))
assert (AN, A23, A25, A275, A30) == (330, 65.5, 45.2, 27.6, 13.4)
def ci(x): return f'{x["ci95"][0]}–{x["ci95"][1]}%'

# ---------------------------------------------------------------- numbers: registry constants (each asserted in its row)
assert '27.8 kg/m2 for men and greater than or equal to 27.3 kg/m2 for women' in rtext('nhlbi-1998-obesity-guidelines')
assert '85th percentile of body mass index (BMI) for men and women aged 20 through 29 years in NHANES II' in rtext('nhlbi-1998-obesity-guidelines')
assert 'Grade 1: BMI 17.0-18.49 (mild thinness) Grade 2: BMI 16.0-16.99 (moderate thinness) Grade 3: BMI <16 (severe thinness)' in rtext('who-trs-854')
assert 'obese class I 30.0-34.9, class II 35.0-39.9, class III >=40' in rtext('who-trs-894-obesity')
assert 'should be adopted internationally' in rtext('who-trs-894-obesity')
assert 'action points 23.0, 27.5, 32.5 and 37.5' in rtext('who-2004-asian-bmi')
assert 'overweight BMI 23 to 27.4, obesity 27.5 or above' in rtext('nice-ng246-ethnicity-thresholds')
assert '23 or higher if you\'re an Asian American person' in rtext('cdc-ndpp-eligibility')
GBMC = [('25–27.4', 1.07), ('27.5–29.9', 1.20), ('30–34.9', 1.45), ('35–39.9', 1.94), ('40–59.9', 2.76)]
for band, hr in GBMC:
    lo = band.split('–')[0]
    assert f'{lo}.0-<' in rtext('gbmc-2016-bmi-mortality') or f'{lo}-<' in rtext('gbmc-2016-bmi-mortality'), band
assert '30.0-<35.0 1.45' in rtext('gbmc-2016-bmi-mortality') and '35.0-<40.0 1.94' in rtext('gbmc-2016-bmi-mortality')
assert '40.0-<60.0 2.76' in rtext('gbmc-2016-bmi-mortality') and '25.0-<27.5 1.07' in rtext('gbmc-2016-bmi-mortality')
assert '27.5-<30.0 1.20' in rtext('gbmc-2016-bmi-mortality') and '239 prospective studies' in rtext('gbmc-2016-bmi-mortality')
assert 'Severe Obesity, 120% of the 95th percentile or greater, or 35 kg/m2 or greater' in rtext('cdc-child-bmi-categories')
assert 'reference BMI 23.0-23.9' in rtext('winter-2014-bmi-mortality-65')


# ---------------------------------------------------------------- numbers: BMI arithmetic (the calculator's rules)
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def bmi_lb(w, h): return r1(703 * w / (h * h))
def starts(h):
    cm = h * 2.54
    return {band: (gate_bounds('lb', h, cm, band)[0], gate_bounds('kg', h, cm, band)[0]) for band in (3, 4, 5)}
H5 = [(5, 0), (5, 4), (5, 8), (6, 0), (6, 4)]
ST = {(ft, i): starts(ft * 12 + i) for ft, i in H5}
S64, S70 = starts(64), starts(70)
assert S64[5] == (233, 106) and S70[5] == (279, 127), (S64, S70)
# PAA "Is 300 lb considered morbidly obese?": class by height, 5'10" to 6'6".
B300 = {h: bmi_lb(300, h) for h in range(70, 79)}
assert [h for h in B300 if B300[h] >= 40] == [70, 71, 72] and [h for h in B300 if 35 <= B300[h] < 40] == [73, 74, 75, 76, 77]
assert B300[78] < 35 and (B300[72], B300[73], B300[78]) == (40.7, 39.6, 34.7), B300
# PAA "Is a BMI of 29.9 obese?": the weight between BMI 29.9 and 30.0, and one BMI unit, at 5'10".
GAP = r1((30.0 - 29.9) * 70 * 70 / 703)
UNIT70 = r1(70 * 70 / 703)
assert (GAP, UNIT70) == (0.7, 7.0)

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(key, text): return f'<a href="{U[key]}" {EXT}>{text}</a>'
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
def cat_cell(cls, name): return f'<span class="cat-dot {cls}" aria-hidden="true"></span>{name}'
CDC = ext('cdc_cat', 'CDC')
GBMC_CITE = ext('gbmc', 'Global BMI Mortality Collaboration, 2016')

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS = []                                        # (figure, label, x0, y0, x1, y1) estimated boxes
SHAPES = []                                       # (figure, x0, y0, x1, y1)
def tw(s, size, weight=400): return len(s) * size * (0.60 if weight >= 600 else 0.56)
def text(fig, x, y, s, size=13, anchor='start', weight=400, fill='#111827'):
    w = tw(s, size, weight)
    x0 = x if anchor == 'start' else (x - w / 2 if anchor == 'middle' else x - w)
    TEXTS.append((fig, s, x0, y - size * 0.8, x0 + w, y + size * 0.25))
    fw = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{fw} text-anchor="{anchor}" fill="{fill}">{esc(s)}</text>'
def rect(fig, x, y, w, h, fill):
    SHAPES.append((fig, x, y, x + w, y + h))
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{fill}"/>'
def svg(fig, vbw, vbh, title, desc, body):
    return (f'<svg viewBox="0 0 {vbw} {vbh}" role="img" aria-labelledby="fig-{fig}-t fig-{fig}-d" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif">'
            f'<title id="fig-{fig}-t">{esc(title)}</title><desc id="fig-{fig}-d">{esc(desc)}</desc>{body}</svg>')
COL = {'underweight': '#3b82f6', 'healthy': '#22c55e', 'overweight': '#f59e0b', 'class_1': '#ef4444', 'class_2': '#ef4444',
       'class_3': '#991b1b'}
NAMES = {'underweight': ('Underweight', 'BMI under 18.5'), 'healthy': ('Healthy weight', 'BMI 18.5–24.9'),
         'overweight': ('Overweight', 'BMI 25–29.9'), 'class_1': ('Class 1 obesity', 'BMI 30–34.9'),
         'class_2': ('Class 2 obesity', 'BMI 35–39.9'), 'class_3': ('Class 3 obesity', 'BMI 40 or more')}

# Hero: the six categories, each with its BMI range and the share of US adults in it; obesity's total under the rows.
# 320-unit viewBox like the other guides' figures, so 13 px labels stay 13 px or more on a phone.
VW, RH, TOP = 320, 44, 4
BW = 200 / 35                                     # px per percentage point, axis to 35%
hero = []
for i, k in enumerate(KEYS):
    y = TOP + i * RH
    name, rng = NAMES[k]
    hero.append(text('hero', 0, y + 14, name, 14, weight=600))
    hero.append(text('hero', tw(name, 14, 600) + 8, y + 14, rng, 13, fill='#4b5563'))
    w = CS[k] * BW
    hero.append(rect('hero', 0, y + 21, w, 16, COL[k]))
    hero.append(text('hero', w + 6, y + 34, f'{CS[k]}%', 13, weight=600))
hero.append(text('hero', 0, TOP + 6 * RH + 14, f'Obesity, classes 1–3: {OB}%', 14, weight=600, fill='#991b1b'))
VH = TOP + 6 * RH + 22
svg_hero = svg('hero', VW, VH, 'Six adult BMI categories and the share of US adults in each',
               f'Underweight under 18.5: {CS["underweight"]}%. Healthy weight 18.5 to 24.9: {CS["healthy"]}%. Overweight 25 to '
               f'29.9: {CS["overweight"]}%. Class 1 obesity 30 to 34.9: {CS["class_1"]}%. Class 2 obesity 35 to 39.9: '
               f'{CS["class_2"]}%. Class 3 obesity 40 or more: {CS["class_3"]}%. Obesity, all three classes: {OB}%. US adults '
               'aged 20 and over, 2021 to 2023.', ''.join(hero))


def legend(fig, items):
    out = []
    for i, (lab, col) in enumerate(items):
        out.append(rect(fig, 0, 4 + i * 20, 12, 12, col))
        out.append(text(fig, 18, 14 + i * 20, lab, 13))
    return out


# 1998: share at or above the overweight line, old lines (27.8 men, 27.3 women) against today's 25.
f98 = legend('y98', (('Before 1998: 27.8 men, 27.3 women', '#94a3b8'), ('Since 1998: 25 for both', '#b45309')))
BW98, R98, Y98 = 210 / 75, 66, 50
for i, (g, lab) in enumerate((('all', 'All adults'), ('men', 'Men'), ('women', 'Women'))):
    y = Y98 + i * R98
    f98.append(text('y98', 0, y + 14, lab, 14, weight=600))
    for j, (v, col) in enumerate(((OLD[g], '#94a3b8'), (AB25[g], '#b45309'))):
        yy = y + 21 + j * 20
        w = v * BW98
        f98.append(rect('y98', 0, yy, w, 16, col))
        f98.append(text('y98', w + 6, yy + 13, f'{v}%', 13, weight=600))
H98 = Y98 + 3 * R98 + 2
svg_98 = svg('y98', VW, H98, 'US adults at or above the overweight line: before and since 1998',
             f'Share of US adults with a BMI at or above the overweight line. All adults: {OLD["all"]}% at the old lines, '
             f'{AB25["all"]}% at 25. Men: {OLD["men"]}% at 27.8, {AB25["men"]}% at 25. Women: {OLD["women"]}% at 27.3, '
             f'{AB25["women"]}% at 25. 2021 to 2023.', ''.join(f98))

# Asian adults: the standard lines (25, 30) and WHO's lower action points (23, 27.5).
fas = legend('asian', (('Lower line (WHO, 2004)', '#b45309'), ('Standard line', '#475569')))
BWA, RA, YA = 220 / 70, 44, 48
for i, (lab, v, col) in enumerate((('BMI 23 or more', A23, '#b45309'), ('BMI 25 or more', A25, '#475569'),
                                   ('BMI 27.5 or more', A275, '#b45309'), ('BMI 30 or more', A30, '#475569'))):
    y = YA + i * RA
    fas.append(text('asian', 0, y + 14, lab, 14, weight=600))
    w = v * BWA
    fas.append(rect('asian', 0, y + 21, w, 16, col))
    fas.append(text('asian', w + 6, y + 34, f'{v}%', 13, weight=600))
HA = YA + 4 * RA + 2
svg_asian = svg('asian', VW, HA, 'Non-Hispanic Asian US adults at the standard and the lower BMI lines',
                f'BMI 23 or more: {A23}%. BMI 25 or more: {A25}%. BMI 27.5 or more: {A275}%. BMI 30 or more: {A30}%. '
                f'{AN} adults, 2021 to 2023.', ''.join(fas))

# Estimated collision check (the rendered check runs in cat_test_playwright.py): no text over text, no text over a bar,
# nothing outside the viewBox.
def overlap(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
VB = {'hero': (VW, VH), 'y98': (VW, H98), 'asian': (VW, HA)}
for i, t in enumerate(TEXTS):
    fw, fh = VB[t[0]]
    assert t[2] >= -0.5 and t[4] <= fw + 0.5 and t[3] >= -0.5 and t[5] <= fh + 0.5, f'outside: {t}'
    for u in TEXTS[i + 1:]:
        assert not (t[0] == u[0] and overlap(t[2:], u[2:])), f'text overlap: {t[1]!r} / {u[1]!r}'
    for s in SHAPES:
        if s[0].split('-')[0] == t[0]:
            assert not overlap(t[2:], s[1:]), f'text over shape: {t[1]!r} / {s}'

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in chat's US/English checks of 2026-11-17 ("bmi obesity chart", "obese and morbidly obese"), as asked;
# the last two cover "People also search for" (BMI categories female / male, for children).
FAQ = [
    ('What are the BMI ranges for obesity?',
     f'Obesity starts at a BMI of 30. CDC splits it into three classes: <strong>class 1, 30 to 34.9; class 2, 35 to 39.9; '
     f'and class 3, 40 or more</strong> ({CDC}). WHO’s report on obesity uses the same lines and calls them obese class I, II '
     f'and III ({ext("who2000", "WHO, 2000")}). In 2021–2023, {CS["class_1"]}% of US adults had class 1 obesity, '
     f'{CS["class_2"]}% class 2 and {CS["class_3"]}% class 3 (our calculation from CDC measurements).'),
    ('Is a BMI of 29.9 obese?',
     f'No. <strong>A BMI of 29.9 is overweight</strong>; obesity starts at 30.0 ({CDC}). BMI is reported to one decimal, and '
     f'at 5′10″ the two are {GAP} lb apart. The <a href="/">BMI calculator</a> gives your BMI to one decimal.'),
    ('Are obese and morbidly obese different?',
     '<strong>Yes. Obese means a BMI of 30 or more; morbidly obese means the top class only, a BMI of 40 or more.</strong> '
     f'CDC calls that range class 3 obesity ({CDC}) and NCHS reports it as severe obesity. In 2021–2023, {OB}% of US adults '
     f'had obesity and {CS["class_3"]}% had class 3 ({ext("db508", "NCHS Data Brief 508")}).'),
    ('Am I morbidly obese or just obese?',
     'It depends on your BMI alone: <strong>30 to 39.9 is obesity class 1 or 2, and 40 or more is class 3</strong>, the range '
     f'called morbid or severe obesity. At 5′4″ class 3 starts at {S64[5][0]} lb ({S64[5][1]} kg); at 5′10″, at '
     f'{S70[5][0]} lb ({S70[5][1]} kg). The <a href="/">BMI calculator</a> gives your category, and the '
     '<a href="/bmi-chart/">BMI chart</a> shows the lines at every height.'),
    ('Is 300 lb considered morbidly obese?',
     f'It depends on height. <strong>300 lb is class 3 obesity at 6′0″ or shorter</strong> (a BMI of {B300[72]} at 6′0″), '
     f'class 2 from 6′1″ to 6′5″ (a BMI of {B300[73]} at 6′1″) and class 1 at 6′6″ (a BMI of {B300[78]}).'),
    ('Is morbidly obese the correct term?',
     'The official sources use other names for the same range, a BMI of 40 or more: <strong>class 3 obesity</strong> on '
     f'CDC’s category page ({CDC}), <strong>severe obesity</strong> in NCHS reports ({ext("db508", "NCHS")}) and '
     f'<strong>obese class III</strong> in WHO’s 2000 report ({ext("who2000", "WHO")}).'),
    ('Are BMI categories different for women and men?',
     f'No. For adults 20 and older, CDC bases the categories on BMI “regardless of age, sex, or race” ({CDC}). The shares '
     f'differ: <strong>{P("women", A0, "class_3")}% of women and {P("men", A0, "class_3")}% of men had class 3 obesity</strong> '
     f'in 2021–2023 ({ext("db508", "NCHS")}), while more men than women were overweight ({P("men", A0, "overweight")}% '
     f'against {P("women", A0, "overweight")}%) or in class 1 ({P("men", A0, "class_1")}% against '
     f'{P("women", A0, "class_1")}%; our calculation).'),
    ('Are BMI categories different for children?',
     '<strong>Yes. From 2 to 19, BMI is read as a percentile</strong> for age and sex: under the 5th percentile is '
     'underweight, the 5th to under the 85th healthy weight, the 85th to under the 95th overweight and the 95th or above '
     f'obesity ({ext("cdc_child", "CDC")}). The <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> '
     'works it out.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9">'
        '</polyline></svg>')
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer">'
                   f'<p>{a}</p></div></div>' for q, a in FAQ)

# ---------------------------------------------------------------- page sections
head = (
    '<div class="page-head"><h1>BMI Categories: All Weight Classifications Explained</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Is a BMI of 29.9 obese? Are obese and morbidly obese different? Is 300 lb morbidly obese?</p>'
    f'<p class="intro-text">Most US adults sit above the healthy range: {CS["overweight"]}% are overweight and {OB}% have '
    f'obesity, {CS["class_3"]}% in class 3 (our calculation from CDC measurements, 2021–2023).</p>'
    '<p class="intro-text">Below: the six categories and three obesity classes, how many US adults fall in each by age, the '
    'lower lines for Asian adults, and the history behind 25 and 30.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>Adults have six BMI categories:</strong> underweight (under 18.5), healthy weight (18.5 to '
    '24.9), overweight (25 to 29.9) and obesity in three classes, class 1 (30 to 34.9), class 2 (35 to 39.9) and class 3 (40 '
    'or more). CDC uses the same lines for women and men aged 20 and over; children use percentiles.</p><ul>'
    f'<li><strong>{OB}% of US adults have obesity</strong>: {CS["class_1"]}% class 1, {CS["class_2"]}% class 2 and '
    f'{CS["class_3"]}% class 3. Another {CS["overweight"]}% are overweight and {CS["healthy"]}% at a healthy weight '
    '(2021–2023, our calculation, matching NCHS’s published rates).</li>'
    f'<li><strong>Class 3 obesity is more common in women</strong>: {P("women", A0, "class_3")}% against '
    f'{P("men", A0, "class_3")}% of men (NCHS).</li>'
    '<li><strong>The overweight line moved in 1998.</strong> US surveys had counted adults as overweight from 27.8 (men) or '
    f'27.3 (women); NIH set 25 for both. {MV["all"]}% of US adults today have a BMI between 25 and the old lines (our '
    'calculation).</li>'
    f'<li><strong>Lower lines for Asian adults.</strong> WHO’s 2004 action points are 23 and 27.5. Among non-Hispanic Asian '
    f'US adults, {A275}% have a BMI of 27.5 or more, about twice the {A30}% at 30 or more (our calculation).</li>'
    '<li><strong>BMI can’t tell muscle from fat</strong> (CDC), so a waist or body-fat measurement adds what it misses.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This guide is for information only. BMI is a '
    'screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>The six adult BMI categories and the share of US adults aged 20 '
            f'and over in each, 2021–2023. Categories: CDC. Shares: our calculation from CDC NHANES '
            f'({N_ALL:,} adults).</figcaption></figure>')

TOC = (('categories', 'Categories'), ('obesity', 'Obesity classes'), ('underweight', 'Underweight'),
       ('women-men', 'Women, men, age'), ('children', 'Children'), ('asian', 'Asian adults'), ('history', 'Since 1998'),
       ('near-a-line', 'Near a line'), ('limits', 'Limits'), ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in TOC) + '</nav>')

CLS = {'underweight': 'underweight', 'healthy': 'normal', 'overweight': 'overweight', 'class_1': 'obese', 'class_2': 'obese',
       'class_3': 'obese-severe'}
cat_rows = ''.join(f'<tr><th scope="row">{cat_cell(CLS[k], NAMES[k][0])}</th><td>{NAMES[k][1][4:]}</td>'
                   f'<td class="num">{CS[k]}%</td></tr>' for k in KEYS)
sec_cat = (
    '<section id="categories" class="content-section flow"><h2>The six adult BMI categories</h2>'
    f'<p>For adults 20 and older, CDC uses four categories and splits the fourth, obesity, into three classes ({CDC}). NIH’s '
    f'1998 guidelines set the same lines ({ext("nhlbi98", "NHLBI, 1998")}), and WHO’s report on obesity uses them too, '
    f'calling the classes obese class I, II and III ({ext("who2000", "WHO, 2000")}).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Adult BMI categories and the share of US adults in each, '
    '2021–2023</caption><thead><tr><th scope="col">Category</th><th scope="col">BMI</th><th scope="col" class="num">US adults'
    f'</th></tr></thead><tbody>{cat_rows}</tbody></table></div>'
    f'<p class="source-note">Categories: {ext("cdc_cat", "CDC Adult BMI Categories")}. Shares: our calculation from CDC '
    f'NHANES August 2021–August 2023 ({N_ALL:,} adults aged 20 and over); they match NCHS’s published crude rates for '
    f'underweight ({ext("he119", "Health E-Stat 119")}), overweight ({ext("he111", "Health E-Stat 111")}), obesity and '
    f'class 3 obesity ({ext("db508", "Data Brief 508")}).</p>'
    '<p>BMI is your weight in kilograms divided by your height in meters squared, or your weight in pounds times 703 divided '
    f'by your height in inches squared ({ext("cdc_formula", "CDC")}). It is reported to one decimal, so 24.9 is the top of '
    'the healthy range and 25.0 the start of overweight. The <a href="/bmi-chart/">BMI chart</a> gives the weight for every '
    'category at each height, and the <a href="/">BMI calculator</a> works out yours.</p>'
    '</section>')

st_rows = ''.join(
    f'<tr><th scope="row">{ft}′{i}″<span class="unit-alt">({(ft * 12 + i) * 2.54:.1f} cm)</span></th>'
    + ''.join(f'<td>≥{ST[(ft, i)][b][0]} lb<span class="unit-alt">(≥{ST[(ft, i)][b][1]} kg)</span></td>' for b in (3, 4, 5)) + '</tr>'
    for ft, i in H5)
d = DF
sec_ob = (
    '<section id="obesity" class="content-section flow"><h2>The three classes of obesity</h2>'
    f'<p>CDC splits obesity, every BMI of 30 or more, into three classes: <strong>class 1 is 30 to 34.9, class 2 is 35 to '
    f'39.9 and class 3 is 40 or more</strong> ({CDC}). NCHS reports class 3 as severe obesity '
    f'({ext("db508", "NCHS")}), and it is sometimes called morbid obesity. In pounds, each class starts at a different weight '
    'for each height:</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Where each obesity class starts, at five heights'
    '</caption><thead><tr><th scope="col">Height</th><th scope="col">Class 1 obesity<span class="unit-alt">BMI 30</span></th>'
    '<th scope="col">Class 2 obesity<span class="unit-alt">BMI 35</span></th><th scope="col">Class 3 obesity'
    f'<span class="unit-alt">BMI 40</span></th></tr></thead><tbody>{st_rows}</tbody></table></div>'
    '<p class="source-note">The lightest whole pound and whole kilogram whose BMI, rounded to one decimal, is in the class, '
    'as the site’s calculator rounds. Every height: <a href="/bmi-chart/">BMI chart</a>.</p>'
    '<p>In never-smokers without chronic disease, the risk of death rose with each class. Against a BMI of 22.5 to 24.9, it '
    f'was {GBMC[2][1]:.2f} times as high at 30 to 34.9, {GBMC[3][1]:.2f} times at 35 to 39.9 and {GBMC[4][1]:.2f} times at '
    f'40 to 59.9 ({GBMC_CITE}).</p>'
    f'<p>Class 3 obesity is more common in women than in men: {P("women", A0, "class_3")}% against '
    f'{P("men", A0, "class_3")}% ({ext("db508", "NCHS Data Brief 508")}). So is class 2 ({P("women", A0, "class_2")}% '
    f'against {P("men", A0, "class_2")}%), while class 1 is more common in men ({P("men", A0, "class_1")}% against '
    f'{P("women", A0, "class_1")}%) (our calculation; both differences hold at 95% confidence).</p>'
    '</section>')

sec_uw = (
    '<section id="underweight" class="content-section flow"><h2>Underweight and WHO’s thinness grades</h2>'
    f'<p>Underweight is a BMI under 18.5 ({CDC}), and {CS["underweight"]}% of US adults were underweight in 2021–2023 '
    f'({ext("he119", "Health E-Stat 119")}). WHO’s 1995 report on anthropometry grades it further '
    f'({ext("who1995", "WHO, 1995")}):</p>'
    '<div class="table-responsive"><table class="data-table"><caption>WHO thinness grades for adults</caption><thead><tr>'
    '<th scope="col">Grade</th><th scope="col">BMI</th></tr></thead><tbody>'
    '<tr><th scope="row">Grade 1, mild thinness</th><td>17.0–18.4</td></tr>'
    '<tr><th scope="row">Grade 2, moderate thinness</th><td>16.0–16.9</td></tr>'
    '<tr><th scope="row">Grade 3, severe thinness</th><td>Under 16.0</td></tr></tbody></table></div>'
    '<p>CDC notes that “poor nutrition and underlying health conditions can result in underweight” '
    f'({ext("he119", "Health E-Stat 119")}). <a href="/blog/underweight-bmi-risks/">Underweight BMI risks</a> covers the '
    'causes and when to get help.</p>'
    '</section>')

AG = ('20-39', '40-59', '60+')                    # all adults: the first table
age_rows = ''.join(f'<tr><th scope="row">{NAMES[k][0]}</th>'               # no dot: the table fits a 390 phone
                   + ''.join(f'<td class="num">{P("all", a, k)}%</td>' for a in AG) + '</tr>' for k in KEYS)
sec_wm = (
    '<section id="women-men" class="content-section flow"><h2>The same lines for women, men and every adult age</h2>'
    f'<p>CDC bases the adult categories on BMI “regardless of age, sex, or race” ({CDC}), so a woman and a man of the same '
    'height cross each line at the same weight. What changes with age is how many adults sit in each category:</p>'
    '<div class="table-responsive"><table class="data-table"><caption>US adults in each BMI category by age group, '
    '2021–2023</caption><thead><tr><th scope="col">Category</th><th scope="col" class="num">20–39</th><th scope="col" '
    'class="num">40–59</th><th scope="col" class="num">60+</th></tr></thead>'
    f'<tbody>{age_rows}</tbody></table></div>'
    f'<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023 ({C["all"]["20-39"]["healthy"]["n"]:,}, '
    f'{C["all"]["40-59"]["healthy"]["n"]:,} and {C["all"]["60+"]["healthy"]["n"]:,} adults); obesity by age matches '
    f'{ext("db508", "Data Brief 508")} ({REPRO["obesity_20_39"]["nchs"]}%, {REPRO["obesity_40_59"]["nchs"]}% and '
    f'{REPRO["obesity_60_plus"]["nchs"]}%).</p>'
    f'<p>A healthy BMI is more common at 20 to 39 ({P("all", "20-39", "healthy")}%) than at 40 to 59 '
    f'({P("all", "40-59", "healthy")}%). Class 1 obesity is more common at 60 and over ({P("all", "60+", "class_1")}%) '
    f'than at 20 to 39 ({P("all", "20-39", "class_1")}%), while class 3 is less common at 60 and over '
    f'({P("all", "60+", "class_3")}%) than at 40 to 59 ({P("all", "40-59", "class_3")}%). The page states a difference only '
    'when its 95% confidence interval excludes zero.</p>'
    f'<p>For adults 65 and over, a meta-analysis found a higher risk of death below a BMI of 23 '
    f'({ext("winter", "Winter et al., 2014")}), but the categories themselves don’t change with age. '
    '<a href="/blog/bmi-by-age/">BMI by age</a> covers it.</p>'
    '</section>')

sec_child = (
    '<section id="children" class="content-section flow"><h2>Children and teens: percentiles, not fixed lines</h2>'
    '<p>From 2 to 19, BMI is compared with children of the same sex and age, as a BMI-for-age percentile '
    f'({ext("cdc_child", "CDC")}). The <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it '
    'out.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>BMI categories for children and teens aged 2 to 19'
    '</caption><thead><tr><th scope="col">Category</th><th scope="col">BMI-for-age percentile</th></tr></thead><tbody>'
    f'<tr><th scope="row">{cat_cell("underweight", "Underweight")}</th><td>Under the 5th</td></tr>'
    f'<tr><th scope="row">{cat_cell("normal", "Healthy weight")}</th><td>5th to under the 85th</td></tr>'
    f'<tr><th scope="row">{cat_cell("overweight", "Overweight")}</th><td>85th to under the 95th</td></tr>'
    f'<tr><th scope="row">{cat_cell("obese", "Obesity")}</th><td>95th or above</td></tr>'
    f'<tr><th scope="row">{cat_cell("obese-severe", "Severe obesity")}</th><td>120% of the 95th or more, or a BMI of 35 or '
    'more</td></tr></tbody></table></div>'
    f'<p class="source-note">Source: {ext("cdc_child", "CDC Child and Teen BMI Categories")}.</p>'
    '</section>')

sec_asian = (
    '<section id="asian" class="content-section flow"><h2>Lower action points for Asian adults</h2>'
    '<p>In 2004, a WHO expert consultation found that the share of Asian people at high risk of type 2 diabetes and '
    'cardiovascular disease is substantial at BMIs below 25. It kept the international categories and added 23, 27.5, '
    f'32.5 and 37.5 as points for public-health action ({ext("who2004", "WHO, 2004")}). Two guidelines use the lower '
    'lines:</p><ul>'
    '<li>CDC’s National Diabetes Prevention Program takes Asian American adults from a BMI of 23 instead of 25 '
    f'({ext("ndpp", "CDC")}).</li>'
    '<li>In the UK, NICE uses overweight from 23 to 27.4 and obesity from 27.5 for people with a South Asian, Chinese, other '
    f'Asian, Middle Eastern, Black African or African-Caribbean background ({ext("nice", "NICE guideline NG246")}).</li></ul>'
    f'<figure class="figure">{svg_asian}<figcaption>Non-Hispanic Asian US adults with a BMI at or above each line, '
    f'2021–2023. Our calculation from CDC NHANES ({AN} adults).</figcaption></figure>'
    f'<p>Among non-Hispanic Asian US adults measured in 2021–2023, <strong>{A30}% had a BMI of 30 or more, and {A275}% had '
    f'27.5 or more</strong>. At the overweight lines, {A25}% had 25 or more and {A23}% had 23 or more (our calculation; 95% '
    'confidence intervals in the method note).</p>'
    '</section>')

sec_hist = (
    '<section id="history" class="content-section flow"><h2>Where 25 and 30 came from</h2><ul>'
    '<li><strong>Before 1998:</strong> US surveys counted adults as overweight from a BMI of 27.8 for men and 27.3 for women, '
    f'the 85th percentiles at ages 20 to 29 in NHANES II ({ext("nhlbi98", "NHLBI, 1998")}).</li>'
    '<li><strong>1995:</strong> WHO graded adult thinness at BMI 18.5, 17 and 16 '
    f'({ext("who1995", "WHO, 1995")}).</li>'
    '<li><strong>1998:</strong> NIH’s clinical guidelines set overweight at 25 to 29.9 and obesity at 30 or more '
    f'({ext("nhlbi98", "NHLBI, 1998")}).</li>'
    '<li><strong>2000:</strong> WHO’s report on obesity set out obese classes I, II and III and concluded that a coherent '
    f'system based on BMI “should be adopted internationally” ({ext("who2000", "WHO, 2000")}).</li></ul>'
    f'<figure class="figure">{svg_98}<figcaption>US adults at or above the overweight line under the pre-1998 survey lines '
    'and under today’s line, 2021–2023. Our calculation from CDC NHANES.</figcaption></figure>'
    f'<p>Nobody’s weight changed in 1998, but the line did. Measured today, <strong>{MV["all"]}% of US adults have a BMI '
    f'from 25 up to the old lines</strong>: overweight now, not before 1998. That is {MV["men"]}% of men and '
    f'{MV["women"]}% of women; the men’s old line sat higher, at 27.8. Under the old lines, {OLD["all"]}% of adults would '
    f'count as overweight or above; under today’s, {AB25["all"]}% do (our calculation).</p>'
    '<p>In the 239-study analysis, the risk of death in never-smokers climbed band by band from 25 upward: '
    f'{GBMC[0][1]:.2f} times the reference at 25 to 27.4, {GBMC[1][1]:.2f} at 27.5 to 29.9 and {GBMC[2][1]:.2f} at 30 to '
    f'34.9 ({GBMC_CITE}).</p>'
    '</section>')

sec_near = (
    '<section id="near-a-line" class="content-section flow"><h2>Close to a line</h2>'
    f'<p>Because BMI is reported to one decimal, a category can change with a pound or two. At 5′10″, a BMI of 29.9 and a '
    f'BMI of 30.0 are {GAP} lb apart, and each whole BMI unit is {UNIT70} lb.</p>'
    '</section>')

sec_lim = (
    '<section id="limits" class="content-section flow"><h2>What a category can’t tell you</h2>'
    '<p>CDC calls BMI “a quick, low-cost, and reliable screening measure” but notes that it “does not directly measure body '
    f'fat” and “does not distinguish between fat, muscle, and bone mass” ({ext("cdc_about", "CDC")}). For one person, CDC '
    'says BMI “should be considered with other factors”. A muscular person can reach the overweight range with little body '
    'fat; the <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> and the '
    '<a href="/body-fat-calculator/">body fat calculator</a> measure what BMI misses, and '
    '<a href="/blog/bmi-limitations/">BMI limitations</a> covers the rest.</p>'
    '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC. {ext("cdc_cat", "Adult BMI Categories")}: the adult categories, the three obesity classes and the “regardless of '
    'age, sex, or race” rule.',
    f'CDC. {ext("cdc_child", "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'CDC. {ext("cdc_about", "About Body Mass Index (BMI)")}: what BMI measures and what it misses.',
    f'CDC. {ext("cdc_formula", "Calculating BMI")}: the formulas in metric and US units.',
    f'NHLBI. {ext("nhlbi98", "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")} '
    '(NIH, 1998): the categories and the pre-1998 survey lines.',
    f'WHO. {ext("who1995", "Physical status: the use and interpretation of anthropometry")} (Technical Report Series 854, '
    '1995): thinness grades.',
    f'WHO. {ext("who2000", "Obesity: preventing and managing the global epidemic")} (Technical Report Series 894, 2000): '
    'obese classes I, II and III.',
    f'WHO Expert Consultation. {ext("who2004", "The Lancet, 2004")}: BMI in Asian populations and the public-health action '
    'points.',
    f'NICE (UK). {ext("nice", "Overweight and obesity management, guideline NG246")}: lower BMI thresholds for people from '
    'some ethnic backgrounds (recommendation 1.9.11, 2022).',
    f'CDC. {ext("ndpp", "National Diabetes Prevention Program eligibility")}: BMI of 25 or higher, 23 or higher for Asian '
    'American adults.',
    f'The Global BMI Mortality Collaboration. {ext("gbmc", "Body-mass index and all-cause mortality")} (Lancet, 2016): '
    'hazard ratios by BMI band in never-smokers without chronic disease.',
    f'Winter JE, et al. {ext("winter", "American Journal of Clinical Nutrition, 2014")}: BMI and mortality in adults 65 and '
    'over.',
    f'Emmerich SD, et al. {ext("db508", "NCHS Data Brief No. 508")} (Sep 2024): obesity and severe obesity in US adults, '
    'August 2021–August 2023.',
    f'Fryar CD, Afful J, Saif NT. {ext("he111", "NCHS Health E-Stat 111")}: overweight and obesity in US adults.',
    f'NCHS. {ext("he119", "Health E-Stat 119")}: underweight in US adults.',
    f'CDC {ext("bmx", "NHANES August 2021–August 2023")} exam files (DEMO_L, BMX_L): our calculation of the share of adults '
    f'aged 20 and over in each category by age and sex ({N_ALL:,}: {N_MEN:,} men, {N_WOM:,} women), the 1998 line move and '
    f'the Asian action points ({AN} non-Hispanic Asian adults).',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> US adults: CDC NHANES August 2021–August 2023, adults aged 20 and over '
    'with a measured height and weight, pregnant women excluded, weighted with the exam weights; crude shares, BMI as CDC '
    f'records it, to one decimal. The shares reproduce NCHS’s published crude rates: obesity {REPRO["obesity_all"]["nchs"]}% '
    f'({REPRO["obesity_men"]["nchs"]}% of men, {REPRO["obesity_women"]["nchs"]}% of women), class 3 '
    f'{REPRO["class3_all"]["nchs"]}%, overweight {REPRO["overweight_all"]["nchs"]}% and underweight '
    f'{REPRO["underweight_all"]["nchs"]}%. 95% confidence intervals by Taylor linearisation (15 design degrees of freedom); '
    'a difference is stated only when its interval excludes zero. The 1998 move counts men with a BMI of 25.0 to 27.7 and '
    f'women with 25.0 to 27.2. Non-Hispanic Asian adults ({AN}): BMI 30 or more {A30}% (95% CI {ci(AS["bmi_30_plus"])}), '
    f'27.5 or more {A275}% ({ci(AS["bmi_27_5_plus"])}), 25 or more {A25}% ({ci(AS["bmi_25_plus"])}), 23 or more {A23}% '
    f'({ci(AS["bmi_23_plus"])}). Weights where each obesity class starts: the lightest whole pound and whole kilogram whose '
    'BMI, rounded to one decimal, is in the class.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/age-bmi-calculator/', 'BMI calculator by age'),
        ('/kids-bmi-calculator/', 'BMI calculator for children and teens'), ('/body-fat-calculator/', 'Body fat calculator'),
        ('/ideal-weight/', 'Ideal weight calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/bmi-chart/', 'BMI chart'), ('/blog/healthy-bmi-range/', 'Healthy BMI range'),
        ('/blog/bmi-chart-women/', 'BMI chart for women'), ('/blog/bmi-chart-men/', 'BMI chart for men'),
        ('/blog/bmi-by-age/', 'BMI by age'), ('/blog/underweight-bmi-risks/', 'Underweight BMI risks'),
        ('/blog/bmi-limitations/', 'BMI limitations'), ('/us-obesity-statistics/', 'US obesity statistics')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_cat, sec_ob, sec_uw, sec_wm, sec_child, sec_asian, sec_hist, sec_near, sec_lim,
     sec_faq, sec_src, sec_rel]) + ' </div></main>')
for a, _ in TOC:
    assert f'<section id="{a}"' in main, a
probs = table_problems(main)
assert not probs, probs

# ---------------------------------------------------------------- head: meta, OG, JSON-LD (title and H1 kept, D-28)
H1 = 'BMI Categories: All Weight Classifications Explained'
assert f'<title>{H1} (2026)</title>' in src and f'<h1>{H1}</h1>' in src
DESC = ('Adult BMI categories, from underweight to obesity classes 1 to 3, with the share of US adults in each by age, the '
        '1998 line change and the Asian cut-offs.')
assert len(DESC) <= 160, len(DESC)
OG_T = 'BMI categories: six adult categories and the three obesity classes'
OG_D = ('The adult BMI categories and obesity classes, the share of US adults in each by age (CDC data, our calculation), '
        'the 1998 line change and the lower lines for Asian adults.')
OG_IMG = 'https://calculatemybmi.net/assets/images/og/bmi-categories-us-adults.png'


def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out


src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG_IMG}">', src)
src = sub1(r'<meta property="article:modified_time" content="[^"]*">',
           f'<meta property="article:modified_time" content="{TODAY}T00:00:00Z">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG_IMG}">', src)

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
types = [json.loads(b.group(1))['@type'] for b in blocks]
assert types == ['Article', 'BreadcrumbList', 'FAQPage'], types
art = json.loads(blocks[0].group(1))
art.update({'headline': H1, 'image': OG_IMG, 'description': DESC, 'dateModified': TODAY})
assert art['datePublished'] == '2026-01-15'
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
for b, new in ((blocks[2], faq_ld), (blocks[0], art)):            # back to front, so offsets stay valid
    src = src[:b.start(1)] + ' ' + json.dumps(new, ensure_ascii=False) + ' ' + src[b.end(1):]

i, j = src.index('<main'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('<main') == 1 and '<article' not in src
open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>', ' ', main)).split())
print(f'blog/bmi-categories/index.html written: {len(src):,} bytes, {words:,} words in <main>, {len(FAQ)} FAQ, '
      f'{len(TEXTS)} SVG labels checked')
