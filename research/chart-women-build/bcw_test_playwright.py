#!/usr/bin/env python3
"""BMI chart for women checks in Chromium (CMB-014). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/chart-women-build/bcw_test_playwright.py http://localhost:8000 research/chart-women-build/bcw_stats.json
  - chart table: all 90 cells equal the whole-pound and whole-kilogram limits found here by brute force (each unit on its
    own, BMI rounded to one decimal), not by the rule gen_bcw.py uses; every row has its #h-F-I anchor;
  - printable chart: bcw_grid.csv (the values drawn in the image) equals the brute-force BMI at every height and weight;
    the image loads at 1360 px, has alt text and links to itself;
  - the US women table and both data figures equal bcw_stats.json; the pregnancy table equals CDC's values;
  - rendered SVG labels don't overlap, stay inside their figure and sit on no shape except a bar that holds the label,
    at 390 and 1280 px;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px; the chart table scrolls inside its frame;
  - every contents chip lands on its section; every FAQ question opens with one tap; the FAQ JSON-LD equals the answers;
  - no {TODAY} placeholder is left in the page."""
import sys, os, json, math, re, csv
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
S = json.load(open(stats))
C = S['categories']
GRID = os.path.join(os.path.dirname(os.path.abspath(stats)), 'bcw_grid.csv')
URL = base + '/blog/bmi-chart-women/'
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
BANDS = [(0, 18.4), (18.5, 24.9), (25.0, 29.9), (30.0, 34.9), (35.0, 39.9), (40.0, 99)]

def brute(h_in, lo, hi, unit):
    m = h_in * 0.0254
    ws = [w for w in range(10, 700) if lo <= r1(w * 703 / h_in ** 2 if unit == 'lb' else w / m ** 2) <= hi]
    return ws[0], ws[-1]

