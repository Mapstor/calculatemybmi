#!/usr/bin/env python3
"""CMB-050: research/stage1-audit/manual.json entry for /blog/how-to-lower-bmi/'s one new number the audit's rules can't
place on their own: CDC's "15-minute evening walk" in step 3 of the five steps, a paragraph whose only link is to the
page's own goals section (the steps' source is linked in the sentence above them).
usage: python3 research/cmb-050/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/how-to-lower-bmi/'
NEW = [
    {'page': PAGE, 'sig': 'Pick two or three short-term goals at a time, such as water instead of sugary drinks, a #-minute '
                          'evening walk or a vegetable with supper.', 'classes': 'C', 'row': 'cdc-losing-weight', 'exact': True,
     'why': "CDC's short-term goal examples, step 3 of its Steps for Losing Weight (CMB-050)"},
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
