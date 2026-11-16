#!/usr/bin/env python3
"""CMB-059: research/stage1-audit/manual.json for /blog/bmi-history/.
  - new: the heading "BMI and Survival After 65" names the age of Winter et al.'s meta-analysis; a heading carries no
    link, so the row is named here;
  - gone: the entries for the two sentences CMB-059 cut ("The Body Mass Index has a #-year history ..." and "The same BMI
    at age # and # has different implications ...").
usage: python3 research/cmb-059/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/bmi-history/'
NEW = [
    {'page': PAGE, 'sig': 'BMI and Survival After #', 'classes': 'C', 'row': 'winter-2014-bmi-mortality-65',
     'why': 'a heading: the meta-analysis of people aged 65 and over, Winter 2014 (CMB-059)'},
]
DROP = ('The Body Mass Index has a #-year history',
        'The same BMI at age # and # has different implications')


def key(e):
    return (e['page'], e['sig'], e.get('value'))


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    n0 = len(m['entries'])
    m['entries'] = [e for e in m['entries'] if not (e['page'] == PAGE and e['sig'].startswith(DROP))]
    dropped = n0 - len(m['entries'])
    have = {key(e) for e in m['entries']}
    add = [e for e in NEW if key(e) not in have]
    m['entries'].extend(add)
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {len(add)} added, {dropped} dropped')


if __name__ == '__main__':
    main()
