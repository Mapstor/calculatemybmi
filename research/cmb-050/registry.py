#!/usr/bin/env python3
"""CMB-050: the registry and the page map for /blog/how-to-lower-bmi/'s claims pass (claims batch 3).
  - research/data-sources.csv: four new rows, each read in Chrome on 2026-11-14 and holding the words the page uses:
      cdc-healthy-eating-weight (CDC "Tips for Healthy Eating for a Healthy Weight", dated Apr. 29, 2026),
      cdc-physical-activity-weight (CDC "Physical Activity and Your Weight and Health", dated Apr. 7, 2026, with the
        calories table the page prints six rows of),
      cdc-rethink-your-drink (CDC "Rethink Your Drink", dated Mar. 5, 2026),
      nhlbi-sleep-health-effects (NHLBI "How Sleep Affects Your Health", last updated June 15, 2022);
    cdc-losing-weight gains the five steps as CDC words them (re-read in Chrome, page dated January 17, 2025);
    cdc-about-bmi's quote is corrected: CDC's key point reads "a quick, low-cost, and reliable screening measure", not
      "quick, safe, and reliable" (the row and two pages had it wrong since CMB-012/013; apply.py fixes the pages);
    odphp-physical-activity-guidelines is re-read (unchanged);
    blog/how-to-lower-bmi joins pages_served on every row the page now cites.
  - research/page-map.csv: the page's data_source becomes cdc-losing-weight instead of "CDC healthy weight guidance
    (verify)", which check_sources.py failed.
usage: python3 research/cmb-050/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/how-to-lower-bmi'
TODAY = '2026-11-14'
CITED = ('cdc-losing-weight', 'cdc-about-bmi', 'cdc-adult-bmi-categories', 'hall-2011-energy-imbalance',
         'niddk-body-weight-planner', 'cdc-healthy-eating-weight', 'cdc-rethink-your-drink', 'medlineplus-alcohol-calories',
         'odphp-physical-activity-guidelines', 'cdc-physical-activity-weight', 'hollis-2008-food-records',
         'nhlbi-sleep-health-effects', 'cappuccio-2008-sleep-obesity', 'nhlbi-1998-obesity-guidelines',
         'orsama-2014-weight-rhythms', 'madigan-2015-self-weighing', 'nimh-eating-disorders')
COMMON = dict(access='page', tier='A', cadence='irregular', granularity='n/a', format='HTML', key_required='no',
              verified_date=TODAY, next_check='2027-11-14', status='verified', pages_served=SLUG,
              license='public domain (US federal work)')
NEW = [
    dict(COMMON, domain='cdc-healthy-eating-weight',
         source='CDC: Tips for Healthy Eating for a Healthy Weight (Healthy Weight and Growth)',
         publisher='Centers for Disease Control and Prevention',
         url='https://www.cdc.gov/healthy-weight-growth/healthy-eating/index.html',
         endpoint='https://www.cdc.gov/healthy-weight-growth/healthy-eating/index.html',
         attribution='CDC', coverage='US adults; eating patterns for weight management',
         sample_note=('Read in Chrome 2026-11-14 (page dated Apr. 29, 2026): "An eating plan that helps promote health and '
                      'manage weight includes a variety of nutrient-dense foods."; "According to the Dietary Guidelines for '
                      'Americans, a healthy eating plan: Emphasizes vegetables, fruits, protein, diary [sic] without added '
                      'sugars, healthy fats, and whole grains. Includes healthful protein options, such as seafood, meats, '
                      'poultry, eggs, legumes (beans and peas), soy products, nuts, and seeds. Is low in added sugars, sodium '
                      '(salt), saturated fats, trans fats, and cholesterol. Stays within your daily calorie needs."; tips: "Look '
                      'for frozen and canned vegetables without added salt."; "Be aware that dried and canned fruit may contain '
                      'added sugars or syrups. Choose canned varieties of fruit packed in water or in its own juice."; "If your '
                      'favorite recipe calls for frying fish or breading chicken, try healthier variations by baking or '
                      'grilling. Maybe even try beans in place of meats."'),
         notes=('CMB-050: /blog/how-to-lower-bmi/ "Eating for a Healthy Weight" and its foods FAQ. CDC links the Dietary '
                'Guidelines for Americans PDF (cdn.realfood.gov/DGA.pdf); the page cites CDC\'s page, not the PDF, and gives no '
                'servings or grams (D-06).')),
    dict(COMMON, domain='cdc-physical-activity-weight',
         source='CDC: Physical Activity and Your Weight and Health (Healthy Weight and Growth)',
         publisher='Centers for Disease Control and Prevention',
         url='https://www.cdc.gov/healthy-weight-growth/physical-activity/index.html',
         endpoint='https://www.cdc.gov/healthy-weight-growth/physical-activity/index.html',
         attribution='CDC', coverage='US adults; physical activity and weight',
         sample_note=('Read in Chrome 2026-11-14 (page dated Apr. 7, 2026): "Regular physical activity provides immediate and '
                      'long-term health benefits."; "Being physically active can improve your brain health. Other benefits '
                      'include stronger bones and muscles and better ability to perform everyday activities."; "Physical '
                      'activity also helps: Improve sleep quality. Reduce high blood pressure and risk of heart disease and '
                      'stroke. Reduce risk of type 2 diabetes. Reduce risk of several forms of cancer. Reduce arthritis pain and '
                      'associated disability. Reduce risk of osteoporosis and falls. Reduce symptoms of depression and '
                      'anxiety."; "More physical activity increases the number of calories your body uses for energy. Using '
                      'calories through physical activity, combined with reducing the calories you eat, creates a calorie '
                      'deficit that results in weight loss."; "Most weight loss occurs from decreasing calories. However, the '
                      'only way to maintain weight loss is to engage in regular physical activity."; "You may need more than the '
                      'recommended minutes of physical activity a week to maintain your weight. The exact amount of physical '
                      'activity needed to maintain a healthy weight varies greatly from person to person."; "To lose weight and '
                      'keep it off, you will need a high amount of physical activity unless you also adjust your diet to reduce '
                      'the number of calories you eat and drink. Getting to and staying at a healthy weight requires both '
                      'regular physical activity and healthy eating patterns."'),
         notes=('Calories table, "Approximate Calories/30 Minutes for a 154 lb Person": moderate: Walking (3.5 mph) 140, '
                'Bicycling (<10 mph) 145, Weight lifting (general light workout) 110; vigorous: Walking (4.5 mph) 230, Swimming '
                '(slow freestyle laps) 255, Running/jogging (5 mph) 295; footnote: "Calories burned will be higher for persons '
                'who weigh more than 154 lbs (70 kg) and lower for people who weigh less. Adapted from Dietary Guidelines for '
                'Americans 2005, page 16, Table 4." CMB-050: /blog/how-to-lower-bmi/ prints these six rows (30 minutes, 154 lb, '
                '70 kg), the deficit lines, the benefits and the diet-or-exercise FAQ.')),
    dict(COMMON, domain='cdc-rethink-your-drink', source='CDC: Rethink Your Drink (Healthy Weight and Growth)',
         publisher='Centers for Disease Control and Prevention',
         url='https://www.cdc.gov/healthy-weight-growth/rethink-your-drink/index.html',
         endpoint='https://www.cdc.gov/healthy-weight-growth/rethink-your-drink/index.html',
         attribution='CDC', coverage='US; sugary drinks',
         sample_note=('Read in Chrome 2026-11-14 (page dated Mar. 5, 2026): "Sugary drinks are the leading source of added '
                      'sugars in the American diet."; 12-ounce servings, teaspoons of sugar and total drink calories: Regular '
                      'Soda 10 and 155, Fruit Juice Drink 10 and 186, Sports Drinks 5 and 97, Plain Water 0 and 0 (sugar from '
                      'USDA FoodData Central); "Choose water instead of sugary drinks."'),
         notes='CMB-050: /blog/how-to-lower-bmi/ "Swaps CDC Suggests" (drinks: 12-ounce regular soda, 155 calories, 10 teaspoons).'),
    dict(COMMON, domain='nhlbi-sleep-health-effects',
         source='NHLBI: Sleep Deprivation and Deficiency, How Sleep Affects Your Health',
         publisher='National Heart, Lung, and Blood Institute (NIH)',
         url='https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects',
         endpoint='https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects',
         attribution='NHLBI (NIH)', coverage='US; sleep and health',
         sample_note=('Read in Chrome 2026-11-14 (last updated June 15, 2022): good-quality sleep "Helps support a healthy '
                      'balance of the hormones that make you feel hungry (ghrelin) or full (leptin): When you don\'t get enough '
                      'sleep, your level of ghrelin goes up and your level of leptin goes down. This makes you feel hungrier '
                      'than when you\'re well-rested."; "Affects how your body reacts to insulin: Insulin is the hormone that '
                      'controls your blood glucose (sugar) level. Sleep deficiency results in a higher-than-normal blood sugar '
                      'level, which may raise your risk of diabetes."'),
         notes=('CMB-050: /blog/how-to-lower-bmi/ "The Sleep-Weight Connection". Not used: NHLBI-funded research on adults '
                'who sleep 7-8 hours a night (D-06: the page gives no sleep hours of its own or anyone\'s).')),
]
LOSING_NOTE = (
    ' CMB-050 (re-read in Chrome 2026-11-14, page dated January 17, 2025): key points: "If you want to lose weight, making a '
    'specific plan can help."; "Healthy weight loss includes a lifestyle with healthy eating patterns, regular physical '
    'activity, enough sleep, and stress management."; overview: "Factors, such as medicines, medical conditions, stress, '
    'genes, hormones, environment, and age can also affect weight management."; "If you\'re concerned about your weight or '
    'have questions about your medications, talk with your health care provider." Step 1, understand your "why": write down '
    'your reasons (heart disease in the family, wanting to be more active) and place them where you see them daily; "If you '
    'are not at a healthy weight, even modest weight loss can help improve your blood pressure, cholesterol, and blood sugar '
    'levels. For example, a 5% weight reduction for a person who weighs 200 pounds is 10 pounds." Step 2, track where you '
    'are: a food and beverage diary of everything you consume for a few days, a physical activity diary (time of day, '
    'activity, duration), hours of sleep, healthy ways you are reducing stress ("Write down or use an app"); the lifestyle '
    'challenges table: a work schedule that makes activity hard (walk to work or take public transportation, take walk '
    'breaks, ask a coworker to join you for a walk at lunch or after work), sugary foods bought for the kids (have fruits and '
    'vegetables on hand, bring the family together to create healthier changes, plan meals ahead), coworkers\' treats (bring '
    'healthier snacks to share), tiredness from too little sleep (set regular bed and wake times, avoid caffeine in the '
    'afternoon and evening, turn off electronic devices at least 30 minutes before bedtime). Step 3: short-term goals with '
    'rewards, e.g. "drinking water instead of sugary beverages, taking a 15-minute evening walk, or having a vegetable with '
    'supper"; "Focus on two or three goals at a time. Effective goals are specific and realistic."; "exercise more" is not '
    'specific, "I will walk 15 minutes, 3 days a week for the first week," is specific and potentially more realistic; '
    '"Setting unrealistic goals, such as losing 20 pounds in 2 weeks, can leave you feeling defeated and frustrated."; '
    'occasional setbacks are expected: get back on track as quickly as possible, then think about how to prevent them. Step '
    '4: family members or friends, coworkers or neighbors with similar goals; "It may help to join a weight-loss program or '
    'visit a health care professional, such as a nutrition or weight-loss specialist."; your provider may refer you to a '
    'registered dietitian or clinical or community programs (the medicines, devices and surgery in the same list are left out '
    'under D-01). Step 5: revisit your goals, decide which parts of the plan work and which need changing, add a new goal '
    'when you consistently meet one, use non-food rewards. /blog/how-to-lower-bmi/ uses all of it.')
ABOUT_OLD = '"a quick, safe, and reliable screening measure"'
ABOUT_NEW = '"a quick, low-cost, and reliable screening measure"'
ABOUT_NOTE = (' CMB-050 (read in Chrome 2026-11-14, page dated Dec. 16, 2025): the key point reads "BMI is a quick, '
              'low-cost, and reliable screening measure for underweight, overweight, or obesity." This row, / and '
              '/blog/healthy-bmi-range/ had "quick, safe, and reliable" (since CMB-012 and CMB-013), corrected; the other '
              'three quotes read as above.')
ODPHP_NOTE = ' CMB-050: re-read in Chrome 2026-11-14; the adult amounts read as above.'


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
    for d, note in (('cdc-losing-weight', LOSING_NOTE), ('cdc-about-bmi', ABOUT_NOTE),
                    ('odphp-physical-activity-guidelines', ODPHP_NOTE)):
        m = by[d]
        if 'CMB-050' not in m['notes']:
            m['notes'] = (m['notes'].rstrip() + note).strip()
            m['verified_date'] = TODAY
            n += 1
    a = by['cdc-about-bmi']
    if ABOUT_OLD in a['sample_note']:
        a['sample_note'] = a['sample_note'].replace(ABOUT_OLD, ABOUT_NEW)
        n += 1
    assert ABOUT_NEW in a['sample_note']
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'cdc-losing-weight'
    if 'CMB-050' not in r['notes']:
        r['notes'] = (r['notes'] + '. CMB-050: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page; title and H1 kept (D-28).').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
