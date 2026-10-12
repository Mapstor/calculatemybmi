#!/usr/bin/env python3
"""CMB-006 PILOT-MEN — rebuilds /men-bmi-calculator/ with the content-page, seo-visibility,
anti-slop-prose and impeccable skills, inside the current look.

Every number on the page is read from men_stats.json (our NHANES 2021-2023 calculation, see
men_stats.py), from the calculator's own rounding rule (weightBounds, mirrored below), or is a
figure already verified on the live page (Health E-Stat 111, Series 3 No. 50, DXA analysis,
Provencher 2018, Wing 2011, Winter 2014).

usage: python3 gen_men_pilot.py REPO_ROOT STATS_JSON
Runs once, on the page as it stood after CMB-005; kept as the build record and as the template for a rollout.
"""
import sys, os, re, json, math, html

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
PAGE = os.path.join(ROOT, 'men-bmi-calculator/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()

# ---------------------------------------------------------------- numbers
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def bounds(h, lo, hi):                       # mirrors weightBounds() in assets/js/calculator.js
    k = h * h / 703; L = (lo - 0.05) * k; H = (hi + 0.05) * k
    return dict(minLb=math.ceil(L - 1e-9), maxLb=math.ceil(H - 1e-9) - 1,
                minKg=math.ceil(L / 2.20462 - 1e-9), maxKg=math.ceil(H / 2.20462 - 1e-9) - 1)
Q = S['p1_p99']
def rank(b):
    if b <= Q[0]: return 0.0
    if b >= Q[-1]: return 100.0
    for i in range(98):
        if b < Q[i + 1]: return i + 1 + (b - Q[i]) / (Q[i + 1] - Q[i])

EX_H, EX_W = 70, 180                          # calculator defaults: 5'10", 180 lb
EX_BMI = r1(EX_W * 703 / EX_H ** 2)
EX_KG = round(EX_W / 2.20462, 1)
HB = bounds(EX_H, 18.5, 24.9)
EX_GAP = EX_W - HB['maxLb']
EX_GAP_KG = round(EX_GAP / 2.20462, 1)
EX_RANK = round(rank(EX_BMI))
EX_PRIME = round(EX_BMI / 25, 2)
EX_PI = round((EX_W / 2.20462) / ((EX_H * 2.54 / 100) ** 3), 1)
FROM = {c: bounds(EX_H, c, 99)['minLb'] for c in (25, 30, 35, 40)}
T = S['table']
assert (EX_BMI, EX_GAP, EX_RANK, HB['minLb'], HB['maxLb']) == (25.8, 7, 32, 129, 173), (EX_BMI, EX_GAP, EX_RANK, HB)
assert T['p50'] == 28.2 and S['bmi_n'] == 2680
WAIST_SHARE = round(S['share_waist_over_102cm_bmi_25_29_9'])          # 30 -> "3 in 10"
assert WAIST_SHARE == 30
WAIST_ALL = round(S['share_waist_over_102cm'])                          # 47
WAIST_MEAN = S['waist_mean_in']                                          # 40.6
assert (WAIST_ALL, WAIST_MEAN) == (47, 40.6)
def lb_kg(lb): return f'{lb} lb' if False else lb

def fmt_kg1(lb): return f'{lb / 2.20462:.1f}'

# ---------------------------------------------------------------- SVGs (checked for label collisions below)
TEXTS = []          # (svg id, x0, y0, x1, y1, label) for the collision check
def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#1f2937', extra=''):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"'
            + (f' font-weight="{weight}"' if weight != 400 else '') + f' fill="{fill}"{extra}>{html.escape(s)}</text>')

def svg_example():
    sid = 'ex'
    W, x0, x1 = 300, 10, 290
    out = []
    out.append(text(sid, 150, 22, f'{EX_W} lb × 703 ÷ 70² = {EX_BMI}', 17, weight=700, fill='#111827'))
    out.append(text(sid, 150, 44, f'70 in (177.8 cm), {EX_W} lb ({EX_KG} kg)', 14, fill='#4b5563'))
    sx = lambda b: x0 + (b - 15) * (x1 - x0) / 25
    segs = [(15, 18.5, '#3b82f6'), (18.5, 25, '#22c55e'), (25, 30, '#f59e0b'), (30, 35, '#ef4444'), (35, 40, '#991b1b')]
    for a_, b_, c in segs:
        out.append(f'<rect x="{sx(a_):.1f}" y="84" width="{sx(b_) - sx(a_):.1f}" height="18" fill="{c}"/>')
    mx = sx(EX_BMI)
    out.append(f'<line x1="{mx:.1f}" y1="78" x2="{mx:.1f}" y2="108" stroke="#111827" stroke-width="3"/>')
    out.append(text(sid, mx, 72, f'BMI {EX_BMI}: overweight', 15, weight=700, fill='#111827'))
    for b_ in (18.5, 25, 30, 35):
        out.append(text(sid, sx(b_), 124, f'{b_:g}', 14, fill='#4b5563'))
    wl, wh = 120, 200
    wx = lambda lb: x0 + (lb - wl) * (x1 - x0) / (wh - wl)
    out.append(text(sid, x0, 160, f'Healthy at 5′10″: {HB["minLb"]}–{HB["maxLb"]} lb', 15, anchor='start', weight=600, fill='#111827'))
    out.append(f'<rect x="{x0}" y="192" width="{x1 - x0}" height="16" rx="8" fill="#e5e7eb"/>')
    out.append(f'<rect x="{wx(HB["minLb"]):.1f}" y="192" width="{wx(HB["maxLb"]) - wx(HB["minLb"]):.1f}" height="16" fill="#86efac"/>')
    px = wx(EX_W)
    gx0 = wx(HB['maxLb'])
    out.append(f'<path d="M{gx0:.1f} 188 V182 H{px:.1f} V188" fill="none" stroke="#111827" stroke-width="1.5"/>')
    out.append(text(sid, (gx0 + px) / 2, 176, f'+{EX_GAP} lb', 14, weight=700, fill='#111827'))
    out.append(f'<line x1="{px:.1f}" y1="186" x2="{px:.1f}" y2="214" stroke="#111827" stroke-width="3"/>')
    out.append(text(sid, wx(HB['minLb']), 232, f'{HB["minLb"]} lb', 14, fill='#374151'))
    out.append(text(sid, gx0 - 6, 232, f'{HB["maxLb"]}', 14, fill='#374151'))
    out.append(text(sid, px + 10, 232, f'{EX_W}', 14, weight=700, fill='#111827'))
    title = f'Worked example: 5 feet 10 inches and {EX_W} pounds gives a BMI of {EX_BMI}'
    desc = (f'{EX_W} times 703 divided by 70 squared equals {EX_BMI}. On the BMI scale from 15 to 40 the marker sits just past 25, '
            f'in the overweight range. On a weight bar for 5 feet 10 inches, the healthy range runs from {HB["minLb"]} to {HB["maxLb"]} pounds '
            f'and the marker at {EX_W} pounds sits {EX_GAP} pounds above it.')
    return (f'<svg viewBox="0 0 {W} 240" width="{W}" height="240" role="img" aria-labelledby="fig-ex-t fig-ex-d" font-family="inherit">'
            f'<title id="fig-ex-t">{html.escape(title)}</title><desc id="fig-ex-d">{html.escape(desc)}</desc>'
            + ''.join(out) + '</svg>')

