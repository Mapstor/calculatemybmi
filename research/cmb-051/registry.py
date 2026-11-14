#!/usr/bin/env python3
"""CMB-051: the registry and the page map for /blog/bmi-and-health-risks/'s claims pass (claims batch 4).
  - research/data-sources.csv: two new rows, each read in Chrome on 2026-11-14 and holding the words the page uses:
      niddk-health-risks (NIDDK "Health Risks of Overweight & Obesity", last reviewed May 2023),
      nci-obesity-cancer (NCI "Obesity and Cancer" fact sheet, reviewed January 28, 2025);
    gbmc-2016-bmi-mortality gains a note on how this page writes the study;
    blog/bmi-and-health-risks joins pages_served on every row the page now cites.
  - research/page-map.csv: the page's data_source becomes niddk-health-risks instead of "Flegal 2013 JAMA; WHO; NIDDK
    (verify each)", which check_sources.py failed.
usage: python3 research/cmb-051/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-and-health-risks'
TODAY = '2026-11-14'
CITED = ('niddk-health-risks', 'nci-obesity-cancer', 'gbmc-2016-bmi-mortality', 'flegal-2013-jama-mortality',
         'winter-2014-bmi-mortality-65', 'who-trs-894-obesity', 'wing-2011-look-ahead', 'provencher-2018-nfl-combine',
         'caleyachetty-2017-mho', 'cdc-about-bmi', 'cdc-losing-weight', 'nimh-eating-disorders')
COMMON = dict(access='page', tier='A', cadence='irregular', granularity='n/a', format='HTML', key_required='no',
              verified_date=TODAY, next_check='2027-11-14', status='verified', pages_served=SLUG)
NEW = [
    dict(COMMON, domain='niddk-health-risks', source='NIDDK: Health Risks of Overweight & Obesity',
         publisher='National Institute of Diabetes and Digestive and Kidney Diseases (NIH)',
         url='https://www.niddk.nih.gov/health-information/weight-management/adult-overweight-obesity/health-risks',
         endpoint='https://www.niddk.nih.gov/health-information/weight-management/adult-overweight-obesity/health-risks',
         license='public domain (US federal work)', attribution='NIDDK (NIH)',
         coverage='US adults; health problems linked to overweight and obesity',
         sample_note=('Read in Chrome 2026-11-14 (last reviewed May 2023): "Overweight and obesity may increase your risk for '
                      'many health problems—especially if you carry extra fat around your waist. Reaching and staying at a '
                      'healthy weight can help prevent these problems, stop them from getting worse, or even make them go '
                      'away."; type 2 diabetes: "Nearly 9 in 10 people with type 2 diabetes have overweight or obesity."; '
                      '"Over time, high blood glucose can lead to heart disease, stroke, kidney disease, eye problems, nerve '
                      'damage, and other health problems."; "If you are at risk for type 2 diabetes, you may be able to prevent '
                      'or delay diabetes by losing at least 5% to 7% of your starting weight. For instance, if you weigh 200 '
                      'pounds, your goal would be to lose about 10 to 14 pounds."; high blood pressure: "Having a large body '
                      'size may increase blood pressure because your heart needs to pump harder to supply blood to all your '
                      'cells. Excess fat may also damage your kidneys, which help regulate blood pressure."; "High blood '
                      'pressure can strain your heart, damage blood vessels, and raise your risk of heart attack, stroke, kidney '
                      'disease, and death."; heart disease: "Having overweight or obesity increases your risk of developing '
                      'conditions that can lead to heart disease, such as high blood pressure, high blood cholesterol, and high '
                      'blood glucose. In addition, excess weight can also make your heart have to work harder to send blood to '
                      'all the cells in your body."; stroke: "Overweight and obesity are known to increase blood pressure—and '
                      'high blood pressure is the leading cause of strokes."; metabolic syndrome: "a group of conditions that '
                      'increase your risk for heart disease, diabetes, and stroke", at least three of large waist size, high '
                      'triglycerides, high blood pressure, high fasting blood glucose, low HDL cholesterol; "closely linked to '
                      'overweight and obesity and to a lack of physical activity"; fatty liver diseases (NAFLD and NASH) '
                      '"can lead to severe liver damage, cirrhosis, or even liver failure"; "NAFLD and NASH most often affect '
                      'people who have overweight or obesity"; "losing at least 3% to 5% of your body weight may reduce fat in '
                      'the liver"; breathing problems: "Overweight and obesity can also affect how well your lungs work, and '
                      'excess weight increases your risk for breathing problems."; "Obesity is a common cause of sleep apnea in '
                      'adults."; "you may have more fat stored around your neck, making the airway smaller"; "Untreated sleep '
                      'apnea may raise your risk for developing many health problems, including heart disease and diabetes."; '
                      '"losing weight may help reduce sleep apnea or make it go away"; asthma: "Obesity can increase your risk '
                      'of developing asthma, experiencing worse symptoms, and having a harder time managing the condition."; '
                      '"Obesity is a leading risk factor for osteoarthritis in the knees, hips, and ankles."; extra pressure on '
                      'joints and cartilage, and "If you have excess body fat, your blood may have higher levels of substances '
                      'that cause inflammation. Inflamed joints may raise your risk for osteoarthritis."; gout: "Risk factors '
                      'include having obesity"; gallbladder diseases (gallstones, cholecystitis) and pancreatitis; kidney '
                      'disease: "Obesity raises the risk of developing diabetes and high blood pressure, which are the most '
                      'common causes of chronic kidney disease (CKD). Even if you don\'t have diabetes or high blood pressure, '
                      'having obesity may increase your risk of developing CKD and speed up its progress."; pregnancy problems '
                      '(gestational diabetes, preeclampsia, needing a caesarean delivery); infertility in women and men; sexual '
                      'function problems (erectile dysfunction); mental health: "obesity can also affect mental health, '
                      'increasing the risk for developing long-term stress, body image problems, low self-esteem, depression, '
                      'eating disorders"; "people with overweight or obesity are also likely to face weight-related bias at '
                      'school and work, which may cause long-term harm to their quality of life"; "Losing excess weight has '
                      'been found to improve body image and self-esteem and reduce symptoms of depression."'),
         notes=('CMB-051: /blog/bmi-and-health-risks/ takes its condition sections from this page, lightly reworded (NIDDK is '
                'a federal source); its mentions of weight-loss surgery and medicines are left out under D-01.')),
    dict(COMMON, domain='nci-obesity-cancer', source='NCI: Obesity and Cancer (fact sheet)',
         publisher='National Cancer Institute (NIH)',
         url='https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
         endpoint='https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
         license='public domain (NCI asks for credit and a link to the original)', attribution='National Cancer Institute',
         coverage='US; obesity and cancer risk, mechanisms, attributable cases',
         sample_note=('Read in Chrome 2026-11-14 (reviewed January 28, 2025): "Compared with people of healthy weight, those '
                      'with overweight or obesity are at greater risk for many diseases, including diabetes, high blood '
                      'pressure, cardiovascular disease, stroke, and at least 13 types of cancer, as well as having an elevated '
                      'risk of death from all causes"; adult categories: 25.0 to 29.9 overweight, 30.0 to 39.9 obese, 40.0 or '
                      'higher severely obese; an IARC Working Group, "based on a review of more than 1000 such studies", found '
                      '"consistent evidence that higher amounts of body fat are associated with an increased risk of a number '
                      'of cancers": endometrial, esophageal, upper stomach, liver, kidney, multiple myeloma, meningioma, '
                      'pancreatic, colorectal, gallbladder, breast (postmenopausal), ovarian, thyroid; "The risk increases '
                      'associated with obesity are highest for endometrial and esophageal cancers."; type 1 endometrial: '
                      'severe obesity "about seven times the risk", overweight or obesity "two to four times the risk"; '
                      'esophageal: severe obesity "nearly five times the risk", obesity "more than twice the risk"; others: '
                      '"from about a 10% increase in risk to a doubling of risk"; mechanisms: fat tissue "produces excess '
                      'amounts of estrogen"; high estrogen "associated with increased risks of breast, endometrial, ovarian, and '
                      'some other cancers"; insulin and IGF-1 "associated with increased risks of colorectal, thyroid, breast, '
                      'prostate, ovarian, and endometrial cancers"; "chronic inflammation, which directly promotes tumor '
                      'growth"; adipokines: leptin "increases with increasing body fat, and high levels of leptin can promote '
                      'aberrant cell proliferation"; adiponectin "less abundant in people with obesity"; visceral fat "seems to '
                      'be more dangerous, in terms of disease risks, than overall fat or subcutaneous fat"; waist '
                      'circumference, waist-to-hip ratio, waist-to-height ratio and DXA "sometimes used along with BMI"; 2019 '
                      'US, ages 30 and older: about 43,720 new cancer cases in men (4.8%) and 92,200 in women (10.6%) "due to '
                      'excess body weight".'),
         notes=('CMB-051: /blog/bmi-and-health-risks/ cancer section, takeaway and FAQ. Left out under D-01: the fact sheet\'s '
                'paragraphs on bariatric surgery and GLP-1 medicines. Number words as the page prints them: two to four '
                'times (2 to 4), about seven times (7), nearly five times (5), more than twice (2), a doubling (2); more than '
                '1,000 studies (1000 in the sheet).')),
]
GBMC_NOTE = (' CMB-051: /blog/bmi-and-health-risks/ draws the same nine bars as the underweight page (one scale, 1.00 = 22.5 '
             'to 24.9) and writes "lowest at a BMI of 20.0 to 24.9" for the minimum at 20.0-25.0; the main analysis left '
             'out the first 5 years of follow-up (notes above).')


def rewrite(path, change):
    rows = list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8'))))
    fields = list(rows[0].keys())
    n = change(rows, fields)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def registry(rows, fields):
    n = 0
    have = {x['domain'] for x in rows}
    for r in NEW:
        if r['domain'] not in have:
            assert set(r) == set(fields), sorted(set(fields) ^ set(r))
            rows.append({k: r[k] for k in fields})
            n += 1
    by = {x['domain']: x for x in rows}
    for d in CITED:
        served = [s.strip() for s in by[d]['pages_served'].split(';') if s.strip()]
        if SLUG not in served:
            by[d]['pages_served'] = ';'.join(served + [SLUG])
            n += 1
    g = by['gbmc-2016-bmi-mortality']
    if 'CMB-051' not in g['notes']:
        g['notes'] = (g['notes'].rstrip() + GBMC_NOTE).strip()
        n += 1
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'niddk-health-risks'
    if 'CMB-051' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-051: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
