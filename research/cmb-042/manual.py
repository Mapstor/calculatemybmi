#!/usr/bin/env python3
"""CMB-042 SOURCES-4: hand classifications for the Stage 1 audit (research/stage1-audit/manual.json) on the four guides.
Stat tiles, timeline years, headings and figure labels that carry a number but no link or author get the registry row
that holds them; reference-list fragments get theirs; one FAQ sentence's year gap is checked as arithmetic, and its
rounded ages are listed as labels.
usage: python3 research/cmb-042/manual.py   (idempotent)
"""
import json
from pathlib import Path

MANUAL = Path(__file__).resolve().parent.parent / 'stage1-audit' / 'manual.json'
MET, LOW, HIS, WHT = '/blog/bmi-and-metabolism/', '/blog/how-to-lower-bmi/', '/blog/bmi-history/', '/blog/waist-to-height-ratio/'
W = ' (CMB-042)'


def tile(page, sig, value, row, why):
    return {'page': page, 'sig': sig, 'classes': 'C', 'exact': True, 'value': value, 'row': row, 'why': why + W}


def row(page, sig, r, why, classes='C', **kw):
    return dict({'page': page, 'sig': sig, 'classes': classes, 'row': r, 'why': why + W}, **kw)


E = [
    tile(MET, '#%', 34.7, 'hirode-2020-metabolic-syndrome', 'the metabolic syndrome tile, Hirode & Wong 2020'),
    row(MET, 'US adults with it, #-#', 'hirode-2020-metabolic-syndrome', 'the tile label, NHANES 2011 to 2016'),
    tile(MET, '#x', 5, 'alberti-2009-metabolic-syndrome', 'the diabetes tile, Alberti 2009 ("5-fold")'),
    tile(MET, '#x', 2, 'alberti-2009-metabolic-syndrome', 'the cardiovascular tile, Alberti 2009 ("twice the risk")'),
    row(MET, 'Cardiovascular disease risk over #-# years', 'alberti-2009-metabolic-syndrome', 'the tile label, Alberti 2009'),
    row(MET, 'The American Thyroid Association says about # to # pounds', 'ata-thyroid-weight',
        'the thyroid FAQ names the ATA without a link'),
    tile(MET, '#.', 2009, 'alberti-2009-metabolic-syndrome', 'a reference-list year, Alberti 2009'),
    tile(MET, 'Am J Clin Nutr. #.', 1984, 'roza-shizgal-1984-harris-benedict', 'a reference-list year, Roza & Shizgal 1984'),
    tile(LOW, '#', 1.55, 'cappuccio-2008-sleep-obesity', 'the sleep tile, Cappuccio 2008 (pooled odds ratio)'),
    row(HIS, 'The Complete History of BMI: From Quetelet to Modern Medicine (#-#)', 'eknoyan-2008-quetelet',
        'the title and H1: the 1832 index (2026, the current year)', classes=['C', 'D']),
    tile(HIS, '#', 1832, 'eknoyan-2008-quetelet', 'a timeline year: the Quetelet index, Eknoyan 2008'),
    tile(HIS, '#', 1959, 'nuttall-2015-bmi-review', 'a timeline year: MetLife\'s 1959 tables, Nuttall 2015'),
    tile(HIS, '#', 1972, 'keys-1972-indices', 'a timeline year: Keys et al. 1972'),
    tile(HIS, '#', 1985, 'nih-1985-consensus-obesity', 'a timeline year: the NIH consensus conference'),
    tile(HIS, '#', 1995, 'who-trs-854', 'a timeline year: WHO TRS 854'),
    tile(HIS, '#', 1998, 'nhlbi-1998-obesity-guidelines', 'a timeline year: the NIH guidelines'),
    row(HIS, 'NIH sets # and #', 'nhlbi-1998-obesity-guidelines', 'a timeline label: the 1998 cut-offs'),
    tile(HIS, '# MetLife', 1959, 'nuttall-2015-bmi-review', 'the timeline figure label, Nuttall 2015'),
    row(HIS, 'The Birth of the Quetelet Index (#)', 'eknoyan-2008-quetelet', 'a heading: the 1832 index'),
    row(HIS, 'The Quetelet Index (#)', 'eknoyan-2008-quetelet', 'the formula box: the 1832 index'),
    row(HIS, 'Asian BMI Cutoffs (#)', 'who-2004-asian-bmi', 'a heading: WHO Expert Consultation 2004'),
    row(HIS, 'NIH and the # Cut-Offs', 'nhlbi-1998-obesity-guidelines', 'a heading and its contents entry'),
    row(HIS, '#: An NIH Consensus Conference', 'nih-1985-consensus-obesity', 'a heading: the 1985 conference'),
    row(HIS, '#: The Cut-Offs Used Today', 'nhlbi-1998-obesity-guidelines', 'a heading: the 1998 guidelines'),
    row(HIS, 'Adolphe Quetelet described the index in #, and it became known as the Quetelet index.',
        'eknoyan-2008-quetelet', 'FAQ: the 1832 index, Eknoyan 2008'),
    row(HIS, 'Ancel Keys and colleagues named it the body mass index in a # paper in the Journal of Chronic Diseases, # '
        'years later.', 'keys-1972-indices', 'FAQ: Keys 1972, and the gap from Quetelet\'s 1832 index', classes=['C', 'B'],
        checks=[{'target': 2, 'kind': 'num', 'expr': '$1 - 1832', 'dec': 0,
                 'label': 'years from the 1832 index to the 1972 paper'}]),
    row(HIS, 'So the formula is nearly # years old and the name BMI just over #.', None,
        'rounded ages: 2026 - 1832 = 194 and 2026 - 1972 = 54', classes='D'),
    row(HIS, 'Earlier weight standards came from insurers, such as Metropolitan Life', 'nuttall-2015-bmi-review',
        'FAQ: MetLife\'s 1959 tables, Nuttall 2015'),
    tile(HIS, 'Quetelet, A. (#).', 1835, 'eknoyan-2008-quetelet', 'a reference-list year: the 1835 book'),
    tile(HIS, '(#).', 1998, 'nhlbi-1998-obesity-guidelines', 'a reference-list year: the NIH guidelines'),
    row(HIS, 'The history of BMI, from Adolphe Quetelet', 'eknoyan-2008-quetelet',
        'the meta description: the 1832 index and the 1972 name, Eknoyan 2008'),
    row(WHT, 'NICE applies the same # boundary to both sexes and all ethnicities.',
        'nice-ng246-ethnicity-thresholds', 'an info card: NICE NG246'),
    row(HIS, "The Body Mass Index has a #-year history, from a Belgian mathematician's statistical curiosity to one of the "
        'most widely used health metrics in the world.', None, 'years since 1832, to the hundred', classes='B',
        checks=[{'target': 1, 'kind': 'num', 'expr': '2026 - 1832', 'label': '2026 minus 1832, rounded to the hundred',
                 'dec': -2}]),
    tile(WHT, '# - #', 0.4, 'nice-ng246-ethnicity-thresholds', 'a chart bar: NICE NG246 healthy central adiposity'),
    tile(WHT, '# - #', 0.5, 'nice-ng246-ethnicity-thresholds', 'a chart bar: NICE NG246 increased central adiposity'),
    tile(WHT, '# or more', 0.6, 'nice-ng246-ethnicity-thresholds', 'a chart bar: NICE NG246 high central adiposity'),
    row(WHT, 'Half your height is the waist at a ratio of #; a waist below it keeps the ratio under #:',
        'nice-ng246-ethnicity-thresholds', 'the waist table intro: the NICE boundary'),
    row(WHT, 'Height | Waist at a Ratio of #', 'nice-ng246-ethnicity-thresholds', 'the waist table header: the NICE boundary',
        region='table'),
    row(WHT, 'That is why NICE pairs the ratio with BMI for adults with a BMI under #.', 'nice-ng246-ethnicity-thresholds',
        'FAQ: NICE NG246, adults with a BMI under 35'),
]
for e in E:
    if e.get('row') is None:
        e.pop('row', None)
