#!/usr/bin/env python3
"""CMB-060 CLAIMS-11: claims pass batch 11 (DEVLOG §5 P1) on /blog/bmi-chart-explained/ (7 probe hits, and the lines
round them that had no source). Each line now says what a registry row says, or went (D-10, D-01, D-06):
  - "What Is a BMI Chart?": "developed to make body mass index accessible to everyone", "widely used in clinical
    settings, schools, fitness facilities" and "WHO, CDC and NIH all publish standardized BMI charts" become NHLBI's BMI
    table and CDC's and WHO's categories;
  - colour coding: "as health risk increases", "the healthy BMI range to aim for" (a target, D-06) and "these category
    cutoffs are based on the relationship between BMI and health outcomes" (not on CDC's page) out; CDC's "regardless of
    age, sex, or race" in;
  - "Why the Same Categories Apply to Both Sexes": "made for simplicity and based on population-level mortality data"
    becomes WHO's 2000 conclusion and CDC's rule, with CDC's body-scan medians for women and men;
  - "Why age matters": "Height shrinkage" and "Reverse causation" had no source; Gallagher et al. (2000, Table 4) and
    NICE 1.9.13 in; "(morning is best, as you are tallest)" out;
  - the four zones: the underweight concerns and causes lists (D-01), "the lowest health risks", "Lowest risk of
    weight-related diseases", "Maintain through balanced nutrition", "pre-obese" (not in the registry), "the other
    medical organizations classify as a chronic disease" and "progressively higher risk" out; CDC's categories,
    MedlinePlus's own "when" for unexplained weight loss, GBMC 2016, CDC on muscle and on individuals, NIH's waist lines,
    WHO's classes, NCI's risk list, Look AHEAD with its population (adults with type 2 diabetes), and CDC's provider line
    in;
  - limitations: the two lists keep only what CDC, NIH, Gallagher and NICE back, with a source line; "Muscle weighs more
    than fat", "skinny fat" and "People of African descent: ... standard cutoffs potentially too strict" (NICE uses LOWER
    thresholds for Black African and African-Caribbean backgrounds) become CDC, NICE 1.9.12/1.9.14, Gallagher, CDC's
    2021-2023 waist shares and NICE 1.9.11;
  - FAQ: five answers; the FAQPage JSON-LD rebuilt from the seven visible answers;
  - disclaimer: "Always consult a qualified healthcare provider ... treatment recommendations" becomes CDC's "when" (§4);
  - intro: "This comprehensive guide explains ..." (two prose-score tells) becomes the one promise line ("Below: ...").
dateModified and lastmod follow.
usage: python3 research/cmb-060/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
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
PG, SM = 'blog/bmi-chart-explained/index.html', 'sitemap.xml'
BASE = {PG: '0912493ecbbbea35684fa6d1d36064636c45841b0ef4070467ea32269ddcff7f',
        SM: 'af435cd8109952a7a481d964546ff302bf3093f75942b9dade36984ccd366743'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'nhlbi_tbl': 'https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_tbl.pdf',
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'who_fs': 'https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight',
    'who00': 'https://pubmed.ncbi.nlm.nih.gov/11234459/',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'gal': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'medline': 'https://medlineplus.gov/ency/article/003107.htm',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
    'wing': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
    'who04': 'https://pubmed.ncbi.nlm.nih.gov/14726171/',
    'nhanes': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


LI = '<li style="margin-bottom: 0.5rem;">'
UL = '<ul style="margin: 1rem 0; padding-left: 1.5rem;">'
CDC_Q = '“a quick, low-cost, and reliable screening measure”'
SCANS = ('in CDC’s 2011–2018 body scans of adults aged 20 to 59 with a BMI of 18.5 to 24.9, the median body fat was 33.4% '
         'for women and 22.1% for men (our <a href="/body-fat-percentage-chart/">body fat percentage chart</a> uses the same '
         'scans)')

EDITS = [
    ('<p>BMI charts were developed to make body mass index accessible to everyone, including those without calculators or '
     'mathematical confidence. They remain widely used in clinical settings, schools, fitness facilities, and public health '
     'materials because they provide:</p>',
     '<p>Compared with working out the formula, a chart gives you:</p>'),
    ('<p>The World Health Organization (WHO), Centers for Disease Control and Prevention (CDC), and National Institutes of '
     'Health (<a href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" target="_blank" rel="noopener">NIH NHLBI</a>) '
     'all publish standardized BMI charts using consistent category definitions.</p>',
     f'<p>NHLBI publishes a BMI table for adults ({a("nhlbi_tbl", "NHLBI")}), and CDC and WHO define the adult categories '
     f'its colours follow ({a("cdc_cat", "CDC")}; {a("who_fs", "WHO")}).</p>'),
    ('<p>The color gradient serves multiple purposes beyond quick identification:</p> ' + UL + ' ' + LI +
     '<strong>Risk visualization:</strong> Colors progress from cool (blue/green) to warm (yellow/orange/red) as health risk '
     'increases</li> ' + LI + '<strong>Zone boundaries:</strong> Color changes mark the exact BMI thresholds between '
     'categories</li> ' + LI + '<strong>Target identification:</strong> The green zone clearly shows the healthy BMI range to '
     'aim for</li> ' + LI + '<strong>Progress tracking:</strong> You can visualize how weight changes would shift you between '
     'color zones</li> </ul> <p>According to the <a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" '
     'target="_blank" rel="noopener">CDC Adult BMI Categories</a>, these category cutoffs are based on the relationship '
     'between BMI and health outcomes across populations, though they acknowledge individual variation exists.</p>',
     '<p>The colours help in two ways:</p> ' + UL + ' ' + LI + '<strong>Zone boundaries:</strong> a colour change marks the '
     'BMI where one category ends and the next begins</li> ' + LI + '<strong>Neighbouring cells:</strong> you can see how far '
     'a weight is from the next category</li> </ul> <p>CDC applies the categories to adults 20 and older regardless of age, '
     f'sex or race ({a("cdc_cat", "CDC")}).</p>'),
    ('<p>The decision to use unified cutoffs was made for simplicity and based on population-level mortality data. At the BMI '
     'thresholds, health risks increase for both sexes, making these reasonable screening cutpoints for general use.</p>',
     '<p>WHO’s 2000 report concluded that a coherent system of BMI classes should be adopted internationally '
     f'({a("who00", "WHO, 2000")}), and CDC applies its categories regardless of sex ({a("cdc_cat", "CDC")}). Body fat '
     f'differs at the same BMI: {SCANS}.</p>'),
    (UL + ' ' + LI + '<strong>Body composition changes:</strong> muscle mass declines with age and fat mass tends to increase, '
     'even at stable weight.</li> ' + LI + '<strong>Height shrinkage:</strong> stature loss across later life inflates BMI even '
     'when weight is unchanged.</li> ' + LI + '<strong>Reverse causation in cohort data:</strong> older adults with low BMI '
     'often include those who have lost weight to undiagnosed illness &mdash; this can inflate mortality in the '
     '&ldquo;normal&rdquo; comparison group.</li> </ul>',
     UL + ' ' + LI + '<strong>Body fat at the same BMI:</strong> rises with age; at a BMI of 25, Gallagher and colleagues '
     'predicted 20% body fat for African American and white men aged 20 to 39 and 25% at 60 to 79 '
     f'({a("gal", "Gallagher et al., 2000")}, Table 4).</li> ' + LI + '<strong>Caution after 65:</strong> NICE advises '
     'interpreting BMI with caution in people aged 65 and over, taking into account other conditions and the possible '
     f'protective effect of a slightly higher BMI when older ({a("nice", "NICE NG246")}).</li> </ul>'),
    ('Measure height without shoes (morning is best, as you are tallest) and weight with minimal clothing at a consistent '
     'time of day.',
     'Measure height without shoes and weight with minimal clothing, at a consistent time of day.'),
    ('<p>This article is for informational purposes only and does not constitute medical advice. BMI charts and calculators '
     'are screening tools, not diagnostic tests. They cannot account for individual factors like muscle mass, bone density, '
     'age, sex, ethnicity, or fat distribution. A "normal" BMI does not guarantee good health, and an elevated BMI does not '
     'automatically indicate a health problem. Always consult a qualified healthcare provider for personalized assessment, '
     'diagnosis, and treatment recommendations. Do not make health decisions based solely on BMI classification.</p>',
     '<p>This article is for informational purposes only and does not constitute medical advice. BMI charts and calculators '
     'are screening tools, not diagnostic tests. They cannot account for individual factors like muscle mass, bone density, '
     'age, sex, ethnicity, or fat distribution. A "normal" BMI does not guarantee good health, and an elevated BMI does not '
     'automatically indicate a health problem. If you’re concerned about your weight, CDC says to talk with your health care '
     f'provider ({a("cdc_lw", "CDC")}).</p>'),
    ('This comprehensive guide explains how to read BMI charts, understand the color-coded zones, interpret your results, '
     'and know when to use a chart versus a <a href="/">BMI calculator</a>.</p>',
     'Below: how to read the chart, what its colours mean, and when a <a href="/">BMI calculator</a> is the better '
     'tool.</p>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

ZONES = (
    '<h2 id="interpreting-zones">Interpreting BMI Chart Zones</h2> <p>Each colour on the chart is one of CDC’s adult '
    'categories. Here is what the sources say about each:</p> '
    '<h3>Underweight Zone (Blue - BMI Under 18.5)</h3> <p>A BMI below 18.5 is underweight '
    f'({a("cdc_cat", "CDC")}). If you are losing weight without trying, MedlinePlus advises contacting a provider after a loss '
    'of about 10 pounds (4.5 kg), or 5% of your normal weight, over 6 to 12 months or less without a known reason '
    f'({a("medline", "MedlinePlus")}). Our guide to <a href="/blog/underweight-bmi-risks/">underweight BMI risks</a> covers '
    'the rest.</p> '
    '<h3>Normal Weight Zone (Green - BMI 18.5-24.9)</h3> <p>CDC calls a BMI of 18.5 to 24.9 healthy weight '
    f'({a("cdc_cat", "CDC")}); our <a href="/blog/healthy-bmi-range/">healthy BMI range</a> guide goes further. In a pooled '
    'analysis of 239 studies, all-cause mortality was lowest at a BMI of 20 to 25 '
    f'({a("gbmc", "Global BMI Mortality Collaboration, 2016")}).</p> '
    '<h3>Overweight Zone (Yellow/Orange - BMI 25-29.9)</h3> <p>A BMI of 25 to 29.9 is overweight '
    f'({a("cdc_cat", "CDC")}). BMI does not distinguish between fat, muscle and bone mass, so a muscular person can fall in '
    'this range, and for individuals CDC says BMI should be considered with other factors, such as blood pressure and '
    f'cholesterol levels ({a("cdc_about", "CDC")}). NIH reads the waist alongside BMI from 25 to 34.9: over 40 in (102 cm) '
    f'for men or 35 in (88 cm) for women marks higher risk ({a("nhlbi", "NHLBI, 1998")}).</p> '
    '<h3>Obese Zone (Red - BMI 30+)</h3> <p>A BMI of 30 or more is obesity, in three classes: 30 to 34.9, 35 to 39.9 and '
    f'40 or more ({a("who00", "WHO, 2000")}). People with obesity are at greater risk for diabetes, high blood pressure, '
    f'cardiovascular disease, stroke and at least 13 types of cancer ({a("nci", "NCI")}). In the Look AHEAD trial of adults '
    'with overweight or obesity and type 2 diabetes, those who lost 5 to 10% of their weight in a year had greater odds of '
    f'better blood sugar, blood pressure, HDL cholesterol and triglycerides ({a("wing", "Wing et al., 2011")}). If you’re '
    f'concerned about your weight, CDC says to talk with your health care provider ({a("cdc_lw", "CDC")}).</p> ')

LIMITS = (
    f'<h2 id="limitations">Limitations of BMI Charts</h2> <p>CDC calls BMI {CDC_Q}, but it does not directly measure body '
    f'fat ({a("cdc_about", "CDC")}).</p> <div class="pros-cons"> <div class="pros-list"> <h3>What BMI Charts Do Well</h3> '
    '<ul> <li>Quick, low-cost screening</li> <li>The same categories for every adult</li> <li>No arithmetic: you look up a '
    'cell</li> </ul> </div> <div class="cons-list"> <h3>What BMI Charts Cannot Do</h3> <ul> <li>Tell fat from muscle and '
    'bone</li> <li>Measure body fat</li> <li>Show where fat sits</li> <li>Allow for age: body fat at the same BMI rises with '
    'age</li> <li>Allow for family background</li> </ul> </div> </div> <p class="source-note">Sources: '
    f'{a("cdc_about", "CDC, About BMI")}; {a("cdc_cat", "CDC, adult categories")}; NIH reads the waist alongside BMI '
    f'({a("nhlbi", "NHLBI, 1998")}); {a("gal", "Gallagher et al., 2000")}; lower thresholds for some family backgrounds '
    f'({a("nice", "NICE NG246")}).</p> '
    '<h3>Who May Be Misclassified by BMI Charts</h3> <p>BMI can misread these groups:</p> ' + UL + ' ' + LI +
    '<strong>Athletes and muscular individuals:</strong> BMI does not distinguish between fat, muscle and bone mass '
    f'({a("cdc_about", "CDC")}), so a very muscular person can reach an overweight or obese BMI; NICE says its '
    f'waist-to-height ratio classes can be used in adults with high muscle mass ({a("nice", "NICE NG246")})</li> ' + LI +
    '<strong>Older adults:</strong> body fat at the same BMI rises with age '
    f'({a("gal", "Gallagher et al., 2000")}), and NICE advises caution in reading BMI at 65 and over '
    f'({a("nice", "NICE NG246")})</li> ' + LI + '<strong>People with a lot of fat around the waist:</strong> in CDC’s '
    '2021–2023 survey, 50.2% of women and 42.9% of men with a healthy BMI had a waist of at least half their height (our '
    f'calculation from {a("nhanes", "CDC NHANES 2021–2023")}); the <a href="/blog/waist-to-height-ratio/">waist-to-height '
    'ratio calculator</a> checks yours</li> ' + LI + '<strong>Asian populations:</strong> a WHO expert consultation found the '
    'share of Asian people at high risk of type 2 diabetes and cardiovascular disease substantial below a BMI of 25, and '
    f'named lower action points ({a("who04", "Lancet, 2004")})</li> ' + LI + '<strong>Black African or African-Caribbean '
    'family background:</strong> NICE uses lower thresholds, overweight from 23 and obesity from 27.5, as for South Asian, '
    f'Chinese, other Asian and Middle Eastern backgrounds ({a("nice", "NICE NG246")})</li> </ul> ')

BLOCKS = [
    ('<h2 id="interpreting-zones">', '<!-- Range Indicator Visual -->', ZONES),
    ('<h2 id="limitations">', '<p>For more on what BMI misses', LIMITS),
]

FAQ = {
    'What do the colors on a BMI chart mean?':
        'BMI charts use color coding to quickly identify weight categories. Blue typically indicates underweight (BMI under '
        '18.5), green shows normal weight (18.5-24.9), yellow or orange represents overweight (25-29.9), and red indicates '
        f'obesity (30+). The categories are CDC’s ({a("cdc_cat", "CDC")}); the exact colours vary from chart to chart.',
    'Are BMI charts different for men and women?':
        'Standard BMI charts use the same categories for both sexes (underweight below 18.5, normal 18.5-24.9, overweight '
        f'25-29.9, obese 30+), as CDC does ({a("cdc_cat", "CDC")}). Women carry more body fat than men at the same BMI: '
        f'{SCANS}. For tailored guidance, see our guides on <a href="/women-bmi-calculator/">BMI for women</a> and '
        '<a href="/men-bmi-calculator/">BMI for men</a>.',
    'Why does my BMI chart show different values than online calculators?':
        'This usually happens due to rounding or unit conversion differences. Charts typically round BMI to whole numbers, '
        'while calculators show one or two decimal places. Also ensure you are using the same units (metric vs imperial) and '
        'that the chart uses the standard BMI formula: weight in kg divided by height in meters squared.',
    'What BMI range is highlighted as healthy on the chart?':
        f'The green or healthy zone on standard BMI charts covers BMI 18.5 to 24.9, which CDC calls healthy weight '
        f'({a("cdc_cat", "CDC")}). In a pooled analysis of 239 studies, all-cause mortality was lowest at a BMI of 20 to 25 '
        f'({a("gbmc", "Global BMI Mortality Collaboration, 2016")}). NICE uses lower thresholds for some family backgrounds '
        f'({a("nice", "NICE NG246")}). See our <a href="/blog/healthy-bmi-range/">healthy BMI range</a> guide for more '
        'detail.',
    'How accurate are BMI charts for athletes?':
        f'BMI does not distinguish between fat, muscle and bone mass ({a("cdc_about", "CDC")}), so a muscular athlete can '
        'read as overweight or even obese on a chart. NICE says its waist-to-height ratio classes can be used in adults with '
        f'high muscle mass ({a("nice", "NICE NG246")}); the <a href="/blog/waist-to-height-ratio/">waist-to-height ratio '
        'calculator</a> works yours out.',
}


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
    for old, new in EDITS:
        src = one(src, old, new, PG)
    for start, end, new in BLOCKS:
        src = block(src, start, end, new)
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question">' + re.escape(q) + r'<svg.*?</button> <div class="faq-answer"><p>)'
                         r'(.*?)(</p></div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question">(.*?)<svg.*?</button> <div class="faq-answer"><p>(.*?)</p></div>', src)
    assert len(qa) == 7, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + ' ' + jsonld_block(d) + ' ' + src[fb.end(2):]
    for gone in ('Muscle weighs more than fat', 'potentially too strict', 'skinny fat', 'pre-obese', 'Always consult a qualified',
                 'progressively higher risk', 'Eating disorders, hyperthyroidism', 'to aim for', 'widely used in clinical',
                 'some healthcare providers recommend', 'morning is best', 'Reverse causation', 'chronic disease'):
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
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-chart-explained/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-chart-explained/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
