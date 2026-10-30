#!/usr/bin/env python3
"""CMB-022 registry, page map, the image gate, DESIGN.md and styles.css for /us-obesity-statistics/ (sources read in chat
2026-10-29).
usage: patch_cmb022.py REPO_ROOT"""
import sys, os, csv, io

ROOT = sys.argv[1]
SLUG = 'us-obesity-statistics'

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

# The page now also cites these rows.
USED = ('lancet-clinical-obesity-2025', 'cdc-brfss-state-obesity', 'nhanes-2021-2023-exam-files')

NOTES = {
    'nhanes-2021-2023-exam-files': (
        ' CMB-022: /us-obesity-statistics/ prints, from research/home-build/home_stats.json, class 1 obesity 20.6% and class 2 '
        '10.3% (adults 20+, pregnant women excluded; the code reproduces NCHS\'s crude 1.6 / 32.1 / 40.3 / 9.4) and the mean BMI of '
        'all adults 29.7; and, from research/us-obesity-statistics-build/obs_stats.py, the share weighing 300 lb (136.1 kg as '
        'recorded) or more: 2.87% [2.40, 3.34] of 5,942 examined adults with a measured weight, men 4.05% [3.05, 5.04], women '
        '1.74% [1.29, 2.19] (Taylor linearization, 15 df), printed as 2.9% / about 3%, 4% and 2%. obs_stats.py re-derives the '
        'class split and the mean with its own code and asserts them equal. The CMB-022 fact-check reproduced all of them '
        'independently (20.55 / 10.29 / 29.68; 2.87 / 4.05 / 1.74).'),
    'nhanes-adult-weight-trends': (
        ' CMB-022 (re-read 2026-10-29): Table 1 "All" rows typed in again for ages 20-74 (15 periods) and 20+ (12 periods), '
        'all equal to us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv; "Because surveys before 1988 did not '
        'include people older than age 74"; "at a given BMI level, body fat may vary by sex, age, and race and Hispanic '
        'origin"; "health risks may begin at a lower BMI among Asian people"; "research suggests that BMI overestimates '
        'adiposity (body fat) among Black people at a given BMI compared with others"; "a new sample design with no '
        'oversampling by race and Hispanic origin"; "Age adjusted by the direct method to the U.S. Census 2000 estimates using '
        'the age groups 20-39, 40-59, and 60 and older"; "height and weight are measured by trained technicians in a mobile '
        'examination center"; published February 25, 2026 (Fryar, Afful, Saif). The 2017-2018 set (30.7 / 42.4 / 9.2) is the '
        'one the NIDDK statistics page still shows. Its main text says surveys before 1988 "did not include people older than '
        'age 74", but footnote 2 says the 1960-1962 NHES covered ages 18-79 (the page\'s CSV notes it): only the 1971-1974 and '
        '1976-1980 surveys stopped at 74, which is how /us-obesity-statistics/ words it (CMB-022 fact-check). Age adjustment '
        'uses 20-39, 40-59 and 60-74 for the 20-74 series. Overweight, ages 20-74, ranges 30.3 (2017-2018) to 34.4 (2001-2002), '
        'never "near 31%" except at the two ends; 2017-2018 obesity (42.8, SE 1.9; 20+: 42.4, 1.8) is not significantly above '
        '2021-2023 (40.8, 2.0; 40.3, 1.9), so the page says "highest estimate", not "peak".'),
    'nhanes-adult-obesity-2021-2023': (
        ' CMB-022 (re-read 2026-10-29): "Following a pause in data collection in March 2020 due to the COVID-19 pandemic, '
        'field operations resumed in August 2021"; "No significant differences between men and women were seen in obesity '
        'prevalence by education level." (men 43.3 / 43.0 / 31.1, women 46.0 / 46.9 / 31.9); tables: 5,929 adults age 20 and '
        'older; Figure 4 (age-adjusted) obesity 37.7 / 39.6 / 41.9 / 40.3 and severe obesity 7.7 / 7.7 / 9.2 / 9.7 for '
        '2013-2014, 2015-2016, 2017-March 2020 and Aug 2021-Aug 2023, the decade change in obesity and the change between the '
        'last two cycles not significant, the rise in severe obesity significant.'),
    'nhanes-child-weight-trends': (
        ' CMB-022 (re-read 2026-10-29): title "Prevalence of Overweight, Obesity, and Severe Obesity Among Children and '
        'Adolescents Ages 2-19 Years: United States, 1963-1965 Through August 2021-August 2023" (Noiman, Fryar, Saif, Afful; '
        'the suggested citation says "2025 Feb", the page date is February 25, 2026); ages 2-19 overweight / obesity / severe '
        '15.1 / 21.1 / 7.0, boys 13.0 / 23.0 / 7.8, girls 17.5 / 19.1 / 6.3; obesity at 2-5, 6-11 and 12-19: 14.9 / 22.1 / '
        '22.9; 1971-1974 obesity 5.2 (SE 0.3).'),
    'nhanes-underweight': (
        ' CMB-022 (re-read 2026-10-29): adults 20+ crude 1.6 (men 1.1, women 2.0), age-adjusted 1.6 (women 2.1); ages 20-74 '
        'age-adjusted 4.0 (1960-1962) and 1.7 (Aug 2021-Aug 2023); "The unweighted examination response rate for all '
        'participants was 25.6% in August 2021-August 2023."'),
    'gallup-self-reported-obesity': (
        ' CMB-022 (the 2025 article re-read 2026-10-29): "combined data from three nationally representative surveys of '
        '16,946 U.S. adults" "interviewed by web in the first three quarters of 2025" (Feb. 18-26, May 27-June 4, Aug. 26-Sept. '
        '3); men 35.2%, women 38.8% in 2025; "A “vanity effect” in how respondents present themselves may explain why '
        'Gallup’s obesity estimates are typically somewhat lower". The article links no newer Gallup obesity piece; the '
        '2026 update stays excluded. The fact-check (2026-10-30) read Gallup\'s July 7, 2026 article (reweighted September 8, '
        '2026): 36.8% "thus far in 2026"; still excluded (its table and text disagreed when last checked), so the page quotes '
        '2025, the latest full year. The vanity-effect sentence ends "than those obtained from studies that use randomized '
        'clinical measurements".'),
    'cdc-brfss-state-obesity': (
        ' CMB-022 (maps page re-read 2026-10-29: published May 15, 2024, updated and reviewed September 24, 2026): "21 states, '
        'Guam, and Puerto Rico had an obesity prevalence between 35% and less than 40%."; "No state or territory had an obesity '
        'prevalence of 40% or higher."; the District of Columbia 24.2%; regions Midwest 35.5, South 34.8, West 30.7, Northeast '
        '29.6; no national figure on the page. /us-obesity-statistics/ quotes, from the 2011-2025 CSV this row serves, the 2025 '
        'range (DC 24.2 to Alabama 39.7), the top three (Alabama 39.7, North Dakota 39.1, Kentucky 38.8), Mississippi 40.4 in '
        '2024 with no 2025 estimate, and the states at 40% or higher (2024 Mississippi and West Virginia, 2025 none).'),
    'lancet-clinical-obesity-2025': (
        ' CMB-022 (the paper\'s text read 2026-10-29 from a copy of the article; King\'s College London release of January 15, '
        '2025): Table 1, statement 14: excess adiposity confirmed by direct body fat measurement, or "At least one '
        'anthropometric criteria (waist circumference, waist-to-hip ratio or waist-to-height ratio)" in addition to BMI, or '
        '"At least two anthropometric criteria (waist circumference, waist-to-hip ratio or waist-to-height ratio) regardless '
        'of BMI"; "In people with very high BMI (ie, >40 kg/m²), however, excess adiposity can pragmatically be '
        'assumed"; no numeric cut-offs: "Validated methods and age- gender- and ethnicity-appropriate cut-off points should '
        'be used for all anthropometric criteria." The KCL release says 56 experts; the paper says 58 (the site uses the '
        'paper\'s). Studies that apply it to US adults pick their own cut-offs: fourman-2025-all-of-us-new-definition (68.6%), '
        'alroub-2025-nhanes-new-definition (75.2%).'),
}

