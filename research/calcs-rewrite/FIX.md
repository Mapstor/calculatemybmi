# Batch G2e — /calculators/ corrections (calculatemybmi). Apply after G2d.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2d (edb2cb2). Tested there: check_structure 40/40, research/f1/verify.py clean (FAQ structured data synced and valid), 40-page audit (no script errors, menu opens everywhere), phone render (no overflow).

What changes on /calculators/:
- Last age-myth wording removed: comparison table ("WHO standard + age adjustment", "Age-adjusted healthy ranges for seniors", "focus 45+"), decision table ("age-adjusted healthy ranges — a slightly higher BMI may be protective"), "Best for: adults over 45", and the three meta descriptions that still said "age-adjusted".
- "Gender-specific guidance" wording replaced by what the women/men pages actually add (NIH waist cut-off, body fat, ACOG pregnancy ranges).
- Lean body mass card: "typical spread is under 2 kg for average bodies" was false for men; replaced with the computed spreads using the calculator's own equations (average US woman 1.6 kg, average US man 5.8 kg).
- New BMI described as a proposal not adopted by health agencies (was "corrects height bias", "fairer results"); ideal weight "clinically-backed target" -> formula-based estimates; "where most people should aim" -> CDC healthy range.
- FAQ: unsourced weigh-in advice ("few times per year", "daily weight varies 2-4 lbs") replaced; FAQ structured data synced to the visible answers.
- Decision table: Body Fat calculator row added.
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/calcs-rewrite/`. Anything else: STOP and report.
1. `python3 research/calcs-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/calcs-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o -i "age-adjusted\|gender-specific\|may be protective\|under 2&nbsp;kg" calculators/index.html | wc -l` → `0`
   3.4 `grep -o "Estimate your body fat percentage" calculators/index.html | wc -l` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(calculators): remove remaining age/gender myths, correct lean-mass spread, sourced FAQ, body fat row"`
5. REPORT — print exactly this, nothing after it:
```
REPORT calcs-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
