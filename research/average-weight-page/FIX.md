# Batch A1 — new page /average-weight/ (calculatemybmi)
Prepared in chat, 3 Oct 2026 on a copy of the live commit 1a120fd. Tested there: check_structure 37/37, research/f1/verify.py clean, number audit clean, ledger check OK, registry check: no violation for this page, tool test 6/6 in a simulated browser (jsdom; shipped for reference), renders checked at 390 px and 1280 px.

What it adds:
- /average-weight/ — our weighted calculation from CDC NHANES August 2021-August 2023 exam files (DEMO_L + BMX_L; adults 20+, pregnant women excluded, MEC exam weights, Taylor-linearised standard errors, cells with fewer than 30 people suppressed). Method verified: reproduces NCHS Series 3 No. 50 exactly (men 199.0 lb, women 171.8 lb; height 68.9 / 63.5 in; BMI 29.4 / 30.0).
- Compare tool (sex, height, optional weight; ft/lb or cm/kg): average, median and middle half for that height, healthy range (site BMI rule), your BMI and your percentile among people within an inch of your height.
- Height tables for women (4'9"-5'9") and men (5'2"-6'3") with anchored rows, 95% ranges, middle half, healthy range, BMI at average and sample size; age table (weight, waist, BMI); average-vs-healthy chart; FAQ (no FAQPage markup); methodology; CSV; Article + Dataset + BreadcrumbList schema; OG image.
- Inbound links: /bmi-chart/ (FAQ answer, visible + its structured data kept identical), /ideal-weight/.
- sitemap.xml entry; research/: page-map (built), new verified registry row nhanes-2021-2023-exam-files, HANDOFF, scripts + results + the two raw NHANES files for reruns.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/average-weight-page/`. Anything else: STOP and report.
1. `python3 research/average-weight-page/apply_build.py --dry-run` — must print `DRY RUN — applied: 9 new files, 2 replaced files, 5 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/average-weight-page/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `37/37 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c "/average-weight/" sitemap.xml bmi-chart/index.html ideal-weight/index.html` → each `:1`
4. Commit: `git add average-weight/ research/ sitemap.xml bmi-chart/index.html ideal-weight/index.html`; `git status --porcelain` must be empty; then
   `git commit -m "feat: /average-weight/ — NHANES 2021-2023 average weight by height and age (verified vs NCHS Series 3), compare tool, tables, chart, CSV; inbound links"`
5. REPORT — print exactly this, nothing after it:
```
REPORT average-weight-page
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <lines>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -22>
final status: <git status --porcelain, or "clean">
```
