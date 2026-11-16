#!/usr/bin/env python3
"""CMB-055: research/stage1-audit/manual.json for /blog/bmi-limitations/ after its claims pass. Three entries go with the
text they classified: the old intro ("#-year-old formula"), the second half of the figure's athlete line (the line is now
one sentence, which the "NFL prospects" entry already classes) and the Western Pacific line of the figure's Asian tile
(the tile now gives the 2004 WHO consultation, which the audit finds in its row).
usage: python3 research/cmb-055/audit_manual.py   (idempotent)"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'research/stage1-audit/manual.json'
PAGE = '/blog/bmi-limitations/'
DROP = {
    'Body Mass Index (BMI) has been the go-to health screening tool for decades, but mounting scientific evidence reveals '
    'significant flaws in this #-year-old formula.',
    'but #% obese by body fat (#)',
    'overweight cutoff # (not #)',
}


def main():
    m = json.loads(P.read_text(encoding='utf-8'))
    before = len(m['entries'])
    m['entries'] = [e for e in m['entries'] if not (e['page'] == PAGE and e['sig'] in DROP)]
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'manual.json: {before - len(m["entries"])} entries dropped')


if __name__ == '__main__':
    main()
