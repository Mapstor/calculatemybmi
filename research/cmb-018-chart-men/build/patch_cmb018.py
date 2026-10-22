#!/usr/bin/env python3
"""CMB-018 registry, page map, DESIGN.md and the image gate for /blog/bmi-chart-men/ (sources re-read in chat 2026-10-22).
usage: patch_cmb018.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'blog/bmi-chart-men'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2021-2023-exam-files', 'nhanes-adult-obesity-2021-2023', 'cdc-adult-bmi-categories', 'cdc-child-bmi-categories',
        'cdc-calculating-bmi', 'cdc-about-bmi', 'nih-bmi-table-2022', 'nhanes-2011-2018-dxa', 'nhlbi-1998-obesity-guidelines',
        'nice-ng246-ethnicity-thresholds', 'ada-2026-obesity-standards', 'cdc-ndpp-eligibility', 'gbmc-2016-bmi-mortality',
        'winter-2014-bmi-mortality-65')

NOTES = {
    'nhanes-2021-2023-exam-files': ('sample_note',
        '. CMB-018 (2026-10-22): men 20+ (n 2,680) by CDC category and age: healthy 24.0 (28.3 / 20.7 / 22.5 at 20-39 / 40-59 '
        '/ 60+), overweight 35.7 (35.4 / 33.5 / 38.9), obesity 39.2 (34.3 / 45.4 / 38.0), class 3 6.7 (6.1 / 9.2 / 4.3), all = '
        'NCHS DB508; BMI 25+ by measured height 5\'4"-6\'2": 64-81%, every CI above 50%; men at 5\'10" (n 313): healthy 22.3, '
        'overweight 38.3, obesity 39.4; waist >= 102 cm and waist-to-height >= 0.5 by BMI category (n 2,596): healthy 0.6 / '
        '42.9, overweight 30.8 / 93.7, obesity 94.3 / 100.0; ADA 2026 thresholds 73.4 vs BMI-only 39.5 in the same 2,659 men '
        '(= bc_stats.json); research/chart-men-build/bcm_stats.py'),
    'nhanes-adult-obesity-2021-2023': ('notes',
        ' CMB-018 (checked 2026-10-22): Figure 1 and 3 data tables, men by age: obesity 34.3 / 45.4 / 38.0, severe obesity '
        '6.1 / 9.2 / 4.3 at 20-39 / 40-59 / 60+; text: "This pattern was seen in both men and women" (obesity highest at 40-59) '
        'and "Among men, the prevalence [of severe obesity] was highest in those ages 40-59." Reproduced exactly by '
        'research/chart-men-build/bcm_stats.py.'),
    'nih-bmi-table-2022': ('notes',
        ' CMB-018 (PDF re-read 2026-10-22 at internet-prod.nhlbi.nih.gov, file bmi_tbl-508NF3, no publication number printed): '
        'rows 58-76 in, BMI 19-54; the 70-inch row reads 132 lb under BMI 19, 167 under 24, 174 under 25, 209 under 30; the '
        'first column group is labeled "Normal" (the sample note above says "Healthy Weight").'),
    'nhanes-2011-2018-dxa': ('notes',
        ' CMB-018: /blog/bmi-chart-men/ quotes men 20-59 by BMI category (10th / 25th / 50th / 75th / 90th percentile of '
        'body fat): healthy 16.0 / 18.6 / 22.1 / 25.0 / 27.7, overweight 21.7 / 24.2 / 26.9 / 29.8 / 32.0, obesity 26.0 / 28.7 / '
        '31.6 / 35.1 / 38.2 (= bfpc_stats.json); 11.8% of men with an overweight BMI and 1.4% with obesity at or below the '
        'healthy-BMI median, 14.0% of men with a healthy BMI at or above the overweight median '
        '(research/chart-men-build/bcm_dxa.py).'),
    'gbmc-2016-bmi-mortality': ('notes',
        ' CMB-018 (abstract re-read 2026-10-22 via the University of Cambridge repository): main analyses in 3,951,455 '
        'never-smokers without pre-existing disease from 189 of 239 studies, first 5 years of follow-up excluded; "All-cause '
        'mortality was minimal at 20.0-25.0 kg/m2"; per 5 units above 25 the association was stronger in men (1.51) than in '
        'women (1.30) and at 35-49 (1.52) than at 70-89 (1.21).'),
    'ada-2026-obesity-standards': ('notes',
        ' CMB-018 (section PDF re-read 2026-10-22, same datocms-assets URL): Table 3.1 note gives the waist lines in inches: '
        '"Elevated WC in women with a non-Asian background is >=35 inches and in men with a non-Asian background is >=40 '
        'inches." "Elevated WC in women with an Asian background is >=31.5 inches and in men with an Asian background is >=35.5 '
        'inches." The recommendations (3.3a/3.3b) give cm (>=102 / >=90 cm for men); /blog/bmi-chart-men/ pairs each with '
        'the table\'s inches (40 in, 35.5 in) and computes in cm. Muscle sentence re-read verbatim; press release dated '
        '2026-06-29.'),
    'winter-2014-bmi-mortality-65': ('notes',
        ' CMB-017/CMB-018 (abstract re-read 2026-10-22 on a University of Queensland copy): "Because the risk of mortality '
        'increased in older people with a BMI <23.0"; "Mortality risk began to increase for BMI >33.0".'),
}

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    linked, noted = set(), set()
    for r in rows[1:]:
        d = r[ix['domain']]
        if d in USED:
            ps = [x for x in r[ix['pages_served']].split(';') if x]
            if SLUG not in ps: ps.append(SLUG)
            r[ix['pages_served']] = ';'.join(ps); linked.add(d)
        if d in NOTES:
            col, txt = NOTES[d]
            assert txt.strip() not in r[ix[col]], d
            r[ix[col]] += txt; noted.add(d)
    assert linked == set(USED), set(USED) - linked
    assert noted == set(NOTES), set(NOTES) - noted
    return rows

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    hit = 0
    for r in rows[1:]:
        if r[ix['slug']] == SLUG:
            hit += 1
            r[ix['wedge']] = ('US men on the chart: most men above the healthy range at every height 5\'4"-6\'2" (NHANES '
                              '2021-2023, = NCHS DB508 for men by age), the 5\'10" answers, muscle or fat (DXA body fat at '
                              'the same BMI, how often they disagree) and the waist-to-height ratio deciding the June 2026 '
                              'ADA thresholds for men (built CMB-018)')
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = ('Restored URL (P0 B2). D-14 rebuild CMB-018 (research/chart-men-build/); also cites '
                              'nhanes-2011-2018-dxa, nih-bmi-table-2022, ada-2026-obesity-standards, gbmc-2016-bmi-mortality '
                              'and the other rows listing this page. Owns "bmi chart for men" (40.5k) and 263 more keywords, '
                              '168k/mo')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: the two distribution figures.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'Distributions over the chart (CMB-018)' not in d
d = d.replace(anchor, (
    '### Distributions over the chart (CMB-018)\n'
    '- A chart figure can carry where real people fall on it: on `/blog/bmi-chart-men/` each height row shows the CDC '
    'categories as the light table tints, a 6 px bar in the series color (men `#4338ca`) for the middle half of US men of '
    'that height, and a 3 px ink tick (`#111827`) for the median. Tints stay light so the bar and tick read on every band.\n'
    '- Box plots for one measure across categories: the 10th-90th percentile as a 1.5 px line, the middle half as a box in '
    'the series color at 16% opacity with a 1 px outline, the median as an ink tick; a dashed grey line marks a reference '
    'value, named in the figure. Row labels sit above their box, so values never collide with the marks.\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/women-bmi-calculator/': 'women-bmi-calculator'}"
assert c.count(old) == 1
c = c.replace(old, "             '/women-bmi-calculator/': 'women-bmi-calculator',\n"
                   "             '/blog/bmi-chart-men/': 'bmi-chart-men'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)
print('patched: registry', len(USED), 'rows linked,', len(NOTES), 'noted; page map; DESIGN.md; check_images PREFERRED')
