#!/usr/bin/env python3
"""Builds /ideal-weight/ (CMB-028) from iw_stats.json. usage: python3 research/ideal-weight-build/gen_iw.py
Replaces, in ideal-weight/index.html, only what the page owns: everything inside <main>, and in the head the title, the meta
description, the og:* and twitter:* text and images and the JSON-LD. The Raptive, consent and GA4 scripts, the header, the
scripts after </main> (calculator.js, the FAQ and menu toggles) and the footer stay byte for byte, so running it twice gives
the same file. Every number on the page comes from iw_stats.json (our calculation with calculator.js's arithmetic) or is one
of the CMB-028 prompt's facts 1-7 (registry rows pai-paloucek-2000-ibw, robinson-1983-ibw, peterson-2016-ibw,
davidson-2015-hamwi-dbw, medlineplus-frame-size, cdc-calculating-bmi, cdc-adult-bmi-categories, cdc-about-bmi,
cdc-child-bmi-categories)."""
import html, json, os, re
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PAGE = os.path.join(ROOT, 'ideal-weight/index.html')
S = json.load(open(os.path.join(HERE, 'iw_stats.json'), encoding='utf-8'))
SITE = 'https://calculatemybmi.net'
URL = SITE + '/ideal-weight/'
IMG = {r: f'{SITE}/assets/images/preferred/ideal-weight-{r}.png' for r in ('1x1', '4x3', '16x9')}
PAI = 'https://pubmed.ncbi.nlm.nih.gov/10981254/'
ROBINSON = 'https://pubmed.ncbi.nlm.nih.gov/6869387/'
PETERSON = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4841935/'
DAVIDSON = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4503941/'
MEDLINE = 'https://medlineplus.gov/ency/imagepages/17182.htm'
CDC_CALC = 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html'
CDC_CATS = 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html'
CDC_ABOUT = 'https://www.cdc.gov/bmi/about/index.html'
CDC_CHILD = 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html'
FT, IN, NB = '′', '″', '\u00a0'
ROB_TITLE = 'Determination of ideal body weight for drug dosage calculations'
PET_TITLE = 'Universal equation for estimating ideal body weight and body weight at any BMI'

TITLE = 'Ideal Body Weight Calculator (IBW): 4 Formulas Compared'
H1 = 'Ideal Body Weight Calculator'
DESC = ('How much should you weigh? Get your ideal body weight from the Devine, Robinson, Miller and Hamwi formulas, '
        'next to the healthy BMI range for your height.')
OG_ALT = ('Chart: the Hamwi, Devine, Robinson and Miller ideal body weights by height for women and men, drawn over the '
          'healthy BMI weight range at each height.')
NAMES = ('hamwi', 'devine', 'robinson', 'miller')
LABEL = {'hamwi': 'Hamwi', 'devine': 'Devine', 'robinson': 'Robinson', 'miller': 'Miller'}
YEAR = {'hamwi': 1964, 'devine': 1974, 'robinson': 1983, 'miller': 1983}

T = {sex: {r['inches']: r for r in rows} for sex, rows in S['tables'].items()}
FR = {sex: {r['inches']: r for r in rows} for sex, rows in S['frames'].items()}
AG = S['agree']
EXW, EXM = S['examples']['woman_5_6'], S['examples']['man_5_10']
FTAB = S['formula_table']
w60, w66, w72 = T['female'][60], T['female'][66], T['female'][72]
m60, m70, m78 = T['male'][60], T['male'][70], T['male'][78]
WN, MW = AG['female']['narrowest'][0], AG['male']['widest'][0]
MN = AG['male']['narrowest']
W66F, M70L = FR['female'][66], EXM['large']
assert w66['span']['lb'] == [130, 135] and w66['healthy']['lb'] == [115, 154] and m78['span']['lb'] == [180, 214]
assert [x['height'] for x in MN] == ['5′5″', '5′6″'] and MN[0]['width'] == MN[1]['width'] == 3
assert WN['height'] == '5′8″' and WN['lb'] == [138, 141] and AG['female']['widest'][0]['lb'] == [100, 117] and MW['height'] == '6′6″'
assert m78['miller']['lb'] == MW['lb'][0] and m78['hamwi']['lb'] == MW['lb'][1]


def ext(href, text):
    return f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'


def to(a, b, unit=''):
    return f'{a} to {b}' + (f' {unit}' if unit else '')


def ft_in(i):
    return f'{i // 12}{FT}{i % 12}{IN}'


def cm1(x):
    return f'{Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)}'


def per_inch_lb(sex):
    """The four formulas' pounds per inch, as the formulas table prints them (lowest, highest)."""
    vals = []
    for n in NAMES:
        f = FTAB[sex][n]
        vals.append(Decimal(f['per_inch'] if f['unit'] == 'lb' else f['per_inch_other']))
    return f'{min(vals):f}', f'{max(vals):f}'


