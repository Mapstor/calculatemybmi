# Backlog

Post-Raptive-remediation backlog: nice-to-haves not required for approval, deferred by choice.

## Distinct per-post OG images

All 29 pages currently share the generic `/assets/images/og-image.png` (1200x630). Phase 5.1 repointed 6 per-post URLs that pointed at files that never existed on disk, and filled in 10 pages that had no og:image at all.

Future work:
- Produce distinct 1200x630 OG images for the highest-traffic pages so social shares
  and rich cards stand out. Priority order (highest first):
  1. Homepage (`/`)
  2. `/blog/what-is-bmi/`
  3. `/blog/bmi-categories/`
  4. `/blog/healthy-bmi-range/`
  5. `/blog/bmi-and-health-risks/`
  6. `/women-bmi-calculator/`, `/men-bmi-calculator/`, `/kids-bmi-calculator/`,
     `/age-bmi-calculator/`
  7. Everything else (batch).
- Filename convention when created: `/assets/images/og/<page-slug>.png`.
- Keep `/assets/images/og-image.png` as the fallback for anything not yet given a
  bespoke card.

## Author photo variants

`/assets/images/marko-visic.jpg` and `.webp` are referenced on `/about/`. Consider
producing a smaller (e.g. 160x160) variant for future in-content byline usage — the
current asset is sized for the full about-page hero.

## OG image field completeness

The 10 pages patched in Phase 5.1 all received `og:image` and `twitter:image`. If a
crawler wants richer cards, add `og:image:alt` describing the image (e.g. "BMI
Calculator logo on gradient background") on each page — omitted for now because it
would say the same thing on all 29 pages.