def want_cell(h, band):
    lb, kg = brute(h, *BANDS[band], 'lb'), brute(h, *BANDS[band], 'kg')
    if band == 0: return f'≤ {lb[1]} lb ({kg[1]} kg)'
    if band == 5: return f'≥ {lb[0]} lb ({kg[0]} kg)'
    return f'{lb[0]}–{lb[1]} lb ({kg[0]}–{kg[1]} kg)'

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# The printable chart's values (the image is drawn from bcw_grid.csv by chart_bcw.py).
rows = list(csv.reader(open(GRID)))
weights = [int(c.split()[0]) for c in rows[0][2:]]
ok(weights == list(range(90, 251, 10)), f'grid weights {weights}')
ok(len(rows) == 16, f'{len(rows) - 1} grid rows')
for r in rows[1:]:
    m = re.match(r"(\d)'(\d{1,2})\"", r[0]); h = int(m.group(1)) * 12 + int(m.group(2))
    ok(r[1] == f'{h * 2.54:.1f}', f'grid cm {r[0]}')
    for lb, v in zip(weights, r[2:]):
        ok(v == f'{r1(lb * 703 / h ** 2):.1f}', f'grid {r[0]} {lb} lb: {v}')

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    html = pg.content()
    ok('{TODAY}' not in html, '{TODAY} placeholder left in the page')

    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [r.id, ...[...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim())])])""")
    ok(len(tables) == 3, f'{len(tables)} tables')
    chart = [t for t in tables if t[0].startswith('BMI chart for women')][0][1]
    ok(len(chart) == 15, f'{len(chart)} chart rows')
    for row in chart:
        m = re.match(r"(\d)′(\d{1,2})″ \((\d+\.\d) cm\)", row[1]); ok(bool(m), f'height cell {row[1]!r}')
        h = int(m.group(1)) * 12 + int(m.group(2))
        ok(row[0] == f'h-{h // 12}-{h % 12}', f'row anchor {row[0]} for {row[1]}')
        ok(m.group(3) == f'{h * 2.54:.1f}', f'{row[1]}: cm label')
        for band in range(6):
            ok(row[2 + band] == want_cell(h, band), f'{row[1]} band {band}: {row[2 + band]!r} vs {want_cell(h, band)!r}')
    women = [t for t in tables if t[0].startswith('US women by BMI category')][0][1]
    keys = ['20-39', '40-59', '60+', 'all_ages']
    for row, k in zip(women, keys):
        want = [f"{C[k][c]['pct']}%" for c in ('underweight', 'healthy', 'overweight', 'obesity', 'class_3')] + [f"{C[k]['n']:,}"]
        ok(row[2:] == want, f'women row {row} vs {k}')
    preg = [t for t in tables if t[0].startswith('Recommended weight gain')][0][1]
    ok([(r[1].split(' ')[0], r[2].split(' (')[0]) for r in preg] ==
       [('Under', '28–40 lb'), ('18.5–24.9', '25–35 lb'), ('25.0–29.9', '15–25 lb'), ('30.0–39.9', '11–20 lb')], f'pregnancy {preg}')

    # Printable chart image
    img = pg.evaluate("""() => { const i = document.querySelector('main figure img'); const a = i.closest('a');
        return [i.getAttribute('src'), i.getAttribute('alt'), +i.getAttribute('width'), +i.getAttribute('height'), a && a.getAttribute('href')]; }""")
    ok(img[0] == '/assets/images/charts/bmi-chart-women.png' and img[4] == img[0], f'chart image link {img}')
    ok(len(img[1]) > 60 and 'BMI chart for women' in img[1], f'chart alt {img[1]!r}')
    ok((img[2], img[3]) == (1360, 1492), f'chart size attributes {img}')
    pg.evaluate("document.querySelector('main figure img').scrollIntoView()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("document.querySelector('main figure img').naturalWidth") == 1360, 'chart image did not load')

    # Figure labels come from the same data
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => [s.getAttribute('aria-labelledby'),
        [...s.querySelectorAll('text')].map(e => e.textContent)])""")
    ok([f[0] for f in figs] == ['fig-hero-t fig-hero-d', 'fig-women-t fig-women-d', 'fig-waist-t fig-waist-d'], f'figures {[f[0] for f in figs]}')
    hero = figs[0][1]
    ok([t for t in hero if re.fullmatch(r"\d′\d{1,2}″", t)] == [f'{h // 12}′{h % 12}″' for h in range(58, 73)], 'hero height labels')
    lb64 = brute(64, 18.5, 24.9, 'lb')
    ok(any(f'{lb64[0]}–{lb64[1]} lb' in t for t in hero), 'hero 5′4″ subtitle')
    wfig = [t for t in figs[1][1] if t.endswith('%')]
    vals = {f"{C[k][c]['pct']:.1f}%" for k in keys for c in ('healthy', 'overweight', 'obesity')}
    ok(len(wfig) == 12 and set(wfig) <= vals, f'women figure labels {wfig}')
    wst = [t for t in figs[2][1] if t.endswith('%')]
    WB = S['waist']['by_bmi']
    ok(wst == [f"{WB[c][m]['pct']:.1f}%" for m in ('waist_88_plus', 'whtr_05_plus') for c in ('healthy', 'overweight', 'obesity')],
       f'waist figure labels {wst}')

    # Contents chips land on their sections; FAQ opens with one tap; JSON-LD equals the visible answers
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(len(chips) == 9, f'{len(chips)} contents chips')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    qs = pg.query_selector_all('.faq-question')
    ok(len(qs) == 11, f'{len(qs)} FAQ questions')
    for i, q in enumerate(qs):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
        ok(pg.evaluate('i => document.querySelectorAll(".faq-answer")[i].getBoundingClientRect().height > 20', i), f'FAQ {i} answer not shown')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok([x['@type'] for x in ld] == ['Article', 'BreadcrumbList', 'FAQPage'], f'JSON-LD types {[x["@type"] for x in ld]}')
    faq = [x for x in ld if x['@type'] == 'FAQPage'][0]['mainEntity']
    vis = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([[q['name'], q['acceptedAnswer']['text']] for q in faq] == vis, 'FAQ JSON-LD differs from the visible answers')
    art = [x for x in ld if x['@type'] == 'Article'][0]
    ok(re.fullmatch(r'\d{4}-\d{2}-\d{2}', art['dateModified']) is not None, f"dateModified {art['dateModified']!r}")
    ok(art['headline'] == pg.inner_text('h1'), 'Article headline is not the H1')
    crumbs = [x for x in ld if x['@type'] == 'BreadcrumbList'][0]['itemListElement']
    ok(crumbs[2]['name'] == pg.inner_text('h1'), 'breadcrumb name is not the H1')
    ok(not errs, f'JS errors {errs}')

    # Figures and page width
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fit = pg.evaluate("() => { const t = document.querySelector('.weight-chart'), f = t.closest('.table-responsive'); return [t.offsetWidth, f.clientWidth, getComputedStyle(f).overflowX]; }")
        ok(fit[2] == 'auto' and (fit[0] <= fit[1] or w < 1280), f'chart table at {w}: {fit}')
        if w == 1280: ok(fit[0] <= fit[1], f'chart table scrolls on desktop: {fit}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom], size: parseFloat(getComputedStyle(svg.querySelector('text')).fontSize) * r.width / svg.viewBox.baseVal.width,
                        texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e), e.getAttribute('fill')]),
                        shapes: [...svg.querySelectorAll('rect, path')].filter(e => e.getAttribute('fill') !== 'none').map(e => [e.getAttribute('fill'), ...bx(e)])}; })""")
            ok(len(res) == 3, f'{len(res)} figures at {w}')
            for f in res:
                L, T, R, B = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L - 0.5 and a[3] <= R + 0.5 and a[2] >= T - 0.5 and a[4] <= B + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s in f['shapes']:
                        hit = a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5
                        inside = a[1] >= s[1] + 1 and a[3] <= s[3] - 1 and a[2] >= s[2] - 3 and a[4] <= s[4] + 3
                        if hit and not (a[5] in ('#ffffff', '#111827') and inside):
                            fails.append(f'{w}px label over a shape: {a[0]!r} / {s[0]}')
    b.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
sys.exit(1 if fails else 0)
