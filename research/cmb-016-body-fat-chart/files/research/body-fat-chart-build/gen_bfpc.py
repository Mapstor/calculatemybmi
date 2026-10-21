#!/usr/bin/env python3
"""CMB-016 BODY-FAT-CHART — rebuilds /body-fat-percentage-chart/ to the D-14 guide pattern (DESIGN.md "Guide pages",
as /blog/bmi-chart-women/ and /bmi-chart/ applied it): intro, answer block and key takeaways, a hero figure, contents
chips, the chart as a real table plus a printable chart image, the rank tool, what every whole percentage means, the
provisional ranges and where they come from, body fat at each BMI, age and sex, a flat FAQ whose JSON-LD equals the
visible answers, sources and method, one related block, one 680 px reading column.

Wedge: what US adults actually measure on CDC's DXA scanner (NHANES 2011-2018, our calculation, which reproduces Liu
et al., BMJ 2021), set against the provisional ranges many charts use (Gallagher et al., 2000): the share above and
below every whole percentage, body fat at each BMI, and how the ranges' edges compare with CDC's scans at the same BMI.

Rounding: every printed figure is rounded once, from the unrounded estimate (bfpc_stats.py stores 4 decimals and checks
that this prints the same). The 2026-10-21 fact-check caught double rounding: men 50-59 at 28.4 (unrounded 28.347) and
four table shares one point high.

Images in search results (CMB-015 standard): a text-free preferred image (og:image, Article image in 1:1, 4:3 and 16:9,
WebPage primaryImageOfPage; research/preferred-images/pref_images.py), max-image-preview:large, and the printable chart
as an <img> listed in the image sitemap.

Every number on the page comes from bfpc_stats.json (bfpc_stats.py), the weight-table gate's own rule
(scripts/check_weight_tables.py) or a source verified in chat on 2026-10-04/14/21 (constants below, each with its
source; all listed in "Sources and method").

usage: python3 gen_bfpc.py REPO_ROOT STATS_JSON
Runs once, on body-fat-percentage-chart/index.html as it stood at 0c418db; kept as the build record. The page is
written with {TODAY} in its schema dateModified; apply_build.py puts in the apply date (manifest "today": true).
"""
import sys, os, re, json, html

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
PAGE = os.path.join(ROOT, 'body-fat-percentage-chart/index.html')
src = open(PAGE, encoding='utf-8').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds

SITE = 'https://calculatemybmi.net'
URL = SITE + '/body-fat-percentage-chart/'

# ---------------------------------------------------------------- numbers (our calculation, bfpc_stats.json)
BA, DIF, LK, BM = S['by_age'], S['diff'], S['lookup'], S['bmi']
GAL = {k: {g: tuple(v) for g, v in d.items()} for k, d in S['gallagher']['cuts'].items()}
META = S['meta']
assert (META['n_men_20_59'], META['n_women_20_59'], META['n_adults_20_59']) == (5402, 5462, 10864)
assert META['df'] == 62 and META['t975'] == 1.999
def f1(x): return f'{x:.1f}'
def mean(k, g): return f1(BA[k][g]['mean4'])                  # 'mean' is the 2-decimal record; printing it rounds twice
def qv(k, g, p): return f1(BA[k][g][p])
SEXN = {'f': 'women', 'm': 'men'}
SEXK = {'f': 'girls', 'm': 'boys'}
AVG_F, AVG_M = mean('f', '20-59'), mean('m', '20-59')
assert (AVG_F, AVG_M) == ('38.7', '27.2')
DEC = ('20-29', '30-39', '40-49', '50-59')
KIDS = ('8-11', '12-15', '16-19')
assert [mean('m', g) for g in DEC] == ['25.4', '27.4', '28.1', '28.3']          # the live page said 28.4 (28.35 rounded again)
assert [mean('f', g) for g in DEC] == ['36.9', '38.2', '39.2', '40.3']
assert [mean('m', g) for g in KIDS] == ['29.2', '26.1', '23.4'] and [mean('f', g) for g in KIDS] == ['32.5', '33.5', '35.3']
# Differences stated on the page: each 95% CI excludes 0 (NHANES comparison rule).
WM = DIF['women_minus_men']
assert all(WM[g]['excludes_0'] for g in DEC + ('20-59',)) and WM['20-59']['diff'] == 11.5
WM_LO, WM_HI = min(WM[g]['diff'] for g in DEC), max(WM[g]['diff'] for g in DEC)
assert (WM_LO, WM_HI) == (10.8, 12.0)
AGE_M, AGE_F = DIF['age']['m']['50s_minus_20s'], DIF['age']['f']['50s_minus_20s']
assert AGE_M['excludes_0'] and AGE_F['excludes_0'] and (AGE_M['diff'], AGE_F['diff']) == (2.9, 3.4)
KID_M, KID_F = DIF['age']['m']['16_19_minus_8_11'], DIF['age']['f']['16_19_minus_8_11']
assert KID_M['excludes_0'] and KID_F['excludes_0'] and (KID_M['diff'], KID_F['diff']) == (-5.8, 2.8)

def more(k, g, p): return LK[k][g][str(p)]['more']
def less(k, g, p): return LK[k][g][str(p)]['less']
def le(k, g, p): return LK[k][g][str(p)]['at_or_below']
def share_txt(v):
    """A share of US adults, with the tails written out: rounding must not print 100% or 0%. Halves round up, as the
    rank tool's Math.round does, so a table and the tool never differ by one."""
    if v >= 99.5: return 'more than 99%'
    if v <= 0.5: return 'under 1%'
    return f'{int(v + 0.5)}%'
def cat(k, g, p):
    a, b, c = GAL[k][g]
    return 'low' if p < a else 'healthy' if p < b else 'high' if p < c else 'very high'
TINT = {'low': 'under', 'healthy': 'healthy', 'high': 'over', 'very high': 'ob2'}
def rng(k, g, which):
    a, b, c = GAL[k][g]
    return {'low': f'under {a}%', 'healthy': f'{a}–{b - 0.1:.1f}%', 'high': f'{b}–{c - 0.1:.1f}%', 'very high': f'{c}% or more'}[which]
assert rng('f', '20-39', 'healthy') == '21–32.9%' and rng('m', '20-39', 'healthy') == '8–19.9%'

# Body fat by BMI (adults 20-59).
BC = BM['by_cat']
def mid(k, c): return f'{f1(BC[k][c]["p25"])}–{f1(BC[k][c]["p75"])}%'
assert mid('f', 'healthy') == '29.8–36.5%' and mid('m', 'healthy') == '18.6–25.0%'
assert (f1(BC['f']['healthy']['p50']), f1(BC['m']['healthy']['p50'])) == ('33.4', '22.1')
BIN = BM['by_bin']
# The women-minus-men gap in median body fat at each BMI 19-30, printed in whole points. Readings are recorded to 0.1%,
# so how tied readings are ordered moves a bin's median by up to about 0.1: the fact-check's own build put the range at
# 10.9-13.0, an order-free method (one weight per distinct reading) at 11.1-13.2, this build at 10.9-13.1. Whole points
# read the same under all three; the assert keeps both ends at least 0.25 from a rounding edge.
_gap = [BIN['f'][str(b)]['p50'] - BIN['m'][str(b)]['p50'] for b in range(19, 31)]
_lo, _hi = min(_gap), max(_gap)
assert all(abs(x - int(x) - 0.5) >= 0.25 for x in (_lo, _hi)), (_lo, _hi)
GAP_LO, GAP_HI = int(_lo + 0.5), int(_hi + 0.5)
assert (GAP_LO, GAP_HI) == (11, 13)
AT = BM['at_lines']
def at(k, line, g): return f1(AT[k][line][g]['mean'])
assert (at('m', '25', '20-39'), at('f', '25', '20-39'), at('m', '25', '40-59'), at('f', '25', '40-59')) == ('24.3', '35.6', '26.5', '37.6')
assert all(AT[k]['25'][g]['n'] >= 100 for k in 'mf' for g in ('20-39', '40-59'))
HB = BM['healthy_bmi_above']
HB_M, HB_F = HB['m']['above_healthy']['pct'], HB['f']['above_healthy']['pct']
assert (HB_M, HB_F) == (60.6, 49.1)
# Worked example (PAA "Is 140 pounds fat for a 5'4" female?"): BMI = 140 x 703 / 64^2 = 24.03.
EX = S['example_5_4_140']
assert EX['bmi'] == 24.0 and EX['n'] == 285
EX_MED, EX_LO, EX_HI = f1(EX['p50']), f1(EX['p25']), f1(EX['p75'])
assert (EX_MED, EX_LO, EX_HI) == ('35.5', '33.0', '38.2')
assert bounds('lb', 64, 64 * 2.54, 1) == (108, 145)                     # healthy weight at 5'4" (the women's chart)
# Tails (FAQ "lowest body fat a woman can have").
F_P1, F_P5 = qv('f', '20-59', 'p1'), qv('f', '20-59', 'p5')
assert (F_P1, F_P5) == ('23.3', '27.2')

