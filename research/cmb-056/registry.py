#!/usr/bin/env python3
"""CMB-056: the registry and the page map for /blog/waist-to-height-ratio/'s claims pass (claims batch 9).
  - research/data-sources.csv: blog/waist-to-height-ratio joins pages_served on the rows the page now cites.
  - research/page-map.csv: the page's data_source becomes nice-ng246-ethnicity-thresholds instead of "NICE 2022 WHtR
    guidance; primary meta-analyses (verify)", which check_sources.py failed.
usage: python3 research/cmb-056/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/waist-to-height-ratio'
CITED = ('nhlbi-1998-obesity-guidelines', 'nci-obesity-cancer', 'nice-ng246-ethnicity-thresholds',
         'ashwell-2012-whtr-meta-analysis', 'cdc-about-bmi', 'nhanes-2021-2023-exam-files')
NOTES = {}


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
        if 'CMB-056' not in by[d]['notes']:
            by[d]['notes'] = (by[d]['notes'].rstrip() + note).strip()
            n += 1
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'nice-ng246-ethnicity-thresholds'
    if 'CMB-056' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-056: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
