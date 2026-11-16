#!/usr/bin/env python3
"""CMB-063: the registry and the page map for /lean-body-mass/'s claims pass (claims batch 14).
  - research/data-sources.csv: lean-body-mass joins pages_served on the five rows it now cites for the first time
    (cdc-about-bmi, wang-2010-organ-metabolic-rates, provencher-2018-nfl-combine, gallagher-2000-bf-ranges,
    body-fat-method-validation). nhanes-2011-2018-dxa, james-1976-lbm and the formula rows already list it.
  - research/page-map.csv: the page's data_source becomes boer-1984-lbm (verified since CMB-038) instead of
    "Boer 1984; James 1976; Hume 1966 (primary citations to verify)", which check_sources.py failed.
usage: python3 research/cmb-063/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'lean-body-mass'
CITED = ('cdc-about-bmi', 'wang-2010-organ-metabolic-rates', 'provencher-2018-nfl-combine', 'gallagher-2000-bf-ranges',
         'body-fat-method-validation')


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
    w = by['wang-2010-organ-metabolic-rates']
    if 'CMB-063' not in w['notes']:
        w['notes'] = (w['notes'] + ' CMB-063: /lean-body-mass/ quotes the same two rates (13 and 4.5 kcal per kg a day) and '
                      'the same ratio, 2.9, and links the PubMed record (20962155) as /blog/bmi-and-metabolism/ does.').strip()
        n += 1
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'boer-1984-lbm'
    if 'CMB-063' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-063: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page (Boer, James and Hume rows for the formulas).').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
