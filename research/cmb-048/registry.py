#!/usr/bin/env python3
"""CMB-048: the registry and the page map for the calculators hub's rewritten answers.
  - research/data-sources.csv: calculators joins pages_served on the rows its FAQ now cites;
  - research/page-map.csv: the hub's data_source becomes cdc-adult-bmi-categories (the categories every adult
    calculator uses) instead of "structural hub", which check_sources.py failed.
usage: python3 research/cmb-048/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'calculators'
CITED = ('cdc-about-bmi', 'cdc-adult-bmi-categories', 'cdc-child-bmi-categories', 'nhanes-adult-weight-trends',
         'nhlbi-1998-obesity-guidelines', 'provencher-2018-nfl-combine', 'orsama-2014-weight-rhythms',
         'nhanes-2011-2018-dxa', 'trefethen-new-bmi', 'winter-2014-bmi-mortality-65')


def rewrite(path, change):
    rows = list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8'))))
    fields = list(rows[0].keys())
    n = change(rows)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
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
    if 'CMB-048' not in r['notes']:
        r['notes'] = (r['notes'].rstrip() + ' CMB-048: FAQ answers and card claims sourced (claims pass); the nine '
                      'examples and the FAQ are checked by research/cmb-027/hub_examples_playwright.py.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
