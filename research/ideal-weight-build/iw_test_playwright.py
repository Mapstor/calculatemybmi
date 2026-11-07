#!/usr/bin/env python3
"""/ideal-weight/ checks in Chromium (CMB-028). Needs Python Playwright + Chromium.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/ideal-weight-build/iw_test_playwright.py http://localhost:8000 research/ideal-weight-build/iw_stats.json
  - the calculator: every row of both by-height tables typed into the real calculator at a medium frame, and the page's
    cells equal what it prints, the formulas written again here (exact fractions, halves up) and iw_stats.json; the span
    tile and the summary sentence for every row; Hamwi at a small and a large frame at 5′0″, 5′6″ and 6′0″ for both sexes,
    and only Hamwi changes; chat's step 1 anchors typed in as literals (three metric entries and 4′10″ included);
  - the formulas table: every coefficient equals the published constants (and calculator.js uses them), every conversion
    is right to its printed decimals; the wrist table and its cm;
  - the figure: every point of the eight lines and the two bands against the formulas and the healthy-range rule, the
    colours and dashes (no purple), the legend above the panels, the axis labels, the hover titles; rendered labels stay
    inside the figure and off each other, every shape and every plotted line;
  - labels: each names the expected field and a click on it focuses that field, in US units and in metric;
  - Calculate ends above the fold at 360 and 390 px; the page is never wider than the screen at 320, 360, 390 and 1280,
    before and after Calculate; every table fits its frame at 360, 390 and 1280 (at 320 a table may scroll inside a frame
    that stays on the screen);
  - 9 FAQ in order, the JSON-LD equal to the visible answers, one tap opens an answer and one closes it;
  - sections sit directly in main .container, no <article>, no page-level style, no inline style in <main> outside the
    figure; the head's scripts other than JSON-LD, the header and everything after </main> equal origin/main's;
  - head: title, description, OG and Twitter text and images, the JSON-LD graph, the preferred images, old OG image gone;
  - internal links answer 200, anchors exist, outside links are registry URLs; nothing from the prompt's NEVER WRITE list,
    and no "average" in <main>, in the results or in the head.
Every check runs; nothing is skipped. Exit 1 on any failure."""
import sys, os, json, math, re, csv, struct, subprocess
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction as Fr
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1].rstrip('/'), sys.argv[2]
BUILD = os.path.dirname(os.path.abspath(stats))
ROOT = os.path.abspath(os.path.join(BUILD, '..', '..'))
S = json.load(open(stats, encoding='utf-8'))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()}
URL = base + '/ideal-weight/'
SITE = 'https://calculatemybmi.net'
FT, IN = '′', '″'

fails, checks, skipped = [], 0, 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

def norm(t): return re.sub(r'\s+', ' ', (t or '').replace(' ', ' ').replace('­', '')).strip()
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def hlab(i): return f'{i // 12}{FT}{i % 12}{IN}'
def hq(i): return f"{i // 12}'{i % 12}\""          # the calculator writes heights with ASCII quotes (heightToFtIn)

# ---- the formulas, written again here from the published constants (prompt facts 1, 4, 5), in exact fractions
LB = Fr('2.20462')
CONST = {'female': {'hamwi': ('100', '5', 'lb'), 'devine': ('45.5', '2.3', 'kg'), 'robinson': ('49', '1.7', 'kg'), 'miller': ('53.1', '1.36', 'kg')},
         'male': {'hamwi': ('106', '6', 'lb'), 'devine': ('50', '2.3', 'kg'), 'robinson': ('52', '1.9', 'kg'), 'miller': ('56.2', '1.41', 'kg')}}
NAMES = ('hamwi', 'devine', 'robinson', 'miller')
LABEL = {'hamwi': 'Hamwi', 'devine': 'Devine', 'robinson': 'Robinson', 'miller': 'Miller'}
FRAME = {'small': Fr(9, 10), 'medium': Fr(1), 'large': Fr(11, 10)}

def half(x, places=0):
    return math.floor(x * 10 ** places + Fr(1, 2))

def kg_s(k10): return f'{k10 // 10}.{k10 % 10}'

def exact(inches, sex, frame='medium'):
    """{name: (lb, kg)} as fractions; inches may be a fraction (a metric entry is cm / 2.54)."""
    over = Fr(inches) - 60
    out = {}
    for n in NAMES:
        b, p, u = CONST[sex][n]
        v = Fr(b) + Fr(p) * over
        out[n] = (v * FRAME[frame], v * FRAME[frame] / LB) if u == 'lb' else (v * LB, v)
    return out

def printed(inches, sex, frame='medium'):
    """What the calculator should print: whole lb and kg to 0.1, halves up."""
    return {n: (half(lb), kg_s(half(kg, 1))) for n, (lb, kg) in exact(inches, sex, frame).items()}

def bmi_r(lb, inches):                 # CDC's US formula, rounded once to 0.1, halves up
    return Fr(half(lb * 703 / Fr(inches) ** 2, 1), 10)

def healthy(inches):
    """Whole lb and whole kg whose BMI, rounded half up to 0.1, is 18.5 to 24.9 at this exact height (brute force)."""
    h = Fr(inches)
    def band(f):
        ws = [w for w in range(20, 400) if Fr(185, 10) <= Fr(half(f(w), 1), 10) <= Fr(249, 10)]
        return ws[0], ws[-1]
    return band(lambda w: Fr(w) * 703 / h ** 2), band(lambda w: Fr(w) / (h * Fr('0.0254')) ** 2)

def conv(v, unit, places):
    x = Fr(v) / LB if unit == 'lb' else Fr(v) * LB
    return f'{(Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)}'

TABLE_H = {'female': range(60, 73), 'male': range(60, 79)}
TITLE = 'Ideal Body Weight Calculator (IBW): 4 Formulas Compared'
H1 = 'Ideal Body Weight Calculator'
DESC = ('How much should you weigh? Get your ideal body weight from the Devine, Robinson, Miller and Hamwi formulas, '
        'next to the healthy BMI range for your height.')
PI = {r: f'{SITE}/assets/images/preferred/ideal-weight-{r}.png' for r in ('1x1', '4x3', '16x9')}
FAQ_Q = ['How much should I weigh for my height?', 'What is ideal body weight (IBW)?', 'What is the formula for ideal body weight?',
         'Why do the four formulas give different results?', 'Which ideal weight formula is the most accurate?',
         'Does ideal weight change with age?', 'How do I find my body frame size?', 'Is ideal body weight the same as a healthy weight?',
         'Can children use these formulas?']
