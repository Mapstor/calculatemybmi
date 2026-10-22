#!/usr/bin/env python3
"""Women's BMI calculator checks in Chromium (CMB-017). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/women-calc-build/wbc_test_playwright.py http://localhost:8000 research/women-calc-build/wbc_stats.json
  - the rank: 14 inputs in both units (both tails included) give the rank, the three age-group ranks and the median line
    computed here from wbc_stats.json by the page's rule (strictly lower / strictly higher; equal BMIs on neither side);
  - "US women with a BMI like yours": the body fat line for each whole BMI (CDC DXA bins with 50 or more women, 45 and over
    as one bin) and the waist line for each category, hidden when there is nothing to say;
  - the waist check: hidden without a waist or with one out of range; 16 cases cover every NICE class, the BMI-35 limit,
    the US-guidelines line in both units, every ADA outcome and the Asian-background sentence only when it differs;
  - typed-in values (worked out by hand, not read from the stats): the starting values give BMI 24.0, "Higher than 24% of
    US women", 32% / 19% / 21% by age, 36.1% body fat (33.6% to 38.7%), ratio 0.51 (33 / 64 = 0.516, cut) with the Asian
    sentence; the fact-check's cases: a waist just under half the height (31.7 in at 5'4", 80.5 cm at 162 cm) shows 0.49
    and is not "at least half"; 34.8 in at 5'11" is "not over" 35 in and, at 88.4 cm, meets the ADA's 88 cm; exactly half
    (32 in at 5'4", or 31.96 in printed as 32) shows 0.50; 5'5" half height is 82.6 cm;
  - the tables (percentiles, decades, healthy weight by height against the weight-table gate's rule, pregnancy gains),
    the figure descriptions and hover labels equal the stats;
  - head: title, description, one robots max-image-preview:large, og:image and twitter:image = the 16:9 preferred image
    (1200 x 675), the WebApplication image list and the WebPage primaryImageOfPage, author named, preferred files at size;
  - the Calculate button ends above the fold at 360 and 390 px; the page is never wider than the screen at 320, 360, 390
    and 1280 px; tables fit their frame at 390 and 1280; rendered SVG labels don't overlap and stay inside the figure;
  - every contents chip lands on its section; every FAQ opens with one tap; FAQ JSON-LD equals the visible answers;
    no JavaScript error."""
import sys, os, json, re, math, struct
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
S = json.load(open(stats))
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(stats)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds
BFP = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
BCW = json.load(open(os.path.join(ROOT, 'research/chart-women-build/bcw_stats.json')))
URL = base + '/women-bmi-calculator/'
SITE = 'https://calculatemybmi.net'
C, T, DEC = S['curves'], S['table'], S['decades']

