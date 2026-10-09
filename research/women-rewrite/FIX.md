# Batch G2h — /women-bmi-calculator/ corrections (calculatemybmi). Apply after G2g.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2g (661c24c). Tested there: check_structure 40/40, research/f1/verify.py clean (FAQ structured data valid and synced), number audit clean, calculator checks 36/36, 40-page audit (no script errors, menu opens everywhere), phone render (no overflow).

What changes on /women-bmi-calculator/ (the calculator is untouched):
- New "US women by the numbers" section: average height, weight, BMI (30.0) and obesity (41.3%), body fat (38.7%), and a table of average BMI, weight and waist by age (our verified NHANES 2021-2023 calculation; Data Brief 508; our DXA analysis).
- Replaced unsourced figures with sourced ones: "BMI 22 = about 25% body fat in women vs 18% in men" -> CDC-scan medians at a healthy BMI (women 33.4%, men 22.1%); ACE "essential fat 10-13%, healthy 21-31%" -> Gallagher 2000 provisional range (21-32.9% at 20-39) and CDC-scan averages; menstrual "2-6 lbs" and menopause "5-10 pounds" removed; menopause waist now uses our NHANES data (women's waist largest at 50-59); 65+ "BMI below 22" -> 23 per Winter 2014.
- Waist: NHLBI cited for the risk statements; the measuring step now follows the NIH method (tape just above the hip bones) to match the NIH cut-off used on the page; "more metabolically dangerous" and the 38-vs-30-inch example replaced.
- Removed unsourced claims: "supports hormone production", "gynoid fat lowers cardiovascular risk", "pre-pregnancy BMI is one of the strongest predictors", "resistance training is the actionable lever after 65"; NIH guideline description corrected (BMI + waist + risk factors).
- FAQ: four answers rewritten with sources; "How does birth control affect BMI?" and "Does BMI affect fertility?" removed (unsourced; also removed from the FAQ structured data).
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/women-rewrite/`. Anything else: STOP and report.
1. `python3 research/women-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/women-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "2-6 lbs\|10-13%\|21-31%\|about 25% body fat\|birth control" women-bmi-calculator/index.html | wc -l` → `0`
   3.4 `grep -o "US women by the numbers" women-bmi-calculator/index.html | wc -l` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(women): US women data section, CDC-scan and Gallagher figures replace ACE/unsourced numbers, NIH waist method, sourced FAQ"`
5. REPORT — print exactly this, nothing after it:
```
REPORT women-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
