#!/usr/bin/env python3
"""CMB-012 HOME — rebuilds / (index.html) to the D-14 pattern (the CMB-006 men page): tool first, answer
block and key takeaways, contents chips, a worked example, real tables, a flat FAQ whose JSON-LD equals the
visible answers, sources and method, one related block, one 680 px reading column.

Wedge: the result ranked among US adults, and among men and women separately (CDC NHANES 2021-2023,
5,929 adults, our calculation in home_stats.py).

Every number on the page comes from home_stats.json, from the calculator's own rounding rule (mirrored
below and asserted against assets/js/calculator.js outputs), or from a source verified in chat on
2026-10-14 (listed in "Sources and method").

usage: python3 gen_home.py REPO_ROOT STATS_JSON
Runs once, on index.html as it stood at c4004c8; kept as the build record.
"""
import sys, os, re, json, math, html

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
PAGE = os.path.join(ROOT, 'index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
MEN = json.load(open(os.path.join(ROOT, 'research/men-pilot/men_stats.json')))
assert S['men']['p1_p99'] == MEN['p1_p99'], 'men curve must equal the men page curve'

# ---------------------------------------------------------------- numbers
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10

def bounds(h_in, lo, hi):
    """Mirrors weightBounds() in assets/js/calculator.js: pounds via 703, kilograms via kg/m2 (CMB-011)."""
    k = h_in * h_in / 703; m2 = (h_in * 0.0254) ** 2
    out = {}
    if lo is not None:
        out['minLb'] = math.ceil((lo - 0.05) * k - 1e-9); out['minKg'] = math.ceil((lo - 0.05) * m2 - 1e-9)
    if hi is not None:
        out['maxLb'] = math.ceil((hi + 0.05) * k - 1e-9) - 1; out['maxKg'] = math.ceil((hi + 0.05) * m2 - 1e-9) - 1
    return out

def rank(q, b):
    """The share of adults with a BMI at or below b, read from the 1st-99th percentile curve (the page script's pct())."""
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0

def lower(q, b): return rank(q, round(b - 0.1, 1))     # share with a lower BMI (BMI is recorded to 0.1)
def higher(q, b): return 100 - rank(q, b)              # share with a higher BMI

QA, QM, QW = S['adults']['p1_p99'], S['men']['p1_p99'], S['women']['p1_p99']
TA, TM, TW = S['adults']['table'], S['men']['table'], S['women']['table']
CS = S['category_shares_pct']
N_ADULTS, N_MEN, N_WOMEN = S['adults']['bmi_n'], S['men']['bmi_n'], S['women']['bmi_n']
assert (N_ADULTS, N_MEN, N_WOMEN) == (5929, 2680, 3249)
assert (TA['p50'], TM['p50'], TW['p50']) == (28.2, 28.2, 28.3)
assert S['reproduces_nchs_crude_prevalence']['ours'] == S['reproduces_nchs_crude_prevalence']['nchs']
assert CS == {'underweight': 1.6, 'healthy': 26.0, 'overweight': 32.1, 'obesity_class_1': 20.6,
              'obesity_class_2': 10.3, 'obesity_class_3': 9.4}
SHARE25 = S['share_bmi_25_plus_pct']; assert SHARE25 == 72.4 == round(CS['overweight'] + S['obesity_pct'], 1)

# Worked example: the calculator's imperial starting values, 5'7" and 160 lb.
EX_H, EX_W = 67, 160
EX_BMI = r1(EX_W * 703 / EX_H ** 2)
HB = bounds(EX_H, 18.5, 24.9)
EX_GAP = EX_W - HB['maxLb']
EX_RA, EX_RM, EX_RW = (round(lower(q, EX_BMI)) for q in (QA, QM, QW))
EX_HA = round(higher(QA, EX_BMI))
EX_PRIME = '1.00'                                   # bmiPrime(25.1): Math.round(25.1 * 4) / 100
EX_PI = round((EX_W / 2.20462) / ((EX_H * 0.0254) ** 3), 1)
FROM = {c: bounds(EX_H, c, None)['minLb'] for c in (25, 30, 35, 40)}
PER_LB = 703 / EX_H ** 2
assert (EX_BMI, HB['minLb'], HB['maxLb'], HB['minKg'], HB['maxKg'], EX_GAP) == (25.1, 118, 159, 54, 72, 1)
assert (EX_RA, EX_RM, EX_RW, EX_HA) == (28, 26, 31, 71), (EX_RA, EX_RM, EX_RW, EX_HA)
assert EX_PI == 14.7 and FROM == {25: 160, 30: 192, 35: 224, 40: 256}, (EX_PI, FROM)
assert r1(159 * 703 / EX_H ** 2) == 24.9 and r1(155 * 703 / EX_H ** 2) == 24.3 and round(PER_LB, 2) == 0.16
EX_CM = round(EX_H * 2.54, 1); EX_KG = round(EX_W / 2.20462, 1)
assert (EX_CM, EX_KG) == (170.2, 72.6)
# Limits converted, as imperial mode prints them in brackets (fmtBound): 118 lb = 53.5 kg, 159 lb = 72.1 kg.
assert (f"{HB['minLb'] / 2.20462:.1f}", f"{HB['maxLb'] / 2.20462:.1f}") == ('53.5', '72.1')

# PAA: 70 kg at 170 cm (the metric starting values).
M_BMI = r1(70 / 1.7 ** 2)
MB = bounds(170 / 2.54, 18.5, 24.9)
M_RA = round(lower(QA, M_BMI))
assert (M_BMI, MB['minKg'], MB['maxKg'], MB['minLb'], MB['maxLb'], M_RA) == (24.2, 54, 72, 118, 158, 22)
# PAA: a BMI of 23.
H23 = higher(QA, 23.0); assert round(H23) == 84
W23_LB, W23_KG = 23 * 66 ** 2 / 703, 23 * (66 * 0.0254) ** 2
assert (round(W23_LB), round(W23_KG)) == (143, 65)

# Healthy weight by height, 3-inch steps; each unit worked out on its own.
ROWS = []
for ft, inch in ((5, 0), (5, 3), (5, 6), (5, 9), (6, 0), (6, 3)):
    h = ft * 12 + inch
    hb, ob, xb = bounds(h, 18.5, 24.9), bounds(h, 25, None), bounds(h, 30, None)
    ROWS.append((ft, inch, round(h * 2.54, 1), hb, ob, xb))
assert [(r[3]['minLb'], r[3]['maxLb'], r[3]['minKg'], r[3]['maxKg'], r[4]['minLb'], r[4]['minKg'], r[5]['minLb'], r[5]['minKg'])
        for r in ROWS] == [(95, 127, 43, 57, 128, 58, 154, 70), (105, 140, 48, 63, 141, 64, 170, 77),
                          (115, 154, 52, 70, 155, 71, 186, 85), (125, 168, 57, 76, 169, 77, 203, 92),
                          (137, 183, 62, 83, 184, 84, 221, 101), (148, 199, 67, 90, 200, 91, 240, 109)]
B64, B70 = bounds(64, 18.5, 24.9), bounds(70, 18.5, 24.9)
assert (B64['minLb'], B64['maxLb'], B64['minKg'], B64['maxKg']) == (108, 145, 49, 65)
assert (B70['minLb'], B70['maxLb'], B70['minKg'], B70['maxKg']) == (129, 173, 59, 78)

# 100 adults by category, rounded to whole adults.
GRID = [('underweight', round(CS['underweight'])), ('healthy', round(CS['healthy'])), ('overweight', round(CS['overweight'])),
        ('obese', round(CS['obesity_class_1'] + CS['obesity_class_2'])), ('obese-severe', round(CS['obesity_class_3']))]
assert [n for _, n in GRID] == [2, 26, 32, 31, 9] and sum(n for _, n in GRID) == 100

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'he111': 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm',
    'he119': 'https://www.cdc.gov/nchs/data/hestat/hestat119.htm',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    's3': 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf',
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'nhlbi_oo': 'https://www.nhlbi.nih.gov/health/overweight-and-obesity',
    'who2004': 'https://pubmed.ncbi.nlm.nih.gov/14726171/',
    'who1995': 'https://www.who.int/publications/i/item/9241208546',
    'lancet': 'https://pubmed.ncbi.nlm.nih.gov/39824205/',
    'wing': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
}