# ---------------------------------------------------------------- the figure (inline SVG, 320 wide like the other D-14 figures)
INK, TEXT, GRID, AXIS, BAND = '#111827', '#4b5563', '#e5e7eb', '#9ca3af', '#d1fae5'
# ink, pink-700, cyan-600, amber-700: every neighbouring pair in this order passes the dataviz validator for colour-blind and
# normal vision; the Devine and Miller lines are dashed, so a line drawn under another shows through the gaps (CMB-028)
STYLE = {'hamwi': ('#111827', None), 'devine': ('#be185d', '7 4'), 'robinson': ('#0891b2', None), 'miller': ('#b45309', '2.5 2.5')}
K, GAP, LX = 8.0, 30, 34                        # units per inch in both panels, the gap between them, the women's left edge
PAN = {'female': (LX, 60, 72), 'male': (LX + 12 * K + GAP, 60, 78)}
YT, YB, LO, HI = 64, 232, 90, 220               # plot top and bottom; 90 to 220 lb on one shared axis
FIG_H = 270


def xs(sex, i):
    x0, a, _ = PAN[sex]
    return x0 + (i - a) * K


def ys(lb):
    return YB - (lb - LO) * (YB - YT) / (HI - LO)


def f1(v):
    return f'{v:.1f}'


def sex_word(sex):
    return 'women' if sex == 'female' else 'men'


def figure():
    desc = (f'Lines for the Hamwi, Devine, Robinson and Miller formulas at a medium frame, in pounds, over the healthy BMI '
            f'range (18.5 to 24.9) at each height. Women, 5′0″ to 6′0″: {to(*w60["span"]["lb"])} lb at 5′0″ (healthy '
            f'{to(*w60["healthy"]["lb"])} lb) and {to(*w72["span"]["lb"])} lb at 6′0″ (healthy {to(*w72["healthy"]["lb"])} lb), '
            f'closest at {WN["height"]} ({to(*WN["lb"])} lb). Men, 5′0″ to 6′6″: {to(*m60["span"]["lb"])} lb at 5′0″ and '
            f'{to(*MW["lb"])} lb at 6′6″ (healthy {to(*m78["healthy"]["lb"])} lb), closest at 5′5″ and 5′6″, '
            f'{MN[0]["width"]} lb apart. Our calculation.')
    t = [f'<figure class="figure"><svg viewBox="0 0 320 {FIG_H}" role="img" aria-labelledby="iw-t iw-d" '
         'xmlns="http://www.w3.org/2000/svg" font-family="inherit">'
         '<title id="iw-t">Ideal body weight by height: the four formulas over the healthy BMI range, women and men</title>'
         f'<desc id="iw-d">{desc}</desc>']
    est = lambda s: 6.9 * len(s)                    # a generous width for 12-unit text, so legend entries never touch
    widths = [20 + est(LABEL[n]) for n in NAMES]
    x = (320 - (sum(widths) + 12 * (len(widths) - 1))) / 2
    for n, wd in zip(NAMES, widths):
        col, dash = STYLE[n]
        cap = f' stroke-dasharray="{dash}" stroke-linecap="butt"' if dash else ' stroke-linecap="round"'
        t.append(f'<line x1="{f1(x)}" y1="10" x2="{f1(x + 16)}" y2="10" stroke="{col}" stroke-width="2"{cap}/>')
        t.append(f'<text x="{f1(x + 20)}" y="14" font-size="12" fill="{TEXT}">{LABEL[n]}</text>')
        x += wd + 12
    band_lab = 'Healthy BMI range (18.5 to 24.9)'
    x = (320 - (20 + est(band_lab))) / 2
    t.append(f'<rect x="{f1(x)}" y="24" width="16" height="10" fill="{BAND}"/>')
    t.append(f'<text x="{f1(x + 20)}" y="33" font-size="12" fill="{TEXT}">{band_lab}</text>')
    for sex, (x0, a, b) in PAN.items():
        t.append(f'<text x="{f1((x0 + xs(sex, b)) / 2)}" y="50" font-size="12" font-weight="600" text-anchor="middle" '
                 f'fill="{INK}">{"Women" if sex == "female" else "Men"}</text>')
    t.append(f'<text x="30" y="50" font-size="12" text-anchor="end" fill="{TEXT}">lb</text>')
    for lb in range(100, HI + 1, 20):
        t.append(f'<text x="30" y="{f1(ys(lb) + 4)}" font-size="12" text-anchor="end" fill="{TEXT}">{lb}</text>')
        for sex, (x0, a, b) in PAN.items():
            t.append(f'<line x1="{f1(x0)}" y1="{f1(ys(lb))}" x2="{f1(xs(sex, b))}" y2="{f1(ys(lb))}" stroke="{GRID}" stroke-width="1"/>')
    for sex, (x0, a, b) in PAN.items():
        pts = S['figure'][sex]
        top = ' '.join(f'{f1(xs(sex, p["inches"]))},{f1(ys(p["healthy_lb"][1]))}' for p in pts)
        bot = ' '.join(f'{f1(xs(sex, p["inches"]))},{f1(ys(p["healthy_lb"][0]))}' for p in reversed(pts))
        t.append(f'<polygon data-sex="{sex}" points="{top} {bot}" fill="{BAND}"/>')
        t.append(f'<line x1="{f1(x0)}" y1="{YB}" x2="{f1(xs(sex, b))}" y2="{YB}" stroke="{AXIS}" stroke-width="1"/>')
        for i in range(a, b + 1, 6):
            xx = xs(sex, i)
            t.append(f'<line x1="{f1(xx)}" y1="{YB}" x2="{f1(xx)}" y2="{YB + 4}" stroke="{AXIS}" stroke-width="1"/>')
            t.append(f'<text x="{f1(xx)}" y="{YB + 16}" font-size="12" text-anchor="middle" fill="{TEXT}">{ft_in(i)}</text>')
            t.append(f'<text x="{f1(xx)}" y="{YB + 32}" font-size="12" text-anchor="middle" fill="{TEXT}">{round(i * 2.54)}</text>')
    for n in ('hamwi', 'robinson', 'devine', 'miller'):          # the dashed lines go on top
        col, dash = STYLE[n]
        cap = f'stroke-dasharray="{dash}" stroke-linecap="butt"' if dash else 'stroke-linecap="round"'
        for sex in PAN:
            pts = ' '.join(f'{f1(xs(sex, p["inches"]))},{ys(p[n]):.2f}' for p in S['figure'][sex])
            t.append(f'<polyline data-formula="{n}" data-sex="{sex}" points="{pts}" fill="none" stroke="{col}" '
                     f'stroke-width="2" {cap} stroke-linejoin="round"/>')
    for sex, (x0, a, b) in PAN.items():                         # hover: one column per inch
        for i in range(a, b + 1):
            r = T[sex][i]
            lx, rx = max(x0, xs(sex, i) - K / 2), min(xs(sex, b), xs(sex, i) + K / 2)
            names = ', '.join(f'{LABEL[n]} {r[n]["lb"]} lb' for n in NAMES)
            t.append(f'<rect x="{f1(lx)}" y="{YT}" width="{f1(rx - lx)}" height="{YB - YT}" fill="#ffffff" fill-opacity="0">'
                     f'<title>{r["height"]} ({r["cm"]}), {sex_word(sex)}: {names}; healthy range '
                     f'{r["healthy"]["lb"][0]}–{r["healthy"]["lb"][1]} lb</title></rect>')
    t.append('</svg><figcaption>Heights in feet and inches, cm under them. Our calculation; the tables below list every '
             'value.</figcaption></figure>')
    return ''.join(t)


