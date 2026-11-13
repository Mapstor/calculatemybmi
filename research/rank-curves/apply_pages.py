#!/usr/bin/env python3
"""CMB-033: write the 4-decimal rank curves (research/rank-curves/curves.json) into the inline scripts of /,
/men-bmi-calculator/ and /women-bmi-calculator/. Each array is replaced only where the page holds exactly the curve
the 2-decimal version of curves.json rounds to, so a page that changed since stops the run.
usage: python3 research/rank-curves/apply_pages.py"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
C = json.loads((REPO / 'research/rank-curves/curves.json').read_text())
# The 2-decimal curves the pages carried until CMB-033 (home_stats.json and wbc_stats.json at 2c67a8e^ hold them).
OLD = json.loads((REPO / 'research/rank-curves/curves_2dec.json').read_text())


def js(arr):
    return '[' + ','.join(f'{x:.4f}'.rstrip('0').rstrip('.') for x in arr) + ']'


def js2(arr):
    return '[' + ','.join(f'{x:.2f}'.rstrip('0').rstrip('.') for x in arr) + ']'


PAGES = {
    'index.html': [('a', 'adults'), ('m', 'men'), ('w', 'women')],
    'women-bmi-calculator/index.html': [('a', 'women'), ('y', 'women_20_39'), ('m', 'women_40_59'), ('o', 'women_60plus')],
    'men-bmi-calculator/index.html': [(None, 'men')],
}
for f, keys in PAGES.items():
    path = REPO / f
    t = path.read_text(encoding='utf-8')
    for key, name in keys:
        old, new = js2(OLD[name]), js(C[name]['p1_p99'])
        pat = (f'var Q={old};' if key is None else None)
        if key is None:
            assert t.count(pat) == 1, (f, name)
            t = t.replace(pat, f'var Q={new};')
        else:
            n = len(re.findall(re.escape(f'{key}:{old}'), t))
            assert n == 1, (f, key, name, n)
            t = t.replace(f'{key}:{old}', f'{key}:{new}')
    path.write_text(t, encoding='utf-8')
    print(f, 'curves written:', ', '.join(n for _, n in keys))
