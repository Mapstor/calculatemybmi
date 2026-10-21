#!/usr/bin/env python3
"""Printable body fat percentage chart (CMB-016, /body-fat-percentage-chart/): the provisional ranges for women and men
in three age groups (Gallagher et al., Am J Clin Nutr 2000, as tabulated in J Public Health Afr 2016, Table 1; registry
gallagher-2000-bf-ranges), with the median body fat CDC measured in US adults of that sex and age (our calculation from
NHANES 2011-2018 DXA scans, bfpc_stats.json; ages 8-59 only, so 60-79 reads "not scanned"). The same cells as the page's
chart table, so the page test can compare the two through bfpc_chart.csv.

Renders an SVG in Chromium at 2x to a 1360 px wide PNG, checks every rendered label for overlaps and for fitting its
cell, then stores an adaptive-palette PNG. Cells use the category tints with text from the same hue (DESIGN.md,
5.2:1 or better), as the page's .weight-chart table does.
usage: chart_bfpc.py STATS_JSON OUT_PNG"""
import sys, os, csv, html, io, json
from playwright.sync_api import sync_playwright
from PIL import Image

STATS, OUT = sys.argv[1], sys.argv[2]
S = json.load(open(STATS))
GAL = S['gallagher']['cuts']
BA = S['by_age']

def rng(k, g, which):
    a, b, c = GAL[k][g]
    return {'low': f'under {a}%', 'healthy': f'{a}–{b - 0.1:.1f}%', 'high': f'{b}–{c - 0.1:.1f}%', 'very high': f'{c}% or more'}[which]
ROWS = [(k, g) for k in ('f', 'm') for g in ('20-39', '40-59', '60-79')]
CATS = (('low', 'Low', 'BMI under 18.5'), ('healthy', 'Healthy', 'BMI 18.5–24.9'), ('high', 'High', 'BMI 25–29.9'),
        ('very high', 'Very high', 'BMI 30 or more'))
TINT = {'low': '#dbeafe', 'healthy': '#d1fae5', 'high': '#fde68a', 'very high': '#fecaca'}
INKC = {'low': '#1e3a8a', 'healthy': '#14532d', 'high': '#713f12', 'very high': '#7f1d1d'}
SEXN = {'f': 'Women', 'm': 'Men'}
grid = []
for k, g in ROWS:
    med = f'{BA[k][g]["p50"]:.1f}%' if g in BA[k] else 'not scanned'
    grid.append([SEXN[k], g.replace('-', '–')] + [rng(k, g, c) for c, _, _ in CATS] + [med])
assert grid[0] == ['Women', '20–39', 'under 21%', '21–32.9%', '33–38.9%', '39% or more', '38.1%'], grid[0]
assert grid[5][-1] == 'not scanned' and grid[3][3] == '8–19.9%'

W = 680
X0, LCOL, CW = 20, 120, 100
MW = W - 2 * X0 - LCOL - 4 * CW
TOP, HEAD, ROW, GAP = 76, 46, 40, 10
def esc(s): return html.escape(s, quote=False)
def t(x, y, s, size, cls, anchor='middle', weight=400, fill='#111827'):
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text class="{cls}" x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'
def r(x, y, w, h, fill): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{fill}"/>'

out = [t(X0, 34, 'Body fat percentage chart for women and men', 20, 'title', anchor='start', weight=700),
       t(X0, 56, 'Provisional ranges matched to BMI 18.5, 25 and 30, by age (Gallagher et al., 2000)', 13, 'title',
         anchor='start', fill='#374151')]
# header
out.append(r(X0 + 1, TOP + 1, LCOL - 2, HEAD - 2, '#f3f4f6'))
out.append(t(X0 + 10, TOP + 28, 'Sex and age', 14, 'head', anchor='start', weight=600, fill='#1f2937'))
for i, (c, name, sub) in enumerate(CATS):
    x = X0 + LCOL + i * CW
    out.append(r(x + 1, TOP + 1, CW - 2, HEAD - 2, '#f3f4f6'))
    out.append(t(x + CW / 2, TOP + 20, name, 14, 'head', weight=600, fill='#1f2937'))
    out.append(t(x + CW / 2, TOP + 37, sub, 11.5, 'head', fill='#4b5563'))
xm = X0 + LCOL + 4 * CW
out.append(r(xm + 1, TOP + 1, MW - 2, HEAD - 2, '#f3f4f6'))
out.append(t(xm + MW / 2, TOP + 20, 'US median', 14, 'head', weight=600, fill='#1f2937'))
out.append(t(xm + MW / 2, TOP + 37, 'CDC scans, 2011–18', 11.5, 'head', fill='#4b5563'))
y = TOP + HEAD
for i, row in enumerate(grid):
    if i == 3: y += GAP
    out.append(r(X0 + 1, y + 1, LCOL - 2, ROW - 2, '#f3f4f6'))
    out.append(t(X0 + 10, y + 25, f'{row[0]} {row[1]}', 14, 'row', anchor='start', weight=600, fill='#1f2937'))
    for j, (c, _, _) in enumerate(CATS):
        x = X0 + LCOL + j * CW
        out.append(r(x + 1, y + 1, CW - 2, ROW - 2, TINT[c]))
        out.append(t(x + CW / 2, y + 25, row[2 + j], 14, 'cell', fill=INKC[c]))
    out.append(r(xm + 1, y + 1, MW - 2, ROW - 2, '#ffffff'))
    med = row[-1]
    out.append(t(xm + MW / 2, y + 25, med, 14 if med != 'not scanned' else 12.5, 'cell',
                 weight=600 if med != 'not scanned' else 400, fill='#111827' if med != 'not scanned' else '#4b5563'))
    y += ROW
y += 24
for line in ('Ranges: Gallagher et al., Am J Clin Nutr 2000, as tabulated in J Public Health Afr 2016 (Table 1). The original',
             'study gives different values for each of its three ethnic groups. US median: our calculation from CDC NHANES',
             '2011–2018 DXA body scans, which covered ages 8 to 59.   calculatemybmi.net/body-fat-percentage-chart/'):
    out.append(t(X0, y, line, 12, 'foot', anchor='start', fill='#374151'))
    y += 17
H = y + 4
assert (2 * W, 2 * H) == (1360, 902), (2 * W, 2 * H)
doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif">'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + ''.join(out) + '</svg>')

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
        if a[1] in ('cell', 'head', 'row'):                        # a label must sit inside one box with 3 px to spare
            cx, cy = (a[2] + a[4]) / 2, (a[3] + a[5]) / 2
            box = [b for b in cells if b[0] <= cx <= b[2] and b[1] <= cy <= b[3]]
            assert box and box[0][0] + 3 <= a[2] and a[4] <= box[0][2] - 3, f'label does not fit its box: {a[0]!r}'
    png = pg.screenshot(clip={'x': 0, 'y': 0, 'width': W, 'height': H})
    br.close()
im = Image.open(io.BytesIO(png)).convert('RGB')
assert im.size == (2 * W, 2 * H), im.size
im.convert('P', palette=Image.ADAPTIVE, colors=96).save(OUT, optimize=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bfpc_chart.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['sex', 'age', 'low', 'healthy', 'high', 'very_high', 'us_median'])
    for row in grid: w.writerow(row)
print(f'chart written {OUT}: {im.size[0]}x{im.size[1]}, {os.path.getsize(OUT):,} bytes, {len(labs)} labels, no collisions')
