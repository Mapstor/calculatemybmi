#!/usr/bin/env python3
"""CMB-014 CHART-WOMEN — rebuilds /blog/bmi-chart-women/ to the D-14 guide pattern (DESIGN.md "Guide pages", as
/blog/healthy-bmi-range/ applied it in CMB-013): intro, answer block and key takeaways, a hero figure, contents chips,
the chart as a real table plus a printable chart image, a flat FAQ whose JSON-LD equals the visible answers, sources
and method, one related block, one 680 px reading column.

Wedge: where US women actually sit on the chart, by age (CDC NHANES August 2021-August 2023, 3,249 women; our
calculation in bcw_stats.py, which reproduces NCHS's published rates for women at every age), and what waist size adds
at the same BMI, including the June 2026 American Diabetes Association obesity thresholds applied to the same women.

Every number on the page comes from bcw_stats.json, research/healthy-range-build/healthy_stats.json,
research/home-build/home_stats.json, research/average-weight/avgw_results.json, research/body-fat/bf_results.json,
the weight-table gate's own rule (scripts/check_weight_tables.py), or a source verified in chat on 2026-10-15
(constants below, each with its source; all listed in "Sources and method").

usage: python3 gen_bcw.py REPO_ROOT STATS_JSON
Runs once, on blog/bmi-chart-women/index.html as it stood at e63e2e1; kept as the build record. The page is written with
{TODAY} in its schema dateModified; apply_build.py puts in the apply date (manifest "today": true), the same clock git
commits with, so research/dates/date_truth.py agrees.
"""
import sys, os, re, json, html

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
HS = json.load(open(os.path.join(ROOT, 'research/healthy-range-build/healthy_stats.json')))
HOME = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
AVGW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json')))
BF = json.load(open(os.path.join(ROOT, 'research/body-fat/bf_results.json')))
PAGE = os.path.join(ROOT, 'blog/bmi-chart-women/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds, round1          # the CMB-008 gate's own rule

# ---------------------------------------------------------------- numbers: US women (our calculation)
C = S['categories']
AGES = ('20-39', '40-59', '60+')
assert [C[a]['n'] for a in ('all_ages',) + AGES] == [3249, 826, 947, 1476]
def p(a, c): return C[a][c]['pct']
assert [p(a, 'healthy') for a in ('all_ages',) + AGES] == [28.1, 33.8, 23.9, 26.5]
assert [p(a, 'obesity') for a in ('all_ages',) + AGES] == [41.3, 36.8, 47.4, 39.6]          # = NCHS Data Brief 508
assert [p(a, 'class_3') for a in ('all_ages',) + AGES] == [12.1, 13.0, 14.7, 8.4]           # = NCHS Data Brief 508
assert all(v['ours'] == v['reference'] or abs(v['ours'] - v['reference']) <= 0.1 for v in S['checks'].values())
for a in ('all_ages',) + AGES:
    assert round(p(a, 'class_1') + p(a, 'class_2') + p(a, 'class_3'), 1) == p(a, 'obesity'), a
    assert C[a]['healthy']['ci95'] == HS['groups']['women'][a]['healthy_ci95'], a     # same as CMB-013
HALF = [(C[a][c]['ci95'][1] - C[a][c]['ci95'][0]) / 2 for a in ('all_ages',) + AGES
        for c in ('underweight', 'healthy', 'overweight', 'obesity', 'class_3')]
HALF_HI = round(max(HALF)); assert HALF_HI == 8, max(HALF)
CI_W = C['all_ages']['healthy']['ci95']; assert CI_W == [24.3, 31.8]
DIF = S['age_differences']
for k in ('healthy_20_39_minus_40_59', 'healthy_20_39_minus_60_plus', 'obesity_40_59_minus_20_39',
          'obesity_40_59_minus_60_plus', 'class_3_20_39_minus_60_plus', 'class_3_40_59_minus_60_plus'):
    assert DIF[k]['ci95'][0] > 0, k                               # stated on the page
assert DIF['healthy_60_plus_minus_40_59']['ci95'][0] < 0 < DIF['healthy_60_plus_minus_40_59']['ci95'][1]   # not stated
MED_W = HOME['women']['table']['p50']; assert MED_W == 28.3
# PAA "Is a 23 BMI chubby?": share of US women with a strictly higher BMI, read from the women's 1st-99th percentile
# curve the homepage rank uses (home_stats.json; CMB-012 rule).
QW = HOME['women']['p1_p99']
def rank(q, b):
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
H23W = round(100 - rank(QW, 23.0)); assert H23W == 81
# Waist at the same BMI and the 2026 ADA thresholds (bcw_stats.py).
WB = S['waist']['by_bmi']
WAIST88 = {c: WB[c]['waist_88_plus']['pct'] for c in ('healthy', 'overweight', 'obesity')}
WHTR = {c: WB[c]['whtr_05_plus']['pct'] for c in ('healthy', 'overweight', 'obesity')}
assert WAIST88 == {'healthy': 16.8, 'overweight': 79.1, 'obesity': 99.2} and WHTR == {'healthy': 50.2, 'overweight': 95.5, 'obesity': 100.0}
ADA = S['ada2026']
ADA_N, ADA_OB, ADA_BMI = ADA['n'], ADA['obesity_ada']['pct'], ADA['obesity_bmi_only']['pct']
assert (ADA_N, ADA_OB, ADA_BMI) == (3216, 69.4, 41.8) and ADA['difference']['ci95'][0] > 0
ADA_CENTRAL = ADA['bmi25_30_nonasian_central']['pct']; assert ADA_CENTRAL == 95.2
ADA_DIFF = ADA['difference']['diff']; ADA_FROM_25 = ADA['difference_parts_pts']['nonasian_25_29_9']
assert (ADA_DIFF, ADA_FROM_25) == (27.7, 24.9)
N_WAIST = S['waist']['n_measured']; assert N_WAIST == 3113
# Body fat from CDC DXA scans, ages 20-59 (research/body-fat/bf_results.json by_bmi medians, as on /body-fat-percentage-chart/).
BFW = {k: BF['f']['by_bmi'][k]['q'][2] for k in ('18.5–24.9', '25–29.9', '30+')}
BF_M = BF['m']['by_bmi']['18.5–24.9']['q'][2]
assert BFW == {'18.5–24.9': 33.4, '25–29.9': 39.5, '30+': 44.0} and BF_M == 22.1
# Average weight of US women at 5'2" and 5'4" (research/average-weight/avgw_results.json, the /average-weight/ table).
AW = AVGW['women']['height']
AVG62, AVG62_N = round(AW['62']['wt']['mean'], 1), AW['62']['wt']['n']
AVG64 = round(AW['64']['wt']['mean'], 1)
LB_PER_KG = 2.2046226218
assert (AVG62, AVG62_N, AVG64) == (165.1, 385, 171.2)
AVG62_KG = round(AVG62 / LB_PER_KG, 1); assert AVG62_KG == 74.9

# ---------------------------------------------------------------- numbers: the chart (the gate's rule, every inch 4'10"-6'0")
CATS6 = [('under', 'Underweight', 'under 18.5'), ('healthy', 'Healthy weight', '18.5–24.9'),
         ('over', 'Overweight', '25–29.9'), ('ob1', 'Class 1 obesity', '30–34.9'),
         ('ob2', 'Class 2 obesity', '35–39.9'), ('ob3', 'Class 3 obesity', '40 or more')]
CHART = []
for h in range(58, 73):
    cm = h * 2.54
    cells = [(gate_bounds('lb', h, cm, b), gate_bounds('kg', h, cm, b)) for b in range(6)]
    for b in range(5):                                            # contiguous bands, no gaps or overlaps
        assert cells[b][0][1] + 1 == cells[b + 1][0][0] and cells[b][1][1] + 1 == cells[b + 1][1][0], (h, b)
    CHART.append((h, cm, cells))
BY = {h: cells for h, cm, cells in CHART}
def hb(h, band=1): return BY[h][band]                            # ((minLb, maxLb), (minKg, maxKg))
assert hb(58) == ((89, 119), (41, 54)) and hb(72) == ((137, 183), (62, 83))
assert hb(62) == ((101, 136), (46, 61)) and hb(63) == ((105, 140), (48, 63)) and hb(64) == ((108, 145), (49, 65))
assert hb(65) == ((111, 149), (51, 68)) and hb(66) == ((115, 154), (52, 70))
assert hb(64, 2) == ((146, 174), (66, 79)) and hb(64, 3)[0][0] == 175 and hb(64, 5) == ((233, None), (106, None))
def bmi_lb(lb, h): return round1(703.0 * lb / (h * h))
def kg_of(lb): return round(lb / LB_PER_KG, 1)
# Worked example: 5'5", 160 lb.
EX_H, EX_LB = 65, 160
EX_BMI = bmi_lb(EX_LB, EX_H); assert EX_BMI == 26.6 and hb(65, 2)[0] == (150, 179)
EX_OVER = EX_LB - hb(65)[0][1]; assert EX_OVER == 11
assert kg_of(EX_LB) == 72.6
# PAA answers at 5'4".
assert bmi_lb(140, 64) == 24.0 and kg_of(140) == 63.5
assert bmi_lb(125, 64) == 21.5 and kg_of(125) == 56.7
LB23 = round(23 * 64 * 64 / 703); assert LB23 == 134 and bmi_lb(LB23, 64) == 23.0
KG23 = round(23 * (64 * 0.0254) ** 2); assert KG23 == 61

# ---------------------------------------------------------------- numbers: sources verified in chat (2026-10-15)
# NIH printable BMI table (NIH Publication No. 22-HL-8190, September 2022): one column per whole BMI 19-54, heights
# 4'10" to 6'4"; the 64-inch row reads 110 lb under BMI 19 and 140 lb under BMI 24.
NIH_COLS, NIH_64 = (19, 54), (110, 140)
# ADA Standards of Care in Overweight and Obesity-2026, section 3 (recs 3.3a-3.3d, Table 3.1; press release 2026-06-29):
# non-Asian background: obesity at BMI >= 30, or BMI >= 25 with waist-to-height >= 0.5 or waist >= 88 cm (women) / 102 cm
# (men); Asian background: BMI >= 27.5, or BMI >= 23 with ratio >= 0.5 or waist >= 80 cm (women) / 90 cm (men).
# Table 3.1 gives 88 cm as 35 inches and 80 cm as 31.5 inches. Scope: nonpregnant adults. "Loss of muscle mass in
# older adults reduces the accuracy of BMI, which may lead to underdiagnosis of obesity."
# CDC "Weight Gain During Pregnancy" (recommendations from the Institute of Medicine; last reviewed 2023-12-13): single
# pregnancy, by BMI before pregnancy: under 18.5, 28-40 lb; 18.5-24.9, 25-35 lb; 25.0-29.9, 15-25 lb; 30.0-39.9 (as the
# page writes it), 11-20 lb.
PREG = [('Under 18.5', 'Underweight', 28, 40), ('18.5–24.9', 'Normal weight', 25, 35),
        ('25.0–29.9', 'Overweight', 15, 25), ('30.0–39.9', 'Obese', 11, 20)]
# CDC Adult BMI Categories page: last reviewed 2024-03-19.
# Winter et al. 2014 (adults 65+): 197,940 people; reference BMI 23-23.9; risk higher below 23, rising from about 33.
# Global BMI Mortality Collaboration 2016: per 5 BMI units above 25 in never-smokers, 52% higher at ages 35-49 and 21% at 70-89.
GB_35_49, GB_70_89 = 52, 21

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'nih_tbl': 'https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_tbl.pdf',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'nhlbi_tg': 'https://www.ncbi.nlm.nih.gov/books/NBK2004/',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'ada': 'https://doi.org/10.2337/doci26-0003',
    'ada_pr': 'https://diabetes.org/newsroom/press-releases/new-standards-care-overweight-and-obesity-section-screening-diagnosis-0',
    'ndpp': 'https://www.cdc.gov/diabetes-prevention/eligible-lifestyle-change-program/index.html',
    'preg': 'https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
}
ADA_CITE = ext(U['ada'], 'ADA, 2026')

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS = [], []          # estimated boxes: (svg, x0, y0, x1, y1, label, inside) ; (svg, x0, y0, x1, y1, rid)
VBW = {}

