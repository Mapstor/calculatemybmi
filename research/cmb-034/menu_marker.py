#!/usr/bin/env python3
"""CMB-034: one rule for the menu's current-page marker on every sitemap page (DEVLOG §5 menu marker).
A header link to the page itself carries class "active" and aria-current="page" (desktop menu, dropdown and mobile
menu alike; never the logo). A page the menu doesn't link marks its section instead, with class "active" and aria-current="true":
/blog/ guides mark Guides, /obesity-rate-by-state/ and /childhood-obesity-statistics/ mark Obesity Statistics; any
other page (the legal pages, /average-weight/, /body-fat-percentage-chart/) marks nothing. Only the <header> changes,
so no page date moves (§4). usage: python3 research/cmb-034/menu_marker.py [--check]   (--check changes nothing and
exits 1 if a page breaks the rule)"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SECTION = {'/obesity-rate-by-state/': '/us-obesity-statistics/', '/childhood-obesity-statistics/': '/us-obesity-statistics/'}


def pages():
    xml = (REPO / 'sitemap.xml').read_text(encoding='utf-8')
    return [re.sub(r'^https?://[^/]+', '', u) or '/' for u in re.findall(r'<loc>\s*([^<\s]+)', xml) if '/assets/' not in u]


def target(pg, links):
    if pg in links:
        return pg, 'page'
    if pg.startswith('/blog/') and pg != '/blog/':
        return '/blog/', 'true'
    if pg in SECTION:
        return SECTION[pg], 'true'
    return None, None


def mark(tag, on, kind):
    if 'class="logo' in tag:          # the logo links home on every page; it never carries the marker
        on = False
    t = re.sub(r' aria-current="(?:page|true)"', '', tag)
    m = re.search(r' class="([^"]*)"', t)
    classes = [c for c in (m.group(1).split() if m else []) if c != 'active']
    if on:
        classes.append('active')
    attr = f' class="{" ".join(classes)}"' if classes else ''
    t = re.sub(r' class="[^"]*"', '', t)
    t = t[:-1] + attr + (f' aria-current="{kind}"' if on else '') + '>'
    return t


bad = 0
for pg in pages():
    f = REPO / ('index.html' if pg == '/' else pg.strip('/') + '/index.html')
    src = f.read_text(encoding='utf-8')
    hs, he = src.index('<header'), src.index('</header>')
    head = src[hs:he]
    links = set(re.findall(r'<a href="([^"]+)"', head))
    href, kind = target(pg, links)
    new = re.sub(r'<a href="([^"]+)"[^>]*>', lambda m: mark(m.group(0), m.group(1) == href, kind), head)
    if '--check' in sys.argv:
        if new != head:
            bad += 1
            print('menu marker off rule:', pg)
        continue
    if new != head:
        f.write_text(src[:hs] + new + src[he:], encoding='utf-8')
        print('marked', pg, '->', href, kind)
sys.exit(1 if bad else 0)
