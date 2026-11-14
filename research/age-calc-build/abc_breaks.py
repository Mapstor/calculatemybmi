#!/usr/bin/env python3
"""Deliberate breaks for abc_test_playwright.py (CMB-045). usage: python3 research/age-calc-build/abc_breaks.py [PORT]
Copies the served site (the repo without .git, research, .claude and audit) to a temp folder, serves it on PORT (default
8768) and runs the page test against it: once unbroken (must pass), then once per break (each must fail):
  1. a wrong cell:            women aged 40 to 59, the median 29.3 shown as 29.4 in the percentile table
  2. a wrong curve point:     the page script's first point of one age-group curve moved by 0.5
  3. the sexes swapped:       the page script reads "Woman" as men
  4. the old Winter wording:  calculator.js (the temp copy) says "the lowest all-cause mortality across BMI 23 to 33"
  5. no under-20 hand-off:    calculator.js (the temp copy) gives an adult result at any age
  6. a stray number:          "About 31% of adults have obesity." added to the averages section
  7. a figure bar moved:      the women's middle-half bar at 50 to 59 drawn 10 units to the right
  8. an inline style:         the averages section gets style="margin-top:0"
  9. FAQ out of step:         one visible answer changed, the JSON-LD left as it was
Needs Python Playwright + Chromium (the test does). Exit 1 if the control fails or any break passes."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
BASE = f'http://localhost:{PORT}'
TEST = os.path.join(HERE, 'abc_test_playwright.py')
STATS = os.path.join(HERE, 'abc_stats.json')
AP, JS = 'age-bmi-calculator/index.html', 'assets/js/calculator.js'
BREAKS = [
    ('a wrong cell', AP, [('<th scope="row">Median</th><td class="num">27.1</td><td class="num">29.3</td>',
                           '<th scope="row">Median</th><td class="num">27.1</td><td class="num">29.4</td>')]),
    ('a wrong curve point', AP, [('m:[18.3017,', 'm:[18.8017,')]),
    ('the sexes swapped', AP, [('male=panel.querySelector(".sex-select").value==="male"',
                                'male=panel.querySelector(".sex-select").value==="female"')]),
    ('the old Winter wording', JS, [('compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise '
                                     'at about 33', 'the lowest all-cause mortality was across BMI 23 to 33')]),
    ('no under-20 hand-off', JS, [('if (!isNaN(age) && age < 20) {', 'if (false) {')]),
    ('a stray number', AP, [('<section id="averages" class="content-section flow"><h2>Average BMI, weight and waist by age</h2><p>',
                             '<section id="averages" class="content-section flow"><h2>Average BMI, weight and waist by age</h2><p>'
                             'About 31% of adults have obesity. ')]),
    ('a figure bar moved', AP, [('<rect x="136.0" y="163.5" width="100.2"', '<rect x="146.0" y="163.5" width="100.2"')]),
    ('an inline style', AP, [('<section id="averages" class="content-section flow">',
                              '<section id="averages" class="content-section flow" style="margin-top:0">')]),
    ('FAQ out of step', AP, [('<p>Yes. BMI divides weight by height squared', '<p>Yes. BMI divides the weight by height squared')]),
]


def run_test():
    r = subprocess.run([sys.executable, TEST, BASE, STATS], capture_output=True, text=True, cwd=ROOT)
    lines = r.stdout.strip().splitlines()
    head = next((l for l in lines if 'checks,' in l), r.stderr.strip()[-300:])
    return r.returncode, head, [l for l in lines if l.startswith('FAIL')]


def main():
    tmp = tempfile.mkdtemp(prefix='age-breaks-')
    site = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', 'research', '.claude', 'audit', '_snap', '__pycache__'))
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--directory', site],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bad = 0
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + '/age-bmi-calculator/', timeout=2)
                break
            except Exception:                                        # noqa: BLE001
                time.sleep(0.2)
        code, head, _ = run_test()
        print(f'control (unbroken copy): exit {code}, {head}')
        bad += code != 0
        for name, rel, edits in BREAKS:
            path = os.path.join(site, rel)
            pristine = open(path, encoding='utf-8').read()
            s = pristine
            for old, new in edits:
                assert s.count(old) == 1, (name, old, s.count(old))
                s = s.replace(old, new)
            open(path, 'w', encoding='utf-8').write(s)
            try:
                code, head, fl = run_test()
            finally:
                open(path, 'w', encoding='utf-8').write(pristine)
            print(f'break: {name}: exit {code}, {head}')
            for l in fl[:3]:
                print('   ', l[:200])
            bad += code == 0
    finally:
        srv.terminate()
        srv.wait()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'{len(BREAKS)} breaks; {"every break failed the test, the control passed" if not bad else f"{bad} problem(s)"}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
