# Batch A2 — /average-weight/ redesign: beautiful inputs, rich results, clean charts (calculatemybmi)
Prepared in chat, 4 Oct 2026 on a copy of the live commit 3abb342. Tested there: check_structure 37/37, research/f1/verify.py clean, number audit clean, tool test 16/16 in a simulated browser (incl. a label-collision sweep across 31 weights), renders checked at 390 px and 1280 px.

What changes (same URL, same verified data):
- Form: pill toggles (woman/man, ft·lb / cm·kg), big height readout with slider and − / + steppers, weight field with unit suffix, styled age select, full-width button.
- Results: chips, four tiles (average at your height, your rank at that height or typical range, your BMI or healthy range, your height rank among US adults of your sex), smoothed weight distribution for your height with the healthy band, average and your weight (labels stacked so they never overlap, sized to the screen), side-by-side bars (you, average at your height, your age group, all US adults of your sex, top of healthy range), BMI gauge with value badge and names below the track, plain-English notes.
- Page chart: women and men as two separate small charts (titles and key outside the plot, nothing drawn over the data).
- Data: height percentiles by sex added to the results (same NHANES files). Reviewed date and dateModified 4 Oct; sitemap lastmod 2026-10-04.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/average-weight-v2/`. Anything else: STOP and report.
1. `python3 research/average-weight-v2/apply_build.py --dry-run` — must print `DRY RUN — applied: 2 new files, 3 replaced files, 2 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/average-weight-v2/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `37/37 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -c 'id="aw-h"' average-weight/index.html` → `1`
4. Commit: `git add average-weight/index.html research/ sitemap.xml`; `git status --porcelain` must be empty; then
   `git commit -m "feat(average-weight): redesigned compare tool (inputs, rich results, distribution chart, BMI gauge, height rank) + small-multiple charts"`
5. REPORT — print exactly this, nothing after it:
```
REPORT average-weight-v2
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -12>
final status: <git status --porcelain, or "clean">
```
