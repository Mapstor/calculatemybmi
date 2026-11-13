#!/usr/bin/env python3
"""CMB-038 SOURCES-3: batch 4b of the scores run (D-26), the S items on four pages: /blog/bmi-formula/,
/lean-body-mass/, /blog/bmi-tracking-guide/ and /blog/bmi-for-athletes/. Every number the Stage 1 audit could not
trace now traces to a registry row (research/cmb-038/registry.py), or the claim goes (D-10, D-06, D-01).
Every replacement must match exactly once (or the count given), so a page that changed since stops the run.
usage: python3 research/cmb-038/apply.py [--check]   (--check counts the matches and writes nothing)

1. /blog/bmi-formula/: Quetelet 1832 and Keys 1972 as Eknoyan 2008 gives them; Keys et al. 1972 as its abstract
   reports it (7,424 men, 12 cohorts, five countries; the ponderal index poorest, BMI slightly better than
   weight/height); "NIH Adoption (1985)" and the MetLife line become the pre-1998 survey definition and NIH's 1998
   classes (NHLBI 1998, the bmi-categories wording); WHO 1995 and 2000 as the two registry rows hold them; "why
   squared" from Keys and Trefethen instead of "CDC confirms" and "all subsequent studies"; Smart BMI and SBSI cut
   (no primary source); the Broca line fixed (weight / height is not the Broca index); the 703 FAQ says what CDC's
   formula uses instead of "absolutely no impact"; category names as calculator.js prints them; the duplicate steps
   chart and the ponderal formula box go (probe hits).
2. /lean-body-mass/: Boer 1984 (abstract), Hume 1966 (the paper: sample, ages, equations), James 1976 (as Caruso et
   al. 2018 print it) with links; invented lines cut ("proxy for skeletal frame size", "most moderate ... widely
   preferred", "increasingly used in clinical settings"); the sleep line quotes the AASM/SRS statement itself
   (Watson 2015); the nested figure keeps one caption; the measurement section gets its heading back.
3. /blog/bmi-tracking-guide/: daily-swing, clothing, 4-week and day-of-week numbers with no source go; Madigan 2015
   (self-weighing meta-analysis) and Orsama 2014 (weekly weight rhythm) come in; waist method and cut-offs from
   NHLBI 1998, waist-hip ratio from WHO 2008 Table A1; the NHLBI "~5%" list becomes the Wing 2011 sentence the home
   page uses; the plateau causes and fixes (no source; calorie targets, D-06) become NIDDK's Body Weight Planner;
   a Sources list.
4. /blog/bmi-for-athletes/: the college football study named (Lambert 2012) with its comparison group as the
   abstract describes it (260 age- and sex-matched general-population volunteers, not "non-athletes"); the
   skinfold and Bod Pod lines read "below DXA" (Burns 2019 Table 3 is DXA minus method, §4); "Anyone who lifts
   regularly can be in that lean tenth" goes.
5. Dates (§4): schema dateModified, article:modified_time and sitemap lastmod of the four pages.
"""
import datetime
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv


def a(url):
    return f'<a href="{url}" target="_blank" rel="noopener">'


EKNOYAN = a('https://doi.org/10.1093/ndt/gfm517')
KEYS = a('https://doi.org/10.1016/0021-9681(72)90027-6')
NHLBI98 = a('https://www.ncbi.nlm.nih.gov/books/NBK2003/')
WHO854 = a('https://www.who.int/publications/i/item/9241208546')
WHO894 = a('https://iris.who.int/handle/10665/42330')
CDCABOUT = a('https://www.cdc.gov/bmi/about/index.html')
CDCCALC = a('https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html')
TREF = a('https://people.maths.ox.ac.uk/trefethen/bmi.html')
BOER = a('https://doi.org/10.1152/ajprenal.1984.247.4.F632')
HUME = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC473290/')
CARUSO = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC6110034/')
WATSON = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC4434546/')
BURNS = a('https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029')
MADIGAN = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC4546162/')
ORSAMA = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC5644907/')
WING = a('https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/')
WHO2008 = a('https://www.who.int/publications/i/item/9789241501491')
NIDDK = a('https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner')
LI = '<li style="margin-bottom: 0.5rem;">'

FORMULA_CHART = (
    '<!-- Visual Chart: Metric vs Imperial Comparison --> <div class="chart-bar-h" style="margin: 2rem 0;"> <h4 '
    'style="text-align: center; margin-bottom: 1.5rem; color: var(--gray-700);">Formula Complexity Comparison</h4> '
    '<div style="display: flex; flex-direction: column; gap: 1rem;"> <div style="display: flex; align-items: center; '
    'gap: 1rem;"> <span style="min-width: 100px; font-weight: 600; color: var(--gray-700);">Metric</span> <div '
    'style="flex: 1; background: var(--gray-100); border-radius: var(--radius-md); overflow: hidden;"> <div '
    'style="width: 60%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 0.75rem 1rem; color: '
    'white; font-weight: 600;">3 Steps</div> </div> </div> <div style="display: flex; align-items: center; gap: '
    '1rem;"> <span style="min-width: 100px; font-weight: 600; color: var(--gray-700);">Imperial</span> <div '
    'style="flex: 1; background: var(--gray-100); border-radius: var(--radius-md); overflow: hidden;"> <div '
    'style="width: 80%; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); padding: '
    '0.75rem 1rem; color: white; font-weight: 600;">4 Steps (+ conversion)</div> </div> </div> </div> <p '
    'style="text-align: center; font-size: 0.8125rem; color: var(--gray-500); margin-top: 1rem;">Both formulas '
    'produce identical BMI results</p> </div> <div class="table-responsive">')

