#!/usr/bin/env python3
"""Builds /kids-bmi-calculator/ (CMB-030) from kids_stats.json. usage: python3 research/kids-build/gen_kids.py
Replaces, in kids-bmi-calculator/index.html, only what the CMB-030 prompt lets change: everything inside <main> (the H1,
the byline, #panel-kids with its controls, ids and starting values kept), and in the head the OG and Twitter images
(og:image, og:image:alt, og:image:width/height, twitter:image) and the JSON-LD. The title, the meta description, the OG
and Twitter text, the Raptive, consent and GA4 scripts, the header, the scripts after </main> (cdc-bmi-lms.js,
calculator.js, the FAQ and menu toggles) and the footer stay byte for byte, so running it twice gives the same file.
Every number on the page is one of the prompt's facts 1-3 (registry rows cdc-extended-bmi-data, cdc-child-bmi-categories,
nhanes-child-weight-trends, cdc-calculating-bmi, cdc-about-bmi) or our calculation from data/cdc/bmi-age-2022.csv through
kids_stats.json."""
import html, json, os, re
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PAGE = os.path.join(ROOT, 'kids-bmi-calculator/index.html')
S = json.load(open(os.path.join(HERE, 'kids_stats.json'), encoding='utf-8'))
SITE = 'https://calculatemybmi.net'
URL = SITE + '/kids-bmi-calculator/'
IMG = {r: f'{SITE}/assets/images/preferred/kids-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
CDC_EXT = 'https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm'
CDC_CSV = 'https://www.cdc.gov/growthcharts/data/extended-bmi/bmi-age-2022.csv'
CDC_CHILD = 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html'
CDC_CALC = 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html'
CDC_ABOUT = 'https://www.cdc.gov/bmi/about/index.html'
ESTAT = 'https://www.cdc.gov/nchs/data/hestat/hestat112.htm'
FT, IN, NB = '′', '″', '\u00a0'
ESTAT_TITLE = ('Prevalence of overweight, obesity, and severe obesity among children and adolescents ages 2–19 years: '
               'United States, 1963–1965 through August 2021–August 2023')

TITLE = 'BMI Calculator for Kids &amp; Teens (Ages 2–19): CDC Percentile'      # kept from origin/main, as the head has it
TITLE_TEXT = html.unescape(TITLE)
H1 = 'BMI Calculator for Kids and Teens'
OG_ALT = ('Chart: CDC BMI-for-age bands for boys and girls aged 2 to 20, from underweight through healthy weight, '
          'overweight and obesity to severe obesity.')

T = {sex: {r['age']: r for r in rows} for sex, rows in S['tables'].items()}
MED = S['medians']
A = S['anchors']
EX = S['examples']
AGE_EX = S['age_example']
G70, G98, B150 = A['girl-10-70'], A['girl-10-98'], A['boy-14-6-150']
CG, CB = EX['cdc_girl'], EX['cdc_boy']
assert (G98['bmi'], G98['ordinal'], G98['category']) == ('23.6', 96, 'Obesity')
assert (CB['pct_of_p95'], CB['category'], CB['aap_class']) == ('126.8', 'Severe obesity', 2)
assert (T['female'][10]['p5'], T['female'][10]['p85'], T['male'][10]['p5'], T['male'][10]['p85']) == ('14.0', '20.0', '14.2', '19.4')
assert (MED['male']['at_2'], MED['male']['lowest'], MED['male']['lowest_ages'], MED['male']['at_19']) == ('16.5', '15.4', [5, 6], '22.5')
assert (MED['female']['at_2'], MED['female']['lowest'], MED['female']['lowest_ages'], MED['female']['at_19']) == ('16.4', '15.2', [5, 6], '21.6')


def ext(href, text):
    return f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'


def nw(t):
    return f'<span class="nowrap">{t}</span>'


def eq(*parts):
    """A formula as short unbreakable pieces, so a line breaks only between them (before ÷ or =) on a 320 px phone."""
    return ' '.join(nw(x) for x in parts)


def f1(v):
    return f'{v:.1f}'


def dec_ordinal(s):
    """92.2 -> 92.2nd, 99.7683 -> 99.7683rd: the suffix of the last digit, as CDC writes them."""
    return s + {'1': 'st', '2': 'nd', '3': 'rd'}.get(s[-1], 'th')


def ordinal(n):
    v = n % 100
    return f'{n}' + ({1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') if not 11 <= v <= 13 else 'th')


# ---------------------------------------------------------------- the figure (inline SVG, 320 wide like the other D-14 figures)
INK, TEXT, LEG, AXIS = '#111827', '#4b5563', '#1f2937', '#9ca3af'
# the site's category tints, as the /bmi-chart/ figure uses them (DESIGN.md: under, healthy, over; obesity and the more
# severe band in the two red tints); white gaps between the bands carry the edges, so colour never carries them alone
BANDS = (('under', 'Underweight', '#dbeafe'), ('healthy', 'Healthy weight', '#d1fae5'), ('over', 'Overweight', '#fde68a'),
         ('obese', 'Obesity', '#fecaca'), ('severe', 'Severe obesity', '#fca5a5'))
LINES = ('p5', 'p85', 'p95', 'p120')
PW, GAP, LX = 126, 20, 34                       # panel width (216 months), gap, the boys' left edge
PAN = {'male': LX, 'female': LX + PW + GAP}
YT, YB, LO, HI = 64, 260, 12, 36                # plot top and bottom; BMI 12 to 36 on one shared axis (every edge is 35 or lower)
FIG_H = 300


def xm(sex, m):
    return PAN[sex] + (m - 24) * PW / 216


def yb(v):
    return YB - (v - LO) * (YB - YT) / (HI - LO)


def edge(p, line):
    """A band edge at one month: the series value, except that a BMI of 35 is severe obesity at any age (CDC)."""
    return min(p['p120'], 35.0) if line == 'p120' else p[line]


def series(sex, line):
    """(x, y) along a band edge: each month's row holds for the whole month, so the ends run to 24 and 240 months."""
    pts = S['figure'][sex]
    out = [(xm(sex, 24), yb(edge(pts[0], line)))]
    out += [(xm(sex, p['agemos']), yb(edge(p, line))) for p in pts]
    out.append((xm(sex, 240), yb(edge(pts[-1], line))))
    return out


def ptxt(pts):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)


def figure():
    b, g = T['male'], T['female']
    desc = (f'Two panels, boys and girls, with age from 2 to 20 years across and BMI from {LO} to {HI} up, shaded in five bands, '
            'one per CDC category: underweight below the 5th percentile, healthy weight from the 5th to the 85th, overweight '
            'from the 85th to the 95th, obesity from the 95th to 120% of the 95th or a BMI of 35, whichever is lower, and '
            'severe obesity above that. Boys at 2: '
            f'{b[2]["p5"]}, {b[2]["p85"]}, {b[2]["p95"]} and {b[2]["p120"]} (the 5th, 85th and 95th percentiles and 120% of the '
            f'95th); at 19: {b[19]["p5"]}, {b[19]["p85"]}, {b[19]["p95"]} and {b[19]["p120"]}. Girls at 2: {g[2]["p5"]}, '
            f'{g[2]["p85"]}, {g[2]["p95"]} and {g[2]["p120"]}; at 19: {g[19]["p5"]}, {g[19]["p85"]}, {g[19]["p95"]} and '
            f'{g[19]["p120"]}. Our calculation from CDC’s data file.')
    t = [f'<figure class="figure"><svg viewBox="0 0 320 {FIG_H}" role="img" aria-labelledby="kids-t kids-d" '
         'xmlns="http://www.w3.org/2000/svg" font-family="inherit">'
         '<title id="kids-t">BMI-for-age charts for boys and girls: CDC’s five weight categories from age 2 to 20</title>'
         f'<desc id="kids-d">{desc}</desc>']
    est = lambda s: 6.6 * len(s)                    # a generous width for 12-unit text, so legend entries never touch
    for row, y in ((BANDS[:3], 14), (BANDS[3:], 32)):
        widths = [18 + est(name) for _, name, _ in row]
        x = (320 - (sum(widths) + 12 * (len(widths) - 1))) / 2
        for (key, name, fill), wd in zip(row, widths):
            t.append(f'<rect data-key="{key}" x="{f1(x)}" y="{y - 10}" width="12" height="12" fill="{fill}" stroke="{AXIS}" '
                     'stroke-width="0.75"/>')
            t.append(f'<text x="{f1(x + 18)}" y="{y}" font-size="12" fill="{LEG}">{name}</text>')
            x += wd + 12
    for sex, word in (('male', 'Boys'), ('female', 'Girls')):
        t.append(f'<text x="{f1(PAN[sex] + PW / 2)}" y="54" font-size="12" font-weight="600" text-anchor="middle" '
                 f'fill="{INK}">{word}</text>')
    t.append(f'<text x="{LX - 8}" y="50" font-size="12" text-anchor="end" fill="{TEXT}">BMI</text>')
    for v in range(LO, HI + 1, 4):
        t.append(f'<text x="{LX - 8}" y="{f1(yb(v) + 4)}" font-size="12" text-anchor="end" fill="{TEXT}">{v}</text>')
    for sex in PAN:
        x0, x1 = xm(sex, 24), xm(sex, 240)
        below = [(x0, yb(LO)), (x1, yb(LO))]
        above = [(x0, yb(HI)), (x1, yb(HI))]
        edges = [below] + [series(sex, ln) for ln in LINES] + [above]
        for (key, _, fill), lo, hi in zip(BANDS, edges, edges[1:]):
            t.append(f'<polygon data-sex="{sex}" data-band="{key}" points="{ptxt(lo + hi[::-1])}" fill="{fill}"/>')
        for v in range(LO + 4, HI, 4):              # grid: a faint ink hairline over the tints
            t.append(f'<line x1="{f1(x0)}" y1="{f1(yb(v))}" x2="{f1(x1)}" y2="{f1(yb(v))}" stroke="{INK}" stroke-opacity="0.12" '
                     'stroke-width="0.75"/>')
        for ln in LINES:                            # the band edges as white gaps
            t.append(f'<polyline data-sex="{sex}" data-line="{ln}" points="{ptxt(series(sex, ln))}" fill="none" '
                     'stroke="#ffffff" stroke-width="1.5" stroke-linejoin="round"/>')
        t.append(f'<line x1="{f1(x0)}" y1="{YB}" x2="{f1(x1)}" y2="{YB}" stroke="{AXIS}" stroke-width="1"/>')
        for age in (2, 5, 10, 15, 20):
            xx = xm(sex, age * 12)
            t.append(f'<line x1="{f1(xx)}" y1="{YB}" x2="{f1(xx)}" y2="{YB + 4}" stroke="{AXIS}" stroke-width="1"/>')
            t.append(f'<text x="{f1(xx)}" y="{YB + 16}" font-size="12" text-anchor="middle" fill="{TEXT}">{age}</text>')
        t.append(f'<text x="{f1(PAN[sex] + PW / 2)}" y="{YB + 32}" font-size="12" text-anchor="middle" fill="{TEXT}">'
                 'Age (years)</text>')
    for sex, word in (('male', 'Boys'), ('female', 'Girls')):     # hover: one column per year of age
        for age in range(2, 20):
            r = T[sex][age]
            lx, rx = xm(sex, age * 12), xm(sex, age * 12 + 12)
            extra = ' (severe obesity from 35)' if Decimal(r['p120']) > 35 else ''
            t.append(f'<rect x="{f1(lx)}" y="{YT}" width="{f1(rx - lx)}" height="{YB - YT}" fill="#ffffff" fill-opacity="0">'
                     f'<title>{word} at {age} years: 5th percentile {r["p5"]}, 85th {r["p85"]}, 95th {r["p95"]}, 120% of the '
                     f'95th {r["p120"]}{extra}</title></rect>')
    t.append('</svg><figcaption>Our calculation from CDC’s data file, month by month. The tables below give the values at each '
             'birthday.</figcaption></figure>')
    return ''.join(t)


# ---------------------------------------------------------------- tables
def chart_table(sex):
    word = 'Boys' if sex == 'male' else 'Girls'
    head = ('<thead><tr><th scope="col">Age</th><th scope="col" class="num">5th</th><th scope="col" class="num">50th</th>'
            '<th scope="col" class="num">85th</th><th scope="col" class="num">95th</th>'
            '<th scope="col" class="num">120% of 95th</th></tr></thead>')
    body = ''.join(f'<tr id="{word.lower()}-{r["age"]}"><th scope="row">{r["age"]}</th>'
                   + ''.join(f'<td class="num">{r[k]}</td>' for k in ('p5', 'p50', 'p85', 'p95', 'p120')) + '</tr>'
                   for r in S['tables'][sex])
    return ('<div class="table-responsive"><table class="data-table data-table--fit data-table--tight">'
            f'<caption>{word}: BMI at each percentile, ages 2 to 19</caption>' + head + f'<tbody>{body}</tbody></table></div>')


CATS = (('underweight', 'Underweight', 'Less than the 5th percentile'),
        ('normal', 'Healthy weight', '5th percentile to less than the 85th percentile'),
        ('overweight', 'Overweight', '85th to less than the 95th percentile'),
        ('obese', 'Obesity', '95th percentile or greater'),
        ('obese-severe', 'Severe obesity', '120% of the 95th percentile or greater, or a BMI of 35 or greater'))


def categories_table():
    rows = ''.join(f'<tr><th scope="row"><span class="cat-dot {c}" aria-hidden="true"></span>{name}</th><td>{rule}</td></tr>'
                   for c, name, rule in CATS)
    return ('<div class="table-responsive"><table class="data-table data-table--fit">'
            '<caption>BMI categories for children and teens aged 2 through 19 (CDC)</caption>'
            '<thead><tr><th scope="col">Category</th><th scope="col">Percentile</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


# ---------------------------------------------------------------- the calculator (shared parts; ids and starting values kept)
def field(fid, label, cls, value, lo, hi):
    return (f'<div class="form-group"><label class="form-label" for="{fid}">{label}</label>'
            f'<input type="number" id="{fid}" class="form-input {cls}" value="{value}" min="{lo}" max="{hi}"></div>')


CALC = ('<div class="calculator-card"><div id="panel-kids" class="calc-panel active">'
        '<div class="unit-toggle"><button class="unit-btn active" data-unit="imperial">Imperial</button>'
        '<button class="unit-btn" data-unit="metric">Metric</button></div>'
        '<div class="form-grid">'
        '<div class="form-row form-row--trio imperial-inputs">'
        + field('kids-height-ft', 'Height (ft)', 'height-ft', 4, 1, 7)
        + field('kids-height-in', 'Height (in)', 'height-in', 6, 0, 11)
        + field('kids-weight-lbs', 'Weight (lb)', 'weight-lbs', 70, 20, 300) + '</div>'
        '<div class="form-row form-row--pair metric-inputs" hidden>'
        + field('kids-height-cm', 'Height (cm)', 'height-cm', 137, 50, 200)
        + field('kids-weight-kg', 'Weight (kg)', 'weight-kg', 32, 10, 150) + '</div>'
        '<div class="form-row form-row--trio">'
        + field('kids-age-years', 'Age (years)', 'age-input', 10, 2, 19)
        + field('kids-age-months', 'Age (months)', 'months-input', 0, 0, 11)
        + '<div class="form-group"><label class="form-label" for="kids-sex">Sex</label><select id="kids-sex" '
          'class="form-select sex-select"><option value="female">Girl</option><option value="male">Boy</option></select></div>'
        '</div></div>'
        '<button class="calculate-btn" id="calc-kids-btn">Calculate Pediatric BMI</button>'
        '<div class="results-section" id="kids-results"><div class="bmi-result-card normal" id="kids-result-card">'
        '<div class="bmi-value normal" id="kids-bmi-value">—</div><div class="bmi-category" id="kids-bmi-category">—</div>'
        '<div class="bmi-range" id="kids-percentile-note">—</div></div></div>'
        '</div></div>')

# ---------------------------------------------------------------- worked examples
st_b, st_g, st_14 = CB['steps'], EX['girl_10_98']['steps'], EX['boy_14_6_150']['steps']
g98x, b150x = EX['girl_10_98'], EX['boy_14_6_150']
EXAMPLES = (
    '<h3>CDC’s example: a girl of 9 years 6 months, BMI 21.2</h3>'
    f'<p>Her row is {CG["row"]} months, where the 95th percentile is {CG["p95"]}. Her BMI is below it, so the LMS '
    f'formula applies. CDC works it out to a z-score of {CG["z4"]}, the {dec_ordinal(CG["percentile"])} percentile. That is between the '
    f'85th and the 95th, so she is in the overweight category; the calculator shows the {ordinal(CG["ordinal"])} percentile '
    f'and z = {CG["z"]}.</p>'
    '<h3>CDC’s example: a boy of 4 years 2 months, BMI 22.6</h3>'
    f'<p>His row is {CB["row"]} months: the 95th percentile is {st_b["p95"]} and sigma {st_b["sigma"]}. His BMI is above the '
    f'95th, so the extended formula applies: {eq(f"(22.6 − {st_b['p95']})", f"÷ {st_b['sigma']}", f"= {st_b['arg4']}")}, '
    f'Φ({st_b["arg4"]}) = {st_b["phi5"]}, and {eq(f"90 + 10 × {st_b['phi5']}", f"= {CB['percentile4']}")}, the '
    f'{dec_ordinal(CB["percentile4"])} percentile. A BMI of 22.6 is {CB["pct_of_p95"]}% of his row’s 95th percentile, '
    'over the 120% line, so the category is severe obesity, which the American Academy of Pediatrics calls class 2 obesity '
    '(120% to under 140%). The calculator shows it as above the 99th percentile.</p>'
    f'<h3>A 10-year-old girl, {G98["height"]} and {G98["lb"]} lb</h3>'
    f'<p>Her BMI is {eq(f"703 × {G98['lb']}", '÷ 54²', f"= {g98x['bmi_exact2']}")}, shown as {G98["bmi"]}. At 10 years 0 months her '
    f'row is {G98["row"]} months, where the 95th percentile is {st_g["p95"]} ({g98x["p95_1dp"]} in the table) and sigma '
    f'{st_g["sigma"]}. Her BMI is above the 95th, so the extended formula applies: '
    f'{eq(f"90 + 10 × Φ(({g98x['bmi_exact2']} − {st_g['p95']})", f"÷ {st_g['sigma']})")} gives {G98["percentile"]}, the '
    f'{ordinal(G98["ordinal"])} percentile, which is obesity. Her BMI is {G98["pct_of_p95"]}% of the 95th percentile, short '
    'of the 120% that would make it severe obesity.</p>'
    f'<h3>A boy of 14 years 6 months, {B150["height"]} and {B150["lb"]} lb</h3>'
    f'<p>His BMI is {eq(f"703 × {B150['lb']}", '÷ 65²', f"= {b150x['bmi_exact2']}")}, shown as {B150["bmi"]}. His row is '
    f'{B150["row"]} months, with a 95th percentile of {st_14["p95"]}, so the LMS formula applies with the row’s '
    f'L = −{st_14["L4"]}, M = {st_14["M4"]} and S = {st_14["S4"]}: '
    f'{eq(f"z = (({b150x['bmi_exact2']} ÷ {st_14['M4']})<sup>−{st_14['L4']}</sup>", '− 1)', f"÷ (−{st_14['L4']} × {st_14['S4']})", f"= {st_14['z2_again']}")}'
    f', a percentile of {B150["percentile"]}. The calculator shows the {ordinal(B150["ordinal"])} '
    'percentile, in the overweight category.</p>')
assert CG['percentile'] == '92.2' and CG['ordinal'] == 92 and CG['category'] == 'Overweight'
assert B150['category'] == 'Overweight' and G98['category'] == 'Obesity' and CB['line'] == 'Above the 99th percentile'

# ---------------------------------------------------------------- FAQ (plain text answers, so the JSON-LD is the visible text)
g10, b10 = T['female'][10], T['male'][10]
mb, mg = MED['male'], MED['female']
FAQ = [
    ('What is a healthy BMI for a child?',
     f'For a child or teen, a healthy weight is a BMI from the 5th to below the 85th percentile for their age and sex. On '
     f'CDC’s charts at age 10, a girl’s healthy BMI runs from {g10["p5"]} to just under {g10["p85"]} and a boy’s from '
     f'{b10["p5"]} to just under {b10["p85"]}. The tables above list every age.'),
    ('How is BMI calculated for a child?',
     'With the adult formula: weight in pounds divided by height in inches squared, times 703, or weight in kilograms '
     'divided by height in meters squared. CDC then places that BMI on its BMI-for-age chart for the child’s sex and age in '
     'months, which gives the percentile and the category.'),
    ('What does a BMI percentile mean?',
     'It shows where a child’s BMI sits among children of the same sex and age on CDC’s growth charts. In CDC’s words, '
     '“Because children and teens are growing, their BMI values are expressed relative to others of the same sex and age. '
     'These values are called BMI-for-age percentiles.”'),
    ('What are the 85th and 95th percentiles?',
     f'Overweight is a BMI at or above the 85th percentile for the child’s age and sex, and obesity is at or above the 95th. '
     f'On CDC’s charts at age 10, they are {b10["p85"]} and {b10["p95"]} for boys and {g10["p85"]} and {g10["p95"]} for '
     f'girls; the tables above list every age.'),
    ('What is severe obesity in children?',
     'CDC defines it as a BMI at or above 120% of the 95th percentile for age and sex, or a BMI of 35 or more. CDC adds that '
     '“the American Academy of Pediatrics uses an expanded definition of severe obesity”: class 2 obesity is 120% to less '
     'than 140% of the 95th percentile, or a BMI of 35 to less than 40, and class 3 obesity is 140% of the 95th percentile '
     'or more, or a BMI of 40 or more. For severe obesity, the calculator shows the class under the category.'),
    ('What is a BMI z-score?',
     'The BMI on CDC’s standard scale, where 0 is the median for the child’s age and sex. At or below the 95th percentile '
     'it comes from the LMS formula, z = ((BMI ÷ M)^L − 1) ÷ (L × S), and a z-score of 1.645 is the 95th percentile. '
     'Above it, CDC’s extended charts work out the percentile first and turn it into a z-score, up to 5. The calculator '
     'shows the z-score under the percentile.'),
    ('Why does my child’s BMI change as they grow?',
     f'BMI changes with age in growing children, and not in one direction. The median BMI for boys is {mb["at_2"]} at age 2, '
     f'{mb["lowest"]} at 5 and 6 and {mb["at_19"]} at 19; for girls it is {mg["at_2"]}, {mg["lowest"]} and {mg["at_19"]}. '
     'That is why CDC’s categories go by the percentile for the child’s age, not by the BMI alone.'),
    ('Can I use adult BMI categories for my teenager?',
     f'No. CDC’s child and teen categories cover ages 2 through 19, and the adult categories start at 20. The same BMI '
     f'reads differently: {G98["bmi"]} is in the adult healthy range, but for a 10-year-old girl it is the '
     f'{ordinal(G98["ordinal"])} percentile, which is obesity.'),
    ('What ages does this calculator cover?',
     '2 years 0 months to 19 years 11 months (24 to 239 months), the ages CDC’s child and teen categories cover. From 20, '
     'use the <a href="/">adult BMI calculator</a>.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')


def faq_html(items):
    return ('<div class="faq-list flat">' + ''.join(
        f'<div class="faq-item"><button class="faq-question">{q}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
        for q, a in items) + '</div>')


# ---------------------------------------------------------------- the page
a5, a19 = AGE_EX['girl_5'], AGE_EX['girl_19']
MAIN = (
    '<main class="reading"><div class="container">'
    '<div class="page-head">'
    f'<h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Enter your child’s age, sex, height and weight to get their BMI-for-age percentile and CDC weight '
    'category.</p>'
    '<p class="intro-note">For ages 2 through 19, with CDC’s BMI-for-age growth charts. <a href="#sources">Method and '
    'sources</a></p>'
    '</div>'
    + CALC +
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer">A child’s BMI is worked out the same way as an adult’s, then compared with <strong>CDC’s BMI-for-age '
    'charts</strong> for the child’s sex and age in months. The percentile sets the category: under the 5th is underweight, '
    'the 5th to below the 85th healthy weight, the 85th to below the 95th overweight, and the 95th or above obesity.</p>'
    '<ul>'
    '<li>Severe obesity is a BMI at or above 120% of the 95th percentile, or 35 or more. The American Academy of Pediatrics '
    'splits it into class 2 (120% to under 140%) and class 3 (140% or more).</li>'
    f'<li>The same BMI means different things at different ages: {G98["bmi"]} is in the adult healthy range, but for a '
    f'10-year-old girl it sits at the {ordinal(G98["ordinal"])} percentile, which is obesity.</li>'
    '<li>Up to the 95th percentile the charts are CDC’s 2000 growth charts; above it, CDC’s 2022 extended charts give '
    'percentiles up to the 99.99th.</li>'
    '<li>In CDC’s measured survey for August 2021–August 2023, 21.1% of children and teens aged 2–19 had obesity.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information only. '
    'BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>'
    '<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
    '<a href="#categories">Categories</a><a href="#chart">Charts</a><a href="#how">How it works</a>'
    '<a href="#examples">Examples</a><a href="#age">BMI and age</a><a href="#prevalence">How common</a>'
    '<a href="#faq">FAQ</a><a href="#sources">Sources</a></nav>'

    '<section id="categories" class="content-section flow"><h2>CDC BMI categories for children and teens</h2>'
    '<p>The same five categories apply from age 2 through 19.</p>'
    + categories_table() +
    f'<p>CDC adds that “the American Academy of Pediatrics uses an expanded definition of severe obesity,” in two classes:</p>'
    '<ul><li><strong>Class 2 obesity:</strong> 120% to less than 140% of the 95th percentile, or a BMI of 35 to less than '
    '40.</li><li><strong>Class 3 obesity:</strong> 140% of the 95th percentile or greater, or a BMI of 40 or greater.</li></ul>'
    '<p>The calculator shows CDC’s category, and for severe obesity it adds the class on the line under it. CDC also notes: '
    '“Race is not a factor used in calculating BMI percentiles.”</p>'
    '</section>'

    '<section id="chart" class="content-section flow"><h2>BMI-for-age charts for boys and girls</h2>'
    '<p>Each band is one CDC category. The edges are the 5th, 85th and 95th percentiles and 120% of the 95th (or a BMI of 35, '
    'where that is lower) for every month from age 2 to 20, the values the calculator reads.</p>'
    + figure() +
    '<p>In the tables, each row is the month that starts at the birthday: the row for 10 is 10 years 0 months, the '
    '120.5-month row in CDC’s file. The values shift a little from one month to the next, and the calculator uses the '
    'child’s own month.</p>'
    + chart_table('male') + chart_table('female') +
    f'<p class="source-note">Source: {ext(CDC_EXT, "CDC’s data file for the extended BMI-for-age growth charts")}; our '
    'calculation, rounded to 0.1. A BMI of 35 or more is severe obesity at any age, so where 120% of the 95th is above 35 '
    '(boys at 19, girls from 17), severe obesity starts at 35.</p>'
    '</section>'

    '<section id="how" class="content-section flow"><h2>How the calculator works</h2>'
    f'<p>It works out BMI with {ext(CDC_CALC, "CDC’s formula")}: 703 × weight in pounds ÷ height in inches², or weight in '
    'kilograms ÷ height in meters². Then it reads the child’s row in CDC’s '
    f'{ext(CDC_EXT, "data file for the extended BMI-for-age growth charts")}, which lists the values for boys and girls month '
    'by month. CDC explains how a row covers the month: “Age is listed at the half month point for the entire month; for '
    'example, 48.5 months represents 48.0 months up to but not including 49.0 months of age.” So a child of 2 years 0 '
    'months reads the 24.5-month row, and one of 9 years 6 months the 114.5-month row. The calculator takes any age from 24 '
    'to 239 months.</p>'
    '<p>At or below the row’s 95th percentile, the percentile comes from the LMS formula, with the row’s L, M and S: '
    f'{eq("z = ((BMI ÷ M)<sup>L</sup> − 1)", "÷ (L × S)")}, and the percentile is Φ(z) × 100, where Φ is the cumulative standard '
    'normal distribution. CDC writes that “BMI percentiles and z-scores up to the 95th percentile (z-score 1.645) are the '
    'same as those in the 2000 CDC BMI-for-age growth charts.”</p>'
    '<p>Above the 95th, the extended charts use the row’s 95th percentile (P95) and its sigma: '
    f'{eq("percentile = 90 + 10", "× Φ((BMI − P95)", "÷ sigma)")}, and the z-score is Φ<sup>−1</sup> of that percentile ÷ 100. '
    'That is how they add percentiles “above the 95th percentile up to the 99.99th percentile (z-scores up to 5).”</p>'
    '<p>The calculator also gives BMI as a percentage of the 95th percentile, 100 × BMI ÷ P95. Severe obesity starts at '
    '120%, and the American Academy of Pediatrics’ class 3 at 140%.</p>'
    f'<p>BMI is a screening measure. {ext(CDC_ABOUT, "CDC notes")} that “BMI does not distinguish between fat, muscle, and '
    'bone mass.”</p>'
    '</section>'

    '<section id="examples" class="content-section flow"><h2>Four worked examples</h2>'
    '<p>The first two are CDC’s own examples from its data file page. We typed the other two into the calculator above.</p>'
    + EXAMPLES +
    '</section>'

    '<section id="age" class="content-section flow"><h2>How BMI changes with age</h2>'
    '<p>CDC gives the reason children are measured against their own age and sex: “Because children and teens are growing, '
    'their BMI values are expressed relative to others of the same sex and age. These values are called BMI-for-age '
    'percentiles.”</p>'
    f'<p>The median shows how far BMI moves. For boys it is {mb["at_2"]} at age 2, falls to {mb["lowest"]} at 5 and 6, and '
    f'climbs to {mb["at_19"]} at 19. For girls it is {mg["at_2"]} at 2, {mg["lowest"]} at 5 and 6, and {mg["at_19"]} at 19.</p>'
    f'<p>A single cut-off can’t follow that: a BMI of {AGE_EX["bmi"]} is above the 85th percentile for a 5-year-old girl '
    f'({a5["p85"]}), so it is overweight, but below the 5th for a 19-year-old ({a19["p5"]}), so it is underweight.</p>'
    '</section>'

    '<section id="prevalence" class="content-section flow"><h2>How common obesity is in children</h2>'
    '<p>In CDC’s measured survey for August 2021–August 2023, 21.1% of children and teens aged 2–19 had obesity and 7.0% '
    f'had severe obesity ({ext(ESTAT, "NCHS Health E-Stat 112")}). The '
    '<a href="/childhood-obesity-statistics/">childhood obesity statistics</a> page has the trend and the figures by age '
    'and sex.</p>'
    '</section>'

    '<section id="faq" class="content-section"><h2>Frequently asked questions</h2>'
    + faq_html(FAQ) +
    '</section>'

    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means worked out as described '
    'below.</p>'
    '<ul class="source-list">'
    f'<li>CDC. {ext(CDC_EXT, "Data file for the CDC Extended BMI-for-Age Growth Charts")} (last reviewed September 2, '
    f'2024), and the file itself, {ext(CDC_CSV, "bmi-age-2022.csv")}.</li>'
    f'<li>CDC. {ext(CDC_CHILD, "Child and Teen BMI Categories")} (June 28, 2024).</li>'
    f'<li>CDC. {ext(CDC_CALC, "Calculating BMI")}; {ext(CDC_ABOUT, "About Body Mass Index (BMI)")}.</li>'
    f'<li>NCHS. {ext(ESTAT, ESTAT_TITLE)}. Health E-Stat 112.</li>'
    '</ul>'
    '<p class="source-note"><strong>Method.</strong> The tables, the figure and the examples come from CDC’s data file, '
    'bmi-age-2022.csv, used unchanged; the calculator holds the same values to 8 significant digits, which changes no '
    'number shown here. BMI is CDC’s formula (US units × 703, or kg/m²), shown to 0.1. The calculator reads the row for the '
    'child’s month of age, the whole months plus 0.5, so 2 years 0 months is the 24.5-month row. At or below the row’s 95th '
    'percentile it uses the LMS formula; above it, CDC’s extended formula with the row’s sigma. Severe obesity is 120% of '
    'the row’s 95th percentile or a BMI of 35. The tables give the row that starts at each birthday (age × 12 + 0.5 '
    'months), with CDC’s percentile columns rounded half up to 0.1; the figure plots every month from 24.5 to 239.5.</p>'
    '</section>'

    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul><li><a href="/">BMI calculator</a></li>'
    '<li><a href="/women-bmi-calculator/">BMI calculator for women</a></li>'
    '<li><a href="/men-bmi-calculator/">BMI calculator for men</a></li>'
    '<li><a href="/body-fat-calculator/">Body fat calculator</a></li></ul></div>'
    '<div><h3>Guides and data</h3><ul><li><a href="/childhood-obesity-statistics/">Childhood obesity statistics</a></li>'
    '<li><a href="/body-fat-percentage-chart/">Body fat percentage chart</a></li>'
    '<li><a href="/blog/bmi-categories/">BMI categories</a></li>'
    '<li><a href="/blog/bmi-limitations/">Limitations of BMI</a></li></ul></div>'
    '</div></section>'
    '</div></main>')


def nbsp_units(markup):
    """A number keeps its unit on one line (DEVLOG §4, CMB-021): a no-break space between them, in text only."""
    unit = re.compile(r'(\d) (lb|lbs|kg|cm|in|inches|feet|months)(?![\w])')
    out = []
    for chunk in re.split(r'(?s)(<svg\b.*?</svg>)', markup):           # SVG text never wraps: leave the figure alone
        out.append(chunk if chunk.startswith('<svg') else
                   ''.join(p if p.startswith('<') else unit.sub('\\1\u00a0\\2', p) for p in re.split(r'(<[^>]+>)', chunk)))
    return ''.join(out)


MAIN = nbsp_units(MAIN)
FAQ = [(q, nbsp_units(a)) for q, a in FAQ]


def faq_text(a):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', a)).replace('\u00a0', ' ')).strip()


LD = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE_TEXT,
     'isPartOf': {'@id': SITE + '/#website'}, 'mainEntity': {'@id': URL + '#calculator'},
     'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG['16x9'], 'width': 1200, 'height': 675}},
    {'@type': 'WebApplication', '@id': URL + '#calculator', 'image': [IMG['1x1'], IMG['4x3'], IMG['16x9']],
     'name': H1,
     'description': ('Calculates BMI, the BMI-for-age percentile, the z-score and the CDC weight category for children and '
                     'teens aged 2 through 19 from age in years and months, sex, height and weight in US or metric units, '
                     'with CDC’s data file for the extended BMI-for-age growth charts, and names the American Academy of '
                     'Pediatrics’ class for severe obesity.'),
     'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any',
     'browserRequirements': 'Requires JavaScript', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
     'featureList': ['BMI-for-age percentile and z-score from CDC’s data file, month by month',
                     'CDC weight category for ages 2 through 19',
                     'BMI as a percentage of the 95th percentile',
                     'The American Academy of Pediatrics’ class 2 or class 3 for severe obesity'],
     'author': {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}},
    {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Calculators', 'item': SITE + '/calculators/'},
        {'@type': 'ListItem', 'position': 3, 'name': H1, 'item': URL}]},
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': faq_text(a)}}
                                        for q, a in FAQ]}]}


