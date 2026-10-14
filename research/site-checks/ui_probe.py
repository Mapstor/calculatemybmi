#!/usr/bin/env python3
"""UI integrity probe (things the impeccable detector does not look for).
usage: ui_probe.py BASE_URL OUT_JSON PATH [PATH ...]
Per page, at 390x844 and 1280x900:
  dead_cta      short call-to-action text ("Calculate ...", "Try ...", "... ->") with no link or button
  unstyled_btn  a/button with btn/cta/button class that renders as plain text
  no_rule_cls   classes in <main> with no CSS rule anywhere (candidate missing styles)
  broken_img    images that failed to load
  raw_entity    literal &xxx; in rendered text
  artifact      undefined / NaN / null / {{ }} in rendered text (before and after a calculator run)
  empty_box     visible cards/boxes/cells with no content
  dup_id        duplicate ids
  dead_link     <a> without href, href="#", or href to a missing local page
  small_target  non-inline buttons/controls under 24 px
"""
import sys, json, os, re
from playwright.sync_api import sync_playwright

BASE, OUT, PATHS = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3:]
ROOT = os.environ.get('PROBE_ROOT', '.')   # repo root, for the missing-page check

JS = r"""
() => {
 const out = {dead_cta:[], unstyled_btn:[], no_rule_cls:{}, broken_img:[], raw_entity:[], artifact:[], empty_box:[], dup_id:[], dead_link:[], small_target:[], hrefs:[]};
 const sels = new Set();
 for (const ss of document.styleSheets) { let rules; try { rules = ss.cssRules } catch(e) { continue }
   const walk = (rs) => { for (const r of rs) { if (r.selectorText) { for (const m of r.selectorText.matchAll(/\.([A-Za-z0-9_-]+)/g)) sels.add(m[1]); } if (r.cssRules) walk(r.cssRules); } };
   walk(rules); }
 const main = document.querySelector('main') || document.body;
 const label = (el) => el.tagName.toLowerCase() + (el.id ? '#'+el.id : '') + (el.className && typeof el.className === 'string' ? '.'+el.className.trim().split(/\s+/).join('.') : '');
 for (const el of main.querySelectorAll('[class]')) { if (el.closest('svg')) continue; for (const c of el.classList) if (!sels.has(c)) { const k = el.tagName.toLowerCase()+'.'+c; out.no_rule_cls[k] = (out.no_rule_cls[k]||0)+1; } }
 const CTA = /^(calculate|try|use|check|see|find|get|start|read|view|learn|open|compare|explore|go to|discover|take|estimate|measure)\b/i;
 for (const el of main.querySelectorAll('p, div, span, li, strong, em')) {
   if (el.closest('a,button,label,select,option,nav,th,td,summary,svg,figcaption,.faq-question')) continue;
   if (el.querySelector('a,button,input,select,textarea')) continue;
   const t = (el.textContent||'').trim().replace(/\s+/g,' ');
   if (!t || t.split(' ').length > 9) continue;
   const r = el.getBoundingClientRect(); if (r.width === 0 || r.height === 0) continue;
   if (CTA.test(t) || /(→|»)\s*$/.test(t)) out.dead_cta.push(label(el)+': '+t);
 }
 for (const el of main.querySelectorAll('a, button')) {
   const cls = (typeof el.className === 'string' ? el.className : '');
   if (!/btn|button|cta/i.test(cls) && el.tagName !== 'BUTTON') continue;
   const cs = getComputedStyle(el); const r = el.getBoundingClientRect(); if (r.width === 0) continue;
   const bg = cs.backgroundColor; const hasBg = !(bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') || cs.backgroundImage !== 'none';
   const hasBorder = parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none';
   const pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingLeft);
   if (!hasBg && !hasBorder && pad < 6) out.unstyled_btn.push(label(el)+': '+el.textContent.trim().slice(0,60));
 }
 for (const img of document.images) if (img.complete && img.naturalWidth === 0 && img.getAttribute('loading') !== 'lazy') out.broken_img.push(img.getAttribute('src'));
 const txt = document.body.innerText;
 for (const m of txt.matchAll(/&(?:[a-zA-Z]+|#\d+);/g)) out.raw_entity.push(m[0]);
 for (const m of txt.matchAll(/\b(undefined|NaN)\b|\{\{|\}\}|\[object Object\]/g)) out.artifact.push(m[0]);
 for (const el of main.querySelectorAll('[class*=card], [class*=box], [class*=tile], [class*=kpi], [class*=stat], li, td, p')) {
   if ((el.textContent||'').trim()) continue;
   if (el.querySelector('img,svg,canvas,input,iframe,select,button')) continue;
   if (el.closest('.adthrive, [id^=AdThrive], [class*=adthrive], [class*=ad-]')) continue;
   const r = el.getBoundingClientRect(); if (r.width*r.height > 0) out.empty_box.push(label(el)+' '+Math.round(r.width)+'x'+Math.round(r.height));
 }
 const ids = {}; for (const el of document.querySelectorAll('[id]')) ids[el.id] = (ids[el.id]||0)+1;
 out.dup_id = Object.entries(ids).filter(([k,v])=>v>1).map(([k,v])=>k+' x'+v);
 for (const a of document.querySelectorAll('a')) {
   const h = a.getAttribute('href');
   if (h === null) { if ((a.textContent||'').trim()) out.dead_link.push('no href: '+a.textContent.trim().slice(0,60)); continue; }
   if (h === '#' || h === '') out.dead_link.push('href="'+h+'": '+a.textContent.trim().slice(0,60));
   else out.hrefs.push(h);
 }
 for (const el of main.querySelectorAll('button, input, select, a[class]')) {
   const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
   if (r.width > 0 && r.height > 0 && (r.height < 24 || r.width < 24) && cs.display !== 'inline' && el.type !== 'hidden' && el.type !== 'radio' && el.type !== 'checkbox')
     out.small_target.push(label(el)+' '+Math.round(r.width)+'x'+Math.round(r.height));
 }
 return out;
}
"""

