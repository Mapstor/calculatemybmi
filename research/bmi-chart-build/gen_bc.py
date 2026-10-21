#!/usr/bin/env python3
"""CMB-015 BMI-CHART — rebuilds /bmi-chart/ to the D-14 guide pattern (DESIGN.md "Guide pages", as
/blog/bmi-chart-women/ applied it in CMB-014): intro, answer block and key takeaways, a hero figure, contents chips,
the chart as real tables (pounds and kilograms) plus a printable BMI table image, the chart turned around (heights for
each weight), a flat FAQ whose JSON-LD equals the visible answers, sources and method, one related block, one 680 px
reading column.

Wedge: the June 2026 American Diabetes Association waist rule on the chart (the waist line for every height, and the
rule applied to US adults: our calculation from CDC NHANES August 2021-August 2023, which reproduces NCHS's published
rates), where 600 US adults sit on the chart, and the heights at which a given weight is healthy (answers "Is 70 kg a
normal weight?").

Images in search results (CMB-015): the page names a text-free preferred image (og:image, Article image in 1:1, 4:3
and 16:9, WebPage primaryImageOfPage; research/preferred-images/), carries max-image-preview:large, and shows its
printable table as an <img> listed in the image sitemap.

Every number on the page comes from bc_stats.json, research/healthy-range-build/healthy_stats.json,
research/average-weight/avgw_results.json, research/body-fat/bf_results.json,
the weight-table gate's own rule (scripts/check_weight_tables.py), or a source verified in chat on 2026-10-15/16
(constants below, each with its source; all listed in "Sources and method").

usage: python3 gen_bc.py REPO_ROOT STATS_JSON
Runs once, on bmi-chart/index.html as it stood at 621bf8b; kept as the build record. The page is written with {TODAY}
in its schema dateModified; apply_build.py puts in the apply date (manifest "today": true).
"""
import sys, os, re, json, html, math

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
HS = json.load(open(os.path.join(ROOT, 'research/healthy-range-build/healthy_stats.json')))
AVGW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json')))
BF = json.load(open(os.path.join(ROOT, 'research/body-fat/bf_results.json')))
PAGE = os.path.join(ROOT, 'bmi-chart/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds, round1, category       # the CMB-008 gate's own rule

SITE = 'https://calculatemybmi.net'
URL = SITE + '/bmi-chart/'

# ---------------------------------------------------------------- numbers: US adults (our calculation)
C = S['categories']
GR = ('all', 'men', 'women')
def p(g, c): return C[g][c]['pct']
assert [C[g]['n'] for g in GR] == [5929, 2680, 3249]
assert [p(g, 'underweight') for g in GR] == [1.6, 1.1, 2.0]
assert [p(g, 'healthy') for g in GR] == [26.0, 24.0, 28.1]
assert [p(g, 'overweight') for g in GR] == [32.1, 35.7, 28.6]
assert [p(g, 'obesity') for g in GR] == [40.3, 39.2, 41.3]                     # = NCHS Data Brief 508
assert [p(g, 'class_3') for g in GR] == [9.4, 6.7, 12.1]                       # = NCHS Data Brief 508
for g in GR:                                                     # rounded shares: sums agree to within 0.1-0.2
    assert abs(p(g, 'class_1') + p(g, 'class_2') + p(g, 'class_3') - p(g, 'obesity')) <= 0.11, g
    assert abs(sum(p(g, k) for k in ('underweight', 'healthy', 'overweight', 'class_1', 'class_2', 'class_3')) - 100) <= 0.21, g
CATKEYS = ('underweight', 'healthy', 'overweight', 'class_1', 'class_2', 'class_3', 'obesity')
HALF_HI = round(max((C[g][c]['ci95'][1] - C[g][c]['ci95'][0]) / 2 for g in GR for c in CATKEYS), 1)
assert HALF_HI == 4.7, HALF_HI
SD = S['sex_differences']
assert SD['healthy_women_minus_men']['ci95'][0] > 0 and SD['class_3_women_minus_men']['ci95'][0] > 0     # stated
assert SD['obesity_women_minus_men']['ci95'][0] < 0 < SD['obesity_women_minus_men']['ci95'][1]          # not stated
U20 = S['bmi_under_20']['all']['pct']; assert U20 == 4.6
HCOV = S['height_on_chart']['all']['pct']; assert HCOV == 99.2
AGE = {a: HS['groups']['all'][a]['healthy'] for a in ('20-39', '40-59', '60+')}
assert AGE == {'20-39': 31.0, '40-59': 22.3, '60+': 24.6}
# The 2026 ADA thresholds against BMI alone, same adults (bc_stats.py).
ADA = S['ada2026']
A_N, A_LEFT = ADA['all']['n'], ADA['all']['n_left_out']
A = {g: (ADA[g]['obesity_ada']['pct'], ADA[g]['obesity_bmi_only']['pct']) for g in GR}
assert (A_N, A_LEFT) == (5875, 54) and A == {'all': (71.4, 40.6), 'men': (73.4, 39.5), 'women': (69.4, 41.8)}
assert all(ADA[g]['difference']['ci95'][0] > 0 for g in GR)
A_CI = ADA['all']['obesity_ada']['ci95']; assert A_CI == [68.0, 74.8]
A_PART_NA, A_PART_AS = ADA['all']['parts_pts']['nonasian_25_29_9'], ADA['all']['parts_pts']['asian']
assert (A_PART_NA, A_PART_AS) == (27.9, 2.8) and round(A_PART_NA + A_PART_AS, 1) == ADA['all']['difference']['diff']
OW_WHTR = ADA['all']['bmi25_30_whtr_05']['pct']; assert OW_WHTR == 94.5
# Body fat from CDC DXA scans, ages 20-59 (research/body-fat/bf_results.json, as on /body-fat-percentage-chart/).
BF_W, BF_M = BF['f']['by_bmi']['18.5–24.9']['q'][2], BF['m']['by_bmi']['18.5–24.9']['q'][2]
assert (BF_W, BF_M) == (33.4, 22.1)
# Average weight of US men at 5'9" (the /average-weight/ table).
AVG69_M = round(AVGW['men']['height']['69']['wt']['mean'], 1); assert AVG69_M == 204.0
LB_PER_KG = 2.2046226218

# ---------------------------------------------------------------- numbers: the chart (the gate's rule)
CATS6 = [('under', 'Underweight', 'under 18.5'), ('healthy', 'Healthy weight', '18.5–24.9'),
         ('over', 'Overweight', '25–29.9'), ('ob1', 'Class 1 obesity', '30–34.9'),
         ('ob2', 'Class 2 obesity', '35–39.9'), ('ob3', 'Class 3 obesity', '40 or more')]
def ftin(h): return f'{h // 12}′{h % 12}″'
CHART = []                                                       # every inch 4'10"-6'6", lb with kg
for h in range(58, 79):
    cm = h * 2.54
    cells = [(gate_bounds('lb', h, cm, b), gate_bounds('kg', h, cm, b)) for b in range(6)]
    for b in range(5):
        assert cells[b][0][1] + 1 == cells[b + 1][0][0] and cells[b][1][1] + 1 == cells[b + 1][1][0], (h, b)
    CHART.append((h, cm, cells))
BY = {h: cells for h, cm, cells in CHART}
def hb(h, band=1): return BY[h][band]                            # ((minLb, maxLb), (minKg, maxKg))
# The rows the old page showed, unchanged (the gate passed them): 4'10", 5'9", 6'6".
assert hb(58) == ((89, 119), (41, 54)) and hb(69) == ((125, 168), (57, 76)) and hb(78) == ((160, 215), (73, 97))
assert hb(69, 2) == ((169, 202), (77, 91)) and hb(69, 3)[0] == (203, 236) and hb(69, 0)[0] == (None, 124)
METRIC = []                                                      # every 5 cm 145-200, kg with lb
for cm in range(145, 201, 5):
    h_in = cm / 2.54
    cells = [(gate_bounds('kg', h_in, cm, b), gate_bounds('lb', h_in, cm, b)) for b in range(6)]
    for b in range(5):
        assert cells[b][0][1] + 1 == cells[b + 1][0][0] and cells[b][1][1] + 1 == cells[b + 1][1][0], (cm, b)
    METRIC.append((cm, h_in, cells))
MB = {cm: cells for cm, h_in, cells in METRIC}
assert MB[170][1] == ((54, 72), (118, 158)) and MB[145][1] == ((39, 52), (86, 115))
def bmi_lb(lb, h): return round1(703.0 * lb / (h * h))
def kg_of(lb): return round(lb / LB_PER_KG, 1)
# Worked example: 5'9", 185 lb.
EX_H, EX_LB = 69, 185
EX_BMI = bmi_lb(EX_LB, EX_H); assert EX_BMI == 27.3 and category(703.0 * EX_LB / EX_H ** 2) == 2
EX_OVER = EX_LB - hb(69)[0][1]; assert EX_OVER == 17 and kg_of(EX_LB) == 83.9
# The printable table (chart_bc.py draws it): the lightest whole pound whose rounded BMI reaches each column.
PRINT_BMI = [18.5] + list(range(19, 41))
def start_lb(h, b):
    w = math.ceil((b - 0.05) * h * h / 703.0 - 1e-9)
    while round1(703.0 * w / (h * h)) < b: w += 1
    while round1(703.0 * (w - 1) / (h * h)) >= b: w -= 1
    return w
for h in range(58, 79):                                           # the category columns equal the chart's limits
    assert [start_lb(h, b) for b in (18.5, 25, 30, 35, 40)] == [hb(h, k)[0][0] for k in (1, 2, 3, 4, 5)], h
assert start_lb(69, 19) == 129 and bmi_lb(128, 69) == 18.9
# PAA "Is 20 BMI too skinny?": BMI 20 at 5'9".
LB20 = round(20 * 69 * 69 / 703); KG20 = round(20 * (69 * 0.0254) ** 2); assert (LB20, KG20) == (135, 61)

# ---------------------------------------------------------------- numbers: the chart turned around (heights per weight)
H_IN = list(range(58, 79)); H_CM = list(range(145, 201))
def heights_lb(w):
    """Whole-inch heights from 4'10" to 6'6" in each band at this weight (lb)."""
    out = [[] for _ in range(4)]
    for h in H_IN:
        out[min(category(703.0 * w / (h * h)), 3)].append(h)
    return out
def heights_kg(w):
    out = [[] for _ in range(4)]
    for cm in H_CM:
        out[min(category(w / (cm / 100.0) ** 2), 3)].append(cm)
    return out
def span(hs, unit):
    if not hs: return '—'
    for a, b in zip(hs, hs[1:]): assert b == a + 1                # one run of heights per band
    f = ftin if unit == 'in' else (lambda c: f'{c} cm')
    if unit == 'cm': return f'{hs[0]}–{hs[-1]} cm' if len(hs) > 1 else f'{hs[0]} cm'
    return f'{f(hs[0])}–{f(hs[-1])}' if len(hs) > 1 else f(hs[0])
REV_LB = [(w, heights_lb(w)) for w in range(100, 251, 10)]
REV_KG = [(w, heights_kg(w)) for w in range(40, 131, 10)]
R160 = dict(REV_LB)[160]; R70 = dict(REV_KG)[70]
assert span(R160[1], 'in') == '5′8″–6′6″' and span(R70[1], 'cm') == '168–194 cm'
# FAQ "Is 70 kg a normal weight?" and "Is 62kg heavy for a girl?" (every whole cm, not only 145-200).
def kg_band_cm(w, band):
    hs = [cm for cm in range(120, 231) if min(category(w / (cm / 100.0) ** 2), 3) == band]
    return hs[0], hs[-1]
K70 = kg_band_cm(70, 1); K70_OB = kg_band_cm(70, 3); K62 = kg_band_cm(62, 1); K62_OB = kg_band_cm(62, 3)
assert K70 == (168, 194) and K70_OB[1] == 152 and K62 == (158, 183) and K62_OB[1] == 143
def cm_ftin(cm): return f'{cm / 2.54 // 12:.0f}′{cm / 2.54 % 12:.1f}″'
def cm_ftin0(cm): i = round(cm / 2.54); return f'{i // 12}′{i % 12}″'            # to the nearest whole inch
assert [cm_ftin0(c) for c in (168, 194, 158, 183)] == ['5′6″', '6′4″', '5′2″', '6′0″']
assert cm_ftin(168) == '5′6.1″' and cm_ftin(194) == '6′4.4″' and cm_ftin(158) == '5′2.2″' and cm_ftin(183) == '6′0.0″'

# ---------------------------------------------------------------- numbers: the waist line (ADA 2026)
# ADA Standards of Care in Overweight and Obesity-2026, section 3 (recommendations 3.3a/3.3b, Table 3.1; press release
# 2026-06-29; registry ada-2026-obesity-standards): non-Asian background, obesity at BMI >= 30, or BMI >= 25 with
# waist-to-height ratio >= 0.5 or waist >= 88 cm (women) / 102 cm (men); Asian background, BMI >= 27.5, or BMI >= 23
# with ratio >= 0.5 or waist >= 80 cm (women) / 90 cm (men). Table 3.1 gives 88 cm as 35 in and 80 cm as 31.5 in.
# Nonpregnant adults. The line that counts first is the lower of half the height and the sex-specific waist.
def waist_line(h, cut_cm):
    half = h * 2.54 / 2
    return (half, 'half') if half < cut_cm else (cut_cm, 'cut')
WAIST_ROWS = [(h, waist_line(h, 102), waist_line(h, 88)) for h in range(58, 79, 2)]
assert all(m[1] == 'half' for _, m, _ in WAIST_ROWS)                  # men: half the height at every height shown
assert [w[1] for _, _, w in WAIST_ROWS] == ['half'] * 6 + ['cut'] * 5  # women: 88 cm from 5'10" (70 in)
assert waist_line(69, 88)[1] == 'half' and waist_line(70, 88)[1] == 'cut'
assert waist_line(62, 80)[1] == 'half' and waist_line(63, 80)[1] == 'cut'      # Asian women: 80 cm from 5'3"
assert waist_line(70, 90)[1] == 'half' and waist_line(71, 90)[1] == 'cut'      # Asian men: 90 cm from 5'11"
def wl(v): return f'{v / 2.54:.1f} in ({v:.1f} cm)'
assert wl(69 * 2.54 / 2) == '34.5 in (87.6 cm)'

# ---------------------------------------------------------------- numbers: sources verified in chat
# NIH printable BMI table (NIH Publication No. 22-HL-8190, September 2022; PDF read 2026-10-16): one column per whole
# BMI from 19 to 54, heights 4'10" to 6'4"; the 69-inch row reads 128 lb (BMI 19), 162 (24), 169 (25) and 203 (30).
NIH_COLS, NIH_69 = (19, 54), {19: 128, 24: 162, 25: 169, 30: 203}
assert NIH_69[25] == hb(69, 2)[0][0] and NIH_69[30] == hb(69, 3)[0][0]
# CDC Adult BMI Categories: last reviewed March 19, 2024; "regardless of age, sex, or race".
# CDC About BMI (page dated 2025-12-16): "BMI does not distinguish between fat, muscle, and bone mass".
# Lancet Commission on Clinical Obesity (Rubino et al., Lancet Diabetes Endocrinol 2025;13:221-62, epub 2025-01-14):
# excess adiposity confirmed by a direct body-fat measurement or at least one body-size measure besides BMI (waist
# circumference, waist-to-hip or waist-to-height ratio); endorsed by 76 organisations.

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'cdc_preg': 'https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
    'nih_tbl': 'https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_tbl.pdf',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'hes111': 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm',
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'ada': 'https://doi.org/10.2337/doci26-0003',
    'ada_pr': 'https://diabetes.org/newsroom/press-releases/new-standards-care-overweight-and-obesity-section-screening-diagnosis-0',
    'lancet': 'https://pubmed.ncbi.nlm.nih.gov/39824205/',
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

# The site's base category colours (DESIGN.md category lock; the homepage's 100-square figure uses the same five).
BASE = {'under': '#3b82f6', 'healthy': '#22c55e', 'over': '#f59e0b', 'obese': '#ef4444', 'severe': '#991b1b'}
TINTS = {'under': '#dbeafe', 'healthy': '#d1fae5', 'over': '#fde68a', 'obese': '#fecaca', 'severe': '#fca5a5'}
LEG5 = [('under', 'Underweight'), ('healthy', 'Healthy weight'), ('over', 'Overweight'), ('obese', 'Obesity, 30–39.9'),
        ('severe', 'Class 3 obesity')]
BAND_EDGES = [(None, 18.5, 'under'), (18.5, 25, 'healthy'), (25, 30, 'over'), (30, 40, 'obese'), (40, None, 'severe')]

def legend(svg, x0, y0, items, colors, col_w=150, stroke=None):
    out = []
    for i, (k, lab) in enumerate(items):
        x = x0 + (i % 2) * col_w; y = y0 + (i // 2) * 20
        extra = f' stroke="{stroke}" stroke-width="0.75"' if stroke else ''
        out.append(rect(svg, x, y - 10, 12, 12, colors[k], rid='swatch', extra=extra))
        out.append(text(svg, x + 18, y, lab, 12, anchor='start', fill='#1f2937'))
    return ''.join(out)

def band_paths(hx, wy, hlo, hhi, wlo, whi, colors, svg, tip=True):
    """Filled regions between the BMI lines over heights hlo..hhi (in), clipped to weights wlo..whi (lb)."""
    steps = [hlo + i * 0.25 for i in range(int(round((hhi - hlo) / 0.25)) + 1)]
    def curve(b): b -= 0.05; return [(hx(h), wy(min(max(b * h * h / 703.0, wlo), whi))) for h in steps]   # rounds to b
    out = []
    for lo, hi, k in BAND_EDGES:
        lower = curve(lo) if lo else [(hx(h), wy(wlo)) for h in steps]
        upper = curve(hi) if hi else [(hx(h), wy(whi)) for h in steps]
        pts = lower + upper[::-1]
        d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
        rng = (f'BMI under {hi}' if lo is None else f'BMI {lo} or more' if hi is None else f'BMI {lo} to {hi - 0.1:.1f}')
        name = dict(LEG5)[k].split(',')[0]
        t = f'<title>{esc(name)}: {rng}</title>' if tip else ''
        out.append(f'<path d="{d}" fill="{colors[k]}">{t}</path>')
    return ''.join(out)

# Hero: the chart in one picture. Height across, weight up, one band per category; the dot is 5'9" and 185 lb.
VBW['hero'] = W1 = 320
PX0, PX1, PY0, PY1 = 46, 284, 50, 316
HLO, HHI, WLO, WHI = 58, 78, 80, 360
def hx(h): return PX0 + (h - HLO) * (PX1 - PX0) / (HHI - HLO)
def wy(lb): return PY1 - (lb - WLO) * (PY1 - PY0) / (WHI - WLO)
hero = [text('hero', W1 / 2, 17, 'BMI chart for adults', 14, weight=700),
        text('hero', W1 / 2, 35, f'Dot: 5′9″ and {EX_LB} lb, BMI {EX_BMI} (overweight)', 12, fill='#374151')]
RECTS.append(('hero', PX0, PY0, PX1, PY1, 'plot'))
hero.append(band_paths(hx, wy, HLO, HHI, WLO, WHI, BASE, 'hero'))
for b in (34.95,):                                                # class 1/2 line inside the obesity band (rounds to 35.0)
    pts = ' '.join(f'{hx(h):.1f},{wy(b * h * h / 703.0):.1f}' for h in [HLO + i * 0.25 for i in range(81)])
    hero.append(f'<polyline points="{pts}" fill="none" stroke="#ffffff" stroke-width="1" stroke-opacity="0.8"/>')
for b in (18.5, 25, 30, 35, 40):                                  # each BMI line named at the right edge
    hero.append(text('hero', PX1 + 4, wy(b * HHI * HHI / 703.0) + 4, f'{b:g}', 12, anchor='start', fill='#374151'))
hero.append(text('hero', PX1 + 4, PY0 - 2, 'BMI', 12, anchor='start', weight=600, fill='#374151'))
hero.append(f'<line x1="{PX0}" y1="{PY1}" x2="{PX1}" y2="{PY1}" stroke="#9ca3af" stroke-width="1"/>')
for h in range(58, 79, 4):
    hero.append(f'<line x1="{hx(h):.1f}" y1="{PY1}" x2="{hx(h):.1f}" y2="{PY1 + 4}" stroke="#9ca3af" stroke-width="1"/>')
    hero.append(text('hero', hx(h), PY1 + 17, ftin(h), 12, fill='#4b5563'))
hero.append(text('hero', (PX0 + PX1) / 2, PY1 + 34, 'Height', 12, weight=600, fill='#374151'))
for lb in range(120, 361, 40):                                    # no 80 label: it would meet 4'10" in the corner
    hero.append(text('hero', PX0 - 5, wy(lb) + 4, f'{lb} lb' if lb == 360 else str(lb), 12, anchor='end', fill='#4b5563'))
ex_x, ex_y = hx(EX_H), wy(EX_LB)
hero.append(f'<circle cx="{ex_x:.1f}" cy="{ex_y:.1f}" r="5" fill="#111827" stroke="#ffffff" stroke-width="2">'
            f'<title>5′9″ and {EX_LB} lb: BMI {EX_BMI}, overweight</title></circle>')
hero.append(legend('hero', 18, PY1 + 62, LEG5, BASE))
H1V = PY1 + 62 + 2 * 20 + 18
svg_hero = (f'<svg viewBox="0 0 {W1} {H1V}" width="{W1}" height="{H1V}" role="img" aria-labelledby="fig-hero-t fig-hero-d" font-family="inherit">'
            '<title id="fig-hero-t">BMI chart for adults: the healthy weight rises with height</title>'
            '<desc id="fig-hero-d">Height from 4 feet 10 inches to 6 feet 6 inches across, weight from 80 to 360 pounds up. '
            'Bands for underweight, healthy weight, overweight, obesity and class 3 obesity, separated by the lines for BMI '
            f'18.5, 25, 30, 35 and 40. The healthy band runs from {hb(58)[0][0]} to {hb(58)[0][1]} pounds at 4 feet 10 inches '
            f'and from {hb(78)[0][0]} to {hb(78)[0][1]} pounds at 6 feet 6 inches. A dot marks 5 feet 9 inches and {EX_LB} '
            f'pounds, a BMI of {EX_BMI}, in the overweight band. Cut-offs: CDC.</desc>' + ''.join(hero) + '</svg>')

# Wedge figure: obesity by BMI alone and by the 2026 ADA thresholds, all adults, men, women (same adults per group).
VBW['ada'] = W2 = 320
AX0, AXW = 10, 236
COL2 = {'bmi': '#fca5a5', 'ada': '#b91c1c'}
ada = [text('ada', W2 / 2, 17, 'Two definitions of obesity', 14, weight=700),
       text('ada', W2 / 2, 35, 'US adults 20 and over, 2021–2023 (%)', 12, fill='#4b5563'),
       legend('ada', 18, 60, [('bmi', 'BMI 30 or more'), ('ada', '2026 ADA rule')], COL2, col_w=140, stroke='#7f1d1d')]
y = 92
for g, lab in (('all', 'All adults'), ('men', 'Men'), ('women', 'Women')):
    ada.append(text('ada', AX0, y, lab, 12, anchor='start', weight=600, fill='#1f2937'))
    y += 8
    for k, v in (('bmi', A[g][1]), ('ada', A[g][0])):
        w = v / 100 * AXW
        name = 'BMI 30 or more' if k == 'bmi' else 'the 2026 ADA rule'
        ada.append(bar('ada', AX0, y, w, 15, COL2[k], rid='bar', tip=f'{lab}, {name}: {v:.1f}%'))
        ada.append(text('ada', AX0 + w + 5, y + 12, f'{v:.1f}%', 12, anchor='start', weight=600, fill='#111827'))
        y += 19
    y += 16
ada.append(text('ada', W2 / 2, y - 2, 'CDC NHANES 2021–2023; our calculation', 12, fill='#4b5563'))
H2V = y + 6
svg_ada = (f'<svg viewBox="0 0 {W2} {H2V}" width="{W2}" height="{H2V}" role="img" aria-labelledby="fig-ada-t fig-ada-d" font-family="inherit">'
           '<title id="fig-ada-t">Share of US adults with obesity by BMI alone and by the 2026 ADA thresholds, 2021 to 2023</title>'
           '<desc id="fig-ada-d">Pairs of bars. '
           + '; '.join(f'{lab}: BMI 30 or more {A[g][1]}%, 2026 ADA thresholds {A[g][0]}%'
                       for g, lab in (('all', 'all adults'), ('men', 'men'), ('women', 'women')))
           + '. Our calculation from CDC NHANES measured BMI, waist and height, August 2021 to August 2023.</desc>'
           + ''.join(ada) + '</svg>')

# Data figure: 600 US adults on the chart (bc_stats.py draws them with probability proportional to their exam weight).
VBW['dots'] = W3 = 320
DX0, DX1, DY0, DY1 = 46, 306, 50, 300
DHLO, DHHI, DWLO, DWHI = 54, 78, 60, 440
def dhx(h): return DX0 + (h - DHLO) * (DX1 - DX0) / (DHHI - DHLO)
def dwy(lb): return DY1 - (lb - DWLO) * (DY1 - DY0) / (DWHI - DWLO)
PTS = S['dots']['points']
assert len(PTS) == 600 and all(DHLO <= h <= DHHI and DWLO <= w <= DWHI for h, w, _ in PTS)
dots = [text('dots', W3 / 2, 17, '600 US adults on the BMI chart', 14, weight=700),
        text('dots', W3 / 2, 35, 'Each dot is one adult measured by CDC, 2021–2023', 12, fill='#4b5563')]
RECTS.append(('dots', DX0, DY0, DX1, DY1, 'plot'))
dots.append(band_paths(dhx, dwy, DHLO, DHHI, DWLO, DWHI, TINTS, 'dots', tip=False))
dots.append('<g fill="#111827" fill-opacity="0.62">' + ''.join(
    f'<circle cx="{dhx(h):.1f}" cy="{dwy(w):.1f}" r="1.7"/>' for h, w, _ in PTS) + '</g>')
dots.append(f'<line x1="{DX0}" y1="{DY1}" x2="{DX1}" y2="{DY1}" stroke="#9ca3af" stroke-width="1"/>')
for h in range(54, 79, 4):
    dots.append(f'<line x1="{dhx(h):.1f}" y1="{DY1}" x2="{dhx(h):.1f}" y2="{DY1 + 4}" stroke="#9ca3af" stroke-width="1"/>')
    dots.append(text('dots', dhx(h), DY1 + 17, ftin(h), 12, fill='#4b5563'))
for lb in (100, 200, 300, 400):
    dots.append(text('dots', DX0 - 5, dwy(lb) + 4, f'{lb} lb' if lb == 400 else str(lb), 12, anchor='end', fill='#4b5563'))
dots.append(legend('dots', 18, DY1 + 44, LEG5, TINTS, stroke='#9ca3af'))
dots.append(text('dots', W3 / 2, DY1 + 44 + 3 * 20 + 6, 'CDC NHANES 2021–2023; our sample of 600', 12, fill='#4b5563'))
H3V = DY1 + 44 + 3 * 20 + 14
n_band = [0] * 5
for h, w, _ in PTS:
    b = round1(703.0 * w / (h * h)); n_band[0 if b < 18.5 else 1 if b < 25 else 2 if b < 30 else 3 if b < 40 else 4] += 1
svg_dots = (f'<svg viewBox="0 0 {W3} {H3V}" width="{W3}" height="{H3V}" role="img" aria-labelledby="fig-dots-t fig-dots-d" font-family="inherit">'
            '<title id="fig-dots-t">600 US adults on the BMI chart, 2021 to 2023</title>'
            '<desc id="fig-dots-d">A scatter of 600 adults by height and weight over the BMI category bands. '
            f'{n_band[0]} dots fall in the underweight band, {n_band[1]} in the healthy band, {n_band[2]} in the overweight '
            f'band, {n_band[3]} in obesity and {n_band[4]} in class 3 obesity. Adults drawn from CDC NHANES, August 2021 to '
            'August 2023, with a chance in proportion to the number of US adults each one stands for.</desc>'
            + ''.join(dots) + '</svg>')

# Collision check on the estimated boxes (the rendered check runs in bc_test_playwright.py): no text over text, no text
# over a shape unless it is the label that shape holds, nothing outside the viewBox.
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
# People also ask in the owner's US/English pastes of 2026-10-16 ("bmi chart", "height and weight chart", "weight
# charts"; Google marked them personalised): "bmi chart" first, then "weight charts" ("height and weight chart" showed
# none). Then the ledger's "at 5 9 how much should i weigh" (1,300/mo) and the old page's men-and-women question.
B69 = hb(69)
FAQ = [
    ('What is a healthy BMI by age?',
     f'For adults, the same at every age: <strong>18.5 to 24.9</strong> from age 20 on ({ext(U["cdc_cat"], "CDC")}). Under '
     '20, BMI is read as a percentile for age and sex instead (<a href="/kids-bmi-calculator/">BMI calculator for children '
     f'and teens</a>). Among US adults, {AGE["20-39"]}% of those aged 20 to 39 have a BMI in the range, {AGE["40-59"]}% at '
     f'40 to 59 and {AGE["60+"]}% at 60 and over (our calculation from CDC measurements, 2021–2023).'),
    ('What is the new BMI chart for 2026?',
     'There isn’t a new chart. CDC’s adult categories are unchanged: a healthy weight is a BMI of 18.5 to 24.9, and CDC '
     f'last reviewed its page on them in March 2024 ({ext(U["cdc_cat"], "CDC")}). What changed in June 2026 is the American '
     'Diabetes Association’s definition of obesity: at a BMI of 25 to 29.9, a waist of at least half the height, or 88 cm '
     f'or more in women and 102 cm or more in men, now counts as obesity, with lower lines for adults of Asian background ({ADA_CITE}). '
     f'{A["all"][0]}% of US adults meet the new thresholds, against {A["all"][1]}% of the same adults by BMI alone (our '
     'calculation).'),
    ('Is 20 BMI too skinny?',
     'No. A BMI of 20 is inside CDC’s healthy range of 18.5 to 24.9; underweight starts below 18.5 '
     f'({ext(U["cdc_cat"], "CDC")}). At 5′9″, a BMI of 20 is about {LB20} lb ({KG20} kg). Only {U20}% of US adults have a '
     'BMI under 20 (our calculation from CDC measurements, 2021–2023).'),
    ('At what BMI are you no longer obese?',
     f'Below 30. CDC’s obesity category starts at a BMI of 30.0, so 29.9 is overweight ({ext(U["cdc_cat"], "CDC")}). At '
     f'5′9″ that means {hb(69, 2)[0][1]} lb or less; obesity starts at {hb(69, 3)[0][0]} lb (a BMI of 30.0, rounded to one '
     'decimal). Under the 2026 American Diabetes Association standards a lower BMI can still count: from 25 when the waist '
     'is at least half the height, or 88 cm or more in women and 102 cm or more in men. For adults of Asian background it '
     'counts from 23 with a waist at least half the height, or 80 cm or more in women and 90 cm or more in men, and from '
     f'27.5 whatever the waist ({ADA_CITE}).'),
    ('What is the correct weight for my age and height?',
     'For adults, the healthy weight depends on height, not age: it is the range that gives a BMI of 18.5 to 24.9 at your '
     f'height, at every age from 20 ({ext(U["cdc_cat"], "CDC")}). At 5′9″ that is {B69[0][0]} to {B69[0][1]} lb '
     f'({B69[1][0]} to {B69[1][1]} kg); the chart on this page has every height from 4′10″ to 6′6″. What US adults '
     'actually weigh at each height and age is on <a href="/average-weight/">average weight by height and age</a>. Under 20, '
     'use the <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a>.'),
    ('What is an ideal weight chart?',
     'A chart that gives one “ideal” weight for each height, worked out from a formula; the '
     '<a href="/ideal-weight/">ideal weight calculator</a> shows four of them (Devine, Robinson, Miller and Hamwi). CDC’s '
     f'guidance gives a range instead: the weights with a BMI of 18.5 to 24.9 at your height ({ext(U["cdc_cat"], "CDC")}). '
     f'At 5′9″ that range is {B69[0][0]} to {B69[0][1]} lb.'),
    ('Is 70 kg a normal weight?',
     f'It depends on your height. For adults, 70 kg is a healthy weight (BMI 18.5 to 24.9) from {K70[0]} to {K70[1]} cm '
     f'tall, about {cm_ftin0(K70[0])} to {cm_ftin0(K70[1])}. Below {K70[0]} cm it is overweight, and at '
     f'{K70_OB[1]} cm or less it is obesity ({ext(U["cdc_cat"], "CDC")} categories). The <a href="#by-weight">heights for '
     'each weight</a> table runs from 40 to 130 kg.'),
    ('Is 62kg heavy for a girl?',
     f'For women 20 and older, 62 kg is a healthy weight from {K62[0]} to {K62[1]} cm tall, about '
     f'{cm_ftin0(K62[0])} to {cm_ftin0(K62[1])}; below {K62[0]} cm it is overweight, and at {K62_OB[1]} cm or less it is '
     f'obesity ({ext(U["cdc_cat"], "CDC")} categories). For girls under 20, BMI is read as a percentile for age instead: the '
     '<a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it out.'),
    ('How much should I weigh at 5′9″?',
     f'A healthy weight at 5′9″ (175.3 cm) is <strong>{B69[0][0]} to {B69[0][1]} lb ({B69[1][0]} to {B69[1][1]} kg)</strong>, '
     f'a BMI of 18.5 to 24.9 ({ext(U["cdc_cat"], "CDC")}). Under {B69[0][0]} lb is underweight, {hb(69, 2)[0][0]} to '
     f'{hb(69, 2)[0][1]} lb is overweight and {hb(69, 3)[0][0]} lb or more is obesity. The average US man of that height '
     f'weighs about {round(AVG69_M)} lb (our calculation from CDC measurements, 2021–2023; <a href="/average-weight/">average weight by '
     'height</a>).'),
    ('Is the BMI chart different for men and women?',
     'No. CDC uses the same adult categories “regardless of age, sex, or race” '
     f'({ext(U["cdc_cat"], "CDC")}), so one chart serves both. The body behind the number differs: at a healthy BMI, the '
     f'median US woman aged 20 to 59 had {BF_W}% body fat and the median man {BF_M}% (our analysis of CDC body scans, '
     '2011–2018). The <a href="/blog/bmi-chart-women/">BMI chart for women</a> and <a href="/blog/bmi-chart-men/">BMI '
     'chart for men</a> show the chart over each sex’s usual heights.'),
]
assert K70[0] == 168
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
head = (
    '<div class="page-head"><h1>BMI Chart for Adults: Height and Weight Chart</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">What should you weigh for your height? Which BMI does your weight give, without a calculator? '
    'And is there a new chart for 2026?</p>'
    f'<p class="intro-text">Only {p("all", "healthy")}% of US adults have a BMI in CDC’s healthy range of 18.5 to 24.9 (our '
    'calculation from CDC measurements, 2021–2023). Since June 2026, the American Diabetes Association also counts the '
    f'waist, and {A["all"][0]}% of US adults meet its obesity thresholds, against {A["all"][1]}% of the same adults by BMI '
    'alone (our calculation).</p>'
    '<p class="intro-text">Below: <a href="#chart">the chart for every height</a> from 4′10″ to 6′6″ in pounds and '
    'kilograms, a printable BMI table, the heights at which a weight is healthy, and the 2026 waist rule.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>A BMI chart gives the weight range for each BMI category at your height.</strong> CDC’s '
    'healthy range is a BMI of 18.5 to 24.9 for every adult, women and men, at any age. At 5′9″ that is '
    f'{B69[0][0]} to {B69[0][1]} lb ({B69[1][0]} to {B69[1][1]} kg); {hb(69, 2)[0][0]} to {hb(69, 2)[0][1]} lb is '
    f'overweight and {hb(69, 3)[0][0]} lb or more is obesity.</p><ul>'
    f'<li><strong>About 1 in 4 US adults has a healthy BMI ({p("all", "healthy")}%)</strong>; {p("all", "overweight")}% are '
    f'overweight and {p("all", "obesity")}% have obesity (our calculation from CDC measurements, 2021–2023, matching NCHS’s '
    'published crude rates).</li>'
    '<li><strong>The 2026 waist rule:</strong> at a BMI of 25 to 29.9, the American Diabetes Association counts a waist of '
    f'at least half your height toward obesity, and {OW_WHTR}% of US adults in that range have one (our calculation).</li>'
    '<li>Under 20, BMI is read as a percentile for age and sex, not on this chart.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This page is for information only. BMI is a '
    'screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>Every height and weight falls in one band. The lines are BMI '
            '18.5, 25, 30, 35 and 40, and the healthy band rises with height.</figcaption></figure>')

CHIPS = (('chart', 'Chart'), ('reading', 'Reading it'), ('printable', 'Printable'), ('by-weight', 'By weight'),
         ('waist', '2026 waist rule'), ('us-adults', 'US adults'), ('age-sex', 'Age and sex'), ('faq', 'FAQ'),
         ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

def cell(r1_, r2_, u1, u2):
    (a0, a1), (b0, b1) = r1_, r2_
    if a0 is None: return f'&le; {a1} {u1} <span class="cell-kg">({b1} {u2})</span>'
    if a1 is None: return f'&ge; {a0} {u1} <span class="cell-kg">({b0} {u2})</span>'
    return f'{a0}&ndash;{a1} {u1} <span class="cell-kg">({b0}&ndash;{b1} {u2})</span>'
def thead(first):
    return (f'<thead><tr><th scope="col">{first}</th>'
            + ''.join(f'<th scope="col">{name}<span class="th-sub">BMI <span class="nw">{rng}</span></span></th>'
                      for _, name, rng in CATS6) + '</tr></thead>')
chart_rows = ''.join(
    f'<tr id="h-{h // 12}-{h % 12}"><th scope="row">{ftin(h)} <span class="cell-cm">({cm:.1f} cm)</span></th>'
    + ''.join(f'<td class="c-{k}">{cell(cells[b][0], cells[b][1], "lb", "kg")}</td>' for b, (k, _, _) in enumerate(CATS6))
    + '</tr>' for h, cm, cells in CHART)
metric_rows = ''.join(
    f'<tr id="h-{cm}cm"><th scope="row">{cm} cm <span class="cell-cm">({cm_ftin(cm)})</span></th>'
    + ''.join(f'<td class="c-{k}">{cell(cells[b][0], cells[b][1], "kg", "lb")}</td>' for b, (k, _, _) in enumerate(CATS6))
    + '</tr>' for cm, h_in, cells in METRIC)
assert cm_ftin(170) == '5′6.9″' and cm_ftin(145) == '4′9.1″'
sec_chart = (
    '<section id="chart" class="content-section flow"><h2>BMI chart by height and weight</h2>'
    '<p>Each cell is the range of whole pounds, with kilograms below, that gives a BMI in that category at that height. '
    f'The healthy weight is <strong>{hb(58)[0][0]} to {hb(58)[0][1]} lb at 4′10″</strong> and '
    f'<strong>{hb(78)[0][0]} to {hb(78)[0][1]} lb at 6′6″</strong>.</p>'
    f'<div class="table-responsive"><table class="weight-chart"><caption>BMI chart in pounds, 4′10″ to 6′6″</caption>{thead("Height")}'
    f'<tbody>{chart_rows}</tbody></table></div>'
    '<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, falls in each category at the '
    'height shown. Each unit is worked out on its own, so the kilograms are not conversions of the pounds. Cut-offs: '
    f'{ext(U["cdc_cat"], "CDC Adult BMI Categories")}. Kilogram limits are for the exact height in inches; the centimeters '
    'shown are rounded to one decimal. Each row has its own link, for example #h-5-9 for 5′9″.</p>'
    '<h3 id="chart-kg">BMI chart in kilograms</h3>'
    '<p>The same chart for heights in centimeters, every 5 cm from 145 to 200 cm, with pounds below each range.</p>'
    f'<div class="table-responsive"><table class="weight-chart"><caption>BMI chart in kilograms, 145 to 200 cm</caption>{thead("Height")}'
    f'<tbody>{metric_rows}</tbody></table></div>'
    '<p class="source-note">Whole kilograms and pounds, each worked out on its own at the height shown. Feet and inches are '
    'rounded to one decimal of an inch. Each row has its own link, for example #h-170cm.</p>'
    '</section>')

sec_read = (
    '<section id="reading" class="content-section flow"><h2>How to read a BMI chart</h2><ol>'
    '<li>Find your height in the left column. Centimeters are under each height.</li>'
    '<li>Read across to the cell that holds your weight. Its column is your BMI category.</li>'
    '<li>For the BMI number, use the <a href="#printable">printable BMI table</a> or the <a href="/">BMI calculator</a>.</li></ol>'
    f'<p><strong>Example.</strong> Say you’re 5′9″ and weigh {EX_LB} lb ({kg_of(EX_LB)} kg). The overweight cell in that row '
    f'runs from {hb(69, 2)[0][0]} to {hb(69, 2)[0][1]} lb, so {EX_LB} lb is overweight: a BMI of {EX_BMI} '
    f'({EX_LB} × 703 ÷ 69², rounded to one decimal; {ext(U["cdc_formula"], "CDC formula")}). The healthy range at 5′9″ is '
    f'{B69[0][0]} to {B69[0][1]} lb, so {EX_LB} lb is {EX_OVER} lb above it.</p>'
    '<h3>Why other charts give different numbers</h3>'
    f'<p>NIH’s {ext(U["nih_tbl"], "printable BMI table")} has one column for each whole BMI from {NIH_COLS[0]} to '
    f'{NIH_COLS[1]}. At 5′9″ its BMI 19 column reads {NIH_69[19]} lb and its BMI 24 column {NIH_69[24]} lb, '
    f'so a chart read from those two columns gives <strong>{NIH_69[19]} to {NIH_69[24]} lb</strong>. CDC’s healthy range '
    f'runs from 18.5 to 24.9, and at 5′9″ that is <strong>{B69[0][0]} to {B69[0][1]} lb</strong>. Where NIH’s columns '
    f'start a category, at BMI 25 and 30, its weights match this chart: {NIH_69[25]} and {NIH_69[30]} lb at 5′9″.</p>'
    '<p>“Ideal weight” charts differ for another reason: they give one weight per height from a formula, not a range. The '
    '<a href="/ideal-weight/">ideal weight calculator</a> shows four of them.</p>'
    '</section>')

CHART_IMG = '/assets/images/charts/bmi-chart.png'
CHART_W, CHART_H = 1640, 1854                                   # written by chart_bc.py
_png = os.path.join(ROOT, CHART_IMG.lstrip('/'))
if os.path.exists(_png):
    from PIL import Image
    assert Image.open(_png).size == (CHART_W, CHART_H), Image.open(_png).size
sec_print = (
    '<section id="printable" class="content-section flow"><h2>Printable BMI table</h2>'
    '<p>The table gives the BMI for every height from 4′10″ to 6′6″. Find your height and move across to the heaviest weight '
    'that is not above yours: your BMI is the number at the top of that column or a little more. A weight below the 18.5 '
    'column is underweight.</p>'
    f'<figure class="figure figure--wide"><a href="{CHART_IMG}"><img src="{CHART_IMG}" width="{CHART_W}" height="{CHART_H}" '
    'loading="lazy" decoding="async" alt="Printable BMI chart for adults: the weight in pounds at which each BMI from 18.5 to '
    '40 begins, for every height from 4 feet 10 inches to 6 feet 6 inches, colored by CDC category"></a><figcaption>'
    'Printable BMI table for adults: the lightest whole pound for each BMI from 18.5 to 40, at every height from 4′10″ to '
    '6′6″. Open the image to print or save it.</figcaption></figure>'
    '<p>Each cell is the lightest whole pound whose BMI, rounded to one decimal, reaches the number at the top of the '
    'column, so the 18.5, 25, 30, 35 and 40 columns match the category limits in the chart above. NIH’s table lists one '
    f'weight for each whole BMI and can differ by a pound: at 5′9″ and BMI 19, NIH gives {NIH_69[19]} lb and this table '
    f'{start_lb(69, 19)} lb, because {NIH_69[19]} lb is a BMI of {bmi_lb(NIH_69[19], 69)}.</p>'
    '</section>')

def rev_rows(rows, unit):
    out = []
    for w, bands in rows:
        rid = f'w-{w}-{"lb" if unit == "in" else "kg"}'
        wlab = f'{w} lb <span class="cell-cm">({kg_of(w)} kg)</span>' if unit == 'in' else f'{w} kg <span class="cell-cm">({w * LB_PER_KG:.1f} lb)</span>'
        out.append(f'<tr id="{rid}"><th scope="row">{wlab}</th>'
                   + ''.join(f'<td class="c-{k}">{span(bands[i], unit)}</td>'
                             for i, k in enumerate(('under', 'healthy', 'over', 'ob1'))) + '</tr>')
    return ''.join(out)
REV_HEAD = ('<thead><tr><th scope="col">Weight</th>' + ''.join(
    f'<th scope="col">{n}<span class="th-sub">BMI <span class="nw">{r}</span></span></th>' for n, r in (
        ('Underweight', 'under 18.5'), ('Healthy weight', '18.5–24.9'), ('Overweight', '25–29.9'), ('Obesity', '30 or more')))
    + '</tr></thead>')
sec_rev = (
    '<section id="by-weight" class="content-section flow"><h2>Start from your weight: heights for each weight</h2>'
    '<p>These tables turn the chart around: for each weight, they give the heights at which it falls in each category. At '
    f'<strong>160 lb</strong>, a BMI of 18.5 to 24.9 means a height of <strong>{span(R160[1], "in")}</strong>; at '
    f'<strong>70 kg</strong>, <strong>{span(R70[1], "cm")}</strong>.</p>'
    f'<div class="table-responsive"><table class="weight-chart"><caption>Heights for each weight, 100 to 250 lb</caption>{REV_HEAD}'
    f'<tbody>{rev_rows(REV_LB, "in")}</tbody></table></div>'
    f'<div class="table-responsive"><table class="weight-chart"><caption>Heights for each weight, 40 to 130 kg</caption>{REV_HEAD}'
    f'<tbody>{rev_rows(REV_KG, "cm")}</tbody></table></div>'
    '<p class="source-note">Whole-inch heights from 4′10″ to 6′6″ and whole-centimeter heights from 145 to 200 cm, the '
    'span of the charts above; a dash means no height in that span. BMI rounded to one decimal, CDC categories. Each row '
    'has its own link, for example #w-160-lb or #w-70-kg.</p>'
    '</section>')

sec_waist = (
    '<section id="waist" class="content-section flow"><h2>The 2026 waist rule</h2>'
    '<p>A BMI chart can’t show where fat sits. In June 2026 the American Diabetes Association published a new chapter of '
    'its obesity standards that adds the waist to the diagnosis of obesity in adults who aren’t pregnant '
    f'({ext(U["ada_pr"], "ADA")}). CDC’s categories haven’t changed.</p><ul>'
    '<li><strong>BMI 30 or more:</strong> obesity, as on the chart.</li>'
    '<li><strong>BMI 25 to 29.9:</strong> obesity when the waist is at least half the height, or 88 cm (about 35 in) or '
    'more in women and 102 cm (about 40 in) or more in men; otherwise overweight.</li>'
    '<li><strong>Adults of Asian background:</strong> obesity from a BMI of 27.5, or from 23 with a waist at least half '
    f'the height, or 80 cm (31.5 in) or more in women and 90 cm (35.4 in) or more in men ({ADA_CITE}).</li></ul>'
    f'<p>Either waist test is enough, so the lower line decides. For most adults that is half the height: '
    f'{wl(60 * 2.54 / 2)} at 5′0″, {wl(69 * 2.54 / 2)} at 5′9″ and {wl(72 * 2.54 / 2)} at 6′0″. For women 5′10″ and '
    'taller it is 88 cm. For adults of Asian background it is 80 cm for women 5′3″ and taller, and 90 cm for men 5′11″ and '
    'taller.</p>'
    f'<div class="stat-callout"><div class="stat-callout-value">{A["all"][0]}%</div><div class="stat-callout-text">of US '
    f'adults meet the 2026 ADA obesity thresholds, against {A["all"][1]}% by BMI alone, in the same {A_N:,} adults.</div>'
    '<div class="stat-callout-source">Source: our calculation from CDC NHANES 2021–2023 measured BMI, waist and height; 95% '
    f'confidence interval {A_CI[0]}% to {A_CI[1]}%</div></div>'
    f'<figure class="figure">{svg_ada}<figcaption>Share of US adults with obesity by BMI alone and by the 2026 ADA '
    'thresholds, each pair in the same adults.</figcaption></figure>'
    f'<p class="source-note">The {A_LEFT} adults left out of this comparison, whose class depends on a waist that wasn’t '
    f'measured, all have a BMI under 30. That is why BMI alone gives {A["all"][1]}% here and {p("all", "obesity")}% across all '
    f'{C["all"]["n"]:,} adults.</p>'
    f'<p>Most of the gap is adults with a BMI of 25 to 29.9: <strong>{OW_WHTR}% of them have a waist at least half their '
    f'height</strong>. Non-Asian adults in that range account for {A_PART_NA} percentage points of the difference, and adults '
    f'of Asian background with a BMI of 23 to 29.9 for {A_PART_AS}. By sex: {A["men"][0]}% of men against {A["men"][1]}%, '
    f'and {A["women"][0]}% of women against {A["women"][1]}% (the <a href="/blog/bmi-chart-women/#waist">BMI chart for '
    'women</a> has the detail).</p>'
    '<p>In January 2025 a Lancet commission, endorsed by 76 organizations, also proposed confirming excess body fat with a '
    'waist measure or a direct body-fat measurement in addition to BMI '
    f'({ext(U["lancet"], "Rubino et al., 2025")}). The <a href="/blog/waist-to-height-ratio/">waist-to-height ratio '
    'guide</a> shows how to measure your waist.</p>'
    '</section>')

cat_rows_def = (('underweight', 'underweight', 'Underweight', 'under 18.5'), ('healthy', 'normal', 'Healthy weight', '18.5–24.9'),
                ('overweight', 'overweight', 'Overweight', '25–29.9'), ('class_1', 'obese', 'Class 1 obesity', '30–34.9'),
                ('class_2', 'obese', 'Class 2 obesity', '35–39.9'), ('class_3', 'obese-severe', 'Class 3 obesity', '40 or more'))
us_rows = ''.join(
    f'<tr><th scope="row"><span class="cat-dot {dot}" aria-hidden="true"></span>{name}<span class="th-sub">BMI {rng}</span></th>'
    + ''.join(f'<td class="num">{p(g, k)}%</td>' for g in GR) + '</tr>'
    for k, dot, name, rng in cat_rows_def)
us_rows += ('<tr><th scope="row">Adults measured</th>' + ''.join(f'<td class="num">{C[g]["n"]:,}</td>' for g in GR)
            + '</tr>')
sec_us = (
    '<section id="us-adults" class="content-section flow"><h2>Where US adults fall on the chart</h2>'
    '<p>CDC measures the height and weight of a national sample of adults. In 2021–2023 most landed above the healthy '
    f'band: {p("all", "overweight")}% overweight and {p("all", "obesity")}% with obesity, including {p("all", "class_3")}% '
    'with a BMI of 40 or more.</p>'
    f'<figure class="figure">{svg_dots}<figcaption>600 US adults drawn from CDC’s 2021–2023 survey, each with a chance in '
    'proportion to the number of adults it stands for, so the cloud has the shape of the US adult population.</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table"><caption>US adults by BMI category (%)</caption><thead><tr>'
    '<th scope="col">Category</th><th scope="col" class="num">All adults</th><th scope="col" '
    f'class="num">Men</th><th scope="col" class="num">Women</th></tr></thead><tbody>{us_rows}</tbody></table></div>'
    f'<p>Women are more likely than men to have a healthy BMI ({p("women", "healthy")}% against {p("men", "healthy")}%) and '
    f'a BMI of 40 or more ({p("women", "class_3")}% against {p("men", "class_3")}%). Obesity as a whole is about as common '
    f'in both: {p("women", "obesity")}% of women and {p("men", "obesity")}% of men, a difference within the margin of '
    'error.</p>'
    f'<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023 measured heights and weights '
    f'({C["all"]["n"]:,} adults aged 20 and over; survey-weighted; pregnant women excluded). The obesity and BMI 40 or more '
    f'rates match NCHS’s published crude rates for all adults, men and women ({ext(U["db508"], "Data Brief 508")}), and the '
    f'overweight rate matches the crude rate in {ext(U["hes111"], "Health E-Stat 111")}. Each share '
    f'has a 95% margin of error of up to ±{HALF_HI} points, and each difference stated above is larger than its own margin of '
    f'error. Heights from 4′10″ to 6′6″, the chart’s rows, cover {HCOV}% of US adults.</p>'
    '<p>For what US adults weigh at each height, see <a href="/average-weight/">average weight by height</a>; '
    '<a href="/us-obesity-statistics/">US obesity statistics</a> has the trends since 1960.</p>'
    '</section>')

sec_age = (
    '<section id="age-sex" class="content-section flow"><h2>Age, sex and children</h2>'
    '<p><strong>One chart for every adult.</strong> CDC sets adult BMI categories “regardless of age, sex, or race” '
    f'({ext(U["cdc_cat"], "CDC")}), so the chart is the same for women and men at 20 or at 80. The body behind the '
    'number differs:</p><ul>'
    f'<li><strong>Sex.</strong> At a healthy BMI, the median US woman aged 20 to 59 had {BF_W}% body fat and the median man '
    f'{BF_M}% (our analysis of CDC body scans, 2011–2018). The <a href="/blog/bmi-chart-women/">BMI chart for women</a> and '
    'the <a href="/blog/bmi-chart-men/">BMI chart for men</a> cover each sex’s usual heights.</li>'
    '<li><strong>Muscle.</strong> “BMI does not distinguish between fat, muscle, and bone mass” '
    f'({ext(U["cdc_about"], "CDC")}), so a very muscular adult can read as overweight.</li>'
    '<li><strong>Age.</strong> “Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to '
    f'underdiagnosis of obesity” ({ADA_CITE}). <a href="/blog/bmi-by-age/">BMI by age</a> covers older adults.</li></ul>'
    '<p><strong>Children and teens.</strong> Under 20, BMI is read as a percentile for age and sex, not on this chart '
    f'({ext(U["cdc_child"], "CDC")}); the <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it '
    'out for ages 2 to 19.</p>'
    f'<p><strong>Pregnancy.</strong> During pregnancy, {ext(U["cdc_preg"], "CDC’s advice on weight gain")} depends on BMI '
    'before pregnancy; the <a href="/blog/bmi-chart-women/#pregnancy">BMI chart for women</a> has the table.</p>'
    '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the adult cut-offs and the “regardless of age, sex, or race” rule '
    '(page last reviewed March 2024).',
    f'CDC. {ext(U["cdc_about"], "About Body Mass Index (BMI)")}: what BMI does and doesn’t measure.',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formulas in US units and metric.',
    f'CDC. {ext(U["cdc_preg"], "Weight Gain During Pregnancy")}: recommended gain by BMI before pregnancy (Institute of '
    'Medicine).',
    f'NIH (NHLBI). {ext(U["nih_tbl"], "Body Mass Index Table")} (NIH Publication No. 22-HL-8190, September 2022): one '
    f'column for each whole BMI from {NIH_COLS[0]} to {NIH_COLS[1]}.',
    f'CDC {ext(U["bmx"], "NHANES August 2021–August 2023")} demographics and body measures files (DEMO_L, BMX_L): our '
    f'calculation of the share of adults aged 20 and over in each BMI category ({C["all"]["n"]:,} adults), of the 2026 ADA '
    f'thresholds ({A_N:,} adults), of BMI under 20 and of heights from 4′10″ to 6′6″, weighted with the exam weights, '
    'pregnant women excluded; the 600-adult figure is a sample drawn from the same files. The same files give the average '
    'weight at each height on <a href="/average-weight/">average weight by height</a>.',
    f'Emmerich SD, et al. {ext(U["db508"], "NCHS Data Brief No. 508")} (Sep 2024): obesity and severe obesity in US adults '
    'by sex and age, August 2021–August 2023.',
    f'Fryar CD, Afful J, Saif NT. {ext(U["hes111"], "NCHS Health E-Stat 111")} (Feb 2026): overweight and obesity in US '
    'adults, August 2021–August 2023.',
    'American Diabetes Association Professional Practice Committee for Obesity. '
    f'{ext(U["ada"], "Screening, Diagnosis, Evaluation, and Staging of Obesity in Adults: Standards of Care in Overweight and Obesity—2026")}: '
    f'obesity thresholds with waist size (recommendations 3.3a and 3.3b); {ext(U["ada_pr"], "ADA press release")}, June 2026.',
    f'Rubino F, et al. {ext(U["lancet"], "Definition and diagnostic criteria of clinical obesity")} (Lancet Diabetes & '
    'Endocrinology, 2025): the Lancet Commission on Clinical Obesity.',
    'CDC NHANES 2011–2018 DXA body scans: our analysis of body fat by BMI band, women and men aged 20 to 59 '
    '(<a href="/body-fat-percentage-chart/">body fat percentage chart</a>).',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Charts: the lightest and heaviest whole pounds (or kilograms) whose '
    'BMI, rounded to one decimal, falls in each CDC category at each height, each unit worked out on its own; BMI = lb × 703 '
    '÷ in², or kg ÷ m². Printable table: the lightest whole pound whose rounded BMI reaches each column. Heights for each '
    'weight: every whole inch from 4′10″ to 6′6″ and every whole centimeter from 145 to 200 cm, classed by the same rule. '
    'US adults: CDC NHANES August 2021–August 2023, adults aged 20 and over with a measured height and weight, pregnant '
    'women excluded, weighted with the exam weights; BMI, waist and height as CDC records them; 95% confidence intervals by '
    'Taylor linearization over the survey’s strata and primary sampling units, and the page states only differences whose '
    'interval excludes zero. The 2026 ADA thresholds are applied to the measured BMI, waist and height; adults identified '
    'in the survey as non-Hispanic Asian get the Asian thresholds; adults whose class depends on a waist that was not '
    f'measured ({A_LEFT}) are left out of that comparison, and the BMI-only share is computed on the same adults. The '
    '600 dots are drawn by systematic sampling with probability proportional to the exam weight, from a shuffled list with '
    'a fixed seed.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/kids-bmi-calculator/', 'BMI calculator for children and teens'),
        ('/ideal-weight/', 'Ideal weight calculator'), ('/body-fat-calculator/', 'Body fat calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/blog/bmi-chart-women/', 'BMI chart for women'), ('/blog/bmi-chart-men/', 'BMI chart for men'),
        ('/blog/healthy-bmi-range/', 'Healthy BMI range'), ('/average-weight/', 'Average weight by height'),
        ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'), ('/blog/bmi-by-age/', 'BMI by age'),
        ('/blog/bmi-chart-explained/', 'How to read a BMI chart'), ('/us-obesity-statistics/', 'US obesity statistics')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> <article> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_chart, sec_read, sec_print, sec_rev, sec_waist, sec_us, sec_age, sec_faq,
     sec_src, sec_rel]) + ' </article> </div></main>')