def f1(x): return f'{x:.1f}'
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def cut2(x): return math.floor(x * 100 + 1e-9) / 100
def cm1(inches): return str((Decimal(str(inches)) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None

# ---- the page's rules, written out again here
def pct(q, b):
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
def rk(q, b): return pct(q, round(b * 10 - 1) / 10), 100 - pct(q, b)
def n(x): return 99 if x > 99 else int(math.floor(x + 0.5))
def lab(r): return f'lower than {n(r[1])}%' if r[0] < 1 else f'higher than {n(r[0])}%'
def rank_text(b):
    lo, hi = rk(C['all'], b); s = f1(b)
    if lo < 1: t = f'Your BMI of {s} is lower than about {n(hi)}% of US women aged 20 and over.'
    elif hi < 1: t = f'Your BMI of {s} is higher than about {n(lo)}% of US women aged 20 and over.'
    else: t = f'Your BMI of {s} is higher than about {n(lo)}% of US women aged 20 and over and lower than about {n(hi)}%.'
    t += (f' By age it is {lab(rk(C["20-39"], b))} of women aged 20 to 39, {lab(rk(C["40-59"], b))} of those 40 to 59 and '
          f'{lab(rk(C["60+"], b))} of those 60 and over. The median US woman has a BMI of {f1(T["all"]["p50"])}.')
    head = lab((lo, hi)); return head[0].upper() + head[1:] + ' of US women', t

BINS = {int(k): v for k, v in BFP['bmi']['by_bin']['f'].items() if v.get('n', 0) >= 50}
WS = {c: (BCW['waist']['by_bmi'][c]['waist_88_plus']['pct'], BCW['waist']['by_bmi'][c]['whtr_05_plus']['pct'])
      for c in ('healthy', 'overweight', 'obesity')}
def share(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{x:.1f}%'
def like_texts(b):
    k = min(int(math.floor(b)), 45); fat = waist = ''
    if k in BINS:
        v = BINS[k]
        fat = (f'Body fat: on CDC’s body scans, women aged 20 to 59 with a BMI of {"45 or more" if k >= 45 else f"{k} to {k}.9"} '
               f'had a median of {f1(v["p50"])}%; the middle half measured {f1(v["p25"])}% to {f1(v["p75"])}%.')
    c = None if b < 18.5 else 'healthy' if b < 25 else 'overweight' if b < 30 else 'obesity'
    if c:
        cn = {'healthy': 'a healthy BMI', 'overweight': 'an overweight BMI', 'obesity': 'a BMI of 30 or more'}[c]
        waist = (f'Waist: among US women with {cn}, {share(WS[c][0])} have a waist of 88 cm (34.6 in) or more and '
                 f'{share(WS[c][1])} one at least half their height.')
    return fat, waist

def ada(b, ratio, cm, asian):
    B0, B1, line = (27.5, 23, 80) if asian else (30, 25, 88)
    if b >= B0: return 'bmi'
    if b >= B1: return 'ratio' if ratio >= 0.5 else 'cm' if cm >= line else 'small'
    return 'low'
def ada_text(o, b, cm, q):
    s, c = f1(b), f'{cm:.1f}'
    L = 'Under the 2026 ADA standards, ' + ('for women of non-Asian background ' if q else '')
    return L + {'bmi': f'a BMI of {s} counts as obesity on BMI alone.',
                'ratio': f'a BMI of {s} counts as obesity with a waist of at least half the height, and yours is.',
                'cm': f'a BMI of {s} counts as obesity with a waist of 88 cm or more, and yours, at {c} cm, is.',
                'small': f'a BMI of {s} counts as obesity only with a waist of at least half the height or of 88 cm or more; '
                         f'at {c} cm, yours is under both.',
                'low': 'the waist doesn’t change the class at a BMI under 25.'}[o]
def is_ob(o): return o in ('bmi', 'ratio', 'cm')
def waist_texts(b, h, w, metric):
    wr = r1(w)                                                      # the waist as printed; the ratio comes from it
    cm = wr if metric else r1(wr * 2.54)
    wtxt = f'{wr:g} cm ({r1(wr / 2.54):.1f} in)' if metric else f'{wr:g} in ({cm:.1f} cm)'
    ratio = cut2(wr / h); rs = f'{ratio:.2f}'
    t1 = f'Your waist, {wtxt}, is {rs} of your height.'
    if b >= 35: t1 += ' NICE’s ratio classes are for adults with a BMI under 35, so they don’t apply at yours.'
    elif ratio < 0.4: t1 += ' NICE’s classes for adults with a BMI under 35 start at 0.4 (0.4 to 0.49 is healthy central adiposity).'
    else:
        cls = ('0.4 to 0.49 is healthy central adiposity' if ratio < 0.5 else '0.5 to 0.59 is increased central adiposity'
               if ratio < 0.6 else '0.6 or more is high central adiposity')
        t1 += f' On NICE’s scale for adults with a BMI under 35, {cls}.'
    over = wr > 88 if metric else wr > 35
    t2 = (f'US guidelines treat a waist over {"88 cm" if metric else "35 in"} as a sign of higher risk for women, mainly at a '
          f'BMI of 25 to 34.9. Yours is {"over" if over else "not over"} that line.')
    na, as_ = ada(b, ratio, cm, False), ada(b, ratio, cm, True)
    q = is_ob(as_) and not is_ob(na)
    t3 = ada_text(na, b, cm, q)
    if q:
        t3 += (' For women of Asian background the lines are lower: a BMI of 27.5, or 23 with a waist of at least half the height '
               'or of 80 cm (31.5 in). With your numbers that counts as obesity.')
    if is_ob(as_) and b < 30:
        t3 += f' By BMI alone (CDC) it is {"underweight" if b < 18.5 else "a healthy weight" if b < 25 else "overweight"}.'
    return f'Waist-to-height ratio {rs}', t1, t2, t3

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

with sync_playwright() as p:
    br = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
    ok('{TODAY}' not in pg.content(), '{TODAY} left in the page')
    ok(pg.evaluate("document.querySelector('.calculate-btn').getBoundingClientRect().bottom") <= 844, 'Calculate below the fold at 390')
    ok(pg.evaluate("[...document.querySelectorAll('#panel-women input')].every(i => document.querySelector('label[for=\"' + i.id + '\"]'))"),
       'an input without its label')

    def run(unit, h, wt, waist=None):
        pg.click(f'#panel-women .unit-btn[data-unit="{unit}"]')
        if unit == 'imperial':
            pg.fill('#women-height-ft', str(h[0])); pg.fill('#women-height-in', str(h[1])); pg.fill('#women-weight-lbs', str(wt))
            pg.fill('#women-waist-in', '' if waist is None else str(waist))
        else:
            pg.fill('#women-height-cm', str(h)); pg.fill('#women-weight-kg', str(wt)); pg.fill('#women-waist-cm', '' if waist is None else str(waist))
        pg.click('#calc-women-btn'); pg.wait_for_timeout(60)
        return pg.evaluate("""() => { const g = i => document.getElementById(i), vis = i => !g(i).hidden;
            return {bmi: g('women-bmi-value').textContent, rank: vis('women-rank'), rv: g('women-rank-value').textContent,
                    rt: g('women-rank-text').textContent, like: vis('women-like'), fat: vis('women-like-fat') ? g('women-like-fat').textContent : '',
                    lw: vis('women-like-waist') ? g('women-like-waist').textContent : '', waist: vis('women-waist'),
                    wv: g('women-waist-value').textContent, w1: g('women-waist-ratio').textContent, w2: g('women-waist-us').textContent,
                    w3: g('women-waist-ada').textContent}; }""")

    def bmi_of(unit, h, wt):
        if unit == 'imperial':
            hi = h[0] * 12 + h[1]; return r1(wt * 703 / hi / hi), hi
        return r1(wt / (h / 100) ** 2), h

    # 1. The starting values (typed-in checks).
    o = run('imperial', (5, 4), 140, 33)
    ok(o['bmi'] == '24.0' and o['rv'] == 'Higher than 24% of US women', f'start: {o["bmi"]} {o["rv"]!r}')
    ok('higher than 32% of women aged 20 to 39, higher than 19% of those 40 to 59 and higher than 21% of those 60 and over' in o['rt'],
       f'start ages: {o["rt"]!r}')
    ok('a median of 36.1%; the middle half measured 33.6% to 38.7%' in o['fat'], f'start fat: {o["fat"]!r}')
    ok(o['wv'] == 'Waist-to-height ratio 0.51' and o['w3'].startswith('Under the 2026 ADA standards, for women of non-Asian background the waist')
       and 'For women of Asian background' in o['w3'] and o['w3'].endswith('it is a healthy weight.'),
       f'start waist: {o["wv"]!r} {o["w3"]!r}')

    # 2. Rank and "like you" across both units and both tails.
    cases = [('imperial', (5, 4), 140), ('imperial', (5, 2), 130), ('imperial', (5, 6), 200), ('imperial', (5, 0), 90),
             ('imperial', (5, 8), 300), ('imperial', (5, 3), 400), ('imperial', (6, 0), 105), ('imperial', (5, 5), 160),
             ('metric', 162, 63), ('metric', 170, 90), ('metric', 150, 40), ('metric', 158, 160), ('metric', 175, 49),
             ('metric', 165, 74)]
    for unit, h, wt in cases:
        o = run(unit, h, wt)
        b, _ = bmi_of(unit, h, wt)
        head, txt = rank_text(b)
        ok(o['bmi'] == f1(b), f'{unit} {h} {wt}: BMI {o["bmi"]} vs {f1(b)}')
        ok(o['rank'] and o['rv'] == head and o['rt'] == txt, f'{unit} {h} {wt}: rank {o["rv"]!r} / {o["rt"]!r} vs {head!r} / {txt!r}')
        fat, lw = like_texts(b)
        ok(o['fat'] == fat and o['lw'] == lw and o['like'] == bool(fat or lw), f'{unit} {h} {wt}: like {o["fat"]!r} {o["lw"]!r}')
        ok(not o['waist'], f'{unit} {h} {wt}: waist box shown without a waist')

    # 3. The waist check.
    wcases = [('imperial', (5, 4), 140, 33), ('imperial', (5, 4), 160, 36), ('imperial', (5, 6), 160, 30),
              ('imperial', (5, 4), 169, 30), ('imperial', (5, 8), 171, 33), ('imperial', (5, 4), 210, 44),
              ('imperial', (5, 10), 120, 26), ('imperial', (5, 6), 160, 34.8), ('metric', 165, 72, 82),
              ('metric', 165, 70, 88.5), ('metric', 160, 60, 70),
              ('imperial', (5, 4), 146, 31.7), ('metric', 162, 66, 80.5), ('imperial', (5, 11), 179, 34.8),
              ('imperial', (5, 4), 146, 32), ('imperial', (5, 4), 146, 31.96)]
    for unit, h, wt, w in wcases:
        o = run(unit, h, wt, w)
        b, hh = bmi_of(unit, h, wt)
        want = waist_texts(b, hh, w, unit == 'metric')
        ok(o['waist'] and (o['wv'], o['w1'], o['w2'], o['w3']) == want, f'waist {unit} {h} {wt} {w}: {(o["wv"], o["w1"], o["w2"], o["w3"])} vs {want}')
    o = run('imperial', (5, 4), 140, 5); ok(not o['waist'], 'waist 5 in accepted')
    o = run('metric', 162, 63, 300); ok(not o['waist'], 'waist 300 cm accepted')
    # Typed-in waist outcomes.
    o = run('imperial', (5, 4), 169, 30); ok('For women of Asian background' in o['w3'] and o['w3'].endswith('it is overweight.'), f'29.0 small waist: {o["w3"]!r}')
    o = run('imperial', (5, 4), 160, 36); ok('Asian' not in o['w3'] and 'counts as obesity with a waist of at least half the height' in o['w3'], f'27.5: {o["w3"]!r}')
    o = run('metric', 165, 70, 88.5); ok(o['w2'] == 'US guidelines treat a waist over 88 cm as a sign of higher risk for women, mainly at a BMI '
                                         'of 25 to 34.9. Yours is over that line.', f'88.5 cm: {o["w2"]!r}')
    o = run('imperial', (5, 6), 160, 34.8); ok(o['w2'].endswith('Yours is not over that line.') and '(88 cm)' not in o['w2'], f'34.8 in: {o["w2"]!r}')
    o = run('imperial', (5, 4), 210, 44); ok(o['w3'].startswith('Under the 2026 ADA standards, a BMI of 36.0 counts as obesity on BMI alone.'), f'36.0: {o["w3"]!r}')
    # The fact-check's cases (typed in).
    o = run('imperial', (5, 4), 146, 31.7)
    ok(o['bmi'] == '25.1' and o['wv'] == 'Waist-to-height ratio 0.49' and 'healthy central adiposity' in o['w1']
       and o['w3'].startswith('Under the 2026 ADA standards, for women of non-Asian background a BMI of 25.1 counts as obesity only '
                              'with a waist of at least half the height or of 88 cm or more; at 80.5 cm, yours is under both.')
       and 'With your numbers that counts as obesity.' in o['w3'], f'31.7 in at 5′4″: {o["wv"]!r} {o["w3"]!r}')
    o = run('metric', 162, 66, 80.5)
    ok(o['wv'] == 'Waist-to-height ratio 0.49' and 'at 80.5 cm, yours is under both' in o['w3'], f'80.5 cm at 162: {o["wv"]!r} {o["w3"]!r}')
    o = run('imperial', (5, 11), 179, 34.8)
    ok(o['bmi'] == '25.0' and o['w1'].startswith('Your waist, 34.8 in (88.4 cm), is 0.49 of your height.')
       and o['w2'].endswith('Yours is not over that line.')
       and o['w3'] == 'Under the 2026 ADA standards, a BMI of 25.0 counts as obesity with a waist of 88 cm or more, and yours, at 88.4 cm, is. '
                      'By BMI alone (CDC) it is overweight.', f'34.8 in at 5′11″: {o["w1"]!r} {o["w3"]!r}')
    o = run('imperial', (5, 4), 146, 32)
    ok(o['wv'] == 'Waist-to-height ratio 0.50' and 'with a waist of at least half the height, and yours is.' in o['w3'], f'32 in at 5′4″: {o["w3"]!r}')
    o = run('imperial', (5, 4), 146, 31.96)
    ok(o['wv'] == 'Waist-to-height ratio 0.50' and o['w1'].startswith('Your waist, 32 in (81.3 cm),'), f'31.96 in: {o["w1"]!r}')
    ok('32.5 inches (82.6 cm)' in pg.text_content('#faq'), 'FAQ 5′5″ half height')

    # 4. Tables and figures.
    tables = pg.evaluate("""() => [...document.querySelectorAll('main table:not(.er-table)')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim()))])""")
    tb = {cap: rows for cap, rows in tables}
    ok(len(tables) == 4, f'{len(tables)} tables')
    want = [[lab_] + [f1(T[g][k]) for g in ('all', '20-39', '40-59', '60+')] for k, lab_ in
            (('p5', '5th'), ('p10', '10th'), ('p25', '25th'), ('p50', 'Median'), ('p75', '75th'), ('p90', '90th'), ('p95', '95th'))]
    ok(tb.get('BMI of US women by percentile and age group') == want, 'percentile table')
    ages = ('20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')
    want = [[d.replace('-', '–'), f1(DEC[d]['p50']), f'{f1(DEC[d]["p25"])}–{f1(DEC[d]["p75"])}', f'{f1(DEC[d]["healthy"]["pct"])}%']
            for d in ages]
    ok(tb.get('BMI of US women by decade of age') == want, 'decade table')
    hrows = tb.get('Healthy weight and half the height, women 4′10″ to 6′0″', [])
    ok(len(hrows) == 15, f'{len(hrows)} height rows')
    for row, h in zip(hrows, range(58, 73)):
        lb, kg = gate_bounds('lb', h, h * 2.54, 1), gate_bounds('kg', h, h * 2.54, 1)
        ok(row == [f'{h // 12}′{h % 12}″ ({cm1(h)} cm)', f'{lb[0]}–{lb[1]} lb ({kg[0]}–{kg[1]} kg)', f'{h / 2:.1f} in ({cm1(Decimal(h) / 2)} cm)'],
           f'height row {row}')
    ok(hrows[7][2] == '32.5 in (82.6 cm)', f'5′5″ half height {hrows[7][2] if len(hrows) > 7 else None}')
    ok(tb.get('Recommended weight gain in pregnancy with one baby') == [['Under 18.5', '28–40 lb'], ['18.5–24.9', '25–35 lb'],
                                                                       ['25.0–29.9', '15–25 lb'], ['30.0–39.9', '11–20 lb']], 'pregnancy table')
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => [s.getAttribute('aria-labelledby'),
        (s.querySelector('desc') || {}).textContent, [...s.querySelectorAll('rect title')].map(t => t.textContent)])""")
    ok([f[0] for f in figs] == ['ex-t ex-d', 'age-t age-d'], f'figures {[f[0] for f in figs]}')
    for d in ages:
        v = DEC[d]; nm = d.replace('-', ' to ').replace('+', ' and over')
        ok(f'{nm}: median {f1(v["p50"])}, middle half {f1(v["p25"])} to {f1(v["p75"])}.' in figs[1][1], f'age desc {d}')
        ok(f'Women {nm}: median BMI {f1(v["p50"])}, middle half {f1(v["p25"])}–{f1(v["p75"])}, 10th to 90th percentile '
           f'{f1(v["p10"])}–{f1(v["p90"])} ({v["n"]:,} women)' in figs[1][2], f'age hover {d}')

    # 5. Head, JSON-LD, images.
    head = pg.evaluate("""() => ({title: document.title, desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content),
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content),
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content)})""")
    P = {r: f'{SITE}/assets/images/preferred/women-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['title'] == 'BMI Calculator for Women: Waist Check and US Women Compared', f'title {head["title"]!r}')
    ok(len(head['desc']) <= 160 and 'waist check' in head['desc'], f'description {head["desc"]!r}')
    ok(head['robots'] == ['max-image-preview:large'], f'robots {head["robots"]}')
    ok(head['og'] == [P['16x9']] and head['tw'] == [P['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter {head}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/women-bmi-calculator-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['WebPage', 'WebApplication', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    G = {x['@type']: x for x in ld[0]['@graph']}
    ok(G['WebApplication']['image'] == [P['1x1'], P['4x3'], P['16x9']] and G['WebApplication']['author']['name'] == 'Marko Visic', 'app image/author')
    ok(G['WebPage']['primaryImageOfPage']['url'] == P['16x9'], 'primaryImageOfPage')
    ok(G['BreadcrumbList']['itemListElement'][-1]['name'] == pg.inner_text('h1'), 'breadcrumb name is not the H1')
    vis = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok(len(vis) == 10 and [[q['name'], q['acceptedAnswer']['text']] for q in G['FAQPage']['mainEntity']] == vis, 'FAQ JSON-LD differs from the page')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(len(chips) == 10, f'{len(chips)} chips')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.tagName === "SECTION"; }', href), f'chip {href}')
    qs = pg.query_selector_all('.faq-question')
    for i, q in enumerate(qs):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')

    # 6. Widths, table frames, label collisions.
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 844}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        pg.fill('#women-waist-in', '33'); pg.click('#calc-women-btn'); pg.wait_for_timeout(120)
        ok(pg.evaluate('document.documentElement.scrollWidth') <= w, f'page wider than {w}')
        if w in (360, 390):
            pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
            ok(pg.evaluate("document.querySelector('.calculate-btn').getBoundingClientRect().bottom") <= 844, f'Calculate below the fold at {w}')
        if w in (390, 1280):
            fits = pg.evaluate("() => [...document.querySelectorAll('main .table-responsive > table')].map(t => [t.caption ? t.caption.textContent : '', t.offsetWidth, t.parentElement.clientWidth])")
            for cap, tw, fw in fits:
                ok(tw <= fw + 1, f'table scrolls at {w}: {cap} {tw} > {fw}')
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom], texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)])}; })""")
            for f in res:
                L, T_, R, B = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L - 0.5 and a[3] <= R + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
sys.exit(1 if fails else 0)
