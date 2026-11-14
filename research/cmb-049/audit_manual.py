#!/usr/bin/env python3
"""CMB-049: research/stage1-audit/manual.json entries for /blog/underweight-bmi-risks/'s new numbers that the audit's
rules can't place on their own: the GBMC bar chart (its BMI bands are labels, D; its hazard ratios are the study's, C
in gbmc-2016-bmi-mortality; its title), MedlinePlus's "10 pounds (4.5 kg) or 5% ... over 6 to 12 months" in a list item
with no link of its own, the Alliance helpline's hours and the 988 Lifeline number (phone numbers and hours, D).
usage: python3 research/cmb-049/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/underweight-bmi-risks/'
GBMC = 'gbmc-2016-bmi-mortality'
NEW = [
    {'page': PAGE, 'sig': 'BMI #-#', 'classes': 'D', 'exact': True,
     'why': "bar labels: the Global BMI Mortality Collaboration's BMI bands, 15.0 to under 18.5 written 15.0–18.4 (CMB-049)"},
    {'page': PAGE, 'sig': 'Risk of death by BMI (hazard ratio; # = BMI # to #)', 'classes': 'C', 'row': GBMC, 'exact': True,
     'why': "the GBMC chart's title: its reference band (CMB-049)"},
] + [{'page': PAGE, 'sig': '#', 'classes': 'C', 'row': GBMC, 'exact': True, 'value': v,
      'why': "a hazard ratio in the GBMC bar chart (CMB-049)"} for v in (1.51, 1.13, 1.0, 1.07, 1.2, 1.45, 1.94, 2.76)] + [
    {'page': PAGE, 'sig': "You have lost more than # pounds (# kg), or #% of your usual weight, within # to # months and don't know "
                          "why.", 'classes': 'C', 'row': 'medlineplus-unintentional-weight-loss', 'exact': True,
     'why': "MedlinePlus's criterion, in a list its paragraph links (CMB-049)"},
    {'page': PAGE, 'sig': '#:# am to #:# pm Eastern', 'classes': 'D',
     'why': "the helpline's number and hours (Alliance for Eating Disorders; registry alliance-eating-disorders-helpline, CMB-049)"},
    {'page': PAGE, 'sig': 'call or text #, the Suicide and Crisis Lifeline, or chat at #lifeline.org; in a life-threatening emergency, '
                          'call #', 'classes': 'D',
     'why': 'the 988 Lifeline number, as NIMH gives it (registry nimh-eating-disorders, CMB-049)'},
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