assert 'placeholder' not in main and 'style="' not in re.sub(r'(?s)<svg.*?</svg>', '', main)
assert len(re.findall(r'<section id="([^"]+)"', main)) == 9 and all(f'id="{a}"' in main for a, _ in CHIPS)

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'BMI Chart for Adults: Height and Weight Chart (Printable)'
H1 = 'BMI Chart for Adults: Height and Weight Chart'
DESC = ('BMI chart for adults from 4′10″ to 6′6″: healthy, overweight and obesity weights at every height in lb and kg, a '
        'printable BMI table and the 2026 waist rule.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'BMI chart for adults: height and weight chart in lb and kg'
OG_D = ('Every height from 4′10″ to 6′6″ in lb and kg, a printable BMI table, the heights for each weight, and where US '
        'adults fall (CDC data, our calculation).')
PREF = SITE + '/assets/images/preferred/bmi-chart-'
IMG16, IMG43, IMG11 = PREF + '16x9.png', PREF + '4x3.png', PREF + '1x1.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG16}">', src)
src = sub1(r'<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
src = sub1(re.escape(VIEWPORT), VIEWPORT + '<meta name="robots" content="max-image-preview:large">', src)
# The old chart's page-level <style> (.bmi-chart cells, jump selects, stat grid) gives way to .weight-chart in styles.css.
# (A second <style>, the old hero's desktop/mobile switch, sits inside <main> and goes with it.)
_head = src[:src.index('<main>')]
assert _head.count('<style>') == 1 and '.bmi-chart' in re.search(r'(?s)<style>.*?</style>', _head).group(0)
assert src.count('<style>') == 2 and 'hero-chart-mobile' in re.findall(r'(?s)<style>.*?</style>', src)[1]
src = re.sub(r'(?s)<style>.*?</style>', '', src, count=1)

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
types = [json.loads(b.group(1))['@type'] for b in blocks]
assert types == ['Article', 'BreadcrumbList', 'FAQPage'], types
art = json.loads(blocks[0].group(1))
assert art['datePublished'] == '2026-09-27' and art['url'] == URL
art.update({'headline': H1, 'description': DESC, 'dateModified': '{TODAY}', 'image': [IMG11, IMG43, IMG16],
            'author': {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'},
            'publisher': {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'CalculateMyBMI', 'url': SITE + '/'},
            'mainEntityOfPage': {'@type': 'WebPage', '@id': URL, 'url': URL, 'primaryImageOfPage': {
                '@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}}})
crumbs = json.loads(blocks[1].group(1))
assert crumbs['itemListElement'][1]['item'] == URL
crumbs['itemListElement'][1]['name'] = H1
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
for b, new in ((blocks[2], faq_ld), (blocks[1], crumbs), (blocks[0], art)):      # back to front, so offsets stay valid
    src = src[:b.start(1)] + ' ' + json.dumps(new, ensure_ascii=False) + ' ' + src[b.end(1):]

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('{TODAY}') == 1 and '<style' not in src

open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'bmi-chart/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, '
      f'{len(FAQ)} FAQ, {len(TEXTS)} SVG labels checked, dots by band {n_band}')
