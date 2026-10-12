#!/usr/bin/env python3
"""Structure gate for calculatemybmi.
Runs before every commit. Requires all 33 sitemap pages to pass:
  - exactly one <head>, </head>, <body, and </body>
  - <link rel="stylesheet" href="/assets/css/styles.css"> present
  - <title>, meta description, canonical, exactly one <h1>
  - shared <header class="header"> containing a nav link to /bmi-chart/ labelled "BMI Chart"
  - <footer> present
  - Raptive/AdThrive head tag present exactly once
  - HTML parses (best-effort tag balance + libxml if available)
  - exactly one click binding for FAQ accordions and for the mobile-menu toggle
    (two bindings cancel out: one tap opens and closes; CMB-005)
  - FAQPage JSON-LD answers match the visible FAQ answers word for word (CMB-005)
  - weight-by-height tables list whole-unit weights inside each category, in lb and kg (CMB-008)
Exits non-zero on any failure.
"""
import re, os, glob, sys, json, html
from html.parser import HTMLParser

def sitemap_pages(root='/workspace'):
    sm = os.path.join(root, 'sitemap.xml')
    urls = re.findall(r'<loc>([^<]+)</loc>', open(sm).read())
    files = []
    for u in urls:
        path = u.replace('https://calculatemybmi.net', '')
        if path.endswith('/'):
            f = os.path.join(root, path.strip('/'), 'index.html')
        else:
            f = os.path.join(root, path.strip('/'))
        files.append((path, f))
    return files

_CALC_INIT = None
def calc_init_calls(fn, root='/workspace'):
    """1 if assets/js/calculator.js init() still calls fn(), else 0."""
    global _CALC_INIT
    if _CALC_INIT is None:
        try:
            calc = open(os.path.join(root, 'assets/js/calculator.js')).read()
            m = re.search(r'function init\(\) \{(.*?)\n\}', calc, re.S)
            _CALC_INIT = m.group(1) if m else ''
        except OSError:
            _CALC_INIT = ''
    return 1 if re.search(r'^\s*' + fn + r'\(\);', _CALC_INIT, re.M) else 0

def click_bindings(src, selector, calc_fn, attr_class):
    n = sum(1 for m in re.finditer(r'<script(?: [^>]*)?>([\s\S]*?)</script>', src)
            if ("'" + selector + "'") in m.group(1) and 'addEventListener' in m.group(1))
    n += 1 if re.search(r'class="' + attr_class + r'"[^>]*onclick=', src) else 0
    n += calc_init_calls(calc_fn) if 'assets/js/calculator.js' in src else 0
    return n

