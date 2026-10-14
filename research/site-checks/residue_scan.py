"""Residue scan (CMB-011): after a bulk deletion, find the text that sat right after (or right before) each deleted
block, still exists at HEAD, and reads as if it refers back to what was deleted ("This paradox...", "these
differences", "Rows 18-64...", a list intro ending in ":"). The structural gate in scripts/check_content_integrity.py
catches numbering gaps, captions without a table, empty chart rows and empty headings; this scan finds the rest.
usage (repo root): python3 research/site-checks/residue_scan.py . COMMIT [COMMIT ...]
Review every hit by reading the page; many are fine (a table cell, an FAQ question)."""
import re, html, sys, subprocess, difflib
repo = sys.argv[1]; commits = sys.argv[2:]
def git(*a): return subprocess.run(['git','-C',repo]+list(a), capture_output=True, text=True).stdout
BLOCK = r'</?(?:p|div|h[1-6]|li|ul|ol|table|tr|td|th|section|figure|figcaption|caption|thead|tbody|blockquote|details|summary|button|span class="[^"]*(?:title|label)[^"]*")\b[^>]*>'
def blocks(s):
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', s, flags=re.S)
    m = re.search(r'<main\b.*?</main>', s, re.S); s = m.group(0) if m else s
    out = []
    for p in re.split(BLOCK, s):
        t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', p))).strip()
        if t: out.append(t)
    return out
ANA = re.compile(r'^(this|these|that|those|such|it|they|both|either|neither|also|additionally|notably|however|moreover|furthermore|in addition|as (shown|seen|noted|listed)|the (above|following|table|chart|graph|list)|rows?\b|columns?\b|\*|note:|source:|for (example|instance)|similarly|likewise|meanwhile|despite|instead|otherwise|thus|therefore|hence|which|where|and\b|but\b|or\b|[a-z])', re.I)
REF = re.compile(r'\b(table|chart|graph|list|rows?|columns?|figure|example|method|step) (above|below)\b|\b(above|below) (table|chart|list|figure)\b|\bthe (table|chart|list) (shows|above|below)\b|\b(method|step|example|option) [2-9]\b|\bthis (paradox|table|chart|list|difference|pattern|data|section)\b|\bthese (differences|classifications|figures|numbers|values|ranges|categories|findings|methods|guidelines|recommendations|data)\b', re.I)
seen = set()
for c in commits:
    files = [f for f in git('show','--name-only','--format=',c).split() if f.endswith('.html')]
    for f in files:
        try: head = blocks(open(f'{repo}/{f}').read())
        except FileNotFoundError: continue
        hs = set(head)
        a = blocks(git('show', f'{c}^:{f}')); b = blocks(git('show', f'{c}:{f}'))
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag not in ('delete', 'replace'): continue
            dl = sum(len(x) for x in a[i1:i2]); al = sum(len(x) for x in b[j1:j2])
            if dl < 40 or al > dl * 0.6: continue          # real deletions only
            after = b[j2] if j2 < len(b) else ''
            before = b[j1-1] if j1 > 0 else ''
            flags = []
            if after in hs and (ANA.match(after) or REF.search(after)): flags.append('AFTER')
            if before in hs and before.endswith(':') and after in hs: flags.append('BEFORE:')
            if before in hs and REF.search(before): flags.append('BEFORE-REF')
            if not flags: continue
            key = (f, after[:80], before[-80:])
            if key in seen: continue
            seen.add(key)
            print(f'== {c} {f} {flags}')
            print(f'   DELETED: {" | ".join(a[i1:i2])[:200]}')
            print(f'   BEFORE : {before[-200:]}')
            print(f'   AFTER  : {after[:240]}')
