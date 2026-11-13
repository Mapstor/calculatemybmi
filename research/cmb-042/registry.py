#!/usr/bin/env python3
"""CMB-042 SOURCES-4: registry rows for the four guides (research/data-sources.csv): seventeen new rows, each read on
2026-11-13 by the route its sample_note names (WebFetch was not answered this session, so every quote came through a
web search's page text), the four pages added to the rows that now serve them, and notes added to the Eknoyan, NHLBI,
NIDDK and NICE rows for the facts the pages now take from them. The NHLBI row's endpoint becomes NBK2005, the evidence
report chapter /blog/bmi-history/ links for the NHANES III shares (its url stays NBK2003, the book).
usage: python3 research/cmb-042/registry.py   (stops if a row it adds exists or a row it updates is missing)
"""
import csv
import io
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CSV = REPO / 'research' / 'data-sources.csv'
DAY = '2026-11-13'
NEXT = '2027-11-13'
STATIC = dict(cadence='static', key_required='no', verified_date=DAY, next_check=NEXT, status='verified', access='page')
WS = 'read through a web search, 2026-11-13'

NEW = [
    dict(STATIC, domain='hirode-2020-metabolic-syndrome',
         source='Hirode G, Wong RJ. Trends in the Prevalence of Metabolic Syndrome in the United States, 2011-2016. JAMA '
                '2020;323(24):2526-2528',
         publisher='JAMA (American Medical Association)', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC7312413/',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/32573660/', license='Research letter; facts cited with attribution',
         tier='A', granularity='national prevalence by survey cycle, age, sex and race/ethnicity', format='article',
         attribution='Hirode & Wong, JAMA 2020', coverage='US adults aged 20 or more, NHANES 2011 to 2016',
         sample_note=f'PMC full text and JAMA PDF ({WS}): "syndrome prevalence was 34.7% (95% CI, 33.1%-36.3% [n = '
                     '5885])" for NHANES 2011 to 2016; crude prevalence 32.5% in 2011-2012 and 36.9% in 2015-2016 (P = .07 '
                     'for trend); 19.5% at ages 20 to 39 and 48.6% at 60 or more. Year 2020.',
         pages_served='blog/bmi-and-metabolism',
         notes='The page prints 34.7% (it had said "about 1 in 3").'),
    dict(STATIC, domain='pontzer-2021-energy-expenditure',
         source='Pontzer H, Yamada Y, Sagayama H, et al. Daily energy expenditure through the human life course. Science '
                '2021;373(6556):808-812',
         publisher='Science (AAAS)', url='https://doi.org/10.1126/science.abe5017',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/34385400/', license='Abstract; facts cited with attribution', tier='A',
         granularity='study-level', format='article', attribution='Pontzer et al., Science 2021',
         coverage='doubly labeled water measurements, ages 8 days to 95 years, 29 countries',
         sample_note=f'Abstract (university repository records, {WS}): "Total expenditure increased with fat-free mass in '
                     'a power-law manner, with four distinct life stages."; "Fat-free mass-adjusted expenditure accelerates '
                     'rapidly in neonates to ~50% above adult values at ~1 year; declines slowly to adult levels by ~20 '
                     'years; remains stable in adulthood (20 to 60 years), even during pregnancy; then declines in older '
                     'adults." Year 2021.',
         pages_served='blog/bmi-and-metabolism'),
    dict(STATIC, domain='alberti-2009-metabolic-syndrome',
         source='Alberti KGMM, Eckel RH, Grundy SM, et al. Harmonizing the metabolic syndrome: a joint interim statement. '
                'Circulation 2009;120(16):1640-1645',
         publisher='Circulation (American Heart Association)', url='https://doi.org/10.1161/CIRCULATIONAHA.109.192644',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/19805654/', license='Statement; facts cited with attribution',
         tier='A', granularity='definition and risk summary', format='article', attribution='Alberti et al., Circulation 2009',
         coverage='joint statement of IDF, NHLBI, AHA, World Heart Federation, IAS and IASO',
         sample_note=f'Statement text (World Heart Federation PDF and ESPA library copies, {WS}): "patients with the '
                     'metabolic syndrome are at twice the risk of developing CVD over the next 5 to 10 years as individuals '
                     'without the syndrome"; "the metabolic syndrome confers a 5-fold increase in risk for type 2 diabetes '
                     'mellitus"; "Three abnormal findings out of 5 would qualify a person for the metabolic syndrome." Year '
                     '2009.',
         pages_served='blog/bmi-and-metabolism',
         notes='The page\'s "2x" tile is the statement\'s "twice the risk" (2).'),
    dict(STATIC, domain='wang-2010-organ-metabolic-rates',
         source='Wang Z, Ying Z, Bosy-Westphal A, et al. Specific metabolic rates of major organs and tissues across '
                'adulthood: evaluation by mechanistic model of resting energy expenditure. Am J Clin Nutr '
                '2010;92(6):1369-1377',
         publisher='American Journal of Clinical Nutrition', url='https://doi.org/10.3945/ajcn.2010.29885',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/20962155/', license='Abstract; values cited with attribution',
         tier='A', granularity='organ and tissue metabolic rates', format='article', attribution='Wang et al., Am J Clin Nutr 2010',
         coverage='131 nonobese healthy adults, MRI organ masses and indirect calorimetry',
         sample_note=f'PubMed abstract ({WS}): Elia\'s specific resting metabolic rates (kcal per kg per day): "200 for '
                     'liver, 240 for brain, 440 for heart and kidneys, 13 for skeletal muscle, 4.5 for adipose tissue, and '
                     '12 for residual organs and tissues"; "The general applicability of Elia\'s K(i) values was validated '
                     'across adulthood"; age-adjusted for adults over 50: 12.6 for skeletal muscle and 4.4 for adipose '
                     'tissue. Year 2010.',
         pages_served='blog/bmi-and-metabolism',
         notes='Our arithmetic on the page: 13 / 4.5 = 2.9 (the tile); per pound, 13 kcal/kg = 5.9 kcal and 4.5 kcal/kg = '
               '2.0 kcal (13 and 4.5 divided by 2.20462).'),
    dict(STATIC, domain='mifflin-1990-ree',
         source='Mifflin MD, St Jeor ST, Hill LA, Scott BJ, Daugherty SA, Koh YO. A new predictive equation for resting '
                'energy expenditure in healthy individuals. Am J Clin Nutr 1990;51(2):241-247',
         publisher='American Journal of Clinical Nutrition', url='https://doi.org/10.1093/ajcn/51.2.241',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/2305711/', license='Abstract; equations cited with attribution',
         tier='A', granularity='equation', format='article', attribution='Mifflin et al., Am J Clin Nutr 1990',
         coverage='498 healthy adults aged 19 to 78, indirect calorimetry',
         sample_note=f'PubMed abstract ({WS}): "derived from data from 498 healthy subjects, including females (n = 247) '
                     'and males (n = 251), aged 19-78 y"; "REE = 9.99 x weight + 6.25 x height - 4.92 x age + 166 x sex '
                     '(males, 1; females, 0) - 161"; "REE (males) = 10 x weight (kg) + 6.25 x height (cm) - 5 x age (y) + '
                     '5; REE (females) = 10 x weight (kg) + 6.25 x height (cm) - 5 x age (y) - 161"; "The Harris-Benedict '
                     'Equations derived in 1919 overestimated measured REE by 5%"; "Fat-free mass (FFM) was the best '
                     'single predictor of REE". Year 1990.',
         pages_served='blog/bmi-and-metabolism'),
    dict(STATIC, domain='roza-shizgal-1984-harris-benedict',
         source='Roza AM, Shizgal HM. The Harris Benedict equation reevaluated: resting energy requirements and the body '
                'cell mass. Am J Clin Nutr 1984;40(1):168-182',
         publisher='American Journal of Clinical Nutrition', url='https://doi.org/10.1093/ajcn/40.1.168',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/6741850/', license='Equations cited with attribution', tier='B',
         granularity='equation', format='article', attribution='Roza & Shizgal, Am J Clin Nutr 1984',
         coverage='the Harris-Benedict equations with recalculated coefficients',
         sample_note=f'The recalculated equations as a PubMed-indexed study prints them (PubMed 11817239, "Calculating the '
                     f'basal metabolic rate and severe and morbid obesity", abstract {WS}): "the recalculated version (by '
                     'Roza et al.) was more accurate"; "BMR (men) = 88.362 + 4.799 x (length) + 13.397 x (weight) - 5.677 x '
                     '(age); BMR (women) = 447.593 + 3.098 x (length) + 9.247 x (weight) - 4.330 x (age)" (length in cm, '
                     'weight in kg). Year 1984.',
         pages_served='blog/bmi-and-metabolism',
         notes='Tier B: the paper\'s own text was not read; the coefficients come from a study that cites it.'),
    dict(STATIC, domain='caleyachetty-2017-mho',
         source='Caleyachetty R, Thomas GN, Toulis KA, et al. Metabolically healthy obese and incident cardiovascular '
                'disease events among 3.5 million men and women. J Am Coll Cardiol 2017;70(12):1429-1437',
         publisher='Journal of the American College of Cardiology (Elsevier)',
         url='https://doi.org/10.1016/j.jacc.2017.07.763', endpoint='https://wrap.warwick.ac.uk/id/eprint/94321',
         license='Abstract; facts cited with attribution', tier='A', granularity='cohort study', format='article',
         attribution='Caleyachetty et al., JACC 2017',
         coverage='3.5 million UK adults 18 or older free of cardiovascular disease, THIN records 1995 to 2015',
         sample_note=f'Abstract (WRAP and University of Birmingham records, {WS}): THIN electronic health records 1995 to '
                     '2015, a cohort of 3.5 million individuals 18 or older initially free of cardiovascular disease; body '
                     'size phenotypes by BMI category and 3 metabolic abnormalities (diabetes, hypertension, '
                     'hyperlipidemia); "During a mean follow-up period of 5.4 years, obese individuals with 0 metabolic '
                     'abnormalities had a higher risk of CHD (multivariable-adjusted hazard ratio (HR) 1.49" (95% CI 1.45 '
                     'to 1.54), cerebrovascular disease HR 1.07 (1.04 to 1.11) and heart failure HR 1.96 (1.86 to 2.06) '
                     '"compared with normal weight individuals with 0 metabolic abnormalities"; "Risk of CHD, '
                     'cerebrovascular disease, and heart failure in normal weight, overweight, and obese individuals '
                     'increased with increasing number of metabolic abnormalities." Year 2017.',
         pages_served='blog/bmi-and-metabolism',
         notes='The University of Birmingham release: "3.5 million British adults"; obesity = BMI 30 or more. 3.5 million '
               '= 3,500,000.'),
    dict(STATIC, domain='ata-thyroid-weight',
         source='American Thyroid Association. Thyroid and Weight (patient page and brochure)',
         publisher='American Thyroid Association', url='https://www.thyroid.org/thyroid-and-weight/',
         endpoint='https://www.thyroid.org/wp-content/uploads/patients/brochures/ata-thyroid-weight-brochure.pdf',
         license='Patient information; facts cited with attribution', tier='A', granularity='summary', format='web page',
         attribution='American Thyroid Association', coverage='hypothyroidism, hyperthyroidism and body weight',
         sample_note=f'Patient page ({WS}): "Most of the weight gained is actually due to retaining salt and water. For '
                     'most patients, about 5-10 pounds of weight gain may be related to the thyroid, depending on the '
                     'severity of the hypothyroidism, but individuals may differ."; the earlier page text: "Massive weight '
                     'gain is rarely associated with hypothyroidism. In general, 5-10 pounds of body weight may be '
                     'attributable to the thyroid, depending on the severity of the hypothyroidism."',
         pages_served='blog/bmi-and-metabolism'),
    dict(STATIC, domain='hall-2011-energy-imbalance',
         source='Hall KD, Sacks G, Chandramohan D, et al. Quantification of the effect of energy imbalance on bodyweight. '
                'Lancet 2011;378(9793):826-837',
         publisher='The Lancet', url='https://doi.org/10.1016/S0140-6736(11)60812-X',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/21872751/', license='Abstract and full text; facts cited with attribution',
         tier='A', granularity='model', format='article', attribution='Hall et al., Lancet 2011',
         coverage='adult bodyweight dynamics model (the basis of NIDDK\'s Body Weight Planner)',
         sample_note=f'PubMed abstract ({WS}): "the bodyweight response to a change of energy intake is slow, with half '
                     'times of about 1 year"; PMC full text (PMC3880593): "slow and steady weight loss of about 0.5 kg per '
                     'week. This ubiquitous weight-loss rule (also known as the 3500 kcal per pound rule) was derived by '
                     'estimation of the energy content of weight lost but it ignores dynamic physiological adaptations"; '
                     'the rule of thumb as Hall states it (quoted in AusFoodNews, 26 August 2011): "every change of energy '
                     'intake of 100 kJ per day will lead to an eventual body weight change of about 1 kg (equivalently, 10 '
                     'kcal per day per pound of weight change) with half of the weight change being achieved in about one '
                     'year and 95% of the weight change in about three years" (1 year, 3 years); The Lancet\'s release: '
                     '"every 10 calories per day reduction in energy intake will result in a bodyweight loss of about 1 '
                     'pound over 3 years, with half of that occurring in the first year" and doctors and dietitians have '
                     'assumed "that cutting 500 calories of energy intake per day will result in steady weight loss of '
                     'about one pound per week"; NIH\'s release of 25 August 2011: "For every pound you want to lose, '
                     'permanently cut 10 calories from your current intake per day." Year 2011.',
         pages_served='blog/how-to-lower-bmi'),
    dict(STATIC, domain='cappuccio-2008-sleep-obesity',
         source='Cappuccio FP, Taggart FM, Kandala NB, et al. Meta-analysis of short sleep duration and obesity in children '
                'and adults. Sleep 2008;31(5):619-626',
         publisher='Sleep (American Academy of Sleep Medicine)', url='https://doi.org/10.1093/sleep/31.5.619',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/18517032/', license='Abstract; facts cited with attribution',
         tier='A', granularity='meta-analysis', format='article', attribution='Cappuccio et al., Sleep 2008',
         coverage='30 studies, 36 population samples, 634,511 participants (30,002 children and 604,509 adults)',
         sample_note=f'Abstract (PubMed and WRAP, {WS}): "They included 634,511 participants (30,002 children and 604,509 '
                     'adults)"; "In children the pooled OR for short duration of sleep and obesity was 1.89 (1.46 to 2.43; P '
                     '< 0.0001). In adults the pooled OR was 1.55 (1.43 to 1.68; P < 0.0001)."; "Causal inference is '
                     'difficult due to lack of control for important confounders and inconsistent evidence of temporal '
                     'sequence in prospective studies." Year 2008.',
         pages_served='blog/how-to-lower-bmi',
         notes='The short-sleep cut-off differs between the pooled studies (news reports give five hours or less for '
               'adults; a CDC-hosted review gives less than 5 h); the page gives none.'),
    dict(STATIC, domain='hollis-2008-food-records',
         source='Hollis JF, Gullion CM, Stevens VJ, et al. Weight loss during the intensive intervention phase of the '
                'weight-loss maintenance trial. Am J Prev Med 2008;35(2):118-126',
         publisher='American Journal of Preventive Medicine', url='https://doi.org/10.1016/j.amepre.2008.04.013',
         endpoint='https://doi.org/10.1016/j.amepre.2008.04.013', license='Abstract; facts cited with attribution',
         tier='A', granularity='trial', format='article', attribution='Hollis et al., Am J Prev Med 2008',
         coverage='1,685 overweight or obese adults on blood pressure or lipid medication, 20 weekly group sessions',
         sample_note=f'Abstract (Aprifel summary and Zhenzhi records, {WS}): "Participants (n=1685) attended 20 weekly '
                     'group sessions"; they "kept 3.7 daily food records per week"; "Mean (SD) weight change was -5.8 kg '
                     '(4.4), and 69% lost at least 4 kg"; "Behavioral measures (e.g., diet records and physical activity) '
                     'accounted for most of the weight-loss variation". Year 2008.',
         pages_served='blog/how-to-lower-bmi',
         notes='Not used: the Kaiser Permanente release\'s quote of the lead author ("twice as much weight"), which is not '
               'in the abstract.'),
    dict(STATIC, domain='medlineplus-alcohol-calories',
         source='MedlinePlus (US National Library of Medicine): Alcohol and diet (image page 17023)',
         publisher='MedlinePlus', url='https://medlineplus.gov/ency/imagepages/17023.htm',
         endpoint='https://medlineplus.gov/ency/imagepages/17023.htm', license='Public domain (US government)', tier='A',
         granularity='fact', format='web page', attribution='MedlinePlus', coverage='energy from alcohol',
         sample_note=f'Page text ({WS}): "Alcohol is considered a macronutrient in that it provides energy (about 7 '
                     'calories per gram)."; review date 4/19/2025.',
         pages_served='blog/how-to-lower-bmi'),
    dict(STATIC, domain='cdc-losing-weight',
         source='CDC: Steps for Losing Weight (Healthy Weight and Growth)',
         publisher='Centers for Disease Control and Prevention',
         url='https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
         endpoint='https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
         license='Public domain (US government)', tier='A', granularity='guidance', format='web page',
         attribution='CDC', coverage='adults',
         sample_note=f'Page text ({WS}): "People who lose weight at a gradual, steady pace—about 1 to 2 pounds a '
                     'week—are more likely to keep the weight off than people who lose weight quicker."; the 2009 '
                     'version: "people who lose weight gradually and steadily (about 1 to 2 pounds per week) are more '
                     'successful at keeping weight off."',
         pages_served='blog/how-to-lower-bmi;blog/waist-to-height-ratio'),
    dict(STATIC, domain='nih-1985-consensus-obesity',
         source='Health implications of obesity: an NIH Consensus Development Conference. Int J Obes 1985;9(3):155-170 '
                '(consensus statement: Ann Intern Med 1985;103(6 Pt 2):1073-1077)',
         publisher='National Institutes of Health', url='https://pubmed.ncbi.nlm.nih.gov/3840463/',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/3840463/', license='Abstract; facts cited with attribution', tier='A',
         granularity='consensus statement', format='article', attribution='NIH, 1985',
         coverage='NIH Consensus Development Conference on the Health Implications of Obesity, February 11-13, 1985',
         sample_note=f'PubMed abstract ({WS}): "A Consensus Development Conference on the Health Implications of Obesity '
                     'was held in February 1985 at the National Institutes of Health in Bethesda"; it "provides reference '
                     'tables of body mass index (BMI) values and weight goals ... to illustrate the potential clinical value '
                     'of wider use of the BMI, as recommended in the conference"; the panel\'s statement as a 1986 JAMA '
                     'letter quotes it (Frankel HM, JAMA 1986;255:1292): treatment "is strongly advised ... for the '
                     'thirty-four million adult Americans [who] have a body mass index (BMI) greater than 27.8 (men) or '
                     '27.3 (women)". Year 1985.',
         pages_served='blog/bmi-history'),
    dict(STATIC, domain='wells-2014-bmi-commentary',
         source='Wells JCK. Commentary: The paradox of body mass index in obesity assessment: not a good index of '
                'adiposity, but not a bad index of cardio-metabolic risk. Int J Epidemiol 2014;43(3):672-674',
         publisher='International Journal of Epidemiology', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4052141/',
         endpoint='https://doi.org/10.1093/ije/dyu060', license='Open access (CC BY-NC); quoted with attribution',
         tier='A', granularity='commentary', format='article', attribution='Wells, Int J Epidemiol 2014',
         coverage='history of BMI as the primary obesity index',
         sample_note=f'PMC and UCL Discovery PDF text ({WS}): "a very simple statistical construct that was first proposed '
                     'by Adolphe Quetelet in 1832"; Quetelet (A Treatise on Man and the Development of his Faculties, '
                     '1842): "If man increased equally in all dimensions, his weight at different ages would be as the cube '
                     'of his height. Now, this is not what we really observe."; "Alongside Quetelet\'s WT/HT2, others had '
                     'suggested WT/HT3, W/H and HT/WT0.33."; "In a classic paper published in 1972, Keys and colleagues set '
                     'out to resolve this dilemma"; "It was only after BMI had already become established as the primary '
                     'obesity index that the accurate assessment of human body composition became possible in large '
                     'samples." Year 2014.',
         pages_served='blog/bmi-history'),
    dict(STATIC, domain='nuttall-2015-bmi-review',
         source='Nuttall FQ. Body Mass Index: Obesity, BMI, and Health: A Critical Review. Nutr Today 2015;50(3):117-128',
         publisher='Nutrition Today (Wolters Kluwer)', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4890841/',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/27340299/', license='Open access; facts cited with attribution',
         tier='A', granularity='review', format='article', attribution='Nuttall, Nutr Today 2015',
         coverage='history of weight-for-height tables and BMI',
         sample_note=f'PMC full text ({WS}): "the Metropolitan Life Insurance Company in 1959 published tables of average '
                     'body weights for heights (Wt/Ht) by gender and at different ages. This was based on data from 1935 to '
                     '1953 from more than 4 million adults, mostly men"; "The latter was referred to as the \'ideal\' or '
                     'later the \'desirable\' weight."; "frame size based on elbow width was included in the Metropolitan '
                     'Life weight/height tables, even though it was never validated." Year 2015.',
         pages_served='blog/bmi-history',
         notes='More than 4 million = 4,000,000 adults (the page: more than 4 million).'),
    dict(STATIC, domain='browning-2010-whtr-review',
         source='Browning LM, Hsieh SD, Ashwell M. A systematic review of waist-to-height ratio as a screening tool for '
                'the prediction of cardiovascular disease and diabetes: 0.5 could be a suitable global boundary value. '
                'Nutr Res Rev 2010;23(2):247-269',
         publisher='Nutrition Research Reviews (Cambridge University Press)',
         url='https://doi.org/10.1017/S0954422410000144', endpoint='https://pubmed.ncbi.nlm.nih.gov/20819243/',
         license='Abstract; facts cited with attribution', tier='A', granularity='systematic review', format='article',
         attribution='Browning et al., Nutr Res Rev 2010', coverage='78 studies published 1950 to 2008',
         sample_note=f'Abstract (PubMed and Peeref records, {WS}): "This systematic review collated seventy-eight studies" '
                     '(78) "published in English between 1950 and 2008"; "mean area under ROC (AUROC) values of 0.704, '
                     '0.693 and 0.671 for WHtR, WC and BMI, respectively"; "Mean boundary values for WHtR, covering all '
                     'cardiometabolic outcomes, from studies in fourteen different countries and including Caucasian, '
                     'Asian and Central American subjects, were 0.50 for men and 0.50 for women"; "a weighted mean '
                     'boundary value of 0.5, supporting the simple public health message \'keep your waist circumference '
                     'to less than half your height\'". Year 2010.',
         pages_served='blog/waist-to-height-ratio',
         notes='The page writes "14 countries" for the abstract\'s "fourteen different countries".'),
]