# ---------------------------------------------------------------- SVGs
TEXTS = []          # (svg, x0, y0, x1, y1, label): estimated boxes for the collision check below

def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827'):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'

# Figure 1: BMI at each weight from 156 to 163 lb at 5'7" (one pound over the line).
CELL, X0, VB1 = 38, 48, 360
cells, nums, bmis = [], [], []
WTS = list(range(156, 164))
for i, w in enumerate(WTS):
    b = r1(w * 703 / EX_H ** 2)
    x = X0 + i * CELL
    healthy = b <= 24.9
    cells.append(f'<rect x="{x}" y="62" width="{CELL}" height="36" fill="{"#d1fae5" if healthy else "#fde68a"}" stroke="#ffffff" stroke-width="2"/>')
    nums.append(text('f1', x + CELL / 2, 85, str(w), 15, weight=600))
    bmis.append(text('f1', x + CELL / 2, 122, f'{b:.1f}', 14, fill='#1f2937'))
assert [r1(w * 703 / EX_H ** 2) for w in WTS] == [24.4, 24.6, 24.7, 24.9, 25.1, 25.2, 25.4, 25.5]
ex_x = X0 + 4 * CELL
svg1 = (f'<svg viewBox="0 0 {VB1} 190" width="{VB1}" height="190" role="img" aria-labelledby="fig-line-t fig-line-d" font-family="inherit">'
        '<title id="fig-line-t">At 5 feet 7 inches, 159 pounds is a healthy weight and 160 pounds is overweight</title>'
        '<desc id="fig-line-d">A strip of eight weights from 156 to 163 pounds with the BMI of each underneath. 156 to 159 pounds '
        'give BMIs of 24.4 to 24.9, a healthy weight. 160 to 163 pounds give 25.1 to 25.5, overweight. Each pound adds about '
        '0.16 to BMI at this height. The calculator example, 160 pounds, is outlined.</desc>'
        + text('f1', VB1 / 2, 20, '5′7″ (170.2 cm): BMI at each weight', 15, weight=700)
        + text('f1', X0 + 2 * CELL, 52, 'Healthy weight', 13, weight=600, fill='#15803d')
        + text('f1', X0 + 6 * CELL, 52, 'Overweight', 13, weight=600, fill='#92400e')
        + text('f1', 6, 85, 'lb', 13, anchor='start', weight=600, fill='#4b5563')
        + text('f1', 6, 122, 'BMI', 13, anchor='start', weight=600, fill='#4b5563')
        + ''.join(cells)
        + f'<line x1="{ex_x}" y1="38" x2="{ex_x}" y2="130" stroke="#111827" stroke-width="1.5" stroke-dasharray="4 3"/>'
        + f'<rect x="{ex_x + 1.5}" y="63.5" width="{CELL - 3}" height="33" fill="none" stroke="#111827" stroke-width="3"/>'
        + ''.join(nums) + ''.join(bmis)
        + text('f1', ex_x + CELL / 2, 156, 'Example: 160 lb, BMI 25.1', 14, weight=700)
        + text('f1', VB1 / 2, 180, 'Each pound adds about 0.16 at this height', 13, fill='#4b5563')
        + '</svg>')

# Figure 2: 100 US adults by BMI category (10 x 10 squares, filled row by row).
COLORS = {'underweight': '#3b82f6', 'healthy': '#22c55e', 'overweight': '#f59e0b', 'obese': '#ef4444', 'obese-severe': '#991b1b'}
LABELS = {'underweight': 'underweight (under 18.5)', 'healthy': 'healthy weight (18.5–24.9)',
          'overweight': 'overweight (25–29.9)', 'obese': 'class 1–2 obesity (30–39.9)',
          'obese-severe': 'class 3 obesity (40 or more)'}
SQ, GAP, GX, GY = 18, 4, 50, 34
squares, k = [], 0
for cat, n in GRID:
    for _ in range(n):
        r, c = divmod(k, 10)
        squares.append(f'<rect x="{GX + c * (SQ + GAP)}" y="{GY + r * (SQ + GAP)}" width="{SQ}" height="{SQ}" rx="3" fill="{COLORS[cat]}"/>')
        k += 1
legend, ly = [], GY + 10 * (SQ + GAP) + 16
for i, (cat, n) in enumerate(GRID):
    y = ly + i * 22
    legend.append(f'<rect x="{GX}" y="{y - 11}" width="12" height="12" rx="2" fill="{COLORS[cat]}"/>')
    legend.append(text('f2', GX + 20, y, f'{n} {LABELS[cat]}', 13, anchor='start', fill='#1f2937'))