# ---------------------------------------------------------------- sources verified in chat
# CDC NHANES DXA documentation (DXX_J, read 2026-10-21): "Participants aged 8-59 years were eligible"; pregnancy,
# barium in the past 7 days and "Self-reported weight over 450 pounds or height over 6'5" (DXA table limitation)" exclude;
# "The percentage of participants with 100% valid data also decreases with increasing BMI"; "The NHANES BCA option was
# enabled for whole body scan analysis, this option adds 5% of lean mass to the fat mass".
# Gallagher et al. 2000 (PubMed abstract, read 2026-10-21): 1,626 adults with a BMI of 35 or less; white, African American
# and Asian; Cambridge (UK), Columbia (US) and Jikei (Japan); four-compartment model at 2 labs and DXA at all 3; predictors
# 1/BMI, sex, age and ethnic group; "provisional healthy percentage body fat ranges" from the BMI limits 18.5, 25 and 30.
# The cut-offs as tabulated in J Public Health Afr 2016;7:515, Table 1 (registry gallagher-2000-bf-ranges, 2026-10-04).
# CDC About BMI (registry cdc-about-bmi): "BMI does not distinguish between fat, muscle, and bone mass".
# Liu et al., BMJ 2021;372:n365: our pooled method reproduces its Table 3 mean body fat for every cycle (registry).
# Burns, Fu & Constantino, PLOS ONE 2019 (registry body-fat-method-validation, read 2026-10-07): 437 college students;
# against DXA, the hand-held impedance device (Omron) differed by 4.9 points on average.

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'liu': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7961695/',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'jpha': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5349253/table/table001',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
}
GAL_CITE = ext(U['gallagher'], 'Gallagher et al., 2000')
CSV = '/body-fat-percentage-chart/body-fat-percentiles-nhanes-2011-2018.csv'

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS = [], []          # estimated boxes: (svg, x0, y0, x1, y1, label, inside) ; (svg, x0, y0, x1, y1, rid)
VBW = {}

def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827', inside=None):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s, inside))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'

def rect(svg, x, y, w, h, fill, rid=None, extra='', tip=None):
    RECTS.append((svg, x, y, x + w, y + h, rid))
    t = f'<title>{esc(tip)}</title>' if tip else ''
    if t:
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}>{t}</rect>'
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>'

# The site's base category colours (DESIGN.md category lock); the provisional ranges sit on the same BMI lines.
BASE = {'under': '#3b82f6', 'healthy': '#22c55e', 'over': '#f59e0b', 'obese': '#ef4444'}
CATS4 = (('low', 'under', 'Low'), ('healthy', 'healthy', 'Healthy'), ('high', 'over', 'High'), ('very high', 'obese', 'Very high'))
# Women and men as series (dataviz validator, light mode: CVD dE 18.3, normal-vision dE 29.3, both >= 3:1 on white).
SER = {'f': '#be185d', 'm': '#4338ca'}
INK, MUTED, GRID = '#1f2937', '#4b5563', '#e5e7eb'

def legend_row(svg, x0, y, items, gap=14):
    """One row of swatch + label pairs; items = (kind, colour, label)."""
    out, x = [], x0
    for kind, col, lab in items:
        if kind == 'box':
            out.append(rect(svg, x, y - 10, 10, 10, col, rid='swatch', extra=' rx="2"'))
            tx = x + 14
        else:                                                    # a line swatch for a series
            RECTS.append((svg, x, y - 6, x + 16, y - 3, 'swatch'))
            out.append(f'<line x1="{x}" y1="{y - 4.5}" x2="{x + 16}" y2="{y - 4.5}" stroke="{col}" stroke-width="2.5"/>')
            tx = x + 20
        out.append(text(svg, tx, y, lab, 12, anchor='start', fill=INK))
        x = tx + len(lab) * 12 * 0.55 + gap
    return ''.join(out), x

# ---------------------------------------------------------------- hero: the provisional ranges by age and sex
HW, HX0, HX1 = 320, 52, 312
def hx(p): return HX0 + p * (HX1 - HX0) / 50.0
VBW['hero'] = HW
hero = []
leg, _ = legend_row('hero', 0, 14, [('box', BASE[c], lab) for _, c, lab in CATS4], gap=12)
hero.append(leg)
y = 42
for k, label in (('f', 'Women'), ('m', 'Men')):
    hero.append(text('hero', 0, y, label, 13, anchor='start', weight=600, fill=INK))
    y += 8
    for g in ('20-39', '40-59', '60-79'):
        a, b, c = GAL[k][g]
        edges = [0, a, b, c, 50]
        for i, (key, colk, lab) in enumerate(CATS4):
            x0, x1 = hx(edges[i]) + (1 if i else 0), hx(edges[i + 1]) - (1 if i < 3 else 0)
            tip = f'{label} {g.replace("-", "–")}: {lab.lower()}, {rng(k, g, key)}'
            hero.append(rect('hero', x0, y, x1 - x0, 16, BASE[colk], rid=f'band-{k}-{g}', extra=' rx="3"', tip=tip))
        hero.append(text('hero', 0, y + 12, g.replace('-', '–'), 12, anchor='start', fill=INK))
        for v in (a, b, c):
            hero.append(text('hero', hx(v), y + 29, f'{v}', 12, fill=MUTED))
        y += 38
    y += 14
HH = y - 18                                                      # last cut-off labels end 3 px above
svg_hero = (f'<svg viewBox="0 0 {HW} {HH}" role="img" aria-labelledby="hero-t hero-d" xmlns="http://www.w3.org/2000/svg" '
            'font-family="inherit"><title id="hero-t">Body fat percentage chart for women and men by age</title>'
            '<desc id="hero-d">Provisional body fat ranges matched to BMI 18.5, 25 and 30 (Gallagher et al., 2000). '
            + ' '.join(f'{SEXN[k].capitalize()} {g.replace("-", " to ")}: low under {GAL[k][g][0]}%, healthy {rng(k, g, "healthy")}, '
                       f'high {rng(k, g, "high")}, very high {GAL[k][g][2]}% or more.'
                       for k in ('f', 'm') for g in ('20-39', '40-59', '60-79'))
            + '</desc>' + ''.join(hero) + '</svg>')

# ---------------------------------------------------------------- figure: body fat at each BMI (women and men, 20-59)
BW_, BX0, BX1, BY0, BY1 = 320, 36, 268, 34, 206
def bx(b): return BX0 + (b - 18) * (BX1 - BX0) / 22.0
def by(p): return BY1 - (p - 10) * (BY1 - BY0) / 40.0
VBW['bmi'] = BW_
fig_b = []
leg, _ = legend_row('bmi', 0, 14, [('line', SER['f'], 'Women'), ('line', SER['m'], 'Men'), ('box', '#d1d5db', 'Middle half')])
fig_b.append(leg)
for p in (10, 20, 30, 40, 50):
    fig_b.append(f'<line x1="{BX0}" y1="{by(p):.1f}" x2="{BX1}" y2="{by(p):.1f}" stroke="{GRID}" stroke-width="1"/>')
    fig_b.append(text('bmi', BX0 - 5, by(p) + 4, f'{p}%', 12, anchor='end', fill=MUTED))
