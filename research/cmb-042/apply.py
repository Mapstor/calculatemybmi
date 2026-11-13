#!/usr/bin/env python3
"""CMB-042 SOURCES-4: S (sourcing) on the four G2 guides with the most numbers that didn't trace to a registry row
(the Stage 1 audit on main: 191 with no row and 27 not in their row): /blog/bmi-and-metabolism/,
/blog/how-to-lower-bmi/, /blog/bmi-history/ and /blog/waist-to-height-ratio/. Every number now traces to a row in
research/data-sources.csv (research/cmb-042/registry.py) or to our arithmetic on one, or the claim goes (D-10, D-06,
D-01, D-11). The base pages are checked by SHA-256, every marker must occur once (FAQ texts the count given). The
history and waist pages' social images are then redrawn from their corrected figures (research/cmb-042/og_images.py).
usage: python3 research/cmb-042/apply.py [--check]   (--check applies in memory and writes nothing)
Run order from main: registry.py, manual.py, apply.py, og_images.py.

1. /blog/bmi-and-metabolism/: Hirode & Wong 2020 (34.7%), Alberti 2009 (5-fold, twice over 5 to 10 years), Pontzer
   2021, Wang 2010 (13 vs 4.5 kcal/kg a day), Mifflin 1990 and Roza & Shizgal 1984 (the two BMR equations, with a
   source line), Caleyachetty 2017 (the MHO definition and results, and normal weight with metabolic abnormalities),
   the American Thyroid Association (5 to 10 pounds, salt and water). Cut (no source): both .chart-compare blocks,
   the Katch-McArdle row and its "+/- 5%" cell, "Estimated to represent 10-30%", "Prevalence rises with BMI", the
   thyroid symptom list and the FAQ's testing and treatment lines (D-01), the sources list's ". Healthy Living".
2. /blog/how-to-lower-bmi/: Hall 2011 (the 3,500 kcal rule, half times of about a year, about 1 lb of eventual loss
   per 10 kcal a day), CDC (about 1 to 2 pounds a week), NIDDK's Body Weight Planner in place of the Mifflin-St Jeor
   and activity-factor steps (D-06), the Physical Activity Guidelines in place of the calories-burned chart (D-06),
   Hollis 2008 (food records), Cappuccio 2008 (odds ratio 1.55), MedlinePlus (alcohol, about 7 calories per gram),
   NHLBI 1998 (who should try to lose weight). Cut: "3-6 months to move down one BMI category", the week and month
   timeline, "every 10-15 pounds lost", "after 2-4 weeks" (page and JSON-LD), "even 10 minutes daily", "each 5-pound
   loss"; category names as calculator.js prints them; article:modified_time follows dateModified.
3. /blog/bmi-history/: Eknoyan 2008 (Quetelet, the 1832 index, the 1835 book, insurers and Louis Dublin, Keys
   1904-2004), Wells 2014 (Quetelet's own words on height and weight, body composition after BMI), Keys et al. 1972
   (the abstract's indices, criteria and verbatim conclusion; the old quote was not the paper's), the NIH 1985
   consensus conference, NHLBI 1998 (the cut-offs, NHANES III 54.9%, 32.6%, 22.3%), Nuttall 2015 (MetLife's 1959
   tables), WHO 1995, 2000 and 2004 as their rows hold them, Winter 2014 (§4 wording), Trefethen (his own caveat),
   CDC's 2011-2018 body scans for women and men at a healthy BMI. Cut: the "average man ... type of perfection" quote
   (not verified), "first director ... at just 27", "between 1830 and 1850", the list of original applications, the
   insurance pros and cons lists, "millions ... reclassified", "Several Asian countries ...", "smart BMI", "different
   healthy ranges for women and men" (D-11), "BMI cutoffs may need age-specific adjustments" (D-11). The timeline,
   its figure and the social image show 1959 MetLife in place of "1900s insurance"; the references get the WHO
   fact sheet's link and lose ": How useful is BMI?".
4. /blog/waist-to-height-ratio/: NICE NG246 (the ratio classes for adults with a BMI under 35, both sexes and all
   ethnicities; children and young people from 5; when to seek advice), Ashwell 2012 (31 studies, more than 300,000
   adults, its own words), Browning 2010 (78 studies, AUROC 0.704 / 0.693 / 0.671, boundary 0.50 in studies from
   14 countries), WHO 2008 (waist-hip 0.90 and 0.85), CDC (1 to 2 pounds a week). Cut: "outperforms BMI in
   predicting ... all-cause mortality", "first proposed ... in the 1990s", the "<0.4 Underweight Risk" bar, the
   International Journal of Obesity sentence, the children's risk-factor list, the ethnicity list, "0.46-0.48 for
   Asian populations", MONW "similar health risks", "within 4-8 weeks", "requiring medical attention", "Free
   calculator" in the meta description (the page has none).
5. Second pass, after the anti-slop read of the new text (16 fixes: vague authority 5, re-explaining 3, about-the-page 2,
   inflation 2, not-X-but-Y, sales word, throat-clearing, vague hedge): the history intro without "fascinating", its
   figure caption and "not medicine"; the lower-BMI planner described once; the waist page's "Why better" intro,
   "elegantly simple", the figure caption's pointer, the card's repeated age clause, the children's section (said "no
   percentile charts" twice and "exceeds half their height ... may warrant attention"), and its three improve lists
   ("has been shown", "strongly linked", "effective for", no source) replaced by CDC's pace and the Physical Activity
   Guidelines (D-06).
   Read against the sources in Chrome: the thyroid FAQ keeps only what ATA's page says now (its "massive weight gain"
   line is gone from the page), and Caleyachetty's 3.5 million adults are "a study", not "the largest"; the metabolism
   page's link to the age calculator no longer promises age-specific recommendations (D-11).
   The waist figure marks NICE's boundary as "≥ 0.5, increased risk" (was "> 0.5, elevated risk") and its description
   no longer puts the waist at the navel or the callouts on the right. /blog/bmi-and-metabolism/ shares the site card:
   its old image (removed) drew a TDEE donut with overlapping arcs and a "60-75% per NIDDK" share no row holds.
6. Dates (§4): schema dateModified, article:modified_time where the page has it, sitemap lastmod of the four pages;
   research/page-scores-known.csv loses the three rows this batch closes.
"""
import datetime
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv

BASE = {
    'blog/bmi-and-metabolism/index.html': '446806c785af82ceb3acac7239975920beca5a2b1a5c8dfcb6537fcd38ce2c8b',
    'blog/how-to-lower-bmi/index.html': '9447ec518bbbcd24f34b7d5ec65a2292a480b4da5faf4123dd53c4c30c2086a9',
    'blog/bmi-history/index.html': '31ed8b09cb2514fcbcec243851db4844ad3bd3e096d4bf7aa28a5527a7a6a155',
    'blog/waist-to-height-ratio/index.html': 'b9af10d456a9921dc825b089aaf91ff7d5e9bffaea9031fd188fbbbf4dcf5663',
    'sitemap.xml': '86dad1e2fe1a17a83af9598f524264f0b82827c4d234b64a5ee26cb01f069bee',
}


def a(url):
    return f'<a href="{url}" target="_blank" rel="noopener">'


HIRODE = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC7312413/')
PONTZER = a('https://pubmed.ncbi.nlm.nih.gov/34385400/')
ALBERTI = a('https://pubmed.ncbi.nlm.nih.gov/19805654/')
WANG = a('https://pubmed.ncbi.nlm.nih.gov/20962155/')
MIFFLIN = a('https://pubmed.ncbi.nlm.nih.gov/2305711/')
ROZA = a('https://pubmed.ncbi.nlm.nih.gov/6741850/')
CALEY = a('https://doi.org/10.1016/j.jacc.2017.07.763')
ATA = a('https://www.thyroid.org/thyroid-and-weight/')
HALL = a('https://pubmed.ncbi.nlm.nih.gov/21872751/')
CDCLW = a('https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html')
NIDDK = a('https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner')
ODPHP = a('https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/'
          'top-10-things-know')
HOLLIS = a('https://doi.org/10.1016/j.amepre.2008.04.013')
CAPPUCCIO = a('https://pubmed.ncbi.nlm.nih.gov/18517032/')
MEDALC = a('https://medlineplus.gov/ency/imagepages/17023.htm')
NHLBI98 = a('https://www.ncbi.nlm.nih.gov/books/NBK2003/')
NHLBI98E = a('https://www.ncbi.nlm.nih.gov/books/NBK2005/')
EKNOYAN = a('https://doi.org/10.1093/ndt/gfm517')
WELLS = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC4052141/')
KEYS = a('https://doi.org/10.1016/0021-9681(72)90027-6')
NIH85 = a('https://pubmed.ncbi.nlm.nih.gov/3840463/')
NUTTALL = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC4890841/')
WHO854 = a('https://www.who.int/publications/i/item/9241208546')
WHO894 = a('https://iris.who.int/handle/10665/42330')
WHO2004 = a('https://pubmed.ncbi.nlm.nih.gov/14726171/')
WHOFS = a('https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight')
WINTER = a('https://pubmed.ncbi.nlm.nih.gov/24452240/')
TREF = a('https://people.maths.ox.ac.uk/trefethen/bmi.html')
NICE = a('https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity')
ASHWELL = a('https://pubmed.ncbi.nlm.nih.gov/22106927/')
BROWNING = a('https://pubmed.ncbi.nlm.nih.gov/20819243/')
WHO2008 = a('https://www.who.int/publications/i/item/9789241501491')
SRC = '<p style="font-size:0.8125rem;color:var(--gray-500);">'


