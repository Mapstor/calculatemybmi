# CONSOLIDATION-2.md — full pass over all 33 surviving blog posts

Analysis of every current `/blog/*/index.html` route against the criterion **distinct
intent AND distinct data**. Target from the prompt: roughly 18-20 survivors. **My
recommendation lands at 16 blog survivors.** The 2-post shortfall vs. 18 is deliberate
&mdash; I could not justify keeping two more posts under a strict distinctness rule
without adding maintenance debt for pages that duplicate an already-strong survivor. If
you disagree on any specific line I list below, flag it and I'll flip it.

The 8 tool pages (`/`, `/women-bmi-calculator/`, `/men-bmi-calculator/`,
`/age-bmi-calculator/`, `/kids-bmi-calculator/`, `/new-bmi-calculator/`,
`/ideal-weight/`, `/lean-body-mass/`) are not blog posts and are not being consolidated
&mdash; but 8 of the 17 blog 308s point at them (the "doorway" pattern that Raptive
flags). Those merges make the tool pages stronger, not weaker.

---

## Verdict summary

| Verdict | Count |
|---|---:|
| KEEP (blog) | **16** |
| 308 → another blog post | 6 |
| 308 → a tool page (doorway pattern) | 11 |
| **Total analysed** | **33** |

Net article count on `/blog/` after this pass: **16** (down from 33). The 11 doorway 308s
also make 5 tool pages meaningfully stronger.

---

## Cluster A — Blog-vs-tool doorway pattern (highest priority)

Six posts are shadow articles about tools that already exist on the site. Merge blog
content into the tool page and 308.

| Route | Verdict | Target | One-line reason |
|---|---|---|---|
| `blog/ideal-weight-calculator/` (3.4k words) | **308** | `/ideal-weight/` | Shadow article of the tool. Formulas and per-height tables belong on the tool page &mdash; and after Phase 1b the tool already carries the References block. |
| `blog/bmi-calculator-by-age/` (4.4k words) | **308** | `/age-bmi-calculator/` | Shadow article. Age-band context already sits on the tool page (Winter 2014, Flegal 2013 in cluster survivors); absorb the prose depth. |
| `blog/pediatric-bmi-calculator/` (4.1k words) | **308** | `/kids-bmi-calculator/` | Shadow article for the kids tool. Absorb CDC-percentile explainer. |
| `blog/lean-body-mass-calculator/` (3.2k words) | **308** | `/lean-body-mass/` | Same pattern. Tool already carries the LBM References block. Absorb any body-composition prose. |
| `blog/bmi-percentile-calculator/` (3.4k words) | **308** | `/kids-bmi-calculator/` | Second shadow of the pediatric tool (percentile-focused). Absorb whichever percentile detail is not already there. |
| `blog/bmi-for-children/` (3.3k words) | **308** | `/kids-bmi-calculator/` | Also pediatric-tool-adjacent. All three "kids" blog posts fold into the tool. |

The kids tool is the biggest absorber (3 blog posts merging in). Post-merge it becomes
a genuinely comprehensive pediatric-BMI resource; today the blog and the tool duplicate
each other.

## Cluster B — Weight-loss advice (4 → 1)

| Route | Verdict | Target | Reason |
|---|---|---|---|
| `blog/how-to-lower-bmi/` (4.2k) | **KEEP** | &mdash; | Umbrella. Already carries the Phase-1 reframe of the 3,500 kcal rule and the DPP reference. |
| `blog/improving-your-bmi/` (3.1k) | **308** | `blog/how-to-lower-bmi/` | Same topic, softer framing ("improving" vs "lowering"). No distinct data. |
| `blog/healthy-weight-tips/` (4.0k) | **308** | `blog/how-to-lower-bmi/` | "12 tips" listicle overlapping heavily with the umbrella. Absorb any tip that isn't already covered. |
| `blog/bmi-tracking-guide/` (3.4k) | **KEEP** | &mdash; | Distinct intent: *how to weigh* (frequency, technique, interpreting fluctuations), not what to eat. Different search intent from weight-loss strategy. |

## Cluster C — Charts (3 → 1)

| Route | Verdict | Target | Reason |
|---|---|---|---|
| `blog/bmi-chart-explained/` (4.3k) | **KEEP** | &mdash; | The one non-gendered chart interpretation guide. |
| `blog/bmi-chart-women/` (3.6k) | **308** | `/women-bmi-calculator/` | Gendered chart tables belong on the gendered calculator. The tool is already the gendered surface; a separate chart post is triple-redundant with the tool and with the general chart guide. |
| `blog/bmi-chart-men/` (3.5k) | **308** | `/men-bmi-calculator/` | Same as above. |

