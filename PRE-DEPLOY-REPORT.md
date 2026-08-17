# Pre-Deploy Report — Phase 17 Integration Audit

**Audit performed against**: 30 HTML pages (29 real content pages + 404). One additional file, `google12f8c2f9c03913a3.html`, is a Google Search Console verification stub and is excluded from all audits.

**Sitewide integrity signals (post-fix)**:

| Signal | Result |
|---|---|
| Inline JS `node --check` | 0 failures across all pages |
| JSON-LD parses | 0 failures |
| Distinct byline strings | 1 (byte-identical sitewide) |
| Consent Mode v2 default block missing | 0 / 29 |
| `nav-toggle` binder missing | 0 / 29 |
| Cookie settings footer button missing | 0 / 29 |

---

## 17.1 — Per-page completeness matrix

Columns: T=title, MD=meta desc, C=canonical, OGT=og:title, OGD=og:desc, OGI=og:image, OGWH=og:image:width/height, TC=twitter:card, TI=twitter:image, JLD=JSON-LD parses, BC=BreadcrumbList, AID=author @id, BY=byline, H1=count, VP=viewport, CI=consent inline, CB=consent-banner.js, NT=nav-toggle, BND=binder, FT=footer.

| Page | T | MD | C | OGT | OGD | OGI | OGWH | TC | TI | JLD | primary @type | BC | AID | BY | H1 | VP | CI | CB | NT | BND | FT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| / | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | WebSite | — | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /404 | ✓ | ✓ | ✓ | — | — | — | — | — | — | ✓ | — | — | — | — | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /about/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Person,FAQPage,BreadcrumbList | ✓ | — | — | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /age-bmi-calculator/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | CollectionPage | — | — | — | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-and-health-risks/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-and-metabolism/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-categories/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-chart-explained/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-for-athletes/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-formula/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-history/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-limitations/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/bmi-tracking-guide/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/body-fat-vs-bmi/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/healthy-bmi-range/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/how-to-lower-bmi/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/underweight-bmi-risks/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/waist-to-height-ratio/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /blog/what-is-bmi/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Article,FAQPage,BreadcrumbList | ✓ | ✓ | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /calculators/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (no schema) | — | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /contact/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ContactPage | — | — | — | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /ideal-weight/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /kids-bmi-calculator/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /lean-body-mass/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /men-bmi-calculator/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /new-bmi-calculator/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /privacy/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | WebPage | — | ✓ | — | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /terms/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | WebPage | — | ✓ | — | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| /women-bmi-calculator/ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | FAQPage,WebApplication | ✓ | — | ✓ | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Fixes applied in this phase**:
- Added `og:image:width` + `og:image:height` (1200×630) to `/about/`, `/contact/`, `/`, `/privacy/` — 4 pages.

**Cells intentionally left blank (—) — judgment calls for you**:

| Missing cell | Where | Reason |
|---|---|---|
| BreadcrumbList | `/`, `/blog/`, `/calculators/`, `/contact/`, `/privacy/`, `/terms/` | Hub / utility / homepage pages; BreadcrumbList typically not used above depth 1. |
| author @id in schema | 8 calculator pages, `/`, `/about/`, `/blog/`, `/calculators/`, `/contact/` | Calculator pages use WebApplication schema; author @id is standard for Article but optional for WebApplication. |
| byline | `/404`, `/about/`, `/blog/`, `/contact/`, `/privacy/`, `/terms/` | Author bio is on `/about/`; utility/legal pages don't carry the byline. |
| OG on `/404` | `/404` | 404 is noindex; social preview meta not needed. |

None of the above blocks shipping.

---

## 17.2 — Interlinking

### Inbound content-link counts (nav/footer excluded), sorted desc

