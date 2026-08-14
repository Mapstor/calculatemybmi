# Phase 13 — Quality Audit

Findings + applied fixes. Companion file: `EXTERNAL-LINKS.md`.

---

## 13.1 Hub descriptions — APPLIED

**`/blog/` hub** &mdash; 24 card descriptions rewritten across six sections. Rule check:

- Length varies: 9 single-sentence, 5 two-sentence, 2 three-sentence (across the 15 unique blog pages).
- Every card names something specific: the exact question answered ("Answers 'what does BMI stand for'"), the named visual (percentile curve, dot matrix, U-curve), the named citation (Winter 2014, ACOG, NHLBI, WHO Western Pacific), or the specific artefact (703 constant, 40-inch waist marker, adiposity rebound).
- 15 distinct opening constructions across the 15 pages: Answers, Two visuals, From Quetelet's, Why the healthy, The eight, Colour-coded, Association matrix, Cause-to-consequence, Four archetype, Donut of, Two silhouettes, Scatter plot, Tape-measure, Time-series, Evidence-based.
- Related-calculator cards on the hub also rewritten with specific detail (ACOG 28-40/25-35/15-25/11-20 lbs bands named; NHLBI 40-inch waist; Winter 2014 23-33 plateau; CDC growth-chart median curves; four ideal-weight formulas by year and author; Trefethen 2013 height^2.5 delta).

**`/calculators/` hub** &mdash; 8 calculator-card descriptions rewritten with the same variance rule. Length: 4 two-sentence, 4 single-sentence. Openings: The classic, Adds life-stage, Male-specific, Uses the WHO, Percentile-based, Uses the 2013, Four formulas, Splits total.

Additional fix applied on `/calculators/` while there: the "BMI by Age" card's Example block previously read "recommended range for seniors (23-28)" and "where a slightly higher BMI is protective." Both contradicted the Phase 10.2 Winter 2014 alignment. Corrected to "observed lower-mortality band for adults 65+ (23-33 in Winter 2014)" and "per the Winter 2014 meta-analysis."

## 13.2 Per-page OG images — APPLIED

**Rasterizer:** `sharp` (Node.js, v0.34+, installed via `npm install sharp` into `/tmp/node_modules/`). The libraries in your list (sharp / resvg / cairosvg / Playwright) &mdash; sharp was installable and works with the SVG tokens my Phase 11 SVGs use. `cairosvg` failed (no pip), `librsvg2-bin` failed (no sudo). ImageMagick is installed but its SVG renderer struggles with SVG text (Phase 6.1 evidence). Sharp is the honest choice here.

**Delivery:** 25 PNGs at exactly 1200x630 in `/workspace/assets/images/og/` &mdash; one per Phase 11 SVG. Each rendered on a light `#f8fafc` canvas with a 90px teal header band carrying the page title (helps when the diagram alone is ambiguous), plus a bottom-right `CalculateMyBMI` wordmark. File sizes 44-136 KB.

**Wiring:** 21 pages that carry a Phase 11 SVG now have their PRIMARY OG PNG wired as `og:image`, `twitter:image`, and Article/WebPage schema `image`, with `og:image:width` / `og:image:height` meta added where missing. When a page has multiple SVGs (kids-bmi-calculator has 3, bmi-formula has 2, lean-body-mass has 2), the most visually distinctive one was picked as the primary; the additional PNGs sit in `/assets/images/og/` for later use (SEO image sitemap or a "gallery" if you build one).

**8 pages keeping the generic `og-image.png`** (unchanged):

| Page | Why generic |
|---|---|
| `/index.html` | Homepage — no Phase 11 SVG (dropped per Phase 11 E2 audit: existing BMI Classification Table + BMI Chart already carry the WHO thresholds) |
| `/about/` | Bio page; author photo already carries identity |
| `/contact/` | Utility page |
| `/privacy/` | Legal page |
| `/terms/` | Legal page |
| `/calculators/` | Navigation hub |
| `/blog/` | Navigation hub |
| `/blog/how-to-lower-bmi/` | Lifestyle guide; no visual added in Phase 11 (Tier B stripped its numeric figures) |

**Verification:** every `og:image` / `twitter:image` / schema `image` URL sitewide resolves to an existing file. Zero missing images. All URLs are absolute apex form (`https://calculatemybmi.net/assets/images/og/*.png`).

## 13.3 Thin-page audit — REPORT ONLY

Rendered word count excludes nav, footer, script, style, and SVG content. Utility pages listed but not flagged as "thin."