H2 = ly + 4 * 22 + 12
svg2 = (f'<svg viewBox="0 0 320 {H2}" width="320" height="{H2}" role="img" aria-labelledby="fig-100-t fig-100-d" font-family="inherit">'
        '<title id="fig-100-t">Of every 100 US adults: 2 underweight, 26 healthy weight, 32 overweight, 31 with class 1 or 2 obesity and 9 with class 3 obesity</title>'
        '<desc id="fig-100-d">A grid of 100 squares, one per adult, coloured by BMI category: 2 blue for underweight, 26 green for '
        'a healthy weight, 32 amber for overweight, 31 red for class 1 or 2 obesity and 9 dark red for class 3 obesity. '
        'CDC measurements of US adults aged 20 and over, August 2021 to August 2023.</desc>'
        + text('f2', 160, 20, 'Of every 100 US adults', 15, weight=700)
        + ''.join(squares) + ''.join(legend) + '</svg>')

# Collision check on the estimated text boxes (the rendered check runs in research/home-build/home_test_playwright.py).
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
            raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    width = VB1 if svg == 'f1' else 320
    assert x0 >= 0 and x1 <= width, f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
FAQ = [
    ('What is the correct BMI for my age?',
     f'For adults 20 and over there is one healthy range at every age: <strong>18.5 to 24.9</strong>. CDC applies its adult '
     f'categories “regardless of age, sex, or race” ({ext(U["cdc_cat"], "CDC")}). Under 20, BMI is read as a percentile for age '
     f'and sex instead; use the <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a>. Body composition does '
     f'change: body fat at a given BMI depends on age and sex ({ext(U["gallagher"], "Gallagher et al., 2000")}). In adults 65 '
     f'and over, a meta-analysis of 197,940 people found that the risk of death rose below a BMI of 23 and above 33 '
     f'({ext(U["winter"], "Winter et al., 2014")}), an association rather than a target. The '
     f'<a href="/age-bmi-calculator/">BMI calculator by age</a> has more on adults 65 and over.'),
    ('What is the BMI of 70 kg 170 cm?',
     f'<strong>{M_BMI}</strong>, a healthy weight: 70 ÷ (1.70 × 1.70) = 70 ÷ 2.89 = {M_BMI}. At 170 cm the healthy range is '
     f'{MB["minKg"]} to {MB["maxKg"]} kg ({MB["minLb"]} to {MB["maxLb"]} lb), so 70 kg sits {MB["maxKg"] - 70} kg below its top. '
     f'Among US adults, a BMI of {M_BMI} is higher than about {M_RA}% (our calculation from CDC measurements, 2021–2023).'),
    ('Is a 23 BMI chubby?',
     f'No. A BMI of 23 is in the <strong>healthy weight</strong> range (18.5 to 24.9), 2 points below where overweight starts; at '
     f'5′6″ (167.6 cm) it’s about {round(W23_LB)} lb ({round(W23_KG)} kg). About {round(H23)}% of US adults have a higher '
     f'BMI (our calculation from CDC measurements, 2021–2023). BMI can’t show how much of your weight is fat: the '
     f'<a href="/body-fat-calculator/">body fat calculator</a> estimates that, and a waist measurement shows where fat sits.'),
    ('What is the new BMI chart for 2026?',
     f'There isn’t one. CDC’s adult categories are unchanged: under 18.5 underweight, 18.5 to 24.9 healthy weight, 25 to 29.9 '
     f'overweight and 30 or more obesity, in classes 1 to 3 ({ext(U["cdc_cat"], "CDC")}). What changed in 2025 is advice on '
     f'diagnosis: the {ext(U["lancet"], "Lancet Commission on Clinical Obesity")} recommended confirming excess body fat with a '
     f'waist measurement or a direct body-fat measurement instead of diagnosing obesity from BMI alone. The “new BMI” formula '
     f'some sites show is Nick Trefethen’s 2013 proposal; CDC and WHO still use the standard formula (see the '
     f'<a href="/new-bmi-calculator/">new BMI calculator</a>).'),
    ('What is a normal BMI?',
     f'<strong>18.5 to 24.9</strong>, which CDC calls a healthy weight. It’s the same for men and women at every adult age. '
     f'At 5′4″ (162.6 cm) that’s {B64["minLb"]} to {B64["maxLb"]} lb ({B64["minKg"]} to {B64["maxKg"]} kg); at 5′10″ (177.8 cm), '
     f'{B70["minLb"]} to {B70["maxLb"]} lb ({B70["minKg"]} to {B70["maxKg"]} kg). The '
     f'<a href="/blog/healthy-bmi-range/">healthy BMI range guide</a> covers the range in more depth.'),
    ('Is BMI the same for men and women?',
     f'The formula and the cut-offs are the same. Bodies differ: body fat at a given BMI depends on sex '
     f'({ext(U["gallagher"], "Gallagher et al., 2000")}), and in CDC’s body scans the average woman aged 20 to 59 had 38.7% body '
     f'fat against 27.2% for the average man (our analysis of NHANES 2011–2018). US distributions differ too: the median BMI is '
     f'{TM["p50"]} for men and {TW["p50"]} for women, but 1 in 10 women has a BMI of {TW["p90"]} or more, against {TM["p90"]} for '
     f'men. The calculators <a href="/women-bmi-calculator/">for women</a> and <a href="/men-bmi-calculator/">for men</a> add '
     f'the waist cut-off for each sex.'),
    ('Is BMI a percentage?',
     f'No. BMI is a ratio in kilograms per square meter, so a BMI of 25 means 25 kg/m², not 25%. Body fat percentage is a '
     f'different measure: the share of your weight that is fat, which the <a href="/body-fat-calculator/">body fat '
     f'calculator</a> estimates. The only percentage this calculator shows is your rank, the share of US adults with a lower BMI '
     f'than yours.'),
    ('How accurate is BMI?',
     f'The number is exact for the height and weight you enter. As a measure of body fat it’s indirect: CDC notes that BMI '
     f'“does not directly measure body fat” and “does not distinguish between fat, muscle, and bone mass”, though it is '
     f'moderately to strongly associated with other measures of body fat ({ext(U["cdc_about"], "CDC")}). For one person, CDC says '
     f'BMI “should be considered with other factors”, such as blood pressure and cholesterol. A waist measurement is the '
     f'simplest check to add (see <a href="#misleading">when BMI misleads</a>).'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
def cat_cell(cls, name): return f'<span class="cat-dot {cls}" aria-hidden="true"></span>{name}'

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>BMI (body mass index)</strong> is your weight in kilograms divided by your height in meters '
    'squared, or pounds × 703 ÷ inches². For adults 20 and over, CDC uses one scale for everyone: <strong>under 18.5 is '
    'underweight, 18.5 to 24.9 is a healthy weight</strong>, 25 to 29.9 is overweight and 30 or more is obesity.</p><ul>'
    f'<li>The healthy weight depends only on height: at 5′7″ (170.2 cm) it is <strong>{HB["minLb"]} to {HB["maxLb"]} lb '
    f'({HB["minKg"]} to {HB["maxKg"]} kg)</strong>.</li>'
    f'<li><strong>The median US adult has a BMI of {TA["p50"]}</strong>, and {SHARE25}% have a BMI of 25 or more (CDC '
    'measurements, 2021–2023).</li>'
    '<li>Obesity has three classes: 30 to 34.9, 35 to 39.9 and 40 or more.</li>'
    '<li>Under 20, BMI is read as a percentile for age and sex, not on this scale.</li>'
    '<li><strong>BMI can’t tell muscle from fat</strong>, and it can’t show where fat sits; a waist measurement can.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information only. '
    'BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in (
           ('read-result', 'Your result'), ('us-adults', 'US adults'), ('categories', 'Categories'),
           ('by-height', 'Weight by height'), ('by-hand', 'By hand'), ('misleading', 'When BMI misleads'),
           ('children', 'Children'), ('health', 'Health'), ('situations', 'Situations'), ('faq', 'FAQ'),
           ('sources', 'Sources')))
       + '</nav>')

