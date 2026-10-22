#!/usr/bin/env python3
"""CMB-017 WOMEN-CALC: rebuilds /women-bmi-calculator/ to the D-14 calculator pattern (DESIGN.md; the homepage and
/men-bmi-calculator/ applied it): tool first, answer block and key takeaways, contents chips, a worked example, real
tables and figures, a flat FAQ whose JSON-LD equals the visible answers, sources and method, one related block, one
680 px reading column.

Wedge (owner's SERP pastes of 2026-10-22, US/English, not personalized: "bmi calculator women", "bmi calculator female",
"bmi calculator for older women"): every result is a bare calculator (CDC, NHLBI, Calculator.net, ACS, AARP, Harvard,
Hers, Mayo, Omni). None places a woman among US women of her age, none applies the June 2026 waist rule to her own waist,
and none says what body fat goes with her BMI. This page does all three:
  1. rank among US women aged 20+ and in three age groups (NHANES 2021-2023, wbc_stats.py; the all-women curve is the
     homepage's, so both pages rank a woman the same way);
  2. an optional waist field and a waist check (NHLBI 1998, NICE NG246, ADA Standards of Care in Overweight and Obesity
     2026, non-Asian and Asian lines shown when they differ);
  3. "US women with a BMI like yours": body fat on CDC's DXA scans at that whole BMI (research/body-fat-chart-build/
     bfpc_stats.json) and the share with a large waist in that BMI category (research/chart-women-build/bcw_stats.json).

Every number comes from wbc_stats.json, bcw_stats.json, bfpc_stats.json, home_stats.json, the weight-table gate's rule
(scripts/check_weight_tables.py) or a source verified in chat (constants below, each with its source). Round once: a
printed figure is formatted from the unrounded (4-decimal) value or from a value its source rounded once.

usage: python3 gen_wbc.py REPO_ROOT STATS_JSON
Runs once, on women-bmi-calculator/index.html as it stood at 9bf7429; kept as the build record.
"""
import sys, os, re, json, html, math
from decimal import Decimal, ROUND_HALF_UP

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
BCW = json.load(open(os.path.join(ROOT, 'research/chart-women-build/bcw_stats.json')))
BFP = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
HOME = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
PAGE = os.path.join(ROOT, 'women-bmi-calculator/index.html')
src = open(PAGE, encoding='utf-8').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds

SITE = 'https://calculatemybmi.net'
URL = SITE + '/women-bmi-calculator/'

# ---------------------------------------------------------------- numbers
def f1(x): return f'{x:.1f}'
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10            # calculator.js round1()
def r2(x): return math.floor(x * 100 + 0.5 + 1e-9) / 100
def cut2(x): return math.floor(x * 100 + 1e-9) / 100                # the waist check's ratio: cut, never rounded up
def dcm(inches): return str((Decimal(str(inches)) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))  # exact, half up

def pct(q, b):
    """The page script's pct(): the share of women at or below b, read from the 1st-99th percentile curve."""
    if b <= q[0]: return 0.0
    if b >= q[98]: return 100.0
    for i in range(98):
        if b < q[i + 1]: return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0
def lower(q, b): return pct(q, round(b - 0.1, 1))                  # strictly lower BMI (US rank rule, CMB-012)
def higher(q, b): return 100 - pct(q, b)                           # strictly higher BMI
def nn(x): return 99 if x > 99 else int(math.floor(x + 0.5))       # the script's n(): Math.round, capped at 99
def lab(q, b):
    lo, hi = lower(q, b), higher(q, b)
    return f'lower than {nn(hi)}%' if lo < 1 else f'higher than {nn(lo)}%'

C = S['curves']; T = S['table']; DEC = S['decades']; DD = S['decade_differences']
QA, QY, QM, QO = C['all'], C['20-39'], C['40-59'], C['60+']
assert QA == HOME['women']['p1_p99']                               # the homepage's women-only curve
N_ALL, N_Y, N_M, N_O = T['all']['n'], T['20-39']['n'], T['40-59']['n'], T['60+']['n']
assert (N_ALL, N_Y, N_M, N_O) == (3249, 826, 947, 1476)
MED = f1(T['all']['p50']); assert MED == '28.3' and f1(T['all']['p25']) == '24.1'
CAT = BCW['categories']
HEALTHY_ALL, OB_ALL = CAT['all_ages']['healthy']['pct'], CAT['all_ages']['obesity']['pct']
assert (HEALTHY_ALL, OB_ALL) == (28.1, 41.3)
WS = BCW['waist']['by_bmi']
WSH = {c: (WS[c]['waist_88_plus']['pct'], WS[c]['whtr_05_plus']['pct']) for c in ('healthy', 'overweight', 'obesity')}
assert WSH['healthy'] == (16.8, 50.2) and WSH['overweight'] == (79.1, 95.5) and WSH['obesity'] == (99.2, 100.0)
N_WAIST = BCW['waist']['n_measured']; assert N_WAIST == 3113
ADA = BCW['ada2026']
ADA_OB, ADA_BMI, ADA_N = ADA['obesity_ada']['pct'], ADA['obesity_bmi_only']['pct'], ADA['n']
assert (ADA_OB, ADA_BMI, ADA_N) == (69.4, 41.8, 3216)
# Decades: each difference the page states has a 95% CI that excludes 0 (NHANES comparison rule).
DM = {d: f1(DEC[d]['mean']) for d in DEC}
assert [DM[d] for d in ('20-29', '50-59', '70-79', '80+')] == ['28.0', '31.4', '29.5', '27.7']
for k in ('mean_50-59_minus_20-29', 'mean_70-79_minus_50-59', 'mean_80+_minus_70-79', 'mean_80+_minus_50-59',
          'healthy_20-29_minus_50-59'):
    assert DD[k]['excludes_0'], k
DH = {d: f1(DEC[d]['healthy']['pct']) for d in DEC}
assert (DH['20-29'], DH['50-59'], DH['70-79']) == ('40.6', '23.3', '25.7')
MAX_MOE = max(max(DEC[d]['healthy']['ci95'][1] - DEC[d]['healthy']['pct'], DEC[d]['healthy']['pct'] - DEC[d]['healthy']['ci95'][0])
              for d in DEC)
assert 9.5 <= MAX_MOE <= 10.5, MAX_MOE                             # "up to about 10 points"

# Body fat at each whole BMI, women 20-59 (CDC DXA 2011-2018): the bins the body fat chart draws (n >= 50).
BIN = BFP['bmi']['by_bin']['f']
BF_BINS = {int(b): [f1(v['p25']), f1(v['p50']), f1(v['p75'])] for b, v in BIN.items() if v.get('n', 0) >= 50}
assert min(BF_BINS) == 18 and max(BF_BINS) == 45 and len(BF_BINS) == 28   # 45 = "45 or more"
BC = BFP['bmi']['by_cat']
BF_CAT = {k: {c: (f1(BC[k][c]['p50']), f1(BC[k][c]['p25']), f1(BC[k][c]['p75'])) for c in BC[k]} for k in BC}
assert BF_CAT['f']['healthy'] == ('33.4', '29.8', '36.5') and BF_CAT['m']['healthy'] == ('22.1', '18.6', '25.0')
assert BF_CAT['f']['over'][0] == '39.5' and BF_CAT['f']['obese'][0] == '44.0'

# Worked example: the calculator's starting values, 5'4" and 140 lb (63.5 kg), with a 33-inch waist.
EX_H, EX_W, EX_WAIST = 64, 140, 33
EX_BMI = r1(EX_W * 703 / EX_H ** 2)
HB_LB, HB_KG = gate_bounds('lb', EX_H, EX_H * 2.54, 1), gate_bounds('kg', EX_H, EX_H * 2.54, 1)
assert EX_BMI == 24.0 and HB_LB == (108, 145) and HB_KG == (49, 65)
OVER_FROM = gate_bounds('lb', EX_H, EX_H * 2.54, 2)[0]
FROM = {c: gate_bounds('lb', EX_H, EX_H * 2.54, i)[0] for c, i in ((25, 2), (30, 3), (35, 4), (40, 5))}
assert OVER_FROM == 146 and FROM == {25: 146, 30: 175, 35: 204, 40: 233}, FROM
EX_RANK = {g: lower(q, EX_BMI) for g, q in (('all', QA), ('y', QY), ('m', QM), ('o', QO))}
EX_R = {g: nn(v) for g, v in EX_RANK.items()}
EX_HI = nn(higher(QA, EX_BMI))
EX_CM, EX_KG = f1(EX_H * 2.54), f1(EX_W / 2.20462)
assert (EX_CM, EX_KG) == ('162.6', '63.5')
EX_PRIME = '0.96'                                                   # bmiPrime(24.0) = Math.round(24.0 * 4) / 100
EX_PI = f'{(EX_W / 2.20462) / ((EX_H * 2.54 / 100) ** 3):.1f}'     # genKeyMetrics(): kg / m^3, toFixed(1)
EX_WCM = dcm(EX_WAIST)
EX_RAW = EX_WAIST / EX_H                                            # 0.515625
EX_RATIO = cut2(EX_RAW)                                             # shown as 0.51 (cut to two decimals)
assert (EX_WCM, EX_RATIO, f'{EX_RAW:.3f}') == ('83.8', 0.51, '0.516')
EX_BIN = BF_BINS[24]
assert EX_BIN == ['33.6', '36.1', '38.7']

