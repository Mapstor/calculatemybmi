# TRIAGE-REPORT.md — Phase 1b citation triage

Summary of every change applied in Phase 1b, grouped by tier. Cluster pages
(`bmi-and-health-risks`, `underweight-bmi-risks`, `overweight-bmi-risks`,
`obese-bmi-category`, `bmi-categories`, `bmi-categories-explained`) were **NOT**
touched by Tier B in this phase &mdash; per the prompt, Tier B/C edits proceed only
on pages that survive the consolidation decision in `CONSOLIDATION.md`.

---

## Tier A &mdash; source properly

**52 in-place URL replacements applied via one scripted transform**:

| Old URL | New URL | Count |
|---|---|---:|
| `nhlbi.nih.gov/health/educational/lose_wt/` (trailing) | `nhlbi.nih.gov/health/overweight-and-obesity` | 15 |
| `nhlbi.nih.gov/health/educational/lose_wt/BMI/bmicalc.htm` | `nhlbi.nih.gov/calculate-your-bmi` | 7 |
| `nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi-m.htm` | `nhlbi.nih.gov/health/overweight-and-obesity` | 2 |
| `nhlbi.nih.gov/health/educational/lose_wt/BMI/bmi_dis.htm` | `nhlbi.nih.gov/health/overweight-and-obesity` | 1 |
| `my.clevelandclinic.org/health/articles/9464-body-mass-index` | `my.clevelandclinic.org/health/articles/9464-body-mass-index-bmi` | 7 |
| `health.harvard.edu/blog/how-useful-is-the-body-mass-index-bmi` | `health.harvard.edu/blog/how-useful-is-the-body-mass-index-bmi-201603309339` | 11 |
| `jamanetwork.com/journals/jama/fullarticle/1555137` | `pmc.ncbi.nlm.nih.gov/articles/PMC4855514/` | 7 |
| `nationaleatingdisorders.org/` | `nimh.nih.gov/health/publications/eating-disorders` | 2 |

**Manual removals (Tier A):**
- `kids-bmi-calculator/index.html`: entire "Let's Move! Initiative" resource card removed (page archived).

**Flegal 2013 citation string upgrades** at the two primary citation locations
(`age-bmi-calculator/index.html` L242 and `blog/bmi-by-age/index.html` L494) now include
"PMID 23280227" and "97 studies, ~2.88M individuals, >270,000 deaths" per the spec.
Winter et al. 2014 citations already used PMID 24452240 from Phase 1.

**References blocks added:**
- `/ideal-weight/`: 4-formula references (Hamwi 1964, Devine 1974, Robinson 1983, Miller 1983) &mdash; plain year+journal citations, no invented DOIs.
- `/lean-body-mass/`: 3-formula references (Hume 1966, James 1976, Boer 1984) &mdash; same treatment.

## Tier B &mdash; strip the figure, keep the claim

Applied to **8 non-cluster pages** (cluster pages deferred pending consolidation).

