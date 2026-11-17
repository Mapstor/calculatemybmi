#!/usr/bin/env python3
"""OG image for /blog/bmi-categories/ (CMB-067): page topic + one real data set, the share of US adults aged 20 and over in
each of the six adult BMI categories, 2021-2023 (CDC NHANES, our calculation in cat_stats.py, the shares the page prints).
Replaces bmi-categories-scale.png (a generic WHO scale with no data). Renders an inline SVG in Chromium to a 1200x630 PNG
and checks the rendered labels for collisions.
usage: og_cat.py STATS_JSON OUT_PNG"""
import html
import json
import sys

from playwright.sync_api import sync_playwright

C = json.load(open(sys.argv[1]))['categories']['all']['all_ages']
out = sys.argv[2]
ROWS = [('Underweight', 'under 18.5', 'underweight', '#3b82f6'), ('Healthy weight', '18.5–24.9', 'healthy', '#22c55e'),
        ('Overweight', '25–29.9', 'overweight', '#f59e0b'), ('Class 1 obesity', '30–34.9', 'class_1', '#ef4444'),
        ('Class 2 obesity', '35–39.9', 'class_2', '#ef4444'), ('Class 3 obesity', '40 or more', 'class_3', '#991b1b')]
X0, K, Y0, RH = 492, 15, 196, 62
bars, labels = [], []
for i, (name, rng, key, col) in enumerate(ROWS):
    y = Y0 + i * RH
    v = C[key]['pct']
    labels.append(f'<text x="80" y="{y + 30}" font-size="30" font-weight="700" fill="#111827">{html.escape(name)}</text>')
    labels.append(f'<text x="330" y="{y + 30}" font-size="26" fill="#4b5563">{html.escape(rng)}</text>')
    bars.append(f'<rect x="{X0}" y="{y + 6}" width="{v * K:.1f}" height="34" rx="4" fill="{col}"/>')
    labels.append(f'<text x="{X0 + v * K + 14:.1f}" y="{y + 33}" font-size="28" font-weight="700" fill="#111827">{v}%</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" font-family="Inter, sans-serif">
<rect width="1200" height="630" fill="#f9fafb"/>
<rect width="1200" height="92" fill="#164e63"/>
<circle cx="104" cy="46" r="20" fill="none" stroke="#22d3ee" stroke-width="4"/><path d="M104 34 V46 L112 52" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round"/>
<text x="140" y="57" font-size="30" font-weight="700" fill="#ffffff">CalculateMyBMI</text>
<text x="80" y="160" font-size="50" font-weight="700" fill="#111827">BMI categories: US adults in each</text>
{''.join(bars)}
{''.join(labels)}
<text x="80" y="606" font-size="22" fill="#4b5563">Adults 20+, CDC NHANES 2021–2023, our calculation</text>
<text x="1120" y="606" font-size="22" font-weight="600" text-anchor="end" fill="#0e7490">calculatemybmi.net</text>
</svg>'''
page = f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:#f9fafb}}</style></head><body>{svg}</body></html>'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    pg.set_content(page)
    pg.wait_for_timeout(200)
    boxes = pg.evaluate("() => [...document.querySelectorAll('text')].map(t => { const r = t.getBoundingClientRect(); return [t.textContent, r.left, r.top, r.right, r.bottom]; })")
    rects = pg.evaluate("() => [...document.querySelectorAll('rect')].slice(2).map(t => { const r = t.getBoundingClientRect(); return [t.getAttribute('fill'), r.left, r.top, r.right, r.bottom]; })")
    for i, a in enumerate(boxes):
        assert a[1] >= 0 and a[3] <= 1200 and a[2] >= 0 and a[4] <= 630, f'outside: {a}'
        for c in boxes[i + 1:]:
            if a[1] < c[3] and c[1] < a[3] and a[2] < c[4] and c[2] < a[4]:
                raise SystemExit(f'collision: {a[0]!r} / {c[0]!r}')
        for r in rects:
            if a[1] < r[3] and r[1] < a[3] and a[2] < r[4] and r[2] < a[4]:
                raise SystemExit(f'label over a bar: {a[0]!r}')
    pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
    b.close()
print('og written', out, len(boxes), 'labels, no collisions')
