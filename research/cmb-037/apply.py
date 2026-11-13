#!/usr/bin/env python3
"""CMB-037 SOURCES-2: batch 4a of the scores run (D-26), the S items on six pages with few untraced numbers. Every
number the Stage 1 audit could not trace now traces to a registry row, or the claim goes (D-10, D-06). Every replacement
must match exactly once (or the count given), so a page that changed since stops the run.
usage: python3 research/cmb-037/apply.py [--check]   (--check counts the matches and writes nothing)

1. /blog/body-fat-vs-bmi/: "waist-to-height ratio should be < 0.5 for optimal health" becomes NICE's classification
   (0.5 or more, increased central adiposity; registry nice-ng246-ethnicity-thresholds notes).
2. /blog/ and /blog/what-is-bmi/: Quetelet's index dated 1832 as Eknoyan 2008 gives it (not "the 1830s" or "the 19th
   century").
3. /blog/underweight-bmi-risks/: the "Sample 2,500 Calorie Day" meal plan goes (D-06: no calorie targets of our own);
   "3+ months" goes from the amenorrhea line (definitions differ by source and none is on the page).
4. /about/: the §5 item (New BMI called "the Trefethen height-corrected variant", the ideal-weight formulas "developed
   for clinical dosing ... widely used in healthcare settings") and the untraced years: Quetelet 1832 (Eknoyan 2008);
   the formula years next to the papers that give them (Pai and Paloucek 2000, Davidson 2015); CDC's child categories
   and growth charts as CDC words them; the lean-body-mass equations without years (their page gives the sources).
5. /privacy/ changes nothing: its numbers get registry rows (research/cmb-037/registry.py).
6. Dates (§4): schema dateModified, article:modified_time and sitemap lastmod of the five changed pages.
"""
import datetime
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv

NICE = ('<a href="https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-'
        'central-adiposity" target="_blank" rel="noopener">')
EKNOYAN = '<a href="https://doi.org/10.1093/ndt/gfm517" target="_blank" rel="noopener">'
PAI = '<a href="https://pubmed.ncbi.nlm.nih.gov/10981254/" target="_blank" rel="noopener">'
DAVIDSON = '<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4503941/" target="_blank" rel="noopener">'
CDCKIDS = '<a href="https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html" target="_blank" rel="noopener">'
CDCEXT = '<a href="https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm" target="_blank" rel="noopener">'
TREF = '<a href="https://people.maths.ox.ac.uk/trefethen/bmi.html" target="_blank" rel="noopener">'

