#!/usr/bin/env python3
"""Printable BMI table for adults (CMB-015, /bmi-chart/): for every height from 4'10" to 6'6" (every inch), the lightest
whole pound whose BMI reaches each column's BMI (18.5, then every whole BMI from 19 to 40). Cells are tinted by the CDC
adult category the column starts, so the 18.5, 25, 30, 35 and 40 columns equal the category limits in the page's
chart table. The image is the page's <img> chart (indexable, printable); the page's HTML tables carry the same limits
as weight ranges.

BMI = lb x 703 / in^2, rounded half-up to one decimal (the gate's round1), as the calculator and
scripts/check_weight_tables.py do. Writes the cell values to bc_grid.csv next to this script. Renders an SVG in
Chromium at 2x to a 1640 px wide PNG, checks every rendered label for overlaps and for fitting its cell, then stores
it as an adaptive-palette PNG.
usage: chart_bc.py REPO_ROOT OUT_PNG"""
import sys, os, csv, html, io, math
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import round1, bounds

HEIGHTS = list(range(58, 79))
COLS = [18.5] + list(range(19, 41))
def col_cat(b): return 1 if b < 25 else 2 if b < 30 else 3 if b < 35 else 4 if b < 40 else 5
TINT = ['#dbeafe', '#d1fae5', '#fde68a', '#fed7aa', '#fecaca', '#fca5a5']        # DESIGN.md category tints
INK = ['#1e3a8a', '#14532d', '#713f12', '#7c2d12', '#7f1d1d', '#7f1d1d']         # text from the same hue (>= 5.2:1)
NAMES = [None, 'Healthy weight, 18.5–24.9', 'Overweight, 25–29.9', 'Class 1 obesity, 30–34.9',
         'Class 2 obesity, 35–39.9', 'Class 3 obesity, 40 or more']


def start_lb(h, b):
    """Lightest whole pound whose BMI, rounded half-up to 0.1, is at least b at h inches."""
    w = math.ceil((b - 0.05) * h * h / 703.0 - 1e-9)
    while round1(703.0 * w / (h * h)) < b: w += 1
    while round1(703.0 * (w - 1) / (h * h)) >= b: w -= 1
    return w


W = 820
LCOL, X0, TOP, HEAD, ROW = 64, 8, 92, 30, 32
CW = (W - X0 - LCOL - 8) / len(COLS)
grid, svg = [], []
def t(x, y, s, size, anchor='middle', weight=400, fill='#111827', cls='lab'):
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{html.escape(s)}</text>'

svg.append(t(X0, 30, 'BMI table for adults', 22, anchor='start', weight=700))
svg.append(t(X0, 54, 'Find your height, then move across to the heaviest weight that is not above yours. Your BMI is the number at the',
             12.5, anchor='start', fill='#374151'))
svg.append(t(X0, 72, 'top of that column or a little more. Each cell is in pounds. Colors follow CDC adult BMI categories.', 12.5,
             anchor='start', fill='#374151'))
gx0 = X0 + LCOL
svg.append(f'<rect x="{X0}" y="{TOP}" width="{LCOL - 2}" height="{HEAD - 2}" fill="#f3f4f6"/>')
svg.append(t(X0 + LCOL - 8, TOP + 19, 'BMI', 12, anchor='end', weight=700, fill='#1f2937'))
for j, b in enumerate(COLS):
    c = col_cat(b); x = gx0 + j * CW
    svg.append(f'<rect x="{x:.1f}" y="{TOP}" width="{CW - 2:.1f}" height="{HEAD - 2}" fill="{TINT[c]}"/>')
    svg.append(t(x + CW / 2 - 1, TOP + 19, f'{b:g}', 11.5, weight=700, fill=INK[c], cls='cell'))
for i, h in enumerate(HEIGHTS):
    y = TOP + HEAD + i * ROW
    svg.append(f'<rect x="{X0}" y="{y}" width="{LCOL - 2}" height="{ROW - 2}" fill="#f3f4f6"/>')
    svg.append(t(X0 + 6, y + 13, f'{h // 12}′{h % 12}″', 12.5, anchor='start', weight=700, fill='#1f2937'))
    svg.append(t(X0 + 6, y + 27, f'{h * 2.54:.1f} cm', 10, anchor='start', fill='#4b5563'))
    row = []
    for j, b in enumerate(COLS):
        lb = start_lb(h, b); c = col_cat(b)
        row.append(lb)
        x = gx0 + j * CW
        svg.append(f'<rect x="{x:.1f}" y="{y}" width="{CW - 2:.1f}" height="{ROW - 2}" fill="{TINT[c]}"/>')
        svg.append(t(x + CW / 2 - 1, y + 20, str(lb), 12, fill=INK[c], cls='cell'))
    grid.append((f'{h // 12}\'{h % 12}"', round(h * 2.54, 1), row))
gy1 = TOP + HEAD + len(HEIGHTS) * ROW
LEGY = gy1 + 26
for k in range(1, 6):
    lx = X0 + ((k - 1) % 3) * 262; ly = LEGY + ((k - 1) // 3) * 22
    svg.append(f'<rect x="{lx}" y="{ly - 11}" width="14" height="14" fill="{TINT[k]}" stroke="{INK[k]}" stroke-width="1"/>')
    svg.append(t(lx + 20, ly, NAMES[k], 12, anchor='start', fill='#1f2937'))
svg.append(t(X0 + 2 * 262, LEGY + 22, 'Lighter than the 18.5 column: underweight', 12, anchor='start', fill='#1f2937'))
FOOT = LEGY + 2 * 22 + 16
svg.append(t(X0, FOOT, 'Each cell is the lightest whole pound whose BMI, rounded to one decimal, reaches the BMI at the top of '
             'its column.', 11, anchor='start', fill='#4b5563'))
svg.append(t(X0, FOOT + 16, 'BMI = weight (lb) × 703 ÷ height (in)². Categories: CDC adult BMI categories. Not for pregnancy '
             'or under age 20.', 11, anchor='start', fill='#4b5563'))
svg.append(t(X0, FOOT + 35, 'calculatemybmi.net/bmi-chart/', 11.5, anchor='start', weight=600, fill='#0e7490'))
H = int(FOOT + 47)
doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Inter, -apple-system, Segoe UI, Roboto, Arial, sans-serif"><rect width="{W}" height="{H}" fill="#ffffff"/>'
       + ''.join(svg) + '</svg>')

# The category columns equal the chart table's lower limits (the gate's own bounds), at every height.
for h, (name, cm, row) in zip(HEIGHTS, grid):
    for k, b in ((1, 18.5), (2, 25), (3, 30), (4, 35), (5, 40)):
        assert row[COLS.index(b)] == bounds('lb', h, h * 2.54, k)[0], (h, b)
    for j, b in enumerate(COLS):                                  # each cell reaches its BMI; one pound less does not
        assert round1(703.0 * row[j] / (h * h)) >= b > round1(703.0 * (row[j] - 1) / (h * h)), (h, b)
G = {g[0]: g[2] for g in grid}
assert G['5\'9"'][COLS.index(19)] == 129 and G['5\'9"'][COLS.index(25)] == 169 and G['4\'10"'][0] == 89

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
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bc_grid.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['height', 'cm'] + [f'BMI {b:g}' for b in COLS])
    for name, cm, row in grid: w.writerow([name, cm] + row)
print(f'chart written {OUT}: {im.size[0]}x{im.size[1]}, {os.path.getsize(OUT):,} bytes, {len(labs)} labels, no collisions')