| Page | Words | H2/H3 | Visual | Verdict |
|---|---:|:-:|:-:|---|
| `/index.html` | 4,520 | 12/25 | ✓ | substantial |
| `/about/` | 2,229 | 10/28 | ✓ | substantial |
| `/contact/` | 313 | 4/0 | ✓ | utility |
| `/privacy/` | 1,450 | 12/6 | ✓ | utility |
| `/terms/` | 2,791 | 16/2 | ✓ | utility |
| `/calculators/` | 2,378 | 17/6 | ✓ | utility |
| `/blog/` | 625 | 7/0 | ‐ | utility |
| `/blog/what-is-bmi/` | 3,049 | 13/36 | ✓ | substantial |
| `/blog/bmi-formula/` | 3,058 | 14/23 | ✓ | substantial |
| `/blog/bmi-history/` | 3,799 | 14/19 | ✓ | substantial |
| `/blog/healthy-bmi-range/` | 3,239 | 15/10 | ✓ | substantial |
| `/blog/bmi-categories/` | 4,015 | 19/15 | ✓ | substantial |
| `/blog/bmi-chart-explained/` | 3,687 | 14/13 | ✓ | substantial |
| `/blog/bmi-and-health-risks/` | 3,973 | 18/23 | ✓ | substantial |
| `/blog/underweight-bmi-risks/` | 2,899 | 9/15 | ✓ | substantial |
| `/blog/bmi-limitations/` | 2,884 | 14/3 | ✓ | substantial |
| `/blog/bmi-and-metabolism/` | 3,414 | 12/14 | ✓ | substantial |
| `/blog/body-fat-vs-bmi/` | 3,075 | 12/14 | ✓ | substantial |
| `/blog/bmi-for-athletes/` | 3,564 | 11/29 | ✓ | substantial |
| `/blog/waist-to-height-ratio/` | 2,798 | 12/10 | ✓ | substantial |
| `/blog/how-to-lower-bmi/` | 3,613 | 11/20 | ✓ | substantial |
| `/blog/bmi-tracking-guide/` | 3,211 | 14/20 | ✓ | substantial |
| `/women-bmi-calculator/` | 3,448 | 11/26 | ✓ | substantial |
| `/men-bmi-calculator/` | 3,818 | 11/30 | ✓ | substantial |
| `/age-bmi-calculator/` | 4,717 | 10/35 | ✓ | substantial |
| `/kids-bmi-calculator/` | 6,056 | 11/37 | ✓ | substantial |
| `/new-bmi-calculator/` | 4,017 | 10/31 | ✓ | substantial |
| `/ideal-weight/` | 4,701 | 10/39 | ✓ | substantial |
| `/lean-body-mass/` | 4,847 | 11/35 | ✓ | substantial |

**Content pages under 800 rendered words:** 0. Every content page is 2,229 words or more. No padding needed anywhere.

**Utility pages flagged separately:** `/contact/` (313 words, form-heavy), `/privacy/` (1,450), `/terms/` (2,791), `/calculators/` (2,378), `/blog/` (625). These are navigation/legal/form pages where brevity is appropriate.

## 13.4 Link integrity — REPORT ONLY

### Internal — broken links

**2 false positives** on the audit script's URL normaliser:

- `/privacy/` and `/terms/` each contain `https://calculatemybmi.net` (apex, no trailing slash) as an absolute self-reference in the data-controller callout box. The normaliser mangled this to `//`. Both actually resolve to the homepage in a browser. Not a real bug.

**0 real broken internal links.**

### Internal — links to redirected slugs

**0.** Every previously-redirected slug (`bmi-calculator-guide`, `bmi-chart-women`, `ideal-weight-calculator`, etc.) has zero remaining internal `href` references. The Phase 4.4 sweep + Phase 4.4 vercel-json remain complete after all subsequent phases.

### Internal — missing anchor fragments

**9 hits.** All the same pattern: 3 blog articles (`/blog/bmi-categories/`, `/blog/bmi-formula/`, `/blog/healthy-bmi-range/`) link to `/#panel-women`, `/#panel-men`, and `/#panel-ideal` &mdash; anchors that used to be tab panel ids on a tabbed-calculator homepage. The current homepage only has `#panel-standard`; the other panels have moved to their own dedicated calculator pages (`/women-bmi-calculator/`, `/men-bmi-calculator/`, `/ideal-weight/`).

Every occurrence per file:

| Page | Broken anchor href |
|---|---|
| `/blog/bmi-categories/` | `/#panel-women`, `/#panel-men`, `/#panel-ideal` |
| `/blog/bmi-formula/` | `/#panel-women`, `/#panel-men`, `/#panel-ideal` |
| `/blog/healthy-bmi-range/` | `/#panel-women`, `/#panel-men`, `/#panel-ideal` |

**Not fixed here** (report only per your spec). Recommended fix on approval: repoint each to the dedicated calculator page &mdash; `/#panel-women` → `/women-bmi-calculator/`, etc. Same destination the anchor was trying to reach; without the dead fragment.

### External URL inventory

**76 distinct external URLs** referenced sitewide. Full listing (URL + pages using it) in `EXTERNAL-LINKS.md`. No network available in this box for verification; hand-check the file. The bulk are institutional sources already in use across multiple phases (WHO, CDC, NHLBI, NIH, ACOG, Mayo Clinic, Harvard Health, PubMed / PMC papers).

