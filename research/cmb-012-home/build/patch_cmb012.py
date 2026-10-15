#!/usr/bin/env python3
"""CMB-012 patches outside the homepage, applied after gen_home.py (build record; chat runs it on a scratch tree).
1. assets/js/calculator.js: the converted unit shows one decimal in both directions, so a converted healthy limit can't
   round across the category line (72 kg at 170 cm showed "159 lbs", and 159 lb at 170 cm is BMI 25.0); "−1 lb", not "−1 lbs".
2. /men-bmi-calculator/: the US rank counts only men with a lower BMI (ties at the same recorded BMI were counted as lower),
   as on the homepage; the worked example moves from 32% to 31%. Winter 2014 is paraphrased as its abstract states it.
usage: patch_cmb012.py REPO_ROOT"""
import sys, os, re, json

ROOT = sys.argv[1]

def patch(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding='utf-8', newline='').read()
    for old, new, n in pairs:
        c = s.count(old)
        assert c == n, f'{path}: expected {n} of {old[:70]!r}, found {c}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8', newline='').write(s)

patch('assets/js/calculator.js', [
    ("// Limits are whole numbers in the user's unit; the bracketed value converts that same number.\n",
     "// Limits are whole numbers in the user's unit; the bracketed value converts that same number to one decimal, either way,\n"
     "// so a converted limit can't round across the category line (72 kg at 170 cm is 158.7 lbs, not 159; CMB-012).\n", 1),
    ("  return CMB_METRIC ? Math.round(kg * 2.20462) + ' lbs' : (lb / 2.20462).toFixed(1) + ' kg';",
     "  return CMB_METRIC ? (kg * 2.20462).toFixed(1) + ' lbs' : (lb / 2.20462).toFixed(1) + ' kg';", 1),
    ("  return CMB_METRIC ? Math.round(b.minKg * 2.20462) + '–' + Math.round(b.maxKg * 2.20462) + ' lbs' : ",
     "  return CMB_METRIC ? (b.minKg * 2.20462).toFixed(1) + '–' + (b.maxKg * 2.20462).toFixed(1) + ' lbs' : ", 1),
    ("function fmtWalt(lbs) { return CMB_METRIC ? Math.round(lbs) + ' lbs' : lbsToKg(lbs).toFixed(1) + ' kg'; }",
     "function fmtWalt(lbs) { return CMB_METRIC ? lbs.toFixed(1) + ' lbs' : lbsToKg(lbs).toFixed(1) + ' kg'; }", 1),
    ("const dU = CMB_METRIC ? Math.round(lbsToKg(diff)) : Math.round(diff), uL = CMB_METRIC ? ' kg' : ' lbs';",
     "const dU = CMB_METRIC ? Math.round(lbsToKg(diff)) : Math.round(diff), uL = CMB_METRIC ? ' kg' : (Math.abs(dU) === 1 ? ' lb' : ' lbs');", 1),
])

# Men page: same rank rule as the homepage.
MEN = 'men-bmi-calculator/index.html'
src = open(os.path.join(ROOT, MEN), encoding='utf-8').read()
m = re.search(r'<script>\(function\(\)\{var Q=(\[[^\]]*\]);var v=document\.getElementById\("men-bmi-value"\).*?\}\)\(\);</script>', src, re.S)
assert m, 'men rank script not found'
Q = json.loads(m.group(1))
assert Q == json.load(open(os.path.join(ROOT, 'research/men-pilot/men_stats.json')))['p1_p99']
new_js = ('<script>(function(){var Q=' + m.group(1) + ';var v=document.getElementById("men-bmi-value"),box=document.getElementById("men-rank");'
          'if(!v||!box)return;function pct(b){if(b<=Q[0])return 0;if(b>=Q[98])return 100;for(var i=0;i<98;i++){if(b<Q[i+1])return i+1+(b-Q[i])/(Q[i+1]-Q[i]);}return 100;}'
          'function n(x){return x>99?99:Math.round(x);}'
          'function show(){var b=parseFloat(v.textContent);if(!(b>0)){box.hidden=true;return;}'
          'var lo=pct(Math.round(b*10-1)/10),hi=100-pct(b),s=b.toFixed(1),head,txt;'
          'if(lo<1){head="Lower than "+n(hi)+"% of US men";txt="Your BMI of "+s+" is lower than about "+n(hi)+"% of US men aged 20 and over.";}'
          'else if(hi<1){head="Higher than "+n(lo)+"% of US men";txt="Your BMI of "+s+" is higher than about "+n(lo)+"% of US men aged 20 and over.";}'
          'else{head="Higher than "+n(lo)+"% of US men";txt="Your BMI of "+s+" is higher than about "+n(lo)+"% of US men aged 20 and over and lower than about "+n(hi)+"%. The median US man has a BMI of 28.2.";}'
          'document.getElementById("men-rank-value").textContent=head;document.getElementById("men-rank-text").textContent=txt;'
          'document.getElementById("men-rank-marker").style.left=Math.min(99,Math.max(1,lo))+"%";box.hidden=false;}'
          'new MutationObserver(show).observe(v,{childList:true,characterData:true,subtree:true});})();</script>')

