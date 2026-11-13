#!/usr/bin/env python3
"""CMB-039: writes /body-fat-percentage-chart/body-fat-percentiles-nhanes-2011-2018.csv from research/body-fat/bf_results.json,
row for row as research/body-fat/gen_bf.py wrote it in B1 (that script rebuilds the old page, so it must not run again).
Columns: mean and se as stored; p5, p10, p25, p50, p75, p90, p95 are the 5%-step percentiles ('p' indices 0, 1, 4, 9, 14,
17, 18), which compute_bf.py stores at 2 decimals by the weighted midpoint rule over distinct values (since CMB-039).
usage: python3 csv_download.py BF_RESULTS_JSON OUT_CSV"""
import sys, csv, json

BF, OUT = sys.argv[1], sys.argv[2]
R = json.load(open(BF))
GROUPS = ['8-11', '12-15', '16-19', '20-29', '30-39', '40-49', '50-59', '20-39', '40-59', '20-59']
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['# Percent body fat (whole-body DXA, NHANES BCA option) of US residents, NHANES 2011-2018 pooled (weights '
                'WTMEC2YR/4), pregnant excluded. Calculated by calculatemybmi.net from CDC public-use files; CC BY 4.0.'])
    w.writerow(['sex', 'age_group', 'mean', 'se', 'p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'n'])
    for sx, k in (('male', 'm'), ('female', 'f')):
        for g in GROUPS:
            S = R[k][g]; p = S['p']
            w.writerow([sx, g, S['mean'], S['se'], p[0], p[1], p[4], p[9], p[14], p[17], p[18], S['n']])
print('written', OUT)
