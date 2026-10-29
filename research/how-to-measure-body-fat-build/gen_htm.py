#!/usr/bin/env python3
"""CMB-021 HOW-TO-MEASURE: rebuilds /blog/how-to-measure-body-fat/ to the D-14 guide pattern (DESIGN.md "Guide pages
(CMB-013)"): H1 + byline, three intro paragraphs, key takeaways, disclaimer, hero figure, contents chips, sections, a flat
FAQ whose JSON-LD equals the visible answers, sources and method, one related block, one 680 px reading column. No
<article> wrapper (D-16).

Demand (research/keyword-ledger.csv): the page owns 913 keywords worth 114,170/mo, "how to calculate body fat percentage"
18,100 the primary; scales 8.1k ("how do scales measure body fat" 1,000, "how accurate are bodyfat scales" 880), how much
body fat to have 3.5k, at home 4.3k, calipers 2.4k, tape 1.1k, InBody 670, Bod Pod 70. Owner's SERP pastes of 2026-10-29
(US/English): "how to calculate body fat percentage", "how to measure body fat percentage", "how accurate are body fat
scales". Ledger owners elsewhere: calculator queries -> /body-fat-calculator/; ranges by age -> /body-fat-percentage-chart/.

The page answers the question with the steps, worked by hand for one example man, then puts numbers on how close each
method gets:
  1. every method against DXA: the study that tested seven methods on the same people against one scanner (Burns et al.,
     2019, Table 3, burns_2019_table3.json: every method read low on average; the average miss as a share of the scan),
     the tape method (Foulis et al., 2023), InBody 770 and SECA mBCA 515 (Lahav et al., 2021) and three smart scales
     (Frija-Masson et al., 2021);
  2. the two home formulas on CDC's own scans (our calculation, htm_stats.py: average miss in points and as a share of the
     scan, with why the share can't be set against Burns's; how far the two formulas land from each other for the same
     person, the second figure);
  3. how much a measuring slip moves each estimate (our calculation: CDC's measurements for the two formulas; the
     published equations at stated example people for the tape and calipers).

Every number comes from htm_stats.json, bfc_stats.json, bfpc_stats.json, burns_2019_table3.json, the published equations,
or a source read in chat on 2026-10-29 (constants below, each with its source and registry row). Round once: f1() prints
halves up and stops if Python's own format would print a figure differently.

usage: python3 gen_htm.py REPO_ROOT
Runs once, on blog/how-to-measure-body-fat/index.html as it stood at 7662c95 (the G1 page); kept as the build record. The
page is written with {TODAY} in its Article dateModified; apply_build.py puts in the apply date (manifest "today": true).
"""
import sys, os, re, json, html, math, csv
from decimal import Decimal, ROUND_HALF_UP

