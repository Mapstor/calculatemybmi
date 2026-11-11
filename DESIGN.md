---
name: calculatemybmi.net
description: Static health-content and tool site — BMI calculators, body-composition tools, obesity data pages (cyan health theme).
colors:
  primary: "#06b6d4"
  primary-dark: "#0891b2"
  primary-light: "#22d3ee"
  primary-bg: "#ecfeff"
  link: "#0e7490"
  link-hover: "#155e75"
  secondary: "#164e63"
  accent: "#f59e0b"
  underweight: "#3b82f6"
  normal: "#22c55e"
  overweight: "#f59e0b"
  obese: "#ef4444"
  obese-severe: "#991b1b"
  success: "#22c55e"
  success-bg: "#dcfce7"
  warning: "#f59e0b"
  warning-bg: "#fef3c7"
  error: "#ef4444"
  error-bg: "#fee2e2"
  gray-50: "#f9fafb"
  gray-100: "#f3f4f6"
  gray-200: "#e5e7eb"
  gray-300: "#d1d5db"
  gray-400: "#9ca3af"
  gray-500: "#6b7280"
  gray-600: "#4b5563"
  gray-700: "#374151"
  gray-800: "#1f2937"
  gray-900: "#111827"
typography:
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  display:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: "2.25rem"
    fontWeight: 600
    lineHeight: 1.3
  headline:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.3
rounded:
  md: "0.5rem"
  lg: "0.75rem"
  xl: "1rem"
  full: "9999px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.lg}"
    padding: "0 1rem"
    height: "48px"
  card:
    backgroundColor: "#ffffff"
    rounded: "{rounded.xl}"
    padding: "0"
---

# Design System: calculatemybmi.net

## Overview

Cyan health theme on a near-white canvas. Content-first, tool-first — pages lead with the calculator or the data visualisation, then explain. The look is professional-utility: clear hierarchy, generous whitespace around the primary action, no decorative illustration, no motion by default. A single cyan accent carries both brand and interactivity; a muted deep-teal (`--secondary`) owns the header; semantic category colours (blue/green/amber/red) carry BMI classification throughout.

Density is comfortable, not minimalist. The container caps at 1200 px, the calculator card at 720 px, and reading passages at 800 px (`.content-narrow`). On phones (≤ 600 px) multi-column grids collapse to 1–2 columns rather than horizontal scroll. There are no shadows on body prose; depth belongs to interactive surfaces (card, dropdown, button).

**Key Characteristics:**
- Single stylesheet, hand-written tokens (CSS custom properties in `:root`).
- No framework, no Tailwind — class names are descriptive (`.calculator-card`, `.results-grid`, `.faq-item`).
- One cyan accent + one deep teal + semantic category colors; no secondary brand palette.
- System-UI font stack only (`-apple-system, BlinkMacSystemFont, …`); no web fonts loaded.
- Flat body, lifted interactive surfaces. Shadows only on cards, dropdowns and the primary CTA.

## Colors

A tight utility palette: one cyan brand, one deep-teal header, one amber accent, and a locked-in BMI category scale.

### Primary
- **Cyan 500** (`#06b6d4`): brand accent, link hover, calculator CTA fill, focus ring on tool inputs.
- **Cyan 600 — Primary Dark** (`#0891b2`): default link color, border on header-chrome, CTA gradient end.
- **Cyan 400 — Primary Light** (`#22d3ee`): logo mark glyph, hover text in dark header, nav underline.
- **Cyan 50 — Primary Bg** (`#ecfeff`): tint behind active nav items in dropdowns.
- **Cyan 700 — Link** (`#0e7490`, `--link`): text links and accent text on light backgrounds — 5.4:1 on white (WCAG AA). Links on the dark footer stay `--primary-light`. Added in the CMB-006 pilot; `--primary-dark` keeps its other roles (borders, chart fills).
- **Cyan 800 — Link hover** (`#155e75`, `--link-hover`): hover for text links on light backgrounds and for the Calculate button — 7.3:1 on white.
- **Action buttons** (`.calculate-btn` on the calculators, `.aw-cta` on the data-page tools; CMB-007, owner decision 2026-10-12): flat `--link` background, white text (5.4:1), hover `--link-hover`; no gradient, glow or lift. Retired: the cyan gradient (2.4–3.7:1 with white text) and the orange tool-button gradient (3.4:1).
- **Form controls** (buttons, inputs, selects) inherit the body font stack.

