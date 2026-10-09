# Batch G2c — homepage content corrections (calculatemybmi). Apply after G2b.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2b (69879fa). Tested there: check_structure 40/40, research/f1/verify.py clean, number audit clean, calculator checks 36/36, 40-page audit (no script errors, menu opens everywhere). The calculator itself is untouched.

What changes on the homepage:
- "Health Risks by BMI Category": three long unsourced lists replaced by a short sourced summary (NHLBI clinical guidelines for overweight/obesity risks, Winter 2014 for low BMI in adults 65+, Wing 2011 for 5-10% weight loss), linking the full BMI-and-health-risks guide.
- "Learn About BMI": CDC wording ("moderately correlated"), NHLBI-linked risk and waist statements, WHO 2004 consultation instead of the unsourced Western Pacific line; the "5-10%" stat card now credits Wing et al. 2011 (was "NHLBI").
- FAQ: underweight, check frequency and "can BMI predict outcomes" answers rewritten to sourced statements; waist answer uses the NIH cut-offs; Asian cut-offs per WHO 2004; FAQ structured data synced to the visible answers.
- Metrics comparison table: unsourced superlatives softened ("gold standard", "better predictor").
- Example table: heading "BMI Classification Table" (it was a weights-by-height table) -> "Healthy weight by height: examples"; stale "top row" note replaced by the method; values verified against the site's BMI rule.
- "More Calculators": Body Fat Calculator card added.
- sitemap.xml homepage lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/home-rewrite/`. Anything else: STOP and report.
1. `python3 research/home-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/home-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "Western Pacific\|reasonably well\|Gold standard accuracy\|BMI Classification Table" index.html | wc -l` → `0`
   3.4 `grep -o 'href="/body-fat-calculator/">Body Fat Calculator</a>' index.html | wc -l` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(home): sourced health-risk summary and FAQ, CDC/NHLBI/WHO wording, example-table fixes, body fat calculator card"`
5. REPORT — print exactly this, nothing after it:
```
REPORT home-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
