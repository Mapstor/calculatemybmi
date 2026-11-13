#!/usr/bin/env python3
"""CMB-038 SOURCES-3: registry rows for batch 4b (research/data-sources.csv): ten new rows, each read on 2026-11-13 by
the route its sample_note names, and the batch's four pages added to the rows that now serve them. The NHLBI 1998 row
gains the waist-measuring method the tracking guide now gives.
usage: python3 research/cmb-038/registry.py   (stops if a row it adds exists or a row it updates is missing)
"""
import csv
import io
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CSV = REPO / 'research' / 'data-sources.csv'
DAY = '2026-11-13'
NEXT = '2027-11-13'
STATIC = dict(cadence='static', key_required='no', verified_date=DAY, next_check=NEXT, status='verified')

NEW = [
    dict(STATIC, domain='keys-1972-indices',
         source='Keys A, Fidanza F, Karvonen MJ, Kimura N, Taylor HL. Indices of relative weight and obesity. J Chronic '
                'Dis 1972;25(6):329-343 (reprinted Int J Epidemiol 2014;43(3):655-665)',
         publisher='Journal of Chronic Diseases (Pergamon)', url='https://doi.org/10.1016/0021-9681(72)90027-6',
         endpoint='https://pubmed.ncbi.nlm.nih.gov/4650929/', access='page',
         license='Abstract; facts cited with attribution', tier='A', granularity='study-level comparison of indices',
         format='article', attribution='Keys et al., J Chronic Dis 1972',
         coverage='7,424 healthy men in 12 cohorts in five countries (US, Finland, Italy, Japan, South Africa)',
         sample_note='Abstract (via a web search, 2026-11-13; PubMed 4650929 record: J Chronic Dis 1972 Jul 1;25(6):329-43, '
                     'Keys, Fidanza, Karvonen, Kimura, Taylor; first part of the abstract on scinapse): "Analyses are '
                     'reported on the correlation with height and with subcutaneous fat thickness of relative weight '
                     'expressed as per cent of average weight at given height, and of the ratios weight/height, '
                     'weight/height squared, and the ponderal index (cube root of weight divided by height) in 7424 '
                     '\'healthy\' men in 12 cohorts in five countries. Analyses are also reported on the relationship of '
                     'those indicators of relative weight to body density in 180 [men]"; the rest of the abstract '
                     '(PubMed 24691951, the 2014 reprint; scite): "Judged by the criteria of correlation with height '
                     '(lowest is best) and to measures of body fatness (highest is best), the ponderal index is the '
                     'poorest of the relative weight indices studied."; "The ratio of weight to height squared, here '
                     'termed the body mass index, is slightly better in these respects than the simple ratio of weight '
                     'to height."; "The body mass index seems preferable over other indices of relative weight on these '
                     'grounds as well as on the simplicity of the calculation and, in contrast to percentage of average '
                     'weight, the applicability to all populations at all times." Year 1972; 7,424 men.',
         pages_served='blog/bmi-formula',
         notes='The countries: the 2014 reprint\'s introduction names men in several countries in Europe, in Japan, in '
               'South Africa and white men in the United States; the reference list names the Finnish (Karvonen) and '
               'Italian (Fidanza, Taylor) cohorts, so five countries = US, Finland, Italy, Japan, South Africa. The page '
               'says "five countries" only. The ponderal index Keys tested is the cube-root form (cube root of weight '
               'divided by height), not weight/height cubed; /blog/bmi-formula/ says so.'),
    dict(STATIC, domain='lambert-2012-football-dxa',
         source='Lambert BS, Oliver JM, Katts GR, Green JS, Martin SE, Crouse SF. DEXA or BMI: clinical considerations '
                'for evaluating obesity in collegiate division I-A American football athletes. Clin J Sport Med '
                '2012;22(5):436-438',
         publisher='Clinical Journal of Sport Medicine (Lippincott Williams & Wilkins)',
         url='https://doi.org/10.1097/JSM.0b013e31825d5d65', endpoint='https://pubmed.ncbi.nlm.nih.gov/22805182/',
         access='page', license='Abstract; facts cited with attribution', tier='A', granularity='study-level',
         format='article', attribution='Lambert et al., Clin J Sport Med 2012',
         coverage='156 Division I-A football players and 260 age- and sex-matched general-population volunteers, two '
                  'Texas universities, DXA',
         sample_note='PubMed abstract (text via a web search, 2026-11-13): "Football athletes (n = 156, 20.0 +- 1.3 years, '
                     '185.6 +- 6.5cm, 103.3 +- 20.4 kg). Comparison group (n = 260, 21.5 +- 2.7 years ...)" of '
                     '"age-matched/gender-matched general population volunteers"; "Body mass index cutoffs for '
                     'overweight/obese corresponded to the following %Fat in each group [BMI >=25 = 19.9% (CG) and 11.1% '
                     '(FBA); BMI >=30 = 27.3% (CG) and 20.2% (FBA)]"; "Football athletes had significantly higher WT, '
                     'BMI, FFM, and frequency of BMI >=25 with lower %Fat and FM than CG"; "Linemen had the highest WT, '
                     'BMI, FFM, %Fat, and frequency of BMI >=25." Authors from the Houston Methodist record. Year 2012; '
                     'BMI 25 and 30.',
         pages_served='blog/bmi-for-athletes',
         notes='The comparison group is general-population volunteers, not selected non-athletes: the page says '
               '"matched volunteers" (CMB-038; it had said "non-athletes").'),
    dict(STATIC, domain='boer-1984-lbm',
         source='Boer P. Estimated lean body mass as an index for normalization of body fluid volumes in humans. Am J '
                'Physiol 1984;247(4 Pt 2):F632-F636',
         publisher='American Journal of Physiology (American Physiological Society)',
         url='https://doi.org/10.1152/ajprenal.1984.247.4.F632', endpoint='https://pubmed.ncbi.nlm.nih.gov/6496691/',
         access='page', license='Abstract; equations cited with attribution', tier='A', granularity='equation',
         format='article', attribution='Boer, Am J Physiol 1984',
         coverage='LBM = 0.407 W + 0.267 H - 19.2 (men), 0.252 W + 0.473 H - 48.3 (women); W kg, H cm',
         sample_note='Abstract (journals.physiology.org, read in Chrome 2026-11-13; the full text is paywalled): "Blood '
                     'volume was measured in 66 healthy subjects (38 males, 28 females), and extracellular fluid volume in '
                     '54 subjects (31 males, 23 females). Volumes were normalized against body weight, height, body surface '
                     'area, leanness index, and lean body mass (estimated from body weight and height). The regression '
                     'lines of body fluid volumes against lean body mass passed through the origin on extrapolation and '
                     'were not different for males and females. None of the other indices fulfilled these criteria. It is '
                     'concluded that estimated lean body mass is a suitable index for normalization of body fluid '
                     'volumes." Volume 247, issue 4, October 1984, pages F632-F636. The equations as Caruso et al. 2018 '
                     '(PMC6110034, equations 1-2, citing Boer as reference 11; read 2026-11-13) print them: '
                     '"LBWmaleBoer=0.407 W+0.267 H-19.2", "LBWfemaleBoer=0.252 W+0.473 H-48.3".',
         pages_served='lean-body-mass',
         notes='Caruso et al. 2018 print "H the patient height in meters"; the constants only give lean masses in the '
               'range of body weights with height in cm (their own James equations use 100 x H), so cm is right. The '
               'calculator (calculateLBM) uses these constants with cm.'),
    dict(STATIC, domain='james-1976-lbm',
         source='DHSS/MRC Group on Obesity Research (Waterlow JC, James WPT). Research on Obesity. London: HMSO; 1976 '
                '(James lean body mass equations)',
         publisher='Her Majesty\'s Stationery Office', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC6110034/',
         endpoint='https://pmc.ncbi.nlm.nih.gov/articles/PMC6110034/', access='page',
         license='Equations cited with attribution', tier='B', granularity='equation', format='article',
         attribution='James 1976, as printed by Caruso et al., BioMed Res Int 2018',
         coverage='LBM = 1.1 W - 128 (W/H)^2 (men), 1.07 W - 148 (W/H)^2 (women); W kg, H cm',
         sample_note='The 1976 HMSO report is not online. Caruso D, De Santis D, Rivosecchi F, et al. Lean body '
                     'weight-tailored iodinated contrast injection in obese patient: Boer versus James formula. BioMed Res '
                     'Int 2018;2018:8521893 (PMC6110034, read 2026-11-13): equations 3-4 "LBWmaleJames=1.10 W-128 '
                     'W2/(100 H)2", "LBWfemaleJames=1.07 W-148 W2/(100 H)2", H in meters (so 100 H is cm); reference 15: '
                     '"DHSS/MRC Group on Obesity Research, Waterlow J. C., James W. P. T. Research on Obesity. London, UK: '
                     'H.M.S.O.; 1976." Equations 1-2 of the same paper are Boer\'s (reference 11, Boer 1984). Years '
                     '1976, 1984 and 2018.',
         pages_served='lean-body-mass',
         notes='Tier B: a secondary source prints the equations. "Stops rising and falls at high weights" on the page is '
               'the equations\' own arithmetic (the W squared term), not a claim from a source.'),
    dict(STATIC, domain='hume-1966-lbm',
         source='Hume R. Prediction of lean body mass from height and weight. J Clin Pathol 1966;19(4):389-391',
         publisher='Journal of Clinical Pathology (BMJ)', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC473290/',
         endpoint='https://doi.org/10.1136/jcp.19.4.389', access='page',
         license='Free full text (PMC); equations cited with attribution', tier='A', granularity='equation',
         format='article (scanned PDF)', attribution='Hume, J Clin Pathol 1966',
         coverage='LBM = 0.32810 W + 0.33929 H - 29.5336 (men), 0.29569 W + 0.41813 H - 43.2933 (women); W kg, H cm',
         sample_note='The paper (PMC scan, read in Chrome 2026-11-13): synopsis "Lean body mass, calculated from the '
                     'measurement of total body water using antipyrine space, was estimated in 29 males and 27 females"; '
                     'formulae "with multiple correlation coefficients (r) of 0.96 and 0.83 respectively"; Methods: '
                     '"Fifty-six subjects were studied (29 males and 27 females)" in four main clinical groups: no '
                     'apparent disorder, polycythaemia vera, chronic bronchitis and obesity; "The ages of the males '
                     'ranged from 40 to 77 years with a mean of 61 years. The ages of the females ranged from 37 to 80 '
                     'years with a mean of 60.0 years."; Results (page 390): males "L.B.M. = 0.32810 W + 0.33929 H - '
                     '29.5336 (equation 1)", females "L.B.M. = 0.29569 W + 0.41813 H - 43.2933 (equation 1)", W in kg, H '
                     'in cm. Year 1966; ages 37, 40, 77, 80.',
         pages_served='lean-body-mass', notes='The page prints the men\'s weight coefficient as 0.3281 (the same value).'),
    dict(STATIC, domain='caspersen-1985-fitness',
         source='Caspersen CJ, Powell KE, Christenson GM. Physical activity, exercise, and physical fitness: definitions '
                'and distinctions for health-related research. Public Health Rep 1985;100(2):126-131',
         publisher='Public Health Reports (US Public Health Service)',
         url='https://pmc.ncbi.nlm.nih.gov/articles/PMC1424733/', endpoint='https://stacks.cdc.gov/view/cdc/66195',
         access='page', license='Public domain (US federal work)', tier='A', granularity='definitions',
         format='article', attribution='Caspersen et al., Public Health Reports 1985',
         coverage='definitions of physical activity, exercise and physical fitness',
         sample_note='CDC Stacks PDF (cdc_66195_DS1.pdf, read 2026-11-13): "The health-related components of physical '
                     'fitness are (a) cardiorespiratory endurance, (b) muscular endurance, (c) muscular strength, (d) body '
                     'composition, and (e) flexibility."; Public Health Reports, March-April 1985, Vol. 100, No. 2, pages '
                     '126-130; PMC abstract: "Physical fitness is a set of attributes that are either health- or '
                     'skill-related." Year 1985.',
         pages_served='lean-body-mass', notes=''),
    dict(STATIC, domain='watson-2015-sleep-duration',
         source='Watson NF, Badr MS, Belenky G, et al. Recommended amount of sleep for a healthy adult: a joint consensus '
                'statement of the American Academy of Sleep Medicine and Sleep Research Society. Sleep '
                '2015;38(6):843-844 (also J Clin Sleep Med 2015;11(6):591-592)',
         publisher='SLEEP (AASM and SRS)', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4434546/',
         endpoint='https://pmc.ncbi.nlm.nih.gov/articles/PMC4434546/', access='page',
         license='Free full text; recommendation quoted with attribution', tier='A', granularity='recommendation',
         format='article', attribution='Watson et al., Sleep 2015 (AASM/SRS consensus statement)',
         coverage='adults aged 18 to 60', cadence='irregular',
         sample_note='PMC text (via a web search, 2026-11-13): "Adults should sleep 7 or more hours per night on a regular '
                     'basis to promote optimal health."; the panel developed "a recommendation regarding the sleep '
                     'duration, or sleep duration range, that promotes optimal health in adults aged 18 to 60 years"; '
                     'AASM\'s news release: "adults aged 18 to 60 years should sleep 7 or more hours per night on a '
                     'regular basis". Year 2015.',
         pages_served='lean-body-mass',
         notes='D-06: an official recommendation, quoted, attributed and linked; /lean-body-mass/ had linked CDC\'s 2016 '
               'press release about it.'),
    dict(STATIC, domain='who-2008-waist-hip-ratio',
         source='WHO. Waist circumference and waist-hip ratio: report of a WHO expert consultation, Geneva, 8-11 December '
                '2008 (published 2011), Table A1',
         publisher='World Health Organization', url='https://www.who.int/publications/i/item/9789241501491',
         endpoint='https://iris.who.int/bitstream/handle/10665/44583/9789241501491_eng.pdf', access='pdf',
         license='WHO publication; cut-offs cited with attribution', tier='A', granularity='cut-off points',
         format='PDF', attribution='WHO expert consultation on waist circumference and waist-hip ratio (2008)',
         coverage='adults; sex-specific cut-offs',
         sample_note='Report PDF (WHO IRIS, read in Chrome 2026-11-13), Annex A1, printed page 27, "Table A1 World Health '
                     'Organization cut-off points and risk of metabolic complications": waist circumference >94 cm (M), '
                     '>80 cm (W) increased; >102 cm (M), >88 cm (W) substantially increased; waist-hip ratio >=0.90 cm '
                     '(M), >=0.85 cm (W) substantially increased. The text above it: the WHR line is from WHO\'s 1999 '
                     'diabetes report ("waist-hip ratio above 0.90 for males and above 0.85 for females"), and "those '
                     'sex-specific cut-off points cited in the report of the WHO Expert Consultation on Obesity (2000b) '
                     'were an example only and not WHO recommendations" (the waist circumference lines). Year 2008.',
         pages_served='blog/bmi-tracking-guide;men-bmi-calculator',
         notes='/men-bmi-calculator/ has cited this report for the 0.90 line since CMB-007 without a registry row.'),
    dict(STATIC, domain='madigan-2015-self-weighing',
         source='Madigan CD, Daley AJ, Lewis AL, Aveyard P, Jolly K. Is self-weighing an effective tool for weight '
                'loss: a systematic literature review and meta-analysis. Int J Behav Nutr Phys Act 2015;12:104',
         publisher='International Journal of Behavioral Nutrition and Physical Activity (BioMed Central)',
         url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4546162/', endpoint='https://doi.org/10.1186/s12966-015-0267-4',
         access='page', license='Open access; facts cited with attribution', tier='A', granularity='meta-analysis',
         format='article', attribution='Madigan et al., IJBNPA 2015',
         coverage='randomised trials of weight loss that included self-weighing',
         sample_note='Abstract (via a web search, 2026-11-13; University of Bristol record and PMC4546162): "Only one study '
                     'examined self-weighing as a single strategy and there was no evidence it was effective (-0.5 kg 95 % '
                     'CI -1.3 to 0.3). Four trials added self-weighing/self-regulation techniques to multi-component '
                     'programmes and resulted in a significant difference of -1.7 kg (95 % CI -2.6 to -0.8)."; "There was '
                     'no significant difference in the interventions with weekly or daily weighing."; "Adding '
                     'self-weighing to a behavioural weight loss programme may improve weight loss." Year 2015; 1.7 kg; '
                     'four trials.',
         pages_served='blog/bmi-tracking-guide', notes=''),
    dict(STATIC, domain='orsama-2014-weight-rhythms',
         source='Orsama AL, Mattila E, Ermes M, van Gils M, Wansink B, Korhonen I. Weight rhythms: weight increases '
                'during weekends and decreases during weekdays. Obes Facts 2014;7(1):36-47',
         publisher='Obesity Facts (Karger)', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC5644907/',
         endpoint='https://doi.org/10.1159/000356147', access='page', license='Open access; facts cited with attribution',
         tier='A', granularity='study-level', format='article', attribution='Orsama et al., Obesity Facts 2014',
         coverage='80 adults, BMI 20.0-33.5, ages 25-62, 4,657 daily weights over 15-330 days',
         sample_note='Abstract (via a web search, 2026-11-13; PubMed 24504358, PMC5644907): "The daily weight in 80 adults '
                     '(BMI 20.0-33.5 kg/m2; age, 25-62 years) was recorded and analysed"; "A pattern of daily weight '
                     'changes was found (p <0.05), with higher weight early in the week (Sunday and Monday) and decreasing '
                     'weight during the week. Increases begin on Saturday and decreases begin on Tuesday."; "Weight '
                     'variations between weekends and weekdays should be considered as normal instead of signs of weight '
                     'gain." Year 2014; 80 adults.',
         pages_served='blog/bmi-tracking-guide',
         notes='Checked 2026-11-13: no retraction or correction found for this paper (a co-author, Brian Wansink, has '
               'retractions for other work; this study\'s data came from VTT in Finland).'),
]