## Cluster D — Age (both blog posts fold into the tool)

| Route | Verdict | Target | Reason |
|---|---|---|---|
| `blog/bmi-by-age/` (3.7k) | **308** | `/age-bmi-calculator/` | Prose companion to the age tool. Body-composition-by-decade content absorbed into the tool page (which already carries Winter 2014 detail after Phase 1). |
| `blog/bmi-calculator-by-age/` | **308** | (already in Cluster A above) | Same as Cluster A entry. |

## Cluster E — Body composition (4 → 2)

| Route | Verdict | Target | Reason |
|---|---|---|---|
| `blog/body-fat-vs-bmi/` (3.7k) | **KEEP** | &mdash; | Umbrella: BMI vs body-fat percentage, methods to measure body fat (DEXA, BIA, skinfolds), healthy ranges. |
| `blog/bmi-for-athletes/` (4.1k) | **KEEP** | &mdash; | Distinct population (competitive/muscular). Distinct data (sport-specific patterns). Already cleaned in Phase 1b (sport-range table stripped). |
| `blog/muscle-mass-and-bmi/` (3.4k) | **308** | `blog/bmi-for-athletes/` | Same topic viewed from the metric side rather than the population side. Absorb into athletes page. |
| `blog/bmi-vs-body-composition/` (3.1k) | **308** | `blog/body-fat-vs-bmi/` | Same comparison, weaker framing. Absorb body-comp methods that aren't already covered on `body-fat-vs-bmi`. |

## Cluster F — Definitions (3 → 2)

| Route | Verdict | Target | Reason |
|---|---|---|---|
| `blog/what-is-bmi/` (3.8k) | **KEEP** | &mdash; | Plain-language explainer. Distinct intent from formula/math. |
| `blog/bmi-formula/` (3.3k) | **KEEP** | &mdash; | Math deep-dive: metric/imperial derivation, 703 conversion factor, Trefethen 2013 formula. Distinct data. |
| `blog/bmi-calculator-guide/` (3.9k) | **308** | `blog/what-is-bmi/` | The "how to use our calculator" framing is really a duplicate explainer. Absorb any calculator-use content that isn't already on `what-is-bmi` or the `/` tool page itself. |

## Everything else (not in a listed cluster)

| Route | Verdict | Target | Reason |
|---|---|---|---|
| `blog/bmi-and-health-risks/` (5.7k) | **KEEP** | &mdash; | Phase 1b survivor. Umbrella for excess-weight risks + obesity classes + bariatric surgery. |
| `blog/bmi-categories/` (4.3k) | **KEEP** | &mdash; | Phase 1b survivor. Canonical 8-category WHO classification. |
| `blog/underweight-bmi-risks/` (3.2k) | **KEEP** | &mdash; | Phase 1b survivor. Distinct topic (undernutrition mechanisms + weight-gain strategies + eating-disorder framing). |
| `blog/bmi-accuracy/` (3.5k) | **308** | `blog/bmi-limitations/` | "How accurate is BMI" and "10 limitations of BMI" answer the same underlying question (does BMI work, and where does it fail). Absorb accuracy data into the limitations page. |
| `blog/bmi-and-metabolism/` (3.7k) | **KEEP** | &mdash; | Distinct intent: metabolic rate, BMR/TDEE calculation, metabolic syndrome (linked to the Alberti-2009 material now on `bmi-and-health-risks`). "Understand your metabolism" is a distinct search from "understand health risks." |
| `blog/bmi-for-men/` (3.7k) | **308** | `/men-bmi-calculator/` | Doorway pattern &mdash; shadow guide for the men's tool. Absorb male-specific health context. |
| `blog/bmi-for-surgery/` (2.9k) | **KEEP** | &mdash; | Distinct topic (surgical BMI thresholds across procedure types), distinct data (transplant / joint / bariatric / cosmetic ranges). No overlap. |
| `blog/bmi-for-women/` (3.9k) | **308** | `/women-bmi-calculator/` | Doorway pattern &mdash; shadow guide for the women's tool. Absorb female-specific health context, pregnancy/menopause detail. |
| `blog/bmi-history/` (4.2k) | **KEEP** | &mdash; | Distinct topic (200-year history: Quetelet → Keys → WHO → NIH thresholds). Standalone; no other page covers it. |
| `blog/bmi-limitations/` (3.4k) | **KEEP** | &mdash; | 10 specific limitations. Absorbs `bmi-accuracy`. |
| `blog/healthy-bmi-range/` (3.4k) | **KEEP** | &mdash; | "Healthy BMI range" is a distinct search intent from "what is BMI." Focuses specifically on the 18.5-24.9 band and how to get into it. Already carries age-adjusted content from Phase 1. |
| `blog/waist-to-height-ratio/` (3.3k) | **KEEP** | &mdash; | Distinct alternative metric (WHtR). Standalone. |

