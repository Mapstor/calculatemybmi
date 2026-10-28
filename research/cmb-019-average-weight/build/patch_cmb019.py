#!/usr/bin/env python3
"""CMB-019 registry, page map, DESIGN.md and the image gate for /average-weight/ (sources re-read in chat 2026-10-22).
usage: patch_cmb019.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'average-weight'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2021-2023-exam-files', 'nhanes-anthropometric-reference', 'cdc-adult-bmi-categories',
        'nhlbi-1998-obesity-guidelines')

NOTES = {
    'nhanes-2021-2023-exam-files': ('sample_note',
        '. CMB-019 (2026-10-22): research/average-weight/compute.py reproduces NCHS Series 3 No. 50 exactly (Table 4 in '
        'full, the adult rows of Tables 8 and 12, the adult BMI mean and median of Table 10: 204 values; lb = kg x 2.2046, '
        'the NCHS factor; percentiles over the weighted distribution of distinct measured values; heights keep pregnant '
        'women, as Table 8 does), so the women\'s 95th percentile is now 262.7 lb too; the CMB-019 fact-check reproduced '
        'all 478 means and percentiles of Tables 4, 8 and 12 with the same method. By measured height (nearest inch, 30+ measured): women 4\'9"-5\'9" average 138.5-192.4 lb, men 5\'2"-6\'3" '
        '149.9-245.4 lb, every average above the healthy range for its height; BMI 25+ by height 60-78% women, 64-81% men; '
        'waist over the NHLBI lines (>102 / >88 cm) 47.4% of men, 67.5% of women; ages 20-74: men 200.2 lb, women 173.7 lb; '
        'decade steps outside the 95% CI: 30s vs 20s +10.2 lb men, +13.4 lb women; 80+ vs 70s -13.3 lb men; women 60s, '
        '70s, 80+ each lower than the decade before. Same method moves the men\'s 5\'10" median on /blog/bmi-chart-men/ '
        'from 199.3 to 199.1 lb (bcm_stats.py rerun)'),
    'nhanes-anthropometric-reference': ('notes',
        ' CMB-019 (PDF re-read 2026-10-22): /average-weight/ prints Table 4 (weight, adults 20+ and each decade; men '
        '199.0 lb, women 171.8 lb, medians 191.0 / 162.0 lb), Table 8 (height 68.9 / 63.5 in; keeps pregnant women, n 3,307 '
        'women), Table 10 (BMI: means 29.4 / 30.0, medians 28.2 / 28.3) and Table 12 (waist, in cm; the page gives the '
        'inch means 40.6 / 38.5 in, = FastStats). compute.py reproduces Table 4 in full and the adult rows of Tables 8, 10 '
        'and 12 at 0.1 (204 values).'),
}

NEW = [
    {'domain': 'cdc-faststats-body-measurements',
     'source': 'CDC FastStats: Body Measurements',
     'publisher': 'CDC National Center for Health Statistics',
     'url': 'https://www.cdc.gov/nchs/fastats/body-measurements.htm', 'endpoint': '', 'access': 'page',
     'license': 'Public domain (US federal work)', 'tier': 'A', 'cadence': 'per NHANES cycle',
     'granularity': 'national; adults 20+ by sex', 'format': 'HTML', 'key_required': 'no',
     'attribution': 'Source: CDC National Center for Health Statistics, FastStats: Body Measurements',
     'verified_date': '2026-10-22', 'next_check': '2027-04-22', 'coverage': 'adults 20+, August 2021-August 2023',
     'sample_note': ('men: height 68.9 in, weight 199.0 lb, waist 40.6 in; women: 63.5 in, 171.8 lb, 38.5 in; source line: '
                     '"Anthropometric Reference Data for Children and Adults: United States, August 2021-August 2023, '
                     'tables 4, 8, 12"; "Last Reviewed: June 26, 2025" (read 2026-10-22)'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-019: the page /average-weight/ points readers to as the figures CDC itself quotes. Same values as '
               'nhanes-anthropometric-reference.')},
    {'domain': 'nhanes-anthropometric-reference-2015-2018',
     'source': 'NCHS Vital and Health Statistics Series 3 No. 46: anthropometric reference data, 2015-2018',
     'publisher': 'CDC National Center for Health Statistics',
     'url': 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-046-508.pdf', 'endpoint': '', 'access': 'page',
     'license': 'Public domain (US federal work)', 'tier': 'A', 'cadence': 'superseded by Series 3 No. 50',
     'granularity': 'national; by sex and age group; means, SEs, percentiles', 'format': 'PDF tables',
     'key_required': 'no',
     'attribution': 'Source: CDC National Center for Health Statistics, Vital and Health Statistics Series 3, No. 46',
     'verified_date': '2026-10-22', 'next_check': '2027-10-22', 'coverage': '2015-2018, ages 2+',
     'sample_note': ('Fryar CD, Carroll MD, Gu Q, Afful J, Ogden CL, January 2021. Adults 20+: mean weight men 199.8 lb '
                     '(5,085 examined), women 170.8 lb (5,386; "Data exclude pregnant females.") (read 2026-10-22)'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-019: superseded; cited only to explain the 199.8 lb that most results for "average weight for men" '
               'still quote (owner SERP pastes 2026-10-22).')},
    {'domain': 'nchs-advance-data-347',
     'source': 'CDC Advance Data from Vital and Health Statistics No. 347: Mean body weight, height, and body mass index, '
               'United States 1960-2002',
     'publisher': 'CDC National Center for Health Statistics',
     'url': 'https://www.cdc.gov/nchs/data/ad/ad347.pdf', 'endpoint': '', 'access': 'page',
     'license': 'Public domain (US federal work)', 'tier': 'A', 'cadence': 'one-off (2004)',
     'granularity': 'national; by survey, sex and age group', 'format': 'PDF tables', 'key_required': 'no',
     'attribution': 'Source: Ogden CL et al., Advance Data from Vital and Health Statistics No. 347, NCHS 2004',
     'verified_date': '2026-10-22', 'next_check': '2028-10-22',
     'coverage': 'adults 20-74 and children, NHES I (1960-1962) to NHANES 1999-2002',
     'sample_note': ('Ogden CL, Fryar CD, Carroll MD, Flegal KM, October 27, 2004. Table 6, "Mean weight (pounds) by '
                     'survey, sex, and age group; adults": ages 20-74, men 166.3 lb (SE 0.7) in 1960-1962 and 191.0 (1.0) '
                     'in 1999-2002; women 140.2 (0.5) and 164.3 (1.1). No age-adjustment footnote on the table; Methods: '
                     'trend tests on age-adjusted values; "Pregnant females were excluded from all the analyses." (read '
                     '2026-10-22)'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-019: /average-weight/ compares these with its own 2021-2023 mean for ages 20-74 (men 200.2 lb, '
               'women 173.7 lb; crude weighted means, as the table prints).')},
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
            if SLUG not in ps: ps.append(SLUG)
            r[ix['pages_served']] = ';'.join(ps); linked.add(d)
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
            r[ix['wedge']] = ('What US adults weigh at every height, women 4\'9"-5\'9" and men 5\'2"-6\'3" (NHANES 2021-2023, '
                              'our calculation; the national figures = NCHS Series 3 No. 50): the average above the healthy '
                              'range at every height measured, a tool that places a weight among people measured at the same '
                              'height or an inch either side, age steps stated only outside their margin of error, and why '
                              'results still quote 199.8 lb (built CMB-019)')
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = ('One page with height and age tables and row anchors - never one page per height (doorway '
                              'rule). D-14 rebuild CMB-019 (research/average-weight-build/); also cites '
                              'nhanes-anthropometric-reference, cdc-faststats-body-measurements, '
                              'nhanes-anthropometric-reference-2015-2018, nchs-advance-data-347, cdc-adult-bmi-categories and '
                              'nhlbi-1998-obesity-guidelines. Owns "average weight for men" (9.9k) and 186 more keywords, '
                              '161k/mo')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: the average weight tool.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'Average weight tool (CMB-019)' not in d
d = d.replace(anchor, (
    '### Average weight tool (CMB-019)\n'
    '- `/average-weight/` compares a height, and an optional weight and age group, with US adults of the same sex, using '
    'the shared calculator parts and no page-level style: `.calculator-card.awt` › `.calc-panel` › two `.unit-toggle`s '
    '(Woman / Man; ft, in, lb / cm, kg; `aria-pressed`) › `.form-row.form-row--pair` rows (feet and inches, or cm; weight '
    'and age group) › `.calculate-btn`. The card follows its `.content-section`, never inside it.\n'
    '- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the BMI category when a weight '
    'is entered (neutral without one), with the share of people measured at that height or an inch either side (heights '
    'rounded to the nearest inch) who weigh less, or the '
    'average at that height, in a neutral `.bmi-value`; then `.er-section`s with `h3` headings: where you fall (the CMB-018 '
    'box plot: 10th-90th percentile line, middle half in the series colour at 16%, the average as an ink tick, the healthy '
    'range as a green bar, the weight entered as a dashed ink line labelled "You"), your BMI with a `.cat-dot`, the age '
    'group\'s average, the height rank, and the source line. The figure is drawn in the unit entered (kg ticks every 10 or '
    '20, lb every 20 or 40); weights print in that unit first.\n'
    '- A height with fewer than 30 people measured gets no average: the card says so and gives the national average and '
    'the healthy range instead. Shares follow the CMB-016 rule ("more than 99%", "under 1%").\n'
    '- By-height tables (`.data-table` in a `.flow` section): one row per inch with an id (`#women-5-4`, `#men-5-9`), '
    'centimeters under the height (`.th-sub`), kilograms under the average (`.cell-kg`), a † on heights with fewer than 60 '
    'people measured, explained in the source note.\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/blog/bmi-chart-men/': 'bmi-chart-men'}"
assert c.count(old) == 1
c = c.replace(old, "             '/blog/bmi-chart-men/': 'bmi-chart-men',\n"
                   "             '/average-weight/': 'average-weight'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)
# styles.css: the average weight tool takes the body fat rank tool's sizes (no page-level style).
sp = os.path.join(ROOT, 'assets/css/styles.css'); st = open(sp, encoding='utf-8', newline='').read()
for old, new in (('.bfr .bmi-value { font-size: 3rem; }', '.bfr .bmi-value, .awt .bmi-value { font-size: 3rem; }'),
                 ('.bfr .bmi-category { font-size: 1.0625rem; line-height: 1.4; }',
                  '.bfr .bmi-category, .awt .bmi-category { font-size: 1.0625rem; line-height: 1.4; }'),
                 ('.bfr .er-section svg { display: block;', '.bfr .er-section svg, .awt .er-section svg { display: block;')):
    assert st.count(old) == 1, old
    st = st.replace(old, new)
assert 'data-table--fit' not in st and '.awt [hidden]' not in st
st = st.rstrip('\n') + '\n' + (
    '\n/* CMB-019 — /average-weight/: the US / metric rows of the weight tool hide with the hidden attribute (.form-row sets\n'
    '   display: grid), and five-column number tables fit a 390 px phone: smaller type and tighter cells below 600 px,\n'
    '   numbers and ranges on one line. */\n'
    '.awt [hidden] { display: none; }\n'
    '.data-table--fit td.num { white-space: nowrap; }\n'
    '@media (max-width: 600px) { .flow .data-table--fit { font-size: 0.8125rem; } '
    '.flow .data-table--fit th, .flow .data-table--fit td { padding: 0.5rem 0.375rem; } }\n')
open(sp, 'w', encoding='utf-8', newline='').write(st)
print('patched: registry', len(USED), 'rows linked,', len(NOTES), 'noted,', len(NEW), 'new; page map; DESIGN.md; '
      'check_images PREFERRED; styles.css .awt')
