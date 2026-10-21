# CMB-015 BMI-CHART — `/bmi-chart/` rebuilt to the D-14 pattern, and every page set up for images in Google results

Built and tested in chat on 2026-10-21 against GitHub `main` `621bf8b` (after CMB-014). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are fixed below (§7).

## Why
- **Demand.** `/bmi-chart/` owns 471 keywords worth 305,070/mo (`research/keyword-ledger.csv`), page 4 of the D-14 rollout:
  - "bmi index chart" 201,000 (primary, the ledger's form of "bmi chart"), "height and weight chart" 12,100, "height weight chart" 9,900, "weight on height" 9,900, "weight charts" 8,100;
  - "bmi body chart" 3,600, "bmi table" 2,900, "bmi ht wt chart" 2,400, "weight table according to height" 1,900;
  - per-height "at 5 X how much should i weigh": 5′4″ and 5′2″ 1,600 each, 5′9″ 1,300, 5′3″ 1,000, 5′8″ 880.
- **The old page broke site rules:**
  - 1,036 words outside the tables, 5 FAQ, and no `<img>`, although its title said "(Printable)".
  - A page-level `<style>` with grey kilograms on the category tints (low contrast), plus a second `<style>` inside `<main>` switching two hero SVGs.
  - Article JSON-LD description with heights written `4'10'` and `6'6'`.
  - The generic `og-image.png` logo card.
  - Detector: 4 findings at 390×844 and 12 at 1280×800.
- **SERP (owner's pastes of google.com, US/English, 2026-10-16; Google marked them personalised):**
  - "bmi chart": AI Overview with CDC's categories, "How to Use a BMI Chart" and BMI's limits, topped by a row of five chart images; then CDC's Adult BMI Calculator, NIH's BMI table PDF and other tables. People also ask: "What is a healthy BMI by age?", "What is the new BMI chart for 2026?", "Is 20 BMI too skinny?", "At what BMI are you no longer obese?".
  - "height and weight chart": AI Overview listing healthy weights by height, image row; Rush, Banner ("ideal weight"), NIH, a women's table by frame size. No People also ask.
  - "weight charts": AI Overview, image row; growth charts, Banner, Rush, NIH, WHO. People also ask: "What is the correct weight for my age and height?", "What is an ideal weight chart?", "Is 70 kg a normal weight?", "Is 62kg heavy for a girl?".
  - Gap: every result is a lookup table, NIH's whole-number BMI columns or 18.5–24.9 ranges. None shows where US adults fall on the chart, none starts from a weight (the two kg questions), none applies the June 2026 ADA standards.
- **Images in Google results (owner, 2026-10-16: "make everything possible for serp to show a photo").** Google picks the picture next to a result by itself. Its image guide (section "Specify a preferred image with metadata", March 2026) says how to steer it: name a preferred image in `og:image`, in schema.org `primaryImageOfPage` or as the main entity's `image`; make it relevant; avoid a generic image such as a logo, and images with text; avoid extreme aspect ratios; use high resolution. Its Article guide asks for 16:9, 4:3 and 1:1 images. `max-image-preview:large` allows large previews (Discover needs it). Image results only take images in an `<img>`; inline SVG and CSS backgrounds don't count. The site before this batch:
  - no page set `max-image-preview:large`;
  - no page named a preferred image in its structured data;
  - every OG image carried a title or logo text, and 10 pages used the generic logo card;
  - only 2 pages had an image Google Images can index (the women's chart PNG and the headshot on `/about/`).

## What changes

### 1. `/bmi-chart/` rebuilt (D-14, guide form)
- **Order:** H1 "BMI Chart for Adults: Height and Weight Chart" and the byline → three intro paragraphs (the searcher's questions; the stakes, 26.0% of US adults in the healthy range and the 2026 ADA rule; the promise) → key takeaways (answer first) → disclaimer → hero figure → 9 contents chips → seven sections (the chart, how to read it, the printable table, heights for each weight, the 2026 waist rule, US adults, age and sex) → 10 FAQ → sources and method → one related block.
- **Hero figure:** the CDC category bands over height (4′10″–6′6″) and weight, with the worked example's dot (5′9″, 185 lb, BMI 27.3).
- **The chart:**
  - Pounds: every inch from 4′10″ to 6′6″ (21 rows) by six CDC categories, kilograms below each range; metric: every 5 cm from 145 to 200 cm (12 rows), pounds below. Each unit worked out on its own; `check_weight_tables.py` checks all 198 cells through the 40/40 gate. Row anchors `#h-5-9` (kept) and `#h-170cm`.
  - Printable BMI table, `assets/images/charts/bmi-chart.png` (1640 × 1854): the lightest whole pound for each BMI from 18.5 to 40 at every height from 4′10″ to 6′6″ (483 values, in `bc_grid.csv`), so its 18.5, 25, 30, 35 and 40 columns equal the chart's limits. An `<img>` with alt text, width and height, linked to itself for printing, listed in the image sitemap.
- **How to read it:** three steps and a worked example (5′9″, 185 lb: BMI 27.3, overweight, 17 lb above the healthy range). **Why other charts differ:** NIH's table has one column per whole BMI from 19 to 54, so at 5′9″ its BMI 19 and 24 columns read 128 to 162 lb; CDC's 18.5 to 24.9 gives 125 to 168 lb; at BMI 25 and 30 the two agree (169 and 203 lb).
- **Heights for each weight:** the chart turned around, 100–250 lb and 40–130 kg in 10-unit steps, with row anchors (`#w-160-lb`, `#w-70-kg`). It answers the two kg questions.
- **The wedge: the 2026 waist rule on US adults.** The ADA's June 2026 thresholds (recommendations 3.3a/3.3b, non-Asian and Asian) applied to CDC NHANES 2021–2023: 71.4% of US adults meet them against 40.6% by BMI alone, in the same 5,875 adults (men 73.4% vs 39.5%, women 69.4% vs 41.8%); 94.5% of adults with a BMI of 25–29.9 have a waist at least half their height. The Lancet Commission (2025) for context.
- **Where US adults fall on the chart:** 600 adults drawn in proportion to their exam weights over the tinted bands; the share in each category for all adults, men and women (5,929 adults, 95% CIs; obesity, BMI 40+ and overweight equal NCHS's published crude rates); sex differences stated only where the 95% CI excludes 0 (healthy BMI and BMI 40+), obesity called equal within the margin of error.
- **Age, sex and children:** CDC's categories "regardless of age, sex, or race"; body fat at a healthy BMI by sex (CDC DXA scans); muscle (CDC); older adults (the ADA's sentence); children as percentiles; pregnancy points to CDC and the women's chart.
- **FAQ:** 10 questions: the 8 People-also-ask questions above as asked, then the ledger's 5′9″ question and the old page's men-and-women question. JSON-LD equals the visible text.
- **Head:** `<title>` "BMI Chart for Adults: Height and Weight Chart (Printable)" (57 characters); new meta, OG and Twitter text; the preferred image (§2); Article JSON-LD gets the H1 as headline, the description, the image list, `mainEntityOfPage` with `primaryImageOfPage`, and `dateModified`; the BreadcrumbList page name becomes the H1; FAQPage rebuilt. Both `<style>` blocks removed.
- **Build record:** `research/bmi-chart-build/`: `SPEC.md`; `bc_stats.py` → `bc_stats.json` (stops unless it reproduces NCHS's published rates, CMB-013's healthy shares and CMB-014's women's ADA result); `gen_bc.py`; `chart_bc.py` with `bc_grid.csv`; `bc_test_playwright.py`.

### 2. Images in Google results (every page)
- **Large previews:** `<meta name="robots" content="max-image-preview:large">` on all 40 pages (39 head edits; `/bmi-chart/` carries it in its new head).
- **Preferred images:** `research/preferred-images/pref_images.py` draws each D-14 page's own figure with no words, numbers or logo, in 16:9 (1200 × 675), 4:3 (1200 × 900) and 1:1 (1200 × 1200): `assets/images/preferred/{bmi-chart, bmi-calculator, healthy-bmi-range, bmi-chart-women}-{16x9,4x3,1x1}.png` (12 files). On `/bmi-chart/`, `/`, `/blog/healthy-bmi-range/` and `/blog/bmi-chart-women/`:
  - `og:image` and `twitter:image` become the 16:9 file and `og:image:height` 675;
  - the main entity's JSON-LD `image` lists the 1:1, 4:3 and 16:9 files (Article on the guides; the WebApplication on `/`);
  - a WebPage `primaryImageOfPage` names the 16:9 file (`mainEntityOfPage` on the guides; on `/`, a new WebPage node whose `mainEntity` is the calculator);
  - on the three guides, the Article `author` and `publisher` carry their names (Marko Visic; CalculateMyBMI), not only an `@id` (fact-check note).
  - The three old OG images with text (`assets/images/og/home-bmi-us-adults.png`, `healthy-bmi-range-risk.png`, `bmi-chart-women.png`) are referenced nowhere after this and are deleted.
- **Image sitemap:** the image namespace, and `<image:image>` for every `<img>` inside a page's `<main>`: the headshot on `/about/`, the women's printable chart and the new printable table.
- **Gate:** new `scripts/check_images.py`, run by `check_structure.py` on every page: the robots tag on every page; on the pages in its `PREFERRED` list (and any page pointing at `assets/images/preferred/`), the three files at their exact sizes and all three namings; the image sitemap equal to the `<img>` elements in `<main>`, both ways. A later rebuild adds its page to `PREFERRED`. Tested: a missing robots tag, an old `og:image` and a missing sitemap entry each fail the gate.
- **DESIGN.md:** "Images in search results (CMB-015)".
- The other 36 pages get only the robots tag now. Their preferred images come with their D-14 rebuilds; drawing them now would mean redrawing them within weeks and would move their sitemap dates twice.

### 3. Registry and page map
- `research/data-sources.csv`: no new rows. 12 rows now list `bmi-chart`; notes added on `nhanes-2021-2023-exam-files` (this batch's results), `ada-2026-obesity-standards` (all US adults) and `nih-bmi-table-2022` (the 69-inch row).
- `research/page-map.csv`: the `bmi-chart` row is built, with `data_source` `nhanes-2021-2023-exam-files`; the data-sourcing check passes for it; 31 other rows still fail on free-text `data_source` (32 before).

### 4. `styles.css`
- `.weight-chart` cells get 8 px (0.5rem) beside the text, as the detector asks for 13 px text (was 7.2 px; the women's chart stays at 0 findings).
- `.th-sub` also works in `.data-table` row headers (the US adults table).

### 5. Dates
- `/bmi-chart/` ships as a `{TODAY}` template (`"today": true`) for its schema `dateModified`.
- Sitemap `lastmod` is a `{TODAY}` edit for `/bmi-chart/` (text) and for `/`, `/blog/healthy-bmi-range/` and `/blog/bmi-chart-women/` (JSON-LD only, so their schema `dateModified` stays). The robots tag and the OG tags are head tags and move no date.

### 6. Fixes from chat's own checks
- The hero's 80 lb label met the 4′10″ label in the corner at both widths; it is gone (the axis starts at 80 lb).
- Two kg answers printed heights as "5′6.″"; they now round to whole inches ("about 5′6″ to 6′4″").
- anti-slop: 6 fixes (staging 4, re-explaining 1, vague wording 1).

### 7. Fixes from the independent fact-check (separate agent, on the draft)
No number was wrong. The agent recomputed about 130 survey figures from the raw NHANES files with its own code, checked 1,247 formula values (every chart cell, the heights-for-each-weight tables, the 483 printable-table values) and 59 row labels, and matched the 600 plotted dots to real NHANES adults: no mismatch. Its sandbox could not open the web, so chat verified the outside claims: the ADA press release (June 29, 2026) and ADA Meeting News, CDC's About BMI page, and the registry rows verified 2026-10-14 to 2026-10-16. Fixed before packaging:
- **FAIL:** the 62 kg answer now says 143 cm or less is obesity.
- **Warnings (6):**
  - The ADA sentence now reads "published a new chapter of its obesity standards that adds the waist". A 2025 edition of the standards existed; the screening-and-diagnosis chapter is new in June 2026.
  - A note explains why BMI alone gives 40.6% in the ADA comparison and 40.3% across all adults: the 54 adults left out all have a BMI under 30.
  - "matching NCHS's published crude rates".
  - The FAQ spells out the Asian thresholds (80 cm / 90 cm, and 27.5 whatever the waist).
  - Both figures draw the category edges at the rounding lines, so the dot counts in the description match the picture.
  - CDC's muscle sentence checked verbatim (no change).
- **Notes (8):** the all-adult median removed (NCHS publishes medians by sex only, and the weighted median sits on a rounding edge); "about 204 lb"; "±4.7 points"; 203 lb marked as a BMI of 30.0 rounded to one decimal; the printable table says your BMI is the column's number "or a little more" (page and image); the Article author and publisher are named on the page, also on `/blog/healthy-bmi-range/` and `/blog/bmi-chart-women/` (4 more JSON-LD edits). No change for CDC's "18.5 to less than 25" (the same range at one decimal) or for the 54 adults left out (disclosed in the method).

### Chat results (fresh GitHub clone of `621bf8b` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-23` and commit dates set to that day. Both runs: dry-run and apply `23 / 6 / 63 / 3`; gates 3.1–3.9 pass; 3.10 `0 1 4 10 0 0 0 12 3 0 1 0 31`; 3.11 `same`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **Browser checks (Chromium, on the applied clone served locally):**
  - `bc_test_playwright.py`: 1,086 checks, 0 failures. It covers both chart tables (198 cells) by brute force and every row link; the heights-for-each-weight tables; the printable table's 483 values, size, alt text and link; the US adults table; the figure labels and the 600 dots; the robots tag, OG and Twitter images, the JSON-LD image list and `primaryImageOfPage`, and the preferred files at their sizes; 9 chips and 10 FAQ; JSON-LD against the visible text; SVG label collisions at 390 and 1280; widths at 320, 360, 390 and 1280. A planted wrong cell fails it.
  - After their head and JSON-LD edits: the women's chart test 604/0, the healthy-range test 214/0, the homepage test 131/0.
  - Calculator jsdom 95/95; calculator end-to-end 1,316 checks, 0 failures; FAQ opens on all 25 pages that have one; no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Gate test:** in a copy, a missing robots tag on `/about/`, the old `og:image` on the women's chart, a dropped image-sitemap entry and a wrong chart cell each fail `check_structure.py`.
- **Detector (impeccable 0.1.14):** `/bmi-chart/` 4 → 0 at 390×844 and 12 → 0 at 1280×800; `/`, `/blog/healthy-bmi-range/` and `/blog/bmi-chart-women/` stay at 0 at both widths. Sitewide static 311 → 307 at 390×844, only `/bmi-chart/` changed (`research/impeccable-baseline/2026-10-21-cmb015-390x844.json`).
- **Live R4 (owner):** the detector on production `/blog/bmi-chart-women/` printed only the consent-banner note, so 0 findings. That closes CMB-014's open item.

### Not in this batch (logged for §5)
- The other 36 pages: preferred images and their own OG images in their D-14 rebuilds. Nine still use the generic `og-image.png` logo card: `/about/`, `/blog/`, `/calculators/`, `/contact/`, `/privacy/`, `/terms/`, `/blog/bmi-by-age/`, `/blog/bmi-chart-men/`, `/blog/how-to-lower-bmi/`.
- `/blog/bmi-chart-men/` keeps its page-level `.bmi-chart` `<style>` (grey kilograms on the tints), the `5'2'` JSON-LD description, arrow glyphs in links and "no numbers on this page are hand-authored" until its rebuild.
- Image license metadata (the "Licensable" badge in Google Images) needs the owner to choose a license for the chart images.
- Other Article pages (e.g. `/average-weight/`) still name their author and publisher by `@id` only; name them in each D-14 rebuild. The `#organization` node is named "CalculateMyBMI" on `/` and "Moving Data Systems d.o.o." on `/about/`; settle one `name` (with `legalName` for the company) the next time `/about/` changes.
- Google's choice of thumbnail shows only after it recrawls the pages; Search Console's performance report (Search appearance) is where to watch it after the final round (D-07).

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-015-bmi-chart/`.
0.3 `git log --oneline -4 | grep -c "CMB-014"` → 1 or more. If 0, STOP: CMB-014 must run first.

### 1. Dry run
`python3 research/cmb-015-bmi-chart/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 23 new files, 6 replaced files, 63 edits, 3 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-015-bmi-chart/apply_build.py`
Must print exactly: `applied: 23 new files, 6 replaced files, 63 edits, 3 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py bmi-chart/index.html` → `bmi-chart/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py bmi-chart/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown:
- `grep -o '{TODAY}' bmi-chart/index.html | wc -l` → `0`
- `grep -o "\"dateModified\": \"$(date +%F)\"" bmi-chart/index.html | wc -l` → `1`
- `grep -o "<lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `4`
- `grep -o 'class="faq-question"' bmi-chart/index.html | wc -l` → `10`
- `grep -o '<style>' bmi-chart/index.html | wc -l` → `0`
- `grep -o 'og-image.png' bmi-chart/index.html | wc -l` → `0`
- `grep -o "4'10'" bmi-chart/index.html | wc -l` → `0`
- `ls assets/images/preferred/ | wc -l` → `12`
- `grep -o '<image:image>' sitemap.xml | wc -l` → `3`
- `ls assets/images/og/ | grep -c 'home-bmi-us-adults.png\|healthy-bmi-range-risk.png\|bmi-chart-women.png'` → `0`
- `grep -o '.data-table .th-sub' assets/css/styles.css | wc -l` → `1`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'bmi-chart'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `31`
3.11 If `python3 -c "import pandas"` succeeds, run:
`python3 research/bmi-chart-build/bc_stats.py research/average-weight/raw research/healthy-range-build/healthy_stats.json research/chart-women-build/bcw_stats.json /tmp/cmb015-stats.json >/dev/null && cmp /tmp/cmb015-stats.json research/bmi-chart-build/bc_stats.json && echo same; rm -f /tmp/cmb015-stats.json`
It must print `same`. Without pandas, record `skipped (no pandas)`.
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /bmi-chart/ rebuilt to the D-14 pattern with where US adults fall on the chart and the 2026 ADA waist rule (NHANES 2021-2023), printable BMI table image and heights for each weight; images in search: max-image-preview:large on every page, text-free preferred images on the four D-14 pages, image sitemap, check_images gate (CMB-015)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb015-dates.txt; echo $?; grep -c '^ok' /tmp/cmb015-dates.txt; grep '^BAD' /tmp/cmb015-dates.txt; rm /tmp/cmb015-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the pages report BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-015 BMI-CHART
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-014 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 <same or skipped> | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
