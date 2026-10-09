# DEVLOG — calculatemybmi.net
> Handoff file. Read §0–§5 and the last 10 entries of §6 before any work. Rules: devlog skill (.claude/skills/devlog/SKILL.md).

## §0 Resume here
_last update: 2026-10-09 · CMB-001_
- Phase: content rewrites — G2 pass of older guides
- Last confirmed: CMB-001 DEVLOG-INIT — handoff log + devlog/impeccable/anti-slop setup — done (this commit)
- In flight (handed, NOT confirmed): none
- Next action: CMB-002 — start G2 claim-by-claim rewrites of the 15 older guides (list in §5 [P1])
- Waiting on owner: push origin/main → HEAD (3 commits ahead: 661c24c, f0b0bce, f5e0b93); eventually IndexNow / Search Console / Bing final round
- Open questions:
  - Rebuilt data/tool pages built 2026-10-02…10-08 show "Reviewed <date>" or "Updated <date>" in the byline, conflicting with D-04 (no visible review date) — keep "Updated", or remove both?

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

## §3 Rejected — don't re-propose
- 2026-08-02 · Medical / treatment / surgery content — YMYL rejection risk.
- 2026-08 · Tag Manager (GTM) alongside direct gtag — Raptive overhead with no site benefit.
- 2026-08-15 · Visible "Last reviewed <date>" byline — implies a review cadence that doesn't exist.
- 2026-09-30 · Second consent tool alongside Raptive's CMP — consent conflicts, duplicate consoles.
- 2026-10 · Our own calorie / protein / sleep / exercise targets — hedges data integrity; official guidelines only.
- 2026-10-07 · ACE body-fat tiers and age/sex-specific "healthy BMI ranges" — not supported by CDC/WHO cut-offs.

## §4 Gotchas & hard rules
- Pages are minified onto one line — `grep -c` counts lines, not matches. Use `grep -o PATTERN FILE | wc -l` in gates.
- Editing visible FAQ text can break or desync FAQPage JSON-LD; re-validate with `python3 research/f1/verify.py` after any FAQ change.
- The jsdom test scripts under `research/` need Node + jsdom; the box has Node 20 but no jsdom (install step missing by design) — they ship for reference and run on Marko's Mac. Treat skipped jsdom runs as unverified.
- Content batches ride in `research/<batch>/`; only their `apply_build.py` writes files. Never edit a batch-managed file by hand mid-flow — the hash-guarded replacements will refuse the next run.
- The box has no browser — layout, hover and viewport-specific behaviour are `unverified` until Marko confirms with Chrome DevTools on Mac 2 (or impeccable detect with --viewport).

## §5 Backlog (priority order)
- [P1] G2 claim-by-claim rewrites of 15 older guides: `bmi-and-health-risks`, `bmi-and-metabolism`, `bmi-limitations`, `bmi-tracking-guide`, `bmi-chart-explained`, `bmi-chart-men`, `bmi-chart-women`, `bmi-formula`, `bmi-history`, `healthy-bmi-range`, `how-to-lower-bmi`, `body-fat-vs-bmi`, `underweight-bmi-risks`, `waist-to-height-ratio`, `bmi-by-age`.
- [P1] After [P1] guides: owner push → final IndexNow / Search Console / Bing submission round (D-07).
- [P2] Anti-slop pass over every page rewritten in chat before the anti-slop-prose skill was installed.
- [P2] Resolve §0 open question on "Reviewed/Updated" byline (D-04) sitewide.
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

## §7 History & archive
- 2026-02 · Initial commit of BMI calculator site; GA4 + webmaster verification added (78f9434, 92b3baa).
- 2026-08 · raptive-remediation phases 1–17: truth + sources, citation triage, cluster consolidation, author identity, privacy + consent, SEO surface, plumbing, brand/mobile, author credential, author entity corroboration, direct GA4 with consent gate, voice fix, obesity figure correction, bespoke visuals, mobile nav + FAQ toggle, functional audit, OG imagery + quality audit, citation integrity, whitespace + sourcing repair, visible review dates removed, pre-deploy audit (32fc6d6 → 688001a).
- 2026-08-31 … 2026-09-25 · ads.txt + Raptive install + CMP switch + no-ads removal (f8293a2, 41096d9, 0e85c8b, dca1467).
- 2026-09-26 … 2026-09-28 · P0 recovery (restore chart pages, residue + accuracy, tool-first); P1 CDC LMS kids calculator + overflow fixes; shared nav on 7 legacy pages; `/bmi-chart/` added + de-cannibalize; P2 claim-level pass on 15 core pages + guides (JSON-LD, verified history, WHtR sources) (7866479, e30ddf0, 28e031a, 38d3cdd, 47c44f6, 8b68674, a83d1f7, ae2ff9b).
- 2026-09-30 … 2026-10-01 · Exact-list cleanup of 35 unsourced tables/columns; last unsourced accuracy figures and prescriptive column removed; `/us-obesity-statistics/` built with CSV and embeddable chart (NHANES 1960-2023) and nav/inbound links; stale PRE-DEPLOY-REPORT.md removed; Raptive-only consent setup (consent script, GA loader `gtag`, Cookie Settings text removed, privacy/terms updated); fabricated quote + link-stripping fix + FAQ schema parity (3a99491, 1826fe2, 1f16af7, 07bbd93, 3d2b73e, e61c9e0, 661d60c).
- 2026-10-01 … 2026-10-02 · C2b (1-4): rounds of unsourced-number removals with verified primary sources (metabolism, sarcopenia, sleep, 5-10%, body-fat ranges, athletes chart, 1998 history, WHO, frame size, NFL study, muscle-vs-fat kcal, empty FAQs, prescriptive targets attributed to official guidelines) (121c65c, 8d61f91, 89a8491, c952de3).
- 2026-10-02 · F1 final check (empty section headings, long-word wrap on phones, sitemap lastmod batch) (1a85c58).
- 2026-10-02 … 2026-10-09 · See §6: data/tool page builds and G2 content rewrites.
