#!/usr/bin/env python3
"""CMB-018 CHART-MEN — rebuilds /blog/bmi-chart-men/ to the D-14 guide pattern (DESIGN.md "Guide pages"; its sister page,
/blog/bmi-chart-women/, applied it in CMB-014): intro, answer block and key takeaways, a hero figure, contents chips,
the chart as a real table plus a printable chart image, the 5′10″ answers, a flat FAQ whose JSON-LD equals the visible
answers, sources and method, one related block, one 680 px reading column.

Wedge (owner's SERP pastes of 2026-10-22, US/English, not personalized: "bmi chart for men", "ideal weight for 5 10
male", "men height weight chart"): the results are CDC's and NIH's calculators and tables, hospital charts and Reddit
threads. Their 5′10″ numbers disagree (132, 140, 144 or 149 lb at the bottom of the range), the AI Overview's height
table is wrong at every row, and the questions people ask are about muscle ("with muscle"), the waist (40 inches) and
age. None shows where US men actually fall on the chart. This page does:
  1. US men on the chart: at every height from 5′4″ to 6′2″ most men have a BMI of 25 or more (bcm_stats.py, CDC NHANES
     2021-2023, which reproduces NCHS Data Brief 508 for men at every age); the 5′10″ answers with US men of that height;
  2. muscle or fat: body fat on CDC's DXA scans at the same BMI, and how often BMI and body fat disagree, both ways
     (bcm_dxa.py, NHANES 2011-2018);
  3. the waist: for men the waist-to-height ratio, not the 102 cm line, decides the June 2026 ADA thresholds.

Every number comes from bcm_stats.json, bcm_dxa.json, research/home-build/home_stats.json (the men's BMI curve, as the
homepage's rank), research/average-weight/avgw_results.json (average weight by height and age, the /average-weight/
tables), the weight-table gate's own rule (scripts/check_weight_tables.py), or a source verified in chat (constants
below, each with its source). Round once: a printed figure is formatted from the unrounded (4-decimal) value.

usage: python3 gen_bcm.py REPO_ROOT STATS_JSON DXA_JSON
Runs once, on blog/bmi-chart-men/index.html as it stood at dcd6b47; kept as the build record. The page is written with
{TODAY} in its schema dateModified; apply_build.py puts in the apply date (manifest "today": true).
"""
import sys, os, re, json, html, math
from decimal import Decimal, ROUND_HALF_UP