### Secondary
- **Deep Teal** (`#164e63`): sticky header background and mobile nav drawer. Used for brand chrome only, never body prose.

### Accent
- **Amber** (`#f59e0b`): warnings, "overweight" category chip, used sparingly.

### Category (semantic — do not retheme)
- **Underweight — Blue 500** (`#3b82f6`)
- **Normal — Green 500** (`#22c55e`)
- **Overweight — Amber 500** (`#f59e0b`)
- **Obese — Red 500** (`#ef4444`)
- **Obese severe — Red 800** (`#991b1b`)
- **Strong shades for white labels** (CMB-010): a bar, segment or step number that carries white text uses `--underweight-strong` `#1d4ed8`, `--normal-strong` `#15803d`, `--overweight-strong` `#b45309`, `--obese-strong` `#b91c1c` (all 5:1 or better with white). Unlabeled bars keep the base colours.
- **Tints for table cells**: category cells use the `/bmi-chart/` tints (under `#dbeafe`, healthy `#d1fae5`, over `#fde68a`, class 1 `#fed7aa`, class 2 `#fecaca`, class 3 `#fca5a5`) with text tinted from the same hue, never grey on colour.

### Status (sparing)
- **Success / Success Bg** (`#22c55e` / `#dcfce7`), **Warning / Warning Bg** (`#f59e0b` / `#fef3c7`), **Error / Error Bg** (`#ef4444` / `#fee2e2`). Used for inline notes, never full-bleed banners.

### Neutral
- **Gray 50–900** (`#f9fafb` → `#111827`): body background `--gray-50`, body text `--gray-800`, headings `--gray-900`, muted body `--gray-600`, borders `--gray-200`/`--gray-300`.

### Named Rules
**The One Cyan Rule.** The brand accent appears on exactly one interactive surface per page section — the CTA, the active nav underline, or a highlighted chart series. Doubling up turns the page into a toy.

**The Category Lock.** The five BMI colors (blue / green / amber / red / dark red) are the only reliable visual metadata on the site. Never retheme them for a one-off chart.

## Typography