# PAA heights (healthy range in whole pounds and kilograms, each worked out on its own).
def hb(h): return gate_bounds('lb', h, h * 2.54, 1), gate_bounds('kg', h, h * 2.54, 1)
B62, B65 = hb(62), hb(65)
assert B62 == ((101, 136), (46, 61)) and B65 == ((111, 149), (51, 68)), (B62, B65)
P62_W = 130; P62_BMI = r1(P62_W * 703 / 62 ** 2); assert P62_BMI == 23.8
P62_R = nn(lower(QA, P62_BMI))
P140_HI = nn(higher(QA, 24.0))

# Older women.
D70 = DEC['70-79']; assert (f1(D70['p50']), D70['n']) == ('28.0', 493)

# ---------------------------------------------------------------- sources verified in chat
# CDC Adult BMI Categories (read 2026-10-22): "For adults 20 and older, BMI categories are based on a person's BMI
#   regardless of age, sex, or race."; healthy weight "18.5 to less than 25"; class 3 "40 or greater"; dated March 19, 2024.
# CDC Weight Gain During Pregnancy (read 2026-10-22): one baby, BMI before pregnancy: under 18.5 28-40 lb, 18.5-24.9 25-35
#   lb, 25.0-29.9 15-25 lb, 30.0-39.9 11-20 lb; "All recommendations are from the Institute of Medicine, with the exception
#   of underweight women with twins."
# NHLBI 1998 (registry nhlbi-1998-obesity-guidelines): waist over 35 in (88 cm) for women, "in conjunction with BMI" at 25
#   to 34.9.
# NICE NG246 (registry nice-ng246-ethnicity-thresholds, checked 2026-10-15): waist-to-height ratio for adults with a BMI
#   under 35: 0.4-0.49 healthy central adiposity, 0.5-0.59 increased, 0.6 or more high, "both sexes and all ethnicities";
#   overweight 23-27.4 and obesity 27.5+ for South Asian, Chinese, other Asian, Middle Eastern, Black African or
#   African-Caribbean backgrounds (a 2022 recommendation).
# ADA 2026 (registry ada-2026-obesity-standards; recommendations 3.3a/3.3b): non-Asian: BMI >= 30, or >= 25 with WHtR >=
#   0.5 or waist >= 88 cm (women); Asian: >= 27.5, or >= 23 with WHtR >= 0.5 or waist >= 80 cm (women); nonpregnant adults;
#   "Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to underdiagnosis of obesity".
# CDC National DPP eligibility (registry cdc-ndpp-eligibility): BMI 25 or higher, 23 or higher for Asian American adults.
# WHO 2004 (registry who-2004-asian-bmi): international categories kept; 23, 27.5, 32.5 and 37.5 as "potential public
#   health action points" for Asian populations (abstract wording).
# Winter et al. 2014 (registry winter-2014-bmi-mortality-65; abstract re-read 2026-10-22 on a University of Queensland
#   copy): 197,940 people aged 65 and over; reference BMI 23.0-23.9; 12% greater risk at 21.0-21.9; "Mortality risk began
#   to increase for BMI >33.0"; conclusion: "the risk of mortality increased in older people with a BMI <23.0".
# Senior BMI calculators online (read 2026-10-22; not named on the page): omnicalculator.com/health/geriatric-bmi classes
#   "23-29.9" as "Normal" for adults over 65 (sources: Winter et al. 2014; Porter Starr and Bales 2015);
#   vanswefitness.com/pages/bmi-calculator-for-seniors gives "between 23 and 30" (sources: Kiskac et al. 2022; Winter et
#   al. 2014). Both cite Winter et al. 2014.
# NCHS Series 3 No. 50 (registry nhanes-anthropometric-reference; read 2026-10-22): Fryar CD et al., "Anthropometric
#   Reference Data for Children and Adults: United States, August 2021-August 2023", June 2025; "Pregnant females were
#   excluded from the tabulations of weight, body mass index (BMI), and circumference measurements." The decade means and
#   medians here equal its Table 10.

# ---------------------------------------------------------------- text helpers
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_formula': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_preg': 'https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
    'nhanes': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2004/',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'ada': 'https://doi.org/10.2337/doci26-0003',
    'ndpp': None,
    'who2004': 'https://pubmed.ncbi.nlm.nih.gov/14726171/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    's3': None,
}
import csv
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    if r['domain'] == 'cdc-ndpp-eligibility': U['ndpp'] = r['url']
    if r['domain'] == 'nhanes-anthropometric-reference': U['s3'] = r['url']
assert U['ndpp'] and U['s3'], 'registry rows cdc-ndpp-eligibility and nhanes-anthropometric-reference'

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS, VBW = [], [], {}

def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827'):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'

def rect(svg, x, y, w, h, fill, extra='', tip=None, track=True):
    if track: RECTS.append((svg, x, y, x + w, y + h))
    t = f'<title>{esc(tip)}</title>' if tip else ''
    tag = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}'
    return f'{tag}>{t}</rect>' if t else f'{tag}/>'

BASE = {'under': '#3b82f6', 'healthy': '#22c55e', 'over': '#f59e0b', 'obese': '#ef4444', 'severe': '#991b1b'}
INK, MUTED, GRID, SER = '#1f2937', '#4b5563', '#e5e7eb', '#be185d'

# Figure 1: the worked example (formula, the BMI scale with the marker, the weight bar at 5'4").
VBW['ex'] = 300
fx = []
fx.append(text('ex', 150, 22, f'{EX_W} lb × 703 ÷ {EX_H}² = {EX_BMI}', 17, weight=700, fill='#111827'))
fx.append(text('ex', 150, 44, f'{EX_H} in ({EX_CM} cm), {EX_W} lb ({EX_KG} kg)', 14, fill=MUTED))
SX0, SX1, SLO, SHI = 10, 290, 15, 40
def sx(b): return SX0 + (min(max(b, SLO), SHI) - SLO) * (SX1 - SX0) / (SHI - SLO)
for lo, hi, k in ((15, 18.5, 'under'), (18.5, 25, 'healthy'), (25, 30, 'over'), (30, 35, 'obese'), (35, 40, 'severe')):
    fx.append(rect('ex', sx(lo), 84, sx(hi) - sx(lo), 18, BASE[k], track=False))
fx.append(f'<line x1="{sx(EX_BMI):.1f}" y1="78" x2="{sx(EX_BMI):.1f}" y2="108" stroke="#111827" stroke-width="3"/>')
fx.append(text('ex', sx(EX_BMI), 72, f'BMI {EX_BMI}: healthy weight', 15, weight=700))
for b in (18.5, 25, 30, 35):
    fx.append(text('ex', sx(b), 124, f'{b:g}', 14, fill=MUTED))
