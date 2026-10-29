# /blog/how-to-measure-body-fat/ — CMB-021 build record

D-14 rebuild #10. The page owns 913 keywords worth 114,170/mo (`research/keyword-ledger.csv`): "how to calculate body fat
percentage" 18,100 (primary), then "how to figure body fat" and "how to check fat percentage" 6,600 each, "how to check
your body fat" 5,400 and the rest of the calculate / check / find phrasings (about 86k in all); scales 8.1k ("how do scales
measure body fat" 1,000, "how accurate are bodyfat scales" 880, "how does a scale determine body fat" 590, "how do body
composition scales work" 480); at home 4.3k ("how to find body fat percentage at home" 1,300); how much body fat to have
3.5k ("how much body fat should i have" 1,300, "how much body fat should a women have" 880); calipers 2.4k ("measure body
fat caliper" 590); tape 1.1k ("tape measure fat percentage" 590); InBody 670 ("how accurate is the in body scan" 320);
Bod Pod 70. Calculator queries belong to `/body-fat-calculator/` and the ranges by age to `/body-fat-percentage-chart/`
(ledger owners).

## Wedge
Owner's SERP pastes of 2026-10-29 (US/English, not personalized): "how to calculate body fat percentage", "how to
measure body fat percentage", "how accurate are body fat scales". The AI Overviews list the methods, quote the ACE fitness
tiers (D-11) and give scales a loose "21% to 34%" error; "Is 30% body fat chubby?" is in all three People-also-ask boxes
(the chart page owns it; this page links there). The page answers the question with the steps for each home method,
worked by hand for one example man, then puts numbers on how close the tested methods get to a DXA scan:
- **seven methods against one scanner, the same people:** Burns et al. (2019), Table 3, all seven methods
  (`burns_2019_table3.json`): every method read lower than DXA on average, from 1.0 point (underwater weighing) to 4.9
  (a hand-held impedance device); the average miss as a share of the scan (MAPE) from 11.7% (seven-site skinfolds) to
  21.9%; average difference inside the ±2.7-point equivalence margin: underwater weighing, skinfolds, the Bod Pod and a
  four-electrode analyzer (single readings miss by more). The G1 page drew the signed means as magnitudes and left two
  methods without numbers; the full table fixes both;
- **the two home formulas on CDC's own scans** (`htm_stats.py`, our calculation): average miss 3.1 points for relative fat
  mass and 4.4 for the Deurenberg BMI formula (10.4% and 14.0% of the scan's reading). The page doesn't set those shares
  beside Burns's: CDC's scans average 32.9% body fat against the students' 27.0%, so the same miss in points is a smaller
  share (the CMB-021 fact-check; an average-miss figure that drew both on one axis was dropped);
- **the formulas disagree for the same person:** more than 5 points apart for 38% of US women and 15% of men; the second
  figure shows the split (within 3 points / 3 to 5 / more than 5: women 37 / 25 / 38%, men 60 / 25 / 15%);
- **what a measuring slip costs:** about a point for 1 inch on the waist or 5 lb on the scale (medians over CDC's
  measurements), 1.2 to 1.9 points for the tape and calipers at stated example people;
- **scales and clinic devices:** CDC's own impedance documentation (how the test works, percent fat "subject to
  additional error", who was not tested), three smart scales against DXA (Frija-Masson et al., 2021: median weight
  differences 0 to 0.3 kg, fat mass 2.2 to 4.4 kg low), InBody 770 and SECA mBCA 515 (Lahav et al., 2021), the tape method in 1,407 Army
  recruits (Foulis et al., 2023, replacing the G1 page's conference abstract).

## Data (`htm_stats.py`, our calculation)
- The sample, weights, design, exact-tie rounding and percentile rule of `research/body-fat-calculator-build/bfc_stats.py`,
  whose n, within-3 and within-5 shares and typical misses this script asserts equal: NHANES 2011–2012 to 2017–2018 DEMO,
  DXX, BMX; WTMEC2YR / 4; adults 20–59, not pregnant, valid DXDTOPF: 10,864; Taylor linearization over 59 strata and 121
  PSUs (df 62).
- Average miss in points = mean of |formula − scan|: relative fat mass 3.13 [3.05, 3.21], Deurenberg 4.44 [4.35, 4.53]
  (women and men asserted equal to `bfc_stats.json`'s typical misses). As a share, mean of |formula − scan| / scan × 100
  (Burns et al.'s MAPE): relative fat mass 10.37 [10.05, 10.70] (women 9.92, men 10.82; ages 20–29 10.74), Deurenberg
  13.97 [13.64, 14.29] (women 12.03, men 15.88; ages 20–29 16.94). The average scan reads 32.94% [32.64, 33.25] (women
  38.71, men 27.24), above Burns's 27.0%, which is why the page doesn't compare the two MAPEs.
- The two formulas for the same person (5,386 women, 5,361 men with both): more than 5 points apart 38.3% [36.4, 40.2] and
  15.3% [14.0, 16.6]; more than 3 points apart 63.1% and 40.1% (so within 3 points 36.9% and 59.9%, 3 to 5 points 24.8%
  and 24.8%: the second figure, whole percents 37 / 25 / 38 and 60 / 25 / 15); weighted median distance 4.08 and 2.43
  points; relative fat mass the higher of the two for 76.5% and 63.8%.
- A measuring slip, worked from each person's own measurements (CDC records cm and kg): +1 inch on the waist moves relative
  fat mass by a median of +0.92 (women) and +0.90 (men) points; +5 lb moves the Deurenberg estimate by +1.03 and +0.88
  (through BMI); a height entered 1 inch short by +1.06 and +0.99. Weighted medians by the midpoint rule over distinct
  values.
- Medians from `bfpc_stats.json` print as whole percents (38 and 26 at ages 20–39): the men's, 26.17 there, sits on a tie
  boundary and moves between 26.13 and 26.18 with the order of tied readings (CMB-021 fact-check; DEVLOG §5).
- Margins the method note states: every share quoted has a 95% half-width under 2 points (the largest, 1.88, for women
  more than 5 points apart), every average miss under 0.4 (MAPE 0.33).
- Round once: `keep()` as `bfc_stats.py`; the generator prints halves up and stops if Python's own format would print a
  figure differently.
- Rebuild: `python3 research/how-to-measure-body-fat-build/htm_stats.py RAW research/body-fat-calculator-build/bfc_stats.json
  research/how-to-measure-body-fat-build/htm_stats.json` (RAW = CDC's DEMO/DXX/BMX G–J files, not in the repo) rebuilds
  the stats byte for byte.

## Page (`gen_htm.py`, run on the G1 page at 7662c95)
H1 "How to Calculate Body Fat Percentage" (kept, so the `/blog/` hub card and its ItemList still match) + byline → three
intro paragraphs (the questions; how home methods work and the seven-method study; the promise line) → key takeaways (the
answer: the relative fat mass formula and its check on CDC's scans; 5 bullets) → disclaimer → the hero figure (Burns's
seven methods, method minus DXA with the 90% CI, a dashed zero line per row) → 8 chips → how to calculate body fat
percentage at home (relative fat mass, the Navy tape method, the Deurenberg formula, Jackson–Pollock 3-site calipers with
Siri: steps and the example man worked by hand, 26.2 / 20.4 / 24.0 / 18.5%; no cited study checked the 3-site version
against DXA, and the page says so) → how close tested methods get to a DXA scan (the seven-method table, the two formulas
on CDC's scans in points and as shares, three more comparisons) → how accurate are body fat scales → how to measure body
fat accurately (the measuring-slip table in four groups, repeat and average, the pre-test routine, compare like with like
and the formula-gap figure) → lab and gym methods (DXA, underwater weighing, the Bod Pod, near-infrared) →
what your number means (provisional ranges; US medians at 20–39; links to the chart and body fat vs BMI) → 10 FAQ → sources
and method → one related block. No `<article>` (D-16), no page-level style, no inline style in `<main>` outside the
figures; no visible dates (D-12); no fitness tiers (D-11).
Head: title "How to Calculate Body Fat Percentage: Home Methods vs DXA"; new meta description, OG and Twitter text (with
`twitter:title` and `twitter:description`); the preferred image; JSON-LD `@graph`: Article (`@id` and `datePublished`
kept, `dateModified` `{TODAY}`, author and publisher named, image list, `primaryImageOfPage`, citations), BreadcrumbList
(kept), FAQPage (= the visible answers). The G1 graph's Organization and Person nodes go (named inside the Article). The
menu marks Guides, in both menus (the G1 shell marked Obesity Statistics).
Tables: `.data-table--fit.data-table--wrap` (styles.css, DESIGN.md "Tables with long row labels (CMB-021)"): row labels
wrap, so both three-column tables fit a 320 px phone; the slip table's groups are `tbody` elements led by
`th[scope="rowgroup"][colspan="3"]`; a number keeps its unit on one line (no-break space).

## Images
`research/preferred-images/pref_images.py ROOT how-to-measure-body-fat` draws the hero without a word or number (dots, 90%
CI lines, dashed zero lines, light grid lines at −6, −4 and −2; −6.5 to +0.5 points, centered) at 1200×675, 1200×900 and
1200×1200, redrawn byte for byte. The G1 OG card `blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png` (only this
page used it) is deleted.

## Checks
- `htm_test_playwright.py` (348 checks): Burns's Table 3 typed in again against `burns_2019_table3.json`; the check on CDC's
  scans typed in against the stats files; the equations written again (the Army examples, the JP3 density, the worked
  example, the tape and caliper slips); every sentence that states a number rebuilt and found on the page (FAQ answers
  included); removed wording; both tables cell by cell (groups and scopes); both figures at their drawn positions, with
  titles and descriptions; head, OG/Twitter text and JSON-LD (dates = sitemap lastmod, `datePublished` kept, FAQ = visible
  answers); the menu; links (internal 200, anchors, outside links in the registry, new tab); chips; FAQ opens; widths
  320/360/390/1280, table frames, rendered labels (inside the figure, no overlap, on no shape or line; an in-bar label
  wholly inside its bar); no JavaScript error. Deliberate breaks on a copy each failed it (22): a table value, a hero dot, a prose number, the FAQ JSON-LD, the mobile
  menu marker, the old og:image, dateModified against lastmod, the slip table without `--wrap` (too wide at 320), a figure
  label moved onto the grid, the old conference-abstract wording, an outside link not in the registry, an inline style,
  `burns_2019_table3.json`, `htm_stats.json`, an em dash, a chip to a missing section, a gap-figure segment width and a
  share label, a slip's sign, the worked example, the old "weighed within 0.3 kg" wording, the old "Obesity Statistics"
  marker.
- Independent fact-check (separate agent, its own code on CDC's raw files, the page in Chromium, sources re-read live):
  0 FAIL, 7 WARN, 13 NOTE on the draft; the 7 WARN and 10 NOTE fixed, 3 NOTE kept with reasons (FIX.md §6). 21 of the 22
  "our calculation" figures reproduced; the 22nd, the men's 20–39 median, depends on tie order and now prints whole.
