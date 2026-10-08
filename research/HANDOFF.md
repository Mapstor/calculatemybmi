# calculatemybmi.net — HANDOFF (updated 1 Oct 2026)

Paste this into a new chat to continue. Lives in the repo at research/HANDOFF.md.

## Setup
- Live host: https://calculatemybmi.net/ (non-www canonical; www 308s to it). Static HTML on Vercel; repo Mapstor/calculatemybmi; push to main deploys production.
- Claude Code box: Mac 2, port 3013, repo at /workspace, no network inside the box.
- Raptive ads live on every page; ads.txt is a 301 in vercel.json.
- Consent: Raptive's CMP only (decision 1 Oct 2026). Every <head> carries Raptive's "Standard GA delay script" verbatim (help.raptive.com article 47199949578651); /assets/js/consent-banner.js loads GA4 and defines gtag itself. No other consent tool and no footer "Cookie settings" link.
- IndexNow: bash scripts/indexnow.sh (no args = every sitemap URL; --dry-run available). Key file at the site root.
- Gate: python3 scripts/check_structure.py must pass 34/34 before every commit.
- Fix workflow: chat prepares a package (FIX.md + apply_fixes.py + edits.json + verify.py) of exact old->new edits with expected counts; Claude Code applies it, runs the gates and commits; Marko pushes. Packages stay under research/<batch>/ (excluded from deploy).

## Goal and reality
- Goal: 10,000 visitors/month from Google.
- Google (www property, Feb-Sep 2026): 29 clicks, 22,800 impressions. The site is indexed on the non-www host (site: search, 30 Sep): the problem is ranking, not indexing. Non-www GSC property added 28 Sep.
- Bing: 10,872 clicks Mar-Sep; crashed after the August 308s of the chart pages (restored 26 Sep); recovering (~25-30 clicks/day at 30 Sep).

## Shipped
- Aug-Sep: 7866479 P0 (chart pages restored), e30ddf0 P1 (kids calculator, CDC LMS), a83d1f7 / ae2ff9b claim passes, 8b68674 /bmi-chart/, 28e031a shared nav, 38d3cdd, 47c44f6, 3a99491, 1826fe2 cleanup.
- 30 Sep: 1f16af7 /us-obesity-statistics/ (NHANES 1960-2023, CSV, embeddable chart, Dataset schema). 07bbd93 render fixes, nav (desktop BMI Chart, mobile Obesity Statistics, Guides no longer active everywhere), 9 inbound links, stale prevalence figures updated to 2021-2023. 3d2b73e PRE-DEPLOY-REPORT.md removed.
- 1 Oct: e61c9e0 Raptive-only consent + rebuilt the truncated reference lists (women, new-bmi). 661d60c C2a: fabricated quote removed, sentences broken by the old link stripping repaired, ACE remnants, dead TOC links, FAQ schema parity. 121c65c C2b-1 and 8d61f91 C2b-2: unsourced numbers removed or sourced (metabolism, sarcopenia, sleep, 1998 history, body-fat ranges, men/women claims, lean FAQs). C2b-3 (see git log): last unsourced numbers sourced or removed (WHO child figures, frame-size convention, sarcopenia, athletes NFL study), first prescriptive targets removed, this handoff rewritten.

## Standards (non-negotiable)
- Verified-or-omitted: every number or specific claim cites a primary (R1) source or is removed.
- Nothing prescriptive: no calorie, protein, sleep or exercise targets of our own. Official guidelines may be quoted only when attributed and linked (Physical Activity Guidelines for Americans; AASM/SRS sleep recommendation via CDC) — decision 1 Oct 2026 (option B).
- Never cite: Harvard (any), Mayo Clinic, Cleveland Clinic, NHS, American Heart Association / heart.org, ACE, ACSM, NSCA, Wikipedia (an entity sameAs in schema is fine).
- No quotes attributed to named people unless the source is verified and linked.
- Structured data must match visible content (every FAQPage question visible on the page).
- BMI bands: lb x 703 / in^2 (or kg / m^2), rounded to 0.1 half-up, then CDC ranges. Tests: 5'9" -> <=124 / 125-168 / 169-202 / 203-236 / 237-270 / >=271; 170 cm healthy 54-72 kg.
- Before any redirect or deletion: pull that URL's GSC and Bing clicks first.
- After each batch: gate 34/34; periodically git archive -> chat render check (360 px + desktop).
- Give Claude Code exact-edit packages, never judgment rules.
- Portfolio: never republish this site's pages, datasets or shared prose on other health sites; embed/licence links use the brand anchor only, nofollow allowed.

## Verified sources (R1) — details in research/data-sources.csv
- CDC/NCHS: Adult BMI categories; Child & Teen BMI categories; extended BMI-for-age method; Data Brief 508; Health E-Stats 111 (trend series verified), 112, 119; Vital and Health Statistics Series 3 No. 50; NHANES population totals.
- Studies and reports: Winter 2014 (PMID 24452240); Keys 1972; Quetelet 1832/1842; Ashwell 2012; Browning 2010; WHO TRS 854; WHO expert consultation, Lancet 2004 (PMID 14726171); NHLBI 1998 Clinical Guidelines (NBK2003, NBK2005); Wing et al., Diabetes Care 2011 (PMC3120182); Pontzer et al., Science 2021 (PMID 34385400); Hirode & Wong, JAMA 2020 (PMC7312413); Alberti et al., Circulation 2009 (PMID 19805654); Volpi et al. 2004 (PMC2804956); Cappuccio et al., Sleep 2008 (PMID 18517032); Caspersen et al. 1985 (PMC1424733); Gallagher et al., AJCN 2000 (PMID 10966886); Pai & Paloucek 2000 (PMID 10981254); Provencher et al., J Strength Cond Res 2018 (doi 10.1519/JSC.0000000000002449); WHO obesity and overweight fact sheet; Gallup 28 Oct 2025 (self-reported; its 2026 update excluded).

