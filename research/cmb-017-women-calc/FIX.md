# CMB-017 WOMEN-CALC — `/women-bmi-calculator/` rebuilt to the D-14 pattern

Built and tested in chat on 2026-10-22 against GitHub `main` `9bf7429` (after CMB-016). Tools: Chromium (Playwright), impeccable engine 0.1.14, pandas. A separate agent fact-checked the draft; its findings are settled below (§6).

## Why
- **Demand.** `/women-bmi-calculator/` owns 33 keywords worth 279,290/mo (`research/keyword-ledger.csv`), page 6 of the D-14 rollout:
  - "bmi calculator women" 201,000 (primary); "bmi calculate women" 74,000 (KWP group with "womens bmi calculator" and "female bmi calculator");
  - "calculate my bmi female" 880, "bmi chart women calculator" 720, "bmi older woman calculator" 390, "bmi check for women" 390, "bmi calculator women kg" 210, "bmi calculator female asian" 210.
- **The old page broke site rules:**
  - inputs without `for`/`id`, and the key takeaways, disclaimer and weight-difference line lost in `a83d1f7` (§5 [P1]);
  - "When to See a Doctor" lists and life-stage advice (menstrual cycle, postpartum, hormones, menopause) with no source (D-01, D-10, §4 see-a-doctor rule);
  - Winter 2014 paraphrased as "lowest mortality across BMI 23–33" (§5 [P2]); ACOG pregnancy ranges with an OG image of text;
  - gradient purple cards and inline styles; detector 16 findings at 390×844 (nested cards 10, AI palette 5, gray on color 1) and 28 at 1280×800.
