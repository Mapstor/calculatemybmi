#!/usr/bin/env python3
"""CMB-062: research/stage1-audit/manual.json for /blog/bmi-tracking-guide/: the "#% Loss" label entry goes with the
four-step strip it described (5%, 10%, 15%, "Target BMI"); the table header keeps its own entry.
usage: python3 research/cmb-062/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/bmi-tracking-guide/'
NEW = []


def key(e):
    return (e['page'], e['sig'], e.get('value'))


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    n0 = len(m['entries'])
    m['entries'] = [e for e in m['entries'] if not (e['page'] == PAGE and e['sig'] == '#% Loss')]
    dropped = n0 - len(m['entries'])
    have = {key(e) for e in m['entries']}
    add = [e for e in NEW if key(e) not in have]
    m['entries'].extend(add)
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {len(add)} added, {dropped} dropped')


if __name__ == '__main__':
    main()