sec_read = (
    '<section id="read-result" class="content-section flow"><h2>How to read your result</h2>'
    f'<p>Every number below uses the calculator’s imperial starting values: 5′7″ ({EX_CM} cm) and {EX_W} lb ({EX_KG} kg). '
    'That weight sits right on the line between two categories.</p>'
    f'<figure class="figure">{svg1}<figcaption>At 5′7″ the healthy range ends at 159 lb (BMI 24.9); at 160 lb the BMI is 25.1, '
    'overweight.</figcaption></figure>'
    '<dl>'
    f'<dt>BMI: {EX_BMI}, overweight</dt><dd>{EX_W} × 703 ÷ {EX_H}² = {EX_BMI}, rounded to one decimal; the category comes from '
    'that rounded number. At 159 lb the BMI would be 24.9, a healthy weight. The calculator shows the CDC category for adults, '
    f'and below 17 the WHO thinness grades: moderate thinness from 16 to 16.9 and severe thinness under 16 '
    f'({ext(U["who1995"], "WHO, 1995")}).</dd>'
    f'<dt>Healthy weight: {HB["minLb"]}–{HB["maxLb"]} lb ({HB["minKg"]}–{HB["maxKg"]} kg)</dt><dd>The lightest and heaviest '
    'whole pounds at your height with a BMI of 18.5 to 24.9, and the same in whole kilograms. It depends only on height. '
    'In imperial mode the tiles also show each limit converted (53.5 and 72.1 kg).</dd>'
    f'<dt>{EX_GAP} lb (0.5 kg) above the healthy range</dt><dd>The distance from your weight to the nearest end of that range.</dd>'
    f'<dt>Compared with US adults: higher than {EX_RA}%</dt><dd>The share of adults aged 20 and over, measured by CDC in '
    f'2021–2023, whose BMI is lower than yours. The result adds the figure for men alone ({EX_RM}%) and women alone '
    f'({EX_RW}%); the <a href="#us-adults">next section</a> has the full table.</dd>'
    f'<dt>BMI Prime: {EX_PRIME}</dt><dd>Your BMI divided by 25, where overweight starts. 1.00 means you’re at that line; '
    'under 1.00 is below it.</dd>'
    f'<dt>Ponderal index: {EX_PI} kg/m³</dt><dd>Weight in kilograms divided by height in meters cubed. CDC and WHO publish no '
    'adult cut-offs for it, so compare it only with your own earlier results.</dd>'
    f'<dt>Weight milestones</dt><dd>The weight where each range starts at your height. At 5′7″: healthy from {HB["minLb"]} lb, '
    f'overweight from {FROM[25]} lb, obesity from {FROM[30]} lb, class 2 obesity from {FROM[35]} lb and class 3 from '
    f'{FROM[40]} lb.</dd>'
    '<dt>What-if table</dt><dd>Your BMI after losing or gaining 5 to 20 lb (2.5 to 10 kg in metric). Five pounds lighter, '
    'at 155 lb, the example’s BMI is 24.3.</dd>'
    '</dl></section>')

pct_rows = ''.join(
    f'<tr><th scope="row">{lab}</th><td class="num">{TA[k]}</td><td class="num">{TM[k]}</td><td class="num">{TW[k]}</td></tr>'
    for k, lab in (('p5', '5th'), ('p10', '10th'), ('p25', '25th'), ('p50', '50th'), ('p75', '75th'),
                   ('p90', '90th'), ('p95', '95th')))
sec_us = (
    '<section id="us-adults" class="content-section flow"><h2>How your BMI compares with US adults</h2>'
    f'<p>The comparison uses CDC’s measurements of {N_ADULTS:,} adults aged 20 and over (pregnant women excluded), taken from '
    f'August 2021 to August 2023 in its National Health and Nutrition Examination Survey (NHANES). <strong>The middle adult had '
    f'a BMI of {TA["p50"]}</strong>, '
    f'in the overweight range, and a quarter had a BMI of {TA["p25"]} or lower. The calculator ranks your result against these '
    'adults, then against men and women separately.</p>'
    f'<div class="stat-callout"><div class="stat-callout-value">{SHARE25}%</div><div class="stat-callout-text">of US adults '
    f'aged 20 and over have a BMI of 25 or more: {CS["overweight"]}% overweight and {S["obesity_pct"]}% with obesity, August '
    f'2021–August 2023.</div><div class="stat-callout-source">Source: CDC, {ext(U["he111"], "NCHS Health E-Stat 111")} '
    '(crude rates; 72.4% is their sum)</div></div>'
    '<div class="table-responsive"><table class="data-table"><caption>BMI percentiles, US adults aged 20 and over, '
    '2021–2023</caption><thead><tr><th scope="col">Percentile</th><th scope="col" class="num">All adults</th>'
    f'<th scope="col" class="num">Men</th><th scope="col" class="num">Women</th></tr></thead><tbody>{pct_rows}</tbody></table></div>'
    f'<p class="source-note">Read a row as: 25% of US adults have a BMI of {TA["p25"]} or lower. Our calculation from CDC '
    f'NHANES 2021–2023 measured heights and weights ({N_ADULTS:,} adults: {N_MEN:,} men and {N_WOMEN:,} women, '
    'survey-weighted, pregnant women excluded); the same method reproduces NCHS’s published medians (28.2 for men, 28.3 for '
    'women) and means (29.4 and 30.0).</p>'
    f'<p>The spread is wider among women. A quarter of women have a BMI of {TW["p25"]} or lower and one in ten has '
    f'{TW["p90"]} or more; for men the same points are {TM["p25"]} and {TM["p90"]}. The '
    '<a href="/us-obesity-statistics/">US obesity statistics</a> page has the trends since 1960 and the splits by age.</p>'
    '</section>')

