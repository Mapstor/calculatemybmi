# CMB-021 HOW-TO-MEASURE — `/blog/how-to-measure-body-fat/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-29 against GitHub `main` `7662c95` (after CMB-020). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/blog/how-to-measure-body-fat/` owns 913 keywords worth 114,170/mo (`research/keyword-ledger.csv`), page 10 of the D-14 rollout:
  - "how to calculate body fat percentage" 18,100 (primary); "how to figure body fat" and "how to check fat percentage" 6,600 each; "how to check your body fat" 5,400; about 86k in all for the calculate / check / find phrasings;
  - scales 8.1k ("how do scales measure body fat" 1,000, "how accurate are bodyfat scales" 880, "how does a scale determine body fat" 590); at home 4.3k; how much body fat to have 3.5k ("how much body fat should i have" 1,300); calipers 2.4k; tape 1.1k; InBody 670; Bod Pod 70.
  - Ledger owners elsewhere: calculator queries → `/body-fat-calculator/`; ranges by age → `/body-fat-percentage-chart/`.
- **The old page broke site rules:** three page-level `<style>` blocks, 10 inline styles in `<main>`, one `<article>` wrapper, a five-question FAQ as `<details>`/`h3` with no FAQPage JSON-LD, Organization and Person nodes in the page graph, a text OG card (`og-how-to-measure-body-fat.png`), and a menu that marked "Obesity Statistics" as the current page (its shell came from `/us-obesity-statistics/`). Detector: 7 findings at 390×844 (side tab 7), 18 at 1280×800 (plus line length 11).
- **The old numbers told half the story:** its chart drew five of the seven methods in Burns et al. (2019) as distances from DXA ("within 1.0–1.6 points"), but Table 3's figures are signed (DXA minus method): every method read lower than the scan. Two methods had "Not reported in text" though Table 3 reports them. The tape method rested on a conference abstract.
- **SERP (owner's pastes of google.com, US/English, not personalized, 2026-10-29):** "how to calculate body fat percentage", "how to measure body fat percentage" and "how accurate are body fat scales". The AI Overviews list the methods (the BMI formula, the Navy tape, calipers, scales, DXA, underwater weighing), quote the ACE fitness tiers (D-11) and give scales a loose "21% to 34%" error; People also ask: "How do I check my body fat percentage at home?", "How is body fat% calculated?", "Is 30% body fat chubby?" (in all three; `/body-fat-percentage-chart/` answers it and this page links there). This page puts the tested methods against the same scan, works the steps by hand, and says what a measuring slip costs.

## What changes

### 1. `/blog/how-to-measure-body-fat/` rebuilt (D-14, guide form)
- **Order:** H1 "How to Calculate Body Fat Percentage" (kept: the `/blog/` hub card and ItemList still match) and the byline → three intro paragraphs → key takeaways (the answer plus 5 bullets) → disclaimer → the hero figure → 8 contents chips → how to calculate body fat percentage at home → how close tested methods get to a DXA scan → how accurate are body fat scales → how to measure body fat accurately → lab and gym methods → what your number means → 10 FAQ → sources and method → one related block. No `<article>` wrapper (D-16), no page-level style, no inline style in `<main>` outside the figures, no visible dates (D-12), no fitness tiers (D-11).
- **Steps, worked by hand for one man** (40, 5′10″, 180 lb, neck 15.5 in, waist 36 in at the navel and 37 in at the top of the hip bones, skinfolds 15 / 25 / 18 mm): relative fat mass 26.2%, the Navy tape method 20.4%, the Deurenberg BMI formula 24.0%, Jackson–Pollock 3-site calipers with Siri 18.5% (density 1.0565; the page says no study it cites checked the 3-site version against DXA). Where and how to measure follows Cedars-Sinai and Woolcott & Bergman (waist at the top of the hip bones), the Army's 2013 worksheets (DA Forms 5500 and 5501: three readings averaged) and Burns et al. (two skinfold readings, a third if they differ by more than 2 mm).
- **The wedge:**
  - all seven methods of Burns et al. 2019, Table 3, on the same 437 college students against one scanner, as a table and the hero figure (method minus DXA with the 90% CI): every method read low on average, by 1.0 (underwater weighing) to 4.9 points (a hand-held device); average miss (MAPE) 11.7% (seven-site skinfolds) to 21.9%; average difference inside the ±2.7-point equivalence margin: underwater weighing, skinfolds, the Bod Pod and the four-electrode analyzer (single readings missed by more);
  - the two home formulas on CDC's own DXA scans (our calculation, NHANES 2011–2018, 10,864 adults aged 20 to 59): relative fat mass missed by 3.1 points on average, the Deurenberg formula by 4.4 (10.4% and 14.0% of the scan's reading); the page says those shares can't be set against the students' (CDC's scans average 32.9% body fat, the students' 27.0%);
  - the formulas disagree for the same person: more than 5 points apart for 38% of US women and 15% of men (median gap 4.1 and 2.4 points), drawn as the second figure (within 3 points / 3 to 5 / more than 5: women 37 / 25 / 38%, men 60 / 25 / 15%);
  - what a measuring slip costs (our calculation): 1 inch on the waist moves relative fat mass by 0.9 points for the typical US adult, 5 lb on the scale moves the Deurenberg estimate by 0.9 to 1.0, a height 1 inch short by 1.0 to 1.1; the tape method 1.2 to 1.9 and 2 mm at each skinfold site 1.7 to 1.9 at stated example people;
  - scales and clinic devices: CDC's impedance documentation (how the test works; percent fat "subject to additional error"; who was not tested), three smart scales against DXA (Frija-Masson et al., 2021: median weight differences 0 to 0.3 kg, fat mass 2.2 to 4.4 kg low), InBody 770 and SECA mBCA 515 (Lahav et al., 2021), the tape method in 1,407 Army recruits (Foulis et al., 2023);
  - DXA itself (CDC: the most widely accepted method; under 20 µSv; the 5% lean-to-fat software option; the 450 lb and 6′5″ table limits), underwater weighing, the Bod Pod and near-infrared, each with its Table 3 row.
