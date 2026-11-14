#!/usr/bin/env python3
"""CMB-045 AGE-CALC: builds /age-bmi-calculator/ to the D-14 calculator pattern (DESIGN.md; the homepage, the women's,
men's and kids' calculators applied it): tool first, answer block and key takeaways, contents chips, a worked example,
real tables and a figure, a flat FAQ whose JSON-LD equals the visible answers, sources and method, one related block,
one 680 px reading column. usage: python3 research/age-calc-build/gen_abc.py

Owns everything inside <main> and, in the head, the meta description, the OG and Twitter text and images and the JSON-LD.
The title stays as it is (D-28: the page has search traffic; the title, H1 and URL are the owner's call), as do the
Raptive, consent and GA4 scripts, the header, the scripts after </main> and the footer; running it twice gives the same
file.

SERP (chat in Claude in Chrome, google.com, hl=en, gl=us, pws=0, 2026-11-14):
  "bmi calculator by age": CDC Child and Teen BMI Calculator, Smart BMI ("Free BMI Calculator by Age Gender": its own
    0-70 point score from age and sex), CDC Adult BMI Calculator, Calculator.net, Pennington (PBRC), Medical News Today,
    American Cancer Society, Baylor BMI z-score. AI Overview: adults use the same categories at every age; children are
    read as percentiles; for "age-adjusted" scoring it points to Smart BMI. People also ask: "What is correct BMI for my
    age?", "What is a good BMI for a senior over 70?", "What body type lives the longest?", "How to calculate BMI for
    seniors?". The senior answer quotes 25 to 29.9 or 23 to 29.9 from senior-living and fitness sites; the "my age"
    answer quotes 22 to 26 for older adults.
  "bmi calculator kg with age": CDC, Calculator.net, NHLBI, PBRC, ACS, NHS, Axis Max Life, Heart Foundation; PAA adds
    "How to calculate BMI including age?".
  "bmi calculator women age": CDC, Calculator.net, Smart BMI, PBRC, NHLBI, ACS, Omni (women), Mayo; PAA: "What is the
    ideal BMI for females by age?", "Is BMI calculated differently for seniors?", "What is my BMI for my age?", "How to
    calculate BMI with age, height, and weight?".
  Gap: no result places a BMI among US adults of the same age and sex from measured data; the one "age and gender" tool
  uses a score of its own; the senior answers give ranges CDC doesn't use.
Wedge: (1) the rank among US women or men in the same age group (20-39, 40-59, 60+), CDC NHANES 2021-2023, 5,929 adults
  (abc_stats.json; the women's curves are the women's calculator's); (2) what is typical for the same sex and decade:
  average BMI, weight and waist (research/average-weight/avgw_results.json = NCHS Series 3 No. 50), median and middle
  half, the share with a healthy BMI; (3) the age-adjusted and senior ranges answered with CDC's rule and Winter et al.
  2014 in the §4 wording, and ages 2-19 handed to the kids calculator.

Removed from the old page (why): the "WHO adult BMI range at a glance" box ("65+ (Winter 2014) 23-33 (observed
plateau)" next to 18.5-24.9 read as an age-specific range: D-11, §5 [P2]); the 18-64 / 65+ table (CDC's categories start
at 20; 18-64 had no source); "The Obesity Paradox Explained" with a schematic U-curve (no data behind it) and a Flegal
2013 bar chart (it printed +5% for grade 1 obesity, whose hazard ratio of 0.95 is 5% lower, and +23% for underweight,
which the registry row doesn't hold); "Official guidance on activity and sleep" (the sleep figures had no registry row;
off the page's subject); "BMI and age-related health conditions" (unsourced list, §5 [P1] claims); "Trusted External
Resources" (descriptions without sources); the OG image assets/images/og/age-bmi-ucurve.png (the same schematic curve).
Not on the page (why): an age-specific healthy range (D-11); weight targets of our own (D-06); a "see your doctor" line
without an official source that says when (§4).
"""
import csv
import html
import json
import math
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PAGE = os.path.join(ROOT, 'age-bmi-calculator/index.html')
S = json.load(open(os.path.join(HERE, 'abc_stats.json'), encoding='utf-8'))
AVGW = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json'), encoding='utf-8'))
BFP = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json'), encoding='utf-8'))
KIDS = json.load(open(os.path.join(ROOT, 'research/kids-build/kids_stats.json'), encoding='utf-8'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds                 # noqa: E402

SITE = 'https://calculatemybmi.net'
URL = SITE + '/age-bmi-calculator/'
TITLE = 'BMI Calculator by Age &amp; Gender (kg or lbs): US Averages'  # kept (D-28), as the head has it
TITLE_TEXT = html.unescape(TITLE)
H1 = 'BMI Calculator by Age'                                          # kept (D-28)
IMG = {r: f'{SITE}/assets/images/preferred/age-bmi-calculator-{r}.png' for r in ('1x1', '4x3', '16x9')}


# ---------------------------------------------------------------- numbers
def f1(x): return f'{x:.1f}'
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10              # calculator.js round1()
def dcm(inches): return str((Decimal(str(inches)) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))


def pct(q, b):
    """The page script's pct(): the share at or below b, read off the 1st-99th percentile curve."""
    if b <= q[0]:
        return 0.0
    if b >= q[98]:
        return 100.0
    for i in range(98):
        if b < q[i + 1]:
            return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0


def lower(q, b): return pct(q, round(b - 0.1, 1))                   # strictly lower BMI (US rank rule, CMB-012)
def higher(q, b): return 100 - pct(q, b)                            # strictly higher BMI
def nn(x): return 99 if x > 99 else int(math.floor(x + 0.5))        # the script's n(): Math.round, capped at 99


C, G, DEC, DIF = S['curves'], S['groups'], S['decades'], S['differences']
SEXES = ('women', 'men')
GRPS = ('20-39', '40-59', '60+')
AGES = ('20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')
N = {s: G[s]['n'] for s in SEXES}
NG = {s: {g: G[f'{s}_{g}']['n'] for g in GRPS} for s in SEXES}
assert (N['women'], N['men'], N['women'] + N['men']) == (3249, 2680, 5929)
assert NG == {'women': {'20-39': 826, '40-59': 947, '60+': 1476}, 'men': {'20-39': 672, '40-59': 762, '60+': 1246}}
MED = {s: {g: f1(G[f'{s}_{g}']['p50']) for g in GRPS} for s in SEXES}
assert MED == {'women': {'20-39': '27.1', '40-59': '29.3', '60+': '28.4'}, 'men': {'20-39': '27.3', '40-59': '29.0', '60+': '28.4'}}
MED_ALL = {s: f1(G[s]['p50']) for s in SEXES}
assert MED_ALL == {'women': '28.3', 'men': '28.2'}
PCT_ROWS = (('p5', '5th'), ('p10', '10th'), ('p25', '25th'), ('p50', 'Median'), ('p75', '75th'), ('p90', '90th'), ('p95', '95th'))

# Decades: the mean must equal avgw_results.json (= NCHS Series 3 No. 50); the weights and waists are its own.
AV = {s: {d: AVGW[s]['age'][d.replace('-', '–')] for d in AGES} for s in SEXES}
for s in SEXES:
    for d in AGES:
        assert abs(DEC[s][d]['mean'] - AV[s][d]['bmi']['mean']) < 1e-3 and DEC[s][d]['n'] == AV[s][d]['bmi']['n'], (s, d)
KG_PER_LB = 2.2046                                                   # avgw_results.json: lb = kg x 2.2046 (NCHS)
def avg_wt(s, d): return AV[s][d]['wt']['mean']
def avg_kg(s, d): return AV[s][d]['wt']['mean'] / KG_PER_LB
def avg_in(s, d): return AV[s][d]['waist']['mean']
def avg_cm(s, d): return AV[s][d]['waist']['mean'] * 2.54
DM = {s: {d: f1(DEC[s][d]['mean']) for d in AGES} for s in SEXES}
assert DM['women'] == {'20-29': '28.0', '30-39': '30.5', '40-49': '30.7', '50-59': '31.4', '60-69': '30.1', '70-79': '29.5', '80+': '27.7'}
assert DM['men'] == {'20-29': '27.8', '30-39': '29.5', '40-49': '30.5', '50-59': '30.2', '60-69': '29.2', '70-79': '29.4', '80+': '27.8'}
# "25 or higher in every decade": the low end of every decade mean's 95% interval is above 25.
assert all(DEC[s][d]['ci95'][0] > 25 for s in SEXES for d in AGES)
LOW = {s: min(DM[s].values(), key=float) for s in SEXES}
HIGH = {s: max(DM[s].values(), key=float) for s in SEXES}
assert (LOW, HIGH) == ({'women': '27.7', 'men': '27.8'}, {'women': '31.4', 'men': '30.5'})
# Differences the page states (each 95% interval excludes 0).
for s in SEXES:
    for k in ('mean_40-49_minus_20-29', 'mean_50-59_minus_20-29', 'mean_80+_minus_50-59', 'healthy_20-29_minus_50-59'):
        assert DIF[f'{s}_{k}']['excludes_0'], (s, k)
        assert (DIF[f'{s}_{k}']['diff'] > 0) == ('minus_20-29' in k or k.startswith('healthy')), (s, k)
DH = {s: {d: f1(DEC[s][d]['healthy']['pct']) for d in AGES} for s in SEXES}
assert (DH['women']['20-29'], DH['women']['50-59'], DH['men']['20-29'], DH['men']['50-59']) == ('40.6', '23.3', '32.2', '21.6')
D70 = {s: (f1(DEC[s]['70-79']['p50']), DH[s]['70-79'], DEC[s]['70-79']['n']) for s in SEXES}
assert D70 == {'women': ('28.0', '25.7', 493), 'men': ('28.8', '20.9', 444)}

# NCHS Data Brief 508 (registry nhanes-adult-obesity-2021-2023): obesity by age group, reproduced by abc_stats.py.
DB = {g: f1(S['db508'][f'adults_{g}']['pct']) for g in GRPS}
assert DB == {'20-39': '35.5', '40-59': '46.4', '60+': '38.9'}

# CDC's body scans, 2011-2018 (bfpc_stats.json, the body fat chart's; ages 8-59 only).
BA = BFP['by_age']
BF = {s: (f1(BA[s]['20-29']['mean4']), f1(BA[s]['50-59']['mean4'])) for s in 'mf'}
assert BF == {'m': ('25.4', '28.3'), 'f': ('36.9', '40.3')}
assert all(BFP['diff']['age'][s]['50s_minus_20s']['excludes_0'] for s in 'mf')

# The kids' example (kids_stats.json): a 10-year-old girl with a BMI of 23.6 is at the 96th percentile, obesity.
GIRL = KIDS['anchors']['girl-10-98']
assert (GIRL['bmi'], GIRL['ordinal'], GIRL['category'], GIRL['years'], GIRL['sex']) == ('23.6', 96, 'Obesity', 10, 'female')

# Worked example: the calculator's starting values, a 45-year-old woman, 5'6" and 170 lb.
EX_AGE, EX_H, EX_W = 45, 66, 170
EX_BMI = r1(EX_W * 703 / EX_H ** 2)
assert EX_BMI == 27.4
EX_CM, EX_KG = dcm(EX_H), f1(EX_W / 2.20462)
assert (EX_CM, EX_KG) == ('167.6', '77.1')
HB_LB, HB_KG = gate_bounds('lb', EX_H, EX_H * 2.54, 1), gate_bounds('kg', EX_H, EX_H * 2.54, 1)
assert HB_LB == (115, 154) and HB_KG == (52, 70), (HB_LB, HB_KG)
FROM = {c: gate_bounds('lb', EX_H, EX_H * 2.54, i)[0] for c, i in ((25, 2), (30, 3), (35, 4), (40, 5))}
assert FROM == {25: 155, 30: 186, 35: 217, 40: 248}, FROM
EXR = {g: nn(lower(C[f'women_{g}'], EX_BMI)) for g in GRPS}
EXH = nn(higher(C['women_40-59'], EX_BMI))
EX_ALL = nn(lower(C['women'], EX_BMI))
EX_MAN = nn(lower(C['men_40-59'], EX_BMI))
assert (EXR, EXH, EX_ALL, EX_MAN) == ({'20-39': 51, '40-59': 39, '60+': 43}, 60, 44, 38), (EXR, EXH, EX_ALL, EX_MAN)
EX_DEC = '40-49'
EX_TYP = (DM['women'][EX_DEC], f1(avg_wt('women', EX_DEC)), f1(avg_kg('women', EX_DEC)), f1(avg_in('women', EX_DEC)),
          f1(avg_cm('women', EX_DEC)))
assert EX_TYP == ('30.7', '177.3', '80.4', '38.7', '98.2'), EX_TYP
EX_PRIME = f'{math.floor(EX_BMI * 4 + 0.5) / 100:.2f}'                # bmiPrime(): Math.round(27.4 * 4) / 100
EX_PI = f'{(EX_W / 2.20462) / ((EX_H * 2.54 / 100) ** 3):.1f}'      # genKeyMetrics(): kg / m^3, toFixed(1)
assert (EX_PRIME, EX_PI) == ('1.10', '16.4'), (EX_PRIME, EX_PI)

# Height loss: the same weight at 5'8" and 5'6", from a BMI of 25 at 5'8".
W25 = 25 * 68 ** 2 / 703
LOSS = W25 * 703 / 66 ** 2 - 25
assert f'{LOSS:.1f}' == '1.5', LOSS

# ---------------------------------------------------------------- sources verified in chat
# CDC Adult BMI Categories (registry cdc-adult-bmi-categories): "For adults 20 and older, BMI categories are based on a
#   person's BMI regardless of age, sex, or race."; healthy weight "18.5 to less than 25".
# CDC Calculating BMI (registry cdc-calculating-bmi): kg / m^2 and lb / in^2 x 703.
# CDC Child and Teen BMI Categories (registry cdc-child-bmi-categories): under the 5th percentile underweight, 5th to less
#   than 85th healthy weight, 85th to less than 95th overweight, 95th or greater obesity.
# Winter et al. 2014 (registry winter-2014-bmi-mortality-65): 32 cohort studies, 197,940 people aged 65 and over;
#   reference BMI 23.0-23.9; "Mortality risk began to increase for BMI >33.0"; "the risk of mortality increased in older
#   people with a BMI <23.0". Wording on this page: DEVLOG §4 (since CMB-036).
# Volpi et al. 2004 (registry volpi-2004-muscle-aging): "Muscle mass decreases approximately 3-8% per decade after the
#   age of 30" and "this rate of decline is even higher after the age of 60".
# ADA Standards of Care in Overweight and Obesity 2026 (registry ada-2026-obesity-standards): "Loss of muscle mass in
#   older adults reduces the accuracy of BMI, which may lead to underdiagnosis of obesity."
# NCHS Data Brief 508 (registry nhanes-adult-obesity-2021-2023): 35.5 / 46.4 / 38.9% at 20-39 / 40-59 / 60+; "This
#   pattern was seen in both men and women"; 5,929 adults aged 20 and older.
# NCHS Series 3 No. 50 (registry nhanes-anthropometric-reference): the decade means of weight, BMI and waist; pregnant
#   women excluded.
# Senior calculators (chat in Chrome, 2026-11-14; not named on the page): omnicalculator.com/health/geriatric-bmi reads a
#   BMI of 23-29.9 as "Normal" (<23 "Underweight", >=30 "Overweight/obese") and lists Winter et al. 2014 among its
#   sources; vanswefitness.com/pages/bmi-calculator-for-seniors: "For adults over age 65, a healthy Body Mass Index (BMI)
#   is generally considered to be between 23 and 30", "adapted from geriatric meta-analyses by Winter et al.".


def ext(url, text): return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'


def esc(s): return html.escape(s, quote=False)


U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'nhanes': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'volpi': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/',
    'ada': 'https://doi.org/10.2337/doci26-0003',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    's3': 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf',
}
REG = {r['domain']: r['url'] for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}
for k, dom in (('cdc_cat', 'cdc-adult-bmi-categories'), ('cdc_formula', 'cdc-calculating-bmi'), ('cdc_child', 'cdc-child-bmi-categories'),
               ('nhanes', 'nhanes-2021-2023-exam-files'), ('dxx', 'nhanes-2011-2018-dxa'), ('winter', 'winter-2014-bmi-mortality-65'),
               ('volpi', 'volpi-2004-muscle-aging'), ('ada', 'ada-2026-obesity-standards'), ('db508', 'nhanes-adult-obesity-2021-2023'),
               ('s3', 'nhanes-anthropometric-reference')):
    assert REG.get(dom) == U[k], (k, dom, REG.get(dom))
S3_TITLE = 'NCHS, Anthropometric Reference Data for Children and Adults, August 2021–August 2023'
DB508_TITLE = 'Obesity and Severe Obesity Prevalence in Adults: United States, August 2021–August 2023'
WINTER = ('compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 '
          f'({ext(U["winter"], "Winter et al., 2014")})')                # DEVLOG §4 wording

# ---------------------------------------------------------------- the figure: BMI of US women and men by decade
TEXTS, RECTS, VBW = [], [], {}


def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827'):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'


def rect(svg, x, y, w, h, fill, extra='', tip=None, track=True):
    if track:
        RECTS.append((svg, x, y, x + w, y + h))
    t = f'<title>{esc(tip)}</title>' if tip else ''
    tag = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}'
    return f'{tag}>{t}</rect>' if t else f'{tag}/>'