cat_rows = ''.join(
    f'<tr><th scope="row">{cat_cell(cls, name)}</th><td>{rng}</td><td class="num">{share}%</td></tr>'
    for cls, name, rng, share in (
        ('underweight', 'Underweight', 'Under 18.5', CS['underweight']),
        ('normal', 'Healthy weight', '18.5–24.9', CS['healthy']),
        ('overweight', 'Overweight', '25–29.9', CS['overweight']),
        ('obese', 'Class 1 obesity', '30–34.9', CS['obesity_class_1']),
        ('obese', 'Class 2 obesity', '35–39.9', CS['obesity_class_2']),
        ('obese-severe', 'Class 3 obesity', '40 or more', CS['obesity_class_3'])))
sec_cat = (
    '<section id="categories" class="content-section flow"><h2>BMI categories for adults</h2>'
    f'<p>For adults 20 and older, CDC bases the categories on BMI alone, “regardless of age, sex, or race”. Only about '
    f'<strong>1 in 4 US adults ({CS["healthy"]}%) has a BMI in the healthy range</strong>; the last column shows how the rest '
    'are spread.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Adult BMI categories and the share of US adults in each, '
    '2021–2023</caption><thead><tr><th scope="col">Category</th><th scope="col">BMI</th><th scope="col" class="num">US adults'
    f'</th></tr></thead><tbody>{cat_rows}</tbody></table></div>'
    f'<p class="source-note">Categories: {ext(U["cdc_cat"], "CDC Adult BMI Categories")}. Shares: our calculation from CDC '
    f'NHANES 2021–2023 ({N_ADULTS:,} adults); they match NCHS’s published crude rates for underweight '
    f'({ext(U["he119"], "Health E-Stat 119")}), overweight ({ext(U["he111"], "Health E-Stat 111")}), obesity and class 3 '
    f'obesity ({ext(U["db508"], "Data Brief 508")}).</p>'
    f'<figure class="figure">{svg2}<figcaption>Of every 100 US adults aged 20 and over, 26 have a healthy weight and 72 have a '
    'BMI of 25 or more. CDC measurements, August 2021–August 2023; our calculation, rounded to whole adults.</figcaption></figure>'
    '<p>The <a href="/bmi-chart/">BMI chart</a> gives the weights for each category at every height, and there are charts '
    '<a href="/blog/bmi-chart-women/">for women</a> and <a href="/blog/bmi-chart-men/">for men</a>. '
    '<a href="/blog/bmi-categories/">BMI categories explained</a> covers what each range means for health.</p>'
    '</section>')

h_rows = ''.join(
    f'<tr><th scope="row">{ft}′{inch}″<span class="unit-alt">{cm:.1f} cm</span></th>'
    f'<td class="nowrap">{hb["minLb"]}–{hb["maxLb"]} lb<span class="unit-alt">{hb["minKg"]}–{hb["maxKg"]} kg</span></td>'
    f'<td class="nowrap">{xb["minLb"]} lb<span class="unit-alt">{xb["minKg"]} kg</span></td></tr>'
    for ft, inch, cm, hb, ob, xb in ROWS)
assert all(ob['minLb'] == hb['maxLb'] + 1 and ob['minKg'] == hb['maxKg'] + 1 for _, _, _, hb, ob, _ in ROWS)
sec_height = (
    '<section id="by-height" class="content-section flow"><h2>Healthy weight by height</h2>'
    '<p>The healthy range depends only on height and is the same for men and women. Overweight starts at the next pound (or '
    'kilogram) above it. Six heights below, 3 inches apart; the <a href="/bmi-chart/">full BMI chart</a> covers every inch '
    'from 4′10″ to 6′6″ and every 5 cm from 145 to 200 cm.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Healthy weight, and where obesity starts, by height'
    '</caption><thead><tr><th scope="col">Height</th><th scope="col">Healthy weight<span class="unit-alt">BMI 18.5–24.9</span>'
    '</th><th scope="col">Obesity from<span class="unit-alt">BMI 30</span></th></tr></thead>'
    f'<tbody>{h_rows}</tbody></table></div>'
    '<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, falls in each range at the height '
    'shown; each unit is worked out on its own. Cut-offs: ' + ext(U['cdc_cat'], 'CDC Adult BMI Categories') + '.</p>'
    '</section>')

sec_hand = (
    '<section id="by-hand" class="content-section flow"><h2>How to calculate BMI by hand</h2>'
    '<p>In pounds and inches, multiply your weight by 703 and divide by your height in inches squared. In metric, divide your '
    'weight in kilograms by your height in meters squared. Both formulas are CDC’s '
    f'({ext(U["cdc_formula"], "Calculating BMI")}); 703 turns pounds per square inch into kilograms per square meter.</p>'
    '<ul>'
    f'<li><strong>US units:</strong> {EX_W} lb at 5′7″ (67 in): {EX_W} × 703 ÷ (67 × 67) = 112,480 ÷ 4,489 = {EX_BMI}.</li>'
    f'<li><strong>Metric:</strong> 70 kg at 170 cm (1.70 m): 70 ÷ (1.70 × 1.70) = 70 ÷ 2.89 = {M_BMI}.</li>'
    f'<li><strong>From centimeters:</strong> 70 ÷ 170 ÷ 170 × 10,000 = {M_BMI}, the same result without converting to meters.</li>'
    '</ul>'
    '<p>Round to one decimal before reading the category, as the calculator and the BMI charts do. The '
    '<a href="/blog/bmi-formula/">BMI formula guide</a> explains where 703 comes from and the version Nick Trefethen proposed '
    'in 2013.</p>'
    '</section>')

