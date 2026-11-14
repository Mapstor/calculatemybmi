#!/usr/bin/env python3
"""CMB-049: the registry and the page map for /blog/underweight-bmi-risks/'s claims pass.
  - research/data-sources.csv: four new rows, each read in Chrome on 2026-11-14 and holding the words the page uses:
      nimh-eating-disorders (NIMH "Eating Disorders: What You Need to Know", NIH Publication No. 24-MH-4901, revised
        2024; the topic page as endpoint), niams-osteoporosis (NIAMS "Osteoporosis", last reviewed December 2022),
        owh-infertility (HHS Office on Women's Health "Infertility", page last updated June 4, 2026),
        alliance-eating-disorders-helpline (the Alliance for Eating Disorders' own page: number and hours);
    medlineplus-unintentional-weight-loss gains a CMB-049 note (causes, home care, when to contact, the visit), and
    gbmc-2016-bmi-mortality one with the bands as the page writes them;
    blog/underweight-bmi-risks joins pages_served on every row the page cites.
  - research/page-map.csv: the page's data_source becomes gbmc-2016-bmi-mortality (its main study) instead of
    "WHO; Flegal 2013 (verify)", which check_sources.py failed.
usage: python3 research/cmb-049/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/underweight-bmi-risks'
CITED = ('cdc-adult-bmi-categories', 'cdc-about-bmi', 'nhanes-underweight', 'who-trs-854', 'gbmc-2016-bmi-mortality',
         'winter-2014-bmi-mortality-65', 'cdc-pregnancy-weight-gain', 'medlineplus-unintentional-weight-loss',
         'nimh-eating-disorders', 'niams-osteoporosis', 'owh-infertility', 'alliance-eating-disorders-helpline')
COMMON = dict(access='page', tier='A', cadence='irregular', granularity='n/a', format='HTML', key_required='no',
              verified_date='2026-11-14', next_check='2027-11-14', status='verified', pages_served=SLUG)
NEW = [
    dict(COMMON, domain='nimh-eating-disorders',
         source='NIMH: Eating Disorders: What You Need to Know (NIH Publication No. 24-MH-4901, revised 2024)',
         publisher='National Institute of Mental Health (NIH)',
         url='https://www.nimh.nih.gov/health/publications/eating-disorders',
         endpoint='https://www.nimh.nih.gov/health/publications/eating-disorders ; https://www.nimh.nih.gov/health/topics/eating-disorders',
         license='public domain (the publication says so; images excluded)', attribution='National Institute of Mental Health',
         coverage='US; eating disorders (anorexia nervosa, binge-eating disorder, bulimia nervosa, ARFID)',
         sample_note=('Read in Chrome 2026-11-14: "Eating disorders are serious illnesses marked by severe disturbances to '
                      'one\'s eating behaviors."; "Eating disorders are not a choice."; "People with eating disorders can be '
                      'underweight, average weight, or overweight."; ARFID: "People with ARFID are frequently underweight." '
                      'Signs of anorexia nervosa: extremely restricted eating; intense and excessive exercise; extreme thinness '
                      '(emaciation); a relentless pursuit of thinness and unwillingness to maintain a healthy weight; intense '
                      'fear of gaining weight; distorted body image or self-image; denial of the seriousness of low body weight. '
                      'Over time: thinning of the bones (osteopenia or osteoporosis), mild anemia, muscle wasting and weakness, '
                      'delayed puberty, severe constipation, low blood pressure, slowed breathing and pulse, damage to the '
                      'structure and function of the heart, feeling tired all the time, infertility, brain damage, multiple '
                      'organ failure. "People exhibiting any combination of these symptoms may have an eating disorder and should '
                      'talk to a health care provider." Co-occurring: "most often include depression, anxiety, and substance use '
                      'disorders"; "also at a higher risk for suicide". "Eating disorders can be treated successfully. Early '
                      'detection and treatment are important for recovery." "If you have concerns about your eating behavior or '
                      'mental health, talk to a primary care provider. They can refer you to a qualified mental health '
                      'professional". "If you or someone you know is struggling or having thoughts of suicide, call or text the '
                      '988 Suicide and Crisis Lifeline at 988 or chat at 988lifeline.org. In life-threatening situations, call '
                      '911." Topic page (last reviewed December 2024) says the same of co-occurring illness and treatment.'),
         notes='CMB-049: /blog/underweight-bmi-risks/ quotes the signs, the harms, the "talk to a health care provider" line, '
               'co-occurring illness, "can be treated successfully" and the 988 line; treatment plans and medicines are left '
               'out under D-01.'),
    dict(COMMON, domain='niams-osteoporosis', source='NIAMS: Osteoporosis (health topic page)',
         publisher='National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIH)',
         url='https://www.niams.nih.gov/health-topics/osteoporosis', endpoint='https://www.niams.nih.gov/health-topics/osteoporosis',
         license='public domain (US federal work)', attribution='NIAMS (NIH)', coverage='US adults; osteoporosis risk factors',
         sample_note=('Read in Chrome 2026-11-14 (last reviewed December 2022): "Body size. Slender, thin-boned women and men are '
                      'at greater risk to develop osteoporosis because they have less bone to lose compared to larger boned women '
                      'and men."; "Diet. Beginning in childhood and into old age, a diet low in calcium and vitamin D can increase '
                      'your risk for osteoporosis and fractures. Excessive dieting or poor protein intake may increase your risk '
                      'for bone loss and osteoporosis."; other medical conditions that can raise the risk include "anorexia '
                      'nervosa".'),
         notes='CMB-049: /blog/underweight-bmi-risks/ "Osteoporosis and Bone Health".'),
    dict(COMMON, domain='owh-infertility', source="HHS Office on Women's Health: Infertility",
         publisher="US Department of Health and Human Services, Office on Women's Health",
         url='https://womenshealth.gov/a-z-topics/infertility', endpoint='https://womenshealth.gov/a-z-topics/infertility',
         license='public domain (US federal work)', attribution="Office on Women's Health (HHS)", coverage='US women and men',
         sample_note=('Read in Chrome 2026-11-14 (page last updated June 4, 2026): "Many things can change a woman\'s ability to '
                      'have a baby. These include: Age, Smoking, Excess alcohol use, Stress, Poor diet, Athletic training, Being '
                      'overweight or underweight, Sexually transmitted infections (STIs), Health problems that cause hormonal '
                      'changes"; "Most cases of female infertility are caused by problems with ovulation."; "Some signs that a '
                      'woman is not ovulating normally include irregular or absent menstrual periods." The list of things that '
                      'reduce the health or number of sperm does not include weight.'),
         notes='CMB-049: /blog/underweight-bmi-risks/ "Fertility and Pregnancy" and its fertility FAQ; the page\'s old lines '
               'on men (testosterone, sperm, libido) were cut, this page gives no weight line for men.'),
    dict(COMMON, domain='alliance-eating-disorders-helpline', source='Alliance for Eating Disorders: free helpline',
         publisher='Alliance for Eating Disorders (formerly the National Alliance for Eating Disorders)',
         url='https://www.allianceforeatingdisorders.com/', endpoint='https://www.allianceforeatingdisorders.com/',
         license='facts (a phone number and hours)', attribution='Alliance for Eating Disorders', tier='B',
         coverage='US; helpline', cadence='check yearly',
         sample_note=('Read in Chrome 2026-11-14: "CALL OUR FREE HELPLINE TODAY" +1 (866) 662-1235; "Our free helpline is run by '
                      'licensed therapists who specialize in eating disorders"; "9:00 am — 7:00 pm EST (Monday — Friday)".'),
         notes='CMB-049: the helpline on /blog/underweight-bmi-risks/ (1-866-662-1235, Monday to Friday, 9:00 am to 7:00 pm '
               'Eastern). The SAMHSA line the page carried was dropped: samhsa.gov answered 403 Forbidden in Chrome, so its '
               'number could not be checked.'),
]
MEDLINE_NOTE = (' CMB-049 (re-read in Chrome 2026-11-14, review date 1/1/2025; A.D.A.M. text, so paraphrased here and on '
                'the page): unintentional weight loss is losing 10 pounds (4.5 kg) or 5% of normal body weight over 6 to 12 '
                'months or less without knowing why. Causes it lists: appetite loss from depression, stress or anxiety, cancer '
                '(even without other symptoms), long-term infections such as AIDS or tuberculosis, chronic illness such as COPD or '
                'Parkinson disease, drugs such as amphetamines and cocaine, and medicines including chemotherapy and thyroid '
                'medicines; digestive problems that cut absorption (celiac disease, long-lasting diarrhea or infections such as '
                'parasites, chronic pancreatitis, removal of part of the small intestine, laxative overuse); and an eating '
                'disorder such as anorexia nervosa, diabetes or an overactive thyroid not yet diagnosed. Home care: diet and '
                'exercise changes a provider suggests depend on the cause. Contact a provider when someone loses more weight than '
                'is healthy for age and height, when the 10 pounds (4.5 kg) or 5% is lost in 6 to 12 months or less without a '
                'known reason, or when other symptoms come with the loss. The visit: a physical exam, a weight check, questions '
                'on history and symptoms; a dietitian may be needed for nutrition advice.')

GBMC_NOTE = (' CMB-049: /blog/underweight-bmi-risks/ writes the study\'s bands as one-decimal BMI ranges, 15.0-18.4, 18.5-19.9, '
             '20.0-22.4, 22.5-24.9 (the reference), 25.0-27.4, 27.5-29.9, 30.0-34.9, 35.0-39.9 and 40.0-59.9, with the hazard '
             'ratios above (1.51, 1.13, 1.00, 1.00, 1.07, 1.20, 1.45, 1.94, 2.76) in a bar chart and in prose; 239 studies, 32 '
             'countries (coverage).')


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
    for d, note in (('medlineplus-unintentional-weight-loss', MEDLINE_NOTE), ('gbmc-2016-bmi-mortality', GBMC_NOTE)):
        m = by[d]
        if 'CMB-049' not in m['notes']:
            m['notes'] = (m['notes'].rstrip() + note).strip()
            n += 1
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'gbmc-2016-bmi-mortality'
    if 'CMB-049' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-049: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page; title and H1 kept (D-28).').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