PAGES = [
    ('volpi-2004-muscle-aging', 'blog/bmi-and-metabolism'),
    ('cdc-about-bmi', 'blog/bmi-and-metabolism;blog/bmi-history'),
    ('niddk-body-weight-planner', 'blog/how-to-lower-bmi'),
    ('odphp-physical-activity-guidelines', 'blog/how-to-lower-bmi;blog/waist-to-height-ratio'),
    ('nhlbi-1998-obesity-guidelines', 'blog/how-to-lower-bmi;blog/bmi-history'),
    ('eknoyan-2008-quetelet', 'blog/bmi-history'),
    ('keys-1972-indices', 'blog/bmi-history'),
    ('who-trs-854', 'blog/bmi-history'),
    ('who-trs-894-obesity', 'blog/bmi-history'),
    ('who-2004-asian-bmi', 'blog/bmi-history'),
    ('who-obesity-fact-sheet', 'blog/bmi-history'),
    ('winter-2014-bmi-mortality-65', 'blog/bmi-history'),
    ('trefethen-new-bmi', 'blog/bmi-history'),
    ('nhanes-2011-2018-dxa', 'blog/bmi-history'),
    ('nice-ng246-ethnicity-thresholds', 'blog/waist-to-height-ratio;blog/bmi-history'),
    ('ashwell-2012-whtr-meta-analysis', 'blog/waist-to-height-ratio'),
    ('who-2008-waist-hip-ratio', 'blog/waist-to-height-ratio'),
]