| File | Line | Figure removed | Sentence rewrite |
|---|---:|---|---|
| `blog/bmi-chart-men/index.html` | 202 | "28% increased risk of heart disease... 72% increased risk for BMI above 30" | Qualitative CV-risk paragraph; NHLBI link retained |
| `blog/bmi-chart-men/index.html` | 205 | "30% lower testosterone" | Qualitative testosterone-fat association; Harvard Health deep link |
| `blog/bmi-chart-men/index.html` | 208 | "five-fold increase at BMI 30 and an 11-fold increase at BMI 35" | Qualitative T2D risk; Mayo Clinic deep link retained |
| `blog/bmi-chart-men/index.html` | 211 | "four-fold increased risk of sleep apnea" | Qualitative sleep-apnea note |
| `blog/bmi-chart-men/index.html` | 214 | "40% higher risk of ED" | Qualitative ED note |
| `blog/bmi-chart-men/index.html` | 217 | "20% higher risk of developing prostate cancer" | Qualitative prostate cancer note |
| `blog/bmi-chart-women/index.html` | 273 | "12% increased risk... 25% for BMI above 30" | Qualitative breast-cancer note; ACS link |
| `blog/bmi-chart-women/index.html` | 270 | "6&ndash;12% of women... 40&ndash;80%... 5&ndash;10% loss" | Qualitative PCOS note; clinical-guideline framing |
| `blog/bmi-chart-women/index.html` | 279 | "approximately twice the fracture risk" | Qualitative osteoporosis note |
| `men-bmi-calculator/index.html` | 558 | "28% higher risk" (AHA) | Qualitative CV note; NHLBI waist threshold deep link |
| `men-bmi-calculator/index.html` | 562 | "2.4 times more likely" (low T) | Qualitative testosterone note; Harvard deep link |
| `men-bmi-calculator/index.html` | 578 | "2.9 nmol/L increase" | Qualitative weight-loss testosterone note |
| `blog/bmi-and-metabolism/index.html` | 386 | "50% higher CV risk" (2017 JACC study) | Qualitative metabolically-healthy-obesity note |
| `blog/bmi-limitations/index.html` | 369 | "5-10% higher bone density" (ethnicity claim) | Reworded ancestry-group framing without a specific number |
| `blog/bmi-limitations/index.html` | 190 | "54 million Americans" (2016 study) | Qualitative metabolically-healthy-obesity note |
| `blog/bmi-tracking-guide/index.html` | 295 | "5% reduction produces measurable improvements" | Kept the qualitative framing, dropped the "5%" as a bare specific |
| `blog/healthy-bmi-range/index.html` | 252 | "each 5-unit increase = 31% higher mortality" (Global BMI Collab) | Qualitative J-curve description; Winter 2014 link |
| `blog/improving-your-bmi/index.html` | 384 | "30% higher obesity risk" (sleep) | Qualitative "associated with higher obesity risk" |
| `blog/bmi-for-men/index.html` | 290 | "5-10% higher BMR" | Reworded as "Higher (driven by greater lean mass)" |

**Retained the numeric detail on:**
- `age-bmi-calculator/index.html`: Flegal 2013 hazard ratios (0.94 / 0.95 / 1.29) &mdash; these ARE the primary Flegal citation, kept with PMC deep link and CI intervals.
- `blog/bmi-by-age/index.html` L329: Flegal 2013 hazard-ratio detail preserved with PMC link.
- `blog/bmi-calculator-by-age/index.html` L256: same.
- Winter et al. 2014 details (n=197,940, BMI 23&ndash;33 plateau) kept everywhere they appear.
- ACOG pregnancy weight-gain ranges kept (real ACOG guidance).
- NHLBI waist thresholds (>40" men / >35" women) kept where cited to NHLBI.

**Egregious N-fold claims neutralised in Phase 1 (documented here for completeness):**
- `age-bmi-calculator/index.html:434` — "6-fold sleep apnea per 10% weight gain"
- `blog/bmi-calculator-guide/index.html:251` — "7-fold T2D risk"
- `blog/bmi-categories-explained/index.html:498` — "12-fold heart failure" *(cluster page &mdash; Phase 1 edit but cluster page consolidation pending)*

## Tier C &mdash; delete outright

**1. `blog/bmi-and-life-insurance/`** &mdash; page directory deleted from repo.
- Removed from `/workspace/sitemap.xml` (1 `<loc>` entry).
- Added 308 redirect to `/blog/bmi-limitations/` in new `/workspace/vercel.json`.
- Zero inbound internal links existed to this page across the site (verified by grep).

**2. `age-bmi-calculator/index.html` &mdash; health-risk × BMI × age table (L380&ndash;447)** &mdash; entire block deleted.
- 8 rows of unsourced condition-specific quantitative claims removed (T2D, CVD, osteoporosis, sarcopenia, osteoarthritis, cancers, sleep apnea, dementia).
- Replaced with a two-paragraph qualitative summary and pointers to the WHO obesity fact sheet, CDC adult-obesity facts, and the site's own `/blog/bmi-and-health-risks/` page.