INK, MUTED, GRID = '#1f2937', '#4b5563', '#e5e7eb'
SER = {'women': '#be185d', 'men': '#4338ca'}                         # DESIGN.md series colours (CMB-016)
AW, AX0, AX1, AY0, PITCH = 320, 50, 310, 56, 36


def ax(b): return AX0 + (b - 15) * (AX1 - AX0) / 30.0                 # BMI 15 to 45


def age_words(d): return d.replace('-', ' to ').replace('+', ' and over')


VBW['age'] = AW
fa = [f'<rect x="{ax(18.5):.1f}" y="{AY0 - 8}" width="{ax(25) - ax(18.5):.1f}" height="{PITCH * len(AGES) + 2}" fill="#dcfce7"/>']
fa.append(text('age', (ax(18.5) + ax(25)) / 2, AY0 - 14, 'Healthy 18.5–24.9', 12, fill='#15803d'))
for i, s in enumerate(SEXES):                                          # legend
    x = AX0 + i * 92
    fa.append(rect('age', x, 8, 12, 12, SER[s], track=True))
    fa.append(text('age', x + 17, 18.5, s.capitalize(), 12, anchor='start', fill=INK))
for b in (20, 25, 30, 35, 40, 45):
    fa.append(f'<line x1="{ax(b):.1f}" y1="{AY0 - 8}" x2="{ax(b):.1f}" y2="{AY0 + PITCH * len(AGES) - 6}" stroke="{GRID}" stroke-width="1"/>')
