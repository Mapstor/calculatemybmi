#!/usr/bin/env python3
"""CMB-052 CLAIMS-5: claims pass batch 5 (DEVLOG §5 P1) on /blog/bmi-and-metabolism/ (17 probe hits).
Every sentence now says what a registry row says, or goes (D-10); no protein or other targets of our own (D-06); the
help line is CDC's (§4). Sources: already in the registry (CMB-042) Pontzer 2021, Wang 2010, Volpi 2004, Mifflin 1990,
Roza and Shizgal 1984, Hirode and Wong 2020, Alberti 2009, Caleyachetty 2017, the American Thyroid Association (re-read
in Chrome 2026-11-14 for the thyroid lines); from CMB-050 and CMB-051 NIDDK's Health Risks, NCI, CDC's Steps for Losing
Weight and physical activity page, the Physical Activity Guidelines, CDC's healthy eating page, NIDDK's Body Weight
Planner, Hall 2011, CDC About BMI; new: Fothergill et al. 2016 (PubMed abstract read in Chrome 2026-11-14).
Out: "According to NIDDK, understanding metabolism is essential ...", "Protein has the highest thermic effect",
"diagnosed metabolic disorders account for only a small share of obesity cases", leptin resistance, "metabolic
inflexibility", the NHLBI pointer and "a clinician's call", "This fundamental principle underlies many weight management
strategies", the protein step's clinician line and progressive overload, the age list's hormone, activity, NEAT and
mitochondria lines, "much of the metabolic slowdown is preventable", T3 and T4, the adaptive-thermogenesis, hormone and
NEAT cards, the five "minimize adaptation" tips, the "Evidence-Based Metabolism Boosters" (stress and cortisol, HIIT and
EPOC, crash diets), the FAQ lines on insulin sensitivity and hormones, thermic effect, sleep, supplements, diet breaks and
reverse dieting, the disclaimer's advice, two related-card claims ("better indicator", a target BMI "based on age,
sex"). In: the measured life-course curve, NIDDK and NCI on metabolic markers, NIDDK's metabolic syndrome definition,
CDC on reading BMI with other factors, the guidelines on muscle-strengthening and protein foods, Hall on why loss slows,
Fothergill on lasting adaptation, CDC on keeping weight off, CDC on activity and calories. Title, H1 and URL kept.
Meta descriptions, the Article description, the FAQPage JSON-LD (all four visible answers), dateModified and lastmod
follow. Files are checked by SHA-256 first; every marker must occur once.
usage: python3 research/cmb-052/apply.py [--check]   Run order from main: registry.py, apply.py."""
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
PG, SM = 'blog/bmi-and-metabolism/index.html', 'sitemap.xml'
BASE = {PG: '4782e57c69477c3ad9cdf151f94141ef96843d1bdcc8d313227eb21bc9152895',
        SM: '32ac1fcecc1ac45466abf4be2bab0fca222c6a52f52aa7b04a6854bd6aa0288d'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'ata': 'https://www.thyroid.org/thyroid-and-weight/',
    'pontzer': 'https://pubmed.ncbi.nlm.nih.gov/34385400/',
    'wang': 'https://pubmed.ncbi.nlm.nih.gov/20962155/',
    'volpi': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/',
    'hall': 'https://pubmed.ncbi.nlm.nih.gov/21872751/',
    'fothergill': 'https://pubmed.ncbi.nlm.nih.gov/27136388/',
    'niddk': 'https://www.niddk.nih.gov/health-information/weight-management/adult-overweight-obesity/health-risks',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'cdc_pa': 'https://www.cdc.gov/healthy-weight-growth/physical-activity/index.html',
    'cdc_eat': 'https://www.cdc.gov/healthy-weight-growth/healthy-eating/index.html',
    'pag': ('https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines/'
            'top-10-things-know'),
    'bwp': 'https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


def step(title, body):
    return (f'<div class="numbered-step"> <div class="numbered-step-content"> <h4>{title}</h4> <p>{body}</p> </div> '
            '</div> ')


EDITS = [
    # intro
    ('<p class="intro-text">Your metabolism affects weight management and overall health. Understanding how your metabolic '
     'rate interacts with BMI can help you make informed decisions about diet, exercise, and lifestyle.</p>',
     '<p class="intro-text">Metabolism turns food into energy, and the energy your body uses at rest is the basal metabolic '
     f'rate ({a("ata", "ATA")}). Bigger bodies burn more, not less: total daily energy expenditure rises with fat-free mass '
     f'({a("pontzer", "Pontzer et al., 2021")}). Below: the BMR equations, how BMI relates to metabolic rate and metabolic '
     'health, muscle, age, the thyroid, and what weight loss does to the energy you burn.</p>'),
    ('<li><a href="#boost-metabolism">Boosting Metabolism Naturally</a></li>',
     '<li><a href="#boost-metabolism">Raising the Energy You Burn</a></li>'),
    # key takeaways
    ('<li><strong>Metabolism encompasses all chemical processes</strong> in your body that convert food into energy, '
     'including basal metabolic rate (BMR)</li>',
     '<li><strong>Metabolism</strong> turns food into energy; the energy used at rest is the basal metabolic rate, or BMR '
     f'({a("ata", "ATA")})</li>'),
    ('<li><strong>Higher BMI generally correlates with higher BMR</strong> because larger bodies require more energy to '
     'maintain basic functions</li>',
     '<li><strong>Bigger bodies burn more:</strong> total daily energy expenditure rises with fat-free mass '
     f'({a("pontzer", "Pontzer et al., Science 2021")})</li>'),
    ('<li><strong>Muscle mass is metabolically active:</strong> at rest it uses more energy than the same weight of fat</li>',
     '<li><strong>Muscle is metabolically active:</strong> at rest it uses about 13 kcal per kg a day, against 4.5 for fat '
     f'({a("wang", "Wang et al., 2010")})</li> '
     '<li><strong>Weight loss can lower energy use for years:</strong> six years after “The Biggest Loser”, 14 contestants '
     'burned 499 kcal a day less at rest than their body composition and age predicted '
     f'({a("fothergill", "Fothergill et al., 2016")})</li>'),
    # what is metabolism
    (' According to the <a href="https://www.niddk.nih.gov/health-information/weight-management" target="_blank" '
     'rel="noopener">National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)</a>, understanding metabolism is '
     'essential for effective weight management.</p>', '</p>'),
    ('<p>Energy expended digesting, absorbing, and processing the nutrients in your food. Protein has the highest thermic '
     'effect.</p>', '<p>Energy expended digesting, absorbing, and processing the nutrients in your food.</p>'),
    (' <p>The relationship between metabolism and <a href="/blog/what-is-bmi/">BMI</a> is complex. Many people blame a '
     '&ldquo;slow metabolism&rdquo; for weight gain, but diagnosed metabolic disorders account for only a small share of '
     'obesity cases.</p>', ''),
    (' <p>Larger bodies need more energy to maintain, so absolute energy expenditure rises with body size: the 2021 '
     '<em>Science</em> analysis found total expenditure increases with fat-free mass (<a '
     'href="https://pubmed.ncbi.nlm.nih.gov/34385400/" target="_blank" rel="noopener">Pontzer et al.</a>).</p>', ''),
    # BMI and metabolic rate
    ('<p>The relationship between BMI and metabolic rate is often misunderstood. Many assume that people with obesity have '
     '"slow metabolisms," but individuals with higher body weights typically have higher absolute metabolic rates.</p>',
     '<p>People with a higher <a href="/blog/what-is-bmi/">BMI</a> typically burn more energy in absolute terms, because '
     f'total expenditure rises with fat-free mass ({a("pontzer", "Pontzer et al., 2021")}).</p>'),
    ('<h3>BMI vs. metabolic Health Indicators</h3> <p>While people with higher BMIs burn more total calories, their metabolic '
     'health markers often tell a different story. Elevated BMI is associated with:</p> <ul> <li><strong>Insulin '
     'resistance:</strong> reduced ability to use glucose efficiently</li> <li><strong>Leptin resistance:</strong> '
     'diminished response to satiety hormones</li> <li><strong>Chronic low-grade inflammation:</strong> elevated '
     'inflammatory markers</li> <li><strong>Dyslipidemia:</strong> abnormal blood lipid levels</li> </ul> <p>These factors '
     'contribute to "metabolic inflexibility": the reduced ability to switch between burning carbohydrates and fats for '
     'fuel. This is why <a href="/blog/bmi-and-health-risks/">BMI remains an important health indicator</a> despite its '
     '<a href="/blog/bmi-limitations/">limitations</a>.</p>',
     '<h3>BMI vs. Metabolic Health Indicators</h3> <p>Burning more does not mean healthier markers. Overweight and obesity '
     f'raise the risk of high blood pressure, high blood cholesterol and high blood glucose ({a("niddk", "NIDDK")}), and '
     f'people with obesity often have higher blood levels of insulin and chronic inflammation ({a("nci", "NCI")}). The '
     'risks that go with each BMI range are in <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>; what BMI '
     'misses is in <a href="/blog/bmi-limitations/">BMI limitations</a>.</p>'),
    # metabolic syndrome
    ('<p>The specific diagnostic thresholds for metabolic syndrome (waist, lipids, blood pressure, fasting glucose) and the '
     'assessment itself are a clinician\'s call. See the <a href="https://www.nhlbi.nih.gov/health/metabolic-syndrome" '
     'target="_blank" rel="noopener">NHLBI overview of metabolic syndrome</a> for context. See our <a '
     'href="/blog/how-to-lower-bmi/">how to lower BMI</a> guide for practical, non-prescriptive strategies.</p>',
     '<p>A diagnosis needs at least three of five conditions: a large waist, high triglycerides, high blood pressure, high '
     'fasting blood glucose and low HDL cholesterol. NIDDK says metabolic syndrome is closely linked to overweight and '
     f'obesity and to a lack of physical activity ({a("niddk", "NIDDK")}). Our <a href="/blog/how-to-lower-bmi/">how to '
     'lower BMI</a> guide has CDC’s steps.</p>'),
    # NWMU
    ('<p>Just as some individuals with obesity maintain metabolic health, the reverse is also true. "Normal weight '
     'metabolically unhealthy" (NWMU), colloquially known as "skinny fat", describes individuals with normal BMI who exhibit '
     'metabolic dysfunction.</p>',
     '<p>The reverse group exists too. &ldquo;Normal weight metabolically unhealthy&rdquo; (NWMU), sometimes called '
     '&ldquo;skinny fat&rdquo;, means a BMI in the healthy range with metabolic abnormalities.</p>'),
    ('<p>This phenomenon shows a limitation of BMI as a health assessment tool. Our guide on <a '
     'href="/blog/body-fat-vs-bmi/">body fat vs BMI</a> explores this in detail.</p>',
     '<p>CDC says that for individuals, BMI should be considered with other factors, such as blood pressure and cholesterol '
     f'levels ({a("cdc_about", "CDC")}). Our guide on <a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a> goes further.</p>'),
    # muscle
    ('<p>Muscle tissue is significantly more metabolically active than fat tissue. This fundamental principle underlies many '
     'weight management strategies and explains why body composition matters as much as, or more than, total body '
     'weight.</p>',
     '<p>At rest, a kilogram of skeletal muscle uses about 13 kcal a day and a kilogram of fat about 4.5, in the '
     f'organ-by-organ rates Wang and colleagues validated across adulthood ({a("wang", "Wang et al., 2010")}).</p>'),
    # age
    ('<p>Metabolism changes throughout the lifespan, with significant implications for weight management and BMI. '
     'Understanding these changes can help you adapt your approach to maintain metabolic health as you age.</p>',
     '<p>Pontzer and colleagues measured daily energy expenditure from 8 days to 95 years of age in 29 countries. Adjusted '
     'for fat-free mass, it climbed to about 50% above adult values around age 1, fell slowly to adult levels by about 20, '
     'held steady from 20 to 60, even in pregnancy, and declined after that '
     f'({a("pontzer", "Pontzer et al., 2021")}).</p>'),
    # thyroid
    ('<p>The thyroid gland is central to regulating metabolism. Located in the neck, this butterfly-shaped gland produces '
     'hormones (T3 and T4) that control how quickly your body burns calories and uses energy.</p>',
     '<p>The thyroid, a butterfly-shaped gland in the lower front of the neck, makes hormones the body relies on to use '
     'energy and keep warm. In thyroid disorders, high hormone levels raise the basal metabolic rate and low levels lower it, '
     f'though BMR is only part of the story for weight ({a("ata", "American Thyroid Association")}).</p>'),
    # disclaimer and related cards
    ('<p>This article is for informational purposes only and does not constitute medical advice. The relationship between '
     'BMI, metabolism, and health is complex and individual. Metabolic conditions, thyroid disorders, and weight management '
     'strategies should be discussed with qualified healthcare providers. BMI is a screening tool, not a diagnostic measure. '
     'Always consult a physician before making significant changes to your diet or exercise regimen, especially if you have '
     'existing health conditions.</p>',
     '<p>This article is for information only and is not medical advice. BMI is a screening measure, not a diagnosis; CDC '
     'says that for individuals it should be considered with other factors, such as blood pressure and cholesterol levels '
     f'({a("cdc_about", "CDC")}).</p>'),
    ('<p>Understand how different BMI ranges correlate with various health conditions and disease risks.</p>',
     '<p>The risk of death across the BMI range, and what NIH says about each condition.</p>'),
    ('<p>Learn why body fat percentage may be a better indicator of health than BMI alone.</p>',
     '<p>How body fat percentage and BMI differ, and what each can miss.</p>'),
    ('<p>Evidence-based strategies for achieving and maintaining a healthy BMI range.</p>',
     '<p>CDC’s steps, the eating and activity guidance, and the weight one BMI point is at your height.</p>'),
    ('<p>Define your target BMI based on age, sex, and individual health factors.</p>',
     '<p>What the healthy BMI range is and the healthy weight for your height.</p>'),
    # sources box
    ('<li>National Institute of Diabetes and Digestive and Kidney Diseases. <a '
     'href="https://www.niddk.nih.gov/health-information/weight-management" target="_blank" rel="noopener">Weight '
     'Management</a></li>',
     f'<li>National Institute of Diabetes and Digestive and Kidney Diseases. {a("niddk", "Health Risks of Overweight &amp; Obesity")}.</li>'),
    ('<li>Centers for Disease Control and Prevention. <a href="https://www.cdc.gov/bmi/" target="_blank" '
     'rel="noopener">About BMI</a></li>',
     f'<li>Centers for Disease Control and Prevention. {a("cdc_about", "About BMI")}; {a("cdc_lw", "Steps for Losing Weight")}; '
     f'{a("cdc_pa", "Physical Activity and Your Weight and Health")}; {a("cdc_eat", "Tips for Healthy Eating for a Healthy Weight")}.</li> '
     f'<li>US Department of Health and Human Services. {a("pag", "Physical Activity Guidelines for Americans, 2nd edition")}.</li> '
     f'<li>National Cancer Institute. {a("nci", "Obesity and Cancer")}.</li> '
     f'<li>Hall KD, et al. {a("hall", "Quantification of the effect of energy imbalance on bodyweight")}. Lancet. 2011.</li> '
     f'<li>Fothergill E, et al. {a("fothergill", "Persistent metabolic adaptation 6 years after “The Biggest Loser” competition")}. Obesity. 2016.</li> '
     f'<li>Volpi E, et al. {a("volpi", "Muscle tissue changes with aging")}. Curr Opin Clin Nutr Metab Care. 2004.</li>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

# the sections rebuilt whole (start marker, end marker inclusive) -> new html
BLOCKS = [
    ('<h3>Building Metabolically Active Tissue</h3>', 'our <a href="/blog/bmi-for-athletes/">muscle mass and BMI guide</a>.</p>',
     '<h3>Building and Keeping Muscle</h3> <div class="numbered-steps"> '
     + step('Muscle-Strengthening Activity', 'The Physical Activity Guidelines ask adults for muscle-strengthening activity, '
            f'like lifting weights or doing push-ups, at least 2 days each week ({a("pag", "Physical Activity Guidelines")}), '
            'and CDC counts stronger bones and muscles among the benefits of regular activity '
            f'({a("cdc_pa", "CDC")}).')
     + step('Protein Foods', 'CDC’s healthy eating plan, from the Dietary Guidelines for Americans, includes protein foods '
            'such as seafood, meats, poultry, eggs, beans and peas, soy products, nuts and seeds '
            f'({a("cdc_eat", "CDC")}).')
     + '</div> <p>More on muscle and BMI in our <a href="/blog/bmi-for-athletes/">BMI for athletes</a> guide.</p>'),
    ('<h3>Why Metabolism Slows with Age</h3>', 'explains how BMI is read at different ages.</p>',
     '<h3>Why Energy Use Falls With Age</h3> <p>Muscle mass falls by an estimated '
     f'3&ndash;8% per decade after age 30 ({a("volpi", "Volpi et al., 2004")}), and total daily expenditure rises and '
     f'falls with fat-free mass ({a("pontzer", "Pontzer et al., 2021")}). Our <a href="/age-bmi-calculator/">BMI by age '
     'guide</a> explains how BMI is read at different ages.</p>'),
    ('<p>One of the most challenging aspects of weight loss is the metabolic adaptation',
     '<li><strong>Get adequate sleep:</strong> Sleep deprivation increases metabolic adaptation</li> </ul>',
     '<p>As weight falls, so does the energy the body burns, so the same intake brings less loss over time; in Hall and '
     'colleagues’ model, half of the eventual change from a new intake comes in about a year '
     f'({a("hall", "Hall 2011")}). Our <a href="/blog/how-to-lower-bmi/">how to lower BMI</a> guide covers the '
     'arithmetic.</p> <h3>Metabolic Adaptation</h3> <p>The drop can be larger than the lost weight explains. In 14 '
     'contestants from &ldquo;The Biggest Loser&rdquo;, who lost 58.3 kg on average in a 30-week competition, resting '
     'metabolic rate six years later was 704 kcal a day below where it started, and 499 kcal a day below what their body '
     'composition and age predicted, although they had regained 41.0 kg on average. The authors call the adaptation '
     'persistent and likely a proportional but incomplete response to efforts to keep weight down '
     f'({a("fothergill", "Fothergill et al., 2016")}).</p> <h3>Keeping Weight Off</h3> <ul> '
     '<li><strong>Gradual loss:</strong> people who lose about 1 to 2 pounds a week are more likely to keep the weight off '
     f'than people who lose weight quicker ({a("cdc_lw", "CDC")})</li> '
     '<li><strong>Regular activity:</strong> most weight loss comes from eating fewer calories, but regular physical '
     f'activity is the only way to maintain it ({a("cdc_pa", "CDC")})</li> '
     f'<li><strong>A plan from your current weight:</strong> NIDDK’s {a("bwp", "Body Weight Planner")} works out calories '
     'and activity to reach a goal weight and keep it</li> </ul>'),
    ('<h2 id="boost-metabolism">Boosting Metabolism Naturally</h2>', '</div> </div> </div> <!-- CTA -->',
     '<h2 id="boost-metabolism">Raising the Energy You Burn</h2> <p>More physical activity raises the number of calories '
     f'your body uses ({a("cdc_pa", "CDC")}); CDC’s calories table, in our <a href="/blog/how-to-lower-bmi/">how to lower '
     'BMI</a> guide, shows how much common activities use. At rest, muscle uses about 13 kcal per kg a day against 4.5 for '
     f'fat ({a("wang", "Wang et al., 2010")}), and the Physical Activity Guidelines ask for muscle-strengthening activity '
     f'at least 2 days each week ({a("pag", "Physical Activity Guidelines for Americans")}).</p> <!-- CTA -->'),
]

FAQ = {
    'Does having a high BMI mean I have a slow metabolism?': (
        'No: bigger bodies burn more energy, and total daily expenditure rises with fat-free mass '
        f'({a("pontzer", "Pontzer et al., 2021")}). What tends to change with a high BMI is metabolic health: overweight and '
        f'obesity raise the risk of high blood pressure, high cholesterol and high blood glucose ({a("niddk", "NIDDK")}). An '
        'underactive thyroid may be behind about 5 to 10 pounds of weight gain for most patients, most of it salt and water '
        f'({a("ata", "American Thyroid Association")}).'),
    'Can I significantly increase my metabolism?': (
        'At rest, muscle makes a small difference per pound: a pound of skeletal muscle uses about 6 calories a day against '
        f'about 2 for a pound of fat (13 vs 4.5 kcal per kg; {a("wang", "Wang et al., 2010")}). Activity uses more: 30 '
        f'minutes of walking at 3.5 mph uses about 140 calories for a 154-pound person ({a("cdc_pa", "CDC")}), and the '
        'Physical Activity Guidelines ask adults for 150 to 300 minutes of moderate-intensity activity a week, plus '
        f'muscle-strengthening activity at least 2 days a week ({a("pag", "Physical Activity Guidelines")}).'),
    'Does losing weight permanently damage metabolism?': (
        'It can lower energy use for years. In 14 “Biggest Loser” contestants, resting metabolic rate six years after the '
        'competition was still 499 kcal a day below what their body composition and age predicted '
        f'({a("fothergill", "Fothergill et al., 2016")}). More generally, as weight falls the body burns less, so the same '
        f'intake brings slower loss ({a("hall", "Hall 2011")}).'),
}

DESC_OLD = ('Comprehensive guide to BMI and metabolism. Learn how metabolic rate affects weight, understand metabolic syndrome, '
            'BMR formulas, and whether you can be metabolically healthy at any weight.')
DESC_NEW = ('How BMI relates to metabolic rate: the BMR equations, metabolic syndrome, muscle, age, the thyroid, and what '
            'weight loss does to the energy you burn.')
META = [
    (f'<meta name="description" content="{DESC_OLD}">', f'<meta name="description" content="{DESC_NEW}">'),
    ('<meta property="og:description" content="Learn how BMI relates to metabolic rate, metabolic syndrome, and whether you '
     'can be metabolically healthy at any weight.">', f'<meta property="og:description" content="{DESC_NEW}">'),
    ('<meta name="twitter:description" content="Learn how BMI relates to metabolic rate, metabolic syndrome, and whether you '
     'can be metabolically healthy at any weight.">', f'<meta name="twitter:description" content="{DESC_NEW}">'),
    ('"description": "Comprehensive guide to understanding the relationship between BMI and metabolism, including metabolic '
     'rate, metabolic syndrome, and metabolically healthy obesity."', f'"description": "{DESC_NEW}"'),
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
    for start, end, new in BLOCKS:
        assert src.count(start) == 1, start[:60]
        i = src.index(start)
        j = src.index(end, i) + len(end)
        src = src[:i] + new + src[j:]
    for old, new in EDITS + META:
        src = one(src, old, new, PG)
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question"> ' + re.escape(q) + r' <svg.*?</button> <div class="faq-answer"> <p>)(.*?)(</p> </div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question"> (.*?) <svg.*?</button> <div class="faq-answer"> <p>(.*?)</p> </div>', src)
    assert len(qa) == 4, len(qa)
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
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-and-metabolism/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-and-metabolism/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
