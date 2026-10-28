# /body-fat-calculator/ — CMB-020 build record

D-14 rebuild #9. The page owns 329 keywords worth 147,710/mo (`research/keyword-ledger.csv`): "body fat calculator" 74,000
(primary), "bfp calculator" 40,500 (KWP's group for "body fat percentage calculator"), "body fat calculator online" 4,400,
"fat calc" 2,900, "bf calculator" 1,900, then the method phrasings ("bodyfat calculator caliper" 1,000, "7 site skinfold
calculator" 320, "3 site skinfold calculator" 260, "body fat calculator height weight" 170, "relative fat mass
calculator" 70), the accuracy phrasings ("most accurate body fat calculator" 390, "accurate body fat calculator" 170),
"body fat calculator female" 1,000 and "male" 720, and the fat-mass phrasings ("body fat weight calculator" 210, "fat mass
calculator" 170). Army and Navy standards queries belong to the planned army- and navy-body-fat-calculator pages; the
healthy and ideal ranges to `/body-fat-percentage-chart/`; measuring at home, calipers and scales to
`/blog/how-to-measure-body-fat/` (ledger owners).

## Wedge
Owner's SERP pastes of 2026-10-28 (US/English, not personalized): "body fat calculator", "body fat percentage
calculator", "body fat calculator female". Every result is a calculator that prints a number from the Navy tape method,
BMI or skinfolds and stops there; none says how close that number is likely to be. This page does, for each method:
- **waist and height (relative fat mass, Woolcott & Bergman 2018) and height and weight (Deurenberg 1991)** are checked on
  CDC's own DXA scans of US adults aged 20 to 59 (NHANES 2011–2018, `bfc_stats.py`): within 3 and 5 points, typical miss,
  average error overall and by BMI and age group, the two formulas compared in the same people, and for any estimate the
  middle half and median of the scans of people whose formula gave about the same estimate (the calculator shows these);
- **the tape measure and calipers**, which CDC's survey can't check (no neck or skinfold measurements), rest on published
  DXA comparisons: 1,407 Army recruits (Foulis et al., 2023: 6.0 points low) and 437 college students (Burns et al., 2019:
  seven-site skinfolds 1.4 points below DXA on average, Table 3 "DXA–Surrogate"; average miss, MAPE, 11.7%, the lowest of
  seven methods);
- the result is placed on the provisional ranges (Gallagher et al., 2000) and among US adults of the same sex and age
  group, read exactly as `/body-fat-percentage-chart/`'s rank tool reads `bfpc_stats.json`; the results say both treat
  the estimate as a scan reading, so they are only as close as the estimate.
- D-15: `bodyfatpercentagecalc.com` stays unlinked; this page's distinct asset is the DXA check. Chat could not open the
  sister site from its tools, so the owner should confirm its calculator page doesn't make the same pitch.

## Data (`bfc_stats.py`, our calculation)
- NHANES 2011–2012 to 2017–2018 DEMO, DXX, BMX; weights WTMEC2YR / 4; adults 20–59, not pregnant, valid DXDTOPF:
  10,864 (asserted equal to `bfpc_stats.json`: n and means by sex). RFM needs height and waist (5,388 women, 5,363 men),
  Deurenberg needs BMI (5,446 and 5,383). Error = formula minus scan.
- Exact ties: BMI and DXDTOPF are recorded to 0.1 and age in whole years, so a Deurenberg estimate and its error are exact
  hundredths, rounded so before any comparison (RFM to 10 decimals, which only removes float noise: heights are recorded
  to 0.1 cm, 12 in 2013–2014 to 0.01, and waists to 0.1, so a non-tie lies at least 0.000009 from any boundary). The
  independent fact-check found float noise deciding these ties: Deurenberg within 3 points for women was 41.4%, is 41.5%;
  30 of the 81 Deurenberg calibration windows change their count by 1 to 4.
- Taylor linearization over 59 strata and 121 PSUs (df 62); a difference is stated only when its 95% CI excludes 0.
- Percentiles: the weighted midpoint rule of `bfpc_stats.py` (each reading's weight centred on it, linear in between),
  the rule behind the page's US comparison, taken over distinct values so tied readings' order can't matter. On the 50
  quartiles the page prints from `bfpc_stats.json` the two agree within 0.08 (asserted); `bfpc_stats.py` applies it
  reading by reading after an unstable sort, and a stable sort alone moves 5 of those 50 by 0.1 when printed (DEVLOG §5).
  The CMB-019 rule (CDF over distinct values) runs about 0.07 low on readings recorded to 0.1 and is not used here.
- Medians of the error get a 95% CI by Woodruff's method (CI of the share at or below the median, mapped back through the
  percentile rule): RFM +2.32 [2.11, 2.53] for women, +0.81 [0.63, 1.03] for men, against the authors' 2005–2006
  validation medians 0.9 [0.6, 1.1] and 0.5 [0.3, 0.8] (Woolcott & Bergman 2018, Table 2): women clearly higher, men not
  clearly different. Scanner model (Hologic Discovery A against the QDR 4500A) and ages (20–59 against 20–69) also differ,
  so the page names no cause.
- Calibration: for each whole percent b, people whose formula gave b − 1 to under b + 1, if 30 or more: the 25th, 50th
  and 75th percentile of their scans.
- Round once: `keep()` stores 4 decimals (more only where 4 would print differently); the generator prints halves up, as
  JavaScript's `toFixed`, and stops if Python's own format would print a figure differently.
- Results: within 5 points RFM 74.3% / 86.3% (women / men), Deurenberg 62.4% / 66.4%; within 3 points 49.9% / 61.5% and
  41.5% / 44.3%; typical miss 3.54 / 2.73 and 4.67 / 4.21; mean error RFM +2.33 [2.15, 2.52] / +0.74 [0.60, 0.89],
  Deurenberg −0.19 [−0.47, 0.09] / −0.13 [−0.35, 0.10] (includes 0); Deurenberg at a healthy BMI −3.06 / −2.90, with
  obesity +4.11 / +2.88, ages 20–39 −2.20 / −2.30, 40–59 +1.68 / +2.14; same people: RFM within 5 points for 12.0 [9.7,
  14.3] more women in 100 and 19.9 [18.1, 21.7] more men, typical miss 1.12 [0.97, 1.27] and 1.47 [1.36, 1.59] points
  less. The only group error whose CI includes 0: RFM, men, healthy BMI (+0.09), named on the page.

## Page (`gen_bfcalc.py`, run on the B2 page at f365b8b)
H1 "Body Fat Calculator" + byline → one-line intro and source note → the calculator → key takeaways → disclaimer → 9
chips → how to read your result (the starting values: a woman of 35, 5′4″, 150 lb; tape 13 / 31 / 40 in → 33.0%;
height and weight → 33.5%; waist and height with a 34-in waist, a field that starts empty → 38.4%; the figure shows the
three estimates and the scans behind the two checked formulas: 34.0 / 36.8 / 39.5% (446 women) and 33.7 / 36.1 / 38.5%
(543)) → how accurate is each method (the four methods, the paired comparison, the error figure, one table per formula,
the RFM median errors against its authors', the Deurenberg group misses, the published studies) → one section per method
(formula, where to measure, how close it gets; the tape section cites the Army's 2013 worksheets and names Army
Directive 2023-11, the one-site test; the calipers section takes its coefficients from Topend Sports and names Serra's
0.0001395 variant) → what your result means (provisional ranges, two tables; US means) → 9 FAQ → sources and method →
one related block. No `<article>` (D-16), no page-level style, no inline style in `<main>`. Head: title "Body Fat
Calculator: 4 Methods Compared With DXA Scans", new meta, OG, Twitter (the description says which methods were checked on
CDC's scans); JSON-LD `@graph` WebPage (`dateModified` `{TODAY}`, `primaryImageOfPage`), WebApplication `#calculator`
(image list, featureList, author), BreadcrumbList, FAQPage. The menu marks Body Fat as the current page (the B2 shell
marked Obesity Statistics).

## The calculator (`.calculator-card.bfc`, DESIGN.md "Body fat calculator (CMB-020)")
- Inputs: woman / man, US / metric, method (tape, waist and height, height and weight, calipers with 3 / 7 sites);
  height, weight (optional except for height and weight), age 18–79 in whole years; tape: neck, waist and, for women,
  hips; RFM: waist at the top of the hip bones; calipers: 3 sites by sex or 7 sites, in mm.
- Limits: height 4 ft–7 ft 6 in (122–229 cm); weight 50–700 lb (23–318 kg); neck 8–30 in (20–76 cm); waist 15–80 in
  (38–203 cm); hips 20–80 in (51–203 cm); skinfolds 1–100 mm; an estimate under 2% or over 70% is refused.
- Units: the switch converts every length to 0.1 cm or in and the weight to 0.1; switching back with nothing retyped
  restores the numbers as they were, so flipping units never changes a result (the fact-check saw whole centimeters turn
  the starting 33.0% "High" into 32.9% "Healthy").
- The tape equations take inches (centimeters ÷ 2.54); BMI as the calculators (703 × lb ÷ in², or kg ÷ m², rounded half
  up to 0.1). The estimate prints to 0.1 (halves up, with a 1e-9 nudge so exact hundredths round up); its range, US share,
  calibration window and fat mass come from that value.
- Results: card tinted by the provisional range (neutral under 20); how close (the calibration window, with a line that
  trained technicians took CDC's measurements and measuring yourself adds some error; or the published study, with a
  line that measuring at home can add more); where it falls (the CMB-016 figure: the US middle half and 10th–90th
  percentile for the age group, the four provisional bands, the estimate; a line that the share and the range are only
  as close as the estimate); fat and lean mass with a weight; other estimates (other methods the numbers allow, each with
  its check "for X% of US women aged 20 to 59"; a pane counts only once typed in, the height-and-weight formula whenever
  a weight is entered); source line.

## Checks
- `bfcalc_test_playwright.py` (447 checks): typed-in published values (the Army examples, the JP3 density, the Woolcott
  Table 2 medians, the fact-check's exact ties), the prose rebuilt from the stats, every table cell, both figures at their
  drawn positions, the tool's data and 26 cases (worked out here from the formulas and the stats), the switches (the
  unit switch keeps 33.0% "High" both ways; 5′4.5″ ↔ 163.8 cm, 163 cm ↔ 5′4.2″ and 68.3 kg ↔ 150.6 lb round-trip), head,
  OG/Twitter text and JSON-LD, links, chips, FAQ, widths 320/360/390/1280, table frames, label collisions, removed
  wording. Deliberate breaks on a copy each failed it (17): a calibration value, a Navy coefficient (0.18 points), the RFM women's constant, a JP7 women's coefficient, the JP3 men's age term (caught by the exact-formula check: too small to move a printed case), the Deurenberg age term, two table cells (one the exact tie, 41.5% back to 41.4%), a visible FAQ answer, the "other estimates" rule, a figure label, whole-centimeter unit conversion, no restore on switching back, the precision note, the technicians line, the ages on the other estimates and the old Burns wording
- Rebuild: `python3 research/body-fat-calculator-build/bfc_stats.py RAW research/body-fat-chart-build/bfpc_stats.json
  research/body-fat-calculator-build/bfc_stats.json` (RAW = CDC's DEMO/DXX/BMX G–J files, not in the repo) rebuilds the
  stats byte for byte; `gen_bfcalc.py` runs once on the B2 page; `pref_images.py ROOT body-fat-calculator` redraws the
  preferred images.
- Independent fact-check (separate agent, its own code on CDC's raw files, sources re-read live): 1 FAIL, 6 WARN, 12
  NOTE on the draft, all settled as FIX.md §6 lists.
