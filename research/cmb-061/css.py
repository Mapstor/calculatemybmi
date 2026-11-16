#!/usr/bin/env python3
"""CMB-061: the two-person bars on /blog/body-fat-vs-bmi/ (.chart-compare-row, used on that page only; /blog/bmi-formula/
uses .chart-compare as a plain container) put the label between two bars in a 1fr auto 1fr grid, so at 390 px the left
bar is about 60 px wide and its "15% Body Fat" wraps out of the 24 px bar (seen in Chrome on the CMB-061 preview). On
phones the row now stacks, label first, and an empty mirror bar (decoration, no text; the scenario 3 rows) stays hidden;
the "What Each Metric Captures" rows keep both bars, which carry text. Refinement inside
the current look (CLAUDE.md R2); DESIGN.md records it.
usage: python3 research/cmb-061/css.py [--check]"""
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHECK = '--check' in sys.argv
CSS, DS = 'assets/css/styles.css', 'DESIGN.md'
BASE = {CSS: '7c2fdf10da2e8a5b720543513051989506023e7a245ce842996e8e1568f7443a',
        DS: '8b4ad3174742262bf439510ae4b51b35bc973cf9670db5b53cd0fac1dd261c45'}
CSS_ADD = """
/* CMB-061 — /blog/body-fat-vs-bmi/ (DESIGN.md "Old guides (CMB-040)"): the two-person bars (.chart-compare-row) stack on
   phones, the label above its bars, so "15% Body Fat" stays inside its bar; an empty mirror bar is decoration and hides. */
@media (max-width: 600px) { .chart-compare-row { grid-template-columns: 1fr; gap: 0.5rem; } .chart-compare-label { order: -1; text-align: left; } .chart-compare-bar.right:empty { display: none; } }
"""
DS_OLD = '\n### Category badges\n'
DS_NEW = ('\n- The two-person bars on `/blog/body-fat-vs-bmi/` (`.chart-compare-row`) stack below 600 px, the label above its '
          'bars, and an empty mirror bar hides there, so a bar\'s label stays inside the bar (CMB-061).\n\n### Category badges\n')


def main():
    for rel in (CSS, DS):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == CSS:
            src = src.rstrip('\n') + '\n' + CSS_ADD
        else:
            assert src.count(DS_OLD) == 1
            src = src.replace(DS_OLD, DS_NEW)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
