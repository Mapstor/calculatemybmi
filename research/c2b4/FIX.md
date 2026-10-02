# Batch C2b-4 — prescriptive targets (option B) + empty FAQs (calculatemybmi)
Prepared in chat, 2 Oct 2026. 72 exact edits across 15 files, tested on a copy of HEAD 89a8491: check_structure 34/34, number audit clean, JSON-LD and inline JS parse on every page, 0 dead anchors, FAQ schema parity intact, 0 empty FAQ answers.

Rule applied (decision B): no calorie, protein, sleep or exercise targets of our own; official guidelines kept only when attributed and linked.
- Replaced by attributed guidelines: Physical Activity Guidelines for Americans (adults 150-300 min moderate + muscle-strengthening on 2+ days; youth 60 min/day; ages 3-5 about 3 hours of active play; HHS/ODPHP) and the AASM/SRS sleep recommendation (adults 18-60: at least 7 hours; via CDC).
- Removed: site-invented calorie deficits/surpluses and kcal floors, protein-per-pound/kg targets, training-frequency/minute targets, fluid targets, weight-loss-rate targets and BMI-per-week conversions (healthy-bmi-range, how-to-lower-bmi, bmi-categories, age-bmi-calculator, bmi-and-metabolism, underweight-bmi-risks, lean-body-mass, women postpartum), plus medical advice on the age calculator (testosterone checks, supplementation, screening).
- Sourced: "about 6 vs 2 calories per pound at rest" for muscle vs fat (13 vs 4.5 kcal/kg; Wang et al., Am J Clin Nutr 2010).
- /lean-body-mass/ "How to improve your body composition" rewritten (was a training/protein program with a glued sentence fragment and an empty heading).
- FAQ items whose visible answer was empty (left by earlier cleanups) removed on 8 pages, together with their FAQPage structured-data entries; answered FAQs untouched.
- research/HANDOFF.md: standard and next list updated.

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/c2b4/`. Anything else: STOP and report.
1. `python3 research/c2b4/apply_fixes.py --dry-run` — must print `DRY RUN — applied 72 edits to 15 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/c2b4/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `python3 research/c2b4/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/c2b4/`; `git status --porcelain` must be empty; then
   `git commit -m "fix(content): C2b-4 prescriptive targets removed (official guidelines attributed), muscle-vs-fat kcal sourced, empty FAQs removed"`
5. REPORT — print exactly this, nothing after it:
```
REPORT c2b4
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -22>
final status: <git status --porcelain, or "clean">
```