def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827', inside=None):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s, inside))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'

def rect(svg, x, y, w, h, fill, rid=None, extra='', tip=None):
    RECTS.append((svg, x, y, x + w, y + h, rid))
    t = f'<title>{esc(tip)}</title>' if tip else ''
    if t:
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}>{t}</rect>'
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>'

def bar(svg, x, y, w, h, fill, rid, tip, r=4):
    """Bar with a rounded data end on the right, square at the baseline (dataviz mark spec)."""
    RECTS.append((svg, x, y, x + w, y + h, rid))
    r = min(r, w / 2, h / 2)
    d = (f'M{x:.1f} {y:.1f}h{w - r:.1f}a{r:g} {r:g} 0 0 1 {r:g} {r:g}v{h - 2 * r:.1f}a{r:g} {r:g} 0 0 1 {-r:g} {r:g}'
         f'h{-(w - r):.1f}z')
    return f'<path d="{d}" fill="{fill}"><title>{esc(tip)}</title></path>'

# Category colours: the site's strong shades with white labels, amber base with ink labels (palette validated with the
# dataviz validator: lightness, chroma, CVD and normal-vision separation pass; amber needs labels or a table, both given).
COL = {'under': '#1d4ed8', 'healthy': '#15803d', 'over': '#f59e0b', 'obese': '#b91c1c'}
INK_ON = {'under': '#ffffff', 'healthy': '#ffffff', 'over': '#111827', 'obese': '#ffffff'}
LEG = [('under', 'Underweight'), ('healthy', 'Healthy weight'), ('over', 'Overweight'), ('obese', 'Obesity')]

