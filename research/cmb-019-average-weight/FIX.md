# CMB-019 AVERAGE-WEIGHT — `/average-weight/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-22 against GitHub `main` `56acc27` (after CMB-018). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/average-weight/` owns 187 keywords worth 161,260/mo (`research/keyword-ledger.csv`), page 8 of the D-14 rollout:
  - "average weight for men" 9,900 (primary); "average weight 5 4 woman" 12,100; "average weight 5 7 female", "average weight for 5 9 male" and "average weight 5 5 female" 8,100 each;
  - per-height phrasings ("5 3 female average weight" 8,100, "average female weight 5 6" 6,600, "average weight for 6 1 male" and "6 2 male" 4,400 each), the national averages ("average male weight us" 8,100, "average weight for women" 8,100, "average us woman weight" 6,600), BMI ("average bmi" 2,900, "average bmi for women" 2,400), waist ("average female waist size" 4,400) and "average weight by age" 1,000.
- **The old page broke site rules:**
  - three page-level `<style>` blocks (the `aw-*` tool, `cmb-*` page styles), 44 inline `style` attributes, a visible breadcrumb with inline styles, the content inside one `<article>` (§5 [P1] Raptive list), the FAQ as `h3` + paragraphs with no FAQPage JSON-LD, Organization and Person nodes in the page graph, and a text OG card (`og-average-weight.png`);
  - one claim the data don't support: "Weight peaks in middle age: men average the most at 40–49 (210.2 lb)". No step from 30 to 59 is outside its margin of error, and NCHS prints 210.1 lb;
  - detector 10 findings at 390×844 (border-accent-on-rounded 4, low contrast 3, undersized UI text 2, side tab 1) and 19 at 1280×800 (plus line length 9).
