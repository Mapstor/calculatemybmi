#!/usr/bin/env python3
# Reference test (CMB-005): clicks the first FAQ question on each page and the mobile-menu toggle. Needs Playwright + Chromium.
# usage: python3 faq_probe_playwright.py http://localhost:8000 / /men-bmi-calculator/ ...
"""Click the first FAQ question on each page; report whether it opens. usage: faqprobe.py BASEURL path1 path2 ..."""
import sys, json
from playwright.sync_api import sync_playwright
base=sys.argv[1]; paths=sys.argv[2:]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--no-sandbox','--disable-dev-shm-usage'])
    ctx=b.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
    for path in paths:
        pg=ctx.new_page(); pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://localhost') else r.abort())
        pg.goto(base+path, wait_until='load')
        q=pg.locator('.faq-question')
        if q.count()==0: print(path,'no faq'); pg.close(); continue
        q.first.scroll_into_view_if_needed(); q.first.click(); pg.wait_for_timeout(120)
        o1=pg.locator('.faq-item.open').count()
        vis=pg.locator('.faq-answer').first.is_visible()
        # nav toggle
        nt=pg.locator('.nav-toggle'); navok=None
        if nt.count() and nt.first.is_visible():
            pg.evaluate("window.scrollTo(0,0)"); nt.first.click(); pg.wait_for_timeout(120)
            navok=pg.locator('.nav-mobile.active').count()
        print(f"{path:45s} faq_open={o1} answer_visible={vis} mobile_menu_open={navok}")
        pg.close()
    b.close()