EDITS = {
    'blog/bmi-formula/index.html': [
        ('<p class="intro-text">The BMI formula is one of the simplest and most widely used health calculations in the '
         'world. Whether you prefer metric or imperial units, this guide walks you through every step of the BMI '
         'calculation, explains where the formula came from, and shows you how to use it correctly with worked '
         'examples.</p>',
         '<p class="intro-text">BMI is your weight divided by the square of your height. This guide works through the '
         'formula step by step in metric and imperial units, explains the 703 in the imperial version, traces the '
         'formula&rsquo;s history and lists the mistakes that most often give a wrong answer.</p>', 1),
        ('<li><strong>BMI was created</strong> by Adolphe Quetelet in the 1830s, named by Ancel Keys in 1972</li>',
         '<li><strong>Its history:</strong> Adolphe Quetelet described the index in 1832, and Ancel Keys named it the '
         f'body mass index in 1972 ({EKNOYAN}Eknoyan, 2008</a>)</li>', 1),
        ('The formula was designed to provide a simple numerical ratio that relates body weight to height, allowing '
         'healthcare professionals to quickly categorize individuals into weight status groups. According to the World '
         'Health Organization (WHO), BMI is a useful population-level measure of overweight and obesity.</p>',
         'The result is one number that relates weight to height. CDC reads adult weight categories from it and notes '
         f'that BMI &ldquo;does not directly measure body fat&rdquo; ({CDCABOUT}CDC</a>).</p>', 1),
        ('<p>The formula that we now call BMI has a rich historical background spanning nearly two centuries:</p> '
         '<h3>Adolphe Quetelet (1830s)</h3>  <p>Quetelet specifically chose height squared (rather than height cubed) '
         'because his empirical data showed that this power provided the best fit. If humans were perfectly '
         'proportional three-dimensional objects, weight would scale with the cube of height. But humans are not '
         'perfectly proportional &mdash; taller people tend to be relatively slimmer, making the square of height a '
         'better predictor.</p>',
         '<p>The formula is older than its name:</p> <h3>Adolphe Quetelet (1832)</h3> <p>The Belgian mathematician, '
         'astronomer and statistician Adolphe Quetelet described the index, weight divided by the square of height, in '
         f'1832. It was known as the Quetelet index until 1972 ({EKNOYAN}Eknoyan, 2008</a>).</p>', 1),
        ('<p>The term &ldquo;Body Mass Index&rdquo; was coined by American physiologist Ancel Keys in a 1972 paper '
         'published in the Journal of Chronic Diseases. Keys compared several body weight indices (including '
         'weight/height, weight/height&sup2;, weight/height&sup3;, and others) across populations in the United States, '
         'Finland, Italy, South Africa, and Japan. He concluded that weight/height&sup2; had the best correlation with '
         'body fat percentage while having the lowest correlation with height &mdash; meaning it measured fatness '
         'rather than tallness.</p>',
         '<p>Ancel Keys and colleagues named it the body mass index in a 1972 paper in the <em>Journal of Chronic '
         'Diseases</em>. They compared weight/height, weight/height&sup2;, the ponderal index (the cube root of weight '
         'divided by height) and percentage of average weight in 7,424 men in 12 cohorts in five countries, asking which '
         'index tracked height least and body fat most, with skinfolds as the fat measure and body density in a smaller '
         'group. The ponderal index did worst, and weight/height&sup2; did slightly better than weight/height. They '
         'preferred it for that, for its simple arithmetic and because, unlike percentage of average weight, it applies '
         f'to any population ({KEYS}Keys et al., 1972</a>).</p>', 1),
        ('<h3>NIH Adoption (1985)</h3> <p>In 1985, the <a href="https://www.nhlbi.nih.gov/calculate-your-bmi" '
         'target="_blank" rel="noopener noreferrer">National Institutes of Health</a> formally adopted BMI as the '
         'standard measure for defining obesity in the United States. Prior to this, ideal weight tables from the '
         'Metropolitan Life Insurance Company were the primary reference for weight assessment. For more context',
         '<h3>US cut-offs (1998)</h3> <p>Before 1998, US surveys counted adults as overweight at a BMI of 27.8 or more '
         'for men and 27.3 or more for women, the 85th percentiles at ages 20 to 29 in NHANES II. NIH&rsquo;s 1998 '
         'guidelines classify overweight as a BMI of 25 to 29.9 and obesity as 30 or more '
         f'({NHLBI98}NHLBI, 1998</a>). For more context', 1),
        ('<h3>WHO Classification (1995&ndash;2000)</h3> <p>The World Health Organization established the current BMI '
         'classification system in 1995, defining underweight (below 18.5), normal weight (18.5&ndash;24.9), overweight '
         '(25&ndash;29.9), and obese (30+). These cutoffs were refined in a 2000 WHO technical report and have remained '
         'the global standard since. Read our',
         '<h3>WHO reports (1995 and 2000)</h3> <p>WHO&rsquo;s 1995 report on anthropometry set three grades of '
         f'thinness: a BMI below 18.5, below 17 and below 16 ({WHO854}WHO, 1995</a>). Its 2000 report on obesity set '
         'out obesity classes I (30 to 34.9), II (35 to 39.9) and III (40 or more) '
         f'({WHO894}WHO, 2000</a>). Read our', 1),
        ('The short answer is that it works best empirically. Research from <a '
         'href="https://www.cdc.gov/bmi/about/index.html" target="_blank" rel="noopener noreferrer">the Centers for '
         'Disease Control and Prevention (CDC)</a> confirms this mathematical relationship. Here is a more detailed '
         'explanation:</p>  <p>However, humans are not perfectly proportional when scaled. Taller people do not simply '
         'grow in all three dimensions equally. They tend to be relatively thinner &mdash; their width and depth do not '
         'increase at the same rate as their height. Quetelet&rsquo;s empirical data, and all subsequent studies, have '
         'confirmed that weight scales approximately with height&sup2;, not height&sup3;, in adult populations. Learn '
         'more',
         'An index of fatness should rise with body fat and stay as flat as possible with height. Keys and colleagues '
         'tested the candidates against both in 1972: weight/height&sup2; met them slightly better than weight/height, '
         f'and the cube-based ponderal index did worst ({KEYS}Keys et al., 1972</a>).</p> <p>Oxford mathematician Nick '
         'Trefethen argues that a power of 2.5 fits the shapes of tall and short '
         f'people better ({TREF}Trefethen</a>); his formula is below. Learn more', 1),
        ('<p>While the standard BMI formula is the most widely used, several variations and alternatives exist. '
         'Research from <a href="https://www.nih.gov/news-events/nih-research-matters/limitations-bmi" target="_blank" '
         'rel="noopener noreferrer">the National Institutes of Health (NIH)</a> has explored various alternatives to '
         'address some of BMI\'s <a href="/blog/bmi-limitations/">known limitations</a>:</p>',
         '<p>Other indices change the power of height, mostly in answer to BMI&rsquo;s '
         '<a href="/blog/bmi-limitations/">known limitations</a>:</p>', 1),
        ('margin-top: 0.5rem;">Better for extremes</p>', 'margin-top: 0.5rem;">Height to the power 2.5</p>', 1),
        ('<h3>The Ponderal Index (PI)</h3> <div style="background: var(--gray-50); border-radius: var(--radius-lg); '
         'padding: 1.25rem; margin: 1rem 0; text-align: center;"> <p style="font-size: 1.125rem; font-weight: 700; '
         'color: var(--gray-700); margin: 0;">PI = weight (kg) &divide; height (m)&sup3;</p> </div> <p>The Ponderal '
         'Index uses height cubed instead of height squared. It is sometimes preferred for very tall and very short '
         'individuals because it better accounts for the non-linear relationship between height and weight at extreme '
         'heights. It has not been widely adopted in clinical practice.</p>',
         '<h3>The Ponderal Index (PI)</h3> <p>The ponderal index uses the cube of height instead of the square: '
         'PI = weight (kg) &divide; height (m)&sup3;. Keys and colleagues tested its cube-root form (the cube root of '
         f'weight divided by height) and found it the poorest of the indices they compared ({KEYS}Keys et al., '
         '1972</a>).</p>', 1),
        ('<h3>SBMI (Smart BMI)</h3> <p>Smart BMI incorporates age and sex into the calculation, producing a result on a '
         '0&ndash;70 scale where 30 represents the statistical median for the population. It was designed to address '
         'the fact that the same BMI value has different health implications at different ages and between sexes. '
         'While theoretically more accurate, it has not replaced standard BMI in clinical practice.</p> <h3>Surface-Based '
         'Body Shape Index (SBSI)</h3> <p>A newer metric that combines body surface area, vertical trunk circumference, '
         'waist circumference, and height. It requires more measurements than BMI but provides a better prediction of '
         'mortality risk. It has shown promise in research settings but is not yet practical for routine clinical '
         'use.</p> ', '', 1),
        (FORMULA_CHART, '<div class="table-responsive">', 1),
        ('If you simply divide weight by height (without squaring), you get the Broca Index, not BMI, and the result will '
         'be far too high.',
         'If you divide weight by height only once, the result is far too high to be a BMI.', 1),
        ('These classifications are based on <a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" '
         'target="_blank" rel="noopener noreferrer">CDC Adult BMI Categories</a>.',
         'These classifications follow <a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" '
         'target="_blank" rel="noopener noreferrer">CDC Adult BMI Categories</a>, with WHO&rsquo;s two lowest thinness '
         'grades below a BMI of 17, as the site&rsquo;s calculators name them.', 1),
        ('<td>Severe Thinness</td>', '<td>Severe thinness</td>', 1),
        ('<td>Moderate Thinness</td>', '<td>Moderate thinness</td>', 1),
        ('<td>Mild Thinness</td>', '<td>Underweight</td>', 1),
        ('<td><strong>Normal Weight</strong></td>', '<td><strong>Healthy weight</strong></td>', 1),
        ('<td>Obese Class I</td>', '<td>Class 1 obesity</td>', 1),
        ('<td>Obese Class II</td>', '<td>Class 2 obesity</td>', 1),
        ('<td>Obese Class III</td>', '<td>Class 3 obesity</td>', 1),
        ('<td>Normal</td>', '<td>Healthy weight</td>', 7),
        ('<td>Obese I</td>', '<td>Class 1 obesity</td>', 1),
        ('<td>16.5</td><td>Underweight</td>', '<td>16.5</td><td>Moderate thinness</td>', 1),
        ('<p>Use these conversions when calculating BMI manually:</p>', '<p>Conversions for working out BMI by '
         'hand:</p>', 1),
        ('<p>The precise conversion factor is 703.0696. It is rounded to 703 for simplicity because the difference is '
         'clinically insignificant &mdash; it changes the BMI result by less than 0.01 points. Since BMI categories span '
         'ranges of 5&ndash;7 points (e.g., normal is 18.5 to 24.9), this tiny rounding error has absolutely no impact '
         'on which category a person falls into.</p>',
         '<p>The precise conversion factor is 703.0696. Rounding it to 703 changes a BMI by less than 0.01, and '
         'CDC&rsquo;s own formula uses 703: weight (lb) &divide; height (in)&sup2; &times; 703 '
         f'({CDCCALC}CDC</a>).</p>', 1),
        ('"The precise conversion factor is 703.0696. It is rounded to 703 for simplicity because the difference is '
         'clinically insignificant — it changes the BMI result by less than 0.01 points. Since BMI categories span '
         'ranges of 5–7 points (e.g., normal is 18.5 to 24.9), this tiny rounding error has absolutely no impact on '
         'which category a person falls into."',
         '"The precise conversion factor is 703.0696. Rounding it to 703 changes a BMI by less than 0.01, and CDC’s own '
         'formula uses 703: weight (lb) ÷ height (in)² × 703 (CDC)."', 1),
    ],
    'lean-body-mass/index.html': [
        ('<figure style="margin:1.25rem 0 0.5rem;"> <figure style="margin:1rem 0;"><svg',
         '<figure style="margin:1.25rem 0 0.5rem;"><svg', 1),
        ('</svg><figcaption style="font-size:0.8125rem;color:var(--gray-500);margin-top:0.25rem;">Identical BMI, '
         'different body composition &#8212; the reason LBM adds information beyond weight and '
         'height.</figcaption></figure> <figcaption', '</svg> <figcaption', 1),
        ('so the same BMI can mean quite different body compositions. <p>Comparing',
         'so the same BMI can mean quite different body compositions.</p> <p>Comparing', 1),
        ('body fat vs. BMI comparison</a>.</p> Individual factors like age, ethnicity, and fitness history all play a '
         'role. For a more personalized assessment, use this calculator alongside our <a href="/">BMI calculator</a> '
         'and <a href="/ideal-weight/">ideal weight calculator</a> to build a complete picture of your health '
         'metrics.</p>',
         'body fat vs. BMI comparison</a>.</p> <p>Use this calculator alongside our <a href="/">BMI calculator</a> and '
         '<a href="/ideal-weight/">ideal weight calculator</a> for a fuller picture.</p>', 1),
        ('This calculator uses the <strong>Boer formula</strong> (published by P. Boer in 1984) to estimate lean body '
         'mass. Boer developed it to normalise body fluid volumes, as the title of his 1984 paper says. Unlike simpler '
         'methods that only consider weight, the Boer formula incorporates both height and weight, providing a more '
         'nuanced estimate that accounts for skeletal frame size.',
         'This calculator uses the <strong>Boer formula</strong>, published by P. Boer in 1984, to estimate lean body '
         'mass from height and weight. Boer used it to normalise body fluid volumes: blood volume, measured in 66 '
         'healthy adults, and extracellular fluid volume, measured in 54, lined up with estimated lean body mass the '
         'same way in men and women, and none of the other indices he tried (weight, height, body surface area, a '
         f'leanness index) did ({BOER}Boer, 1984</a>).', 1),
        ('<h3 style="margin-top:1.5rem;">Why the Boer Formula Uses Both Height and Weight</h3> <p>The inclusion of height '
         'is what separates the Boer formula from naive approaches. Height serves as a proxy for skeletal frame size -- '
         'taller people inherently have more bone mass, larger organs, and more connective tissue, all of which '
         'contribute to lean body mass independent of muscle development. By weighting both inputs, the formula can '
         'distinguish between a tall, light person (who still has significant lean mass from their skeleton) and a '
         'short, heavy person (whose extra weight is more likely to be fat).</p> <p>Notice that the height coefficient '
         'for women (0.473) is substantially larger than for men (0.267), while the weight coefficient for men (0.407) '
         'is higher than for women (0.252). The coefficients differ because the equations were fitted separately for '
         'men and women (correlated with weight), while women\'s lean mass is more strongly predicted by frame size '
         '(correlated with height).</p>',
         '<h3 style="margin-top:1.5rem;">How the Two Boer Equations Differ</h3> <p>Each sex has its own equation. In the '
         'women&rsquo;s, the height coefficient (0.473) is larger than the weight coefficient (0.252); in the '
         'men&rsquo;s, the weight coefficient (0.407) is larger than the height coefficient (0.267).</p>', 1),
        ('the comparison table below shows how much. <a href="/blog/bmi-limitations/">BMI accuracy guide</a>.</p>',
         'the comparison table below shows how much.</p>', 1),
        ('<p>Used in this calculator. Published by P. Boer in 1984 in the American Journal of Physiology. <ul>',
         '<p>Used in this calculator. Published by P. Boer in 1984 in the American Journal of Physiology; the equations '
         f'below are as {CARUSO}Caruso et al. (2018)</a> print them, citing Boer.</p> <ul>', 1),
        ('<p>One of the earliest widely-used LBM formulas, developed by W.P.T. James. It uses a different mathematical '
         'structure with squared terms for height, which can cause it to diverge significantly from other formulas at '
         'extreme heights or weights.</p>',
         '<p>From the 1976 report of the DHSS/MRC Group on Obesity Research (Waterlow and James), as '
         f'{CARUSO}Caruso et al. (2018)</a> print it. It squares the weight-to-height ratio, so at high weights its '
         'estimate rises more slowly, then stops rising and falls.</p>', 1),
        ('<p>Published by R. Hume in 1966 in the Journal of Clinical Pathology. Like Boer&rsquo;s, it is linear in height '
         'and weight, with different coefficients. <ul>',
         f'<p>Published by R. Hume in 1966 in the Journal of Clinical Pathology ({HUME}Hume, 1966</a>). Like '
         'Boer&rsquo;s, it is linear in height and weight, with different coefficients. Hume fitted it to 29 men aged '
         '40 to 77 and 27 women aged 37 to 80, among them patients with polycythaemia, chronic bronchitis or obesity, '
         'with lean body mass worked out from total body water.</p> <ul>', 1),
        ('so the spread is a reminder of how uncertain any single number is, especially for who are carrying excess '
         'fat. The Boer formula tends to produce the most moderate, middle-ground estimates, which is why it is widely '
         'preferred in clinical settings.</p>',
         'so the spread is a reminder of how uncertain any single number is.</p>', 1),
        ('<li>Hume R. Prediction of lean body mass from height and weight. <em>Journal of Clinical Pathology</em>. '
         '1966;19(4):389&ndash;391.</li> <li>James WPT. <em>Research on Obesity: A Report of the DHSS/MRC Group</em>. '
         'London: Her Majesty&rsquo;s Stationery Office; 1976.</li> <li>Boer P. Estimated lean body mass as an index for '
         'normalization of body fluid volumes in humans. <em>American Journal of Physiology &mdash; Renal '
         'Physiology</em>. 1984;247(4):F632&ndash;F636.</li> </ul> <p style="font-size:0.8125rem;color:var(--gray-500);'
         'margin:0.75rem 0 0;">Primary sources for the equations used by this calculator.</p>',
         f'<li>Hume R. {HUME}Prediction of lean body mass from height and weight</a>. <em>Journal of Clinical '
         'Pathology</em>. 1966;19(4):389&ndash;391.</li> <li>DHSS/MRC Group on Obesity Research (Waterlow JC, James '
         'WPT). <em>Research on Obesity</em>. London: Her Majesty&rsquo;s Stationery Office; 1976.</li> <li>Boer P. '
         f'{BOER}Estimated lean body mass as an index for normalization of body fluid volumes in humans</a>. '
         '<em>American Journal of Physiology &mdash; Renal Physiology</em>. 1984;247(4):F632&ndash;F636.</li> '
         f'<li>Caruso D, et al. {CARUSO}Lean body weight-tailored iodinated contrast injection in obese patient: Boer '
         'versus James formula</a>. <em>BioMed Research International</em>. 2018;2018:8521893.</li> </ul> <p '
         'style="font-size:0.8125rem;color:var(--gray-500);margin:0.75rem 0 0;">Hume&rsquo;s equations are from his '
         'paper; the Boer and James equations are as Caruso et al. print them.</p>', 1),
        ('Tracking body composition can show changes that the scale hides.<a href="/blog/bmi-for-athletes/">BMI for '
         'athletes guide</a> explores why traditional metrics fall short for active individuals and what alternatives to '
         'use instead. For a deeper understanding, see our comprehensive lean body mass calculator guide and learn about '
         'the relationship between <a href="/blog/bmi-for-athletes/">muscle mass and BMI</a>.</p>',
         'Tracking body composition can show changes that the scale hides. Our <a href="/blog/bmi-for-athletes/">BMI '
         'for athletes guide</a> explains why BMI falls short for muscular people and what to use instead.</p>', 1),
        ('<!-- Methods to Measure Body Composition --> <section class="content-section"> <p>For most people,',
         '<!-- Methods to Measure Body Composition --> <section class="content-section"> <h2>Methods to Measure Body '
         'Composition</h2> <p>For most people,', 1),
        ('<p>Adults aged 18&ndash;60 should sleep at least 7 hours a night, according to the American Academy of Sleep '
         'Medicine and the Sleep Research Society (<a '
         'href="https://archive.cdc.gov/www_cdc_gov/media/releases/2016/p0215-enough-sleep.html" target="_blank" '
         'rel="noopener">CDC</a>).</p>',
         '<p>The American Academy of Sleep Medicine and the Sleep Research Society recommend that adults aged 18 to 60 '
         f'sleep 7 or more hours a night on a regular basis ({WATSON}Watson et al., 2015</a>).</p>', 1),
        ('LBM helps distinguish between these cases, which is why it is increasingly used in clinical settings alongside '
         'or instead of BMI.', 'LBM helps distinguish between these cases.', 2),
        ('explains how BMI is read at older ages. </div></div>', 'explains how BMI is read at older ages.</p></div></div>',
         1),
        ('-- National Institutes of Health tool using body composition for metabolic prediction</li>',
         '-- NIDDK tool for calorie and physical activity plans to reach a goal weight</li>', 1),
        ('<p>Calculate ideal weight using clinical formulas.</p>', '<p>Ideal weight from four published formulas.</p>', 1),
    ],
    'blog/bmi-tracking-guide/index.html': [
        ('<li><strong>Optimal frequency:</strong> Weekly weigh-ins provide the best balance between useful data and '
         'avoiding obsession</li>',
         '<li><strong>How often:</strong> weight-loss trials found no significant difference between weekly and daily '
         f'weighing ({MADIGAN}Madigan et al., 2015</a>)</li>', 1),
        ('<li><strong>Normal fluctuation:</strong> Daily weight can vary 2&ndash;6 lbs (1&ndash;3 kg) due to water, '
         'food, and other factors</li>',
         '<li><strong>Weekly rhythm:</strong> weight tends to be highest on Sunday and Monday and to fall through the '
         f'week, so compare the same weekday each week ({ORSAMA}Orsama et al., 2014</a>)</li>', 1),
        ('<li><strong>Track trends:</strong> Focus on 4-week moving averages rather than individual measurements</li>',
         '<li><strong>Track trends:</strong> a weekly average says more than any single reading</li>', 1),
        ('<p>Body Mass Index tracking serves several important purposes in your health journey. Regular weight '
         'monitoring is associated with better weight management outcomes. Here is why tracking matters:</p>',
         '<p>In a meta-analysis of weight-loss trials, adding self-weighing and self-regulation steps to a programme led '
         'to 1.7 kg more weight lost across four trials; the one trial of self-weighing on its own found no clear effect '
         f'({MADIGAN}Madigan et al., 2015</a>). Here is what tracking gives you:</p>', 1),
        ('<p>Consistent self-weighing is associated with better weight-loss and weight-maintenance outcomes in cohort '
         'studies. See the <a href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" target="_blank" '
         'rel="noopener">NHLBI overweight and obesity overview</a> for general clinical guidance.</p>',
         '<p>For the clinical side of weight, see the <a href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" '
         'target="_blank" rel="noopener">NHLBI overweight and obesity overview</a>.</p>', 1),
        ('A time-series chart across eight weeks (56 days). Faint scattered dots represent daily weigh-ins showing normal '
         '1-2 kg short-term noise from water, food, and other factors. A bold polyline overlays the weekly rolling mean, '
         'showing a gentle downward trend that the daily noise obscures.',
         'A time-series chart of illustrative data across eight weeks (56 days). Faint dots represent daily weigh-ins '
         'scattered around the trend. A bold polyline overlays the weekly rolling mean, showing a gentle downward trend '
         'that the daily scatter obscures.', 1),
        ('Illustrative. Individual weights swing by 1&ndash;2 kg day-to-day; the weekly average smooths the noise and '
         'reveals the underlying trend.',
         'Illustrative data: daily readings scatter, and the weekly average shows the trend underneath.', 1),
        ('Clothes can add 1&ndash;3 lbs depending on what you are wearing. Underwear only or naked provides the most '
         'accurate comparison.',
         'Different clothes weigh different amounts, so the same outfit (or none) keeps readings comparable.', 1),
        ('<p>If weighing weekly, pick a consistent day. Avoid Mondays (weekend eating can cause temporary spikes) and '
         'Fridays (workweek stress may affect hydration). Wednesday or Thursday often works well.</p>',
         '<p>If you weigh weekly, use the same day each week. In a study of 80 adults who weighed themselves daily, '
         'weight was highest early in the week (Sunday and Monday) and fell during the week, with increases starting '
         f'on Saturday ({ORSAMA}Orsama et al., 2014</a>). Weighing on the same weekday keeps that rhythm out of your '
         'trend.</p>', 1),
        ('<h3>Visualizing Typical Weight Fluctuation Pattern</h3> <p>The following chart illustrates how daily weight can '
         'fluctuate while the overall trend (shown by the weekly average) moves steadily downward during a weight loss '
         'phase:</p>',
         '<h3>An Illustrative Weekly Trend</h3> <p>The illustration below shows weekly averages moving steadily downward '
         'during a weight loss phase, while single days move up and down:</p>', 1),
        ('>Weekly averages show consistent progress despite daily variations of 2&ndash;4 lbs</p>',
         '>Illustrative weekly averages in pounds: the trend keeps falling even when single days jump around</p>', 1),
        ('<td>Tracks central fat, often changes before weight</td>', '<td>Fat around the middle; cut-offs below</td>', 1),
        ('<td>Visual changes often precede scale changes</td>', '<td>A record that doesn&rsquo;t rely on the scale</td>',
         1),
        ('<td>Body recomposition indicator</td>', '<td>Changes in shape</td>', 1),
        ('<td>Overall health indicator</td>', '<td>How you feel alongside the numbers</td>', 1),
        ('<td>Explains predictable fluctuations</td>', '<td>Context for week-to-week changes</td>', 1),
        ('<td>Affects weight through hormones and hunger</td>', '<td>Context for your readings</td>', 1),
        ('<p>Perhaps the most important supplementary measurement. Waist circumference is a better predictor of '
         'cardiovascular risk than BMI for many people because it directly measures dangerous visceral fat.</p>',
         '<p>Waist size adds what BMI can&rsquo;t show. NIH&rsquo;s 1998 guidelines use it alongside BMI because the '
         'waist reflects fat in the abdomen, which they treat as a risk factor in its own right '
         f'({NHLBI98}NHLBI, 1998</a>).</p>', 1),
        (f'{LI}<strong>How to measure:</strong> Use a flexible tape measure around your bare abdomen at the level of your '
         'navel, while standing relaxed (not sucking in)</li>',
         f'{LI}<strong>How to measure:</strong> stand, put the tape around your bare waist just above your hip bones, '
         'and read it just after you breathe out (NHLBI)</li>', 1),
        (f'{LI}<strong>Risk thresholds:</strong> Men &gt; 40 inches (102 cm), Women &gt; 35 inches (88 cm) indicate '
         'elevated health risk</li>',
         f'{LI}<strong>Cut-offs:</strong> more than 40 inches (102 cm) for men and more than 35 inches (88 cm) for women '
         f'mark a higher risk ({NHLBI98}NHLBI, 1998</a>)</li>', 1),
        ('This ratio indicates body fat distribution:</p> <ul style="margin: 1rem 0; padding-left: 1.5rem;"> '
         f'{LI}<strong>Men:</strong> &gt; 0.90 indicates elevated health risk</li> {LI}<strong>Women:</strong> &gt; 0.85 '
         'indicates elevated health risk</li> </ul>',
         'In the report of WHO&rsquo;s 2008 expert consultation, these ratios mark a substantially increased risk of '
         f'metabolic complications ({WHO2008}WHO, 2008</a>):</p> <ul style="margin: 1rem 0; padding-left: 1.5rem;"> '
         f'{LI}<strong>Men:</strong> 0.90 or more</li> {LI}<strong>Women:</strong> 0.85 or more</li> </ul>', 1),
        ('<p>Long-term BMI goals become more achievable when broken into smaller milestones. Here is how to structure your '
         'tracking around meaningful targets:</p>',
         '<p>A long-term BMI goal can be split into smaller steps. Here is one way to set them out:</p>', 1),
        ('<p>Guidance from the <a href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" target="_blank" '
         'rel="noopener">NHLBI</a> notes that clinically meaningful weight loss (commonly cited as ~5% of body weight in '
         'guidelines) is associated with measurable improvements including:</p> <ul style="margin: 1rem 0; '
         f'padding-left: 1.5rem;"> {LI}Lower blood pressure</li> {LI}Better blood-sugar control (including HbA1c in '
         f'people with prediabetes or type 2 diabetes)</li> {LI}Improved lipid profile</li> {LI}Reduced joint pain and '
         f'improved mobility</li> {LI}Better sleep quality, particularly if obstructive sleep apnea is present</li> </ul> '
         '<p>You do not need to reach an &ldquo;ideal&rdquo; BMI to experience meaningful health benefits &mdash; each '
         'incremental step tends to help.</p>',
         '<p>In a large trial of adults with overweight or obesity and type 2 diabetes, losing 5 to 10% of body weight '
         'was linked to better blood sugar, blood pressure, HDL cholesterol and triglycerides after one year '
         f'({WING}Wing et al., 2011</a>).</p>', 1),
    ],
    'blog/bmi-for-athletes/index.html': [
        ('<span>body fat at BMI 30 in college football players (27.3% in non-athletes)</span>',
         '<span>body fat at BMI 30 in college football players (27.3% in matched volunteers)</span>', 1),
        ('<p><strong>College football.</strong> A DXA study of 156 Division I-A football players and matched '
         'non-athletes asked what body fat each BMI cut-off corresponds to. In the players, a BMI of 25 matched about '
         '11.1% body fat and a BMI of 30 about 20.2%; in the non-athletes, the same cut-offs matched 19.9% and 27.3%.',
         '<p><strong>College football.</strong> Lambert and colleagues scanned 156 Division I-A football players and '
         '260 age- and sex-matched volunteers from the general population with DXA and asked what body fat each BMI '
         'cut-off corresponds to. In the players, a BMI of 25 corresponded to about 11.1% body fat and a BMI of 30 to '
         'about 20.2%; in the volunteers, the same cut-offs corresponded to 19.9% and 27.3%.', 1),
        ('college football players versus non-athletes"', 'college football players versus matched volunteers"', 1),
        ('class="at-l">Non-athletes</text>', 'class="at-l">Matched volunteers</text>', 2),
        ('college football players vs matched non-athletes (DXA). Source: <a href="https://pubmed.ncbi.nlm.nih.gov/'
         '22805182/" rel="noopener">Clin J Sport Med',
         'college football players vs matched volunteers from the general population (DXA). Source: <a '
         'href="https://pubmed.ncbi.nlm.nih.gov/22805182/" rel="noopener">Lambert et al., Clin J Sport Med', 1),
        ('(our calculation from NHANES 2011&ndash;2018). Anyone who lifts regularly can be in that lean tenth. The',
         '(our calculation from NHANES 2011&ndash;2018). The', 1),
        ('In a study that tested seven methods against DXA, skinfold calipers came within 1.4 points on average, and lab '
         'methods such as the Bod Pod within 1.6 (<a href="/blog/how-to-measure-body-fat/">how to measure body '
         'fat</a>).',
         'In a study that tested seven methods against DXA in 437 college students, skinfold calipers read 1.4 points '
         f'below DXA on average and the Bod Pod 1.6 points below ({BURNS}Burns et al., 2019</a>; more in <a '
         'href="/blog/how-to-measure-body-fat/">how to measure body fat</a>).', 1),
        ('<li><a href="https://pubmed.ncbi.nlm.nih.gov/22805182/" rel="noopener">DEXA or BMI',
         '<li>Lambert BS, Oliver JM, Katts GR, Green JS, Martin SE, Crouse SF. <a '
         'href="https://pubmed.ncbi.nlm.nih.gov/22805182/" rel="noopener">DEXA or BMI', 1),
        ('<li>Centers for Disease Control and Prevention. <a href="https://www.cdc.gov/bmi/adult-calculator/'
         'bmi-categories.html" rel="noopener">Adult BMI Categories</a>.</li>',
         f'<li>Burns, Fu and Constantino. {BURNS}Measurement agreement in percent body fat estimates among laboratory and '
         'field assessments in college students: use of equivalence testing</a>. PLOS ONE 2019;14(3):e0214029.</li>\n'
         '<li>Centers for Disease Control and Prevention. <a href="https://www.cdc.gov/bmi/adult-calculator/'
         'bmi-categories.html" rel="noopener">Adult BMI Categories</a>.</li>', 1),
    ],
}

