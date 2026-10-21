#!/usr/bin/env python3
"""Body fat chart page checks in Chromium (CMB-016). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/body-fat-chart-build/bfpc_test_playwright.py http://localhost:8000 research/body-fat-chart-build/bfpc_stats.json
  - the chart table: every cell equals the provisional cut-offs (low under a, healthy a to b - 0.1, ...) and the US median
    from bfpc_stats.json; bfpc_chart.csv (the values drawn in the printable image) equals the table row for row;
  - what every percentage means: every row from 5 to 40 (men) and 10 to 50 (women) carries the share with more body fat
    (tails written "more than 99%" / "under 1%") and the provisional range for 20-39 and 40-59; every row has its anchor;
  - the BMI tables, the age tables, the BMI figure's hover labels and the figure descriptions equal bfpc_stats.json;
  - single rounding (the 2026-10-21 fact-check's numbers, typed in here, not read from the stats): men 50-59 average
    28.3%; men 20-39 at 21% 77%, men 40-59 at 31% 28%, women 20-39 at 36% 61% and at 42% 26%; BMI-figure labels women
    BMI 39 median 44.7%, men BMI 18 middle half from 15.5%, men BMI 31 middle half to 32.1%; the tool 90% for a boy of 9 at
    20% and 82% for a woman of 25 at 30%;
  - the rank tool: eight cases (default, a man at 15.5%, a woman of 65, a girl of 12, a boy of 9 at 20%, a woman of 25 at
    30%, a man of 41 at 31.7%, an out-of-range reading) give the share interpolated here from the stats, the range on the
    provisional chart, the age group's percentiles as the age tables print them, and no overlapping labels;
  - images in search: one robots max-image-preview:large tag; og:image, twitter:image, the Article image list (1:1, 4:3,
    16:9) and primaryImageOfPage name this page's preferred images, which load at their sizes; the printable chart loads
    at 1360 px, has alt text and links to itself; the CSV download loads;
  - rendered SVG labels don't overlap, stay inside their figure and sit on no bar or point, at 390 and 1280 px;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px; the three-column tables fit a 320 px screen;
  - every contents chip lands on its section; every FAQ question opens with one tap; the FAQ JSON-LD equals the answers;
  - no {TODAY} placeholder is left in the page; no JavaScript error."""
import sys, os, json, re, csv, struct
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
S = json.load(open(stats))
BA, LK, GAL, BM, TOOL = S['by_age'], S['lookup'], S['gallagher']['cuts'], S['bmi'], S['tool']
CSV_CHART = os.path.join(os.path.dirname(os.path.abspath(stats)), 'bfpc_chart.csv')
URL = base + '/body-fat-percentage-chart/'
SITE = 'https://calculatemybmi.net'
SEXN = {'f': 'women', 'm': 'men'}

def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def share_txt(v): return 'more than 99%' if v >= 99.5 else 'under 1%' if v <= 0.5 else f'{int(v + 0.5)}%'      # halves up, as Math.round
def cat(k, g, p):
    a, b, c = GAL[k][g]
    return 'low' if p < a else 'healthy' if p < b else 'high' if p < c else 'very high'
def ranges(k, g):
    a, b, c = GAL[k][g]
    return [f'under {a}%', f'{a}–{b - 0.1:.1f}%', f'{b}–{c - 0.1:.1f}%', f'{c}% or more']
