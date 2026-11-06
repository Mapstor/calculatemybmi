#!/usr/bin/env python3
"""Builds /new-bmi-calculator/ (CMB-023) from nb_stats.json. usage: python3 research/new-bmi-build/gen_nb.py
Replaces, in new-bmi-calculator/index.html, only what the page owns: everything inside <main>, and in the head the meta
description, the og:* and twitter:* text and images and the JSON-LD. The title, the Raptive, consent and GA4 scripts, the
header, the scripts after </main> (calculator.js, the FAQ and menu toggles) and the footer stay byte for byte, so running
it twice gives the same file. Every number on the page comes from nb_stats.json or is a fact from the registry rows
trefethen-new-bmi, economist-2013-trefethen-letter, cdc-calculating-bmi, cdc-adult-bmi-categories, cdc-about-bmi and
who-obesity-fact-sheet (CMB-023 prompt, FACTS 1-7)."""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PAGE = os.path.join(ROOT, 'new-bmi-calculator/index.html')
S = json.load(open(os.path.join(HERE, 'nb_stats.json'), encoding='utf-8'))
SITE = 'https://calculatemybmi.net'
URL = SITE + '/new-bmi-calculator/'
IMG = {r: f'{SITE}/assets/images/preferred/new-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}
TREFETHEN = 'https://people.maths.ox.ac.uk/trefethen/bmi.html'
ECONOMIST = 'https://www.economist.com/letters/2013/01/05/body-mass-index'
CDC_CALC = 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html'
CDC_CATS = 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html'
CDC_ABOUT = 'https://www.cdc.gov/bmi/about/index.html'
WHO = 'https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight'
M = '−'

TITLE = 'New BMI Calculator (Trefethen) - Updated Body Mass Index Formula'      # kept (KWP check pending, DEVLOG §5)
H1 = 'New BMI Calculator (Trefethen Formula)'                                  # kept
DESC = ('Compare New BMI, Trefethen’s 2013 formula, with traditional BMI for your height and weight. '
        'See both numbers, the gap at your height and which one to use.')
OG_TITLE = H1
OG_ALT = ('Chart: New BMI minus traditional BMI by height at 154 lb (70 kg), above zero for shorter people, '
          'crossing zero at 5′6.5″ (1.69 m) and below zero for taller people.')


def ext(href, text):
    return f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'


SBS = {(r['inches'], r['lb']): r for r in S['side_by_side']}
BH = {b['inches']: b for b in S['by_height']}
EX = {e['inches']: e for e in S['examples']}
C = S['curve']
MK = {m['inches']: m for m in C['marks']}
assert C['lb'] == '154' and C['kg'] == 70 and C['cross_height'] == '5′6.5″'


def pct_abs(p): return p.lstrip('+' + M)


# ---------------------------------------------------------------- the figure (inline SVG, 320 wide like the other D-14 figures)
X0, X1, Y0, Y1 = 30, 310, 30, 186          # plot box; x: 1.40 to 2.00 m, y: +4 to -2 points
def xs(m): return X0 + (m - 1.40) * (X1 - X0) / 0.60
def ys(v): return Y0 + (4 - v) * (Y1 - Y0) / 6
def n1(v): return f'{v:.1f}'


def figure():
    lo, hi, m5, m6 = C['diff_lo'], C['diff_hi'], MK[60], MK[72]
    t = ('<figure class="figure"><svg viewBox="0 0 320 226" role="img" aria-labelledby="nb-t nb-d" '
         'xmlns="http://www.w3.org/2000/svg" font-family="inherit">'
         '<title id="nb-t">How much New BMI differs from traditional BMI at each height, at 154 lb (70 kg)</title>'
         f'<desc id="nb-d">New BMI minus traditional BMI at 154 lb (70 kg), from {C["height_lo"]} to {C["height_hi"]} '
         f'(1.40 to 2.00 m): {n1(lo)} points higher at {C["height_lo"]}, {pct_abs(m5["difference"])} higher at 5′0″ (1.52 m), '
         f'the same at 5′6.5″ (1.69 m), {pct_abs(m6["difference"])} lower at 6′0″ (1.83 m) and {n1(abs(hi))} lower at '
         f'{C["height_hi"]}. Our calculation from the two formulas.</desc>')
    t += '<text x="4" y="14" font-size="12" text-anchor="start" fill="#4b5563">New BMI minus traditional BMI at 154 lb (70 kg)</text>'
    for v in range(-2, 5):
        lab = '0' if v == 0 else (f'+{v}' if v > 0 else f'{M}{-v}')
        t += (f'<line x1="26" y1="{n1(ys(v))}" x2="{X0}" y2="{n1(ys(v))}" stroke="#9ca3af" stroke-width="1"/>'
              f'<text x="23" y="{n1(ys(v) + 4)}" font-size="12" text-anchor="end" fill="#4b5563">{lab}</text>')
    t += f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="#d1d5db" stroke-width="1"/>'
    for inch in (56, 60, 64, 68, 72, 76):
        x = xs(inch * 0.0254)
        m_lab = f'{inch * 0.0254:.2f}'
        t += (f'<line x1="{n1(x)}" y1="{Y1}" x2="{n1(x)}" y2="{Y1 + 4}" stroke="#4b5563" stroke-width="1"/>'
              f'<text x="{n1(x)}" y="203" font-size="12" text-anchor="middle" fill="#374151">{inch // 12}′{inch % 12}″</text>'
              f'<text x="{n1(x)}" y="219" font-size="12" text-anchor="middle" fill="#4b5563">{m_lab} m</text>')
    t += f'<line x1="{X0}" y1="{n1(ys(0))}" x2="{X1}" y2="{n1(ys(0))}" stroke="#4b5563" stroke-width="1"/>'
    pts = ' '.join(f'{xs(m):.2f},{ys(d):.2f}' for m, d in C['points'])
    t += (f'<polyline points="{pts}" fill="none" stroke="#0e7490" stroke-width="2.5" stroke-linejoin="round" '
          'stroke-linecap="round"/>')
    for mk, (dx, dy, anchor, word) in ((m5, (7, -7, 'start', 'higher')), (m6, (-7, 17, 'end', 'lower'))):
        cx, cy = xs(mk['m']), ys(mk['diff_exact'])
        tip = f'{mk["height"]} ({mk["m"]:.2f} m): New BMI {pct_abs(mk["difference"])} points {word} at 154 lb'
        t += (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4" fill="#0e7490" stroke="#ffffff" stroke-width="1.5"><title>{tip}</title></circle>'
              f'<text x="{cx + dx:.1f}" y="{cy + dy:.1f}" font-size="12" text-anchor="{anchor}" font-weight="600" '
              f'fill="#111827">{mk["difference"]} at {mk["height"]}</text>')
    cx, cy = xs(C['cross_m']), ys(0)
    t += (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4" fill="#ffffff" stroke="#111827" stroke-width="1.5">'
          f'<title>Same at 5′6.5″ (1.69 m)</title></circle>'
          f'<text x="{cx + 7:.1f}" y="{cy - 8:.1f}" font-size="12" text-anchor="start" fill="#111827">Same at 5′6.5″ (1.69 m)</text>')
    t += ('</svg><figcaption>New BMI minus traditional BMI at 154 lb (70 kg), from '
          f'{C["height_lo"]} to {C["height_hi"]} (1.40 to 2.00 m): higher below 5′6.5″, lower above it. '
          'Our calculation.</figcaption></figure>')
    return t


# ---------------------------------------------------------------- tables
def by_height_table():
    rows = ''.join(f'<tr><th scope="row">{b["height"]}<span class="th-sub">{b["m"]}</span></th>'
                   f'<td class="num">{b["percent"]}</td><td class="num">{b["traditional_25_becomes"]}</td></tr>'
                   for b in S['by_height'])
    return ('<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap">'
            '<caption>New BMI against traditional BMI, by height</caption>'
            '<thead><tr><th scope="col">Height</th><th scope="col" class="num">Change</th>'
            '<th scope="col" class="num">25.0 becomes</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def side_table():
    groups = ''
    for h in (60, 64, 68, 72, 76):
        first = SBS[(h, 120)]
        g = f'<tbody><tr><th scope="rowgroup" colspan="4">{first["height"]} ({first["cm"]})</th></tr>'
        for lb in (120, 150, 180, 210):
            r = SBS[(h, lb)]
            dag = '†' if r['category_changes'] else ''
            g += (f'<tr><th scope="row">{lb} lb{dag}<span class="th-sub">{r["kg"]}</span></th>'
                  f'<td class="num">{r["traditional"]}</td><td class="num">{r["new"]}</td><td class="num">{r["difference"]}</td></tr>')
        groups += g + '</tbody>'
    return ('<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap">'
            '<caption>Traditional and New BMI at five heights and four weights</caption>'
            '<thead><tr><th scope="col">Weight</th><th scope="col" class="num">Traditional</th>'
            '<th scope="col" class="num">New BMI</th><th scope="col" class="num">Difference</th></tr></thead>'
            f'{groups}</table></div>')


changed = [r for r in S['side_by_side'] if r['category_changes']]
assert [(r['inches'], r['lb']) for r in changed] == [(60, 150), (72, 120), (76, 210)], changed
c5, c6, c7 = SBS[(60, 150)], SBS[(76, 210)], SBS[(72, 120)]
assert (c7['traditional_category'], c7['new_category']) == ('Moderate thinness', 'Severe thinness')
gaps = sorted(S['side_by_side'], key=lambda r: float(r['difference'].replace(M, '-')))
big_neg, big_pos = gaps[0], gaps[-1]
assert (big_pos['inches'], big_pos['lb'], big_pos['difference']) == (60, 210, '+2.2')
assert (big_neg['inches'], big_neg['lb'], big_neg['difference']) == (76, 210, M + '1.7')
d58 = [abs(float(SBS[(68, lb)]['difference'].replace(M, '-'))) for lb in (120, 150, 180, 210)]
assert max(d58) == 0.3
b25 = {h: BH[h]['traditional_25_becomes'] for h in (60, 72)}
assert b25 == {60: '26.3', 72: '24.0'}
up5 = f'{float(b25[60]) - 25:.1f}'
dn6 = f'{25 - float(b25[72]):.1f}'


def nw(t): return f'<span class="nowrap">{t}</span>'


def example(e):
    h = e['inches']
    same = e['traditional_category'] == e['new_category']
    cat_line = (f'Both numbers are {e["new_category"].lower()}, so the category stays the same.' if same else
                f'The category changes from {e["traditional_category"]} to {e["new_category"]}: New BMI drops below CDC’s '
                f'18.5 cut-off. CDC set that cut-off on traditional BMI, and on CDC’s scale this person, at '
                f'{e["traditional"]}, is a healthy weight.')
    trad, new, kg, m = e['traditional'], e['new'], e['kg_2dp'], e['m_4dp']
    us_trad = nw(f'150 × 703 ÷ {h}² = {trad}')
    met_trad = nw(f'{kg} ÷ {m}²')
    us_new = nw(f'5734 × 150 ÷ {h}<sup>2.5</sup> = {e["us_new"]}')
    met_new = nw(f'1.3 × {kg} ÷ {m}<sup>2.5</sup> = {new}')
    diff = nw(f'{new} {M} {trad}')
    return (f'<h3>{e["height"]} and 150 lb ({e["cm"]}, {e["kg"]})</h3><dl>'
            f'<dt>Traditional BMI: {trad}, {e["traditional_category"]}</dt>'
            f'<dd>{us_trad}. In metric, {met_trad} gives the same {e["metric_traditional"]}.</dd>'
            f'<dt>New BMI: {new}, {e["new_category"]}</dt>'
            f'<dd>{us_new}. In metric, {met_new}.</dd>'
            f'<dt>Difference: {e["difference"]}</dt>'
            f'<dd>{diff}. {cat_line}</dd></dl>')


e62, e74 = EX[62], EX[74]
assert e62['traditional_category'] == e62['new_category'] == 'Overweight'
assert (e74['traditional_category'], e74['new_category']) == ('Healthy weight', 'Underweight')

# ---------------------------------------------------------------- FAQ (plain text answers, so the JSON-LD is the visible text)
FAQ = [
    ('What is the new BMI formula?',
     'New BMI = 5734 × weight (lb) ÷ height (in) to the power 2.5, or 1.3 × weight (kg) ÷ height (m) to the power 2.5. '
     'Nick Trefethen set it out in 2013 on his University of Oxford page as an alternative to the traditional formula, '
     'which divides by height squared. The two constants make both formulas give the same reading at about 5′6.5″ (1.69 m).'),
    ('Who created the new BMI?',
     'Nick Trefethen, who signed his letter to The Economist of 5 January 2013 as professor of numerical analysis at the '
     'University of Oxford. The letter called BMI “a bizarre measure”; the formula itself is on his Oxford page. He describes '
     'himself there as “an applied mathematician, not a doctor or an epidemiologist.”'),
    ('Why is the new BMI different from traditional BMI?',
     'It divides weight by height to the power 2.5 instead of height squared, then multiplies by 1.3. Weight cancels out '
     'when you compare the two: New BMI = traditional BMI × 1.3 ÷ √height (m). So the gap depends on height alone, from '
     f'{BH[60]["percent"].lstrip("+")} higher at 5′0″ to {pct_abs(BH[72]["percent"])} lower at 6′0″ (our calculation).'),
    ('Is the new BMI more accurate than traditional BMI?',
     'Trefethen doesn’t claim that. He writes that his formulas are “not based on epidemiological studies” and may not '
     'be an improvement, and he points to a 2007 paper by Heymsfield and colleagues in the American Journal of Clinical '
     'Nutrition that supports the exponent 2. CDC’s adult categories are set on traditional BMI.'),
    ('Should I use new BMI or traditional BMI?',
     'Use traditional BMI for anything medical, since CDC’s adult categories are set on it. New BMI is a second look if you '
     f'are very short or very tall, where the two differ most: {BH[60]["percent"].lstrip("+")} higher at 5′0″ and '
     f'{pct_abs(BH[76]["percent"])} lower at 6′4″ (our calculation). Neither formula can tell muscle from fat.'),
    ('Does the new BMI change my category?',
     f'Only when your BMI is close to a cut-off. At 5′0″ and 150 lb, traditional BMI is {c5["traditional"]} '
     f'({c5["traditional_category"]}) and New BMI {c5["new"]} ({c5["new_category"]}); at 6′4″ and 210 lb, '
     f'{c6["traditional"]} ({c6["traditional_category"]}) becomes {c6["new"]} ({c6["new_category"]}). At 5′8″ the two stay '
     'within 0.3 of each other from 120 to 210 lb. The calculator shows both categories for your numbers.'),
    ('Which BMI do CDC and WHO use?',
     'CDC uses traditional BMI: weight (kg) ÷ height (m)², or weight (lb) ÷ height (in)² × 703. WHO defines adult '
     'overweight as a BMI of 25 or more and obesity as 30 or more, the same lines as CDC’s categories. The calculator puts '
     'both numbers on CDC’s scale.'),
]
CHEVRON = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{q}{CHEVRON}</button>'
                   f'<div class="faq-answer"><p>{a}</p></div></div>' for q, a in FAQ)

# ---------------------------------------------------------------- the calculator (shared parts; ids and starting values kept)
def field(fid, label, cls, value, lo, hi):
    return (f'<div class="form-group"><label class="form-label" for="{fid}">{label}</label>'
            f'<input type="number" id="{fid}" class="form-input {cls}" value="{value}" min="{lo}" max="{hi}"></div>')


def tile(label, rid, wide=False):
    return (f'<div class="result-item{" result-item--wide" if wide else ""}"><div class="result-item-label">{label}</div>'
            f'<div class="result-item-value" id="{rid}">—</div></div>')


CALC = ('<div class="calculator-card"><div id="panel-newbmi" class="calc-panel active">'
        '<div class="unit-toggle"><button class="unit-btn active" data-unit="imperial">Imperial (ft, lbs)</button>'
        '<button class="unit-btn" data-unit="metric">Metric (cm, kg)</button></div>'
        '<div class="form-grid">'
        '<div class="form-row form-row--trio imperial-inputs">'
        + field('newbmi-height-ft', 'Height (ft)', 'height-ft', 5, 1, 8)
        + field('newbmi-height-in', 'Height (in)', 'height-in', 8, 0, 11)
        + field('newbmi-weight-lbs', 'Weight (lb)', 'weight-lbs', 160, 50, 500) + '</div>'
        '<div class="form-row form-row--pair metric-inputs" hidden>'
        + field('newbmi-height-cm', 'Height (cm)', 'height-cm', 173, 50, 250)
        + field('newbmi-weight-kg', 'Weight (kg)', 'weight-kg', 73, 20, 250) + '</div>'
        '</div>'
        '<button class="calculate-btn" id="calc-newbmi-btn">Calculate New BMI</button>'
        '<div class="results-section" id="newbmi-results">'
        '<div class="bmi-result-card normal" id="newbmi-result-card"><div class="bmi-value normal" id="newbmi-bmi-value">—</div>'
        '<div class="bmi-category" id="newbmi-bmi-category">—</div><div class="bmi-range" id="newbmi-bmi-range">—</div></div>'
        '<div class="bmi-scale"><div class="bmi-scale-bar"><div class="bmi-scale-segment underweight">Under</div>'
        '<div class="bmi-scale-segment normal">Healthy</div><div class="bmi-scale-segment overweight">Over</div>'
        '<div class="bmi-scale-segment obese">Class 1</div><div class="bmi-scale-segment obese-severe">Class 2+</div>'
        '<div class="bmi-scale-marker" id="newbmi-scale-marker"></div></div>'
        '<div class="bmi-scale-labels"><span>15</span><span>18.5</span><span>25</span><span>30</span><span>35</span><span>40</span></div></div>'
        '<div class="er-section"><h2>New BMI and traditional BMI</h2><div class="results-grid">'
        + tile('New BMI', 'newbmi-bmi-value-compare') + tile('Traditional BMI', 'newbmi-traditional-value')
        + tile('Difference', 'newbmi-diff', True) + tile('Category', 'newbmi-category-change', True) + '</div></div>'
        '<div class="er-section"><h2>Healthy weight at your height</h2>'
        '<p class="er-note">CDC’s healthy range, a traditional BMI of 18.5 to 24.9.</p><div class="results-grid">'
        + tile('Lowest healthy weight', 'newbmi-healthy-min') + tile('Highest healthy weight', 'newbmi-healthy-max') + '</div>'
        '<div class="weight-range-box"><p id="newbmi-weight-diff">—</p></div></div>'
        '</div></div></div>')

# ---------------------------------------------------------------- the page
up60, dn72, dn76 = BH[60]['percent'].lstrip('+'), pct_abs(BH[72]['percent']), pct_abs(BH[76]['percent'])
MAIN = (
    '<main class="reading"><div class="container">'
    '<div class="page-head">'
    f'<h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">See your BMI with Nick Trefethen’s 2013 formula next to the traditional one.</p>'
    '<p class="intro-note">A mathematician’s proposal, not a medical standard: CDC still calculates BMI with height '
    'squared. <a href="#sources">Method and sources</a></p>'
    '</div>'
    + CALC +
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>New BMI</strong> is Nick Trefethen’s 2013 alternative to the traditional formula: '
    '1.3 × kg ÷ m<sup>2.5</sup>, or 5734 × lb ÷ in<sup>2.5</sup>. It <strong>matches traditional BMI at about 5′6.5″ '
    '(1.69 m)</strong>, reads higher if you are shorter and lower if you are taller.</p><ul>'
    f'<li>The gap depends on height alone: New BMI is <strong>{up60} higher</strong> than traditional BMI at 5′0″ and '
    f'<strong>{dn72} lower</strong> at 6′0″, whatever you weigh.</li>'
    f'<li>A traditional BMI of 25.0 becomes {b25[60]} at 5′0″ and {b25[72]} at 6′0″.</li>'
    '<li>Trefethen says his formula is “not based on epidemiological studies” and may not be an improvement.</li>'
    '<li>CDC’s formula uses height squared and its cut-offs are set on that number, so <strong>use traditional BMI for '
    'anything medical</strong>.</li></ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information '
    'only. BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>'
    '<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
    '<a href="#formulas">The formulas</a><a href="#by-height">By height</a><a href="#side-by-side">Side by side</a>'
    '<a href="#examples">Examples</a><a href="#why">Why 2.5</a><a href="#which">Which to use</a>'
    '<a href="#faq">FAQ</a><a href="#sources">Sources</a></nav>'

    '<section id="formulas" class="content-section flow"><h2>The two formulas</h2>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap">'
    '<caption>Traditional BMI and New BMI</caption>'
    '<thead><tr><th scope="col">Formula</th><th scope="col">US units</th><th scope="col">Metric</th></tr></thead>'
    '<tbody><tr><th scope="row">Traditional BMI</th><td>lb ÷&nbsp;in²&nbsp;×&nbsp;703</td><td>kg ÷&nbsp;m²</td></tr>'
    '<tr><th scope="row">New BMI</th><td>5734&nbsp;×&nbsp;lb ÷&nbsp;in<sup>2.5</sup></td>'
    '<td>1.3&nbsp;×&nbsp;kg ÷&nbsp;m<sup>2.5</sup></td></tr>'
    '</tbody></table></div>'
    '<p>The constants keep the reading unchanged at what Trefethen calls “average height, which I take to be about '
    '66.5 inches, i.e., 1.69 meters”. The square root of 1.69 is 1.3, so at that height New BMI and traditional BMI are '
    'the same number.</p>'
    '<p>Divide one formula by the other and weight cancels: <strong>New BMI = traditional BMI × 1.3 ÷ √height (m)</strong>. '
    'Below 1.69 m that factor is above 1, so New BMI comes out higher; above 1.69 m it is below 1, so it comes out '
    'lower.</p></section>'

    '<section id="by-height" class="content-section flow"><h2>How much New BMI changes your number</h2>'
    '<p>The figure shows the gap in points at 154 lb (70 kg); the table under it gives the gap as a percentage of '
    'traditional BMI.</p>'
    + figure() + by_height_table() +
    '<p>Weight doesn’t change these percentages, only the number of points they come to, which is why the gap grows with '
    'weight in the next table.</p>'
    '<p>Trefethen’s rough guide is that “each person 6 feet tall would lose a point from their BMI reading” and “each '
    f'person 5 feet tall would gain a point”. At a traditional BMI of 25.0 the formula gives {dn6} point less at 6′0″ and '
    f'{up5} points more at 5′0″.</p></section>'

    '<section id="side-by-side" class="content-section flow"><h2>Traditional and New BMI side by side</h2>'
    '<p>Each row is what the calculator above prints for that height and weight. The difference subtracts the two rounded '
    'numbers, as the calculator does.</p>'
    + side_table() +
    f'<p class="source-note">† The category changes with New BMI: at 5′0″ and 150 lb from {c5["traditional_category"]} '
    f'to {c5["new_category"]}, at 6′4″ and 210 lb from {c6["traditional_category"]} to {c6["new_category"]}, and at 6′0″ '
    f'and 120 lb from {c7["traditional_category"]} to {c7["new_category"]} (the calculator’s names for a BMI of 16 to '
    '16.9 and under 16).</p>'
    f'<p>The widest gaps sit at the ends: {big_pos["difference"]} at 5′0″ and 210 lb, {big_neg["difference"]} at 6′4″ and '
    '210 lb. At 5′8″, close to the 5′6.5″ crossover, the two formulas stay within 0.3 of each other at every weight '
    'shown.</p></section>'

    '<section id="examples" class="content-section flow"><h2>Two worked examples</h2>'
    + example(e62) + example(e74) + '</section>'

    '<section id="why" class="content-section flow"><h2>Why Trefethen proposed it</h2>'
    f'<p>In a {ext(ECONOMIST, "letter to The Economist")} published on 5 January 2013, signed as professor of numerical '
    'analysis at the University of Oxford, Nick Trefethen called BMI “a bizarre measure”. He wrote: “We live in a '
    'three-dimensional world, yet the BMI is defined as weight divided by height squared.” His conclusion was that '
    '“millions of short people think they are thinner than they are, and millions of tall people think they are fatter.”</p>'
    f'<p>The formula is on his {ext(TREFETHEN, "Oxford page")}, where he explains the exponent: “I propose that a better '
    'approximation to the actual sizes and shapes of healthy bodies might be given by an exponent of 2.5.”</p>'
    '<p>On the same page he sets out the limits of his proposal. “I am an applied mathematician, not a doctor or an '
    'epidemiologist,” he writes, and the new formulas are “not based on epidemiological studies” and may not be an '
    'improvement. He points to a 2007 paper by Heymsfield and colleagues in the American Journal of Clinical Nutrition '
    'that supports the exponent 2.</p>'
    '</section>'

    '<section id="which" class="content-section flow"><h2>Which number to use</h2>'
    f'<p>For anything medical, use traditional BMI. CDC {ext(CDC_CALC, "calculates BMI")} as weight (kg) ÷ height (m)², '
    f'or weight (lb) ÷ height (in)² × 703, and sets its {ext(CDC_CATS, "adult categories")} on that number: under 18.5 '
    'underweight, 18.5 to 24.9 healthy weight, 25 to 29.9 overweight and 30 or more obesity. '
    f'{ext(WHO, "WHO")} uses the same two lines for adults: overweight at a BMI of 25 or more, obesity at 30 or more.</p>'
    '<p>New BMI is worth a second look if you are very short or very tall, where the formulas part most: '
    f'{up60} higher at 5′0″, {dn76} lower at 6′4″. The calculator applies CDC’s cut-offs to both numbers so you can '
    'compare them.</p>'
    f'<p>Neither formula can separate muscle from fat. {ext(CDC_ABOUT, "CDC notes")} that “BMI does not distinguish '
    'between fat, muscle, and bone mass”, and New BMI works from the same height and weight. The '
    '<a href="/body-fat-calculator/">body fat calculator</a> estimates body fat with a tape measure or calipers, and '
    '<a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a> covers how the two measures differ.</p></section>'

    f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}</div></section>'

    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we worked the figure out '
    'from the two formulas with the method below.</p><ul class="source-list">'
    f'<li>Trefethen N. {ext(TREFETHEN, "New BMI (New Body Mass Index)")}, University of Oxford: the formula in metric '
    'and US units, the constants, the 2.5 exponent and his caveats.</li>'
    f'<li>Trefethen N. {ext(ECONOMIST, "Letter")}, The Economist, 5 January 2013.</li>'
    f'<li>CDC. {ext(CDC_CALC, "Calculating BMI")}: the formula in metric and US units.</li>'
    f'<li>CDC. {ext(CDC_CATS, "Adult BMI Categories")}: the cut-offs.</li>'
    f'<li>CDC. {ext(CDC_ABOUT, "About Body Mass Index (BMI)")}: what BMI does not measure.</li>'
    f'<li>WHO. {ext(WHO, "Obesity and overweight")}, fact sheet: the adult definitions of overweight and obesity.</li>'
    '</ul><p class="source-note"><strong>Method.</strong> Every number in the tables, the figure and the examples is our '
    'calculation with the calculator’s own arithmetic: traditional BMI = lb ÷ in² × 703 (kg ÷ m² for metric entries) and '
    'New BMI = 1.3 × kg ÷ m<sup>2.5</sup>, with kg = lb ÷ 2.20462 and m = in × 0.0254. Each BMI is rounded once to one '
    'decimal, halves up, and its category comes from that rounded value. The difference subtracts the two rounded values, '
    'so it matches what the calculator prints. The percentages are 1.3 ÷ √height (m) − 1, rounded to 0.1%. The figure '
    'plots the unrounded difference at 70 kg every 0.01 m from 1.40 to 2.00 m. Trefethen’s 5734 rounds the US-unit '
    'constant, so working in pounds and inches with it can move the last decimal near a rounding edge; both worked '
    'examples give the same result either way.</p></section>'

    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul><li><a href="/">BMI calculator</a></li>'
    '<li><a href="/women-bmi-calculator/">BMI calculator for women</a></li>'
    '<li><a href="/men-bmi-calculator/">BMI calculator for men</a></li>'
    '<li><a href="/age-bmi-calculator/">BMI calculator by age</a></li>'
    '<li><a href="/body-fat-calculator/">Body fat calculator</a></li>'
    '<li><a href="/ideal-weight/">Ideal weight calculator</a></li></ul></div>'
    '<div><h3>Guides and data</h3><ul><li><a href="/blog/bmi-formula/">BMI formula</a></li>'
    '<li><a href="/bmi-chart/">BMI chart</a></li>'
    '<li><a href="/blog/healthy-bmi-range/">Healthy BMI range</a></li>'
    '<li><a href="/blog/body-fat-vs-bmi/">Body fat vs BMI</a></li>'
    '<li><a href="/blog/bmi-limitations/">Limitations of BMI</a></li>'
    '<li><a href="/blog/what-is-bmi/">What is BMI?</a></li></ul></div>'
    '</div></section>'
    '</div></main>')