def lit(old, new, n=1):
    return ('lit', old, new, n)


def span(start, end, new):
    """From the one occurrence of start through the first end after it."""
    return ('span', start, end, new)


def faq(question, new):
    """A FAQ answer, visible and in the FAQPage JSON-LD (when the question is there), replaced by new (plain text)."""
    return ('faq', question, new)


def do(h, e, page):
    kind = e[0]
    if kind == 'lit':
        _, old, new, n = e
        got = h.count(old)
        if got != n:
            sys.exit(f'{page}: expected {n} of {old[:90]!r}, found {got}')
        return h.replace(old, new)
    if kind == 'span':
        _, start, end, new = e
        if h.count(start) != 1:
            sys.exit(f'{page}: expected 1 of {start[:90]!r}, found {h.count(start)}')
        i = h.index(start)
        j = h.find(end, i + len(start))
        if j < 0:
            sys.exit(f'{page}: no {end[:60]!r} after {start[:60]!r}')
        return h[:i] + new + h[j + len(end):]
    if kind == 'faq':
        _, q, new = e
        rx = re.compile(r'(<button class="faq-question">\s*' + re.escape(q) + r'\s*(?:<svg.*?</svg>)?\s*</button>\s*'
                        r'<div class="faq-answer">\s*<p>)(.*?)(</p>)', re.S)
        ms = list(rx.finditer(h))
        if len(ms) != 1:
            sys.exit(f'{page}: expected 1 visible FAQ {q!r}, found {len(ms)}')
        m = ms[0]
        old_vis = html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
        h = h[:m.start(2)] + html.escape(new, quote=False) + h[m.end(2):]
        for blk in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                data = json.loads(blk.group(1))
            except ValueError:
                continue
            if data.get('@type') != 'FAQPage':
                continue
            for item in data['mainEntity']:
                if item['name'].strip() == q.strip():
                    old = item['acceptedAnswer']['text']
                    if re.sub(r'\s+', '', old) != re.sub(r'\s+', '', old_vis):
                        sys.exit(f'{page}: FAQ {q!r} differs between the page and the JSON-LD before the edit')
                    raw_old = json.dumps(old, ensure_ascii=False)[1:-1]
                    if h.count(raw_old) != 1:
                        sys.exit(f'{page}: JSON-LD answer for {q!r} not found once as written')
                    h = h.replace(raw_old, json.dumps(new, ensure_ascii=False)[1:-1])
        return h
    sys.exit(f'unknown edit {kind}')


MET = 'blog/bmi-and-metabolism/index.html'
LOW = 'blog/how-to-lower-bmi/index.html'
HIS = 'blog/bmi-history/index.html'
WHT = 'blog/waist-to-height-ratio/index.html'

EDITS = {MET: [
    lit('<li><strong>Metabolic syndrome</strong> affects about 1 in 3 American adults (' + HIRODE + 'Hirode &amp; Wong, JAMA '
        '2020</a>) and is strongly linked to elevated BMI</li>',
        '<li><strong>Metabolic syndrome:</strong> 34.7% of US adults had it in 2011&ndash;2016 (' + HIRODE + 'Hirode &amp; '
        'Wong, JAMA 2020</a>)</li>'),
    lit('<li><strong>"Metabolically healthy obesity"</strong> exists but may be temporary; long-term health risks often '
        'emerge over time</li>',
        '<li><strong>"Metabolically healthy" obesity</strong> still carried more coronary heart disease and heart failure '
        'than a healthy weight with no metabolic abnormalities, in a study of 3.5 million adults (' + CALEY +
        'Caleyachetty et al., 2017</a>)</li>'),
    lit('<p>Several validated formulas exist to estimate BMR. The most commonly used are:</p>',
        '<p>Published equations estimate resting energy expenditure from weight, height, age and sex. Mifflin and '
        'colleagues measured it in 498 adults and found that the original Harris-Benedict equations of 1919 '
        'overestimated it by 5% (' + MIFFLIN + 'Mifflin et al., 1990</a>). Two equations in use:</p>'),
    lit('<tr><td><strong>Katch-McArdle</strong></td><td colspan="2">370 + (21.6 x lean body mass in kg)</td><td>+/- 5%</td>'
        '</tr></table></div> <p>The Katch-McArdle formula accounts for <a href="/lean-body-mass/">lean body mass</a>, which '
        'is the primary driver of metabolic rate. However, it requires knowing your body fat percentage, which you can '
        'estimate using our <a href="/lean-body-mass/">lean body mass calculator guide</a>.</p>',
        '</table></div> ' + SRC + 'Source: ' + ROZA + 'Roza and Shizgal, 1984</a> (Harris-Benedict revised); ' + MIFFLIN +
        'Mifflin et al., 1990</a> (the simplified form the paper gives). Weight in kg, height in cm, age in years; the '
        'result is kcal a day.</p> <p>Both equations use total weight, so neither can tell muscle from fat. In '
        'Mifflin&rsquo;s data, fat-free mass was the best single predictor of resting energy expenditure (' + MIFFLIN +
        'Mifflin et al., 1990</a>); the <a href="/lean-body-mass/">lean body mass calculator</a> estimates it.</p>'),
    span('<h3>BMI vs. metabolic Health Indicators</h3> <div class="chart-compare">',
         'Comparison: Normal BMI (left/cyan) vs. obese BMI (right/dark)</p>',
         '<h3>BMI vs. metabolic Health Indicators</h3>'),
    lit('<div class="stat-box-value" style="color: var(--obese-strong);">1 in 3</div> <div class="stat-box-label">US Adults '
        'Affected</div>',
        '<div class="stat-box-value" style="color: var(--obese-strong);">34.7%</div> <div class="stat-box-label">US adults '
        'with it, 2011&ndash;2016</div>'),
    lit('<div class="stat-box-label">Diabetes Risk Increase</div>', '<div class="stat-box-label">Type 2 diabetes risk</div>'),
    lit('<div class="stat-box-label">Cardiovascular Risk (5&ndash;10 yrs)</div>',
        '<div class="stat-box-label">Cardiovascular disease risk over 5&ndash;10 years</div>'),
    lit(' Prevalence rises with BMI.', ''),
    span('<div class="alert alert-info"> <div class="alert-title">Definition</div>',
         'is still generally the safer target for long-term health.</p>',
         '<div class="alert alert-info"> <div class="alert-title">Definition</div> <strong>Metabolically healthy obesity '
         '(MHO)</strong>: obesity without metabolic disease. Definitions vary; the largest study, of 3.5 million UK adults, '
         'counted a BMI of 30 or more with none of three abnormalities: diabetes, hypertension and hyperlipidaemia (' +
         CALEY + 'Caleyachetty et al., 2017</a>). </div> <h3>The MHO Controversy</h3>  <p>Over a mean 5.4 years, people '
         'in that study with obesity and none of the three had a higher risk of coronary heart disease (hazard ratio '
         '1.49), cerebrovascular disease (1.07) and heart failure (1.96) than people of healthy weight with none (' +
         CALEY + 'Caleyachetty et al., 2017</a>). So &ldquo;metabolically healthy&rdquo; did not mean free of heart risk. '
         'The <a href="/blog/healthy-bmi-range/">healthy BMI range</a> guide explains the categories.</p>'),
    lit('describes individuals with normal BMI who exhibit metabolic dysfunction.</p>',
        'describes individuals with normal BMI who exhibit metabolic dysfunction.</p> <p>In the same 3.5 million adults, '
        'the risk of coronary heart disease, cerebrovascular disease and heart failure rose with the number of metabolic '
        'abnormalities in people of healthy weight as well as in those with overweight or obesity (' + CALEY +
        'Caleyachetty et al., 2017</a>).</p>'),
    span('<div class="stat-highlight"> <div class="stat-highlight-value">3x</div>',
         'Person A (left): Athletic build | Person B (right): Higher body fat. Both weigh 170 lbs</p>',
         '<div class="stat-highlight"> <div class="stat-highlight-value">2.9x</div> <div class="stat-highlight-label">Muscle '
         'vs fat at rest, per kg</div> <div class="stat-highlight-sub">13 vs 4.5 kcal per kg a day, about 6 vs 2 per pound '
         '(' + WANG + 'Wang et al., 2010</a>)</div> </div>'),
    span('<div class="alert alert-warning"> <div class="alert-title">Important Note</div>',
         '<li>Mood changes or brain fog</li> </ul>',
         '<div class="alert alert-warning"> <div class="alert-title">Important Note</div> For most patients, about 5 to 10 '
         'pounds of weight gain may be related to an underactive thyroid, depending on how severe it is, and most of that '
         'gain is salt and water (' + ATA + 'American Thyroid Association</a>). </div>'),
    lit('Yes, hypothyroidism (underactive thyroid) can slow metabolism and contribute to weight gain. However, the typical '
        'weight gain from hypothyroidism is modest: usually 5-10 pounds, much of which is fluid retention. Significant '
        'weight gain or inability to lose weight is rarely due to thyroid issues alone. If you suspect thyroid problems, '
        'symptoms like fatigue, cold sensitivity, dry skin, and hair loss alongside weight changes warrant testing. Proper '
        'treatment with thyroid hormone replacement typically resolves metabolic effects.',
        'Yes, an underactive thyroid (hypothyroidism) can slow metabolism and add weight, but usually not much. The '
        'American Thyroid Association says about 5 to 10 pounds of weight gain may be related to the thyroid for most '
        'patients, depending on how severe the hypothyroidism is, and that most of the weight gained is salt and '
        'water.', 2),
    lit('<li>. Healthy Living</li> <li>Pontzer H, et al. Daily energy expenditure through the human life course. Science. '
        '2021.</li> <li>Caleyachetty R, et al. Metabolically Healthy Obese and Incident Cardiovascular Disease Events. '
        'JACC. 2017.</li> </ul>',
        '<li>Pontzer H, et al. ' + PONTZER + 'Daily energy expenditure through the human life course</a>. Science. '
        '2021.</li> <li>Caleyachetty R, et al. ' + CALEY + 'Metabolically Healthy Obese and Incident Cardiovascular '
        'Disease Events Among 3.5 Million Men and Women</a>. JACC. 2017.</li> <li>Hirode G, Wong RJ. ' + HIRODE +
        'Trends in the Prevalence of Metabolic Syndrome in the United States, 2011-2016</a>. JAMA. 2020.</li> '
        '<li>Alberti KGMM, et al. ' + ALBERTI + 'Harmonizing the Metabolic Syndrome</a>. Circulation. 2009.</li> '
        '<li>Mifflin MD, et al. ' + MIFFLIN + 'A new predictive equation for resting energy expenditure in healthy '
        'individuals</a>. Am J Clin Nutr. 1990.</li> <li>Roza AM, Shizgal HM. ' + ROZA + 'The Harris Benedict equation '
        'reevaluated</a>. Am J Clin Nutr. 1984.</li> <li>Wang Z, et al. ' + WANG + 'Specific metabolic rates of major '
        'organs and tissues across adulthood</a>. Am J Clin Nutr. 2010.</li> <li>American Thyroid Association. ' + ATA +
        'Thyroid and Weight</a>.</li> </ul>'),
]}

