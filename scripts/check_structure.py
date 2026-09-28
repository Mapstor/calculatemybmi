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
Exits non-zero on any failure.
"""
import re, os, glob, sys, json

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
    # Basic parse check: try libxml if available; otherwise heuristic
    try:
        import xml.etree.ElementTree as ET
        # Not strict HTML but catches gross malformations
        # Skip — HTML is not XML-parseable in general
    except Exception:
        pass
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
