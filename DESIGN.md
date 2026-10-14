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
- No targets of our own (option B) and no unsourced thresholds; official guidance is attributed and linked.
- `scripts/check_structure.py` runs `js_problems()` on `assets/js/calculator.js`: no emoji or arrow entities, no low-contrast hexes as text colour, no gradients.

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
