#!/usr/bin/env python3
"""CMB-051: research/stage1-audit/manual.json entries for /blog/bmi-and-health-risks/'s new numbers that the audit's
rules can't place on their own: the GBMC bar chart (its BMI bands are labels, D; its hazard ratios and its title are
the study's, C in gbmc-2016-bmi-mortality), as CMB-049 did for the same chart on /blog/underweight-bmi-risks/; and the
page description (239 studies, the GBMC's count, C; 13 cancers, a count in prose, D).
usage: python3 research/cmb-051/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/bmi-and-health-risks/'
GBMC = 'gbmc-2016-bmi-mortality'
NEW = [
    {'page': PAGE, 'sig': 'BMI #-#', 'classes': 'D', 'exact': True,
     'why': "bar labels: the Global BMI Mortality Collaboration's BMI bands, 15.0 to under 18.5 written 15.0–18.4 (CMB-051)"},
    {'page': PAGE, 'sig': 'Risk of death by BMI (hazard ratio; # = BMI # to #)', 'classes': 'C', 'row': GBMC, 'exact': True,
     'why': "the GBMC chart's title: its reference band (CMB-051)"},
] + [{'page': PAGE, 'sig': '#', 'classes': 'C', 'row': GBMC, 'exact': True, 'value': v,
      'why': "a hazard ratio in the GBMC bar chart (CMB-051)"} for v in (1.51, 1.13, 1.0, 1.07, 1.2, 1.45, 1.94, 2.76)] + [
    {'page': PAGE, 'sig': 'The risk of death across the BMI range, from # studies, and what NIH and NCI say about diabetes, '
                          'heart disease, stroke, # cancers, sleep apnea and more.', 'classes': ['C', 'D'], 'row': GBMC,
     'exact': True, 'why': "the page description: the GBMC's 239 studies (C) and NCI's 13 cancers, a count in prose (D) (CMB-051)"},
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
