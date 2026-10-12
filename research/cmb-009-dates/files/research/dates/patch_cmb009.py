#!/usr/bin/env python3
"""CMB-009 DATES (D-12) + operator address consistency. usage: patch_cmb009.py REPO_ROOT DAY  (build record: ran once in chat on the state after CMB-008, DAY 2026-10-12)
1. D-12: remove visible review/update dates from bylines (9 pages) and the "<Month YYYY> • N min read" line
   above the H1 of 13 older guides (the reading times were stale too: e.g. 18 min for 1,206 words).
   Provenance dates stay (survey periods, "released", "published", "retrieved", "Data as of", source update dates).
   Legal pages keep "Last updated" (owner, 2026-10-12).
2. Operator address: /privacy/ section 13 said "Registered address: Maribor, Slovenia" next to the callout's
   "Smolnik 62, 2342 Ruse, Slovenia"; the Organization schema on 10 pages said addressLocality "Maribor".
   All now Smolnik 62, 2342 Ruse (DEVLOG §1). Privacy text changed -> its "Last updated" moves to DAY.
3. Dates: schema dateModified = the last visible main-content change; sitemap lastmod = the last significant
   change (visible main content, structured data or links) — from git history (dates_cmb009.json), then this
   batch's own significant changes (privacy text: both; address schema: lastmod). Removing a visible date is
   not a content change and moves nothing.
4. check_structure: bylines carry no date and no page shows "N min read" (D-12 gate)."""
import sys, os, re, json
root, DAY = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
MONTH = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'

def rd(p): return open(os.path.join(root, p), encoding='utf-8', newline='').read()
def wr(p, s): open(os.path.join(root, p), 'w', encoding='utf-8', newline='').write(s)
done = {}

# ---- 1a. the 13 older guides: meta line above the H1 ----
GUIDES = ['bmi-and-health-risks', 'bmi-and-metabolism', 'bmi-categories', 'bmi-chart-explained', 'bmi-formula',
          'bmi-history', 'bmi-limitations', 'bmi-tracking-guide', 'body-fat-vs-bmi', 'healthy-bmi-range',
          'how-to-lower-bmi', 'underweight-bmi-risks', 'waist-to-height-ratio']
META = re.compile(r'<p style="font-size: 0\.8125rem; color: var\(--gray-500\);">(?:Updated )?February 2026 (?:•|&bull;) \d+ min read</p> ?')
for g in GUIDES:
    f = f'blog/{g}/index.html'; s = rd(f)
    s2, n = META.subn('', s); assert n == 1, (f, n); wr(f, s2); done[f] = 'meta line'

# ---- 1b. bylines: drop the "· Reviewed <date>" / "· Updated <date>" segment ----
BYLINE_PAGES = ['average-weight', 'body-fat-calculator', 'body-fat-percentage-chart', 'childhood-obesity-statistics',
                'obesity-rate-by-state', 'bmi-chart', 'blog/how-to-measure-body-fat', 'blog/what-is-bmi', 'blog/bmi-for-athletes']
SEG = re.compile(rf' &middot; (?:Reviewed|Updated) (?:\d{{1,2}} )?{MONTH}(?: \d{{1,2}},)? \d{{4}}')
for p in BYLINE_PAGES:
    f = f'{p}/index.html'; s = rd(f)
    m = re.search(r'(?s)<p class="byline"[^>]*>.*?</p>', s); assert m, f
    by, n = SEG.subn('', m.group(0)); assert n == 1, (f, n)
    s = s[:m.start()] + by + s[m.end():]; wr(f, s); done[f] = 'byline'

# ---- 2. operator address ----
s = rd('privacy/index.html')
for a, b in (('Registered address: Maribor, Slovenia', 'Registered address: Smolnik 62, 2342 Ruse, Slovenia'),
             ('Last updated 25 September 2026', 'Last updated ' + str(int(DAY[8:])) + ' October 2026')):
    assert s.count(a) == 1, a; s = s.replace(a, b)
assert DAY[5:7] == '10'
wr('privacy/index.html', s)
ADDR = re.compile(r'(\s*)"addressLocality":\s*"Maribor"')
ADDR_PAGES = ['about', 'average-weight', 'body-fat-calculator', 'body-fat-percentage-chart', 'childhood-obesity-statistics',
              'obesity-rate-by-state', 'us-obesity-statistics', 'blog/bmi-for-athletes', 'blog/how-to-measure-body-fat', 'blog/what-is-bmi']