EDITS[LOW] = [
    lit('<li><strong>Lose weight gradually:</strong> slow, steady loss is easier to sustain</li>',
        '<li><strong>Lose weight gradually:</strong> CDC notes that people who lose about 1 to 2 pounds a week are more '
        'likely to keep the weight off (' + CDCLW + 'CDC</a>)</li>'),
    lit('<li><strong>The 3,500 kcal rule is a rough approximation:</strong> traditionally &quot;1 lb of fat = ~3,500 '
        'kcal&quot;, but dynamic models (' + HALL + 'Hall 2011</a>; NIH Body Weight Planner) show it overestimates '
        'long-term loss.</li>',
        '<li><strong>The 3,500 kcal rule overstates long-term loss:</strong> Hall and colleagues&rsquo; model gives about '
        '1 pound of eventual weight change for every 10 kcal a day of change in intake, half of it in about a year (' +
        HALL + 'Hall 2011</a>)</li>'),
    lit(' <li><strong>Timeline reality:</strong> Expect 3-6 months to move down one BMI category</li>', ''),
    lit('<tr><td>18.5 - 24.9</td><td>Normal weight</td></tr>', '<tr><td>18.5 - 24.9</td><td>Healthy weight</td></tr>'),
    lit('<td>Obese Class I</td>', '<td>Class 1 obesity</td>'),
    lit('<td>Obese Class II</td>', '<td>Class 2 obesity</td>'),
    lit('<td>Obese Class III</td>', '<td>Class 3 obesity</td>'),
    span('<p>The traditional teaching is that ~3,500 kcal equals one pound of body fat',
         'than a fixed kcal-per-pound number.</p>',
         '<p>The traditional teaching is that about 3,500 kcal equals a pound of body fat, so cutting 500 kcal a day takes '
         'off about a pound a week. Hall and colleagues showed that this rule ignores how the body adapts: as weight '
         'falls, so does the energy it burns, and the response to a change in intake is slow, with half times of about a '
         'year (' + HALL + 'Hall et al., <em>Lancet</em> 2011</a>). Their rule of thumb for an average overweight adult '
         'is about 1 pound of eventual weight change for every 10 kcal a day of change in intake, with half of it reached '
         'in about a year and 95% in about three years. NIDDK&rsquo;s ' + NIDDK + 'Body Weight Planner</a> is built on the '
         'same model.</p>'),
    span('<div class="numbered-step"> <div class="numbered-step-content"> <h4>Calculate Your BMR</h4>',
         'is best set with a clinician or registered dietitian.</p> </div> </div>',
         '<div class="numbered-step"> <div class="numbered-step-content"> <h4>Start From an Official Estimate</h4> <p>NIDDK&rsquo;s ' +
         NIDDK + 'Body Weight Planner</a> makes a personal calorie and physical activity plan to reach a goal weight by '
         'a chosen date and to keep it afterwards, from the model described above.</p> </div> </div> <div '
         'class="numbered-step"> <div class="numbered-step-content"> <h4>Set a Target With a Professional</h4> <p>A safe '
         'calorie target for weight loss depends on your health and is best set with a clinician or registered '
         'dietitian.</p> </div> </div>'),
    lit('<li><strong>Alcohol:</strong> High in calories (7 per gram), reduces inhibitions around food, and disrupts '
        'metabolism</li>',
        '<li><strong>Alcohol:</strong> about 7 calories per gram (' + MEDALC + 'MedlinePlus</a>)</li>'),
    span('<h3>Calories Burned by Activity</h3> <div class="chart-bar-h">',
         'Actual calorie burn varies by weight and intensity.</p>',
         '<h3>How Much Activity the Guidelines Call For</h3> <p>The federal Physical Activity Guidelines say adults need '
         'at least 150 to 300 minutes of moderate-intensity aerobic activity a week, and muscle-strengthening activity, '
         'like lifting weights or doing push-ups, at least 2 days each week (' + ODPHP + 'Physical Activity Guidelines '
         'for Americans</a>).</p>'),
    lit('<p>People who track their food intake lose twice as much weight as those who don\'t. Use an app or notebook to '
        'record everything you eat and drink.</p>',
        '<p>In a 20-week group program for 1,685 adults, who lost 5.8 kg on average, the food records people kept and '
        'their physical activity accounted for most of the differences in how much they lost (' + HOLLIS + 'Hollis et '
        'al., 2008</a>). Use an app or a notebook to record everything you eat and drink.</p>'),
    lit('<div class="stat-box-value">55%</div> <div class="stat-box-label">Higher odds of obesity in adults sleeping 5 '
        'hours or less</div>',
        '<div class="stat-box-value">1.55</div> <div class="stat-box-label">Odds ratio for obesity in adult short '
        'sleepers</div>'),
    lit('<p style="font-size:0.8125rem;color:var(--gray-500);">Pooled cross-sectional studies covering 604,509 adults: an '
        'association, not proof of cause (',
        '<p style="font-size:0.8125rem;color:var(--gray-500);">Pooled from cross-sectional studies covering 604,509 '
        'adults: an association, not proof of cause ('),
    lit('<li>Mindfulness meditation (even 10 minutes daily helps)</li>', '<li>Mindfulness meditation</li>'),
    span('<h3>Weight Loss Timeline Expectations</h3> <div class="progress-steps">',
         '<div class="progress-step-label">Month 6-12: Maintenance Phase</div> </div> </div> ',
         '<h3>Weight to Lose for One Category Down</h3> <p>CDC notes that people who lose about 1 to 2 pounds a week are '
         'more likely to keep the weight off (' + CDCLW + 'CDC</a>). The weight it takes to move down one category:</p> '),
    lit('Celebrate each 5-pound loss or each week of consistent exercise.',
        'Celebrate each milestone you reach, on the scale or in the habits you keep.'),
    lit('<li>Your BMI is 30 or higher (obesity range)</li> <li>Your BMI is 25+ and you have weight-related health '
        'conditions</li>',
        '<li>Your BMI is 30 or more, or 25 to 29.9 (or your waist is high) with two or more risk factors: the adults '
        'NIH&rsquo;s 1998 guidelines say should try to lose weight (' + NHLBI98 + 'NHLBI, 1998</a>)</li>'),
    faq('How quickly can I lower my BMI safely?',
        'Gradually. CDC notes that people who lose about 1 to 2 pounds a week are more likely to keep the weight off '
        'than people who lose weight quicker. NIDDK\'s Body Weight Planner works out a calorie and activity plan to reach '
        'a goal weight by a chosen date.'),
    faq('Why has my weight loss stalled even though I\'m still dieting?',
        'Weight loss plateaus are normal and occur for several reasons. As you lose weight, your body requires fewer '
        'calories to function, so your original calorie deficit shrinks. Your metabolism also adapts somewhat to lower '
        'calorie intake. You might also be retaining water, or portion sizes may have slowly crept up. Solutions include '
        'recalculating your calorie needs at your new weight (NIDDK\'s Body Weight Planner does this), tracking food '
        'carefully for a week, varying your exercise routine and eating enough protein.'),
]

