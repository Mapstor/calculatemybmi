# Batch C2b-3 — last unsourced numbers, first prescriptive targets, handoff rewrite (calculatemybmi)
Prepared in chat, 1 Oct 2026. 17 exact edits across 10 files, tested on a copy of HEAD 8d61f91: check_structure 34/34, number audit clean, JSON-LD and inline JS parse on every page, 0 dead anchors, FAQ schema parity intact.

- Sourced: WHO child figures on /kids-bmi-calculator/ (updated to the current fact sheet: 35 million under-5s overweight in 2024; 390 million aged 5-19 in 2022, incl. 160 million with obesity); Hamwi frame-size ±10% on /ideal-weight/ (Pai & Paloucek, 2000); sarcopenia on /lean-body-mass/ (Volpi et al., 2004; visible + FAQ JSON-LD, unsourced "30-40% by 80" removed); athletes NFL claims replaced with Provencher et al., J Strength Cond Res 2018 (obesity 53.4% by BMI vs 8.9% by measured body fat) and the misattributed "NIH database" line removed.
- Removed: unsourced "30-35% more muscle" and "15-20% body fat at BMI 20-25" (/blog/healthy-bmi-range/, now CDC NCHS-sourced wording); the women's 75/25 vs 82/18 body-composition chart.
- Prescriptive targets removed (first set): calorie surplus/deficit and kcal floors (/blog/healthy-bmi-range/, /blog/how-to-lower-bmi/ step + checklist + SMART example), weekly loss-rate and training frequency (/blog/bmi-and-metabolism/, /blog/underweight-bmi-risks/). The rest (about 9 pages incl. FAQ JSON-LD) is batch C2b-4.
- research/HANDOFF.md rewritten as one current document.

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/c2b3/`. Anything else: STOP and report.
1. `python3 research/c2b3/apply_fixes.py --dry-run` — must print `DRY RUN — applied 17 edits to 10 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/c2b3/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `python3 research/c2b3/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/c2b3/`; `git status --porcelain` must be empty; then
   `git commit -m "fix(content): C2b-3 last unsourced numbers (WHO, frame size, sarcopenia, NFL study), first prescriptive targets removed, HANDOFF rewritten"`
5. REPORT — print exactly this, nothing after it:
```
REPORT c2b3
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -16>
final status: <git status --porcelain, or "clean">
```