ROOT, STATS, DXA = sys.argv[1], sys.argv[2], sys.argv[3]
S = json.load(open(STATS))
X = json.load(open(DXA))
HOME = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
AVGW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json')))
PAGE = os.path.join(ROOT, 'blog/bmi-chart-men/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds, round1          # the CMB-008 gate's own rule

SITE = 'https://calculatemybmi.net'
URL = SITE + '/blog/bmi-chart-men/'

# ---------------------------------------------------------------- formatting (round once)
def f1(x): return f'{x:.1f}'
def pc(x): return f'{x:.1f}%'
def share(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{x:.1f}%'
def whole(x): return int(math.floor(x + 0.5))
def dcm(inches): return str((Decimal(str(inches)) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))
LB_PER_KG = 2.2046226218
def kg1(lb): return str((Decimal(str(lb)) / Decimal(str(LB_PER_KG))).quantize(Decimal('0.1'), ROUND_HALF_UP))
def ft(h): return f'{h // 12}′{h % 12}″'
def spoken(h): return f'{h // 12} feet' + (f' {h % 12} inch' + ('es' if h % 12 > 1 else '') if h % 12 else '')
TALL_IN = int(204 / 2.54)                                         # 80.3 in: half of 204 cm is the 102 cm line
assert TALL_IN == 80 and 2 * 102 == 204

# ---------------------------------------------------------------- numbers: US men, 2021-2023 (bcm_stats.py)
C = S['categories']
AGES = ('20-39', '40-59', '60+')
def p(g, c): return C[g][c]['pct']
assert [C[g]['n'] for g in ('all',) + AGES] == [2680, 672, 762, 1246]
assert [f1(p(g, 'healthy')) for g in ('all',) + AGES] == ['24.0', '28.3', '20.7', '22.5']
assert [f1(p(g, 'obesity')) for g in ('all',) + AGES] == ['39.2', '34.3', '45.4', '38.0']         # = NCHS Data Brief 508
assert [f1(p(g, 'class_3')) for g in ('all',) + AGES] == ['6.7', '6.1', '9.2', '4.3']           # = NCHS Data Brief 508
CI_H = C['all']['healthy']['ci95']; assert [f1(x) for x in CI_H] == ['20.5', '27.4']
HALF = [(C[g][c]['ci95'][1] - C[g][c]['ci95'][0]) / 2 for g in ('all',) + AGES
        for c in ('underweight', 'healthy', 'overweight', 'obesity', 'class_3')]
HALF_HI = whole(max(HALF)); assert HALF_HI == 6, max(HALF)
DIF = S['age_differences']
STATED = ('healthy_20-39_minus_40-59', 'healthy_20-39_minus_60+', 'obesity_40-59_minus_20-39', 'obesity_40-59_minus_60+',
          'class_3_40-59_minus_20-39', 'class_3_40-59_minus_60+', 'overweight_60+_minus_40-59')
for k in STATED:
    assert DIF[k]['excludes_0'] and DIF[k]['diff'] > 0, k                  # stated on the page
for k in ('obesity_60+_minus_20-39', 'class_3_20-39_minus_60+', 'healthy_60+_minus_40-59'):
    assert not DIF[k]['excludes_0'], k                                     # not stated
MED_M = HOME['men']['table']['p50']; assert f1(MED_M) == '28.2'
QM = HOME['men']['p1_p99']
def pct_curve(q, b):
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
def n_rank(x): return 99 if x > 99 else whole(x)                          # the rank's n(): Math.round, capped at 99
def higher(b): return n_rank(100 - pct_curve(QM, b))                      # men with a strictly higher BMI (CMB-012 rule)
# Waist at the same BMI and the 2026 ADA thresholds.
WB = S['waist']['by_bmi']
W102 = {c: WB[c]['waist_102_plus']['pct'] for c in ('healthy', 'overweight', 'obesity')}
WHT = {c: WB[c]['whtr_05_plus']['pct'] for c in ('healthy', 'overweight', 'obesity')}
assert [f1(W102[c]) for c in W102] == ['0.6', '30.8', '94.3'] and [f1(WHT[c]) for c in WHT] == ['42.9', '93.7', '100.0']
N_WAIST = S['waist']['n_measured']; assert N_WAIST == 2596
ADA = S['ada2026']
ADA_N, ADA_OB, ADA_BMI = ADA['n'], ADA['obesity_ada']['pct'], ADA['obesity_bmi_only']['pct']
assert (ADA_N, f1(ADA_OB), f1(ADA_BMI)) == (2659, '73.4', '39.5') and ADA['difference']['excludes_0']
ADA_OUT = ADA['n_left_out']; assert ADA_OUT == 21 and ADA_N + ADA_OUT == C['all']['n']
ADA_25 = ADA['parts_pts']['nonasian_25_29_9']; ADA_CEN = ADA['bmi25_30_nonasian_central']['pct']
assert (f1(ADA_25), f1(ADA_CEN)) == ('30.9', '93.4')
# By height: men whose BMI is 25 or more (every CI above half), the weight quartiles of /average-weight/.
BH = S['by_height']
HH = list(range(64, 75))
assert [int(k) for k in BH] == HH
for h in HH:
    assert BH[str(h)]['bmi25_plus']['ci95'][0] > 50, h                     # "most men" holds at every height
for h in HH:
    assert BH[str(h)]['weight_q'][1] > gate_bounds('lb', h, h * 2.54, 1)[1], h   # the median man is above the healthy range
OVER_LO = min(BH[str(h)]['bmi25_plus']['pct'] for h in HH); OVER_HI = max(BH[str(h)]['bmi25_plus']['pct'] for h in HH)
assert (whole(OVER_LO), whole(OVER_HI)) == (64, 81)
A70 = S['at_70in']
assert [f1(A70[c]['pct']) for c in ('healthy', 'overweight', 'obesity')] == ['22.3', '38.3', '39.4']
N70 = BH['70']['n']; AV70 = BH['70']['weight_mean']; MD70 = BH['70']['weight_q'][1]
assert (N70, f1(AV70), f1(MD70)) == (313, '205.5', '199.1')   # CMB-019: NCHS's percentile method (was 199.3)
AV72 = AVGW['men']['height']['72']['wt']['mean']; assert f1(AV72) == '215.7'
for h in HH:                                                              # the by-height table = /average-weight/'s men's rows
    a = AVGW['men']['height'][str(h)]['wt']
    assert abs(BH[str(h)]['weight_mean'] - a['mean']) < 1e-3 and BH[str(h)]['weight_n'] == a['n'] == BH[str(h)]['n'], h
    assert BH[str(h)]['weight_mean'] > gate_bounds('lb', h, h * 2.54, 1)[1], h      # the average man is above the range too
assert f1(BH['71']['weight_mean']) == '215.1' and min(BH[str(h)]['n'] for h in HH) == 76 and max(BH[str(h)]['n'] for h in HH) == 374
BMI7079 = AVGW['men']['age']['70–79']['bmi']['mean']; assert f1(BMI7079) == '29.4'
# Body fat at the same BMI, men 20-59, CDC DXA 2011-2018 (bcm_dxa.py; the body fat chart's numbers).
DX = X['by_cat']
assert [f1(DX[c]['p50']) for c in ('healthy', 'over', 'obese')] == ['22.1', '26.9', '31.6']
DIS = X['disagree']
LEAN_OV, LEAN_OB, FAT_H = (DIS['over_at_or_below_healthy_median']['pct'], DIS['obese_at_or_below_healthy_median']['pct'],
                           DIS['healthy_at_or_above_over_median']['pct'])
assert (f1(LEAN_OV), f1(LEAN_OB), f1(FAT_H)) == ('11.8', '1.4', '14.0')
MISS = {c: X['missing_scan'][c]['pct'] for c in ('healthy', 'over', 'obese')}               # men without a valid scan
assert [f1(MISS[c]) for c in MISS] == ['18.7', '18.2', '26.1']

# ---------------------------------------------------------------- numbers: the chart (the gate's rule, every inch 5'2"-6'6")
CATS6 = [('under', 'Underweight', 'under 18.5'), ('healthy', 'Healthy weight', '18.5–24.9'),
         ('over', 'Overweight', '25–29.9'), ('ob1', 'Class 1 obesity', '30–34.9'),
         ('ob2', 'Class 2 obesity', '35–39.9'), ('ob3', 'Class 3 obesity', '40 or more')]
CHART = []
for h in range(62, 79):
    cm = h * 2.54
    cells = [(gate_bounds('lb', h, cm, b), gate_bounds('kg', h, cm, b)) for b in range(6)]
    for b in range(5):                                            # contiguous bands, no gaps or overlaps
        assert cells[b][0][1] + 1 == cells[b + 1][0][0] and cells[b][1][1] + 1 == cells[b + 1][1][0], (h, b)
    CHART.append((h, cells))
BY = {h: cells for h, cells in CHART}
def hb(h, band=1): return BY[h][band]                            # ((minLb, maxLb), (minKg, maxKg))
assert hb(70) == ((129, 173), (59, 78)) and hb(70, 2) == ((174, 208), (79, 94)) and hb(70, 3)[0][0] == 209
assert hb(72) == ((137, 183), (62, 83)) and hb(69) == ((125, 168), (57, 76)) and hb(62)[0] == (101, 136)
assert hb(78)[0] == (160, 215)
def bmi_lb(lb, h): return round1(703.0 * lb / (h * h))
# The 5'10" weights the SERPs ask about, and round steps between them.
W70 = (140, 150, 160, 170, 180, 185, 190, 200, 210, 215, 230)
CATNAME = {0: 'Underweight', 1: 'Healthy weight', 2: 'Overweight', 3: 'Class 1 obesity', 4: 'Class 2 obesity', 5: 'Class 3 obesity'}
def cat_of(b): return 0 if b < 18.5 else 1 if b < 25 else 2 if b < 30 else 3 if b < 35 else 4 if b < 40 else 5
assert [bmi_lb(w, 70) for w in (140, 170, 180, 185, 200, 215)] == [20.1, 24.4, 25.8, 26.5, 28.7, 30.8]
EX_LB = 185; EX_BMI = bmi_lb(EX_LB, 70); EX_OVER = EX_LB - hb(70)[0][1]; assert (EX_BMI, EX_OVER) == (26.5, 12)

# ---------------------------------------------------------------- sources verified in chat
# NIH printable BMI table (registry nih-bmi-table-2022; PDF re-read 2026-10-22): heights 58-76 in, one column per whole
#   BMI from 19 to 54; the 70-inch row reads 132 lb under BMI 19, 167 under 24, 174 under 25, 209 under 30.
NIH_COLS, NIH_70 = (19, 54), (132, 167)
# CDC About BMI (registry cdc-about-bmi): "BMI does not distinguish between fat, muscle, and bone mass".
# NHLBI 1998 (registry nhlbi-1998-obesity-guidelines): waist over 102 cm (40 in) for men, over 88 cm (35 in) for women,
#   "in conjunction with BMI" at 25 to 34.9.
# NICE NG246 (registry nice-ng246-ethnicity-thresholds): waist-to-height ratio for adults with a BMI under 35: 0.4-0.49
#   healthy central adiposity, 0.5-0.59 increased, 0.6 or more high, both sexes and all ethnicities (2022 recommendation).
# ADA 2026 (registry ada-2026-obesity-standards; recommendations 3.3a/3.3b): non-Asian: BMI >= 30, or >= 25 with waist-to-
#   height >= 0.5 or waist >= 102 cm (men); Asian: >= 27.5, or >= 23 with the ratio >= 0.5 or waist >= 90 cm (men);
#   nonpregnant adults; "Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to underdiagnosis
#   of obesity". Table 3.1 gives the men's lines in inches as >= 40 in (non-Asian) and >= 35.5 in (Asian) (the section's
#   PDF, read 2026-10-22 by the CMB-018 fact-check and in chat); the page pairs each cm line with the ADA's own inches.
# CDC National DPP (registry cdc-ndpp-eligibility): BMI of 25 or higher, 23 or higher for Asian American adults.
# Global BMI Mortality Collaboration 2016 (registry gbmc-2016-bmi-mortality; abstract re-read 2026-10-22): 3,951,455
#   never-smokers without pre-existing disease in 189 studies, first 5 years of follow-up excluded; all-cause mortality
#   minimal at BMI 20.0-25.0; per 5 units above 25, HR 1.52 at ages 35-49 and 1.21 at 70-89; men 1.51, women 1.30.
GB_N = '3.95 million'; GB_MEN, GB_WOMEN, GB_35_49, GB_70_89 = 51, 30, 52, 21
# Winter et al. 2014 (registry winter-2014-bmi-mortality-65): 197,940 people aged 65 and over; reference BMI 23-23.9;
#   "the risk of mortality increased in older people with a BMI <23.0"; risk began to increase above 33.
# Owner's SERP paste "ideal weight for 5 10 male" (2026-10-22): the AI Overview quotes "170 to 185 pounds" as a range
#   Reddit users favor for 5′10″; its BMI values here are ours.

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'nih_tbl': 'https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_tbl.pdf',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'nhlbi_tg': 'https://www.ncbi.nlm.nih.gov/books/NBK2004/',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'ada': 'https://doi.org/10.2337/doci26-0003',
    'ada_pr': 'https://diabetes.org/newsroom/press-releases/new-standards-care-overweight-and-obesity-section-screening-diagnosis-0',
    'ndpp': 'https://www.cdc.gov/diabetes-prevention/eligible-lifestyle-change-program/index.html',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
}
import csv
REG = {r['domain']: r for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}
for k, d in (('cdc_cat', 'cdc-adult-bmi-categories'), ('cdc_child', 'cdc-child-bmi-categories'), ('cdc_formula', 'cdc-calculating-bmi'),
             ('cdc_about', 'cdc-about-bmi'), ('nih_tbl', 'nih-bmi-table-2022'), ('db508', 'nhanes-adult-obesity-2021-2023'),
             ('dxx', 'nhanes-2011-2018-dxa'), ('nice', 'nice-ng246-ethnicity-thresholds'), ('ada', 'ada-2026-obesity-standards'),
             ('ndpp', 'cdc-ndpp-eligibility'), ('winter', 'winter-2014-bmi-mortality-65'), ('gbmc', 'gbmc-2016-bmi-mortality')):
    assert REG[d]['url'] == U[k], (k, REG[d]['url'])                  # every link is the registry's
assert REG['nhanes-2021-2023-exam-files']['url'] == U['bmx'] and REG['ada-2026-obesity-standards']['endpoint'] == U['ada_pr']
assert U['nhlbi_tg'] in REG['nhlbi-1998-obesity-guidelines']['notes']             # the registry's text deep link (chapter 4)
ADA_CITE = ext(U['ada'], 'ADA, 2026')

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS, VBW = [], [], {}

def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827', inside=None):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s, inside))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'

def rect(svg, x, y, w, h, fill, rid=None, extra='', tip=None, track=True):
    if track: RECTS.append((svg, x, y, x + w, y + h, rid))
    t = f'<title>{esc(tip)}</title>' if tip else ''
    tag = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}'
    return f'{tag}>{t}</rect>' if t else f'{tag}/>'

