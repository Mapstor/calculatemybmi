#!/usr/bin/env python3
"""US obesity statistics page checks in Chromium (CMB-022). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/us-obesity-statistics-build/obs_test_playwright.py http://localhost:8000 research/us-obesity-statistics-build/obs_sources.json
  - typed-in values: NCHS Health E-Stat 111 Table 1 (ages 20-74, 15 surveys; 20 and older, 12 surveys) and Table 3, Data
    Brief 508 (age and sex, severe obesity, education, Figure 4), Health E-Stats 112 and 119, Series 3 No. 50, the
    population totals, against the page's CSV; Gallup, Fourman et al., Al-Roub et al. and the Lancet Commission against
    obs_sources.json; the CDC state file (2025 top three, DC, Mississippi, the states at 40% or more); home_stats.json's
    class 1 and 2 split and mean BMI;
  - the arithmetic, done again here: counts (share x population), healthy weight by subtraction, the ratios the prose
    states, and the comparisons it makes (CDC-significant, or more than twice the standard error);
  - the prose: each sentence that states a number is rebuilt here from those values and found on the page (FAQ answers
    included); removed wording stays removed;
  - tables: all nine, cell by cell (the "why" table by group); figures: the hero's 45 dots, three lines, legend and
    labels at their drawn positions and the category bars' widths, with titles and descriptions; the embeddable chart
    loads and the embed code is the one sites were given;
  - the "Where do you fit?" tool: the starting values, a case in each of the six categories in both units, the BMI 25.0
    rounding edge both ways, the unit round trip, out-of-range messages, the table row marked "You", the Enter key;
  - head: title kept, description, robots, canonical, og:image and twitter:image = the 16:9 preferred image, twitter title
    and description, JSON-LD (Article: image list, primaryImageOfPage, dateModified = sitemap lastmod, datePublished kept,
    author and publisher named, citations in the registry; the Dataset with its CSV and license; BreadcrumbList;
    FAQPage = the visible answers), preferred files at size, old OG image gone, sitemap image entry, no {TODAY}, no
    page-level style, no <article>, no inline style outside figures; the menu marks this page only;
  - every internal link answers 200, every anchor exists, every outside link is a registry URL and opens in a new tab;
    chips land on their sections; every FAQ opens;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px and every table fits its frame; rendered SVG
    labels don't overlap, stay inside their figure and sit on no shape, line or plotted line; no JavaScript error."""
import sys, os, json, math, re, csv, struct, html
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, srcs = sys.argv[1], sys.argv[2]
BUILD = os.path.dirname(os.path.abspath(srcs))
ROOT = os.path.abspath(os.path.join(BUILD, '..', '..'))
SR = json.load(open(srcs, encoding='utf-8'))
HS = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
OS = json.load(open(os.path.join(BUILD, 'obs_stats.json')))
CSVROWS = list(csv.DictReader(open(os.path.join(ROOT, 'us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv'), encoding='utf-8')))
STATES = list(csv.DictReader(open(os.path.join(ROOT, 'research/state-obesity/cdc-brfss-adult-obesity-by-state-2011-2025.csv'), encoding='utf-8')))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ') if e.strip()}
URL = base + '/us-obesity-statistics/'
SITE = 'https://calculatemybmi.net'

def D(x): return Decimal(str(x))
def whole(x): return int(D(x).quantize(Decimal(1), rounding=ROUND_HALF_UP))
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def norm(t): return re.sub(r'\s+', ' ', t.replace('\u00a0', ' ').replace('\u00ad', '')).strip()
def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# ---- NCHS values typed in again (read live 2026-10-29)
T74 = [('1960-1962', 1961.5, '31.5', '13.4', '0.9'), ('1971-1974', 1973.0, '32.7', '14.5', '1.3'), ('1976-1980', 1978.5, '32.1', '15.0', '1.4'),
       ('1988-1994', 1991.5, '32.6', '23.2', '3.0'), ('1999-2000', 2000.0, '33.6', '30.9', '5.0'), ('2001-2002', 2002.0, '34.4', '31.2', '5.4'),
       ('2003-2004', 2004.0, '33.4', '32.9', '5.1'), ('2005-2006', 2006.0, '32.2', '35.1', '6.2'), ('2007-2008', 2008.0, '33.6', '34.3', '6.0'),
       ('2009-2010', 2010.0, '32.7', '36.1', '6.6'), ('2011-2012', 2012.0, '33.3', '35.3', '6.6'), ('2013-2014', 2014.0, '31.9', '38.2', '8.1'),
       ('2015-2016', 2016.0, '31.0', '40.0', '8.0'), ('2017-2018', 2018.0, '30.3', '42.8', '9.6'), ('Aug 2021-Aug 2023', 2022.6, '31.3', '40.8', '10.2')]
T20 = {'1988-1994': ('33.1', '22.9', '2.8'), '2013-2014': ('32.5', '37.7', '7.7'), '2015-2016': ('31.6', '39.6', '7.7'),
       '2017-2018': ('30.7', '42.4', '9.2'), 'Aug 2021-Aug 2023': ('31.7', '40.3', '9.7')}
OW_SEX = ('35.5', '28.1')
CRUDE = ('32.1', '40.3', '9.4')                      # overweight, obesity, severe obesity; adults 20+, 2021-2023
DB_OB = {'all': ('40.3', '35.5', '46.4', '38.9'), 'men': ('39.2', '34.3', '45.4', '38.0'), 'women': ('41.3', '36.8', '47.4', '39.6')}
DB_SV = {'all': ('9.4', '9.5', '12.0', '6.6'), 'men': ('6.7', '6.1', '9.2', '4.3'), 'women': ('12.1', '13.0', '14.7', '8.4')}
DB_ED = {'all': ('44.6', '45.0', '31.6'), 'men': ('43.3', '43.0', '31.1'), 'women': ('46.0', '46.9', '31.9')}
DEC = [('2013–2014', '37.7', '7.7'), ('2015–2016', '39.6', '7.7'), ('2017–March 2020', '41.9', '9.2'), ('Aug 2021–Aug 2023', '40.3', '9.7')]
RACE = [('Asian, non-Hispanic', '13.1', '17.8', None), ('Black, non-Hispanic', '52.1', '47.3†', '56.0'),
        ('White, non-Hispanic', '39.3', '38.3', '40.4'), ('Hispanic', '44.0', '43.6', '44.6'), ('Mexican American', '48.0', '44.2', None)]
KIDS = {'all': ('21.1', '7.0', '15.1'), 'boys': ('23.0', '7.8', '13.0'), 'girls': ('19.1', '6.3', '17.5')}
KAGE, K1971 = ('14.9', '22.1', '22.9'), '5.2'
UW, UW74 = '1.6', ('4.0', '1.7')
S3 = {'mean': ('29.4', '30.0'), 'median': ('28.2', '28.3'), 'p95lb': ('290.6', '262.7'), 'p95kg': ('131.8', '119.2')}
POP_A, POP_K = 245061169, 74908988
CLASS = ('20.6', '10.3'); MEAN_ALL = '29.7'; NEX = 5929

def csvv(ds, per, m, sex='all', group='all', age=None):
    h = [r for r in CSVROWS if r['dataset'] == ds and r['survey_period'] == per and r['measure'] == m and r['sex'] == sex
         and r['group'] == group and (age is None or r['age_group'] == age)]
    return h[0]['percent'] if len(h) == 1 else None
ok(len(CSVROWS) == 585, 'CSV rows')
# the Dataset description's periods by age: children 6-11 from 1963-1965, teens 12-17 in 1966-1970 (filed under 12-19 with a
# note), ages 2-19 from 1971-1974; adults from 1960-1962
ok([(r['age_group'], r['note']) for r in CSVROWS if r['survey_period'] in ('1963-1965', '1966-1970')] == [('6-11', ''), ('12-19', '1966-1970 value is ages 12-17, not 12-19')]
   and min(r['survey_period'] for r in CSVROWS if r['population'] == 'children and adolescents' and r['age_group'] == '2-19') == '1971-1974'
   and min(r['survey_period'] for r in CSVROWS if r['population'] == 'adults') == '1960-1962', 'CSV periods by age')
