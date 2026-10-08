# Batch K3 — legacy-page fixes from the claim triage (calculatemybmi)
Prepared in chat, 8 Oct 2026 on a copy of the live state (K2 = a7f23f6). Tested there: check_structure 40/40, research/f1/verify.py clean (structured data valid on every page), number audit clean, calculator checks 36/36, 40-page audit (no script errors, menu opens everywhere), 64 calculator runs (only the known New BMI worked-example text flags).

What changes (15 files, all hash-guarded replacements):
- Myths removed sitewide: "age-adjusted ranges", "women-/men-specific ranges", "older adults may benefit from a higher BMI" (calculator cards on 8 pages, homepage, /calculators/ incl. visible FAQ, /about/, ideal weight incl. FAQ, lean body mass, New BMI, categories guide, women/men intros). Adult cut-offs are the same at every age; the 65+ evidence is cited as Winter 2014 (observational).
- Age calculator: the unsourced "Why a slightly higher BMI may be protective" / "paradox" boxes replaced by one sourced box (Winter et al., Am J Clin Nutr 2014) with the observational caveat.
- Asian cut-offs corrected (homepage, /calculators/, categories guide): WHO 2004 identified BMI 23 and 27.5 as public-health action points, not new overweight/obesity definitions; the wrong country list removed.
- Broken text fixed: stray "e>" and "Overview references:…;on BMI." and "see the's BMI overview" on the homepage, "The's healthy aging guide" (age), "the's childhood obesity page" (kids, original CDC link kept), "an two-stage" (BMI by age).
- assets/js/calculator.js: New BMI comparison box now shows the New BMI value (was an empty dash); invented "Risk Level" row removed; distances read "1 lb (0.5 kg)" instead of "1 lbs (0 kg)".
- /about/: registered address, "nine calculators". /blog/what-is-bmi/: severe obesity 9.7% (age-adjusted, matching 40.3%).
- research/HANDOFF.md: K3 note + next step (G2 rewrites).

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/legacy-fix/`. Anything else: STOP and report.
1. `python3 research/legacy-fix/apply_build.py --dry-run` — must print `DRY RUN — applied: 0 new files, 15 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/legacy-fix/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `node --check assets/js/calculator.js && echo "calculator.js syntax OK"` → `calculator.js syntax OK`
   3.4 `grep -l "Age-adjusted BMI recommendations\|women-specific ranges\|Overview references:\|27.5 is considered obese\|may benefit from a slightly higher BMI\|for age-adjusted healthy ranges" --include=index.html -r . | grep -v research | wc -l` → `0` (the term "obesity paradox" itself stays where pages explain it as an observational finding)
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "fix(content): remove age/sex-specific range myths, correct Asian cut-offs, fix broken sentences, New BMI comparison value, distance formatting"`
5. REPORT — print exactly this, nothing after it:
```
REPORT legacy-fix
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
