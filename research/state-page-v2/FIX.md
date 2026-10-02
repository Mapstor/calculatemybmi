# Batch S2 — /obesity-rate-by-state/ redesign: real US map + rich state panel (calculatemybmi)
Prepared in chat, 2 Oct 2026 on a copy of the live commit f27aa28. Tested there: check_structure 35/35, research/f1/verify.py clean, number audit clean, widget test 26/26 in a simulated browser (jsdom; shipped for reference), renders checked at 390 px and 1280 px.

What changes (one page, same URL, same data and sources):
- Tile grid replaced by a real US choropleth: US Census Bureau cartographic boundaries (via the us-atlas package, simplified, Albers USA with Alaska/Hawaii insets), hatched "no estimate" states, DC marker, state labels on wider screens, hover tooltips, keyboard access.
- Play button (animates 2011-2025) + year slider; highlight cards (highest, lowest, states at 35%+, biggest rise).
- State panel: big number + rank badge, 95% CI bar with the median state, plain-English comparisons (vs median, range, land neighbours from shared borders, previous year with CI-overlap check, since 2011 incl. rank then/now, peak year, CDC 2025 regional figure), comparison bars (median, highest, lowest, neighbours), 2011-2025 trend with CI band and median-state line, 2025 age bars.
- Static sections: ranked bar lists, region cards, stacked "how states shifted between bands" chart (replaces the 35%+ bar chart), inline bars in the ranking table.
- research/: generator v2 (gen_page2.py + viz2.py + states_paths.json), facts, widget test; HANDOFF note.

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/state-page-v2/`. Anything else: STOP and report.
1. `python3 research/state-page-v2/apply_build.py --dry-run` — must print `DRY RUN — applied: 5 new files, 1 replaced files, 1 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/state-page-v2/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `35/35 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `grep -o 'class="obs-st"' obesity-rate-by-state/index.html | wc -l` → `50`
4. Commit: `git add obesity-rate-by-state/index.html research/`; `git status --porcelain` must be empty; then
   `git commit -m "feat(state map): real US choropleth (Census boundaries), play/slider, rich state panel (median, neighbours, CI, trend, age), visual sections"`
5. REPORT — print exactly this, nothing after it:
```
REPORT state-page-v2
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -12>
final status: <git status --porcelain, or "clean">
```