for per, mid, ow, ob, sv in T74:
    got = tuple(csvv('HE111_T1_adults_20-74', per, m) for m in ('overweight', 'obesity', 'severe obesity'))
    ok(got == (ow, ob, sv), f'CSV 20-74 {per}: {got}')
    ok(any(r['dataset'] == 'HE111_T1_adults_20-74' and r['survey_period'] == per and float(r['midpoint_year']) == mid for r in CSVROWS), f'midpoint {per}')
for per, v in T20.items():
    ok(tuple(csvv('HE111_T1_adults_20plus', per, m) for m in ('overweight', 'obesity', 'severe obesity')) == v, f'CSV 20+ {per}')
ok((csvv('HE111_T1_adults_20plus', 'Aug 2021-Aug 2023', 'overweight', sex='men'), csvv('HE111_T1_adults_20plus', 'Aug 2021-Aug 2023', 'overweight', sex='women')) == OW_SEX, 'overweight by sex')
ok(tuple(csvv('HE111_crude_snapshot', 'Aug 2021-Aug 2023', m) for m in ('overweight', 'obesity', 'severe obesity')) == CRUDE, 'crude snapshot')
AG = (('20+', 'all'), ('20-39', '20-39'), ('40-59', '40-59'), ('60+', '60+'))
for s in ('all', 'men', 'women'):
    ok(tuple(csvv('DB508_sex_age', 'Aug 2021-Aug 2023', 'obesity', sex=s, group=g, age=a) for a, g in AG) == DB_OB[s], f'DB 508 obesity {s}')
    ok(tuple(csvv('DB508_sex_age', 'Aug 2021-Aug 2023', 'severe obesity', sex=s, group=g, age=a) for a, g in AG) == DB_SV[s], f'DB 508 severe {s}')
    ok(tuple(csvv('DB508_education', 'Aug 2021-Aug 2023', 'obesity', sex=s, group=g) for g in
             ('High school diploma or less', 'Some college', "Bachelor's degree or more")) == DB_ED[s], f'DB 508 education {s}')
ok((csvv('DB508_fig4_trend', '2017-Mar 2020', 'obesity'), csvv('DB508_fig4_trend', '2017-Mar 2020', 'severe obesity')) == ('41.9', '9.2'), 'DB 508 2017-March 2020')
for g, a, m, w in RACE:
    ok((csvv('HE111_T3_obesity_by_race', 'Aug 2021-Aug 2023', 'obesity', group=g), csvv('HE111_T3_obesity_by_race', 'Aug 2021-Aug 2023', 'obesity', sex='men', group=g)) == (a, m.rstrip('†')), f'race {g}')
for s in ('all', 'boys', 'girls'):
    ok(tuple(csvv('HE112_T1_children_2-19', 'Aug 2021-Aug 2023', m, sex=s) for m in ('obesity', 'severe obesity', 'overweight')) == KIDS[s], f'kids {s}')
ok(tuple(csvv('HE112_T2_children_by_age', 'Aug 2021-Aug 2023', 'obesity', group=a, age=a) for a in ('2-5', '6-11', '12-19')) == KAGE, 'kids by age')
ok(csvv('HE112_T1_children_2-19', '1971-1974', 'obesity') == K1971, 'kids 1971-1974')
ok(csvv('HE119_underweight', 'Aug 2021-Aug 2023', 'underweight', age='20+') == UW, 'underweight')
ok((csvv('HE119_underweight', '1960-1962', 'underweight', age='20-74'), csvv('HE119_underweight', 'Aug 2021-Aug 2023', 'underweight', age='20-74')) == UW74, 'underweight 20-74')
# home_stats.json (our calculation): reproduces NCHS, the class split, the mean
ok(HS['reproduces_nchs_crude_prevalence']['ours'] == {'underweight': 1.6, 'overweight': 32.1, 'obesity': 40.3, 'obesity_class_3': 9.4}, 'home_stats reproduces NCHS')
ok((f'{HS["category_shares_pct"]["obesity_class_1"]:.1f}', f'{HS["category_shares_pct"]["obesity_class_2"]:.1f}') == CLASS, 'class split')
ok(f'{HS["adults"]["mean"]:.1f}' == MEAN_ALL and HS['adults']['bmi_n'] == NEX, 'mean BMI / n')
R3 = HS['reproduces_series3']
ok((str(R3['men_bmi_mean']), str(R3['women_bmi_mean']), str(R3['men_bmi_median']), str(R3['women_bmi_median']), str(R3['men_wt_p95_lb']), str(R3['women_wt_p95_lb']))
   == (*S3['mean'], *S3['median'], *S3['p95lb']), 'Series 3 No. 50 values')
# the other sources, typed in again
G, F4, AR, LC = SR['gallup_2025'], SR['fourman_2025'], SR['alroub_2025'], SR['lancet_2025']
ok((G['rate_2025'], G['peak'], G['peak_year'], G['n'], G['men_2025'], G['women_2025']) == ('37.0', '39.9', 2022, 16946, '35.2', '38.8'), 'Gallup')
ok((F4['new_definition'], F4['bmi_based'], F4['n'], F4['clinical'], F4['ages']) == ('68.6', '42.9', 301026, '36.1', '18 to 80'), 'Fourman')
ok((AR['new_definition'], AR['bmi_30_plus'], AR['whtr_over_05'][0], AR['n'], AR['represents']) == (['75.2', '73.8', '76.5'], ['39.9', '38.0', '41.0'], '80.0', 14414, 237700000), 'Al-Roub')
ok((LC['experts'], LC['organizations']) == (58, 76), 'Lancet Commission')
# CDC state file
def st(y, s): return [r for r in STATES if r['year'] == str(y) and r['state'] == s][0]
ok([st(2025, s)['prevalence_pct'] for s in ('Alabama', 'North Dakota', 'Kentucky', 'District of Columbia')] == ['39.7', '39.1', '38.8', '24.2'], 'states 2025')
NS = {'Guam', 'Puerto Rico', 'Virgin Islands', 'District of Columbia'}
s25 = sorted([r for r in STATES if r['year'] == '2025' and r['status'] == 'ok' and r['state'] not in NS], key=lambda r: -float(r['prevalence_pct']))
ok([r['state'] for r in s25[:3]] == ['Alabama', 'North Dakota', 'Kentucky'] and min(float(r['prevalence_pct']) for r in STATES if r['year'] == '2025' and r['status'] == 'ok') == 24.2, 'state ranks 2025')
ok(st(2024, 'Mississippi')['prevalence_pct'] == '40.4' and st(2025, 'Mississippi')['status'] == 'insufficient', 'Mississippi')
o40 = {y: sorted(r['state'] for r in STATES if r['year'] == str(y) and r['status'] == 'ok' and r['state'] not in NS and float(r['prevalence_pct']) >= 40) for y in (2024, 2025)}
ok(o40 == {2024: ['Mississippi', 'West Virginia'], 2025: []}, f'states at 40% {o40}')
o35 = {y: sum(1 for r in STATES if r['year'] == str(y) and r['status'] == 'ok' and r['state'] not in NS and float(r['prevalence_pct']) >= 35) for y in (2024, 2025)}
ok(o35 == {2024: 19, 2025: 21} and sum(1 for r in STATES if r['year'] == '2025' and r['status'] == 'ok' and r['state'] not in NS) == 47, f'states at 35% {o35}')
# our calculation, typed in from the chat run (the fact-check reproduced 2.87 / 4.05 / 1.74 with its own code)
L3 = OS['lb300']
ok((round(L3['all']['pct'], 2), round(L3['men']['pct'], 2), round(L3['women']['pct'], 2), L3['all']['n'], L3['men']['n'], L3['women']['n']) == (2.87, 4.05, 1.74, 5942, 2688, 3254), f'300 lb {L3}')
ok(OS['check_home_stats']['n_bmi'] == 5929 and round(OS['check_home_stats']['class_1_pct'], 1) == 20.6 and round(OS['check_home_stats']['mean_bmi'], 1) == 29.7, 'obs_stats cross-check')
ok(all(abs(r['pct'] % 1 - 0.5) > 0.05 for r in L3.values()) and abs((L3['all']['pct'] * 10) % 1 - 0.5) > 0.05, '300 lb near a rounding tie')
ok(min(float(x[2]) for x in T74) == 30.3 and max(float(x[2]) for x in T74) == 34.4, 'overweight range 20-74')