def more_at(arr, v):
    i, f = int(v // 1) - TOOL['percents'][0], v - int(v // 1)
    if i < 0: return arr[0]
    if i >= len(arr) - 1: return arr[-1]
    return arr[i] + (arr[i + 1] - arr[i]) * f

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# The values drawn in the printable chart.
chart_csv = list(csv.reader(open(CSV_CHART, encoding='utf-8')))
ok(chart_csv[0] == ['sex', 'age', 'low', 'healthy', 'high', 'very_high', 'us_median'], f'chart csv header {chart_csv[0]}')
WANT_CHART = []
for k in ('f', 'm'):
    for g in ('20-39', '40-59', '60-79'):
        med = f'{BA[k][g]["p50"]:.1f}%' if g in BA[k] else 'not scanned'
        WANT_CHART.append([SEXN[k].capitalize(), g.replace('-', '–')] + ranges(k, g) + [med])
ok(chart_csv[1:] == WANT_CHART, 'bfpc_chart.csv differs from the provisional cut-offs and the US medians')

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
    ok(len(tables) == 7, f'{len(tables)} tables before the tool runs')
    def table(prefix):
        hit = [t for t in tables if t[0].startswith(prefix)]
        ok(len(hit) == 1, f'table {prefix!r}: {len(hit)}')
        return hit[0][1] if hit else []
    chart = table('Provisional ranges by sex and age')
    ok([r[1:] for r in chart] == [[f'{w[0]} {w[1]}'] + w[2:] for w in WANT_CHART], f'chart table {chart}')
    ok([r[0] for r in chart] == [f'{SEXN[k]}-{g}' for k in ('f', 'm') for g in ('20-39', '40-59', '60-79')], 'chart row anchors')
    for k, lo, hi in (('m', 5, 40), ('f', 10, 50)):
        rows = table(f'What each body fat percentage means for US {SEXN[k]}')
        ok(len(rows) == hi - lo + 1, f'{k}: {len(rows)} rows')
        for row, pc in zip(rows, range(lo, hi + 1)):
            ok(row[0] == f'{SEXN[k]}-{pc}' and row[1] == f'{pc}%', f'{k} row {row[:2]}')
            want = [f"{share_txt(LK[k][g][str(pc)]['more'])} {cat(k, g, pc)}" for g in ('20-39', '40-59')]
            ok(row[2:] == want, f'{k} {pc}%: {row[2:]} vs {want}')
    bc = table('Body fat in each BMI category')
    for row, c in zip(bc, ('under', 'healthy', 'over', 'obese')):
        want = [f"{BM['by_cat'][k][c]['p50']:.1f}% {BM['by_cat'][k][c]['p25']:.1f}–{BM['by_cat'][k][c]['p75']:.1f}%" for k in ('f', 'm')]
        ok(row[2:] == want, f'BMI category {c}: {row[2:]} vs {want}')
    at = table('Body fat at a BMI of 25')
    ok([r[1:] for r in at] == [[f'{SEXN[k].capitalize()} {g.replace("-", "–")}', f"{BM['at_lines'][k]['25'][g]['mean']:.1f}%",
                                f'{GAL[k][g][1]}%'] for k in ('f', 'm') for g in ('20-39', '40-59')], f'BMI 25 table {at}')
    for k, kid in (('f', 'girls'), ('m', 'boys')):
        rows = table(f'US {SEXN[k]} and {kid} by age')
        groups = ('8-11', '12-15', '16-19', '20-29', '30-39', '40-49', '50-59')
        ok([r[1] for r in rows] == [g.replace('-', '–') for g in groups], f'{k} age rows {[r[1] for r in rows]}')
        for row, g in zip(rows, groups):
            a = BA[k][g]
            want = [f'{a[q]:.1f}%' for q in ('p10', 'p25', 'p50', 'p75', 'p90')] + [f"{a['mean4']:.1f}%", f"{a['n']:,}"]
            ok(row[2:] == want, f'{k} {g}: {row[2:]} vs {want}')
        if k == 'm':
            ok(rows[-1][7] == '28.3%', f'men 50-59 average {rows[-1][7]!r} (fact-check: 28.347, so 28.3%)')
    # The fact-check's four cells (unrounded 77.48, 28.48, 61.475, 26.48), typed in here rather than read from the stats.
    every = {k: {r[0]: r[2:] for r in table(f'What each body fat percentage means for US {SEXN[k]}')} for k in ('m', 'f')}
    for k, pc, col, want in (('m', 21, 0, '77%'), ('m', 31, 1, '28%'), ('f', 36, 0, '61%'), ('f', 42, 0, '26%')):
        got = every[k].get(f'{SEXN[k]}-{pc}', ['', ''])[col].split(' ')[0]
        ok(got == want, f'fact-check cell {k} {pc}% col {col}: {got!r} vs {want!r}')
    main_text = pg.evaluate("() => document.querySelector('main').textContent.replace(/\\s+/g, ' ')")   # closed FAQ answers too
    ok('(25.4% to 28.3%)' in main_text and 'from 25.4% to 28.3% for men' in main_text, 'men 20s-to-50s text not 25.4% to 28.3%')
    ok('28.4%' not in main_text, 'a 28.4% is still printed')
    # BMI figure hover labels: every one equals the stats; three the fact-check found rounded twice are typed in.
    tips = pg.evaluate("() => [...document.querySelectorAll('#bmi figure svg circle title')].map(t => t.textContent)")
    want_tips = []
    for k in ('f', 'm'):
        for b, v in sorted(((int(b), v) for b, v in BM['by_bin'][k].items() if 18 <= int(b) <= 39 and v.get('n', 0) >= 50)):
            want_tips.append(f"{SEXN[k].capitalize()}, BMI {b} to {b}.9: median {v['p50']:.1f}%, middle half "
                             f"{v['p25']:.1f}–{v['p75']:.1f}% ({v['n']:,} scanned)")
    ok(tips == want_tips, f'BMI figure hover labels differ from the stats ({len(tips)} vs {len(want_tips)})')
    for frag in ('Women, BMI 39 to 39.9: median 44.7%', 'Men, BMI 18 to 18.9: median', 'Men, BMI 31 to 31.9: median'):
        ok(any(t.startswith(frag) for t in tips), f'hover label {frag!r} missing')
    ok(any(t.startswith('Men, BMI 18 to 18.9:') and 'middle half 15.5–' in t for t in tips), 'men BMI 18 middle half not from 15.5%')
    ok(any(t.startswith('Men, BMI 31 to 31.9:') and '–32.1%' in t for t in tips), 'men BMI 31 middle half not to 32.1%')

    # Images in search: robots, OG/Twitter, JSON-LD, the preferred files, the printable chart, the CSV
    head = pg.evaluate("""() => ({robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content),
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content),
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content)})""")
    P = {r: f'{SITE}/assets/images/preferred/body-fat-percentage-chart-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['robots'] == ['max-image-preview:large'], f"robots {head['robots']}")
    ok(head['og'] == [P['16x9']] and head['tw'] == [P['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter image {head}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/body-fat-percentage-chart-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}: {res.status}')
    img = pg.evaluate("""() => { const i = document.querySelector('#printable figure img'); const a = i.closest('a');
        return [i.getAttribute('src'), i.getAttribute('alt'), +i.getAttribute('width'), +i.getAttribute('height'), a && a.getAttribute('href')]; }""")
    ok(img[0] == '/assets/images/charts/body-fat-percentage-chart.png' and img[4] == img[0], f'chart image link {img}')
    ok(len(img[1]) > 60 and img[1].startswith('Body fat percentage chart for women and men by age'), f'chart alt {img[1]!r}')
    ok((img[2], img[3]) == (1360, 902), f'chart size attributes {img}')
    pg.evaluate("document.querySelector('#printable figure img').scrollIntoView()"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelector('#printable figure img').naturalWidth") == 1360, 'chart image did not load')
    res = pg.request.get(f'{base}/body-fat-percentage-chart/body-fat-percentiles-nhanes-2011-2018.csv')
    ok(res.status == 200 and res.text().count('\n') >= 20, f'CSV download {res.status}')

    # Figure descriptions come from the same data
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(s => [s.getAttribute('aria-labelledby'),
        (s.querySelector('desc') || {}).textContent, [...s.querySelectorAll('text')].map(e => e.textContent)])""")
    ok([f[0] for f in figs] == ['hero-t hero-d', 'bmi-t bmi-d', 'age-t age-d'], f'figures {[f[0] for f in figs]}')
    for k in ('f', 'm'):
        for g in ('20-39', '40-59', '60-79'):
            a, b, c = GAL[k][g]
            ok(f'{SEXN[k].capitalize()} {g.replace("-", " to ")}: low under {a}%, healthy {a}–{b - 0.1:.1f}%' in figs[0][1], f'hero desc {k} {g}')
    hero_nums = [t for t in figs[0][2] if t.isdigit()]
    ok(hero_nums == [str(v) for k in ('f', 'm') for g in ('20-39', '40-59', '60-79') for v in GAL[k][g]], f'hero cut-off labels {hero_nums}')
    ok(f"median {BA['m']['8-11']['p50']:.1f}% at 8 to 11, {BA['m']['16-19']['p50']:.1f}% at 16 to 19" in figs[2][1], 'age figure description')

    # The rank tool
    def run(sex, v, a):
        pg.click(f'#bfr .unit-btn[data-sex="{sex}"]')
        pg.fill('#bfr-v', str(v)); pg.fill('#bfr-a', str(a)); pg.click('#bfr-go'); pg.wait_for_timeout(80)
        return pg.evaluate("""() => { const o = document.getElementById('bfr-out');
            const t = [...o.querySelectorAll('svg text')].map(e => { const b = e.getBoundingClientRect(); return [e.textContent, b.left, b.top, b.right, b.bottom]; });
            const s = o.querySelector('svg'); const r = s ? s.getBoundingClientRect() : null;
            return {vis: o.classList.contains('visible'), big: (o.querySelector('.bmi-value') || {}).textContent || '',
                    line: (o.querySelector('.bmi-category') || {}).textContent || '', text: o.innerText,
                    cells: [...o.querySelectorAll('.data-table td')].map(c => c.textContent),
                    pressed: [...document.querySelectorAll('#bfr .unit-btn')].map(b => b.getAttribute('aria-pressed')),
                    labels: t, box: r ? [r.left, r.top, r.right, r.bottom] : null}; }""")
    cases = [('f', 30, 35, '30-39', '20-39'), ('m', 15.5, 25, '20-29', '20-39'), ('f', 30, 65, None, '60-79'),
             ('f', 33, 12, '12-15', None), ('m', 20, 9, '8-11', None), ('f', 30, 25, '20-29', '20-39'),
             ('m', 31.7, 41, '40-49', '40-59')]
    FC_TOOL = {('m', 20, 9): '90%', ('f', 30, 25): '82%'}          # fact-check: unrounded 90.47 and 82.48
    for sex, v, a, g, gg in cases:
        o = run(sex, v, a)
        ok(o['vis'], f'tool {sex} {v} {a}: results not shown')
        ok(o['pressed'] == (['true', 'false'] if sex == 'f' else ['false', 'true']), f'tool {sex}: aria-pressed {o["pressed"]}')
        if g:
            want = share_txt(more_at(TOOL['more'][sex][g], v))
            who = (SEXN[sex] if a >= 20 else {'f': 'girls', 'm': 'boys'}[sex])
            ok(o['big'] == want, f'tool {sex} {v} {a}: {o["big"]!r} vs {want!r}')
            if (sex, v, a) in FC_TOOL:
                ok(o['big'] == FC_TOOL[(sex, v, a)], f'tool {sex} {v} {a}: {o["big"]!r}, fact-check {FC_TOOL[(sex, v, a)]!r}')
            ok(o['line'] == f'of US {who} aged {g.replace("-", "–")} measured more body fat than {v}%', f'tool line {o["line"]!r}')
            ok(f"{BA[sex][g]['p50']:.1f}" in o['text'], f'tool {sex} {g}: median missing')
            want_cells = [f"{BA[sex][g][q]:.1f}" for q in ('p10', 'p25', 'p50', 'p75', 'p90')]
            ok(o['cells'] == want_cells, f'tool {sex} {g} percentiles {o["cells"]} vs the age table {want_cells}')
        else:
            ok(o['big'] == f'{v}%' and o['line'] == f'{cat(sex, gg, v).capitalize()} on the provisional range for women 60–79', f'tool 65: {o["big"]} {o["line"]!r}')
        if gg:
            ok(f'{v}% is {cat(sex, gg, v)} on the provisional ranges' in o['text'], f'tool {sex} {v} {a}: range line')
        else:
            ok('The provisional adult ranges start at age 20' in o['text'], f'tool {sex} {a}: under-20 note')
        L, T, R, B = o['box']
        for i, x in enumerate(o['labels']):
            ok(x[1] >= L - 0.5 and x[3] <= R + 0.5, f'tool label outside its figure: {x[0]!r}')
            for y in o['labels'][i + 1:]:
                if x[1] < y[3] - 0.5 and y[1] < x[3] - 0.5 and x[2] < y[4] - 0.5 and y[2] < x[4] - 0.5:
                    fails.append(f'tool labels overlap: {x[0]!r} / {y[0]!r}')
    o = run('f', 80, 35)
    ok('Enter a body fat percentage from 3 to 65 and an age from 8 to 79.' in o['text'], 'tool: out-of-range reading not caught')

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
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['Article', 'Dataset', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    G = {x['@type']: x for x in ld[0]['@graph']}
    vis = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([[q['name'], q['acceptedAnswer']['text']] for q in G['FAQPage']['mainEntity']] == vis, 'FAQ JSON-LD differs from the visible answers')
    art = G['Article']
    ok(re.fullmatch(r'\d{4}-\d{2}-\d{2}', art['dateModified']) is not None, f"dateModified {art['dateModified']!r}")
    ok(art['headline'] == pg.inner_text('h1'), 'Article headline is not the H1')
    ok(art['image'] == [P['1x1'], P['4x3'], P['16x9']], f"Article image {art['image']}")
    ok(art['author'].get('name') == 'Marko Visic' and art['publisher'].get('name') == 'CalculateMyBMI', 'author/publisher named')
    mp = art.get('mainEntityOfPage', {})
    ok(mp.get('@type') == 'WebPage' and mp.get('url') == SITE + '/body-fat-percentage-chart/' and mp.get('primaryImageOfPage', {}).get('url') == P['16x9'],
       f'primaryImageOfPage {mp}')
    ok(G['Dataset']['distribution'][0]['contentUrl'].endswith('/body-fat-percentiles-nhanes-2011-2018.csv'), 'Dataset download')
    ok(G['BreadcrumbList']['itemListElement'][-1]['name'] == pg.inner_text('h1'), 'breadcrumb name is not the H1')
    ok(not errs, f'JS errors {errs}')

    # Figures and page width
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("() => [...document.querySelectorAll('.weight-chart')].map(t => { const f = t.closest('.table-responsive'); return [t.className, t.offsetWidth, f.clientWidth, getComputedStyle(f).overflowX]; })")
        ok(len(fits) == 3, f'{len(fits)} weight-chart tables')
        for fit in fits:
            ok(fit[3] == 'auto', f'chart table frame at {w}: {fit}')
            if 'weight-chart--fit' in fit[0] or w == 1280: ok(fit[1] <= fit[2], f'table scrolls at {w}: {fit}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom],
                        texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                        shapes: [...svg.querySelectorAll('rect, path, circle')].filter(e => e.getAttribute('fill') !== 'none').map(e => [e.tagName, ...bx(e)])}; })""")
            ok(len(res) == 3, f'{len(res)} figures at {w}')
            for f in res:
                L, T, R, B = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L - 0.5 and a[3] <= R + 0.5 and a[2] >= T - 0.5 and a[4] <= B + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s in f['shapes']:
                        if a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5:
                            fails.append(f'{w}px label box meets a shape: {a[0]!r} / {s[0]}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
sys.exit(1 if fails else 0)