# Spans cut whole: (page, start marker, end marker (kept out of the cut), replacement)
SPANS = [
    ('blog/bmi-tracking-guide/index.html', '<h2>What to Do When Progress Stalls</h2>',
     '<p>For more on reading your numbers, see these guides:</p>',
     '<h2>What to Do When Progress Stalls</h2> <p>If your weekly average stops falling, a plan built from your current '
     f'weight is the place to start. NIH&rsquo;s {NIDDK}Body Weight Planner</a> lets you make &ldquo;personalized '
     'calorie and physical activity plans to reach a goal weight within a specific time period&rdquo; (NIDDK); it is '
     'for adults 18 and older and not for pregnant or breastfeeding women.</p> '),
]

TRACKING_SOURCES = (
    '<h2>Sources</h2> <ul style="margin: 1rem 0; padding-left: 1.5rem;"> '
    f'{LI}Madigan CD, Daley AJ, Lewis AL, Aveyard P, Jolly K. {MADIGAN}Is self-weighing an effective tool for weight '
    'loss: a systematic literature review and meta-analysis</a>. Int J Behav Nutr Phys Act 2015;12:104.</li> '
    f'{LI}Orsama AL, Mattila E, Ermes M, van Gils M, Wansink B, Korhonen I. {ORSAMA}Weight rhythms: weight increases '
    'during weekends and decreases during weekdays</a>. Obes Facts 2014;7(1):36&ndash;47.</li> '
    f'{LI}NHLBI. {NHLBI98}Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity '
    'in Adults</a> (NIH, 1998): the waist cut-offs and how to measure.</li> '
    f'{LI}WHO. {WHO2008}Waist circumference and waist&ndash;hip ratio: report of a WHO expert consultation</a> (Geneva, '
    '2008; published 2011), Table A1.</li> '
    f'{LI}Wing RR, et al. {WING}Benefits of modest weight loss in improving cardiovascular risk factors in overweight '
    'and obese individuals with type 2 diabetes</a>. Diabetes Care 2011;34:1481&ndash;6.</li> '
    f'{LI}NIDDK. {NIDDK}Body Weight Planner</a>.</li> </ul> ')
