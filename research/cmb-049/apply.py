#!/usr/bin/env python3
"""CMB-049 CLAIMS-2: claims pass batch 2 (DEVLOG §5 P1) on /blog/underweight-bmi-risks/, the probe's top page (41 hits).
Every sentence now says what a registry row says, or goes (D-10); treatment and our own weight-gain advice go under
D-01 and D-06 (the 2026-11-11 kids-page precedent); the doctor lines are MedlinePlus's and NIMH's own "when" (§4).
Sources read in Chrome 2026-11-14 (registry.py records them): MedlinePlus "Weight loss - unintentional" (causes, when
to contact a provider, the visit), NIMH "Eating Disorders: What You Need to Know" (2024; signs and effects of
anorexia nervosa, co-occurring illness, "can be treated successfully", 988), NIAMS "Osteoporosis" (body size, diet,
anorexia nervosa), the HHS Office on Women's Health "Infertility" (being underweight among the things that change a
woman's ability to have a baby), the Alliance for Eating Disorders helpline (number, hours); already in the registry:
the Global BMI Mortality Collaboration 2016, NCHS Health E-Stat 119, CDC About BMI, CDC's pregnancy weight gain page,
Winter et al. 2014, WHO TRS 854.
Out: "Weakened Immune System" (infections, wound healing, vaccine response, surgical risk), the four bone mechanisms,
miscarriage, preterm birth, the men's testosterone, sperm and libido lines, "Additional Health Concerns", the risk bars
("Very High … Low", no source; §5 P2), "High metabolism", "Genetic factors", "Economic factors", the "BMI Below 17 /
Persistent Fatigue / Menstrual Irregularities / Difficulty Gaining Weight" doctor cards, the blood-test line, the
weight-gain diet and exercise lists, the "bidirectional" mental-health lists, "Withdrawal from social eating
situations", "mortality risks comparable to or even greater than severe obesity" (GBMC: 1.51 at BMI 15.0-18.4
against 2.76 at 40-59.9), the SAMHSA line (samhsa.gov answers 403 to a browser, so its number could not be checked).
In: the GBMC hazard ratios as bars, NCHS's 1.6%, NIAMS, OWH, CDC's 28-40 lb, MedlinePlus's causes and "when", NIMH's
signs, effects and 988 line. Title, H1 and URL kept (D-28; the page has impressions). The og image is redrawn with
sourced labels (og_underweight.py). dateModified, lastmod, the meta descriptions and the FAQPage JSON-LD (all five
visible answers) follow. Files are checked by SHA-256 first; every marker must occur once.
usage: python3 research/cmb-049/apply.py [--check]   Run order from main: registry.py, apply.py, og_underweight.py."""
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
PG, SM = 'blog/underweight-bmi-risks/index.html', 'sitemap.xml'
BASE = {PG: '28d23ee144a9d0af8be6e3f90efdf1e171b4e444bd5d204285f0dddafc79ff18',
        SM: '2509802b9bd84c195240e9e0c0604991cf7baa73c54fe85bc1bee81726611f52'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_cats': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'hestat119': 'https://www.cdc.gov/nchs/data/hestat/hestat119.htm',
    'who': 'https://www.who.int/publications/i/item/9241208546',
    'gbmc': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/',
    'winter': 'https://pubmed.ncbi.nlm.nih.gov/24452240/',
    'niams': 'https://www.niams.nih.gov/health-topics/osteoporosis',
    'owh': 'https://womenshealth.gov/a-z-topics/infertility',
    'cdc_preg': 'https://www.cdc.gov/maternal-infant-health/pregnancy-weight/index.html',
    'medline': 'https://medlineplus.gov/ency/article/003107.htm',
    'nimh': 'https://www.nimh.nih.gov/health/publications/eating-disorders',
    'alliance': 'https://www.allianceforeatingdisorders.com/',
}


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


# Global BMI Mortality Collaboration 2016, never-smokers without chronic disease, HR vs 22.5-<25 (registry sample)
GBMC = [('15.0–18.4', 1.51, 'underweight'), ('18.5–19.9', 1.13, 'normal'), ('20.0–22.4', 1.00, 'normal'),
        ('22.5–24.9', 1.00, 'normal'), ('25.0–27.4', 1.07, 'overweight'), ('27.5–29.9', 1.20, 'overweight'),
        ('30.0–34.9', 1.45, 'obese'), ('35.0–39.9', 1.94, 'obese'), ('40.0–59.9', 2.76, 'obese')]
