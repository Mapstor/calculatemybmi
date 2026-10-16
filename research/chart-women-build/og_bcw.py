#!/usr/bin/env python3
"""OG image for /blog/bmi-chart-women/ (CMB-014): page title + one real data point (the healthy weight at 5'4") over the
chart itself, one bar per height every 2 inches from 4'10" to 6'0", split where the weight crosses a CDC category line
(the page's own weight limits, from scripts/check_weight_tables.py). Replaces the generic og-image.png.
Renders an inline SVG in Chromium to a 1200x630 PNG and checks the rendered labels for collisions.
usage: og_bcw.py REPO_ROOT OUT_PNG"""
import sys, os, html
from playwright.sync_api import sync_playwright

ROOT, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds

COL = {'under': '#1d4ed8', 'healthy': '#15803d', 'over': '#f59e0b', 'obese': '#b91c1c'}
X0, X1, LO, HI = 150, 1120, 80, 250
def x(lb): return X0 + (lb - LO) * (X1 - X0) / (HI - LO)
rows, labels = [], []
TOP, PITCH, BH = 262, 33, 22
for i, h in enumerate(range(58, 73, 2)):
    cm = h * 2.54
    b = [bounds('lb', h, cm, k) for k in range(4)]
    segs = [('under', LO, b[0][1] + 0.5), ('healthy', b[1][0] - 0.5, b[1][1] + 0.5), ('over', b[2][0] - 0.5, b[2][1] + 0.5),
            ('obese', b[3][0] - 0.5, HI)]
    y = TOP + i * PITCH
    labels.append(f'<text x="{X0 - 14}" y="{y + 18}" font-size="22" font-weight="600" text-anchor="end" fill="#1f2937">{h // 12}′{h % 12}″</text>')
    for k, a, c in segs:
        rows.append(f'<rect x="{x(a) + 1.5:.1f}" y="{y}" width="{x(c) - x(a) - 3:.1f}" height="{BH}" fill="{COL[k]}"/>')
    if h == 64:
        rows.append(f'<rect x="{X0 - 4}" y="{y - 4}" width="{X1 - X0 + 8}" height="{BH + 8}" fill="none" stroke="#111827" stroke-width="3" rx="4"/>')
AXY = TOP + 8 * PITCH + 2
ticks = ''.join(f'<line x1="{x(lb):.1f}" y1="{AXY}" x2="{x(lb):.1f}" y2="{AXY + 6}" stroke="#9ca3af" stroke-width="2"/>'
                f'<text x="{x(lb):.1f}" y="{AXY + 28}" font-size="20" text-anchor="middle" fill="#4b5563">{lb} lb</text>'
                for lb in (80, 120, 160, 200, 240))
leg = ''.join(f'<rect x="{lx}" y="16" width="20" height="20" fill="{COL[k]}"/><text x="{lx + 30}" y="33" '
              f'font-size="22" fill="#1f2937">{n}</text>'
              for lx, (k, n) in zip((80, 290, 520, 720), (('under', 'Underweight'), ('healthy', 'Healthy weight'),
                                                          ('over', 'Overweight'), ('obese', 'Obesity'))))
hb = bounds('lb', 64, 64 * 2.54, 1); kb = bounds('kg', 64, 64 * 2.54, 1)
assert hb == (108, 145) and kb == (49, 65)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" font-family="Inter, sans-serif">
<rect width="1200" height="630" fill="#f9fafb"/>
<rect width="1200" height="92" fill="#164e63"/>
<circle cx="104" cy="46" r="20" fill="none" stroke="#22d3ee" stroke-width="4"/><path d="M104 34 V46 L112 52" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round"/>
<text x="140" y="57" font-size="30" font-weight="700" fill="#ffffff">CalculateMyBMI</text>
<text x="80" y="168" font-size="58" font-weight="700" fill="#111827">BMI chart for women</text>
<text x="80" y="218" font-size="30" fill="#374151">At 5′4″, a healthy weight is {hb[0]}–{hb[1]} lb ({kb[0]}–{kb[1]} kg). CDC bands by height:</text>
{''.join(rows)}
<line x1="{X0}" y1="{AXY}" x2="{X1}" y2="{AXY}" stroke="#d1d5db" stroke-width="2"/>
{''.join(labels)}
{ticks}
<g transform="translate(0 572)">{leg}</g>
<text x="1120" y="618" font-size="20" font-weight="600" text-anchor="end" fill="#0e7490">calculatemybmi.net</text>
</svg>'''
page = f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:#f9fafb}}</style></head><body>{svg}</body></html>'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    pg.set_content(page); pg.wait_for_timeout(200)
    boxes = pg.evaluate("() => [...document.querySelectorAll('text')].map(t => { const r = t.getBoundingClientRect(); return [t.textContent, r.left, r.top, r.right, r.bottom]; })")
    rects = pg.evaluate("() => [...document.querySelectorAll('rect')].slice(2).map(t => { const r = t.getBoundingClientRect(); return [t.getAttribute('fill'), r.left, r.top, r.right, r.bottom]; })")
    for i, a in enumerate(boxes):
        assert a[1] >= 0 and a[3] <= 1200 and a[2] >= 0 and a[4] <= 630, f'outside: {a}'
        for c in boxes[i + 1:]:
            if a[1] < c[3] and c[1] < a[3] and a[2] < c[4] and c[2] < a[4]:
                raise SystemExit(f'collision: {a[0]!r} / {c[0]!r}')
        for r in rects:                       # no label over a bar (swatches sit beside their labels)
            if r[0] not in ('none',) and a[1] < r[3] and r[1] < a[3] and a[2] < r[4] and r[2] < a[4]:
                raise SystemExit(f'label over a shape: {a[0]!r} / {r[0]}')
    pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
    b.close()
print('og written', out, len(boxes), 'labels, no collisions')
