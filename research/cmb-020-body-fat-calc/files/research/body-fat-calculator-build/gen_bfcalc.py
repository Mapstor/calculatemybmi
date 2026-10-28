#!/usr/bin/env python3
"""CMB-020 BODY-FAT-CALC: rebuilds /body-fat-calculator/ to the D-14 calculator pattern (DESIGN.md; the homepage and the
women's and men's calculators applied it): the tool first, then key takeaways, contents chips, a worked example, real
tables and figures, a flat FAQ whose JSON-LD equals the visible answers, sources and method, one related block, one 680 px
reading column. No <article> wrapper (D-16): the sections sit directly in main .container.

Wedge (owner's SERP pastes of 2026-10-28, US/English, not personalized: "body fat calculator", "body fat percentage
calculator", "body fat calculator female"): every result is a calculator that prints a number from the Navy tape method,
BMI or skinfolds and stops there. None says how close that number is likely to be. This page does, for each method:
  1. waist and height (relative fat mass, Woolcott and Bergman 2018) and height and weight (Deurenberg 1991), checked on
     CDC's own DXA scans of US adults aged 20 to 59 (NHANES 2011-2018, our calculation in bfc_stats.py): the share within
     3 and 5 points of the scan, the typical miss, the average error overall and by BMI and age group, and, for any
     estimate, what CDC's scans read in people whose formula gave the same estimate;
  2. the tape measure and calipers, which CDC's survey can't check (no neck or skinfold measurements), from published
     comparisons with DXA: Army recruits (Foulis et al., 2023) and college students (Burns et al., 2019);
  3. the result placed on the provisional ranges (Gallagher et al., 2000) and among US adults of the same sex and age
     group (the /body-fat-percentage-chart/ data, bfpc_stats.json, read the way that page's rank tool reads it).
D-15: bodyfatpercentagecalc.com (the owner's other site) stays unlinked; this page's distinct asset is the DXA check.

Every number comes from bfc_stats.json, bfpc_stats.json, the formulas themselves or a source verified in chat on
2026-10-28 (constants below, each with its source). Round once: a printed figure is formatted from the unrounded value
(bfc_stats.py stores 4 decimals, more where 4 would print differently) with halves rounded up, as JavaScript's
toFixed does; f1() stops if Python's own format would print it differently, so the page and its tool can't disagree.

usage: python3 gen_bfcalc.py REPO_ROOT STATS_JSON
Runs once, on body-fat-calculator/index.html as it stood at f365b8b (the B2 page); kept as the build record. The page is
written with {TODAY} in its WebPage dateModified; apply_build.py puts in the apply date (manifest "today": true).
"""
import sys, os, re, json, html, math, csv
from decimal import Decimal, ROUND_HALF_UP

