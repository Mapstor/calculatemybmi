#!/usr/bin/env python3
"""Deliberate breaks for nb_test_playwright.py (CMB-023). usage: python3 research/new-bmi-build/nb_breaks.py [PORT]
Copies the served site (the repo without .git, research, .claude and audit) to a temp folder, serves it on PORT (default
8765) and runs the page test against it: once unbroken (must pass), then once per break (each must fail):
  1. a wrong cell:        5′4″ and 150 lb, New BMI 26.3 shown as 26.4 in the side-by-side table
  2. a wrong percent:     5′4″, +2.0% shown as +2.1% in the by-height table
  3. a removed for:       the label of lbm-sex on /lean-body-mass/ loses its for attribute
  4. an article wrapper:  the #why section wrapped in <article>
  5. a banned phrase:     "mathematically sound" added to the formulas section
Needs Python Playwright + Chromium (the test does). Exit 1 if the control fails or any break passes."""
import os, shutil, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
BASE = f'http://localhost:{PORT}'
TEST = os.path.join(HERE, 'nb_test_playwright.py')
STATS = os.path.join(HERE, 'nb_stats.json')
NB, LBM = 'new-bmi-calculator/index.html', 'lean-body-mass/index.html'
BREAKS = [
    ('a wrong cell', NB, [('<td class="num">25.7</td><td class="num">26.3</td>', '<td class="num">25.7</td><td class="num">26.4</td>')]),
    ('a wrong percent', NB, [('<td class="num">+2.0%</td>', '<td class="num">+2.1%</td>')]),
    ('a removed for', LBM, [(' for="lbm-sex"', '')]),
    ('an article wrapper', NB, [('<section id="why"', '<article><section id="why"'),
                                ('</section><section id="which"', '</section></article><section id="which"')]),
    ('a banned phrase', NB, [('The square root of 1.69 is 1.3', 'The formula is mathematically sound. The square root of 1.69 is 1.3')]),
]


def run_test():
    r = subprocess.run([sys.executable, TEST, BASE, STATS], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    return r.returncode, lines[0] if lines else r.stderr.strip()[-300:], [l for l in lines if l.startswith('FAIL')]


def main():
    tmp = tempfile.mkdtemp(prefix='nb-breaks-')
    site = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', 'research', '.claude', 'audit', '__pycache__'))
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--directory', site],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bad = 0
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + '/new-bmi-calculator/', timeout=2); break
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
