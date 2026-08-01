# CONSOLIDATION.md — proposal for the health-risks / categories cluster

Six pages currently occupy overlapping territory in the health-risks / BMI-category
space. Phase 1b evaluates them against the criterion **distinct intent AND distinct
data** and proposes the consolidation below. Phase 2 byline/schema work + Phase 1b
Tier B/C citation edits will apply only to whichever pages survive.

## Pages under review

| Route | Words | H1 |
|---|---:|---|
| `/blog/bmi-categories/` | 3,102 | BMI Categories: All Weight Classifications Explained |
| `/blog/bmi-categories-explained/` | 2,900 | BMI Categories Explained: Complete Guide to Understanding Your Body Mass Index |
| `/blog/bmi-and-health-risks/` | 3,522 | BMI and Health Risks: Complete Guide to Weight-Related Conditions |
| `/blog/underweight-bmi-risks/` | 2,886 | Underweight BMI Risks: Complete Guide to Health Concerns, Causes & Solutions |
| `/blog/overweight-bmi-risks/` | 3,273 | Overweight BMI Risks: Understanding the Health Implications of BMI 25-29.9 |
| `/blog/obese-bmi-category/` | 2,897 | Obese BMI Category: Understanding Obesity Classes I, II & III |

## Intent + data analysis

**`bmi-categories`** &mdash; canonical reference: full 8-category WHO classification
(severe/moderate/mild thinness through Obese I/II/III), plus **history of the 25/30
cutoffs** and **ethnic variations** (Asian-population lower thresholds). Data set:
WHO/CDC classification thresholds + historical + ethnic overlays.

**`bmi-categories-explained`** &mdash; reference: 6-category WHO summary with per-range
sections and an "Asian-adjusted" block. **Same intent, subset of same data.** Nothing
here is missing from `bmi-categories`.

**`bmi-and-health-risks`** &mdash; umbrella: BMI/mortality relationship + one-section-per-
condition (CV, T2D, cancer, respiratory, musculoskeletal, liver, kidney, mental
health, and a section on being underweight). Organised **by health condition**.

**`underweight-bmi-risks`** &mdash; range-specific: BMI &lt;18.5. Distinct data: severity
sub-classes of underweight, causes of underweight (medical vs behavioural), healthy
**weight-gain** strategies, mental-health / eating-disorder considerations. None of
this is fully covered by the umbrella.

**`overweight-bmi-risks`** &mdash; range-specific: BMI 25&ndash;29.9. Covers CV, T2D,
joint, sleep apnea, cancer, mental health, obesity paradox. **Almost every section is
also in the umbrella page.** The one distinctive bit is the obesity-paradox discussion
&mdash; but that also lives on `age-bmi-calculator` and `bmi-by-age`.

**`obese-bmi-category`** &mdash; range-specific: BMI &ge;30, with Class I/II/III
differentiation. Distinct data: **class-by-class risk stratification**, **treatment
options** (medication, behavioural, bariatric), **bariatric-surgery eligibility
criteria**, and **life-expectancy impact**. None of this is fully covered by the
umbrella.

## Recommended consolidation (primary proposal, 6 &rarr; 4)

| Route | Action | Target |
|---|---|---|
| `/blog/bmi-categories/` | **KEEP** &mdash; canonical classification page | &mdash; |
| `/blog/bmi-categories-explained/` | **308** | `/blog/bmi-categories/` |
| `/blog/bmi-and-health-risks/` | **KEEP** &mdash; umbrella disease-organised page | &mdash; |
| `/blog/underweight-bmi-risks/` | **KEEP** &mdash; distinct range with gain strategies + eating-disorder framing | &mdash; |
| `/blog/overweight-bmi-risks/` | **308** | `/blog/bmi-and-health-risks/` |
| `/blog/obese-bmi-category/` | **KEEP** &mdash; distinct class breakdown + bariatric criteria | &mdash; |

Rationale for the two 308s:
- `bmi-categories-explained` fails both prongs against `bmi-categories`: same intent,
  same data (in fact a strict subset).
- `overweight-bmi-risks` shares intent and most data with `bmi-and-health-risks`; its
  only distinctive material (the obesity-paradox discussion) duplicates content that
  already exists on other surviving pages. Keeping it forces us to maintain the same
  content in two places.

If Approach 1 is approved: net article count on `/blog/` drops from 37 &rarr; 35 after
these two 308s (plus the earlier deletion of `bmi-and-life-insurance` in Phase 1b Tier
C brings it to 34).

## Alternative A (conservative, 6 &rarr; 5)

Keep both range pages, only merge the classification duplicate.

| Route | Action | Target |
|---|---|---|
| `/blog/bmi-categories/` | KEEP | &mdash; |
| `/blog/bmi-categories-explained/` | 308 | `/blog/bmi-categories/` |
| `/blog/bmi-and-health-risks/` | KEEP | &mdash; |
| `/blog/underweight-bmi-risks/` | KEEP | &mdash; |
| `/blog/overweight-bmi-risks/` | KEEP | &mdash; |
| `/blog/obese-bmi-category/` | KEEP | &mdash; |

Reason to prefer: cleaner intent story for the reader ("underweight risks vs
overweight risks vs obesity classes") maps neatly to the three range pages. The
"redundancy" is acceptable if we accept that the umbrella page + range pages serve
different reader entry points.

Reason against: leaves the biggest overlap (health-risks vs overweight-risks) in
place, keeping the citation-debt maintenance burden on both.

## Alternative B (aggressive, 6 &rarr; 3)

Fold both mid-range pages into the umbrella.

| Route | Action | Target |
|---|---|---|
| `/blog/bmi-categories/` | KEEP | &mdash; |
| `/blog/bmi-categories-explained/` | 308 | `/blog/bmi-categories/` |
| `/blog/bmi-and-health-risks/` | KEEP | &mdash; |
| `/blog/underweight-bmi-risks/` | KEEP | &mdash; |
| `/blog/overweight-bmi-risks/` | 308 | `/blog/bmi-and-health-risks/` |
| `/blog/obese-bmi-category/` | 308 | `/blog/bmi-and-health-risks/` |

Reason to prefer: minimises maintenance surface and citation-verification workload.
Bariatric criteria + class differentiation can move into a section of
`bmi-and-health-risks` (or a shorter satellite page linked from it).

Reason against: loses the range-organised entry point that a reader searching "BMI 32
what does it mean" might prefer, and loses the bariatric-surgery deep dive as a
first-class page.

## Whichever you pick

Once approved, Phase 1b will:
1. Add the corresponding 308 redirects to `/workspace/vercel.json` (the file already
   exists from the `bmi-and-life-insurance` deletion).
2. Remove the redirected pages from `/workspace/sitemap.xml`.
3. Sweep every internal link across the site and update `href` values to point to the
   destination.
4. Delete the redirected pages' directories.
5. Apply Tier B/C citation edits only to surviving pages.

## STOP for approval

I am awaiting your decision: **Approach 1 (recommended)**, **Alternative A**,
**Alternative B**, or a custom mapping.

If Approach 1: reply "approve consolidation approach 1".
If Alternative A: reply "approve alternative A".
If Alternative B: reply "approve alternative B".
Or specify a custom keep/308 mapping and I will apply it.