fx.append(text('ex', 10, 160, f'Healthy at 5′4″: {HB_LB[0]}–{HB_LB[1]} lb', 15, anchor='start', weight=600))
WX0, WX1, WLO, WHI = 10, 290, 90, 190
def wx(lb): return WX0 + (lb - WLO) * (WX1 - WX0) / (WHI - WLO)
fx.append(f'<rect x="{WX0}" y="192" width="{WX1 - WX0}" height="16" rx="8" fill="{GRID}"/>')
fx.append(f'<rect x="{wx(HB_LB[0]):.1f}" y="192" width="{wx(HB_LB[1]) - wx(HB_LB[0]):.1f}" height="16" fill="#86efac"/>')
fx.append(f'<line x1="{wx(EX_W):.1f}" y1="186" x2="{wx(EX_W):.1f}" y2="214" stroke="#111827" stroke-width="3"/>')
fx.append(f'<path d="M{wx(EX_W) + 2:.1f} 188 V182 H{wx(OVER_FROM):.1f} V188" fill="none" stroke="#111827" stroke-width="1.5"/>')
fx.append(text('ex', (wx(EX_W) + wx(OVER_FROM)) / 2 + 22, 176, f'{OVER_FROM - EX_W} lb to overweight', 13, fill=INK))
fx.append(text('ex', wx(HB_LB[0]), 232, f'{HB_LB[0]} lb', 14, fill='#374151'))
fx.append(text('ex', wx(EX_W) - 16, 232, f'{EX_W}', 14, weight=700))
fx.append(text('ex', wx(HB_LB[1]) + 14, 232, f'{HB_LB[1]}', 14, fill='#374151'))
svg_ex = ('<svg viewBox="0 0 300 240" role="img" aria-labelledby="ex-t ex-d" xmlns="http://www.w3.org/2000/svg" '
          f'font-family="inherit"><title id="ex-t">Worked example: 5 feet 4 inches and 140 pounds gives a BMI of {EX_BMI}</title>'
          f'<desc id="ex-d">140 times 703 divided by 64 squared equals {EX_BMI}. On the BMI scale from 15 to 40 the marker sits in '
          f'the healthy range, below 25. On a weight bar for 5 feet 4 inches, the healthy range runs from {HB_LB[0]} to '
          f'{HB_LB[1]} pounds; 140 pounds sits inside it, {OVER_FROM - EX_W} pounds below where overweight starts at '
          f'{OVER_FROM}.</desc>' + ''.join(fx) + '</svg>')

# Figure 2: BMI of US women by decade (10th-90th line, middle-half bar, median tick) over CDC's healthy range.
AGES = ('20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')
AW, AX0, AX1, AY0 = 320, 52, 304, 46
ROWH = 28
def ax(b): return AX0 + (b - 15) * (AX1 - AX0) / 30.0                # BMI 15 to 45
VBW['age'] = AW
fa = []
fa.append(rect('age', ax(18.5), AY0 - 10, ax(25) - ax(18.5), ROWH * len(AGES) + 8, '#dcfce7', track=False))
fa.append(text('age', (ax(18.5) + ax(25)) / 2, AY0 - 16, 'Healthy 18.5–24.9', 12, fill='#15803d'))
for b in (20, 25, 30, 35, 40, 45):
    x = ax(b)
    fa.append(f'<line x1="{x:.1f}" y1="{AY0 - 10}" x2="{x:.1f}" y2="{AY0 + ROWH * len(AGES) - 2}" stroke="{GRID}" stroke-width="1"/>')
for i, d in enumerate(AGES):
    v = DEC[d]; yc = AY0 + i * ROWH + 8
    fa.append(text('age', 0, yc + 4, d.replace('-', '–'), 12, anchor='start', fill=INK))
    tip = (f'Women {d.replace("-", " to ").replace("+", " and over")}: median BMI {f1(v["p50"])}, middle half {f1(v["p25"])}–'
           f'{f1(v["p75"])}, 10th to 90th percentile {f1(v["p10"])}–{f1(v["p90"])} ({v["n"]:,} women)')
    fa.append(f'<line x1="{ax(v["p10"]):.1f}" y1="{yc}" x2="{ax(v["p90"]):.1f}" y2="{yc}" stroke="{SER}" stroke-width="1.5"/>')
    fa.append(rect('age', ax(v['p25']), yc - 6, ax(v['p75']) - ax(v['p25']), 12, SER, extra=' fill-opacity="0.35" rx="2"', tip=tip))
    fa.append(f'<line x1="{ax(v["p50"]):.1f}" y1="{yc - 8}" x2="{ax(v["p50"]):.1f}" y2="{yc + 8}" stroke="#111827" stroke-width="2.5"/>')
AXY = AY0 + ROWH * len(AGES) + 12
for b in (20, 25, 30, 35, 40, 45):
    fa.append(text('age', ax(b), AXY, f'{b}', 12, fill=MUTED))
fa.append(text('age', (AX0 + AX1) / 2, AXY + 18, 'BMI', 12, fill=INK))
AH = AXY + 26
svg_age = (f'<svg viewBox="0 0 {AW} {AH}" role="img" aria-labelledby="age-t age-d" xmlns="http://www.w3.org/2000/svg" '
           'font-family="inherit"><title id="age-t">BMI of US women by age</title>'
           '<desc id="age-d">For each decade of age, the median BMI of US women and the middle half, against CDC’s healthy '
           'range of 18.5 to 24.9. ' + ' '.join(f'{d.replace("-", " to ").replace("+", " and over")}: median {f1(DEC[d]["p50"])}, '
                                               f'middle half {f1(DEC[d]["p25"])} to {f1(DEC[d]["p75"])}.' for d in AGES)
           + ' CDC NHANES 2021 to 2023, our calculation.</desc>' + ''.join(fa) + '</svg>')

def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r): raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- the calculator card and its page script
def fg(lab, iid, cls, val, mn, mx, step=None, ph=None):
    st = f' step="{step}"' if step else ''
    v = f' value="{val}"' if val is not None else ''
    p = f' placeholder="{ph}"' if ph else ''
    return (f'<div class="form-group"><label class="form-label" for="{iid}">{lab}</label><input type="number" id="{iid}" '
            f'class="form-input {cls}"{v} min="{mn}" max="{mx}"{st}{p}></div>')
calc = (
    '<div class="calculator-card"><div id="panel-women" class="calc-panel active">'
    '<div class="unit-toggle"><button class="unit-btn active" data-unit="imperial">Imperial (ft, lbs)</button>'
    '<button class="unit-btn" data-unit="metric">Metric (cm, kg)</button></div><div class="form-grid">'
    '<div class="form-row form-row--pair imperial-inputs">' + fg('Height (feet)', 'women-height-ft', 'height-ft', 5, 1, 8)
    + fg('Height (inches)', 'women-height-in', 'height-in', 4, 0, 11) + '</div>'
    '<div class="form-row metric-inputs" style="display:none;">' + fg('Height (cm)', 'women-height-cm', 'height-cm', 162, 50, 250) + '</div>'
    '<div class="form-row form-row--pair imperial-inputs">' + fg('Weight (lbs)', 'women-weight-lbs', 'weight-lbs', 140, 50, 700)
    + fg('Waist (inches)', 'women-waist-in', 'waist-in', None, 15, 80, '0.1', 'Optional') + '</div>'
    '<div class="form-row form-row--pair metric-inputs" style="display:none;">' + fg('Weight (kg)', 'women-weight-kg', 'weight-kg', 63, 20, 300)
    + fg('Waist (cm)', 'women-waist-cm', 'waist-cm', None, 38, 200, '0.1', 'Optional') + '</div>'
    '</div><button class="calculate-btn" id="calc-women-btn">Calculate BMI</button>'
    '<div class="results-section" id="women-results"><div class="bmi-result-card normal" id="women-result-card">'
    '<div class="bmi-value normal" id="women-bmi-value">—</div><div class="bmi-category" id="women-bmi-category">—</div>'
    '<div class="bmi-range" id="women-bmi-range">—</div></div>'
    '<div class="bmi-scale"><div class="bmi-scale-bar"><div class="bmi-scale-segment underweight">Under</div>'
    '<div class="bmi-scale-segment normal">Healthy</div><div class="bmi-scale-segment overweight">Over</div>'
    '<div class="bmi-scale-segment obese">Class 1</div><div class="bmi-scale-segment obese-severe">Class 2+</div>'
    '<div class="bmi-scale-marker" id="women-scale-marker" style="left:40%"></div></div>'
    '<div class="bmi-scale-labels"><span>15</span><span>18.5</span><span>25</span><span>30</span><span>35</span><span>40</span></div></div>'
    '<div class="results-grid"><div class="result-item"><div class="result-item-label">Lowest healthy weight</div>'
    '<div class="result-item-value" id="women-healthy-min">—</div></div><div class="result-item"><div class="result-item-label">'
    'Highest healthy weight</div><div class="result-item-value" id="women-healthy-max">—</div></div></div>'
    '<div class="weight-range-box"><p id="women-weight-diff" style="margin:0;font-size:0.9375rem;">—</p></div>'
    '<div class="rank-box" id="women-rank" hidden><div class="rank-title">Compared with US women aged 20 and over</div>'
    '<div class="rank-value" id="women-rank-value">—</div><div class="rank-track" aria-hidden="true"><span class="rank-median">'
    '</span><span class="rank-marker" id="women-rank-marker"></span></div><div class="rank-axis" aria-hidden="true"><span>Lowest BMI'
    f'</span><span>Median {MED}</span><span>Highest</span></div><p class="rank-text" id="women-rank-text"></p>'
    f'<p class="rank-source">CDC NHANES 2021–2023, {N_ALL:,} women measured; our calculation.</p></div>'
    '<div class="rank-box" id="women-like" hidden><div class="rank-title">US women with a BMI like yours</div>'
    '<p class="rank-text" id="women-like-fat"></p><p class="rank-text" id="women-like-waist"></p>'
    '<p class="rank-source">Body fat: CDC NHANES 2011–2018 body scans, women aged 20 to 59. Waist: CDC NHANES 2021–2023. '
    'Our calculation.</p></div>'
    '<div class="rank-box" id="women-waist" hidden><div class="rank-title">Waist check</div>'
    '<div class="rank-value" id="women-waist-value">—</div><p class="rank-text" id="women-waist-ratio"></p>'
    '<p class="rank-text" id="women-waist-us"></p><p class="rank-text" id="women-waist-ada"></p>'
    '<p class="rank-source">Published thresholds applied to the numbers you entered, for adults who aren’t pregnant; not a '
    'diagnosis. NICE guideline NG246 (2025); NHLBI guidelines (1998); American Diabetes Association, Standards of Care in '
    'Overweight and Obesity 2026.</p></div>'
    '</div></div></div>')