ROOT, STATS = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
P = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
PAGE = os.path.join(ROOT, 'body-fat-calculator/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()

SITE = 'https://calculatemybmi.net'
URL = SITE + '/body-fat-calculator/'

# ---------------------------------------------------------------- formatting (round once, halves up)
def half(x, nd=1):
    return Decimal(x).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
def f1(x):
    s = str(half(x))
    assert s == f'{x:.1f}' or (s == '0.0' and f'{x:.1f}' == '-0.0'), ('a tie: JavaScript and Python would print differently', x)
    return s
def sg(x):                                                    # signed, with a real minus sign
    s = f1(x)
    return ('−' + s[1:]) if s.startswith('-') else ('+' + s)
def pc(x):                                                    # a share as a whole percent, rounded once
    return int(half(x, 0))
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10        # the tool's r1()
def esc(s): return html.escape(s, quote=False)

# ---------------------------------------------------------------- the formulas (the tool's own, mirrored here)
LG = math.log10
def navy(sex, h, neck, waist, hips=0.0):
    """Hodgdon & Beckett 1984, inches (registry body-fat-equations)."""
    if sex == 'm': return 86.010 * LG(waist - neck) - 70.041 * LG(h) + 36.76
    return 163.205 * LG(waist + hips - neck) - 97.684 * LG(h) - 78.387
def rfm(sex, h, waist):
    """Woolcott & Bergman 2018: 64 - 20 x height / waist + 12 x sex (sex 1 = women), any one unit."""
    return 64 - 20 * h / waist + (12 if sex == 'f' else 0)
def deur(sex, bmi, age):
    """Deurenberg et al. 1991, adults: 1.20 x BMI + 0.23 x age - 10.8 x sex - 5.4 (sex 1 = men)."""
    return 1.20 * bmi + 0.23 * age - 10.8 * (1 if sex == 'm' else 0) - 5.4
def jp(sex, k, s, age):
    """Jackson & Pollock (men 1978) and Jackson, Pollock & Ward (women 1980), 3 or 7 skinfolds, then Siri 495/D - 450."""
    if k == 7:
        d = (1.112 - 0.00043499 * s + 0.00000055 * s * s - 0.00028826 * age if sex == 'm'
             else 1.097 - 0.00046971 * s + 0.00000056 * s * s - 0.00012828 * age)
    else:
        d = (1.10938 - 0.0008267 * s + 0.0000016 * s * s - 0.0002574 * age if sex == 'm'
             else 1.0994921 - 0.0009929 * s + 0.0000023 * s * s - 0.0001392 * age)
    return 495 / d - 450

# The equations' own checks (registry body-fat-equations): the Army's Table B-5 worked examples (46.73% and 38.62% by
# hand with rounded logarithms, reported as 47% and 39%) and the published JP3 density 1.0597633 (sum 53 mm, age 40).
ARMY_F, ARMY_M = navy('f', 64, 15, 42, 44), navy('m', 69, 16, 49)
assert (f1(ARMY_F), f1(ARMY_M), int(half(ARMY_F, 0)), int(half(ARMY_M, 0))) == ('47.3', '38.6', 47, 39)
assert abs(1.10938 - 0.0008267 * 53 + 0.0000016 * 53 * 53 - 0.0002574 * 40 - 1.0597633) < 1e-7
# Centimeters typed into the inch equations (FAQ): the same two people.
CM_F = navy('f', 64 * 2.54, 15 * 2.54, 42 * 2.54, 44 * 2.54) - ARMY_F
CM_M = navy('m', 69 * 2.54, 16 * 2.54, 49 * 2.54) - ARMY_M
assert (f1(CM_M), f1(CM_F)) == ('6.5', '26.5'), (CM_M, CM_F)

# ---------------------------------------------------------------- our check on CDC's scans (bfc_stats.json)
F, PAIR, META = S['formulas'], S['paired'], S['meta']
assert META['n_scanned_20_59'] == 10864 and META['df'] == 62
SX = ('women', 'men')
SK = {'women': 'f', 'men': 'm'}                              # the tool's keys
def excl0(ci): return ci[0] > 0 or ci[1] < 0
W5 = {f: {s: pc(F[f][s]['within5']['pct']) for s in SX} for f in ('rfm', 'deur')}
W3 = {f: {s: F[f][s]['within3']['pct'] for s in SX} for f in ('rfm', 'deur')}
assert W5 == {'rfm': {'women': 74, 'men': 86}, 'deur': {'women': 62, 'men': 66}}, W5
MAE = {f: {s: F[f][s]['mae']['mean'] for s in SX} for f in ('rfm', 'deur')}
BIAS = {f: {s: F[f][s]['bias'] for s in SX} for f in ('rfm', 'deur')}
assert all(excl0(BIAS['rfm'][s]['ci95']) and BIAS['rfm'][s]['mean'] > 0 for s in SX)          # RFM reads high
assert not any(excl0(BIAS['deur'][s]['ci95']) for s in SX)                                    # Deurenberg: about right
assert (sg(BIAS['rfm']['women']['mean']), sg(BIAS['rfm']['men']['mean'])) == ('+2.3', '+0.7')
assert (f1(MAE['rfm']['women']), f1(MAE['rfm']['men']), f1(MAE['deur']['women']), f1(MAE['deur']['men'])) == \
       ('3.5', '2.7', '4.7', '4.2')
NCK = {f: {s: F[f][s]['n'] for s in SX} for f in ('rfm', 'deur')}
assert NCK == {'rfm': {'women': 5388, 'men': 5363}, 'deur': {'women': 5446, 'men': 5383}}, NCK
N_RFM, N_DEU = sum(NCK['rfm'].values()), sum(NCK['deur'].values())
MED_ERR = {f: {s: F[f][s]['err_q']['p50'] for s in SX} for f in ('rfm', 'deur')}
assert (f1(MED_ERR['rfm']['women']), f1(MED_ERR['rfm']['men'])) == ('2.3', '0.8')
MED_CI = {s: F['rfm'][s]['err_median_ci95'] for s in SX}
# The two formulas in the same people: RFM came within 5 points for more of them, and missed by less.
PW5 = {s: PAIR[s]['within5_rfm_minus_deur'] for s in SX}
PMAE = {s: PAIR[s]['mae_rfm_minus_deur'] for s in SX}
assert all(excl0(PW5[s]['ci95']) and PW5[s]['mean'] > 0 and excl0(PMAE[s]['ci95']) and PMAE[s]['mean'] < 0 for s in SX)
PW5N = {s: pc(PW5[s]['mean']) for s in SX}
assert PW5N == {'women': 12, 'men': 20}, PW5N
# By BMI and age group: every value stated in the text has a 95% CI that excludes 0; the one that doesn't is named.
GROUPS = (('healthy', 'BMI 18.5–24.9'), ('over', 'BMI 25–29.9'), ('obese', 'BMI 30 and over'),
          ('20-39', 'Ages 20–39'), ('40-59', 'Ages 40–59'))
def grp_bias(f, s, k):
    r = F[f][s]['by_bmi'][k]['bias'] if k in ('healthy', 'over', 'obese') else F[f][s]['by_age'][k]['bias']
    return r
NOT_EXCL = [(f, s, k) for f in ('deur', 'rfm') for s in SX for k, _ in GROUPS if not excl0(grp_bias(f, s, k)['ci95'])]
assert NOT_EXCL == [('rfm', 'men', 'healthy')], NOT_EXCL
DB = {(s, k): grp_bias('deur', s, k)['mean'] for s in SX for k, _ in GROUPS}
assert [sg(DB[(s, k)]) for s in SX for k in ('healthy', 'obese', '20-39', '40-59')] == \
       ['−3.1', '+4.1', '−2.2', '+1.7', '−2.9', '+2.9', '−2.3', '+2.1']
# Calibration: CDC's scans in people whose formula gave an estimate within a point of each whole percent (n >= 30).
CAL = {f: {SK[s]: {int(b): [float(f1(x)) for x in v['q']] + [v['n']] for b, v in F[f][s]['calib'].items()} for s in SX}
       for f in ('rfm', 'deur')}
assert min(CAL['rfm']['f']) == 27 and max(CAL['rfm']['f']) == 54 and min(CAL['deur']['m']) == 10

# ---------------------------------------------------------------- US adults and the provisional ranges (bfpc_stats.json)
BA = P['by_age']
GAL = {k: {g: tuple(v) for g, v in d.items()} for k, d in P['gallagher']['cuts'].items()}
assert GAL['f']['20-39'] == (21, 33, 39) and GAL['m']['20-39'] == (8, 20, 25)
MEAN_F, MEAN_M = f'{BA["f"]["20-59"]["mean4"]:.1f}', f'{BA["m"]["20-59"]["mean4"]:.1f}'   # as the chart page prints them
assert (MEAN_F, MEAN_M) == ('38.7', '27.2')
UGR = ('16-19', '20-29', '30-39', '40-49', '50-59')
# As the chart's rank tool: percentiles as its tables print them, shares interpolated between whole percents.
TQ = {k: {g: [float(f'{BA[k][g][p]:.1f}') for p in ('p10', 'p25', 'p50', 'p75', 'p90')] for g in UGR} for k in 'fm'}
TN = {k: {g: BA[k][g]['n'] for g in UGR} for k in 'fm'}
MORE = {k: {g: P['tool']['more'][k][g] for g in UGR} for k in 'fm'}
P0 = P['tool']['percents'][0]
def more_at(arr, v):
    i, fr = math.floor(v) - P0, v - math.floor(v)
    if i < 0: return arr[0]
    if i >= len(arr) - 1: return arr[-1]
    return arr[i] + (arr[i + 1] - arr[i]) * fr
def cat(v, c): return 'low' if v < c[0] else 'healthy' if v < c[1] else 'high' if v < c[2] else 'very high'
def rng(c, k): return {'low': f'under {c[0]}%', 'healthy': f'{c[0]}–{c[1] - 0.1:.1f}%', 'high': f'{c[1]}–{c[2] - 0.1:.1f}%',
                       'very high': f'{c[2]}% or more'}[k]
def share_txt(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{int(half(x, 0))}%'

# ---------------------------------------------------------------- published comparisons (verified in chat 2026-10-28)
# Foulis SA et al., Front Physiol 2023;14:1183836 (abstract): 481 women and 926 men, Army basic combat training; before
#   training, circumference %BF vs DXA mean errors "-6.0%±4.4% for women and -6.0%±3.5% for men (both p<0.01)"; text:
#   "Current circumference-based methodology ... was developed by the Navy in 1984" (Hodgdon and Beckett); men measured
#   at the neck and the abdomen at the umbilicus, women at the neck, the narrowest part of the torso and the widest part
#   of the buttocks.
FOULIS = {'n': 481 + 926, 'err': '6.0', 'sd_w': '4.4', 'sd_m': '3.5'}
# Burns RD, Fu Y, Constantino N, PLOS ONE 2019;14(3):e0214029 (registry body-fat-method-validation): 437 college students
#   (301 women, 136 men), mean age 19.2; seven-site skinfolds (chest, midaxillary, triceps, subscapular, abdomen,
#   suprailiac, thigh; Lange caliper; Siri; "Trained graduate students performed the skinfolds thickness measurements");
#   Table 3 "Mean Difference (DXA–Surrogate; % Body Fat)" 1.4% for skinfolds, so skinfolds read 1.4 points below DXA on
#   average (fact-check CMB-020: a signed mean, not a typical miss); MAPE "ranged from 11.7% using skinfold thickness to
#   21.9% using the Omron BIA", the lowest of the seven methods (hydrostatic weighing had the smaller mean difference, 1.0).
BURNS = {'n': 437, 'age': '19', 'diff': '1.4', 'mape': '11.7'}
# Deurenberg P, Weststrate JA, Seidell JC, Br J Nutr 1991;65:105-14 (abstract): 1,229 subjects (521 men, 708 women),
#   ages 7-83, body fat by densitometry; children 15 and under get their own formula; adult formula SEE 4.1% (R2 0.79);
#   "slightly overestimated" body fat in obese subjects; prediction error comparable to skinfolds and impedance.
DEUR91 = {'n': '1,229', 'see': '4.1'}
# Woolcott OO, Bergman RN, Sci Rep 2018;8:10980: developed on NHANES 1999-2004 (n = 12,581) and validated on 2005-2006
#   (n = 3,456) against DXA (Hologic QDR 4500A); adults 20 and over; waist "at the level of the uppermost lateral border of
#   the right ilium"; validation ages 20 to 69; bias "the median difference between estimated and measured body fat
#   percentage", Table 2: women 0.9 (95% CI 0.6 to 1.1), men 0.5 (0.3 to 0.8). Cedars-Sinai (the authors' center): "put
#   the tape measure at the top of your hip bone".
WB18 = {'dev': '12,581', 'val': '3,456', 'bias_w': '0.9', 'bias_m': '0.5', 'ci_w': (0.6, 1.1), 'ci_m': (0.3, 0.8)}
# US Army DA Form 5500 (male) and 5501 (female), MAY 2013: "Measure neck just below level of larynx (Adam's apple)";
#   men "Measure abdomen at the level of the navel (belly button.)"; women "waist (abdomen) at the point of minimal
#   abdominal circumference" and "hips at point where the gluteus muscles (buttocks) protrude backward the most";
#   each "Repeat three times, then average to the nearest 0.50 inch." Army.mil, 2023-06-12: Army Directive 2023-11
#   "requires tape testing at only one site on the body" (the multi-site method stays authorized for 12 months).
# CDC NHANES DXX_J documentation: "Dual-energy x-ray absorptiometry (DXA) is the most widely accepted method of measuring
#   body composition"; Hologic Discovery model A; ages 8-59 eligible.
# Topend Sports (Robert Wood), "Jackson-Pollock body density": all four equations as above, the women's 3-site age term
#   0.0001392, citing Jackson & Pollock 1978 and Jackson, Pollock & Ward 1980. Serra AJ et al., ConScientiae Saude
#   2009;8(1):19-24: the same equations, but the women's 3-site age term printed 0.0001395 (fact-check CMB-020: the page
#   had cited Serra for 0.0001392), Siri 495/D - 450.

# ---------------------------------------------------------------- links (every outside link is a registry row's)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
REG = {r['domain']: r for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}
U = {
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'army': 'https://cdn.clinicaltrials.gov/large-docs/38/NCT02734238/Prot_SAP_000.pdf',
    'jp': 'https://periodicos.uninove.br/saude/article/download/1421/1197',
    'deur': 'https://pubmed.ncbi.nlm.nih.gov/2043597/',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'jpha': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5349253/table/table001',
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
    'rfm': 'https://doi.org/10.1038/s41598-018-29362-1',
    'cedars': 'https://www.cedars-sinai.org/stories-and-insights/healthy-living/relative-fat-mass',
    'foulis': 'https://doi.org/10.3389/fphys.2023.1183836',
    'da5500': 'https://home.army.mil/stewart/index.php/download_file/force/6943/434',
    'da5501': 'https://home.army.mil/stewart/index.php/download_file/force/6944/434',
    'army23': 'https://www.army.mil/article/267486',
    'topend': 'https://www.topendsports.com/testing/density-jackson-pollock.htm',
}
assert REG['nhanes-2011-2018-dxa']['url'] == U['dxx'] and REG['body-fat-equations']['url'] == U['army']
assert U['jp'] in REG['body-fat-equations']['endpoint'] and U['deur'] in REG['body-fat-equations']['endpoint']
assert REG['gallagher-2000-bf-ranges']['url'] == U['gallagher'] and REG['gallagher-2000-bf-ranges']['endpoint'] == U['jpha']
assert REG['body-fat-method-validation']['url'] == U['burns']
for d, k in (('rfm-woolcott-2018', 'rfm'), ('foulis-2023-circumference-dxa', 'foulis'), ('army-tape-worksheets', 'da5500')):
    assert REG[d]['url'] == U[k], d                               # the rows patch_cmb020.py adds
assert U['cedars'] in REG['rfm-woolcott-2018']['endpoint'] and U['da5501'] in REG['army-tape-worksheets']['endpoint']
assert U['army23'] in REG['army-tape-worksheets']['notes'] and U['topend'] in REG['body-fat-equations']['endpoint']

# ---------------------------------------------------------------- the worked example: the calculator's starting values
EX_AGE, EX_H, EX_LB = 35, 64, 150
EX_NECK, EX_WAIST, EX_HIPS, EX_RWAIST = 13, 31, 40, 34
EX_TAPE = navy('f', EX_H, EX_NECK, EX_WAIST, EX_HIPS)
EX_BMI = r1(703 * EX_LB / EX_H ** 2)
EX_DEUR = deur('f', EX_BMI, EX_AGE)
EX_RFM = rfm('f', EX_H, EX_RWAIST)
assert (f1(EX_TAPE), EX_BMI, f1(EX_DEUR), f1(EX_RFM)) == ('33.0', 25.7, '33.5', '38.4')
def calbin(v): return math.floor(r1(v) + 0.5)
EX_BD, EX_BR = calbin(EX_DEUR), calbin(EX_RFM)
EX_CD, EX_CR = CAL['deur']['f'][EX_BD], CAL['rfm']['f'][EX_BR]
assert (EX_BD, EX_BR) == (34, 38) and EX_CD == [34.0, 36.8, 39.5, 446] and EX_CR == [33.7, 36.1, 38.5, 543], (EX_CD, EX_CR)
EX_G, EX_GG = '30-39', '20-39'
EX_MORE = more_at(MORE['f'][EX_G], r1(EX_TAPE))
EX_CAT = cat(r1(EX_TAPE), GAL['f'][EX_GG])
assert share_txt(EX_MORE) == '79%' and EX_CAT == 'high' and TQ['f'][EX_G][2] == 38.9
EX_FAT = EX_LB * r1(EX_TAPE) / 100
EX_LEAN = EX_LB - EX_FAT
def kg(lb): return f1(lb * 0.45359237)
assert (f1(EX_FAT), kg(EX_FAT), f1(EX_LEAN), kg(EX_LEAN)) == ('49.5', '22.5', '100.5', '45.6')
EX_CM, EX_KG = f1(EX_H * 2.54), kg(EX_LB)
assert (EX_CM, EX_KG) == ('162.6', '68.0')

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS, VBW = [], [], {}
def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827'):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'
def track(svg, x0, y0, x1, y1): RECTS.append((svg, x0, y0, x1, y1))
SER = {'women': '#be185d', 'men': '#4338ca'}
BASE = {'low': '#3b82f6', 'healthy': '#22c55e', 'high': '#f59e0b', 'very high': '#ef4444'}
INK, MUTED, GRID = '#111827', '#4b5563', '#e5e7eb'

# Figure 1, the worked example: one woman, three estimates; for the two formulas checked on CDC's scans, the middle half
# and median of the scans of US women whose formula gave about the same estimate.
VBW['ex'] = 320
EX0, EX1, ELO, EHI = 14, 306, 20, 50
def exx(v): return EX0 + (v - ELO) * (EX1 - EX0) / (EHI - ELO)
fe = []
ROWS_EX = (('Tape measure', EX_TAPE, None), ('Height and weight', EX_DEUR, EX_CD), ('Waist and height', EX_RFM, EX_CR))
for i, (lab_, v, c) in enumerate(ROWS_EX):
    yl = 14 + i * 42; ym = yl + 16
    fe.append(text('ex', 4, yl, f'{lab_}: {f1(v)}%', 12, anchor='start', weight=600, fill='#1f2937'))
    if c:
        fe.append(f'<rect x="{exx(c[0]):.1f}" y="{ym - 7}" width="{exx(c[2]) - exx(c[0]):.1f}" height="14" rx="2" '
                  f'fill="{SER["women"]}" fill-opacity="0.16" stroke="{SER["women"]}" stroke-width="1"><title>'
                  f'{esc(f"CDC scans of US women whose {lab_.lower()} estimate was within a point of {calbin(v)}%: middle half {c[0]:.1f}–{c[2]:.1f}%, median {c[1]:.1f}% ({c[3]} women)")}'
                  '</title></rect>')
        track('ex', exx(c[0]), ym - 7, exx(c[2]), ym + 7)
        fe.append(f'<line x1="{exx(c[1]):.1f}" y1="{ym - 10}" x2="{exx(c[1]):.1f}" y2="{ym + 10}" stroke="{INK}" stroke-width="2.5"/>')
    fe.append(f'<circle cx="{exx(r1(v)):.1f}" cy="{ym}" r="5" fill="{INK}" stroke="#ffffff" stroke-width="1.5"/>')
    track('ex', exx(r1(v)) - 5, ym - 5, exx(r1(v)) + 5, ym + 5)
YR = 14 + 3 * 42
fe.append(text('ex', 4, YR, 'Provisional ranges, women aged 20 to 39', 12, anchor='start', fill='#1f2937'))
edges = [ELO, *GAL['f']['20-39'], EHI]
for j, k in enumerate(('low', 'healthy', 'high', 'very high')):
    a, b = edges[j], edges[j + 1]
    fe.append(f'<rect x="{exx(a) + (1 if j else 0):.1f}" y="{YR + 7}" width="{exx(b) - exx(a) - (2 if 0 < j < 3 else 1):.1f}" '
              f'height="8" rx="2" fill="{BASE[k]}"><title>{k.capitalize()}: {rng(GAL["f"]["20-39"], k)}</title></rect>')
    track('ex', exx(a), YR + 7, exx(b), YR + 15)
YAX = YR + 34
for t in range(ELO, EHI + 1, 5):
    fe.append(text('ex', exx(t), YAX, f'{t}%', 12, fill=MUTED))
H_EX = YAX + 8
svg_ex = (f'<svg viewBox="0 0 320 {H_EX}" role="img" aria-labelledby="ex-t ex-d" xmlns="http://www.w3.org/2000/svg" '
          'font-family="inherit"><title id="ex-t">One woman, three body fat estimates</title><desc id="ex-d">'
          f'A woman of {EX_AGE}, 5 feet 4 inches and {EX_LB} pounds. The tape measure gives {f1(EX_TAPE)}%, the height-and-weight '
          f'formula {f1(EX_DEUR)}% and the waist-and-height formula {f1(EX_RFM)}%. Among US women whose height-and-weight '
          f'estimate was within a point of {EX_BD}%, the middle half of CDC’s scans read {EX_CD[0]:.1f}% to {EX_CD[2]:.1f}% '
          f'(median {EX_CD[1]:.1f}%); for a waist-and-height estimate within a point of {EX_BR}%, {EX_CR[0]:.1f}% to '
          f'{EX_CR[2]:.1f}% (median {EX_CR[1]:.1f}%). Below, the provisional ranges for women aged 20 to 39: low under 21%, '
          'healthy 21% to 32.9%, high 33% to 38.9%, very high 39% or more.</desc>' + ''.join(fe) + '</svg>')

# Figure 2, the accuracy figure: formula minus scan for both formulas and both sexes (10th-90th line, middle half,
# median), against a dashed zero line.
VBW['acc'] = 320
AX0, AX1, ALO, AHI = 16, 304, -10, 10
def ax(e): return AX0 + (e - ALO) * (AX1 - AX0) / (AHI - ALO)
fa = []
ROWS_ACC = (('rfm', 'women', 'Waist and height, women'), ('rfm', 'men', 'Waist and height, men'),
            ('deur', 'women', 'Height and weight, women'), ('deur', 'men', 'Height and weight, men'))
YB = 14 + 4 * 46
for i, (f, s, lab_) in enumerate(ROWS_ACC):
    q = F[f][s]['err_q']; col = SER[s]
    yl = 14 + i * 46; ym = yl + 16
    fa.append(text('acc', 4, yl, f'{lab_}: median {sg(q["p50"])}', 12, anchor='start', weight=600, fill='#1f2937'))
    for e in (-10, -5, 5, 10):                                   # light grid and the dashed zero line, row by row, so no
        fa.append(f'<line x1="{ax(e):.1f}" y1="{ym - 12}" x2="{ax(e):.1f}" y2="{ym + 12}" stroke="{GRID}" stroke-width="1"/>')
    fa.append(f'<line x1="{ax(0):.1f}" y1="{ym - 12}" x2="{ax(0):.1f}" y2="{ym + 12}" stroke="{MUTED}" stroke-width="1.5" '
              'stroke-dasharray="4 3"/>')                        # line crosses a label
    track('acc', ax(0) - 1, ym - 12, ax(0) + 1, ym + 12)
    fa.append(f'<line x1="{ax(q["p10"]):.1f}" y1="{ym}" x2="{ax(q["p90"]):.1f}" y2="{ym}" stroke="{col}" stroke-width="1.5"/>')
    tip = (f'{lab_}: formula minus scan, 10th to 90th percentile {sg(q["p10"])} to {sg(q["p90"])} points, middle half '
           f'{sg(q["p25"])} to {sg(q["p75"])}, median {sg(q["p50"])} ({F[f][s]["n"]:,} people)')
    fa.append(f'<rect x="{ax(q["p25"]):.1f}" y="{ym - 7}" width="{ax(q["p75"]) - ax(q["p25"]):.1f}" height="14" rx="2" '
              f'fill="{col}" fill-opacity="0.16" stroke="{col}" stroke-width="1"><title>{esc(tip)}</title></rect>')
    track('acc', ax(q['p10']), ym - 9, ax(q['p90']), ym + 9)
    fa.append(f'<line x1="{ax(q["p50"]):.1f}" y1="{ym - 9}" x2="{ax(q["p50"]):.1f}" y2="{ym + 9}" stroke="{INK}" stroke-width="2.5"/>')
for e in (-10, -5, 0, 5, 10):
    fa.append(text('acc', ax(e), YB + 6, ('−' if e < 0 else '+' if e > 0 else '') + str(abs(e)), 12, fill=MUTED))
fa.append(text('acc', 160, YB + 24, 'Formula minus scan, percentage points', 12, fill='#1f2937'))
H_ACC = YB + 32
svg_acc = (f'<svg viewBox="0 0 320 {H_ACC}" role="img" aria-labelledby="acc-t acc-d" xmlns="http://www.w3.org/2000/svg" '
           'font-family="inherit"><title id="acc-t">How far two body fat formulas were from DXA scans of US adults</title>'
           '<desc id="acc-d">Formula minus scan, in percentage points, for US adults aged 20 to 59 on CDC’s DXA scans, '
           '2011 to 2018. ' + ' '.join(
               f'{lab_}: median {sg(F[f][s]["err_q"]["p50"])}, middle half {sg(F[f][s]["err_q"]["p25"])} to '
               f'{sg(F[f][s]["err_q"]["p75"])}, 10th to 90th percentile {sg(F[f][s]["err_q"]["p10"])} to '
               f'{sg(F[f][s]["err_q"]["p90"])}.' for f, s, lab_ in ROWS_ACC)
           + ' Right of the dashed line, the formula read higher than the scan. Our calculation.</desc>' + ''.join(fa) + '</svg>')

def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r): raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- the calculator card and its script
def fg(lab_, iid, val=None, mn=None, mx=None, step='0.1', mode='decimal', ph=None, extra=''):
    v = f' value="{val}"' if val is not None else ''
    p = f' placeholder="{ph}"' if ph else ''
    rg = (f' min="{mn}"' if mn is not None else '') + (f' max="{mx}"' if mx is not None else '')
    return (f'<div class="form-group"{extra}><label class="form-label" for="{iid}" id="{iid}-l">{lab_}</label><input type="number" '
            f'id="{iid}" class="form-input" inputmode="{mode}"{rg} step="{step}"{v}{p}></div>')
SF = (('chest', 'Chest'), ('midax', 'Midaxillary'), ('tri', 'Triceps'), ('sub', 'Subscapular'), ('abd', 'Abdomen'),
      ('supra', 'Suprailiac'), ('thigh', 'Thigh'))
SF3 = {'f': ('tri', 'supra', 'thigh'), 'm': ('chest', 'abd', 'thigh')}
calc = (
    '<div class="calculator-card bfc" id="bfc"><div class="calc-panel active">'
    '<div class="bfc-toggles"><div class="unit-toggle" role="group" aria-label="Sex"><button type="button" class="unit-btn active" '
    'data-sex="f" aria-pressed="true">Woman</button><button type="button" class="unit-btn" data-sex="m" aria-pressed="false">Man'
    '</button></div><div class="unit-toggle" role="group" aria-label="Units"><button type="button" class="unit-btn active" '
    'data-units="us" aria-pressed="true">US</button><button type="button" class="unit-btn" data-units="metric" '
    'aria-pressed="false">Metric</button></div></div>'
    '<div class="unit-toggle unit-toggle--methods" role="group" aria-label="Method">'
    '<button type="button" class="unit-btn active" data-method="tape" aria-pressed="true">Tape measure</button>'
    '<button type="button" class="unit-btn" data-method="rfm" aria-pressed="false">Waist and height</button>'
    '<button type="button" class="unit-btn" data-method="bmi" aria-pressed="false">Height and weight</button>'
    '<button type="button" class="unit-btn" data-method="sf" aria-pressed="false">Calipers</button></div>'
    '<div class="form-grid">'
    '<div class="form-row form-row--pair" id="bfc-us">' + fg('Height (ft)', 'bfc-ft', 5, 4, 7, '1', 'numeric')
    + fg('Height (in)', 'bfc-in', 4, 0, 11.9) + '</div>'
    '<div class="form-row" id="bfc-metric" hidden>' + fg('Height (cm)', 'bfc-cm', EX_CM, 122, 229) + '</div>'
    '<div class="form-row form-row--pair">' + fg('Weight (lb)', 'bfc-w', EX_LB, 23, 700, ph='Optional')
    + fg('Age (years)', 'bfc-age', EX_AGE, 18, 79, '1', 'numeric') + '</div>'
    '<div class="bfc-pane" id="bfc-p-tape"><div class="form-row form-row--trio">'
    + fg('Neck (in)', 'bfc-neck', EX_NECK, 8, 76) + fg('Waist (in)', 'bfc-waist', EX_WAIST, 15, 203)
    + fg('Hips (in)', 'bfc-hips', EX_HIPS, 20, 203, extra=' id="bfc-hips-g"') + '</div>'
    '<p class="form-hint" id="bfc-tape-hint">Neck just below the Adam’s apple, waist at its narrowest, hips where the buttocks '
    'stick out most.</p></div>'
    '<div class="bfc-pane" id="bfc-p-rfm" hidden><div class="form-row">' + fg('Waist (in)', 'bfc-rwaist', None, 15, 203)
    + '</div><p class="form-hint">Measure at the top of your hip bones, where CDC’s survey measures the waist.</p></div>'
    '<div class="bfc-pane" id="bfc-p-bmi" hidden><p class="form-hint">Uses your height, weight, age and sex: enter your weight '
    'above.</p></div>'
    '<div class="bfc-pane" id="bfc-p-sf" hidden><div class="unit-toggle" role="group" aria-label="Skinfold sites">'
    '<button type="button" class="unit-btn active" data-sites="3" aria-pressed="true">3 sites</button><button type="button" '
    'class="unit-btn" data-sites="7" aria-pressed="false">7 sites</button></div><div class="form-row form-row--trio">'
    + ''.join(fg(t, f'bfc-sf-{k}', None, 1, 100, '0.5', extra=f' id="bfc-sf-{k}-g"') for k, t in SF)
    + '</div><p class="form-hint">Each skinfold in millimeters.</p></div>'
    '</div><button type="button" class="calculate-btn" id="bfc-go">Calculate body fat</button>'
    '<div class="results-section" id="bfc-out" aria-live="polite"></div></div></div>'
    '<noscript><p>The calculator needs JavaScript. The formulas for each method are below: '
    '<a href="#tape">tape measure</a>, <a href="#rfm">waist and height</a>, <a href="#bmi-method">height and weight</a> '
    'and <a href="#calipers">calipers</a>.</p></noscript>')

TOOL = {'p0': P0, 'more': MORE, 'q': TQ, 'n': TN, 'gal': {k: {g: list(v) for g, v in d.items()} for k, d in GAL.items()},
        'cal': {f: {s: {str(b): v for b, v in sorted(d.items())} for s, d in CAL[f].items()} for f in CAL},
        'w5': {f: {SK[s]: W5[f][s] for s in SX} for f in W5},
        'rb': {SK[s]: sg(BIAS['rfm'][s]['mean'])[1:] for s in SX},
        'pub': {'foulis': FOULIS, 'burns': BURNS}}
# The tool's rules, mirrored by bfcalc_test_playwright.py:
#  - the unit switch converts every length to 0.1 (cm or in) and the weight to 0.1 (kg or lb); switching back with nothing
#    retyped restores the numbers as they were, so a round trip never changes a result (fact-check CMB-020: whole
#    centimeters had turned the starting 33.0% into 32.9%).
#  - height: ft + in, or cm / 2.54; 4 ft to 7 ft 6 in (122 to 229 cm). Age 18 to 79 (whole years). Weight optional, 50 to
#    700 lb or 23 to 318 kg; the height-and-weight method needs it. Tape: neck 8-30 in (20-76 cm), waist 15-80 in (38-203 cm),
#    hips 20-80 in (51-203 cm); the equations take inches, so centimeters are divided by 2.54. Skinfolds 1 to 100 mm.
#  - BMI as the calculators: 703 x lb / in^2 or kg / m^2, rounded half up to 0.1; the height-and-weight formula uses it.
#  - an estimate prints to 0.1 (halves up); the category, the US share, the calibration window and the fat mass all
#    come from the printed value. An estimate under 2% or over 70% is refused as a measuring or unit slip.
#  - calibration: the window is the printed estimate's nearest whole percent b (people whose formula gave b - 1 to under
#    b + 1); windows with fewer than 30 people say so.
#  - "Your other estimates" lists the other methods the entered numbers allow; a method pane counts only once its fields
#    were typed in (the starting tape values belong to the worked example), the height-and-weight formula whenever a
#    weight is entered.
TOOL_JS = r'''(function(){var D=window.BFC,$=function(i){return document.getElementById(i);};
var sex='f',units='us',method='tape',sites='3',out=$('bfc-out'),touched={tape:false,rfm:false,sf:false};
var BASE={low:'#3b82f6',healthy:'#22c55e',high:'#f59e0b','very high':'#ef4444'},SER={f:'#be185d',m:'#4338ca'};
var CARD={low:'underweight',healthy:'normal',high:'overweight','very high':'obese'};
var NAME={tape:'Tape measure (Navy method)',rfm:'Waist and height (relative fat mass)',bmi:'Height and weight (Deurenberg formula)',sf3:'Calipers, 3 sites (Jackson–Pollock)',sf7:'Calipers, 7 sites (Jackson–Pollock)'};
var SHORT={tape:'Tape measure',rfm:'Waist and height',bmi:'Height and weight',sf3:'Calipers, 3 sites',sf7:'Calipers, 7 sites'};
var SF={f3:['tri','supra','thigh'],m3:['chest','abd','thigh'],a7:['chest','midax','tri','sub','abd','supra','thigh']};
function nd(s){return s.replace('-','–');}
function r1(x){return Math.floor(x*10+0.5+1e-9)/10;}
function d1(x){return r1(x).toFixed(1);}
function lg(x){return Math.log(x)/Math.LN10;}
function num(id){var v=parseFloat($(id).value);return v>0?v:0;}
function grp(a){return a<=19?'16-19':a<=29?'20-29':a<=39?'30-39':a<=49?'40-49':a<=59?'50-59':null;}
function ggrp(a){return a>=20&&a<=39?'20-39':a>=40&&a<=59?'40-59':a>=60&&a<=79?'60-79':null;}
function moreAt(arr,v){var i=Math.floor(v)-D.p0,f=v-Math.floor(v);if(i<0)return arr[0];if(i>=arr.length-1)return arr[arr.length-1];return arr[i]+(arr[i+1]-arr[i])*f;}
function shareTxt(x){return x>=99.5?'more than 99%':x<=0.5?'under 1%':Math.round(x)+'%';}
function cat(v,c){return v<c[0]?'low':v<c[1]?'healthy':v<c[2]?'high':'very high';}
function rangeTxt(c,k){return k==='low'?'under '+c[0]+'%':k==='healthy'?c[0]+'–'+(c[1]-0.1).toFixed(1)+'%':k==='high'?c[1]+'–'+(c[2]-0.1).toFixed(1)+'%':c[2]+'% or more';}
function word(s,a){return a<20?(s==='f'?'girls':'boys'):(s==='f'?'women':'men');}
function navy(s,h,n,w,hp){return s==='m'?86.010*lg(w-n)-70.041*lg(h)+36.76:163.205*lg(w+hp-n)-97.684*lg(h)-78.387;}
function rfm(s,h,w){return 64-20*h/w+(s==='f'?12:0);}
function deur(s,b,a){return 1.20*b+0.23*a-10.8*(s==='m'?1:0)-5.4;}
function jp(s,k,sum,a){var d=k==='7'?(s==='m'?1.112-0.00043499*sum+0.00000055*sum*sum-0.00028826*a:1.097-0.00046971*sum+0.00000056*sum*sum-0.00012828*a):(s==='m'?1.10938-0.0008267*sum+0.0000016*sum*sum-0.0002574*a:1.0994921-0.0009929*sum+0.0000023*sum*sum-0.0001392*a);return 495/d-450;}
function fig(v,q,c,s){var W=280,P=14,qa=q||[v,v,v,v,v],lo=Math.min(10,Math.floor(Math.min(qa[0],v)/5)*5),hi=Math.max(50,Math.ceil(Math.max(qa[4],v)/5)*5),
 X=function(x){return P+(x-lo)*(W-2*P)/(hi-lo);},g='',t,lx;
 if(q){g+='<rect x="'+X(q[0]).toFixed(1)+'" y="26" width="'+(X(q[4])-X(q[0])).toFixed(1)+'" height="18" rx="3" fill="'+SER[s]+'" fill-opacity="0.18"/>';
  g+='<rect x="'+X(q[1]).toFixed(1)+'" y="26" width="'+(X(q[3])-X(q[1])).toFixed(1)+'" height="18" rx="3" fill="'+SER[s]+'" fill-opacity="0.45"/>';
  g+='<line x1="'+X(q[2]).toFixed(1)+'" y1="23" x2="'+X(q[2]).toFixed(1)+'" y2="47" stroke="#111827" stroke-width="2"/>';}
 if(c){var e=[lo,c[0],c[1],c[2],hi],ks=['low','healthy','high','very high'];for(var i=0;i<4;i++){var a=Math.max(e[i],lo),b=Math.min(e[i+1],hi);if(b>a)g+='<rect x="'+(X(a)+(i?1:0)).toFixed(1)+'" y="54" width="'+(X(b)-X(a)-(i&&i<3?2:1)).toFixed(1)+'" height="8" rx="2" fill="'+BASE[ks[i]]+'"/>';}}
 g+='<line x1="'+X(v).toFixed(1)+'" y1="18" x2="'+X(v).toFixed(1)+'" y2="'+(c?66:50)+'" stroke="#111827" stroke-width="2" stroke-dasharray="3 2"/>';
 t='You '+v.toFixed(1)+'%';lx=Math.min(Math.max(X(v),t.length*3.6+2),W-t.length*3.6-2);
 g+='<text x="'+lx.toFixed(1)+'" y="13" font-size="12" text-anchor="middle" fill="#1f2937">'+t+'</text>';
 for(var x=lo;x<=hi;x+=10)g+='<text x="'+X(x).toFixed(1)+'" y="82" font-size="12" text-anchor="middle" fill="#4b5563">'+x+'%</text>';
 return '<svg viewBox="0 0 '+W+' 88" role="img" aria-label="Your estimate of '+v.toFixed(1)+'% on a scale from '+lo+'% to '+hi+'%" xmlns="http://www.w3.org/2000/svg" font-family="inherit">'+g+'</svg>';}
function msg(t){out.innerHTML='<p class="er-note">'+t+'</p>';out.classList.add('visible');}
function estimates(H,cm,age,wv){var metric=units==='metric',cv=metric?1/2.54:1,u=metric?' cm':' in',E={},M={},n,w,hp,rw,b=0,ids,s=0,bad=false,miss=false,i,v;
 var L=metric?{n:[20,76],w:[38,203],h:[51,203]}:{n:[8,30],w:[15,80],h:[20,80]};
 function inr(x,r){return x>=r[0]&&x<=r[1];}
 n=num('bfc-neck');w=num('bfc-waist');hp=num('bfc-hips');
 if(!(n&&w&&(sex==='m'||hp)))M.tape='Enter your neck and waist'+(sex==='f'?' and hips':'')+' for the tape method.';
 else if(!inr(n,L.n)||!inr(w,L.w)||(sex==='f'&&!inr(hp,L.h)))M.tape='Check the tape measurements: neck '+L.n[0]+' to '+L.n[1]+u+', waist '+L.w[0]+' to '+L.w[1]+u+(sex==='f'?', hips '+L.h[0]+' to '+L.h[1]+u:'')+'.';
 else if(sex==='m'&&w<=n)M.tape='For the tape method, your waist needs to be larger than your neck.';
 else E.tape=navy(sex,H,n*cv,w*cv,hp*cv);
 rw=num('bfc-rwaist');
 if(!rw)M.rfm='Enter your waist, measured at the top of your hip bones.';
 else if(!inr(rw,L.w))M.rfm='Enter a waist from '+L.w[0]+' to '+L.w[1]+u+'.';
 else E.rfm=rfm(sex,H,rw*cv);
 if(wv){b=metric?r1(wv/Math.pow(cm/100,2)):r1(703*wv/(H*H));E.bmi=deur(sex,b,age);}else M.bmi='Enter your weight to use the height-and-weight method.';
 ids=sites==='7'?SF.a7:SF[sex+'3'];
 for(i=0;i<ids.length;i++){v=num('bfc-sf-'+ids[i]);if(!v)miss=true;else if(v<1||v>100)bad=true;s+=v;}
 if(miss)M['sf'+sites]='Enter all '+sites+' skinfolds, in millimeters.';else if(bad)M['sf'+sites]='Check the skinfolds: each one 1 to 100 mm.';else E['sf'+sites]=jp(sex,sites,s,age);
 for(var k in E){if(!(E[k]>=2&&E[k]<=70)){M[k]='Those measurements give '+d1(E[k])+'%, outside what these formulas can estimate. Check the numbers and the units.';delete E[k];}}
 return {E:E,M:M,b:b};}
function show(){var metric=units==='metric',H,cm,age=parseFloat($('bfc-age').value),wv=num('bfc-w'),k=method==='sf'?'sf'+sites:method;
 if(metric){cm=parseFloat($('bfc-cm').value);H=cm/2.54;}else{H=parseFloat($('bfc-ft').value)*12+parseFloat($('bfc-in').value||'0');}
 if(!(age>=18&&age<=79)||Math.floor(age)!==age)return msg('Enter your age in whole years, from 18 to 79.');
 if(!(H>=48&&H<=90))return msg('Enter a height from 4 ft to 7 ft 6 in (122 to 229 cm).');
 if(wv&&!(metric?wv>=23&&wv<=318:wv>=50&&wv<=700))return msg('Enter a weight from 50 to 700 lb (23 to 318 kg), or leave it empty.');
 var R=estimates(H,cm,age,wv);if(!(k in R.E))return msg(R.M[k]);
 var v=r1(R.E[k]),g=grp(age),gg=ggrp(age),c=gg?D.gal[sex][gg]:null,cg=c?cat(v,c):null,q=g?D.q[sex][g]:null,w=word(sex,age),W=sex==='f'?'women':'men',h='',notes=[],f,cal,bin,rows=[],x;
 h+='<div class="bmi-result-card'+(cg?' '+CARD[cg]:'')+'"><div class="bmi-value">'+v.toFixed(1)+'%</div><div class="bmi-category">'+(cg?cg.charAt(0).toUpperCase()+cg.slice(1)+' on the provisional range for '+w+' aged '+nd(gg):'Estimated body fat')+'</div><div class="bmi-range">'+NAME[k]+(k==='bmi'?', from a BMI of '+R.b.toFixed(1):'')+'</div></div>';
 h+='<div class="er"><section class="er-section"><h2>How close this estimate is likely to be</h2>';
 if(k==='rfm'||k==='bmi'){f=k==='rfm'?'rfm':'deur';bin=Math.floor(v+0.5);cal=D.cal[f][sex][String(bin)];
  if(cal)h+='<p class="er-note">Among US '+W+' aged 20 to 59 whose '+(k==='rfm'?'waist-and-height':'height-and-weight')+' estimate was within a point of '+bin+'%, CDC’s DXA scans read '+cal[0].toFixed(1)+'% to '+cal[2].toFixed(1)+'% for the middle half, with a median of '+cal[1].toFixed(1)+'% ('+cal[3].toLocaleString('en-US')+' '+W+'; our calculation). Trained technicians measured them; measuring yourself adds some error.</p>';
  else h+='<p class="er-note">Fewer than 30 US '+W+' aged 20 to 59 had an estimate within a point of '+bin+'%, too few to check this one on CDC’s scans.</p>';
  h+='<p class="er-note">Across all US '+W+' aged 20 to 59, this formula came within 5 points of the scan for '+D.w5[f][sex]+'%.'+(k==='rfm'?' It tends to read high: on average by '+D.rb[sex]+' points.':'')+(age>59?' CDC scanned adults only up to age 59.':'')+(k==='rfm'&&age<20?' Its authors built it on adults aged 20 and over.':'')+'</p>';}
 else if(k==='tape')h+='<p class="er-note">CDC’s survey didn’t measure the neck, so this method can’t be checked on its scans. In '+D.pub.foulis.n.toLocaleString('en-US')+' US Army recruits at the start of basic training, it read '+D.pub.foulis.err+' points below a DXA scan on average, in women and in men (Foulis et al., 2023). Measuring yourself at home can add more error.</p>';
 else h+='<p class="er-note">CDC’s survey didn’t measure skinfolds, so this method can’t be checked on its scans. In '+D.pub.burns.n+' college students, seven-site skinfolds read '+D.pub.burns.diff+' points below DXA on average, and the average miss was '+D.pub.burns.mape+'% of the scan’s reading (Burns et al., 2019).'+(k==='sf3'?' That study used seven sites; you entered three.':'')+' Measuring yourself at home can add more error.</p>';
 h+='</section><section class="er-section"><h2>Where '+v.toFixed(1)+'% falls</h2>'+fig(v,q,c,sex);
 if(q)notes.push('On CDC’s scans, '+shareTxt(moreAt(D.more[sex][g],v))+' of US '+w+' aged '+nd(g)+' measured more body fat than '+v.toFixed(1)+'%. Bar: their middle half (darker) and 10th to 90th percentile; solid line: their median, '+q[2].toFixed(1)+'%.');
 else notes.push('CDC’s scans stopped at age 59, so there is no US comparison at your age.');
 if(c)notes.push('<span class="cat-dot '+CARD[cg]+'"></span>'+v.toFixed(1)+'% is '+cg+' on the provisional ranges for '+w+' aged '+nd(gg)+': healthy is '+rangeTxt(c,'healthy')+' (Gallagher et al., 2000).');
 else notes.push('The provisional ranges start at age 20.');
 if(q||c)notes.push((q&&c?'The share and the range treat':q?'The share treats':'The range treats')+' this estimate as if it were a scan reading, so '+(q&&c?'they are':'it is')+' only as close as the estimate.');
 h+=notes.map(function(n){return '<p class="er-note">'+n+'</p>';}).join('')+'</section>';
 if(wv){var fm=wv*v/100,ln=wv-fm,one=function(x){return metric?d1(x)+' kg ('+d1(x/0.45359237)+' lb)':d1(x)+' lb ('+d1(x*0.45359237)+' kg)';};
  h+='<section class="er-section"><h2>Fat and lean mass</h2><p class="er-note">At '+String(r1(wv))+(metric?' kg':' lb')+' and '+v.toFixed(1)+'% body fat: about '+one(fm)+' of fat; the other '+one(ln)+' is lean mass. Both are only as close as the estimate.</p></section>';}
 for(x in R.E){if(x===k)continue;if(x!=='bmi'&&!touched[x==='sf3'||x==='sf7'?'sf':x])continue;rows.push(x);}
 if(rows.length){h+='<section class="er-section"><h2>Your other estimates</h2><table class="er-table"><thead><tr><th scope="col">Method</th><th scope="col" class="er-num">Estimate</th></tr></thead><tbody>';
  [k].concat(rows).forEach(function(x){var f2=x==='rfm'?'rfm':x==='bmi'?'deur':null;h+='<tr'+(x===k?' class="er-active"':'')+'><td>'+SHORT[x]+(x===k?'<span class="er-you">Shown above</span>':'')+'<span class="er-alt">'+(f2?'Within 5 points of CDC’s scans for '+D.w5[f2][sex]+'% of US '+W+' aged 20 to 59':'Not checked on CDC’s scans')+'</span></td><td class="er-num">'+d1(R.E[x])+'%</td></tr>';});
  h+='</tbody></table></section>';}
 h+='<section class="er-section"><p class="er-note">Formulas: Hodgdon and Beckett (tape measure), Woolcott and Bergman (waist and height), Deurenberg et al. (height and weight), Jackson and Pollock with Siri (calipers). Checks: our calculation from CDC NHANES 2011–2018 DXA scans; published studies for the tape measure and calipers. Ranges: Gallagher et al., 2000 (provisional).</p></section></div>';
 out.innerHTML=h;out.classList.add('visible');}
function pick(sel,attr,fn){var bs=document.querySelectorAll(sel);for(var i=0;i<bs.length;i++)bs[i].addEventListener('click',function(){for(var j=0;j<bs.length;j++){var on=bs[j]===this;bs[j].classList.toggle('active',on);bs[j].setAttribute('aria-pressed',on?'true':'false');}fn(this.getAttribute(attr));});}
function sync(){var m=sex==='m',U=units==='us'?'in':'cm',ids=sites==='7'?SF.a7:SF[sex+'3'],all=SF.a7,i;
 $('bfc-hips-g').hidden=m;$('bfc-tape-hint').textContent=m?'Neck just below the Adam’s apple, waist at the navel.':'Neck just below the Adam’s apple, waist at its narrowest, hips where the buttocks stick out most.';
 ['neck','waist','hips','rwaist'].forEach(function(id){var l=$('bfc-'+id+'-l');l.textContent=l.textContent.replace(/\((in|cm)\)/,'('+U+')');});
 for(i=0;i<all.length;i++)$('bfc-sf-'+all[i]+'-g').hidden=ids.indexOf(all[i])<0;
 ['tape','rfm','bmi','sf'].forEach(function(p){$('bfc-p-'+p).hidden=p!==method;});
 $('bfc-w').placeholder=method==='bmi'?'':'Optional';}
pick('#bfc [data-sex]','data-sex',function(v){sex=v;sync();});
pick('#bfc [data-method]','data-method',function(v){method=v;sync();});
pick('#bfc [data-sites]','data-sites',function(v){sites=v;sync();});
var IDS=['bfc-ft','bfc-in','bfc-cm','bfc-w','bfc-neck','bfc-waist','bfc-hips','bfc-rwaist'],stash=null;
function snap(){var o={};IDS.forEach(function(id){o[id]=$(id).value;});return o;}
pick('#bfc [data-units]','data-units',function(v){if(v===units)return;var now=snap(),w=parseFloat($('bfc-w').value),f=v==='metric'?2.54:1/2.54;
 if(stash&&stash.unit===units&&IDS.every(function(id){return now[id]===stash.shown[id];})){IDS.forEach(function(id){$(id).value=stash.orig[id];});stash=null;}
 else{if(v==='metric'){var hi=parseFloat($('bfc-ft').value)*12+parseFloat($('bfc-in').value||'0');if(hi>0)$('bfc-cm').value=String(r1(hi*2.54));if(w>0)$('bfc-w').value=String(r1(w*0.45359237));}
  else{var cc=parseFloat($('bfc-cm').value);if(cc>0){var t=r1(cc/2.54),ft=Math.floor(t/12+1e-9);$('bfc-ft').value=ft;$('bfc-in').value=String(r1(t-ft*12));}if(w>0)$('bfc-w').value=String(r1(w/0.45359237));}
  ['bfc-neck','bfc-waist','bfc-hips','bfc-rwaist'].forEach(function(id){var x=parseFloat($(id).value);if(x>0)$(id).value=String(r1(x*f));});
  stash={unit:v,orig:now,shown:snap()};}
 units=v;$('bfc-us').hidden=v!=='us';$('bfc-metric').hidden=v!=='metric';$('bfc-w-l').textContent=v==='us'?'Weight (lb)':'Weight (kg)';sync();});
[['tape',['bfc-neck','bfc-waist','bfc-hips']],['rfm',['bfc-rwaist']],['sf',SF.a7.map(function(s){return 'bfc-sf-'+s;})]].forEach(function(p){p[1].forEach(function(id){$(id).addEventListener('input',function(){touched[p[0]]=true;});});});
$('bfc-go').addEventListener('click',show);
Array.prototype.forEach.call(document.querySelectorAll('#bfc input'),function(e){e.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();show();}});});
sync();})();'''
calc += f'<script>window.BFC={json.dumps(TOOL, separators=(",", ":"), ensure_ascii=False)};</script><script>{TOOL_JS}</script>'

# ---------------------------------------------------------------- the page's own text
H1 = 'Body Fat Calculator'
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">Estimate your body fat percentage four ways and see how close each method comes to a DXA '
    'scan.</p>'
    f'<p class="intro-note">Accuracy: our check on CDC’s scans of {META["n_scanned_20_59"]:,} US adults (2011–2018) and '
    'published studies. <a href="#sources">Method and sources</a></p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>A body fat calculator estimates your body fat from a few measurements, and the estimate can '
    'miss.</strong> On CDC’s DXA scans of US adults, the waist-and-height formula came within 5 points of the scan for '
    f'{W5["rfm"]["men"]}% of men and {W5["rfm"]["women"]}% of women, and the height-and-weight formula for '
    f'{W5["deur"]["men"]}% and {W5["deur"]["women"]}% (our calculation).</p><ul>'
    f'<li><strong>The methods disagree for the same person:</strong> the woman in the worked example below gets '
    f'{f1(EX_TAPE)}% by tape measure, {f1(EX_DEUR)}% by height and weight and {f1(EX_RFM)}% by waist and height.</li>'
    f'<li>The waist-and-height formula reads high on average, by {sg(BIAS["rfm"]["women"]["mean"])[1:]} points for women and '
    f'{sg(BIAS["rfm"]["men"]["mean"])[1:]} for men. The height-and-weight formula reads low at a healthy BMI and high with '
    'obesity.</li>'
    f'<li>CDC’s survey measured neither the neck nor skinfolds. In published studies, the tape method read {FOULIS["err"]} '
    f'points below DXA on average in Army recruits, and seven-site skinfolds {BURNS["diff"]} points below in college '
    'students.</li>'
    f'<li><strong>Healthy body fat ranges are provisional:</strong> {rng(GAL["f"]["20-39"], "healthy")} for women and '
    f'{rng(GAL["m"]["20-39"], "healthy")} for men aged 20 to 39 (Gallagher et al., 2000).</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This calculator gives estimates for information '
    'only. A body fat estimate is not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

CHIPS = (('read-result', 'Your result'), ('accuracy', 'Accuracy'), ('tape', 'Tape measure'), ('rfm', 'Waist and height'),
         ('bmi-method', 'Height and weight'), ('calipers', 'Calipers'), ('ranges', 'Ranges'), ('faq', 'FAQ'),
         ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

sec_read = (
    '<section id="read-result" class="content-section flow"><h2>How to read your result</h2>'
    f'<p>Every number here uses the calculator’s starting values: a woman of {EX_AGE}, 5′4″ ({EX_CM} cm) and {EX_LB} lb '
    f'({EX_KG} kg), with a neck of {EX_NECK}, a waist of {EX_WAIST} and hips of {EX_HIPS} inches for the tape measure. For '
    f'waist and height, whose field starts empty, the example adds a {EX_RWAIST}-inch waist at the hip bones.</p>'
    f'<figure class="figure">{svg_ex}<figcaption>Three estimates for the same woman. For the two formulas checked on CDC’s '
    'scans, the box shows the middle half of the scans of US women whose formula gave about the same estimate, and the tick '
    'their median.</figcaption></figure>'
    '<dl>'
    f'<dt>Body fat: {f1(EX_TAPE)}%, by tape measure</dt><dd>163.205 × log10({EX_WAIST} + {EX_HIPS} − {EX_NECK}) − 97.684 × '
    f'log10({EX_H}) − 78.387 = {f1(EX_TAPE)}, the women’s tape equation, in inches.</dd>'
    f'<dt>High on the provisional range</dt><dd>For women aged 20 to 39, the provisional ranges call '
    f'{rng(GAL["f"]["20-39"], "healthy")} healthy and {rng(GAL["f"]["20-39"], "high")} high (Gallagher et al., 2000), so '
    f'{f1(EX_TAPE)}% is high: the high range starts at {GAL["f"]["20-39"][1]}%. The result card is tinted to match.</dd>'
    f'<dt>How close: checked in Army recruits, not on CDC’s scans</dt><dd>CDC’s survey didn’t measure the neck. In '
    f'{FOULIS["n"]:,} Army recruits, the tape method read {FOULIS["err"]} points below DXA on average (Foulis et al., '
    '2023).</dd>'
    f'<dt>Where {f1(EX_TAPE)}% falls: {share_txt(EX_MORE)} of US women aged 30 to 39 measured more</dt><dd>On CDC’s scans, '
    f'{share_txt(EX_MORE)} of US women aged 30 to 39 had more body fat than {f1(EX_TAPE)}%; their median was '
    f'{TQ["f"][EX_G][2]:.1f}%.</dd>'
    f'<dt>Fat and lean mass: {f1(EX_FAT)} lb and {f1(EX_LEAN)} lb</dt><dd>{EX_LB} lb × {f1(EX_TAPE)}% = {f1(EX_FAT)} lb of fat '
    f'({kg(EX_FAT)} kg); the other {f1(EX_LEAN)} lb ({kg(EX_LEAN)} kg) is lean mass.</dd>'
    f'<dt>Other estimates: {f1(EX_DEUR)}% from height and weight</dt><dd>Her BMI is {EX_BMI} ({EX_LB} × 703 ÷ {EX_H}²), and '
    f'1.20 × {EX_BMI} + 0.23 × {EX_AGE} − 5.4 = {f1(EX_DEUR)}. Among US women whose height-and-weight estimate was within a '
    f'point of {EX_BD}%, CDC’s scans read {EX_CD[0]:.1f}% to {EX_CD[2]:.1f}% for the middle half, median {EX_CD[1]:.1f}% '
    f'({EX_CD[3]} women).</dd>'
    f'<dt>Waist and height: {f1(EX_RFM)}% with a {EX_RWAIST}-inch waist</dt><dd>Measured at the top of the hip bones, a waist of '
    f'{EX_RWAIST} inches gives 76 − 20 × {EX_H} ÷ {EX_RWAIST} = {f1(EX_RFM)}. Among US women whose estimate was within a '
    f'point of {EX_BR}%, the scans read {EX_CR[0]:.1f}% to {EX_CR[2]:.1f}%, median {EX_CR[1]:.1f}% ({EX_CR[3]} women). The two '
    f'formulas disagree by {f1(EX_RFM - EX_DEUR)} points, yet women with either estimate had scans with a median near '
    '36% to 37%.</dd>'
    '</dl></section>')
assert abs(EX_CD[1] - EX_CR[1]) < 1 and 36 <= min(EX_CD[1], EX_CR[1]) and max(EX_CD[1], EX_CR[1]) < 37

ACC_ROWS = (('Within 3 points', lambda f, s: f'{f1(W3[f][s])}%'),
            ('Within 5 points', lambda f, s: f'{f1(F[f][s]["within5"]["pct"])}%'),
            ('Typical miss<span class="th-sub">points</span>', lambda f, s: f1(MAE[f][s])),
            ('Average error<span class="th-sub">points</span>', lambda f, s: sg(BIAS[f][s]['mean'])))
def ftable(f, name):
    """One formula: how close it came overall, then its average error by BMI and age group; women and men side by side."""
    rows = ''.join(f'<tr><th scope="row">{lab_}</th>' + ''.join(f'<td class="num">{fn(f, s)}</td>' for s in SX) + '</tr>'
                   for lab_, fn in ACC_ROWS)
    rows += '<tr><th scope="colgroup" colspan="3">Average error by group (points)</th></tr>'
    rows += ''.join(f'<tr><th scope="row">{lab_}</th>' + ''.join(f'<td class="num">{sg(grp_bias(f, s, k)["mean"])}</td>'
                                                              for s in SX) + '</tr>' for k, lab_ in GROUPS)
    return ('<div class="table-responsive"><table class="data-table data-table--fit"><caption>' + name + ' compared with '
            'CDC’s scans, US adults aged 20 to 59</caption><thead><tr><th scope="col">Measure</th><th scope="col" '
            f'class="num">Women</th><th scope="col" class="num">Men</th></tr></thead><tbody>{rows}</tbody></table></div>')
METHODS = (
    f'<ul><li><strong>Tape measure</strong> (neck, waist, hips for women, height): in {FOULIS["n"]:,} US Army recruits, '
    f'{FOULIS["err"]} points below DXA on average.</li>'
    f'<li><strong>Waist and height</strong>: on CDC’s scans of {N_RFM:,} US adults, within 5 points for {W5["rfm"]["women"]}% '
    f'of women and {W5["rfm"]["men"]}% of men.</li>'
    f'<li><strong>Height and weight</strong>: on CDC’s scans of {N_DEU:,} US adults, within 5 points for '
    f'{W5["deur"]["women"]}% of women and {W5["deur"]["men"]}% of men.</li>'
    f'<li><strong>Calipers</strong> (3 or 7 skinfolds): in {BURNS["n"]} college students, seven sites read {BURNS["diff"]} '
    f'points below DXA on average; the average miss was {BURNS["mape"]}% of the scan’s reading.</li></ul>')
sec_acc = (
    '<section id="accuracy" class="content-section flow"><h2>How accurate is each method?</h2>'
    '<p>Each method predicts body fat from something easier to measure, and the prediction can miss. To see by how much, we applied two of the formulas to CDC’s DXA scans of US adults aged 20 to 59, taken from 2011 '
    f'to 2018 in its National Health and Nutrition Examination Survey (NHANES). CDC’s {ext(U["dxx"], "documentation")} calls '
    'DXA “the most widely accepted method of measuring body composition”. The survey measured height, weight and waist, but not the '
    'neck or skinfolds, so the tape and caliper methods rest on published studies.</p>'
    + METHODS +
    f'<p><strong>The waist-and-height formula came closer.</strong> In the same people, it came within 5 points of the scan '
    f'for {PW5N["women"]} more women in every 100 than the height-and-weight formula, and for {PW5N["men"]} more men. Its '
    f'typical miss was {f1(MAE["rfm"]["women"])} points for women and {f1(MAE["rfm"]["men"])} for men, against '
    f'{f1(MAE["deur"]["women"])} and {f1(MAE["deur"]["men"])} (our calculation; all four differences are outside their margins of '
    'error).</p>'
    f'<figure class="figure">{svg_acc}<figcaption>Formula minus scan for US adults aged 20 to 59: the middle half (box), the '
    '10th to 90th percentile (line) and the median (tick). Right of the dashed line, the formula read higher than the scan. '
    'CDC NHANES 2011–2018, our calculation.</figcaption></figure>'
    + ftable('rfm', 'Waist and height') + ftable('deur', 'Height and weight') +
    f'<p class="source-note">Our calculation from CDC NHANES 2011–2018: {NCK["rfm"]["women"]:,} women and '
    f'{NCK["rfm"]["men"]:,} men aged 20 to 59 with a measured waist, {NCK["deur"]["women"]:,} and {NCK["deur"]["men"]:,} with '
    'a BMI. Typical miss: the average distance from the scan, either way. Average error: formula minus scan. BMI groups '
    'follow CDC’s adult categories, from 18.5 up. In the group rows, every average error is outside its margin of error '
    'except waist and height for men with a healthy BMI (+0.1); overall, the height-and-weight formula’s average errors '
    f'({sg(BIAS["deur"]["women"]["mean"])} and {sg(BIAS["deur"]["men"]["mean"])}) are within theirs.</p>'
    f'<p><strong>The waist-and-height formula reads high.</strong> Its median error, the measure its authors report, was '
    f'{sg(MED_ERR["rfm"]["women"])} points for women and {sg(MED_ERR["rfm"]["men"])} for men. On the 2005–2006 scans they '
    f'tested it on (adults aged 20 to 69), the median errors were {WB18["bias_w"]} and {WB18["bias_m"]} points '
    f'({ext(U["rfm"], "Woolcott and Bergman, 2018")}). For women it read clearly higher on the newer scans (the two 95% '
    'confidence intervals don’t overlap); for men the two don’t clearly differ. The samples also differ in scanner model '
    '(Hologic Discovery A, against the QDR 4500A) and age range, so the reason isn’t known.</p>'
    '<p><strong>The height-and-weight formula misses by group.</strong> Averaged over everyone it comes out about right (an '
    f'average error of {sg(BIAS["deur"]["women"]["mean"])} points for women and {sg(BIAS["deur"]["men"]["mean"])} for men, within '
    f'its margin of error), but only because its misses cancel out. At a healthy BMI it read {sg(DB[("women", "healthy")])[1:]} '
    f'points low for women and {sg(DB[("men", "healthy")])[1:]} for men; with obesity, {sg(DB[("women", "obese")])[1:]} and '
    f'{sg(DB[("men", "obese")])[1:]} points high. It also read about 2 points low under age 40 and about 2 points high from 40 '
    'to 59.</p>'
    f'<p><strong>The tape measure and calipers.</strong> In {FOULIS["n"]:,} US Army recruits, the tape method read '
    f'{FOULIS["err"]} points below DXA on average, in women and in men, at the start of basic training '
    f'({ext(U["foulis"], "Foulis et al., 2023")}). In {BURNS["n"]} college students, seven-site skinfolds read '
    f'{BURNS["diff"]} points below DXA on average, and their average miss, {BURNS["mape"]}% of the scan’s reading, was the '
    f'lowest of the seven methods tested ({ext(U["burns"], "Burns et al., 2019")}). Both studies were of young adults; '
    'neither covered older ages.</p>'
    '</section>')
assert f'{sg(grp_bias("rfm", "men", "healthy")["mean"])}' == '+0.1'
# "clearly higher" for women, "don't clearly differ" for men: our Woodruff 95% CI of the median error against Table 2's
assert MED_CI['women'][0] > WB18['ci_w'][1] and not (MED_CI['men'][0] > WB18['ci_m'][1] or MED_CI['men'][1] < WB18['ci_m'][0])
assert 1.5 <= -DB[('women', '20-39')] <= 2.5 and 1.5 <= -DB[('men', '20-39')] <= 2.5
assert 1.5 <= DB[('women', '40-59')] <= 2.5 and 1.5 <= DB[('men', '40-59')] <= 2.5            # "about 2 points"

sec_tape = (
    '<section id="tape" class="content-section flow"><h2>Tape measure (the Navy method)</h2>'
    '<p>Hodgdon and Beckett, at the US Naval Health Research Center, worked out these equations in 1984 from the neck, the '
    'waist and the height, plus the hips for women. The same equations appear in the US Army’s sample body fat '
    f'calculations ({ext(U["army"], "Army Table B-5")}). They take inches; the calculator converts centimeters first.</p>'
    '<ul><li>Men: 86.010 × log10(waist − neck) − 70.041 × log10(height) + 36.76</li>'
    '<li>Women: 163.205 × log10(waist + hips − neck) − 97.684 × log10(height) − 78.387</li></ul>'
    f'<p><strong>Where to measure</strong>, as on the Army’s 2013 worksheets ({ext(U["da5500"], "DA Form 5500")} and '
    f'{ext(U["da5501"], "5501")}):</p><ul>'
    '<li>Neck: just below the Adam’s apple.</li>'
    '<li>Waist, men: at the navel.</li>'
    '<li>Waist, women: at the narrowest point.</li>'
    '<li>Hips, women: where the buttocks stick out most.</li></ul>'
    '<p>The worksheets take each measurement three times and average them.</p>'
    f'<p><strong>The Army’s worked examples:</strong> a woman with a 15-inch neck, 42-inch waist, 44-inch hips and a height of '
    f'64 inches, and a man with a 16-inch neck, 49-inch waist and a height of 69 inches. Worked by hand with rounded '
    f'logarithms, the document gets 46.73% and 38.62% and reports 47% and 39%. Computed exactly, they are {f1(ARMY_F)}% and '
    f'{f1(ARMY_M)}%, which round to the same.</p>'
    f'<p>Against DXA, the tape method read {FOULIS["err"]} points low on average in Army recruits, with a standard deviation '
    f'of {FOULIS["sd_w"]} points for women and {FOULIS["sd_m"]} for men (Foulis et al., 2023). In June 2023 the Army moved to '
    f'a one-site tape test ({ext(U["army23"], "Army Directive 2023-11")}). For a military body composition check, follow '
    'your service’s own procedure; this calculator is for information.</p>'
    '</section>')

sec_rfm = (
    '<section id="rfm" class="content-section flow"><h2>Waist and height (relative fat mass)</h2>'
    f'<p>Woolcott and Bergman built relative fat mass (RFM) on CDC’s DXA scans of {WB18["dev"]} adults from 1999–2004 and '
    f'tested it on {WB18["val"]} from 2005–2006 ({ext(U["rfm"], "Sci Rep, 2018")}). It needs one tape '
    'measurement and your height, in the same unit:</p>'
    '<ul><li>Men: 64 − 20 × height ÷ waist</li><li>Women: 76 − 20 × height ÷ waist</li></ul>'
    f'<p>Measure the waist at the top of your hip bones ({ext(U["cedars"], "Cedars-Sinai")}). CDC’s survey measures it there, '
    f'at the top of the right hip bone ({ext(U["rfm"], "Woolcott and Bergman, 2018")}). The tape method uses another spot '
    '(the navel for men, the narrowest point for women), so the two waists can differ.</p>'
    f'<p>On CDC’s newer scans, from 2011–2018, it came within 5 points for {W5["rfm"]["women"]}% of women and '
    f'{W5["rfm"]["men"]}% of men, with a typical miss of {f1(MAE["rfm"]["women"])} and {f1(MAE["rfm"]["men"])} points, and '
    f'read {sg(BIAS["rfm"]["women"]["mean"])[1:]} and {sg(BIAS["rfm"]["men"]["mean"])[1:]} points high on average (our '
    'calculation).</p></section>')

sec_bmi = (
    '<section id="bmi-method" class="content-section flow"><h2>Height and weight (the Deurenberg formula)</h2>'
    f'<p>Deurenberg and colleagues measured body fat from body density in {DEUR91["n"]} people aged 7 to 83 and fitted a '
    'formula for adults from BMI, age and sex. Its standard error of estimate is 4.1 points, and its authors found it slightly '
    f'overestimates body fat in people with obesity ({ext(U["deur"], "Br J Nutr, 1991")}):</p>'
    '<p>Body fat % = 1.20 × BMI + 0.23 × age − 10.8 × sex − 5.4, with sex 1 for men and 0 for women.</p>'
    '<p>It needs no tape, but it starts from BMI, so it can’t tell muscle from fat. Children 15 and under have a formula of '
    'their own in the same paper.</p>'
    f'<p>Checked on CDC’s 2011–2018 scans, it came within 5 points for {W5["deur"]["women"]}% of women and '
    f'{W5["deur"]["men"]}% of men, with a typical miss of {f1(MAE["deur"]["women"])} and {f1(MAE["deur"]["men"])} points. '
    f'It read {sg(DB[("women", "healthy")])[1:]} points low for women with a healthy BMI and '
    f'{sg(DB[("women", "obese")])[1:]} high for women with obesity (our calculation; <a href="#accuracy">all groups</a>).</p>'
    '</section>')

sec_sf = (
    '<section id="calipers" class="content-section flow"><h2>Skinfold calipers (Jackson–Pollock)</h2>'
    '<p>Calipers measure a pinch of skin and the fat under it. Jackson and Pollock’s equations turn the sum of the pinches, '
    'in millimeters, and your age into body density, and Siri’s equation turns density into body fat.</p>'
    '<ul><li>3 sites, men: chest, abdomen and thigh.</li><li>3 sites, women: triceps, suprailiac (just above the hip bone) '
    'and thigh.</li><li>7 sites, both: chest, midaxillary (side of the chest), triceps, subscapular (below the shoulder '
    'blade), abdomen, suprailiac and thigh.</li></ul>'
    '<ul><li>3 sites, men: density = 1.10938 − 0.0008267 × S + 0.0000016 × S² − 0.0002574 × age</li>'
    '<li>3 sites, women: density = 1.0994921 − 0.0009929 × S + 0.0000023 × S² − 0.0001392 × age</li>'
    '<li>7 sites, men: density = 1.112 − 0.00043499 × S + 0.00000055 × S² − 0.00028826 × age</li>'
    '<li>7 sites, women: density = 1.097 − 0.00046971 × S + 0.00000056 × S² − 0.00012828 × age</li>'
    '<li>Body fat (Siri): 495 ÷ density − 450</li></ul>'
    '<p class="source-note">S is the sum of the skinfolds in millimeters. Coefficients as printed by '
    f'{ext(U["topend"], "Topend Sports")}, citing Jackson and Pollock (1978) and Jackson, Pollock and Ward (1980). '
    f'{ext(U["jp"], "Serra et al., ConScientiae Saúde 2009")} print the same equations, but the women’s 3-site age term as '
    '0.0001395 instead of 0.0001392, which changes the result by less than 0.02 points at any age from 18 to 79.</p>'
    f'<p>In {BURNS["n"]} college students, seven-site skinfolds read {BURNS["diff"]} points below DXA on average; the '
    f'average miss was {BURNS["mape"]}% of the scan’s reading ({ext(U["burns"], "Burns et al., 2019")}).</p>'
    '</section>')
# "less than 0.02 points at any age from 18 to 79": the 0.0000003 x age difference in density, over every 3-site sum the
# calculator takes (3 to 300 mm) whose estimate it shows (2% to 70%), at every age it takes
_d = max(abs(jp('f', 3, s_, a_) - (495 / (1.0994921 - 0.0009929 * s_ + 0.0000023 * s_ * s_ - 0.0001395 * a_) - 450))
         for s_ in range(3, 301) for a_ in range(18, 80) if 2 <= jp('f', 3, s_, a_) <= 70)
assert _d < 0.02, _d

def gal_table(k):
    rows = ''.join(f'<tr><th scope="row">{lab_}</th>' + ''.join(f'<td>{rng(GAL[k][g], x)}</td>'
                                                          for g in ('20-39', '40-59', '60-79')) + '</tr>'
                   for x, lab_ in (('low', 'Low'), ('healthy', 'Healthy'), ('high', 'High'), ('very high', 'Very high')))
    return ('<div class="table-responsive"><table class="data-table data-table--fit"><caption>Provisional body fat ranges for '
            f'{"women" if k == "f" else "men"}, by age</caption><thead><tr><th scope="col">Range</th>'
            + ''.join(f'<th scope="col">{g.replace("-", "–")}</th>' for g in ('20-39', '40-59', '60-79'))
            + f'</tr></thead><tbody>{rows}</tbody></table></div>')
sec_ranges = (
    '<section id="ranges" class="content-section flow"><h2>What your result means</h2>'
    '<p>Gallagher and colleagues worked out the body fat that goes with a BMI of 18.5, 25 and 30, by sex and age, and called '
    f'the ranges provisional ({ext(U["gallagher"], "Gallagher et al., 2000")}). The calculator tints its result by '
    'them:</p>'
    + gal_table('f') + gal_table('m') +
    f'<p class="source-note">Ranges as tabulated in {ext(U["jpha"], "J Public Health Afr 2016, Table 1")}; the original study '
    'gives values for each of its three ethnic groups.</p>'
    f'<p>For comparison, US women aged 20 to 59 measured {MEAN_F}% body fat on average on CDC’s scans and men {MEAN_M}%. The '
    '<a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows the share above and below every whole '
    'percentage, by age.</p>'
    '</section>')

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# Questions: the ledger's calculator-owned queries (research/keyword-ledger.csv) as questions: "most accurate body fat
# calculator" 390 (+ accurate 170, best 90), "body fat calculator height weight" 170 (+ using height and weight 140),
# "relative fat mass calculator" 70, waist placement for the two waist methods, "7 site skinfold calculator" 320 and
# "3 site skinfold calculator" 260, "fat mass calculator" 170 and "body fat weight calculator" 210, "body fat calculator
# female" 1,000, "body fat calculator for teenager" 90, and the metric questions ("body fat calculator cm"). The healthy
# and ideal range questions belong to /body-fat-percentage-chart/, the home-measuring and scale questions to
# /blog/how-to-measure-body-fat/ (ledger owners).
FAQ = [
    ('Which body fat calculator is most accurate?',
     'Of the two formulas we could check on CDC’s DXA scans of US adults aged 20 to 59, the waist-and-height formula '
     f'(relative fat mass) came closer: within 5 points of the scan for {W5["rfm"]["men"]}% of men and {W5["rfm"]["women"]}% '
     f'of women, against {W5["deur"]["men"]}% and {W5["deur"]["women"]}% for the height-and-weight formula (our calculation). '
     'CDC’s data can’t check the tape and caliper methods: in published studies, the tape method read '
     f'{FOULIS["err"]} points below DXA in Army recruits ({ext(U["foulis"], "Foulis et al., 2023")}), and seven-site '
     f'skinfolds read {BURNS["diff"]} points below DXA on average in college students '
     f'({ext(U["burns"], "Burns et al., 2019")}).'),
    ('Can you calculate body fat from height and weight?',
     'Yes, roughly, with the Deurenberg formula: 1.20 × BMI + 0.23 × age − 10.8 × sex − 5.4, where sex is 1 for men and 0 '
     f'for women ({ext(U["deur"], "Deurenberg et al., 1991")}). On CDC’s scans of US adults aged 20 to 59, it came within 5 '
     f'points of the scan for {W5["deur"]["women"]}% of women and {W5["deur"]["men"]}% of men. It read '
     f'{sg(DB[("women", "healthy")])[1:]} points low for women and {sg(DB[("men", "healthy")])[1:]} for men with a healthy '
     f'BMI, and {sg(DB[("women", "obese")])[1:]} and {sg(DB[("men", "obese")])[1:]} points high with obesity (our '
     'calculation).'),
    ('What is relative fat mass (RFM)?',
     f'A body fat formula from Woolcott and Bergman ({ext(U["rfm"], "2018")}) that needs only your height and waist: 64 − 20 × '
     'height ÷ waist for men and 76 − 20 × height ÷ waist for women, with the waist measured at the top of the hip bones. '
     'They built it on CDC’s 1999–2004 DXA scans. On the newer 2011–2018 scans it came within 5 points of the scan for '
     f'{W5["rfm"]["men"]}% of men and {W5["rfm"]["women"]}% of women, reading {sg(BIAS["rfm"]["men"]["mean"])[1:]} and '
     f'{sg(BIAS["rfm"]["women"]["mean"])[1:]} points high on average (our calculation).'),
    ('Where do I measure my waist for body fat?',
     'It depends on the method. For the tape method, men measure at the navel and women at the narrowest point of the waist, '
     f'as on the US Army’s 2013 worksheets ({ext(U["da5500"], "DA Forms 5500")} and {ext(U["da5501"], "5501")}). For relative fat '
     'mass, measure at the top of the '
     'hip bones, the level CDC’s survey uses. The calculator gives the spot for each method under its fields.'),
    ('What is the difference between the 3-site and 7-site skinfold tests?',
     'The number of skinfolds. The 3-site test uses the chest, abdomen and thigh for men, and the triceps, suprailiac and '
     'thigh for women. The 7-site test uses the chest, midaxillary, triceps, subscapular, abdomen, suprailiac and thigh for '
     'both. Jackson and Pollock published an equation for each, and Siri’s equation turns the result into body fat. In a '
     f'study of {BURNS["n"]} college students, the 7-site test read {BURNS["diff"]} points below DXA on average '
     f'({ext(U["burns"], "Burns et al., 2019")}).'),
    ('How many pounds of fat do I have?',
     f'Multiply your weight by your body fat percentage. At {EX_LB} lb and {f1(EX_TAPE)}% body fat, that is {f1(EX_FAT)} lb of '
     f'fat ({kg(EX_FAT)} kg), and the other {f1(EX_LEAN)} lb ({kg(EX_LEAN)} kg) is lean mass. The calculator does this when '
     'you enter your weight; the answer is only as close as the body fat estimate. The '
     '<a href="/lean-body-mass/">lean body mass calculator</a> estimates lean mass from height and weight instead.'),
    ('Is the body fat calculator different for women?',
     'Each method has its own version for women. The tape method adds the hips, relative fat mass adds 12 points, the '
     'height-and-weight formula gives women 10.8 points more than men of the same BMI and age, and the 3-site caliper test '
     'uses the triceps, suprailiac and thigh. Women carry more fat: on CDC’s scans, US women aged 20 to 59 measured '
     f'{MEAN_F}% body fat on average and men {MEAN_M}%.'),
    ('Can teenagers use a body fat calculator?',
     'The formulas here were built for adults, so the calculator takes ages 18 and over. Deurenberg’s team fitted a separate '
     'formula for ages 15 and under, and relative fat mass was built on adults aged 20 and over. For teens, the '
     '<a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows what CDC’s scans measured in US girls and '
     'boys from age 8.'),
    ('Does the tape method work in centimeters?',
     'Its equations take inches. Entering centimeters straight into them gives a far higher number: in the US Army’s two '
     f'worked examples, {f1(CM_M)} points higher for the man and {f1(CM_F)} for the woman (our calculation). The calculator '
     'converts centimeters to inches first, so either unit works.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p>'
                   '</div></div>' for q, a in FAQ)
sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC NHANES 2011–2018 {ext(U["dxx"], "whole-body DXA scans")} with the demographics and body measures files (DXX, DEMO, '
    f'BMX, cycles G to J): our calculation for {META["n_scanned_20_59"]:,} adults aged 20 to 59, {N_RFM:,} with a measured '
    f'waist and {N_DEU:,} with a BMI. The documentation calls DXA “the most widely accepted method of measuring body '
    'composition”.',
    f'Woolcott OO, Bergman RN. {ext(U["rfm"], "Relative fat mass (RFM) as a new estimator of whole-body fat percentage")}. '
    'Sci Rep 2018;8:10980.',
    f'Cedars-Sinai. {ext(U["cedars"], "Building a Better Body Measurement: Relative Fat Mass")} (where to measure the waist).',
    'Hodgdon JA, Beckett MB. Prediction of percent body fat for U.S. Navy men and women from body circumferences and height. '
    'Naval Health Research Center reports 84-11 and 84-29, 1984, as reproduced in the US Army’s sample calculations '
    f'(Table B-5) in study protocol {ext(U["army"], "NCT02734238")}.',
    f'US Army. Body fat content worksheets {ext(U["da5500"], "DA Form 5500 (male)")} and '
    f'{ext(U["da5501"], "DA Form 5501 (female)")}, May 2013: where to measure.',
    f'Foulis SA, et al. {ext(U["foulis"], "Body composition changes during 8 weeks of military training are not accurately captured by circumference-based assessments")}. '
    'Front Physiol 2023;14:1183836.',
    f'Deurenberg P, Weststrate JA, Seidell JC. {ext(U["deur"], "Body mass index as a measure of body fatness: age- and sex-specific prediction formulas")}. '
    'Br J Nutr 1991;65:105–14.',
    'Jackson AS, Pollock ML. Br J Nutr 1978;40:497–504; Jackson AS, Pollock ML, Ward A. Med Sci Sports Exerc 1980;12:175–81; '
    f'Siri WE, 1956; as printed by {ext(U["topend"], "Topend Sports (Jackson-Pollock body density)")} and in '
    f'{ext(U["jp"], "Serra AJ, et al. ConScientiae Saúde 2009;8(1):19–24")}.',
    f'US Army. {ext(U["army23"], "Army Directive 2023-11")}, June 2023: the one-site tape test.',
    f'Burns RD, Fu Y, Constantino N. {ext(U["burns"], "Measurement agreement in percent body fat estimates among laboratory and field assessments in college students: Use of equivalence testing")}. '
    'PLOS ONE 2019;14(3):e0214029.',
    f'Gallagher D, et al. {ext(U["gallagher"], "Healthy percentage body fat ranges")}. Am J Clin Nutr 2000;72:694–701, as '
    f'tabulated in {ext(U["jpha"], "J Public Health Afr 2016, Table 1")}.',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Adults aged 20 to 59 with a valid whole-body DXA scan in NHANES 2011–2012 '
    'to 2017–2018, pregnant women excluded, weighted with CDC’s exam weights divided by four. For each person we worked out '
    'the height-and-weight formula from their measured BMI and age, and relative fat mass from their measured height and '
    'waist, then subtracted their scan. Shares, typical misses and average errors are survey-weighted, with 95% confidence '
    'intervals from Taylor linearization over the survey’s 59 strata and 121 primary sampling units; the page states a '
    'difference only when its interval excludes zero. The two formulas are compared in the same people. For the estimate '
    'checks, we took the people whose formula gave an estimate within a point of each whole percent (at least 30 of them) '
    'and read the middle half and median of their scans (weighted percentiles by the midpoint rule, as on the body fat '
    'percentage chart). Every figure is rounded once, from the unrounded estimate. The US '
    'comparison and the provisional ranges are the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>’s.'
    '</p></section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/lean-body-mass/', 'Lean body mass calculator'),
        ('/women-bmi-calculator/', 'BMI calculator for women'), ('/men-bmi-calculator/', 'BMI calculator for men'),
        ('/ideal-weight/', 'Ideal weight calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/body-fat-percentage-chart/', 'Body fat percentage chart'), ('/blog/how-to-measure-body-fat/', 'How to measure body fat'),
        ('/blog/body-fat-vs-bmi/', 'Body fat vs BMI'), ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'),
        ('/average-weight/', 'Average weight by height')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, calc, takeaways, toc, sec_read, sec_acc, sec_tape, sec_rfm, sec_bmi, sec_sf, sec_ranges, sec_faq, sec_src, sec_rel])
    + ' </div></main>')