- **FAQ:** 10 questions from the ledger's owned queries: at home, most accurate, scale accuracy, how scales measure body fat, calipers, tape measure, InBody, Bod Pod, why methods differ, how much body fat. JSON-LD equals the visible text.
- **Head:** title "How to Calculate Body Fat Percentage: Home Methods vs DXA"; new meta description, OG and Twitter text (with `twitter:title` and `twitter:description`); the preferred image (§2); JSON-LD `@graph`: Article (`@id` and `datePublished` 2026-10-07 kept, `dateModified` `{TODAY}`, author and publisher named, image list, `primaryImageOfPage`, citations), BreadcrumbList (kept), FAQPage. The menu now marks Guides, in both menus.
- **Build record:** `research/how-to-measure-body-fat-build/`: `SPEC.md`; `htm_stats.py` and `htm_stats.json` (our calculation; asserts its sample equals `bfc_stats.json`); `burns_2019_table3.json` (Table 3, typed in from the paper); `gen_htm.py` (writes the page; stops unless every printed figure equals the stats, the table or a source value typed in, every outside link is a registry URL and no figure label collides); `htm_test_playwright.py`.

### 2. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/how-to-measure-body-fat-{16x9,4x3,1x1}.png` (the hero: seven dots with their interval lines on dashed zero lines, no words or numbers), drawn by `research/preferred-images/pref_images.py` (new `htm` drawing). Named in `og:image` (with `og:image:alt`), `twitter:image`, the Article image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`.
- Deleted: `blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png` (the old text card; only this page used it).