PAGES = [
    ('provencher-2018-nfl-combine', 'blog/bmi-for-athletes'),
    ('nhanes-2011-2018-dxa', 'blog/bmi-for-athletes'),
    ('body-fat-method-validation', 'blog/bmi-for-athletes'),
    ('cdc-adult-bmi-categories', 'blog/bmi-for-athletes;blog/bmi-formula'),
    ('eknoyan-2008-quetelet', 'blog/bmi-formula'),
    ('nhlbi-1998-obesity-guidelines', 'blog/bmi-formula;blog/bmi-tracking-guide'),
    ('who-trs-854', 'blog/bmi-formula'),
    ('who-trs-894-obesity', 'blog/bmi-formula'),
    ('trefethen-new-bmi', 'blog/bmi-formula'),
    ('cdc-calculating-bmi', 'blog/bmi-formula'),
    ('cdc-about-bmi', 'blog/bmi-formula'),
    ('cdc-child-bmi-categories', 'blog/bmi-formula'),
    ('wing-2011-look-ahead', 'blog/bmi-tracking-guide'),
    ('niddk-body-weight-planner', 'blog/bmi-tracking-guide;lean-body-mass'),
    ('winter-2014-bmi-mortality-65', 'lean-body-mass'),
    ('volpi-2004-muscle-aging', 'lean-body-mass'),
    ('odphp-physical-activity-guidelines', 'lean-body-mass'),
    ('nhanes-2011-2018-dxa', 'lean-body-mass'),
]

NHLBI_NOTE = (' CMB-038 (read 2026-11-13 through a web search): how to measure, as the guidelines\' NHANES III protocol '
              'box gives it (NBK2004/box/A236): the examiner "palpates the upper hip bone to locate the right iliac '
              'crest. Just above the uppermost lateral border of the right iliac crest, a horizontal mark is drawn"; '
              'NHLBI\'s patient page (archived DCI "How Are Overweight and Obesity Diagnosed?"): "stand and place a tape '
              'measure around your middle, just above your hipbones. Measure your waist just after you breathe out." '
              '/blog/bmi-tracking-guide/ gives that method and the >40 in (102 cm) / >35 in (88 cm) cut-offs.')


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
    nh = have['nhlbi-1998-obesity-guidelines']
    assert 'CMB-038' not in nh['notes']
    nh['notes'] = nh['notes'].rstrip() + NHLBI_NOTE
    rows += [{k: n.get(k, '') for k in fields} for n in NEW]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print(f'{len(NEW)} rows added, {len(PAGES)} rows serve more pages; {len(rows)} rows')


if __name__ == '__main__':
    main()