NOTES = {
    'eknoyan-2008-quetelet':
        f' CMB-042 (the full text on typeset.io, {WS}): "Born in the historic Belgian town of Gent on 22 [February '
        '1796]"; Quetelet applied probability calculus "to study human physical characteristics and social aptitudes" '
        'and "is considered a founder of the social sciences"; he "became the first to develop height and weight tables '
        'to study their relationships"; the abstract: "The quest for a practical index of relative body weight that began '
        'shortly after actuaries reported the increased mortality of their overweight policyholders culminated after '
        'World War II, when the relationship between weight and cardiovascular disease became the subject of '
        'epidemiological studies"; "\'the weight increases as the square of the height\', known as the Quetelet Index '
        'until it was termed the Body Mass Index in 1972 by Ancel Keys (1904-2004)"; "Louis I. Dublin (1882-1969), a '
        'statistician and vice president of the Metropolitan Life Insurance Company, was the first to lead the '
        'development of tables of normal weights, based on the average weights recorded for a given height", thirds '
        'labelled "\'small\', \'medium\' and \'large\' frames" and termed "\'ideal\' weights, later less presumptuously '
        'labelled \'desirable\' weight"; "In developing his index, Quetelet had no interest in obesity. His concern was '
        'defining the characteristics of \'normal man\' and fitting the distribution around the norm" (as quoted from '
        'the article by T. Taylor, Conversable Economist, 2020, and Psychology Today, 2016).',
    'nhlbi-1998-obesity-guidelines':
        f' CMB-042 ({WS}): the guidelines\' rationale (NHLBI\'s archived e-textbook, ratnl/20.htm): "According to NHANES '
        'III data, 54.9 percent of U.S. adults aged 20 years and older are either overweight or obese; 32.6 percent are '
        'overweight, defined as having a body mass index (BMI) of 25.0 to 29.9 kg/m2; and 22.3 percent are obese with a '
        'BMI of [30 or more]" (Flegal et al., Int J Obes 1998, PubMed 9481598: "54.9% overall"); the treatment goals '
        '(e-textbook txgd/431.htm): "All patients with a BMI of 30 or those with a BMI of 25 to 29.9 kg/m2 (or a high '
        'waist circumference) and two or more risk factors should attempt to lose weight"; the executive summary '
        '(NBK2008): "Treatment of overweight is recommended only when patients have two or more risk factors or a high '
        'waist circumference." Endpoint NBK2005: the evidence report chapter /blog/bmi-history/ links.',
    'niddk-body-weight-planner':
        f' CMB-042 (NIDDK, "Research Behind the Body Weight Planner", {WS}): "The research behind the Body Weight Planner '
        'is from work done by Dr. Kevin Hall and his research group"; "This research was published as part of The Lancet '
        'Series on Obesity (August 27, 2011)" (Hall et al., row hall-2011-energy-imbalance); the planner "allows users to '
        'make personalized calorie and physical activity plans to reach a goal weight within a specific time period and '
        'to maintain it afterwards".',
    'nice-ng246-ethnicity-thresholds':
        f' CMB-042 ({WS}): NG246\'s overview, last reviewed 8 January 2026: "We amended recommendations 1.10.5, 1.10.10 '
        'and 1.10.11 ... to clarify that waist-to-height ratios should only be used to classify the degree of central '
        'adiposity in children and young people aged 5 years and over"; box 1: "For children and young people aged 5 '
        'years and over, see the NHS waist-to-height ratio calculator"; NICE quality standard QS212 gives the same '
        'classes for "children and young people of both sexes and all ethnicities" (0.4 to 0.49 healthy, 0.5 to 0.59 '
        'increased); the guideline as GPnotebook quotes it: "in adults with BMI below 35 kg/m2, measure and use their '
        'waist-to-height ratio, as well as their BMI"; "When talking to a child, young person, and their families and '
        'carers, explain that they should try and keep their waist to half their height (so a waist-to-height-ratio of '
        'under 0.5)"; the chapter on identifying and assessing central adiposity: encourage adults to "seek advice and further clinical assessments ... '
        'from a healthcare professional if the measurement indicates an increased health risk".',
}
NHLBI_ENDPOINT = 'https://www.ncbi.nlm.nih.gov/books/NBK2005/'


def main():
    raw = CSV.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    have = {r['domain']: r for r in rows}
    for n in NEW:
        assert n['domain'] not in have, n['domain']
        assert set(n) <= set(fields), set(n) - set(fields)
    for d, add in PAGES:
        r = have[d]
        cur = [x for x in r['pages_served'].split(';') if x]
        r['pages_served'] = ';'.join(cur + [x for x in add.split(';') if x not in cur])
    for d, add in NOTES.items():
        r = have[d]
        assert 'CMB-042' not in r['notes'], d
        r['notes'] = (r['notes'].rstrip() + add).strip()
    have['nhlbi-1998-obesity-guidelines']['endpoint'] = NHLBI_ENDPOINT
    rows += [{k: n.get(k, '') for k in fields} for n in NEW]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print(f'{len(NEW)} rows added, {len(PAGES)} rows serve more pages, {len(NOTES)} rows gain notes; {len(rows)} rows')


if __name__ == '__main__':
    main()
