#!/usr/bin/env python3
"""CMB-013 HEALTHY-RANGE — rebuilds /blog/healthy-bmi-range/ to the D-14 pattern (the CMB-006 men page, as the
homepage applied it in CMB-012): intro, answer block and key takeaways, a hero figure, contents chips, real tables
and charts, a flat FAQ whose JSON-LD equals the visible answers, sources and method, one related block, one 680 px
reading column.

Wedge: the share of US adults with a BMI in the healthy range, by age and sex (CDC NHANES August 2021-August 2023,
5,929 adults; our calculation in healthy_stats.py, which reproduces NCHS's published prevalences), next to the
mortality evidence the range rests on (Global BMI Mortality Collaboration, Lancet 2016).

Every number on the page comes from healthy_stats.json, research/home-build/home_stats.json,
research/body-fat/bf_results.json, the calculator's weight-limit rule (mirrored below and asserted against
scripts/check_weight_tables.py), or a source verified in chat on 2026-10-15 (constants below, each with its source;
all listed in "Sources and method").

usage: python3 gen_hbr.py REPO_ROOT STATS_JSON
Runs once, on blog/healthy-bmi-range/index.html as it stood at 192fb02; kept as the build record. The page is written
with {TODAY} in its two date fields (schema dateModified, article:modified_time); apply_build.py puts in the apply
date (manifest "today": true), the same clock git commits with, so research/dates/date_truth.py agrees.
"""
import sys, os, re, json, math, html

