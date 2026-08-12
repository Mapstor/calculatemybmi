# Phase 11 — Bespoke Visuals Plan

Per-page inline-SVG proposal for all 29 sitemap pages. Awaiting your approval
before build.

## Ground rules (from the phase brief)

- **0-3 SVGs per page.** Not a uniform rollout.
- **No two pages share a visual form.** Each row below names a unique form.
- **Vary the count deliberately.** 7 pages get zero; 21 get one; 1 gets two.
- **Every SVG must reflect a data point or relationship the page already
  states and sources.** No decorative graphics, no new numbers, no visual
  that would need a fresh citation.
- **Inline SVG only.** `viewBox`, no fixed pixel widths; `<title>` and
  `<desc>` for a11y; `currentColor` or CSS-var fills; legible at 360px.

## Count summary

| Bucket | Count | Pages |
|---|---|---|
| 0 SVGs | 7 | about, contact, privacy, terms, calculators (hub), blog (hub), blog/how-to-lower-bmi |
| 1 SVG  | 21 | everything else in the sitemap |
| 2 SVGs | 1 | blog/bmi-formula |
| **Total** | **29** | **23 SVGs across 22 pages** |

## Pages that get zero — and why

| Page | Why zero |
|---|---|
| `/about/` | Personal-bio page. The author photograph is already the human-anchor visual; a data-viz on this page would clash with the identity signal, not add to it. |
| `/contact/` | Utility page (form + email). Nothing data-shaped to visualise. |
| `/privacy/` | Legal boilerplate. A visual here would look decorative and could mislead about what the policy actually says. |
| `/terms/` | Same as `/privacy/`. |
| `/calculators/` | Navigation hub, not a content page. Cards already are the visual affordance. |
| `/blog/` | Same as `/calculators/` &mdash; navigation hub. |
| `/blog/how-to-lower-bmi/` | Lifestyle guidance page. Everything specific enough to draw (weekly weight-loss rate, calorie-deficit magnitude, "gradual over 6-12 months") is exactly the kind of number Phase 10 stripped. The page reads better without a visual than with a hollow one. |

## Pages that get one or two — proposals

Every row names the **form** first (so uniqueness is visible), then the
**relationship** the visual carries, and the **source already on that page**
that the visual traces to. A single sentence sketch explains what the SVG
would look like.

