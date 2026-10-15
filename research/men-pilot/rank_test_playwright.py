#!/usr/bin/env python3
"""Checks the men-page rank line against the Python percentile curve. usage: rank_test.py BASEURL STATS_JSON
Since CMB-012 the rank counts only men with a lower BMI: the curve is read at BMI - 0.1 (BMI is recorded to 0.1)."""
import sys, json, math
from playwright.sync_api import sync_playwright
base, stats = sys.argv[1], sys.argv[2]
Q = json.load(open(stats))['p1_p99']
def r1(x): return math.floor(x*10+0.5+1e-9)/10
def rank(b):
    if b <= Q[0]: return 0.0
    if b >= Q[-1]: return 100.0
    for i in range(98):
        if b < Q[i+1]: return i+1+(b-Q[i])/(Q[i+1]-Q[i])
cases = [('imp',5,10,180),('imp',5,10,100),('imp',5,10,400),('imp',5,10,197),('imp',6,0,170),('imp',5,6,230),('met',178,82,None),('met',190,60,None)]
fails = 0; n = 0
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox','--disable-dev-shm-usage']); pg = b.new_page(viewport={'width':390,'height':844})
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://localhost') else r.abort())
    pg.goto(base + '/men-bmi-calculator/', wait_until='load')
    hidden0 = pg.eval_on_selector('#men-rank', 'e => e.hidden')
    print('rank box hidden before calculating:', hidden0)
    for c in cases:
        if c[0] == 'imp':
            pg.click('#panel-men .unit-btn[data-unit="imperial"]'); pg.fill('#men-height-ft', str(c[1])); pg.fill('#men-height-in', str(c[2])); pg.fill('#men-weight-lbs', str(c[3]))
            bmi = r1(c[3]*703/(c[1]*12+c[2])**2)
        else:
            pg.click('#panel-men .unit-btn[data-unit="metric"]'); pg.fill('#men-height-cm', str(c[1])); pg.fill('#men-weight-kg', str(c[2]))
            bmi = r1(c[2]/(c[1]/100)**2)                                  # metric BMI is kg/m2 (CMB-011)
        pg.click('#calc-men-btn'); pg.wait_for_timeout(80)
        head = pg.inner_text('#men-rank-value'); txt = pg.inner_text('#men-rank-text'); left = pg.eval_on_selector('#men-rank-marker', 'e => e.style.left')
        lo = rank(round(bmi - 0.1, 1)); hi = 100 - rank(bmi); nn = lambda x: 99 if x > 99 else round(x)
        exp = f'Lower than {nn(hi)}% of US men' if lo < 1 else f'Higher than {nn(lo)}% of US men'
        n += 1; ok = head == exp and f'{bmi:.1f}' in txt and not pg.eval_on_selector('#men-rank', 'e => e.hidden')
        if not ok: fails += 1
        print(('OK  ' if ok else 'FAIL'), c, 'BMI', bmi, '|', head, '|', left, '|', txt[:90])
    b.close()
print(f'{n} rank cases, {fails} failures')
