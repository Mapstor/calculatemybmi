# Batch S1 — new page /obesity-rate-by-state/ (calculatemybmi)
Prepared in chat, 2 Oct 2026 on a copy of the live commit 1a85c58. Tested there: check_structure 35/35, research/f1/verify.py clean (JSON-LD, inline JS, anchors, FAQ parity), number audit on /us-obesity-statistics/ clean, 0 broken internal links, widget test 19/19 in a simulated browser (jsdom; needs network to install, so it is shipped for reference only), renders checked at 360 px and 1280 px.

What it adds:
- /obesity-rate-by-state/ — CDC BRFSS adult obesity for every state 2011-2025 (801 state-year values with 95% CIs) + 2025 by age; tile map with year slider, state panel (trend, CI, rank, age), full static ranking table (JS-off safe), top/bottom 10, trend chart, self-reported vs measured figure, gaps disclosure, FAQ (no FAQPage markup), sources, two CSV downloads, Article + Dataset + BreadcrumbList schema, OG image.
- Inbound link from /us-obesity-statistics/ (measured vs self-reported section, anchor "obesity rate by state").
- sitemap.xml entry (lastmod 2026-10-02).
- research/: keyword ledger (+105 rows, 19 KWP variants folded), page-map (state page built, verified source), source registry (cdc-brfss-state-obesity verified), HANDOFF note, research/state-obesity/ (CDC raw CSVs, parsed data, generator, facts).

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/state-page/`. Anything else: STOP and report.
1. `python3 research/state-page/apply_build.py --dry-run` — must print `DRY RUN — applied: 12 new files, 3 replaced files, 3 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/state-page/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `35/35 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c "obesity-rate-by-state" sitemap.xml us-obesity-statistics/index.html` → `sitemap.xml:1` and `us-obesity-statistics/index.html:1`
4. Commit: `git add obesity-rate-by-state/ research/ sitemap.xml us-obesity-statistics/index.html`; `git status --porcelain` must be empty; then
   `git commit -m "feat: /obesity-rate-by-state/ — CDC BRFSS 2011-2025 state rates, tile map + year slider, rankings, age 2025, CSV downloads; ledger/registry/page-map updated"`
5. REPORT — print exactly this, nothing after it:
```
REPORT state-page
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <lines>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -25>
final status: <git status --porcelain, or "clean">
```
