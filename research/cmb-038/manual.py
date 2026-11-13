#!/usr/bin/env python3
"""CMB-038 SOURCES-3: hand classifications for the Stage 1 audit (research/stage1-audit/manual.json) on batch 4b's
pages. Headings that pair a name with a year ("Boer Formula (1984)") and stat tiles with no text of their own get the
registry row that holds them; the 703 FAQ entry follows its rewritten sentence; entries for sentences this batch cut
are removed (they printed as unused).
usage: python3 research/cmb-038/manual.py   (idempotent)
"""
import json
from pathlib import Path

MANUAL = Path(__file__).resolve().parent.parent / 'stage1-audit' / 'manual.json'
RND = ('(70 * Math.abs(1 / Math.pow(__A.in2m(1), 2) / __A.kg2lb(1) - 703) / 703) < $2 ? $2 : -1')
E = [
    {'page': '/blog/bmi-formula/', 'sig': 'Adolphe Quetelet (#)', 'classes': 'C', 'row': 'eknoyan-2008-quetelet',
     'why': "a heading: Quetelet's 1832 index, Eknoyan 2008 (CMB-038)"},
    {'page': '/blog/bmi-formula/', 'sig': 'US cut-offs (#)', 'classes': 'C', 'row': 'nhlbi-1998-obesity-guidelines',
     'why': "a heading: NIH's 1998 guidelines (CMB-038)"},
    {'page': '/blog/bmi-formula/', 'sig': 'Height to the power #', 'classes': 'B',
     'why': "the New BMI exponent in the formula card (CMB-038)",
     'checks': [{'target': 1, 'kind': 'srcnum', 'fn': 'calculateNewBMI', 'label': 'a number literal in calculateNewBMI'}]},
    {'page': '/blog/bmi-formula/', 'sig': "Rounding it to # changes a BMI by less than #, and CDC's own formula uses #: "
     'weight (lb) / height (in)² x # (CDC).', 'classes': ['-', 'B', '-', '-'],
     'why': 'the error of rounding 703.07 to 703 (CMB-038: the sentence names CDC\'s formula)',
     'checks': [{'target': 2, 'kind': 'num', 'expr': RND,
                 'label': 'at a BMI of 70, the difference 703.07 vs 703 makes is under this', 'dec': 2}]},
    {'page': '/lean-body-mass/', 'sig': 'Boer Formula (#)', 'classes': 'C', 'row': 'boer-1984-lbm',
     'why': 'a heading: Boer 1984 (CMB-038)'},
    {'page': '/lean-body-mass/', 'sig': 'James Formula (#)', 'classes': 'C', 'row': 'james-1976-lbm',
     'why': 'a heading: the James equations of the 1976 DHSS/MRC report (CMB-038)'},
    {'page': '/lean-body-mass/', 'sig': 'Hume Formula (#)', 'classes': 'C', 'row': 'hume-1966-lbm',
     'why': 'a heading: Hume 1966 (CMB-038)'},
    {'page': '/lean-body-mass/', 'sig': 'How BMI is read at different ages, including research on adults #+.',
     'classes': 'C', 'row': 'winter-2014-bmi-mortality-65',
     'why': "the age calculator's card: its Winter 2014 lines are about adults 65 and over (CMB-038)"},
    {'page': '/blog/bmi-for-athletes/', 'sig': '#%', 'classes': 'C', 'exact': True, 'value': 53.4,
     'row': 'provencher-2018-nfl-combine', 'why': 'the NFL tile, Provencher 2018 (CMB-038)'},
    {'page': '/blog/bmi-for-athletes/', 'sig': '#%', 'classes': 'C', 'exact': True, 'value': 8.9,
     'row': 'provencher-2018-nfl-combine', 'why': 'the NFL tile, Provencher 2018 (CMB-038)'},
    {'page': '/blog/bmi-for-athletes/', 'sig': '#%', 'classes': 'C', 'exact': True, 'value': 20.2,
     'row': 'lambert-2012-football-dxa', 'why': 'the college football tile, Lambert 2012 (CMB-038)'},
    {'page': '/blog/bmi-for-athletes/', 'sig': '#%', 'classes': 'C', 'exact': True, 'value': 21.7,
     'row': 'nhanes-2011-2018-dxa',
     'why': "the US men tile: the 10th percentile of body fat at BMI 25-29.9, our calculation (CMB-038)"},
    {'page': '/blog/bmi-for-athletes/', 'sig': 'Why BMI misclassifies muscular athletes: #% of NFL prospects had a BMI '
     'of #+, but #% had obesity by body fat.', 'classes': ['C', '-', 'C'], 'row': 'provencher-2018-nfl-combine',
     'why': 'the meta description, Provencher 2018 (CMB-038)'},
    {'page': '/blog/bmi-tracking-guide/', 'sig': 'Men: # or more', 'classes': 'C', 'row': 'who-2008-waist-hip-ratio',
     'why': 'WHO 2008 Table A1, waist-hip ratio (CMB-038)'},
    {'page': '/blog/bmi-tracking-guide/', 'sig': 'Women: # or more', 'classes': 'C', 'row': 'who-2008-waist-hip-ratio',
     'why': 'WHO 2008 Table A1, waist-hip ratio (CMB-038)'},
    {'page': '/blog/bmi-tracking-guide/', 'sig': 'Starting Point | #% Loss | #% Loss | BMI Change', 'classes': 'D',
     'region': 'table', 'why': "a label (the example's loss steps the table works out) (CMB-038)"},
]
GONE = [
    ('/blog/bmi-formula/', 'It is rounded to # for simplicity because the difference is clinically insignificant - it '
     'changes the BMI result by less than # points.'),
    ('/blog/bmi-formula/', 'Since BMI categories span ranges of #-# points (e.g., normal is # to #), this tiny rounding '
     'error has absolutely no impact on which category a person falls into.'),
    ('/blog/bmi-tracking-guide/', 'Track trends: Focus on #-week moving averages rather than individual measurements'),
    ('/blog/bmi-tracking-guide/', 'Clothes can add #-# lbs depending on what you are wearing.'),
]


def key(e):
    return e['page'], e['sig'], e.get('value'), e.get('nth')


d = json.loads(MANUAL.read_text(encoding='utf-8'))
before = len(d['entries'])
d['entries'] = [x for x in d['entries'] if (x['page'], x['sig']) not in GONE]
removed = before - len(d['entries'])
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
print(f'{removed} removed, {updated} updated, {added} added, {len(d["entries"])} in all')
