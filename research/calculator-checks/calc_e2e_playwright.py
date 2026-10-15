#!/usr/bin/env python3
# Reference test (CMB-005): needs Python Playwright + Chromium; the box has neither, so chat or the Mac runs it.
# Serve the repo with `python3 -m http.server 8000`, then: python3 calc_e2e_playwright.py http://localhost:8000
"""End-to-end calculator checks in Chromium against a local server.
usage: calc_e2e.py BASEURL"""
import sys, math, re, json
from playwright.sync_api import sync_playwright
base = sys.argv[1]
def r1(x): return math.floor(x*10 + 0.5 + 1e-9)/10
def bounds(h, lo=18.5, hi=24.9):
    k = h*h/703; L = (lo-0.05)*k; H = (hi+0.05)*k
    m2 = (h*0.0254)**2; LK = (lo-0.05)*m2; HK = (hi+0.05)*m2          # metric limits follow kg/m2 (CMB-011)
    return dict(minLb=math.ceil(L-1e-9), maxLb=math.ceil(H-1e-9)-1, minKg=math.ceil(LK-1e-9), maxKg=math.ceil(HK-1e-9)-1, L=L, H=H)
def cat(b):
    return 'under' if b < 18.5 else 'normal' if b < 25 else 'over' if b < 30 else 'obese'
