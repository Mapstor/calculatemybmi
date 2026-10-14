# CMB-010 SITEWIDE-REPAIR — broken content repaired, D-11 and option B on the old guides, shared components polished, content-integrity gate

Built and tested in chat on 2026-10-14 against GitHub `main` `59716d5` (after CMB-009). Tools: Chromium 141, jsdom 24, impeccable engine 0.1.14, wordfreq.

## Why
- The owner found "Calculate My BMI Now" as plain text at the end of `/blog/body-fat-vs-bmi/`.
- Its link was stripped on 2026-09-26 (commit 7866479). Automated passes in Aug and Sept (phase 14 "citation integrity", the P2 claim passes, the P0 recovery) also removed:
  - named sources from sentence openings;
  - links from the middle of sentences;
  - the text inside boxes and steps.
- These leftovers have been live for weeks. The impeccable detector cannot see them: it looks for style anti-patterns, not for a link or a sentence that is missing.
- Only `/men-bmi-calculator/` had the full impeccable and anti-slop pass. The other 39 pages carried 734 detector findings.

## What changes

### 1. Broken content repaired (18 pages)
- **Dead CTA and broken boxes:**
  - `/blog/body-fat-vs-bmi/`: the closing call to action is a real button again.
  - `/blog/bmi-chart-explained/`: the empty Example box gets its worked example back (our own calculation: 5′6″, 160 lb → BMI 25.8, overweight).
  - `/blog/bmi-tracking-guide/`: the unfinished "see our guides on" with three cards stuffed inside the paragraph (they covered the text) is now a sentence and a plain link list.
  - `/calculators/` Trusted Resources: the WHO link had been stripped and three tiles were empty. It is now a three-link list (WHO, CDC, NHLBI); all three URLs are already cited elsewhere on the site.
- **Calculator results:** `/women-bmi-calculator/` and `/new-bmi-calculator/` showed an empty grey box under the healthy range after Calculate. The deleted `<p id="…-weight-diff">` is restored, so the "within / above / below the healthy range" line shows again.
- **Empty boxes, steps and tables removed:** the "When to seek help" box, three empty numbered steps, four empty table frames and an orphan "Source:" line.
- **Sentences with their opening cut, fixed:**
  - "and other institutions has identified…"
  - "recommendations, weekly weigh-ins…"
  - "weight management experts, these…"
  - ". it is associated…"
  - ". obesity significantly increases…" (its unsourced "over 200 conditions" figure removed)
  - ", For detailed strategies…"
  - ". children, BMI should…" (FAQ text and FAQ schema)
  - ". body composition is…"
  - "the other leading institutions…"
- **Words glued where a link was removed:** "theanalysis", "Theweekly-weighing", "calculationsboth", "theoverview", plus the orphan ", :".
- **Wrong history claim:** `/blog/bmi-limitations/` said BMI became the screening standard "in the 1970s when insurance companies needed…". It now says Keys named it in 1972 and NIH and WHO guidelines adopted it in the 1980s and 1990s, matching `/blog/bmi-history/`.
- **Related blocks:** six duplicate cards (old slugs that redirect to the same page) and two cards that linked nowhere are removed.
- **Calculators hub:**
  - Three worked examples disagreed with the tools they describe:
    - kids example: 16.8 / 50th percentile, the tool says 16.9 / 54.5th;
    - ideal-weight example: 120–144 lb with wrong Robinson and Miller values, the tool says 129–135 lb;
    - lean-body-mass example: 141 lb with a body-fat "healthy range" claim, the tool says 128.5 lb.
  - The Healthy BMI Range card claimed the range "varies by age, sex, and ethnicity".
- **Other leftovers:**
  - "(teaser)" removed from a women-page H2.
  - The `/blog/bmi-chart-explained/` grids coloured boundary cells by the wrong category (5′2″ at 100 lb = BMI 18.3 was green). All 104 cells are recoloured from the exact BMI in the `/bmi-chart/` tints. The legend table, cut to four rows, is complete again.