BARS = ''.join(
    f'<div class="chart-bar-h-item"><span class="chart-bar-h-label">BMI {r}</span><div class="chart-bar-h-track">'
    f'<div class="chart-bar-h-fill {c}" style="width:{hr / 2.76 * 100:.1f}%;"></div></div>'
    f'<span class="chart-bar-h-value">{hr:.2f}{" (ref.)" if r == "22.5–24.9" else ""}</span></div>' for r, hr, c in GBMC)

TAKEAWAYS = (
    '<div class="key-takeaways"> <div class="key-takeaways-title">Key Takeaways</div> <ul> '
    f'<li><strong>Definition:</strong> a BMI below 18.5 is underweight for adults ({a("cdc_cats", "CDC")}); about 1.6% of US '
    f'adults aged 20 and over were underweight in August 2021–August 2023 ({a("hestat119", "NCHS")}).</li> '
    '<li><strong>Grades:</strong> WHO grades adult thinness in three steps: 17.0–18.4 (the calculator’s Underweight), '
    f'16.0–16.9 (moderate thinness) and below 16.0 (severe thinness) ({a("who", "WHO")}).</li> '
    '<li><strong>Risk of death:</strong> in pooled data from 239 studies, a BMI of 15.0 to 18.4 carried 1.51 times the risk '
    f'of death of a BMI of 22.5 to 24.9 ({a("gbmc", "Global BMI Mortality Collaboration, 2016")}).</li> '
    '<li><strong>Causes:</strong> poor nutrition and underlying health conditions, CDC’s survey team says '
    f'({a("hestat119", "NCHS")}); weight lost without trying has a longer list, from depression to celiac disease '
    f'({a("medline", "MedlinePlus")}).</li> '
    '<li><strong>When to act:</strong> MedlinePlus advises seeing a provider if you lose more than 10 pounds (4.5 kg), or 5% '
    f'of your usual weight, within 6 to 12 months without knowing why ({a("medline", "MedlinePlus")}).</li> '
    '<li><strong>Your BMI:</strong> work it out with our <a href="/">BMI calculator</a>.</li> </ul> </div>')

TOC = (
    '<div class="toc"> <div class="toc-title">In This Guide</div> <ul class="toc-list"> '
    '<li><a href="#what-is-underweight">What Defines Underweight BMI?</a></li> '
    '<li><a href="#underweight-classifications">Underweight Classifications</a></li> '
    '<li><a href="#health-risks">Health Risks of Being Underweight</a></li> '
    '<li class="toc-h3"><a href="#bone-health">Osteoporosis and Bone Health</a></li> '
    '<li class="toc-h3"><a href="#fertility">Fertility and Pregnancy</a></li> '
    '<li><a href="#causes">Causes of Being Underweight</a></li> '
    '<li><a href="#when-to-see-doctor">When to See a Doctor</a></li> '
    '<li><a href="#weight-gain-strategies">Getting Help</a></li> '
    '<li><a href="#mental-health">Mental Health Considerations</a></li> '
    '<li><a href="#faq">Frequently Asked Questions</a></li> </ul> </div>')

