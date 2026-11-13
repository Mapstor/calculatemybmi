#!/usr/bin/env python3
"""CMB-043: the SHA-256 of /childhood-obesity-statistics/'s CSV in the row form research/cmb-043/he112_check.js
gives CDC's Health E-Stat 112 tables (table|period|group|measure|percent|se|flag, sorted). Equal hashes mean every
row's percent, standard error and flag is CDC's. Exit 1 when the CSV no longer gives the hash checked on
2026-11-13 (then run he112_check.js on CDC's page again and update both hashes, here and in the Stage 1 audit).
usage: python3 research/cmb-043/he112_canon.py"""
import csv
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CSV = REPO / 'childhood-obesity-statistics' / 'childhood-obesity-nhanes-1963-2023.csv'
CHECKED = '4ac5923e653732381454885a9dbd389f9024e7af75eb223d2808160ccc897a5f'   # he112_check.js on CDC's page
FILE_SHA = '4ff775bf81e6955eaf2c5a85f36817e988922e6b5b89e143ee735345b99a75ed'  # the CSV file itself (audit.py)

rows = list(csv.reader(open(CSV, newline='', encoding='utf-8')))[2:]
lines = sorted('|'.join(r) for r in rows)
got = hashlib.sha256(('\n'.join(lines) + '\n').encode('utf-8')).hexdigest()
file_sha = hashlib.sha256(CSV.read_bytes()).hexdigest()
per = {t: sum(1 for r in rows if r[0] == t) for t in '123'}
print(f'{len(rows)} rows (table 1 {per["1"]}, 2 {per["2"]}, 3 {per["3"]}); rows sha256 {got}; file sha256 {file_sha}')
ok = got == CHECKED and file_sha == FILE_SHA
print('same as CDC\'s tables on 2026-11-13' if ok else 'CHANGED since the 2026-11-13 check against CDC\'s tables')
sys.exit(0 if ok else 1)