**Font:** system UI stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`). No web fonts.

**Character:** sans only, semibold for headings, regular for body. The point is zero font loading cost and native-OS legibility on phones.

### Hierarchy
- **H1** (`font-weight: 600`, `font-size: 2.25rem`, `line-height: 1.3`): one per page, page-topic.
- **H2** (`font-weight: 600`, `font-size: 1.5rem`, `line-height: 1.3`, `margin-top: 2rem`): section headings.
- **H3** (`font-weight: 600`, `line-height: 1.3`): sub-section (size inherits from H3 default).
- **Body** (`font-size: 16px`, `line-height: 1.6`, `color: var(--gray-800)`): the baseline — reading column maxes at 800 px via `.content-narrow`.
- **Intro text** (`font-size: 1.125rem`, `color: var(--gray-600)`, `max-width: 700px`): page lede under H1.
- **Label / tiny** (uppercase, `font-size: 0.6875rem`, `letter-spacing: 0.05em`, `color: rgba(255,255,255,0.4)`): mobile-nav section headers; the only uppercase typography on the site.

### Named Rules
**The Native Stack Rule.** No web fonts, ever. Load time matters more than typographic range on a Raptive ad site.

## Layout

- **Container**: `.container` — `max-width: 1200px`, `padding: 0 1rem`, centered.
- **Reading column**: `.content-narrow` — `max-width: 800px`, centered. Prose and FAQ live here.
- **Reading layout (D-14)**: `main.reading` keeps every block in one 680 px column. Inside it, the key-takeaways answer and bullets stop at `34rem`, about 75 characters a line at 15 px (CMB-013).
- **Guide pages (CMB-013, `/blog/healthy-bmi-range/`)**: page head (H1, byline, up to three `.intro-text` paragraphs: pain, stakes, promise) → `.key-takeaways` (`p.answer` of 40–60 words, then bullets) → `.disclaimer-box` → hero `figure.figure` → `.toc-inline` → `section.content-section.flow` blocks → flat FAQ → sources and method → one `.related-cols` block. SVG text is 12 px or larger in viewBox units.
- **Calculator card**: `.calculator-card` — `max-width: 720px`, centered, white, radius `--radius-xl` (1rem), shadow `--shadow-lg`.
- **Main padding**: `main { padding: 2rem 0 3rem; }` with `overflow-wrap: break-word` so long sourced URLs can wrap on phones (added F1).
- **Grids**: `.results-grid`, `.results-grid-3`, `.results-grid-4`, `.form-row`, `.form-row-3`, `.footer-grid`, `.tips-grid`, `.pros-cons` — CSS Grid, column counts tuned per widget.
- **Breakpoints**: `768px` (nav collapses to the hamburger drawer, footer grid 1fr 1fr), `600px` (form rows and most result grids collapse to 1-2 columns), `480px` (footer collapses to one column).
- **Header**: `.header` is `position: sticky; top: 0; z-index: 100`, deep-teal; dropdowns rendered on hover with a white card and a chevron caret.
- **Z-index**: header 100, nav dropdown 200. Keep ad containers below 100.

## Elevation & Depth

Mostly flat. Depth lives in three places:
- **Card** (`.calculator-card`, `.nav-dropdown-menu`): `box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1)` (`--shadow-lg`).
- **Elevated grid cells** (where used): `box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1)` (`--shadow-md`).
- **Primary CTA** (`.calculate-btn`): color-tinted shadow `0 4px 14px 0 rgba(6, 182, 212, 0.4)`, lifts to `0 6px 20px 0 rgba(6, 182, 212, 0.5)` with `transform: translateY(-2px)` on hover.

### Named Rules
**The Lift-On-Intent Rule.** Only interactive surfaces lift. Static content never has a shadow.

## Shapes

Rounded, not pill-y:
- `--radius-md: 0.5rem` — form inputs, nav-mobile links.
- `--radius-lg: 0.75rem` — buttons, dropdown cards, result tiles.
- `--radius-xl: 1rem` — the calculator card.
- `--radius-full: 9999px` — chips and category badges only.

No sharp corners (0 radius) and no custom clip-paths. Borders are hairline (`1px solid var(--gray-200)` or `--gray-300`); the header's bottom border is `1px solid var(--primary-dark)` on `--secondary`.

## Components

### Primary CTA — `.calculate-btn` and `.cta-button`
- `.calculate-btn` (calculators): full-width `height: 48px`, flat `--link` background, white text (5.4:1), hover `--link-hover`; no gradient, glow or lift (D-13).
- `.cta-button` (links that act as buttons, CMB-010): the same flat `--link` treatment, `min-height: 48px`, radius `--radius-lg`; `.cta-button--sm` is 40 px for in-card actions. Inline-styled button links are not allowed (check_structure fails them).

### Nav — desktop
- Deep-teal bar, white logo, 0.9375 rem semibold links with `rgba(255,255,255,0.8)` default and white at active/hover; active state uses a 2 px `--primary-light` underline.
- Dropdowns are white cards (`.nav-dropdown-menu`) with a chevron, `min-width: 240px`, radius `--radius-lg`, show on hover.

### Nav — mobile
- `@media (max-width: 768px)`: desktop nav hides, 44×44 toggle appears, drawer slides down as a `--secondary` panel with grouped sections (`.nav-mobile-section` tiny uppercase label + links). Minimum tap target 44 px.

### Calculator card — `.calculator-card`
- White, max-width 720 px, radius `--radius-xl`, shadow `--shadow-lg`, `overflow: hidden` so inner tabs/toggles don't poke the corners.

### Forms
- `.form-row` / `.form-row-3` grids; inputs use `--radius-md`, `--gray-300` border, cyan focus (via `calculator.js` theme).
- Pill toggles (sex, units) are the preferred control over native radios on tool pages; the Average Weight v2 and Body Fat Calculator pages establish the pattern.

### Result tiles & charts
- Grids (`.results-grid`, `.results-grid-3`, `.results-grid-4`) of flat tiles on `--gray-50`; labels `--gray-600` at 0.75 rem. The main tile may span the row on phones (`.result-item--wide`).
- Charts are inline SVG or plain CSS, no library; label-collision is checked geometrically before shipping (see A2/B1 widget tests).

### Calculator results — answer first (CMB-011)
- Result card: flat category tint (`#eff6ff`, `#ecfdf5`, `#fffbeb`, `#fef2f2`), no border or gradient. The BMI number takes the strong shade (4.7:1 or more on its tint); the category name is `--gray-900`.
- Scale segments use the strong shades with white 0.75 rem labels (5:1 or more).
- Extended results (`.er`) are flat sections divided by hairlines, never cards inside the calculator card. Order: what the result means, in plain sentences → the visual → tables → more numbers → links.
- Section headings in sentence case. Numbers right-aligned with tabular figures (`.er-num`); the other unit sits under the value (`.er-alt`).
- Category colour only on dots and on BMI values (strong shades from `catColor()`); differences, labels and notes stay neutral. The user's row gets `.er-active` and a "You" pill (`.er-you`), never an arrow glyph.
- Every weight shows in the unit the user entered first and the other unit second, ideal weight and lean mass included. Metric input is computed in kg/m², US input with 703; the healthy kg limits follow kg/m².
- The converted unit has one decimal both ways ("159 lbs (72.1 kg)", "72 kg (158.7 lbs)"), so a converted limit never rounds across a category line (CMB-012; whole-pound rounding showed 72 kg at 170 cm as 159 lbs, which is BMI 25.0).
- US rank (`.rank-box`, homepage and men page): "higher than X%" counts only adults with a lower BMI and "lower than Y%" only those with a higher one. NHANES records BMI to one decimal, so the curve is read at BMI − 0.1 for X; adults with the same BMI count on neither side (CMB-012).
- No targets of our own (option B) and no unsourced thresholds; official guidance is attributed and linked.
- `scripts/check_structure.py` runs `js_problems()` on `assets/js/calculator.js`: no emoji or arrow entities, no low-contrast hexes as text colour, no gradients.

