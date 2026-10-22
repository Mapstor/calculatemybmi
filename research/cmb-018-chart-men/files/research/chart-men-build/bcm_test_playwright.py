#!/usr/bin/env python3
"""BMI chart for men checks in Chromium (CMB-018). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/chart-men-build/bcm_test_playwright.py http://localhost:8000 research/chart-men-build/bcm_stats.json
  - chart table: all 102 cells (5'2" to 6'6", six categories) equal the whole-pound and whole-kilogram limits found here by
    brute force (each unit on its own, BMI rounded to one decimal), not by the gate's rule that gen_bcm.py uses; every row
    has its #h-F-I anchor and its centimeters;
  - printable chart: bcm_grid.csv (the values drawn in the image) equals the brute-force BMI at every height and weight; the
    image loads at 1640 x 1628 once scrolled to, has alt text, links to itself and is in the image sitemap;
  - the by-height table (5'4" to 6'2"): brute-force healthy limits, the /average-weight/ means, the BMI 25+ shares;
  - the 5'10" table: BMI, category and "US men with a higher BMI" worked out here (the homepage's men's curve, the rank
    rule: 100 - percentile, Math.round, capped at 99) plus typed-in values; the age and waist tables equal bcm_stats.json;
  - the hero: every row's bands equal the brute-force limits, the bar spans the 25th to 75th percentile weight and the tick
    sits on the median (drawn positions checked), and in every row the median is above the healthy range; the body-fat box
    plot is drawn at bcm_dxa.json's percentiles, which equal the body fat chart's (bfpc_stats.json); descriptions and hover
    labels carry the same numbers;
  - the prose figures: each sentence that states a number is rebuilt here from the stats files and found on the page;
  - head: title, description, one robots max-image-preview:large, canonical, og:image and twitter:image = the 16:9 preferred
    image (1200 x 675) with its alt, the Article image list and primaryImageOfPage, author named, preferred files at size;
    dateModified = the sitemap lastmod; no {TODAY} left;
  - every internal link answers 200 and every outside link is a registry URL; every contents chip lands on its section;
    every FAQ opens with one tap; the FAQ JSON-LD equals the visible answers;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px; every table fits its frame at 390 and 1280 except
    the chart table on phones, which scrolls inside its frame; rendered SVG labels don't overlap, stay inside their figure
    and sit on no shape; no JavaScript error."""
import sys, os, json, math, re, csv, struct
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(stats))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
S = json.load(open(stats))
X = json.load(open(os.path.join(HERE, 'bcm_dxa.json')))
HOME = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
AVGW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json')))
BFP = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
REG_URLS = set()                                                          # a registry row's url, endpoint or a link in its notes
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ')} | set(re.findall(r'https?://[^\s;,)"]+', r['notes']))
URL = base + '/blog/bmi-chart-men/'
SITE = 'https://calculatemybmi.net'
C, BH, DX = S['categories'], S['by_height'], X['by_cat']