for i, d in enumerate(AGES):
    y0 = AY0 + i * PITCH
    fa.append(text('age', 0, y0 + 13, d.replace('-', '–'), 12, anchor='start', fill=INK))
    for j, s in enumerate(SEXES):
        v = DEC[s][d]
        yc = y0 + 4 + j * 12
        tip = (f'{s.capitalize()} {age_words(d)}: median BMI {f1(v["p50"])}, middle half {f1(v["p25"])}–{f1(v["p75"])}, '
               f'10th to 90th percentile {f1(v["p10"])}–{f1(v["p90"])} ({v["n"]:,} {s})')
        fa.append(f'<line x1="{ax(v["p10"]):.1f}" y1="{yc}" x2="{ax(v["p90"]):.1f}" y2="{yc}" stroke="{SER[s]}" stroke-width="1.5"/>')
        fa.append(rect('age', ax(v['p25']), yc - 4.5, ax(v['p75']) - ax(v['p25']), 9, SER[s], extra=' fill-opacity="0.35" rx="2"', tip=tip))
        fa.append(f'<line x1="{ax(v["p50"]):.1f}" y1="{yc - 6}" x2="{ax(v["p50"]):.1f}" y2="{yc + 6}" stroke="#111827" stroke-width="2.5"/>')
AXY = AY0 + PITCH * len(AGES) + 8
for b in (20, 25, 30, 35, 40, 45):
    fa.append(text('age', ax(b), AXY, f'{b}', 12, fill=MUTED))
fa.append(text('age', (AX0 + AX1) / 2, AXY + 18, 'BMI', 12, fill=INK))
AH = AXY + 26
FIG_DESC = ('For each decade of age, the median BMI of US women and of US men and the middle half, against CDC’s healthy '
            'range of 18.5 to 24.9. ' + ' '.join(
                f'{age_words(d).capitalize()}: women median {f1(DEC["women"][d]["p50"])}, middle half {f1(DEC["women"][d]["p25"])} '
                f'to {f1(DEC["women"][d]["p75"])}; men median {f1(DEC["men"][d]["p50"])}, middle half {f1(DEC["men"][d]["p25"])} '
                f'to {f1(DEC["men"][d]["p75"])}.' for d in AGES) + ' CDC NHANES 2021 to 2023, our calculation.')
svg_age = (f'<svg viewBox="0 0 {AW} {AH}" role="img" aria-labelledby="age-fig-t age-fig-d" xmlns="http://www.w3.org/2000/svg" '
           'font-family="inherit"><title id="age-fig-t">BMI of US women and men by age</title>'
           f'<desc id="age-fig-d">{esc(FIG_DESC)}</desc>' + ''.join(fa) + '</svg>')


def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]


for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b):
            raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r):
            raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg] and y0 >= 0 and y1 <= AH, f'{svg} label outside the viewBox: {s!r}'


