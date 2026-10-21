#!/usr/bin/env python3
"""BMI chart page checks in Chromium (CMB-015). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/bmi-chart-build/bc_test_playwright.py http://localhost:8000 research/bmi-chart-build/bc_stats.json
  - both chart tables: every cell equals the whole-pound and whole-kilogram limits found here by brute force (each unit on
    its own, BMI rounded to one decimal), not by the rule gen_bc.py uses; every row has its anchor (#h-5-9, #h-170cm);
  - heights for each weight: every cell equals the whole-inch (4'10"-6'6") or whole-cm (145-200) heights found by brute force;
  - printable table: bc_grid.csv (the values drawn in the image) holds, at every height and BMI column, the lightest whole
    pound whose rounded BMI reaches the column; the image loads at 1640 px, has alt text and links to itself;
  - the US adults table and the two data figures equal bc_stats.json; the dot figure has 600 dots and its description
    counts them by band correctly;
  - images in search: one robots max-image-preview:large tag; og:image, twitter:image, the Article image list (1:1, 4:3,
    16:9) and primaryImageOfPage name this page's preferred images, which load at 1200x1200, 1200x900 and 1200x675;
  - rendered SVG labels don't overlap, stay inside their figure and sit on no shape, at 390 and 1280 px;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px; chart tables scroll inside their frames;
  - every contents chip lands on its section; every FAQ question opens with one tap; the FAQ JSON-LD equals the answers;
  - no {TODAY} placeholder is left in the page."""
import sys, os, json, math, re, csv, struct
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
S = json.load(open(stats))
C, ADA = S['categories'], S['ada2026']
GRID = os.path.join(os.path.dirname(os.path.abspath(stats)), 'bc_grid.csv')
URL = base + '/bmi-chart/'
SITE = 'https://calculatemybmi.net'
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
BANDS = [(0, 18.4), (18.5, 24.9), (25.0, 29.9), (30.0, 34.9), (35.0, 39.9), (40.0, 99)]
def bmi(w, h_in, unit): return r1(w * 703 / h_in ** 2 if unit == 'lb' else w / (h_in * 0.0254) ** 2)

def brute(h_in, lo, hi, unit):
    ws = [w for w in range(10, 700) if lo <= bmi(w, h_in, unit) <= hi]
    return ws[0], ws[-1]

def want_cell(h_in, band, first, second):
    a, b = brute(h_in, *BANDS[band], first), brute(h_in, *BANDS[band], second)
    if band == 0: return f'≤ {a[1]} {first} ({b[1]} {second})'
    if band == 5: return f'≥ {a[0]} {first} ({b[0]} {second})'
    return f'{a[0]}–{a[1]} {first} ({b[0]}–{b[1]} {second})'

def ftin(i): return f'{i // 12}′{i % 12}″'
def band4(b): return 0 if b < 18.5 else 1 if b < 25 else 2 if b < 30 else 3
def want_heights(w, unit):
    hs = range(58, 79) if unit == 'lb' else range(145, 201)
    out = [[] for _ in range(4)]
    for h in hs:
        out[band4(bmi(w, h if unit == 'lb' else h / 2.54, unit))].append(h)
    def span(x):
        if not x: return '—'
        if unit == 'lb': return ftin(x[0]) if len(x) == 1 else f'{ftin(x[0])}–{ftin(x[-1])}'
        return f'{x[0]} cm' if len(x) == 1 else f'{x[0]}–{x[-1]} cm'
    return [span(x) for x in out]

def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# The printable table's values (the image is drawn from bc_grid.csv by chart_bc.py).
rows = list(csv.reader(open(GRID)))
cols = [float(c.split()[1]) for c in rows[0][2:]]
ok(cols == [18.5] + list(range(19, 41)), f'grid columns {cols}')
ok(len(rows) == 22, f'{len(rows) - 1} grid rows')
for r in rows[1:]:
    m = re.match(r"(\d)'(\d{1,2})\"", r[0]); h = int(m.group(1)) * 12 + int(m.group(2))
    ok(r[1] == f'{h * 2.54:.1f}', f'grid cm {r[0]}')
    for b, v in zip(cols, r[2:]):
        want = min(w for w in range(40, 500) if bmi(w, h, 'lb') >= b)
        ok(v == str(want), f'grid {r[0]} BMI {b:g}: {v} vs {want}')

