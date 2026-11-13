#!/usr/bin/env python3
"""CMB-039: registry nhanes-2011-2018-dxa after the move to order-free percentiles. Two statements in its notes go
stale (the men's chart percentiles and the two-rule remark); one note records the change and what it moved.
usage: python3 research/cmb-039/registry.py   (from the repo root; stops if a note is not as CMB-038 left it)"""
import csv, io, pathlib

CSV = pathlib.Path('research/data-sources.csv')
EDITS = [
    ('healthy 16.0 / 18.6 / 22.1 / 25.0 / 27.7, overweight',
     'healthy 15.9 / 18.6 / 22.1 / 25.0 / 27.6 (16.0 and 27.7 before CMB-039), overweight'),
    ("Percentiles: the weighted midpoint rule over distinct values (bfpc_stats.py applies it reading by reading after an "
     "unstable sort, so tied readings' order moves up to 5 of its 50 tool quartiles by 0.1 when printed; the two agree "
     "within 0.08).",
     'Percentiles: the weighted midpoint rule over distinct values, one rule in compute_bf.py, bfpc_stats.py, bcm_dxa.py '
     'and bfc_stats.py since CMB-039.'),
]
NOTE = (' CMB-039 (2026-11-13): every DXA percentile now comes from the weighted midpoint rule over distinct values '
        '(research/body-fat/compute_bf.py, research/body-fat-chart-build/bfpc_stats.py, research/chart-men-build/bcm_dxa.py; '
        'before, compute_bf.py and bfpc_stats.py placed each reading after an unstable sort, so the order of tied readings '
        'moved printed percentiles by 0.1). The twelve CDC files were re-read from Marko\'s download (DEMO, BMX and DXX, '
        'G to J; not kept in the repo): samples, counts, means, CIs and shares are unchanged (n 10,864 adults 20-59; women '
        '38.71, men 27.24). Printed changes: /body-fat-percentage-chart/ (age tables, BMI-figure labels, the rank tool\'s '
        'quartiles, the women 20-59 5th percentile in the FAQ 27.3%, the US median of men 20-39 26.1% and 40-59 28.2% in '
        'the chart table and the printable chart image), /blog/bmi-chart-men/ (healthy BMI 10th to 90th percentile 15.9% to '
        '27.6%), and the quartiles in the tool data of /body-fat-calculator/ and /women-bmi-calculator/; the CSV download '
        'is rebuilt by research/cmb-039/csv_download.py. The by_bmi medians the other pages quote (women 33.4 / 39.5 / 44.0, '
        'men 22.1 / 26.9 / 31.6, leanest tenth of overweight men 21.7) print the same. /blog/bmi-chart-men/ compares '
        'readings, recorded to 0.1, with the medians as printed (22.1 and 26.9; unrounded 22.1151 and 26.9027), so a man '
        'whose reading equals the printed median counts as having as much body fat; its shares stay 11.8% / 1.4% / 14.0%.')


def main():
    raw = CSV.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    r = next(x for x in rows if x['domain'] == 'nhanes-2011-2018-dxa')
    assert 'CMB-039' not in r['notes']
    for old, new in EDITS:
        assert r['notes'].count(old) == 1, old[:60]
        r['notes'] = r['notes'].replace(old, new)
    r['notes'] = r['notes'].rstrip() + NOTE
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print('nhanes-2011-2018-dxa notes updated;', len(rows), 'rows')


if __name__ == '__main__':
    main()