for b in (18.5, 25, 30):
    fig_b.append(f'<line x1="{bx(b):.1f}" y1="{BY0 - 4}" x2="{bx(b):.1f}" y2="{BY1}" stroke="#9ca3af" stroke-width="1" '
                 'stroke-dasharray="3 3"/>')
for b in (18.5, 25, 30, 35, 40):
    fig_b.append(text('bmi', bx(b), BY1 + 21, f'{b:g}', 12, fill=MUTED))
fig_b.append(text('bmi', (BX0 + BX1) / 2, BY1 + 38, 'BMI, adults aged 20 to 59', 12, fill=INK))
ENDS = {}
for k in ('f', 'm'):
    pts = [(int(b) + 0.5, v) for b, v in BIN[k].items() if 18 <= int(b) <= 39 and v.get('n', 0) >= 50]
    assert len(pts) >= 21, (k, len(pts))
    up = ' '.join(f'{bx(b):.1f},{by(v["p75"]):.1f}' for b, v in pts)
    dn = ' '.join(f'{bx(b):.1f},{by(v["p25"]):.1f}' for b, v in pts[::-1])
    fig_b.append(f'<polygon points="{up} {dn}" fill="{SER[k]}" fill-opacity="0.16"><title>{SEXN[k].capitalize()}: middle half of '
                 f'body fat at each BMI</title></polygon>')
    fig_b.append('<polyline points="' + ' '.join(f'{bx(b):.1f},{by(v["p50"]):.1f}' for b, v in pts)
                 + f'" fill="none" stroke="{SER[k]}" stroke-width="2"><title>{SEXN[k].capitalize()}: median body fat at each BMI'
                 '</title></polyline>')
    for b, v in pts:
        fig_b.append(f'<circle cx="{bx(b):.1f}" cy="{by(v["p50"]):.1f}" r="5" fill="transparent"><title>{SEXN[k].capitalize()}, '
                     f'BMI {int(b)} to {int(b)}.9: median {f1(v["p50"])}%, middle half {f1(v["p25"])}–{f1(v["p75"])}% '
                     f'({v["n"]:,} scanned)</title></circle>')
    ENDS[k] = (bx(pts[-1][0]), by(pts[-1][1]['p50']))
for k in ('f', 'm'):
    fig_b.append(text('bmi', BX1 + 6, ENDS[k][1] + 4, SEXN[k].capitalize(), 12, anchor='start', fill=INK))
BH = BY1 + 46
svg_bmi = (f'<svg viewBox="0 0 {BW_} {BH}" role="img" aria-labelledby="bmi-t bmi-d" xmlns="http://www.w3.org/2000/svg" '
           'font-family="inherit"><title id="bmi-t">Body fat at each BMI, US women and men aged 20 to 59</title>'
           f'<desc id="bmi-d">Median body fat and the middle half at each whole BMI from 18 to 39, from CDC body scans '
           f'2011 to 2018. At every BMI from 19 to 30 the median woman measured about {GAP_LO} to {GAP_HI} points more body fat '
           'than the median man.</desc>' + ''.join(fig_b) + '</svg>')

# ---------------------------------------------------------------- figure: body fat by age (8 to 59)
AW, AX0, AX1, AY0, AY1 = 320, 36, 268, 46, 196
AGES = KIDS + DEC
def ax(i): return AX0 + i * (AX1 - AX0) / (len(AGES) - 1)
def ay(p): return AY1 - (p - 10) * (AY1 - AY0) / 40.0
VBW['age'] = AW
fig_a = []
leg, _ = legend_row('age', 0, 14, [('line', SER['f'], 'Female'), ('line', SER['m'], 'Male'), ('box', '#d1d5db', 'Middle half')])
fig_a.append(leg)
for p in (10, 20, 30, 40, 50):
    fig_a.append(f'<line x1="{AX0}" y1="{ay(p):.1f}" x2="{AX1}" y2="{ay(p):.1f}" stroke="{GRID}" stroke-width="1"/>')
    fig_a.append(text('age', AX0 - 5, ay(p) + 4, f'{p}%', 12, anchor='end', fill=MUTED))
xdiv = (ax(2) + ax(3)) / 2
fig_a.append(f'<line x1="{xdiv:.1f}" y1="{AY0 - 12}" x2="{xdiv:.1f}" y2="{AY1}" stroke="#9ca3af" stroke-width="1" stroke-dasharray="3 3"/>')
fig_a.append(text('age', (AX0 + xdiv) / 2, AY0 - 16, 'Under 20', 12, fill=MUTED))
fig_a.append(text('age', (xdiv + AX1) / 2, AY0 - 16, 'Adults', 12, fill=MUTED))
for i, g in enumerate(AGES):
    fig_a.append(text('age', ax(i), AY1 + 21, g.replace('-', '–'), 12, fill=MUTED))
fig_a.append(text('age', (AX0 + AX1) / 2, AY1 + 38, 'Age, years', 12, fill=INK))
AENDS = {}
for k in ('f', 'm'):
    up = ' '.join(f'{ax(i):.1f},{ay(BA[k][g]["p75"]):.1f}' for i, g in enumerate(AGES))
    dn = ' '.join(f'{ax(i):.1f},{ay(BA[k][g]["p25"]):.1f}' for i, g in list(enumerate(AGES))[::-1])
    fig_a.append(f'<polygon points="{up} {dn}" fill="{SER[k]}" fill-opacity="0.16"><title>{"Girls and women" if k == "f" else "Boys and men"}: '
                 'middle half of body fat by age</title></polygon>')
    fig_a.append('<polyline points="' + ' '.join(f'{ax(i):.1f},{ay(BA[k][g]["p50"]):.1f}' for i, g in enumerate(AGES))
                 + f'" fill="none" stroke="{SER[k]}" stroke-width="2"/>')
    for i, g in enumerate(AGES):
        fig_a.append(f'<circle cx="{ax(i):.1f}" cy="{ay(BA[k][g]["p50"]):.1f}" r="4" fill="{SER[k]}" stroke="#ffffff" stroke-width="2">'
                     f'<title>{"Female" if k == "f" else "Male"}, {g.replace("-", "–")}: median {qv(k, g, "p50")}%, middle half '
                     f'{qv(k, g, "p25")}–{qv(k, g, "p75")}% ({BA[k][g]["n"]:,} scanned)</title></circle>')
    AENDS[k] = ay(BA[k]['50-59']['p50'])
for k, lab in (('f', 'Women'), ('m', 'Men')):
    fig_a.append(text('age', AX1 + 8, AENDS[k] + 4, lab, 12, anchor='start', fill=INK))
AH = AY1 + 46
svg_age = (f'<svg viewBox="0 0 {AW} {AH}" role="img" aria-labelledby="age-t age-d" xmlns="http://www.w3.org/2000/svg" '
           'font-family="inherit"><title id="age-t">Body fat by age, US females and males aged 8 to 59</title>'
           f'<desc id="age-d">Median body fat and the middle half by age group from CDC body scans 2011 to 2018. Boys: median '
           f'{qv("m", "8-11", "p50")}% at 8 to 11, {qv("m", "16-19", "p50")}% at 16 to 19. Girls: {qv("f", "8-11", "p50")}% and '
           f'{qv("f", "16-19", "p50")}%. Men rise from {qv("m", "20-29", "p50")}% in their 20s to {qv("m", "50-59", "p50")}% in '
           f'their 50s; women from {qv("f", "20-29", "p50")}% to {qv("f", "50-59", "p50")}%.</desc>' + ''.join(fig_a) + '</svg>')

# Collision check on the estimated boxes (the rendered check runs in bfpc_test_playwright.py): no text over text, no text
# over a shape unless it is the label that shape holds, nothing outside the viewBox.
def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r) and a[6] != r[5]:
            raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r} / {r[5]!r}')
