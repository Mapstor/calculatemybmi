#!/usr/bin/env python3
"""/men-bmi-calculator/ full check in Chromium (CMB-047; before it, rank_test_playwright.py covered the rank line only).
Serve the repo (python3 -m http.server 8000), then:
  python3 research/men-pilot/men_test_playwright.py http://localhost:8000 research/men-pilot/men_stats.json
Every expected value is worked out here from the data, not read from the page:
  - men_stats.json is rebuilt from the raw CDC files (men_stats.py on research/average-weight/raw) and must come out equal;
    its curve must equal research/rank-curves/curves.json's men curve;
  - averages from research/average-weight/avgw_results.json, body fat from research/body-fat-chart-build/bfpc_stats.json,
    the decade differences from research/age-calc-build/abc_stats.json, weights from the weight-table gate's rule, and the
    outside figures from the registry rows that hold them (HE-Stat 111, Series 3, Provencher 2018, WHO 2008, Wing 2011,
    Winter 2014, Gallagher 2000), each checked in the row's own text;
  - the four tables cell by cell with their captions; both figures (text, title, desc and every drawn position); 40 number
    sentences rebuilt from the files, then every number in the visible text outside the tool, the tables and the figures
    must be one of those values or a listed constant (cut-offs, ages, years, source numbers);
  - the tool at its starting values (5'10", 180 lb): BMI, category, healthy limits, the distance, milestones, what-if
    steps, BMI Prime and the ponderal index the worked example quotes; then the rank line typed in at every BMI from 10.0
    to 70.0 (metric, 100 cm) against the US rank rule on the curve;
  - the FAQ: 8 questions, JSON-LD equal to the visible answers, one tap opens and one closes;
  - the head's numbers (description, og:image:alt and the og image's generator), title and H1 kept (D-28);
  - outside <main> the page equals origin/main's; internal links answer 200, outside links are registry URLs;
  - the page never wider than the screen at 320, 360, 390 and 1280 px, before and after Calculate;
  - the CMB-047 fixes: no "highest" decade claim, no bare doctor lines, CDC's provider and other-factors lines, the
    measuring steps NHLBI gives and nothing more.
Every check runs; nothing is skipped. Exit 1 on any failure."""
import csv
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

from playwright.sync_api import sync_playwright

base, stats = sys.argv[1].rstrip('/'), sys.argv[2]
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(stats)), '..', '..'))
MS = json.load(open(stats, encoding='utf-8'))
AW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json'), encoding='utf-8'))['men']
BF = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json'), encoding='utf-8'))
ABC = json.load(open(os.path.join(ROOT, 'research/age-calc-build/abc_stats.json'), encoding='utf-8'))
CURVES = json.load(open(os.path.join(ROOT, 'research/rank-curves/curves.json'), encoding='utf-8'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds                 # noqa: E402

REG, REG_URLS = {}, set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG[r['domain']] = ' '.join((r['coverage'], r['sample_note'], r['notes']))
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()} | set(re.findall(r'https?://[^\s;,)"]+', r['notes']))
PATH = '/men-bmi-calculator/'
fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def norm(t):
    t = (t or '').replace(' ', ' ').replace('­', '').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', t).strip()


def flat(t): return norm(t).replace('–', '-').replace('×', 'x').replace('÷', '/').replace('′', "'").replace('″', '"')
def d1(x): return str(Decimal(repr(float(x))).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def d0(x): return str(Decimal(repr(float(x))).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def jround(x): return math.floor(x + 0.5)                             # JavaScript's Math.round for these positive values


def cat(b):
    return ('Underweight' if b < 18.5 else 'Healthy' if b < 25 else 'Overweight' if b < 30 else 'Obesity class 1' if b < 35
            else 'Obesity class 2' if b < 40 else 'Obesity class 3')


# ---------------------------------------------------------------- the data behind the page
with tempfile.TemporaryDirectory() as td:
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'research/men-pilot/men_stats.py'),
                        os.path.join(ROOT, 'research/average-weight/raw'), os.path.join(td, 'm.json')], capture_output=True, text=True)
    ok(p.returncode == 0 and json.load(open(os.path.join(td, 'm.json'), encoding='utf-8')) == MS,
       f'men_stats.py on the raw CDC files does not rebuild {stats} ({p.stderr[-200:]})')
