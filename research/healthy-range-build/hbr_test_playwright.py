#!/usr/bin/env python3
"""Healthy BMI range guide checks in Chromium (CMB-013). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/healthy-range-build/hbr_test_playwright.py http://localhost:8000 research/healthy-range-build/healthy_stats.json
  - height table: every cell equals the whole-pound and whole-kilogram limits found here by brute force (each unit on its
    own, BMI rounded to one decimal), not by the formula gen_hbr.py uses;
  - the age x sex table and the chart labels equal healthy_stats.json; the hazard-ratio table and figure equal the
    published values (Global BMI Mortality Collaboration, Lancet 2016);
  - rendered SVG labels don't overlap, stay inside their figure and sit on no shape except a band that holds a white
    label, at 390 and 1280 px;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px;
  - every contents chip lands on its section; every FAQ question opens with one tap; the FAQ JSON-LD equals the answers;
  - no {TODAY} placeholder is left in the page."""
import sys, json, math, re
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
G = json.load(open(stats))['groups']
URL = base + '/blog/healthy-bmi-range/'
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10

def brute(h_in, lo, hi, unit):
    m = h_in * 0.0254
    ws = [w for w in range(20, 500) if lo <= r1(w * 703 / h_in ** 2 if unit == 'lb' else w / m ** 2) <= hi]
    return ws[0], ws[-1]

GBMC = [('15–18.4', '1.51', '1.43–1.59'), ('18.5–19.9', '1.13', '1.09–1.17'), ('20–22.4', '1.00', '0.98–1.02'),
        ('22.5–24.9', '1.00', '0.99–1.01'), ('25–27.4', '1.07', '1.07–1.08'), ('27.5–29.9', '1.20', '1.18–1.22'),
        ('30–34.9', '1.45', '1.41–1.48'), ('35–39.9', '1.94', '1.87–2.01'), ('40–59.9', '2.76', '2.60–2.92')]

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    html = pg.content()
    ok('{TODAY}' not in html, '{TODAY} placeholder left in the page')

    # Tables: [caption, rows of cell texts]
    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim()))])""")
    ok(len(tables) == 5, f'{len(tables)} tables')
    byh = [t for t in tables if t[0].startswith('Healthy weight and overweight by height')][0][1]
    ok(len(byh) == 10, f'{len(byh)} height rows')
    for row in byh:
        m = re.match(r"(\d)′(\d{1,2})″ \((\d+\.\d) cm\)", row[0]); ok(bool(m), f'height cell {row[0]!r}')
        h = int(m.group(1)) * 12 + int(m.group(2))
        ok(m.group(3) == f'{h * 2.54:.1f}', f'{row[0]}: cm label')
        for cell, (lo, hi) in ((row[1], (18.5, 24.9)), (row[2], (25.0, 29.9))):
            lb, kg = brute(h, lo, hi, 'lb'), brute(h, lo, hi, 'kg')
            ok(cell == f'{lb[0]}–{lb[1]} lb ({kg[0]}–{kg[1]} kg)', f'{row[0]} {lo}-{hi}: {cell!r} vs {lb} lb {kg} kg')
    age = [t for t in tables if t[0].startswith('US adults with a healthy BMI')][0][1]
    keys = ['20-39', '40-59', '60+', 'all_ages']
    ok(len(age) == 4, f'{len(age)} age rows')
    for row, k in zip(age, keys):
        ok(row[1:] == [f"{G[g][k]['healthy']}%" for g in ('all', 'men', 'women')], f'age row {row} vs {k}')
    cats = [t for t in tables if t[0].startswith('Adult BMI categories')][0][1]
    ok([r[2] for r in cats] == ['1.6%', '26.0%', '32.1%', '20.6%', '10.3%', '9.4%'], f'category shares {[r[2] for r in cats]}')
    hr = [t for t in tables if t[0].startswith('Risk of death by BMI')][0][1]
    ok([(r[0], r[1].replace('reference', '').strip(), r[2]) for r in hr] == GBMC, f'hazard-ratio table {hr}')
    ok(hr[3][1] == '1.00 reference', f'reference row {hr[3]}')

    # Figure labels: the chart values come from the same data
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => [s.getAttribute('aria-labelledby'),
        [...s.querySelectorAll('text')].map(e => e.textContent)])""")
    ok([f[0] for f in figs] == ['fig-hero-t fig-hero-d', 'fig-risk-t fig-risk-d', 'fig-share-t fig-share-d'], f'figures {[f[0] for f in figs]}')
    risk = figs[1][1]
    ok(all(v in risk for _, v, _ in GBMC) and all(band in risk for band, _, _ in GBMC), f'risk figure labels {risk}')
    share = figs[2][1]
    want = [f"{G[g][k]['healthy']:.1f}" for k in keys for g in ('men', 'women')]
    ok([t for t in share if re.fullmatch(r'\d+\.\d', t)] == want, f'share figure values {share}')
    hero = figs[0][1]
    for ft, inch in ((5, 0), (5, 6), (6, 0)):
        h = ft * 12 + inch; lb, kg = brute(h, 18.5, 24.9, 'lb'), brute(h, 18.5, 24.9, 'kg')
        ok(f'{lb[0]}–{lb[1]} lb ({kg[0]}–{kg[1]} kg)' in hero, f'hero row {ft}′{inch}″')

    # Contents chips land on their sections; FAQ opens with one tap; JSON-LD equals the visible answers
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

    # Figures and page width
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom],
                        texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e), e.getAttribute('fill')]),
                        shapes: [...svg.querySelectorAll('rect')].filter(e => e.getAttribute('fill') !== 'none').map(e => [e.getAttribute('fill'), ...bx(e)])}; })""")
            ok(len(res) == 3, f'{len(res)} figures at {w}')
            for f in res:
                L, T, R, B = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L - 0.5 and a[3] <= R + 0.5 and a[2] >= T - 0.5 and a[4] <= B + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s in f['shapes']:
                        if s[0] == '#ecfdf5': continue                       # the healthy-range band behind the bars
                        hit = a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5
                        inside = a[1] >= s[1] and a[3] <= s[3] and a[2] >= s[2] - 1 and a[4] <= s[4] + 1
                        if hit and not (a[5] == '#ffffff' and inside):
                            fails.append(f'{w}px label over a shape: {a[0]!r} / {s[0]}')
    b.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)