def svg_waist():
    sid = 'waist'
    W, x0, x1 = 300, 10, 290
    ix = lambda inch: x0 + (inch - 30) * (x1 - x0) / 20
    out = []
    out.append(text(sid, 150, 20, 'NIH cut-off: 40 in (102 cm)', 15, weight=700, fill='#7f1d1d'))
    out.append(f'<rect x="{x0}" y="36" width="{ix(40) - x0:.1f}" height="32" fill="#bbf7d0"/>')
    out.append(f'<rect x="{ix(40):.1f}" y="36" width="{x1 - ix(40):.1f}" height="32" fill="#fecaca"/>')
    out.append(text(sid, (x0 + ix(40)) / 2, 57, 'Lower risk', 15, weight=600, fill='#14532d'))
    out.append(text(sid, (ix(40) + x1) / 2, 57, 'Higher risk', 15, weight=600, fill='#7f1d1d'))
    out.append(f'<line x1="{ix(40):.1f}" y1="28" x2="{ix(40):.1f}" y2="76" stroke="#7f1d1d" stroke-width="3"/>')
    for inch, anchor in ((30, 'start'), (35, 'middle'), (45, 'middle'), (50, 'end')):
        out.append(f'<line x1="{ix(inch):.1f}" y1="68" x2="{ix(inch):.1f}" y2="74" stroke="#6b7280" stroke-width="1"/>')
        out.append(text(sid, ix(inch), 92, f'{inch} in', 14, anchor=anchor, fill='#4b5563'))
    ax = ix(WAIST_MEAN)
    out.append(f'<line x1="{ax:.1f}" y1="68" x2="{ax:.1f}" y2="104" stroke="#164e63" stroke-width="2" stroke-dasharray="3 2"/>')
    out.append(f'<circle cx="{ax:.1f}" cy="68" r="4" fill="#164e63"/>')
    out.append(text(sid, ax, 122, f'Average US man: {WAIST_MEAN} in ({round(WAIST_MEAN * 2.54)} cm)', 14, weight=600, fill='#164e63'))
    title = 'Waist size for men: the NIH cut-off at 40 inches (102 cm)'
    desc = (f'A scale from 30 to 50 inches. Below 40 inches is marked lower risk, above it higher risk. '
            f'A dashed marker shows the average US man aged 20 and over at {WAIST_MEAN} inches, just above the cut-off.')
    return (f'<svg viewBox="0 0 {W} 130" width="{W}" height="130" role="img" aria-labelledby="fig-waist-t fig-waist-d" font-family="inherit">'
            f'<title id="fig-waist-t">{html.escape(title)}</title><desc id="fig-waist-d">{html.escape(desc)}</desc>'
            + ''.join(out) + '</svg>')

SVG_EX, SVG_WAIST = svg_example(), svg_waist()
# collision check: no two labels in the same figure overlap, and every label stays inside the 320-wide viewBox
for i, a in enumerate(TEXTS):
    assert a[1] >= 0 and a[3] <= 300, f'label outside viewBox: {a}'
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
            raise SystemExit(f'label collision in {a[0]}: {a[5]!r} vs {b[5]!r}')

# ---------------------------------------------------------------- copy
CDC_CAT = 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html'
HESTAT = 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm'
SR3 = 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf'
NHANES = 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm'
NHLBI_GL = 'https://www.ncbi.nlm.nih.gov/books/NBK2003/'
NHLBI = 'https://www.nhlbi.nih.gov/health/overweight-and-obesity'
PROV = 'https://doi.org/10.1519/JSC.0000000000002449'
WING = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/'
WINTER = 'https://pubmed.ncbi.nlm.nih.gov/24452240/'
GALLAGHER = 'https://pubmed.ncbi.nlm.nih.gov/10966886/'
def a(href, txt):   # external sources open in a new tab, as on every other page
    ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
    return f'<a href="{href}"{ext}>{txt}</a>'

