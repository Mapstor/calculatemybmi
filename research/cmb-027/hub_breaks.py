#!/usr/bin/env python3
"""Proof for hub_examples_playwright.py (CMB-027): deliberate breaks on /calculators/ that it must catch.

usage: python3 research/cmb-027/hub_breaks.py

Serves the repo on a free localhost port with /calculators/ replaced by a copy of the working
calculators/index.html, then runs hub_examples_playwright.py against it once per case:
  - clean: the unchanged copy must pass (exit 0, 0 failures, 0 skipped);
  - each break changes one thing in that copy and must exit 1 with FAIL or SKIP lines that match
    exactly the expected checks: every expected pattern matches at least one line, and every
    FAIL / SKIP line matches an expected pattern (a break may not hit anything else).
Breaks: a wrong number or category in each of the nine examples (the two errors CMB-027 fixed
among them), "about 42 lbs" of fat mass (within 0.5 of the printed 41.5, so only the round-once
rule catches it), a swapped direction and a moved crossing for New BMI, a number, a number word
and a category nothing checks, an input the text no longer gives, a card linking to no known
calculator, and a missing example block.
Exit 0 = every expectation held.
"""
import http.server
import os
import re
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TEST = os.path.join(HERE, 'hub_examples_playwright.py')
CLEAN = open(os.path.join(REPO, 'calculators', 'index.html'), encoding='utf-8').read()
served = {'html': CLEAN}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=REPO, **k)

    def do_GET(self):
        if self.path.split('?')[0] in ('/calculators/', '/calculators/index.html'):
            body = served['html'].encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, *a):
        pass


def rep(old, new):
    def fn(src):
        n = src.count(old)
        if n != 1:
            raise SystemExit(f'break setup: {old[:60]!r} is on the page {n} times, need 1')
        return src.replace(old, new)
    return fn


def drop_example(lead):
    def fn(src):
        rx = re.compile(r'<div style="[^"]*"> <strong style="color:var\(--gray-700\);">Example:</strong> '
                        + re.escape(lead) + r'.*?</div> ')
        out, n = rx.subn('', src)
        if n != 1:
            raise SystemExit(f'break setup: example {lead!r} found {n} times, need 1')
        return out
    return fn


E1, E2, E3, E4, E5 = (r'Example 1 /:', r'Example 2 /women-bmi-calculator/:', r'Example 3 /men-bmi-calculator/:',
                      r'Example 4 /age-bmi-calculator/:', r'Example 5 /kids-bmi-calculator/:')
E6, E7, E8, E9 = (r'Example 6 /new-bmi-calculator/:', r'Example 7 /ideal-weight/:', r'Example 8 /lean-body-mass/:',
                  r'Example 9 /body-fat-calculator/:')
