# CMB-006 PILOT-MEN — /men-bmi-calculator/ rebuilt with the skills, on a branch

Built and tested in chat on 2026-10-11 against GitHub `main` at `e6d94fd` + CMB-005 (Chromium 1194, jsdom 24, impeccable engine 0.1.14). It is a pilot: everything lands on branch **`pilot/men-skills`**; `main` gets only the DEVLOG entry. The owner pushes the branch, looks at the Vercel preview and decides whether the pattern rolls out.

What it changes and why: `research/men-pilot/SPEC.md` (spec, scorecard, rollout notes). In short:
- `men-bmi-calculator/index.html`: rebuilt page.
  - Tool first; "Compared with US men" rank in the results (NHANES 2021–2023 percentile); answer block + Key takeaways under the card.
  - Contents chips, a worked example explaining every output, percentile / by-height / body-fat tables, waist section with a new SVG.
  - 8-question FAQ (JSON-LD in sync), one sources-and-method block, one flat related block.
  - New descriptions, new OG image.
- `assets/css/styles.css`: new `--link` token (#0e7490) for text links (global), footer links stay light. Opt-in classes appended (`main.reading`, `.flow`, `.stat-callout`, `.toc-inline`, `.faq-list.flat`, `.related-cols`, `.rank-box`, `.figure`, `.result-item-alt`).
- `assets/js/calculator.js`: healthy min/max tiles put the converted unit on its own line (no mid-unit wrap at 390 px). Shared: every adult calculator.
- `DESIGN.md`: the `--link` colour.
- `research/data-sources.csv`, `research/page-map.csv`: the NHANES row and the men-page row record the built wedge.
- New: `assets/images/og/men-bmi-us-rank.png`, `research/men-pilot/` (generator, stats script + output, CSS source, OG renderer, reference tests, SPEC.md).

Chat results:
- impeccable detect on the men page: 57 → 2 at 390×844 and 76 → 2 at 1280×800; advisories 3 → 0. The 2 left are the brand CTA gradient, an owner decision.
- Anti-slop: 31 tells → 0.
- Calculator: 1,140 Chromium checks and jsdom 77/77 pass; 8/8 rank cases pass.
- No sideways scroll at 360/390/1280. An independent fact-check found all 149 numbers traceable.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's last step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start on main, CMB-005 in place
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-006-pilot-men/`.
0.3 `git log --oneline -15 | grep -c "CMB-005"` → 1 or more. If 0, STOP: CMB-005 must run first.
0.4 `git branch --list pilot/men-skills` → no output. If the branch exists, STOP.

### 1. Branch
`git switch -c pilot/men-skills` → `Switched to a new branch 'pilot/men-skills'`. The untracked package folder comes along.

### 2. Dry run
`python3 research/cmb-006-pilot-men/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 10 new files, 6 replaced files, 0 edits, 0 deletions`. An `ABORT` line → STOP and report the list. Run `git switch main` first so main stays untouched, then delete the empty branch with `git branch -d pilot/men-skills`.

### 3. Apply
`python3 research/cmb-006-pilot-men/apply_build.py`
Must print exactly: `applied: 10 new files, 6 replaced files, 0 edits, 0 deletions`.

### 4. Gates (all must pass)
4.1 `python3 scripts/check_structure.py` → first line `check_structure: 40/40 pages pass`.
4.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
4.3 `node --check assets/js/calculator.js` → no output, exit 0.
4.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
4.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
4.6 `python3 scripts/check_markup.py men-bmi-calculator/index.html` → `men-bmi-calculator/index.html: 0 issues`.
4.7 `grep -o 'id="men-rank"' men-bmi-calculator/index.html | wc -l` → `1`; `grep -o "(teaser)\|whatever the BMI\|men-specific" men-bmi-calculator/index.html | wc -l` → `0`.
4.8 `grep -o "\-\-link: #0e7490" assets/css/styles.css | wc -l` → `1`; `grep -o "result-item-alt" assets/js/calculator.js | wc -l` → `4`.
4.9 `python3 research/men-pilot/slop_scan.py men-bmi-calculator/index.html | tail -1` → ends `tells 0, per 1000 words 0.0`.
4.10 Browser and jsdom tests: the box has neither (DEVLOG §4) → record as skipped, not run. Chat ran them: Chromium 1,140 calculator checks 0 failures, 8 rank cases 0 failures, jsdom 77/77, impeccable detect 2 findings (CTA) at 390×844 and 1280×800.

### 5. Commit on the branch
```
git add -A
git commit -m "pilot: /men-bmi-calculator/ rebuilt with content-page, seo-visibility, anti-slop and impeccable skills (CMB-006)"
```
Note the commit hash.

### 6. Back to main for the DEVLOG
`git switch main`. Then `git status --porcelain` → no output (the pilot files live only on the branch). The DEVLOG step in the prompt runs **on main** and commits DEVLOG.md there; the branch never carries a DEVLOG change, so a later merge can't conflict on it.

### 7. REPORT
```
REPORT CMB-006 PILOT-MEN
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-005 commits <0.3> | existing branch <0.4 or none>
dry-run: <line>
apply: <line>
gates: 4.1 <line> | 4.2 <line> | 4.3 <exit code> | 4.4 <last line> | 4.5 <line> | 4.6 <line> | 4.7 <n> <n> | 4.8 <n> <n> | 4.9 <line> | 4.10 skipped (no browser/jsdom in box)
pilot commit: <git log --oneline -1 pilot/men-skills>
diff vs main: <git diff --stat main pilot/men-skills | tail -1>
main after DEVLOG: <git log --oneline -3 main>
final: <git status --short, or "clean"> on <git branch --show-current>
```
