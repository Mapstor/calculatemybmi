#!/usr/bin/env python3
"""Stripped-content probe: leftovers of earlier automated edits that a style detector can't see.
usage: text_probe.py BASE OUT_JSON PATH ...
  title_only_box   a box (alert/card/callout) whose only text is its title
  empty_section    a heading followed directly by a heading of the same or higher level, or by nothing
  dangling         a paragraph/list item whose text stops on a word that needs an object ("see our guides on")
  glued_word       two words run together ("theoverview")
  orphan_punct     "( )", " ." , ", ," and similar residue
  lowercase_start  a prose paragraph that starts lowercase (a fragment)
  dup_related      the same URL twice in one related/next-steps block
  emoji            emoji in visible text
"""
import sys, re, json
from playwright.sync_api import sync_playwright
from wordfreq import zipf_frequency as zf

BASE, OUT, PATHS = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3:]
JS = r"""
() => {
 const out = {title_only_box:[], empty_section:[], blocks:[], dup_related:[], emoji:[]};
 const main = document.querySelector('main') || document.body;
 const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
 const label = el => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
 // boxes: elements with a visible background or border that hold only one short line of text
 for (const el of main.querySelectorAll('div, aside, section, article')) {
   if (!vis(el) || el.closest('svg, table, form, .calculator-card, .results-section, nav')) continue;
   const cs = getComputedStyle(el);
   const boxed = (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'rgb(255, 255, 255)') || parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 0;
   if (!boxed) continue;
   const t = (el.innerText || '').trim();
   if (!t || t.length > 40 || t.includes('\n')) continue;
   if (el.querySelector('img, svg, canvas, input, select, button, a, iframe')) continue;
   if (el.children.length === 0) continue;  // a plain label/badge, not a box
   out.title_only_box.push(label(el) + ': ' + t);
 }
 // empty sections
 const hs = [...main.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(vis);
 for (let i = 0; i < hs.length; i++) {
   const h = hs[i], lvl = +h.tagName[1];
   // walk forward in document order until the next heading; count visible text in between
   let n = h, text = '';
   const nextH = hs[i + 1];
   const walker = document.createTreeWalker(main, NodeFilter.SHOW_ALL);
   walker.currentNode = h;
   let node = walker.nextNode(), seenContent = false;
   while (node && node !== nextH) {
     if (!h.contains(node)) {
       if (node.nodeType === 3 && node.textContent.trim() && node.parentElement && vis(node.parentElement) && !node.parentElement.closest('h1,h2,h3,h4,h5,h6')) { seenContent = true; break; }
       if (node.nodeType === 1 && /^(IMG|SVG|TABLE|CANVAS|INPUT|SELECT|FIGURE|IFRAME|svg)$/.test(node.nodeName) && vis(node)) { seenContent = true; break; }
     }
     node = walker.nextNode();
   }
   if (!seenContent && (!nextH || +nextH.tagName[1] <= lvl)) out.empty_section.push(h.tagName.toLowerCase() + ': ' + h.innerText.trim().slice(0, 80));
 }
 // prose blocks for text checks
 for (const el of main.querySelectorAll('p, li, td, dd, figcaption, blockquote')) {
   if (!vis(el) || el.closest('svg, nav, .calculator-card, form, .results-section, table')) continue;
   if (el.querySelector('p, li, ul, ol, div')) continue;
   out.blocks.push([label(el), (el.innerText || '').trim()]);
 }
 // related blocks: same href twice
 for (const blk of main.querySelectorAll('[class*=related], [class*=next-steps], .blog-grid, section')) {
   const seen = {};
   for (const a of blk.querySelectorAll('a[href^="/"]')) { const h = a.getAttribute('href').split('#')[0]; seen[h] = (seen[h] || 0) + 1; }
   const d = Object.entries(seen).filter(([h, c]) => c > 1 && /related|next|blog-grid/.test(blk.className));
   for (const [h, c] of d) out.dup_related.push(label(blk) + ': ' + h + ' x' + c);
 }
 const txt = main.innerText;
 for (const m of txt.matchAll(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F000}-\u{1F2FF}]️?/gu)) out.emoji.push(m[0]);
 return out;
}
"""
DANGLE = re.compile(r"\b(on|of|the|our|see|and|or|to|for|with|by|from|at|in|a|an|via|about|like|including|such as|e\.g\.|see our [\w-]+)\s*[:]?\s*$", re.I)

def glued(tok):
    w = tok.lower().strip("'’")
    if len(w) < 8 or not w.isalpha() or zf(w, 'en') > 1.0: return None
    best = None
    for i in range(2, len(w) - 1):
        a, b = w[:i], w[i:]
        fa, fb = zf(a, 'en'), zf(b, 'en')
        if fa >= 3.0 and fb >= 3.0 and len(a) >= 2 and len(b) >= 3:
            s = min(fa, fb)
            if not best or s > best[0]: best = (s, a + ' ' + b)
    return best[1] if best else None

res = {}
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox'])
    page = br.new_page(viewport={'width': 1280, 'height': 900})
    page.route(re.compile(r'^(?!http://localhost).*'), lambda r: r.abort())
    for p in PATHS:
        page.goto(BASE + p, wait_until='load'); page.wait_for_timeout(200)
        r = page.evaluate(JS)
        blocks = r.pop('blocks')
        r['dangling'] = []; r['glued_word'] = []; r['orphan_punct'] = []; r['lowercase_start'] = []
        for lab, t in blocks:
            if not t: continue
            if DANGLE.search(t) and not re.search(r'[.!?)”"]\s*$', t) and len(t.split()) > 3:
                r['dangling'].append(f'{lab}: …{t[-90:]}')
            for tok in re.findall(r"[A-Za-z’']+", t):
                g = glued(tok)
                if g: r['glued_word'].append(f'{tok} -> {g}  [{lab}: …{t[max(0, t.find(tok) - 40):t.find(tok) + 40]}]')
            for m in re.finditer(r'\(\s*\)|\s[.,;:](?=\s|$)|,\s*,|\.\s*\.(?!\.)|\b(according to|see|from|by|via)\s*[.,;)]', t):
                r['orphan_punct'].append(f'{lab}: …{t[max(0, m.start() - 50):m.end() + 30]}')
            if re.match(r'^[a-z]', t) and len(t.split()) > 5 and lab.startswith('p'):
                r['lowercase_start'].append(f'{lab}: {t[:90]}')
        res[p] = {k: v for k, v in r.items() if v}
    br.close()
json.dump(res, open(OUT, 'w'), indent=1)
import collections
c = collections.Counter()
for p, v in res.items():
    for k, vv in v.items(): c[k] += len(vv)
print(dict(c))