## 13.5 Schema audit + fixes — APPLIED

### Types declared per page (post-fix)

**All 29 pages: JSON-LD parses cleanly.** Type-vs-page appropriateness:

| Page class | Types | Correct? |
|---|---|---|
| Homepage | WebSite, WebApplication, Organization, FAQPage, BreadcrumbList | ✓ |
| About page | AboutPage, Person, Organization, WebSite, CollegeOrUniversity, EducationalOccupationalCredential, ImageObject, PostalAddress, FAQPage, BreadcrumbList | ✓ |
| Contact page | ContactPage, ContactPoint, Organization, BreadcrumbList | ✓ |
| Privacy / Terms | WebPage, BreadcrumbList (Privacy has WebSite too) | ✓ |
| Calculators hub | CollectionPage, ItemList, ListItem, FAQPage, WebSite, BreadcrumbList | ✓ |
| Blog hub | CollectionPage, ItemList, ListItem, BreadcrumbList | ✓ |
| Blog articles | Article, Person, Organization, WebPage, FAQPage (where visible FAQs exist), BreadcrumbList | ✓ |
| Calculator tools | WebApplication, Offer, FAQPage, BreadcrumbList | ✓ |

No wrong-type-on-wrong-page cases (e.g., no Article on a calculator page).

### Fixes applied

**BreadcrumbList added on 23 pages** that were missing it. Trails match the URL structure:

- Calculator pages: `Home > Calculators > <Calculator name>` (3 levels)
- Blog articles: `Home > Guides > <Article title>` (3 levels)
- About: `Home > About`
- Homepage: single-crumb "Home" root

**Article `image` property added on 12 blog articles** that were missing it. Each points at the per-page OG PNG created in 13.2, or the generic `og-image.png` for `how-to-lower-bmi` (no SVG).

**FAQPage schema added on 13 pages** that had visible FAQ markup (`class="faq-question"` + `class="faq-answer"`) but no schema block. Every schema Q&A extracted verbatim from the DOM markup, so the schema and the visible content are byte-identical:

| Page | # of FAQ Qs added to schema |
|---|---:|
| `/about/` | 7 |
| `/age-bmi-calculator/` | 10 |
| `/blog/bmi-and-metabolism/` | 8 |
| `/blog/bmi-categories/` | 8 |
| `/blog/bmi-formula/` | 6 |
| `/blog/bmi-tracking-guide/` | 8 |
| `/blog/healthy-bmi-range/` | 6 |
| `/ideal-weight/` | 10 |
| `/kids-bmi-calculator/` | 10 |
| `/lean-body-mass/` | 8 |
| `/men-bmi-calculator/` | 10 |
| `/new-bmi-calculator/` | 8 |
| `/women-bmi-calculator/` | 8 |

### Calculator page WebApplication check

All 7 calculator pages + `/index.html` carry `WebApplication` schema with:
- `applicationCategory: "HealthApplication"` ✓
- `operatingSystem: "Any"` ✓ (or `"Any"` equivalent)
- `offers`: `{"@type":"Offer","price":"0","priceCurrency":"USD"}` ✓

### Article completeness (blog posts)

Every Article schema now populated: `headline`, `author` (@id → Person), `publisher` (@id → Organization), `datePublished`, `dateModified`, `image` (per-page PNG or generic), `mainEntityOfPage`. All URL / image references resolve to on-disk files.

### Schema properties referencing URLs / images that don't resolve

**0.** Every schema property that names a URL or an image points to a file that exists.

## 13.6 Image SERP readiness — APPLIED (no changes needed)

Audit checked every `<img>` and every OG PNG for: alt text (present + non-empty), explicit width/height (attribute or inline style px), descriptive filename (rejected: `image.png`, `diagram-1.png`, `photo.jpg`, `chart.png`, single numeric names).

- `<img>` sitewide: only `/assets/images/marko-visic.jpg` (author photo on `/about/`) exists, with `alt="Portrait of Marko Visic"` and `width="128" height="128"`. ✓
- OG PNGs in `/assets/images/og/`: all 25 have descriptive filenames (e.g., `bmi-formula-trefethen.png`, `waist-height-diagram.png`, `underweight-cause-tree.png`). Zero non-descriptive names. ✓
- Legacy generic assets: `og-image.png`, `logo.png`, `logo.svg`, `marko-visic.jpg`/`.webp`, `favicon/*` &mdash; all named for their content. ✓

## What was NOT fixed here (per your report-only spec)

- 9 broken anchor fragments (`/#panel-women`, `/#panel-men`, `/#panel-ideal`) on 3 blog articles.
- 76 external URLs pending your out-of-box verification.

Ready for your review; committing now with the 13.1 / 13.2 / 13.5 / 13.6 fixes applied and 13.3 / 13.4 findings above.
