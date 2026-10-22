#!/usr/bin/env python3
"""Image signals for Google Search (CMB-015). usage: python3 scripts/check_images.py [ROOT]
Imported by scripts/check_structure.py (image_problems, once per sitemap page); exits 1 when a page has problems.

Google chooses the picture next to a result, in Discover and in the image strip by itself. These rules give it the
best material, as Google Search Central documents it ("Google image SEO best practices": "Specify a preferred image
with metadata" and "Use HTML image elements to embed images"; the robots meta max-image-preview rule; the Article
image property):
  1. Every sitemap page allows large image previews: exactly one <meta name="robots" content="max-image-preview:large">.
  2. A page in PREFERRED names its own text-free preferred image (research/preferred-images/pref_images.py) three ways:
     og:image and twitter:image are the 16:9 file and og:image:width/height say 1200/675; a JSON-LD "image" is the
     list [1:1, 4:3, 16:9]; a WebPage's primaryImageOfPage is the 16:9 file. The files exist at 1200x1200, 1200x900
     and 1200x675. Any other page that points at /assets/images/preferred/ is held to the same rule.
  3. Every site image in an <img> inside <main> is listed for that page in sitemap.xml as <image:image>, every
     <image:loc> listed is an <img> on that page, and the file exists.
A D-14 rebuild adds its page to PREFERRED in the same batch."""
import os, re, sys, json

SITE = 'https://calculatemybmi.net'
ROBOTS = '<meta name="robots" content="max-image-preview:large">'
PREFERRED = {'/': 'bmi-calculator', '/blog/healthy-bmi-range/': 'healthy-bmi-range',
             '/blog/bmi-chart-women/': 'bmi-chart-women', '/bmi-chart/': 'bmi-chart',
             '/body-fat-percentage-chart/': 'body-fat-percentage-chart',
             '/women-bmi-calculator/': 'women-bmi-calculator'}
SIZES = {'1x1': (1200, 1200), '4x3': (1200, 900), '16x9': (1200, 675)}


def png_size(path):
    with open(path, 'rb') as f:
        head = f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR':
        return None
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def root_of(page, path):
    rel = 'index.html' if page == '/' else page.strip('/') + '/index.html'
    assert path.replace(os.sep, '/').endswith(rel), (page, path)
    return path[:len(path) - len(rel)] or '.'


def sitemap_images(root):
    """{page path: [image paths]} from sitemap.xml's <image:loc> entries."""
    sm = open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read()
    out = {}
    for block in re.findall(r'(?s)<url>(.*?)</url>', sm):
        loc = re.search(r'<loc>([^<]+)</loc>', block)
        if loc:
            out[loc.group(1).replace(SITE, '')] = [u.replace(SITE, '') for u in re.findall(r'<image:loc>([^<]+)</image:loc>', block)]
    return out, sm


def ld_nodes(src):
    nodes = []
    for b in re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', src):
        try:
            stack = [json.loads(b)]
        except ValueError:
            continue
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                nodes.append(x); stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return nodes


def meta(src, attr, name):
    return re.findall(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)">', src)


def image_problems(page, src, path):
    root = root_of(page, path)
    out = []
    # 1. large image previews
    robots = re.findall(r'<meta name="robots" content="([^"]*)">', src)
    if src.count(ROBOTS) != 1 or len(robots) != 1:
        out.append(f'needs exactly one {ROBOTS} (found {robots})')
    # 2. preferred image
    og = meta(src, 'property', 'og:image')
    name = PREFERRED.get(page)
    if name is None:
        hit = [u for u in og if '/assets/images/preferred/' in u]
        if hit:
            mm = re.search(r'/assets/images/preferred/(.+)-16x9\.png$', hit[0])
            name = mm.group(1) if mm else '?'
    if name:
        url = {r: f'{SITE}/assets/images/preferred/{name}-{r}.png' for r in SIZES}
        for r, (w, h) in SIZES.items():
            f = os.path.join(root, f'assets/images/preferred/{name}-{r}.png')
            if not os.path.exists(f): out.append(f'preferred image missing: {f}')
            elif png_size(f) != (w, h): out.append(f'preferred image {name}-{r}.png is {png_size(f)}, needs {w}x{h}')
        if og != [url['16x9']]: out.append(f'og:image should be {url["16x9"]} (found {og})')
        if meta(src, 'name', 'twitter:image') != [url['16x9']]: out.append('twitter:image should be the 16:9 preferred image')
        if meta(src, 'property', 'og:image:width') != ['1200'] or meta(src, 'property', 'og:image:height') != ['675']:
            out.append('og:image:width/height should be 1200/675')
        nodes = ld_nodes(src)
        if not any(n.get('image') == [url['1x1'], url['4x3'], url['16x9']] for n in nodes):
            out.append('no JSON-LD "image" listing the 1:1, 4:3 and 16:9 preferred images')
        def pio(n):
            v = n.get('primaryImageOfPage')
            return v.get('url') if isinstance(v, dict) else v
        if not any(n.get('@type') == 'WebPage' and pio(n) == url['16x9'] for n in nodes):
            out.append('no WebPage primaryImageOfPage naming the 16:9 preferred image')
    # 3. image sitemap = the <img> elements in <main>
    m = re.search(r'(?s)<main\b.*?</main>', src)
    imgs = sorted(set(u.replace(SITE, '') for u in re.findall(r'<img [^>]*?src="([^"]+)"', m.group(0) if m else '')
                      if u.startswith('/') or u.startswith(SITE)))
    listed, sm = sitemap_images(root)
    have = sorted(set(listed.get(page, [])))
    if imgs != have:
        out.append(f'image sitemap for {page} lists {have}, the page shows {imgs}')
    if have and 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' not in sm:
        out.append('sitemap.xml lists images without the image namespace')
    for u in imgs:
        if not os.path.exists(os.path.join(root, u.lstrip('/'))): out.append(f'image file missing: {u}')
    return out


def main(root='.'):
    sm = open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read()
    bad = 0
    for u in re.findall(r'<loc>([^<]+)</loc>', sm):
        page = u.replace(SITE, '')
        path = os.path.join(root, 'index.html' if page == '/' else page.strip('/') + '/index.html')
        probs = image_problems(page, open(path, encoding='utf-8').read(), path)
        for p in probs: print(f'{page}: {p}')
        bad += bool(probs)
    print(f'check_images: {bad} page(s) with problems')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