ROOT = sys.argv[1]
BUILD = os.path.join(ROOT, 'research/how-to-measure-body-fat-build')
H = json.load(open(os.path.join(BUILD, 'htm_stats.json')))
T3 = json.load(open(os.path.join(BUILD, 'burns_2019_table3.json'), encoding='utf-8'))
C = json.load(open(os.path.join(ROOT, 'research/body-fat-calculator-build/bfc_stats.json')))
P = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))
PAGE = os.path.join(ROOT, 'blog/how-to-measure-body-fat/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
SITE = 'https://calculatemybmi.net'
URL = SITE + '/blog/how-to-measure-body-fat/'


# ---------------------------------------------------------------- formatting (round once, halves up)
def half(x, nd=1):
    return Decimal(x).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
def f1(x):
    s = str(half(x))
    assert s == f'{x:.1f}' or (s == '0.0' and f'{x:.1f}' == '-0.0'), ('a tie: JavaScript and Python would print differently', x)
    return s
def f4(x): return str(half(x, 4))
def sg(x):
    s = f1(x)
    return ('−' + s[1:]) if s.startswith('-') else ('+' + s)
def pc(x): return int(half(x, 0))
def esc(s): return html.escape(s, quote=False)
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10


# ---------------------------------------------------------------- the published equations (registry body-fat-equations)
LG = math.log10
def navy(sex, h, neck, waist, hips=0.0):
    return 86.010 * LG(waist - neck) - 70.041 * LG(h) + 36.76 if sex == 'm' else 163.205 * LG(waist + hips - neck) - 97.684 * LG(h) - 78.387
def rfm(sex, h, waist): return 64 - 20 * h / waist + (12 if sex == 'f' else 0)
def deur(sex, bmi, age): return 1.20 * bmi + 0.23 * age - 10.8 * (1 if sex == 'm' else 0) - 5.4
def jp3_density(sex, s, age):
    return (1.10938 - 0.0008267 * s + 0.0000016 * s * s - 0.0002574 * age if sex == 'm'
            else 1.0994921 - 0.0009929 * s + 0.0000023 * s * s - 0.0001392 * age)
def siri(d): return 495 / d - 450

# The worked example: one man, by hand. Inputs are the example's; every output is the equation's.
M_AGE, M_H, M_LB, M_NECK, M_WAIST, M_RWAIST, M_SF = 40, 70, 180, 15.5, 36, 37, (15, 25, 18)
EX_TAPE = navy('m', M_H, M_NECK, M_WAIST)
EX_RFM = rfm('m', M_H, M_RWAIST)
EX_BMI = r1(703 * M_LB / M_H ** 2)
EX_DEUR = deur('m', EX_BMI, M_AGE)
EX_SUM = sum(M_SF)
EX_D = jp3_density('m', EX_SUM, M_AGE)
EX_SF = siri(EX_D)
assert (f1(EX_TAPE), f1(EX_RFM), EX_BMI, f1(EX_DEUR), EX_SUM, f4(EX_D), f1(EX_SF)) == \
       ('20.4', '26.2', 25.8, '24.0', 58, '1.0565', '18.5'), (EX_TAPE, EX_RFM, EX_BMI, EX_DEUR, EX_D, EX_SF)
assert f1(siri(float(f4(EX_D)))) == f1(EX_SF)                      # the printed density gives the printed answer
EX_ALL = sorted([('calipers', EX_SF), ('the tape', EX_TAPE), ('height and weight', EX_DEUR), ('waist and height', EX_RFM)],
                key=lambda t: t[1])
# The example woman for the tape and caliper slips: the body fat calculator's starting values (5'4", neck 13, waist 31,
# hips 40, age 35) and skinfolds of 20, 15 and 25 mm (triceps, suprailiac, thigh).
W_AGE, W_H, W_NECK, W_WAIST, W_HIPS, W_SF = 35, 64, 13, 31, 40, (20, 15, 25)
SLIP_TAPE_WAIST = {'f': navy('f', W_H, W_NECK, W_WAIST + 1, W_HIPS) - navy('f', W_H, W_NECK, W_WAIST, W_HIPS),
                   'm': navy('m', M_H, M_NECK, M_WAIST + 1) - navy('m', M_H, M_NECK, M_WAIST)}
SLIP_TAPE_NECK = {'f': navy('f', W_H, W_NECK + 1, W_WAIST, W_HIPS) - navy('f', W_H, W_NECK, W_WAIST, W_HIPS),
                  'm': navy('m', M_H, M_NECK + 1, M_WAIST) - navy('m', M_H, M_NECK, M_WAIST)}
SLIP_SF = {'f': siri(jp3_density('f', sum(W_SF) + 6, W_AGE)) - siri(jp3_density('f', sum(W_SF), W_AGE)),
           'm': siri(jp3_density('m', EX_SUM + 6, M_AGE)) - siri(jp3_density('m', EX_SUM, M_AGE))}
assert ([sg(SLIP_TAPE_WAIST[k]) for k in 'fm'], [sg(SLIP_TAPE_NECK[k]) for k in 'fm'], [sg(SLIP_SF[k]) for k in 'fm']) == \
       (['+1.2', '+1.8'], ['−1.2', '−1.9'], ['+1.9', '+1.7']), (SLIP_TAPE_WAIST, SLIP_TAPE_NECK, SLIP_SF)

# ---------------------------------------------------------------- published comparisons (read in chat 2026-10-29)
# Burns et al., PLOS ONE 2019, Table 3 (burns_2019_table3.json; registry body-fat-method-validation): "Mean Difference
#   (DXA–Surrogate; % Body Fat)", 90% CI, a 10% equivalence interval of -2.7 to 2.7 points ("+/- 10% of the criterion
#   mean, which corresponded to +/- 2.7% body fat"; Table 1: DXA 27.0%, SD 7.6) and MAPE. All seven differences are
#   positive: every method read lower than DXA on average. "differences between DXA and each surrogate assessment
#   increased as mean percent body fat increased" (Table 4: all but Valhalla BIA, r = 0.04). At 15%, "all surrogate
#   assessments, except for Omron BIA and IR, were statistically equivalent with DXA". Pre-test: "large meals at least 2
#   hours prior to testing", "vigorous physical activity or exercise at least 12 hours prior to testing", "alcohol at
#   least 48 hours prior to testing" avoided; liquids limited to 2 glasses of water at least 2 hours before; bladder
#   emptied immediately before. "dehydration can lead to overestimation of percent body fat", "overhydration can lead to
#   underestimation of percent body fat". Skinfolds: "Trained graduate students"; "If the two measurements differed by
#   more than 2mm, a third measurement was taken."
EXPECT_T3 = {'hw': (1.0, [0.6, 1.4], 13.4, True, True), 'sf': (1.4, [1.1, 1.7], 11.7, True, True),
             'adp': (1.6, [1.3, 1.9], 14.5, True, True), 'ir': (4.2, [3.7, 4.7], 18.7, False, False),
             'omron': (4.9, [4.5, 5.3], 21.9, False, False), 'tanita': (3.5, [3.0, 4.0], 17.2, False, True),
             'valhalla': (1.6, [1.1, 2.1], 17.0, True, True)}
assert {r['key']: (r['diff'], r['ci90'], r['mape'], r['eq10'], r['eq15']) for r in T3['rows']} == EXPECT_T3
assert (T3['n'], T3['women'], T3['men'], T3['dxa_mean'], T3['margin']) == (437, 301, 136, 27.0, 2.7)
assert T3['margin'] == round(T3['dxa_mean'] / 10, 1)
BURNS = sorted(T3['rows'], key=lambda r: r['diff'])                 # stable: the Bod Pod before the lab analyzer at 1.6
assert [r['key'] for r in BURNS] == ['hw', 'sf', 'adp', 'valhalla', 'tanita', 'ir', 'omron']
B = {r['key']: r for r in T3['rows']}
assert all(r['diff'] > 0 and r['ci90'][0] > 0 for r in BURNS)                       # all seven read low
assert min(BURNS, key=lambda r: r['mape'])['key'] == 'sf' and max(BURNS, key=lambda r: r['mape'])['key'] == 'omron'
assert [r['key'] for r in BURNS if r['eq10']] == ['hw', 'sf', 'adp', 'valhalla']
assert sorted(r['key'] for r in BURNS if not r['eq15']) == ['ir', 'omron']
BN = T3['n']
# Foulis SA et al., Front Physiol 2023;14:1183836 (registry foulis-2023-circumference-dxa): 481 women and 926 men, Army
#   basic combat training; circumference vs DXA "-6.0%±4.4% for women and -6.0%±3.5% for men".
FOULIS = {'n': 481 + 926, 'err': '6.0', 'sd_w': '4.4', 'sd_m': '3.5'}
# Lahav Y, Goldstein N, Gepner Y, Eur J Clin Nutr 2021;75(8):1275-1282 (PubMed 33483630, read 2026-10-29; registry
#   lahav-2021-inbody-seca): "226 participants (51% men, aged 18-80 years, BMI 18-56 kg/m²)"; InBody 770 and SECA mBCA
#   515; "with 95% limits of agreements between 2.6 and -8.9, and 7.1 and -7.6, respectively"; "BF% assessment by SECA was
#   similar to DXA (-0.3%, p = 0.267), and underestimated by InBody (-3.1%, p < 0.0001)"; "InBody deviations were largest
#   among normal weight people and decreased with increasing BMI group".
LAHAV = {'n': 226, 'inbody': ('3.1', '2.6', '8.9'), 'seca': ('0.3', '7.1', '7.6')}
# Frija-Masson J et al., JMIR Mhealth Uhealth 2021;9(4):e22487 (read 2026-10-29; registry frija-masson-2021-smart-scales):
#   consecutive patients evaluated by DEXA (Lunar iDXA) in the physiology unit of Bichat hospital, Paris, each weighed on
#   one smart scale right after the scan; 53, 52 and 48 patients for Body Partner (Tefal), DietPack (Terraillon) and Body
#   Cardio (Withings); median absolute error for body weight 0.3, 0 and 0.25 kg; fat mass -2.2, -4.4 and -3.7 kg; "Body
#   fat was globally underestimated in all 3 scales"; "Smart scales are not accurate for body composition and should not
#   replace DEXA in patient care."
FRIJA = {'n': (53, 52, 48), 'weight': ('0.3', '0', '0.25'), 'fat': ('2.2', '4.4', '3.7')}
assert max(float(x) for x in FRIJA['weight']) == 0.3
# CDC NHANES 2003-2004 Bioelectrical Impedance Analysis documentation (BIX_C, read 2026-10-29; registry
#   nhanes-bia-documentation): "A small alternating current was passed through surface electrodes placed on the right hand
#   and foot"; impedance, "or opposition to the flow of the electric current"; "Fat mass (FM) was calculated by
#   subtracting FFM by impedance from the participants' measured weight."; "Estimation of percent fat is third order and
#   subject to additional error."; not examined: "Pregnant females"; "Artificial joints, pins, plates, or other types of
#   metal objects in the body"; "Pacemaker or automatic defibrillator".
# CDC NHANES DXX_J documentation (registry nhanes-2011-2018-dxa, read 2026-10-29): DXA "is the most widely accepted method
#   of measuring body composition" "due in part to its speed, ease of use, and low radiation exposure"; "The radiation
#   exposure from DXA whole body scans is extremely low at less than 20 uSv."; "The NHANES BCA option was enabled for whole
#   body scan analysis, this option adds 5% of lean mass to the fat mass."; "Self-reported weight over 450 pounds or height
#   over 6'5" (DXA table limitation)".
# US Army DA Forms 5500 / 5501, May 2013 (registry army-tape-worksheets): neck "just below level of larynx (Adam's
#   apple)"; men abdomen "at the level of the navel"; women waist "at the point of minimal abdominal circumference", hips
#   "where the gluteus muscles (buttocks) protrude backward the most"; "Repeat three times, then average to the nearest
#   0.50 inch."
# Cedars-Sinai (registry rfm-woolcott-2018): "put the tape measure at the top of your hip bone"; Woolcott & Bergman 2018:
#   NHANES waist "at the level of the uppermost lateral border of the right ilium".

# ---------------------------------------------------------------- our calculation (htm_stats.json, bfc_stats.json)
assert H['meta']['n_scanned_20_59'] == C['meta']['n_scanned_20_59'] == 10864 and H['meta']['df'] == 62
MAPE = {f: {s: H['mape'][f][s]['20-59']['mean'] for s in ('women', 'men', 'all')} for f in ('rfm', 'deur')}
MAPE29 = {f: H['mape'][f]['all']['20-29']['mean'] for f in ('rfm', 'deur')}
assert {f: {s: f1(v) for s, v in d.items()} for f, d in MAPE.items()} == \
       {'rfm': {'women': '9.9', 'men': '10.8', 'all': '10.4'}, 'deur': {'women': '12.0', 'men': '15.9', 'all': '14.0'}}, MAPE
assert (f1(MAPE29['rfm']), f1(MAPE29['deur'])) == ('10.7', '16.9')
MAE = {f: H['mae'][f]['all']['mean'] for f in ('rfm', 'deur')}
assert (f1(MAE['rfm']), f1(MAE['deur'])) == ('3.1', '4.4'), MAE
SCAN = H['scan_mean']['all']['mean']
assert f1(SCAN) == '32.9' and SCAN > T3['dxa_mean']                       # CDC's scans average higher than Burns's 27.0%
# The 95% margins of error the method note promises: under 2 points for each share and under 0.4 for each average miss.
MARGINS = ([C['formulas']['rfm'][s_]['within5']['ci95'] for s_ in ('women', 'men')] +
           [H['gap'][s_]['over5']['ci95'] for s_ in ('women', 'men')])
assert all((hi - lo) / 2 < 2 for lo, hi in MARGINS), MARGINS
assert all((v['ci95'][1] - v['ci95'][0]) / 2 < 0.4 for f in ('rfm', 'deur') for v in (H['mape'][f]['all']['20-59'], H['mae'][f]['all']))
NB = {'waist': C['formulas']['rfm']['women']['n'] + C['formulas']['rfm']['men']['n'],
      'bmi': C['formulas']['deur']['women']['n'] + C['formulas']['deur']['men']['n'],
      'both': H['gap']['women']['n'] + H['gap']['men']['n']}
assert NB == {'waist': 10751, 'bmi': 10829, 'both': 10747}, NB
W5 = {f: {s: pc(C['formulas'][f][s]['within5']['pct']) for s in ('women', 'men')} for f in ('rfm', 'deur')}
assert W5 == {'rfm': {'women': 74, 'men': 86}, 'deur': {'women': 62, 'men': 66}}, W5
GAP = H['gap']
assert (pc(GAP['women']['over5']['pct']), pc(GAP['men']['over5']['pct'])) == (38, 15)
assert (f1(GAP['women']['median_abs']), f1(GAP['men']['median_abs'])) == ('4.1', '2.4')
SL = H['slip']
SLIP = {k: {s: SL[s][k]['p50'] for s in ('women', 'men')} for k in ('rfm_waist_in', 'deur_5lb', 'deur_height_in')}
assert {k: [sg(v['women']), sg(v['men'])] for k, v in SLIP.items()} == \
       {'rfm_waist_in': ['+0.9', '+0.9'], 'deur_5lb': ['+1.0', '+0.9'], 'deur_height_in': ['+1.1', '+1.0']}, SLIP
ALL_SLIPS = [abs(v) for d in SLIP.values() for v in d.values()] + \
            [abs(d[k]) for d in (SLIP_TAPE_WAIST, SLIP_TAPE_NECK, SLIP_SF) for k in 'fm']
assert 0.85 <= min(ALL_SLIPS) and max(ALL_SLIPS) < 1.95                              # "by about 1 to 2 points"
# The chart page's numbers (bfpc_stats.json): the provisional ranges and US medians at 20-39
GAL = {k: tuple(v['20-39']) for k, v in P['gallagher']['cuts'].items()}
assert GAL == {'f': (21, 33, 39), 'm': (8, 20, 25)}
# Whole percent: the men's median sits on a tie boundary, 26.13 to 26.18 by tie order (CMB-021 fact-check; DEVLOG §5).
MED = {k: str(pc(P['by_age'][k]['20-39']['p50'])) for k in 'fm'}
assert MED == {'f': '38', 'm': '26'}, MED
HI = {k: f'{GAL[k][1] - 0.1:.1f}' for k in 'fm'}
assert HI == {'f': '32.9', 'm': '19.9'}

# ---------------------------------------------------------------- links (every outside link is a registry row's)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
REG = {r['domain']: r for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}
U = {
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
    'foulis': 'https://doi.org/10.3389/fphys.2023.1183836',
    'lahav': 'https://doi.org/10.1038/s41430-020-00839-5',
    'frija': 'https://doi.org/10.2196/22487',
    'bix': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/BIX_C.htm',
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'rfm': 'https://doi.org/10.1038/s41598-018-29362-1',
    'cedars': 'https://www.cedars-sinai.org/stories-and-insights/healthy-living/relative-fat-mass',
    'army': 'https://cdn.clinicaltrials.gov/large-docs/38/NCT02734238/Prot_SAP_000.pdf',
    'da5500': 'https://home.army.mil/stewart/index.php/download_file/force/6943/434',
    'da5501': 'https://home.army.mil/stewart/index.php/download_file/force/6944/434',
    'deur': 'https://pubmed.ncbi.nlm.nih.gov/2043597/',
    'topend': 'https://www.topendsports.com/testing/density-jackson-pollock.htm',
    'siri': 'https://www.topendsports.com/testing/siri-equation.htm',
    'jp': 'https://periodicos.uninove.br/saude/article/download/1421/1197',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'jpha': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5349253/table/table001',
}
def in_reg(u): return any(u == r['url'] or u in [e.strip() for e in r['endpoint'].split(' ; ')] for r in REG.values())
missing = [k for k, u in U.items() if not in_reg(u)]
assert not missing, missing                                          # patch_cmb021.py adds the new rows first
assert REG['body-fat-method-validation']['url'] == U['burns'] and REG['nhanes-2011-2018-dxa']['url'] == U['dxx']

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS, VBW = [], [], {}
def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827'):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'
def track(svg, x0, y0, x1, y1): RECTS.append((svg, x0, y0, x1, y1))
INK, MUTED, GRID, LINK, OURS = '#111827', '#4b5563', '#e5e7eb', '#0e7490', '#4b5563'

# Figure 1 (hero): the seven methods against one DXA scanner, the same 437 people: method minus scan (dot) with its 90% CI.
VBW['m7'] = 320
MX0, MX1, MLO, MHI = 16, 304, -6, 1
def mx(e): return MX0 + (e - MLO) * (MX1 - MX0) / (MHI - MLO)
fm = []
for i, r in enumerate(BURNS):
    lab, d, ci, mape = r['label'], r['diff'], r['ci90'], r['mape']
    yl = 14 + i * 46; ym = yl + 16
    fm.append(text('m7', 4, yl, f'{lab}: −{f1(d)}', 12, anchor='start', weight=600, fill='#1f2937'))
    for e in (-6, -4, -2):
        fm.append(f'<line x1="{mx(e):.1f}" y1="{ym - 12}" x2="{mx(e):.1f}" y2="{ym + 12}" stroke="{GRID}" stroke-width="1"/>')
    fm.append(f'<line x1="{mx(0):.1f}" y1="{ym - 12}" x2="{mx(0):.1f}" y2="{ym + 12}" stroke="{MUTED}" stroke-width="1.5" '
              'stroke-dasharray="4 3"/>')
    track('m7', mx(0) - 1, ym - 12, mx(0) + 1, ym + 12)
    tip = (f'{lab}: read {f1(d)} points below DXA on average (90% CI {f1(ci[0])} to {f1(ci[1])}); average miss {f1(mape)}% '
           f'of the scan’s reading')
    fm.append(f'<line x1="{mx(-ci[1]):.1f}" y1="{ym}" x2="{mx(-ci[0]):.1f}" y2="{ym}" stroke="{LINK}" stroke-width="3" '
              f'stroke-linecap="round"><title>{esc(tip)}</title></line>')
    fm.append(f'<circle cx="{mx(-d):.1f}" cy="{ym}" r="5" fill="{INK}" stroke="#ffffff" stroke-width="1.5"><title>{esc(tip)}</title></circle>')
    track('m7', mx(-ci[1]) - 5, ym - 5, mx(-ci[0]) + 5, ym + 5)
YB = 14 + len(BURNS) * 46
for e in (-6, -4, -2, 0):
    fm.append(text('m7', mx(e), YB + 6, ('−' if e < 0 else '') + str(abs(e)), 12, fill=MUTED))
fm.append(text('m7', 160, YB + 24, 'Method minus DXA scan, body fat points', 12, fill='#1f2937'))
H_M7 = YB + 32
svg_m7 = (f'<svg viewBox="0 0 320 {H_M7}" role="img" aria-labelledby="m7-t m7-d" xmlns="http://www.w3.org/2000/svg" '
          f'font-family="inherit"><title id="m7-t">Seven body fat methods against one DXA scan, the same {BN} people</title>'
          f'<desc id="m7-d">Average difference from a DXA scan in {BN} college students, with 90% confidence intervals. '
          + ' '.join(f'{r["label"]}: {f1(r["diff"])} points lower ({f1(r["ci90"][0])} to {f1(r["ci90"][1])}).' for r in BURNS)
          + ' Every method read lower than the scan on average. Burns et al., PLOS ONE 2019, Table 3.</desc>'
          + ''.join(fm) + '</svg>')

# Figure 2: how far apart the two home formulas landed for the same person (htm_stats gap): within 3 points, 3 to 5, more
# than 5. (The CMB-021 fact-check: an average-miss figure that set the formulas' MAPE beside Burns's invited a comparison
# the different average scan readings don't allow, 32.9% on CDC's scans against 27.0%; the page states that in words.)
VBW['gap'] = 320
GX0, GW = 4, 300
SEG = (('Within 3 points of each other', '#cffafe', '#164e63'), ('3 to 5 points apart', '#67e8f9', '#164e63'),
       ('More than 5 points apart', LINK, '#ffffff'))
def thirds(g):
    o3, o5 = g['over3']['pct'], g['over5']['pct']
    return [100 - o3, o3 - o5, o5]
GAPS = {s_: thirds(GAP[s_]) for s_ in ('women', 'men')}
GAPR = {s_: [pc(v) for v in GAPS[s_]] for s_ in GAPS}
assert GAPR == {'women': [37, 25, 38], 'men': [60, 25, 15]} and all(sum(v) == 100 for v in GAPR.values()), GAPR
fg = []
for k, (lab, fill, _) in enumerate(SEG):
    yy = 14 + k * 18
    fg.append(f'<rect x="4" y="{yy - 10}" width="12" height="12" rx="2" fill="{fill}" stroke="{LINK}" stroke-width="1"/>')
    track('gap', 4, yy - 10, 16, yy + 2)
    fg.append(text('gap', 22, yy, lab, 12, anchor='start', fill='#1f2937'))
GROWS = (('women', 'Women', 76), ('men', 'Men', 134))
for s_, lab, yt in GROWS:
    yb = yt + 8
    fg.append(text('gap', 4, yt, lab, 12, anchor='start', weight=600, fill='#1f2937'))
    x = GX0
    for k, (v, (seg, fill, ink)) in enumerate(zip(GAPS[s_], SEG)):
        w = GW * v / 100
        tip = f'{lab}: {GAPR[s_][k]}% {seg[0].lower() + seg[1:]}'
        fg.append(f'<rect x="{x:.1f}" y="{yb}" width="{w:.1f}" height="26" fill="{fill}" stroke="#ffffff" stroke-width="1">'
                  f'<title>{esc(tip)}</title></rect>')
        t = f'{GAPR[s_][k]}%'
        assert len(t) * 12 * 0.6 + 6 <= w, ('in-bar label does not fit', s_, k, w)
        fg.append(f'<text x="{x + w / 2:.1f}" y="{yb + 17}" font-size="12" text-anchor="middle" font-weight="600" fill="{ink}">{t}</text>')
        x += w
    assert abs(x - (GX0 + GW)) < 1e-6
    fg.append(f'<rect x="{GX0}" y="{yb}" width="{GW}" height="26" fill="none" stroke="#94a3b8" stroke-width="1"/>')
    track('gap', GX0, yb, GX0 + GW, yb + 26)
H_GAP = GROWS[-1][2] + 8 + 26 + 10
gap_desc = (f'Women: {GAPR["women"][0]}% within 3 points of each other, {GAPR["women"][1]}% 3 to 5 points apart, '
            f'{GAPR["women"][2]}% more than 5 points apart. Men: {GAPR["men"][0]}%, {GAPR["men"][1]}% and {GAPR["men"][2]}%. '
            'US adults aged 20 to 59 with both formulas, CDC’s 2011–2018 survey (our calculation).')
svg_gap = (f'<svg viewBox="0 0 320 {H_GAP}" role="img" aria-labelledby="gap-t gap-d" xmlns="http://www.w3.org/2000/svg" '
           'font-family="inherit"><title id="gap-t">How far apart the two home formulas landed for the same person</title>'
           f'<desc id="gap-d">{gap_desc}</desc>' + ''.join(fg) + '</svg>')

def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b_ in TEXTS[i + 1:]:
        if a[0] == b_[0] and overlap(a, b_): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b_[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r): raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- the page's text
H1 = 'How to Calculate Body Fat Percentage'
rfm_all, deur_all = f1(MAPE['rfm']['all']), f1(MAPE['deur']['all'])
lo_all, hi_all = f1(BURNS[0]['diff']), f1(BURNS[-1]['diff'])
assert (lo_all, hi_all) == ('1.0', '4.9')
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">How do you calculate your body fat percentage at home? How accurate is a body fat scale? Which '
    'method comes closest to a scan?</p>'
    '<p class="intro-text">At home, you take a few measurements with a tape measure or skinfold calipers and put them into '
    'a published equation. A DXA scan, which CDC calls the most widely accepted method of measuring body composition '
    f'({ext(U["dxx"], "CDC")}), is the reference in the studies below. In a study that tested seven methods on the same '
    f'{BN} college students, all seven read lower than the scan on average, by {lo_all} to {hi_all} points '
    f'({ext(U["burns"], "Burns et al., 2019")}).</p>'
    '<p class="intro-text">Below: the steps for each home method, worked through for one example, how close the tested '
    'methods get to a scan, how body fat scales work, and how much a slip of the tape changes the answer.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    '<p class="answer"><strong>To calculate your body fat percentage at home, take a few body measurements and put them '
    'into a published equation.</strong> The simplest needs a tape measure and your height: men 64 − 20 × height ÷ waist, '
    'women 76 − 20 × height ÷ waist, with the waist measured at the top of the hip bones (relative fat mass). On CDC’s '
    f'scans of US adults aged 20 to 59, it came within 5 points of the scan for {W5["rfm"]["men"]}% of men and '
    f'{W5["rfm"]["women"]}% of women (our calculation).</p><ul>'
    f'<li>Seven-site skinfolds had <strong>the smallest average miss of seven methods</strong> tested on the same college '
    f'students, {f1(B["sf"]["mape"])}% of the scan’s reading, and a hand-held device the largest, '
    f'{f1(B["omron"]["mape"])}% (Burns et al., 2019).</li>'
    f'<li>Three smart scales checked against DXA <strong>read fat mass {FRIJA["fat"][0]} to {FRIJA["fat"][1]} kg low</strong>, '
    f'while their median weight differences from the scan were 0 to {FRIJA["weight"][0]} kg (Frija-Masson et al., '
    '2021).</li>'
    f'<li><strong>A small measuring slip moves the answer by about a point:</strong> for the typical US adult aged 20 to '
    f'59, 1 inch on '
    f'the waist moves the waist-and-height estimate by {sg(SLIP["rfm_waist_in"]["women"])[1:]} points, and 5 lb on the '
    f'scale moves the height-and-weight estimate by {sg(SLIP["deur_5lb"]["men"])[1:]} to '
    f'{sg(SLIP["deur_5lb"]["women"])[1:]} (our calculation).</li>'
    f'<li><strong>Methods disagree for the same person:</strong> in CDC’s survey of US adults aged 20 to 59, the two home '
    f'formulas were more than 5 points apart for {pc(GAP["women"]["over5"]["pct"])}% of women and '
    f'{pc(GAP["men"]["over5"]["pct"])}% of men (our calculation), so track one method, with the same device and the same '
    'measuring spots.</li>'
    '<li>Before any test, copy the seven-method study’s routine: no large meal for 2 hours, no vigorous exercise for 12, '
    'no alcohol for 48, and an empty bladder.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This guide is for information only. A body fat '
    'estimate is not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')
