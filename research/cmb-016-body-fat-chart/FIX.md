# CMB-016 BODY-FAT-CHART — `/body-fat-percentage-chart/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-21 against GitHub `main` `0c418db` (after CMB-015). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/body-fat-percentage-chart/` owns 501 keywords worth 283,690/mo (`research/keyword-ledger.csv`), page 5 of the D-14 rollout:
  - "body fat index" 74,000, "body fat percentage women" 27,100, "body fat percentage men" 18,100, "body fat percentage chart" 14,800 (primary), "ideal fat percentage female" 9,900;
  - the "N% body fat" long tail: "15 body fat men" 6,600, "20 percent bodyfat" 4,400, "male 20 body fat" 4,400, "30 body fat female" 3,600, "25 body fat women" 2,900, "18 body fat men" 2,400, "20 body fat female" 2,400 and hundreds more;
  - "average fat percentage" 3,600, "normal body fat percentage for women" 5,400, "body fat chart" 5,400.
- **The old page broke site rules:**
  - three page-level `<style>` blocks (old chart cells, page styles, a tool with a gradient header) and inline-styled containers;
  - an FAQ written as plain headings with no FAQPage JSON-LD;
  - an OG image with text (`og-body-fat-percentage-chart.png`) and no preferred image;
  - detector: 8 findings at 390×844 and 17 at 1280×800.
