#!/usr/bin/env python3
"""Printable BMI chart for women (CMB-014): BMI at each height (4'10" to 6'0", every inch) and weight (90 to 250 lb, every
10 lb), each cell coloured by CDC adult category. The image is the page's <img> chart (indexable, printable); the
page's HTML table carries the same categories as weight ranges.

BMI = lb x 703 / in^2, rounded half-up to one decimal (the gate's round1); category by the rounded value, as the
calculator and scripts/check_weight_tables.py do. Writes the cell values to bcw_grid.csv next to this script.
Renders an SVG in Chromium at 2x to a 1360 px wide PNG, checks every rendered label for overlaps and for fitting its
cell, then stores it as an adaptive-palette PNG.
usage: chart_bcw.py REPO_ROOT OUT_PNG"""
import sys, os, csv, html, io
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import round1, category

HEIGHTS = list(range(58, 73))
WEIGHTS = list(range(90, 251, 10))
TINT = ['#dbeafe', '#d1fae5', '#fde68a', '#fed7aa', '#fecaca', '#fca5a5']        # DESIGN.md category tints
INK = ['#1e3a8a', '#14532d', '#713f12', '#7c2d12', '#7f1d1d', '#7f1d1d']         # text from the same hue (>= 5.2:1)
NAMES = ['Underweight, under 18.5', 'Healthy weight, 18.5–24.9', 'Overweight, 25–29.9', 'Class 1 obesity, 30–34.9',
         'Class 2 obesity, 35–39.9', 'Class 3 obesity, 40 or more']
W = 680
LCOL, X0, TOP, HEAD, ROW = 64, 8, 84, 40, 34
CW = (W - X0 - LCOL - 8) / len(WEIGHTS)

grid, svg = [], []
def t(x, y, s, size, anchor='middle', weight=400, fill='#111827', cls='lab'):
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{html.escape(s)}</text>'

svg.append(t(X0, 30, 'BMI chart for women', 22, anchor='start', weight=700))
svg.append(t(X0, 54, 'BMI at each height and weight, rounded to one decimal. Colors follow CDC adult BMI categories.', 12.5,
             anchor='start', fill='#374151'))
gx0 = X0 + LCOL
svg.append(f'<rect x="{X0}" y="{TOP}" width="{LCOL - 2}" height="{HEAD - 2}" fill="#f3f4f6"/>')
svg.append(t(X0 + LCOL - 8, TOP + 16, 'lb', 12, anchor='end', weight=700, fill='#1f2937'))
svg.append(t(X0 + LCOL - 8, TOP + 31, 'kg', 10.5, anchor='end', fill='#4b5563'))
for j, lb in enumerate(WEIGHTS):
    cx = gx0 + j * CW + CW / 2
    svg.append(f'<rect x="{gx0 + j * CW:.1f}" y="{TOP}" width="{CW - 2:.1f}" height="{HEAD - 2}" fill="#f3f4f6"/>')
    svg.append(t(cx - 1, TOP + 16, f'{lb}', 12, weight=700, fill='#1f2937', cls='cell'))
    svg.append(t(cx - 1, TOP + 31, f'{lb / 2.2046226218:.1f}', 10, fill='#4b5563', cls='cell'))       # exact kg of the lb column, one decimal
for i, h in enumerate(HEIGHTS):
    y = TOP + HEAD + i * ROW
    svg.append(f'<rect x="{X0}" y="{y}" width="{LCOL - 2}" height="{ROW - 2}" fill="#f3f4f6"/>')
    svg.append(t(X0 + 6, y + 13, f'{h // 12}′{h % 12}″', 12.5, anchor='start', weight=700, fill='#1f2937'))
    svg.append(t(X0 + 6, y + 28, f'{h * 2.54:.1f} cm', 10.5, anchor='start', fill='#4b5563'))
    row = []
    for j, lb in enumerate(WEIGHTS):
        b = round1(703.0 * lb / (h * h)); c = category(703.0 * lb / (h * h))
        row.append(b)
        x = gx0 + j * CW
        svg.append(f'<rect x="{x:.1f}" y="{y}" width="{CW - 2:.1f}" height="{ROW - 2}" fill="{TINT[c]}"/>')
        svg.append(t(x + CW / 2 - 1, y + 21, f'{b:.1f}', 12, weight=600 if c == 1 else 400, fill=INK[c], cls='cell'))
    grid.append((f'{h // 12}\'{h % 12}"', round(h * 2.54, 1), row))