assert sg(SLIP['rfm_waist_in']['women']) == sg(SLIP['rfm_waist_in']['men']) and SLIP['deur_5lb']['men'] < SLIP['deur_5lb']['women']

hero = (f'<figure class="figure">{svg_m7}<figcaption>Seven ways to estimate body fat, tested on the same {BN} college '
        'students against one DXA scanner: each method’s average difference from the scan (dot) and its 90% confidence '
        'interval (line). Left of the dashed line, the method read lower than the scan. Burns et al., PLOS ONE 2019, '
        'Table 3.</figcaption></figure>')

CHIPS = (('steps', 'Step by step'), ('accuracy', 'How close'), ('scales', 'Scales'), ('measuring', 'Measuring well'),
         ('lab', 'Lab and gym'), ('meaning', 'What it means'), ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

answers = ', '.join(f'{f1(v)}% from {lab}' for lab, v in EX_ALL[:-1]) + f' and {f1(EX_ALL[-1][1])}% from {EX_ALL[-1][0]}'
assert answers == '18.5% from calipers, 20.4% from the tape, 24.0% from height and weight and 26.2% from waist and height'
sec_steps = (
    '<section id="steps" class="content-section flow"><h2>How to calculate body fat percentage at home</h2>'
    '<p>Each home method is a published equation fed with a few measurements. The worked examples are for one man: 40 '
    'years old, 5′10″ (70 inches) and 180 lb, with a 15.5-inch neck, and a waist of 36 inches at the navel and 37 inches at '
    'the top of the hip bones. The <a href="/body-fat-calculator/">body fat calculator</a> does the arithmetic for all four '
    'methods.</p>'
    '<h3>Waist and height (relative fat mass)</h3><ol>'
    '<li>Measure your height without shoes.</li>'
    f'<li>Measure your waist at the top of your hip bones ({ext(U["cedars"], "Cedars-Sinai")}). CDC’s survey measures the '
    f'waist at the same level, the top of the right hip bone ({ext(U["rfm"], "Woolcott and Bergman, 2018")}).</li>'
    '<li>With both in the same unit, work out 64 − 20 × height ÷ waist for men, or 76 − 20 × height ÷ waist for '
    'women.</li></ol>'
    f'<p>For the example man: 64 − 20 × {M_H} ÷ {M_RWAIST} = {f1(EX_RFM)}%. The formula uses the same two measurements as '
    'the <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>.</p>'
    '<h3>Tape measure (the Navy method)</h3><ol>'
    '<li>Measure your neck just below the Adam’s apple.</li>'
    '<li>Men: measure your waist at the navel. Women: measure your waist at its narrowest and your hips where the buttocks '
    'stick out most.</li>'
    f'<li>Take each measurement three times and average them, as the Army’s 2013 worksheets do '
    f'({ext(U["da5500"], "DA Forms 5500")} and {ext(U["da5501"], "5501")}).</li>'
    '<li>Put the inches into the Navy equations: men 86.010 × log10(waist − neck) − 70.041 × log10(height) + 36.76; '
    'women 163.205 × log10(waist + hips − neck) − 97.684 × log10(height) − 78.387 '
    f'({ext(U["army"], "US Army Table B-5")}).</li></ol>'
    f'<p>For the example man: 86.010 × log10({M_WAIST} − {M_NECK}) − 70.041 × log10({M_H}) + 36.76 = {f1(EX_TAPE)}%.</p>'
    '<h3>Height and weight (the BMI formula)</h3><ol>'
    '<li>Work out your BMI: weight in pounds × 703 ÷ height in inches squared, rounded to one decimal (the '
    '<a href="/">BMI calculator</a> does this).</li>'
    '<li>Body fat % = 1.20 × BMI + 0.23 × age − 10.8 × sex − 5.4, with sex 1 for men and 0 for women '
    f'({ext(U["deur"], "Deurenberg et al., 1991")}).</li></ol>'
    f'<p>For the example man: BMI = {M_LB} × 703 ÷ {M_H}² = {EX_BMI}, then 1.20 × {EX_BMI} + 0.23 × {M_AGE} − 10.8 − 5.4 = '
    f'{f1(EX_DEUR)}%.</p>'
    '<h3>Skinfold calipers (3 sites)</h3><ol>'
    '<li>Measure a skinfold with the calipers, in millimeters, at three sites: chest, abdomen and thigh for men; triceps, '
    'suprailiac (just above the hip bone) and thigh for women.</li>'
    '<li>Measure each site twice and take a third reading if the two differ by more than 2 mm, as the trained measurers in '
    f'the seven-method study did ({ext(U["burns"], "Burns et al., 2019")}).</li>'
    f'<li>Add the three, turn the sum into body density with the {ext(U["topend"], "Jackson–Pollock equation")}, then into '
    f'body fat with {ext(U["siri"], "Siri’s")}: 495 ÷ density − 450.</li></ol>'
    f'<p>For the example man, skinfolds of {M_SF[0]}, {M_SF[1]} and {M_SF[2]} mm add up to {EX_SUM}: density = 1.10938 − '
    f'0.0008267 × {EX_SUM} + 0.0000016 × {EX_SUM}² − 0.0002574 × {M_AGE} = {f4(EX_D)}, and 495 ÷ {f4(EX_D)} − 450 = '
    f'{f1(EX_SF)}%. For women the density equation is 1.0994921 − 0.0009929 × S + 0.0000023 × S² − 0.0001392 × age, where '
    'S is the sum. The seven-method study measured seven sites, with trained measurers; no study cited here checked the '
    '3-site version against DXA.</p>'
    f'<p><strong>Four methods, four answers for one man:</strong> {answers}.</p></section>')

def nb(label):                                                     # a number keeps its unit on the same line
    return re.sub(r'(\d) (sites|electrodes|inch|lb|mm)\b', '\\1\u00a0\\2', label)
burns_rows = ''.join(f'<tr><th scope="row">{nb(r["label"])}</th><td class="num">{f1(r["diff"])}</td>'
                     f'<td class="num">{f1(r["mape"])}%</td></tr>' for r in BURNS)
sec_acc = (
    '<section id="accuracy" class="content-section flow"><h2>How close tested methods get to a DXA scan</h2>'
    '<p>Studies that test one method each use different people and different scanners, so the clearest comparison puts '
    f'every method on the same people. Burns and colleagues did that for seven methods in {BN} college students, mean age '
    '19, against one DXA scanner (Hologic Discovery W). Every method read lower than the scan on average, and for all but the '
    f'four-electrode analyzer the gap grew as body fat rose ({ext(U["burns"], "Burns et al., 2019")}).</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Seven methods against '
    f'DXA in the same {BN} college students</caption><thead><tr><th scope="col">Method</th><th scope="col" class="num">Below '
    'DXA<span class="th-sub">points</span></th><th scope="col" class="num">Average miss</th></tr></thead>'
    f'<tbody>{burns_rows}</tbody></table></div>'
    '<p class="source-note">Below DXA: how far below the scan the method read on average (the 90% confidence intervals '
    'are in the figure at the top). Average miss: the average distance from the scan as a share of the scan’s reading (mean '
    'absolute percentage error), so at 30% body fat a 10% miss is 3 points. Average difference inside the study’s '
    f'±{f1(T3["margin"])}-point equivalence margin (10% of the {f1(T3["dxa_mean"])}% average scan): underwater weighing, '
    'skinfolds, the Bod Pod and the four-electrode analyzer; single readings missed by more.</p>'
    f'<p><strong>The two home formulas on CDC’s scans.</strong> On CDC’s scans of US adults aged 20 to 59, the '
    f'waist-and-height formula missed by {f1(MAE["rfm"])} points on average and the height-and-weight formula by '
    f'{f1(MAE["deur"])} points: {rfm_all}% and {deur_all}% of the scan’s reading (our calculation). Those shares don’t line '
    'up with the college study’s. The people and scanners differ, and CDC’s scans read '
    f'{f1(SCAN)}% body fat on average against the students’ {f1(T3["dxa_mean"])}%, so the same miss in points is a '
    'smaller share of a higher reading.</p>'
    '<h3>Three more comparisons with DXA</h3><ul>'
    f'<li>Tape measure: in {FOULIS["n"]:,} US Army recruits, the Navy method read {FOULIS["err"]} points below DXA on '
    f'average, with a standard deviation of {FOULIS["sd_w"]} points for women and {FOULIS["sd_m"]} for men '
    f'({ext(U["foulis"], "Foulis et al., 2023")}).</li>'
    f'<li>InBody 770: in {LAHAV["n"]} adults aged 18 to 80, it read {LAHAV["inbody"][0]} points below DXA on average, and '
    f'for about 95% of them it landed between {LAHAV["inbody"][1]} points above and {LAHAV["inbody"][2]} points below the '
    'scan; its underestimate was largest at normal weight and shrank as BMI rose. A SECA mBCA 515 in the same people read '
    f'{LAHAV["seca"][0]} points below on average ({ext(U["lahav"], "Lahav et al., 2021")}).</li>'
    f'<li>Smart scales: three home scales checked against DXA in {min(FRIJA["n"])} to {max(FRIJA["n"])} hospital patients '
    f'each read fat mass low, by a median of {FRIJA["fat"][0]} to {FRIJA["fat"][1]} kg '
    f'({ext(U["frija"], "Frija-Masson et al., 2021")}).</li></ul>'
    '<p>The <a href="/body-fat-calculator/#accuracy">body fat calculator</a> checks the two formulas in more detail: by BMI, '
    'by age, and what the scans read for any estimate.</p></section>')

sec_scales = (
    '<section id="scales" class="content-section flow"><h2>How accurate are body fat scales?</h2>'
    '<p>A body fat scale runs an impedance test: it passes a small current between electrodes under your feet and measures '
    'the impedance, the body’s opposition to the current. CDC’s documentation for its own impedance test, which used '
    'electrodes on the right hand and foot, explains the rest: '
    'an equation turns the impedance into fat-free mass, fat mass is your weight minus that, and percent fat, worked out '
    f'from those estimates, is a third-order estimate, “subject to additional error” ({ext(U["bix"], "CDC")}).</p>'
    f'<p>In the seven-method study, the foot-to-foot scale (Tanita BF-556) read {f1(B["tanita"]["diff"])} points below DXA '
    f'on average, with an average miss of {f1(B["tanita"]["mape"])}%, and the hand-held device (Omron HBF-306) read '
    f'{f1(B["omron"]["diff"])} points below, with {f1(B["omron"]["mape"])}%, the largest miss of the seven. The lab '
    'analyzer, with four electrodes on the right hand and foot while lying down, read '
    f'{f1(B["valhalla"]["diff"])} points below (Burns et al., 2019).</p>'
    '<p>Three smart scales sold for home use (Tefal Body Partner, Terraillon DietPack and Withings Body Cardio) were checked '
    'against DXA in patients referred for a scan at a Paris hospital. Their median weight differences from the scan’s body '
    f'mass were {FRIJA["weight"][0]}, {FRIJA["weight"][1]} and {FRIJA["weight"][2]} kg, but each underestimated fat mass, '
    f'by a median of {FRIJA["fat"][0]}, {FRIJA["fat"][1]} and {FRIJA["fat"][2]} kg (Frija-Masson et al., 2021).</p>'
    '<p>Water moves the reading: dehydration can push the body fat estimate up and overhydration can push it down (Burns et '
    'al., 2019). To follow a trend, weigh in under the same conditions every time, with the routine in the next section. '
    'CDC’s survey did not run its impedance test on pregnant women, or on people with a pacemaker or automatic '
    'defibrillator or with artificial joints, pins or plates (CDC).</p></section>')

SLIP_GROUPS = [
    ('Waist and height formula', [('Waist 1 inch too large', SLIP['rfm_waist_in']['women'], SLIP['rfm_waist_in']['men'])]),
    ('Height and weight formula', [('Weight 5 lb too high', SLIP['deur_5lb']['women'], SLIP['deur_5lb']['men']),
                                   ('Height 1 inch too short', SLIP['deur_height_in']['women'], SLIP['deur_height_in']['men'])]),
    ('Tape method*', [('Waist 1 inch too large', SLIP_TAPE_WAIST['f'], SLIP_TAPE_WAIST['m']),
                      ('Neck 1 inch too large', SLIP_TAPE_NECK['f'], SLIP_TAPE_NECK['m'])]),
    ('Calipers, 3 sites*', [('2 mm too much at each site', SLIP_SF['f'], SLIP_SF['m'])]),
]
slip_body = ''.join(
    f'<tbody><tr><th scope="rowgroup" colspan="3">{g}</th></tr>'
    + ''.join(f'<tr><th scope="row">{nb(a)}</th><td class="num">{sg(w)}</td><td class="num">{sg(m)}</td></tr>' for a, w, m in rows)
    + '</tbody>' for g, rows in SLIP_GROUPS)
sec_measuring = (
    '<section id="measuring" class="content-section flow"><h2>How to measure body fat accurately</h2>'
    '<p>A small measuring slip moves each estimate by about 1 to 2 points:</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>How much a measuring '
    'slip moves each estimate, in body fat points</caption><thead><tr><th scope="col">Measuring slip</th><th scope="col" '
    f'class="num">Women</th><th scope="col" class="num">Men</th></tr></thead>{slip_body}</table></div>'
    '<p class="source-note">Our calculation from the published equations. The two formulas’ rows are medians across US '
    'adults aged 20 to 59, from each person’s own height, waist and weight in CDC’s 2011–2018 survey. *CDC measured neither '
    'the neck nor skinfolds, so the tape and caliper rows use the example man above and a woman of 35, 5′4″, with a 13-inch '
    'neck, a 31-inch waist, 40-inch hips and skinfolds of 20, 15 and 25 mm (triceps, suprailiac, thigh).</p>'
    '<p><strong>Repeat and average.</strong> The Army’s worksheets take each tape measurement three times and average them '
    'to the nearest half inch; the seven-method study measured each skinfold twice and took a third reading when the two '
    'differed by more than 2 mm.</p>'
    '<p><strong>Before any test.</strong> The seven-method study asked for a routine you can copy for any method: no large '
    'meal in the 2 hours before, no vigorous exercise in the 12 hours before, no alcohol in the 48 hours before, no more '
    'than two glasses of water, finished at least 2 hours before, and an empty bladder (Burns et al., 2019).</p>'
    '<p><strong>Compare like with like.</strong> Two methods can differ by several points for the same person: in CDC’s '
    'survey of US adults aged 20 to 59, the waist-and-height and height-and-weight formulas were more than 5 points apart '
    f'for {pc(GAP["women"]["over5"]["pct"])}% of women and {pc(GAP["men"]["over5"]["pct"])}% of men, and the median gap was '
    f'{f1(GAP["women"]["median_abs"])} points for women and {f1(GAP["men"]["median_abs"])} for men (our calculation). Track '
    'one method, one device and the same measuring spots.</p>'
    f'<figure class="figure">{svg_gap}<figcaption>How far apart the waist-and-height formula (relative fat mass) and the '
    'height-and-weight formula (Deurenberg) landed for the same person: US adults aged 20 to 59 with both measured in '
    'CDC’s 2011–2018 survey (our calculation).</figcaption></figure></section>')

sec_lab = (
    '<section id="lab" class="content-section flow"><h2>Lab and gym methods: DXA, Bod Pod and underwater weighing</h2>'
    '<h3>DXA scan</h3>'
    '<p>A whole-body X-ray scan that measures bone and soft tissue and splits the soft tissue into fat and lean. CDC uses it '
    'in its national survey and calls it the most widely accepted method of measuring body composition, in part for its '
    f'speed, ease of use and low radiation, less than 20 µSv for a whole-body scan ({ext(U["dxx"], "CDC")}). The software '
    'matters too: CDC’s scans were analyzed with an option that adds 5% of lean mass to the fat mass, and the scanner table '
    'kept out people over 450 lb or taller than 6′5″ (CDC).</p>'
    '<h3>Underwater weighing</h3>'
    '<p>You breathe out fully and are weighed under water; with your weight on land, that gives your body density, which an '
    f'equation turns into body fat. In the seven-method study it read {f1(B["hw"]["diff"])} point below DXA on average, the '
    f'closest of the seven, with an average miss of {f1(B["hw"]["mape"])}% (Burns et al., 2019).</p>'
    '<h3>Bod Pod (air displacement)</h3>'
    '<p>You sit in a sealed chamber that measures the air you displace, which gives your body volume and so your density. '
    f'It read {f1(B["adp"]["diff"])} points below DXA on average, with an average miss of {f1(B["adp"]["mape"])}% (Burns et '
    'al., 2019).</p>'
    '<h3>Near-infrared</h3>'
    '<p>A light wand held on the biceps (the study used a Futrex-6100). It read '
    f'{f1(B["ir"]["diff"])} points below DXA on average, with an average miss of {f1(B["ir"]["mape"])}%, and was one of the '
    'two methods that failed even the study’s looser 15% equivalence test (Burns et al., 2019).</p></section>')

sec_meaning = (
    '<section id="meaning" class="content-section flow"><h2>What your number means</h2>'
    f'<p>Provisional ranges tied to BMI call {GAL["f"][0]} to {HI["f"]}% body fat healthy for women aged 20 to 39 and '
    f'{GAL["m"][0]} to {HI["m"]}% for men, with higher ranges at older ages '
    f'({ext(U["gallagher"], "Gallagher et al., 2000")}). On CDC’s scans of US adults aged 20 to 39, the median was about '
    f'{MED["f"]}% for women and {MED["m"]}% for men. The <a href="/body-fat-percentage-chart/">body fat percentage '
    'chart</a> has the ranges and the US shares for every age, and <a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a> '
    'explains why the two measures can disagree.</p></section>')

FAQ = [
    ('How do I calculate my body fat percentage at home?',
     'Take a few measurements and put them into a published equation. With only a tape measure and your height, relative '
     'fat mass is 64 − 20 × height ÷ waist for men and 76 − 20 × height ÷ waist for women, with the waist at the top of the '
     f'hip bones; on CDC’s scans of US adults aged 20 to 59 it came within 5 points of the scan for {W5["rfm"]["men"]}% of men and '
     f'{W5["rfm"]["women"]}% of women (our calculation). The tape method and calipers need more measurements; the '
     '<a href="/body-fat-calculator/">body fat calculator</a> does the arithmetic for all four methods.'),
    ('What is the most accurate way to measure body fat?',
     'No method is exact. DXA, which CDC calls the most widely accepted method of measuring body composition, is the '
     f'reference the studies here check other methods against. Against DXA in {BN} college students, underwater weighing '
     f'came closest on average ({f1(B["hw"]["diff"])} point lower) and seven-site skinfolds had the smallest average miss, '
     f'{f1(B["sf"]["mape"])}% of the scan’s reading (Burns et al., 2019). At home, the waist-and-height formula missed '
     f'CDC’s scans of US adults aged 20 to 59 by {f1(MAE["rfm"])} points on average (our calculation).'),
    ('How accurate are body fat scales?',
     f'Close for weight, much less so for fat. In {BN} college students, a foot-to-foot scale read '
     f'{f1(B["tanita"]["diff"])} points below DXA on average and missed by {f1(B["tanita"]["mape"])}% of the scan’s '
     'reading (Burns et al., 2019). Three smart scales checked against DXA in hospital patients had median weight '
     f'differences of 0 to {FRIJA["weight"][0]} kg from the scan’s body mass but read fat mass {FRIJA["fat"][0]} to '
     f'{FRIJA["fat"][1]} kg low (Frija-Masson et al., 2021).'),
    ('How do scales measure body fat?',
     'They pass a small current between electrodes under your feet and measure the impedance, the body’s opposition to '
     'the current. An equation turns that into fat-free mass, and fat mass is your weight minus that. CDC’s documentation '
     'for its own impedance test calls percent fat a third-order estimate, “subject to additional error,” and water '
     'matters: dehydration can push the estimate up and overhydration down (Burns et al., 2019).'),
    ('How accurate are body fat calipers?',
     f'In trained hands, among the closest methods: seven-site skinfolds taken by trained graduate students read '
     f'{f1(B["sf"]["diff"])} points below DXA on average and had the smallest average miss of seven methods, '
     f'{f1(B["sf"]["mape"])}% of the scan’s reading (Burns et al., 2019). A slip of 2 mm at each of three sites moves a '
     f'3-site estimate by about {sg(SLIP_SF["m"])[1:]} points for a {M_AGE}-year-old man whose three skinfolds add up to '
     f'{EX_SUM} mm (our calculation); no study cited here checked the 3-site version against DXA.'),
    ('How do I measure body fat with a tape measure?',
     'Measure your neck just below the Adam’s apple and your waist at the navel (men) or at its narrowest (women), plus '
     'the hips where the buttocks stick out most for women, three times each, and average them, as the Army’s 2013 '
     f'worksheets do. Then use the Navy equations, in inches. In US Army recruits, the method read {FOULIS["err"]} points '
     'below DXA on average (Foulis et al., 2023).'),
    ('How accurate is InBody?',
     f'In {LAHAV["n"]} adults aged 18 to 80, the InBody 770 read {LAHAV["inbody"][0]} points below DXA on average, and for '
     f'about 95% of them it landed between {LAHAV["inbody"][1]} points above and {LAHAV["inbody"][2]} points below the '
     'scan; its underestimate was largest at normal weight and shrank as BMI rose (Lahav et al., 2021). A SECA mBCA 515 in the '
     f'same people read {LAHAV["seca"][0]} points below DXA on average.'),
    ('How accurate is a Bod Pod?',
     f'In {BN} college students, the Bod Pod read {f1(B["adp"]["diff"])} points below DXA on average and missed by '
     f'{f1(B["adp"]["mape"])}% of the scan’s reading; underwater weighing read {f1(B["hw"]["diff"])} point below (Burns et '
     'al., 2019).'),
    ('Why do different methods give different numbers?',
     'Each method measures something else (body density, impedance, skinfold thickness or circumferences) and turns it '
     'into body fat with its own equation. In CDC’s survey of US adults aged 20 to 59, the waist-and-height and '
     'height-and-weight formulas '
     f'were more than 5 points apart for {pc(GAP["women"]["over5"]["pct"])}% of women and '
     f'{pc(GAP["men"]["over5"]["pct"])}% of men (our calculation).'),
    ('How much body fat should I have?',
     f'Provisional ranges tied to BMI put a healthy body fat at {GAL["f"][0]} to {HI["f"]}% for women and {GAL["m"][0]} to '
     f'{HI["m"]}% for men aged 20 to 39, a little higher at older ages (Gallagher et al., 2000). On CDC’s scans of US adults '
     f'aged 20 to 39, the median was about {MED["f"]}% for women and {MED["m"]}% for men. The '
     '<a href="/body-fat-percentage-chart/">body fat percentage chart</a> has the ranges for every age.'),
]
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p>'
                   '</div></div>' for q, a in FAQ)
sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'Burns RD, Fu Y, Constantino N. {ext(U["burns"], "Measurement agreement in percent body fat estimates among laboratory and field assessments in college students: Use of equivalence testing")}. '
    'PLOS ONE 2019;14(3):e0214029 (Table 3: differences from DXA, confidence intervals and average misses; the devices; the '
    'pre-test routine).',
    f'Foulis SA, et al. {ext(U["foulis"], "Body composition changes during 8 weeks of military training are not accurately captured by circumference-based assessments")}. '
    'Front Physiol 2023;14:1183836.',
    f'Lahav Y, Goldstein N, Gepner Y. {ext(U["lahav"], "Comparison of body composition assessment across body mass index categories by two multifrequency bioelectrical impedance analysis devices and dual-energy X-ray absorptiometry in clinical settings")}. '
    'Eur J Clin Nutr 2021;75(8):1275–82.',
    f'Frija-Masson J, et al. {ext(U["frija"], "Accuracy of Smart Scales on Weight and Body Composition: Observational Study")}. '
    'JMIR Mhealth Uhealth 2021;9(4):e22487.',
    f'CDC, NHANES 2003–2004 {ext(U["bix"], "Bioelectrical Impedance Analysis")} documentation: how the test works and who '
    'was not tested.',
    f'CDC, NHANES 2011–2018 {ext(U["dxx"], "whole-body DXA scans")} with the demographics and body measures files (DXX, DEMO, '
    f'BMX, cycles G to J): our calculation for {H["meta"]["n_scanned_20_59"]:,} adults aged 20 to 59 ({NB["waist"]:,} '
    f'with a measured waist, {NB["bmi"]:,} with a BMI, {NB["both"]:,} with both). The documentation '
    'calls DXA “the most widely accepted method of measuring body composition”.',
    f'Woolcott OO, Bergman RN. {ext(U["rfm"], "Relative fat mass (RFM) as a new estimator of whole-body fat percentage")}. '
    f'Sci Rep 2018;8:10980. Cedars-Sinai, {ext(U["cedars"], "Building a Better Body Measurement: Relative Fat Mass")} '
    '(where to measure the waist).',
    'Hodgdon JA, Beckett MB. Prediction of percent body fat for U.S. Navy men and women from body circumferences and '
    'height. Naval Health Research Center reports 84-11 and 84-29, 1984, as reproduced in the US Army’s sample calculations '
    f'(Table B-5) in study protocol {ext(U["army"], "NCT02734238")}.',
    f'US Army. Body fat content worksheets {ext(U["da5500"], "DA Form 5500 (male)")} and '
    f'{ext(U["da5501"], "DA Form 5501 (female)")}, May 2013: where and how to measure.',
    f'Deurenberg P, Weststrate JA, Seidell JC. {ext(U["deur"], "Body mass index as a measure of body fatness: age- and sex-specific prediction formulas")}. '
    'Br J Nutr 1991;65:105–14.',
    'Jackson AS, Pollock ML. Br J Nutr 1978;40:497–504; Jackson AS, Pollock ML, Ward A. Med Sci Sports Exerc '
    f'1980;12:175–81: the skinfold equations as printed by {ext(U["topend"], "Topend Sports (Jackson-Pollock body density)")} '
    f'and in {ext(U["jp"], "Serra AJ, et al. ConScientiae Saúde 2009;8(1):19–24")}. Siri WE (1961): the body fat equation, '
    f'as printed by {ext(U["siri"], "Topend Sports (Siri equation)")}.',
    f'Gallagher D, et al. {ext(U["gallagher"], "Healthy percentage body fat ranges: an approach for developing guidelines based on body mass index")}. '
    'Am J Clin Nutr 2000;72:694–701, as '
    f'tabulated in {ext(U["jpha"], "J Public Health Afr 2016, Table 1")}.',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Adults aged 20 to 59 with a valid whole-body DXA scan in NHANES '
    '2011–2012 to 2017–2018, pregnant women excluded, weighted with CDC’s exam weights divided by four: the sample of the '
    '<a href="/body-fat-calculator/">body fat calculator</a>’s check. For each person we worked out both formulas from their '
    'measurements and each formula’s distance from the scan, in points and as a share of the scan’s reading (averaged, the '
    'average miss); we also worked out how far the two formulas landed from each other, and how much a 1-inch or 5-lb slip '
    'moves each formula with the person’s own height, waist and weight. Averages and shares are survey-weighted; each share '
    'quoted here has a 95% margin of error under 2 percentage points and each average miss under 0.4 (Taylor linearization '
    'over the survey’s 59 strata and 121 primary sampling units); medians use the weighted midpoint rule. '
    'Every figure is rounded once, from the unrounded value. The worked example and the tape and caliper slips are '
    'arithmetic on the published equations.</p></section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/body-fat-calculator/', 'Body fat calculator'), ('/lean-body-mass/', 'Lean body mass calculator'),
        ('/', 'BMI calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/body-fat-percentage-chart/', 'Body fat percentage chart'), ('/blog/body-fat-vs-bmi/', 'Body fat vs BMI'),
        ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'), ('/average-weight/', 'Average weight by height')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, takeaways, hero, toc, sec_steps, sec_acc, sec_scales, sec_measuring, sec_lab, sec_meaning, sec_faq, sec_src, sec_rel])
    + ' </div></main>')
