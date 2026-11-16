#!/usr/bin/env python3
"""CMB-059 CLAIMS-10: claims pass batch 10 (DEVLOG §5 P1) on /blog/bmi-history/ (8 probe hits).
The history itself was sourced in CMB-037/CMB-042; what was left were the lines around it. Each now says what a registry
row says, or went (D-10):
  - intro: "one of the most widely used health metrics in the world" and "reveals why BMI works the way it does" out;
    the 1832 index and the 1972 name (Eknoyan, 2008) in;
  - key takeaways: "Controversy: ... remains the global standard due to simplicity and broad applicability" becomes
    "Why it stuck", Keys and colleagues' own two reasons (Keys et al., 1972);
  - critiques: "growing criticism from researchers, clinicians, and public health advocates" becomes CDC's "quick,
    low-cost, and reliable screening measure" that "does not directly measure body fat"; the six limitation cards say
    what CDC, NICE NG246 (1.9.12 high muscle mass, 1.9.13 aged 65 and over, 1.9.11 lower thresholds), Trefethen and
    Gallagher et al. (2000, Table 4) say, not "vastly different health profiles", "may underestimate fatness in short
    people" (Trefethen's argument, now his) or "Standard cutoffs may not apply equally"; "These limitations trace back
    to BMI's origin" and "provide more meaningful health information" become CDC's line on individuals;
  - "The 'Obesity Paradox'": the label had no source; the h3 now names what Winter et al. (2014) measured;
  - alternatives: "spurred development", "show promise", the five-row table whose "Advantage Over BMI" and "Limitation"
    columns had no source, and "decades of research validating its population-level utility" out; the h3 now points to
    the BMI limitations guide's sourced comparison and the waist-to-height ratio calculator;
  - "The Future of Body Composition Metrics" becomes "Where BMI Stands Now": "The next decade will likely see",
    "Precision Medicine" and "unlikely to disappear soon" out; home devices now carry Burns et al. (2019)'s hand-held
    impedance result; "Will BMI Be Replaced?" answers with WHO's and CDC's adult definitions;
  - FAQ: the medical-standard answer gets its four sources; "BMI persists because ..." and "The medical community
    increasingly recommends" become Keys's reasons, CDC's two lines and the NIH and NICE waist pairings; the Trefethen
    answer gets its link. FAQPage JSON-LD rebuilt from the six visible answers (it held four);
  - disclaimer: "Always consult a qualified healthcare provider for personalized health assessment" and "Individual
    health status depends on many factors" become CDC's own "when" (§4); the sources list's 1995 entry is WHO's Expert
    Committee (TRS 854), not an Expert Consultation.
dateModified and lastmod follow.
usage: python3 research/cmb-059/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
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
PG, SM = 'blog/bmi-history/index.html', 'sitemap.xml'
BASE = {PG: '2fb730d99568ba8b9fb12bd3cc33d2972d8020b1b64e6afdf7dcac662f11d69b',
        SM: '3c6df32f041ea2ac8cf2735a0a14fff07b94c6b07387af01b3c69aae9d3efc5f'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'eknoyan': 'https://doi.org/10.1093/ndt/gfm517',
    'keys': 'https://doi.org/10.1016/0021-9681(72)90027-6',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'tref': 'https://people.maths.ox.ac.uk/trefethen/bmi.html',
    'gal': 'https://pubmed.ncbi.nlm.nih.gov/10966886/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
    'who_fs': 'https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight',
    'nih85': 'https://pubmed.ncbi.nlm.nih.gov/3840463/',
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'who00': 'https://iris.who.int/handle/10665/42330',
    'nuttall': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4890841/',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


CDC_Q = '“a quick, low-cost, and reliable screening measure”'

EDITS = [
    ('<p class="intro-text">The Body Mass Index has a 200-year history, from a Belgian mathematician\'s statistical curiosity '
     'to one of the most widely used health metrics in the world. Understanding this history reveals why BMI works the way '
     'it does, its original purpose, and why it remains both useful and controversial today.</p>',
     '<p class="intro-text">The body mass index dates from 1832, when Adolphe Quetelet described it; Ancel Keys gave it its '
     f'name in 1972 ({a("eknoyan", "Eknoyan, 2008")}). Its history explains what it was built to measure and where it '
     'stops.</p>'),
    ('<li><strong>Controversy:</strong> Despite known limitations, BMI remains the global standard due to simplicity and '
     'broad applicability</li>',
     '<li><strong>Why it stuck:</strong> Keys and colleagues preferred it for the simple calculation and because it applies '
     f'to all populations at all times ({a("keys", "Keys et al., 1972")})</li>'),
    ('<p>Despite its widespread adoption, BMI has faced growing criticism from researchers, clinicians, and public health '
     'advocates. Understanding these limitations is essential for using BMI appropriately. For an in-depth analysis, see our '
     '<a href="/blog/bmi-limitations/">BMI limitations guide</a>.</p>',
     f'<p>CDC calls BMI {CDC_Q}, but it does not directly measure body fat ({a("cdc_about", "CDC")}). Our '
     '<a href="/blog/bmi-limitations/">BMI limitations guide</a> goes through the evidence.</p>'),
    ('<p>BMI treats all weight equally. A muscular athlete and a sedentary person with high body fat can have identical BMI '
     'values despite vastly different health profiles.</p>',
     f'<p>BMI “does not distinguish between fat, muscle, and bone mass” ({a("cdc_about", "CDC")}). NICE advises '
     f'interpreting it with caution in adults with high muscle mass ({a("nice", "NICE NG246")}).</p>'),
    ('<p>Standard BMI may underestimate fatness in short people and overestimate it in tall people. This was a key '
     'motivation for Trefethen\'s "New BMI" proposal.</p>',
     '<p>Trefethen argues that dividing by height squared makes short people think they are thinner, and tall people '
     f'fatter, than they are ({a("tref", "Trefethen")}); it is why he proposed his “New BMI”.</p>'),
    ('<p>Body composition changes with age. The same BMI at age 30 and 70 has different implications, yet the formula and '
     'cutoffs remain unchanged.</p>',
     f'<p>CDC’s adult categories apply regardless of age ({a("cdc_cat", "CDC")}), but body fat at the same BMI rises with '
     'age: at a BMI of 25, Gallagher and colleagues predicted 20% body fat for African American and white men aged 20 to '
     f'39 and 25% at 60 to 79 ({a("gal", "Gallagher et al., 2000")}, Table 4). NICE advises interpreting BMI with caution '
     f'in people aged 65 and over ({a("nice", "NICE NG246")}).</p>'),
    ('<p>Different ethnic groups have different relationships between BMI and body fat. Standard cutoffs may not apply '
     'equally across all populations.</p>',
     '<p>NICE uses lower thresholds for adults of South Asian, Chinese, other Asian, Middle Eastern, Black African or '
     'African-Caribbean family background, whose cardiometabolic risk occurs at a lower BMI: overweight from 23 and '
     f'obesity from 27.5 ({a("nice", "NICE NG246")}).</p>'),
    ('<p>These limitations trace back to BMI&rsquo;s origin as a population statistic rather than an individual assessment. '
     'For athletes and highly muscular individuals, measures of body composition like DEXA scans, hydrostatic weighing, or '
     'even simple waist circumference provide more meaningful health information. Read more in our '
     '<a href="/blog/bmi-limitations/">BMI accuracy guide</a>.</p>',
     '<p>For individuals, CDC says BMI should be considered with other factors, such as blood pressure and cholesterol '
     f'levels ({a("cdc_about", "CDC")}).</p>'),
    ('<h3>The "Obesity Paradox"</h3> <p>One pattern called the &ldquo;obesity paradox&rdquo; shows up in older adults: '
     'compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 '
     f'({a("winter", "Winter et al., 2014")}).</p>',
     '<h3>BMI and Survival After 65</h3> <p>In a meta-analysis of 197,940 people aged 65 and over, compared with a BMI of '
     f'23 to 23.9, the risk of death was higher below 23 and began to rise above 33 ({a("winter", "Winter et al., 2014")}).</p>'),
    ('<p>The limitations of BMI have spurred development of alternative metrics. While none has replaced BMI as the global '
     'standard, several show promise for specific applications.</p>',
     '<p>The alternatives come in two kinds: another formula from weight and height, and measures that look at the waist '
     'or at fat itself.</p>'),
    ('<li><a href="#future">The Future of Body Composition Metrics</a></li>', '<li><a href="#future">Where BMI Stands Now</a></li>'),
    ('<h2 id="future">The Future of Body Composition Metrics</h2> <p>The next decade will likely see significant changes in '
     'how we assess body composition and weight-related health risk. Several trends are emerging:</p>',
     '<h2 id="future">Where BMI Stands Now</h2>'),
    ('<p>This article is for informational and educational purposes only and does not constitute medical advice. BMI is a '
     'screening tool, not a diagnostic measure. The historical information presented reflects the evolution of medical and '
     'scientific understanding over time. Always consult a qualified healthcare provider for personalized health assessment '
     'and recommendations. Individual health status depends on many factors beyond BMI, including body composition, fitness '
     'level, diet, genetics, and medical history.</p>',
     '<p>This article is for informational and educational purposes only and does not constitute medical advice. BMI is a '
     f'screening tool, not a diagnostic measure. If you’re concerned about your weight, CDC says to talk with your health '
     f'care provider ({a("cdc_lw", "CDC")}).</p>'),
    ('<li>WHO Expert Consultation. (1995). <em>Physical s', '<li>WHO Expert Committee. (1995). <em>Physical s'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

BLOCKS = [
    ('<h3>Other Alternative Metrics</h3>', '<!-- Future Section -->',
     '<h3>Other Measures</h3> <p>Our <a href="/blog/bmi-limitations/">BMI limitations guide</a> compares the measures used '
     'beside BMI, from waist circumference to DXA scans, each with its source, and the '
     '<a href="/blog/waist-to-height-ratio/">waist-to-height ratio calculator</a> works out one of them.</p> '),
    ('<h3>Technology-Enabled Assessment</h3>', '<p style="text-align: center; margin: 2rem 0;">',
     '<h3>Home Body Fat Devices</h3> <p>Body fat scales and hand-held devices estimate body fat by bioelectrical impedance. '
     'In a study of 437 college students, a hand-held impedance device was 4.9 points off a DXA scan on average '
     f'({a("burns", "Burns et al., 2019")}); our guide on <a href="/blog/how-to-measure-body-fat/">how to measure body '
     'fat</a> compares the methods.</p> <h3>Will BMI Be Replaced?</h3> <p>Not so far: WHO and CDC still define adult '
     f'overweight and obesity by BMI ({a("who_fs", "WHO")}; {a("cdc_cat", "CDC")}).</p> '),
]

FAQ = {
    'When did BMI become a medical standard?':
        f'In stages. In 1985 an NIH consensus conference recommended wider use of BMI ({a("nih85", "NIH, 1985")}). NIH’s '
        '1998 guidelines then set overweight at a BMI of 25 to 29.9 and obesity at 30 or more '
        f'({a("nhlbi", "NHLBI, 1998")}). WHO’s 2000 report set the obesity classes used today ({a("who00", "WHO, 2000")}). '
        'Earlier weight standards came from insurers, such as Metropolitan Life’s 1959 tables of desirable weights '
        f'({a("nuttall", "Nuttall, 2015")}).',
    'Why is BMI still used despite its known limitations?':
        'Keys and colleagues preferred it in 1972 for the simple calculation and because, unlike percentage of average '
        f'weight, it applies to all populations at all times ({a("keys", "Keys et al., 1972")}). CDC calls it {CDC_Q} and '
        'says that for individuals it should be considered with other factors, such as blood pressure and cholesterol '
        f'levels ({a("cdc_about", "CDC")}). Guidelines pair it with a waist measure: NIH’s 1998 guidelines with waist '
        f'circumference, NICE with the waist-to-height ratio ({a("nhlbi", "NHLBI, 1998")}; {a("nice", "NICE NG246")}).',
    'What is Trefethen\'s "New BMI" and is it better?':
        'In 2013, Oxford mathematician Nick Trefethen proposed a modified formula: New BMI = 1.3 × weight (kg) / height '
        '(m)^2.5. He argues that the standard BMI makes short people think they are thinner, and tall people fatter, than '
        'they are; he also writes that his formula is not based on epidemiological studies and may not be an improvement '
        f'({a("tref", "Trefethen")}). Try our <a href="/new-bmi-calculator/">New BMI calculator</a> to see how your results '
        'compare.',
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
    assert len(qa) == 6, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + ' ' + jsonld_block(d) + ' ' + src[fb.end(2):]
    for gone in ('growing criticism', 'Precision Medicine', 'The next decade', 'Always consult a qualified',
                 'Obesity Paradox', 'Advantage Over BMI', 'medical community increasingly', 'Controversy:',
                 'WHO Expert Consultation. (1995)', 'widely used health metrics'):
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
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-history/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-history/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
