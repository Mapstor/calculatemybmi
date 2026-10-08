# Batch W1 — rebuild /blog/what-is-bmi/ (calculatemybmi)
Prepared in chat, 7 Oct 2026 on a copy of the box state after G1 (commit c838370). Tested there: check_structure 40/40, research/f1/verify.py clean, number audit clean, BMI explorer test 10/10 in a simulated browser, renders checked at 390 px and 1280 px.

What changes (same URL; the old page had 2,385 words and no sources at all):
- New sourced hub explainer: definition + CDC categories (answer block), live BMI explorer (height and weight sliders with steppers, ft/lb or cm/kg, BMI with category chip and scale, weight bands for underweight/healthy/overweight/obesity at your height; server-rendered default 5'9" / 170 lb so it reads without JavaScript), formula with worked examples, CDC adult categories incl. obesity classes, WHO 2004 Asian action points, children (CDC percentiles), US averages (BMI 29.4 / 30.0; 40.3% obesity, 9.4% severe), limits (our DXA data: healthy-BMI men 18.6-25.0% body fat middle half; Volpi muscle loss), how doctors use BMI (NHLBI: BMI + waist + risk factors), BMI vs body fat, FAQ (no FAQPage markup), 8 sources. Links out to every deeper BMI guide (formula, categories, healthy range, history, limitations, athletes, waist-to-height, body fat pages, calculators).
- Article schema keeps datePublished 2026-01-15, dateModified 2026-10-07; sitemap lastmod 2026-10-07; OG image.
- research/: page-map (data_source cdc-adult-bmi-categories), HANDOFF, generator + data + explorer test.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/what-is-bmi-rebuild/`. Anything else: STOP and report.
1. `python3 research/what-is-bmi-rebuild/apply_build.py --dry-run` — must print `DRY RUN — applied: 5 new files, 2 replaced files, 2 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/what-is-bmi-rebuild/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c 'id="wb-h"' blog/what-is-bmi/index.html` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "feat(what-is-bmi): rebuilt sourced explainer with live BMI explorer, CDC/NHLBI/WHO sources, links to every BMI guide"`
5. REPORT — print exactly this, nothing after it:
```
REPORT what-is-bmi
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -14>
final status: <git status --porcelain, or "clean">
```