# ---------------------------------------------------------------- the calculator card and its page script
def fg(lab, iid, cls, val, mn, mx):
    return (f'<div class="form-group"><label class="form-label" for="{iid}">{lab}</label><input type="number" id="{iid}" '
            f'class="form-input {cls}" value="{val}" min="{mn}" max="{mx}"></div>')


CALC = (
    '<div class="calculator-card"><div id="panel-age" class="calc-panel active">'
    '<div class="unit-toggle"><button class="unit-btn active" data-unit="imperial">Imperial (ft, lbs)</button>'
    '<button class="unit-btn" data-unit="metric">Metric (cm, kg)</button></div><div class="form-grid">'
    '<div class="form-row form-row--trio imperial-inputs">' + fg('Height (ft)', 'age-height-ft', 'height-ft', 5, 1, 8)
    + fg('Height (in)', 'age-height-in', 'height-in', 6, 0, 11) + fg('Weight (lb)', 'age-weight-lbs', 'weight-lbs', 170, 50, 700)
    + '</div><div class="form-row form-row--pair metric-inputs" hidden>' + fg('Height (cm)', 'age-height-cm', 'height-cm', 168, 50, 250)
    + fg('Weight (kg)', 'age-weight-kg', 'weight-kg', 77, 20, 300) + '</div>'
    '<div class="form-row form-row--pair">' + fg('Age (years)', 'age-years', 'age-input', EX_AGE, 2, 120)
    + '<div class="form-group"><label class="form-label" for="age-sex">Sex</label><select id="age-sex" class="form-select sex-select">'
    '<option value="female">Woman</option><option value="male">Man</option></select></div></div>'
    '</div><button class="calculate-btn" id="calc-age-btn">Calculate BMI by Age</button>'
    '<p class="calc-note" id="age-note" role="status" hidden></p>'
    '<div class="results-section" id="age-results"><div class="bmi-result-card normal" id="age-result-card">'
    '<div class="bmi-value normal" id="age-bmi-value">—</div><div class="bmi-category" id="age-bmi-category">—</div>'
    '<div class="bmi-range" id="age-bmi-range">—</div></div>'
    '<div class="bmi-scale"><div class="bmi-scale-bar"><div class="bmi-scale-segment underweight">Under</div>'
    '<div class="bmi-scale-segment normal">Healthy</div><div class="bmi-scale-segment overweight">Over</div>'
    '<div class="bmi-scale-segment obese">Class 1</div><div class="bmi-scale-segment obese-severe">Class 2+</div>'
    '<div class="bmi-scale-marker" id="age-scale-marker"></div></div>'
    '<div class="bmi-scale-labels"><span>15</span><span>18.5</span><span>25</span><span>30</span><span>35</span><span>40</span></div></div>'
    '<div class="results-grid"><div class="result-item"><div class="result-item-label">Lowest healthy weight</div>'
    '<div class="result-item-value" id="age-healthy-min">—</div></div><div class="result-item"><div class="result-item-label">'
    'Highest healthy weight</div><div class="result-item-value" id="age-healthy-max">—</div></div></div>'
    '<div class="weight-range-box"><p id="age-weight-diff">—</p></div>'
    '<div class="rank-box" id="age-rank" hidden><div class="rank-title" id="age-rank-title">Compared with US adults your age</div>'
    '<div class="rank-value" id="age-rank-value">—</div><div class="rank-track" aria-hidden="true"><span class="rank-median">'
    '</span><span class="rank-marker" id="age-rank-marker"></span></div><div class="rank-axis" aria-hidden="true"><span>Lowest BMI'
    '</span><span id="age-rank-median">Median</span><span>Highest</span></div><p class="rank-text" id="age-rank-text"></p>'
    '<p class="rank-source" id="age-rank-source"></p></div>'
    '<div class="rank-box" id="age-typical" hidden><div class="rank-title" id="age-typical-title">US adults your age</div>'
    '<p class="rank-text" id="age-typical-text"></p><p class="rank-text" id="age-typical-mid"></p>'
    '<p class="rank-source">CDC NHANES 2021–2023, our calculation; the averages match NCHS’s published reference data.</p></div>'
    '</div></div></div>')


def arr(q): return '[' + ','.join(f'{x:g}' for x in q) + ']'


Q = '{' + ','.join(f'{s}:{{a:{arr(C[s])},y:{arr(C[s + "_20-39"])},m:{arr(C[s + "_40-59"])},o:{arr(C[s + "_60+"])}}}' for s in SEXES) + '}'
TYP = {s: {d: [f1(DEC[s][d]['mean']), f1(DEC[s][d]['p50']), f1(DEC[s][d]['p25']), f1(DEC[s][d]['p75']),
               f1(avg_wt(s, d)), f1(avg_kg(s, d)), f1(avg_in(s, d)), f1(avg_cm(s, d)), f1(DEC[s][d]['healthy']['pct'])]
           for d in AGES} for s in SEXES}
GM = {s: {k: MED[s][g] for k, g in zip('ymo', GRPS)} for s in SEXES}
GN = {s: {k: f'{NG[s][g]:,}' for k, g in zip('ymo', GRPS)} for s in SEXES}
SCRIPT = ('<script>(function(){var Q=' + Q + ',T=' + json.dumps(TYP, separators=(',', ':')) + ',M='
          + json.dumps(GM, separators=(',', ':')) + ',N=' + json.dumps(GN, separators=(',', ':')) + ',A='
          + json.dumps(MED_ALL, separators=(',', ':')) + ';' + r'''
var v=document.getElementById("age-bmi-value"),panel=document.getElementById("panel-age"),box=document.getElementById("age-rank"),typ=document.getElementById("age-typical");if(!v||!panel||!box||!typ)return;
function $(i){return document.getElementById(i);}
function pct(q,b){if(b<=q[0])return 0;if(b>=q[98])return 100;for(var i=0;i<98;i++){if(b<q[i+1])return i+1+(b-q[i])/(q[i+1]-q[i]);}return 100;}
function rk(q,b){return{lo:pct(q,Math.round(b*10-1)/10),hi:100-pct(q,b)};}
function n(x){return x>99?99:Math.round(x);}
function lab(r){return r.lo<1?"lower than "+n(r.hi)+"%":"higher than "+n(r.lo)+"%";}
function show(){var b=parseFloat(v.textContent),age=parseInt(panel.querySelector(".age-input").value,10),male=panel.querySelector(".sex-select").value==="male",s=male?"men":"women",S=male?"Men":"Women";
 if(!(b>0)||isNaN(age)||age<20){box.hidden=true;typ.hidden=true;return;}
 var g=age<40?"y":age<60?"m":"o",gw=age<40?"20 to 39":age<60?"40 to 59":"60 and over",r=rk(Q[s][g],b),t=b.toFixed(1),head=lab(r),txt,all=rk(Q[s].a,b);
 $("age-rank-title").textContent="Compared with US "+s+" aged "+gw;
 head=head.charAt(0).toUpperCase()+head.slice(1)+" of them";
 if(r.lo<1)txt="Your BMI of "+t+" is lower than about "+n(r.hi)+"% of US "+s+" aged "+gw+".";else if(r.hi<1)txt="Your BMI of "+t+" is higher than about "+n(r.lo)+"% of US "+s+" aged "+gw+".";else txt="Your BMI of "+t+" is higher than about "+n(r.lo)+"% of US "+s+" aged "+gw+" and lower than about "+n(r.hi)+"%.";
 txt+=" Among all US "+s+" aged 20 and over, it is "+lab(all).replace("than ","than about ")+". The median for "+s+" aged "+gw+" is "+M[s][g]+".";
 $("age-rank-value").textContent=head;$("age-rank-text").textContent=txt;$("age-rank-median").textContent="Median "+M[s][g];
 $("age-rank-source").textContent="CDC NHANES 2021–2023, "+N[s][g]+" "+s+" aged "+gw+" measured; our calculation.";
 $("age-rank-marker").style.left=Math.min(99,Math.max(1,r.lo))+"%";box.hidden=false;
 var d=age<30?"20-29":age<40?"30-39":age<50?"40-49":age<60?"50-59":age<70?"60-69":age<80?"70-79":"80+",dw=d==="80+"?"80 and over":d.replace("-"," to "),x=T[s][d],metric=panel.querySelector(".unit-btn.active").dataset.unit==="metric";
 var wt=metric?x[5]+" kg ("+x[4]+" lb)":x[4]+" lb ("+x[5]+" kg)",ws=metric?x[7]+" cm ("+x[6]+" in)":x[6]+" in ("+x[7]+" cm)";
 $("age-typical-title").textContent="US "+s+" aged "+dw;
 $("age-typical-text").textContent=S+" aged "+dw+" average a BMI of "+x[0]+", a weight of "+wt+" and a waist of "+ws+".";
 $("age-typical-mid").textContent="Their median BMI is "+x[1]+", and half of them have a BMI between "+x[2]+" and "+x[3]+". Of them, "+x[8]+"% have a BMI in the healthy range, 18.5 to 24.9, the same range at every adult age.";
 typ.hidden=false;}
new MutationObserver(show).observe(v,{childList:true,characterData:true,subtree:true});})();</script>''')

