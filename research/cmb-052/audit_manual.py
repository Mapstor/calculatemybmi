#!/usr/bin/env python3
"""CMB-052: research/stage1-audit/manual.json entry for /blog/bmi-and-metabolism/: the years that close the references in
its sources box ("Science. 2021." splits into a sentence "2021."), which the audit's name rule tied to whichever
guideline the box names first once the box listed CDC, HHS and NCI pages too. A year closing a reference is a citation
detail (D), as the audit already classes years inside citations elsewhere.
usage: python3 research/cmb-052/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/bmi-and-metabolism/'
NEW = [
    {'page': PAGE, 'sig': '#.', 'classes': 'D', 'exact': True,
     'why': 'a year closing a reference in the sources box, a citation detail (CMB-052)'},
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