BODY = (
    '<!-- Health Risks Section --> <h2 id="health-risks">Health Risks of Being Underweight</h2> '
    '<p>The Global BMI Mortality Collaboration pooled 239 studies from 32 '
    'countries and, to limit the effect of smoking and existing illness, analysed never-smokers without chronic disease at '
    'the start. Against a BMI of 22.5 to 24.9, a BMI of 15.0 to 18.4 carried 1.51 times the risk of death, close to the 1.45 '
    f'of a BMI of 30.0 to 34.9 ({a("gbmc", "Global BMI Mortality Collaboration, 2016")}).</p> '
    f'<div class="chart-bar-h"> <p style="font-size: 0.875rem; '
    f'font-weight: 600; margin-bottom: 1rem; color: var(--gray-700);">Risk of death by BMI (hazard ratio; 1.00 = BMI 22.5 '
    f'to 24.9)</p> {BARS}</div> '
    '<p class="source-note">Never-smokers without chronic disease at the start, 239 studies, 32 countries. Source: Global BMI '
    f'Mortality Collaboration, The Lancet, 2016 ({a("gbmc", "full text")}).</p> '
    '<p>For adults aged 65 and over, a meta-analysis of 197,940 people found that, compared with a BMI of 23 to 23.9, the '
    f'risk of death was higher below 23 and began to rise at about 33 ({a("winter", "Winter et al., 2014")}).</p> '
    '<!-- Bone Health --> <h3 id="bone-health">Osteoporosis and Bone Health</h3> '
    '<p>NIH lists body size among the risk factors for osteoporosis: slender, thin-boned women and men are at greater risk '
    'because they have less bone to lose. It adds that a diet low in calcium and vitamin D can raise the risk of osteoporosis '
    f'and fractures, and that excessive dieting or poor protein intake may raise the risk of bone loss ({a("niams", "NIAMS")}).</p> '
    '<!-- Fertility --> <h3 id="fertility">Fertility and Pregnancy</h3> '
    '<p>The HHS Office on Women’s Health lists being overweight or underweight among the things that can change a woman’s '
    'ability to have a baby. Most female infertility comes from problems with ovulation, and irregular or absent periods are '
    f'one sign that ovulation isn’t normal ({a("owh", "Office on Women’s Health")}).</p> '
    '<p>For a pregnancy with one baby, CDC lists a weight gain of 28 to 40 lb for women who were underweight before pregnancy, '
    'against 25 to 35 lb for a BMI of 18.5 to 24.9; the ranges are the Institute of Medicine’s '
    f'({a("cdc_preg", "CDC")}).</p> '
    '<!-- Causes Section --> <h2 id="causes">Causes of Being Underweight</h2> '
    '<p>CDC’s survey team names two broad causes: “Poor nutrition and underlying health conditions can result in underweight '
    f'among youth and adults” ({a("hestat119", "NCHS")}). For weight lost without trying, MedlinePlus lists a wider set '
    f'({a("medline", "MedlinePlus")}):</p> '
    '<ul> <li><strong>Things that blunt appetite:</strong> depression, stress or anxiety; cancer, sometimes before other '
    'symptoms appear; long-term infections such as AIDS or tuberculosis; chronic diseases such as COPD or Parkinson disease; '
    'stimulant drugs such as cocaine and amphetamines; some medicines, among them chemotherapy and thyroid drugs.</li> '
    '<li><strong>Problems absorbing food:</strong> celiac disease; persistent diarrhea or infections such as parasites; '
    'long-term inflammation of the pancreas; surgery that removed part of the small intestine; laxative overuse.</li> '
    '<li><strong>Conditions not yet diagnosed:</strong> an eating disorder such as anorexia nervosa, diabetes, or an '
    'overactive thyroid.</li> </ul> '
    '<h3>Eating Disorders</h3> '
    '<p>NIMH describes eating disorders as serious illnesses, not choices, marked by severe disturbances in eating; people '
    'with them can be underweight, average weight or overweight, and those with avoidant restrictive food intake disorder '
    f'(ARFID) are often underweight ({a("nimh", "NIMH")}).</p> '
    '<div class="alert alert-warning"> <div class="alert-title">Signs of anorexia nervosa (NIMH)</div> '
    '<ul style="margin: 0.5rem 0 0 1.25rem; font-size: 0.875rem;"> '
    '<li>Severely restricted eating</li> <li>Intense, excessive exercise</li> <li>Extreme thinness (emaciation)</li> '
    '<li>A relentless drive to be thin and an unwillingness to keep a healthy weight</li> '
    '<li>Intense fear of weight gain</li> <li>A distorted body image or self-image</li> '
    '<li>Denying how serious a low body weight is</li> </ul> </div> '
    '<p>Over time, NIMH says, anorexia nervosa can lead to thinning of the bones, mild anemia, muscle wasting and weakness, '
    'low blood pressure, slowed breathing and pulse, damage to the heart, feeling tired all the time and infertility, among '
    'other harms. People with any combination of these signs may have an eating disorder and should talk to a health care '
    f'provider ({a("nimh", "NIMH")}).</p> '
    '<p><strong>Support:</strong> the Alliance for Eating Disorders runs a free helpline staffed by licensed therapists, '
    f'1-866-662-1235, Monday to Friday, 9:00 am to 7:00 pm Eastern ({a("alliance", "allianceforeatingdisorders.com")}). '
    'If you or someone you know is struggling or thinking about suicide, call or text 988, the Suicide and Crisis Lifeline, '
    f'or chat at 988lifeline.org; in a life-threatening emergency, call 911 ({a("nimh", "NIMH")}).</p> '
    '<!-- When to See a Doctor --> <h2 id="when-to-see-doctor">When to See a Doctor</h2> '
    f'<p>MedlinePlus advises contacting a provider in three situations ({a("medline", "MedlinePlus")}):</p> '
    '<ul> <li>You or someone in your family is losing more weight than is healthy for their age and height.</li> '
    '<li>You have lost more than 10 pounds (4.5 kg), or 5% of your usual weight, within 6 to 12 months and don’t know '
    'why.</li> <li>Other symptoms have come with the weight loss.</li> </ul> '
    '<p>Expect a physical exam, a weight check and questions about your history and symptoms, and possibly a referral to a '
    f'dietitian ({a("medline", "MedlinePlus")}). If you have concerns '
    'about your eating behavior or mental health, NIMH says to talk to a primary care provider, who can refer you to a '
    f'qualified mental health professional ({a("nimh", "NIMH")}).</p> '
    '<!-- Getting Help --> <h2 id="weight-gain-strategies">Getting Help</h2> '
    '<p>The plan depends on the cause: MedlinePlus says any diet and exercise changes a provider suggests depend on what is '
    f'behind the weight loss ({a("medline", "MedlinePlus")}). When an eating disorder is the cause, NIMH '
    'says eating disorders can be treated successfully, and that early detection and treatment are important for recovery '
    f'({a("nimh", "NIMH")}). We don’t give weight-gain targets or meal plans of our own; the <a href="/ideal-weight/">ideal '
    'weight calculator</a> shows what four published formulas give for your height.</p> '
    '<!-- Mental Health Section --> <h2 id="mental-health">Mental Health Considerations</h2> '
    '<p>Low mood and worry can push weight down: MedlinePlus counts depression, stress and anxiety among the things that blunt '
    f'appetite ({a("medline", "MedlinePlus")}). Eating disorders carry their own risks: NIMH says people with '
    'them are at risk for co-occurring mental illnesses, most often depression, anxiety and substance use disorders, and are '
    f'at a higher risk for suicide ({a("nimh", "NIMH")}).</p> '
    '<!-- CTA Section --> ')

