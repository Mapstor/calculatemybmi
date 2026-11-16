#!/usr/bin/env python3
"""CMB-054: the registry and the page map for /blog/bmi-categories/'s claims pass (claims batch 7).
  - research/data-sources.csv: blog/bmi-categories joins pages_served on every row the page now cites; the GBMC and
    Flegal rows note the figures the page now prints per category.
  - research/page-map.csv: the page's data_source becomes cdc-adult-bmi-categories instead of "CDC adult categories; WHO
    classification", which check_sources.py failed.
usage: python3 research/cmb-054/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-categories'
CITED = ('who-trs-854', 'who-trs-894-obesity', 'who-2004-asian-bmi', 'cdc-adult-bmi-categories', 'cdc-about-bmi',
         'cdc-child-bmi-categories', 'cdc-losing-weight', 'nhlbi-1998-obesity-guidelines', 'gbmc-2016-bmi-mortality',
         'flegal-2013-jama-mortality', 'winter-2014-bmi-mortality-65', 'nhanes-adult-weight-trends',
         'nhanes-adult-obesity-2021-2023', 'nhanes-underweight', 'nci-obesity-cancer', 'medlineplus-unintentional-weight-loss',
         'nimh-eating-disorders', 'nice-ng246-ethnicity-thresholds', 'odphp-physical-activity-guidelines',
         'wing-2011-look-ahead', 'provencher-2018-nfl-combine')
NOTES = {
    'gbmc-2016-bmi-mortality': (' CMB-054: /blog/bmi-categories/ gives the band for each category: 1.51 at 15.0 to 18.4 (all '
                                'three thinness grades), 1.13 at 18.5 to 19.9, lowest at 20.0 to 24.9, 1.07 at 25.0 to 27.4, '
                                '1.20 at 27.5 to 29.9, 1.45 at 30.0 to 34.9, 1.94 at 35.0 to 39.9, 2.76 at 40.0 to 59.9 (the '
                                'highest), each against 22.5 to 24.9; and the main analysis\'s never-smokers without known '
                                'disease and the first five years (5) left out.'),
    'flegal-2013-jama-mortality': (' CMB-054: /blog/bmi-categories/ also prints grade 1 obesity (30 to 34.9), 0.95, as "no '
                                   'clear difference" (its 95% CI, 0.88 to 1.01, spans 1).'),
}


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
    by = {x['domain']: x for x in rows}
    for d in CITED:
        served = [s.strip() for s in by[d]['pages_served'].split(';') if s.strip()]
        if SLUG not in served:
            by[d]['pages_served'] = ';'.join(served + [SLUG])
            n += 1
    for d, note in NOTES.items():
        if 'CMB-054' not in by[d]['notes']:
            by[d]['notes'] = (by[d]['notes'].rstrip() + note).strip()
            n += 1
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'cdc-adult-bmi-categories'
    if 'CMB-054' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-054: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
