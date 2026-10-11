# Batch CMB-004 — markup repair v2 + men-page input labels (calculatemybmi)

Prepared in the skills chat on 11 Oct 2026, on a copy of local main 6670731 (pushed as `review/cmb-003`). Rendered and tested there in Chromium at 390 and 1280 px. The numbers below come from those renders. This batch supersedes the tag fixes from CMB-003 STEP 1.

## Why
CMB-003 balanced the tags but nested them wrong. Its gates check tag balance and text, not structure, and the box can't render. The review push rendered like this:
- 11 guides: the article text moved out of `.container`. Text touching the screen edge at 390 px went from 602 blocks (live) to 948.
- Homepage: the "Healthy weight by height: examples" h2 still holds its paragraph and table.
- `/women-bmi-calculator/`, `/new-bmi-calculator/`, `/kids-bmi-calculator/`, `/lean-body-mass/`: the article still sits inside the calculator card. On `/new-bmi-calculator/` it sits inside the hidden results box, so 62 text blocks stay invisible until someone presses Calculate. This has been live since a83d1f7 (27 Sept).
- `/blog/bmi-limitations/`: 68 text blocks are still clipped inside a broken chart bar (live).

## What changes
Markup only. On every page, the visible text, links, title, meta and JSON-LD stay byte-identical to production.
- **20 pages** are rebuilt from their production versions with structure-correct fixes:
  - Each missing closing tag goes back where its element's content ends: bold labels, the homepage h2, card and FAQ items, and the calculator and results boxes.
  - Leftover closers of removed wrappers are deleted.
  - One emptied section is removed on `/lean-body-mass/`.
  - The Sources block on `/blog/bmi-history/` moves inside `.container`.
- **`/men-bmi-calculator/`**: the 5 calculator inputs get an `id`, and their labels get a matching `for` (kept from the CMB-003 Impeccable test). "BMI Distribution Among U.S. Adult Men" becomes an h2, which fixes the skipped heading level.
- **`scripts/check_markup.py`** gets three structure checks: `block-in-heading`, `outside-container` and `content-in-calculator`. `check_structure.py` already runs it, so every batch gate enforces them from now on.
- **`.gitignore`** gets `__pycache__/`, because `check_structure.py` imports `check_markup.py`.

## Rendered result (all 40 pages, 390 px)

| Check | Live | After this batch |
|---|---|---|
| Bold-bleed paragraphs | 393 | 43 (all intended bold paragraphs on untouched pages) |
| Text touching the screen edge | 602 | 0 |
| Hidden article text | 132 | 2 (both intended: the New BMI results heading before Calculate, and a method note in an inactive panel) |
| Sections inside calculators | 35 | 0 |
| Headings holding block content | 1 | 0 |
| Pages with sideways scroll | 1 | 0 |

`assets/css/men.css` from the test branch is **not** part of this batch (see DEVLOG).

## Rules
Do not edit any file by hand: only `apply_build.py` writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain`. Expected: `?? research/cmb-004-markup/`, plus `?? scripts/__pycache__/` if present. Any modified or staged tracked file: STOP and report. Other untracked files: list them, leave them alone and never commit them.
1. `python3 research/cmb-004-markup/apply_build.py --dry-run` must print `DRY RUN — applied: 0 new files, 22 replaced files, 0 edits, 0 deletions`. If it prints ABORT, STOP and report its full output.
2. `python3 research/cmb-004-markup/apply_build.py`
3. Gates. All must pass. On any FAIL, STOP before committing and report.
   - 3.1 `python3 scripts/check_structure.py` → `check_structure: 40/40 pages pass`
   - 3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   - 3.3 `python3 scripts/check_markup.py` on every page in sitemap.xml plus `404.html` → every file `0 issues`
   - 3.4 Text identical to production. For each of the 20 changed pages (`git diff --name-only HEAD -- '*.html'`), this must print nothing:
     `diff <(python3 scripts/check_markup.py --text <(git show origin/main:PAGE) | tail -n +2) <(python3 scripts/check_markup.py --text PAGE | tail -n +2)`
   - 3.5 Negative test: `git show origin/main:index.html > /tmp/cmb004-old.html && python3 scripts/check_markup.py /tmp/cmb004-old.html` must exit 1 and list `block-in-heading`.
4. Commit.
   - Stage the files: `git add .gitignore scripts/check_markup.py research/cmb-004-markup/ && git add -u -- '*.html'`
   - `git status --porcelain` must show no modified or unstaged tracked file, only the untracked files listed in step 0 (if any).
   - `git commit -m "fix(markup): structure-correct repair v2 on 20 pages, men-page input labels, structure checks in check_markup (CMB-004)"`
5. REPORT. Print exactly this, nothing after it:
```
REPORT cmb-004-markup
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <N files, all 0 issues> | 3.4 <pages with a text diff: 0> | 3.5 <exit code + kinds listed>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -4>
final status: <git status --porcelain, or "clean">
```