def local_exists(href):
    if re.match(r'^(https?:|mailto:|tel:|javascript:|#)', href): return True
    p = href.split('#')[0].split('?')[0]
    if not p.startswith('/'): return True
    f = os.path.join(ROOT, p.lstrip('/'))
    return os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html')) or os.path.isfile(f + '.html')

results = {}
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox'])
    for vw, vh in ((390, 844), (1280, 900)):
        ctx = br.new_context(viewport={'width': vw, 'height': vh})
        page = ctx.new_page()
        page.route(re.compile(r'^(?!http://localhost).*'), lambda r: r.abort())  # no third-party calls
        for p in PATHS:
            page.goto(BASE + p, wait_until='load')
            page.wait_for_timeout(250)
            # scroll through so lazy images load
            page.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 700) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 15)); } window.scrollTo(0, 0); }")
            page.wait_for_timeout(200)
            r = page.evaluate(JS)
            # run the calculator if the page has one, then look for artifacts again
            if page.query_selector('.calculate-btn'):
                try:
                    btn = page.query_selector('.calculate-btn')
                    btn.scroll_into_view_if_needed(); btn.click(); page.wait_for_timeout(300)
                    t = page.evaluate("() => document.body.innerText")
                    for m in re.finditer(r'\b(undefined|NaN)\b|\{\{|\}\}|\[object Object\]', t): r['artifact'].append('after calc: ' + m.group(0))
                except Exception as e:
                    r['artifact'].append('calc click failed: ' + str(e)[:80])
            r['dead_link'] += ['missing page: ' + h for h in sorted(set(r.pop('hrefs'))) if not local_exists(h)]
            key = f'{p} @{vw}'
            results[key] = {k: v for k, v in r.items() if v}
        ctx.close()
    br.close()
json.dump(results, open(OUT, 'w'), indent=1, sort_keys=True)
# summary
import collections
tot = collections.Counter()
for k, v in results.items():
    for kk, vv in v.items():
        if kk != 'no_rule_cls': tot[kk] += len(vv)
print('issues by type (both widths):', dict(tot))
