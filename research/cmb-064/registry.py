#!/usr/bin/env python3
"""CMB-064: the registry and the page map for the claims pass's close-out (claims batch 15).
  - research/page-map.csv: the four live pages whose data_source was still free text, which check_sources.py failed, get
    the registry row their claims rest on: blog (the CDC line, cdc-losing-weight), blog/bmi-by-age (NCHS Data Brief 508,
    nhanes-adult-obesity-2021-2023), blog/bmi-formula (CDC's formula page, cdc-calculating-bmi) and blog/bmi-for-athletes
    (provencher-2018-nfl-combine). What is left failing is the seven planned pages, not built yet.
  - research/data-sources.csv: blog joins pages_served on cdc-losing-weight; gbmc-2016-bmi-mortality gets a note on the
    passage /blog/healthy-bmi-range/ words as the paper does (CMB-013), so the reviewed probe hits there trace to the row.
usage: python3 research/cmb-064/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
DATA_SOURCE = {
    'blog': 'cdc-losing-weight',
    'blog/bmi-by-age': 'nhanes-adult-obesity-2021-2023',
    'blog/bmi-formula': 'cdc-calculating-bmi',
    'blog/bmi-for-athletes': 'provencher-2018-nfl-combine',
}
GBMC_NOTE = (' CMB-064: /blog/healthy-bmi-range/ also says, as CMB-013 read it in the paper (research/cmb-013-healthy-range/'
             'FIX.md): crude analyses that ignored smoking and existing disease gave exaggerated risks for underweight and '
             'made overweight look protective, and the authors reproduced a 2013 review\'s lower risk for overweight only '
             '"with inadequate control" for those biases, not in the strict analysis.')


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
    for slug, d in DATA_SOURCE.items():
        assert by[d]['status'] == 'verified', d
    lw = by['cdc-losing-weight']
    served = [s.strip() for s in lw['pages_served'].split(';') if s.strip()]
    if 'blog' not in served:
        lw['pages_served'] = ';'.join(served + ['blog'])
        n += 1
    g = by['gbmc-2016-bmi-mortality']
    if 'CMB-064' not in g['notes']:
        g['notes'] = (g['notes'] + GBMC_NOTE).strip()
        n += 1
    return n


def page_map(rows):
    n = 0
    for r in rows:
        if r['slug'] in DATA_SOURCE:
            before = dict(r)
            r['data_source'] = DATA_SOURCE[r['slug']]
            if 'CMB-064' not in r['notes']:
                r['notes'] = (r['notes'] + ' CMB-064: data_source set to the registry row the page\'s claims rest on; the '
                              'other rows that list this page in pages_served hold the rest.').strip()
            n += int(before != r)
    return n


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'rows changed')
