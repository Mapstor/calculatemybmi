# Batch C2b-2 — unsourced numbers, round 2 (calculatemybmi)
Prepared in chat, 1 Oct 2026. 18 exact edits across 8 files, tested on a copy of HEAD 121c65c: check_structure 34/34, number audit clean, JSON-LD and inline JS parse on every page, 0 dead anchors, FAQ schema parity intact.

- /blog/body-fat-vs-bmi/: "healthy body fat by age" chart (exact values not verifiable against the primary) replaced by a sourced statement (Gallagher et al., Am J Clin Nutr 2000: no accepted ranges; provisional ranges proposed).
- /women-bmi-calculator/: "6-11% more body fat" and "25% vs 18% at BMI 22" made qualitative, sourced to CDC NCHS.
- /men-bmi-calculator/: unsourced "low testosterone at high BMI" card (2.4x claim, broken "discussed in detail by.") and testosterone FAQ (visible + JSON-LD) removed; unsourced "misclassifies up to 25%" sentence removed.
- /blog/bmi-history/ and /blog/bmi-categories/: "29 million reclassified", "40% to 55%" and the before/after chart removed; 55% kept on bmi-history, now sourced to the NHLBI 1998 Evidence Report (NHANES III: 32.6% overweight + 22.3% obesity).
- /lean-body-mass/: prescriptive "how to increase lean mass" FAQ removed (visible + JSON-LD); Boer-accuracy FAQ without unsourced numbers (visible + JSON-LD).
- /blog/bmi-for-athletes/: wrong muscle-vs-fat volume chart and an empty "LeBron James" heading removed. (The page itself is thin; rebuild proposed separately.)

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/c2b2/`. Anything else: STOP and report.
1. `python3 research/c2b2/apply_fixes.py --dry-run` — must print `DRY RUN — applied 18 edits to 8 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/c2b2/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `python3 research/c2b2/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/c2b2/`; `git status --porcelain` must be empty; then
   `git commit -m "fix(content): C2b-2 unsourced numbers round 2 (body-fat ranges, women/men claims, 1998 history, lean FAQs, athletes chart) with verified primary sources"`
5. REPORT — print exactly this, nothing after it:
```
REPORT c2b2
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -14>
final status: <git status --porcelain, or "clean">
```
