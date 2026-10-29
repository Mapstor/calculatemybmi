#!/usr/bin/env python3
"""How-to-measure guide checks in Chromium (CMB-021). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/how-to-measure-body-fat-build/htm_test_playwright.py http://localhost:8000 research/how-to-measure-body-fat-build/htm_stats.json
  - typed-in values: Burns et al. 2019 Table 3 (all seven rows, the margin, the sample) against burns_2019_table3.json;
    the check on CDC's scans (average miss 10.4% / 14.0%, by sex and at 20-29; the formulas more than 5 points apart for
    38% / 15%; the slips) against htm_stats.json; bfc_stats.json's within-5 shares; the chart's ranges and medians;
  - the equations, written again here: the worked example (18.5 / 20.4 / 24.0 / 26.2%, density 1.0565, BMI 25.8) and the
    tape and caliper slips;
  - the prose: each sentence that states a number is rebuilt here from those values and found on the page; removed
    wording stays removed;
  - tables: the seven-method table and the measuring-slip table (its groups and rows) equal the values; the figures: the
    hero's dots, interval lines and dashed zero lines, and the formula-gap bars, at their drawn positions, with titles
    and descriptions carrying the numbers;
  - head: title, description, robots, canonical, og:image and twitter:image = the 16:9 preferred image with its alt,
    twitter title and description, the Article image list, primaryImageOfPage and dateModified = sitemap lastmod,
    datePublished kept, author and publisher named, preferred files at size, old OG image gone, no {TODAY}, no
    page-level style, no <article>, no inline style outside figures; the menu marks Guides, in both menus, and nothing else;
  - every internal link answers 200 and every outside link is a registry URL; chips land on their sections; every FAQ
    opens; the FAQ JSON-LD equals the visible answers;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px and every table fits its frame; rendered SVG
    labels don't overlap, stay inside their figure and sit on no shape or line (an in-bar label sits wholly inside its bar);
    no JavaScript error."""
import sys, os, json, math, re, csv, struct
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
BUILD = os.path.dirname(os.path.abspath(stats))
ROOT = os.path.abspath(os.path.join(BUILD, '..', '..'))
S = json.load(open(stats))
T3 = json.load(open(os.path.join(BUILD, 'burns_2019_table3.json'), encoding='utf-8'))
C = json.load(open(os.path.join(ROOT, 'research/body-fat-calculator-build/bfc_stats.json')))
P = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()}
URL = base + '/blog/how-to-measure-body-fat/'
SITE = 'https://calculatemybmi.net'