for p in ADDR_PAGES:
    f = f'{p}/index.html'; s = rd(f)
    s2, n = ADDR.subn(lambda m: f'{m.group(1)}"streetAddress": "Smolnik 62",{m.group(1)}"postalCode": "2342",{m.group(1)}"addressLocality": "Ruse"', s)
    assert n == 1, (f, n); wr(f, s2)


def object_spans(text):
    """(start, end, obj) for every JSON object in text that parses on its own"""
    spans, stack, i, ins, esc = [], [], 0, False, False
    while i < len(text):
        c = text[i]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        elif c == '"': ins = True
        elif c == '{': stack.append(i)
        elif c == '}' and stack:
            a = stack.pop()
            try: spans.append((a, i + 1, json.loads(text[a:i + 1])))
            except Exception: pass
        i += 1
    return spans

def set_date_modified(page, day):
    """dateModified of every non-Dataset schema object that carries one -> day (Dataset dates track the data)"""
    olds = []
    def fix_block(m):
        blk = m.group(2); edits = []
        for a, b, obj in object_spans(blk):
            if isinstance(obj, dict) and 'dateModified' in obj and obj.get('@type') != 'Dataset':
                inner = [(x, y) for x, y, o in object_spans(blk[a + 1:b - 1]) if isinstance(o, dict) and 'dateModified' in o]
                sub = blk[a:b]
                mm = None
                for mt in re.finditer(r'("dateModified":\s?")([0-9-]+)(")', sub):
                    if not any(x + 1 <= mt.start() < y + 1 for x, y in inner): mm = mt; break
                if mm and mm.group(2) != day:
                    olds.append(mm.group(2)); edits.append((a + mm.start(2), a + mm.end(2)))
        for x, y in sorted(edits, reverse=True): blk = blk[:x] + day + blk[y:]
        return m.group(1) + blk + m.group(3)
    out = re.sub(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', fix_block, page)
    return out, olds


# ---- 3. dates ----
truth = json.load(open(os.path.join(here, 'dates_cmb009.json')))   # path -> {"visible": d, "significant": d}
batch_visible = {'/privacy/'}
batch_significant = {'/privacy/'} | {f'/{p}/' for p in ADDR_PAGES}
sm = rd('sitemap.xml'); changed = []
for path, t in sorted(truth.items()):
    vis = max(t['visible'], DAY) if path in batch_visible else t['visible']
    sig = max(t['significant'], DAY) if path in batch_significant else t['significant']
    f = (path.strip('/') + '/index.html') if path != '/' else 'index.html'
    s = rd(f); s2, olds = set_date_modified(s, vis)
    if s2 != s:
        wr(f, s2); changed.append((path, 'dateModified', ','.join(olds), vis))
    loc = f'<loc>https://calculatemybmi.net{path}</loc><lastmod>'
    m = re.search(re.escape(loc) + r'([0-9-]+)</lastmod>', sm); assert m, path
    if m.group(1) != sig:
        sm = sm.replace(m.group(0), loc + sig + '</lastmod>'); changed.append((path, 'lastmod', m.group(1), sig))
wr('sitemap.xml', sm)

# ---- 4. D-12 gate in check_structure ----
cs = rd('scripts/check_structure.py')
a = "  - weight-by-height tables list whole-unit weights inside each category, in lb and kg (CMB-008)\n"
b = a + "  - no visible review/update date in bylines and no \"N min read\" line (D-12, CMB-009)\n"
assert cs.count(a) == 1; cs = cs.replace(a, b)
a = "    # Weight-by-height tables: each listed weight sits inside its category at that exact height, per unit (CMB-008).\n"
b = ("    # D-12: no visible review/update date in bylines, no reading-time line (legal pages keep \"Last updated\").\n"
     "    for by in re.findall(r'(?s)<p class=\"byline\"[^>]*>(.*?)</p>', src):\n"
     "        if re.search(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \\d{1,2},)? \\d{4}|\\b\\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \\d{4}', by) and re.search(r'Reviewed|Updated', by):\n"
     "            problems.append('byline shows a review/update date (D-12)')\n"
     "    if re.search(r'\\b\\d+ min read\\b', re.sub(r'(?s)<script.*?</script>', '', src)):\n"
     "        problems.append('page shows an \"N min read\" line (D-12)')\n" + a)
assert cs.count(a) == 1; cs = cs.replace(a, b); wr('scripts/check_structure.py', cs)

print(json.dumps({'visible-date removals': len(done), 'date changes': changed}, indent=1))