### 2. D-11 and option B
- **`/blog/healthy-bmi-range/`:**
  - The "optimal" 19–24 (women), 20–25 (men) and 23–28 (65+) takeaways go.
  - The two sections built on them become one answer: the same 18.5–24.9 for women and men, with the CDC NCHS body-fat difference.
  - The figure that drew the healthy band "widening" after 64 is removed. The age table, which frames Winter 2014 as an observed association, stays.
- **`/blog/bmi-formula/`:** the FAQ's "19–24 for women, 20–25 for men" is removed, in both the visible text and the schema.
- **`/blog/bmi-limitations/`:** "optimal BMI increases with age (25–27)" becomes the observational framing (Winter 2014, BMI 23–33, not a target).
- **`/about/`:** the women and men calculator cards said the tools are "tailored for male physiology" or "account for" body fat. They use the same adult cut-offs; the cards now say what the pages add.
- **Option B:** our own protein targets (0.7–1 g per lb) and the unsourced "maintenance calories reset hormones" claims are removed from `/blog/bmi-tracking-guide/`, `/blog/how-to-lower-bmi/` and `/blog/bmi-and-metabolism/`.

### 3. Shared components: impeccable polish, no copy changes
- **Buttons:** all 31 inline-styled button links (white on 2.1–3.7:1 cyan, green, amber, pink and purple, gradients, glow) become `.cta-button`, the flat cyan-700 of D-13 at 5.4:1; `.cta-button--sm` inside cards.
- **Bylines:** the 34 inline styles are removed, including the side stripe on 21 pages. Every byline is now the men-page byline.
- **Emoji icons removed:**
  - 6 on the homepage and 8 on `/blog/underweight-bmi-risks/`;
  - the ⚕️ and 📚 CSS icons;
  - the 27 emoji in calculator result headings (`calculator.js`, every calculator).
- **No card inside a card:** related cards and FAQ items inside a section card render flat, as on the men page.
- **Contrast:**
  - Chart bars, segments and steps that carry white text use new strong category shades, all 5:1 or better. Unlabeled bars keep their look, so the men page is pixel-identical before Calculate.
  - Cyan gradient fills are flat.
  - Inline cyan and rainbow link colours become `--link`.
- **DESIGN.md:** records the shades, tints, `.cta-button`, the flat-card rule and the icon ban, and retires the stale "gradient-and-shadow" CTA guidance that contradicted D-13.

### 4. Gate
- **`scripts/check_content_integrity.py`** is new and imported by `check_structure.py`. It fails a page on:
  - a call to action without a link;
  - a box with only its title, a step with only its heading, an empty table frame, an empty result box, or a padded empty box;
  - a paragraph or sentence that starts mid-sentence, or ", For …" joins;
  - a duplicate or dead related link, or cards inside a paragraph;
  - emoji in visible text;
  - inline-styled button links or bylines;
  - D-11 sex-specific ranges;
  - "(teaser)", TODO or TBD in headings.
- The pre-CMB-010 site scores **5/40** against it.
- `research/site-checks/` holds the chat-side browser probes behind this batch.

### 5. Dates
- The 19 pages whose visible text changes move to 2026-10-14: `lastmod` on all 19, schema `dateModified` on the 13 that carry one.
- Rule from DEVLOG §4; checked with `research/dates/date_truth.py`.

### Chat results
- **Gates:** check_structure 40/40; verify, schema and number audit clean; markup clean on all 37 changed pages; `date_truth` 40/40 after a 2026-10-14 commit.
- **Calculators:** jsdom 77/77; Chromium end-to-end 1,161 checks, 0 failures.
- **Browser:** FAQ 25/25; menu 41/41; no page wider than the screen at 360/390/1280 px.
- **Detector:** 734 → 339 findings (−54%), no page worse; `/men-bmi-calculator/` 0.
- **Visible-text diff:** only the changes listed above.

### Not in this batch
- **Calculator results panel:** the detector cannot open it, so chat snapshotted each calculator with its results showing. Even the men page has 28 findings there: the amber BMI value at 1.8:1, white labels on the BMI scale, category-coloured table text, cards inside the results card. Next batch: CMB-011.
- **Per-page leftovers** for the D-14 rebuilds: tiny SVG labels, skipped headings, KPI top borders, the `/calculators/` card stripes, and the remaining nested cards on the calculator pages.

