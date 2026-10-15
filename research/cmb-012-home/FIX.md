# CMB-012 HOME — homepage rebuilt to the D-14 pattern, with where your BMI ranks among US adults

Built and tested in chat on 2026-10-14 against GitHub `main` `c4004c8` (after CMB-011). Tools: Chromium (Playwright), jsdom 24, impeccable engine 0.1.14. An independent fact-check by a separate agent ran on the draft; its findings are fixed below.

## Why
- **Demand.** `/` owns the biggest keyword group on the site: "bmi calculator" close variants, 2,240,000/mo, plus "calculating body mass" 49,500 and "bmi chart calculator" 18,100 (`research/keyword-ledger.csv`). Search Console baseline: average position 44.6 on "bmi calculator", 126 impressions and 7 clicks in 7 days.
- **The old page was the pre-D-14 template:**
  - Key takeaways sat inside the calculator card.
  - The inputs had no `for`/`id` (backlog P1).
  - A "When to see a doctor" list gave unsourced thresholds ("BMI below 16.0: seek prompt consultation", "consistent upward BMI trend").
  - A metric comparison table rated methods with unsourced pros and cons.
  - "BMI around the world" ended on "research … is ongoing".
  - A 15-card link grid kept a build note ("One card per destination — each links to a distinct page").
  - The WebSite JSON-LD declared a `SearchAction`. The site has no search, so its target URL just returned the homepage.
  - Detector: 20 findings at 390×844 (11 nested cards, 4 cramped padding, 2 side tabs, 2 skipped headings, 1 grey on colour) and 48 at 1280×800.
