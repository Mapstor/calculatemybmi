#!/usr/bin/env python3
"""CMB-029: plant 3 errors on a temp copy of the site and show audit.py reports each one.

usage: python3 research/stage1-audit/audit_breaks.py

Copies the served site (the repo without .git and research/) to two temp folders, serves each on a free port
(python3 -m http.server) and runs audit.py on the three affected pages, writing its report into the temp folder:

  control  the copy as it is: the three spots must NOT show up as findings
  broken   the same copy with three planted errors:
    1. a wrong example output   /blog/underweight-bmi-risks/  "would have a BMI of 17.3" -> 17.8
                                expected: an A mismatch (typed into the calculator, which prints 17.3)
    2. a wrong range cell       /blog/bmi-categories/  "Weight Ranges for Normal BMI by Height", 5'6" row,
                                "115 lbs (52 kg)" -> "117 lbs (52 kg)"
                                expected: a B mismatch (weightBounds(66, 18.5, 24.9).minLb is 115)
    3. an unsourced statistic   /blog/what-is-bmi/  a new sentence "Roughly 61.7% of adults check their BMI
                                less than once a year." in the "What is BMI" section
                                expected: a C number with no registry row

Prints each expectation with what the report says, then "N of 3 planted errors reported; control clean: yes/no".
Exit 0 only when all three are reported in the broken copy and none of the three spots is a finding in the control.
"""
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PAGES = ['/blog/underweight-bmi-risks/', '/blog/bmi-categories/', '/blog/what-is-bmi/']
PLANTED_STAT = 'Roughly 61.7% of adults check their BMI less than once a year.'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def copy_site(dst):
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns('.git', 'research', 'node_modules', '__pycache__', '_snap'))


def replace_once(path, old, new):
    text = path.read_text(encoding='utf-8')
    if text.count(old) < 1:
        sys.exit(f'cannot plant: "{old[:60]}" not found in {path}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


def plant(root):
    # 1. the worked example's output
    replace_once(root / 'blog/underweight-bmi-risks/index.html', 'would have a BMI of 17.3', 'would have a BMI of 17.8')
    # 2. one cell of the weight-range table (5'6" row, low normal)
    p = root / 'blog/bmi-categories/index.html'
    text = p.read_text(encoding='utf-8')
    m = re.search(r'(5(?:&prime;|′)6(?:&Prime;|″)[^<]*</t[dh]>\s*<td[^>]*>)115 lbs', text)
    if not m:
        sys.exit('cannot plant: the 5\'6" row of the weight-range table not found')
    p.write_text(text[:m.end(1)] + '117 lbs' + text[m.end():], encoding='utf-8')
    # 3. an unsourced statistic, as its own sentence at the end of a paragraph in <main>
    p = root / 'blog/what-is-bmi/index.html'
    text = p.read_text(encoding='utf-8')
    i = text.find('It’s a quick screening number, not a diagnosis')
    if i < 0:
        i = text.find('quick screening number')
    j = text.find('</p>', i)
    if i < 0 or j < 0:
        sys.exit('cannot plant: the what-is-bmi paragraph not found')
    p.write_text(text[:j] + ' ' + PLANTED_STAT + text[j:], encoding='utf-8')


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
        r = subprocess.run([sys.executable, str(HERE / 'audit.py'), f'http://127.0.0.1:{port}', '--out', str(out),
                            '--pages', ','.join(PAGES)], capture_output=True, text=True)
        print('   ', (r.stdout.strip().splitlines() or ['(no output)'])[0])
        return json.loads((out / 'report.json').read_text(encoding='utf-8'))
    finally:
        srv.terminate()
        srv.wait()


def findings(rep):
    pages = {P['page']: P for P in rep['pages']}
    a = [m for m in pages['/blog/underweight-bmi-risks/']['mismatches'] if m['class'] == 'A' and 'a person who weighs 50 kg' in m['sentence']]
    b = [m for m in pages['/blog/bmi-categories/']['mismatches'] if m['class'] == 'B' and m['sentence'].startswith('5′6″') or
         (m['class'] == 'B' and m['sentence'].startswith("5'6"))]
    c = [x for x in pages['/blog/what-is-bmi/']['c_no_row'] if x['number'] == '61.7']
    return a, b, c


def main():
    with tempfile.TemporaryDirectory() as tmp:
        control, broken = Path(tmp) / 'control', Path(tmp) / 'broken'
        copy_site(control)
        copy_site(broken)
        plant(broken)
        print('control (unbroken copy):')
        a0, b0, c0 = findings(run_audit(control))
        print('broken (three planted errors):')
        a1, b1, c1 = findings(run_audit(broken))
    caught = 0
    for n, (label, hit, want) in enumerate((
            ('1. wrong example output (A)', a1, 'page BMI 17.8, calculator 17.3'),
            ('2. wrong range cell (B)', b1, 'page 117, computed 115'),
            ('3. unsourced statistic (C)', c1, '61.7 with no registry row')), 1):
        ok = bool(hit)
        if n == 1:
            ok = ok and '17.8' in hit[0]['page_value'] and '17.3' in hit[0]['computed']
        if n == 2:
            ok = ok and any(m['page_value'] == '117' and m['computed'] == '115' for m in hit)
        caught += ok
        got = hit[0] if hit else None
        shown = (f"{got.get('page_value')} vs {got.get('computed')}" if got and 'page_value' in got else
                 (f"no row: \"{got['sentence']}\"" if got else 'not reported'))
        print(f"  {'caught' if ok else 'MISSED'}  {label}: expected {want}; report: {shown}")
    clean = not a0 and not [m for m in b0 if m.get('page_value') == '117'] and not c0
    print(f'  control: example {"clean" if not a0 else "REPORTED"}, range cell {"clean" if not b0 else "REPORTED"}, '
          f'statistic {"absent" if not c0 else "REPORTED"}')
    print(f'{caught} of 3 planted errors reported; control clean: {"yes" if clean else "no"}')
    sys.exit(0 if caught == 3 and clean else 1)


if __name__ == '__main__':
    main()