def legend(svg, x0, y0, items, col_w=150):
    out = []
    for i, (k, lab) in enumerate(items):
        x = x0 + (i % 2) * col_w; y = y0 + (i // 2) * 20
        out.append(rect(svg, x, y - 10, 12, 12, COL[k], rid='swatch'))
        out.append(text(svg, x + 18, y, lab, 12, anchor='start', fill='#1f2937'))
    return ''.join(out)

# Hero: the chart in one picture. One bar per height, 4'10" to 6'0", split at the category limits; 5'4" outlined.
VBW['hero'] = W1 = 320
HX0, HX1, HLO, HHI = 44, 314, 80, 250
def hx(lb): return HX0 + (lb - HLO) * (HX1 - HX0) / (HHI - HLO)
TOP1, PITCH1, BH1 = 52, 17, 11
hero = [text('hero', W1 / 2, 17, 'Healthy weight by height', 14, weight=700),
        text('hero', W1 / 2, 35, f'Outlined: 5′4″, healthy at {hb(64)[0][0]}–{hb(64)[0][1]} lb', 12, fill='#374151')]
for i, (h, cm, cells) in enumerate(CHART):
    y = TOP1 + i * PITCH1
    hero.append(text('hero', HX0 - 6, y + 9.5, f'{h // 12}′{h % 12}″', 12, anchor='end', fill='#1f2937'))
    segs = [('under', HLO, cells[0][0][1] + 0.5), ('healthy', cells[1][0][0] - 0.5, cells[1][0][1] + 0.5),
            ('over', cells[2][0][0] - 0.5, cells[2][0][1] + 0.5), ('obese', cells[3][0][0] - 0.5, HHI)]
    tips = {'under': f'≤ {cells[0][0][1]} lb', 'healthy': f'{cells[1][0][0]}–{cells[1][0][1]} lb',
            'over': f'{cells[2][0][0]}–{cells[2][0][1]} lb', 'obese': f'≥ {cells[3][0][0]} lb'}
    for k, a, b in segs:
        x0, x1 = hx(a) + 1, hx(b) - 1                              # 2 px surface gap between segments
        name = dict(LEG)[k]
        hero.append(rect('hero', x0, y, x1 - x0, BH1, COL[k], rid='seg', tip=f'{h // 12}′{h % 12}″, {name.lower()}: {tips[k]}'))
    if h == 64:
        hero.append(f'<rect x="{HX0 - 2:.1f}" y="{y - 2.5:.1f}" width="{HX1 - HX0 + 4:.1f}" height="{BH1 + 5:.1f}" fill="none" '
                    'stroke="#111827" stroke-width="2" rx="3"/>')
axis_y = TOP1 + len(CHART) * PITCH1 + 2
hero.append(f'<line x1="{HX0}" y1="{axis_y}" x2="{HX1}" y2="{axis_y}" stroke="#d1d5db" stroke-width="1"/>')
for lb in (80, 120, 160, 200, 240):
    hero.append(f'<line x1="{hx(lb):.1f}" y1="{axis_y}" x2="{hx(lb):.1f}" y2="{axis_y + 4}" stroke="#9ca3af" stroke-width="1"/>')
    hero.append(text('hero', hx(lb), axis_y + 17, f'{lb} lb' if lb == 240 else str(lb), 12, fill='#4b5563'))
hero.append(legend('hero', 18, axis_y + 44, LEG))
H1V = axis_y + 44 + 30
svg_hero = (f'<svg viewBox="0 0 {W1} {H1V}" width="{W1}" height="{H1V}" role="img" aria-labelledby="fig-hero-t fig-hero-d" font-family="inherit">'
            '<title id="fig-hero-t">BMI chart for women: the healthy weight rises with height</title>'
            '<desc id="fig-hero-d">One bar per height from 4 feet 10 inches to 6 feet, split into underweight, healthy weight, '
            'overweight and obesity at each height’s limits in pounds. The healthy band runs from '
            f'{hb(58)[0][0]} to {hb(58)[0][1]} pounds at 4 feet 10 inches and from {hb(72)[0][0]} to {hb(72)[0][1]} pounds '
            f'at 6 feet; at 5 feet 4 inches, outlined, it is {hb(64)[0][0]} to {hb(64)[0][1]} pounds. Cut-offs: CDC.</desc>'
            + ''.join(hero) + '</svg>')

# Data chart: US women by BMI category, all ages and by age group (100% stacked bars, 2 px gaps, labels where they fit).
VBW['women'] = W3 = 320
GROUPS = [('all_ages', 'All women 20 and over'), ('20-39', 'Ages 20 to 39'), ('40-59', 'Ages 40 to 59'), ('60+', 'Ages 60 and over')]
SX0, SX1 = 10, 310
st = [text('women', W3 / 2, 17, 'US women by BMI category (%)', 14, weight=700), legend('women', 18, 40, LEG)]
TOP3, PITCH3, BH3 = 80, 48, 22
for i, (key, lab) in enumerate(GROUPS):
    y = TOP3 + i * PITCH3
    st.append(text('women', SX0, y, lab, 12, anchor='start', weight=600, fill='#1f2937'))
    vals = [('under', p(key, 'underweight')), ('healthy', p(key, 'healthy')), ('over', p(key, 'overweight')),
            ('obese', p(key, 'obesity'))]
    tot = sum(v for _, v in vals); x = SX0
    for k, v in vals:
        w = v / tot * (SX1 - SX0)
        x0, x1 = x + (1 if x > SX0 else 0), x + w - (1 if x + w < SX1 - 0.01 else 0)
        rid = f'{key}-{k}'
        st.append(rect('women', x0, y + 7, x1 - x0, BH3, COL[k], rid=rid, tip=f'{lab}: {dict(LEG)[k].lower()} {v:.1f}%'))
        lab_v = f'{v:.1f}%'
        if len(lab_v) * 12 * 0.6 + 8 <= x1 - x0:                  # label only where it fits with padding
            st.append(text('women', (x0 + x1) / 2, y + 7 + 15.5, lab_v, 12, weight=600, fill=INK_ON[k], inside=rid))
        x += w
foot3 = TOP3 + len(GROUPS) * PITCH3 + 4
st.append(text('women', W3 / 2, foot3, 'CDC NHANES 2021–2023; our calculation', 12, fill='#4b5563'))
H3V = foot3 + 10
svg_women = (f'<svg viewBox="0 0 {W3} {H3V}" width="{W3}" height="{H3V}" role="img" aria-labelledby="fig-women-t fig-women-d" font-family="inherit">'
             '<title id="fig-women-t">US women by BMI category, all ages and by age group, 2021 to 2023</title>'
             '<desc id="fig-women-d">Stacked bars that add to 100%. '
             + '; '.join(f'{lab.lower()}: underweight {p(k, "underweight")}%, healthy weight {p(k, "healthy")}%, '
                         f'overweight {p(k, "overweight")}%, obesity {p(k, "obesity")}%' for k, lab in GROUPS)
             + '. Our calculation from CDC NHANES measurements, August 2021 to August 2023.</desc>'
             + ''.join(st) + '</svg>')

# Supporting figure (the wedge made visible): waist size at the same BMI category, two panels, bars in category colours.
VBW['waist'] = W2 = 320
LX, BX0, BXW = 10, 108, 160
wst = [text('waist', W2 / 2, 17, 'Same BMI category, different waist', 14, weight=700),
       text('waist', W2 / 2, 35, 'US women 20 and over, 2021–2023 (%)', 12, fill='#4b5563')]
PANELS = [('Waist 88 cm (34.6 in) or more', WAIST88), ('Waist at least half of height', WHTR)]
y = 62
for title, vals in PANELS:
    wst.append(text('waist', LX, y, title, 12, anchor='start', weight=700, fill='#1f2937'))
    y += 10
    wst.append(f'<line x1="{BX0}" y1="{y}" x2="{BX0}" y2="{y + 3 * 22 - 4}" stroke="#d1d5db" stroke-width="1"/>')   # this panel's baseline
    for k, c, lab in (('healthy', 'healthy', 'Healthy weight'), ('over', 'overweight', 'Overweight'), ('obese', 'obesity', 'Obesity')):
        v = vals[c]; w = v / 100 * BXW
        wst.append(text('waist', LX, y + 12, lab, 12, anchor='start', fill='#1f2937'))
        wst.append(bar('waist', BX0, y + 1, w, 14, COL[k], rid='bar', tip=f'{title}, {lab.lower()}: {v:.1f}%'))
        wst.append(text('waist', BX0 + w + 5, y + 12.5, f'{v:.1f}%', 12, anchor='start', weight=600, fill='#111827'))
        y += 22
    y += 18
wst.append(text('waist', W2 / 2, y - 4, 'CDC NHANES 2021–2023; our calculation', 12, fill='#4b5563'))
H2V = y + 4
svg_waist = (f'<svg viewBox="0 0 {W2} {H2V}" width="{W2}" height="{H2V}" role="img" aria-labelledby="fig-waist-t fig-waist-d" font-family="inherit">'
             '<title id="fig-waist-t">Waist size of US women at each BMI category, 2021 to 2023</title>'
             '<desc id="fig-waist-d">Two panels of bars. Waist of 88 centimeters (34.6 inches) or more: '
             f'healthy weight {WAIST88["healthy"]}%, overweight {WAIST88["overweight"]}%, obesity {WAIST88["obesity"]}%. '
             f'Waist at least half of height: healthy weight {WHTR["healthy"]}%, overweight {WHTR["overweight"]}%, obesity '
             f'{WHTR["obesity"]}%. Our calculation from CDC NHANES measurements, August 2021 to August 2023.</desc>'
             + ''.join(wst) + '</svg>')

# Collision check on the estimated boxes (the rendered check runs in bcw_test_playwright.py): no text over text, no text
# over a shape unless it is the label that shape holds, nothing outside the viewBox.
def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r) and a[6] != r[5]:
            raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r} / {r[5]!r}')
    if a[6]:
        holder = [r for r in RECTS if r[0] == a[0] and r[5] == a[6]][0]
        assert holder[1] + 2 <= a[1] and a[3] <= holder[3] - 2, f'label does not fit its band: {a[5]!r}'
