#!/usr/bin/env python3
"""CMB-027: the nine "Example:" blocks on /calculators/, typed into the calculators they link to.

usage: python3 research/cmb-027/hub_examples_playwright.py BASE
       BASE = the served repo root, e.g. http://localhost:8000 (python3 -m http.server 8000)

Needs Python Playwright and Chromium (cloud sessions: the preinstalled Chromium plus
`pip install playwright==1.63.0`). Requests to any host other than BASE's are aborted
(ads, consent, analytics), as in research/calculator-checks/calc_e2e_playwright.py.

At a 390 x 844 viewport it:
  1. opens /calculators/ and collects every block that starts with "Example:" (there must be 9)
     and the href of the "Try Calculator" button in the same card;
  2. reads the example's inputs from its own text (height, weight, age, sex, frame, neck, waist,
     method), opens the calculator page that button links to, types them in (US units; optional
     fields the example doesn't give are left empty) and presses Calculate;
  3. compares every number and category the example states with what that calculator prints:
       /                       BMI and category; lowest and highest healthy weight
       /women-bmi-calculator/  BMI and category; "within the healthy range"; lowest and highest
                               healthy weight
       /men-bmi-calculator/    BMI and category; the waist line in inches; the rank among US men (CMB-048)
       /age-bmi-calculator/    BMI; the Winter 2014 finding (higher below 23, rising at about 33, adults 65 and over, the
                               year twice; CMB-045 wording) and
                               that the BMI falls inside it (since CMB-036 the example names the band's
                               ends as the points where the risk of death was higher and began to
                               rise, and says the BMI lies between the two); also that the same height and weight
                               give the same BMI at age 30 (the calculator doesn't adjust for age)
       /kids-bmi-calculator/   BMI, percentile, category; the sex and age the result names
       /new-bmi-calculator/    traditional BMI and New BMI; where the example states them, the
                               difference in points and its direction, and the height where the two
                               formulas cross with the side that reads lower, against the printed
                               note and every row of the "How height changes the difference" table
       /ideal-weight/          the span, the number of formulas, Devine, Robinson, Miller, Hamwi;
                               the sex and frame the result names
       /lean-body-mass/        lean mass in lb and kg, the formula, body fat %, and "about N lbs" of
                               fat mass: the calculator prints fat mass to 0.1 lb and keeps it to
                               0.01 kg in the element's data-kg (the page's donut chart reads it);
                               N must equal that value in lb rounded once to a whole pound
       /body-fat-calculator/   the estimate and the method; the share of US men or women with more
                               body fat and their age group
     plus no page error on any calculator page and a visible result;
  4. accounts for every number (digits and number words) and every BMI category word in each
     example: each must sit inside an input or a compared claim, or it is reported as SKIP. A block
     whose button links to no known calculator, or an input the text doesn't give, is SKIP too.

  5. (CMB-048) the FAQ: JSON-LD equal to the visible answers; each sourced sentence present, its numbers worked out from
     bfpc_stats.json or checked in the registry row's own text; the claims the claims pass removed stay out; outside
     links in the registry. The men's example states the rank the calculator prints.

Prints every check, then "N checks, F failures, S skipped". Exit 0 only when F = 0 and S = 0.
"""
import re
import sys

from playwright.sync_api import sync_playwright

if len(sys.argv) != 2:
    sys.exit(__doc__)
BASE = sys.argv[1].rstrip('/')
VIEWPORT = {'width': 390, 'height': 844}
LB_PER_KG = 2.20462  # calculator.js kgToLbs / lbsToKg

