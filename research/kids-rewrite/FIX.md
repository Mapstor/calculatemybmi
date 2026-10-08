# Batch G2a — /kids-bmi-calculator/ rewrite (calculatemybmi). Apply after K3.
Prepared in chat, 8 Oct 2026 on a copy of the box state after K3 (e0cb070). Tested there: check_structure 40/40, research/f1/verify.py clean, 40-page audit (no script errors, menu opens everywhere), 64 calculator runs (kids calculator unchanged and working), phone render checked (tables fit 390 px).

What changes:
- The calculator itself is untouched. The 5,349-word long-form below it (26 flagged claims: unsourced health lists, prescriptive diet/screen/juice tips, an unsourced "five times more likely" figure, a broken ": Childhood Obesity" resource, links to redirected guides) is replaced by ~1,500 sourced words:
  CDC categories table and percentile explanation; how the calculator works (LMS, CDC extended data); NEW girls/boys BMI-for-age percentile cut-off tables (5th/85th/95th, ages 2-19) computed from the same CDC LMS file the calculator uses, checked against the CDC medians; the CDC median table (kept); NCHS Health E-Stat 112 figures; CDC-attributed health links and contributing factors; attributed HHS activity guidance and AASM sleep recommendations (Paruthi et al. 2016); when to talk to the doctor; 5 FAQs (site FAQ component, no FAQPage markup); sources; related links.
- Title/H1 now target the page's top query ("bmi calculator teenage", 12,100/mo): "BMI Calculator for Kids & Teens (Ages 2–19): CDC Percentile" / "BMI Calculator for Kids and Teens"; meta description updated.
- sitemap.xml lastmod 2026-10-08; research/HANDOFF.md progress note; generator kept in research/g2/.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/kids-rewrite/`. Anything else: STOP and report.
1. `python3 research/kids-rewrite/apply_build.py --dry-run` — must print `DRY RUN — applied: 1 new files, 3 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/kids-rewrite/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -c 'class="faq-item"' kids-bmi-calculator/index.html` → `5`
   3.4 `grep -c "Girls: BMI at each percentile" kids-bmi-calculator/index.html` → `1`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "content(kids): sourced rewrite, CDC-LMS percentile cut-off tables for girls and boys, teen-focused title"`
5. REPORT — print exactly this, nothing after it:
```
REPORT kids-rewrite
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
