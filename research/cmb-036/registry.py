#!/usr/bin/env python3
"""CMB-036 SOURCES-1: registry rows for the batch (research/data-sources.csv). Six new rows and the facts read on
2026-11-13 added to nine existing ones. Each fact names where it was read: PubMed itself shows a reCAPTCHA to fetchers,
so abstracts came from PMC full texts, OpenAlex records or university repository copies, and cdc.gov pages through the
text a web search returned for them (chat's shell cannot reach either site).
usage: python3 research/cmb-036/registry.py   (stops if a row it adds exists or a row it updates is missing)
"""
import csv
import io
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CSV = REPO / 'research' / 'data-sources.csv'
DAY = '2026-11-13'
NEXT = '2027-11-13'

NEW = [
    dict(domain='flegal-2013-jama-mortality',
         source='Flegal KM, Kit BK, Orpana H, Graubard BI. Association of all-cause mortality with overweight and obesity '
                'using standard body mass index categories: a systematic review and meta-analysis. JAMA 2013;309(1):71-82',
         publisher='JAMA (American Medical Association); author manuscript in PMC',
         url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/', endpoint='https://pubmed.ncbi.nlm.nih.gov/23280227/',
         access='page', license='abstract cited, not reproduced', tier='A', cadence='static', granularity='international',
         format='HTML', key_required='no', attribution='Flegal KM, et al. JAMA 2013',
         verified_date=DAY, next_check=NEXT, coverage='97 prospective studies, general populations',
         sample_note='Abstract (PMC4855514, read 2026-11-13): "97 studies were retained for analysis"; "more than 2.88 '
                     'million individuals and more than 270 000 deaths" (2,880,000 and 270,000); HR vs normal weight (BMI 18.5-<25): overweight '
                     '0.94 (0.91-0.96), obesity all grades 1.18 (1.12-1.25), grade 1 obesity (30-<35) 0.95 (0.88-1.01), '
                     'grades 2 and 3 obesity (BMI >=35) 1.29 (1.18-1.41)',
         status='verified', pages_served='blog/bmi-categories;blog/bmi-and-health-risks',
         notes='PMID 23280227. Pages quote the hazard ratios, not percentages worked out from them (CMB-036).'),
    dict(domain='provencher-2018-nfl-combine',
         source='Provencher MT, Chahla J, Sanchez G, et al. Body mass index versus body fat percentage in prospective '
                'National Football League athletes: overestimation of obesity rate in athletes at the National Football '
                'League Scouting Combine. J Strength Cond Res 2018;32(4):1013-1019',
         publisher='Journal of Strength and Conditioning Research (NSCA)',
         url='https://doi.org/10.1519/JSC.0000000000002449',
         endpoint='https://api.openalex.org/works/doi:10.1519/JSC.0000000000002449',
         access='page', license='abstract cited, not reproduced', tier='A', cadence='static', granularity='US (NFL '
         'Scouting Combine)', format='HTML', key_required='no', attribution='Provencher MT, et al. J Strength Cond Res 2018',
         verified_date=DAY, next_check=NEXT, coverage='NFL Scouting Combine athletes, 2010-2016',
         sample_note='Abstract (OpenAlex record, read 2026-11-13): body fat by air displacement plethysmography at the '
                     'Combine 2010-2016; BMI classed 53.4% of the athletes as obese, body fat 8.9%; PMID 29351164',
         status='verified', pages_served='blog/bmi-categories;blog/bmi-limitations;blog/bmi-and-health-risks',
         notes='The DOI page refused the fetcher (2026-11-13); the abstract was read from OpenAlex.'),
    dict(domain='volpi-2004-muscle-aging',
         source='Volpi E, Nazemi R, Fujita S. Muscle tissue changes with aging. Curr Opin Clin Nutr Metab Care '
                '2004;7(4):405-410',
         publisher='Current Opinion in Clinical Nutrition and Metabolic Care; author manuscript in PMC',
         url='https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/', endpoint='https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/',
         access='page', license='cited, not reproduced', tier='A', cadence='static', granularity='review',
         format='HTML', key_required='no', attribution='Volpi E, et al. 2004',
         verified_date=DAY, next_check=NEXT, coverage='adults (review)',
         sample_note='PMC full text (read 2026-11-13): "Muscle mass decreases approximately 3-8% per decade after the age '
                     'of 30" and "this rate of decline is even higher after the age of 60"; sarcopenia: "the involuntary '
                     'loss of muscle mass, strength, and function"; PMID 15192443',
         status='verified', pages_served='blog/bmi-limitations',
         notes='Quoted on five pages (§5); the others get this row as their audit reaches them.'),
    dict(domain='ashwell-2012-whtr-meta-analysis',
         source='Ashwell M, Gunn P, Gibson S. Waist-to-height ratio is a better screening tool than waist circumference '
                'and BMI for adult cardiometabolic risk factors: systematic review and meta-analysis. Obes Rev '
                '2012;13(3):275-286',
         publisher='Obesity Reviews (World Obesity Federation, Wiley)',
         url='https://pubmed.ncbi.nlm.nih.gov/22106927/', endpoint='https://doi.org/10.1111/j.1467-789X.2011.00952.x',
         access='page', license='abstract cited, not reproduced', tier='A', cadence='static', granularity='international',
         format='HTML', key_required='no', attribution='Ashwell M, et al. Obes Rev 2012',
         verified_date=DAY, next_check=NEXT, coverage='31 studies, more than 300,000 adults',
         sample_note='Abstract (OpenAlex record, read 2026-11-13): 31 studies, more than 300,000 adults; "the superiority '
                     'of WHtR over WC and BMI for detecting cardiometabolic risk factors in both sexes"; "Waist-to-height '
                     'ratio should therefore be considered as a screening tool"; online 2011, issue 2012',
         status='verified', pages_served='blog/bmi-limitations', notes=''),
    dict(domain='eknoyan-2008-quetelet',
         source='Eknoyan G. Adolphe Quetelet (1796-1874): the average man and indices of obesity. Nephrol Dial Transplant '
                '2008;23(1):47-51',
         publisher='Nephrology Dialysis Transplantation (Oxford University Press)',
         url='https://doi.org/10.1093/ndt/gfm517', endpoint='https://pubmed.ncbi.nlm.nih.gov/17890752/',
         access='page', license='abstract cited, not reproduced', tier='A', cadence='static', granularity='history',
         format='HTML', key_required='no', attribution='Eknoyan G. Nephrol Dial Transplant 2008',
         verified_date=DAY, next_check=NEXT, coverage='history of the Quetelet index and the term body mass index',
         sample_note='Abstract (OpenAlex record, read 2026-11-13): Quetelet (1796-1874) "was a Belgian mathematician, '
                     'astronomer and statistician"; "the Quetelet Index described in 1832"; his book "published in 1835"; '
                     '"until it was termed the Body Mass Index in 1972 by Ancel Keys (1904-2004)"',
         status='verified', pages_served='blog/bmi-limitations',
         notes='The dates Quetelet 1832 and Keys 1972 repeat on four pages (§5); the others get this row as their audit '
               'reaches them. Online 2007, issue 2008.'),
    dict(domain='who-trs-894-obesity',
         source='WHO. Obesity: preventing and managing the global epidemic. Report of a WHO Consultation. WHO Technical '
                'Report Series 894 (2000)',
         publisher='WHO', url='https://pubmed.ncbi.nlm.nih.gov/11234459/', endpoint='https://iris.who.int/handle/10665/42330',
         access='page', license='WHO publication; cited, not reproduced', tier='A', cadence='irregular',
         granularity='international', format='PDF', key_required='no',
         attribution='WHO, Technical Report Series 894 (2000)', verified_date=DAY, next_check=NEXT,
         coverage='international adult classification of overweight and obesity',
         sample_note='PubMed record 11234459 (via search, 2026-11-13): World Health Organ Tech Rep Ser. 2000;894:i-xii, '
                     '1-253; the abstract (Carolina Population Center listing): the Consultation "considered the system '
                     'for classifying overweight and obesity based on the body mass index, and concluded that a coherent '
                     'system is now available and should be adopted internationally"; obese class I 30.0-34.9, class II '
                     '35.0-39.9, class III >=40, as tabulated from this report in J Sports Sci Med (Table 4, "Source: '
                     '(WHO, 2000)")',
         status='verified', pages_served='blog/bmi-categories;blog/bmi-chart-explained',
         notes='WHO IRIS and the who.int publication page refused the fetcher (2026-11-13); the class names come through '
               'a table that cites this report, as who-trs-854 does through Cole et al.'),
]