gy1 = TOP + HEAD + len(HEIGHTS) * ROW
LEGY = gy1 + 24
for k, name in enumerate(NAMES):
    lx = X0 + (k % 3) * 222; ly = LEGY + (k // 3) * 22
    svg.append(f'<rect x="{lx}" y="{ly - 11}" width="14" height="14" fill="{TINT[k]}" stroke="{INK[k]}" stroke-width="1"/>')
    svg.append(t(lx + 20, ly, name, 12, anchor='start', fill='#1f2937'))
FOOT = LEGY + 2 * 22 + 14
svg.append(t(X0, FOOT, 'BMI = weight (lb) × 703 ÷ height (in)². Categories: CDC Adult BMI Categories. Not for pregnancy or under 20.',
             11, anchor='start', fill='#4b5563'))
svg.append(t(X0, FOOT + 18, 'calculatemybmi.net/blog/bmi-chart-women/', 11.5, anchor='start', weight=600, fill='#0e7490'))
H = int(FOOT + 30)
doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Inter, -apple-system, Segoe UI, Roboto, Arial, sans-serif"><rect width="{W}" height="{H}" fill="#ffffff"/>'
       + ''.join(svg) + '</svg>')

# spot checks against the page's table rule: 5'4" 140 lb = 24.0 (healthy), 150 lb = 25.7 (overweight); 4'10" 90 lb = 18.8
G = {g[0]: g[2] for g in grid}
assert G['5\'4"'][WEIGHTS.index(140)] == 24.0 and G['5\'4"'][WEIGHTS.index(150)] == 25.7 and G['4\'10"'][0] == 18.8

with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': W, 'height': H}, device_scale_factor=2)
    pg.set_content('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#fff}</style>'
                   f'</head><body>{doc}</body></html>')
    pg.wait_for_timeout(200)
    labs = pg.evaluate("() => [...document.querySelectorAll('text')].map(t => { const r = t.getBoundingClientRect(); "
                       "return [t.textContent, t.getAttribute('class'), r.left, r.top, r.right, r.bottom]; })")
    cells = pg.evaluate("() => [...document.querySelectorAll('rect')].slice(1).map(t => { const r = t.getBoundingClientRect(); "
                        "return [r.left, r.top, r.right, r.bottom]; })")
    for i, a in enumerate(labs):
        assert a[2] >= 0 and a[4] <= W and a[3] >= 0 and a[5] <= H, f'outside: {a}'
        for c in labs[i + 1:]:
            if a[2] < c[4] and c[2] < a[4] and a[3] < c[5] and c[3] < a[5]:
                raise SystemExit(f'collision: {a[0]!r} / {c[0]!r}')
        if a[1] == 'cell':                                         # a cell label must sit inside one cell with 2 px to spare
            cx, cy = (a[2] + a[4]) / 2, (a[3] + a[5]) / 2
            box = [r for r in cells if r[0] <= cx <= r[2] and r[1] <= cy <= r[3]]
            assert box and box[0][0] + 2 <= a[2] and a[4] <= box[0][2] - 2, f'label does not fit its cell: {a[0]!r}'
    png = pg.screenshot(clip={'x': 0, 'y': 0, 'width': W, 'height': H})
    br.close()
im = Image.open(io.BytesIO(png)).convert('RGB')
assert im.size == (2 * W, 2 * H), im.size
im.convert('P', palette=Image.ADAPTIVE, colors=96).save(OUT, optimize=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bcw_grid.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['height', 'cm'] + [f'{lb} lb' for lb in WEIGHTS])
    for name, cm, row in grid: w.writerow([name, cm] + [f'{b:.1f}' for b in row])
print(f'chart written {OUT}: {im.size[0]}x{im.size[1]}, {os.path.getsize(OUT):,} bytes, {len(labs)} labels, no collisions')
