# CMB-005 LIVE-FIX — FAQ taps and schema, BMI rounding, calculator claims and stats

Built and tested in chat on 2026-10-11 against GitHub `main` at `e6d94fd` (Chromium 1194 + jsdom 24):
- FAQ accordions did not open on 13 live pages: `/`, `/calculators/`, `/women-bmi-calculator/`, `/men-bmi-calculator/`, `/age-bmi-calculator/`, `/kids-bmi-calculator/`, `/ideal-weight/`, `/lean-body-mass/`, `/new-bmi-calculator/`, `/blog/bmi-and-health-risks/`, `/blog/bmi-limitations/`, `/blog/waist-to-height-ratio/`, `/blog/how-to-lower-bmi/`. Each had two click bindings (calculator.js `setupFAQ()` plus the page's own toggle, or two inline toggles / an `onclick`), so one tap opened and closed the answer. `/blog/bmi-and-metabolism/` and `/blog/underweight-bmi-risks/` had three and only worked by accident.
- The adult calculators categorised the unrounded BMI but showed it rounded: 5'10" 174 lb showed **25.0 "Normal"**, 6'2" 144 lb showed **18.5 "Underweight"**, and 178 cm / 79 kg said "0.1 kg above the healthy range" at BMI 24.9. The healthy maximum (174 lb at 5'10") disagreed with the page tables (173 lb), and the milestones table listed 174 lb as both "Normal upper end" and "Overweight threshold".
- `/age-bmi-calculator/` at age 65+: the "Adult BMI range" tile showed the literal text `&middot;`, and the extended result called the Winter 2014 observational band "Your range".
- `/calculators/`: the stats block said **8** free calculators (the page and the menu list nine), and on phones it was wider than the screen (366 px on a 360 px phone) and broke "18.5-24.9" over three lines at 390 px.
- FAQ schema: on 8 pages the FAQPage JSON-LD still carried answers the page no longer shows (30 answers, older text kept after the visible answers were rewritten). Example: `/ideal-weight/` schema said the Robinson formula "tended to give results closest to the middle of the healthy range"; the page says no formula has been shown to be more accurate.
- Claims (D-11): meta, og/twitter and WebApplication descriptions on the men and women calculators promised "men-specific / women-specific healthy weight ranges"; the age calculator's WebApplication description said "Age-adjusted BMI calculator with personalized healthy weight ranges for different life stages"; `/terms/`, `/blog/bmi-chart-explained/` and `/new-bmi-calculator/` described the calculators the same way.

After the fix: 1,140 Chromium checks on the standard, women, men and age calculators (12 imperial + 9 metric cases each) pass; `research/calculator-checks/calc_test_jsdom.js` 77/77 (main fails 24: 11 calculator checks and 13 FAQ checks); a first-question tap opens the answer on all 25 FAQ pages; no page is wider than the screen at 360, 390 or 1280 px (123 page loads); FAQPage JSON-LD answers equal the visible answers on all 20 pages that have them.

