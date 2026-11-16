#!/usr/bin/env python3
"""CMB-054: research/stage1-audit/manual.json for /blog/bmi-categories/ after its claims pass.
  - The healthy range's width: the sentence now reads "about 6.5 BMI points" (18.5 to under 25), so the check keeps its
    expression and gives one decimal.
  - The 6-year-old example: "perfectly normal" became "in CDC's healthy weight category, boys and girls alike"; same check.
  - Two entries go with their sentences (the "continuous spectrum" illustration and the "one-size-fits-all" ages).
  - New: the GBMC band in the key takeaways (20.0 to 24.9 is the study's lowest-risk band, not a calculator category), and
    CDC's own "18.5 to less than 25" for healthy weight in the Category 4 text and an FAQ answer.
Signatures are number-blind (20.0 is one #) and written with straight quotes, as audit.py normalises them.
usage: python3 research/cmb-054/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/bmi-categories/'
RESIG = {
    'This is a wide range - a #-point span that encompasses a substantial weight difference at any given height.':
        ('That is a span of about # BMI points, a sizeable weight difference at any height.', {'dec': 1}),
    'A #-year-old with a BMI of # is perfectly normal, but adult categories would classify them as severely underweight.':
        ("A #-year-old with a BMI of # is in CDC's healthy weight category, boys and girls alike, but adult categories would "
         "classify them as severely underweight.", {}),
}
DROP = {
    'A person with a BMI of # is not meaningfully healthier than one at # - the categories represent points on a continuous '
    'spectrum.',
    'One-size-fits-all cutoffs: The same categories apply to a #-year-old woman and a #-year-old man, despite very different '
    'body compositions and health implications.',
}
NEW = [
    {'page': PAGE, 'sig': 'the risk of death was lowest at a BMI of # to # and higher below and above it',
     'classes': ['C', 'C', 'C', '-'], 'row': 'gbmc-2016-bmi-mortality',
     'why': "the GBMC's 239 studies and its lowest-risk band, 20.0 to 24.9 (minimal at 20.0-25.0), not a calculator "
            "category (CMB-054)"},
    {'page': PAGE, 'sig': 'CDC calls a BMI from # to just under # healthy weight', 'classes': ['C', 'C'],
     'row': 'cdc-adult-bmi-categories', 'why': 'CDC\'s healthy weight, "18.5 to less than 25" (CMB-054)'},
    {'page': PAGE, 'sig': 'CDC counts all of # to just under # as healthy weight', 'classes': ['C', 'C'],
     'row': 'cdc-adult-bmi-categories', 'why': 'CDC\'s healthy weight, "18.5 to less than 25" (CMB-054)'},
]


def key(e):
    return (e['page'], e['sig'], e.get('value'))


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    n = 0
    keep = []
    for e in m['entries']:
        if e['page'] == PAGE and e['sig'] in DROP:
            n += 1
            continue
        if e['page'] == PAGE and e['sig'] in RESIG:
            sig, extra = RESIG[e['sig']]
            e['sig'] = sig
            for c in e.get('checks', []):
                c.update(extra)
            e['why'] = e['why'].rstrip() + (' (CMB-054: sentence reworded)' if 'CMB-054' not in e['why'] else '')
            n += 1
        keep.append(e)
    m['entries'] = keep
    have = {key(e) for e in m['entries']}
    add = [e for e in NEW if key(e) not in have]
    m['entries'].extend(add)
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {n} entries changed or dropped, {len(add)} added')


if __name__ == '__main__':
    main()