HIS_DESC_OLD = ('A horizontal timeline showing that 140 years passed between Quetelet\'s 1832 formula and Ancel Keys naming '
                'it BMI in 1972, then only 13 years to NIH adoption in 1985, another 10 years to WHO adoption in 1995, and 31 '
                'years to the present.')
HIS_DESC_NEW = ('A horizontal timeline: Quetelet\'s index in 1832; Metropolitan Life\'s desirable-weight tables in 1959; '
                'Ancel Keys naming it BMI in 1972, 140 years after Quetelet; an NIH consensus conference backing wider use '
                'of BMI in 1985; WHO\'s anthropometry report in 1995; and the present, 54 years after Keys.')
HIS_SVG_OLD = ('<circle cx="177" cy="70" r="5" fill="currentColor" fill-opacity="0.5"/> <text x="177" y="55" '
               'text-anchor="middle" font-size="11" font-weight="600">1900s</text> <text x="177" y="95" '
               'text-anchor="middle" font-size="10">insurance</text> <text x="177" y="107" text-anchor="middle" '
               'font-size="10">adoption</text>')
HIS_SVG_NEW = ('<circle cx="305" cy="70" r="5" fill="currentColor" fill-opacity="0.5"/> <text x="299" y="42" '
               'text-anchor="end" font-size="10" font-weight="600">1959 MetLife</text>')