FAQ = {
    'How can I gain weight in a healthy way?': (
        'Start with the cause: MedlinePlus says the diet and exercise changes a provider may suggest depend on what is behind '
        f'the weight loss, and a dietitian may help with nutrition ({a("medline", "MedlinePlus")}). If an eating disorder is '
        'behind it, NIMH says eating disorders can be treated successfully and that catching them early matters for recovery '
        f'({a("nimh", "NIMH")}).'),
    'Can being underweight affect fertility?': (
        'It can for women: the HHS Office on Women’s Health lists being overweight or underweight among the things that can '
        'change a woman’s ability to have a baby, and irregular or absent periods are one sign that ovulation isn’t normal '
        f'({a("owh", "Office on Women’s Health")}). NIMH lists infertility among the harms of anorexia nervosa '
        f'({a("nimh", "NIMH")}). In pregnancy, CDC lists a weight gain of 28 to 40 lb for women underweight before '
        f'pregnancy ({a("cdc_preg", "CDC")}).'),
    'Is being underweight as dangerous as being overweight?': (
        'For the risk of death, more than overweight and about as much as class 1 obesity. In never-smokers without chronic '
        'disease, a BMI of 15.0 '
        'to 18.4 carried 1.51 times the risk of death of a BMI of 22.5 to 24.9, against 1.07 at 25.0 to 27.4, 1.20 at 27.5 to '
        f'29.9, 1.45 at 30.0 to 34.9 and 2.76 at 40.0 to 59.9 ({a("gbmc", "Global BMI Mortality Collaboration, 2016")}). '
        'More in <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>.'),
    'What causes someone to be underweight?': (
        'CDC’s survey team names poor nutrition and underlying health conditions '
        f'({a("hestat119", "NCHS")}). For weight lost without trying, MedlinePlus lists things that blunt appetite (depression, '
        'stress or anxiety, cancer, long-term infections and diseases, some drugs and medicines), problems absorbing food '
        '(celiac disease, persistent diarrhea or parasites, long-term pancreatitis, intestinal surgery, laxative overuse) and '
        f'conditions not yet diagnosed: an eating disorder, diabetes or an overactive thyroid ({a("medline", "MedlinePlus")}).'),
}

