# CMB-018 CHART-MEN — `/blog/bmi-chart-men/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-22 against GitHub `main` `dcd6b47` (after CMB-017). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/blog/bmi-chart-men/` owns 264 keywords worth 167,820/mo (`research/keyword-ledger.csv`), page 7 of the D-14 rollout:
  - "bmi chart for men" 40,500 (primary); "ideal weight for 5 10 male" 12,100; "bmi for men" 12,100; "male normal bmi" 8,100; "men height weight chart" 8,100;
  - per-height phrasings 65,770 in all, e.g. "normal weight 5 7 male" 8,100, "average weight for 5 11 male" 8,100, "average weight 5 6 male" 6,600, "healthy weight 6 foot male" 5,400, "healthy weight for 59 male" 4,400.
- **The old page broke site rules:**
  - thin: 717 words, one table, no figure, 4 FAQ with no FAQPage JSON-LD, the generic OG image, a byline with no author ("Reference chart · Not medical advice") (§5 [P1] G2 list);
  - a page-level `.bmi-chart` `<style>` with grey kilograms on the tints, 16 inline `style` attributes, arrow glyphs in links, "no numbers on this page are hand-authored", and a JSON-LD description that writes heights as `5'2'` and `6'6'` (§5 [P2]);
  - detector 2 findings at 390×844 (low contrast 2) and 11 at 1280×800 (line length 6, low contrast 5).