EDITS[HIS] = [
    lit('content="Discover the fascinating 200-year history of BMI. From Adolphe Quetelet\'s 1832 formula to Ancel Keys '
        'naming it in 1972, WHO adoption, and modern critiques. Comprehensive timeline and evolution."',
        'content="The history of BMI, from Adolphe Quetelet\'s 1832 index to Ancel Keys naming it in 1972, the NIH and '
        'WHO cut-offs, and the critiques since."'),
    lit('content="Discover the fascinating 200-year history of BMI. From Quetelet\'s 1832 formula to WHO adoption and '
        'modern critiques."',
        'content="The history of BMI, from Quetelet\'s 1832 index to Ancel Keys naming it in 1972 and the NIH and WHO '
        'cut-offs."', 2),
    lit('<li><a href="#insurance">Insurance Industry Adoption (1900s)</a></li>',
        '<li><a href="#insurance">Insurance Weight Tables</a></li>'),
    lit('<li><a href="#nih-adoption">NIH Adoption and the 1998 Change</a></li>',
        '<li><a href="#nih-adoption">NIH and the 1998 Cut-Offs</a></li>'),
    lit('<li><strong>1832:</strong> Belgian mathematician Adolphe Quetelet created the formula (weight/height&sup2;) as '
        'the "Quetelet Index"</li> <li><strong>Original purpose:</strong> Designed to study population statistics, not '
        'assess individual health</li> <li><strong>1972:</strong> American physiologist Ancel Keys coined the term "Body '
        'Mass Index" in a landmark study</li> <li><strong>1985:</strong> NIH formally adopted BMI as the standard for '
        'defining obesity in the US</li> <li><strong>1995:</strong> WHO established the global BMI classification system '
        'still used today</li>',
        '<li><strong>1832:</strong> Belgian mathematician Adolphe Quetelet described the index, weight divided by height '
        'squared, later known as the Quetelet index (' + EKNOYAN + 'Eknoyan, 2008</a>)</li> <li><strong>Original '
        'purpose:</strong> Quetelet was describing the &ldquo;average man&rdquo;, not measuring obesity (' + EKNOYAN +
        'Eknoyan, 2008</a>)</li> <li><strong>1972:</strong> Ancel Keys and colleagues named it the body mass index (' +
        KEYS + 'Keys et al., 1972</a>)</li> <li><strong>1985:</strong> an NIH consensus conference on obesity '
        'recommended wider use of BMI (' + NIH85 + 'NIH, 1985</a>)</li> <li><strong>1995:</strong> WHO graded adult '
        'thinness by BMI (' + WHO854 + 'WHO, 1995</a>); its 2000 report set the obesity classes I to III (' + WHO894 +
        'WHO, 2000</a>)</li>'),
    lit('<div class="progress-step-number">1832</div> <div class="progress-step-label">Quetelet creates formula</div>',
        '<div class="progress-step-number">1832</div> <div class="progress-step-label">Quetelet&rsquo;s index</div>'),
    lit('<div class="progress-step-number">1900s</div> <div class="progress-step-label">Insurance adoption</div>',
        '<div class="progress-step-number">1959</div> <div class="progress-step-label">MetLife desirable weights</div>'),
    lit('<div class="progress-step-label">NIH adoption</div>', '<div class="progress-step-label">NIH conference backs BMI</div>'),
    lit('<div class="progress-step-label">WHO standards</div>',
        '<div class="progress-step-label">WHO thinness grades</div> </div> <div class="progress-step completed"> <div '
        'class="progress-step-number">1998</div> <div class="progress-step-label">NIH sets 25 and 30</div>'),
    lit(HIS_DESC_OLD, HIS_DESC_NEW),
    span(' <!-- events at proportional positions', 'x=30+194*2.165=450 -->', ''),
    lit(HIS_SVG_OLD, HIS_SVG_NEW),
    lit('<p>The story of BMI begins not in medicine, but in mathematics and astronomy. Lambert Adolphe Jacques Quetelet '
        '(1796-1874) was a Belgian polymath who made groundbreaking contributions to statistics, astronomy, and social '
        'science. Born in Ghent, he initially trained as a mathematician and became the first director of the Royal '
        'Observatory of Belgium at just 27 years old.</p>',
        '<p>The story of BMI begins in mathematics and astronomy. Adolphe Quetelet (1796&ndash;1874) was a '
        'Belgian mathematician, astronomer and statistician, born in Ghent, who applied probability to human physical '
        'characteristics and social aptitudes; he is considered a founder of the social sciences (' + EKNOYAN +
        'Eknoyan, 2008</a>).</p>'),
    lit('<blockquote> "If the average man were completely determined, we might consider him as the type of perfection; and '
        'everything differing from his proportions or conditions would constitute deformity and disease." <cite>Adolphe '
        'Quetelet, A Treatise on Man and the Development of His Faculties (1835)</cite> </blockquote>',
        '<blockquote> "If man increased equally in all dimensions, his weight at different ages would be as the cube of '
        'his height. Now, this is not what we really observe." <cite>Adolphe Quetelet, <em>A Treatise on Man and the '
        'Development of His Faculties</em> (English edition, 1842), as quoted by ' + WELLS + 'Wells (2014)</a></cite> '
        '</blockquote>'),
    lit('<h3>The Birth of the Quetelet Index (1832-1850)</h3> <p>Between 1830 and 1850, Quetelet analyzed anthropometric '
        'data from thousands of individuals and made a crucial observation: in adult populations, body weight tends to '
        'scale with the square of height, not with the cube as one might expect from simple three-dimensional scaling. '
        'This led him to propose the formula:</p>',
        '<h3>The Birth of the Quetelet Index (1832)</h3> <p>Weight does not grow as the cube of height, as it would if '
        'people grew equally in all dimensions. Quetelet&rsquo;s observation that &ldquo;the weight increases as the '
        'square of the height&rdquo; became the Quetelet index, described in 1832 (' + EKNOYAN + 'Eknoyan, 2008</a>):</p>'),
    lit('<p>This formula, which Quetelet called the "Quetelet Index," would remain largely unknown outside academic circles '
        'for over a century. Quetelet published his findings in his 1835 work <em>Sur l\'homme et le d&eacute;veloppement '
        'de ses facult&eacute;s</em> (A Treatise on Man and the Development of His Faculties), which is considered the '
        'founding text of quantitative social science.</p>',
        '<p>Quetelet set out his work on the &ldquo;average man&rdquo; in his 1835 book <em>Sur l\'homme et le '
        'd&eacute;veloppement de ses facult&eacute;s</em> (' + EKNOYAN + 'Eknoyan, 2008</a>), published in English in '
        '1842 as <em>A Treatise on Man and the Development of His Faculties</em> (' + WELLS + 'Wells, 2014</a>).</p>'),
    span('<p>A crucial point often overlooked in modern discussions of BMI is that',
         '<li>Defining statistical norms for actuarial science</li> </ul>',
         '<p>Quetelet wasn&rsquo;t measuring obesity. In developing his index, Eknoyan writes, his concern was defining '
         'the characteristics of &ldquo;normal man&rdquo; and fitting the distribution around the norm (' + EKNOYAN +
         'Eknoyan, 2008</a>).</p> <div class="alert alert-info"> <div class="alert-title">Important Historical '
         'Context</div> <p style="margin: 0;">The search for a practical index of relative weight began after life '
         'insurers reported higher death rates among overweight policyholders, and it ended after World War II, when '
         'epidemiologists studying heart disease found the Quetelet index the best of them; Keys named it the body mass '
         'index in 1972 (' + EKNOYAN + 'Eknoyan, 2008</a>).</p> </div>'),
    lit('<h2 id="insurance">Insurance Industry Adoption (1900s-1970s)</h2>', '<h2 id="insurance">Insurance Weight Tables</h2>'),
    span('<p>These tables provided "desirable" weight ranges based on height and frame size',
         '<li>Works across populations</li> </ul> </div> </div>',
         '<p>Louis Dublin, a statistician and vice president of the Metropolitan Life Insurance Company, led the first '
         'tables of normal weights for height; the weights were later split by small, medium and large frames and called '
         '&ldquo;ideal&rdquo;, then &ldquo;desirable&rdquo; (' + EKNOYAN + 'Eknoyan, 2008</a>). The company&rsquo;s 1959 '
         'tables drew on more than 4 million adults, mostly men, insured from 1935 to 1953, and the frame size, judged by '
         'elbow width, was never validated (' + NUTTALL + 'Nuttall, 2015</a>).</p> <p>Keys and colleagues later '
         'preferred the body mass index to percentage of average weight for the simplicity of the calculation and '
         'because it applies to all populations at all times (' + KEYS + 'Keys et al., 1972</a>).</p>'),
    lit('<p>The transformation of the Quetelet Index into the Body Mass Index occurred thanks to <strong>Ancel '
        'Keys</strong> (1904-2004), a pioneering American physiologist best known for the Seven Countries Study that '
        'established the link between diet and cardiovascular disease.</p> <p>In 1972, Keys and his colleagues published '
        'a landmark paper in the <em>Journal of Chronic Diseases</em> titled "Indices of relative weight and obesity." This '
        'study would fundamentally change how the medical community measured body weight.</p>',
        '<p>The American physiologist <strong>Ancel Keys</strong> (1904&ndash;2004) renamed the Quetelet index (' +
        EKNOYAN + 'Eknoyan, 2008</a>). In 1972, Keys and his colleagues published &ldquo;Indices of relative weight and '
        'obesity&rdquo; in the <em>Journal of Chronic Diseases</em> (' + KEYS + 'Keys et al., 1972</a>).</p>'),
    span('<p>Keys analyzed data from 7,424 men across five countries',
         '<li><strong>High correlation with body fat percentage</strong> &mdash; making it useful for health '
         'assessment</li> </ol>',
         '<p>Keys and colleagues analysed 7,424 men in 12 cohorts in five countries (the United States, Finland, Italy, '
         'South Africa and Japan) and compared these indices (' + KEYS + 'Keys et al., 1972</a>):</p> <div '
         'class="table-responsive"> <table class="data-table"> <thead> <tr><th>Index</th><th>Formula</th><th>What Keys and '
         'colleagues found</th></tr> </thead> <tbody> <tr><td>Percentage of average weight</td><td>W as a % of the average '
         'W at that height</td><td>Unlike BMI, doesn&rsquo;t apply to all populations at all times</td></tr> '
         '<tr><td>Weight/Height</td><td>W/H</td><td>Slightly worse than W/H&sup2;</td></tr> <tr><td>Weight/Height&sup2; '
         '(BMI)</td><td>W/H&sup2;</td><td><strong>Slightly better than W/H</strong></td></tr> <tr><td>Ponderal '
         'index</td><td>&#8731;W / H</td><td>The poorest of the indices</td></tr> </tbody> </table> </div> ' + SRC +
         'Source: ' + KEYS + 'Keys et al., 1972</a> (abstract).</p> <p>The two tests were correlation with height, where '
         'lower is better, and with body fatness, measured by skinfolds and, in 180 men, body density, where higher is '
         'better (' + KEYS + 'Keys et al., 1972</a>).</p>'),
    lit('<blockquote> "The body mass index seems preferable over other indices of relative weight on both theoretical and '
        'empirical grounds." <cite>Ancel Keys et al., Journal of Chronic Diseases (1972)</cite> </blockquote> '
        '<p>Crucially, Keys gave the formula a new, more accessible name: <strong>Body Mass Index</strong>. This simple '
        'rebranding helped transform an obscure statistical measure into a household term.</p> <h3>Keys\' Caveats (Often '
        'Forgotten)</h3> <p>Importantly, Keys himself acknowledged significant limitations. He noted that BMI was only '
        '"somewhat better than other indices" and explicitly stated that it was not a perfect measure of body fat. He '
        'recommended BMI for population studies, not individual clinical diagnosis &mdash; echoing Quetelet\'s original '
        'intent from 140 years earlier.</p>',
        '<blockquote> "The body mass index seems preferable over other indices of relative weight on these grounds as '
        'well as on the simplicity of the calculation and, in contrast to percentage of average weight, the '
        'applicability to all populations at all times." <cite>' + KEYS + 'Keys et al., Journal of Chronic Diseases '
        '(1972)</a></cite> </blockquote> <p>The paper named the ratio: &ldquo;the ratio of weight to height squared, here '
        'termed the body mass index&rdquo; (' + KEYS + 'Keys et al., 1972</a>).</p> <h3>What Keys Did and Didn&rsquo;t '
        'Claim</h3> <p>Keys and colleagues judged BMI only slightly better than weight divided by height. And body '
        'composition could be measured accurately in large samples only after BMI was already established as the main '
        'obesity index (' + WELLS + 'Wells, 2014</a>).</p>'),
    lit('<h2 id="nih-adoption">NIH Adoption and the Transformative 1998 Change</h2> <p>The transition from insurance tables '
        'to BMI as the medical standard occurred gradually through the 1980s and 1990s, culminating in two pivotal '
        'decisions by the National Institutes of Health (NIH).</p> <h3>1985: Official NIH Endorsement</h3>',
        '<h2 id="nih-adoption">NIH and the 1998 Cut-Offs</h2> <p>Two NIH steps set out how BMI was to be used in the '
        'United States.</p> <h3>1985: An NIH Consensus Conference</h3> <p>In February 1985, an NIH consensus conference '
        'on the health implications of obesity recommended wider use of BMI, and its summary gave reference tables of '
        'BMI values (' + NIH85 + 'NIH, 1985</a>). Its panel strongly advised treatment for adults with a BMI above 27.8 '
        'for men or 27.3 for women.</p> <h3>1998: The Cut-Offs Used Today</h3>'),
    lit('<div class="stat-box-value">55%</div> <div class="stat-box-label">US adults overweight or obese (NHANES '
        'III)</div>',
        '<div class="stat-box-value">54.9%</div> <div class="stat-box-label">US adults overweight or obese (NHANES '
        'III)</div>'),
    lit('<p>In 1998, the NHLBI\'s clinical guidelines defined overweight as a BMI of 25 to 29.9, so millions of Americans '
        'who had been considered normal weight were reclassified as overweight without gaining a pound. Under the new '
        'definitions, about 55% of US adults were overweight or obese in NHANES III: 32.6% overweight and 22.3% with '
        'obesity (' + NHLBI98E + 'NHLBI Evidence Report, 1998</a>).</p>',
        '<p>NIH&rsquo;s 1998 clinical guidelines set overweight at a BMI of 25 to 29.9 and obesity at 30 or more (' +
        NHLBI98 + 'NHLBI, 1998</a>). US surveys had counted adults as overweight from a BMI of 27.8 for men and 27.3 for '
        'women, so adults between 25 and those values moved into the overweight group (' + NHLBI98 + 'NHLBI, 1998</a>). '
        'By the new definitions, 54.9% of US adults were overweight or obese in NHANES III: 32.6% overweight and 22.3% '
        'with obesity (' + NHLBI98E + 'NHLBI Evidence Report, 1998</a>).</p>'),
    lit('<h2 id="who-standardization">WHO Global Standardization (1995-2000)</h2> <p>While the NIH was establishing BMI as '
        'the US standard, the World Health Organization (WHO) was working to create global standards that could be '
        'applied across all countries and ethnicities.</p>',
        '<h2 id="who-standardization">WHO Global Standardization</h2> <p>WHO&rsquo;s 1995 report on anthropometry graded '
        'adult thinness by BMI: below 18.5, below 17 and below 16 (' + WHO854 + 'WHO, 1995</a>). Its 2000 report on '
        'obesity set out classes I (30 to 34.9), II (35 to 39.9) and III (40 or more) and concluded that a coherent '
        'system based on BMI should be adopted internationally (' + WHO894 + 'WHO, 2000</a>).</p>'),
    span('<p>While not establishing strict alternative cutoffs, the WHO acknowledged that for Asian populations:</p>',
         'have adopted modified BMI cutoffs reflecting these findings.</p>',
         '<p>A WHO expert consultation kept the international cut-offs but found that the share of Asian people at high '
         'risk of type 2 diabetes and cardiovascular disease is substantial below the overweight cut-off of 25, and it '
         'named public health action points at a BMI of 23.0, 27.5, 32.5 and 37.5 (' + WHO2004 + 'WHO Expert '
         'Consultation, 2004</a>).</p>'),
    lit('<h4>Ignores Fat Distribution</h4>  </div>',
        '<h4>Ignores Fat Distribution</h4> <p>BMI says nothing about where fat sits. NIH&rsquo;s 1998 guidelines add '
        'waist circumference because excess abdominal fat is an independent risk factor for disease (' + NHLBI98 +
        'NHLBI, 1998</a>).</p> </div>'),
    lit('<p>Women naturally carry more body fat than men at the same BMI. Some researchers suggest different healthy ranges '
        'for <a href="/women-bmi-calculator/">women</a> and <a href="/men-bmi-calculator/">men</a>.</p>',
        '<p>Women carry more body fat than men at the same BMI. In CDC&rsquo;s 2011&ndash;2018 body scans of adults aged '
        '20 to 59 with a BMI of 18.5 to 24.9, the median body fat was 33.4% for women and 22.1% for men (our <a '
        'href="/body-fat-percentage-chart/">body fat percentage chart</a> uses the same scans).</p>'),
    lit('<p>Research has identified situations where higher BMI appears protective rather than harmful. Some studies show '
        'that "overweight" elderly individuals have better survival rates than "normal weight" peers, and that patients '
        'with certain chronic diseases fare better at higher BMI. This phenomenon, called the "obesity paradox," suggests '
        'that BMI cutoffs may need age-specific adjustments.</p>',
        '<p>One pattern called the &ldquo;obesity paradox&rdquo; shows up in older adults: compared with a BMI of 23 to '
        '23.9, the risk of death was higher below 23 and began to rise at about 33 (' + WINTER + 'Winter et al., '
        '2014</a>).</p>'),
    lit('<p>The New BMI addresses the height bias in standard BMI, giving more accurate comparisons between short and tall '
        'individuals. Try it with our <a href="/new-bmi-calculator/">New BMI calculator</a>.</p>',
        '<p>Trefethen argues that the 2.5 power fits the shapes of short and tall people better than the square, which '
        'makes short people think they are thinner, and tall people fatter, than they are; he adds that his formula is '
        'not based on epidemiological studies (' + TREF + 'Trefethen</a>). Try it with our <a '
        'href="/new-bmi-calculator/">New BMI calculator</a>.</p>'),
    lit('<p>Rather than relying on BMI alone, guidelines increasingly recommend combining multiple measures. The CDC and '
        'other organizations now suggest using BMI alongside waist circumference for a more complete risk assessment.</p>',
        '<p>Guidelines pair BMI with other measures. NIH&rsquo;s 1998 guidelines read waist circumference alongside BMI '
        'in adults with a BMI of 25 to 34.9 (' + NHLBI98 + 'NHLBI, 1998</a>), and NICE now uses waist-to-height ratio '
        '(' + NICE + 'NICE NG246</a>).</p>'),
    lit(' Some researchers envision "smart BMI" calculations that adjust cutoffs based on individual factors.', ''),
    faq('Who invented BMI and when?',
        'Belgian mathematician, astronomer and statistician Adolphe Quetelet described the index in 1832, and it became '
        'known as the Quetelet index. Ancel Keys and colleagues named it the body mass index in a 1972 paper in the '
        'Journal of Chronic Diseases, 140 years later. So the formula is nearly 200 years old and the name BMI just over '
        '50.'),
    faq('Why was BMI originally created?',
        'Quetelet was studying the average man (l\'homme moyen): he applied probability to human physical characteristics '
        'and social aptitudes. In developing his index he had no interest in obesity; his concern was the '
        'characteristics of normal man and the distribution around the norm (Eknoyan, 2008).'),
    faq('When did BMI become a medical standard?',
        'In stages. In 1985 an NIH consensus conference recommended wider use of BMI. NIH\'s 1998 guidelines then set '
        'overweight at a BMI of 25 to 29.9 and obesity at 30 or more. WHO\'s 2000 report set the obesity classes used '
        'today. Earlier weight standards came from insurers, such as Metropolitan Life\'s 1959 tables of desirable '
        'weights.'),
    faq('What is Trefethen\'s "New BMI" and is it better?',
        'In 2013, Oxford mathematician Nick Trefethen proposed a modified formula: New BMI = 1.3 × weight (kg) / '
        'height (m)^2.5. He argues that the standard BMI makes short people think they are thinner, and tall people '
        'fatter, than they are; he also writes that his formula is not based on epidemiological studies and may not be '
        'an improvement. Try our New BMI calculator to see how your results compare.'),
    faq('Did Quetelet know his formula would be used for health assessment?',
        'No. Quetelet was a mathematician, astronomer and statistician studying the average man, and in developing his '
        'index he had no interest in obesity (Eknoyan, 2008). Medical use came after World War II, when heart disease '
        'epidemiology took up the Quetelet index, which Keys named the body mass index in 1972.'),
    lit('<p>Try Trefethen\'s improved BMI formula</p>', '<p>Try Trefethen\'s proposed BMI formula</p>'),
    lit('<li>WHO: Obesity and Overweight Fact Sheet</li> <li><a href="https://www.cdc.gov/bmi/" target="_blank" '
        'rel="noopener">CDC: About BMI</a></li> <li>: How useful is BMI?</li> </ul>',
        '<li>' + WHOFS + 'WHO: Obesity and Overweight Fact Sheet</a></li> <li><a href="https://www.cdc.gov/bmi/" '
        'target="_blank" rel="noopener">CDC: About BMI</a></li> <li>Eknoyan G. (2008). ' + EKNOYAN + 'Adolphe Quetelet '
        '(1796&ndash;1874): the average man and indices of obesity</a>. <em>Nephrology Dialysis Transplantation</em>, '
        '23(1), 47-51.</li> <li>Nuttall FQ. (2015). ' + NUTTALL + 'Body Mass Index: Obesity, BMI, and Health: A Critical '
        'Review</a>. <em>Nutrition Today</em>, 50(3), 117-128.</li> <li>NIH Consensus Development Conference. (1985). ' +
        NIH85 + 'Health implications of obesity</a>. <em>International Journal of Obesity</em>, 9(3), 155-170.</li> '
        '<li>Winter JE, et al. (2014). ' + WINTER + 'BMI and all-cause mortality in older adults: a meta-analysis</a>. '
        '<em>American Journal of Clinical Nutrition</em>, 99(4), 875-890.</li> </ul>'),
    lit('<li>IJE 2014 commentary on the post-1972 adoption of BMI as the primary obesity index: <a '
        'href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4052141/" target="_blank" rel="noopener">PMC4052141</a>.</li>',
        '<li>Wells JCK. Commentary: The paradox of body mass index in obesity assessment. <em>Int J Epidemiol</em>. '
        '2014;43(3):672&ndash;674. ' + WELLS + 'PMC4052141</a>.</li>'),
]