for svg, x0, y0, x1, y1, s, _ in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in the owner's US/English pastes of 2026-10-15 (not personalised): "bmi chart female", "bmi for women",
# "healthy weight 5'4 female". The 5'4" weight question was on all three pages (asked three ways) and the 2026 chart on two;
# the rest in page order. The last two cover ledger keywords this page owns: "average weight 5 2 woman" (14,800/mo) and
# "5 3 ideal weight woman" (8,100/mo).
B64, B62, B63 = hb(64), hb(62), hb(63)
FAQ = [
    ('How much should a 5\'4" female weigh?',
     f'At 5′4″ (162.6 cm), a healthy weight is <strong>{B64[0][0]} to {B64[0][1]} lb ({B64[1][0]} to {B64[1][1]} kg)</strong>, a '
     f'BMI of 18.5 to 24.9 ({ext(U["cdc_cat"], "CDC")}). Under {B64[0][0]} lb is underweight, {hb(64, 2)[0][0]} to '
     f'{hb(64, 2)[0][1]} lb is overweight and {hb(64, 3)[0][0]} lb or more is obesity. The average US woman of that height '
     f'weighs {AVG64} lb (our calculation from CDC measurements, 2021–2023; <a href="/average-weight/">average weight by '
     'height</a>).'),
    ('What is the new BMI chart for 2026?',
     'There isn’t a new chart. CDC’s adult categories are unchanged: a healthy weight is a BMI of 18.5 to 24.9, and the '
     f'page was last reviewed in March 2024 ({ext(U["cdc_cat"], "CDC")}). What changed in June 2026 is the American '
     'Diabetes Association’s definition of obesity: its new standards add the waist, so a woman of non-Asian background '
     'with a BMI of 25 or more meets it if her waist is 88 cm (about 35 in) or more, or at least half her height '
     f'({ADA_CITE}). By the ADA thresholds, including its lower ones for women of Asian background, {ADA_OB}% of US women '
     f'have obesity, against {ADA_BMI}% of the same women by BMI alone (our calculation).'),
    ('What is a healthy BMI for a female?',
     '<strong>18.5 to 24.9</strong>, the same as for men: CDC bases adult categories on BMI “regardless of age, sex, or '
     f'race” ({ext(U["cdc_cat"], "CDC")}). At a healthy BMI, though, the median US woman aged 20 to 59 had '
     f'{BFW["18.5–24.9"]}% body fat and the median man {BF_M}% (our analysis of CDC body scans, 2011–2018). '
     f'{p("all_ages", "healthy")}% of US women have a BMI in the range (our calculation, 2021–2023).'),
    ('Is a 23 BMI chubby?',
     f'Not by CDC’s categories. A BMI of 23 sits inside CDC’s healthy range of 18.5 to 24.9; at 5′4″ it is about {LB23} lb '
     f'({KG23} kg). About {H23W}% of US women have a higher BMI (our calculation from CDC measurements, 2021–2023). For women '
     'of Asian background, 23 is where the 2026 American Diabetes Association standards start counting the waist: a BMI of '
     f'23 or more with a waist of 80 cm (31.5 in) or more, or at least half the height, counts as obesity ({ADA_CITE}).'),
    ('What is the correct BMI for my age as a female?',
     f'The same at every adult age: 18.5 to 24.9 for women 20 and older ({ext(U["cdc_cat"], "CDC")}). Under 20, BMI is '
     'read as a percentile for age and sex instead (<a href="/kids-bmi-calculator/">BMI calculator for children and '
     f'teens</a>). Among US women, {p("20-39", "healthy")}% of those aged 20 to 39 have a BMI in the range, '
     f'{p("40-59", "healthy")}% at 40 to 59 and {p("60+", "healthy")}% at 60 and over (our calculation, 2021–2023).'),
    ('What is an acceptable BMI for a 70 year old female?',
     'CDC’s healthy range, 18.5 to 24.9, applies at 70 too. In a meta-analysis of 197,940 people aged 65 and over, compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began '
     f'to rise at about 33 ({ext(U["winter"], "Winter et al., 2014")}). That is an association, not a separate range. The '
     'American Diabetes Association also notes that “loss of muscle mass in older adults reduces the accuracy of BMI, which '
     f'may lead to underdiagnosis of obesity” ({ADA_CITE}).'),
    ('Is 140 pounds fat for a 5\'4" female?',
     f'Not by CDC’s categories. At 5′4″, 140 lb ({kg_of(140)} kg) is a BMI of {bmi_lb(140, 64)}, inside the healthy range for '
     f'that height, {B64[0][0]} to {B64[0][1]} lb; overweight starts at {hb(64, 2)[0][0]} lb. For women of Asian background, the '
     '2026 American Diabetes Association standards count a BMI of 23 or more as obesity when the waist is 80 cm (31.5 in) '
     f'or more, or at least half the height ({ADA_CITE}).'),
    ('Is 5\'4" 125 pounds skinny?',
     f'No. At 5′4″, 125 lb ({kg_of(125)} kg) is a BMI of {bmi_lb(125, 64)}, in the middle of the healthy range '
     f'({B64[0][0]} to {B64[0][1]} lb). Underweight starts below {B64[0][0]} lb, a BMI under 18.5 '
     f'({ext(U["cdc_cat"], "CDC")}).'),
    ('What is considered morbidly obese for a 5\'4" female?',
     f'CDC’s term is class 3 or severe obesity: a BMI of 40 or more ({ext(U["cdc_cat"], "CDC")}). At 5′4″ that is '
     f'<strong>{hb(64, 5)[0][0]} lb ({hb(64, 5)[1][0]} kg) or more</strong>. {p("all_ages", "class_3")}% of US women have a '
     f'BMI of 40 or more (our calculation; NCHS publishes the same rate in {ext(U["db508"], "Data Brief 508")}).'),
    ('What is the average weight for a 5\'2" woman?',
     f'The average US woman who is 5′2″ weighs <strong>{AVG62} lb ({AVG62_KG} kg)</strong>, measured in CDC’s 2021–2023 '
     f'survey (our calculation, {AVG62_N} women). That is above the healthy range at that height, {B62[0][0]} to '
     f'{B62[0][1]} lb ({B62[1][0]} to {B62[1][1]} kg). <a href="/average-weight/">Average weight by height</a> has every '
     'height.'),
    ('What is the ideal weight for a 5\'3" woman?',
     f'There is no official ideal weight. At 5′3″ (160.0 cm), CDC’s healthy BMI range of 18.5 to 24.9 works out to '
     f'<strong>{B63[0][0]} to {B63[0][1]} lb ({B63[1][0]} to {B63[1][1]} kg)</strong>. Published “ideal weight” formulas give one '
     'weight per height instead; the <a href="/ideal-weight/">ideal weight calculator</a> shows four of them.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
def cat_cell(cls, name): return f'<span class="cat-dot {cls}" aria-hidden="true"></span>{name}'

head = (
    '<div class="page-head"><h1>BMI Chart for Women: Healthy Weight by Height</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">How much should a 5′4″ woman weigh? Is 140 pounds too much at that height? And is there a new '
    'BMI chart for 2026?</p>'
    f'<p class="intro-text">Only {p("all_ages", "healthy")}% of US women have a BMI in CDC’s healthy range of 18.5 to 24.9 '
    '(our calculation from CDC measurements, 2021–2023). Since June 2026, the American Diabetes Association also counts '
    f'waist size, and its thresholds put {ADA_OB}% of US women in the obesity range, compared with about 4 in 10 by BMI '
    'alone (our calculation).</p>'
    '<p class="intro-text">Below: <a href="#chart">the chart for every height</a> from 4′10″ to 6′0″ in pounds and kilograms, where US women '
    'fall on it by age, and what the 2026 waist rules add.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>A healthy BMI for women is 18.5 to 24.9</strong>, the same range as for men (CDC). Under '
    f'18.5 is underweight, 25 to 29.9 overweight and 30 or more obesity. At 5′4″, the healthy weight is {B64[0][0]} to '
    f'{B64[0][1]} lb ({B64[1][0]} to {B64[1][1]} kg); at 5′6″, {hb(66)[0][0]} to {hb(66)[0][1]} lb ({hb(66)[1][0]} to '
    f'{hb(66)[1][1]} kg).</p><ul>'
    f'<li><strong>{p("all_ages", "healthy")}% of US women have a healthy BMI</strong> and {p("all_ages", "obesity")}% have '
    'obesity (our calculation from CDC measurements, 2021–2023; NCHS publishes the same obesity rate).</li>'
    f'<li><strong>Half of US women with a healthy BMI ({WHTR["healthy"]}%) have a waist at least half their height.</strong> '
    'Since June 2026, the American Diabetes Association counts a waist that size toward obesity from a BMI of 25, or 23 for '
    'women of Asian background.</li>'
    '<li>The chart doesn’t apply in pregnancy: CDC’s weight-gain advice depends on BMI before pregnancy.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This guide is for information only. BMI is a '
    'screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>Each bar is one height, split where the weight in pounds '
            'crosses a CDC category line. The healthy band moves right as height rises.</figcaption></figure>')

toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in (
           ('chart', 'Chart'), ('reading', 'Reading it'), ('other-charts', 'Other charts'), ('us-women', 'US women'),
           ('waist', 'Waist'), ('age', 'Age'), ('pregnancy', 'Pregnancy'), ('faq', 'FAQ'), ('sources', 'Sources')))
       + '</nav>')

