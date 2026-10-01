# Batch C2b-1 — unsourced numbers, round 1 (calculatemybmi)
Prepared in chat, 1 Oct 2026. 20 exact edits across 7 files, tested on a copy of HEAD 661d60c: check_structure 34/34, number audit clean, JSON-LD and inline JS parse on every page, 0 dead anchors, FAQ schema parity intact.

Every number kept now carries a primary source checked in chat; numbers without one are removed or made qualitative:
- /blog/bmi-and-metabolism/: invented "metabolic rate by decade" (-3% to -25%) and "BMR by BMI" (1,450-2,400 cal) charts removed; the "2-3% per decade" claim replaced with Pontzer et al., Science 2021 (stable 20-60, declines after); metabolic syndrome "1 in 3" (Hirode & Wong, JAMA 2020), "5x diabetes" and "2x cardiovascular" (Alberti et al., Circulation 2009) now sourced; the unsourced "80%" box, BMR/energy-share percentages, the 6-vs-2 calorie claim and the training-frequency instruction removed.
- Sarcopenia "3-8% per decade after 30" cited to Volpi et al. 2004 on metabolism, bmi-limitations and ideal-weight (ideal-weight also said 3-5%; now consistent, including its FAQ structured data).
- /blog/how-to-lower-bmi/: plate-size claim removed; sleep box kept only for the sourced 55% (Cappuccio et al., Sleep 2008).
- /blog/bmi-chart-explained/: 5-10% weight-loss line cited (Wing et al., 2011).
- Homepage: "weight loss >5% in 6 months" (no source) made qualitative.

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/c2b1/`. Anything else: STOP and report.
1. `python3 research/c2b1/apply_fixes.py --dry-run` — must print `DRY RUN — applied 20 edits to 7 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/c2b1/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `python3 research/c2b1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/c2b1/`; `git status --porcelain` must be empty; then
   `git commit -m "fix(content): C2b-1 unsourced numbers round 1 (metabolism charts/claims, sarcopenia, sleep, 5-10%, homepage threshold) with verified primary sources"`
5. REPORT — print exactly this, nothing after it:
```
REPORT c2b1
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -14>
final status: <git status --porcelain, or "clean">
```