EDITS[WHT] = [
    lit('content="Learn how to calculate your waist-to-height ratio (WHtR), a simple metric that predicts health risks '
        'better than BMI. Free calculator, healthy ranges, and research-backed guidelines."',
        'content="How to work out your waist-to-height ratio (WHtR), the healthy and increased-risk ranges NICE uses, and '
        'what the research says about it compared with BMI."'),
    lit('<li><strong>The golden rule: keep your waist less than half your height</strong> - a WHtR under 0.5 indicates '
        'healthy abdominal fat levels for both men and women</li> <li><strong>WHtR outperforms BMI</strong> in '
        'predicting cardiovascular disease, type 2 diabetes, and all-cause mortality according to multiple large-scale '
        'studies</li>',
        '<li><strong>Keep your waist to less than half your height:</strong> NICE classes a ratio of 0.4 to 0.49 as '
        'healthy central adiposity and 0.5 or more as increased, for men and women (' + NICE + 'NICE NG246</a>)</li> '
        '<li><strong>WHtR beat BMI</strong> and waist circumference at detecting cardiometabolic risk factors in both '
        'sexes, in a meta-analysis of more than 300,000 adults (' + ASHWELL + 'Ashwell et al., 2012</a>)</li>'),
    lit('<li><strong>Universal threshold:</strong> unlike BMI, the same 0.5 cutoff works for men, women, and children of '
        'all ethnicities</li>',
        '<li><strong>One boundary:</strong> NICE uses the same 0.5 boundary for both sexes and all ethnicities, and for '
        'children and young people from age 5 (' + NICE + 'NICE NG246</a>)</li>'),
    lit('This "keep your waist to less than half your height" message is easy to remember and applies universally across '
        'age, sex, and ethnicity.</p>',
        'NICE uses that message for adults and for children and young people aged 5 and over (' + NICE + 'NICE '
        'NG246</a>).</p>'),
    lit(' <p>WHtR was first proposed as a health indicator in the 1990s and has been studied as a screening tool for '
        'central adiposity since.</p>', ''),
    lit('<p>The same 0.5 threshold works for everyone - men, women, children, all ethnicities.</p>',
        '<p>NICE applies the same 0.5 boundary to both sexes and all ethnicities.</p>'),
    lit('<p>Multiple large-scale studies confirm WHtR outperforms BMI for predicting health risks.</p>',
        '<p>A meta-analysis of more than 300,000 adults found WHtR better than BMI at detecting cardiometabolic risk '
        'factors (' + ASHWELL + 'Ashwell et al., 2012</a>).</p>'),
    lit(' The 0.5 threshold is discussed in the Healthy Ranges section below.</figcaption>', '</figcaption>'),
    lit('<td style="color: var(--overweight-strong);">Increased Risk</td>', '<td style="color: var(--overweight-strong);">'
        'Increased</td>', 2),
    lit('<td style="color: var(--obese-strong);">High Risk</td>', '<td style="color: var(--obese-strong);">High</td>'),
    span('<div class="chart-bar-h"> <div class="chart-bar-h-item"> <span class="chart-bar-h-label">Underweight Risk</span>',
         '<div class="chart-bar-h-fill obese" style="width: 60%;">0.6+</div> </div> </div> </div>',
         '<div class="chart-bar-h"> <div class="chart-bar-h-item"> <span class="chart-bar-h-label">Healthy central '
         'adiposity</span> <div class="chart-bar-h-track"> <div class="chart-bar-h-fill primary" style="width: '
         '50%;">0.4 - 0.49</div> </div> </div> <div class="chart-bar-h-item"> <span class="chart-bar-h-label">Increased '
         'central adiposity</span> <div class="chart-bar-h-track"> <div class="chart-bar-h-fill overweight" '
         'style="width: 50%;">0.5 - 0.59</div> </div> </div> <div class="chart-bar-h-item"> <span '
         'class="chart-bar-h-label">High central adiposity</span> <div class="chart-bar-h-track"> <div '
         'class="chart-bar-h-fill obese" style="width: 60%;">0.6 or more</div> </div> </div> </div> ' + SRC +
         'Source: ' + NICE + 'NICE NG246</a>, for adults with a BMI under 35 of both sexes and all ethnicities.</p>'),
    lit('<p>To maintain a WHtR under 0.5, your maximum waist circumference should be:</p>',
        '<p>Half your height is the waist at a ratio of 0.5; a waist below it keeps the ratio under 0.5:</p>'),
    lit('<th>Maximum Healthy Waist</th>', '<th>Waist at a Ratio of 0.5</th>'),
    lit('<li>Universal threshold (0.5) for all populations</li>',
        '<li>One boundary, 0.5, for both sexes and all ethnicities (' + NICE + 'NICE NG246</a>)</li>'),
    lit('pooled data from roughly 300,000 adults across multiple populations. They reported that WHtR discriminated '
        'diabetes, hypertension, and cardiovascular risk factors better than BMI or waist circumference in both sexes.</p>',
        'pooled 31 studies of more than 300,000 adults and reported &ldquo;the superiority of WHtR over WC and BMI for '
        'detecting cardiometabolic risk factors in both sexes&rdquo;.</p>'),
    lit('<blockquote> "Waist-to-height ratio is a better screening tool than BMI for discriminating cardiometabolic risk '
        'factors in both sexes." <cite>Ashwell M, et al., Obesity Reviews (2012)</cite> </blockquote>',
        '<blockquote> "Waist-to-height ratio should therefore be considered as a screening tool." <cite>' + ASHWELL +
        'Ashwell M, et al., Obesity Reviews (2012)</a></cite> </blockquote>'),
    lit('<p>An earlier review by Browning, Hsieh &amp; Ashwell in <em>Nutrition Research Reviews</em> (2010) pooled '
        'diagnostic-accuracy data across 14 countries and reported a mean AUROC of 0.704 for WHtR, 0.693 for waist '
        'circumference, and 0.671 for BMI, with a boundary value of 0.5 for both men and women.',
        '<p>An earlier systematic review of 78 studies by Browning, Hsieh and Ashwell (' + BROWNING + '<em>Nutrition '
        'Research Reviews</em>, 2010</a>) found a mean area under the ROC curve of 0.704 for WHtR, 0.693 for waist '
        'circumference and 0.671 for BMI, and a mean boundary value of 0.50 for men and for women in studies from 14 '
        'countries.'),
    lit('<div class="alert-title">The Hidden Danger</div> People with normal BMI but high WHtR (often called "metabolically '
        'obese, normal weight" or MONW) face similar health risks to those classified as obese by BMI. This condition is '
        'invisible to BMI screening but clearly identified by WHtR. </div>',
        '<div class="alert-title">A Healthy BMI Can Hide It</div> The ratio doesn&rsquo;t use weight, so a person with a '
        'BMI of 18.5 to 24.9 can still have a waist-to-height ratio of 0.5 or more, which NICE classes as increased '
        'central adiposity (' + NICE + 'NICE NG246</a>). </div>'),
    span(' The same 0.5 threshold applies to children of all ages.</p>',
         'and the simple 0.5 cutoff worked across all age groups from 5 to 18 years.</p>',
         ' NICE uses the same boundaries for children and young people aged 5 and over, and only from that age (' + NICE +
         'NICE NG246</a>).</p>'),
    span('<p>Unlike BMI, which requires <a href="/blog/bmi-limitations/#ethnic-variations">adjusted cutoffs for different '
         'ethnic groups</a>, WHtR appears to work effectively with the same 0.5 threshold across populations.',
         'you may benefit from aiming for WHtR well below 0.5.</p>',
         '<p>NICE lowers the <a href="/blog/bmi-limitations/#ethnic-variations">BMI thresholds</a> for people of South '
         'Asian, Chinese, other Asian, Middle Eastern, Black African or African-Caribbean background but uses the same '
         'waist-to-height ratio boundaries for all ethnicities (' +
         NICE + 'NICE NG246</a>).</p> <p>The review by Browning and colleagues found its 0.50 boundary in studies of '
         'Caucasian, Asian and Central American people (' + BROWNING + 'Browning et al., 2010</a>).</p>'),
    lit('<p>If your WHtR exceeds 0.5, the good news is that abdominal fat is often the first to respond to lifestyle '
        'changes. Here are evidence-based strategies to reduce your waist circumference:</p>',
        '<p>If your ratio is 0.5 or more, NICE suggests seeking advice and further assessment from a healthcare '
        'professional (' + NICE + 'NICE NG246</a>).</p>'),
    lit('If your WHtR exceeds 0.5 or you have concerns about your health, please consult with your doctor.',
        'NICE suggests asking a healthcare professional for further assessment when the ratio shows an increased '
        'health risk, 0.5 or more (' + NICE + 'NICE NG246</a>).'),
    faq('What is a healthy waist-to-height ratio?',
        'NICE guideline NG246 classes a ratio of 0.4 to 0.49 as healthy central adiposity for both men and women, so '
        'your waist should be less than half your height. In NG246 a ratio of 0.5 to 0.59 is increased central '
        'adiposity, with increased health risks, and 0.6 or more is high central adiposity, with further increased '
        'health risks.'),
    faq('Does waist-to-height ratio work for children?',
        'Yes, from age 5. NICE guideline NG246 uses waist-to-height ratio for children and young people aged 5 and '
        'over, with the same boundaries as for adults, and says to explain to them that they should try to keep their '
        'waist to half their height.'),
    faq('What\'s the difference between waist-to-height and waist-to-hip ratio?',
        'Waist-to-height ratio compares waist size with height; NICE guideline NG246 uses the same 0.5 boundary for men '
        'and women. Waist-to-hip ratio compares waist with hip circumference, and the WHO cut-offs for substantially '
        'increased risk differ by sex: 0.90 for men and 0.85 for women (WHO, 2008). The waist-to-height ratio needs one '
        'tape measurement and your height; the hip ratio needs two tape measurements.'),
    faq('Can I have a normal BMI but unhealthy WHtR?',
        'Yes. The ratio doesn\'t use weight, so a BMI of 18.5 to 24.9 can come with a waist of half your height or more, '
        'a ratio NICE guideline NG246 classes as increased central adiposity. That is why NICE pairs the ratio with BMI '
        'for adults with a BMI under 35.'),
    faq('How quickly can I improve my WHtR?',
        'There is no set timetable. CDC notes that people who lose about 1 to 2 pounds a week are more likely to keep '
        'the weight off, so aim for steady change rather than rapid weight loss.'),
]

