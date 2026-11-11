#!/usr/bin/env python3
"""/kids-bmi-calculator/ checks in Chromium (CMB-030). Needs Python Playwright + Chromium.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/kids-build/kids_test_playwright.py http://localhost:8000 research/kids-build/kids_stats.json
  - the tables: every cell equals kids_stats.json; for every age 2 to 19 and both sexes, in metric at 150 cm, weights
    giving a BMI 0.06 below and 0.06 above each of the four cut-off columns (5th, 85th, 95th, 120% of the 95th) land in
    the categories either side of it in the real calculator, at that age in whole years (the low side of a 120% value
    above 35 is skipped: the BMI 35 rule decides there, and that is checked as its own case);
  - the calculator: chat's step 1 anchors typed in as literals (US units); CDC's two examples through
    computeKidsPercentile(); the American Academy of Pediatrics' class line under severe obesity at 126.8% (class 2),
    at 140% or more (class 3), at BMI 40 or more under 140% (class 3) and at BMI 35 to 40 under 120% (class 2), gone
    again after a result that isn't severe obesity; getLMSRow() reads floor(age in months) + 0.5 at every age;
  - the worked examples, the age example and every number sentence in the takeaways, FAQ and sections against
    kids_stats.json, the two examples chat typed in also typed in here;
  - the figure: every band and band-edge point against kids_stats.json, the tints, the legend above the panels, the
    axis labels, the hover titles, the description; rendered labels stay inside the figure, off each other, off every
    shape and out of the plot areas;
  - labels: each names the expected field and a click on it focuses that field, in US units and in metric;
  - Calculate ends above the fold at 360 x 800 and 390 x 844; the page is never wider than the screen at 320, 360, 390
    and 1280, before and after Calculate; tables fit their frames (at 320 a table may scroll inside a frame that stays
    on the screen);
  - 9 FAQ in order, the JSON-LD equal to the visible answers, one tap opens an answer and one closes it;
  - sections sit directly in main .container, no <article>, no page-level style, no inline style in <main> outside the
    figure; the head's scripts other than JSON-LD, the header and everything after </main> equal origin/main's; the
    title, meta description, H1, byline, OG and Twitter text kept;
  - head: OG and Twitter images, the JSON-LD graph, the preferred images, the old OG image gone;
  - internal links answer 200, anchors exist, outside links are registry URLs; nothing from the prompt's NEVER WRITE
    list on the page, in the head or in the calculator's new line.
Every check runs; nothing is skipped. Exit 1 on any failure."""
import sys, os, json, math, re, csv, struct, subprocess
from decimal import Decimal, ROUND_HALF_UP
from statistics import NormalDist
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1].rstrip('/'), sys.argv[2]
BUILD = os.path.dirname(os.path.abspath(stats))
ROOT = os.path.abspath(os.path.join(BUILD, '..', '..'))
S = json.load(open(stats, encoding='utf-8'))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()}
URL = base + '/kids-bmi-calculator/'
SITE = 'https://calculatemybmi.net'
N = NormalDist()

fails, checks, skipped = [], 0, 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

