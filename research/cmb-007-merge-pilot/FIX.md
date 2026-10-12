# CMB-007 MERGE-PILOT — men page to main, action colour, small cleanups

Owner, 2026-10-12: "new page looks splendid! much much better!"
- **R4 check on pilot/men-skills:** `impeccable detect` at 390×844 found 2 findings, both on the brand CTA gradient.
- **Decisions:** Calculate button = option A (flat cyan-700); link colour #0e7490 sitewide; `/privacy/` and `/terms/` keep "Last updated".

Built and tested in chat on 2026-10-12 against a replica of the owner's `main` (`e6d94fd` + CMB-005 + CMB-006 + DEVLOG commits) with Chromium 1194, jsdom 24 and impeccable engine 0.1.14.

## What changes
1. **Merge.** `pilot/men-skills` (CMB-006) is merged into `main` with `--no-ff`. Only the git merge and `apply_build.py` change files.
2. **`assets/css/styles.css`**
   - New token `--link-hover: #155e75` (cyan-800, 7.3:1 on white).
   - **Calculate button** (`.calculate-btn`: the 8 calculator pages plus the 2 buttons on `/us-obesity-statistics/`): flat `--link` (#0e7490, white text 5.4:1); hover `--link-hover`. The gradient, glow and hover lift are gone. The old gradient measured 2.4–3.7:1 with white text.
   - **Text-link hover:** `a:hover`, `.nav-dropdown-menu a:hover`, `.toc-list a:hover` and `.related-article-card h4 a:hover` use `--link-hover`. The old hover, #06b6d4, is 2.4:1 on white.
   - **Footer links:** `.footer-bottom a:hover` turns white (dark footer).
   - **Form controls:** `button, input, select, textarea { font-family: inherit; }`. Buttons, inputs and FAQ questions now use the site font; they used the browser default (Arial on Windows and Linux).
3. **Orange tool button** (`.aw-cta` on `/average-weight/`, `/body-fat-calculator/`, `/body-fat-percentage-chart/`; `/blog/what-is-bmi/` carries the same CSS, unused): same flat `--link` and hover. It was white on an orange gradient, 3.4:1. Size, radius and weight are unchanged.
4. **`/men-bmi-calculator/`:** the WHO 2008 waist–hip report gets its link, in the body sentence and in the sources list (https://www.who.int/publications/i/item/9789241501491). `sitemap.xml` lastmod for the page → 2026-10-12.
5. **`DESIGN.md`:** the `--link-hover` token, the action-button rule and the form-control font.
6. **Deleted:** `assets/images/og/men-waist-nhlbi-scale.png`. After the merge no page references it; only `research/` archives do.
7. **New:** `research/impeccable-baseline/2026-10-12-cmb007-390x844.json`, chat's per-page detector counts after this batch (734 findings on 41 pages). Each rollout batch reports its page against it.

**Chat results**
- **impeccable detect at 390×844, all 41 pages:** 757 → 734 findings, no page worse. The men page is at **0**. The calculators and the three data-page tools each lose their button findings.
- **Calculator checks:** jsdom 77/77, Chromium 1,140/1,140, rank 8/8.
- **Page behaviour:** the FAQ opens on all 25 FAQ pages and the menu opens and closes on 41/41. No page is wider than the screen at 360, 390 or 1280 px (123 loads).
- **Hover:** buttons and links measured #0e7490 → #155e75; footer links white.

## Rules
- Only the merge in step 1 and `apply_build.py` change files. Do not edit any file by hand (DEVLOG.md in the prompt's DEVLOG step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-007-merge-pilot/`.
0.3 `git log --oneline -1 pilot/men-skills` → a line ending `(CMB-006)`. No such branch → STOP.
0.4 `git diff --name-only main...pilot/men-skills | wc -l` → `35`; `git diff --name-only main...pilot/men-skills | grep -c DEVLOG.md` → `0`.

### 1. Merge
`git merge --no-ff pilot/men-skills -m "merge: men page pilot approved by owner 2026-10-12 (CMB-006 into main, CMB-007)"`
- Must finish without conflicts. On a conflict: `git merge --abort`, then STOP and report.
- Then `git diff --name-only HEAD pilot/men-skills` → exactly `DEVLOG.md`.

### 2. Dry run
`python3 research/cmb-007-merge-pilot/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 1 new files, 8 replaced files, 0 edits, 1 deletions`. An `ABORT` line → STOP and report the list. The merge commit stays; do not reset.

### 3. Apply
`python3 research/cmb-007-merge-pilot/apply_build.py`
Must print exactly: `applied: 1 new files, 8 replaced files, 0 edits, 1 deletions`.

### 4. Gates (all must pass)
4.1 `python3 scripts/check_structure.py` → first line `check_structure: 40/40 pages pass`.
4.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
4.3 `node --check assets/js/calculator.js` → no output, exit 0.
4.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
4.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
4.6 `for f in men-bmi-calculator average-weight body-fat-calculator body-fat-percentage-chart blog/what-is-bmi; do python3 scripts/check_markup.py $f/index.html >/dev/null || echo "MARKUP FAIL $f"; done` → no output.
4.7 Each of these prints the number shown:
- `grep -o 'background: var(--link); border: none' assets/css/styles.css | wc -l` → `1`
- `grep -o 'rgba(6, 182, 212' assets/css/styles.css | wc -l` → `0`
- `grep -o 'button, input, select, textarea { font-family: inherit; }' assets/css/styles.css | wc -l` → `1`
- `grep -o 'linear-gradient(135deg,#C2481E 0%,#E5743F 100%)' average-weight/index.html body-fat-calculator/index.html body-fat-percentage-chart/index.html blog/what-is-bmi/index.html | wc -l` → `0`
4.8 `test -e assets/images/og/men-waist-nhlbi-scale.png; echo $?` → `1`; `grep -l "men-waist-nhlbi-scale" */index.html blog/*/index.html index.html | wc -l` → `0`.
4.9 `grep -o 'who.int/publications/i/item/9789241501491' men-bmi-calculator/index.html | wc -l` → `2`.
4.10 Browser, jsdom and detector checks: the box has none (DEVLOG §4) → record as skipped. Chat's results are in "What changes" above. Layout stays unverified until the owner's R4 check on the live men page after the push.

### 5. Commit
```
git add -A
git commit -m "style: flat cyan-700 action buttons and darker link hover (AA contrast), form controls use the site font, WHO waist-hip link, old men OG image removed (CMB-007)"
```

### 6. Remove the merged local branch
`git branch -d pilot/men-skills` → `Deleted branch pilot/men-skills (was …)`. If git refuses (not fully merged), STOP. Never use `-D`.

### 7. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 8. REPORT
```
REPORT CMB-007 MERGE-PILOT
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | pilot head <0.3> | branch files <0.4 n> <0.4 DEVLOG n>
merge: <git log --oneline -1> | HEAD vs branch: <output>
dry-run: <line>
apply: <line>
gates: 4.1 <line> | 4.2 <line> | 4.3 <exit> | 4.4 <last line> | 4.5 <line> | 4.6 <output or none> | 4.7 <n> <n> <n> <n> | 4.8 <exit> <n> | 4.9 <n> | 4.10 skipped (no browser/jsdom in box)
commit: <git log --oneline -3>
branch delete: <line>
final: <git status --short, or "clean"> on <git branch --show-current>
```
