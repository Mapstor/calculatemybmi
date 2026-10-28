# CMB-020 BODY-FAT-CALC — `/body-fat-calculator/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-28 against GitHub `main` `f365b8b` (after CMB-019). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/body-fat-calculator/` owns 329 keywords worth 147,710/mo (`research/keyword-ledger.csv`), page 9 of the D-14 rollout:
  - "body fat calculator" 74,000 (primary); "bfp calculator" 40,500 (KWP's group for "body fat percentage calculator"); "body fat calculator online" 4,400; "fat calc" 2,900; "bf calculator" 1,900;
  - the methods ("bodyfat calculator caliper" 1,000, "7 site skinfold calculator" 320, "3 site skinfold calculator" 260, "body fat calculator height weight" 170, "relative fat mass calculator" 70), accuracy ("most accurate body fat calculator" 390, "accurate body fat calculator" 170), sex ("body fat calculator female" 1,000, "male" 720) and fat mass ("body fat weight calculator" 210, "fat mass calculator" 170).
  - Ledger owners elsewhere: Army and Navy standards → the planned army- and navy-body-fat-calculator pages; healthy and ideal ranges → `/body-fat-percentage-chart/`; measuring at home, calipers and scales → `/blog/how-to-measure-body-fat/`.
- **The old page broke site rules:** three page-level `<style>` blocks, inline styles in `<main>` (the breadcrumb, byline and container), one `<article>` wrapper, the FAQ as `<details>`/`h3` with no FAQPage JSON-LD, Organization and Person nodes in the page graph, a text OG card (`og-body-fat-calculator.png`), and a menu that marked "Obesity Statistics" as the current page (its shell came from `/us-obesity-statistics/`). Detector: 9 findings at 390×844 (low contrast 4, undersized UI text 3, side tab 2), 19 at 1280×800 (plus line length 10).
- **SERP (owner's pastes of google.com, US/English, 2026-10-28, not personalized):** "body fat calculator", "body fat percentage calculator" and "body fat calculator female" return calculators that print a number from the Navy tape method, BMI or skinfolds and stop there. None says how close that number is likely to be. That is the wedge.

## What changes

### 1. `/body-fat-calculator/` rebuilt (D-14, calculator form)
- **Order:** H1 "Body Fat Calculator" and the byline → a one-line intro and the source note → the calculator → key takeaways → disclaimer → 9 contents chips → how to read your result (the worked example and its figure) → how accurate is each method → tape measure → waist and height → height and weight → calipers → what your result means → 9 FAQ → sources and method → one related block. No `<article>` wrapper (D-16), no page-level style, no inline style in `<main>`.
- **The calculator** (shared parts, `.calculator-card.bfc`): woman / man, US / metric, four methods (tape measure = the Navy equations; waist and height = relative fat mass, Woolcott & Bergman 2018; height and weight = the Deurenberg formula; calipers = Jackson–Pollock 3 or 7 sites with Siri). Answer first: the estimate on a card tinted by the provisional range (Gallagher et al., 2000), then how close the method is likely to be, where the estimate falls among US adults of the same sex and age group (the `/body-fat-percentage-chart/` figure and data), fat and lean mass from the weight, the other estimates the entered numbers allow, and the source line. The notes say what each check can and can't tell (CDC's measurements were taken by trained technicians; the US share and the range treat the estimate as a scan reading). The US / Metric switch converts to 0.1 and restores the numbers when switched back, so flipping units never changes a result.
- **The wedge (our calculation from CDC NHANES 2011–2018 DXA scans of 10,864 adults aged 20 to 59, survey-weighted, 95% CIs):**
  - waist and height came within 5 points of the scan for 74.3% of women and 86.3% of men, height and weight for 62.4% and 66.4%; in the same people that is 12 more women and 20 more men in every 100; typical miss 3.5 / 2.7 against 4.7 / 4.2 points (all four differences' CIs exclude zero);
  - waist and height reads high (+2.3 women, +0.7 men on average; its median error, +2.3 and +0.8, against its authors' 2005–2006 medians of 0.9 and 0.5: clearly higher for women, not clearly different for men); height and weight is right on average (−0.2 and −0.1, within the margin of error) only because it reads 3.1 / 2.9 low at a healthy BMI and 4.1 / 2.9 high with obesity, about 2 low under 40 and 2 high from 40 to 59;
  - for any estimate from those two formulas, the calculator shows the middle half and median of the scans of US adults whose formula gave about the same estimate (within a point of the same whole percent, 30 or more people);
  - the tape measure and calipers can't be checked on CDC's data (no neck or skinfolds), so the page cites published DXA comparisons: 6.0 points low in 1,407 Army recruits (Foulis et al., 2023), seven-site skinfolds 1.4 points below DXA in 437 college students, with the lowest average miss of seven methods (MAPE 11.7%; Burns et al., 2019).
- **FAQ:** 9 questions, the ledger's calculator-owned queries as questions: most accurate, height and weight, relative fat mass, where to measure the waist, 3-site vs 7-site, pounds of fat, women, teenagers, centimeters. JSON-LD equals the visible text.
- **Head:** title "Body Fat Calculator: 4 Methods Compared With DXA Scans"; new meta description, OG and Twitter text (with `twitter:title` and `twitter:description`; the description says CDC's scans checked two formulas and published studies the tape and calipers); the preferred image (§3); JSON-LD `@graph`: WebPage (`dateModified` `{TODAY}`, author, `primaryImageOfPage`), WebApplication `#calculator` (image list, featureList, author), BreadcrumbList, FAQPage. The menu now marks Body Fat as the current page.
- **Build record:** `research/body-fat-calculator-build/`: `SPEC.md`; `bfc_stats.py` and `bfc_stats.json` (the check on CDC's scans; asserts its sample equals `bfpc_stats.json`); `gen_bfcalc.py` (writes the page; stops unless every printed figure equals the stats or a source value typed in, every outside link is a registry URL and no figure label collides); `bfcalc_test_playwright.py`.

### 2. `/body-fat-percentage-chart/`: the rank tool's figure
- The "You 30%" label sat 0.5–0.9 px above the tool's figure, so its top was clipped. Every mark moves 2 units down and the figure is 88 units tall (the CMB-019 `/average-weight/` fix). One edit on the page's script; `research/body-fat-chart-build/gen_bfpc.py` gets the same change so it still rebuilds the page. No visible text, link or JSON-LD changes, so no date moves.

### 3. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/body-fat-calculator-{16x9,4x3,1x1}.png` (the accuracy figure: formula minus scan for both formulas and both sexes on a dashed zero line, no words or numbers), drawn by `research/preferred-images/pref_images.py` (new `bf_calc` drawing). Named in `og:image` (with `og:image:alt`), `twitter:image`, the WebApplication image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`.
- Deleted: `body-fat-calculator/og-body-fat-calculator.png` (the old text card; only this page used it).

### 4. Registry, page map, DESIGN.md, styles.css
- `research/data-sources.csv`: 3 new rows, read in chat 2026-10-28: `rfm-woolcott-2018` (the formula, the waist site, the development and validation samples, the scanner, the validation bias; Cedars-Sinai's measuring note), `foulis-2023-circumference-dxa` (the tape method against DXA in Army recruits), `army-tape-worksheets` (DA Forms 5500 and 5501: where to measure). `body-fat-calculator` added to `pages_served` of `nhanes-2011-2018-dxa`, `gallagher-2000-bf-ranges` and `body-fat-method-validation`; notes on `body-fat-equations` (JP7 coefficients and sites, the Deurenberg abstract re-read, Topend Sports added to its endpoints: it prints the JP coefficients the page uses), `body-fat-method-validation` (Burns: seven sites, Siri, N, Table 3's sign: skinfolds read 1.4 below DXA) and `nhanes-2011-2018-dxa` (the CMB-020 check, exact ties, the percentile rule, CDC's "trained health technicians"); `rfm-woolcott-2018` carries Table 2's CIs and our median CIs, `army-tape-worksheets` Army Directive 2023-11.
- `research/page-map.csv`: the row's wedge and notes (`data_source` stays `body-fat-equations`).
- `DESIGN.md`: "Body fat calculator (CMB-020)" (the parts, the answer-first results, the notes on what each check can tell, the unit switch that round-trips).
- `assets/css/styles.css`: `.bfc` shares the body fat rank tool's three size rules (selectors added to the CMB-016 lines); `.bfc [hidden]`; `.bfc-toggles` (sex and units side by side, stacked under 360 px); `.unit-toggle--methods` (four options, two rows on phones); `.form-row--trio` (three measurements in a row, two under 360 px); `.bfc .form-hint`; and, below 600 px, 8 px beside the text of a table heading row that spans its columns. No other page uses these classes.

### 5. Dates
- The page ships as a `{TODAY}` template (`"today": true`) for its WebPage `dateModified`; its sitemap `lastmod` is a `{TODAY}` edit. `/body-fat-percentage-chart/` keeps its dates (§2 changes no visible text).

### 6. Fixes from chat's checks and the independent fact-check
**Chat's own checks, fixed on the draft:**
- four tables overflowed a 390 px phone (the four-methods table cut off its last column; the two-formula tables and the ranges table were 316–350 px in a 310 px frame): the four methods became a list, each formula got its own three-column table (overall, then by BMI and age), and the ranges became one table per sex with the ranges as rows; the results' other-estimates table puts each method's check under its name. All tables fit at 320, 360, 390 and 1280;
- the accuracy figure's dashed zero line crossed the row labels: it is drawn row by row now;
- the tool figure's "You" label sat 0.5 px above the figure (as on the chart page, §2): marks 2 units down, figure 88 tall;
- the detector flagged 6 px beside the text of the tables' spanning heading rows on phones: 8 px (styles.css);
- facts: "the closest of the seven methods" was wrong (Burns: hydrostatic weighing had the smaller mean difference, 1.0); skinfolds had the lowest average error (MAPE 11.7%), which the page now says; "so a scan could well read higher" (an inference from a recruit study) cut; "just past the line" → "the high range starts at 33%"; the note on margins of error names the group rows and the overall averages separately;
- wording: "colours" (US English site) → "tints"; the women's hip site follows the Army worksheet ("where the buttocks stick out most"); a weight prints as entered ("150 lb", not "150.0 lb"); the units toggle reads "US / Metric" so both toggles share a row on phones;
- anti-slop: 12 fixes (staging 3: three "estimates, not measures" constructions stated plainly, the FAQ answer leading with the finding; rhythm 5: one run-on split, a dramatic fragment merged, four repeated "How close it gets:" openings varied; repetition 2: authors named twice in one sentence; style 2); rescored from the built HTML: 0 tells and 0 em dashes in 3,349 words of body prose (the old page: 1 em dash in 1,123 words); the calculator's result text in eight cases (both sexes, four methods): 0 tells, 0 em dashes in 2,286 words.

**Chat's read-through, fixed on the draft:** the FAQ cited only DA Form 5501 (women) for the men's navel site too → DA Forms 5500 and 5501; the "most accurate" FAQ cited Burns but not Foulis → both cited; "CDC calls DXA … (CDC)" → "CDC's documentation calls DXA …"; the 3-site result note "That study used seven sites." → "That study used seven sites; you entered three."; "Overall, this formula came within 5 points … for 74% of US women aged 20 to 59" → "Across all US women aged 20 to 59, this formula came within 5 points of the scan for 74%."

**Independent fact-check (separate agent: its own code on CDC's raw files, the tool in Playwright, sources re-read live): 1 FAIL, 6 WARN, 12 NOTE, all settled.**
- Passed: every sample count (10,864; 10,751; 10,829; 59 strata, 121 PSUs), 35 of the 36 table values, all 44 accuracy-figure values, every margin-of-error statement, the paired comparison, the US means, all 137 calibration windows under the stated method, all 630 US-comparison shares (= `bfpc_stats.json`), the calculator in 24 runs (estimates, ranges, shares, windows, fat and lean mass, conversions), the sources (Foulis, Burns, Deurenberg, Woolcott, CDC's DXX_J, DA 5500 and 5501), the FAQ JSON-LD (9 of 9 equal), links.
- FAIL, fixed: float noise decided ties. A Deurenberg estimate is an exact hundredth (BMI and DXA recorded to 0.1, age in whole years), and 6 women whose error was exactly 3.00 fell outside "within 3 points"; estimates of exactly a whole percent landed in the wrong windows. `bfc_stats.py` now rounds Deurenberg estimates and errors to 0.01 (relative fat mass to 10 decimals, which only removes the noise). Within 3 points for women: 41.4% → 41.5%; 30 of the 81 Deurenberg windows change their count by 1 to 4 (men "12": 75 → 72; women "36": 432 → 430). The tool already rounded exact hundredths up (its `r1()` adds 1e-9).
- WARN, fixed (6):
  - the OG and Twitter description said every method came close to "CDC's DXA scans of 10,864 US adults": it now says CDC's scans checked two formulas and published studies the tape and calipers;
  - the comparison with relative fat mass's authors implied more than the data show. New Woodruff 95% CIs of our median error, +2.32 [2.11, 2.53] for women and +0.81 [0.63, 1.03] for men, against Table 2's 0.9 [0.6, 1.1] and 0.5 [0.3, 0.8]: the page now says it read clearly higher for women, not clearly differently for men, and that scanner model and age range (20–69 in their test) also differ, so the reason isn't known (the old scanner sentence implied a cause);
  - Burns's 1.4 is DXA minus skinfolds (Table 3, "DXA–Surrogate"), a signed mean, not a typical miss: "differed from DXA by 1.4 points" → "read 1.4 points below DXA on average" in the takeaways, the methods list, the accuracy section, the calipers section, 2 FAQ answers and the tool, with the average miss (MAPE 11.7%) named beside it where methods are compared;
  - switching units changed the result: 64 in became a whole 163 cm, so the starting 33.0% "High" turned into 32.9% "Healthy", and 5′4.5″ went to 164 cm and back as 5′5″. The switch now converts to 0.1 and restores the numbers when switched back with nothing retyped; the metric height starts at 162.6 cm; the test checks the result both ways and four round trips. The worked example stays at 33.0% (32.98 unrounded, 32.96 from the metric values): the page uses it to show where the high range starts;
  - the 0.0001392 coefficient had no cited source (Serra, the cited reproduction, prints 0.0001395): the coefficients now cite Topend Sports, which prints all four equations as the page does, with 0.0001392, citing Jackson, Pollock and Ward (1980); Serra is named as the 0.0001395 variant (under 0.02 points at any age from 18 to 79);
  - the results overstated how close the estimate is: the calibration note adds "Trained technicians measured them; measuring yourself adds some error." (CDC's BMX_J documentation: collected "by trained health technicians"), the tape and caliper notes "Measuring yourself at home can add more error.", and the US comparison "The share and the range treat this estimate as if it were a scan reading, so they are only as close as the estimate."
- NOTE, fixed (10): one percentile rule on the page (the calibration windows now use the chart's weighted midpoint rule, over distinct values so tied readings' order can't matter; within 0.08 of the chart's 50 printed quartiles; the worked example's windows 33.9 / 36.7 / 39.5 → 34.0 / 36.8 / 39.5% and 33.6 / 36.0 / 38.4 → 33.7 / 36.1 / 38.5%); "standard error" → "standard error of estimate"; the waist site cites Cedars-Sinai for "the top of your hip bones" and Woolcott and Bergman for CDC's level; the tape method's waist differs for men too (navel); "both differences" → "all four differences"; the median error labelled as the measure the authors report; the starting values say the waist-and-height field starts empty; the JSON-LD featureList no longer says "US adults aged 16–59"; the other-estimates rows say "aged 20 to 59"; "the Army's 2013 worksheets", plus one sentence on Army Directive 2023-11 (army.mil, June 12, 2023: a one-site tape test).
- NOTE, already fixed by chat (1): "less than 0.1 point, even at 60" → "less than 0.02 points at any age from 18 to 79" (at most 0.012).
- Kept: an 18- or 19-year-old is still compared with US "girls" or "boys" aged 16–19 (the rest of the ages note), the chart's rank tool group and wording; and the Army's Table B-5 printed values and the J Public Health Afr table couldn't be re-read live (a binary PDF; PMC's reCAPTCHA). Both were verified in earlier batches (registry `body-fat-equations`, `gallagher-2000-bf-ranges`), and the agent's own checks agree (logarithms rounded to two decimals give 46.734 and 38.620; the BMI 18.5 and 25 cut-offs for ages 20–59 match Genes Nutr 2017). The BMI-30 and 60–79 cut-offs stay on the registry's re-check list.

### Chat results (fresh GitHub clone of `f365b8b` + this package)
- **Gates and dates:** FIX.md steps 0–5 as written, run twice (today, and with `CMB_TODAY=2026-10-30` and commit dates set to that day): dry-run and apply 9 / 8 / 2 / 1; gates 3.1–3.9 pass; 3.10 `0 1 1 9 0 0 1 1 1 2 2 27 0 1 1 1 1 1 3 0 29`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **Data:** `bfc_stats.py` rebuilds `bfc_stats.json` byte for byte from CDC's raw files; `pref_images.py` redraws the three preferred images byte for byte.
- **Tests:** page test 462 checks, 0 failures on the applied clone (17 deliberate breaks each failed it; SPEC.md lists them); `/body-fat-percentage-chart/` test 519 checks, 0 failures; Chromium end-to-end 1,316 checks, 0 failures; jsdom 95 / 0; FAQ opens on all 28 FAQ pages; menu 40 / 40; no page wider than the screen at 360 / 390 / 1280 (120 checks).
- **Detector (impeccable 0.1.14):** this page 9 → 0 at 390×844 and 19 → 0 at 1280×800; results open in three states (tape for a woman, waist and height, 7-site calipers for a man) 0; `/body-fat-percentage-chart/` stays 0; sitewide static 271 → 262 (41 pages, `research/impeccable-baseline/2026-10-28-cmb020-390x844.json`); the 8 shared calculators with results open stay at 88.

### Not in this batch (logged for §5)
- The menu's current-page marker is inconsistent sitewide: `/average-weight/`, `/body-fat-percentage-chart/`, `/blog/bmi-for-athletes/`, `/blog/how-to-measure-body-fat/` and `/blog/what-is-bmi/` mark "Obesity Statistics" (their shells came from `/us-obesity-statistics/`); `/bmi-chart/` and `/calculators/` mark nothing though the menu links them; blog posts mark "Guides" in the desktop menu only, or in both. A small sitewide fix plus a `check_structure` rule (the marked link must be this page, or its section), outside `<main>`, so no dates move.
- `research/body-fat-chart-build/bfpc_stats.py` applies the midpoint rule reading by reading after an unstable sort (`np.argsort`), so the order of tied readings can move its percentiles: a stable sort alone moves 5 of the 50 tool quartiles by 0.1 when printed. An order-free version (over distinct values, as `bfc_stats.py` now does) regenerates `/body-fat-percentage-chart/` and every page that quotes its percentiles or `research/body-fat/bf_results.json`'s (same rule; the registry's `nhanes-2011-2018-dxa` row lists the pages).

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-020-body-fat-calc/`.
0.3 `git log --oneline -4 | grep -c "CMB-019"` → 1 or more. If 0, STOP: CMB-019 must run first.

### 1. Dry run
`python3 research/cmb-020-body-fat-calc/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 9 new files, 8 replaced files, 2 edits, 1 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-020-body-fat-calc/apply_build.py`
Must print exactly: `applied: 9 new files, 8 replaced files, 2 edits, 1 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py body-fat-calculator/index.html body-fat-percentage-chart/index.html` → `body-fat-calculator/index.html: 0 issues` and `body-fat-percentage-chart/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py body-fat-calculator/index.html body-fat-percentage-chart/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `body-fat-calculator/index.html`, CH = `body-fat-percentage-chart/index.html`):
- `grep -o '{TODAY}' $PG | wc -l` → `0`
- `grep -o "net/body-fat-calculator/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $PG | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `9`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o '<article' $PG | wc -l` → `0`
- `grep -o 'application/ld+json' $PG | wc -l` → `1`
- `grep -o 'max-image-preview:large' $PG | wc -l` → `1`
- `grep -o 'window.BFC=' $PG | wc -l` → `1`
- `grep -o 'href="/body-fat-calculator/" class="active" aria-current="page"' $PG | wc -l` → `2`
- `grep -o 'aria-current="page"' $PG | wc -l` → `2`
- `ls assets/images/preferred/ | wc -l` → `27`
- `ls body-fat-calculator/og-body-fat-calculator.png 2>/dev/null | wc -l` → `0`
- `grep -o "'/body-fat-calculator/': 'body-fat-calculator'" scripts/check_images.py | wc -l` → `1`
- `grep -c 'Body fat calculator (CMB-020)' DESIGN.md` → `1`
- `grep -c '\.bfc \[hidden\]' assets/css/styles.css` → `1`
- `grep -o "viewBox=\"0 0 '+W+' 88\"" $CH | wc -l` → `1`
- `grep -c "viewBox=\"0 0 '+W+' 88\"" research/body-fat-chart-build/gen_bfpc.py` → `1`
- `grep -c '^rfm-woolcott-2018,\|^foulis-2023-circumference-dxa,\|^army-tape-worksheets,' research/data-sources.csv` → `3`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'body-fat-calculator'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `29`
3.11 Reproducing `bfc_stats.json` needs CDC's raw DXA files, which stay out of the repo (size; registry `nhanes-2011-2018-dxa`). Record `skipped (raw DXA files not in repo)`; chat ran it (see Chat results).
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /body-fat-calculator/ rebuilt to the D-14 pattern: four methods (Navy tape, relative fat mass, Deurenberg, Jackson-Pollock 3/7 sites) on shared components, each with how close it gets to DXA (our check on CDC NHANES 2011-2018 scans for the waist and BMI formulas, published studies for the tape and calipers), the provisional range and the US comparison; preferred images; menu marks Body Fat; chart tool label no longer clipped (CMB-020)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb020-dates.txt; echo $?; grep -c '^ok' /tmp/cmb020-dates.txt; grep '^BAD' /tmp/cmb020-dates.txt; rm /tmp/cmb020-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-020 BODY-FAT-CALC
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-019 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 skipped (raw DXA files not in repo) | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines: <none or list>
devlog: <git log --oneline -1>
git status: <clean or list>
```
