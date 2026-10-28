#!/usr/bin/env python3
"""Body fat calculator page checks in Chromium (CMB-020). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/body-fat-calculator-build/bfcalc_test_playwright.py http://localhost:8000 research/body-fat-calculator-build/bfc_stats.json
  - typed-in values: the Army's worked examples (47.3% and 38.6%), the published JP3 density (1.0597633 at 53 mm and age 40),
    the check on CDC's scans (within 5 points 74.3% / 86.3% for waist and height, 62.4% / 66.4% for height and weight;
    the worked example's calibration windows), the chart's US share (79% of women 30-39 above 33.0%) and the provisional
    cut-offs (Gallagher, as tabulated);
  - the prose: each sentence that states a number is rebuilt here from the stats files and found on the page; removed
    wording stays removed;
  - tables: both formula tables and both range tables equal the stats; the figures: the worked example's dots, boxes and
    ticks and the accuracy figure's boxes, lines and ticks at their drawn positions, with descriptions carrying the numbers;
  - the tool: its data equals the stats files; 26 cases (four methods, both sexes, both units, 3 and 7 skinfold sites,
    ages 18-79, the tails of the calibration, every refusal) give the card, the tint, every note, the figure's labels, the
    fat and lean mass and the other estimates worked out here from the formulas and the stats; a method pane counts as an
    other estimate only after typing in it; the unit switch converts every length; the sex switch shows the hips and the
    right 3-site skinfolds; one pane shows at a time;
  - head: title, description, robots, canonical, og:image and twitter:image = the 16:9 preferred image with its alt,
    twitter title, the WebApplication image list, WebPage primaryImageOfPage and dateModified = sitemap lastmod, author
    named, preferred files at size, old OG image gone, no {TODAY}, no page-level style, no <article>; the menu marks Body
    Fat as the current page and nothing else;
  - every internal link answers 200 and every outside link is a registry URL; chips land on their sections; every FAQ
    opens; the FAQ JSON-LD equals the visible answers;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px and every table fits its frame; rendered SVG
    labels don't overlap, stay inside their figure and sit on no shape; no JavaScript error."""
import sys, os, json, math, re, csv, struct
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(stats)), '..', '..'))
S = json.load(open(stats))
P = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ')} | set(re.findall(r'https?://[^\s;,)"]+', r['notes']))
URL = base + '/body-fat-calculator/'
SITE = 'https://calculatemybmi.net'
F = S['formulas']
SX = ('women', 'men'); SK = {'f': 'women', 'm': 'men'}

