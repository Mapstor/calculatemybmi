#!/usr/bin/env python3
"""CMB-056: research/stage1-audit/manual.json entry for /blog/waist-to-height-ratio/: the new heading "If Your Ratio Is
0.5 or More" (and its TOC line) names NICE's boundary for increased central adiposity; a heading carries no link, so the
row is named here.
usage: python3 research/cmb-056/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/waist-to-height-ratio/'
NEW = [
    {'page': PAGE, 'sig': 'If Your Ratio Is # or More', 'classes': 'C', 'row': 'nice-ng246-ethnicity-thresholds',
     'why': "a heading naming NICE's 0.5 boundary for increased central adiposity (CMB-056)"},
]


def key(e):
    return (e['page'], e['sig'], e.get('value'))


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    have = {key(e) for e in m['entries']}
    add = [e for e in NEW if key(e) not in have]
    m['entries'].extend(add)
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {len(add)} entries added')


if __name__ == '__main__':
    main()