def h1d(x): return str(Decimal(x).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))   # halves up, as toFixed
def h4d(x): return str(Decimal(x).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def sg(x): s = h1d(x); return ('−' + s[1:]) if s.startswith('-') else '+' + s
def pc(x): return int(Decimal(x).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def lg(x): return math.log(x) / math.log(10)
def norm(t): return re.sub(r'\s+', ' ', t.replace(' ', ' ')).strip()

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# ---- Burns et al. 2019, Table 3, typed in again from the paper (PMC6426203): DXA minus method, 90% CI, MAPE, equivalence
TYPED = [('hw', 'Underwater weighing', 1.0, 0.6, 1.4, 13.4, True, True), ('sf', 'Skinfolds, 7 sites', 1.4, 1.1, 1.7, 11.7, True, True),
         ('adp', 'Bod Pod', 1.6, 1.3, 1.9, 14.5, True, True), ('valhalla', 'Lab analyzer, 4 electrodes', 1.6, 1.1, 2.1, 17.0, True, True),
         ('tanita', 'Foot-to-foot scale', 3.5, 3.0, 4.0, 17.2, False, True), ('ir', 'Near-infrared', 4.2, 3.7, 4.7, 18.7, False, False),
         ('omron', 'Hand-held device', 4.9, 4.5, 5.3, 21.9, False, False)]
J = {r['key']: r for r in T3['rows']}
ok(sorted(J) == sorted(t[0] for t in TYPED), 'Table 3 rows')
for k, lab, d, lo, hi, m, e10, e15 in TYPED:
    r = J.get(k, {})
    ok((r.get('label'), r.get('diff'), r.get('ci90'), r.get('mape'), r.get('eq10'), r.get('eq15')) == (lab, d, [lo, hi], m, e10, e15), f'Table 3 {k}: {r}')
ok((T3['n'], T3['women'], T3['men'], T3['dxa_mean'], T3['margin']) == (437, 301, 136, 27.0, 2.7), 'Table 3 sample and margin')
ROWS = sorted(TYPED, key=lambda t: t[2])                                 # stable, as the page orders them
B = {t[0]: t for t in TYPED}

# ---- our calculation on CDC's scans (typed in from the chat run) and the stats files
M = S['mape']
ok(S['meta']['n_scanned_20_59'] == C['meta']['n_scanned_20_59'] == 10864 and S['meta']['df'] == 62, 'sample')
MP = {f: {s: h1d(M[f][s]['20-59']['mean']) for s in ('all', 'women', 'men')} for f in ('rfm', 'deur')}
ok(MP == {'rfm': {'all': '10.4', 'women': '9.9', 'men': '10.8'}, 'deur': {'all': '14.0', 'women': '12.0', 'men': '15.9'}}, f'MAPE {MP}')
ok((h1d(M['rfm']['all']['20-29']['mean']), h1d(M['deur']['all']['20-29']['mean'])) == ('10.7', '16.9'), 'MAPE 20-29')
ok(M['rfm']['all']['20-59']['ci95'][1] < M['deur']['all']['20-59']['ci95'][0], 'the two formulas\' MAPE intervals overlap')
ok([M[f]['all']['20-59']['n'] for f in ('rfm', 'deur')] == [10751, 10829], 'MAPE samples')
G = S['gap']
ok((pc(G['women']['over5']['pct']), pc(G['men']['over5']['pct']), h1d(G['women']['median_abs']), h1d(G['men']['median_abs'])) == (38, 15, '4.1', '2.4'), 'formula gap')
GP = {s: [100 - G[s]['over3']['pct'], G[s]['over3']['pct'] - G[s]['over5']['pct'], G[s]['over5']['pct']] for s in ('women', 'men')}
GPR = {s: [pc(v) for v in GP[s]] for s in GP}
ok(GPR == {'women': [37, 25, 38], 'men': [60, 25, 15]} and all(sum(v) == 100 for v in GPR.values()), f'formula gap thirds {GPR}')
MAE = {f: h1d(S['mae'][f]['all']['mean']) for f in ('rfm', 'deur')}
ok(MAE == {'rfm': '3.1', 'deur': '4.4'}, f'miss in points {MAE}')
ok(all(f"{S['mae'][f][s]['mean']:.4f}" == f"{C['formulas'][f][s]['mae']['mean']:.4f}" for f in ('rfm', 'deur') for s in ('women', 'men')), 'miss in points = bfc_stats')
SCAN = h1d(S['scan_mean']['all']['mean'])
ok(SCAN == '32.9' and S['scan_mean']['all']['ci95'][0] > T3['dxa_mean'], f'average scan {SCAN}')
MARG = [C['formulas']['rfm'][s]['within5']['ci95'] for s in ('women', 'men')] + [G[s]['over5']['ci95'] for s in ('women', 'men')]
ok(all((b - a) / 2 < 2 for a, b in MARG), f'share margins {MARG}')
ok(all((v['ci95'][1] - v['ci95'][0]) / 2 < 0.4 for f in ('rfm', 'deur') for v in (M[f]['all']['20-59'], S['mae'][f]['all'])), 'average-miss margins')
ok((G['women']['n'], G['men']['n']) == (5386, 5361), 'formula gap samples')
SL = {k: {s: S['slip'][s][k]['p50'] for s in ('women', 'men')} for k in ('rfm_waist_in', 'deur_5lb', 'deur_height_in')}
ok({k: (sg(v['women']), sg(v['men'])) for k, v in SL.items()} ==
   {'rfm_waist_in': ('+0.9', '+0.9'), 'deur_5lb': ('+1.0', '+0.9'), 'deur_height_in': ('+1.1', '+1.0')}, f'slips {SL}')
W5 = {f: {s: pc(C['formulas'][f][s]['within5']['pct']) for s in ('women', 'men')} for f in ('rfm', 'deur')}
ok(W5['rfm'] == {'women': 74, 'men': 86}, f'within 5 {W5}')
GAL = P['gallagher']['cuts']
ok(GAL['f']['20-39'] == [21, 33, 39] and GAL['m']['20-39'] == [8, 20, 25], 'provisional ranges (typed in)')
MED = {k: str(pc(P['by_age'][k]['20-39']['p50'])) for k in 'fm'}                   # whole percent: the men's sits on a tie
ok(MED == {'f': '38', 'm': '26'}, f'US medians {MED}')

# ---- the equations, written again here
def navy(s, h, n, w, hp=0): return 86.010 * lg(w - n) - 70.041 * lg(h) + 36.76 if s == 'm' else 163.205 * lg(w + hp - n) - 97.684 * lg(h) - 78.387
def jp3(s, t, a): return (1.10938 - 0.0008267 * t + 0.0000016 * t * t - 0.0002574 * a) if s == 'm' else (1.0994921 - 0.0009929 * t + 0.0000023 * t * t - 0.0001392 * a)
ok((h1d(navy('f', 64, 15, 42, 44)), h1d(navy('m', 69, 16, 49))) == ('47.3', '38.6'), 'Army Table B-5 examples')
ok(abs(jp3('m', 53, 40) - 1.0597633) < 1e-7, 'JP3 published density')
BMI = r1(703 * 180 / 70 ** 2)
EX = {'rfm': 64 - 20 * 70 / 37, 'tape': navy('m', 70, 15.5, 36), 'deur': 1.20 * BMI + 0.23 * 40 - 10.8 - 5.4, 'd': jp3('m', 58, 40)}
EX['sf'] = 495 / EX['d'] - 450
ok((h1d(EX['rfm']), h1d(EX['tape']), BMI, h1d(EX['deur']), h4d(EX['d']), h1d(EX['sf'])) == ('26.2', '20.4', 25.8, '24.0', '1.0565', '18.5'), f'worked example {EX}')
ok(h1d(495 / 1.0565 - 450) == '18.5', 'printed density gives the printed answer')
TW = {'f': navy('f', 64, 13, 32, 40) - navy('f', 64, 13, 31, 40), 'm': navy('m', 70, 15.5, 37) - navy('m', 70, 15.5, 36)}
TN = {'f': navy('f', 64, 14, 31, 40) - navy('f', 64, 13, 31, 40), 'm': navy('m', 70, 16.5, 36) - navy('m', 70, 15.5, 36)}
SF = {'f': (495 / jp3('f', 66, 35) - 450) - (495 / jp3('f', 60, 35) - 450), 'm': (495 / jp3('m', 64, 40) - 450) - (495 / jp3('m', 58, 40) - 450)}
ok(([sg(TW[k]) for k in 'fm'], [sg(TN[k]) for k in 'fm'], [sg(SF[k]) for k in 'fm']) == (['+1.2', '+1.8'], ['−1.2', '−1.9'], ['+1.9', '+1.7']), 'tape and caliper slips')

# ---- the prose, rebuilt here
BN, LO, HI = 437, h1d(ROWS[0][2]), h1d(ROWS[-1][2])
PROSE = [
    f'In a study that tested seven methods on the same {BN} college students, all seven read lower than the scan on average, by {LO} to {HI} points (Burns et al., 2019).',
    f'On CDC’s scans of US adults aged 20 to 59, it came within 5 points of the scan for {W5["rfm"]["men"]}% of men and {W5["rfm"]["women"]}% of women (our calculation).',
    f'Seven-site skinfolds had the smallest average miss of seven methods tested on the same college students, {h1d(B["sf"][5])}% of the scan’s reading, and a hand-held '
    f'device the largest, {h1d(B["omron"][5])}% (Burns et al., 2019).',
    'Three smart scales checked against DXA read fat mass 2.2 to 4.4 kg low, while their median weight differences from the scan were 0 to 0.3 kg (Frija-Masson et al., 2021).',
    'A DXA scan, which CDC calls the most widely accepted method of measuring body composition (CDC), is the reference in the studies below.',
    f'A small measuring slip moves the answer by about a point: for the typical US adult aged 20 to 59, 1 inch on the waist moves the waist-and-height estimate by '
    f'{sg(SL["rfm_waist_in"]["women"])[1:]} points, and 5 lb on the scale moves the height-and-weight estimate by {sg(SL["deur_5lb"]["men"])[1:]} to '
    f'{sg(SL["deur_5lb"]["women"])[1:]} (our calculation).',
    f'Methods disagree for the same person: in CDC’s survey of US adults aged 20 to 59, the two home formulas were more than 5 points apart for '
    f'{pc(G["women"]["over5"]["pct"])}% of women and {pc(G["men"]["over5"]["pct"])}% of men (our calculation), so track one method, with the same device and the '
    'same measuring spots.',
    'no large meal for 2 hours, no vigorous exercise for 12, no alcohol for 48, and an empty bladder.',
    'The worked examples are for one man: 40 years old, 5′10″ (70 inches) and 180 lb, with a 15.5-inch neck, and a waist of 36 inches at the navel and 37 inches at the top of the hip bones.',
    f'For the example man: 64 − 20 × 70 ÷ 37 = {h1d(EX["rfm"])}%.',
    f'For the example man: 86.010 × log10(36 − 15.5) − 70.041 × log10(70) + 36.76 = {h1d(EX["tape"])}%.',
    f'For the example man: BMI = 180 × 703 ÷ 70² = {BMI}, then 1.20 × {BMI} + 0.23 × 40 − 10.8 − 5.4 = {h1d(EX["deur"])}%.',
    f'For the example man, skinfolds of 15, 25 and 18 mm add up to 58: density = 1.10938 − 0.0008267 × 58 + 0.0000016 × 58² − 0.0002574 × 40 = {h4d(EX["d"])}, '
    f'and 495 ÷ {h4d(EX["d"])} − 450 = {h1d(EX["sf"])}%.',
    'For women the density equation is 1.0994921 − 0.0009929 × S + 0.0000023 × S² − 0.0001392 × age, where S is the sum. The seven-method study measured seven '
    'sites, with trained measurers; no study cited here checked the 3-site version against DXA.',
    f'Four methods, four answers for one man: {h1d(EX["sf"])}% from calipers, {h1d(EX["tape"])}% from the tape, {h1d(EX["deur"])}% from height and weight and '
    f'{h1d(EX["rfm"])}% from waist and height.',
    'men 86.010 × log10(waist − neck) − 70.041 × log10(height) + 36.76; women 163.205 × log10(waist + hips − neck) − 97.684 × log10(height) − 78.387',
    'Body fat % = 1.20 × BMI + 0.23 × age − 10.8 × sex − 5.4, with sex 1 for men and 0 for women (Deurenberg et al., 1991).',
    f'Burns and colleagues did that for seven methods in {BN} college students, mean age 19, against one DXA scanner (Hologic Discovery W). Every method read lower than the '
    'scan on average, and for all but the four-electrode analyzer the gap grew as body fat rose (Burns et al., 2019).',
    'Average difference inside the study’s ±2.7-point equivalence margin (10% of the 27.0% average scan): underwater weighing, skinfolds, the Bod Pod and the '
    'four-electrode analyzer; single readings missed by more.',
    f'On CDC’s scans of US adults aged 20 to 59, the waist-and-height formula missed by {MAE["rfm"]} points on average and the height-and-weight formula by '
    f'{MAE["deur"]} points: {MP["rfm"]["all"]}% and {MP["deur"]["all"]}% of the scan’s reading (our calculation). Those shares don’t line up with the college study’s. '
    f'The people and scanners differ, and CDC’s scans read {SCAN}% body fat on average against the students’ 27.0%, so the same miss in points is a smaller share '
    'of a higher reading.',
    'Tape measure: in 1,407 US Army recruits, the Navy method read 6.0 points below DXA on average, with a standard deviation of 4.4 points for women and 3.5 for men (Foulis et al., 2023).',
    'InBody 770: in 226 adults aged 18 to 80, it read 3.1 points below DXA on average, and for about 95% of them it landed between 2.6 points above and 8.9 points below the '
    'scan; its underestimate was largest at normal weight and shrank as BMI rose. A SECA mBCA 515 in the same people read 0.3 points below on average (Lahav et al., 2021).',
    'Smart scales: three home scales checked against DXA in 48 to 53 hospital patients each read fat mass low, by a median of 2.2 to 4.4 kg (Frija-Masson et al., 2021).',
    f'the foot-to-foot scale (Tanita BF-556) read {h1d(B["tanita"][2])} points below DXA on average, with an average miss of {h1d(B["tanita"][5])}%, and the hand-held device '
    f'(Omron HBF-306) read {h1d(B["omron"][2])} points below, with {h1d(B["omron"][5])}%, the largest miss of the seven.',
    f'The lab analyzer, with four electrodes on the right hand and foot while lying down, read {h1d(B["valhalla"][2])} points below (Burns et al., 2019).',
    'Their median weight differences from the scan’s body mass were 0.3, 0 and 0.25 kg, but each underestimated fat mass, by a median of 2.2, 4.4 and 3.7 kg '
    '(Frija-Masson et al., 2021).',
    'CDC’s documentation for its own impedance test, which used electrodes on the right hand and foot, explains the rest:',
    '“subject to additional error” (CDC).',
    'CDC’s survey did not run its impedance test on pregnant women, or on people with a pacemaker or automatic defibrillator or with artificial joints, pins or plates (CDC).',
    'A small measuring slip moves each estimate by about 1 to 2 points:',
    'a woman of 35, 5′4″, with a 13-inch neck, a 31-inch waist, 40-inch hips and skinfolds of 20, 15 and 25 mm (triceps, suprailiac, thigh).',
    'no more than two glasses of water, finished at least 2 hours before, and an empty bladder (Burns et al., 2019).',
    f'Compare like with like. Two methods can differ by several points for the same person: in CDC’s survey of US adults aged 20 to 59, the waist-and-height and '
    f'height-and-weight formulas were more than 5 points apart for {pc(G["women"]["over5"]["pct"])}% of women and {pc(G["men"]["over5"]["pct"])}% of men, and the '
    f'median gap was {h1d(G["women"]["median_abs"])} points for women and {h1d(G["men"]["median_abs"])} for men (our calculation).',
    'in part for its speed, ease of use and low radiation, less than 20 µSv for a whole-body scan (CDC).',
    'CDC’s scans were analyzed with an option that adds 5% of lean mass to the fat mass, and the scanner table kept out people over 450 lb or taller than 6′5″ (CDC).',
    f'In the seven-method study it read {h1d(B["hw"][2])} point below DXA on average, the closest of the seven, with an average miss of {h1d(B["hw"][5])}% (Burns et al., 2019).',
    f'It read {h1d(B["adp"][2])} points below DXA on average, with an average miss of {h1d(B["adp"][5])}% (Burns et al., 2019).',
    f'It read {h1d(B["ir"][2])} points below DXA on average, with an average miss of {h1d(B["ir"][5])}%, and was one of the two methods that failed even the study’s looser 15% '
    'equivalence test (Burns et al., 2019).',
    f'Provisional ranges tied to BMI call {GAL["f"]["20-39"][0]} to {GAL["f"]["20-39"][1] - 0.1:.1f}% body fat healthy for women aged 20 to 39 and '
    f'{GAL["m"]["20-39"][0]} to {GAL["m"]["20-39"][1] - 0.1:.1f}% for men, with higher ranges at older ages (Gallagher et al., 2000).',
    f'On CDC’s scans of US adults aged 20 to 39, the median was about {MED["f"]}% for women and {MED["m"]}% for men.',
    f'A slip of 2 mm at each of three sites moves a 3-site estimate by about {sg(SF["m"])[1:]} points for a 40-year-old man whose three skinfolds add up to 58 mm (our '
    'calculation); no study cited here checked the 3-site version against DXA.',
    'No method is exact. DXA, which CDC calls the most widely accepted method of measuring body composition, is the reference the studies here check other methods against.',
    f'At home, the waist-and-height formula missed CDC’s scans of US adults aged 20 to 59 by {MAE["rfm"]} points on average (our calculation).',
    'Three smart scales checked against DXA in hospital patients had median weight differences of 0 to 0.3 kg from the scan’s body mass but read fat mass 2.2 to 4.4 kg low',
    'its underestimate was largest at normal weight and shrank as BMI rose (Lahav et al., 2021).',
    'In CDC’s survey of US adults aged 20 to 59, the waist-and-height and height-and-weight formulas were more than 5 points apart for 38% of women and 15% of men (our calculation).',
    f'On CDC’s scans of US adults aged 20 to 39, the median was about {MED["f"]}% for women and {MED["m"]}% for men. The body fat percentage chart has the ranges for every age.',
    'our calculation for 10,864 adults aged 20 to 59 (10,751 with a measured waist, 10,829 with a BMI, 10,747 with both).',
    'each share quoted here has a 95% margin of error under 2 percentage points and each average miss under 0.4 (Taylor linearization over the survey’s 59 strata and 121 '
    'primary sampling units)',
    'Siri WE (1961): the body fat equation, as printed by Topend Sports (Siri equation).',
    'Healthy percentage body fat ranges: an approach for developing guidelines based on body mass index.',
]
REMOVED = ('Not reported in text', 'conference abstract', 'digitalcommons.wku.edu', 'og-how-to-measure-body-fat', 'Every accuracy figure from published studies',
           'The real question', 'Fine as a first rough guess', 'which is why', 'in this guide', 'The next section shows', 'this guide’s', 'Equivalent; lowest',
           'closest to the truth', 'says little about', 'weighed within 0.3 kg', 'came within 0.3 kg', 'Every Method vs DXA', 'every method against a DXA scan',
           'is what those equations are checked against', 'its misses were largest', 'for half of women they were more than', 'half of men more than',
           'Siri WE, 1956', 'missed by 10.4% (our calculation)', 'how close each method gets', 'How close each method gets')

with sync_playwright() as p:
    br = p.chromium.launch(args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 1280, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())     # no ads or analytics
    resp = pg.goto(URL, wait_until='load')
    ok(resp.status == 200, f'page status {resp.status}')
    raw = pg.content()
    faq_text = norm(' '.join(pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')))
    body = norm(pg.inner_text('main')) + ' ' + faq_text                    # the FAQ answers are closed, so innerText skips them
    for s_ in PROSE: ok(norm(s_) in body, f'prose not found: {s_!r}')
    for s_ in REMOVED: ok(s_ not in body and s_ not in raw, f'removed wording back on the page: {s_!r}')
    src = pg.request.get(URL).text()
    ok('{TODAY}' not in src and '<style' not in src and '<article' not in src, 'template marker, page-level style or <article>')
    mains = src[src.index('<main'):src.index('</main>')]
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>', '', mains), 'inline style in <main> outside figures')
    ok(mains.startswith('<main class="reading"><div class="container">'), 'reading column')
    ok('—' not in norm(re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<svg.*?</svg>', '', mains))), 'em dash in the body')

    # Tables.
    tabs = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => ({cap: t.caption.textContent,
        head: [...t.tHead.rows[0].cells].map(c => c.textContent),
        groups: [...t.tBodies].map(b => [...b.rows].map(r => [...r.cells].map(c => [c.tagName, c.getAttribute('scope'), c.getAttribute('colspan'), c.textContent])))}))""")
    ok(len(tabs) == 2, f'{len(tabs)} tables')
    t1, t2 = tabs
    ok(t1['cap'] == f'Seven methods against DXA in the same {BN} college students' and t1['head'] == ['Method', 'Below DXApoints', 'Average miss'], f'table 1 head {t1["cap"]} {t1["head"]}')
    want1 = [[['TH', 'row', None, lab], ['TD', None, None, h1d(d)], ['TD', None, None, f'{h1d(m)}%']] for _, lab, d, _, _, m, _, _ in ROWS]
    got1 = [[[c[0], c[1], c[2], norm(c[3])] for c in r] for r in t1['groups'][0]]
    ok(len(t1['groups']) == 1 and got1 == want1, f'table 1 rows {got1}')
    ok(t2['cap'] == 'How much a measuring slip moves each estimate, in body fat points' and t2['head'] == ['Measuring slip', 'Women', 'Men'], f'table 2 head {t2["head"]}')
    want2 = [('Waist and height formula', [('Waist 1 inch too large', SL['rfm_waist_in']['women'], SL['rfm_waist_in']['men'])]),
             ('Height and weight formula', [('Weight 5 lb too high', SL['deur_5lb']['women'], SL['deur_5lb']['men']),
                                            ('Height 1 inch too short', SL['deur_height_in']['women'], SL['deur_height_in']['men'])]),
             ('Tape method*', [('Waist 1 inch too large', TW['f'], TW['m']), ('Neck 1 inch too large', TN['f'], TN['m'])]),
             ('Calipers, 3 sites*', [('2 mm too much at each site', SF['f'], SF['m'])])]
    got2 = [[[c[0], c[1], c[2], norm(c[3])] for c in r] for b in t2['groups'] for r in b]
    exp2 = []
    for g, rows in want2:
        exp2.append([['TH', 'rowgroup', '3', g]])
        exp2 += [[['TH', 'row', None, a], ['TD', None, None, sg(w)], ['TD', None, None, sg(m)]] for a, w, m in rows]
    ok(len(t2['groups']) == 4 and got2 == exp2, f'table 2 rows {got2}')

    # Figures.
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => ({vb: svg.getAttribute('viewBox'),
        title: svg.querySelector('title').textContent, desc: svg.querySelector('desc').textContent,
        circles: [...svg.querySelectorAll('circle')].map(c => [+c.getAttribute('cx'), +c.getAttribute('cy'), c.querySelector('title') ? c.querySelector('title').textContent : '']),
        lines: [...svg.querySelectorAll('line')].map(l => [+l.getAttribute('x1'), +l.getAttribute('x2'), +l.getAttribute('y1'), +l.getAttribute('y2'),
                 l.getAttribute('stroke'), l.getAttribute('stroke-dasharray'), l.querySelector('title') ? l.querySelector('title').textContent : '']),
        rects: [...svg.querySelectorAll('rect')].map(r => [+r.getAttribute('x'), +r.getAttribute('width'), r.getAttribute('fill'), r.querySelector('title') ? r.querySelector('title').textContent : '',
                 +r.getAttribute('y'), +r.getAttribute('height')]),
        texts: [...svg.querySelectorAll('text')].map(t => t.textContent)}))""")
    ok(len(figs) == 2, f'{len(figs)} figures')
    hero, gapf = figs
    mx = lambda e: 16 + (e + 6) * 288 / 7
    ok(len(hero['circles']) == 7, 'hero dots')
    for i, (k, lab, d, lo, hi, m, _, _) in enumerate(ROWS):
        c_ = hero['circles'][i]
        tip = f'{lab}: read {h1d(d)} points below DXA on average (90% CI {h1d(lo)} to {h1d(hi)}); average miss {h1d(m)}% of the scan’s reading'
        ok(abs(c_[0] - mx(-d)) < 0.06 and c_[2] == tip, f'hero dot {k}: {c_}')
        ok(any(abs(l[0] - mx(-hi)) < 0.06 and abs(l[1] - mx(-lo)) < 0.06 and l[4] == '#0e7490' and l[6] == tip for l in hero['lines']), f'hero interval {k}')
        ok(f'{lab}: −{h1d(d)}' in hero['texts'], f'hero label {k}')
        ok(f'{lab}: {h1d(d)} points lower ({h1d(lo)} to {h1d(hi)}).' in hero['desc'], f'hero desc {k}')
    ok(sum(1 for l in hero['lines'] if abs(l[0] - mx(0)) < 0.06 and abs(l[1] - mx(0)) < 0.06 and l[5] == '4 3') == 7, 'hero dashed zero line per row')
    ok(all(c_[0] < mx(0) for c_ in hero['circles']) and hero['title'] == f'Seven body fat methods against one DXA scan, the same {BN} people', 'hero: all left of zero / title')
    # The formula-gap figure: two 100% bars (women, men), three segments each at 3 px per percent from x = 4, labelled inside.
    SEGS = (('Within 3 points of each other', '#cffafe'), ('3 to 5 points apart', '#67e8f9'), ('More than 5 points apart', '#0e7490'))
    segs = [r_ for r_ in gapf['rects'] if r_[3]]
    ok(len(segs) == 6, f'{len(segs)} gap segments')
    for i, (s_, lab) in enumerate((('women', 'Women'), ('men', 'Men'))):
        x = 4
        for k, (seg, fill) in enumerate(SEGS):
            r_ = segs[i * 3 + k]; w = 3 * GP[s_][k]
            ok(abs(r_[0] - x) < 0.06 and abs(r_[1] - w) < 0.06 and r_[2] == fill and r_[3] == f'{lab}: {GPR[s_][k]}% {seg[0].lower() + seg[1:]}',
               f'gap segment {s_} {k}: {r_}')
            x += w
        ok(abs(x - 304) < 0.06, f'gap bar {s_} ends at {x}')
        ok(lab in gapf['texts'] and all(f'{v}%' in gapf['texts'] for v in GPR[s_]), f'gap labels {s_}')
    ok(all(seg in gapf['texts'] for seg, _ in SEGS), 'gap legend')
    ok(gapf['desc'] == f'Women: {GPR["women"][0]}% within 3 points of each other, {GPR["women"][1]}% 3 to 5 points apart, {GPR["women"][2]}% more than 5 points '
       f'apart. Men: {GPR["men"][0]}%, {GPR["men"][1]}% and {GPR["men"][2]}%. US adults aged 20 to 59 with both formulas, CDC’s 2011–2018 survey (our calculation).',
       f'gap desc {gapf["desc"]!r}')
    ok(gapf['title'] == 'How far apart the two home formulas landed for the same person', 'gap title')

    # Head and JSON-LD.
    head = pg.evaluate("""() => ({title: document.title, desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content), canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content), ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        ogt: document.querySelector('meta[property="og:title"]').content, twt: (document.querySelector('meta[name="twitter:title"]') || {}).content || '',
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content),
        ogd: document.querySelector('meta[property="og:description"]').content, twd: (document.querySelector('meta[name="twitter:description"]') || {}).content || ''})""")
    PI = {r: f'{SITE}/assets/images/preferred/how-to-measure-body-fat-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['title'] == 'How to Calculate Body Fat Percentage: Home Methods vs DXA', f'title {head["title"]!r}')
    ok(len(head['desc']) <= 160 and head['desc'].startswith('How to calculate body fat percentage at home with a tape or calipers, step by step'), f'description {head["desc"]!r}')
    ok(head['robots'] == ['max-image-preview:large'] and head['canon'] == SITE + '/blog/how-to-measure-body-fat/', f'robots / canonical {head}')
    ok(head['og'] == [PI['16x9']] and head['tw'] == [PI['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter image {head}')
    ok(head['ogd'] == head['twd'] and head['ogt'] == head['twt'] == 'How to calculate body fat percentage: home methods against a DXA scan', f'og/twitter text {head}')
    ok(head['ogalt'].startswith('Chart: seven body fat methods tested on the same people'), f'og alt {head["ogalt"]!r}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/how-to-measure-body-fat-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png').status == 404, 'old OG image still served')
    sm = pg.request.get(base + '/sitemap.xml').text()
    ent = re.search(r'<url><loc>https://calculatemybmi\.net/blog/how-to-measure-body-fat/</loc>(.*?)</url>', sm)
    lastmod = re.search(r'<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>', ent.group(1)).group(1) if ent else None
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['Article', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    GR = {x['@type']: x for x in ld[0]['@graph']}
    A = GR['Article']
    h1 = pg.inner_text('h1')
    ok(h1 == A['headline'] == 'How to Calculate Body Fat Percentage', 'H1 / headline')
    ok(A['image'] == [PI['1x1'], PI['4x3'], PI['16x9']] and A['mainEntityOfPage']['primaryImageOfPage']['url'] == PI['16x9'], 'image list / primaryImageOfPage')
    ok(A['dateModified'] == lastmod and re.fullmatch(r'\d{4}-\d{2}-\d{2}', lastmod or '') and A['datePublished'] == '2026-10-07', f'dates {A.get("dateModified")!r} {lastmod!r}')
    ok(A['author']['name'] == 'Marko Visic' and A['publisher']['name'] == 'CalculateMyBMI' and A['@id'] == SITE + '/blog/how-to-measure-body-fat/#article', 'author / publisher / @id')
    ok(set(A['citation']) <= REG_URLS and A['description'] == head['desc'], 'citations in the registry / description')
    ok([i['name'] for i in GR['BreadcrumbList']['itemListElement']] == ['Home', 'Guides', h1], 'breadcrumb')
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok(len(visq) == 10 and [[q['name'], q['acceptedAnswer']['text']] for q in GR['FAQPage']['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')
    ok([q for q, _ in visq] == ['How do I calculate my body fat percentage at home?', 'What is the most accurate way to measure body fat?',
        'How accurate are body fat scales?', 'How do scales measure body fat?', 'How accurate are body fat calipers?',
        'How do I measure body fat with a tape measure?', 'How accurate is InBody?', 'How accurate is a Bod Pod?',
        'Why do different methods give different numbers?', 'How much body fat should I have?'], 'FAQ questions')

    # The menu marks Guides, in both menus, and nothing else.
    cur = pg.eval_on_selector_all('[aria-current="page"]', 'as => as.map(a => [a.getAttribute("href"), a.className, a.textContent.trim()])')
    ok(cur == [['/blog/', 'active', 'Guides'], ['/blog/', 'active', 'Guides']], f'menu current page {cur}')
    ok(pg.eval_on_selector_all('header a.active, nav a.active', 'as => as.length') == 2, 'other menu links marked active')

    # Links, chips, FAQ.
    hrefs = pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for h_ in sorted({h_.split('#')[0] for h_ in hrefs if h_.startswith('/')}):
        ok(pg.request.get(base + h_).status == 200, f'internal link {h_} does not answer 200')
    for h_ in sorted({h_ for h_ in hrefs if h_.startswith('/') and '#' in h_}):
        path, frag = h_.split('#')
        ok(f'id="{frag}"' in pg.request.get(base + path).text(), f'anchor {h_} missing')
    for h_ in {h_ for h_ in hrefs if h_.startswith('#')}:
        ok(pg.evaluate('h => !!document.getElementById(h.slice(1))', h_), f'anchor {h_} missing')
    outside = {h_ for h_ in pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))')}
    ok(outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')
    ok(len(outside) == 17, f'{len(outside)} outside links')
    ok(all(pg.evaluate('h => [...document.querySelectorAll(`main a[href="${h}"]`)].every(a => a.target === "_blank" && a.rel === "noopener")', h_) for h_ in outside), 'outside links open in a new tab')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#steps', '#accuracy', '#scales', '#measuring', '#lab', '#meaning', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    for i, q in enumerate(pg.query_selector_all('.faq-question')):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
    ok(pg.evaluate("() => document.querySelectorAll('main h2').length") == 9 and pg.evaluate("() => document.querySelectorAll('h1').length") == 1, 'headings')

    # Widths, table frames, rendered labels.
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption.textContent, t.offsetWidth, t.parentElement.clientWidth])""")
        for cap, tw, fw in fits: ok(tw <= fw + 1, f'table scrolls at {w}: {cap} {tw} > {fw}')
        res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
            const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
            return {box: [r.left, r.top, r.right, r.bottom], texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                    shapes: [...svg.querySelectorAll('rect, circle, line')].map(e => [e.tagName + ' ' + (e.getAttribute('fill') || e.getAttribute('stroke')), ...bx(e)])}; })""")
        ok(len(res) == 2, f'{len(res)} figures at {w}')
        for f_ in res:
            L_, T_, R_, B_ = f_['box']
            for j, a in enumerate(f_['texts']):
                ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                for c2 in f_['texts'][j + 1:]:
                    if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5: fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                for s_ in f_['shapes']:
                    inside = s_[0].lower().startswith('rect') and a[1] >= s_[1] - 0.5 and a[3] <= s_[3] + 0.5 and a[2] >= s_[2] - 0.5 and a[4] <= s_[4] + 0.5
                    if not inside and a[1] < s_[3] - 0.5 and s_[1] < a[3] - 0.5 and a[2] < s_[4] - 0.5 and s_[2] < a[4] - 0.5:
                        fails.append(f'{w}px label over a shape: {a[0]!r} / {s_[0]}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f_ in fails[:40]: print('FAIL', f_)
sys.exit(1 if fails else 0)
