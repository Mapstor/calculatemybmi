# CMB-011 CALC-RESULTS — calculator results rebuilt answer-first, metric BMI in kg/m², deletion leftovers repaired, guides hub fixed, stronger gate

Built and tested in chat on 2026-10-14 against GitHub `main` `f3b50ba` (after CMB-010). Tools: Chromium 141, jsdom 24, impeccable engine 0.1.14.

## Why
- **Results panel.** The impeccable detector cannot press Calculate, so chat scanned each calculator with its results open. The panel carried 159 findings across the 8 calculators, including:
  - the BMI number in amber at 1.8:1;
  - white scale labels on 2.1–3.8:1;
  - category-coloured table text;
  - cards inside the results card;
  - arrow glyphs.
  - Its content also had problems:
    - LBM showed the same numbers five times;
    - ideal weight was in kg only for US users;
    - the kids panel called the CDC method a "simplified estimate" and buried the percentile;
    - the ideal-weight "Origin" column and the wrist-size frame rules were unsourced;
    - the FFMI "natural limit" claim was unsourced.
- **Metric BMI.** Metric input went through pounds and the 703 factor. Example: 145 cm / 84 kg showed 39.9 (class II); the kg/m² value is 40.0 (class III). The new test fails on the live code in exactly 16 places (2 cases × 4 calculators × value and category) and passes here.
- **Deletion leftovers.** CMB-010's gate missed text left behind by the Aug–Oct bulk deletions. Chat re-read every bulk-deletion commit since August (`research/site-checks/residue_scan.py`). 15 leftovers are still live on 9 pages. Examples:
  - a caption for a deleted table ("Rows 18–64… Row 65+");
  - a frame-size section that starts at "Method 2";
  - "Limitation #1, #3…" with #2 deleted;
  - "This paradox…" with the paradox deleted.
- **Guides hub.** `/blog/` used link-list classes that have no CSS at all, so every card rendered as run-on cyan text. The hub was also out of date:
  - it says "15 guides" (there are 19) and leaves out the waist-to-height guide;
  - its blurbs are build notes ("Two visuals sit alongside the derivation…");
  - one blurb breaks D-11 ("Why the healthy band widens after age 65").

## What changes

### 1. Results panel, all 8 calculators (`assets/js/calculator.js`, `styles.css`)
- **Answer first.** The order is:
  1. what the result means, in plain sentences;
  2. the weight bar;
  3. milestones;
  4. what-if scenarios;
  5. categories;
  6. more numbers;
  7. links.
  - Section headings are sentence-case `h2` (no more skipped heading after the page `h1`).
- **Flat, readable.**
  - Result card: flat category tint, no border or gradient. The BMI number takes the strong shade (4.7:1 or better on its tint).
  - Scale labels are white on the strong shades (5:1 or better).
  - Sections are divided by hairlines; there are no cards inside the calculator card.
  - Table headers are light; numbers are right-aligned with tabular figures, and the other unit sits under each value.
  - The user's row gets a "You" pill instead of the old "➜ You".
- **Category names** follow CDC: Healthy weight, Overweight, Class 1/2/3 obesity, plus WHO's Severe and Moderate thinness. The milestones already used "Class 2 obesity".
- **Each calculator:**
  - **BMI calculators** (home, women, men, age): the duplicated BMI and healthy-range tiles are gone from "More numbers".
    - The age result gives one sentence ("At 70, the healthy BMI range is 18.5 to 24.9, the same as at every adult age") instead of a six-row table with the same value in every row.
    - Under 20, it points to the kids calculator.
    - The 65+ Winter 2014 note is said once, with its link.
  - **Kids:**
    - The card now says "54th percentile for boys aged 10 years".
    - The "simplified estimate" disclaimer is replaced by what the tool actually uses: CDC charts, with the 2022 extended charts above the 95th percentile.
    - Severe obesity gets its own row.
    - The unsourced growth-spurt and nutrition rows are removed. The page already has an "Official guidance on activity and sleep" section.
  - **Ideal weight:**
    - Results show in the unit entered, e.g. "131 lbs (59.3 kg)".
    - The average shows one decimal (131.4 lbs), because it is the mean of four results.
    - The BMI range uses the same whole-pound band as the BMI calculators.
    - A new line gives the BMI at the formula weights (20.9 to 21.8 at 5′6″).
    - "Where the formulas come from" now matches Pai & Paloucek 2000, verified against the paper: Devine from gentamicin dosing, Robinson from the 1959 tables, Miller from the 1983 tables, "any one of these equations may be used".
    - Removed: the unsourced wrist rules, the "Origin" descriptors, and a duplicate table and chart.
  - **Lean mass:**
    - The tiles show lean mass, fat mass and body fat in the unit entered, with one decimal, matching the /calculators/ example (128.5 lbs).
    - Removed: the "Lean Mass (lbs)" tile, the second composition bar, the bar chart that repeated the tiles, and the FFMI "natural limit" claim.
    - The donut is flat cyan/amber and reads kg from `data-kg`.
  - **New BMI:**
    - The difference and the category change are shown in neutral colours, without red/green judgement.
    - The verdict is attributed: "Trefethen argued…".
    - It no longer says "may be more accurate for you".
    - It states that WHO and CDC define the categories on the traditional formula.
