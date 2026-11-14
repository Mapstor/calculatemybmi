#!/usr/bin/env python3
"""CMB-048 CLAIMS-1: the first batch of the claims pass (DEVLOG §5 P1): the calculators' own words.
  - assets/js/calculator.js, genSummary(): the adult results' two bare doctor lines (underweight: "A doctor can tell you
    whether this is normal for you."; obesity: "A doctor can put this in context with your other health measures.")
    give way to CDC: the Adult BMI Calculator page's provider sentence for underweight, the About BMI page's
    other-factors sentence for obesity, each quoted or paraphrased and linked (§4: no bare doctor lines).
  - /calculators/: six FAQ answers rewritten so each sentence says what a registry row says (or what the calculators
    do): out go "corrects the traditional formula's height bias" (Trefethen writes it may not be an improvement),
    "population-level screening tool", "we recommend ... blood work", "6-11% more body fat", "men store fat
    abdominally, which is associated with higher cardiovascular risk", the football player's 12% and 35%, "sometimes
    more accurate", "athletes ... will typically exceed these ranges", "no official schedule", "tracked at regular
    pediatric checkups, typically annually", "BMI is not recommended under 2 ... under pediatrician guidance" and two
    bare doctor lines; in come CDC (About BMI, Adult BMI Categories, child categories), NCHS Health E-Stat 111, NHLBI,
    Provencher 2018, Orsama 2014 and our DXA medians. The FAQPage JSON-LD is rebuilt from the visible answers.
    The cards and the comparison table stop describing features the calculators don't have (the women's ACOG pregnancy
    ranges and menopause notes, removed in CMB-017) and say what they do (the rank among US adults, women or men);
    the men's example drops "if he exercises regularly ... his actual risk may be lower" for the rank the calculator
    prints; "WHO category" and "adults 18+" on the standard card match the calculator (adults 20+); the trusted-sources
    intro and the disclaimer lose their sales words. The decision table: "Correct for height bias" becomes Trefethen's
    proposal, "a target weight goal ... realistic range" becomes formula-based weights (D-06), the body fat row stops
    repeating the lean mass row; "2-100" ages becomes "2+" (no calculator stops at 100). Eleven table cells get their
    missing </td>.
  - dateModified and the sitemap lastmod of /calculators/ move to the commit's day.
Files are checked by SHA-256 before any edit; every marker must occur once.
usage: python3 research/cmb-048/apply.py [--check]   Run order from main: registry.py, apply.py."""
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
HUB, JS, SM = 'calculators/index.html', 'assets/js/calculator.js', 'sitemap.xml'
BASE = {HUB: '7976855030f4a6da07f2d8702a4a101cb375b4daa94860d1316845cf2d5bfe87',
        JS: '4b287fcce7bf5134226c3ed5b4a024fddedcf6736fd34059a913be8661dd4fb5',
        SM: '65007234dde29aabd5889064afc13b6e905888669e12d2d52719146235a54345'}
EXT = 'target="_blank" rel="noopener"'
CDC_ABOUT = 'https://www.cdc.gov/bmi/about/index.html'
CDC_CALC = 'https://www.cdc.gov/bmi/adult-calculator/index.html'
CDC_CATS = 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html'
CDC_KIDS = 'https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html'
HESTAT = 'https://www.cdc.gov/nchs/data/hestat/hestat111.htm'
NHLBI = 'https://www.ncbi.nlm.nih.gov/books/NBK2003/'
PROV = 'https://doi.org/10.1519/JSC.0000000000002449'
ORSAMA = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5644907/'
TREF = 'https://people.maths.ox.ac.uk/trefethen/bmi.html'
TD = '<td style="padding:0.625rem;border:1px solid var(--gray-200);color:var(--gray-600);">'
TL = '<td style="padding:0.75rem;border:1px solid var(--gray-200);color:var(--gray-700);">'      # the decision table
TC = '<td style="padding:0.75rem;border:1px solid var(--gray-200);color:var(--gray-600);">'