FAQ = [
    ('What is a healthy BMI for men?',
     f'The healthy BMI range for men is <strong>18.5 to 24.9</strong>, the same as for women, and it doesn’t change with age ({a(CDC_CAT, "CDC")}). '
     f'At 5′10″ (177.8 cm) that means {HB["minLb"]} to {HB["maxLb"]} lb ({HB["minKg"]} to {HB["maxKg"]} kg). '
     f'The {a("/blog/bmi-chart-men/", "BMI chart for men")} lists the range for every height from 5′2″ to 6′6″.'),
    ('What is the average BMI for American men?',
     f'The average BMI of US men aged 20 and over is <strong>29.4</strong> and the median is {T["p50"]}, both in the overweight range '
     f'(CDC measurements, August 2021–August 2023; {a(SR3, "NCHS Series 3, No. 50")}). In the same survey 39.3% of men had obesity and another 35.5% were overweight, '
     f'so about 3 in 4 are above the healthy range ({a(HESTAT, "NCHS Health E-Stat 111")}, age-adjusted). '
     f'More averages by height and age: {a("/average-weight/", "average weight for men")}.'),
    ('How is BMI calculated for men?',
     f'The same way as for women: weight in kilograms divided by height in metres squared. In pounds and inches, multiply weight by 703 and divide by height squared. '
     f'For a man who is 5′10″ (70 in) and weighs {EX_W} lb: {EX_W} × 703 ÷ 4,900 = <strong>{EX_BMI}</strong>. '
     f'The {a("/blog/bmi-formula/", "BMI formula guide")} explains the 703.'),
    ('Is BMI accurate for muscular men?',
     f'Not always. BMI can’t tell muscle from fat, so a very muscular man can score overweight or even obese with little body fat. '
     f'At the NFL Scouting Combine, 53.4% of players had a BMI of 30 or more, but only 8.9% had obesity when body fat was measured ({a(PROV, "Provencher et al., 2018")}). '
     f'A waist measurement or a {a("/body-fat-calculator/", "body fat estimate")} tells you more; see {a("/blog/bmi-for-athletes/", "BMI for athletes")}.'),
    ('Should men focus on BMI or body fat percentage?',
     f'Both, if you can. BMI needs only a scale and your height, so it’s easy to track. Body fat percentage is more direct but needs equipment: '
     f'DXA is the reference method, underwater weighing came closest to it, and at home skinfold calipers come closest ({a("/blog/how-to-measure-body-fat/", "how accurate each method is")}). '
     f'NIH guidelines pair BMI with a waist measurement, which costs nothing.'),
    ('Why does waist size matter for men?',
     f'NIH guidelines treat a waist of more than 40 inches (102 cm) as a marker of higher risk of type 2 diabetes, high blood pressure and heart disease in men, '
     f'mainly at a BMI of 25 to 34.9; above that, nearly every man is over the cut-off ({a(NHLBI_GL, "NHLBI")}). In the overweight range it splits men: about 3 in 10 US men with a BMI of 25 to 29.9 '
     f'have a waist over 102 cm, and the rest don’t (our calculation from CDC NHANES 2021–2023).'),
    ('Does BMI change with age for men?',
     f'The cut-offs don’t: 18.5 to 24.9 is the healthy range at every adult age. Body composition does change: at the same BMI, older men tend to carry more fat. '
     f'The body fat ranges matched to a healthy BMI rise from 8–19.9% at ages 20–39 to 13–24.9% at 60–79 ({a(GALLAGHER, "Gallagher et al., 2000")}, provisional ranges). '
     f'For adults 65 and over, a meta-analysis of 197,940 people found the lowest death rates across BMI 23 to 33 ({a(WINTER, "Winter et al., 2014")}); '
     f'that is an observed association, not a target. See the {a("/age-bmi-calculator/", "BMI calculator by age")}.'),
    ('What BMI raises heart disease risk in men?',
     f'NIH guidelines link a BMI above the healthy range with higher risk of high blood pressure, coronary heart disease and stroke, and the risk climbs from the overweight range '
     f'(25 to 29.9) into obesity (30 and above) ({a(NHLBI_GL, "NHLBI")}). At a BMI of 25 to 34.9, a waist over 40 inches (102 cm) adds to that risk. '
     f'{a("/blog/bmi-categories/", "BMI categories explained")} covers each range.'),
]

def faq_html():
    chev = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
    return ''.join(f'<div class="faq-item"><button class="faq-question">{html.escape(q)}{chev}</button>'
                   f'<div class="faq-answer"><p>{ans}</p></div></div>' for q, ans in FAQ)

def plain(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))

pct_rows = [('5th', 'p5'), ('10th', 'p10'), ('25th', 'p25'), ('50th (median)', 'p50'), ('75th', 'p75'), ('90th', 'p90'), ('95th', 'p95')]
def cat(b):
    return ('Underweight' if b < 18.5 else 'Healthy' if b < 25 else 'Overweight' if b < 30 else
            'Obesity class 1' if b < 35 else 'Obesity class 2' if b < 40 else 'Obesity class 3')
PCT_TABLE = ''.join(f'<tr><th scope="row">{lab}</th><td class="num">{T[k]:.1f}</td><td>{cat(T[k])}</td></tr>' for lab, k in pct_rows)

def height_row(h):
    b, o, ob = bounds(h, 18.5, 24.9), bounds(h, 25, 99), bounds(h, 30, 99)
    ft = f'{h // 12}′{h % 12}″<span class="unit-alt">{h * 2.54:.1f} cm</span>'
    return (f'<tr><th scope="row">{ft}</th><td>{b["minLb"]}–{b["maxLb"]} lb<span class="unit-alt">{b["minKg"]}–{b["maxKg"]} kg</span></td>'
            f'<td>{o["minLb"]} lb<span class="unit-alt">{o["minKg"]} kg</span></td><td>{ob["minLb"]} lb<span class="unit-alt">{ob["minKg"]} kg</span></td></tr>')

