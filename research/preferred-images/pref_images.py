#!/usr/bin/env python3
"""Preferred images for Google Search (CMB-015): one text-free picture per page in three aspect ratios, 16:9
(1200x675), 4:3 (1200x900) and 1:1 (1200x1200), written to assets/images/preferred/<name>-<ratio>.png.

Why: Google picks the image next to a result (and in Discover) on its own, and its image guide (section "Specify a
preferred image with metadata", March 2026) says how to steer that choice: name a preferred image in og:image, in
schema.org primaryImageOfPage or as the main entity's image; make it relevant and representative of the page; avoid a
generic image such as a site logo and avoid an image with text; avoid extreme aspect ratios; use a high resolution.
Its Article guide asks for several high-resolution images in 16:9, 4:3 and 1:1. So each picture below is the page's
own figure redrawn without a word, number or logo, centered so any crop keeps it whole.

Pages and pictures (the data are the pages' own):
  bmi-chart          the BMI chart: CDC category bands over height (4'10"-6'6") and weight (80-300 lb), the bands'
                     edges at BMI 18.5, 25, 30 and 40 (35 as a thin line), and the page's example dot (5'9", 185 lb).
  bmi-calculator     the homepage's "of every 100 US adults" grid: 2 underweight, 26 healthy weight, 32 overweight,
                     31 class 1-2 obesity, 9 class 3 obesity (research/bmi-chart-build/bc_stats.json, largest remainder).
  healthy-bmi-range  the guide's risk-of-death bars by BMI band, never-smokers (GBMC 2016 hazard ratios, as in
                     research/healthy-range-build/gen_hbr.py), the healthy bands on a light green ground.
  bmi-chart-women    the women's chart hero: one bar per height (4'10"-6'0", every 2 in) split where the weight crosses
                     a CDC category line (scripts/check_weight_tables.py), 5'4" outlined.
  body-fat-percentage-chart  the body fat chart hero (CMB-016): the provisional ranges for women and men aged 20-39,
                     40-59 and 60-79 (low, healthy, high, very high; research/body-fat-chart-build/bfpc_stats.json),
                     one bar per group, women above men.
  women-bmi-calculator  the women's calculator "BMI by age" figure (CMB-017): for each decade from the 20s to 80 and over,
                     the 10th-90th percentile line, the middle half and the median of US women's BMI
                     (research/women-calc-build/wbc_stats.json) over CDC's healthy range, BMI 16.5 to 44.5.
  bmi-chart-men      the men's chart hero (CMB-018): one row per height from 5'4" to 6'2", the CDC category bands in
                     pounds as light tints, and across each row the middle half of US men of that height (bar) and their
                     median weight (tick), research/chart-men-build/bcm_stats.json; 100 to 260 lb, centered.
  average-weight     the /average-weight/ hero (CMB-019): the band of healthy weights at each height (BMI 18.5-24.9,
                     whole pounds by scripts/check_weight_tables.py) and the average weight of US women and men at each
                     height with 30 or more measured (research/average-weight/avgw_results.json), dots joined by a line;
                     4'9" to 6'3" by 80 to 260 lb, centered.
  body-fat-calculator  the body fat calculator's accuracy figure (CMB-020): formula minus scan on CDC's DXA scans for
                     relative fat mass and the Deurenberg formula, women and men (research/body-fat-calculator-build/
                     bfc_stats.json): the 10th-90th percentile line, the middle half and the median, each row on its own
                     dashed zero line; -10 to +10 points, centered.
  how-to-measure-body-fat  the /blog/how-to-measure-body-fat/ hero (CMB-021): seven methods against one DXA scanner in the
                     same 437 college students (Burns et al. 2019, Table 3; research/how-to-measure-body-fat-build/
                     burns_2019_table3.json): each method's average difference from the scan (dot) and its 90% CI (line),
                     each row on its own dashed zero line, light grid lines at -6, -4 and -2; -6.5 to +0.5 points, centered.
  us-obesity-statistics  the /us-obesity-statistics/ hero (CMB-022): obesity, overweight and severe obesity among US
                     adults aged 20 to 74 in every CDC survey from 1960-1962 to August 2021-August 2023 (age-adjusted; the
                     page's CSV, = NCHS Health E-Stat 111 Table 1): three lines with a dot per survey in the category
                     colors (red, amber, dark red) over light grid lines at 0, 10, 20, 30, 40 and 50%, centered.
Renders each SVG in Chromium at its exact size, checks there is no <text> and the size, and stores a palette PNG.
usage: pref_images.py REPO_ROOT [NAME ...]   (NAMEs: draw only those pages; CMB-022 drew us-obesity-statistics)"""
import sys, os, io, json
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds

