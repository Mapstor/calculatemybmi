# calculatemybmi.net — HANDOFF (30 Sep 2026)

Paste this into a new chat to continue. Keep it in the repo at research/HANDOFF.md.

## Setup
- Live host: https://calculatemybmi.net/ (non-www canonical; www 308s to it since Aug 1). Static HTML on Vercel, Git repo Mapstor/calculatemybmi — push to main deploys production.
- Claude Code box: Mac 2, port 3013, repo mounted at /workspace, no network inside the box.
- Raptive ads live (script on all 33 pages; ads.txt is a 301 redirect in vercel.json).
- IndexNow: scripts/indexnow.sh (bash-3.2 safe; no args = all sitemap URLs). Key file at the site root.
- Gate: scripts/check_structure.py must pass 33/33 before every commit (structure + banned-source content gate).

## Goal and reality
- Goal: 10,000 visitors/month from Google.
- Google so far: www property, Feb 11 – Sep 2026 — 29 clicks, 22,800 impressions lifetime (peak April 8,679; then down). Only real visibility: /blog/body-fat-vs-bmi/ cited in AI features for body-fat queries (position ~1, zero clicks). Non-www property added Sep 28 — no data yet. Google site: search (Sep 30) shows about 3 pages of results, all on the non-www host: the site IS indexed; the problem is ranking, not indexing.
- Bing: 10,872 clicks Mar–Sep; ~70/day in July, 145–172/day early August; crashed to ~12/day after the August 308s of the chart pages (81.5% of clicks came from removed URLs). Chart pages restored Sep 26. Early recovery: between the Sep 25 and Sep 30 Bing exports, /blog/bmi-chart-women/ gained +1,546 impressions and +43 clicks; sitewide about 25–30 clicks/day vs ~12/day mid-September.

## Shipped (commits)
- 7866479 P0: chart pages restored at old URLs (women, men, by-age), CDC rounding rule, residue fixes, tool-first calculators.
- e30ddf0 P1: kids calculator on CDC LMS/extended method (unit tests pass), SVG and mobile fixes, .vercelignore (*.md, research/, data/, audit/, scripts/).
- a83d1f7, ae2ff9b: claim-level primary-source passes (batch 1 core pages, batch 2 guides).
- 8b68674: /bmi-chart/ built (201k "bmi chart" group), homepage and chart-explained de-cannibalized.
- 28e031a: shared nav with "BMI Chart", indexnow fix. 38d3cdd: repair of 7 pages a regex had broken. 47c44f6: claims content restored + content gates. 3a99491: exact-list removal of 35 unsourced tables/columns, WHO TRS 854 citation. 1826fe2: last accuracy figures + prescriptive column removed — cleanup complete, pushed.

## Standards (non-negotiable)
- Verified-or-omitted: every number or specific claim cites an R1 source or is removed. Nothing prescriptive (no calorie, protein, sleep or exercise targets).
- Never cite: Harvard (any), Mayo Clinic, Cleveland Clinic, NHS / National Health Service, American Heart Association / heart.org, ACE, ACSM, NSCA, Wikipedia.
- BMI bands: BMI = lb × 703 ÷ in² (or kg ÷ m²), rounded to 0.1 half-up, then CDC ranges; a band = lowest to highest whole pound/kg in that category. Tests: 5'9" → ≤124 / 125–168 / 169–202 / 203–236 / 237–270 / ≥271; 170 cm healthy 54–72 kg.
- Before any 308 or deletion: pull that URL's GSC and Bing clicks first.
- Every Claude Code batch: gate 33/33, then git archive → chat render check (360 px + desktop, SVG collisions) before building the next thing.
- Give Claude Code exact lists, not judgment rules — rule-based passes failed twice.

## Verified sources (R1)
- CDC Adult BMI Categories — https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html — underweight <18.5; healthy 18.5 to <25; overweight 25 to <30; obesity ≥30 (class 1 30 to <35, class 2 35 to <40, class 3 ≥40).
- CDC Child and Teen BMI Categories — https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html — <5th; 5th to <85th; 85th to <95th; ≥95th; severe ≥120% of 95th or BMI ≥35.
- CDC extended BMI-for-age method — https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm — LMS up to P95; above: pct = 90 + 10·Φ((BMI−P95)/sigma). Tests: girl 114.5 mo BMI 21.2 → 92.2nd (overweight); boy 50.5 mo BMI 22.6 → 99.77th, 126.8% of P95.
- NCHS Data Brief 508 — https://www.cdc.gov/nchs/products/databriefs/db508.htm — Aug 2021–Aug 2023, adults 20+: obesity 40.3% (men 39.2, women 41.3); by age 20–39 / 40–59 / 60+: 35.5 / 46.4 / 38.9 (women 36.8 / 47.4 / 39.6; men 34.3 / 45.4 / 38.0); severe obesity 9.4% (age-adj. 9.7), men 6.7, women 12.1.
- NCHS Health E-Stat 111 (Fryar, Afful, Saif, Feb 2026) — https://www.cdc.gov/nchs/data/hestat/hestat111.htm — age-adjusted overweight 31.7% (unadjusted 32.1), obesity 40.3%, severe 9.7%. Trend series NOT yet verified.
- Winter 2014 — https://pubmed.ncbi.nlm.nih.gov/24452240/ — meta-analysis of 32 cohort studies, 197,940 adults 65+: risk higher below BMI 23, rising above 33.
- Keys 1972 — https://doi.org/10.1016/0021-9681(72)90027-6 (reprint https://pubmed.ncbi.nlm.nih.gov/24691951/) — 7,424 men, 12 cohorts, 5 countries; weight/height² named body mass index. Commentary: https://pmc.ncbi.nlm.nih.gov/articles/PMC4052141/
- Quetelet 1832 memoir and 1842 English Treatise (text references).
- Ashwell 2012 Obes Rev 13:275–286 (31 studies, >300,000 adults; WHtR +4–5% vs BMI). Browning 2010 Nutr Res Rev 23:247–269 (0.5 boundary).
- WHO TRS 854 (1995) for thinness grades (text reference).

