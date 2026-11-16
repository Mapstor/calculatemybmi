#!/usr/bin/env python3
"""CMB-053 CLAIMS-6: claims pass batch 6 (DEVLOG §5 P1) on /about/ (13 probe hits).
The About page's own claims about BMI now say what CDC, GBMC and NCI say (D-10); its doctor lines are CDC's own "when"
(§4); its claims about the site match the site as it is now. Out: "Free, evidence-based", "recommended by WHO, CDC and
NHLBI as a first-line screening metric", "It is not a substitute for a clinician", "All formulas are sourced from
peer-reviewed research and established clinical standards", "the universally recognized WHO formula", the women's
"menopause" notes (gone since CMB-017), "decade-specific guidance", "following pediatric clinical guidelines", "Essential
for understanding body composition ... fitness tracking and nutritional planning", "peer-reviewed formula ... used in
clinical practice", the organisations list (an unlinked WHO fact sheet, NHLBI's overview page) and its "most often linked"
claim, ACOG and Flegal 2013 in the sourcing line (no live page links either), three "qualified clinician / healthcare
provider" lines, "one of the most widely used", "Universally recognised", "Decades of epidemiological research", "a prompt
for further evaluation", "take the results to your own healthcare provider", "the site presents established science" and
"evidence-based" in the bio and its Person JSON-LD. In: CDC About BMI (screening measure; quick and simple, inexpensive,
noninvasive next to direct measures of body fat; fat, muscle and bone; read with other factors), CDC's provider line,
GBMC 2016 and NCI on risk, WHO 2000 for the classification, the body fat calculator (the site has nine calculators; the
page listed eight) and the seven sources linked from the most pages (counted 2026-11-16, /about/ left out). Title, H1
and URL kept; the bio's facts kept. Meta descriptions, the AboutPage description, the FAQPage JSON-LD (all seven visible
answers), dateModified and lastmod follow. The same Person description on four other pages (blog/bmi-for-athletes,
blog/what-is-bmi, obesity-rate-by-state, childhood-obesity-statistics) waits for each page's own batch, so their lastmod
moves with a real edit. Files are checked by SHA-256 first; every marker must occur once.
usage: python3 research/cmb-053/apply.py [--check]   Run order from main: registry.py, apply.py."""
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
PG, SM = 'about/index.html', 'sitemap.xml'
BASE = {PG: '033b9a5f8c8b22c38816bb2626a8c9e43c206d62317b368cf33d3b589edb568b',
        SM: 'c4f955b093d2fd929c19f2fb630115cfee325611281a1e9b1261af9ccc691e53'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'cdc_cats': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_child': 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html',
    'cdc_lw': 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html',
    'cdc_calc': 'https://www.cdc.gov/growth-chart-training/hcp/using-bmi/calculating-bmi.html',
    'nchs508': 'https://www.cdc.gov/nchs/products/databriefs/db508.htm',
    'nhlbi98': 'https://www.ncbi.nlm.nih.gov/books/NBK2003/',
    'who2000': 'https://pubmed.ncbi.nlm.nih.gov/11234459/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'nci': 'https://www.cancer.gov/about-cancer/causes-prevention/risk/obesity/obesity-fact-sheet',
}


