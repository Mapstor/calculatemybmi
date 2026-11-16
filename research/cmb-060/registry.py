#!/usr/bin/env python3
"""CMB-060: the registry and the page map for /blog/bmi-chart-explained/'s claims pass (claims batch 11).
  - research/data-sources.csv: blog/bmi-chart-explained joins pages_served on the rows it now cites.
  - research/page-map.csv: the page's data_source becomes cdc-adult-bmi-categories instead of "Quetelet formula", which
    check_sources.py failed.
usage: python3 research/cmb-060/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-chart-explained'
CITED = ('nih-bmi-table-2022', 'cdc-losing-weight', 'who-obesity-fact-sheet', 'nice-ng246-ethnicity-thresholds',
         'gallagher-2000-bf-ranges', 'medlineplus-unintentional-weight-loss', 'nhlbi-1998-obesity-guidelines',
         'nci-obesity-cancer', 'wing-2011-look-ahead', 'who-2004-asian-bmi', 'nhanes-2021-2023-exam-files',
         'nhanes-2011-2018-dxa', 'cdc-about-bmi', 'cdc-adult-bmi-categories', 'gbmc-2016-bmi-mortality', 'who-trs-894-obesity')


def rewrite(path, change):
    text = path.read_text(encoding='utf-8')
    rd = csv.DictReader(io.StringIO(text))
    rows = list(rd)
    n = change(rows)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=rd.fieldnames, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def registry(rows):
    n = 0
    by = {x['domain']: x for x in rows}
    for d in CITED:
        served = [s.strip() for s in by[d]['pages_served'].split(';') if s.strip()]
        if SLUG not in served:
            by[d]['pages_served'] = ';'.join(served + [SLUG])
            n += 1
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'cdc-adult-bmi-categories'
    if 'CMB-060' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-060: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
