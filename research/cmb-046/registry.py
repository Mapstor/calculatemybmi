#!/usr/bin/env python3
"""CMB-046: research/data-sources.csv's cdc-child-bmi-categories row gains CDC's Child and Teen BMI Calculator page as an
endpoint, with the sentence the kids results now quote in place of their bare pediatrician lines (read in Chrome,
2026-11-14). The Adult BMI Calculator page says the same; it is named in the note for the claims pass (§5).
usage: python3 research/cmb-046/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

CSV = Path(__file__).resolve().parents[2] / 'research' / 'data-sources.csv'
DOMAIN = 'cdc-child-bmi-categories'
URL = 'https://www.cdc.gov/bmi/child-teen-calculator/index.html'
NOTE = (' CMB-046 (read in Chrome, 2026-11-14): CDC\'s Child and Teen BMI Calculator page (endpoint) says "Persons may '
        'consider seeking advice from their health care providers about their BMI."; /kids-bmi-calculator/\'s results quote it. '
        'CDC\'s Adult BMI Calculator page (https://www.cdc.gov/bmi/adult-calculator/index.html) carries the same sentence.')

raw = CSV.read_text(encoding='utf-8')
rows = list(csv.DictReader(io.StringIO(raw)))
fields = list(rows[0].keys())
r = next(x for x in rows if x['domain'] == DOMAIN)
eps = [e.strip() for e in r['endpoint'].split(' ; ') if e.strip()]
changed = 0
if URL not in eps:
    r['endpoint'] = ' ; '.join(eps + [URL])
    changed += 1
if 'CMB-046' not in r['notes']:
    r['notes'] = (r['notes'].rstrip() + NOTE).strip()
    changed += 1
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
w.writeheader()
w.writerows(rows)
CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
print(f'{DOMAIN}: {changed} change(s)')
