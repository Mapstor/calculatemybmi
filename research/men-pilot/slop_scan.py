#!/usr/bin/env python3
"""Rough anti-slop scan of a page's main prose (sections, intro, takeaways, FAQ). usage: slop_scan.py FILE"""
import re, sys, html
s = open(sys.argv[1], encoding='utf-8').read()
m = s[s.index('<main'):s.index('</main>')]
m = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>', ' ', m, flags=re.S)
m = re.sub(r'<div class="calculator-card">.*?<div class="key-takeaways">', '<div class="key-takeaways">', m, flags=re.S)   # calculator UI out of scope
m = re.sub(r'<table.*?</table>', ' ', m, flags=re.S)              # data cells out of scope
m = re.sub(r'<ul class="source-list">.*?</ul>', ' ', m, flags=re.S)  # citations out of scope
m = re.sub(r'<nav.*?</nav>', ' ', m, flags=re.S)
txt = html.unescape(re.sub(r'<[^>]+>', ' ', m)); txt = re.sub(r'\s+', ' ', txt).strip()
words = len(re.findall(r"[A-Za-z0-9’'%.–-]+", txt))
pats = {
 'em dash': r'—', 'not-X-but-Y': r"\bnot (just|only|merely)\b|\bnot \w+,? but\b", 'throat-clearing': r"\b(Here'?s|Here is|It'?s worth|It is worth|It'?s important|important to note|When it comes to|Let'?s|The truth is|The bottom line)\b",
 'AI vocab': r'\b(delve|tapestry|testament|pivotal|crucial|intricate|meticulous|seamless|leverage|harness|unlock|elevate|empower|foster|garner|bolster|showcase|underscore|highlight[s]? the|interplay|realm|landscape|navigate|vibrant|game-changer|cutting-edge|a wide range of|plays a vital role|comprehensive|particularly relevant|especially useful|actionable)\b',
 'opener adverb': r'(^|[.!?] )(Additionally|Moreover|Furthermore|Notably|Importantly)\b', 'stacked hedge': r'\b(may potentially|can help to|generally tends to|can help contextualize)\b',
 'sales': r'\b(amazing|incredible|stunning|powerful|effortless|ultimate|everything you need to know|for best results|for a deeper dive|for a more accurate)\b',
 'vague authority': r'\b(experts say|studies show|research (consistently )?shows|it is widely believed|widely discussed|well-documented)\b',
 'about-the-page': r'\b(this (article|guide|page) (will|explores|covers)|in this (guide|article)|our [\w-]+ (guide|article) explores|explore our guides|learn more about)\b',
 'generic ending': r'\b(In conclusion|Overall,|Ultimately,)\b', 'double hyphen': r' -- ',
}
total = 0
for k, p in pats.items():
    hits = [mm.group(0) for mm in re.finditer(p, txt, re.I)]
    total += len(hits)
    if hits: print(f'{k}: {len(hits)} {hits[:6]}')
print(f'words {words}, tells {total}, per 1000 words {1000 * total / max(words, 1):.1f}')
