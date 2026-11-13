#!/usr/bin/env python3
"""CMB-033: the rank lines at every BMI the 4-decimal curves change, typed into the calculators.
usage: python3 research/rank-curves/rank_check_playwright.py BASE   (e.g. http://localhost:8000)
For each BMI in curves.json "changed_ranks" (BMI 10.0 to 80.0 where the 2-decimal curves showed a different whole
percent), types a 170 cm height and the weight in kg that gives that BMI into /, /men-bmi-calculator/ and
/women-bmi-calculator/ (metric), and checks the rank text against the pages' rule read off the 4-decimal curves
(lower = strictly lower BMI, the curve at BMI - 0.1; higher = 100 - the curve at BMI). Each case must also differ from
what the 2-decimal curve would print, so the check proves the change. Exit 1 on any failure."""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
C = json.loads((HERE / 'curves.json').read_text())
OLD = json.loads((HERE / 'curves_2dec.json').read_text())
base = sys.argv[1].rstrip('/')


def pct(q, b):
    if b <= q[0]:
        return 0.0
    if b >= q[98]:
        return 100.0
    for i in range(98):
        if b < q[i + 1]:
            return i + 1 + (b - q[i]) / (q[i + 1] - q[i])
    return 100.0


def n(x):
    return 99 if x > 99 else int(x + 0.5)


def lab(q, b):
    lo, hi = pct(q, round(b * 10 - 1) / 10), 100 - pct(q, b)
    return f'lower than {n(hi)}%' if lo < 1 else f'higher than {n(lo)}%'


def kg_for(b):
    for d in range(0, 6):
        for k in (round(b * 2.89 + s * d / 10, 1) for s in (1, -1)):
            if round(k / 2.89 * 10 + 1e-9) / 10 == b:   # the pages' BMI: kg / 1.7², rounded once
                return k
    raise SystemExit(f'no whole 0.1 kg gives BMI {b} at 170 cm')


PAGES = {
    '/': ('standard', {'adults': None, 'men': 'men only', 'women': 'women only'}),
    '/men-bmi-calculator/': ('men', {'men': None}),
    '/women-bmi-calculator/': ('women', {'women': None, 'women_20_39': 'aged 20 to 39', 'women_40_59': '40 to 59', 'women_60plus': '60 and over'}),
}
fails = checks = proved = 0
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 390, 'height': 844})
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://localhost') else r.abort())
    for path, (px, curves) in PAGES.items():
        bmis = sorted({b for name in curves for b in C['changed_ranks'][name]})
        pg.goto(base + path, wait_until='load')
        pg.click(f'#panel-{px} .unit-btn[data-unit="metric"]')
        for b in bmis:
            pg.fill(f'#{px}-height-cm', '170')
            pg.fill(f'#{px}-weight-kg', f'{kg_for(b):.1f}')
            pg.click(f'#panel-{px} .calculate-btn')
            pg.wait_for_timeout(150)
            shown = pg.inner_text(f'#{px}-bmi-value').strip()
            box = pg.inner_text(f'#{px}-rank').replace(' ', ' ').lower()
            for name, cue in curves.items():
                want, old = lab(C[name]['p1_p99'], b), lab(OLD[name], b)
                checks += 1
                proved += want != old
                ok = shown == f'{b:.1f}' and want in box
                if not ok:
                    fails += 1
                    print('FAIL', path, b, name, 'want', want, 'shown BMI', shown, '|', box[:200])
    br.close()
print(f'{checks} checks, {fails} failures, 0 skipped; {proved} of them differ from the 2-decimal curves')
sys.exit(1 if fails or not proved else 0)