### 3. Registry, page map, DESIGN.md, styles.css
- `research/data-sources.csv`: 3 new rows, read in chat 2026-10-29: `frija-masson-2021-smart-scales` (three smart scales against DXA; the paper's signed "absolute error"), `lahav-2021-inbody-seca` (InBody 770 and SECA mBCA 515 against DXA), `nhanes-bia-documentation` (CDC's impedance method and exclusions). `blog/how-to-measure-body-fat` added to `pages_served` of `nhanes-2011-2018-dxa`, `rfm-woolcott-2018`, `foulis-2023-circumference-dxa`, `army-tape-worksheets`, `body-fat-equations` and `gallagher-2000-bf-ranges`; notes on `body-fat-method-validation` (all seven Table 3 rows, the equivalence results, the devices, the pre-test routine; its WKU conference-abstract endpoint is no longer cited) and `nhanes-2011-2018-dxa` (the CMB-021 numbers; DXX_J re-read); Topend Sports' Siri page added to `body-fat-equations`' endpoints (it prints 495 ÷ density − 450; the Jackson-Pollock page prints only the density equations).
- `research/page-map.csv`: the row's wedge, status and notes (`data_source` stays `body-fat-method-validation`).
- `DESIGN.md`: "Tables with long row labels (CMB-021)".
- `assets/css/styles.css`: `.flow .data-table--wrap th[scope="row"] { white-space: normal; }`, so a table whose row labels are names of several words fits a 320 px phone. Only this page uses the class.

### 4. Dates
- The page ships as a `{TODAY}` template (`"today": true`) for its Article `dateModified`; its sitemap `lastmod` is a `{TODAY}` edit.

### 5. Detector baseline
- `research/impeccable-baseline/2026-10-29-cmb021-390x844.json`: 41 pages, before Calculate: 262 → 255 (this page 7 → 0; no other page changed); results open carried over (88; no calculator changed).