### Category dots in data tables — `.cat-dot` (CMB-012)
- A 10 px dot before the category name in a static table (`<span class="cat-dot normal">`), in the strong shades. The category colour sits on the dot only; the text stays `--gray-800`.

### Weight-by-height chart tables — `.weight-chart` (CMB-014)
- The chart table on D-14 chart pages (first `/blog/bmi-chart-women/`): one row per height with a `#h-5-4` id, one column per CDC category, pounds with kilograms below (`.cell-kg`), centimeters under the height (`.cell-cm`). Cells use the category tints with text from the same hue (`.c-under` … `.c-ob3`, 5.2:1 or better); white hairlines between cells; the height column stays put while the table scrolls sideways; a targeted row gets a 3 px `--link` bar. `min-width: 600px`, inside `.table-responsive`; headers wrap.
- A printable chart image goes in `figure.figure.figure--wide` (680 px) as an `<img>` with width and height, linked to the full-size file, so search engines can index it.
- Cells keep 8 px (0.5rem) beside the text. `.th-sub`, the muted second line, also works in `.data-table` row headers (CMB-015, the US adults table on `/bmi-chart/`).

### Images in search results (CMB-015)
- Every page carries `<meta name="robots" content="max-image-preview:large">`, which lets Google show a large image preview (and is required for large images in Discover).
- Each D-14 page names a **preferred image**: its own figure redrawn with no words, numbers or logo (Google: avoid a generic image such as a logo, and images with text), in 16:9 (1200 × 675), 4:3 (1200 × 900) and 1:1 (1200 × 1200), drawn by `research/preferred-images/pref_images.py` into `assets/images/preferred/<name>-<ratio>.png`. The 16:9 file is `og:image` and `twitter:image` (`og:image:width` 1200, `og:image:height` 675); the main entity's JSON-LD `image` lists the 1:1, 4:3 and 16:9 files; a `WebPage` `primaryImageOfPage` names the 16:9 file. Keep wide margins so any crop holds the whole picture.
- A figure meant for image results goes in an `<img>` (inline SVG and CSS backgrounds are not indexed as images) with alt text, width and height, next to the text it illustrates, and is listed under its page in `sitemap.xml` (`<image:image>`).
- `scripts/check_images.py`, run by `check_structure.py`, enforces all three. A rebuild adds its page to `PREFERRED` there.