# The chart table: every inch 4'10"-6'0", six categories, pounds with kilograms below, each unit worked out on its own.
def cell(lbr, kgr):
    (l0, l1), (k0, k1) = lbr, kgr
    if l0 is None: return f'&le; {l1} lb <span class="cell-kg">({k1} kg)</span>'
    if l1 is None: return f'&ge; {l0} lb <span class="cell-kg">({k0} kg)</span>'
    return f'{l0}&ndash;{l1} lb <span class="cell-kg">({k0}&ndash;{k1} kg)</span>'
chart_rows = ''.join(
    f'<tr id="h-{h // 12}-{h % 12}"><th scope="row">{h // 12}′{h % 12}″ <span class="cell-cm">({cm:.1f} cm)</span></th>'
    + ''.join(f'<td class="c-{k}">{cell(*cells[b])}</td>' for b, (k, _, _) in enumerate(CATS6)) + '</tr>'
    for h, cm, cells in CHART)
CHART_IMG = '/assets/images/charts/bmi-chart-women.png'
CHART_W, CHART_H = 1360, 1492                                    # written by chart_bcw.py
_png = os.path.join(ROOT, CHART_IMG.lstrip('/'))
if os.path.exists(_png):
    from PIL import Image
    assert Image.open(_png).size == (CHART_W, CHART_H), Image.open(_png).size
