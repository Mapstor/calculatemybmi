#!/usr/bin/env python3
"""CMB-022 US-OBESITY: rebuilds /us-obesity-statistics/ to the D-14 data-page pattern (DESIGN.md "Guide pages (CMB-013)"
order): H1 + byline, three intro paragraphs, key takeaways, disclaimer, hero figure, contents chips, sections, the
"Where do you fit?" tool on the shared calculator parts, a flat FAQ whose JSON-LD equals the visible answers, sources and
method, one related block, one 680 px reading column. No <article> wrapper (D-16), no page-level style.

Demand (research/keyword-ledger.csv): the page owns 472 keywords worth 100,830/mo: "obesity rate in us" 14,800 (primary),
"us obesity rate" and "what percentage of americans are obese" 14,800 each, "obesity in america" 5,400, "obese percentage
usa" and "percentage of obese americans" 3,600 each, "how many people are obese in america" 2,900, "us obesity
statistics", "america overweight rate" and "percentage of overweight americans" 2,400 each, "america average bmi" 1,600,
"childhood obesity usa" 1,300, "us obesity rate by year" 1,000. Owner's SERP pastes of 2026-10-29 (US/English, not
personalized): "obesity rate in us", "what percentage of americans are obese", "us obesity rate by year". The AI Overviews
give 40.3% to 42.4%, Gallup's 37.0%, "68.6% to 75%" under the new Lancet definition, old state figures and NIDDK's
2017-2018 numbers; People also ask: "Is it true that 70% of Americans are overweight?", "Are obesity rates rising or
falling in the US?", "Is it true that 40% of Americans are obese?", "Which state is #1 in obesity?", "What was the obesity
rate in 1960?".

The wedge: the 60-year measured series as the hero (with the CSV and the embeddable chart, the page-map's link magnet),
and one table that says what each number in those results counts: weighed or asked, which years and ages, which
definition.

Every number comes from the page's CSV (us-obesity-data-nhanes-1960-2023.csv, NCHS tables typed in), obs_sources.json
(the other published sources), research/home-build/home_stats.json (our calculation on CDC's 2021-2023 files: the class 1
and class 2 split, the all-adult mean BMI), the CDC state file of /obesity-rate-by-state/, or a value read in chat on
2026-10-29 and typed in below; the generator stops if any of them disagree.

usage: python3 gen_obs.py REPO_ROOT
Runs once, on us-obesity-statistics/index.html as it stood at be1ca97; kept as the build record. The page is written with
{TODAY} in its Article dateModified; apply_build.py puts in the apply date (manifest "today": true).
"""
import sys, os, re, json, html, csv, math
from decimal import Decimal, ROUND_HALF_UP

ROOT = sys.argv[1]
BUILD = os.path.join(ROOT, 'research/us-obesity-statistics-build')
PAGE = os.path.join(ROOT, 'us-obesity-statistics/index.html')
CSVF = os.path.join(ROOT, 'us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv')
SRCS = json.load(open(os.path.join(BUILD, 'obs_sources.json'), encoding='utf-8'))
HS = json.load(open(os.path.join(ROOT, 'research/home-build/home_stats.json')))
OS = json.load(open(os.path.join(BUILD, 'obs_stats.json')))       # obs_stats.py: the 300 lb share (our calculation)
STATES = list(csv.DictReader(open(os.path.join(ROOT, 'research/state-obesity/cdc-brfss-adult-obesity-by-state-2011-2025.csv'),
                                  encoding='utf-8')))
ROWS = list(csv.DictReader(open(CSVF, encoding='utf-8')))
src = open(PAGE, encoding='utf-8', newline='').read()
SITE = 'https://calculatemybmi.net'
URL = SITE + '/us-obesity-statistics/'


