#!/usr/bin/env python3
"""CMB-061: research/stage1-audit/manual.json for /blog/body-fat-vs-bmi/: the entries for the three lines CMB-061 changed
go ("You're athletic or muscular, ... older (#+) ...", "Both individuals have the same BMI (# - "overweight") ..." and the
"#%" tile, value 30, which was the unsourced "30% of normal BMI individuals" stat, not an illustration); new: the
scenario 3 caption's BMI 26 (its category) and its sentence on the provisional ranges (15% and 30% are the two
hypothetical men; 19.9 is just under Table 4's 20%).
usage: python3 research/cmb-061/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/body-fat-vs-bmi/'
NEW = [
    {'page': PAGE, 'sig': 'Both have a BMI of #, overweight.', 'classes': 'B', 'why': 'the category of BMI 26 (CMB-061)',
     'checks': [{'target': 1, 'kind': 'catname', 'expr': '__A.cat($1)', 'text': 'overweight',
                 'label': 'category of that BMI (getBMICategory)'}]},
    {'page': PAGE, 'sig': 'On the provisional ranges for men aged # to #, #% body fat is healthy (# to #%) and #% is very high '
                          '(#% or more) (Gallagher et al., #).',
     'classes': ['-', '-', 'D', '-', 'B', 'D', '-', '-'],
     'why': "two hypothetical men (15% and 30%); 19.9 is just under the 20% where Gallagher's Table 4 puts BMI 25 for men "
            "aged 20 to 39 (CMB-061)",
     'checks': [{'target': 5, 'kind': 'num', 'expr': '20 - 0.1', 'label': "just under Table 4's 20% (men 20-39, BMI 25)",
                 'dec': 1}]},
]
DROP = ("You're athletic or muscular, making specific body composition goals, older (#+)",
        'Both individuals have the same BMI (#')


def key(e):
    return (e['page'], e['sig'], e.get('value'))


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    n0 = len(m['entries'])
    m['entries'] = [e for e in m['entries'] if not (e['page'] == PAGE and (e['sig'].startswith(DROP)
                    or (e['sig'] == '#%' and e.get('value') == 30)))]
    dropped = n0 - len(m['entries'])
    have = {key(e) for e in m['entries']}
    add = [e for e in NEW if key(e) not in have]
    m['entries'].extend(add)
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {len(add)} added, {dropped} dropped')


if __name__ == '__main__':
    main()
