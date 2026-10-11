# DEVLOG — calculatemybmi.net
> Handoff file. Read §0–§5 and the last 10 entries of §6 before any work. Rules: devlog skill (.claude/skills/devlog/SKILL.md).

## §0 Resume here
_last update: 2026-10-11 · CMB-006 PILOT-MEN_
- Phase: `/men-bmi-calculator/` pilot built on branch `pilot/men-skills` (new NHANES US-men rank, flat FAQ/related, 680 px reading column, new OG image); `main` carries CMB-003 + CMB-004 + CMB-005 unpushed, plus this DEVLOG entry.
- Last confirmed (local, done): CMB-006 PILOT-MEN on branch `pilot/men-skills` (824bf57) — gates all pass; layout stays `unverified` (R4) until the owner's Vercel preview + `impeccable detect` check. On main: CMB-005 LIVE-FIX (2e2ca23) stacked on CMB-004 MARKUP-V2 (7c22067) and CMB-003 STEPS 0–2.
- In flight (handed, NOT confirmed): none — the pilot is a branch artifact pending the owner's preview review.
- Next action: owner runs `git push origin pilot/men-skills main`, opens the Vercel preview of `/men-bmi-calculator/`, runs `.claude/skills/impeccable/scripts/impeccable detect --viewport 390x844 <preview-url>` (R4) and sends screenshots. Chat then evaluates and proposes rollout (or adjust / drop). Project chat's next ID is CMB-007.
- Waiting on owner:
  - Push `pilot/men-skills` and `main` to GitHub (same push covers CMB-003 + CMB-004 + CMB-005 to production and makes the pilot preview available).
  - Vercel preview + R4 detect of `/men-bmi-calculator/` on the pilot branch.
  - Three pilot decisions: (a) adopt `--link #0e7490` sitewide (lives in `styles.css`, global by nature); (b) brand CTA gradient (white on cyan, 2.7:1) — keep with an R3 impeccable-ignore, or darken; (c) adopt the calculator-page pattern (flat FAQ + flat related + one 680 px reading column) across the other calculators.
  - D-12 scope call: do `/privacy/` and `/terms/` keep their "Last updated" line? Chat recommends keeping both.
  - GitHub branch deletes: `review/cmb-003`, `test/impeccable-men` (and `pilot/men-skills` if dropped).
  - IndexNow / Search Console / Bing final round (D-07).
  - Repo-visibility decision (`Mapstor/calculatemybmi` is public on GitHub).
- Open questions:
  - D-12 scope: do `/privacy/` and `/terms/` keep their "Last updated" line? Chat recommends keeping both — privacy §11 and the terms "Last Updated" clause promise that date in-text, and California's CCPA regulations require a privacy policy to state when it was last updated.
  - GitHub repo `Mapstor/calculatemybmi` is public (checked 2026-10-10): everything committed (incl. `DEVLOG.md`, `.claude/`, `research/`, `CLAIMS-DECISIONS*.csv`) is world-readable on GitHub even though `.vercelignore` keeps it off the production domain — owner decides whether to make the repo private.

## §1 Site card
- Domain · status · Raptive: calculatemybmi.net · live · Raptive ads live since late Sept 2026 (CMP owned by Raptive)
- Owner (pushes, runs account steps) · machine: Marko Visic · Mac 2 (claude-box, port 3013)
- Author (byline · credentials · sameAs): Marko Visic · pharmacist by training, MPharm, Faculty of Pharmacy, University of Ljubljana (never "registered" or "licensed") · sameAs as in `about/index.html` Person schema
- Operator: Moving Data Systems d.o.o., Smolnik 62, 2342 Ruse, Slovenia
- Repo origin · branch: https://github.com/Mapstor/calculatemybmi.git · main
- Project folder · box project · preview port: `/workspace` · claude-box on Mac 2 · 3013 (.devcontainer/port)
- Stack · Node in box: static HTML (no package.json) · v20.20.2
- Commands:
  - dev: `python3 -m http.server 8000` or `npx vercel dev`
  - build: ? (static root, no build step)
  - test: `python3 scripts/check_structure.py`; `python3 research/f1/verify.py`; `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html`
  - lint: ?
- Deploy: Vercel, git-connected since 2026-08-13; trigger `git push origin main` (owner pushes); apex `calculatemybmi.net` canonical, `www` 308 → apex
- Analytics / Search Console / Bing: GA4 via direct `gtag` behind Consent Mode v2 through Raptive's CMP; IndexNow / GSC / Bing final-round submission pending
- Data sources (registry): `research/data-sources.csv`
- Key paths:
  - 40 pages at `/`, `/blog/*`, calculators (`/age-bmi-calculator/`, `/body-fat-calculator/`, `/body-fat-percentage-chart/`, `/kids-bmi-calculator/`, `/lean-body-mass/`, `/men-bmi-calculator/`, `/new-bmi-calculator/`, `/women-bmi-calculator/`, `/ideal-weight/`), data pages (`/us-obesity-statistics/`, `/obesity-rate-by-state/`, `/childhood-obesity-statistics/`, `/average-weight/`), hub (`/calculators/`), charts (`/bmi-chart/`)
  - `assets/css/styles.css` (single stylesheet, cyan health theme)
  - `assets/js/calculator.js` (shared calculator logic for 9 pages)
  - `sitemap.xml`
  - `research/<batch>/` per content batch; `research/us-obesity-build/tools/number_audit.py`; `research/f1/verify.py` (JSON-LD, inline JS, anchors, FAQ-schema parity)
  - `scripts/check_structure.py`