def a(key, text, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a href="{U[key]}" {EXT}{c}>{text}</a>'


CDC_LIMITS = ('it does not distinguish between fat, muscle and bone mass, and for individuals it should be considered with '
              'other factors, such as blood pressure, cholesterol levels and a physical examination '
              f'({a("cdc_about", "CDC")})')
CDC_PROVIDER = ('If you’re concerned about your weight or have questions about your medications, CDC says to talk with your '
                f'health care provider ({a("cdc_lw", "CDC")}).')

EDITS = [
    ('Free, evidence-based BMI and body composition calculators. Built and maintained by Marko Visic, MPharm, and operated '
     'by Moving Data Systems d.o.o.',
     'Free BMI and body composition calculators, each built on a cited formula. Built and maintained by Marko Visic, MPharm, '
     'and operated by Moving Data Systems d.o.o.'),
    ('He builds evidence-based health calculators and writes the guides on this site.',
     'He builds health calculators on published formulas and writes the guides on this site.'),
    ('Body Mass Index is recommended by the World Health Organization (WHO), the Centers for Disease Control and Prevention '
     '(CDC), and the <a href="https://www.nhlbi.nih.gov/calculate-your-bmi" target="_blank" rel="noopener">National Heart, '
     'Lung, and Blood Institute (NHLBI)</a> as a first-line screening metric, but many people have never calculated their BMI '
     'or seen it interpreted in context.</p>',
     'CDC calls Body Mass Index “a quick, low-cost, and reliable screening measure” for underweight, overweight or obesity '
     f'({a("cdc_about", "CDC")}).</p>'),
    ('plus <a href="/ideal-weight/">ideal weight</a>, <a href="/lean-body-mass/">lean body mass</a>, and Nick '
     'Trefethen&rsquo;s <a href="/new-bmi-calculator/">New BMI</a> proposal.</p>',
     'plus <a href="/ideal-weight/">ideal weight</a>, <a href="/lean-body-mass/">lean body mass</a>, <a '
     'href="/body-fat-calculator/">body fat</a> and Nick Trefethen&rsquo;s <a href="/new-bmi-calculator/">New BMI</a> '
     'proposal.</p>'),
    ('and (3) help readers prepare more informed conversations with their own healthcare providers. It is not a substitute '
     'for a clinician.</p>',
     'and (3) show the source behind every number.</p>'),
    ('<h3>Evidence-Based</h3> <p>All formulas are sourced from peer-reviewed research and established clinical '
     'standards.</p>',
     '<h3>Cited Formulas</h3> <p>Each calculator names the source of its formula on its own page: CDC and WHO for BMI, the '
     'original authors for the other equations.</p>'),
    ('<p>Calculate your Body Mass Index using the universally recognized WHO formula. Enter your height and weight to '
     'receive an instant BMI classification with a detailed breakdown of what your result means for your health.</p>',
     '<p>Calculates your BMI from height and weight and places it in the WHO and CDC adult categories, with what your '
     'result means.</p>'),
    ('<p>The standard adult BMI with context for women: the NIH waist cut-off, body fat tools, and notes on pregnancy and '
     'menopause.</p>',
     '<p>The standard adult BMI with context for women: where your result ranks among US women, waist size, body fat at the '
     'same BMI and BMI in pregnancy.</p>'),
    (' Provides decade-specific guidance from young adults through older age.</p>',
     ' It also gives average BMI, weight and waist for US adults by age group.</p>'),
    ('Results are presented as age- and sex-specific percentile rankings rather than fixed adult categories, following '
     'pediatric clinical guidelines.</p>',
     'Results are age- and sex-specific percentiles, read in CDC&rsquo;s child and teen categories rather than the adult '
     'ones.</p>'),
    ('<p>Estimates your lean body mass (total weight minus fat weight) using the Boer, James, and Hume formulas. Essential for '
     'understanding body composition beyond what BMI alone can reveal, particularly useful for fitness tracking and '
     'nutritional planning.</p> </div>',
     '<p>Estimates your lean body mass (total weight minus fat weight) with the Boer, James and Hume formulas.</p> </div> '
     '<div class="suite-card"> <h3><a href="/body-fat-calculator/">Body Fat Calculator</a></h3> <p>Estimates body fat '
     'percentage four ways: the Navy tape method, relative fat mass from waist and height, the Deurenberg formula and skinfold '
     'calipers, with how close each gets to a DXA scan.</p> </div>'),
    ('<p>Every calculator on CalculateMyBMI.net implements a peer-reviewed formula or classification system used in clinical '
     'practice. Nothing on this site is an original method; the tools implement equations that have been in the medical '
     'literature for years or decades.</p>',
     '<p>Every calculator on CalculateMyBMI.net implements a published formula or classification, and its page names the '
     'source. Nothing on this site is an original method.</p>'),
    ('Obese Class I (30.0&ndash;34.9), Obese Class II (35.0&ndash;39.9), and Obese Class III (&ge;40.0).</li>',
     'Obese Class I (30.0&ndash;34.9), Obese Class II (35.0&ndash;39.9), and Obese Class III (&ge;40.0) '
     f'({a("who2000", "WHO, 2000")}).</li>'),
    ('the <a href="/lean-body-mass/">lean body mass calculator</a> gives the source of each.</li> </ul>',
     'the <a href="/lean-body-mass/">lean body mass calculator</a> gives the source of each.</li> <li><strong>Body Fat '
     'Formulas:</strong> the Navy tape equations (Hodgdon and Beckett), relative fat mass, the Deurenberg formula and '
     'Jackson&ndash;Pollock skinfolds; the <a href="/body-fat-calculator/">body fat calculator</a> gives the source of '
     'each.</li> </ul>'),
    ('<h3>Organisations referenced across the site</h3> <p style="color:var(--gray-600);font-size:0.9375rem;">This is not a '
     'global citation list: each guide and calculator page carries its own inline references. The following organisations '
     'are the ones most often linked to for classification standards, clinical thresholds, and background context:</p>',
     '<h3>Sources cited most often</h3> <p style="color:var(--gray-600);font-size:0.9375rem;">This is not a global citation '
     'list: each guide and calculator page carries its own inline references. These seven sources are linked from the most '
     'pages:</p>'),
    ('<div style="margin: 1rem 0;"> WHO obesity fact sheet <a href="https://www.cdc.gov/bmi/about/index.html" '
     'target="_blank" rel="noopener" class="source-ref">CDC adult BMI</a> <a href="https://www.cdc.gov/growthcharts/" '
     'target="_blank" rel="noopener" class="source-ref">CDC growth charts (pediatric)</a> <a '
     'href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" target="_blank" rel="noopener" class="source-ref">NHLBI '
     'overweight and obesity</a>  <a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener" '
     'class="source-ref">Winter 2014 meta-analysis (older adults)</a> </div>',
     '<div style="margin: 1rem 0;"> ' + ' '.join([
         a('cdc_cats', 'CDC adult BMI categories', 'source-ref'), a('cdc_about', 'CDC About Body Mass Index', 'source-ref'),
         a('winter', 'Winter 2014 meta-analysis (older adults)', 'source-ref'),
         a('nchs508', 'NCHS adult obesity data, 2021–2023', 'source-ref'),
         a('cdc_child', 'CDC child and teen BMI categories', 'source-ref'),
         a('cdc_calc', 'CDC: calculating BMI', 'source-ref'),
         a('nhlbi98', 'NIH clinical guidelines, 1998', 'source-ref')]) + ' </div>'),
    ('<p>Every quantitative claim on the site is either linked to an institutional source (WHO, CDC, NHLBI, NIH, ACOG) or a '
     'specific paper (Flegal 2013, Winter 2014, Trefethen 2013, and the ideal-weight and lean-body-mass equations by their '
     'original authors).',
     '<p>Every quantitative claim on the site is linked to an institutional source (CDC, NIH, WHO and others) or to a '
     'specific paper (for example Winter 2014, Trefethen 2013, and the ideal-weight, lean-body-mass and body-fat equations '
     'by their original authors).'),
    ('It does not cover medical treatment content: medication choices, bariatric surgery decisions, or clinical diagnostic '
     'thresholds. Those belong with a qualified clinician.</p>',
     'It does not cover medical treatment: medicines, bariatric surgery or clinical diagnosis.</p>'),
    ('<p>The calculators and content on CalculateMyBMI.net are provided for informational and educational purposes only. They '
     'are not a substitute for professional medical advice, diagnosis, or treatment. BMI is a screening tool, not a diagnostic '
     'measure. It does not account for muscle mass, bone density, ethnic differences, or individual health conditions. '
     'Consult a qualified healthcare provider before making decisions about your health, diet, or exercise based on your BMI '
     'or any other metric.</p>',
     '<p>The calculators and content on CalculateMyBMI.net are for information only and are not medical advice, diagnosis '
     f'or treatment. {CDC_PROVIDER}</p>'),
    ('<p>Despite its limitations, BMI remains one of the most widely used weight screening tools. It is:</p> <ul> '
     '<li><strong>Universally recognised:</strong> BMI is used by the WHO and CDC as a first-line screening tool.</li> '
     '<li><strong>Simple and accessible:</strong> It needs only two measurements, height and weight, which makes it practical '
     'in clinical settings, population studies, and self-tracking alike.</li> <li><strong>Extensively studied:</strong> '
     'Decades of epidemiological research have documented associations between BMI ranges and outcomes including '
     'cardiovascular disease, type 2 diabetes, and certain cancers.</li> <li><strong>A screening prompt, not a '
     'diagnosis:</strong> A BMI outside the healthy range is a prompt for further evaluation (body-fat percentage, waist '
     'circumference, blood panels), not a diagnosis in itself.</li> <li><strong>Free and immediate:</strong> Unlike blood '
     'tests, DEXA scans, or clinical evaluations, BMI can be calculated instantly at no cost.</li> </ul>',
     '<p>Why BMI is used, and where it stops:</p> <ul> '
     '<li><strong>Simple:</strong> it needs only height and weight. Compared with direct measures of body fat, CDC lists it '
     f'as quick and simple to calculate, inexpensive and noninvasive ({a("cdc_about", "CDC")}).</li> '
     '<li><strong>Studied at scale:</strong> in pooled data from 239 studies, the risk of death was lowest at a BMI of 20.0 '
     f'to 24.9 and higher above and below that range ({a("gbmc", "GBMC, 2016")}). NCI says people with overweight or '
     'obesity are at greater risk of diabetes, high blood pressure, cardiovascular disease, stroke and at least 13 types of '
     f'cancer ({a("nci", "NCI")}).</li> '
     f'<li><strong>A screening measure, not a diagnosis:</strong> {CDC_LIMITS}.</li> </ul>'),
    ('<p>Read BMI as one piece of a larger health picture. Consider it alongside a <a href="/lean-body-mass/">lean body '
     'mass</a> estimate and an <a href="/ideal-weight/">ideal weight</a> target range, and take the results to your own '
     'healthcare provider for interpretation.',
     '<p>Read BMI as one piece of a larger picture: the <a href="/lean-body-mass/">lean body mass</a>, <a '
     'href="/body-fat-calculator/">body fat</a> and <a href="/ideal-weight/">ideal weight</a> calculators add three more.'),
    ('"description": "Marko Visic, MPharm, builds evidence-based BMI and body composition calculators. CalculateMyBMI.net is '
     'operated by Moving Data Systems d.o.o."',
     '"description": "Marko Visic, MPharm, builds BMI and body composition calculators, each on a cited formula. '
     'CalculateMyBMI.net is operated by Moving Data Systems d.o.o."'),
    ('"description": "Pharmacist by training (MPharm) with a BSc in Physics, both from the University of Ljubljana. Builds '
     'evidence-based BMI and body composition calculators."',
     '"description": "Pharmacist by training (MPharm) with a BSc in Physics, both from the University of Ljubljana. Builds '
     'BMI and body composition calculators on published formulas."'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

FAQ = {
    'Is this BMI calculator accurate?': (
        'The calculators implement published formulas: the standard BMI formula (weight in kilograms divided by height in '
        'metres squared), the CDC growth-chart percentile method for children, Nick Trefethen’s 2013 New BMI proposal, the '
        'Devine/Robinson/Miller/Hamwi ideal-weight equations, the Boer/James/Hume lean-body-mass equations and four body-fat '
        'methods. BMI itself has limits: CDC notes that it does not distinguish between fat, muscle and bone mass '
        f'({a("cdc_about", "CDC")}).'),
    'Who created these calculators?': (
        'The site is built and maintained by <a href="#author-bio">Marko Visic, MPharm</a>, and operated by Moving Data '
        'Systems d.o.o. The calculators implement published formulas (Devine, Robinson, Miller, Hamwi for ideal weight; '
        'Boer, James, Hume for lean body mass; the Navy, relative fat mass, Deurenberg and Jackson–Pollock equations for body '
        'fat; the Quetelet formula for BMI; Trefethen 2013 for New BMI) and cite institutional guidance from CDC, NIH, WHO '
        'and other bodies. No original methodology is introduced.'),
    'Can I use these results for medical decisions?': (
        'No. The results are for information only: for individuals, CDC says BMI should be considered with other factors, '
        f'such as blood pressure, cholesterol levels and a physical examination ({a("cdc_about", "CDC")}). {CDC_PROVIDER}'),
    'What makes your calculators different from others online?': (
        'There are nine calculators for different people and uses (women, men, by age, pediatric, New BMI, ideal weight, '
        'lean body mass, body fat). Each supports imperial and metric units, runs in your '
        'browser and links to the source behind its numbers. The <a href="/blog/">guides section</a> covers the underlying '
        'science, the limits of BMI and how to read your result alongside other measures.'),
}

DESC_NEW = ('Who builds CalculateMyBMI.net, the nine calculators and the sources behind them, how pages are sourced, and what '
            'happens to your data.')
META = [
    ('<meta name="description" content="Learn about CalculateMyBMI.net, our mission to provide free, evidence-based BMI and '
     'body composition calculators, our methodology, editorial standards, and commitment to user privacy.">',
     f'<meta name="description" content="{DESC_NEW}">'),
    ('<meta property="og:description" content="Learn about our mission to provide free, evidence-based BMI and body '
     'composition calculators accessible to everyone worldwide.">', f'<meta property="og:description" content="{DESC_NEW}">'),
    ('<meta name="twitter:description" content="Learn about our mission to provide free, evidence-based BMI and body '
     'composition calculators accessible to everyone.">', f'<meta name="twitter:description" content="{DESC_NEW}">'),
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
    for old, new in EDITS + META:
        src = one(src, old, new, PG)
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question">' + re.escape(q) + r'<svg.*?</button> <div class="faq-answer"> <p>)(.*?)(</p> </div>)', re.S)
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
            src = one(src, '<url><loc>https://calculatemybmi.net/about/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/about/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