# (domain, field, text to add); sample_note and notes get "; " + text, pages_served gets the pages it lacks
UPDATE = [
    ('winter-2014-bmi-mortality-65', 'sample_note', '32 cohort studies (coverage)'),
    ('winter-2014-bmi-mortality-65', 'pages_served', 'calculators;blog/bmi-by-age;blog/bmi-chart-explained;'
                                                     'blog/bmi-and-health-risks;blog/bmi-categories;blog/bmi-limitations'),
    ('nhanes-adult-obesity-2021-2023', 'sample_note',
     'published September 2024; by age 20-39 35.5, 60+ 38.9 ("The prevalence of obesity in adults ages 40-59 was 46.4%, '
     'which was higher than the prevalence in adults ages 20-39 (35.5%) and 60 and older (38.9%)"); Figure 1 note: '
     'age-adjusted men 39.3, women 41.4 (db508.htm and the CDC Stacks PDF as returned by a web search, 2026-11-13)'),
    ('nhanes-adult-obesity-2021-2023', 'pages_served', 'blog/bmi-by-age;blog/bmi-chart-explained;blog/bmi-categories'),
    ('nhanes-adult-weight-trends', 'sample_note',
     'Table 1, 20 and older, Aug 2021-Aug 2023 (n 5,929), age-adjusted percent (SE): men overweight 35.5 (1.4), obesity '
     '39.3 (1.9), severe 6.8 (0.7); women overweight 28.1 (0.9), obesity 41.4 (2.3), severe 12.6 (1.0) (hestat111.htm '
     'as returned by a web search, 2026-11-13)'),
    ('nhanes-adult-weight-trends', 'pages_served', 'blog/bmi-chart-explained;blog/bmi-by-age'),
    ('who-2004-asian-bmi', 'sample_note',
     '"The consultation concluded that the proportion of Asian people with a high risk of type 2 diabetes and '
     'cardiovascular disease is substantial at BMIs lower than the existing WHO cut-off point for overweight (>=25 '
     'kg/m2)" (abstract on the Monash University research repository record, read 2026-11-13)'),
    ('who-2004-asian-bmi', 'pages_served', 'blog/bmi-categories;blog/bmi-limitations'),
    ('who-trs-854', 'notes',
     'CMB-036 (read 2026-11-13 through a web search): a WHO EMRO publication (applications.emro.who.int/dsaf/dsa55.pdf) '
     'says the expert committee on "Physical Status: the Use and Interpretation of Anthropometry" gave three grades of '
     'thinness, "Grade 1: BMI 17.0-18.49 (mild thinness) Grade 2: BMI 16.0-16.99 (moderate thinness) Grade 3: BMI <16 '
     '(severe thinness)"; WHO\'s TB Knowledge Sharing Platform also defines moderate thinness in adults as BMI '
     '16.00-16.99 and severe thinness as below 16. So the calculator\'s "moderate thinness" and "severe thinness" next '
     'to "WHO, 1995" are the report\'s grades 2 and 3 under WHO\'s own names.'),
    ('who-trs-854', 'pages_served', 'blog/bmi-categories;blog/bmi-chart-explained'),
    ('nhlbi-1998-obesity-guidelines', 'notes',
     'CMB-036 (the guidelines\' "Prevalence and Time Trends" text on NHLBI\'s archived e_txtbk pages, read through a web '
     'search 2026-11-13): earlier US surveys used "a statistical one that corresponded to the 85th percentile of body '
     'mass index (BMI) for men and women aged 20 through 29 years in NHANES II"; "Adults in these surveys have been '
     'categorized as overweight with a BMI greater than or equal to 27.8 kg/m2 for men and greater than or equal to '
     '27.3 kg/m2 for women". CDC\'s MMWR 00046647 gives the same: overweight at 27.8 (men) and 27.3 (women), "85th '
     'percentiles from NHANES II for ages 20-29 years".'),
    ('nhlbi-1998-obesity-guidelines', 'pages_served', 'blog/bmi-categories'),
    ('cdc-adult-bmi-categories', 'pages_served', 'blog/bmi-chart-explained;blog/bmi-categories'),
    ('cdc-about-bmi', 'pages_served', 'blog/bmi-chart-explained'),
    ('gbmc-2016-bmi-mortality', 'pages_served', 'blog/bmi-chart-explained'),
    ('wing-2011-look-ahead', 'pages_served', 'blog/bmi-and-health-risks'),
    ('lancet-clinical-obesity-2025', 'notes', 'CMB-036: / now gives the BMI > 40 exception next to its two Commission '
                                              'lines.'),
]


def main():
    raw = CSV.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    have = {r['domain']: r for r in rows}
    for n in NEW:
        assert n['domain'] not in have, n['domain']
        assert set(n) <= set(fields), set(n) - set(fields)
    for d, f, text in UPDATE:
        r = have[d]
        if f == 'pages_served':
            cur = [x for x in r[f].split(';') if x]
            r[f] = ';'.join(cur + [x for x in text.split(';') if x not in cur])
        else:
            assert text not in r[f], (d, f)
            r[f] = (r[f].rstrip() + '; ' + text) if r[f].strip() else text
        if f in ('sample_note', 'notes') and DAY in text:   # a fact read today
            r['verified_date'] = DAY
    rows += [{k: n.get(k, '') for k in fields} for n in NEW]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print(f'{len(NEW)} rows added, {len(UPDATE)} updates; {len(rows)} rows')


if __name__ == '__main__':
    main()