def arr(q): return '[' + ','.join(f'{x:g}' for x in q) + ']'
DATA = {'bf': {str(b): v for b, v in BF_BINS.items()},
        'ws': {c: list(v) for c, v in WSH.items()}}
SCRIPT = ('<script>(function(){var Q={a:' + arr(QA) + ',y:' + arr(QY) + ',m:' + arr(QM) + ',o:' + arr(QO) + '},'
          'D=' + json.dumps(DATA, separators=(',', ':')) + ';' + r'''
var v=document.getElementById("women-bmi-value"),box=document.getElementById("women-rank"),like=document.getElementById("women-like"),wbox=document.getElementById("women-waist"),panel=document.getElementById("panel-women");if(!v||!box)return;
function $(i){return document.getElementById(i);}
function pct(q,b){if(b<=q[0])return 0;if(b>=q[98])return 100;for(var i=0;i<98;i++){if(b<q[i+1])return i+1+(b-q[i])/(q[i+1]-q[i]);}return 100;}
function rk(q,b){return{lo:pct(q,Math.round(b*10-1)/10),hi:100-pct(q,b)};}
function n(x){return x>99?99:Math.round(x);}
function lab(r){return r.lo<1?"lower than "+n(r.hi)+"%":"higher than "+n(r.lo)+"%";}
function share(x){return x>=99.5?"more than 99%":x<=0.5?"under 1%":x.toFixed(1)+"%";}
function num(sel){var e=panel.querySelector(sel);var x=e?parseFloat(e.value):NaN;return x;}
function r1(x){return Math.round(x*10+1e-9)/10;}
function r2(x){return Math.round(x*100+1e-9)/100;}
function trim(x){return String(r1(x));}
function rank(b){var r=rk(Q.a,b),s=b.toFixed(1),head=lab(r),txt;head=head.charAt(0).toUpperCase()+head.slice(1)+" of US women";
 if(r.lo<1)txt="Your BMI of "+s+" is lower than about "+n(r.hi)+"% of US women aged 20 and over.";else if(r.hi<1)txt="Your BMI of "+s+" is higher than about "+n(r.lo)+"% of US women aged 20 and over.";else txt="Your BMI of "+s+" is higher than about "+n(r.lo)+"% of US women aged 20 and over and lower than about "+n(r.hi)+"%.";
 txt+=" By age it is "+lab(rk(Q.y,b))+" of women aged 20 to 39, "+lab(rk(Q.m,b))+" of those 40 to 59 and "+lab(rk(Q.o,b))+" of those 60 and over. The median US woman has a BMI of '''
          + MED + r'''.";
 $("women-rank-value").textContent=head;$("women-rank-text").textContent=txt;$("women-rank-marker").style.left=Math.min(99,Math.max(1,r.lo))+"%";box.hidden=false;}
function likeYou(b){var k=Math.floor(b),f="",w="",c=b<18.5?null:b<25?"healthy":b<30?"overweight":"obesity",cn={healthy:"a healthy BMI",overweight:"an overweight BMI",obesity:"a BMI of 30 or more"};
 if(k>=45)k=45;var t=D.bf[String(k)];
 if(t)f="Body fat: on CDC’s body scans, women aged 20 to 59 with a BMI of "+(k>=45?"45 or more":k+" to "+k+".9")+" had a median of "+t[1]+"%; the middle half measured "+t[0]+"% to "+t[2]+"%.";
 if(c){var s=D.ws[c];w="Waist: among US women with "+cn[c]+", "+share(s[0])+" have a waist of 88 cm (34.6 in) or more and "+share(s[1])+" one at least half their height.";}
 $("women-like-fat").textContent=f;$("women-like-fat").hidden=!f;$("women-like-waist").textContent=w;$("women-like-waist").hidden=!w;like.hidden=!(f||w);}
function ada(b,p,cm,asian){var B0=asian?27.5:30,B1=asian?23:25,line=asian?80:88;if(b>=B0)return"bmi";if(b>=B1)return p>=0.5?"ratio":cm>=line?"cm":"small";return"low";}
function adaText(o,b,cm,q){var s=b.toFixed(1),c=cm.toFixed(1),L="Under the 2026 ADA standards, "+(q?"for women of non-Asian background ":"");
 if(o==="bmi")return L+"a BMI of "+s+" counts as obesity on BMI alone.";
 if(o==="ratio")return L+"a BMI of "+s+" counts as obesity with a waist of at least half the height, and yours is.";
 if(o==="cm")return L+"a BMI of "+s+" counts as obesity with a waist of 88 cm or more, and yours, at "+c+" cm, is.";
 if(o==="small")return L+"a BMI of "+s+" counts as obesity only with a waist of at least half the height or of 88 cm or more; at "+c+" cm, yours is under both.";
 return L+"the waist doesn’t change the class at a BMI under 25.";}
function isOb(o){return o==="bmi"||o==="ratio"||o==="cm";}
function waist(b){var metric=panel.querySelector(".unit-btn.active").dataset.unit==="metric",h,w,wr,cm,wtxt;
 if(metric){h=num(".height-cm");w=num(".waist-cm");if(!(w>=38&&w<=200)||!(h>0)){wbox.hidden=true;return;}wr=r1(w);cm=wr;wtxt=trim(wr)+" cm ("+r1(wr/2.54).toFixed(1)+" in)";}
 else{h=num(".height-ft")*12+(num(".height-in")||0);w=num(".waist-in");if(!(w>=15&&w<=80)||!(h>0)){wbox.hidden=true;return;}wr=r1(w);cm=r1(wr*2.54);wtxt=trim(wr)+" in ("+cm.toFixed(1)+" cm)";}
 var p=Math.floor(wr/h*100+1e-9)/100,rs=p.toFixed(2),t1,t2,t3,na=ada(b,p,cm,false),as=ada(b,p,cm,true),q=isOb(as)&&!isOb(na),cls;
 t1="Your waist, "+wtxt+", is "+rs+" of your height.";
 if(b>=35)t1+=" NICE’s ratio classes are for adults with a BMI under 35, so they don’t apply at yours.";
 else if(p<0.4)t1+=" NICE’s classes for adults with a BMI under 35 start at 0.4 (0.4 to 0.49 is healthy central adiposity).";
 else{cls=p<0.5?"0.4 to 0.49 is healthy central adiposity":p<0.6?"0.5 to 0.59 is increased central adiposity":"0.6 or more is high central adiposity";t1+=" On NICE’s scale for adults with a BMI under 35, "+cls+".";}
 t2="US guidelines treat a waist over "+(metric?"88 cm":"35 in")+" as a sign of higher risk for women, mainly at a BMI of 25 to 34.9. Yours is "+(wr>(metric?88:35)?"over":"not over")+" that line.";
 t3=adaText(na,b,cm,q);
 if(q)t3+=" For women of Asian background the lines are lower: a BMI of 27.5, or 23 with a waist of at least half the height or of 80 cm (31.5 in). With your numbers that counts as obesity.";
 if(isOb(as)&&b<30)t3+=" By BMI alone (CDC) it is "+(b<18.5?"underweight":b<25?"a healthy weight":"overweight")+".";
 $("women-waist-value").textContent="Waist-to-height ratio "+rs;$("women-waist-ratio").textContent=t1;$("women-waist-us").textContent=t2;$("women-waist-ada").textContent=t3;wbox.hidden=false;}
function show(){var b=parseFloat(v.textContent);if(!(b>0)){box.hidden=true;like.hidden=true;wbox.hidden=true;return;}rank(b);likeYou(b);waist(b);}
new MutationObserver(show).observe(v,{childList:true,characterData:true,subtree:true});})();</script>''')