TINT = {'under': '#dbeafe', 'healthy': '#d1fae5', 'over': '#fde68a', 'obese': '#fecaca'}     # DESIGN.md category tints
EDGE = {'under': '#1e3a8a', 'healthy': '#14532d', 'over': '#713f12', 'obese': '#7f1d1d'}     # the same hues' ink
MEN, INK, MUTED, GRID = '#4338ca', '#111827', '#4b5563', '#d1d5db'                              # men's series color (DESIGN.md)
LEG = [('under', 'Underweight'), ('healthy', 'Healthy weight'), ('over', 'Overweight'), ('obese', 'Obesity')]

# Hero: where US men sit on the chart. One row per height 5'4"-6'2", the CDC bands in pounds, the middle half of US men's
# weights at that height (bar) and their median (tick).
VBW['hero'] = W1 = 320
HX0, HX1, HLO, HHI = 46, 312, 100, 260
def hx(lb): return HX0 + (min(max(lb, HLO), HHI) - HLO) * (HX1 - HX0) / (HHI - HLO)
TOP1, PITCH1, BH1 = 56, 20, 14
hero = [text('hero', W1 / 2, 17, 'Where US men sit on the chart', 14, weight=700),
        text('hero', W1 / 2, 36, 'Bar: the middle half of men; tick: median', 12, fill='#374151')]
for i, h in enumerate(HH):
    y = TOP1 + i * PITCH1
    cells = BY[h]
    hero.append(text('hero', HX0 - 6, y + 11, ft(h), 12, anchor='end', fill='#1f2937'))
    segs = [('under', HLO, cells[0][0][1] + 0.5), ('healthy', cells[1][0][0] - 0.5, cells[1][0][1] + 0.5),
            ('over', cells[2][0][0] - 0.5, cells[2][0][1] + 0.5), ('obese', cells[3][0][0] - 0.5, HHI)]
    tips = {'under': f'≤ {cells[0][0][1]} lb', 'healthy': f'{cells[1][0][0]}–{cells[1][0][1]} lb',
            'over': f'{cells[2][0][0]}–{cells[2][0][1]} lb', 'obese': f'≥ {cells[3][0][0]} lb'}
    for k, a, b in segs:
        x0, x1 = hx(a) + 0.5, hx(b) - 0.5
        hero.append(rect('hero', x0, y, x1 - x0, BH1, TINT[k], rid='band',
                         tip=f'{ft(h)}, {dict(LEG)[k].lower()}: {tips[k]}'))
    q = BH[str(h)]['weight_q']
    hero.append(rect('hero', hx(q[0]), y + BH1 / 2 - 3, hx(q[2]) - hx(q[0]), 6, MEN, rid='mid', extra=' rx="3"',
                     tip=f'US men at {ft(h)}: middle half {f1(q[0])}–{f1(q[2])} lb, median {f1(q[1])} lb '
                         f'({BH[str(h)]["weight_n"]} men)'))
    hero.append(rect('hero', hx(q[1]) - 1.5, y - 1, 3, BH1 + 2, INK, rid='tick'))
axis_y = TOP1 + len(HH) * PITCH1 + 2
hero.append(f'<line x1="{HX0}" y1="{axis_y}" x2="{HX1}" y2="{axis_y}" stroke="{GRID}" stroke-width="1"/>')
for lb in (100, 140, 180, 220, 260):
    hero.append(f'<line x1="{hx(lb):.1f}" y1="{axis_y}" x2="{hx(lb):.1f}" y2="{axis_y + 4}" stroke="#9ca3af" stroke-width="1"/>')
    if lb == 260: hero.append(text('hero', HX1 + 6, axis_y + 17, '260 lb', 12, anchor='end', fill=MUTED))
    else: hero.append(text('hero', hx(lb), axis_y + 17, str(lb), 12, fill=MUTED))
