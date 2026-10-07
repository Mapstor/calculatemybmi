# Batch N1 — Body Fat calculator in the header menus + /calculators/ hub (calculatemybmi)
Prepared in chat, 7 Oct 2026 on a copy of the box state after B2 (commit 0ac545b). Tested there: check_structure 39/39, research/f1/verify.py clean, number audit clean, every page has exactly 2 "Body Fat" menu links, hub schema parses (ItemList 9), hub card rendered at 390 px.

What changes (93 exact edits, no new files):
- Header: "Body Fat" (/body-fat-calculator/) added after "Lean Body Mass" in the desktop Calculators dropdown and the mobile menu, on all 39 pages.
- /calculators/: card 9 "Body Fat Calculator" (example computed with the calculator's equations and our verified CDC percentiles: 18.5% -> 94% of US men 30-39 have more body fat; links the body fat chart), comparison-table row, ItemList entry 9 (numberOfItems 9), counts 8 -> 9 (copy, og/twitter image alt, comment), the "use 2-3 calculators together" tip now mentions the body fat calculator, dateModified 2026-10-07.
- sitemap.xml: /calculators/ lastmod 2026-10-07 (the other pages only got a menu link, so their dates stay).
- research/: stale comment fixed in research/body-fat-calculator/tool_test_jsdom.js; HANDOFF note.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/nav-hub/`. Anything else: STOP and report.
1. `python3 research/nav-hub/apply_build.py --dry-run` — must print `DRY RUN — applied: 0 new files, 0 replaced files, 93 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/nav-hub/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `39/39 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `python3 -c "import glob;b=[p for p in glob.glob('**/index.html',recursive=True) if not p.startswith('research/') and open(p,encoding='utf-8').read().count('<a href=\"/body-fat-calculator/\">Body Fat</a>')!=2];print('nav check:',b or 'all pages have 2')"` → `nav check: all pages have 2`
4. Commit: `git add -A`; then `git status --porcelain` must be empty; then
   `git commit -m "feat(nav): Body Fat calculator in header menus on all pages; /calculators/ card, table row, ItemList, counts 8->9"`
5. REPORT — print exactly this, nothing after it:
```
REPORT nav-hub
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -3>
stat: <git show --stat HEAD | tail -6>
final status: <git status --porcelain, or "clean">
```