CASES = [
    ('women category back to "Normal" (origin/main)', rep('24.0 (Healthy weight)', '24.0 (Normal)'),
     [f'FAIL {E2} category: example Normal, calculator Healthy weight']),
    ('New BMI back to 24.3 (origin/main)', rep('New BMI of 23.7', 'New BMI of 24.3'),
     [f'FAIL {E6} New BMI: example 24.3, calculator 23.7']),
    ('standard BMI', rep('25.1 (Overweight)', '25.2 (Overweight)'), [f'FAIL {E1} BMI: example 25.2']),
    ('standard category', rep('25.1 (Overweight)', '25.1 (Healthy weight)'), [f'FAIL {E1} category']),
    ('women highest healthy weight', rep('108&ndash;145 lbs for her height', '108&ndash;146 lbs for her height'),
     [f'FAIL {E2} highest healthy weight']),
    ('men waist line', rep('waist under 40"', 'waist under 38"'), [f'FAIL {E3} waist line']),
    ('age band', rep('(23&ndash;33 in <a', '(23&ndash;35 in <a'), [f'FAIL {E4} band \\(BMI low-high\\)']),
    ('kids percentile', rep('54th percentile', '55th percentile'), [f'FAIL {E5} percentile']),
    ('New BMI points', rep('1.3 points lower', '1.4 points lower'), [f'FAIL {E6} difference \\(points\\)']),
    ('New BMI direction', rep('1.3 points lower', '1.3 points higher'), [f'FAIL {E6} difference direction']),
    ('New BMI crossing moved', rep('above about 5\'6.5"', 'above about 5\'8.5"'),
     [f'FAIL {E6} crossing height', f'FAIL {E6} table row 5\'7"']),
    ('New BMI sides swapped',
     rep('reads lower than traditional BMI above about 5\'6.5" and higher below it',
         'reads higher than traditional BMI above about 5\'6.5" and lower below it'),
     [f'FAIL {E6} New BMI above the crossing', f'FAIL {E6} New BMI below the crossing', f'FAIL {E6} table row']),
    ('ideal Miller', rep('Miller 135 lbs', 'Miller 136 lbs'), [f'FAIL {E7} Miller']),
    ('ideal formula count', rep('the four clinical formulas', 'the three clinical formulas'),
     [f'FAIL {E7} number of formulas']),
    ('lbm "about 42 lbs"', rep('about 41 lbs', 'about 42 lbs'), [f'FAIL {E8} fat mass \\(about N lbs\\)']),
    ('lbm kg', rep('58.3 kg, Boer', '58.4 kg, Boer'), [f'FAIL {E8} lean body mass \\(kg\\)']),
    ('body fat share', rep('94% of US men', '93% of US men'), [f'FAIL {E9} share with more body fat']),
    ('body fat age group', rep('aged 30&ndash;39 have', 'aged 40&ndash;49 have'), [f'FAIL {E9} group']),
    ('unchecked numbers', rep('118&ndash;159 lbs.', '118&ndash;159 lbs. About 3 in 10 US adults are in this range.'),
     [f'SKIP {E1} number "3"', f'SKIP {E1} number "10"']),
    ('unchecked number word', rep('See every age group', 'See all six age groups'),
     [f'SKIP {E9} number word "six"']),
    ('unchecked category', rep('his actual risk may be lower.', 'his actual risk may be lower than Overweight suggests.'),
     [f'SKIP {E3} category "Overweight"']),
    ('input not in the text', rep('weighs 140 lbs', 'weighs about 140 lbs'),
     [f'SKIP {E2} weight: not found', f'SKIP {E2} .* is neither an input nor compared']),
    ('card links to no known calculator', rep('<a href="/ideal-weight/" class="cta-button', '<a href="/ideal-weight-old/" class="cta-button'),
     [r'SKIP Example 7 /ideal-weight-old/: the card links to no known calculator']),
    ('an example block removed', drop_example('A 10-year-old boy'),
     [r'FAIL /calculators/ at 390 px: "Example:" blocks: example 9, calculator 8']),
]


def run(base):
    p = subprocess.run([sys.executable, TEST, base], capture_output=True, text=True, timeout=600)
    lines = [l for l in p.stdout.splitlines() if l.startswith(('FAIL ', 'SKIP '))]
    summary = next((l for l in p.stdout.splitlines() if re.match(r'\d+ checks, ', l)), '(no summary)')
    return p.returncode, lines, summary, p.stdout + p.stderr


def main():
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{httpd.server_address[1]}'
    bad = 0
    served['html'] = CLEAN
    code, lines, summary, out = run(base)
    good = code == 0 and not lines and summary.endswith('0 failures, 0 skipped')
    print(f'{"ok  " if good else "BAD "} clean copy: exit {code}, {summary}')
    if not good:
        bad += 1
        print(out[-3000:])
    for name, fn, expect in CASES:
        served['html'] = fn(CLEAN)
        code, lines, summary, out = run(base)
        missing = [e for e in expect if not any(re.search(e, l) for l in lines)]
        stray = [l for l in lines if not any(re.search(e, l) for e in expect)]
        good = code == 1 and not missing and not stray
        print(f'{"ok  " if good else "BAD "} {name}: exit {code}, {summary}')
        if not good:
            bad += 1
            for e in missing:
                print('     expected, not reported:', e)
            for l in stray:
                print('     reported, not expected:', l)
    httpd.shutdown()
    print(f'\n{len(CASES) + 1} cases, {bad} not as expected')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
