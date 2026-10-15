#!/usr/bin/env python3
"""OG image for /blog/healthy-bmi-range/ (CMB-013): page title + one real data point, the risk of death by BMI band in
3,951,455 never-smokers without chronic disease (Global BMI Mortality Collaboration, Lancet 2016;388:776-86, the
hazard ratios gen_hbr.py prints on the page). Replaces healthy-bmi-envelope.png, which drew age-specific "healthy"
bands (D-11).
Renders an inline SVG in Chromium to a 1200x630 PNG and checks the rendered labels for collisions.
usage: og_hbr.py OUT_PNG"""
import sys, html
from playwright.sync_api import sync_playwright

out = sys.argv[1]
GBMC = [('15–18.4', 1.51, '#3b82f6'), ('18.5–19.9', 1.13, '#22c55e'), ('20–22.4', 1.00, '#22c55e'),
        ('22.5–24.9', 1.00, '#22c55e'), ('25–27.4', 1.07, '#f59e0b'), ('27.5–29.9', 1.20, '#f59e0b'),
        ('30–34.9', 1.45, '#ef4444'), ('35–39.9', 1.94, '#ef4444'), ('40–59.9', 2.76, '#991b1b')]
X0, X1, BASE, K, GAP = 80, 1120, 540, 76, 20
CW = (X1 - X0 - GAP * (len(GBMC) - 1)) / len(GBMC)
cols, labels = [], []
hx0, hx1 = X0 + 1 * (CW + GAP) - GAP / 2, X0 + 3 * (CW + GAP) + CW + GAP / 2
band = f'<rect x="{hx0:.1f}" y="362" width="{hx1 - hx0:.1f}" height="{BASE + 4 - 362}" fill="#ecfdf5"/>'
labels.append(f'<text x="{(hx0 + hx1) / 2:.1f}" y="392" font-size="26" font-weight="700" text-anchor="middle" fill="#15803d">Healthy range</text>')
for i, (lab, hr, col) in enumerate(GBMC):
    x = X0 + i * (CW + GAP); h = hr * K; cx = x + CW / 2
    cols.append(f'<rect x="{x:.1f}" y="{BASE - h:.1f}" width="{CW:.1f}" height="{h:.1f}" fill="{col}"/>')
    labels.append(f'<text x="{cx:.1f}" y="{BASE - h - 10:.1f}" font-size="26" font-weight="700" text-anchor="middle" fill="#111827">{hr:.2f}</text>')
    labels.append(f'<text x="{cx:.1f}" y="{BASE + 28}" font-size="20" text-anchor="middle" fill="#374151">{html.escape(lab)}</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" font-family="Inter, sans-serif">
<rect width="1200" height="630" fill="#f9fafb"/>
<rect width="1200" height="92" fill="#164e63"/>
<circle cx="104" cy="46" r="20" fill="none" stroke="#22d3ee" stroke-width="4"/><path d="M104 34 V46 L112 52" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round"/>
<text x="140" y="57" font-size="30" font-weight="700" fill="#ffffff">CalculateMyBMI</text>
<text x="80" y="170" font-size="60" font-weight="700" fill="#111827">Healthy BMI range: 18.5–24.9</text>
<text x="80" y="222" font-size="30" fill="#4b5563">The same for every adult. Risk of death by BMI in never-smokers:</text>
{band}
{''.join(cols)}
<line x1="{X0}" y1="{BASE}" x2="{X1}" y2="{BASE}" stroke="#9ca3af" stroke-width="2"/>
{''.join(labels)}
<text x="80" y="612" font-size="22" fill="#4b5563">Hazard ratio vs BMI 22.5–24.9 (= 1.00). GBMC, Lancet 2016</text>
<text x="1120" y="612" font-size="22" font-weight="600" text-anchor="end" fill="#0e7490">calculatemybmi.net</text>
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
        for r in rects:                       # no label over a column (the shaded band behind the healthy columns is allowed)
            if r[0] != '#ecfdf5' and a[1] < r[3] and r[1] < a[3] and a[2] < r[4] and r[2] < a[4]:
                raise SystemExit(f'label over a column: {a[0]!r}')
    pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
    b.close()
print('og written', out, len(boxes), 'labels, no collisions')
