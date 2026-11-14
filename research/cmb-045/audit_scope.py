#!/usr/bin/env python3
"""CMB-045: /age-bmi-calculator/ leaves the Stage 1 audit (research/stage1-audit/audit.py) and its hand classifications
(research/stage1-audit/manual.json) go with it. Its D-14 rebuild has a page test of its own
(research/age-calc-build/abc_test_playwright.py, in scripts/page_scores.py PAGE_TESTS) that checks every number on the
page against abc_stats.json and the files it reproduces, as on the other fifteen D-14 pages with a test; the audit's nine
entries for the page classified sentences the rebuild removed.
usage: python3 research/cmb-045/audit_scope.py   (idempotent)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / 'stage1-audit' / 'audit.py'
MANUAL = HERE.parent / 'stage1-audit' / 'manual.json'
P = '/age-bmi-calculator/'

src = AUDIT.read_text(encoding='utf-8')
old = "'/about/', '/contact/', '/privacy/', '/terms/', '/blog/', '/age-bmi-calculator/', '/kids-bmi-calculator/',"
new = "'/about/', '/contact/', '/privacy/', '/terms/', '/blog/', '/kids-bmi-calculator/',"
note = ("# /age-bmi-calculator/ left this list in CMB-045: its D-14 page test (research/age-calc-build/abc_test_playwright.py)\n"
        "# checks every number on it, as on the other D-14 pages with a test.\n")
if old in src:
    src = src.replace(old, new, 1).replace('PAGES = [\n', note + 'PAGES = [\n', 1)
    AUDIT.write_text(src, encoding='utf-8')
    print('audit.py: /age-bmi-calculator/ removed from PAGES')
else:
    assert new in src and note in src, 'audit.py PAGES is not what this script expects'
    print('audit.py: already done')

# the report's totals follow the page list (they said "of 25" since CMB-029)
src = AUDIT.read_text(encoding='utf-8')
old_t = "    L.append('# Stage 1 audit: every number on the 25 pages Stage 1 hadn\\'t covered (CMB-029)')"
new_t = ("    L.append(f'# Stage 1 audit: every number on the {len(PAGES)} pages Stage 1 hadn\\'t covered (CMB-029; '\n"
         "             '/age-bmi-calculator/ moved to its page test in CMB-045)')")
old_n = "    L.append(f'- Pages audited: **{R[\"pages_audited\"]}** of 25, skipped: **{len(R[\"pages_skipped\"])}**')"
new_n = "    L.append(f'- Pages audited: **{R[\"pages_audited\"]}** of {len(PAGES)}, skipped: **{len(R[\"pages_skipped\"])}**')"
if old_t in src:
    src = src.replace(old_t, new_t, 1).replace(old_n, new_n, 1)
    AUDIT.write_text(src, encoding='utf-8')
    print('audit.py: the report counts the page list')
else:
    assert new_t in src and new_n in src, 'audit.py report lines are not what this script expects'

d = json.loads(MANUAL.read_text(encoding='utf-8'))
before = len(d['entries'])
d['entries'] = [e for e in d['entries'] if e.get('page') != P]
MANUAL.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'manual.json: {before - len(d["entries"])} entries for {P} removed, {len(d["entries"])} in all')
