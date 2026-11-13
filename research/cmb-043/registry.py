#!/usr/bin/env python3
"""CMB-043: research/data-sources.csv's nhanes-child-weight-trends row records the check of the childhood page's CSV
against Health E-Stat 112 as published, and the page's line on the 2020-2021 pause in CDC's own words.
usage: python3 research/cmb-043/registry.py   (stops if the row already has its CMB-043 note)"""
import csv
import io
from pathlib import Path

CSV = Path(__file__).resolve().parents[2] / 'research' / 'data-sources.csv'
NOTE = (' CMB-043 (Chrome, 2026-11-13): research/cmb-043/he112_check.js read Tables 1-3 of the live page and gave the '
        'same 278 rows as childhood-obesity-statistics/childhood-obesity-nhanes-1963-2023.csv (percent, standard '
        'error and flag; Table 3 percent and flag, 2017-2018 and Aug 2021-Aug 2023): SHA-256 of the sorted rows '
        '4ac5923e653732381454885a9dbd389f9024e7af75eb223d2808160ccc897a5f on both sides '
        '(research/cmb-043/he112_canon.py), so the file serves the Stage 1 audit as this row\'s dataset while its '
        'SHA-256 stays 4ff775bf81e6955eaf2c5a85f36817e988922e6b5b89e143ee735345b99a75ed. The page\'s technical notes: '
        '"Data collection was interrupted due to the COVID-19 pandemic in March 2020 and resumed in August 2021 with '
        'a new sample design that included no oversampling by race and Hispanic origin."; "NHANES included '
        'oversampling of total Hispanic people starting in 2007-2008 and of Asian non-Hispanic people starting in '
        '2011-2012."; Table 2\'s footnote 2 on 1966-1970: "Data are for adolescents ages 12-17, not 12-19".')


def main():
    raw = CSV.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    r = next(x for x in rows if x['domain'] == 'nhanes-child-weight-trends')
    assert 'CMB-043' not in r['notes'], 'already has its CMB-043 note'
    r['notes'] = (r['notes'].rstrip() + NOTE).strip()
    r['verified_date'] = '2026-11-13'
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print(f'nhanes-child-weight-trends: CMB-043 note added, verified 2026-11-13; {len(rows)} rows')


if __name__ == '__main__':
    main()
