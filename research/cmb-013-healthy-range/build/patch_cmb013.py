#!/usr/bin/env python3
"""CMB-013 registry and page map: the healthy-range guide's sources, verified in chat on 2026-10-15.
usage: patch_cmb013.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'blog/healthy-bmi-range'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2021-2023-exam-files', 'nhanes-adult-weight-trends', 'nhanes-adult-obesity-2021-2023', 'nhanes-underweight',
        'cdc-adult-bmi-categories', 'cdc-child-bmi-categories', 'cdc-about-bmi', 'nhanes-2011-2018-dxa',
        'gallagher-2000-bf-ranges', 'nhlbi-1998-obesity-guidelines', 'winter-2014-bmi-mortality-65', 'who-2004-asian-bmi',
        'lancet-clinical-obesity-2025', 'niddk-body-weight-planner', 'wing-2011-look-ahead', 'cdc-calculating-bmi', 'who-trs-854')

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
            r[ix['sample_note']] += ('. CMB-013 (2026-10-15): share of adults 20+ (excl. pregnant) in each CDC category by sex and age '
                                     '(20-39, 40-59, 60+): healthy weight 26.0 (men 24.0, women 28.1; 31.0 / 22.3 / 24.6 by age); '
                                     'reproduces NCHS obesity 40.3 / 39.2 / 41.3 and 46.4 at 40-59, class 3 9.4 / 6.7 / 12.1, '
                                     'overweight 32.1, underweight 1.6; research/healthy-range-build/healthy_stats.py')
        if d == 'nhanes-2011-2018-dxa':
            r[ix['notes']] += (' CMB-013: /blog/healthy-bmi-range/ quotes the weighted median body fat of adults 20-59 with a BMI of '
                               '18.5-24.9: women 33.4%, men 22.1% (research/body-fat/bf_results.json by_bmi, n 1,667 and 1,540).')
        if d == 'nhlbi-1998-obesity-guidelines':
            r[ix['notes']] += (' CMB-013 (checked 2026-10-15): classification underweight <18.5, normal 18.5-24.9, overweight 25.0-29.9, '
                               'obesity classes 1-3 from 30.0, 35.0, 40 in the Rev Panam Salud Publica 2001 summary of the NIH practical '
                               'guide built on the 1998 guidelines; "Excess abdominal fat is an important, independent risk factor for '
                               'disease." Waist text deep link: Chapter 4, Treatment Guidelines, https://www.ncbi.nlm.nih.gov/books/NBK2004/ '
                               '(cut-offs "in conjunction with BMI" at 25 to 34.9; "the waist circumference correlates with the amount of fat '
                               'in the abdomen"; excess abdominal fat "an independent predictor" of risk).')
        if d == 'cdc-adult-bmi-categories':
            r[ix['notes']] += (' CMB-013 (checked 2026-10-15): "For adults 20 and older, BMI categories are based on a person\'s BMI '
                               'regardless of age, sex, or race."; healthy weight "18.5 to less than 25".')
    assert linked == set(USED), set(USED) - linked
    def row(**k):
        r = [''] * len(head)
        for a, v in k.items(): r[ix[a]] = v
        return r
    base = dict(access='page', license='public-domain', tier='A', cadence='irregular', granularity='national', format='HTML',
                key_required='no', verified_date='2026-10-15', next_check='2027-10-15', status='verified', pages_served=SLUG)
    new = [
        row(domain='gbmc-2016-bmi-mortality',
            source='The Global BMI Mortality Collaboration. Body-mass index and all-cause mortality: individual-participant-data meta-analysis of 239 prospective studies in four continents. Lancet 2016;388:776-86',
            publisher='The Lancet', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/', endpoint='https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
            attribution='Global BMI Mortality Collaboration, Lancet 2016',
            coverage='10,625,411 participants, 239 prospective studies, 32 countries (Asia, Australia and New Zealand, Europe, North America); primary analysis 3,951,455 never-smokers without chronic disease at recruitment who survived 5 years (189 studies), 385,879 deaths',
            sample_note='All-cause mortality HR (95% CI) vs BMI 22.5-<25.0: 15.0-<18.5 1.51 (1.43-1.59); 18.5-<20.0 1.13 (1.09-1.17); 20.0-<22.5 1.00 (0.98-1.02); 22.5-<25.0 1.00 (0.99-1.01); 25.0-<27.5 1.07 (1.07-1.08); 27.5-<30.0 1.20 (1.18-1.22); 30.0-<35.0 1.45 (1.41-1.48); 35.0-<40.0 1.94 (1.87-2.01); 40.0-<60.0 2.76 (2.60-2.92); minimal at 20.0-25.0. Per 5 kg/m2 above 25: Europe 1.39, North America 1.29, East Asia 1.39, Australia and New Zealand 1.31; ages 35-49 1.52, 70-89 1.21; men 1.51, women 1.30. Interpretation: "The associations of both overweight and obesity with higher all-cause mortality were broadly consistent in four continents." (PMC full text checked 2026-10-15)',
            **dict(base, license='open access (PMC); cited, not reproduced', granularity='international; by BMI band, region, age and sex')),
        row(domain='who-obesity-fact-sheet', source='WHO fact sheet: Obesity and overweight', publisher='World Health Organization',
            url='https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight', endpoint='https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight',
            attribution='WHO, Obesity and overweight (fact sheet)', coverage='global definitions (adults, children, infants)',
            sample_note='For adults: "overweight is a BMI greater than or equal to 25" and "obesity is a BMI greater than or equal to 30"; fact sheet dated 7 October 2026 (checked 2026-10-15)',
            notes='Not quoted: the sheet\'s sentence that BMI categories "vary by age and sex for adults, adolescents, children and infants" (its adult definitions are single cut-offs). WHO Europe\'s "A healthy lifestyle" page that carried the Normal weight / Pre-obesity table is now "Everyday actions for better health" with no BMI table (checked 2026-10-15).',
            **dict(base, license='WHO terms; cited, not reproduced', granularity='international')),
        row(domain='odphp-physical-activity-guidelines', source='HHS Physical Activity Guidelines for Americans, 2nd edition (2018): ODPHP "Top 10 Things to Know"',
            publisher='US Department of Health and Human Services (ODPHP)',
            url='https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/top-10-things-know',
            endpoint='https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/top-10-things-know',
            attribution='HHS, Physical Activity Guidelines for Americans, 2nd edition', coverage='US adults (and other age groups)',
            sample_note='"adults need at least 150 to 300 minutes of moderate-intensity aerobic activity" a week; "Adults also need muscle-strengthening activity, like lifting weights or doing push-ups, at least 2 days each week." Same amounts (and 75-150 min vigorous) in Piercy KL et al., JAMA 2018;320:2020-8, CDC Stacks copy (checked 2026-10-15)',
            **base),
        row(domain='ko-tang-2006-wpro-2000',
            source='Ko GT, Tang JS. Prevalence of obesity, overweight and underweight in a Hong Kong community. Asia Pac J Clin Nutr 2006;15(2):236-41 (cites WHO/IASO/IOTF, The Asia-Pacific perspective: redefining obesity and its treatment, 2000)',
            publisher='Asia Pacific Journal of Clinical Nutrition', url='https://apjcn.qdu.edu.cn/15_2_7.pdf', endpoint='https://apjcn.qdu.edu.cn/15_2_7.pdf',
            attribution='Ko GT, Tang JS. Asia Pac J Clin Nutr 2006', coverage='Asian adults (2000 Asia-Pacific proposal; 2004 WHO consultation)',
            sample_note='"In this proposal, BMI cutoff levels for overweight and obesity in Asians were redefined as >=23 kg/m2 and >=25 kg/m2 respectively" (ref. 9: WHO/IASO/IOTF, Health Communications Australia, 2000); also the January 2004 WHO consultation adding 23, 27.5, 32.5 and 37.5 as public health action points (PDF checked 2026-10-15)',
            notes='Secondary citation of the 2000 WHO Western Pacific / IASO / IOTF report: the WHO IRIS record returned an error to fetchers (2026-10-15).',
            **dict(base, license='cited, not reproduced', tier='B', granularity='Asia-Pacific', format='PDF')),
        row(domain='medlineplus-unintentional-weight-loss', source='MedlinePlus Medical Encyclopedia: Weight loss - unintentional',
            publisher='NIH National Library of Medicine', url='https://medlineplus.gov/ency/article/003107.htm',
            endpoint='https://medlineplus.gov/ency/article/003107.htm', attribution='MedlinePlus (NIH National Library of Medicine)',
            coverage='adults and children (general)',
            sample_note='Unexplained weight loss: about 10 pounds (4.5 kg) or 5% of normal body weight over 6 to 12 months or less without a known reason; "When to Contact a Medical Professional" includes having lost that amount without knowing why; review date 2025-01-01 (checked 2026-10-15)',
            **dict(base, license='public-domain (NLM text; A.D.A.M. content cited, not reproduced)', granularity='n/a')),
        row(domain='nice-ng246-ethnicity-thresholds', source='NICE guideline NG246: Overweight and obesity management (January 2025), recommendations 1.9.10-1.9.11',
            publisher='National Institute for Health and Care Excellence (UK)',
            url='https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
            endpoint='https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
            attribution='NICE guideline NG246 (recommendation 1.9.11, 2022)', coverage='UK adults; South Asian, Chinese, other Asian, Middle Eastern, Black African or African-Caribbean backgrounds',
            sample_note='1.9.11 [2022]: these groups "are prone to central adiposity and their cardiometabolic risk occurs at lower BMI, so use lower BMI thresholds": overweight BMI 23 to 27.4, obesity 27.5 or above; classes 2 and 3 usually 2.5 below the standard thresholds. 1.9.10: healthy weight 18.5 to 24.9, overweight 25 to 29.9, obesity classes from 30, 35, 40. NG246 replaced CG189 and PH46 (checked 2026-10-15)',
            **dict(base, license='NICE content; cited, not reproduced', granularity='UK')),
        row(domain='cdc-ndpp-eligibility', source='CDC: Are You Eligible to Join the National DPP Lifestyle Change Program?', publisher='CDC',
            url='https://www.cdc.gov/diabetes-prevention/eligible-lifestyle-change-program/index.html',
            endpoint='https://www.cdc.gov/diabetes-prevention/eligible-lifestyle-change-program/index.html',
            attribution='CDC, National Diabetes Prevention Program eligibility', coverage='US adults 18+',
            sample_note='"Have a body mass index (BMI) of 25 or higher (23 or higher if you\'re an Asian American person)"; page last reviewed 2024-05-15 (checked 2026-10-15)',
            **base),
        row(domain='nhlbi-calculate-your-bmi', source='NHLBI: Calculate Your BMI', publisher='NIH NHLBI',
            url='https://www.nhlbi.nih.gov/calculate-your-bmi', endpoint='https://www.nhlbi.nih.gov/calculate-your-bmi',
            attribution='NHLBI, Calculate Your BMI', coverage='US adults',
            sample_note='Underweight (below 18.5); Healthy (18.5 - 24.9); Overweight (25.0 - 29.9); Obesity (30.0 or above) (checked 2026-10-15)',
            **base),
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
            r[ix['wedge']] = ('Share of US adults with a healthy BMI by age and sex: NHANES 2021-2023 (built CMB-013) + the GBMC 2016 '
                              'mortality evidence behind 18.5-24.9')
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = ('D-14 rebuild CMB-013 (research/healthy-range-build/); also cites gbmc-2016-bmi-mortality, '
                              'cdc-adult-bmi-categories, who-obesity-fact-sheet, nhlbi-1998-obesity-guidelines, who-2004-asian-bmi, '
                              'ko-tang-2006-wpro-2000, nice-ng246-ethnicity-thresholds, cdc-ndpp-eligibility, nhlbi-calculate-your-bmi, '
                              'odphp-physical-activity-guidelines, '
                              'medlineplus-unintentional-weight-loss and the other rows '
                              'listing this page. '
                              'Owns 22.2k + 18.1k "normal bmi" groups as secondaries')
    assert hit == 1
    return rows

# DESIGN.md: the reading layout and the guide-page order the rollout repeats.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '- **Reading column**: `.content-narrow` — `max-width: 800px`, centered. Prose and FAQ live here.\n'
assert d.count(anchor) == 1
d = d.replace(anchor, anchor + (
    '- **Reading layout (D-14)**: `main.reading` keeps every block in one 680 px column. Inside it, the key-takeaways answer and '
    'bullets stop at `34rem`, about 75 characters a line at 15 px (CMB-013).\n'
    '- **Guide pages (CMB-013, `/blog/healthy-bmi-range/`)**: page head (H1, byline, up to three `.intro-text` paragraphs: pain, '
    'stakes, promise) → `.key-takeaways` (`p.answer` of 40–60 words, then bullets) → `.disclaimer-box` → hero `figure.figure` → '
    '`.toc-inline` → `section.content-section.flow` blocks → flat FAQ → sources and method → one `.related-cols` block. SVG text '
    'is 12 px or larger in viewBox units.\n'))
open(dp, 'w', encoding='utf-8', newline='').write(d)
print('patched DESIGN.md')

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)
print(f'registry: 8 rows added, {SLUG} linked to {len(USED)} rows; page-map row updated')