# age table: reuse the verified rows already on the page (G2i, our NHANES calculation)
age_rows = re.findall(r"<tr><th scope='row'>(\d\d–\d\d|80\+)</th><td>([\d.]+)</td><td>(\d+)</td><td>([\d.]+)</td></tr>", src)
assert len(age_rows) == 7, age_rows
AGE_TABLE = ''.join(f'<tr><th scope="row">{a_}</th><td class="num">{b_}</td><td class="num">{w_}</td><td class="num">{x_}</td></tr>' for a_, b_, w_, x_ in age_rows)
assert age_rows[2] == ('40–49', '30.5', '210', '41.2')

MAIN = f'''
<main class="reading">
<div class="container">
<div class="page-head">
<h1>BMI Calculator for Men</h1>
<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>
<p class="intro-text">Enter your height and weight to get your BMI, your healthy weight range and where you rank among US men.</p>
<p class="intro-note">Same CDC cut-offs as for women. The US comparison uses CDC measurements of {S["bmi_n"]:,} men, 2021–2023. <a href="#sources">Method and sources</a></p>
</div>
@@CALCULATOR@@
<div class="key-takeaways">
<div class="key-takeaways-title">Key takeaways</div>
<p class="answer"><strong>BMI for men</strong> uses the same formula and cut-offs as for women: weight in kilograms divided by height in metres squared, or pounds × 703 ÷ inches². <strong>18.5 to 24.9 is the healthy range</strong>, 25 to 29.9 is overweight and 30 or more is obesity. NIH guidelines add a waist cut-off for men: more than 40 inches (102 cm).</p>
<ul>
<li>The average US man has a BMI of <strong>29.4</strong>, and about 3 in 4 are at 25 or above (CDC, 2021–2023).</li>
<li><strong>Muscle raises BMI</strong> without adding fat, so a muscular man can score overweight.</li>
<li><strong>Waist size adds what BMI misses:</strong> about 3 in 10 US men with an overweight BMI have a waist over 40 inches.</li>
<li>The cut-offs are the same at every adult age.</li>
</ul>
</div>
<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information only. BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>
<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span><a href="#read-result">Your result</a><a href="#us-men">US men compared</a><a href="#by-height">Weight by height</a><a href="#misleading">When BMI misleads</a><a href="#waist">Waist size</a><a href="#health-risks">Health risks</a><a href="#situations">Situations</a><a href="#faq">FAQ</a><a href="#sources">Sources</a></nav>

<section id="read-result" class="content-section flow">
<h2>How to read your result</h2>
<p>Every number below uses the calculator’s imperial starting values: a man who is 5′10″ (177.8 cm) and weighs {EX_W} lb ({EX_KG} kg).</p>
<figure class="figure">{SVG_EX}<figcaption>{EX_W} lb at 5′10″ gives a BMI of {EX_BMI}, just inside the overweight range; the healthy range at that height ends at {HB["maxLb"]} lb.</figcaption></figure>
<dl>
<dt>BMI: {EX_BMI}, overweight</dt><dd>Weight divided by height squared, rounded to one decimal; the category comes from that rounded number. CDC cut-offs for adults: under 18.5 underweight, 18.5 to 24.9 healthy, 25 to 29.9 overweight, 30 and above obesity.</dd>
<dt>Healthy weight: {HB["minLb"]}–{HB["maxLb"]} lb</dt><dd>The lightest and heaviest whole-pound weights at your height with a BMI of 18.5 to 24.9; in whole kilograms, {HB["minKg"]}–{HB["maxKg"]} kg. It depends only on height. In imperial mode the calculator also shows each limit converted ({fmt_kg1(HB["minLb"])} and {fmt_kg1(HB["maxLb"])} kg).</dd>
<dt>{EX_GAP} lb ({EX_GAP_KG} kg) above the healthy range</dt><dd>The distance from your weight to the nearest end of that range, as imperial mode shows it ({EX_GAP_KG} kg is {EX_GAP} lb converted).</dd>
<dt>Compared with US men: higher than {EX_RANK}%</dt><dd>Where your BMI falls among men aged 20 and over whom CDC measured in 2021–2023 (next section).</dd>
<dt>BMI Prime: {EX_PRIME:.2f}</dt><dd>Your BMI divided by 25, where the overweight range starts. Under 1.00 is below it; {EX_PRIME:.2f} is {round((EX_PRIME - 1) * 100)}% over.</dd>
<dt>Ponderal index: {EX_PI} kg/m³</dt><dd>Weight divided by height cubed. There are no official adult cut-offs, so compare it only with your own earlier results.</dd>
<dt>Weight milestones</dt><dd>The weight where each CDC range starts at your height. At 5′10″: healthy from {HB["minLb"]} lb, overweight from {FROM[25]} lb, obesity from {FROM[30]} lb, class 2 obesity from {FROM[35]} lb and class 3 from {FROM[40]} lb.</dd>
<dt>What-if table</dt><dd>Your BMI and category after gaining or losing 5, 10, 15 or 20 lb (2.5 to 10 kg in metric).</dd>
</dl>
</section>

<section id="us-men" class="content-section flow">
<h2>How your BMI compares with US men</h2>
<p>CDC measured {S["bmi_n"]:,} men aged 20 and over between August 2021 and August 2023. <strong>The middle man had a BMI of {T["p50"]}</strong>, and only a quarter had a BMI under 25. Your result in the calculator is ranked against these men.</p>
<div class="stat-callout"><div class="stat-callout-value">29.4</div><div class="stat-callout-text">Average BMI of US men aged 20 and over, measured August 2021–August 2023.</div><div class="stat-callout-source">Source: CDC, {a(SR3, "NCHS Series 3, No. 50")}</div></div>
<div class="table-responsive"><table class="data-table"><caption>BMI percentiles, US men aged 20 and over, 2021–2023</caption><thead><tr><th scope="col">Percentile</th><th scope="col" class="num">BMI</th><th scope="col">Category</th></tr></thead><tbody>{PCT_TABLE}</tbody></table></div>
<p class="source-note">Read a row as: 25% of US men have a BMI of {T["p25"]} or lower. Our calculation from CDC NHANES 2021–2023 measured heights and weights ({S["bmi_n"]:,} men, survey-weighted); the same method reproduces NCHS’s published median BMI ({T["p50"]}) and 95th-percentile weight (290.6 lb).</p>
<h3>Overweight and obesity among US men</h3>
<div class="chart-bar-h"><div class="chart-bar-h-item"><span class="chart-bar-h-label">Overweight</span><div class="chart-bar-h-track"><div class="chart-bar-h-fill overweight" style="width:35.5%;"></div></div><span class="chart-bar-h-value">35.5%</span></div><div class="chart-bar-h-item"><span class="chart-bar-h-label">Obesity</span><div class="chart-bar-h-track"><div class="chart-bar-h-fill obese" style="width:39.3%;"></div></div><span class="chart-bar-h-value">39.3%</span></div><div class="chart-bar-h-item"><span class="chart-bar-h-label">Severe obesity</span><div class="chart-bar-h-track"><div class="chart-bar-h-fill obese" style="width:6.8%;"></div></div><span class="chart-bar-h-value">6.8%</span></div></div>
<p class="source-note">Men 20 and older, August 2021–August 2023, age-adjusted; severe obesity (BMI 40+) is part of obesity. Source: Fryar CD, Afful J, Saif NT. {a(HESTAT, "NCHS Health E-Stat 111")} (Feb 2026). Men and women by age: {a("/us-obesity-statistics/#age-gender-education", "obesity rates by age and gender")}.</p>
<h3>Average BMI, weight and waist by age</h3>
<p>The average US man is 5′9″ (175 cm) and weighs 199.0 lb (90.3 kg), with a BMI of 29.4 and a waist of {WAIST_MEAN} in ({round(WAIST_MEAN * 2.54)} cm). Average BMI is highest in men in their 40s and 50s (30.5 and 30.2). CDC body scans put average body fat at 27.2% at ages 20 to 59.</p>
<div class="table-responsive"><table class="data-table"><caption>US men: average BMI, weight (lb) and waist (in) by age, 2021–2023</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">BMI</th><th scope="col" class="num">Weight</th><th scope="col" class="num">Waist</th></tr></thead><tbody>{AGE_TABLE}</tbody></table></div>
<p class="source-note">Sources: our calculation from CDC NHANES 2021–2023 (the method reproduces the overall averages in {a(SR3, "NCHS Series 3 No. 50")}); body fat from our NHANES 2011–2018 DXA analysis. More: {a("/average-weight/", "average weight by height")}, {a("/body-fat-percentage-chart/", "body fat chart")}.</p>
</section>

<section id="by-height" class="content-section flow">
<h2>Healthy weight for men by height</h2>
<p>The healthy range depends only on height and is the same for men and women. Three common heights below; the {a("/blog/bmi-chart-men/", "BMI chart for men")} covers every inch from 5′2″ to 6′6″.</p>
<div class="table-responsive"><table class="data-table"><caption>Healthy weight, and where overweight and obesity start, by height</caption><thead><tr><th scope="col">Height</th><th scope="col">Healthy<span class="unit-alt">BMI 18.5–24.9</span></th><th scope="col">Overweight<span class="unit-alt">from BMI 25</span></th><th scope="col">Obesity<span class="unit-alt">from BMI 30</span></th></tr></thead><tbody>{height_row(66)}{height_row(70)}{height_row(74)}</tbody></table></div>
<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, falls in each range at the height shown. Cut-offs: {a(CDC_CAT, "CDC Adult BMI Categories")}.</p>
</section>

<section id="misleading" class="content-section flow">
<h2>When BMI misleads men</h2>
<p>BMI can’t tell muscle from fat. In CDC body scans of US men aged 20 to 59, <strong>body fat varied widely within every BMI category</strong>, and the categories overlap:</p>
<div class="table-responsive"><table class="data-table"><caption>Body fat of US men aged 20–59 by BMI category, DXA scans 2011–2018</caption><thead><tr><th scope="col">BMI category</th><th scope="col" class="num">Median body fat</th><th scope="col">Middle half of men</th></tr></thead><tbody><tr><th scope="row">Healthy<span class="unit-alt">BMI 18.5–24.9</span></th><td class="num">22.1%</td><td class="nowrap">18.6–25.0%</td></tr><tr><th scope="row">Overweight<span class="unit-alt">BMI 25–29.9</span></th><td class="num">26.9%</td><td class="nowrap">24.2–29.8%</td></tr><tr><th scope="row">Obesity<span class="unit-alt">BMI 30 or more</span></th><td class="num">31.6%</td><td class="nowrap">28.7–35.1%</td></tr></tbody></table></div>
<p class="source-note">Our analysis of CDC NHANES 2011–2018 DXA scans; full charts on the {a("/body-fat-percentage-chart/", "body fat percentage chart")}.</p>
<p>One in ten men with an overweight BMI had less body fat (under 21.7%) than the typical man with a healthy BMI (22.1%).</p>
<h3>Muscular men and athletes</h3>
<p>Very muscular men can land in the overweight or obesity range with little body fat. At the NFL Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat ({a(PROV, "Provencher et al., 2018")}). If you lift or play a power sport, estimate your body fat with the {a("/body-fat-calculator/", "body fat calculator")}; {a("/blog/bmi-for-athletes/", "BMI for athletes")} goes further.</p>
<h3>What to check alongside BMI</h3>
<ul>
<li><strong>Waist size:</strong> more than 40 in (102 cm) is the NIH cut-off for men (next section).</li>
<li><strong>Body fat percentage:</strong> DXA is the reference method and underwater weighing came closest to it; at home, skinfold calipers come closest ({a("/blog/how-to-measure-body-fat/", "how accurate each method is")}).</li>
<li><strong>Waist-to-height ratio:</strong> your waist divided by your height; the {a("/blog/waist-to-height-ratio/", "waist-to-height ratio guide")} covers the 0.5 boundary and its sources.</li>
<li><strong>Blood pressure, blood sugar and cholesterol:</strong> routine checks that BMI can’t replace.</li>
</ul>
</section>

<section id="waist" class="content-section flow">
<h2>Waist size for men: the 40-inch cut-off</h2>
<p>NIH guidelines treat a waist of more than 40 inches (102 cm) as a marker of higher risk of type 2 diabetes, high blood pressure and heart disease in men. The cut-off matters most at a BMI of 25 to 34.9; at 35 and above nearly every man is over it ({a(NHLBI_GL, "NHLBI")}).</p>
<figure class="figure">{SVG_WAIST}<figcaption>The NIH cut-off for men is a waist of more than 40 in (102 cm). The average US man aged 20 and over measures {WAIST_MEAN} in (CDC NHANES 2021–2023, our calculation).</figcaption></figure>
<div class="stat-callout"><div class="stat-callout-value">{WAIST_ALL}%</div><div class="stat-callout-text">of US men aged 20 and over have a waist of more than 102 cm (40 in).</div><div class="stat-callout-source">Our calculation from CDC {a(NHANES, "NHANES August 2021–August 2023")} ({S["waist_n"]:,} men measured)</div></div>
<p>The waist adds the most in the overweight range. <strong>About 3 in 10 US men with a BMI of 25 to 29.9 have a waist over 102 cm</strong>; the other 7 don’t, though their BMI category is the same.</p>
<h3>Waist-to-hip ratio</h3>
<p>Divide your waist by your hip measurement. A WHO expert consultation (2008) uses a ratio of 0.90 or more in men as the cut-off for a substantially increased risk of metabolic complications.</p>
<h3>How to measure your waist</h3>
<ol>
<li>Stand up straight and breathe out normally. Don’t pull your stomach in.</li>
<li>Put a tape measure around your bare waist, just above your hip bones.</li>
<li>Keep the tape snug and level all the way round, without pressing into the skin.</li>
<li>Read it at the end of a normal breath out, to the nearest half inch (or 1 cm).</li>
</ol>
<p>Measure at the same time of day so the numbers compare. To log waist and BMI together, see the {a("/blog/bmi-tracking-guide/", "BMI tracking guide")}.</p>
</section>

<section id="health-risks" class="content-section flow">
<h2>BMI and health risks for men</h2>
<p>NIH guidelines link a BMI above the healthy range with higher risk of high blood pressure, type 2 diabetes, coronary heart disease, stroke, sleep apnea and osteoarthritis ({a(NHLBI_GL, "NHLBI")}).</p>
<p>In a large trial of adults with overweight or obesity and type 2 diabetes, <strong>losing 5 to 10% of body weight</strong> was linked to improvements in cardiovascular risk factors within a year ({a(WING, "Wing et al., 2011")}).</p>
<p>A BMI under 18.5 can reflect undernutrition or an illness and is also worth checking with a doctor. The evidence behind each risk is in {a("/blog/bmi-and-health-risks/", "BMI and health risks")}.</p>
<h3>When to see a doctor</h3>
<ul>
<li>Your BMI is 30 or higher, or under 18.5.</li>
<li>Your waist is more than 40 inches (102 cm).</li>
<li>Your weight changes quickly without a clear reason.</li>
<li>You snore loudly, stop breathing or gasp in your sleep, or feel very sleepy during the day.</li>
<li>Heart disease, type 2 diabetes or stroke runs in your family.</li>
</ul>
</section>

<section id="situations" class="content-section flow">
<h2>Common situations</h2>
<h3>You lift weights and your BMI says overweight</h3>
<p>Muscle can push BMI past 25. Your waist and a body fat estimate from the {a("/body-fat-calculator/", "body fat calculator")} help show whether the extra weight is fat.</p>
<h3>You’re over 65</h3>
<p>The cut-offs stay the same, but at the same BMI older men tend to carry more fat (see the FAQ below). The {a("/age-bmi-calculator/", "BMI calculator by age")} adds US averages for your age group and the research on adults 65 and over.</p>
<h3>You use kilograms and centimetres</h3>
<p>Switch the calculator to Metric. Results then show kilograms first, pounds in brackets, and the healthy range in whole kilograms.</p>
<h3>You want the healthy weight for your exact height</h3>
<p>The {a("/blog/bmi-chart-men/", "BMI chart for men")} lists the healthy, overweight and obesity weights for every inch from 5′2″ to 6′6″.</p>
<h3>You’re tracking weight loss</h3>
<p>The what-if table shows your BMI at 5 lb (2.5 kg) steps, and the milestones table shows where each range starts at your height. Weigh at the same time of day; the {a("/blog/bmi-tracking-guide/", "tracking guide")} explains why.</p>
</section>

<section id="faq" class="content-section">
<h2>Frequently asked questions</h2>
<div class="faq-list flat">{faq_html()}</div>
</section>

<section id="sources" class="content-section flow">
<h2>Sources and method</h2>
<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from CDC’s public survey files with the method below.</p>
<ul class="source-list">
<li>CDC. {a(CDC_CAT, "Adult BMI Categories")}: the cut-offs used by the calculator and the tables.</li>
<li>Fryar CD, Afful J, Saif NT. {a(HESTAT, "NCHS Health E-Stat 111")} (Feb 2026): overweight, obesity and severe obesity in US men, August 2021–August 2023, age-adjusted.</li>
<li>CDC NCHS. {a(SR3, "Vital and Health Statistics Series 3, No. 50")}: average and median BMI of US men.</li>
<li>CDC {a(NHANES, "NHANES August 2021–August 2023")} exam files (DEMO_L, BMX_L): our calculation of averages by age, BMI percentiles and waist shares for men aged 20 and over ({S["bmi_n"]:,} with BMI, {S["waist_n"]:,} with waist), weighted with the exam weights.</li>
<li>CDC NHANES 2011–2018 DXA body scans: our analysis of body fat by BMI category, men aged 20 to 59 ({a("/body-fat-percentage-chart/", "body fat percentage chart")}).</li>
<li>NHLBI. {a(NHLBI_GL, "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")} (NIH, 1998) and {a(NHLBI, "Overweight and Obesity")}: waist cut-off, conditions linked to excess weight, measuring method.</li>
<li>WHO. Waist circumference and waist–hip ratio: report of a WHO expert consultation, Geneva, 2008.</li>
<li>Provencher MT, et al. {a(PROV, "Journal of Strength and Conditioning Research, 2018")}: BMI and body fat at the NFL Scouting Combine.</li>
<li>Wing RR, et al. {a(WING, "Diabetes Care, 2011")}: weight loss and cardiovascular risk factors after one year (Look AHEAD).</li>
<li>Winter JE, et al. {a(WINTER, "American Journal of Clinical Nutrition, 2014")}: BMI and mortality in adults 65 and over.</li>
<li>Gallagher D, et al. {a(GALLAGHER, "American Journal of Clinical Nutrition, 2000")}: provisional body fat ranges matched to BMI cut-offs, by age.</li>
</ul>
<p class="source-note"><strong>Method.</strong> BMI = weight (kg) ÷ height (m)², or lb × 703 ÷ in², rounded to one decimal; the category uses the rounded value. Healthy limits are the lightest and heaviest whole pounds (or kilograms) whose rounded BMI is 18.5 to 24.9. Percentiles come from the survey-weighted distribution of measured BMI with linear interpolation between values; the same method reproduces NCHS’s published medians (BMI 28.2 men, 28.3 women) and 95th-percentile weights (290.6 lb men, 262.7 lb women). Data: CDC NHANES August 2021–August 2023 and 2011–2018.</p>
</section>

<section class="content-section">
<h2>Related calculators and guides</h2>
<div class="related-cols">
<div><h3>Calculators</h3><ul>
<li><a href="/">BMI calculator for all adults</a></li>
<li><a href="/women-bmi-calculator/">BMI calculator for women</a></li>
<li><a href="/age-bmi-calculator/">BMI calculator by age</a></li>
<li><a href="/body-fat-calculator/">Body fat calculator</a></li>
<li><a href="/lean-body-mass/">Lean body mass calculator</a></li>
<li><a href="/ideal-weight/">Ideal weight calculator</a></li>
<li><a href="/calculators/">All calculators</a></li>
</ul></div>
<div><h3>Guides and data</h3><ul>
<li><a href="/blog/bmi-chart-men/">BMI chart for men</a></li>
<li><a href="/blog/bmi-for-athletes/">BMI for athletes</a></li>
<li><a href="/blog/body-fat-vs-bmi/">Body fat vs BMI</a></li>
<li><a href="/blog/how-to-measure-body-fat/">How to measure body fat</a></li>
<li><a href="/blog/bmi-and-health-risks/">BMI and health risks</a></li>
<li><a href="/average-weight/">Average weight for men</a></li>
</ul></div>
</div>
</section>
</div>
</main>'''

