# CMB-022 US-OBESITY — `/us-obesity-statistics/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-29/30 against GitHub `main` `be1ca97` (after CMB-021). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/us-obesity-statistics/` owns 472 keywords worth 100,830/mo (`research/keyword-ledger.csv`), page 11 of the D-14 rollout:
  - "obesity rate in us" 14,800 (primary); "us obesity rate" and "what percentage of americans are obese" 14,800 each; "obesity in america" 5,400; "obese percentage usa" and "percentage of obese americans" 3,600 each; "how many people are obese in america" 2,900; "us obesity statistics", "america overweight rate" and "percentage of overweight americans" 2,400 each; "america average bmi" 1,600; "childhood obesity usa" 1,300; "us obesity rate by year" 1,000.
  - Groups: overweight 10.6k, how many 7k, by year 2.8k, children 2.2k, race 1.1k, states 1.1k, severe 340. State rankings belong to `/obesity-rate-by-state/`, the children's detail to `/childhood-obesity-statistics/`: this page answers each briefly and links there.
- **The old page broke site rules:** two page-level `<style>` blocks (one a copied `.bmi-chart` shell block), the `<article class="cmb-stats">` wrapper, inline styles in `<main>` (the container and a visible breadcrumb), its own `.cmb-*` components with off-palette colours, four SVGs with their own `<style>`, an 8-question FAQ as `<details>` with no FAQPage JSON-LD, Organization and Person nodes in its graph, a text OG card. Detector: 1 finding at 390×844 (side tab), 27 at 1280×800 (line length 26).
- **SERP (owner's pastes of google.com, US/English, not personalized, 2026-10-29):** "obesity rate in us", "what percentage of americans are obese", "us obesity rate by year". The AI Overviews give "40.3% to 42.4%", Gallup's 37.0%, "as high as 68.6% to 75%" under the Lancet Commission's new definition, NIDDK's 2017–2018 figures and 2023 state data. People also ask: "Is it true that 70% of Americans are overweight?", "Are obesity rates rising or falling in the US?", "Is it true that 40% of Americans are obese?", "Which state is #1 in obesity?", "What was the obesity rate in 1960?" (all five are FAQ now). No result says what each of those numbers counts.

## What changes

### 1. `/us-obesity-statistics/` rebuilt (D-14, data page)
- **Order:** H1 "US Obesity Rate and Statistics" (kept) and the byline → three intro paragraphs → key takeaways (the answer plus 5 bullets) → disclaimer → the hero figure → 10 contents chips → how many Americans are obese (category figure in millions, a six-category table, "What percentage of Americans are overweight?") → where do you fit (the tool) → US obesity rate by year (all 15 surveys) → are obesity rates rising or falling → why do sources say 37%, 40%, 42% or 75% → age, gender and education → race and Hispanic origin → severe obesity → children → use this chart or data → 12 FAQ → sources and method → one related block. No `<article>` wrapper (D-16), no page-level style, no inline style in `<main>` outside the figures and the embed code's own markup, no visible dates (D-12). Every anchor of the old page is kept (19 pages link `#age-gender-education`).
- **The wedge:**
  - the 60-year measured series as the hero: obesity, overweight and severe obesity in each survey of CDC's national series, adults 20–74, age-adjusted, 1960–1962 to August 2021–August 2023 (NCHS Health E-Stat 111, Table 1, re-read live 2026-10-29: all 45 values equal the page's CSV); obesity 13.4% → 40.8% (highest estimate 42.8% in 2017–2018, not significantly above 2021–2023, so never "peak"), severe obesity 0.9% → 10.2%, overweight between 30.3% and 34.4% (31.5% in 1960–1962, 31.3% in 2021–2023);
  - one table of what each figure in the search results counts: 40.3% / 41.9% / 42.4% weighed and measured (NHANES August 2021–August 2023; 2017–March 2020, stopped by the pandemic; 2017–2018, its first two years), 37.0% (Gallup 2025, 16,946 adults, self-reported online) and 24.2–39.7% (CDC state surveys 2025, self-reported by phone; 47 states and DC), 68.6% (Fourman et al. 2025, 301,026 All of Us volunteers aged 18–80, not weighted to the US population; 42.9% by BMI alone) and 75.2% (Al-Roub et al. 2025, NHANES 2017–2023, 14,414 adults; 39.9% by BMI alone; 58.4% with a waist-to-height cut-off of 0.6 instead of 0.5) under the 2025 Lancet Commission definition; with what moves each (weighed or asked; years and ages; crude or age-adjusted; the definition);
  - counts by category (our calculation): about 99 million adults with obesity, 79 million overweight, 64 million healthy weight, 23 million class 3; obesity split into class 1 (20.6%, 50 million) and class 2 (10.3%, 25 million) from CDC's 2021–2023 files with the code that reproduces CDC's published crude shares exactly;
  - the "Where do you fit?" tool rebuilt on the shared calculator parts (§3).