ROOT, STATS = sys.argv[1], sys.argv[2]
G = json.load(open(STATS))['groups']
HOME = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
BF = json.load(open(os.path.join(ROOT, 'research/body-fat/bf_results.json')))
PAGE = os.path.join(ROOT, 'blog/healthy-bmi-range/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds          # the CMB-008 gate's own rule

# ---------------------------------------------------------------- numbers: US adults (our calculation)
A, M, W = G['all'], G['men'], G['women']
assert (A['all_ages']['n'], M['all_ages']['n'], W['all_ages']['n']) == (5929, 2680, 3249)
assert (A['all_ages']['healthy'], M['all_ages']['healthy'], W['all_ages']['healthy']) == (26.0, 24.0, 28.1)
assert [A[a]['healthy'] for a in ('20-39', '40-59', '60+')] == [31.0, 22.3, 24.6]
assert [M[a]['healthy'] for a in ('20-39', '40-59', '60+')] == [28.3, 20.7, 22.5]
assert [W[a]['healthy'] for a in ('20-39', '40-59', '60+')] == [33.8, 23.9, 26.5]
assert (A['all_ages']['underweight'], A['all_ages']['overweight'], A['all_ages']['obesity'], A['all_ages']['class_3']) == (1.6, 32.1, 40.3, 9.4)
CS = HOME['category_shares_pct']                                 # the homepage's category table, same files and method
assert CS == {'underweight': 1.6, 'healthy': 26.0, 'overweight': 32.1, 'obesity_class_1': 20.6,
              'obesity_class_2': 10.3, 'obesity_class_3': 9.4}
assert round(CS['obesity_class_1'] + CS['obesity_class_2'] + CS['obesity_class_3'], 1) == A['all_ages']['obesity']
MEDIAN = HOME['adults']['table']['p50']; assert MEDIAN == 28.2
REPRO = json.load(open(STATS))['reproduces_nchs']
assert all(v['ours'] == v['nchs'] for v in REPRO.values())
# Body fat from CDC DXA scans, ages 20-59 (research/body-fat/bf_results.json, the /body-fat-percentage-chart/ data).
# Matched comparison: weighted median body fat of adults 20-59 with a BMI of 18.5-24.9 (by_bmi q = p10, p25, p50, p75, p90).
BF_W, BF_M = BF['f']['by_bmi']['18.5–24.9']['q'][2], BF['m']['by_bmi']['18.5–24.9']['q'][2]
assert (BF_W, BF_M) == (33.4, 22.1)
# Sampling error (healthy_stats.py: Taylor linearisation, 15 design df). The page states only differences whose 95% CI excludes 0.
S_ALL = json.load(open(STATS))
CI26 = A['all_ages']['healthy_ci95']; assert CI26 == [22.8, 29.3]
HALF = [round((g[a]['healthy_ci95'][1] - g[a]['healthy_ci95'][0]) / 2, 1) for g in (A, M, W) for a in ('20-39', '40-59', '60+')]
HALF_LO, HALF_HI = round(min(HALF)), round(max(HALF)); assert (HALF_LO, HALF_HI) == (3, 6), HALF
DIF = S_ALL['healthy_differences']
for k in ('women_minus_men', 'women_20_39_minus_men_20_39', 'women_20_39_minus_women_60_plus'):
    assert DIF[k]['ci95'][0] > 0, k                              # stated on the page
for k in ('men_60_plus_minus_men_40_59', 'women_60_plus_minus_women_40_59'):
    assert DIF[k]['ci95'][0] < 0 < DIF[k]['ci95'][1], k           # not stated: within sampling error
assert max(W[a]['healthy'] for a in ('20-39', '40-59', '60+')) == W['20-39']['healthy'] > max(M[a]['healthy'] for a in ('20-39', '40-59', '60+'))
OTHER = sorted(g[a]['healthy'] for g in (M, W) for a in ('20-39', '40-59', '60+'))[:-1]

# ---------------------------------------------------------------- numbers: the calculator's weight limits
def bounds(h_in, lo, hi):
    """Mirrors weightBounds() in assets/js/calculator.js: pounds via 703, kilograms via kg/m2 (CMB-011)."""
    k = h_in * h_in / 703; m2 = (h_in * 0.0254) ** 2
    out = {}
    if lo is not None:
        out['minLb'] = math.ceil((lo - 0.05) * k - 1e-9); out['minKg'] = math.ceil((lo - 0.05) * m2 - 1e-9)
    if hi is not None:
        out['maxLb'] = math.ceil((hi + 0.05) * k - 1e-9) - 1; out['maxKg'] = math.ceil((hi + 0.05) * m2 - 1e-9) - 1
    return out

def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10

ROWS = []
for h in range(58, 77, 2):                                       # 4'10" to 6'4", every 2 inches
    cm = h * 2.54
    hb, ob, xb = bounds(h, 18.5, 24.9), bounds(h, 25, 29.9), bounds(h, 30, None)
    assert (hb['minLb'], hb['maxLb']) == gate_bounds('lb', h, cm, 1) and (hb['minKg'], hb['maxKg']) == gate_bounds('kg', h, cm, 1)
    assert (ob['minLb'], ob['maxLb']) == gate_bounds('lb', h, cm, 2) and (ob['minKg'], ob['maxKg']) == gate_bounds('kg', h, cm, 2)
    assert ob['minLb'] == hb['maxLb'] + 1 and ob['minKg'] == hb['maxKg'] + 1 and xb['minLb'] == ob['maxLb'] + 1
    ROWS.append((h // 12, h % 12, round(cm, 1), hb, ob, xb))
assert [(r[3]['minLb'], r[3]['maxLb'], r[3]['minKg'], r[3]['maxKg']) for r in ROWS] == [
    (89, 119, 41, 54), (95, 127, 43, 57), (101, 136, 46, 61), (108, 145, 49, 65), (115, 154, 52, 70),
    (122, 164, 56, 74), (129, 173, 59, 78), (137, 183, 62, 83), (144, 194, 66, 88), (152, 204, 69, 92)]
assert [(r[4]['minLb'], r[4]['maxLb'], r[4]['minKg'], r[4]['maxKg']) for r in ROWS] == [
    (120, 143, 55, 65), (128, 153, 58, 69), (137, 163, 62, 74), (146, 174, 66, 79), (155, 185, 71, 84),
    (165, 196, 75, 89), (174, 208, 79, 94), (184, 220, 84, 100), (195, 233, 89, 105), (205, 246, 93, 111)]
STEP_MIN = sorted({b[3]['minLb'] - a[3]['minLb'] for a, b in zip(ROWS, ROWS[1:])})
STEP_MAX = sorted({b[3]['maxLb'] - a[3]['maxLb'] for a, b in zip(ROWS, ROWS[1:])})
assert (STEP_MIN[0], STEP_MIN[-1], STEP_MAX[0], STEP_MAX[-1]) == (6, 8, 8, 11), (STEP_MIN, STEP_MAX)
B64, B70 = bounds(64, 18.5, 24.9), bounds(70, 18.5, 24.9)
assert (B64['minLb'], B64['maxLb'], B64['minKg'], B64['maxKg']) == (108, 145, 49, 65)
assert (B70['minLb'], B70['maxLb'], B70['minKg'], B70['maxKg']) == (129, 173, 59, 78)
# PAA "What is BMI for 70 kg?": BMI at 160, 170 and 180 cm, and the heights where 70 kg is a healthy weight, in whole cm and
# whole inches, each worked out on its own (kg / m2, m = cm / 100 or in x 0.0254).
KG70 = 70
B70KG = {cm: r1(KG70 / (cm / 100) ** 2) for cm in (160, 170, 180)}
assert B70KG == {160: 27.3, 170: 24.2, 180: 21.6}
H70_CM = [cm for cm in range(140, 221) if 18.5 <= r1(KG70 / (cm / 100) ** 2) <= 24.9]
H70_IN = [i for i in range(55, 88) if 18.5 <= r1(KG70 / (i * 0.0254) ** 2) <= 24.9]
assert H70_CM == list(range(168, 195)) and H70_IN == list(range(66, 77))
LB70 = round(KG70 * 2.20462, 1); assert LB70 == 154.3
# PAA "Is a BMI of 23 chubby?": share of US adults with a higher BMI, read from the 1st-99th percentile curve the homepage
# rank uses (home_stats.json; "higher" counts only strictly higher BMIs, the CMB-012 rule).
QA = HOME['adults']['p1_p99']
def rank(q, b):
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
H23 = round(100 - rank(QA, 23.0)); assert H23 == 84
# PAA "Is a BMI of 25 realistic?": share of US adults at 25 or more (overweight + obesity, crude).
SHARE25 = round(A['all_ages']['overweight'] + A['all_ages']['obesity'], 1); assert SHARE25 == 72.4 == HOME['share_bmi_25_plus_pct']
# Hero rows: 5'0", 5'6", 6'0".
HERO = [(5, 0), (5, 6), (6, 0)]
HB = {fi: bounds(fi[0] * 12 + fi[1], 18.5, 24.9) for fi in HERO}

# ---------------------------------------------------------------- numbers: Global BMI Mortality Collaboration (2016)
# Lancet 2016;388:776-86 (PMC4995441), checked in chat 2026-10-15. Never-smokers without chronic disease at recruitment
# who survived 5 years: hazard ratios for all-cause death (95% CI) against BMI 22.5 to <25.
# Bands as published (15.0 to <18.5, 18.5 to <20.0, ... 40.0 to <60.0), written to one decimal as CDC writes 18.5-24.9.
GBMC = [('15–18.4', 1.51, '1.43–1.59', 'underweight'), ('18.5–19.9', 1.13, '1.09–1.17', 'normal'),
        ('20–22.4', 1.00, '0.98–1.02', 'normal'), ('22.5–24.9', 1.00, '0.99–1.01', 'normal'),
        ('25–27.4', 1.07, '1.07–1.08', 'overweight'), ('27.5–29.9', 1.20, '1.18–1.22', 'overweight'),
        ('30–34.9', 1.45, '1.41–1.48', 'obese'), ('35–39.9', 1.94, '1.87–2.01', 'obese'),
        ('40–59.9', 2.76, '2.60–2.92', 'obese-severe')]
GB = {g[0]: g[1] for g in GBMC}
def pct_higher(hr): return round((hr - 1) * 100)
assert [pct_higher(GB[k]) for k in ('15–18.4', '18.5–19.9', '25–27.4', '27.5–29.9', '30–34.9', '35–39.9')] == [51, 13, 7, 20, 45, 94]
GBMC_N_ALL, GBMC_STUDIES, GBMC_COUNTRIES = 10625411, 239, 32
GBMC_N, GBMC_N_STUDIES, GBMC_DEATHS = 3951455, 189, 385879
# Hazard ratio per 5 kg/m2 higher BMI above 25 (same paper).
PER5 = {'europe': 1.39, 'north_america': 1.29, 'east_asia': 1.39, 'anz': 1.31, 'age_35_49': 1.52, 'age_70_89': 1.21,
        'men': 1.51, 'women': 1.30}
assert [pct_higher(PER5[k]) for k in ('europe', 'east_asia', 'anz', 'north_america', 'men', 'women', 'age_35_49', 'age_70_89')] \
    == [39, 39, 31, 29, 51, 30, 52, 21]

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'who_fs': 'https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'he111': 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm',
    'he119': 'https://www.cdc.gov/nchs/data/hestat/hestat119.htm',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'who2004': 'https://pubmed.ncbi.nlm.nih.gov/14726171/',
    'kotang': 'https://apjcn.qdu.edu.cn/15_2_7.pdf',
    'lancet': 'https://pubmed.ncbi.nlm.nih.gov/39824205/',
    'wing': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'pag': 'https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/top-10-things-know',
    'bwp': 'https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner',
    'mlp': 'https://medlineplus.gov/ency/article/003107.htm',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'nhlbi_calc': 'https://www.nhlbi.nih.gov/calculate-your-bmi',
    'who1995': 'https://www.who.int/publications/i/item/9241208546',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'nhlbi_tg': 'https://www.ncbi.nlm.nih.gov/books/NBK2004/',
    'ndpp': 'https://www.cdc.gov/diabetes-prevention/eligible-lifestyle-change-program/index.html',
}
GBMC_CITE = ext(U['gbmc'], 'Global BMI Mortality Collaboration, 2016')

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS = [], []          # estimated boxes: (svg, x0, y0, x1, y1, label) ; (svg, x0, y0, x1, y1, holds_text)
VBW = {}

def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827', inside=None):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s, inside))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'

def rect(svg, x, y, w, h, fill, rid=None, extra=''):
    RECTS.append((svg, x, y, x + w, y + h, rid))
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>'

STRONG = {'underweight': '#1d4ed8', 'normal': '#15803d', 'overweight': '#b45309', 'obese': '#b91c1c', 'obese-severe': '#991b1b'}
BASE = {'underweight': '#3b82f6', 'normal': '#22c55e', 'overweight': '#f59e0b', 'obese': '#ef4444', 'obese-severe': '#991b1b'}

# Hero: one BMI range, a different weight at each height. Scale BMI 15-40, then the healthy pounds at three heights.
VBW['hero'] = W1 = 320
SX0, SX1 = 10, 310
def sx(b): return SX0 + (b - 15) * (SX1 - SX0) / 25
segs = [('underweight', 15, 18.5, 'Under'), ('normal', 18.5, 25, 'Healthy'), ('overweight', 25, 30, 'Over'),
        ('obese', 30, 40, 'Obesity')]
hero = [text('hero', W1 / 2, 18, 'One BMI range for every adult', 15, weight=700)]
for cat, lo, hi, lab in segs:
    x0, x1 = sx(lo), sx(hi)
    hero.append(rect('hero', x0, 44, x1 - x0, 28, STRONG[cat], rid=lab))
    hero.append(text('hero', (x0 + x1) / 2, 63, lab, 12.5, weight=600, fill='#ffffff', inside=lab))
hero.append(f'<rect x="{sx(18.5) + 1.5:.1f}" y="42.5" width="{sx(25) - sx(18.5) - 3:.1f}" height="31" fill="none" stroke="#111827" stroke-width="3" rx="2"/>')
hero.append(text('hero', (sx(18.5) + sx(25)) / 2, 37, '18.5 to 24.9', 12.5, weight=700, fill='#15803d'))
for b in (18.5, 25, 30):
    hero.append(text('hero', sx(b), 88, f'{b:g}', 12, fill='#374151'))
hero.append(text('hero', 10, 118, 'Healthy weight at three heights', 13, anchor='start', weight=700, fill='#1f2937'))
WX0, WX1, WLO, WHI = 60, 310, 80, 200
def wx(lb): return WX0 + (lb - WLO) * (WX1 - WX0) / (WHI - WLO)
for i, (ft, inch) in enumerate(HERO):
    hb = HB[(ft, inch)]; y = 146 + i * 40
    x0, x1 = wx(hb['minLb']), wx(hb['maxLb'])
    hero.append(text('hero', 10, y + 13, f'{ft}′{inch}″', 13, anchor='start', weight=700, fill='#1f2937'))
    hero.append(rect('hero', x0, y, x1 - x0, 18, BASE['normal'], rid='bar'))
    hero.append(text('hero', (x0 + x1) / 2, y - 5, f'{hb["minLb"]}–{hb["maxLb"]} lb ({hb["minKg"]}–{hb["maxKg"]} kg)', 12, fill='#1f2937'))
axis_y = 146 + 2 * 40 + 18 + 8
hero.append(f'<line x1="{WX0}" y1="{axis_y}" x2="{WX1}" y2="{axis_y}" stroke="#9ca3af" stroke-width="1"/>')
for lb in (80, 120, 160, 200):
    hero.append(f'<line x1="{wx(lb):g}" y1="{axis_y}" x2="{wx(lb):g}" y2="{axis_y + 4}" stroke="#9ca3af" stroke-width="1"/>')
    hero.append(text('hero', wx(lb) if lb < 200 else WX1, axis_y + 17, f'{lb} lb' if lb == 200 else str(lb), 12,
                     anchor='middle' if lb < 200 else 'end', fill='#4b5563'))
H1V = axis_y + 26
svg_hero = (f'<svg viewBox="0 0 {W1} {H1V}" width="{W1}" height="{H1V}" role="img" aria-labelledby="fig-hero-t fig-hero-d" font-family="inherit">'
            '<title id="fig-hero-t">The healthy BMI range is 18.5 to 24.9 for every adult; the healthy weight depends on height</title>'
            '<desc id="fig-hero-d">A BMI scale from 15 to 40 with four bands: underweight under 18.5, healthy weight 18.5 to 24.9 '
            '(outlined), overweight 25 to 29.9 and obesity 30 or more. Below it, the healthy weight at three heights: '
            + ', '.join(f'{ft} feet {inch} inches, {HB[(ft, inch)]["minLb"]} to {HB[(ft, inch)]["maxLb"]} pounds '
                        f'({HB[(ft, inch)]["minKg"]} to {HB[(ft, inch)]["maxKg"]} kilograms)' for ft, inch in HERO)
            + '.</desc>' + ''.join(hero) + '</svg>')

# Supporting figure (the wedge made visible): risk of death by BMI band, never-smokers (GBMC 2016).
VBW['gbmc'] = W2 = 320
BX0, K, PITCH, TOP = 78, 74, 25, 58
rows = []
band_bg = rect('gbmc', 0, TOP + PITCH * 1 - 4, W2, PITCH * 3, '#ecfdf5', rid='healthy-band')
for i, (band, hr, ci, cat) in enumerate(GBMC):
    y = TOP + i * PITCH
    rows.append(text('gbmc', BX0 - 6, y + 13, band, 12, anchor='end', fill='#1f2937'))
    rows.append(rect('gbmc', BX0, y + 2, hr * K, 15, BASE[cat], rid='bar'))
    rows.append(text('gbmc', BX0 + hr * K + 4, y + 14, f'{hr:.2f}', 12, anchor='start', weight=700, fill='#111827'))
ref_x = BX0 + K
bottom = TOP + len(GBMC) * PITCH
rows.append(f'<line x1="{ref_x}" y1="{TOP - 4}" x2="{ref_x}" y2="{bottom - 4}" stroke="#111827" stroke-width="1.5" stroke-dasharray="4 3"/>')
lab_healthy = text('gbmc', W2 - 6, TOP + PITCH * 2 + 13, 'Healthy range', 12, anchor='end', weight=700, fill='#15803d')
H2V = bottom + 40
svg_gbmc = (f'<svg viewBox="0 0 {W2} {H2V}" width="{W2}" height="{H2V}" role="img" aria-labelledby="fig-risk-t fig-risk-d" font-family="inherit">'
            '<title id="fig-risk-t">Risk of death by BMI in 3.95 million never-smokers: lowest at BMI 20 to 24.9, higher on both sides</title>'
            '<desc id="fig-risk-d">Horizontal bars, one per BMI band, showing the hazard ratio for death against BMI 22.5 to 24.9: '
            + '; '.join(f'BMI {band.replace("–", " to ")}: {hr:.2f}' for band, hr, _, _ in GBMC)
            + '. The three bands of the healthy range are shaded. Global BMI Mortality Collaboration, Lancet 2016.</desc>'
            + band_bg
            + text('gbmc', W2 / 2, 18, 'Risk of death by BMI, never-smokers', 14, weight=700)
            + text('gbmc', W2 / 2, 37, 'Hazard ratio against BMI 22.5–24.9 (= 1.00)', 12, fill='#4b5563')
            + ''.join(rows) + lab_healthy
            + text('gbmc', ref_x, bottom + 12, '1.00', 12, weight=700, fill='#111827')
            + text('gbmc', W2 / 2, bottom + 30, 'Global BMI Mortality Collaboration, Lancet 2016', 12, fill='#4b5563')
            + '</svg>')

# Data chart: share of US adults with a healthy BMI, by age and sex.
VBW['share'] = W3 = 320
GROUPS3 = [('20-39', '20–39'), ('40-59', '40–59'), ('60+', '60+'), ('all_ages', 'All 20+')]
BASE_Y, PX_PER_PT, BW, GAP = 196, 3.4, 27, 4
MEN_C, WOMEN_C = '#15803d', '#86efac'
bars3 = []
for i, (key, lab) in enumerate(GROUPS3):
    gx = 22 + i * 74
    for j, (grp, col) in enumerate(((M, MEN_C), (W, WOMEN_C))):
        v = grp[key]['healthy']; hpx = v * PX_PER_PT
        x = gx + j * (BW + GAP)
        bars3.append(rect('share', x, BASE_Y - hpx, BW, hpx, col, rid='bar',
                          extra=' stroke="#15803d" stroke-width="1"' if col == WOMEN_C else ''))
        bars3.append(text('share', x + BW / 2, BASE_Y - hpx - 5, f'{v:.1f}', 12, weight=600, fill='#111827'))
    bars3.append(text('share', gx + BW + GAP / 2, BASE_Y + 17, lab, 12, fill='#1f2937'))
legend3 = (rect('share', 22, 33, 12, 12, MEN_C) + text('share', 40, 43, 'Men', 12, anchor='start', fill='#1f2937')
           + rect('share', 92, 33, 12, 12, WOMEN_C, extra=' stroke="#15803d" stroke-width="1"')
           + text('share', 110, 43, 'Women', 12, anchor='start', fill='#1f2937'))
H3V = BASE_Y + 44
svg_share = (f'<svg viewBox="0 0 {W3} {H3V}" width="{W3}" height="{H3V}" role="img" aria-labelledby="fig-share-t fig-share-d" font-family="inherit">'
             '<title id="fig-share-t">Share of US adults with a healthy BMI, by age and sex, 2021 to 2023</title>'
             '<desc id="fig-share-d">Paired bars for men and women. '
             + '; '.join(f'ages {lab.replace("–", " to ").replace("All 20+", "all ages 20 and over")}: men {M[k]["healthy"]:.1f}%, women {W[k]["healthy"]:.1f}%'
                         for k, lab in GROUPS3)
             + '. Our calculation from CDC NHANES measurements, August 2021 to August 2023.</desc>'
             + text('share', W3 / 2, 18, 'US adults with a healthy BMI (%)', 14, weight=700)
             + legend3 + ''.join(bars3)
             + f'<line x1="14" y1="{BASE_Y}" x2="{W3 - 6}" y2="{BASE_Y}" stroke="#9ca3af" stroke-width="1"/>'
             + text('share', W3 / 2, BASE_Y + 36, 'CDC NHANES 2021–2023; our calculation', 12, fill='#4b5563')
             + '</svg>')

# Collision check on the estimated boxes (the rendered check runs in research/healthy-range-build/hbr_test_playwright.py):
# no text over text, no text over a shape unless it is the label that shape holds, nothing outside the viewBox.
def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and r[5] not in ('healthy-band',) and overlap(a, r) and a[6] != r[5]:
            raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r} / {r[5]!r}')
    if a[6]:
        holder = [r for r in RECTS if r[0] == a[0] and r[5] == a[6]][0]
        assert holder[1] + 2 <= a[1] and a[3] <= holder[3] - 2, f'label does not fit its band: {a[5]!r}'
for svg, x0, y0, x1, y1, s, _ in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in the owner's US/English pastes of 2026-10-15 ("healthy bmi range", "normal bmi", "healthy bmi"), phrased as
# asked and ordered by how many of the three pages showed them; "What is a good BMI by age?" is the same question as the first.
# The last question covers the ideal / optimal / healthiest BMI keywords this page owns.
FAQ = [
    ('What is a healthy BMI by age?',
     f'For adults 20 and over it is <strong>18.5 to 24.9</strong> at every age: CDC bases its adult categories on BMI '
     f'“regardless of age, sex, or race” ({ext(U["cdc_cat"], "CDC")}). Under 20, BMI is read as a percentile for age and '
     f'sex; use the <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a>. The evidence around the range '
     f'does change with age. In never-smokers, per 5 BMI units above 25, the risk of death was 52% higher for BMI measured '
     f'at ages 35 to 49 but 21% higher at 70 to 89 ({GBMC_CITE}). In adults 65 and over, compared with a BMI of 23 to 23.9, the risk of death '
     f'was higher below 23 and began to rise at about 33 ({ext(U["winter"], "Winter et al., 2014")}). These are associations, '
     'not separate ranges or targets.'),
    ('What is BMI for 70 kg?',
     f'It depends on height. 70 kg ({LB70} lb) is a BMI of {B70KG[160]} at 160 cm, {B70KG[170]} at 170 cm and {B70KG[180]} at '
     f'180 cm. It is a healthy weight at heights from {H70_CM[0]} to {H70_CM[-1]} cm, or from {H70_IN[0] // 12}′{H70_IN[0] % 12}″ '
     f'to {H70_IN[-1] // 12}′{H70_IN[-1] % 12}″ in whole inches. The <a href="/">BMI calculator</a> works it out for your height.'),
    ('Is a BMI of 23 chubby?',
     f'No. A BMI of 23 is a healthy weight, 2 points below where overweight starts, and it sits in 22.5 to 24.9, one of the '
     f'two bands where never-smokers had the lowest risk of death ({GBMC_CITE}). About {H23}% of US adults have a higher BMI '
     '(our calculation from CDC measurements, 2021–2023). BMI can’t show how much of your weight is fat: the '
     '<a href="/body-fat-calculator/">body fat calculator</a> estimates that, and a waist measurement reflects fat around the '
     f'abdomen ({ext(U["nhlbi_tg"], "NHLBI")}).'),
    ('What is a normal BMI for a woman?',
     f'The same as for a man: <strong>18.5 to 24.9</strong>. At 5′4″ (162.6 cm) that is {B64["minLb"]} to {B64["maxLb"]} lb '
     f'({B64["minKg"]} to {B64["maxKg"]} kg). {W["all_ages"]["healthy"]}% of US women have a BMI in the range (our '
     f'calculation from CDC measurements, 2021–2023). The waist cut-offs differ: US guidelines treat a waist '
     f'over 35 inches (88 cm) in women as a marker of higher risk, against 40 inches (102 cm) in men, mainly at a BMI of 25 to '
     f'34.9 ({ext(U["nhlbi_tg"], "NHLBI")}).'),
    ('What is the BMI of normal?',
     f'A normal BMI for adults is <strong>18.5 to 24.9</strong>, the range CDC calls a healthy weight. Under 18.5 is '
     'underweight, 25 to 29.9 is overweight and 30 or more is obesity, in three classes: 30 to 34.9, 35 to 39.9 and 40 or '
     f'more ({ext(U["cdc_cat"], "CDC")}). The same ranges apply to every adult aged 20 and over; the '
     '<a href="/bmi-chart/">BMI chart</a> lists the weights for each height.'),
    ('Is a BMI of 25 realistic?',
     f'For most US adults, a BMI under 25 means losing weight: {SHARE25}% have a BMI of 25 or more, and the median is {MEDIAN} '
     '(our calculation from CDC measurements, 2021–2023). Smaller changes count too: in an analysis of the Look AHEAD trial in '
     'adults with overweight or obesity and type 2 diabetes, losing 5 to 10% of body weight was linked to better blood sugar, '
     f'blood pressure, HDL cholesterol and triglycerides after one year ({ext(U["wing"], "Wing et al., 2011")}).'),
    ('Is a BMI of 12 healthy?',
     f'No. A BMI of 12 is far below the healthy range of 18.5 to 24.9. WHO’s 1995 expert report puts any adult BMI under 16 in '
     f'grade 3 thinness, the most severe of its three grades ({ext(U["who1995"], "WHO, 1995")}). Even at 15 to 18.4, '
     f'never-smokers had a 51% higher risk of death than at 22.5 to 24.9; the study left out BMIs under 15 ({GBMC_CITE}). CDC '
     f'notes that “poor nutrition and underlying health conditions can result in underweight” '
     f'({ext(U["he119"], "Health E-Stat 119")}), and {ext(U["mlp"], "MedlinePlus")} (NIH) advises contacting a health care '
     'provider if you lose more weight than is considered healthy for your age and height.'),
    ('What is the healthiest BMI?',
     f'There is no single number. Among {GBMC_N:,} never-smokers in {GBMC_N_STUDIES} studies, the risk of death was lowest '
     f'at a BMI of <strong>20 to 24.9</strong>, and the bands 20 to 22.4 and 22.5 to 24.9 had about the same risk ({GBMC_CITE}). '
     f'Below 20 it rose (13% higher at 18.5 to 19.9), and above 25 it rose step by step (7% higher at 25 to 27.4, 20% at '
     f'27.5 to 29.9).'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
def cat_cell(cls, name): return f'<span class="cat-dot {cls}" aria-hidden="true"></span>{name}'

head = (
    '<div class="page-head"><h1>Healthy BMI Range: What Is a Normal BMI?</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Is a BMI of 23 chubby? What BMI is 70 kg? Does the healthy range change with age, or for women?</p>'
    f'<p class="intro-text">Only about 1 in 4 US adults ({A["all_ages"]["healthy"]}%) has a BMI in CDC’s healthy range of '
    f'18.5 to 24.9. Among {GBMC_N / 1e6:.2f} million never-smokers without chronic disease, the risk of death was lowest at '
    f'a BMI of 20 to 24.9 ({GBMC_CITE}).</p>'
    '<p class="intro-text">Below: healthy weights by height, what death rates show about the range, and US adults in it by '
    'age and sex.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>A healthy BMI for adults is 18.5 to 24.9.</strong> CDC calls this range a healthy weight and '
    'uses it for everyone aged 20 and over, regardless of age, sex or race. A normal BMI means the same range. Under 18.5 is '
    'underweight, 25 to 29.9 is overweight and 30 or more is obesity. Before age 20, BMI is read as a percentile instead.</p><ul>'
    f'<li>The healthy weight depends only on height: <strong>{B64["minLb"]} to {B64["maxLb"]} lb ({B64["minKg"]} to '
    f'{B64["maxKg"]} kg) at 5′4″</strong> and {B70["minLb"]} to {B70["maxLb"]} lb ({B70["minKg"]} to {B70["maxKg"]} kg) at '
    '5′10″.</li>'
    f'<li><strong>{W["all_ages"]["healthy"]}% of US women and {M["all_ages"]["healthy"]}% of men have a healthy BMI</strong>; '
    f'by age, {A["20-39"]["healthy"]}% at 20 to 39, {A["40-59"]["healthy"]}% at 40 to 59 and {A["60+"]["healthy"]}% at 60 and '
    'over (our calculation from CDC measurements, 2021–2023).</li>'
    '<li><strong>Risk is not flat inside the range.</strong> In never-smokers, the risk of death was 13% higher at 18.5 to '
    '19.9 than at 22.5 to 24.9; just above the range, at 25 to 27.4, it was 7% higher.</li>'
    '<li>The range is the same for women and men; the waist cut-off isn’t: 35 inches (88 cm) for women, 40 inches (102 cm) '
    'for men.</li>'
    '<li><strong>BMI can’t tell muscle from fat</strong>, so a waist or body-fat measurement adds what it misses.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This guide is for information only. BMI is a '
    'screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>The healthy range is the same BMI for every adult, 18.5 to 24.9; '
            'in pounds and kilograms it moves with height. Cut-offs: CDC.</figcaption></figure>')

toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in (
           ('range', 'The range'), ('by-height', 'By height'), ('age', 'Age'), ('women-men', 'Women and men'),
           ('evidence', 'Why 18.5–24.9'), ('us-adults', 'US adults'), ('ethnicity', 'Ethnicity'),
           ('beyond', 'Beyond BMI'), ('reaching', 'Reaching the range'), ('faq', 'FAQ'), ('sources', 'Sources')))
       + '</nav>')

cat_rows = ''.join(
    f'<tr><th scope="row">{cat_cell(cls, name)}</th><td>{rng}</td><td class="num">{share}%</td></tr>'
    for cls, name, rng, share in (
        ('underweight', 'Underweight', 'Under 18.5', CS['underweight']),
        ('normal', 'Healthy weight', '18.5–24.9', CS['healthy']),
        ('overweight', 'Overweight', '25–29.9', CS['overweight']),
        ('obese', 'Class 1 obesity', '30–34.9', CS['obesity_class_1']),
        ('obese', 'Class 2 obesity', '35–39.9', CS['obesity_class_2']),
        ('obese-severe', 'Class 3 obesity', '40 or more', CS['obesity_class_3'])))
sec_range = (
    '<section id="range" class="content-section flow"><h2>What is the healthy BMI range?</h2>'
    '<p>For adults 20 and older, CDC calls a BMI of <strong>18.5 to less than 25</strong> a healthy weight. BMI is reported to '
    'one decimal, so in practice the range is 18.5 to 24.9. CDC bases the adult categories “on a person’s BMI regardless of '
    f'age, sex, or race” ({ext(U["cdc_cat"], "CDC")}), and WHO’s adult definitions use the same lines: overweight from 25, '
    f'obesity from 30 ({ext(U["who_fs"], "WHO")}). NIH’s heart institute lists the same ranges ({ext(U["nhlbi_calc"], "NHLBI")}). '
    'Whether a chart calls it normal, healthy or good, it means this range.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Adult BMI categories and the share of US adults in each, '
    '2021–2023</caption><thead><tr><th scope="col">Category</th><th scope="col">BMI</th><th scope="col" class="num">US adults'
    f'</th></tr></thead><tbody>{cat_rows}</tbody></table></div>'
    f'<p class="source-note">Categories: {ext(U["cdc_cat"], "CDC Adult BMI Categories")}. Shares: our calculation from CDC '
    f'NHANES August 2021–August 2023 ({A["all_ages"]["n"]:,} adults aged 20 and over); they match NCHS’s published crude rates for '
    f'underweight ({ext(U["he119"], "Health E-Stat 119")}), overweight ({ext(U["he111"], "Health E-Stat 111")}), obesity and '
    f'class 3 obesity ({ext(U["db508"], "Data Brief 508")}).</p>'
    '<p>BMI is your weight in kilograms divided by your height in meters squared, or your weight in pounds times 703 divided '
    f'by your height in inches squared ({ext(U["cdc_formula"], "CDC")}). The median US adult has a BMI of {MEDIAN}, which is in '
    'the overweight range (our calculation from CDC measurements, 2021–2023). The <a href="/blog/bmi-formula/">BMI formula '
    'guide</a> walks through the calculation, the '
    '<a href="/bmi-chart/">BMI chart</a> gives the weights for every category at each height, and '
    '<a href="/blog/bmi-categories/">BMI categories explained</a> covers what each range means.</p>'
    '</section>')

h_rows = ''.join(
    f'<tr><th scope="row">{ft}′{inch}″<span class="unit-alt">({cm:.1f} cm)</span></th>'
    f'<td class="nowrap">{hb["minLb"]}–{hb["maxLb"]} lb<span class="unit-alt">({hb["minKg"]}–{hb["maxKg"]} kg)</span></td>'
    f'<td class="nowrap">{ob["minLb"]}–{ob["maxLb"]} lb<span class="unit-alt">({ob["minKg"]}–{ob["maxKg"]} kg)</span></td></tr>'
    for ft, inch, cm, hb, ob, xb in ROWS)
sec_height = (
    '<section id="by-height" class="content-section flow"><h2>Healthy weight by height</h2>'
    f'<p>In pounds or kilograms, the healthy range depends only on height. At 5′4″ (162.6 cm) it runs from <strong>'
    f'{B64["minLb"]} to {B64["maxLb"]} lb ({B64["minKg"]} to {B64["maxKg"]} kg)</strong>; at 5′10″ (177.8 cm), from <strong>'
    f'{B70["minLb"]} to {B70["maxLb"]} lb ({B70["minKg"]} to {B70["maxKg"]} kg)</strong>. Every 2 inches of height moves the '
    f'lower limit up by {STEP_MIN[0]} to {STEP_MIN[-1]} lb and the upper limit by {STEP_MAX[0]} to {STEP_MAX[-1]} lb.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Healthy weight and overweight by height, adults</caption>'
    '<thead><tr><th scope="col">Height</th><th scope="col">Healthy weight<span class="unit-alt">BMI 18.5–24.9</span></th>'
    '<th scope="col">Overweight<span class="unit-alt">BMI 25–29.9</span></th></tr></thead>'
    f'<tbody>{h_rows}</tbody></table></div>'
    '<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, falls in each range at the height '
    'shown. Each unit is worked out on its own, so the kilogram limits are not conversions of the pound limits. Obesity starts '
    'at the next pound or kilogram above the overweight range. Cut-offs: ' + ext(U['cdc_cat'], 'CDC Adult BMI Categories') + '.</p>'
    '<p>The <a href="/bmi-chart/">BMI chart</a> covers every inch from 4′10″ to 6′6″, and there are BMI charts '
    '<a href="/blog/bmi-chart-women/">for women</a> and <a href="/blog/bmi-chart-men/">for men</a>. The '
    '<a href="/">BMI calculator</a> gives the range for your exact height.</p>'
    '</section>')

gbmc_rows = ''.join(
    f'<tr><th scope="row">{cat_cell(cat, band)}</th><td class="num">{hr:.2f}'
    f'{"<span class=\"unit-alt\">reference</span>" if band == "22.5–24.9" else ""}</td><td class="num nowrap">{ci}</td></tr>'
    for band, hr, ci, cat in GBMC)
sec_evidence = (
    '<section id="evidence" class="content-section flow"><h2>Why 18.5 to 24.9? What the mortality data show</h2>'
    '<p>The cut-offs follow health risk. US guidelines link a BMI above the range with higher risk of high blood pressure, '
    f'type 2 diabetes, coronary heart disease, stroke, sleep apnea and osteoarthritis ({ext(U["nhlbi"], "NHLBI")}). Those '
    '1998 guidelines already used the 18.5, 25 and 30 cut-offs; later studies tested them against death rates.</p>'
    f'<p>The {ext(U["gbmc"], "Global BMI Mortality Collaboration")} pooled {GBMC_STUDIES} studies of '
    f'{GBMC_N_ALL / 1e6:.1f} million people in {GBMC_COUNTRIES} countries (Lancet, 2016). To keep smoking and existing illness '
    f'from distorting the picture, its main analysis used {GBMC_N:,} never-smokers who had no chronic disease when they '
    f'joined and survived the first five years; {GBMC_DEATHS:,} of them died during follow-up.</p>'
    '<p>Crude analyses that ignored smoking and existing disease gave exaggerated risks for '
    'underweight and inverted ones for overweight, so overweight looked protective. The authors could reproduce a 2013 '
    'review’s finding that overweight carried a lower risk of death in analyses with inadequate control for these biases, '
    'but not in the strict one.</p>'
    '<p><strong>The risk of death was lowest at a BMI of 20 to 24.9.</strong> Compared with 22.5 to 24.9, it was 13% higher at '
    '18.5 to 19.9 and 51% higher at 15 to 18.4. Above the range it rose at every step: 7% higher at 25 to 27.4, 20% at 27.5 '
    'to 29.9, 45% at 30 to 34.9, 94% at 35 to 39.9, and 2.76 times as high at 40 to 59.9.</p>'
    f'<figure class="figure">{svg_gbmc}<figcaption>Hazard ratio for death by BMI band among {GBMC_N:,} never-smokers without '
    'chronic disease; 1.20 means a 20% higher risk than at 22.5 to 24.9. The three shaded bands make up the healthy '
    'range.</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table"><caption>Risk of death by BMI, never-smokers without chronic '
    'disease (Global BMI Mortality Collaboration, 2016)</caption><thead><tr><th scope="col">BMI</th>'
    '<th scope="col" class="num">Hazard ratio</th><th scope="col" class="num">95% CI</th></tr></thead>'
    f'<tbody>{gbmc_rows}</tbody></table></div>'
    '<p class="source-note">All-cause death against BMI 22.5 to 24.9, in never-smokers without chronic disease at '
    f'recruitment who survived the first five years ({GBMC_N:,} people, {GBMC_N_STUDIES} studies). Bands as published (15 to '
    f'under 18.5, 18.5 to under 20, and so on; the top band is 40 to under 60). Source: {ext(U["gbmc"], "Lancet 2016;388:776–86")}.</p>'
    '<p>Per 5 BMI units above 25, the risk of death in never-smokers was 39% higher in '
    'Europe and in East Asia, 31% in Australia and New Zealand and 29% in North America; the authors write that “the '
    'associations of both overweight and obesity with higher all-cause mortality were broadly consistent in four continents”. '
    'These are associations in observational data; they don’t show how much changing your own BMI would change your risk.</p>'
    '</section>')

age_rows = ''.join(
    f'<tr><th scope="row">{lab}</th><td class="num">{A[k]["healthy"]}%</td><td class="num">{M[k]["healthy"]}%</td>'
    f'<td class="num">{W[k]["healthy"]}%</td></tr>'
    for k, lab in (('20-39', '20 to 39'), ('40-59', '40 to 59'), ('60+', '60 and over'), ('all_ages', 'All, 20 and over')))
sec_us = (
    '<section id="us-adults" class="content-section flow"><h2>How many US adults have a healthy BMI?</h2>'
    f'<div class="stat-callout"><div class="stat-callout-value">{A["all_ages"]["healthy"]}%</div><div class="stat-callout-text">'
    f'of US adults aged 20 and over have a BMI of 18.5 to 24.9: {M["all_ages"]["healthy"]}% of men and '
    f'{W["all_ages"]["healthy"]}% of women, August 2021–August 2023.</div><div class="stat-callout-source">Source: our '
    f'calculation from {ext(U["bmx"], "CDC NHANES 2021–2023")} measurements ({A["all_ages"]["n"]:,} adults; 95% confidence '
    f'interval {CI26[0]}% to {CI26[1]}%)</div></div>'
    f'<p>Women are more likely than men to have a healthy BMI: {W["all_ages"]["healthy"]}% against {M["all_ages"]["healthy"]}%. '
    f'<strong>The share is highest among women aged 20 to 39, at {W["20-39"]["healthy"]}%</strong>; in the other age and sex '
    f'groups it runs from {OTHER[0]}% to {OTHER[-1]}%.</p>'
    f'<figure class="figure">{svg_share}<figcaption>Share of US adults with a BMI of 18.5 to 24.9, by age group and sex. CDC '
    'measurements, August 2021–August 2023; our calculation.</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table"><caption>US adults with a healthy BMI (18.5–24.9), by age and '
    'sex, 2021–2023</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">All adults</th>'
    f'<th scope="col" class="num">Men</th><th scope="col" class="num">Women</th></tr></thead><tbody>{age_rows}</tbody></table></div>'
    f'<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023 measured heights and weights '
    f'({A["all_ages"]["n"]:,} adults aged 20 and over: {M["all_ages"]["n"]:,} men and {W["all_ages"]["n"]:,} women; '
    'survey-weighted; pregnant women excluded). The same method reproduces NCHS’s published crude rates: obesity 40.3% (39.2% '
    'of men, 41.3% of women; 35.5%, 46.4% and 38.9% at ages 20 to 39, 40 to 59 and 60 and over), class 3 obesity 9.4%, '
    f'overweight 32.1% and underweight 1.6%. These are survey estimates: each age-and-sex share has a 95% margin of error of '
    f'about ±{HALF_LO} to ±{HALF_HI} points, so small gaps between groups can be sampling noise.</p>'
    '<p>For how the shares above 25 have changed since 1960, the <a href="/us-obesity-statistics/">US obesity statistics</a> '
    'page has the trends.</p>'
    '</section>')

sec_wm = (
    '<section id="women-men" class="content-section flow"><h2>Is the healthy BMI range different for women and men?</h2>'
    '<p><strong>No.</strong> CDC’s cut-offs are the same for women and men, so the healthy weight at a given height is the same '
    'too.</p>'
    f'<p>Body fat at a given BMI depends on sex '
    f'({ext(U["gallagher"], "Gallagher et al., 2000")}): in CDC’s body scans of adults aged 20 to 59 with a BMI of 18.5 to '
    f'24.9, the median woman had <strong>{BF_W}% body fat</strong> and the median man {BF_M}% (our analysis of NHANES '
    '2011–2018). Waist cut-offs also differ by sex: US guidelines treat a waist over 35 inches (88 cm) in women and over 40 '
    f'inches (102 cm) in men as a marker of higher risk, mainly at a BMI of 25 to 34.9 ({ext(U["nhlbi_tg"], "NHLBI")}).</p>'
    f'<p>The link between BMI and death is steeper in men: in never-smokers, per 5 BMI units above 25, the risk of death was 51% '
    f'higher in men and 30% higher in women ({GBMC_CITE}). In the US, {W["all_ages"]["healthy"]}% of women and '
    f'{M["all_ages"]["healthy"]}% of men have a healthy BMI (our calculation from CDC measurements, 2021–2023). The BMI '
    'calculators <a href="/women-bmi-calculator/">for women</a> and '
    '<a href="/men-bmi-calculator/">for men</a> add the US data for each sex.</p>'
    '</section>')

sec_age = (
    '<section id="age" class="content-section flow"><h2>Does the healthy BMI range change with age?</h2>'
    '<p><strong>Not for adults.</strong> CDC uses one set of categories for everyone aged 20 and over. Three things around it '
    'do change with age:</p><ul>'
    '<li><strong>Body fat at the same BMI.</strong> It depends on age as well as sex '
    f'({ext(U["gallagher"], "Gallagher et al., 2000")}), so the same BMI can mean a different amount of fat at 25 and at '
    '75.</li>'
    '<li><strong>How strongly BMI tracks death.</strong> In never-smokers, per 5 BMI units above 25, the risk of death was 52% higher for BMI '
    f'measured at ages 35 to 49 but 21% higher for BMI measured at 70 to 89 ({GBMC_CITE}).</li>'
    '<li><strong>Mortality data in adults 65 and over.</strong> In a meta-analysis of 197,940 people aged 65 and over, '
    'compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 '
    f'({ext(U["winter"], "Winter et al., 2014")}). That is an association, not a separate healthy range or a target.</li></ul>'
    '<p>The <a href="/age-bmi-calculator/">BMI calculator by age</a> '
    'has more on adults 65 and over, and <a href="/blog/bmi-by-age/">BMI by age</a> explains how the range applies across '
    'adult life.</p>'
    '<h3>Children and teens</h3>'
    '<p>Under 20, the same BMI means different things at different ages, so CDC reads it as a percentile on growth charts for '
    'age and sex. A healthy weight is the 5th to under the 85th percentile; the '
    '<a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it out for ages 2 to 19.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>BMI categories for children and teens aged 2 to 19'
    '</caption><thead><tr><th scope="col">Category</th><th scope="col">BMI-for-age percentile</th></tr></thead><tbody>'
    f'<tr><th scope="row">{cat_cell("underweight", "Underweight")}</th><td>Under the 5th</td></tr>'
    f'<tr><th scope="row">{cat_cell("normal", "Healthy weight")}</th><td>5th to under the 85th</td></tr>'
    f'<tr><th scope="row">{cat_cell("overweight", "Overweight")}</th><td>85th to under the 95th</td></tr>'
    f'<tr><th scope="row">{cat_cell("obese", "Obesity")}</th><td>95th or above</td></tr>'
    f'<tr><th scope="row">{cat_cell("obese-severe", "Severe obesity")}</th><td>120% of the 95th or more, or a BMI of 35 or more</td></tr>'
    '</tbody></table></div>'
    f'<p class="source-note">Source: {ext(U["cdc_child"], "CDC Child and Teen BMI Categories")}.</p>'
    '</section>')

sec_eth = (
    '<section id="ethnicity" class="content-section flow"><h2>Does the healthy BMI range change with ethnicity?</h2>'
    '<p>In the US, CDC’s BMI categories don’t change with race, but its National Diabetes Prevention Program takes Asian '
    f'American adults from a BMI of 23 instead of 25 ({ext(U["ndpp"], "CDC")}). Outside the US, three documents address it:</p><ul>'
    '<li>The WHO Western Pacific Region, the International Association for the Study of Obesity and the '
    'International Obesity Task Force proposed lower cut-offs for Asian adults in 2000: <strong>overweight from 23 and obesity from '
    f'25</strong> (cited in {ext(U["kotang"], "Ko and Tang, 2006")}).</li>'
    '<li>A WHO expert consultation in 2004 found that the share of Asian people at high risk of type 2 diabetes and '
    'cardiovascular disease is substantial below a BMI of 25. It kept the international categories for everyone and added BMI '
    f'23, 27.5, 32.5 and 37.5 as points for public-health action ({ext(U["who2004"], "WHO, 2004")}).</li>'
    '<li>In the UK, NICE says people with a South Asian, Chinese, other Asian, Middle Eastern, Black African or '
    'African-Caribbean background are prone to central adiposity and reach cardiometabolic risk at a lower BMI. It uses '
    '<strong>overweight from 23 to 27.4 and obesity from 27.5</strong> for them '
    f'({ext(U["nice"], "NICE guideline NG246")}, a 2022 recommendation).</li></ul>'
    '<p>Above 25, the link between BMI and death was as strong in East Asia as in Europe: in never-smokers, per 5 BMI units, '
    f'the risk of death was 39% higher in both ({GBMC_CITE}). The study had too few deaths in South Asia to give a reliable estimate there.</p>'
    '</section>')

sec_beyond = (
    '<section id="beyond" class="content-section flow"><h2>What a healthy BMI can’t tell you</h2>'
    '<p>CDC calls BMI “a quick, safe, and reliable screening measure” but notes that it “does not directly measure body fat” '
    f'and “does not distinguish between fat, muscle, and bone mass” ({ext(U["cdc_about"], "CDC")}). For one person, CDC says '
    'BMI “should be considered with other factors”. Three checks fill the gaps:</p><ul>'
    '<li><strong>Waist.</strong> Waist size reflects fat around the abdomen, which US guidelines treat as an independent '
    f'predictor of risk ({ext(U["nhlbi_tg"], "NHLBI")}); the <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> '
    'compares it with your height.</li>'
    '<li><strong>Body fat.</strong> The <a href="/body-fat-calculator/">body fat calculator</a> estimates it from tape or '
    'skinfold measurements, and the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows typical values '
    'from CDC body scans.</li>'
    '<li><strong>Muscle.</strong> Because BMI can’t separate muscle from fat, a muscular person can have a BMI over 25 with '
    'little body fat; <a href="/blog/bmi-for-athletes/">BMI for athletes</a> goes further.</li></ul>'
    f'<p>In 2025 the {ext(U["lancet"], "Lancet Commission on Clinical Obesity")} recommended confirming excess body fat with a '
    'body measurement such as waist size, or with a direct body-fat measurement, instead of diagnosing obesity from BMI alone; '
    'above a BMI of 40 it says excess fat can be assumed. <a href="/blog/bmi-limitations/">BMI limitations</a> covers the '
    'rest.</p>'
    '</section>')

sec_reach = (
    '<section id="reaching" class="content-section flow"><h2>How to reach or stay in the healthy range</h2>'
    '<p>Official US guidance, and what one large trial found:</p><ul>'
    '<li><strong>Activity.</strong> “[A]dults need at least 150 to 300 minutes of moderate-intensity aerobic activity” a week, '
    f'plus muscle-strengthening activity on at least 2 days ({ext(U["pag"], "Physical Activity Guidelines for Americans")}).</li>'
    f'<li><strong>A plan for a goal weight.</strong> NIH’s {ext(U["bwp"], "Body Weight Planner")} builds a calorie and physical '
    'activity plan for a goal weight, for adults who aren’t pregnant or breastfeeding.</li>'
    '<li><strong>Above 25.</strong> In an analysis of a large trial (Look AHEAD) in adults with overweight or obesity and type 2 '
    'diabetes, losing 5 to 10% of body weight was linked to better blood sugar, blood pressure, HDL cholesterol and '
    'triglycerides after one year '
    f'({ext(U["wing"], "Wing et al., 2011")}). <a href="/blog/how-to-lower-bmi/">How to lower your BMI</a> covers diet, '
    'activity and when to seek medical help.</li>'
    '<li><strong>Under 18.5.</strong> CDC notes that “poor nutrition and underlying health conditions can result in '
    f'underweight” ({ext(U["he119"], "Health E-Stat 119")}). {ext(U["mlp"], "MedlinePlus")} (NIH) advises contacting a health '
    'care provider if you lose more than 10 lb (4.5 kg) or 5% of your body weight within 6 to 12 months without knowing why. '
    '<a href="/blog/underweight-bmi-risks/">Underweight BMI risks</a> covers the causes.</li></ul>'
    '<p>The <a href="/">BMI calculator</a> shows how far your weight is from the range at your height, in pounds and '
    'kilograms, and the <a href="/ideal-weight/">ideal weight calculator</a> shows the single weights four published formulas '
    'give.</p>'
    '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the adult cut-offs and the “regardless of age, sex, or race” rule.',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'CDC. {ext(U["cdc_about"], "About Body Mass Index (BMI)")}: what BMI measures and what it misses.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formulas in metric and US units.',
    f'NHLBI. {ext(U["nhlbi_calc"], "Calculate Your BMI")}: the same adult ranges.',
    f'WHO. {ext(U["who_fs"], "Obesity and overweight")} (fact sheet): adult overweight from 25, obesity from 30.',
    f'The Global BMI Mortality Collaboration. {ext(U["gbmc"], "Body-mass index and all-cause mortality")} (Lancet, 2016): '
    f'{GBMC_STUDIES} studies, {GBMC_N_ALL:,} participants; hazard ratios in {GBMC_N:,} never-smokers without chronic disease.',
    f'CDC {ext(U["bmx"], "NHANES August 2021–August 2023")} exam files (DEMO_L, BMX_L): our calculation of the share of adults '
    f'aged 20 and over in each BMI category by age and sex ({A["all_ages"]["n"]:,}: {M["all_ages"]["n"]:,} men, '
    f'{W["all_ages"]["n"]:,} women), weighted with the exam weights, pregnant women excluded.',
    f'Emmerich SD, et al. {ext(U["db508"], "NCHS Data Brief No. 508")} (Sep 2024): obesity and severe obesity in US adults, '
    'August 2021–August 2023.',
    f'Fryar CD, Afful J, Saif NT. {ext(U["he111"], "NCHS Health E-Stat 111")} (Feb 2026): overweight and obesity in US adults.',
    f'Ansai N, Fryar CD, Afful J. {ext(U["he119"], "NCHS Health E-Stat 119")} (Jun 2026): underweight in US adults.',
    'CDC NHANES 2011–2018 DXA body scans: our analysis of body fat by sex at a BMI of 18.5 to 24.9, ages 20 to 59 '
    '(<a href="/body-fat-percentage-chart/">body fat percentage chart</a>).',
    f'NHLBI. {ext(U["nhlbi"], "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")} '
    '(NIH, 1998): conditions linked to excess weight; waist cut-offs and abdominal fat in its '
    f'{ext(U["nhlbi_tg"], "treatment guidelines chapter")}.',
    f'CDC. {ext(U["ndpp"], "National Diabetes Prevention Program eligibility")}: BMI of 25 or higher, 23 or higher for Asian '
    'American adults.',
    f'Gallagher D, et al. {ext(U["gallagher"], "American Journal of Clinical Nutrition, 2000")}: body fat predicted from BMI, '
    'sex, age and ethnic group.',
    f'Winter JE, et al. {ext(U["winter"], "American Journal of Clinical Nutrition, 2014")}: BMI and mortality in adults 65 and over.',
    f'WHO Expert Consultation. {ext(U["who2004"], "The Lancet, 2004")}: BMI in Asian populations and the public-health action points.',
    f'Ko GT, Tang JS. {ext(U["kotang"], "Asia Pacific Journal of Clinical Nutrition, 2006")}: cites the 2000 WHO Western Pacific '
    'Region, IASO and IOTF proposal (overweight from 23, obesity from 25 for Asian adults).',
    f'NICE (UK). {ext(U["nice"], "Overweight and obesity management, guideline NG246")}: lower BMI thresholds for people from '
    'some ethnic backgrounds (recommendation 1.9.11, 2022).',
    f'WHO. {ext(U["who1995"], "Physical status: the use and interpretation of anthropometry")} (Technical Report Series 854, '
    '1995): thinness grades.',
    f'Rubino F, et al. {ext(U["lancet"], "Lancet Diabetes & Endocrinology, 2025")}: definition and diagnostic criteria of '
    'clinical obesity.',
    f'US Department of Health and Human Services. {ext(U["pag"], "Physical Activity Guidelines for Americans, 2nd edition")}: '
    'activity for adults.',
    'NIDDK. ' + ext(U['bwp'], 'Body Weight Planner') + ': calorie and physical activity plans for a goal weight, adults only.',
    f'Wing RR, et al. {ext(U["wing"], "Diabetes Care, 2011")}: weight loss and cardiovascular risk factors after one year, '
    'an analysis of the Look AHEAD trial.',
    f'MedlinePlus (NIH National Library of Medicine). {ext(U["mlp"], "Weight loss - unintentional")}: when to contact a '
    'health care provider.',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Shares of US adults: CDC NHANES August 2021–August 2023, adults aged 20 and '
    'over with a measured height and weight, pregnant women excluded, weighted with the exam weights; BMI as CDC records it, '
    'to one decimal; the shares reproduce NCHS’s published rates (listed in the note under the US adults table). Healthy '
    'weight by height: the '
    'lightest and heaviest whole pounds (or kilograms) whose BMI, rounded '
    'to one decimal, is 18.5 to 24.9, each unit worked out on its own; BMI = lb × 703 ÷ in², or kg ÷ m². Hazard ratios are '
    'quoted from the Global BMI Mortality Collaboration as published; percentages such as “13% higher” are the hazard ratio '
    'minus 1.</p>'
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
        ('/bmi-chart/', 'BMI chart'), ('/blog/bmi-chart-women/', 'BMI chart for women'),
        ('/blog/bmi-chart-men/', 'BMI chart for men'), ('/blog/bmi-categories/', 'BMI categories explained'),
        ('/blog/bmi-by-age/', 'BMI by age'), ('/blog/bmi-formula/', 'BMI formula'), ('/blog/what-is-bmi/', 'What is BMI'),
        ('/blog/bmi-limitations/', 'BMI limitations'), ('/us-obesity-statistics/', 'US obesity statistics')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> <article> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_range, sec_height, sec_age, sec_wm, sec_evidence, sec_us, sec_eth,
     sec_beyond, sec_reach, sec_faq, sec_src, sec_rel]) + ' </article> </div></main>')
