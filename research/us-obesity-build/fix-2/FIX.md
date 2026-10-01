# FIX-2 — calculatemybmi follow-up to commit 1f16af7
Prepared in chat, 30 Sep 2026. 103 exact edits across 37 files, tested on a fresh copy of the 1f16af7 archive: check_structure 34/34, number audit clean, widget 14/14, JSON-LD and inline JS parse on every page, 0 broken internal links.

What it changes:
- /us-obesity-statistics/: visible breadcrumb; the trend chart's CSS classes collided with the 100-adults figure (lines drew as filled shapes); the widget showed both unit rows; tables overflowed at phone width; source-list numbers were clipped.
- Nav on all 35 pages: the desktop nav gains "BMI Chart"; the duplicate "BMI Chart" in the mobile nav becomes "Obesity Statistics"; "Guides" is no longer marked current on non-blog pages.
- 8 new contextual links to /us-obesity-statistics/: home, /bmi-chart/, /calculators/, men, women and kids calculators, /blog/bmi-categories/, /blog/bmi-chart-explained/.
- Stale figures replaced with NHANES 2021–2023 values and primary-source links: men calculator (chart + average-BMI FAQ, including its FAQPage JSON-LD), kids calculator (2017–2020 figures), /blog/bmi-chart-explained/ (unsourced men/women chart + orphan footnote), /calculators/ (42%).
- research/HANDOFF.md: corrects the wrong "31.7% misattributed" note; logs the dead "Cookie settings" footer text as open.

## Rules
Do not edit any file by hand. Only apply_fixes.py changes files, plus the `git rm` in step 5. No network. Do not push. Run everything from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: `?? research/us-obesity-build/fix-2/`, and `PRE-DEPLOY-REPORT.md` either as ` D` or not listed. Anything else: STOP and report the list.
1. `python3 research/us-obesity-build/fix-2/apply_fixes.py --dry-run` — must print `DRY RUN — applied 103 edits to 37 files`. If it prints `ABORT`, STOP and report its full output. Do not attempt manual edits.
2. `python3 research/us-obesity-build/fix-2/apply_fixes.py`
3. Gates — all must pass. On any FAIL, STOP before committing and report.
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `node research/us-obesity-build/tools/widget_test.js us-obesity-statistics/index.html` → `WIDGET: ALL PASS`
   3.4 Sitewide verification — must print `json/js failures: none | broken links: none | content inbound: 9 | nav anomalies: none | stale left: none`:
```
python3 - <<'PY'
import re,json,glob,os,subprocess
files=[p for p in glob.glob("**/*.html",recursive=True) if not p.startswith("research/") and "google" not in p]
bad=[];broken=set();inbound=[];navbad=[]
for p in files:
    s=open(p,encoding="utf-8").read()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
        try: json.loads(b)
        except Exception: bad.append((p,"json"))
    for m in re.finditer(r'<script(\s[^>]*)?>(.*?)</script>',s,re.S):
        a=m.group(1) or ""
        if "src=" in a or "ld+json" in a or not m.group(2).strip(): continue
        open("/tmp/j.js","w").write(m.group(2))
        if subprocess.run(["node","--check","/tmp/j.js"],capture_output=True).returncode: bad.append((p,"js"))
    for h in set(re.findall(r'href="(/[^"#?]*)(?:#[^"]*)?"',s)):
        q=h.strip("/"); ok=os.path.exists("index.html") if h=="/" else (os.path.exists(os.path.join(q,"index.html")) if h.endswith("/") else os.path.exists(q))
        if not ok: broken.add((p,h))
    hd=re.search(r'<header.*?</header>',s,re.S); body=s.replace(hd.group(0),"") if hd else s
    if p!="us-obesity-statistics/index.html" and "/us-obesity-statistics/" in body: inbound.append(p)
    if hd:
        h=hd.group(0)
        if h.count('href="/bmi-chart/"')!=2 or h.count('href="/us-obesity-statistics/"')!=1: navbad.append(p)
        if not p.startswith("blog/") and re.search(r'<a href="/blog/" class="active"',h): navbad.append(p+" guides")
pat=re.compile(r'(19\.7%|14\.7 million|22\.2%|20\.7%|12\.7%|Approximately 42%|approximately 29\.1|43% of American men|Men - Obese|Women - Obese)')
left=[(p,m.group(0)) for p in files for m in pat.finditer(open(p,encoding="utf-8").read())]
print("json/js failures:",bad or "none","| broken links:",sorted(broken) or "none","| content inbound:",len(inbound),"| nav anomalies:",navbad or "none","| stale left:",left or "none")
PY
```
4. Commit A. Stage exactly the modified tracked files plus the package: `git add $(git diff --name-only --diff-filter=M) research/us-obesity-build/fix-2/`. Run `git status --porcelain`: the only line allowed to remain is ` D PRE-DEPLOY-REPORT.md`. Then commit:
   `git commit -m "fix: /us-obesity-statistics/ render bugs, sitewide nav, 9 inbound links, stale prevalence figures -> NHANES 2021-2023, handoff correction"`
5. Commit B: `git rm -q PRE-DEPLOY-REPORT.md` (works whether the file is deleted or restored in the working tree), then
   `git commit -m "chore: remove stale Phase 17 PRE-DEPLOY-REPORT.md (kept in history at 688001a)"`.
   If git says the file isn't tracked, skip this commit and report it.
6. REPORT — print exactly this, nothing after it:
```
REPORT fix-2
0 status: <lines from step 0>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4-5 commits: <git log --oneline -3>
stat A: <git show --stat HEAD~1 | tail -40>
final status: <git status --porcelain, or "clean">
```