# ---------------------------------------------------------------- tables
# Six number columns fit a 360 px phone only if a heading can break: soft hyphens, used only where the screen needs them
HYPH = {'hamwi': 'Ham&shy;wi', 'devine': 'Dev&shy;ine', 'robinson': 'Robin&shy;son', 'miller': 'Mil&shy;ler'}


def by_height_table(sex):
    word = sex_word(sex)
    head = ('<thead><tr><th scope="col">Height<span class="th-sub">cm</span></th>'
            + ''.join(f'<th scope="col" class="num">{HYPH[n]}</th>' for n in NAMES)
            + '<th scope="col" class="num">Heal&shy;thy BMI range</th></tr></thead>')
    body = []
    for r in S['tables'][sex]:
        rid = f'{word}-{r["inches"] // 12}-{r["inches"] % 12}'
        cells = ''.join(f'<td class="num">{r[n]["lb"]}<span class="cell-kg">{r[n]["kg"]}</span></td>' for n in NAMES)
        h = r['healthy']
        body.append(f'<tr id="{rid}"><th scope="row">{r["height"]}<span class="th-sub">{r["cm"].split()[0]}</span></th>{cells}'
                    f'<td class="num">{h["lb"][0]}–{h["lb"][1]}<span class="cell-kg">{h["kg"][0]}–{h["kg"][1]}</span></td></tr>')
    return ('<div class="table-responsive"><table class="data-table data-table--fit data-table--tight">'
            f'<caption>{word.capitalize()}, medium frame: lb, with kg under each value</caption>'
            + head + '<tbody>' + ''.join(body) + '</tbody></table></div>')


def formula_cell(sex, n):
    f = FTAB[sex][n]
    u, o = f['unit'], f['other_unit']
    return (f'<td>{f["base"]}{NB}{u} + {f["per_inch"]}{NB}{u}'
            f'<span class="unit-alt">{f["base_other"]}{NB}{o} + {f["per_inch_other"]}{NB}{o}</span></td>')


