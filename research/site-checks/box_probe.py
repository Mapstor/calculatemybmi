#!/usr/bin/env python3
"""Visible empty boxes, before and after running each page's calculator. usage: box_probe.py BASE PATH ..."""
import sys, re
from playwright.sync_api import sync_playwright
BASE, PATHS = sys.argv[1].rstrip('/'), sys.argv[2:]
JS = r"""
() => {
  const out = [];
  const root = document.querySelector('main') || document.body;
  for (const el of root.querySelectorAll('div, p, section, aside, li, td, span, a')) {
    const r = el.getBoundingClientRect(); if (r.width < 24 || r.height < 16) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    if (el.closest('svg, [hidden], [aria-hidden="true"], .rank-track, [class*=bar], [class*=track], [class*=fill], [class*=marker], [class*=legend], [class*=swatch], [class*=dot], [class*=key], [class*=scale], [class*=spark], [id*=map], [class*=map], [class*=chart], [class*=adthrive], [id^=AdThrive]')) continue;
    const bg = cs.backgroundColor, boxed = (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') || parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 1;
    if (!boxed) continue;
    if ((el.innerText || '').trim()) continue;
    if (el.querySelector('img, svg, canvas, input, select, button, iframe, video')) continue;
    out.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).join('.') : '') + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  }
  return out;
}
"""
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox'])
    page = br.new_page(viewport={'width': 390, 'height': 844})
    page.route(re.compile(r'^(?!http://localhost).*'), lambda r: r.abort())
    for p in PATHS:
        page.goto(BASE + p, wait_until='load'); page.wait_for_timeout(200)
        before = page.evaluate(JS)
        after = []
        btn = page.query_selector('.calculate-btn, .aw-cta')
        if btn:
            try:
                btn.scroll_into_view_if_needed(); btn.click(); page.wait_for_timeout(400)
                after = [x for x in page.evaluate(JS) if x not in before]
            except Exception as e: after = ['click failed ' + str(e)[:60]]
        if before or after: print(p, '| before calc:', before, '| after calc:', after)
    br.close()
print('done')