OUT = os.path.join(ROOT, 'assets/images/preferred')
SIZES = {'16x9': (1200, 675), '4x3': (1200, 900), '1x1': (1200, 1200)}
BG = '#f8fafc'
BASE = {'under': '#3b82f6', 'healthy': '#22c55e', 'over': '#f59e0b', 'obese': '#ef4444', 'severe': '#991b1b'}


def frame(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>')


def bmi_chart(w, h):
    """CDC category bands over height x weight, as the /bmi-chart/ hero draws them."""
    mx, my = round(w * 0.06), round(h * 0.08)
    x0, x1, y0, y1 = mx, w - mx, my, h - my
    HLO, HHI, WLO, WHI = 58, 78, 80, 300
    hx = lambda i: x0 + (i - HLO) * (x1 - x0) / (HHI - HLO)
    wy = lambda lb: y1 - (lb - WLO) * (y1 - y0) / (WHI - WLO)
    steps = [HLO + k * 0.1 for k in range(int((HHI - HLO) / 0.1) + 1)]
    def curve(b): return [(hx(s), wy(min(max(b * s * s / 703.0, WLO), WHI))) for s in steps]
    bands = [(None, 18.5, 'under'), (18.5, 25, 'healthy'), (25, 30, 'over'), (30, 40, 'obese'), (40, None, 'severe')]
    out = [f'<clipPath id="c"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="28"/></clipPath><g clip-path="url(#c)">']
    for lo, hi, k in bands:
        lower = curve(lo) if lo else [(hx(s), wy(WLO)) for s in steps]
        upper = curve(hi) if hi else [(hx(s), wy(WHI)) for s in steps]
        pts = lower + upper[::-1]
        out.append('<path d="M' + 'L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + f'Z" fill="{BASE[k]}"/>')
    for b, sw, op in ((18.5, 5, 1), (25, 5, 1), (30, 5, 1), (35, 2.5, 0.75), (40, 5, 1)):
        out.append('<polyline points="' + ' '.join(f'{a:.1f},{c:.1f}' for a, c in curve(b))
                   + f'" fill="none" stroke="#ffffff" stroke-width="{sw}" stroke-opacity="{op}"/>')
    out.append('</g>')
    r = min(w, h) * 0.022
    out.append(f'<circle cx="{hx(69):.1f}" cy="{wy(185):.1f}" r="{r:.1f}" fill="#111827" stroke="#ffffff" stroke-width="{r * 0.45:.1f}"/>')
    return frame(w, h, ''.join(out))


def waffle(w, h):
    """Of every 100 US adults, by BMI category (the homepage grid, filled row by row)."""
    S = json.load(open(os.path.join(ROOT, 'research/bmi-chart-build/bc_stats.json')))['categories']['all']
    shares = [('under', S['underweight']['pct']), ('healthy', S['healthy']['pct']), ('over', S['overweight']['pct']),
              ('obese', S['class_1']['pct'] + S['class_2']['pct']), ('severe', S['class_3']['pct'])]
    n = [int(v) for _, v in shares]                              # largest remainder to 100
    for i in sorted(range(5), key=lambda i: -(shares[i][1] - int(shares[i][1])))[:100 - sum(n)]: n[i] += 1
    assert n == [2, 26, 32, 31, 9], n                            # = the homepage figure
    side = min(w, h) * 0.84
    gap = side / 10 * 0.14
    sq = (side - 9 * gap) / 10
    gx, gy = (w - side) / 2, (h - side) / 2
    cats = [k for (k, _), c in zip(shares, n) for _ in range(c)]
    out = []
    for i, k in enumerate(cats):
        r, c = divmod(i, 10)
        out.append(f'<rect x="{gx + c * (sq + gap):.1f}" y="{gy + r * (sq + gap):.1f}" width="{sq:.1f}" height="{sq:.1f}" '
                   f'rx="{sq * 0.16:.1f}" fill="{BASE[k]}"/>')
    return frame(w, h, ''.join(out))


def risk_bars(w, h):
    """Risk of death by BMI band, never-smokers: GBMC 2016 hazard ratios (the healthy-range guide's figure)."""
    G = [(1.51, 'under'), (1.13, 'healthy'), (1.00, 'healthy'), (1.00, 'healthy'), (1.07, 'over'), (1.20, 'over'),
         (1.45, 'obese'), (1.94, 'obese'), (2.76, 'severe')]
    mx, my = w * 0.07, h * 0.1
    x0, x1, y0, y1 = mx, w - mx, my, h - my
    slot = (x1 - x0) / len(G)
    bw = slot * 0.72
    k = (y1 - y0) / 2.76
    out = [f'<rect x="{x0 + slot * 1 - slot * 0.1:.1f}" y="{y0 - h * 0.04:.1f}" width="{slot * 3.2:.1f}" height="{y1 - y0 + h * 0.04:.1f}" '
           f'rx="{slot * 0.18:.1f}" fill="#dcfce7"/>']
    for i, (hr, c) in enumerate(G):
        bx = x0 + i * slot + (slot - bw) / 2
        bh = hr * k
        r = bw * 0.14
        out.append(f'<path d="M{bx:.1f} {y1:.1f}V{y1 - bh + r:.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {-r:.1f}h{bw - 2 * r:.1f}'
                   f'a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {r:.1f}V{y1:.1f}Z" fill="{BASE[c]}"/>')
    ref = y1 - 1.0 * k
    out.append(f'<line x1="{x0:.1f}" y1="{ref:.1f}" x2="{x1:.1f}" y2="{ref:.1f}" stroke="#111827" stroke-width="{max(3, h * 0.005):.1f}" '
               f'stroke-dasharray="{w * 0.012:.1f} {w * 0.01:.1f}" stroke-opacity="0.55"/>')
    out.append(f'<line x1="{x0:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#9ca3af" stroke-width="4"/>')
    return frame(w, h, ''.join(out))


def women_bars(w, h):
    """The women's chart hero: one bar per height, split at the CDC category weights; 5'4" outlined."""
    HS = list(range(58, 73, 2))
    LO, HI = 80, 250
    mx, my = w * 0.07, h * 0.09
    x0, x1 = mx, w - mx
    pitch = (h - 2 * my) / len(HS)
    bh = pitch * 0.66
    xs = lambda lb: x0 + (lb - LO) * (x1 - x0) / (HI - LO)
    out = []
    for i, ht in enumerate(HS):
        cm = ht * 2.54
        b = [bounds('lb', ht, cm, q) for q in range(4)]
        segs = [('under', LO, b[0][1] + 0.5), ('healthy', b[1][0] - 0.5, b[1][1] + 0.5),
                ('over', b[2][0] - 0.5, b[2][1] + 0.5), ('obese', b[3][0] - 0.5, HI)]
        y = my + i * pitch + (pitch - bh) / 2
        for k, a, c in segs:
            out.append(f'<rect x="{xs(a) + 2:.1f}" y="{y:.1f}" width="{xs(c) - xs(a) - 4:.1f}" height="{bh:.1f}" rx="{bh * 0.12:.1f}" fill="{BASE[k]}"/>')
        if ht == 64:
            pad = pitch * 0.12
            out.append(f'<rect x="{x0 - pad:.1f}" y="{y - pad:.1f}" width="{x1 - x0 + 2 * pad:.1f}" height="{bh + 2 * pad:.1f}" '
                       f'rx="{bh * 0.25:.1f}" fill="none" stroke="#111827" stroke-width="{max(4, pad * 0.45):.1f}"/>')
    return frame(w, h, ''.join(out))


def body_fat(w, h):
    """The body fat chart hero: provisional ranges for women and men in three age groups, a gap between the sexes."""
    G = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))['gallagher']['cuts']
    rows = [G[k][g] for k in ('f', 'm') for g in ('20-39', '40-59', '60-79')]
    assert rows[0] == [21, 33, 39] and rows[3] == [8, 20, 25]
    mx, my = w * 0.07, h * 0.1
    x0, x1 = mx, w - mx
    pitch = (h - 2 * my) / 6.6                                   # six bars and a gap of 0.6 bar between the sexes
    bh = pitch * 0.62
    xs = lambda p: x0 + p * (x1 - x0) / 50.0
    out = []
    for i, (a, b, c) in enumerate(rows):
        y = my + (i + (0.6 if i >= 3 else 0)) * pitch + (pitch - bh) / 2
        for k, lo, hi in (('under', 0, a), ('healthy', a, b), ('over', b, c), ('obese', c, 50)):
            out.append(f'<rect x="{xs(lo) + 3:.1f}" y="{y:.1f}" width="{xs(hi) - xs(lo) - 6:.1f}" height="{bh:.1f}" '
                       f'rx="{bh * 0.18:.1f}" fill="{BASE[k]}"/>')
    return frame(w, h, ''.join(out))