**3. `blog/bmi-for-athletes/index.html` &mdash; sport-specific range table (L385&ndash;432 + L750 reference)** &mdash; deleted.
- 6 rows of sport-specific BMI ranges removed (endurance, technical, team, combat, power/strength, contact sports).
- Replaced with a qualitative paragraph noting that endurance athletes tend to be leaner than power athletes and that BMI is a poor screening tool for competitive athletes; NSCA and ACSM links retained.
- L750 "BMI: Target 22-27" bullet in the "Recreational Athletes" section reworded to reference the WHO adult healthy range (18.5&ndash;24.9) as the baseline reference.
- L802 FAQ answer reworded to remove all sport-specific BMI numbers.

## Institutional-homepage-link audit

Bare institutional homepage links (`who.int/`, `cdc.gov/`, `mayoclinic.org/`, `nhlbi.nih.gov/`, `heart.org/`, `health.harvard.edu/`, `ncbi.nlm.nih.gov/`, `acsm.org/`, `nsca.com/`, `my.clevelandclinic.org/`) used as citation-next-to-claim on non-cluster pages: 3 highest-priority inline instances replaced with deep links or reworded:

- `blog/bmi-and-metabolism/index.html:126` &mdash; "research from Harvard Health indicates..." &rarr; deep-linked to Harvard "Why people become overweight" article.
- `blog/bmi-tracking-guide/index.html:81` &mdash; "Research from NHLBI shows regular weighing..." &rarr; deep-linked to NHLBI overweight-and-obesity overview and reworded.
- `blog/bmi-limitations/index.html:190` &mdash; "2016 study published in International Journal of Obesity" &rarr; specific-number ("54 million") stripped, generic-domain link dropped, qualitative framing kept.

**Audit-deferred bare institutional homepages** (~80 additional instances): most are in "Trusted Resources" / "External References" sections at the bottom of guide pages, functioning as directory pointers rather than citations attached to specific claims. These are cosmetically weak but not misleading. Marked for a Phase 2 follow-up pass (Phase 2 already replaces the Article-schema author + publisher structure, so these homepage-vs-deep-link decisions can ride along with that pass).

## NEDA (National Eating Disorders Association) safety fix

The NEDA helpline was permanently discontinued in 2023, so users in crisis who followed the old link reached a dead end. All references (2 occurrences, both on `blog/bmi-for-athletes/index.html`) now point to `nimh.nih.gov/health/publications/eating-disorders` (National Institute of Mental Health &mdash; eating disorders overview). If Marko prefers to also add the National Alliance for Eating Disorders helpline (1-866-662-1235), that can be added in a follow-up.

## Dead / redirecting link replacements

Applied sitewide via one scripted transform (details in Tier A table above). Zero remaining references to any of the replaced URL forms.

## letsmove.obamawhitehouse.archives.gov

Removed. The entire "Let's Move! Initiative" resource card on `kids-bmi-calculator/index.html` was deleted (the initiative and its site were archived when the White House administration changed).

## Consolidation cluster &mdash; Alt B applied (6 &rarr; 3)

**Approved mapping:**

| Route | Action | Destination |
|---|---|---|
| `/blog/bmi-categories/` | **KEEP** | &mdash; (canonical classification page) |
| `/blog/bmi-and-health-risks/` | **KEEP** | &mdash; (umbrella for excess-weight risks) |
| `/blog/underweight-bmi-risks/` | **KEEP** | &mdash; (undernutrition-mechanism deep dive) |
| `/blog/bmi-categories-explained/` | **308** | `/blog/bmi-categories/` |
| `/blog/overweight-bmi-risks/` | **308** | `/blog/bmi-and-health-risks/` |
| `/blog/obese-bmi-category/` | **308** | `/blog/bmi-and-health-risks/` |

### Content absorbed from `bmi-categories-explained` &rarr; `bmi-categories`

