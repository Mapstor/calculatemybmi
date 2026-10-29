#!/usr/bin/env python3
"""CMB-021 registry, page map, the image gate, DESIGN.md and styles.css for /blog/how-to-measure-body-fat/ (sources read
in chat 2026-10-29).
usage: patch_cmb021.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'blog/how-to-measure-body-fat'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

# The page also cites these rows (body-fat-method-validation already lists it).
USED = ('nhanes-2011-2018-dxa', 'rfm-woolcott-2018', 'foulis-2023-circumference-dxa', 'army-tape-worksheets',
        'body-fat-equations', 'gallagher-2000-bf-ranges')

NOTES = {
    'body-fat-method-validation': ('notes',
        ' CMB-021 (PMC6426203 re-read 2026-10-29): Table 3 "Agreement in percent body fat estimates compared to '
        'dual-emission X-ray absorptiometry", all seven rows (DXA minus method in points, 90% CI, MAPE): hydrostatic '
        'weighing 1.0 (0.6-1.4) 13.4%; skinfold thickness 1.4 (1.1-1.7) 11.7%; ADP 1.6 (1.3-1.9) 14.5%; IR 4.2 (3.7-4.7) '
        '18.7%; Omron BIA 4.9 (4.5-5.3) 21.9%; Tanita BIA 3.5 (3.0-4.0) 17.2%; Valhalla BIA 1.6 (1.1-2.1) 17.0%. 10% '
        'equivalence interval -2.7 to 2.7 ("+/- 10% of the criterion mean, which corresponded to +/- 2.7% body fat"): '
        'hydrostatic weighing, skinfolds, ADP and Valhalla BIA equivalent; at 15% "all surrogate assessments, except for '
        'Omron BIA and IR". Table 1: DXA 27.0% (SD 7.6) overall (its women and men rows, 28.2 and 20.8, do not average to '
        'it with 301 and 136: not used). Table 4: "differences between DXA and each surrogate assessment increased as mean '
        'percent body fat increased", all but Valhalla BIA (r = 0.04, p = 0.784). Devices: DXA Hologic Discovery W '
        '(software 12.1); BOD POD (COSMED), seated, two volume measurements; Futrex-6100 A/ZL light wand on the belly of the '
        'biceps; OMRON HBF-306 handheld, arms extended; Tanita BF-556 two-electrode foot-to-foot scale; Valhalla Scientific '
        'Model 1990B, four electrodes on the right hand and foot, supine; hydrostatic weighing on an underwater swing after '
        'full exhalation. Pre-test: large meals avoided 2 hours, vigorous exercise 12 hours, alcohol 48 hours, liquids '
        'limited to 2 glasses of water at least 2 hours before, bladder emptied immediately before; "dehydration can lead '
        'to overestimation of percent body fat", "overhydration can lead to underestimation". Machine-readable copy: '
        'research/how-to-measure-body-fat-build/burns_2019_table3.json. The endpoint (a WKU conference abstract on the '
        'military tape method) is no longer cited by /blog/how-to-measure-body-fat/: Foulis 2023 '
        '(foulis-2023-circumference-dxa) replaces it.'),
    'nhanes-2011-2018-dxa': ('notes',
        ' CMB-021: /blog/how-to-measure-body-fat/ (research/how-to-measure-body-fat-build/htm_stats.py, its sample and '
        'shares asserted equal to bfc_stats.json): average miss in points (mean |formula - scan|) relative fat mass 3.13 '
        '[3.05, 3.21], Deurenberg 4.44 [4.35, 4.53]; as a share of the scan (MAPE, the unit of Burns et al. 2019) relative '
        'fat mass 10.37 [10.05, 10.70] (women 9.92, men 10.82; ages 20-29 10.74), Deurenberg 13.97 [13.64, 14.29] (women '
        '12.03, men 15.88; ages 20-29 16.94); the average scan reads 32.94% [32.64, 33.25] (Burns\'s students 27.0%), so '
        'MAPE here can\'t be set against Burns\'s (CMB-021 fact-check; the page says so and gives the points); in the same people (5,386 women / 5,361 men) the two formulas '
        'more than 5 points apart 38.3% [36.4, 40.2] / 15.3% [14.0, 16.6], median distance 4.08 / 2.43 points, relative fat '
        'mass the higher 76.5% / 63.8%; a measuring slip worked from each person\'s own height, waist and weight (weighted '
        'median): 1 inch on the waist moves relative fat mass +0.92 / +0.90 points, 5 lb on the scale moves Deurenberg '
        '+1.03 / +0.88, a height entered 1 inch short +1.06 / +0.99. DXX_J re-read 2026-10-29: DXA "is the most widely '
        'accepted method of measuring body composition" "due in part to its speed, ease of use, and low radiation '
        'exposure"; "extremely low at less than 20 uSv"; "The NHANES BCA option was enabled for whole body scan analysis, '
        'this option adds 5% of lean mass to the fat mass."'),
}

NEW = [
    {'domain': 'frija-masson-2021-smart-scales',
     'source': ('Frija-Masson J, Mullaert J, Vidal-Petiot E, Pons-Kerjean N, Flamant M, d\'Ortho M-P. Accuracy of Smart '
                'Scales on Weight and Body Composition: Observational Study. JMIR Mhealth Uhealth 2021;9(4):e22487'),
     'publisher': 'JMIR mHealth and uHealth (JMIR Publications)',
     'url': 'https://doi.org/10.2196/22487',
     'endpoint': 'https://mhealth.jmir.org/2021/4/e22487',
     'access': 'page', 'license': 'Open access article; facts cited with attribution', 'tier': 'A', 'cadence': 'static',
     'granularity': 'device-level agreement statistics', 'format': 'article', 'key_required': 'no',
     'attribution': 'Frija-Masson et al., JMIR Mhealth Uhealth 2021',
     'verified_date': '2026-10-29', 'next_check': '2027-10-29',
     'coverage': ('Three smart scales (Tefal Body Partner, Terraillon DietPack, Withings Body Cardio) against DXA (Lunar '
                  'iDXA) in 53, 52 and 48 adult patients referred for a scan at Bichat hospital, Paris'),
     'sample_note': ('Read 2026-10-29 (mhealth.jmir.org/2021/4/e22487): consecutive patients evaluated by DEXA in the '
                     'physiology unit of a French tertiary hospital, each weighed on one smart scale immediately after '
                     'DEXA; referrals mainly for obesity or chronic conditions affecting body composition. Median absolute '
                     'error, body weight 0.3 kg (IQR -0.1, 0.7), 0 kg (-0.4, 0.3), 0.25 kg (-0.10, 0.52); fat mass -2.2 kg '
                     '(-5.8, 1.3), -4.4 kg (-6.6, 0), -3.7 kg (-8.0, 0.28). "Body fat was globally underestimated in all 3 '
                     'scales." Conclusion: "Smart scales are not accurate for body composition and should not replace '
                     'DEXA in patient care." The abstract\'s muscle-mass errors repeat the fat-mass figures (the Results '
                     'give other values); no page uses muscle mass.'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-021: smart scales on /blog/how-to-measure-body-fat/ (takeaways, accuracy list, scales section, FAQ). '
               'The paper\'s "absolute error" is the signed scale-minus-DXA difference in kg (negative = read low), not a '
               'magnitude: the page gives the median weight differences (0.3, 0 and 0.25 kg) and says the scales read fat '
               'mass "2.2 to 4.4 kg low" (the CMB-021 fact-check: "within 0.3 kg" would read as a bound; one scale\'s upper '
               'quartile was 0.7 kg).')},
    {'domain': 'lahav-2021-inbody-seca',
     'source': ('Lahav Y, Goldstein N, Gepner Y. Comparison of body composition assessment across body mass index '
                'categories by two multifrequency bioelectrical impedance analysis devices and dual-energy X-ray '
                'absorptiometry in clinical settings. Eur J Clin Nutr 2021;75(8):1275-1282'),
     'publisher': 'European Journal of Clinical Nutrition (Springer Nature)',
     'url': 'https://doi.org/10.1038/s41430-020-00839-5',
     'endpoint': 'https://pubmed.ncbi.nlm.nih.gov/33483630/',
     'access': 'page', 'license': 'Abstract facts cited with attribution', 'tier': 'A', 'cadence': 'static',
     'granularity': 'device-level agreement statistics', 'format': 'article', 'key_required': 'no',
     'attribution': 'Lahav et al., Eur J Clin Nutr 2021',
     'verified_date': '2026-10-29', 'next_check': '2027-10-29',
     'coverage': ('InBody 770 and SECA mBCA 515 (multifrequency impedance, standing, eight electrodes) against DXA in 226 '
                  'adults, 51% men, 18-80 years, BMI 18-56'),
     'sample_note': ('PubMed abstract read 2026-10-29: "Measurements were performed in a random order, after a 3 h fast '
                     'and no prior exercise."; Lin\'s concordance InBody 0.922, SECA 0.940; "with 95% limits of '
                     'agreements between 2.6 and -8.9, and 7.1 and -7.6, respectively"; "BF% assessment by SECA was '
                     'similar to DXA (-0.3%, p = 0.267), and underestimated by InBody (-3.1%, p < 0.0001)."; "InBody '
                     'deviations were largest among normal weight people and decreased with increasing BMI group, while '
                     'SECA measurements remained unaffected." The DXA model is not in the abstract.'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-021: InBody 770 and SECA on /blog/how-to-measure-body-fat/ (accuracy list, FAQ "How accurate is '
               'InBody?"). The page reads the limits of agreement as the range that held about 95% of the differences '
               '(device minus DXA): from 2.6 points above to 8.9 below for InBody.')},
    {'domain': 'nhanes-bia-documentation',
     'source': 'CDC NHANES 2003-2004 Bioelectrical Impedance Analysis (BIX_C) data documentation',
     'publisher': 'CDC National Center for Health Statistics',
     'url': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/BIX_C.htm',
     'endpoint': '',
     'access': 'page', 'license': 'Public domain (US federal work)', 'tier': 'A', 'cadence': 'static',
     'granularity': 'method documentation', 'format': 'HTML', 'key_required': 'no',
     'attribution': 'Source: CDC National Center for Health Statistics, NHANES 2003-2004 bioelectrical impedance documentation',
     'verified_date': '2026-10-29', 'next_check': '2027-10-29',
     'coverage': ('How NHANES measured impedance (HYDRA ECF/ICF Bio-Impedance Spectrum Analyzer Model 4200, right hand '
                  'and foot, participants aged 8-49), how fat-free mass, fat mass and percent fat follow from it, and '
                  'who was not examined'),
     'sample_note': ('Read 2026-10-29: "A small alternating current was passed through surface electrodes placed on the '
                     'right hand and foot"; "The voltage drop between electrodes provided a measure of impedance, or '
                     'opposition to the flow of the electric current."; "Fat mass (FM) was calculated by subtracting FFM by '
                     'impedance from the participants\' measured weight."; "the prediction of fat-free mass with impedance '
                     'is a second order estimation subject to error"; "Estimation of percent fat is third order and subject '
                     'to additional error."; not examined: "Pregnant females", "Amputations other than fingers or toes", '
                     '"Artificial joints, pins, plates, or other types of metal objects in the body", "Pacemaker or '
                     'automatic defibrillator", "Coronary stents or metal suture material in the heart", "Weight over 300 '
                     'pounds"; "A 6-hour fast is recommended by the manufacturer".'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-021: how an impedance test works on /blog/how-to-measure-body-fat/ (scales section, FAQ "How do scales '
               'measure body fat?"). The page attributes the method and the exclusions to CDC\'s own test; it makes no '
               'claim about any scale maker\'s equation or warnings.')},
]

SIRI = 'https://www.topendsports.com/testing/siri-equation.htm'
SIRI_NOTE = (' CMB-021 (2026-10-29): Topend Sports\' Siri page (Robert Wood; endpoint) prints "% Body Fat = (495 / Body '
             'Density) - 450", citing Siri WE (1961) in Brozek & Henschel (eds), Techniques for measuring body composition, pp. '
             '223-244; its Jackson-Pollock page prints only the density '
             'equations (fact-check). /blog/how-to-measure-body-fat/ links each; /body-fat-calculator/ still cites "Siri WE, '
             '1956" next to the Jackson-Pollock page (DEVLOG §5).')

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
        if d == 'body-fat-method-validation':
            assert SLUG in r[ix['pages_served']].split(';')
        if d == 'body-fat-equations':
            assert SIRI not in r[ix['endpoint']] and SIRI_NOTE.strip() not in r[ix['notes']]
            r[ix['endpoint']] += ' ; ' + SIRI; r[ix['notes']] += SIRI_NOTE
        if d in NOTES:
            col, txt = NOTES[d]
            assert txt.strip() not in r[ix[col]], d
            r[ix[col]] += txt; noted.add(d)
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
            assert r[ix['data_source']] == 'body-fat-method-validation'
            assert r[ix['wedge']] == 'Every method scored against DXA using published validation studies'
            r[ix['wedge']] = ('The steps for each home method (relative fat mass, Navy tape, Deurenberg BMI formula, '
                              'Jackson-Pollock 3-site calipers) worked by hand for one example man, then how close each '
                              'method gets to DXA: all seven methods of Burns 2019 Table 3 on the same 437 students (every '
                              'one read low; average miss 11.7-21.9%), the two home formulas on CDC NHANES 2011-2018 DXA in '
                              'the same unit (our calculation: 10.4% and 14.0%), the formulas more than 5 points apart for '
                              '38% of women and 15% of men, how much a measuring slip moves each estimate (about 1 to 2 '
                              'points), smart scales (Frija-Masson 2021), InBody and SECA (Lahav 2021), the tape method '
                              '(Foulis 2023) (built CMB-021)')
            r[ix['notes']] = ('Built 7 Oct 2026 (G1); D-14 rebuild CMB-021 (research/how-to-measure-body-fat-build/); '
                              'also cites nhanes-2011-2018-dxa, rfm-woolcott-2018, foulis-2023-circumference-dxa, '
                              'army-tape-worksheets, body-fat-equations, gallagher-2000-bf-ranges, '
                              'frija-masson-2021-smart-scales, lahav-2021-inbody-seca and nhanes-bia-documentation. Owns '
                              '"how to calculate body fat percentage" (18.1k) and 912 more keywords, 114,170/mo; '
                              'calculator queries belong to /body-fat-calculator/, ranges by age to '
                              '/body-fat-percentage-chart/.')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/body-fat-calculator/': 'body-fat-calculator'}"
assert c.count(old) == 1
c = c.replace(old, "             '/body-fat-calculator/': 'body-fat-calculator',\n"
                   "             '/blog/how-to-measure-body-fat/': 'how-to-measure-body-fat'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)
# DESIGN.md: tables whose row labels are names of several words.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'data-table--wrap' not in d
d = d.replace(anchor, (
    '### Tables with long row labels (CMB-021)\n'
    '- `.data-table--wrap` lets a table\'s row labels (`th[scope="row"]`, which `.flow` tables keep on one line) wrap. Use it '
    'with `.data-table--fit` where the labels are names of several words (methods, measuring slips), so a three-column '
    'table fits a 320 px phone; numbers stay on one line.\n'
    '- Groups inside such a table are `tbody` elements, each led by a `th[scope="rowgroup"][colspan]` row '
    '(`/blog/how-to-measure-body-fat/`, the measuring-slip table).\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)

# styles.css: the row labels of .data-table--wrap tables wrap (no page-level style).
sp = os.path.join(ROOT, 'assets/css/styles.css'); st = open(sp, encoding='utf-8', newline='').read()
assert 'data-table--wrap' not in st and st.count('.flow .data-table th[scope="row"] { background: transparent; color: var(--gray-800); white-space: nowrap; }') == 1
st = st.rstrip('\n') + '\n' + (
    '\n/* CMB-021 — /blog/how-to-measure-body-fat/ (DESIGN.md "Tables with long row labels (CMB-021)"): row labels that are\n'
    '   names of several words wrap, so a three-column table fits a 320 px phone; numbers stay on one line (.data-table--fit). */\n'
    '.flow .data-table--wrap th[scope="row"] { white-space: normal; }\n')
open(sp, 'w', encoding='utf-8', newline='').write(st)
print('patched: registry', len(USED), 'rows linked,', len(NOTES), 'noted,', len(NEW), 'new; page map; check_images PREFERRED; '
      'DESIGN.md; styles.css .data-table--wrap')