# ---------------------------------------------------------------- formatting
def D(x): return Decimal(str(x))
def whole(x): return int(D(x).quantize(Decimal(1), rounding=ROUND_HALF_UP))
def d1(x): return str(D(x).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def esc(s): return html.escape(s, quote=False)
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
def period(p):                                                   # CSV survey period -> display label
    return p.replace('-', '–').replace('Mar ', 'March ')
def nb(s): return re.sub(r'(\d) (million|lb|kg|points)\b', '\\1\u00a0\\2', s)


# ---------------------------------------------------------------- the CSV (NCHS tables, typed in by the S1 build)
def row(ds, per, measure, sex='all', group='all', age=None):
    hit = [r for r in ROWS if r['dataset'] == ds and r['survey_period'] == per and r['measure'] == measure
           and r['sex'] == sex and r['group'] == group and (age is None or r['age_group'] == age)]
    assert len(hit) == 1, (ds, per, measure, sex, group, age, len(hit))
    return hit[0]
def V(*a, **k): return row(*a, **k)['percent']
def SE(*a, **k): return float(row(*a, **k)['standard_error'])
assert len(ROWS) == 585

# Health E-Stat 111, Table 1, "All", age-adjusted (re-read live 2026-10-29; Fryar, Afful, Saif, February 25, 2026):
T74_LIVE = {
    '1960-1962': ('31.5', '13.4', '0.9'), '1971-1974': ('32.7', '14.5', '1.3'), '1976-1980': ('32.1', '15.0', '1.4'),
    '1988-1994': ('32.6', '23.2', '3.0'), '1999-2000': ('33.6', '30.9', '5.0'), '2001-2002': ('34.4', '31.2', '5.4'),
    '2003-2004': ('33.4', '32.9', '5.1'), '2005-2006': ('32.2', '35.1', '6.2'), '2007-2008': ('33.6', '34.3', '6.0'),
    '2009-2010': ('32.7', '36.1', '6.6'), '2011-2012': ('33.3', '35.3', '6.6'), '2013-2014': ('31.9', '38.2', '8.1'),
    '2015-2016': ('31.0', '40.0', '8.0'), '2017-2018': ('30.3', '42.8', '9.6'), 'Aug 2021-Aug 2023': ('31.3', '40.8', '10.2')}
T20_LIVE = {
    '1988-1994': ('33.1', '22.9', '2.8'), '1999-2000': ('34.0', '30.5', '4.7'), '2001-2002': ('35.1', '30.5', '5.1'),
    '2003-2004': ('34.1', '32.2', '4.8'), '2005-2006': ('32.6', '34.3', '5.9'), '2007-2008': ('34.3', '33.7', '5.7'),
    '2009-2010': ('33.0', '35.7', '6.3'), '2011-2012': ('33.6', '34.9', '6.4'), '2013-2014': ('32.5', '37.7', '7.7'),
    '2015-2016': ('31.6', '39.6', '7.7'), '2017-2018': ('30.7', '42.4', '9.2'), 'Aug 2021-Aug 2023': ('31.7', '40.3', '9.7')}
MEAS = ('overweight', 'obesity', 'severe obesity')
for ds, live in (('HE111_T1_adults_20-74', T74_LIVE), ('HE111_T1_adults_20plus', T20_LIVE)):
    for p, vals in live.items():
        assert tuple(V(ds, p, m) for m in MEAS) == vals, (ds, p)
PER74 = list(T74_LIVE)
MID = {p: float(row('HE111_T1_adults_20-74', p, 'obesity')['midpoint_year']) for p in PER74}
assert MID['1960-1962'] == 1961.5 and MID['Aug 2021-Aug 2023'] == 2022.6
LAST = 'Aug 2021-Aug 2023'
OW74 = {p: T74_LIVE[p][0] for p in PER74}; OB74 = {p: T74_LIVE[p][1] for p in PER74}; SV74 = {p: T74_LIVE[p][2] for p in PER74}
assert max(PER74, key=lambda p: D(OB74[p])) == '2017-2018' and OB74['2017-2018'] == '42.8'
# HE-Stat 111 Table 1 by sex, adults 20+, Aug 2021-Aug 2023, age-adjusted overweight: men 35.5 (SE 1.4), women 28.1 (0.9).
OW_SEX = (V('HE111_T1_adults_20plus', LAST, 'overweight', sex='men'), V('HE111_T1_adults_20plus', LAST, 'overweight', sex='women'))
assert OW_SEX == ('35.5', '28.1')
# HE-Stat 111 text/footnote crude estimates for 2021-2023, adults 20+ (the snapshot rows).
CRUDE = {m: V('HE111_crude_snapshot', LAST, m) for m in MEAS}
assert CRUDE == {'overweight': '32.1', 'obesity': '40.3', 'severe obesity': '9.4'}
AA = {m: T20_LIVE[LAST][i] for i, m in enumerate(MEAS)}
assert AA == {'overweight': '31.7', 'obesity': '40.3', 'severe obesity': '9.7'}

# Data Brief 508 (re-read live 2026-10-29; Emmerich, Fryar, Stierman, Ogden, September 2024), crude, adults 20+.
AGES = (('20+', 'all', 'All 20 and older'), ('20-39', '20-39', '20–39'), ('40-59', '40-59', '40–59'), ('60+', '60+', '60 and older'))
DB_OB = {s: tuple(V('DB508_sex_age', LAST, 'obesity', sex=s, group=g, age=a) for a, g, _ in AGES) for s in ('all', 'men', 'women')}
DB_SV = {s: tuple(V('DB508_sex_age', LAST, 'severe obesity', sex=s, group=g, age=a) for a, g, _ in AGES) for s in ('all', 'men', 'women')}
assert DB_OB == {'all': ('40.3', '35.5', '46.4', '38.9'), 'men': ('39.2', '34.3', '45.4', '38.0'), 'women': ('41.3', '36.8', '47.4', '39.6')}
assert DB_SV == {'all': ('9.4', '9.5', '12.0', '6.6'), 'men': ('6.7', '6.1', '9.2', '4.3'), 'women': ('12.1', '13.0', '14.7', '8.4')}
EDU = (('High school diploma or less', 'High school diploma or less'), ('Some college', 'Some college'),
       ("Bachelor's degree or more", 'Bachelor’s degree or more'))
DB_ED = {s: tuple(V('DB508_education', LAST, 'obesity', sex=s, group=g) for g, _ in EDU) for s in ('all', 'men', 'women')}
assert DB_ED == {'all': ('44.6', '45.0', '31.6'), 'men': ('43.3', '43.0', '31.1'), 'women': ('46.0', '46.9', '31.9')}
# Figure 4 data table (age-adjusted): 2017-March 2020 is the pre-pandemic cycle; the other cycles equal HE-Stat 111.
DECADE = [('2013–2014', T20_LIVE['2013-2014'][1], T20_LIVE['2013-2014'][2]),
          ('2015–2016', T20_LIVE['2015-2016'][1], T20_LIVE['2015-2016'][2]),
          ('2017–March 2020', V('DB508_fig4_trend', '2017-Mar 2020', 'obesity'), V('DB508_fig4_trend', '2017-Mar 2020', 'severe obesity')),
          ('Aug 2021–Aug 2023', T20_LIVE[LAST][1], T20_LIVE[LAST][2])]
assert [(o, s) for _, o, s in DECADE] == [('37.7', '7.7'), ('39.6', '7.7'), ('41.9', '9.2'), ('40.3', '9.7')]
HP2030 = '36.0'                     # DB 508: "remains above the Healthy People 2030 goal of 36.0%"
N_EXAM = 5929                       # DB 508 tables: 5,929 adults age 20 and older (= home_stats bmi_n)
assert HS['adults']['bmi_n'] == N_EXAM

# Health E-Stat 111, Table 3, age-adjusted obesity by race and Hispanic origin (re-read live 2026-10-29). * = does not
# meet NCHS reliability standards (not shown); dagger = see Ogden et al. on 2021-2023 race and ethnicity estimates.
RACES = (('Asian, non-Hispanic', 'Asian, non-Hispanic'), ('Black, non-Hispanic', 'Black, non-Hispanic'),
         ('White, non-Hispanic', 'White, non-Hispanic'), ('Hispanic', 'Hispanic'), ('Mexican American', 'Mexican American'))
RACE = {g: tuple(V('HE111_T3_obesity_by_race', LAST, 'obesity', sex=s, group=g) for s in ('all', 'men', 'women')) for g, _ in RACES}
assert RACE == {'Asian, non-Hispanic': ('13.1', '17.8', '9.8'), 'Black, non-Hispanic': ('52.1', '47.3', '56.0'),
                'White, non-Hispanic': ('39.3', '38.3', '40.4'), 'Hispanic': ('44.0', '43.6', '44.6'),
                'Mexican American': ('48.0', '44.2', '52.1')}
UNRELIABLE = {('Asian, non-Hispanic', 'women'), ('Mexican American', 'women')}
for g, s in UNRELIABLE:
    assert row('HE111_T3_obesity_by_race', LAST, 'obesity', sex=s, group=g)['note'].startswith('UNRELIABLE')
DAGGER = ('Black, non-Hispanic', 'men')
assert 'dagger' in row('HE111_T3_obesity_by_race', LAST, 'obesity', sex='men', group='Black, non-Hispanic')['note']

# Health E-Stat 112 (re-read live 2026-10-29; Noiman, Fryar, Saif, Afful, February 2026), ages 2-19.
KIDS = {s: tuple(V('HE112_T1_children_2-19', LAST, m, sex=s) for m in ('obesity', 'severe obesity', 'overweight'))
        for s in ('all', 'boys', 'girls')}
assert KIDS == {'all': ('21.1', '7.0', '15.1'), 'boys': ('23.0', '7.8', '13.0'), 'girls': ('19.1', '6.3', '17.5')}
KAGE = tuple(V('HE112_T2_children_by_age', LAST, 'obesity', group=a, age=a) for a in ('2-5', '6-11', '12-19'))
assert KAGE == ('14.9', '22.1', '22.9')
K1971 = V('HE112_T1_children_2-19', '1971-1974', 'obesity')
assert K1971 == '5.2'
# Health E-Stat 119 (re-read live 2026-10-29; Ansai, Fryar, Afful, June 18, 2026): underweight, BMI under 18.5.
UW = V('HE119_underweight', LAST, 'underweight', age='20+', sex='all')
UW74 = (V('HE119_underweight', '1960-1962', 'underweight', age='20-74'), V('HE119_underweight', LAST, 'underweight', age='20-74'))
assert (UW, UW74) == ('1.6', ('4.0', '1.7'))
RESP = '25.6'                       # "The unweighted examination response rate for all participants was 25.6%"

# Population totals (registry nhanes-population-totals): adults 20+ and children 2-19 represented by the survey.
POP_A, POP_K = 245061169, 74908988
def millions(share, pop=POP_A, nd=0):
    v = D(share) * pop / Decimal(10 ** 8)
    return int(v.quantize(Decimal(1), rounding=ROUND_HALF_UP)) if nd == 0 else str(v.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

# Our calculation (research/home-build/home_stats.py, CDC DEMO_L + BMX_L): the same code reproduces NCHS's crude shares.
assert HS['reproduces_nchs_crude_prevalence']['ours'] == HS['reproduces_nchs_crude_prevalence']['nchs'] == \
       {'underweight': 1.6, 'overweight': 32.1, 'obesity': 40.3, 'obesity_class_3': 9.4}
CS = HS['category_shares_pct']
CLASS1, CLASS2 = f'{CS["obesity_class_1"]:.1f}', f'{CS["obesity_class_2"]:.1f}'
assert (CLASS1, CLASS2) == ('20.6', '10.3') and D(CLASS1) + D(CLASS2) == D(CRUDE['obesity']) - D(CRUDE['severe obesity'])
HEALTHY = D(100) - D(UW) - D(CRUDE['overweight']) - D(CRUDE['obesity'])
assert str(HEALTHY) == '26.0' == f'{CS["healthy"]:.1f}'
OWOB = D(CRUDE['overweight']) + D(CRUDE['obesity'])
assert str(OWOB) == '72.4' == f'{HS["share_bmi_25_plus_pct"]:.1f}'
H60 = D(100) - D(UW74[0]) - D(OW74['1960-1962']) - D(OB74['1960-1962'])
H23 = D(100) - D(UW74[1]) - D(OW74[LAST]) - D(OB74[LAST])
assert (str(H60), str(H23)) == ('51.1', '26.2')
S3 = HS['reproduces_series3']       # NCHS Series 3 No. 50 values the same code reproduces
assert (S3['men_bmi_mean'], S3['women_bmi_mean'], S3['men_bmi_median'], S3['women_bmi_median']) == (29.4, 30.0, 28.2, 28.3)
assert (S3['men_wt_p95_lb'], S3['women_wt_p95_lb']) == (290.6, 262.7)
P95KG = ('131.8', '119.2')          # Series 3 No. 50 Table 4, the same 95th percentiles in kg (registry sample_note)
MEAN_ALL = f'{HS["adults"]["mean"]:.1f}'
assert MEAN_ALL == '29.7'

CATS = [('underweight', 'Underweight', 'under 18.5', UW), ('normal', 'Healthy weight', '18.5–24.9', str(HEALTHY)),
        ('overweight', 'Overweight', '25.0–29.9', CRUDE['overweight']), ('obese', 'Class 1 obesity', '30.0–34.9', CLASS1),
        ('obese', 'Class 2 obesity', '35.0–39.9', CLASS2), ('obese-severe', 'Class 3 obesity', '40.0 or higher', CRUDE['severe obesity'])]
CATS = [(k, n, r, s, millions(s)) for k, n, r, s in CATS]
assert [c[4] for c in CATS] == [4, 64, 79, 50, 25, 23] and sum(D(c[3]) for c in CATS) == 100
M_OB, M_OW, M_SV, M_OWOB = millions(CRUDE['obesity']), millions(CRUDE['overweight']), millions(CRUDE['severe obesity']), millions(OWOB)
assert (M_OB, M_OW, M_SV, M_OWOB) == (99, 79, 23, 177)
K_MIL, K_SV_MIL = millions(KIDS['all'][0], POP_K, 1), millions(KIDS['all'][1], POP_K, 1)
assert (K_MIL, K_SV_MIL) == ('15.8', '5.2')
POPA_M = d1(D(POP_A) / Decimal(10 ** 6))
assert POPA_M == '245.1'

# CDC's state surveys (BRFSS, self-reported), the file /obesity-rate-by-state/ prints (registry cdc-brfss-state-obesity).
NOT_STATE = {'Guam', 'Puerto Rico', 'Virgin Islands', 'District of Columbia'}
def yr(y): return [r for r in STATES if r['year'] == str(y)]
S25 = sorted([r for r in yr(2025) if r['status'] == 'ok' and r['state'] not in NOT_STATE], key=lambda r: -float(r['prevalence_pct']))
TOP3 = [(r['state'], r['prevalence_pct']) for r in S25[:3]]
assert TOP3 == [('Alabama', '39.7'), ('North Dakota', '39.1'), ('Kentucky', '38.8')], TOP3
DC25 = [r['prevalence_pct'] for r in yr(2025) if r['state'] == 'District of Columbia'][0]
LOW25 = (S25[-1]['state'], S25[-1]['prevalence_pct'])
assert DC25 == '24.2' and LOW25 == ('Colorado', '25.7')
MS = {y: [r for r in yr(y) if r['state'] == 'Mississippi'][0] for y in (2024, 2025)}
assert MS[2024]['prevalence_pct'] == '40.4' and MS[2025]['status'] == 'insufficient'
OVER40 = {y: sorted(r['state'] for r in yr(y) if r['status'] == 'ok' and r['state'] not in NOT_STATE
                    and float(r['prevalence_pct']) >= 40) for y in (2024, 2025)}
assert OVER40 == {2024: ['Mississippi', 'West Virginia'], 2025: []}
NO25 = sorted(r['state'] for r in yr(2025) if r['status'] != 'ok' and r['state'] not in NOT_STATE)
assert NO25 == ['California', 'Mississippi', 'Nevada']

G, F4, AR, LC = SRCS['gallup_2025'], SRCS['fourman_2025'], SRCS['alroub_2025'], SRCS['lancet_2025']
assert (G['rate_2025'], G['peak'], G['peak_year'], G['n'], G['men_2025'], G['women_2025']) == ('37.0', '39.9', 2022, 16946, '35.2', '38.8')
assert (F4['new_definition'], F4['bmi_based'], F4['n'], F4['clinical']) == ('68.6', '42.9', 301026, '36.1')
assert round(100 * F4['counts']['new_definition'] / F4['n'], 1) == 68.6 and round(100 * F4['counts']['bmi_based'] / F4['n'], 1) == 42.9
assert (AR['new_definition'][0], AR['bmi_30_plus'][0], AR['whtr_over_05'][0], AR['n']) == ('75.2', '39.9', '80.0', 14414)
assert (LC['experts'], LC['organizations']) == (58, 76)

# The NHANES comparison rule (DEVLOG §4): a difference is stated only where CDC reports it as significant, or where it is
# more than 2.131 times its standard error (t at 95% for the 2021-2023 survey's 15 degrees of freedom) from CDC's published
# standard errors (groups treated as independent).
TCRIT = 2.131
def z(a, b): return abs(float(a[0]) - float(b[0])) / math.hypot(a[1], b[1])
OWS = ((OW_SEX[0], SE('HE111_T1_adults_20plus', LAST, 'overweight', sex='men')),
       (OW_SEX[1], SE('HE111_T1_adults_20plus', LAST, 'overweight', sex='women')))
assert z(*OWS) > TCRIT                                               # men more often overweight than women
BW = [(RACE[g][2], SE('HE111_T3_obesity_by_race', LAST, 'obesity', sex='women', group=g))
      for g in ('Black, non-Hispanic', 'White, non-Hispanic')]
assert z(*BW) > TCRIT                                                # Black and White women
KA = [(v, SE('HE112_T2_children_by_age', LAST, 'obesity', group=a, age=a)) for v, a in zip(KAGE, ('2-5', '6-11', '12-19'))]
assert z(KA[0], KA[1]) > TCRIT and z(KA[0], KA[2]) > TCRIT             # ages 2-5 lower than 6-11 and 12-19
BG = [(KIDS[s][0], SE('HE112_T1_children_2-19', LAST, 'obesity', sex=s)) for s in ('boys', 'girls')]
assert z(*BG) < TCRIT                                                # boys and girls: no comparison stated
RW = [(RACE[g][0], SE('HE111_T3_obesity_by_race', LAST, 'obesity', group=g)) for g in ('Black, non-Hispanic', 'Hispanic', 'Mexican American')]
assert z(RW[0], RW[1]) < TCRIT and z(RW[0], RW[2]) < TCRIT             # so the page gives a range, not a "highest"
# 2017-2018 has the series' highest estimates, but 2021-2023 is not significantly lower (fact-check W1): no "peak".
PK = [((OB74['2017-2018'], SE('HE111_T1_adults_20-74', '2017-2018', 'obesity')), (OB74[LAST], SE('HE111_T1_adults_20-74', LAST, 'obesity'))),
      ((T20_LIVE['2017-2018'][1], SE('HE111_T1_adults_20plus', '2017-2018', 'obesity')), (T20_LIVE[LAST][1], SE('HE111_T1_adults_20plus', LAST, 'obesity')))]
assert all(z(a, b) < TCRIT for a, b in PK)
# Overweight, ages 20-74: between 30% and 35% in every survey (fact-check W2: not "near 31%").
OWR = (min(OW74.values(), key=float), max(OW74.values(), key=float))
assert OWR == ('30.3', '34.4') and all(30 <= float(v) < 35 for v in OW74.values())
# The 300 lb share (obs_stats.py, our calculation): the all-adult share to 0.1 and whole, men and women whole.
L3 = OS['lb300']
L3P = (d1(L3['all']['pct']), whole(L3['all']['pct']), whole(L3['men']['pct']), whole(L3['women']['pct']))
assert L3P == ('2.9', 3, 4, 2) and L3['all']['n'] == 5942 and OS['check_home_stats']['n_bmi'] == N_EXAM, L3P
assert L3['men']['pct'] < 5 and L3['women']['pct'] < 5                # fits CDC's 95th percentiles (both under 300 lb)
# CDC's state surveys, states at 35% or more in 2024 and 2025 (fact-check W3: no clear change).
OVER35 = {y: sum(1 for r in yr(y) if r['status'] == 'ok' and r['state'] not in NOT_STATE and float(r['prevalence_pct']) >= 35)
          for y in (2024, 2025)}
N25 = sum(1 for r in yr(2025) if r['status'] == 'ok' and r['state'] not in NOT_STATE)
assert OVER35 == {2024: 19, 2025: 21} and N25 == 47, (OVER35, N25)

# ---------------------------------------------------------------- links (every outside link is a registry row's)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
REG = {r['domain']: r for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}
U = {
    'he111': 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm',
    'db508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'he112': 'https://www.cdc.gov/nchs/data/hestat/hestat112.htm',
    'he119': 'https://www.cdc.gov/nchs/data/hestat/hestat119.htm',
    's3': 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf',
    'pop': 'https://wwwn.cdc.gov/nchs/data/ResponseRates/ACS-Population-Totals-For-August-2021-August-2023.pdf',
    'gallup': 'https://news.gallup.com/poll/696599/obesity-rate-declining.aspx',
    'maps': 'https://www.cdc.gov/obesity/data-and-statistics/adult-obesity-prevalence-maps.html',
    'cats': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    'lancet': 'https://pubmed.ncbi.nlm.nih.gov/39824205/',
    'fourman': 'https://doi.org/10.1001/jamanetworkopen.2025.37619',
    'alroub': 'https://doi.org/10.1001/jamanetworkopen.2025.49124',
}
def in_reg(u): return any(u == r['url'] or u in [e.strip() for e in r['endpoint'].split(' ; ')] for r in REG.values())
missing = [k for k, u in U.items() if not in_reg(u)]
assert not missing, missing                                          # patch_cmb022.py adds the two new rows first
assert REG[F4['registry']]['url'] == U['fourman'] and REG[AR['registry']]['url'] == U['alroub']
assert REG[G['registry']]['url'] == U['gallup'] and REG[LC['registry']]['url'] == U['lancet']

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS, VBW = [], [], {}
INK, MUTED, GRID = '#111827', '#4b5563', '#e5e7eb'
def text(svg, x, y, s, size=12, anchor='middle', weight=400, fill=INK):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'
def track(svg, x0, y0, x1, y1): RECTS.append((svg, x0, y0, x1, y1))
def track_line(svg, pts, pad=1.5):                                  # a polyline as small boxes along its length
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) / 2))
        for i in range(n + 1):
            x, y = xa + (xb - xa) * i / n, ya + (yb - ya) * i / n
            track(svg, x - pad, y - pad, x + pad, y + pad)
