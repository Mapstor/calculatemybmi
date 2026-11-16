#!/usr/bin/env python3
"""CMB-059: the registry and the page map for /blog/bmi-history/'s claims pass (claims batch 10).
  - research/data-sources.csv: blog/bmi-history joins pages_served on the four rows it now cites for the first time
    (cdc-adult-bmi-categories, gallagher-2000-bf-ranges, body-fat-method-validation, cdc-losing-weight); the NICE row
    records 1.9.12 and 1.9.13 as read in Chrome on 2026-11-16 (BMI with caution in adults with high muscle mass, and in
    people aged 65 and over).
  - research/page-map.csv: the page's data_source becomes eknoyan-2008-quetelet instead of "Primary historical sources
    (Quetelet 1835; Keys 1972)", which check_sources.py failed.
usage: python3 research/cmb-059/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-history'
CITED = ('cdc-adult-bmi-categories', 'gallagher-2000-bf-ranges', 'body-fat-method-validation', 'cdc-losing-weight')
NICE_NOTE = (' CMB-059 (read in Claude in Chrome, 2026-11-16): 1.9.12 [2022] "Interpret BMI with caution in adults with high '
             'muscle mass because it may be a less accurate measure of central adiposity in this group"; 1.9.13 [2022] '
             '"Interpret BMI with caution in people aged 65 and over, taking into account comorbidities, conditions that may '
             'affect functional capacity and the possible protective effect of having a slightly higher BMI when older".')


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
    r = by['nice-ng246-ethnicity-thresholds']
    if 'CMB-059' not in r['notes']:
        r['notes'] = r['notes'].rstrip() + NICE_NOTE
        n += 1
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'eknoyan-2008-quetelet'
    if 'CMB-059' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-059: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
