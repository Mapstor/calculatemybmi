#!/usr/bin/env python3
"""CMB-062: the registry and the page map for /blog/bmi-tracking-guide/'s claims pass (claims batch 13).
  - research/data-sources.csv: blog/bmi-tracking-guide joins pages_served on the two rows it now cites for the first time
    (cdc-about-bmi, body-fat-method-validation).
  - research/page-map.csv: the page's data_source becomes madigan-2015-self-weighing instead of "Primary sources (verify)",
    which check_sources.py failed.
usage: python3 research/cmb-062/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-tracking-guide'
CITED = ('cdc-about-bmi', 'body-fat-method-validation')


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
    r['data_source'] = 'madigan-2015-self-weighing'
    if 'CMB-062' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-062: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