SER = (('obesity', 'Obesity', '#ef4444'), ('overweight', 'Overweight', '#f59e0b'), ('severe obesity', 'Severe obesity', '#991b1b'))

# Figure 1 (hero): every CDC survey since 1960, adults 20-74, age-adjusted (HE-Stat 111 Table 1).
VBW['trend'] = 320
TX0, TX1, TY0, TY1, YR0, YR1 = 34, 274, 28, 196, 1959, 2024
def tx(y): return TX0 + (y - YR0) * (TX1 - TX0) / (YR1 - YR0)
def ty(v): return TY1 - float(v) * (TY1 - TY0) / 50
ft = []
x = 4
for key, name, col in SER:                                          # legend row
    ft.append(f'<line x1="{x}" y1="10" x2="{x + 14}" y2="10" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
    track('trend', x, 8, x + 14, 12)
    ft.append(text('trend', x + 18, 14, name, anchor='start'))
    x = TEXTS[-1][3] + 12
for v in range(0, 51, 10):
    ft.append(f'<line x1="{TX0}" y1="{ty(v):.1f}" x2="{TX1}" y2="{ty(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
    ft.append(text('trend', TX0 - 6, ty(v) + 4, f'{v}%', anchor='end', fill=MUTED))
for yv in (1960, 1980, 2000, 2020):
    ft.append(f'<line x1="{tx(yv):.1f}" y1="{TY1}" x2="{tx(yv):.1f}" y2="{TY1 + 4}" stroke="{MUTED}" stroke-width="1"/>')
    ft.append(text('trend', tx(yv), TY1 + 20, str(yv), fill=MUTED))        # clear of the 0% label's descent
SERIES = {'obesity': OB74, 'overweight': OW74, 'severe obesity': SV74}
for key, name, col in SER:
    pts = [(tx(MID[p]), ty(SERIES[key][p])) for p in PER74]
    ft.append('<polyline points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="none" stroke="{col}" '
              'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    track_line('trend', pts)
for key, name, col in SER:
    for p in PER74:
        tip = f'{period(p)}: {name.lower()} {SERIES[key][p]}%'
        ft.append(f'<circle cx="{tx(MID[p]):.1f}" cy="{ty(SERIES[key][p]):.1f}" r="3.5" fill="{col}" stroke="#ffffff" '
                  f'stroke-width="1.25"><title>{esc(tip)}</title></circle>')
for key, name, col in SER:                                          # first and last values, and the 2017-2018 high
    v0, v1 = SERIES[key][PER74[0]], SERIES[key][LAST]
    ft.append(text('trend', 36, ty(v0) - 9, f'{v0}%', anchor='start', weight=600))
    ft.append(text('trend', TX1 + 6, ty(v1) + 4, f'{v1}%', anchor='start', weight=600))
ft.append(text('trend', tx(MID['2017-2018']), ty(OB74['2017-2018']) - 8, f'{OB74["2017-2018"]}%'))
H_TREND = TY1 + 26
svg_trend = (f'<svg viewBox="0 0 320 {H_TREND}" role="img" aria-labelledby="trend-t trend-d" xmlns="http://www.w3.org/2000/svg" '
             'font-family="inherit"><title id="trend-t">US adults with obesity, overweight and severe obesity, 1960–2023</title>'
             '<desc id="trend-d">Age-adjusted percent of US adults aged 20 to 74, weighed and measured in each survey of CDC’s '
             f'national series from 1960–1962 to August 2021–August 2023. Obesity rose from {OB74["1960-1962"]}% to {OB74[LAST]}%; '
             f'its highest estimate was {OB74["2017-2018"]}% in 2017–2018. Severe obesity rose from {SV74["1960-1962"]}% to '
             f'{SV74[LAST]}%. Overweight stayed between {OWR[0]}% and {OWR[1]}% ({OW74["1960-1962"]}% in 1960–1962, '
             f'{OW74[LAST]}% in August 2021–August 2023). Source: CDC NCHS Health E-Stat 111.</desc>'
             + ''.join(ft) + '</svg>')

# Figure 2: US adults by BMI category, in millions (CDC's shares, the class split ours, counts = share x 245.1 million).
VBW['cats'] = 320
BASEC = {'underweight': '#3b82f6', 'normal': '#22c55e', 'overweight': '#f59e0b', 'obese': '#ef4444', 'obese-severe': '#991b1b'}
fc = []
for k, (cls, name, rng, share, mil) in enumerate(CATS):
    yl = 14 + 36 * k
    fc.append(text('cats', 4, yl, f'{name}: {mil} million ({share}%)', anchor='start'))
    w = 300 * float(share) * POP_A / 1e8 / 80                        # the unrounded count, in millions
    tip = f'{name} (BMI {rng}): {share}% of US adults, about {mil} million'
    fc.append(f'<rect x="4" y="{yl + 6}" width="{w:.1f}" height="12" rx="3" fill="{BASEC[cls]}"><title>{esc(tip)}</title></rect>')
    track('cats', 4, yl + 6, 4 + w, yl + 18)
H_CATS = 14 + 36 * 5 + 24
cats_desc = ' '.join(f'{n} (BMI {r}): {s}%, about {m} million.' for _, n, r, s, m in CATS)
svg_cats = (f'<svg viewBox="0 0 320 {H_CATS}" role="img" aria-labelledby="cats-t cats-d" xmlns="http://www.w3.org/2000/svg" '
            'font-family="inherit"><title id="cats-t">US adults by BMI category, August 2021–August 2023</title>'
            f'<desc id="cats-d">{esc(cats_desc)} Adults 20 and older; CDC NCHS, our split of obesity into classes.</desc>'
            + ''.join(fc) + '</svg>')

def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b_ in TEXTS[i + 1:]:
        if a[0] == b_[0] and overlap(a, b_): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b_[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r): raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'

# ---------------------------------------------------------------- the page's text
H1 = 'US Obesity Rate and Statistics'
G_URL = ext(U['gallup'], 'Gallup')
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">What percentage of Americans are obese? Search for it and you can find 37%, 40.3%, 42.4% and '
    '75% on the same results page.</p>'
    '<p class="intro-text">Each of them comes from a real study. They differ in whether people were weighed or asked, in '
    'the years and ages they cover and, since 2025, in how obesity is defined. CDC’s National Health and Nutrition '
    'Examination Survey, which weighs and measures a national sample, puts it at '
    f'{CRUDE["obesity"]}% of adults for August 2021 to August 2023 ({ext(U["db508"], "CDC")}).</p>'
    '<p class="intro-text">Below: the measured rates for adults and children since 1960, by age, sex, race and '
    'education, what each of the other numbers counts, and the data to download.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    f'<p class="answer"><strong>{CRUDE["obesity"]}% of US adults have obesity, a BMI of 30 or higher: about {M_OB} million '
    'people.</strong> That is CDC’s measured figure for adults 20 and older, August 2021 to August 2023. Another '
    f'{CRUDE["overweight"]}% are overweight, so {OWOB}% have a BMI of 25 or more, and {CRUDE["severe obesity"]}% have '
    'severe obesity, a BMI of 40 or higher.</p><ul>'
    f'<li><strong>Obesity has about tripled since the early 1960s</strong>, from {OB74["1960-1962"]}% to {OB74[LAST]}% of '
    'adults aged 20 to 74 (age-adjusted), while the share who are overweight stayed between 30% and 35%.</li>'
    f'<li><strong>No significant change in the measured data:</strong> CDC found the change from {DECADE[2][1]}% (2017 to '
    f'March 2020) to the latest {DECADE[3][1]}% not statistically significant, and severe obesity rose from {DECADE[0][2]}% to '
    f'{DECADE[3][2]}% (age-adjusted) over the decade. Gallup’s self-reported rate fell from {G["peak"]}% in {G["peak_year"]} to {G["rate_2025"]}% in 2025.</li>'
    f'<li><strong>Highest at ages 40 to 59</strong> ({DB_OB["all"][2]}%). Women and men have similar rates '
    f'({DB_OB["women"][0]}% and {DB_OB["men"][0]}%), but severe obesity is almost twice as common in women '
    f'({DB_SV["women"][0]}% against {DB_SV["men"][0]}%).</li>'
    f'<li><strong>{KIDS["all"][0]}% of children and teens aged 2 to 19 have obesity</strong>, about {K_MIL} million, four '
    f'times the {K1971}% of 1971 to 1974.</li>'
    f'<li><strong>The {F4["new_definition"]}% and {AR["new_definition"][0]}% figures use a new definition</strong> that '
    f'adds waist measures to BMI. In the same people, BMI alone gave {F4["bmi_based"]}% and {AR["bmi_30_plus"][0]}%.</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This page describes the US population for '
    'information only. A BMI category is not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')
assert 2.95 < float(OB74[LAST]) / float(OB74['1960-1962']) < 3.1                      # "about tripled"
assert 3.9 < float(KIDS['all'][0]) / float(K1971) < 4.1                               # "four times"
assert 1.7 < float(DB_SV['women'][0]) / float(DB_SV['men'][0]) < 1.9                  # "almost twice"

hero = (f'<figure class="figure">{svg_trend}<figcaption>US adults aged 20 to 74 with obesity, overweight and severe obesity '
        'in each survey of CDC’s national series from 1960–1962 to August 2021–August 2023, age-adjusted, everyone weighed '
        'and measured. Source: '
        f'CDC, {ext(U["he111"], "NCHS Health E-Stat 111")}, Table 1. The figures are in the table under '
        '<a href="#by-year">US obesity rate by year</a>, and the data and an embeddable chart under '
        '<a href="#use-this-data">Use this chart or data</a>.</figcaption></figure>')

CHIPS = (('how-many', 'How many'), ('by-year', 'By year'), ('going-down', 'Rising or falling'),
         ('why-numbers-differ', 'Why numbers differ'), ('age-gender-education', 'Age and sex'), ('race', 'Race'),
         ('children', 'Children'), ('use-this-data', 'The data'), ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

cat_rows = ''.join(
    f'<tr><th scope="row"><span class="cat-dot {cls}"></span>{n}<span class="th-sub">BMI {r}</span></th>'
    f'<td class="num">{s}%</td><td class="num">{nb(f"{m} million")}</td></tr>' for cls, n, r, s, m in CATS)
cat_rows += (f'<tr><th scope="row">Obesity, all classes<span class="th-sub">BMI 30.0 or higher</span></th>'
             f'<td class="num">{CRUDE["obesity"]}%</td><td class="num">{nb(f"{M_OB} million")}</td></tr>'
             f'<tr><th scope="row">Overweight or obesity<span class="th-sub">BMI 25.0 or higher</span></th>'
             f'<td class="num">{OWOB}%</td><td class="num">{nb(f"{M_OWOB} million")}</td></tr>')
sec_how = (
    '<section id="how-many" class="content-section flow"><h2>How many Americans are obese?</h2>'
    f'<p><strong>About {M_OB} million US adults had obesity</strong> in August 2021 to August 2023: {CRUDE["obesity"]}% of '
    f'the {POPA_M} million adults aged 20 and older that CDC’s survey represents. About {M_OW} million more were '
    f'overweight, and about {M_SV} million had severe obesity.</p>'
    f'<p>Only about 1 in 4 adults ({HEALTHY}%) has a BMI in the healthy range, fewer than have obesity. The typical adult is '
    f'overweight: the median BMI is {S3["men_bmi_median"]} for men and {S3["women_bmi_median"]} for women, and the averages '
    f'are {S3["men_bmi_mean"]} and {S3["women_bmi_mean"]} ({ext(U["s3"], "CDC")}).</p>'
    f'<figure class="figure">{svg_cats}<figcaption>US adults aged 20 and older by BMI category, August 2021–August 2023. '
    'Shares from CDC, healthy weight by subtraction; the split of obesity into classes 1 and 2 is our calculation from '
    'CDC’s survey files.</figcaption></figure>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>US adults by BMI '
    'category, August 2021–August 2023</caption><thead><tr><th scope="col">BMI category</th><th scope="col" '
    'class="num">Share</th><th scope="col" class="num">Adults</th></tr></thead>'
    f'<tbody>{cat_rows}</tbody></table></div>'
    '<p class="source-note">Adults 20 and older, not age-adjusted, pregnant women excluded. Underweight, overweight, '
    f'obesity and class 3 (severe) obesity: {ext(U["he111"], "CDC NCHS Health E-Stat 111")} and '
    f'{ext(U["he119"], "119")}. Healthy weight: 100% minus the other categories. Classes 1 and 2: our calculation from '
    'CDC’s 2021–2023 files, with the code that reproduces CDC’s four published shares exactly. Counts: share × '
    f'{POPA_M} million adults ({ext(U["pop"], "CDC’s population total")} for the survey), rounded to the nearest '
    'million. Class 3 is the name CDC’s BMI categories use for a BMI of 40 or higher.</p>'
    '<h3 id="overweight">What percentage of Americans are overweight?</h3>'
    f'<p><strong>{CRUDE["overweight"]}% of US adults are overweight</strong>, a BMI of 25.0 to 29.9. Add the '
    f'{CRUDE["obesity"]}% with obesity and {OWOB}% have a BMI of 25 or higher, the figure behind claims that about 70% of '
    f'Americans are overweight. Men are more often overweight than women, {OW_SEX[0]}% against {OW_SEX[1]}% '
    '(age-adjusted).</p>'
    '<p>Unlike obesity, the overweight share ended where it started: '
    f'{OW74["1960-1962"]}% of adults aged 20 to 74 in 1960–1962 and {OW74[LAST]}% in 2021–2023 (age-adjusted), between 30% '
    'and 35% in every survey. The '
    f'healthy-weight share shrank instead, from {H60}% to {H23}% (our calculation from CDC’s figures).</p></section>')

sec_fit = (
    '<section id="where-you-fit" class="content-section flow"><h2>Where do you fit?</h2>'
    '<p>Enter your height and weight to see your BMI category and how many US adults share it. The shares are for adults '
    '20 and older; for children and teens, use the <a href="/kids-bmi-calculator/">kids BMI calculator</a>.</p></section>')
OBW = {'cats': [[c[0], c[1], c[2], c[3], c[4]] for c in CATS], 'ob': [CRUDE['obesity'], M_OB], 'owob': [str(OWOB), M_OWOB]}
tool = (
    '<div class="calculator-card obw" id="obw"><div class="calc-panel active">'
    '<div class="unit-toggle" role="group" aria-label="Units"><button type="button" class="unit-btn active" data-units="us" '
    'aria-pressed="true">ft, in, lb</button><button type="button" class="unit-btn" data-units="metric" '
    'aria-pressed="false">cm, kg</button></div>'
    '<div class="form-grid"><div class="form-row form-row--trio" id="obw-us"><div class="form-group"><label class="form-label" '
    'for="obw-ft">Height (ft)</label><input type="number" id="obw-ft" class="form-input" inputmode="numeric" min="4" max="8" '
    'step="1" value="5"></div><div class="form-group"><label class="form-label" for="obw-in">Height (in)</label><input '
    'type="number" id="obw-in" class="form-input" inputmode="decimal" min="0" max="11.9" step="0.1" value="7"></div>'
    '<div class="form-group"><label class="form-label" for="obw-lb">Weight (lb)</label><input type="number" id="obw-lb" '
    'class="form-input" inputmode="decimal" min="50" max="700" step="0.1" value="160"></div></div>'
    '<div class="form-row form-row--pair" id="obw-metric" hidden><div class="form-group"><label class="form-label" '
    'for="obw-cm">Height (cm)</label><input type="number" id="obw-cm" class="form-input" inputmode="decimal" min="122" '
    'max="244" step="0.1" value="170.2"></div><div class="form-group"><label class="form-label" for="obw-kg">Weight (kg)'
    '</label><input type="number" id="obw-kg" class="form-input" inputmode="decimal" min="23" max="318" step="0.1" '
    'value="72.6"></div></div></div>'
    '<button type="button" class="calculate-btn" id="obw-go">Show where I fit</button>'
    '<div class="results-section" id="obw-out" aria-live="polite"></div></div></div>'
    '<noscript><p>The tool needs JavaScript. <a href="#how-many">The table above</a> gives every BMI category’s share of '
    'US adults.</p></noscript>'
    '<script>window.OBW=' + json.dumps(OBW, ensure_ascii=False, separators=(',', ':')) + ';</script>'
    '<script>(function(){var D=window.OBW,$=function(i){return document.getElementById(i);},units="us",out=$("obw-out"),snap=null;'
    'function r1(x){return Math.round(x*10+1e-9)/10;}'
    'function cat(b){return b<18.5?0:b<25?1:b<30?2:b<35?3:b<40?4:5;}'
    'function msg(t){out.innerHTML=\'<p class="er-note">\'+t+\'</p>\';out.classList.add("visible");}'
    'function vals(){return units==="us"?[$("obw-ft").value,$("obw-in").value,$("obw-lb").value]:[$("obw-cm").value,$("obw-kg").value];}'
    'function show(){var metric=units==="metric",hIn,cm,w=parseFloat($(metric?"obw-kg":"obw-lb").value),b;'
    'if(metric){cm=parseFloat($("obw-cm").value);hIn=cm/2.54;}else{hIn=parseFloat($("obw-ft").value)*12+parseFloat($("obw-in").value||"0");cm=hIn*2.54;}'
    'if(!(hIn>=48&&hIn<=96))return msg("Enter a height from 4 ft to 8 ft (122 to 244 cm).");'
    'if(!(metric?w>=23&&w<=318:w>=50&&w<=700))return msg("Enter a weight from 50 to 700 lb (23 to 318 kg).");'
    'b=metric?r1(w/((cm/100)*(cm/100))):r1(703*w/(hIn*hIn));'
    'var k=cat(b),c=D.cats[k],h=\'<div class="bmi-result-card \'+c[0]+\'"><div class="bmi-value \'+c[0]+\'">\'+b.toFixed(1)+\'</div>'
    '<div class="bmi-category">\'+c[1]+\'</div><div class="bmi-range">\'+c[3]+\'% of US adults are in this group: about \'+c[4]+'
    '\' million people.</div></div><div class="er"><section class="er-section"><h3>US adults by BMI category</h3>'
    '<table class="er-table"><thead><tr><th>BMI category</th><th class="er-num">Share</th><th class="er-num">Adults</th></tr>'
    '</thead><tbody>\';'
    'D.cats.forEach(function(r,i){h+=\'<tr\'+(i===k?\' class="er-active"\':\'\')+\'><td><span class="cat-dot \'+r[0]+\'"></span>\'+r[1]+'
    '(i===k?\'<span class="er-you">You</span>\':\'\')+\'<span class="er-alt">BMI \'+r[2]+\'</span></td><td class="er-num">\'+r[3]+'
    '\'%</td><td class="er-num">\'+r[4]+\' million</td></tr>\';});'
    'h+=\'</tbody></table><p class="er-note">Obesity, the three classes together: \'+D.ob[0]+\'% of US adults, about \'+D.ob[1]+'
    '\' million. Overweight or obesity: \'+D.owob[0]+\'%, about \'+D.owob[1]+\' million.</p></section>'
    '<div class="er-section"><p class="er-note">CDC NHANES August 2021–August 2023, adults 20 and older, pregnant women '
    'excluded: CDC’s shares, with healthy weight by subtraction and the split of obesity into classes 1 and 2 our '
    'calculation from CDC’s files. Counts: share × 245.1 million adults. A BMI category is not a diagnosis. For your full '
    'result and where you rank among US adults, use the <a href="/">BMI calculator</a>.</p></div></div>\';'
    'out.innerHTML=h;out.classList.add("visible");}'
    'function pick(sel,fn){var bs=document.querySelectorAll(sel);for(var i=0;i<bs.length;i++)bs[i].addEventListener("click",function(){'
    'for(var j=0;j<bs.length;j++){var on=bs[j]===this;bs[j].classList.toggle("active",on);bs[j].setAttribute("aria-pressed",on?"true":"false");}'
    'fn(this.getAttribute("data-units"));});}'
    'pick("#obw [data-units]",function(v){if(v===units)return;var cur=vals();'
    'if(snap&&snap.to===units&&snap.conv.join("|")===cur.join("|")){var o=snap.orig;'
    'if(v==="us"){$("obw-ft").value=o[0];$("obw-in").value=o[1];$("obw-lb").value=o[2];}else{$("obw-cm").value=o[0];$("obw-kg").value=o[1];}snap=null;}'
    'else{if(v==="metric"){var hi=parseFloat($("obw-ft").value)*12+parseFloat($("obw-in").value||"0"),lb=parseFloat($("obw-lb").value);'
    'if(hi>0)$("obw-cm").value=(hi*2.54).toFixed(1);if(lb>0)$("obw-kg").value=(lb*0.45359237).toFixed(1);}'
    'else{var cc=parseFloat($("obw-cm").value);if(cc>0){var t=cc/2.54,f=Math.floor(t/12),r=Math.round((t-12*f)*10)/10;if(r>=12){f+=1;r=0;}'
    '$("obw-ft").value=f;$("obw-in").value=r;}var kg=parseFloat($("obw-kg").value);if(kg>0)$("obw-lb").value=(kg/0.45359237).toFixed(1);}'
    'units=v;snap={to:v,orig:cur,conv:vals()};}'
    'units=v;$("obw-us").hidden=v!=="us";$("obw-metric").hidden=v!=="metric";});'
    '$("obw-go").addEventListener("click",show);'
    '["obw-ft","obw-in","obw-lb","obw-cm","obw-kg"].forEach(function(id){$(id).addEventListener("keydown",function(e){if(e.key==="Enter"){e.preventDefault();show();}});});'
    '})();</script>')

year_rows = ''.join(f'<tr><th scope="row">{period(p)}</th><td class="num">{OW74[p]}%</td><td class="num">{OB74[p]}%</td>'
                    f'<td class="num">{SV74[p]}%</td></tr>' for p in PER74)
sec_year = (
    '<section id="by-year" class="content-section flow"><h2>US obesity rate by year, 1960–2023</h2>'
    f'<p><strong>Adult obesity has about tripled since the early 1960s:</strong> {OB74["1960-1962"]}% of adults aged 20 to 74 '
    f'had obesity in 1960–1962 and {OB74[LAST]}% in 2021–2023 (age-adjusted). Severe obesity rose from '
    f'{SV74["1960-1962"]}% to {SV74[LAST]}%, 11 times as high.</p>'
    '<p>The fastest climb came between the late 1970s and 2000, when the rate doubled from '
    f'{OB74["1976-1980"]}% (1976–1980) to {OB74["1999-2000"]}% (1999–2000). It kept rising more slowly, to '
    f'{OB74["2017-2018"]}% in 2017–2018; the {OB74[LAST]}% of 2021–2023 is not significantly lower.</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>US adults aged 20 '
    'to 74 by survey years, age-adjusted</caption><thead><tr><th scope="col">Survey years</th><th scope="col" '
    'class="num">Over\u00adweight</th><th scope="col" class="num">Obesity</th><th scope="col" class="num">Severe obesity</th>'
    f'</tr></thead><tbody>{year_rows}</tbody></table></div>'
    '<p class="source-note">Weighed and measured. CDC uses ages 20 to 74 for the long series because the 1971–1974 and '
    '1976–1980 surveys did not include anyone older than 74. Each survey covers two years or more, so there are no single-year figures. The '
    'table has no survey between 2017–2018 and 2021–2023: data collection paused in March 2020 for the pandemic and '
    'resumed in August 2021 (CDC’s 2017–March 2020 estimate is in the next section). '
    f'For all adults 20 and older (from 1988–1994), obesity rose from {T20_LIVE["1988-1994"][1]}% to '
    f'{T20_LIVE["2017-2018"][1]}% in 2017–2018 and was {T20_LIVE[LAST][1]}% in 2021–2023, not a significant change; both '
    'series are in the CSV under '
    f'<a href="#use-this-data">Use this chart or data</a>. Source: {ext(U["he111"], "CDC NCHS Health E-Stat 111")}, '
    f'Table 1; the pause: {ext(U["db508"], "NCHS Data Brief 508")}.</p></section>')
assert 11.0 < float(SV74[LAST]) / float(SV74['1960-1962']) < 11.5                    # "11 times as high"
assert 2.0 < float(OB74['1999-2000']) / float(OB74['1976-1980']) < 2.1               # "doubled"

dec_rows = ''.join(f'<tr><th scope="row">{p}</th><td class="num">{o}%</td><td class="num">{s}%</td></tr>' for p, o, s in DECADE)
sec_trend = (
    '<section id="going-down" class="content-section flow"><h2>Are obesity rates rising or falling?</h2>'
    f'<p><strong>CDC’s measured data show no significant change.</strong> The latest CDC estimate, {DECADE[3][1]}% of adults 20 '
    f'and older (age-adjusted), is below the {DECADE[2][1]}% of 2017 to March 2020, but CDC found neither that change nor '
    f'the change over the decade since 2013–2014 ({DECADE[0][1]}%) statistically significant. Severe obesity did rise, '
    f'from {DECADE[0][2]}% to {DECADE[3][2]}% (age-adjusted), and adult obesity remains above the Healthy People 2030 goal of {HP2030}% '
    f'({ext(U["db508"], "CDC")}).</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Adult obesity over '
    'the last decade, adults 20 and older, age-adjusted</caption><thead><tr><th scope="col">Survey years</th><th scope="col" '
    f'class="num">Obesity</th><th scope="col" class="num">Severe obesity</th></tr></thead><tbody>{dec_rows}</tbody></table></div>'
    f'<p class="source-note">Source: {ext(U["db508"], "CDC NCHS Data Brief 508")}, Figure 4.</p>'
    f'<p>A survey where people give their own height and weight points down: the Gallup National Health and Well-Being '
    f'Index put obesity at {G["peak"]}% in {G["peak_year"]} and {G["rate_2025"]}% in 2025, with women at {G["women_2025"]}% '
    f'and men at {G["men_2025"]}% ({G_URL}). CDC’s state surveys, also self-reported, show no clear change: '
    f'{OVER35[2025]} states were at 35% or higher in 2025 against {OVER35[2024]} in 2024, and none reached 40% in 2025, but '
    f'Mississippi ({MS[2024]["prevalence_pct"]}% in 2024) had no 2025 estimate ({ext(U["maps"], "CDC")}). Under the new '
    'definition that adds waist measures, one study found no change between 2017–2020 and 2021–2023 '
    f'({ext(U["alroub"], "Al-Roub et al., 2025")}).</p></section>')

def why_row(fig, where, what):
    return f'<tr><th scope="row">{fig}</th><td>{where}</td><td>{what}</td></tr>'
WHY = [
    ('Weighed and measured, BMI 30 or higher (CDC)', [
        (f'{CRUDE["obesity"]}%', 'NHANES, August 2021–August 2023', 'Adults 20 and older: the latest'),
        (f'{DECADE[2][1]}%', 'NHANES, 2017–March 2020', 'The survey before, stopped early by the pandemic (age-adjusted)'),
        (f'{T20_LIVE["2017-2018"][1]}%', 'NHANES, 2017–2018', 'Its first two years, the last full two-year survey; still quoted '
                                                             'on many pages (age-adjusted)')]),
    ('Self-reported height and weight, BMI 30 or higher', [
        (f'{G["rate_2025"]}%', 'Gallup, 2025', f'{G["n"]:,} adults 18 and older, online'),
        (f'{DC25}–{TOP3[0][1]}%', 'CDC state surveys (BRFSS), 2025', f'Adults 18 and older, by phone; {N25} states and DC had a '
                                                                       '2025 figure')]),
    ('BMI plus waist measures (the 2025 Lancet Commission definition)', [
        (f'{F4["new_definition"]}%', 'All of Us (NIH), enrolled 2017–2023', f'{F4["n"]:,} volunteers aged 18 to 80, not '
                                                                         'weighted to the US population; '
                                                                         f'{F4["bmi_based"]}% by BMI alone'),
        (f'{AR["new_definition"][0]}%', 'NHANES, 2017–2023', f'{AR["n"]:,} adults; {AR["bmi_30_plus"][0]}% by BMI alone')]),
]
why_body = ''.join(f'<tbody><tr><th scope="rowgroup" colspan="3">{g}</th></tr>' + ''.join(why_row(*r) for r in rows) + '</tbody>'
                   for g, rows in WHY)
sec_why = (
    '<section id="why-numbers-differ" class="content-section flow"><h2>Why do sources say 37%, 40%, 42% or 75%?</h2>'
    '<p>Each figure is right for what it counts. Three things move it: whether people were weighed or asked, which years '
    'and ages it covers, and which definition of obesity it uses.</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>US adult obesity '
    'figures and what each one counts</caption><thead><tr><th scope="col">Figure</th><th scope="col">Source and years</th>'
    f'<th scope="col">Who and how</th></tr></thead>{why_body}</table></div>'
    f'<p class="source-note">Sources: {ext(U["db508"], "CDC NCHS Data Brief 508")}; '
    f'{ext(U["he111"], "Health E-Stat 111")}; {G_URL}, “Obesity Rate Declining in U.S.”, October 28, 2025; '
    f'{ext(U["maps"], "CDC Adult Obesity Prevalence Maps")}, updated September 24, 2026; '
    f'{ext(U["fourman"], "Fourman et al., JAMA Network Open, 2025")}; {ext(U["alroub"], "Al-Roub et al., JAMA Network Open, 2025")}.</p>'
    '<h3>Weighed or asked</h3>'
    '<p>In CDC’s survey, trained technicians measure height and weight in a mobile examination center. Surveys that ask '
    f'people come in lower: Gallup says a “vanity effect” in how people describe themselves may explain why its estimates '
    f'usually run somewhat below measured ones. CDC’s state figures are self-reported too, and every one of them in 2025, from '
    f'{DC25}% (the District of Columbia) to {TOP3[0][1]}% ({TOP3[0][0]}), sits below the national {CRUDE["obesity"]}%: compare '
    'states with states, on the <a href="/obesity-rate-by-state/">obesity rate by state</a> page.</p>'
    '<h3>Which years and ages</h3>'
    f'<p>{T20_LIVE["2017-2018"][1]}% (2017–2018) and {DECADE[2][1]}% (2017 to March 2020) are CDC’s earlier figures, and '
    'neither is current. CDC’s adult figures start at age 20; Gallup and the state surveys include adults of 18 and 19. '
    f'The 60-year series covers ages 20 to 74, which is why its latest value is {OB74[LAST]}%, not {CRUDE["obesity"]}%.</p>'
    '<p>Crude shares are the actual shares of adults: in 2021–2023, '
    f'{CRUDE["obesity"]}% with obesity, {CRUDE["overweight"]}% overweight and {CRUDE["severe obesity"]}% with severe '
    'obesity. Age-adjusted shares are reweighted to the age mix of the 2000 census so that years and groups compare '
    f'fairly: {AA["obesity"]}%, {AA["overweight"]}% and {AA["severe obesity"]}%.</p>'
    '<h3>A new definition: BMI plus waist measures</h3>'
    f'<p>In January 2025 the Lancet Commission on Clinical Obesity ({LC["experts"]} experts, endorsed by '
    f'{LC["organizations"]} organizations) recommended confirming excess body fat instead of diagnosing obesity from BMI '
    'alone: a high BMI plus at least one waist measure above its cut-off (waist circumference, waist-to-hip ratio or '
    'waist-to-height ratio), at least two waist measures whatever the BMI, or a direct body fat measurement. Above a BMI '
    'of 40, it says excess fat can be assumed. It asks for validated cut-offs appropriate to age, sex and ethnicity '
    f'({ext(U["lancet"], "Rubino et al., 2025")}).</p>'
    f'<p>Applied to {F4["n"]:,} volunteers aged 18 to 80 in NIH’s All of Us program, a cohort not weighted to the US '
    f'population, the new definition gave {F4["new_definition"]}% against {F4["bmi_based"]}% by BMI with WHO’s race-specific '
    f'cut-offs ({ext(U["fourman"], "Fourman et al., 2025")}). Applied to '
    f'CDC’s 2017–2023 survey, with a waist more than half the height counted as one criterion, it gave '
    f'{AR["new_definition"][0]}% against {AR["bmi_30_plus"][0]}%; {AR["whtr_over_05"][0]}% of adults had a waist more than '
    f'half their height, and with 0.6 as the cut-off instead of 0.5 the study found {AR["whtr_06_definition"][0]}% '
    f'({ext(U["alroub"], "Al-Roub et al., 2025")}). The Commission also splits obesity into clinical '
    'obesity, with signs of reduced organ function or a reduced ability to carry out daily activities, and preclinical '
    'obesity; in All of Us, '
    f'{F4["clinical"]}% had clinical obesity. CDC’s figures still use BMI, and the '
    '<a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> guide explains that measure.</p></section>')

age_rows = ''.join(f'<tr><th scope="row">{lab}</th><td class="num">{DB_OB["all"][i]}%</td><td class="num">{DB_OB["men"][i]}%</td>'
                   f'<td class="num">{DB_OB["women"][i]}%</td></tr>' for i, (_, _, lab) in list(enumerate(AGES))[1:] + [(0, AGES[0])])
edu_rows = ''.join(f'<tr><th scope="row">{lab}</th><td class="num">{DB_ED["all"][i]}%</td><td class="num">{DB_ED["men"][i]}%</td>'
                   f'<td class="num">{DB_ED["women"][i]}%</td></tr>' for i, (_, lab) in enumerate(EDU))
sec_age = (
    '<section id="age-gender-education" class="content-section flow"><h2>Obesity rate by age, gender and education</h2>'
    '<h3>By age: highest in middle age</h3>'
    f'<p>Adults aged 40 to 59 have the highest rate, {DB_OB["all"][2]}%, above both ages 20 to 39 ({DB_OB["all"][1]}%) and 60 '
    f'and older ({DB_OB["all"][3]}%). The same middle-age peak shows in men and in women ({ext(U["db508"], "CDC")}).</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Obesity by age and sex, August '
    '2021–August 2023</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">All</th><th scope="col" '
    f'class="num">Men</th><th scope="col" class="num">Women</th></tr></thead><tbody>{age_rows}</tbody></table></div>'
    '<h3>Men and women</h3>'
    f'<p>Women and men have similar obesity rates, {DB_OB["women"][0]}% and {DB_OB["men"][0]}%, a difference CDC found not '
    f'statistically significant. The gap is at the heavy end: {DB_SV["women"][0]}% of women have severe obesity against '
    f'{DB_SV["men"][0]}% of men. Men are more often overweight ({OW_SEX[0]}% against {OW_SEX[1]}%, age-adjusted).</p>'
    '<h3>By education</h3>'
    f'<p>Adults with a bachelor’s degree or more have a lower rate ({DB_ED["all"][2]}%) than those with some college '
    f'({DB_ED["all"][1]}%) or a high school diploma or less ({DB_ED["all"][0]}%), and the last two don’t differ '
    'significantly. CDC found no significant differences between men and women at any education level.</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Obesity by '
    'education, August 2021–August 2023</caption><thead><tr><th scope="col">Education</th><th scope="col" class="num">All'
    f'</th><th scope="col" class="num">Men</th><th scope="col" class="num">Women</th></tr></thead><tbody>{edu_rows}</tbody>'
    '</table></div>'
    f'<p class="source-note">Adults 20 and older, not age-adjusted. Source: {ext(U["db508"], "CDC NCHS Data Brief 508")}; '
    f'overweight by sex: {ext(U["he111"], "Health E-Stat 111")}.</p></section>')

def race_cell(g, s, i):
    if (g, s) in UNRELIABLE: return '<td class="num">n/a*</td>'
    return f'<td class="num">{RACE[g][i]}%{"†" if (g, s) == DAGGER else ""}</td>'
race_rows = ''.join(f'<tr><th scope="row">{lab}</th>' + ''.join(race_cell(g, s, i) for i, s in enumerate(('all', 'men', 'women')))
                    + '</tr>' for g, lab in RACES)
sec_race = (
    '<section id="race" class="content-section flow"><h2>Obesity rate by race and ethnicity</h2>'
    f'<p>Age-adjusted obesity rates in 2021–2023 ranged from {RACE["Asian, non-Hispanic"][0]}% among non-Hispanic Asian '
    f'adults to {RACE["Black, non-Hispanic"][0]}% among non-Hispanic Black adults. They were {RACE["Mexican American"][0]}% '
    f'for Mexican American adults, {RACE["Hispanic"][0]}% for Hispanic adults overall and {RACE["White, non-Hispanic"][0]}% '
    f'for non-Hispanic White adults. Among women, {RACE["Black, non-Hispanic"][2]}% of non-Hispanic Black women had obesity '
    f'against {RACE["White, non-Hispanic"][2]}% of non-Hispanic White women.</p>'
    '<p>CDC adds two cautions. At a given BMI, body fat may vary by sex, age, and race and Hispanic origin; CDC points to '
    'research that health risks may begin at a lower BMI among Asian people, and that BMI overestimates body fat among '
    'Black people compared with others at the same BMI. And the 2021–2023 survey used a new sample design with no oversampling '
    'by race and Hispanic origin; two estimates for women did not meet NCHS standards of reliability. CDC prints them '
    'flagged, and the table below leaves them out.</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Obesity by race and '
    'Hispanic origin, adults 20 and older, August 2021–August 2023, age-adjusted</caption><thead><tr><th scope="col">Group'
    '</th><th scope="col" class="num">All</th><th scope="col" class="num">Men</th><th scope="col" class="num">Women</th>'
    f'</tr></thead><tbody>{race_rows}</tbody></table></div>'
    '<p class="source-note">* Left out: CDC flags the estimate as not meeting NCHS standards of reliability or precision. † NCHS '
    'refers readers to Ogden et al. for more on 2021–2023 estimates by race and ethnicity. Source: '
    f'{ext(U["he111"], "CDC NCHS Health E-Stat 111")}, Table 3.</p></section>')

sev_rows = ''.join(f'<tr><th scope="row">{lab}</th><td class="num">{DB_SV["all"][i]}%</td><td class="num">{DB_SV["men"][i]}%</td>'
                   f'<td class="num">{DB_SV["women"][i]}%</td></tr>' for i, (_, _, lab) in list(enumerate(AGES))[1:] + [(0, AGES[0])])
sec_sev = (
    '<section id="morbid" class="content-section flow"><h2>What percentage of Americans are morbidly obese?</h2>'
    f'<p><strong>{CRUDE["severe obesity"]}% of US adults have severe obesity</strong>, CDC’s term for a BMI of 40 or higher, '
    f'also called class 3 obesity: about {M_SV} million adults. It is almost twice as common in women ({DB_SV["women"][0]}%) '
    f'as in men ({DB_SV["men"][0]}%), and women’s rate is higher in every age group. It is more common at ages 20 to 39 '
    f'({DB_SV["all"][1]}%) and 40 to 59 ({DB_SV["all"][2]}%) than at 60 and older ({DB_SV["all"][3]}%). Over 60 years it '
    f'rose from {SV74["1960-1962"]}% to {SV74[LAST]}% of adults aged 20 to 74 (age-adjusted).</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Severe obesity (BMI 40 or higher) by '
    'age and sex, August 2021–August 2023</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">All</th>'
    f'<th scope="col" class="num">Men</th><th scope="col" class="num">Women</th></tr></thead><tbody>{sev_rows}</tbody>'
    f'</table></div><p class="source-note">Adults 20 and older, not age-adjusted. Source: '
    f'{ext(U["db508"], "CDC NCHS Data Brief 508")}; the 60-year change: {ext(U["he111"], "Health E-Stat 111")}.</p></section>')

kid_rows = ''.join(f'<tr><th scope="row">{lab}</th><td class="num">{KIDS[s][0]}%</td><td class="num">{KIDS[s][1]}%</td>'
                   f'<td class="num">{KIDS[s][2]}%</td></tr>' for s, lab in (('all', 'Ages 2–19'), ('boys', 'Boys'), ('girls', 'Girls')))
sec_kids = (
    '<section id="children" class="content-section flow"><h2>Childhood obesity rate in America</h2>'
    f'<p><strong>{KIDS["all"][0]}% of US children and teens aged 2 to 19 had obesity</strong> in August 2021 to August 2023, '
    f'including {KIDS["all"][1]}% with severe obesity, and another {KIDS["all"][2]}% were overweight: about {K_MIL} million '
    'children and teens with obesity (our calculation).</p>'
    f'<p>Obesity is lower at ages 2 to 5 ({KAGE[0]}%) than at 6 to 11 ({KAGE[1]}%) and 12 to 19 ({KAGE[2]}%). It was '
    f'{KIDS["boys"][0]}% among boys and {KIDS["girls"][0]}% among girls. In 1971–1974, {K1971}% of children and teens had '
    'obesity, about a quarter of the rate now.</p>'
    '<p>Children are classified differently from adults: obesity means a BMI at or above the 95th percentile for their age '
    'and sex on CDC’s 2000 growth charts, and severe obesity 120% of that value or more. The '
    '<a href="/childhood-obesity-statistics/">childhood obesity statistics</a> page has the trend by age, sex and race, and '
    'the <a href="/kids-bmi-calculator/">kids BMI calculator</a> shows where a child falls.</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit data-table--wrap"><caption>Children and teens aged 2 to 19, '
    'August 2021–August 2023</caption><thead><tr><th scope="col">Group</th><th scope="col" class="num">Obesity</th><th '
    'scope="col" class="num">Severe obesity</th><th scope="col" class="num">Over\u00adweight</th></tr></thead>'
    f'<tbody>{kid_rows}</tbody></table></div>'
    f'<p class="source-note">Source: {ext(U["he112"], "CDC NCHS Health E-Stat 112")}. Count: {KIDS["all"][0]}% × '
    f'{d1(D(POP_K) / Decimal(10 ** 6))} million children aged 2 to 19 ({ext(U["pop"], "CDC’s population total")}).</p></section>')
assert 0.23 < float(K1971) / float(KIDS['all'][0]) < 0.27                             # "about a quarter"

EMBED_ALT = 'Line chart: US adult obesity rose from 13.4% in 1960–62 to 40.8% in 2021–23'
EMBED_OLD = ('<figure style="margin:0;max-width:640px"><img src="https://calculatemybmi.net/us-obesity-statistics/'
             f'us-obesity-trend-1960-2023.svg" alt="{EMBED_ALT}" width="640" height="440" loading="lazy" '
             'style="width:100%;height:auto"><figcaption>Chart: <a href="https://calculatemybmi.net/us-obesity-statistics/">'
             'CalculateMyBMI</a>. Data: CDC NCHS (NHANES).</figcaption></figure>')
assert EMBED_OLD in html.unescape(src)                              # the S1 embed code, as sites may have copied it
# Same image URL, size, alt text and link, so copies already in use keep working; only the credit line changes, to name
# both surveys as the chart now does (1960-1962 is the National Health Examination Survey; CMB-022 fact-check NOTE 4).
EMBED = EMBED_OLD.replace('Data: CDC NCHS (NHANES).', 'Data: CDC NCHS (NHES, NHANES).')
assert EMBED.count('(NHES, NHANES)') == 1 and EMBED != EMBED_OLD
SVGF = '/us-obesity-statistics/us-obesity-trend-1960-2023.svg'
CSVU = '/us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv'
sec_data = (
    '<section id="use-this-data" class="content-section flow"><h2>Use this chart or data</h2>'
    '<p>The chart and the compiled data are free to reuse under CC BY 4.0: credit CalculateMyBMI and link to this page. '
    'The NCHS figures themselves are in the public domain.</p>'
    f'<figure class="figure figure--wide"><a href="{SVGF}"><img src="{SVGF}" alt="{EMBED_ALT}, while overweight stayed between '
    '30% and 35% and severe obesity rose to 10.2%" width="640" height="440" loading="lazy"></a><figcaption>The chart to embed: US '
    'adults aged 20 to 74, age-adjusted, each survey of CDC’s national series from 1960–1962 to August 2021–August 2023. '
    'Source: CDC NCHS Health E-Stat 111.</figcaption></figure>'
    f'<p><a href="{CSVU}" download>Download the data (CSV, {len(ROWS)} rows)</a>: the NCHS adult and child figures behind '
    'this page, with standard errors, survey years and the formula for each calculated value. '
    f'<a href="{SVGF}">Chart image (SVG)</a>.</p>'
    '<label class="form-label" for="obs-embed">Embed code</label>'
    f'<textarea id="obs-embed" class="embed-code" rows="5" readonly>{html.escape(EMBED)}</textarea>'
    '<p><button type="button" class="cta-button cta-button--sm" id="obs-embed-copy">Copy embed code</button></p>'
    '<script>(function(){var b=document.getElementById("obs-embed-copy"),t=document.getElementById("obs-embed");if(!b||!t)return;'
    'b.addEventListener("click",function(){function done(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy embed code";},2000);}'
    'if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t.value).then(done,function(){t.select();document.execCommand("copy");done();});}'
    'else{t.select();document.execCommand("copy");done();}});})();</script></section>')

FAQ = [
    ('Is it true that 40% of Americans are obese?',
     f'Yes. CDC’s measured survey put adult obesity at {CRUDE["obesity"]}% in August 2021 to August 2023: about {M_OB} '
     'million adults aged 20 and older had a BMI of 30 or higher.'),
    ('Is it true that 70% of Americans are overweight?',
     f'Yes, if overweight includes obesity: {OWOB}% of US adults have a BMI of 25 or higher ({CRUDE["overweight"]}% '
     f'overweight plus {CRUDE["obesity"]}% with obesity). Overweight alone, a BMI of 25.0 to 29.9, is {CRUDE["overweight"]}%.'),
    ('Are obesity rates rising or falling in the US?',
     f'In CDC’s measured data the change from {DECADE[2][1]}% (2017 to March 2020) to {DECADE[3][1]}% (August 2021 to '
     f'August 2023) was not statistically significant, and severe obesity rose from '
     f'{DECADE[0][2]}% to {DECADE[3][2]}% (age-adjusted) over the decade. Gallup’s self-reported rate fell from {G["peak"]}% in '
     f'{G["peak_year"]} to {G["rate_2025"]}% in 2025.'),
    ('Which state is #1 in obesity?',
     f'{TOP3[0][0]} had the highest estimate in 2025, {TOP3[0][1]}% of adults, followed by {TOP3[1][0]} ({TOP3[1][1]}%) '
     f'and {TOP3[2][0]} ({TOP3[2][1]}%), within each other’s margins of error, in CDC’s state surveys, where people report '
     'their own height and weight. '
     f'Mississippi, at {MS[2024]["prevalence_pct"]}% in 2024, had no 2025 estimate. The '
     '<a href="/obesity-rate-by-state/">obesity rate by state</a> page ranks every state.'),
    ('What was the obesity rate in 1960?',
     f'{OB74["1960-1962"]}% of adults aged 20 to 74 had obesity in 1960–1962 (age-adjusted), the earliest survey in CDC’s '
     'national series. '
     f'In August 2021 to August 2023 it was {OB74[LAST]}%, about three times as high.'),
    ('Why do some sources say 68% or 75% of Americans are obese?',
     'They use the definition the Lancet Commission proposed in 2025, which adds waist measures to BMI. Applied to '
     f'{F4["n"]:,} volunteers in NIH’s All of Us program, it gave {F4["new_definition"]}% ({F4["bmi_based"]}% by BMI '
     f'alone); applied to CDC’s 2017–2023 survey, {AR["new_definition"][0]}% ({AR["bmi_30_plus"][0]}% by BMI alone). '
     f'CDC’s own figure, {CRUDE["obesity"]}%, uses BMI.'),
    ('Why do some sources say 42.4% or 41.9%?',
     f'Those are earlier CDC figures: {T20_LIVE["2017-2018"][1]}% for 2017–2018 and {DECADE[2][1]}% for 2017 to March 2020 '
     f'(age-adjusted, adults 20 and older). The latest is {CRUDE["obesity"]}% for August 2021 to August 2023.'),
    ('What is the average BMI in America?',
     f'{S3["men_bmi_mean"]} for men and {S3["women_bmi_mean"]} for women aged 20 and older in August 2021 to August 2023, '
     f'and {MEAN_ALL} for all adults (our calculation from CDC’s files); the medians are {S3["men_bmi_median"]} for men '
     f'and {S3["women_bmi_median"]} for women. The typical adult’s BMI is in the overweight range.'),
    ('What age group has the highest obesity rate?',
     f'Adults aged 40 to 59: {DB_OB["all"][2]}% had obesity in August 2021 to August 2023, more than at ages 20 to 39 '
     f'({DB_OB["all"][1]}%) or 60 and older ({DB_OB["all"][3]}%).'),
    ('Are women more obese than men?',
     f'Not overall: {DB_OB["women"][0]}% of women and {DB_OB["men"][0]}% of men had obesity, a difference CDC found not '
     f'statistically significant. Severe obesity is almost twice as common in women, {DB_SV["women"][0]}% against '
     f'{DB_SV["men"][0]}%.'),
    ('What percent of Americans weigh over 300 pounds?',
     f'About {L3P[1]}%: {L3P[0]}% of US adults weighed 300 lb (136 kg) or more in August 2021 to August 2023, about '
     f'{L3P[2]}% of men and {L3P[3]}% of women (our calculation from CDC’s survey files). That fits CDC’s published 95th '
     f'percentiles: 95% of men weighed {S3["men_wt_p95_lb"]} lb ({P95KG[0]} kg) or less and 95% of women '
     f'{S3["women_wt_p95_lb"]} lb ({P95KG[1]} kg) or less.'),
    ('What percentage of Americans are a healthy weight?',
     f'About 1 in 4: {HEALTHY}% of adults 20 and older had a BMI of 18.5 to 24.9 in August 2021 to August 2023 (100% minus '
     f'CDC’s underweight, overweight and obesity shares). Among adults aged 20 to 74 (age-adjusted), the share fell from '
     f'about half, {H60}% in 1960–1962, to {H23}%.'),
]
assert round(300 * 0.45359237) == 136 and float(P95KG[0]) < 136 and float(P95KG[1]) < 136
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p>'
                   '</div></div>' for q, a in FAQ)
sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'Fryar CD, Afful J, Saif NT. {ext(U["he111"], "Prevalence of overweight, obesity, and severe obesity among adults age 20 and older: United States, 1960–1962 through August 2021–August 2023")}. '
    'NCHS Health E-Stat 111. February 2026.',
    f'Emmerich SD, Fryar CD, Stierman B, Ogden CL. {ext(U["db508"], "Obesity and severe obesity prevalence in adults: United States, August 2021–August 2023")}. '
    'NCHS Data Brief No. 508. September 2024.',
    f'Noiman AN, Fryar CD, Saif NT, Afful J. {ext(U["he112"], "Prevalence of overweight, obesity, and severe obesity among children and adolescents ages 2–19 years: United States, 1963–1965 through August 2021–August 2023")}. '
    'NCHS Health E-Stat 112. February 2026.',
    f'Ansai N, Fryar CD, Afful J. {ext(U["he119"], "Prevalence of underweight among children, adolescents, and adults: United States, 1960–1962 through August 2021–August 2023")}. '
    'NCHS Health E-Stat 119. June 2026.',
    f'Fryar CD, Gu Q, Afful J, Carroll MD, Ogden CL. {ext(U["s3"], "Anthropometric reference data for children and adults: United States, August 2021–August 2023")}. '
    'Vital and Health Statistics, Series 3, No. 50. June 2025.',
    f'National Center for Health Statistics. {ext(U["pop"], "NHANES population totals, August 2021–August 2023")} '
    '(American Community Survey 2021).',
    f'CDC. {ext(U["bmx"], "NHANES August 2021–August 2023 body measures (BMX_L)")} and demographics (DEMO_L) files: our '
    'calculation of the class 1 and class 2 shares, the mean BMI of all adults and the share at 300 lb or more.',
    f'CDC. {ext(U["maps"], "Adult Obesity Prevalence Maps")} (Behavioral Risk Factor Surveillance System, 2025 data). '
    'Updated September 24, 2026.',
    f'Gallup. {ext(U["gallup"], "Obesity Rate Declining in U.S.")} National Health and Well-Being Index. October 28, 2025.',
    f'Rubino F, et al. {ext(U["lancet"], "Definition and diagnostic criteria of clinical obesity")}. Lancet Diabetes '
    'Endocrinol 2025;13:221–62 (Lancet Commission on Clinical Obesity).',
    f'Fourman LT, et al. {ext(U["fourman"], "Implications of a New Obesity Definition Among the All of Us Cohort")}. '
    'JAMA Netw Open 2025;8(10):e2537619.',
    f'Al-Roub NM, et al. {ext(U["alroub"], "Body Mass Index and Anthropometric Criteria to Assess Obesity")}. JAMA Netw '
    'Open 2025;8(12):e2549124.',
    f'CDC. {ext(U["cats"], "Adult BMI categories")} (the class 3 name).',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. Every figure is copied from the publication named '
    'with it; “our calculation” means we computed it from CDC’s public files or from the published figures, as described '
    'below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note" id="methods"><strong>Method.</strong> Every rate comes from CDC’s examination surveys, the '
    'National Health Examination Survey for 1960–1962 and the National Health and Nutrition Examination Survey (NHANES) '
    'since 1971–1974, unless another source is named. Trained technicians measure height and weight '
    'in a mobile examination center, the results are weighted to represent the US civilian noninstitutionalized '
    f'population, and pregnant women are excluded. The 2021–2023 adult figures rest on {N_EXAM:,} examined adults aged 20 '
    f'and older; the unweighted examination response rate, all ages, was {RESP}%. Crude shares are the actual shares; '
    'age-adjusted shares are standardized to the 2000 census (ages 20 to 39, 40 to 59, and 60 and older; 60 to 74 for the '
    '20-to-74 series). We call a difference higher or lower only where CDC reports it as statistically significant, or where '
    'it is more than 2.13 times its standard error (the 95% level for the survey’s 15 degrees of freedom), worked out from '
    'CDC’s published standard errors. Counts are a share times CDC’s population total for the survey '
    f'({POPA_M} million adults, {d1(D(POP_K) / Decimal(10 ** 6))} million children aged 2 to 19), rounded. Our calculation '
    'from CDC’s 2021–2023 files (DEMO_L and BMX_L, weighted with the exam weights): the split of obesity into classes 1 '
    f'and 2, and the mean BMI of all adults, {MEAN_ALL}; the same code reproduces CDC’s published {UW}%, '
    f'{CRUDE["overweight"]}%, {CRUDE["obesity"]}% and {CRUDE["severe obesity"]}% exactly. The share at 300 lb or more '
    f'counts the {L3["all"]["n"]:,} examined adults with a measured weight ({ext(U["bmx"], "CDC’s body measures file")}).</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and data</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/kids-bmi-calculator/', 'Kids BMI calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/obesity-rate-by-state/', 'Obesity rate by state'), ('/childhood-obesity-statistics/', 'Childhood obesity statistics'),
        ('/average-weight/', 'Average weight by height'), ('/bmi-chart/', 'BMI chart'),
        ('/blog/healthy-bmi-range/', 'Healthy BMI range')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, takeaways, hero, toc, sec_how, sec_fit, tool, sec_year, sec_trend, sec_why, sec_age, sec_race, sec_sev, sec_kids,
     sec_data, sec_faq, sec_src, sec_rel]) + ' </div></main>')
