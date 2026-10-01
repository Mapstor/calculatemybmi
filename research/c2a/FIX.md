# Batch C2a — fabricated quote, broken sentences, ACE remnants, dead TOC links, FAQ schema parity (calculatemybmi)
Prepared in chat, 1 Oct 2026. 44 exact edits across 14 files, tested on a copy of HEAD e61c9e0: check_structure 34/34, number audit clean, JSON-LD and inline JS parse on every page, 0 dead in-page anchors, every FAQPage question visible on its page, 0 leftover artifacts.

What it changes:
- /blog/bmi-limitations/: removes a fabricated quote credited to "Dr. Timothy Church" (its first sentence is really Jeffrey Hunger, UCSB 2016; the rest and the attribution have no source).
- Repairs sentences broken by the old never-cite link stripping ("Thenotes", "Asexplains", "Therecommends", "thenotes", "Asnotes", "The()", "Asresearchers") on home, men, women, healthy-bmi-range, bmi-chart-explained, bmi-history, lean-body-mass. Claims kept only with a verified primary source: Wing et al., Diabetes Care 2011 (PMC3120182); NCHS Data Brief 508; WHO expert consultation, Lancet 2004 (PMID 14726171); Caspersen et al. 1985 (PMC1424733).
- Removes ACE body-fat numbers (never-cite) and the empty "categories" headings/tables they left behind; the men's "14-17% fitness body fat" box that credited ACE's range to NHLBI; an invented body-composition donut chart (45/30/15/10%); FAQ entries carrying ACE numbers.
- Removes table-of-contents links that point to sections deleted in earlier cleanups.
- Aligns FAQPage structured data with the FAQs actually shown (schema-only questions removed; Google requires markup to match visible content).
- Rebuilds the lean-body-mass "Trusted Resources" list (stripped ACE/ACSM/NSCA/Harvard remnants removed; CDC, NHLBI, NIH Body Weight Planner linked).

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/c2a/`. Anything else: STOP and report.
1. `python3 research/c2a/apply_fixes.py --dry-run` — must print `DRY RUN — applied 44 edits to 14 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/c2a/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `python3 research/c2a/verify.py` → must print `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/c2a/`; `git status --porcelain` must be empty; then
   `git commit -m "fix(content): remove fabricated quote, repair link-stripping sentences with verified sources, drop ACE remnants + invented chart, dead TOC links, FAQ schema parity"`
5. REPORT — print exactly this, nothing after it:
```
REPORT c2a
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -22>
final status: <git status --porcelain, or "clean">
```
