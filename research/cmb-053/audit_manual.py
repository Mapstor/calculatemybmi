#!/usr/bin/env python3
"""CMB-053: research/stage1-audit/manual.json entries for /about/.
1. "in pooled data from 239 studies, the risk of death was lowest at a BMI of 20.0 to 24.9" quotes the GBMC 2016 bands
   (row gbmc-2016-bmi-mortality, notes: "lowest at a BMI of 20.0 to 24.9" for the minimum at 20.0-25.0), not a calculator
   category, so the audit's category check does not apply; the citation year is left to the rules.
2. "Nick Trefethen's 2013 New BMI proposal" in the FAQ answer that now also links CDC About BMI: the year is Trefethen's
   (row trefethen-new-bmi), not CDC's; "four body-fat methods" is left to the rules.
Signatures are number-blind (20.0 is one #) and written with straight quotes, as audit.py normalises them.
usage: python3 research/cmb-053/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/about/'
NEW = [
    {'page': PAGE, 'sig': 'the risk of death was lowest at a BMI of # to #', 'classes': ['C', 'C', 'C', '-'],
     'row': 'gbmc-2016-bmi-mortality',
     'why': "the GBMC's 239 studies and its lowest-risk band, 20.0 to 24.9 (minimal at 20.0-25.0), not a calculator category (CMB-053)"},
    {'page': PAGE, 'sig': "Nick Trefethen's # New BMI proposal", 'classes': ['C', '-'], 'row': 'trefethen-new-bmi',
     'why': "the year of Trefethen's proposal, in an answer that also links CDC (CMB-053)"},
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