def pct(b):
    if b <= Q[0]: return 0.0
    if b >= Q[98]: return 100.0
    for i in range(98):
        if b < Q[i + 1]: return i + 1 + (b - Q[i]) / (Q[i + 1] - Q[i])
    return 100.0
EX = round(pct(25.7))                      # the men page example: 5'10", 180 lb = BMI 25.8
assert EX == 31, EX

patch(MEN, [
    (m.group(0), new_js, 1),
    ('<dt>Compared with US men: higher than 32%</dt>', f'<dt>Compared with US men: higher than {EX}%</dt>', 1),
    ('a meta-analysis of 197,940 people found the lowest death rates across BMI 23 to 33',
     'a meta-analysis of 197,940 people found that the risk of death rose below a BMI of 23 and above 33', 2),
])
print('patched calculator.js and', MEN)

# Tests follow the new formats.
patch('research/calculator-checks/calc_e2e_playwright.py', [
    ("""            ok(hmin == f"{B['minKg']} kg ({round(B['minKg']*2.20462)} lbs)", f'{path} {cm}cm min {hmin} vs {B}')
            ok(hmax == f"{B['maxKg']} kg ({round(B['maxKg']*2.20462)} lbs)", f'{path} {cm}cm max {hmax} vs {B}')""",
     """            ok(hmin == f"{B['minKg']} kg ({B['minKg']*2.20462:.1f} lbs)", f'{path} {cm}cm min {hmin} vs {B}')
            ok(hmax == f"{B['maxKg']} kg ({B['maxKg']*2.20462:.1f} lbs)", f'{path} {cm}cm max {hmax} vs {B}')
            # the converted limits stay inside the healthy range at that height (CMB-012: 72 kg at 170 cm is 158.7 lbs, not 159)
            ok(r1(B['maxKg']*2.20462*703/h/h) <= 24.9 and r1(round(B['maxKg']*2.20462, 1)*703/h/h) <= 24.9, f'{path} {cm}cm converted max crosses 24.9')""", 1),
    ("metric_cases = [(178,82),(178,79),(178,80),(188,66),(188,65),(157,61),(157,62),(165,45),(200,140),(145,84),(159,101)]",
     "metric_cases = [(178,82),(178,79),(178,80),(188,66),(188,65),(157,61),(157,62),(165,45),(200,140),(145,84),(159,101),(170,70)]", 1),
])
patch('research/men-pilot/rank_test_playwright.py', [
    ('"""Checks the men-page rank line against the Python percentile curve. usage: rank_test.py BASEURL STATS_JSON"""',
     '"""Checks the men-page rank line against the Python percentile curve. usage: rank_test.py BASEURL STATS_JSON\n'
     'Since CMB-012 the rank counts only men with a lower BMI: the curve is read at BMI - 0.1 (BMI is recorded to 0.1)."""', 1),
    ("""        p_ = rank(bmi); r = round(p_)
        exp = 'Lower than 99% of US men' if p_ < 1 else 'Higher than 99% of US men' if p_ > 99 else f'Higher than {r}% of US men'""",
     """        lo = rank(round(bmi - 0.1, 1)); hi = 100 - rank(bmi); nn = lambda x: 99 if x > 99 else round(x)
        exp = f'Lower than {nn(hi)}% of US men' if lo < 1 else f'Higher than {nn(lo)}% of US men'""", 1),
    ("""            h = c[1]/2.54; bmi = r1(c[2]*2.20462*703/h/h)""",
     """            bmi = r1(c[2]/(c[1]/100)**2)                                  # metric BMI is kg/m2 (CMB-011)""", 1),
])
print('patched tests')

