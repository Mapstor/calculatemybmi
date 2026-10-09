# Batch G2g — /lean-body-mass/ corrections (calculatemybmi). Apply after G2f (already pushed).
Prepared in chat, 8 Oct 2026 on a copy of the live state (7e870be). Tested there: check_structure 40/40, research/f1/verify.py clean (FAQ structured data valid and synced), calculator checks 36/36, 40-page audit (no script errors, menu opens everywhere), 64 calculator runs.

What changes on /lean-body-mass/ (the calculator is untouched):
- Formula comparison table: every printed value was wrong (e.g. Hume for a 175 cm / 75 kg man shown as 59.7 kg; the equation gives 54.4 kg). Rebuilt from the same Boer/James/Hume equations the calculator uses; the figure that plotted the wrong values removed; the commentary now matches the numbers (Hume lowest in every example; spread 1.4 kg for the women, 2.9-6.3 kg for the men).
- Hume authorship corrected (Hume 1966, not "Hume and Weyers"); unsourced Peters "for children" section removed (not used by the calculator); "most widely cited and validated" and "studies show Boer closest to DEXA" removed; coefficient interpretation replaced by the fact that the equations were fitted separately by sex.
- Body fat vs BMI: the ACE-tier caption and the orphan "values are approximate ranges" note (its table no longer exists) removed; the claim linked to an unrelated NCHS brief now points to our CDC-scan body fat chart.
- Removed a protein target (105-150 g/day), drug-dosing specifics, "crash dieting costs lean mass", and unsourced FAQ figures ("40-50% of LBM", "2-3% essential lipid", "easier to gain fat with age", "people in their 70s and 80s can build muscle"); Volpi kept for muscle loss; link to the body-fat method comparison added.
- "Deep links pending" note on the references removed. FAQ structured data synced.
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md note; patch script in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/lbm-rewrite/`. Anything else: STOP and report.
1. `python3 research/lbm-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/lbm-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o "59.7 kg\|72.1 kg\|56.4 kg\|E. Weyers\|105-150\|ACE" lean-body-mass/index.html | wc -l` → `0`
   3.4 `grep -o "54.4 kg" lean-body-mass/index.html | wc -l` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(lean-body-mass): rebuild wrong comparison table from the equations, fix authorship, remove unsourced claims and targets"`
5. REPORT — print exactly this, nothing after it:
```
REPORT lbm-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
