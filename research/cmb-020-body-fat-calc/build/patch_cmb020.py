#!/usr/bin/env python3
"""CMB-020 registry, page map, DESIGN.md, the image gate and styles.css for /body-fat-calculator/ (sources re-read in
chat 2026-10-28). usage: patch_cmb020.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'body-fat-calculator'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2011-2018-dxa', 'gallagher-2000-bf-ranges', 'body-fat-method-validation')   # body-fat-equations has it
TOPEND = 'https://www.topendsports.com/testing/density-jackson-pollock.htm'

NOTES = {
    'body-fat-equations': ('notes',
        ' CMB-020 (2026-10-28): Serra 2009 re-read: JP7 men D = 1.112 - 0.00043499 S + 0.00000055 S^2 - 0.00028826 age, '
        'women D = 1.0970 - 0.00046971 S + 0.00000056 S^2 - 0.00012828 age (seven sites: subscapular, suprailiac, '
        'midaxillary, pectoral, triceps, abdominal, thigh); JP3 sites men thigh, pectoral, abdominal, women triceps, thigh, '
        'suprailiac. Deurenberg abstract re-read (research.vu.nl): 1,229 subjects (521 men, 708 women), ages 7-83, BMI '
        '13.9-40.9, densitometry; children 15 and under 1.51 x BMI - 0.70 x age - 3.6 x sex + 1.4 (SEE 4.4); adults SEE 4.1, '
        'R2 0.79; "slightly overestimated" body fat in obese subjects; error comparable to skinfolds and impedance. '
        '/body-fat-calculator/ rebuilt with four methods: Navy, relative fat mass (rfm-woolcott-2018), Deurenberg, JP3/JP7. '
        'Topend Sports (Robert Wood, read 2026-10-28; endpoint) prints all four JP equations as the page does, the women\'s '
        '3-site age term 0.0001392, citing Jackson & Pollock 1978 and Jackson, Pollock & Ward 1980; Serra 2009 prints that '
        'term as 0.0001395 (fact-check CMB-020: under 0.02 points at any age 18-79). The page cites Topend for the '
        'coefficients and names Serra\'s variant.'),
    'body-fat-method-validation': ('notes',
        ' CMB-020 (PMC6426203 re-read 2026-10-28): the skinfold method is a seven-site assessment (chest, midaxillary, '
        'triceps, subscapular, abdomen, suprailiac, thigh; Lange caliper, right side, two rotating measurements and a third '
        'if they differ by more than 2 mm; Siri; the equation is not named, the paper cites Jackson and Pollock 1978 and '
        'Jackson, Pollock and Ward 1980); N = 437 (301 women, 136 men), mean age 19.2; skinfolds mean difference from DXA '
        '1.4% (90% CI 1.1-1.7, Table 3); title "Measurement agreement in percent body fat estimates among laboratory and '
        'field assessments in college students: Use of equivalence testing". Table 3 column "Mean Difference '
        '(DXA–Surrogate; % Body Fat)": skinfolds +1.4, so they read 1.4 points below DXA on average (a signed mean, not a '
        'typical miss: the page says "read 1.4 points below" and gives the MAPE, 11.7%, as the average miss); MAPE lowest of '
        'the seven methods, hydrostatic weighing the smallest mean difference (1.0); "Trained graduate students performed the '
        'skinfolds thickness measurements".'),
    'nhanes-2011-2018-dxa': ('notes',
        ' CMB-020: /body-fat-calculator/ checks two body fat formulas on these scans (research/body-fat-calculator-build/'
        'bfc_stats.py, its sample asserted equal to bfpc_stats.json: 10,864 adults 20-59, means 38.71 / 27.24): relative fat '
        'mass (5,388 women / 5,363 men with a measured waist) within 5 points of the scan 74.3% / 86.3%, typical miss 3.54 / '
        '2.73, mean error +2.33 [2.15, 2.52] / +0.74 [0.60, 0.89], median error +2.32 / +0.81; Deurenberg (5,446 / 5,383 '
        'with a BMI) within 5 points 62.4% / 66.4%, typical miss 4.67 / 4.21, mean error -0.19 [-0.47, 0.09] / -0.13 '
        '[-0.35, 0.10] (both include 0), at a healthy BMI -3.06 / -2.90, with obesity +4.11 / +2.88, ages 20-39 -2.20 / '
        '-2.30, 40-59 +1.68 / +2.14; same people (5,386 / 5,361): RFM within 5 points for 12.0 [9.7, 14.3] more women in '
        '100 and 19.9 [18.1, 21.7] more men, typical miss 1.12 [0.97, 1.27] / 1.47 [1.36, 1.59] points less; within 3 points '
        'RFM 49.9 / 61.5, Deurenberg 41.5 / 44.3; RFM median error with a Woodruff 95% CI +2.32 [2.11, 2.53] / +0.81 [0.63, '
        '1.03]; calibration windows (estimate within a point of each whole percent, 30 or more people) feed the calculator. '
        'Exact ties: BMI and DXDTOPF are recorded to 0.1 and age in whole years, so a Deurenberg estimate and its error are '
        'exact hundredths (rounded so, after an independent fact-check found float noise deciding 39 ties); BMXHT carries '
        '0.01 cm for 12 people in 2013-2014. Percentiles: the weighted midpoint rule over distinct values (bfpc_stats.py '
        'applies it reading by reading after an unstable sort, so tied readings\' order moves up to 5 of its 50 tool '
        'quartiles by 0.1 when printed; the two agree within 0.08). BMX_J documentation: "The body measures data were '
        'collected, in the Mobile Examination Center (MEC), by trained health technicians."'),
}

NEW = [
    {'domain': 'rfm-woolcott-2018',
     'source': ('Woolcott OO, Bergman RN. Relative fat mass (RFM) as a new estimator of whole-body fat percentage - A '
                'cross-sectional study in American adult individuals. Sci Rep 2018;8:10980'),
     'publisher': 'Scientific Reports (Nature Portfolio); Cedars-Sinai',
     'url': 'https://doi.org/10.1038/s41598-018-29362-1',
     'endpoint': ('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6054651/ ; '
                  'https://www.cedars-sinai.org/stories-and-insights/healthy-living/relative-fat-mass'),
     'access': 'page', 'license': 'Open access article; equation and facts cited with attribution', 'tier': 'A',
     'cadence': 'static', 'granularity': 'equation; validation statistics', 'format': 'article', 'key_required': 'no',
     'attribution': 'Formula: Woolcott and Bergman, Sci Rep 2018',
     'verified_date': '2026-10-28', 'next_check': '2027-10-28',
     'coverage': 'RFM = 64 - 20 x height / waist + 12 x sex (sex 0 men, 1 women); adults 20 and over',
     'sample_note': ('Read 2026-10-28 (link.springer.com/10.1038/s41598-018-29362-1): the equation; waist "at the level of '
                     'the uppermost lateral border of the right ilium", horizontal plane; height by electronic '
                     'stadiometer; development NHANES 1999-2004 (n = 12,581, ages 20-85), validation 2005-2006 (n = 3,456, '
                     'ages 20-69); DXA "Hologic QDR 4500A fan-beam densitometer"; validation median bias women 0.9% (95% CI '
                     '0.6-1.1), men 0.5% (0.3-0.8, Table 2); bias "the median difference between estimated and measured body '
                     'fat percentage". Cedars-Sinai (the authors\' center): "put the tape measure at the top of your hip '
                     'bone"; men 64 - (20 x height/waist), women 76 - (20 x height/waist).'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-020: checked on CDC NHANES 2011-2018 DXA (Hologic Discovery A), see nhanes-2011-2018-dxa notes: within '
               '5 points 74.3% of women, 86.3% of men; reads high (+2.33 / +0.74 on average). Median error +2.32 [2.11, 2.53] '
               'for women, clearly above the authors\' 0.9 [0.6, 1.1]; men +0.81 [0.63, 1.03], not clearly different from '
               '0.5 [0.3, 0.8]; scanner and ages (20-69 there, 20-59 here) also differ, so the page names no cause.')},
    {'domain': 'foulis-2023-circumference-dxa',
     'source': ('Foulis SA, Friedl KE, Spiering BA, Walker LA, Guerriere KI, Pecorelli VP, Zeppetelli DJ, Reynoso MC, '
                'Taylor KM, Hughes JM. Body composition changes during 8 weeks of military training are not accurately '
                'captured by circumference-based assessments. Front Physiol 2023;14:1183836'),
     'publisher': 'Frontiers in Physiology',
     'url': 'https://doi.org/10.3389/fphys.2023.1183836',
     'endpoint': 'https://public-pages-files-2025.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1183836/text',
     'access': 'page', 'license': 'Open access article; facts cited with attribution', 'tier': 'A', 'cadence': 'static',
     'granularity': 'method-level agreement statistics', 'format': 'article', 'key_required': 'no',
     'attribution': 'Foulis et al., Front Physiol 2023',
     'verified_date': '2026-10-28', 'next_check': '2027-10-28',
     'coverage': ('US Army basic combat training recruits, 481 women and 926 men: the circumference method (Navy 1984 '
                  'equations) against DXA before and after 8 weeks'),
     'sample_note': ('Abstract read 2026-10-28: before training, circumference vs DXA mean errors "-6.0%±4.4% for women and '
                     '-6.0%±3.5% for men (both p<0.01)"; "Circumference measures underestimated changes in %BF during BCT '
                     'in men and did not detect changes in women." Text (PDF): "Current circumference-based methodology for '
                     'measuring body composition in the U.S. Army was developed by the Navy in 1984" (Hodgdon and Beckett); '
                     'men neck and abdomen at the umbilicus, women neck, the narrowest part of the torso and the widest part '
                     'of the buttocks; after training mean errors -2.0% ± 3.9% (women) and -4.9% ± 3.5% (men).'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-020: the tape method\'s DXA check on /body-fat-calculator/ (NHANES measured no neck). Young recruits; '
               'the page says both studies were of young adults and neither covered older ages.')},
    {'domain': 'army-tape-worksheets',
     'source': ('US Army DA Form 5500, Body Fat Content Worksheet (Male), and DA Form 5501, Body Fat Content Worksheet '
                '(Female), May 2013 editions'),
     'publisher': 'US Army',
     'url': 'https://home.army.mil/stewart/index.php/download_file/force/6943/434',
     'endpoint': 'https://home.army.mil/stewart/index.php/download_file/force/6944/434',
     'access': 'document', 'license': 'Public domain (US federal work)', 'tier': 'A',
     'cadence': 'revised editions exist (DA 5500 JUN 2023)', 'granularity': 'measurement procedure', 'format': 'PDF',
     'key_required': 'no', 'attribution': 'US Army DA Forms 5500 and 5501',
     'verified_date': '2026-10-28', 'next_check': '2027-10-28',
     'coverage': 'where and how to measure for the tape method: neck, abdomen (men), waist and hips (women)',
     'sample_note': ('Read 2026-10-28: "Measure neck just below level of larynx (Adam\'s apple)", round up to the nearest '
                     '0.50 inch; men "Measure abdomen at the level of the navel (belly button.)", round down; women "Measure '
                     'waist (abdomen) at the point of minimal abdominal circumference" and "Measure hips at point where the '
                     'gluteus muscles (buttocks) protrude backward the most", both rounded down; each "Repeat three times, '
                     'then average to the nearest 0.50 inch." A JUN 2023 DA 5500 (csu.edu ROTC copy) gives the same neck and '
                     'abdomen instructions.'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-020: where to measure for the tape method on /body-fat-calculator/ (the page says "the Army\'s 2013 '
               'worksheets"). Army.mil 2023-06-12, https://www.army.mil/article/267486 : Army Directive 2023-11 "requires '
               'tape testing at only one site on the body"; the multi-site method stays authorized for 12 months as a '
               'confirmation; the page names the change in one sentence. Army standards and the 2023 one-site equation '
               'belong to the planned /army-body-fat-calculator/ (ledger owner).')},
]

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    linked, noted = set(), set()
    have = {r[ix['domain']] for r in rows[1:]}
    assert not have & {n['domain'] for n in NEW}, 'rows already there'
    for r in rows[1:]:
        d = r[ix['domain']]
        if d in USED:
            ps = [x.strip() for x in r[ix['pages_served']].split(';') if x.strip()]
            assert SLUG not in ps, d
            ps.append(SLUG); r[ix['pages_served']] = ';'.join(ps); linked.add(d)
        if d in NOTES:
            col, txt = NOTES[d]
            assert txt.strip() not in r[ix[col]], d
            r[ix[col]] += txt; noted.add(d)
        if d == 'body-fat-equations':
            assert SLUG in r[ix['pages_served']].split(';')
            assert TOPEND not in r[ix['endpoint']]
            r[ix['endpoint']] += ' ; ' + TOPEND
    assert linked == set(USED), set(USED) - linked
    assert noted == set(NOTES), set(NOTES) - noted
    for n in NEW:
        assert set(n) == set(head), set(head) ^ set(n)
        rows.append([n[k] for k in head])
    return rows

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    hit = 0
    for r in rows[1:]:
        if r[ix['slug']] == SLUG:
            hit += 1
            assert r[ix['data_source']] == 'body-fat-equations'
            r[ix['wedge']] = ('Four methods (Navy tape, relative fat mass, Deurenberg BMI formula, Jackson-Pollock 3- and '
                              '7-site skinfolds) and how close each gets to DXA: relative fat mass and Deurenberg checked on '
                              'CDC NHANES 2011-2018 DXA scans (our calculation; within 5 points 74%/86% vs 62%/66% of '
                              'women/men; what the scans read for any estimate), tape and calipers from published DXA '
                              'comparisons (Foulis 2023, Burns 2019); result on the provisional ranges and among US adults '
                              '(built CMB-020)')
            r[ix['status']] = 'built'
            r[ix['notes']] = ('Google already cites /blog/body-fat-vs-bmi for body-fat queries (AI features). D-14 rebuild '
                              'CMB-020 (research/body-fat-calculator-build/); also cites nhanes-2011-2018-dxa, '
                              'rfm-woolcott-2018, foulis-2023-circumference-dxa, army-tape-worksheets, '
                              'body-fat-method-validation and gallagher-2000-bf-ranges. Owns "body fat calculator" (74k) and '
                              '328 more keywords, 147,710/mo; Army and Navy standards queries belong to the planned army- and '
                              'navy-body-fat-calculator pages. D-15: no link to bodyfatpercentagecalc.com')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: the body fat calculator.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'Body fat calculator (CMB-020)' not in d
d = d.replace(anchor, (
    '### Body fat calculator (CMB-020)\n'
    '- `/body-fat-calculator/` estimates body fat four ways with the shared calculator parts and no page-level style: '
    '`.calculator-card.bfc` › `.calc-panel` › `.bfc-toggles` (two `.unit-toggle`s side by side, Woman / Man and US / '
    'Metric, stacked under 360 px) › a four-way `.unit-toggle.unit-toggle--methods` (Tape measure, Waist and height, '
    'Height and weight, Calipers; two rows on phones) › `.form-row.form-row--pair` rows for the height and for weight and '
    'age › one `.bfc-pane` per method (`.form-row.form-row--trio` puts three measurements in a row, two under 360 px; a '
    '`.form-hint` says where to measure; calipers add a 3 sites / 7 sites toggle) › `.calculate-btn`. Panes and rows hide '
    'with the `hidden` attribute (`.bfc [hidden]`).\n'
    '- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the provisional range (neutral '
    'under 20) with the estimate in a neutral `.bmi-value`, then `.er-section`s with `h2` headings (the card sits under the '
    'H1): how close the estimate is likely to be (for relative fat mass and the Deurenberg formula, the middle half and '
    'median of CDC\'s scans in people whose formula gave an estimate within a point of the same whole percent; for the tape '
    'and calipers, the published DXA comparison), where the estimate falls (the CMB-016 figure and notes), fat and lean '
    'mass when a weight is entered, the other estimates the entered numbers allow (an `.er-table`, the method shown above '
    'as `.er-active` with an `.er-you` pill), and the source line.\n'
    '- Every result comes from the printed estimate (0.1, halves up): its range, its US share, its calibration window and '
    'the fat mass. A method pane\'s starting values belong to the worked example, so a pane joins "Your other estimates" '
    'only after the user types in it; the height-and-weight formula joins whenever a weight is entered.\n'
    '- The notes say what each check can and can\'t tell: trained technicians took CDC\'s measurements (measuring yourself '
    'adds error), and the US share and the range treat the estimate as a scan reading, so they are only as close as it.\n'
    '- The US / Metric switch converts every length and the weight to 0.1; switching back with nothing retyped restores '
    'the numbers as they were, so flipping units never changes a result.\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/average-weight/': 'average-weight'}"
assert c.count(old) == 1
c = c.replace(old, "             '/average-weight/': 'average-weight',\n"
                   "             '/body-fat-calculator/': 'body-fat-calculator'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)

# styles.css: the calculator takes the body fat rank tool's sizes, plus its own layout rules (no page-level style).
sp = os.path.join(ROOT, 'assets/css/styles.css'); st = open(sp, encoding='utf-8', newline='').read()
for old, new in (('.bfr .bmi-value, .awt .bmi-value { font-size: 3rem; }',
                  '.bfr .bmi-value, .awt .bmi-value, .bfc .bmi-value { font-size: 3rem; }'),
                 ('.bfr .bmi-category, .awt .bmi-category { font-size: 1.0625rem; line-height: 1.4; }',
                  '.bfr .bmi-category, .awt .bmi-category, .bfc .bmi-category { font-size: 1.0625rem; line-height: 1.4; }'),
                 ('.bfr .er-section svg, .awt .er-section svg { display: block;',
                  '.bfr .er-section svg, .awt .er-section svg, .bfc .er-section svg { display: block;')):
    assert st.count(old) == 1, old
    st = st.replace(old, new)
assert '.bfc [hidden]' not in st and 'form-row--trio' not in st and 'unit-toggle--methods' not in st
st = st.rstrip('\n') + '\n' + (
    '\n/* CMB-020 — /body-fat-calculator/ (DESIGN.md "Body fat calculator (CMB-020)"): the sex and units toggles share a row\n'
    '   (stacked under 360 px), the four-way method toggle wraps to two rows on phones, three measurements share a row (two\n'
    '   under 360 px), panes and rows hidden with the hidden attribute stay hidden (.form-row sets display: grid), and a table\n'
    '   heading row that spans the columns keeps 8 px beside its text on its grey ground. */\n'
    '.bfc [hidden] { display: none; }\n'
    '.bfc-toggles { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }\n'
    '.unit-toggle--methods { flex-wrap: wrap; gap: 4px; }\n'
    '.form-row.form-row--trio { grid-template-columns: repeat(3, minmax(0, 1fr)); }\n'
    '.bfc .form-hint { margin: 0.375rem 0 0; }\n'
    '@media (max-width: 600px) { .unit-toggle--methods .unit-btn { flex: 1 1 calc(50% - 2px); padding: 0.5rem; } '
    '.bfc-toggles .unit-btn { padding: 0.5rem; } .flow .data-table--fit th[colspan] { padding: 0.5rem; } }\n'
    '@media (max-width: 359px) { .bfc-toggles { grid-template-columns: 1fr; gap: 0; } '
    '.form-row.form-row--trio { grid-template-columns: repeat(2, minmax(0, 1fr)); } }\n')
open(sp, 'w', encoding='utf-8', newline='').write(st)
# The body fat chart's rank tool figure moves its marks 2 units down (edits.json changes the page); its generator, the
# page's build record, gets the same change so a rerun gives the same page.
import json
E = [e for e in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edits.json'), encoding='utf-8'))
     if e['file'] == 'body-fat-percentage-chart/index.html']
assert len(E) == 1
gp = os.path.join(ROOT, 'research/body-fat-chart-build/gen_bfpc.py'); g = open(gp, encoding='utf-8', newline='').read()
assert g.count(E[0]['old']) == 1
open(gp, 'w', encoding='utf-8', newline='').write(g.replace(E[0]['old'], E[0]['new']))
print('patched: registry', len(USED), 'rows linked,', len(NOTES), 'noted,', len(NEW), 'new; page map; DESIGN.md; '
      'check_images PREFERRED; styles.css .bfc')
