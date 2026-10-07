# Batch B1 — new page /body-fat-percentage-chart/ (calculatemybmi)
Prepared in chat, 4 Oct 2026 on a copy of the live commit (A2 pushed). Tested there: check_structure 38/38, research/f1/verify.py clean, number audit clean, ledger check OK, registry check: no violation for this page, tool test 13/13 in a simulated browser (incl. label-collision sweeps), renders checked at 390 px and 1280 px.

What it adds:
- /body-fat-percentage-chart/ — our calculation from CDC NHANES 2011-2018 whole-body DXA scans (DXX_G-J with DEMO and BMX; pooled weights /4; pregnant excluded; Taylor-linearised SEs). Method verified: reproduces Liu et al., BMJ 2021 Table 3 exactly (age-adjusted mean body fat 32.6 / 33.1 / 32.9 / 33.0% for the four cycles, identical n = 10,864; two subgroup values also match).
- Rank tool (same design as /average-weight/): sex, age 8-79, body fat % -> share of US adults your sex and age with more body fat, median, middle half, provisional healthy range (Gallagher 2000), smoothed distribution chart with collision-free labels, side-by-side bars, notes; 60+ handled honestly (no scan data, ranges only).
- Percentile chart by age (men/boys, women/girls), percentile tables, "what X% body fat means" rank tables (answers the "15% / 20% / 30% body fat" searches), Gallagher provisional ranges, body fat by BMI category chart, FAQ (no FAQPage markup), methodology, sources, CSV, Article + Dataset + BreadcrumbList schema, OG image.
- Inbound links: /blog/body-fat-vs-bmi/, /lean-body-mass/.
- sitemap.xml entry; research/: page-map (built), registry rows nhanes-2011-2018-dxa and gallagher-2000-bf-ranges (verified), HANDOFF, scripts + results (raw NHANES files not stored: 37 MB; re-download URLs in the registry).

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/body-fat-chart/`. Anything else: STOP and report.
1. `python3 research/body-fat-chart/apply_build.py --dry-run` — must print `DRY RUN — applied: 9 new files, 2 replaced files, 4 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/body-fat-chart/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `38/38 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c "/body-fat-percentage-chart/" sitemap.xml blog/body-fat-vs-bmi/index.html lean-body-mass/index.html` → each `:1`
4. Commit: `git add body-fat-percentage-chart/ research/ sitemap.xml blog/body-fat-vs-bmi/index.html lean-body-mass/index.html`; `git status --porcelain` must be empty; then
   `git commit -m "feat: /body-fat-percentage-chart/ — NHANES 2011-2018 DXA percentiles (verified vs BMJ 2021), rank tool, charts, X% tables, Gallagher ranges, CSV; inbound links"`
5. REPORT — print exactly this, nothing after it:
```
REPORT body-fat-chart
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <lines>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -22>
final status: <git status --porcelain, or "clean">
```