sec_mis = (
    '<section id="misleading" class="content-section flow"><h2>When BMI misleads</h2>'
    f'<p>CDC calls BMI “a quick, safe, and reliable screening measure” and adds that it “does not distinguish between fat, '
    f'muscle, and bone mass” ({ext(U["cdc_about"], "CDC")}). Four common cases:</p>'
    '<ul>'
    '<li><strong>Muscle.</strong> A muscular person can have a BMI over 25 with little body fat. The '
    '<a href="/body-fat-calculator/">body fat calculator</a> estimates body fat from tape or skinfold measurements, and '
    '<a href="/blog/bmi-for-athletes/">BMI for athletes</a> goes further.</li>'
    '<li><strong>Where fat sits.</strong> US guidelines treat a waist over 40 inches (102 cm) in men and 35 inches (88 cm) in '
    f'women as a marker of higher risk, mainly at a BMI of 25 to 34.9 ({ext(U["nhlbi"], "NHLBI")}). The '
    '<a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> is another check.</li>'
    '<li><strong>Age.</strong> The cut-offs stay the same at every adult age, but body fat at a given BMI also depends on age, '
    f'sex and ethnic group ({ext(U["gallagher"], "Gallagher et al., 2000")}), so the same BMI can mean a different amount of '
    'fat at 25 and at 75. The <a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows typical body fat by '
    'age.</li>'
    '<li><strong>Asian ancestry.</strong> A WHO expert consultation found that many Asian populations have higher risk at '
    'lower BMIs. It kept the international categories and identified BMI 23, 27.5, 32.5 and 37.5 as points for public-health '
    f'action ({ext(U["who2004"], "WHO, 2004")}).</li>'
    '</ul>'
    f'<p>In 2025 the {ext(U["lancet"], "Lancet Commission on Clinical Obesity")} (58 experts, endorsed by 76 organizations) '
    'recommended confirming excess body fat with a body measurement such as waist size, or with a direct body-fat '
    'measurement, instead of diagnosing obesity from BMI alone. More in <a href="/blog/bmi-limitations/">BMI limitations</a>.</p>'
    '</section>')

sec_kids = (
    '<section id="children" class="content-section flow"><h2>BMI for children and teens</h2>'
    '<p>Under 20, the same BMI means different things at different ages, so CDC reads it as a percentile on growth charts for '
    'age and sex. This calculator uses the adult scale; for ages 2 to 19, use the '
    '<a href="/kids-bmi-calculator/">BMI calculator for children and teens</a>.</p>'
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

sec_health = (
    '<section id="health" class="content-section flow"><h2>BMI and health</h2>'
    '<p>US guidelines link a BMI above the healthy range with higher risk of high blood pressure, type 2 diabetes, coronary '
    f'heart disease, stroke, sleep apnea and osteoarthritis ({ext(U["nhlbi"], "NHLBI")}). In a large trial of adults with '
    'overweight or obesity and type 2 diabetes, losing 5 to 10% of body weight was linked to better blood sugar, blood '
    f'pressure, HDL cholesterol and triglycerides after one year ({ext(U["wing"], "Wing et al., 2011")}).</p>'
    f'<p>CDC notes that “poor nutrition and underlying health conditions can result in underweight” '
    f'({ext(U["he119"], "Health E-Stat 119")}); if your BMI is under 18.5 and you don’t know why, ask a doctor. '
    'For one person, CDC says BMI “should be considered with other factors”, such as blood pressure and cholesterol. The '
    'evidence behind each risk is in <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>.</p>'
    '</section>')

SIT = [
    ('You want a version for women or men',
     'The cut-offs are the same for everyone. The <a href="/women-bmi-calculator/">BMI calculator for women</a> and the '
     '<a href="/men-bmi-calculator/">one for men</a> add the waist cut-off for each sex and US data for women or men.'),
    ('You’re 65 or older',
     'The categories don’t change. The <a href="/age-bmi-calculator/">BMI calculator by age</a> adds the research on BMI and '
     'survival in adults 65 and over.'),
    ('You lift weights or play a power sport',
     'Muscle can push BMI past 25. A waist measurement and a tape or skinfold estimate from the '
     '<a href="/body-fat-calculator/">body fat calculator</a> can suggest whether the extra weight is fat.'),
    ('You want one target weight',
     'The healthy range is every weight with a BMI of 18.5 to 24.9 at your height. The <a href="/ideal-weight/">ideal weight '
     'calculator</a> shows the single weights that four published formulas give.'),
    ('You use kilograms and centimeters',
     'Switch the calculator to Metric. Results then show kilograms first, pounds second, and the healthy range in whole '
     'kilograms.'),
    ('You want to lower your BMI',
     'The what-if table shows your BMI at each 5 lb (2.5 kg) step. NIH’s '
     f'{ext("https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner", "Body Weight Planner")} '
     'builds a calorie and physical activity plan for a goal weight, for adults who aren’t pregnant or breastfeeding. More in '
     '<a href="/blog/how-to-lower-bmi/">how to lower your BMI</a>.'),
]
sec_sit = ('<section id="situations" class="content-section flow"><h2>Common situations</h2>'
           + ''.join(f'<h3>{t}</h3><p>{p}</p>' for t, p in SIT) + '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the cut-offs used by the calculator and the tables.',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formulas in US and metric units.',
    f'CDC. {ext(U["cdc_about"], "About Body Mass Index (BMI)")}: what BMI measures and what it misses.',
    f'CDC {ext(U["bmx"], "NHANES August 2021–August 2023")} exam files (DEMO_L, BMX_L): our calculation of BMI percentiles '
    f'and category shares for adults aged 20 and over ({N_ADULTS:,}: {N_MEN:,} men, {N_WOMEN:,} women), weighted with the exam '
    'weights, pregnant women excluded.',
    f'Fryar CD, Afful J, Saif NT. {ext(U["he111"], "NCHS Health E-Stat 111")} (Feb 2026): overweight and obesity in US adults, '
    'August 2021–August 2023.',
    f'Emmerich SD, et al. {ext(U["db508"], "NCHS Data Brief No. 508")} (Sep 2024): obesity and severe obesity in US adults, '
    'August 2021–August 2023.',
    f'Ansai N, Fryar CD, Afful J. {ext(U["he119"], "NCHS Health E-Stat 119")} (Jun 2026): underweight in US adults, August '
    '2021–August 2023.',
    f'CDC NCHS. {ext(U["s3"], "Vital and Health Statistics Series 3, No. 50")}: median and mean BMI of US men and women.',
    'CDC NHANES 2011–2018 DXA body scans: our analysis of average body fat by sex, ages 20 to 59 '
    '(<a href="/body-fat-percentage-chart/">body fat percentage chart</a>).',
    f'NHLBI. {ext(U["nhlbi"], "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")} '
    '(NIH, 1998): waist cut-offs and conditions linked to excess weight.',
    f'WHO Expert Consultation. {ext(U["who2004"], "The Lancet, 2004")}: BMI in Asian populations and the public-health action points.',
    'Trefethen N. ' + ext('https://people.maths.ox.ac.uk/trefethen/bmi.html', 'New BMI (University of Oxford)')
    + ': the 2013 proposal some sites call the “new BMI”.',
    f'WHO. {ext(U["who1995"], "Physical status: the use and interpretation of anthropometry")} (Technical Report Series 854, '
    '1995): thinness grades.',
    f'Rubino F, et al. {ext(U["lancet"], "Lancet Diabetes & Endocrinology, 2025")}: definition and diagnostic criteria of '
    'clinical obesity.',
    f'Wing RR, et al. {ext(U["wing"], "Diabetes Care, 2011")}: weight loss and cardiovascular risk factors after one year (Look AHEAD).',
    'NIDDK. ' + ext('https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner', 'Body Weight Planner')
    + ': calorie and physical activity plans for a goal weight, adults only.',
    f'Winter JE, et al. {ext(U["winter"], "American Journal of Clinical Nutrition, 2014")}: BMI and mortality in adults 65 and over.',
    f'Gallagher D, et al. {ext(U["gallagher"], "American Journal of Clinical Nutrition, 2000")}: body fat predicted from BMI, '
    'sex, age and ethnic group.',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> BMI = weight (kg) ÷ height (m)², or lb × 703 ÷ in², rounded to one '
    'decimal; the category uses the rounded value. Metric input is computed in kg/m², US input with 703. Healthy limits are '
    'the lightest and heaviest whole pounds (or kilograms) whose rounded BMI is 18.5 to 24.9, each unit worked out on its own. '
    'The rank is the share of adults with a lower BMI (and, for “lower than”, the share with a higher one), read from the '
    'survey-weighted distribution of measured BMI, which CDC records to one decimal (1st to 99th percentile, linear '
    'interpolation between them); adults with the same BMI count on neither side. The category shares reproduce NCHS’s '
    'published crude rates: underweight '
    '1.6%, overweight 32.1%, obesity 40.3%, class 3 obesity 9.4%. Data: CDC NHANES August 2021–August 2023.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/women-bmi-calculator/', 'BMI calculator for women'), ('/men-bmi-calculator/', 'BMI calculator for men'),
        ('/age-bmi-calculator/', 'BMI calculator by age'), ('/kids-bmi-calculator/', 'BMI calculator for children and teens'),
        ('/body-fat-calculator/', 'Body fat calculator'), ('/ideal-weight/', 'Ideal weight calculator'),
        ('/calculators/', 'All calculators')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/bmi-chart/', 'BMI chart'), ('/blog/healthy-bmi-range/', 'Healthy BMI range'),
        ('/blog/bmi-categories/', 'BMI categories explained'), ('/blog/bmi-formula/', 'BMI formula'),
        ('/blog/bmi-limitations/', 'BMI limitations'), ('/us-obesity-statistics/', 'US obesity statistics'),
        ('/average-weight/', 'Average weight')))
    + '</ul></div></div></section>')

