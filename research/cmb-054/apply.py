#!/usr/bin/env python3
"""CMB-054 CLAIMS-7: claims pass batch 7 (DEVLOG §5 P1) on /blog/bmi-categories/ (13 probe hits).
Each category now says what WHO, CDC, NCHS and the pooled studies say about it (D-10); doctor lines are the sources' own
"when" (§4); no targets of our own (D-06) and no treatment (D-01). Out: "a condition associated with significant medical
risk", catabolizing organs, "often indicates an eating disorder", "Immediate medical evaluation is essential", "needs
prompt medical evaluation", "Medical consultation is recommended to identify and treat", "the most common form of
underweight", ectomorph genetics, the unsourced causes list, "the lowest overall health risk ... as noted by NHLBI" (its
link was NHLBI's calculator page), the "7-point span" (6.5 points), "a transitional zone", the NHLBI risk list the
registry does not hold (high cholesterol, gallbladder disease, some cancers), "the most debated", "the entry point into
clinical obesity", "substantially elevated health risk across virtually all organ systems", "the greatest reduction in
quality of life and life expectancy", "Prevalence has risen substantially", "Several countries have since set lower
cut-offs" (unsourced), "The WHO recommended unified cutoffs of 25 and 30" in 1995 (the 1995 report graded thinness; NIH
set 25 and 30 in 1998), "aligned U.S. guidelines with the WHO cut-offs", "a continuous risk curve" (twice), the
borderline advice (energy, menstrual regularity, "Trends over months", "clinical significance ... screening cadence",
"Any downstream decisions belong with a clinician"), "skinny fat", "Arbitrary boundaries", the "Focus on Direction" tip,
"Talk to Your Doctor", metabolically healthy overweight, "lifestyle interventions alone are usually sufficient", "Most
elite athletes in strength and power sports", "prioritizing protein and fiber", "strength training to preserve muscle",
"Individual factors ... matter more", and the WHO fact sheet and NHLBI overview in the sources list (no claim used them).
In: GBMC 2016 band by band, Flegal 2013's grade 1 result next to it, NCI's risk list, NCHS on underweight causes, body fat
at a given BMI and the 1960-2023 trend, MedlinePlus's and NIMH's "when", NICE's lower thresholds, NIH's waist cut-offs,
CDC's provider line and its weight-loss summary, the activity guidelines. The figure's title, description and caption
said the bands were drawn to scale; they are not, and now say so. Title, H1, URL and meta descriptions kept (D-28).
FAQPage JSON-LD rebuilt from the eight visible answers; dateModified and lastmod follow.
usage: python3 research/cmb-054/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
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
PG, SM = 'blog/bmi-categories/index.html', 'sitemap.xml'
BASE = {PG: '4d41d2227ed1169e3aeefb5eb0bcd595243af3292d28e4635db3cd5dfd0e1733',
        SM: '4ed35d846a192be71f2e8ab77b9bbf60a65e9a88bb72553aff5ae6cfef1267c2'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'who1995': 'https://www.who.int/publications/i/item/9241208546',
    'who2000': 'https://pubmed.ncbi.nlm.nih.gov/11234459/',
    'who2004': 'https://pubmed.ncbi.nlm.nih.gov/14726171/',
    'cdc_cats': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'flegal': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'hestat': 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm',
    'nchs508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'nchs_uw': 'https://www.cdc.gov/nchs/data/hestat/hestat119.htm',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
    'medline': 'https://medlineplus.gov/ency/article/003107.htm',
    'nimh': 'https://www.nimh.nih.gov/health/publications/eating-disorders',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'odphp': 'https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/top-10-things-know',
    'wing': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
    'provencher': 'https://doi.org/10.1519/JSC.0000000000002449',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


L = {  # the inline citations, as the page already writes them
    'who1995': a('who1995', 'WHO, 1995'), 'who2000': a('who2000', 'WHO, 2000'),
    'who2004': a('who2004', 'WHO expert consultation, 2004'), 'cdc_cats': a('cdc_cats', 'CDC'),
    'cdc_about': a('cdc_about', 'CDC'), 'cdc_child': a('cdc_child', 'CDC'), 'cdc_lw': a('cdc_lw', 'CDC'),
    'nhlbi': a('nhlbi', 'NHLBI'), 'gbmc': a('gbmc', 'GBMC, 2016'), 'flegal': a('flegal', 'Flegal et al., JAMA 2013'),
    'winter': a('winter', 'Winter 2014 meta-analysis'), 'hestat': a('hestat', 'NCHS'),
    'nchs_uw': a('nchs_uw', 'NCHS'), 'nci': a('nci', 'NCI'), 'medline': a('medline', 'MedlinePlus'),
    'nimh': a('nimh', 'NIMH'), 'nice': a('nice', 'NICE guideline NG246'), 'odphp': a('odphp', 'HHS'),
    'wing': a('wing', 'Wing et al., 2011'), 'provencher': a('provencher', 'Provencher et al., 2018'),
}
UL = '<ul style="margin: 1rem 0; padding-left: 1.5rem;">'
LI5, LI75 = '<li style="margin-bottom: 0.5rem;">', '<li style="margin-bottom: 0.75rem;">'
CDC_FACTORS = ('for individuals, CDC says BMI should be considered with other factors, such as blood pressure, cholesterol '
               'levels and a physical examination ({cdc_about})').format(**L)
NICE_LINE = ('In the UK, NICE uses lower thresholds for adults with a South Asian, Chinese, other Asian, Middle Eastern, '
             'Black African or African-Caribbean background: overweight from 23 to 27.4 and obesity from 27.5 ({nice}).'
             ).format(**L)

EDITS = [
    ('<p class="intro-text">The World Health Organization divides BMI into eight categories, from severe thinness to class '
     'III obesity. Each category carries different health implications, and understanding where you fall &mdash; and what '
     'it actually means &mdash; is the first step toward making informed decisions about your health. This guide explains '
     'every BMI category in detail, including the health risks, weight ranges, and important limitations.</p>',
     '<p class="intro-text">The World Health Organization divides adult BMI into eight categories, from severe thinness to '
     'class III obesity. Below: each category&rsquo;s range, what large studies tie to it, healthy weights by height, and '
     'where the categories fall short.</p>'),
    ('<li><strong>Health risk increases</strong> at both extremes &mdash; being significantly underweight is also '
     'dangerous</li>',
     '<li><strong>Risk at both ends:</strong> in pooled data from 239 studies, the risk of death was lowest at a BMI of 20.0 '
     'to 24.9 and higher below and above it ({gbmc})</li>'.format(**L)),
    ('<li><strong>BMI is a screening tool,</strong> not a diagnosis &mdash; your category is a starting point, not a '
     'verdict</li>',
     '<li><strong>A screening measure, not a diagnosis:</strong> for individuals, CDC says BMI should be read with other '
     'factors, such as blood pressure and cholesterol ({cdc_about})</li>'.format(**L)),
    ('<p>The World Health Organization set out the current classification in a <a '
     'href="https://www.who.int/publications/i/item/9241208546" target="_blank" rel="noopener">1995 expert report</a> and '
     'added the obesity classes in a <a href="https://pubmed.ncbi.nlm.nih.gov/11234459/" target="_blank" rel="noopener">2000 '
     'technical report</a>; the <a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" target="_blank" '
     'rel="noopener">CDC</a> uses the same cut-offs for adults aged 20 and older:',
     '<p>The World Health Organization graded adult thinness in a <a href="https://www.who.int/publications/i/item/9241208546" '
     'target="_blank" rel="noopener">1995 expert report</a> and set out the obesity classes in a <a '
     'href="https://pubmed.ncbi.nlm.nih.gov/11234459/" target="_blank" rel="noopener">2000 technical report</a>; <a '
     'href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" target="_blank" rel="noopener">CDC</a> uses the '
     'same cut-offs from 18.5 up for adults aged 20 and older, with a single underweight category below 18.5:'),
    ('<p>Note that children and teens (ages 2&ndash;19) use a completely different system based on age- and sex-specific '
     'percentiles, not these fixed cutoffs. See our <a href="/kids-bmi-calculator/">Pediatric BMI Calculator</a> guide for '
     'children&rsquo;s BMI categories.</p>',
     '<p>Children and teens aged 2 through 19 are classed differently: because they are growing, CDC compares their BMI with '
     'others of the same sex and age, as BMI-for-age percentiles ({cdc_child}). See our <a '
     'href="/kids-bmi-calculator/">Pediatric BMI Calculator</a> for the child and teen categories.</p>'.format(**L)),
    # the figure: its text said the bands were drawn to scale
    ('role="img" aria-labelledby="svg-cat-title svg-cat-desc" role="img" aria-label="BMI category scale with WHO '
     'cut-offs"><title>BMI category scale with WHO cut-offs</title> <title id="svg-cat-title">Vertical WHO BMI band scale with '
     'heights proportional to BMI-unit width</title> <desc id="svg-cat-desc">A vertical column showing the WHO adult BMI '
     'categories stacked from severe thinness at the top to obese class III at the bottom. Each band\'s height is '
     'proportional to its BMI-unit width, making the narrow normal-weight band visually distinct from the wider overweight '
     'and obese classes. Numeric ranges match the WHO classification table above.</desc>',
     'role="img" aria-labelledby="svg-cat-title svg-cat-desc"><title id="svg-cat-title">The eight WHO adult BMI categories, '
     'stacked</title> <desc id="svg-cat-desc">A vertical column of the eight WHO adult BMI categories, from severe thinness '
     '(below 16.0) at the top to obese class III (40.0 and above) at the bottom, each labelled with its BMI range. Band '
     'heights are for legibility, not to scale.</desc>'),
    ('<text x="150" y="140" font-size="10">(WHO healthy range)</text>',
     '<text x="150" y="140" font-size="10">(normal range)</text>'),
    ('Band heights are drawn proportional to each category\'s BMI-unit width. The narrow ~6-unit "normal" band sits between '
     'two much wider adjacent regions.</figcaption>',
     'The eight WHO adult categories, from severe thinness to obese class III. Band heights are for legibility, not to '
     'scale.</figcaption>'),
    # Category 4
    ('<p>The normal weight category represents the BMI range associated with the lowest overall health risk for most adults, '
     'as noted by the <a href="https://www.nhlbi.nih.gov/calculate-your-bmi" target="_blank" rel="noopener">National Heart, '
     'Lung, and Blood Institute (NHLBI)</a>. This is a wide range &mdash; a 7-point span that encompasses a substantial '
     'weight difference at any given height.',
     '<p>CDC calls a BMI from 18.5 to just under 25 healthy weight ({cdc_cats}). That is a span of about 6.5 BMI points, a '
     'sizeable weight difference at any height.'.format(**L)),
    (' Both ends of this range are considered healthy. For more on target ranges, see our Healthy BMI Range guide.', ''),
    ('<p>The whole 18.5&ndash;24.9 range counts as healthy weight, for men and women alike.',
     '<p>CDC draws no line inside the range ({cdc_cats}). In the same pooled data from 239 studies, the lowest risk of death '
     'sat at a BMI of 20.0 to 24.9; at 18.5 to 19.9 it was a little higher (hazard ratio 1.13 against 22.5 to 24.9; '
     '{gbmc}).'.format(**L)),
    # Category 5
    ('The WHO uses the term &ldquo;pre-obese&rdquo; for this range, indicating it is a transitional zone between normal weight '
     'and obesity.',
     'WHO&rsquo;s name for it is pre-obese ({who2000}).'.format(**L)),
    ('<p>The US clinical guidelines on overweight and obesity link excess weight with higher risk of high blood pressure, '
     'high cholesterol, type 2 diabetes, coronary heart disease, stroke, gallbladder disease, osteoarthritis, sleep apnea and '
     'some cancers, with risk rising as BMI rises (<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" '
     'rel="noopener">NHLBI</a>).</p>',
     '<p>NCI says that, compared with people at a healthy weight, those with overweight or obesity are at greater risk for '
     'many diseases, including diabetes, high blood pressure, cardiovascular disease, stroke and at least 13 types of cancer '
     '({nci}).</p>'.format(**L)),
    ('<p>The overweight category is the most debated. In a pooled analysis of 97 studies, all-cause mortality in the '
     'overweight range was slightly lower than in the healthy range (hazard ratio 0.94; <a '
     'href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/" target="_blank" rel="noopener">Flegal et al., JAMA 2013</a>); '
     'why is still argued over, and it is not a reason to aim for a higher BMI.</p>',
     '<p>Two large pooled analyses disagree about this range. In one, of 97 studies, all-cause mortality in the overweight '
     'range was slightly lower than in the healthy range (hazard ratio 0.94; {flegal}). In the other, of 239 studies, whose '
     'main results kept to never-smokers without known disease and left out the first five years of follow-up, the risk was '
     'higher: hazard ratios 1.07 at a BMI of 25.0 to 27.4 and 1.20 at 27.5 to 29.9, against 22.5 to 24.9 ({gbmc}).</p>'
     .format(**L)),
    # Categories 6 to 8
    ('<p style="margin:0;font-size:0.9375rem;color:#78350f;">The obesity-class sections below describe the WHO classification '
     'and the health-risk <em>associations</em> reported at each class. They are not personalised medical advice, and this '
     'site does not cover treatment options, medication choices, or surgical decisions &mdash; those belong with a qualified '
     'clinician.</p>',
     '<p style="margin:0;font-size:0.9375rem;color:#78350f;">The obesity-class sections below give the WHO classification '
     'and the risks reported at each class. They are not personal medical advice, and this site does not cover treatment: '
     'medicines, surgery or other care.</p>'),
    ('<p>Class I obesity is the entry point into clinical obesity. At this level, health-risk associations with excess '
     'weight become substantially more consistent across populations.  For the health-risk discussion see our',
     '<p>WHO calls a BMI of 30.0 to 34.9 obese class I; CDC calls it class 1 obesity ({cdc_cats}). In the 239-study data, the '
     'risk of death at 30.0 to 34.9 was higher than at 22.5 to 24.9 (hazard ratio 1.45; {gbmc}); the 2013 '
     'analysis of 97 studies found no clear difference at this grade (hazard ratio 0.95; {flegal}). For the health-risk '
     'discussion see our'.format(**L)),
    ('<p>The same NHLBI list applies, at higher risk than in the overweight range (<a '
     'href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">NHLBI</a>). Obesity is also linked to '
     'at least 13 types of cancer (see our <a href="/blog/bmi-and-health-risks/">BMI and health risks</a> page for the list '
     'and sources).</p> ', ''),
    ('<p>Class II obesity carries substantially elevated health risk across virtually all organ systems. At this level, '
     'obesity often coexists with multiple other conditions (comorbidities), creating a compounding effect on health.</p>',
     '<p>WHO calls a BMI of 35.0 to 39.9 obese class II; CDC calls it class 2 obesity ({cdc_cats}). The risk of death at 35.0 '
     'to 39.9 was higher again (hazard ratio 1.94 against 22.5 to 24.9; {gbmc}).</p>'
     .format(**L)),
    ('<p>Class III obesity, sometimes called severe or morbid obesity, represents the highest-risk BMI category, with the '
     'most significant health consequences and the greatest reduction in quality of life and life expectancy.</p>',
     '<p>WHO calls a BMI of 40.0 or more obese class III; CDC calls it class 3 obesity, NCHS reports it as severe obesity, '
     'and it is sometimes called morbid obesity. In US adults in 2021&ndash;2023, 9.7% had severe obesity (age-adjusted; '
     '{hestat}). At a BMI of 40.0 to 59.9, the risk of death was the highest of any band in the 239-study data (hazard '
     'ratio 2.76 against 22.5 to 24.9; {gbmc}).</p>'.format(**L)),
    # prevalence and the Asian action points
    ('<p>Adults with obesity (BMI &ge; 30) together with those in the overweight range account for the majority of the U.S. '
     'Adult population. Prevalence has risen substantially across recent decades.</p>',
     '<p>Together, overweight and obesity cover most US adults: 31.7% and 40.3% in 2021&ndash;2023 (age-adjusted). Among '
     'adults aged 20 to 74, obesity rose from 13.4% in 1960&ndash;1962 to 40.8% in 2021&ndash;2023 ({hestat}).</p>'
     .format(**L)),
    (' Several countries have since set lower cut-offs of their own.</p>', ' ' + NICE_LINE + '</p>'),
    # history
    ('<li style="margin-bottom: 0.75rem;"><strong>1995:</strong> The WHO recommended unified cutoffs of 25 (overweight) and '
     '30 (obesity) regardless of sex.</li>',
     LI75 + '<strong>1995:</strong> WHO graded adult thinness by BMI: below 18.5, below 17 and below 16 ({who1995}).</li>'
     .format(**L)),
    ('<strong>1998:</strong> The NIH aligned U.S. guidelines with the WHO cut-offs. Nobody&rsquo;s weight changed,',
     '<strong>1998:</strong> NIH&rsquo;s clinical guidelines set overweight at a BMI of 25 to 29.9 and obesity at 30 or '
     'more. Nobody&rsquo;s weight changed,'),
    ('<strong>2000:</strong> The WHO published <a href="https://pubmed.ncbi.nlm.nih.gov/11234459/" target="_blank" '
     'rel="noopener">Technical Report 894</a>, which set out obesity classes I, II and III; the thinness grades come from its '
     'earlier report on anthropometry.</li>',
     '<strong>2000:</strong> WHO&rsquo;s report on obesity (<a href="https://pubmed.ncbi.nlm.nih.gov/11234459/" '
     'target="_blank" rel="noopener">Technical Report 894</a>) set out obesity classes I, II and III and concluded that a '
     'coherent system based on BMI should be adopted internationally.</li>'),
]

# whole stretches, start marker included, end marker (the next heading) left in place
BLOCKS = [
    ('<h2>Category 1: Severe Thinness / Grade 3 Underweight (BMI Below 16.0)</h2>',
     '<h2>Category 4: Normal Weight (BMI 18.5&ndash;24.9)</h2>',
     ('<h2>Category 1: Severe Thinness / Grade 3 Underweight (BMI Below 16.0)</h2> <p>WHO calls a BMI below 16.0 severe '
      'thinness: grade 3, the lowest of its three underweight grades ({who1995}). Our <a '
      'href="/blog/underweight-bmi-risks/">underweight BMI risks</a> guide covers the risks and causes in detail.</p> '
      '<p>NIMH lists extreme thinness among the signs of anorexia nervosa, and says people with any combination of its signs '
      'should talk to a health care provider ({nimh}).</p> '
      '<h2>Category 2: Moderate Thinness / Grade 2 Underweight (BMI 16.0&ndash;16.9)</h2> <p>WHO calls a BMI of 16.0 to 16.9 '
      'moderate thinness, grade 2 ({who1995}).</p> '
      '<h2>Category 3: Mild Thinness / Grade 1 Underweight (BMI 17.0&ndash;18.4)</h2> <p>WHO calls a BMI of 17.0 to 18.4 '
      'mild thinness, grade 1 ({who1995}). CDC does not split the grades: it puts every BMI below 18.5 in one category, '
      'underweight ({cdc_cats}).</p> '
      '<h3 id="why-underweight">Why Some Adults Are Underweight</h3> <p>CDC&rsquo;s survey team names two broad causes: '
      '&ldquo;Poor nutrition and underlying health conditions can result in underweight among youth and adults&rdquo; '
      '({nchs_uw}). For weight lost without trying, MedlinePlus lists a wider set, from depression and long-term infections '
      'to problems absorbing food, such as celiac disease ({medline}).</p> <p>Risk data come in wider bands than WHO&rsquo;s '
      'grades: in pooled data from 239 studies, the risk of death at a BMI of 15.0 to 18.4 was higher than at 22.5 to 24.9 '
      '(hazard ratio 1.51; {gbmc}).</p> <p>MedlinePlus advises seeing a provider if you lose more than 10 pounds (4.5 kg), or '
      '5% of your usual weight, within 6 to 12 months without knowing why ({medline}). If you have concerns about your '
      'eating behavior or mental health, NIMH says to talk to a primary care provider ({nimh}).</p> ').format(**L)),
    ('<p>These cut-offs have since been the reference point in a large body of BMI/mortality research,',
     '<h2>Category Borderlines and What They Mean</h2>',
     ('<p>Risk does not jump at either cut-off: in the 239-study data, the risk of death rose band by band through 25 and 30 '
      '({gbmc}). Learn more about the formula behind these numbers in our <a href="/blog/bmi-formula/">BMI '
      'Formula</a> guide.</p> ').format(**L)),
    ('<p>Many readers find themselves sitting near the boundary between two categories.',
     '<h2>Limitations of BMI Categories</h2>',
     ('<p>Near a boundary, a small change in weight can move you into the next category. What each boundary means:</p> '
      '<h3>BMI 18&ndash;19: near the underweight / normal boundary</h3> ' + UL + ' ' + LI5 + 'Just below 18.5 is CDC&rsquo;s '
      'underweight and WHO&rsquo;s mild thinness; from 18.5 it is CDC&rsquo;s healthy weight and WHO&rsquo;s normal range '
      '({who1995}; {cdc_cats}).</li> ' + LI5 + 'Losing weight without trying: MedlinePlus&rsquo;s rule on when to get '
      'checked is under <a href="#why-underweight">Why Some Adults Are Underweight</a>.</li> </ul> '
      '<h3>BMI 24&ndash;26: near the normal / overweight boundary</h3> ' + UL + ' ' + LI5 + '25.0 is where CDC&rsquo;s '
      'overweight category and WHO&rsquo;s pre-obese range start ({cdc_cats}; {who2000}).</li> ' + LI5 + 'From a BMI of 25, '
      'NIH guidelines add a waist measurement (see <a href="#measure-waist">Measure Your Waist</a> below).</li> </ul> '
      '<h3>BMI 29&ndash;31: near the overweight / obese boundary</h3> ' + UL + ' ' + LI5 + '30.0 is where class 1 obesity '
      'starts for CDC and obese class I for WHO ({cdc_cats}; {who2000}).</li> ' + LI5 + 'In a large trial of adults with '
      'overweight or obesity and type 2 diabetes, losing 5&ndash;10% of body weight was linked to improvements in blood '
      'sugar, blood pressure and cholesterol within a year ({wing}).</li> </ul> ').format(**L)),
    ('<p>While BMI categories are a useful population-level screening tool,',
     '<h2>Tips for Understanding Your BMI Category</h2>',
     ('<p>CDC calls BMI &ldquo;a quick, low-cost, and reliable screening measure,&rdquo; but notes that it does not directly '
      'measure body fat ({cdc_about}). For more, see our <a href="/blog/bmi-limitations/">BMI limitations</a> guide.</p> ' + UL
      + ' ' + LI75 + '<strong>Fat, muscle and bone:</strong> CDC notes that BMI does not distinguish between them '
      '({cdc_about}). The <a href="/lean-body-mass/">lean body mass calculator</a> estimates the part of your weight that '
      'isn&rsquo;t fat.</li> ' + LI75 + '<strong>Where fat sits:</strong> NIH guidelines call excess abdominal fat &ldquo;an '
      'important, independent risk factor for disease&rdquo; and pair BMI with a waist measurement ({nhlbi}).</li> ' + LI75 +
      '<strong>One set of cut-offs:</strong> CDC applies the adult categories to everyone 20 and older regardless of age, sex '
      'or race ({cdc_cats}), yet NCHS notes that at a given BMI, body fat may vary by sex, age, and race and Hispanic origin '
      '({hestat}).</li> ' + LI75 + '<strong>Ethnicity:</strong> NCHS notes that health risks may begin at a lower BMI '
      'among Asian people, and that BMI may overestimate body fat among Black people at a given BMI compared with others '
      '({hestat}).</li> </ul> ').format(**L)),
    ('<h2>Tips for Understanding Your BMI Category</h2>',
     '<h2>Frequently Asked Questions</h2>',
     ('<h2>Tips for Understanding Your BMI Category</h2> <div class="tips-grid"> '
      '<div class="tip-item"> <div class="tip-icon">1</div> <div class="tip-content"> <h3>Look Beyond the Label</h3> <p>A '
      'category is a screening result, not a diagnosis: ' + CDC_FACTORS + '.</p> </div> </div> '
      '<div class="tip-item"> <div class="tip-icon">2</div> <div class="tip-content"> <h3 id="measure-waist">Measure Your '
      'Waist</h3> <p>NIH guidelines pair BMI with a waist measurement: more than 40 inches (102 cm) for men or 35 inches (88 '
      'cm) for women marks higher risk, at a BMI of 25 to 34.9 ({nhlbi}).</p> </div> </div> '
      '<div class="tip-item"> <div class="tip-icon">3</div> <div class="tip-content"> <h3>Account for Age and Sex</h3> '
      '<p>The adult categories don&rsquo;t change with age or sex, but our <a href="/blog/bmi-by-age/">BMI by age guide</a> '
      'and the calculators for <a href="/women-bmi-calculator/">women</a> and <a href="/men-bmi-calculator/">men</a> show how '
      'a result compares with US adults of the same age or sex.</p> </div> </div> '
      '<div class="tip-item"> <div class="tip-icon">4</div> <div class="tip-content"> <h3>If Your Weight Concerns You</h3> '
      '<p>If you&rsquo;re concerned about your weight or have questions about your medications, CDC says to talk with your '
      'health care provider ({cdc_lw}).</p> </div> </div> </div> ').format(**L)),
    ('<h2>Sources</h2>',
     '<p style="font-size: 0.8125rem; color: var(--gray-500); margin-top: 2rem;',
     ('<h2>Sources</h2> <ul style="font-size: 0.875rem; line-height: 1.65; margin: 1rem 0; padding-left: 1.25rem;"> '
      '<li>World Health Organization. ' + a('who1995', 'Physical status: the use and interpretation of anthropometry') +
      '. Technical Report Series 854, 1995.</li> '
      '<li>World Health Organization. ' + a('who2000', 'Obesity: preventing and managing the global epidemic') +
      '. Technical Report Series 894, 2000.</li> '
      '<li>Centers for Disease Control and Prevention. ' + a('cdc_cats', 'Adult BMI categories') + ' and ' +
      a('cdc_about', 'About Body Mass Index (BMI)') + '.</li> '
      '<li>National Heart, Lung, and Blood Institute. ' + a('nhlbi', 'Clinical guidelines on the identification, evaluation, '
                                                           'and treatment of overweight and obesity in adults') + ', 1998.</li> '
      '<li>Global BMI Mortality Collaboration. ' + a('gbmc', 'Body-mass index and all-cause mortality: '
                                                     'individual-participant-data meta-analysis of 239 prospective studies in '
                                                     'four continents') + '. <em>Lancet</em> 2016;388:776&ndash;86.</li> '
      '<li>Flegal KM, Kit BK, Orpana H, Graubard BI. ' + a('flegal', 'Association of all-cause mortality with overweight and '
                                                           'obesity using standard body mass index categories') +
      '. <em>JAMA</em> 2013;309(1):71&ndash;82 (PMID 23280227).</li> '
      '<li>Winter JE, MacInnis RJ, Wattanapenpaiboon N, Nowson CA. ' + a('winter', 'BMI and all-cause mortality in older '
                                                                       'adults: a meta-analysis') +
      '. <em>Am J Clin Nutr</em> 2014;99(4):875&ndash;90.</li> '
      '<li>WHO Expert Consultation. ' + a('who2004', 'Appropriate body-mass index for Asian populations and its implications '
                                          'for policy and intervention strategies') +
      '. <em>Lancet</em> 2004;363:157&ndash;63.</li> '
      '<li>National Center for Health Statistics. ' + a('hestat', 'Health E-Stat 111') + ' (overweight and obesity, '
      '1960&ndash;2023) and ' + a('nchs_uw', 'Health E-Stat 119') + ' (underweight).</li> </ul> ')),
]

FAQ = {
    'Are BMI categories the same worldwide?': (
        'WHO&rsquo;s categories are the international ones: underweight below 18.5, normal 18.5&ndash;24.9, pre-obese '
        '25&ndash;29.9 and obese 30 or more ({who2000}). A 2004 WHO expert consultation kept them but added lower '
        'public-health action points for Asian populations, at 23 and 27.5 ({who2004}). ' + NICE_LINE),
    'Can you be healthy with an overweight BMI?': (
        'BMI alone can&rsquo;t tell: ' + CDC_FACTORS + '. Across whole populations, the two pooled analyses on this page '
        'disagree about the overweight range: all-cause mortality was slightly lower than in the healthy range in one '
        '({flegal}) and higher in the other ({gbmc}).'),
    'What is the difference between overweight and obese?': (
        'Overweight is a BMI of 25.0 to 29.9 and obesity 30.0 or more, in three classes ({cdc_cats}). In US adults in '
        '2021&ndash;2023, 31.7% had overweight and 40.3% had obesity (age-adjusted; {hestat}). In pooled data from 239 '
        'studies, the risk of death was higher in each obesity class than in the overweight range ({gbmc}).'),
    'Do BMI categories apply to athletes?': (
        'Not on their own. CDC notes that BMI does not distinguish between fat, muscle and bone mass ({cdc_about}). At the '
        'NFL Scouting Combine, for example, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured '
        'body fat ({provencher}). For muscular people, a body fat estimate or <a href="/lean-body-mass/">lean body mass</a> '
        'measures what BMI cannot.'),
    'Should children use adult BMI categories?': (
        'No. Because children and teens are growing, CDC expresses their BMI as a percentile against others of the same sex '
        'and age, from age 2 through 19 ({cdc_child}). A 6-year-old with a BMI of 15.5 is in CDC&rsquo;s healthy weight '
        'category, boys and girls alike, but adult categories would classify them as severely underweight. See our <a '
        'href="/kids-bmi-calculator/">Pediatric BMI Calculator</a> for the child and teen categories.'),
    'How do I move to a healthier BMI category?': (
        'CDC&rsquo;s summary: &ldquo;Healthy weight loss includes a lifestyle with healthy eating patterns, regular physical '
        'activity, enough sleep, and stress management&rdquo; ({cdc_lw}). For activity, the Physical Activity Guidelines for '
        'Americans say adults need at least 150 to 300 minutes of moderate-intensity aerobic activity a week, plus '
        'muscle-strengthening activity on at least 2 days ({odphp}). In a large trial of adults with overweight or obesity '
        'and type 2 diabetes, losing 5&ndash;10% of body weight was linked to improvements in blood sugar, blood pressure and '
        'cholesterol within a year ({wing}). Our guide to <a href="/blog/how-to-lower-bmi/">lowering your BMI</a> goes '
        'through CDC&rsquo;s steps.'),
    'What is the healthiest BMI to have?': (
        'CDC counts all of 18.5 to just under 25 as healthy weight ({cdc_cats}). Within it, pooled data from 239 studies put '
        'the lowest risk of death at 20.0 to 24.9 ({gbmc}). Older adults may differ: in adults 65 and over, compared with a '
        'BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 ({winter}).'),
    'How accurate is BMI as a health indicator?': (
        'CDC calls BMI &ldquo;a quick, low-cost, and reliable screening measure&rdquo; for underweight, overweight or '
        'obesity, but notes that it does not directly measure body fat and does not distinguish between fat, muscle and bone '
        'mass ({cdc_about}). At a given BMI, body fat may vary by sex, age, and race and Hispanic origin, NCHS notes '
        '({hestat}). See our <a href="/blog/bmi-limitations/">BMI limitations</a> guide for a full analysis.'),
}
FAQ = {q: ans.format(**L) for q, ans in FAQ.items()}

COMMENTS = re.compile(r'<!-- band widths in BMI units:.*?= 300 --> ', re.S)


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:90]}'
    return src.replace(old, new)


def block(src, start, end, new):
    i = src.find(start)
    assert i >= 0 and src.count(start) == 1, f'block start: {start[:70]}'
    j = src.find(end, i)
    assert j > i and src.count(end) == 1, f'block end: {end[:70]}'
    return src[:i] + new + src[j:]


def page(src):
    assert len(COMMENTS.findall(src)) == 1, 'figure comments'
    src = COMMENTS.sub('', src)
    for old, new in EDITS:
        src = one(src, old, new, PG)
    for start, end, new in BLOCKS:
        src = block(src, start, end, new)
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question">' + re.escape(q) + r'<svg.*?</button> <div class="faq-answer">)<p>.*?'
                         r'(?:</p>)?\s*</div>', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + '<p>' + ans + '</p></div>', src)
    qa = re.findall(r'(?s)<button class="faq-question">(.*?)<svg.*?</button> <div class="faq-answer"><p>(.*?)</p></div>', src)
    assert len(qa) == 8, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + json.dumps(d, ensure_ascii=False) + src[fb.end(2):]
    return one(src, '"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"', PG)


def main():
    for rel in (PG, SM):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == PG:
            src = page(src)
        else:
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-categories/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-categories/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