def women_calc(w, h):
    """The women's calculator figure: US women's BMI by decade (10th-90th line, middle half, median) over the healthy range."""
    DEC = json.load(open(os.path.join(ROOT, 'research/women-calc-build/wbc_stats.json')))['decades']
    ages = ('20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')
    assert f"{DEC['20-29']['p50']:.1f}" == '25.5' and f"{DEC['80+']['p50']:.1f}" == '26.9'
    mx, my = w * 0.07, h * 0.1
    x0, x1 = mx, w - mx
    xs = lambda b: x0 + (b - 16.5) * (x1 - x0) / 28.0               # BMI 16.5-44.5: the rows and the band, centered
    pitch = (h - 2 * my) / len(ages)
    bh = pitch * 0.5
    out = [f'<rect x="{xs(18.5):.1f}" y="{my - pitch * 0.15:.1f}" width="{xs(25) - xs(18.5):.1f}" height="{h - 2 * my + pitch * 0.3:.1f}" '
           f'rx="{pitch * 0.12:.1f}" fill="#bbf7d0"/>']
    for i, d in enumerate(ages):
        v = DEC[d]; yc = my + (i + 0.5) * pitch
        out.append(f'<line x1="{xs(v["p10"]):.1f}" y1="{yc:.1f}" x2="{xs(v["p90"]):.1f}" y2="{yc:.1f}" stroke="#be185d" '
                   f'stroke-width="{max(3, pitch * 0.07):.1f}" stroke-linecap="round"/>')
        out.append(f'<rect x="{xs(v["p25"]):.1f}" y="{yc - bh / 2:.1f}" width="{xs(v["p75"]) - xs(v["p25"]):.1f}" height="{bh:.1f}" '
                   f'rx="{bh * 0.2:.1f}" fill="#f9a8d4"/>')
        out.append(f'<rect x="{xs(v["p50"]) - max(3, pitch * 0.05):.1f}" y="{yc - bh * 0.7:.1f}" width="{2 * max(3, pitch * 0.05):.1f}" '
                   f'height="{bh * 1.4:.1f}" rx="2" fill="#111827"/>')
    return frame(w, h, ''.join(out))