class _FAQText(HTMLParser):
    """(question, answer) text pairs from .faq-question buttons and .faq-answer divs, as textContent."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pairs, self.mode, self.depth, self.buf, self.q, self.skip = [], None, 0, [], None, 0
    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get('class') or '').split()
        if self.mode is None:
            if tag == 'button' and 'faq-question' in cls: self.mode, self.buf = 'q', []
            elif tag == 'div' and 'faq-answer' in cls: self.mode, self.buf, self.depth = 'a', [], 1
            return
        if tag in ('svg', 'script', 'style'): self.skip += 1
        if self.mode == 'a' and tag == 'div': self.depth += 1
    def handle_endtag(self, tag):
        if self.mode is None: return
        if tag in ('svg', 'script', 'style') and self.skip: self.skip -= 1; return
        if self.mode == 'q' and tag == 'button':
            self.q, self.mode = ''.join(self.buf), None
        elif self.mode == 'a' and tag == 'div':
            self.depth -= 1
            if self.depth == 0: self.pairs.append((self.q, ''.join(self.buf))); self.mode = None
    def handle_data(self, data):
        if self.mode and not self.skip: self.buf.append(data)

def _squash(t):
    t = html.unescape(t or '')
    for a, b in (('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'), ('\u201d', '"')): t = t.replace(a, b)
    return re.sub(r'\s+', '', t)

def faq_schema_drift(src):
    """Problems where a FAQPage JSON-LD answer is not the visible answer to the same question."""
    qs = []
    for blk in re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', src):
        try: data = json.loads(blk)
        except Exception: continue
        st = [data]
        while st:
            x = st.pop()
            if isinstance(x, dict):
                if x.get('@type') == 'Question': qs.append(x)
                st.extend(x.values())
            elif isinstance(x, list): st.extend(x)
    if not qs: return []
    p = _FAQText(); p.feed(src); p.close()
    vis = {_squash(q): _squash(a) for q, a in p.pairs}
    out = []
    for qd in qs:
        name = qd.get('name', '')
        a = vis.get(_squash(name))
        if a is None: out.append(f'FAQ schema question not shown: "{name[:60]}"')
        elif a != _squash((qd.get('acceptedAnswer') or {}).get('text', '')):
            out.append(f'FAQ schema answer differs from the page: "{name[:60]}"')
    return out

def check_file(page, path):
    problems = []
    if not os.path.exists(path):
        return ['file missing']
    src = open(path).read()
    if src.count('<head>') != 1: problems.append(f'<head> count != 1 ({src.count("<head>")})')
    if src.count('</head>') != 1: problems.append(f'</head> count != 1 ({src.count("</head>")})')
    if src.count('<body') < 1 or src.count('<body') > 1: problems.append(f'<body count = {src.count("<body")}')
    if src.count('</body>') != 1: problems.append(f'</body> count != 1 ({src.count("</body>")})')
    if 'href="/assets/css/styles.css"' not in src: problems.append('styles.css not linked')
    # Count <title> only outside <svg> blocks (SVG <title> is legit a11y and doesn't count as HTML title).
    src_no_svg = re.sub(r'<svg[\s\S]*?</svg>', '', src)
    title_count = src_no_svg.count('<title>')
    if title_count != 1: problems.append(f'<title> count (outside SVG) != 1 ({title_count})')
    if '<meta name="description"' not in src: problems.append('no meta description')
    if 'rel="canonical"' not in src: problems.append('no canonical')
    h1_count = len(re.findall(r'<h1[\s>]', src))
    if h1_count != 1: problems.append(f'H1 count != 1 ({h1_count})')
    if '<header class="header">' not in src: problems.append('no shared header')
    else:
        header_block = re.search(r'<header class="header">[\s\S]*?</header>', src)
        if header_block and '<a href="/bmi-chart/">BMI Chart</a>' not in header_block.group(0):
            problems.append('shared header missing BMI Chart nav link')
    if '<footer' not in src: problems.append('no footer')
    rap_count = src.count('Raptive Head Tag Manual')
    if rap_count != 1: problems.append(f'Raptive tag count != 1 ({rap_count})')

    # Content gates: zero secondary-source mentions in body text or as links.
    secondary_hosts = ['health.harvard.edu','mayoclinic.org','my.clevelandclinic.org','clevelandclinic.org',
                        'nhs.uk','heart.org','americanheart.org','acefitness.org','acsm.org','nsca.com','wikipedia.org']
    secondary_brands = ['Harvard','Mayo Clinic','Cleveland Clinic',
                         'NHS','National Health Service',
                         'American Heart Association','American Council on Exercise',
                         'American College of Sports Medicine','ACSM','NSCA','Wikipedia']
    # Links to secondary domains
    for host in secondary_hosts:
        n = len(re.findall(r'href="https?://(?:www\.)?' + re.escape(host), src))
        if n:
            problems.append(f'link to secondary domain {host} ({n})')
    # Body-text brand mentions (strip tags, scripts, styles first)
    src_notag = re.sub(r'<script[\s\S]*?</script>', '', src)
    src_notag = re.sub(r'<style[\s\S]*?</style>', '', src_notag)
    src_notag = re.sub(r'<[^>]+>', ' ', src_notag)
    import html
    src_notag = html.unescape(src_notag)
    for brand in secondary_brands:
        n = src_notag.count(brand)
        if n:
            problems.append(f'body-text brand mention "{brand}" ({n})')
    # One click binding per toggle: a second binding closes what the first opened.
    if 'class="faq-question"' in src:
        n = click_bindings(src, '.faq-question', 'setupFAQ', 'faq-question')
        if n != 1: problems.append(f'FAQ accordion has {n} click bindings (need exactly 1)')
    if 'class="nav-toggle"' in src:
        n = click_bindings(src, '.nav-toggle', 'setupMobileNav', 'nav-toggle')
        if n != 1: problems.append(f'mobile menu toggle has {n} click bindings (need exactly 1)')
    # Schema must match visible content: FAQPage answers are the visible answers.
    problems.extend(faq_schema_drift(src))
    # Tag-balance check — delegates to scripts/check_markup.py's parser.
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        from check_markup import MarkupChecker
        parser = MarkupChecker(src)
        try:
            parser.feed(src)
            parser.close()
        except Exception as exc:
            problems.append(f'markup parse error: {exc}')
        for off, kind, detail in parser.issues:
            problems.append(f'markup @{off} [{kind}] {detail}')
    except Exception as exc:
        problems.append(f'check_markup import failed: {exc}')
    # Weight-by-height tables: each listed weight sits inside its category at that exact height, per unit (CMB-008).
    try:
        from check_weight_tables import table_problems
        problems.extend(f'weight table: {p}' for p in table_problems(src))
    except Exception as exc:
        problems.append(f'check_weight_tables import failed: {exc}')
    return problems

def main():
    pages = sitemap_pages()
    ok = 0; fails = []
    for page, path in pages:
        probs = check_file(page, path)
        if probs:
            fails.append((page, probs))
        else:
            ok += 1
    print(f'check_structure: {ok}/{len(pages)} pages pass')
    for page, probs in fails:
        print(f'  FAIL {page}:')
        for p in probs: print(f'    - {p}')
    return 0 if not fails else 1

if __name__ == '__main__':
    sys.exit(main())