### Body fat rank tool and lookup tables (CMB-016)
- `/body-fat-percentage-chart/` ranks a body fat reading with the shared calculator parts, not a page-level style: `.calculator-card.bfr` › `.calc-panel` › `.unit-toggle` (Woman / Man, `aria-pressed`) › `.form-row` with two `.form-input`s (body fat %, age) › `.calculate-btn`. Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the provisional range, the share in a neutral `.bmi-value` (a share is not a BMI, so no category colour on the number), then `.er-section`s with `h3` headings (the tool sits inside a section that has its own `h2`), a `.cat-dot` on the range line, and a compact percentile `.data-table`.
- Shares of US adults never print as 100% or 0%: 99.5% or more reads “more than 99%”, 0.5% or less “under 1%”. A reading equal to the row counts on neither side, as in the US rank rule.
- Narrow chart tables (three columns) use `.weight-chart.weight-chart--fit` (no 600 px minimum, so they fit a phone); the provisional range shows as the cell tint and as a second line (`.cell-kg`), so colour never carries it alone.
- Women and men as chart series: `#be185d` and `#4338ca` (dataviz validator, light mode: CVD ΔE 18.3, normal-vision ΔE 29.3, both 3:1 or more on white); the middle half as the same hue at 16% opacity. The category colours stay for categories.

### Waist field and result boxes (CMB-017)
- `/women-bmi-calculator/` adds an optional waist input to the shared calculator: a `.form-input.waist-in` beside the weight in the imperial row and a `.form-input.waist-cm` in the metric row, labeled "Waist (inches)" / "Waist (cm)", empty with the placeholder "Optional". `calculator.js` reads only the height and weight classes, so the field changes nothing there.
- After Calculate the page script fills up to three flat boxes below the status line, each a `.rank-box` (hairline above, `.rank-title`, `.rank-text`, `.rank-source`; no card): the rank among US women (all and by age group), "US women with a BMI like yours" (body fat at that whole BMI, waist shares for that category) and, only when a waist is entered, the waist check. A box with nothing to say stays hidden.
- The waist check compares what it prints. The waist is rounded to 0.1 in or 0.1 cm and the ratio is worked out from that printed waist, then cut (not rounded) to two decimals, so 0.50 always means a waist of at least half the height (0.4953 shows as 0.49). The BMI is the one the result card shows. The US-guidelines line compares in the unit the user entered and names only that unit (over 35 in, or over 88 cm). The ADA sentences quote the waist in cm against 88 cm, the unit the standard uses. When the answer for women of Asian background differs, the first ADA sentence says "for women of non-Asian background" and the Asian sentence follows. The source line says these are published thresholds applied to the numbers entered, not a diagnosis. Shares of US women follow the CMB-016 rule ("more than 99%", "under 1%").

### Distributions over the chart (CMB-018)
- A chart figure can carry where real people fall on it: on `/blog/bmi-chart-men/` each height row shows the CDC categories as the light table tints, a 6 px bar in the series color (men `#4338ca`) for the middle half of US men of that height, and a 3 px ink tick (`#111827`) for the median. Tints stay light so the bar and tick read on every band.
- Box plots for one measure across categories: the 10th-90th percentile as a 1.5 px line, the middle half as a box in the series color at 16% opacity with a 1 px outline, the median as an ink tick; a dashed grey line marks a reference value, named in the figure. Row labels sit above their box, so values never collide with the marks.

### Average weight tool (CMB-019)
- `/average-weight/` compares a height, and an optional weight and age group, with US adults of the same sex, using the shared calculator parts and no page-level style: `.calculator-card.awt` › `.calc-panel` › two `.unit-toggle`s (Woman / Man; ft, in, lb / cm, kg; `aria-pressed`) › `.form-row.form-row--pair` rows (feet and inches, or cm; weight and age group) › `.calculate-btn`. The card follows its `.content-section`, never inside it.
- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the BMI category when a weight is entered (neutral without one), with the share of people measured at that height or an inch either side (heights rounded to the nearest inch) who weigh less, or the average at that height, in a neutral `.bmi-value`; then `.er-section`s with `h3` headings: where you fall (the CMB-018 box plot: 10th-90th percentile line, middle half in the series colour at 16%, the average as an ink tick, the healthy range as a green bar, the weight entered as a dashed ink line labelled "You"), your BMI with a `.cat-dot`, the age group's average, the height rank, and the source line. The figure is drawn in the unit entered (kg ticks every 10 or 20, lb every 20 or 40); weights print in that unit first.
- A height with fewer than 30 people measured gets no average: the card says so and gives the national average and the healthy range instead. Shares follow the CMB-016 rule ("more than 99%", "under 1%").
- By-height tables (`.data-table` in a `.flow` section): one row per inch with an id (`#women-5-4`, `#men-5-9`), centimeters under the height (`.th-sub`), kilograms under the average (`.cell-kg`), a † on heights with fewer than 60 people measured, explained in the source note.