# ---------------------------------------------------------------- calculator card: keep inputs + results, add the rank block, drop the old takeaways
mi, mj = src.index('<main>'), src.index('</main>') + len('</main>')
old_main = src[mi:mj]
ci = old_main.index('<div class="calculator-card">')
ki = old_main.index('<div class="key-takeaways">')
calc = old_main[ci:ki]                           # card + panel + results, up to the old takeaways (still inside the panel)
m_anchor = re.search(r'<div class="weight-range-box"><p id="men-weight-diff"[^>]*>[^<]*</p></div>', calc)
assert m_anchor and len(re.findall(r'class="weight-range-box"', calc)) == 1
anchor = m_anchor.group(0)
RANK = ('<div class="rank-box" id="men-rank" hidden><div class="rank-title">Compared with US men aged 20 and over</div>'
        '<div class="rank-value" id="men-rank-value">—</div>'
        '<div class="rank-track" aria-hidden="true"><span class="rank-median"></span><span class="rank-marker" id="men-rank-marker"></span></div>'
        '<div class="rank-axis" aria-hidden="true"><span>Lowest BMI</span><span>Median {:.1f}</span><span>Highest</span></div>'
        '<p class="rank-text" id="men-rank-text"></p>'
        '<p class="rank-source">CDC NHANES 2021–2023, {:,} men measured; our calculation.</p></div>').format(T['p50'], S['bmi_n'])