# ---------------------------------------------------------------- the page's own text
H1 = 'BMI Calculator for Women'
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Get your BMI, your healthy weight and how you compare with US women your age. Add your waist for '
    'the 2026 waist check.</p>'
    f'<p class="intro-note">CDC adult categories, the same for women and men. US comparison: CDC measurements of {N_ALL:,} women, '
    '2021–2023. <a href="#sources">Method and sources</a></p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>BMI for women</strong> uses the same formula and CDC cut-offs as for men: weight in kilograms '
    'divided by height in meters squared, or pounds × 703 ÷ inches². <strong>18.5 to 24.9 is a healthy weight</strong>, 25 to '
    '29.9 is overweight and 30 or more is obesity, at every adult age.</p><ul>'
    f'<li><strong>The median US woman has a BMI of {MED}</strong>, and {HEALTHY_ALL}% of women have one in the healthy range '
    '(CDC measurements, 2021–2023).</li>'
    f'<li>At 5′4″ (162.6 cm), a healthy weight is <strong>{HB_LB[0]} to {HB_LB[1]} lb ({HB_KG[0]} to {HB_KG[1]} kg)</strong>.</li>'
    f'<li><strong>Since June 2026 the waist counts too:</strong> {ADA_OB}% of US women meet the American Diabetes '
    f'Association’s new obesity thresholds, against {ADA_BMI}% of the same women by BMI alone (our calculation).</li>'
    '<li>At the same BMI women carry more fat: on CDC’s scans of adults aged 20 to 59 with a healthy BMI, women had a median '
    f'of {BF_CAT["f"]["healthy"][0]}% body fat and men {BF_CAT["m"]["healthy"][0]}%.</li>'
    '<li>In pregnancy the categories don’t apply; CDC’s advice on weight gain uses your BMI before pregnancy.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information only. '
    'BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

