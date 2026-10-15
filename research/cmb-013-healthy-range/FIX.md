# CMB-013 HEALTHY-RANGE — `/blog/healthy-bmi-range/` rebuilt to the D-14 pattern, with how many US adults are in the range and the mortality data behind it

Built and tested in chat on 2026-10-15 against GitHub `main` `192fb02` (after CMB-012). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the drafts twice; its findings are fixed below (§5).

## Why
- **Demand.** The guide owns 29 keywords worth 58,340/mo (`research/keyword-ledger.csv`):
  - "normal of bmi" group 22,200;
  - "healthy body bmi" 18,100;
  - "healthy bmi range" 8,100 (primary);
  - "bmi average range" 2,900 and "good bmi" 2,900;
  - "ideal body mass" 2,400.
  It is D-14 rollout #2.
- **The old page broke site rules:**
  - Its OG image (`healthy-bmi-envelope.png`) drew "WHO 18.5–24.9 (ages 20–64)" and "Winter 2014 23–33 (65+)" as bands. That is an age-specific healthy range (D-11).
  - Backlog P1 lines: the "gray zone" BMI 25–27, "lowest all-cause mortality 20–25" with no source, and "0.5 BMI points per month".
  - It said "WHO … overweight from 23, obese from 25" for Asian populations. That was the 2000 WHO Western Pacific / IASO / IOTF proposal.
  - Winter 2014 was written as "lowest across BMI 23–33" (backlog P2).
  - Unsourced claims and targets:
    - a relative-risk bar chart;
    - "lowest mortality at 22–23";
    - "5–6 smaller meals";
    - "2–5 lbs day to day";
    - "people who weigh themselves regularly are more successful";
    - depression and anxiety rates.
  - "Our calculator includes a Lean Body Mass tab" linked to `/`, which has no such tab.
  - The related cards were inline-styled, and `article:modified_time` was stale (2026-08-12).
  - Detector: 15 findings at 390×844 and 31 at 1280×800.
- **SERP (owner's US/English pastes, 2026-10-15; Google marked them personalised to Maribor, so features can differ in the US):**
  - "healthy bmi range", "normal bmi", "healthy bmi": the top results are CDC, NHLBI, Cleveland Clinic, heart.org, American Cancer Society, Cigna, CVS, Harvard, Calculator.net, Northwestern, Better Health Channel and one PMC review (Nuttall 2015, arguing the lowest-mortality BMI sits higher). All give the same 18.5–24.9 table; none shows how many US adults are in the range or the mortality data behind it.
  - AI Overviews: the CDC table, the two formulas, "screening tool, not a diagnosis", muscle vs fat, older adults, and lower thresholds for Asian and African-Caribbean backgrounds (via a UK source).
  - People also ask: "What is a healthy BMI by age?" (2 of 3 pages; "What is a good BMI by age?" on the third), "What is BMI for 70 kg?" (3 of 3), "Is a BMI of 23 chubby?" (2), "What is a normal BMI for a woman?", "What is the BMI of normal?", "Is a BMI of 25 realistic?", "Is a BMI of 12 healthy?".
  - People also search for: healthy/normal BMI for women, for men, for adults; BMI chart (men, women); BMI formula; BMI calculator kg with age.

## What changes

### 1. `/blog/healthy-bmi-range/` rebuilt (D-14, guide form)
- **Order:**
  1. H1 "Healthy BMI Range: What Is a Normal BMI?" and the byline.
  2. Three intro paragraphs: the searcher's questions, the stakes (26.0% of US adults in the range; GBMC's lowest risk at 20 to 24.9), the promise.
  3. Key takeaways, opening with a 63-word answer.
  4. Disclaimer.
  5. Hero figure.
  6. Contents chips (11).
  7. Nine sections: the range, healthy weight by height, age, women and men, the mortality data, US adults, ethnicity, what BMI can't tell you, reaching the range.
  8. FAQ, then sources and method, then one related block.
- **Hero figure:** one BMI scale for every adult, with the healthy band outlined, and the healthy weight at 5′0″, 5′6″ and 6′0″ in lb and kg.
- **The range:**
  - CDC's categories ("regardless of age, sex, or race"), WHO's adult lines (25, 30) and NHLBI's matching ranges.
  - The share of US adults in each category, and the median BMI (28.2).
  - The two formulas (CDC), which the AI Overviews carry.
- **Healthy weight by height:**
  - 10 heights, 4′10″ to 6′4″, with the healthy and overweight ranges in lb and kg, each unit worked out on its own.
  - The cells use the `A–B lb (C–D kg)` form, so `check_weight_tables.py` checks every one through the 40/40 gate.