calc = calc.replace(anchor, anchor + RANK)
# the card's open tags (card, panel, results) closed after the old takeaways; keep exactly that tag structure
tail = old_main[ki:]
kt_end = re.search(r'</ul>\s*</div>', tail).end()
after = tail[kt_end:]
closers = re.match(r'\s*((?:</div>\s*)+)', after).group(1)
calc_html = calc + re.sub(r'\s+', '', closers)
# byline/intro classes replace the old inline styles
new_main = MAIN.replace('@@CALCULATOR@@', calc_html)

def squash(h):
    h = re.sub(r'>\s*\n\s*<', '> <', h.strip())
    return re.sub(r'\n\s*', ' ', h)
new_main = squash(new_main)
src = src[:mi] + new_main + src[mj:]

# ---------------------------------------------------------------- head: descriptions + schema
def sub1(old, new):
    global src
    assert src.count(old) == 1, old[:80]
    src = src.replace(old, new)
DESC = f'Free BMI calculator for men. Get your BMI, the healthy weight for your height and how your BMI ranks among US men, from CDC data on {S["bmi_n"]:,} men.'
assert len(DESC) <= 160, len(DESC)
sub1(re.search(r'<meta name="description" content="[^"]*">', src).group(0), f'<meta name="description" content="{DESC}">')
sub1(re.search(r'<meta property="og:description" content="[^"]*">', src).group(0),
     '<meta property="og:description" content="Get your BMI, the healthy weight for your height and how you rank among US men (CDC data, 2021–2023).">')