def men_chart(w, h):
    """The men's chart hero: CDC bands in pounds per height (light tints), US men's middle half (bar) and median (tick)."""
    BH = json.load(open(os.path.join(ROOT, 'research/chart-men-build/bcm_stats.json')))['by_height']
    HS = list(range(64, 75))
    assert f"{BH['70']['weight_q'][1]:.1f}" == '199.1'                    # CMB-019: NCHS's factor and percentile method
    LO, HI = 100, 260
    TINTS = {'under': '#dbeafe', 'healthy': '#d1fae5', 'over': '#fde68a', 'obese': '#fecaca'}
    mx, my = w * 0.07, h * 0.08
    x0, x1 = mx, w - mx
    pitch = (h - 2 * my) / len(HS)
    bh = pitch * 0.7
    xs = lambda lb: x0 + (min(max(lb, LO), HI) - LO) * (x1 - x0) / (HI - LO)
    out = []
    for i, ht in enumerate(HS):
        cm = ht * 2.54
        b = [bounds('lb', ht, cm, q) for q in range(4)]
        segs = [('under', LO, b[0][1] + 0.5), ('healthy', b[1][0] - 0.5, b[1][1] + 0.5),
                ('over', b[2][0] - 0.5, b[2][1] + 0.5), ('obese', b[3][0] - 0.5, HI)]
        y = my + i * pitch + (pitch - bh) / 2
        for k, a, c in segs:
            out.append(f'<rect x="{xs(a) + 1.5:.1f}" y="{y:.1f}" width="{xs(c) - xs(a) - 3:.1f}" height="{bh:.1f}" fill="{TINTS[k]}"/>')
        q = BH[str(ht)]['weight_q']
        th = max(8, bh * 0.36)
        out.append(f'<rect x="{xs(q[0]):.1f}" y="{y + (bh - th) / 2:.1f}" width="{xs(q[2]) - xs(q[0]):.1f}" height="{th:.1f}" '
                   f'rx="{th / 2:.1f}" fill="#4338ca"/>')
        tw = max(5, w * 0.005)
        out.append(f'<rect x="{xs(q[1]) - tw / 2:.1f}" y="{y - bh * 0.06:.1f}" width="{tw:.1f}" height="{bh * 1.12:.1f}" rx="2" fill="#111827"/>')
    return frame(w, h, ''.join(out))