# ---------------------------------------------------------------- the page's own text
HEAD = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Get your BMI, the CDC category and how you compare with US adults of your sex and age, in pounds '
    'or kilograms.</p>'
    f'<p class="intro-note">CDC adult categories, the same at every age from 20. US comparison: CDC measurements of '
    f'{N["women"] + N["men"]:,} adults, 2021–2023. <a href="#sources">Method and sources</a></p></div>')

TAKEAWAYS = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer">BMI is worked out the same way at every age: weight in kilograms divided by height in meters '
    'squared, or pounds × 703 ÷ inches². <strong>From age 20, the categories don’t change with age</strong>: 18.5 to 24.9 '
    'is a healthy weight at 25 and at 75, 25 to 29.9 is overweight and 30 or more is obesity (CDC). Under 20, BMI is read '
    'as a percentile for age and sex.</p><ul>'
    f'<li><strong>What changes with age is the comparison.</strong> The median BMI of US women is {MED["women"]["20-39"]} at '
    f'ages 20 to 39, {MED["women"]["40-59"]} at 40 to 59 and {MED["women"]["60+"]} at 60 and over; of US men, '
    f'{MED["men"]["20-39"]}, {MED["men"]["40-59"]} and {MED["men"]["60+"]} (CDC measurements, 2021–2023). The calculator '
    'ranks you within your own age group.</li>'
    f'<li><strong>The average is above the healthy range:</strong> in every decade from the 20s to 80 and over, the average '
    f'BMI of US women and of US men is {min(LOW.values(), key=float)} or more, in the overweight range.</li>'
    '<li><strong>There is no separate range for seniors.</strong> The 23 to 29.9 that some senior calculators call normal '
    'isn’t CDC’s; the meta-analysis they cite describes risk of death, not a healthy range.</li>'
    '<li>Muscle mass tends to fall with age, so the same BMI can mean more body fat; the American Diabetes Association '
    'notes that this may lead to obesity being missed in older adults.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information only. '
    'BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

CHIPS = (('read-result', 'Your result'), ('by-age', 'By age group'), ('averages', 'US averages'),
         ('what-changes', 'What changes'), ('older-adults', '65 and over'), ('under-20', 'Under 20'), ('faq', 'FAQ'),
         ('sources', 'Sources'))
TOC = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

SEC_READ = (
    '<section id="read-result" class="content-section flow"><h2>How to read your result</h2>'
    f'<p>Every number below uses the calculator’s starting values: a {EX_AGE}-year-old woman, 5′6″ ({EX_CM} cm) and {EX_W} lb '
    f'({EX_KG} kg).</p><dl>'
    f'<dt>BMI: {EX_BMI}, overweight</dt><dd>{EX_W} × 703 ÷ {EX_H}² = {EX_BMI}, rounded to one decimal '
    f'({ext(U["cdc_formula"], "CDC formula")}); the category comes from that rounded number. CDC’s adult cut-offs are the same '
    'at every age from 20: under 18.5 underweight, 18.5 to 24.9 healthy, 25 to 29.9 overweight, 30 and above obesity.</dd>'
    f'<dt>Healthy weight at 5′6″: {HB_LB[0]}–{HB_LB[1]} lb ({HB_KG[0]}–{HB_KG[1]} kg)</dt><dd>The lightest and heaviest whole '
    'pounds at that height with a BMI of 18.5 to 24.9, and the same in whole kilograms. The range depends on height only, '
    'never on age.</dd>'
    f'<dt>Compared with US women aged 40 to 59: higher than {EXR["40-59"]}%</dt><dd>About {EXR["40-59"]}% of women aged 40 to '
    f'59, measured by CDC in 2021–2023, have a lower BMI and about {EXH}% a higher one. Her BMI is under the median for her age '
    f'group, {MED["women"]["40-59"]}, and still overweight. With the same height and weight at 25 she would rank higher than '
    f'about {EXR["20-39"]}% of women aged 20 to 39, and at 70 higher than about {EXR["60+"]}% of women 60 and over; the '
    f'category stays overweight at all three ages. A man of {EX_AGE} with the same numbers ranks higher than about {EX_MAN}% of '
    'men aged 40 to 59.</dd>'
    f'<dt>US women aged 40 to 49</dt><dd>Their average BMI is {EX_TYP[0]}, their average weight {EX_TYP[1]} lb ({EX_TYP[2]} kg) '
    f'and their average waist {EX_TYP[3]} in ({EX_TYP[4]} cm), CDC’s figures for her decade of age. An average describes US '
    'adults; it isn’t a target.</dd>'
    f'<dt>Weight milestones</dt><dd>The weight where each range starts at 5′6″: healthy from {HB_LB[0]} lb, overweight from '
    f'{FROM[25]} lb, obesity from {FROM[30]} lb, class 2 obesity from {FROM[35]} lb and class 3 from {FROM[40]} lb.</dd>'
    f'<dt>BMI Prime {EX_PRIME} and ponderal index {EX_PI} kg/m³</dt><dd>BMI Prime is your BMI divided by 25, where '
    'overweight starts. The ponderal index divides weight in kilograms by height in meters cubed; CDC’s adult categories use '
    'BMI, not this index.</dd>'
    '</dl></section>')


def pct_table(s):
    rows = ''.join(f'<tr><th scope="row">{lab_}</th>' + ''.join(f'<td class="num">{f1(G[f"{s}_{g}"][k])}</td>' for g in GRPS)
                   + '</tr>' for k, lab_ in PCT_ROWS)
    return ('<div class="table-responsive"><table class="data-table data-table--fit"><caption>BMI of US ' + s
            + ' by percentile and age group</caption><thead><tr><th scope="col">Percentile</th>'
            + ''.join(f'<th scope="col" class="num">{g.replace("-", "–")}</th>' for g in GRPS)
            + f'</tr></thead><tbody>{rows}</tbody></table></div>')


