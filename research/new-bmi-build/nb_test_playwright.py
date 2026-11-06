#!/usr/bin/env python3
"""/new-bmi-calculator/ checks in Chromium (CMB-023). Needs Python Playwright + Chromium.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/new-bmi-build/nb_test_playwright.py http://localhost:8000 research/new-bmi-build/nb_stats.json
  - the calculator: every side-by-side row and both worked examples typed into the real calculator, and the page's cells
    equal what it prints (and the formula, written again here, and nb_stats.json); the anchors chat read off the live
    calculator on 2026-11-05 typed in as literals; three metric entries worked out from the formula;
  - the by-height table and the figure's points (the curve, the two marked heights, the crossing at 1.69 m, the axis
    labels) against the formula; the figure's colours stay in the site palette;
  - labels on /age-bmi-calculator/, /kids-bmi-calculator/, /ideal-weight/, /lean-body-mass/ and this page: every label
    names the expected id and clicking it focuses its field, in US units and in metric;
  - Calculate ends above the fold at 360 and 390 px; the page is never wider than the screen at 320, 360, 390 and 1280,
    before and after Calculate; every table fits its frame; rendered SVG labels stay inside the figure and off each
    other, every shape and line and the plotted curve;
  - 7 FAQ in order, the JSON-LD equal to the visible answers, one tap opens an answer and one closes it;
  - sections sit directly in main .container, no <article>, no page-level style, no inline style in <main> outside the
    figure; the head's scripts other than JSON-LD, the header, and the scripts after </main> equal origin/main's;
  - head: title and H1 kept, description, OG/Twitter text and the preferred images, the JSON-LD graph; old OG image gone;
  - internal links answer 200, anchors exist, outside links are registry URLs; nothing from the prompt's NEVER WRITE list.
Every check runs; nothing is skipped. Exit 1 on any failure."""
import sys, os, json, math, re, csv, struct, subprocess
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1].rstrip('/'), sys.argv[2]
BUILD = os.path.dirname(os.path.abspath(stats))
ROOT = os.path.abspath(os.path.join(BUILD, '..', '..'))
S = json.load(open(stats, encoding='utf-8'))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()}
URL = base + '/new-bmi-calculator/'
SITE = 'https://calculatemybmi.net'
M = '−'
FT, IN = '′', '″'

fails, checks, skipped = [], 0, 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