FAQ = {
    'Which BMI calculator should I use?': (
        'For a quick check, start with the <a href="/">Standard BMI Calculator</a>, which also ranks your BMI among US '
        'adults. The <a href="/women-bmi-calculator/">Women</a> and <a href="/men-bmi-calculator/">Men</a> versions rank '
        'it among US women or men, and the women’s version checks a waist measurement too. The '
        '<a href="/age-bmi-calculator/">BMI by Age</a> calculator compares you with US adults of your sex and age group. For '
        'children and teens aged 2 to 19, use the <a href="/kids-bmi-calculator/">Pediatric BMI Calculator</a>: it reads '
        'BMI as a percentile on CDC’s growth charts instead of the adult cut-offs. The '
        '<a href="/new-bmi-calculator/">New BMI Calculator</a> shows Trefethen’s proposed formula next to the standard one; '
        f'he writes that it may not be an improvement (<a href="{TREF}" {EXT}>Trefethen</a>). For body composition, the <a href="/body-fat-calculator/">Body '
        'Fat</a> and <a href="/lean-body-mass/">Lean Body Mass</a> calculators estimate fat and lean mass.'),
    'Are these calculators accurate?': (
        'Each calculator uses a published, named formula, and the categories follow CDC and WHO; the arithmetic is exact. '
        'The limits are BMI’s own: CDC calls it a screening measure that “does not distinguish between fat, muscle, and '
        'bone mass” and says that for an individual it should be considered with other factors, such as blood pressure '
        f'and cholesterol levels (<a href="{CDC_ABOUT}" {EXT}>CDC</a>). At a given BMI, body fat may vary by sex, age, and '
        f'race and Hispanic origin, NCHS notes (<a href="{HESTAT}" {EXT}>Health E-Stat 111</a>).'),
    'Is BMI the same for men and women?': (
        'The formula and the adult categories are the same: CDC applies its adult categories regardless of age, sex, or '
        f'race (<a href="{CDC_CATS}" {EXT}>CDC</a>). Body composition differs: on CDC’s body scans of adults aged 20 to '
        '59 with a healthy BMI, women had a median of 33.4% body fat and men 22.1% (our calculation; see the '
        '<a href="/body-fat-percentage-chart/">body fat percentage chart</a>). The NIH waist cut-offs differ too: more '
        f'than 35 inches (88 cm) for women and 40 inches (102 cm) for men (<a href="{NHLBI}" {EXT}>NHLBI</a>). The '
        '<a href="/women-bmi-calculator/">women’s</a> and <a href="/men-bmi-calculator/">men’s</a> calculators add that '
        'context.'),
    'What age group is each calculator for?': (
        'The <a href="/">Standard</a>, <a href="/women-bmi-calculator/">Women</a>, <a href="/men-bmi-calculator/">Men</a>, '
        '<a href="/age-bmi-calculator/">BMI by Age</a> and <a href="/new-bmi-calculator/">New BMI</a> calculators are for '
        '<strong>adults aged 20 and over</strong>, the ages CDC’s adult categories cover; the BMI by Age calculator also '
        'covers the research on adults 65 and over. The <a href="/kids-bmi-calculator/">Pediatric BMI Calculator</a> is '
        'for <strong>children and teens aged 2 through 19</strong>, the ages of CDC’s BMI-for-age charts. The '
        '<a href="/ideal-weight/">Ideal Weight</a> and <a href="/lean-body-mass/">Lean Body Mass</a> calculators use '
        'formulas for adults.'),
    "Can I use these calculators if I'm an athlete?": (
        f'Yes, but read the result with care: BMI can’t tell muscle from fat (<a href="{CDC_ABOUT}" {EXT}>CDC</a>). At the '
        'NFL Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat '
        f'(<a href="{PROV}" {EXT}>Provencher et al., 2018</a>). A body fat estimate from the '
        '<a href="/body-fat-calculator/">Body Fat Calculator</a> or a waist measurement tells you more; '
        '<a href="/blog/bmi-for-athletes/">BMI for athletes</a> covers the research.'),
    'How often should I check my BMI?': (
        'Weight moves from day to day: in a study of 80 adults who weighed themselves daily, weight was higher early in '
        f'the week and fell during it (<a href="{ORSAMA}" {EXT}>Orsama et al., 2014</a>), so one reading can mislead. The '
        '<a href="/blog/bmi-tracking-guide/">BMI tracking guide</a> covers how to weigh and log it. For a child, use the '
        '<a href="/kids-bmi-calculator/">Pediatric BMI Calculator</a>: CDC reads a child’s BMI as a percentile among '
        f'children of the same sex and age (<a href="{CDC_KIDS}" {EXT}>CDC</a>).'),
}