def formula_table():
    rows = ''.join(f'<tr><th scope="row">{LABEL[n]}<span class="th-sub">{YEAR[n]}</span></th>'
                   f'{formula_cell("female", n)}{formula_cell("male", n)}</tr>' for n in NAMES)
    return ('<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap">'
            '<caption>The weight at 5′0″ plus an amount per inch over 5′0″, as published, with our conversion under it</caption>'
            '<thead><tr><th scope="col">Formula</th><th scope="col">Women</th><th scope="col">Men</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def formula_text(sex):
    """One sex's four formulas as published, our conversion in parentheses (the FAQ)."""
    out = []
    for n in NAMES:
        f = FTAB[sex][n]
        u, o = f['unit'], f['other_unit']
        out.append(f'{LABEL[n]} {f["base"]} {u} + {f["per_inch"]} {u} ({f["base_other"]} {o} + {f["per_inch_other"]} {o})')
    return '; '.join(out[:-1]) + ' and ' + out[-1]


# MedlinePlus wrist cut-offs in inches (fact 6); cm is our conversion to 0.1 cm
WRIST = [('Women under 5′2″', ('<', '5.5'), ('5.5', '5.75'), ('>', '5.75')),
         ('Women 5′2″ to 5′5″', ('<', '6'), ('6', '6.25'), ('>', '6.25')),
         ('Women over 5′5″', ('<', '6.25'), ('6.25', '6.5'), ('>', '6.5')),
         ('Men over 5′5″', ('5.5', '6.5'), ('6.5', '7.5'), ('>', '7.5'))]


def cm_of(inch):
    return cm1(Decimal(inch) * Decimal('2.54'))


def wrist_cell(c):
    a, b = c
    if a in ('<', '>'):
        op = '&lt;' if a == '<' else '&gt;'
        return f'<td class="num">{op}{NB}{b}<span class="unit-alt">{op}{NB}{cm_of(b)}</span></td>'
    return f'<td class="num">{a}–{b}<span class="unit-alt">{cm_of(a)}–{cm_of(b)}</span></td>'


def wrist_table():
    rows = ''.join(f'<tr><th scope="row">{h}</th>{"".join(wrist_cell(c) for c in cs)}</tr>' for h, *cs in WRIST)
    return ('<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap">'
            '<caption>Body frame from wrist size: inches, with cm under each value</caption>'
            '<thead><tr><th scope="col">Height</th><th scope="col" class="num">Small</th><th scope="col" class="num">Medium</th>'
            '<th scope="col" class="num">Large</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


# ---------------------------------------------------------------- worked examples
def nw(t):
    return f'<span class="nowrap">{t}</span>'


def example_dl(ex, row):
    over, out = ex['over'], []
    for n in NAMES:
        s, r = ex['steps'][n], row[n]
        base, per, value, other = s['base'], s['per_inch'], s['value'], s['other_1dp']
        unit = s['unit']
        if unit == 'lb':
            assert int(value) == r['lb'] and other == r['kg'], (n, s, r)
        else:
            assert Decimal(value).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) == Decimal(r['kg']), (n, s, r)
            assert Decimal(other).quantize(Decimal(1), rounding=ROUND_HALF_UP) == r['lb'], (n, s, r)
        out.append(f'<dt>{LABEL[n]}: {r["lb"]} lb ({r["kg"]} kg)</dt><dd>{nw(f"{base} + {per} × {over} = {value} {unit}")}</dd>')
    return '<dl>' + ''.join(out) + '</dl>'


wh, mh = w66['healthy'], m70['healthy']
assert M70L['hamwi']['lb'] == 183 and M70L['hamwi']['kg'] == '82.8' and EXM['hamwi_large_bmi'] == '26.2'
assert float(EXM['hamwi_large_bmi']) >= 25 and EXM['hamwi_large_exact_lb'] == '182.6'
HL_MED, HL_EXACT = m70['hamwi']['lb'], EXM['hamwi_large_exact_lb']
LARGE_STEP = f'{HL_MED} × 1.1 = {HL_EXACT}'
EXAMPLES = (
    f'<h3>A 5′6″ woman, medium frame: {EXW["over"]} inches over 5 feet</h3>'
    + example_dl(EXW, EXW['medium']) +
    f'<p>The four span {to(*w66["span"]["lb"], "lb")}, a BMI of {to(*w66["bmi"])}. The healthy range at 5′6″ is '
    f'{to(*wh["lb"], "lb")} ({to(*wh["kg"], "kg")}).</p>'
    f'<h3>A 5′10″ man, medium and large frame: {EXM["over"]} inches over 5 feet</h3>'
    + example_dl(EXM, EXM['medium']) +
    f'<p>The four span {to(*m70["span"]["lb"], "lb")}, a BMI of {to(*m70["bmi"])}, inside the healthy range of '
    f'{to(*mh["lb"], "lb")} ({to(*mh["kg"], "kg")}). A large frame changes only Hamwi’s: {nw(LARGE_STEP)}, so '
    f'{M70L["hamwi"]["lb"]} lb ({M70L["hamwi"]["kg"]} kg), a BMI of {EXM["hamwi_large_bmi"]}, above that range.</p>')

# ---------------------------------------------------------------- FAQ (plain text answers, so the JSON-LD is the visible text)
wl, wh_ = per_inch_lb('female')
ml, mh_ = per_inch_lb('male')
FAQ = [
    ('How much should I weigh for my height?',
     f'There are two answers. Each formula gives one weight for your height: {to(*w66["span"]["lb"], "lb")} across the four '
     f'for a 5′6″ woman. A healthy weight on CDC’s BMI scale is a range, {to(*wh["lb"], "lb")} at 5′6″ (a BMI of 18.5 to '
     f'24.9). The calculator gives both.'),
    ('What is ideal body weight (IBW)?',
     'A weight worked out from height alone. Peterson and colleagues write that it “was originally defined as the weight '
     'associated with the greatest life expectancy at each height” and that “IBW equations are still being used by '
     'clinicians to calculate drug dosing, to estimate overweight and underweight statuses, and to calculate nutrient '
     'intakes.”'),
    ('What is the formula for ideal body weight?',
     f'Four are in use, each a weight at 5 feet plus an amount for every inch over 5 feet. Women: {formula_text("female")}. Men: '
     f'{formula_text("male")}. Values in parentheses are our conversions. By 2000 more than 200 articles had cited Devine’s. '
     f'All four start at 60 inches.'),
    ('Why do the four formulas give different results?',
     f'They come from different places (Hamwi’s rule in pounds, Devine’s equations with no data set behind them, two '
     f'Metropolitan Life tables) and add different amounts per inch: {wl} to {wh_} lb for women, {ml} to {mh_} lb for men. They come closest '
     f'at {WN["height"]} for women and at 5′5″ and 5′6″ for men, and split apart toward both ends: '
     f'{to(*w60["span"]["lb"], "lb")} for women at 5′0″, {to(*MW["lb"], "lb")} for men at 6′6″.'),
    ('Which ideal weight formula is the most accurate?',
     'The sources here don’t rank them. Pai and Paloucek concluded that “any one of these equations may be used to '
     'estimate IBW.” Robinson and colleagues found that estimates “obtained by the widely used empirical method probably '
     'contain only minor errors.” Peterson and colleagues point out that the equations give a single weight, where most '
     'clinicians favor a range.'),
    ('Does ideal weight change with age?',
     'No: none of the four has an age term. Peterson and colleagues note that “there is no single ideal weight that is '
     'applicable across all demographic factors, including age and ethnicity.” The '
     '<a href="/age-bmi-calculator/">BMI calculator by age</a> covers how BMI is read at older ages.'),
    ('How do I find my body frame size?',
     'Compare your wrist with the MedlinePlus cut-offs for your height: for a woman over 5′5″, under 6.25 in is small, 6.25 '
     'to 6.5 in medium and over 6.5 in large; for a man over 5′5″, 5.5 to 6.5 in is small, 6.5 to 7.5 in medium and over '
     '7.5 in large. Or grasp the other wrist with the thumb and middle finger of your predominant hand: they meet for a '
     'medium frame, overlap appreciably for a small one and fail to meet for a large one. Frame size changes only Hamwi’s '
     'number.'),
    ('Is ideal body weight the same as a healthy weight?',
     f'No. A formula gives one weight; a healthy weight is a range. At 5′6″ the four give a woman '
     f'{to(*w66["span"]["lb"], "lb")}, while CDC’s healthy BMI range runs from {to(*wh["lb"], "lb")}. Peterson and '
     f'colleagues write that “IBW equations have largely been replaced by BMI ranges.”'),
    ('Can children use these formulas?',
     'The formulas start at 5 feet and ignore age. For children and teens, CDC uses BMI percentiles: a healthy weight is '
     'the 5th to below the 85th percentile, which the <a href="/kids-bmi-calculator/">kids BMI calculator</a> gives.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')


def faq_html(items):
    return ('<div class="faq-list flat">' + ''.join(
        f'<div class="faq-item"><button class="faq-question">{q}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
        for q, a in items) + '</div>')


# ---------------------------------------------------------------- the calculator (shared parts; ids and starting values kept)
def field(fid, label, cls, value, lo, hi):
    return (f'<div class="form-group"><label class="form-label" for="{fid}">{label}</label>'
            f'<input type="number" id="{fid}" class="form-input {cls}" value="{value}" min="{lo}" max="{hi}"></div>')


def select(fid, label, cls, opts):
    o = ''.join(f'<option value="{v}"{" selected" if sel else ""}>{t}</option>' for v, t, sel in opts)
    return (f'<div class="form-group"><label class="form-label" for="{fid}">{label}</label>'
            f'<select id="{fid}" class="form-select {cls}">{o}</select></div>')


def tile(label, rid, wide=False):
    return (f'<div class="result-item{" result-item--wide" if wide else ""}"><div class="result-item-label">{label}</div>'
            f'<div class="result-item-value" id="{rid}">—</div></div>')


CALC = ('<div class="calculator-card"><div id="panel-ideal" class="calc-panel active">'
        '<div class="unit-toggle"><button class="unit-btn active" data-unit="imperial">Imperial (ft, in)</button>'
        '<button class="unit-btn" data-unit="metric">Metric (cm)</button></div>'
        '<div class="form-grid">'
        '<div class="form-row form-row--pair imperial-inputs">'
        + field('ideal-height-ft', 'Height (ft)', 'height-ft', 5, 1, 8)
        + field('ideal-height-in', 'Height (in)', 'height-in', 6, 0, 11) + '</div>'
        '<div class="form-row form-row--pair metric-inputs" hidden>'
        + field('ideal-height-cm', 'Height (cm)', 'height-cm', 168, 50, 250) + '</div>'
        '<div class="form-row">'
        + select('ideal-sex', 'Sex', 'sex-select', [('female', 'Female', False), ('male', 'Male', False)])
        + select('ideal-frame', 'Body frame (changes Hamwi only)', 'frame-select',
                 [('small', 'Small', False), ('medium', 'Medium', True), ('large', 'Large', False)]) + '</div>'
        '</div>'
        '<button class="calculate-btn" id="calc-ideal-btn">Calculate Ideal Weight</button>'
        '<div class="results-section" id="ideal-results">'
        '<div class="results-grid">' + tile('The four formulas', 'ideal-span', True)
        + tile('Healthy BMI range (18.5–24.9)', 'ideal-bmi-range', True) + '</div>'
        '<div class="results-grid results-grid-4">'
        + ''.join(tile(f'{LABEL[n]} ({YEAR[n]})', f'ideal-{n}') for n in NAMES) + '</div>'
        '</div></div></div>')

# ---------------------------------------------------------------- the page
W_BMI, M_BMI = AG['female']['bmi'], AG['male']['bmi']
assert AG['female']['all_inside_healthy'] and AG['male']['all_inside_healthy']
SMALL, LARGE = W66F['small'], W66F['large']
MAIN = (
    '<main class="reading"><div class="container">'
    '<div class="page-head">'
    f'<h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Find your ideal body weight with all four published formulas, next to the healthy weight range '
    'for your height.</p>'
    '<p class="intro-note">Height formulas from 1964 to 1983, not a medical standard: CDC screens weight with BMI. '
    '<a href="#sources">Method and sources</a></p>'
    '</div>'
    + CALC +
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>Ideal body weight (IBW)</strong> is a weight worked out from height alone. The four formulas in '
    f'use start at 5 feet and add a fixed amount per inch: for a 5′6″ woman they give <strong>{to(*w66["span"]["lb"], "lb")}</strong>, '
    f'inside the healthy BMI range of {to(*wh["lb"], "lb")} at that height.</p>'
    '<ul>'
    f'<li>The formulas agree within {WN["width"]} lb at {WN["height"]} for women and 5′6″ for men and split apart toward both '
    f'ends: at 6′6″ the men’s run from {MW["lb"][0]} lb (Miller) to {MW["lb"][1]} lb (Hamwi).</li>'
    '<li>At a medium frame every formula stays inside CDC’s healthy BMI range at the heights in the tables, at a BMI of '
    f'{to(*W_BMI)} for women and {to(*M_BMI)} for men.</li>'
    '<li>Hamwi (1964) works in pounds and adjusts for frame size: 10% less for a small frame, 10% more for a large one.</li>'
    '<li>Pai and Paloucek concluded that “any one of these equations may be used to estimate IBW,” and Peterson and '
    'colleagues note that IBW equations “have largely been replaced by BMI ranges.”</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information only. '
    'BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>'
    '<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
    '<a href="#formulas">The formulas</a><a href="#by-height">By height</a><a href="#frame">Frame size</a>'
    '<a href="#examples">Examples</a><a href="#healthy-range">Healthy range</a><a href="#faq">FAQ</a>'
    '<a href="#sources">Sources</a></nav>'

    '<section id="formulas" class="content-section flow"><h2>The four formulas</h2>'
    '<p>Hamwi’s formula is in pounds, the other three in kilograms.</p>'
    + formula_table() +
    '<p>Hamwi’s rule, the oldest, comes from a 1964 chapter in an American Diabetes Association book: a desirable body '
    'weight in pounds, adjusted by 10% for frame size.</p>'
    '<p>Devine’s equations (1974) come from an article on gentamicin dosing. Pai and Paloucek note that they “were not '
    'referenced to a particular data set” and trace them to a simple rule worked out from height–weight tables: 100 lb plus '
    '5 lb an inch over 5 feet for women, 110 lb plus 5 lb for men. They don’t name its author.</p>'
    '<p>Robinson’s team fitted its equations to the 1959 Metropolitan Life tables, Miller’s to the 1983 tables. Pai and '
    'Paloucek found them “strikingly similar” to Devine’s and concluded that “any one of these equations may be used to '
    'estimate IBW.”</p>'
    '<p>Robinson’s abstract gives 51.65 kg + 1.85 kg (men) and 48.67 kg + 1.65 kg (women); the rounded values in Pai and '
    'Paloucek’s table are the ones in common use and in this calculator. All four start at 60 inches, so under 5 feet the '
    'calculator gives no formula weight.</p>'
    '</section>'

    '<section id="by-height" class="content-section flow"><h2>Ideal weight by height</h2>'
    '<p>Each line is one formula at a medium frame, over the healthy BMI range at each height.</p>'
    + figure() +
    f'<p>The four come closest at {WN["height"]} for women ({to(*WN["lb"], "lb")}) and at 5′5″ and 5′6″ for men ({MN[0]["width"]} '
    f'lb apart), and split apart toward both ends: {to(*w60["span"]["lb"], "lb")} for women at 5′0″, {to(*MW["lb"], "lb")} for '
    f'men at 6′6″.</p>'
    + by_height_table('female') + by_height_table('male') +
    '<p class="source-note">The formula columns are what the calculator prints. The healthy range runs over the whole pounds '
    'and whole kilograms with a BMI of 18.5 to 24.9.</p>'
    '</section>'

    '<section id="frame" class="content-section flow"><h2>Body frame size</h2>'
    f'<p>Hamwi’s rule adds 10% for a large frame and takes off 10% for a small one: for a 5′6″ woman, {SMALL["lb"]} lb small, '
    f'{w66["hamwi"]["lb"]} lb medium, {LARGE["lb"]} lb large.</p>'
    '<p>In the early height–weight tables, frame sizes “were not defined and were left to the subjective judgment of the '
    'examiner”; body frame was later defined in the 1959 Metropolitan table (Pai and Paloucek).</p>'
    '<p>MedlinePlus reads frame size from the wrist:</p>'
    + wrist_table() +
    '<p class="source-note">MedlinePlus gives no cut-off for men 5′5″ and shorter. The cm values are our conversion.</p>'
    '<p>A quicker test, from Davidson’s table: grasp the other wrist with the thumb and middle finger of your predominant '
    'hand. If they meet, the frame is medium; if they overlap appreciably, small; if they fail to meet, large.</p>'
    '<p>In the calculator, frame size changes only Hamwi’s number.</p>'
    '</section>'

    '<section id="examples" class="content-section flow"><h2>Two worked examples</h2>'
    + EXAMPLES +
    '</section>'

    '<section id="healthy-range" class="content-section flow"><h2>Ideal weight or a healthy weight range?</h2>'
    '<p>A formula gives one weight for a height. Peterson and colleagues note that “IBW equations predict a single target '
    'body weight, whereas most clinicians favor, and the empirical data support, a range of target body weights.” '
    f'CDC’s {ext(CDC_CATS, "adult BMI categories")} give that range: a healthy weight is a BMI of 18.5 to under 25, which at '
    f'5′6″ is {to(*wh["lb"], "lb")}. The <a href="/bmi-chart/">BMI chart</a> lists it at every height, as do the charts for '
    '<a href="/blog/bmi-chart-women/">women</a> and <a href="/blog/bmi-chart-men/">men</a>.</p>'
    f'<p>Neither measure tells muscle from fat. CDC {ext(CDC_ABOUT, "notes")} that “BMI does not distinguish between fat, '
    'muscle, and bone mass”; the <a href="/lean-body-mass/">lean body mass calculator</a> and the '
    '<a href="/body-fat-calculator/">body fat calculator</a> estimate lean mass and body fat.</p>'
    '<p>Clinicians still use IBW equations “to calculate drug dosing, to estimate overweight and underweight statuses, and '
    'to calculate nutrient intakes,” Peterson and colleagues write. This page doesn’t cover drug dosing.</p>'
    '</section>'

    '<section id="faq" class="content-section"><h2>Frequently asked questions</h2>'
    + faq_html(FAQ) +
    '</section>'

    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means worked out as described '
    'below.</p>'
    '<ul class="source-list">'
    f'<li>Pai MP, Paloucek FP. {ext(PAI, "The origin of the “ideal” body weight equations")}. Ann Pharmacother '
    '2000;34:1066–9.</li>'
    f'<li>Robinson JD, et al. {ext(ROBINSON, ROB_TITLE)}. Am J Hosp Pharm 1983;40:1016–9 (abstract).</li>'
    f'<li>Peterson CM, et al. {ext(PETERSON, PET_TITLE)}. Am J Clin Nutr 2016;103:1197–1203.</li>'
    f'<li>Davidson MB. {ext(DAVIDSON, "Insulin therapy: a personal approach")}. Clin Diabetes 2015;33:123–135, Table 2, '
    'citing Hamwi GJ, Therapy: changing dietary concepts (American Diabetes Association, 1964).</li>'
    '<li>Devine BJ, Drug Intell Clin Pharm 1974;8:650–5, and Miller DR, et al., Am J Hosp Pharm 1983;40:1622, as cited by '
    'Pai and Paloucek.</li>'
    f'<li>MedlinePlus. {ext(MEDLINE, "Calculating body frame size")} (A.D.A.M., reviewed July 23, 2024).</li>'
    f'<li>CDC. {ext(CDC_CALC, "Calculating BMI")}; {ext(CDC_CATS, "Adult BMI Categories")}; '
    f'{ext(CDC_ABOUT, "About Body Mass Index (BMI)")}; {ext(CDC_CHILD, "Child and Teen BMI Categories")}.</li>'
    '</ul>'
    '<p class="source-note"><strong>Method.</strong> Every number in the tables, figure and examples is our calculation '
    'with the calculator’s arithmetic: the constants in the first table and 2.20462 lb per kg, from 60 inches up, with '
    'Hamwi’s weight × 0.9 for a small frame and × 1.1 for a large one. Weights print as whole pounds and kilograms to 0.1, '
    'halves up; the span runs from the lowest to the highest as printed. BMI is CDC’s formula at one decimal. Healthy '
    'ranges are the whole pounds and whole kilograms with a BMI of 18.5 to 24.9 at that height, each unit worked out on '
    'its own.</p>'
    '</section>'

    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul><li><a href="/">BMI calculator</a></li>'
    '<li><a href="/women-bmi-calculator/">BMI calculator for women</a></li>'
    '<li><a href="/men-bmi-calculator/">BMI calculator for men</a></li>'
    '<li><a href="/lean-body-mass/">Lean body mass calculator</a></li>'
    '<li><a href="/body-fat-calculator/">Body fat calculator</a></li>'
    '<li><a href="/new-bmi-calculator/">New BMI calculator</a></li></ul></div>'
    '<div><h3>Guides and data</h3><ul><li><a href="/bmi-chart/">BMI chart</a></li>'
    '<li><a href="/blog/bmi-chart-women/">BMI chart for women</a></li>'
    '<li><a href="/blog/bmi-chart-men/">BMI chart for men</a></li>'
    '<li><a href="/blog/healthy-bmi-range/">Healthy BMI range</a></li>'
    '<li><a href="/blog/body-fat-vs-bmi/">Body fat vs BMI</a></li>'
    '<li><a href="/blog/bmi-limitations/">Limitations of BMI</a></li></ul></div>'
    '</div></section>'
    '</div></main>')


def nbsp_units(markup):
    """A number keeps its unit on one line (DEVLOG §4, CMB-021): a no-break space between them, in text only."""
    unit = re.compile(r'(\d) (lb|lbs|kg|cm|in|inches|feet)(?![\w])')
    out = []
    for chunk in re.split(r'(?s)(<svg\b.*?</svg>)', markup):           # SVG text never wraps: leave the figure alone
        out.append(chunk if chunk.startswith('<svg') else
                   ''.join(p if p.startswith('<') else unit.sub('\\1\u00a0\\2', p) for p in re.split(r'(<[^>]+>)', chunk)))
    return ''.join(out)


MAIN = nbsp_units(MAIN)                         # the FAQ answers inside MAIN get their no-break spaces here too
FAQ = [(q, nbsp_units(a)) for q, a in FAQ]


def faq_text(a):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', a)).replace('\u00a0', ' ')).strip()


LD = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE,
     'isPartOf': {'@id': SITE + '/#website'}, 'mainEntity': {'@id': URL + '#calculator'},
     'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG['16x9'], 'width': 1200, 'height': 675}},
    {'@type': 'WebApplication', '@id': URL + '#calculator', 'image': [IMG['1x1'], IMG['4x3'], IMG['16x9']],
     'name': H1,
     'description': ('Calculates ideal body weight from height and sex with the Hamwi (1964), Devine (1974), Robinson (1983) '
                     'and Miller (1983) formulas in US or metric units, applies Hamwi’s frame-size rule to his formula, and '
                     'gives the healthy weight range for the height (BMI 18.5 to 24.9).'),
     'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any',
     'browserRequirements': 'Requires JavaScript', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
     'featureList': ['Hamwi, Devine, Robinson and Miller ideal body weight from US or metric units',
                     'The span of the four formulas, as printed', 'Hamwi’s frame-size rule (small, medium, large)',
                     'Healthy weight range for your height (BMI 18.5 to 24.9)'],
     'author': {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}},
    {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Calculators', 'item': SITE + '/calculators/'},
        {'@type': 'ListItem', 'position': 3, 'name': 'Ideal Body Weight Calculator', 'item': URL}]},
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
    assert '"' not in DESC and '"' not in OG_ALT and '"' not in TITLE      # attribute values never hold a raw quote (DEVLOG §4)
    head, rest = src.split('</head>', 1)
    head = put_meta(head, 'name', 'description', DESC)
    head = put_meta(head, 'property', 'og:title', TITLE)
    head = put_meta(head, 'property', 'og:description', DESC)
    head = put_meta(head, 'property', 'og:image', IMG['16x9'])
    head = put_meta(head, 'property', 'og:image:alt', OG_ALT, after=('property', 'og:image'))
    head = put_meta(head, 'property', 'og:image:width', '1200')
    head = put_meta(head, 'property', 'og:image:height', '675')
    head = put_meta(head, 'name', 'twitter:title', TITLE)
    head = put_meta(head, 'name', 'twitter:description', DESC)
    head = put_meta(head, 'name', 'twitter:image', IMG['16x9'])
    blocks = list(re.finditer(r'(?s)\n?<script type="application/ld\+json">.*?</script>', head))
    assert blocks, 'no JSON-LD in the head'
    ld = '\n<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>'
    head = head[:blocks[0].start()] + ld + ''.join(head[a.end():b.start()] for a, b in zip(blocks, blocks[1:])) + head[blocks[-1].end():]
    titles = re.findall(r'<title>[^<]*</title>', head)
    assert len(titles) == 1, titles
    head = head.replace(titles[0], f'<title>{TITLE}</title>')
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
    print(f'{PAGE}: {len(out):,} bytes; <main> {len(MAIN):,} bytes, about {words(MAIN)} words outside the figure; '
          f'description {len(DESC)} characters, title {len(TITLE)}')
