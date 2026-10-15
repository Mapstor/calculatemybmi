#!/usr/bin/env python3
"""Homepage checks in Chromium (CMB-012). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then: python3 home_test_playwright.py http://localhost:8000 research/home-build/home_stats.json
  - the US rank box is hidden before Calculate and shows the right shares after it (all adults, men only, women only),
    imperial and metric, including both ends of the curve;
  - rendered SVG labels don't overlap and stay inside their figure, at 390 and 1280 px;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px;
  - every FAQ question opens with one tap."""
import sys, json, math
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
S = json.load(open(stats))
Q = {k: S[k]['p1_p99'] for k in ('adults', 'men', 'women')}
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def pct(q, b):
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
def rk(q, b): return pct(q, round(b - 0.1, 1)), 100 - pct(q, b)      # (share lower, share higher)
def n(x): return 99 if x > 99 else round(x)
def lab(q, b):
    lo, hi = rk(q, b)
    return f'lower than {n(hi)}%' if lo < 1 else f'higher than {n(lo)}%'

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

cases = [('imp', 5, 7, 160), ('imp', 5, 4, 95), ('imp', 5, 4, 80), ('imp', 6, 0, 400), ('imp', 5, 10, 180), ('imp', 5, 2, 230),
         ('met', 170, 70), ('met', 160, 120), ('met', 190, 55), ('met', 145, 84)]
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://localhost') else r.abort())
    pg.goto(base + '/', wait_until='load')
    ok(pg.eval_on_selector('#standard-rank', 'e => e.hidden'), 'rank box visible before Calculate')
    for c in cases:
        if c[0] == 'imp':
            pg.click('#panel-standard .unit-btn[data-unit="imperial"]')
            pg.fill('#standard-height-ft', str(c[1])); pg.fill('#standard-height-in', str(c[2])); pg.fill('#standard-weight-lbs', str(c[3]))
            bmi = r1(c[3] * 703 / (c[1] * 12 + c[2]) ** 2)
        else:
            pg.click('#panel-standard .unit-btn[data-unit="metric"]')
            pg.fill('#standard-height-cm', str(c[1])); pg.fill('#standard-weight-kg', str(c[2]))
            bmi = r1(c[2] / (c[1] / 100) ** 2)
        pg.click('#calc-standard-btn'); pg.wait_for_timeout(80)
        head = pg.inner_text('#standard-rank-value'); txt = pg.inner_text('#standard-rank-text')
        lo, hi = rk(Q['adults'], bmi)
        exp_head = lab(Q['adults'], bmi)[0].upper() + lab(Q['adults'], bmi)[1:] + ' of US adults'
        ok(head == exp_head, f'{c} BMI {bmi}: head {head!r}, expected {exp_head!r}')
        ok(f'{bmi:.1f}' in txt, f'{c}: BMI {bmi} missing from {txt!r}')
        ok(f"Compared with men only, it is {lab(Q['men'], bmi)}; with women only, {lab(Q['women'], bmi)}." in txt, f'{c}: sex split in {txt!r}')
        if 1 <= lo and 1 <= hi:
            ok(f'higher than about {n(lo)}% of US adults aged 20 and over and lower than about {n(hi)}%' in txt, f'{c}: shares in {txt!r}')
        ok(not pg.eval_on_selector('#standard-rank', 'e => e.hidden'), f'{c}: rank box still hidden')
        left = float(pg.eval_on_selector('#standard-rank-marker', 'e => parseFloat(e.style.left)'))
        ok(abs(left - min(99, max(1, lo))) < 0.01, f'{c}: marker at {left}, expected {lo:.2f}')
        print('OK ' if not fails else '.. ', c, 'BMI', bmi, '|', head, '|', txt[:100])
    ok(not errs, f'JS errors {errs}')
    # FAQ: one tap opens each answer
    pg.goto(base + '/', wait_until='load')
    qs = pg.query_selector_all('.faq-question')
    ok(len(qs) == 8, f'{len(qs)} FAQ questions')
    for i, q in enumerate(qs):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
    # Figures and page width
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(base + '/', wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), t = [...svg.querySelectorAll('text')].map(e => { const b = e.getBoundingClientRect(); return [e.textContent, b.left, b.top, b.right, b.bottom]; });
                return {box: [r.left, r.top, r.right, r.bottom], texts: t}; })""")
            ok(len(res) == 2, f'{len(res)} figures at {w}')
            for f in res:
                L, T, R, B = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L - 0.5 and a[3] <= R + 0.5 and a[2] >= T - 0.5 and a[4] <= B + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
    b.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)
