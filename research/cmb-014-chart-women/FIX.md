# CMB-014 CHART-WOMEN — `/blog/bmi-chart-women/` rebuilt to the D-14 pattern, with where US women fall on the chart and what waist size adds at the same BMI

Built and tested in chat on 2026-10-15 against GitHub `main` `e63e2e1` (after CMB-013). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are fixed below (§6).

## Why
- **Demand.** The page owns 603 keywords worth 390,030/mo (`research/keyword-ledger.csv`), the largest page left in the D-14 rollout (#3):
  - "bmi chart female" 74,000 (primary), "chart bmi female" 27,100, "female weight chart" 14,800, "female weight table" 12,100;
  - per-height "healthy / normal weight 5′X woman" queries, 151,210 in all ("healthy weight 54 female" 14,800, "normal weight 5 6 woman" 12,100, "normal weight for 5 7 woman" 12,100);
  - "bmi for women" 22,200; "average weight 5 2 woman" 14,800; ideal weight by height 21,510; age 9,150.
- **The old page broke site rules:**
  - Thin (1,295 words), no figure, the generic `og-image.png`, and a byline with no author ("Reference chart · Not medical advice").
  - Winter 2014 written as "lowest across a somewhat higher BMI range (roughly 23 to 33)" (backlog P2 list).
  - "Discuss your target with a healthcare provider": an unsourced see-a-doctor line, and a target (§4, D-06).
  - Arrow glyphs in links, inline-styled boxes, "no numbers on this page are hand-authored".
  - A page-level `<style>` block with grey kilograms on the category tints (low contrast).
  - Meta, OG and Twitter descriptions cut short by an unescaped `"` (`4'10"`), which ended the attribute.
  - Detector: 2 findings at 390×844 and 11 at 1280×800.
- **SERP (owner's pastes of google.com in English, 2026-10-15, "Results are not personalized"):**
  - "bmi chart female": an image pack first (Verywell, Ramsay, Harvard Health, Eat Smart Move More NC, BHF, Medical News Today, Business Insider, Calculator.net, Alamy, American Cancer Society), then CDC's Adult BMI Calculator and NIH's printable BMI table. The AI Overview lists healthy weights read from NIH's BMI 19 and 24 columns (5′4″: 110–140 lb) under an 18.5–24.9 label.
  - "bmi for women": AI Overview with the categories, the formulas, a waist of 35 in or more, and pregnancy.
  - "healthy weight 5'4 female": AI Overview 108–145 lb (matches this chart); Reddit threads; Rush, Banner and Verywell tables.
  - People also ask (all used, as asked): the 5′4″ weight question (on all three pages, asked three ways), "What is the new BMI chart for 2026?" (two pages), "What is a healthy BMI for a female?", "Is a 23 BMI chubby?", "What is the correct BMI for my age as a female?", "What is an acceptable BMI for a 70 year old female?", "Is 140 pounds fat for a 5'4" female?", "Is 5'4" 125 pounds skinny?", "What is considered morbidly obese for a 5'4" female?".
  - Gap: every result repeats the CDC table or a whole-number BMI grid. None shows where US women actually fall on the chart, what waist size adds at the same BMI, or the June 2026 ADA standards.

## What changes

### 1. `/blog/bmi-chart-women/` rebuilt (D-14, guide form)
- **Order:**
  1. H1 "BMI Chart for Women: Healthy Weight by Height" and the byline.
  2. Three intro paragraphs: the searcher's questions, the stakes (28.1% of US women in the range; the 2026 ADA thresholds), the promise.
  3. Key takeaways, opening with a 53-word answer.
  4. Disclaimer.
  5. Hero figure.
  6. Contents chips (9).
  7. Seven sections: the chart, how to read it, why other charts differ, US women, waist, age, pregnancy.
  8. FAQ, then sources and method, then one related block.
- **Hero figure:** one bar per height from 4′10″ to 6′0″, split where the weight in pounds crosses each CDC category line; 5′4″ outlined.
- **The chart:**
  - Every inch from 4′10″ to 6′0″ (15 rows) by six CDC categories, pounds with kilograms below, each unit worked out on its own. The `#h-5-4` row links are kept.
  - The 90 cells use the gate's range forms, so `check_weight_tables.py` checks every one through the 40/40 gate (a wrong cell fails it; tested).
  - A printable chart image, `assets/images/charts/bmi-chart-women.png` (1360 × 1492): the BMI at every height and at 90 to 250 lb in 10 lb steps, kilograms to one decimal in the header, cells coloured by category. It is an `<img>` with alt text, width and height, linked to itself for printing, so image search can index it (the SERP opens with an image pack).
- **How to read it:** three steps and a worked example (5′5″, 160 lb: BMI 26.6, overweight, 11 lb above the healthy range).
- **Why other charts differ:** NIH's printable table has one column per whole BMI from 19 to 54, so at 5′4″ it reads 110 to 140 lb; CDC's 18.5 to 24.9 gives 108 to 145 lb. Rounding and "ideal weight" formulas explain the rest.
- **The wedge, part 1: US women by BMI category and age.**
  - 28.1% healthy (95% CI 24.3–31.8%), 28.6% overweight, 41.3% obesity, 12.1% at 40 or more; median BMI 28.3.
  - By age: healthy 33.8% / 23.9% / 26.5% at 20–39 / 40–59 / 60+; obesity 36.8% / 47.4% / 39.6%; class 3 13.0% / 14.7% / 8.4%.
  - Our calculation from CDC NHANES 2021–2023 (3,249 women), matching NCHS Data Brief 508 for women at every age.
  - The text states only age differences whose 95% CI excludes zero (healthy 20–39 vs the other two groups; obesity 40–59 vs the other two; class 3 at 60+ vs the other two).
- **The wedge, part 2: waist at the same BMI.**
  - NHLBI's waist line and NICE's waist-to-height bands, with sources.
  - Among US women with a healthy BMI, 16.8% have a waist of 88 cm (34.6 in) or more and 50.2% a waist at least half their height; at an overweight BMI 79.1% and 95.5%.
  - The June 2026 ADA Standards of Care in Overweight and Obesity (recommendations 3.3a and 3.3b, non-Asian and Asian thresholds) applied to the same women: 69.4% meet the obesity thresholds against 41.8% by BMI alone; 24.9 points of the gap come from non-Asian women with a BMI of 25 to 29.9.
  - Body fat by BMI band for women aged 20 to 59 (CDC DXA scans, our analysis): 33.4% / 39.5% / 44.0%.
- **Age:** CDC's categories at every adult age; body fat (Gallagher 2000); muscle (the ADA's full sentence on older adults); the GBMC age gradient (women and men combined) and Winter 2014, both worded as associations; children read as percentiles.
- **Pregnancy:** CDC's recommended weight gain by BMI before pregnancy (Institute of Medicine), one baby, in lb with kg conversions.
- **FAQ:** 11 questions: the 9 People-also-ask questions above, as asked, most frequent first, then the ledger's "average weight 5 2 woman" (linking `/average-weight/`) and "5 3 ideal weight woman" (linking `/ideal-weight/`). The JSON-LD equals the visible text.
- **Head:**
  - `<title>` "BMI Chart for Women: Healthy Weight by Height (lb and kg)" (57 characters), with new meta, OG and Twitter text. The new description has no unescaped quote.
  - New OG image `assets/images/og/bmi-chart-women.png`, showing the chart's bands and the 5′4″ healthy weight.
  - Article JSON-LD gets the H1 as headline, the description, both images and `dateModified`. BreadcrumbList's page name becomes the H1. FAQPage is added.
  - The page-level `<style>` block is removed (see §2).
- **Build record:** `research/chart-women-build/`:
  - `SPEC.md`;
  - `bcw_stats.py` → `bcw_stats.json`, which stops unless it reproduces NCHS's rates for women at every age and CMB-013's healthy shares;
  - `gen_bcw.py`, `chart_bcw.py` (with `bcw_grid.csv`, the values drawn in the image), `og_bcw.py` and `bcw_test_playwright.py`.

### 2. Chart-table component: `.weight-chart` (`styles.css`, `DESIGN.md`)
- Category tints as on `/bmi-chart/`, with text tinted from each cell's hue (5.2:1 or better), white hairlines between cells, and the height column kept in view while the table scrolls sideways on phones. A targeted row (`#h-5-4`) gets a bar in the link colour.
- `min-width: 600px`: the table fits the 680 px reading column on desktop and scrolls inside its frame on phones. Header ranges wrap only between words.
- `.figure--wide` (680 px) and `.figure img` for the printable chart. Print rules drop the table's minimum width.
- New classes only; no other page uses them, so no other page changes. `/bmi-chart/` and `/blog/bmi-chart-men/` keep their page-level `.bmi-chart` styles until their rebuilds.

### 3. Registry and page map
- `research/data-sources.csv`: 3 verified rows, checked 2026-10-15 (34 → 37 rows):
  - `ada-2026-obesity-standards`;
  - `cdc-pregnancy-weight-gain`;
  - `nih-bmi-table-2022`.
- 12 existing rows now list `blog/bmi-chart-women`. Notes are added on `nhanes-2021-2023-exam-files`, `nhanes-adult-obesity-2021-2023`, `nice-ng246-ethnicity-thresholds`, `nhanes-2011-2018-dxa` and `cdc-adult-bmi-categories`.
- `research/page-map.csv`:
  - the row is built, with `data_source` `nhanes-2021-2023-exam-files`;
  - the data-sourcing check passes for this page;
  - 32 other rows still fail on free-text `data_source` (33 before).

### 4. Dates
- The page ships as a `{TODAY}` template (`"today": true`), for its schema `dateModified`. Its sitemap `lastmod` is a `{TODAY}` edit. Same mechanism as CMB-013.

### 5. Head-tag fix on two sibling chart pages (`/bmi-chart/`, `/blog/bmi-chart-men/`)
- Their meta, OG and Twitter descriptions had the same unescaped `"` (`4'10"`, `5'2"`), so search engines and social cards got a description cut off after the first height. Six edits write the heights with primes (`4′10″`); the wording is otherwise unchanged.
- Head tags only: no text inside `<main>` and no JSON-LD changes, so neither page's dates move.

### 6. Fixes from the independent fact-check (separate agent, on the draft)
No FAIL. It recomputed about 85 survey figures from the raw NHANES files, all 90 chart cells and all 255 printable-chart values, and checked about 45 external claims in 14 sources; all matched. Its 6 warnings and 10 of its 11 notes were fixed (the eleventh, the 5′2″ average's ±11 lb margin, needs no change: "above the healthy range" holds at its lower bound):
- The waist share is labelled with the line it uses: 88 cm (34.6 in), not "35 in".
- The 69.4% carries "(our calculation)" wherever it appears, and the comparison always uses 41.8% of the same women; the gap's size is no longer stated next to rounded figures.
- "Is a 23 BMI chubby?" and "Is 140 pounds fat …?" open with "Not by CDC's categories" and give the ADA's Asian thresholds.
- The ADA sentence on older adults is quoted in full ("…which may lead to underdiagnosis of obesity").
- The printable chart's kilogram header shows the exact conversion to one decimal (63.5, not 64).
- The takeaway and FAQ say the 69.4% applies the ADA's thresholds for Asian women too; "how obesity is diagnosed" became "the ADA's definition of obesity".
- GBMC's age figures are marked "women and men combined"; weight ranges are no longer attributed to CDC (CDC publishes the BMI range).
- The National DPP line reads as an eligibility criterion; NICE NG246 is dated 2025 with its 2022 recommendation; the kg limits are for the exact height in inches (noted under the chart); the DXA period (2011–2018) is given; "demographics and body measures files".
- The chart table uses primes for heights, like the rest of the page.

### Chat results (fresh GitHub clone of `e63e2e1` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-17` and commit dates set to that day. Both runs: dry-run and apply `11 / 5 / 7 / 0`; gates 3.1–3.8 pass; 3.9 `0 1 1 11 0 1 0 0 1 0 32 0 0`; 3.10 `same`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **Browser checks (Chromium, on the applied clone served locally):**
  - `bcw_test_playwright.py`: 604 checks, 0 failures. It covers all 90 chart cells by brute force and the 15 row links; the printable chart's 255 values (`bcw_grid.csv`), its size, alt text and link; the US women and pregnancy tables; the figure labels; 9 chips and 11 FAQ; JSON-LD against the visible text, the H1 as headline and breadcrumb; SVG label collisions at 390 and 1280; widths at 320, 360, 390 and 1280, with the chart table fitting the column on desktop and scrolling inside its frame on phones. A planted wrong cell and a wrong share both fail it.
  - Calculator jsdom 95/95; calculator end-to-end 1,316 checks, 0 failures.
  - FAQ opens on all 25 pages that have one; no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Detector (impeccable 0.1.14):** this guide 2 → 0 at 390×844 and 11 → 0 at 1280×800. `/bmi-chart/` (4) and `/blog/bmi-chart-men/` (2) are unchanged by their head edits; `/` stays at 0. Sitewide static 313 → 311 at 390×844, no page worse (`research/impeccable-baseline/2026-10-15-cmb014-390x844.json`).
- **Live R4 (owner, 2026-10-15):** the detector on production `/blog/healthy-bmi-range/` printed only the consent-banner note, so 0 findings. That closes CMB-013's open item.
- **Anti-slop:** 5 fixes (staging 3, re-explaining 1, passive voice 1).

### Not in this batch (logged for §5)
- `/bmi-chart/` and `/blog/bmi-chart-men/` still carry the page-level `.bmi-chart` `<style>` with grey kilograms on the tints (the detector's low-contrast findings on both). Their JSON-LD descriptions write heights as `4'10'` and `5'2'`. Move both pages to `.weight-chart` and fix the JSON-LD in their D-14 rebuilds (`/bmi-chart/` is next).
- `/blog/bmi-chart-men/` has the same old-page leftovers this page had: arrow glyphs in links and "no numbers on this page are hand-authored".
- `/women-bmi-calculator/` answers "What is a healthy BMI for women?" in its FAQ; this page now answers "What is a healthy BMI for a female?" as asked in the SERP. Settle which page carries it in the calculator's D-14 rebuild.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-014-chart-women/`.
0.3 `git log --oneline -4 | grep -c "CMB-013"` → 1 or more. If 0, STOP: CMB-013 must run first.

### 1. Dry run
`python3 research/cmb-014-chart-women/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 11 new files, 5 replaced files, 7 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-014-chart-women/apply_build.py`
Must print exactly: `applied: 11 new files, 5 replaced files, 7 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py blog/bmi-chart-women/index.html` → `blog/bmi-chart-women/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py blog/bmi-chart-women/index.html; echo $?` → only `0`.
3.9 Each command prints the number shown:
- `grep -o '{TODAY}' blog/bmi-chart-women/index.html | wc -l` → `0`
- `grep -o "\"dateModified\": \"$(date +%F)\"" blog/bmi-chart-women/index.html | wc -l` → `1`
- `grep -o "<loc>https://calculatemybmi.net/blog/bmi-chart-women/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o 'class="faq-question"' blog/bmi-chart-women/index.html | wc -l` → `11`
- `grep -o 'og-image.png' blog/bmi-chart-women/index.html | wc -l` → `0`
- `ls assets/images/charts/ | grep -c '^bmi-chart-women.png$'` → `1`
- `grep -o '<style>' blog/bmi-chart-women/index.html | wc -l` → `0`
- `grep -o -i 'somewhat higher BMI range\|hand-authored\|Discuss your target\|&larr;\|&rarr;\|←\|→' blog/bmi-chart-women/index.html | wc -l` → `0`
- `grep -o '.weight-chart .c-healthy' assets/css/styles.css | wc -l` → `1`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "blog/bmi-chart-women"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `32`
- `grep -o "content=\"[^\"]*4'10\"" bmi-chart/index.html | wc -l` → `0`
- `grep -o "content=\"[^\"]*5'2\"" blog/bmi-chart-men/index.html | wc -l` → `0`
3.10 If `python3 -c "import pandas"` succeeds, run:
`python3 research/chart-women-build/bcw_stats.py research/average-weight/raw research/healthy-range-build/healthy_stats.json /tmp/cmb014-stats.json >/dev/null && cmp /tmp/cmb014-stats.json research/chart-women-build/bcw_stats.json && echo same; rm -f /tmp/cmb014-stats.json`
It must print `same`. Without pandas, record `skipped (no pandas)`.
3.11 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /blog/bmi-chart-women/ rebuilt to the D-14 pattern with US women by BMI category and age, waist at the same BMI and the 2026 ADA thresholds (NHANES 2021-2023); printable chart image; .weight-chart table; head-tag fix on /bmi-chart/ and /blog/bmi-chart-men/ (CMB-014)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb014-dates.txt; echo $?; grep -c '^ok' /tmp/cmb014-dates.txt; grep '^BAD' /tmp/cmb014-dates.txt; rm /tmp/cmb014-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-014 CHART-WOMEN
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-013 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.10 <same or skipped> | 3.11 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
