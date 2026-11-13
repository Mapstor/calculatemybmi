#!/usr/bin/env python3
"""CMB-044: research/data-sources.csv's cdc-brfss-state-obesity row gains the two lines of CDC's maps page that
/obesity-rate-by-state/ words in its own way: the age comparison and the rule for a state with no estimate.
usage: python3 research/cmb-044/registry.py   (stops if the row already has its CMB-044 note)"""
import csv
import io
from pathlib import Path

CSV = Path(__file__).resolve().parents[2] / 'research' / 'data-sources.csv'
NOTE = (' CMB-044 (the maps page read in Chrome, 2026-11-13): "Middle-aged adults (40–59 years) are about 36% more '
        'likely to have obesity than younger adults (18–39 years) and 25% more likely to have obesity than older adults '
        '(60 and older)."; the maps\' and tables\' note on a state with no estimate: "*Sample size <50, the relative '
        'standard error (dividing the standard error by the prevalence) ≥30%, or no data in a specific year." The 2011-'
        '2025 CSV has no estimate for New Jersey 2019, Florida 2021, Kentucky and Pennsylvania 2023, Tennessee 2024, and '
        'California, Mississippi and Nevada 2025 (and the Virgin Islands 2025).')


def main():
    raw = CSV.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    r = next(x for x in rows if x['domain'] == 'cdc-brfss-state-obesity')
    assert 'CMB-044' not in r['notes'], 'already has its CMB-044 note'
    r['notes'] = (r['notes'].rstrip() + NOTE).strip()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print(f'cdc-brfss-state-obesity: CMB-044 note added; {len(rows)} rows')


if __name__ == '__main__':
    main()
