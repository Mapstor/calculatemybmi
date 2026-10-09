# Batch G2i — /men-bmi-calculator/ corrections (calculatemybmi). Apply after G2h.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2h (f0b0bce). Tested there: check_structure 40/40, research/f1/verify.py clean (FAQ structured data valid and synced), number audit clean, calculator checks 36/36, 40-page audit (no script errors, menu opens everywhere), phone render (no overflow). A sitewide scan for text swallowed into HTML attributes found this page only.

What changes on /men-bmi-calculator/ (the calculator is untouched):
- Broken markup repaired: in "Why BMI can be misleading for men", two paragraphs had their opening text swallowed into a broken style attribute (`style="margin:0;font-size:0. Testosterone drives…`), so browsers showed half-sentences; both rewritten (CDC-scan body-fat medians at a healthy BMI; NFL Combine data, Provencher 2018). The empty "Testosterone's role" box removed and the next box renumbered.
- Unsourced claims replaced: visceral fat "contributing to arterial plaque", "apple shape more metabolically dangerous", sleep apnea "twice the rate of women / neck over 17 inches", "every extra pound adds 4 pounds on the knees", underweight risk list, "muscle weighs more than fat" -> NHLBI-sourced statements and our data; waist boxes no longer give instructions ("Action recommended"); WHR cut-off attributed to the WHO expert consultation (2008); "quality bioimpedance scales" replaced with a link to the body-fat method comparison.
- Broken text fixed: "See theguidance on BMI in adults", "Thelists sleep apnea…". Two medical list items (low-testosterone symptoms, "over 45 assessment") and the unsourced testosterone FAQ removed (also from the FAQ structured data).
- New "US men by the numbers" section (NHANES 2021-2023 averages by age; DXA body fat).
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/men-rewrite/`. Anything else: STOP and report.
1. `python3 research/men-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/men-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "font-size:0\. Testosterone\|font-size:0\.Athletes\|theguidance\|Thelists\|muscle weighs more\|quality bioimpedance" men-bmi-calculator/index.html | wc -l` → `0`
   3.4 `grep -o "US men by the numbers" men-bmi-calculator/index.html | wc -l` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(men): repair broken paragraphs, sourced claims, US men data section, remove unsourced testosterone content"`
5. REPORT — print exactly this, nothing after it:
```
REPORT men-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
