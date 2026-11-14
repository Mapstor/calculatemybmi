#!/usr/bin/env python3
"""CMB-051 CLAIMS-4: claims pass batch 4 (DEVLOG §5 P1) on /blog/bmi-and-health-risks/ (30 probe hits).
Every sentence now says what a registry row says, or goes (D-10); no treatment, medicines or surgery (D-01); the help
lines are CDC's and NIMH's own "when" (§4). Sources read in Chrome 2026-11-14 (registry.py records them): NIDDK "Health
Risks of Overweight & Obesity" (last reviewed May 2023: each condition), NCI "Obesity and Cancer" (reviewed January 28,
2025: the 13 cancers, the size of the risks, the mechanisms, the 2019 share of cases); already in the registry: the
Global BMI Mortality Collaboration 2016, Flegal 2013, Winter 2014, WHO TRS 894 (the obesity classes), Wing 2011,
Caleyachetty 2017, Provencher 2018, CDC About BMI, CDC Steps for Losing Weight, NIMH.
Out: the dot matrix figure and its og image ("qualitative association strength" no source gives), the category table
under a mortality heading with no mortality in it, "CVD is the leading cause of death worldwide ... most significant
modifiable risk factor", the heart mechanism list, the cardiovascular trend table, "hypertension is often the earliest
sign", the diabetes mechanism list, "the single strongest BMI-linked chronic disease", the per-cancer mechanism column,
"impaired immune surveillance", the respiratory and musculoskeletal run-ups, the sleep apnea consequence list, non-
weight-bearing osteoarthritis, "most common chronic liver condition", the NAFLD spectrum, "approximately doubles the risk
of developing CKD", dialysis and resistant hypertension, the bidirectional mental-health claims, the anxiety and quality-
of-life lists, "severely underweight ... comparable to Class II obesity", "Subcutaneous fat ... less harmful", "Ongoing
monitoring is important", the amber "starting point, not a verdict" box, "one of the most important modifiable cancer-
risk factors after not smoking", the obesity paradox's populations and bias list, three bare clinician lines; the WHO
fact sheet link for the obesity classes (the sheet has none; WHO's 2000 report does).
In: the GBMC hazard ratios as bars (the underweight page's chart) and prose, NIDDK on each condition, NCI on cancer,
Caleyachetty on "metabolically healthy" obesity, CDC on reading BMI with other factors, NCI on fat distribution, the CDC
and NIMH help lines. Title, H1 and URL kept. Meta descriptions, the Article description and image, the FAQPage JSON-LD
(all seven visible answers), dateModified, article:modified_time and lastmod follow. The og image is redrawn as the
GBMC bars (og_health_risks.py) under a new name; the old matrix image is deleted. Files are checked by SHA-256 first;
every marker must occur once.
usage: python3 research/cmb-051/apply.py [--check]   Run order from main: registry.py, apply.py, og_health_risks.py,
audit_manual.py."""
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
PG, SM = 'blog/bmi-and-health-risks/index.html', 'sitemap.xml'
OLD_OG = 'assets/images/og/bmi-health-risks-matrix.png'
NEW_OG = 'assets/images/og/bmi-health-risks-death.png'
BASE = {PG: '9aa6a15ad79bac1ba6b300088218736f7385a41be914247e783888edf01a3604',
        SM: 'b0e2a6992926480b37054e651a34e37ea176fed3d43e7bc2da3448784d525465'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'niddk': 'https://www.niddk.nih.gov/health-information/weight-management/adult-overweight-obesity/health-risks',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'flegal': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/',
    'who2000': 'https://pubmed.ncbi.nlm.nih.gov/11234459/',
    'wing': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
    'caley': 'https://doi.org/10.1016/j.jacc.2017.07.763',
    'prov': 'https://doi.org/10.1519/JSC.0000000000002449',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'nimh': 'https://www.nimh.nih.gov/health/publications/eating-disorders',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


# Global BMI Mortality Collaboration 2016, never-smokers without chronic disease, HR vs 22.5-<25 (registry sample);
# the same bars as /blog/underweight-bmi-risks/ (CMB-049), one scale: width = HR / 2.76
GBMC = [('15.0–18.4', 1.51, 'underweight'), ('18.5–19.9', 1.13, 'normal'), ('20.0–22.4', 1.00, 'normal'),
        ('22.5–24.9', 1.00, 'normal'), ('25.0–27.4', 1.07, 'overweight'), ('27.5–29.9', 1.20, 'overweight'),
        ('30.0–34.9', 1.45, 'obese'), ('35.0–39.9', 1.94, 'obese'), ('40.0–59.9', 2.76, 'obese')]
BARS = ''.join(
    f'<div class="chart-bar-h-item"><span class="chart-bar-h-label">BMI {r}</span><div class="chart-bar-h-track">'
    f'<div class="chart-bar-h-fill {c}" style="width:{hr / 2.76 * 100:.1f}%;"></div></div>'
    f'<span class="chart-bar-h-value">{hr:.2f}</span></div>' for r, hr, c in GBMC)
CHART = ('<div class="chart-bar-h"> <p style="font-size: 0.875rem; font-weight: 600; margin-bottom: 1rem; color: '
         'var(--gray-700);">Risk of death by BMI (hazard ratio; 1.00 = BMI 22.5 to 24.9)</p> ' + BARS + ' </div>')


def grab(src, start, end):
    assert src.count(start) == 1, start[:60]
    i = src.index(start)
    return src[i:src.index(end, i) + len(end)]


def body(src):
    cta_bmi = grab(src, '<p style="text-align: center; margin: 2rem 0;"><a href="/" class="cta-button">', '</p>')
    winter = grab(src, 'For adults 65 and over, <a href="https://pubmed.ncbi.nlm.nih.gov/24452240/"', '</p>')
    older = grab(src, '<h3>Older adults (65+)</h3>', '</p>')
    cta_ideal = grab(src, '<p style="text-align: center; margin: 2rem 0;"><a href="/ideal-weight/" class="cta-button">',
                     '</p>')
    tk_wing = grab(src, '<li><strong>Modest weight loss:</strong>', '</li>')
    tk_calc = grab(src, '<li><strong>Use our <a href="/">BMI calculator</a></strong>', '</li>')
    return (
        '<p class="intro-text">Compared with people at a healthy weight, those with overweight or obesity are at greater '
        'risk for many diseases, including diabetes, high blood pressure, cardiovascular disease, stroke and at least 13 '
        f'types of cancer, and have a higher risk of death from all causes ({a("nci", "NCI")}). NIDDK adds that the risk '
        f'is greater for people who carry extra fat around the waist ({a("niddk", "NIDDK")}). Below: the risk of death '
        'across the BMI range, each condition as NIH describes it, and the cases where BMI’s '
        '<a href="/blog/bmi-limitations/">limits</a> make it misjudge risk.</p> '
        '<div class="key-takeaways"> <div class="key-takeaways-title">Key Takeaways</div> <ul> '
        '<li><strong>Risk of death:</strong> in pooled data from 239 studies it was lowest at a BMI of 20.0 to 24.9, 1.51 '
        f'times as high at 15.0 to 18.4 and 2.76 times at 40.0 to 59.9 ({a("gbmc", "GBMC, 2016")})</li> '
        '<li><strong>Diabetes:</strong> nearly 9 in 10 people with type 2 diabetes have overweight or obesity '
        f'({a("niddk", "NIDDK")})</li> '
        '<li><strong>Blood pressure and stroke:</strong> a large body may raise blood pressure because the heart has to pump '
        f'harder, and high blood pressure is the leading cause of strokes ({a("niddk", "NIDDK")})</li> '
        '<li><strong>Cancer:</strong> overweight and obesity are linked to 13 cancers, with the largest increases for '
        f'endometrial and esophageal cancer ({a("nci", "NCI")})</li> '
        + tk_wing + ' ' + tk_calc + ' </ul> </div> '
        # risk of death
        '<h2 id="risk-of-death">BMI and the Risk of Death</h2> '
        '<p>The Global BMI Mortality Collaboration pooled 239 studies from 32 countries and, to limit the effect of smoking '
        'and existing illness, analysed never-smokers without chronic disease at the start, leaving out the first 5 years of '
        'follow-up. Against a BMI of 22.5 to 24.9, the risk of death was higher below 20 and at every step above 25 '
        f'({a("gbmc", "Global BMI Mortality Collaboration, 2016")}).</p> ' + CHART + ' '
        f'<p>Pooling general-population studies, {a("flegal", "Flegal et al. 2013 (<em>JAMA</em>, PMID 23280227; ~2.88M individuals, >270,000 deaths)")} '
        'reported overweight HR 0.94, Grade 1 obesity HR 0.95 (not statistically significant) and Grade 2+ obesity HR '
        '1.29, all relative to normal weight. ' + winter + ' ' + cta_bmi + ' '
        # obesity classes
        '<h2 id="obesity-classes">Obesity classes at a glance</h2> '
        '<p>WHO’s 2000 report divides the obese range into three classes: Class I (BMI 30.0&ndash;34.9), Class II (BMI '
        f'35.0&ndash;39.9) and Class III (BMI &ge; 40.0) ({a("who2000", "WHO, 2000")}). See our '
        '<a href="/blog/bmi-categories/">BMI Categories</a> guide for the full classification. This site does not cover '
        'treatment, medicines or surgery.</p> '
        # heart
        '<h2>Cardiovascular Disease and BMI</h2> '
        '<h3>Heart Disease</h3> <p>Having overweight or obesity raises the risk of conditions that can lead to heart '
        'disease, such as high blood pressure, high blood cholesterol and high blood glucose, and extra weight can make the '
        f'heart work harder to send blood to all the cells in the body ({a("niddk", "NIDDK")}).</p> '
        '<h3>Hypertension (High Blood Pressure)</h3> <p>A large body may raise blood pressure because the heart has to pump '
        'harder to supply blood to all the cells, and excess fat may also damage the kidneys, which help regulate blood '
        'pressure. High blood pressure can strain the heart, damage blood vessels and raise the risk of heart attack, '
        f'stroke, kidney disease and death ({a("niddk", "NIDDK")}).</p> '
        '<h3>Stroke</h3> <p>Overweight and obesity are known to raise blood pressure, and high blood pressure is the leading '
        f'cause of strokes ({a("niddk", "NIDDK")}).</p> '
        # diabetes
        '<h2>Type 2 Diabetes and BMI</h2> <p>Nearly 9 in 10 people with type 2 diabetes have overweight or obesity, and over '
        'time high blood glucose can lead to heart disease, stroke, kidney disease, eye problems and nerve damage. For people '
        'at risk of type 2 diabetes, NIDDK says losing at least 5% to 7% of their starting weight may prevent or delay it: '
        f'about 10 to 14 pounds for someone who weighs 200 ({a("niddk", "NIDDK")}).</p> '
        # cancer
        '<h2>Cancer and BMI</h2> <p>An International Agency for Research on Cancer working group reviewed more than 1,000 '
        'studies and found consistent evidence that more body fat goes with a higher risk of a number of cancers. NCI lists '
        f'13, and the size of the increase differs between them ({a("nci", "NCI")}):</p> '
        '<h3>Obesity-associated cancers</h3> <div class="table-responsive"><table class="data-table"> <thead> <tr> '
        '<th>Cancer</th> <th>Risk compared with a healthy weight</th> </tr> </thead> <tbody> '
        '<tr><td>Endometrial (type 1)</td><td>Two to four times with overweight or obesity; about seven times with severe '
        'obesity</td></tr> '
        '<tr><td>Esophageal</td><td>More than twice with obesity; nearly five times with severe obesity</td></tr> '
        '<tr><td>Upper stomach, liver, kidney, multiple myeloma, meningioma, pancreatic, colorectal, gallbladder, '
        'postmenopausal breast, ovarian, thyroid</td><td>From about 10% higher to double with obesity</td></tr> '
        '</tbody> </table></div> '
        f'<p class="source-note">Source: {a("nci", "NCI, Obesity and Cancer")} (reviewed January 28, 2025).</p> '
        '<p>A study NCI cites estimated that in 2019 about 4.8% of new cancer cases in US men aged 30 and older, and 10.6% '
        f'in women, were due to excess body weight ({a("nci", "NCI")}).</p> '
        '<h3>How Obesity Might Raise Cancer Risk</h3> <p>NCI lists several possible mechanisms:</p> <ul> '
        '<li><strong>Estrogen:</strong> fat tissue makes extra estrogen, and high levels are associated with higher risks of '
        f'breast, endometrial, ovarian and some other cancers ({a("nci", "NCI")})</li> '
        '<li><strong>Insulin and IGF-1:</strong> people with obesity often have higher blood levels of both, and high levels '
        'are associated with higher risks of colorectal, thyroid, breast, prostate, ovarian and endometrial cancers '
        f'({a("nci", "NCI")})</li> '
        '<li><strong>Inflammation:</strong> chronic inflammation, common with obesity, directly promotes tumor growth '
        f'({a("nci", "NCI")})</li> '
        '<li><strong>Adipokines:</strong> leptin rises with body fat and at high levels can promote abnormal cell growth, '
        f'while adiponectin, which may hold tumor growth back, is lower in people with obesity ({a("nci", "NCI")})</li> </ul> '
        # breathing
        '<h2>Respiratory Conditions</h2> <p>Overweight and obesity can affect how well the lungs work, and excess weight '
        f'raises the risk of breathing problems ({a("niddk", "NIDDK")}).</p> '
        '<h3>Obstructive Sleep Apnea (OSA)</h3> <p>Obesity is a common cause of sleep apnea in adults: with overweight or '
        'obesity, more fat may be stored around the neck, which makes the airway smaller. Untreated sleep apnea may raise the '
        'risk of many health problems, including heart disease and diabetes, and losing weight may help reduce it or make '
        f'it go away ({a("niddk", "NIDDK")}).</p> '
        '<h3>Asthma</h3> <p>Asthma is more likely with obesity, NIDDK says, and so are worse symptoms and a harder time '
        f'managing it ({a("niddk", "NIDDK")}).</p> '
        # joints
        '<h2>Musculoskeletal Problems</h2> <p>Obesity is a leading risk factor for osteoarthritis in the knees, hips and '
        'ankles. Extra weight puts more pressure on joints and cartilage, and excess body fat may raise blood levels of '
        'substances that cause inflammation, which may raise the risk as well. Gout, arthritis caused by uric acid crystals in '
        f'the joints, counts obesity among its risk factors too ({a("niddk", "NIDDK")}).</p> '
        # liver
        '<h2>Liver Disease (Non-Alcoholic Fatty Liver Disease)</h2> <p>Nonalcoholic fatty liver disease (NAFLD) and '
        'nonalcoholic steatohepatitis (NASH) develop when fat builds up in the liver, which can lead to severe liver damage, '
        'cirrhosis or liver failure. They most often affect people with overweight or obesity, and NIDDK says losing at least '
        f'3% to 5% of body weight may reduce fat in the liver ({a("niddk", "NIDDK")}).</p> '
        # metabolic syndrome
        '<h2>Metabolic syndrome</h2> <p>Metabolic syndrome is a group of conditions that raise the risk of heart disease, '
        'diabetes and stroke. A diagnosis needs at least three of these: a large waist, high triglycerides, high blood '
        'pressure, high fasting blood glucose and low HDL cholesterol. NIDDK says it is closely linked to overweight and '
        f'obesity and to a lack of physical activity ({a("niddk", "NIDDK")}).</p> '
        # kidney
        '<h2>Kidney Disease</h2> <p>Obesity raises the risk of diabetes and high blood pressure, the most common causes of '
        'chronic kidney disease (CKD), and even without them obesity may raise the risk of CKD and speed up its progress '
        f'({a("niddk", "NIDDK")}).</p> '
        # others
        f'<h2>Other Conditions NIDDK Lists</h2> <p>NIDDK also lists ({a("niddk", "NIDDK")}):</p> <ul> '
        '<li>Gallbladder disease, such as gallstones, and inflammation of the pancreas (pancreatitis)</li> '
        '<li>Problems in pregnancy, including gestational diabetes, preeclampsia and needing a caesarean delivery</li> '
        '<li>Infertility in women and in men</li> <li>Sexual function problems, such as erectile dysfunction</li> </ul> '
        # mental health
        '<h2>Mental Health Connections</h2> <p>Obesity can also affect mental health, raising the risk of long-term stress, '
        'body image problems, low self-esteem, depression and eating disorders. People with overweight or obesity are also '
        'likely to face weight-related bias at school and work, which may harm their quality of life over the long term; '
        'losing excess weight has been found to improve body image and self-esteem and reduce symptoms of depression '
        f'({a("niddk", "NIDDK")}). If you have concerns about your eating behavior or mental health, NIMH says to talk to a '
        f'primary care provider ({a("nimh", "NIMH")}).</p> '
        # underweight
        '<h2>Health Risks of Being Underweight</h2> <p>Being <a href="/blog/underweight-bmi-risks/">underweight</a> (BMI '
        'below 18.5) carries risks of its own. In the Global BMI Mortality Collaboration’s never-smokers, a BMI of 15.0 to '
        f'18.4 carried 1.51 times the risk of death of 22.5 to 24.9, close to the 1.45 of 30.0 to 34.9 ({a("gbmc", "GBMC, 2016")}).</p> '
        # when BMI misjudges
        '<h2>When BMI may overstate or understate risk</h2> <p>CDC says that for individuals, BMI should be considered with '
        f'other factors, such as blood pressure, cholesterol levels and a physical examination ({a("cdc_about", "CDC")}).</p> '
        + older + ' '
        '<h3>Fat distribution</h3> <p>Visceral fat, the fat around the internal organs, seems more dangerous for disease '
        'risk than overall or subcutaneous fat, which is why waist circumference, waist-to-hip '
        f'ratio and waist-to-height ratio are sometimes used along with BMI ({a("nci", "NCI")}).</p> '
        '<h3>&ldquo;Metabolically healthy&rdquo; obesity or overweight</h3> <p>In 3.5 million British adults followed for a '
        'mean of 5.4 years, people with obesity and none of three metabolic abnormalities (diabetes, high blood pressure, '
        'high blood fats) still had a higher risk of coronary heart disease (HR 1.49), cerebrovascular disease (1.07) and '
        'heart failure (1.96) than normal-weight people with none '
        f'({a("caley", "Caleyachetty et al., 2017")}).</p> '
        # reducing
        '<h2>How Reducing BMI Reduces Health Risks</h2> <h3>Modest weight loss</h3> <p>In the Look AHEAD trial of adults '
        'with overweight or obesity and type 2 diabetes, those who lost 5% to under 10% of their weight in a year had greater '
        'odds of improving blood sugar (HbA1c), blood pressure, HDL cholesterol and triglycerides '
        f'({a("wing", "Wing et al., 2011")}).</p> '
        '<p>Reaching and staying at a healthy weight can help prevent these problems, stop them from getting worse or even '
        f'make them go away, NIDDK says ({a("niddk", "NIDDK")}). Our <a href="/blog/how-to-lower-bmi/">How to lower BMI</a> '
        'guide has CDC’s steps; if you’re concerned about your weight, CDC says to talk with your health care provider '
        f'({a("cdc_lw", "CDC")}).</p> '
        # the related guides, described by what they hold now (the women's page lost its hormone notes in CMB-017)
        '<h2>Special Considerations by Population</h2> <p>For particular groups, see our detailed articles:</p> <ul> '
        '<li><strong>Women:</strong> <a href="/women-bmi-calculator/">BMI for women</a>, with where your BMI ranks among US '
        'women, waist size and body fat at the same BMI</li> '
        '<li><strong>Men:</strong> <a href="/men-bmi-calculator/">BMI for men</a>, with where your BMI ranks among US men, '
        'when BMI misleads and waist size</li> '
        '<li><strong>Metabolic factors:</strong> <a href="/blog/bmi-and-metabolism/">BMI and metabolism</a> covers '
        'metabolic rate, metabolic syndrome and muscle</li> '
        '<li><strong>BMI limitations:</strong> <a href="/blog/bmi-limitations/">what BMI misses</a> in certain '
        'populations</li> </ul> ' + cta_ideal + ' ')


FAQ = {
    'Can you be healthy with a high BMI?': (
        'Being free of diabetes, high blood pressure and high blood fats doesn’t erase the risk: in 3.5 million British '
        'adults, people with obesity and none of those three still had a higher risk of coronary heart disease (HR 1.49) and '
        f'heart failure (1.96) than normal-weight people with none ({a("caley", "Caleyachetty et al., 2017")}). Obesity also '
        'raises the risk of conditions that have nothing to do with those three, such as osteoarthritis and sleep apnea '
        f'({a("niddk", "NIDDK")}). Muscle is the other exception: BMI does not distinguish between fat, muscle and bone mass '
        f'({a("cdc_about", "CDC")}).'),
    'How much does reducing BMI lower health risks?': (
        'In the Look AHEAD trial of adults with overweight or obesity and type 2 diabetes, those who lost 5% to under 10% of '
        'their weight in a year had greater odds of improving blood sugar (HbA1c), blood pressure, HDL cholesterol and '
        f'triglycerides ({a("wing", "Wing et al., 2011")}). NIDDK adds that people at risk of type 2 diabetes may prevent or '
        'delay it by losing at least 5% to 7% of their starting weight, and that losing at least 3% to 5% may reduce fat in '
        f'the liver ({a("niddk", "NIDDK")}). Our <a href="/blog/how-to-lower-bmi/">guide to lowering BMI</a> has CDC’s '
        'steps.'),
    'At what BMI does cancer risk increase?': (
        'NCI links both overweight (BMI 25.0 to 29.9) and obesity (30.0 or more) to 13 cancers: endometrial, esophageal, '
        'upper stomach, liver, kidney, multiple myeloma, meningioma, pancreatic, colorectal, gallbladder, postmenopausal '
        'breast, ovarian and thyroid. The increases are largest for endometrial and esophageal cancer; for the others, '
        'obesity raises the risk by about 10% up to double. A study NCI cites estimated that in 2019 about 4.8% of new '
        f'cancer cases in US men aged 30 and older, and 10.6% in women, were due to excess body weight ({a("nci", "NCI")}).'),
    'Does BMI affect mental health?': (
        'Obesity can raise the risk of long-term stress, body image problems, low self-esteem, depression and eating '
        'disorders, and people with overweight or obesity often face weight-related bias at school and work. Losing excess '
        f'weight has been found to improve body image and self-esteem and reduce symptoms of depression ({a("niddk", "NIDDK")}). '
        f'If you have concerns about your eating behavior or mental health, NIMH says to talk to a primary care provider '
        f'({a("nimh", "NIMH")}).'),
    'What health conditions are most strongly linked to BMI?': (
        'NIDDK’s list runs from type 2 diabetes, high blood pressure, heart disease and stroke to fatty liver disease, some '
        'cancers, sleep apnea, osteoarthritis, kidney disease and mental health problems. Nearly 9 in 10 people with type 2 '
        f'diabetes have overweight or obesity ({a("niddk", "NIDDK")}), and among cancers the '
        f'increases are largest for endometrial and esophageal cancer ({a("nci", "NCI")}).'),
    'Is BMI accurate for people with a lot of muscle?': (
        f'Not always: BMI does not distinguish between fat, muscle and bone mass ({a("cdc_about", "CDC")}). At the NFL '
        'Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat '
        f'({a("prov", "Provencher et al., 2018")}). Waist circumference, waist-to-hip and waist-to-height ratio and DXA are '
        f'among the measures sometimes used along with BMI ({a("nci", "NCI")}). See our '
        '<a href="/blog/bmi-limitations/">BMI limitations</a> and <a href="/blog/bmi-for-athletes/">BMI for athletes</a> '
        'guides.'),
    'What is the “obesity paradox”?': (
        'The name for findings like Flegal 2013’s, where overweight carried a slightly lower risk of death than normal weight '
        f'(HR 0.94) and grade 1 obesity about the same (0.95) ({a("flegal", "Flegal 2013")}). The Global BMI Mortality '
        'Collaboration limited its main analysis to never-smokers without chronic disease and left out the first 5 years of '
        'follow-up; there, the risk of death rose at every step above a BMI of 25, from 1.07 at 25.0 to 27.4 to 2.76 at 40.0 '
        f'to 59.9 ({a("gbmc", "GBMC, 2016")}).'),
}

DESC_OLD = ('Comprehensive guide to BMI-related health risks including heart disease, diabetes, cancer, and more. '
            'Evidence-based information on how BMI affects your health and what you can do about it.')
DESC_NEW = ('The risk of death across the BMI range, from 239 studies, and what NIH and NCI say about diabetes, heart disease, '
            'stroke, 13 cancers, sleep apnea and more.')
EDITS = [
    (f'<meta name="description" content="{DESC_OLD}">', f'<meta name="description" content="{DESC_NEW}">'),
    ('<meta property="og:description" content="Evidence-based guide covering all major health conditions associated with '
     'BMI, from cardiovascular disease to mental health. Learn how to reduce your risk.">',
     f'<meta property="og:description" content="{DESC_NEW}">'),
    ('<meta name="twitter:description" content="Evidence-based guide covering all major health conditions associated with '
     'BMI, from cardiovascular disease to mental health.">', f'<meta name="twitter:description" content="{DESC_NEW}">'),
    ('"description": "Comprehensive guide to BMI-related health risks including heart disease, diabetes, cancer, and more."',
     f'"description": "{DESC_NEW}"'),
    ('<p>This article provides general health information about BMI and associated health risks based on population-level '
     'research. It is not a substitute for professional medical advice, diagnosis, or treatment. Individual health risks vary '
     'based on numerous factors beyond BMI, including genetics, lifestyle, existing conditions, and fat distribution. Always '
     'consult with qualified healthcare providers for personalized health assessment and recommendations. If you have '
     'concerns about your weight or health, please seek guidance from a physician, registered dietitian, or other appropriate '
     'healthcare professional.</p>',
     '<p>This article is for information only and is not medical advice. The figures describe groups of people; CDC says '
     f'that for one person, BMI should be read with other factors such as blood pressure and cholesterol ({a("cdc_about", "CDC")}).</p>'),
    ('<p>Evidence-based strategies for reaching and maintaining a healthier weight.</p>',
     '<p>CDC’s steps, the eating and activity guidance, and the weight one BMI point is at your height.</p>'),
    ('<p>Health concerns associated with being underweight and how to address them.</p>',
     '<p>The risks of a BMI below 18.5, and when to get help.</p>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
    ('<meta property="article:modified_time" content="2026-11-13T00:00:00Z">',
     f'<meta property="article:modified_time" content="{TODAY}T00:00:00Z">'),
]


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
    j = src.index('<h2>Frequently Asked Questions</h2>', i)
    src = src[:i] + body(src) + src[j:]
    for old, new in EDITS:
        src = one(src, old, new, PG)
    n_img = src.count(OLD_OG)
    assert n_img == 3, n_img                                  # og:image, twitter:image, the Article's image
    src = src.replace(OLD_OG, NEW_OG)
    for q, ans in FAQ.items():
        qh = html.escape(q, quote=False).replace('“', '&ldquo;').replace('”', '&rdquo;')
        pat = re.compile(r'(<button class="faq-question">' + re.escape(qh) + r'<svg.*?</button> <div class="faq-answer"> <p>)(.*?)(</p> </div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question">(.*?)<svg.*?</button> <div class="faq-answer"> <p>(.*?)</p> </div>', src)
    assert len(qa) == 7, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + ' ' + jsonld_block(d) + ' ' + src[fb.end(2):]
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
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-and-health-risks/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-and-health-risks/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')
    old = REPO / OLD_OG
    if not CHECK and old.exists():
        old.unlink()
        print(f'{OLD_OG}: deleted (og_health_risks.py draws {NEW_OG})')


if __name__ == '__main__':
    main()
