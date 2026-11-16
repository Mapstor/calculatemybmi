#!/usr/bin/env python3
"""CMB-052: the registry and the page map for /blog/bmi-and-metabolism/'s claims pass (claims batch 5).
  - research/data-sources.csv: one new row, fothergill-2016-biggest-loser (Fothergill et al., Obesity 2016, the
    PubMed abstract read in Chrome on 2026-11-14); pontzer-2021-energy-expenditure gains a note with the numbers the
    page now prints; ata-thyroid-weight gains the thyroid lines the page paraphrases (read in Chrome 2026-11-14);
    blog/bmi-and-metabolism joins pages_served on every row the page now cites.
  - research/page-map.csv: the page's data_source becomes pontzer-2021-energy-expenditure instead of "Mifflin-St Jeor
    1990; Harris-Benedict (primary citations)", which check_sources.py failed.
usage: python3 research/cmb-052/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-and-metabolism'
TODAY = '2026-11-14'
CITED = ('fothergill-2016-biggest-loser', 'pontzer-2021-energy-expenditure', 'ata-thyroid-weight', 'wang-2010-organ-metabolic-rates',
         'volpi-2004-muscle-aging', 'hall-2011-energy-imbalance', 'niddk-health-risks', 'nci-obesity-cancer',
         'cdc-losing-weight', 'cdc-physical-activity-weight', 'odphp-physical-activity-guidelines', 'niddk-body-weight-planner',
         'cdc-healthy-eating-weight', 'cdc-about-bmi')
NEW = [
    dict(domain='fothergill-2016-biggest-loser',
         source='Fothergill E, Guo J, Howard L, et al. Persistent metabolic adaptation 6 years after "The Biggest Loser" '
                'competition. Obesity (Silver Spring) 2016;24(8):1612-9',
         publisher='Obesity (The Obesity Society); NIH intramural study (NIDDK)',
         url='https://pubmed.ncbi.nlm.nih.gov/27136388/', endpoint='https://doi.org/10.1002/oby.21538 ; PMC4989512',
         access='page', license='abstract quoted briefly; figures are facts', tier='A', cadence='static',
         granularity='study', format='HTML', key_required='no', attribution='Fothergill et al., Obesity 2016',
         verified_date=TODAY, next_check='2027-11-14',
         coverage='14 of 16 "Biggest Loser" competitors; DXA and indirect calorimetry at baseline, the end of the 30-week '
                  'competition and 6 years later',
         sample_note=('PubMed abstract (read in Chrome 2026-11-14): "Of the 16 “Biggest Loser” competitors originally '
                      'investigated, 14 participated in this follow-up study. Weight loss at the end of the competition was '
                      '(mean ± SD) 58.3 ± 24.9 kg (P < 0.0001), and RMR decreased by 610 ± 483 kcal/day (P = 0.0004). After '
                      '6 years, 41.0 ± 31.3 kg of the lost weight was regained (P = 0.0002), while RMR was 704 ± 427 '
                      'kcal/day below baseline (P < 0.0001) and metabolic adaptation was -499 ± 207 kcal/day (P < 0.0001)."; '
                      'metabolic adaptation "was defined as the residual RMR after adjusting for changes in body composition '
                      'and age"; conclusion: "Metabolic adaptation persists over time and is likely a proportional, but '
                      'incomplete, response to contemporaneous efforts to reduce body weight." Year 2016.'),
         status='verified', pages_served=SLUG,
         notes=('CMB-052: /blog/bmi-and-metabolism/ "Metabolic Adaptation", a takeaway and the FAQ on lasting damage (14, '
                '58.3 kg, 30 weeks, six years (6), 704, 499, 41.0 kg). A letter in the same journal (Kuchnia et al., 2016, '
                '"Overstated metabolic adaptation") disputes the size; the page reports the study as a small one.')),
]
PONTZER_NOTE = (' CMB-052: /blog/bmi-and-metabolism/ prints the coverage and the life stages: ages 8 days to 95 years, 29 '
                'countries, about 50% above adult values at about age 1 (~50%, ~1 year), adult levels by about 20, steady from '
                '20 to 60, even in pregnancy, then lower.')
ATA_NOTE = (' CMB-052 (read in Chrome 2026-11-14; ATA text, so paraphrased on the page): "Metabolism is the process of turning '
            'food into energy." At rest the energy used is the basal metabolic rate (BMR). "In thyroid disorders, high thyroid '
            'hormone levels raise BMR and low levels decrease BMR. However, BMR does not tell the whole story about weight and '
            'thyroid." The thyroid is "a butterfly-shaped gland located in the lower front of the neck" that makes thyroid '
            'hormones, which help the body use energy and stay warm.')


def rewrite(path, change):
    rows = list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8'))))
    fields = list(rows[0].keys())
    n = change(rows, fields)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def registry(rows, fields):
    n = 0
    have = {x['domain'] for x in rows}
    for r in NEW:
        if r['domain'] not in have:
            assert set(r) == set(fields), sorted(set(fields) ^ set(r))
            rows.append({k: r[k] for k in fields})
            n += 1
    by = {x['domain']: x for x in rows}
    for d in CITED:
        served = [s.strip() for s in by[d]['pages_served'].split(';') if s.strip()]
        if SLUG not in served:
            by[d]['pages_served'] = ';'.join(served + [SLUG])
            n += 1
    for d, note in (('pontzer-2021-energy-expenditure', PONTZER_NOTE), ('ata-thyroid-weight', ATA_NOTE)):
        m = by[d]
        if 'CMB-052' not in m['notes']:
            m['notes'] = (m['notes'].rstrip() + note).strip()
            m['verified_date'] = TODAY if d == 'ata-thyroid-weight' else m['verified_date']
            n += 1
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'pontzer-2021-energy-expenditure'
    if 'CMB-052' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-052: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
