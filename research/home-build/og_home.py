#!/usr/bin/env python3
"""OG image for / (CMB-012): page title + one real data point, the share of US adults in each BMI category
(CDC NHANES August 2021-August 2023; our calculation in home_stats.json, matching NCHS's crude rates).
Renders an inline SVG in Chromium to a 1200x630 PNG and checks the rendered labels for collisions.
usage: og_home.py STATS_JSON OUT_PNG"""
import sys, json, html
from playwright.sync_api import sync_playwright

S = json.load(open(sys.argv[1])); out = sys.argv[2]
CS = S['category_shares_pct']
parts = [('Underweight', CS['underweight'], '#3b82f6'), ('Healthy weight', CS['healthy'], '#22c55e'),
         ('Overweight', CS['overweight'], '#f59e0b'),
         ('Obesity', round(CS['obesity_class_1'] + CS['obesity_class_2'] + CS['obesity_class_3'], 1), '#ef4444')]
assert [p[1] for p in parts] == [1.6, 26.0, 32.1, 40.3], parts
x0, x1, y = 80, 1120, 330
bars, labels, x = [], [], x0
for name, pct, col in parts:
    w = (x1 - x0) * pct / 100
    bars.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="64" fill="{col}"/>')
    if name != 'Underweight':
        cx = x + w / 2
        labels.append(f'<text x="{cx:.1f}" y="{y + 108}" font-size="30" font-weight="700" text-anchor="middle" fill="#111827">{pct:.1f}%</text>')
        labels.append(f'<text x="{cx:.1f}" y="{y + 144}" font-size="26" text-anchor="middle" fill="#374151">{html.escape(name)}</text>')
    x += w
labels.append(f'<text x="{x0}" y="{y - 22}" font-size="24" text-anchor="start" fill="#374151">Underweight 1.6%</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" font-family="Inter, sans-serif">
<rect width="1200" height="630" fill="#f9fafb"/>
<rect width="1200" height="92" fill="#164e63"/>
<circle cx="104" cy="46" r="20" fill="none" stroke="#22d3ee" stroke-width="4"/><path d="M104 34 V46 L112 52" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round"/>
<text x="140" y="57" font-size="30" font-weight="700" fill="#ffffff">CalculateMyBMI</text>
<text x="80" y="182" font-size="68" font-weight="700" fill="#111827">BMI Calculator</text>
<text x="80" y="236" font-size="32" fill="#4b5563">Your BMI, your healthy weight and where you rank among US adults</text>
{''.join(bars)}
{''.join(labels)}
<text x="80" y="580" font-size="24" fill="#4b5563">US adults by BMI category, measured by CDC, 2021–2023</text>
<text x="1120" y="580" font-size="24" font-weight="600" text-anchor="end" fill="#0e7490">calculatemybmi.net</text>
</svg>'''
page = f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:#f9fafb}}</style></head><body>{svg}</body></html>'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    pg.set_content(page); pg.wait_for_timeout(200)
    boxes = pg.evaluate("() => [...document.querySelectorAll('text')].map(t => { const r = t.getBoundingClientRect(); return [t.textContent, r.left, r.top, r.right, r.bottom]; })")
    for i, a in enumerate(boxes):
        assert a[1] >= 0 and a[3] <= 1200 and a[2] >= 0 and a[4] <= 630, f'outside: {a}'
        for c in boxes[i + 1:]:
            if a[1] < c[3] and c[1] < a[3] and a[2] < c[4] and c[2] < a[4]:
                raise SystemExit(f'collision: {a[0]!r} / {c[0]!r}')
    pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
    b.close()
print('og written', out, len(boxes), 'labels, no collisions')