sub1(re.search(r'<meta name="twitter:description" content="[^"]*">', src).group(0),
     '<meta name="twitter:description" content="Free BMI calculator for men: your BMI, the healthy weight for your height and how you rank among US men.">')
sub1(re.search(r'"description": "Calculates BMI for adult men[^"]*"', src).group(0),
     '"description": "Calculates BMI for adult men, the healthy weight range for their height (same CDC cut-offs as for women), how the result ranks among US men (CDC NHANES 2021-2023) and the NIH waist cut-off for men"')

blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', src, re.S))
faq_blocks = [b for b in blocks if '"FAQPage"' in b.group(1)]
assert len(faq_blocks) == 1
faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(ans)}} for q, ans in FAQ]}
b = faq_blocks[0]
src = src[:b.start(1)] + ' ' + json.dumps(faq_ld, ensure_ascii=False) + ' ' + src[b.end(1):]

OLD_OG = 'https://calculatemybmi.net/assets/images/og/men-waist-nhlbi-scale.png'
assert src.count(OLD_OG) == 2
src = src.replace(OLD_OG, 'https://calculatemybmi.net/assets/images/og/men-bmi-us-rank.png')
sub1('<meta property="og:image:height" content="630">',
     '<meta property="og:image:height" content="630"> <meta property="og:image:alt" content="BMI Calculator for Men: the average US man has a BMI of 29.4 (CDC, 2021–2023)">')

