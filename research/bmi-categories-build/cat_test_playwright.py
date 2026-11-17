#!/usr/bin/env python3
"""BMI categories guide checks in Chromium (CMB-067). Needs Python Playwright + Chromium.
Serve the repo (python3 -m http.server 8765), then:
  python3 research/bmi-categories-build/cat_test_playwright.py http://localhost:8765 research/bmi-categories-build/cat_stats.json
  - tables: the category shares and the age table equal cat_stats.json; the obesity-class start weights equal the lightest
    whole pound and whole kilogram found here by brute force (each unit on its own, BMI rounded to one decimal), not by
    the rule gen_cat.py uses; the thinness grades and the children's table read as their sources give them;
  - every percentage with a decimal in the page text is a cat_stats.json value or a published one listed here; the
    worked numbers (300 lb by height, 29.9 against 30.0 at 5'10", where class 3 starts) are recomputed here;
  - the figures' values equal cat_stats.json; rendered SVG labels don't overlap, stay inside their figure and sit on no
    bar, at 390 and 1280 px; the page is never wider than the screen at 320, 360, 390 and 1280 px;
  - every contents chip lands on its section; every FAQ question opens with one tap; the FAQ JSON-LD equals the answers;
    the Article headline is the H1; no JS errors."""
import json
import math
import re
import sys

from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
S = json.load(open(stats))
C, L98, AS, DF = S['categories'], S['line_1998'], S['asian'], S['differences']
URL = base + '/blog/bmi-categories/'
KEYS = ('underweight', 'healthy', 'overweight', 'class_1', 'class_2', 'class_3')
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def lightest(h_in, lo, unit):
    m = h_in * 0.0254
    return next(w for w in range(20, 600) if r1(w * 703 / h_in ** 2 if unit == 'lb' else w / m ** 2) >= lo)

fails, checks = [], 0
def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)

# Percentages the page may print: every cat_stats.json share, CI bound and difference, plus published values.
ALLOWED = set()
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, float):
        ALLOWED.add(f'{o:.1f}')