LABEL_IDS = ['ideal-height-ft', 'ideal-height-in', 'ideal-height-cm', 'ideal-sex', 'ideal-frame']
# The prompt's NEVER WRITE list (the FAQ question that asks "most accurate" is the searcher's own words and is removed first)
NEVER = [r'\bmore accurate\b', r'\bmost accurate\b', r'\bvalidated\b', r'\bproven\b', r'\bthe best\b', r'\bbest formula', r'robust',
         r'averag', r'\belbow', r'\bmortality\b', r'correlat\w* with',
         r'Hamwi[’\']?s? (?:rule|formula|equation)s?[^.]{0,60}\b(?:behind|basis|became|converted|turned into)\b[^.]{0,40}Devine',
         r'Devine[^.]{0,60}\b(?:convert\w*|version|based on|took|adapted)\b[^.]{0,40}Hamwi', r'Pai and Paloucek[^.]{0,80}\bframe\b[^.]{0,40}10%',
         r'\btarget weight', r'\bgoal weight', r'you should weigh', r'\blose weight', r'\bweight[- ]loss', r'\bdiet\b', r'\bcalori',
         r'\bexercise', r'adjusted body weight', r'\bABW\b', r'\bmg/kg', r'\bdose\b', r'loading dose', r'dosing weight',
         r'\bnormal weight\b', r'\bobese\b', r'\bWinter\b', r'\bWing\b', r'NHLBI', r'\bWHO\b', r'World Health Organization',
         r'healthy (?:BMI )?range for (?:wo)?men']
CASE = {r'\bABW\b', r'\bWinter\b', r'\bWing\b', r'NHLBI', r'\bWHO\b'}


def git_main():
    return subprocess.run(['git', '-C', ROOT, 'show', 'origin/main:ideal-weight/index.html'], capture_output=True, text=True, check=True).stdout


def head_scripts(src):
    head = src[:src.index('</head>')]
    return [s for s in re.findall(r'(?s)<script\b[^>]*>.*?</script>', head) if 'application/ld+json' not in s]


US_RX = re.compile(r'(\d+) lbs \((\d+\.\d) kg\)')
MET_RX = re.compile(r'(\d+\.\d) kg \((\d+) lbs\)')


def calc(pg, ft=None, inch=None, cm=None, sex='female', frame='medium'):
    """Types an entry into the page's calculator, presses Calculate and reads what it prints."""
    unit = 'metric' if cm is not None else 'imperial'
    pg.click(f'#panel-ideal .unit-btn[data-unit="{unit}"]')
    if unit == 'imperial':
        pg.fill('#ideal-height-ft', str(ft)); pg.fill('#ideal-height-in', str(inch))
    else:
        pg.fill('#ideal-height-cm', str(cm))
    pg.select_option('#ideal-sex', sex); pg.select_option('#ideal-frame', frame)
    pg.click('#calc-ideal-btn'); pg.wait_for_timeout(30)
    got = {k: norm(pg.inner_text(f'#ideal-{k}')) for k in (*NAMES, 'span', 'bmi-range')}
    got['results'] = norm(pg.inner_text('#ideal-results'))
    got['visible'] = pg.evaluate("getComputedStyle(document.getElementById('ideal-results')).display") != 'none'
    for n in NAMES:
        mm = (US_RX if unit == 'imperial' else MET_RX).fullmatch(got[n])
        got[n + '_p'] = None if not mm else ((int(mm.group(1)), mm.group(2)) if unit == 'imperial' else (int(mm.group(2)), mm.group(1)))
    return got