- **Kept:** the CSV (585 rows; two blank standard errors filled, §3) and the embeddable chart at their URLs; the embed code's image URL, size, alt text and link, so copies already in use keep working (its credit line now names both surveys: "Data: CDC NCHS (NHES, NHANES)."); the Dataset schema (`@id`, CC BY 4.0, the CSV download; its `dateModified` becomes the apply day because the CSV changed; its name, description and `measurementTechnique` now name both surveys and the child periods).
- **FAQ:** 12 questions, the five People-also-ask questions first, then the 68% / 75% and 42.4% / 41.9% figures, the average BMI, age, sex, 300 lb (2.9%, our calculation) and healthy weight. JSON-LD equals the visible text.
- **Head:** title kept ("US Obesity Rate & Statistics: 40.3% of Adults (CDC Data)"); new meta description, OG and Twitter text (with `twitter:title` and `twitter:description`); the preferred image (§2); JSON-LD `@graph`: Article (`@id` and `datePublished` 2026-09-30 kept, `dateModified` `{TODAY}`, author and publisher named, image list, `primaryImageOfPage`, 12 citations, `isBasedOn` the Dataset), Dataset (kept, `dateModified` `{TODAY}`), BreadcrumbList (kept), FAQPage. The menu already marked this page.
- **Build record:** `research/us-obesity-statistics-build/`: `SPEC.md`; `obs_sources.json` (Gallup, Fourman, Al-Roub, the Lancet Commission, CDC's maps page, typed in with the sentences read); `obs_stats.py` and `obs_stats.json` (our calculation from CDC's 2021–2023 files: the share of adults at 300 lb or more with standard errors, and an independent re-derivation of the class split and mean BMI the page takes from `home_stats.json`); `gen_obs.py` (writes the page; stops unless every printed figure equals the CSV, Table 1 as read live, the sources file, `home_stats.json`, `obs_stats.json` or the state file, every outside link is a registry URL and no figure label collides); `obs_test_playwright.py`.

### 2. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/us-obesity-statistics-{16x9,4x3,1x1}.png` (the hero's three lines and dots in the category colours over grid lines, no words or numbers), drawn by `research/preferred-images/pref_images.py` (new `obs_trend` drawing). Named in `og:image` (with `og:image:alt`), `twitter:image`, the Article image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`.
- The embeddable chart is now an `<img>` on the page, so `sitemap.xml` lists it under the page (`<image:image>`).
- `us-obesity-statistics/us-obesity-trend-1960-2023.svg`: same URL, data and size; its series colours move to the site's category colours (DESIGN.md "The Category Lock"); its description names NHES (1960–1962) and NHANES and gives the overweight range (30.3% to 34.4%), and its subtitle reads "measured (NHES, NHANES)" (§6).
- Deleted: `us-obesity-statistics/og-us-obesity-statistics.png` (the old text card; only this page used it).