- **Metric BMI is kg/m²** as entered, US units keep 703. The metric healthy limits use kg/m².
- **Dead code removed:** `genHealthRisks`, `riskColor`, `fmtRange`, `getWeightForBMI`.

### 2. Deletion leftovers repaired (9 pages)
- **`/women-bmi-calculator/`:**
  - The "Rows 18–64… Row 65+" caption for a deleted table becomes a sentence (Winter 2014, same facts).
  - The section gets its heading, "BMI for women by age".
  - The unlinked "full BMI chart for women" now links to /bmi-chart/.
  - "Prevalence in U.S. Adult women" → "Obesity among US women".
- **`/ideal-weight/`:**
  - The frame section started at "Method 2" (Method 1 was deleted). It now opens with a heading (`#frame-size`) and the wrist-size cut-offs from MedlinePlus (US National Library of Medicine), verified 2026-10-14.
  - The elbow-breadth sentence was cited to Pai & Paloucek, which does not mention elbow breadth (checked in the full text). The citation now covers only what the paper says.
  - "Hamwi's rule of thumb" is removed from the 10% sentence; the paper doesn't name Hamwi.
  - The FAQ pointed to the deleted wrist table; it now points to the new section (visible text and schema).
  - The frame comparison chart was wrong for men: large frame at 5′6″ showed 167 lb, while the formulas and the page's own table give 155. All four values now come from the formulas (118/145 women, 127/155 men).
- **`/blog/bmi-limitations/`:**
  - "Limitation #2: It Ignores Fat Distribution" is restored, with the NHLBI waist cut-offs and Ashwell 2012. Both sources are already cited on the site. The table of contents is updated.
  - An empty "Muscle/Fat Density" chart is removed.
  - "This has led the WHO to recommend different cut-offs for Asian populations" was wrong: WHO kept the international categories. It now states what the WHO 2004 consultation found.
  - The unsourced "Important Consideration" box built on it is removed.
- **`/blog/body-fat-vs-bmi/`:**
  - Removed: a caption for a deleted chart, and a "Pro Tip" about a deleted measurement table.
  - "Why athletes often have high BMI but low body fat" now answers its own heading.
- **`/blog/bmi-history/`:** "Learn more about these classifications" (none listed) and "This paradox underscores…" (paradox deleted) are rewritten.
- **`/blog/bmi-categories/`:**
  - "acknowledged these differences" (differences deleted) gets its subject back, with a sub-heading.
  - The garbled "lower cut-offs of their own recommendation" is fixed.
- **`/new-bmi-calculator/`:** the "non-adoption" section repeated "The Bottom Line" and cited "some health experts". Removed.
- **`/blog/bmi-and-health-risks/`:**
  - "Notably, obesity also increases…" no longer depends on the deleted osteoarthritis table.
  - An FAQ question had an empty chevron (`stroke-with`, no path).
  - A second link list repeated three links that are already on the page.
- **`/blog/waist-to-height-ratio/`:** a paragraph orphaned by a deleted heading gets a sub-heading.
- **`/calculators/`:** the kids example said "about the 55th percentile". The exact value is 54.46, so it is the 54th; the calculator now prints it.

### 3. Guides hub `/blog/`
- `.related-grid` / `.related-card` get CSS: a flat list, divided by hairlines. This also fixes `/404.html`.
- Every guide is listed once (19), including the missing waist-to-height ratio, and there are no duplicates between "Start here" and "Foundations".
- The blurbs are rewritten for readers (anti-slop), with no D-11 claim and no build notes.
- The misplaced citation inside a card link and the "former shadow guides" note are removed.
- Title, meta, OG/Twitter and intro say 19.
- The ItemList lists the same 19 guides.
- "Calculate now →" becomes "Open the BMI calculator".

### 4. Gate (`scripts/check_content_integrity.py`, `scripts/check_structure.py`)
- New page checks:
  - numbered items that skip a number ("Limitation #1, #3", "Method 2" alone);
  - a "Rows…/Columns…" caption in a section without a table, or "the table below/above" on a page without one;
  - a chart row without its bar, an empty bar track, or an empty icon;
  - a heading with nothing under it.
- `js_problems()` checks `assets/js/calculator.js`: no emoji or arrow entities, no low-contrast hexes as text colour, no gradients.
- Hub check: `/blog/` links every sitemap guide, its ItemList lists exactly those, and the counts in title, description and intro match.
- On the pre-CMB-011 tree these fail:
  - 4 pages (women, ideal-weight, health-risks, limitations);
  - calculator.js (8 problems);
  - the hub (5 problems).
- Tests updated:
  - `research/calculator-checks/calc_e2e_playwright.py`: metric kg/m² expectations, metric category checks, two class-3 cases, no NaN on the other four calculators.
  - `calc_test_jsdom.js`: 95 checks.
