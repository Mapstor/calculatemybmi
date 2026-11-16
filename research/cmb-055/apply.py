#!/usr/bin/env python3
"""CMB-055 CLAIMS-8: claims pass batch 8 (DEVLOG §5 P1) on /blog/bmi-limitations/ (13 probe hits).
Each of the ten limitations now says what CDC, NCHS, NIH, NICE, WHO or a registry study says, or what CDC's own DXA scans
show (our calculation, as the body fat pages already print it); the rest went (D-10). Doctor lines are CDC's own (§4).
Out: "mounting scientific evidence", the metabolically-healthy-obesity paragraph under the muscle heading, "Perhaps no
group illustrates BMI's flaws better", "far more relevant than BMI", "This muscle loss is often accompanied by fat gain",
the height-loss paragraph (no registry row), "developed primarily using data from European populations", the pregnancy
lines the registry does not hold (what the weight gain is made of, "meaningless and potentially harmful"), the "skinny
fat" features list, the bone factor list and "several pounds more", "essential body fat", the MHO/MUNW list and the
metabolic-panel advice, "evidence-based alternatives" and the unsourced accuracy, ease and cost ratings, "the gold
standard", "even basic bioelectrical impedance scales offer more insight", "effective for tracking obesity trends",
"may benefit from further assessment", "Very high or very low BMI values generally do indicate health concerns", the
FAQ claims ("notoriously", "recommended by many researchers", puberty) and the four-line doctor disclaimer. The figure's
height tile had Trefethen backwards (he argues the standard formula reads tall people too high and short people too low),
its older-adult tile claimed "more fat mass at the same weight", its Asian tile now gives the 2004 WHO consultation the
section cites (it gave the 2000 Western Pacific proposal, row ko-tang-2006-wpro-2000), and its caption said each case has
a numbered section (height has none). Title, H1 and URL kept (D-28);
meta descriptions and the Article description follow; FAQPage JSON-LD rebuilt from the seven visible answers;
dateModified and lastmod. The alternatives table has two columns (the measure and what it shows in one cell) so it fits
a 390 px phone.
usage: python3 research/cmb-055/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
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
PG, SM = 'blog/bmi-limitations/index.html', 'sitemap.xml'
BASE = {PG: '5d874c79b2cfe7414219686c28fb76d99a7c40bc7336b51322462c492c93ec7a',
        SM: 'ede6fb2a866e479ac240fce3d1e0184a370e7e8817756411131362e0dd410db1'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_cats': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_child_calc': 'https://www.cdc.gov/bmi/child-teen-calculator/index.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'cdc_preg': 'https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
    'hestat': 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm',
    'dxa': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'browning': 'https://doi.org/10.1017/S0954422410000144',
    'provencher': 'https://doi.org/10.1519/JSC.0000000000002449',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'niams': 'https://www.niams.nih.gov/health-topics/osteoporosis',
    'eknoyan': 'https://doi.org/10.1093/ndt/gfm517',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


L = {
    'cdc_about': a('cdc_about', 'CDC'), 'cdc_cats': a('cdc_cats', 'CDC'), 'cdc_child': a('cdc_child', 'CDC'),
    'cdc_lw': a('cdc_lw', 'CDC'), 'cdc_preg': a('cdc_preg', 'CDC'), 'hestat': a('hestat', 'NCHS'),
    'dxa': a('dxa', 'CDC NHANES 2011&ndash;2018 DXA scans'), 'nhlbi': a('nhlbi', 'NHLBI'),
    'nice': a('nice', 'NICE guideline NG246'), 'browning': a('browning', 'Browning et al., 2010'),
    'provencher': a('provencher', 'Provencher et al., 2018'), 'gbmc': a('gbmc', 'GBMC, 2016'),
    'niams': a('niams', 'NIAMS'), 'eknoyan': a('eknoyan', 'Eknoyan, 2008'),
    'cdc_child_calc': a('cdc_child_calc', 'CDC'),
}
CDC_FACTORS = ('For individuals, CDC says BMI should be considered with other factors, such as blood pressure, cholesterol '
               'levels and a physical examination ({cdc_about}).').format(**L)
CDC_PREG = ('for one baby, 28 to 40 lb below 18.5, 25 to 35 lb at 18.5 to 24.9, 15 to 25 lb at 25.0 to 29.9 and 11 to 20 lb '
            'at 30.0 to 39.9, from the Institute of Medicine ({cdc_preg})').format(**L)
NICE_LINE = ('In the UK, NICE uses lower thresholds for adults with a South Asian, Chinese, other Asian, Middle Eastern, '
             'Black African or African-Caribbean background: overweight from 23 to 27.4 and obesity from 27.5 ({nice}).'
             ).format(**L)
DESC = ('Ten ways BMI can mislead, from muscle and fat distribution to age, sex and ethnicity, with what CDC, NIH and the '
        'studies say, and the measures that fill the gaps.')

EDITS = [
    # meta and the Article description
    ('<meta name="description" content="Discover the major limitations of BMI as a health metric. Learn why BMI fails for '
     'athletes, elderly, and different ethnicities, plus better alternatives like waist-to-height ratio and body composition '
     'analysis.">', f'<meta name="description" content="{DESC}">'),
    ('<meta property="og:description" content="Discover why BMI isn\'t always accurate. Learn about its limitations for '
     'athletes, elderly, different ethnicities, and explore better alternatives.">',
     f'<meta property="og:description" content="{DESC}">'),
    ('<meta name="twitter:description" content="Discover why BMI isn\'t always accurate and explore better alternatives for '
     'measuring body composition and health.">', f'<meta name="twitter:description" content="{DESC}">'),
    ('"description": "A comprehensive guide to understanding the limitations of BMI as a health metric, including why it fails '
     'for certain populations and what alternatives exist."',
     '"description": "Where BMI can mislead as a health measure, what the sources say about each case, and the measures that '
     'fill the gaps."'),
    # intro and key takeaways
    ('<p class="intro-text">Body Mass Index (BMI) has been the go-to health screening tool for decades, but mounting '
     'scientific evidence reveals significant flaws in this 200-year-old formula. Understanding these limitations is crucial '
     'for anyone using BMI to assess their health status.</p>',
     '<p class="intro-text">CDC calls BMI &ldquo;a quick, low-cost, and reliable screening measure&rdquo; for underweight, '
     'overweight or obesity, but notes that it does not directly measure body fat ({cdc_about}). Below: ten ways a BMI can '
     'mislead, what the sources say about each, and the measures that fill the gaps.</p>'.format(**L)),
    ('<li><strong>BMI cannot distinguish between muscle and fat</strong> - making it unreliable for athletes, bodybuilders, '
     'and anyone with above-average muscle mass</li>',
     '<li><strong>BMI treats fat, muscle and bone alike:</strong> CDC notes it does not distinguish between them '
     '({cdc_about})</li>'.format(**L)),
    ('<li><strong>Fat distribution matters more than total weight</strong> - visceral fat around organs poses greater health '
     'risks than subcutaneous fat, but BMI ignores this</li>',
     '<li><strong>Where fat sits matters:</strong> NIH guidelines call excess abdominal fat an independent risk factor and add '
     'a waist measurement ({nhlbi})</li>'.format(**L)),
    ('<li><strong>Different populations need different thresholds</strong> - ethnic variations, age differences, and '
     'sex-based body composition changes affect BMI accuracy</li>',
     '<li><strong>Same BMI, different body fat:</strong> at a given BMI, body fat may vary by sex, age, and race and Hispanic '
     'origin, NCHS notes ({hestat})</li>'.format(**L)),
    ('<li><strong>Normal BMI doesn\'t guarantee health</strong> - "skinny fat" individuals with normal BMI but high body fat '
     'face hidden metabolic risks</li>',
     '<li><strong>A healthy BMI can still mean high body fat</strong> (&ldquo;normal weight obesity&rdquo;): BMI does not '
     'measure body fat directly ({cdc_about})</li>'.format(**L)),
    ('<li><strong>Better alternatives exist</strong> - <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>, body '
     'fat percentage, and DEXA scans provide more accurate health assessments</li>',
     '<li><strong>Measures that fill the gaps:</strong> a waist measurement, the <a href="/blog/waist-to-height-ratio/">'
     'waist-to-height ratio</a>, a body fat estimate or a DXA scan (see the table below)</li>'),
    # the figure
    ('<title id="svg-lim-tiles-title">Four archetypes where BMI misleads: muscular athlete, older adult with sarcopenia, '
     'height extremes, ethnic body-composition variation</title>',
     '<title id="svg-lim-tiles-title">Four cases where BMI can mislead: a muscular athlete, an older adult, height extremes '
     'and ethnic variation</title>'),
    ('Four tiles, each capturing a well-documented case where BMI misclassifies. Muscular athlete: high BMI, low body fat. '
     'Older adult: normal BMI can mask sarcopenia. Height extremes: standard formula over- or under-reads at very short or '
     'very tall statures. Ethnic variation: WHO Western Pacific uses lower cutoffs for Asian populations.</desc>',
     'Four tiles. Muscular athlete: at the NFL Scouting Combine, 53.4% of prospects had obesity by BMI but 8.9% by body fat '
     '(Provencher et al., 2018). Older adult: muscle mass falls about 3 to 8% per decade after age 30 (Volpi et al., 2004), '
     'and BMI cannot tell muscle from fat (CDC). Height extremes: Trefethen argues the standard formula reads tall people too '
     'high and short people too low, and proposes height to the power 2.5. Ethnic variation: a 2004 WHO expert consultation '
     'found high risk below a BMI of 25 in many Asian people and added action points at 23 and 27.5.</desc>'),
    ('<text x="22" y="71" fill-opacity="0.7">Standard categorisation labels as "overweight/obese" — misleading.</text>',
     '<text x="22" y="71" fill-opacity="0.7">BMI does not distinguish fat from muscle (CDC).</text>'),
    ('<text x="22" y="135">BMI in "normal" range, but body composition has shifted:</text>',
     '<text x="22" y="135">Muscle mass falls about 3–8% per decade after age 30,</text>'),
    ('<text x="22" y="153" fill-opacity="0.7">less muscle, more fat mass at the same weight.</text>',
     '<text x="22" y="153" fill-opacity="0.7">and BMI cannot see it (Volpi et al., 2004; CDC).</text>'),
    ('<text x="22" y="217">Very short: standard reads too high. Very tall: standard reads too low.</text>',
     '<text x="22" y="217">Trefethen (2013) argues the standard formula reads tall</text>'),
    ('<text x="22" y="235" fill-opacity="0.7">Trefethen 2013 addresses this with a height^2.5 exponent.</text>',
     '<text x="22" y="235" fill-opacity="0.7">people too high, short people too low; he proposes height^2.5.</text>'),
    ('<text x="22" y="299">Same BMI, different risk profile. WHO Western Pacific Region uses</text>',
     '<text x="22" y="299">A 2004 WHO expert consultation found high risk below</text>'),
    ('<text x="22" y="317" fill-opacity="0.7">overweight cutoff 23 (not 25) for Asian populations.</text>',
     '<text x="22" y="317" fill-opacity="0.7">BMI 25 in many Asian people; action points at 23 and 27.5.</text>'),
    ('Four well-documented cases where BMI misleads &mdash; each is discussed in a numbered section below.</figcaption>',
     'Four cases where BMI can mislead. Three have numbered sections below; the height argument is on our <a '
     'href="/new-bmi-calculator/">New BMI calculator</a> page.</figcaption>'),
    # what BMI is
    (' Quetelet created the formula (weight in kg divided by height in meters squared) to study population-level '
     'statistics, not individual health. The formula was never intended to diagnose obesity or predict health outcomes for '
     'individuals.</p>',
     ' He was studying the &ldquo;average man&rdquo;, and in developing the index he had no interest in obesity '
     '({eknoyan}).</p>'.format(**L)),
    (' Today, it remains the most widely used metric because it requires only two measurements: <a '
     'href="/blog/bmi-formula/">height and weight</a>.</p>',
     ' It needs only two measurements: <a href="/blog/bmi-formula/">height and weight</a>.</p>'),
    ('<p>While useful for large population studies, BMI has well-known limitations when applied to individuals.</p> ', ''),
    # 1 muscle and fat
    ('<p>A meaningful share of adults classified as &ldquo;overweight&rdquo; or &ldquo;obese&rdquo; by BMI show no '
     'cardiometabolic abnormalities on clinical testing &mdash; the phenomenon commonly labelled &ldquo;metabolically healthy '
     'obesity.&rdquo; The magnitude reported varies substantially between cohorts and definitions; the takeaway is that BMI '
     'on its own does not determine an individual\'s metabolic health.</p>',
     '<p>BMI is weight divided by height squared, so a kilogram of muscle counts the same as a kilogram of fat. CDC notes '
     'that BMI does not distinguish between fat, muscle and bone mass ({cdc_about}). The spread is wide even inside the '
     'healthy range: on CDC&rsquo;s DXA scans of adults aged 20 to 59 with a BMI of 18.5 to 24.9, the middle half of women '
     'measured 29.8% to 36.5% body fat and the middle half of men 18.6% to 25.0% (our calculation from {dxa}).</p>'
     .format(**L)),
    # 3 athletes
    ('<p>Perhaps no group illustrates BMI\'s flaws better than elite athletes. Due to their high muscle mass and low body '
     'fat, many professional athletes are technically "obese" according to BMI despite being in peak physical condition.</p>',
     '<p>At the NFL Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body '
     'fat ({provencher}).</p>'.format(**L)),
    ('<p>For athletes specifically, body fat percentage and performance metrics are far more relevant than BMI. Learn more in '
     'our detailed guide:',
     '<p>For muscular people, a body fat estimate measures what BMI cannot. Learn more in our detailed guide:'),
    # 4 older adults
    ('<p>BMI becomes increasingly unreliable as people age due to natural changes in body composition. After age 30, adults '
     'lose an estimated 3&ndash;8% of muscle mass per decade, a process called sarcopenia (<a '
     'href="https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/" target="_blank" rel="noopener">Volpi et al., 2004</a>). This '
     'muscle loss is often accompanied by fat gain, but weight may remain stable - meaning BMI stays the same while health '
     'declines.</p>',
     '<p>Muscle mass decreases by about 3&ndash;8% per decade after age 30, and faster after 60; the involuntary loss of '
     'muscle mass, strength and function is called sarcopenia (<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/" '
     'target="_blank" rel="noopener">Volpi et al., 2004</a>). BMI cannot show that change, and NCHS notes that at a given '
     'BMI, body fat may vary by age ({hestat}).</p>'.format(**L)),
    ('<p>Older adults also often experience height loss due to spinal compression and osteoporosis. Since BMI uses height '
     'squared in its denominator, even small height reductions artificially inflate BMI readings.</p> ', ''),
    # 5 ethnicity
    ('<p>BMI thresholds were developed primarily using data from European populations and don\'t account for significant '
     'differences in body composition across ethnic groups. In 2004,',
     '<p>NCHS notes that health risks may begin at a lower BMI among Asian people, and that BMI may overestimate body fat '
     'among Black people at a given BMI compared with others ({hestat}). In 2004,'.format(**L)),
    ('identified BMI 23 and 27.5 as additional public-health action points.</p>',
     'identified BMI 23 and 27.5 as additional public-health action points. ' + NICE_LINE + '</p>'),
    # 6 pregnancy
    ('<p>BMI should not be used to assess healthy weight during pregnancy. Weight gain during pregnancy includes the baby, '
     'placenta, amniotic fluid, increased blood volume, and necessary fat stores - none of which indicate health problems.'
     '</p> <p>Pre-pregnancy BMI is used to determine appropriate weight gain during pregnancy, but ongoing BMI calculations '
     'during pregnancy are meaningless and potentially harmful if they cause unnecessary anxiety.</p>',
     '<p>CDC&rsquo;s weight-gain ranges for pregnancy go by BMI before pregnancy: ' + CDC_PREG + '.</p>'),
    # 8 bone
    ('<p>Our <a href="/lean-body-mass/">Lean Body Mass Calculator</a> can help estimate your non-fat mass, including bones '
     'and muscle.</p>',
     '<p>Our <a href="/lean-body-mass/">Lean Body Mass Calculator</a> estimates your non-fat mass, bone and muscle '
     'included.</p>'),
    # 9 sex
    ('<p>BMI uses identical formulas and cutoffs for men and women, despite significant differences in body composition '
     'between the sexes. Women naturally carry more essential body fat (necessary for hormonal function and reproductive '
     'health), while men typically have more muscle mass.</p>',
     '<p>CDC uses the same adult categories &ldquo;regardless of age, sex, or race&rdquo; ({cdc_cats}), but women carry more '
     'fat at the same BMI: on CDC&rsquo;s DXA scans of adults aged 20 to 59 with a BMI of 18.5 to 24.9, the median body fat '
     'was 33.4% for women and 22.1% for men (our calculation from {dxa}).</p>'.format(**L)),
    # alternatives
    ('<h3>Waist-to-Height Ratio: The Best Free Alternative</h3>', '<h3>Waist-to-Height Ratio: A Free Check</h3>'),
    ('<p>For a complete picture, body composition analysis reveals the percentages of fat, muscle, bone, and water in your '
     'body. While DEXA scans provide the gold standard, even basic bioelectrical impedance scales offer more insight than BMI '
     'alone.</p>',
     '<p>A DXA scan measures fat, lean and bone mass. At home, our <a href="/body-fat-calculator/">body fat calculator</a> '
     'shows how close four simpler methods come to CDC&rsquo;s DXA scans.</p>'),
    ('BMI vs. body Composition: Understanding the Difference', 'BMI vs. Body Composition: Understanding the Difference'),
    # when BMI is useful
    ('<p>Despite its limitations, BMI isn\'t entirely useless. It remains valuable in certain contexts:</p>',
     '<p>Where BMI still helps:</p>'),
    ('<p>BMI is effective for tracking obesity trends in large populations where individual variations average out.</p>',
     '<p>CDC&rsquo;s survey has tracked adult obesity by measured BMI since 1960&ndash;1962: among adults aged 20 to 74, from '
     '13.4% then to 40.8% in 2021&ndash;2023 ({hestat}).</p>'.format(**L)),
    ('<p>As a quick, free screening tool, BMI can identify individuals who may benefit from further assessment.</p>',
     '<p>Compared with direct measures of body fat, CDC lists BMI as quick and simple to calculate, inexpensive and '
     'noninvasive ({cdc_about}).</p>'.format(**L)),
    ('<p>Very high or very low BMI values generally do indicate health concerns worth investigating.</p>',
     '<p>In pooled data from 239 studies, the risk of death rose at both ends: a hazard ratio of 1.51 at a BMI of 15.0 to 18.4 '
     'and 2.76 at 40.0 to 59.9, against 22.5 to 24.9 ({gbmc}).</p>'.format(**L)),
    ('then supplement with waist measurements and, if possible, body composition analysis for a complete health picture.</p>',
     'then add a waist measurement (see <a href="#fat-distribution">Limitation #2</a>).</p>'),
    ('<p>For a complete understanding of how BMI is calculated and what the numbers mean, see our comprehensive',
     '<p>For how BMI is calculated and what the numbers mean, see our'),
    # disclaimer and related articles
    ('<p>The information provided in this article is for educational purposes only and should not be considered medical '
     'advice. BMI and other body composition metrics are screening tools, not diagnostic tests. Individual health status '
     'depends on many factors that only a qualified healthcare provider can assess. Always consult with your doctor or '
     'registered dietitian before making health decisions based on any single metric. If you have concerns about your weight '
     'or health, please seek professional medical evaluation.</p>',
     '<p>This information is for education only and is not medical advice. BMI and other body composition '
     'measures are screening tools, not diagnostic tests. If you&rsquo;re concerned about your weight or have questions about '
     'your medications, CDC says to talk with your health care provider ({cdc_lw}).</p>'.format(**L)),
    ('<p>Compare body fat percentage to BMI and learn which metric matters more for your health.</p>',
     '<p>How body fat percentage and BMI differ, and what each one measures.</p>'),
    ('<p>Why standard BMI categories don\'t apply to athletic populations and what to use instead.</p>',
     '<p>What BMI misses in muscular people, with NFL Scouting Combine data.</p>'),
    ('<p>Learn about this simple, free alternative that many researchers consider superior to BMI.</p>',
     '<p>Your waist divided by your height, with NICE&rsquo;s thresholds.</p>'),
    ('<p>Calculate your fat-free mass including muscle, bone, and organs for better health insight.</p>',
     '<p>Estimate your fat-free mass with the Boer, James and Hume formulas.</p>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

BLOCKS = [
    ('<p>One of BMI\'s most dangerous blind spots is its inability',
     '<p>For more on body composition beyond BMI, see our detailed comparison:',
     ('<p>&ldquo;Normal weight obesity&rdquo;, or &ldquo;skinny fat&rdquo;, describes a healthy BMI with a high body fat '
      'percentage. BMI can&rsquo;t flag it, because it does not directly measure body fat ({cdc_about}). Body fat varies '
      'widely at the same BMI: US women aged 20 to 59 with a BMI of 23.5 to 24.4 measured a median of 35.5% body fat on '
      'CDC&rsquo;s DXA scans, and the middle half were between 33.0% and 38.2% (our calculation from {dxa}). Our <a '
      'href="/body-fat-calculator/">body fat calculator</a> estimates yours four ways.</p> ').format(**L)),
    ('<p>Bone density varies significantly between individuals and populations,',
     '<p>Our <a href="/lean-body-mass/">Lean Body Mass Calculator</a>',
     ('<p>BMI counts bone along with fat and muscle (see <a href="#muscle-vs-fat">Limitation #1</a>), and bone differs '
      'between people: NIH contrasts slender, thin-boned women and men with larger-boned ones, who have more bone '
      '({niams}).</p> ').format(**L)),
    ('<p>BMI tells you nothing about metabolic health',
     '<h2 id="alternatives">',
     ('<p>BMI comes from height and weight alone, so it can&rsquo;t show blood pressure, blood sugar or cholesterol. '
      + CDC_FACTORS + '</p> <!-- Alternatives Section --> ')),
    ('<p>Given BMI\'s limitations, what should you use instead?',
     '<h3>Waist-to-Height Ratio: The Best Free Alternative</h3>',
     ('<p>Each of these adds something BMI can&rsquo;t show:</p> <div class="table-responsive"> <table '
      'class="comparison-table"> <thead> <tr><th>Measure</th><th>What the source says</th></tr> </thead> <tbody> <tr> '
      '<td><strong>Waist circumference</strong><br>Fat around the waist</td> <td>More than 40 in (102 cm) for men or 35 in '
      '(88 cm) for women marks higher risk, at a BMI of 25 to 34.9 (NIH)</td> </tr> <tr> <td><strong>Waist-to-height '
      'ratio</strong><br>Waist fat, scaled to height</td> <td>For adults with a BMI under 35: 0.4 to 0.49 healthy, 0.5 to '
      '0.59 increased, 0.6 or more high (NICE)</td> </tr> <tr> <td><strong>Relative fat mass</strong><br>Body fat %, from '
      'waist and height</td> <td>Within 5 points of a DXA scan for 86% of men and 74% of women (our calculation)</td> </tr> '
      '<tr> <td><strong>DXA scan</strong><br>Fat, lean and bone mass</td> <td>&ldquo;The most widely accepted method of '
      'measuring body composition&rdquo; (CDC)</td> </tr> </tbody> </table> '
      '</div> <p class="source-note">Sources: waist, NIH clinical guidelines, 1998 ({nhlbi}); waist-to-height ratio, '
      '{nice}; relative fat mass, our calculation from {dxa}; the DXA quote, CDC&rsquo;s documentation for those scans '
      '({dxa_doc}).</p> ').format(**L, dxa_doc=a('dxa', 'CDC'))),
]

FAQ = {
    'Why is BMI considered an inaccurate measure of health?': (
        'CDC calls BMI a screening measure that does not directly measure body fat and does not distinguish between fat, '
        'muscle and bone mass ({cdc_about}). It also leaves out where fat sits: NIH guidelines add a waist measurement '
        'because excess abdominal fat is an independent risk factor for disease ({nhlbi}).'),
    'What is a better alternative to BMI?': (
        'A few measures add what BMI misses. A waist measurement shows fat around the middle: NIH guidelines mark '
        'higher risk above 40 inches (102 cm) for men and 35 inches (88 cm) for women ({nhlbi}). For the <a '
        'href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>, a review of 78 studies backed the message &ldquo;keep '
        'your waist circumference to less than half your height&rdquo; ({browning}), and NICE treats 0.5 to 0.59 as '
        'increased and 0.6 or more as high for adults with a BMI under 35 ({nice}). A DXA scan measures body composition '
        'directly.'),
    'Is BMI accurate for athletes and bodybuilders?': (
        'Not on its own. CDC notes that BMI does not distinguish between fat, muscle and bone mass ({cdc_about}). At the NFL '
        'Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat '
        '({provencher}). Our guide to <a href="/blog/bmi-for-athletes/">BMI for athletes</a> goes further.'),
    'Does BMI account for differences between men and women?': (
        'No. CDC uses the same adult categories regardless of sex ({cdc_cats}), but women carry more fat at the same BMI: on '
        'CDC&rsquo;s DXA scans of adults aged 20 to 59 with a healthy BMI, the median body fat was 33.4% for women and 22.1% '
        'for men (our calculation from {dxa}). See the <a href="/women-bmi-calculator/">women&rsquo;s</a> and <a '
        'href="/men-bmi-calculator/">men&rsquo;s</a> calculators.'),
    'What is "skinny fat" and why doesn\'t BMI detect it?': (
        'It describes a healthy BMI with a high body fat percentage, also called normal weight obesity. BMI can&rsquo;t '
        'detect it because it does not directly measure body fat ({cdc_about}); a <a href="/blog/body-fat-vs-bmi/">body fat '
        'percentage</a> estimate can.'),
    'Can BMI be used during pregnancy?': (
        'Before pregnancy, yes: CDC&rsquo;s weight-gain ranges for pregnancy go by it, ' + CDC_PREG + '.'),
    'Is BMI accurate for children and teenagers?': (
        'Children and teens are measured differently: because they are growing, CDC expresses their BMI as a percentile '
        'against others of the same sex and age, from age 2 through 19 ({cdc_child}); see our <a '
        'href="/kids-bmi-calculator/">pediatric BMI calculator</a>. CDC&rsquo;s child and teen calculator page adds: '
        '&ldquo;Persons may consider seeking advice from their health care providers about their BMI&rdquo; '
        '({cdc_child_calc}).'),
}
FAQ = {q: ans.format(**L) for q, ans in FAQ.items()}


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()


def jsonld_block(d):
    return re.sub(r'\n\s*', ' ', json.dumps(d, ensure_ascii=False, indent=1))


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:90]}'
    return src.replace(old, new)


def block(src, start, end, new):
    assert src.count(start) == 1, f'block start: {start[:70]}'
    i = src.find(start)
    j = src.find(end, i)
    assert j > i and src.count(end) == 1, f'block end: {end[:70]}'
    return src[:i] + new + src[j:]


def page(src):
    for start, end, new in BLOCKS:          # the blocks first: two of their end markers are edited below
        src = block(src, start, end, new)
    for old, new in EDITS:
        src = one(src, old, new, PG)
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question">' + re.escape(q) + r'<svg.*?</button> <div class="faq-answer"> <p>)'
                         r'(.*?)(</p> </div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question">(.*?)<svg.*?</button> <div class="faq-answer"> <p>(.*?)</p> </div>', src)
    assert len(qa) == 7, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    return src[:fb.start(2)] + ' ' + jsonld_block(d) + ' ' + src[fb.end(2):]


def main():
    for rel in (PG, SM):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == PG:
            src = page(src)
        else:
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-limitations/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-limitations/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