## Research files (repo research/)
keyword-ledger.csv, page-map.csv, data-sources.csv (created 30 Sep; older pages still lack registry rows), sitemap.md, us-obesity-build/ and one folder per fix batch.

## Next
1. Done in C2b-4 (see git log): remaining calorie, protein, sleep and exercise targets removed or replaced by attributed official guidelines (Physical Activity Guidelines for Americans; AASM/SRS via CDC); 6-vs-2 kcal now Wang et al. AJCN 2010 (PMC2980962); FAQ items with empty visible answers removed sitewide (visible + JSON-LD); lean-body-mass how-to rewritten.
2. Final check done 2 Oct 2026 on the live commit (batch F1): empty section headings removed, long words wrap on phones, sitemap lastmod updated for content-changed pages. Then one IndexNow run (all URLs).
3. Built 2 Oct 2026: /obesity-rate-by-state/ — CDC BRFSS 2011-2025 state tables + 2025 by age (verified: 2025 PDF = CDC CSV 54/54; CDC band counts reproduced). Hub only: per-state demand 4,680/mo over 38 states (8 >= 150/mo), so no per-state pages (doorway risk); state rows are anchored on the hub. Refresh when CDC publishes 2026 maps (~Sep 2027). Redesigned the same day (batch S2): real US choropleth from US Census Bureau boundaries (us-atlas, simplified, Albers USA), play button + year slider, hover tooltips, and a state panel comparing each state with the median state, the extremes, its land neighbours (from shared borders), the previous year (95% CI overlap) and 2011, plus trend with CI band and 2025 age bars. Generator: research/state-obesity/gen_page2.py + viz2.py.
4. Built 2 Oct 2026: /childhood-obesity-statistics/ — NCHS Health E-Stat 112 Tables 1-3 (1963-2023, by age, sex, race with CDC reliability flags; flagged cells not shown), Health E-Stat 119 underweight, NHANES population totals for counts; interactive trend chart with series chips, 100-kid pictogram, age/sex bars. State-level child data (NSCH) not verified -> disclosed gap. Inbound links: /us-obesity-statistics/ childhood section, /kids-bmi-calculator/.
5. Built 4 Oct 2026: /body-fat-percentage-chart/ — our calculation from NHANES 2011-2018 whole-body DXA (DXX_G-J + DEMO + BMX, pooled weights /4, pregnant excluded), verified by reproducing Liu et al. BMJ 2021 Table 3 (32.6/33.1/32.9/33.0%, identical n=10,864). Rank tool (sex, age 8-79, body fat %), percentile chart + tables, X%-rank tables, Gallagher 2000 provisional ranges (as tabulated in PMC5349253), body fat by BMI category. No scan data 60+ (disclosed). Body fat calculator built 4 Oct 2026 (batch B2): Navy/Army tape equations (Army Table B-5 sample calcs via NCT02734238; exact values 47.3%/38.6% round to the Army's 47%/39%), Jackson-Pollock 3-site + Siri (published density 1.0597633 reproduced), Deurenberg 1991 BMI formula (SEE 4.1); results placed on the DXA percentiles + Gallagher ranges. Calculators hub card, comparison-table row, counts (now 9) and header nav entry (all pages) added 7 Oct 2026 (batch N1). /blog/how-to-measure-body-fat/ built 7 Oct 2026 (batch G1): methods scored against DXA from Burns et al. PLOS ONE 2019 (n=437; HW 1.0, skinfolds 1.4, ADP 1.6, 4-electrode BIA 1.6, hand-held BIA 4.9 points; +-2.7-point equivalence), Deurenberg SEE 4.1, DoD tape LoA > +-3.5 (conference abstract). Body-fat cluster complete. /blog/what-is-bmi/ rebuilt 7 Oct 2026 (batch W1): sourced hub explainer (CDC, NHLBI, WHO 2004, NCHS, Volpi, Deurenberg, our DXA data) + live BMI explorer; it had no sources before.
6. Built 3 Oct 2026: /average-weight/ — our weighted calculation from NHANES Aug 2021-Aug 2023 DEMO_L + BMX_L (adults 20+, non-pregnant, MEC weights, Taylor-linearised SEs, cells n<30 suppressed), verified by reproducing NCHS Series 3 No. 50 (199.0 / 171.8 lb, 68.9 / 63.5 in, BMI 29.4 / 30.0). Height tables with row anchors, age table, comparison tool (percentile within +-1 inch), healthy range per height (site rule). Still open from this item: army/navy calculators, growth-chart calculator, FFMI. Redesigned 4 Oct 2026 (batch A2): new form (pill toggles, height slider with big readout and steppers, unit-suffixed weight, age select), rich result (tiles incl. height rank, smoothed weight distribution with collision-free labels, side-by-side bars, BMI gauge, notes), page chart split into women/men small multiples. Generator: research/average-weight/gen_avgw2.py.
7. Possible /obesity-rate-by-country/ (WHO GHO is the candidate source; verify first).

## Open items
- Bing Webmaster: add https://calculatemybmi.net/ (import from GSC) and submit its sitemap.
- GSC non-www: Performance + Pages exports once data appears.
- /blog/bmi-for-athletes/ is still short (~700 words): candidate for a sourced expansion.
- Registry debt: data-sources.csv rows for the older pages.
- SERP checks queued: body-fat chart one page vs women/men split; average weight split; "bmi for women" chart vs calculator intent.
