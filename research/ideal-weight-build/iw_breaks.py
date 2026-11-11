#!/usr/bin/env python3
"""Deliberate breaks for iw_test_playwright.py (CMB-028). usage: python3 research/ideal-weight-build/iw_breaks.py [PORT]
Copies the served site (the repo without .git, research, .claude and audit) to a temp folder, serves it on PORT (default
8766) and runs the page test against it: once unbroken (must pass), then once per break (each must fail):
  1. a wrong cell:              women 5′6″, Miller 135 lb shown as 136 in the by-height table
  2. a wrong coefficient:       Devine for women 45.5 kg + 2.3 kg shown as + 2.4 kg in the formulas table
  3. the frame on Devine:       calculator.js (the temp copy) multiplies Devine by the frame factor too
  4. a removed for:             the label of ideal-frame loses its for attribute
  5. an article wrapper:        the #frame section wrapped in <article>
  6. a banned phrase:           "Averaging the four gives a more robust estimate." added to the formulas section
  7. a soft hyphen back:        the women's by-height heading Robinson written Robin&shy;son again (CMB-031)
  8. the small headings gone:   the women's by-height table loses .data-table--small-head, so its whole names no longer
                                fit a 360 or a 390 px phone (CMB-031)
  9. an average of formulas:    "Their average ideal weight is the middle of the span." added to the formulas section
                                (CMB-031: the narrowed "average" rule still bans it)
Needs Python Playwright + Chromium (the test does). Exit 1 if the control fails or any break passes."""
import os, shutil, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
BASE = f'http://localhost:{PORT}'
TEST = os.path.join(HERE, 'iw_test_playwright.py')
STATS = os.path.join(HERE, 'iw_stats.json')
IW, JS = 'ideal-weight/index.html', 'assets/js/calculator.js'
NB = ' '
BREAKS = [
    ('a wrong cell', IW, [('<td class="num">135<span class="cell-kg">61.3</span></td>', '<td class="num">136<span class="cell-kg">61.3</span></td>')]),
    ('a wrong coefficient', IW, [(f'<td>45.5{NB}kg + 2.3{NB}kg', f'<td>45.5{NB}kg + 2.4{NB}kg')]),
    ('the frame on Devine', JS, [('const devine = fromKg(male ? 50 + 2.3 * over : 45.5 + 2.3 * over);',
                                  "const devine = fromKg((male ? 50 + 2.3 * over : 45.5 + 2.3 * over) * (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1));")]),
    ('a removed for', IW, [(' for="ideal-frame"', '')]),
    ('an article wrapper', IW, [('<section id="frame"', '<article><section id="frame"'),
                                ('</section><section id="examples"', '</section></article><section id="examples"')]),
    ('a banned phrase', IW, [('<p>Hamwi’s formula is in pounds, the other three in kilograms.</p>',
                              '<p>Hamwi’s formula is in pounds, the other three in kilograms. Averaging the four gives a more robust estimate.</p>')]),
    ('a soft hyphen back', IW, [('<caption>Women, medium frame: lb, with kg under each value</caption><thead><tr><th scope="col">Height'
                                 '<span class="th-sub">cm</span></th><th scope="col" class="num">Hamwi</th><th scope="col" class="num">Devine</th>'
                                 '<th scope="col" class="num">Robinson</th>',
                                 '<caption>Women, medium frame: lb, with kg under each value</caption><thead><tr><th scope="col">Height'
                                 '<span class="th-sub">cm</span></th><th scope="col" class="num">Hamwi</th><th scope="col" class="num">Devine</th>'
                                 '<th scope="col" class="num">Robin&shy;son</th>')]),
    ('the small headings gone', IW, [('<table class="data-table data-table--fit data-table--tight data-table--small-head"><caption>Women',
                                      '<table class="data-table data-table--fit data-table--tight"><caption>Women')]),
    ('an average of formulas', IW, [('<p>Hamwi’s formula is in pounds, the other three in kilograms.</p>',
                                     '<p>Hamwi’s formula is in pounds, the other three in kilograms. Their average ideal weight is the middle of the span.</p>')]),
]


def run_test():
    r = subprocess.run([sys.executable, TEST, BASE, STATS], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    return r.returncode, lines[0] if lines else r.stderr.strip()[-300:], [l for l in lines if l.startswith('FAIL')]


def main():
    tmp = tempfile.mkdtemp(prefix='iw-breaks-')
    site = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', 'research', '.claude', 'audit', '_snap', '__pycache__'))
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--directory', site],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bad = 0
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + '/ideal-weight/', timeout=2); break
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