## What changes
1. `assets/js/calculator.js`
   - `init()` no longer calls `setupFAQ()` (every page's inline script binds its FAQ, as K1 did for the menu).
   - `round1()`: BMI is rounded to one decimal once; categories, the classification and what-if tables, BMI Prime and New BMI all use that shown value.
   - `weightBounds()` / `getHealthyWeightRange()`: healthy limits are whole units whose rounded BMI is 18.5–24.9 (the rule the BMI charts use); metric users get whole-kg limits. The bracketed value converts the same number.
   - "Above/below the healthy range" measures to those limits (5'10", 180 lb → 7 lbs (3.2 kg) above, not 6).
   - Milestones table lists the CDC thresholds only: healthy range starts (18.5) / ends (24.9), overweight (25), obesity (30), class 2 (35), class 3 (40); the invented "Normal low end 20" and "Normal midpoint 22" rows are gone.
   - Dead sex-specific "ideal" BMI bands (19–24 women, 20–25 men; never displayed) removed.
   - BMI Prime (`bmiPrime()`): BMI ÷ 25 to two decimals, capped at 0.99 below a BMI of 25 — a BMI of 24.9 showed "1.00 · Above upper normal"; it now shows 0.99 with a label taken from the shown BMI ("Under / At or over the overweight cut-off"). New BMI's Prime rows use the same helper.
   - Waist note in the men/women results: "whatever the BMI" → "mainly at a BMI of 25 to 34.9" (NHLBI applies the waist cut-offs to BMI 25–34.9; above 35 nearly everyone exceeds them).
   - Age calculator, 65+: the tile reads "18.5 - 24.9 (WHO adult range) · lowest mortality observed across BMI 23-33 in adults 65+ (Winter 2014); observational, not a target" (a real middle dot, wording as on the page body); the extended line says "Adult BMI range", not "Your range".
2. FAQ duplicates removed (whole `<script>` elements or whole `onclick` attributes only): `blog/bmi-and-health-risks`, `blog/bmi-limitations`, `blog/waist-to-height-ratio`, `blog/bmi-and-metabolism`, `blog/underweight-bmi-risks`, `blog/how-to-lower-bmi`.
3. Claims (D-11): men + women meta description, og:description, twitter:description and WebApplication `description`; the age calculator's WebApplication `description` (now the page's meta description); three service lines on `/terms/`; two related-guide blurbs on `/blog/bmi-chart-explained/`; the women blurb in `/new-bmi-calculator/`'s related guides. The chart guide's contents link now matches its heading ("Age and BMI charts", was "Standard vs Age-Adjusted BMI Charts").
4. Teaser tables: 6'2" men 65–88 kg → **66–88 kg**; 5'2" women 46–62 kg → **46–61 kg** (65 kg at 6'2" is BMI 18.4; 62 kg at 5'2" is BMI 25.0). The kg limits are for the exact inch height, so the cm labels now carry one decimal (168 cm → 167.6 cm: at a full 168 cm, 52 kg is BMI 18.4).
5. `/calculators/` stats: **9** free calculators; age range **2-100** (pediatric 2–19, age calculator up to 100). Below 480 px each stat is one row (number box, label beside it; the label drops under the number on a 320 px screen). Desktop and tablet layouts unchanged.
6. `scripts/check_structure.py`: the 40/40 gate now fails any page whose FAQ accordion or mobile-menu toggle has a click-binding count other than 1, and any page whose FAQPage JSON-LD answer is not the visible answer to the same question (schema must match visible content). On `e6d94fd` this gate reports 23/40.
6a. FAQPage JSON-LD answers replaced by the visible answers on `/ideal-weight/`, `/blog/bmi-history/`, `/blog/bmi-chart-explained/`, `/blog/bmi-and-health-risks/`, `/blog/underweight-bmi-risks/`, `/blog/bmi-limitations/`, `/blog/waist-to-height-ratio/`, `/blog/how-to-lower-bmi/` (30 answers). Nothing visible changes; only the answer strings inside the JSON-LD.
7. `research/calculator-checks/calc_test_jsdom.js`: expectations for the new limits + rounding cases + the age 65+ result + FAQ open/close on 15 pages. New reference tests (need Playwright + Chromium, not in the box): `calc_e2e_playwright.py`, `faq_probe_playwright.py`.
8. `sitemap.xml` lastmod 2026-10-11 for `/men-bmi-calculator/`, `/women-bmi-calculator/`, `/age-bmi-calculator/`, `/new-bmi-calculator/`, `/calculators/`, `/terms/`, `/blog/bmi-chart-explained/`, and the 7 other pages in 6a (structured data changed). Their `dateModified` stays: it moves only when visible content changes.
9. Dates that follow: `/terms/` shows "Last Updated: October 11, 2026" (the Terms say changes are posted "with the 'Last Updated' date revised accordingly"); `dateModified` 2026-10-11 on `/terms/`, `/blog/bmi-chart-explained/` and `/calculators/`, so schema and sitemap agree.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's last step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
`git status --porcelain` must print exactly one line: `?? research/cmb-005-live-fix/`. Anything else → STOP.

### 1. Dry run
`python3 research/cmb-005-live-fix/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 2 new files, 19 replaced files, 0 edits, 0 deletions`. An `ABORT` line → STOP (a file changed since the package was built; report the list).

### 2. Apply
`python3 research/cmb-005-live-fix/apply_build.py`
Must print exactly: `applied: 2 new files, 19 replaced files, 0 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → first line `check_structure: 40/40 pages pass` (includes the new FAQ binding and FAQ schema checks).
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `grep -o "setupFAQ();" assets/js/calculator.js | wc -l` → `0`.
3.7 `grep -o "men-specific\|women-specific\|Male-specific\|Female-specific\|age-adjusted BMI interpretations\|Age-adjusted BMI calculator\|healthy BMI ranges by age" men-bmi-calculator/index.html women-bmi-calculator/index.html terms/index.html blog/bmi-chart-explained/index.html age-bmi-calculator/index.html new-bmi-calculator/index.html | wc -l` → `0`.
3.8 `grep -o 'onclick="this.parentElement' blog/*/index.html | wc -l` → `0`.
3.9 `for f in men-bmi-calculator women-bmi-calculator age-bmi-calculator new-bmi-calculator calculators terms blog/bmi-chart-explained; do python3 scripts/check_markup.py $f/index.html >/dev/null || echo "MARKUP FAIL $f"; done` → no output.
3.10 `grep -o "Last Updated: October 11, 2026" terms/index.html | wc -l` → `1`; `grep -o '"dateModified": "2026-10-11"' terms/index.html blog/bmi-chart-explained/index.html calculators/index.html | wc -l` → `3`.
3.11 `grep -o "&middot; 23 - 33" assets/js/calculator.js | wc -l` → `0`; `grep -o '>9</div> <div class="stat-label">Free Calculators' calculators/index.html | wc -l` → `1`; `grep -o "max-width: 480px) { .info-card-grid" calculators/index.html | wc -l` → `1`.
3.12 jsdom test: the box has no jsdom (DEVLOG §4) → record as skipped, not run. Chat ran it: 77 passed, 0 failed.

### 4. Commit
```
git add -A
git commit -m "fix: one FAQ binding per page, FAQ schema matches the page, BMI rounding and healthy limits consistent, calculator claims, stats and small-screen layout corrected (CMB-005)"
```

### 5. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 6. REPORT
```
REPORT CMB-005 LIVE-FIX
status: OK | STOPPED at step N (reason)
step 0: <git status --porcelain output>
dry-run: <line>
apply: <line>
gates: 3.1 <line> | 3.2 <line> | 3.3 <exit code> | 3.4 <last line> | 3.5 <line> | 3.6 <n> | 3.7 <n> | 3.8 <n> | 3.9 <output or none> | 3.10 <n> <n> | 3.11 <n> <n> <n> | 3.12 skipped (no jsdom in box)
commit: <git log --oneline -2>
stat: <git show --stat --oneline <work-commit-hash> | tail -1>
final: <git status --short, or "clean">
```
