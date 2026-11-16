#!/usr/bin/env python3
"""CMB-056 CLAIMS-9: claims pass batch 9 (DEVLOG §5 P1) on /blog/waist-to-height-ratio/ (9 probe hits).
The CMB-042 rewrite sourced the page's numbers; what was left are the lines §5 listed (the visceral-fat section, "Works
for muscular individuals", the limitations list) and a few more. Each now says what NIH, NCI, NICE, CDC or a registry
study says, or what CDC's own survey shows (our calculation, as the women's and men's chart pages already print it);
the rest went (D-10). Out: "may be the single best indicator", "dangerous abdominal fat that wraps around your vital
organs", "poses the greatest health risks", "the most metabolically dangerous type", "This is typically at or slightly
above your navel" (the figure says not at the navel), "Directly measures abdominal fat", "Works for muscular
individuals", "Better predictor of cardiovascular risk" (now what Ashwell found), the duplicate "Works the same for men
and women", "Misses skinny fat individuals", "Inaccurate for athletes and elderly", "The effectiveness of WHtR stems from
basic human physiology", the visceral-fat paragraph and its four-item list (cytokines, insulin and cortisol, the portal
vein, triglycerides), "visceral fat can be elevated even in people who appear thin", the estrogen and menopause lines,
the doubled link to the same lowering guide, "an excellent screening tool", "Less useful at extremes", "correlates with
visceral fat", "should not be used to assess pregnant women", "the most comprehensive health assessment", the
disclaimer's "only a qualified healthcare provider" and "personalized recommendations", "Evidence-based strategies", and
"many researchers consider it superior" / "for most people" in the og and twitter descriptions. The h2 and TOC "How to
Improve" become "If Your Ratio Is 0.5 or More". Title and H1 kept (the title's "Calculator" is still §5's open item).
FAQPage JSON-LD rebuilt from the seven visible answers; dateModified and lastmod follow.
usage: python3 research/cmb-056/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
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
PG, SM = 'blog/waist-to-height-ratio/index.html', 'sitemap.xml'
BASE = {PG: '829a999292ce89a886f28019faeb6ffd8501232fbbf6d97aadc4c7e5a3ee77df',
        SM: 'd705d470c6ba72b8ee00605d19dd2a627a9de3a33d6503d24f51536348aea0ae'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'nhlbi': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
    'nice': 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity',
    'ashwell': 'https://pubmed.ncbi.nlm.nih.gov/22106927/',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'nhanes': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


L = {'nhlbi': a('nhlbi', 'NHLBI'), 'nci': a('nci', 'NCI'), 'nice': a('nice', 'NICE NG246'),
     'ashwell': a('ashwell', 'Ashwell et al., 2012'), 'cdc_about': a('cdc_about', 'CDC'),
     'nhanes': a('nhanes', 'CDC NHANES 2021&ndash;2023')}
OG = ('Work out your waist-to-height ratio, the ranges NICE uses, and how it compared with BMI in a meta-analysis of more '
      'than 300,000 adults.')

EDITS = [
    ('<meta property="og:description" content="Calculate your waist-to-height ratio and learn why many researchers consider '
     'it superior to BMI for predicting health risks.">', f'<meta property="og:description" content="{OG}">'),
    ('<meta name="twitter:description" content="Calculate your WHtR and learn why it predicts health risks better than BMI '
     'for most people.">', f'<meta name="twitter:description" content="{OG}">'),
    ('"description": "A comprehensive guide to waist-to-height ratio (WHtR), including how to calculate it, healthy ranges '
     'for men and women, and why research shows it predicts health risks better than BMI."',
     '"description": "How to work out your waist-to-height ratio (WHtR), the ranges NICE uses for men and women, and how it '
     'compared with BMI in pooled studies."'),
    ('<p class="intro-text">Your waist-to-height ratio (WHtR) may be the single best indicator of your cardiometabolic health '
     'risk. This simple calculation - just your waist circumference divided by your height - captures what <a '
     'href="/">BMI</a> misses: dangerous abdominal fat that wraps around your vital organs.</p>',
     '<p class="intro-text">Your waist-to-height ratio (WHtR) is your waist circumference divided by your height. In a '
     'meta-analysis of more than 300,000 adults it beat <a href="/">BMI</a> and waist circumference at detecting '
     'cardiometabolic risk factors ({ashwell}), and it shows what BMI leaves out: where fat sits.</p>'.format(**L)),
    ('<li>Combine WHtR with your <a href="/">BMI calculation</a> for a more complete health picture</li>',
     '<li>NICE pairs the ratio with your <a href="/">BMI</a> for adults with a BMI under 35 ({nice})</li>'.format(**L)),
    ('WHtR specifically targets abdominal obesity - the fat stored around your midsection that poses the greatest health '
     'risks.</p>', 'WHtR looks at the waist, where abdominal fat sits.</p>'),
    ('<p>WHtR captures abdominal fat, the most metabolically dangerous type that surrounds vital organs.</p>',
     '<p>NIH guidelines call excess abdominal fat &ldquo;an important, independent risk factor for disease&rdquo; '
     '({nhlbi}).</p>'.format(**L)),
    ('<li>This is typically at or slightly above your navel</li> ', ''),
    # the comparison lists
    ('<li>Directly measures abdominal fat</li>', '<li>Measures the waist, where abdominal fat sits</li>'),
    ('<li>Works for muscular individuals</li> ', ''),
    ('<li>Better predictor of cardiovascular risk</li>',
     '<li>Beat BMI at detecting cardiometabolic risk factors in a meta-analysis ({ashwell})</li>'.format(**L)),
    ('<li>Works the same for men and women</li> ', ''),
    ('<li>Cannot distinguish muscle from fat</li>',
     '<li>Does not distinguish between fat, muscle and bone mass ({cdc_about})</li>'.format(**L)),
    ('<li>Misses "skinny fat" individuals</li> ', ''),
    ('<li>Inaccurate for athletes and elderly</li> ', ''),
    # the science and visceral fat
    ('<p>The effectiveness of WHtR stems from basic human physiology: where you store fat matters enormously for health, and '
     'waist circumference is the best simple proxy for the most dangerous fat deposits.</p>',
     '<p>NIH guidelines note that waist circumference correlates with the amount of fat in the abdomen ({nhlbi}); the '
     'ratio scales that measurement by height.</p>'.format(**L)),
    ('<p>Unlike <a href="/blog/body-fat-vs-bmi/">total body fat percentage</a>, visceral fat can be elevated even in people '
     'who appear thin. This is why waist circumference - and by extension, WHtR - captures health risks that BMI and even '
     'body fat scales can miss.</p>',
     '<p>A healthy BMI is no guarantee of a smaller waist: among US adults with a BMI of 18.5 to 24.9, 50.2% of women and '
     '42.9% of men have a waist at least half their height (our calculation from {nhanes}). For body fat as a whole, see <a '
     'href="/blog/body-fat-vs-bmi/">body fat percentage vs. BMI</a>.</p>'.format(**L)),
    # limitations
    ('<p>While WHtR is an excellent screening tool, it\'s not perfect. Understanding its limitations helps you use it '
     'appropriately:</p>', '<p>What the ratio can&rsquo;t do:</p>'),
    ('<li><strong>Not a diagnostic tool:</strong> Like BMI, WHtR is a screening metric, not a medical diagnosis. Elevated '
     'WHtR indicates increased risk but doesn\'t confirm disease.</li>',
     '<li><strong>Not a diagnosis:</strong> NICE classes a ratio of 0.5 or more as increased central adiposity, a reason to '
     'seek further assessment, not a diagnosis ({nice}).</li>'.format(**L)),
    ('<li><strong>Measurement variation:</strong> Waist circumference can vary with breathing, time of day, and measurement '
     'technique. Consistency is important for tracking changes.</li>',
     '<li><strong>Measurement:</strong> the number depends on where the tape sits and whether you&rsquo;re breathing in; '
     'measure at the same spot, after breathing out, each time.</li>'),
    ('<li><strong>Less useful at extremes:</strong> For very tall or very short individuals, the ratio may be less '
     'predictive.</li> ', ''),
    ('<li><strong>Doesn\'t distinguish fat types:</strong> While WHtR correlates with visceral fat, it can\'t differentiate '
     'between visceral and subcutaneous abdominal fat.</li>',
     '<li><strong>Fat type:</strong> a tape measure can&rsquo;t tell visceral fat from the fat just under the skin.</li>'),
    ('<li><strong>Not useful during pregnancy:</strong> Like BMI, WHtR should not be used to assess pregnant women.</li> ', ''),
    ('<p>For the most comprehensive health assessment, combine WHtR with your BMI, blood pressure, blood lipids, and blood '
     'glucose measurements. No single metric tells the whole story.</p>',
     '<p>NICE uses the ratio as well as BMI for adults with a BMI under 35 ({nice}), and for individuals, CDC says BMI should '
     'be considered with other factors, such as blood pressure, cholesterol levels and a physical examination '
     '({cdc_about}).</p>'.format(**L)),
    # lowering the ratio
    ('<li><a href="#how-to-improve">How to Improve Your Ratio</a></li>',
     '<li><a href="#how-to-improve">If Your Ratio Is 0.5 or More</a></li>'),
    ('<h2 id="how-to-improve">How to Improve Your Waist-to-Height Ratio</h2>',
     '<h2 id="how-to-improve">If Your Ratio Is 0.5 or More</h2>'),
    ('<p>For more detailed guidance on healthy weight management, see our guides on <a href="/blog/how-to-lower-bmi/">'
     'improving your BMI</a> and <a href="/blog/how-to-lower-bmi/">how to lower your BMI</a>.</p>',
     '<p>Our guide to <a href="/blog/how-to-lower-bmi/">lowering your BMI</a> goes through CDC&rsquo;s steps.</p>'),
    # disclaimer and related
    ('<p>The information provided in this article is for educational purposes only and should not be considered medical '
     'advice. Waist-to-height ratio is a screening tool and cannot diagnose medical conditions. Individual health depends on '
     'many factors that only a qualified healthcare provider can assess. NICE suggests',
     '<p>This information is for education only and is not medical advice. Waist-to-height ratio is a screening measure and '
     'cannot diagnose medical conditions. NICE suggests'),
    (' They can provide appropriate testing and personalized recommendations based on your complete health picture.</p>',
     '</p>'),
    ('<p>Evidence-based strategies for healthy weight management that also reduce WHtR.</p>',
     '<p>CDC&rsquo;s steps for losing weight, with the activity guidelines.</p>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

BLOCKS = [
    ('<p>WHtR\'s effectiveness comes from its ability to estimate visceral fat',
     '<p>A healthy BMI is no guarantee of a smaller waist',     # an EDIT above writes this paragraph first
     ('<p>Fat around the waist includes visceral fat, which lies around the internal organs, and subcutaneous fat, just under '
      'the skin. NCI says visceral fat &ldquo;seems to be more dangerous, in terms of disease risks, than overall fat or '
      'subcutaneous fat&rdquo; ({nci}). A tape measure can&rsquo;t tell the two apart.</p> ').format(**L)),
    ('<p>Women typically have lower WHtR values than men at the same fitness level',
     '<!-- Section 8: Children -->',
     ('<p>NICE uses the same boundaries for women and men ({nice}). Most US adults with an overweight BMI are over the line: '
      '95.5% of women and 93.7% of men have a waist at least half their height (our calculation from {nhanes}).</p> ')
     .format(**L)),
]

FAQ = {
    'Where should I measure my waist for WHtR?': (
        'Measure your waist at the midpoint between the bottom of your ribs and the top of your hip bones. Stand upright, '
        'breathe out normally (don\'t suck in), and keep the tape measure snug but not compressing your skin. Measure on '
        'bare skin if possible.'),
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
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/waist-to-height-ratio/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/waist-to-height-ratio/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