DEC_ROWS = ''.join(
    f'<tr><th scope="row">{d.replace("-", "–")}</th>' + ''.join(
        f'<td class="num">{f1(DEC[s][d]["p50"])}<span class="cell-kg">{f1(DEC[s][d]["p25"])}–{f1(DEC[s][d]["p75"])}</span></td>'
        for s in SEXES) + '</tr>' for d in AGES)
NDEC = sorted(DEC[s][d]['n'] for s in SEXES for d in AGES)
SEC_AGE = (
    '<section id="by-age" class="content-section flow"><h2>BMI by age group: US women and men</h2>'
    f'<p>CDC’s National Health and Nutrition Examination Survey (NHANES) weighed and measured {N["women"] + N["men"]:,} adults '
    'aged 20 and over from August 2021 to August 2023, pregnant women excluded. <strong>In every age group the median BMI was '
    f'above 25</strong>: for women {MED["women"]["20-39"]} at ages 20 to 39, {MED["women"]["40-59"]} at 40 to 59 and '
    f'{MED["women"]["60+"]} at 60 and over; for men {MED["men"]["20-39"]}, {MED["men"]["40-59"]} and {MED["men"]["60+"]}. '
    'The calculator ranks your BMI within your own group.</p>'
    f'<figure class="figure">{svg_age}<figcaption>BMI of US women and men by decade of age: the median (tick), the middle half '
    '(bar) and the 10th to 90th percentile (line), against CDC’s healthy range. CDC NHANES 2021–2023, our calculation.'
    '</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table data-table--fit"><caption>Median BMI of US adults by decade of '
    'age, with the middle half</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">Women<span '
    'class="th-sub">median, middle half</span></th><th scope="col" class="num">Men<span class="th-sub">median, middle half'
    f'</span></th></tr></thead><tbody>{DEC_ROWS}</tbody></table></div>'
    f'<p>In their 20s, {DH["women"]["20-29"]}% of women and {DH["men"]["20-29"]}% of men have a BMI in the healthy range; in '
    f'their 50s, {DH["women"]["50-59"]}% and {DH["men"]["50-59"]}% (each difference is larger than its margin of error).</p>'
    + pct_table('women') + pct_table('men') +
    f'<p>Read down a column: at ages 40 to 59, a quarter of men have a BMI of {f1(G["men_40-59"]["p25"])} or lower and a '
    f'quarter {f1(G["men_40-59"]["p75"])} or higher. In the rank, only people with a lower BMI count as below you and only '
    'those with a higher one as above you; people with the same BMI count on neither side.</p>'
    f'<p class="source-note">Source: our calculation from {ext(U["nhanes"], "CDC NHANES August 2021–August 2023")} measured '
    f'heights and weights, weighted with the exam weights: {NDEC[0]} to {NDEC[-1]} people in each decade; by age group, '
    f'{NG["women"]["20-39"]:,}, {NG["women"]["40-59"]:,} and {NG["women"]["60+"]:,} women and {NG["men"]["20-39"]:,}, '
    f'{NG["men"]["40-59"]:,} and {NG["men"]["60+"]:,} men. The women’s columns are the ones the '
    '<a href="/women-bmi-calculator/">BMI calculator for women</a> ranks against, so both pages give a woman the same '
    'answer.</p>'
    '</section>')