sec_chart = (
    '<section id="chart" class="content-section flow"><h2>BMI chart for women by height and weight</h2>'
    '<p>Each cell is the range of whole pounds, with kilograms below, that gives a BMI in that category at that height.'
    f' The healthy weight runs from <strong>{hb(58)[0][0]} to {hb(58)[0][1]} lb at 4′10″</strong> '
    f'to <strong>{hb(72)[0][0]} to {hb(72)[0][1]} lb at 6′0″</strong>.</p>'
    '<div class="table-responsive"><table class="weight-chart"><caption>BMI chart for women, 4′10″ to 6′0″</caption><thead><tr><th scope="col">Height</th>'
    + ''.join(f'<th scope="col">{name}<span class="th-sub">BMI <span class="nw">{rng}</span></span></th>' for _, name, rng in CATS6)
    + f'</tr></thead><tbody>{chart_rows}</tbody></table></div>'
    '<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, falls in each category at the '
    'height shown. Each unit is worked out on its own, so the kilograms are not conversions of the pounds. Cut-offs: '
    f'{ext(U["cdc_cat"], "CDC Adult BMI Categories")}. Kilogram limits are for the exact height in inches; the centimeters '
    'shown are rounded to one decimal. Each row has its own link, for example #h-5-4 for 5′4″.</p>'
    f'<figure class="figure figure--wide"><a href="{CHART_IMG}"><img src="{CHART_IMG}" width="{CHART_W}" height="{CHART_H}" '
    'loading="lazy" decoding="async" alt="Printable BMI chart for women: BMI at each height from 4 feet 10 inches to 6 feet '
    'and each weight from 90 to 250 pounds, every cell colored by CDC category"></a><figcaption>Printable BMI chart for '
    'women: the BMI at each height and weight from 90 to 250 lb, in 10 lb steps. Open the image to print or save it.'
    '</figcaption></figure>'
    '</section>')

sec_read = (
    '<section id="reading" class="content-section flow"><h2>How to read the chart</h2><ol>'
    '<li>Find your height in the left column. Centimeters are under each height.</li>'
    '<li>Read across to the cell that holds your weight. Its column is your BMI category.</li>'
    '<li>For the exact number, use the <a href="/women-bmi-calculator/">BMI calculator for women</a>, or find your height and '
    'weight on the printable chart.</li></ol>'
    f'<p><strong>Example.</strong> Say you’re 5′5″ and weigh {EX_LB} lb ({kg_of(EX_LB)} kg). The overweight cell in that row runs '
    f'from {hb(65, 2)[0][0]} to {hb(65, 2)[0][1]} lb, so {EX_LB} lb is overweight: a BMI of {EX_BMI} ({EX_LB} × 703 ÷ 65², '
    f'rounded to one decimal; {ext(U["cdc_formula"], "CDC formula")}). The healthy range at 5′5″ is {hb(65)[0][0]} to '
    f'{hb(65)[0][1]} lb, so {EX_LB} lb is {EX_OVER} lb above it.</p>'
    '</section>')

sec_other = (
    '<section id="other-charts" class="content-section flow"><h2>Why other charts give different numbers</h2>'
    f'<p>NIH’s printable BMI table has one column for each whole BMI from {NIH_COLS[0]} to {NIH_COLS[1]} '
    f'({ext(U["nih_tbl"], "NIH")}). At 5′4″ its BMI 19 column reads {NIH_64[0]} lb and its BMI 24 column {NIH_64[1]} lb, '
    f'so a chart read from it gives <strong>{NIH_64[0]} to {NIH_64[1]} lb</strong> for that height. CDC’s healthy range runs '
    f'from 18.5 to 24.9, and on this chart that is <strong>{B64[0][0]} to {B64[0][1]} lb</strong>.</p>'
    '<p>Other differences come from rounding and from “ideal weight” formulas. We round BMI to one decimal, the way CDC’s '
    'survey records it, and list only whole pounds whose rounded BMI falls in the range. Ideal-weight formulas give one '
    'weight per height instead of a range; the <a href="/ideal-weight/">ideal weight calculator</a> shows four of them.</p>'
    '</section>')

cat_cols = (('underweight', 'Under 18.5'), ('healthy', '18.5–24.9'), ('overweight', '25–29.9'), ('obesity', '30 or more'),
            ('class_3', '40 or more'))
women_rows = ''.join(
    f'<tr><th scope="row">{lab}</th>' + ''.join(f'<td class="num">{p(k, c)}%</td>' for c, _ in cat_cols)
    + f'<td class="num">{C[k]["n"]:,}</td></tr>'
    for k, lab in (('20-39', '20 to 39'), ('40-59', '40 to 59'), ('60+', '60 and over'), ('all_ages', 'All, 20 and over')))
sec_us = (
    '<section id="us-women" class="content-section flow"><h2>Where US women fall on the chart</h2>'
    f'<div class="stat-callout"><div class="stat-callout-value">{p("all_ages", "healthy")}%</div><div class="stat-callout-text">'
    'of US women aged 20 and over have a BMI of 18.5 to 24.9, August 2021–August 2023.</div><div class="stat-callout-source">'
    f'Source: our calculation from {ext(U["bmx"], "CDC NHANES 2021–2023")} measurements ({C["all_ages"]["n"]:,} women; 95% '
    f'confidence interval {CI_W[0]}% to {CI_W[1]}%)</div></div>'
    f'<p>Most US women are above the healthy range: {p("all_ages", "overweight")}% are overweight and '
    f'<strong>{p("all_ages", "obesity")}% have obesity</strong>, including {p("all_ages", "class_3")}% with a BMI of 40 or more. '
    f'The median US woman has a BMI of {MED_W}, in the overweight band (our calculation).</p>'
    f'<figure class="figure">{svg_women}<figcaption>Share of US women in each BMI category. Obesity combines classes 1 to 3; '
    'the table has class 3 on its own.</figcaption></figure>'
    f'<p><strong>Women aged 20 to 39 are the most likely to have a healthy BMI</strong>, at {p("20-39", "healthy")}%. Obesity '
    f'peaks at 40 to 59 ({p("40-59", "obesity")}%), and class 3 obesity is least common at 60 and over '
    f'({p("60+", "class_3")}%, against {p("20-39", "class_3")}% at 20 to 39 and {p("40-59", "class_3")}% at 40 to 59).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>US women by BMI category and age (%)</caption>'
    '<thead><tr><th scope="col">Age</th>'
    + ''.join(f'<th scope="col" class="num">{h}</th>' for _, h in cat_cols)
    + f'<th scope="col" class="num">Women measured</th></tr></thead><tbody>{women_rows}</tbody></table></div>'
    f'<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023 measured heights and weights '
    f'({C["all_ages"]["n"]:,} women aged 20 and over; survey-weighted; pregnant women excluded). The obesity and BMI 40 or more '
    f'shares match NCHS’s published rates for women at every age ({ext(U["db508"], "Data Brief 508")}). Each share has a 95% '
    f'margin of error of up to ±{HALF_HI} points, and each difference by age stated above is larger than its own margin of error.</p>'
    '<p>For what US women weigh at each height, see <a href="/average-weight/">average weight by height</a>; '
    '<a href="/us-obesity-statistics/">US obesity statistics</a> has the trends since 1960.</p>'
    '</section>')

