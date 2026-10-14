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
    return out

if __name__ == '__main__':
    bad = 0
    for f in sys.argv[1:]:
        probs = integrity_problems(open(f, encoding='utf-8').read())
        if probs:
            bad += 1; print(f'FAIL {f}')
            for x in probs: print('   -', x)
    sys.exit(1 if bad else 0)