calc = (
    '<div class="calculator-card"><div id="panel-standard" class="calc-panel active">'
    '<div class="unit-toggle"><button class="unit-btn active" data-unit="imperial">Imperial (ft, lbs)</button>'
    '<button class="unit-btn" data-unit="metric">Metric (cm, kg)</button></div>'
    '<div class="form-grid">'
    '<div class="form-row imperial-inputs"><div class="form-group"><label class="form-label" for="standard-height-ft">Height (feet)</label>'
    '<input type="number" id="standard-height-ft" class="form-input height-ft" value="5" min="1" max="8"></div>'
    '<div class="form-group"><label class="form-label" for="standard-height-in">Height (inches)</label>'
    '<input type="number" id="standard-height-in" class="form-input height-in" value="7" min="0" max="11"></div></div>'
    '<div class="form-row metric-inputs" style="display:none;"><div class="form-group"><label class="form-label" for="standard-height-cm">Height (cm)</label>'
    '<input type="number" id="standard-height-cm" class="form-input height-cm" value="170" min="50" max="250"></div></div>'
    '<div class="form-row imperial-inputs"><div class="form-group"><label class="form-label" for="standard-weight-lbs">Weight (lbs)</label>'
    '<input type="number" id="standard-weight-lbs" class="form-input weight-lbs" value="160" min="50" max="700"></div></div>'
    '<div class="form-row metric-inputs" style="display:none;"><div class="form-group"><label class="form-label" for="standard-weight-kg">Weight (kg)</label>'
    '<input type="number" id="standard-weight-kg" class="form-input weight-kg" value="70" min="20" max="300"></div></div>'
    '</div>'
    '<button class="calculate-btn" id="calc-standard-btn">Calculate BMI</button>'
    '<div class="results-section" id="standard-results">'
    '<div class="bmi-result-card normal" id="standard-result-card"><div class="bmi-value normal" id="standard-bmi-value">—</div>'
    '<div class="bmi-category" id="standard-bmi-category">—</div><div class="bmi-range" id="standard-bmi-range">—</div></div>'
    '<div class="bmi-scale"><div class="bmi-scale-bar"><div class="bmi-scale-segment underweight">Under</div>'
    '<div class="bmi-scale-segment normal">Healthy</div><div class="bmi-scale-segment overweight">Over</div>'
    '<div class="bmi-scale-segment obese">Class 1</div><div class="bmi-scale-segment obese-severe">Class 2+</div>'
    '<div class="bmi-scale-marker" id="standard-scale-marker" style="left:40%"></div></div>'
    '<div class="bmi-scale-labels"><span>15</span><span>18.5</span><span>25</span><span>30</span><span>35</span><span>40</span></div></div>'
    '<div class="results-grid"><div class="result-item"><div class="result-item-label">Lowest healthy weight</div>'
    '<div class="result-item-value" id="standard-healthy-min">—</div></div><div class="result-item">'
    '<div class="result-item-label">Highest healthy weight</div><div class="result-item-value" id="standard-healthy-max">—</div></div></div>'
    '<div class="weight-range-box"><p id="standard-weight-diff" style="margin:0;font-size:0.9375rem;">—</p></div>'
    '<div class="rank-box" id="standard-rank" hidden><div class="rank-title">Compared with US adults aged 20 and over</div>'
    '<div class="rank-value" id="standard-rank-value">—</div><div class="rank-track" aria-hidden="true"><span class="rank-median">'
    '</span><span class="rank-marker" id="standard-rank-marker"></span></div><div class="rank-axis" aria-hidden="true">'
    f'<span>Lowest BMI</span><span>Median {TA["p50"]}</span><span>Highest</span></div><p class="rank-text" id="standard-rank-text"></p>'
    f'<p class="rank-source">CDC NHANES 2021–2023, {N_ADULTS:,} adults measured; our calculation.</p></div>'
    '</div></div></div>')