assert 'style="' not in re.sub(r'(?s)<svg.*?</svg>', '', main)
assert all(f'id="{a}"' in main for a, _ in CHIPS) and '<article' not in main
for old_id in ('how-many', 'overweight', 'where-you-fit', 'by-year', 'going-down', 'age-gender-education', 'race', 'morbid',
               'children', 'use-this-data', 'methods', 'faq', 'sources'):
    assert f'id="{old_id}"' in main, old_id                         # anchors the old page had (19 pages link one of them)
assert '—' not in plain(re.sub(r'(?s)<svg.*?</svg>|<script.*?</script>|<textarea.*?</textarea>', '', main)), \
    'an em dash in the body text'
for bad in ('harvard.edu', 'heart.org', 'wikipedia.org', 'mayoclinic.org', 'clevelandclinic.org', 'nhs.uk'):
    assert bad not in main, bad                                      # BUILD.md: never cite these

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'US Obesity Rate & Statistics: 40.3% of Adults (CDC Data)'
assert src.count(f'<title>{esc(TITLE)}</title>') == 1                # kept
DESC = ('40.3% of US adults have obesity (CDC, measured, 2021–2023). The rate by year since 1960, by age, sex and race, '
        'kids, and why other sources say 37% or 75%.')
assert len(DESC) <= 160, len(DESC)
OG_T = 'US obesity rate: 40.3% of adults, and why some sources say 37% or 75%'
OG_D = ('CDC’s measured rate since 1960, by age, sex and race, with the data to download, and what the self-reported and '
        'new-definition figures count.')
