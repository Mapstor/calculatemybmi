#!/usr/bin/env python3
"""CMB-050 CLAIMS-3: claims pass batch 3 (DEVLOG §5 P1) on /blog/how-to-lower-bmi/ (32 probe hits), plus one misquote
of CDC found while sourcing it.
Every sentence now says what a registry row says, or goes (D-10); no targets of our own (D-06); the doctor lines are
CDC's and NIMH's own "when" (§4). Sources read in Chrome 2026-11-14 (registry.py records them): CDC "Steps for Losing
Weight" (January 17, 2025: the five steps, even modest loss, the lifestyle challenges, the provider line), CDC "Tips for
Healthy Eating for a Healthy Weight" (Apr. 29, 2026, citing the Dietary Guidelines), CDC "Physical Activity and Your
Weight and Health" (Apr. 7, 2026: the deficit, the benefits, the calories table), CDC "Rethink Your Drink" (Mar. 5,
2026), NHLBI "How Sleep Affects Your Health" (ghrelin, leptin, blood sugar), the Physical Activity Guidelines (re-read),
CDC "About BMI" (Dec. 16, 2025); already in the registry: Hall 2011, NIDDK's Body Weight Planner, Hollis 2008, Cappuccio
2008, MedlinePlus (alcohol), NHLBI 1998, Orsama 2014, Madigan 2015, NIMH.
Out: the plate method and the portion, "Foods to Emphasize" and "Foods to Limit" claims (satiety, blood sugar spikes,
"designed to override satiety signals", hormone function), the cardio and strength benefit lists ("boosts metabolism",
"burns calories even at rest", "essential for long-term maintenance"), "Behavioral interventions significantly improve",
meal planning, triggers, self-compassion and environment-design tips, "Set a Target With a Professional", the cravings,
energy and recovery sleep lines, cortisol and the stress-technique list, "Unrealistic expectations are a major reason",
the SMART acronym and our own goal example, the energy, clothes-fit and inches cards, water retention, muscle gain and
calorie creep, "Your body adapts to repetitive workouts", "Patience Is Key", three unsourced doctor items, the old
disclaimer's advice, and the FAQ lines on metabolism, muscle density, protein and weighing anxiety.
In: CDC's eating plan and swaps, the activity amounts for weight, CDC's calories for six activities, CDC's benefit list,
CDC's five steps and three of its lifestyle challenges, NHLBI on ghrelin, leptin and blood sugar, CDC's sleep tips,
CDC's goal advice and example, NIH's waist cut-offs, CDC on modest loss, Hall on why loss slows, Orsama's weekly rhythm,
Madigan on daily or weekly weighing, the CDC and NIMH provider lines.
Also: CDC's About BMI page calls BMI "a quick, low-cost, and reliable screening measure"; / and /blog/healthy-bmi-range/
quoted it as "quick, safe, and reliable" (and so did their generators): corrected, with their dates.
Title, H1 and URL kept (D-28). Meta descriptions, the Article description, the FAQPage JSON-LD (all seven visible
answers), dateModified, article:modified_time and lastmod follow. Files are checked by SHA-256 first; every marker must
occur once.
usage: python3 research/cmb-050/apply.py [--check]   Run order from main: registry.py, apply.py."""
import datetime
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PG, SM, HOME, HBR = 'blog/how-to-lower-bmi/index.html', 'sitemap.xml', 'index.html', 'blog/healthy-bmi-range/index.html'
GEN_HOME, GEN_HBR = 'research/home-build/gen_home.py', 'research/healthy-range-build/gen_hbr.py'
BASE = {PG: 'a7a48270e8ce74b607cc51393b8505a77d7421292bf79cbf24ec2f26cfc1f59f',
        SM: 'f50759d41f091b3e3d7a9d4cf7bda5c339514fe1945662c20f7d94b1fa563954',
        HOME: '4b7e75bfa58a9b9026c12ab3e2b6bcbe029a95874c35add566017396aac54f4e',
        HBR: 'c2617110e9e28c70f6e656ab9b61a881a72701e3169ac844336ede91fd129c60',
        GEN_HOME: '9dd4527cba1d9118182884eb1f868fdb9059f6a4099a3a7b57a1ea7752f70c78',
        GEN_HBR: 'd59e2afc505adb9cf3faf7254d06864e6e6baaa81234dd5fbb040175bdaf905f'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'cdc_eat': 'https://www.cdc.gov/healthy-weight-growth/healthy-eating/index.html',
    'cdc_pa': 'https://www.cdc.gov/healthy-weight-growth/physical-activity/index.html',
    'cdc_drink': 'https://www.cdc.gov/healthy-weight-growth/rethink-your-drink/index.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_cats': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'hall': 'https://pubmed.ncbi.nlm.nih.gov/21872751/',
    'bwp': 'https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner',
    'medline': 'https://medlineplus.gov/ency/imagepages/17023.htm',
    'pag': ('https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/'
            'top-10-things-know'),
    'hollis': 'https://doi.org/10.1016/j.amepre.2008.04.013',
    'nhlbi_sleep': 'https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects',
    'nhlbi98': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'orsama': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5644907/',
    'madigan': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4546162/',
    'nimh': 'https://www.nimh.nih.gov/health/publications/eating-disorders',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


def step(title, body, h='h3'):
    return (f'<div class="numbered-step"> <div class="numbered-step-content"> <{h}>{title}</{h}> <p>{body}</p> </div> '
            '</div> ')


def card(n, title, body):
    return (f'<div class="info-card"> <div class="info-card-icon">{n}</div> <h3>{title}</h3> <p>{body}</p> </div> ')


def grab(src, start, end):
    """The original fragment from start through the first end after it (kept word for word)."""
    i = src.index(start)
    j = src.index(end, i) + len(end)
    assert src.count(start) == 1, start[:60]
    return src[i:j]


def body(src):
    t_cats = grab(src, '<div class="table-responsive"><table class="data-table"><tr><th>BMI Range</th>', '</table></div>')
    t_point = grab(src, '<div class="table-responsive"><table class="data-table"> <thead> <tr> <th>Your Height</th>',
                   '</table></div>')
    t_down = grab(src, '<div class="table-responsive"><table class="data-table"><tr><th>Starting BMI</th>', '</table></div>')
    p_formula = grab(src, '<p>The BMI formula is straightforward:', '</p>')
    hall = grab(src, '<h3>The 3,500 kcal rule', '</p>')
    pag = grab(src, '<p>The federal Physical Activity Guidelines say', '</p>')
    stat = grab(src, '<div class="stat-grid">', 'Cappuccio et al., Sleep 2008</a>).</p>')
    down_p = grab(src, '<p>CDC notes that people who lose about 1 to 2 pounds a week are more likely to keep the weight off '
                       '(<a href="https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html" target="_blank" '
                       'rel="noopener">CDC</a>). The weight it takes', '</p>')
    tk_keep = [grab(src, '<li><strong>Lose weight gradually:</strong>', '</li>'),
               grab(src, '<li><strong>The 3,500 kcal rule overstates long-term loss:</strong>', '</li>')]
    return (
        '<p class="intro-text">BMI is weight divided by height squared, so for an adult it falls only when weight does. CDC '
        'describes healthy weight loss as a lifestyle with healthy eating patterns, regular physical activity, enough sleep '
        f'and stress management ({a("cdc_lw", "CDC")}). Below: how much weight one BMI point is at your height, what the '
        'official guidance says on each of those four, and CDC’s five steps for getting started.</p> '
        '<!-- Key Takeaways --> <div class="key-takeaways"> <div class="key-takeaways-title">Key Takeaways</div> <ul> '
        + tk_keep[0] + ' ' + tk_keep[1] + ' '
        '<li><strong>Eating and activity:</strong> most weight loss comes from eating fewer calories, and regular physical '
        f'activity is the only way to keep it off, CDC says ({a("cdc_pa", "CDC")})</li> '
        '<li><strong>Even modest loss helps:</strong> if you are not at a healthy weight, CDC says even modest weight loss can '
        f'help improve blood pressure, cholesterol and blood sugar levels; 5% of 200 pounds is 10 pounds ({a("cdc_lw", "CDC")})</li> '
        f'<li><strong>Healthy weight:</strong> a BMI of 18.5 to 24.9 for adults ({a("cdc_cats", "CDC")}; see our '
        '<a href="/blog/healthy-bmi-range/">healthy BMI guide</a>)</li> '
        '<li>Use our <a href="/">BMI calculator</a> to track your progress</li> </ul> </div> '
        '<!-- Table of Contents --> <div class="toc"> <div class="toc-title">In This Guide</div> <ul class="toc-list"> '
        '<li><a href="#understanding-bmi">Understanding BMI and Weight Loss</a></li> '
        '<li><a href="#calorie-deficit">Creating a Calorie Deficit</a></li> '
        '<li><a href="#dietary-changes">Eating for a Healthy Weight</a></li> '
        '<li><a href="#exercise-recommendations">Exercise Recommendations</a></li> '
        '<li><a href="#behavior-modification">CDC’s Five Steps</a></li> '
        '<li><a href="#sleep-stress">Sleep and Stress Management</a></li> '
        '<li><a href="#realistic-goals">Setting Realistic Goals</a></li> '
        '<li><a href="#tracking-progress">Tracking Progress Beyond the Scale</a></li> '
        '<li><a href="#weight-plateaus">When Weight Loss Plateaus</a></li> '
        '<li><a href="#medical-help">When to Seek Medical Help</a></li> '
        '<li><a href="#faq">Frequently Asked Questions</a></li> </ul> </div> '
        # 1 Understanding BMI
        '<!-- Section 1: Understanding BMI --> <h2 id="understanding-bmi">Understanding BMI and Weight Loss</h2> '
        '<p>CDC calls BMI “a quick, low-cost, and reliable screening measure” for underweight, overweight and obesity, though '
        f'it does not directly measure body fat ({a("cdc_about", "CDC")}).</p> '
        + p_formula + ' ' + t_cats + ' '
        '<p>More on each category in our guides to <a href="/blog/bmi-categories/">BMI categories</a> and '
        '<a href="/blog/bmi-and-health-risks/">BMI and health risks</a>.</p> '
        '<h3>How Much Weight Do You Need to Lose?</h3> ' + t_point + ' '
        '<p>The <a href="/ideal-weight/">ideal weight calculator</a> shows what four published formulas give for your '
        'height.</p> '
        # 2 Calorie deficit
        '<!-- Section 2: Calorie Deficit --> <h2 id="calorie-deficit">Creating a Calorie Deficit: The Foundation of Weight '
        'Loss</h2> '
        '<p>More physical activity raises the number of calories your body uses, and using calories through activity while '
        'eating fewer creates a calorie deficit that results in weight loss, CDC says. Most of the loss, it adds, comes from '
        f'eating fewer calories ({a("cdc_pa", "CDC")}).</p> '
        + hall + ' '
        f'<h3>Start From an Official Estimate</h3> <p>NIDDK’s {a("bwp", "Body Weight Planner")} makes a personal calorie and '
        'physical activity plan to reach a goal weight by a chosen date and to keep it afterwards, from the model described '
        'above.</p> '
        # 3 Eating
        '<!-- Section 3: Eating --> <h2 id="dietary-changes">Eating for a Healthy Weight</h2> '
        '<p>CDC says an eating plan that helps promote health and manage weight includes a variety of nutrient-dense foods. '
        'Citing the Dietary Guidelines for Americans, it describes a healthy eating plan as one that '
        f'({a("cdc_eat", "CDC")}):</p> '
        '<ul> <li>Emphasizes vegetables, fruits, protein, dairy without added sugars, healthy fats and whole grains</li> '
        '<li>Includes protein foods such as seafood, meats, poultry, eggs, legumes (beans and peas), soy products, nuts and '
        'seeds</li> <li>Is low in added sugars, sodium (salt), saturated fats, trans fats and cholesterol</li> '
        '<li>Stays within your daily calorie needs</li> </ul> '
        '<h3>Swaps CDC Suggests</h3> <ul> '
        '<li><strong>Drinks:</strong> water instead of sugary drinks, the leading source of added sugars in the American '
        f'diet; a 12-ounce regular soda has about 155 calories and 10 teaspoons of sugar ({a("cdc_drink", "CDC")})</li> '
        '<li><strong>Cooking:</strong> baking or grilling instead of frying fish or breading chicken, and beans in place of '
        f'meat ({a("cdc_eat", "CDC")})</li> '
        '<li><strong>Fruit:</strong> canned fruit packed in water or its own juice, since dried and canned fruit may contain '
        f'added sugars or syrups ({a("cdc_eat", "CDC")})</li> '
        f'<li><strong>Vegetables:</strong> frozen and canned vegetables without added salt ({a("cdc_eat", "CDC")})</li> '
        f'<li><strong>Alcohol:</strong> it counts too, at about 7 calories per gram ({a("medline", "MedlinePlus")})</li> </ul> '
        # 4 Exercise
        '<!-- Section 4: Exercise --> <h2 id="exercise-recommendations">Exercise Recommendations for Lowering BMI</h2> '
        '<h3>How Much Activity the Guidelines Call For</h3> ' + pag + ' '
        '<p>For weight, CDC adds that you may need more than that to maintain your weight, and that the amount varies greatly '
        'from person to person. To lose weight and keep it off, you will need a high amount of activity unless you also cut '
        f'the calories you eat and drink ({a("cdc_pa", "CDC")}).</p> '
        '<h3>Calories Used in 30 Minutes</h3> '
        '<p>The figures are for a 154-pound (70 kg) person; people who weigh more use more, and people who weigh less use '
        f'fewer ({a("cdc_pa", "CDC")}).</p> '
        '<div class="table-responsive"><table class="data-table"> <thead> <tr> <th>Activity</th> <th>Intensity</th> '
        '<th>Calories</th> </tr> </thead> <tbody> '
        '<tr><td>Walking (3.5 mph)</td><td>Moderate</td><td>140</td></tr> '
        '<tr><td>Bicycling (under 10 mph)</td><td>Moderate</td><td>145</td></tr> '
        '<tr><td>Weight lifting (general light workout)</td><td>Moderate</td><td>110</td></tr> '
        '<tr><td>Walking (4.5 mph)</td><td>Vigorous</td><td>230</td></tr> '
        '<tr><td>Swimming (slow freestyle laps)</td><td>Vigorous</td><td>255</td></tr> '
        '<tr><td>Running or jogging (5 mph)</td><td>Vigorous</td><td>295</td></tr> </tbody> </table></div> '
        f'<p class="source-note">Source: {a("cdc_pa", "CDC, Physical Activity and Your Weight and Health")}, adapted from '
        'the Dietary Guidelines for Americans 2005.</p> '
        '<h3>What Regular Activity Does</h3> '
        '<p>CDC lists stronger bones and muscles, better brain health and a better ability to do everyday activities among the '
        'benefits. Physical activity also helps improve sleep quality, it says, and reduce high blood pressure, the risk of '
        'heart disease, stroke, type 2 diabetes, several forms of cancer, osteoporosis and falls, arthritis pain, and symptoms '
        f'of depression and anxiety ({a("cdc_pa", "CDC")}).</p> '
        '<p>For body composition beyond BMI, see <a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a> and '
        '<a href="/lean-body-mass/">lean body mass</a>.</p> '
        # 5 CDC's five steps
        '<!-- Section 5: Five Steps --> <h2 id="behavior-modification">CDC’s Five Steps for Losing Weight</h2> '
        '<p>If you want to lose weight, CDC says making a specific plan can help, and it sets out five steps for getting '
        f'started ({a("cdc_lw", "CDC")}):</p> <div class="numbered-steps"> '
        + step('Understand Your “Why”', 'Write down why you want to lose weight, whether heart disease runs in your family or '
               'you want to be more active, and keep the list where you’ll see it every day.')
        + step('Track Where You Are', 'For a few days, write down or log in an app everything you eat and drink, your '
               'physical activity (time of day, activity, duration), your hours of sleep and the healthy ways you’re reducing '
               'stress. In a 20-week group program for 1,685 adults, who lost 5.8 kg on average, the food records people kept '
               'and their physical activity accounted for most of the differences in how much they lost '
               f'({a("hollis", "Hollis et al., 2008")}).')
        + step('Set Specific Goals', 'Pick two or three short-term goals at a time, such as water instead of sugary drinks, a '
               '15-minute evening walk or a vegetable with supper. <a href="#realistic-goals">Setting Realistic Goals</a> '
               'has CDC’s test for a specific goal.')
        + step('Find Support', 'Family and friends who back your efforts, or coworkers and neighbors with similar goals who '
               'might share recipes and plan group activities. CDC says it may help to join a weight-loss program or visit a '
               f'health care professional, such as a nutrition or weight-loss specialist ({a("cdc_lw", "CDC")}).')
        + step('Monitor Your Progress', 'Revisit your goals regularly: keep the parts of your plan that work, change the rest, '
               'add a new goal once you’re meeting one consistently, and reward yourself with something other than food '
               f'({a("cdc_lw", "CDC")}).')
        + '</div> <h3>Everyday Obstacles</h3> '
        f'<p>CDC’s examples of lifestyle challenges, with ways around them ({a("cdc_lw", "CDC")}):</p> <ul> '
        '<li><strong>Work makes it hard to be active:</strong> walk to work or take public transportation, take walk breaks, '
        'or ask a coworker to walk with you at lunch or after work</li> '
        '<li><strong>Sugary foods bought for the kids:</strong> keep fruits and vegetables on hand to grab, make healthier '
        'changes as a family, and plan meals ahead</li> '
        '<li><strong>Coworkers bring in treats:</strong> bring healthier snacks to share</li> </ul> '
        '<p>For tracking your BMI over the weeks, see our <a href="/blog/bmi-tracking-guide/">BMI tracking guide</a>.</p> '
        # 6 Sleep and stress
        '<!-- Section 6: Sleep and Stress --> <h2 id="sleep-stress">Sleep and Stress Management</h2> '
        '<p>CDC counts enough sleep and stress management as part of healthy weight loss, and names stress among the factors '
        'that can affect weight management, alongside medicines, medical conditions, genes, hormones, environment and age '
        f'({a("cdc_lw", "CDC")}).</p> '
        '<h3>The Sleep-Weight Connection</h3> '
        '<p>Sleep helps keep the hunger hormone ghrelin and the fullness hormone leptin in balance. Without enough sleep, '
        'ghrelin goes up and leptin goes down, and you feel hungrier than when you’re well rested. Sleep deficiency also leaves '
        f'blood sugar higher than normal, which may raise the risk of diabetes ({a("nhlbi_sleep", "NHLBI")}).</p> '
        + stat + ' '
        '<p>If you’re tired because you’re not getting enough sleep, CDC suggests regular bed and wake times, no caffeine in '
        'the afternoon and evening, and turning off electronic devices at least 30 minutes before bedtime '
        f'({a("cdc_lw", "CDC")}).</p> '
        # 7 Goals
        '<!-- Section 7: Realistic Goals --> <h2 id="realistic-goals">Setting Realistic Goals</h2> '
        '<p>CDC warns that unrealistic goals, such as losing 20 pounds in 2 weeks, can leave you feeling defeated and '
        f'frustrated ({a("cdc_lw", "CDC")}).</p> '
        '<h3>Weight to Lose for One Category Down</h3> ' + down_p + ' ' + t_down + ' '
        '<h3>What Makes a Goal Specific</h3> '
        '<p>CDC’s advice is two or three short-term goals at a time, each specific and realistic, with a reward along the way '
        f'({a("cdc_lw", "CDC")}):</p> '
        '<blockquote> Not specific: “Exercise more.”<br> Specific, and potentially more realistic: “I will walk 15 minutes, 3 '
        'days a week for the first week.” </blockquote> '
        '<p>Occasional setbacks are expected, CDC says: get back on track as quickly as you can, then think about how to '
        'prevent the same setback next time. To read your targets, see our <a href="/blog/bmi-categories/">BMI categories '
        'guide</a>.</p> '
        # 8 Tracking
        '<!-- Section 8: Tracking Progress --> <h2 id="tracking-progress">Tracking Progress Beyond the Scale</h2> '
        '<p>Alongside weight and BMI, NIH and CDC give three more things to watch:</p> <div class="info-card-grid"> '
        + card(1, 'Waist Size', 'NIH’s 1998 guidelines mark higher risk above 40 in (102 cm) for men and 35 in (88 cm) for '
               f'women, used with BMI ({a("nhlbi98", "NHLBI, 1998")}). Our <a href="/blog/bmi-tracking-guide/">tracking '
               'guide</a> shows how to measure it.')
        + card(2, 'Health Markers', 'If you are not at a healthy weight, even modest weight loss can help improve blood '
               f'pressure, cholesterol and blood sugar levels, CDC says ({a("cdc_lw", "CDC")}).')
        + card(3, 'Sleep and Activity', 'CDC’s tracking step logs your hours of sleep and each activity’s time of day and '
               f'duration ({a("cdc_lw", "CDC")}), and better sleep quality is among the effects of regular activity CDC '
               f'lists ({a("cdc_pa", "CDC")}).')
        + '</div> '
        # 9 Plateaus
        '<!-- Section 9: Plateaus --> <h2 id="weight-plateaus">When Weight Loss Plateaus</h2> '
        '<p>As weight falls, so does the energy the body burns, so the same intake brings less loss over time. In Hall and '
        'colleagues’ model, half of the eventual change from a new intake comes in about a year and 95% in about three years '
        f'({a("hall", "Hall 2011")}).</p> '
        '<h3>Why Plateaus Happen</h3> <ul> '
        '<li><strong>Lower energy needs:</strong> a smaller body burns less, so the deficit you started with shrinks '
        f'({a("hall", "Hall 2011")})</li> '
        '<li><strong>Weekly swings:</strong> in 80 adults weighed daily, weight ran highest on Sunday and Monday and fell '
        'through the week; the researchers advise reading weekend-to-weekday swings as normal, not as weight gain '
        f'({a("orsama", "Orsama et al., 2014")})</li> </ul> '
        '<h3>What to Do About a Plateau</h3> <div class="numbered-steps"> '
        + step('Recalculate From Your Current Weight', f'NIDDK’s {a("bwp", "Body Weight Planner")} works out a new calorie '
               'and activity plan from where you are now.', 'h4')
        + step('Track Everything for a Few Days', 'A food and beverage diary shows what you eat and drink and where small '
               f'changes could go, CDC says ({a("cdc_lw", "CDC")}).', 'h4')
        + step('Revisit Your Goals', 'Decide which parts of your plan work and which need changing, then revise your goals to '
               f'match ({a("cdc_lw", "CDC")}).', 'h4')
        + '</div> '
        # 10 Medical help
        '<!-- Section 10: Medical Help --> <h2 id="medical-help">When to Seek Medical Help</h2> <ul> '
        '<li><strong>Concerned about your weight or your medicines:</strong> talk with your health care provider, CDC says '
        f'({a("cdc_lw", "CDC")})</li> '
        '<li><strong>Concerned about your eating or your mental health:</strong> talk to a primary care provider, who can refer '
        f'you to a qualified mental health professional, NIMH says ({a("nimh", "NIMH")})</li> '
        '<li><strong>A BMI of 30 or more:</strong> NIH’s 1998 guidelines say these adults should try to lose weight, and so '
        'should adults at 25 to 29.9 (or with a high waist) who have two or more risk factors '
        f'({a("nhlbi98", "NHLBI, 1998")})</li> </ul> '
        '<p>A provider can also refer you to a registered dietitian or to clinical or community programs, CDC says '
        f'({a("cdc_lw", "CDC")}). This site does not cover clinical treatment (medicines, procedures or medically supervised '
        'diets). For the health risks at different BMI levels, see our <a href="/blog/bmi-and-health-risks/">BMI and health '
        'risks</a> guide.</p> '
        '<!-- Medical Disclaimer --> <div class="medical-disclaimer"> <div class="medical-disclaimer-title">Medical '
        'Disclaimer</div> <p>This guide is for information only and is not medical advice. <a href="#medical-help">When to '
        'Seek Medical Help</a> gives CDC’s and NIMH’s advice on when to get help.</p> </div> ')


FAQ = {
    'What is a calorie deficit and how does it help lower BMI?': (
        'Using calories through physical activity while eating fewer creates a calorie deficit, which results in weight loss, '
        f'CDC says ({a("cdc_pa", "CDC")}). The traditional rule of 3,500 kcal per pound of fat overstates long-term loss: as '
        'weight falls, so does the energy the body burns, so the same intake brings less loss over the months '
        f'({a("hall", "Hall 2011")}). NIDDK’s Body Weight Planner uses the same model.'),
    'Is exercise or diet more important for lowering BMI?': (
        'Most weight loss comes from eating fewer calories, CDC says, and regular physical activity is the only way to keep '
        'it off. Without changing what you eat, losing weight and keeping it off takes a high amount of activity; getting to '
        f'and staying at a healthy weight takes both ({a("cdc_pa", "CDC")}).'),
    "Why has my weight loss stalled even though I'm still dieting?": (
        'Partly because a smaller body burns less: as weight falls, so does the energy the body uses, so the same intake '
        f'brings slower loss, with half of the eventual change in about a year ({a("hall", "Hall 2011")}). Weight also swings '
        f'through the week, highest on Sunday and Monday ({a("orsama", "Orsama et al., 2014")}). NIDDK’s Body Weight Planner '
        'recalculates a plan from your current weight, and CDC suggests revisiting your goals and changing the parts of your '
        f'plan that aren’t working ({a("cdc_lw", "CDC")}).'),
    'Can strength training help lower BMI?': (
        'It uses calories, so it adds to a deficit: in CDC’s table, 30 minutes of general light weight lifting uses about 110 '
        f'calories for a 154-pound person, against 140 for walking at 3.5 mph ({a("cdc_pa", "CDC")}). The Physical Activity '
        'Guidelines ask adults for muscle-strengthening activity, like lifting weights or doing push-ups, on at least 2 days a '
        f'week, on top of aerobic activity ({a("pag", "Physical Activity Guidelines")}). BMI can’t tell the muscle you keep '
        f'from fat: CDC notes that it does not distinguish between fat, muscle and bone mass ({a("cdc_about", "CDC")}).'),
    'What foods should I eat to lower my BMI?': (
        'CDC, citing the Dietary Guidelines for Americans, describes a healthy eating plan as one that emphasizes vegetables, '
        'fruits, protein, dairy without added sugars, healthy fats and whole grains; includes protein foods such as seafood, '
        'meats, poultry, eggs, beans and peas, soy products, nuts and seeds; is low in added sugars, sodium, saturated and '
        f'trans fats and cholesterol; and stays within your daily calorie needs ({a("cdc_eat", "CDC")}). Sugary drinks are '
        'the leading source of added sugars in the American diet, and CDC suggests water instead '
        f'({a("cdc_drink", "CDC")}).'),
    'How often should I weigh myself when trying to lower BMI?': (
        'Daily or weekly: weight-loss trials found no significant difference between the two '
        f'({a("madigan", "Madigan et al., 2015")}). Weight tends to be highest on Sunday and Monday and to fall through the '
        f'week ({a("orsama", "Orsama et al., 2014")}), so compare the same weekday each week. Our '
        '<a href="/blog/bmi-tracking-guide/">BMI tracking guide</a> covers the rest, waist size included.'),
}

DESC_OLD = ('Learn proven, science-backed methods to lower your BMI safely. Comprehensive guide covering calorie deficit, '
            'exercise, nutrition, and lifestyle changes for sustainable weight loss.')
DESC_NEW = ('How much weight one BMI point is at your height, CDC’s 1 to 2 pounds a week and five steps, and what the federal '
            'eating and activity guidance says.')
META = [
    (f'<meta name="description" content="{DESC_OLD}">', f'<meta name="description" content="{DESC_NEW}">'),
    ('<meta property="og:description" content="Learn proven, science-backed methods to lower your BMI safely. Comprehensive '
     'guide covering calorie deficit, exercise, nutrition, and lifestyle changes.">',
     f'<meta property="og:description" content="{DESC_NEW}">'),
    ('<meta name="twitter:description" content="Learn proven, science-backed methods to lower your BMI safely with our '
     'comprehensive guide.">', f'<meta name="twitter:description" content="{DESC_NEW}">'),
    (f'"description": "{DESC_OLD}"', f'"description": "{DESC_NEW}"'),
    ('<p>How to monitor your BMI progress effectively and understand what the numbers mean.</p>',
     '<p>How to track your BMI over time and what the numbers mean.</p>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
    ('<meta property="article:modified_time" content="2026-11-13T00:00:00Z">',
     f'<meta property="article:modified_time" content="{TODAY}T00:00:00Z">'),
]
QUOTE = ('“a quick, safe, and reliable screening measure”', '“a quick, low-cost, and reliable screening measure”')


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()


def jsonld_block(d):
    """The page's own style: indented JSON folded onto one line ("{ "@context": ..., [ { ... } ] }")."""
    return re.sub(r'\n\s*', ' ', json.dumps(d, ensure_ascii=False, indent=1))


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:80]}'
    return src.replace(old, new)