def nbsp_units(markup):
    """A number keeps its unit on one line (DEVLOG §4, CMB-021): a no-break space between them, in text only."""
    unit = re.compile(r'(\d) (lb|kg|cm|m|points?)(?![\w])')
    out = []
    for chunk in re.split(r'(?s)(<svg\b.*?</svg>)', markup):           # SVG text never wraps: leave the figure alone
        out.append(chunk if chunk.startswith('<svg') else
                   ''.join(p if p.startswith('<') else unit.sub('\\1\u00a0\\2', p) for p in re.split(r'(<[^>]+>)', chunk)))
    return ''.join(out)


MAIN = nbsp_units(MAIN)
faq_html = nbsp_units(faq_html)
FAQ = [(q, nbsp_units(a)) for q, a in FAQ]


def faq_text(a): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', a)).replace('\u00a0', ' ')).strip()


LD = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE,
     'isPartOf': {'@id': SITE + '/#website'}, 'mainEntity': {'@id': URL + '#calculator'},
     'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG['16x9'], 'width': 1200, 'height': 675}},
    {'@type': 'WebApplication', '@id': URL + '#calculator', 'image': [IMG['1x1'], IMG['4x3'], IMG['16x9']],
     'name': H1,
     'description': ('Calculates New BMI (Nick Trefethen’s 2013 formula, 1.3 × kg ÷ m^2.5) and traditional BMI (CDC’s '
                     'formula) from height and weight in US or metric units, shows the difference and each number’s '
                     'category on CDC’s adult scale, and gives the healthy weight range for the height on traditional BMI.'),
     'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any',
     'browserRequirements': 'Requires JavaScript', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
     'featureList': ['New BMI and traditional BMI from US or metric units', 'The difference between the two, as rounded',
                     'Each number’s category on CDC’s adult scale', 'Healthy weight range for your height (traditional BMI)'],
     'author': {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}},
    {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Calculators', 'item': SITE + '/calculators/'},
        {'@type': 'ListItem', 'position': 3, 'name': 'New BMI Calculator (Trefethen)', 'item': URL}]},
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
    assert '"' not in DESC and '"' not in OG_ALT                 # attribute values never hold a raw quote (DEVLOG §4)
    head, rest = src.split('</head>', 1)
    head = put_meta(head, 'name', 'description', DESC)
    head = put_meta(head, 'property', 'og:title', OG_TITLE)
    head = put_meta(head, 'property', 'og:description', DESC)
    head = put_meta(head, 'property', 'og:image', IMG['16x9'])
    head = put_meta(head, 'property', 'og:image:alt', OG_ALT, after=('property', 'og:image'))
    head = put_meta(head, 'property', 'og:image:width', '1200')
    head = put_meta(head, 'property', 'og:image:height', '675')
    head = put_meta(head, 'name', 'twitter:title', OG_TITLE)
    head = put_meta(head, 'name', 'twitter:description', DESC)
    head = put_meta(head, 'name', 'twitter:image', IMG['16x9'])
    blocks = list(re.finditer(r'(?s)\n?<script type="application/ld\+json">.*?</script>', head))
    assert blocks, 'no JSON-LD in the head'
    ld = '\n<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>'
    head = head[:blocks[0].start()] + ld + ''.join(head[a.end():b.start()] for a, b in zip(blocks, blocks[1:])) + head[blocks[-1].end():]
    assert f'<title>{TITLE}</title>' in head
    body = re.sub(r'(?s)<main\b.*?</main>', lambda _: MAIN, rest, count=1)
    return head + '</head>' + body


if __name__ == '__main__':
    src = open(PAGE, encoding='utf-8').read()
    out = build(src)
    assert build(out) == out, 'not idempotent'
    with open(PAGE, 'w', encoding='utf-8') as f:
        f.write(out)
    words = len(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<svg.*?</svg>', ' ', MAIN)))).split())
    print(f'{PAGE}: {len(out):,} bytes; <main> {len(MAIN):,} bytes, about {words} words outside the figure')
