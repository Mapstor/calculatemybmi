#!/usr/bin/env python3
"""CMB-066 D28-TITLES: the two titles and H1s on the D-28 list (CMB-064), changed as proposed; Marko approved both on
2026-11-17 ("1 yes lets do as u recommend"). Both pages have Search Console impressions, hence D-28.
  - /blog/how-to-lower-bmi/: "How to Lower BMI: Evidence-Based Strategies for Healthy Weight Loss" becomes
    "How to Lower BMI: CDC’s Steps for Healthy Weight Loss" (the page's steps are CDC's, cdc-losing-weight; "Evidence-Based"
    named no source). The <title> keeps its " | CalculateMyBMI" suffix and drops from 84 to 69 characters.
  - /blog/bmi-tracking-guide/: "BMI Tracking Guide: How to Monitor Your Progress Effectively" loses "Effectively" (a claim the page
    doesn't measure); the <title> keeps "(2026)".
Each in the <title>, the H1, og:title, twitter:title and the Article headline; dateModified and lastmod follow.
usage: python3 research/cmb-066/apply.py [--check]"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
LOW, TRK, SM = 'blog/how-to-lower-bmi/index.html', 'blog/bmi-tracking-guide/index.html', 'sitemap.xml'
BASE = {LOW: 'dcf4d8ea5d41f442f679a9cb8bbe0073c699fd7417a9f6b3c026d01a4f067841',
        TRK: '82f45802cb613ebaee61d2e4d8335b44817a9638f39e7f105ef41f1122f5bce1',
        SM: '5797cbaa7444d00506a9c49c60b1c2836159face3cc2d5ef0a710fc705271af8'}
OLD_LOW, NEW_LOW = ('How to Lower BMI: Evidence-Based Strategies for Healthy Weight Loss',
                    'How to Lower BMI: CDC’s Steps for Healthy Weight Loss')
OLD_TRK, NEW_TRK = ('BMI Tracking Guide: How to Monitor Your Progress Effectively',
                    'BMI Tracking Guide: How to Monitor Your Progress')


def title_edits(old, new, dm_was):
    return [(f'<title>{old} | CalculateMyBMI</title>', f'<title>{new} | CalculateMyBMI</title>') if 'Lower' in old else
            (f'<title>{old} (2026)</title>', f'<title>{new} (2026)</title>'),
            (f'<h1>{old}</h1>', f'<h1>{new}</h1>'),
            (f'<meta property="og:title" content="{old}"', f'<meta property="og:title" content="{new}"'),
            (f'<meta name="twitter:title" content="{old}"', f'<meta name="twitter:title" content="{new}"'),
            (f'"headline": "{old}"', f'"headline": "{new}"'),
            (f'"dateModified": "{dm_was}"', f'"dateModified": "{TODAY}"')]


EDITS = {
    LOW: title_edits(OLD_LOW, NEW_LOW, '2026-11-14'),
    TRK: title_edits(OLD_TRK, NEW_TRK, '2026-11-16'),
    SM: [(f'<url><loc>https://calculatemybmi.net/blog/{slug}/</loc><lastmod>{was}</lastmod>',
          f'<url><loc>https://calculatemybmi.net/blog/{slug}/</loc><lastmod>{TODAY}</lastmod>')
         for slug, was in (('how-to-lower-bmi', '2026-11-14'), ('bmi-tracking-guide', '2026-11-16'))],
}
GONE = {LOW: ('Evidence-Based',), TRK: ('Effectively',)}


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
