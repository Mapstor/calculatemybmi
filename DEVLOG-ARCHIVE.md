# DEVLOG archive — calculatemybmi.net
> Append-only. The oldest §6 entries of DEVLOG.md, moved here verbatim (devlog skill: past 40 entries, move the oldest 20).

### 2026-10-02 · S1 obesity-rate-by-state · chat → CC · live
- What: new page `/obesity-rate-by-state/` — CDC BRFSS 2011-2025 state rates, tile map + year slider, rankings, age 2025, CSV downloads.
- Files: `obesity-rate-by-state/`, `research/state-obesity/`, `sitemap.xml`, `us-obesity-statistics/index.html`.
- Verified: check_structure 35/35; verify.py clean; number audit clean.
- Commit: f27aa28 (pushed: yes).

### 2026-10-02 · S2 state-page-v2 · chat → CC · live
- What: real US choropleth (Census boundaries), play/slider, rich state panel (median, neighbours, CI, trend, age); visual sections replace tile grid.
- Files: `obesity-rate-by-state/index.html`, `research/state-obesity/`.
- Verified: check_structure 35/35; verify.py clean; 50 state paths rendered.
- Commit: ebf6c30 (pushed: yes).

### 2026-10-02 · C3 childhood-obesity-statistics · chat → CC · live
- What: new page `/childhood-obesity-statistics/` — NCHS 1963-2023 measured data, interactive trend chart, pictogram, age/sex/race, CSV; inbound links.
- Files: `childhood-obesity-statistics/`, `research/childhood/`, `sitemap.xml`, inbound links from `us-obesity-statistics/`, `kids-bmi-calculator/`.
- Verified: check_structure 36/36; verify.py clean; number audit clean.
- Commit: 1a120fd (pushed: yes).

### 2026-10-03 · A1 average-weight · chat → CC · live
- What: new page `/average-weight/` — NHANES 2021-2023 average weight by height and age (verified vs NCHS Series 3), compare tool, tables, chart, CSV; inbound links from `/bmi-chart/`, `/ideal-weight/`.
- Files: `average-weight/`, `research/average-weight/`, `sitemap.xml`, `bmi-chart/index.html`, `ideal-weight/index.html`.
- Verified: check_structure 37/37; verify.py clean.
- Commit: 3abb342 (pushed: yes).

### 2026-10-04 · A2 average-weight-v2 · chat → CC · live
- What: redesigned compare tool (pill toggles, slider inputs, rich results, distribution chart, BMI gauge, height rank); small-multiple page charts.
- Files: `average-weight/index.html`, `research/average-weight/`, `sitemap.xml`.
- Verified: check_structure 37/37; verify.py clean.
- Commit: a4812a7 (pushed: yes).

### 2026-10-07 · B1 body-fat-percentage-chart · chat → CC · live
- What: new page `/body-fat-percentage-chart/` — NHANES 2011-2018 DXA percentiles (verified vs BMJ 2021), rank tool, charts, X% tables, Gallagher ranges, CSV; inbound links.
- Files: `body-fat-percentage-chart/`, `research/body-fat/`, `sitemap.xml`, `blog/body-fat-vs-bmi/`, `lean-body-mass/`.
- Verified: check_structure 38/38; verify.py clean; number audit clean.
- Commit: 4f17cb0 (pushed: yes).

### 2026-10-07 · B2 body-fat-calculator · chat → CC · live
- What: new page `/body-fat-calculator/` — Navy tape, Jackson-Pollock skinfold and Deurenberg BMI methods (verified), results on NHANES DXA percentiles; inbound links.
- Files: `body-fat-calculator/`, `research/body-fat-calculator/`, `sitemap.xml`, `body-fat-percentage-chart/`, `lean-body-mass/`, `blog/body-fat-vs-bmi/`.
- Verified: check_structure 39/39; verify.py clean.
- Commit: 0ac545b (pushed: yes).

### 2026-10-07 · N1 nav-hub · chat → CC · live
- What: Body Fat calculator in header menus on all 39 pages; `/calculators/` card, table row, ItemList, counts 8→9.
- Files: 39 pages, `calculators/`, `research/nav-hub/`.
- Verified: check_structure 39/39; verify.py clean; nav check: all pages have 2.
- Commit: 4b93338 (pushed: yes).

### 2026-10-07 · G1 how-to-measure-body-fat · chat → CC · live
- What: new guide `/blog/how-to-measure-body-fat/` — methods scored against DXA (Burns et al. PLOS ONE 2019), comparison chart + table; inbound links.
- Files: `blog/how-to-measure-body-fat/`, `research/how-to-measure-body-fat/`, `sitemap.xml`, `body-fat-calculator/`, `blog/body-fat-vs-bmi/`, `blog/index.html`.
- Verified: check_structure 40/40; verify.py clean; number audit clean.
- Commit: c838370 (pushed: yes).

### 2026-10-08 · W1 what-is-bmi · chat → CC · live
- What: rebuilt sourced explainer with live BMI explorer, CDC/NHLBI/WHO sources, links to every BMI guide.
- Files: `blog/what-is-bmi/`, `research/what-is-bmi/`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean.
- Commit: fe05b91 (pushed: yes).

### 2026-10-08 · T1 tech-cleanup · chat → CC · live
- What: BreadcrumbList on `/blog/`, `/contact/`, `/privacy/`, `/terms/`; `author` on WebApplication of homepage + 7 calculators; `/blog/bmi-for-athletes/` rebuilt with sources; 9 unreferenced assets removed.
- Files: 15 pages, `research/tech-cleanup/`, `research/tech-cleanup-checks/schema_check.py`, `research/bmi-for-athletes/`.
- Verified: check_structure 40/40; verify.py clean; schema check (missing BreadcrumbList / WebApplication without author) both none.
- Commit: 8819105 (pushed: yes).

