#!/usr/bin/env python3
"""CMB-057: /blog/underweight-bmi-risks/ title and H1, "Solutions" -> "When to Get Help".
D-28 ask from CMB-049 (§0 Waiting on owner): under D-01 the page ends in sourced help lines ("When to See a Doctor",
"Getting Help"), not treatment, so "Causes & Solutions" promised what the page does not hold. Marko, 2026-11-16: "ok
fix this". Changed: <title>, og:title, twitter:title, the Article JSON-LD headline and the H1; URL and everything else
kept. dateModified and lastmod follow (the H1 is visible text).
usage: python3 research/cmb-057/apply.py [--check]"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PG, SM = 'blog/underweight-bmi-risks/index.html', 'sitemap.xml'
BASE = {PG: '54b66cfc4830d352e550fc46ed9d49d4a2025ef9c401f2f9fd868cbff1cdd3f4',
        SM: '88d7ae969edd5ee4d90f0c406fa40a0babe074a4a15525b17fa5d7065f755d3b'}
OLD, NEW = 'Health Concerns, Causes & Solutions', 'Health Concerns, Causes & When to Get Help'
EDITS = [
    (f'<title>Underweight BMI Risks: {OLD} | CalculateMyBMI</title>',
     f'<title>Underweight BMI Risks: {NEW} | CalculateMyBMI</title>'),
    (f'<meta property="og:title" content="Underweight BMI Risks: {OLD}">',
     f'<meta property="og:title" content="Underweight BMI Risks: {NEW}">'),
    (f'<meta name="twitter:title" content="Underweight BMI Risks: {OLD}">',
     f'<meta name="twitter:title" content="Underweight BMI Risks: {NEW}">'),
    (f'"headline": "Underweight BMI Risks: {OLD}"', f'"headline": "Underweight BMI Risks: {NEW}"'),
    ('<h1>Underweight BMI Risks: Complete Guide to Health Concerns, Causes & Solutions</h1>',
     '<h1>Underweight BMI Risks: Complete Guide to Health Concerns, Causes & When to Get Help</h1>'),
    ('"dateModified": "2026-11-14"', f'"dateModified": "{TODAY}"'),
]


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:90]}'
    return src.replace(old, new)


def main():
    for rel in (PG, SM):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == PG:
            for old, new in EDITS:
                src = one(src, old, new, PG)
            assert 'Solutions' not in src, 'a "Solutions" is left'
        else:
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/underweight-bmi-risks/</loc><lastmod>2026-11-14</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/underweight-bmi-risks/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
