#!/usr/bin/env python3
"""CMB-044 STATE-SOURCES: S on /obesity-rate-by-state/. Two of its numbers sat next to a link to the other survey,
so the audit read them against the wrong row: the survey-comparison figure's caption links only NCHS Data Brief 508,
though its left half is BRFSS (24.2-39.7%, 2025), and the Gallup sentence's "measured 40.3%" (NHANES) sits next to the
Gallup link alone. Each gets its own source by linking words already on the page, so no visible text changes and the
page's dateModified stays; the sitemap lastmod follows the new links (§4). The page and the sitemap are checked by
SHA-256; every marker must occur once.
usage: python3 research/cmb-044/apply.py [--check]   (--check applies in memory and writes nothing)
Run order from main: registry.py, manual.py, apply.py."""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PAGE = 'obesity-rate-by-state/index.html'
BASE = {PAGE: '3a12926571883327fe459d80d4cc503e0c12aab0921c0ff1accced8010737970',
        'sitemap.xml': '55f06385c7144c19f059b64b9e494cb9271bc4a92e76d37abde40eeed34a0a8d'}
MAPS = 'https://www.cdc.gov/obesity/data-and-statistics/adult-obesity-prevalence-maps.html'
DB508 = 'https://www.cdc.gov/nchs/products/databriefs/db508.htm'
EDITS = {
    PAGE: [
        ('State estimates: BRFSS 2025. National measured estimate',
         f'State estimates: <a href="{MAPS}" rel="noopener">BRFSS 2025</a>. National measured estimate'),
        ('against the measured 40.3%.</p>', f'against the <a href="{DB508}" rel="noopener">measured 40.3%</a>.</p>'),
    ],
    'sitemap.xml': [
        ('<loc>https://calculatemybmi.net/obesity-rate-by-state/</loc><lastmod>2026-10-12</lastmod>',
         f'<loc>https://calculatemybmi.net/obesity-rate-by-state/</loc><lastmod>{TODAY}</lastmod>'),
    ],
}


def main():
    out = {}
    for rel, sha in BASE.items():
        text = (REPO / rel).read_text(encoding='utf-8')
        got = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if got != sha:
            sys.exit(f'{rel}: not the base this batch was written for (sha256 {got[:12]}, expected {sha[:12]})')
        for old, new in EDITS[rel]:
            if text.count(old) != 1:
                sys.exit(f'{rel}: "{old[:60]}" occurs {text.count(old)} times, expected 1')
            text = text.replace(old, new)
        out[rel] = text
    n = sum(len(v) for v in EDITS.values())
    if CHECK:
        print(f'check: {n} edits apply; nothing written')
        return
    for rel, text in out.items():
        (REPO / rel).write_text(text, encoding='utf-8')
    print(f'{n} edits applied; lastmod {TODAY}; wrote {len(out)} files')


if __name__ == '__main__':
    main()