- **Age:**
  - The range is the same at every adult age.
  - Body fat at a given BMI depends on age (Gallagher 2000).
  - The risk gradient by age at measurement (GBMC).
  - Mortality data in adults 65+ (Winter 2014, worded as an association).
  - Children's percentile table (CDC).
- **Women and men:**
  - Same cut-offs for both.
  - Body fat at a healthy BMI: median 33.4% in women vs 22.1% in men (our analysis of CDC DXA scans).
  - Waist cut-offs differ by sex (NHLBI).
  - The risk gradient is steeper in men (GBMC).
- **Why 18.5–24.9: the mortality data.**
  - Source: Global BMI Mortality Collaboration (Lancet 2016): 239 studies, 10.6 million people. The main analysis covers 3,951,455 never-smokers without chronic disease.
  - Why the restriction matters: analyses with inadequate control for smoking and existing disease made overweight look protective (the authors' own finding).
  - Risk of death was lowest at BMI 20 to 24.9.
  - Compared with 22.5–24.9: 13% higher at 18.5–19.9 and 7% higher at 25–27.4, rising to 2.76 times at 40–59.9.
  - Figure plus a table with the 95% CIs, and the per-5-unit hazard ratios by continent.
- **The wedge: US adults in the range.**
  - 26.0% of US adults aged 20 and over (95% CI 22.8–29.3%): men 24.0%, women 28.1%.
  - By age: 31.0% at 20–39, 22.3% at 40–59, 24.6% at 60+.
  - Our calculation from CDC NHANES 2021–2023 (5,929 adults), shown as a figure and a table.
  - The text states only differences whose 95% CI excludes zero: women vs men, and the top share (women 20–39, 33.8%).
- **Ethnicity** (the AI Overviews' "lower thresholds" line, answered from the sources themselves):
  - US: CDC's categories don't change with race, but its National Diabetes Prevention Program takes Asian American adults from a BMI of 23 instead of 25.
  - The 2000 WHO Western Pacific / IASO / IOTF proposal (23 / 25, via Ko & Tang 2006).
  - The 2004 WHO consultation (international categories kept; action points 23, 27.5, 32.5, 37.5).
  - NICE NG246 (UK; recommendation 1.9.11, 2022): overweight 23–27.4 and obesity from 27.5 for South Asian, Chinese, other Asian, Middle Eastern, Black African or African-Caribbean backgrounds.
  - GBMC: per 5 units above 25, 39% higher risk in both East Asia and Europe; too few deaths in South Asia for an estimate.
- **What a healthy BMI can't tell you:** CDC's quotes; waist (NHLBI); body fat; muscle; the Lancet Commission 2025, including its exception above a BMI of 40.
- **Reaching the range:** official guidance only:
  - Physical Activity Guidelines for Americans;
  - NIDDK Body Weight Planner;
  - the Look AHEAD analysis (Wing 2011);
  - Health E-Stat 119 on underweight;
  - MedlinePlus on unexplained weight loss.
- **FAQ:** 8 questions: the 7 People-also-ask questions as asked, most frequent first, then "What is the healthiest BMI?" (the ideal / optimal / healthiest keywords). The JSON-LD equals the visible text.
- **Head:**
  - `<title>` "Healthy BMI Range: What Is a Normal BMI for Adults?" (51 characters), with new meta, OG and Twitter text.
  - New OG image `assets/images/og/healthy-bmi-range-risk.png`, showing the GBMC hazard ratios by band. The old envelope image is deleted.
  - Article JSON-LD gets a new headline, description and image. BreadcrumbList is unchanged.
- **Build record:** `research/healthy-range-build/`:
  - `SPEC.md`;
  - `healthy_stats.py` → `healthy_stats.json`, which stops unless it reproduces NCHS's crude rates and computes the 95% CIs;
  - `gen_hbr.py`, `og_hbr.py` and `hbr_test_playwright.py`.

### 2. Reading layout: takeaways measure (`styles.css`, `DESIGN.md`)
- `main.reading .key-takeaways .answer, main.reading .key-takeaways ul { max-width: 34rem; }` keeps the answer to about 75 characters a line on wide screens. At 1280 px the detector flagged ~90 characters a line.
- It affects only `main.reading` pages: `/`, `/men-bmi-calculator/` and this guide. All three stay at 0 findings.
- `DESIGN.md` gains the reading-layout line and the guide-page order the rollout repeats.

### 3. Registry and page map
- `research/data-sources.csv`: 8 verified rows, checked 2026-10-15 (26 → 34 rows):
  - `gbmc-2016-bmi-mortality`;
  - `who-obesity-fact-sheet`;
  - `odphp-physical-activity-guidelines`;
  - `ko-tang-2006-wpro-2000`;
  - `medlineplus-unintentional-weight-loss`;
  - `nice-ng246-ethnicity-thresholds`;
  - `cdc-ndpp-eligibility`;
  - `nhlbi-calculate-your-bmi`.
- 17 existing rows now list `blog/healthy-bmi-range` (25 in all). Notes are added on `nhanes-2021-2023-exam-files`, `nhanes-2011-2018-dxa`, `nhlbi-1998-obesity-guidelines` and `cdc-adult-bmi-categories`.
- `research/page-map.csv`:
  - the row is built, with `data_source` `nhanes-2021-2023-exam-files`;
  - the data-sourcing check passes for this page;
  - 33 other rows still fail on free-text `data_source` (34 before).

### 4. `{TODAY}` in whole files (`apply_build.py`)
- A new or replaced file whose manifest entry says `"today": true` gets `{TODAY}` replaced with the apply date when it is written.
- The hash is of the package copy, which keeps `{TODAY}`.
- The page uses this for schema `dateModified` and `article:modified_time`. The sitemap `lastmod` is a `{TODAY}` edit, as in CMB-012.
- `date_truth.py` passes on any day, as long as apply and commit happen the same day.

### 5. Fixes from the independent fact-checks (two rounds by a separate agent, on the drafts, before this package)
**Round 1 (first draft):**
- The waist cut-offs no longer claim a reason for the sex difference.
- Age and sex comparisons are stated only where the 95% CI excludes zero. "Lowest among middle-aged men" and "higher at 60+ than 40–59" are gone; the margin of error (±3 to ±6 points) is stated.
- The intro's edge example is now the band next to the edge (7% at 25–27.4). "Every height" is now "heights".
- "The low end in older adults" is now "Mortality data in adults 65 and over", and the Winter wording names its reference band (23–23.9) and "about 33".
- The FAQ says "in CDC's healthy weight range" instead of an unqualified "Yes" for BMI 24 and 18.5.
- "Ask a doctor" is replaced by MedlinePlus's sourced advice on unexplained weight loss.
- Body-fat averages are replaced by medians at the same BMI.
- "Crude" is added to the NCHS matches.
- Other wording fixes:
  - the South Asia caveat;
  - "for BMI measured at ages …";
  - the Lancet Commission's BMI > 40 exception;
  - Look AHEAD described as an analysis of a trial;
  - the women's and men's chart height ranges;
  - the OG legend.

**Round 2 (after the SERP changes: FAQ, ethnicity, formulas):**
- "Is a BMI of 12 healthy?": WHO 1995 calls BMI under 16 "grade 3 thinness", and MedlinePlus is quoted as written ("more weight than is considered healthy for their age and height").
- "Is a BMI of 25 realistic?": the GBMC comparison is removed; the answer keeps the US shares and Look AHEAD.
- Ethnicity: CDC's National Diabetes Prevention Program (23 for Asian American adults) added as the US source.
- GBMC's crude-analysis finding is worded as the paper puts it: a 2013 review's result reproduced only "with inadequate control" for the biases.
- "In never-smokers" is added to every per-5-unit statement; GBMC's lowest-risk range is "20 to 24.9" everywhere.
- The median BMI carries "(our calculation …)"; the method note points to the NCHS figures under the US adults table.
- The 70 kg answer adds "or from 5′6″ to 6′4″ in whole inches"; the women's answer says the waist cut-offs apply "mainly at a BMI of 25 to 34.9".
- The waist claims link to the NHLBI treatment-guidelines chapter (NBK2004), which says them; "independent predictor of risk" is its wording.
- MedlinePlus's weight-loss threshold is "more than 10 lb (4.5 kg) or 5%"; the intro's promise follows the page order; the OG description says "(CDC data, our calculation)".

### Chat results (fresh GitHub clone of `192fb02` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-17` and commit dates set to that day. Both runs: dry-run and apply `8 / 5 / 1 / 1`; gates 3.1–3.8 pass; 3.9 `0 1 1 1 8 0 0 0 1 0 33`; 3.10 `same`; date check exit 0, 40/40.
- **Browser checks (Chromium, on the applied clone served locally):**
  - `hbr_test_playwright.py`: 214 checks, 0 failures. It covers the height table by brute force; the age, category and hazard-ratio tables; the figure labels; 11 chips and 8 FAQ; JSON-LD against the visible text; SVG label collisions at 390 and 1280; widths at 320, 360, 390 and 1280.
  - Calculator jsdom 95/95; calculator end-to-end 1,316 checks, 0 failures.
  - FAQ opens on all 25 pages that have one; no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Detector (impeccable 0.1.14):** this guide 15 → 0 at 390×844 and 31 → 0 at 1280×800; `/` and `/men-bmi-calculator/` stay at 0 at both. Sitewide static 328 → 313 at 390×844, no page worse (`research/impeccable-baseline/2026-10-15-cmb013-390x844.json`).
- **Live R4 (owner, 2026-10-15):** the detector on production `/` and `/men-bmi-calculator/` printed only the consent-banner note, so 0 findings. This closes the CMB-007 men-page R4 item.
- **Anti-slop:** 23 fixes in two passes (re-explaining and repetition 10, staging 7, vague or overclaimed 5, rhythm 1).

### Not in this batch (logged for §5)
- `/age-bmi-calculator/`:
  - its "WHO adult BMI range at a glance" box lists "65+ (Winter 2014) 23–33 (observed plateau)" next to 18.5–24.9, which reads as an age-specific range;
  - its OG image (`age-bmi-ucurve.png`) draws a schematic mortality curve with no data.
  Fix both in its D-14 rebuild.
- `/` has the same unsourced "ask a doctor" line and lacks the Lancet Commission's BMI > 40 exception. `/` and `/men-bmi-calculator/` word Winter 2014 as "rose … above 33". `/` labels BMI 16–16.9 and under 16 "moderate" and "severe thinness" and cites WHO 1995, whose report says grade 2 and grade 3 thinness. Align these the next time those pages change.
- WHO Europe's "A healthy lifestyle" page, which carried the "Normal weight / Pre-obesity" table, is now "Everyday actions for better health" with no BMI table (checked 2026-10-15). No live page cites it.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-013-healthy-range/`.
0.3 `git log --oneline -4 | grep -c "CMB-012"` → 1 or more. If 0, STOP: CMB-012 must run first.

### 1. Dry run
`python3 research/cmb-013-healthy-range/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 8 new files, 5 replaced files, 1 edits, 1 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-013-healthy-range/apply_build.py`
Must print exactly: `applied: 8 new files, 5 replaced files, 1 edits, 1 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py blog/healthy-bmi-range/index.html` → `blog/healthy-bmi-range/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py blog/healthy-bmi-range/index.html; echo $?` → only `0`.
3.9 Each command prints the number shown:
- `grep -o '{TODAY}' blog/healthy-bmi-range/index.html | wc -l` → `0`
- `grep -o "\"dateModified\": \"$(date +%F)\"" blog/healthy-bmi-range/index.html | wc -l` → `1`
- `grep -o "content=\"$(date +%F)T00:00:00Z\"" blog/healthy-bmi-range/index.html | wc -l` → `1`
- `grep -o "<loc>https://calculatemybmi.net/blog/healthy-bmi-range/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o 'class="faq-question"' blog/healthy-bmi-range/index.html | wc -l` → `8`
- `grep -o 'healthy-bmi-envelope' blog/healthy-bmi-range/index.html | wc -l` → `0`
- `ls assets/images/og/ | grep -c 'healthy-bmi-envelope'` → `0`
- `grep -o -i 'gray zone\|0.5 BMI points\|lowest death rates\|Lean Body Mass tab' blog/healthy-bmi-range/index.html | wc -l` → `0`
- `grep -o 'main.reading .key-takeaways .answer' assets/css/styles.css | wc -l` → `1`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "blog/healthy-bmi-range"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `33`
3.10 If `python3 -c "import pandas"` succeeds, run:
`python3 research/healthy-range-build/healthy_stats.py research/average-weight/raw /tmp/cmb013-stats.json >/dev/null && cmp /tmp/cmb013-stats.json research/healthy-range-build/healthy_stats.json && echo same; rm -f /tmp/cmb013-stats.json`
It must print `same`. Without pandas, record `skipped (no pandas)`.
3.11 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /blog/healthy-bmi-range/ rebuilt to the D-14 pattern with US adults in the healthy range by age and sex (NHANES 2021-2023) and the GBMC 2016 mortality evidence; takeaways measure in the reading layout (CMB-013)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb013-dates.txt; echo $?; grep -c '^ok' /tmp/cmb013-dates.txt; grep '^BAD' /tmp/cmb013-dates.txt; rm /tmp/cmb013-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-013 HEALTHY-RANGE
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-012 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.10 <same or skipped> | 3.11 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
