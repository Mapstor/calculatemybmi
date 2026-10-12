# CMB-009 DATES — D-12 visible dates removed, page dates from git history, one operator address

Built and tested in chat on 2026-10-12 against GitHub `main` `006bea3`, after CMB-008. Tools: Chromium 1194, jsdom 24, impeccable engine 0.1.14.

## What changes
1. **D-12: visible dates removed on 22 pages.**
   - **9 bylines** lose their "· Reviewed <date>" or "· Updated <date>" segment: `/average-weight/`, `/body-fat-calculator/`, `/body-fat-percentage-chart/`, `/childhood-obesity-statistics/`, `/obesity-rate-by-state/`, `/bmi-chart/`, `/blog/how-to-measure-body-fat/`, `/blog/what-is-bmi/`, `/blog/bmi-for-athletes/`.
   - **13 older guides** lose the "(Updated) February 2026 • N min read" line above the H1. The reading times were stale too: "18 min read" on `/blog/body-fat-vs-bmi/` (1,206 words) and on `/blog/bmi-tracking-guide/` (1,584 words).
   - **Kept:** provenance dates ("released September 24, 2026", "published February 2026", "Data as of: September 2026", source update dates in reference lists) and the legal pages' "Last updated" (owner, 2026-10-12).
2. **Operator address, one version everywhere.**
   - `/privacy/` section 13 said "Registered address: Maribor, Slovenia" while its own callout says "Smolnik 62, 2342 Ruse, Slovenia". It now says the latter. The policy text changed, so its "Last updated" moves to **12 October 2026** (§11 of the policy promises this).
   - The Organization schema on 10 pages had `"addressLocality": "Maribor"`. It is now `"streetAddress": "Smolnik 62"`, `"postalCode": "2342"`, `"addressLocality": "Ruse"` (DEVLOG §1). Pages: `/about/`, `/average-weight/`, `/body-fat-calculator/`, `/body-fat-percentage-chart/`, `/childhood-obesity-statistics/`, `/obesity-rate-by-state/`, `/us-obesity-statistics/`, `/blog/bmi-for-athletes/`, `/blog/how-to-measure-body-fat/`, `/blog/what-is-bmi/`.
3. **Page dates from git history** (DEVLOG §4 rule, made exact):
   - schema `dateModified` = the last commit that changed the visible text inside `<main>`;
   - `sitemap.xml` lastmod = the last commit that changed that text, its links or the JSON-LD.
   - JSON-LD date fields and visible review dates don't count, so this batch's date removal moves nothing.
   - Dataset objects keep their own `dateModified`, which tracks the data.
   - **20 pages were wrong**, e.g. `/blog/bmi-formula/` said 2026-08-12 but its content last changed 2026-09-30; `/about/` said 2026-08-12 / lastmod 2026-08-10 but changed 2026-10-08.
   - Then this batch's own changes: `/privacy/` text → both dates 2026-10-12; the 10 address pages → lastmod 2026-10-12.
4. **Gate:** `scripts/check_structure.py` now fails any page whose byline shows a review/update date or whose source shows "N min read". The pre-CMB-009 state scores 18/40.
5. **New tools, `research/dates/`:**
   - `date_truth.py` compares every page's dates with the history; exit 0 = all agree.
   - `dates_cmb009.json` holds the history dates used here.
   - `patch_cmb009.py` is this batch's build record.

**Chat results**
- **Gates:** check_structure 40/40; verify, schema and number audit clean; markup clean on all 41 pages.
- **Visible-text diff:** the only visible changes are the 22 removed date strings and the two privacy edits.
- **Date check:** after a test commit, `date_truth.py` reports 40/40 ok; the pre-CMB-009 state reports 20 wrong.
- **Browser and calculator checks:** jsdom 77/77; FAQ 25/25; menu 41/41; no page wider than the screen at 360, 390 or 1280 px.
- **Detector:** impeccable detect on the 26 changed pages 379 → 379, no page worse.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's DEVLOG step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-009-dates/`.
0.3 `git log --oneline -6 | grep -c "CMB-008"` → 1 or more. If 0, STOP: CMB-008 must run first.

### 1. Dry run
`python3 research/cmb-009-dates/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 3 new files, 28 replaced files, 0 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-009-dates/apply_build.py`
Must print exactly: `applied: 3 new files, 28 replaced files, 0 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → first line `check_structure: 40/40 pages pass`.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `for f in $(git diff --name-only HEAD -- '*.html'); do python3 scripts/check_markup.py $f >/dev/null || echo "MARKUP FAIL $f"; done` → no output.
3.7 Each prints the number shown:
- `grep -o "min read" index.html */index.html blog/*/index.html | wc -l` → `0`
- `grep -o "&middot; Reviewed\|&middot; Updated" index.html */index.html blog/*/index.html | wc -l` → `0`
- `grep -o "Last updated 12 October 2026" privacy/index.html | wc -l` → `1`
- `grep -o "Last Updated: October 11, 2026" terms/index.html | wc -l` → `1`
3.8 Each prints the number shown:
- `grep -o "Registered address: Smolnik 62, 2342 Ruse, Slovenia" privacy/index.html | wc -l` → `1`
- `grep -l '"addressLocality": "Maribor"' index.html */index.html blog/*/index.html | wc -l` → `0`
- `grep -l '"streetAddress": "Smolnik 62"' index.html */index.html blog/*/index.html | wc -l` → `10`
3.9 Browser, jsdom and detector checks: the box has none (DEVLOG §4) → record as skipped. Chat's results are under "What changes".

### 4. Commit
```
git add -A
git commit -m "fix: D-12 visible dates removed, page dates from git history, operator address consistent (CMB-009)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb009-dates.txt; echo $?; grep -c '^ok' /tmp/cmb009-dates.txt; rm /tmp/cmb009-dates.txt` → `0` and `40`.
- This holds when the commit date is 2026-10-12.
- On a later day, the 11 pages this batch changes (`/privacy/` and the 10 address pages) report BAD by the day difference. Record the output; don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 7. REPORT
```
REPORT CMB-009 DATES
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-008 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <line> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <output or none> | 3.7 <n> <n> <n> <n> | 3.8 <n> <n> <n> | 3.9 skipped (no browser/jsdom in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