def norm(t): return re.sub(r'\s+', ' ', (t or '').replace(' ', ' ')).strip()
def half_up(x, places): return Decimal(repr(x)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None

# ---- the formula, written again here (calculator.js: round once to 0.1, halves up; difference of the rounded values)
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def f1(x): return f'{r1(x):.1f}'
def sg(d): return ('+' if d > 1e-9 else M if d < -1e-9 else '') + f'{abs(d):.1f}'
def edge(x): v = x * 10; return abs((v - math.floor(v)) - 0.5) < 1e-6
def cat(b):
    b = r1(b)
    return ('Severe thinness' if b < 16 else 'Moderate thinness' if b < 17 else 'Underweight' if b < 18.5 else 'Healthy weight' if b < 25
            else 'Overweight' if b < 30 else 'Class 1 obesity' if b < 35 else 'Class 2 obesity' if b < 40 else 'Class 3 obesity')
def us(inches, lb):
    return lb * 703 / inches ** 2, 1.3 * (lb / 2.20462) / (inches * 0.0254) ** 2.5
def metric(cm, kg):
    return kg / (cm / 100) ** 2, 1.3 * kg / (cm / 100) ** 2.5
def expect(t, n):
    return {'traditional': f1(t), 'new': f1(n), 'difference': sg(r1(n) - r1(t)), 'tc': cat(t), 'nc': cat(n)}
def hlab(inches): ft, i = divmod(inches, 12); return f'{ft}{FT}{i}{IN}'
def cm1(inches): return f'{(Decimal(inches) * Decimal("2.54")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)} cm'
def kg1(lb): return f'{half_up(lb / 2.20462, 1)} kg'
def curve(m): return 1.3 * 70 / m ** 2.5 - 70 / m ** 2

GRID = [(h, lb) for h in (60, 64, 68, 72, 76) for lb in (120, 150, 180, 210)]
SBS = {(r['inches'], r['lb']): r for r in S['side_by_side']}
ok(sorted(SBS) == sorted(GRID), 'nb_stats.json side-by-side grid')
# The anchors chat read off the live calculator on 2026-11-05, typed in here.
ANCHORS = [((5, 2, 150), '27.4', '28.4', '+1.0', None),
           ((6, 2, 150), '19.3', '18.3', M + '1.0', ('Healthy weight', 'Underweight')),
           ((5, 0, 150), '29.3', '30.8', '+1.5', ('Overweight', 'Class 1 obesity')),
           ((6, 4, 210), '25.6', '23.9', M + '1.7', ('Overweight', 'Healthy weight')),
           ((6, 4, 150), '18.3', '17.1', M + '1.2', 'same')]
METRIC = [(152, 68), (173, 73), (190, 95)]
for cm, kg in METRIC:
    t, n = metric(cm, kg)
    ok(not edge(t) and not edge(n), f'metric case {cm} cm {kg} kg sits on a rounding edge')

NEVER = [r'more accurate', r'\bcorrect', r'\bbias', r'remov\w* (?:a|the) bias', r'nobody has tested', r'\btested\b', r'\badopt',
         r'mathematically sound', r'clinically validated', r'thousands of studies', r'major health organi[sz]ations',
         r'Royal Society', r'International Journal of Obesity', r'see.s analysis', r'cubed', r'\bcube\b', r'compromise',
         r'slimmer', r'\bNormal\b', r'\bobese\b']
FAQ_Q = ['What is the new BMI formula?', 'Who created the new BMI?', 'Why is the new BMI different from traditional BMI?',
         'Is the new BMI more accurate than traditional BMI?', 'Should I use new BMI or traditional BMI?',
         'Does the new BMI change my category?', 'Which BMI do CDC and WHO use?']
LABELS = {'/age-bmi-calculator/': ['age-height-ft', 'age-height-in', 'age-height-cm', 'age-weight-lbs', 'age-weight-kg', 'age-years'],
          '/kids-bmi-calculator/': ['kids-height-ft', 'kids-height-in', 'kids-height-cm', 'kids-weight-lbs', 'kids-weight-kg',
                                    'kids-age-years', 'kids-age-months', 'kids-sex'],
          '/ideal-weight/': ['ideal-height-ft', 'ideal-height-in', 'ideal-height-cm', 'ideal-sex', 'ideal-frame'],
          '/lean-body-mass/': ['lbm-height-ft', 'lbm-height-in', 'lbm-height-cm', 'lbm-weight-lbs', 'lbm-weight-kg', 'lbm-sex'],
          '/new-bmi-calculator/': ['newbmi-height-ft', 'newbmi-height-in', 'newbmi-weight-lbs', 'newbmi-height-cm', 'newbmi-weight-kg']}
PI = {r: f'{SITE}/assets/images/preferred/new-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
TITLE = 'New BMI Calculator (Trefethen) - Updated Body Mass Index Formula'
H1 = 'New BMI Calculator (Trefethen Formula)'
DESC = ('Compare New BMI, Trefethen’s 2013 formula, with traditional BMI for your height and weight. '
        'See both numbers, the gap at your height and which one to use.')


def git_main():
    return subprocess.run(['git', '-C', ROOT, 'show', 'origin/main:new-bmi-calculator/index.html'],
                          capture_output=True, text=True, check=True).stdout


def head_scripts(src):
    head = src[:src.index('</head>')]
    return [s for s in re.findall(r'(?s)<script\b[^>]*>.*?</script>', head) if 'application/ld+json' not in s]


def calc(pg, ft=None, inch=None, lb=None, cm=None, kg=None):
    """Types an entry into the page's calculator, presses Calculate and reads what it prints."""
    unit = 'metric' if cm is not None else 'imperial'
    pg.click(f'#panel-newbmi .unit-btn[data-unit="{unit}"]')
    if unit == 'imperial':
        pg.fill('#newbmi-height-ft', str(ft)); pg.fill('#newbmi-height-in', str(inch)); pg.fill('#newbmi-weight-lbs', str(lb))
    else:
        pg.fill('#newbmi-height-cm', str(cm)); pg.fill('#newbmi-weight-kg', str(kg))
    pg.click('#calc-newbmi-btn'); pg.wait_for_timeout(40)
    got = {k: norm(pg.inner_text(s)) for k, s in (('new', '#newbmi-bmi-value'), ('nc', '#newbmi-bmi-category'),
           ('traditional', '#newbmi-traditional-value'), ('difference', '#newbmi-diff'), ('change', '#newbmi-category-change'),
           ('compare', '#newbmi-bmi-value-compare'))}
    ch = got['change']
    if ch == 'Same category with both formulas':
        got['tc'] = got['nc']
    else:
        mm = re.fullmatch(r'(.+) with the traditional formula, (.+) with the new one', ch)
        got['tc'] = mm.group(1) if mm else '?'
        ok(mm and mm.group(2) == got['nc'], f'category sentence {ch!r} vs card {got["nc"]!r}')
    ok(got['compare'] == got['new'], 'the New BMI tile differs from the result card')
    return got


with sync_playwright() as p:
    br = p.chromium.launch(args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 1280, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())     # no ads or analytics
    resp = pg.goto(URL, wait_until='load')
    ok(resp.status == 200, f'page status {resp.status}')
    src = pg.request.get(URL).text()
    orig = git_main()

    # ---- the page as served: kept parts, structure, no inline style, no <article>
    ok(head_scripts(src) == head_scripts(orig) and len(head_scripts(orig)) == 3, 'head scripts other than JSON-LD differ from origin/main')
    hdr = lambda s: re.search(r'(?s)<header class="header">.*?</header>', s).group(0)
    ok(hdr(src) == hdr(orig), 'the header differs from origin/main')
    ok(src[src.index('</main>'):] == orig[orig.index('</main>'):], 'the scripts and footer after </main> differ from origin/main')
    ok(f'<title>{TITLE}</title>' in src and pg.inner_text('h1') == H1 and src.count('<h1') == 1, 'title / H1 kept')
    mains = src[src.index('<main'):src.index('</main>')]
    ok('<style' not in src and '<article' not in src and pg.evaluate("document.querySelectorAll('article').length") == 0,
       'page-level style or <article>')
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>', '', mains), 'inline style in <main> outside figures')
    ok(mains.startswith('<main class="reading"><div class="container">'), 'reading column')
    body_text = pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, #newbmi-results').forEach(e => e.remove()); return m.textContent; }""")
    ok('—' not in body_text, 'em dash in the body (the result placeholders aside)')
    kids = pg.evaluate("""() => [...document.querySelector('main > .container').children].map(e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + '.' + [...e.classList].join('.'))""")
    ok(kids == ['div.page-head', 'div.calculator-card', 'div.key-takeaways', 'div.disclaimer-box', 'nav.toc-inline',
                'section#formulas.content-section.flow', 'section#by-height.content-section.flow', 'section#side-by-side.content-section.flow',
                'section#examples.content-section.flow', 'section#why.content-section.flow', 'section#which.content-section.flow',
                'section#faq.content-section', 'section#sources.content-section.flow', 'section.content-section'], f'blocks in main .container: {kids}')
    ok(pg.evaluate("[...document.querySelectorAll('main section')].every(s => s.parentElement.matches('main > .container'))"),
       'a section is not a direct child of main .container')
    words = pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, script, style, #newbmi-results').forEach(e => e.remove()); return m.textContent.split(/\\s+/).filter(Boolean).length; }""")
    ok(1500 <= words <= 2200, f'{words} words in main')
    ids = ['newbmi-results', 'newbmi-result-card', 'newbmi-bmi-value', 'newbmi-bmi-category', 'newbmi-bmi-range', 'newbmi-scale-marker',
           'newbmi-bmi-value-compare', 'newbmi-traditional-value', 'newbmi-diff', 'newbmi-category-change', 'newbmi-healthy-min',
           'newbmi-healthy-max', 'newbmi-weight-diff', 'panel-newbmi', 'calc-newbmi-btn']
    ok(all(f'id="{i}"' in mains for i in ids), 'a kept calculator id is missing')
    start = pg.evaluate("['newbmi-height-ft', 'newbmi-height-in', 'newbmi-weight-lbs', 'newbmi-height-cm', 'newbmi-weight-kg'].map(i => document.getElementById(i).value)")
    ok(start == ['5', '8', '160', '173', '73'], f'starting values {start}')

    # ---- head and JSON-LD
    head = pg.evaluate("""() => ({desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content), canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content), ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        ogt: document.querySelector('meta[property="og:title"]').content, twt: document.querySelector('meta[name="twitter:title"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content),
        ogd: document.querySelector('meta[property="og:description"]').content, twd: document.querySelector('meta[name="twitter:description"]').content})""")
    ok(head['desc'] == DESC and len(DESC) <= 160, f'description {head["desc"]!r}')
    ok(head['ogd'] == head['twd'] == DESC and head['ogt'] == head['twt'] == H1, f'OG / Twitter text {head}')
    ok(head['robots'] == ['max-image-preview:large'] and head['canon'] == SITE + '/new-bmi-calculator/', 'robots / canonical')
    ok(head['og'] == [PI['16x9']] and head['tw'] == [PI['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'OG / Twitter image {head}')
    ok(head['ogalt'].startswith('Chart: New BMI minus traditional BMI by height') and '"' not in head['ogalt'], 'og:image:alt')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/new-bmi-calculator-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/assets/images/og/new-bmi-height-delta.png').status == 404, 'old OG image still served')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['WebPage', 'WebApplication', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    GR = {x['@type']: x for x in ld[0]['@graph']}
    ok(GR['WebPage']['primaryImageOfPage']['url'] == PI['16x9'] and GR['WebPage']['name'] == TITLE, 'WebPage')
    ok(GR['WebApplication']['image'] == [PI['1x1'], PI['4x3'], PI['16x9']] and GR['WebApplication']['author']['name'] == 'Marko Visic'
       and GR['WebApplication']['name'] == H1, 'WebApplication image list / author')
    ok([i['name'] for i in GR['BreadcrumbList']['itemListElement']] == ['Home', 'Calculators', 'New BMI Calculator (Trefethen)'], 'breadcrumb')

    # ---- the fixed text: intro, takeaways, disclaimer (the men page's, verbatim)
    ok(norm(pg.inner_text('.intro-text')) == 'See your BMI with Nick Trefethen’s 2013 formula next to the traditional one.', 'intro text')
    ok(norm(pg.inner_text('.intro-note')) == 'A mathematician’s proposal, not a medical standard: CDC still calculates BMI with height squared. Method and sources'
       and pg.get_attribute('.intro-note a', 'href') == '#sources', 'intro note')
    kt = pg.evaluate("() => [document.querySelector('.key-takeaways .answer').textContent, ...[...document.querySelectorAll('.key-takeaways li')].map(l => l.textContent)]")
    ok([norm(x) for x in kt] == [
        'New BMI is Nick Trefethen’s 2013 alternative to the traditional formula: 1.3 × kg ÷ m2.5, or 5734 × lb ÷ in2.5. It matches traditional BMI at about 5′6.5″ (1.69 m), reads higher if you are shorter and lower if you are taller.',
        'The gap depends on height alone: New BMI is 5.3% higher than traditional BMI at 5′0″ and 3.9% lower at 6′0″, whatever you weigh.',
        'A traditional BMI of 25.0 becomes 26.3 at 5′0″ and 24.0 at 6′0″.',
        'Trefethen says his formula is “not based on epidemiological studies” and may not be an improvement.',
        'CDC’s formula uses height squared and its cut-offs are set on that number, so use traditional BMI for anything medical.'], f'key takeaways {kt}')
    men = pg.request.get(base + '/men-bmi-calculator/').text()
    disc = lambda s: re.search(r'(?s)<div class="disclaimer-box">.*?</div>', s).group(0)
    ok(disc(src) == disc(men), 'disclaimer is not the men page wording')

    # ---- the tables on the page
    T = pg.evaluate("""() => ({
        byhHead: [...document.querySelectorAll('#by-height table thead th')].map(c => c.textContent),
        byh: [...document.querySelectorAll('#by-height table tbody tr')].map(r => [r.cells[0].firstChild.textContent, r.cells[0].querySelector('.th-sub').textContent, r.cells[1].textContent, r.cells[2].textContent]),
        sbs: [...document.querySelectorAll('#side-by-side table tbody')].map(b => ({head: [b.rows[0].cells[0].textContent, b.rows[0].cells[0].getAttribute('scope'), b.rows[0].cells[0].getAttribute('colspan')],
             rows: [...b.rows].slice(1).map(r => [r.cells[0].firstChild.textContent, r.cells[0].querySelector('.th-sub').textContent, r.cells[1].textContent, r.cells[2].textContent, r.cells[3].textContent])})),
        sbsHead: [...document.querySelectorAll('#side-by-side table thead th')].map(c => c.textContent),
        note: document.querySelector('#side-by-side .source-note').textContent,
        formulas: [...document.querySelectorAll('#formulas table tr')].map(r => [...r.cells].map(c => c.textContent)),
        ex: [...document.querySelectorAll('#examples h3')].map(h => [h.textContent, ...[...h.nextElementSibling.children].map(c => c.textContent)])})""")
    ok([[norm(c) for c in r] for r in T['formulas']] == [['Formula', 'US units', 'Metric'], ['Traditional BMI', 'lb ÷ in² × 703', 'kg ÷ m²'],
                                                        ['New BMI', '5734 × lb ÷ in2.5', '1.3 × kg ÷ m2.5']], f'formulas table {T["formulas"]}')
    ok([norm(c) for c in T['sbsHead']] == ['Weight', 'Traditional', 'New BMI', 'Difference'], 'side-by-side head')
    page_rows = {}
    ok(len(T['sbs']) == 5, f'{len(T["sbs"])} height groups')
    for g, h in zip(T['sbs'], (60, 64, 68, 72, 76)):
        ok([norm(g['head'][0]), g['head'][1], g['head'][2]] == [f'{hlab(h)} ({cm1(h)})', 'rowgroup', '4'], f'group head {g["head"]}')
        ok(len(g['rows']) == 4, f'{hlab(h)}: {len(g["rows"])} rows')
        for row, lb in zip(g['rows'], (120, 150, 180, 210)):
            lab, kg, t, n, d = [norm(c) for c in row]
            mm = re.fullmatch(r'(\d+) lb(†?)', lab)
            ok(mm and int(mm.group(1)) == lb and kg == kg1(lb), f'{hlab(h)} row {lab!r} {kg!r}')
            page_rows[(h, lb)] = {'traditional': t, 'new': n, 'difference': d, 'dagger': bool(mm and mm.group(2))}
    note = norm(T['note'])

    # ---- every side-by-side row typed into the calculator: page = calculator = formula = nb_stats.json
    for (h, lb) in GRID:
        got = calc(pg, h // 12, h % 12, lb)
        e = expect(*us(h, lb))
        pr = page_rows.get((h, lb), {})
        js = SBS[(h, lb)]
        for k in ('traditional', 'new', 'difference'):
            ok(pr.get(k) == got[k] == e[k] == js[k], f'{hlab(h)} {lb} lb {k}: page {pr.get(k)!r}, calculator {got[k]!r}, formula {e[k]!r}, stats {js[k]!r}')
        ok((got['tc'], got['nc']) == (e['tc'], e['nc']) == (js['traditional_category'], js['new_category']), f'{hlab(h)} {lb} lb categories {got["tc"]}/{got["nc"]}')
        changes = got['tc'] != got['nc']
        ok(pr.get('dagger') == changes, f'{hlab(h)} {lb} lb: dagger {pr.get("dagger")} but the category {"changes" if changes else "stays"}')
        if changes:
            ok(f'at {hlab(h)} and {lb} lb from {got["tc"]} to {got["nc"]}' in note, f'the note does not name {hlab(h)} {lb} lb: {got["tc"]} to {got["nc"]}')
    ok(note.startswith('† The category changes with New BMI:'), 'dagger note')

    # ---- the worked examples, typed in
    ok(len(T['ex']) == 2, 'two worked examples')
    for ex, h in zip(T['ex'], (62, 74)):
        got = calc(pg, h // 12, h % 12, 150)
        e = expect(*us(h, 150))
        kg2, m4 = f'{half_up(150 / 2.20462, 2)}', f'{Decimal(h) * Decimal("0.0254"):.4f}'
        us_new, shown_new = f1(5734 * 150 / h ** 2.5), f1(1.3 * float(kg2) / float(m4) ** 2.5)
        shown_trad = f1(float(kg2) / float(m4) ** 2)
        hd, dt1, dd1, dt2, dd2, dt3, dd3 = [norm(x) for x in ex]
        ok(hd == f'{hlab(h)} and 150 lb ({cm1(h)}, {kg1(150)})', f'example head {hd!r}')
        ok(got['traditional'] == e['traditional'] and dt1 == f'Traditional BMI: {got["traditional"]}, {got["tc"]}', f'example {hlab(h)}: {dt1!r} vs calculator {got["traditional"]} {got["tc"]}')
        ok(got['new'] == e['new'] and dt2 == f'New BMI: {got["new"]}, {got["nc"]}', f'example {hlab(h)}: {dt2!r} vs calculator {got["new"]} {got["nc"]}')
        ok(got['difference'] == e['difference'] and dt3 == f'Difference: {got["difference"]}', f'example {hlab(h)}: {dt3!r} vs calculator {got["difference"]}')
        ok(dd1 == f'150 × 703 ÷ {h}² = {e["traditional"]}. In metric, {kg2} ÷ {m4}² gives the same {shown_trad}.' and shown_trad == e['traditional'], f'example arithmetic {dd1!r}')
        ok(dd2 == f'5734 × 150 ÷ {h}2.5 = {us_new}. In metric, 1.3 × {kg2} ÷ {m4}2.5 = {e["new"]}.' and us_new == shown_new == e['new'], f'example arithmetic {dd2!r}')
        ok(dd3.startswith(f'{e["new"]} {M} {e["traditional"]}.'), f'example difference {dd3!r}')
        if h == 74:
            ok('The category changes from Healthy weight to Underweight' in dd3 and (got['tc'], got['nc']) == ('Healthy weight', 'Underweight'), f'6′2″ category change {dd3!r}')
        else:
            ok('the category stays the same' in dd3 and got['tc'] == got['nc'], f'5′2″ same category {dd3!r}')

    # ---- the anchors, typed in as literals
    for (ft, inch, lb), t, n, d, cats in ANCHORS:
        got = calc(pg, ft, inch, lb)
        ok((got['traditional'], got['new'], got['difference']) == (t, n, d), f'anchor {ft}′{inch}″ {lb} lb: calculator {got["traditional"]} {got["new"]} {got["difference"]}, chat read {t} {n} {d}')
        if cats == 'same': ok(got['tc'] == got['nc'], f'anchor {ft}′{inch}″ {lb} lb should keep its category')
        elif cats: ok((got['tc'], got['nc']) == cats, f'anchor {ft}′{inch}″ {lb} lb categories {got["tc"]}/{got["nc"]}')
        pr = page_rows.get((ft * 12 + inch, lb))
        if pr: ok((pr['traditional'], pr['new'], pr['difference']) == (t, n, d), f'anchor row on the page {ft}′{inch}″ {lb} lb: {pr}')
    ex_vals = {norm(x[0]).split(' and ')[0]: [norm(c).split(': ')[1].split(',')[0] for c in (x[1], x[3], x[5])] for x in T['ex']}
    ok(ex_vals == {f'5{FT}2{IN}': ['27.4', '28.4', '+1.0'], f'6{FT}2{IN}': ['19.3', '18.3', M + '1.0']}, f'worked examples against the anchors {ex_vals}')

    # ---- three metric entries, from the formula
    for cm, kg in METRIC:
        got = calc(pg, cm=cm, kg=kg)
        e = expect(*metric(cm, kg))
        ok(all(got[k] == e[k] for k in ('traditional', 'new', 'difference', 'tc', 'nc')), f'metric {cm} cm {kg} kg: calculator {got}, formula {e}')
    pg.click('#panel-newbmi .unit-btn[data-unit="imperial"]')

    # ---- the by-height table: the formula and the anchors
    want = []
    for h in (60, 64, 66.5, 68, 70, 72, 76):
        m = h * 0.0254
        ratio = 1.3 / math.sqrt(m)
        pct = half_up((ratio - 1) * 100, 1)
        ps = ('+' if pct > 0 else M if pct < 0 else '') + f'{abs(pct):.1f}%'
        ft, i = divmod(Decimal(str(h)), 12)
        lab = f'{int(ft)}{FT}{i.normalize() if i != i.to_integral() else int(i)}{IN}'
        want.append([lab, f'{half_up(m, 2)} m', ps, f1(25.0 * ratio)])
    ok([norm(c) for c in T['byhHead']] == ['Height', 'Change', '25.0 becomes'], f'by-height head {T["byhHead"]}')
    byh = [[norm(c) for c in r] for r in T['byh']]
    ok(byh == want, f'by-height table {byh} != {want}')
    ok(byh[0][2:] == ['+5.3%', '26.3'] and byh[5][2:] == [M + '3.9%', '24.0'], f'by-height anchors {byh[0]} {byh[5]}')
    ok([b['percent'] for b in S['by_height']] == [w[2] for w in want], 'nb_stats.json by-height percentages')

    # ---- the figure against the formula
    F = pg.evaluate("""() => { const svg = document.querySelector('#by-height figure svg');
        return {vb: svg.getAttribute('viewBox'), poly: [...svg.querySelectorAll('polyline')].map(p => p.getAttribute('points')),
          circles: [...svg.querySelectorAll('circle')].map(c => [+c.getAttribute('cx'), +c.getAttribute('cy'), c.getAttribute('fill'), c.querySelector('title').textContent]),
          texts: [...svg.querySelectorAll('text')].map(t => t.textContent), title: svg.querySelector('title').textContent, desc: svg.querySelector('desc').textContent,
          colors: [...svg.querySelectorAll('*')].flatMap(e => [e.getAttribute('fill'), e.getAttribute('stroke')]).filter(Boolean),
          cap: svg.parentElement.querySelector('figcaption').textContent} }""")
    xs = lambda m: 30 + (m - 1.40) * 280 / 0.60
    ys = lambda v: 30 + (4 - v) * 156 / 6
    ok(F['vb'] == '0 0 320 226' and len(F['poly']) == 1, f'figure viewBox / curve {F["vb"]}')
    pts = [tuple(map(float, q.split(','))) for q in F['poly'][0].split()]
    ok(len(pts) == 61, f'{len(pts)} curve points')
    for k, (x, y) in enumerate(pts):
        m = (140 + k) / 100
        ok(abs(x - xs(m)) < 0.006 and abs(y - ys(curve(m))) < 0.006, f'curve point {k} at {m} m: {x},{y}')
    for (cx, cy, fill, tip), (inch, word) in zip(F['circles'][:2], ((60, 'higher'), (72, 'lower'))):
        m = inch * 0.0254
        t, n = metric(inch * 2.54, 70)
        d = sg(r1(n) - r1(t))
        ok(abs(cx - xs(m)) < 0.006 and abs(cy - ys(curve(m))) < 0.006 and fill == '#0e7490', f'mark at {hlab(inch)}: {cx},{cy}')
        ok(d == sg(float(half_up(curve(m), 1))) and f'{d} at {hlab(inch)}' in F['texts'], f'mark label {d} at {hlab(inch)}')
        ok(tip == f'{hlab(inch)} ({m:.2f} m): New BMI {d.lstrip("+" + M)} points {word} at 154 lb', f'mark tooltip {tip!r}')
    cx, cy, fill, tip = F['circles'][2]
    ok(len(F['circles']) == 3 and abs(cx - xs(1.69)) < 0.006 and abs(cy - ys(0)) < 0.006 and fill == '#ffffff' and abs(curve(1.69)) < 1e-12,
       f'crossing {cx},{cy}')
    ok('Same at 5′6.5″ (1.69 m)' in F['texts'] and tip == 'Same at 5′6.5″ (1.69 m)', 'crossing label')
    for inch in (56, 60, 64, 68, 72, 76):
        ok(hlab(inch) in F['texts'] and f'{inch * 0.0254:.2f} m' in F['texts'], f'x label {hlab(inch)}')
    ok(all(lab in F['texts'] for lab in ('+4', '+3', '+2', '+1', '0', M + '1', M + '2')), 'y labels')
    ok('New BMI minus traditional BMI at 154 lb (70 kg)' in F['texts'] and half_up(70 * 2.20462, 0) == 154, 'figure heading')
    lo, hi = curve(1.40), curve(2.00)
    hl = lambda m: f'{int(Decimal(str(m / 0.0254)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) // 12)}{FT}' \
                   f'{Decimal(str(m / 0.0254)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) % 12}{IN}'
    ok(norm(F['desc']) == (f'New BMI minus traditional BMI at 154 lb (70 kg), from {hl(1.40)} to {hl(2.00)} (1.40 to 2.00 m): '
       f'{half_up(lo, 1)} points higher at {hl(1.40)}, 1.6 higher at 5′0″ (1.52 m), the same at 5′6.5″ (1.69 m), 0.8 lower at '
       f'6′0″ (1.83 m) and {half_up(-hi, 1)} lower at {hl(2.00)}. Our calculation from the two formulas.'), f'figure desc {F["desc"]!r}')
    ok(norm(F['cap']).startswith(f'New BMI minus traditional BMI at 154 lb (70 kg), from {hl(1.40)} to {hl(2.00)}'), 'figure caption')
    PALETTE = {'#0e7490', '#4b5563', '#111827', '#ffffff', '#374151', '#9ca3af', '#d1d5db', 'none'}
    ok(set(c.lower() for c in F['colors']) <= PALETTE, f'colours outside the palette: {set(F["colors"]) - PALETTE}')

    # ---- FAQ: questions, JSON-LD = visible, one tap opens and one closes
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([q for q, _ in visq] == FAQ_Q, f'FAQ questions {[q for q, _ in visq]}')
    ok([[q['name'], q['acceptedAnswer']['text']] for q in GR['FAQPage']['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')
    ok(len(visq) == 7 and visq[3][1].startswith('Trefethen doesn’t claim that.'), 'FAQ 4 first sentence')
    for i, q in enumerate(pg.query_selector_all('.faq-question')):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open in one tap')
        q.click(); pg.wait_for_timeout(30)
        ok(not pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not close in one tap')

    # ---- words: nothing from the NEVER WRITE list (the FAQ question that asks it is the searcher's own words)
    faq_text = ' '.join(a for _, a in visq)
    words_all = norm(pg.inner_text('main')) + ' ' + faq_text + ' ' + ' '.join(str(v) for v in head.values()) + ' ' + json.dumps(ld, ensure_ascii=False)
    words_all = words_all.replace('Is the new BMI more accurate than traditional BMI?', '')
    for pat in NEVER:
        hit = re.search(pat, words_all, re.I if pat not in (r'\bNormal\b',) else 0)
        ok(not hit, f'banned wording on the page: {hit.group(0) if hit else ""!r} ({pat})')

    # ---- links and chips
    hrefs = pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for h_ in sorted({h_.split('#')[0] for h_ in hrefs if h_.startswith('/')}):
        ok(pg.request.get(base + h_).status == 200, f'internal link {h_} does not answer 200')
    for h_ in sorted({h_ for h_ in hrefs if h_.startswith('/') and '#' in h_}):
        path, frag = h_.split('#')
        ok(f'id="{frag}"' in pg.request.get(base + path).text(), f'anchor {h_} missing')
    for h_ in {h_ for h_ in hrefs if h_.startswith('#')}:
        ok(pg.evaluate('h => !!document.getElementById(h.slice(1))', h_), f'anchor {h_} missing')
    outside = set(pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))'))
    ok(outside and outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')
    ok(len(outside) == 6, f'{len(outside)} outside links')
    ok(all(pg.evaluate('h => [...document.querySelectorAll(`main a[href="${h}"]`)].every(a => a.target === "_blank" && a.rel === "noopener")', h_) for h_ in outside),
       'outside links open in a new tab')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#formulas', '#by-height', '#side-by-side', '#examples', '#why', '#which', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')

    # ---- labels on the five pages: each names the expected field, and a click on it focuses that field
    for path, want_ids in LABELS.items():
        pg.goto(base + path, wait_until='load'); pg.wait_for_timeout(50)
        fors = pg.eval_on_selector_all('main label', 'ls => ls.map(l => l.htmlFor)')
        ok(sorted(fors) == sorted(want_ids), f'{path}: labels name {fors}')
        ok(pg.evaluate("ids => ids.every(i => document.querySelectorAll('[id=\"' + i + '\"]').length === 1)", want_ids), f'{path}: an id is missing or repeated')
        seen = set()
        for unit in ('imperial', 'metric'):
            pg.click(f'.unit-btn[data-unit="{unit}"]'); pg.wait_for_timeout(20)
            for f in fors:
                if not pg.evaluate('f => { const c = document.getElementById(f); return !!c && c.offsetParent !== null; }', f): continue
                pg.evaluate('() => document.activeElement && document.activeElement.blur()')
                pg.click(f'label[for="{f}"]')
                ok(pg.evaluate('() => document.activeElement && document.activeElement.id') == f, f'{path}: clicking the label for {f} does not focus it')
                seen.add(f)
        ok(seen == set(want_ids), f'{path}: labels never shown: {sorted(set(want_ids) - seen)}')

    # ---- widths before and after Calculate, the fold, table frames, rendered labels
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 844}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
        if w in (360, 390):
            ok(pg.evaluate("document.querySelector('#calc-newbmi-btn').getBoundingClientRect().bottom") <= 844, f'Calculate below the fold at {w}')
        for when in ('before', 'after'):
            if when == 'after':
                pg.click('#calc-newbmi-btn'); pg.wait_for_timeout(120)
                ok(pg.evaluate("getComputedStyle(document.getElementById('newbmi-results')).display") != 'none', f'results hidden at {w}')
                txt = pg.inner_text('#newbmi-results')
                ok('NaN' not in txt and 'undefined' not in txt and 'Infinity' not in txt, f'NaN/undefined in the results at {w}')
            sw = pg.evaluate('document.documentElement.scrollWidth')
            ok(sw <= w, f'page {sw}px wide at {w} {when} Calculate')
            fits = pg.evaluate("""() => [...document.querySelectorAll('main table')].filter(t => t.offsetParent !== null)
                .map(t => [t.caption ? t.caption.textContent : t.className, t.offsetWidth, t.parentElement.clientWidth,
                           !!t.closest('#newbmi-results'), getComputedStyle(t.parentElement).overflowX, t.parentElement.getBoundingClientRect().right])""")
            for cap, tw, fw, result, ovf, right in fits:
                if not result or w >= 390:                   # the page's own tables at every width; the results tables at 390 and up
                    ok(tw <= fw + 1, f'table wider than its frame at {w} {when} Calculate: {cap} {tw} > {fw}')
                else:                                        # calculator.js's result tables at 320/360 scroll inside their .er-section
                    ok(ovf == 'auto' and right <= w + 0.5, f'result table outside a scrolling frame at {w}: {cap} {tw} > {fw} ({ovf})')
        res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
            const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
            const ctm = svg.getScreenCTM(), pt = svg.createSVGPoint();
            const curve = [...svg.querySelectorAll('polyline')].map(pl => [...pl.points].map(q => { pt.x = q.x; pt.y = q.y; const s = pt.matrixTransform(ctm); return [s.x, s.y]; }));
            return {box: [r.left, r.top, r.right, r.bottom], scale: ctm.a, curve,
                    texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                    shapes: [...svg.querySelectorAll('rect, circle, line')].map(e => [e.tagName + ' ' + (e.getAttribute('fill') || e.getAttribute('stroke')), ...bx(e)])}; })""")
        ok(len(res) == 1, f'{len(res)} figures at {w}')
        for f_ in res:
            L_, T_, R_, B_ = f_['box']
            half = 1.25 * f_['scale']                                                    # half the curve's stroke, on screen
            for j, a in enumerate(f_['texts']):
                ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                for c2 in f_['texts'][j + 1:]:
                    ok(not (a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5), f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                for s_ in f_['shapes']:
                    ok(not (a[1] < s_[3] - 0.5 and s_[1] < a[3] - 0.5 and a[2] < s_[4] - 0.5 and s_[2] < a[4] - 0.5), f'{w}px label over a shape: {a[0]!r} / {s_[0]}')
                for line in f_['curve']:
                    hit = False
                    for (x1, y1), (x2, y2) in zip(line, line[1:]):
                        steps = max(1, int(math.hypot(x2 - x1, y2 - y1) / 0.5))
                        for k in range(steps + 1):
                            x, y = x1 + (x2 - x1) * k / steps, y1 + (y2 - y1) * k / steps
                            if a[1] - half < x < a[3] + half and a[2] - half < y < a[4] + half: hit = True
                    ok(not hit, f'{w}px label on the plotted curve: {a[0]!r}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures, {skipped} skipped')
for f_ in fails[:40]: print('FAIL', f_)
sys.exit(1 if fails or skipped else 0)