- **SERP (owner's pastes of google.com, US/English, 2026-10-22, not personalized):** "average weight for men", "average weight 5 4 woman" and "average weight for 5 9 male" return Healthline, CDC FastStats, Hims, MNT, Rush, Banner, health.com, Verywell, AARP and Reddit. Most quote 199.8 lb, CDC's 2015–2018 average; the AI Overview credits 199.8 lb to FastStats (which says 199.0), and for "5 9 male" it gives the national average as the average at 5′9″. Every height query is answered with a healthy-weight table or the national average. People also ask "How heavy is a 5'7" man?", "Is 200 pounds heavy for a male?", "Is 180 pounds at 5'9" overweight?" and healthy-weight questions at 5′4″. Gap: no result says what Americans of a given height actually weigh. That is the wedge.

## What changes

### 1. `/average-weight/` rebuilt (D-14, guide form, with the tool)
- **Order:** H1 "Average Weight for Men and Women by Height and Age" and the byline → three intro paragraphs → key takeaways (answer first) → disclaimer → hero figure → 8 contents chips → "How does your weight compare?" and the tool → women by height → men by height → by age → height, BMI and waist → since 1960 → 13 FAQ → sources and method → one related block. No `<article>` wrapper: the sections sit in `main .container`, as on the calculators and `/blog/bmi-chart-men/` (the owner's decision on Raptive, §5).
- **The wedge (CDC NHANES August 2021–August 2023, 2,688 men and 3,254 non-pregnant women aged 20 and over, survey-weighted, 95% CIs; the national figures equal NCHS Series 3 No. 50 and FastStats):**
  - by height: one table per sex, one row per inch with 30 or more measured (women 4′9″–5′9″, men 5′2″–6′3″; row links `#women-5-4`, `#men-5-9`, as before): the average with kilograms, the middle half, the healthy range at that height (whole pounds, the weight-table gate's rule), the share with a BMI of 25 or more, a † under 60 measured. At every height measured the average is above the healthy range (the hero shows it; 60%–78% of women and 64%–81% of men of each height have a BMI of 25 or more);
  - the tool: woman or man, US or metric, height, optional weight and age group. It gives the share of US women or men measured at that height or an inch either side (heights rounded to the nearest inch, e.g. "measured at 5′3″ to 5′5″") who weigh less, or the average at that height; a box plot with the healthy range and the weight entered; the BMI and category; the age group's average; the height rank. A height with fewer than 30 measured gets the national average and the healthy range;
  - by age: the decade means (= NCHS Table 4); stated changes only where the 95% CI excludes zero (30s vs 20s: +13.4 lb women, +10.2 lb men; women lower in each decade from 60; men 80+ 13.3 lb below their 70s); from 30 to 59 the averages "are not statistically different" (every pair's 95% CI includes zero);
  - height, BMI and waist: the national means (68.9 / 63.5 in, BMI 29.4 / 30.0, waist 40.6 / 38.5 in), the medians, the middle half of waist sizes, 47.4% of men and 67.5% of women over NHLBI's waist lines (over 102 cm and 88 cm); BMI and waist by decade;
  - since 1960: ages 20–74, 166.3 → 191.0 → 200.2 lb for men and 140.2 → 164.3 → 173.7 lb for women (Advance Data No. 347 Table 6; our calculation for 2021–2023); why results say 199.8 lb (NCHS Series 3 No. 46, 2015–2018).
- **FAQ:** 13 questions: the national averages, the four secondary heights (5′4″, 5′5″ and 5′7″ women, 5′9″ men), three People-also-ask questions as asked ("How heavy is a 5′7″ man?", "Is 200 pounds heavy for a male?", "Is 180 pounds at 5′9″ overweight?"), average BMI, waist size, weight by age, and 199.8 lb. JSON-LD equals the visible text.
- **Head:** the title stays ("Average Weight for Men and Women by Height and Age (CDC)"), and so does the meta description (still true); new OG and Twitter text with `twitter:title` and `twitter:description`; the preferred image (§2); JSON-LD Article (`dateModified` `{TODAY}`, author named, publisher, image list, `mainEntityOfPage` with `primaryImageOfPage`, citations), Dataset (`dateModified` `{TODAY}`, the CSV), BreadcrumbList and a new FAQPage. The three `<style>` blocks and every inline style are gone.
- **CSV download** (`average-weight/average-weight-nhanes-2021-2023.csv`, same URL; the old columns plus `bmi25_plus_pct`, `mean_bmi`, `se_bmi`, `mean_waist_in`, `se_waist_in`, as the Dataset JSON-LD describes): regenerated with the method below; the medians and quartiles move by up to a few pounds, the means don't.
- **Build record:** `research/average-weight-build/`: `SPEC.md`; `gen_aw.py` (writes the page and the CSV; stops unless every printed figure equals `avgw_results.json` or a source value typed in, every link is a registry URL and no label collides); `aw_test_playwright.py`.

### 2. The method, and the men's chart
- `research/average-weight/compute.py` now converts with NCHS's factor (2.2046 lb per kg), reads percentiles from the weighted distribution over distinct measured values (no tie order: the CMB-018 [P3]) and keeps pregnant women for height, as NCHS's Table 8 does. It stops unless it reproduces NCHS Series 3 No. 50's Table 4 in full and the adult rows of Tables 8, 10 and 12 (204 values). `avgw_results.json` adds what the page prints (by-height quartiles, BMI 25+ shares and the tool's percentiles for the height and an inch either side, waist, ages 20–74, decade steps and the 30–59 pairs with CIs).
- `research/chart-men-build/bcm_stats.py` uses the same method (its quartiles are asserted equal to `avgw_results.json`), so `/blog/bmi-chart-men/` is regenerated: the middle-half ranges and medians in its hero, by-height figure text and the 5′10″ answer move by 0.1–1.8 lb (the 5′10″ median 199.3 → 199.1 lb, also in its FAQ); every other figure is unchanged. Its preferred images are redrawn and its `dateModified` and sitemap `lastmod` move to the apply date. `gen_bcm.py`'s one assert follows (199.1).
- No other page prints a figure that changed (the means other generators read from `avgw_results.json` are the same).

### 3. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/average-weight-{16x9,4x3,1x1}.png` (the hero: the healthy band and the women's and men's averages per height, no words or numbers), drawn by `research/preferred-images/pref_images.py` (new `avg_weight` drawing; `men_chart` redrawn with the new quartiles). Named in `og:image` (with `og:image:alt`), `twitter:image`, the Article image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`.
- Deleted: `average-weight/og-average-weight.png` (the old text card; only this page used it).

### 4. Registry, page map, DESIGN.md, styles.css
- `research/data-sources.csv`: 3 new rows, read in chat 2026-10-22: `cdc-faststats-body-measurements` (FastStats, the figures CDC quotes), `nhanes-anthropometric-reference-2015-2018` (Series 3 No. 46: 199.8 / 170.8 lb), `nchs-advance-data-347` (Ogden et al. 2004, Table 6). `average-weight` added to `pages_served` of `nhanes-anthropometric-reference`, `cdc-adult-bmi-categories` and `nhlbi-1998-obesity-guidelines` (7 rows list the page); notes on `nhanes-2021-2023-exam-files` (the CMB-019 figures and the method) and `nhanes-anthropometric-reference` (the tables the page prints, 204 values reproduced).
- `research/page-map.csv`: the row's wedge and notes.
- `DESIGN.md`: "Average weight tool (CMB-019)".
- `assets/css/styles.css`: `.awt` shares the body fat tool's three size rules (selectors added to the CMB-016 lines); `.awt [hidden] { display: none; }` (the US / metric rows); `.data-table--fit` (five-column number tables fit a 390 px phone: 13 px type and 6 px side padding below 600 px, numbers on one line). No other page uses these classes.

### 5. Dates
- Both pages ship as `{TODAY}` templates (`"today": true`): `/average-weight/` for its Article and Dataset `dateModified`, `/blog/bmi-chart-men/` for its Article `dateModified`. The two sitemap `lastmod` values are `{TODAY}` edits.

### 6. Fixes from chat's checks and the independent fact-check
**Chat's own checks, fixed on the draft:**
- the metric height row showed in US mode (`.form-row` sets `display: grid`, which beats the `hidden` attribute): `.awt [hidden]`;
- the by-height tables were 343 px in a 310 px frame at 390 (ranges wrapped, the BMI 25+ column cut off): `.data-table--fit`; all five tables now fit at 390 and 1280;
- the tool figure's "You 320 lb" label sat 0.5 px above the figure, and a weight past the last tick left the scale without its unit: the figure moved down 2 units and the ticks align to their step;
- Advance Data No. 347's weights are in Table 6 only (the draft said "Tables 6 and 8"; chat re-read the PDF); the table's 20–74 means carry no age-adjustment note (the trend tests were adjusted), so they are compared with our crude mean for the same ages;
- wording: "Weight rises in the 30s" (a cross-section, not people followed) → "Adults in their 30s weigh more than adults in their 20s"; the age FAQ no longer implies a peak at 40–49; "have gained" → "the average weight … has risen"; "CDC has weighed Americans since 1960" → "National health surveys have weighed Americans since 1960–1962"; the 5′9″ FAQ names the 199.8 lb answers ("CDC's 2015–2018 average for all US men, whatever their height");
- FAQ: "What is a normal BMI for women?" dropped (`/blog/healthy-bmi-range/` already answers "What is a normal BMI for a woman?"); "What is the average weight for a 5′7″ woman?" (a secondary) and "Is 180 pounds at 5′9″ overweight?" (People also ask) added; "Is 200 pounds heavy for a man?" → "… for a male?" as asked;
- anti-slop: 6 fixes (vague wording 3, staging 1, writing about the page 1, repetition 1); rescored from the built HTML: 0 tells in 2,313 words, 0 em dashes (the old page: 3 em dashes in 1,105 words).

**Independent fact-check (separate agent, on the draft).** It rebuilt the sample from CDC's raw files with its own code and found no wrong number on either page: 498 published NCHS values reproduced (all of Tables 4, 8 and 12 and Table 10's adult rows; only with 2.2046 lb per kg), the 27 by-height rows, the hero, the 14 decade means and 28 BMI and waist values, every stated and unstated age change, all 13 FAQ answers (JSON-LD equal to the visible text), the 43 CSV rows, the tool on 4 inputs against raw shares (36% vs 36.2%, 57% vs 56.7%, 80% vs 80.3%, 41% vs 41.1%), and all 33 new values on `/blog/bmi-chart-men/`. The 1960 comparison is like-for-like (Advance Data No. 347's means are crude and exclude pregnant women, as ours do). Settled before packaging:
- **WARN, fixed:** "differ by less than their margins of error" (the men's 40s-vs-30s gap, 8.6 lb, exceeds the 30s' own ±5.3) → "are not statistically different: the 95% confidence interval of the gap between any two of those age groups includes zero"; `compute.py` adds the 30s-vs-50s pair, asserted in the generator and the test.
- **WARN, fixed:** "within an inch": the tool groups rounded heights h−1 to h+1, so measured heights up to about 1.5 in away (at 5′9″: 1,021 men; 722 within ±1.0 in; shares move by under a point). The card, note, intro and method now say "measured at 5′8″ to 5′10″" / "at your height or an inch either side", heights rounded to the nearest inch.
- **WARN, fixed:** the waist shares use NHLBI's cm lines (with the inch lines they would be 48.6% and 65.2%): the sentence now leads with "over 102 cm (40 in) … over 88 cm (35 in)" and says the calculation is in centimeters.
- **WARN, fixed:** 200 lb at 6′3″ is BMI 24.996, overweight only after rounding: the FAQ now says 6′3″ "sits right at the line (25.0)" and overweight runs 5′9″ to 6′2″ (29.5 down to 25.7).
- **WARN, fixed:** the Dataset JSON-LD promised BMI and waist by age with standard errors that the CSV lacked: the CSV adds them (and BMI by height), and the description names what the file holds.
- **WARN, fixed:** "above the healthy range at every height" → "at every height measured (women 4′9″–5′9″, men 5′2″–6′3″)"; meta and OG "by height and age"; hero "at every height shown"; the OG alt gives the spans.
- **NOTEs taken:** the method names exactly what is reproduced (Table 4 in full, the adult rows of Tables 8 and 12, Table 10's adult BMI means and medians: 204 values); Table 10 joins the sources; the tool's percentiles are stored at 4 decimals and rounded once (126 of 2,673 were 0.1 lb off, nothing visible).
- **NOTEs kept:** the site's rounded "18.5 to 24.9" against CDC's "18.5 to less than 25" (CMB-008 rule, stated); the women's 30.0 "at the line" (NCHS prints 30.0); the title's "(CDC)"; "1960–1962" as Advance Data No. 347 labels NHES I (CDC's page says 1959–1962).
- **Not checked by the agent:** the images and layout (chat's tests and the detector cover them). A newer NHANES cycle: CDC lists 2025–2027 with documentation only, so August 2021–August 2023 is the latest with data (chat, 2026-10-22).

### Chat results (fresh GitHub clone of `56acc27` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-24` and commit dates set to that day. Both runs: dry-run and apply `7 / 18 / 2 / 1`; gates 3.1–3.9 pass; 3.10 `0 1 1 2 1 13 0 0 4 13 14 1 24 0 1 1 1 4 3 0 29`; 3.11 `same same`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **3.11 in chat:** `compute.py` on CDC's raw DEMO_L and BMX_L files rebuilds `avgw_results.json` byte for byte (it stops unless the 204 NCHS values reproduce); `bcm_stats.py` rebuilds `bcm_stats.json` byte for byte (it stops unless its quartiles equal `avgw_results.json`, and its shares NCHS Data Brief 508, `healthy_stats.json` and `bc_stats.json`); `pref_images.py` redraws both pages' preferred images.
- **Browser checks (Chromium):**
  - `aw_test_playwright.py` on the applied clone: 545 checks, 0 failures. It covers the published NCHS, FastStats, Advance Data No. 347 and Series 3 No. 46 values typed in; both by-height tables row by row (brute-force healthy ranges, kg, cm, middle half, BMI 25+, the † rows) with two rows typed in; the age, BMI-and-waist and since-1960 tables; the CSV's 43 rows and new columns; the hero's 27 dots and the healthy band at their drawn positions, hover labels and description; the tool's data against the stats file and 10 cases (both sexes, both units, with and without weight and age, a height with too few measured, out-of-range input) worked out from the stats file, plus typed-in answers (36%, 57%, BMI 26.6 and 29.3); the unit switch; the hidden rows; 45 sentences that state numbers, rebuilt from the stats; the fact-check's fixes (no "within an inch", "margins of error", "over 40 inches (102 cm)", "from 5′9″ to 6′3″"); head, OG/Twitter, the four JSON-LD blocks, the preferred images at size, both `dateModified` values = the sitemap `lastmod`, the old OG image gone; every internal link answers 200 and every outside link is a registry URL; 8 chips and 13 FAQ with JSON-LD equal to the visible text; no page wider than 320, 360, 390 or 1280; every table inside its frame at 390 and 1280; no SVG label collisions or labels on shapes in the hero or the tool's figure; no JavaScript error. Five deliberate breaks on a copy of the page (one by-height cell, one age-table cell, one hero dot, one FAQ answer, the tool's share rounding) each failed the test.
  - `bcm_test_playwright.py` (`/blog/bmi-chart-men/`, regenerated) on the applied clone: 921 checks, 0 failures.
  - On chat's work tree (identical to the clone): calculator end-to-end 1,316 checks, 0 failures; FAQ opens on all 27 pages that have one (this page joins them); no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Detector (impeccable 0.1.14):** this page 10 → 0 at 390×844 and 19 → 0 at 1280×800; `/blog/bmi-chart-men/` stays 0 and 0. Sitewide static 281 → 271 at 390×844, only this page changed (`research/impeccable-baseline/2026-10-22-cmb019-390x844.json`); with results open the 8 calculators stay at 88 (no calculator changed).
- **Live R4 (owner):** the detector on production `/blog/bmi-chart-men/` printed only the consent-banner note, so 0 findings. That closes CMB-018's open item.

### Not in this batch (logged for §5)
- A printable chart image: the tables carry the per-height answers and the "chart" queries for this page are small (about 1,000/mo in all); add one if Search Console shows image traffic.
- Heights with fewer than 30 measured (women 5′10″ and taller, men under 5′2″ and 6′4″ and taller) get no average; the group of an inch either side could still rank a weight there (e.g. women measured at 5′9″ to 5′11″). Possible with a separate window-only entry in `avgw_results.json`.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-019-average-weight/`.
0.3 `git log --oneline -4 | grep -c "CMB-018"` → 1 or more. If 0, STOP: CMB-018 must run first.

### 1. Dry run
`python3 research/cmb-019-average-weight/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 7 new files, 18 replaced files, 2 edits, 1 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-019-average-weight/apply_build.py`
Must print exactly: `applied: 7 new files, 18 replaced files, 2 edits, 1 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py average-weight/index.html blog/bmi-chart-men/index.html` → `average-weight/index.html: 0 issues` and `blog/bmi-chart-men/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py average-weight/index.html blog/bmi-chart-men/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `average-weight/index.html`, MEN = `blog/bmi-chart-men/index.html`):
- `grep -o '{TODAY}' $PG $MEN | wc -l` → `0`
- `grep -o "net/average-weight/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o "blog/bmi-chart-men/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $PG | wc -l` → `2`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $MEN | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `13`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o '<article' $PG | wc -l` → `0`
- `grep -o 'application/ld+json' $PG | wc -l` → `4`
- `grep -o 'id="women-' $PG | wc -l` → `13`
- `grep -o 'id="men-' $PG | wc -l` → `14`
- `grep -o 'max-image-preview:large' $PG | wc -l` → `1`
- `ls assets/images/preferred/ | wc -l` → `24`
- `ls average-weight/og-average-weight.png 2>/dev/null | wc -l` → `0`
- `grep -o "'/average-weight/': 'average-weight'" scripts/check_images.py | wc -l` → `1`
- `grep -c 'Average weight tool (CMB-019)' DESIGN.md` → `1`
- `grep -c '\.awt \[hidden\]' assets/css/styles.css` → `1`
- `grep -o 'median 199.1 lb' $MEN | wc -l` → `4`
- `grep -c '^cdc-faststats-body-measurements,\|^nhanes-anthropometric-reference-2015-2018,\|^nchs-advance-data-347,' research/data-sources.csv` → `3`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'average-weight'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `29`
3.11 Reproducing the stats needs pandas (the raw files are in `research/average-weight/raw/`). If `python3 -c "import pandas"` fails, record `skipped (no pandas)`; chat ran both (see Chat results). Otherwise:
- `python3 research/average-weight/compute.py research/average-weight/raw /tmp/avgw_check.json > /dev/null && cmp /tmp/avgw_check.json research/average-weight/avgw_results.json && echo same; rm -f /tmp/avgw_check.json` → `same`
- `python3 research/chart-men-build/bcm_stats.py research/average-weight/raw research/healthy-range-build/healthy_stats.json research/bmi-chart-build/bc_stats.json research/average-weight/avgw_results.json /tmp/bcm_check.json > /dev/null && cmp /tmp/bcm_check.json research/chart-men-build/bcm_stats.json && echo same; rm -f /tmp/bcm_check.json` → `same`
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /average-weight/ rebuilt to the D-14 pattern: the average at every height for US women and men (NHANES 2021-2023, = NCHS Series 3 No. 50), the comparison tool on shared components, age steps outside their margin of error, BMI and waist, since 1960 and the 199.8 lb answers; NCHS-matching method also regenerates /blog/bmi-chart-men/'s quartiles; preferred images (CMB-019)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb019-dates.txt; echo $?; grep -c '^ok' /tmp/cmb019-dates.txt; grep '^BAD' /tmp/cmb019-dates.txt; rm /tmp/cmb019-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the two pages report BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-019 AVERAGE-WEIGHT
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-018 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 <same same, or skipped (no pandas)> | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines: <none or list>
devlog: <git log --oneline -1>
git status: <clean or list>
```