def avg_table(s):
    rows = ''.join(
        f'<tr><th scope="row">{d.replace("-", "–")}</th><td class="num">{DM[s][d]}</td>'
        f'<td class="num">{f1(avg_wt(s, d))} lb<span class="cell-kg">{f1(avg_kg(s, d))} kg</span></td>'
        f'<td class="num">{f1(avg_in(s, d))} in<span class="cell-kg">{f1(avg_cm(s, d))} cm</span></td></tr>' for d in AGES)
    return ('<div class="table-responsive"><table class="data-table data-table--fit"><caption>US ' + s + ': average BMI, '
            'weight and waist by age, 2021–2023</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">BMI</th>'
            '<th scope="col" class="num">Weight</th><th scope="col" class="num">Waist</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


SEC_AVG = (
    '<section id="averages" class="content-section flow"><h2>Average BMI, weight and waist by age</h2>'
    '<p>These averages are the ones NCHS publishes as reference data for August 2021 to August 2023, which our calculation '
    'from the same CDC files reproduces. <strong>In every decade the average BMI was 25 or higher</strong>, for women from '
    f'{LOW["women"]} to {HIGH["women"]} and for men from {LOW["men"]} to {HIGH["men"]}.</p>'
    + avg_table('women') + avg_table('men') +
    f'<p class="source-note">Source: {ext(U["s3"], S3_TITLE)} (Series 3, No. 50), which excludes pregnant women and gives '
    'weight in pounds and waist in centimeters; the kilograms and inches are converted from the same averages. Average weight by height: <a href="/average-weight/">average weight for men and women</a>.</p>'
    f'<p>Obesity (BMI 30 or higher) was most common in middle age: {DB["20-39"]}% of adults aged 20 to 39, {DB["40-59"]}% '
    f'at 40 to 59 and {DB["60+"]}% at 60 and over, a pattern seen in women and in men '
    f'({ext(U["db508"], "NCHS Data Brief 508")}). More detail: <a href="/us-obesity-statistics/">US obesity statistics</a>.</p>'
    '</section>')

SEC_CHANGE = (
    '<section id="what-changes" class="content-section flow"><h2>What changes with age, and what doesn’t</h2>'
    '<p><strong>The cut-offs don’t change.</strong> For everyone 20 and older, CDC bases the adult categories on BMI '
    f'“regardless of age, sex, or race” ({ext(U["cdc_cat"], "CDC")}), so a BMI of 25.0 is overweight at 25 and at 85.</p>'
    '<p><strong>Body composition does.</strong> Muscle mass decreases by about 3–8% per decade after age 30, and faster after '
    f'60 ({ext(U["volpi"], "Volpi et al., 2004")}), so the same BMI can mean more fat later in life. On CDC’s body scans, '
    f'average body fat was {BF["m"][0]}% for men in their 20s and {BF["m"][1]}% in their 50s, and {BF["f"][0]}% and '
    f'{BF["f"][1]}% for women (our calculation from {ext(U["dxx"], "NHANES 2011–2018")}; both differences are larger than '
    'their margins of error). These scans covered ages 8 to 59 only, so they don’t show older adults.</p>'
    '<p><strong>Height can change.</strong> BMI divides by height squared, so if your height drops, your BMI rises at the '
    f'same weight: going from 5′8″ to 5′6″ adds about {LOSS:.1f} points at a BMI of 25. Use your height as measured now.</p>'
    '<p><strong>The US averages differ by age.</strong> Average BMI was higher in the 40s and 50s than in the 20s, and lower '
    'at 80 and over than in the 50s, for women and for men (each difference is larger than its margin of error). These are '
    'different people measured in the same years, not the same people followed as they aged.</p>'
    '</section>')

SEC_OLD = (
    '<section id="older-adults" class="content-section flow"><h2>BMI at 65 and over</h2>'
    '<p>Some senior BMI calculators online class a BMI of 23 to 29.9 (or 23 to 30) as normal for adults over 65 and list the '
    'meta-analysis below among their sources. That range isn’t CDC’s: its adult categories have no upper age limit. In that '
    f'meta-analysis of 32 studies covering 197,940 people aged 65 and over, {WINTER}: an association, not a healthy range or '
    'a target.</p>'
    f'<p>US adults aged 70 to 79 have a median BMI of {D70["women"][0]} (women) and {D70["men"][0]} (men), and '
    f'{D70["women"][1]}% of the women and {D70["men"][1]}% of the men have a BMI of 18.5 to 24.9 (our calculation). The '
    'American Diabetes Association adds a caution for this age: “Loss of muscle mass in older adults reduces the accuracy of '
    f'BMI, which may lead to underdiagnosis of obesity” ({ext(U["ada"], "ADA, 2026")}). A waist measurement shows what BMI '
    'can’t: the <a href="/blog/waist-to-height-ratio/">waist-to-height ratio guide</a> explains how to take it.</p>'
    '</section>')

SEC_KIDS = (
    '<section id="under-20" class="content-section flow"><h2>Under 20: BMI-for-age percentiles</h2>'
    '<p>Children and teens get the same formula but not the adult categories. CDC compares their BMI with growth charts for '
    'the same age and sex and reads it as a percentile: under the 5th is underweight, the 5th to below the 85th healthy '
    f'weight, the 85th to below the 95th overweight, and the 95th or above obesity ({ext(U["cdc_child"], "CDC")}). The same '
    f'number means different things at different ages: a BMI of {GIRL["bmi"]} is in the adult healthy range, but for a '
    f'{GIRL["years"]}-year-old girl it sits at the {GIRL["ordinal"]}th percentile, which is obesity.</p>'
    '<p>This calculator starts at 20. For ages 2 to 19, the <a href="/kids-bmi-calculator/">BMI calculator for children and '
    'teens</a> takes the age in years and months.</p>'
    '</section>')

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask on the 2026-11-14 SERPs ("bmi calculator by age", "bmi calculator kg with age", "bmi calculator women
# age"), each question once, in the words of the box; then the old page's height question.
FAQ = [
    ('What is the correct BMI for my age?',
     'For adults, the same at every age: CDC calls 18.5 to 24.9 a healthy weight from age 20 on, “regardless of age, sex, or '
     f'race” ({ext(U["cdc_cat"], "CDC")}). Under 20, BMI is read as a percentile for age and sex instead. Among US adults the '
     f'median BMI is {MED["women"]["20-39"]} for women and {MED["men"]["20-39"]} for men at ages 20 to 39, '
     f'{MED["women"]["40-59"]} and {MED["men"]["40-59"]} at 40 to 59, and {MED["women"]["60+"]} for both at 60 and over (our '
     'calculation from CDC measurements, 2021–2023), so the typical BMI at every adult age is above the healthy range.'),
    ('What is a good BMI for a senior over 70?',
     'CDC’s healthy range, 18.5 to 24.9, has no upper age limit. Some senior calculators online class 23 to 29.9 as normal '
     'after 65; that range isn’t CDC’s, and the meta-analysis they cite describes risk of death, not a healthy range: '
     f'{WINTER}. US adults aged 70 to 79 have a median BMI of {D70["women"][0]} (women) and {D70["men"][0]} (men).'),
    ('How to calculate BMI for seniors?',
     'The same way as at any adult age: weight in kilograms divided by height in meters squared, or pounds × 703 ÷ '
     f'inches² ({ext(U["cdc_formula"], "CDC")}). Use your height as measured now: if you have lost height, the same weight '
     'gives a higher BMI. Muscle mass tends to fall with age, so the same BMI can mean more body fat; the American Diabetes '
     f'Association notes that this may lead to obesity being missed in older adults ({ext(U["ada"], "ADA, 2026")}).'),
    ('How to calculate BMI including age?',
     'Age isn’t part of the formula. From 20 it changes only the comparison: this calculator ranks your BMI among US adults '
     'of your sex in your age group and gives the averages for your decade. Under 20, age matters more: CDC reads a child’s '
     'BMI as a percentile for age in months and sex, which the <a href="/kids-bmi-calculator/">BMI calculator for children '
     'and teens</a> works out.'),
    ('What is the ideal BMI for females by age?',
     'CDC uses one healthy range for women of every adult age: 18.5 to 24.9. What changes with age is how US women measure: '
     f'the median BMI is {MED["women"]["20-39"]} at ages 20 to 39, {MED["women"]["40-59"]} at 40 to 59 and '
     f'{MED["women"]["60+"]} at 60 and over (our calculation, 2021–2023). The '
     '<a href="/women-bmi-calculator/">BMI calculator for women</a> adds a waist check.'),
    ('What is the average BMI by age?',
     f'In CDC’s 2021–2023 measurements the average BMI ranged from {LOW["men"]} to {HIGH["men"]} for men and from '
     f'{LOW["women"]} to {HIGH["women"]} for women across the decades from the 20s to 80 and over, so every decade averaged '
     'in the overweight range or above. The tables above give each decade, with the average weight and waist.'),
    ('Does losing height change my BMI?',
     'Yes. BMI divides weight by height squared, so a lower height gives a higher BMI at the same weight: going from 5′8″ to '
     f'5′6″ adds about {LOSS:.1f} points at a BMI of 25. Use your height as measured now, not the height you had at 25.'),
    ('Is BMI less accurate for older adults?',
     'It can be. BMI doesn’t measure body fat, and muscle mass decreases by about 3–8% per decade after age 30, faster '
     f'after 60 ({ext(U["volpi"], "Volpi et al., 2004")}), so an older adult can carry more fat at the same BMI. On CDC’s body '
     f'scans, average body fat was {BF["m"][0]}% for men in their 20s and {BF["m"][1]}% in their 50s; for women, {BF["f"][0]}% '
     f'and {BF["f"][1]}% (our calculation, NHANES 2011–2018). A waist measurement adds what BMI can’t show.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')

SOURCES = [
    f'CDC NHANES August 2021–August 2023 {ext(U["nhanes"], "demographics and body measures files")} (DEMO_L, BMX_L): our '
    f'calculation for {N["women"]:,} women and {N["men"]:,} men aged 20 and over (BMI percentiles by age group and by '
    'decade, shares in the healthy range).',
    f'Fryar CD, et al. {ext(U["s3"], "Anthropometric Reference Data for Children and Adults: United States, August 2021–August 2023")} '
    '(NCHS, Vital and Health Statistics Series 3, No. 50, 2025): the average BMI, weight and waist by decade.',
    f'Emmerich SD, et al. {ext(U["db508"], DB508_TITLE)} (NCHS Data Brief No. 508, 2024): obesity by age group.',
    f'CDC NHANES 2011–2018 {ext(U["dxx"], "whole-body DXA scans")}: our calculation of average body fat by decade, ages 20 to '
    '59 (the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> has the method).',
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the cut-offs and the “regardless of age, sex, or race” rule.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formula in US and metric units.',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles under 20.',
    f'Winter JE, et al. {ext(U["winter"], "BMI and all-cause mortality in older adults: a meta-analysis")} (Am J Clin Nutr, '
    '2014).',
    f'Volpi E, et al. {ext(U["volpi"], "Muscle tissue changes with aging")} (Curr Opin Clin Nutr Metab Care, 2004).',
    'American Diabetes Association Professional Practice Committee for Obesity. '
    f'{ext(U["ada"], "Screening, Diagnosis, Evaluation, and Staging of Obesity in Adults: Standards of Care in Overweight and Obesity—2026")}: '
    'the note on older adults.',
]
SEC_SRC = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Adults aged 20 and over with a measured height and weight in NHANES '
    'August 2021–August 2023, pregnant women excluded, weighted with CDC’s exam weights. Percentiles come from the weighted '
    'distribution of the measured BMIs (one weight per distinct BMI, straight lines in between), the method that reproduces '
    'NCHS’s published medians; the rank reads your BMI off the 1st to 99th percentiles of your sex and age group (20 to 39, '
    '40 to 59, 60 and over), stored to four decimals. Shares and means carry 95% confidence intervals from Taylor '
    'linearization over the survey’s 15 strata, and the page states a difference between ages only when its interval '
    'excludes zero. NHANES records ages over 79 as 80, so the last decade is 80 and over. Every figure is rounded once, from '
    'the unrounded estimate. The calculator takes ages 20 and over; at 2 to 19 it sends you to the children’s calculator.</p>'
    '</section>')

SEC_REL = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/kids-bmi-calculator/', 'BMI calculator for children and teens'),
        ('/body-fat-calculator/', 'Body fat calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/blog/bmi-by-age/', 'BMI by age'), ('/average-weight/', 'Average weight by height'),
        ('/body-fat-percentage-chart/', 'Body fat percentage chart'), ('/blog/bmi-and-health-risks/', 'BMI and health risks'),
        ('/blog/bmi-limitations/', 'Limitations of BMI')))
    + '</ul></div></div></section>')