assert 'id="edges"' not in main and 'id="asian"' not in main

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'Healthy BMI Range: What Is a Normal BMI for Adults?'
H1 = 'Healthy BMI Range: What Is a Normal BMI?'
DESC = ('A healthy BMI for adults is 18.5 to 24.9 at every age, for women and men. See the healthy weight for your height '
        'and how many US adults are in the range.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'Healthy BMI range: 18.5 to 24.9 for every adult'
OG_D = ('Healthy weight by height, the share of US adults in the range by age and sex (CDC data, our calculation), and what '
        'death rates show about the range.')
OG_IMG = 'https://calculatemybmi.net/assets/images/og/healthy-bmi-range-risk.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG_IMG}">', src)
src = sub1(r'<meta property="article:modified_time" content="[^"]*">', '<meta property="article:modified_time" content="{TODAY}T00:00:00Z">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG_IMG}">', src)

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
types = [json.loads(b.group(1))['@type'] for b in blocks]
assert types == ['Article', 'BreadcrumbList', 'FAQPage'], types
art = json.loads(blocks[0].group(1))
art.update({'headline': H1, 'image': OG_IMG, 'description': DESC, 'dateModified': '{TODAY}'})
assert art['datePublished'] == '2026-01-15'
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
for b, new in ((blocks[2], faq_ld), (blocks[0], art)):            # back to front, so offsets stay valid
    src = src[:b.start(1)] + ' ' + json.dumps(new, ensure_ascii=False) + ' ' + src[b.end(1):]

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('{TODAY}') == 2

open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>', ' ', main)).split())
print(f'blog/healthy-bmi-range/index.html written: {len(src):,} bytes, {words:,} words in <main>, {len(FAQ)} FAQ, '
      f'{len(TEXTS)} SVG labels checked')