assert 'style="' not in re.sub(r'(?s)<svg.*?</svg>', '', main)
assert all(f'id="{a}"' in main for a, _ in CHIPS) and '<article' not in main and 'bodyfatpercentagecalc' not in main
assert '—' not in plain(re.sub(r'(?s)<svg.*?</svg>', '', main)), 'an em dash in the body text'
assert 'digitalcommons.wku.edu' not in main                         # the old tape-method source (a conference abstract)

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD, nav
TITLE = 'How to Calculate Body Fat Percentage: Home Methods vs DXA'
DESC = ('How to calculate body fat percentage at home with a tape or calipers, step by step, and how close tested methods '
        'and body fat scales come to a DXA scan.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
OG_T = 'How to calculate body fat percentage: home methods against a DXA scan'
OG_D = ('The steps for each home method, and how close tested methods and body fat scales come to a DXA scan, from '
        'published studies and CDC’s scans of US adults.')
OG_ALT = ('Chart: seven body fat methods tested on the same people, each shown as its average difference from a DXA scan '
          'with its confidence interval, all to the left of zero.')
for s_ in (DESC, OG_T, OG_D, OG_ALT): assert '"' not in s_ and '—' not in s_
PREF = SITE + '/assets/images/preferred/how-to-measure-body-fat-'
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
assert 'twitter:title' not in src and 'twitter:description' not in src          # the G1 head had neither; add them
src = sub1(r'(<meta name="twitter:card" content="summary_large_image">)',
           f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{OG_T}">'
           f'<meta name="twitter:description" content="{OG_D}">', src)
n_style = len(re.findall(r'(?s)<style>.*?</style>', src)); assert n_style == 3, n_style   # the G1 page-level styles
src = re.sub(r'(?s)<style>.*?</style>', '', src)
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1 and '<style' not in src
# The menu marked "Obesity Statistics" as the current page (the G1 shell came from /us-obesity-statistics/); a guide marks
# Guides, in both menus (as /blog/healthy-bmi-range/ does).
OBS = '<a href="/us-obesity-statistics/" class="active" aria-current="page">Obesity Statistics</a>'
assert src.count(OBS) == 1
src = src.replace(OBS, '<a href="/us-obesity-statistics/">Obesity Statistics</a>')
GD = '<a href="/blog/">Guides</a>'
head_part = src[:src.index('<main')]
assert head_part.count(GD) == 2, head_part.count(GD)                              # desktop menu and mobile menu
src = head_part.replace(GD, '<a href="/blog/" class="active" aria-current="page">Guides</a>') + src[src.index('<main'):]

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 1, len(blocks)
old = json.loads(blocks[0].group(1))
assert [x['@type'] for x in old['@graph']] == ['Article', 'BreadcrumbList', 'Organization', 'Person']
art_old, crumbs = old['@graph'][0], old['@graph'][1]
assert art_old['datePublished'] == '2026-10-07' and art_old['@id'] == URL + '#article'
assert [i['name'] for i in crumbs['itemListElement']] == ['Home', 'Guides', H1]
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
ORG = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'CalculateMyBMI', 'url': SITE + '/'}
graph = [
    {'@type': 'Article', '@id': URL + '#article', 'headline': H1, 'description': DESC, 'url': URL,
     'datePublished': art_old['datePublished'], 'dateModified': '{TODAY}', 'inLanguage': 'en-US',
     'isPartOf': {'@type': 'WebSite', 'name': 'CalculateMyBMI', 'url': SITE + '/'}, 'author': PERSON, 'publisher': ORG,
     'image': [IMG11, IMG43, IMG16],
     'mainEntityOfPage': {'@type': 'WebPage', '@id': URL, 'url': URL,
                          'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}},
     'citation': [U['burns'], U['foulis'], U['lahav'], U['frija'], U['bix'], U['dxx'], U['rfm'], U['deur']]},
    crumbs,
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}}
                                       for q, a in FAQ]},
]
ld = {'@context': 'https://schema.org', '@graph': graph}
src = src[:blocks[0].start()] + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' + src[blocks[0].end():]
assert src.count('{TODAY}') == 1

# ---------------------------------------------------------------- body
i, j = src.index('<main'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('og-how-to-measure-body-fat.png') == 0
open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'blog/how-to-measure-body-fat/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, '
      f'{len(FAQ)} FAQ, {len(TEXTS)} SVG labels checked; example {answers}; RFM miss {f1(MAE["rfm"])} points ({rfm_all}%), '
      f'BMI formula {f1(MAE["deur"])} ({deur_all}%)')
