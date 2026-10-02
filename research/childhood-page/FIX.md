# Batch C3 — new page /childhood-obesity-statistics/ (calculatemybmi)
Prepared in chat, 2 Oct 2026 on a copy of the live commit ebf6c30. Tested there: check_structure 36/36, research/f1/verify.py clean, number audit on /us-obesity-statistics/ clean, ledger check OK, 0 broken internal links, chart test 8/8 in a simulated browser (jsdom; shipped for reference), renders checked at 390 px and 1280 px.

What it adds:
- /childhood-obesity-statistics/ — measured CDC data (NCHS Health E-Stat 112, Tables 1-3; Health E-Stat 119 underweight; NHANES population totals for counts): KPI cards, "out of 100 kids" pictogram, interactive 1963-2023 trend chart (series chips: all / severe / overweight / boys / girls / ages 2-5, 6-11, 12-19; tap a point for value and approximate 95% range; server-rendered default for JS-off), age-by-sex bars, full tables, race table with CDC reliability flags (flagged cells not shown), definitions, kids BMI calculator call-out, honest state-data gap, FAQ (no FAQPage markup), sources, CSV, Article + Dataset + BreadcrumbList schema, OG image.
- Inbound links: /us-obesity-statistics/ childhood section ("childhood obesity in America"), /kids-bmi-calculator/ existing link "childhood obesity rate in America" now points here.
- sitemap.xml entry; research/: page-map (built), registry pages_served, HANDOFF note, generator + chart test.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/childhood-page/`. Anything else: STOP and report.
1. `python3 research/childhood-page/apply_build.py --dry-run` — must print `DRY RUN — applied: 5 new files, 2 replaced files, 4 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/childhood-page/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `36/36 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c "childhood-obesity-statistics" sitemap.xml us-obesity-statistics/index.html kids-bmi-calculator/index.html` → each `:1`
4. Commit: `git add childhood-obesity-statistics/ research/ sitemap.xml us-obesity-statistics/index.html kids-bmi-calculator/index.html`; `git status --porcelain` must be empty; then
   `git commit -m "feat: /childhood-obesity-statistics/ — NCHS 1963-2023 measured data, interactive trend chart, pictogram, age/sex/race, CSV; inbound links"`
5. REPORT — print exactly this, nothing after it:
```
REPORT childhood-page
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <lines>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -20>
final status: <git status --porcelain, or "clean">
```