| Rank | Inbound | Page |
|---:|---:|---|
| 1 | 79 | `/` |
| 2 | 61 | `/women-bmi-calculator/` |
| 3 | 60 | `/men-bmi-calculator/` |
| 4 | 57 | `/lean-body-mass/` |
| 5 | 52 | `/blog/bmi-limitations/` |
| 6 | 45 | `/age-bmi-calculator/` |
| 7 | 40 | `/blog/body-fat-vs-bmi/` |
| 8 | 40 | `/ideal-weight/` |
| 9 | 40 | `/kids-bmi-calculator/` |
| 10 | 38 | `/blog/how-to-lower-bmi/` |
| 11 | 34 | `/blog/bmi-categories/` |
| 12 | 28 | `/blog/bmi-and-health-risks/` |
| 13 | 27 | `/blog/bmi-for-athletes/` |
| 14 | 24 | `/about/` |
| 15 | 23 | `/blog/bmi-formula/` |
| 16 | 23 | `/blog/healthy-bmi-range/` |
| 17 | 23 | `/blog/what-is-bmi/` |
| 18 | 14 | `/new-bmi-calculator/` |
| 19 | 10 | `/blog/bmi-and-metabolism/` |
| 20 | 10 | `/blog/waist-to-height-ratio/` |
| 21 | 9  | `/blog/underweight-bmi-risks/` |
| 22 | 6  | `/blog/` |
| 23 | 6  | `/privacy/` |
| 24 | 5  | `/blog/bmi-history/` |
| 25 | 4  | `/blog/bmi-tracking-guide/` |
| 26 | 4  | `/calculators/` |
| 27 | 3  | `/blog/bmi-chart-explained/` |
| 28 | 2  | `/contact/` |
| 29 | 2  | `/terms/` |
| 30 | 0  | `/404` — expected, not linked from content |

**Pages with < 2 content inbounds**: only `/404`, which is correct.

### Outbound content links per page (top 5, plus flag summary)

Every non-utility content page exceeds ~10 outbound content links (the ~10 threshold assumed a leaner site). The three heaviest fan-outs are `/calculators/` (70), `/ideal-weight/` (62), `/` (52). This shape is intentional for a hub-and-spoke content site — full listing available in the interlinking log if you want to see it. **Judgment call for you**: is ~30 outbound content links per page on this site model acceptable, or do you want a trim?

### Orphans (reachable only via nav/footer)

- `/404` — expected. No other orphans.

### Click depth from homepage (BFS on all internal links)

- Depth 0: `/`
- Depth 1: 20 pages (about, contact, privacy, terms, calculators hub, all 7 secondary calculators, all 15-6 = 9 blog posts linked from `/`)
- Depth 2: 6 blog posts (bmi-and-health-risks, bmi-and-metabolism, bmi-chart-explained, bmi-history, bmi-tracking-guide, waist-to-height-ratio)
- Unreachable: `/404` (correct)

Max depth = 2 for indexable pages. Within target.

### Reciprocal-link clusters

A dense hub-and-spoke pattern with `/about/`, `/`, and the calculator pages at the centre. About-page is reciprocal with 14 other pages; each calculator page is reciprocal with 3–8 others. This is typical for tightly-interlinked content site — no clusters look pathological. **Fixed during audit**: 33 self-referential links (a page linking to itself) were unambiguously broken UX — 11 Related-Guides cards removed and 22 inline body self-links unlinked across 12 pages.

### Exact-match anchor repetition (≥ 3 pages)

| Count | Anchor | Target |
|---:|---|---|
| 24 | "marko visic, mpharm" | `/about/` (author byline — 1 per page) |
| 17 | "ideal weight calculator" | `/ideal-weight/` |
| 16 | "lean body mass calculator" | `/lean-body-mass/` |
| 15 | "pediatric bmi calculator" | `/kids-bmi-calculator/` |
| 15 | "bmi limitations" | `/blog/bmi-limitations/` |
| 13 | "bmi categories" | `/blog/bmi-categories/` |
| 13 | "healthy bmi range" | `/blog/healthy-bmi-range/` |
| 13 | "bmi calculator" | `/` |
| 12 | "bmi calculator for men" | `/men-bmi-calculator/` |
| 12 | "bmi calculator by age" | `/age-bmi-calculator/` |
| 11 | "bmi calculator for women" | `/women-bmi-calculator/` |
| 10 | "standard bmi calculator" | `/` |
| 10 | "bmi for men" | `/men-bmi-calculator/` |
| 10 | "bmi for women" | `/women-bmi-calculator/` |
| 9 | "lean body mass" | `/lean-body-mass/` |

**Judgment call for you**: These are product names that recur naturally in a BMI calculator site. Some SEO practitioners rotate anchor text; some don't. Not flagged as broken.

### Link importance: calculators vs blog

- 8 calculators: **396** inbound total (avg 49.5)
- 15 blog posts: **329** inbound total (avg 21.9)