def norm(t):
    t = (t or '').replace(' ', ' ').replace('­', '').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', t).strip()
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def d1(x): return str(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def ordinal(n):
    v = n % 100
    return f'{n}' + ({1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') if not 11 <= v <= 13 else 'th')

T = {sex: {r['age']: r for r in rows} for sex, rows in S['tables'].items()}
A = S['anchors']
EX = S['examples']
MED = S['medians']
AGE_EX = S['age_example']
COLS = ('p5', 'p50', 'p85', 'p95', 'p120')
TITLE = 'BMI Calculator for Kids & Teens (Ages 2–19): CDC Percentile'
H1 = 'BMI Calculator for Kids and Teens'
PI = {r: f'{SITE}/assets/images/preferred/kids-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
FAQ_Q = ['What is a healthy BMI for a child?', 'How is BMI calculated for a child?', 'What does a BMI percentile mean?',
         'What are the 85th and 95th percentiles?', 'What is severe obesity in children?', 'What is a BMI z-score?',
         "Why does my child's BMI change as they grow?", 'Can I use adult BMI categories for my teenager?',
         'What ages does this calculator cover?']
LABEL_IDS = ['kids-height-ft', 'kids-height-in', 'kids-weight-lbs', 'kids-height-cm', 'kids-weight-kg', 'kids-age-years',
             'kids-age-months', 'kids-sex']
# The prompt's NEVER WRITE list, as patterns over the page, the head, the JSON-LD and the calculator's new line
NEVER = [r'blood pressure', r'cholesterol', r'diabetes', r'asthma', r'apnea', r'fatty liver', r'gallstone', r'reflux', r'anxiety',
         r'depression', r'self-esteem', r'bully', r'stigma', r'insulin', r'glucose', r'heart disease', r'joint problems',
         r'linked to', r'\bcauses?\b', r'contributing factors', r'genetic', r'screen time', r'\bdiet', r'physical activity',
         r'\bexercis', r'\bsleep', r'calori', r'\bnutrition', r'60 minutes', r'Paruthi', r'Academy of Sleep',
         r'Physical Activity Guidelines', r'odphp', r'\bdoctor', r'pediatrician', r'Official guidance', r'talk (?:to|with) your',
         r'(?:BMI|percentile)[^.]{0,40}\b(?:measures?|shows?|tells? you)\b[^.]{0,30}\bbody fat', r'measures? body fat',
         r'\bpredict', r'as adults', r'adult(?:hood)? (?:obesity|weight)', r'\bnormal weight\b', r'\bnormal BMI\b', r'\bnormal range\b',
         r'class 1 obesity', r'18\.5\s*(?:to|–|-)\s*(?:24\.9|25)', r'\b25\s*(?:to|–|-)\s*29\.9', r'\b30\s*(?:to|–|-)\s*34\.9',
         r'healthy (?:BMI )?range for (?:wo)?men', r'older adults',
         r'2022[^.]{0,80}\b(?:changed|updated|revised|replaced)\b[^.]{0,60}\b(?:below|under|5th|50th|85th)\b',
         r'What childhood obesity is linked to', r'When to talk']
CASE = set()


def git_main(path):
    return subprocess.run(['git', '-C', ROOT, 'show', f'origin/main:{path}'], capture_output=True, text=True, check=True).stdout


def head_scripts(src):
    head = src[:src.index('</head>')]
    return [s for s in re.findall(r'(?s)<script\b[^>]*>.*?</script>', head) if 'application/ld+json' not in s]


def meta_content(src, attr, name):
    return re.findall(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)">', src)


RESULT_JS = """() => {
  const t = id => { const e = document.getElementById(id); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
  const metrics = {};
  document.querySelectorAll('#kids-results .er-metric').forEach(m => {
    metrics[m.querySelector('.er-metric-label').textContent.trim()] =
      [m.querySelector('.er-metric-value').textContent.trim(), m.querySelector('.er-metric-sub').textContent.trim()]; });
  const card = document.getElementById('kids-result-card');
  const kids = [...card.children].map(e => e.id);
  return {bmi: t('kids-bmi-value'), cat: t('kids-bmi-category'), line: t('kids-percentile-note'), aap: t('kids-aap-class'),
          kids, metrics, visible: getComputedStyle(document.getElementById('kids-results')).display !== 'none',
          text: document.getElementById('kids-results').textContent};
}"""


def calc(pg, sex, years, months, ft=None, inch=None, lb=None, cm=None, kg=None):
    """Types an entry into the page's calculator, presses Calculate and reads what it prints."""
    unit = 'metric' if cm is not None else 'imperial'
    pg.click(f'#panel-kids .unit-btn[data-unit="{unit}"]')
    if unit == 'imperial':
        pg.fill('#kids-height-ft', str(ft)); pg.fill('#kids-height-in', str(inch)); pg.fill('#kids-weight-lbs', str(lb))
    else:
        pg.fill('#kids-height-cm', str(cm)); pg.fill('#kids-weight-kg', str(kg))
    pg.fill('#kids-age-years', str(years)); pg.fill('#kids-age-months', str(months)); pg.select_option('#kids-sex', sex)
    pg.click('#calc-kids-btn')
    return pg.evaluate(RESULT_JS)


with sync_playwright() as p:
    br = p.chromium.launch(args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 1280, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())     # no ads or analytics
    resp = pg.goto(URL, wait_until='load')
    ok(resp.status == 200, f'page status {resp.status}')
    src = pg.request.get(URL).text()
    orig = git_main('kids-bmi-calculator/index.html')

    # ---- the page as served: kept parts, structure, no inline style, no <article>
    ok(head_scripts(src) == head_scripts(orig) and len(head_scripts(orig)) == 3, 'head scripts other than JSON-LD differ from origin/main')
    hdr = lambda s: re.search(r'(?s)<header class="header">.*?</header>', s).group(0)
    ok(hdr(src) == hdr(orig), 'the header differs from origin/main')
    ok(src[src.index('</main>'):] == orig[orig.index('</main>'):], 'the scripts and footer after </main> differ from origin/main')
    htitle = lambda s: re.findall(r'<title>[^<]*</title>', s[:s.index('</head>')])
    ok(htitle(src) == htitle(orig) and len(htitle(src)) == 1 and pg.title() == TITLE, f'title {pg.title()!r}')
    for attr, name in (('name', 'description'), ('property', 'og:title'), ('property', 'og:description'), ('name', 'twitter:title'),
                       ('name', 'twitter:description'), ('property', 'og:url'), ('property', 'og:type'), ('name', 'twitter:card'),
                       ('property', 'og:image:width')):
        ok(meta_content(src, attr, name) == meta_content(orig, attr, name) and len(meta_content(src, attr, name)) == 1, f'{name} changed')
    ok(pg.inner_text('h1') == H1 and src.count('<h1') == 1, 'H1')
    by_new = norm(pg.inner_text('.byline'))
    by_old = norm(re.sub(r'<[^>]+>', '', re.search(r'<p class="byline"[^>]*>(.*?)</p>', orig).group(1)).replace('&middot;', '·'))
    ok(by_new == by_old == 'Written by Marko Visic, MPharm · Not medical advice', f'byline {by_new!r} / {by_old!r}')
    mains = src[src.index('<main'):src.index('</main>')]
    ok('<style' not in src and '<article' not in src and pg.evaluate("document.querySelectorAll('article').length") == 0, 'page-level style or <article>')
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>', '', mains), 'inline style in <main> outside figures')
    ok(mains.startswith('<main class="reading"><div class="container">'), 'reading column')
    blocks = pg.evaluate("""() => [...document.querySelector('main > .container').children].map(e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + '.' + [...e.classList].join('.'))""")
    ok(blocks == ['div.page-head', 'div.calculator-card', 'div.key-takeaways', 'div.disclaimer-box', 'nav.toc-inline',
                  'section#categories.content-section.flow', 'section#chart.content-section.flow', 'section#how.content-section.flow',
                  'section#examples.content-section.flow', 'section#age.content-section.flow', 'section#prevalence.content-section.flow',
                  'section#faq.content-section', 'section#sources.content-section.flow', 'section.content-section'], f'blocks in main .container: {blocks}')
    ok(pg.evaluate("[...document.querySelectorAll('main section')].every(s => s.parentElement.matches('main > .container'))"),
       'a section is not a direct child of main .container')
    words = pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, script, style, #kids-results').forEach(e => e.remove()); return m.textContent.split(/\\s+/).filter(Boolean).length; }""")
    ok(1500 <= words <= 2300, f'{words} words in main')
    body_text = pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, #kids-results').forEach(e => e.remove()); return m.textContent; }""")
    ok('—' not in body_text, 'em dash in the body (the result placeholders aside)')
    ids = ['panel-kids', 'calc-kids-btn', 'kids-results', 'kids-result-card', 'kids-bmi-value', 'kids-bmi-category', 'kids-percentile-note', *LABEL_IDS]
    ok(all(src.count(f'id="{i}"') == 1 and orig.count(f'id="{i}"') == 1 for i in ids), 'a kept calculator id is missing')
    start = pg.evaluate("['kids-height-ft', 'kids-height-in', 'kids-height-cm', 'kids-weight-lbs', 'kids-weight-kg', 'kids-age-years', 'kids-age-months', 'kids-sex'].map(i => document.getElementById(i).value)")
    ok(start == ['4', '6', '137', '70', '32', '10', '0', 'female'], f'starting values {start}')
    opts = pg.evaluate("[...document.querySelectorAll('#kids-sex option')].map(o => o.value)")
    ok(opts == ['female', 'male'], f'sex option values {opts}')
    ok(pg.evaluate("document.querySelector('#panel-kids .metric-inputs').hidden && !document.querySelector('#panel-kids .imperial-inputs').hidden"), 'metric row starts hidden')

    # ---- head and JSON-LD
    head = pg.evaluate("""() => ({robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content), canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content), ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content), desc: document.querySelector('meta[name="description"]').content})""")
    ok(head['robots'] == ['max-image-preview:large'] and head['canon'] == SITE + '/kids-bmi-calculator/', 'robots / canonical')
    ok(head['og'] == [PI['16x9']] and head['tw'] == [PI['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'OG / Twitter image {head}')
    ok(head['ogalt'].startswith('Chart: CDC BMI-for-age bands for boys and girls') and '"' not in head['ogalt'], 'og:image:alt')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/kids-bmi-calculator-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/assets/images/og/kids-boys-percentile.png').status == 404, 'old OG image still served')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['WebPage', 'WebApplication', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    GR = {x['@type']: x for x in ld[0]['@graph']}
    ok(GR['WebPage']['primaryImageOfPage']['url'] == PI['16x9'] and GR['WebPage']['name'] == TITLE, 'WebPage')
    ok(GR['WebApplication']['image'] == [PI['1x1'], PI['4x3'], PI['16x9']] and GR['WebApplication']['author']['name'] == 'Marko Visic'
       and GR['WebApplication']['name'] == H1, 'WebApplication image list / author / name')
    ok([i['name'] for i in GR['BreadcrumbList']['itemListElement']] == ['Home', 'Calculators', H1], 'breadcrumb')

    # ---- the fixed text: intro, takeaways (chat's words), disclaimer (the men page's, verbatim)
    ok(norm(pg.inner_text('.intro-text')) == "Enter your child's age, sex, height and weight to get their BMI-for-age percentile and CDC weight category.", 'intro text')
    ok(norm(pg.inner_text('.intro-note')) == "For ages 2 through 19, with CDC's BMI-for-age growth charts. Method and sources"
       and pg.get_attribute('.intro-note a', 'href') == '#sources', 'intro note')
    kt = pg.evaluate("() => [document.querySelector('.key-takeaways .answer').textContent, ...[...document.querySelectorAll('.key-takeaways li')].map(l => l.textContent)]")
    ok([norm(x) for x in kt] == [
        "A child's BMI is worked out the same way as an adult's, then compared with CDC's BMI-for-age charts for the child's sex and age in months. The percentile sets the category: under the 5th is underweight, the 5th to below the 85th healthy weight, the 85th to below the 95th overweight, and the 95th or above obesity.",
        'Severe obesity is a BMI at or above 120% of the 95th percentile, or 35 or more. The American Academy of Pediatrics splits it into class 2 (120% to under 140%) and class 3 (140% or more).',
        'The same BMI means different things at different ages: 23.6 is in the adult healthy range, but for a 10-year-old girl it sits at the 96th percentile, which is obesity.',
        "Up to the 95th percentile the charts are CDC's 2000 growth charts; above it, CDC's 2022 extended charts give percentiles up to the 99.99th.",
        "In CDC's measured survey for August 2021–August 2023, 21.1% of children and teens aged 2–19 had obesity."], f'key takeaways {kt}')
    ok(A['girl-10-98']['bmi'] == '23.6' and A['girl-10-98']['ordinal'] == 96 and A['girl-10-98']['category'] == 'Obesity', 'takeaway 23.6 against the stats')
    men = pg.request.get(base + '/men-bmi-calculator/').text()
    disc = lambda s: re.search(r'(?s)<div class="disclaimer-box">.*?</div>', s).group(0)
    ok(disc(src) == disc(men), 'disclaimer is not the men page wording')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#categories', '#chart', '#how', '#examples', '#age', '#prevalence', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    h2 = pg.evaluate("[...document.querySelectorAll('main section > h2')].map(h => h.textContent)")
    ok(h2 == ['CDC BMI categories for children and teens', 'BMI-for-age charts for boys and girls', 'How the calculator works',
              'Four worked examples', 'How BMI changes with age', 'How common obesity is in children', 'Frequently asked questions',
              'Sources and method', 'Related calculators and guides'], f'section headings {h2}')

    # ---- categories (fact 2)
    cat = pg.evaluate("""() => [...document.querySelectorAll('#categories table tbody tr')].map(r => [r.cells[0].textContent, r.cells[0].querySelector('.cat-dot').className, r.cells[1].textContent])""")
    ok([[norm(a), b, norm(c)] for a, b, c in cat] == [
        ['Underweight', 'cat-dot underweight', 'Less than the 5th percentile'],
        ['Healthy weight', 'cat-dot normal', '5th percentile to less than the 85th percentile'],
        ['Overweight', 'cat-dot overweight', '85th to less than the 95th percentile'],
        ['Obesity', 'cat-dot obese', '95th percentile or greater'],
        ['Severe obesity', 'cat-dot obese-severe', '120% of the 95th percentile or greater, or a BMI of 35 or greater']], f'category table {cat}')
    ctext = norm(pg.inner_text('#categories'))
    ok('Class 2 obesity: 120% to less than 140% of the 95th percentile, or a BMI of 35 to less than 40.' in ctext
       and 'Class 3 obesity: 140% of the 95th percentile or greater, or a BMI of 40 or greater.' in ctext, 'AAP classes')
    ok('"the American Academy of Pediatrics uses an expanded definition of severe obesity,"' in ctext, 'AAP quote')
    ok('"Race is not a factor used in calculating BMI percentiles."' in ctext, 'race quote')

    # ---- the tables: every cell = kids_stats.json
    TB = pg.evaluate("""() => [...document.querySelectorAll('#chart table')].map(t => ({cap: t.caption.textContent, cls: t.className,
        head: [...t.querySelectorAll('thead th')].map(c => c.textContent),
        rows: [...t.querySelectorAll('tbody tr')].map(r => [r.id, ...[...r.cells].map(c => c.textContent)])}))""")
    ok(len(TB) == 2, f'{len(TB)} birthday tables')
    for t, sex, word in zip(TB, ('male', 'female'), ('Boys', 'Girls')):
        ok(norm(t['cap']) == f'{word}: BMI at each percentile, ages 2 to 19', f'caption {t["cap"]!r}')
        ok([norm(c) for c in t['head']] == ['Age', '5th', '50th', '85th', '95th', '120% of 95th'], f'{word} head {t["head"]}')
        ok('data-table--fit' in t['cls'] and 'data-table--tight' in t['cls'], f'{word} table classes {t["cls"]}')
        ok([r[1] for r in t['rows']] == [str(a) for a in range(2, 20)], f'{word} ages')
        for row in t['rows']:
            age = int(row[1])
            want = [T[sex][age][k] for k in COLS]
            ok(row[0] == f'{word.lower()}-{age}' and [norm(c) for c in row[2:]] == want, f'{word} {age}: page {row[2:]}, stats {want}')
    ok(T['male'][10]['p5'] == '14.2' and T['female'][19]['p120'] == '37.2', 'stats spot values')
    chart_t = norm(pg.inner_text('#chart'))
    ok('each row is the month that starts at the birthday' in chart_t and chart_t.count('starts at the birthday') == 1, 'the birthday-row line, once')
    ok(pg.evaluate("document.querySelector('#chart .source-note').textContent.startsWith('Source:')")
       and pg.get_attribute('#chart .source-note a', 'href') == 'https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm', 'table source line')
    over35 = sorted((s, a) for s in ('male', 'female') for a in range(2, 20) if Decimal(T[s][a]['p120']) > 35)
    ok(over35 == [('female', 17), ('female', 18), ('female', 19), ('male', 19)] and '(boys at 19, girls from 17)' in chart_t, f'120% above 35: {over35}')

    # ---- the cut-offs in the real calculator: 0.06 either side of each table value, in metric at 150 cm, whole years
    SIDE = {'p5': ('Underweight', 'Healthy weight'), 'p85': ('Healthy weight', 'Overweight'), 'p95': ('Overweight', 'Obesity'),
            'p120': ('Obesity', 'Severe obesity')}
    for sex in ('male', 'female'):
        for age in range(2, 20):
            for k, (below, above) in SIDE.items():
                v = Decimal(T[sex][age][k])
                for side, want in ((-1, below), (1, above)):
                    b = float(v) + side * 0.06
                    if k == 'p120' and side < 0 and v > 35:
                        ok(b >= 35, f'{sex} {age}: the BMI 35 rule decides below 120% ({v})')
                        continue
                    g = calc(pg, sex, age, 0, cm=150, kg=f'{b * 2.25:.4f}')
                    ok(g['cat'] == want, f'{sex} {age} {k} {v}: BMI {b:.2f} gives {g["cat"]}, want {want}')
    for sex, age, bmi, want, aap in (('female', 19, 36.0, 'Severe obesity', 'class 2'), ('male', 19, 35.3, 'Severe obesity', 'class 2'),
                                     ('female', 19, 34.9, 'Obesity', None), ('female', 19, 41.0, 'Severe obesity', 'class 3')):
        g = calc(pg, sex, age, 0, cm=150, kg=f'{bmi * 2.25:.4f}')
        want_aap = f'The American Academy of Pediatrics calls this {aap} obesity.' if aap else None
        ok(g['cat'] == want and g['aap'] == want_aap, f'{sex} {age} BMI {bmi}: {g["cat"]} / {g["aap"]}, want {want} / {want_aap}')

    # ---- chat's step 1 anchors, typed in as literals (US units)
    def metric(g, label):
        return g['metrics'].get(label, [None, None])
    for name, (sex, y, mo, ft, inch, lb), want in (
            ('girl 10y 4′6″ 70 lb', ('female', 10, 0, 4, 6, 70), ('16.9', '50th percentile for girls aged 10 years', '50.2', 'Healthy weight', '73.4%')),
            ('girl 10y 4′6″ 98 lb', ('female', 10, 0, 4, 6, 98), ('23.6', '96th percentile for girls aged 10 years', '95.6', 'Obesity', '102.8%')),
            ('boy 14y6m 5′5″ 150 lb', ('male', 14, 6, 5, 5, 150), ('25.0', '92nd percentile for boys aged 14 years 6 months', '92.1', 'Overweight', None)),
            ('girl 16y 5′4″ 190 lb', ('female', 16, 0, 5, 4, 190), ('32.6', '97th percentile for girls aged 16 years', '97.2', 'Obesity', '112.8%')),
            ('boy 2y0m 2′10″ 32 lb', ('male', 2, 0, 2, 10, 32), ('19.5', '96th percentile for boys aged 2 years', '95.5', 'Obesity', '100.9%'))):
        g = calc(pg, sex, y, mo, ft=ft, inch=inch, lb=lb)
        got = (g['bmi'], g['line'], metric(g, 'Percentile')[0], g['cat'], metric(g, '% of 95th percentile')[0] if want[4] else None)
        ok(got == want and g['aap'] is None and g['visible'], f'anchor {name}: {got} want {want} (AAP {g["aap"]})')
    a2 = A['boy-2-32']
    ok(a2['percentile'] == '95.5' and a2['percentile_with_24_0_row'] == '95.4', 'stats: the 2-year-old with the 24.5 and the 24.0 row')
    for name, a in A.items():
        g = calc(pg, a['sex'], a['years'], a['months'], ft=a['ft'], inch=a['in'], lb=a['lb'])
        ok((g['bmi'], metric(g, 'Percentile')[0], g['cat'], metric(g, '% of 95th percentile')[0], metric(g, 'Percentile')[1])
           == (a['bmi'], a['percentile'], a['category'], a['pct_of_p95'] + '%', 'z = ' + a['z']), f'stats anchor {name} differs from the calculator')
    # CDC's two examples through computeKidsPercentile()
    cg = pg.evaluate("(() => { const r = computeKidsPercentile(21.2, 114, 'female'); return [r.percentile.toFixed(1), r.z.toFixed(4), r.row.P95, categorizeChildBMI(21.2, r.percentile, r.pctP95).category]; })()")
    ok(cg == ['92.2', '1.4215', 22.3979, 'Overweight'], f'CDC girl {cg}')
    cb = pg.evaluate("(() => { const r = computeKidsPercentile(22.6, 50, 'male'); return [r.percentile.toFixed(2), r.percentile.toFixed(4), r.pctP95.toFixed(1), r.row.P95, r.row.sigma, categorizeChildBMI(22.6, r.percentile, r.pctP95).category]; })()")
    ok(cb == ['99.77', '99.7683', '126.8', 17.8219, 2.398288, 'Severe obesity'], f'CDC boy {cb}')
    # the AAP line: CDC's boy typed in (100 cm, 22.6 kg: BMI 22.6), then 140% or more, then a result that isn't severe obesity
    g = calc(pg, 'male', 4, 2, cm=100, kg='22.6')
    ok(g['cat'] == 'Severe obesity' and g['aap'] == 'The American Academy of Pediatrics calls this class 2 obesity.'
       and metric(g, '% of 95th percentile')[0] == '126.8%' and g['kids'][:4] == ['kids-bmi-value', 'kids-bmi-category', 'kids-aap-class', 'kids-percentile-note'],
       f'AAP class 2 at 126.8%: {g["cat"]} / {g["aap"]} / {g["kids"]}')
    g = calc(pg, 'female', 10, 0, ft=4, inch=6, lb=140)
    ok(g['cat'] == 'Severe obesity' and g['aap'] == 'The American Academy of Pediatrics calls this class 3 obesity.'
       and float(metric(g, '% of 95th percentile')[0].rstrip('%')) >= 140, f'AAP class 3 at 140% or more: {g["aap"]} {metric(g, "% of 95th percentile")}')
    aap_lines = [g['aap']]
    g = calc(pg, 'female', 10, 0, ft=4, inch=6, lb=70)
    ok(g['aap'] is None and 'kids-aap-class' not in g['kids'] and 'American Academy' not in g['text'], 'AAP line left after a healthy result')
    # getLMSRow reads floor(age in months) + 0.5 at every age, the 24.0 row stays in the data and goes unused
    rows_read = pg.evaluate("""(() => { const out = []; for (const sex of ['male', 'female']) for (let m = 24; m < 240; m++) {
        const d = sex === 'male' ? window.CDC_BMI_LMS.boys : window.CDC_BMI_LMS.girls, r = getLMSRow(sex, m), i = d.agemos.indexOf(m + 0.5);
        out.push(r.M === d.M[i] && r.L === d.L[i] && r.S === d.S[i] && r.P95 === d.P95[i]); } return [out.every(Boolean), out.length,
        window.CDC_BMI_LMS.boys.agemos.includes(24)]; })()""")
    ok(rows_read == [True, 432, True], f'getLMSRow at floor + 0.5 for 24-239 months: {rows_read}')

    # ---- the worked examples and the number sentences against kids_stats.json (and typed in)
    ex_t = norm(pg.inner_text('#examples'))
    cgx, cbx, g98, b14 = EX['cdc_girl'], EX['cdc_boy'], EX['girl_10_98'], EX['boy_14_6_150']
    sb, sg, s14 = cbx['steps'], g98['steps'], b14['steps']
    want_sents = [
        "CDC's example: a girl of 9 years 6 months, BMI 21.2",
        f"Her row is {cgx['row']} months, where the 95th percentile is {cgx['p95']}.",
        f"CDC works it out to a z-score of {cgx['z4']}, the {cgx['percentile']}nd percentile.",
        f"the calculator shows the {ordinal(cgx['ordinal'])} percentile and z = {cgx['z']}.",
        "CDC's example: a boy of 4 years 2 months, BMI 22.6",
        f"His row is {cbx['row']} months: the 95th percentile is {sb['p95']} and sigma {sb['sigma']}.",
        f"(22.6 − {sb['p95']}) ÷ {sb['sigma']} = {sb['arg4']}, Φ({sb['arg4']}) = {sb['phi5']}, and 90 + 10 × {sb['phi5']} = {cbx['percentile4']}, the {cbx['percentile4']}rd percentile.",
        f"A BMI of 22.6 is {cbx['pct_of_p95']}% of his row's 95th percentile, over the 120% line, so the category is severe obesity, which the American Academy of Pediatrics calls class 2 obesity (120% to under 140%).",
        f"A 10-year-old girl, 4′6″ and 98 lb",
        f"Her BMI is 703 × 98 ÷ 54² = {g98['bmi_exact2']}, shown as {g98['bmi']}.",
        f"her row is {g98['row']} months, where the 95th percentile is {sg['p95']} ({g98['p95_1dp']} in the table) and sigma {sg['sigma']}.",
        f"90 + 10 × Φ(({g98['bmi_exact2']} − {sg['p95']}) ÷ {sg['sigma']}) gives {g98['percentile']}, the {ordinal(g98['ordinal'])} percentile, which is obesity.",
        f"Her BMI is {g98['pct_of_p95']}% of the 95th percentile, short of the 120% that would make it severe obesity.",
        "A boy of 14 years 6 months, 5′5″ and 150 lb",
        f"His BMI is 703 × 150 ÷ 65² = {b14['bmi_exact2']}, shown as {b14['bmi']}.",
        f"His row is {b14['row']} months, with a 95th percentile of {s14['p95']}, so the LMS formula applies with the row's L = −{s14['L4']}, M = {s14['M4']} and S = {s14['S4']}:",
        f"z = (({b14['bmi_exact2']} ÷ {s14['M4']})−{s14['L4']} − 1) ÷ (−{s14['L4']} × {s14['S4']}) = {s14['z2_again']}, a percentile of {b14['percentile']}.",
        f"The calculator shows the {ordinal(b14['ordinal'])} percentile, in the overweight category."]
    for w in want_sents:
        ok(norm(w) in ex_t, f'examples: missing {w!r}')
    # the steps again from the CSV's printed values: z for the CDC girl, the extended formula for the boy and the girl
    ok(f"{(22.6 - float(sb['p95'])) / float(sb['sigma']):.4f}" == sb['arg4'] and f"{N.cdf(float(sb['arg4'])):.5f}" == sb['phi5']
       and f"{90 + 10 * float(sb['phi5']):.4f}" == cbx['percentile4'] == '99.7683', 'CDC boy steps')
    ok(d1(90 + 10 * N.cdf((float(g98['bmi_exact2']) - float(sg['p95'])) / float(sg['sigma']))) == g98['percentile'] == '95.6', 'girl 98 lb steps')
    zz = ((float(b14['bmi_exact2']) / float(s14['M4'])) ** -float(s14['L4']) - 1) / (-float(s14['L4']) * float(s14['S4']))
    ok(f'{zz:.2f}' == s14['z2_again'] == '1.41' and d1(N.cdf(zz) * 100) == b14['percentile'] == '92.1', 'boy 14 steps')
    ok(f"{703 * 98 / 54 ** 2:.2f}" == g98['bmi_exact2'] and f"{703 * 150 / 65 ** 2:.2f}" == b14['bmi_exact2'], 'example BMIs')
    # the 9 years 6 months girl and the 4 years 2 months boy in the calculator's own words
    g = calc(pg, 'female', 9, 6, cm=100, kg='21.2')
    ok(g['line'] == '92nd percentile for girls aged 9 years 6 months' and g['cat'] == 'Overweight' and metric(g, 'Percentile') == ['92.2', 'z = 1.42'],
       f'CDC girl typed in: {g["line"]} {g["cat"]} {metric(g, "Percentile")}')
    g = calc(pg, 'male', 4, 2, cm=100, kg='22.6')
    ok(g['line'].startswith('Above the 99th percentile for boys aged 4 years 2 months'), f'CDC boy typed in: {g["line"]}')
    # how BMI changes with age: the medians and one BMI at two ages
    age_t = norm(pg.inner_text('#age'))
    mb, mg = MED['male'], MED['female']
    ok(f"For boys it is {mb['at_2']} at age 2, falls to {mb['lowest']} at 5 and 6, and climbs to {mb['at_19']} at 19." in age_t
       and f"For girls it is {mg['at_2']} at 2, {mg['lowest']} at 5 and 6, and {mg['at_19']} at 19." in age_t, 'median sentences')
    ok(mb['lowest_ages'] == [5, 6] == mg['lowest_ages'] and (mb['at_2'], mb['lowest'], mb['at_19'], mg['at_2'], mg['lowest'], mg['at_19'])
       == ('16.5', '15.4', '22.5', '16.4', '15.2', '21.6'), 'medians in the stats')
    ok(all(T[s][a]['p50'] == MED[s]['by_age'][str(a)] for s in ('male', 'female') for a in range(2, 20)), 'medians = the 50th column')
    a5, a19 = AGE_EX['girl_5'], AGE_EX['girl_19']
    ok(f"A single cut-off can't follow that: a BMI of 17.0 is above the 85th percentile for a 5-year-old girl ({a5['p85']}), so it is overweight, but below the 5th for a 19-year-old ({a19['p5']}), so it is underweight." in age_t,
       'the 17.0 example')
    g5 = calc(pg, 'female', 5, 0, cm=150, kg=f'{17.0 * 2.25:.4f}')
    g19 = calc(pg, 'female', 19, 0, cm=150, kg=f'{17.0 * 2.25:.4f}')
    ok((g5['cat'], g19['cat']) == ('Overweight', 'Underweight') == (a5['category'], a19['category']), f'BMI 17.0 at 5 and 19: {g5["cat"]}, {g19["cat"]}')
    ok('"Because children and teens are growing, their BMI values are expressed relative to others of the same sex and age. These values are called BMI-for-age percentiles."' in age_t, 'fact 2 first quote in #age')
    how_t = norm(pg.inner_text('#how'))
    for w in ('"Age is listed at the half month point for the entire month; for example, 48.5 months represents 48.0 months up to but not including 49.0 months of age."',
              'So a child of 2 years 0 months reads the 24.5-month row, and one of 9 years 6 months the 114.5-month row.',
              'The calculator takes any age from 24 to 239 months.', '"BMI percentiles and z-scores up to the 95th percentile (z-score 1.645) are the same as those in the 2000 CDC BMI-for-age growth charts."',
              '"above the 95th percentile up to the 99.99th percentile (z-scores up to 5)."', 'z = ((BMI ÷ M)L − 1) ÷ (L × S)', 'percentile = 90 + 10 × Φ((BMI − P95) ÷ sigma)',
              '100 × BMI ÷ P95', '"BMI does not distinguish between fat, muscle, and bone mass."'):
        ok(norm(w) in how_t, f'#how: missing {w!r}')
    prev = norm(pg.inner_text('#prevalence'))
    ok("In CDC's measured survey for August 2021–August 2023, 21.1% of children and teens aged 2–19 had obesity and 7.0% had severe obesity (NCHS Health E-Stat 112)." in prev
       and pg.evaluate("!!document.querySelector('#prevalence a[href=\"/childhood-obesity-statistics/\"]')"), 'prevalence paragraph and link')
    ok(len(re.findall(r'\d+(?:\.\d+)?%', prev)) == 2, f'prevalence numbers {re.findall(r"[0-9.]+%", prev)}')

    # ---- FAQ: questions, JSON-LD = visible, numbers against the stats, one tap opens and one closes
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([norm(q) for q, _ in visq] == FAQ_Q, f'FAQ questions {[q for q, _ in visq]}')
    ok([[q['name'], q['acceptedAnswer']['text']] for q in GR['FAQPage']['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')
    FA = {norm(q): norm(a) for q, a in visq}
    g10, b10 = T['female'][10], T['male'][10]
    ok('a healthy weight is a BMI from the 5th to below the 85th percentile' in FA[FAQ_Q[0]]
       and f"a girl's healthy BMI runs from {g10['p5']} to just under {g10['p85']} and a boy's from {b10['p5']} to just under {b10['p85']}." in FA[FAQ_Q[0]]
       and (g10['p5'], g10['p85'], b10['p5'], b10['p85']) == ('14.0', '20.0', '14.2', '19.4'), 'FAQ 1')
    ok('times 703' in FA[FAQ_Q[1]] and 'age in months' in FA[FAQ_Q[1]], 'FAQ 2')
    ok('relative to others of the same sex and age' in FA[FAQ_Q[2]], 'FAQ 3')
    ok(f"they are {b10['p85']} and {b10['p95']} for boys and {g10['p85']} and {g10['p95']} for girls" in FA[FAQ_Q[3]] and 'tables above' in FA[FAQ_Q[3]], 'FAQ 4')
    ok('120% of the 95th percentile' in FA[FAQ_Q[4]] and 'class 2 obesity is 120% to less than 140%' in FA[FAQ_Q[4]] and 'class 3 obesity is 140%' in FA[FAQ_Q[4]], 'FAQ 5')
    ok('1.645 is the 95th percentile' in FA[FAQ_Q[5]] and 'up to 5' in FA[FAQ_Q[5]], 'FAQ 6')
    ok(f"{mb['at_2']} at age 2, {mb['lowest']} at 5 and 6 and {mb['at_19']} at 19; for girls it is {mg['at_2']}, {mg['lowest']} and {mg['at_19']}" in FA[FAQ_Q[6]], 'FAQ 7')
    ok('cover ages 2 through 19' in FA[FAQ_Q[7]] and f"{A['girl-10-98']['bmi']} is in the adult healthy range" in FA[FAQ_Q[7]] and '96th percentile' in FA[FAQ_Q[7]], 'FAQ 8')
    ok(FA[FAQ_Q[8]].startswith('2 years 0 months to 19 years 11 months (24 to 239 months)')
       and pg.evaluate("!!document.querySelector('#faq a[href=\"/\"]')"), 'FAQ 9 and its link')
    for i, q in enumerate(pg.query_selector_all('.faq-question')):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open in one tap')
        q.click(); pg.wait_for_timeout(30)
        ok(not pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not close in one tap')

    # ---- the figure against kids_stats.json
    F = pg.evaluate("""() => { const svg = document.querySelector('#chart figure svg');
        return {vb: svg.getAttribute('viewBox'), bands: [...svg.querySelectorAll('polygon')].map(p => [p.dataset.sex, p.dataset.band, p.getAttribute('points'), p.getAttribute('fill')]),
          edges: [...svg.querySelectorAll('polyline')].map(p => [p.dataset.sex, p.dataset.line, p.getAttribute('points'), p.getAttribute('stroke')]),
          keys: [...svg.querySelectorAll('rect[data-key]')].map(r => [r.dataset.key, r.getAttribute('fill'), +r.getAttribute('y')]),
          texts: [...svg.querySelectorAll('text')].map(t => [t.textContent, +t.getAttribute('x'), +t.getAttribute('y')]),
          hover: [...svg.querySelectorAll('rect[fill-opacity="0"]')].map(r => r.querySelector('title').textContent),
          colors: [...svg.querySelectorAll('*')].flatMap(e => [e.getAttribute('fill'), e.getAttribute('stroke')]).filter(Boolean),
          title: svg.querySelector('title').textContent, desc: svg.querySelector('desc').textContent} }""")
    PW, GAP, LX, YT, YB, LO, HI = 126, 20, 34, 64, 260, 12, 36
    X0 = {'male': LX, 'female': LX + PW + GAP}
    xm = lambda sex, m: X0[sex] + (m - 24) * PW / 216
    yb = lambda v: YB - (v - LO) * (YB - YT) / (HI - LO)
    TINT = {'under': '#dbeafe', 'healthy': '#d1fae5', 'over': '#fde68a', 'obese': '#fecaca', 'severe': '#fca5a5'}
    ok(F['vb'] == '0 0 320 300' and len(F['bands']) == 10 and len(F['edges']) == 8, f'figure {F["vb"]}, {len(F["bands"])} bands, {len(F["edges"])} edges')

    def series(sex, line):
        pts = S['figure'][sex]
        val = (lambda q: min(q['p120'], 35.0)) if line == 'p120' else (lambda q: q[line])
        return [(24, val(pts[0]))] + [(q['agemos'], val(q)) for q in pts] + [(240, val(pts[-1]))]
    ok([q['agemos'] for q in S['figure']['male']] == [m + 0.5 for m in range(24, 240)] == [q['agemos'] for q in S['figure']['female']], 'figure months')
    for sex in ('male', 'female'):
        for q in S['figure'][sex]:
            if q['agemos'] == 120.5 or q['agemos'] == 228.5:
                a = int(q['agemos'] // 12)
                ok(d1(q['p5']) == T[sex][a]['p5'] and d1(q['p95']) == T[sex][a]['p95'], f'figure series = table at {sex} {a}')

    def close(P, want, tol=0.01):
        return len(P) == len(want) and all(abs(x - xm_) < tol and abs(y - y_) < tol for (x, y), (xm_, y_) in zip(P, want))
    for sex, ln, pts, stroke in F['edges']:
        P = [tuple(map(float, q.split(','))) for q in pts.split()]
        want = [(xm(sex, m), yb(v)) for m, v in series(sex, ln)]
        ok(stroke == '#ffffff' and close(P, want), f'band edge {sex} {ln}')
    ORDER = ['under', 'healthy', 'over', 'obese', 'severe']
    for sex, band, pts, fill in F['bands']:
        P = [tuple(map(float, q.split(','))) for q in pts.split()]
        i = ORDER.index(band)
        lo = [(xm(sex, 24), yb(LO)), (xm(sex, 240), yb(LO))] if i == 0 else [(xm(sex, m), yb(v)) for m, v in series(sex, ('p5', 'p85', 'p95', 'p120')[i - 1])]
        hi = [(xm(sex, 24), yb(HI)), (xm(sex, 240), yb(HI))] if i == 4 else [(xm(sex, m), yb(v)) for m, v in series(sex, ('p5', 'p85', 'p95', 'p120')[i])]
        ok(fill == TINT[band] and close(P, lo + hi[::-1]), f'band {sex} {band}')
    ok(sorted((s, b) for s, b, *_ in F['bands']) == sorted((s, b) for s in ('male', 'female') for b in ORDER), 'every band once per panel')
    ok([k for k, _, _ in F['keys']] == ORDER and all(f == TINT[k] for k, f, _ in F['keys']), f'legend keys {F["keys"]}')
    TX = {t: (x, y) for t, x, y in F['texts']}
    names = ['Underweight', 'Healthy weight', 'Overweight', 'Obesity', 'Severe obesity']
    ok(all(n in TX for n in names) and max(TX[n][1] for n in names) < min(TX['Boys'][1], TX['Girls'][1]) < YT, 'legend above the panels')
    ok(abs(TX['Boys'][0] - (X0['male'] + PW / 2)) < 0.06 and abs(TX['Girls'][0] - (X0['female'] + PW / 2)) < 0.06 and 'BMI' in TX, 'panel titles / BMI')
    for v in range(LO, HI + 1, 4):
        ok(any(t == str(v) and abs(x - (LX - 8)) < 0.06 and abs(y - (yb(v) + 4)) < 0.06 for t, x, y in F['texts']), f'y label {v}')
    for sex in ('male', 'female'):
        for age in (2, 5, 10, 15, 20):
            ok(any(t == str(age) and abs(x - xm(sex, age * 12)) < 0.06 and abs(y - (YB + 16)) < 0.06 for t, x, y in F['texts']), f'x label {sex} {age}')
    ok(sum(1 for t, *_ in F['texts'] if t == 'Age (years)') == 2, 'age axis titles')
    PAL = {'#dbeafe', '#d1fae5', '#fde68a', '#fecaca', '#fca5a5', '#ffffff', '#111827', '#4b5563', '#1f2937', '#9ca3af', 'none'}
    ok(set(c.lower() for c in F['colors']) <= PAL, f'colours outside the palette: {set(F["colors"]) - PAL}')
    hov = []
    for sex, word in (('male', 'Boys'), ('female', 'Girls')):
        for age in range(2, 20):
            r = T[sex][age]
            hov.append(f'{word} at {age} years: 5th percentile {r["p5"]}, 85th {r["p85"]}, 95th {r["p95"]}, 120% of the 95th {r["p120"]}'
                       + (' (severe obesity from 35)' if Decimal(r['p120']) > 35 else ''))
    ok([norm(x) for x in F['hover']] == hov, 'hover titles')
    b, gg = T['male'], T['female']
    ok(norm(F['desc']) == norm(
        'Two panels, boys and girls, with age from 2 to 20 years across and BMI from 12 to 36 up, shaded in five bands, one per CDC category: '
        'underweight below the 5th percentile, healthy weight from the 5th to the 85th, overweight from the 85th to the 95th, obesity from '
        'the 95th to 120% of the 95th or a BMI of 35, whichever is lower, and severe obesity above that. Boys at 2: '
        f'{b[2]["p5"]}, {b[2]["p85"]}, {b[2]["p95"]} and {b[2]["p120"]} (the 5th, 85th and 95th percentiles and 120% of the 95th); at 19: '
        f'{b[19]["p5"]}, {b[19]["p85"]}, {b[19]["p95"]} and {b[19]["p120"]}. Girls at 2: {gg[2]["p5"]}, {gg[2]["p85"]}, {gg[2]["p95"]} and '
        f'{gg[2]["p120"]}; at 19: {gg[19]["p5"]}, {gg[19]["p85"]}, {gg[19]["p95"]} and {gg[19]["p120"]}. Our calculation from CDC\'s data file.'),
       f'figure desc {F["desc"]!r}')

    # ---- words: nothing from the NEVER WRITE list (page, head, JSON-LD, the calculator's new line)
    allw = (norm(body_text) + ' ' + ' '.join(str(v) for v in head.values()) + ' ' + json.dumps(ld, ensure_ascii=False) + ' '
            + norm(src[:src.index('</head>')]) + ' ' + ' '.join(a for a in aap_lines if a))
    for pat in NEVER:
        hit = re.search(pat, allw, 0 if pat in CASE else re.I)
        ok(not hit, f'banned wording: {hit.group(0) if hit else ""!r} ({pat})')
    ok(not re.search(r'\bNormal\b', allw), 'Normal as a category name')
    ok(not re.search(r'\bobese\b', norm(body_text), re.I), '"obese" in the page')
    prose = norm(pg.evaluate("""() => { const m = document.querySelector('main').cloneNode(true);
        m.querySelectorAll('svg, table, #kids-results').forEach(e => e.remove()); return m.textContent; }"""))
    ok(not re.search(r'(?<![\d.])(?:18\.5|24\.9|29\.9|34\.9)(?![\d])', prose), 'an adult cut-off in the prose')

    # ---- links
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
    ok(outside == {'https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm', 'https://www.cdc.gov/growthcharts/data/extended-bmi/bmi-age-2022.csv',
                   'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html', 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
                   'https://www.cdc.gov/bmi/about/index.html', 'https://www.cdc.gov/nchs/data/hestat/hestat112.htm'}, f'outside links {sorted(outside)}')
    ok(all(pg.evaluate('h => [...document.querySelectorAll(`main a[href="${h}"]`)].every(a => a.target === "_blank" && a.rel === "noopener")', h_) for h_ in outside),
       'outside links open in a new tab')
    ok(pg.evaluate("document.querySelectorAll('main .related-cols').length") == 1, 'one related block')

    # ---- labels: each names the expected field, and a click on it focuses that field (US units and metric)
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(50)
    fors = pg.eval_on_selector_all('main label', 'ls => ls.map(l => l.htmlFor)')
    ok(sorted(fors) == sorted(LABEL_IDS), f'labels name {fors}')
    LTXT = {'kids-height-ft': 'Height (ft)', 'kids-height-in': 'Height (in)', 'kids-weight-lbs': 'Weight (lb)', 'kids-height-cm': 'Height (cm)',
            'kids-weight-kg': 'Weight (kg)', 'kids-age-years': 'Age (years)', 'kids-age-months': 'Age (months)', 'kids-sex': 'Sex'}
    ok(dict(pg.evaluate("() => [...document.querySelectorAll('main label')].map(l => [l.htmlFor, l.textContent.trim()])")) == LTXT, 'label text')
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
    for w, hgt in ((320, 844), (360, 800), (390, 844), (1280, 844)):
        pg.set_viewport_size({'width': w, 'height': hgt}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
        if w in (360, 390):
            bottom = pg.evaluate("document.querySelector('#calc-kids-btn').getBoundingClientRect().bottom")
            ok(bottom <= hgt, f'Calculate below the fold at {w} x {hgt} ({bottom})')
        for when in ('before', 'after'):
            if when == 'after':
                pg.click('#calc-kids-btn'); pg.wait_for_timeout(120)
                ok(pg.evaluate("getComputedStyle(document.getElementById('kids-results')).display") != 'none', f'results hidden at {w}')
                txt = pg.inner_text('#kids-results')
                ok('NaN' not in txt and 'undefined' not in txt and 'Infinity' not in txt, f'NaN/undefined in the results at {w}')
            sw = pg.evaluate('document.documentElement.scrollWidth')
            ok(sw <= w, f'page {sw}px wide at {w} {when} Calculate')
            fits = pg.evaluate("""() => [...document.querySelectorAll('main table')].filter(t => t.offsetParent !== null)
                .map(t => [t.caption ? t.caption.textContent : t.className, t.offsetWidth, t.parentElement.clientWidth,
                           getComputedStyle(t.parentElement).overflowX, t.parentElement.getBoundingClientRect().right])""")
            ok(len(fits) == (3 if when == 'before' else 4), f'{len(fits)} tables at {w} {when}')
            for cap, tw, fw, ovf, right in fits:
                if 'er-table' in cap:
                    continue                                 # the results table is calculator.js's (DEVLOG §5 [P3])
                if w >= 360:
                    ok(tw <= fw + 1, f'table wider than its frame at {w} {when} Calculate: {cap} {tw} > {fw}')
                else:
                    ok(tw <= fw + 1 or (ovf == 'auto' and right <= w + 0.5), f'table outside a scrolling frame at {w}: {cap} {tw} > {fw} ({ovf})')
        res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
            const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
            const ctm = svg.getScreenCTM(), pt = svg.createSVGPoint(), sc = (x, y) => { pt.x = x; pt.y = y; const s = pt.matrixTransform(ctm); return [s.x, s.y]; };
            const plots = [[34, 64, 160, 260], [180, 64, 306, 260]].map(([a, b, c, d]) => [...sc(a, b), ...sc(c, d)]);
            return {box: [r.left, r.top, r.right, r.bottom], plots,
                    texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                    shapes: [...svg.querySelectorAll('rect:not([fill-opacity="0"]), line')].map(e => [e.tagName + ' ' + (e.getAttribute('fill') || e.getAttribute('stroke')), ...bx(e)])}; })""")
        ok(len(res) == 1, f'{len(res)} figures at {w}')
        for f_ in res:
            L_, T0, R_, B_ = f_['box']
            for j, a in enumerate(f_['texts']):
                ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T0 - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                for c2 in f_['texts'][j + 1:]:
                    ok(not (a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5), f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                for s_ in f_['shapes']:
                    ok(not (a[1] < s_[3] - 0.5 and s_[1] < a[3] - 0.5 and a[2] < s_[4] - 0.5 and s_[2] < a[4] - 0.5), f'{w}px label over a shape: {a[0]!r} / {s_[0]}')
                for pl in f_['plots']:
                    ok(not (a[1] < pl[2] - 0.5 and pl[0] < a[3] - 0.5 and a[2] < pl[3] - 0.5 and pl[1] < a[4] - 0.5), f'{w}px label inside a plot area: {a[0]!r}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures, {skipped} skipped')
for f_ in fails[:40]: print('FAIL', f_)
sys.exit(1 if fails or skipped else 0)