CHIPS = (('read-result', 'Your result'), ('us-women', 'US women'), ('by-age', 'By age'), ('by-height', 'Weight by height'),
         ('waist', 'Waist'), ('body-fat', 'Body fat'), ('background', 'Background'), ('pregnancy', 'Pregnancy'),
         ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

EXR = EX_R
sec_read = (
    '<section id="read-result" class="content-section flow"><h2>How to read your result</h2>'
    f'<p>Every number below uses the calculator’s starting values, 5′4″ ({EX_CM} cm) and {EX_W} lb ({EX_KG} kg), with a waist '
    f'of {EX_WAIST} inches ({EX_WCM} cm) entered in the optional field.</p>'
    f'<figure class="figure">{svg_ex}<figcaption>{EX_W} lb at 5′4″ gives a BMI of {EX_BMI}, inside the healthy range; '
    f'overweight starts at {OVER_FROM} lb.</figcaption></figure>'
    '<dl>'
    f'<dt>BMI: {EX_BMI}, healthy weight</dt><dd>{EX_W} × 703 ÷ {EX_H}² = {EX_BMI}, rounded to one decimal '
    f'({ext(U["cdc_formula"], "CDC formula")}); the category comes from that rounded number. CDC’s adult cut-offs: under 18.5 '
    'underweight, 18.5 to 24.9 healthy, 25 to 29.9 overweight, 30 and above obesity.</dd>'
    f'<dt>Healthy weight: {HB_LB[0]}–{HB_LB[1]} lb ({HB_KG[0]}–{HB_KG[1]} kg)</dt><dd>The lightest and heaviest whole pounds at '
    'your height with a BMI of 18.5 to 24.9, and the same in whole kilograms. It depends only on height. The line under the '
    'tiles says how far you are from the range when you are outside it.</dd>'
    f'<dt>Compared with US women: higher than {EXR["all"]}%</dt><dd>About {EXR["all"]}% of women aged 20 and over, measured '
    f'by CDC in 2021–2023, have a lower BMI than yours and about {EX_HI}% a higher one, read off the percentiles in the next '
    f'section. The text adds the figure for women aged 20 to 39 ({EXR["y"]}%), 40 to 59 ({EXR["m"]}%) and 60 and over '
    f'({EXR["o"]}%).</dd>'
    f'<dt>US women with a BMI like yours</dt><dd>On CDC’s body scans, women aged 20 to 59 with a BMI of 24 to 24.9 had a median '
    f'of {EX_BIN[1]}% body fat (middle half {EX_BIN[0]}% to {EX_BIN[2]}%), and among US women with a healthy BMI, {WSH["healthy"][1]}% '
    'have a waist at least half their height.</dd>'
    f'<dt>Waist check: ratio {EX_RATIO:.2f}</dt><dd>{EX_WAIST} ÷ {EX_H} = {EX_RAW:.3f}, which the check shows as '
    f'{EX_RATIO:.2f}: it cuts the ratio to two decimals, so 0.50 always means a waist of at least half the height. That is '
    'increased central adiposity on NICE’s scale, and under the 35-inch line in US guidelines. Under the 2026 ADA '
    'standards, for women of non-Asian background the waist doesn’t change the class '
    'at a BMI under 25. For women of Asian background the line is 23, so for them a BMI of 24.0 with this waist counts as '
    'obesity.</dd>'
    f'<dt>BMI Prime: {EX_PRIME}</dt><dd>Your BMI divided by 25, where overweight starts; under 1.00 is below it.</dd>'
    f'<dt>Ponderal index: {EX_PI} kg/m³</dt><dd>Weight in kilograms divided by height in meters cubed. CDC’s adult categories '
    'use BMI, not this index, so compare it only with your own earlier results.</dd>'
    f'<dt>Weight milestones</dt><dd>The weight where each range starts at your height. At 5′4″: healthy from {HB_LB[0]} lb, '
    f'overweight from {FROM[25]} lb, obesity from {FROM[30]} lb, class 2 obesity from {FROM[35]} lb and class 3 from '
    f'{FROM[40]} lb.</dd>'
    '</dl></section>')

PCT_ROWS = (('p5', '5th'), ('p10', '10th'), ('p25', '25th'), ('p50', 'Median'), ('p75', '75th'), ('p90', '90th'), ('p95', '95th'))
pct_rows = ''.join(f'<tr><th scope="row">{lab_}</th>' + ''.join(f'<td class="num">{f1(T[g][k])}</td>' for g in ('all', '20-39', '40-59', '60+'))
                   + '</tr>' for k, lab_ in PCT_ROWS)
sec_us = (
    '<section id="us-women" class="content-section flow"><h2>How your BMI compares with US women</h2>'
    f'<p>The comparison uses CDC’s measurements of {N_ALL:,} women aged 20 and over (pregnant women excluded), taken from '
    'August 2021 to August 2023 in its National Health and Nutrition Examination Survey (NHANES). <strong>The median woman had '
    f'a BMI of {MED}</strong>, in the overweight range, and a quarter had a BMI of {f1(T["all"]["p25"])} or lower. The '
    'calculator ranks your result against all of them and against women in your age group.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>BMI of US women by percentile and age group</caption>'
    '<thead><tr><th scope="col">Percentile</th>'
    + ''.join(f'<th scope="col" class="num"><span class="nowrap">{h}</span></th>' for h in ('All', '20–39', '40–59', '60+'))
    + f'</tr></thead><tbody>{pct_rows}</tbody></table></div>'
    f'<p>Read down a column: at ages 40 to 59, a quarter of women have a BMI of {f1(T["40-59"]["p25"])} or lower and a quarter '
    f'{f1(T["40-59"]["p75"])} or higher. In the rank, only women with a lower BMI count as below you and only those with a '
    'higher one as above you; women with the same BMI count on neither side.</p>'
    f'<p class="source-note">Our calculation from {ext(U["nhanes"], "CDC NHANES August 2021–August 2023")} measured heights and '
    f'weights, weighted with the exam weights: {N_Y:,} women aged 20 to 39, {N_M:,} aged 40 to 59 and {N_O:,} aged 60 and over. '
    'The all-women column is the curve the homepage’s BMI calculator uses for its women-only rank, so both give the same '
    'answer.</p>'
    '</section>')

AGE_ROWS = ''.join(
    f'<tr><th scope="row">{d.replace("-", "–")}</th><td class="num">{f1(DEC[d]["p50"])}</td><td class="nowrap">{f1(DEC[d]["p25"])}–'
    f'{f1(DEC[d]["p75"])}</td><td class="num">{f1(DEC[d]["healthy"]["pct"])}%</td></tr>' for d in AGES)
N_DEC = sorted(DEC[d]['n'] for d in AGES)
sec_age = (
    '<section id="by-age" class="content-section flow"><h2>BMI for women by age</h2>'
    f'<p>CDC applies its adult categories “regardless of age, sex, or race” ({ext(U["cdc_cat"], "CDC")}), so 18.5 to 24.9 is a '
    'healthy BMI at 70 as at 20. US women’s average BMI differs by age group: <strong>'
    f'{DM["20-29"]} for women in their 20s and {DM["50-59"]} in their 50s</strong>, then {DM["70-79"]} at 70 to 79 and '
    f'{DM["80+"]} at 80 and over (our calculation; each difference is larger than its margin of error). These are different '
    'women measured in the same years, not the same women followed as they aged. '
    f'{DH["20-29"]}% of women in their 20s have a BMI in the healthy range, against {DH["50-59"]}% in their 50s.</p>'
    f'<figure class="figure">{svg_age}<figcaption>BMI of US women by decade of age: the median (tick), the middle half (bar) and '
    'the 10th to 90th percentile (line), against CDC’s healthy range. CDC NHANES 2021–2023, our calculation.</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table"><caption>BMI of US women by decade of age</caption><thead><tr>'
    '<th scope="col">Age</th><th scope="col" class="num">Median</th><th scope="col">Middle half</th><th scope="col" class="num">'
    f'Healthy BMI</th></tr></thead><tbody>{AGE_ROWS}</tbody></table></div>'
    f'<p class="source-note">Median and middle half of BMI, and the share of women with a BMI of 18.5 to 24.9. Our calculation '
    f'from CDC NHANES 2021–2023: {N_DEC[0]} to {N_DEC[-1]} women in each decade. The '
    'averages in the text match NCHS’s published reference data (Series 3, No. 50). The shares carry 95% margins of error of up '
    f'to about 10 points (80 and over, {DEC["80+"]["n"]} women). Under 20, BMI is read as a percentile for age and sex '
    f'({ext(U["cdc_child"], "CDC")}); the '
    '<a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> works it out.</p>'
    '<h3>Women 60 and over</h3>'
    '<p>Some senior BMI calculators online class a BMI of 23 to 29.9 (or 23 to 30) as normal for adults over 65 and list the '
    'meta-analysis below among their sources. That range isn’t CDC’s. In that meta-analysis of 197,940 people aged 65 and over, compared with a '
    'BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 '
    f'({ext(U["winter"], "Winter et al., 2014")}): an association, not a healthy range or a target.</p>'
    '<p>Muscle is the other caveat: “Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to '
    f'underdiagnosis of obesity” ({ext(U["ada"], "ADA, 2026")}). US women aged 70 to 79 have a median BMI of {f1(D70["p50"])}, '
    f'and {DH["70-79"]}% have one in the healthy range. The <a href="/age-bmi-calculator/">BMI calculator by age</a> and '
    '<a href="/blog/bmi-by-age/">BMI by age</a> cover older adults in more depth.</p>'
    '</section>')

HEIGHTS = list(range(58, 73))
def ft(h): return f'{h // 12}′{h % 12}″'
H_ROWS = []
for h in HEIGHTS:
    lb, kg = hb(h)
    H_ROWS.append(f'<tr><th scope="row">{ft(h)} ({dcm(h)} cm)</th><td>{lb[0]}–{lb[1]} lb ({kg[0]}–{kg[1]} kg)</td>'
                  f'<td class="num">{h / 2:.1f} in ({dcm(Decimal(h) / 2)} cm)</td></tr>')
assert hb(64) == ((108, 145), (49, 65)) and hb(70) == ((129, 173), (59, 78))
assert dcm(Decimal(65) / 2) == '82.6' and dcm(65) == '165.1' and dcm(71) == '180.3'
assert 70 * 2.54 / 2 > 88 > 69 * 2.54 / 2 and 63 * 2.54 / 2 >= 80 > 62 * 2.54 / 2
sec_height = (
    '<section id="by-height" class="content-section flow"><h2>Healthy weight for women by height</h2>'
    '<p>The healthy range depends only on height. For every height from 4′10″ to 6′0″, the table gives it in pounds and '
    'kilograms, each worked out on its own, next to half the height: a waist at or above it is a waist-to-height ratio of '
    '0.5 or more. The '
    '<a href="/blog/bmi-chart-women/">BMI chart for women</a> has every category at every height.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Healthy weight and half the height, women 4′10″ to 6′0″'
    '</caption><thead><tr><th scope="col">Height</th><th scope="col">Healthy weight<span class="th-sub">BMI 18.5–24.9</span></th>'
    '<th scope="col" class="num">Half the height<span class="th-sub">ratio 0.5</span></th></tr></thead><tbody>'
    + ''.join(H_ROWS) + '</tbody></table></div>'
    '<p>The 2026 ADA waist rule matters at a BMI of 25 to 29.9 (23 to 27.4 for women of Asian background). Either waist test '
    'is enough, so the lower line decides: half the height up to 5′9″ and 88 cm (34.6 in) from 5′10″. For women of Asian '
    'background the cm line is 80 cm (31.5 in), which decides from 5′3″.</p>'
    '<p class="source-note">Whole pounds and kilograms whose BMI, rounded to one decimal, is 18.5 to 24.9 at the height shown '
    f'(cut-offs: {ext(U["cdc_cat"], "CDC Adult BMI Categories")}). Half the height to 0.1 inch and 0.1 cm.</p>'
    '</section>')

sec_waist = (
    '<section id="waist" class="content-section flow"><h2>Waist size and the 2026 ADA standards</h2>'
    '<p>BMI can’t show where fat sits; a tape measure can. Three rules use the waist, and the calculator’s waist check applies '
    'all three:</p><ul>'
    f'<li><strong>US guidelines</strong> treat a waist over 35 inches (88 cm) as a sign of higher risk for women, mainly at a '
    f'BMI of 25 to 34.9 ({ext(U["nhlbi"], "NHLBI")}).</li>'
    '<li><strong>NICE (UK)</strong> classes a waist-to-height ratio of 0.4 to 0.49 as healthy central adiposity, 0.5 to 0.59 as '
    'increased and 0.6 or more as high, for adults of both sexes and all ethnicities with a BMI under 35 '
    f'({ext(U["nice"], "NICE")}).</li>'
    '<li><strong>The American Diabetes Association’s 2026 standards</strong> count obesity from a BMI of 30, or from 25 with a '
    'waist of at least half the height or 88 cm (34.6 in) in women. For women of Asian background the lines are a BMI of '
    '27.5, or 23 with a waist of at least half the height or 80 cm (31.5 in). The standards cover adults who aren’t pregnant '
    f'({ext(U["ada"], "ADA, 2026")}).</li></ul>'
    f'<p>Among US women with a healthy BMI, <strong>{WSH["healthy"][0]}% have a waist of 88 cm or more and {WSH["healthy"][1]}% '
    f'one at least half their height</strong>; with an overweight BMI, {WSH["overweight"][0]}% and {WSH["overweight"][1]}% (our '
    f'calculation, {N_WAIST:,} women with a measured waist). Applied to {ADA_N:,} women, the ADA thresholds class {ADA_OB}% '
    f'as obesity, against {ADA_BMI}% of the same women by BMI alone.</p>'
    '<p>The <a href="/blog/waist-to-height-ratio/">waist-to-height ratio guide</a> shows how to measure, and the '
    '<a href="/blog/bmi-chart-women/">BMI chart for women</a> breaks the waist shares down further.</p>'
    '</section>')

FB, MB_ = BF_CAT['f'], BF_CAT['m']
sec_fat = (
    '<section id="body-fat" class="content-section flow"><h2>Body fat at the same BMI</h2>'
    '<p>BMI counts muscle, bone and fat alike, and at the same BMI women carry more fat than men. On CDC’s body scans of adults '
    f'aged 20 to 59, <strong>women with a healthy BMI had a median of {FB["healthy"][0]}% body fat</strong> (middle half '
    f'{FB["healthy"][1]}% to {FB["healthy"][2]}%), men {MB_["healthy"][0]}% ({MB_["healthy"][1]}% to {MB_["healthy"][2]}%). At an '
    f'overweight BMI the women’s median was {FB["over"][0]}%, and with obesity {FB["obese"][0]}% (our calculation from '
    f'{ext(U["dxx"], "NHANES 2011–2018")} DXA scans).</p>'
    '<p>After you calculate, the line on US women with a BMI like yours gives the median for your one-point band of BMI (24 '
    'to 24.9, for example). For a reading of your own, '
    'the <a href="/body-fat-calculator/">body fat calculator</a> estimates it from a tape measure, and the '
    '<a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows where a reading sits among US women.</p>'
    '</section>')

sec_bg = (
    '<section id="background" class="content-section flow"><h2>Asian and other backgrounds</h2>'
    f'<p>CDC’s categories don’t change with race: they apply “regardless of age, sex, or race” ({ext(U["cdc_cat"], "CDC")}). '
    'Other bodies use lower lines for some groups:</p><ul>'
    '<li>CDC’s National Diabetes Prevention Program takes Asian American adults from a BMI of 23 instead of 25 '
    f'({ext(U["ndpp"], "CDC")}).</li>'
    '<li>A WHO expert consultation kept the international categories for everyone and named BMI 23, 27.5, 32.5 and 37.5 as '
    f'potential public-health action points for Asian populations ({ext(U["who2004"], "WHO, 2004")}).</li>'
    '<li>In the UK, NICE uses overweight from 23 to 27.4 and obesity from 27.5 for people of South Asian, Chinese, other Asian, '
    f'Middle Eastern, Black African or African-Caribbean background ({ext(U["nice"], "NICE guideline NG246")}, a 2022 '
    'recommendation).</li></ul>'
    '<p>The 2026 ADA standards also set lower lines for adults of Asian background: obesity from a BMI of 27.5, or from 23 with '
    'a waist at least half the height or 80 cm (31.5 in) in women. When your waist is entered, the waist check shows that '
    'result too whenever it differs.</p>'
    '</section>')

PREG = (('Under 18.5', '28–40 lb'), ('18.5–24.9', '25–35 lb'), ('25.0–29.9', '15–25 lb'), ('30.0–39.9', '11–20 lb'))
sec_preg = (
    '<section id="pregnancy" class="content-section flow"><h2>BMI and pregnancy</h2>'
    '<p>The adult categories are for women who aren’t pregnant: NCHS leaves pregnant women out of its adult BMI statistics, as '
    'the US comparison on this page does. During pregnancy, CDC’s advice on weight gain depends on your BMI before pregnancy, '
    f'using recommendations from the Institute of Medicine ({ext(U["cdc_preg"], "CDC")}):</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Recommended weight gain in pregnancy with one baby'
    '</caption><thead><tr><th scope="col">BMI before pregnancy</th><th scope="col" class="num">Total gain</th></tr></thead><tbody>'
    + ''.join(f'<tr><th scope="row">{a}</th><td class="num">{b}</td></tr>' for a, b in PREG)
    + '</tbody></table></div>'
    '<p class="source-note">CDC, Weight Gain During Pregnancy, which also gives ranges for twins.</p>'
    '</section>')

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in the owner's US/English pastes of 2026-10-22, not personalized ("bmi calculator women", "bmi calculator
# female", "bmi calculator for older women"), in that order, each question once; "What is a good BMI for an older woman?"
# is answered by the 70-year-old question and the seniors question. Then the ledger's "bmi for women formula" and the old
# page's pregnancy question.
FAQ = [
    ('What is the correct BMI for a female?',
     f'18.5 to 24.9, which CDC calls a healthy weight. It is the same for women and men: CDC applies its adult categories '
     f'“regardless of age, sex, or race” ({ext(U["cdc_cat"], "CDC")}). Under 18.5 is underweight, 25 to 29.9 overweight and '
     f'30 or more obesity. The median US woman has a BMI of {MED}, and {HEALTHY_ALL}% of women are in the healthy range (our '
     'calculation from CDC measurements, 2021–2023).'),
    ('Is 140 pounds fat for a 5′4″ female?',
     f'Not by BMI. At 5′4″, 140 lb is a BMI of 24.0, a healthy weight; the range at that height is {HB_LB[0]} to {HB_LB[1]} lb, '
     f'and overweight starts at {OVER_FROM} lb. About {P140_HI}% of US women have a higher BMI. BMI can’t say how much of the '
     'weight is fat: the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows what women with that BMI '
     'measured on CDC’s body scans.'),
    ('What is the correct BMI for my age as a female?',
     f'The same at every adult age: 18.5 to 24.9 ({ext(U["cdc_cat"], "CDC")}). Among US women the median BMI is '
     f'{f1(T["20-39"]["p50"])} at ages 20 to 39, {f1(T["40-59"]["p50"])} at 40 to 59 and '
     f'{f1(T["60+"]["p50"])} at 60 and over (our calculation, 2021–2023), and the calculator ranks you in each group. Under '
     '20, BMI is read as a percentile for age and sex; use the <a href="/kids-bmi-calculator/">BMI calculator for children and '
     'teens</a>.'),
    ('What is an acceptable BMI for a 70 year old female?',
     '18.5 to 24.9, the same as at any adult age (CDC). US women aged 70 to 79 have a median BMI of '
     f'{f1(D70["p50"])}, and {DH["70-79"]}% have one in the healthy range (our calculation, {D70["n"]} women). In adults 65 and '
     'over, compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 '
     f'({ext(U["winter"], "Winter et al., 2014")}); that is an association, not a separate range.'),
    ('What is BMI for 5′2″ female?',
     'It depends on weight. At 5′2″ (157.5 cm), a healthy BMI of 18.5 to 24.9 means '
     f'{B62[0][0]} to {B62[0][1]} lb ({B62[1][0]} to {B62[1][1]} kg). At {P62_W} lb, for example, the BMI is {P62_BMI} '
     f'({P62_W} × 703 ÷ 62²), higher than about {P62_R}% of US women. Enter your weight in the calculator for your own '
     'number.'),
    ('How much should a 5′5″ female weigh?',
     f'For a BMI in CDC’s healthy range, {B65[0][0]} to {B65[0][1]} lb ({B65[1][0]} to {B65[1][1]} kg) at 5′5″ ({dcm(65)} cm). '
     'Above that is overweight, and under the 2026 ADA standards an overweight BMI with a waist of half the height, '
     f'32.5 inches ({dcm(Decimal(65) / 2)} cm), or more counts as obesity; the lines are lower for women of Asian background. '
     'The <a href="/blog/bmi-chart-women/">BMI chart for women</a> has every height.'),
    ('Is there a BMI calculator for seniors?',
     'This one works at any adult age, since CDC’s adult categories have no upper age limit. Some senior calculators online '
     'class 23 to 29.9 (or 23 to 30) as normal after 65; that range isn’t CDC’s, and the meta-analysis they cite '
     f'({ext(U["winter"], "Winter et al., 2014")}) describes risk of death, not a healthy range. The calculator here ranks you '
     'among US women aged 60 and over, and the '
     '<a href="/age-bmi-calculator/">BMI calculator by age</a> adds averages for your age group.'),
    ('What is the new BMI chart for 2026?',
     'There isn’t a new chart: CDC’s adult categories are unchanged, on a page dated March 2024 '
     f'({ext(U["cdc_cat"], "CDC")}). What changed in June 2026 is the American Diabetes Association’s definition of obesity, '
     'which adds the waist: for a woman of non-Asian background, a BMI of 25 to 29.9 counts as obesity when the waist is at '
     'least half the height or 88 cm (34.6 in) or more, with lower lines for women of Asian background '
     f'({ext(U["ada"], "ADA, 2026")}). Enter your waist above to apply it.'),
    ('Is BMI calculated differently for women?',
     'No. It is weight in kilograms divided by height in meters squared, or pounds × 703 ÷ inches², with the same CDC '
     'categories. What differs is body composition and the waist lines: at a healthy BMI, women aged 20 to 59 had a median of '
     f'{FB["healthy"][0]}% body fat on CDC’s scans and men {MB_["healthy"][0]}%, and US guidelines draw the waist line at 35 '
     'inches for women and 40 for men.'),
    ('Should I use BMI during pregnancy?',
     'Not to judge your weight. During pregnancy CDC’s advice on weight gain uses your BMI before pregnancy: 28 to 40 lb '
     'under 18.5, 25 to 35 lb at 18.5 to 24.9, 15 to 25 lb at 25.0 to 29.9 and 11 to 20 lb at 30.0 to 39.9, for one baby '
     f'({ext(U["cdc_preg"], "CDC")}, from the Institute of Medicine).'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p>'
                   '</div></div>' for q, a in FAQ)
sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC NHANES August 2021–August 2023 {ext(U["nhanes"], "demographics and body measures files")} (DEMO_L, BMX_L): our '
    f'calculation for {N_ALL:,} women aged 20 and over (BMI percentiles by age, BMI by decade), {N_WAIST:,} with a measured '
    f'waist and {ADA_N:,} for the 2026 ADA thresholds.',
    f'Fryar CD, et al. {ext(U["s3"], "Anthropometric Reference Data for Children and Adults: United States, August 2021–August 2023")} '
    '(NCHS, Vital and Health Statistics Series 3, No. 50, 2025): the published averages our decade figures match.',
    f'CDC NHANES 2011–2018 {ext(U["dxx"], "whole-body DXA scans")}: our calculation of body fat at each BMI for women aged 20 '
    'to 59 (the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> has the method).',
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the cut-offs and the “regardless of age, sex, or race” rule.',
    f'CDC. {ext(U["cdc_formula"], "Calculating BMI")}: the formula in US units.',
    f'CDC. {ext(U["cdc_child"], "Child and Teen BMI Categories")}: percentiles under 20.',
    f'NHLBI. {ext(U["nhlbi"], "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")} '
    '(NIH, 1998): the waist cut-offs for women and men.',
    f'NICE. {ext(U["nice"], "Overweight and obesity management")}, guideline NG246 (2025): waist-to-height ratio classes and '
    'the lower BMI thresholds by family background.',
    'American Diabetes Association Professional Practice Committee for Obesity. '
    f'{ext(U["ada"], "Screening, Diagnosis, Evaluation, and Staging of Obesity in Adults: Standards of Care in Overweight and Obesity—2026")}: '
    'obesity thresholds with waist size (recommendations 3.3a and 3.3b) and the note on older adults.',
    f'CDC. {ext(U["ndpp"], "National Diabetes Prevention Program eligibility")}: BMI of 23 or higher for Asian American adults.',
    f'WHO Expert Consultation. {ext(U["who2004"], "Appropriate body-mass index for Asian populations")} (Lancet, 2004).',
    f'Winter JE, et al. {ext(U["winter"], "BMI and all-cause mortality in older adults: a meta-analysis")} (Am J Clin Nutr, '
    '2014).',
    f'CDC. {ext(U["cdc_preg"], "Weight Gain During Pregnancy")}: recommended gain by BMI before pregnancy (Institute of '
    'Medicine).',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Women aged 20 and over with a measured height and weight in NHANES August '
    '2021–August 2023, pregnant women excluded, weighted with CDC’s exam weights. Percentiles come from the weighted '
    'distribution of the measured BMIs (one weight per distinct BMI, straight lines in between), the method that reproduces '
    'NCHS’s published medians; the rank reads your BMI off those percentiles. Shares carry 95% confidence intervals from '
    'Taylor linearization over the survey’s 15 strata, and the page states a difference between ages only when its interval '
    'excludes zero. Every figure is rounded once, from the unrounded estimate, with one exception: the rank reads percentile '
    'curves stored to two decimals, the homepage’s, which moves a few results by one point. The waist check rounds your '
    'waist to 0.1 inch or 0.1 cm and cuts the ratio to two decimals instead of rounding it (0.4953 shows as 0.49), so 0.50 '
    'always means a waist of at least half the height; it compares what it prints and uses your BMI as the calculator shows '
    'it. US guidelines give their waist line as 35 inches and as 88 cm; the check uses the one in your unit.</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/men-bmi-calculator/', 'BMI calculator for men'), ('/age-bmi-calculator/', 'BMI calculator by age'),
        ('/body-fat-calculator/', 'Body fat calculator'), ('/ideal-weight/', 'Ideal weight calculator'),
        ('/kids-bmi-calculator/', 'BMI calculator for children and teens')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/blog/bmi-chart-women/', 'BMI chart for women'), ('/body-fat-percentage-chart/', 'Body fat percentage chart'),
        ('/blog/healthy-bmi-range/', 'Healthy BMI range'), ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'),
        ('/blog/bmi-by-age/', 'BMI by age'), ('/average-weight/', 'Average weight by height')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, calc, takeaways, toc, sec_read, sec_us, sec_age, sec_height, sec_waist, sec_fat, sec_bg, sec_preg, sec_faq, sec_src,
     sec_rel]) + ' </div></main>')