| # | Page | Count | Form | What it shows | Source it traces to | Sketch |
|---|---|---|---|---|---|---|
| 1 | `/` (homepage) | 1 | Annotated horizontal spectrum | The WHO BMI thresholds (18.5, 25, 30, 40) laid out on a single number line 15 &rarr; 45+, with category bands colour-coded and threshold values called out | WHO obesity fact sheet (already linked); page uses WHO categories throughout | A horizontal axis with gradient-tinted bands. Threshold tick lines with numeric labels above; category names below each band. |
| 2 | `/blog/what-is-bmi/` | 1 | Process flow diagram | The end-to-end BMI calculation: `height + weight` &rarr; formula (metric / imperial) &rarr; numeric BMI &rarr; WHO category &rarr; interpretation prompt | Quetelet formula and WHO categories, both cited on the page | Four numbered nodes connected left-to-right with arrows; the middle two nodes carry the metric and imperial equations respectively. |
| 3 | `/blog/bmi-formula/` | **2** | (a) Formula-step derivation | How the imperial `weight-lbs / height-in²` collapses into `× 703` when converted to `weight-kg / height-m²` &mdash; each unit conversion stacked as a step | Quetelet formula, imperial-conversion arithmetic already worked on the page | Chalkboard-style vertical stack of equations; unit factors cross-cancel with strikethrough marks; final line shows the 703 constant. |
|   |   |   | (b) Multi-line curve overlay | Standard BMI (h²) and Trefethen BMI (h^2.5) plotted against height at a fixed weight, showing where the two curves diverge (short vs tall) | Trefethen 2013, cited on the page | Two labelled curves on the same axes; shaded difference between them; annotations on the "short person overestimate" and "tall person underestimate" regions. |
| 4 | `/blog/bmi-history/` | 1 | Horizontal timeline | Key events: Quetelet 1832 &rarr; Ancel Keys 1972 &rarr; WHO adoption 1993/95 &rarr; CDC growth charts 2000 &rarr; latest NHANES cycle (August 2021&ndash;August 2023) | Every event dated and cited on the page already | Horizontal axis with year markers; each event as a labelled tick with a short caption. |
| 5 | `/blog/healthy-bmi-range/` | 1 | Shaded envelope curve | BMI band associated with lowest observed mortality across the adult life course: 18.5&ndash;24.9 for adults 20&ndash;64, widening to the Winter-2014 23&ndash;33 plateau for adults 65+ | Winter et al. 2014 (PMID 24452240), WHO healthy range | X = age, Y = BMI; a translucent green band drawn as a continuous shape that widens after age 65. WHO band shown as a lighter horizontal reference. |
| 6 | `/blog/bmi-categories/` | 1 | Vertical band scale | The WHO adult classification with band heights proportional to their BMI-unit width (Underweight <18.5; Normal 6.4 units; Overweight 5.0; Obese I 5.0; Obese II 5.0; Obese III open-ended) | WHO obesity fact sheet | Vertical column, each band coloured, band height = numeric range. Labels sit outside; the "open-ended" Class III tapers at the top. |
| 7 | `/blog/bmi-chart-explained/` | 1 | 2D nomogram / heatmap | Height (rows) × Weight (columns) grid, each cell coloured by its resulting BMI band; a walk-through showing how to read the intersection | WHO cutoffs already tabulated on the page | Small grid ~6 heights × ~8 weights; cells shaded per WHO band; a dotted crosshair on one example cell showing the "look-up" pattern. |
| 8 | `/blog/bmi-and-health-risks/` | 1 | Qualitative association matrix (dot grid) | Rows = the conditions the page already discusses (CV, T2D, cancer subtypes, sleep apnea, NAFLD, MSK, mental health); columns = WHO categories (Normal, Overweight, Obese); cell = association strength as dot area &mdash; **qualitative only, no numbers** | The page already names each association with an institutional source (WHO, Flegal 2013, NIDDK, ACS, NHLBI); dot size encodes qualitative strength consistent with the prose | Small matrix with row and column labels; dots grow from left to right; a caption states "size indicates qualitative strength as described in the text; no numeric magnitude implied." |
| 9 | `/blog/underweight-bmi-risks/` | 1 | Branching cause-consequence tree | Left = causes named on the page (high metabolism, eating disorders, chronic illness, medication side effects, insufficient intake) &rarr; centre = underweight (BMI <18.5) &rarr; right = risks named on the page (immunity, bone density, fertility, mortality) | The page already lists both cause and consequence sets with attribution | Two clusters of labelled leaves connected through a central node; arrows point right; hairlines only. |
| 10 | `/blog/bmi-limitations/` | 1 | 2×2 tile grid of misclassification archetypes | Four tiles, each showing an edge case the page discusses: muscular athlete, elderly with sarcopenia, tall/short height bias, ethnic body-composition differences. Each tile carries a small sub-diagram and a one-line label | Every archetype is discussed and sourced on the page (ACSM, WHO, Winter 2014, NHLBI) | 2×2 grid of small compositional tiles; icon or micro-diagram inside each; captions below. |
| 11 | `/blog/bmi-and-metabolism/` | 1 | Annotated donut | Total daily energy expenditure split into BMR / activity / thermic effect of food, with the qualitative share of each labelled ("largest share", "variable", "small") | The page discusses these three components with reference to the Katch-McArdle framework and NHLBI general guidance | Donut with three arcs; labels connected by thin leader lines; no percentages inside the arcs since specific numeric shares are not sourced on the page. |
| 12 | `/blog/body-fat-vs-bmi/` | 1 | Paired body silhouettes | Two schematic bodies at the *same* BMI but different body-fat percentages (a "high-muscle low-fat" figure and a "normal-weight-obesity" figure), each with a composition strip beneath | The page already discusses this dichotomy and cites body-composition assessment methods (DEXA, hydrostatic) | Two silhouettes side by side; each has a small horizontal strip below showing fat/lean split; a single BMI value floats between them to hammer the point. |
| 13 | `/blog/bmi-for-athletes/` | 1 | Quadrant scatter with archetype dots | X = body-fat %, Y = BMI; four labelled dots for archetype figures (endurance athlete low BMI low fat; strength athlete high BMI low fat; sedentary average middle both; sedentary high BMI high fat), with WHO cutoff shown as a horizontal reference | The page discusses these archetypes qualitatively with ACSM/NSCA references | 2D scatter with 4 labelled markers; a light dashed horizontal line at BMI 25 and 30 for WHO reference; no other data points. |
| 14 | `/blog/waist-to-height-ratio/` | 1 | Annotated body illustration with tape measure | A schematic torso figure with the correct waist-measurement location marked (at the navel, mid-way between iliac crest and lower rib), a tape-measure ring overlaid, and a callout box showing WHtR = waist/height with the 0.5 threshold | WHO waist-measurement guidance and the WHtR 0.5 threshold, both already on the page | Vector torso outline with a bold band at the correct level; tape-measure graphic wraps that band; a small calculation block sits to the right. |
| 15 | `/blog/bmi-tracking-guide/` | 1 | Time-series with rolling-average overlay | Faint daily-weight points showing normal short-term noise, with a bold weekly-mean line demonstrating the underlying trend | The page already discusses "trend over time beats individual measurements" and short-term water/food noise | X = 8-week timeline, Y = weight (unitless), light dots for daily, a bolder polyline for the weekly rolling mean. |
| 16 | `/women-bmi-calculator/` | 1 | Grouped horizontal ranges (small multiples) | ACOG recommended pregnancy weight gain, four ranges &mdash; one per pre-pregnancy BMI category (underweight, normal, overweight, obese) &mdash; drawn as horizontal spans | ACOG pregnancy weight-gain guidance, already cited on the page | Four horizontal range bars stacked; each labelled with its starting BMI band and the recommended gain span; source line credits ACOG. |
| 17 | `/men-bmi-calculator/` | 1 | Single measurement scale with threshold marker | Waist circumference in inches (or cm), with the NHLBI 40" (102 cm) elevated-risk marker highlighted | NHLBI waist-circumference threshold, already cited on the page | A horizontal ruler-style scale; a bold vertical marker at 40 in / 102 cm; brief note that above the marker corresponds to elevated cardiometabolic risk per NHLBI. |
| 18 | `/age-bmi-calculator/` | 1 | U-shaped mortality curve with shaded plateau | The classic BMI-vs-mortality U-curve, with the flat 23&ndash;33 plateau shaded to correspond to the Winter 2014 finding for adults 65+ | Winter JE et al. 2014 (PMID 24452240), central citation on this page | Smooth U-curve on axes labelled "BMI" and "relative mortality"; the 23&ndash;33 span highlighted; annotations sit outside the plot area. Qualitative &mdash; no numeric mortality scale shown. |
| 19 | `/kids-bmi-calculator/` | 1 | Percentile curve family | The CDC BMI-for-age percentile curves (5th, 10th, 25th, 50th, 75th, 85th, 95th) across ages 2&ndash;19; the 85th and 95th shown with a colour cue so the "overweight" and "obese" thresholds read at a glance | CDC 2000 sex-specific BMI-for-age growth charts, central to this page | Seven smooth curves rising from left to right; the upper two carry emphasised colour; sex-neutral illustration with a caption pointing to the sex-specific CDC charts. |
| 20 | `/new-bmi-calculator/` | 1 | Single-line delta curve | The *difference* between Trefethen and standard BMI at a fixed weight, plotted across height; shows where the two agree (mid-heights, delta near zero) and where they diverge (short: standard reads low; tall: standard reads high) | Trefethen 2013 formula, already cited on the page | X = height, Y = ΔBMI; a single line crossing zero near a "typical" height; shaded above and below the zero-line to emphasise direction of the correction. |
| 21 | `/ideal-weight/` | 1 | Dot plot (formula-comparison strip) | Four dots, one per formula (Devine, Robinson, Miller, Hamwi), plotted on a horizontal "weight" axis for a single reference height (e.g. 5'8" female); shows how much the four formulas agree or disagree | The four formula equations already on the page, with year-and-author attributions | Horizontal axis; four labelled dots close together; a bracket underneath showing the spread; annotation notes that the four are estimates from different eras and populations. |
| 22 | `/lean-body-mass/` | 1 | Stacked horizontal bar (body composition) | A single stacked bar labelled with the components that make up total body mass: skeletal muscle, other lean tissue (bone, organs, water), and fat mass &mdash; each segment labelled but *unquantified* since specific proportions are population-variable and not individually sourced on the page | The page already discusses the fat-vs-LBM concept and references DEXA/BIA measurement categories | Horizontal bar broken into three named segments; sizes are qualitatively suggestive rather than pinned to specific percentages. |

## Notes on forms

- Some visual forms overlap conceptually but are deliberately kept distinct
  in orientation, semantic axis, or annotation style:
  - **Homepage annotated horizontal spectrum** (1) vs **bmi-categories
    vertical band scale** (6): same underlying WHO threshold data, but the
    homepage version is a wide-axis reference strip and the categories page
    is a vertical column with band heights proportional to numeric width.
  - **healthy-bmi-range shaded envelope** (5) vs **age-bmi U-curve** (18):
    both plot BMI against age or on the BMI axis, but the envelope
    highlights a *range* across life stages while the U-curve highlights a
    *risk shape* on a single axis.
  - **bmi-and-health-risks association matrix** (8) vs **bmi-limitations
    2×2 tile grid** (10): both are grids, but the matrix uses dot-area
    encoding for qualitative strength while the tile grid contains four
    self-contained sub-diagrams with captions.
  - **bmi-formula multi-line curve** (3b) vs **new-bmi delta curve** (20):
    (3b) plots both formulas together, (20) plots only the difference
    between them. Different data type.
  - **women-bmi grouped ranges** (16) vs **ideal-weight dot plot** (21):
    (16) shows recommended *ranges* (min-max spans); (21) shows single
    *point* estimates from four formulas.

## Constraints during build (from the phase brief)

- **Accessibility:** every SVG carries `<title>` and `<desc>`. Text
  legible at ≥11 px effective size on a 360 px viewport.
- **Theming:** `currentColor` where feasible; otherwise the site's CSS
  custom properties (`var(--primary)`, `var(--gray-*)`, etc.).
- **No CLS:** explicit `viewBox` with an aspect ratio and no width/height
  attributes that force layout shift.
- **No new numbers:** every value in an SVG must already be sourced on the
  same page. If a value cannot be defended from the page's existing
  citations, it comes out or the visual is redesigned.
- **No rasterisation:** SVG only; no external image requests.

## Phase 11.4 stagger (not part of this plan file, noted for build phase)

At build time I will set each page's `dateModified` and byline
"Last reviewed" to the date of that page's most recent substantive commit
across phases 1&ndash;11, and report the resulting spread. Not doing it
now &mdash; the spread will look different depending on which SVGs you
approve.

## Awaiting your approval

Reply with either a green light, or edits (e.g. "swap #6 to a different
form", "drop the visual on X", "add a second SVG on Y for reason Z"). I
will not build anything until you approve.
