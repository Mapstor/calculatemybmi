#!/usr/bin/env python3
"""Content-integrity gate (CMB-010). Imported by scripts/check_structure.py; also runs alone:
    python3 scripts/check_content_integrity.py FILE ...
Catches what earlier automated edits left behind and what a style detector cannot see:
  - a call to action left as plain text (its link was removed)
  - empty boxes: a box with only its title, a step with only its heading, an empty table frame,
    an empty result box, a padded box with nothing inside
  - sentences whose opening was cut: a paragraph that starts lowercase, a sentence that starts
    lowercase, ", For ..." joins
  - the same page linked twice in one related block, or a related card that links nowhere
  - cards inside a paragraph
  - emoji or pictographs used as icons in visible text
  - inline-styled button links (use .cta-button, D-13) and inline-styled bylines (use .byline)
  - D-11: sex-specific "healthy/optimal" BMI ranges
  - placeholders in headings ("(teaser)", TODO, TBD, lorem)
CMB-011 adds what a deleted table or section leaves behind:
  - numbered items that skip a number ("Limitation #1, #3", "Method 2" with no Method 1)
  - a caption for rows or columns in a section that has no table, or "the table below" on a page without one
  - a chart row without its bar, an empty bar track, an empty icon
  - a heading with nothing under it before the next heading of the same or higher rank
js_problems() checks assets/js/calculator.js (the results panel): no emoji or arrow/dingbat entities,
no base category hexes or other low-contrast hexes as text colour, no gradients.
"""
import re, sys, html
from html.parser import HTMLParser

CTA_START = r'(?:Calculate|Check|Try|Use|See|Find|Get|Start|Compare|Estimate|Measure|Explore|Go to|Open)'
ABBR = {'e.g', 'i.e', 'vs', 'approx', 'etc', 'dr', 'st', 'no', 'fig', 'al', 'u.s', 'cf', 'ca', 'min', 'max',
        'lb', 'lbs', 'kg', 'cm', 'in', 'ft', 'oz', 'jr', 'sr', 'dis', 'nutr', 'med', 'res', 'vol', 'p', 'pp'}
LOWER_OK = {'doi', 'et', 'and', 'com', 'net', 'org', 'gov', 'pmc', 'pmid', 'html', 'pdf', 'js'}
EMOJI = re.compile('[☀-➿\U0001f000-\U0001faff]')

def _visible(src):
    m = re.search(r'(?s)<main\b.*?</main>', src)
    b = m.group(0) if m else src
    return re.sub(r'(?s)<script.*?</script>|<style.*?</style>|<svg.*?</svg>', '', b)

