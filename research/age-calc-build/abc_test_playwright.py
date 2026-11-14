#!/usr/bin/env python3
"""/age-bmi-calculator/ checks in Chromium (CMB-045). Needs Python Playwright + Chromium.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/age-calc-build/abc_test_playwright.py http://localhost:8000 research/age-calc-build/abc_stats.json
Every expected value is worked out here from the data files (abc_stats.json, research/average-weight/avgw_results.json,
research/body-fat-chart-build/bfpc_stats.json, research/kids-build/kids_stats.json, the weight-table gate's rule), not
read from the generator:
  - the tables: every cell of the two percentile tables, the decade table (median, middle half) and the two average
    tables (BMI, weight in lb and kg, waist in in and cm) against the files;
  - every number sentence: the expected fragments are rebuilt from the files and must be on the page; then every number
    in the visible text outside the tool, the tables and the figure must be one of the expected values or a listed
    constant (cut-offs, years, ages, source numbers), so a stray figure fails;
  - the figure: each decade's bars, lines and median ticks at the positions the percentiles give, the hover titles, the
    description, the legend; rendered labels inside the figure and off each other and off every shape;
  - the calculator, typed in: the starting values; for women and men at ages 20, 39, 40, 59, 60, 79, 80 and 100, BMIs
    from about 9 to 63, the rank box (value, sentence, marker, median, source) against the US rank rule read off the
    curves here; the decade box at every decade in US units and in metric; ages 2, 15 and 19 (no adult result, the note
    with its link), 20 and an empty age; the Winter line at 65 and over only, in the DEVLOG §4 wording; the unit switch;
  - labels name their fields and a click focuses the field;
  - layout: the page never wider than the screen at 320, 360, 390 and 1280, before and after Calculate; Calculate ends
    above the fold at 390 x 844 and 360 x 800; tables fit their frames from 360 up and stay on screen at 320;
  - 8 FAQ in order, the JSON-LD equal to the visible answers, one tap opens an answer and one closes it;
  - head: the title kept (D-28), description, OG and Twitter text and images, robots, the JSON-LD graph; the preferred
    images at size; the old OG image gone; everything outside <main> except those tags equal to origin/main's;
  - structure: H1 kept, sections directly in main .container, no <article>, no inline style in <main> outside the figure;
  - links: internal links answer 200 and anchors exist; outside links are registry URLs; nothing from the NEVER list on
    the page, in the head, in the JSON-LD or in calculator.js.
Every check runs; nothing is skipped. Exit 1 on any failure."""
import csv
import html
import json
import math
import os
import re
import struct
import subprocess
import sys
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

from playwright.sync_api import sync_playwright