EDITS = {
    'blog/body-fat-vs-bmi/index.html': [
        ('<li><strong>Waist-to-height ratio:</strong> Should be &lt; 0.5 for optimal health</li>',
         f'<li><strong>Waist-to-height ratio:</strong> 0.5 or more means increased central adiposity ({NICE}NICE</a>)'
         '</li>', 1),
    ],
    'blog/index.html': [
        ('From Quetelet&rsquo;s 1830s index to Ancel Keys naming it BMI in 1972 and the WHO categories.',
         'From Quetelet&rsquo;s 1832 index to Ancel Keys naming it BMI in 1972 and the WHO categories.', 1),
    ],
    'blog/what-is-bmi/index.html': [
        ('The idea itself is old: it goes back to the 19th-century Belgian statistician Adolphe Quetelet, and our ',
         'The idea itself is old: the Belgian statistician Adolphe Quetelet described the index in 1832 '
         f'({EKNOYAN}Eknoyan, 2008</a>), and our ', 1),
    ],
    'blog/underweight-bmi-risks/index.html': [
        ('<p>Missing periods for 3+ months (amenorrhea) or irregular cycles may signal hormonal imbalances from low '
         'weight.</p>',
         '<p>Missing or irregular periods (amenorrhea) may signal hormonal changes linked to low weight.</p>', 1),
        ('<h3>Sample Daily Meal Plan for Weight Gain</h3> <div class="alert alert-info"> <div class="alert-title">Sample '
         '2,500 Calorie Day</div> <p style="margin-top: 0.5rem;"><strong>Breakfast:</strong> Oatmeal with banana, almond '
         'butter, walnuts, and honey (550 cal)</p> <p><strong>Mid-morning snack:</strong> Greek yogurt with granola and '
         'berries (300 cal)</p> <p><strong>Lunch:</strong> Whole grain sandwich with avocado, turkey, cheese, and soup '
         '(650 cal)</p> <p><strong>Afternoon snack:</strong> Trail mix with dried fruit and chocolate (350 cal)</p> '
         '<p><strong>Dinner:</strong> Salmon, quinoa, roasted vegetables with olive oil (600 cal)</p> <p '
         'style="margin-bottom: 0;"><strong>Evening snack:</strong> Smoothie with milk, peanut butter, and banana (350 '
         'cal)</p> </div> ', '', 1),
    ],
    'about/index.html': [
        ('Calculates your ideal body weight using four established clinical formulas: Devine (1974), Robinson (1983), '
         'Miller (1983), and Hamwi (1964). Compare results across all four methods.',
         'Calculates your ideal body weight with four published formulas: Devine, Robinson, Miller and Hamwi. Compare '
         'the results across all four.', 1),
        ('BMI = weight (kg) / height (m)&sup2;, established by Adolphe Quetelet and adopted globally by the WHO for '
         'population-level weight screening since the 1990s.',
         'BMI = weight (kg) / height (m)&sup2;, the index Adolphe Quetelet described in 1832 '
         f'({EKNOYAN}Eknoyan, 2008</a>); WHO&rsquo;s adult classification is built on it.', 1),
        ("For pediatric BMI calculations, we use the CDC's 2000 sex-specific BMI-for-age percentile growth charts, which "
         'classify children as underweight (&lt;5th percentile), healthy weight (5th&ndash;84th), overweight '
         '(85th&ndash;94th), or obese (&ge;95th percentile).',
         'For children and teens 2 through 19 we use BMI-for-age percentiles by sex, in the categories '
         f'{CDCKIDS}CDC</a> uses: underweight below the 5th percentile, healthy weight from the 5th to below the 85th, '
         'overweight from the 85th to below the 95th, obesity at the 95th or above. The percentiles come from the '
         f'{CDCEXT}2000 CDC growth charts, extended above the 95th percentile in 2022</a>.', 1),
        ('as proposed by Professor Nick Trefethen of the University of Oxford in 2013, which corrects for height bias in '
         'the traditional formula.',
         f'as proposed by Nick Trefethen, professor of numerical analysis at the University of Oxford, in 2013 ({TREF}'
         'his page</a>). It is his proposal: CDC and WHO still use the standard formula.', 1),
        ('Devine (1974), Robinson (1983), Miller (1983), and Hamwi (1964) equations, each originally developed for '
         'clinical dosing and nutritional assessments and now widely used in healthcare settings.',
         f'Devine (1974), Robinson (1983) and Miller (1983), as tabulated by {PAI}Pai and Paloucek (2000)</a>, and '
         f'Hamwi (1964), as given by {DAVIDSON}Davidson (2015)</a>; the <a href="/ideal-weight/">ideal weight '
         'calculator</a> explains where each came from.', 1),
        ('Boer (1984), James (1976), and Hume (1966) equations, developed from clinical studies measuring body '
         'composition through established anthropometric methods.',
         'the Boer, James and Hume equations; the <a href="/lean-body-mass/">lean body mass calculator</a> gives the '
         'source of each.', 1),
        ('the Trefethen height-corrected variant,', 'Nick Trefethen’s 2013 New BMI proposal,', 2),
        ('Trefethen 2013 for the height-corrected variant)', 'Trefethen 2013 for New BMI)', 2),
        ('pediatric, Trefethen height-corrected, ideal weight', 'pediatric, New BMI, ideal weight', 2),
        ('and the Trefethen <a href="/new-bmi-calculator/">height-corrected BMI</a> variant.',
         'and Nick Trefethen&rsquo;s <a href="/new-bmi-calculator/">New BMI</a> proposal.', 1),
        ('Implements the height-corrected BMI formula proposed by Oxford mathematician Nick Trefethen in 2013. This '
         'formula addresses the known limitation of the traditional BMI equation that overestimates BMI for tall '
         'individuals and underestimates it for shorter people.',
         'Implements the New BMI formula that Oxford mathematician Nick Trefethen proposed in 2013. He argues the '
         'standard formula makes tall people read too high and short people too low; CDC and WHO still use the '
         'standard one.', 1),
    ],
}


def rx(literal):
    """The literal with every run of spaces matching any whitespace (the pages wrap lines in places)."""
    return re.compile(r'\s+'.join(re.escape(part) for part in literal.split(' ')))


def set_dates(t):
    t = re.sub(r'("dateModified": ?")\d{4}-\d{2}-\d{2}(")', rf'\g<1>{TODAY}\g<2>', t)
    return re.sub(r'(article:modified_time" content=")\d{4}-\d{2}-\d{2}', rf'\g<1>{TODAY}', t)


def main():
    bad = 0
    for rel, edits in EDITS.items():
        p = REPO / rel
        t = p.read_text(encoding='utf-8')
        for old, new, want in edits:
            pat = rx(old)
            got = len(pat.findall(t))
            if got != want:
                bad += 1
                print('MISMATCH', rel, got, want, '|', old[:100])
                continue
            t = pat.sub(lambda m: new, t)
        if not CHECK:
            p.write_text(set_dates(t), encoding='utf-8')
            print('edited', rel)
    if CHECK or bad:
        print('check done' if not bad else f'{bad} mismatches: nothing should be committed')
        return
    sm = REPO / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    for rel in EDITS:
        loc = 'https://calculatemybmi.net/' + ('' if rel == 'index.html' else rel[:-len('index.html')])
        s, n = re.subn(rf'(<loc>{re.escape(loc)}</loc>\s*<lastmod>)\d{{4}}-\d{{2}}-\d{{2}}', rf'\g<1>{TODAY}', s)
        assert n == 1, (loc, n)
    sm.write_text(s, encoding='utf-8')
    print('sitemap lastmod', TODAY, 'for', len(EDITS), 'pages')


if __name__ == '__main__':
    main()
