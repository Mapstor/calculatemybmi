#!/usr/bin/env python3
"""CMB-036 SOURCES-1: hand classifications for the Stage 1 audit (research/stage1-audit/manual.json) on the batch's
pages: numbers whose registry row the audit cannot find from the sentence alone (chart bars and SVG card lines with
no link next to them) and labels that are not claims. usage: python3 research/cmb-036/manual.py (adds each entry once)
"""
import json
from pathlib import Path

MANUAL = Path(__file__).resolve().parent.parent / 'stage1-audit' / 'manual.json'
E = []
for side, cut in (('underweight / normal', '18.5'), ('normal / overweight', '25'), ('overweight / obese', '30')):
    E.append({'page': '/blog/bmi-categories/', 'sig': f'BMI #-#: near the {side} boundary', 'classes': 'D',
              'why': f'a heading naming the band around the {cut} cut-off (CMB-036)'})
for v, what in ((35.5, 'men, overweight'), (28.1, 'women, overweight'), (39.3, 'men, obesity'), (41.4, 'women, obesity')):
    E.append({'page': '/blog/bmi-chart-explained/', 'sig': '#%', 'classes': 'C', 'exact': True, 'value': v,
              'row': 'nhanes-adult-weight-trends',
              'why': f'a bar of the sex chart whose source line cites Health E-Stat 111: Table 1, 20 and older, '
                     f'age-adjusted, {what} (CMB-036)'})
E += [
    {'page': '/blog/bmi-chart-explained/', 'sig': '#-# years | # - # | The same cut-offs at every adult age (CDC).',
     'classes': ['C', 'D', '-', '-'], 'row': 'cdc-adult-bmi-categories',
     'why': "20: CDC's adults (20 and older); 64: the row ends where the table's 65+ row starts (CMB-036)"},
    {'page': '/blog/bmi-and-health-risks/', 'sig': 'Older adults (#+)', 'classes': 'D', 'exact': True,
     'why': 'a heading naming an age group (CMB-036)'},
    {'page': '/blog/bmi-limitations/', 'sig': 'NFL prospects: #% obese by BMI', 'classes': 'C',
     'row': 'provencher-2018-nfl-combine', 'why': 'the athlete card of the figure, Provencher 2018 (CMB-036)'},
    {'page': '/blog/bmi-limitations/', 'sig': 'but #% obese by body fat (#)', 'classes': 'C',
     'row': 'provencher-2018-nfl-combine', 'why': 'the athlete card of the figure, Provencher 2018 (CMB-036)'},
    {'page': '/blog/bmi-limitations/', 'sig': 'overweight cutoff # (not #)', 'classes': 'C',
     'row': 'ko-tang-2006-wpro-2000',
     'why': 'the ethnic-variation card: the 2000 Asia-Pacific proposal (WHO Western Pacific, IASO, IOTF), overweight '
            'from 23 instead of 25 (CMB-036)'},
]

d = json.loads(MANUAL.read_text(encoding='utf-8'))
have = {(e['page'], e['sig'], e.get('value')) for e in d['entries']}
add = [e for e in E if (e['page'], e['sig'], e.get('value')) not in have]
d['entries'] += add
MANUAL.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'{len(add)} entries added, {len(d["entries"])} in all')