EDITS = [
    ('<p>Body Mass Index (BMI) is a screening tool that uses your height and weight to estimate body fat and categorize your '
     'weight status. According to the World Health Organization (WHO) and the Centers for Disease Control and Prevention (CDC), '
     'a BMI below 18.5 kg/m<sup>2</sup> is classified as underweight.</p>',
     '<p>Body Mass Index (BMI) is a screening measure worked out from your height and weight '
     f'({a("cdc_about", "CDC")}). According to the World Health Organization (WHO) and the Centers for Disease Control and '
     'Prevention (CDC), a BMI below 18.5 kg/m<sup>2</sup> is classified as underweight.</p>'),
    ('<p>While BMI is a useful initial screening tool, it has limitations. It does not directly measure body fat or account for '
     'factors like muscle mass, bone density, age, sex, or ethnicity. Learn more about these nuances in our guide to '
     '<a href="/blog/bmi-categories/">BMI categories</a>.</p>',
     '<p>BMI has limits: CDC notes that it does not directly measure body fat and does not distinguish between fat, muscle, '
     f'and bone mass ({a("cdc_about", "CDC")}). More in our guide to <a href="/blog/bmi-categories/">BMI categories</a>.</p>'),
    ('<p>The World Health Organization further divides underweight into three severity categories based on BMI ranges. '
     'Understanding these classifications helps healthcare providers assess risk levels and determine appropriate '
     'interventions.</p>',
     f'<p>The World Health Organization grades adult thinness in three steps by BMI ({a("who", "WHO, 1995")}); WHO calls '
     'the first grade mild thinness:</p>'),
    ('<p>Use our <a href="/ideal-weight/">ideal weight calculator</a> for personalized weight recommendations based on your '
     'height, age, and body frame.</p>',
     '<p>The <a href="/ideal-weight/">ideal weight calculator</a> shows what four published formulas give for your height.</p>'),
    ('<p>This article is for informational purposes only and does not constitute medical advice. BMI is a screening tool, not '
     'a diagnostic measure. If you are concerned about your weight, have experienced unintentional weight loss, or show signs '
     'of an eating disorder, please consult a qualified healthcare provider. Always seek professional medical guidance before '
     'making significant changes to your diet or exercise routine.</p>',
     '<p>This article is for information only and is not medical advice. BMI is a screening measure, not a diagnosis. For when '
     'to contact a provider, see <a href="#when-to-see-doctor">When to See a Doctor</a>.</p>'),
    ('<p>Evidence-based strategies for reaching and maintaining a healthy weight.</p>',
     '<p>Official guidance on lowering a BMI above the healthy range.</p>'),
]
DESC_OLD = ('Complete guide to underweight BMI (below 18.5): health risks including weakened immunity, osteoporosis, fertility '
            'issues. Learn causes, symptoms, and healthy weight gain strategies.')
DESC_NEW = ('Underweight means a BMI below 18.5. The research on its risks (death, bones, fertility), its causes, and when '
            'MedlinePlus and NIMH say to see a provider.')
META = [
    (f'<meta name="description" content="{DESC_OLD}">', f'<meta name="description" content="{DESC_NEW}">'),
    ('<meta property="og:description" content="Complete guide to underweight BMI (below 18.5): health risks, causes, and '
     'healthy weight gain strategies backed by medical research.">', f'<meta property="og:description" content="{DESC_NEW}">'),
    ('<meta name="twitter:description" content="Complete guide to underweight BMI (below 18.5): health risks, causes, and '
     'healthy weight gain strategies.">', f'<meta name="twitter:description" content="{DESC_NEW}">'),
    (f'"description": "{DESC_OLD}"', f'"description": "{DESC_NEW}"'),
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
    # the key takeaways and the table of contents
    i = src.index('<div class="key-takeaways">')
    j = src.index('<!-- Table of Contents -->', i)
    src = src[:i] + TAKEAWAYS + ' ' + src[j:]
    i = src.index('<div class="toc">')
    j = src.index('</ul> </div>', i) + len('</ul> </div>')
    src = src[:i] + TOC + src[j:]
    # the body from the health risks to the call to action
    i = src.index('<!-- Health Risks Section -->')
    j = src.index('<!-- CTA Section -->', i) + len('<!-- CTA Section --> ')
    src = src[:i] + BODY + src[j:]
    for old, new in EDITS + META:
        src = one(src, old, new, PG)
    # FAQ answers 2-5 (the first stays), then the FAQPage JSON-LD from all five visible answers
    for q, ans in FAQ.items():
        pat = re.compile(r'(<button class="faq-question"> ' + re.escape(q) + r' <svg.*?</button> <div class="faq-answer"> <p>)(.*?)(</p> </div>)', re.S)
        assert len(pat.findall(src)) == 1, f'FAQ "{q}"'
        src = pat.sub(lambda m: m.group(1) + ans + m.group(3), src)
    qa = re.findall(r'(?s)<button class="faq-question"> (.*?) <svg.*?</button> <div class="faq-answer"> <p>(.*?)</p> </div>', src)
    assert len(qa) == 5, len(qa)
    blocks = list(re.finditer(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src))
    fb = next(b for b in blocks if '"FAQPage"' in b.group(2))
    d = json.loads(fb.group(2))
    d['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}}
                       for q, ans in qa]
    src = src[:fb.start(2)] + ' ' + jsonld_block(d) + ' ' + src[fb.end(2):]
    src = one(src, '"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"', PG)
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
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/underweight-bmi-risks/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/underweight-bmi-risks/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