# Second pass (anti-slop read of the new text, and the two social images): applied after the edits above.
# /blog/bmi-and-metabolism/ shares and lists the site card: its old image drew a TDEE donut whose arcs overlap, with a
# "60-75% per NIDDK" share the page doesn't state and no registry row holds; the page has no figure to redraw from.
EDITS[MET] += [
    lit('https://calculatemybmi.net/assets/images/og/metabolism-tdee-donut.png',
        'https://calculatemybmi.net/assets/images/og-image.png', 3),
    # read against the abstract in Chrome: one study of 3.5 million adults, not "the largest"
    lit('Definitions vary; the largest study, of 3.5 million UK adults, counted',
        'Definitions vary; a study of 3.5 million UK adults counted'),
    # D-11: the age page gives no age-specific recommendations
    lit('Our <a href="/age-bmi-calculator/">BMI by age guide</a> provides age-specific recommendations.</p>',
        'Our <a href="/age-bmi-calculator/">BMI by age guide</a> explains how BMI is read at different ages.</p>'),
]
EDITS[HIS] += [
    lit('The Body Mass Index has a fascinating 200-year journey from', 'The Body Mass Index has a 200-year history, from'),
    lit("Same events plotted on a continuous time-axis. The century-long gap between Quetelet's derivation and clinical "
        'adoption is easier to feel than the step-list above shows.</figcaption>',
        'The same events on a continuous time axis, so the gaps between them are to scale.</figcaption>'),
]
EDITS[WHT] += [
    lit('The concept is elegantly simple: <strong>your waist', 'The rule is simple: <strong>your waist'),
    lit('<p>While BMI remains the most commonly used health screening metric, research increasingly shows that WHtR is '
        "superior for predicting actual health outcomes. Here's why:</p>",
        '<p>BMI is the more common screening measure. How the two compare:</p>'),
    # the figure's own text: NICE's boundary is "0.5 or more" (increased), and the callouts sit left of the torso
    lit('fill="#7f1d1d">&gt; 0.5</text> <text x="50" y="246" text-anchor="middle" font-size="10" '
        'fill-opacity="0.85">elevated risk</text>',
        'fill="#7f1d1d">≥ 0.5</text> <text x="50" y="246" text-anchor="middle" font-size="10" '
        'fill-opacity="0.85">increased risk</text>'),
    lit('Schematic torso figure with a highlighted band at the natural waist (mid-way between the lower rib and the top '
        'of the hip bone, approximately at the navel). A tape-measure ring wraps that band. A callout box to the right '
        'shows WHtR equals waist divided by height, with the 0.5 threshold marked.',
        'Schematic torso figure with a highlighted band at the natural waist, mid-way between the lower rib and the top '
        'of the hip bone. A tape-measure ring wraps that band. Callout boxes on the left give the formula, waist '
        'divided by height, and mark a ratio of 0.5 or more as increased risk.'),
    # the three lists claimed effects with no source ("has been shown", "strongly linked", "effective for"); official
    # guidance only (D-06, D-10)
    # the children's section said "no percentile charts" twice and "exceeds half their height ... may warrant
    # attention"; NICE's boundary is half the height or more
    span('<p>WHtR offers significant advantages over ',
         'regardless of what their BMI percentile shows.</p>',
         '<p>Unlike <a href="/kids-bmi-calculator/">BMI for children</a>, the ratio needs no age-specific percentile '
         'chart: NICE uses the same boundaries for children and young people aged 5 and over, and only from that age ('
         + NICE + 'NICE NG246</a>). A child whose waist is half their height or more has a ratio NICE classes as '
         'increased central adiposity, whatever their BMI percentile.</p>'),
    span('<h3>Dietary Changes</h3> <ul> <li><strong>Reduce refined carbohydrates',
         'Smokers tend to have higher WHtR despite lower body weight</li> </ul>',
         '<p>On the pace of weight loss, CDC notes that people who lose about 1 to 2 pounds a week are more likely to '
         'keep the weight off (' + CDCLW + 'CDC</a>). On activity, the federal Physical Activity Guidelines say adults '
         'need at least 150 to 300 minutes of moderate-intensity aerobic activity a week, and muscle-strengthening '
         'activity at least 2 days each week (' + ODPHP + 'Physical Activity Guidelines for Americans</a>).</p>'),
]

