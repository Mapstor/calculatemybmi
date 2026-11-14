#!/usr/bin/env python3
"""CMB-046 SOURCES-5: /body-fat-calculator/'s sources line cited "Siri WE, 1956" next to Topend Sports' Jackson-Pollock
page, which prints only the density equations (§5). Topend's Siri page prints the equation the calculator uses ("% Body
Fat = (495 / Body Density) - 450") and cites Siri WE (1961) in Brozek & Henschel, Techniques for measuring body
composition, pp. 223-244 (registry body-fat-equations, endpoint; re-read in Chrome 2026-11-14). The line now names
Siri 1961 with that page. The visible text changes, so dateModified and the sitemap lastmod move to the commit's day
(§4). research/body-fat-calculator-build/gen_bfcalc.py, the page's build record, gets the same line. Files are checked
by SHA-256 before any edit; every marker must occur once.
usage: python3 research/cmb-046/apply.py [--check]   (--check applies in memory and writes nothing)
Run order from main: registry.py, apply.py."""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PAGE, GEN = 'body-fat-calculator/index.html', 'research/body-fat-calculator-build/gen_bfcalc.py'
BASE = {PAGE: '3e89b6085cdeda135109ced9d419036c291f92d9ee5e7f7f7e5a0552179196b1',
        'sitemap.xml': '24ef1e6569aa412f265e27dff67f2449b2c1da1c5b07055d0c049e29a053a1c0'}
JP = 'https://www.topendsports.com/testing/density-jackson-pollock.htm'
SIRI = 'https://www.topendsports.com/testing/siri-equation.htm'
SERRA = 'https://periodicos.uninove.br/saude/article/download/1421/1197'
EDITS = {
    PAGE: [
        (f'Siri WE, 1956; as printed by <a href="{JP}" target="_blank" rel="noopener">Topend Sports (Jackson-Pollock body '
         f'density)</a> and in <a href="{SERRA}" target="_blank" rel="noopener">Serra AJ, et al. ConScientiae Saúde '
         '2009;8(1):19–24</a>.</li>',
         f'as printed by <a href="{JP}" target="_blank" rel="noopener">Topend Sports (Jackson-Pollock body density)</a> and in '
         f'<a href="{SERRA}" target="_blank" rel="noopener">Serra AJ, et al. ConScientiae Saúde 2009;8(1):19–24</a>. Siri WE, '
         f'1961, as printed by <a href="{SIRI}" target="_blank" rel="noopener">Topend Sports (Siri equation)</a>.</li>'),
        ('"dateModified": "2026-10-28"', f'"dateModified": "{TODAY}"'),
    ],
    'sitemap.xml': [
        ('<url><loc>https://calculatemybmi.net/body-fat-calculator/</loc><lastmod>2026-10-28</lastmod>',
         f'<url><loc>https://calculatemybmi.net/body-fat-calculator/</loc><lastmod>{TODAY}</lastmod>'),
    ],
    GEN: [
        ("    f'Siri WE, 1956; as printed by {ext(U[\"topend\"], \"Topend Sports (Jackson-Pollock body density)\")} and in '\n"
         "    f'{ext(U[\"jp\"], \"Serra AJ, et al. ConScientiae Saúde 2009;8(1):19–24\")}.',",
         "    f'as printed by {ext(U[\"topend\"], \"Topend Sports (Jackson-Pollock body density)\")} and in '\n"
         "    f'{ext(U[\"jp\"], \"Serra AJ, et al. ConScientiae Saúde 2009;8(1):19–24\")}. Siri WE, 1961, as printed by '\n"
         "    f'{ext(\"" + SIRI + "\", \"Topend Sports (Siri equation)\")} (CMB-046).',"),
    ],
}


def main():
    for rel, edits in EDITS.items():
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        if rel in BASE:
            got = hashlib.sha256(src.encode('utf-8')).hexdigest()
            assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        for old, new in edits:
            assert src.count(old) == 1, f'{rel}: marker found {src.count(old)} times: {old[:70]}'
            src = src.replace(old, new)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: {len(edits)} edit(s){" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