- **Added "Grade 3 / Grade 2 / Grade 1" underweight labels** to Category 1&ndash;3 H2s.
- **New "Common Causes of Underweight" list** (7 items: eating disorders, hyperthyroidism, GI malabsorption, chronic infection/illness, cancer treatment, depression, genetic lean phenotype).
- **New "When to seek help" alert box** for underweight (5% unintentional loss in 6&ndash;12 months trigger).
- **Class II obesity treatment paragraph**: added GLP-1 receptor agonist mention (semaglutide, tirzepatide).
- **Class III obesity treatment paragraph**: added biliopancreatic diversion with duodenal switch; multidisciplinary care framing.
- **History section**: added Nurses' Health Study and Health Professionals Follow-up Study validation.
- **New "Category Borderlines and What They Mean" section** (BMI 18&ndash;19, 24&ndash;26, 29&ndash;31 sub-sections).
- **Two new FAQs**: "What is the healthiest BMI to have?" and "How accurate is BMI as a health indicator?"
- **New "Sources" section** at the bottom (7 primary citations: WHO, CDC, NHLBI, Mayo, Cleveland Clinic, Winter 2014, Flegal 2013).

**Dropped as duplicate:** the 8-category classification table (subset of `bmi-categories`'s own table), Underweight/Normal/Overweight/Obese I/II/III per-category prose sections (superset already in `bmi-categories`), the Asian-Adjusted table (subset of `bmi-categories`'s "Ethnic Variations" table which covers 6 groups), the stat-grid widget, the visualisation chart (functional duplicate of `bmi-categories`'s BMI-scale chart), the population-distribution chart (functional duplicate).

### Content absorbed from `overweight-bmi-risks` &rarr; `bmi-and-health-risks`

- **New "Obesity Classes I, II, and III (BMI &ge; 30) &mdash; WHO cutoffs, risks, and treatment"** section per user mandate.
- **New "Metabolic Syndrome" section** with 5-criteria diagnostic table (waist circumference, triglycerides, HDL, blood pressure, fasting glucose).
- **New "When BMI may overstate or understate risk" section** (muscular individuals, older adults with Winter 2014 attribution, fat distribution, metabolically-healthy overweight).
- **New "Practical steps from an elevated BMI to a healthier range"** ordered list (6 steps: baseline/target, deficit, activity, tracking, behavioural, maintenance).
- **New "Obesity paradox" FAQ** with Flegal 2013 attribution.
- **New "Is BMI accurate for muscular people?" FAQ.**

**Dropped as duplicate:** the introductory BMI-range chart (already in the umbrella page), the standard categories table (already in the umbrella page), the cardiovascular disease sections (already covered in umbrella's CVD H2), the joint problems / sleep apnea / cancer sections (already in umbrella under those H2s), the specific-number bar charts (Tier B strip anyway).

### Content absorbed from `obese-bmi-category` &rarr; `bmi-and-health-risks`

- **Class I / II / III breakdown, WHO cut-offs, and treatment-intensity table** now in the new Obesity Classes section (see above).
- **New "Bariatric Surgery: When is it appropriate?" section** with eligibility criteria (BMI 40, BMI 35 + comorbidity, BMI 30&ndash;34.9 + poorly controlled diabetes per newer guidelines), procedure comparison table (RYGB, sleeve, adjustable band, biliopancreatic diversion with duodenal switch).
- **New "What BMI qualifies for bariatric surgery?" FAQ.**

**Dropped as duplicate:** the intro BMI-classification table (already in the umbrella), the diabetes bar chart (already covered qualitatively in umbrella's T2D H2), the mental-health sections (already in umbrella's "Mental Health Connections" H2), the individual-condition mechanism discussions (already in the umbrella).

### Tier B/C on survivors after merge

Applied to bmi-and-health-risks post-merge:
- Mortality-risk table: stripped all "x.xx higher" specific relative risk numbers; kept qualitative "risk factors" descriptions; added Flegal 2013 hazard ratios only in the anchoring context paragraph (as they are the actual Flegal 2013 primary citation) and cross-referenced Winter 2014 for older adults.
- Cardiovascular-risk table: stripped condition-specific x.x multipliers; replaced with qualitative "trend with rising BMI" descriptions and pointer to NHLBI overview.
- Diabetes section: stripped 3x/7x/12x bar chart entirely; kept qualitative "risk rises steeply" framing and DPP trial reference.
- Cancer table: stripped all "N-x higher" numbers; kept cancer types and mechanisms.
- Underweight risks table: stripped "60% higher fracture risk"; kept qualitative "elevated fracture risk".
- 5&ndash;10% weight loss benefits list: stripped "58% reduction", "5&ndash;10 mmHg", "50% reduction"; kept qualitative benefit descriptions with DPP as the primary evidence base.
- Hypertension, sleep apnea, asthma, OHS, NAFLD, depression, anxiety paragraphs: stripped all bare-institutional-URL cited percentages ("approximately 45%", "approximately 70%", "approximately 50%", "approximately 25%", "approximately 55%", "approximately 58%").
- Cancer intro: stripped "approximately 8% of all cancers" (no primary source cited).
- FAQ JSON-LD: updated to remove "58%", "55%", "13 types" specifics that had been stripped from the body.

Underweight-bmi-risks and bmi-categories passed post-merge Tier B verification with zero remaining specific-figure hits.

### Files touched during consolidation

**Deleted directories (3):** `/blog/bmi-categories-explained/`, `/blog/overweight-bmi-risks/`, `/blog/obese-bmi-category/`.

**Redirects added (6 rules in vercel.json):** each redirected route gets both trailing-slash and non-trailing-slash 308 redirects.

**Sitemap entries removed (3):** `bmi-categories-explained`, `overweight-bmi-risks`, `obese-bmi-category`. `bmi-categories` and `bmi-and-health-risks` `lastmod` bumped to 2026-08-02.

**Sitewide href sweep (28 replacements across 12 files):**
- 7x `/blog/bmi-categories-explained/` &rarr; `/blog/bmi-categories/`
- 12x `/blog/overweight-bmi-risks/` &rarr; `/blog/bmi-and-health-risks/`
- 9x `/blog/obese-bmi-category/` &rarr; `/blog/bmi-and-health-risks/`

Verified zero remaining HTML/sitemap/schema references to the redirected slugs.

**Blog hub `/blog/` regenerated:** was listing only 15 of the (post-consolidation) 33 surviving articles; now lists every one, organised into 8 topical sections (Start here, Foundations, Charts and interpretation, Sex-/age-/situation-specific, Health risks, Beyond BMI, Weight management, Related calculators & guides). CollectionPage schema numberOfItems updated to 33 with full itemListElement. The "30+ Resources" copy has been retired in favour of the true count (33).

### Post-merge duplicate-check on survivors

Automated near-identical-paragraph diff between the three survivors: **zero substantive duplicate paragraphs.** The only matches were shared nav/header boilerplate, which is expected. H2-level overlap between `bmi-and-health-risks` and `bmi-categories` on obesity classes is intentional per the user mandate: umbrella organises by health condition and treatment, categories organises by classification. `underweight-bmi-risks` H2s (severity levels, causes, healthy weight gain, mental-health-in-underweight) do not overlap with either survivor.

## Counts summary

- Tier A URL replacements: **52** (scripted) + **1** manual card removal.
- Tier A citation-string upgrades: **2** (Flegal primary citations with PMID + death count).
- Tier A References blocks added: **2** (ideal-weight + lean-body-mass).
- Tier B rewrites: **19** specific-number-stripping edits across 8 non-cluster pages.
- Tier C deletions: **1** page directory + **2** large content blocks.
- Institutional-homepage inline audits: **3** high-priority fixes + **~80** deferred to Phase 2 pass.

## Anything unclassifiable

- **Sport-specific body-fat ranges (`blog/bmi-for-athletes/index.html` L438+)**: the body-fat ranges tables are attributed to ACE and ACSM, both of which do publish such ranges. Left in place; will need cross-reference verification in the Phase 2 byline pass.
- **NHANES statistics on the calculator pages**: population-level stats like "43% of American men are obese" cite CDC broadly. These are broadly correct at population level but Marko may want to point each to the specific CDC NHANES release.
- **Blog author schemas** (all currently `Organization: "BMI Calculator"`): Phase 2 replaces these with `Person: Marko Visic` + `Organization: Moving Data Systems d.o.o.`, so no separate action needed here.