### 2026-10-08 · K1 calc-fix · chat → CC · live
- What: mobile menu double-binding on 9 calculator pages, results now follow the user's units (metric kg/cm first), 6'0" height format (was 5'12"), neutral status wording, remove invented "Risk Level" rows and ACE body-fat tiers, spacing above Key Takeaways.
- Files: `assets/js/calculator.js`, `assets/css/styles.css`, `research/calc-fix/`, `research/calculator-checks/`.
- Verified: check_structure 40/40; verify.py clean; `node --check assets/js/calculator.js` OK; forbidden-tokens grep = 0.
- Commit: aababbb (pushed: yes).

### 2026-10-08 · K2 audit-fix · chat → CC · live
- What: `/blog/bmi-by-age/` leaked meta text repaired; `/about/` overflow at 390 px fixed; `/privacy/` operator address updated; `/calculators/` and `/ideal-weight/` "WHO-endorsed" and "age-adjusted" removed; New BMI + kids results now follow units; kids advice de-prescribed.
- Files: `about/`, `blog/bmi-by-age/`, `calculators/`, `ideal-weight/`, `privacy/`, `assets/js/calculator.js`, `research/audit-fix/`, `research/audit/` (jsdom audit scripts, reference only).
- Verified: check_structure 40/40; verify.py clean; `node --check` OK; `WHO-endorsed` grep = 0.
- Commit: a7f23f6 (pushed: yes).

### 2026-10-08 · K3 legacy-fix · chat → CC · live
- What: sitewide removal of age-adjusted / sex-specific range myths (D-11); corrected Asian BMI cut-offs (WHO 2004 action points, not new definitions); broken-sentence repairs; New BMI comparison value fix; distance formatting ("1 lb (0.5 kg)").
- Files: 15 pages — `about/`, `age-bmi-calculator/`, `assets/js/calculator.js`, `blog/bmi-by-age/`, `blog/bmi-categories/`, `blog/what-is-bmi/`, `calculators/`, `ideal-weight/`, `index.html`, `kids-bmi-calculator/`, `lean-body-mass/`, `men-bmi-calculator/`, `new-bmi-calculator/`, `women-bmi-calculator/`, `research/legacy-fix/`.
- Verified: check_structure 40/40; verify.py clean; `node --check` OK; forbidden-tokens grep = 0.
- Commit: e0cb070 (pushed: yes).

### 2026-10-08 · G2a kids-rewrite · chat → CC · live
- What: `/kids-bmi-calculator/` long-form rebuilt (~1,500 sourced words replace 5,349 unsourced); new girls/boys BMI-for-age percentile cut-off tables from CDC LMS; teen-focused title + meta.
- Files: `kids-bmi-calculator/`, `research/kids-rewrite/`, `research/g2/g2_kids.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; 5 FAQ items; girls table present.
- Commit: 88cb9e5 (pushed: yes).

### 2026-10-09 · G2b ideal-rewrite · chat → CC · live
- What: `/ideal-weight/` rebuilt by-height chart (women 5'0"–6'0", men 5'2"–6'6"); formula history corrected to Pai & Paloucek 2000 and Peterson 2016; references fixed (Miller citation, Peterson PMC).
- Files: `ideal-weight/`, `research/ideal-rewrite/`, `research/g2/g2_ideal.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; 2 tables present; forbidden tokens 0.
- Commit: 69879fa (pushed: yes).

### 2026-10-09 · G2c home-rewrite · chat → CC · live
- What: homepage sourced health-risk summary (NHLBI / Winter 2014 / Wing 2011); CDC/NHLBI/WHO wording in "Learn About BMI"; FAQ rewritten with sources; "BMI Classification Table" renamed; Body Fat Calculator card added to "More Calculators".
- Files: `index.html`, `research/home-rewrite/`, `research/g2/g2_home.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; forbidden tokens 0; body fat card present.
- Commit: 6a71e7e (pushed: yes).

### 2026-10-09 · G2d age-rewrite · chat → CC · live
- What: `/age-bmi-calculator/` long-form rebuilt — US averages by age (our verified NHANES calc + Data Brief 508 + DXA analysis); official PAG + AASM guidance; prescriptive sections removed; sourced FAQ.
- Files: `age-bmi-calculator/`, `research/age-rewrite/`, `research/g2/g2_age.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; "US women/men by the numbers" sections present; forbidden tokens 0.
- Commit: edb2cb2 (pushed: yes).

### 2026-10-09 · G2e calcs-rewrite · chat → CC · live
- What: `/calculators/` — age-myth wording purged (comparison + decision + FAQ + meta); gender-specific guidance language replaced with NIH waist / body fat / ACOG; corrected lean-mass spread (1.6 kg women, 5.8 kg men); New BMI described honestly; Body Fat row in decision table.
- Files: `calculators/`, `research/calcs-rewrite/`, `research/g2/g2_calcs.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; forbidden tokens 0; "Estimate your body fat percentage" present.
- Commit: 74862e2 (pushed: yes).

### 2026-10-09 · G2f cats-rewrite · chat → CC · live
- What: `/blog/bmi-categories/` — WHO attribution (not CDC) for 1995/2000 reports; eight unsourced risk lists replaced by NHLBI + Flegal 2013 (HR 1.29 for BMI 35+) + IARC paragraphs; invented sex-specific "optimal" ranges and overweight-paradox speculation removed.
- Files: `blog/bmi-categories/`, `research/cats-rewrite/`, `research/g2/g2_cats.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; forbidden tokens 0; "hazard ratio 1.29" present.
- Commit: 7e870be (pushed: yes — last push).
