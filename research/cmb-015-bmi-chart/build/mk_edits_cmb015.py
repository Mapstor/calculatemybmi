#!/usr/bin/env python3
"""CMB-015 edits (chat side): builds edits.json for apply_build.py from the tree as it stands at 621bf8b.
  - robots meta max-image-preview:large on every sitemap page except /bmi-chart/ (gen_bc.py writes that page);
  - the preferred image (16:9 og:image / twitter:image, og:image:height 675, JSON-LD image [1:1, 4:3, 16:9] on the
    main entity and a WebPage primaryImageOfPage) on /, /blog/healthy-bmi-range/ and /blog/bmi-chart-women/, and the
    Article author and publisher named on the two guides (head and
    JSON-LD only: no visible text changes, so their schema dateModified stays; their sitemap lastmod moves, since the
    date rule counts JSON-LD);
  - sitemap.xml: the image namespace, <image:image> for every <img> in a page's <main> (/about/, /blog/bmi-chart-women/,
    /bmi-chart/), lastmod {TODAY} for /, /blog/healthy-bmi-range/, /blog/bmi-chart-women/ and /bmi-chart/.
usage: mk_edits_cmb015.py TREE OUT_JSON"""
import sys, re, json, subprocess

T, OUT = sys.argv[1], sys.argv[2]
SITE = 'https://calculatemybmi.net'
def head(f): return subprocess.run(['git', '-C', T, 'show', f'HEAD:{f}'], capture_output=True, text=True, check=True).stdout
assert subprocess.run(['git', '-C', T, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip() == '621bf8b'
E = []
def edit(f, old, new, label, src=None):
    s = src if src is not None else head(f)
    n = s.count(old)
    assert n == 1, (label, n)
    E.append({'file': f, 'old': old, 'new': new, 'count': 1, 'label': label})

VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
ROBOTS = '<meta name="robots" content="max-image-preview:large">'
sm = head('sitemap.xml')
pages = [u.replace(SITE, '') for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
assert len(pages) == 40
for p in pages:
    f = 'index.html' if p == '/' else p.strip('/') + '/index.html'
    if p == '/bmi-chart/': continue
    s = head(f)
    assert 'name="robots"' not in s
    edit(f, VIEWPORT, VIEWPORT + ROBOTS, f'robots max-image-preview:large: {p}', s)

def pref(name): return {r: f'{SITE}/assets/images/preferred/{name}-{r}.png' for r in ('1x1', '4x3', '16x9')}
def img_list(u): return f'["{u["1x1"]}", "{u["4x3"]}", "{u["16x9"]}"]'
def webpage(url, u, extra=''):
    return (f'{{"@type": "WebPage", "@id": "{url}", "url": "{url}"{extra}, "primaryImageOfPage": {{"@type": "ImageObject", '
            f'"url": "{u["16x9"]}", "width": 1200, "height": 675}}}}')
def og_edits(f, old_og, u):
    s = head(f)
    edit(f, f'<meta property="og:image" content="{old_og}">', f'<meta property="og:image" content="{u["16x9"]}">', f'og:image: {f}', s)
    edit(f, '<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', f'og:image:height: {f}', s)
    edit(f, f'<meta name="twitter:image" content="{old_og}">', f'<meta name="twitter:image" content="{u["16x9"]}">', f'twitter:image: {f}', s)

# Homepage: the calculator (WebApplication) is the main entity; a WebPage node names it and the preferred image.
f = 'index.html'; u = pref('bmi-calculator'); s = head(f)
og_edits(f, f'{SITE}/assets/images/og/home-bmi-us-adults.png', u)
edit(f, '{"@type": "WebApplication", "@id": "https://calculatemybmi.net/#calculator", ',
     '{"@type": "WebApplication", "@id": "https://calculatemybmi.net/#calculator", "image": ' + img_list(u) + ', ',
     'JSON-LD WebApplication image: /', s)
edit(f, '"@graph": [{"@type": "WebSite", ',
     '"@graph": [' + webpage(SITE + '/', u, ', "isPartOf": {"@id": "https://calculatemybmi.net/#website"}, '
                             '"mainEntity": {"@id": "https://calculatemybmi.net/#calculator"}').replace(
         '"@id": "https://calculatemybmi.net/", "url"', '"@id": "https://calculatemybmi.net/#webpage", "url"') + ', {"@type": "WebSite", ',
     'JSON-LD WebPage primaryImageOfPage: /', s)

# Healthy-range guide: Article image and mainEntityOfPage.
f = 'blog/healthy-bmi-range/index.html'; u = pref('healthy-bmi-range'); s = head(f); url = SITE + '/blog/healthy-bmi-range/'
og_edits(f, f'{SITE}/assets/images/og/healthy-bmi-range-risk.png', u)
edit(f, f'"image": "{SITE}/assets/images/og/healthy-bmi-range-risk.png"', f'"image": {img_list(u)}', f'JSON-LD Article image: {f}', s)
edit(f, f'"mainEntityOfPage": "{url}"}}', f'"mainEntityOfPage": {webpage(url, u)}}}', f'JSON-LD mainEntityOfPage: {f}', s)

# Women's chart: Article image (the printable chart stays an <img> and an image-sitemap entry) and mainEntityOfPage.
f = 'blog/bmi-chart-women/index.html'; u = pref('bmi-chart-women'); s = head(f); url = SITE + '/blog/bmi-chart-women/'
og_edits(f, f'{SITE}/assets/images/og/bmi-chart-women.png', u)
edit(f, f'"image": ["{SITE}/assets/images/og/bmi-chart-women.png", "{SITE}/assets/images/charts/bmi-chart-women.png"]}}',
     f'"image": {img_list(u)}, "mainEntityOfPage": {webpage(url, u)}}}', f'JSON-LD Article image + mainEntityOfPage: {f}', s)

# Article author and publisher named on the page (Google reads each page on its own; an @id alone names nobody).
AUTH = '"@id": "https://calculatemybmi.net/about/#author-bio", "name": "Marko Visic", "url": "https://calculatemybmi.net/about/"}'
PUB = '"@id": "https://calculatemybmi.net/#organization", "name": "CalculateMyBMI", "url": "https://calculatemybmi.net/"}'
f = 'blog/healthy-bmi-range/index.html'; s = head(f)
edit(f, '"author": {"@type": "Person", "@id": "https://calculatemybmi.net/about/#author-bio"}', '"author": {"@type": "Person", ' + AUTH,
     f'JSON-LD Article author name: {f}', s)
edit(f, '"publisher": {"@type": "Organization", "@id": "https://calculatemybmi.net/#organization"}',
     '"publisher": {"@type": "Organization", ' + PUB, f'JSON-LD Article publisher name: {f}', s)
f = 'blog/bmi-chart-women/index.html'; s = head(f)
edit(f, '"author": {"@id": "https://calculatemybmi.net/about/#author-bio"}', '"author": {"@type": "Person", ' + AUTH,
     f'JSON-LD Article author name: {f}', s)
edit(f, '"publisher": {"@id": "https://calculatemybmi.net/#organization"}', '"publisher": {"@type": "Organization", ' + PUB,
     f'JSON-LD Article publisher name: {f}', s)

# Sitemap: namespace, image entries, lastmod for the four pages whose text or JSON-LD changes.
f = 'sitemap.xml'
edit(f, '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
     'sitemap image namespace', sm)
def entry(p):
    m = re.search(r'<url><loc>' + re.escape(SITE + p) + r'</loc><lastmod>(\d{4}-\d\d-\d\d)</lastmod><priority>([\d.]+)</priority></url>', sm)
    assert m, p
    return m.group(0), m.group(1), m.group(2)
def img_tag(path): return f'<image:image><image:loc>{SITE}{path}</image:loc></image:image>'
for p, newdate, images in (('/', True, []), ('/about/', False, ['/assets/images/marko-visic.jpg']),
                           ('/blog/healthy-bmi-range/', True, []),
                           ('/blog/bmi-chart-women/', True, ['/assets/images/charts/bmi-chart-women.png']),
                           ('/bmi-chart/', True, ['/assets/images/charts/bmi-chart.png'])):
    old, d, pr = entry(p)
    new = (f'<url><loc>{SITE}{p}</loc><lastmod>{"{TODAY}" if newdate else d}</lastmod><priority>{pr}</priority>'
           + ''.join(img_tag(i) for i in images) + '</url>')
    edit(f, old, new, f'sitemap {p}' + (' lastmod' if newdate else '') + (' + image' if images else ''), sm)

json.dump(E, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(E), 'edits:', sum(e['label'].startswith('robots') for e in E), 'robots,',
      sum(e['file'] == 'sitemap.xml' for e in E), 'sitemap,', sum('image' in e['label'] and e['file'] != 'sitemap.xml' and not e['label'].startswith('robots') for e in E), 'image/JSON-LD')