def avg_weight(w, h):
    """The /average-weight/ hero: the healthy band per height and the average weight of US women and men per height."""
    AV = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json')))
    HLO, HHI, WLO, WHI = 56.5, 75.5, 80, 260
    side = min(w, h * 1.5)                                   # same proportions in every crop, centered
    pw, ph = side * 0.84, side * 0.84 / 1.5
    x0, y0 = (w - pw) / 2, (h - ph) / 2
    hx = lambda i: x0 + (i - HLO) * pw / (HHI - HLO)
    wy = lambda lb: y0 + ph - (lb - WLO) * ph / (WHI - WLO)
    hs = list(range(57, 76))
    B = {i: bounds('lb', i, i * 2.54, 1) for i in hs}
    band = ' '.join(f'{hx(i):.1f},{wy(B[i][1]):.1f}' for i in hs) + ' ' + ' '.join(f'{hx(i):.1f},{wy(B[i][0]):.1f}' for i in reversed(hs))
    out = [f'<line x1="{x0:.1f}" y1="{wy(k):.1f}" x2="{x0 + pw:.1f}" y2="{wy(k):.1f}" stroke="#e5e7eb" '
           f'stroke-width="{side * 0.002:.1f}"/>' for k in (100, 150, 200, 250)]          # light grid under the band
    out.append(f'<polygon points="{band}" fill="#d1fae5" stroke="#15803d" stroke-opacity="0.5" stroke-width="{side * 0.003:.1f}"/>')
    for sex, col in (('women', '#be185d'), ('men', '#4338ca')):
        pts = sorted((int(k), v['wt']['mean']) for k, v in AV[sex]['height'].items())
        for i, m in pts:
            assert m > B[i][1], (sex, i)                      # every average sits above the healthy band
        out.append(f'<polyline points="{" ".join(f"{hx(i):.1f},{wy(m):.1f}" for i, m in pts)}" fill="none" stroke="{col}" '
                   f'stroke-width="{side * 0.007:.1f}" stroke-linejoin="round"/>')
        for i, m in pts:
            out.append(f'<circle cx="{hx(i):.1f}" cy="{wy(m):.1f}" r="{side * 0.012:.1f}" fill="{col}" stroke="{BG}" '
                       f'stroke-width="{side * 0.004:.1f}"/>')
    return frame(w, h, ''.join(out))