def put_meta(src, attr, name, value, after=None):
    tag = f'<meta {attr}="{name}" content="{html.escape(value, quote=True)}">'
    pat = re.compile(rf'<meta {attr}="{re.escape(name)}" content="[^"]*">')
    if pat.search(src):
        assert len(pat.findall(src)) == 1, name
        return pat.sub(lambda _: tag, src)
    a = re.search(rf'<meta {after[0]}="{re.escape(after[1])}" content="[^"]*">', src)
    return src[:a.end()] + '\n' + tag + src[a.end():]


def build(src):
    assert '"' not in OG_ALT
    head, rest = src.split('</head>', 1)
    assert f'<title>{TITLE}</title>' in head and head.count('<title>') == 1, 'the title changed'
    head = put_meta(head, 'property', 'og:image', IMG['16x9'])
    head = put_meta(head, 'property', 'og:image:alt', OG_ALT, after=('property', 'og:image'))
    head = put_meta(head, 'property', 'og:image:width', '1200')
    head = put_meta(head, 'property', 'og:image:height', '675')
    head = put_meta(head, 'name', 'twitter:image', IMG['16x9'])
    blocks = list(re.finditer(r'(?s)[ \n]?<script type="application/ld\+json">.*?</script>', head))
    assert blocks, 'no JSON-LD in the head'
    ld = '\n<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>'
    head = head[:blocks[0].start()] + ld + ''.join(head[a.end():b.start()] for a, b in zip(blocks, blocks[1:])) + head[blocks[-1].end():]
    body = re.sub(r'(?s)<main\b.*?</main>', lambda _: MAIN, rest, count=1)
    return head + '</head>' + body


def words(markup):
    return len(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<svg.*?</svg>', ' ', markup)))).split())


if __name__ == '__main__':
    src = open(PAGE, encoding='utf-8').read()
    out = build(src)
    assert build(out) == out, 'not idempotent'
    with open(PAGE, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'{PAGE}: {len(out):,} bytes; <main> {len(MAIN):,} bytes, about {words(MAIN)} words outside the figure')