for svg, x0, y0, x1, y1, s, _ in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in the owner's US/English pastes of 2026-10-21, not personalised ("body fat percentage chart", "body
# fat index", "body fat percentage women"), in that order, each question once; photo and attractiveness questions left
# out (no pictures and no opinions on this page). Then the ledger's "average fat percentage" (3,600/mo) and the old
# page's 60-and-over question.
M30_LESS, M30_MORE = less('m', '20-39', 30), more('m', '20-39', 30)
FAQ = [
    ('What is a good body fat percentage by age?',
     'Widely cited ranges are provisional ones matched to a healthy BMI '
     f'({GAL_CITE}): for women, <strong>{rng("f", "20-39", "healthy")} at ages 20 to 39</strong>, '
     f'{rng("f", "40-59", "healthy")} at 40 to 59 and {rng("f", "60-79", "healthy")} at 60 to 79; for men, '
     f'<strong>{rng("m", "20-39", "healthy")} at 20 to 39</strong>, {rng("m", "40-59", "healthy")} at 40 to 59 and '
     f'{rng("m", "60-79", "healthy")} at 60 to 79. What US adults measure is higher: an average of {AVG_F}% for women and '
     f'{AVG_M}% for men aged 20 to 59 (our calculation from CDC body scans, 2011–2018).'),
    ('What is the lowest body fat a woman can have?',
     f'CDC’s scans show how low US women measure: of {META["n_women_20_59"]:,} women aged 20 to 59, 1 in 100 measured under '
     f'{F_P1}% body fat and 1 in 20 under {F_P5}% (our calculation, 2011–2018). On the provisional ranges, body fat under '
     f'{GAL["f"]["20-39"][0]}% at ages 20 '
     f'to 39 (under {GAL["f"]["40-59"][0]}% at 40 to 59) is “low”: the level that goes with an underweight BMI ({GAL_CITE}).'),
    ('Is 30% body fat chubby?',
     f'It depends on sex. For a woman, 30% is inside the provisional healthy range at 20 to 39 ({rng("f", "20-39", "healthy")}), '
     f'and {share_txt(more("f", "20-39", 30))} of US women that age measured more. For a man, 30% is above the range at every '
     f'age: “very high” starts at {GAL["m"]["20-39"][2]}% at 20 to 39, {GAL["m"]["40-59"][2]}% at 40 to 59 and '
     f'{GAL["m"]["60-79"][2]}% at 60 to 79 ({GAL_CITE}). Still, {share_txt(M30_MORE)} of US men aged 20 to 39 measured more '
     'than 30% (our calculation from CDC body scans).'),
    ('Is 20% body fat skinny?',
     f'Not for a man: 20% is the start of the provisional “high” range at 20 to 39 and inside the healthy range at 40 to 59 '
     f'({rng("m", "40-59", "healthy")}), and {share_txt(more("m", "20-39", 20))} of US men aged 20 to 39 measured more. For a '
     f'woman, 20% is under the provisional healthy range (it starts at {GAL["f"]["20-39"][0]}% at 20 to 39), and '
     f'{share_txt(more("f", "20-39", 20))} of US women aged 20 to 39 measured more (our calculation from CDC body scans).'),
    ('What’s a good body fat index?',
     '“Body fat index” isn’t one fixed measure. If you mean body fat percentage, the share of body weight that is fat, the '
     f'provisional healthy ranges are {rng("f", "20-39", "healthy")} for women and {rng("m", "20-39", "healthy")} for men aged 20 '
     f'to 39, a little higher with age ({GAL_CITE}). If you mean the body mass index (BMI), weight divided by height squared, '
     f'the healthy range is 18.5 to 24.9 ({ext(U["cdc_cat"], "CDC")}). There is also a fat mass index: fat mass in kilograms '
     'divided by height in meters squared.'),
    ('Is 20% body fat realistic?',
     f'For men, yes: {f1(le("m", "20-39", 20))}% of US men aged 20 to 39 measured 20% or less in CDC’s scans. For women it is '
     f'rare: {f1(le("f", "20-39", 20))}% of women aged 20 to 39 measured 20% or less (our calculation, 2011–2018).'),
    ('Is 18% body fat chubby?',
     f'No. For a man, 18% is inside the provisional healthy range at every age from 20 to 79, and '
     f'{share_txt(more("m", "20-39", 18))} of US men aged 20 to 39 measured more. For a woman, 18% is under the provisional '
     f'healthy range; only {f1(le("f", "20-39", 18))}% of US women aged 20 to 39 measured 18% or less (our calculation from '
     'CDC body scans).'),
    ('Is 140 pounds fat for a 5′4″ female?',
     f'Not by BMI. At 5′4″, 140 lb is a BMI of {EX["bmi"]}, inside CDC’s healthy range of 18.5 to 24.9; the healthy weight at that '
     f'height runs up to 145 lb ({ext(U["cdc_cat"], "CDC")} categories). Body fat varies a lot at the same BMI: US women aged '
     f'20 to 59 with a BMI of 23.5 to 24.4 measured a median {EX_MED}% body fat, and the middle half were between {EX_LO}% and '
     f'{EX_HI}% (our calculation from CDC body scans, 2011–2018).'),
    ('What is the average body fat percentage?',
     f'<strong>{AVG_F}% for US women and {AVG_M}% for US men</strong> aged 20 to 59, measured with DXA scans in CDC’s 2011–2018 '
     f'surveys (our calculation). By age it runs from {mean("f", "20-29")}% for women in their 20s to {mean("f", "50-59")}% in '
     f'their 50s, and from {mean("m", "20-29")}% to {mean("m", "50-59")}% for men.'),
    ('Why is there no data for people over 60?',
     f'CDC’s whole-body DXA scans in 2011–2018 covered ages 8 to 59 only ({ext(U["dxx"], "CDC")}). For ages 60 to 79 the chart '
     'shows the provisional ranges, not US measurements.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
H1 = 'Body Fat Percentage Chart for Women and Men by Age'
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">What body fat percentage is healthy for a woman or a man your age? Is 30% a lot? And how does '
    'body fat line up with BMI?</p>'
    '<p class="intro-text">CDC’s adult categories use BMI, not body fat, and the body fat ranges many charts use are '
    'provisional. CDC’s body scans show what Americans actually measure: an average of '
    f'{AVG_F}% body fat for women and {AVG_M}% for men aged 20 to 59 (our calculation, 2011–2018).</p>'
    '<p class="intro-text">Below: <a href="#chart">the chart by age</a> for women and men, <a href="#rank">where your number '
    'ranks</a>, what every percentage means against US adults, and body fat at each BMI.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>Widely cited healthy body fat ranges are '
    f'{rng("f", "20-39", "healthy")} for women and {rng("m", "20-39", "healthy")} for men aged 20 to 39</strong>, a few '
    f'points higher at older ages. They are provisional ranges matched to a healthy BMI ({GAL_CITE}). US adults measure more '
    f'on CDC’s scanner: an average of {AVG_F}% for women and {AVG_M}% for men aged 20 to 59.</p><ul>'
    f'<li><strong>Women measure about {WM["20-59"]["diff"]} points more than men</strong> on average, and {WM_LO} to {WM_HI} '
    'points more in every decade from 20 to 59 (our calculation from CDC body scans).</li>'
    f'<li><strong>Body fat rises with age:</strong> the average goes up {AGE_M["diff"]} points for men and {AGE_F["diff"]} for '
    'women from their 20s to their 50s.</li>'
    '<li><strong>BMI is not a body fat reading:</strong> among US women with a healthy BMI, the middle half measured '
    f'{mid("f", "healthy")} body fat; among men, {mid("m", "healthy")}.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This page is for information only. Body fat '
    'percentage and BMI are measurements, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>Provisional body fat ranges by age, matched to BMI 18.5, 25 and 30 '
            f'({GAL_CITE}). Green is the range that goes with a healthy BMI. The numbers are the body fat percentages where each range '
            'starts; each bar runs from 0 to 50%.</figcaption></figure>')

CHIPS = (('chart', 'Chart'), ('rank', 'Your rank'), ('every-percent', 'Every %'), ('healthy', 'Healthy range'),
         ('bmi', 'Body fat and BMI'), ('age-sex', 'Age and sex'), ('printable', 'Printable'), ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

# --- the chart (provisional ranges with the US median)
def chart_row(k, g):
    a, b, c = GAL[k][g]
    med = f'{qv(k, g, "p50")}%' if g in BA[k] else 'not scanned'
    cells = ''.join(f'<td class="c-{TINT[key]}">{rng(k, g, key)}</td>' for key, _, _ in CATS4)
    return (f'<tr id="{SEXN[k]}-{g}"><th scope="row">{SEXN[k].capitalize()} <span class="nw">{g.replace("-", "–")}</span></th>'
            f'{cells}<td>{med}</td></tr>')
CHART_ROWS = [(k, g) for k in ('f', 'm') for g in ('20-39', '40-59', '60-79')]
chart_head = ('<thead><tr><th scope="col">Sex and age</th>'
              + ''.join(f'<th scope="col">{lab}<span class="th-sub">BMI <span class="nw">{sub}</span></span></th>'
                        for (_, _, lab), sub in zip(CATS4, ('under 18.5', '18.5–24.9', '25–29.9', '30 or more')))
              + '<th scope="col">US median<span class="th-sub">CDC scans</span></th></tr></thead>')
CHART_IMG = '/assets/images/charts/body-fat-percentage-chart.png'
CHART_W, CHART_H = 1360, 902                                     # written by chart_bfpc.py
_png = os.path.join(ROOT, CHART_IMG.lstrip('/'))
if os.path.exists(_png):
    from PIL import Image
    assert Image.open(_png).size == (CHART_W, CHART_H), Image.open(_png).size
sec_chart = (
    '<section id="chart" class="content-section flow"><h2>Body fat percentage chart by age</h2>'
    '<p>Find your sex and age group, then the column that holds your body fat percentage. The ranges come from a study that '
    'worked out the body fat that goes with a BMI of 18.5, 25 and 30, by sex and age; its authors called them provisional '
    f'({GAL_CITE}). The last column is the median CDC measured in US adults of that sex and age.</p>'
    f'<div class="table-responsive"><table class="weight-chart"><caption>Provisional ranges by sex and age</caption>{chart_head}<tbody>'
    + ''.join(chart_row(k, g) for k, g in CHART_ROWS) + '</tbody></table></div>'
    f'<p class="source-note">Ranges: {GAL_CITE}, as tabulated in {ext(U["jpha"], "J Public Health Afr 2016, Table 1")}; the '
    'original study gives different values for each of its three ethnic groups. US median: our calculation from CDC NHANES '
    '2011–2018 DXA scans, which covered ages 8 to 59. The ranges came from other scanners and equations, so the two don’t line up '
    '(see <a href="#bmi">body fat and BMI</a>). Each row has its own link, for example #women-20-39.</p>'
    '</section>')

# --- the rank tool (data from bfpc_stats.json; the page interpolates between whole percents)
TOOL = {'p0': S['tool']['percents'][0], 'more': S['tool']['more'],
        # percentiles as the page's tables print them (1 decimal), so the tool's toFixed(1) can't round a second time
        'q': {k: {g: [float(qv(k, g, p)) for p in ('p10', 'p25', 'p50', 'p75', 'p90')] for g in KIDS + DEC} for k in 'fm'},
        'n': {k: {g: BA[k][g]['n'] for g in KIDS + DEC} for k in 'fm'},
        'gal': {k: {g: list(v) for g, v in GAL[k].items()} for k in 'fm'}}
TOOL_JS = r'''(function(){var D=window.BFR,$=function(i){return document.getElementById(i);};
var sex='f',btns=document.querySelectorAll('#bfr .unit-btn'),out=$('bfr-out');
var BASE={low:'#3b82f6',healthy:'#22c55e',high:'#f59e0b','very high':'#ef4444'},SER={f:'#be185d',m:'#4338ca'};
var CARD={low:'underweight',healthy:'normal',high:'overweight','very high':'obese'},DOT=CARD;
function nd(s){return s.replace('-','–');}
function grp(a){return a<=11?'8-11':a<=15?'12-15':a<=19?'16-19':a<=29?'20-29':a<=39?'30-39':a<=49?'40-49':a<=59?'50-59':null;}
function ggrp(a){return a>=20&&a<=39?'20-39':a>=40&&a<=59?'40-59':a>=60&&a<=79?'60-79':null;}
function moreAt(arr,v){var i=Math.floor(v)-D.p0,f=v-Math.floor(v);if(i<0)return arr[0];if(i>=arr.length-1)return arr[arr.length-1];return arr[i]+(arr[i+1]-arr[i])*f;}
function shareTxt(x){return x>=99.5?'more than 99%':x<=0.5?'under 1%':Math.round(x)+'%';}
function cat(v,c){return v<c[0]?'low':v<c[1]?'healthy':v<c[2]?'high':'very high';}
function rangeTxt(c,k){return k==='low'?'under '+c[0]+'%':k==='healthy'?c[0]+'–'+(c[1]-0.1).toFixed(1)+'%':k==='high'?c[1]+'–'+(c[2]-0.1).toFixed(1)+'%':c[2]+'% or more';}
function word(s,a){return a<20?(s==='f'?'girls':'boys'):(s==='f'?'women':'men');}
function fig(v,q,c,s){var W=280,P=14,qa=q||[v,v,v,v,v],lo=Math.min(10,Math.floor(Math.min(qa[0],v)/5)*5),hi=Math.max(50,Math.ceil(Math.max(qa[4],v)/5)*5),
 X=function(x){return P+(x-lo)*(W-2*P)/(hi-lo);},g='',t,lx;
 if(q){g+='<rect x="'+X(q[0]).toFixed(1)+'" y="24" width="'+(X(q[4])-X(q[0])).toFixed(1)+'" height="18" rx="3" fill="'+SER[s]+'" fill-opacity="0.18"/>';
  g+='<rect x="'+X(q[1]).toFixed(1)+'" y="24" width="'+(X(q[3])-X(q[1])).toFixed(1)+'" height="18" rx="3" fill="'+SER[s]+'" fill-opacity="0.45"/>';
  g+='<line x1="'+X(q[2]).toFixed(1)+'" y1="21" x2="'+X(q[2]).toFixed(1)+'" y2="45" stroke="#111827" stroke-width="2"/>';}
 if(c){var e=[lo,c[0],c[1],c[2],hi],ks=['low','healthy','high','very high'];for(var i=0;i<4;i++){var a=Math.max(e[i],lo),b=Math.min(e[i+1],hi);if(b>a)g+='<rect x="'+(X(a)+(i?1:0)).toFixed(1)+'" y="52" width="'+(X(b)-X(a)-(i&&i<3?2:1)).toFixed(1)+'" height="8" rx="2" fill="'+BASE[ks[i]]+'"/>';}}
 g+='<line x1="'+X(v).toFixed(1)+'" y1="16" x2="'+X(v).toFixed(1)+'" y2="'+(c?64:48)+'" stroke="#111827" stroke-width="2" stroke-dasharray="3 2"/>';
 t='You '+(Math.round(v*10)/10)+'%';lx=Math.min(Math.max(X(v),t.length*3.6+2),W-t.length*3.6-2);
 g+='<text x="'+lx.toFixed(1)+'" y="11" font-size="12" text-anchor="middle" fill="#1f2937">'+t+'</text>';
 for(var x=lo;x<=hi;x+=10)g+='<text x="'+X(x).toFixed(1)+'" y="80" font-size="12" text-anchor="middle" fill="#4b5563">'+x+'%</text>';
 return '<svg viewBox="0 0 '+W+' 86" role="img" aria-label="Your reading of '+v+'% on a scale from '+lo+'% to '+hi+'%" xmlns="http://www.w3.org/2000/svg" font-family="inherit">'+g+'</svg>';}
function show(){var v=parseFloat($('bfr-v').value),a=parseInt($('bfr-a').value,10);
 if(!(v>=3&&v<=65)||!(a>=8&&a<=79)){out.innerHTML='<p class="er-note">Enter a body fat percentage from 3 to 65 and an age from 8 to 79.</p>';out.classList.add('visible');return;}
 var g=grp(a),gg=ggrp(a),c=gg?D.gal[sex][gg]:null,k=c?cat(v,c):null,q=g?D.q[sex][g]:null,w=word(sex,a),h='',m,l;
 if(g){m=moreAt(D.more[sex][g],v);
  h+='<div class="bmi-result-card'+(k?' '+CARD[k]:'')+'"><div class="bmi-value">'+shareTxt(m)+'</div><div class="bmi-category">of US '+w+' aged '+nd(g)+' measured more body fat than '+v+'%</div><div class="bmi-range">CDC body scans, 2011–2018 (our calculation)</div></div>';}
 else{h+='<div class="bmi-result-card '+CARD[k]+'"><div class="bmi-value">'+v+'%</div><div class="bmi-category">'+k.charAt(0).toUpperCase()+k.slice(1)+' on the provisional range for '+w+' '+nd(gg)+'</div><div class="bmi-range">CDC’s scans stopped at age 59, so there is no US comparison at your age.</div></div>';}
 h+='<div class="er"><section class="er-section"><h3>Your reading on the chart</h3>'+fig(v,q,c,sex);
 var notes=[];if(q)notes.push('Bar: the middle half (darker) and the 10th to 90th percentile of US '+w+' aged '+nd(g)+'; the solid line is the median, '+q[2].toFixed(1)+'%.');
 if(c)notes.push('<span class="cat-dot '+DOT[k]+'"></span>'+v+'% is '+k+' on the provisional ranges for '+w+' aged '+nd(gg)+': healthy is '+rangeTxt(c,'healthy')+' (Gallagher et al., 2000).');
 else notes.push('The provisional adult ranges start at age 20; under 20, compare BMI as a percentile for age and sex.');
 h+=notes.map(function(n){return '<p class="er-note">'+n+'</p>';}).join('')+'</section>';
 if(q){h+='<section class="er-section"><h3>US '+w+' aged '+nd(g)+'</h3><table class="data-table"><caption>Body fat (%) by percentile, CDC scans ('+D.n[sex][g].toLocaleString('en-US')+' people)</caption><thead><tr><th scope="col">10th</th><th scope="col">25th</th><th scope="col">Median</th><th scope="col">75th</th><th scope="col">90th</th></tr></thead><tbody><tr>'+q.map(function(x){return '<td>'+x.toFixed(1)+'</td>';}).join('')+'</tr></tbody></table></section>';}
 h+='</div>';out.innerHTML=h;out.classList.add('visible');}
for(var i=0;i<btns.length;i++)btns[i].addEventListener('click',function(){sex=this.getAttribute('data-sex');for(var j=0;j<btns.length;j++){var on=btns[j]===this;btns[j].classList.toggle('active',on);btns[j].setAttribute('aria-pressed',on?'true':'false');}});
$('bfr-go').addEventListener('click',show);
['bfr-v','bfr-a'].forEach(function(id){$(id).addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();show();}});});
})();'''
sec_rank = (
    '<section id="rank" class="content-section flow"><h2>Where does your body fat rank?</h2>'
    '<p>Enter a reading from a scan, a scale or calipers. The tool compares it with US women or men of your age group in CDC’s '
    'body scans (or girls and boys from age 8) and shows the provisional range for your age. A scale or calipers can read '
    'differently from a DXA scan: in a study of 437 college students, a hand-held impedance device was 4.9 points off on '
    f'average ({ext(U["burns"], "Burns et al., 2019")}; <a href="/blog/how-to-measure-body-fat/">how to measure body fat</a>).</p></section>'
    '<div class="calculator-card bfr" id="bfr"><div class="calc-panel active">'
    '<div class="unit-toggle" role="group" aria-label="Sex"><button type="button" class="unit-btn active" data-sex="f" '
    'aria-pressed="true">Woman</button><button type="button" class="unit-btn" data-sex="m" aria-pressed="false">Man</button></div>'
    '<div class="form-grid"><div class="form-row"><div class="form-group"><label class="form-label" for="bfr-v">Body fat (%)</label>'
    '<input type="number" id="bfr-v" class="form-input" inputmode="decimal" min="3" max="65" step="0.1" value="30"></div>'
    '<div class="form-group"><label class="form-label" for="bfr-a">Age (years)</label><input type="number" id="bfr-a" '
    'class="form-input" inputmode="numeric" min="8" max="79" step="1" value="35"></div></div></div>'
    '<button type="button" class="calculate-btn" id="bfr-go">See where I rank</button>'
    '<div class="results-section" id="bfr-out" aria-live="polite"></div></div></div>'
    '<noscript><p>The rank tool needs JavaScript. The <a href="#every-percent">tables below</a> give the share of US men and '
    'women aged 20 to 39 and 40 to 59 with more body fat than each whole percentage.</p></noscript>'
    f'<script>window.BFR={json.dumps(TOOL, separators=(",", ":"))};</script><script>{TOOL_JS}</script>')
# The tool card sits after its section, not inside it, so no card nests in a card (DESIGN.md "Cards inside a section").

# --- every whole percentage
def lk_rows(k, lo, hi):
    out = []
    for p in range(lo, hi + 1):
        cells = ''
        for g in ('20-39', '40-59'):
            c = cat(k, g, p)
            cells += f'<td class="c-{TINT[c]}">{share_txt(more(k, g, p))}<span class="cell-kg">{c}</span></td>'
        out.append(f'<tr id="{SEXN[k]}-{p}"><th scope="row">{p}%</th>{cells}</tr>')
    return ''.join(out)
def lk_table(k, lo, hi):
    return (f'<div class="table-responsive"><table class="weight-chart weight-chart--fit"><caption>What each body fat percentage '
            f'means for US {SEXN[k]}</caption><thead><tr><th scope="col">Body fat</th>'
            + ''.join(f'<th scope="col">{SEXN[k].capitalize()} <span class="nw">{g.replace("-", "–")}</span>'
                      f'<span class="th-sub">share with more body fat</span></th>' for g in ('20-39', '40-59'))
            + f'</tr></thead><tbody>{lk_rows(k, lo, hi)}</tbody></table></div>')
M15 = more('m', '20-39', 15)
assert share_txt(M15) == '97%' and cat('m', '20-39', 15) == 'healthy'
sec_every = (
    '<section id="every-percent" class="content-section flow"><h2>What every body fat percentage means</h2>'
    '<p>Each row gives the share of US men or women in an age group whose scans showed more body fat than that percentage, and '
    f'where it falls on the provisional ranges for that age. Example: at 15% body fat, a man aged 20 to 39 has less body fat '
    f'than {share_txt(M15)} of US men his age, inside the healthy range.</p>'
    '<h3 id="men">Men</h3>' + lk_table('m', 5, 40)
    + '<h3 id="women">Women</h3>' + lk_table('f', 10, 50)
    + f'<p class="source-note">Our calculation from CDC NHANES 2011–2018 DXA scans: {BA["m"]["20-39"]["n"]:,} men aged 20 to 39, '
    f'{BA["m"]["40-59"]["n"]:,} aged 40 to 59, {BA["f"]["20-39"]["n"]:,} women aged 20 to 39 and {BA["f"]["40-59"]["n"]:,} aged '
    '40 to 59. A reading equal to the row counts on neither side. Shading and the second line: the provisional range at that '
    f'age ({GAL_CITE}). Each row has its own link, for example #men-15 or #women-30.</p>'
    '</section>')

# --- healthy body fat: where the ranges come from
sec_healthy = (
    '<section id="healthy" class="content-section flow"><h2>Healthy body fat percentage</h2>'
    '<p>CDC’s adult categories use BMI, and CDC notes that “BMI does not distinguish between fat, muscle, and bone mass” '
    f'({ext(U["cdc_about"], "CDC")}).</p>'
    f'<p>The ranges in the chart come from Gallagher and colleagues ({ext(U["gallagher"], "Am J Clin Nutr, 2000")}). They '
    'measured body fat in 1,626 adults at three universities, Cambridge in the UK, Columbia in the US and Jikei in Japan, with DXA '
    'scans at all three and a four-compartment model at two. From that they predicted the body fat that goes with a BMI of 18.5, 25 and 30 by sex, '
    'age and ethnic group (white, African American and Asian adults), and called the ranges provisional.</p>'
    '<p>Many charts online add tiers such as “athletes” and “fitness”. Those tiers come from a fitness organization’s chart and '
    'aren’t matched to BMI or age, so this page leaves them out.</p>'
    '<p>How body fat is measured matters too. CDC’s scanner software adds 5% of lean mass to the fat mass '
    f'({ext(U["dxx"], "CDC")}), and every US figure on this page, the <a href="#every-percent">tables above</a> included, comes '
    'from those scans. So compare a reading with numbers from the same kind of measurement where you can.</p>'
    '</section>')

# --- body fat and BMI
def bc_cell(k, c): return f'{f1(BC[k][c]["p50"])}%<span class="cell-kg">{mid(k, c)}</span>'
BMI_CATS = (('under', 'Under 18.5'), ('healthy', '18.5–24.9'), ('over', '25–29.9'), ('obese', '30 or more'))
bc_rows = ''.join(f'<tr><th scope="row"><span class="cat-dot {d}"></span>{lab}</th><td>{bc_cell("f", c)}</td><td>{bc_cell("m", c)}</td></tr>'
                  for (c, lab), d in zip(BMI_CATS, ('underweight', 'normal', 'overweight', 'obese')))
at_rows = ''.join(f'<tr><th scope="row">{SEXN[k].capitalize()} {g.replace("-", "–")}</th>'
                  f'<td>{at(k, "25", g)}%</td><td>{GAL[k][g][1]}%</td></tr>'
                  for k in ('f', 'm') for g in ('20-39', '40-59'))
sec_bmi = (
    '<section id="bmi" class="content-section flow"><h2>Body fat and BMI</h2>'
    '<p>On average, body fat rises with BMI, but in CDC’s scans of US adults aged 20 to 59, people with the same BMI measured '
    f'a wide spread of body fat. At every BMI from 19 to 30, the median woman measured about {GAP_LO} to {GAP_HI} points more than '
    'the median man.</p>'
    f'<figure class="figure">{svg_bmi}<figcaption>Body fat at each whole BMI: the median (line) and the middle half (band), US '
    'women and men aged 20 to 59. CDC NHANES 2011–2018 DXA scans, our calculation.</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table"><caption>Body fat in each BMI category, adults aged 20 to 59: the '
    'median, with the middle half below it</caption><thead><tr><th scope="col">BMI</th><th scope="col">Women</th><th scope="col">Men</th></tr></thead>'
    f'<tbody>{bc_rows}</tbody></table></div>'
    f'<p><strong>Example.</strong> A woman 5′4″ tall who weighs 140 lb has a BMI of {EX["bmi"]} (140 × 703 ÷ 64², '
    f'{ext(U["cdc_formula"], "CDC formula")}), a healthy weight on CDC’s categories. US women aged 20 to 59 with a BMI of 23.5 to '
    f'24.4 measured a median {EX_MED}% body fat, and the middle half were between {EX_LO}% and {EX_HI}%.</p>'
    '<h3>How the provisional ranges line up with CDC’s scans</h3>'
    f'<p>The provisional ranges match a BMI of 25 to the start of “high”: {GAL["m"]["20-39"][1]}% body fat for men and '
    f'{GAL["f"]["20-39"][1]}% for women aged 20 to 39, as tabulated in J Public Health Afr 2016. In CDC’s scans, adults within '
    f'half a point of a BMI of 25 averaged {at("m", "25", "20-39")}% (men) and {at("f", "25", "20-39")}% (women) at that age. '
    f'So on CDC’s scanner, readings in the provisional “high” range are common at a healthy BMI: {HB_M}% of US men and {HB_F}% '
    'of US women aged 20 to 59 with a BMI of 18.5 to 24.9 measured in the “high” range or above (our calculation).</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Body fat at a BMI of 25</caption><thead><tr><th scope="col">'
    'Sex and age</th><th scope="col">CDC scans<span class="th-sub">average</span></th><th scope="col">Provisional ranges'
    '<span class="th-sub">“high” starts</span></th></tr></thead>'
    f'<tbody>{at_rows}</tbody></table></div>'
    '<p class="source-note">CDC scans: our calculation, NHANES 2011–2018, the average body fat of adults whose BMI was within half '
    f'a point of 25 (24.5 to 25.4; {min(AT[k]["25"][g]["n"] for k in "mf" for g in ("20-39", "40-59"))} or more adults in each '
    f'row). Provisional: where the “high” range starts ({GAL_CITE}, as tabulated in '
    f'{ext(U["jpha"], "J Public Health Afr 2016, Table 1")}).</p>'
    '</section>')

# --- age, sex and children
def pct_rows(k):
    return ''.join(f'<tr><th scope="row">{g.replace("-", "–")}</th>' + ''.join(f'<td>{qv(k, g, p)}%</td>' for p in ('p10', 'p25', 'p50', 'p75', 'p90'))
                   + f'<td>{mean(k, g)}%</td><td>{BA[k][g]["n"]:,}</td></tr>' for g in KIDS + DEC)
def pct_table(k):
    return (f'<div class="table-responsive"><table class="data-table"><caption>US {SEXN[k]} and {SEXK[k]} by age</caption><thead><tr><th scope="col">Age</th><th scope="col">10th</th>'
            '<th scope="col">25th</th><th scope="col">Median</th><th scope="col">75th</th><th scope="col">90th</th>'
            f'<th scope="col">Average</th><th scope="col">Scanned</th></tr></thead><tbody>{pct_rows(k)}</tbody></table></div>')
sec_age = (
    '<section id="age-sex" class="content-section flow"><h2>Body fat by age and sex</h2>'
    f'<p><strong>Age.</strong> From their 20s to their 50s, the average rose {AGE_M["diff"]} points for US men '
    f'({mean("m", "20-29")}% to {mean("m", "50-59")}%) and {AGE_F["diff"]} points for women ({mean("f", "20-29")}% to '
    f'{mean("f", "50-59")}%).</p>'
    f'<p><strong>Sex.</strong> Women measured {WM_LO} to {WM_HI} points more body fat than men in every decade from 20 to 59 '
    '(our calculation from CDC body scans).</p>'
    f'<figure class="figure">{svg_age}<figcaption>Body fat by age: the median (line) and the middle half (band), US females and '
    'males aged 8 to 59. CDC NHANES 2011–2018 DXA scans, our calculation.</figcaption></figure>'
    f'<p><strong>Children and teens.</strong> Boys’ average fell from {mean("m", "8-11")}% at 8 to 11 to {mean("m", "16-19")}% at '
    f'16 to 19, while girls’ rose from {mean("f", "8-11")}% to {mean("f", "16-19")}%. Under 20, BMI is read as a percentile '
    f'for age and sex ({ext(U["cdc_child"], "CDC")}); the <a href="/kids-bmi-calculator/">BMI calculator for children and '
    'teens</a> works it out.</p>'
    '<p><strong>Over 60.</strong> CDC’s 2011–2018 scans stopped at age 59, so there are no US measurements for older adults '
    'here; the chart’s 60 to 79 rows are the provisional ranges only.</p>'
    + pct_table('f') + pct_table('m') +
    f'<p class="source-note">CDC NHANES 2011–2018 DXA scans, our calculation. The averages, medians and percentiles for every '
    f'group are also in a <a href="{CSV}">CSV download</a> '
    '(free to reuse with a link to this page, CC BY 4.0).</p>'
    '</section>')

sec_print = (
    '<section id="printable" class="content-section flow"><h2>Printable body fat chart</h2>'
    '<p>The <a href="#chart">chart by age</a> as one image to print or save, with the US median and the sources on it.</p>'
    f'<figure class="figure figure--wide"><a href="{CHART_IMG}"><img src="{CHART_IMG}" width="{CHART_W}" height="{CHART_H}" '
    'loading="lazy" decoding="async" alt="Body fat percentage chart for women and men by age: provisional low, healthy, high '
    'and very high ranges for ages 20 to 39, 40 to 59 and 60 to 79, with the median measured in US adults"></a><figcaption>'
    'Printable body fat percentage chart for women and men: the provisional ranges and the US median from CDC body scans. '
    'Open the image to print or save it.</figcaption></figure>'
    '</section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC NHANES 2011–2012 to 2017–2018 {ext(U["dxx"], "whole-body DXA scans")} (DXX_G to DXX_J) with the demographics and body '
    f'measures files: our calculation for {META["n_adults_20_59"]:,} adults aged 20 to 59 ({META["n_women_20_59"]:,} women, '
    f'{META["n_men_20_59"]:,} men) and for children and teens from 8. CDC’s documentation: ages 8 to 59; pregnancy, a weight '
    'over 450 lb or a height over 6′5″ exclude a scan; valid scans are less common at higher BMIs; the software adds 5% of lean '
    'mass to the fat mass.',
    f'Liu B, et al. {ext(U["liu"], "Trends in obesity and adiposity measures by race or ethnicity among adults in the United States 2011-18")} '
    '(BMJ 2021;372:n365): our method reproduces its mean body fat for every survey cycle.',
    f'Gallagher D, et al. {ext(U["gallagher"], "Healthy percentage body fat ranges: an approach for developing guidelines based on body mass index")} '
    '(Am J Clin Nutr 2000;72:694–701): the provisional ranges.',
    f'{ext(U["jpha"], "Interpreting the body fat percentage result, Table 1")} (J Public Health Afr 2016;7:515): the provisional '
    'ranges as tabulated.',
    f'CDC. {ext(U["cdc_about"], "About Body Mass Index (BMI)")}: what BMI does and doesn’t measure.',
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the healthy range of 18.5 to 24.9.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formula in US units.',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles for ages 2 to 19.',
    f'Burns RD, Fu Y, Constantino N. {ext(U["burns"], "Measurement agreement in percent body fat estimates among laboratory and field assessments in college students: use of equivalence testing")} '
    '(PLOS ONE 2019): how far home methods read from DXA (437 college students).',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> We pooled CDC’s National Health and Nutrition Examination Survey cycles '
    '2011–2012 through 2017–2018, kept valid whole-body scans, left out pregnant women and used CDC’s exam weights divided by '
    'four, as CDC’s guidelines advise for four cycles. Percentiles are weighted. Shares above or below a percentage count '
    'readings strictly above or below it, and every figure is rounded once, from the unrounded estimate. We tested averages and '
    'differences with 95% confidence intervals from Taylor linearization over the survey’s strata and primary sampling units '
    f'({META["df"]} degrees of freedom); the page states only differences whose interval excludes zero, and the CSV download '
    'gives each average’s standard error. Body fat at each BMI uses the measured BMI as CDC records it. Because valid scans are less '
    'common at higher BMIs, the heaviest adults are under-represented and the averages may run a little low. With the same age '
    'adjustment as Liu et al. (BMJ 2021), our figures reproduce their mean body fat for every cycle from the same 10,864 '
    'adults.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/body-fat-calculator/', 'Body fat calculator'), ('/', 'BMI calculator'),
        ('/lean-body-mass/', 'Lean body mass calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/kids-bmi-calculator/', 'BMI calculator for children and teens')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/blog/how-to-measure-body-fat/', 'How to measure body fat'), ('/blog/body-fat-vs-bmi/', 'Body fat vs BMI'),
        ('/blog/healthy-bmi-range/', 'Healthy BMI range'), ('/bmi-chart/', 'BMI chart'),
        ('/average-weight/', 'Average weight by height'), ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> <article> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_chart, sec_rank, sec_every, sec_healthy, sec_bmi, sec_age, sec_print, sec_faq, sec_src,
     sec_rel])
    + ' </article> </div></main>')
