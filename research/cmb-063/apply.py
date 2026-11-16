#!/usr/bin/env python3
"""CMB-063 CLAIMS-14: claims pass batch 14 (DEVLOG §5 P1) on /lean-body-mass/ (7 probe hits). CMB-038 sourced the three
formulas; what was left were the lines round them. Each now says what a registry row says, or went (D-10, D-01, D-06):
  - intro: "critical ... vastly different health profiles ... completely different stories" becomes CDC's line (BMI does
    not distinguish between fat, muscle, and bone mass), and the intro now says the calculator estimates from height,
    weight and sex while a scan measures; the lede's "--" becomes a colon;
  - "Other LBM Formulas": "Each has strengths and limitations ... interpret your results in context" out;
  - "Why Lean Body Mass Matters": "not just an academic number ... fundamentally change" out; metabolism becomes Elia's
    rates as Wang et al. (2010) validated them (13 and 4.5 kcal per kg a day), Katch-McArdle out; drug dosing keeps the
    prescriber line and loses "fat and lean tissue handle many drugs differently" (no row), Caruso et al. (2018) as the
    example; "Athletic Performance" (power-to-weight, "primary training goal") becomes Provencher et al. (2018);
    "Nutritional Needs and Protein Requirements" (probe hits 1 and 2) goes; "Health Assessment" ("worlds apart",
    "essential for setting realistic fitness goals") becomes the same two men on BMI, Gallagher's provisional ranges and
    the Boer estimate, which can't tell them apart;
  - "Methods to Measure Body Composition": "sufficient for general health awareness", "consider getting a DEXA scan" and
    "Consistency ... matters more than the absolute accuracy" become CDC's DXA line and Burns et al. (2019);
  - "How to Improve Your Body Composition" (probe hit 3) becomes "Building and Keeping Lean Mass": "shift the ratio ... in
    your favor", Protein (hit 4) and Progressive overload (no row) out; Resistance training (HHS) and Sleep (Watson) stay;
  - FAQ: "important for determining caloric needs ... far more useful" out; Boer accuracy loses "are recommended" (hit 5)
    and "best used ... for tracking general trends" (a height-and-weight formula can't see a change in build at the same
    weight); "Why is lean body mass more useful than BMI?" becomes "Is ...?", answered measured vs estimated; muscle mass
    loses "largest single component" and "technically" (hit 6); the LBM vs fat-free mass answer (no row) goes; the
    FAQPage JSON-LD is rebuilt from the visible answers;
  - "Trusted Resources" (hit 7, "we recommend these authoritative sources") becomes "Further Reading" with registry URLs:
    CDC About BMI (for cdc.gov/bmi/), the NHANES DXA documentation (for NHLBI, not a row) and the NIDDK planner.
lastmod follows (the page has no dateModified).
usage: python3 research/cmb-063/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
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
PG, SM = 'lean-body-mass/index.html', 'sitemap.xml'
BASE = {PG: '8e8b8f2417a1effbae3bb4ea1f3333b7e020f6172f683b1ef727a4b5fbdd6a6c',
        SM: '532686aba8fc473b67ebc4a3faad5d25bf809a66b1ed99e11bf8a12c145bb5ff'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'dxx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm',
    'wang': 'https://pubmed.ncbi.nlm.nih.gov/20962155/',
    'caruso': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6110034/',
    'provencher': 'https://doi.org/10.1519/JSC.0000000000002449',
    'gallagher': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
    'niddk': 'https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner',
}
H3 = '<h3 style="margin-top:1.25rem;">'


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


EDITS = [
    ('(everything except fat -- muscles, bones, organs, water)', '(everything except fat: muscles, bones, organs, water)'),
    ('This distinction is critical because two people can weigh the same yet have vastly different health profiles. A '
     '<a href="/blog/bmi-for-athletes/">muscular athlete</a> and a sedentary individual may share the same '
     '<a href="/blog/what-is-bmi/">BMI score</a>, but their lean body mass and body fat percentages tell completely '
     'different stories. ',
     f'BMI does not distinguish between fat, muscle, and bone mass ({a("cdc_about", "CDC")}), so a '
     '<a href="/blog/bmi-for-athletes/">muscular athlete</a> and a sedentary person can share a '
     '<a href="/blog/what-is-bmi/">BMI score</a> and differ in how much of their weight is fat. The calculator below '
     'estimates lean body mass from height, weight and sex with the Boer formula; a body scan such as DXA measures it. '),
    ('<p>Several formulas have been developed over the decades to estimate lean body mass from simple anthropometric '
     'measurements. Each has strengths and limitations, and they can produce noticeably different results for the same '
     'individual. Understanding these differences helps you interpret your results in context.</p>',
     '<p>Several formulas estimate lean body mass from height and weight. Boer’s, which this calculator uses, James’s and '
     'Hume’s are below, with what each gives for the same five people.</p>'),
    ('<p>Lean body mass is not just an academic number -- it has practical applications across medicine, fitness, and '
     'nutrition. Understanding your LBM can fundamentally change how you approach health goals, and it provides information '
     'that <a href="/blog/bmi-limitations/">BMI alone cannot capture</a>.</p>',
     '<p>Lean body mass matters for resting energy use, some drug doses and muscular athletes, and when it is measured it shows '
     'differences in build that <a href="/blog/bmi-limitations/">BMI alone can’t</a>.</p>'),
    ('<p>Lean tissue, especially skeletal muscle, is metabolically active &mdash; it consumes more energy at rest than the same '
     'mass of adipose tissue does. This is one reason two people of the same weight can have meaningfully different resting '
     'energy expenditure; body composition is part of the picture. Our <a href="/blog/bmi-and-metabolism/">BMI and '
     'metabolism</a> guide has more. Knowing your LBM lets you estimate basal metabolic rate (BMR) via composition-based '
     'formulas like Katch-McArdle rather than weight-only formulas.</p>',
     '<p>At rest, skeletal muscle uses about 13 kcal per kilogram a day and fat tissue about 4.5, figures from Elia that '
     f'Wang and colleagues found held across adulthood ({a("wang", "Wang et al., 2010")}). A kilogram of muscle at rest '
     'uses about 2.9 times as much as a kilogram of fat. Our <a href="/blog/bmi-and-metabolism/">BMI and metabolism</a> '
     'guide has more.</p>'),
    ('<p>Some drug doses are calculated from lean or ideal body weight rather than total weight, because fat and lean tissue '
     'handle many drugs differently. Which weight to use depends on the drug, so this is a decision for the prescriber.</p>',
     '<p>Some doses are worked out from lean body weight rather than total weight. Caruso and colleagues, for example, '
     'compared the Boer and James formulas for tailoring iodinated contrast injection to lean body weight in patients with '
     f'obesity ({a("caruso", "Caruso et al., 2018")}). Which weight a dose is based on depends on the drug, so it is the '
     'prescriber’s decision.</p>'),
    (H3 + '3. Athletic Performance</h3> <p>For athletes, LBM is a core performance metric. In sports where power-to-weight '
     'ratio matters (cycling, climbing, martial arts weight classes, distance running), maximizing lean mass while minimizing '
     'fat mass is a primary training goal. Tracking body composition can show changes that the scale hides. Our ',
     H3 + '3. Muscular Athletes</h3> <p>BMI can’t tell muscle from fat, so very muscular people can reach an obese BMI with '
     'little body fat. At the NFL Scouting Combine from 2010 to 2016, BMI classed 53.4% of the athletes as obese, against '
     f'8.9% by measured body fat ({a("provencher", "Provencher et al., 2018")}). Our '),
    (H3 + '4. Nutritional Needs and Protein Requirements</h3> <p>Some clinicians express protein needs relative to lean mass '
     'rather than total weight. How much you need depends on age, size, health and activity, so targets are best set with a '
     'clinician or registered dietitian.</p> ', ''),
    (H3 + '5. Health Assessment Beyond Weight</h3> <p>Two people at the same height and weight can have dramatically '
     'different health profiles. A 5\'10" man weighing 190 lbs could be a fit athlete with 15% body fat (LBM of 161.5 lbs) or '
     'a sedentary office worker at 30% body fat (LBM of 133 lbs). Standard <a href="/blog/what-is-bmi/">BMI</a> would '
     'classify both identically, but their metabolic health, cardiovascular risk, and physical capability are worlds apart. '
     'LBM provides the missing context. Understanding your <a href="/blog/body-fat-vs-bmi/">BMI vs. body composition</a> is '
     'essential for setting realistic fitness goals.</p>',
     H3 + '4. Same BMI, Different Build</h3> <p>Take two men, both 5\'10" and 190 lbs, one at 15% body fat (LBM of 161.5 '
     'lbs) and one at 30% (LBM of 133 lbs). <a href="/blog/what-is-bmi/">BMI</a> puts both at 27.3, overweight. If both '
     'are 20 to 39 years old, Gallagher and colleagues’ provisional ranges put 15% body fat within the range that matches a healthy '
     f'BMI (8 to 19.9%) and 30% above the 25% that matches a BMI of 30 ({a("gallagher", "Gallagher et al., 2000")}). The '
     'Boer formula can’t see that difference: from height, weight and sex alone, it gives both men 139.7 lbs of lean mass '
     'and 26.5% body fat. Our <a href="/blog/body-fat-vs-bmi/">BMI vs. body composition</a> guide has more.</p>'),
    ('<p>For most people, a formula-based estimate is sufficient for general health awareness. If you are making medical '
     'decisions, training for competition, or tracking body composition changes precisely, consider getting a DEXA scan as a '
     'baseline, then use less expensive methods (calipers or a lab impedance analyzer; see '
     '<a href="/blog/how-to-measure-body-fat/">how accurate each method is</a>) to track changes over time. Consistency in '
     'method and testing conditions matters more than the absolute accuracy of any single measurement. Learn more about how '
     'different metrics compare in our <a href="/blog/body-fat-vs-bmi/">BMI vs. body composition guide</a>.</p>',
     f'<p>The reference is a DXA scan, which CDC’s {a("dxx", "survey documentation")} calls “the most widely accepted '
     'method of measuring body composition”. Cheaper methods read differently: in a '
     'study of 437 college students, seven-site skinfolds read 1.4 points of body fat below DXA on average and a hand-held '
     f'impedance device 4.9 points below ({a("burns", "Burns et al., 2019")}). If you track body fat, use the same method '
     'each time. Our guide to <a href="/blog/how-to-measure-body-fat/">how accurate each method is</a> compares them, and '
     '<a href="/blog/body-fat-vs-bmi/">BMI vs. body composition</a> shows how the numbers relate.</p>'),
    ('<h2>How to Improve Your Body Composition</h2> <p>The goal is not just to lose weight but to shift the ratio between lean '
     'mass and fat mass in your favor. For general guidance on reaching a healthier weight, see our '
     '<a href="/blog/how-to-lower-bmi/">guide to lowering BMI</a>.</p>',
     '<h2>Building and Keeping Lean Mass</h2> <p>For reaching a healthier weight in general, see our '
     '<a href="/blog/how-to-lower-bmi/">guide to lowering BMI</a>.</p>'),
    (H3 + 'Protein</h3> <p>Protein supplies the amino acids muscle needs for repair and growth. How much you need depends on '
     'your age, size, health and activity, so individual targets are best set with a clinician or registered dietitian.</p> '
     + H3 + 'Progressive overload</h3> <p>Muscles adapt to a steady workload, so strength training typically increases the '
     'challenge gradually over time, for example by adding weight, repetitions or sets.</p> ', ''),
    ('<button class="faq-question">Why is lean body mass more useful than BMI?<svg',
     '<button class="faq-question">Is lean body mass more useful than BMI?<svg'),
    ('<h2>Trusted Resources</h2> <p>For further reading on body composition, lean body mass, and health assessment methods, '
     'we recommend these authoritative sources:</p> <ul> <li><a href="https://www.cdc.gov/bmi/" ' + EXT + '>CDC: Body Mass '
     'Index</a> -- Centers for Disease Control and Prevention BMI resources and guidance</li> <li><a '
     'href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" ' + EXT + '>NIH NHLBI: Overweight and Obesity</a> -- '
     'National Heart, Lung, and Blood Institute guidance on body weight</li> <li><a href="' + U['niddk'] + '" ' + EXT +
     '>NIH Body Weight Planner</a> -- NIDDK tool for calorie and physical activity plans to reach a goal weight</li> </ul>',
     f'<h2>Further Reading</h2> <ul> <li>{a("cdc_about", "About Body Mass Index")} (CDC): what BMI measures and what it '
     f'doesn’t</li> <li>{a("dxx", "DXA body composition documentation")} (CDC NHANES): how CDC’s national survey '
     f'measured body fat and lean mass by DXA</li> <li>{a("niddk", "Body Weight Planner")} (NIDDK): a tool for calorie '
     'and physical activity plans to reach a goal weight</li> </ul>'),
]

BLOCKS = [
    ('<div class="faq-item"> <button class="faq-question">What\'s the difference between LBM and fat-free mass?',
     '</div> </section> <!-- External Resources -->', ''),
]

FAQ = {
    'What is lean body mass?':
        'Lean body mass (LBM) is your <strong>total body weight minus all fat weight</strong>. It includes muscles, bones, '
        'organs, skin, blood, and water: everything that isn\'t stored body fat. For example, a 180-pound man with 20% body '
        'fat has an LBM of 144 pounds and 36 pounds of fat.',
    'How accurate is the Boer formula?':
        'The Boer formula is a <strong>population-based estimate</strong>: it predicts lean body mass from height, weight and '
        'sex only, so two people who match on all three get the same result whatever their build. A DXA scan measures lean '
        f'mass instead; {a("dxx", "CDC")} calls DXA the most widely accepted method of measuring body composition.',
    'Is lean body mass more useful than BMI?':
        '<strong>Measured, it tells you more; estimated from height and weight, it doesn’t.</strong> BMI does not '
        f'distinguish between fat, muscle, and bone mass ({a("cdc_about", "CDC")}), and a scan that measures lean mass does. '
        'A formula estimate, this calculator’s included, starts from the same height and weight as BMI, so it can’t separate '
        'a muscular person from one with more fat at the same size. As a screening measure, BMI is quick, low-cost, and '
        'reliable in CDC’s words; our <a href="/">standard BMI calculator</a> works it out.',
    'Is lean body mass the same as muscle mass?':
        'No, lean body mass and muscle mass are <strong>related but not identical</strong>. LBM includes everything in your '
        'body that is not fat: skeletal muscle, smooth muscle (in organs), cardiac muscle, bones, connective tissue, organs, '
        'blood, skin, and water. When people talk about "gaining lean mass," they usually mean muscle, but LBM also rises '
        'with more bone or body water. The Boer formula estimates total LBM only and can\'t split it into muscle, bone and '
        'the rest.',
}


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()


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
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question">' + re.escape(q) + r'<svg.*?</button> <div class="faq-answer"><p>)'
                         r'(.*?)(</p></div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question">(.*?)<svg.*?</button> <div class="faq-answer"><p>(.*?)</p></div>', src)
    assert len(qa) == 5, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = [b for b in blocks if '"FAQPage"' in b.group(2)]
    assert len(fb) == 1, len(fb)
    fb = fb[0]
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + json.dumps(d, ensure_ascii=False) + src[fb.end(2):]
    main = src.split('<main', 1)[1].split('</main>')[0]
    for gone in ('This distinction is critical', 'strengths and limitations', 'not just an academic', 'Katch-McArdle',
                 'core performance metric', 'Nutritional Needs', 'worlds apart', 'realistic fitness goals',
                 'sufficient for general', 'Improve Your Body Composition', 'in your favor', 'Progressive overload',
                 'registered dietitian', 'are recommended', 'technically LBM', 'fat-free mass', 'we recommend',
                 'nhlbi.nih.gov', 'href="https://www.cdc.gov/bmi/"', 'far more useful', 'largest single component',
                 'Trusted Resources', 'handle many drugs', 'fit athlete', 'tracking general trends', ' -- '):
        assert gone not in main, f'"{gone}" is left in main'
    assert '"FAQPage"' in src and 'fat-free mass' not in src
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
            src = one(src, '<url><loc>https://calculatemybmi.net/lean-body-mass/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/lean-body-mass/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
