# CMB-008 WEIGHT-TABLES — every weight-by-height table lists weights inside their category, in lb and kg

Built and tested in chat on 2026-10-12 against a replica of the owner's `main` after CMB-007, made from GitHub `main` `c697285` plus CMB-007. Tools: Chromium 1194, jsdom 24, impeccable engine 0.1.14.

## The problem
The pages say "every listed weight is guaranteed to be inside its category", but in many tables only the pounds were true:
- **How the kilograms were made.** They were rounded conversions of the pound bounds, so a kilogram value often sat in the next category. Example: `/blog/bmi-chart-men/` at 5'2" said healthy is 46–**62 kg**, but 62 kg at 157.5 cm is BMI 25.0 (overweight).
- **Rounded height labels.** The heights were labelled in rounded cm (157 cm), not the exact height the weights were worked out for.
- **The 3 chart pages:** **137 of 390** kg ranges were not the exact whole-kg band. On `/bmi-chart/`'s metric table, **57 of 72** pound ranges were wrong the same way.
- **4 more pages, same bug:** `/` (homepage examples table, 7 wrong kg values), `/blog/healthy-bmi-range/`, `/blog/bmi-categories/` (4 pound values wrong too, e.g. "Low normal 94 lbs" at 5'0" is BMI 18.4), `/blog/underweight-bmi-risks/`.

## What changes
1. **The 3 chart pages, every row regenerated:** 21 + 12 rows on `/bmi-chart/`, 17 on `/blog/bmi-chart-men/`, 15 on `/blog/bmi-chart-women/`.
   - Each cell is the lowest to highest whole pound and whole kilogram whose BMI (rounded half-up to 0.1) falls in that category at that exact height. Each unit is worked out on its own, not converted.
   - Height labels to one decimal: inch rows "5'2" (157.5 cm)", metric rows "145 cm (4'9.1")".
   - The methodology lines say so.
   - The markup, ids and CSS classes are unchanged.
2. **Homepage "Healthy weight by height: examples":** kg ranges and cm labels.
3. **`/blog/healthy-bmi-range/`:** minimum and maximum healthy kg, cm labels.
4. **`/blog/bmi-categories/`:**
   - low and high normal in lb and kg;
   - mid normal = the whole lb and whole kg nearest BMI 21.7;
   - cm labels.
5. **`/blog/underweight-bmi-risks/`:** the "< …" and "normal range start" kg values, cm labels. The third column is untouched.
6. **New gate, `scripts/check_weight_tables.py`:** in any table with a BMI-category header, every range cell (`A–B lb (C–D kg)`, `≤`, `≥`, `<`, kg-first forms) must be the exact whole-unit band in both units, and a paired height label must have one decimal. `scripts/check_structure.py` runs it on every page, so 40/40 now includes it. On the pre-CMB-008 state it reports 33/40.
7. **`research/chart-tables/`:** `chart_rules.py` (the rule), `audit_charts.py` (exact audit of the chart tables), `fix_tables.py` (this batch's build record).
8. **Dates:** `sitemap.xml` lastmod 2026-10-12 for the 7 pages. `dateModified` 2026-10-12 on the 6 that carry one (visible content changed; DEVLOG §4 rule).

**Chat results**
- **Chart tables:** the audit finds 0/390 wrong ranges in lb and in kg.
- **Other pages:** the exact check of the 4 other tables finds 26/26 rows right.
- **`/ideal-weight/` BMI column** (lb only) was already right, 30/30 rows.
- **Gates:** check_structure 40/40 (33/40 before); markup clean on all 41 pages; a visible-text diff shows only table values, labels and the two methodology sentences changed.
- **Browser and calculator checks:** jsdom 77/77; FAQ 25/25; no page wider than the screen at 360, 390 or 1280 px. impeccable detect counts on the 7 pages are unchanged.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's DEVLOG step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-008-weight-tables/`.
0.3 `git log --oneline -8 | grep -c "CMB-007"` → 1 or more. If 0, STOP: CMB-007 must run first.

### 1. Dry run
`python3 research/cmb-008-weight-tables/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 4 new files, 9 replaced files, 0 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-008-weight-tables/apply_build.py`
Must print exactly: `applied: 4 new files, 9 replaced files, 0 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → first line `check_structure: 40/40 pages pass`.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `for f in index.html bmi-chart/index.html blog/bmi-chart-men/index.html blog/bmi-chart-women/index.html blog/healthy-bmi-range/index.html blog/bmi-categories/index.html blog/underweight-bmi-risks/index.html; do python3 scripts/check_markup.py $f >/dev/null || echo "MARKUP FAIL $f"; done` → no output.
3.7 `python3 research/chart-tables/audit_charts.py . | tail -1` → `TOTAL lb wrong 0/390 | kg wrong 0/390`.
3.8 Negative test (the gate catches the old table):
```
git show HEAD:bmi-chart/index.html > /tmp/cmb008-old-chart.html
python3 scripts/check_weight_tables.py /tmp/cmb008-old-chart.html > /dev/null; echo $?
rm /tmp/cmb008-old-chart.html
```
→ prints `1`.
3.9 Browser, jsdom and detector checks: the box has none (DEVLOG §4) → record as skipped. Chat's results are under "What changes".

### 4. Commit
```
git add -A
git commit -m "fix: weight-by-height tables list whole lb and kg inside each category, height labels to one decimal, weight-table gate (CMB-008)"
```

### 5. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 6. REPORT
```
REPORT CMB-008 WEIGHT-TABLES
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-007 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <line> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <output or none> | 3.7 <line> | 3.8 <exit> | 3.9 skipped (no browser/jsdom in box)
commit: <git log --oneline -3>
final: <git status --short, or "clean"> on <git branch --show-current>
```
