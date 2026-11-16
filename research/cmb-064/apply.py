#!/usr/bin/env python3
"""CMB-064 CLAIMS-15: the claims pass's last page edits (DEVLOG §5 P1). Every in-scope probe hit left after CMB-063 was
read; the ones that are headings, labels or attributed quotes over sourced sections are in
research/claims-pass/reviewed.json. What still needed a change:
  - /blog/: "Those decisions belong with a qualified clinician" named no source or "when" (§4); it is now CDC's own line,
    as on /about/ (CMB-053); "we do not provide medical treatment content, medication guidance, or surgical
    recommendations" is shorter and loses its dash; the note, now two lines at 1280, takes the 62ch measure of the
    site's source notes (styles.css .flow p.source-note), as the line-length detector asks;
  - /blog/underweight-bmi-risks/: the related-guide card to /blog/how-to-lower-bmi/ read "Improving Your BMI" on a page
    about a BMI below 18.5; it now carries the guide's name, "How to Lower BMI", as on the other pages' cards;
  - /blog/bmi-by-age/: the first FAQ answer's 65-and-over finding cites Winter et al. (2014) itself (the page cited it
    only further down);
  - /blog/bmi-tracking-guide/: the meta, Open Graph, Twitter and Article descriptions still promised "optimal weighing
    frequency" and "when BMI changes warrant medical attention", which CMB-062 took off the page; they now describe it;
  - /blog/body-fat-vs-bmi/: the Open Graph, Twitter and Article descriptions ("expert insights") now match its meta
    description.
Titles and H1s are untouched (D-28); the two that carry claim words go on the list for Marko.
usage: python3 research/cmb-064/apply.py [--check]   Run order from main: registry.py, apply.py."""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
EXT = 'target="_blank" rel="noopener"'
HUB, UW, AGE, TRK, BFV, SM = ('blog/index.html', 'blog/underweight-bmi-risks/index.html', 'blog/bmi-by-age/index.html',
                              'blog/bmi-tracking-guide/index.html', 'blog/body-fat-vs-bmi/index.html', 'sitemap.xml')
BASE = {
    HUB: 'cbe2764d38b89cecdbcd29f45261ca494109b28dbdfbefcc610d82354b53cec2',
    UW: '8ffdf5a41da5e46cfbed9d696f5fd163e1dab28e87597f0d864753cd26546b5d',
    AGE: '783d564933e74100be5b1435d81e16326eaa1e903ff83dca4a2b6ca67b79c307',
    TRK: '067376d8e3a1cf26872c8c505677287262c7c792bae7278bf8b6e19898fe2ce3',
    BFV: '497806e01462caa47b72a18d3bd5532982c78cdf721bfaf16d3f4d93ceb1b791',
    SM: 'b79daa5b95846e8e94689e74dab02187bf51e5b26168398bb37ed73579cb62d5',
}
CDC_LW = 'https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html'
WINTER = 'https://pubmed.ncbi.nlm.nih.gov/24452240/'
TRK_OLD_LONG = ('Complete guide to tracking your BMI over time. Learn optimal weighing frequency, measurement techniques, progress '
                'indicators, and when BMI changes warrant medical attention.')
TRK_OLD_SHORT = ('Complete guide to tracking your BMI over time. Learn optimal weighing frequency, measurement techniques, and '
                 'progress indicators.')
TRK_NEW = ('How to track your BMI: when and how to weigh, why single days go up and down, what to track beside BMI (waist, '
           'body fat, lean mass) and modest milestones.')
BFV_OLD = ('Compare body fat percentage and BMI to understand which health metric is right for you. Includes healthy ranges, '
           'measurement methods, and expert insights.')
BFV_META = ('Body fat percentage vs BMI: Learn which metric better measures health, how each is calculated, healthy ranges '
            'for men and women, and when to use both together.')

EDITS = {
    HUB: [
        ('<p style="color: var(--gray-600); font-size: 0.9375rem; margin-top: 1rem;">Everything on this site is informational '
         '&mdash; we do not provide medical treatment content, medication guidance, or surgical recommendations. Those '
         'decisions belong with a qualified clinician.</p>',
         '<p style="color: var(--gray-600); font-size: 0.9375rem; margin-top: 1rem; max-width: 62ch;">Everything on this site '
         'is informational: we give no advice on treatment, medication or surgery. If you’re '
         'concerned about your weight or have questions about your medications, CDC says to talk with your health care '
         f'provider (<a href="{CDC_LW}" {EXT}>CDC</a>).</p>'),
    ],
    UW: [
        ('<h4><a href="/blog/how-to-lower-bmi/">Improving Your BMI</a></h4>',
         '<h4><a href="/blog/how-to-lower-bmi/">How to Lower BMI</a></h4>'),
        ('"dateModified": "2026-11-16"', f'"dateModified": "{TODAY}"'),
    ],
    AGE: [
        ('A meta-analysis of adults aged 65 and over found a higher risk of death below a BMI of 23, but the published '
         'categories themselves don&rsquo;t shift.',
         'A meta-analysis of adults aged 65 and over found a higher risk of death below a BMI of 23 '
         f'(<a href="{WINTER}" {EXT}>Winter et al., 2014</a>), but the published categories themselves don&rsquo;t shift.'),
        ('"dateModified":"2026-11-13"', f'"dateModified":"{TODAY}"'),
    ],
    TRK: [
        (f'<meta name="description" content="{TRK_OLD_LONG}">', f'<meta name="description" content="{TRK_NEW}">'),
        (f'<meta property="og:description" content="{TRK_OLD_SHORT}">', f'<meta property="og:description" content="{TRK_NEW}">'),
        (f'<meta name="twitter:description" content="{TRK_OLD_SHORT}">',
         f'<meta name="twitter:description" content="{TRK_NEW}">'),
        (f'"description": "{TRK_OLD_LONG}"', f'"description": "{TRK_NEW}"'),
        ('"dateModified": "2026-11-16"', f'"dateModified": "{TODAY}"'),
    ],
    BFV: [
        (f'<meta property="og:description" content="{BFV_OLD}">', f'<meta property="og:description" content="{BFV_META}">'),
        (f'<meta name="twitter:description" content="{BFV_OLD}">', f'<meta name="twitter:description" content="{BFV_META}">'),
        (f'"description": "{BFV_OLD}"', f'"description": "{BFV_META}"'),
        ('"dateModified": "2026-11-16"', f'"dateModified": "{TODAY}"'),
    ],
    SM: [(f'<url><loc>https://calculatemybmi.net/{slug}</loc><lastmod>{was}</lastmod>',
          f'<url><loc>https://calculatemybmi.net/{slug}</loc><lastmod>{TODAY}</lastmod>')
         for slug, was in (('blog/', '2026-11-13'), ('blog/bmi-by-age/', '2026-11-13'),
                           ('blog/underweight-bmi-risks/', '2026-11-16'), ('blog/bmi-tracking-guide/', '2026-11-16'),
                           ('blog/body-fat-vs-bmi/', '2026-11-16'))],
}
GONE = {HUB: ('qualified clinician', 'surgical recommendations'), UW: ('Improving Your BMI',),
        TRK: ('optimal weighing', 'warrant medical attention', 'Complete guide'), BFV: ('expert insights',)}


def one(src, old, new, what):
    if old == new:
        return src
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:90]}'
    return src.replace(old, new)


def main():
    for rel, edits in EDITS.items():
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        for old, new in edits:
            src = one(src, old, new, rel)
        for gone in GONE.get(rel, ()):
            assert gone not in src, f'{rel}: "{gone}" is left'
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