# ---- the arithmetic, done again here
def mil(share, pop=POP_A): return whole(D(share) * pop / Decimal(10 ** 8))
HEALTHY = str(D(100) - D(UW) - D(CRUDE[0]) - D(CRUDE[1]))
CATS = [('underweight', 'Underweight', 'under 18.5', UW), ('normal', 'Healthy weight', '18.5–24.9', HEALTHY),
        ('overweight', 'Overweight', '25.0–29.9', CRUDE[0]), ('obese', 'Class 1 obesity', '30.0–34.9', CLASS[0]),
        ('obese', 'Class 2 obesity', '35.0–39.9', CLASS[1]), ('obese-severe', 'Class 3 obesity', '40.0 or higher', CRUDE[2])]
CATS = [c + (mil(c[3]),) for c in CATS]
ok(HEALTHY == '26.0' and [c[4] for c in CATS] == [4, 64, 79, 50, 25, 23] and sum(D(c[3]) for c in CATS) == 100, 'categories')
OWOB = str(D(CRUDE[0]) + D(CRUDE[1]))
ok((mil(CRUDE[1]), mil(OWOB), OWOB) == (99, 177, '72.4'), 'obesity / overweight-or-obesity counts')
H60 = str(D(100) - D(UW74[0]) - D(T74[0][2]) - D(T74[0][3])); H23 = str(D(100) - D(UW74[1]) - D(T74[-1][2]) - D(T74[-1][3]))
ok((H60, H23) == ('51.1', '26.2'), 'healthy share 60-year change')
KM = str((D(KIDS['all'][0]) * POP_K / Decimal(10 ** 8)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
ok(KM == '15.8', 'children count')
ok(2.95 < 40.8 / 13.4 < 3.1 and 11 < 10.2 / 0.9 < 11.5 and 2 < 30.9 / 15.0 < 2.1 and 3.9 < 21.1 / 5.2 < 4.1 and 1.7 < 12.1 / 6.7 < 1.9, 'ratios')
ok(round(300 * 0.45359237) == 136, '300 lb')
def zz(a, sa, b, sb): return abs(a - b) / math.hypot(sa, sb)
TC = 2.131                                                          # t, 95%, 15 degrees of freedom
ok(zz(35.5, 1.4, 28.1, 0.9) > TC and zz(56.0, 3.4, 40.4, 2.0) > TC and zz(14.9, 1.3, 22.1, 2.0) > TC and zz(14.9, 1.3, 22.9, 1.7) > TC, 'stated comparisons hold')
ok(zz(23.0, 1.4, 19.1, 1.5) < TC and zz(52.1, 2.7, 44.0, 3.7) < TC, 'comparisons the page does not state')
ok(zz(42.8, 1.9, 40.8, 2.0) < TC and zz(42.4, 1.8, 40.3, 1.9) < TC, '2017-2018 vs 2021-2023 not significant (no "peak")')

# ---- the prose, rebuilt here
TOP = 'Alabama'
PROSE = [
    'What percentage of Americans are obese? Search for it and you can find 37%, 40.3%, 42.4% and 75% on the same results page.',
    'CDC’s National Health and Nutrition Examination Survey, which weighs and measures a national sample, puts it at 40.3% of adults for August 2021 to August 2023 (CDC).',
    f'40.3% of US adults have obesity, a BMI of 30 or higher: about {mil(CRUDE[1])} million people. That is CDC’s measured figure for adults 20 and older, '
    f'August 2021 to August 2023. Another 32.1% are overweight, so {OWOB}% have a BMI of 25 or more, and 9.4% have severe obesity, a BMI of 40 or higher.',
    'Obesity has about tripled since the early 1960s, from 13.4% to 40.8% of adults aged 20 to 74 (age-adjusted), while the share who are overweight stayed between 30% and 35%.',
    'No significant change in the measured data: CDC found the change from 41.9% (2017 to March 2020) to the latest 40.3% not statistically significant, and severe '
    f'obesity rose from 7.7% to 9.7% (age-adjusted) over the decade. Gallup’s self-reported rate fell from {G["peak"]}% in 2022 to {G["rate_2025"]}% in 2025.',
    'Highest at ages 40 to 59 (46.4%). Women and men have similar rates (41.3% and 39.2%), but severe obesity is almost twice as common in women (12.1% against 6.7%).',
    f'21.1% of children and teens aged 2 to 19 have obesity, about {KM} million, four times the 5.2% of 1971 to 1974.',
    f'The {F4["new_definition"]}% and {AR["new_definition"][0]}% figures use a new definition that adds waist measures to BMI. In the same people, BMI alone gave '
    f'{F4["bmi_based"]}% and {AR["bmi_30_plus"][0]}%.',
    f'About {mil(CRUDE[1])} million US adults had obesity in August 2021 to August 2023: 40.3% of the 245.1 million adults aged 20 and older that CDC’s survey '
    f'represents. About {mil(CRUDE[0])} million more were overweight, and about {mil(CRUDE[2])} million had severe obesity.',
    f'Only about 1 in 4 adults ({HEALTHY}%) has a BMI in the healthy range, fewer than have obesity. The typical adult is overweight: the median BMI is 28.2 for men '
    'and 28.3 for women, and the averages are 29.4 and 30.0 (CDC).',
    f'32.1% of US adults are overweight, a BMI of 25.0 to 29.9. Add the 40.3% with obesity and {OWOB}% have a BMI of 25 or higher, the figure behind claims that '
    'about 70% of Americans are overweight. Men are more often overweight than women, 35.5% against 28.1% (age-adjusted).',
    f'Unlike obesity, the overweight share ended where it started: 31.5% of adults aged 20 to 74 in 1960–1962 and 31.3% in 2021–2023 (age-adjusted), between 30% '
    f'and 35% in every survey. The healthy-weight share shrank instead, from {H60}% to {H23}% (our calculation from CDC’s figures).',
    'Adult obesity has about tripled since the early 1960s: 13.4% of adults aged 20 to 74 had obesity in 1960–1962 and 40.8% in 2021–2023 (age-adjusted). Severe '
    'obesity rose from 0.9% to 10.2%, 11 times as high.',
    'The fastest climb came between the late 1970s and 2000, when the rate doubled from 15.0% (1976–1980) to 30.9% (1999–2000). It kept rising more slowly, to '
    '42.8% in 2017–2018; the 40.8% of 2021–2023 is not significantly lower.',
    'CDC uses ages 20 to 74 for the long series because the 1971–1974 and 1976–1980 surveys did not include anyone older than 74.',
    'data collection paused in March 2020 for the pandemic and resumed in August 2021 (CDC’s 2017–March 2020 estimate is in the next section).',
    'For all adults 20 and older (from 1988–1994), obesity rose from 22.9% to 42.4% in 2017–2018 and was 40.3% in 2021–2023, not a significant change;',
    'CDC’s measured data show no significant change. The latest CDC estimate, 40.3% of adults 20 and older (age-adjusted), is below the 41.9% of 2017 to March '
    '2020, but CDC found neither that change nor the change over the decade since 2013–2014 (37.7%) statistically significant. Severe obesity did rise, from 7.7% '
    'to 9.7% (age-adjusted), and adult obesity remains above the Healthy People 2030 goal of 36.0% (CDC).',
    f'A survey where people give their own height and weight points down: the Gallup National Health and Well-Being Index put obesity at {G["peak"]}% in 2022 and '
    f'{G["rate_2025"]}% in 2025, with women at {G["women_2025"]}% and men at {G["men_2025"]}% (Gallup).',
    'CDC’s state surveys, also self-reported, show no clear change: 21 states were at 35% or higher in 2025 against 19 in 2024, and none reached 40% in 2025, but '
    'Mississippi (40.4% in 2024) had no 2025 estimate (CDC).',
    'Under the new definition that adds waist measures, one study found no change between 2017–2020 and 2021–2023 (Al-Roub et al., 2025).',
    'Each figure is right for what it counts. Three things move it: whether people were weighed or asked, which years and ages it covers, and which definition of obesity it uses.',
    'Gallup says a “vanity effect” in how people describe themselves may explain why its estimates usually run somewhat below measured ones.',
    f'CDC’s state figures are self-reported too, and every one of them in 2025, from 24.2% (the District of Columbia) to 39.7% ({TOP}), sits below the national '
    '40.3%: compare states with states, on the obesity rate by state page.',
    '42.4% (2017–2018) and 41.9% (2017 to March 2020) are CDC’s earlier figures, and neither is current. CDC’s adult figures start at age 20; Gallup and the state '
    'surveys include adults of 18 and 19. The 60-year series covers ages 20 to 74, which is why its latest value is 40.8%, not 40.3%.',
    'Crude shares are the actual shares of adults: in 2021–2023, 40.3% with obesity, 32.1% overweight and 9.4% with severe obesity. Age-adjusted shares are '
    'reweighted to the age mix of the 2000 census so that years and groups compare fairly: 40.3%, 31.7% and 9.7%.',
    f'In January 2025 the Lancet Commission on Clinical Obesity ({LC["experts"]} experts, endorsed by {LC["organizations"]} organizations) recommended confirming '
    'excess body fat instead of diagnosing obesity from BMI alone: a high BMI plus at least one waist measure above its cut-off (waist circumference, waist-to-hip '
    'ratio or waist-to-height ratio), at least two waist measures whatever the BMI, or a direct body fat measurement. Above a BMI of 40, it says excess fat can be '
    'assumed. It asks for validated cut-offs appropriate to age, sex and ethnicity (Rubino et al., 2025).',
    f'Applied to {F4["n"]:,} volunteers aged 18 to 80 in NIH’s All of Us program, a cohort not weighted to the US population, the new definition gave '
    f'{F4["new_definition"]}% against {F4["bmi_based"]}% by BMI with WHO’s race-specific cut-offs (Fourman et al., 2025). Applied to CDC’s 2017–2023 survey, with a '
    f'waist more than half the height counted as one criterion, it gave {AR["new_definition"][0]}% against {AR["bmi_30_plus"][0]}%; {AR["whtr_over_05"][0]}% of adults '
    f'had a waist more than half their height, and with 0.6 as the cut-off instead of 0.5 the study found {AR["whtr_06_definition"][0]}% (Al-Roub et al., 2025).',
    f'in All of Us, {F4["clinical"]}% had clinical obesity.',
    'Adults aged 40 to 59 have the highest rate, 46.4%, above both ages 20 to 39 (35.5%) and 60 and older (38.9%). The same middle-age peak shows in men and in women (CDC).',
    'Women and men have similar obesity rates, 41.3% and 39.2%, a difference CDC found not statistically significant. The gap is at the heavy end: 12.1% of women have '
    'severe obesity against 6.7% of men. Men are more often overweight (35.5% against 28.1%, age-adjusted).',
    'Adults with a bachelor’s degree or more have a lower rate (31.6%) than those with some college (45.0%) or a high school diploma or less (44.6%), and the last two '
    'don’t differ significantly. CDC found no significant differences between men and women at any education level.',
    'Age-adjusted obesity rates in 2021–2023 ranged from 13.1% among non-Hispanic Asian adults to 52.1% among non-Hispanic Black adults. They were 48.0% for Mexican '
    'American adults, 44.0% for Hispanic adults overall and 39.3% for non-Hispanic White adults. Among women, 56.0% of non-Hispanic Black women had obesity against '
    '40.4% of non-Hispanic White women.',
    'CDC points to research that health risks may begin at a lower BMI among Asian people, and that BMI overestimates body fat among Black people compared with others at the same BMI.',
    'the 2021–2023 survey used a new sample design with no oversampling by race and Hispanic origin; two estimates for women did not meet NCHS standards of '
    'reliability. CDC prints them flagged, and the table below leaves them out.',
    '* Left out: CDC flags the estimate as not meeting NCHS standards of reliability or precision.',
    f'9.4% of US adults have severe obesity, CDC’s term for a BMI of 40 or higher, also called class 3 obesity: about {mil(CRUDE[2])} million adults. It is almost '
    'twice as common in women (12.1%) as in men (6.7%), and women’s rate is higher in every age group. It is more common at ages 20 to 39 (9.5%) and 40 to 59 '
    '(12.0%) than at 60 and older (6.6%). Over 60 years it rose from 0.9% to 10.2% of adults aged 20 to 74 (age-adjusted).',
    f'21.1% of US children and teens aged 2 to 19 had obesity in August 2021 to August 2023, including 7.0% with severe obesity, and another 15.1% were overweight: '
    f'about {KM} million children and teens with obesity (our calculation).',
    'Obesity is lower at ages 2 to 5 (14.9%) than at 6 to 11 (22.1%) and 12 to 19 (22.9%). It was 23.0% among boys and 19.1% among girls. In 1971–1974, 5.2% of '
    'children and teens had obesity, about a quarter of the rate now.',
    'obesity means a BMI at or above the 95th percentile for their age and sex on CDC’s 2000 growth charts, and severe obesity 120% of that value or more.',
    f'Count: 21.1% × 74.9 million children aged 2 to 19 (CDC’s population total).',
    'The chart and the compiled data are free to reuse under CC BY 4.0: credit CalculateMyBMI and link to this page. The NCHS figures themselves are in the public domain.',
    'Download the data (CSV, 585 rows): the NCHS adult and child figures behind this page, with standard errors, survey years and the formula for each calculated value.',
    'Counts: share × 245.1 million adults (CDC’s population total for the survey), rounded to the nearest million.',
    f'The 2021–2023 adult figures rest on {NEX:,} examined adults aged 20 and older; the unweighted examination response rate, all ages, was 25.6%.',
    'Every rate comes from CDC’s examination surveys, the National Health Examination Survey for 1960–1962 and the National Health and Nutrition Examination Survey '
    '(NHANES) since 1971–1974, unless another source is named.',
    'age-adjusted shares are standardized to the 2000 census (ages 20 to 39, 40 to 59, and 60 and older; 60 to 74 for the 20-to-74 series).',
    'We call a difference higher or lower only where CDC reports it as statistically significant, or where it is more than 2.13 times its standard error (the 95% '
    'level for the survey’s 15 degrees of freedom), worked out from CDC’s published standard errors.',
    f'the split of obesity into classes 1 and 2, and the mean BMI of all adults, {MEAN_ALL}; the same code reproduces CDC’s published 1.6%, 32.1%, 40.3% and 9.4% exactly.',
    f'The share at 300 lb or more counts the {L3["all"]["n"]:,} examined adults with a measured weight (CDC’s body measures file).',
    'Shares from CDC, healthy weight by subtraction; the split of obesity into classes 1 and 2 is our calculation from CDC’s survey files.',
    # FAQ answers
    f'Yes. CDC’s measured survey put adult obesity at 40.3% in August 2021 to August 2023: about {mil(CRUDE[1])} million adults aged 20 and older had a BMI of 30 or higher.',
    f'Yes, if overweight includes obesity: {OWOB}% of US adults have a BMI of 25 or higher (32.1% overweight plus 40.3% with obesity). Overweight alone, a BMI of 25.0 to 29.9, is 32.1%.',
    'In CDC’s measured data the change from 41.9% (2017 to March 2020) to 40.3% (August 2021 to August 2023) was not statistically significant, and severe obesity '
    f'rose from 7.7% to 9.7% (age-adjusted) over the decade. Gallup’s self-reported rate fell from {G["peak"]}% in 2022 to {G["rate_2025"]}% in 2025.',
    'Alabama had the highest estimate in 2025, 39.7% of adults, followed by North Dakota (39.1%) and Kentucky (38.8%), within each other’s margins of error, in CDC’s '
    'state surveys, where people report their own height and weight. Mississippi, at 40.4% in 2024, had no 2025 estimate. The obesity rate by state page ranks every state.',
    '13.4% of adults aged 20 to 74 had obesity in 1960–1962 (age-adjusted), the earliest survey in CDC’s national series. In August 2021 to August 2023 it was 40.8%, '
    'about three times as high.',
    'Each survey covers two years or more, so there are no single-year figures.',
    'The Commission also splits obesity into clinical obesity, with signs of reduced organ function or a reduced ability to carry out daily activities, and preclinical obesity;',
    f'They use the definition the Lancet Commission proposed in 2025, which adds waist measures to BMI. Applied to {F4["n"]:,} volunteers in NIH’s All of Us program, '
    f'it gave {F4["new_definition"]}% ({F4["bmi_based"]}% by BMI alone); applied to CDC’s 2017–2023 survey, {AR["new_definition"][0]}% ({AR["bmi_30_plus"][0]}% by BMI '
    'alone). CDC’s own figure, 40.3%, uses BMI.',
    'Those are earlier CDC figures: 42.4% for 2017–2018 and 41.9% for 2017 to March 2020 (age-adjusted, adults 20 and older). The latest is 40.3% for August 2021 to August 2023.',
    f'29.4 for men and 30.0 for women aged 20 and older in August 2021 to August 2023, and {MEAN_ALL} for all adults (our calculation from CDC’s files); the medians '
    'are 28.2 for men and 28.3 for women. The typical adult’s BMI is in the overweight range.',
    'Adults aged 40 to 59: 46.4% had obesity in August 2021 to August 2023, more than at ages 20 to 39 (35.5%) or 60 and older (38.9%).',
    'Not overall: 41.3% of women and 39.2% of men had obesity, a difference CDC found not statistically significant. Severe obesity is almost twice as common in women, '
    '12.1% against 6.7%.',
    'About 3%: 2.9% of US adults weighed 300 lb (136 kg) or more in August 2021 to August 2023, about 4% of men and 2% of women (our calculation from CDC’s survey '
    'files). That fits CDC’s published 95th percentiles: 95% of men weighed 290.6 lb (131.8 kg) or less and 95% of women 262.7 lb (119.2 kg) or less.',
    f'About 1 in 4: {HEALTHY}% of adults 20 and older had a BMI of 18.5 to 24.9 in August 2021 to August 2023 (100% minus CDC’s underweight, overweight and obesity '
    f'shares). Among adults aged 20 to 74 (age-adjusted), the share fell from about half, {H60}% in 1960–1962, to {H23}%.',
]
REMOVED = ('cmb-', 'retrieved Sep 2026', 'Not in the measured data, at least not yet', 'is what shrank', 'research suggests health risks',
           'og-us-obesity-statistics', 'Harvard', 'heart.org', 'wikipedia', 'The Black–White gap is wider among women', 'highest among non-Hispanic Black',
           'It peaks at', 'Two cautions from NCHS', 'next NHANES cycle (2025–2027)', 'primary source of body measurement information',
           'Is it true that 70% of Americans are obese?', 'Surveys before 1988 didn’t include', 'which asks adults 18 and older to enter their own height',
           'Not falling in the measured data yet', 'so the estimates for smaller groups have wide margins', 'None between 2017–2018', 'and none between 2017–2018',
           'Gallup notes that self-reported figures tend to run lower', 'Home › US Obesity Statistics', '3×', 'The middle adult',
           'CDC’s first measured survey', 'Each survey covers about two years', 'every adult and child figure on this page', 'so each study picks its own',
           'rather than fixing one set', 'That is also why every state', 'cut short by the pandemic', 'The last two-year survey before that',
           'Surveys where people give their own height and weight point down', 'every CDC survey', 'peaked at', 'a peak of', 'stayed near 31%',
           'overweight flat', 'just ahead of', 'Fewer than 5% of adults', 'are not shown', '—*', 'surveys before 1988 did not include',
           'more than twice its standard error', 'participants aged 18 to 80', 'show no significant change yet', 'falling in the measured data yet',
           'one figure per state', 'has hardly moved', 'no state reached 40%')

EMBED_ALT = 'Line chart: US adult obesity rose from 13.4% in 1960–62 to 40.8% in 2021–23'
EMBED = ('<figure style="margin:0;max-width:640px"><img src="https://calculatemybmi.net/us-obesity-statistics/us-obesity-trend-1960-2023.svg" '
         f'alt="{EMBED_ALT}" width="640" height="440" loading="lazy" style="width:100%;height:auto"><figcaption>Chart: <a '
         'href="https://calculatemybmi.net/us-obesity-statistics/">CalculateMyBMI</a>. Data: CDC NCHS (NHES, NHANES).</figcaption></figure>')
TX0, TX1, TY0, TY1, YR0, YR1 = 34, 274, 28, 196, 1959, 2024
def tx(y): return TX0 + (y - YR0) * (TX1 - TX0) / (YR1 - YR0)
def ty(v): return TY1 - float(v) * (TY1 - TY0) / 50
SERC = {'obesity': '#ef4444', 'overweight': '#f59e0b', 'severe obesity': '#991b1b'}
def lab(p): return p.replace('-', '–')

with sync_playwright() as p:
    br = p.chromium.launch(args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 1280, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())     # no ads or analytics
    resp = pg.goto(URL, wait_until='load')
    ok(resp.status == 200, f'page status {resp.status}')
    raw = pg.content()
    faq_text = norm(' '.join(pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')))
    body = norm(pg.inner_text('main')) + ' ' + faq_text
    for s_ in PROSE: ok(norm(s_) in body, f'prose not found: {s_!r}')
    for s_ in REMOVED: ok(s_ not in body and s_ not in raw, f'removed wording back on the page: {s_!r}')
    src = pg.request.get(URL).text()
    ok('{TODAY}' not in src and '<style' not in src and '<article' not in src, 'template marker, page-level style or <article>')
    mains = src[src.index('<main'):src.index('</main>')]
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>', '', mains), 'inline style in <main> outside figures')
    ok(mains.startswith('<main class="reading"><div class="container">'), 'reading column')
    ok('—' not in norm(re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<svg.*?</svg>|<textarea.*?</textarea>|<script.*?</script>', '', mains))), 'em dash in the body')

    # Tables.
    tabs = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => ({cap: t.caption.textContent, cls: t.className,
        head: [...t.tHead.rows[0].cells].map(c => c.textContent),
        groups: [...t.tBodies].map(b => [...b.rows].map(r => [...r.cells].map(c => [c.tagName, c.getAttribute('scope'), c.getAttribute('colspan'), c.textContent])))}))""")
    ok(len(tabs) == 9, f'{len(tabs)} tables')
    def rows_of(t): return [[[c[0], c[1], c[2], norm(c[3])] for c in r] for b in t['groups'] for r in b]
    def simple(rows): return [[['TH', 'row', None, r[0]]] + [['TD', None, None, v] for v in r[1:]] for r in rows]
    T = {t['cap']: t for t in tabs}
    want = {
        'US adults by BMI category, August 2021–August 2023': (['BMI category', 'Share', 'Adults'], simple(
            [[f'{n}BMI {r}', f'{s}%', f'{m} million'] for _, n, r, s, m in CATS] +
            [['Obesity, all classesBMI 30.0 or higher', '40.3%', f'{mil(CRUDE[1])} million'], ['Overweight or obesityBMI 25.0 or higher', f'{OWOB}%', f'{mil(OWOB)} million']])),
        'US adults aged 20 to 74 by survey years, age-adjusted': (['Survey years', 'Overweight', 'Obesity', 'Severe obesity'], simple(
            [[lab(per).replace('Aug 2021', 'Aug 2021'), f'{ow}%', f'{ob}%', f'{sv}%'] for per, _, ow, ob, sv in T74])),
        'Adult obesity over the last decade, adults 20 and older, age-adjusted': (['Survey years', 'Obesity', 'Severe obesity'], simple(
            [[a, f'{b}%', f'{c}%'] for a, b, c in DEC])),
        'Obesity by age and sex, August 2021–August 2023': (['Age', 'All', 'Men', 'Women'], simple(
            [[lab_, f'{DB_OB["all"][i]}%', f'{DB_OB["men"][i]}%', f'{DB_OB["women"][i]}%'] for i, lab_ in ((1, '20–39'), (2, '40–59'), (3, '60 and older'), (0, 'All 20 and older'))])),
        'Obesity by education, August 2021–August 2023': (['Education', 'All', 'Men', 'Women'], simple(
            [[lab_, f'{DB_ED["all"][i]}%', f'{DB_ED["men"][i]}%', f'{DB_ED["women"][i]}%'] for i, lab_ in
             enumerate(('High school diploma or less', 'Some college', 'Bachelor’s degree or more'))])),
        'Obesity by race and Hispanic origin, adults 20 and older, August 2021–August 2023, age-adjusted': (['Group', 'All', 'Men', 'Women'], simple(
            [[g, f'{a}%', (f'{m[:-1]}%†' if m.endswith('†') else f'{m}%'), (f'{w}%' if w else 'n/a*')] for g, a, m, w in RACE])),
        'Severe obesity (BMI 40 or higher) by age and sex, August 2021–August 2023': (['Age', 'All', 'Men', 'Women'], simple(
            [[lab_, f'{DB_SV["all"][i]}%', f'{DB_SV["men"][i]}%', f'{DB_SV["women"][i]}%'] for i, lab_ in ((1, '20–39'), (2, '40–59'), (3, '60 and older'), (0, 'All 20 and older'))])),
        'Children and teens aged 2 to 19, August 2021–August 2023': (['Group', 'Obesity', 'Severe obesity', 'Overweight'], simple(
            [[lab_, f'{KIDS[s][0]}%', f'{KIDS[s][1]}%', f'{KIDS[s][2]}%'] for s, lab_ in (('all', 'Ages 2–19'), ('boys', 'Boys'), ('girls', 'Girls'))])),
    }
    for cap, (hd, rows) in want.items():
        t = T.get(cap)
        ok(t is not None, f'table missing: {cap}')
        if t: ok([norm(x) for x in t['head']] == hd and rows_of(t) == rows, f'table {cap}: {t["head"]} {rows_of(t)}')
    WHY = [('Weighed and measured, BMI 30 or higher (CDC)', [('40.3%', 'NHANES, August 2021–August 2023', 'Adults 20 and older: the latest'),
            ('41.9%', 'NHANES, 2017–March 2020', 'The survey before, stopped early by the pandemic (age-adjusted)'),
            ('42.4%', 'NHANES, 2017–2018', 'Its first two years, the last full two-year survey; still quoted on many pages (age-adjusted)')]),
           ('Self-reported height and weight, BMI 30 or higher', [(f'{G["rate_2025"]}%', 'Gallup, 2025', f'{G["n"]:,} adults 18 and older, online'),
            ('24.2–39.7%', 'CDC state surveys (BRFSS), 2025', 'Adults 18 and older, by phone; 47 states and DC had a 2025 figure')]),
           ('BMI plus waist measures (the 2025 Lancet Commission definition)', [(f'{F4["new_definition"]}%', 'All of Us (NIH), enrolled 2017–2023',
            f'{F4["n"]:,} volunteers aged 18 to 80, not weighted to the US population; {F4["bmi_based"]}% by BMI alone'), (f'{AR["new_definition"][0]}%', 'NHANES, 2017–2023',
            f'{AR["n"]:,} adults; {AR["bmi_30_plus"][0]}% by BMI alone')])]
    tw = T.get('US adult obesity figures and what each one counts')
    ok(tw is not None and tw['head'] == ['Figure', 'Source and years', 'Who and how'], 'why table head')
    if tw:
        exp = []
        for g, rows in WHY:
            exp.append([['TH', 'rowgroup', '3', g]]); exp += [[['TH', 'row', None, a], ['TD', None, None, b], ['TD', None, None, c]] for a, b, c in rows]
        ok(len(tw['groups']) == 3 and rows_of(tw) == exp, f'why table rows {rows_of(tw)}')
    ok(all('data-table--fit' in t['cls'] for t in tabs), 'tables use .data-table--fit')

    # Figures.
    figs = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => ({vb: svg.getAttribute('viewBox'),
        title: svg.querySelector('title').textContent, desc: svg.querySelector('desc').textContent,
        circles: [...svg.querySelectorAll('circle')].map(c => [+c.getAttribute('cx'), +c.getAttribute('cy'), c.getAttribute('fill'), c.querySelector('title') ? c.querySelector('title').textContent : '']),
        polys: [...svg.querySelectorAll('polyline')].map(l => [l.getAttribute('points'), l.getAttribute('stroke')]),
        rects: [...svg.querySelectorAll('rect')].map(r => [+r.getAttribute('x'), +r.getAttribute('y'), +r.getAttribute('width'), r.getAttribute('fill'), r.querySelector('title') ? r.querySelector('title').textContent : '']),
        texts: [...svg.querySelectorAll('text')].map(t => [t.textContent, +t.getAttribute('x'), +t.getAttribute('y')])}))""")
    ok(len(figs) == 2, f'{len(figs)} inline figures')
    hero, catf = figs
    ok(hero['title'] == 'US adults with obesity, overweight and severe obesity, 1960–2023', 'hero title')
    ok(len(hero['circles']) == 45 and len(hero['polys']) == 3, 'hero marks')
    for key, idx in (('obesity', 3), ('overweight', 2), ('severe obesity', 4)):
        pts = [(round(tx(m), 1), round(ty(row[idx]), 1)) for row in T74 for m in (row[1],)]
        want_pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts)
        ok([want_pts, SERC[key]] in hero['polys'], f'hero line {key}')
        for row in T74:
            c_ = [c for c in hero['circles'] if c[3] == f'{lab(row[0])}: {key} {row[idx]}%']
            ok(len(c_) == 1 and abs(c_[0][0] - tx(row[1])) < 0.06 and abs(c_[0][1] - ty(row[idx])) < 0.06 and c_[0][2] == SERC[key], f'hero dot {key} {row[0]}')
    tt = [t[0] for t in hero['texts']]
    ok(all(x in tt for x in ('Obesity', 'Overweight', 'Severe obesity', '13.4%', '40.8%', '31.5%', '31.3%', '0.9%', '10.2%', '42.8%', '1960', '1980', '2000', '2020', '0%', '50%')), f'hero labels {tt}')
    ok([t for t in hero['texts'] if t[0] == '40.8%'][0][1] == TX1 + 6 and [t for t in hero['texts'] if t[0] == '13.4%'][0][1] == 36, 'hero label positions')
    ok('Obesity rose from 13.4% to 40.8%; its highest estimate was 42.8% in 2017–2018. Severe obesity rose from 0.9% to 10.2%. Overweight stayed between 30.3% and '
       '34.4% (31.5% in 1960–1962, 31.3% in August 2021–August 2023).' in hero['desc'], 'hero desc')
    ok(catf['title'] == 'US adults by BMI category, August 2021–August 2023', 'category figure title')
    bars = [r for r in catf['rects'] if r[4]]
    BASEC = {'underweight': '#3b82f6', 'normal': '#22c55e', 'overweight': '#f59e0b', 'obese': '#ef4444', 'obese-severe': '#991b1b'}
    ok(len(bars) == 6, 'category bars')
    for k, (cls, n, r_, s, m) in enumerate(CATS):
        b = bars[k] if k < len(bars) else [0, 0, 0, '', '']
        ok(abs(b[2] - 300 * float(s) * POP_A / 1e8 / 80) < 0.06 and b[0] == 4 and b[3] == BASEC[cls] and b[4] == f'{n} (BMI {r_}): {s}% of US adults, about {m} million', f'category bar {n}: {b}')
        ok(f'{n}: {m} million ({s}%)' in [t[0] for t in catf['texts']], f'category label {n}')
        ok(f'{n} (BMI {r_}): {s}%, about {m} million.' in catf['desc'], f'category desc {n}')
    img = pg.locator('#use-this-data img'); img.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
    im = pg.evaluate("""() => { const i = document.querySelector('#use-this-data img'); return [i.getAttribute('src'), i.alt, i.width, i.height, i.naturalWidth, i.closest('a').getAttribute('href')]; }""")
    ok(im[0] == '/us-obesity-statistics/us-obesity-trend-1960-2023.svg' and im[1].startswith(EMBED_ALT) and im[4] == 640 and im[5] == im[0], f'embeddable chart {im}')
    svgf = pg.request.get(base + im[0]).text()
    ok('US obesity tripled in 60 years' in svgf and '.cmbv-ob{stroke:#ef4444}' in svgf and '#E0612D' not in svgf, 'embeddable chart file (category colors)')
    ok('Overweight stayed between 30.3% and 34.4% (31.5% in 1960–1962, 31.3% in August 2021–August 2023).' in svgf and 'measured (NHES, NHANES)' in svgf
       and 'stayed near 31%' not in svgf, 'embeddable chart text')
    ok(pg.input_value('#obs-embed') == EMBED, 'embed code changed')
    csvr = pg.request.get(base + '/us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv')
    ok(csvr.status == 200 and csvr.text().count('\n') == 586, 'CSV download')
    ok(',1960-1962,1961.5,underweight,4.0,0.2,age-adjusted,' in csvr.text() and ',Aug 2021-Aug 2023,2022.6,underweight,1.7,0.3,age-adjusted,' in csvr.text(), 'CSV standard errors filled')

    # The tool.
    def calc(units, h, w):
        if pg.get_attribute('#obw [data-units="%s"]' % units, 'aria-pressed') != 'true': pg.click('#obw [data-units="%s"]' % units)
        if units == 'us': pg.fill('#obw-ft', str(h[0])); pg.fill('#obw-in', str(h[1]))
        else: pg.fill('#obw-cm', str(h))
        pg.fill('#obw-lb' if units == 'us' else '#obw-kg', str(w)); pg.click('#obw-go'); pg.wait_for_timeout(30)
    def res():
        return pg.evaluate("""() => { const o = document.getElementById('obw-out'), q = s => o.querySelector(s);
            return {v: q('.bmi-value') ? q('.bmi-value').textContent : null, vc: q('.bmi-value') ? q('.bmi-value').className : '',
                    card: q('.bmi-result-card') ? q('.bmi-result-card').className : '', cat: q('.bmi-category') ? q('.bmi-category').textContent : '',
                    rng: q('.bmi-range') ? q('.bmi-range').textContent : '', note: o.textContent,
                    act: [...o.querySelectorAll('tr.er-active')].map(r => r.textContent), you: o.querySelectorAll('.er-you').length,
                    rows: [...o.querySelectorAll('tbody tr')].map(r => [...r.cells].map(c => c.textContent))}; }""")
    def bmi_us(ft, inch, lb): h = ft * 12 + inch; return r1(703 * lb / (h * h))
    def bmi_m(cm, kg): return r1(kg / (cm / 100) ** 2)
    def cat_of(b): return 0 if b < 18.5 else 1 if b < 25 else 2 if b < 30 else 3 if b < 35 else 4 if b < 40 else 5
    pg.goto(URL, wait_until='load')
    ok((pg.input_value('#obw-ft'), pg.input_value('#obw-in'), pg.input_value('#obw-lb'), pg.input_value('#obw-cm'), pg.input_value('#obw-kg')) == ('5', '7', '160', '170.2', '72.6'), 'starting values')
    ok(pg.is_visible('#obw-lb') and not pg.is_visible('#obw-kg') and pg.evaluate("() => getComputedStyle(document.getElementById('obw-us')).gridTemplateColumns.split(' ').length") == 3, 'one row: ft, in, lb')
    pg.click('#obw-go'); pg.wait_for_timeout(30); r0 = res()
    ok((r0['v'], r0['cat'], r0['rng']) == ('25.1', 'Overweight', '32.1% of US adults are in this group: about 79 million people.'), f'starting result {r0}')
    ok(r0['rows'] == [[f'{n}' + ('You' if i == 2 else '') + f'BMI {r_}', f'{s}%', f'{m} million'] for i, (_, n, r_, s, m) in enumerate(CATS)] and r0['you'] == 1, f'tool table {r0["rows"]}')
    ok(f'Obesity, the three classes together: 40.3% of US adults, about {mil(CRUDE[1])} million. Overweight or obesity: {OWOB}%, about {mil(OWOB)} million.' in r0['note'], 'tool note')
    ok('use the BMI calculator' in r0['note'] and 'A BMI category is not a diagnosis.' in r0['note'], 'tool source line')
    CASES = [('us', (5, 4), 95), ('us', (6, 0), 180), ('us', (5, 9), 200), ('us', (5, 7), 230), ('us', (5, 10), 300), ('us', (5, 7), 192),
             ('us', (5, 7), 159.3), ('us', (5, 7), 159.4), ('us', (5, 2), 134.8), ('metric', 170, 72.1), ('metric', 170, 72.2), ('metric', 160, 45),
             ('metric', 182.5, 105), ('metric', 165, 110), ('metric', 175, 130), ('metric', 150, 78)]
    seen = set()
    for units, h, w in CASES:
        calc(units, h, w); r_ = res()
        b = bmi_us(h[0], h[1], w) if units == 'us' else bmi_m(h, w)
        k = cat_of(b); c = CATS[k]; seen.add(k)
        ok((r_['v'], r_['cat'], r_['rng']) == (f'{b:.1f}', c[1], f'{c[3]}% of US adults are in this group: about {c[4]} million people.') and c[0] in r_['card'].split()
           and c[0] in r_['vc'].split() and len(r_['act']) == 1 and r_['act'][0].startswith(c[1]) and r_['you'] == 1, f'tool {units} {h} {w}: BMI {b} → {r_}')
    ok(seen == set(range(6)), f'categories covered {seen}')
    ok(bmi_us(5, 7, 159.3) == 24.9 and bmi_us(5, 7, 159.4) == 25.0 and bmi_m(170, 72.1) == 24.9 and bmi_m(170, 72.2) == 25.0, 'the 25.0 edge cases')
    # unit round trip: converts to 0.1, comes back exactly, same result
    calc('us', (5, 7), 160); before = res()['v']
    pg.click('#obw [data-units="metric"]')
    ok((pg.input_value('#obw-cm'), pg.input_value('#obw-kg'), pg.is_visible('#obw-cm'), pg.is_visible('#obw-kg'), pg.is_visible('#obw-ft'), pg.is_visible('#obw-lb')) == ('170.2', '72.6', True, True, False, False), 'to metric')
    pg.click('#obw [data-units="us"]')
    ok((pg.input_value('#obw-ft'), pg.input_value('#obw-in'), pg.input_value('#obw-lb')) == ('5', '7', '160') and pg.is_visible('#obw-lb'), 'back to US restores the numbers')
    pg.click('#obw-go'); ok(res()['v'] == before, 'round trip changes the result')
    calc('metric', 182.5, 105); m1 = res()['v']; pg.click('#obw [data-units="us"]'); pg.click('#obw [data-units="metric"]')
    ok((pg.input_value('#obw-cm'), pg.input_value('#obw-kg')) == ('182.5', '105'), 'metric round trip restores the numbers')
    pg.click('#obw-go'); ok(res()['v'] == m1, 'metric round trip changes the result')
    calc('us', (5, 7), 20); ok('Enter a weight from 50 to 700 lb (23 to 318 kg).' in res()['note'], 'weight out of range')
    calc('us', (3, 6), 160); ok('Enter a height from 4 ft to 8 ft (122 to 244 cm).' in res()['note'], 'height out of range')
    calc('metric', 300, 70); ok('Enter a height from 4 ft to 8 ft (122 to 244 cm).' in res()['note'], 'cm out of range')
    pg.click('#obw [data-units="us"]'); pg.fill('#obw-ft', '6'); pg.fill('#obw-in', '0'); pg.fill('#obw-lb', '180'); pg.press('#obw-lb', 'Enter'); pg.wait_for_timeout(30)
    ok(res()['v'] == '24.4', 'Enter key')

    # Head and JSON-LD.
    head = pg.evaluate("""() => ({title: document.title, desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content), canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content), ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        ogt: document.querySelector('meta[property="og:title"]').content, twt: (document.querySelector('meta[name="twitter:title"]') || {}).content || '',
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content),
        ogd: document.querySelector('meta[property="og:description"]').content, twd: (document.querySelector('meta[name="twitter:description"]') || {}).content || ''})""")
    PI = {r: f'{SITE}/assets/images/preferred/us-obesity-statistics-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['title'] == 'US Obesity Rate & Statistics: 40.3% of Adults (CDC Data)', f'title {head["title"]!r}')
    ok(len(head['desc']) <= 160 and head['desc'].startswith('40.3% of US adults have obesity (CDC, measured, 2021–2023).'), f'description {head["desc"]!r}')
    ok(head['robots'] == ['max-image-preview:large'] and head['canon'] == URL.replace(base, SITE), f'robots / canonical {head}')
    ok(head['og'] == [PI['16x9']] and head['tw'] == [PI['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter image {head}')
    ok(head['ogd'] == head['twd'] and head['ogt'] == head['twt'] == 'US obesity rate: 40.3% of adults, and why some sources say 37% or 75%', f'og/twitter text {head}')
    ok(head['ogalt'].startswith('Chart: three lines across 60 years of national surveys') and 'overweight roughly level' in head['ogalt'], f'og alt {head["ogalt"]!r}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        rr = pg.request.get(f'{base}/assets/images/preferred/us-obesity-statistics-{r}.png')
        ok(rr.status == 200 and png_size(rr.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/us-obesity-statistics/og-us-obesity-statistics.png').status == 404, 'old OG image still served')
    sm = pg.request.get(base + '/sitemap.xml').text()
    ent = re.search(r'<url><loc>https://calculatemybmi\.net/us-obesity-statistics/</loc>(.*?)</url>', sm)
    lastmod = re.search(r'<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>', ent.group(1)).group(1) if ent else None
    ok(ent and '<image:loc>https://calculatemybmi.net/us-obesity-statistics/us-obesity-trend-1960-2023.svg</image:loc>' in ent.group(1), 'sitemap image entry')
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok(len(ld) == 1 and [x['@type'] for x in ld[0]['@graph']] == ['Article', 'Dataset', 'BreadcrumbList', 'FAQPage'], 'JSON-LD graph')
    GR = {x['@type']: x for x in ld[0]['@graph']}
    A = GR['Article']; DS = GR['Dataset']
    h1 = pg.inner_text('h1')
    ok(h1 == A['headline'] == 'US Obesity Rate and Statistics', 'H1 / headline')
    ok(A['image'] == [PI['1x1'], PI['4x3'], PI['16x9']] and A['mainEntityOfPage']['primaryImageOfPage']['url'] == PI['16x9'], 'image list / primaryImageOfPage')
    ok(A['dateModified'] == lastmod and re.fullmatch(r'\d{4}-\d{2}-\d{2}', lastmod or '') and A['datePublished'] == '2026-09-30', f'dates {A.get("dateModified")!r} {lastmod!r}')
    ok(A['author']['name'] == 'Marko Visic' and A['publisher']['name'] == 'CalculateMyBMI' and A['@id'] == SITE + '/us-obesity-statistics/#article', 'author / publisher / @id')
    ok(set(A['citation']) <= REG_URLS and len(A['citation']) == 12 and A['description'] == head['desc'] and A['isBasedOn'] == {'@id': SITE + '/us-obesity-statistics/#dataset'}, 'citations / description / dataset link')
    ok(DS['@id'] == SITE + '/us-obesity-statistics/#dataset' and DS['license'] == 'https://creativecommons.org/licenses/by/4.0/' and DS['dateModified'] == lastmod
       and DS['distribution'][0]['contentUrl'] == SITE + '/us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv' and DS['creator']['name'] == 'CalculateMyBMI', 'Dataset')
    ok(DS['measurementTechnique'] == 'Measured height and weight: National Health Examination Survey (NHES, 1960–1970) and National Health and Nutrition '
       'Examination Survey (NHANES, since 1971–1974)' and DS['name'] == 'US obesity, overweight and severe obesity prevalence, 1960–2023 (NHES, NHANES)'
       and 'among children aged 6–11 from 1963–1965, teens aged 12–17 in 1966–1970 and children and teens aged 2–19 from 1971–1974' in DS['description'],
       'Dataset survey names and periods')
    ok([i['name'] for i in GR['BreadcrumbList']['itemListElement']] == ['Home', 'US Obesity Statistics'], 'breadcrumb')
    visq = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok(len(visq) == 12 and [[q['name'], q['acceptedAnswer']['text']] for q in GR['FAQPage']['mainEntity']] == visq, 'FAQ JSON-LD differs from the visible answers')
    ok([q for q, _ in visq] == ['Is it true that 40% of Americans are obese?', 'Is it true that 70% of Americans are overweight?',
        'Are obesity rates rising or falling in the US?', 'Which state is #1 in obesity?', 'What was the obesity rate in 1960?',
        'Why do some sources say 68% or 75% of Americans are obese?', 'Why do some sources say 42.4% or 41.9%?', 'What is the average BMI in America?',
        'What age group has the highest obesity rate?', 'Are women more obese than men?', 'What percent of Americans weigh over 300 pounds?',
        'What percentage of Americans are a healthy weight?'], 'FAQ questions')

    # The menu marks this page, in the mobile menu, and nothing else.
    cur = pg.eval_on_selector_all('[aria-current="page"]', 'as => as.map(a => [a.getAttribute("href"), a.className, a.textContent.trim()])')
    ok(cur == [['/us-obesity-statistics/', 'active', 'Obesity Statistics']], f'menu current page {cur}')
    ok(pg.eval_on_selector_all('header a.active, nav a.active', 'as => as.length') == 1, 'other menu links marked active')

    # Links, chips, FAQ.
    hrefs = pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for h_ in sorted({h_.split('#')[0] for h_ in hrefs if h_.startswith('/')}):
        ok(pg.request.get(base + h_).status == 200, f'internal link {h_} does not answer 200')
    for h_ in sorted({h_ for h_ in hrefs if h_.startswith('/') and '#' in h_}):
        path, frag = h_.split('#')
        ok(f'id="{frag}"' in pg.request.get(base + path).text(), f'anchor {h_} missing')
    for h_ in {h_ for h_ in hrefs if h_.startswith('#')}:
        ok(pg.evaluate('h => !!document.getElementById(h.slice(1))', h_), f'anchor {h_} missing')
    outside = {h_ for h_ in pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))')}
    ok(outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')
    ok(len(outside) == 13, f'{len(outside)} outside links')
    ok(all(pg.evaluate('h => [...document.querySelectorAll(`main a[href="${h}"]`)].every(a => a.target === "_blank" && a.rel === "noopener")', h_) for h_ in outside), 'outside links open in a new tab')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#how-many', '#by-year', '#going-down', '#why-numbers-differ', '#age-gender-education', '#race', '#children', '#use-this-data', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    for old in ('#overweight', '#where-you-fit', '#morbid', '#methods'):
        ok(pg.evaluate('h => !!document.querySelector(h)', old), f'old anchor {old} gone')
    for i, q in enumerate(pg.query_selector_all('.faq-question')):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
    ok(pg.evaluate("() => document.querySelectorAll('main h2').length") == 13 and pg.evaluate("() => document.querySelectorAll('h1').length") == 1, 'headings')

    # Widths, table frames, rendered labels (against every shape, line and plotted line).
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(100)
        pg.click('#obw-go'); pg.wait_for_timeout(60)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : t.className, t.offsetWidth, t.parentElement.clientWidth])""")
        for cap, tw_, fw in fits: ok(tw_ <= fw + 1, f'table scrolls at {w}: {cap} {tw_} > {fw}')
        res2 = pg.evaluate("""() => [...document.querySelectorAll('main figure svg')].map(svg => {
            const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
            const m = svg.getScreenCTM(), pt = (x, y) => { const p = svg.createSVGPoint(); p.x = x; p.y = y; const q = p.matrixTransform(m); return [q.x, q.y]; };
            const polys = [...svg.querySelectorAll('polyline')].map(l => l.getAttribute('points').trim().split(/\\s+/).map(s => pt(...s.split(',').map(Number))));
            return {box: [r.left, r.top, r.right, r.bottom], texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                    shapes: [...svg.querySelectorAll('rect, circle, line')].map(e => [e.tagName + ' ' + (e.getAttribute('fill') || e.getAttribute('stroke')), ...bx(e)]), polys}; })""")
        ok(len(res2) == 2, f'{len(res2)} figures at {w}')
        for f_ in res2:
            L_, T_, R_, B_ = f_['box']
            for j, a in enumerate(f_['texts']):
                ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                for c2 in f_['texts'][j + 1:]:
                    if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5: fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                for s_ in f_['shapes']:
                    if a[1] < s_[3] - 0.5 and s_[1] < a[3] - 0.5 and a[2] < s_[4] - 0.5 and s_[2] < a[4] - 0.5:
                        fails.append(f'{w}px label over a shape: {a[0]!r} / {s_[0]}')
                for poly in f_['polys']:
                    for (xa, ya), (xb, yb) in zip(poly, poly[1:]):
                        n = max(1, int(math.hypot(xb - xa, yb - ya)))
                        if any(a[1] - 1 < xa + (xb - xa) * i / n < a[3] + 1 and a[2] - 1 < ya + (yb - ya) * i / n < a[4] + 1 for i in range(n + 1)):
                            fails.append(f'{w}px label on a plotted line: {a[0]!r}'); break
        ok(pg.evaluate("() => { const o = document.getElementById('obw-out'); return o.scrollWidth <= o.clientWidth + 1; }"), f'tool results wider than the card at {w}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f_ in fails[:40]: print('FAIL', f_)
sys.exit(1 if fails else 0)