assert 'placeholder' not in main and 'style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', main)
assert len(re.findall(r'<section id="([^"]+)"', main)) == 9 and all(f'id="{a}"' in main for a, _ in CHIPS)

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'Body Fat Percentage Chart: Women and Men by Age, US Averages'   # not "(CDC Data)": CDC didn't make the ranges
DESC = ('Body fat percentage chart for women and men by age: the provisional healthy ranges, what US adults measure on CDC '
        'body scans, and what any percentage means.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'Body fat percentage chart for women and men by age'
OG_D = (f'The provisional healthy ranges, CDC’s body scans of US adults (average {AVG_F}% for women, {AVG_M}% for men), and what '
        'each whole percentage means: 10–50% for women, 5–40% for men.')
OG_ALT = 'Chart: provisional body fat ranges for women and men in three age groups, low to very high.'
PREF = SITE + '/assets/images/preferred/body-fat-percentage-chart-'
IMG16, IMG43, IMG11 = PREF + '16x9.png', PREF + '4x3.png', PREF + '1x1.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG16}">', src)
src = sub1(r'<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', src)
src = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', src)
src = sub1(r'<meta name="twitter:card" content="summary_large_image">',
           f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{OG_T}">'
           f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1
# The three page-level <style> blocks (the old chart's .bmi-chart cells, the cmb-* page styles and the aw-* tool) give way
# to styles.css: .weight-chart, the calculator card and the answer-first results.
_head = src[:src.index('<body')]
assert _head.count('<style>') == 3 and src.count('<style>') == 3
src = re.sub(r'(?s)<style>.*?</style>', '', src)

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 1
graph = json.loads(blocks[0].group(1))['@graph']
assert [n['@type'] for n in graph] == ['Article', 'Dataset', 'BreadcrumbList', 'Organization', 'Person'], [n['@type'] for n in graph]
art, ds, crumbs = graph[0], graph[1], graph[2]
assert art['datePublished'] == '2026-10-04' and art['mainEntityOfPage']['@id'] == URL
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
ORG = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'CalculateMyBMI', 'url': SITE + '/'}
art = {'@type': 'Article', '@id': URL + '#article', 'headline': H1, 'description': DESC, 'url': URL,
       'datePublished': art['datePublished'], 'dateModified': '{TODAY}', 'inLanguage': 'en-US',
       'isPartOf': {'@type': 'WebSite', 'name': 'CalculateMyBMI', 'url': SITE + '/'},
       'author': PERSON, 'publisher': ORG, 'image': [IMG11, IMG43, IMG16],
       'mainEntityOfPage': {'@type': 'WebPage', '@id': URL, 'url': URL, 'primaryImageOfPage': {
           '@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}},
       'citation': [U['dxx'], U['liu'], U['gallagher'], U['jpha']]}
assert ds['distribution'][0]['contentUrl'] == SITE + CSV and ds['license'] == 'https://creativecommons.org/licenses/by/4.0/'
ds['creator'] = ORG
crumbs['itemListElement'][1]['name'] = H1
faq_ld = {'@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
new_ld = {'@context': 'https://schema.org', '@graph': [art, ds, crumbs, faq_ld]}
b = blocks[0]
src = src[:b.start(1)] + ' ' + json.dumps(new_ld, ensure_ascii=False) + ' ' + src[b.end(1):]

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('{TODAY}') == 1 and '<style' not in src

open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'body-fat-percentage-chart/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, '
      f'{len(FAQ)} FAQ, {len(TEXTS)} SVG labels checked')
