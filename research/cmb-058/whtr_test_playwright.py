#!/usr/bin/env python3
"""Waist-to-height ratio calculator checks in Chromium (CMB-058). Needs Python Playwright + Chromium.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/cmb-058/whtr_test_playwright.py http://localhost:8000
  - NICE's classes: the registry row nice-ng246-ethnicity-thresholds holds the three classes, the BMI-under-35 and
    aged-5-and-over scope and the recommendation numbers the tool cites (1.9.14, 1.10.10);
  - typed-in values: every case's ratio, class, card tint, table bounds, active row and half height are worked out here
    again in whole tenths (cut, not rounded) and compared with what the page prints; boundary cases on both sides of
    0.4, 0.5 and 0.6 in inches and centimeters, a child's numbers, and a float edge (85.1 cm at 170.2 cm);
  - the lines that depend on the class: NICE's seek-advice line from 0.5, the CDC underweight line under 0.4;
  - wrong input: empty, out of range, a waist as long as the height; Enter calculates;
  - the US / Metric switch: converts to 0.1, restores the typed numbers when nothing was retyped, converts retyped
    numbers, and the results on screen follow it;
  - head: title, H1, og and twitter titles and the Article headline name the calculator; the description; the
    WebApplication node; dateModified = sitemap lastmod;
  - the example table: each ratio equals the waist / height both cut and rounded, and its class is NICE's;
  - every outside link is a registry URL; the FAQ JSON-LD equals the visible answers;
  - never wider than the screen at 320, 360, 390 and 1280 px, before and after Calculate; no JavaScript error."""
import csv
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

base = sys.argv[1].rstrip('/')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PATH = '/blog/waist-to-height-ratio/'
NAME = 'Waist-to-Height Ratio Calculator and Healthy Ranges'
CLASSES = ['No NICE class', 'Healthy central adiposity', 'Increased central adiposity', 'High central adiposity']
SHORT = ['No class', 'Healthy', 'Increased', 'High']
TINT = ['', 'normal', 'overweight', 'obese']
RANGE = ['under 0.4', '0.4 to 0.49', '0.5 to 0.59', '0.6 or more']
n_checks = n_fail = 0


def ok(cond, msg):
    global n_checks, n_fail
    n_checks += 1
    if not cond:
        n_fail += 1
        print('FAIL', msg)