- Skills in repo: `devlog`, `anti-slop-prose`, `impeccable` (installed in CMB-001)
- Design system (DESIGN.md / PRODUCT.md): `DESIGN.md` (added CMB-001; auto-extract from CSS, no interactive workshop); PRODUCT.md absent
- Other plans / ledgers: `research/keyword-ledger.csv`, `research/page-map.csv`, `research/HANDOFF.md` (superseded by DEVLOG), legacy repo-root reports (FINAL-SUMMARY.md, PRE-DEPLOY-REPORT.md once existed — now at commit 688001a; CONSOLIDATION.md, DEPLOY-CHECKLIST.md, FUNCTIONAL-AUDIT.md, QUALITY-AUDIT.md kept for the paper trail)
- Prompt code: CMB

## §2 Decisions in force
- D-01 · 2026-08-02 · No medical claims, treatment or surgery content — YMYL rejection risk (Raptive + search raters).
- D-02 · 2026-08 · GA4 wired through direct `gtag`, no GTM — GTM is a Raptive integration step, not an approval requirement; adds a per-site console we don't need.
- D-03 · 2026-08-13 · Before Git-connecting any Vercel project, `origin/main` must match local HEAD — the near-miss would have redeployed the fabricated build.
- D-04 · 2026-08-15 · No visible "Last reviewed" date; schema `dateModified` stays — the visible label implies a review cadence that doesn't exist.
- D-05 · 2026-09-30 · Consent through Raptive's CMP only; no second consent tool.
- D-06 · 2026-10 · Option B: no calorie, protein, sleep or exercise targets of our own — only official guidelines, quoted, attributed and linked.
- D-07 · 2026-10 · IndexNow, Search Console and Bing steps batched into one final round after all site work.
- D-08 · 2026-10 · Goal: every page perfect (all 40, not only new ones), before the final round.
- D-09 · 2026-10 · Design bar for data and tool pages: real interactive US map (not a tile grid), results that explain the differences and stand out, beautiful inputs, charts where nothing overlaps.
- D-10 · 2026-10-07 · Every number on a page traces to the verified registry (`research/data-sources.csv`) or our own reproducible calculation — unsourced claims are cut, not hedged.
- D-11 · 2026-10-07 · ACE (fitness-industry) body-fat tiers banned; age- or sex-specific "healthy BMI ranges" banned — adult cut-offs are the same for everyone at every age.
- D-12 · 2026-10-11 · Remove visible dates from bylines and article meta on every content page ("Reviewed <date>", "Updated <date>", "<Month YYYY> • N min read"). Schema `dateModified` stays (D-04). Data-provenance dates stay (survey periods, "CDC released/updated …", "retrieved <month>"). Scope: 22 content pages — 7 show "Reviewed <date>" (e.g. `/average-weight/` "Reviewed October 4, 2026", `/bmi-chart/` "Reviewed 27 September 2026"), 2 show "Updated October 7, 2026" (`/blog/what-is-bmi/`, `/blog/bmi-for-athletes/`), 13 older guides show "February 2026 • N min read" (6 of them also show "Updated February 2026"). Resolves the earlier "Reviewed/Updated" byline open question.

## §3 Rejected — don't re-propose
- 2026-08-02 · Medical / treatment / surgery content — YMYL rejection risk.
- 2026-08 · Tag Manager (GTM) alongside direct gtag — Raptive overhead with no site benefit.
- 2026-08-15 · Visible "Last reviewed <date>" byline — implies a review cadence that doesn't exist.
- 2026-09-30 · Second consent tool alongside Raptive's CMP — consent conflicts, duplicate consoles.
- 2026-10 · Our own calorie / protein / sleep / exercise targets — hedges data integrity; official guidelines only.
- 2026-10-07 · ACE body-fat tiers and age/sex-specific "healthy BMI ranges" — not supported by CDC/WHO cut-offs.
- 2026-10-11 · Visible "Reviewed <date>" / "Updated <date>" / "<Month YYYY> • N min read" bylines — implied a review cadence we don't run (D-04/D-12); schema `dateModified` carries the review record.

