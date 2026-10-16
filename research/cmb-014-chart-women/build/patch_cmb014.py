#!/usr/bin/env python3
"""CMB-014 registry and page map: the women's chart sources, verified in chat on 2026-10-15; DESIGN.md chart-table lines.
usage: patch_cmb014.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'blog/bmi-chart-women'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2021-2023-exam-files', 'nhanes-adult-obesity-2021-2023', 'cdc-adult-bmi-categories', 'cdc-child-bmi-categories',
        'cdc-calculating-bmi', 'nhlbi-1998-obesity-guidelines', 'nice-ng246-ethnicity-thresholds', 'cdc-ndpp-eligibility',
        'nhanes-2011-2018-dxa', 'gallagher-2000-bf-ranges', 'gbmc-2016-bmi-mortality', 'winter-2014-bmi-mortality-65')

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    seen, linked = set(), set()
    for r in rows[1:]:
        d = r[ix['domain']]; seen.add(d)
        if d in USED:
            ps = [x for x in r[ix['pages_served']].split(';') if x]
            if SLUG not in ps: ps.append(SLUG)
            r[ix['pages_served']] = ';'.join(ps); linked.add(d)
        if d == 'nhanes-2021-2023-exam-files':
            r[ix['sample_note']] += ('. CMB-014 (2026-10-15): women 20+ (excl. pregnant, n 3,249) by CDC category and age: '
                                     'healthy 28.1 (33.8 / 23.9 / 26.5 at 20-39 / 40-59 / 60+), overweight 28.6, obesity 41.3 '
                                     '(36.8 / 47.4 / 39.6), class 3 12.1 (13.0 / 14.7 / 8.4), all = NCHS DB508; waist >= 88 cm '
                                     'and waist-to-height >= 0.5 by BMI category (n 3,113 with a waist): healthy 16.8 / 50.2, '
                                     'overweight 79.1 / 95.5, obesity 99.2 / 100.0; ADA 2026 thresholds 69.4 vs BMI-only 41.8 in '
                                     'the same 3,216 women; research/chart-women-build/bcw_stats.py')
        if d == 'nhanes-adult-obesity-2021-2023':
            r[ix['notes']] += (' CMB-014 (checked 2026-10-15): Figure 1 and 3 data tables, women by age: obesity 36.8 / 47.4 / '
                               '39.6, severe obesity 13.0 / 14.7 / 8.4 at 20-39 / 40-59 / 60+; text: "Among women, the '
                               'prevalence [of severe obesity] was higher in those ages 20-39 and 40-59 than in those age 60 '
                               'and older." Reproduced exactly by research/chart-women-build/bcw_stats.py.')
        if d == 'nice-ng246-ethnicity-thresholds':
            r[ix['notes']] += (' CMB-014 (checked 2026-10-15): same chapter, waist-to-height ratio for adults with BMI below 35 '
                               '[2022]: healthy central adiposity 0.4 to 0.49, increased 0.5 to 0.59, high 0.6 or more; '
                               '"These classifications can be used for people with a BMI under 35 kg/m2 of both sexes and all '
                               'ethnicities".')
        if d == 'nhanes-2011-2018-dxa':
            r[ix['notes']] += (' CMB-014: /blog/bmi-chart-women/ quotes the weighted median body fat of women 20-59 by BMI band: '
                               '33.4% (18.5-24.9), 39.5% (25-29.9), 44.0% (30+); men 22.1% at 18.5-24.9 '
                               '(research/body-fat/bf_results.json by_bmi).')
        if d == 'cdc-adult-bmi-categories':
            r[ix['notes']] += ' CMB-014 (checked 2026-10-15): page last reviewed March 19, 2024; categories unchanged.'
    assert linked == set(USED), set(USED) - linked
    def row(**k):
        r = [''] * len(head)
        for a, v in k.items(): r[ix[a]] = v
        return r
    base = dict(access='page', license='public-domain', tier='A', cadence='irregular', granularity='national', format='HTML',
                key_required='no', verified_date='2026-10-15', next_check='2027-10-15', status='verified', pages_served=SLUG)
    new = [
        row(domain='ada-2026-obesity-standards',
            source='American Diabetes Association Professional Practice Committee for Obesity. Screening, Diagnosis, Evaluation, and Staging of Obesity in Adults: Standards of Care in Overweight and Obesity-2026 (Diabetes, Obesity, and CardioMetabolic CARE; BMJ Open Diabetes Research & Care)',
            publisher='American Diabetes Association', url='https://doi.org/10.2337/doci26-0003',
            endpoint='https://diabetes.org/newsroom/press-releases/new-standards-care-overweight-and-obesity-section-screening-diagnosis-0',
            attribution='American Diabetes Association, Standards of Care in Overweight and Obesity-2026',
            coverage='nonpregnant adults; non-Asian and Asian backgrounds',
            sample_note='3.3a non-Asian: obesity at BMI >=30, or BMI >=25 with waist-to-height ratio >=0.5, or BMI >=25 with waist >=88 cm (women) / >=102 cm (men); 3.3b Asian: BMI >=27.5, or BMI >=23 with ratio >=0.5 or waist >=80 cm (women) / >=90 cm (men); Table 3.1 gives 88 cm as 35 in and 80 cm as 31.5 in; overweight = BMI 25-29.9 (Asian 23-27.4) without central adiposity. "Loss of muscle mass in older adults reduces the accuracy of BMI, which may lead to underdiagnosis of obesity." Press release dated 2026-06-29 (full section PDF and press release checked 2026-10-15)',
            notes='doi.org and PubMed/PMC pages refused the fetcher (captcha/error); the recommendations were read from the ADA-hosted PDF of the section (datocms-assets.com/129290/1784636255-scoo-26-pdf.pdf).',
            **dict(base, license='ADA/BMJ; cited, not reproduced', granularity='n/a')),
        row(domain='cdc-pregnancy-weight-gain', source='CDC: Weight Gain During Pregnancy', publisher='CDC',
            url='https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
            endpoint='https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
            attribution='CDC, Weight Gain During Pregnancy (Institute of Medicine recommendations)',
            coverage='US pregnant women, single and twin pregnancies',
            sample_note='Single pregnancy, by BMI before pregnancy: underweight less than 18.5, 28-40 lb; normal weight 18.5-24.9, 25-35 lb; overweight 25.0-29.9, 15-25 lb; obese "BMI 30.0-39.9", 11-20 lb; "All recommendations are from the Institute of Medicine, with the exception of underweight women with twins"; last reviewed 2023-12-13 (checked 2026-10-15)',
            **base),
        row(domain='nih-bmi-table-2022', source='NIH NHLBI: Body Mass Index Table (NIH Publication No. 22-HL-8190, September 2022)',
            publisher='NIH NHLBI', url='https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_tbl.pdf',
            endpoint='https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_tbl.pdf',
            attribution='NIH, Body Mass Index Table', coverage='heights 4\'10" to 6\'4" (58-76 in), BMI 19 to 54',
            sample_note='One column per whole BMI from 19 to 54; labels Healthy Weight / Overweight / Obese / Extreme Obesity; the 64-inch row reads 110 lb under BMI 19 and 140 lb under BMI 24; 58 in: 91 and 115 (checked 2026-10-15)',
            **dict(base, format='PDF')),
    ]
    for r in new:
        assert r[ix['domain']] not in seen, r[ix['domain']]
    return rows + new

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    hit = 0
    for r in rows[1:]:
        if r[ix['slug']] == SLUG:
            hit += 1
            r[ix['wedge']] = ('US women by BMI category and age (NHANES 2021-2023, = NCHS DB508) + waist at the same BMI and the '
                              'June 2026 ADA obesity thresholds applied to US women (built CMB-014)')
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = ('Restored URL (P0 B2); 7,166 Bing clicks before the Aug 308. D-14 rebuild CMB-014 '
                              '(research/chart-women-build/); also cites ada-2026-obesity-standards, cdc-pregnancy-weight-gain, '
                              'nih-bmi-table-2022, nhanes-adult-obesity-2021-2023 and the other rows listing this page. '
                              'Owns "bmi chart female" (74k) and 602 more keywords, 390k/mo')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: the chart-table component and the wide raster figure.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1
d = d.replace(anchor, (
    '### Weight-by-height chart tables — `.weight-chart` (CMB-014)\n'
    '- The chart table on D-14 chart pages (first `/blog/bmi-chart-women/`): one row per height with a `#h-5-4` id, one '
    'column per CDC category, pounds with kilograms below (`.cell-kg`), centimeters under the height (`.cell-cm`). Cells use '
    'the category tints with text from the same hue (`.c-under` … `.c-ob3`, 5.2:1 or better); white hairlines between '
    'cells; the height column stays put while the table scrolls sideways; a targeted row gets a 3 px `--link` bar. '
    '`min-width: 600px`, inside `.table-responsive`; headers wrap.\n'
    '- A printable chart image goes in `figure.figure.figure--wide` (680 px) as an `<img>` with width and height, linked to '
    'the full-size file, so search engines can index it.\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)
print('registry: 3 new rows,', len(USED), 'rows linked; page map row built; DESIGN.md chart-table lines')