rows = list(csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')))
REG_URLS = set()
for r in rows:
    for col in ('url', 'endpoint'):
        for u in re.split(r'\s*;\s*', r[col]):
            if u.startswith('http'):
                REG_URLS.add(u.strip())
nice = next(r for r in rows if r['domain'] == 'nice-ng246-ethnicity-thresholds')
for frag in ('0.4 to 0.49', '0.5 to 0.59', '0.6 or more', 'BMI under 35', 'aged 5 years and over', '1.9.14', '1.10.10',
             'both sexes and all ethnicities', 'cardiometabolic risk factor assessment', 'less than half the height'):
    ok(frag in nice['notes'] or frag in nice['sample_note'], f'registry NICE row lacks "{frag}"')
ok(nice['status'] == 'verified', 'NICE row not verified')
cdc = next(r for r in rows if r['domain'] == 'cdc-adult-bmi-categories')
ok('blog/waist-to-height-ratio' in cdc['pages_served'].split(';'), 'CDC categories row does not serve the page')


def expect(ht, wt):
    """Whole tenths in, as the page reads them: the cut ratio, the class and the waist bounds."""
    p = (wt * 100) // ht
    c = 0 if p < 40 else 1 if p < 50 else 2 if p < 60 else 3
    b4, b5, b6 = (ht * 4 + 9) // 10, (ht * 5 + 9) // 10, (ht * 6 + 9) // 10
    return p, c, (b4, b5, b6)


def f1(t):
    return f'{t // 10}.{t % 10}'


def tx(t):
    return str(t // 10) if t % 10 == 0 else f1(t)


def half(t):
    h = t / 20
    s = f'{h:.2f}'.rstrip('0').rstrip('.')
    return s


errors = []
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': 1280, 'height': 900})
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto(base + PATH)

    # Head and schema.
    head = pg.evaluate("""() => ({title: document.title, h1: document.querySelector('h1').textContent.trim(),
        og: document.querySelector('meta[property="og:title"]').content, tw: document.querySelector('meta[name="twitter:title"]').content,
        desc: document.querySelector('meta[name="description"]').content,
        ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)})""")
    ok(head['title'] == NAME + ' | CalculateMyBMI', f'title {head["title"]}')
    ok(head['h1'] == NAME and head['og'] == NAME and head['tw'] == NAME, 'H1 / og / twitter title')
    ok(len(head['desc']) <= 160 and 'NICE' in head['desc'], f'description {len(head["desc"])} chars')
    lds = [json.loads(x) for x in head['ld']]
    art = next(x for x in lds if x.get('@type') == 'Article')
    app = next((x for x in lds if x.get('@type') == 'WebApplication'), None)
    ok(art['headline'] == NAME, 'Article headline')
    ok(app is not None and app['@id'] == 'https://calculatemybmi.net' + PATH + '#calculator' and app['url'] == 'https://calculatemybmi.net' + PATH
       and app['applicationCategory'] == 'HealthApplication', 'WebApplication node')
    sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    lm = re.search(r'<loc>https://calculatemybmi\.net' + re.escape(PATH) + r'</loc><lastmod>([^<]+)</lastmod>', sm).group(1)
    ok(art['dateModified'] == lm, f'dateModified {art["dateModified"]} vs lastmod {lm}')
    faq = next(x for x in lds if x.get('@type') == 'FAQPage')
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok([[q['name'], q['acceptedAnswer']['text']] for q in faq['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')

    # The tool sits right under the intro, before the key takeaways.
    order = pg.evaluate("""() => { const a = document.querySelector('.intro-text'), t = document.getElementById('whtr'), k = document.querySelector('.key-takeaways');
        return !!(a.compareDocumentPosition(t) & 4) && !!(t.compareDocumentPosition(k) & 4); }""")
    ok(order, 'calculator not between the intro and the key takeaways')

    # Outside links.
    outside = set(pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))'))
    ok(outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')

    # Example table: ratio both cut and rounded, NICE class.
    ex = pg.evaluate("""() => { const t = [...document.querySelectorAll('table')].find(x => /Person/.test(x.textContent));
        return [...t.querySelectorAll('tbody tr')].map(r => [...r.cells].map(c => c.textContent.trim())); }""")
    ok(len(ex) == 4, 'example table rows')
    for row in ex:
        h = float(re.match(r'([\d.]+)', row[1]).group(1))
        w = float(re.match(r'([\d.]+)', row[2]).group(1))
        ht, wt = round(h * 10), round(w * 10)
        p, c, _ = expect(ht, wt)
        ok(row[4] == f'{p / 100:.2f}' == f'{round(w / h + 1e-12, 2):.2f}', f'example {row[0]}: {row[4]} vs cut {p / 100:.2f}')
        ok(row[5] == SHORT[c], f'example {row[0]}: class {row[5]}')
        ok(row[3] == f'{w:g} ÷ {h:g}', f'example {row[0]}: calculation cell {row[3]}')

    def setv(ids_vals):
        for i, v in ids_vals:
            pg.fill('#' + i, v)

    def units(u):
        pg.click(f'#whtr .unit-btn[data-units="{u}"]')

    def result():
        return pg.evaluate("""() => { const o = document.getElementById('whtr-out'); const card = o.querySelector('.bmi-result-card');
            return {visible: o.classList.contains('visible'), html: o.innerHTML, text: o.textContent,
              card: card ? card.className : null, value: card ? card.querySelector('.bmi-value').textContent : null,
              cat: card ? card.querySelector('.bmi-category').textContent : null, range: card ? card.querySelector('.bmi-range').textContent : null,
              rows: [...o.querySelectorAll('.er-table tbody tr')].map(r => ({active: r.classList.contains('er-active'), cells: [...r.cells].map(c => c.textContent.trim()), you: !!r.querySelector('.er-you'), dot: (r.querySelector('.cat-dot') || {}).className || ''})),
              h2: [...o.querySelectorAll('h2')].map(h => h.textContent), notes: [...o.querySelectorAll('.er-note')].map(n => n.textContent)}; }""")

    def check_case(label, u, vals, ht, wt):
        units(u)
        setv(vals)
        pg.click('#whtr-go')
        r = result()
        p, c, (b4, b5, b6) = expect(ht, wt)
        un = 'in' if u == 'us' else 'cm'
        ok(r['visible'] and r['value'] == f'{p / 100:.2f}', f'{label}: value {r["value"]} vs {p / 100:.2f}')
        ok(r['cat'] == CLASSES[c], f'{label}: class {r["cat"]} vs {CLASSES[c]}')
        ok(r['card'] == 'bmi-result-card' + (' ' + TINT[c] if TINT[c] else ''), f'{label}: card {r["card"]}')
        ok(r['range'] == f'Waist {tx(wt)} {un} ÷ height {tx(ht)} {un}', f'{label}: range line {r["range"]}')
        want = [['under 0.4', 'No class', f'under {f1(b4)} {un}'], ['0.4–0.49', 'Healthy', f'{f1(b4)}–{f1(b5 - 1)} {un}'],
                ['0.5–0.59', 'Increased', f'{f1(b5)}–{f1(b6 - 1)} {un}'], ['0.6 or more', 'High', f'{f1(b6)} {un} or more']]
        got = [[x['cells'][0], x['cells'][1].replace('You', ''), x['cells'][2]] for x in r['rows']]
        ok(got == want, f'{label}: table {got} vs {want}')
        ok([x['active'] for x in r['rows']] == [i == c for i in range(4)] and [x['you'] for x in r['rows']] == [i == c for i in range(4)],
           f'{label}: active row')
        ok([x['dot'] for x in r['rows']] == ['', 'cat-dot normal', 'cat-dot overweight', 'cat-dot obese'], f'{label}: dots')
        ok(r['h2'] == ['What your ratio means', f'Waist sizes for a height of {tx(ht)} {un}'], f'{label}: headings {r["h2"]}')
        notes = ' '.join(r['notes'])
        ok(f'Half your height is {half(ht)} {un}.' in notes, f'{label}: half height ({half(ht)})')
        ok(f'Your waist is {p / 100:.2f} of your height.' in notes, f'{label}: ratio sentence')
        if c:
            ok(f'NICE classes {RANGE[c]} as {CLASSES[c].lower()}' in notes, f'{label}: NICE class sentence')
        else:
            ok('NICE’s classes start at 0.4' in notes and 'under 18.5 is underweight' in notes, f'{label}: under-0.4 lines')
        ok(('seek advice and further checks' in notes) == (c >= 2), f'{label}: seek-advice line')
        ok('cut to two decimals, not rounded' in notes and '1.9.14 (adults) and 1.10.10 (children and young people)' in notes,
           f'{label}: method and source line')
        # Every outside link in the results is a registry URL.
        links = set(re.findall(r'href="(http[^"]+)"', r['html']))
        ok(links <= REG_URLS, f'{label}: result links not in the registry {links - REG_URLS}')

    # Default inputs (5 ft 5 in, 30 in).
    pg.click('#whtr-go')
    r = result()
    ok(r['value'] == '0.46' and r['cat'] == 'Healthy central adiposity', f'default result {r["value"]} {r["cat"]}')
    cases = [
        ('us 5 ft 7 in, 38 in (NICE example)', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '38')], 670, 380),
        ('us 67 in, 33.5 in', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '33.5')], 670, 335),
        ('us 67 in, 33.4 in', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '33.4')], 670, 334),
        ('us 67 in, 40.2 in', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '40.2')], 670, 402),
        ('us 67 in, 40.1 in', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '40.1')], 670, 401),
        ('us 67 in, 26.8 in', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '26.8')], 670, 268),
        ('us 67 in, 26.7 in', 'us', [('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '26.7')], 670, 267),
        ('us 66.5 in, 33.2 in', 'us', [('whtr-ft', '5'), ('whtr-in', '6.5'), ('whtr-win', '33.2')], 665, 332),
        ('us 66.5 in, 33.3 in', 'us', [('whtr-ft', '5'), ('whtr-in', '6.5'), ('whtr-win', '33.3')], 665, 333),
        ('us 6 ft 0 in, empty inches, 36 in', 'us', [('whtr-ft', '6'), ('whtr-in', ''), ('whtr-win', '36')], 720, 360),
        ('metric 170, 85', 'metric', [('whtr-cm', '170'), ('whtr-wcm', '85')], 1700, 850),
        ('metric 170.2, 85.1 (float edge)', 'metric', [('whtr-cm', '170.2'), ('whtr-wcm', '85.1')], 1702, 851),
        ('metric 170.2, 85.0', 'metric', [('whtr-cm', '170.2'), ('whtr-wcm', '85.0')], 1702, 850),
        ('metric 160, 88', 'metric', [('whtr-cm', '160'), ('whtr-wcm', '88')], 1600, 880),
        ('metric 180, 110', 'metric', [('whtr-cm', '180'), ('whtr-wcm', '110')], 1800, 1100),
        ('metric 110, 52 (a child)', 'metric', [('whtr-cm', '110'), ('whtr-wcm', '52')], 1100, 520),
        ('metric 165.1, 66.0', 'metric', [('whtr-cm', '165.1'), ('whtr-wcm', '66.0')], 1651, 660),
    ]
    for case in cases:
        check_case(*case)

    # Wrong input.
    def err_case(label, u, vals, want):
        units(u)
        setv(vals)
        pg.click('#whtr-go')
        r = result()
        ok(r['card'] is None and want in r['text'], f'{label}: {r["text"][:120]}')
    err_case('empty waist', 'us', [('whtr-ft', '5'), ('whtr-in', '5'), ('whtr-win', '')], 'Enter a height from 3 ft to 7 ft 6 in and a waist from 15 to 80 inches.')
    err_case('8 ft', 'us', [('whtr-ft', '8'), ('whtr-in', '0'), ('whtr-win', '30')], 'Enter a height from 3 ft')
    err_case('12 in', 'us', [('whtr-ft', '5'), ('whtr-in', '12'), ('whtr-win', '30')], 'Enter a height from 3 ft')
    err_case('waist 14.9 in', 'us', [('whtr-ft', '5'), ('whtr-in', '5'), ('whtr-win', '14.9')], 'a waist from 15 to 80 inches')
    err_case('waist as long as height', 'us', [('whtr-ft', '3'), ('whtr-in', '0'), ('whtr-win', '40')], 'The waist is as long as the height or longer.')
    err_case('80 cm tall', 'metric', [('whtr-cm', '80'), ('whtr-wcm', '50')], 'Enter a height from 90 to 230 cm and a waist from 38 to 203 cm.')
    err_case('waist 204 cm', 'metric', [('whtr-cm', '200'), ('whtr-wcm', '204')], 'a waist from 38 to 203 cm')

    # Enter calculates.
    units('metric')
    setv([('whtr-cm', '175'), ('whtr-wcm', '80')])
    pg.evaluate("document.getElementById('whtr-out').classList.remove('visible')")
    pg.focus('#whtr-wcm')
    pg.keyboard.press('Enter')
    r = result()
    ok(r['visible'] and r['value'] == '0.45', f'Enter: {r["value"]}')

    # The switch: convert, restore, convert retyped numbers; results follow.
    pg.goto(base + PATH)
    vals = lambda: pg.evaluate("() => ['whtr-ft','whtr-in','whtr-win','whtr-cm','whtr-wcm'].map(i => document.getElementById(i).value)")
    hid = lambda: pg.evaluate("() => [document.getElementById('whtr-us').hidden, document.getElementById('whtr-metric').hidden, document.getElementById('whtr-us').offsetParent === null, document.getElementById('whtr-metric').offsetParent === null]")
    setv([('whtr-ft', '5'), ('whtr-in', '7'), ('whtr-win', '38')])
    pg.click('#whtr-go')
    units('metric')
    v = vals()
    ok(v[3:] == ['170.2', '96.5'], f'US to metric {v}')
    ok(hid() == [True, False, True, False], f'rows after the switch {hid()}')
    r = result()
    ok(r['value'] == f'{(965 * 100 // 1702) / 100:.2f}' and r['range'] == 'Waist 96.5 cm ÷ height 170.2 cm', f'results follow the switch {r["value"]} {r["range"]}')
    units('us')
    ok(vals()[:3] == ['5', '7', '38'], f'restored {vals()}')
    r = result()
    ok(r['value'] == '0.56' and r['range'] == 'Waist 38 in ÷ height 67 in', f'restored result {r["value"]} {r["range"]}')
    units('metric')
    ok(vals()[3:] == ['170.2', '96.5'], f'metric kept {vals()}')
    setv([('whtr-cm', '180'), ('whtr-wcm', '90')])
    units('us')
    ok(vals()[:3] == ['5', '10.9', '35.4'], f'metric to US {vals()}')
    units('metric')
    ok(vals()[3:] == ['180', '90'], f'typed metric restored {vals()}')
    btn = pg.evaluate("() => [...document.querySelectorAll('#whtr .unit-btn')].map(b => [b.dataset.units, b.classList.contains('active'), b.getAttribute('aria-pressed')])")
    ok(btn == [['us', False, 'false'], ['metric', True, 'true']], f'toggle state {btn}')

    # Widths, before and after Calculate.
    for w in (1280, 390, 360, 320):
        pg.set_viewport_size({'width': w, 'height': 900})
        pg.goto(base + PATH)
        for stage in ('before', 'after'):
            if stage == 'after':
                pg.click('#whtr-go')
            sw = pg.evaluate('() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]')
            ok(sw[0] <= sw[1], f'{w} px {stage}: page {sw[0]} wider than {sw[1]}')
            inside = pg.evaluate("""() => { const c = document.getElementById('whtr').getBoundingClientRect();
                return [...document.querySelectorAll('#whtr input, #whtr button, #whtr .bmi-result-card, #whtr .er-section')].every(e => { const r = e.getBoundingClientRect();
                  return r.width === 0 || (r.left >= c.left - 0.5 && r.right <= c.right + 0.5); }); }""")
            ok(inside, f'{w} px {stage}: something sticks out of the calculator card')
            if stage == 'after' and w >= 360:
                fit = pg.evaluate("() => { const s = document.querySelector('#whtr-out .er-table').closest('.er-section'); return [s.scrollWidth, s.clientWidth]; }")
                ok(fit[0] <= fit[1], f'{w} px: the waist table scrolls inside its section ({fit})')
        if w == 320:
            cols = pg.evaluate("() => getComputedStyle(document.getElementById('whtr-us')).gridTemplateColumns.split(' ').length")
            ok(cols == 2, f'320 px: the US row has {cols} columns')
        if w == 390:
            cols = pg.evaluate("() => getComputedStyle(document.getElementById('whtr-us')).gridTemplateColumns.split(' ').length")
            ok(cols == 3, f'390 px: the US row has {cols} columns')
    br.close()

ok(not errors, f'JavaScript errors: {errors}')
print(f'{n_checks} checks, {n_fail} failures')
sys.exit(1 if n_fail else 0)