### 3. Registry, page map, DESIGN.md, styles.css, number audit
- `research/data-sources.csv`: 2 new rows, read in chat 2026-10-29: `fourman-2025-all-of-us-new-definition`, `alroub-2025-nhanes-new-definition`. `us-obesity-statistics` added to `pages_served` of `lancet-clinical-obesity-2025`, `cdc-brfss-state-obesity` and `nhanes-2021-2023-exam-files`; notes on those three and on `nhanes-adult-weight-trends`, `nhanes-adult-obesity-2021-2023`, `nhanes-child-weight-trends`, `nhanes-underweight` and `gallup-self-reported-obesity` (what was re-read and quoted, the fact-check's findings, the 300 lb calculation).
- The page's CSV and its builder: the two HE-Stat 119 rows for ages 20–74 (underweight 4.0% in 1960–1962, 1.7% in August 2021–August 2023) gain their published standard errors, 0.2 and 0.3, in `us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv` and in `research/us-obesity-build/research/build_dataset_us_obesity.py` (it still writes the CSV byte for byte).
- `research/page-map.csv`: the row's wedge and notes (`data_source` stays `nhanes-adult-weight-trends`).
- `DESIGN.md`: "US obesity tool and embed code (CMB-022)".
- `assets/css/styles.css`: `.obw [hidden]` (the tool's rows hide with `hidden`), `.embed-code` (the read-only embed-code box), `button.cta-button` (a button styled as `.cta-button` drops the browser border), and under 360 px the cells of `.data-table--wrap` tables keep 4 px beside their text (so the four-column tables fit a 320 px phone; `/blog/how-to-measure-body-fat/` also uses the class: its page test still passes, 348 / 0).
- `research/us-obesity-build/tools/number_audit.py` scans `<main>` (the page has no `<article class="cmb-stats">` any more); `allowed_numbers.txt` is the new page's 244 numbers, each traced in `gen_obs.py`.
- `research/us-obesity-build/BUILD.md`: one line at the top pointing to the new build record (the S1 file's "no FAQPage" rule no longer applies).

### 4. Dates
- The page ships as a `{TODAY}` template (`"today": true`) for its Article and Dataset `dateModified` (two placeholders); its sitemap `lastmod` is a `{TODAY}` edit (the same edit adds the chart's `<image:image>`).

### 5. Detector baseline
- `research/impeccable-baseline/2026-10-30-cmb022-390x844.json`: 41 pages, before Calculate: 255 → 254 (this page 1 → 0; no other page changed); results open carried over (88; no calculator changed).

### 6. Fixes from chat's checks and the independent fact-check
- **Chat's checks before the fact-check:** two tables overflowed a 320 px phone (261 and 280 px in a 240 px frame) → all nine tables take `.data-table--wrap` with 4 px cell padding under 360 px; the hero's year labels touched "0%" → moved down; "every CDC survey" for the 1960s (NCHS joined CDC in 1987) → "each survey of CDC's national series"; "about two years" per survey → "two years or more"; the CSV "every figure on this page" → "the NCHS adult and child figures behind this page"; a causal claim about the state figures and an overreading of the Lancet paper removed; "The last two-year survey before that" → "Its first two years"; anti-slop 4 fixes.
- **Independent fact-check** (a separate agent; every source read live, the NHANES shares reproduced from CDC's raw files): 1 FAIL, 4 WARN, 15 NOTE; no number was wrong. Settled:
  - FAIL 1: "surveys before 1988 did not include people older than 74" (HE-Stat 111's text, but its footnote 2 and the CSV say 1960–1962 covered ages 18–79) → "the 1971–1974 and 1976–1980 surveys did not include anyone older than 74".
  - WARN 1: "peaked at 42.8%" / "a peak of 42.4%": 2017–2018 is not significantly above 2021–2023 → "highest estimate", "not significantly lower", "not a significant change".
  - WARN 2: "overweight stayed near 31%": it ran 30.3% to 34.4% → "between 30% and 35%" (takeaway, chart alt), "between 30.3% and 34.4%" (figure descriptions), "ended where it started"; OG alt "roughly level".
  - WARN 3: the state surveys read as a fall → "show no clear change: 21 states were at 35% or higher in 2025 against 19 in 2024", with Mississippi's missing 2025 estimate.
  - WARN 4: the All of Us cohort → "volunteers ... not weighted to the US population"; its 42.9% used WHO's race-specific BMI cut-offs (said in the prose).
  - NOTES 1–14 fixed: race estimates "not shown" → CDC prints them flagged, the table leaves them out ("n/a*", which also removes the page's only em dashes); age adjustment "60 to 74 for the 20-to-74 series"; NHES named for 1960–1962 (Method, Dataset, embeddable chart, embed credit); response rate "all ages"; 7.7% → 9.7% labelled age-adjusted; FAQ 12 uses 26.2% (same basis as 51.1%); FAQ 11 gives 2.9% (our calculation, `obs_stats.py`) instead of "fewer than 5%"; "yet" removed; the BRFSS row says 47 states and DC; FAQ 4 says the top three are within each other's margins of error; Al-Roub's 58.4% at a 0.6 cut-off added; category bars drawn from unrounded counts, caption says healthy weight is by subtraction; the Dataset's child periods corrected; the CSV's two blank standard errors filled; the comparison rule is 2.13 times the standard error (t, 15 df; no claim fell between 2.0 and 2.13).
  - NOTE 15 kept out: Gallup's 2026 article (36.8% "thus far in 2026"); its table and text disagreed when last checked, so the page quotes 2025, the latest full year (registry note on `gallup-self-reported-obesity`).
- **Deliberate breaks:** 28 changes to the built page, its data files, the CSV and the sitemap, each caught by `obs_test_playwright.py` (list in SPEC.md).

### Chat results (fresh GitHub clone of `be1ca97` + this package)
- **Gates and dates:** FIX.md steps 0–5 as written, run twice (today, and with `CMB_TODAY=2026-11-01` and commit dates set to that day): dry-run and apply 10 / 13 / 1 / 1; gates 3.1–3.9 pass; 3.10 `0 1 2 1 12 0 0 1 1 1 9 1 1 33 0 1 1 3 2 1 0 2 1 0 29`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **Data:** `obs_stats.py` rebuilds `obs_stats.json` byte for byte from CDC's raw files; `build_dataset_us_obesity.py` writes the patched CSV byte for byte; `pref_images.py` redraws the three preferred images byte for byte.
- **Tests:** page test 589 checks, 0 failures on both applied clones (28 deliberate breaks each failed it; SPEC.md lists them); on chat's work tree: the `/blog/how-to-measure-body-fat/` page test 348 / 0 with the new table padding, Chromium end-to-end 1,316 checks, 0 failures; jsdom 95 / 0; FAQ opens on all 30 FAQ pages; menu 40 / 40; no page wider than the screen at 360 / 390 / 1280 (120 checks).
- **Detector (impeccable 0.1.14):** this page 1 → 0 at 390×844 and 27 → 0 at 1280×800; sitewide static 255 → 254 (41 pages, `research/impeccable-baseline/2026-10-30-cmb022-390x844.json`); no other page changed.
- **Anti-slop:** rescored from the built HTML: 0 tells and 0 em dashes in 3,482 words of body prose (old page: 0 tells, 31 em dashes in 2,695).

### Not in this batch (logged for §5)
- Country comparisons ("What country is #1 in obesity?", "Why is Japan's obesity rate so low?" in People also ask): no verified country source in the registry, 160/mo in the ledger. A WHO / NCD-RisC row would come first.
- A same-person check of self-reported against measured height and weight in CDC's 2021–2023 survey would need NHANES's WHQ_L questionnaire file (not in the repo).

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-022-us-obesity/`.
0.3 `git log --oneline -4 | grep -c "CMB-021"` → 1 or more. If 0, STOP: CMB-021 must run first.

### 1. Dry run
`python3 research/cmb-022-us-obesity/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 10 new files, 13 replaced files, 1 edits, 1 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-022-us-obesity/apply_build.py`
Must print exactly: `applied: 10 new files, 13 replaced files, 1 edits, 1 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `numbers found: 244; not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py us-obesity-statistics/index.html` → `us-obesity-statistics/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py us-obesity-statistics/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `us-obesity-statistics/index.html`; CS = `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv`):
- `grep -o '{TODAY}' $PG | wc -l` → `0`
- `grep -o "net/us-obesity-statistics/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $PG | wc -l` → `2` (the Article and the Dataset)
- `grep -o '"datePublished": "2026-09-30"' $PG | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `12`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o '<article' $PG | wc -l` → `0`
- `grep -o 'application/ld+json' $PG | wc -l` → `1`
- `grep -o 'max-image-preview:large' $PG | wc -l` → `1`
- `grep -o 'aria-current="page"' $PG | wc -l` → `1`
- `grep -o 'data-table--wrap' $PG | wc -l` → `9`
- `grep -o 'class="calculator-card obw"' $PG | wc -l` → `1`
- `grep -o '"@type": "Dataset"' $PG | wc -l` → `1`
- `ls assets/images/preferred/ | wc -l` → `33`
- `ls us-obesity-statistics/og-us-obesity-statistics.png 2>/dev/null | wc -l` → `0`
- `grep -o "'/us-obesity-statistics/': 'us-obesity-statistics'" scripts/check_images.py | wc -l` → `1`
- `grep -c 'US obesity tool and embed code (CMB-022)' DESIGN.md` → `1`
- `grep -c '\.obw \[hidden\]\|\.embed-code {\|button\.cta-button {' assets/css/styles.css` → `3`
- `grep -c '^fourman-2025-all-of-us-new-definition,\|^alroub-2025-nhanes-new-definition,' research/data-sources.csv` → `2`
- `grep -o 'us-obesity-trend-1960-2023.svg</image:loc>' sitemap.xml | wc -l` → `1`
- `grep -c 'E0612D' us-obesity-statistics/us-obesity-trend-1960-2023.svg` → `0`
- `grep -c ',underweight,4.0,0.2,age-adjusted,\|,underweight,1.7,0.3,age-adjusted,' us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv` → `2`
- `grep -c 'measured (NHES, NHANES)' us-obesity-statistics/us-obesity-trend-1960-2023.svg` → `1`
- `$CS | grep -c "page 'us-obesity-statistics'"` → `0`
- `$CS | grep -c '^FAIL'` → `29`
3.11 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /us-obesity-statistics/ rebuilt to the D-14 pattern: the 60-year measured trend as the hero, what each figure in the results counts (40.3/41.9/42.4% measured, 37% and the state maps self-reported, 68.6/75.2% under the 2025 Lancet definition), counts by category, the Where-do-you-fit tool on shared parts, 12 FAQ; preferred images; CSV and embed code kept (CMB-022)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb022-dates.txt; echo $?; grep -c '^ok' /tmp/cmb022-dates.txt; grep '^BAD' /tmp/cmb022-dates.txt; rm /tmp/cmb022-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-022 US-OBESITY
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-021 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines: <none or list>
devlog: <git log --oneline -1>
git status: <clean or list>
```
