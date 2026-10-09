# Batch G2b — /ideal-weight/ corrections + rebuilt chart (calculatemybmi). Apply after G2a.
Prepared in chat, 8 Oct 2026 on a copy of the box state after G2a (88cb9e5). Tested there: check_structure 40/40, research/f1/verify.py clean (FAQ structured data valid), 40-page audit (no script errors, menu opens everywhere), 64 calculator runs (ideal-weight calculator unchanged and working), phone render checked (chart fits 390 px).

What changes on /ideal-weight/ (the calculator is untouched):
- The "Ideal Weight by Height Chart" heading said "the table below" but there was no table (removed in an earlier cleanup). Rebuilt: women 5'0"-6'0" and men 5'2"-6'6", average of the four equations (medium frame), ±10% for small/large frames (Hamwi rule of thumb per Pai & Paloucek 2000), and the BMI 18.5-24.9 healthy range at each height for comparison. Targets "ideal weight chart" / "ideal body weight chart" / "goal weight by height".
- History and formula claims corrected to what the sources say (Pai & Paloucek, Ann Pharmacother 2000; Peterson et al., Am J Clin Nutr 2016): Devine 1974 gentamicin article, >200 citations by 2000; Robinson and Miller 1983 regression equations strikingly similar to Devine's; Miller from the 1983 Metropolitan Life tables; "any one of these equations may be used"; equations misaligned with BMI at short and tall heights. Removed unsourced claims (MetLife "millions of policyholders", "Caucasian populations", "Robinson closest to the BMI middle", "Miller most generous at average height" — false for men, "never validated / inertia").
- 5'8" woman example fixed: the four equations average about 140 lb (page said 137).
- Elbow-breadth frame thresholds (unsourced) removed; frame described as defined in the 1983 MetLife tables.
- FAQ: age answer no longer says "optimal weight shifts with age"; the 5-10% weight-loss claim now cites Wing et al. 2011; formula-accuracy answer matches Pai & Paloucek's conclusion.
- References/resources: Miller reference corrected (Am J Hosp Pharm 1983;40:1622-1625; was 40(11):1806-1808), wrong PMC link replaced by Peterson 2016 (PMC4841935), two resource entries with stripped names removed, WHO fact sheet linked, link to a redirected guide pointed at its live target.
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script kept in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/ideal-rewrite/`. Anything else: STOP and report.
1. `python3 research/ideal-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/ideal-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "<table" ideal-weight/index.html | wc -l` → `2`
   3.4 `grep -c "1806\|PMC4890841\|overweight-bmi-risks" ideal-weight/index.html` → `0`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(ideal-weight): rebuild missing by-height chart, correct formula history to sources, fix references"`
5. REPORT — print exactly this, nothing after it:
```
REPORT ideal-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