NUM = re.compile(r'\d+(?:\.\d+)?')
NUM_WORD = re.compile(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b', re.I)
CATEGORY = re.compile(r'\b(?:severe thinness|moderate thinness|underweight|normal|healthy weight(?! range)'
                      r'|overweight|obese|obesity|class [123](?: obesity)?)\b', re.I)

checks = 0
failures = []
skipped = []

# CMB-048: the FAQ's numbers, from the data files and the registry rows that hold them
import csv, json, os                                                    # noqa: E401,E402
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
_BC = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json'), encoding='utf-8'))['bmi']['by_cat']
REG, REG_URLS = {}, set()
for _r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG[_r['domain']] = ' '.join((_r['coverage'], _r['sample_note'], _r['notes']))
    REG_URLS |= {_r['url']} | {e.strip() for e in _r['endpoint'].split(' ; ') if e.strip()}
_d1 = lambda x: f'{x:.1f}'
FAQ_FRAGMENTS = [
    'CDC calls it a screening measure that "does not distinguish between fat, muscle, and bone mass"',
    'for an individual it should be considered with other factors, such as blood pressure and cholesterol levels',
    'At a given BMI, body fat may vary by sex, age, and race and Hispanic origin, NCHS notes',
    'CDC applies its adult categories regardless of age, sex, or race',
    f"women had a median of {_d1(_BC['f']['healthy']['p50'])}% body fat and men {_d1(_BC['m']['healthy']['p50'])}% (our calculation",
    'more than 35 inches (88 cm) for women and 40 inches (102 cm) for men',
    'adults aged 20 and over, the ages CDC\'s adult categories cover',
    'children and teens aged 2 through 19, the ages of CDC\'s BMI-for-age charts',
    '53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat (Provencher et al., 2018)',
    'in a study of 80 adults who weighed themselves daily, weight was higher early in the week and fell during it',
    'CDC reads a child\'s BMI as a percentile among children of the same sex and age',
    'he writes that it may not be an improvement (Trefethen)',
]
FAQ_NEVER = [r'height bias', r'population-level', r'6-11%', r'store fat abdominally', r'12% body fat', r'sometimes more accurate',
             r'typically exceed', r'no official schedule', r'typically annually', r'under pediatrician guidance',
             r'consult (?:a|your) healthcare', r'ACOG', r'life-stage', r'menopaus', r'exercises regularly',
             r"world's leading", r'authoritative sources']
REG_QUOTES = [
    ('cdc-about-bmi', 'BMI does not distinguish between fat, muscle, and bone mass'),
    ('cdc-about-bmi', 'For individuals, BMI should be considered with other factors, such as blood pressure, cholesterol levels'),
    ('nhanes-adult-weight-trends', 'at a given BMI level, body fat may vary by sex, age, and race and Hispanic origin'),
    ('cdc-adult-bmi-categories', "based on a person's BMI regardless of age, sex, or race"),
    ('nhlbi-1998-obesity-guidelines', 'Waist >102 cm (>40 in) men and >88 cm (>35 in) women'),
    ('cdc-child-bmi-categories', 'expressed relative to others of the same sex and age'),
    ('cdc-child-bmi-categories', 'ages 2 through 19'),
    ('provencher-2018-nfl-combine', '53.4% of the athletes as obese, body fat 8.9%'),
    ('orsama-2014-weight-rhythms', 'The daily weight in 80 adults'),
    ('orsama-2014-weight-rhythms', 'higher weight early in the week'),
    ('trefethen-new-bmi', 'may not be an improvement'),
]


def norm(s):
    """Plain text: no-break spaces, primes, curly quotes, dashes and the minus sign made ASCII."""
    for a, b in ((' ', ' '), (' ', ' '), (' ', ' '), ('′', "'"), ('’', "'"),
                 ('″', '"'), ('“', '"'), ('”', '"'), ('–', '-'), ('—', '-'),
                 ('−', '-')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()


class Example:
    def __init__(self, n, text, href, heading):
        self.n, self.text, self.href, self.heading = n, text, href, heading
        self.tag = f'Example {n} {href}'
        self.covered = []  # spans of the text that are inputs or compared claims

    def find(self, pattern, what, required=True):
        m = re.search(pattern, self.text, re.I)
        if m is None and required:
            skip(self, f'{what}: not found in the example text')
        return m

    def cover(self, m, *groups):
        for g in groups:
            if m.group(g) is not None:
                self.covered.append(m.span(g))

    def unaccounted(self):
        out = []
        for rx, kind in ((NUM, 'number'), (NUM_WORD, 'number word'), (CATEGORY, 'category')):
            for m in rx.finditer(self.text):
                if not any(a <= m.start() and m.end() <= b for a, b in self.covered):
                    out.append(f'{kind} "{m.group(0)}" (char {m.start()}) is neither an input nor compared')
        return out


def check(ex, label, stated, printed, good=None):
    global checks
    checks += 1
    if good is None:
        good = stated == printed
    line = f'{ex.tag}: {label}: example {stated}, calculator {printed}'
    print(('  ok    ' if good else '  FAIL  ') + line)
    if not good:
        failures.append(line)
    return good


def skip(ex, why):
    line = f'{ex.tag}: {why}'
    print('  SKIP  ' + line)
    skipped.append(line)


def text_of(pg, sel):
    return norm(pg.inner_text(sel)) if pg.locator(sel).count() else ''


def first(pattern, s, group=1, flags=re.I):
    m = re.search(pattern, s, flags)
    return m.group(group) if m else None


def same_category(stated, printed):
    a = re.sub(r'^(a|an) ', '', norm(stated).lower())
    return a == norm(printed).lower()


def calculate(ex, pg, button, results, wait=200):
    pg.click(button)
    pg.wait_for_timeout(wait)
    return check(ex, 'result shown', 'visible', 'visible' if pg.is_visible(results) else 'not shown')


def us_units(pg, panel):
    pg.click(f'#panel-{panel} .unit-btn[data-unit="imperial"]')


def height(ex, pattern=r"(\d+)'(\d+)\""):
    m = ex.find(pattern, 'height')
    if m:
        ex.cover(m, 1, 2)
    return m


def bmi_and_category(ex, pg, t, lead=r'BMI of'):
    m = ex.find(lead + r' (\d+\.\d)(?: \(([^)]+)\))?', 'BMI')
    if not m:
        return None
    ex.cover(m, 1)
    printed = text_of(pg, f'#{t}-bmi-value')
    check(ex, 'BMI', m[1], printed)
    if m[2]:
        ex.cover(m, 2)
        cat = text_of(pg, f'#{t}-bmi-category')
        check(ex, 'category', m[2], cat, same_category(m[2], cat))
    return printed


def healthy_limits(ex, pg, t, pattern):
    m = ex.find(pattern, 'healthy weight range')
    if not m:
        return
    ex.cover(m, 1, 2)
    lo = first(r'^(\d+) lbs', text_of(pg, f'#{t}-healthy-min'))
    hi = first(r'^(\d+) lbs', text_of(pg, f'#{t}-healthy-max'))
    check(ex, 'lowest healthy weight (lbs)', m[1], lo)
    check(ex, 'highest healthy weight (lbs)', m[2], hi)


# ---------- one function per calculator: type the example's inputs, compare its claims ----------

def ex_standard(ex, pg):
    h = height(ex)
    w = ex.find(r'weighs (\d+) lbs', 'weight')
    if not (h and w):
        return
    ex.cover(w, 1)
    us_units(pg, 'standard')
    pg.fill('#standard-height-ft', h[1]); pg.fill('#standard-height-in', h[2]); pg.fill('#standard-weight-lbs', w[1])
    if not calculate(ex, pg, '#calc-standard-btn', '#standard-results'):
        return
    bmi_and_category(ex, pg, 'standard')
    healthy_limits(ex, pg, 'standard', r'healthy weight range at this height is (\d+)-(\d+) lbs')


def ex_women(ex, pg):
    h = height(ex)
    w = ex.find(r'weighs (\d+) lbs', 'weight')
    if not (h and w):
        return
    ex.cover(w, 1)
    us_units(pg, 'women')
    pg.fill('#women-height-ft', h[1]); pg.fill('#women-height-in', h[2]); pg.fill('#women-weight-lbs', w[1])
    pg.fill('#women-waist-in', '')  # the example gives no waist
    if not calculate(ex, pg, '#calc-women-btn', '#women-results'):
        return
    bmi_and_category(ex, pg, 'women')
    m = ex.find(r'within the healthy range \((\d+)-(\d+) lbs for her height\)', 'healthy weight range')
    if m:
        diff = text_of(pg, '#women-weight-diff')
        check(ex, 'within the healthy range', 'within', diff,
              diff.lower().startswith('within the healthy weight range'))
        healthy_limits(ex, pg, 'women', r'within the healthy range \((\d+)-(\d+) lbs')


def ex_men(ex, pg):
    h = height(ex)
    w = ex.find(r'weighs (\d+) lbs', 'weight')
    if not (h and w):
        return
    ex.cover(w, 1)
    us_units(pg, 'men')
    pg.fill('#men-height-ft', h[1]); pg.fill('#men-height-in', h[2]); pg.fill('#men-weight-lbs', w[1])
    if not calculate(ex, pg, '#calc-men-btn', '#men-results'):
        return
    bmi_and_category(ex, pg, 'men')
    m = ex.find(r'waist under (\d+)"', 'waist line', required=False)
    if m:
        ex.cover(m, 1)
        check(ex, 'waist line (in)', m[1], first(r'waist above (\d+) inches', text_of(pg, '#men-results')))
    m = ex.find(r'higher than (\d+)% of US men', 'rank', required=False)          # CMB-048
    if m:
        ex.cover(m, 1)
        check(ex, 'rank among US men', f'Higher than {m[1]}% of US men', text_of(pg, '#men-rank-value'))


def ex_age(ex, pg):
    a = ex.find(r'A (\d+)-year-old', 'age')
    h = height(ex)
    w = ex.find(r'weighs (\d+) lbs', 'weight')
    if not (a and h and w):
        return
    ex.cover(a, 1); ex.cover(w, 1)
    us_units(pg, 'age')
    pg.fill('#age-height-ft', h[1]); pg.fill('#age-height-in', h[2]); pg.fill('#age-weight-lbs', w[1])
    pg.fill('#age-years', a[1])
    if not calculate(ex, pg, '#calc-age-btn', '#age-results'):
        return
    bmi = bmi_and_category(ex, pg, 'age', lead=r'standard BMI of')
    res = text_of(pg, '#age-results')
    # CMB-045: the result gives Winter et al. 2014 in the DEVLOG §4 wording; band = (low, high, age group, year)
    w = re.search(r'aged (\d+) and over, compared with a BMI of \d+ to [\d.]+, the risk of death was higher below (\d+) and '
                  r'began to rise at about (\d+) \(Winter et al\., (\d{4})\)', res)
    if not w:
        check(ex, 'Winter 2014 finding printed', 'printed', 'not printed', False)
        return
    band = (None, w[2], w[3], w[1], w[4])
    m = ex.find(r'adults (\d+)(?:\+| and over)', 'band age group')
    if m:
        ex.cover(m, 1)
        check(ex, 'band age group (adults N+)', m[1], band[3])
    # CMB-036 wording (Winter's abstract): higher risk below the band's low end, rising from about its high end
    m = ex.find(r'\((\d+)-(\d+) in Winter|below a BMI of (\d+) and began to rise at about (\d+)', 'band')
    if m:
        lo, hi = (1, 2) if m[1] else (3, 4)
        ex.cover(m, lo, hi)
        check(ex, 'band (BMI low-high)', f'{m[lo]}-{m[hi]}', f'{band[1]}-{band[2]}')
    for m in re.finditer(r'Winter et al\., [^,()]+, (\d{4})|Winter (\d{4})', ex.text):
        g = 1 if m[1] else 2
        ex.cover(m, g)
        check(ex, 'Winter year', m[g], band[4])
    if bmi and ex.find(r'falls within the (?:observed )?lower-mortality band', 'falls within', required=False):
        check(ex, 'BMI falls inside the band', f'{bmi} inside', f'{band[1]}-{band[2]}',
              float(band[1]) <= float(bmi) <= float(band[2]))
    m = ex.find(r'(\d+\.\d) lies between the (two)', 'between', required=False)
    if bmi and m:
        ex.cover(m, 1, 2)
        check(ex, 'the example BMI', m[1], bmi)
        check(ex, 'BMI between the two points', f'{bmi} inside', f'{band[1]}-{band[2]}',
              float(band[1]) <= float(bmi) <= float(band[2]))
    # the calculator doesn't adjust BMI for age: the same inputs at age 30 give the same number
    pg.fill('#age-years', '30')
    pg.click('#calc-age-btn'); pg.wait_for_timeout(200)
    check(ex, f'BMI at age 30 (same height and weight)', bmi, text_of(pg, '#age-bmi-value'))


def ex_kids(ex, pg):
    a = ex.find(r'A (\d+)-year-old (boy|girl)', 'age and sex')
    h = height(ex)
    w = ex.find(r'weighs (\d+) lbs', 'weight')
    if not (a and h and w):
        return
    ex.cover(a, 1); ex.cover(w, 1)
    us_units(pg, 'kids')
    pg.fill('#kids-height-ft', h[1]); pg.fill('#kids-height-in', h[2]); pg.fill('#kids-weight-lbs', w[1])
    pg.fill('#kids-age-years', a[1]); pg.fill('#kids-age-months', '0')
    pg.select_option('#kids-sex', 'male' if a[2].lower() == 'boy' else 'female')
    if not calculate(ex, pg, '#calc-kids-btn', '#kids-results'):
        return
    res = text_of(pg, '#kids-results')
    line = re.search(r'(\d+)(?:st|nd|rd|th) percentile for (boys|girls) aged (\d+) years?', res)
    check(ex, 'sex and age the result names', f'{a[2].lower()}s aged {a[1]}',
          f'{line[2]} aged {line[3]}' if line else 'no percentile line')
    bmi_and_category(ex, pg, 'kids')
    m = ex.find(r'the (\d+)(?:st|nd|rd|th) percentile', 'percentile')
    if m:
        ex.cover(m, 1)
        check(ex, 'percentile', m[1], line[1] if line else None)
    m = ex.find(r'percentile, an? ([a-z ]+?) for (?:his|her) age and sex', 'category')
    if m:
        ex.cover(m, 1)
        cat = text_of(pg, '#kids-bmi-category')
        check(ex, 'category', m[1], cat, same_category(m[1], cat))


def ex_newbmi(ex, pg):
    h = height(ex, r"A (\d+)'(\d+)\" person")
    w = ex.find(r'weighing (\d+) lbs', 'weight')
    if not (h and w):
        return
    ex.cover(w, 1)
    us_units(pg, 'newbmi')
    pg.fill('#newbmi-height-ft', h[1]); pg.fill('#newbmi-height-in', h[2]); pg.fill('#newbmi-weight-lbs', w[1])
    if not calculate(ex, pg, '#calc-newbmi-btn', '#newbmi-results'):
        return
    m = ex.find(r'traditional BMI of (\d+\.\d)', 'traditional BMI')
    if m:
        ex.cover(m, 1)
        check(ex, 'traditional BMI', m[1], text_of(pg, '#newbmi-traditional-value'))
    m = ex.find(r'New BMI of (\d+\.\d)', 'New BMI')
    if m:
        ex.cover(m, 1)
        check(ex, 'New BMI', m[1], text_of(pg, '#newbmi-bmi-value'))
    m = ex.find(r'(\d+\.\d) points? (lower|higher)', 'difference', required=False)
    if m:
        ex.cover(m, 1, 2)
        d = float(text_of(pg, '#newbmi-diff'))
        check(ex, 'difference (points)', m[1], f'{abs(d):.1f}')
        check(ex, 'difference direction', m[2].lower(), 'lower' if d < 0 else 'higher' if d > 0 else 'equal')
    m = ex.find(r'New BMI reads (lower|higher) than traditional BMI above about (\d+)\'(\d+(?:\.\d+)?)" '
                r'and (higher|lower) below it', 'crossing', required=False)
    if m:
        ex.cover(m, 1, 2, 3, 4)
        res = text_of(pg, '#newbmi-results')
        p = re.search(r'gives a (higher|lower) BMI below about [\d.]+ m \((\d+)\'(\d+(?:\.\d+)?)"\) '
                      r'and a (higher|lower) one above it', res)
        if not p:
            check(ex, 'crossing note printed', 'printed', 'not printed', False)
            return
        check(ex, 'crossing height', f'{m[2]}\'{m[3]}"', f'{p[2]}\'{p[3]}"')
        check(ex, 'New BMI above the crossing', m[1].lower(), p[4].lower())
        check(ex, 'New BMI below the crossing', m[4].lower(), p[1].lower())
        # every row of the calculator's "How height changes the difference" table
        cross = int(m[2]) * 12 + float(m[3])
        rows = pg.eval_on_selector_all(
            '#newbmi-results .er-table',
            "ts => ts.filter(t => /Height/.test(t.rows[0].innerText) && /Difference/.test(t.rows[0].innerText))"
            ".flatMap(t => [...t.rows].slice(1).map(r => [...r.cells].map(c => c.innerText)))")
        check(ex, 'height table rows', 'at least 2', len(rows), len(rows) >= 2)
        for cells in rows:
            hm = re.match(r"(\d+)'(\d+)\"", norm(cells[0]))
            d = float(norm(cells[-1]))
            inches = int(hm[1]) * 12 + int(hm[2])
            want = m[1].lower() if inches > cross else m[4].lower()
            got = 'lower' if d < 0 else 'higher' if d > 0 else 'equal'
            check(ex, f'table row {hm[1]}\'{hm[2]}" ({norm(cells[-1])})', want, got)


def ex_ideal(ex, pg):
    h = height(ex, r"A (\d+)'(\d+)\" (woman|man)")
    f = ex.find(r'(small|medium|large) frame', 'frame')
    if not (h and f):
        return
    sex = 'female' if h[3].lower() == 'woman' else 'male'
    us_units(pg, 'ideal')
    pg.fill('#ideal-height-ft', h[1]); pg.fill('#ideal-height-in', h[2])
    pg.select_option('#ideal-sex', sex); pg.select_option('#ideal-frame', f[1].lower())
    if not calculate(ex, pg, '#calc-ideal-btn', '#ideal-results'):
        return
    res = text_of(pg, '#ideal-results')
    check(ex, 'sex and frame the result names', f'{sex}, {f[1].lower()} frame',
          first(r'\), (\w+, \w+ frame)', res))
    span = re.search(r'the (\w+) formulas span (\d+) lbs to (\d+) lbs', res)
    m = ex.find(r'gets (\d+)-(\d+) lbs across the (\w+) clinical formulas', 'span')
    if m:
        ex.cover(m, 1, 2, 3)
        check(ex, 'span (lbs)', f'{m[1]}-{m[2]}', f'{span[2]}-{span[3]}' if span else None)
        check(ex, 'number of formulas', m[3].lower(), span[1].lower() if span else None)
    for name in ('Devine', 'Robinson', 'Miller', 'Hamwi'):
        m = ex.find(name + r' (\d+) lbs', name)
        if m:
            ex.cover(m, 1)
            check(ex, f'{name} (lbs)', m[1], first(r'^(\d+) lbs', text_of(pg, f'#ideal-{name.lower()}')))


def ex_lbm(ex, pg):
    h = height(ex, r"A (\d+)'(\d+)\" (male|female)")
    w = ex.find(r'weighing (\d+) lbs', 'weight')
    if not (h and w):
        return
    ex.cover(w, 1)
    us_units(pg, 'lbm')
    pg.fill('#lbm-height-ft', h[1]); pg.fill('#lbm-height-in', h[2]); pg.fill('#lbm-weight-lbs', w[1])
    pg.select_option('#lbm-sex', h[3].lower())
    if not calculate(ex, pg, '#calc-lbm-btn', '#lbm-results'):
        return
    lean = text_of(pg, '#lbm-lbm')
    m = ex.find(r'lean body mass of (\d+\.\d) lbs \((\d+\.\d) kg, (\w+) formula\)', 'lean body mass')
    if m:
        ex.cover(m, 1, 2)
        check(ex, 'lean body mass (lbs)', m[1], first(r'^(\d+\.\d) lbs', lean))
        check(ex, 'lean body mass (kg)', m[2], first(r'\((\d+\.\d) kg\)', lean))
        check(ex, 'formula', m[3], first(r'the results above use (\w+)', text_of(pg, '#lbm-results')))
    m = ex.find(r'about (\d+) lbs \((\d+\.\d)%\) as fat mass', 'fat mass')
    if m:
        ex.cover(m, 1, 2)
        kg = float(pg.get_attribute('#lbm-fat-mass', 'data-kg'))
        whole = int(kg * LB_PER_KG + 0.5)
        check(ex, 'fat mass (about N lbs)', m[1],
              f'{whole} ({text_of(pg, "#lbm-fat-mass")} printed; {kg:.2f} kg = {kg * LB_PER_KG:.2f} lbs)',
              m[1] == str(whole))
        check(ex, 'body fat %', m[2] + '%', text_of(pg, '#lbm-body-fat'))


def ex_bodyfat(ex, pg):
    a = ex.find(r'A (\d+)-year-old (man|woman)', 'age and sex')
    h = height(ex)
    neck = ex.find(r'(\d+(?:\.\d+)?)-inch neck', 'neck')
    waist = ex.find(r'(\d+(?:\.\d+)?)-inch waist', 'waist')
    meth = ex.find(r'by the (tape) method', 'method')
    if not (a and h and neck and waist and meth):
        return
    ex.cover(a, 1); ex.cover(neck, 1); ex.cover(waist, 1)
    pg.click('.unit-btn[data-sex="%s"]' % ('m' if a[2].lower() == 'man' else 'f'))
    pg.click('.unit-btn[data-units="us"]')
    pg.click('.unit-btn[data-method="tape"]')
    pg.fill('#bfc-ft', h[1]); pg.fill('#bfc-in', h[2]); pg.fill('#bfc-w', '')  # the example gives no weight
    pg.fill('#bfc-age', a[1]); pg.fill('#bfc-neck', neck[1]); pg.fill('#bfc-waist', waist[1])
    if not calculate(ex, pg, '#bfc-go', '#bfc-out', wait=400):
        return
    res = text_of(pg, '#bfc-out')
    m = ex.find(r'comes out at (\d+\.\d)%', 'estimate')
    if m:
        ex.cover(m, 1)
        check(ex, 'body fat estimate', m[1] + '%', first(r'^(\d+\.\d%)', res))
    check(ex, 'method', 'tape', 'tape' if 'Tape measure (Navy method)' in res else res[:60],
          'Tape measure (Navy method)' in res)
    m = ex.find(r'(\d+)% of US (men|women) aged (\d+)-(\d+) have more body fat', 'share with more body fat')
    if m:
        ex.cover(m, 1, 3, 4)
        p = re.search(r'(\d+)% of US (men|women) aged (\d+)-(\d+) measured more body fat than', res)
        check(ex, 'share with more body fat', m[1] + '%', p[1] + '%' if p else None)
        check(ex, 'group', f'US {m[2]} aged {m[3]}-{m[4]}', f'US {p[2]} aged {p[3]}-{p[4]}' if p else None)


SPECS = {
    '/': ex_standard,
    '/women-bmi-calculator/': ex_women,
    '/men-bmi-calculator/': ex_men,
    '/age-bmi-calculator/': ex_age,
    '/kids-bmi-calculator/': ex_kids,
    '/new-bmi-calculator/': ex_newbmi,
    '/ideal-weight/': ex_ideal,
    '/lean-body-mass/': ex_lbm,
    '/body-fat-calculator/': ex_bodyfat,
}


def new_page(ctx):
    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(BASE) else r.abort())
    return pg, errors


with sync_playwright() as p:
    browser = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    ctx = browser.new_context(viewport=VIEWPORT)
    hub, hub_errors = new_page(ctx)
    hub.goto(BASE + '/calculators/', wait_until='load')
    blocks = hub.evaluate("""() => [...document.querySelectorAll('main strong')]
        .filter(s => s.textContent.trim() === 'Example:')
        .map(s => { const box = s.parentElement, card = box.closest('.calc-card');
                    const cta = card && card.querySelector('a.cta-button');
                    return { text: box.innerText, href: cta ? cta.getAttribute('href') : null,
                             heading: card && card.querySelector('h2') ? card.querySelector('h2').innerText : '' }; })""")
    hub.close()
    page = Example(0, '', '/calculators/', '')
    page.tag = f'/calculators/ at {VIEWPORT["width"]} px'
    check(page, '"Example:" blocks', 9, len(blocks))
    check(page, 'page errors', 'none', '; '.join(hub_errors) or 'none')
    for i, b in enumerate(blocks, 1):
        ex = Example(i, norm(b['text']), b['href'], norm(b['heading']))
        print(f'\n{ex.tag} ({ex.heading})\n  {ex.text}')
        spec = SPECS.get(ex.href)
        if spec is None:
            skip(ex, 'the card links to no known calculator')
            continue
        pg, errors = new_page(ctx)
        pg.goto(BASE + ex.href, wait_until='load')
        spec(ex, pg)
        check(ex, 'page errors', 'none', '; '.join(errors) or 'none')
        pg.close()
        for left in ex.unaccounted():
            skip(ex, left)
    # ---- the FAQ (CMB-048 claims pass)
    hub, hub_errors = new_page(ctx)
    hub.goto(BASE + '/calculators/', wait_until='load')
    faq = hub.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent,
        i.querySelector('.faq-answer').textContent, [...i.querySelectorAll('.faq-answer a[href^="http"]')].map(a => a.href)])""")
    ld = hub.evaluate("""() => JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent)['@graph']
        .find(x => x['@type'] === 'FAQPage').mainEntity.map(e => [e.name, e.acceptedAnswer.text])""")
    main_text = norm(hub.evaluate("() => document.querySelector('main').textContent"))
    hub.close()
    page.tag = '/calculators/ FAQ'
    check(page, 'JSON-LD = visible FAQ', 'equal', 'equal' if [(norm(q), norm(a)) for q, a in ld] ==
          [(norm(q), norm(a)) for q, a, _ in faq] else 'differs')
    for f in FAQ_FRAGMENTS:
        check(page, 'FAQ sentence', f[:60], f[:60] if norm(f) in main_text else 'missing')
    for pat in FAQ_NEVER:
        check(page, 'removed claim stays out', pat, 'absent' if not re.search(pat, main_text, re.I) else 'present',
              not re.search(pat, main_text, re.I))
    links = sorted({u for _, _, us in faq for u in us})
    check(page, 'FAQ outside links in the registry', 'all', ', '.join(u for u in links if u not in REG_URLS) or 'all')
    for k, quote in REG_QUOTES:
        check(page, f'registry {k} holds the quote', quote[:50], quote[:50] if quote in REG[k] else 'not in the row')
    browser.close()

print(f'\n{checks} checks, {len(failures)} failures, {len(skipped)} skipped')
for f in failures:
    print('FAIL', f)
for s in skipped:
    print('SKIP', s)
sys.exit(1 if failures or skipped else 0)