def page(src):
    i = src.index('<p class="intro-text">')
    j = src.index('<!-- FAQ Section -->', i)
    src = src[:i] + body(src) + src[j:]
    for old, new in META:
        src = one(src, old, new, PG)
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question"> ' + re.escape(q) + r' <svg.*?</button> <div class="faq-answer"> <p>)(.*?)(</p> </div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question"> (.*?) <svg.*?</button> <div class="faq-answer"> <p>(.*?)</p> </div>', src)
    assert len(qa) == 7, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + ' ' + jsonld_block(d) + ' ' + src[fb.end(2):]
    return src


def hbr(src):
    src = one(src, *QUOTE, HBR)
    src = one(src, '"dateModified": "2026-10-15"', f'"dateModified": "{TODAY}"', HBR)
    return one(src, '<meta property="article:modified_time" content="2026-10-15T00:00:00Z">',
               f'<meta property="article:modified_time" content="{TODAY}T00:00:00Z">', HBR)


def sitemap(src):
    for loc, old in (('blog/how-to-lower-bmi/', '2026-11-13'), ('', '2026-11-13'), ('blog/healthy-bmi-range/', '2026-10-21')):
        src = one(src, f'<url><loc>https://calculatemybmi.net/{loc}</loc><lastmod>{old}</lastmod>',
                  f'<url><loc>https://calculatemybmi.net/{loc}</loc><lastmod>{TODAY}</lastmod>', SM)
    return src


CHANGE = {PG: page, SM: sitemap, HOME: lambda s: one(s, *QUOTE, HOME), HBR: hbr,
          GEN_HOME: lambda s: one(s, *QUOTE, GEN_HOME), GEN_HBR: lambda s: one(s, *QUOTE, GEN_HBR)}


def main():
    for rel, change in CHANGE.items():
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        src = change(src)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