def h1d(x): return str(Decimal(x).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))   # halves up, as toFixed
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10                               # the tool's r1()
def d1(x): return f'{r1(x):.1f}'
def sg(x): s = h1d(x); return ('−' + s[1:]) if s.startswith('-') else '+' + s
def pc(x): return int(Decimal(x).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
def jround(x): return math.floor(x + 0.5)                                            # Math.round
def jstr(x):                                                                          # String(number)
    s = repr(float(x)); return s[:-2] if s.endswith('.0') else s
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def lg(x): return math.log(x) / math.log(10)                                         # Math.log(x) / Math.LN10

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# ---- formulas, as published (typed in from the sources)
def navy(s, h, n, w, hp=0): return 86.010 * lg(w - n) - 70.041 * lg(h) + 36.76 if s == 'm' else 163.205 * lg(w + hp - n) - 97.684 * lg(h) - 78.387
def rfm(s, h, w): return 64 - 20 * h / w + (12 if s == 'f' else 0)
def deur(s, b, a): return 1.20 * b + 0.23 * a - 10.8 * (1 if s == 'm' else 0) - 5.4
def jp(s, k, t, a):
    if k == '7': d = 1.112 - 0.00043499 * t + 0.00000055 * t * t - 0.00028826 * a if s == 'm' else 1.097 - 0.00046971 * t + 0.00000056 * t * t - 0.00012828 * a
    else: d = 1.10938 - 0.0008267 * t + 0.0000016 * t * t - 0.0002574 * a if s == 'm' else 1.0994921 - 0.0009929 * t + 0.0000023 * t * t - 0.0001392 * a
    return 495 / d - 450
ok((h1d(navy('f', 64, 15, 42, 44)), h1d(navy('m', 69, 16, 49))) == ('47.3', '38.6'), 'Army Table B-5 examples')
ok(abs(1.10938 - 0.0008267 * 53 + 0.0000016 * 53 ** 2 - 0.0002574 * 40 - 1.0597633) < 1e-7, 'JP3 published density')
ok((h1d(navy('m', 69 * 2.54, 16 * 2.54, 49 * 2.54) - navy('m', 69, 16, 49)), h1d(navy('f', 64 * 2.54, 15 * 2.54, 42 * 2.54, 44 * 2.54) - navy('f', 64, 15, 42, 44))) == ('6.5', '26.5'), 'cm misuse')

# ---- the check on CDC's scans (typed in from the chat run) and the stats files
W5 = {f: {s: F[f][s]['within5']['pct'] for s in SX} for f in ('rfm', 'deur')}
ok((h1d(W5['rfm']['women']), h1d(W5['rfm']['men']), h1d(W5['deur']['women']), h1d(W5['deur']['men'])) == ('74.3', '86.3', '62.4', '66.4'), 'within 5 points')
ok([F[f][s]['n'] for f in ('rfm', 'deur') for s in SX] == [5388, 5363, 5446, 5383], 'samples')
ok(S['meta']['n_scanned_20_59'] == 10864 and P['meta']['n_adults_20_59'] == 10864, 'scanned adults')
W5N = {f: {s: pc(W5[f][s]) for s in SX} for f in W5}
MAE = {f: {s: F[f][s]['mae']['mean'] for s in SX} for f in W5}
BIAS = {f: {s: F[f][s]['bias']['mean'] for s in SX} for f in W5}
for s in SX:
    ok(F['rfm'][s]['bias']['ci95'][0] > 0 and F['deur'][s]['bias']['ci95'][0] < 0 < F['deur'][s]['bias']['ci95'][1], f'bias CIs {s}')
    for key in ('within5_rfm_minus_deur', 'mae_rfm_minus_deur'):
        ci = S['paired'][s][key]['ci95']; ok(ci[0] > 0 or ci[1] < 0, f'paired {key} {s} not clear of zero')
PW5 = {s: pc(S['paired'][s]['within5_rfm_minus_deur']['mean']) for s in SX}
ok(PW5 == {'women': 12, 'men': 20}, f'paired within 5 {PW5}')
GROUPS = (('healthy', 'BMI 18.5–24.9'), ('over', 'BMI 25–29.9'), ('obese', 'BMI 30 and over'), ('20-39', 'Ages 20–39'), ('40-59', 'Ages 40–59'))
def gb(f, s, k): return F[f][s]['by_bmi'][k]['bias'] if k in ('healthy', 'over', 'obese') else F[f][s]['by_age'][k]['bias']
clear = [(f, s, k) for f in ('rfm', 'deur') for s in SX for k, _ in GROUPS if not (gb(f, s, k)['ci95'][0] > 0 or gb(f, s, k)['ci95'][1] < 0)]
ok(clear == [('rfm', 'men', 'healthy')], f'groups whose CI includes zero: {clear}')
CAL = {f: {k: {int(b): [float(h1d(x)) for x in v['q']] + [v['n']] for b, v in F[f][SK[k]]['calib'].items()} for k in 'fm'} for f in ('rfm', 'deur')}
ok(CAL['deur']['f'][34] == [34.0, 36.8, 39.5, 446] and CAL['rfm']['f'][38] == [33.7, 36.1, 38.5, 543], 'worked-example windows')
# the fact-check's exact ties (Deurenberg estimates and errors are exact hundredths): typed in
ok(h1d(F['deur']['women']['within3']['pct']) == '41.5' and CAL['deur']['m'][12][3] == 72 and CAL['deur']['f'][36][3] == 430, 'exact ties')
# the RFM median error against Woolcott and Bergman's validation medians (Table 2, typed in): women clearly higher, men not
MCI = {s_: F['rfm'][s_]['err_median_ci95'] for s_ in SX}
ok(MCI['women'][0] > 1.1 and MCI['men'][0] <= 0.8 and MCI['men'][1] >= 0.3, f'median error CIs {MCI}')
for f in CAL:
    for k in CAL[f]:
        ok(all(v[3] >= 30 for v in CAL[f][k].values()), f'calibration window under 30 people {f} {k}')
BA = P['by_age']
GAL = P['gallagher']['cuts']
ok(GAL['f'] == {'20-39': [21, 33, 39], '40-59': [23, 34, 40], '60-79': [24, 36, 42]} and
   GAL['m'] == {'20-39': [8, 20, 25], '40-59': [11, 22, 28], '60-79': [13, 25, 30]}, 'provisional cut-offs (typed in)')
P0 = P['tool']['percents'][0]
def more_at(arr, v):
    i, fr = math.floor(v) - P0, v - math.floor(v)
    if i < 0: return arr[0]
    if i >= len(arr) - 1: return arr[-1]
    return arr[i] + (arr[i + 1] - arr[i]) * fr
def share_txt(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{jround(x)}%'
ok(share_txt(more_at(P['tool']['more']['f']['30-39'], 33.0)) == '79%', 'typed-in US share')
UGR = ('16-19', '20-29', '30-39', '40-49', '50-59')
TQ = {k: {g: [float(f'{BA[k][g][p]:.1f}') for p in ('p10', 'p25', 'p50', 'p75', 'p90')] for g in UGR} for k in 'fm'}
MEAN_F, MEAN_M = f'{BA["f"]["20-59"]["mean4"]:.1f}', f'{BA["m"]["20-59"]["mean4"]:.1f}'
ok((MEAN_F, MEAN_M) == ('38.7', '27.2'), 'US means')
def rng(c, k): return {'low': f'under {c[0]}%', 'healthy': f'{c[0]}–{c[1] - 0.1:.1f}%', 'high': f'{c[1]}–{c[2] - 0.1:.1f}%', 'very high': f'{c[2]}% or more'}[k]
def cat(v, c): return 'low' if v < c[0] else 'healthy' if v < c[1] else 'high' if v < c[2] else 'very high'
FOULIS, BURNS = ('1,407', '6.0', '4.4', '3.5'), ('437', '1.4', '11.7')

# ---- the prose, rebuilt here
EX = navy('f', 64, 13, 31, 40); EXB = r1(703 * 150 / 64 ** 2); EXD = deur('f', EXB, 35); EXR = rfm('f', 64, 34)
ok((h1d(EX), EXB, h1d(EXD), h1d(EXR)) == ('33.0', 25.7, '33.5', '38.4'), 'worked example')
CD, CR = CAL['deur']['f'][34], CAL['rfm']['f'][38]
FAT = 150 * r1(EX) / 100
PROSE = [
    f'On CDC’s DXA scans of US adults, the waist-and-height formula came within 5 points of the scan for {W5N["rfm"]["men"]}% of men and '
    f'{W5N["rfm"]["women"]}% of women, and the height-and-weight formula for {W5N["deur"]["men"]}% and {W5N["deur"]["women"]}% (our calculation).',
    f'the woman in the worked example below gets {h1d(EX)}% by tape measure, {h1d(EXD)}% by height and weight and {h1d(EXR)}% by waist and height.',
    f'The waist-and-height formula reads high on average, by {sg(BIAS["rfm"]["women"])[1:]} points for women and {sg(BIAS["rfm"]["men"])[1:]} for men.',
    f'In published studies, the tape method read {FOULIS[1]} points below DXA on average in Army recruits, and seven-site skinfolds {BURNS[1]} points below in college students.',
    f'in {BURNS[0]} college students, seven sites read {BURNS[1]} points below DXA on average; the average miss was {BURNS[2]}% of the scan’s reading.',
    'For waist and height, whose field starts empty, the example adds a 34-inch waist at the hip bones.',
    '(our calculation; all four differences are outside their margins of error).',
    'For women it read clearly higher on the newer scans (the two 95% confidence intervals don’t overlap); for men the two don’t clearly differ. '
    'The samples also differ in scanner model (Hologic Discovery A, against the QDR 4500A) and age range, so the reason isn’t known.',
    'Where to measure, as on the Army’s 2013 worksheets (DA Form 5500 and 5501):',
    'In June 2023 the Army moved to a one-site tape test (Army Directive 2023-11).',
    'Measure the waist at the top of your hip bones (Cedars-Sinai). CDC’s survey measures it there, at the top of the right hip bone (Woolcott and Bergman, 2018). '
    'The tape method uses another spot (the navel for men, the narrowest point for women), so the two waists can differ.',
    'Its standard error of estimate is 4.1 points',
    'Coefficients as printed by Topend Sports, citing Jackson and Pollock (1978) and Jackson, Pollock and Ward (1980). Serra et al., ConScientiae Saúde 2009 '
    'print the same equations, but the women’s 3-site age term as 0.0001395 instead of 0.0001392, which changes the result by less than 0.02 points at any age from 18 to 79.',
    f'In {BURNS[0]} college students, seven-site skinfolds read {BURNS[1]} points below DXA on average; the average miss was {BURNS[2]}% of the scan’s reading (Burns et al., 2019).',
    f'the tape method read {FOULIS[1]} points below DXA in Army recruits (Foulis et al., 2023), and seven-site skinfolds read {BURNS[1]} points below DXA on average in college students (Burns et al., 2019).',
    'as on the US Army’s 2013 worksheets (DA Forms 5500 and 5501).',
    f'In a study of {BURNS[0]} college students, the 7-site test read {BURNS[1]} points below DXA on average (Burns et al., 2019).',
    'read the middle half and median of their scans (weighted percentiles by the midpoint rule, as on the body fat percentage chart).',
    f'{rng(GAL["f"]["20-39"], "healthy")} for women and {rng(GAL["m"]["20-39"], "healthy")} for men aged 20 to 39 (Gallagher et al., 2000).',
    'a woman of 35, 5′4″ (162.6 cm) and 150 lb (68.0 kg), with a neck of 13, a waist of 31 and hips of 40 inches for the tape measure.',
    f'163.205 × log10(31 + 40 − 13) − 97.684 × log10(64) − 78.387 = {h1d(EX)}, the women’s tape equation, in inches.',
    f'so {h1d(EX)}% is high: the high range starts at 33%.',
    f'In {FOULIS[0]} Army recruits, the tape method read {FOULIS[1]} points below DXA on average (Foulis et al., 2023).',
    f'On CDC’s scans, 79% of US women aged 30 to 39 had more body fat than {h1d(EX)}%; their median was {TQ["f"]["30-39"][2]:.1f}%.',
    f'150 lb × {h1d(EX)}% = {h1d(FAT)} lb of fat ({h1d(FAT * 0.45359237)} kg); the other {h1d(150 - FAT)} lb ({h1d((150 - FAT) * 0.45359237)} kg) is lean mass.',
    f'Her BMI is {EXB} (150 × 703 ÷ 64²), and 1.20 × {EXB} + 0.23 × 35 − 5.4 = {h1d(EXD)}. Among US women whose height-and-weight estimate was within a '
    f'point of 34%, CDC’s scans read {CD[0]:.1f}% to {CD[2]:.1f}% for the middle half, median {CD[1]:.1f}% ({CD[3]} women).',
    f'a waist of 34 inches gives 76 − 20 × 64 ÷ 34 = {h1d(EXR)}. Among US women whose estimate was within a point of 38%, the scans read {CR[0]:.1f}% to '
    f'{CR[2]:.1f}%, median {CR[1]:.1f}% ({CR[3]} women). The two formulas disagree by {h1d(EXR - EXD)} points',
    f'on CDC’s scans of {F["rfm"]["women"]["n"] + F["rfm"]["men"]["n"]:,} US adults, within 5 points for {W5N["rfm"]["women"]}% of women and {W5N["rfm"]["men"]}% of men.',
    f'on CDC’s scans of {F["deur"]["women"]["n"] + F["deur"]["men"]["n"]:,} US adults, within 5 points for {W5N["deur"]["women"]}% of women and {W5N["deur"]["men"]}% of men.',
    f'it came within 5 points of the scan for {PW5["women"]} more women in every 100 than the height-and-weight formula, and for {PW5["men"]} more men.',
    f'Its typical miss was {h1d(MAE["rfm"]["women"])} points for women and {h1d(MAE["rfm"]["men"])} for men, against {h1d(MAE["deur"]["women"])} and {h1d(MAE["deur"]["men"])}',
    f'{F["rfm"]["women"]["n"]:,} women and {F["rfm"]["men"]["n"]:,} men aged 20 to 59 with a measured waist, {F["deur"]["women"]["n"]:,} and {F["deur"]["men"]["n"]:,} with a BMI.',
    f'Its median error, the measure its authors report, was {sg(F["rfm"]["women"]["err_q"]["p50"])} points for women and {sg(F["rfm"]["men"]["err_q"]["p50"])} '
    'for men. On the 2005–2006 scans they tested it on (adults aged 20 to 69), the median errors were 0.9 and 0.5 points',
    f'(an average error of {sg(BIAS["deur"]["women"])} points for women and {sg(BIAS["deur"]["men"])} for men, within its margin of error), but only because its misses cancel out.',
    f'At a healthy BMI it read {sg(gb("deur", "women", "healthy")["mean"])[1:]} points low for women and {sg(gb("deur", "men", "healthy")["mean"])[1:]} for men; with '
    f'obesity, {sg(gb("deur", "women", "obese")["mean"])[1:]} and {sg(gb("deur", "men", "obese")["mean"])[1:]} points high.',
    f'seven-site skinfolds read {BURNS[1]} points below DXA on average, and their average miss, {BURNS[2]}% of the scan’s reading, was the lowest of the seven methods tested',
    f'with a standard deviation of {FOULIS[2]} points for women and {FOULIS[3]} for men (Foulis et al., 2023).',
    'Worked by hand with rounded logarithms, the document gets 46.73% and 38.62% and reports 47% and 39%. Computed exactly, they are 47.3% and 38.6%',
    'built relative fat mass (RFM) on CDC’s DXA scans of 12,581 adults from 1999–2004 and tested it on 3,456 from 2005–2006',
    f'it came within 5 points for {W5N["rfm"]["women"]}% of women and {W5N["rfm"]["men"]}% of men, with a typical miss of {h1d(MAE["rfm"]["women"])} and '
    f'{h1d(MAE["rfm"]["men"])} points, and read {sg(BIAS["rfm"]["women"])[1:]} and {sg(BIAS["rfm"]["men"])[1:]} points high on average',
    'measured body fat from body density in 1,229 people aged 7 to 83',
    'Body fat % = 1.20 × BMI + 0.23 × age − 10.8 × sex − 5.4, with sex 1 for men and 0 for women.',
    '7 sites, men: density = 1.112 − 0.00043499 × S + 0.00000055 × S² − 0.00028826 × age',
    '7 sites, women: density = 1.097 − 0.00046971 × S + 0.00000056 × S² − 0.00012828 × age',
    '3 sites, women: density = 1.0994921 − 0.0009929 × S + 0.0000023 × S² − 0.0001392 × age',
    '3 sites, men: density = 1.10938 − 0.0008267 × S + 0.0000016 × S² − 0.0002574 × age',
    'Men: 86.010 × log10(waist − neck) − 70.041 × log10(height) + 36.76',
    'Women: 163.205 × log10(waist + hips − neck) − 97.684 × log10(height) − 78.387',
    'Men: 64 − 20 × height ÷ waist', 'Women: 76 − 20 × height ÷ waist', 'Body fat (Siri): 495 ÷ density − 450',
    f'US women aged 20 to 59 measured {MEAN_F}% body fat on average on CDC’s scans and men {MEAN_M}%.',
    f'in the US Army’s two worked examples, 6.5 points higher for the man and 26.5 for the woman (our calculation).',
    f'At 150 lb and {h1d(EX)}% body fat, that is {h1d(FAT)} lb of fat ({h1d(FAT * 0.45359237)} kg), and the other {h1d(150 - FAT)} lb ({h1d((150 - FAT) * 0.45359237)} kg) is lean mass.',
    'our calculation for 10,864 adults aged 20 to 59, 10,751 with a measured waist and 10,829 with a BMI.',
    'with 95% confidence intervals from Taylor linearization over the survey’s 59 strata and 121 primary sampling units',
]
ok(S['meta']['strata'] == 59 and S['meta']['psus'] == 121, 'design')
REMOVED = ('closest of the seven', 'could well read higher', 'colours', 'just past the line', 'og-body-fat-calculator',
           'None measures body fat', 'it doesn’t measure it', 'Equations checked against', 'How do I calculate my body fat percentage at home',
           'Overall, this formula', 'That study used seven sites.', 'even at 60', '(DA Form 5501)', 'CDC calls DXA',
           'differed from DXA by', 'both differences are outside', 'Its standard error is', 'the level CDC’s survey uses (Cedars',
           'For women, the tape method’s waist', 'seven sites, 1.4 points from DXA', 'One published reproduction prints',
           'came to CDC’s DXA scans of', 'US adults aged 16–59', 'newer scanner model')

# ---- the tool, worked out here
NAME = {'tape': 'Tape measure (Navy method)', 'rfm': 'Waist and height (relative fat mass)', 'bmi': 'Height and weight (Deurenberg formula)',
        'sf3': 'Calipers, 3 sites (Jackson–Pollock)', 'sf7': 'Calipers, 7 sites (Jackson–Pollock)'}
SHORT = {'tape': 'Tape measure', 'rfm': 'Waist and height', 'bmi': 'Height and weight', 'sf3': 'Calipers, 3 sites', 'sf7': 'Calipers, 7 sites'}
SITES = {'f3': ['tri', 'supra', 'thigh'], 'm3': ['chest', 'abd', 'thigh'], 'a7': ['chest', 'midax', 'tri', 'sub', 'abd', 'supra', 'thigh']}
CARD = {'low': 'underweight', 'healthy': 'normal', 'high': 'overweight', 'very high': 'obese'}
def grp(a): return '16-19' if a <= 19 else '20-29' if a <= 29 else '30-39' if a <= 39 else '40-49' if a <= 49 else '50-59' if a <= 59 else None
def ggrp(a): return '20-39' if 20 <= a <= 39 else '40-59' if 40 <= a <= 59 else '60-79' if 60 <= a <= 79 else None
def word(s, a): return ('girls' if s == 'f' else 'boys') if a < 20 else ('women' if s == 'f' else 'men')
def nd(g): return g.replace('-', '–', 1)
def expect(c):
    """c: sex, units, method, sites, ft, in, cm, w, age, neck, waist, hips, rwaist, sf (dict), typed (set of panes)."""
    s, metric, m = c['sex'], c['units'] == 'metric', c['method']
    k = 'sf' + c['sites'] if m == 'sf' else m
    age, wv = c['age'], c.get('w') or 0
    H = c['cm'] / 2.54 if metric else c['ft'] * 12 + c['in']
    if not (18 <= age <= 79) or math.floor(age) != age: return {'msg': 'Enter your age in whole years, from 18 to 79.'}
    if not 48 <= H <= 90: return {'msg': 'Enter a height from 4 ft to 7 ft 6 in (122 to 229 cm).'}
    if wv and not ((23 <= wv <= 318) if metric else (50 <= wv <= 700)): return {'msg': 'Enter a weight from 50 to 700 lb (23 to 318 kg), or leave it empty.'}
    cv, u = (1 / 2.54, ' cm') if metric else (1, ' in')
    L = {'n': (20, 76), 'w': (38, 203), 'h': (51, 203)} if metric else {'n': (8, 30), 'w': (15, 80), 'h': (20, 80)}
    inr = lambda x, r: r[0] <= x <= r[1]
    E, M = {}, {}
    n, w, hp = c.get('neck') or 0, c.get('waist') or 0, c.get('hips') or 0
    if not (n and w and (s == 'm' or hp)): M['tape'] = 'Enter your neck and waist' + (' and hips' if s == 'f' else '') + ' for the tape method.'
    elif not inr(n, L['n']) or not inr(w, L['w']) or (s == 'f' and not inr(hp, L['h'])):
        M['tape'] = (f'Check the tape measurements: neck {L["n"][0]} to {L["n"][1]}{u}, waist {L["w"][0]} to {L["w"][1]}{u}'
                     + (f', hips {L["h"][0]} to {L["h"][1]}{u}' if s == 'f' else '') + '.')
    elif s == 'm' and w <= n: M['tape'] = 'For the tape method, your waist needs to be larger than your neck.'
    else: E['tape'] = navy(s, H, n * cv, w * cv, hp * cv)
    rw = c.get('rwaist') or 0
    if not rw: M['rfm'] = 'Enter your waist, measured at the top of your hip bones.'
    elif not inr(rw, L['w']): M['rfm'] = f'Enter a waist from {L["w"][0]} to {L["w"][1]}{u}.'
    else: E['rfm'] = rfm(s, H, rw * cv)
    b = 0
    if wv:
        b = r1(wv / (c['cm'] / 100) ** 2) if metric else r1(703 * wv / (H * H)); E['bmi'] = deur(s, b, age)
    else: M['bmi'] = 'Enter your weight to use the height-and-weight method.'
    ids = SITES['a7'] if c['sites'] == '7' else SITES[s + '3']
    vals = [(c.get('sf') or {}).get(i, 0) for i in ids]
    if any(not v for v in vals): M['sf' + c['sites']] = f'Enter all {c["sites"]} skinfolds, in millimeters.'
    elif any(v < 1 or v > 100 for v in vals): M['sf' + c['sites']] = 'Check the skinfolds: each one 1 to 100 mm.'
    else: E['sf' + c['sites']] = jp(s, c['sites'], sum(vals), age)
    for x in list(E):
        if not 2 <= E[x] <= 70:
            M[x] = f'Those measurements give {d1(E[x])}%, outside what these formulas can estimate. Check the numbers and the units.'; del E[x]
    if k not in E: return {'msg': M[k]}
    v = r1(E[k]); g, gg = grp(age), ggrp(age)
    cc = GAL[s][gg] if gg else None; cg = cat(v, cc) if cc else None
    q = TQ[s][g] if g else None; wd = word(s, age); W = SK[s]
    out = {'card': [f'{v:.1f}%', (cg[0].upper() + cg[1:] + f' on the provisional range for {wd} aged {nd(gg)}') if cg else 'Estimated body fat',
                    NAME[k] + (f', from a BMI of {b:.1f}' if k == 'bmi' else '')],
           'tint': 'bmi-result-card' + (' ' + CARD[cg] if cg else ''), 'notes': []}
    N = out['notes']
    if k in ('rfm', 'bmi'):
        f = 'rfm' if k == 'rfm' else 'deur'; bn = math.floor(v + 0.5); cal = CAL[f][s].get(bn)
        if cal:
            N.append(f'Among US {W} aged 20 to 59 whose {"waist-and-height" if k == "rfm" else "height-and-weight"} estimate was within a point of {bn}%, '
                     f'CDC’s DXA scans read {cal[0]:.1f}% to {cal[2]:.1f}% for the middle half, with a median of {cal[1]:.1f}% ({cal[3]:,} {W}; our calculation). '
                     'Trained technicians measured them; measuring yourself adds some error.')
        else:
            N.append(f'Fewer than 30 US {W} aged 20 to 59 had an estimate within a point of {bn}%, too few to check this one on CDC’s scans.')
        N.append(f'Across all US {W} aged 20 to 59, this formula came within 5 points of the scan for {W5N[f][W]}%.'
                 + (f' It tends to read high: on average by {sg(BIAS["rfm"][W])[1:]} points.' if k == 'rfm' else '')
                 + (' CDC scanned adults only up to age 59.' if age > 59 else '') + (' Its authors built it on adults aged 20 and over.' if k == 'rfm' and age < 20 else ''))
        out['bin'] = (bn, cal)
    elif k == 'tape':
        N.append('CDC’s survey didn’t measure the neck, so this method can’t be checked on its scans. In 1,407 US Army recruits at the start of basic '
                 'training, it read 6.0 points below a DXA scan on average, in women and in men (Foulis et al., 2023). Measuring yourself at home can add more error.')
    else:
        N.append('CDC’s survey didn’t measure skinfolds, so this method can’t be checked on its scans. In 437 college students, seven-site skinfolds '
                 'read 1.4 points below DXA on average, and the average miss was 11.7% of the scan’s reading (Burns et al., 2019).'
                 + (' That study used seven sites; you entered three.' if k == 'sf3' else '') + ' Measuring yourself at home can add more error.')
    N.append(f'On CDC’s scans, {share_txt(more_at(P["tool"]["more"][s][g], v))} of US {wd} aged {nd(g)} measured more body fat than {v:.1f}%. Bar: their '
             f'middle half (darker) and 10th to 90th percentile; solid line: their median, {q[2]:.1f}%.' if q else
             'CDC’s scans stopped at age 59, so there is no US comparison at your age.')
    N.append(f'{v:.1f}% is {cg} on the provisional ranges for {wd} aged {nd(gg)}: healthy is {rng(cc, "healthy")} (Gallagher et al., 2000).' if cc else
             'The provisional ranges start at age 20.')
    if q or cc:
        N.append(('The share and the range treat' if q and cc else 'The share treats' if q else 'The range treats')
                 + ' this estimate as if it were a scan reading, so ' + ('they are' if q and cc else 'it is') + ' only as close as the estimate.')
    if wv:
        fm = wv * v / 100; ln = wv - fm
        one = (lambda x: f'{d1(x)} kg ({d1(x / 0.45359237)} lb)') if metric else (lambda x: f'{d1(x)} lb ({d1(x * 0.45359237)} kg)')
        N.append(f'At {jstr(r1(wv))}{" kg" if metric else " lb"} and {v:.1f}% body fat: about {one(fm)} of fat; the other {one(ln)} is lean mass. '
                 'Both are only as close as the estimate.')
    rows = [x for x in E if x != k and (x == 'bmi' or (('sf' if x in ('sf3', 'sf7') else x) in c.get('typed', set())))]
    out['others'] = [[SHORT[x] + ('Shown above' if x == k else '') + ('Within 5 points of CDC’s scans for ' +
                      str(W5N['rfm' if x == 'rfm' else 'deur'][W]) + f'% of US {W} aged 20 to 59' if x in ('rfm', 'bmi') else 'Not checked on CDC’s scans'),
                      d1(E[x]) + '%', x == k] for x in [k] + rows] if rows else []
    lo = min(10, math.floor(min((q or [v])[0], v) / 5) * 5); hi = max(50, math.ceil(max((q or [v] * 5)[-1], v) / 5) * 5)
    out['ticks'] = [f'You {v:.1f}%'] + [f'{x}%' for x in range(lo, hi + 1, 10)]
    return out

D0 = dict(sex='f', units='us', method='tape', sites='3', ft=5, **{'in': 4}, cm=None, w=150, age=35, neck=13, waist=31, hips=40, rwaist=None, sf=None, typed=set())
def case(**kw):
    c = {**D0, 'typed': set()}; c.update(kw); return c
CASES = [
    case(),                                                                              # 0 the worked example
    case(method='rfm', rwaist=34, typed={'rfm'}),                                        # 1 the example's waist and height
    case(method='bmi'),                                                                  # 2 the example's height and weight
    case(sex='m', ft=5, **{'in': 10}, w=180, age=40, neck=16, waist=34, hips=None, typed={'tape'}),
    case(sex='m', units='metric', method='rfm', cm=178, w=80, age=50, neck=None, waist=None, hips=None, rwaist=90, typed={'rfm'}),
    case(units='metric', cm=165, w=62, age=28, neck=33, waist=74, hips=100, typed={'tape'}),
    case(method='bmi', ft=5, **{'in': 6}, w=180, age=45),
    case(sex='m', method='bmi', w=None),                                                 # refusal: no weight
    case(method='sf', sf={'tri': 20, 'supra': 15, 'thigh': 25}, age=30, typed={'sf'}),
    case(sex='m', method='sf', sites='7', ft=5, **{'in': 11}, w=175, age=25, neck=None, waist=None, hips=None,
         sf={'chest': 10, 'midax': 12, 'tri': 9, 'sub': 14, 'abd': 20, 'supra': 12, 'thigh': 11}, typed={'sf'}),
    case(method='sf', sites='7', age=45, w=170, sf={'chest': 12, 'midax': 14, 'tri': 22, 'sub': 18, 'abd': 26, 'supra': 20, 'thigh': 30},
         typed={'sf'}),                                                                  # 7 sites, woman
    case(sex='m', method='sf', ft=6, **{'in': 1}, w=200, age=52, neck=None, waist=None, hips=None,
         sf={'chest': 15, 'abd': 28, 'thigh': 18}, typed={'sf'}),                         # 3 sites, man
    case(age=65, typed={'tape'}),                                                        # no US comparison
    case(sex='m', method='rfm', age=19, ft=5, **{'in': 9}, w=160, neck=None, waist=None, hips=None, rwaist=33, typed={'rfm'}),
    case(age=17), case(ft=3, **{'in': 0}), case(w=30), case(age=35.5),                  # refusals
    case(sex='m', neck=16, waist=15.5, hips=None, typed={'tape'}),                        # waist not above the neck
    case(neck=5, typed={'tape'}),                                                        # neck out of range
    case(method='rfm', rwaist=100, typed={'rfm'}),                                       # waist out of range
    case(sex='m', neck=20, waist=21, hips=None, typed={'tape'}),                          # implausible estimate
    case(method='sf', sf={'tri': 20, 'supra': 15}, typed={'sf'}),                        # a missing skinfold
    case(method='rfm', ft=5, **{'in': 0}, rwaist=60, typed={'rfm'}),                     # past the calibration's last window
    case(sex='m', method='bmi', ft=5, **{'in': 6}, w=300, age=59),                       # Deurenberg high tail, man
    # the tape values typed in, then the method switched: the tape estimate joins the other estimates
    case(method='rfm', rwaist=34, waist=30, typed={'rfm', 'tape'}),
]
E0 = expect(CASES[0])
ok(E0['card'] == ['33.0%', 'High on the provisional range for women aged 20–39', 'Tape measure (Navy method)'] and E0['tint'] == 'bmi-result-card overweight', f'typed-in card {E0["card"]}')
ok(E0['others'] == [['Tape measureShown aboveNot checked on CDC’s scans', '33.0%', True],
                    ['Height and weightWithin 5 points of CDC’s scans for 62% of US women aged 20 to 59', '33.5%', False]], f'typed-in other estimates {E0["others"]}')
ok(expect(CASES[1])['bin'] == (38, [33.7, 36.1, 38.5, 543]) and expect(CASES[2])['bin'] == (34, [34.0, 36.8, 39.5, 446]), 'typed-in windows')

# ---- the page
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    raw = pg.request.get(URL).text()
    ok('{TODAY}' not in raw, '{TODAY} placeholder left in the page')
    ok('<style' not in raw and '<article' not in raw, 'page-level style or an <article> wrapper')
    mainsrc = raw[raw.index('<main'):raw.index('</main>')]
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', mainsrc), 'inline style in <main>')
    ok('bodyfatpercentagecalc' not in raw, 'link to the sister site (D-15)')
    body = re.sub(r'\s+', ' ', pg.inner_text('main') + ' ' + ' '.join(pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')))
    for s_ in PROSE: ok(s_ in body, f'prose not found: {s_!r}')
    for s_ in REMOVED: ok(s_ not in body and s_ not in raw, f'removed wording back on the page: {s_!r}')
    # the tool's formulas exactly as published (a coefficient typo too small to move a printed case still fails here)
    for f_ in ("86.010*lg(w-n)-70.041*lg(h)+36.76", "163.205*lg(w+hp-n)-97.684*lg(h)-78.387", "64-20*h/w+(s==='f'?12:0)",
               "1.20*b+0.23*a-10.8*(s==='m'?1:0)-5.4", "1.112-0.00043499*sum+0.00000055*sum*sum-0.00028826*a",
               "1.097-0.00046971*sum+0.00000056*sum*sum-0.00012828*a", "1.10938-0.0008267*sum+0.0000016*sum*sum-0.0002574*a",
               "1.0994921-0.0009929*sum+0.0000023*sum*sum-0.0001392*a", "return 495/d-450;"):
        ok(raw.count(f_) == 1, f'tool formula not as published: {f_}')
    # the menu
    cur = pg.eval_on_selector_all('header a[aria-current="page"]', 'as => as.map(a => [a.getAttribute("href"), a.className])')
    ok(cur == [['/body-fat-calculator/', 'active'], ['/body-fat-calculator/', 'active']], f'menu current page {cur}')

    # Tables.
    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim()))])""")
    tb = {cap: rws for cap, rws in tables}
    ok(len(tables) == 4, f'{len(tables)} tables')
    for f, name in (('rfm', 'Waist and height'), ('deur', 'Height and weight')):
        want = [['Within 3 points'] + [f'{h1d(F[f][s]["within3"]["pct"])}%' for s in SX], ['Within 5 points'] + [f'{h1d(W5[f][s])}%' for s in SX],
                ['Typical miss points'] + [h1d(MAE[f][s]) for s in SX], ['Average error points'] + [sg(BIAS[f][s]) for s in SX],
                ['Average error by group (points)']] + [[lab] + [sg(gb(f, s, k)['mean']) for s in SX] for k, lab in GROUPS]
        got = tb.get(f'{name} compared with CDC’s scans, US adults aged 20 to 59', [])
        ok(got == want, f'{name} table {got} vs {want}')
    for k, word_ in (('f', 'women'), ('m', 'men')):
        want = [[lab] + [rng(GAL[k][g], x) for g in ('20-39', '40-59', '60-79')]
                for x, lab in (('low', 'Low'), ('healthy', 'Healthy'), ('high', 'High'), ('very high', 'Very high'))]
        got = tb.get(f'Provisional body fat ranges for {word_}, by age', [])
        ok(got == want, f'ranges {word_} {got} vs {want}')
    ok(tb.get('Provisional body fat ranges for women, by age', [[]])[1][1:] == ['21–32.9%', '23–33.9%', '24–35.9%'], 'typed-in healthy ranges')

    # Figures.
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => ({id: s.getAttribute('aria-labelledby'),
        desc: s.querySelector('desc').textContent, circles: [...s.querySelectorAll('circle')].map(c => [+c.getAttribute('cx'), +c.getAttribute('cy')]),
        rects: [...s.querySelectorAll('rect')].map(r => [+r.getAttribute('x'), +r.getAttribute('width'), r.querySelector('title') ? r.querySelector('title').textContent : '']),
        lines: [...s.querySelectorAll('line')].map(l => [+l.getAttribute('x1'), +l.getAttribute('x2'), l.getAttribute('stroke'), +l.getAttribute('stroke-width')])}))""")
    ok([f_['id'] for f_ in figs] == ['ex-t ex-d', 'acc-t acc-d'], f'figure ids {[f_["id"] for f_ in figs]}')
    ex, acc = figs[0], figs[1]
    exx = lambda v: 14 + (v - 20) * 292 / 30
    ok(len(ex['circles']) == 3 and all(abs(cx - exx(r1(v))) < 0.06 for (cx, _), v in zip(ex['circles'], (EX, EXD, EXR))), f'example dots {ex["circles"]}')
    for cal_, lab in ((CD, 'height and weight'), (CR, 'waist and height')):
        hit = [r for r in ex['rects'] if r[2].startswith(f'CDC scans of US women whose {lab} estimate')]
        ok(len(hit) == 1 and abs(hit[0][0] - exx(cal_[0])) < 0.06 and abs(hit[0][1] - (exx(cal_[2]) - exx(cal_[0]))) < 0.06
           and f'middle half {cal_[0]:.1f}–{cal_[2]:.1f}%, median {cal_[1]:.1f}% ({cal_[3]} women)' in hit[0][2], f'example box {lab} {hit}')
        ok(any(abs(l[0] - exx(cal_[1])) < 0.06 and l[2] == '#111827' for l in ex['lines']), f'example median tick {lab}')
    ok(f'The tape measure gives {h1d(EX)}%, the height-and-weight formula {h1d(EXD)}% and the waist-and-height formula {h1d(EXR)}%.' in ex['desc'], 'example desc')
    ax = lambda e: 16 + (e + 10) * 288 / 20
    for f, s in (('rfm', 'women'), ('rfm', 'men'), ('deur', 'women'), ('deur', 'men')):
        q = F[f][s]['err_q']; col = '#be185d' if s == 'women' else '#4338ca'
        ok(any(abs(r[0] - ax(q['p25'])) < 0.06 and abs(r[1] - (ax(q['p75']) - ax(q['p25']))) < 0.06 for r in acc['rects']), f'accuracy box {f} {s}')
        ok(any(abs(l[0] - ax(q['p10'])) < 0.06 and abs(l[1] - ax(q['p90'])) < 0.06 and l[2] == col for l in acc['lines']), f'accuracy line {f} {s}')
        ok(any(abs(l[0] - ax(q['p50'])) < 0.06 and l[2] == '#111827' for l in acc['lines']), f'accuracy median {f} {s}')
        lab = ('Waist and height' if f == 'rfm' else 'Height and weight') + f', {s}'
        ok(f'{lab}: median {sg(q["p50"])}, middle half {sg(q["p25"])} to {sg(q["p75"])}, 10th to 90th percentile {sg(q["p10"])} to {sg(q["p90"])}.' in acc['desc'], f'accuracy desc {lab}')
    ok(sum(1 for l in acc['lines'] if abs(l[0] - ax(0)) < 0.06 and abs(l[1] - ax(0)) < 0.06 and l[2] == '#4b5563') == 4, 'zero line per row')

    # The tool's data.
    D = pg.evaluate('window.BFC')
    ok(D['p0'] == P0 and D['more'] == {k: {g: P['tool']['more'][k][g] for g in UGR} for k in 'fm'} and D['q'] == TQ, 'tool data: US shares and percentiles')
    ok(D['gal'] == GAL and D['n'] == {k: {g: BA[k][g]['n'] for g in UGR} for k in 'fm'}, 'tool data: ranges and counts')
    ok(D['cal'] == {f: {k: {str(b): v for b, v in sorted(d.items())} for k, d in CAL[f].items()} for f in CAL}, 'tool data: calibration')
    ok(D['w5'] == {f: {k: W5N[f][SK[k]] for k in 'fm'} for f in W5N} and D['rb'] == {k: sg(BIAS['rfm'][SK[k]])[1:] for k in 'fm'}, 'tool data: checks')
    ok(not pg.is_visible('#bfc-metric') and pg.is_visible('#bfc-us') and pg.is_visible('#bfc-p-tape') and
       not any(pg.is_visible(f'#bfc-p-{p_}') for p_ in ('rfm', 'bmi', 'sf')), 'starting panes')

    # The tool: cases (a fresh page each, so typed panes start untouched). Main fields are typed; a pane's fields are
    # typed only when the case says so, otherwise set without an input event (as the starting values are).
    def setv(sel, v, typed):
        val = '' if v is None else jstr(v)
        if typed: pg.fill(sel, val)
        else: pg.evaluate('([s, v]) => { document.querySelector(s).value = v; }', [sel, val])
    n_result = 0
    for i, c in enumerate(CASES):
        pg.goto(URL, wait_until='load')
        pg.click(f'#bfc [data-sex="{c["sex"]}"]')
        if c['units'] == 'metric': pg.click('#bfc [data-units="metric"]')
        if c['units'] == 'us': setv('#bfc-ft', c['ft'], True); setv('#bfc-in', c['in'], True)
        else: setv('#bfc-cm', c['cm'], True)
        setv('#bfc-w', c['w'], True); setv('#bfc-age', c['age'], True)
        for k_ in ('neck', 'waist', 'hips'):                                   # the tape pane shows first
            setv(f'#bfc-{k_}', c[k_], 'tape' in c['typed'] and not (k_ == 'hips' and c['sex'] == 'm'))
        pg.click('#bfc [data-method="rfm"]'); setv('#bfc-rwaist', c['rwaist'], 'rfm' in c['typed'])
        pg.click('#bfc [data-method="sf"]'); pg.click(f'#bfc [data-sites="{c["sites"]}"]')
        for k_ in SITES['a7']: setv(f'#bfc-sf-{k_}', (c['sf'] or {}).get(k_), 'sf' in c['typed'] and k_ in (c['sf'] or {}))
        pg.click(f'#bfc [data-method="{c["method"]}"]')
        pg.click('#bfc-go'); pg.wait_for_timeout(50)
        E = expect(c)
        got = pg.evaluate("""() => { const o = document.getElementById('bfc-out'), q = s => o.querySelector(s);
            return {vis: o.classList.contains('visible'), text: o.innerText.replace(/\\s+/g, ' ').trim(),
                    card: q('.bmi-result-card') ? [q('.bmi-value').textContent, q('.bmi-category').textContent, q('.bmi-range').textContent] : null,
                    tint: q('.bmi-result-card') ? q('.bmi-result-card').className : null,
                    notes: [...o.querySelectorAll('.er-note')].map(n => n.textContent),
                    heads: [...o.querySelectorAll('h2')].map(h => h.textContent),
                    ticks: q('svg') ? [...q('svg').querySelectorAll('text')].map(t => t.textContent) : null,
                    others: q('.er-table') ? [...q('.er-table').querySelectorAll('tbody tr')].map(r => [r.children[0].textContent,
                            r.children[1].textContent, r.classList.contains('er-active')]) : []}; }""")
        ok(got['vis'], f'case {i}: no output')
        if 'msg' in E:
            ok(got['text'] == E['msg'] and got['card'] is None, f'case {i}: message {got["text"]!r} vs {E["msg"]!r}'); continue
        ok(got['card'] == E['card'], f'case {i}: card {got["card"]} vs {E["card"]}')
        ok(got['tint'] == E['tint'], f'case {i}: tint {got["tint"]} vs {E["tint"]}')
        ok(got['notes'][:len(E['notes'])] == E['notes'], f'case {i}: notes\n  got  {got["notes"]}\n  want {E["notes"]}')
        ok(got['ticks'] == E['ticks'], f'case {i}: figure labels {got["ticks"]} vs {E["ticks"]}')
        ok(got['others'] == E['others'], f'case {i}: other estimates {got["others"]} vs {E["others"]}')
        want_h = ['How close this estimate is likely to be', f'Where {E["card"][0]} falls'] + (['Fat and lean mass'] if c['w'] else []) + (['Your other estimates'] if E['others'] else [])
        ok(got['heads'] == want_h, f'case {i}: headings {got["heads"]}')
        n_result += 1
    ok(n_result == sum(1 for c in CASES if 'msg' not in expect(c)) == 16, f'{n_result} cases with a result')

    # The switches.
    pg.goto(URL, wait_until='load')
    card = lambda: pg.evaluate("() => [...document.querySelectorAll('#bfc-out .bmi-result-card div')].map(d => d.textContent)")
    pg.click('#bfc-go'); us_card = card()
    pg.click('#bfc [data-units="metric"]')
    ok((pg.input_value('#bfc-cm'), pg.input_value('#bfc-w'), pg.input_value('#bfc-neck'), pg.input_value('#bfc-waist'), pg.input_value('#bfc-hips'))
       == ('162.6', '68', '33', '78.7', '101.6'), 'switch to metric converts to 0.1')
    ok(pg.inner_text('#bfc-w-l') == 'Weight (kg)' and pg.inner_text('#bfc-neck-l') == 'Neck (cm)' and pg.is_visible('#bfc-metric') and not pg.is_visible('#bfc-us'), 'metric labels and rows')
    pg.click('#bfc-go'); ok(card() == us_card == E0['card'], f'switching units changed the result: {card()} vs {us_card}')
    pg.click('#bfc [data-units="us"]')
    ok((pg.input_value('#bfc-ft'), pg.input_value('#bfc-in'), pg.input_value('#bfc-w'), pg.input_value('#bfc-neck'), pg.input_value('#bfc-waist'),
        pg.input_value('#bfc-hips')) == ('5', '4', '150', '13', '31', '40'), 'switch back to US restores the numbers')
    pg.fill('#bfc-in', '4.5'); pg.click('#bfc [data-units="metric"]')
    ok(pg.input_value('#bfc-cm') == '163.8', f'5 ft 4.5 in in cm: {pg.input_value("#bfc-cm")}')
    pg.click('#bfc [data-units="us"]')
    ok((pg.input_value('#bfc-ft'), pg.input_value('#bfc-in')) == ('5', '4.5'), 'round trip from 5 ft 4.5 in')
    pg.click('#bfc [data-units="metric"]'); pg.fill('#bfc-cm', '163'); pg.click('#bfc [data-units="us"]')
    ok((pg.input_value('#bfc-ft'), pg.input_value('#bfc-in')) == ('5', '4.2'), f'163 cm in ft and in: {pg.input_value("#bfc-ft")} {pg.input_value("#bfc-in")}')
    pg.click('#bfc [data-units="metric"]')
    ok(pg.input_value('#bfc-cm') == '163', f'round trip from 163 cm: {pg.input_value("#bfc-cm")}')
    pg.fill('#bfc-w', '68.3'); pg.click('#bfc [data-units="us"]'); w_lb = pg.input_value('#bfc-w')
    pg.fill('#bfc-w', w_lb); pg.click('#bfc [data-units="metric"]')
    ok((w_lb, pg.input_value('#bfc-w')) == ('150.6', '68.3'), f'68.3 kg retyped in lb and back: {w_lb} {pg.input_value("#bfc-w")}')
    pg.click('#bfc [data-units="us"]')
    pg.click('#bfc [data-sex="m"]')
    ok(not pg.is_visible('#bfc-hips-g') and pg.inner_text('#bfc-tape-hint') == 'Neck just below the Adam’s apple, waist at the navel.', 'men: no hips')
    pg.click('#bfc [data-method="sf"]')
    vis = [k_ for k_ in SITES['a7'] if pg.is_visible(f'#bfc-sf-{k_}-g')]
    ok(vis == ['chest', 'abd', 'thigh'], f'men 3 sites {vis}')
    pg.click('#bfc [data-sex="f"]')
    vis = [k_ for k_ in SITES['a7'] if pg.is_visible(f'#bfc-sf-{k_}-g')]
    ok(vis == ['tri', 'supra', 'thigh'] and pg.is_visible('#bfc-hips-g') is False, f'women 3 sites {vis}')        # hips: tape pane hidden
    pg.click('#bfc [data-sites="7"]')
    ok([k_ for k_ in SITES['a7'] if pg.is_visible(f'#bfc-sf-{k_}-g')] == SITES['a7'], '7 sites')
    for m_ in ('tape', 'rfm', 'bmi', 'sf'):
        pg.click(f'#bfc [data-method="{m_}"]')
        ok([p_ for p_ in ('tape', 'rfm', 'bmi', 'sf') if pg.is_visible(f'#bfc-p-{p_}')] == [m_], f'pane {m_}')
        ok(pg.get_attribute(f'#bfc [data-method="{m_}"]', 'aria-pressed') == 'true', f'aria-pressed {m_}')
    ok(pg.get_attribute('#bfc-w', 'placeholder') == 'Optional', 'weight placeholder')

    # Head and JSON-LD.
    head = pg.evaluate("""() => ({title: document.title, desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content), canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content), ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        twt: (document.querySelector('meta[name="twitter:title"]') || {}).content || '', tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content),
        ogd: document.querySelector('meta[property="og:description"]').content, twd: (document.querySelector('meta[name="twitter:description"]') || {}).content || ''})""")
    PI = {r: f'{SITE}/assets/images/preferred/body-fat-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['title'] == 'Body Fat Calculator: 4 Methods Compared With DXA Scans', f'title {head["title"]!r}')
    ok(len(head['desc']) <= 160 and head['desc'].startswith('Free body fat calculator: tape measure (Navy), waist and height, BMI or calipers.'), f'description {head["desc"]!r}')
    ok(head['robots'] == ['max-image-preview:large'] and head['canon'] == SITE + '/body-fat-calculator/', f'robots / canonical {head}')
    ok(head['og'] == [PI['16x9']] and head['tw'] == [PI['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter {head}')
    ok(head['ogd'] == head['twd'] and head['ogd'].endswith('see how close each method comes to a DXA scan: CDC’s scans for two formulas, published studies for the tape and calipers.'),
       f'og/twitter description {head["ogd"]!r}')
    ok(head['ogalt'].startswith('Chart: how far two body fat formulas were from DXA scans') and
       head['twt'] == 'Body fat calculator: four methods and how close each gets to a DXA scan', f'og alt / twitter title {head}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/body-fat-calculator-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/body-fat-calculator/og-body-fat-calculator.png').status == 404, 'old OG image still served')
    sm = pg.request.get(base + '/sitemap.xml').text()
    ent = re.search(r'<url><loc>https://calculatemybmi\.net/body-fat-calculator/</loc>(.*?)</url>', sm)
    lastmod = re.search(r'<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>', ent.group(1)).group(1) if ent else None
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['WebPage', 'WebApplication', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    G = {x['@type']: x for x in ld[0]['@graph']}
    h1 = pg.inner_text('h1')
    ok(h1 == G['WebApplication']['name'] == 'Body Fat Calculator', 'H1 / WebApplication name')
    ok(G['WebApplication']['image'] == [PI['1x1'], PI['4x3'], PI['16x9']] and G['WebPage']['primaryImageOfPage']['url'] == PI['16x9'], 'image list / primaryImageOfPage')
    ok(G['WebPage']['dateModified'] == lastmod and re.fullmatch(r'\d{4}-\d{2}-\d{2}', lastmod or ''), f'dateModified {G["WebPage"].get("dateModified")!r} vs lastmod {lastmod!r}')
    ok(G['WebApplication']['author']['name'] == 'Marko Visic' and G['WebPage']['mainEntity']['@id'] == SITE + '/body-fat-calculator/#calculator', 'author / mainEntity')
    ok([i['name'] for i in G['BreadcrumbList']['itemListElement']] == ['Home', 'Calculators', h1], 'breadcrumb')
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok(len(visq) == 9 and [[q['name'], q['acceptedAnswer']['text']] for q in G['FAQPage']['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')

    # Links, chips, FAQ.
    hrefs = pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for h_ in sorted({h_.split('#')[0] for h_ in hrefs if h_.startswith('/')}):
        ok(pg.request.get(base + h_).status == 200, f'internal link {h_} does not answer 200')
    for h_ in {h_ for h_ in hrefs if h_.startswith('#')}:
        ok(pg.evaluate('h => !!document.getElementById(h.slice(1))', h_), f'anchor {h_} missing')
    outside = {h_ for h_ in pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))')}
    ok(outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#read-result', '#accuracy', '#tape', '#rfm', '#bmi-method', '#calipers', '#ranges', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    for i, q in enumerate(pg.query_selector_all('.faq-question')):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')

    # Widths, table frames, rendered labels (both figures, and the tool's figure after a calculation).
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
        pg.click('#bfc-go'); pg.wait_for_timeout(60)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : 'results table',
            t.offsetWidth, t.parentElement.clientWidth])""")
        for cap, tw, fw in fits: ok(tw <= fw + 1, f'table scrolls at {w}: {cap} {tw} > {fw}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg, #bfc-out svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom], texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                        shapes: [...svg.querySelectorAll('rect, circle')].map(e => [e.getAttribute('fill'), ...bx(e)])}; })""")
            ok(len(res) == 3, f'{len(res)} figures at {w}')
            for f_ in res:
                L_, T_, R_, B_ = f_['box']
                for j, a in enumerate(f_['texts']):
                    ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f_['texts'][j + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5: fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s_ in f_['shapes']:
                        if a[1] < s_[3] - 0.5 and s_[1] < a[3] - 0.5 and a[2] < s_[4] - 0.5 and s_[2] < a[4] - 0.5: fails.append(f'{w}px label over a shape: {a[0]!r} / {s_[0]}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f_ in fails[:40]: print('FAIL', f_)
sys.exit(1 if fails else 0)