def bf_calc(w, h):
    """The body fat calculator's accuracy figure: formula minus scan, two formulas x two sexes, on dashed zero lines."""
    F = json.load(open(os.path.join(ROOT, 'research/body-fat-calculator-build/bfc_stats.json')))['formulas']
    assert f"{F['rfm']['women']['err_q']['p50']:.1f}" == '2.3' and f"{F['deur']['men']['err_q']['p50']:.1f}" == '-0.3'
    rows = (('rfm', 'women', '#be185d'), ('rfm', 'men', '#4338ca'), ('deur', 'women', '#be185d'), ('deur', 'men', '#4338ca'))
    side = min(w, h * 1.5)                                   # same proportions in every crop, centered
    pw, ph = side * 0.84, side * 0.84 / 1.5
    x0, y0 = (w - pw) / 2, (h - ph) / 2
    xs = lambda e: x0 + (min(max(e, -10), 10) + 10) * pw / 20
    pitch = ph / len(rows)
    bh = pitch * 0.44
    out = []
    for i, (f, sx, col) in enumerate(rows):
        q = F[f][sx]['err_q']; yc = y0 + (i + 0.5) * pitch
        out.append(f'<line x1="{xs(0):.1f}" y1="{yc - pitch * 0.42:.1f}" x2="{xs(0):.1f}" y2="{yc + pitch * 0.42:.1f}" '
                   f'stroke="#4b5563" stroke-width="{side * 0.004:.1f}" stroke-dasharray="{side * 0.012:.1f} {side * 0.009:.1f}"/>')
        out.append(f'<line x1="{xs(q["p10"]):.1f}" y1="{yc:.1f}" x2="{xs(q["p90"]):.1f}" y2="{yc:.1f}" stroke="{col}" '
                   f'stroke-width="{side * 0.006:.1f}" stroke-linecap="round"/>')
        out.append(f'<rect x="{xs(q["p25"]):.1f}" y="{yc - bh / 2:.1f}" width="{xs(q["p75"]) - xs(q["p25"]):.1f}" height="{bh:.1f}" '
                   f'rx="{bh * 0.15:.1f}" fill="{col}" fill-opacity="0.18" stroke="{col}" stroke-width="{side * 0.003:.1f}"/>')
        tw = max(5, side * 0.006)
        out.append(f'<rect x="{xs(q["p50"]) - tw / 2:.1f}" y="{yc - bh * 0.68:.1f}" width="{tw:.1f}" height="{bh * 1.36:.1f}" '
                   'rx="2" fill="#111827"/>')
    return frame(w, h, ''.join(out))


def htm(w, h):
    """The how-to-measure hero: seven methods minus DXA (dot) with the 90% CI (line), each row on a dashed zero line."""
    T = json.load(open(os.path.join(ROOT, 'research/how-to-measure-body-fat-build/burns_2019_table3.json'), encoding='utf-8'))
    rows = sorted(T['rows'], key=lambda r: r['diff'])
    assert [r['key'] for r in rows] == ['hw', 'sf', 'adp', 'valhalla', 'tanita', 'ir', 'omron']
    assert all(r['diff'] > 0 for r in rows) and max(r['ci90'][1] for r in rows) < 6
    side = min(w, h * 1.5)                                   # same proportions in every crop, centered
    pw, ph = side * 0.84, side * 0.84 / 1.5
    x0, y0 = (w - pw) / 2, (h - ph) / 2
    xs = lambda e: x0 + (e + 6.5) * pw / 7                   # -6.5 to +0.5 points: the -6 grid line and zero line sit evenly
    pitch = ph / len(rows)
    out = []
    for i, r in enumerate(rows):
        yc = y0 + (i + 0.5) * pitch
        for e in (-6, -4, -2):
            out.append(f'<line x1="{xs(e):.1f}" y1="{yc - pitch * 0.4:.1f}" x2="{xs(e):.1f}" y2="{yc + pitch * 0.4:.1f}" '
                       f'stroke="#e5e7eb" stroke-width="{side * 0.003:.1f}"/>')
        out.append(f'<line x1="{xs(0):.1f}" y1="{yc - pitch * 0.42:.1f}" x2="{xs(0):.1f}" y2="{yc + pitch * 0.42:.1f}" '
                   f'stroke="#4b5563" stroke-width="{side * 0.004:.1f}" stroke-dasharray="{side * 0.012:.1f} {side * 0.009:.1f}"/>')
        out.append(f'<line x1="{xs(-r["ci90"][1]):.1f}" y1="{yc:.1f}" x2="{xs(-r["ci90"][0]):.1f}" y2="{yc:.1f}" '
                   f'stroke="#0e7490" stroke-width="{side * 0.009:.1f}" stroke-linecap="round"/>')
        out.append(f'<circle cx="{xs(-r["diff"]):.1f}" cy="{yc:.1f}" r="{side * 0.014:.1f}" fill="#111827" stroke="#ffffff" '
                   f'stroke-width="{side * 0.004:.1f}"/>')
    return frame(w, h, ''.join(out))


