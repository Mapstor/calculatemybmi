#!/usr/bin/env python3
"""number_audit.py — every number in the visible text of the built page must be in allowed_numbers.txt.
Usage (repo root): python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html"""
import re, sys, html, os
p=sys.argv[1]; s=open(p,encoding="utf-8").read()
m=re.search(r'<article class="cmb-stats">.*?</article>',s,re.S)
if not m: print("FAIL: <article class=\"cmb-stats\"> not found"); sys.exit(1)
v=m.group(0)
for pat in (r'<script.*?</script>',r'<svg.*?</svg>',r'<!--.*?-->',r'<textarea.*?</textarea>'): v=re.sub(pat,' ',v,flags=re.S)
text=html.unescape(re.sub(r'<[^>]+>',' ',v))
nums=set(re.findall(r'(?<![\w.,])\d{1,3}(?:,\d{3})+(?![\d])|(?<![\w.,])\d+(?:\.\d+)?(?![\d])',text))
allowed=set(open(os.path.join(os.path.dirname(__file__),"allowed_numbers.txt")).read().split())
bad=sorted(n for n in nums if n not in allowed)
print(f"numbers found: {len(nums)}; not allowed: {bad if bad else 'none'}")
sys.exit(1 if bad else 0)
