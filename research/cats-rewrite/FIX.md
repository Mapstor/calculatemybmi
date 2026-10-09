# Batch G2f — /blog/bmi-categories/ corrections (calculatemybmi). Apply after G2e.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2e (74862e2). Tested there: check_structure 40/40, research/f1/verify.py clean (FAQ structured data valid and synced), number audit clean, 40-page audit (no script errors, menu opens everywhere), phone render (no overflow).

What changes on /blog/bmi-categories/:
- Attribution fixed: the 1995 expert report and the 2000 technical report are WHO's, not CDC's (CDC uses the same cut-offs); the thinness grades come from 1995, the obesity classes from 2000.
- The eight unsourced "Health Risks" lists (incl. "5-8 years" and "8-14 years" of lost life expectancy) replaced by short sourced paragraphs: WHO thinness grades with "see a doctor", NHLBI clinical-guideline risks for overweight/obesity, IARC cancers via our health-risks page, Flegal et al. JAMA 2013 hazard ratios (overweight 0.94; BMI 35+ 1.29).
- Removed: invented sex-specific "optimal" ranges (men 20-25, women 19-24) and the unsourced "lowest mortality at 22-23"; "single most common category" replaced by the sourced figure (31.7% of US adults, NCHS Health E-Stat 111); speculative overweight-paradox explanation; "Japan, China…" cut-off claim; "far more dangerous" visceral fat; "overestimates risk in Black populations"; "what is concerning at 25 may be fine at 65"; Olympic-sprinter claim (NFL example now sourced to Provencher 2018); "ensure adequate protein"; 5-10% weight loss now cites Wing 2011.
- Broken text fixed: "Theobesity topic page…"; two source entries with stripped names removed; WHO fact sheet linked.
- FAQ structured data synced to the visible answers; dateModified + "Updated October 2026".
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/cats-rewrite/`. Anything else: STOP and report.
1. `python3 research/cats-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/cats-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "8–14 years\|5–8 years\|Olympic sprinters\|Theobesity\|single most common\|perfectly fine at 65" blog/bmi-categories/index.html | wc -l` → `0`
   3.4 `grep -o "hazard ratio 1.29" blog/bmi-categories/index.html | wc -l` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(categories): WHO attribution, sourced risk paragraphs (NHLBI, Flegal), remove invented ranges and figures, fix broken text"`
5. REPORT — print exactly this, nothing after it:
```
REPORT cats-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