### Body fat calculator (CMB-020)
- `/body-fat-calculator/` estimates body fat four ways with the shared calculator parts and no page-level style: `.calculator-card.bfc` › `.calc-panel` › `.bfc-toggles` (two `.unit-toggle`s side by side, Woman / Man and US / Metric, stacked under 360 px) › a four-way `.unit-toggle.unit-toggle--methods` (Tape measure, Waist and height, Height and weight, Calipers; two rows on phones) › `.form-row.form-row--pair` rows for the height and for weight and age › one `.bfc-pane` per method (`.form-row.form-row--trio` puts three measurements in a row, two under 360 px; a `.form-hint` says where to measure; calipers add a 3 sites / 7 sites toggle) › `.calculate-btn`. Panes and rows hide with the `hidden` attribute (`.bfc [hidden]`).
- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the provisional range (neutral under 20) with the estimate in a neutral `.bmi-value`, then `.er-section`s with `h2` headings (the card sits under the H1): how close the estimate is likely to be (for relative fat mass and the Deurenberg formula, the middle half and median of CDC's scans in people whose formula gave an estimate within a point of the same whole percent; for the tape and calipers, the published DXA comparison), where the estimate falls (the CMB-016 figure and notes), fat and lean mass when a weight is entered, the other estimates the entered numbers allow (an `.er-table`, the method shown above as `.er-active` with an `.er-you` pill), and the source line.
- Every result comes from the printed estimate (0.1, halves up): its range, its US share, its calibration window and the fat mass. A method pane's starting values belong to the worked example, so a pane joins "Your other estimates" only after the user types in it; the height-and-weight formula joins whenever a weight is entered.
- The notes say what each check can and can't tell: trained technicians took CDC's measurements (measuring yourself adds error), and the US share and the range treat the estimate as a scan reading, so they are only as close as it.
- The US / Metric switch converts every length and the weight to 0.1; switching back with nothing retyped restores the numbers as they were, so flipping units never changes a result.

### Tables with long row labels (CMB-021)
- `.data-table--wrap` lets a table's row labels (`th[scope="row"]`, which `.flow` tables keep on one line) wrap. Use it with `.data-table--fit` where the labels are names of several words (methods, measuring slips), so a three-column table fits a 320 px phone; numbers stay on one line.
- Groups inside such a table are `tbody` elements, each led by a `th[scope="rowgroup"][colspan]` row (`/blog/how-to-measure-body-fat/`, the measuring-slip table).

### US obesity tool and embed code (CMB-022)
- `/us-obesity-statistics/` puts "Where do you fit?" on the shared calculator parts, with no page-level style: `.calculator-card.obw` › `.calc-panel` › `.unit-toggle` (ft, in, lb / cm, kg; `aria-pressed`) › one `.form-row.form-row--trio` (feet, inches, pounds; two columns under 360 px) or one `.form-row.form-row--pair` (centimeters, kilograms) › `.calculate-btn`. The card follows its `.content-section`; rows hide with the `hidden` attribute (`.obw [hidden]`).
- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the CDC category with the BMI in the strong shade, the category, and its share of US adults with the count; then an `.er-section` with an `h3` and an `.er-table` of the six categories (`.cat-dot`, share, adults) where the user's row is `.er-active` with an `.er-you` pill. The BMI is rounded once to 0.1 (as `calculator.js`); the unit switch converts to 0.1 and restores the entered numbers when switched back with nothing retyped (the CMB-020 rule).
- Embed code for a chart others may reuse: a read-only `textarea.embed-code` (system monospace, `--gray-50` ground, hairline border, resizable) under a `.form-label`, and a `button.cta-button.cta-button--sm` that copies it. `button.cta-button` drops the browser's button border.
- Four-column number tables (`.data-table--fit.data-table--wrap`) fit a 320 px phone: under 360 px their cells keep 4 px beside the text (group heading rows keep 8 px), and a long single-word column heading carries a soft hyphen (`Over&shy;weight`) so it can break.

### New BMI page (CMB-023)
- `/new-bmi-calculator/` runs the shared calculator (`calculator.js`, every `newbmi-` id kept) with no inline style in `<main>` outside its figure. The US row is one `.form-row.form-row--trio` (feet, inches, pounds, labels "Height (ft)", "Height (in)", "Weight (lb)" so the three boxes stay level; two columns under 360 px), which keeps Calculate above the fold at 360 px under a four-line H1; the metric row is one `.form-row.form-row--pair` that starts with the `hidden` attribute. `styles.css`: `.calc-panel [hidden] { display: none; }` (`.form-row` sets `display: grid`; the unit toggle then sets the display inline, which wins) and `.weight-range-box p` takes the line's size (the other calculators' inline styles say the same).
- Results: the answer-first card and scale (segments Under, Healthy, Over, Class 1, Class 2+, never "Normal" or "Obese"), then two `.er-section`s with `h2`s: "New BMI and traditional BMI" (two tiles, then Difference and Category as `.result-item--wide`, so the category sentence gets a full row on phones) and "Healthy weight at your height" (an `.er-note` naming CDC's range on traditional BMI, the tiles and the weight-difference line).
- Number tables group rows by height with a `th[scope="rowgroup"][colspan]` heading, weights as row headers with the kilograms in `.th-sub`; a † on a row marks a category change and a `.source-note` under the table names the categories. Formula cells keep each side of a division together with no-break spaces, so they break only before ÷; equations in prose sit in `.nowrap`; a number keeps its unit with a no-break space.
- The figure is a difference line in `--link` (`#0e7490`) on a `#4b5563` zero line, with no grid lines inside the plot so its three labels sit clear of every line; the crossing is an open dot, axis labels are 12 units in a 320-wide viewBox, heights first and metres under them.

### Ideal weight page (CMB-028)
- `/ideal-weight/` runs the shared calculator (`calculateIdealWeight()` and `displayIdealWeightResults()` in `calculator.js`; every `ideal-` id kept except `ideal-average`) with no inline style in `<main>` outside its figure. Feet and inches share a `.form-row.form-row--pair`; sex and frame (label "Body frame (changes Hamwi only)") share a plain `.form-row`, stacked on phones so the long label stays on one line and both selects stay level; the metric row starts `hidden`.
- Results: a `.results-grid` with the span tile ("The four formulas", `#ideal-span`, the lowest to the highest of the four as printed) and the healthy BMI range, both `.result-item--wide`, then a `.results-grid.results-grid-4` with Hamwi, Devine, Robinson and Miller in date order. Under 5 feet the four formula tiles and the span tile say the formulas start at 5 feet (152.4 cm). The extended results keep the CMB-011 order; notes run as short `.er-note`s, so no paragraph sets two lines past 80 characters at desktop width.
- Number tables with six columns (height, four formulas, a range) take `.data-table--fit.data-table--tight.data-table--small-head`: below 400 px the cells keep 4 px beside the text; below 440 px the column headings take the tiny label size (0.6875rem) and sit on the header row's last line, so "Healthy BMI range" wraps between its words onto two lines and every heading ends right above its numbers; below 380 px the heading cells keep 2 px beside the text. No heading carries a soft hyphen: Hamwi, Devine, Robinson and Miller never break, the by-height tables fit every phone from 360 px up, and they scroll inside their frame only below that (CMB-031). Desktop headings are unchanged.
- The figure: two panels on one weight axis and one inches-to-width scale (women 5′0″ to 6′0″, men 5′0″ to 6′6″), the healthy band in the healthy tint `#d1fae5`, the four formulas as 2-unit lines in ink `#111827` (Hamwi), pink-700 `#be185d` dashed (Devine), cyan-600 `#0891b2` (Robinson) and amber-700 `#b45309` dotted (Miller), the dashed lines drawn on top so a line under one shows through its gaps; the legend sits above the panels; one invisible column per inch carries a `<title>` with the four weights and the healthy range for hover. In this order every neighbouring pair passes the dataviz validator for colour-blind and normal vision; ink fails only its gray-chroma check, which the dashes and the legend cover.

### Kids BMI page (CMB-030)
- `/kids-bmi-calculator/` runs the shared calculator (`calculator.js`, every `kids-` id and starting value kept) with no inline style in `<main>` outside its figure. Feet, inches and pounds share a `.form-row.form-row--trio` (two columns under 360 px); the metric row (`.form-row--pair`, cm and kg) starts `hidden`; age in years, age in months and sex share a second `.form-row--trio`, with the sex options reading Girl and Boy (values `female` and `male`) so the select fits its 98 px column at 390 px. Calculate ends at 710 px at 390 × 844 and at 755 px at 360.
- Results: the lines under the category are `.bmi-range` (the percentile line, `#kids-percentile-note`). For severe obesity, `displayKidsResults()` adds `#kids-aap-class` (`.bmi-range`) directly under the category name with the American Academy of Pediatrics' class (2, or 3 at 140% of the 95th or BMI 40); the category name stays CDC's "Severe obesity".
- Tables: the category table is `.data-table--fit` with a `.cat-dot` in each row header; the birthday tables (age, 5th, 50th, 85th, 95th, 120% of 95th) are `.data-table--fit.data-table--tight` and fit a 360 px phone. Their source line starts "Source:" and links CDC's data file, which is how the Stage 1 audit finds a table's source.
- The figure: two panels (boys, girls) on one BMI axis (12 to 36) and one age scale (2 to 20), the five CDC categories as bands in the tints the `/bmi-chart/` figure uses (underweight `#dbeafe`, healthy `#d1fae5`, overweight `#fde68a`, obesity `#fecaca`, severe obesity `#fca5a5`), 1.5-unit white gaps along the band edges (the 5th, 85th and 95th percentiles and 120% of the 95th or BMI 35, whichever is lower), grid hairlines in ink at 12% over the tints, and the legend above the panels in the `/bmi-chart/` swatch style (12-unit squares with a `#9ca3af` outline). One invisible column per year of age carries a `<title>` with that birthday's cut-offs. The dataviz validator fails these tints as a categorical palette (blue-100 against green-100 is ΔE 4.8 for deuteranopes), so identity never rests on colour: the white gaps, the fixed bottom-to-top order, the legend and the tables under the figure carry it.

### Category badges
- Pill (`--radius-full`), category background with white text (BMI color lock applies).

### Cards inside a section
- A `.content-section` is the card. Related cards (`.blog-card`) and FAQ items inside it render flat, divided by hairlines (CMB-010), as on the men page. Never a card inside a card.
- Outside links to sources use `.resource-list` (link plus one muted line), not tiles.

### Icons
- No emoji or Unicode pictographs as icons, in page copy or in calculator results (CMB-010; check_structure fails them).

### FAQ — `.faq-item`
- Site-native accordion. Visible answer must stay in sync with the FAQPage JSON-LD — DEVLOG §4 trap: re-run `research/f1/verify.py` after any FAQ change.

### Footer
- Dark footer with 3-column `.footer-grid` (collapses to 1fr 1fr at 768 px, 1fr at 480 px).

## Do's and Don'ts

### Do:
- **Do** keep every page under one `.container` and use `.content-narrow` for prose columns.
- **Do** place one primary CTA per decision point and give it `.calculate-btn` (a button) or `.cta-button` (a link); flat `--link`, no gradient or shadow (D-13).
- **Do** honor the BMI category lock (blue / green / amber / red / dark red) in every chart that classifies BMI.
- **Do** collapse multi-column grids to 1-2 columns at ≤ 600 px, not horizontal scroll.
- **Do** test any new widget at 390 px and 1280 px before shipping (D-09).

### Don't:
- **Don't** load a web font, add motion, or import a UI framework. The native stack and the one cyan accent are the brand.
- **Don't** retheme the semantic category colors for a one-off visual.
- **Don't** change the header color, logo mark, or ad-container markup — Raptive owns ad surfaces and the CMP (D-05).
- **Don't** add shadows to body prose or static cards; shadows signal interactivity.
- **Don't** publish layout as "done" from the box — mark it `unverified` and route to Marko's Mac 2 check (CLAUDE.md R4).