# DESIGN.md: the rules this batch adds.
patch('DESIGN.md', [
    ("- Every weight shows in the unit the user entered first and the other unit second, ideal weight and lean mass included. Metric input is computed in kg/m², US input with 703; the healthy kg limits follow kg/m².\n",
     "- Every weight shows in the unit the user entered first and the other unit second, ideal weight and lean mass included. Metric input is computed in kg/m², US input with 703; the healthy kg limits follow kg/m².\n"
     "- The converted unit has one decimal both ways (\"159 lbs (72.1 kg)\", \"72 kg (158.7 lbs)\"), so a converted limit never rounds across a category line (CMB-012; whole-pound rounding showed 72 kg at 170 cm as 159 lbs, which is BMI 25.0).\n"
     "- US rank (`.rank-box`, homepage and men page): \"higher than X%\" counts only adults with a lower BMI and \"lower than Y%\" only those with a higher one. NHANES records BMI to one decimal, so the curve is read at BMI − 0.1 for X; adults with the same BMI count on neither side (CMB-012).\n", 1),
    ("### Category badges\n",
     "### Category dots in data tables — `.cat-dot` (CMB-012)\n"
     "- A 10 px dot before the category name in a static table (`<span class=\"cat-dot normal\">`), in the strong shades. The category colour sits on the dot only; the text stays `--gray-800`.\n\n"
     "### Category badges\n", 1),
])
print('patched DESIGN.md')

