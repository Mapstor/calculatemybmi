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
- Nothing prescriptive: no calorie, protein, sleep or exercise targets.
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
1. C2b-4: remove the remaining calorie, protein, sleep and exercise targets (how-to-lower-bmi, healthy-bmi-range, bmi-categories, age-bmi-calculator, bmi-and-metabolism incl. its 6-vs-2 kcal FAQ, underweight-bmi-risks, lean-body-mass, women postpartum) in visible text and FAQ JSON-LD.
2. Final check: fresh git archive -> chat sitewide scan + render check, then one IndexNow run (all URLs).
3. /obesity-rate-by-state/ — verify CDC BRFSS state data first (maps page updated ~24 Sep 2026).
4. /childhood-obesity-statistics/ (proposed; Health E-Stat 112 verified).
5. Body-fat trio: /body-fat-calculator/ (74k group), /body-fat-percentage-chart/, /blog/how-to-measure-body-fat/ — data-sourcing first.
6. /average-weight/ (Series 3 No. 50 data ready), army/navy calculators, growth-chart calculator, FFMI.
7. Possible /obesity-rate-by-country/ (WHO GHO is the candidate source; verify first).

## Open items
- Bing Webmaster: add https://calculatemybmi.net/ (import from GSC) and submit its sitemap.
- GSC non-www: Performance + Pages exports once data appears.
- /blog/bmi-for-athletes/ is still short (~700 words): candidate for a sourced expansion.
- Registry debt: data-sources.csv rows for the older pages.
- SERP checks queued: body-fat chart one page vs women/men split; average weight split; "bmi for women" chart vs calculator intent.