ly = axis_y + 42
for i, (k, lab) in enumerate(LEG):
    x = 14 + (i % 2) * 150; yy = ly + (i // 2) * 20
    hero.append(rect('hero', x, yy - 10, 12, 12, TINT[k], rid='swatch', extra=f' stroke="{EDGE[k]}" stroke-width="1"'))
    hero.append(text('hero', x + 18, yy, lab, 12, anchor='start', fill='#1f2937'))
yy = ly + 40
hero.append(rect('hero', 14, yy - 7, 22, 6, MEN, rid='swatch', extra=' rx="3"'))
hero.append(text('hero', 42, yy, 'Middle half of US men', 12, anchor='start', fill='#1f2937'))
hero.append(rect('hero', 214, yy - 11, 3, 14, INK, rid='swatch'))
hero.append(text('hero', 223, yy, 'Median', 12, anchor='start', fill='#1f2937'))
hero.append(text('hero', W1 / 2, yy + 26, 'CDC NHANES 2021–2023; our calculation', 12, fill=MUTED))
H1V = yy + 34
svg_hero = (f'<svg viewBox="0 0 {W1} {H1V}" width="{W1}" height="{H1V}" role="img" aria-labelledby="fig-hero-t fig-hero-d" font-family="inherit">'
            '<title id="fig-hero-t">BMI chart for men with US men on it: most weigh more than the healthy range</title>'
            '<desc id="fig-hero-d">One row per height from 5 feet 4 inches to 6 feet 2 inches, split into underweight, healthy '
            'weight, overweight and obesity at each height’s limits in pounds (CDC categories). Across each row, a bar marks the '
            'middle half of US men of that height and a tick their median weight. '
            + ' '.join(f'{spoken(h)}: healthy {BY[h][1][0][0]} to {BY[h][1][0][1]} pounds; US men’s median '
                       f'{f1(BH[str(h)]["weight_q"][1])} pounds, middle half {f1(BH[str(h)]["weight_q"][0])} to '
                       f'{f1(BH[str(h)]["weight_q"][2])}.' for h in HH)
            + ' Our calculation from CDC NHANES measurements, August 2021 to August 2023.</desc>' + ''.join(hero) + '</svg>')

# Muscle or fat: body fat of US men aged 20-59 in each BMI category (10th-90th line, middle-half box, median tick), with
# the healthy-BMI median as a dashed line.
VBW['fat'] = W2 = 320
FX0, FX1, FLO, FHI = 20, 300, 10, 40
def fx(v): return FX0 + (v - FLO) * (FX1 - FX0) / (FHI - FLO)
fat = [text('fat', W2 / 2, 17, 'Body fat at each BMI category', 14, weight=700),
       text('fat', W2 / 2, 36, 'US men aged 20 to 59, CDC body scans (%)', 12, fill='#374151')]
ROWS2 = [('healthy', 'Healthy BMI, 18.5–24.9'), ('over', 'Overweight, 25–29.9'), ('obese', 'Obesity, 30 or more')]
TOP2, PITCH2 = 64, 50
for i, (k, lab) in enumerate(ROWS2):
    v = DX[k]; y = TOP2 + i * PITCH2
    fat.append(text('fat', FX0, y, f'{lab}: median {pc(v["p50"])}', 12, anchor='start', weight=600, fill='#1f2937'))
    yc = y + 18
    fat.append(f'<line x1="{fx(v["p10"]):.1f}" y1="{yc}" x2="{fx(v["p90"]):.1f}" y2="{yc}" stroke="{MEN}" stroke-width="1.5"/>')
    fat.append(rect('fat', fx(v['p25']), yc - 8, fx(v['p75']) - fx(v['p25']), 16, MEN, rid='box',
                    extra=f' fill-opacity="0.16" stroke="{MEN}" stroke-width="1"',
                    tip=f'{lab}: 10th to 90th percentile {pc(v["p10"])}–{pc(v["p90"])}, middle half {pc(v["p25"])}–'
                        f'{pc(v["p75"])}, median {pc(v["p50"])} ({v["n"]:,} men)'))
    fat.append(rect('fat', fx(v['p50']) - 1.5, yc - 10, 3, 20, INK, rid='tick'))
ref_x = fx(DX['healthy']['p50'])
for i in range(len(ROWS2)):
    yc = TOP2 + i * PITCH2 + 18
    fat.append(f'<line x1="{ref_x:.1f}" y1="{yc - 13}" x2="{ref_x:.1f}" y2="{yc + 13}" stroke="#6b7280" stroke-width="1" '
               'stroke-dasharray="3 3"/>')
ax2 = TOP2 + len(ROWS2) * PITCH2 - 6
fat.append(f'<line x1="{FX0}" y1="{ax2}" x2="{FX1}" y2="{ax2}" stroke="{GRID}" stroke-width="1"/>')
for v in (10, 20, 30, 40):
    fat.append(f'<line x1="{fx(v):.1f}" y1="{ax2}" x2="{fx(v):.1f}" y2="{ax2 + 4}" stroke="#9ca3af" stroke-width="1"/>')
    fat.append(text('fat', fx(v) - (5 if v == 40 else 0), ax2 + 17, f'{v}%', 12, fill=MUTED))
fat.append(text('fat', W2 / 2, ax2 + 40, 'Dashed: median at a healthy BMI', 12, fill='#374151'))
fat.append(text('fat', W2 / 2, ax2 + 60, 'CDC NHANES 2011–2018; our calculation', 12, fill=MUTED))
H2V = ax2 + 68
svg_fat = (f'<svg viewBox="0 0 {W2} {H2V}" width="{W2}" height="{H2V}" role="img" aria-labelledby="fig-fat-t fig-fat-d" font-family="inherit">'
           '<title id="fig-fat-t">Body fat of US men aged 20 to 59 at each BMI category</title>'
           '<desc id="fig-fat-d">Three box plots on a body fat scale from 10 to 40 percent: the line spans the 10th to 90th '
           'percentile, the box the middle half, the tick the median. '
           + ' '.join(f'{lab}: median {pc(DX[k]["p50"])}, middle half {pc(DX[k]["p25"])} to {pc(DX[k]["p75"])}, 10th to 90th '
                      f'percentile {pc(DX[k]["p10"])} to {pc(DX[k]["p90"])}.' for k, lab in ROWS2)
           + ' A dashed line marks the median at a healthy BMI. Our calculation from CDC NHANES 2011 to 2018 DXA scans.</desc>'
           + ''.join(fat) + '</svg>')

def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r) and a[6] != r[5]:
            raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r} / {r[5]!r}')