### 6. Fixes from chat's checks and the independent fact-check
**Chat's own checks, fixed on the draft:**
- both tables overflowed phones (291 px in a 240 px frame at 320; the slip table 429 px even at 390): `.flow` tables keep row labels on one line, so the page's tables take `.data-table--wrap` (styles.css), the slip table became four groups with short labels, the seven-method column head became "Below DXA", and a number keeps its unit on one line (no-break space). Both fit at 320, 360, 390 and 1280;
- two figure headings ran past the 320-unit viewBox (the generator's label check stopped the build): shortened (that figure later went, below);
- the preferred image sat left of center (the −6 to +1 axis): drawn on −6.5 to +0.5 so the outer grid line and the zero line sit evenly;
- facts: "the best method" → "the method with the smallest miss"; "which is why the Army's worksheets…" (a cause no source states) cut; the takeaway "a slip of the tape moves the answer by 1 to 2 points" next to a 0.9 example → "about a point", with the 1-inch waist and 5-lb figures; "for a 5′4″ woman" (the tape equation's slip doesn't depend on height) cut; "US adults" → "US adults aged 20 to 59" wherever the check is quoted on its own (answer, three FAQ answers);
- sources re-read live in chat before writing: Burns Table 3 and Methods (devices: Valhalla 1990B with four electrodes on the right hand and foot, lying down; Futrex on the biceps; Tanita BF-556; Omron HBF-306), Lahav (PubMed abstract: limits of agreement, the normal-weight sentence), Frija-Masson (JMIR: the setting, signed errors), CDC BIX_C (method, exclusions, the 6-hour fast) and DXX_J (radiation, the 5% option, limits);
- anti-slop: 6 fixes (writing about the page 3: "in this guide", "this guide’s examples", "The next section shows…"; an unsourced cause 1: "which is why the Army’s worksheets…"; inflation 1: "the best method"; a bold label posing as a heading 1: "Three more checks." → an h3). Rescored from the built HTML after the fact-check fixes: 0 tells and 0 em dashes in 3,576 words of body prose (the old page: 0 tells in 1,268 words).

**Independent fact-check (separate agent: its own code on CDC's raw files, the page in Chromium, sources re-read live): 0 FAIL, 7 WARN, 13 NOTE, all settled.**
- Passed: 21 of the 22 "our calculation" figures reproduce with its own code (n 10,864, the average misses, within 5 points, the formula gaps, the slips, the women's median; the 22nd is the NOTE on the men's median below), the worked example and every slip cell (12 of 12), the 7 equations against their sources, all 7 Table 3 rows (21 values) and every Burns detail the page uses, Foulis, Lahav, Frija-Masson, CDC BIX_C and DXX_J, DA Forms 5500 and 5501 (fetched live), the FAQ JSON-LD (10 of 10 equal), both figures against the tables and text; no em dashes, no visible dates, no fitness tiers, US spelling, no horizontal scroll; all internal links resolve. Tie handling changes no conclusion.
- WARN, fixed (7):
  - the takeaway and the "most accurate" FAQ set the waist-and-height formula's 10.4% beside Burns's 11.7% without the caveat, and the shares aren't comparable anyway: CDC's scans average 32.9% body fat against the students' 27.0%, so the same miss in points is a smaller share. The formulas' misses are now given in points (3.1 and 4.4), with the shares and the reason they don't line up with Burns's; the average-miss figure that drew both on one axis is gone, replaced by a figure of how far the two formulas land from each other for the same person (within 3 points, 3 to 5, more than 5);
  - "weighed within 0.3 kg" read a signed median as a bound (one scale's upper quartile was 0.7 kg): "median weight differences of 0 to 0.3 kg" (takeaway, scales section, FAQ);
  - the "most accurate" FAQ answered "DXA", which no cited source says: "No method is exact. DXA, which CDC calls the most widely accepted method of measuring body composition, is the reference the studies here check other methods against";
  - the title and meta text said "every method", and the page teaches a 3-site caliper method no cited study checked against DXA: title "Home Methods vs DXA", "how close tested methods … come to a DXA scan", the section heading "How close tested methods get to a DXA scan", and the calipers step and FAQ say no study cited here checked the 3-site version;
  - "within the study's margin of ±2.7 points" read as individual accuracy (the test is on the average difference): "Average difference inside the study's ±2.7-point equivalence margin … single readings missed by more";
  - "A reading from one method says little about a reading from another" overstated it (the two formulas correlate at r = 0.90 for women and 0.92 for men): "Two methods can differ by several points for the same person";
  - the link for Siri's equation went to Topend's Jackson-Pollock page, which doesn't print it: it links Topend's Siri page now (Siri 1961, as Topend cites it), added to the registry.
- NOTE, fixed (10): the men's 20–39 median, 26.2%, sits on a tie boundary (26.13 to 26.18 by tie order; DEVLOG §5's percentile item), so both medians print as whole percents ("about 38% for women and 26% for men"); "for half of women they were more than 4.1 points apart" → "the median gap was 4.1 points for women and 2.4 for men"; the method note promised confidence intervals the page doesn't show → it gives the margins (under 2 percentage points for each share, under 0.4 for each average miss) and the counts behind the formula figures (10,751 with a measured waist, 10,829 with a BMI, 10,747 with both); formula-against-formula figures say "in CDC's survey" (no scan is involved) and every quoted check names ages 20 to 59; Lahav's "deviations" → "its underestimate was largest at normal weight"; the intro's "is what those equations are checked against" → "is the reference in the studies below"; the calipers answer says the 3-site version wasn't tested; the scales section says CDC's own test used electrodes on the right hand and foot; Gallagher's full title; the old figure's lower-case "bod pod" went with it.
- NOTE, kept (3): the Gallagher ranges could not be re-read live (PMC's browser check): the registry's re-check item (DEVLOG §5 [P2]) stands, and the chart page uses the same values; "the Army's 2013 worksheets": a June 2023 DA 5500 has the same three-readings rule, and the page cites the 2013 editions chat read; the agent could not fetch the Army protocol PDF or Serra 2009 (verified in earlier batches) and confirmed the coefficients elsewhere (Foulis's methods, Topend).

### Chat results (fresh GitHub clone of `7662c95` + this package)
- **Gates and dates:** FIX.md steps 0–5 as written, run twice (today, and with `CMB_TODAY=2026-10-31` and commit dates set to that day): dry-run and apply 10 / 7 / 1 / 1; gates 3.1–3.9 pass; 3.10 `0 1 1 1 10 0 0 1 1 2 2 2 30 0 1 1 1 3 0 29`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **Data:** `htm_stats.py` rebuilds `htm_stats.json` byte for byte from CDC's raw files; `pref_images.py` redraws the three preferred images byte for byte.
- **Tests:** page test 348 checks, 0 failures on the applied clone (22 deliberate breaks each failed it; SPEC.md lists them); Chromium end-to-end 1,316 checks, 0 failures; jsdom 95 / 0; FAQ opens on all 29 FAQ pages; menu 40 / 40; no page wider than the screen at 360 / 390 / 1280 (120 checks).
- **Detector (impeccable 0.1.14):** this page 7 → 0 at 390×844 and 18 → 0 at 1280×800; sitewide static 262 → 255 (41 pages, `research/impeccable-baseline/2026-10-29-cmb021-390x844.json`); no other page changed.

### Not in this batch (logged for §5)
- The menu's current-page marker stays inconsistent on `/average-weight/`, `/body-fat-percentage-chart/`, `/blog/bmi-for-athletes/` and `/blog/what-is-bmi/` (they mark "Obesity Statistics"); this page is fixed. The sitewide fix plus a `check_structure` rule stays in §5.
- `/body-fat-calculator/` cites "Siri WE, 1956" next to Topend's Jackson-Pollock page, which prints only the density equations; Topend's Siri page (which cites Siri 1961) is the right link. A sources-line fix, so it moves that page's dates: do it the next time the calculator changes.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-021-how-to-measure/`.
0.3 `git log --oneline -4 | grep -c "CMB-020"` → 1 or more. If 0, STOP: CMB-020 must run first.

### 1. Dry run
`python3 research/cmb-021-how-to-measure/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 10 new files, 7 replaced files, 1 edits, 1 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-021-how-to-measure/apply_build.py`
Must print exactly: `applied: 10 new files, 7 replaced files, 1 edits, 1 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py blog/how-to-measure-body-fat/index.html` → `blog/how-to-measure-body-fat/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py blog/how-to-measure-body-fat/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `blog/how-to-measure-body-fat/index.html`):
- `grep -o '{TODAY}' $PG | wc -l` → `0`
- `grep -o "net/blog/how-to-measure-body-fat/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $PG | wc -l` → `1`
- `grep -o '"datePublished": "2026-10-07"' $PG | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `10`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o '<article' $PG | wc -l` → `0`
- `grep -o 'application/ld+json' $PG | wc -l` → `1`
- `grep -o 'max-image-preview:large' $PG | wc -l` → `1`
- `grep -o 'href="/blog/" class="active" aria-current="page"' $PG | wc -l` → `2`
- `grep -o 'aria-current="page"' $PG | wc -l` → `2`
- `grep -o 'data-table--wrap' $PG | wc -l` → `2`
- `ls assets/images/preferred/ | wc -l` → `30`
- `ls blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png 2>/dev/null | wc -l` → `0`
- `grep -o "'/blog/how-to-measure-body-fat/': 'how-to-measure-body-fat'" scripts/check_images.py | wc -l` → `1`
- `grep -c 'Tables with long row labels (CMB-021)' DESIGN.md` → `1`
- `grep -c 'data-table--wrap' assets/css/styles.css` → `1`
- `grep -c '^frija-masson-2021-smart-scales,\|^lahav-2021-inbody-seca,\|^nhanes-bia-documentation,' research/data-sources.csv` → `3`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'blog/how-to-measure-body-fat'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `29`
3.11 Reproducing `htm_stats.json` needs CDC's raw DXA files, which stay out of the repo (size; registry `nhanes-2011-2018-dxa`). Record `skipped (raw DXA files not in repo)`; chat ran it (see Chat results).
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /blog/how-to-measure-body-fat/ rebuilt to the D-14 pattern: the steps for four home methods worked by hand, every method against DXA (all seven of Burns 2019 Table 3, the two home formulas on CDC NHANES 2011-2018 scans, smart scales, InBody, the tape method), what a measuring slip costs; preferred images; tables wrap on phones; menu marks Guides (CMB-021)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb021-dates.txt; echo $?; grep -c '^ok' /tmp/cmb021-dates.txt; grep '^BAD' /tmp/cmb021-dates.txt; rm /tmp/cmb021-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-021 HOW-TO-MEASURE
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-020 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 skipped (raw DXA files not in repo) | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines: <none or list>
devlog: <git log --oneline -1>
git status: <clean or list>
```
