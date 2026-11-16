#!/usr/bin/env python3
"""CMB-061 CLAIMS-12: claims pass batch 12 (DEVLOG §5 P1) on /blog/body-fat-vs-bmi/ (7 probe hits, and the lines round
them that had no source). Each line now says what a registry row says, or went (D-10, D-06):
  - intro: "widely used due to its simplicity" and "crucial" become CDC's two lines on BMI;
  - categories table: a source line (CDC; WHO 2000 for the classes);
  - "What Is Body Fat Percentage?": "directly measures one of the key components that actually impacts health", the
    essential/storage fat list (no source) and "many health professionals now recommend tracking body fat" become CDC,
    NIH's abdominal fat line and NCI's visceral fat line;
  - healthy ranges: "due to physiological differences" out; Gallagher's provisional ranges, with Table 4's healthy range
    for women and men aged 20 to 39, in;
  - measuring: "(preferably in the morning, after using the bathroom)" and "personalized insights" out; a "Measuring Body
    Fat" h3 with CDC's own words on DXA;
  - scenario 1: the "30% of normal BMI individuals" tile had no source (the audit had it as an illustration), nor did
    "Higher Risk metabolic syndrome", "Often Missed" or "increased risks for type 2 diabetes, cardiovascular disease, and
    metabolic syndrome"; the scenario now says what CDC says BMI can't show;
  - scenario 2: "extremely common among" and the four-group list become CDC and Provencher et al. (2018): at the NFL
    Combine BMI classed 53.4% of players as obese, body fat 8.9%;
  - scenario 3: 30% body fat is healthy for a woman of 20 to 39, so the two people are now men aged 20 to 39, on
    Gallagher's ranges; "vastly different health profiles" out;
  - accuracy: the two lists keep what CDC, NIH, Gallagher, Provencher and GBMC back, with a source line ("Widely
    understood by healthcare providers" out); Burns et al. (2019) for the body fat methods;
  - "Which Metric Is Better": "body fat percentage is generally more informative", "BMI works well for the general
    population", "the most accurate individual health assessment" and "the most comprehensive health assessment" become
    CDC, NICE 1.9.13 and NIH;
  - "Using Both": "The most effective approach" and the interpretation table ("Ideal body composition", "Likely muscular -
    healthy", ...) out; "Men should aim for < 40 inches" (a target, D-06) becomes NIH's risk line; CDC for blood pressure
    and cholesterol.
dateModified and lastmod follow. Title and H1 kept (the page has Search Console impressions, D-28).
usage: python3 research/cmb-061/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PG, SM = 'blog/body-fat-vs-bmi/index.html', 'sitemap.xml'
BASE = {PG: '424d3b892bb426be546d91d2914ba51ff1a36b744cd8a0fbc092444b28ea9280',
        SM: 'e38e094d3cefbc94da15796cb36ee01eb684ff55bfcdcad045de60639e7214fe'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'who00': 'https://pubmed.ncbi.nlm.nih.gov/11234459/',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
    'gal': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'dxa': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
    'prov': 'https://doi.org/10.1519/JSC.0000000000002449',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


CDC_Q = '“a quick, low-cost, and reliable screening measure”'

EDITS = [
    ('<p>While BMI is widely used due to its simplicity, it has significant <a href="/blog/bmi-limitations/">limitations</a> '
     'that we\'ll explore throughout this guide. Understanding these limitations is crucial for interpreting your BMI results '
     'accurately.</p>',
     f'<p>CDC calls BMI {CDC_Q}, but it does not directly measure body fat ({a("cdc_about", "CDC")}). Body fat percentage '
     'does, and the two can disagree; our <a href="/blog/bmi-limitations/">BMI limitations</a> guide covers the rest.</p>'),
    ('<td><span class="category-dot" style="background: var(--obese-severe);"></span>Obese Class III</td></tr></table> </div>',
     '<td><span class="category-dot" style="background: var(--obese-severe);"></span>Obese Class III</td></tr></table> </div> '
     f'<p class="source-note">Categories: {a("cdc_cat", "CDC")}; obesity classes I to III: {a("who00", "WHO, 2000")}.</p>'),
    ('Unlike BMI, it directly measures one of the key components that actually impacts health: adipose (fat) tissue.',
     f'Unlike BMI, which does not directly measure body fat ({a("cdc_about", "CDC")}), it is a measure of fat itself.'),
    ('<p>Your body contains two types of fat:</p> <ul> <li><strong>Essential fat:</strong> Required for normal physiological '
     'function, including hormone regulation, vitamin absorption, and organ protection.</li> <li><strong>Storage fat:</strong> '
     'Energy reserves stored beneath the skin (subcutaneous) and around organs (visceral). Excess storage fat, particularly '
     'visceral fat, is associated with health risks.</li> </ul> <p>Body fat percentage provides a more complete picture of '
     'body composition than weight alone. This is why many health professionals now recommend tracking body fat alongside or '
     'instead of BMI.</p>',
     '<p>Where fat sits matters too. NIH calls excess abdominal fat an important, independent risk factor for disease '
     f'({a("nhlbi", "NHLBI, 1998")}), and NCI says visceral fat, around the organs, seems to carry more disease risk than '
     f'overall or subcutaneous fat ({a("nci", "NCI")}).</p>'),
    ('<p>One of the most significant differences between BMI and body fat percentage is how healthy ranges are defined. While '
     'BMI uses a single scale for all adults, body fat percentage ranges vary significantly between men and women due to '
     'physiological differences.</p> <p>No universally accepted healthy body-fat ranges exist. A widely cited 2000 study '
     'proposed provisional ranges by translating the healthy BMI range into predicted body fat for each age, sex and ethnic '
     'group (<a href="https://pubmed.ncbi.nlm.nih.gov/10966886/" target="_blank" rel="noopener">Gallagher et al., Am J Clin '
     'Nutr 2000</a>).</p>',
     f'<p>BMI uses one set of categories for all adults ({a("cdc_cat", "CDC")}). Body fat had no accepted published ranges '
     'when, in 2000, Gallagher and colleagues proposed provisional ones by translating the healthy BMI range into predicted '
     f'body fat by age, sex and ethnic group ({a("gal", "Gallagher et al., Am J Clin Nutr 2000")}). For African American and '
     'white adults aged 20 to 39, the healthy range they proposed is 21 to 32.9% for women and 8 to 19.9% for men (Table 4); '
     'our <a href="/body-fat-percentage-chart/">body fat percentage chart</a> has every age.</p>'),
    ('<li><strong>Weight:</strong> Measured using a scale (preferably in the morning, after using the bathroom)</li>',
     '<li><strong>Weight:</strong> Measured on a scale, in light clothing</li>'),
    ('<p>Our <a href="/">free BMI calculator</a> instantly computes your BMI and provides category classification, ideal weight '
     'ranges, and personalized insights.</p>',
     '<p>Our <a href="/">BMI calculator</a> works it out and gives your CDC category and the healthy weight range for your '
     'height.</p> <h3>Measuring Body Fat</h3> <p>CDC calls DXA “the most widely accepted method of measuring body composition” '
     f'({a("dxa", "CDC")}); tape measures, calipers and body fat scales estimate body fat from other measurements. Our '
     '<a href="/body-fat-calculator/">body fat calculator</a> works from a tape measure, calipers, or height and weight.</p>'),
    ('<p>Perhaps the most important reason to understand both metrics is that they can provide contradictory assessments. BMI '
     'and body fat can tell different stories in several common situations.</p>',
     '<p>BMI and body fat can disagree in three ways.</p>'),
    ('<h2 id="athletes">Why Athletes Often Have High BMI But Low Body Fat</h2>   <p>Muscle adds weight, and BMI cannot tell it '
     'from fat, so a muscular athlete can have a high BMI and a low body fat percentage. For athletes and highly active people, '
     'body fat percentage together with <a href="/lean-body-mass/">lean body mass</a> says more than BMI alone; '
     '<a href="/blog/bmi-for-athletes/">BMI for athletes</a> covers the research.</p>',
     '<h2 id="athletes">Why Athletes Often Have High BMI But Low Body Fat</h2> <p>Muscle adds weight, and BMI does not '
     f'distinguish it from fat ({a("cdc_about", "CDC")}), so a muscular athlete can have a high BMI and a low body fat '
     'percentage. Body fat percentage and <a href="/lean-body-mass/">lean body mass</a> add what BMI leaves out; '
     '<a href="/blog/bmi-for-athletes/">BMI for athletes</a> covers the research.</p>'),
    ('<p>When evaluating accuracy, we need to consider what each metric is trying to measure and how well it achieves that '
     'goal.</p> ', ''),
    ('<p>For a deeper dive into these issues, see our comprehensive guide on <a href="/blog/bmi-limitations/">BMI accuracy</a>.'
     '</p> <h3>Body Fat Percentage Accuracy</h3><p>DEXA is commonly used as a reference method in research. For accuracy '
     'figures from a study that tested seven methods against DXA, see <a href="/blog/how-to-measure-body-fat/">how to '
     'calculate body fat percentage</a>.</p>',
     '<p class="source-note">Sources: ' + a('cdc_about', 'CDC, About BMI') + '; ' + a('cdc_cat', 'CDC, adult categories') +
     '; NIH reads the waist alongside BMI (' + a('nhlbi', 'NHLBI, 1998') + '); ' + a('gal', 'Gallagher et al., 2000') + '; '
     + a('prov', 'Provencher et al., 2018') + '; ' + a('gbmc', 'Global BMI Mortality Collaboration, 2016') + '.</p> '
     '<p>Our <a href="/blog/bmi-limitations/">BMI limitations guide</a> goes through each one.</p> <h3>Body Fat Percentage '
     'Accuracy</h3><p>In a study of 437 college students that tested seven methods against DXA, seven-site skinfolds read 1.4 '
     'points below DXA on average and a hand-held impedance device was 4.9 points off '
     f'({a("burns", "Burns et al., 2019")}); our guide to <a href="/blog/how-to-measure-body-fat/">how to measure body '
     'fat</a> has the rest.</p>'),
    ('<p>The short answer: <strong>body fat percentage is generally more informative for individual health assessment</strong>, '
     'but BMI still has its place. Here\'s a framework for choosing which metric to prioritize:</p>',
     f'<p>Each answers a different question. CDC calls BMI {CDC_Q} and says that, for individuals, it should be considered '
     f'with other factors, such as blood pressure and cholesterol levels ({a("cdc_about", "CDC")}). When to use which:</p>'),
    ('<p>You need a quick health screening, have no access to body fat measurement, or are tracking population-level health '
     'data. BMI works well for the general population.</p>',
     '<p>You need a quick screen, have no way to measure body fat, or are comparing with US or WHO figures, which use '
     'BMI.</p>'),
    ('<p>You\'re athletic or muscular, making specific body composition goals, older (65+), or want the most accurate '
     'individual health assessment.</p>',
     '<p>You’re very muscular, tracking body composition, or 65 or older, an age at which NICE advises caution in reading '
     f'BMI ({a("nice", "NICE NG246")}).</p>'),
    ('<p>You want a complete picture. Tracking both metrics together, along with waist circumference, provides the most '
     'comprehensive health assessment.</p>',
     f'<p>You want both answers. NIH also reads the waist alongside BMI from 25 to 34.9 ({a("nhlbi", "NHLBI, 1998")}).</p>'),
    ('<a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>, which helps assess visceral fat,',
     '<a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>, which NICE uses to assess central adiposity,'),
    ('<li><strong>Waist circumference:</strong> Men should aim for &lt; 40 inches; women &lt; 35 inches</li>',
     '<li><strong>Waist circumference:</strong> NIH marks higher risk above 40 in (102 cm) for men and 35 in (88 cm) for '
     f'women, at a BMI of 25 to 34.9 ({a("nhlbi", "NHLBI, 1998")})</li>'),
    ('<li><strong>Blood pressure, cholesterol, and blood glucose:</strong> Key metabolic health indicators</li>',
     '<li><strong>Blood pressure and cholesterol:</strong> CDC lists them among the factors to consider with BMI '
     f'({a("cdc_about", "CDC")})</li>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

BLOCKS = [
    ('<h3>Scenario 1: Normal BMI, High Body Fat ("Skinny Fat")</h3>', '<h3>Scenario 3: Similar BMI, Very Different Health</h3>',
     '<h3>Scenario 1: Normal BMI, High Body Fat ("Skinny Fat")</h3> <p>Also called “normal weight obesity”: a BMI in the '
     f'healthy range with a high body fat percentage. BMI does not directly measure body fat ({a("cdc_about", "CDC")}), so it '
     'can’t show this. A body fat estimate can, and a <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> '
     'shows the fat around the waist.</p> '
     '<h3>Scenario 2: High BMI, Low Body Fat (Muscular Individuals)</h3> <p>The opposite: BMI does not distinguish between '
     f'fat, muscle and bone mass ({a("cdc_about", "CDC")}), so very muscular people can reach an overweight or obese BMI with '
     'little body fat. At the NFL Scouting Combine, BMI classed 53.4% of prospective players as obese, against 8.9% by '
     f'measured body fat ({a("prov", "Provencher et al., 2018")}).</p> <p>Our <a href="/blog/bmi-for-athletes/">BMI for '
     'athletes guide</a> covers the research.</p> '),
    ('<p>Two people with identical BMI can have vastly different health profiles based on their body composition:</p>',
     '<div class="chart-compare">',
     '<p>Two men aged 20 to 39 with the same BMI can sit in different body fat ranges:</p> '),
    ('<p style="font-size: 0.875rem; color: var(--gray-500); text-align: center;"><em>Both individuals have the same BMI',
     '</em></p>',
     '<p style="font-size: 0.875rem; color: var(--gray-500); text-align: center;"><em>Both have a BMI of 26, overweight. On the '
     'provisional ranges for men aged 20 to 39, 15% body fat is healthy (8 to 19.9%) and 30% is very high (25% or more) '
     f'({a("gal", "Gallagher et al., 2000")}).'),
]

USING = (
    '<h2 id="using-both">Using Both Metrics Together</h2> <p>When the two disagree, the scenarios above show why. Beside them, '
    'also check:</p> <ul> ')


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:90]}'
    return src.replace(old, new)


def block(src, start, end, new):
    assert src.count(start) == 1, f'block start: {start[:70]}'
    i = src.find(start)
    j = src.find(end, i)
    assert j > i, f'block end: {end[:70]}'
    return src[:i] + new + src[j:]


def page(src):
    for old, new in EDITS:
        src = one(src, old, new, PG)
    for start, end, new in BLOCKS:
        src = block(src, start, end, new)
    src = block(src, '<h2 id="using-both">', '<li><strong>Waist circumference:</strong>', USING)
    for old in ('<li>Free and simple to calculate</li>', '<li>Useful for population-level statistics</li>',
                '<li>Good screening tool for general population</li>', '<li>Correlates with health outcomes at extremes</li>',
                '<li>Widely understood by healthcare providers</li>', '<li>Consistent measurement methodology</li>',
                '<li>May underestimate obesity in elderly (sarcopenia)</li>', '<li>Doesn\'t reflect metabolic health</li>'):
        assert src.count(old) == 1, old
    src = src.replace('<li>May underestimate obesity in elderly (sarcopenia)</li>',
                      '<li>Body fat at the same BMI rises with age</li>')
    src = src.replace('<li>Doesn\'t reflect metabolic health</li>', '<li>Doesn\'t show blood pressure or cholesterol</li>')
    src = src.replace('<li>Free and simple to calculate</li> <li>Useful for population-level statistics</li> <li>Good screening '
                      'tool for general population</li> <li>Correlates with health outcomes at extremes</li> <li>Widely '
                      'understood by healthcare providers</li> <li>Consistent measurement methodology</li>',
                      '<li>Quick and low-cost</li> <li>A reliable screening measure</li> <li>The same categories for every '
                      'adult</li> <li>Death rates rise at both ends of the scale in pooled data</li>')
    for gone in ('30%</div>', 'Higher Risk', 'Often Missed', 'extremely common', 'Widely understood', 'most comprehensive',
                 'most accurate individual', 'generally more informative', 'Men should aim', 'Ideal body composition',
                 'many health professionals', 'Essential fat', 'personalized insights', 'preferably in the morning',
                 'vastly different health', 'most effective approach', 'Comprehensive Approach'):
        assert gone not in src, f'"{gone}" is left'
    return src


def main():
    for rel in (PG, SM):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == PG:
            src = page(src)
        else:
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/body-fat-vs-bmi/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/body-fat-vs-bmi/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
