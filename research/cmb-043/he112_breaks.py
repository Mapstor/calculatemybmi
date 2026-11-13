#!/usr/bin/env python3
"""CMB-043: show the Stage 1 audit reads /childhood-obesity-statistics/ against Health E-Stat 112 cell by cell.

usage: python3 research/cmb-043/he112_breaks.py

Copies the served site (the repo without .git and research/) to two temp folders, serves each on a free port and runs
research/stage1-audit/audit.py on the childhood page:

  control  the copy as it is: no number of the page is "not in its row"
  broken   the same copy with three planted errors, each to be reported "not in its row":
    1. a cell off by 0.1        Table 1, Aug 2021-Aug 2023, severe obesity 7.0% -> 7.1%
    2. another cell's value     Table 2, 1999-2000, ages 6-11 15.1% -> 14.8% (14.8 is a value of the file, in other
                                cells, so only the keyed reading can catch it)
    3. a prose number           "Teen boys stood out at 26.0%" -> 26.4% (no such value in the file)
  pin      the dataset loads only while the CSV's SHA-256 is the one checked against CDC's tables: with any other
           pinned hash load_datasets() leaves the row without a dataset

Exit 0 only when the control is clean, all three are reported, and the pin holds.
"""
import importlib.util
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT = REPO / 'research' / 'stage1-audit' / 'audit.py'
PAGE = '/childhood-obesity-statistics/'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def copy_site(dst):
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns('.git', 'research', 'node_modules', '__pycache__', '_snap'))


def plant(root):
    p = root / PAGE.strip('/') / 'index.html'
    s = p.read_text(encoding='utf-8')
    for old, new in (('Aug 2021–Aug 2023</th><td>21.1%</td><td>7.0%</td>', 'Aug 2021–Aug 2023</th><td>21.1%</td><td>7.1%</td>'),
                     ('1999–2000</th><td>10.3%</td><td>15.1%</td>', '1999–2000</th><td>10.3%</td><td>14.8%</td>'),
                     ('Teen boys stood out at 26.0%', 'Teen boys stood out at 26.4%')):
        if s.count(old) != 1:
            sys.exit(f'cannot plant: "{old}" occurs {s.count(old)} times')
        s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')


def run_audit(root):
    port = free_port()
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1'], cwd=root,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        out = Path(root) / '_audit'
        r = subprocess.run([sys.executable, str(AUDIT), f'http://127.0.0.1:{port}', '--out', str(out), '--pages', PAGE],
                           capture_output=True, text=True)
        print('   ', next((x for x in r.stdout.splitlines() if x.startswith('pages audited')), '(no summary line)'))
        rep = json.loads((out / 'report.json').read_text(encoding='utf-8'))
        return next(P for P in rep['pages'] if P['page'] == PAGE)
    finally:
        srv.terminate()
        srv.wait()


def pin_holds():
    spec = importlib.util.spec_from_file_location('audit', AUDIT)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    with_pin = 'nhanes-child-weight-trends' in audit.load_datasets()
    audit.HE112_SHA256 = '0' * 64
    without = 'nhanes-child-weight-trends' in audit.load_datasets()
    return with_pin and not without


def main():
    with tempfile.TemporaryDirectory() as tmp:
        control, broken = Path(tmp) / 'control', Path(tmp) / 'broken'
        copy_site(control)
        copy_site(broken)
        plant(broken)
        print('control (unbroken copy):')
        c0 = run_audit(control)['c_not_in_row']
        print('broken (three planted errors):')
        c1 = run_audit(broken)['c_not_in_row']
    want = [('7.1', 'dataset has 7.0'), ('14.8', 'dataset has 15.1'), ('26.4', None)]
    caught = 0
    for n, (num, note) in enumerate(want, 1):
        hit = [c for c in c1 if c['number'] == num and (note is None or note in c.get('note', ''))]
        caught += bool(hit)
        print(f"  {'caught' if hit else 'MISSED'}  {n}. {num}" + (f' ({note})' if note else ' (no such value in the file)'))
    pin = pin_holds()
    print(f'  control: {len(c0)} not in its row; pin: {"holds" if pin else "BROKEN"}')
    print(f'{caught} of 3 planted errors reported; control clean: {"yes" if not c0 else "no"}')
    sys.exit(0 if caught == 3 and not c0 and pin else 1)


if __name__ == '__main__':
    main()