OG_ALT = ('Chart: three lines across 60 years of national surveys, obesity rising steeply, overweight roughly level and severe obesity '
          'rising from near zero.')
for s_ in (DESC, OG_T, OG_D, OG_ALT): assert '"' not in s_ and '—' not in s_
PREF = SITE + '/assets/images/preferred/us-obesity-statistics-'
IMG16, IMG43, IMG11 = PREF + '16x9.png', PREF + '4x3.png', PREF + '1x1.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG16}">', src)
src = sub1(r'<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', src)
src = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
assert 'twitter:title' not in src and 'twitter:description' not in src
src = sub1(r'(<meta name="twitter:card" content="summary_large_image">)',
           f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{OG_T}">'
           f'<meta name="twitter:description" content="{OG_D}">', src)
head_part = src[:src.index('<main')]
n_style = len(re.findall(r'(?s)<style>.*?</style>', head_part)); assert n_style == 2, n_style   # shell copy + .cmb-* styles
src = re.sub(r'(?s)<style>.*?</style>', '', head_part) + src[src.index('<main'):]
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1
# The menu: this page is "Obesity Statistics" (mobile menu), already marked; nothing else is.
OBS = '<a href="/us-obesity-statistics/" class="active" aria-current="page">Obesity Statistics</a>'
assert src.count(OBS) == 1 and src.count('aria-current="page"') == 1

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 1, len(blocks)
old = json.loads(blocks[0].group(1))
assert [x['@type'] for x in old['@graph']] == ['Article', 'Dataset', 'BreadcrumbList', 'Organization', 'Person']
art_old, ds_old, crumbs = old['@graph'][0], old['@graph'][1], old['@graph'][2]
assert art_old['datePublished'] == '2026-09-30' and art_old['@id'] == URL + '#article' and ds_old['@id'] == URL + '#dataset'
assert [i['name'] for i in crumbs['itemListElement']] == ['Home', 'US Obesity Statistics']
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
ORG = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'CalculateMyBMI', 'url': SITE + '/'}
dataset = dict(ds_old)
dataset['creator'] = ORG
assert dataset['name'] == 'US obesity, overweight and severe obesity prevalence, 1960–2023 (NHANES)'
dataset['name'] = 'US obesity, overweight and severe obesity prevalence, 1960–2023 (NHES, NHANES)'
# The CSV's periods by age (build_dataset_us_obesity.py): adults from 1960-1962; children 6-11 from 1963-1965 (NHES II);
# teens 12-17 in 1966-1970 (NHES III, filed under 12-19 with a note); ages 2-19 from 1971-1974 (NHANES I).
assert {r['survey_period'] for r in ROWS if r['population'] == 'children and adolescents'} >= {'1963-1965', '1966-1970', '1971-1974'}
assert [r['age_group'] for r in ROWS if r['survey_period'] == '1963-1965'] == ['6-11']
assert [r['note'] for r in ROWS if r['survey_period'] == '1966-1970'] == ['1966-1970 value is ages 12-17, not 12-19']
dataset['description'] = (
    'Measured prevalence of overweight (BMI 25.0–29.9), obesity (BMI 30 or higher) and severe obesity (BMI 40 or higher) '
    'among US adults from 1960–1962 to August 2021–August 2023, among children aged 6–11 from 1963–1965, teens aged 12–17 '
    'in 1966–1970 and children and teens aged 2–19 from 1971–1974, '
    'with breakdowns by sex, age group, race and Hispanic origin, and education, and the standard errors. Compiled from '
    'National Center for Health Statistics publications (Health E-Stats 111, 112 and 119; Data Brief 508); calculated rows '
    'are labeled with their formulas.')