## §4 Gotchas & hard rules
- Pages are minified onto one line — `grep -c` counts lines, not matches. Use `grep -o PATTERN FILE | wc -l` in gates.
- Editing visible FAQ text can break or desync FAQPage JSON-LD; re-validate with `python3 research/f1/verify.py` after any FAQ change.
- The jsdom test scripts under `research/` need Node + jsdom; the box has Node 20 but no jsdom (install step missing by design) — they ship for reference and run on Marko's Mac. Treat skipped jsdom runs as unverified.
- Content batches ride in `research/<batch>/`; only their `apply_build.py` writes files. Never edit a batch-managed file by hand mid-flow — the hash-guarded replacements will refuse the next run.
- The box has no browser — layout, hover and viewport-specific behaviour are `unverified` until Marko confirms with Chrome DevTools on Mac 2 (or impeccable detect with --viewport).
- `scripts/check_structure.py` enforces balanced tags through `scripts/check_markup.py` since CMB-003 — a batch whose patch drops a closing tag fails the 40/40 gate. Use `scripts/check_markup.py --text FILE` before vs after to prove which text a batch changed.
- Balanced tags can still be nested wrong. Since CMB-004 `scripts/check_markup.py` adds three structure checks — `block-in-heading`, `outside-container`, `content-in-calculator` — all run from the 40/40 gate.
- Markup and layout changes need a render check; the box has no browser, so chat renders a pushed branch. Patch whole elements, never text that runs across tag boundaries — that is how the 21 CMB-003 pages broke.
- One click binding per FAQ accordion and per mobile-menu toggle. Two bindings cancel out (one tap opens and closes) — the CMB-005 regression on 13 pages. Since CMB-005 `scripts/check_structure.py` fails any page whose FAQ or menu toggle has a click-binding count ≠ 1.
- FAQPage JSON-LD answers must equal the visible answers on the same page. `scripts/check_structure.py` enforces this since CMB-005; keep the schema in step whenever FAQ text is rewritten.
- `assets/js/calculator.js` rounds BMI once via `round1()` — categories, what-if tables and BMI Prime all come from the shown value. Healthy limits are whole units whose rounded BMI falls inside 18.5–24.9 (`weightBounds()`), the rule the BMI charts use. A page table that gives kg for an inch height labels the cm with one decimal (5'10" = 177.8 cm).
- `sitemap.xml` `lastmod` moves with any significant change (visible content, structured data, links). Schema `dateModified` moves only when visible content changes.
- Pilot branches never carry DEVLOG changes — DEVLOG commits go to `main`, so a later merge back from a pilot can't conflict on `DEVLOG.md`.

## §5 Backlog (priority order)
- [P1] G2 claim-by-claim rewrites of 15 older guides: `bmi-and-health-risks`, `bmi-and-metabolism`, `bmi-limitations`, `bmi-tracking-guide`, `bmi-chart-explained`, `bmi-chart-men`, `bmi-chart-women`, `bmi-formula`, `bmi-history`, `healthy-bmi-range`, `how-to-lower-bmi`, `body-fat-vs-bmi`, `underweight-bmi-risks`, `waist-to-height-ratio`, `bmi-by-age`.
- [P1] After [P1] guides: owner push → final IndexNow / Search Console / Bing submission round (D-07).
- [P1] `/women-bmi-calculator/` and `/new-bmi-calculator/` lost their **Key Takeaways** box, **Medical Disclaimer** and the "X lbs above/below the healthy range" line (the weight-diff element) in `a83d1f7` on 2026-09-27 — restore them.
- [P1] Review text CMB-004 made visible again (unseen since `a83d1f7`): `/new-bmi-calculator/` (whole article; its FAQ reads "see's analysis of BMI usefulness") and `/blog/bmi-limitations/` (a "Muscle Density / Fat Density" chart with no bars, a metabolic-health chart with clipped labels, "and other institutions has identified…" with its subject missing, a bare "Source: World Health Organization" line).
- [P1] Calculator inputs on the other calculator pages have no programmatic `for`/`id` — apply the men-page pattern.
- [P2] Anti-slop pass over every page rewritten in chat before the anti-slop-prose skill was installed. Men-page review (CMB-003 STEP 2) = **31 tells over ~3,100 words** — see `audit/cmb-003/anti-slop-men.md`.
- [P1] D-12 date removal across the 22 content pages: strip "Reviewed <date>", "Updated <date>" and "<Month YYYY> • N min read" from bylines and article meta; schema `dateModified` stays; data-provenance dates stay. Pending owner call on whether `/privacy/` and `/terms/` keep their "Last updated" line (chat recommends keeping it).
- [P1] BMI chart pages — kg columns cross the neighbouring category: `/blog/bmi-chart-men/` 46/102 cells, `/blog/bmi-chart-women/` 45/90 cells, `/bmi-chart/` 60/126 inch-table cells plus the metric table. Their "Every listed weight is guaranteed to be inside its category" line is false for kg, and the cm labels are rounded. Fix: regenerate with the `weightBounds` rule (whole kg inside each band) and cm to one decimal. CMB-007 candidate.
- [P1] D-11 sweep in older guides (ride with G2 rewrites): `/blog/healthy-bmi-range/` ("optimal range 19–24 for women", "20–25" men, "why the range differs", unsourced pregnancy/testosterone/heart-risk claims, chart of healthy band "widening to" 23–33 after 64); `/blog/bmi-chart-explained/` FAQ "Are BMI charts different for men and women?" ("some providers recommend sex-specific interpretations"); `/blog/bmi-and-metabolism/` (says the BMI-by-age guide gives "age-specific recommendations"); `/blog/underweight-bmi-risks/` (says the ideal-weight calculator uses age — it uses height, sex and frame); `/about/` women card ("female-specific interpretation").
- [P2] `(teaser)` leaks into an H2 on `/men-bmi-calculator/` and `/women-bmi-calculator/` ("Healthy weight range for men (teaser)").
- [P2] On `/men-bmi-calculator/`: the "BMI Calculator by Age" and "BMI by age guide" links both point to `/age-bmi-calculator/`; the "Body Fat Percentage vs BMI for Men" section lost its heading.
- [P2] `/blog/bmi-and-metabolism/`: `theoverview` is glued together; info cards carry a heading with no body (e.g. "Reduced BMR").
- [P2] `/lean-body-mass/`: the "Methods to Measure Body Composition" section lost its heading; the composition figure has two captions. `/women-bmi-calculator/`: the "Rows 18–64 … Row 65+" note describes a removed table. `/blog/bmi-categories/`: the category range chart sizes its zones with BMI values as flex weights (the same bug the scale had). `/blog/bmi-history/` references: "WHO: Obesity and Overweight Fact Sheet" has no link and ": How useful is BMI?" lost its source name.
- [P2] On 15 pages the `sitemap.xml` `lastmod` and schema `dateModified` disagree; ride with the D-12 batch — move `dateModified` only where visible content actually changed, otherwise sync lastmod to the current state.
- [P2] `/men-bmi-calculator/` cites the WHO 2008 waist–hip ratio report without a link — verify the WHO publication URL and add it. (Pilot carries the same citation.)
- [P3] If the CMB-006 pilot merges to `main`, `assets/images/og/men-waist-nhlbi-scale.png` becomes unreferenced — delete it then.
- [P2] Impeccable design candidates (owner decides, project chat implements in `styles.css` sitewide — never per page): links `#0e7490` (4.9:1) instead of `#0891b2` (3.7:1); flat related-guide / other-calculator lists instead of cards-in-cards; Healthy Min/Max values that don't break mid-unit at 390 px; 12 px scale labels; amber callout headings `#854d0e` instead of `#ca8a04`.
- [P3] Homepage `<title>` is 68 chars (truncated in SERP) — decide after Search Console data lands in the final round.
- [P3] `/blog/bmi-for-athletes/` is still short (~700 words after T1 rebuild) — candidate for a sourced expansion.
- [P3] Registry debt in `research/data-sources.csv` — rows missing for older guides.
- [P3] Impeccable baseline findings on current site (CMB-001 scan, 1,424 anti-patterns + 899 advisory): top 5 rules by count — `low-contrast` 1062, `design-system-color` 449, `design-system-font-size` 352, `nested-cards` 125, `design-system-radius` 76. Address inside the current look (no retheme) per CLAUDE.md R2.

## §6 Log (append-only, newest at bottom)

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

### 2026-10-09 · G2g lbm-rewrite · chat → CC · done (NOT live)
- What: `/lean-body-mass/` — formula comparison table rebuilt from the Boer/James/Hume equations (every printed value was wrong, e.g. Hume 175 cm/75 kg was 59.7 kg, should be 54.4 kg); authorship corrected (Hume 1966); unsourced "most widely cited" / ACE / "most generous" claims removed; FAQ figures replaced.
- Files: `lean-body-mass/`, `research/lbm-rewrite/`, `research/g2/g2_lbm.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; forbidden tokens 0; "54.4 kg" present.
- Commit: 661c24c (pushed: no).

### 2026-10-09 · G2h women-rewrite · chat → CC · done (NOT live)
- What: `/women-bmi-calculator/` — new "US women by the numbers" section (NHANES averages, obesity 41.3%, DXA body fat 38.7%); ACE and unsourced numbers replaced with CDC-scan medians + Gallagher 2000; NIH waist method; sourced FAQ; birth control / fertility FAQs removed.
- Files: `women-bmi-calculator/`, `research/women-rewrite/`, `research/g2/g2_women.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; forbidden tokens 0; "US women by the numbers" present.
- Commit: f0b0bce (pushed: no).

### 2026-10-09 · G2i men-rewrite · chat → CC · done (NOT live)
- What: `/men-bmi-calculator/` — repaired paragraphs whose opening text was swallowed into a broken `style="margin:0;font-size:0.` attribute (shown as half-sentences); sourced claims (NHLBI, Provencher 2018, WHO 2008); new "US men by the numbers" section; unsourced testosterone content removed.
- Files: `men-bmi-calculator/`, `research/men-rewrite/`, `research/g2/g2_men.py`, `sitemap.xml`.
- Verified: check_structure 40/40; verify.py clean; forbidden tokens 0; "US men by the numbers" present.
- Commit: f5e0b93 (pushed: no — HEAD).

### 2026-10-09 · CMB-001 DEVLOG-INIT · chat → CC · done
- What: install devlog + anti-slop-prose + impeccable skills (plus 4 impeccable agents); bootstrap DEVLOG.md from git log + repo state; write CLAUDE.md with DEVLOG / anti-slop / content-batches / impeccable sections; auto-extract DESIGN.md from `assets/css/styles.css` (no interactive workshop; `.impeccable/design.json` sidecar skipped — would need North Star / qualitative inputs); tighten .gitignore (ungate `.claude/`; add 3 granular ignores); tighten .vercelignore (add `/CLAIMS-DECISIONS*.csv`; `.impeccable/`); append supersession line to `research/HANDOFF.md`.
- Files: `DEVLOG.md`, `CLAUDE.md`, `DESIGN.md`, `.gitignore`, `.vercelignore`, `research/HANDOFF.md`, `.claude/skills/{devlog,anti-slop-prose,impeccable}/`, `.claude/agents/impeccable-*.md`.
- Verified:
  - impeccable engine-probe → `impeccable-engine 0.1.12` (aarch64 bin).
  - impeccable detect baseline (whole-site HTML + stylesheet, excluding `.claude`/`.git`/`.vercel`/`research`): **1,424 findings + 899 advisory**. Counts per rule: `low-contrast` 1062, `design-system-color` 449, `design-system-font-size` 352, `nested-cards` 125, `design-system-radius` 76, `side-tab` 75, `dark-glow` 40, `cramped-padding` 31, `undersized-ui-text` 29, `skipped-heading` 28, `border-accent-on-rounded` 20, `tiny-text` 11, `ai-color-palette` 10, `gray-on-color` 7, `icon-tile-stack` 4, `design-system-font` 3, `repeating-stripes-gradient` 1. Top 5 recorded in §5 [P3] as backlog — no fixes applied in this prompt.
  - `node --check assets/js/calculator.js` → OK.
  - check_structure 40/40, verify.py clean (unchanged by this prompt).
  - Layout verification `unverified` — no browser in box; Marko to run `.claude/skills/impeccable/scripts/impeccable detect --viewport 390x844 URL` on Mac 2 against localhost or the production URL.
- Commit: this prompt's commit (pushed: no).
- Notes: `.claude/settings.local.json` NOT committed (local-only). `.claude/skills/impeccable/scripts/bin/` NOT committed (compiled binaries, platform-specific). `.impeccable/config.local.json` absent at commit time but ignored going forward.

### 2026-10-11 · CMB-002 LIVE-SYNC · chat → CC · done
- What: record that owner pushed `7e870be..38c5bfc` to `origin/main` on 2026-10-10. Flips G2g lbm-rewrite (661c24c), G2h women-rewrite (f0b0bce), G2i men-rewrite (f5e0b93) and CMB-001 DEVLOG-INIT (38c5bfc) from `done` to `live` (status change recorded here; past entries left untouched per devlog append-only rule).
- Files: `DEVLOG.md` only.
- Verified (production checks, from chat 2026-10-10):
  - `/lean-body-mass/` — Hume 54.4 kg at 175 cm / 75 kg and the 1966 attribution present.
  - `/men-bmi-calculator/` — "US men by the numbers" section present.
  - `/women-bmi-calculator/` — "US women by the numbers" section + 33.4% + 38.7% present; removed phrases absent.
  - `/DEVLOG.md`, `/.claude/skills/devlog/SKILL.md`, `/CLAIMS-DECISIONS.csv`, `/research/HANDOFF.md` — all return not-found on the production domain (`.vercelignore` is working).
- Commit: 60dae68 (pushed: no).
- Notes: `Mapstor/calculatemybmi` is a **public** GitHub repo (checked 2026-10-10) — the Vercel exclusions keep internal files off the live domain but leave them world-readable on GitHub. Logged as a §0 open question for the owner.

### 2026-10-11 · CMB-003 MARKUP+IMPECCABLE · chat → CC · done (STEPS 0–2) / handed (STEP 3)
- What: STEP 0 kept the impeccable self-update (engine reports 0.1.14, matches working-tree VERSION; HEAD was 0.1.12) and added **R5 — no in-task impeccable self-updates** to CLAUDE.md. STEP 1 wrote `scripts/check_markup.py` (stdlib `html.parser`: orphan ends, implicit closes with p/li/td/th/tr/thead/tbody/option/dt/dd excepted, never-closed, block-under-emph for strong/b/em; `--text` snapshot = visible-text stream + href/src list + SHA-256 of title/metas/JSON-LD). Repaired tag balance on 21 failing pages (110 → 0 issues; delta −160 bytes). Replaced the no-op "HTML parses" block in `scripts/check_structure.py` with the new parser's checks. Fixed the BMI scale in `assets/css/styles.css` — segment widths 18.5/25/16.5/20/20 → 14/26/20/20/20, and label positions 0/14/40/60/80/100 % to match the marker's linear 15-40 scale. STEP 2 wrote `audit/cmb-003/anti-slop-men.md` (review-only). STEP 3 (branch `test/impeccable-men` only): added `assets/css/men.css` (scoped refinements — prose max-width, scale-label 12 px, result wrap, un-nest blog-cards inside sections, soften 4 px side-tabs to 1 px, shift the purple accent to primary cyan, darken brand-cyan link + CTA + amber/red callout text to clear AA 4.5:1), 5 `<label for>` + `<input id>` on the calculator, H1 → H2 skipped-heading fix. Linked `men.css` from the page head.
- Files (main): `CLAUDE.md`, `.claude/skills/impeccable/{SKILL.md, reference/{doctor,init,new-work}.md, scripts/VERSION}`, `scripts/check_markup.py`, `scripts/check_structure.py`, `assets/css/styles.css`, `audit/cmb-003/anti-slop-men.md`, and the 21 repaired pages. Files (branch `test/impeccable-men`): `men-bmi-calculator/index.html`, `assets/css/men.css`, `audit/cmb-003/impeccable-men.md`.
- Verified (main):
  - `scripts/check_markup.py` on all 41 sitemap pages + `404.html`: **0 issues**.
  - `scripts/check_markup.py --text` of every page vs `/tmp/cmb003-before/`: **no diff** — content byte-identical.
  - `python3 scripts/check_structure.py` → **40/40 pages pass** (via the new markup parser).
  - `python3 research/f1/verify.py` → **clean**.
  - Scale labels confirmed byte-identical across the 5 pages that use the scale (`span>15</span>…<span>40</span>`); CSS-only change applies to all.
- Verified (branch): markup 0 issues, --text diff empty, check_structure 40/40, verify.py clean, `git diff --stat main..test/impeccable-men` = only `men-bmi-calculator/index.html`, `assets/css/men.css`, `audit/cmb-003/impeccable-men.md`. Impeccable detect on the men page + men.css: **80 → 68 findings** (−22 real, +10 from darker-shade and `clamp()` steps the detector flags because DESIGN.md doesn't yet list them). `skipped-heading`, `side-tab` and `nested-cards` all materially down.
- Unverified: layout, hover, 390 px wrap, menu behaviour — the box has no browser; needs Marko's preview-deploy renders of `review/cmb-003` + `test/impeccable-men`.
- Commits: 0f30a3a (R5 + impeccable kept), 1e5b04f (markup + check_structure gate), e80ab70 (scale CSS), a12dc96 (anti-slop review), 3c834c1 (men design — on branch `test/impeccable-men`). Pushed: no.
- Notes: STEP 3 adds no detector ignores; R3 exception candidates listed in `audit/cmb-003/impeccable-men.md`. Anti-slop pass counted **31 tells** on `/men-bmi-calculator/` body prose (~3,100 words).

### 2026-10-11 · CMB-004 MARKUP-V2 · chat → CC · done
- What: applied the skills chat's `research/cmb-004-markup/` package — a structure-correct supersession of CMB-003 STEP 1's tag repair. 20 pages rebuilt from their production versions so each missing closing tag goes back where the element's content ends (bold labels, the homepage h2, card and FAQ items, calculator and results boxes); leftover closers of removed wrappers deleted; one emptied section removed on `/lean-body-mass/`; the Sources block on `/blog/bmi-history/` moved inside `.container`. `/men-bmi-calculator/`: the five input `id`s + `<label for>` pattern from the CMB-003 test kept and shipped; the first H3 ("BMI Distribution Among U.S. Adult Men") promoted to H2 (skipped-heading fix). `scripts/check_markup.py` gained three structure checks — `block-in-heading`, `outside-container`, `content-in-calculator`; `check_structure.py` already runs it, so the 40/40 gate enforces them from now on. `.gitignore` gained `__pycache__/`. Closed the CMB-003 test: local `test/impeccable-men` deleted (remote awaits owner's GitHub delete). `assets/css/men.css` never reached main.
- CMB-003 STEP 1 status: **superseded** here (balanced but nested wrong on chat's render — 11 guides' text out of `.container`, the homepage h2 still holding its paragraph and table, four calculator pages' articles still inside the calculator card). CMB-003's scale CSS (STEP 1f) and the anti-slop review stand. **CMB-003 STEP 3 verdict: partial.** Kept and shipped here: the 5 input `for`/`id` labels and the h3→h2 fix. Rejected: `assets/css/men.css` — recoloured whole callout paragraphs brown and red while the low-contrast amber heading stayed, left a purple heading on a box it turned cyan, darkened the CTA off-brand, 65-char measure left ragged cards, styled through inline-style substrings with `!important` so none of it was reusable, and missed the text-against-the-screen-edge bug. Detector on the men page at 390 px (chat renders): live 65, test branch 42, CMB-004 60 (edge 3 → 0, skipped heading 1 → 0).
- Files: `.gitignore`, `scripts/check_markup.py`, `research/cmb-004-markup/` (apply_build.py + manifest + files/* mirrors), and 20 page HTMLs: `/index.html`, `/kids-bmi-calculator/`, `/lean-body-mass/`, `/men-bmi-calculator/`, `/new-bmi-calculator/`, `/women-bmi-calculator/`, `/calculators/`, `/ideal-weight/`, and the 12 `/blog/*` guides.
- Verified (CMB-004 FIX.md gates): dry-run `0 new / 22 replaced / 0 edits / 0 deletions`; `python3 scripts/check_structure.py` → **40/40**; `python3 research/f1/verify.py` → clean; `scripts/check_markup.py` on all 41 sitemap pages + `404.html` → **0 issues each**; `--text` of each of the 20 changed pages vs `origin/main`: **0 diffs**; negative test on `origin/main:index.html` → exits 1 and lists `block-in-heading`, `block-under-emph`, `implicit-close`.
- Verified (layout, from chat's Chromium renders at 390 and 1280 px): bold-bleed paragraphs 393 → 43 (intended bold only); text touching the screen edge 602 → 0; hidden article text 132 → 2 (both intended — the New BMI results heading before Calculate, and a method note in an inactive panel); sections inside calculators 35 → 0; headings holding block content 1 → 0; pages with sideways scroll 1 → 0.
- Commits: 7c22067 (markup v2 + men labels + structure gate). Pushed: no (owner pushes `main` next).
- Notes: `scripts/__pycache__/` added to `.gitignore` because `check_structure.py` now imports `check_markup.py`.

### 2026-10-11 · CMB-005 LIVE-FIX · chat → CC · done
- What: applied `research/cmb-005-live-fix/` — one FAQ click binding per page (removed `setupFAQ()` from `calculator.js` init plus the duplicate inline toggles / `onclick` attributes on 13 pages so one tap opens the answer); FAQPage JSON-LD rewritten on 8 pages (30 answers) to equal the visible answers; BMI rounded once via `round1()` so categories, what-if tables and BMI Prime come from the shown value; `weightBounds()` gives whole-unit healthy limits whose rounded BMI is 18.5–24.9 (metric users get whole-kg limits; "above/below" is measured to those limits); milestones table trimmed to CDC thresholds only; dead sex-specific "ideal" bands removed; `bmiPrime()` capped at 0.99 below BMI 25; waist note shifted to "mainly at BMI 25–34.9"; age 65+ tile now shows the real middle dot and "Adult BMI range" (was literal `&middot;` and "Your range"). D-11 claim scrub on `/men-bmi-calculator/`, `/women-bmi-calculator/`, `/age-bmi-calculator/`, `/new-bmi-calculator/`, `/terms/`, `/blog/bmi-chart-explained/` (meta/og/twitter/WebApplication descriptions). Teaser tables: 6'2" men 65→66 kg lower bound, 5'2" women 62→61 kg upper bound, cm labels to one decimal. `/calculators/` stats: 8→9 free calculators, age range 2–100, and info-card grid stacks below 480 px (no 390 px overflow). `scripts/check_structure.py` 40/40 gate now fails any page whose FAQ accordion or mobile-menu toggle has click-binding count ≠ 1 and any FAQPage JSON-LD answer that doesn't equal the visible answer. `/terms/` carries "Last Updated: October 11, 2026"; `dateModified` 2026-10-11 on `/terms/`, `/blog/bmi-chart-explained/`, `/calculators/`.
- Files: `assets/js/calculator.js`; `scripts/check_structure.py`; `sitemap.xml`; `terms/index.html`; `men-bmi-calculator/`, `women-bmi-calculator/`, `age-bmi-calculator/`, `new-bmi-calculator/`, `calculators/`, `ideal-weight/` (6 calculator-area pages); 8 `/blog/*/` pages (`bmi-and-health-risks`, `bmi-and-metabolism`, `bmi-chart-explained`, `bmi-history`, `bmi-limitations`, `how-to-lower-bmi`, `underweight-bmi-risks`, `waist-to-height-ratio`); `research/calculator-checks/calc_test_jsdom.js` (updated), `calc_e2e_playwright.py` + `faq_probe_playwright.py` (new reference tests, need Playwright + Chromium — not run in box); `research/cmb-005-live-fix/` (FIX.md + apply_build.py + manifest + files/* mirrors).
- Verified (CMB-005 FIX.md gates): dry-run `2 new / 19 replaced / 0 edits / 0 deletions`; `python3 scripts/check_structure.py` → **40/40**; `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`; `node --check assets/js/calculator.js` → exit 0; `research/us-obesity-build/tools/number_audit.py` → `not allowed: none`; `schema check: missing BreadcrumbList: none | WebApplication without author: none`; `setupFAQ();` count 0; forbidden claim-phrases count 0; inline `onclick="this.parentElement` count 0; `scripts/check_markup.py` clean on the 7 updated calculator-area pages; `"Last Updated: October 11, 2026"` in `/terms/` = 1; `"dateModified": "2026-10-11"` across `/terms/`, `/blog/bmi-chart-explained/`, `/calculators/` = 3; `"&middot; 23 - 33"` in calculator.js = 0; `>9</div> <div class="stat-label">Free Calculators` in `/calculators/` = 1; 480 px media query present in `/calculators/`.
- Verified (chat, Chromium 1194 + jsdom 24): 1,140 calculator checks pass with 0 failures; jsdom 77/77 (main fails 24); all 25 FAQ pages open the first answer on one tap; menu opens and closes on 41/41 pages; no page is wider than the screen at 360/390/1280 px (123 page loads); FAQPage JSON-LD answers equal visible answers on all 20 pages that have them. On `main@e6d94fd` the new structure checks score 23/40. Also fixes an independent fact-check's BMI Prime and waist-note findings.
- Unverified: jsdom not in box (DEVLOG §4) — recorded as skipped; chat ran it 77/77. Layout changes outside the box's reach stay `unverified` until the production push lets a browser render them.
- Commit: 2e2ca23 (pushed: no — owner pushes `main` next).
- Notes: Resolves the FAQ click-binding regression and the BMI-rounding/healthy-limit inconsistency. Fixes an independent fact-check's BMI Prime and waist-note findings. Hands CMB-006 PILOT-MEN onto branch `pilot/men-skills` (handed 2026-10-11) — runs after the production push lands.

### 2026-10-11 · CMB-006 PILOT-MEN · chat → CC · done (on branch)
- What: applied `research/cmb-006-pilot-men/` to the new branch `pilot/men-skills` — `/men-bmi-calculator/` rebuilt with the content-page / seo-visibility / anti-slop / impeccable skills. Tool first; a new "Compared with US men" rank in the results block from a built NHANES 2021–2023 BMI percentile wedge (2,680 adult men; method reproduces NCHS Series 3 medians and 95th percentiles). Contents chips, a worked example explaining every output, percentile / by-height / body-fat tables, a waist section with a new SVG, an 8-question FAQ with JSON-LD in sync, one sources-and-method block and one flat related block. `assets/css/styles.css` gains a global `--link: #0e7490` token (text links; footer links stay light) and opt-in classes `main.reading`, `.flow`, `.stat-callout`, `.toc-inline`, `.faq-list.flat`, `.related-cols`, `.rank-box`, `.figure`, `.result-item-alt`. `assets/js/calculator.js`: healthy min/max tiles put the converted unit on its own line (shared across every adult calculator; no mid-unit wrap at 390 px). `DESIGN.md` records the `--link` colour; `research/data-sources.csv` and `research/page-map.csv` record the NHANES row and the men-page row. New: `assets/images/og/men-bmi-us-rank.png`, `research/men-pilot/` (generator, stats script + JSON output, CSS source, OG renderer, Playwright reference test, slop scanner, SPEC.md with the scorecard and rollout notes). `main` carries only this DEVLOG entry — the branch stays off `main` until the owner's preview call.
- Files (branch `pilot/men-skills`): `men-bmi-calculator/index.html`, `assets/css/styles.css`, `assets/js/calculator.js`, `DESIGN.md`, `research/data-sources.csv`, `research/page-map.csv`, `assets/images/og/men-bmi-us-rank.png`, `research/men-pilot/` (SPEC.md + 7 files), `research/cmb-006-pilot-men/` (FIX.md + apply_build.py + manifest + files/* mirrors). Files (main): `DEVLOG.md` only.
- Verified (CMB-006 FIX.md gates, on branch): dry-run `10 new / 6 replaced / 0 edits / 0 deletions`; `python3 scripts/check_structure.py` → **40/40**; `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`; `node --check assets/js/calculator.js` → exit 0; `research/us-obesity-build/tools/number_audit.py` → `not allowed: none`; `schema check: missing BreadcrumbList: none | WebApplication without author: none`; `scripts/check_markup.py men-bmi-calculator/index.html` → **0 issues**; `id="men-rank"` count = 1 and `(teaser)|whatever the BMI|men-specific` count = 0; `--link: #0e7490` in `styles.css` = 1 and `result-item-alt` in `calculator.js` = 4; `research/men-pilot/slop_scan.py men-bmi-calculator/index.html` → `words 2471, tells 0, per 1000 words 0.0`.
- Verified (chat, Chromium 1194 + jsdom 24 + impeccable engine 0.1.14): impeccable detect on the men page 57+3 advisory → **2+0** at 390×844 and 76+3 → **2+0** at 1280×800 (the 2 left are the brand CTA gradient — owner decision). Anti-slop tells 31 → 0. Calculate button bottom edge moved from 906 → 816 px (above the fold at 390×844). No sideways scroll at 360, 390 or 1280 px. 1,140 Chromium calculator checks pass, 8/8 rank cases pass, jsdom 77/77. Independent fact-check: 149 numbers all traceable, FAQ JSON-LD in sync with the visible page, 44/44 links resolve.
- Unverified: layout stays `unverified` (R4) — the box has no browser; needs the owner's Vercel preview of `/men-bmi-calculator/` on `pilot/men-skills` + `impeccable detect --viewport 390x844 <preview-url>`. Chromium / jsdom tests not in box — recorded as skipped; chat ran them.
- Commits: 824bf57 on `pilot/men-skills` (pilot build); this DEVLOG commit on `main`. Pushed: no.
- Notes: Pilot pattern — not a sitewide rollout. Three owner decisions carried in §0 waiting on owner: (a) adopt `--link #0e7490` sitewide; (b) keep the brand CTA gradient with an R3 impeccable-ignore or darken it; (c) adopt the flat-FAQ + flat-related + 680 px reading-column pattern across the other calculator pages. The pilot incidentally resolves on-branch the `/men-bmi-calculator/` entries in §5 (teaser-in-H2, Age Guide link, missing "Body Fat Percentage vs BMI for Men" heading) and the men-page [P1] inputs-with-`for`/`id` is already in place from CMB-004; these backlog items describe `main`'s state until a merge happens.

## §7 History & archive
- 2026-02 · Initial commit of BMI calculator site; GA4 + webmaster verification added (78f9434, 92b3baa).
- 2026-08 · raptive-remediation phases 1–17: truth + sources, citation triage, cluster consolidation, author identity, privacy + consent, SEO surface, plumbing, brand/mobile, author credential, author entity corroboration, direct GA4 with consent gate, voice fix, obesity figure correction, bespoke visuals, mobile nav + FAQ toggle, functional audit, OG imagery + quality audit, citation integrity, whitespace + sourcing repair, visible review dates removed, pre-deploy audit (32fc6d6 → 688001a).
- 2026-08-31 … 2026-09-25 · ads.txt + Raptive install + CMP switch + no-ads removal (f8293a2, 41096d9, 0e85c8b, dca1467).
- 2026-09-26 … 2026-09-28 · P0 recovery (restore chart pages, residue + accuracy, tool-first); P1 CDC LMS kids calculator + overflow fixes; shared nav on 7 legacy pages; `/bmi-chart/` added + de-cannibalize; P2 claim-level pass on 15 core pages + guides (JSON-LD, verified history, WHtR sources) (7866479, e30ddf0, 28e031a, 38d3cdd, 47c44f6, 8b68674, a83d1f7, ae2ff9b).
- 2026-09-30 … 2026-10-01 · Exact-list cleanup of 35 unsourced tables/columns; last unsourced accuracy figures and prescriptive column removed; `/us-obesity-statistics/` built with CSV and embeddable chart (NHANES 1960-2023) and nav/inbound links; stale PRE-DEPLOY-REPORT.md removed; Raptive-only consent setup (consent script, GA loader `gtag`, Cookie Settings text removed, privacy/terms updated); fabricated quote + link-stripping fix + FAQ schema parity (3a99491, 1826fe2, 1f16af7, 07bbd93, 3d2b73e, e61c9e0, 661d60c).
- 2026-10-01 … 2026-10-02 · C2b (1-4): rounds of unsourced-number removals with verified primary sources (metabolism, sarcopenia, sleep, 5-10%, body-fat ranges, athletes chart, 1998 history, WHO, frame size, NFL study, muscle-vs-fat kcal, empty FAQs, prescriptive targets attributed to official guidelines) (121c65c, 8d61f91, 89a8491, c952de3).
- 2026-10-02 · F1 final check (empty section headings, long-word wrap on phones, sitemap lastmod batch) (1a85c58).
- 2026-10-02 … 2026-10-09 · See §6: data/tool page builds and G2 content rewrites.
