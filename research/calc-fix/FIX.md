# Batch K1 — calculator fixes from the phone test (calculatemybmi)
Prepared in chat, 7 Oct 2026 on a copy of the box state after T1 (commit 8819105). Tested there: check_structure 40/40, research/f1/verify.py clean, calculator checks 36/36 in a simulated browser (homepage metric + imperial results, 6'0" formatting, neutral status, no invented sections, mobile menu opens on all 9 calculator pages + /blog/, women/men/age/lean-body-mass calculators run with no script errors and no fitness-industry tiers).

What changes (2 site files):
- assets/js/calculator.js:
  - Mobile menu: the 9 pages that load this script also have the inline menu handler, so one tap opened and closed the menu. The duplicate binding is removed.
  - Results follow the units you entered (kg/cm first for metric, lbs/ft first for imperial): key metrics, healthy range, status line, weight bar, milestones, what-if steps (kg steps for metric), summary.
  - Height formatting: 182 cm showed 5'12"; now rounds before splitting (6'0").
  - Status is worded as a distance ("6 kg (12 lbs) above the healthy range for your height"), not an instruction.
  - Removed unsourced or invented content: the "Health Risk Assessment" levels (replaced by a link to the sourced BMI-and-health-risks guide), body-fat guesses fixed at age 30 with fitness-industry tiers and "women/men-specific ideal BMI" on the women/men calculators (replaced by NIH waist cut-offs + links), those tiers and unsourced FFMI labels on the lean body mass calculator (replaced by a link to the CDC-data body fat chart), unsourced life-stage/menstrual/waist claims, ponderal index "normal 11-15", age-band notes that contradicted the site's metabolism page. Summary text rewritten without unsourced health claims.
- assets/css/styles.css: space above Key Takeaways (was flush against the Calculate button); result tables scroll sideways on phones instead of being cut off.
- research/: HANDOFF note; calculator test kept in research/calculator-checks/ for reference (needs jsdom, so not run in the box).

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/calc-fix/`. Anything else: STOP and report.
1. `python3 research/calc-fix/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/calc-fix/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `node --check assets/js/calculator.js && echo "calculator.js syntax OK"` → `calculator.js syntax OK`
   3.4 `grep -c "setupMobileNav();\|Essential Fat\|Health Risk Assessment" assets/js/calculator.js` → `0`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "fix(calculator): mobile menu double-binding, results in the user's units, 6'0\" height format, neutral status, remove invented risk levels and fitness-industry tiers, spacing"`
5. REPORT — print exactly this, nothing after it:
```
REPORT calc-fix
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -8>
final status: <git status --porcelain, or "clean">
```