Calculators receive more inbound than blog posts. Shape reflects the intended product hierarchy.

---

## 17.3 — Content integrity regression sweep (30 pages)

| Gate | Hits | Note |
|---|---:|---|
| AdSense / adsbygoogle / ca-pub / pagead2 | **0** | clean |
| P0.5 fabrication strings | 1 | `/privacy/` contains "we receive your email…" — legitimate privacy-policy prose about the contact form. Not fabrication. |
| Search-volume badges | **0** | clean |
| `www.calculatemybmi.net` | **0** | clean (all canonical hosts are bare `calculatemybmi.net`) |
| Hardcoded `gtag('config')` outside loader | **0** | clean |
| Drug names (semaglutide/tirzepatide/phentermine/orlistat/liraglutide/Ozempic/Wegovy/Mounjaro/Zepbound) | **0** | clean |
| Bariatric / surgical candidacy content | 1 | `/about/` disclaimer explicitly *disclaims* covering it: "We do not cover medical treatment content — medication choices, bariatric surgery decisions…" Legitimate. |
| Stale prevalence figures (41.9 / 42.4 / 37% / 30.7) | 1 | `/` — the `30.7` hit is a BMI **value** in a height/weight lookup table (5'6" @ 180 lb → BMI 30.7), not a CDC prevalence figure. False positive. |
| "up to 27" / "up to 28" older-adult ceilings | **0** | clean |
| `GTM-PLACEHOLDER` | **0** | clean |
| `"Last reviewed"` | **0** | Phase 16 cleanup verified |
| Bare-domain links attached to a specific claim | **0** after fix | 5 resource-list entries removed (Mayo→"Metabolism and Weight", Harvard→"The Truth About Metabolism", Cleveland Clinic→"Metabolic Syndrome" on `/blog/bmi-and-metabolism/`; ACE→"Body Fat Percentage Categories", ACSM→"Body Composition Guidelines" on `/blog/body-fat-vs-bmi/`). Remaining bare-domain links (11) all pair with the org's own name as anchor text and appear in "Further reading" cards — not specific-claim citations. |

**Verdict**: no regression from earlier phases.

---

## 17.4 — Functional re-verify (all 8 calculators)

| Calculator | Own button ID | Own panel ID | Common input classes | External JS | node --check |
|---|---|---|---|---|---|
| `/` (Standard BMI) | `calc-standard-btn` ✓ | `panel-standard` ✓ | 8/8 ✓ | calculator.js + consent-banner.js ✓ | ✓ |
| `/women-bmi-calculator/` | `calc-women-btn` ✓ | `panel-women` ✓ | 8/8 ✓ | ✓ | ✓ |
| `/men-bmi-calculator/` | `calc-men-btn` ✓ | `panel-men` ✓ | 8/8 ✓ | ✓ | ✓ |
| `/age-bmi-calculator/` | `calc-age-btn` ✓ | `panel-age` ✓ | 8/8 ✓ | ✓ | ✓ |
| `/kids-bmi-calculator/` | `calc-kids-btn` ✓ | `panel-kids` ✓ | 8/8 ✓ | ✓ | ✓ |
| `/new-bmi-calculator/` | `calc-newbmi-btn` ✓ | `panel-newbmi` ✓ | 8/8 ✓ | ✓ | ✓ |
| `/ideal-weight/` | `calc-ideal-btn` ✓ | `panel-ideal` ✓ | 6/8 ✓ (no weight input — takes height + sex + frame) | ✓ | ✓ |
| `/lean-body-mass/` | `calc-lbm-btn` ✓ | `panel-lbm` ✓ | 8/8 ✓ | ✓ | ✓ |

- `calculator.js` (70 KB) references all 8 button+panel IDs defensively so a shared file works across pages; parses cleanly (`node --check` OK). Every host page contains its own required IDs.
- `consent-banner.js` (4.8 KB) references three IDs (`cmbmi-consent-{accept,decline,banner}`) that it creates dynamically — no host-page IDs needed.
- FAQ toggle wiring: present in `calculator.js` (references `.faq-item` / `.faq-question`). Every page carrying `.faq-item` markup is served by this handler.
- nav-toggle binder: 29/29 pages match button + inline binder pair.
- Cookie settings footer button (`onclick="reopenConsentSettings()"`): 29/29 pages carry it.
- Consent Accept/Decline buttons and the banner shell are injected at runtime by `consent-banner.js` — verified handlers exist in that file.

Nothing I cannot confirm.

---

## 17.5 — Assets + crawl

### Referenced local assets

- Referenced from HTML (`src` / `href` / `content` / inline `url(...)`), CSS files, JS files, and JSON-LD `image/url` fields.
- **0 missing** — every referenced asset resolves on disk.

### sitemap.xml

- 29 URLs listed. Route set on disk: 29 real pages (excluding `/404`, correctly omitted from sitemap).
- **0 missing** from sitemap.
- **0 extra** in sitemap.

### robots.txt

- `User-agent: *` → `Allow: /`
- Explicit allow blocks for: **Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, GPTBot, Claude-User, Claude-SearchBot, ClaudeBot, PerplexityBot** — 9 bots.
- `Sitemap: https://calculatemybmi.net/sitemap.xml`

### vercel.json

- All redirect `destination` fields resolve to live routes on disk.
- **0 dead destinations**.
- **0 redirect chains** (no `A→B` where B is itself a redirect source).

### Orphaned files in `assets/`

Total files: 40. Referenced (HTML + CSS + JS + manifest scan): 32. **Truly orphaned: 8**.

| Orphan | Notes |
|---|---|
| `/assets/js/analytics.js` | Its own header states "this file is now empty" — legacy placeholder. Deletable. |
| `/assets/images/favicon/favicon-192x192.png` | PWA size, not referenced (no `site.webmanifest`). Deletable, or leave for future PWA. |
| `/assets/images/favicon/favicon-512x512.png` | Same. |
| `/assets/images/logo.svg` | Header uses inline SVG; this file unused. Deletable. |
| `/assets/images/og/bmi-formula-703-derivation.png` | Superseded — `/blog/bmi-formula/` uses `bmi-formula-trefethen.png`. |
| `/assets/images/og/kids-girls-percentile.png` | Superseded — `/kids-bmi-calculator/` uses `kids-boys-percentile.png`. |
| `/assets/images/og/kids-same-bmi-different-age.png` | Superseded — same file uses `kids-boys-percentile.png`. |
| `/assets/images/og/lean-body-mass-formulas.png` | Superseded — `/lean-body-mass/` uses `lean-fat-composition-split.png`. |

**Judgment call for you**: delete all 8 (repo hygiene, ~200 KB), or leave (no shipping impact).

---

## Fixes applied in this phase

| # | What | Count |
|---:|---|---:|
| 1 | `og:image:width` + `og:image:height` added (1200×630) | 4 pages |
| 2 | Resource-list items with bare-domain URLs paired with specific-claim anchor text removed | 5 items across 2 pages |
| 3 | Self-referential Related-Guides / related-card / related-article-card blocks removed | 11 cards across 8 pages |
| 4 | Self-referential inline body links unlinked (kept the anchor text) | 22 links across 10 pages |

Post-fix integrity verified: 0 JS syntax fails, 0 JSON-LD parse fails, 1 distinct byline, 0 missing consent/binder/cookie-settings.

## Judgment calls flagged (not fixed)

1. Missing `author @id` in `WebApplication` schema on 8 calculator pages — optional for that type.
2. Missing `BreadcrumbList` on `/`, `/blog/`, `/calculators/`, `/contact/`, `/privacy/`, `/terms/` — arguably not needed at depth 1 / on utility pages.
3. Outbound content-link counts exceed the "~10" threshold on every content page — this is a hub-and-spoke content site by design.
4. High anchor-text repetition — product name naturally recurs; no rotation applied.
5. Thin blog posts: `/blog/bmi-chart-explained/` (3 inbound), `/blog/bmi-tracking-guide/` (4), `/blog/bmi-history/` (5) — enrichment optional.
6. 8 orphaned files in `assets/` — deletion vs keep is your call.

---

## VERDICT: **SHIP**

Nothing blocks deployment. The four unambiguous defects found during the audit (missing OG dimensions on 4 pages, 5 misleading bare-domain resource-list items, 33 self-referential links) were fixed inline. All 30 pages pass structural, functional, JS, and JSON-LD checks. Redirects and sitemap are consistent with the on-disk route set. Consent Mode v2, nav-toggle binder, and Cookie settings button are byte-consistent across all 29 real pages.