walk(S)
ALLOWED |= {'40.3'}                       # obesity, classes 1-3 together (20.6 + 10.3 + 9.4), also Data Brief 508's figure

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    ok('{TODAY}' not in pg.content(), '{TODAY} placeholder left in the page')
    # visible text plus the FAQ answers, which stay hidden until opened (innerText skips them)
    text = pg.evaluate("""() => (document.querySelector('main').innerText + ' ' +
        [...document.querySelectorAll('.faq-answer')].map(a => a.textContent).join(' ')).replace(/\\s+/g, ' ')""")

    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim()))])""")
    ok(len(tables) == 5, f'{len(tables)} tables')
    T = {cap: rows for cap, rows in tables}
    cats = T.get('Adult BMI categories and the share of US adults in each, 2021–2023', [])
    ok([r[2] for r in cats] == [f"{C['all']['all_ages'][k]['pct']}%" for k in KEYS], f'category shares {cats}')
    ok([r[1] for r in cats] == ['under 18.5', '18.5–24.9', '25–29.9', '30–34.9', '35–39.9', '40 or more'], f'category ranges {cats}')
    st = T.get('Where each obesity class starts, at five heights', [])
    ok(len(st) == 5, f'{len(st)} start-weight rows')
    for row in st:
        m = re.match(r"(\d)′(\d{1,2})″ \((\d+\.\d) cm\)", row[0])
        ok(bool(m), f'height cell {row[0]!r}')
        if not m: continue
        h = int(m.group(1)) * 12 + int(m.group(2))
        ok(m.group(3) == f'{h * 2.54:.1f}', f'{row[0]}: cm label')
        for cell, lo in zip(row[1:], (30, 35, 40)):
            want = f'≥{lightest(h, lo, "lb")} lb (≥{lightest(h, lo, "kg")} kg)'
            ok(cell == want, f'{row[0]} BMI {lo}: {cell!r} vs {want!r}')
    ok(T.get('WHO thinness grades for adults') == [['Grade 1, mild thinness', '17.0–18.4'], ['Grade 2, moderate thinness', '16.0–16.9'],
                                                    ['Grade 3, severe thinness', 'Under 16.0']], 'thinness grades')
    age = T.get('US adults in each BMI category by age group, 2021–2023', [])
    for row, k in zip(age, KEYS):
        ok(row[1:] == [f"{C['all'][a][k]['pct']}%" for a in ('20-39', '40-59', '60+', 'all_ages')], f'age row {row} vs {k}')
    ok(len(age) == 6, f'{len(age)} age rows')
    kids = T.get('BMI categories for children and teens aged 2 to 19', [])
    ok([r[1] for r in kids] == ['Under the 5th', '5th to under the 85th', '85th to under the 95th', '95th or above',
                                '120% of the 95th or more, or a BMI of 35 or more'], f'children table {kids}')

    # Every one-decimal percentage in the text is ours or published.
    for v in re.findall(r'(\d+\.\d)%', text):
        ok(v in ALLOWED, f'unexpected percentage {v}%')
    # Worked numbers, recomputed here.
    for h, txt in ((72, '6′0″'), (73, '6′1″')):
        ok(f'a BMI of {r1(703 * 300 / h ** 2)} at {txt}' in text, f'300 lb at {txt}')
    ok(f'class 1 at 6′6″ (a BMI of {r1(703 * 300 / 78 ** 2)})' in text, '300 lb at 6′6″')
    ok(all(r1(703 * 300 / h ** 2) >= 40 for h in (70, 71, 72)) and all(35 <= r1(703 * 300 / h ** 2) < 40 for h in range(73, 78)),
       '300 lb class bands')
    gap = r1((30.0 - 29.9) * 70 ** 2 / 703); unit = r1(70 ** 2 / 703)
    ok(f'are {gap} lb apart' in text and f'each whole BMI unit is {unit} lb' in text, '29.9 / 30.0 gap at 5′10″')
    ok(f'At 5′4″ class 3 starts at {lightest(64, 40, "lb")} lb ({lightest(64, 40, "kg")} kg)' in text, 'class 3 at 5′4″')
    ok(f'at 5′10″, at {lightest(70, 40, "lb")} lb ({lightest(70, 40, "kg")} kg)' in text, 'class 3 at 5′10″')
    mv = L98['moved']
    ok(f"{mv['all']['pct']}% of US adults have a BMI from 25 up to the old lines" in text, '1998 share')
    ok(f"That is {mv['men']['pct']}% of men and {mv['women']['pct']}% of women" in text, '1998 by sex')
    ok(DF['moved_men_minus_women']['excludes_0'], '1998 sex difference CI')
    for k in ('bmi_23_plus', 'bmi_25_plus', 'bmi_27_5_plus', 'bmi_30_plus'):
        lead = '95% CI ' if k == 'bmi_30_plus' else ''
        ok(f"{AS[k]['pct']}% ({lead}{AS[k]['ci95'][0]}–{AS[k]['ci95'][1]}%)" in text, f'Asian CI {k}')
    for k in ('class_2_women_minus_men', 'class_1_men_minus_women', 'class_3_40_59_minus_60_plus',
              'class_1_60_plus_minus_20_39', 'healthy_20_39_minus_40_59'):
        ok(DF[k]['excludes_0'] and DF[k]['ci95'][0] > 0, f'stated difference {k} has a CI that includes 0')
    for hr in ('1.45 times as high at 30 to 34.9', '1.94 times at 35 to 39.9', '2.76 times at 40 to 59.9',
               '1.07 times the reference at 25 to 27.4', '1.20 at 27.5 to 29.9'):
        ok(hr in text, f'GBMC value {hr}')

    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => [s.getAttribute('aria-labelledby'),
        [...s.querySelectorAll('text')].map(e => e.textContent)])""")
    ok([f[0] for f in figs] == ['fig-hero-t fig-hero-d', 'fig-asian-t fig-asian-d', 'fig-y98-t fig-y98-d'], f'figures {[f[0] for f in figs]}')
    if len(figs) == 3:
        hero = [t for t in figs[0][1] if t.endswith('%')]
        ok(hero == [f"{C['all']['all_ages'][k]['pct']}%" for k in KEYS] + ['40.3%'], f'hero values {hero}')
        asian = [t for t in figs[1][1] if t.endswith('%')]
        ok(asian == [f"{AS[k]['pct']}%" for k in ('bmi_23_plus', 'bmi_25_plus', 'bmi_27_5_plus', 'bmi_30_plus')], f'asian values {asian}')
        y98 = [t for t in figs[2][1] if t.endswith('%')]
        want = [f"{L98[s][g]['pct']}%" for g in ('all', 'men', 'women') for s in ('at_or_above_old_line', 'at_or_above_25')]
        ok(y98 == want, f'1998 values {y98} vs {want}')

    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(len(chips) == 11, f'{len(chips)} contents chips')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    qs = pg.query_selector_all('.faq-question')
    ok(len(qs) == 8, f'{len(qs)} FAQ questions')
    for i, q in enumerate(qs):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
        ok(pg.evaluate('i => document.querySelectorAll(".faq-answer")[i].getBoundingClientRect().height > 20', i), f'FAQ {i} answer not shown')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    faq = [x for x in ld if x['@type'] == 'FAQPage'][0]['mainEntity']
    vis = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([[q['name'], q['acceptedAnswer']['text']] for q in faq] == vis, 'FAQ JSON-LD differs from the visible answers')
    art = [x for x in ld if x['@type'] == 'Article'][0]
    ok(re.fullmatch(r'\d{4}-\d{2}-\d{2}', art['dateModified']) is not None, f"dateModified {art['dateModified']!r}")
    ok(art['headline'] == pg.inner_text('h1'), 'Article headline is not the H1')
    ok(not errs, f'JS errors {errs}')

    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom],
                        texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                        shapes: [...svg.querySelectorAll('rect, path')].map(e => [e.tagName, ...bx(e)])}; })""")
            ok(len(res) == 3, f'{len(res)} figures at {w}')
            for f in res:
                L, T_, R, B = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L - 0.5 and a[3] <= R + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s in f['shapes']:
                        if a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5:
                            fails.append(f'{w}px label over a {s[0]}: {a[0]!r}')
    b.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails:
    print('FAIL', f)
sys.exit(1 if fails else 0)
