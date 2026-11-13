#!/usr/bin/env python3
"""CMB-044: hand classifications for the Stage 1 audit (research/stage1-audit/manual.json) on /obesity-rate-by-state/.
The one-year gaps are checked against the dataset (each state's only year with no estimate); "All 50 states" is the
number of states, not a statistic; the two lines about our own US page name the NHANES trend row they point to.
usage: python3 research/cmb-044/manual.py   (idempotent)
"""
import json
from pathlib import Path

MANUAL = Path(__file__).resolve().parent.parent / 'stage1-audit' / 'manual.json'
P = '/obesity-rate-by-state/'
W = ' (CMB-044)'
# the one year from 2011 to 2025 with no estimate for a state in the CSV the BRFSS row serves; -1 unless exactly one
GAP = ("(st => {{ const g = Array.from({{length: 15}}, (_, i) => String(2011 + i)).filter(y => __D.brfss[st][y] === "
       "undefined); return g.length === 1 ? Number(g[0]) : -1; }})")


def gap(target, *states):
    exprs = [GAP.format() + f"('{st}')" for st in states]
    expr = exprs[0] if len(exprs) == 1 else f"(a => a.every(x => x === a[0]) ? a[0] : -1)([{', '.join(exprs)}])"
    return {'target': target, 'kind': 'num', 'expr': expr, 'dec': 0,
            'label': ' and '.join(states) + ': the only year from 2011 to 2025 with no estimate in the CDC BRFSS CSV'}


E = [
    {'page': P, 'sig': 'Earlier one-year gaps: New Jersey (#), Florida (#), Kentucky and Pennsylvania (#) and Tennessee (#).',
     'classes': 'B', 'why': 'years the dataset has no estimate for' + W,
     'checks': [gap(1, 'New Jersey'), gap(2, 'Florida'), gap(3, 'Kentucky', 'Pennsylvania'), gap(4, 'Tennessee')]},
    {'page': P, 'sig': 'All # states, ranked by the share of adults with a BMI of # or higher in #.', 'classes': ['D', '-', '-'],
     'why': 'the number of US states (the table lists all 50, the three with no 2025 estimate labelled)' + W},
    {'page': P, 'sig': 'our US obesity statistics page has the full measured trend since #.', 'classes': 'C',
     'row': 'nhanes-adult-weight-trends', 'why': 'our US page: the NHANES series from 1960-1962' + W},
    {'page': P, 'sig': 'US obesity rate and statistics (measured, since #)', 'classes': 'C',
     'row': 'nhanes-adult-weight-trends', 'why': 'a related card: the NHANES series from 1960-1962' + W},
]


def key(e):
    return e['page'], e['sig'], e.get('value'), e.get('nth')


d = json.loads(MANUAL.read_text(encoding='utf-8'))
have = {key(x): x for x in d['entries']}
updated = added = 0
for e in E:
    if key(e) in have:
        have[key(e)].clear()
        have[key(e)].update(e)
        updated += 1
    else:
        d['entries'].append(e)
        added += 1
MANUAL.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'{updated} updated, {added} added, {len(d["entries"])} in all')