NEW = [
    {'domain': 'fourman-2025-all-of-us-new-definition',
     'source': ('Fourman LT, Awwad A, Gutierrez-Sacristan A, Dash CA, Johnson JE, Thistle AK, Chahal N, Stockman SL, Toribio '
                'M, Anekwe C, Gattu AK, Grinspoon SK. Implications of a New Obesity Definition Among the All of Us Cohort. '
                'JAMA Netw Open 2025;8(10):e2537619'),
     'publisher': 'JAMA Network Open (American Medical Association)',
     'url': 'https://doi.org/10.1001/jamanetworkopen.2025.37619',
     'endpoint': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12529213/',
     'access': 'page', 'license': 'Open access article; facts cited with attribution', 'tier': 'A', 'cadence': 'static',
     'granularity': 'cohort-level prevalence', 'format': 'article', 'key_required': 'no',
     'attribution': 'Fourman et al., JAMA Netw Open 2025',
     'verified_date': '2026-10-29', 'next_check': '2027-10-29',
     'coverage': ('301,026 participants of the NIH All of Us Research Program aged 18-80 with complete physical '
                  'measurements and EHR data, enrolled May 31, 2017 to September 30, 2023 (median follow-up 4.0 years): '
                  'obesity under the 2025 Lancet Commission definition against the BMI-based one'),
     'sample_note': ('Read 2026-10-29 (PMC12529213; published October 15, 2025): new-definition obesity 206,361 (68.6%) '
                     'against BMI-based 128,992 (42.9%); anthropometric-only obesity 78,047 (25.9% of the cohort); clinical '
                     'obesity 108,650 (36.1% of the cohort, 52.7% of those with obesity); ages 18-29 43.9%, 70 and older '
                     '78.3%. The anthropometric cut-offs are in the supplement (eMethods, not read); WHO race-specific BMI '
                     'cut-offs used. Mass General Brigham release (October 15, 2025): obesity as "a high BMI plus at least '
                     'one elevated anthropometric measure", or "a normal BMI and at least two elevated anthropometric '
                     'measures". CMB-022 fact-check (2026-10-30): the cohort is not weighted to the US population (61.0% '
                     'female; Black or African American participants somewhat overrepresented), and its BMI-based 42.9% '
                     'used race-specific BMI cut-offs per WHO criteria; the authors argue generalizability because it '
                     '"closely aligns with" CDC\'s 40.3%.'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-022: the 68.6% in the AI Overviews (cited there via the Harvard Gazette, which '
               'research/us-obesity-build/BUILD.md bars) traced to the paper. /us-obesity-statistics/ gives 68.6% with the '
               'cohort, the ages, the BMI-only 42.9% in the same people and the 36.1% with clinical obesity; it does not '
               'compare the cohort with NHANES point for point.')},
    {'domain': 'alroub-2025-nhanes-new-definition',
     'source': ('Al-Roub NM, Malik D, Essa M, Lu Y, Yang H, Spatz ES, Krumholz HM, Faridi KF. Body Mass Index and '
                'Anthropometric Criteria to Assess Obesity. JAMA Netw Open 2025;8(12):e2549124 (Research Letter)'),
     'publisher': 'JAMA Network Open (American Medical Association)',
     'url': 'https://doi.org/10.1001/jamanetworkopen.2025.49124',
     'endpoint': 'https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843225',
     'access': 'page', 'license': 'Open access article; facts cited with attribution', 'tier': 'A', 'cadence': 'static',
     'granularity': 'national (NHANES), survey-weighted', 'format': 'article', 'key_required': 'no',
     'attribution': 'Al-Roub et al., JAMA Netw Open 2025',
     'verified_date': '2026-10-29', 'next_check': '2027-10-29',
     'coverage': ('NHANES 2017-March 2020 and August 2021-August 2023: 14,414 adults representing 237.7 million; obesity '
                  'under the 2025 Lancet Commission criteria with a waist-to-height ratio above 0.5 as a criterion (0.6 as an '
                  'alternative)'),
     'sample_note': ('Read 2026-10-29 (published online December 29, 2025): "The study included 14 414 participants '
                     'representing 237 700 000 US adults."; "Survey-weighted obesity prevalence was 75.2% (95% CI, '
                     '73.8%-76.5%) overall."; "39.9% (95% CI, 38.0%-41.0%) of all adults had BMI of 30 or greater."; "A '
                     'waist-to-height ratio >0.5 was considered a criterion for obesity in the primary analysis."; "The most '
                     'common abnormal anthropometric criterion was WHtR above 0.50 (80.0% [95% CI, 78.6%-81.3%] of adults)"; '
                     'elevated waist-to-hip ratio 73.1%, waist circumference 58.3%; "Prevalence did not change from 2017-2020 '
                     'to 2021-2023." The table columns: BMI <30 plus 2 anthropometric criteria, BMI 30 to <40 plus 1, BMI '
                     '>=40. With a waist-to-height ratio above 0.6 instead of 0.5: 58.4% (95% CI, 56.7%-60.2%).'),
     'status': 'verified', 'pages_served': SLUG,
     'notes': ('CMB-022: the "75%" in the AI Overviews. The text and the table disagree for the BMI <25 and 25-29.9 '
               'subgroups (38.5% against 36.9%; 80.4% against 79.5%): no page uses those. The waist circumference and '
               'waist-to-hip cut-offs are in eTable 2 (not read).')},
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
            txt = NOTES[d]
            assert txt.strip() not in r[ix['notes']], d
            r[ix['notes']] = (r[ix['notes']] + txt) if r[ix['notes']] else txt.strip()
            noted.add(d)
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
            assert r[ix['data_source']] == 'nhanes-adult-weight-trends'
            assert r[ix['wedge']] == '60-year NHANES trend + sex/age splits in one embeddable chart (link magnet)'
            r[ix['wedge']] = ('The 60-year NHANES trend as the hero (adults 20-74, age-adjusted: obesity 13.4% in 1960-1962 to '
                              '40.8% in 2021-2023), with the CSV and the embeddable chart kept (the link magnet), and one '
                              'table of what each figure in the search results counts: 40.3% / 41.9% / 42.4% weighed and '
                              'measured (NHANES, three periods), 37.0% (Gallup) and 24.2-39.7% (CDC state surveys) '
                              'self-reported, 68.6% (All of Us, Fourman 2025) and 75.2% (NHANES 2017-2023, Al-Roub 2025) '
                              'under the 2025 Lancet Commission definition; counts by BMI category with the class 1 / 2 split '
                              '(our calculation); the Where-do-you-fit tool (built CMB-022)')
            r[ix['notes']] = ('Built Sep 30, 2026; D-14 rebuild CMB-022 (research/us-obesity-statistics-build/); also cites '
                              'nhanes-adult-obesity-2021-2023, nhanes-child-weight-trends, nhanes-underweight, '
                              'nhanes-anthropometric-reference, nhanes-population-totals, gallup-self-reported-obesity, '
                              'cdc-brfss-state-obesity, cdc-adult-bmi-categories, lancet-clinical-obesity-2025, '
                              'fourman-2025-all-of-us-new-definition and alroub-2025-nhanes-new-definition. Owns "obesity rate '
                              'in us" (14.8k) and 471 more keywords, 100,830/mo; state questions get a short answer and a link '
                              'to /obesity-rate-by-state/, children to /childhood-obesity-statistics/. Dataset schema and the '
                              'embed snippet (unchanged) kept.')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/blog/how-to-measure-body-fat/': 'how-to-measure-body-fat'}"
assert c.count(old) == 1
c = c.replace(old, "             '/blog/how-to-measure-body-fat/': 'how-to-measure-body-fat',\n"
                   "             '/us-obesity-statistics/': 'us-obesity-statistics'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)

# The embeddable chart: the site's category colours (DESIGN.md "The Category Lock"); same URL, data, size and text.
vp = os.path.join(ROOT, 'us-obesity-statistics/us-obesity-trend-1960-2023.svg'); v = open(vp, encoding='utf-8', newline='').read()
OLDC = ('.cmbv-ow{stroke:#E0A526}.cmbv-ob{stroke:#E0612D}.cmbv-sev{stroke:#9E1B1B}.cmbv-owf{fill:#E0A526}.cmbv-obf{fill:#E0612D}'
        '.cmbv-sevf{fill:#9E1B1B}.cmbv-owt{fill:#8A5A00}.cmbv-obt{fill:#B3431A}.cmbv-sevt{fill:#8E1B1B}')
NEWC = ('.cmbv-ow{stroke:#f59e0b}.cmbv-ob{stroke:#ef4444}.cmbv-sev{stroke:#991b1b}.cmbv-owf{fill:#f59e0b}.cmbv-obf{fill:#ef4444}'
        '.cmbv-sevf{fill:#991b1b}.cmbv-owt{fill:#b45309}.cmbv-obt{fill:#b91c1c}.cmbv-sevt{fill:#991b1b}')
assert v.count(OLDC) == 1 and not any(c in v.replace(OLDC, '') for c in ('#E0A526', '#E0612D', '#9E1B1B', '#8A5A00', '#B3431A', '#8E1B1B'))
v = v.replace(OLDC, NEWC)
TXT = [('Age-adjusted percent of US adults ages 20 to 74, measured by NHANES.',
        'Age-adjusted percent of US adults ages 20 to 74, measured by NHES (1960–1962) and NHANES.'),
       ('Overweight stayed near 31% (31.5% to 31.3%).',
        'Overweight stayed between 30.3% and 34.4% (31.5% in 1960–1962, 31.3% in August 2021–August 2023).'),
       ('Adults ages 20–74, age-adjusted percent, measured (NHANES)</text>',
        'Adults ages 20–74, age-adjusted percent, measured (NHES, NHANES)</text>')]
for a, b in TXT:
    assert v.count(a) == 1, a
    v = v.replace(a, b)
open(vp, 'w', encoding='utf-8', newline='').write(v)

# The CSV: the two HE-Stat 119 rows for ages 20-74 gain their standard errors (0.2 and 0.3; fact-check NOTE 14), in the
# S1 dataset builder and in the CSV it writes (the builder reproduces the CSV byte for byte; only these two rows change).
bd = os.path.join(ROOT, 'research/us-obesity-build/research/build_dataset_us_obesity.py'); bs = open(bd, encoding='utf-8', newline='').read()
SEFIX = [('"underweight",4.0,"","age-adjusted","ages 20-74; used for calculated healthy-weight share"',
          '"underweight",4.0,0.2,"age-adjusted","ages 20-74; used for calculated healthy-weight share"'),
         ('"underweight",1.7,"","age-adjusted","ages 20-74; used for calculated healthy-weight share"',
          '"underweight",1.7,0.3,"age-adjusted","ages 20-74; used for calculated healthy-weight share"')]
for a, b in SEFIX:
    assert bs.count(a) == 1, a
    bs = bs.replace(a, b)
open(bd, 'w', encoding='utf-8', newline='').write(bs)
cf = os.path.join(ROOT, 'us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv'); cs = open(cf, encoding='utf-8', newline='').read()
CSVFIX = [('HE119_underweight,adults,20-74,all,all,all,1960-1962,1961.5,underweight,4.0,,age-adjusted,',
           'HE119_underweight,adults,20-74,all,all,all,1960-1962,1961.5,underweight,4.0,0.2,age-adjusted,'),
          ('HE119_underweight,adults,20-74,all,all,all,Aug 2021-Aug 2023,2022.6,underweight,1.7,,age-adjusted,',
           'HE119_underweight,adults,20-74,all,all,all,Aug 2021-Aug 2023,2022.6,underweight,1.7,0.3,age-adjusted,')]
for a, b in CSVFIX:
    assert cs.count(a) == 1, a
    cs = cs.replace(a, b)
open(cf, 'w', encoding='utf-8', newline='').write(cs)

# The S1 build record: a pointer to the current one (its "no FAQPage" rule and the number audit's <article> scope changed).
bp = os.path.join(ROOT, 'research/us-obesity-build/BUILD.md'); b = open(bp, encoding='utf-8', newline='').read()
first = '# BUILD \u2014 /us-obesity-statistics/ \u00b7 calculatemybmi.net\n'
assert b.startswith(first) and 'CMB-022' not in b
b = b.replace(first, first + ('> CMB-022 (D-14 rebuild): the page was rebuilt; `research/us-obesity-statistics-build/SPEC.md` is the current build '
                              'record and `gen_obs.py` its generator. This file is the S1 build of 30 Sep 2026. Changed since: the page now carries '
                              'FAQPage JSON-LD (D-14), has no `<article class="cmb-stats">` wrapper (D-16), and `tools/number_audit.py` scans '
                              '`<main>`; the never-cite list in rule 2 still applies.\n'), 1)
open(bp, 'w', encoding='utf-8', newline='').write(b)

# DESIGN.md: the tool on the shared calculator parts and the embed-code box.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and '.obw' not in d and 'embed-code' not in d
d = d.replace(anchor, (
    '### US obesity tool and embed code (CMB-022)\n'
    '- `/us-obesity-statistics/` puts "Where do you fit?" on the shared calculator parts, with no page-level style: '
    '`.calculator-card.obw` › `.calc-panel` › `.unit-toggle` (ft, in, lb / cm, kg; `aria-pressed`) › one `.form-row.form-row--trio` '
    '(feet, inches, pounds; two columns under 360 px) or one `.form-row.form-row--pair` (centimeters, kilograms) › `.calculate-btn`. The card follows its '
    '`.content-section`; rows hide with the `hidden` attribute (`.obw [hidden]`).\n'
    '- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the CDC category with the BMI in the '
    'strong shade, the category, and its share of US adults with the count; then an `.er-section` with an `h3` and an '
    '`.er-table` of the six categories (`.cat-dot`, share, adults) where the user\'s row is `.er-active` with an `.er-you` '
    'pill. The BMI is rounded once to 0.1 (as `calculator.js`); the unit switch converts to 0.1 and restores the entered '
    'numbers when switched back with nothing retyped (the CMB-020 rule).\n'
    '- Embed code for a chart others may reuse: a read-only `textarea.embed-code` (system monospace, `--gray-50` ground, '
    'hairline border, resizable) under a `.form-label`, and a `button.cta-button.cta-button--sm` that copies it. '
    '`button.cta-button` drops the browser\'s button border.\n'
    '- Four-column number tables (`.data-table--fit.data-table--wrap`) fit a 320 px phone: under 360 px their cells keep 4 px '
    'beside the text (group heading rows keep 8 px), and a long single-word column heading carries a soft hyphen '
    '(`Over&shy;weight`) so it can break.\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)

# styles.css: the tool's hidden rows and the embed-code box (no page-level style).
sp = os.path.join(ROOT, 'assets/css/styles.css'); st = open(sp, encoding='utf-8', newline='').read()
assert '.obw' not in st and 'embed-code' not in st and 'button.cta-button' not in st
st = st.rstrip('\n') + '\n' + (
    '\n/* CMB-022 — /us-obesity-statistics/ (DESIGN.md "US obesity tool and embed code (CMB-022)"): the tool\'s US / metric\n'
    '   rows hide with the hidden attribute (.form-row sets display: grid); the embed code sits in a read-only textarea; a\n'
    '   <button> styled as .cta-button drops the browser\'s border; under 360 px, cells of .data-table--wrap tables keep 4 px\n'
    '   beside their text, so the four-column tables fit a 320 px phone. */\n'
    '.obw [hidden] { display: none; }\n'
    '.embed-code { display: block; width: 100%; min-height: 7.5rem; margin: 0.375rem 0 0.75rem; padding: 0.75rem; '
    'font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.8125rem; line-height: 1.5; '
    'color: var(--gray-800); background: var(--gray-50); border: 1px solid var(--gray-300); border-radius: var(--radius-md); '
    'resize: vertical; }\n'
    '.embed-code:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-bg); }\n'
    'button.cta-button { border: 0; cursor: pointer; }\n'
    '@media (max-width: 359px) { .flow .data-table--wrap th:not([colspan]), .flow .data-table--wrap td { padding-left: 0.25rem; '
    'padding-right: 0.25rem; } }\n')
open(sp, 'w', encoding='utf-8', newline='').write(st)
print('patched: registry', len(USED), 'rows linked,', len(NOTES), 'noted,', len(NEW), 'new; page map; check_images PREFERRED; '
      'embeddable chart colours; BUILD.md pointer; DESIGN.md; styles.css .obw/.embed-code/button.cta-button')
