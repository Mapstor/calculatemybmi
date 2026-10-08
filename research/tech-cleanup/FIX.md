# Batch T1 — technical cleanup (calculatemybmi)
Prepared in chat, 7 Oct 2026 on a copy of the box state after W1 (commit fe05b91). Tested there: check_structure 40/40, research/f1/verify.py clean, number audit clean, schema check (every page except the homepage has BreadcrumbList; every WebApplication has an author), athletes chart labels checked mathematically, renders at 390 px and 1280 px.

What changes:
- Structured data: BreadcrumbList added to /blog/, /contact/, /privacy/, /terms/; author (Person, Marko Visic, about page @id) added to the WebApplication schema of the homepage and 7 calculator pages.
- /blog/bmi-for-athletes/ rebuilt (same URL; was 745 words with a broken sentence and an unsourced claim): NFL Combine (Provencher 2018: 53.4% BMI 30+ vs 8.9% obesity by measured body fat), college-football DXA study (Clin J Sport Med 2012: BMI 25 = 11.1% vs 19.9% fat; BMI 30 = 20.2% vs 27.3%), our NHANES DXA overlap (leanest tenth of men with BMI 25-29.9 under 21.7% fat; healthy-BMI median 22.1%), better measures, FAQ, sources; new data-true share image; blog index card text updated (it described a scatter plot the page no longer has); sitemap lastmod 2026-10-07.
- Deleted 9 files that nothing references (checked across all site HTML/CSS/JS/XML/JSON/TXT): 5 old share images, the old athletes scatter share image, logo.svg, two unused favicon PNGs.
- research/: HANDOFF note, athletes generator + data, schema checker.

## Rules
Do not edit any file by hand: only apply_build.py writes or deletes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/tech-cleanup/`. Anything else: STOP and report.
1. `python3 research/tech-cleanup/apply_build.py --dry-run` — must print `DRY RUN — applied: 4 new files, 1 replaced files, 15 edits, 9 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/tech-cleanup/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "chore(seo): breadcrumbs on 4 pages, author on calculator schema, remove 9 unreferenced assets; rebuild /blog/bmi-for-athletes/ with sources"`
5. REPORT — print exactly this, nothing after it:
```
REPORT tech-cleanup
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -8>
final status: <git status --porcelain, or "clean">
```