# files this batch removes: the metabolism page's old social image (see EDITS[MET] above)
REMOVE = {'assets/images/og/metabolism-tdee-donut.png':
          'e1f304edbd19ed0155ca4956794848a8ebaf96b1c294a9225c890f340e43f7d3'}
# rows of research/page-scores-known.csv this batch closes (DEVLOG §5 items fixed above)
KNOWN = 'research/page-scores-known.csv'
KNOWN_BASE = 'e7dee360e6f6304c5ec004e7f14b743dbfa92e1f2f8db4a5f1445cd67f8c0e41'
KNOWN_CLOSE = ['/blog/bmi-and-metabolism/', '/blog/how-to-lower-bmi/', '/blog/bmi-history/']

DATES = {
    MET: [('"dateModified": "2026-11-07"', f'"dateModified": "{TODAY}"')],
    LOW: [('"dateModified": "2026-11-11"', f'"dateModified": "{TODAY}"'),
          ('<meta property="article:modified_time" content="2026-08-10T00:00:00Z">',
           f'<meta property="article:modified_time" content="{TODAY}T00:00:00Z">')],
    HIS: [('"dateModified": "2026-10-14"', f'"dateModified": "{TODAY}"'),
          ('<meta property="article:modified_time" content="2026-08-12T00:00:00Z">',
           f'<meta property="article:modified_time" content="{TODAY}T00:00:00Z">')],
    WHT: [('"dateModified": "2026-11-11"', f'"dateModified": "{TODAY}"')],
}
SITEMAP = [
    ('<loc>https://calculatemybmi.net/blog/bmi-and-metabolism/</loc><lastmod>2026-11-07</lastmod>',
     f'<loc>https://calculatemybmi.net/blog/bmi-and-metabolism/</loc><lastmod>{TODAY}</lastmod>'),
    ('<loc>https://calculatemybmi.net/blog/how-to-lower-bmi/</loc><lastmod>2026-11-11</lastmod>',
     f'<loc>https://calculatemybmi.net/blog/how-to-lower-bmi/</loc><lastmod>{TODAY}</lastmod>'),
    ('<loc>https://calculatemybmi.net/blog/bmi-history/</loc><lastmod>2026-10-14</lastmod>',
     f'<loc>https://calculatemybmi.net/blog/bmi-history/</loc><lastmod>{TODAY}</lastmod>'),
    ('<loc>https://calculatemybmi.net/blog/waist-to-height-ratio/</loc><lastmod>2026-11-11</lastmod>',
     f'<loc>https://calculatemybmi.net/blog/waist-to-height-ratio/</loc><lastmod>{TODAY}</lastmod>'),
]


def main():
    out = {}
    for rel, sha in BASE.items():
        h = (REPO / rel).read_text(encoding='utf-8')
        got = hashlib.sha256(h.encode('utf-8')).hexdigest()
        if got != sha:
            sys.exit(f'{rel}: not the base this batch was written for (sha256 {got[:12]}, expected {sha[:12]})')
        out[rel] = h
    for rel, edits in EDITS.items():
        h = out[rel]
        for e in edits:
            h = do(h, e, rel)
        for old, new in DATES[rel]:
            h = do(h, lit(old, new), rel)
        out[rel] = h
    s = out['sitemap.xml']
    for old, new in SITEMAP:
        s = do(s, lit(old, new), 'sitemap.xml')
    out['sitemap.xml'] = s
    for rel, sha in REMOVE.items():
        got = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        if got != sha:
            sys.exit(f'{rel}: not the file this batch removes (sha256 {got[:12]}, expected {sha[:12]})')
    k = (REPO / KNOWN).read_bytes()
    if hashlib.sha256(k).hexdigest() != KNOWN_BASE:
        sys.exit(f'{KNOWN}: not the base this batch was written for')
    lines = k.decode('utf-8').splitlines(keepends=True)
    keep = [x for x in lines if not any(x.startswith(p + ',S,') for p in KNOWN_CLOSE)]
    if len(lines) - len(keep) != len(KNOWN_CLOSE):
        sys.exit(f'{KNOWN}: expected to close {len(KNOWN_CLOSE)} rows, found {len(lines) - len(keep)}')
    n = sum(len(v) for v in EDITS.values())
    if CHECK:
        print(f'check: {n} edits apply to the four pages, dates and sitemap; {len(REMOVE)} file to remove, '
              f'{len(KNOWN_CLOSE)} known rows to close; nothing written')
        return
    for rel, h in out.items():
        (REPO / rel).write_text(h, encoding='utf-8')
    for rel in REMOVE:
        (REPO / rel).unlink()
    (REPO / KNOWN).write_bytes(''.join(keep).encode('utf-8'))
    print(f'{n} edits applied; dates {TODAY}; wrote {len(out)} files, removed {len(REMOVE)}, closed '
          f'{len(KNOWN_CLOSE)} rows of {KNOWN}')


if __name__ == '__main__':
    main()