## Rules
- Only `apply_build.py` writes files. Do not edit any file by hand (DEVLOG.md in the prompt's DEVLOG step is the only exception).
- No network. Do not push.
- STOP at the first failed check and report it in the REPORT block; do not improvise a fix.

## Steps

### 0. Clean start
0.1 `git branch --show-current` → `main`.
0.2 `git status --porcelain` must print exactly one line: `?? research/cmb-010-sitewide-repair/`.
0.3 `git log --oneline -6 | grep -c "CMB-009"` → 1 or more. If 0, STOP: CMB-009 must run first.

### 1. Dry run
`python3 research/cmb-010-sitewide-repair/apply_build.py --dry-run`
Must print exactly: `DRY RUN — applied: 9 new files, 43 replaced files, 0 edits, 0 deletions`. An `ABORT` line → STOP and report the list.

### 2. Apply
`python3 research/cmb-010-sitewide-repair/apply_build.py`
Must print exactly: `applied: 9 new files, 43 replaced files, 0 edits, 0 deletions`.

### 3. Gates (all must pass)
3.1 `python3 scripts/check_structure.py` → first line `check_structure: 40/40 pages pass`.
3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`.
3.3 `node --check assets/js/calculator.js` → no output, exit 0.
3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → last line ends `not allowed: none`.
3.5 `python3 research/tech-cleanup-checks/schema_check.py` → `schema check: missing BreadcrumbList: none | WebApplication without author: none`.
3.6 `for f in $(git diff --name-only HEAD -- '*.html'); do python3 scripts/check_markup.py $f >/dev/null || echo "MARKUP FAIL $f"; done` → no output (37 files checked).
3.7 `python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html; echo $?` → only `0`.
3.8 Each prints the number shown:
- `grep -o 'class="cta-button' index.html */index.html blog/*/index.html | wc -l` → `31`
- `grep -l '<p class="byline" style=' index.html */index.html blog/*/index.html | wc -l` → `0`
- `grep -o 'er-icon' assets/js/calculator.js | wc -l` → `0`
- `grep -o 'id="women-weight-diff"\|id="newbmi-weight-diff"' women-bmi-calculator/index.html new-bmi-calculator/index.html | wc -l` → `2`
- `grep -o 'Optimal range for\|19&ndash;24 for women\|19–24 for women' blog/healthy-bmi-range/index.html blog/bmi-formula/index.html | wc -l` → `0`
- `grep -o 'per pound of body weight' blog/bmi-tracking-guide/index.html blog/how-to-lower-bmi/index.html | wc -l` → `0`
3.9 Browser, jsdom and detector checks: the box has none (DEVLOG §4) → record as skipped. Chat's results are under "Chat results".

### 4. Commit
```
git add -A
git commit -m "fix: sitewide repair of stripped links, sentences and boxes; D-11 and option B on old guides; shared components polished (buttons, bylines, emoji, nested cards, contrast); content-integrity gate (CMB-010)"
```

### 5. Date check (needs the commit)
`python3 research/dates/date_truth.py > /tmp/cmb010-dates.txt; echo $?; grep -c '^ok' /tmp/cmb010-dates.txt; grep '^BAD' /tmp/cmb010-dates.txt; rm /tmp/cmb010-dates.txt` → `0` and `40`.
- This holds when the commit date is 2026-10-14.
- On a later day, the 19 pages this batch changes report BAD by the day difference. Record the output; don't fix it.

### 6. DEVLOG
Run the DEVLOG step from the prompt (commit DEVLOG.md too; don't push).

### 7. REPORT
```
REPORT CMB-010 SITEWIDE-REPAIR
status: OK | STOPPED at step N (reason)
step 0: branch <0.1> | porcelain <0.2> | CMB-009 commits <0.3>
dry-run: <line>
apply: <line>
gates: 3.1 <line> | 3.2 <line> | 3.3 <exit> | 3.4 <last line> | 3.5 <line> | 3.6 <output or none> | 3.7 <exit> | 3.8 <n> <n> <n> <n> <n> <n> | 3.9 skipped (no browser/jsdom in box)
commit: <git log --oneline -2>
date check: exit <n> | ok <n>/40 | BAD lines if any
final: <git status --short, or "clean"> on <git branch --show-current>
```
