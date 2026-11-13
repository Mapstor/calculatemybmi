#!/usr/bin/env python3
"""Social images for /blog/bmi-history/ and /blog/waist-to-height-ratio/ (CMB-042), redrawn from each page's own
figure after this batch corrected it: the history timeline shows Metropolitan Life's 1959 tables of desirable weights
(Nuttall 2015) in place of "1900s insurance adoption", and the waist diagram marks NICE's boundary as "≥ 0.5,
increased risk" in place of "> 0.5, elevated risk" (NICE NG246: 0.5 or more is increased central adiposity).

Same frame as the phase-13 image set they belong to: 1200x630, a 90 px header band (#0d5567) with the title in white
bold sans, the figure scaled to fit 1080x480 and centred in the space below the band, and the CalculateMyBMI wordmark
(#94a3b8) at the bottom right; with the default serif, main's history figure in this frame gives the old image to
within anti-aliasing. The labels are set in the site's own font stack, as the page draws them: in the set's default
serif, "measure here" runs into the note CMB-040 moved beside it. Renders in Chromium and checks that no label leaves
the image, no two labels collide, and each image says what its page now says.

usage: python3 research/cmb-042/og_images.py [--check] [--only history|whtr] [--page FILE] [--out PNG]
  --check  render and check, write nothing
  --only   one image; --page and --out then override where its figure is read from and where it is written"""
import argparse
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[2]
BAND, BG, INK, MARK = '#0d5567', '#f8fafc', '#000000', '#94a3b8'
W, H, BAND_H, FIT_W, FIT_H = 1200, 630, 90, 1080, 480
# --font-sans in assets/css/styles.css
FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
IMAGES = {
    'history': dict(page='blog/bmi-history/index.html', out='assets/images/og/bmi-history-timeline.png',
                    figure='svg-history-title svg-history-desc', title='BMI history timeline (1832–2026)',
                    must=['1959 MetLife'], never=['1900', 'insurance adoption']),
    'whtr': dict(page='blog/waist-to-height-ratio/index.html', out='assets/images/og/waist-height-diagram.png',
                 figure='svg-whtr-diagram-title svg-whtr-diagram-desc', title='Waist measurement + WHtR formula',
                 must=['≥ 0.5', 'increased risk'], never=['elevated', '> 0.5']),
}

ap = argparse.ArgumentParser()
ap.add_argument('--check', action='store_true')
ap.add_argument('--only', choices=sorted(IMAGES))
ap.add_argument('--page')
ap.add_argument('--out')
ap.add_argument('--no-content-check', action='store_true', help=argparse.SUPPRESS)  # re-rendering main's figures
args = ap.parse_args()
if (args.page or args.out) and not args.only:
    ap.error('--page and --out need --only')


def frame(spec, page_file):
    page = Path(page_file).read_text(encoding='utf-8')
    m = re.search(r'<svg[^>]*aria-labelledby="' + re.escape(spec['figure']) + r'"[^>]*>.*?</svg>', page, re.S)
    assert m, f'figure {spec["figure"]} not found on {page_file}'
    svg = m.group(0)
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    vw, vh = int(vb.group(1)), int(vb.group(2))
    k = min(FIT_W / vw, FIT_H / vh)
    fw, fh = vw * k, vh * k
    # the page sizes the figure with CSS; here it gets the frame's size and the set's serif labels
    svg = re.sub(r'\sstyle="[^"]*"', '', svg, count=1)
    svg = svg.replace('<svg ', f'<svg width="{fw}" height="{fh}" ', 1)
    left, top = (W - fw) / 2, BAND_H + (H - BAND_H - fh) / 2
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:{BG};}}
#frame{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{BG};}}
#band{{position:absolute;left:0;top:0;width:{W}px;height:{BAND_H}px;background:{BAND};}}
#fig{{position:absolute;left:{left}px;top:{top}px;width:{fw}px;height:{fh}px;color:{INK};font-family:{FONT};}}
#over{{position:absolute;left:0;top:0;}}
</style></head><body><div id="frame">
<div id="band"></div>
<div id="fig">{svg}</div>
<svg id="over" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="DejaVu Sans, sans-serif">
<text x="{W / 2}" y="58" font-size="30" font-weight="700" text-anchor="middle" fill="#ffffff">{spec['title']}</text>
<text x="1180" y="614" font-size="18" text-anchor="end" fill="{MARK}">CalculateMyBMI</text>
</svg></div></body></html>'''


names = [args.only] if args.only else list(IMAGES)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
    for name in names:
        spec = IMAGES[name]
        src = args.page or str(REPO / spec['page'])
        out = args.out or str(REPO / spec['out'])
        pg.set_content(frame(spec, src))
        pg.wait_for_timeout(300)
        boxes = pg.evaluate("""() => [...document.querySelectorAll('text')].map(t => {
            const r = t.getBoundingClientRect(); return [t.textContent, r.left, r.top, r.right, r.bottom]; })""")
        words = ' | '.join(x[0] for x in boxes)
        if not args.no_content_check:
            for w in spec['must']:
                assert w in words, f'{name}: "{w}" missing: {words}'
            for w in spec['never']:
                assert w not in words, f'{name}: "{w}" still drawn: {words}'
        for i, a in enumerate(boxes):
            assert a[1] >= 0 and a[3] <= W and a[2] >= 0 and a[4] <= H, f'{name}: outside the image: {a}'
            for c in boxes[i + 1:]:
                # 1 px of slack: the two lines of a stacked label touch at their line boxes
                if a[1] < c[3] and c[1] < a[3] and a[2] < c[4] - 1 and c[2] < a[4] - 1:
                    raise SystemExit(f'{name}: labels collide: {a[0]!r} / {c[0]!r}')
        if args.check:
            print(f'check {name}: {len(boxes)} labels, none outside the image, no collisions; nothing written')
        else:
            pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': W, 'height': H})
            print(f'written {out}: {len(boxes)} labels, none outside the image, no collisions')
    b.close()