- **SERP (owner's pastes of google.com, US/English, 2026-10-22, not personalized):**
  - "bmi calculator women" and "bmi calculator female": CDC, NHLBI, Calculator.net, ACS, AARP, Harvard Health, Hers, Mayo Clinic's BMI-and-waist tool, Omni. People also ask: "What is the correct BMI for a female?", "Is 140 pounds fat for a 5'4" female?", "What is the correct BMI for my age as a female?", "What is an acceptable BMI for a 70 year old female?", "What is BMI for 5'2" female?", "How much should a 5'5" female weigh?".
  - "bmi calculator for older women": the AI Overview quotes a "65+" range of 23 to 29.9 from a fitness shop's calculator. People also ask: "What is a good BMI for an older woman?", "Is there a BMI calculator for seniors?", "What is the new BMI chart for 2026?".
  - Gap: every result is a bare calculator. None places a woman among US women of her age, none applies the June 2026 waist rule to her own waist, none says what body fat goes with her BMI. That is the wedge.

## What changes

### 1. `/women-bmi-calculator/` rebuilt (D-14, calculator form)
- **Order:** H1 "BMI Calculator for Women" and the byline → two intro lines → the calculator → key takeaways (answer first) → disclaimer → 10 contents chips → your result (worked example) → US women compared → by age (with "Women 60 and over") → weight by height → waist and the 2026 ADA standards → body fat at the same BMI → Asian and other backgrounds → pregnancy → 10 FAQ → sources and method → one related block.
- **The calculator:** the shared parts and `calculator.js`, inputs with `for`/`id`, plus an optional waist field (inches or cm). On phones the height pair and the weight-and-waist pair sit side by side (`.form-row--pair`), so Calculate ends at 761 px on 390×844. Scale labels use CDC names.
- **Results (the wedge):** after the shared answer-first panel, three flat sections from the page script:
  - **Compared with US women aged 20 and over:** the rank by the US rank rule, plus women aged 20–39, 40–59 and 60+ (CDC NHANES 2021–2023, 3,249 women; the all-women curve is the homepage's, asserted equal);
  - **US women with a BMI like yours:** body fat on CDC's DXA scans at that whole BMI (women 20–59, NHANES 2011–2018) and the share with a large waist in that BMI category;
  - **Waist check** (only with a waist): the ratio on NICE's scale, the US guidelines' 35-inch line, and the 2026 ADA thresholds, with the answer for women of Asian background when it differs.
- **Sections:** the worked example explains every output at the starting values (5′4″, 140 lb, waist 33 in); BMI percentiles of US women by age group (table); BMI by decade 20–29 to 80+ (figure and table; average 28.0 in the 20s, 31.4 in the 50s, 29.5 at 70–79 and 27.7 at 80+, each difference outside its margin of error, different women measured in the same years); older women (CDC's "regardless of age", the senior calculators' 23–29.9 named as not CDC's, Winter 2014 worded to its abstract, ADA's muscle note); healthy weight at every height 4′10″–6′0″ with the half-height waist line; the three waist rules and US women's waist shares; body fat at the same BMI; the lower lines by background (CDC National DPP, WHO 2004, NICE NG246, ADA 2026); CDC's pregnancy table.
- **FAQ:** 10 questions: 8 of the 9 People-also-ask questions as asked (the ninth, "What is a good BMI for an older woman?", is answered by the 70-year-old and seniors questions), then the ledger's "bmi for women formula" and the old page's pregnancy question. JSON-LD equals the visible text. The guide `/blog/bmi-chart-women/` keeps "What is a healthy BMI for a female?" (§5 [P3] settled).
- **Head:** `<title>` "BMI Calculator for Women: Waist Check and US Women Compared" (59 characters); new meta, OG and Twitter text; the preferred image (§2); one JSON-LD graph: WebPage (`primaryImageOfPage`), WebApplication (image list, feature list, author named), BreadcrumbList, FAQPage.
- **Build record:** `research/women-calc-build/`: `SPEC.md`; `wbc_stats.py` → `wbc_stats.json` (stops unless the all-women curve equals `home_stats.json`, the decade means equal `research/average-weight/avgw_results.json` and the age-group shares equal `bcw_stats.json`; stores 4 decimals, round once); `gen_wbc.py`; `wbc_test_playwright.py`.

### 2. Images in Google results (the CMB-015 standard)
- Text-free preferred images `assets/images/preferred/women-bmi-calculator-{16x9,4x3,1x1}.png` (the decade rows over the healthy band), drawn by `research/preferred-images/pref_images.py` (new `women_calc` drawing; only this page's files are redrawn). Named in `og:image`, `twitter:image`, the WebApplication image list and `primaryImageOfPage`.
- `scripts/check_images.py`: the page joins `PREFERRED`. The page has no `<img>`, so no image-sitemap entry (as on `/`).
- `assets/images/og/women-acog-pregnancy-ranges.png` (a card with text) is referenced nowhere after this and is deleted.

### 3. Registry, page map, DESIGN.md
- `research/data-sources.csv`: no new rows; 13 rows list the page; notes added on `nhanes-2021-2023-exam-files` (the women's curves), `cdc-pregnancy-weight-gain` and `cdc-adult-bmi-categories` (both re-read 2026-10-22).
- `research/page-map.csv`: the row's wedge and notes; `data_source` set to the registry domain `nhanes-2021-2023-exam-files`, so `check_sources.py` passes for this page (FAIL lines 31 → 30).
- `DESIGN.md`: "Waist field and result boxes (CMB-017)".

### 4. `styles.css`
- `.form-row.form-row--pair` keeps two columns below 600 px. Used only on this page.

### 5. Dates and removals
- The page has no schema `dateModified` (as on `/`), so it ships as a plain replacement; the sitemap `lastmod` is a `{TODAY}` edit. No other page's text, links or JSON-LD change.

### 6. Fixes from chat's checks and the independent fact-check
**Chat's own checks, fixed on the draft:**
- Calculate ended at 930 px on a 390×844 phone (below the fold): the height pair and the weight-and-waist pair now sit side by side below 600 px (`.form-row--pair`) and the intro is two short lines, so it ends at 761 px (784 at 360, 852 at 320);
- the percentile and decade tables were wider than their 310 px frame at 390 (324 and 345 px): shorter headers ("All" for women 20+), the decade table cut to four columns (age, median, middle half, healthy), the sample sizes moved into the notes;
- the preferred image sat left of center: it now spans BMI 16.5–44.5, and the figure's axis runs 15–45;
- anti-slop: 5 fixes (staging 2, vague wording 3).

**Independent fact-check (separate agent, on the draft).** It rebuilt the 2021–2023 sample from CDC's raw files with its own code and ran the page's own script in Node over BMI 10.0–90.0 and 181,328 waist inputs. Every number matched: the 396 curve points, the percentile and decade tables, the figure, the averages and stated differences, the body-fat and waist shares (13 DXA cells rebuilt from the raw files), the ADA shares, the 60 healthy-weight bounds, the worked example and the FAQ JSON-LD; the decade means and medians also equal NCHS Series 3 No. 50. Live sources re-read: CDC (adult categories, pregnancy, National DPP, formula, child categories), NICE NG246, the WHO 2004 and Winter 2014 abstracts, Series 3 No. 50 and both senior calculators. All settled before packaging (detail in `SPEC.md`):
- **FAIL, the ratio was rounded before the ADA test (fixed):** a 31.7-inch waist at 5′4″ (0.4953) printed 0.50 and was called "at least half the height", so obesity under the ADA rule (1,320 of 181,328 grid outputs). The check now works the ratio out from the printed waist and cuts it to two decimals (0.4953 shows as 0.49), so 0.50 always means at least half the height; the worked example shows 0.51 (33 ÷ 64 = 0.516).
- **FAIL, the imperial waist check contradicted itself (fixed):** at 5′11″ with 34.8 in (88.4 cm) one box said "not over 35 in (88 cm)" and then "88 cm or more, and yours is". The US-guidelines line names only the unit compared; the ADA sentences quote the waist in cm against 88 cm; "about 35 in" is gone (88 cm = 34.6 in).
- **FAIL, one cell (fixed):** 5′5″ half height read 82.5 cm (82.55 printed down by float formatting); cm figures are now exact decimals rounded half up (82.6). The calculator's waist conversion had the same slip (32.5 in shown as 82.5 cm) and now rounds half up.
- **WARN (fixed):** the height column is "Half the height (ratio 0.5)", with a note on where the ADA rule matters (BMI 25–29.9) and which line decides (88 cm from 5′10″, 80 cm from 5′3″ for women of Asian background); the senior calculators "class 23 to 29.9 (or 23 to 30) as normal" and cite Winter et al. 2014 (chat re-read both); the by-age text says the average "differs by age group" in "different women measured in the same years"; "whatever the waist" → "on BMI alone", the waist box says it applies published thresholds "for adults who aren't pregnant; not a diagnosis", and "for women of non-Asian background" leads the first ADA sentence when the Asian-background answer differs; the method names the rank as the one figure not rounded once (2-decimal curves, the homepage's: 8 of 3,204 results one point off in chat's count; logged).
- **NOTEs taken:** "about" before the worked example's ranks; the FAQ lists the age-group medians without "vary with age"; the 80+ vs 70–79 fall is now computed and asserted (−1.9, CI −3.1 to −0.6); Series 3 No. 50 joins the sources; no "CDC and WHO publish no adult cut-offs"; WHO's "potential" action points; the takeaway says 69.4% "meet" the ADA thresholds against 41.8% "of the same women"; og:description no longer says "rank among 3,249 US women"; "aged 20 to 59" on the body-fat takeaway, FAQ and feature list.
- **NOTEs kept:** "risk higher below 23" (the Winter abstract's conclusion: "the risk of mortality increased in older people with a BMI <23.0"); body fat figures stay the body fat chart's (`bfpc_stats.json`, its quantile rule; the order-free move is CMB-016's [P3]); the 5′11″ row follows the site's table rule (CMB-008); BreadcrumbList without a visible trail is sitewide (logged).
- **Not reachable:** ADA's own section PDF and doi page; the thresholds stay as the registry recorded them (2026-10-15).

### Chat results (fresh GitHub clone of `9bf7429` + this package)
- **Steps 0–5 as written, run twice:** applied and committed today, and again with `CMB_TODAY=2026-10-24` and commit dates set to that day. Both runs: dry-run and apply `9 / 7 / 1 / 1`; gates 3.1–3.9 pass; 3.10 `0 1 10 0 0 0 18 1 1 7 1 0 0 30`; 3.11 `same`; date check exit 0, 40/40. The applied clone is identical to chat's work tree.
- **3.11 in chat:** `wbc_stats.py` on CDC's raw DEMO_L and BMX_L files rebuilds `wbc_stats.json` byte for byte; it stops unless the all-women curve equals `home_stats.json`, the decade means equal `avgw_results.json` and the age-group shares equal `bcw_stats.json`.
- **Browser checks (Chromium):**
  - `wbc_test_playwright.py` on the applied clone: 230 checks, 0 failures. It covers the starting values typed in (BMI 24.0, "Higher than 24% of US women", 32% / 19% / 21% by age, 36.1% body fat, ratio 0.51 with the Asian sentence); 14 rank cases in both units and both tails; the "like you" lines; 16 waist cases (every NICE class, the BMI-35 limit, the US line in both units, every ADA outcome, the Asian sentence only when it differs) with the fact-check's cases typed in (31.7 in at 5′4″ and 80.5 cm at 162 cm show 0.49 and are not "at least half"; 34.8 in at 5′11″ is not over 35 in and, at 88.4 cm, meets 88 cm; exactly half shows 0.50; 5′5″ half height 82.6 cm); out-of-range waists; the 4 tables against the stats and the weight-table gate's rule; figure descriptions and hover labels; head, OG, Twitter, JSON-LD and the preferred images at size; 10 chips; 10 FAQ with JSON-LD equal to the visible text; Calculate above the fold at 360 and 390 (761 px at 390); no page wider than 320, 360, 390 or 1280; tables inside their frames; no SVG label collisions; no JavaScript error.
  - The page's own script over the fact-check's grid of 181,328 waist inputs: 0 sentences that disagree with the unrounded ratio or the printed waist (the draft had 1,320 false "at least half").
  - On chat's work tree (identical to the clone): calculator jsdom 95/95; calculator end-to-end 1,316 checks, 0 failures; FAQ opens on all 26 pages that have one; no page wider than the screen (120 checks at 360, 390 and 1280); the mobile menu opens and closes on 40/40.
- **Detector (impeccable 0.1.14):** this page 16 → 0 at 390×844 and 28 → 0 at 1280×800; with results open 16 → 0, also with a 33-inch waist entered. Sitewide static 299 → 283 at 390×844, only this page changed (`research/impeccable-baseline/2026-10-22-cmb017-390x844.json`); with results open the 8 calculators 104 → 88.
- **Live R4 (owner):** the detector on production `/body-fat-percentage-chart/` printed only the consent-banner note, so 0 findings. That closes CMB-016's open item.

### Not in this batch (logged for §5)
- `/age-bmi-calculator/` still carries the Winter 2014 misparaphrase and the "65+ (Winter 2014) 23–33" box (§5 [P2]); its D-14 rebuild fixes both.
- Order-free weighted percentiles (§5 [P3]) are unaffected: this page's percentiles already use the order-free method of `home_stats.py`.
- The rank curves are stored at 2 decimals on `/`, `/men-bmi-calculator/` and this page (8 of 3,204 women's results one point off). Moving all three to 4-decimal curves together keeps the pages equal ([P3]).
- Every page carries BreadcrumbList JSON-LD with no visible breadcrumb trail. Google's structured-data guidelines ask markup to match what readers see; add a visible trail sitewide or keep it as it is ([P3], owner's call).

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand; DEVLOG.md in the prompt's DEVLOG step is the only exception.
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block. Do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-017-women-calc/`.
0.3 `git log --oneline -4 | grep -c "CMB-016"` → 1 or more. If 0, STOP: CMB-016 must run first.

### 1. Dry run
`python3 research/cmb-017-women-calc/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 9 new files, 7 replaced files, 1 edits, 1 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-017-women-calc/apply_build.py`
Must print exactly: `applied: 9 new files, 7 replaced files, 1 edits, 1 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → exactly one line: `check_structure: 40/40 pages pass`. A `FAIL assets/js/calculator.js` or `FAIL /blog/ hub` line is a failure.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `python3 scripts/check_markup.py women-bmi-calculator/index.html` → `women-bmi-calculator/index.html: 0 issues`.
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo $?` → only `0`.
3.8 `python3 scripts/check_weight_tables.py women-bmi-calculator/index.html; echo $?` → only `0`.
3.9 `python3 scripts/check_images.py . | tail -1` → `check_images: 0 page(s) with problems`.
3.10 Each command prints the number shown (PG = `women-bmi-calculator/index.html`):
- `grep -o '{TODAY}' $PG | wc -l` → `0`
- `grep -o "women-bmi-calculator/</loc><lastmod>$(date +%F)</lastmod>" sitemap.xml | wc -l` → `1`
- `grep -o 'class="faq-question"' $PG | wc -l` → `10`
- `grep -o '<style' $PG | wc -l` → `0`
- `grep -o 'women-acog-pregnancy-ranges' $PG | wc -l` → `0`
- `ls assets/images/og/ | grep -c women-acog` → `0`
- `ls assets/images/preferred/ | wc -l` → `18`
- `grep -o "'/women-bmi-calculator/': 'women-bmi-calculator'" scripts/check_images.py | wc -l` → `1`
- `grep -o 'form-row--pair' assets/css/styles.css | wc -l` → `1`
- `grep -o 'for="women-' $PG | wc -l` → `7`
- `grep -o 'id="women-waist-in"' $PG | wc -l` → `1`
- `grep -o 'lowest mortality\|lowest all-cause mortality' $PG | wc -l` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c "page 'women-bmi-calculator'"` → `0`
- `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | grep -c '^FAIL'` → `30`
3.11 Reproducing `wbc_stats.json` needs pandas (the raw files are in `research/average-weight/raw/`). If `python3 -c "import pandas"` fails, record `skipped (no pandas)`; chat ran it (see Chat results). Otherwise run `python3 research/women-calc-build/wbc_stats.py research/average-weight/raw research/home-build/home_stats.json research/average-weight/avgw_results.json research/chart-women-build/bcw_stats.json /tmp/wbc_check.json && cmp /tmp/wbc_check.json research/women-calc-build/wbc_stats.json && echo same; rm -f /tmp/wbc_check.json` → `same`.
3.12 Browser and detector checks: the box has none (DEVLOG §4), so record them as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "feat: /women-bmi-calculator/ rebuilt to the D-14 pattern: rank among US women by age (NHANES 2021-2023), optional waist check against the NHLBI, NICE and 2026 ADA thresholds, body fat measured at your BMI (CDC DXA); preferred images (CMB-017)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb017-dates.txt; echo $?; grep -c '^ok' /tmp/cmb017-dates.txt; grep '^BAD' /tmp/cmb017-dates.txt; rm /tmp/cmb017-dates.txt` → `0` and `40`.
- Apply (step 2) and commit (step 4) must happen on the same day. If they don't, the page reports BAD; record the output and don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt. Commit DEVLOG.md too; don't push.

### 7. REPORT
```
REPORT CMB-017 WOMEN-CALC
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-016 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <output> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <line> | 3.7 <exit> | 3.8 <exit> | 3.9 <line> | 3.10 <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> <n> | 3.11 <same or skipped (no pandas)> | 3.12 skipped (no browser/detector in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
