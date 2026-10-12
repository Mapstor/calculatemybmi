#!/usr/bin/env python3
"""Page dates from git history (CMB-009). usage: python3 research/dates/date_truth.py [PATH ...]
For each sitemap page (or the paths given, e.g. /blog/bmi-formula/) prints the schema dateModified and the
sitemap lastmod next to what the history says they should be (DEVLOG §4):
  - dateModified = date of the last commit that changed the visible text inside <main>;
  - lastmod      = date of the last commit that changed visible <main> text, its links or the JSON-LD
                   (JSON-LD date fields and visible review/update dates are ignored, so date-only edits move nothing).
Dataset objects keep their own dateModified (it tracks the data, not the page). Exit 1 when a page disagrees."""
import subprocess, re, html, json, sys

def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout

DATE_LINE = re.compile(r'(?:Updated |Reviewed )?(?:January|February|March|April|May|June|July|August|September|October|'
                       r'November|December)(?: \d{1,2},?)? \d{4} • \d+ min read')
BYLINE_DATE = re.compile(r' · (?:Reviewed|Updated) [^·]*\d{4}')

def parts(src):
    m = re.search(r'(?s)<main\b.*?</main>', src)
    body = m.group(0) if m else src
    lds = []
    for b in re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', src):
        try:
            s = json.dumps(json.loads(b), sort_keys=True)
        except Exception:
            s = b
        lds.append(re.sub(r'"date(Modified|Published)": "[^"]*"', '', s))
    vis = re.sub(r'(?s)<script.*?</script>|<style.*?</style>', '', body)
    links = sorted(set(re.findall(r'href="([^"#]+)', vis)))
    txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', vis))).strip()
    txt = re.sub(r'\s+', ' ', BYLINE_DATE.sub('', DATE_LINE.sub('', txt))).strip()
    return txt, links, lds

def truth(path):
    f = (path.strip('/') + '/index.html') if path != '/' else 'index.html'
    vis = sig = None
    for line in git('log', '--format=%h %ad', '--date=short', '--', f).splitlines():
        h, d = line.split()
        cur = parts(git('show', f'{h}:{f}'))
        prev_src = git('show', f'{h}~1:{f}') if git('rev-list', '--count', h).strip() != '1' else ''
        prev = parts(prev_src) if prev_src else ('', [], [])
        if vis is None and cur[0] != prev[0]: vis = d
        if sig is None and cur != prev: sig = d
        if vis and sig: break
    return f, vis, sig

if __name__ == '__main__':
    sm = open('sitemap.xml').read()
    paths = sys.argv[1:] or [re.sub(r'https://calculatemybmi\.net', '', u) for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
    bad = 0
    for p in paths:
        f, vis, sig = truth(p)
        src = open(f, encoding='utf-8').read()
        dms = []
        for b in re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', src):
            st = [json.loads(b)]
            while st:
                x = st.pop()
                if isinstance(x, dict):
                    if 'dateModified' in x and x.get('@type') != 'Dataset': dms.append(x['dateModified'])
                    st.extend(x.values())
                elif isinstance(x, list): st.extend(x)
        lm = re.search(r'<loc>https://calculatemybmi\.net' + re.escape(p) + r'</loc><lastmod>([^<]+)', sm)
        lm = lm.group(1) if lm else None
        ok = all(d == vis for d in dms) and lm == sig
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {p:36s} dateModified {','.join(dms) or '-':10s} (history {vis}) | lastmod {lm} (history {sig})")
    sys.exit(1 if bad else 0)