for svg, x0, y0, x1, y1, s, _ in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in the owner's US/English pastes of 2026-10-22, not personalized ("bmi chart for men", "ideal weight for 5
# 10 male", "men height weight chart"), each question once: the healthy BMI, the 5′10″ weights in order of weight asked
# (170, 180, 200, 215) then the low one (140), the ledger's 6-foot question ("healthy weight 6 foot male" and its group),
# height and age, then the 2026 chart and the body-type question.
B70, B72, B69 = hb(70), hb(72), hb(69)
FAQ = [
    ('What is a healthy BMI for a man?',
     f'<strong>18.5 to 24.9</strong>, the same as for women: CDC bases adult categories on BMI “regardless of age, sex, or '
     f'race” ({ext(U["cdc_cat"], "CDC")}). Under 18.5 is underweight, 25 to 29.9 overweight and 30 or more obesity. '
     f'{pc(p("all", "healthy"))} of US men have a BMI in the healthy range, and the median US man has a BMI of {f1(MED_M)} '
     '(our calculation from CDC measurements, 2021–2023).'),
    ('Is 170 lbs overweight for a 5′10″ man?',
     f'No. At 5′10″, 170 lb is a BMI of {bmi_lb(170, 70)}, inside the healthy range for that height, {B70[0][0]} to '
     f'{B70[0][1]} lb ({ext(U["cdc_cat"], "CDC categories")}). Overweight starts at {hb(70, 2)[0][0]} lb.'),
    ('Is 5′10″ 180 lbs fat?',
     f'By BMI it is overweight: 180 lb at 5′10″ is a BMI of {bmi_lb(180, 70)}, and the healthy range ends at {B70[0][1]} lb. '
     'BMI can’t say how much of that is fat. On CDC’s body scans (2011–2018), only '
     f'{pc(LEAN_OV)} of men aged 20 to 59 with an overweight BMI carried no more body fat than the median man with a '
     f'healthy BMI, {pc(DX["healthy"]["p50"])} (our calculation). Waist size is the next check: at 5′10″, a waist of 35 '
     f'inches is half the height, the point where NICE starts to class central adiposity as increased '
     f'({ext(U["nice"], "NICE")}).'),
    ('Is 200 lbs heavy for a 5′10″ man?',
     f'It is overweight by BMI: {bmi_lb(200, 70)} at 5′10″. Obesity starts at {hb(70, 3)[0][0]} lb. It is also close to what '
     f'US men of that height weigh: their average is {f1(AV70)} lb and their median {f1(MD70)} lb (our calculation from CDC '
     f'measurements, {N70} men, 2021–2023).'),
    ('Is 215 lbs at 5′10″ obese?',
     f'Yes, by BMI. At 5′10″, 215 lb is a BMI of {bmi_lb(215, 70)}, which CDC calls class 1 obesity (30 to 34.9); obesity '
     f'starts at {hb(70, 3)[0][0]} lb at that height ({ext(U["cdc_cat"], "CDC")}). Of US men who are 5′10″, '
     f'{pc(A70["obesity"]["pct"])} have a BMI of 30 or more (our calculation).'),
    ('Is 140 lbs at 5′10″ skinny?',
     f'Not by BMI. At 5′10″, 140 lb is a BMI of {bmi_lb(140, 70)}, in the healthy range; underweight starts below '
     f'{B70[0][0]} lb, a BMI under 18.5 ({ext(U["cdc_cat"], "CDC")}). About {higher(bmi_lb(140, 70))}% of US men have a '
     'higher BMI (our calculation).'),
    ('How much should a 6-foot man weigh?',
     f'At 6′0″ (182.9 cm), a healthy weight is <strong>{B72[0][0]} to {B72[0][1]} lb ({B72[1][0]} to {B72[1][1]} kg)</strong>. '
     f'Overweight runs from {hb(72, 2)[0][0]} to {hb(72, 2)[0][1]} lb and obesity starts at {hb(72, 3)[0][0]} lb. The average US '
     f'man of that height weighs {f1(AV72)} lb (our calculation; <a href="/average-weight/">average weight by height</a>).'),
    ('What is the correct weight and height for men?',
     'There isn’t one correct weight: every height has a range of weights with a healthy BMI of 18.5 to 24.9 '
     f'({ext(U["cdc_cat"], "CDC")}). At 5′10″ it is {B70[0][0]} to {B70[0][1]} lb, at 6′0″ {B72[0][0]} to {B72[0][1]} lb, and '
     '<a href="#chart">the chart</a> has every height from 5′2″ to 6′6″.'),
    ('How much should I weigh for my height and age?',
     'For men 20 and over, age doesn’t change the answer: find your height on <a href="#chart">the chart</a>, and the '
     f'healthy cell holds your range ({ext(U["cdc_cat"], "CDC")}). Under 20, BMI is read as a percentile for age and sex '
     f'instead ({ext(U["cdc_child"], "CDC")}); the <a href="/kids-bmi-calculator/">BMI calculator for children and '
     'teens</a> works it out.'),
    ('How much should a 5′9″ 70 year old man weigh?',
     f'The same as at any adult age: {B69[0][0]} to {B69[0][1]} lb ({B69[1][0]} to {B69[1][1]} kg) at 5′9″ '
     f'({ext(U["cdc_cat"], "CDC")}). US men aged 70 to 79 have an average BMI of {f1(BMI7079)} (our calculation). In adults '
     'aged 65 and over, the risk of death was higher below a BMI of 23 and began to rise at about 33, compared with 23 to '
     f'23.9 ({ext(U["winter"], "Winter et al., 2014")}), and muscle loss can make BMI miss obesity in older adults '
     f'({ADA_CITE}).'),
    ('What is the new BMI chart for 2026?',
     'There isn’t a new chart. CDC’s adult categories are unchanged, on a page last reviewed in March 2024 '
     f'({ext(U["cdc_cat"], "CDC")}). What changed in June 2026 is the American Diabetes Association’s definition of obesity: '
     'for a man of non-Asian background, a BMI of 25 to 29.9 now counts as obesity when the waist is at least half the height '
     f'or 102 cm (40 in) or more, with lower lines for men of Asian background ({ADA_CITE}). {pc(ADA_OB)} of US men meet '
     f'those thresholds, against {pc(ADA_BMI)} of the same {ADA_N:,} men by BMI alone (our calculation; the {ADA_OUT} men '
     'whose class depends on a waist that wasn’t measured are left out).'),
    ('What body type lives the longest?',
     f'In {GB_N} never-smokers without certain chronic diseases at the start, pooled from 189 studies, death rates were lowest at '
     f'a BMI of 20 to 25. Above 25 they rose faster in men than in women: {GB_MEN}% against {GB_WOMEN}% per 5 BMI units '
     f'({ext(U["gbmc"], "Global BMI Mortality Collaboration, 2016")}). That is an association, not proof that a given '
     'weight lengthens life.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
H1 = 'BMI Chart for Men: Healthy Weight by Height'
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">How much should a 5′10″ man weigh? Is 180 pounds too much at that height, or is it muscle? And '
    'does the chart change after 60?</p>'
    f'<p class="intro-text">Only {pc(p("all", "healthy"))} of US men have a BMI in CDC’s healthy range of 18.5 to 24.9, and '
    'at every height from 5′4″ to 6′2″ most men are above it (our calculation from CDC measurements, 2021–2023). Since June '
    f'2026 the American Diabetes Association also counts waist size: {pc(ADA_OB)} of US men meet its new thresholds for '
    f'obesity, against {pc(ADA_BMI)} of the same {ADA_N:,} men by BMI alone (our calculation).</p>'
    '<p class="intro-text">Below: <a href="#chart">the chart for every height</a> from 5′2″ to 6′6″ in pounds and kilograms, '
    'the 5′10″ answers, and what muscle, waist size and age change.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>A healthy BMI for men is 18.5 to 24.9</strong>, the same range as for women (CDC). Under '
    f'18.5 is underweight, 25 to 29.9 overweight and 30 or more obesity. At 5′10″, the healthy weight is {B70[0][0]} to '
    f'{B70[0][1]} lb ({B70[1][0]} to {B70[1][1]} kg); at 6′0″, {B72[0][0]} to {B72[0][1]} lb ({B72[1][0]} to {B72[1][1]} kg).</p><ul>'
    f'<li><strong>{pc(p("all", "healthy"))} of US men have a healthy BMI</strong> and {pc(p("all", "obesity"))} have obesity '
    '(our calculation from CDC measurements, 2021–2023; NCHS publishes the same obesity rate).</li>'
    '<li><strong>Most men with an overweight BMI carry more body fat than the typical man with a healthy BMI.</strong> On '
    'CDC’s body scans (2011–2018), only '
    f'{pc(LEAN_OV)} of men aged 20 to 59 with a BMI of 25 to 29.9 carried no more body fat than the median man with a '
    'healthy BMI (our calculation).</li>'
    '<li><strong>The waist counts too.</strong> US guidelines flag a man’s waist over 40 inches, and since June 2026 the '
    'American Diabetes Association counts a waist of at least half the height toward obesity from a BMI of 25, or 23 for '
    'men of Asian background.</li>'
    '<li>The chart is for men 20 and over and doesn’t change with age.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This guide is for information only. BMI is a '
    'screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>Each row is one height, its weights in pounds colored by CDC category. The bar '
            'across it is the middle half of US men of that height and the tick their median weight: in every row the median '
            'man is above the healthy range.</figcaption></figure>')

CHIPS = (('chart', 'Chart'), ('five-ten', '5′10″'), ('us-men', 'US men'), ('muscle', 'Muscle or fat'), ('waist', 'Waist'),
         ('age', 'Age'), ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

# The chart table: every inch 5'2"-6'6", six categories, pounds with kilograms below, each unit worked out on its own.
def cell(lbr, kgr):
    (l0, l1), (k0, k1) = lbr, kgr
    if l0 is None: return f'&le; {l1} lb <span class="cell-kg">({k1} kg)</span>'
    if l1 is None: return f'&ge; {l0} lb <span class="cell-kg">({k0} kg)</span>'
    return f'{l0}&ndash;{l1} lb <span class="cell-kg">({k0}&ndash;{k1} kg)</span>'
chart_rows = ''.join(
    f'<tr id="h-{h // 12}-{h % 12}"><th scope="row">{ft(h)} <span class="cell-cm">({dcm(h)} cm)</span></th>'
    + ''.join(f'<td class="c-{k}">{cell(*cells[b])}</td>' for b, (k, _, _) in enumerate(CATS6)) + '</tr>'
    for h, cells in CHART)
CHART_IMG = '/assets/images/charts/bmi-chart-men.png'
CHART_W, CHART_H = 1640, 1628                                    # written by chart_bcm.py
_png = os.path.join(ROOT, CHART_IMG.lstrip('/'))
if os.path.exists(_png):
    from PIL import Image
    assert Image.open(_png).size == (CHART_W, CHART_H), Image.open(_png).size
sec_chart = (
    '<section id="chart" class="content-section flow"><h2>BMI chart for men by height and weight</h2>'
    '<p>Each cell is the range of whole pounds, with kilograms below, that gives a BMI in that category at that height. '
    f'The healthy weight runs from <strong>{hb(62)[0][0]} to {hb(62)[0][1]} lb at 5′2″</strong> to '
    f'<strong>{hb(78)[0][0]} to {hb(78)[0][1]} lb at 6′6″</strong>.</p>'
    '<div class="table-responsive"><table class="weight-chart"><caption>BMI chart for men, 5′2″ to 6′6″</caption><thead><tr>'
    '<th scope="col">Height</th>'
    + ''.join(f'<th scope="col">{name}<span class="th-sub">BMI <span class="nw">{rng}</span></span></th>' for _, name, rng in CATS6)
    + f'</tr></thead><tbody>{chart_rows}</tbody></table></div>'
    '<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, falls in each category at the '
    'height shown. Each unit is worked out on its own, so the kilograms are not conversions of the pounds. Cut-offs: '
    f'{ext(U["cdc_cat"], "CDC Adult BMI Categories")}. Kilogram limits are for the exact height in inches; the centimeters '
    'shown are rounded to one decimal. Each row has its own link, for example #h-5-10 for 5′10″.</p>'
    '<p><strong>To read it,</strong> find your height in the left column and the cell that holds your weight; its column is '
    'your BMI category. For the exact number, use the <a href="/men-bmi-calculator/">BMI calculator for men</a> or the '
    'printable chart below.</p>'
    f'<figure class="figure figure--wide"><a href="{CHART_IMG}"><img src="{CHART_IMG}" width="{CHART_W}" height="{CHART_H}" '
    'loading="lazy" decoding="async" alt="Printable BMI chart for men: BMI at each height from 5 feet 2 inches to 6 feet 6 '
    'inches and every 10 pounds from 100 to 300 pounds, with cells colored by CDC category"></a><figcaption>Printable BMI chart '
    'for men: the BMI at every height from 5′2″ to 6′6″ and every 10 lb from 100 to 300 lb. Open the image to print or '
    'save it.'
    '</figcaption></figure>'
    '</section>')

def w70_row(w):
    b = bmi_lb(w, 70); c = cat_of(b)
    hi = higher(b)
    return (f'<tr><th scope="row">{w} lb <span class="cell-kg">({kg1(w)} kg)</span></th><td class="num">{b:.1f}</td>'
            f'<td><span class="nowrap"><span class="cat-dot {("underweight", "normal", "overweight", "obese", "obese", "obese-severe")[c]}" '
            f'aria-hidden="true"></span>{CATNAME[c].split(" ", 1)[0]}</span>{(" " + CATNAME[c].split(" ", 1)[1]) if " " in CATNAME[c] else ""}'
            f'</td><td class="num">{hi}%</td></tr>')
sec_510 = (
    '<section id="five-ten" class="content-section flow"><h2>How much should a 5′10″ man weigh?</h2>'
    f'<p>At 5′10″ (177.8 cm), <strong>a healthy weight is {B70[0][0]} to {B70[0][1]} lb ({B70[1][0]} to {B70[1][1]} kg)</strong>, '
    f'a BMI of 18.5 to 24.9. Overweight runs from {hb(70, 2)[0][0]} to {hb(70, 2)[0][1]} lb ({hb(70, 2)[1][0]} to '
    f'{hb(70, 2)[1][1]} kg), and obesity starts at {hb(70, 3)[0][0]} lb ({hb(70, 3)[1][0]} kg).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Weights at 5′10″: BMI and category</caption><thead><tr>'
    '<th scope="col">Weight</th><th scope="col" class="num">BMI</th><th scope="col">Category</th>'
    '<th scope="col" class="num">All US men with a higher BMI</th></tr></thead><tbody>'
    + ''.join(w70_row(w) for w in W70) + '</tbody></table></div>'
    f'<p class="source-note">BMI = weight × 703 ÷ 70², rounded to one decimal ({ext(U["cdc_formula"], "CDC formula")}); '
    f'categories: {ext(U["cdc_cat"], "CDC")}. The last column is our calculation from CDC measurements of {C["all"]["n"]:,} '
    'men aged 20 and over of every height, 2021–2023, read from the BMI curve the site’s calculators use, so it matches '
    'what they show; men with the same BMI count on neither side, and the exact share can differ by a point after '
    'rounding.</p>'
    f'<p><strong>US men of that height are mostly above the range.</strong> Of men measured at 5′10″ to the nearest inch, '
    f'{pc(A70["healthy"]["pct"])} have a healthy BMI, {pc(A70["overweight"]["pct"])} are overweight and '
    f'{pc(A70["obesity"]["pct"])} have obesity. Their average weight is {f1(AV70)} lb and their median {f1(MD70)} lb (our '
    f'calculation from CDC measurements, {N70} men, 2021–2023; <a href="/average-weight/">average weight by height</a> has '
    'every height).</p>'
    '<p>Other sources give other numbers for 5′10″. NIH’s printable BMI table starts at a BMI of 19, so its 5′10″ row '
    f'reads {NIH_70[0]} lb under BMI 19 and {NIH_70[1]} lb under 24 ({ext(U["nih_tbl"], "NIH")}); CDC’s healthy range starts '
    f'at 18.5, which is {B70[0][0]} lb. “Ideal weight” formulas give one weight per height instead of a range; the '
    '<a href="/ideal-weight/">ideal weight calculator</a> shows four of them. Some online answers put the ideal at 170 '
    f'to 185 lb, which by BMI runs from {bmi_lb(170, 70)}, healthy, to {bmi_lb(185, 70)}, overweight.</p>'
    f'<p><strong>Example.</strong> {EX_LB} lb at 5′10″ is {EX_LB} × 703 ÷ 70² = {EX_BMI}, rounded to one decimal: overweight, '
    f'{EX_OVER} lb above the healthy range for that height.</p>'
    '</section>')

cat_cols = (('healthy', '18.5–24.9', 'healthy'), ('overweight', '25–29.9', 'overweight'), ('obesity', '30 or more', 'obesity'),
            ('class_3', '40 or more', 'class 3'))
men_rows = ''.join(
    f'<tr><th scope="row">{lab}</th>' + ''.join(f'<td class="num">{f1(p(g, c))}%</td>' for c, _, _ in cat_cols) + '</tr>'
    for g, lab in (('20-39', '20–39'), ('40-59', '40–59'), ('60+', '60+'), ('all', 'All 20+')))
sec_us = (
    '<section id="us-men" class="content-section flow"><h2>Where US men fall on the chart</h2>'
    f'<div class="stat-callout"><div class="stat-callout-value">{pc(p("all", "healthy"))}</div><div class="stat-callout-text">'
    'of US men aged 20 and over have a BMI of 18.5 to 24.9, August 2021–August 2023.</div><div class="stat-callout-source">'
    f'Source: our calculation from {ext(U["bmx"], "CDC NHANES 2021–2023")} measurements ({C["all"]["n"]:,} men; 95% '
    f'confidence interval {pc(CI_H[0])} to {pc(CI_H[1])})</div></div>'
    f'<p>Most US men are above the healthy range: {pc(p("all", "overweight"))} are overweight and '
    f'<strong>{pc(p("all", "obesity"))} have obesity</strong>, including {pc(p("all", "class_3"))} with a BMI of 40 or more; '
    f'{pc(p("all", "underweight"))} are underweight. '
    f'The median US man has a BMI of {f1(MED_M)}, in the overweight range (our calculation).</p>'
    f'<p>At every height from 5′4″ to 6′2″, between {whole(OVER_LO)}% and {whole(OVER_HI)}% of '
    'men have a BMI of 25 or more, and both the median and the average man weigh more than the healthy range allows (the '
    'figure at the top and the table below).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>US men by height: healthy weight and average weight'
    '</caption><thead><tr><th scope="col">Height</th><th scope="col" class="num">Healthy weight<span class="th-sub">lb</span></th>'
    '<th scope="col" class="num">Average weight<span class="th-sub">lb</span></th><th scope="col" class="num">BMI 25 or more</th>'
    '</tr></thead><tbody>'
    + ''.join(f'<tr><th scope="row">{ft(h)}</th><td class="num">{hb(h)[0][0]}–{hb(h)[0][1]}</td>'
              f'<td class="num">{f1(BH[str(h)]["weight_mean"])}</td><td class="num">{pc(BH[str(h)]["bmi25_plus"]["pct"])}</td></tr>'
              for h in HH)
    + '</tbody></table></div>'
    '<p class="source-note">Healthy weight: whole pounds with a BMI of 18.5 to 24.9 (CDC categories). Average weight and the '
    'share with a BMI of 25 or more: our calculation from CDC NHANES August 2021–August 2023, men aged 20 and over by '
    f'measured height to the nearest inch ({min(BH[str(h)]["n"] for h in HH)} to {max(BH[str(h)]["n"] for h in HH)} men '
    'per height; survey-weighted). The averages are the ones on <a href="/average-weight/">average weight by height</a>.</p>'
    f'<p><strong>Men aged 20 to 39 are the most likely to have a healthy BMI</strong>, at {pc(p("20-39", "healthy"))}, '
    f'compared with {pc(p("40-59", "healthy"))} at 40 to 59 and {pc(p("60+", "healthy"))} at 60 and over. Obesity peaks at 40 to '
    f'59 ({pc(p("40-59", "obesity"))}, against {pc(p("20-39", "obesity"))} at 20 to 39 and {pc(p("60+", "obesity"))} at 60 '
    f'and over), and so does a BMI of 40 or more ({pc(p("40-59", "class_3"))}). Men 60 and over are more often overweight '
    f'than men aged 40 to 59 ({pc(p("60+", "overweight"))} against {pc(p("40-59", "overweight"))}).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>US men by BMI category and age (%)</caption>'
    '<thead><tr><th scope="col">Age</th>'
    + ''.join(f'<th scope="col" class="num">{h}</th>' for _, h, _ in cat_cols)
    + f'</tr></thead><tbody>{men_rows}</tbody></table></div>'
    f'<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023 measured heights and weights '
    f'({C["all"]["n"]:,} men aged 20 and over: {C["20-39"]["n"]:,} aged 20 to 39, {C["40-59"]["n"]:,} aged 40 to 59 and '
    f'{C["60+"]["n"]:,} aged 60 and over; survey-weighted). The columns are CDC’s healthy weight, overweight and obesity '
    'ranges; obesity includes the class 3 column (BMI 40 or more), and underweight (under 18.5) makes up the rest: '
    f'{pc(p("20-39", "underweight"))}, {pc(p("40-59", "underweight"))} and {pc(p("60+", "underweight"))} by age. The '
    'obesity and BMI 40 or more shares match NCHS’s '
    f'published rates for men at every age ({ext(U["db508"], "Data Brief 508")}). Each share has a 95% margin of error of up '
    f'to ±{HALF_HI} points, and each difference by age stated above is larger than its own margin of error.</p>'
    '<p>For what US men weigh at each height, see <a href="/average-weight/">average weight by height</a>; '
    '<a href="/us-obesity-statistics/">US obesity statistics</a> has the trends since 1960.</p>'
    '</section>')

sec_muscle = (
    '<section id="muscle" class="content-section flow"><h2>Muscle or fat? Body fat at the same BMI</h2>'
    '<p>BMI can’t tell muscle from fat: CDC notes that it “does not distinguish between fat, muscle, and bone mass” '
    f'({ext(U["cdc_about"], "CDC")}). CDC’s survey also measured body fat directly in 2011–2018, with whole-body DXA scans up '
    'to age 59, '
    'so the two can be compared in the same men.</p>'
    f'<figure class="figure">{svg_fat}<figcaption>Body fat of US men in each BMI category: the median (tick), the middle half '
    '(box) and the 10th to 90th percentile (line). The dashed line is the median at a healthy BMI.</figcaption></figure>'
    f'<p>The median man with a healthy BMI carried {pc(DX["healthy"]["p50"])} body fat, with an overweight BMI '
    f'{pc(DX["over"]["p50"])} and with obesity {pc(DX["obese"]["p50"])}. <strong>Only {pc(LEAN_OV)} of men with an '
    'overweight BMI carried no more body fat than the median man with a healthy BMI</strong>, and '
    f'{pc(LEAN_OB)} of men with obesity. The mismatch runs the other way too: {pc(FAT_H)} of men with a healthy BMI carried '
    f'at least as much body fat as the median man with an overweight BMI (our calculation from {ext(U["dxx"], "NHANES 2011–2018")} '
    'scans).</p>'
    '<p>BMI alone can’t tell which group a man is in. A waist measurement is a quick next check (next section), the '
    '<a href="/body-fat-calculator/">body fat calculator</a> estimates body fat from a few measurements, and the '
    '<a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows where a reading sits among US men. '
    '<a href="/blog/bmi-for-athletes/">BMI for athletes</a> covers training.</p>'
    '</section>')

waist_rows = ''.join(
    f'<tr><th scope="row">{lab}<span class="th-sub">BMI {rng}</span></th><td class="num">{share(W102[c])}</td>'
    f'<td class="num">{share(WHT[c])}</td></tr>'
    for c, lab, rng in (('healthy', 'Healthy weight', '18.5–24.9'), ('overweight', 'Overweight', '25–29.9'),
                        ('obesity', 'Obesity', '30 or more')))
sec_waist = (
    '<section id="waist" class="content-section flow"><h2>Waist size and the 2026 ADA standards</h2>'
    '<p>US guidelines treat a man’s waist over 40 inches (102 cm) as a sign of higher risk, mainly at a BMI of 25 to 34.9 '
    f'({ext(U["nhlbi_tg"], "NHLBI")}). For adults with a BMI under 35, NICE (UK) classes a waist-to-height ratio of 0.5 to '
    f'0.59 as increased central adiposity and 0.6 or more as high ({ext(U["nice"], "NICE")}).</p>'
    f'<p>In June 2026 the American Diabetes Association put the waist into its definition of obesity ({ext(U["ada_pr"], "ADA")}). '
    'For men of non-Asian background, obesity is a BMI of 30 or more, or a BMI of 25 or more with a waist at least half the '
    'height or a waist of 102 cm (40 in) or more. For men of Asian background the lines are a BMI of 27.5, or 23 with the '
    f'same ratio or a waist of 90 cm (35.5 in) ({ADA_CITE}). For comparison, CDC’s National Diabetes Prevention Program uses '
    'a BMI of 23 or higher, instead of 25, as one of its eligibility criteria for Asian American adults '
    f'({ext(U["ndpp"], "CDC")}).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>US men with a large waist, by BMI category (%)</caption>'
    '<thead><tr><th scope="col">BMI category</th><th scope="col" class="num">Waist 102 cm or more</th>'
    f'<th scope="col" class="num">Waist half the height or more</th></tr></thead><tbody>{waist_rows}</tbody></table></div>'
    f'<p><strong>For almost every man, half the height is the lower of the two waist lines:</strong> it is under 102 cm for '
    f'anyone shorter than 204 cm, about {ft(TALL_IN)}. At an overweight BMI, {pc(WHT["overweight"])} of US '
    f'men have a waist at least half their height, but only {pc(W102["overweight"])} reach 102 cm; at a healthy BMI, '
    f'{pc(WHT["healthy"])} and {pc(W102["healthy"])} (our calculation, {N_WAIST:,} men with a measured waist).</p>'
    f'<div class="stat-callout"><div class="stat-callout-value">{pc(ADA_OB)}</div><div class="stat-callout-text">of US men meet '
    f'the 2026 ADA obesity thresholds, against {pc(ADA_BMI)} of the same {ADA_N:,} men by BMI alone.</div>'
    '<div class="stat-callout-source">Source: our calculation from CDC NHANES 2021–2023 measured BMI, waist and height '
    f'({ADA_N:,} men); 95% confidence interval {pc(ADA["obesity_ada"]["ci95"][0])} to {pc(ADA["obesity_ada"]["ci95"][1])}'
    '</div></div>'
    f'<p>Most of the gap, {f1(ADA_25)} points, comes from men of non-Asian background with a BMI of 25 to 29.9: '
    f'{pc(ADA_CEN)} of them have a waist at or over one of the lines. The <a href="/bmi-chart/">BMI chart for adults</a> '
    'shows the same comparison for women and men, and the <a href="/blog/waist-to-height-ratio/">waist-to-height ratio '
    'guide</a> shows how to measure.</p>'
    '</section>')

sec_age = (
    '<section id="age" class="content-section flow"><h2>Does the chart change with age?</h2>'
    '<p><strong>Not for adults.</strong> CDC uses one set of categories for every man aged 20 and over, “regardless of age, '
    f'sex, or race” ({ext(U["cdc_cat"], "CDC")}). What changes with age is what a given BMI is linked to:</p><ul>'
    f'<li><strong>Death rates.</strong> In {GB_N} never-smokers without certain chronic diseases at the start, leaving out the '
    'first five years of follow-up, death rates were lowest at a BMI of 20 to 25. Per 5 BMI units above 25, the risk was '
    f'{GB_35_49}% higher for BMI measured at ages 35 to 49 and {GB_70_89}% higher at 70 to 89, and the rise was steeper in '
    f'men than in women ({GB_MEN}% against {GB_WOMEN}%; {ext(U["gbmc"], "Global BMI Mortality Collaboration, 2016")}).</li>'
    '<li><strong>Older adults.</strong> In adults 65 and over, compared with a BMI of 23 to 23.9, the risk of death was '
    f'higher below 23 and began to rise at about 33 ({ext(U["winter"], "Winter et al., 2014")}). That is an association, '
    'not a separate range.</li>'
    '<li><strong>Muscle.</strong> “Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to '
    f'underdiagnosis of obesity” ({ADA_CITE}).</li></ul>'
    f'<p>So a 70-year-old man of 5′9″ has the same healthy range as a 30-year-old: {B69[0][0]} to {B69[0][1]} lb '
    f'({B69[1][0]} to {B69[1][1]} kg). US men aged 70 to 79 have an average BMI of {f1(BMI7079)} (our calculation, '
    '2021–2023).</p>'
    '<p>Under 20, BMI is read as a percentile for age and sex, not on this chart; the '
    '<a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it out for ages 2 to 19. '
    '<a href="/blog/bmi-by-age/">BMI by age</a> explains how the adult range applies across life, and the '
    '<a href="/blog/healthy-bmi-range/">healthy BMI range</a> guide has the mortality data behind it.</p>'
    '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the adult cut-offs and the “regardless of age, sex, or race” rule '
    '(page last reviewed March 2024).',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formulas in US units and metric.',
    f'CDC. {ext(U["cdc_about"], "About Body Mass Index (BMI)")}: what BMI does and doesn’t measure.',
    f'NIH (NHLBI). {ext(U["nih_tbl"], "Body Mass Index Table")}: one column for each whole BMI from {NIH_COLS[0]} to '
    f'{NIH_COLS[1]}.',
    f'CDC {ext(U["bmx"], "NHANES August 2021–August 2023")} demographics and body measures files (DEMO_L, BMX_L): our '
    f'calculation of the share of men aged 20 and over in each BMI category by age ({C["all"]["n"]:,} men) and by measured '
    f'height, of waist size by BMI category ({N_WAIST:,} with a measured waist) and of the 2026 ADA thresholds '
    f'({ADA_N:,} men), weighted with the exam weights; the same files give the average weight at each height on '
    '<a href="/average-weight/">average weight by height</a>.',
    f'Emmerich SD, et al. {ext(U["db508"], "NCHS Data Brief No. 508")} (Sep 2024): obesity and severe obesity in US adults '
    'by sex and age, August 2021–August 2023.',
    f'CDC NHANES 2011–2018 {ext(U["dxx"], "whole-body DXA scans")}: our calculation of body fat by BMI category, men aged 20 '
    'to 59 (the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> has the method).',
    f'NHLBI. {ext(U["nhlbi_tg"], "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")}, '
    'treatment guidelines chapter (NIH, 1998): waist cut-offs for women and men.',
    f'NICE (UK). {ext(U["nice"], "Overweight and obesity management, guideline NG246")} (2025): waist-to-height ratio '
    'categories for adults with a BMI under 35, a 2022 recommendation.',
    'American Diabetes Association Professional Practice Committee for Obesity. '
    f'{ext(U["ada"], "Screening, Diagnosis, Evaluation, and Staging of Obesity in Adults: Standards of Care in Overweight and Obesity—2026")}: '
    f'obesity thresholds with waist size (recommendations 3.3a and 3.3b); {ext(U["ada_pr"], "ADA press release")}, June 2026.',
    f'CDC. {ext(U["ndpp"], "National Diabetes Prevention Program eligibility")}: BMI of 25 or higher, 23 or higher for Asian '
    'American adults.',
    f'The Global BMI Mortality Collaboration. {ext(U["gbmc"], "Body-mass index and all-cause mortality")} (Lancet, 2016): '
    'never-smokers in 189 studies; hazard ratios by age at measurement and by sex.',
    f'Winter JE, et al. {ext(U["winter"], "BMI and all-cause mortality in older adults: a meta-analysis")} (Am J Clin Nutr, '
    '2014).',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Men aged 20 and over with a measured height and weight in NHANES August '
    '2021–August 2023, weighted with CDC’s exam weights; heights are measured heights rounded to the nearest inch. Shares '
    'carry 95% confidence intervals from Taylor linearization over the survey’s 15 strata, and the page states a difference '
    'between age groups only when its interval excludes zero. Body fat comes from whole-body DXA scans of men aged 20 to 59 '
    f'in NHANES 2011–2018, four survey cycles pooled; men without a valid scan are left out ({pc(MISS["healthy"])} of men '
    f'with a healthy BMI, {pc(MISS["over"])} with an overweight BMI and {pc(MISS["obese"])} with obesity). The ADA '
    f'comparison leaves out the {ADA_OUT} men whose class depends on a waist that wasn’t measured, and applies the lines '
    'for adults of Asian background to the men CDC records as non-Hispanic Asian. The median BMI and the last column of the '
    '5′10″ table read the homepage’s BMI curve for men, as its calculator does; the weight percentiles by height are the '
    'ones on average weight by height, and the body fat percentiles the body fat chart’s. Every figure is rounded once, '
    'from the unrounded estimate, except that rank, which reads percentile curves stored to two decimals. NHLBI gives the '
    'men’s waist line as over 102 cm (over 40 in) and the ADA as 102 cm or more (40 in or more in its Table 3.1); the waist '
    'shares on this page use the measured waist in centimeters.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/', 'BMI calculator'), ('/body-fat-calculator/', 'Body fat calculator'),
        ('/ideal-weight/', 'Ideal weight calculator'), ('/age-bmi-calculator/', 'BMI calculator by age')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/bmi-chart/', 'BMI chart for adults'), ('/blog/bmi-chart-women/', 'BMI chart for women'),
        ('/average-weight/', 'Average weight by height'), ('/body-fat-percentage-chart/', 'Body fat percentage chart'),
        ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'), ('/blog/healthy-bmi-range/', 'Healthy BMI range')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_chart, sec_510, sec_us, sec_muscle, sec_waist, sec_age, sec_faq, sec_src, sec_rel])
    + ' </div></main>')
assert 'style="' not in re.sub(r'(?s)<svg.*?</svg>', '', main)
assert all(f'id="{a}"' in main for a, _ in CHIPS)

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'BMI Chart for Men: Healthy Weight by Height (lb and kg)'
DESC = ('The BMI chart for men from 5′2″ to 6′6″: healthy, overweight and obesity weights at every height in lb and kg, '
        'where US men fall, and what muscle changes.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'BMI chart for men: healthy weight at every height'
OG_D = ('The chart from 5′2″ to 6′6″ in lb and kg, the 5′10″ answers, where US men fall on it, and what muscle, waist size '
        'and age change (CDC data, our calculation).')
OG_ALT = ('Chart: for each height from 5 feet 4 to 6 feet 2, the weights of the middle half of US men over the underweight, '
          'healthy, overweight and obesity bands.')
for s_ in (DESC, OG_T, OG_D, OG_ALT): assert '"' not in s_
PREF = SITE + '/assets/images/preferred/bmi-chart-men-'
IMG16, IMG43, IMG11 = PREF + '16x9.png', PREF + '4x3.png', PREF + '1x1.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">',
           f'<meta property="og:image" content="{IMG16}"><meta property="og:image:alt" content="{OG_ALT}">', src)
src = sub1(r'<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
src = sub1(r'(?s)<style>.*?</style>', '', src)                           # the page-level .bmi-chart style (§5 [P2])
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1 and '<style' not in src

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 2, len(blocks)                                   # the old page had no FAQPage block
types = [json.loads(b.group(1))['@type'] for b in blocks]
assert types == ['Article', 'BreadcrumbList'], types
art_old = json.loads(blocks[0].group(1))
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
ORG = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'CalculateMyBMI', 'url': SITE + '/'}
article = {'@context': 'https://schema.org', '@type': 'Article', 'headline': H1, 'description': DESC, 'url': URL,
           'datePublished': art_old['datePublished'], 'dateModified': '{TODAY}', 'inLanguage': 'en-US',
           'isPartOf': {'@type': 'WebSite', 'name': 'CalculateMyBMI', 'url': SITE + '/'}, 'author': PERSON, 'publisher': ORG,
           'image': [IMG11, IMG43, IMG16],
           'mainEntityOfPage': {'@type': 'WebPage', '@id': URL, 'url': URL,
                                'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}}}
assert art_old['datePublished'] == '2026-01-28'
crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': 'Guides', 'item': SITE + '/blog/'},
    {'@type': 'ListItem', 'position': 3, 'name': H1, 'item': URL}]}
faqld = {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
LD = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (article, crumbs, faqld))
start, end = blocks[0].start(), blocks[1].end()
src = src[:start] + LD + src[end:]
assert src.count('{TODAY}') == 1

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'blog/bmi-chart-men/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, {len(FAQ)} FAQ, '
      f'{len(TEXTS)} SVG labels checked; 5\'10" higher: ' + ', '.join(f'{w} lb {bmi_lb(w, 70)} -> {higher(bmi_lb(w, 70))}%' for w in W70))