# entries for sentences this batch cut or rewrote (they printed as unused), and the old WHtR band entry, which took the
# NICE bands before the entries above could
GONE = [
    (HIS, 'Discover the fascinating #-year history of BMI.'),
    (HIS, "The Body Mass Index has a fascinating #-year journey from a Belgian mathematician's statistical curiosity to "
          'one of the most widely used health metrics in the world.'),
    (WHT, 'NICE applies the same # boundary to both sexes and all ethnicities, and to children from age #.'),
    (HIS, 'For the first # years after its creation, the Quetelet Index was used almost exclusively by statisticians and '
          'social scientists.'),
    (HIS, 'The term "Body Mass Index" (BMI) was coined # years later by American physiologist Ancel Keys in a # paper '
          'published in the Journal of Chronic Diseases.'),
    (HIS, "Its adoption as a medical diagnostic tool didn't occur until the #s-#s, over # years after its creation."),
    (HIS, 'The repurposing of his formula for individual health assessment came #+ years later, driven by needs that '
          'Quetelet never envisioned.'),
    (HIS, "He recommended BMI for population studies, not individual clinical diagnosis - echoing Quetelet's original "
          'intent from # years earlier.'),
    (HIS, 'So while the formula is nearly # years old, the name "BMI" is only about # years old.'),
    (HIS, 'BMI #-# may represent increased risk (vs #-# for general population)'),
    (LOW, 'The traditional teaching is that ~# kcal equals one pound of body fat, so a # kcal/day deficit gives ~# lb/week '
          'and # kcal/day gives ~# lb/week.'),
    (MET, '# lbs LBM'),
    (MET, '# lbs fat'),
    (MET, 'While thyroid disorders can affect metabolism and weight, they typically account for only modest weight changes '
          '(#-# pounds).'),
]
OLD_BAND = (WHT, '# - #')


def key(e):
    return e['page'], e['sig'], e.get('value'), e.get('nth')


d = json.loads(MANUAL.read_text(encoding='utf-8'))
before = len(d['entries'])
d['entries'] = [x for x in d['entries'] if (x['page'], x['sig']) not in GONE
                and not ((x['page'], x['sig']) == OLD_BAND and 'value' not in x)]
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