- **SERP (owner's pastes of google.com, US/English, 2026-10-22, not personalized):** "bmi chart for men", "ideal weight for 5 10 male" and "men height weight chart" return CDC's and NIH's calculators and tables, hospital charts and Reddit threads. Their 5′10″ answers disagree (132, 140, 144 or 149 lb at the bottom of the range), the AI Overview's height table is wrong at every row, and for 5′10″ it quotes "170 to 185 pounds", a range Reddit users favor. People also ask about 170, 180, 200, 215 and 140 lb at 5′10″, the correct weight for a height, height and age, a 5′9″ 70-year-old, "the new BMI chart for 2026" and the body type that lives longest. Gap: no result shows where US men actually fall on the chart, how often a high BMI is muscle, or what the June 2026 waist rule does for men. That is the wedge.

## What changes

### 1. `/blog/bmi-chart-men/` rebuilt (D-14, guide form)
- **Order:** H1 "BMI Chart for Men: Healthy Weight by Height" and the byline → three intro paragraphs → key takeaways (answer first) → disclaimer → hero figure → 8 contents chips → the chart → the 5′10″ answers → where US men fall → muscle or fat → waist and the 2026 ADA standards → age → 12 FAQ → sources and method → one related block.
- **The chart:** a `.weight-chart` table for every inch from 5′2″ to 6′6″ (17 rows, six CDC categories, whole pounds with whole kilograms below, each unit worked out on its own by the weight-table gate's rule, `#h-F-I` row links), plus a printable chart image (`assets/images/charts/bmi-chart-men.png`, 1640 × 1628: the BMI at every height and every 10 lb from 100 to 300 lb, linked to itself, listed in the image sitemap).
- **The wedge (CDC NHANES August 2021–August 2023, 2,680 men aged 20 and over, survey-weighted, 95% CIs):**
  - where US men fall: 24.0% have a healthy BMI, 35.7% are overweight and 39.2% have obesity (obesity and BMI 40+ equal NCHS Data Brief 508 for men at every age); at every height from 5′4″ to 6′2″, 64% to 81% have a BMI of 25 or more and both the median and the average man weigh more than the healthy range allows (the hero figure, and a by-height table of the healthy range, the average weight, equal to `/average-weight/`'s, and the share with a BMI of 25 or more); shares by age, each stated difference outside its margin of error;
  - the 5′10″ answers: the healthy range 129–173 lb; 11 weights with BMI, category and the share of US men with a higher BMI (the homepage's curve); US men of that height (313 men: 22.3% healthy, average 205.5 lb); why other answers differ (NIH's table starts at BMI 19, ideal-weight formulas, the online 170–185 lb);
  - muscle or fat: body fat on CDC's DXA scans (men 20–59, 2011–2018) by BMI category, and how often BMI and body fat disagree (11.8% of men with an overweight BMI carried no more body fat than the median healthy-BMI man; 14.0% of healthy-BMI men at least as much as the median overweight man); the body fat chart's numbers, asserted equal;
  - the waist: NHLBI's 40-inch line, NICE's waist-to-height classes and the June 2026 ADA thresholds; half the height is under 102 cm for any man shorter than 204 cm, so at an overweight BMI 93.7% of US men reach the ratio but 30.8% reach 102 cm; 73.4% meet the 2026 ADA thresholds against 39.5% of the same men by BMI alone;
  - age: one adult chart from 20 (CDC), the GBMC 2016 and Winter 2014 findings worded to their abstracts, the ADA's sentence on muscle loss.
- **FAQ:** 12 questions: the People-also-ask questions from the owner's pastes as asked, plus the ledger's 6-foot question. JSON-LD equals the visible text.
- **Head:** `<title>` "BMI Chart for Men: Healthy Weight by Height (lb and kg)" (55 characters); new meta, OG and Twitter text (heights with primes, no raw `"`); the preferred image (§2); JSON-LD Article (`dateModified` `{TODAY}`, author named, image list, `mainEntityOfPage` with `primaryImageOfPage`), BreadcrumbList and a new FAQPage. The page-level `<style>` and every inline style are gone.
- **Build record:** `research/chart-men-build/`:
  - `SPEC.md`;
  - `bcm_stats.py` → `bcm_stats.json`: stops unless the shares equal NCHS Data Brief 508 for men by age, `research/healthy-range-build/healthy_stats.json` and `research/bmi-chart-build/bc_stats.json`, and the by-height weights equal `research/average-weight/avgw_results.json`; stores 4 decimals and stops if storing would change a printed figure;
  - `bcm_dxa.py` → `bcm_dxa.json`: CDC's 2011–2018 DXA files (not in the repo); stops unless the percentiles equal `research/body-fat-chart-build/bfpc_stats.json`;
  - `chart_bcm.py` → the printable PNG and `bcm_grid.csv`; `gen_bcm.py`; `bcm_test_playwright.py`.

### 2. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/bmi-chart-men-{16x9,4x3,1x1}.png` (the height rows over the CDC bands with the men's bars and ticks), drawn by `research/preferred-images/pref_images.py` (new `men_chart` drawing; only this page's files are redrawn). Named in `og:image` (with `og:image:alt`), `twitter:image`, the Article image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`.
- `sitemap.xml`: the printable chart joins the page's entry as `<image:image>`.

### 3. Registry, page map, DESIGN.md
- `research/data-sources.csv`: no new rows; 14 rows list the page; notes added on 7 rows: `nhanes-2021-2023-exam-files` (the men's shares by age and height, waist and ADA), `nhanes-adult-obesity-2021-2023` (Data Brief 508's men's tables, re-read 2026-10-22), `nih-bmi-table-2022` (the 70-inch row and the "Normal" label, re-read 2026-10-22), `nhanes-2011-2018-dxa` (men's body fat by category and the disagree shares), `ada-2026-obesity-standards` (Table 3.1's inch lines: men ≥40 in, ≥35.5 in for an Asian background), `gbmc-2016-bmi-mortality` and `winter-2014-bmi-mortality-65` (abstracts re-read 2026-10-22).
- `research/page-map.csv`: the row's wedge, status and notes; `data_source` set to the registry domain `nhanes-2021-2023-exam-files`, so `check_sources.py` passes for this page (FAIL lines 30 → 29).
- `DESIGN.md`: "Distributions over the chart (CMB-018)" (the bar-and-tick rows over the category tints; box plots with a dashed reference line).

### 4. `styles.css`
- No change: the page uses existing components only (`.weight-chart`, `.data-table` with `.th-sub`, `.stat-callout`, `.figure--wide`, `.faq-list.flat`).

### 5. Dates, one number on `/bmi-chart/`, removals
- The page ships as a `{TODAY}` template (`"today": true`) for its schema `dateModified`; the sitemap `lastmod` is a `{TODAY}` edit, in the same edit that adds the image entry.
- One other page changes, by one number: `/bmi-chart/` gave the ADA's waist line for men of Asian background as "90 cm (35.4 in)"; the ADA's own Table 3.1 says 35.5 in (§6, F1). Edits make it "90 cm (35.5 in)", move the page's schema `dateModified` and sitemap `lastmod` to `{TODAY}`, and make its generator (`research/bmi-chart-build/gen_bc.py`) write the same line. No other page's text, links or JSON-LD change.
- Nothing is deleted. The old page used the shared `og-image.png`, which other pages still use.

### 6. Fixes from chat's checks and the independent fact-check
**Chat's own checks, fixed on the draft:**
- the age table was 356 px wide in its 310 px frame at 390: the "men measured" and "under 18.5" columns moved into the note under it;
- the hero's "260 lb" axis label ran past the figure edge (now anchored at the end); the dashed reference line of the body-fat figure crossed the row labels (now one short segment per row); a category dot wrapped onto its own line in the 5′10″ table (now kept with its word);
- the by-height table's ranges wrapped as "108–145 / lb" on phones: units moved into the column headers;
- one FAQ said a waist of at least half the height "points to fat rather than muscle" (no source says that); it now says where NICE's "increased" class starts. The takeaways now give the Asian-background line (23); the National DPP sentence says it is an eligibility criterion; the 5′9″ answer and the age section quote the ADA's muscle sentence as written;
- anti-slop: 9 fixes (staging 4, vague wording 4, repetition 1); rescored from the built HTML: 0 watch-word tells in 3,635 words, 1 em dash (inside the ADA document's title).

**Independent fact-check (separate agent, on the draft).** It rebuilt both samples from CDC's raw files with its own code (2,680 men 2021–2023; 5,383 men aged 20–59 with a valid 2011–2018 scan) and compared 189 printed figures: 185 matched, the 4 others are below. Everything else matched: all 102 chart cells and 17 cm labels by brute force with exact fractions; the 357 printable-chart values and every cell's color by pixel; the 44 hero bands and the bars and ticks in all 11 rows (within 0.25 lb); the box plot; NCHS Data Brief 508 for men 8/8 (fetched live); the 7 stated age differences (each 95% CI excludes 0; the 3 unstated ones include 0); by height 11/11 averages, BMI 25+ shares and n's, every lower bound above 50%; 5′10″ and 6′0″; the waist and ADA shares (73.4%, 39.5%, n 2,659, 30.9 points, 93.4%); the DXA percentiles and disagree shares; FAQ JSON-LD 12/12; all 33 quotes verbatim. Live sources re-read: CDC (adult and child categories with the March 19, 2024 date, About BMI, the formula), the NIH table PDF, NICE NG246, the ADA's section PDF and press release, CDC National DPP, GBMC 2016, Winter 2014. Findings, all settled before packaging:
- **FAIL, the ADA's inch lines (fixed).** The page paired the ADA's cm lines with its own conversions, "102 cm (40.2 in)" and "90 cm (35.4 in)", and the method said "the ADA uses 102 cm". The ADA's Table 3.1 gives the men's lines in inches as ≥40 in and, for an Asian background, ≥35.5 in (chat re-read the PDF). The page now says "102 cm (40 in)" and "90 cm (35.5 in)", the waist table's column is "Waist 102 cm or more" (the shares are computed in cm), and the method says "NHLBI gives the men's waist line as over 102 cm (over 40 in) and the ADA as 102 cm or more (40 in or more in its Table 3.1)". `/bmi-chart/` had the same "90 cm (35.4 in)" and is fixed by edits (§5). The registry's ADA row now records the table's inch lines (it held only the women's).
- **WARN, two "BMI alone" rates (fixed).** The intro and the FAQ compared 73.4% with "39.5% of the same men by BMI alone", five lines from the takeaways' 39.2% with obesity. Both are right: 39.5% is for the 2,659 men the ADA rule can class; 21 men with a BMI of 25.3–29.5 whose class depends on a waist that wasn't measured are left out. The intro, the FAQ and the callout now say "the same 2,659 men", and the FAQ and the method say who is left out.
- **WARN, one rank (disclosed).** The 5′10″ table shows 79% of US men with a higher BMI than 170 lb (BMI 24.4); the exact weighted share is 78.4%. The column reads the curve the homepage and men's calculators use, so it matches what they show (the other 10 rows agree both ways). The note under the table now says so and that the exact share can differ by a point after rounding; the header says "All US men with a higher BMI" (it compares with men of every height). The [P3] 4-decimal curves item stays.
- **NOTEs taken.** The method says how the median BMI is read (the homepage's curve), that the ADA's Asian-background lines apply to the men CDC records as non-Hispanic Asian, and which men lack a valid scan (18.7%, 18.2% and 26.1% of men with a healthy, overweight and obesity BMI, now computed in `bcm_dxa.py`); "2011–2018" joins the body-fat takeaway, FAQ and section; GBMC's never-smokers are "without certain chronic diseases" (the abstract: "without specific chronic diseases"); the takeaway says "Most men with an overweight BMI carry more body fat than the typical man with a healthy BMI" and "a high BMI from muscle is real but uncommon" is gone (the scans compare different men, not where one man's weight comes from); the OG description and OG image alt match what the page shows; the hero description says "6 feet" and "6 feet 1 inch"; the printable chart's alt says "every 10 pounds".
- **NOTEs kept.** The weight-table rule (BMI rounded to one decimal, CMB-008; NIH's table also puts 174 lb under BMI 25 and 209 under 30 at 70 in); "more than 99%" for a share of 100.0% (DESIGN.md rule); "most men at every height" holds height by height, as written; percentiles at tied values depend on sort order: the 5′11″ lower quartile prints 182.7 (the `/average-weight/` file's value) where a stable sort gives 182.9 (logged for CMB-019).
- **Not reachable for the agent:** NHLBI's 1998 chapter (NBK2004; the registry's reading stands, and the 2001 summary partly supports "mainly at a BMI of 25 to 34.9"), the NHANES documentation pages, the NCHS Series 3 median.

### Chat results (fresh GitHub clone of `dcd6b47` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-24` and commit dates set to that day. Both runs: dry-run and apply `14 / 6 / 6 / 0`; gates 3.1–3.9 pass; 3.10 `0 1 1 1 12 0 3 17 1 21 1 1 1 1 1 0 29`; 3.11 `same`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **3.11 in chat:** `bcm_stats.py` on CDC's raw DEMO_L and BMX_L files rebuilds `bcm_stats.json` byte for byte (it stops unless the shares equal NCHS Data Brief 508, `healthy_stats.json` and `bc_stats.json`, and the by-height weights equal `avgw_results.json`); `bcm_dxa.py` on CDC's 2011–2018 DEMO, BMX and DXX files rebuilds `bcm_dxa.json` byte for byte (it stops unless the percentiles equal `bfpc_stats.json`); `chart_bcm.py` redraws the printable chart pixel for pixel.
- **Browser checks (Chromium):**
  - `bcm_test_playwright.py` on the applied clone: 921 checks, 0 failures. It covers all 102 chart cells by brute force and the 17 row links; the printable chart's 357 values from `bcm_grid.csv`, its size, alt text, link, lazy load and image-sitemap entry; the by-height table (brute-force healthy limits, the `/average-weight/` means, the BMI 25+ shares), the 5′10″ table (BMI, category and the rank rule worked out again, with values typed in), the age and waist tables against the stats; the hero's bands, bars and ticks at their drawn positions, and the box plot at `bcm_dxa.json`'s percentiles (equal to `bfpc_stats.json`); 48 sentences that state numbers, rebuilt from the stats files; the fact-check's fixes (no "40.2 in", "35.4 in", "BMI from muscle" or "6 feet 1 inches"); head, OG/Twitter, the JSON-LD and the preferred images at size, `dateModified` = the sitemap `lastmod`; every internal link answers 200 and every outside link is a registry URL; 8 chips and 12 FAQ with JSON-LD equal to the visible text; no page wider than 320, 360, 390 or 1280; tables inside their frames (the chart table scrolls inside its frame on phones); no SVG label collisions or labels on shapes; no JavaScript error. Four deliberate breaks on a copy of the page (one chart cell, one age-table cell, one hero tick, one FAQ answer) each failed the test.
  - `bc_test_playwright.py` (`/bmi-chart/`, after the 35.5 in edit) on the applied clone: 1,086 checks, 0 failures.
  - On chat's work tree (identical to the clone): calculator jsdom 95/95; calculator end-to-end 1,316 checks, 0 failures; FAQ opens on all 26 pages that have one; no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Detector (impeccable 0.1.14):** this page 2 → 0 at 390×844 and 11 → 0 at 1280×800; `/bmi-chart/` stays 0. Sitewide static 283 → 281 at 390×844, only this page changed (`research/impeccable-baseline/2026-10-22-cmb018-390x844.json`); with results open the 8 calculators stay at 88 (no calculator changed).
- **Live R4 (owner):** the detector on production `/women-bmi-calculator/` printed only the consent-banner note, so 0 findings. That closes CMB-017's open item.

### Not in this batch (logged for §5)
- Percentiles at tied values depend on sort order in `research/average-weight/compute.py`'s weighted quantiles (the fact-check: the 5′11″ lower quartile is 182.7 or 182.9 by tie order; no other printed value moves today). `/average-weight/` is CMB-019: make the quantiles order-free there and regenerate this page's hero in the same batch (its quartiles are asserted equal to that file).
- ADA waist inches: `/women-bmi-calculator/` states the ADA's women's line as "88 cm (34.6 in)", its own conversion (the calculator compares in cm); the ADA's Table 3.1 says 35 in. Settle one convention sitewide (the ADA's table inches next to a threshold, exact conversions only next to our computed shares) when that page next changes.
- The rank curves stored at 2 decimals ([P3], CMB-017) also feed this page's 5′10″ column.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-018-chart-men/`.
0.3 `git log --oneline -4 | grep -c "CMB-017"` → 1 or more. If 0, STOP: CMB-017 must run first.

### 1. Dry run
`python3 research/cmb-018-chart-men/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 14 new files, 6 replaced files, 6 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-018-chart-men/apply_build.py`
Must print exactly: `applied: 14 new files, 6 replaced files, 6 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py blog/bmi-chart-men/index.html bmi-chart/index.html` → `blog/bmi-chart-men/index.html: 0 issues` and `bmi-chart/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py blog/bmi-chart-men/index.html bmi-chart/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `blog/bmi-chart-men/index.html`):
- `grep -o '{TODAY}' $PG | wc -l` → `0`
- `grep -o "blog/bmi-chart-men/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o '<image:loc>https://calculatemybmi.net/assets/images/charts/bmi-chart-men.png</image:loc>' sitemap.xml | wc -l` → `1`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $PG | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `12`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o 'application/ld+json' $PG | wc -l` → `3`
- `grep -o 'id="h-' $PG | wc -l` → `17`
- `grep -o 'max-image-preview:large' $PG | wc -l` → `1`
- `ls assets/images/preferred/ | wc -l` → `21`
- `grep -o "'/blog/bmi-chart-men/': 'bmi-chart-men'" scripts/check_images.py | wc -l` → `1`
- `grep -c 'Distributions over the chart (CMB-018)' DESIGN.md` → `1`
- `grep -o '90 cm (35.5 in)' bmi-chart/index.html | wc -l` → `1`
- `grep -o "\"dateModified\": \"$(date +%F)\"" bmi-chart/index.html | wc -l` → `1`
- `grep -o "net/bmi-chart/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'blog/bmi-chart-men'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `29`
3.11 Reproducing `bcm_stats.json` needs pandas (the raw files are in `research/average-weight/raw/`). If `python3 -c "import pandas"` fails, record `skipped (no pandas)`; chat ran it (see Chat results). Otherwise run `python3 research/chart-men-build/bcm_stats.py research/average-weight/raw research/healthy-range-build/healthy_stats.json research/bmi-chart-build/bc_stats.json research/average-weight/avgw_results.json /tmp/bcm_check.json > /dev/null && cmp /tmp/bcm_check.json research/chart-men-build/bcm_stats.json && echo same; rm -f /tmp/bcm_check.json` → `same`. (`bcm_dxa.json` needs CDC's 2011–2018 DXA files, which are not in the repo; chat rebuilt it byte for byte.)
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /blog/bmi-chart-men/ rebuilt to the D-14 pattern: where US men fall on the chart by height and age (NHANES 2021-2023), the 5'10\" answers, body fat at the same BMI (CDC DXA), waist and the 2026 ADA thresholds; printable chart image in the image sitemap; preferred images (CMB-018)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb018-dates.txt; echo $?; grep -c '^ok' /tmp/cmb018-dates.txt; grep '^BAD' /tmp/cmb018-dates.txt; rm /tmp/cmb018-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-018 CHART-MEN
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-017 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 <same or skipped (no pandas)> | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines: <none or list>
devlog: <git log --oneline -1>
git status: <clean or list>
```