- New `research/site-checks/residue_scan.py`; the README is updated.

### 5. Dates
- 12 pages change visible text. 9 were already at 2026-10-14 from CMB-010.
- `lastmod` moves to 2026-10-14 on `/ideal-weight/`, `/blog/bmi-and-health-risks/` and `/blog/body-fat-vs-bmi/`. Schema `dateModified` moves on the last two (the calculator pages carry none).
- Rule from DEVLOG §4.

### Chat results (fresh clone of `f3b50ba` + this package)
- **Gates:**
  - check_structure 40/40, plus the calculator.js and hub checks;
  - verify, schema and number audit clean;
  - markup clean on all 12 changed pages;
  - content-integrity exit 0 on every page and on calculator.js;
  - `date_truth` 40/40 after a 2026-10-14 commit.
- **Calculators:**
  - jsdom 95/95;
  - Chromium end-to-end 1,248 checks, 0 failures. The same test on the live code fails in 16 places, all metric 40.0 cases.
- **Browser:**
  - FAQ 25/25;
  - menu 41/41;
  - no page wider than the screen at 360/390/1280 px;
  - results sections have no sideways scroll at 360/390/1280 in either unit.
- **Detector:**
  - Results panel 159 → **0** findings.
  - With results open, the 8 calculator pages go from 317 → 124 findings in total; the rest is static content left for the D-14 rebuilds.
  - Men page with results open: 30 → 0.
  - Static pages before Calculate: 350 → 348 sitewide, no page worse.
  - `/men-bmi-calculator/` is pixel-identical before Calculate at 390 and 1280.
- **Visible-text diff:** only the changes listed above.
- **anti-slop:** 46 fixes. Top types:
  - build-note blurbs on /blog/: 27;
  - unsourced or overstated claims in results: 9;
  - arrow glyphs: 7;
  - openers and dashes: 3.

### Not in this batch
- Static detector leftovers (348) on the old pages stay for the D-14 rebuilds. On the calculator pages:
  - nested cards on `/ideal-weight/` and `/new-bmi-calculator/`;
  - the stat-highlight gradients on `/age-bmi-calculator/`;
  - purple headings on `/women-bmi-calculator/`.
- Unverified attributions on `/ideal-weight/`, for its rebuild:
  - "more than 200 articles had cited them";
  - Hamwi as the source of the 10% frame rule elsewhere on the page;
  - "averaging gives a more robust estimate".
- `/blog/healthy-bmi-range/` still credits WHO with "overweight from 23, obese from 25" for Asian populations. That is the 2000 WHO Western Pacific / IASO proposal; the 2004 WHO consultation kept the international cut-offs. It is fixed in that page's rebuild (next after the homepage).
- At 320 px, the static tables on `/` and `/new-bmi-calculator/` are wider than the screen. This was already the case before this batch.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's DEVLOG step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-011-calc-results/`.
0.3 `git log --oneline -6 | grep -c "CMB-010"` → 1 or more. If 0, STOP: CMB-010 must run first.

### 1. Dry run
`python3 research/cmb-011-calc-results/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 2 new files, 21 replaced files, 0 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-011-calc-results/apply_build.py`
Must print exactly: `applied: 2 new files, 21 replaced files, 0 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass` (a `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure).
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `for f in $(git diff --name-only HEAD -- '*.html'); do python3 scripts/check_markup.py $f >/dev/null || echo "MARKUP FAIL $f"; done` → no output (12 files checked).
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 Each prints the number shown:
- `grep -o '&#10140;\|gradient\|genHealthRisks\|riskColor' assets/js/calculator.js | wc -l` → `0`
- `grep -o 'Method 2' ideal-weight/index.html | wc -l` → `0`
- `grep -o 'Rows 18' women-bmi-calculator/index.html | wc -l` → `0`
- `grep -o 'Limitation #2' blog/bmi-limitations/index.html | wc -l` → `2`
- `grep -o 'class="related-card"' blog/index.html | wc -l` → `26`
- `grep -o '"numberOfItems": 19' blog/index.html | wc -l` → `1`
- `grep -o 'Large: 155 lbs' ideal-weight/index.html | wc -l` → `1`
3.9 Browser, jsdom and detector checks: the box has none (DEVLOG §4) → record as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "fix: calculator results answer-first with readable colours, metric BMI in kg/m2, deletion leftovers on 9 pages, guides hub styled and complete, residue and results gates (CMB-011)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb011-dates.txt; echo $?; grep -c '^ok' /tmp/cmb011-dates.txt; grep '^BAD' /tmp/cmb011-dates.txt; rm /tmp/cmb011-dates.txt` → `0` and `40`.
- This holds when the commit date is 2026-10-14.
- On a later day, the 12 pages this batch changes report BAD by the day difference. Record the output; don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 7. REPORT
```
REPORT CMB-011 CALC-RESULTS
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-010 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <output or none> | 3.7 <exit> | 3.8 <n> <n> <n> <n> <n> <n> <n> | 3.9 skipped (no browser/jsdom in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