HUB_EDITS = [
    ('The classic Body Mass Index calculator for adults 18+. Input in metric or imperial; output is the number, the WHO '
     'category, and your healthy weight span at your height.',
     'The standard Body Mass Index calculator for adults aged 20 and over. Input in metric or imperial; output is the '
     'number, the category, your healthy weight span at your height and where your BMI ranks among US adults.'),
    ('Adds life-stage context to the BMI number. Includes ACOG pregnancy weight-gain ranges by pre-pregnancy BMI and '
     'menopausal body-composition notes.',
     'Ranks your BMI among US women and checks a waist measurement against the NIH, NICE and ADA thresholds.'),
    ('Women who want context beyond the number: waist, body fat and pregnancy weight-gain ranges <div',
     'Women who want context beyond the number: the US comparison and a waist check</p> <div'),
    ('. However, if he exercises regularly and has a waist under 40", his actual risk may be lower. </div>',
     ', higher than 31% of US men. </div>'),
    ('Uses the WHO adult 18.5&ndash;24.9 range for all adults, then adds a finding for adults 65 and over:',
     'Uses CDC’s adult categories (healthy 18.5&ndash;24.9) at every age from 20, ranks your BMI among US adults of your '
     'sex and age group, then adds a finding for adults 65 and over:'),
    ('<strong style="color:var(--gray-700);">Best for:</strong> Athletes, fitness enthusiasts, and anyone tracking body '
     'composition</p>',
     '<strong style="color:var(--gray-700);">Best for:</strong> Anyone who wants lean mass estimated from height and '
     'weight with three published formulas</p>'),
    (f'{TD}Quickest calculation, universally recognized</td>', f'{TD}Rank among US adults</td>'),
    (f'{TD}NIH waist cut-off, ACOG pregnancy weight-gain ranges </tr>',
     f'{TD}Rank among US women; NIH, NICE and ADA waist check</td> </tr>'),
    (f'{TD}NIH waist cut-off, muscle-mass note </tr>', f'{TD}Rank among US men; NIH waist cut-off</td> </tr>'),
    (f'{TD}Proposed height correction (not used clinically) </tr>', f'{TD}A proposed formula, not the one CDC uses</td> </tr>'),
    (f'{TD}US averages by age; Winter 2014 data for 65+ </tr>', f'{TD}US averages by age; Winter 2014 data for 65+</td> </tr>'),
    ('<div class="stat-highlight" style="color:#8b5cf6;">2-100</div>', '<div class="stat-highlight" style="color:#8b5cf6;">2+</div>'),
    (f'{TC}The fastest way to calculate your BMI using the WHO formula</td>',
     f'{TC}BMI, category, healthy weight span and rank among US adults</td>'),
    (f'{TC}Adds waist, body fat and pregnancy context </tr>', f'{TC}Adds waist, body fat and pregnancy context</td> </tr>'),
    (f'{TC}Adds the NIH waist cut-off and muscle-mass context </tr>',
     f'{TC}Adds the NIH waist cut-off and muscle-mass context</td> </tr>'),
    (f'{TL}See your BMI next to people your age <td', f'{TL}See your BMI next to people your age</td> <td'),
    (f'{TC}Shows US average BMI, weight and waist by age; the cut-offs stay the same </tr>',
     f'{TC}Shows US average BMI, weight and waist by age; the cut-offs stay the same</td> </tr>'),
    (f'{TL}Correct for height bias (very short/tall)</td>', f'{TL}Try the formula Trefethen proposed for very short or tall people</td>'),
    (f'{TC}Uses height^2.5 instead of height^2, a proposal that health agencies have not adopted </tr>',
     f'{TC}Uses height^2.5 instead of height^2; CDC’s formula uses height^2</td> </tr>'),
    (f'{TL}Find a target weight goal</td>', f'{TL}See formula-based weights for your height</td>'),
    (f'{TC}Compares four clinical formulas (Devine, Robinson, Miller, Hamwi) for a realistic range</td>',
     f'{TC}Compares four published formulas (Devine, Robinson, Miller, Hamwi)</td>'),
    (f'{TC}Estimates lean mass and fat mass from height and weight </tr> <tr style="background:var(--gray-50);">',
     f'{TC}Estimates lean mass and fat mass from height and weight</td> </tr> <tr style="background:var(--gray-50);">'),
    (f'{TC}Estimates lean mass and fat mass from height and weight </tr> </tbody>',
     f'{TC}Estimates body fat three ways (tape, skinfolds, height and weight) and ranks it against CDC body scans</td> </tr> </tbody>'),
    ("<p>Our calculators are built on formulas and guidelines from the world's leading health organizations. These "
     'authoritative sources provide additional context for understanding your BMI results.</p>',
     '<p>The cut-offs and growth charts these calculators use come from these sources.</p>'),
    ('<strong>Medical Disclaimer:</strong> These calculators provide estimates for informational purposes only. BMI is a '
     'screening tool, not a diagnostic measure. It does not account for muscle mass, bone density, age, sex, or '
     'ethnicity. Always consult a healthcare professional for medical advice. The information on this page should not be '
     'used as a substitute for professional medical advice, diagnosis, or treatment.</p>',
     '<strong>Medical Disclaimer:</strong> These calculators give estimates for information only. BMI is a screening '
     'measure, not a diagnosis. Ask a healthcare professional for medical advice.</p>'),
]
JS_EDITS = [
    ('above your current weight. A doctor can tell you whether this is normal for you.`;',
     'above your current weight. CDC: &ldquo;Persons may consider seeking advice from their health care providers about '
     f'their BMI&rdquo; (<a href="{CDC_CALC}" target="_blank" rel="noopener">Adult BMI Calculator</a>).`;'),
    ('below your current weight. A doctor can put this in context with your other health measures.`;',
     'below your current weight. CDC says that for an individual, BMI should be considered with other factors, such as '
     f'blood pressure and cholesterol levels (<a href="{CDC_ABOUT}" target="_blank" rel="noopener">CDC</a>).`;'),
]
SM_EDITS = [('<url><loc>https://calculatemybmi.net/calculators/</loc><lastmod>2026-11-13</lastmod>',
             f'<url><loc>https://calculatemybmi.net/calculators/</loc><lastmod>{TODAY}</lastmod>')]


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()