---

## Blog survivors after this pass (16)

1. `blog/bmi-and-health-risks/` &mdash; umbrella for excess-weight risks
2. `blog/bmi-and-metabolism/` &mdash; metabolism, BMR, TDEE
3. `blog/bmi-categories/` &mdash; canonical classification
4. `blog/bmi-chart-explained/` &mdash; general chart interpretation
5. `blog/bmi-for-athletes/` &mdash; population-specific (athletes)
6. `blog/bmi-for-surgery/` &mdash; surgical BMI thresholds
7. `blog/bmi-formula/` &mdash; math deep dive
8. `blog/bmi-history/` &mdash; 200-year history
9. `blog/bmi-limitations/` &mdash; 10 failure modes (absorbs `bmi-accuracy`)
10. `blog/bmi-tracking-guide/` &mdash; how to weigh + interpret fluctuations
11. `blog/body-fat-vs-bmi/` &mdash; body-fat % + methods umbrella
12. `blog/healthy-bmi-range/` &mdash; 18.5&ndash;24.9 focused
13. `blog/how-to-lower-bmi/` &mdash; weight-loss strategies umbrella
14. `blog/underweight-bmi-risks/` &mdash; undernutrition
15. `blog/waist-to-height-ratio/` &mdash; alternative metric
16. `blog/what-is-bmi/` &mdash; plain-language explainer

## Full redirect list (17 blog 308s)

Blog → blog:
1. `blog/bmi-accuracy/` → `blog/bmi-limitations/`
2. `blog/bmi-calculator-guide/` → `blog/what-is-bmi/`
3. `blog/bmi-vs-body-composition/` → `blog/body-fat-vs-bmi/`
4. `blog/muscle-mass-and-bmi/` → `blog/bmi-for-athletes/`
5. `blog/healthy-weight-tips/` → `blog/how-to-lower-bmi/`
6. `blog/improving-your-bmi/` → `blog/how-to-lower-bmi/`

Blog → tool (doorway pattern):
7. `blog/ideal-weight-calculator/` → `/ideal-weight/`
8. `blog/lean-body-mass-calculator/` → `/lean-body-mass/`
9. `blog/pediatric-bmi-calculator/` → `/kids-bmi-calculator/`
10. `blog/bmi-percentile-calculator/` → `/kids-bmi-calculator/`
11. `blog/bmi-for-children/` → `/kids-bmi-calculator/`
12. `blog/bmi-calculator-by-age/` → `/age-bmi-calculator/`
13. `blog/bmi-by-age/` → `/age-bmi-calculator/`
14. `blog/bmi-chart-women/` → `/women-bmi-calculator/`
15. `blog/bmi-chart-men/` → `/men-bmi-calculator/`
16. `blog/bmi-for-women/` → `/women-bmi-calculator/`
17. `blog/bmi-for-men/` → `/men-bmi-calculator/`

## Where I'm materially under 18-20

Two areas I could push back on if you want more blog survivors:

- **`bmi-accuracy` and `bmi-limitations` as two separate posts.** I merged them because
  both answer "does BMI work / when does it fail." If you'd rather keep both, note that
  one becomes a 3,500-word "sensitivity/specificity vs body-fat correlation" page and
  the other stays as a "10 failure modes" list. Together they add 2 blog posts and one
  more maintenance obligation for citations.

- **`bmi-and-metabolism` stayed KEEP by a thin margin.** If you'd rather fold it
  into `bmi-and-health-risks` (which now carries the Alberti-2009 metabolic-syndrome
  material), the survivor list drops to 15 &mdash; but the umbrella page grows by
  another ~3,700 words and its intent widens from "excess-weight risks" to "excess-
  weight risks + how metabolism works," which is a real intent shift.

## STOP for your approval

Reply **"approve consolidation-2 as proposed"** and Phase 4.4 will:
1. Absorb each dying page's unique sections/tables/FAQs/citations into its survivor.
2. Add all 17 redirects to `vercel.json` (alongside the existing 6 from Phase 1b).
3. Sweep internal links sitewide (grep-verified zero pointers at redirected slugs).
4. Delete the 17 page directories.
5. Regenerate `sitemap.xml` and the `/blog/` hub with the new count and full ItemList.
6. Re-run Tier B on every survivor including absorbed content &mdash; no stripped figure may
   re-enter through a merge.
7. Post-merge duplicate check across all survivors, flagging any near-duplicates.
8. Commit `raptive-remediation: phase 4 — seo surface and consolidation`.

Or reply with edits to specific keep/308 lines and I'll apply your version.
