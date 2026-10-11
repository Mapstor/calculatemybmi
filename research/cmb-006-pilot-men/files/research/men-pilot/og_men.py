#!/usr/bin/env python3
"""OG image for /men-bmi-calculator/: page title + one real data point (average US man's BMI, CDC 2021-2023).
Renders an inline SVG in Chromium (Inter, the closest match to the site's system-UI stack) to a 1200x630 PNG.
usage: og_men.py OUT_PNG"""
import sys, html
from playwright.sync_api import sync_playwright
out = sys.argv[1]
x0, x1 = 80, 1120
sx = lambda b: x0 + (b - 15) * (x1 - x0) / 25
segs = [(15, 18.5, '#3b82f6'), (18.5, 25, '#22c55e'), (25, 30, '#f59e0b'), (30, 35, '#ef4444'), (35, 40, '#991b1b')]
bars = ''.join(f'<rect x="{sx(a):.1f}" y="352" width="{sx(b) - sx(a):.1f}" height="44" fill="{c}"/>' for a, b, c in segs)
ticks = ''.join(f'<text x="{sx(b):.1f}" y="436" font-size="26" text-anchor="middle" fill="#4b5563">{b:g}</text>' for b in (18.5, 25, 30, 35))
mx = sx(29.4)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" font-family="Inter, sans-serif">
<rect width="1200" height="630" fill="#f9fafb"/>
<rect width="1200" height="92" fill="#164e63"/>
<circle cx="104" cy="46" r="20" fill="none" stroke="#22d3ee" stroke-width="4"/><path d="M104 34 V46 L112 52" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round"/>
<text x="140" y="57" font-size="30" font-weight="700" fill="#ffffff">CalculateMyBMI</text>
<text x="80" y="190" font-size="68" font-weight="700" fill="#111827">BMI Calculator for Men</text>
<text x="80" y="246" font-size="32" fill="#4b5563">Your BMI, your healthy weight and where you rank among US men</text>
{bars}
<line x1="{mx:.1f}" y1="336" x2="{mx:.1f}" y2="410" stroke="#111827" stroke-width="6"/>
<text x="{mx:.1f}" y="322" font-size="30" font-weight="700" text-anchor="middle" fill="#111827">Average US man: BMI 29.4</text>
{ticks}
<text x="80" y="560" font-size="24" fill="#4b5563">Measured by CDC, NHANES August 2021–August 2023</text>
<text x="1120" y="560" font-size="24" font-weight="600" text-anchor="end" fill="#0e7490">calculatemybmi.net</text>
</svg>'''
page = f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:#f9fafb}}</style></head><body>{svg}</body></html>'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    pg.set_content(page); pg.wait_for_timeout(200)
    # collision check on rendered text boxes
    boxes = pg.evaluate("() => [...document.querySelectorAll('text')].map(t => { const r = t.getBoundingClientRect(); return [t.textContent, r.left, r.top, r.right, r.bottom]; })")
    for i, a in enumerate(boxes):
        assert a[1] >= 0 and a[3] <= 1200 and a[2] >= 0 and a[4] <= 630, f'outside: {a}'
        for c in boxes[i + 1:]:
            if a[1] < c[3] and c[1] < a[3] and a[2] < c[4] and c[2] < a[4]:
                raise SystemExit(f'collision: {a[0]!r} / {c[0]!r}')
    pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
    b.close()
print('og written', out, len(boxes), 'labels, no collisions')