head = (
    '<div class="page-head"><h1>BMI Calculator</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Enter your height and weight to see your BMI, healthy weight and how you compare with US adults.</p>'
    f'<p class="intro-note">CDC adult categories. US comparison: CDC measurements of {N_ADULTS:,} adults, 2021–2023. '
    '<a href="#sources">Method and sources</a></p></div>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, calc, takeaways, toc, sec_read, sec_us, sec_cat, sec_height, sec_hand, sec_mis, sec_kids, sec_health, sec_sit,
     sec_faq, sec_src, sec_rel]) + ' </div></main>')

# ---------------------------------------------------------------- rank script (mirrors the men page script)
def arr(q): return '[' + ','.join(f'{x:g}' for x in q) + ']'
rank_js = (
    '<script>(function(){var Q={a:' + arr(QA) + ',m:' + arr(QM) + ',w:' + arr(QW) + '};'
    'var v=document.getElementById("standard-bmi-value"),box=document.getElementById("standard-rank");if(!v||!box)return;'
    'function pct(q,b){if(b<=q[0])return 0;if(b>=q[98])return 100;for(var i=0;i<98;i++){if(b<q[i+1])return i+1+(b-q[i])/(q[i+1]-q[i]);}return 100;}'
    # lo = share with a lower BMI (BMI is recorded to 0.1, so the curve is read at b - 0.1); hi = share with a higher BMI
    'function rk(q,b){return{lo:pct(q,Math.round(b*10-1)/10),hi:100-pct(q,b)};}'
    'function n(x){return x>99?99:Math.round(x);}'
    'function lab(r){return r.lo<1?"lower than "+n(r.hi)+"%":"higher than "+n(r.lo)+"%";}'
    'function show(){var b=parseFloat(v.textContent);if(!(b>0)){box.hidden=true;return;}'
    'var r=rk(Q.a,b),s=b.toFixed(1),head=lab(r),txt;head=head.charAt(0).toUpperCase()+head.slice(1)+" of US adults";'
    'if(r.lo<1)txt="Your BMI of "+s+" is lower than about "+n(r.hi)+"% of US adults aged 20 and over.";'
    'else if(r.hi<1)txt="Your BMI of "+s+" is higher than about "+n(r.lo)+"% of US adults aged 20 and over.";'
    'else txt="Your BMI of "+s+" is higher than about "+n(r.lo)+"% of US adults aged 20 and over and lower than about "+n(r.hi)+"%.";'
    'txt+=" Compared with men only, it is "+lab(rk(Q.m,b))+"; with women only, "+lab(rk(Q.w,b))+". The median US adult has a BMI of ' + f'{TA["p50"]}' + '.";'
    'document.getElementById("standard-rank-value").textContent=head;document.getElementById("standard-rank-text").textContent=txt;'
    'document.getElementById("standard-rank-marker").style.left=Math.min(99,Math.max(1,r.lo))+"%";box.hidden=false;}'
    'new MutationObserver(show).observe(v,{childList:true,characterData:true,subtree:true});})();</script>')

# ---------------------------------------------------------------- head: meta, OG, JSON-LD
DESC = ('Free BMI calculator for adults: your BMI, category and healthy weight for your height in pounds or kilograms, '
        'plus where you rank among US adults (CDC data).')
assert len(DESC) <= 160, len(DESC)
OG_T = 'BMI Calculator: your BMI and where you rank among US adults'
OG_D = 'Your BMI, the healthy weight for your height and your rank among US adults, from CDC measurements of 5,929 adults (2021–2023).'
TW_D = 'Your BMI, the healthy weight for your height and your rank among US adults (CDC, 2021–2023).'
OG_IMG = 'https://calculatemybmi.net/assets/images/og/home-bmi-us-adults.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG_IMG}">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{TW_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG_IMG}">', src)

m = re.search(r'(?s)<script type="application/ld\+json">(.*?)</script>', src)
ld = json.loads(m.group(1))
g = ld['@graph']
types = [x['@type'] for x in g]
assert types == ['WebSite', 'WebApplication', 'Organization', 'FAQPage'], types
g[0].pop('potentialAction')                          # the site has no search; the SearchAction target was the homepage
g[1] = {
    '@type': 'WebApplication', '@id': 'https://calculatemybmi.net/#calculator', 'name': 'BMI Calculator',
    'description': ('Calculates BMI from height and weight in pounds and inches or kilograms and centimeters, gives the CDC '
                    'adult category and the healthy weight range for the height, and ranks the result among US adults, men '
                    'and women using CDC NHANES August 2021–August 2023 measurements.'),
    'url': 'https://calculatemybmi.net/', 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any',
    'browserRequirements': 'Requires JavaScript', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
    'featureList': ['BMI from US or metric units', 'CDC adult BMI category',
                    'Healthy weight range for your height in pounds and kilograms',
                    'Rank among US adults, men and women (CDC NHANES 2021–2023)', 'Weight milestones and what-if table'],
    'author': g[1]['author'],
}
g[3] = {'@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
src = src[:m.start(1)] + json.dumps(ld, ensure_ascii=False) + src[m.end(1):]

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
calc_tag = '<script src="/assets/js/calculator.js"></script>'
assert src.count(calc_tag) == 1
src = src.replace(calc_tag, calc_tag + ' ' + rank_js)

open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(main).split())
print(f'index.html written: {len(src):,} bytes, {words:,} words in <main>, {len(FAQ)} FAQ, {len(TEXTS)} SVG labels checked')