- **SERP (owner's pastes, 2026-10-14):**
  - Every top-10 result is a calculator or a calculator plus an explainer: NHLBI, CDC, Calculator.net, American Cancer Society, Harvard, Mayo, PBRC, MDCalc.
  - The AI Overview gives the formula, the six adult categories and BMI's limits.
  - People also ask: "What is the correct BMI for my age?", "What is the BMI of 70 kg 170 cm?", "Is a 23 BMI chubby?", "What is the new BMI chart for 2026?".
  - No result tells the reader where they stand among real US adults. That is this page's wedge.

## What changes

### 1. `/` rebuilt to the men-page pattern (D-14)
- **Tool first.** The H1, a two-line hook and the calculator. Inputs get `for`/`id`. The Calculate button's bottom edge sits at 770 px on a 390×844 phone, above the fold. Scale labels use the CDC names: Under, Healthy, Over, Class 1, Class 2+.
- **The wedge: rank among US adults.**
  - After Calculate, a rank box shows, for example, "Higher than 28% of US adults", with a marker against the median, 28.2.
  - A sentence gives the rank among men only and among women only.
  - The data are CDC NHANES August 2021–August 2023: 5,929 adults aged 20 and over, survey-weighted, pregnant women excluded.
- **Below the tool:**
  - Key takeaways open with a 55-word answer (formula plus CDC categories), followed by a medical disclaimer and contents chips.
  - "How to read your result" walks the starting values (5′7″, 160 lb, BMI 25.1) through every output. Its figure is "one pound over the line": 159 lb is 24.9, 160 lb is 25.1.
  - US adults compared: a percentile table for all adults, men and women, and a 72.4% stat callout.
  - Adult categories with the share of US adults in each, plus a 100-square figure: 2 underweight, 26 healthy, 32 overweight, 31 class 1–2, 9 class 3.
  - Healthy weight by height for six heights, in pounds and kilograms each worked out on its own.
  - BMI by hand: US, metric and the centimetre formula, from CDC.
  - When BMI misleads: muscle, where fat sits (NHLBI waist), age, Asian ancestry (WHO 2004), and the 2025 Lancet Commission.
  - Children and teens: the CDC percentile table.
  - Health: NHLBI, Wing 2011, and Health E-Stat 119 on underweight.
  - Six common situations, the FAQ, sources and method, and one related block.
- **FAQ.** 8 questions. The four People-also-ask questions come first, as asked. The rest: normal BMI, men vs women, "Is BMI a percentage?", accuracy. The JSON-LD equals the visible text.
- **Head.**
  - New meta, OG and Twitter descriptions, and a new data-bearing OG image (`assets/images/og/home-bmi-us-adults.png`, US adults by category).
  - The WebApplication is described. The `SearchAction` is removed.
  - The `<title>` is unchanged; the backlog P3 decision stays open.
- **Data.** `research/home-build/home_stats.py` → `home_stats.json`. The script stops unless it reproduces:
  - NCHS Series 3 No. 50: medians 28.2 and 28.3, means 29.4 and 30.0, 95th-percentile weights;
  - the crude NCHS prevalences: underweight 1.6%, overweight 32.1%, obesity 40.3%, class 3 9.4%. All reproduce exactly.
- **Build record.** `research/home-build/`: `SPEC.md`, `gen_home.py`, `og_home.py`, `home_test_playwright.py`.

### 2. Rank rule: homepage and men page
- "Higher than X%" now counts only adults with a lower BMI. "Lower than Y%" counts only those with a higher one.
- NHANES records BMI to one decimal. The old rule read the curve at the user's BMI, so it also counted people with the same BMI as lower; that adds 0.5–1 point.
- The men page uses the same rule. Its worked example moves from "higher than 32%" to "higher than 31%" (5′10″, 180 lb, BMI 25.8).

### 3. Shared results panel (`assets/js/calculator.js`)
- The converted unit shows one decimal both ways.
  - Example: metric mode showed the top of the healthy range at 170 cm as "72 kg (159 lbs)". 159 lb at 170 cm is BMI 25.0, overweight.
  - It now shows "72 kg (158.7 lbs)", matching imperial mode's "159 lbs (72.1 kg)".
  - This applies to the healthy-limit tiles, the ideal-weight BMI-range tile, milestones and the weight tile.
- The milestone change column says "−1 lb", not "−1 lbs".

### 4. Fixes from the independent fact-check
- **Men page.** "found the lowest death rates across BMI 23 to 33" becomes "found that the risk of death rose below a BMI of 23 and above 33". That is what Winter 2014 reports: reference 23.0–23.9, higher risk below 23, rising above 33. The FAQ text and JSON-LD are both changed.
- **`/blog/bmi-formula/`.**
  - The unsourced "A healthy PI is approximately 11–15 kg/m³" is removed. CDC and WHO publish no adult cut-offs for the ponderal index, as the homepage now says.
  - Its schema `dateModified` and `lastmod` follow the change (the date rule, §6).
- **Homepage draft, before this package:**
  - the pound range at 170 cm, now 118–158 lb, worked out on its own;
  - the body fat calculator described as estimating from tape or skinfolds, not "directly";
  - 72.4% labelled as the sum of the two Health E-Stat 111 rates;
  - all four WHO 2004 action points (23, 27.5, 32.5, 37.5);
  - Gallagher 2000 cited only for what its abstract states;
  - an underweight sentence quoted from Health E-Stat 119;
  - the Trefethen source added.

### 5. Registry and design notes
- `research/data-sources.csv`: 11 verified rows added, with what chat checked on 2026-10-14:
  - CDC child categories, About BMI, Calculating BMI;
  - Lancet Commission 2025;
  - NIDDK Body Weight Planner;
  - WHO TRS 854 and WHO 2004;
  - Winter 2014, Wing 2011, NHLBI 1998;
  - Trefethen.
  - `home` is added to the NHANES, NCHS and CDC rows it uses.
- `research/page-map.csv`: the `home` row is built, with `data_source` `nhanes-2021-2023-exam-files`. The data-sourcing check now passes for `home`. It still fails on 34 other rows whose `data_source` is free text; those were already failing.
- `DESIGN.md`: the one-decimal conversion rule, the rank rule and `.cat-dot`.
- `styles.css`: `.cat-dot`, a category dot in static tables. It is additive; no other rule changes.
- Tests:
  - `calc_e2e_playwright.py` expects the one-decimal conversion, checks that a converted limit never crosses 24.9, and adds the 170 cm / 70 kg case;
  - `research/men-pilot/rank_test_playwright.py` uses the new rank rule;
  - new `research/home-build/home_test_playwright.py`.
- New detector baseline: `research/impeccable-baseline/2026-10-14-cmb012-390x844.json`.

### 6. Dates follow the day you run this (new in `apply_build.py`)
- Five edits carry `{TODAY}`, which `apply_build.py` replaces with the box's local date. That is the same clock `git commit` uses:
  - `sitemap.xml` `lastmod` for `/`, `/men-bmi-calculator/` and `/blog/bmi-formula/`;
  - the formula guide's schema `dateModified`;
  - the formula guide's text change itself, which carries no date.
- `date_truth.py` therefore passes on whatever day this runs, as long as apply and commit happen the same day.
- The homepage and the men page carry no schema `dateModified`; calculator pages have none.

### Chat results (fresh GitHub clone of `c4004c8` + this package)
- **Gates:**
  - check_structure 40/40, plus the calculator.js and hub checks;
  - verify, schema and number audit clean;
  - markup clean on the 3 changed pages;
  - content-integrity exit 0 on every page and on calculator.js;
  - `date_truth` 40/40 after commits dated today and, with `CMB_TODAY`, a later day.
- **Calculators:**
  - jsdom 95/95;
  - Chromium end-to-end 1,316 checks, 0 failures (new metric case and the no-crossing check included);
  - homepage test 131 checks, 0 failures: rank for all adults, men and women in both units including both ends of the curve, SVG label collisions at 390 and 1280, page width at 320, 360, 390 and 1280, all 8 FAQ items;
  - men rank test 8/8.
- **Browser:**
  - FAQ opens with one tap on all 25 FAQ pages;
  - menu 41/41;
  - no page wider than the screen at 360, 390 and 1280;
  - at 320 the homepage no longer runs wider than the screen (it was 325 px). Two of its tables scroll 15–16 px inside their own frames.
- **Detector:**
  - homepage 20 → **0** at 390×844 and 48 → 0 at 1280×800;
  - with results open 20 → 0, both units;
  - sitewide static 348 → 328, no page worse;
  - results open on the 8 calculators 124 → 104.
- **Site probes** (text, UI, empty box) on the 3 changed pages: no new hits. The formula guide keeps its 5 older hits for its own rebuild.
- **Fact-check** (separate agent): about 150 numbers recomputed, plus the 297 values in the rank arrays; 24 external claims checked. Its 12 findings are fixed or logged (§5 "Not in this batch").
- **anti-slop:** 16 fixes. Top types:
  - overclaims ("estimates fat directly", "collects the official guidance", "lowest death rates"): 7;
  - vague lines: 4;
  - awkward constructions ("lightest overweight weight"): 4;
  - fragment: 1.

### Not in this batch (logged for §5)
- The homepage `<title>` (backlog P3) is unchanged.
- "Lowest mortality across BMI 23–33" (Winter 2014) is still on 11 pages: `/age-bmi-calculator/`, `/women-bmi-calculator/`, `/ideal-weight/`, `/calculators/`, `/blog/healthy-bmi-range/`, `/blog/bmi-chart-explained/`, `/blog/bmi-by-age/`, `/blog/bmi-limitations/`, `/blog/bmi-and-health-risks/`, `/blog/bmi-chart-women/`, `/blog/bmi-categories/`. Reword in each rebuild.
- Gallagher 2000 provisional body fat ranges on the women, men, age and body-fat-chart pages need checking against the paper's own table. PMC was blocked during the check, and one secondary source (IJMS) differs for men 20–39 and women 60–79.
- `/blog/bmi-formula/` keeps 4 probe hits and its other unsourced lines, for its G2 rewrite.
- At 320 px the homepage's percentile and category tables scroll 15–16 px inside their frames. The P3 page-width issue is fixed for `/`; `/new-bmi-calculator/` still has it.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's DEVLOG step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-012-home/`.
0.3 `git log --oneline -4 | grep -c "CMB-011"` → 1 or more. If 0, STOP: CMB-011 must run first.

### 1. Dry run
`python3 research/cmb-012-home/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 8 new files, 9 replaced files, 5 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-012-home/apply_build.py`
Must print exactly: `applied: 8 new files, 9 replaced files, 5 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass` (a `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure).
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `for f in index.html men-bmi-calculator/index.html blog/bmi-formula/index.html; do python3 scripts/check_markup.py $f >/dev/null || echo "MARKUP FAIL $f"; done` → no output.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 Each prints the number shown:
- `grep -o 'potentialAction' index.html | wc -l` → `0`
- `grep -o 'class="faq-question"' index.html | wc -l` → `8`
- `grep -o 'for="standard-' index.html | wc -l` → `5`
- `grep -o 'id="standard-rank"' index.html | wc -l` → `1`
- `grep -o 'Math.round(kg \* 2.20462)' assets/js/calculator.js | wc -l` → `0`
- `grep -o 'higher than 31%' men-bmi-calculator/index.html | wc -l` → `1`
- `grep -o 'lowest death rates' index.html men-bmi-calculator/index.html | wc -l` → `0`
- `grep -o 'A healthy PI' blog/bmi-formula/index.html | wc -l` → `0`
- `grep -o "<lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `3` or more (the three pages above; others may already carry today's date)
3.9 If `python3 -c "import pandas"` succeeds: `python3 research/home-build/home_stats.py research/average-weight/raw /tmp/cmb012-stats.json >/dev/null && cmp /tmp/cmb012-stats.json research/home-build/home_stats.json && echo same; rm -f /tmp/cmb012-stats.json` → `same`. Without pandas, record `skipped (no pandas)`.
3.10 Browser, jsdom and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: homepage rebuilt to the D-14 pattern with rank among US adults (NHANES 2021-2023), one-decimal unit conversions, strict rank rule on the men page, fact-check fixes (CMB-012)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb012-dates.txt; echo $?; grep -c '^ok' /tmp/cmb012-dates.txt; grep '^BAD' /tmp/cmb012-dates.txt; rm /tmp/cmb012-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the 3 changed pages report BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 7. REPORT
```
REPORT CMB-012 HOME
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-011 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <output or none> | 3.7 <exit> | 3.8 <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.9 <same or skipped> | 3.10 skipped (no browser/jsdom in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
