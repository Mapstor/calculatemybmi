#!/usr/bin/env python3
"""Deliberate breaks for kids_test_playwright.py (CMB-030). usage: python3 research/kids-build/kids_breaks.py [PORT]
Copies the served site (the repo without .git, research, .claude and audit) to a temp folder, serves it on PORT (default
8767) and runs the page test against it: once unbroken (must pass), then once per break (each must fail):
  1. a wrong cell:              boys at 10, the 95th percentile 22.2 shown as 22.3 in the birthday table
  2. the 24.0 row back:         calculator.js (the temp copy) reads the 24.0-month row at exactly 2 years 0 months again
  3. a wrong AAP class:         calculator.js (the temp copy) puts class 3 at 150% of the 95th instead of 140%
  4. a removed for:             the label of kids-sex loses its for attribute
  5. an article wrapper:        the #examples section wrapped in <article>
  6. a banned phrase:           "Children with obesity are more likely to have type 2 diabetes." added to #prevalence
  7. the 120% sentence back:    calculator.js (the temp copy) says "120% of the 95th percentile" when only BMI 35 decides (CMB-031)
Needs Python Playwright + Chromium (the test does). Exit 1 if the control fails or any break passes."""
import os, shutil, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
BASE = f'http://localhost:{PORT}'
TEST = os.path.join(HERE, 'kids_test_playwright.py')
STATS = os.path.join(HERE, 'kids_stats.json')
KP, JS = 'kids-bmi-calculator/index.html', 'assets/js/calculator.js'
BREAKS = [
    ('a wrong cell', KP, [('<tr id="boys-10"><th scope="row">10</th><td class="num">14.2</td><td class="num">16.6</td>'
                           '<td class="num">19.4</td><td class="num">22.2</td>',
                           '<tr id="boys-10"><th scope="row">10</th><td class="num">14.2</td><td class="num">16.6</td>'
                           '<td class="num">19.4</td><td class="num">22.3</td>')]),
    ('the 24.0 row back for age 2', JS, [('var target = Math.floor(agemos) + 0.5;',
                                          'var target = (agemos === 24) ? 24 : Math.floor(agemos) + 0.5;')]),
    ('a wrong AAP class', JS, [('(p95 >= 140 || bmi >= 40 ? 3 : 2)', '(p95 >= 150 || bmi >= 40 ? 3 : 2)')]),
    ('a removed for', KP, [(' for="kids-sex"', '')]),
    ('an article wrapper', KP, [('<section id="examples"', '<article><section id="examples"'),
                                ('</section><section id="age"', '</section></article><section id="age"')]),
    ('a banned phrase', KP, [('had severe obesity (', 'had severe obesity. Children with obesity are more likely to have type 2 '
                                                      'diabetes (')]),
    ('the 120% sentence back for the BMI 35 case', JS, [('const by35 = bmi >= 35 && result && result.pctP95 < 120;', 'const by35 = false;')]),
]


def run_test():
    r = subprocess.run([sys.executable, TEST, BASE, STATS], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    head = next((l for l in lines if 'checks,' in l), r.stderr.strip()[-300:])
    return r.returncode, head, [l for l in lines if l.startswith('FAIL')]


def main():
    tmp = tempfile.mkdtemp(prefix='kids-breaks-')
    site = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', 'research', '.claude', 'audit', '_snap', '__pycache__'))
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--directory', site],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bad = 0
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + '/kids-bmi-calculator/', timeout=2); break
            except Exception:
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
            for l in fl[:3]: print('   ', l)
            bad += code == 0
    finally:
        srv.terminate(); srv.wait()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'{len(BREAKS)} breaks; {"every break failed the test, the control passed" if not bad else f"{bad} problem(s)"}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