def span_text(p, metric=False):
    lbs, kgs = [p[n][0] for n in NAMES], [Decimal(p[n][1]) for n in NAMES]
    rl = lambda a, b, u: (f'{a}' if a == b else f'{a}–{b}') + f' {u}'
    lb_s, kg_s_ = rl(min(lbs), max(lbs), 'lbs'), rl(min(kgs), max(kgs), 'kg')
    return f'{kg_s_} ({lb_s})' if metric else f'{lb_s} ({kg_s_})'


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
    ok(f'<title>{TITLE}</title>' in src and pg.inner_text('h1') == H1 and src.count('<h1') == 1, 'title / H1')
    mains = src[src.index('<main'):src.index('</main>')]
    ok('<style' not in src and '<article' not in src and pg.evaluate("document.querySelectorAll('article').length") == 0, 'page-level style or <article>')
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>', '', mains), 'inline style in <main> outside figures')
    ok(mains.startswith('<main class="reading"><div class="container">'), 'reading column')
    kids = pg.evaluate("""() => [...document.querySelector('main > .container').children].map(e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + '.' + [...e.classList].join('.'))""")
    ok(kids == ['div.page-head', 'div.calculator-card', 'div.key-takeaways', 'div.disclaimer-box', 'nav.toc-inline',
                'section#formulas.content-section.flow', 'section#by-height.content-section.flow', 'section#frame.content-section.flow',
                'section#examples.content-section.flow', 'section#healthy-range.content-section.flow', 'section#faq.content-section',
                'section#sources.content-section.flow', 'section.content-section'], f'blocks in main .container: {kids}')
    ok(pg.evaluate("[...document.querySelectorAll('main section')].every(s => s.parentElement.matches('main > .container'))"),
       'a section is not a direct child of main .container')
    words = pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, script, style, #ideal-results').forEach(e => e.remove()); return m.textContent.split(/\\s+/).filter(Boolean).length; }""")
    ok(1500 <= words <= 2300, f'{words} words in main')
    body_text = pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, #ideal-results').forEach(e => e.remove()); return m.textContent; }""")
    ok('—' not in body_text, 'em dash in the body (the result placeholders aside)')
    ids = ['panel-ideal', 'calc-ideal-btn', 'ideal-results', 'ideal-span', 'ideal-hamwi', 'ideal-devine', 'ideal-robinson', 'ideal-miller',
           'ideal-bmi-range', *LABEL_IDS]
    ok(all(src.count(f'id="{i}"') == 1 for i in ids) and 'ideal-average' not in src, 'a kept calculator id is missing or ideal-average is left')
    start = pg.evaluate("['ideal-height-ft', 'ideal-height-in', 'ideal-height-cm', 'ideal-sex', 'ideal-frame'].map(i => document.getElementById(i).value)")
    ok(start == ['5', '6', '168', 'female', 'medium'], f'starting values {start}')
    lab = pg.evaluate("() => [...document.querySelectorAll('#panel-ideal label')].map(l => [l.htmlFor, l.textContent.trim()])")
    ok(['ideal-frame', 'Body frame (changes Hamwi only)'] in lab, f'frame label {lab}')
    tiles = pg.evaluate("() => [...document.querySelectorAll('#ideal-results .result-item')].map(t => [t.querySelector('.result-item-value').id, t.querySelector('.result-item-label').textContent])")
    ok(tiles == [['ideal-span', 'The four formulas'], ['ideal-bmi-range', 'Healthy BMI range (18.5–24.9)'], ['ideal-hamwi', 'Hamwi (1964)'],
                 ['ideal-devine', 'Devine (1974)'], ['ideal-robinson', 'Robinson (1983)'], ['ideal-miller', 'Miller (1983)']], f'result tiles {tiles}')

    # ---- head and JSON-LD
    head = pg.evaluate("""() => ({desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content), canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content), ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        ogt: document.querySelector('meta[property="og:title"]').content, twt: document.querySelector('meta[name="twitter:title"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content),
        ogd: document.querySelector('meta[property="og:description"]').content, twd: document.querySelector('meta[name="twitter:description"]').content})""")
    ok(head['desc'] == DESC and len(head['desc']) <= 160, f'description ({len(head["desc"])} characters) {head["desc"]!r}')
    ok(head['ogd'] == head['twd'] == DESC and head['ogt'] == head['twt'] == TITLE, f'OG / Twitter text {head}')
    ok(head['robots'] == ['max-image-preview:large'] and head['canon'] == SITE + '/ideal-weight/', 'robots / canonical')
    ok(head['og'] == [PI['16x9']] and head['tw'] == [PI['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'OG / Twitter image {head}')
    ok(head['ogalt'].startswith('Chart: the Hamwi, Devine, Robinson and Miller ideal body weights') and '"' not in head['ogalt'], 'og:image:alt')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/ideal-weight-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/assets/images/og/ideal-weight-formula-fan.png').status == 404, 'old OG image still served')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['WebPage', 'WebApplication', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    GR = {x['@type']: x for x in ld[0]['@graph']}
    ok(GR['WebPage']['primaryImageOfPage']['url'] == PI['16x9'] and GR['WebPage']['name'] == TITLE, 'WebPage')
    ok(GR['WebApplication']['image'] == [PI['1x1'], PI['4x3'], PI['16x9']] and GR['WebApplication']['author']['name'] == 'Marko Visic'
       and GR['WebApplication']['name'] == H1, 'WebApplication image list / author')
    ok([i['name'] for i in GR['BreadcrumbList']['itemListElement']] == ['Home', 'Calculators', 'Ideal Body Weight Calculator'], 'breadcrumb')

    # ---- the fixed text: intro, takeaways (chat's words), disclaimer (the men page's, verbatim)
    ok(norm(pg.inner_text('.intro-text')) == 'Find your ideal body weight with all four published formulas, next to the healthy weight range for your height.', 'intro text')
    ok(norm(pg.inner_text('.intro-note')) == 'Height formulas from 1964 to 1983, not a medical standard: CDC screens weight with BMI. Method and sources'
       and pg.get_attribute('.intro-note a', 'href') == '#sources', 'intro note')
    kt = pg.evaluate("() => [document.querySelector('.key-takeaways .answer').textContent, ...[...document.querySelectorAll('.key-takeaways li')].map(l => l.textContent)]")
    ok([norm(x) for x in kt] == [
        'Ideal body weight (IBW) is a weight worked out from height alone. The four formulas in use start at 5 feet and add a fixed amount per inch: for a 5′6″ woman they give 130 to 135 lb, inside the healthy BMI range of 115 to 154 lb at that height.',
        'The formulas agree within 3 lb at 5′8″ for women and 5′6″ for men and split apart toward both ends: at 6′6″ the men’s run from 180 lb (Miller) to 214 lb (Hamwi).',
        'At a medium frame every formula stays inside CDC’s healthy BMI range at the heights in the tables, at a BMI of 19.5 to 22.9 for women and 20.7 to 24.7 for men.',
        'Hamwi (1964) works in pounds and adjusts for frame size: 10% less for a small frame, 10% more for a large one.',
        'Pai and Paloucek concluded that “any one of these equations may be used to estimate IBW,” and Peterson and colleagues note that IBW equations “have largely been replaced by BMI ranges.”'],
       f'key takeaways {kt}')
    men = pg.request.get(base + '/men-bmi-calculator/').text()
    disc = lambda s: re.search(r'(?s)<div class="disclaimer-box">.*?</div>', s).group(0)
    ok(disc(src) == disc(men), 'disclaimer is not the men page wording')

    # ---- the formulas table: constants as published, conversions right to their printed decimals; calculator.js uses them
    FTb = pg.evaluate("""() => [...document.querySelectorAll('#formulas table tbody tr')].map(r => [r.cells[0].firstChild.textContent,
        r.cells[0].querySelector('.th-sub').textContent, ...[1, 2].flatMap(i => [r.cells[i].firstChild.textContent, r.cells[i].querySelector('.unit-alt').textContent])])""")
    ok([r[:2] for r in FTb] == [['Hamwi', '1964'], ['Devine', '1974'], ['Robinson', '1983'], ['Miller', '1983']], f'formula rows {[r[:2] for r in FTb]}')
    for row, n in zip(FTb, NAMES):
        for sex, pub, alt in (('female', row[2], row[3]), ('male', row[4], row[5])):
            b, pi, u = CONST[sex][n]
            o = 'kg' if u == 'lb' else 'lb'
            mm = re.fullmatch(r'([\d.]+) (lb|kg) \+ ([\d.]+) (lb|kg)', norm(pub))
            ok(mm and (mm.group(1), mm.group(2), mm.group(3), mm.group(4)) == (b, u, pi, u), f'{n} {sex} as published: {pub!r}')
            ma = re.fullmatch(r'([\d.]+) (lb|kg) \+ ([\d.]+) (lb|kg)', norm(alt))
            if ma:
                d1, d2 = len(ma.group(1).split('.')[1]) if '.' in ma.group(1) else 0, len(ma.group(3).split('.')[1]) if '.' in ma.group(3) else 0
                ok((ma.group(1), ma.group(3)) == (conv(b, u, d1), conv(pi, u, d2)) and ma.group(2) == ma.group(4) == o and (d1, d2) == (1, 2),
                   f'{n} {sex} conversion {alt!r}: {conv(b, u, d1)} + {conv(pi, u, d2)}')
            else:
                ok(False, f'{n} {sex} conversion not readable: {alt!r}')
    ok(pg.evaluate("document.querySelector('#formulas caption').textContent").endswith('with our conversion under it'), 'formulas caption')
    js = open(os.path.join(ROOT, 'assets/js/calculator.js'), encoding='utf-8').read()
    fn = re.search(r'(?s)function calculateIdealWeight\(\) \{.*?\n\}', js).group(0)
    for frag in ('male ? 50 + 2.3 * over : 45.5 + 2.3 * over', 'male ? 52 + 1.9 * over : 49 + 1.7 * over',
                 'male ? 56.2 + 1.41 * over : 53.1 + 1.36 * over', 'male ? 106 + 6 * over : 100 + 5 * over',
                 "f === 'small' ? 0.9 : f === 'large' ? 1.1 : 1", 'heightInches < 60', 'lbsToKg(lb)', 'kgToLbs(kg)'):
        ok(frag in fn, f'calculator.js calculateIdealWeight() lacks {frag!r}')
    ok('2.20462' in re.search(r'function lbsToKg[^\n]*', js).group(0) and '2.20462' in re.search(r'function kgToLbs[^\n]*', js).group(0), '2.20462 in calculator.js')

    # ---- the by-height tables, every row typed into the calculator: page = calculator = formula = iw_stats.json
    TB = pg.evaluate("""() => [...document.querySelectorAll('#by-height table')].map(t => ({cap: t.caption.textContent,
        head: [...t.querySelectorAll('thead th')].map(c => c.textContent), cls: t.className,
        rows: [...t.querySelectorAll('tbody tr')].map(r => [r.id, r.cells[0].firstChild.textContent, r.cells[0].querySelector('.th-sub').textContent,
              ...[...r.cells].slice(1).flatMap(c => [c.firstChild.textContent, c.querySelector('.cell-kg').textContent])])}))""")
    ok(len(TB) == 2, f'{len(TB)} by-height tables')
    for t, sex in zip(TB, ('female', 'male')):
        word = 'Women' if sex == 'female' else 'Men'
        ok(norm(t['cap']) == f'{word}, medium frame: lb, with kg under each value', f'caption {t["cap"]!r}')
        ok([norm(c) for c in t['head']] == ['Heightcm', 'Hamwi', 'Devine', 'Robinson', 'Miller', 'Healthy BMI range'], f'{word} head {t["head"]}')
        ok('data-table--fit' in t['cls'] and 'data-table--tight' in t['cls'], f'{word} table classes {t["cls"]}')
        ok(len(t['rows']) == len(TABLE_H[sex]), f'{word}: {len(t["rows"])} rows')
        st = {r['inches']: r for r in S['tables'][sex]}
        for row, h in zip(t['rows'], TABLE_H[sex]):
            rid, hl, cm, *cells = [norm(c) for c in row]
            ok(rid == f'{word.lower()}-{h // 12}-{h % 12}' and hl == hlab(h) and cm == f'{Decimal(h) * Decimal("2.54"):.1f}', f'{word} row head {rid} {hl} {cm}')
            got = calc(pg, h // 12, h % 12, sex=sex)
            want = printed(h, sex)
            for k, n in enumerate(NAMES):
                page_v = (int(cells[2 * k]) if cells[2 * k].isdigit() else cells[2 * k], cells[2 * k + 1])
                stats_v = (st[h][n]['lb'], st[h][n]['kg'])
                ok(page_v == got[n + '_p'] == want[n] == stats_v, f'{word} {hlab(h)} {n}: page {page_v}, calculator {got[n + "_p"]}, formula {want[n]}, stats {stats_v}')
            (lo, hi), (klo, khi) = healthy(h)
            ok(cells[8] == f'{lo}–{hi}' and got['bmi-range'].startswith(f'{lo}–{hi} lbs (') and st[h]['healthy']['lb'] == [lo, hi],
               f'{word} {hlab(h)} healthy lb: page {cells[8]}, calculator {got["bmi-range"]}, rule {lo}–{hi}')
            wb = pg.evaluate('h => { const b = weightBounds(h, 18.5, 24.9); return [b.minKg, b.maxKg]; }', h)
            ok(cells[9] == f'{klo}–{khi}' and wb == [klo, khi] and st[h]['healthy']['kg'] == [klo, khi],
               f'{word} {hlab(h)} healthy kg: page {cells[9]}, weightBounds {wb}, rule {klo}–{khi}')
            ok(got['span'] == span_text(want), f'{word} {hlab(h)} span tile {got["span"]!r} != {span_text(want)!r}')
            ex = exact(h, sex)
            bm = [bmi_r(ex[n][0], h) for n in NAMES]
            lbs = [want[n][0] for n in NAMES]
            summ = (f'For {hq(h)} ({math.floor(h * 2.54 + 0.5)} cm), {sex}, medium frame, the four formulas span {min(lbs)} lbs to {max(lbs)} lbs. '
                    f'At those weights your BMI would be {float(min(bm)):.1f} to {float(max(bm)):.1f}, inside the healthy range of 18.5 to 24.9.')
            ok(summ in got['results'] and Fr(185, 10) <= min(bm) and max(bm) <= Fr(249, 10), f'{word} {hlab(h)} summary: want {summ!r}')
            ok(st[h]['bmi'] == [f'{float(min(bm)):.1f}', f'{float(max(bm)):.1f}'], f'{word} {hlab(h)} stats BMI {st[h]["bmi"]}')
            ok('averag' not in got['results'].lower(), f'{word} {hlab(h)}: "average" in the results')

    # ---- Hamwi at a small and a large frame: only Hamwi changes
    for sex in ('female', 'male'):
        for h in (60, 66, 72):
            med = calc(pg, h // 12, h % 12, sex=sex)
            for fr in ('small', 'large'):
                got = calc(pg, h // 12, h % 12, sex=sex, frame=fr)
                want = printed(h, sex, fr)
                stf = next(r for r in S['frames'][sex] if r['inches'] == h)[fr]
                ok(got['hamwi_p'] == want['hamwi'] == (stf['lb'], stf['kg']), f'{sex} {hlab(h)} {fr}: Hamwi {got["hamwi_p"]}, formula {want["hamwi"]}, stats {stf}')
                ok(all(got[n + '_p'] == med[n + '_p'] for n in ('devine', 'robinson', 'miller')), f'{sex} {hlab(h)} {fr}: a formula other than Hamwi moved')
                others = [f for f in ('small', 'medium', 'large') if f != fr]
                sent = '; '.join(f'for a {f} frame' + (' Hamwi’s weight is ' if i == 0 else ', ') +
                                 f'{printed(h, sex, f)["hamwi"][0]} lbs ({printed(h, sex, f)["hamwi"][1]} kg)' for i, f in enumerate(others))
                ok(('F' + sent[1:] + '.') in got['results'], f'{sex} {hlab(h)} {fr}: frame sentence, want {"F" + sent[1:]!r}')

    # ---- chat's step 1 anchors, typed in as literals (US units unless named)
    g = calc(pg, 5, 6, sex='female')
    ok([g[n] for n in NAMES] == ['130 lbs (59.0 kg)', '131 lbs (59.3 kg)', '131 lbs (59.2 kg)', '135 lbs (61.3 kg)'], f'anchor woman 5′6″ {[g[n] for n in NAMES]}')
    ok(g['span'] == '130–135 lbs (59.0–61.3 kg)' and g['bmi-range'].startswith('115–154 lbs') and 'your BMI would be 21.0 to 21.8' in g['results'], f'anchor woman 5′6″ span/healthy/BMI {g["span"]} {g["bmi-range"]}')
    ok('For 5\'6" (168 cm), female, medium frame, the four formulas span 130 lbs to 135 lbs.' in g['results'], 'the summary pattern hub_examples reads')
    ok('averag' not in g['results'].lower() and g['visible'], 'average in the results / results hidden')
    origins = ('Where the formulas come from Hamwi (1964): desirable body weight in pounds, from an American Diabetes Association book, with a frame rule. '
               'Devine (1974): from an article on gentamicin dosing. Robinson (1983): fitted to the 1959 Metropolitan Life tables. '
               'Miller (1983): fitted to the 1983 Metropolitan Life tables. Pai and Paloucek found Robinson’s and Miller’s equations “strikingly similar” '
               'to Devine’s and concluded that “any one of these equations may be used to estimate IBW” (2000')
    ok(origins in g['results'], 'Where the formulas come from (step 1f)')
    ok(pg.get_attribute('#ideal-results a[href^="https://pubmed"]', 'href') == 'https://pubmed.ncbi.nlm.nih.gov/10981254/', 'Pai and Paloucek link in the results')
    ok('Frame size changes only Hamwi’s number: his rule subtracts 10% for a small frame and adds 10% for a large one. '
       'The Devine, Robinson and Miller equations used here have no frame term.' in g['results'], 'frame note (step 1g)')
    ok(pg.get_attribute('#ideal-results a[href="#frame"]', 'href') == '#frame' and pg.evaluate("!!document.getElementById('frame')"), 'frame link')
    g = calc(pg, 5, 10, sex='male')
    ok([g[n] for n in NAMES] == ['166 lbs (75.3 kg)', '161 lbs (73.0 kg)', '157 lbs (71.0 kg)', '155 lbs (70.3 kg)'], f'anchor man 5′10″ {[g[n] for n in NAMES]}')
    ok(g['span'] == '155–166 lbs (70.3–75.3 kg)' and g['bmi-range'].startswith('129–173 lbs') and 'your BMI would be 22.2 to 23.8' in g['results'], f'anchor man 5′10″ {g["span"]}')
    gl = calc(pg, 5, 10, sex='male', frame='large')
    ok(gl['hamwi'] == '183 lbs (82.8 kg)' and [gl[n] for n in NAMES[1:]] == [g[n] for n in NAMES[1:]], f'anchor man 5′10″ large {gl["hamwi"]}')
    g = calc(pg, 5, 4, sex='female', frame='small')
    ok(g['hamwi'] == '108 lbs (49.0 kg)' and [g[n + '_p'][0] for n in NAMES[1:]] == [121, 123, 129], f'anchor woman 5′4″ small {[g[n] for n in NAMES]}')
    g = calc(pg, 4, 10, sex='female')
    ok(all(g[n] == 'Starts at 5 feet (152.4 cm)' for n in NAMES) and g['span'] == 'Start at 5 feet (152.4 cm)', f'4′10″ tiles {[g[n] for n in NAMES]} {g["span"]}')
    ok(g['bmi-range'] == '89–119 lbs (40.4–54.0 kg)' and healthy(58)[0] == (89, 119), f'4′10″ healthy {g["bmi-range"]}')
    ok('The four formulas start at 5 feet (60 inches), so they give no weight for 4\'10" (147 cm). At that height the healthy BMI range of 18.5 to 24.9 is 89–119 lbs (40.4–54.0 kg).' in g['results'],
       '4′10″ summary')
    ok(not re.search(r'\b\d+ lbs \(\d+\.\d kg\)', g['results'].split('Where the formulas')[0].replace('89–119 lbs (40.4–54.0 kg)', '')), '4′10″ shows a formula weight')
    for cm, sex, want, (klo, khi) in ((160, 'female', ['52.1', '52.4', '54.1', '57.2'], (48, 63)), (170, 'male', ['66.9', '65.9', '65.2', '66.0'], (54, 72)),
                                      (185, 'male', ['83.0', '79.5', '76.4', '74.3'], (64, 85))):
        g = calc(pg, cm=cm, sex=sex)
        ok([g[n + '_p'][1] if g[n + '_p'] else None for n in NAMES] == want == [printed(Fr(cm) / Fr('2.54'), sex)[n][1] for n in NAMES],
           f'anchor metric {cm} cm {sex}: {[g[n] for n in NAMES]}')
        ok(g['bmi-range'].startswith(f'{klo}–{khi} kg (') and healthy(Fr(cm) / Fr('2.54'))[1] == (klo, khi), f'anchor metric {cm} cm healthy {g["bmi-range"]}')
        ok(g['span'] == span_text({n: (g[n + '_p'][0], g[n + '_p'][1]) for n in NAMES}, metric=True), f'metric {cm} cm span {g["span"]}')
    g = calc(pg, cm=147, sex='female')
    ok(all(g[n] == 'Starts at 152.4 cm (5 feet)' for n in NAMES) and g['span'] == 'Start at 152.4 cm (5 feet)', f'147 cm tiles {[g[n] for n in NAMES]}')
    g = calc(pg, cm=152.4, sex='female')
    ok(g['hamwi_p'] == printed(60, 'female')['hamwi'] and g['hamwi_p'] is not None, f'152.4 cm is 5 feet: {g["hamwi"]}')
    pg.click('#panel-ideal .unit-btn[data-unit="imperial"]')

    # ---- where they agree (2d), and the sentences that state it
    def spans(sex):
        return {h: (min(printed(h, sex)[n][0] for n in NAMES), max(printed(h, sex)[n][0] for n in NAMES)) for h in TABLE_H[sex]}
    for sex in ('female', 'male'):
        sp = spans(sex)
        wmin = min(b - a for a, b in sp.values()); wmax = max(b - a for a, b in sp.values())
        nar = [h for h, (a, b) in sp.items() if b - a == wmin]; wid = [h for h, (a, b) in sp.items() if b - a == wmax]
        if sex == 'female':
            ok(nar == [68] and sp[68] == (138, 141) and wid == [60] and sp[60] == (100, 117), f'women narrowest {nar} widest {wid}')
        else:
            ok(nar == [65, 66] and sp[66] == (140, 143) and sp[65] == (136, 139) and wid == [78] and sp[78] == (180, 214), f'men narrowest {nar} widest {wid}')
    bmis = {sex: [bmi_r(lb, h) for h in TABLE_H[sex] for lb, _ in exact(h, sex).values()] for sex in ('female', 'male')}
    ok((float(min(bmis['female'])), float(max(bmis['female'])), float(min(bmis['male'])), float(max(bmis['male']))) == (19.5, 22.9, 20.7, 24.7),
       f'BMI at the four across the tables {[float(min(v)) for v in bmis.values()]} {[float(max(v)) for v in bmis.values()]}')
    bh = norm(pg.inner_text('#by-height'))
    ok('The four come closest at 5′8″ for women (138 to 141 lb) and at 5′5″ and 5′6″ for men (3 lb apart), and split apart toward both ends: '
       '100 to 117 lb for women at 5′0″, 180 to 214 lb for men at 6′6″.' in bh, 'the agree-and-split line')
    fr_ = norm(pg.inner_text('#frame'))
    ok(f'for a 5′6″ woman, {printed(66, "female", "small")["hamwi"][0]} lb small, {printed(66, "female")["hamwi"][0]} lb medium, '
       f'{printed(66, "female", "large")["hamwi"][0]} lb large.' in fr_, 'frame section 5′6″ woman')
    ok('MedlinePlus gives no cut-off for men 5′5″ and shorter.' in fr_ and 'In the calculator, frame size changes only Hamwi’s number.' in fr_, 'frame section lines')

    # ---- the wrist table (MedlinePlus, fact 6) with cm to 0.1 (our conversion)
    WR = pg.evaluate("""() => [...document.querySelectorAll('#frame table tbody tr')].map(r => [r.cells[0].textContent,
        ...[...r.cells].slice(1).flatMap(c => [c.firstChild.textContent, c.querySelector('.unit-alt').textContent])])""")
    WANT_W = [('Women under 5′2″', ('<', '5.5'), ('5.5', '5.75'), ('>', '5.75')), ('Women 5′2″ to 5′5″', ('<', '6'), ('6', '6.25'), ('>', '6.25')),
              ('Women over 5′5″', ('<', '6.25'), ('6.25', '6.5'), ('>', '6.5')), ('Men over 5′5″', ('5.5', '6.5'), ('6.5', '7.5'), ('>', '7.5'))]
    cmc = lambda x: f'{(Decimal(x) * Decimal("2.54")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)}'
    want_rows = []
    for hdr_, *cs in WANT_W:
        r = [hdr_]
        for a, b in cs:
            r += ([f'{a} {b}', f'{a} {cmc(b)}'] if a in '<>' else [f'{a}–{b}', f'{cmc(a)}–{cmc(b)}'])
        want_rows.append(r)
    ok([[norm(c) for c in r] for r in WR] == want_rows, f'wrist table {WR}')
    ok([cmc(x) for x in ('5.5', '5.75', '6', '6.25', '6.5', '7.5')] == ['14.0', '14.6', '15.2', '15.9', '16.5', '19.1'], 'cm conversions')

    # ---- the worked examples
    EX = pg.evaluate("""() => [...document.querySelectorAll('#examples h3')].map(h => [h.textContent, ...[...h.nextElementSibling.children].map(c => c.textContent), h.nextElementSibling.nextElementSibling.textContent])""")
    ok(len(EX) == 2, 'two worked examples')
    for ex, (h, sex, word) in zip(EX, ((66, 'female', 'woman'), (70, 'male', 'man'))):
        over, pr_ = h - 60, printed(h, sex)
        ok(norm(ex[0]).startswith(f'A {hlab(h)} {word}, medium') and norm(ex[0]).endswith(f': {over} inches over 5 feet'), f'example head {ex[0]!r}')
        for k, n in enumerate(NAMES):
            b, pi, u = CONST[sex][n]
            v = Fr(b) + Fr(pi) * over
            vs = f'{Decimal(v.numerator) / Decimal(v.denominator):f}'
            ok(norm(ex[1 + 2 * k]) == f'{LABEL[n]}: {pr_[n][0]} lb ({pr_[n][1]} kg)' and norm(ex[2 + 2 * k]) == f'{b} + {pi} × {over} = {vs} {u}',
               f'example {hlab(h)} {n}: {ex[1 + 2 * k]!r} {ex[2 + 2 * k]!r}')
        (lo, hi), (klo, khi) = healthy(h)
        bm = sorted(bmi_r(lb, h) for lb, _ in exact(h, sex).values())
        lbs = sorted(pr_[n][0] for n in NAMES)
        last = norm(ex[-1])
        ok(last.startswith(f'The four span {lbs[0]} to {lbs[-1]} lb, a BMI of {float(bm[0]):.1f} to {float(bm[-1]):.1f}') and f'{lo} to {hi} lb ({klo} to {khi} kg)' in last,
           f'example {hlab(h)} summary {last!r}')
        if h == 70:
            L = exact(70, 'male', 'large')['hamwi'][0]
            ok(f'166 × 1.1 = 182.6, so {half(L)} lb ({printed(70, "male", "large")["hamwi"][1]} kg), a BMI of {float(bmi_r(L, 70)):.1f}, above that range.' in last
               and bmi_r(L, 70) >= 25, f'large-frame Hamwi {last!r}')

    # ---- the figure against the formulas and the healthy-range rule
    F = pg.evaluate("""() => { const svg = document.querySelector('#by-height figure svg');
        return {vb: svg.getAttribute('viewBox'), lines: [...svg.querySelectorAll('polyline')].map(p => [p.dataset.formula, p.dataset.sex, p.getAttribute('points'), p.getAttribute('stroke'), p.getAttribute('stroke-dasharray')]),
          bands: [...svg.querySelectorAll('polygon')].map(p => [p.dataset.sex, p.getAttribute('points'), p.getAttribute('fill')]),
          keys: [...svg.querySelectorAll('line')].filter(l => +l.getAttribute('y1') === 10).map(l => [l.getAttribute('stroke'), l.getAttribute('stroke-dasharray')]),
          texts: [...svg.querySelectorAll('text')].map(t => [t.textContent, +t.getAttribute('x'), +t.getAttribute('y')]),
          hover: [...svg.querySelectorAll('rect[fill-opacity="0"]')].map(r => r.querySelector('title').textContent),
          colors: [...svg.querySelectorAll('*')].flatMap(e => [e.getAttribute('fill'), e.getAttribute('stroke')]).filter(Boolean),
          title: svg.querySelector('title').textContent, desc: svg.querySelector('desc').textContent,
          cap: svg.parentElement.querySelector('figcaption').textContent} }""")
    K, GAP, LX, YT, YB, LO, HI = 8.0, 30, 34, 64, 232, 90, 220
    X0 = {'female': LX, 'male': LX + 12 * K + GAP}
    STY = {'hamwi': ('#111827', None), 'devine': ('#be185d', '7 4'), 'robinson': ('#0891b2', None), 'miller': ('#b45309', '2.5 2.5')}
    ok(F['vb'] == '0 0 320 270' and len(F['lines']) == 8 and len(F['bands']) == 2, f'figure {F["vb"]}, {len(F["lines"])} lines, {len(F["bands"])} bands')
    for n, sex, pts, stroke, dash in F['lines']:
        ok((stroke, dash) == STY.get(n, (None, None)), f'line {n} {sex} style {stroke} {dash}')
        P = [tuple(map(float, q.split(','))) for q in pts.split()]
        ok(len(P) == len(TABLE_H[sex]), f'line {n} {sex}: {len(P)} points')
        for (x, y), h in zip(P, TABLE_H[sex]):
            inch = (x - X0[sex]) / K + 60
            lb = LO + (YB - y) * (HI - LO) / (YB - YT)
            ok(abs(inch - h) < 0.01 and abs(lb - float(exact(h, sex)[n][0])) < 0.01, f'line {n} {sex} {hlab(h)}: {inch:.2f} in, {lb:.3f} lb')
    for sex, pts, fill in F['bands']:
        P = [tuple(map(float, q.split(','))) for q in pts.split()]
        hs = list(TABLE_H[sex])
        want = [(h, healthy(h)[0][1]) for h in hs] + [(h, healthy(h)[0][0]) for h in reversed(hs)]
        ok(fill == '#d1fae5' and len(P) == len(want) and all(abs((x - X0[sex]) / K + 60 - h) < 0.01 and abs(LO + (YB - y) * (HI - LO) / (YB - YT) - lb) < 0.06
                                                             for (x, y), (h, lb) in zip(P, want)), f'healthy band {sex}')
    ok(F['keys'] == [list(STY[n]) for n in NAMES], f'legend keys {F["keys"]}')
    T_ = {t: (x, y) for t, x, y in F['texts']}
    ok(all(n in T_ for n in LABEL.values()) and 'Healthy BMI range (18.5 to 24.9)' in T_, 'legend names')
    ok(max(T_[n][1] for n in [*LABEL.values(), 'Healthy BMI range (18.5 to 24.9)']) < min(T_['Women'][1], T_['Men'][1]) < YT, 'legend above the panels')
    for v in range(100, HI + 1, 20):
        ok(str(v) in T_ and abs(T_[str(v)][1] - (YB - (v - LO) * (YB - YT) / (HI - LO) + 4)) < 0.06, f'y label {v}')
    xl = [t for t, x, y in F['texts']]
    for sex, hs in (('female', (60, 66, 72)), ('male', (60, 66, 72, 78))):
        for h in hs:
            ok(any(t == hlab(h) and abs(x - (X0[sex] + (h - 60) * K)) < 0.06 for t, x, y in F['texts'])
               and any(t == str(round(h * 2.54)) and abs(x - (X0[sex] + (h - 60) * K)) < 0.06 for t, x, y in F['texts']), f'x labels {sex} {hlab(h)}')
    ok('lb' in xl, 'weight unit label')
    PAL = {'#111827', '#be185d', '#0891b2', '#b45309', '#4b5563', '#e5e7eb', '#9ca3af', '#d1fae5', '#ffffff', 'none'}
    ok(set(c.lower() for c in F['colors']) <= PAL and '#4338ca' not in F['colors'], f'colours outside the palette: {set(F["colors"]) - PAL}')
    hov = []
    for sex in ('female', 'male'):
        for h in TABLE_H[sex]:
            pr_ = printed(h, sex)
            (lo, hi), _ = healthy(h)
            hov.append(f'{hlab(h)} ({Decimal(h) * Decimal("2.54"):.1f} cm), {"women" if sex == "female" else "men"}: '
                       + ', '.join(f'{LABEL[n]} {pr_[n][0]} lb' for n in NAMES) + f'; healthy range {lo}–{hi} lb')
    ok([norm(x) for x in F['hover']] == hov, 'hover titles')
    wsp, msp = spans('female'), spans('male')
    want_desc = (f'Lines for the Hamwi, Devine, Robinson and Miller formulas at a medium frame, in pounds, over the healthy BMI range (18.5 to 24.9) '
                 f'at each height. Women, 5′0″ to 6′0″: {wsp[60][0]} to {wsp[60][1]} lb at 5′0″ (healthy {healthy(60)[0][0]} to {healthy(60)[0][1]} lb) and '
                 f'{wsp[72][0]} to {wsp[72][1]} lb at 6′0″ (healthy {healthy(72)[0][0]} to {healthy(72)[0][1]} lb), closest at 5′8″ ({wsp[68][0]} to {wsp[68][1]} lb). '
                 f'Men, 5′0″ to 6′6″: {msp[60][0]} to {msp[60][1]} lb at 5′0″ and {msp[78][0]} to {msp[78][1]} lb at 6′6″ (healthy {healthy(78)[0][0]} to '
                 f'{healthy(78)[0][1]} lb), closest at 5′5″ and 5′6″, 3 lb apart. Our calculation.')
    ok(norm(F['desc']) == want_desc, f'figure desc {F["desc"]!r}')

    # ---- FAQ: questions, JSON-LD = visible, one tap opens and one closes
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([q for q, _ in visq] == FAQ_Q, f'FAQ questions {[q for q, _ in visq]}')
    ok([[q['name'], q['acceptedAnswer']['text']] for q in GR['FAQPage']['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')
    A = {q: norm(a) for q, a in visq}
    ok(A.get(FAQ_Q[4], '').startswith('The sources here don’t rank them.'), 'FAQ "most accurate" first sentence')
    ok('130 to 135 lb' in A.get(FAQ_Q[0], '') and '115 to 154 lb' in A.get(FAQ_Q[0], ''), 'FAQ 1 numbers')
    ok(all(f'{LABEL[n]} {CONST[s][n][0]} {CONST[s][n][2]} + {CONST[s][n][1]} {CONST[s][n][2]}' in A.get(FAQ_Q[2], '') for s in CONST for n in NAMES)
       and 'more than 200 articles' in A.get(FAQ_Q[2], '') and '60 inches' in A.get(FAQ_Q[2], ''), 'FAQ 3 formulas')
    ok('5th to below the 85th percentile' in A.get(FAQ_Q[8], ''), 'FAQ 9 percentiles')
    for i, q in enumerate(pg.query_selector_all('.faq-question')):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open in one tap')
        q.click(); pg.wait_for_timeout(30)
        ok(not pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not close in one tap')

    # ---- words: nothing from the NEVER WRITE list; no "average" in <main>, the results or the head
    calc(pg, 5, 6)
    faq_t = ' '.join(a for _, a in visq)
    allw = (norm(pg.evaluate("document.querySelector('main').textContent")) + ' ' + faq_t + ' ' + ' '.join(str(v) for v in head.values())
            + ' ' + json.dumps(ld, ensure_ascii=False) + ' ' + norm(src[:src.index('</head>')]))
    allw = allw.replace('Which ideal weight formula is the most accurate?', '')
    for pat in NEVER:
        hit = re.search(pat, allw, 0 if pat in CASE else re.I)
        ok(not hit, f'banned wording: {hit.group(0) if hit else ""!r} ({pat})')
    ok(not re.search(r'\bNormal\b', allw), 'Normal as a category name')

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
    ok(len(outside) == 9, f'{len(outside)} outside links: {sorted(outside)}')
    ok(all(pg.evaluate('h => [...document.querySelectorAll(`main a[href="${h}"]`)].every(a => a.target === "_blank" && a.rel === "noopener")', h_) for h_ in outside),
       'outside links open in a new tab')
    for h_ in ('/bmi-chart/', '/blog/bmi-chart-women/', '/blog/bmi-chart-men/', '/lean-body-mass/', '/body-fat-calculator/'):
        ok(pg.evaluate('h => !!document.querySelector(`#healthy-range a[href="${h}"]`)', h_), f'#healthy-range does not link {h_}')
    ok(pg.evaluate("!!document.querySelector('#faq a[href=\"/age-bmi-calculator/\"]') && !!document.querySelector('#faq a[href=\"/kids-bmi-calculator/\"]')"), 'FAQ links')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#formulas', '#by-height', '#frame', '#examples', '#healthy-range', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    ok(pg.evaluate("document.querySelectorAll('main .related-cols').length") == 1, 'one related block')

    # ---- labels: each names the expected field, and a click on it focuses that field (US units and metric)
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(50)
    fors = pg.eval_on_selector_all('main label', 'ls => ls.map(l => l.htmlFor)')
    ok(sorted(fors) == sorted(LABEL_IDS), f'labels name {fors}')
    seen = set()
    for unit in ('imperial', 'metric'):
        pg.click(f'.unit-btn[data-unit="{unit}"]'); pg.wait_for_timeout(20)
        for f in fors:
            if not pg.evaluate('f => { const c = document.getElementById(f); return !!c && c.offsetParent !== null; }', f): continue
            pg.evaluate('() => document.activeElement && document.activeElement.blur()')
            pg.click(f'label[for="{f}"]')
            ok(pg.evaluate('() => document.activeElement && document.activeElement.id') == f, f'clicking the label for {f} does not focus it')
            seen.add(f)
    ok(seen == set(LABEL_IDS), f'labels never shown: {sorted(set(LABEL_IDS) - seen)}')

    # ---- widths before and after Calculate, the fold, table frames, rendered labels
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 844}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
        if w in (360, 390):
            bottom = pg.evaluate("document.querySelector('#calc-ideal-btn').getBoundingClientRect().bottom")
            ok(bottom <= 844, f'Calculate below the fold at {w} ({bottom})')
        for when in ('before', 'after'):
            if when == 'after':
                pg.click('#calc-ideal-btn'); pg.wait_for_timeout(120)
                ok(pg.evaluate("getComputedStyle(document.getElementById('ideal-results')).display") != 'none', f'results hidden at {w}')
                txt = pg.inner_text('#ideal-results')
                ok('NaN' not in txt and 'undefined' not in txt and 'Infinity' not in txt, f'NaN/undefined in the results at {w}')
            sw = pg.evaluate('document.documentElement.scrollWidth')
            ok(sw <= w, f'page {sw}px wide at {w} {when} Calculate')
            fits = pg.evaluate("""() => [...document.querySelectorAll('main table')].filter(t => t.offsetParent !== null)
                .map(t => [t.caption ? t.caption.textContent : t.className, t.offsetWidth, t.parentElement.clientWidth,
                           getComputedStyle(t.parentElement).overflowX, t.parentElement.getBoundingClientRect().right])""")
            ok(len(fits) == 4, f'{len(fits)} tables at {w}')
            for cap, tw, fw, ovf, right in fits:
                if w >= 360:
                    ok(tw <= fw + 1, f'table wider than its frame at {w} {when} Calculate: {cap} {tw} > {fw}')
                else:                                        # 320: a table may scroll inside its frame, the page never does
                    ok(tw <= fw + 1 or (ovf == 'auto' and right <= w + 0.5), f'table outside a scrolling frame at {w}: {cap} {tw} > {fw} ({ovf})')
        res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
            const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
            const ctm = svg.getScreenCTM(), pt = svg.createSVGPoint();
            const curves = [...svg.querySelectorAll('polyline, polygon')].map(pl => [[...pl.points].map(q => { pt.x = q.x; pt.y = q.y; const s = pt.matrixTransform(ctm); return [s.x, s.y]; }), pl.tagName === 'polygon']);
            return {box: [r.left, r.top, r.right, r.bottom], scale: ctm.a, curves,
                    texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                    shapes: [...svg.querySelectorAll('rect, circle, line')].map(e => [e.tagName + ' ' + (e.getAttribute('fill') || e.getAttribute('stroke')), ...bx(e)])}; })""")
        ok(len(res) == 1, f'{len(res)} figures at {w}')
        for f_ in res:
            L_, T0, R_, B_ = f_['box']
            halfw = 1.0 * f_['scale']                                                # half the 2-unit stroke, on screen
            for j, a in enumerate(f_['texts']):
                ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T0 - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                for c2 in f_['texts'][j + 1:]:
                    ok(not (a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5), f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                for s_ in f_['shapes']:
                    ok(not (a[1] < s_[3] - 0.5 and s_[1] < a[3] - 0.5 and a[2] < s_[4] - 0.5 and s_[2] < a[4] - 0.5), f'{w}px label over a shape: {a[0]!r} / {s_[0]}')
                for line, closed in f_['curves']:
                    hit = False
                    for (x1, y1), (x2, y2) in zip(line, line[1:] + (line[:1] if closed else [])):
                        steps = max(1, int(math.hypot(x2 - x1, y2 - y1) / 0.5))
                        for k in range(steps + 1):
                            x, y = x1 + (x2 - x1) * k / steps, y1 + (y2 - y1) * k / steps
                            if a[1] - halfw < x < a[3] + halfw and a[2] - halfw < y < a[4] + halfw: hit = True
                    ok(not hit, f'{w}px label on a plotted line or band: {a[0]!r}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures, {skipped} skipped')
for f_ in fails[:40]: print('FAIL', f_)
sys.exit(1 if fails or skipped else 0)
