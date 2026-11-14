#!/usr/bin/env python3
"""CMB-045: the registry and the page map for /age-bmi-calculator/'s D-14 rebuild.
  - research/page-map.csv: the page's wedge, data_source (nhanes-2021-2023-exam-files, its main dataset, instead of the
    free text that check_sources.py failed), status built and a note on the rebuild;
  - research/data-sources.csv: age-bmi-calculator joins pages_served on the ten rows the page cites, and
    nhanes-2021-2023-exam-files gains a CMB-045 note on what the page computes from it.
usage: python3 research/cmb-045/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'age-bmi-calculator'
ROWS = ('nhanes-2021-2023-exam-files', 'nhanes-anthropometric-reference', 'nhanes-adult-obesity-2021-2023', 'nhanes-2011-2018-dxa',
        'cdc-adult-bmi-categories', 'cdc-calculating-bmi', 'cdc-child-bmi-categories', 'winter-2014-bmi-mortality-65',
        'volpi-2004-muscle-aging', 'ada-2026-obesity-standards')
NOTE = (' CMB-045 (2026-11-14): /age-bmi-calculator/ ranks a BMI among US women or men aged 20-39, 40-59 or 60+ (the '
        "women's curves equal research/rank-curves/curves.json; the men's are new: 672 / 762 / 1,246 men, medians 27.3 / "
        '29.0 / 28.4) and prints BMI by decade for both sexes (median, middle half, 10th-90th, share 18.5-24.9) from '
        'research/age-calc-build/abc_stats.py, which stops unless the decade means equal research/average-weight/'
        "avgw_results.json, the women's figures equal wbc_stats.json and the obesity shares by age group equal NCHS Data "
        'Brief 508 for women, men and all adults (5,929).')
PM = {'wedge': ('Rank among US women or men in the same age group (20-39, 40-59, 60+; NHANES 2021-2023 percentiles) and '
                'the average BMI, weight and waist for the same sex and decade; CDC adult categories at every age from 20, '
                'Winter 2014 for 65+ in the §4 wording, under 20 handed to the kids calculator; built CMB-045'),
      'data_source': 'nhanes-2021-2023-exam-files', 'status': 'built',
      'notes': ('D-14 rebuild CMB-045 (research/age-calc-build/): gen_abc.py from abc_stats.json; page test '
                'abc_test_playwright.py; title, H1 and URL kept (D-28). Owns 60 keywords ("bmi calculator by age" 5,400 '
                'primary; "bmi calculator kg with age" 8,100; "bmi calculator women age" 5,400; "bmi for age calculator" '
                '5,400; "bmi age gender calculator" 1,900).')}


def rewrite(path, key, change):
    raw = path.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    n = change(rows)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r.update(PM)
    return int(before != r)


def registry(rows):
    n = 0
    by = {x['domain']: x for x in rows}
    for d in ROWS:
        r = by[d]
        served = [s.strip() for s in r['pages_served'].split(';') if s.strip()]
        if SLUG not in served:
            r['pages_served'] = ';'.join(served + [SLUG])
            n += 1
    r = by['nhanes-2021-2023-exam-files']
    if 'CMB-045' not in r['notes']:
        r['notes'] = (r['notes'].rstrip() + NOTE).strip()
        n += 1
    return n


if __name__ == '__main__':
    print('page-map.csv:', rewrite(R / 'page-map.csv', 'slug', page_map), 'row changed')
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', 'domain', registry), 'changes')