# ---------------------------------------------------------------- rank script (reads the BMI the calculator shows)
q_js = ','.join(f'{x:g}' for x in Q)
RANK_JS = ('<script>(function(){var Q=[' + q_js + '];var v=document.getElementById("men-bmi-value"),box=document.getElementById("men-rank");if(!v||!box)return;'
           'function pct(b){if(b<=Q[0])return 0;if(b>=Q[98])return 100;for(var i=0;i<98;i++){if(b<Q[i+1])return i+1+(b-Q[i])/(Q[i+1]-Q[i]);}return 100;}'
           'function show(){var b=parseFloat(v.textContent);if(!(b>0)){box.hidden=true;return;}var p=pct(b),r=Math.round(p),head,txt;'
           'if(p<1){head="Lower than 99% of US men";txt="Your BMI of "+b.toFixed(1)+" is lower than 99% of US men aged 20 and over.";}'
           'else if(p>99){head="Higher than 99% of US men";txt="Your BMI of "+b.toFixed(1)+" is higher than 99% of US men aged 20 and over.";}'
           'else{head="Higher than "+r+"% of US men";txt="Your BMI of "+b.toFixed(1)+" is higher than about "+r+"% of US men aged 20 and over and lower than about "+(100-r)+"%. The median US man has a BMI of ' + f'{T["p50"]:.1f}' + '.";}'
           'document.getElementById("men-rank-value").textContent=head;document.getElementById("men-rank-text").textContent=txt;'
           'document.getElementById("men-rank-marker").style.left=Math.min(99,Math.max(1,p))+"%";box.hidden=false;}'
           'new MutationObserver(show).observe(v,{childList:true,characterData:true,subtree:true});})();</script>')
sub1('</body>', RANK_JS + ' </body>')

open(PAGE, 'w', encoding='utf-8', newline='').write(src)

# ---------------------------------------------------------------- styles.css: link token + reusable content classes
CSS = os.path.join(ROOT, 'assets/css/styles.css')
css = open(CSS, encoding='utf-8', newline='').read()
def csub(old, new):
    global css
    assert css.count(old) == 1, old[:60]
    css = css.replace(old, new)
csub('  --secondary: #164e63;\n', '  --secondary: #164e63;\n  --link: #0e7490;             /* cyan-700: 5.4:1 on white, AA for text links (CMB-006) */\n')
csub('a { color: var(--primary-dark); text-decoration: none; }', 'a { color: var(--link); text-decoration: none; }')
csub('.unit-btn.active { background: white; color: var(--primary-dark); box-shadow: var(--shadow-md); }',
     '.unit-btn.active { background: white; color: var(--link); box-shadow: var(--shadow-md); }')
csub('.key-takeaways-title { font-weight: 600; color: var(--primary-dark); margin-bottom: 0.5rem; font-size: 0.9375rem; }',
     '.key-takeaways-title { font-weight: 600; color: var(--link); margin-bottom: 0.5rem; font-size: 0.9375rem; }')
css = css.rstrip('\n') + '\n' + open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pilot.css'), encoding='utf-8').read()
open(CSS, 'w', encoding='utf-8', newline='').write(css)

print('built: example BMI', EX_BMI, '| rank', EX_RANK, '| healthy', HB['minLb'], HB['maxLb'], '| desc', len(DESC), 'chars')
