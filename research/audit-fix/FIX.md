# Batch K2 — fixes from the full-site audit (calculatemybmi). Apply AFTER K1.
Prepared in chat, 7 Oct 2026 on a copy of the box state after K1. Audit run there: all 40 pages in a simulated browser (script errors, menu, H1, image alt, duplicate titles/descriptions, internal links, missing assets incl. share images, HTML inside meta tags), phone-width render of every page, 64 calculator runs (8 calculators x imperial/metric x typical/short-heavy/tall-light/empty). After K2: check_structure 40/40, verify clean, calculator checks 36/36, no script errors, menu opens on all 40 pages, no HTML in meta tags.

What changes:
- /blog/bmi-by-age/: og:description contained an <a> tag; its quotes broke the attribute and printed "Winter et al., Am J Clin Nutr, 2014 plateau for 65+.">" above the header on every visit. Now plain text.
- /about/: the author text box could not shrink below 250 px, so the page was wider than a phone screen (426 px at 390). Fixed.
- /privacy/: data controller shown with the registered address (Smolnik 62, 2342 Ruse) instead of "based in Maribor".
- /calculators/: removed "WHO-endorsed formulas" (WHO doesn't endorse Devine, Boer, Trefethen or the Navy equations) in the quick guide, the FAQ answer and its structured data; removed "age-adjusted / modified healthy ranges" (adult cut-offs don't change with age) and outdated women/men descriptions in the structured data.
- /ideal-weight/: "Endorsed by the WHO and CDC" -> "Used to classify weight status by the WHO and CDC".
- assets/js/calculator.js: New BMI and kids results follow the chosen units; kids results no longer show unsourced sleep-hour recommendations or diet advice (pediatrician guidance instead).
- research/: audit scripts in research/audit/ (need jsdom, reference only); HANDOFF note.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace). K1 must already be committed.

## Steps
0. `git status --porcelain` — expected: only `?? research/audit-fix/`. `git log --oneline -1` must show the K1 commit ("fix(calculator): mobile menu double-binding..."). Anything else: STOP and report.
1. `python3 research/audit-fix/apply_build.py --dry-run` — must print `DRY RUN — applied: 3 new files, 7 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/audit-fix/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `40/40 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `node --check assets/js/calculator.js && echo "calculator.js syntax OK"` → `calculator.js syntax OK`
   3.4 `grep -c "WHO-endorsed" calculators/index.html` → `0`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "fix(audit): leaked meta text on bmi-by-age, about overflow, privacy address, remove WHO-endorsed/age-adjusted claims, New BMI + kids units, kids advice"`
5. REPORT — print exactly this, nothing after it:
```
REPORT audit-fix
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -3>
stat: <git show --stat HEAD | tail -12>
final status: <git status --porcelain, or "clean">
```