assert 'placeholder=' in main and 'style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>|<div class="form-row (?:form-row--pair )?(?:imperial|metric)-inputs" style="display:none;">|<p id="women-weight-diff" style="[^"]*">|<div class="bmi-scale-marker" id="women-scale-marker" style="left:40%">', '', main)
assert all(f'id="{a}"' in main for a, _ in CHIPS)

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'BMI Calculator for Women: Waist Check and US Women Compared'
DESC = ('Free BMI calculator for women: your BMI and healthy weight, an optional waist check against the 2026 ADA thresholds, '
        'and how you compare with US women by age.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'BMI Calculator for Women: your BMI, a waist check and US women by age'
OG_D = (f'Your BMI, the healthy weight for your height, an optional waist check (NHLBI, NICE and the 2026 ADA thresholds) and '
        f'how your BMI ranks among US women, from CDC’s measurements of {N_ALL:,} women.')
OG_ALT = 'Chart: the BMI of US women in each decade of age from their 20s to 80 and over, against the healthy range.'
PREF = SITE + '/assets/images/preferred/women-bmi-calculator-'
IMG16, IMG43, IMG11 = PREF + '16x9.png', PREF + '4x3.png', PREF + '1x1.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">',
           f'<meta property="og:image" content="{IMG16}"><meta property="og:image:alt" content="{OG_ALT}">', src)