assert 'style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', main)
assert all(f'id="{a}"' in main for a, _ in CHIPS) and '<article' not in main and 'bodyfatpercentagecalc' not in main

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD, nav
TITLE = 'Body Fat Calculator: 4 Methods Compared With DXA Scans'
DESC = ('Free body fat calculator: tape measure (Navy), waist and height, BMI or calipers. Get your body fat percentage and '
        'how close each method gets to a DXA scan.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'Body fat calculator: four methods and how close each gets to a DXA scan'
OG_D = ('Estimate your body fat percentage by tape measure, waist and height, BMI or calipers, and see how close each '
        'method comes to a DXA scan: CDC’s scans for two formulas, published studies for the tape and calipers.')
OG_ALT = ('Chart: how far two body fat formulas were from DXA scans of US women and men, shown as box plots around a '
          'dashed zero line.')
for s_ in (DESC, OG_T, OG_D, OG_ALT): assert '"' not in s_
PREF = SITE + '/assets/images/preferred/body-fat-calculator-'
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
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
assert 'twitter:title' not in src and 'twitter:description' not in src          # the B2 head had neither; add them
src = sub1(r'(<meta name="twitter:card" content="summary_large_image">)',
           f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{OG_T}">'
           f'<meta name="twitter:description" content="{OG_D}">', src)
n_style = len(re.findall(r'(?s)<style>.*?</style>', src)); assert n_style == 3, n_style   # the B2 page-level styles
src = re.sub(r'(?s)<style>.*?</style>', '', src)
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1 and '<style' not in src
# The menu marked "Obesity Statistics" as the current page (the B2 page took its shell from /us-obesity-statistics/).
OBS = '<a href="/us-obesity-statistics/" class="active" aria-current="page">Obesity Statistics</a>'
assert src.count(OBS) == 1
src = src.replace(OBS, '<a href="/us-obesity-statistics/">Obesity Statistics</a>')
BF = '<a href="/body-fat-calculator/">Body Fat</a>'
assert src.count(BF) == 2                                                          # desktop menu and mobile menu
src = src.replace(BF, '<a href="/body-fat-calculator/" class="active" aria-current="page">Body Fat</a>')

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 1, len(blocks)
old = json.loads(blocks[0].group(1))
assert [x['@type'] for x in old['@graph']] == ['WebApplication', 'BreadcrumbList', 'Organization', 'Person']
crumbs = old['@graph'][1]
assert [i['name'] for i in crumbs['itemListElement']] == ['Home', 'Calculators', 'Body Fat Calculator']
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
graph = [
    {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'isPartOf': {'@id': SITE + '/#website'},
     'mainEntity': {'@id': URL + '#calculator'}, 'dateModified': '{TODAY}', 'author': PERSON,
     'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}},
    {'@type': 'WebApplication', '@id': URL + '#calculator', 'image': [IMG11, IMG43, IMG16], 'name': H1,
     'description': ('Estimates body fat percentage for adults by four methods, the US Navy tape equations, relative fat mass '
                     'from waist and height, the Deurenberg formula from BMI, age and sex, and Jackson–Pollock 3- or 7-site '
                     'skinfolds, and shows how close each method came to DXA scans: CDC NHANES 2011–2018 for the waist and '
                     'BMI formulas, published studies for the tape and calipers. Places the estimate on the provisional '
                     'ranges and among US adults of the same sex and age.'),
     'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any', 'browserRequirements': 'Requires JavaScript',
     'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
     'featureList': ['Tape measure (US Navy, Hodgdon and Beckett) in inches or centimeters',
                     'Relative fat mass from waist and height (Woolcott and Bergman 2018)',
                     'Deurenberg formula from height, weight, age and sex',
                     'Jackson–Pollock 3-site and 7-site skinfolds with Siri',
                     'How close each method came to DXA scans (CDC NHANES 2011–2018 and published studies)',
                     'Provisional range (Gallagher et al., 2000) and rank among people of the same sex and age group on CDC’s '
                     'scans, ages 16 to 59',
                     'Fat mass and lean mass from your weight'],
     'author': PERSON},
    {k: v for k, v in crumbs.items() if k != '@context'},
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}}
                                       for q, a in FAQ]},
]
ld = {'@context': 'https://schema.org', '@graph': graph}
src = src[:blocks[0].start()] + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' + src[blocks[0].end():]
assert src.count('{TODAY}') == 1

# ---------------------------------------------------------------- body
i, j = src.index('<main'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('og-body-fat-calculator.png') == 0
open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>|<noscript>.*?</noscript>', ' ',
                         re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'body-fat-calculator/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, {len(FAQ)} FAQ, '
      f'{len(TEXTS)} SVG labels checked; example tape {f1(EX_TAPE)} / BMI {f1(EX_DEUR)} / RFM {f1(EX_RFM)}, US share '
      f'{share_txt(EX_MORE)}, calibration {EX_CD} {EX_CR}')
