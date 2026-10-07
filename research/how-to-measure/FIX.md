# Batch G1 — new guide /blog/how-to-measure-body-fat/ (calculatemybmi)
Prepared in chat, 7 Oct 2026 on a copy of the box state after N1 (commit 4b93338). Tested there: check_structure 40/40, research/f1/verify.py clean, number audit clean, ledger check OK, registry check: no violation for this page, body-fat calculator test 18/18 after its FAQ edit, chart checked for label overlaps (geometric check + renders at 390 px and 1280 px).

What it adds:
- /blog/how-to-measure-body-fat/ (primary keyword "how to calculate body fat percentage", 18,100/mo): every method scored against DXA using one study that tested seven methods on the same 437 people (Burns, Fu & Constantino, PLOS ONE 2019): underwater weighing 1.0, skinfolds 1.4, Bod Pod 1.6, 4-electrode lab analyzer 1.6, hand-held impedance 4.9 points from DXA; foot-to-foot scale and near-infrared not equivalent; MAPE 11.7-21.9%. Plus the Deurenberg BMI formula (SEE 4.1), the DoD tape method (conference abstract, limits of agreement wider than +-3.5) and CDC's DXA notes. Comparison chart (labels never crossed by the cut-off line) and table, lab vs home method cards, the study's pre-test routine, FAQ (no FAQPage markup), sources, Article + BreadcrumbList schema, OG image.
- Links in: /body-fat-calculator/ FAQ (page + its generator), /blog/body-fat-vs-bmi/, /blog/ index card.
- sitemap.xml entry; research/: page-map (built), registry row body-fat-method-validation (verified), HANDOFF (body-fat cluster complete).

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/how-to-measure/`. Anything else: STOP and report.
1. `python3 research/how-to-measure/apply_build.py --dry-run` — must print `DRY RUN — applied: 3 new files, 3 replaced files, 5 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/how-to-measure/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c "/blog/how-to-measure-body-fat/" sitemap.xml blog/index.html body-fat-calculator/index.html blog/body-fat-vs-bmi/index.html` → each `:1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "feat: /blog/how-to-measure-body-fat/ — methods scored against DXA (Burns et al. PLOS ONE 2019), comparison chart + table; inbound links"`
5. REPORT — print exactly this, nothing after it:
```
REPORT how-to-measure
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <lines>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -16>
final status: <git status --porcelain, or "clean">
```