- **SERP (owner's pastes of google.com, US/English, 2026-10-21, not personalised):**
  - "body fat percentage chart": a row of photo charts; the AI Overview quotes fitness-industry tiers and healthy ranges by age. People also ask: "What is a good body fat percentage by age?", "What is the lowest bf a woman can have?", "Is 30% body fat chubby?", "Is 20% body fat skinny?".
  - "body fat index": the AI Overview contrasts body fat with BMI. People also ask: "What's a good body fat index?", "Is 20% body fat realistic?", "Is 18% body fat chubby?".
  - "body fat percentage women": the ranges for women by age. People also ask: "Is 140 pounds fat for a 5'4" female?" (plus a photo question and an attractiveness question, left out). The owner's own bodyfatpercentagecalc.com shows at about position 16 (Search Console box).
  - Gap: every result restates ranges. None shows what US adults measure for every percentage, none sets a reading against a real distribution by age, none shows how the provisional ranges sit against today's CDC scanner at the same BMI. That is the wedge.

## What changes

### 1. `/body-fat-percentage-chart/` rebuilt (D-14, guide form with the rank tool)
- **Order:** H1 "Body Fat Percentage Chart for Women and Men by Age" and the byline → three intro paragraphs (the searcher's questions; the stakes, CDC's averages; the promise) → key takeaways (answer first) → disclaimer → hero figure → 9 contents chips → the chart → the rank tool → every percentage → healthy body fat → body fat and BMI → age and sex → printable chart → 10 FAQ → sources and method → one related block.
- **Hero figure:** the provisional ranges for women and men aged 20–39, 40–59 and 60–79 as banded bars, cut-offs labelled.
- **The chart:** a `.weight-chart` table, six rows (sex × age) by low / healthy / high / very high, plus the US median from CDC's scans (`not scanned` for 60–79); row anchors `#women-20-39` … `#men-60-79`. Ranges: Gallagher et al., 2000, as tabulated in J Public Health Afr 2016, Table 1 (registry `gallagher-2000-bf-ranges`), labelled provisional, with the ethnic-group caveat.
- **The rank tool** (kept, rebuilt on the shared calculator parts, no page-level style): sex, body fat % and age 8–79 → the share of US women or men of that 4-year or 10-year age group (8–11 … 50–59) with more body fat (shares at every whole percent, worked out as the tables' are, interpolated in between), the provisional range for the age, a percentile bar and the age group's percentiles. Under 20: percentiles only; 60–79: the provisional range only (CDC scanned ages 8–59).
- **Every percentage (the wedge, part 1):** two tables, men 5–40% and women 10–50%, each row the share of US adults aged 20–39 and 40–59 with more body fat, tinted and labelled with the provisional range at that age; anchors `#men-15`, `#women-30`. Tails print "more than 99%" and "under 1%".
- **Body fat and BMI (the wedge, part 2):** body fat at each whole BMI (median and middle half, women and men 20–59), body fat in each BMI category, the 5′4″ / 140 lb example, and how the provisional ranges' BMI-25 edge sits on CDC's scanner: adults within half a point of a BMI of 25 averaged 24.3% (men 20–39) and 35.6% (women 20–39), against the 20% and 33% the ranges put there.
- **Age and sex:** +2.9 points for men and +3.4 for women from their 20s to their 50s, women 10.8 to 12.0 points above men in every decade (each 95% CI excludes 0), children and teens (boys fall, girls rise), no scans over 59; percentile tables for every age group 8–59.
- **Printable chart:** `assets/images/charts/body-fat-percentage-chart.png` (1360 × 902): the chart table with the US median and the sources, an `<img>` in its own section, linked to itself, listed in the image sitemap; its cells in `bfpc_chart.csv`.
- **FAQ:** 10 questions: 8 People-also-ask questions as asked, then the ledger's average and the old page's 60-and-over question. JSON-LD equals the visible text.
- **Head:** `<title>` "Body Fat Percentage Chart: Women and Men by Age, US Averages" (60 characters; not "(CDC Data)", since CDC didn't make the ranges); new meta, OG and Twitter text; the preferred image (§2); one JSON-LD graph: Article (H1 as headline, author and publisher named, image list, `mainEntityOfPage` with `primaryImageOfPage`, `dateModified`), the Dataset (unchanged CSV download, creator named), BreadcrumbList (page name = H1), FAQPage. The three `<style>` blocks, the visible breadcrumb and the old OG image go.
- **Build record:** `research/body-fat-chart-build/`: `SPEC.md`; `bfpc_stats.py` → `bfpc_stats.json` (stops unless it reproduces `research/body-fat/bf_results.json`, the numbers on other pages, and stops if storing a value would change any figure the page prints: every figure is rounded once); `gen_bfpc.py`; `chart_bfpc.py` with `bfpc_chart.csv`; `bfpc_test_playwright.py`.

### 2. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/body-fat-percentage-chart-{16x9,4x3,1x1}.png` (the hero's bars without labels), drawn by `research/preferred-images/pref_images.py` (new `body_fat` drawing; the script now takes page names, so the other 12 files are not redrawn). Named in `og:image`, `twitter:image`, the Article image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`.
- Sitemap: the page's `<image:image>` for the printable chart.
- `body-fat-percentage-chart/og-body-fat-percentage-chart.png` (a stats card with text) is referenced nowhere after this and is deleted.

### 3. Registry, page map, DESIGN.md
- `research/data-sources.csv`: no new rows; 7 rows list the page (`nhanes-2011-2018-dxa`, `gallagher-2000-bf-ranges`, `cdc-about-bmi`, `cdc-adult-bmi-categories`, `cdc-calculating-bmi`, `cdc-child-bmi-categories`, `body-fat-method-validation` for the scales-and-calipers line); notes added on the DXA row (CDC's documentation re-read 2026-10-21: ages 8–59, the 450 lb / 6′5″ exclusion, valid scans rarer at higher BMI, the BCA option adding 5% of lean mass to fat mass) and the Gallagher row (the paper's table still out of reach; abstract re-read).
- `research/page-map.csv`: the row's wedge and notes (data source unchanged, `nhanes-2011-2018-dxa`, passing).
- `DESIGN.md`: "Body fat rank tool and lookup tables (CMB-016)".

### 4. `styles.css`
- `.weight-chart--fit` (no 600 px minimum, cells may wrap), for the three-column tables that must fit a 320 px screen.
- `.er-section h3` (results headings inside a section that has its own `h2`); `.data-table .cell-kg` (a muted second line in a data table); `.bfr …` sizes for the tool.
- All new selectors are scoped: no other page uses `.weight-chart--fit`, `.bfr`, an `h3` in `.er-section` or `.cell-kg` in a `.data-table` (checked across all 40 pages).

### 5. Dates and removals
- The page ships as a `{TODAY}` template (`"today": true`) for its schema `dateModified`; the sitemap `lastmod` is a `{TODAY}` edit.
- One other page changes, by one number: `/age-bmi-calculator/` printed the average for men in their 50s as 28.4%, from `bf_results.json`'s 28.35 rounded a second time (unrounded 28.347, see §6). An edit makes it 28.3% and another moves its sitemap `lastmod` to `{TODAY}` (the page has no schema `dateModified`). No other page prints a double-rounded body-fat figure (every page that quotes `bf_results.json` checked); no other page's text, links or JSON-LD change.
- `research/body-fat/tool_test_jsdom.js` tested the old tool's markup and is deleted; `bfpc_test_playwright.py` covers the new tool.

### 6. Fixes from chat's checks and the independent fact-check
**Chat's own checks, fixed on the draft:**
- the hero's cut-off labels met ("20%25%"): they print without "%";
- BMI-category cells wrapped badly: the middle half moved to a second line (`.cell-kg`);
- the tool's percentile table and the three-column lookup tables overflowed a 320 px screen (273 px in a 240 px frame): compact cells and `.weight-chart--fit`;
- labels met at 1280 px in both line figures: axis labels and titles moved down;
- the tables and the tool rounded halves differently ("91%" against "90%"): both round halves up;
- the detector's nested-card finding: the tool card sits after its section, not inside it.
- anti-slop: 9 fixes (re-explaining 4, vague wording 3, staging 1, hedge 1).

**Independent fact-check (separate agent, on the draft).** It rebuilt the sample from CDC's raw files with its own code (59 strata, 121 PSUs, df 62; 10,864 adults) and matched every mean, CI, difference, share, percentile, figure value, the chart, its CSV and PNG, the rank tool's data and the FAQ JSON-LD, apart from the items below. Live sources re-read: CDC DXX_J, the Gallagher abstract, CDC About BMI and the adult categories. All settled before packaging (detail in `SPEC.md`):
- **FAIL, double rounding (fixed):**
  - men 50–59 averaged 28.347%; stored as 28.35, the page printed 28.4% in the age table, the age text and the FAQ. Now 28.3%. `/age-bmi-calculator/` carried the same 28.4% (§5);
  - four lookup shares stored at 0.1 printed one point high: men 20–39 at 21% (78 → 77), men 40–59 at 31% (29 → 28), women 20–39 at 36% (62 → 61) and at 42% (27 → 26). The rank tool's shares had the same cause (22 of 882 whole-percent answers one point high, e.g. a boy of 9 at 20%: 91% → 90%), and three BMI-figure labels moved (now 44.7, 15.5, 32.1);
  - the fix: `bfpc_stats.py` stores 4 decimals (the tool's shares 2–3) and stops if storing would change any printed figure; the page prints the 4-decimal mean; the tool takes its percentiles at the 1 decimal the tables print. The page test now also checks these values as typed in from the agent's report.
- **WARN (fixed):**
  - the BMI-25 cut-offs were credited to "the 2000 study"; they are the tabulation's (J Public Health Afr 2016, Table 1). The paper's predictions differ by ethnic group, and its table is still unread;
  - "the charts state no data source" was wrong (charts that copy the athlete and fitness tiers name their source). Now: the tiers "come from a fitness organization’s chart and aren’t matched to BMI or age";
  - "most cited" / "most charts copy" → "widely cited" / "many charts use";
  - "the tables above are all DXA" → every US figure comes from CDC's scans, whose software adds 5% of lean mass to fat mass.
- **NOTEs taken:** the method says the intervals tested the differences (none is shown; the CSV gives each average's standard error) and that every figure is rounded once; meta and OG say "10–50% for women, 5–40% for men"; the noscript line says what the tables cover; the title drops "(CDC Data)"; the lowest-body-fat answer says it reports what US women measure; the body fat index answer adds the fat mass index; "rise together, but loosely" became "on average … a wide spread".
- **NOTE kept, tie order:** readings are recorded to 0.1%, so the midpoint rule after numpy's default sort (`compute_bf.py`'s method, kept so the page equals its CSV download and the figures other pages quote) depends on how tied readings are ordered; an order-free method moves 14 of 70 age-table percentiles by 0.1. The one derived figure that read differently in the agent's build, the women-minus-men gap at each BMI, now prints whole points ("about 11 to 13"), the same under every order. Moving all three files to the order-free method together is logged below.
- **Not reachable** for the agent or chat: Gallagher's own table (the `[P2]` item stays open).

### Chat results (fresh GitHub clone of `0c418db` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-23` and commit dates set to that day. Both runs: dry-run and apply `12 / 7 / 3 / 2`; gates 3.1–3.9 pass; 3.10 `0 1 1 10 0 0 2 15 4 1 3 0 0 31 1 1`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **3.11 in chat:** `bfpc_stats.py` on CDC's raw DEMO, DXX and BMX files (2011–2018) rebuilds `bfpc_stats.json` byte for byte and reproduces `research/body-fat/bf_results.json` (means, n, percentile curves, band shares).
- **Browser checks (Chromium, on the applied tree served locally):**
  - `bfpc_test_playwright.py`: 519 checks, 0 failures. It covers the chart table against the cut-offs, the stats and `bfpc_chart.csv`; all 77 lookup rows with their anchors, labels and tints; the BMI, BMI-25 and age tables; the BMI figure's 44 hover labels; the fact-check's corrected values (typed in); the printable image's size, alt text and link; the CSV download; the robots tag, OG and Twitter images, the JSON-LD image list, `primaryImageOfPage` and the preferred files at their sizes; seven tool cases plus an out-of-range reading; 9 chips and 10 FAQ; JSON-LD against the visible text; SVG label collisions at 390 and 1280; widths at 320, 360, 390 and 1280. Restoring the old 28.4% or the old 78% cell fails it.
  - Calculator jsdom 95/95; calculator end-to-end 1,316 checks, 0 failures; FAQ opens on all 26 pages that have one; no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Gate test:** in a copy, the old `og:image` and a dropped image-sitemap entry each fail `check_structure.py`.
- **Detector (impeccable 0.1.14):** this page 8 → 0 at 390×844 and 17 → 0 at 1280×800; `/age-bmi-calculator/` unchanged (18; one number changed). Sitewide static 307 → 299 at 390×844, only this page changed (`research/impeccable-baseline/2026-10-21-cmb016-390x844.json`).
- **Live R4 (owner):** the detector on production `/bmi-chart/` printed only the consent-banner note, so 0 findings. That closes CMB-015's open item.

### Not in this batch (logged for §5)
- Gallagher et al. 2000's own table is still out of reach; the cut-offs come from the registry's tabulation. The `[P2]` re-check stays open.
- The owner's bodyfatpercentagecalc.com and this page compete for body-fat queries; owner decides whether that is a deliberate hedge.
- Image license metadata (the "Licensable" badge): the page already offers its CSV under CC BY 4.0; extending that to the chart images is the owner's call.
- Order-free weighted percentiles (one weight per distinct reading) in `research/body-fat/compute_bf.py`, `bfpc_stats.py` and the CSV download together, then the pages that print them regenerated: moves some percentiles by 0.1. `[P3]`.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-016-body-fat-chart/`.
0.3 `git log --oneline -4 | grep -c "CMB-015"` → 1 or more. If 0, STOP: CMB-015 must run first.

### 1. Dry run
`python3 research/cmb-016-body-fat-chart/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 12 new files, 7 replaced files, 3 edits, 2 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-016-body-fat-chart/apply_build.py`
Must print exactly: `applied: 12 new files, 7 replaced files, 3 edits, 2 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py body-fat-percentage-chart/index.html` → `body-fat-percentage-chart/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py body-fat-percentage-chart/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `body-fat-percentage-chart/index.html`):
- `grep -o '{TODAY}' $PG | wc -l` → `0`
- `grep -o "\"dateModified\": \"$(date +%F)\"" $PG | wc -l` → `1`
- `grep -o "body-fat-percentage-chart/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `10`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o 'og-body-fat-percentage-chart.png' $PG | wc -l` → `0`
- `ls body-fat-percentage-chart/ | wc -l` → `2`
- `ls assets/images/preferred/ | wc -l` → `15`
- `grep -o '<image:image>' sitemap.xml | wc -l` → `4`
- `grep -o "'/body-fat-percentage-chart/': 'body-fat-percentage-chart'" scripts/check_images.py | wc -l` → `1`
- `grep -o 'weight-chart--fit' assets/css/styles.css | wc -l` → `3`
- `ls research/body-fat/ | grep -c tool_test_jsdom` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'body-fat-percentage-chart'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `31`
- `grep -c 'to 28.3% in their 50s' age-bmi-calculator/index.html` → `1`
- `grep -o "age-bmi-calculator/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
3.11 Reproducing `bfpc_stats.json` needs CDC's raw DXA files, which stay out of the repo (size; registry `nhanes-2011-2018-dxa`). Record `skipped (raw DXA files not in repo)`; chat ran it (see Chat results).
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /body-fat-percentage-chart/ rebuilt to the D-14 pattern with US body fat on CDC DXA scans (NHANES 2011-2018) for every whole percent, the rank tool on shared calculator parts, body fat at each BMI and the provisional ranges' BMI-25 edge on CDC's scanner; printable chart image and preferred images; /age-bmi-calculator/ men's 50s average corrected to 28.3% (CMB-016)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb016-dates.txt; echo $?; grep -c '^ok' /tmp/cmb016-dates.txt; grep '^BAD' /tmp/cmb016-dates.txt; rm /tmp/cmb016-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-016 BODY-FAT-CHART
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-015 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 skipped (raw DXA files not in repo) | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