assert dataset['dateModified'] == '2026-09-30' and dataset['distribution'][0]['contentUrl'] == SITE + CSVU
assert dataset['measurementTechnique'] == 'Measured height and weight, National Health and Nutrition Examination Survey (NHANES)'
dataset['measurementTechnique'] = ('Measured height and weight: National Health Examination Survey (NHES, 1960–1970) and '
                                   'National Health and Nutrition Examination Survey (NHANES, since 1971–1974)')
dataset['dateModified'] = '{TODAY}'                 # the CSV gains two standard errors in this batch (patch_cmb022.py)
graph = [
    {'@type': 'Article', '@id': URL + '#article', 'headline': H1, 'description': DESC, 'url': URL,
     'datePublished': art_old['datePublished'], 'dateModified': '{TODAY}', 'inLanguage': 'en-US',
     'isPartOf': {'@type': 'WebSite', 'name': 'CalculateMyBMI', 'url': SITE + '/'}, 'author': PERSON, 'publisher': ORG,
     'image': [IMG11, IMG43, IMG16],
     'mainEntityOfPage': {'@type': 'WebPage', '@id': URL, 'url': URL,
                          'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}},
     'citation': [U['he111'], U['db508'], U['he112'], U['he119'], U['s3'], U['pop'], U['bmx'], U['maps'], U['gallup'],
                  U['lancet'], U['fourman'], U['alroub']],
     'isBasedOn': {'@id': URL + '#dataset'}},
    dataset,
    crumbs,
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}}
                                       for q, a in FAQ]},
]
ld = {'@context': 'https://schema.org', '@graph': graph}
src = src[:blocks[0].start()] + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' + src[blocks[0].end():]
assert src.count('{TODAY}') == 2                   # Article and Dataset dateModified

# ---------------------------------------------------------------- body
i, j = src.index('<main'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
assert src.count('og-us-obesity-statistics.png') == 0
open(PAGE, 'w', encoding='utf-8', newline='').write(src)
words = len(plain(re.sub(r'(?s)<svg.*?</svg>|<script.*?</script>|<textarea.*?</textarea>', ' ',
                         re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'us-obesity-statistics/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, '
      f'{len(FAQ)} FAQ, {len(TEXTS)} SVG labels checked; {CRUDE["obesity"]}% = about {M_OB} million adults')