sec_waist = (
    '<section id="waist" class="content-section flow"><h2>Waist size at the same BMI</h2>'
    '<p>BMI can’t show where fat sits. US guidelines treat a waist over 35 inches (88 cm) in women as a marker of higher risk, mainly at a BMI of 25 to 34.9 '
    f'({ext(U["nhlbi_tg"], "NHLBI")}). For adults with a BMI under 35, NICE (UK) classes a waist-to-height ratio of 0.5 '
    f'to 0.59 as increased central adiposity and 0.6 or more as high ({ext(U["nice"], "NICE")}).</p>'
    f'<figure class="figure">{svg_waist}<figcaption>Share of US women with a large waist, by BMI category. Women with a '
    f'measured waist ({N_WAIST:,}).</figcaption></figure>'
    f'<p>Among US women with a healthy BMI, <strong>{WAIST88["healthy"]}% have a waist of 88 cm (34.6 in) or more, and '
    f'{WHTR["healthy"]}% have a waist at least half their height</strong>. At an overweight BMI the shares are '
    f'{WAIST88["overweight"]}% and {WHTR["overweight"]}%; with obesity, nearly all.</p>'
    f'<p>In June 2026 the American Diabetes Association put the waist into the diagnosis ({ext(U["ada_pr"], "ADA")}). For '
    'adults of non-Asian background, obesity is a BMI of 30 or more, or a BMI of 25 or more with a waist-to-height ratio of '
    '0.5 or more or a waist of 88 cm (about 35 in) or more in women. For adults of Asian background the lines are a BMI of 27.5, or '
    f'23 with the same ratio or a waist of 80 cm (31.5 in) in women ({ADA_CITE}). For comparison, CDC’s National Diabetes '
    f'Prevention Program uses a BMI of 23 or higher, instead of 25, as one of its eligibility criteria for Asian American '
    f'adults ({ext(U["ndpp"], "CDC")}).</p>'
    f'<div class="stat-callout"><div class="stat-callout-value">{ADA_OB}%</div><div class="stat-callout-text">of US women meet '
    f'the 2026 ADA obesity thresholds, against {ADA_BMI}% by BMI alone, in the same {ADA_N:,} women.</div>'
    '<div class="stat-callout-source">Source: our calculation from CDC NHANES 2021–2023 measured BMI, waist and height; 95% '
    f'confidence interval {ADA["obesity_ada"]["ci95"][0]}% to {ADA["obesity_ada"]["ci95"][1]}%</div></div>'
    f'<p>Most of the gap, {ADA_FROM_25} points, comes from non-Asian women with a BMI of 25 to 29.9: '
    f'{ADA_CENTRAL}% of them have a waist at or above the line. In CDC’s body scans of women aged 20 to 59, '
    f'the median woman had {BFW["18.5–24.9"]}% body fat at a BMI of 18.5 to 24.9, {BFW["25–29.9"]}% at 25 to 29.9 and '
    f'{BFW["30+"]}% at 30 or more; the median man at a healthy BMI had {BF_M}% (our analysis of NHANES 2011–2018).</p>'
    '<p>The <a href="/blog/waist-to-height-ratio/">waist-to-height ratio guide</a> shows how to measure it, and the '
    '<a href="/body-fat-calculator/">body fat calculator</a> estimates body fat from a tape measure.</p>'
    '</section>')

sec_age = (
    '<section id="age" class="content-section flow"><h2>Does the chart change with age?</h2>'
    '<p><strong>Not for adults.</strong> CDC uses one set of categories for every woman aged 20 and over, “regardless of '
    f'age, sex, or race” ({ext(U["cdc_cat"], "CDC")}). The body behind the BMI does change with age:</p><ul>'
    '<li><strong>Body fat.</strong> At the same BMI, body fat depends on age as well as sex '
    f'({ext(U["gallagher"], "Gallagher et al., 2000")}).</li>'
    f'<li><strong>Muscle.</strong> “Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to '
    f'underdiagnosis of obesity” ({ADA_CITE}).</li>'
    '<li><strong>Mortality data.</strong> In never-smokers, per 5 BMI units above 25, the risk of death was '
    f'{GB_35_49}% higher for BMI measured at ages 35 to 49 but {GB_70_89}% higher at 70 to 89, women and men combined '
    f'({ext(U["gbmc"], "Global BMI Mortality Collaboration, 2016")}). In adults 65 and over, compared with a BMI of 23 to '
    '23.9, the risk of death was higher below 23 and began to rise at about 33 '
    f'({ext(U["winter"], "Winter et al., 2014")}). These are associations, not separate ranges.</li></ul>'
    '<p>Under 20, BMI is read as a percentile for age and sex, not on this chart; the '
    '<a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it out for ages 2 to 19. '
    '<a href="/blog/bmi-by-age/">BMI by age</a> explains how the adult range applies across life, and the '
    '<a href="/blog/healthy-bmi-range/">healthy BMI range</a> guide has the mortality data behind it.</p>'
    '</section>')

preg_rows = ''.join(
    f'<tr><th scope="row">{rng}<span class="unit-alt">{name}</span></th><td class="nowrap">{lo}–{hi} lb'
    f'<span class="unit-alt">({kg_of(lo)}–{kg_of(hi)} kg)</span></td></tr>' for rng, name, lo, hi in PREG)
