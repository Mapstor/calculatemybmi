# Batch G2d — /age-bmi-calculator/ rewrite (calculatemybmi). Apply after G2c.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2c (6a71e7e). Tested there: check_structure 40/40, research/f1/verify.py clean, number audit clean, calculator checks 36/36, 40-page audit (no script errors, menu opens everywhere), 64 calculator runs, phone renders checked (no table overflows).

What changes on /age-bmi-calculator/ (the calculator is untouched):
- Removed unsourced/prescriptive sections: "How body composition changes with age" (bone/estrogen claims, "1-3 inches", "metabolic rate slows", HRT), "BMI by decade" (protein 0.8-1.0 g/lb targets, HIIT claims, "addressing it now is easier"), "Practical strategies" (diet/habit advice, "gender-specific BMI ranges"), and FAQ answers with unsourced figures ("BMR -1-2% per decade", "weight loss not recommended over 65 unless BMI >30").
- New, data-driven content: average BMI, weight and waist by age for US women and men (NHANES 2021-2023, our verified calculation that reproduces NCHS Series 3), obesity by age (NCHS Data Brief 508), what changes with age (CDC cut-offs; Volpi muscle loss; body fat by age from our DXA analysis; height arithmetic), official activity and sleep guidance (PAG; AASM/SRS via CDC). The sourced Flegal 2013 / Winter 2014 section and the health-conditions paragraph are kept; the standard-range table cells are shortened for phones.
- FAQ: 6 sourced answers; the FAQPage markup is removed (questions rewritten).
- Title/description target the page's keywords ("bmi calculator kg with age", "bmi calculator by age", "bmi age gender calculator"): "BMI Calculator by Age & Gender (kg or lbs): US Averages".
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/age-rewrite/`. Anything else: STOP and report.
1. `python3 research/age-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/age-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "Women: average BMI, weight and waist by age\|Men: average BMI, weight and waist by age" age-bmi-calculator/index.html | wc -l` → `2`
   3.4 `grep -o "0.8-1.0 g\|HIIT\|Hormone replacement\|1-2% per decade\|gender-specific BMI ranges" age-bmi-calculator/index.html | wc -l` → `0`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(age): NHANES averages by age, sourced changes-with-age, remove unsourced advice, sourced FAQ, kg/lbs title"`
5. REPORT — print exactly this, nothing after it:
```
REPORT age-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