fails = []; checks = 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)
pages = {'/': 'standard', '/women-bmi-calculator/': 'women', '/men-bmi-calculator/': 'men', '/age-bmi-calculator/': 'age'}
imperial_cases = [(5,10,180),(5,10,173),(5,10,174),(5,10,128),(5,10,129),(6,2,144),(6,2,143),(5,2,136),(5,2,137),(6,0,250),(5,4,95),(6,6,330)]
metric_cases = [(178,82),(178,79),(178,80),(188,66),(188,65),(157,61),(157,62),(165,45),(200,140),(145,84),(159,101),(170,70)]  # last two: 40.0 in kg/m2, 39.9 with 703 (CMB-011)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox','--disable-dev-shm-usage'])
    ctx = b.new_context(viewport={'width':390,'height':844})
    for path, t in pages.items():
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://localhost') else r.abort())
        pg.goto(base + path, wait_until='load')
        panel = f'#panel-{t}'
        # imperial
        for ft, inch, lb in imperial_cases:
            pg.click(f'{panel} .unit-btn[data-unit="imperial"]')
            pg.fill(f'{panel} .height-ft', str(ft)); pg.fill(f'{panel} .height-in', str(inch)); pg.fill(f'{panel} .weight-lbs', str(lb))
            if t == 'age': pg.fill(f'{panel} .age-input', '40')
            pg.click(f'#calc-{t}-btn'); pg.wait_for_timeout(60)
            h = ft*12+inch; exact = lb*703/h/h; R = r1(exact); B = bounds(h)
            shown = pg.inner_text(f'#{t}-bmi-value'); catTxt = pg.inner_text(f'#{t}-bmi-category')
            ok(shown == f'{R:.1f}', f'{path} {ft}\'{inch}" {lb}: shown {shown} expected {R:.1f}')
            exp = cat(R)
            got = 'under' if re.search('(?i)thin|under', catTxt) else 'normal' if re.search('Normal|Healthy', catTxt) else 'over' if 'Overweight' in catTxt else 'obese'
            ok(got == exp, f'{path} {ft}\'{inch}" {lb}: category {catTxt} for BMI {R}')
            if not pg.locator(f'#{t}-healthy-min').count(): print('no healthy-min on', path); continue
            hmin = ' '.join(pg.inner_text(f'#{t}-healthy-min').split()); hmax = ' '.join(pg.inner_text(f'#{t}-healthy-max').split())
            ok(hmin == f"{B['minLb']} lbs ({B['minLb']/2.20462:.1f} kg)", f'{path} {h}in min {hmin} vs {B}')
            ok(hmax == f"{B['maxLb']} lbs ({B['maxLb']/2.20462:.1f} kg)", f'{path} {h}in max {hmax} vs {B}')
            diff = pg.inner_text(f'#{t}-weight-diff') if pg.locator(f'#{t}-weight-diff').count() else None
            if diff is None: pass
            elif exp == 'normal': ok(diff.startswith('Within'), f'{path} {h}in {lb}: diff {diff}')
            elif R >= 25: ok(diff.startswith(f"{round(lb-B['maxLb'])} lb") and 'above' in diff, f'{path} {h}in {lb}: diff {diff} (max {B["maxLb"]})')
            else: ok(diff.startswith(f"{round(B['minLb']-lb)} lb") and 'below' in diff, f'{path} {h}in {lb}: diff {diff} (min {B["minLb"]})')
            # milestones: every listed weight sits on the right side of its threshold
            rows = pg.eval_on_selector_all(f'#{t}-results .er-table', 'ts => ts.map(t => t.innerText)')
            ms = [x for x in rows if 'starts' in x]
            ok(len(ms) == 1, f'{path}: milestones table missing')
            if ms:
                for line in ms[0].split('\n')[1:]:
                    m = re.match(r'(.+?)\t([\d.]+)\t(\d+) lbs', line)
                    if not m: continue
                    w = int(m.group(3)); th = float(m.group(2)); Rw = r1(w*703/h/h)
                    if 'ends' in m.group(1): ok(Rw <= th and r1((w+1)*703/h/h) > th, f'{path} {h}in milestone {line}')
                    else: ok(Rw >= th and r1((w-1)*703/h/h) < th, f'{path} {h}in milestone {line}')
            # what-if: category matches shown BMI
            wi = [x for x in rows if 'Current' in x]
            if wi:
                for line in wi[0].split('\n')[1:]:
                    cells = line.split('\t')
                    if len(cells) >= 4:
                        bb = float(cells[2]); c = cells[3]
                        g = 'under' if re.search('(?i)thin|under', c) else 'normal' if re.search('Normal|Healthy', c) else 'over' if 'Overweight' in c else 'obese'
                        ok(g == cat(bb), f'{path} what-if {line}')
        # metric
        for cm, kg in metric_cases:
            pg.click(f'{panel} .unit-btn[data-unit="metric"]')
            pg.fill(f'{panel} .height-cm', str(cm)); pg.fill(f'{panel} .weight-kg', str(kg))
            if t == 'age': pg.fill(f'{panel} .age-input', '40')
            pg.click(f'#calc-{t}-btn'); pg.wait_for_timeout(60)
            h = cm/2.54; R = r1(kg/(cm/100)**2); B = bounds(h)               # metric BMI is kg/m2 as entered (CMB-011)
            shown = pg.inner_text(f'#{t}-bmi-value'); catTxt = pg.inner_text(f'#{t}-bmi-category')
            ok(shown == f'{R:.1f}', f'{path} {cm}cm {kg}kg shown {shown} vs {R}')
            got = 'under' if re.search('(?i)thin|under', catTxt) else 'normal' if re.search('Normal|Healthy', catTxt) else 'over' if 'Overweight' in catTxt else 'obese'
            ok(got == cat(R), f'{path} {cm}cm {kg}kg category {catTxt} for BMI {R}')
            if R >= 40: ok('Class 3' in catTxt, f'{path} {cm}cm {kg}kg: BMI {R} should be class 3 obesity, shown {catTxt}')
            hmin = ' '.join(pg.inner_text(f'#{t}-healthy-min').split()); hmax = ' '.join(pg.inner_text(f'#{t}-healthy-max').split())
            ok(hmin == f"{B['minKg']} kg ({B['minKg']*2.20462:.1f} lbs)", f'{path} {cm}cm min {hmin} vs {B}')
            ok(hmax == f"{B['maxKg']} kg ({B['maxKg']*2.20462:.1f} lbs)", f'{path} {cm}cm max {hmax} vs {B}')
            # the converted limits stay inside the healthy range at that height (CMB-012: 72 kg at 170 cm is 158.7 lbs, not 159)
            ok(r1(B['maxKg']*2.20462*703/h/h) <= 24.9 and r1(round(B['maxKg']*2.20462, 1)*703/h/h) <= 24.9, f'{path} {cm}cm converted max crosses 24.9')
            diff = pg.inner_text(f'#{t}-weight-diff') if pg.locator(f'#{t}-weight-diff').count() else None
            if diff is None: pass
            elif 18.5 <= R < 25: ok(diff.startswith('Within'), f'{path} {cm}cm {kg}: {diff}')
            elif R >= 25:
                d = kg - B['maxKg']; ok(diff.startswith((f'{d:.1f} kg' if d < 10 else f'{round(d)} kg')) and 'above' in diff, f'{path} {cm}cm {kg}kg diff {diff} (maxKg {B["maxKg"]})')
            else:
                d = B['minKg'] - kg; ok(diff.startswith((f'{d:.1f} kg' if d < 10 else f'{round(d)} kg')) and 'below' in diff, f'{path} {cm}cm {kg}kg diff {diff} (minKg {B["minKg"]})')
        ok(not errs, f'{path} JS errors {errs}')
        pg.close()
    # other calculators: run once, no errors
    for path, btn in [('/new-bmi-calculator/', '#calc-newbmi-btn'), ('/kids-bmi-calculator/', '#calc-kids-btn'), ('/ideal-weight/', '#calc-ideal-btn'), ('/lean-body-mass/', '#calc-lbm-btn')]:
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://localhost') else r.abort())
        pg.goto(base + path, wait_until='load'); pg.click(btn); pg.wait_for_timeout(100)
        vis = pg.eval_on_selector('.results-section', 'e => getComputedStyle(e).display') if pg.locator('.results-section').count() else 'n/a'
        ok(not errs and vis != 'none', f'{path} errors {errs} results {vis}')
        rid = {'/new-bmi-calculator/': '#newbmi-results', '/kids-bmi-calculator/': '#kids-results', '/ideal-weight/': '#ideal-results', '/lean-body-mass/': '#lbm-results'}[path]
        txt = pg.inner_text(rid); ok('NaN' not in txt and 'undefined' not in txt and 'Infinity' not in txt, f'{path} NaN/undefined in results')
        if path == '/new-bmi-calculator/':
            print('newbmi sample:', [pg.inner_text(x) for x in ('#newbmi-healthy-min', '#newbmi-healthy-max', '#newbmi-weight-diff') if pg.locator(x).count()])
        pg.close()
    b.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