TRACKING_CTA = '<p style="text-align: center; margin: 2.5rem 0;"><a href="/" class="cta-button">Calculate My BMI Now'


def rx(literal):
    """The literal with every run of spaces matching any whitespace (the pages wrap lines in places)."""
    return re.compile(r'\s+'.join(re.escape(part) for part in literal.split(' ')))


def set_dates(t):
    t = re.sub(r'("dateModified": ?")\d{4}-\d{2}-\d{2}(")', rf'\g<1>{TODAY}\g<2>', t)
    return re.sub(r'(article:modified_time" content=")\d{4}-\d{2}-\d{2}', rf'\g<1>{TODAY}', t)


def main():
    bad = 0
    out = {}
    for rel, edits in EDITS.items():
        t = (REPO / rel).read_text(encoding='utf-8')
        for old, new, want in edits:
            pat = rx(old)
            got = len(pat.findall(t))
            if got != want:
                bad += 1
                print('MISMATCH', rel, got, want, '|', old[:100])
                continue
            t = pat.sub(lambda m: new, t)
        out[rel] = t
    for rel, start, end, new in SPANS:
        t = out[rel]
        i, j = t.find(start), t.find(end)
        if t.count(start) != 1 or t.count(end) != 1 or j < i:
            bad += 1
            print('SPAN MISMATCH', rel, start[:60])
            continue
        out[rel] = t[:i] + new + t[j:]
    t = out['blog/bmi-tracking-guide/index.html']
    if t.count(TRACKING_CTA) != 1:
        bad += 1
        print('MISMATCH tracking CTA')
    else:
        out['blog/bmi-tracking-guide/index.html'] = t.replace(TRACKING_CTA, TRACKING_SOURCES + TRACKING_CTA)
    if CHECK or bad:
        print('check done' if not bad else f'{bad} mismatches: nothing written')
        return 1 if bad else 0
    for rel, t in out.items():
        (REPO / rel).write_text(set_dates(t), encoding='utf-8')
        print('edited', rel)
    sm = REPO / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    for rel in EDITS:
        loc = 'https://calculatemybmi.net/' + rel[:-len('index.html')]
        s, n = re.subn(rf'(<loc>{re.escape(loc)}</loc>\s*<lastmod>)\d{{4}}-\d{{2}}-\d{{2}}', rf'\g<1>{TODAY}', s)
        assert n == 1, (loc, n)
    sm.write_text(s, encoding='utf-8')
    print('sitemap lastmod', TODAY, 'for', len(EDITS), 'pages')
    return 0


if __name__ == '__main__':
    sys.exit(main())