def hub(src):
    for old, new in HUB_EDITS:
        assert src.count(old) == 1, f'{HUB}: marker found {src.count(old)} times: {old[:70]}'
        src = src.replace(old, new)
    # the visible FAQ answers
    for q, a in FAQ.items():
        pat = re.compile(r'(<button class="faq-question">' + re.escape(html.escape(q, quote=False).replace("'", "'")) +
                         r'<svg.*?</button> <div class="faq-answer"><p>)(.*?)(</p></div>)', re.S)
        found = pat.findall(src)
        assert len(found) == 1, f'{HUB}: FAQ "{q}" found {len(found)} times'
        src = pat.sub(lambda m: m.group(1) + a + m.group(3), src)
    # the JSON-LD: FAQPage answers rebuilt from the visible text, dateModified moved
    m = re.search(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', src)
    d = json.loads(m.group(2))
    assert json.dumps(d, ensure_ascii=False) == m.group(2).strip(), 'JSON-LD does not round-trip'
    g = {x['@type']: x for x in d['@graph']}
    names = [e['name'] for e in g['FAQPage']['mainEntity']]
    assert names == list(FAQ), f'FAQ questions differ: {names}'
    for e in g['FAQPage']['mainEntity']:
        e['acceptedAnswer']['text'] = plain(FAQ[e['name']])
    g['CollectionPage']['dateModified'] = TODAY
    lead = m.group(2)[:len(m.group(2)) - len(m.group(2).lstrip())]
    tail = m.group(2)[len(m.group(2).rstrip()):]
    src = src[:m.start(2)] + lead + json.dumps(d, ensure_ascii=False) + tail + src[m.end(2):]
    return src


def main():
    for rel in (HUB, JS, SM):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == HUB:
            src, n = hub(src), len(HUB_EDITS) + len(FAQ) + 1
        else:
            edits = JS_EDITS if rel == JS else SM_EDITS
            for old, new in edits:
                assert src.count(old) == 1, f'{rel}: marker found {src.count(old)} times: {old[:70]}'
                src = src.replace(old, new)
            n = len(edits)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: {n} edit(s){" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