Q = MS['p1_p99']
ok(Q == CURVES['men']['p1_p99'], "men_stats.json's curve differs from curves.json's men curve")
T = MS['table']
ok((MS['bmi_n'], MS['waist_n']) == (AW['BMXBMI']['n'], AW['waist_in']['n']), 'men_stats n differs from avgw n')
ok((d1(AW['BMXBMI']['mean']), d1(AW['bmi_p50']), d1(AW['wt_pct']['p95']), d1(AW['wt_lb']['mean']), d1(AW['ht_in']['mean'])) ==
   ('29.4', '28.2', '290.6', '199.0', '68.9'), 'our averages differ from Series 3 No. 50')
S3 = MS['reproduces_series3']
for k, v in (('nhanes-adult-weight-trends', ('men overweight 35.5 (1.4), obesity 39.3 (1.9), severe 6.8',)),
             ('nhanes-anthropometric-reference', ('mean men 29.4', f"median {S3['men_bmi_median']}/{S3['women_bmi_median']}",
                                                  f"95th pct {S3['men_wt_p95_lb']} lb", f"{S3['women_wt_p95_lb']} lb",
                                                  'weight mean 199.0', 'height 68.9')),
             ('provencher-2018-nfl-combine', ('53.4% of the athletes as obese, body fat 8.9%',)),
             ('who-2008-waist-hip-ratio', ('waist-hip ratio >=0.90 cm (M)',)),
             ('winter-2014-bmi-mortality-65', ('197,940 people aged 65+', 'reference BMI 23.0-23.9', 'increase for BMI >33.0')),
             ('wing-2011-look-ahead', ('5 to <10% weight loss',)),
             ('gallagher-2000-bf-ranges', ('men 8/20/25, 11/22/28, 13/25/30',)),
             ('cdc-adult-bmi-categories', ('Persons may consider seeking advice from their health care providers about their BMI',)),
             ('cdc-about-bmi', ('For individuals, BMI should be considered with other factors, such as blood pressure, cholesterol levels',)),
             ('nhlbi-1998-obesity-guidelines', ('stand and place a tape measure around your middle, just above your hipbones. Measure '
                                                'your waist just after you breathe out', 'The plane of the tape is parallel to the floor '
                                                'and the tape is snug, but does not compress the skin', 'normal minimal respiration',
                                                'Waist >102 cm (>40 in) men'))):
    for x in v:
        ok(x in REG[k], f'registry {k} does not hold: {x}')
GAL = BF['gallagher']['cuts']['m']
ok([GAL[a] for a in ('20-39', '40-59', '60-79')] == [[8, 20, 25], [11, 22, 28], [13, 25, 30]], 'Gallagher cut-offs in bfpc_stats.json')
BC = BF['bmi']['by_cat']['m']
DXA = {c: (d1(BC[c]['p50']), d1(BC[c]['p25']), d1(BC[c]['p75'])) for c in ('healthy', 'over', 'obese')}
BF2059 = d1(BF['by_age']['m']['20-59']['mean4'])
OVER_P10 = d1(BC['over']['p10'])
ok(float(OVER_P10) < float(DXA['healthy'][0]), '"one in ten overweight men had less fat than the typical healthy-BMI man"')
DM = AW['age']
ok(list(DM) == ['20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80+'], f'decades {list(DM)}')
for k in ('men_mean_40-49_minus_20-29', 'men_mean_50-59_minus_20-29'):
    ok(ABC['differences'][k]['excludes_0'] and ABC['differences'][k]['ci95'][0] > 0, f'{k}: the 95% interval does not sit above 0')
for d in ('20–29', '40–49', '50–59'):
    ok(abs(ABC['decades']['men'][d.replace('–', '-')]['mean'] - DM[d]['bmi']['mean']) < 0.01, f'abc_stats {d} mean differs from avgw')
W_OVER = MS['share_waist_over_102cm_bmi_25_29_9']
ok(25 <= W_OVER < 35, f'"about 3 in 10" overweight men with a waist over 102 cm: {W_OVER}')
ok(abs(35.5 + 39.3 - 75) < 2.5, '"about 3 in 4" from HE-Stat 111')
H, W = 70, 180
EXB = r1(W * 703 / H ** 2)
HB = gate_bounds('lb', H, H * 2.54, 1)
HBK = gate_bounds('kg', H, H * 2.54, 1)
FROM = [gate_bounds('lb', H, H * 2.54, i)[0] for i in (2, 3, 4, 5)]
HT = jround(AW['ht_in']['mean'])


def pct(b):
    if b <= Q[0]:
        return 0.0
    if b >= Q[98]:
        return 100.0
    for i in range(98):
        if b < Q[i + 1]:
            return i + 1 + (b - Q[i]) / (Q[i + 1] - Q[i])
    return 100.0


def nn(x): return 99 if x > 99 else jround(x)