def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def f1(x): return f'{x:.1f}'
def whole(x): return int(math.floor(x + 0.5))
def ft(h): return f'{h // 12}′{h % 12}″'
def cm1(h): return str((Decimal(h) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))
def kg_of(lb): return str((Decimal(lb) * Decimal('0.45359237')).quantize(Decimal('0.1'), ROUND_HALF_UP))   # exact lb
def spoken(h): return {64: '5 feet 4 inches', 65: '5 feet 5 inches', 66: '5 feet 6 inches', 67: '5 feet 7 inches',
                        68: '5 feet 8 inches', 69: '5 feet 9 inches', 70: '5 feet 10 inches', 71: '5 feet 11 inches',
                        72: '6 feet', 73: '6 feet 1 inch', 74: '6 feet 2 inches'}[h]          # typed out, not computed
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def share(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{x:.1f}%'
BANDS = [(0, 18.4), (18.5, 24.9), (25.0, 29.9), (30.0, 34.9), (35.0, 39.9), (40.0, 99)]
NAMES = ['Underweight', 'Healthy weight', 'Overweight', 'Class 1 obesity', 'Class 2 obesity', 'Class 3 obesity']

def brute(h_in, lo, hi, unit):
    m = h_in * 0.0254
    ws = [w for w in range(10, 700) if lo <= r1(w * 703 / h_in ** 2 if unit == 'lb' else w / m ** 2) <= hi]
    return ws[0], ws[-1]
def band_of(b): return next(i for i, (lo, hi) in enumerate(BANDS) if lo <= b <= hi)
def want_cell(h, band):
    lb, kg = brute(h, *BANDS[band], 'lb'), brute(h, *BANDS[band], 'kg')
    if band == 0: return f'≤ {lb[1]} lb ({kg[1]} kg)'
    if band == 5: return f'≥ {lb[0]} lb ({kg[0]} kg)'
    return f'{lb[0]}–{lb[1]} lb ({kg[0]}–{kg[1]} kg)'
QM = HOME['men']['p1_p99']
def pct_curve(q, b):
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
def higher(b):
    x = 100 - pct_curve(QM, b)
    return 99 if x > 99 else whole(x)

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# ---- 1. The printable chart's values (chart_bcm.py draws the image from bcm_grid.csv).
rows = list(csv.reader(open(os.path.join(HERE, 'bcm_grid.csv'))))
weights = [int(c.split()[0]) for c in rows[0][2:]]
ok(weights == list(range(100, 301, 10)), f'grid weights {weights}')
ok(len(rows) == 18, f'{len(rows) - 1} grid rows')
for r in rows[1:]:
    m = re.match(r"(\d)'(\d{1,2})\"", r[0]); h = int(m.group(1)) * 12 + int(m.group(2))
    ok(r[1] == cm1(h), f'grid cm {r[0]}')
    for lb, v in zip(weights, r[2:]):
        ok(v == f'{r1(lb * 703 / h ** 2):.1f}', f'grid {r[0]} {lb} lb: {v}')
ok([re.match(r"(\d)'(\d{1,2})", r[0]).groups() for r in rows[1:]] == [(str(h // 12), str(h % 12)) for h in range(62, 79)], 'grid heights')
# Typed in: 5'10" 170 lb 24.4, 180 lb 25.8, 210 lb 30.1; 6'6" 150 lb 17.3; 5'2" 300 lb 54.9.
G = {r[0]: r[2:] for r in rows[1:]}
ok((G['5\'10"'][7], G['5\'10"'][8], G['5\'10"'][11], G['6\'6"'][5], G['5\'2"'][20]) == ('24.4', '25.8', '30.1', '17.3', '54.9'), 'grid typed-in values')

# ---- 2. The numbers the page states, rebuilt from the stats files.
def p(g, c): return C[g][c]['pct']
AGES = ('20-39', '40-59', '60+')
DIF = S['age_differences']
for k in ('healthy_20-39_minus_40-59', 'healthy_20-39_minus_60+', 'obesity_40-59_minus_20-39', 'obesity_40-59_minus_60+',
          'class_3_40-59_minus_20-39', 'class_3_40-59_minus_60+', 'overweight_60+_minus_40-59'):
    ok(DIF[k]['diff'] > 0 and DIF[k]['ci95'][0] > 0, f'stated age difference {k} not clear of zero')
HH = range(64, 75)
for h in HH:
    ok(BH[str(h)]['bmi25_plus']['ci95'][0] > 50, f'{ft(h)}: "most men" not clear of half')
    ok(BH[str(h)]['weight_q'][1] > brute(h, 18.5, 24.9, 'lb')[1], f'{ft(h)}: median not above the healthy range')
lo25, hi25 = min(BH[str(h)]['bmi25_plus']['pct'] for h in HH), max(BH[str(h)]['bmi25_plus']['pct'] for h in HH)
half = max((C[g][c]['ci95'][1] - C[g][c]['ci95'][0]) / 2 for g in ('all',) + AGES
           for c in ('underweight', 'healthy', 'overweight', 'obesity', 'class_3'))
A70 = S['at_70in']; WB = S['waist']['by_bmi']; ADA = S['ada2026']; DIS = X['disagree']
b70, b72, b69 = brute(70, 18.5, 24.9, 'lb'), brute(72, 18.5, 24.9, 'lb'), brute(69, 18.5, 24.9, 'lb')
k70, k72, k69 = brute(70, 18.5, 24.9, 'kg'), brute(72, 18.5, 24.9, 'kg'), brute(69, 18.5, 24.9, 'kg')
med_m = HOME['men']['table']['p50']
for k in ('healthy', 'over', 'obese'):                                     # the body fat chart's numbers, unchanged
    for q in ('n', 'p10', 'p25', 'p50', 'p75', 'p90'):
        ok(DX[k][q] == BFP['bmi']['by_cat']['m'][k][q], f'DXA {k} {q} differs from bfpc_stats.json')
ok(round(204 / 2.54, 1) == 80.3 and ft(int(204 / 2.54)) == '6′8″', '204 cm')
PROSE = [
    f'Only {f1(p("all", "healthy"))}% of US men have a BMI in CDC’s healthy range of 18.5 to 24.9',
    f'{f1(ADA["obesity_ada"]["pct"])}% of US men meet its new thresholds for obesity, against '
    f'{f1(ADA["obesity_bmi_only"]["pct"])}% of the same {ADA["n"]:,} men by BMI alone',
    f'against {f1(ADA["obesity_bmi_only"]["pct"])}% of the same {ADA["n"]:,} men by BMI alone (our calculation; the '
    f'{ADA["n_left_out"]} men whose class depends on a waist that wasn’t measured are left out)',
    f'measured BMI, waist and height ({ADA["n"]:,} men); 95% confidence interval',
    f'The ADA comparison leaves out the {ADA["n_left_out"]} men whose class depends on a waist that wasn’t measured',
    'or a waist of 102 cm (40 in) or more. For men of Asian background the lines are a BMI of 27.5, or 23 with the same '
    'ratio or a waist of 90 cm (35.5 in)',
    'at least half the height or 102 cm (40 in) or more, with lower lines for men of Asian background',
    'NHLBI gives the men’s waist line as over 102 cm (over 40 in) and the ADA as 102 cm or more (40 in or more in its '
    'Table 3.1)',
    f'men without a valid scan are left out ({f1(X["missing_scan"]["healthy"]["pct"])}% of men with a healthy BMI, '
    f'{f1(X["missing_scan"]["over"]["pct"])}% with an overweight BMI and {f1(X["missing_scan"]["obese"]["pct"])}% with obesity)',
    'Most men with an overweight BMI carry more body fat than the typical man with a healthy BMI. On CDC’s body scans '
    '(2011–2018), only',
    f'At 5′10″, the healthy weight is {b70[0]} to {b70[1]} lb ({k70[0]} to {k70[1]} kg); at 6′0″, {b72[0]} to {b72[1]} lb '
    f'({k72[0]} to {k72[1]} kg).',
    f'{f1(p("all", "healthy"))}% of US men have a healthy BMI and {f1(p("all", "obesity"))}% have obesity',
    f'only {f1(DIS["over_at_or_below_healthy_median"]["pct"])}% of men aged 20 to 59 with a BMI of 25 to 29.9 carried no more '
    'body fat than the median man with a healthy BMI',
    f'The healthy weight runs from {brute(62, 18.5, 24.9, "lb")[0]} to {brute(62, 18.5, 24.9, "lb")[1]} lb at 5′2″ to '
    f'{brute(78, 18.5, 24.9, "lb")[0]} to {brute(78, 18.5, 24.9, "lb")[1]} lb at 6′6″.',
    f'At 5′10″ (177.8 cm), a healthy weight is {b70[0]} to {b70[1]} lb ({k70[0]} to {k70[1]} kg), a BMI of 18.5 to 24.9. '
    f'Overweight runs from {brute(70, 25, 29.9, "lb")[0]} to {brute(70, 25, 29.9, "lb")[1]} lb ({brute(70, 25, 29.9, "kg")[0]} '
    f'to {brute(70, 25, 29.9, "kg")[1]} kg), and obesity starts at {brute(70, 30, 99, "lb")[0]} lb ({brute(70, 30, 99, "kg")[0]} kg).',
    f'{f1(A70["healthy"]["pct"])}% have a healthy BMI, {f1(A70["overweight"]["pct"])}% are overweight and '
    f'{f1(A70["obesity"]["pct"])}% have obesity. Their average weight is {f1(BH["70"]["weight_mean"])} lb and their median '
    f'{f1(BH["70"]["weight_q"][1])} lb (our calculation from CDC measurements, {BH["70"]["n"]} men, 2021–2023',
    f'its 5′10″ row reads 132 lb under BMI 19 and 167 lb under 24 (NIH); CDC’s healthy range starts at 18.5, which is {b70[0]} lb.',
    f'which by BMI runs from {f1(r1(170 * 703 / 4900))}, healthy, to {f1(r1(185 * 703 / 4900))}, overweight.',
    f'185 lb at 5′10″ is 185 × 703 ÷ 70² = {f1(r1(185 * 703 / 4900))}, rounded to one decimal: overweight, {185 - b70[1]} lb above',
    f'{f1(p("all", "overweight"))}% are overweight and {f1(p("all", "obesity"))}% have obesity, including '
    f'{f1(p("all", "class_3"))}% with a BMI of 40 or more; {f1(p("all", "underweight"))}% are underweight. The median US man has '
    f'a BMI of {f1(med_m)}, in the overweight range',
    f'between {whole(lo25)}% and {whole(hi25)}% of men have a BMI of 25 or more, and both the median and the average man weigh '
    'more than the healthy range allows',
    f'({min(BH[str(h)]["n"] for h in HH)} to {max(BH[str(h)]["n"] for h in HH)} men per height; survey-weighted)',
    f'Men aged 20 to 39 are the most likely to have a healthy BMI, at {f1(p("20-39", "healthy"))}%, compared with '
    f'{f1(p("40-59", "healthy"))}% at 40 to 59 and {f1(p("60+", "healthy"))}% at 60 and over.',
    f'Obesity peaks at 40 to 59 ({f1(p("40-59", "obesity"))}%, against {f1(p("20-39", "obesity"))}% at 20 to 39 and '
    f'{f1(p("60+", "obesity"))}% at 60 and over), and so does a BMI of 40 or more ({f1(p("40-59", "class_3"))}%).',
    f'Men 60 and over are more often overweight than men aged 40 to 59 ({f1(p("60+", "overweight"))}% against '
    f'{f1(p("40-59", "overweight"))}%).',
    f'({C["all"]["n"]:,} men aged 20 and over: {C["20-39"]["n"]:,} aged 20 to 39, {C["40-59"]["n"]:,} aged 40 to 59 and '
    f'{C["60+"]["n"]:,} aged 60 and over; survey-weighted)',
    f'{f1(p("20-39", "underweight"))}%, {f1(p("40-59", "underweight"))}% and {f1(p("60+", "underweight"))}% by age',
    f'Each share has a 95% margin of error of up to ±{whole(half)} points',
    f'The median man with a healthy BMI carried {f1(DX["healthy"]["p50"])}% body fat, with an overweight BMI '
    f'{f1(DX["over"]["p50"])}% and with obesity {f1(DX["obese"]["p50"])}%.',
    f'Only {f1(DIS["over_at_or_below_healthy_median"]["pct"])}% of men with an overweight BMI carried no more body fat than the '
    f'median man with a healthy BMI, and {f1(DIS["obese_at_or_below_healthy_median"]["pct"])}% of men with obesity.',
    f'{f1(DIS["healthy_at_or_above_over_median"]["pct"])}% of men with a healthy BMI carried at least as much body fat as the '
    'median man with an overweight BMI',
    'it is under 102 cm for anyone shorter than 204 cm, about 6′8″.',
    f'At an overweight BMI, {f1(WB["overweight"]["whtr_05_plus"]["pct"])}% of US men have a waist at least half their height, '
    f'but only {f1(WB["overweight"]["waist_102_plus"]["pct"])}% reach 102 cm; at a healthy BMI, '
    f'{f1(WB["healthy"]["whtr_05_plus"]["pct"])}% and {f1(WB["healthy"]["waist_102_plus"]["pct"])}% (our calculation, '
    f'{S["waist"]["n_measured"]:,} men with a measured waist)',
    f'of US men meet the 2026 ADA obesity thresholds, against {f1(ADA["obesity_bmi_only"]["pct"])}% of the same '
    f'{ADA["n"]:,} men by BMI alone.',
    f'95% confidence interval {f1(ADA["obesity_ada"]["ci95"][0])}% to {f1(ADA["obesity_ada"]["ci95"][1])}%',
    f'95% confidence interval {f1(C["all"]["healthy"]["ci95"][0])}% to {f1(C["all"]["healthy"]["ci95"][1])}%',
    f'Most of the gap, {f1(ADA["parts_pts"]["nonasian_25_29_9"])} points, comes from men of non-Asian background with a BMI of '
    f'25 to 29.9: {f1(ADA["bmi25_30_nonasian_central"]["pct"])}% of them',
    f'So a 70-year-old man of 5′9″ has the same healthy range as a 30-year-old: {b69[0]} to {b69[1]} lb ({k69[0]} to '
    f'{k69[1]} kg). US men aged 70 to 79 have an average BMI of {f1(AVGW["men"]["age"]["70–79"]["bmi"]["mean"])}',
    f'At 5′10″, 170 lb is a BMI of {f1(r1(170 * 703 / 4900))}, inside the healthy range for that height, {b70[0]} to {b70[1]} lb',
    f'180 lb at 5′10″ is a BMI of {f1(r1(180 * 703 / 4900))}, and the healthy range ends at {b70[1]} lb.',
    f'At 5′10″, 215 lb is a BMI of {f1(r1(215 * 703 / 4900))}, which CDC calls class 1 obesity (30 to 34.9)',
    f'At 5′10″, 140 lb is a BMI of {f1(r1(140 * 703 / 4900))}, in the healthy range; underweight starts below {b70[0]} lb',
    f'About {higher(r1(140 * 703 / 4900))}% of US men have a higher BMI',
    f'At 6′0″ (182.9 cm), a healthy weight is {b72[0]} to {b72[1]} lb ({k72[0]} to {k72[1]} kg). Overweight runs from '
    f'{brute(72, 25, 29.9, "lb")[0]} to {brute(72, 25, 29.9, "lb")[1]} lb and obesity starts at {brute(72, 30, 99, "lb")[0]} lb. '
    f'The average US man of that height weighs {f1(AVGW["men"]["height"]["72"]["wt"]["mean"])} lb',
    'at 5′10″, a waist of 35 inches is half the height',
    'In 3.95 million never-smokers without certain chronic diseases at the start',
    'the risk was 52% higher for BMI measured at ages 35 to 49 and 21% higher at 70 to 89',
    'the rise was steeper in men than in women (51% against 30%',
]

with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    html_ = pg.content()
    ok('{TODAY}' not in html_, '{TODAY} placeholder left in the page')
    body = re.sub(r'\s+', ' ', pg.inner_text('main') + ' ' + ' '.join(pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')))
    for s in PROSE:
        ok(s in body, f'prose not found: {s!r}')
    for s in ('40.2 in', '35.4 in', 'aren’t just muscle', 'BMI from muscle', 'without a chronic disease', '6 feet 0 inches', '6 feet 1 inches'):
        ok(s not in html_, f'fact-check fix undone: {s!r} on the page')       # CMB-018 fact-check (F1, N8, N11, N13)
    ok(re.findall(r'<th scope="col"[^>]*>([^<]*higher BMI)</th>', html_) == ['All US men with a higher BMI'], 'rank column header')

    # ---- 3. Tables.
    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [r.id, ...[...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim())])])""")
    tb = {cap: rws for cap, rws in tables}
    ok(len(tables) == 5, f'{len(tables)} tables')
    byh = tb.get('US men by height: healthy weight and average weight', [])
    want = [['', ft(h), f'{brute(h, 18.5, 24.9, "lb")[0]}–{brute(h, 18.5, 24.9, "lb")[1]}', f'{f1(BH[str(h)]["weight_mean"])}',
             f'{f1(BH[str(h)]["bmi25_plus"]["pct"])}%'] for h in HH]
    ok(byh == want, f'by-height table {byh} vs {want}')
    for h in HH:                                                           # the /average-weight/ means, above the healthy range
        ok(f1(AVGW['men']['height'][str(h)]['wt']['mean']) == f1(BH[str(h)]['weight_mean']), f'{ft(h)} average differs from avgw')
        ok(BH[str(h)]['weight_mean'] > brute(h, 18.5, 24.9, 'lb')[1], f'{ft(h)}: average not above the healthy range')
    ok(len(byh) == 11 and byh[7][1:] == ['5′11″', '133–178', '215.1', '80.1%'], f'5′11″ row typed in {byh[7] if len(byh) > 7 else None}')
    chart = tb.get('BMI chart for men, 5′2″ to 6′6″', [])
    ok(len(chart) == 17, f'{len(chart)} chart rows')
    for row, h in zip(chart, range(62, 79)):
        ok(row[0] == f'h-{h // 12}-{h % 12}' and row[1] == f'{ft(h)} ({cm1(h)} cm)', f'chart row head {row[:2]}')
        for band in range(6):
            ok(row[2 + band] == want_cell(h, band), f'{ft(h)} band {band}: {row[2 + band]!r} vs {want_cell(h, band)!r}')
    ten = tb.get('Weights at 5′10″: BMI and category', [])
    W70 = (140, 150, 160, 170, 180, 185, 190, 200, 210, 215, 230)
    want = [['', f'{w} lb ({kg_of(w)} kg)', f1(r1(w * 703 / 4900)), NAMES[band_of(r1(w * 703 / 4900))],
             f'{higher(r1(w * 703 / 4900))}%'] for w in W70]
    ok(ten == want, f'5′10″ table {ten} vs {want}')
    typed = [(r[1].split(' ')[0], r[2], r[3], r[4]) for r in ten]          # worked out by hand
    ok(typed[:5] == [('140', '20.1', 'Healthy weight', '96%'), ('150', '21.5', 'Healthy weight', '93%'),
                     ('160', '23.0', 'Healthy weight', '87%'), ('170', '24.4', 'Healthy weight', '79%'),
                     ('180', '25.8', 'Overweight', '68%')] and typed[8][1:3] == ('30.1', 'Class 1 obesity'), f'typed {typed}')
    age = tb.get('US men by BMI category and age (%)', [])
    want = [['', lab] + [f'{f1(p(g, c))}%' for c in ('healthy', 'overweight', 'obesity', 'class_3')]
            for g, lab in (('20-39', '20–39'), ('40-59', '40–59'), ('60+', '60+'), ('all', 'All 20+'))]
    ok(age == want, f'age table {age} vs {want}')
    ok([r[2:] for r in age][1] == ['20.7%', '33.5%', '45.4%', '9.2%'], 'age table typed-in 40–59 row (NCHS: 45.4, 9.2)')
    wst = tb.get('US men with a large waist, by BMI category (%)', [])
    want = [['', f'{lab} BMI {rng}', share(WB[c]['waist_102_plus']['pct']), share(WB[c]['whtr_05_plus']['pct'])]
            for c, lab, rng in (('healthy', 'Healthy weight', '18.5–24.9'), ('overweight', 'Overweight', '25–29.9'),
                                ('obesity', 'Obesity', '30 or more'))]
    ok(wst == want, f'waist table {wst} vs {want}')
    ok(wst and wst[2][3] == 'more than 99%', 'waist table: 100.0 prints as "more than 99%"')

    # ---- 4. Figures: drawn positions, descriptions, hover labels.
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => ({id: s.getAttribute('aria-labelledby'),
        desc: (s.querySelector('desc') || {}).textContent, texts: [...s.querySelectorAll('text')].map(e => e.textContent),
        rects: [...s.querySelectorAll('rect')].map(r => [r.querySelector('title') ? r.querySelector('title').textContent : '',
            +r.getAttribute('x'), +r.getAttribute('y'), +r.getAttribute('width'), +r.getAttribute('height'), r.getAttribute('fill')]),
        lines: [...s.querySelectorAll('line')].map(l => [+l.getAttribute('x1'), +l.getAttribute('x2'), l.getAttribute('stroke-dasharray')])}))""")
    ok([f['id'] for f in figs] == ['fig-hero-t fig-hero-d', 'fig-fat-t fig-fat-d'], f'figures {[f["id"] for f in figs]}')
    hero, fat = figs[0], figs[1]
    def hx(lb): return 46 + (min(max(lb, 100), 260) - 100) * 266 / 160
    ok([t for t in hero['texts'] if re.fullmatch(r"\d′\d{1,2}″", t)] == [ft(h) for h in HH], 'hero height labels')
    for i, h in enumerate(HH):
        y = 56 + 20 * i; q = BH[str(h)]['weight_q']
        hl = brute(h, 18.5, 24.9, 'lb'); ov = brute(h, 25, 29.9, 'lb')
        bands = [r for r in hero['rects'] if r[0].startswith(f'{ft(h)}, ')]
        ok([r[0] for r in bands] == [f'{ft(h)}, underweight: ≤ {hl[0] - 1} lb', f'{ft(h)}, healthy weight: {hl[0]}–{hl[1]} lb',
                                     f'{ft(h)}, overweight: {ov[0]}–{ov[1]} lb', f'{ft(h)}, obesity: ≥ {ov[1] + 1} lb'],
           f'hero bands {ft(h)}: {[r[0] for r in bands]}')
        if len(bands) == 4:
            hb_ = bands[1]
            ok(abs(hb_[1] - (hx(hl[0] - 0.5) + 0.5)) < 0.06 and abs(hb_[1] + hb_[3] - (hx(hl[1] + 0.5) - 0.5)) < 0.11, f'hero healthy band drawn {ft(h)}')
        mid = [r for r in hero['rects'] if r[0].startswith(f'US men at {ft(h)}:')]
        ok(len(mid) == 1 and mid[0][0] == f'US men at {ft(h)}: middle half {f1(q[0])}–{f1(q[2])} lb, median {f1(q[1])} lb '
                                             f'({BH[str(h)]["weight_n"]} men)', f'hero bar label {ft(h)}')
        if mid:
            ok(abs(mid[0][1] - hx(q[0])) < 0.06 and abs(mid[0][1] + mid[0][3] - hx(q[2])) < 0.11 and abs(mid[0][2] - (y + 4)) < 0.06,
               f'hero bar drawn {ft(h)}: {mid[0][1:5]}')
        tick = [r for r in hero['rects'] if not r[0] and r[5] == '#111827' and abs(r[2] - (y - 1)) < 0.06]
        ok(len(tick) == 1 and abs(tick[0][1] + 1.5 - hx(q[1])) < 0.06, f'hero tick {ft(h)}')
        ok(f'{spoken(h)}: healthy {hl[0]} to {hl[1]} pounds; US men’s median {f1(q[1])} pounds, middle half '
           f'{f1(q[0])} to {f1(q[2])}.' in hero['desc'], f'hero desc {ft(h)}')
    def fx(v): return 20 + (v - 10) * 280 / 30
    labs = {'healthy': 'Healthy BMI, 18.5–24.9', 'over': 'Overweight, 25–29.9', 'obese': 'Obesity, 30 or more'}
    boxes = [r for r in fat['rects'] if r[0]]
    ok(len(boxes) == 3, f'{len(boxes)} boxes')
    for (k, lab), bx in zip(labs.items(), boxes):
        v = DX[k]
        ok(f'{lab}: median {f1(v["p50"])}%' in fat['texts'], f'fat label {k}')
        ok(bx[0] == f'{lab}: 10th to 90th percentile {f1(v["p10"])}%–{f1(v["p90"])}%, middle half {f1(v["p25"])}%–'
                    f'{f1(v["p75"])}%, median {f1(v["p50"])}% ({v["n"]:,} men)', f'fat hover {k}: {bx[0]!r}')
        ok(abs(bx[1] - fx(v['p25'])) < 0.06 and abs(bx[1] + bx[3] - fx(v['p75'])) < 0.11, f'fat box drawn {k}')
        ok(any(abs(r[1] + 1.5 - fx(v['p50'])) < 0.06 and r[5] == '#111827' and abs(r[2] - (bx[2] - 2)) < 0.06 for r in fat['rects']), f'fat tick {k}')
        ok(any(abs(l[0] - fx(v['p10'])) < 0.06 and abs(l[1] - fx(v['p90'])) < 0.06 for l in fat['lines']), f'fat whisker {k}')
        ok(f'{lab}: median {f1(v["p50"])}%, middle half {f1(v["p25"])}% to {f1(v["p75"])}%, 10th to 90th percentile '
           f'{f1(v["p10"])}% to {f1(v["p90"])}%.' in fat['desc'], f'fat desc {k}')
    dashed = [l for l in fat['lines'] if l[2]]
    ok(len(dashed) == 3 and all(abs(l[0] - fx(DX['healthy']['p50'])) < 0.06 for l in dashed), 'fat reference line')

    # ---- 5. The printable chart image and the image sitemap.
    img = pg.evaluate("""() => { const i = document.querySelector('main figure img'); const a = i.closest('a');
        return [i.getAttribute('src'), i.getAttribute('alt'), +i.getAttribute('width'), +i.getAttribute('height'), a && a.getAttribute('href'), i.getAttribute('loading')]; }""")
    ok(img[0] == '/assets/images/charts/bmi-chart-men.png' and img[4] == img[0], f'chart image link {img}')
    ok(img[1].startswith('Printable BMI chart for men') and 'every 10 pounds from 100 to 300 pounds' in img[1], f'chart alt {img[1]!r}')
    ok((img[2], img[3], img[5]) == (1640, 1628, 'lazy'), f'chart size attributes {img}')
    res = pg.request.get(base + img[0]); ok(res.status == 200 and png_size(res.body()) == (1640, 1628), 'chart file size')
    pg.evaluate("document.querySelector('main figure img').scrollIntoView()"); pg.wait_for_timeout(600)
    ok(pg.evaluate("document.querySelector('main figure img').naturalWidth") == 1640, 'chart image did not load after scrolling')
    sm = pg.request.get(base + '/sitemap.xml').text()
    ent = re.search(r'<url><loc>https://calculatemybmi\.net/blog/bmi-chart-men/</loc>(.*?)</url>', sm)
    ok(bool(ent) and '<image:loc>https://calculatemybmi.net/assets/images/charts/bmi-chart-men.png</image:loc>' in ent.group(1),
       'image sitemap entry')
    lastmod = re.search(r'<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>', ent.group(1)).group(1) if ent else None

    # ---- 6. Head and JSON-LD.
    head = pg.evaluate("""() => ({title: document.title, desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content),
        canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content),
        ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        ogt: document.querySelector('meta[property="og:title"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content)})""")
    P = {r: f'{SITE}/assets/images/preferred/bmi-chart-men-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['title'] == 'BMI Chart for Men: Healthy Weight by Height (lb and kg)', f'title {head["title"]!r}')
    ok(len(head['desc']) <= 160 and head['desc'].startswith('The BMI chart for men from 5′2″ to 6′6″'), f'description {head["desc"]!r}')
    ok(head['robots'] == ['max-image-preview:large'], f'robots {head["robots"]}')
    ok(head['canon'] == SITE + '/blog/bmi-chart-men/', f'canonical {head["canon"]}')
    ok(head['og'] == [P['16x9']] and head['tw'] == [P['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter {head}')
    ok(head['ogalt'].startswith('Chart: for each height') and 'underweight, healthy, overweight and obesity' in head['ogalt'],
       f'og:image:alt {head["ogalt"]!r}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/bmi-chart-men-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok([x['@type'] for x in ld] == ['Article', 'BreadcrumbList', 'FAQPage'], f'JSON-LD types {[x["@type"] for x in ld]}')
    L = {x['@type']: x for x in ld}
    art = L.get('Article', {})
    ok(art.get('headline') == pg.inner_text('h1') == 'BMI Chart for Men: Healthy Weight by Height', 'Article headline is not the H1')
    ok(art.get('image') == [P['1x1'], P['4x3'], P['16x9']], f'Article image list {art.get("image")}')
    ok(art.get('mainEntityOfPage', {}).get('primaryImageOfPage', {}).get('url') == P['16x9'], 'primaryImageOfPage')
    ok(art.get('author', {}).get('name') == 'Marko Visic' and art.get('datePublished') == '2026-01-28', 'author / datePublished')
    ok(re.fullmatch(r'\d{4}-\d{2}-\d{2}', art.get('dateModified', '')) is not None and art.get('dateModified') == lastmod,
       f'dateModified {art.get("dateModified")!r} vs sitemap lastmod {lastmod!r}')
    ok(L.get('BreadcrumbList', {}).get('itemListElement', [{}])[-1].get('name') == pg.inner_text('h1'), 'breadcrumb name is not the H1')
    vis = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok(len(vis) == 12 and [[q['name'], q['acceptedAnswer']['text']] for q in L.get('FAQPage', {}).get('mainEntity', [])] == vis,
       'FAQ JSON-LD differs from the visible answers')

    # ---- 7. Links, chips, FAQ.
    hrefs = pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for h_ in sorted({h_.split('#')[0] for h_ in hrefs if h_.startswith('/')}):
        ok(pg.request.get(base + h_).status == 200, f'internal link {h_} does not answer 200')
    for h_ in {h_ for h_ in hrefs if h_.startswith('#')}:
        ok(pg.evaluate('h => !!document.getElementById(h.slice(1))', h_), f'anchor {h_} missing')
    outside = {h_ for h_ in pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))')}
    ok(outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#chart', '#five-ten', '#us-men', '#muscle', '#waist', '#age', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    qs = pg.query_selector_all('.faq-question')
    for i, q in enumerate(qs):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
        ok(pg.evaluate('i => document.querySelectorAll(".faq-answer")[i].getBoundingClientRect().height > 20', i), f'FAQ {i} answer not shown')
    ok(pg.evaluate("() => { location.hash = '#h-5-10'; return !!document.getElementById('h-5-10'); }"), 'row anchor #h-5-10')

    # ---- 8. Widths, table frames, rendered labels.
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("""() => [...document.querySelectorAll('main .table-responsive > table')].map(t => [t.caption ? t.caption.textContent : '',
            t.offsetWidth, t.parentElement.clientWidth, getComputedStyle(t.parentElement).overflowX])""")
        for cap, tw, fw, ov in fits:
            ok(ov == 'auto', f'{cap}: frame does not scroll')
            if w in (390, 1280) and not (cap.startswith('BMI chart for men') and w == 390):
                ok(tw <= fw + 1, f'table scrolls at {w}: {cap} {tw} > {fw}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom],
                        texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                        shapes: [...svg.querySelectorAll('rect')].map(e => [e.getAttribute('fill'), ...bx(e)])}; })""")
            ok(len(res) == 2, f'{len(res)} figures at {w}')
            for f in res:
                L_, T_, R_, B_ = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s in f['shapes']:
                        if a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5:
                            fails.append(f'{w}px label over a shape: {a[0]!r} / {s[0]}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
sys.exit(1 if fails else 0)