def obs_trend(w, h):
    """The US obesity hero: obesity, overweight and severe obesity, adults 20-74, every survey 1960-1962 to 2021-2023."""
    import csv
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, 'us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv'),
                                           encoding='utf-8'))
            if r['dataset'] == 'HE111_T1_adults_20-74' and r['sex'] == 'all']
    ser = {}
    for r in rows:
        ser.setdefault(r['measure'], []).append((float(r['midpoint_year']), float(r['percent'])))
    for k in ser: ser[k].sort()
    assert sorted(ser) == ['obesity', 'overweight', 'severe obesity'] and all(len(v) == 15 for v in ser.values())
    assert ser['obesity'][0] == (1961.5, 13.4) and ser['obesity'][-1] == (2022.6, 40.8)
    side = min(w, h * 1.6)                                   # same proportions in every crop, centered
    pw, ph = side * 0.84, side * 0.84 / 1.6
    x0, y0 = (w - pw) / 2, (h - ph) / 2
    xs = lambda y: x0 + (y - 1960) * pw / 64                 # 1960 to 2024
    ys = lambda v: y0 + ph - v * ph / 50                     # 0 to 50%
    out = []
    for v in range(0, 51, 10):
        out.append(f'<line x1="{x0:.1f}" y1="{ys(v):.1f}" x2="{x0 + pw:.1f}" y2="{ys(v):.1f}" stroke="#e2e8f0" '
                   f'stroke-width="{side * 0.0025:.1f}"/>')
    for key, col in (('overweight', BASE['over']), ('obesity', BASE['obese']), ('severe obesity', BASE['severe'])):
        pts = ' '.join(f'{xs(a):.1f},{ys(b):.1f}' for a, b in ser[key])
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{side * 0.008:.1f}" '
                   'stroke-linejoin="round" stroke-linecap="round"/>')
        for a, b in ser[key]:
            out.append(f'<circle cx="{xs(a):.1f}" cy="{ys(b):.1f}" r="{side * 0.009:.1f}" fill="{col}" stroke="#ffffff" '
                       f'stroke-width="{side * 0.003:.1f}"/>')
    return frame(w, h, ''.join(out))


PAGES = {'bmi-chart': bmi_chart, 'bmi-calculator': waffle, 'healthy-bmi-range': risk_bars, 'bmi-chart-women': women_bars,
         'body-fat-percentage-chart': body_fat, 'women-bmi-calculator': women_calc, 'bmi-chart-men': men_chart,
         'average-weight': avg_weight, 'body-fat-calculator': bf_calc, 'how-to-measure-body-fat': htm,
         'us-obesity-statistics': obs_trend}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
        for name, draw in PAGES.items():
            if sys.argv[2:] and name not in sys.argv[2:]:
                continue
            for ratio, (w, h) in SIZES.items():
                svg = draw(w, h)
                assert '<text' not in svg and '<image' not in svg            # no words, numbers or logos
                pg = br.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
                pg.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0}}</style>'
                               f'</head><body>{svg}</body></html>')
                pg.wait_for_timeout(100)
                png = pg.screenshot(clip={'x': 0, 'y': 0, 'width': w, 'height': h})
                pg.close()
                im = Image.open(io.BytesIO(png)).convert('RGB')
                assert im.size == (w, h), im.size
                path = os.path.join(OUT, f'{name}-{ratio}.png')
                im.convert('P', palette=Image.ADAPTIVE, colors=64).save(path, optimize=True)
                print(f'{path}: {w}x{h}, {os.path.getsize(path):,} bytes')
        br.close()