base, stats = sys.argv[1].rstrip('/'), sys.argv[2]
BUILD = os.path.dirname(os.path.abspath(stats))
ROOT = os.path.abspath(os.path.join(BUILD, '..', '..'))
S = json.load(open(stats, encoding='utf-8'))
AVGW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json'), encoding='utf-8'))
BFP = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json'), encoding='utf-8'))
KIDS = json.load(open(os.path.join(ROOT, 'research/kids-build/kids_stats.json'), encoding='utf-8'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds                 # noqa: E402

REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()}
PATH = '/age-bmi-calculator/'
URL = base + PATH
SITE = 'https://calculatemybmi.net'
TITLE = 'BMI Calculator by Age & Gender (kg or lbs): US Averages'
H1 = 'BMI Calculator by Age'
PI = {r: f'{SITE}/assets/images/preferred/age-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
SIZES = {'1x1': (1200, 1200), '4x3': (1200, 900), '16x9': (1200, 675)}
FAQ_Q = ['What is the correct BMI for my age?', 'What is a good BMI for a senior over 70?', 'How to calculate BMI for seniors?',
         'How to calculate BMI including age?', 'What is the ideal BMI for females by age?', 'What is the average BMI by age?',
         'Does losing height change my BMI?', 'Is BMI less accurate for older adults?']
LABEL_IDS = ['age-height-ft', 'age-height-in', 'age-weight-lbs', 'age-height-cm', 'age-weight-kg', 'age-years', 'age-sex']
NEVER = [r'plateau', r'lowest (all-cause )?mortality', r'23[–-]33', r'WHO adult range', r'obesity paradox', r'Flegal',
         r'\bsleep\b', r'age-adjusted (range|cut-?off)', r'rose above 33', r'observed low-mortality', r'U-shaped',
         r'hazard ratio', r'your doctor can say', r'\bideal BMI for your age\b']
WINTER = ('compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 '
          '(Winter et al., 2014)')

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def norm(t):
    t = (t or '').replace(' ', ' ').replace('­', '').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', t).strip()


def d1(x): return str(Decimal(repr(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None


# ---------------------------------------------------------------- expected values, from the files
SEXES = ('women', 'men')
GRPS = ('20-39', '40-59', '60+')
GW = {'20-39': '20 to 39', '40-59': '40 to 59', '60+': '60 and over'}
AGES = ('20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')
C, G, DEC, DIF = S['curves'], S['groups'], S['decades'], S['differences']
AV = {s: {d: AVGW[s]['age'][d.replace('-', '–')] for d in AGES} for s in SEXES}
MED = {s: {g: d1(G[f'{s}_{g}']['p50']) for g in GRPS} for s in SEXES}
NG = {s: {g: G[f'{s}_{g}']['n'] for g in GRPS} for s in SEXES}
NTOT = G['women']['n'] + G['men']['n']
DMEAN = {s: {d: d1(AV[s][d]['bmi']['mean']) for d in AGES} for s in SEXES}
for s in SEXES:                                                       # the stats file's decade means are avgw's
    for d in AGES:
        ok(abs(DEC[s][d]['mean'] - AV[s][d]['bmi']['mean']) < 1e-3 and DEC[s][d]['n'] == AV[s][d]['bmi']['n'],
           f'stats: {s} {d} mean/n differ from avgw_results.json')
WT = {s: {d: (d1(AV[s][d]['wt']['mean']), d1(AV[s][d]['wt']['mean'] / 2.2046)) for d in AGES} for s in SEXES}
WS = {s: {d: (d1(AV[s][d]['waist']['mean']), d1(AV[s][d]['waist']['mean'] * 2.54)) for d in AGES} for s in SEXES}
HEALTHY = {s: {d: d1(DEC[s][d]['healthy']['pct']) for d in AGES} for s in SEXES}
LOWHI = {s: (min(DMEAN[s].values(), key=float), max(DMEAN[s].values(), key=float)) for s in SEXES}
ok(all(DEC[s][d]['ci95'][0] > 25 for s in SEXES for d in AGES), 'a decade mean’s 95% interval reaches 25')
for s in SEXES:
    for k in ('mean_40-49_minus_20-29', 'mean_50-59_minus_20-29', 'mean_80+_minus_50-59', 'healthy_20-29_minus_50-59'):
        ok(DIF[f'{s}_{k}']['excludes_0'], f'stated difference {s} {k} does not exclude 0')
DB = {g: d1(S['db508'][f'adults_{g}']['pct']) for g in GRPS}
ok(DB == {'20-39': '35.5', '40-59': '46.4', '60+': '38.9'}, f'Data Brief 508 shares not reproduced: {DB}')
BA = BFP['by_age']
BF = {s: (d1(BA[s]['20-29']['mean4']), d1(BA[s]['50-59']['mean4'])) for s in 'mf'}
ok(all(BFP['diff']['age'][s]['50s_minus_20s']['excludes_0'] for s in 'mf'), 'DXA 50s-20s difference does not exclude 0')
GIRL = KIDS['anchors']['girl-10-98']


def pct(q, b):
    if b <= q[0]:
        return 0.0
    if b >= q[98]:
        return 100.0
    for i in range(98):
        if b < q[i + 1]:
            return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0


def rk(q, b): return pct(q, round(b * 10 - 1) / 10), 100 - pct(q, b)
def nn(x): return 99 if x > 99 else math.floor(x + 0.5)
def lab(r): return f'lower than {nn(r[1])}%' if r[0] < 1 else f'higher than {nn(r[0])}%'


# Worked example: a 45-year-old woman, 5'6", 170 lb.
EXB = r1(170 * 703 / 66 ** 2)
HB_LB, HB_KG = gate_bounds('lb', 66, 66 * 2.54, 1), gate_bounds('kg', 66, 66 * 2.54, 1)
FROM = [gate_bounds('lb', 66, 66 * 2.54, i)[0] for i in (2, 3, 4, 5)]
EXR = {g: nn(rk(C[f'women_{g}'], EXB)[0]) for g in GRPS}
EXH = nn(rk(C['women_40-59'], EXB)[1])
EXM = nn(rk(C['men_40-59'], EXB)[0])
PRIME = f'{math.floor(EXB * 4 + 0.5) / 100:.2f}'
PONDERAL = f'{(170 / 2.20462) / (1.6764 ** 3):.1f}'
LOSS = d1(25 * 68 ** 2 / 703 * 703 / 66 ** 2 - 25)

FRAG = [                                                              # number sentences rebuilt from the files
    f"The median BMI of US women is {MED['women']['20-39']} at ages 20 to 39, {MED['women']['40-59']} at 40 to 59 and "
    f"{MED['women']['60+']} at 60 and over; of US men, {MED['men']['20-39']}, {MED['men']['40-59']} and {MED['men']['60+']} "
    "(CDC measurements, 2021-2023)",
    f"the average BMI of US women and of US men is {min(LOWHI['women'][0], LOWHI['men'][0], key=float)} or more, in the "
    "overweight range",
    f"CDC measurements of {NTOT:,} adults, 2021-2023",
    f"a 45-year-old woman, 5'6\" ({d1(66 * 2.54)} cm) and 170 lb ({d1(170 / 2.20462)} kg)",
    f"{170} x 703 / 66² = {EXB}",
    f"Healthy weight at 5'6\": {HB_LB[0]}-{HB_LB[1]} lb ({HB_KG[0]}-{HB_KG[1]} kg)",
    f"Compared with US women aged 40 to 59: higher than {EXR['40-59']}%",
    f"About {EXR['40-59']}% of women aged 40 to 59, measured by CDC in 2021-2023, have a lower BMI and about {EXH}% a higher one",
    f"Her BMI is under the median for her age group, {MED['women']['40-59']}, and still overweight",
    f"higher than about {EXR['20-39']}% of women aged 20 to 39, and at 70 higher than about {EXR['60+']}% of women 60 and over",
    f"A man of 45 with the same numbers ranks higher than about {EXM}% of men aged 40 to 59",
    f"Their average BMI is {DMEAN['women']['40-49']}, their average weight {WT['women']['40-49'][0]} lb ({WT['women']['40-49'][1]} kg) "
    f"and their average waist {WS['women']['40-49'][0]} in ({WS['women']['40-49'][1]} cm)",
    f"healthy from {HB_LB[0]} lb, overweight from {FROM[0]} lb, obesity from {FROM[1]} lb, class 2 obesity from {FROM[2]} lb "
    f"and class 3 from {FROM[3]} lb",
    f"BMI Prime {PRIME} and ponderal index {PONDERAL} kg/m³",
    f"weighed and measured {NTOT:,} adults aged 20 and over from August 2021 to August 2023",
    f"for women {MED['women']['20-39']} at ages 20 to 39, {MED['women']['40-59']} at 40 to 59 and {MED['women']['60+']} at 60 "
    f"and over; for men {MED['men']['20-39']}, {MED['men']['40-59']} and {MED['men']['60+']}",
    f"In their 20s, {HEALTHY['women']['20-29']}% of women and {HEALTHY['men']['20-29']}% of men have a BMI in the healthy range; "
    f"in their 50s, {HEALTHY['women']['50-59']}% and {HEALTHY['men']['50-59']}%",
    f"a quarter of men have a BMI of {d1(G['men_40-59']['p25'])} or lower and a quarter {d1(G['men_40-59']['p75'])} or higher",
    f"{min(DEC[s][d]['n'] for s in SEXES for d in AGES)} to {max(DEC[s][d]['n'] for s in SEXES for d in AGES)} people in each decade",
    f"{NG['women']['20-39']:,}, {NG['women']['40-59']:,} and {NG['women']['60+']:,} women and {NG['men']['20-39']:,}, "
    f"{NG['men']['40-59']:,} and {NG['men']['60+']:,} men",
    f"for women from {LOWHI['women'][0]} to {LOWHI['women'][1]} and for men from {LOWHI['men'][0]} to {LOWHI['men'][1]}",
    f"{DB['20-39']}% of adults aged 20 to 39, {DB['40-59']}% at 40 to 59 and {DB['60+']}% at 60 and over",
    f"average body fat was {BF['m'][0]}% for men in their 20s and {BF['m'][1]}% in their 50s, and {BF['f'][0]}% and {BF['f'][1]}% for women",
    f"going from 5'8\" to 5'6\" adds about {LOSS} points at a BMI of 25",
    "meta-analysis of 32 studies covering 197,940 people aged 65 and over, " + WINTER,
    f"US adults aged 70 to 79 have a median BMI of {d1(DEC['women']['70-79']['p50'])} (women) and {d1(DEC['men']['70-79']['p50'])} "
    f"(men), and {HEALTHY['women']['70-79']}% of the women and {HEALTHY['men']['70-79']}% of the men have a BMI of 18.5 to 24.9",
    f"a BMI of {GIRL['bmi']} is in the adult healthy range, but for a {GIRL['years']}-year-old girl it sits at the "
    f"{GIRL['ordinal']}th percentile, which is obesity",
    f"the median BMI is {MED['women']['20-39']} for women and {MED['men']['20-39']} for men at ages 20 to 39, "
    f"{MED['women']['40-59']} and {MED['men']['40-59']} at 40 to 59, and {MED['women']['60+']} for both at 60 and over",
    f"the average BMI ranged from {LOWHI['men'][0]} to {LOWHI['men'][1]} for men and from {LOWHI['women'][0]} to "
    f"{LOWHI['women'][1]} for women",
    f"our calculation for {G['women']['n']:,} women and {G['men']['n']:,} men aged 20 and over",
]
ok(MED['women']['60+'] == MED['men']['60+'], 'the FAQ says "for both" at 60 and over: the medians must be equal')
ok(EXB == 27.4 and EXR['40-59'] < 50 < EXH, 'worked example: under the median')

# every number allowed in the visible text outside the tool, tables and figure: the fragments' numbers plus constants
CONST = {'1', '15', '19', '25.0', '29.9', '30', '49', '75', '80', '85', '90', '95', '99',   # cut-offs, ages, percentiles
         '508', '2004', '2011', '2018', '2024', '2025', '2026'}                              # source numbers and years
ALLOWED = set(CONST)
NUM = re.compile(r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?')
for f in FRAG:
    ALLOWED |= set(NUM.findall(f))
for s in SEXES:
    ALLOWED |= set(MED[s].values())

# ---------------------------------------------------------------- source checks (no browser)
def fetch(path):
    with urllib.request.urlopen(base + path, timeout=20) as r_:
        return r_.read().decode('utf-8')


src = fetch(PATH)                                                     # the page as served, so a break in a served copy shows
head = src[:src.index('</head>')]
main_html = re.search(r'(?s)<main\b.*?</main>', src).group(0)
ok(f'<title>{html.escape(TITLE, quote=False)}</title>' in head, 'title changed (D-28)')
ok(head.count('<meta name="robots" content="max-image-preview:large">') == 1, 'robots max-image-preview')
ok('<link rel="canonical" href="https://calculatemybmi.net/age-bmi-calculator/">' in head, 'canonical')
meta = dict(re.findall(r'<meta (?:name|property)="([^"]+)" content="([^"]*)">', head))
ok(meta.get('og:image') == PI['16x9'] and meta.get('twitter:image') == PI['16x9'], 'og/twitter image = preferred 16:9')
ok(meta.get('og:image:width') == '1200' and meta.get('og:image:height') == '675', 'og:image size 1200x675')
ok('BMI of US women and men in each decade of age' in html.unescape(meta.get('og:image:alt', '')), 'og:image:alt')
desc = html.unescape(meta.get('description', ''))
ok(0 < len(desc) <= 160 and 'by age and gender' in desc and 'kg or lbs' in desc, f'meta description: {desc!r}')
ok(f'{NTOT:,} adults' in html.unescape(meta.get('og:description', '')), 'og:description names the sample')
ok(meta.get('og:title') == meta.get('twitter:title') and meta.get('og:description') == meta.get('twitter:description'),
   'og and twitter text equal')
for r_, (w, h) in SIZES.items():
    p = os.path.join(ROOT, f'assets/images/preferred/age-bmi-calculator-{r_}.png')
    ok(os.path.exists(p) and png_size(open(p, 'rb').read(32)) == (w, h), f'preferred image {r_} at {w}x{h}')
ok(not os.path.exists(os.path.join(ROOT, 'assets/images/og/age-bmi-ucurve.png')), 'old OG image file still there')
ok('age-bmi-ucurve' not in src, 'old OG image still named')
blocks = re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', src)
ok(len(blocks) == 1, f'{len(blocks)} JSON-LD blocks')
LD = json.loads(blocks[0]) if blocks else {'@graph': []}
types = [g.get('@type') for g in LD.get('@graph', [])]
ok(types == ['WebPage', 'WebApplication', 'BreadcrumbList', 'FAQPage'], f'JSON-LD types {types}')
gr = {g['@type']: g for g in LD.get('@graph', [])}
ok(gr.get('WebPage', {}).get('primaryImageOfPage') == {'@type': 'ImageObject', 'url': PI['16x9'], 'width': 1200, 'height': 675},
   'primaryImageOfPage')
ok(gr.get('WebPage', {}).get('name') == TITLE, 'WebPage name = title')
ok(gr.get('WebApplication', {}).get('image') == [PI['1x1'], PI['4x3'], PI['16x9']], 'WebApplication image list')
ok(gr.get('WebApplication', {}).get('name') == H1, 'WebApplication name = H1')
ok([i['name'] for i in gr.get('BreadcrumbList', {}).get('itemListElement', [])] == ['Home', 'Calculators', H1], 'breadcrumb')
ok(not re.search(r'<article\b', main_html), '<article> in main')
ok('style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', main_html), 'inline style in main outside the figure')
whole = norm(html.unescape(re.sub(r'<[^>]+>', ' ', src)))
calcjs = fetch('/assets/js/calculator.js')
age_js = calcjs[calcjs.index('function calculateByAge'):calcjs.index('function calculateKids')]
age_js += calcjs[calcjs.index('function genSummary'):calcjs.index('/* ===== DISPLAY: BMI RESULTS')]
age_js += calcjs[calcjs.index('// 8. Age:'):calcjs.index('// 9. Health')]
for pat in NEVER:
    ok(not re.search(pat, whole, re.I), f'NEVER: {pat} on the page')
    ok(not re.search(pat, html.unescape(age_js), re.I), f'NEVER: {pat} in calculator.js age code')
ok(WINTER.replace('(Winter et al., 2014)', '') in norm(html.unescape(re.sub(r'<[^>]+>', '', age_js))),
   'calculator.js: the 65+ note in the §4 wording')
# outside <main>, the page equals origin/main's except the owned head tags (description, OG, Twitter, JSON-LD)
try:
    old = subprocess.run(['git', 'show', 'origin/main:age-bmi-calculator/index.html'], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout


    def outside(s):
        s = re.sub(r'(?s)<main\b.*?</main>', '<main/>', s)
        s = re.sub(r'(?s)\s*<script type="application/ld\+json">.*?</script>', '', s)
        s = re.sub(r'\s*<meta (?:name|property)="(?:description|og:title|og:description|og:image(?::alt|:width|:height)?|'
                   r'twitter:title|twitter:description|twitter:image)" content="[^"]*">', '', s)
        return s
    ok(outside(old) == outside(src), 'outside <main> the page differs from origin/main beyond the owned head tags')
except subprocess.CalledProcessError:
    ok(False, 'git show origin/main:age-bmi-calculator/index.html failed')

# ---------------------------------------------------------------- browser
TYPE_JS = r'''async (cases) => {
  const P = document.getElementById('panel-age'), q = s => P.querySelector(s), $ = i => document.getElementById(i);
  const out = [];
  for (const c of cases) {
    P.querySelector(`.unit-btn[data-unit="${c.unit}"]`).click();
    if (c.unit === 'metric') { q('.height-cm').value = c.cm; q('.weight-kg').value = c.kg; }
    else { q('.height-ft').value = c.ft; q('.height-in').value = c.inch; q('.weight-lbs').value = c.lb; }
    q('.age-input').value = c.age; q('.sex-select').value = c.sex;
    $('calc-age-btn').click();
    await new Promise(r => setTimeout(r, 0));
    const res = $('age-results');
    out.push({bmi: $('age-bmi-value').textContent, cat: $('age-bmi-category').textContent,
      visible: res.classList.contains('visible'), note: $('age-note').hidden ? null : $('age-note').textContent,
      noteLink: $('age-note').querySelector('a') ? $('age-note').querySelector('a').getAttribute('href') : null,
      rankHidden: $('age-rank').hidden, typHidden: $('age-typical').hidden,
      rankTitle: $('age-rank-title').textContent, rankValue: $('age-rank-value').textContent,
      rankText: $('age-rank-text').textContent, rankSource: $('age-rank-source').textContent,
      median: $('age-rank-median').textContent, marker: $('age-rank-marker').style.left,
      typTitle: $('age-typical-title').textContent, typText: $('age-typical-text').textContent,
      typMid: $('age-typical-mid').textContent, er: (res.querySelector('.er') || {}).textContent || ''});
  }
  return out;
}'''


def group_of(age): return '20-39' if age < 40 else '40-59' if age < 60 else '60+'


def decade_of(age):
    return '80+' if age >= 80 else f'{age // 10 * 10}-{age // 10 * 10 + 9}'


def expect_rank(sex, age, b):
    g = group_of(age)
    q, qa = C[f'{sex}_{g}'], C[sex]
    lo, hi = rk(q, b)
    t = f'{b:.1f}'
    head = lab((lo, hi))
    head = head[0].upper() + head[1:] + ' of them'
    if lo < 1:
        txt = f'Your BMI of {t} is lower than about {nn(hi)}% of US {sex} aged {GW[g]}.'
    elif hi < 1:
        txt = f'Your BMI of {t} is higher than about {nn(lo)}% of US {sex} aged {GW[g]}.'
    else:
        txt = f'Your BMI of {t} is higher than about {nn(lo)}% of US {sex} aged {GW[g]} and lower than about {nn(hi)}%.'
    txt += (f' Among all US {sex} aged 20 and over, it is {lab(rk(qa, b)).replace("than ", "than about ")}. The median for '
            f'{sex} aged {GW[g]} is {MED[sex][g]}.')
    src_ = f'CDC NHANES 2021–2023, {NG[sex][g]:,} {sex} aged {GW[g]} measured; our calculation.'
    return {'rankTitle': f'Compared with US {sex} aged {GW[g]}', 'rankValue': head, 'rankText': txt, 'rankSource': src_,
            'median': f'Median {MED[sex][g]}', 'marker': min(99, max(1, lo))}


def expect_typical(sex, age, metric):
    d = decade_of(age)
    dw = '80 and over' if d == '80+' else d.replace('-', ' to ')
    wt = f'{WT[sex][d][1]} kg ({WT[sex][d][0]} lb)' if metric else f'{WT[sex][d][0]} lb ({WT[sex][d][1]} kg)'
    ws = f'{WS[sex][d][1]} cm ({WS[sex][d][0]} in)' if metric else f'{WS[sex][d][0]} in ({WS[sex][d][1]} cm)'
    v = DEC[sex][d]
    return {'typTitle': f'US {sex} aged {dw}',
            'typText': f'{sex.capitalize()} aged {dw} average a BMI of {DMEAN[sex][d]}, a weight of {wt} and a waist of {ws}.',
            'typMid': (f'Their median BMI is {d1(v["p50"])}, and half of them have a BMI between {d1(v["p25"])} and '
                       f'{d1(v["p75"])}. Of them, {HEALTHY[sex][d]}% have a BMI in the healthy range, 18.5 to 24.9, the same '
                       'range at every adult age.')}


with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])

    def page_at(w, h):
        pg = br.new_page(viewport={'width': w, 'height': h})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
        pg.goto(URL, wait_until='load')
        return pg, errs

    pg, errs = page_at(390, 844)
    # ---- visible text: tables, fragments, numbers
    ok(norm(pg.inner_text('h1')) == H1 and pg.locator('h1').count() == 1, 'H1 kept (D-28)')
    ok('Written by Marko Visic, MPharm' in norm(pg.inner_text('.byline')), 'byline')
    tables = pg.eval_on_selector_all('main table', '''ts => ts.map(t => ({cap: t.caption ? t.caption.textContent : '',
        rows: [...t.tBodies[0].rows].map(r => [...r.cells].map(c => [...c.childNodes].map(n => n.textContent.trim()).filter(x => x)))}))''')
    caps = [norm(t['cap']) for t in tables]
    ok(caps == ['Median BMI of US adults by decade of age, with the middle half', 'BMI of US women by percentile and age group',
                'BMI of US men by percentile and age group', 'US women: average BMI, weight and waist by age, 2021–2023',
                'US men: average BMI, weight and waist by age, 2021–2023'], f'table captions {caps}')
    if len(tables) == 5:
        rows = tables[0]['rows']
        ok(len(rows) == 7, 'decade table rows')
        for d, row in zip(AGES, rows):
            ok(norm(row[0][0]) == d.replace('-', '–'), f'decade table age {row[0]}')
            for s, cell in zip(SEXES, row[1:]):
                v = DEC[s][d]
                ok(cell == [d1(v['p50']), f"{d1(v['p25'])}–{d1(v['p75'])}"], f'decade table {s} {d}: {cell}')
        PROWS = (('p5', '5th'), ('p10', '10th'), ('p25', '25th'), ('p50', 'Median'), ('p75', '75th'), ('p90', '90th'), ('p95', '95th'))
        for t, s in zip(tables[1:3], SEXES):
            ok(len(t['rows']) == 7, f'{s} percentile rows')
            for (k, labl), row in zip(PROWS, t['rows']):
                ok(row[0] == [labl] and [c[0] for c in row[1:]] == [d1(G[f'{s}_{g}'][k]) for g in GRPS], f'{s} percentile {k}: {row}')
        for t, s in zip(tables[3:5], SEXES):
            ok(len(t['rows']) == 7, f'{s} average rows')
            for d, row in zip(AGES, t['rows']):
                got_ = [[norm(x) for x in cell] for cell in row]
                ok(got_ == [[d.replace('-', '–')], [DMEAN[s][d]], [f'{WT[s][d][0]} lb', f'{WT[s][d][1]} kg'],
                            [f'{WS[s][d][0]} in', f'{WS[s][d][1]} cm']], f'{s} averages {d}: {got_}')
    body = pg.evaluate('''() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('.calculator-card, table, svg, script, .faq-question svg').forEach(e => e.remove());
        m.querySelectorAll('.faq-answer').forEach(e => e.style.display = 'block');
        return m.textContent; }''')
    text = norm(body).replace('–', '-').replace('×', 'x').replace('÷', '/').replace('′', "'").replace('″', '"')
    for f in FRAG:
        ok(norm(f).replace('–', '-') in text, f'fragment missing: {f[:90]}')
    stray = sorted(set(NUM.findall(text)) - ALLOWED)
    ok(not stray, f'numbers not accounted for: {stray}')
    # ---- figure
    fig = pg.evaluate('''() => { const s = document.querySelector('#by-age figure svg');
        const vb = s.viewBox.baseVal, k = s.getBoundingClientRect().width / vb.width;
        const rects = [...s.querySelectorAll('rect')].map(r => ({x: +r.getAttribute('x'), w: +r.getAttribute('width'),
            y: +r.getAttribute('y'), h: +r.getAttribute('height'), fill: r.getAttribute('fill'), tip: r.querySelector('title') ?
            r.querySelector('title').textContent : null, box: r.getBoundingClientRect().toJSON()}));
        const lines = [...s.querySelectorAll('line')].map(l => ({x1: +l.getAttribute('x1'), x2: +l.getAttribute('x2'),
            y1: +l.getAttribute('y1'), stroke: l.getAttribute('stroke')}));
        const texts = [...s.querySelectorAll('text')].map(t => ({t: t.textContent, box: t.getBoundingClientRect().toJSON()}));
        return {vb: [vb.width, vb.height], svg: s.getBoundingClientRect().toJSON(), rects, lines, texts,
                title: s.querySelector('title').textContent, desc: s.querySelector('desc').textContent}; }''')
    ax = lambda b: 50 + (b - 15) * 260 / 30.0
    SER = {'women': '#be185d', 'men': '#4338ca'}
    tips = {r['tip']: r for r in fig['rects'] if r['tip']}
    for d in AGES:
        for s in SEXES:
            v = DEC[s][d]
            dw = d.replace('-', ' to ').replace('+', ' and over')
            tip = (f'{s.capitalize()} {dw}: median BMI {d1(v["p50"])}, middle half {d1(v["p25"])}–{d1(v["p75"])}, 10th to 90th '
                   f'percentile {d1(v["p10"])}–{d1(v["p90"])} ({v["n"]:,} {s})')
            r_ = tips.get(tip)
            ok(r_ is not None, f'figure hover title missing: {tip}')
            if r_:
                ok(abs(r_['x'] - ax(v['p25'])) < 0.06 and abs(r_['x'] + r_['w'] - ax(v['p75'])) < 0.11 and r_['fill'] == SER[s],
                   f'figure middle half {s} {d}')
                yc = r_['y'] + 4.5
                ln = [l for l in fig['lines'] if abs(l['y1'] - yc) < 0.01 and l['stroke'] == SER[s]]
                ok(len(ln) == 1 and abs(ln[0]['x1'] - ax(v['p10'])) < 0.06 and abs(ln[0]['x2'] - ax(v['p90'])) < 0.06,
                   f'figure 10th-90th line {s} {d}')
                tick = [l for l in fig['lines'] if l['stroke'] == '#111827' and abs(l['x1'] - ax(v['p50'])) < 0.06 and abs(l['y1'] - (yc - 6)) < 0.01]
                ok(len(tick) == 1, f'figure median tick {s} {d}')
    ok(fig['title'] == 'BMI of US women and men by age', 'figure title')
    for d in AGES:
        dw = d.replace('-', ' to ').replace('+', ' and over').capitalize()
        w_, m_ = DEC['women'][d], DEC['men'][d]
        ok(f'{dw}: women median {d1(w_["p50"])}, middle half {d1(w_["p25"])} to {d1(w_["p75"])}; men median {d1(m_["p50"])}, '
           f'middle half {d1(m_["p25"])} to {d1(m_["p75"])}.' in fig['desc'], f'figure description {d}')
    tl = [t['t'] for t in fig['texts']]
    ok(tl[:5] == ['Healthy 18.5–24.9', 'Women', 'Men'] + [] or ('Women' in tl and 'Men' in tl and 'Healthy 18.5–24.9' in tl),
       f'figure legend {tl[:5]}')
    ok([t for t in tl if re.fullmatch(r'\d0–\d9|80\+', t)] == [d.replace('-', '–') for d in AGES], 'figure row labels')
    ok([t for t in tl if t in ('20', '25', '30', '35', '40', '45')] == ['20', '25', '30', '35', '40', '45'] and 'BMI' in tl,
       'figure axis')
    S_ = fig['svg']
    for i, a in enumerate(fig['texts']):
        b_ = a['box']
        ok(b_['left'] >= S_['left'] - 0.5 and b_['right'] <= S_['right'] + 0.5 and b_['top'] >= S_['top'] - 0.5 and
           b_['bottom'] <= S_['bottom'] + 0.5, f'figure label outside: {a["t"]}')
        for c_ in fig['texts'][i + 1:]:
            o = c_['box']
            ok(not (b_['left'] < o['right'] and o['left'] < b_['right'] and b_['top'] < o['bottom'] - 1 and o['top'] < b_['bottom'] - 1),
               f'figure labels collide: {a["t"]} / {c_["t"]}')
        for r_ in fig['rects']:
            if r_['fill'] == '#dcfce7':
                continue                                              # the healthy band is a ground, labels may sit on it
            o = r_['box']
            ok(not (b_['left'] < o['right'] and o['left'] < b_['right'] and b_['top'] < o['bottom'] and o['top'] < b_['bottom']),
               f'figure label on a shape: {a["t"]}')
    # ---- FAQ
    qs = [norm(x) for x in pg.eval_on_selector_all('.faq-question', 'bs => bs.map(b => b.textContent)')]
    ok(qs == [norm(x) for x in FAQ_Q], f'FAQ questions {qs}')
    answers = [norm(x) for x in pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')]
    ld_faq = [(norm(m['name']), norm(m['acceptedAnswer']['text'])) for m in gr.get('FAQPage', {}).get('mainEntity', [])]
    ok(ld_faq == list(zip(qs, answers)), 'FAQ JSON-LD differs from the visible questions and answers')
    btn = pg.locator('.faq-question').first
    btn.click()
    ok(pg.locator('.faq-item.open').count() == 1, 'FAQ opens with one tap')
    btn.click()
    ok(pg.locator('.faq-item.open').count() == 0, 'FAQ closes with one tap')
    # ---- chips, links
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(len(chips) == 8 and all(pg.locator(c).count() == 1 for c in chips), f'chips {chips}')
    links = pg.eval_on_selector_all('main a[href]', 'as => as.map(a => a.getAttribute("href"))')
    inside = sorted({l for l in links if l.startswith('/') or l.startswith('#')})
    outside_ = sorted({l for l in links if l.startswith('http')})
    for l in inside:
        if l.startswith('#'):
            ok(pg.locator(l).count() == 1, f'anchor {l}')
            continue
        try:
            code = urllib.request.urlopen(base + l.split('#')[0], timeout=10).status
        except Exception as e:                                        # noqa: BLE001
            code = str(e)
        ok(code == 200, f'internal link {l}: {code}')
    for l in outside_:
        ok(l in REG_URLS, f'outside link not in the registry: {l}')
    ok(len(outside_) >= 8, f'only {len(outside_)} outside links')
    # ---- labels
    for i in LABEL_IDS:
        ok(pg.locator(f'label[for="{i}"]').count() == 1, f'label for {i}')
    pg.click('.unit-btn[data-unit="metric"]')
    for i in LABEL_IDS:
        loc = pg.locator(f'label[for="{i}"]')
        if loc.is_visible():
            loc.click()
            ok(pg.evaluate('document.activeElement.id') == i, f'label click focuses {i}')
    ok(pg.is_visible('#age-height-cm') and not pg.is_visible('#age-height-ft'), 'metric switch shows cm and hides ft')
    pg.click('.unit-btn[data-unit="imperial"]')
    ok(pg.is_visible('#age-height-ft') and not pg.is_visible('#age-height-cm'), 'imperial switch')
    for i in ('age-height-ft', 'age-height-in', 'age-weight-lbs', 'age-years'):
        pg.locator(f'label[for="{i}"]').click()
        ok(pg.evaluate('document.activeElement.id') == i, f'label click focuses {i}')
    # ---- the calculator: starting values
    vals = pg.evaluate('''() => ["age-height-ft","age-height-in","age-weight-lbs","age-height-cm","age-weight-kg","age-years","age-sex"]
        .map(i => document.getElementById(i).value)''')
    ok(vals == ['5', '6', '170', '168', '77', '45', 'female'], f'starting values {vals}')
    pg.click('#calc-age-btn')
    pg.wait_for_timeout(150)
    ok(pg.inner_text('#age-bmi-value') == '27.4' and pg.inner_text('#age-bmi-category') == 'Overweight', 'starting result 27.4')
    ok(norm(pg.inner_text('#age-rank-value')) == f"Higher than {EXR['40-59']}% of them", 'starting rank')
    ok(f'At 45, the healthy BMI range is 18.5 to 24.9' in norm(pg.inner_text('#age-results')), 'BMI and your age line')
    ok('Winter' not in pg.inner_text('#age-results'), 'no Winter line at 45')
    # ---- rank grid and decade boxes
    cases, exp = [], []
    for sex in ('female', 'male'):
        s = 'women' if sex == 'female' else 'men'
        # every BMI from 10.0 to 70.0 in each of the six curves: at 100 cm a weight in kg is the BMI (kg/m² as entered)
        for age in (30, 50, 70):
            for t in range(100, 701):
                cases.append({'unit': 'metric', 'cm': 100, 'kg': f'{t / 10:.1f}', 'age': age, 'sex': sex})
                exp.append((s, age, t / 10, 'grid'))
        for age in (20, 39, 40, 59, 60, 79, 80, 100):
            for lb in range(60, 420, 14):
                cases.append({'unit': 'imperial', 'ft': 5, 'inch': 7, 'lb': lb, 'age': age, 'sex': sex})
                exp.append((s, age, lb, False))
        for age in (20, 30, 40, 50, 60, 70, 85):
            for unit in ('imperial', 'metric'):
                c = {'unit': unit, 'age': age, 'sex': sex}
                c.update({'cm': 170, 'kg': 80} if unit == 'metric' else {'ft': 5, 'inch': 10, 'lb': 180})
                cases.append(c)
                exp.append((s, age, None, unit == 'metric'))
    got = pg.evaluate(TYPE_JS, cases)
    for c, e, g_ in zip(cases, exp, got):
        s, age, lb, metric = e
        if metric == 'grid':
            b, metric = lb, True
        else:
            b = r1(lb * 703 / 67 ** 2) if lb else (r1(80 / 1.7 ** 2) if metric else r1(180 * 703 / 70 ** 2))
        ok(g_['bmi'] == f'{b:.1f}', f'{c}: BMI {g_["bmi"]} vs {b:.1f}')
        ok(g_['visible'] and g_['note'] is None and not g_['rankHidden'] and not g_['typHidden'], f'{c}: boxes shown')
        want = expect_rank(s, age, b)
        for k in ('rankTitle', 'rankValue', 'rankText', 'rankSource', 'median'):
            ok(norm(g_[k]) == norm(want[k]), f'{c}: {k} {g_[k]!r} vs {want[k]!r}')
        # the browser keeps six significant digits of style.left
        ok(g_['marker'].endswith('%') and abs(float(g_['marker'][:-1]) - want['marker']) < 1e-3, f'{c}: marker {g_["marker"]}')
        wt = expect_typical(s, age, metric)
        for k in ('typTitle', 'typText', 'typMid'):
            ok(norm(g_[k]) == norm(wt[k]), f'{c}: {k} {g_[k]!r} vs {wt[k]!r}')
        has65 = norm(WINTER) in norm(g_['er'])
        ok(has65 == (age >= 65), f'{c}: Winter line {"missing" if age >= 65 else "shown under 65"}')
        ok(f'At {age}, the healthy BMI range is 18.5 to 24.9' in norm(g_['er']), f'{c}: BMI and your age line')
    ranks = {norm(g_['rankValue']) for g_ in got}
    ok(any(r_.startswith('Lower than') for r_ in ranks) and 'Higher than 99% of them' in ranks, 'grid reaches both ends of the rank')
    # under 20, the boundary, an empty age, 64 and 65
    edge = [{'unit': 'imperial', 'ft': 5, 'inch': 2, 'lb': 110, 'age': a, 'sex': 'female'} for a in (2, 15, 19, 20, '', 64, 65)]
    eg = pg.evaluate(TYPE_JS, edge)
    for a, g_ in zip((2, 15, 19), eg[:3]):
        ok(not g_['visible'] and g_['note'] and 'adult categories start at 20' in g_['note'] and g_['noteLink'] == '/kids-bmi-calculator/',
           f'age {a}: under-20 note and no adult result')
    ok(eg[3]['visible'] and eg[3]['note'] is None and not eg[3]['rankHidden'], 'age 20: adult result, no note')
    ok(eg[4]['visible'] and eg[4]['rankHidden'] and eg[4]['typHidden'] and 'BMI and your age' not in eg[4]['er'],
       'empty age: BMI only, no age boxes')
    ok(norm(WINTER) not in norm(eg[5]['er']) and norm(WINTER) in norm(eg[6]['er']), 'Winter line from 65 only')
    ok("CDC's adult categories are the same at 65 and over." in norm(eg[6]['er']), '65+ line opens with the CDC rule')
    ok(not errs, f'JS errors {errs}')
    pg.close()

    # ---- layout
    for w, h in ((320, 700), (360, 800), (390, 844), (1280, 800)):
        pg, errs = page_at(w, h)
        ok(pg.evaluate('document.documentElement.scrollWidth - window.innerWidth') <= 0, f'{w}px: wider than the screen')
        if (w, h) in ((390, 844), (360, 800)):
            bottom = pg.evaluate("document.getElementById('calc-age-btn').getBoundingClientRect().bottom")
            ok(bottom <= h, f'{w}x{h}: Calculate ends at {bottom:.0f}px, below the fold')
        pg.click('#calc-age-btn')
        pg.wait_for_timeout(150)
        ok(pg.evaluate('document.documentElement.scrollWidth - window.innerWidth') <= 0, f'{w}px after Calculate: wider than the screen')
        fr = pg.eval_on_selector_all('main .table-responsive', '''fs => fs.map(f => ({sw: f.querySelector('table').scrollWidth,
            cw: f.clientWidth, right: f.getBoundingClientRect().right}))''')
        for i, f in enumerate(fr):
            if w >= 360:
                ok(f['sw'] <= f['cw'] + 1, f'{w}px: table {i} wider than its frame ({f["sw"]} > {f["cw"]})')
            ok(f['right'] <= w + 0.5, f'{w}px: table frame {i} off the screen')
        ok(not errs, f'{w}px: JS errors {errs}')
        pg.close()
    br.close()

for f in fails[:60]:
    print('FAIL', f)
print(f'{checks:,} checks, {len(fails)} failures, 0 skipped')
sys.exit(1 if fails else 0)