src = sub1(r'<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', src)
src = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_T}">', src)
src = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{OG_D}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1 and '<style' not in src

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 3
types = [json.loads(b.group(1))['@type'] for b in blocks]
assert types == ['WebApplication', 'BreadcrumbList', 'FAQPage'], types
crumbs = json.loads(blocks[1].group(1))
assert [i['name'] for i in crumbs['itemListElement']] == ['Home', 'Calculators', 'BMI Calculator for Women']
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
graph = [
    {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'isPartOf': {'@id': SITE + '/#website'},
     'mainEntity': {'@id': URL + '#calculator'},
     'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}},
    {'@type': 'WebApplication', '@id': URL + '#calculator', 'image': [IMG11, IMG43, IMG16], 'name': H1,
     'description': ('Calculates BMI for adult women from height and weight in pounds and inches or kilograms and centimeters, '
                     'gives the CDC adult category and the healthy weight range for the height, ranks the result among US women '
                     'aged 20 and over and by age group using CDC NHANES August 2021–August 2023 measurements, and checks an '
                     'optional waist against the NHLBI, NICE and 2026 American Diabetes Association thresholds.'),
     'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any', 'browserRequirements': 'Requires JavaScript',
     'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
     'featureList': ['BMI from US or metric units', 'CDC adult BMI category', 'Healthy weight range for your height in pounds and kilograms',
                     'Rank among US women aged 20 and over and aged 20–39, 40–59 and 60+ (CDC NHANES 2021–2023)',
                     'Waist check: waist-to-height ratio, NHLBI waist line and 2026 ADA obesity thresholds',
                     'Body fat measured in US women aged 20–59 at your BMI (CDC NHANES 2011–2018 DXA)'],
     'author': PERSON},
    {k: v for k, v in crumbs.items() if k != '@context'},
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}}
                                       for q, a in FAQ]},
]
ld = {'@context': 'https://schema.org', '@graph': graph}
start, end = blocks[0].start(), blocks[2].end()
src = src[:start] + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' + src[end:]

# ---------------------------------------------------------------- body
i, j = src.index('<main>'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
calcjs = '<script src="/assets/js/calculator.js"></script>'
assert src.count(calcjs) == 1
src = src.replace(calcjs, calcjs + ' ' + SCRIPT)
assert main.count('style="') == 4, 'in <main> only the calculator rows, the status line and the scale marker keep an inline style'

open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'women-bmi-calculator/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, {len(FAQ)} FAQ, '
      f'{len(TEXTS)} SVG labels checked; example ranks all/y/m/o {EX_R}, higher {EX_HI}; 5′2″ 130 lb rank {P62_R}; '
      f'140 lb higher {P140_HI}')