sec_preg = (
    '<section id="pregnancy" class="content-section flow"><h2>BMI charts and pregnancy</h2>'
    '<p>Adult BMI categories are for people who aren’t pregnant: the 2026 ADA standards cover nonpregnant adults '
    f'({ADA_CITE}), and NCHS leaves pregnant women out of its adult BMI statistics, as this page does. During pregnancy, CDC’s advice on weight gain depends on your BMI before pregnancy, using '
    f'recommendations from the Institute of Medicine ({ext(U["preg"], "CDC")}):</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Recommended weight gain in pregnancy with one baby, by '
    'BMI before pregnancy</caption><thead><tr><th scope="col">BMI before pregnancy</th><th scope="col">Total gain</th></tr>'
    f'</thead><tbody>{preg_rows}</tbody></table></div>'
    f'<p class="source-note">Source: {ext(U["preg"], "CDC, Weight Gain During Pregnancy")}, which writes the last row as BMI '
    '30.0–39.9 and also gives ranges for twins. Kilograms are our conversions of CDC’s pounds.</p>'
    '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the adult cut-offs and the “regardless of age, sex, or race” rule '
    '(page last reviewed March 2024).',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formulas in US units and metric.',
    f'NIH (NHLBI). {ext(U["nih_tbl"], "Body Mass Index Table")} (NIH Publication No. 22-HL-8190, September 2022): one '
    f'column for each whole BMI from {NIH_COLS[0]} to {NIH_COLS[1]}.',
    f'CDC {ext(U["bmx"], "NHANES August 2021–August 2023")} demographics and body measures files (DEMO_L, BMX_L): our '
    'calculation of the share of '
    f'women aged 20 and over in each BMI category by age ({C["all_ages"]["n"]:,} women), of waist size by BMI category '
    f'({N_WAIST:,} with a measured waist) and of the 2026 ADA thresholds ({ADA_N:,} women), weighted with the exam weights, '
    'pregnant women excluded; the same files give the average weight at each height on '
    '<a href="/average-weight/">average weight by height</a>.',
    f'Emmerich SD, et al. {ext(U["db508"], "NCHS Data Brief No. 508")} (Sep 2024): obesity and severe obesity in US adults '
    'by sex and age, August 2021–August 2023.',
    f'NHLBI. {ext(U["nhlbi_tg"], "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")}, '
    'treatment guidelines chapter (NIH, 1998): waist cut-offs for women and men.',
    f'NICE (UK). {ext(U["nice"], "Overweight and obesity management, guideline NG246")} (2025): waist-to-height ratio '
    'categories for adults with a BMI under 35, a 2022 recommendation.',
    'American Diabetes Association Professional Practice Committee for Obesity. '
    f'{ext(U["ada"], "Screening, Diagnosis, Evaluation, and Staging of Obesity in Adults: Standards of Care in Overweight and Obesity—2026")}: '
    f'obesity thresholds with waist size (recommendations 3.3a and 3.3b); {ext(U["ada_pr"], "ADA press release")}, June 2026.',
    f'CDC. {ext(U["ndpp"], "National Diabetes Prevention Program eligibility")}: BMI of 25 or higher, 23 or higher for Asian '
    'American adults.',
    'CDC NHANES 2011–2018 DXA body scans: our analysis of body fat by BMI band, women and men aged 20 to 59 '
    '(<a href="/body-fat-percentage-chart/">body fat percentage chart</a>).',
    f'Gallagher D, et al. {ext(U["gallagher"], "American Journal of Clinical Nutrition, 2000")}: body fat predicted from BMI, '
    'sex, age and ethnic group.',
    f'The Global BMI Mortality Collaboration. {ext(U["gbmc"], "Body-mass index and all-cause mortality")} (Lancet, 2016): '
    'hazard ratios per 5 BMI units by age at measurement, never-smokers.',
    f'Winter JE, et al. {ext(U["winter"], "American Journal of Clinical Nutrition, 2014")}: BMI and mortality in adults 65 '
    'and over.',
    f'CDC. {ext(U["preg"], "Weight Gain During Pregnancy")}: recommended gain by BMI before pregnancy, from the Institute of '
    'Medicine.',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Chart: the lightest and heaviest whole pounds (or kilograms) whose BMI, '
    'rounded to one decimal, falls in each CDC category at each height, each unit worked out on its own; BMI = lb × 703 ÷ '
    'in², or kg ÷ m². US women: CDC NHANES August 2021–August 2023, women aged 20 and over with a measured height and '
    'weight, pregnant women excluded, weighted with the exam weights; BMI, waist and height as CDC records them; 95% '
    'confidence intervals by Taylor linearization over the survey’s strata and primary sampling units, and the page states '
    'only differences whose interval excludes zero. The 2026 ADA thresholds are applied to the measured BMI, waist and '
    'height; women identified in the survey as non-Hispanic Asian get the Asian thresholds; women whose class depends on a '
    f'waist that was not measured ({ADA["n_left_out"]}) are left out of that comparison, and the BMI-only share is computed '
    'on the same women.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/women-bmi-calculator/', 'BMI calculator for women'), ('/', 'BMI calculator'),
        ('/age-bmi-calculator/', 'BMI calculator by age'), ('/body-fat-calculator/', 'Body fat calculator'),
        ('/ideal-weight/', 'Ideal weight calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/bmi-chart/', 'BMI chart'), ('/blog/bmi-chart-men/', 'BMI chart for men'),
        ('/blog/healthy-bmi-range/', 'Healthy BMI range'), ('/average-weight/', 'Average weight by height'),
        ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'), ('/body-fat-percentage-chart/', 'Body fat percentage chart'),
        ('/blog/bmi-by-age/', 'BMI by age'), ('/us-obesity-statistics/', 'US obesity statistics')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> <article> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_chart, sec_read, sec_other, sec_us, sec_waist, sec_age, sec_preg, sec_faq, sec_src,
     sec_rel]) + ' </article> </div></main>')
assert 'placeholder' not in main and 'style="' not in re.sub(r'(?s)<svg.*?</svg>', '', main)

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'BMI Chart for Women: Healthy Weight by Height (lb and kg)'
H1 = 'BMI Chart for Women: Healthy Weight by Height'
DESC = ('The BMI chart for women from 4′10″ to 6′0″: healthy, overweight and obesity weights at every height in lb and kg, '
        'and where US women fall by age.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'BMI chart for women: healthy weight at every height'
OG_D = ('The chart from 4′10″ to 6′0″ in lb and kg, US women by BMI category and age (CDC data, our calculation), and the '
        '2026 waist rules.')
OG_IMG = 'https://calculatemybmi.net/assets/images/og/bmi-chart-women.png'
CHART_ABS = 'https://calculatemybmi.net' + CHART_IMG

def sub1(pattern, repl, s):
    # the old descriptions hold an unescaped " (4'10" to 6'0"), so they are matched up to the first ">
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content=".*?">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG_IMG}">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG_IMG}">', src)
# The old chart's page-level <style> (.bmi-chart cells and print rules) gives way to .weight-chart in styles.css.
assert src.count('<style>') == 1 and '.bmi-chart' in re.search(r'(?s)<style>.*?</style>', src).group(0)
src = re.sub(r'(?s)<style>.*?</style>', '', src, count=1)

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
types = [json.loads(b.group(1))['@type'] for b in blocks]
assert types == ['Article', 'BreadcrumbList'], types
art = json.loads(blocks[0].group(1))
art.update({'headline': H1, 'image': [OG_IMG, CHART_ABS], 'description': DESC, 'dateModified': '{TODAY}'})
assert art['datePublished'] == '2026-01-28'
crumbs = json.loads(blocks[1].group(1))
assert crumbs['itemListElement'][2]['item'] == 'https://calculatemybmi.net/blog/bmi-chart-women/'
crumbs['itemListElement'][2]['name'] = H1
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
end_crumbs = blocks[1].end(0)
src = (src[:end_crumbs] + '<script type="application/ld+json"> ' + json.dumps(faq_ld, ensure_ascii=False) + ' </script>'
       + src[end_crumbs:])
for b, new in ((blocks[1], crumbs), (blocks[0], art)):            # back to front, so offsets stay valid
    src = src[:b.start(1)] + ' ' + json.dumps(new, ensure_ascii=False) + ' ' + src[b.end(1):]

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('{TODAY}') == 1

open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'blog/bmi-chart-women/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, '
      f'{len(FAQ)} FAQ, {len(TEXTS)} SVG labels checked')
