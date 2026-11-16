#!/usr/bin/env python3
"""CMB-055: the registry and the page map for /blog/bmi-limitations/'s claims pass (claims batch 8).
  - research/data-sources.csv: blog/bmi-limitations joins pages_served on every row the page now cites; the DXA row notes
    the figures this page prints.
  - research/page-map.csv: the page's data_source becomes cdc-about-bmi instead of "Okorodudu 2010 Int J Obes and other
    primaries (to verify)", which check_sources.py failed.
usage: python3 research/cmb-055/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/bmi-limitations'
CITED = ('cdc-about-bmi', 'cdc-adult-bmi-categories', 'cdc-child-bmi-categories', 'cdc-losing-weight',
         'cdc-pregnancy-weight-gain', 'nhanes-adult-weight-trends', 'nhanes-2011-2018-dxa', 'rfm-woolcott-2018',
         'nhlbi-1998-obesity-guidelines', 'nice-ng246-ethnicity-thresholds', 'ashwell-2012-whtr-meta-analysis',
         'browning-2010-whtr-review', 'provencher-2018-nfl-combine', 'volpi-2004-muscle-aging', 'winter-2014-bmi-mortality-65',
         'who-2004-asian-bmi', 'gbmc-2016-bmi-mortality', 'niams-osteoporosis', 'eknoyan-2008-quetelet', 'trefethen-new-bmi')
NOTES = {
    'nhanes-2011-2018-dxa': (' CMB-055: /blog/bmi-limitations/ prints the healthy-BMI medians (women 33.4%, men 22.1%) and '
                             'middle halves (women 29.8% to 36.5%, men 18.6% to 25.0%), the women at a BMI of 23.5 to 24.4 '
                             '(median 35.5%, middle half 33.0% to 38.2%), relative fat mass within 5 points for 86% of men '
                             'and 74% of women (86.3, 74.3), and the documentation\'s "the most widely accepted method of '
                             'measuring body composition", all for adults aged 20 to 59 scanned 2011-2018.'),
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
        if 'CMB-055' not in by[d]['notes']:
            by[d]['notes'] = (by[d]['notes'].rstrip() + note).strip()
            n += 1
    return n


def page_map(rows, fields):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r['data_source'] = 'cdc-about-bmi'
    if 'CMB-055' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-055: claims pass; every claim sourced or cut, sources in the registry rows that '
                      'list this page.').strip()
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
