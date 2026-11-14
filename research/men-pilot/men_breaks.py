#!/usr/bin/env python3
"""Deliberate breaks for men_test_playwright.py (CMB-047). usage: python3 research/men-pilot/men_breaks.py [PORT]
Copies the served site (the repo without .git, research, .claude and audit) to a temp folder, serves it on PORT (default
8769) and runs the page test against it: once unbroken (must pass), then once per break (each must fail):
  1. a wrong cell:              the 25th percentile 24.9 shown as 25.0
  2. a wrong decade weight:     men 20 to 29 weigh 192 lb instead of 191
  3. a wrong body fat median:   overweight men 27.0% instead of 26.9%
  4. a wrong kg limit:          5'10" healthy up to 79 kg instead of 78
  5. a wrong curve point:       the rank script's median point 28.2237 moved to 28.3237
  6. a stray number:            "About 12% of men skip breakfast." added to the US men section
  7. a figure marker moved:     the worked example's BMI marker drawn at 133 instead of 131
  8. a figure label changed:    the waist figure's average reads 40.8 in
  9. FAQ out of step:           one visible answer changed, the JSON-LD left as it was
 10. an unsourced step back:    "to the nearest half inch (or 1 cm)" back in the measuring steps
 11. a wider page:              a 1,400-px box inside <main>
 12. a wrong formula:           calculator.js (the temp copy) multiplies by 704
 13. the old decade claim:      "Average BMI is highest in men in their 40s and 50s" back
 14. an unregistered link:      CDC's About BMI link pointed at a page the registry doesn't hold
 15. the head changed:          og:image:alt says 29.5
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
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8769
BASE = f'http://localhost:{PORT}'
TEST = os.path.join(HERE, 'men_test_playwright.py')
STATS = os.path.join(HERE, 'men_stats.json')
MP, JS = 'men-bmi-calculator/index.html', 'assets/js/calculator.js'
BREAKS = [
    ('a wrong cell', MP, [('<th scope="row">25th</th><td class="num">24.9</td>', '<th scope="row">25th</th><td class="num">25.0</td>')]),
    ('a wrong decade weight', MP, [('<th scope="row">20–29</th><td class="num">27.8</td><td class="num">191</td>',
                                    '<th scope="row">20–29</th><td class="num">27.8</td><td class="num">192</td>')]),
    ('a wrong body fat median', MP, [('<td class="num">26.9%</td>', '<td class="num">27.0%</td>')]),
    ('a wrong kg limit', MP, [('129–173 lb<span class="unit-alt">59–78 kg</span>', '129–173 lb<span class="unit-alt">59–79 kg</span>')]),
    ('a wrong curve point', MP, [(',28.2237,', ',28.3237,')]),
    ('a stray number', MP, [('Your result in the calculator is ranked against these men.',
                             'Your result in the calculator is ranked against these men. About 12% of men skip breakfast.')]),
    ('a figure marker moved', MP, [('<line x1="131.0" y1="78" x2="131.0"', '<line x1="133.0" y1="78" x2="133.0"')]),
    ('a figure label changed', MP, [('Average US man: 40.6 in (103 cm)</text>', 'Average US man: 40.8 in (103 cm)</text>')]),
    ('FAQ out of step', MP, [('<p>The healthy BMI range for men is', '<p>The healthy BMI range for adult men is')]),
    ('an unsourced step back', MP, [('<li>Breathe out, then read the tape.</li>',
                                     '<li>Breathe out, then read the tape to the nearest half inch (or 1 cm).</li>')]),
    ('a wider page', MP, [('<section id="us-men" class="content-section flow">',
                           '<section id="us-men" class="content-section flow"><div style="width:1400px;height:1px"></div>')]),
    ('a wrong formula', JS, [('return (weightLbs / (heightInches * heightInches)) * 703;',
                              'return (weightLbs / (heightInches * heightInches)) * 704;')]),
    ('the old decade claim', MP, [('Average BMI was higher in men’s 40s and 50s (30.5 and 30.2) than in their 20s (27.8); each difference '
                                   'is larger than its margin of error.',
                                   'Average BMI is highest in men in their 40s and 50s (30.5 and 30.2).')]),
    ('an unregistered link', MP, [('for an individual (<a href="https://www.cdc.gov/bmi/about/index.html"',
                                   'for an individual (<a href="https://www.cdc.gov/bmi/faq/index.html"')]),
    ('the head changed', MP, [('the average US man has a BMI of 29.4 (CDC, 2021–2023)">',
                               'the average US man has a BMI of 29.5 (CDC, 2021–2023)">')]),
]


def run_test():
    r = subprocess.run([sys.executable, TEST, BASE, STATS], capture_output=True, text=True, cwd=ROOT)
    lines = r.stdout.strip().splitlines()
    head = next((l for l in lines if 'checks,' in l), r.stderr.strip()[-300:])
    return r.returncode, head, [l for l in lines if l.startswith('FAIL')]


def main():
    tmp = tempfile.mkdtemp(prefix='men-breaks-')
    site = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', 'research', '.claude', 'audit', '_snap', '__pycache__',
                                                              'node_modules'))
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--directory', site],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bad = 0
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + '/men-bmi-calculator/', timeout=2)
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
