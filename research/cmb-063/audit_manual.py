#!/usr/bin/env python3
"""CMB-063: research/stage1-audit/manual.json for /lean-body-mass/. The "fit athlete ... sedentary office worker" entry goes
with its sentence; the same two men come back in "Same BMI, Different Build", with four entries:
  - the two men: their height, weight and body fat are an illustration (D); the lean masses are 190 lb less 15% and 30% (B);
  - their BMI, 27.3 = 703 x 190 / 70^2, and its category (getBMICategory: overweight);
  - Gallagher's men aged 20 to 39: 19.9 is just under the 20% Table 4 puts at BMI 25 (B), 15 and 30 the two men (D), and
    "a BMI of 30" the category cut-off (B);
  - the Boer estimate both men get, typed into the page's calculator (A: 5 ft 10 in, 190 lb, male).
Plus the muscle-to-fat ratio at rest, 13 / 4.5 = 2.9 (B).
usage: python3 research/cmb-063/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/lean-body-mass/'
DROP = ('A #\'#" man weighing # lbs could be a fit athlete with #% body fat (LBM of # lbs) or a sedentary office worker at #% '
        'body fat (LBM of # lbs).', 'so a kilogram of muscle uses about # times as much.')
TWO_MEN = {'ft': 5, 'in': 10, 'lb': 190, 'sex': 'male'}
NEW = [
    {'page': PAGE, 'sig': 'Take two men, both #\'#" and # lbs, one at #% body fat (LBM of # lbs) and one at #% (LBM of # lbs).',
     'classes': ['-', 'D', 'D', 'D', 'D', 'B', 'D', 'B'],
     'why': 'two illustrative men (CMB-063; "two" is the first number); their lean mass is 190 lb less 15% and 30% body fat',
     'checks': [{'target': 6, 'kind': 'num', 'expr': '$4 * (1 - $5 / 100)', 'label': '190 lb at 15% body fat', 'dec': 1},
                {'target': 8, 'kind': 'num', 'expr': '$4 * (1 - $7 / 100)', 'label': '190 lb at 30% body fat', 'dec': 0}]},
    {'page': PAGE, 'sig': 'puts both at #, overweight.', 'classes': 'B',
     'why': 'the BMI of 5 ft 10 in and 190 lb, and its category (CMB-063)',
     'checks': [{'target': 1, 'kind': 'num', 'expr': '703 * 190 / (70 * 70)', 'label': 'BMI of 190 lb at 70 in', 'dec': 1},
                {'target': 1, 'kind': 'catname', 'expr': '__A.cat($1)', 'text': 'overweight',
                 'label': 'category of that BMI (getBMICategory)'}]},
    {'page': PAGE, 'sig': 'provisional ranges put #% body fat within the range that matches a healthy BMI (# to #%) and #% above '
                          'the #% that matches a BMI of # (Gallagher et al., #).',
     'classes': ['-', '-', 'D', '-', 'B', 'D', '-', 'B', '-'],
     'why': 'Gallagher Table 4, men 20 to 39: 8% at BMI 18.5, 20% at 25, 25% at 30; 15 and 30 are the two men; 19.9 is just '
            'under 20; 30 is the obesity cut-off (CMB-063)',
     'checks': [{'target': 5, 'kind': 'num', 'expr': '20 - 0.1', 'label': 'just under Table 4\'s 20% (men 20-39, BMI 25)',
                 'dec': 1}]},
    {'page': PAGE, 'sig': 'it gives both men # lbs of lean mass and #% body fat.', 'classes': 'A',
     'why': 'the Boer estimate for both men, from the page\'s calculator (CMB-063)',
     'checks': [{'target': 1, 'kind': 'A', 'calc': PAGE, 'units': 'us', 'inputs': TWO_MEN,
                 'claims': [{'tok': 1, 'read': 'lbm_lb'}, {'tok': 2, 'read': 'bf'}]}]},
    {'page': PAGE, 'sig': 'A kilogram of muscle at rest uses about # times as much as a kilogram of fat.', 'classes': 'B',
     'why': 'the ratio of the two rates in the sentence before, 13 and 4.5 kcal per kg a day (Wang et al., 2010) (CMB-063)',
     'checks': [{'target': 1, 'kind': 'num', 'expr': '13 / 4.5', 'label': '13 / 4.5', 'dec': 1}]},
]


def key(e):
    return (e['page'], e['sig'], e.get('value'), e.get('nth'))


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    n0 = len(m['entries'])
    mine = {e['sig'] for e in NEW}
    m['entries'] = [e for e in m['entries'] if not (e['page'] == PAGE and (e['sig'] in DROP or e['sig'] in mine))]
    dropped = n0 - len(m['entries'])  # includes this batch's own entries, re-added below
    have = {key(e) for e in m['entries']}
    add = [e for e in NEW if key(e) not in have]
    m['entries'].extend(add)
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {len(add)} added, {dropped} dropped')


if __name__ == '__main__':
    main()
