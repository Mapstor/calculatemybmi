#!/usr/bin/env python3
"""No page wider than the viewport (360/390/1280) and the mobile menu opens and closes. usage: overflow_menu.py BASE PATH ..."""
import sys, re
from playwright.sync_api import sync_playwright
BASE, PATHS = sys.argv[1].rstrip('/'), sys.argv[2:]
wide = []; menu_ok = 0; menu_bad = []
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox'])
    for w in (360, 390, 1280):
        page = br.new_page(viewport={'width': w, 'height': 800})
        page.route(re.compile(r'^(?!http://localhost).*'), lambda r: r.abort())
        for p in PATHS:
            page.goto(BASE + p, wait_until='load'); page.wait_for_timeout(120)
            sw = page.evaluate('document.documentElement.scrollWidth')
            if sw > w: wide.append(f'{p}@{w}={sw}')
            if w == 390:
                t = page.query_selector('.nav-toggle')
                if t:
                    t.click(); page.wait_for_timeout(250)
                    o = page.evaluate("() => { const n = document.querySelector('.nav-mobile'); return n ? getComputedStyle(n).display !== 'none' && n.getBoundingClientRect().height > 50 : false }")
                    t.click(); page.wait_for_timeout(250)
                    c = page.evaluate("() => { const n = document.querySelector('.nav-mobile'); return n ? (getComputedStyle(n).display === 'none' || n.getBoundingClientRect().height < 5) : true }")
                    if o and c: menu_ok += 1
                    else: menu_bad.append(p)
        page.close()
    br.close()
print(f'overflow checks {len(PATHS) * 3}, pages wider than viewport: {len(wide)} {wide[:5]}')
print(f'menu open+close ok on {menu_ok}/{len(PATHS)} {menu_bad[:5]}')
