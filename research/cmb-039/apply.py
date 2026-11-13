#!/usr/bin/env python3
"""CMB-039: puts the order-free percentiles into the four pages that print them (edits.json). Hash-guarded: each page must
be exactly as it stood before CMB-039 (sha256_before), every old string must occur once and no two may overlap, and the
result must hash to sha256_after. The edits came from a three-way merge (tools/): each page's old generator, run in a scratch
copy on its base commit with the stats before and after the rule change, gave the difference, applied where the live page
still held the generator's text. Only digits change, plus the chart page's schema dateModified (its visible text changed;
DEVLOG §4 dates rule) and its sitemap lastmod.
usage: python3 research/cmb-039/apply.py [--check]   (from the repo root; --check only verifies the pages are done)"""
import sys, json, hashlib, os, re

E = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edits.json'), encoding='utf-8'))
check = '--check' in sys.argv
for page, spec in E.items():
    s = open(page, encoding='utf-8').read()
    h = hashlib.sha256(s.encode()).hexdigest()
    if h == spec['sha256_after']:
        print(f'{page}: done ({len(spec["edits"])} edits)'); continue
    if check: raise SystemExit(f'{page}: not done')
    assert h == spec['sha256_before'], f'{page} changed since CMB-039 was made (hash guard)'
    pos = []
    for old, new in spec['edits']:
        assert s.count(old) == 1, (page, old[:80])
        pos.append((s.index(old), old, new))
    pos.sort()
    for (a, o, _), (b, _, _) in zip(pos, pos[1:]):
        assert a + len(o) <= b, (page, 'overlapping edits')
    for i, old, new in reversed(pos):
        s = s[:i] + new + s[i + len(old):]
    assert hashlib.sha256(s.encode()).hexdigest() == spec['sha256_after'], f'{page}: result differs from the reviewed one'
    open(page, 'w', encoding='utf-8', newline='').write(s)
    print(f'{page}: {len(pos)} edits applied')
LOC, OLD, NEW = 'https://calculatemybmi.net/body-fat-percentage-chart/', '2026-10-21', '2026-11-13'
sm = open('sitemap.xml', encoding='utf-8').read()
cur = re.search(rf'<loc>{re.escape(LOC)}</loc>\s*<lastmod>(\d{{4}}-\d{{2}}-\d{{2}})', sm).group(1)
if cur == NEW: print('sitemap lastmod: done')
elif check: raise SystemExit('sitemap lastmod not done')
else:
    assert cur == OLD, cur
    sm = re.sub(rf'(<loc>{re.escape(LOC)}</loc>\s*<lastmod>){OLD}', rf'\g<1>{NEW}', sm)
    open('sitemap.xml', 'w', encoding='utf-8', newline='').write(sm)
    print('sitemap lastmod', NEW)