with sync_playwright() as p:
    br = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    html = pg.content()
    ok('{TODAY}' not in html, '{TODAY} placeholder left in the page')

    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [r.id, ...[...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim())])])""")
    ok(len(tables) == 5, f'{len(tables)} tables')
    def table(prefix): return [t for t in tables if t[0].startswith(prefix)][0][1]
    lbchart = table('BMI chart in pounds')
    ok(len(lbchart) == 21, f'{len(lbchart)} pound-chart rows')
    for row in lbchart:
        m = re.match(r"(\d)′(\d{1,2})″ \((\d+\.\d) cm\)", row[1]); ok(bool(m), f'height cell {row[1]!r}')
        h = int(m.group(1)) * 12 + int(m.group(2))
        ok(row[0] == f'h-{h // 12}-{h % 12}', f'row anchor {row[0]} for {row[1]}')
        ok(m.group(3) == f'{h * 2.54:.1f}', f'{row[1]}: cm label')
        for band in range(6):
            want = want_cell(h, band, 'lb', 'kg')
            ok(row[2 + band] == want, f'{row[1]} band {band}: {row[2 + band]!r} vs {want!r}')
    kgchart = table('BMI chart in kilograms')
    ok(len(kgchart) == 12, f'{len(kgchart)} kilogram-chart rows')
    for row, cm in zip(kgchart, range(145, 201, 5)):
        h_in = cm / 2.54
        ok(row[0] == f'h-{cm}cm', f'row anchor {row[0]} for {cm} cm')
        ok(row[1] == f'{cm} cm ({h_in // 12:.0f}′{h_in % 12:.1f}″)', f'{cm} cm label {row[1]!r}')
        for band in range(6):
            want = want_cell(h_in, band, 'kg', 'lb')
            ok(row[2 + band] == want, f'{cm} cm band {band}: {row[2 + band]!r} vs {want!r}')
    for prefix, unit, ws in (('Heights for each weight, 100 to 250 lb', 'lb', range(100, 251, 10)),
                             ('Heights for each weight, 40 to 130 kg', 'kg', range(40, 131, 10))):
        rev = table(prefix)
        ok(len(rev) == len(ws), f'{prefix}: {len(rev)} rows')
        for row, w in zip(rev, ws):
            ok(row[0] == f'w-{w}-{unit}', f'row anchor {row[0]} for {w} {unit}')
            ok(row[1].startswith(f'{w} {unit} ('), f'weight cell {row[1]!r}')
            ok(row[2:] == want_heights(w, unit), f'{w} {unit}: {row[2:]} vs {want_heights(w, unit)}')
    us = table('US adults by BMI category')
    names = [('underweight', 'Underweight BMI under 18.5'), ('healthy', 'Healthy weight BMI 18.5–24.9'),
             ('overweight', 'Overweight BMI 25–29.9'), ('class_1', 'Class 1 obesity BMI 30–34.9'),
             ('class_2', 'Class 2 obesity BMI 35–39.9'), ('class_3', 'Class 3 obesity BMI 40 or more')]
    for row, (k, name) in zip(us, names):
        ok(row[1:] == [name] + [f"{C[g][k]['pct']}%" for g in ('all', 'men', 'women')], f'US row {row} vs {k}')
    ok(us[6][1:] == ['Adults measured'] + [f"{C[g]['n']:,}" for g in ('all', 'men', 'women')], f'US n row {us[6]}')

    # Printable table image
    img = pg.evaluate("""() => { const i = document.querySelector('main figure img'); const a = i.closest('a');
        return [i.getAttribute('src'), i.getAttribute('alt'), +i.getAttribute('width'), +i.getAttribute('height'), a && a.getAttribute('href')]; }""")
    ok(img[0] == '/assets/images/charts/bmi-chart.png' and img[4] == img[0], f'chart image link {img}')
    ok(len(img[1]) > 60 and 'Printable BMI chart for adults' in img[1], f'chart alt {img[1]!r}')
    ok((img[2], img[3]) == (1640, 1854), f'chart size attributes {img}')
    pg.evaluate("document.querySelector('main figure img').scrollIntoView()"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelector('main figure img').naturalWidth") == 1640, 'chart image did not load')

    # Images in search: robots, OG/Twitter, JSON-LD, the preferred files themselves
    head = pg.evaluate("""() => ({robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content),
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content),
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content)})""")
    P = {r: f'{SITE}/assets/images/preferred/bmi-chart-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['robots'] == ['max-image-preview:large'], f"robots {head['robots']}")
    ok(head['og'] == [P['16x9']] and head['tw'] == [P['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter image {head}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/bmi-chart-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}: {res.status} {png_size(res.body())}')

    # Figure labels come from the same data
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => [s.getAttribute('aria-labelledby'),
        [...s.querySelectorAll('text')].map(e => e.textContent), s.querySelectorAll('circle').length,
        (s.querySelector('desc') || {}).textContent])""")
    ok([f[0] for f in figs] == ['fig-hero-t fig-hero-d', 'fig-ada-t fig-ada-d', 'fig-dots-t fig-dots-d'], f'figures {[f[0] for f in figs]}')
    hero = figs[0][1]
    ok([t for t in hero if re.fullmatch(r"\d′\d{1,2}″", t)] == [ftin(h) for h in range(58, 79, 4)], 'hero height labels')
    ok(any(f'185 lb, BMI {bmi(185, 69, "lb")} (overweight)' in t for t in hero), 'hero example subtitle')
    ada = [t for t in figs[1][1] if t.endswith('%')]
    ok(ada == [f"{ADA[g][k]['pct']:.1f}%" for g in ('all', 'men', 'women') for k in ('obesity_bmi_only', 'obesity_ada')], f'ADA figure labels {ada}')
    pts = S['dots']['points']
    nb = [0] * 5
    for h, w, _ in pts:
        b = bmi(w, h, 'lb'); nb[0 if b < 18.5 else 1 if b < 25 else 2 if b < 30 else 3 if b < 40 else 4] += 1
    ok(figs[2][2] == 600, f'{figs[2][2]} dots')
    ok(f'{nb[0]} dots fall in the underweight band, {nb[1]} in the healthy band, {nb[2]} in the overweight band, {nb[3]} in '
       f'obesity and {nb[4]} in class 3 obesity' in figs[2][3], f'dot counts {nb} vs description')

    # Contents chips land on their sections; FAQ opens with one tap; JSON-LD equals the visible answers
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(len(chips) == 9, f'{len(chips)} contents chips')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    qs = pg.query_selector_all('.faq-question')
    ok(len(qs) == 10, f'{len(qs)} FAQ questions')
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
    ok(art['image'] == [P['1x1'], P['4x3'], P['16x9']], f"Article image {art['image']}")
    mp = art.get('mainEntityOfPage', {})
    ok(mp.get('@type') == 'WebPage' and mp.get('url') == SITE + '/bmi-chart/' and mp.get('primaryImageOfPage', {}).get('url') == P['16x9'],
       f'primaryImageOfPage {mp}')
    crumbs = [x for x in ld if x['@type'] == 'BreadcrumbList'][0]['itemListElement']
    ok(crumbs[-1]['name'] == pg.inner_text('h1'), 'breadcrumb name is not the H1')
    ok(not errs, f'JS errors {errs}')

    # Figures and page width
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("() => [...document.querySelectorAll('.weight-chart')].map(t => { const f = t.closest('.table-responsive'); return [t.offsetWidth, f.clientWidth, getComputedStyle(f).overflowX]; })")
        ok(len(fits) == 4, f'{len(fits)} weight-chart tables')
        for fit in fits:
            ok(fit[2] == 'auto', f'chart table frame at {w}: {fit}')
            if w == 1280: ok(fit[0] <= fit[1], f'chart table scrolls on desktop: {fit}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom],
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
                        # band paths are curved: test the label box against the path's real fill, not its bounding box
                        if a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5:
                            fails.append(f'{w}px label box meets a shape box: {a[0]!r} / {s[0]}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
sys.exit(1 if fails else 0)