# Registry (research/data-sources.csv) and page map: the homepage's sources, verified in chat on 2026-10-14.
import csv, io
def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    open(p, 'w', encoding='utf-8', newline='').write(out.getvalue())

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    def add_page(r, slug):
        ps = [x for x in r[ix['pages_served']].split(';') if x]
        if slug not in ps: ps.append(slug)
        r[ix['pages_served']] = ';'.join(ps)
    seen = set()
    for r in rows[1:]:
        d = r[ix['domain']]; seen.add(d)
        if d in ('nhanes-2021-2023-exam-files', 'nhanes-adult-weight-trends', 'nhanes-adult-obesity-2021-2023', 'nhanes-underweight',
                 'nhanes-anthropometric-reference', 'cdc-adult-bmi-categories', 'gallagher-2000-bf-ranges'):
            add_page(r, 'home')
        if d == 'nhanes-2021-2023-exam-files':
            r[ix['sample_note']] += ('. CMB-012 (2026-10-14): adults 20+ excl. pregnant (5,929; 2,680 men, 3,249 women): percentiles and '
                                     'category shares reproduce the NCHS crude prevalences exactly (underweight 1.6, overweight 32.1, '
                                     'obesity 40.3, class 3 9.4) and Series 3 means 29.4/30.0; research/home-build/home_stats.py')
        if d == 'nhanes-underweight':
            r[ix['notes']] += (' Ansai N, Fryar CD, Afful J, published 2026-06-18; quote used on /: "Poor nutrition and underlying health '
                               'conditions can result in underweight among youth and adults." (checked 2026-10-14)')
        if d == 'gallagher-2000-bf-ranges':
            r[ix['notes']] += (' CMB-012: / cites only the abstract (predictors 1/BMI, sex, age, ethnic group). Range cells to re-check '
                               'against the paper: one secondary (IJMS) gives men 20-39 8.0-20.9% and women 60+ 25.0-37.9%.')
    def row(**k):
        r = [''] * len(head)
        for a, v in k.items(): r[ix[a]] = v
        return r
    base = dict(access='page', license='public-domain', tier='A', cadence='irregular', granularity='national', format='HTML',
                key_required='no', verified_date='2026-10-14', next_check='2027-10-14', status='verified')
    new = [
        row(domain='cdc-child-bmi-categories', source='CDC Child and Teen BMI Categories', publisher='CDC',
            url='https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html', endpoint='https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
            attribution='Source: CDC, Child and Teen BMI Categories', coverage='ages 2 through 19',
            sample_note='Underweight <5th percentile; healthy 5th to <85th; overweight 85th to <95th; obesity >=95th; severe obesity >=120% of the 95th or >=35 kg/m2; page dated 2024-06-28',
            pages_served='home;kids-bmi-calculator', **base),
        row(domain='cdc-about-bmi', source='CDC About Body Mass Index (BMI)', publisher='CDC',
            url='https://www.cdc.gov/bmi/about/index.html', endpoint='https://www.cdc.gov/bmi/about/index.html',
            attribution='Source: CDC, About Body Mass Index (BMI)', coverage='adults and children (general)',
            sample_note='Quotes used: "a quick, safe, and reliable screening measure"; "does not directly measure body fat" (moderately to strongly associated with other measures); "BMI does not distinguish between fat, muscle, and bone mass"; "For individuals, BMI should be considered with other factors, such as blood pressure, cholesterol levels"; page dated 2025-12-16',
            pages_served='home', **base),
        row(domain='cdc-calculating-bmi', source='CDC Growth Chart Training: Calculating BMI', publisher='CDC',
            url='https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html', endpoint='https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
            attribution='Source: CDC, Calculating BMI', coverage='formulas (all ages)',
            sample_note='BMI = weight (kg) / [height (m)]2; = [weight (kg) / height (cm) / height (cm)] x 10,000; = weight (lb) / [height (in)]2 x 703; page dated 2024-06-18',
            pages_served='home', **base),
        row(domain='lancet-clinical-obesity-2025', source='Rubino F et al. Definition and diagnostic criteria of clinical obesity. Lancet Diabetes Endocrinol 2025;13:221-62 (Lancet Commission on Clinical Obesity)',
            publisher='The Lancet Diabetes & Endocrinology', url='https://pubmed.ncbi.nlm.nih.gov/39824205/', endpoint='https://pubmed.ncbi.nlm.nih.gov/39824205/',
            attribution='Rubino F, et al. Lancet Diabetes Endocrinol 2025', coverage='global consensus (adults and children)',
            sample_note='PubMed abstract: BMI "only as a surrogate measure of health risk at a population level"; excess adiposity confirmed by direct body-fat measurement or >=1 anthropometric criterion (waist circumference, waist-to-hip or waist-to-height ratio) in addition to BMI; 58 experts; endorsed by 76 organisations; epub 2025-01-14',
            pages_served='home', **dict(base, license='abstract cited, not reproduced', granularity='international')),
        row(domain='niddk-body-weight-planner', source='NIDDK Body Weight Planner', publisher='NIH NIDDK',
            url='https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner', endpoint='https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner',
            attribution='NIDDK Body Weight Planner', coverage='adults 18+, not pregnant or breastfeeding',
            sample_note='"allows users to make personalized calorie and physical activity plans to reach a goal weight within a specific time period"; for adults 18 or older, not for younger people or pregnant or breastfeeding women',
            pages_served='home', **base),
        row(domain='who-trs-854', source='WHO Technical Report Series 854: Physical status: the use and interpretation of anthropometry (1995)', publisher='WHO',
            url='https://www.who.int/publications/i/item/9241208546', endpoint='https://www.who.int/publications/i/item/9241208546',
            attribution='WHO, Technical Report Series 854 (1995)', coverage='international',
            sample_note='Publication page resolves (dated 1995-02-28, PDF 4.8 MB). Adult thinness grades 1/2/3 = BMI below 18.5/17/16, as quoted from this report by Cole et al., BMJ 2007 (PMC1934447), checked 2026-10-14',
            pages_served='home', **dict(base, license='WHO publication; cited, not reproduced', granularity='international', format='PDF')),
        row(domain='who-2004-asian-bmi', source='WHO Expert Consultation. Appropriate body-mass index for Asian populations and its implications for policy and intervention strategies. Lancet 2004;363:157-63',
            publisher='WHO / The Lancet', url='https://pubmed.ncbi.nlm.nih.gov/14726171/', endpoint='https://pubmed.ncbi.nlm.nih.gov/14726171/',
            attribution='WHO Expert Consultation, Lancet 2004', coverage='Asian populations',
            sample_note='Abstract: WHO BMI cut-off points retained as the international classification; public health action points 23.0, 27.5, 32.5 and 37.5 kg/m2 (abstract copy checked 2026-10-14; PubMed shows a reCAPTCHA to fetchers)',
            pages_served='home', **dict(base, license='abstract cited, not reproduced', granularity='international')),
        row(domain='winter-2014-bmi-mortality-65', source='Winter JE et al. BMI and all-cause mortality in older adults: a meta-analysis. Am J Clin Nutr 2014;99:875-90',
            publisher='American Journal of Clinical Nutrition', url='https://pubmed.ncbi.nlm.nih.gov/24452240/', endpoint='https://pubmed.ncbi.nlm.nih.gov/24452240/',
            attribution='Winter JE, et al. Am J Clin Nutr 2014', coverage='adults 65+, 32 cohort studies',
            sample_note='197,940 people aged 65+; reference BMI 23.0-23.9; HR 1.12 at 21.0-21.9 and 1.19 at 20.0-20.9; mortality risk began to increase for BMI >33.0 (abstract copy checked 2026-10-14)',
            pages_served='home;men-bmi-calculator', **dict(base, license='abstract cited, not reproduced', granularity='international')),
        row(domain='wing-2011-look-ahead', source='Wing RR et al. Benefits of modest weight loss in improving cardiovascular risk factors in overweight and obese individuals with type 2 diabetes. Diabetes Care 2011;34:1481-6',
            publisher='Diabetes Care', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/', endpoint='https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
            attribution='Wing RR, et al. Diabetes Care 2011', coverage='US adults with overweight or obesity and type 2 diabetes (Look AHEAD)',
            sample_note='5 to <10% weight loss at 1 year: greater odds of improving HbA1c, systolic and diastolic blood pressure, HDL cholesterol and triglycerides (abstract checked 2026-10-14)',
            pages_served='home;men-bmi-calculator', **dict(base, license='open access (PMC); cited, not reproduced')),
        row(domain='nhlbi-1998-obesity-guidelines', source='NHLBI Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults (NIH, 1998)',
            publisher='NIH NHLBI', url='https://www.ncbi.nlm.nih.gov/books/NBK2003/', endpoint='https://www.ncbi.nlm.nih.gov/books/NBK2003/',
            attribution='NHLBI Clinical Guidelines (NIH, 1998)', coverage='US adults',
            sample_note='Waist >102 cm (>40 in) men and >88 cm (>35 in) women = higher risk, cut points lose predictive power at BMI >=35; excess weight linked to hypertension, type 2 diabetes, coronary heart disease, stroke, sleep apnea, osteoarthritis (checked 2026-10-14 through the guideline summary in Rev Panam Salud Publica 2001; NBK2003 blocks fetchers)',
            pages_served='home;men-bmi-calculator', **base),
        row(domain='trefethen-new-bmi', source='Nick Trefethen, New BMI (University of Oxford page)', publisher='University of Oxford',
            url='https://people.maths.ox.ac.uk/trefethen/bmi.html', endpoint='https://people.maths.ox.ac.uk/trefethen/bmi.html',
            attribution='Trefethen N, New BMI (University of Oxford)', coverage='formula proposal',
            sample_note='"New formula: BMI = 1.3*weight(kg)/height(m)^2.5"; prompted by his January 2013 letter to The Economist; "not based on epidemiological studies"',
            pages_served='home;new-bmi-calculator', **dict(base, license='cited, not reproduced', tier='B', granularity='n/a')),
    ]
    for r in new:
        assert r[ix['domain']] not in seen, r[ix['domain']]
    return rows + new

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    for r in rows[1:]:
        if r[ix['slug']] == 'home':
            r[ix['wedge']] = 'Result ranked among US adults, men and women: NHANES 2021-2023 BMI percentiles (built CMB-012) + explained results panel'
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = 'D-14 rebuild CMB-012 (research/home-build/); also cites cdc-adult-bmi-categories, nhanes-adult-weight-trends, nhanes-adult-obesity-2021-2023, nhanes-underweight, nhanes-anthropometric-reference and the rows added in CMB-012'
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)
print('registry: 11 rows added, home linked; page-map home row updated')