ok(abs(pct(25.0) - 25) < 1.5, f'"only a quarter had a BMI under 25": {pct(25.0):.1f}%')
ok(abs((100 - pct(25.0)) - 75) < 2.5, f'"about 3 in 4 are at 25 or above" on our curve: {100 - pct(25.0):.1f}%')
EXR = nn(pct(jround(EXB * 10 - 1) / 10))
PRIME = jround(EXB * 4) / 100
FRAG = [
    f"CDC measurements of {MS['bmi_n']:,} men, 2021-2023",
    f"The average US man has a BMI of {d1(AW['BMXBMI']['mean'])}, and about 3 in 4 are at 25 or above (CDC, 2021-2023)",
    "about 3 in 10 US men with an overweight BMI have a waist over 40 inches",
    f"a man who is 5'10\" ({d1(H * 2.54)} cm) and weighs {W} lb ({d1(W / 2.20462)} kg)",
    f"{W} lb at 5'10\" gives a BMI of {EXB}, just inside the overweight range; the healthy range at that height ends at {HB[1]} lb",
    f"BMI: {EXB}, overweight",
    f"Healthy weight: {HB[0]}-{HB[1]} lb", f"in whole kilograms, {HBK[0]}-{HBK[1]} kg",
    f"({d1(HB[0] / 2.20462)} and {d1(HB[1] / 2.20462)} kg)",
    f"{W - HB[1]} lb ({d1((W - HB[1]) / 2.20462)} kg) above the healthy range",
    f"({d1((W - HB[1]) / 2.20462)} kg is {W - HB[1]} lb converted)",
    f"Compared with US men: higher than {EXR}%",
    f"BMI Prime: {PRIME:.2f}", f"Under 1.00 is below it; {PRIME:.2f} is {jround(EXB * 4) - 100}% over",
    f"Ponderal index: {(W / 2.20462) / ((H * 2.54 / 100) ** 3):.1f} kg/m³",
    f"At 5'10\": healthy from {HB[0]} lb, overweight from {FROM[0]} lb, obesity from {FROM[1]} lb, class 2 obesity from {FROM[2]} lb "
    f"and class 3 from {FROM[3]} lb",
    "gaining or losing 5, 10, 15 or 20 lb (2.5 to 10 kg in metric)",
    f"CDC measured {MS['bmi_n']:,} men aged 20 and over between August 2021 and August 2023",
    f"The middle man had a BMI of {d1(T['p50'])}, and only a quarter had a BMI under 25",
    f"{d1(AW['BMXBMI']['mean'])} Average BMI of US men aged 20 and over, measured August 2021-August 2023",
    f"25% of US men have a BMI of {d1(T['p25'])} or lower",
    f"({MS['bmi_n']:,} men, survey-weighted); the same method reproduces NCHS's published median BMI ({S3['men_bmi_median']}) and "
    f"95th-percentile weight ({S3['men_wt_p95_lb']} lb)",
    "Overweight 35.5% Obesity 39.3% Severe obesity 6.8%",
    f"The average US man is {HT // 12}'{HT % 12}\" ({d0(AW['ht_in']['mean'] * 2.54)} cm) and weighs {d1(AW['wt_lb']['mean'])} lb "
    f"({d1(AW['wt_lb']['mean'] / 2.2046)} kg), with a BMI of {d1(AW['BMXBMI']['mean'])} and a waist of {d1(AW['waist_in']['mean'])} in "
    f"({d0(AW['waist_in']['mean'] * 2.54)} cm)",
    f"Average BMI was higher in men's 40s and 50s ({d1(DM['40–49']['bmi']['mean'])} and {d1(DM['50–59']['bmi']['mean'])}) than in "
    f"their 20s ({d1(DM['20–29']['bmi']['mean'])}); each difference is larger than its margin of error",
    f"CDC body scans put average body fat at {BF2059}% at ages 20 to 59",
    f"One in ten men with an overweight BMI had less body fat (under {OVER_P10}%) than the typical man with a healthy BMI "
    f"({DXA['healthy'][0]}%)",
    "53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat",
    f"The average US man aged 20 and over measures {d1(AW['waist_in']['mean'])} in",
    f"{d0(MS['share_waist_over_102cm'])}% of US men aged 20 and over have a waist of more than 102 cm (40 in)",
    f"({MS['waist_n']:,} men measured)",
    "About 3 in 10 US men with a BMI of 25 to 29.9 have a waist over 102 cm; the other 7 don't",
    "uses a ratio of 0.90 or more in men", "losing 5 to 10% of body weight",
    f"At 5'10\" ({d1(H * 2.54)} cm) that means {HB[0]} to {HB[1]} lb ({HBK[0]} to {HBK[1]} kg)",
    f"The average BMI of US men aged 20 and over is {d1(AW['BMXBMI']['mean'])} and the median is {d1(AW['bmi_p50'])}",
    "39.3% of men had obesity and another 35.5% were overweight, so about 3 in 4 are above the healthy range",
    f"For a man who is 5'10\" (70 in) and weighs 180 lb: 180 x 703 / 4,900 = {EXB}",
    "53.4% of players had a BMI of 30 or more, but only 8.9% had obesity when body fat was measured",
    f"rise from {GAL['20-39'][0]}-{GAL['20-39'][1] - 0.1:.1f}% at ages 20-39 to {GAL['60-79'][0]}-{GAL['60-79'][1] - 0.1:.1f}% at 60-79",
    "a meta-analysis of 197,940 people found that, compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and "
    "began to rise at about 33 (Winter et al., 2014)",
    f"({MS['bmi_n']:,} with BMI, {MS['waist_n']:,} with waist)",
    f"reproduces NCHS's published medians (BMI {S3['men_bmi_median']} men, {S3['women_bmi_median']} women) and 95th-percentile "
    f"weights ({S3['men_wt_p95_lb']} lb men, {S3['women_wt_p95_lb']} lb women)",
    'CDC\'s Adult BMI Calculator page says: "Persons may consider seeking advice from their health care providers about their BMI" (CDC)',
    'Blood pressure and cholesterol: CDC lists both among the other factors to consider with BMI for an individual (CDC)',
    "Stand and breathe normally. Put a tape measure around your bare waist, just above your hip bones. Keep the tape snug and "
    "level all the way round, without pressing into the skin. Breathe out, then read the tape.",
    "These steps are NHLBI's, from its Aim for a Healthy Weight page and the waist-measuring protocol in its 1998 guidelines.",
]
NUM = re.compile(r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?')
CONST = {'18.5', '24.9', '25', '29.9', '30', '34.9', '35', '40', '102', '20', '59', '65', '39', '60', '79', '703', '1',
         '0.5', '1.00', '10', '2', '6', '4', '3', '50', '111', '1998', '2008', '2018', '2011', '2014', '2000', '2021', '2023', '2026'}
ALLOWED = set(CONST)
for f in FRAG:
    ALLOWED |= set(NUM.findall(flat(f)))

# ---------------------------------------------------------------- the served file
src = urllib.request.urlopen(base + PATH, timeout=20).read().decode('utf-8')
main_html = re.search(r'(?s)<main\b.*?</main>', src).group(0)
subprocess.run(['git', 'fetch', '-q', 'origin', 'main'], cwd=ROOT, capture_output=True)
try:
    old = subprocess.run(['git', 'show', 'origin/main:men-bmi-calculator/index.html'], cwd=ROOT, capture_output=True, text=True,
                         check=True).stdout
    strip = lambda s: re.sub(r'(?s)<main\b.*?</main>', '<main/>', s)
    ok(strip(old) == strip(src), 'outside <main> the page differs from origin/main')
except subprocess.CalledProcessError:
    ok(False, 'git show origin/main:men-bmi-calculator/index.html failed')
for pat in (r'Average BMI is highest', r'worth checking with a doctor', r'When to see a doctor', r'routine checks that BMI',
            r'pull your stomach in', r'nearest half inch', r'nhlbi\.nih\.gov/health/overweight-and-obesity'):
    ok(not re.search(pat, main_html), f'CMB-047: "{pat}" still on the page')
ok(re.search(r'<title>BMI Calculator for Men - Free Male BMI Calculator</title>', src) is not None, 'title changed (D-28)')
ok(main_html.count('<h1>') == 1 and '<h1>BMI Calculator for Men</h1>' in main_html, 'H1 changed (D-28)')
meta = dict(re.findall(r'<meta (?:name|property)="([^"]+)" content="([^"]*)"', src))
ok(f"from CDC data on {MS['bmi_n']:,} men." in meta.get('description', ''), 'meta description number')
ok(meta.get('og:image:alt') == f"BMI Calculator for Men: the average US man has a BMI of {d1(AW['BMXBMI']['mean'])} (CDC, 2021–2023)",
   'og:image:alt number')
og = os.path.join(ROOT, meta.get('og:image', '').replace('https://calculatemybmi.net/', ''))
ok(os.path.isfile(og) and struct.unpack('>II', open(og, 'rb').read(24)[16:24]) == (1200, 630), f'og image {og}')
ogsrc = open(os.path.join(ROOT, 'research/men-pilot/og_men.py'), encoding='utf-8').read()
ok(f"mx = sx({d1(AW['BMXBMI']['mean'])})" in ogsrc and f"Average US man: BMI {d1(AW['BMXBMI']['mean'])}" in ogsrc,
   'the og image draws a number other than the average BMI')
ld = [json.loads(b) for b in re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', src)]
ok([d.get('@type') for d in ld] == ['WebApplication', 'BreadcrumbList', 'FAQPage'], f"JSON-LD {[d.get('@type') for d in ld]}")
faq_ld = next((d for d in ld if d.get('@type') == 'FAQPage'), {'mainEntity': []})

TEXT_JS = '''() => { const main = document.querySelector('main'), els = [...main.querySelectorAll('*')];
  els.forEach(e => { const d = getComputedStyle(e).display; if (d !== 'inline' && d !== 'contents') e.setAttribute('data-blk', '1'); });
  const m = main.cloneNode(true); els.forEach(e => e.removeAttribute('data-blk'));
  m.querySelectorAll('.calculator-card, table, svg, script').forEach(e => e.remove());
  m.querySelectorAll('[data-blk]').forEach(e => { e.before(' '); e.after(' '); });
  return m.textContent; }'''
FIG_JS = '''() => [...document.querySelectorAll('main figure svg')].map(s => ({title: s.querySelector('title').textContent,
  desc: s.querySelector('desc').textContent, texts: [...s.querySelectorAll('text')].map(t => [t.textContent, +t.getAttribute('x')]),
  rects: [...s.querySelectorAll('rect')].map(r => [+r.getAttribute('x'), +r.getAttribute('y'), +r.getAttribute('width'), r.getAttribute('fill')]),
  lines: [...s.querySelectorAll('line')].map(l => [+l.getAttribute('x1'), +l.getAttribute('x2'), l.getAttribute('stroke')]),
  path: (s.querySelector('path') || {getAttribute: () => ''}).getAttribute('d'),
  circles: [...s.querySelectorAll('circle')].map(c => +c.getAttribute('cx')),
  caption: s.closest('figure').querySelector('figcaption').textContent}))'''
RANK_JS = r'''async (cases) => {
  const P = document.getElementById('panel-men'), out = [];
  for (const c of cases) {
    P.querySelector(`.unit-btn[data-unit="${c.unit}"]`).click();
    if (c.unit === 'metric') { P.querySelector('.height-cm').value = c.cm; P.querySelector('.weight-kg').value = c.kg; }
    else { P.querySelector('.height-ft').value = c.ft; P.querySelector('.height-in').value = c.inch; P.querySelector('.weight-lbs').value = c.lb; }
    document.getElementById('calc-men-btn').click();
    await new Promise(r => setTimeout(r, 0));
    out.push({bmi: document.getElementById('men-bmi-value').textContent, head: document.getElementById('men-rank-value').textContent,
              text: document.getElementById('men-rank-text').textContent, marker: document.getElementById('men-rank-marker').style.left,
              hidden: document.getElementById('men-rank').hidden});
  }
  return out;
}'''
RES_JS = '''() => { const $ = id => document.getElementById(id);
  const tabs = [...document.querySelectorAll('.er-table')].map(t => [...t.tBodies[0].rows].map(r => [...r.cells].map(c => c.textContent.trim())));
  const metrics = [...document.querySelectorAll('.er-metric')].map(m => [m.querySelector('.er-metric-label').textContent,
    m.querySelector('.er-metric-value').textContent]);
  return {bmi: $('men-bmi-value').textContent, cat: $('men-bmi-category').textContent, min: $('men-healthy-min').textContent,
    max: $('men-healthy-max').textContent, diff: $('men-weight-diff').textContent, tabs, metrics}; }'''

with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])

    def page_at(w, h):
        pg = br.new_page(viewport={'width': w, 'height': h})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
        pg.goto(base + PATH, wait_until='load')
        return pg, errs

    pg, errs = page_at(390, 844)
    # ---- tables
    tables = pg.eval_on_selector_all('main table', '''ts => ts.map(t => ({cap: t.caption ? t.caption.textContent : '',
        rows: [...t.tBodies[0].rows].map(r => [...r.cells].map(c => [...c.childNodes].map(n => n.textContent.trim()).filter(x => x).join(' | ')))}))''')
    ok([norm(t['cap']) for t in tables] == ['BMI percentiles, US men aged 20 and over, 2021–2023',
                                            'US men: average BMI, weight (lb) and waist (in) by age, 2021–2023',
                                            'Healthy weight, and where overweight and obesity start, by height',
                                            'Body fat of US men aged 20–59 by BMI category, DXA scans 2011–2018'],
       f"table captions {[t['cap'] for t in tables]}")
    if len(tables) == 4:
        PR = (('p5', '5th'), ('p10', '10th'), ('p25', '25th'), ('p50', '50th (median)'), ('p75', '75th'), ('p90', '90th'), ('p95', '95th'))
        got = [[norm(c) for c in r] for r in tables[0]['rows']]
        ok(got == [[l, d1(T[k]), cat(T[k])] for k, l in PR], f'percentile table {got}')
        got = [[norm(c) for c in r] for r in tables[1]['rows']]
        ok(got == [[d, d1(v['bmi']['mean']), d0(v['wt']['mean']), d1(v['waist']['mean'])] for d, v in DM.items()], f'decade table {got}')
        want = []
        for h in (66, 70, 74):
            hl, hk = gate_bounds('lb', h, h * 2.54, 1), gate_bounds('kg', h, h * 2.54, 1)
            ow, owk = gate_bounds('lb', h, h * 2.54, 2)[0], gate_bounds('kg', h, h * 2.54, 2)[0]
            ob, obk = gate_bounds('lb', h, h * 2.54, 3)[0], gate_bounds('kg', h, h * 2.54, 3)[0]
            want.append([f"{h // 12}′{h % 12}″ | {d1(h * 2.54)} cm", f'{hl[0]}–{hl[1]} lb | {hk[0]}–{hk[1]} kg', f'{ow} lb | {owk} kg',
                         f'{ob} lb | {obk} kg'])
        got = [[norm(c) for c in r] for r in tables[2]['rows']]
        ok(got == [[norm(c) for c in r] for r in want], f'height table {got} vs {want}')
        got = [[norm(c) for c in r] for r in tables[3]['rows']]
        want = [[f'{nm} | BMI {rng}', f'{DXA[c][0]}%', f'{DXA[c][1]}–{DXA[c][2]}%'] for nm, rng, c in
                (('Healthy', '18.5–24.9', 'healthy'), ('Overweight', '25–29.9', 'over'), ('Obesity', '30 or more', 'obese'))]
        ok(got == [[norm(c) for c in r] for r in want], f'DXA table {got} vs {want}')
    # ---- figures
    figs = pg.evaluate(FIG_JS)
    ok(len(figs) == 2, f'{len(figs)} figures')
    if len(figs) == 2:
        f1, f2 = figs
        xb = lambda b: 10 + (b - 15) * 280 / 25                            # BMI scale 15-40 across the 280-px bar
        ok(norm(f1['title']) == f'Worked example: 5 feet 10 inches and {W} pounds gives a BMI of {EXB}', f"figure 1 title {f1['title']}")
        ok(norm(f1['desc']) == (f'{W} times 703 divided by {H} squared equals {EXB}. On the BMI scale from 15 to 40 the marker sits just '
                                f'past 25, in the overweight range. On a weight bar for 5 feet 10 inches, the healthy range runs from '
                                f'{HB[0]} to {HB[1]} pounds and the marker at {W} pounds sits {W - HB[1]} pounds above it.'),
           f"figure 1 desc {f1['desc']}")
        ok([norm(t) for t, _ in f1['texts']] == [f'{W} lb × 703 ÷ {H}² = {EXB}', f'{H} in ({d1(H * 2.54)} cm), {W} lb ({d1(W / 2.20462)} kg)',
                                                f'BMI {EXB}: overweight', '18.5', '25', '30', '35', f'Healthy at 5′10″: {HB[0]}–{HB[1]} lb',
                                                f'+{W - HB[1]} lb', f'{HB[0]} lb', f'{HB[1]}', f'{W}'], f"figure 1 texts {f1['texts']}")
        scale = [r for r in f1['rects'] if r[1] == 84]
        ok([(round(r[0], 1), round(r[2], 1)) for r in scale] ==
           [(round(xb(a), 1), round(xb(b) - xb(a), 1)) for a, b in ((15, 18.5), (18.5, 25), (25, 30), (30, 35), (35, 40))], f'figure 1 scale {scale}')
        ok(abs(f1['lines'][0][0] - xb(EXB)) < 0.06 and abs(f1['texts'][2][1] - xb(EXB)) < 0.01, 'figure 1 BMI marker position')
        for (t, x), b in zip(f1['texts'][3:7], (18.5, 25, 30, 35)):
            ok(abs(x - xb(b)) < 0.01, f'figure 1 tick {t} at {x}')
        band = next(r for r in f1['rects'] if r[3] == '#86efac')
        mark = f1['lines'][1][0]
        k = band[2] / (HB[1] - HB[0])                                       # px per lb, from the healthy band
        ok(abs((mark - band[0]) / k - (W - HB[0])) < 0.01, 'figure 1: the 180-lb marker is off the healthy band\'s scale')
        ok(f1['path'] == f'M{band[0] + band[2]:.1f} 188 V182 H{mark:.1f} V188', f"figure 1 +7 bracket {f1['path']}")
        ok(abs(f1['texts'][8][1] - (band[0] + band[2] + mark) / 2) < 0.01 and abs(f1['texts'][9][1] - band[0]) < 0.01,
           'figure 1 label positions')
        ok(norm(f1['caption']) == norm(f"{W} lb at 5′10″ gives a BMI of {EXB}, just inside the overweight range; the healthy range at "
                                       f"that height ends at {HB[1]} lb."), 'figure 1 caption')
        xw = lambda i: 10 + (i - 30) * 280 / 20                            # waist scale 30-50 in
        AVW = d1(AW['waist_in']['mean'])
        ok(norm(f2['title']) == 'Waist size for men: the NIH cut-off at 40 inches (102 cm)', 'figure 2 title')
        ok(norm(f2['desc']) == ('A scale from 30 to 50 inches. Below 40 inches is marked lower risk, above it higher risk. A dashed marker '
                                f'shows the average US man aged 20 and over at {AVW} inches, just above the cut-off.'), 'figure 2 desc')
        ok([norm(t) for t, _ in f2['texts']] == ['NIH cut-off: 40 in (102 cm)', 'Lower risk', 'Higher risk', '30 in', '35 in', '45 in',
                                                '50 in', f"Average US man: {AVW} in ({d0(AW['waist_in']['mean'] * 2.54)} cm)"],
           f"figure 2 texts {f2['texts']}")
        ok([(r[0], r[2]) for r in f2['rects']] == [(xw(30), xw(40) - xw(30)), (xw(40), xw(50) - xw(40))], f"figure 2 zones {f2['rects']}")
        ok(f2['lines'][0][0] == xw(40) and [l[0] for l in f2['lines'][1:5]] == [xw(i) for i in (30, 35, 45, 50)], 'figure 2 cut-off and ticks')
        ok(abs(f2['lines'][5][0] - xw(float(AVW))) < 0.01 and abs(f2['circles'][0] - xw(float(AVW))) < 0.01, 'figure 2 average marker')
        ok(float(AVW) > 40, 'figure 2: "just above the cut-off"')
        ok(norm(f2['caption']) == norm(f'The NIH cut-off for men is a waist of more than 40 in (102 cm). The average US man aged 20 and over '
                                       f'measures {AVW} in (CDC NHANES 2021–2023, our calculation).'), 'figure 2 caption')
    # ---- every number in the text
    text = flat(pg.evaluate(TEXT_JS))
    for f in FRAG:
        ok(flat(f) in text, f'fragment missing: {f[:100]}')
    stray = sorted(set(NUM.findall(text)) - ALLOWED)
    ok(not stray, f'numbers not accounted for: {stray}')
    # ---- FAQ
    qs = [norm(x) for x in pg.eval_on_selector_all('.faq-question', 'bs => bs.map(b => b.textContent)')]
    ans = [norm(x) for x in pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')]
    ok(len(qs) == 8, f'{len(qs)} FAQ')
    ok([(norm(m['name']), norm(m['acceptedAnswer']['text'])) for m in faq_ld['mainEntity']] == list(zip(qs, ans)),
       'FAQ JSON-LD differs from the visible answers')
    b = pg.locator('.faq-question').first
    b.click()
    ok(pg.locator('.faq-item.open').count() == 1, 'FAQ opens')
    b.click()
    ok(pg.locator('.faq-item.open').count() == 0, 'FAQ closes')
    # ---- links
    links = pg.eval_on_selector_all('main a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for l in sorted({l for l in links if l.startswith('/')}):
        try:
            code = urllib.request.urlopen(base + l.split('#')[0], timeout=10).status
        except Exception as e:                                        # noqa: BLE001
            code = str(e)
        ok(code == 200, f'internal link {l}: {code}')
    for l in sorted({l for l in links if l.startswith('#')}):
        ok(pg.locator(l).count() == 1, f'anchor {l}')
    out = sorted({l for l in links if l.startswith('http')})
    ok(set(out) <= REG_URLS, f'outside links not in the registry: {sorted(set(out) - REG_URLS)}')
    # ---- the tool at its starting values
    pg.click('#calc-men-btn')
    pg.wait_for_timeout(200)
    res = pg.evaluate(RES_JS)
    ok(res['bmi'] == f'{EXB}' and res['cat'] == 'Overweight', f"starting BMI {res['bmi']} {res['cat']}")
    ok(norm(res['min']) == f'{HB[0]} lbs ({d1(HB[0] / 2.20462)} kg)' and norm(res['max']) == f'{HB[1]} lbs ({d1(HB[1] / 2.20462)} kg)',
       f"healthy limits {res['min']} / {res['max']}")
    ok(norm(res['diff']) == f'{W - HB[1]} lbs ({d1((W - HB[1]) / 2.20462)} kg) above the healthy range for your height', f"distance {res['diff']}")
    ok(norm(pg.inner_text('#men-rank-value')) == f'Higher than {EXR}% of US men', 'starting rank')
    tabs = res['tabs']
    ok(len(tabs) >= 3, f'{len(tabs)} result tables')
    if len(tabs) >= 3:
        ok([norm(r[2]).split(' ')[0] for r in tabs[0]] == [str(x) for x in (HB[0], HB[1], *FROM)], f'milestones {tabs[0]}')
        ok([norm(r[0]) for r in tabs[1]] == ['−20 lbs', '−15 lbs', '−10 lbs', '−5 lbs', 'Current', '+5 lbs', '+10 lbs', '+15 lbs', '+20 lbs'],
           f'what-if steps {[r[0] for r in tabs[1]]}')
        ok([norm(r[2]) for r in tabs[1]] == [f'{r1((W + c) * 703 / H ** 2):.1f}' for c in (-20, -15, -10, -5, 0, 5, 10, 15, 20)],
           'what-if BMIs')
    met = dict((norm(a), norm(v)) for a, v in res['metrics'])
    ok(met.get('BMI Prime') == f'{PRIME:.2f}' and met.get('Ponderal Index') == f"{(W / 2.20462) / ((H * 2.54 / 100) ** 3):.1f}",
       f'BMI Prime and ponderal index {met}')
    pg.click('#panel-men .unit-btn[data-unit="metric"]')
    pg.click('#calc-men-btn')
    pg.wait_for_timeout(200)
    whatif_m = [norm(r[0]) for r in pg.evaluate(RES_JS)['tabs'][1]]
    ok(whatif_m == ['−10 kg', '−7.5 kg', '−5 kg', '−2.5 kg', 'Current', '+2.5 kg', '+5 kg', '+7.5 kg', '+10 kg'], f'metric what-if {whatif_m}')
    # ---- the rank at every BMI 10.0-70.0
    cases = [{'unit': 'metric', 'cm': 100, 'kg': f'{t / 10:.1f}'} for t in range(100, 701)]
    got = pg.evaluate(RANK_JS, cases)
    for c, g in zip(cases, got):
        bm = float(c['kg'])
        ok(g['bmi'] == f'{bm:.1f}' and not g['hidden'], f'{c}: BMI {g["bmi"]}')
        lo, hi = pct(jround(bm * 10 - 1) / 10), 100 - pct(bm)
        if lo < 1:
            head, txt = f'Lower than {nn(hi)}% of US men', f'Your BMI of {bm:.1f} is lower than about {nn(hi)}% of US men aged 20 and over.'
        elif hi < 1:
            head, txt = f'Higher than {nn(lo)}% of US men', f'Your BMI of {bm:.1f} is higher than about {nn(lo)}% of US men aged 20 and over.'
        else:
            head = f'Higher than {nn(lo)}% of US men'
            txt = (f'Your BMI of {bm:.1f} is higher than about {nn(lo)}% of US men aged 20 and over and lower than about {nn(hi)}%. '
                   f'The median US man has a BMI of {d1(T["p50"])}.')
        ok(norm(g['head']) == head and norm(g['text']) == txt, f'{c}: {g["head"]!r} / {g["text"]!r}')
        ok(g['marker'].endswith('%') and abs(float(g['marker'][:-1]) - min(99, max(1, lo))) < 1e-3, f'{c}: marker {g["marker"]}')
    ok(not errs, f'JS errors {errs}')
    pg.close()
    # ---- widths
    for w, h in ((320, 700), (360, 800), (390, 844), (1280, 800)):
        pg, errs = page_at(w, h)
        ok(pg.evaluate('document.documentElement.scrollWidth - window.innerWidth') <= 0, f'{w}px: wider than the screen')
        pg.click('#calc-men-btn')
        pg.wait_for_timeout(150)
        ok(pg.evaluate('document.documentElement.scrollWidth - window.innerWidth') <= 0, f'{w}px after Calculate: wider than the screen')
        ok(not errs, f'{w}px: JS errors {errs}')
        pg.close()
    br.close()

for f in fails[:50]:
    print('FAIL', f)
print(f'{checks:,} checks, {len(fails)} failures, 0 skipped')
sys.exit(1 if fails else 0)
