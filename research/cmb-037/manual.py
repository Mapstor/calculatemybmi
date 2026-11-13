#!/usr/bin/env python3
"""CMB-037 SOURCES-2: hand classifications for the Stage 1 audit (research/stage1-audit/manual.json) on batch 4a's
pages. Sentences with no link next to their numbers (the /blog/ hub's card texts, /privacy/'s plain-text terms) get the
registry row that holds them; an age group in a list is a label. Where a CMB-029 entry already keys the sentence (as an
outside fact with no row), that entry is updated in place, since the first entry that fits a sentence wins.
usage: python3 research/cmb-037/manual.py   (idempotent)
"""
import json
from pathlib import Path

MANUAL = Path(__file__).resolve().parent.parent / 'stage1-audit' / 'manual.json'
E = [
    {'page': '/blog/body-fat-vs-bmi/', 'sig': "You're athletic or muscular, making specific body composition goals, older "
     '(#+), or want the most accurate individual health assessment.', 'classes': 'D',
     'why': 'an age group in a list of situations (CMB-037; was "an age threshold with no source")'},
    {'page': '/blog/', 'sig': "From Quetelet's # index to Ancel Keys naming it BMI in # and the WHO categories.",
     'classes': 'C', 'row': 'eknoyan-2008-quetelet', 'why': "the BMI history card: Eknoyan 2008's dates (CMB-037)"},
    {'page': '/blog/', 'sig': 'Your waist divided by your height: the # boundary and how it compares with BMI.',
     'classes': 'C', 'row': 'nice-ng246-ethnicity-thresholds',
     'why': "the waist-to-height card: NICE's 0.5 boundary (increased central adiposity from 0.5) (CMB-037)"},
    {'page': '/privacy/', 'sig': 'GA# offers # or # months for user-level and event-level data; the setting in force here '
     'is the one selected on the property and can be viewed by the site operator.', 'classes': 'C',
     'row': 'google-analytics-data-retention', 'why': "GA4's retention options, Google's help page (CMB-037)"},
    {'page': '/privacy/', 'sig': 'The site is not directed at children under the age of # (or # in the EEA, depending on '
     'member state law).', 'classes': 'C', 'row': 'gdpr-article-8',
     'why': "COPPA's under 13 (ftc-coppa-rule) and GDPR Article 8's 16, which member states may lower to no less than "
            '13; the Article 8 row holds both numbers (CMB-037)'},
]
d = json.loads(MANUAL.read_text(encoding='utf-8'))
updated = added = 0
for e in E:
    old = [x for x in d['entries'] if x['page'] == e['page'] and x['sig'] == e['sig']]
    if old:
        old[0].clear()
        old[0].update(e)
        updated += 1
    else:
        d['entries'].append(e)
        added += 1
MANUAL.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'{updated} entries updated, {added} added, {len(d["entries"])} in all')