def _text(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()

class _Related(HTMLParser):
    """hrefs per related block (any element whose class mentions related or blog-grid) and cards with no link."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.blocks, self.cards = [], [], []
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        a = dict(attrs); cls = (a.get('class') or '').split()
        is_block = any(c in ('related-articles-grid', 'related-grid', 'blog-grid', 'related-cols') for c in cls)
        is_card = any(c in ('related-article-card', 'blog-card') for c in cls) and tag != 'a'
        self.stack.append({'tag': tag, 'block': is_block, 'card': is_card, 'hrefs': []})
        if tag == 'a' and a.get('href', '').startswith('/'):
            h = a['href'].split('#')[0]
            for fr in self.stack:
                if fr['block'] or fr['card']: fr['hrefs'].append(h)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                fr = self.stack.pop(i)
                del self.stack[i:]
                if fr['block']: self.blocks.append(fr['hrefs'])
                if fr['card'] and not fr['hrefs']: self.cards.append(fr)
                return

def integrity_problems(src):
    out = []
    vis = _visible(src)
    # call to action left as plain text
    for m in re.finditer(r'<p\b[^>]*>(?:\s|<strong>|<em>)*(' + CTA_START + r'\b[^<]{0,48}?)(?:</strong>|</em>|\s)*</p>', vis):
        before = vis[:m.start()]
        if before.rfind('<a ') > before.rfind('</a>'): continue          # inside a link (a card)
        if re.search(r'</a>\s*</h[2-6]>\s*$', before[-200:]): continue     # a card's description under its linked title
        if m.group(1).strip().endswith('.'): continue                    # a sentence, not a button label
        out.append(f'call to action without a link: "{m.group(1).strip()[:50]}"')
    # empty boxes
    for pat, what in ((r'<div class="alert[^"]*">\s*<div class="alert-title">([^<]*)</div>\s*</div>', 'box with only its title'),
                      (r'<div class="numbered-step-content">\s*<h4>([^<]*)</h4>\s*</div>', 'step with only its heading'),
                      (r'<div class="table-responsive">\s*()</div>', 'empty table frame'),
                      (r'<div class="weight-range-box">\s*()</div>', 'empty result box'),
                      (r'<div style="[^"]*padding[^"]*">\s*()</div>', 'padded box with nothing inside'),
                      (r'<div [^>]*>\s*<p [^>]*font-weight:\s*600[^>]*>([^<]{1,40})</p>\s*</div>', 'box with only its title')):
        for m in re.finditer(pat, vis):
            out.append(f'{what}' + (f': "{m.group(1)[:40]}"' if m.group(1) else ''))
    # cut sentences
    for bm in re.finditer(r'(?s)<(?:p|li|dd|figcaption)\b[^>]*>(.*?)</(?:p|li|dd|figcaption)>', vis):
        blk = bm.group(1); t = _text(blk)
        if not t: continue
        after_number = re.search(r'class="[^"]*(?:num|stat|value|kpi)[^"]*"[^>]*>[^<]{1,14}</(?:p|div|span)>\s*$', vis[max(0, bm.start() - 160):bm.start()])
        if re.match(r'^[a-z]', t) and len(t.split()) > 4 and not after_number and not re.match(r'^(?:e\.g\.|i\.e\.)', t):
            out.append(f'paragraph starts mid-sentence: "{t[:60]}"')
        for mm in re.finditer(r'([A-Za-z.]*)[.!?]\s+([a-z][a-z]+)\b', t):
            if mm.group(1).lower().rstrip('.') in ABBR or mm.group(2) in LOWER_OK: continue
            out.append(f'sentence starts lowercase: "...{t[max(0, mm.start() - 30):mm.end() + 20]}"')
        for mm in re.finditer(r',\s+(For|See|Use|Try|Read|Here|This|These)\s', t):
            out.append(f'sentence joined after a cut: "...{t[max(0, mm.start() - 30):mm.end() + 20]}"')
    # related blocks
    p = _Related(); p.feed(vis); p.close()
    for hrefs in p.blocks:
        for h in sorted({h for h in hrefs if hrefs.count(h) > 1}):
            out.append(f'related block links {h} twice')
    for c in p.cards:
        out.append('related card without a link')
    # cards inside a paragraph
    for m in re.finditer(r'<p>(?:(?!</p>).){0,400}?<a [^>]*class="related-article-card"', vis, re.S):
        out.append('cards inside a paragraph')
    # emoji used as icons
    txt = html.unescape(re.sub(r'<[^>]+>', ' ', vis))
    for ch in sorted(set(EMOJI.findall(txt))):
        out.append(f'emoji in visible text: U+{ord(ch):04X}')
    # inline-styled buttons and bylines
    for m in re.finditer(r'<a\b[^>]*style="([^"]*)"', vis):
        st = m.group(1).replace(' ', '').lower()
        bg = re.search(r'background(?:-color)?:([^;]+)', st); col = re.search(r'(?:^|;)color:([^;]+)', st)
        if bg and col and col.group(1) in ('white', '#fff', '#ffffff'):
            out.append('inline-styled button link (use class="cta-button")')
    if re.search(r'<p class="byline" style=', src):
        out.append('inline-styled byline (use the shared .byline)')
    # D-11: no sex-specific healthy/optimal ranges
    for pat in (r'(?i)\b(?:optimal|healthy|ideal|normal)\b[^.<]{0,30}\brange\b[^.<]{0,10}\bfor (?:wo)?men\b[^.<]{0,20}\b(?:19|20|21)\s*(?:&ndash;|–|-|to)\s*(?:24|25|26)\b',
                r'(?i)\b(?:19|20)\s*(?:&ndash;|–|-|to)\s*(?:24|25)\b\s*(?:for|in)\s*(?:wo)?men\b',
                r'(?i)\boptimal (?:bmi )?range for (?:wo)?men\b'):
        for m in re.finditer(pat, src):
            out.append(f'D-11: sex-specific BMI range "{_text(m.group(0))[:60]}"')
    # placeholders in headings
    for m in re.finditer(r'<h[1-6][^>]*>([^<]*(?:\(teaser\)|\bTODO\b|\bTBD\b|lorem ipsum)[^<]*)</h[1-6]>', src, re.I):
        out.append(f'placeholder in heading: "{m.group(1)[:50]}"')
    out.extend(residue_problems(src))
    return out

NUMBERED = re.compile(r'>\s*(Limitation|Method|Step|Example|Tip|Mistake|Phase|Part|Rule|Reason|Myth|Option)\s*#?\s*(\d{1,2})\b')

class _Outline(HTMLParser):
    """Headings in <main> and whether anything (text, table, image, form control) follows before the next one."""
    CONTENT = {'img', 'svg', 'table', 'canvas', 'iframe', 'video', 'input', 'select', 'button', 'picture'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ev, self.main, self.skip, self.head = [], 0, 0, None
    def handle_starttag(self, tag, attrs):
        if tag == 'main': self.main = 1
        if tag in ('script', 'style'): self.skip += 1
        if not self.main: return
        if re.fullmatch(r'h[1-6]', tag): self.head = [int(tag[1]), '']
        elif tag in self.CONTENT and self.head is None: self.ev.append(('c', 0, tag))
        if tag == 'section' and self.head is None: self.ev.append(('s', 0, ''))
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
        if tag == 'main': self.main = 0
        if not self.main: return
        if re.fullmatch(r'h[1-6]', tag) and self.head:
            self.ev.append(('h', self.head[0], ' '.join(self.head[1].split()))); self.head = None
        if tag == 'section': self.ev.append(('/s', 0, ''))
    def handle_data(self, data):
        if self.skip or not self.main: return
        if self.head is not None: self.head[1] += data
        elif data.strip(): self.ev.append(('c', 0, 'text'))

def residue_problems(src):
    out = []
    m = re.search(r'(?s)<main\b.*?</main>', src)
    main = re.sub(r'(?s)<script.*?</script>|<style.*?</style>', '', m.group(0) if m else src)
    vis = _visible(src)
    # numbered items must run from 1 without gaps
    nums = {}
    for mm in NUMBERED.finditer(vis):
        nums.setdefault(mm.group(1), set()).add(int(mm.group(2)))
    for k, ns in sorted(nums.items()):
        missing = [n for n in range(1, max(ns) + 1) if n not in ns]
        if missing: out.append(f'numbered "{k}" items skip {missing}')
    # captions for rows/columns in a section without a table; "the table below/above" on a page without one
    for sec in re.finditer(r'(?s)<section\b[^>]*>(.*?)</section>', vis):
        if '<table' in sec.group(1): continue
        for pm in re.finditer(r'(?s)<(p|figcaption)\b[^>]*>(.*?)</\1>', sec.group(1)):
            t = _text(pm.group(2))
            if re.match(r'^(?:Rows?|Columns?)\s+\d', t): out.append(f'caption for a table that is not there: "{t[:50]}"')
    if '<table' not in vis and re.search(r'(?i)\b(?:the|this) table (?:below|above)\b', _text(vis)):
        out.append('text refers to a table that is not on the page')
    # chart rows without a bar, empty bar tracks, empty icons
    for mm in re.finditer(r'<div class="chart-bar-h-item"[^>]*>\s*<span class="chart-bar-h-label">([^<]*)</span>\s*</div>', main):
        out.append(f'chart row without a bar: "{mm.group(1)[:30]}"')
    if re.search(r'<div class="chart-bar-h-track"[^>]*>\s*</div>', main):
        out.append('empty chart bar track')
    if re.search(r'<svg\b[^>]*>\s*</svg>', main):
        out.append('empty icon (svg with nothing inside)')
    # a heading with nothing under it
    o = _Outline(); o.feed(src); o.close()
    ev = o.ev
    for i, e in enumerate(ev):
        if e[0] != 'h': continue
        j, has = i + 1, False
        while j < len(ev):
            f = ev[j]
            if f[0] == 'c' or (f[0] == 'h' and f[1] > e[1]): has = True; break
            if f[0] in ('h', '/s'): break
            j += 1
        if not has and j < len(ev): out.append(f'heading with nothing under it: "{e[2][:50]}"')
    return out

ARROW_OR_DINGBAT = lambda c: 0x2190 <= c <= 0x21FF or 0x2700 <= c <= 0x27BF or 0x2900 <= c <= 0x297F or 0x2B00 <= c <= 0x2BFF or c >= 0x1F000
LOW_CONTRAST_TEXT = ('#3b82f6', '#60a5fa', '#93c5fd', '#22c55e', '#f59e0b', '#f97316', '#ef4444', '#06b6d4', '#8b5cf6',
                     '#94a3b8', '#e74c3c', '#4a90d9', '#9ca3af')

def js_problems(js):
    """Results-panel rules for assets/js/calculator.js (CMB-011)."""
    out = []
    for mm in re.finditer(r'&#(x[0-9a-fA-F]+|\d+);', js):
        g = mm.group(1); code = int(g[1:], 16) if g[0] in 'xX' else int(g)
        if ARROW_OR_DINGBAT(code): out.append(f'arrow, dingbat or emoji entity {mm.group(0)}')
    for ch in sorted(set(EMOJI.findall(js))):
        out.append(f'emoji: U+{ord(ch):04X}')
    for mm in re.finditer(r'(?i)(?<![-\w])color:\s*(#[0-9a-f]{6})', js):
        if mm.group(1).lower() in LOW_CONTRAST_TEXT: out.append(f'low-contrast text colour {mm.group(1)}')
    if re.search(r'(?i)(?:linear|radial|conic)-gradient', js):
        out.append('gradient in the results panel')
    return out

if __name__ == '__main__':
    bad = 0
    for f in sys.argv[1:]:
        src = open(f, encoding='utf-8').read()
        probs = js_problems(src) if f.endswith('.js') else integrity_problems(src)
        if probs:
            bad += 1; print(f'FAIL {f}')
            for x in probs: print('   -', x)
    sys.exit(1 if bad else 0)