def nbsp_units(markup):
    """A number keeps its unit on one line (DEVLOG §4, CMB-021): a no-break space between them, in text only."""
    unit = re.compile(r'(\d) (lb|lbs|kg|cm|in|inches|feet|points)(?![\w])')
    out = []
    for chunk in re.split(r'(?s)(<svg\b.*?</svg>|<script>.*?</script>)', markup):
        out.append(chunk if chunk.startswith(('<svg', '<script')) else
                   ''.join(p if p.startswith('<') else unit.sub('\\1\u00a0\\2', p) for p in re.split(r'(<[^>]+>)', chunk)))
    return ''.join(out)


FAQ = [(q, nbsp_units(a)) for q, a in FAQ]
FAQ_HTML = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p>'
                   '</div></div>' for q, a in FAQ)
SEC_FAQ = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{FAQ_HTML}'
           '</div></section>')

MAIN = nbsp_units('<main class="reading"><div class="container">' + ''.join(
    [HEAD, CALC, TAKEAWAYS, TOC, SEC_READ, SEC_AGE, SEC_AVG, SEC_CHANGE, SEC_OLD, SEC_KIDS, SEC_FAQ, SEC_SRC, SEC_REL])
    + SCRIPT + '</div></main>')
assert all(f'id="{a}"' in MAIN for a, _ in CHIPS)
assert 'style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', MAIN), 'no inline style in <main>'
for bad in ('plateau', 'lowest mortality', 'lowest all-cause', '23–33', '23-33', 'WHO adult range', '—</p></div></div>',
            'obesity paradox', 'Obesity Paradox', 'rose above 33'):
    assert bad not in re.sub(r'(?s)<script>.*?</script>', '', MAIN).replace('id="age-weight-diff">—</p>', ''), bad


def faq_text(a):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', a)).replace('\u00a0', ' ')).strip()


DESC = ('BMI calculator by age and gender in kg or lbs: your BMI, the CDC category and how you compare with US women or men '
        'your age, plus US averages by age.')
OG_T = 'BMI Calculator by Age & Gender: compare with US adults your age'
OG_D = (f'Your BMI and CDC category, ranked among US women or men in your age group, from CDC’s measurements of '
        f'{N["women"] + N["men"]:,} adults, with average BMI, weight and waist by decade of age.')
OG_ALT = ('Chart: the BMI of US women and men in each decade of age from their 20s to 80 and over, against the healthy '
          'range.')
assert len(DESC) <= 160 and '"' not in OG_ALT + OG_D + OG_T + DESC, len(DESC)

LD = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE_TEXT,
     'isPartOf': {'@id': SITE + '/#website'}, 'mainEntity': {'@id': URL + '#calculator'},
     'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG['16x9'], 'width': 1200, 'height': 675}},
    {'@type': 'WebApplication', '@id': URL + '#calculator', 'image': [IMG['1x1'], IMG['4x3'], IMG['16x9']], 'name': H1,
     'description': ('Calculates BMI for adults aged 20 and over from height and weight in pounds and inches or kilograms and '
                     'centimeters, gives the CDC adult category and the healthy weight range for the height, ranks the result '
                     'among US women or men aged 20 to 39, 40 to 59 or 60 and over using CDC NHANES August 2021–August 2023 '
                     'measurements, and shows the average BMI, weight and waist for the same sex and decade of age.'),
     'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any',
     'browserRequirements': 'Requires JavaScript', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
     'featureList': ['BMI from US or metric units', 'CDC adult BMI category, the same at every age from 20',
                     'Healthy weight range for your height in pounds and kilograms',
                     'Rank among US women or men in your age group (CDC NHANES 2021–2023)',
                     'Average BMI, weight and waist for your sex and decade of age (NCHS reference data)'],
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
    head, rest = src.split('</head>', 1)
    assert f'<title>{TITLE}</title>' in head and head.count('<title>') == 1, 'the title changed (D-28)'
    head = put_meta(head, 'name', 'description', DESC)
    head = put_meta(head, 'property', 'og:title', OG_T)
    head = put_meta(head, 'property', 'og:description', OG_D)
    head = put_meta(head, 'property', 'og:image', IMG['16x9'])
    head = put_meta(head, 'property', 'og:image:alt', OG_ALT, after=('property', 'og:image'))
    head = put_meta(head, 'property', 'og:image:width', '1200')
    head = put_meta(head, 'property', 'og:image:height', '675')
    head = put_meta(head, 'name', 'twitter:title', OG_T)
    head = put_meta(head, 'name', 'twitter:description', OG_D)
    head = put_meta(head, 'name', 'twitter:image', IMG['16x9'])
    blocks = list(re.finditer(r'(?s)[ \n]?<script type="application/ld\+json">.*?</script>', head))
    assert blocks, 'no JSON-LD in the head'
    ld = '\n<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>'
    head = head[:blocks[0].start()] + ld + ''.join(head[a.end():b.start()] for a, b in zip(blocks, blocks[1:])) + head[blocks[-1].end():]
    body = re.sub(r'(?s)<main\b.*?</main>', lambda _: MAIN, rest, count=1)
    return head + '</head>' + body


def words(markup):
    m = re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>|<table.*?</table>', ' ', markup)
    return len(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m))).split())


if __name__ == '__main__':
    src = open(PAGE, encoding='utf-8').read()
    out = build(src)
    assert build(out) == out, 'not idempotent'
    with open(PAGE, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    print(f'{PAGE}: {len(out):,} bytes; <main> {len(MAIN):,} bytes, about {words(MAIN):,} words outside tables and the '
          f'figure; {len(FAQ)} FAQ; {len(TEXTS)} SVG labels checked; example ranks {EXR}, higher {EXH}, all women {EX_ALL}, '
          f'man {EX_MAN}')