## Research files (repo research/)
keyword-ledger.csv (US KWP: 9,462 keywords, 5,068 groups), page-map.csv, sitemap.md.

## Next builds, in order
1. /us-obesity-statistics/ — link magnet (HE-Stat 111 trend series + DB 508 splits, embeddable chart, Dataset schema). Verify the trend table first.
2. /obesity-rate-by-state/ — CDC BRFSS state map (verify data first).
3. Body-fat trio: /body-fat-calculator/ (74k group), /body-fat-percentage-chart/, /blog/how-to-measure-body-fat/ — data-sourcing first (DoD/Navy circumference equations, NHANES DXA reference percentiles, method-validation studies).
4. Then /average-weight/ (NHANES), army/navy calculators, growth-chart calculator, FFMI.

## Open items
- Bing Webmaster: add https://calculatemybmi.net/ (Import from GSC) and submit its sitemap — Bing still reports everything under www URLs.
- GSC non-www property: Performance (16 months) + Pages exports once data appears; URL Inspection results for /, /bmi-chart/, /blog/bmi-chart-women/.
- SERP checks queued: body-fat chart one page vs women/men split; average weight split; "bmi for women" chart vs calculator intent.

## 2026-09-30 · /us-obesity-statistics/ built (see git log)
- Page: US obesity rate and statistics — NHANES Aug 2021–Aug 2023 snapshot + 1960–2023 trend (ages 20–74, age-adjusted), age/sex/education/race, children summary, measured-vs-self-reported section (Gallup), "Where do you fit?" widget, embeddable chart (CC BY 4.0; brand-anchor link only; nofollow allowed) and CSV (585 rows) served from /us-obesity-statistics/.
- Sources verified 30 Sep 2026 (research/data-sources.csv): NCHS Health E-Stats 111, 112, 119; NCHS Data Brief 508; NCHS Series 3 No. 50 (mean/median BMI and weight percentiles — ready for /average-weight/); NHANES population totals; Gallup 28 Oct 2025. Gallup's 2026 update is excluded (text and table disagree).
- Tier-2 KWP (3 batches, 789 keywords → 635 ledger rows): primary "us obesity rate" (14,800/mo). Childhood cluster (~4.8k/mo) → proposed /childhood-obesity-statistics/. State cluster (~13k/mo) → /obesity-rate-by-state/ — its BRFSS source is still a candidate; CDC's adult obesity maps page was updated ~24 Sep 2026, verify before building. Global (~10k/mo) parked; WHO GHO is the candidate source for a possible /obesity-rate-by-country/.
- 30 Sep 2026 follow-up: the 31.7% overweight figures already credit Health E-Stat 111 on every page (the earlier "misattributed" note was wrong); 9.7% severe obesity is in Data Brief 508 (age-adjusted trend). Fixed in the follow-up batch: stale prevalence on /men-bmi-calculator/ (chart 2/24/31/43%, FAQ avg BMI 29.1, 43%/31%), /kids-bmi-calculator/ (19.7%, 22.2/20.7/12.7%, 6.7% → Health E-Stat 112), /blog/bmi-chart-explained/ (approximate sex chart → Health E-Stat 111; orphan footnote removed), /calculators/ (42% → 40.3%). Nav: desktop now links BMI Chart, mobile duplicate replaced by Obesity Statistics, "Guides" no longer marked active on non-blog pages.
- Open: footer "Cookie settings" is plain text on every page (no reopenConsentSettings handler exists) — wire it to Raptive's CMP or remove it.
- Portfolio rules: never republish this page, the dataset or shared prose on other health sites (Google scaled-content policy names multiple sites hiding scaled content). Embed/licence links: brand anchor only, never keyword anchors, nofollow always allowed (Google link-spam policy, widget clause).
- Next builds: /obesity-rate-by-state/ → /childhood-obesity-statistics/ → /average-weight/.
