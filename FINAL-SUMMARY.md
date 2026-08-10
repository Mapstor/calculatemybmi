# CalculateMyBMI Remediation — Final Summary

Every phase of the Raptive-rejection remediation, in order. Each phase links to
its git commit and covers what changed, why, and what to verify.

Local branch is `main`. Nothing has been pushed. The push happens from your Mac.

---

## Baseline

`92b3baa` &mdash; Add GA4 analytics and webmaster verification
`78f9434` &mdash; Initial commit: BMI Calculator website

Where the remediation started: a 33-post BMI calculator site with generic
"BMI Calculator" branding, unsourced quantitative claims, mixed citation
quality, no consent tooling, no author identity, no dedicated privacy
policy, and a large graveyard of low-value shadow guides.

---

## Phase 1 &mdash; Truth + sources
**`32fc6d6`** &middot; raptive-remediation: phase 1 &mdash; truth + sources

Purged unverifiable claims sitewide; every article and calculator page
received a Sources block linking to real institutional pages (WHO, CDC,
NHLBI, NIH, ACOG, Mayo Clinic, Harvard Health, JAMA/PMC citations).
About + contact + privacy + terms rewritten with real legal-entity info
(Moving Data Systems d.o.o., Maribor, Slovenia).

---

## Phase 1b &mdash; Citation triage
**`e4eec49`** &middot; raptive-remediation: phase 1b &mdash; citation triage

Three-tier approach across cited claims:

- **Tier A** (source properly): 52 URL replacements to institutional
  pages &mdash; NHLBI `lose_wt/*` legacy paths &rarr; current
  `/calculate-your-bmi` and `/health/overweight-and-obesity`; Cleveland
  Clinic short slugs &rarr; canonical `-bmi` variant; Flegal 2013 &rarr;
  PMC full text (PMC4855514); NEDA &rarr; NIMH (NEDA helpline
  disconnected); dead `letsmove.obamawhitehouse.archives.gov` resource
  removed.
- **Tier B** (strip figures, keep claims): 19 rewrites on 8 non-cluster
  pages, removing specific N-fold / hazard-ratio / percent-change
  claims attributed to homepages. Kept Flegal 2013 hazard ratios
  (real, cited) and Winter 2014 detail. Kept ACOG pregnancy
  weight-gain ranges and NHLBI waist thresholds.
- **Tier C** (delete): `/blog/bmi-and-life-insurance/` page deleted;
  308 redirect added; sitemap updated. age-bmi-calculator's ~60-line
  unsourced health-risk table replaced with a qualitative summary +
  WHO/CDC deep links. bmi-for-athletes sport-specific BMI-range
  table deleted; replaced with a qualitative paragraph + ACSM/NSCA
  references.

**`fd7b696`** &middot; raptive-remediation: phase 1b &mdash; cluster consolidation

First consolidation cluster (Alt B, 6 &rarr; 3): absorbed content from
`bmi-categories-explained`, `overweight-bmi-risks`, `obese-bmi-category`
into `bmi-categories`, `bmi-and-health-risks`, and `underweight-bmi-risks`
before redirecting. Post-merge Tier B run on the health-risks survivor
stripped specific numbers from the mortality/CV/diabetes/cancer/NAFLD
tables.

---

## Phase 2a &mdash; Absorbed content audit
**`04df0d4`** &middot; raptive-remediation: phase 2a &mdash; absorbed content audit

Before adding bylines, verified that no content absorbed from the Phase 1b
merges was fabricated. Every quantitative claim traced back to a real
source. Emitted `ABSORBED-AUDIT.md`.

---

## Phase 2 &mdash; Author identity / E-E-A-T
**`690702f`** &middot; raptive-remediation: phase 2 &mdash; author identity

Marko Visic byline added to every article. Person schema on `/about/`
with `@id: https://calculatemybmi.net/about/#author-bio`. Every article's
Article schema references that canonical Person `@id`. Corrected the
metabolic-syndrome citation to Alberti 2009 (subsequently removed
altogether by Amendment E in Phase 4).

---

## Phase 3 &mdash; Privacy + consent
**`b52f62a`** &middot; raptive-remediation: phase 3 &mdash; privacy and consent

Google Tag Manager container (placeholder ID) + Google Consent Mode v2
defaults installed on every page. Geo-gated banner: shows only for
visitors in Europe timezones (regex `^Europe/*`) plus the Atlantic
offshore territories that are still EEA in practice
(Reykjavik/Faroe/Azores/Madeira/Canary). US and RoW visitors get
analytics on by default (Raptive-compatible).

Consent snippet split into two parts:
- **Inline synchronous** in every `<head>`: sets `consent default`,
  reads timezone + `localStorage` choice, applies existing choice if
  present. Small (~1 KB).
- **Deferred external** (`/assets/js/consent-banner.js`, 5 KB): loads
  GTM after DOM parse, shows the banner UI if in-scope + no choice
  stored. Never blocks first paint.

Privacy policy rewritten to match actual behaviour (client-side
calculator inputs never sent, GA4 via GTM, geo-gated defaults, real
legal controller, GDPR + CCPA/CPRA rights honoured, Slovenian address).

---

## Phase 4 (partial) &mdash; SEO surface pre-work
**`415eadf`** &middot; raptive-remediation: phase 4 (partial) &mdash; perf split, badges stripped, interlink dedup, consolidation-2 proposal

- **4.0**: `analytics.js` split into a tiny inline defaults block and a
  deferred external file. Removed 87% of the render-blocking bytes on
  the calculator load path.
- **4.1**: 7 "N searches" search-volume badges (leftover from an
  earlier marketing template) stripped sitewide.
- **4.2**: Interlink-density audit; over-linked "related guides"
  sections pruned so links carry weight instead of noise.
- **4.3**: `CONSOLIDATION-2.md` proposal written covering all 33
  surviving blog posts with recommended keep/absorb/redirect
  decisions.

---

## Phase 4 &mdash; SEO surface + consolidation (with amendments A, G, E)
**`9d271ad`** &middot; raptive-remediation: phase 4 &mdash; seo surface and consolidation

The heavy lift. 33 blog posts consolidated down to 15 survivors, with
three critical late amendments:

- **Amendment A**: `blog/bmi-for-surgery` deleted outright (not audited,
  not salvaged). 308 &rarr; `blog/bmi-categories/`.
- **Amendment G &mdash; sitewide medical scope policy**: the site is now
  OUT of medical treatment and diagnosis entirely. Stripped:
  bariatric surgery content (ASMBS candidacy criteria, procedure
  comparisons, RYGB/sleeve/duodenal switch by name), anti-obesity
  pharmacotherapy (GLP-1/semaglutide/tirzepatide/orlistat/phentermine),
  disease-specific numeric risk quantification, "should be evaluated
  by" / "your doctor will" / "treatment plan" phrasings. Replaced
  with brief meta-disclaimers stating what the site does not cover
  and pointing to a qualified clinician.

  **Preserved and made more prominent** (per user's explicit
  instruction, "removing them would be the one genuinely harmful edit
  in this whole remediation"): eating-disorder helpline resources on
  `underweight-bmi-risks` &mdash; National Alliance for Eating Disorders
  (1-866-662-1235), SAMHSA (1-800-662-4357, 24/7), NIMH link &mdash; in
  a dedicated amber callout block. Pediatrician signposting on
  `kids-bmi-calculator` preserved unchanged.
- **Amendment E &mdash; metabolic syndrome demoted**: on both
  `bmi-and-health-risks` and `bmi-and-metabolism`, the 5-criteria
  numeric diagnostic table + "any 3 of 5" framing removed entirely.
  Alberti 2009 and Grundy 2005 citations removed with the thresholds.
  Replaced with a single qualitative paragraph naming the components
  in plain words with no numbers, linking to the NHLBI overview.

**Consolidation-2 execution**: 18 shadow guides deleted (in addition
to the 3 from Phase 1b), leaving 15 survivors. `vercel.json` rebuilt
with 22 conceptual redirects (44 trailing-slash-paired rules), all
statusCode 308, zero redirect chains. Every dying slug covered; zero
remaining internal HTML `href` references to dying slugs (270
replacements across 29 files during the sweep).

Sitemap regenerated (29 URLs). Blog hub regenerated (15-post
`ItemList`, `numberOfItems: 15`, 6 topical sections + related-calculators
grid, plus a meta-disclaimer paragraph).

Distinctness check on `bmi-and-health-risks` after treatment content
removal: still 3,954 words, retains BMI-mortality, CV, T2D, cancer,
respiratory, MSK, liver, kidney, mental health, and the BMI Risk Zones
chart. Distinct from `bmi-categories` (classification-focused). No
folding needed.

---

## Phase 5 &mdash; Plumbing + final verify
**`ab4cd66`** &middot; raptive-remediation: phase 5 &mdash; plumbing and final verify

- **5.1 Images**: 6 broken per-post OG image URLs (pointing at files
  that never existed) repointed to the generic
  `/assets/images/og-image.png` (1200x630, verified present). 10 pages
  had no `og:image` and no `twitter:image` at all &mdash; added both,
  plus `og:image:width/height`, on each. All 29 pages now share the
  generic OG image. Zero missing image files sitewide, zero `<img>`
  missing or empty alt attributes. Distinct per-post OG images
  captured in `BACKLOG.md`.
- **5.2 Crawl surface**: `robots.txt` rewritten with explicit `Allow`
  blocks for Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, GPTBot,
  Claude-User, Claude-SearchBot, ClaudeBot, PerplexityBot on top of
  the wildcard allow. `sitemap.xml`: 29 URLs, all resolving to an
  `index.html` on disk, zero references to redirected slugs. Custom
  styled `404.html` built &mdash; noindex,follow, links to `/`,
  `/blog/`, `/calculators/`, plus a popular-pages grid.
- **5.3 Metadata**: 0 duplicate titles, 0 duplicate descriptions,
  exactly 1 H1 per page across all 29 pages. Brand-string
  inconsistency flagged for user decision (see Phase 6, which
  standardised on "CalculateMyBMI").
- **5.4 Link graph**: 0 broken internal links (5 apparent hits were
  false positives on `<link rel=icon>` and stylesheet paths). 0
  references to any redirected slug &mdash; Phase 4.4 sweep was
  complete. All 29 URLs reachable in &le;2 hops from `/`.
- **5.5 Schema**: 0 JSON-LD parse failures. 0 schema references to
  any deleted URL. Single canonical `Person @id`
  (`about/#author-bio`) and single canonical `Organization @id`
  (`#organization`). All 5 breadcrumb trails match URL structure.
  FAQPage Q&As on G/E-stripped pages remain content-aligned.
- **5.6 Final grep gate**: all zero as required &mdash; AdSense,
  Phase 0.5 fabrications ("millions of users", "150 countries", etc.),
  search-volume badges, `www.calculatemybmi.net` references, hardcoded
  `gtag('config')` outside GTM, metabolic-syndrome numeric thresholds,
  Tier B stripped figures re-entered. Two Amendment G term hits
  intentionally preserved as anti-treatment meta-disclaimers:
  `contact/` ("not a diagnosis, not a treatment plan") and
  `kids-bmi-calculator/` ("screening tools, not diagnostic criteria").
- **5.7 `DEPLOY-CHECKLIST.md`** written: confirms
  `GTM-PLACEHOLDER` is still a placeholder (deploying without
  replacement means zero analytics); lists manual pre-deploy steps;
  documents Vercel non-git-connected deploy procedure; per-phase
  change summary with commit hashes; known non-blockers.

---

## Phase 6 &mdash; Brand, mobile, housekeeping
**`e54cf74`** &middot; raptive-remediation: phase 6 &mdash; brand, mobile, housekeeping

- **6.1 Brand standardisation on "CalculateMyBMI"** (legal entity
  "Moving Data Systems d.o.o." preserved only in footer copyright,
  privacy controller, terms). 94 targeted replacements across 29
  pages: header logo span, `og:site_name`, title pipe suffixes,
  per-page title fixes for about/privacy/terms/contact. Homepage
  Organization schema rewritten with `@id` +
  `name: "CalculateMyBMI"` + `legalName: "Moving Data Systems d.o.o."`
  + `alternateName: "CalculateMyBMI.net"` +
  `logo: /assets/images/logo.png`. Homepage WebSite schema matched with
  `@id: /#website`. `terms/` and `blog/` `isPartOf` collapsed to `@id`
  refs. Logo image regenerated (old rendered "BMI calculator"): new
  512x512 PNG built with ImageMagick shows large "BMI" + "CalculateMyBMI"
  wordmark; SVG vector version added as
  `/assets/images/logo.svg`.
- **6.2 Inbound links repaired**:
  `blog/bmi-chart-explained/` 1 &rarr; 5 non-nav, non-footer inbounds
  (added contextual references from `bmi-categories` inline callout +
  related card, `what-is-bmi` related card, `healthy-bmi-range`
  related card, `women-bmi-calculator` related card,
  `men-bmi-calculator` related card).  
  `terms/` 0 &rarr; 2 (added natural cross-references from `about`
  privacy section and `privacy` final section).  
  `contact/` 1 &rarr; 2 (added from `privacy` final section).  
  Zero survivors with <2 content inbounds.
- **6.3 Mobile audit + fixes**:
  - `viewport` meta: present on all 29 pages.
  - body font-size: 16px (verified).
  - Fixed-width elements >360px: none (36 initial hits were all
    `max-width` containers, which shrink under narrow viewports).
  - Tables: **49 tables wrapped** in `<div class="table-responsive">`
    (styles.css `.table-responsive { overflow-x: auto; }`). Post-fix:
    0 unwrapped tables sitewide.
  - Tap targets: `.nav-mobile a` (was ~32px) &rarr; padding 0.75rem +
    `min-height: 44px`; `.nav-toggle` &rarr; `min-width:44px
    min-height:44px`; consent banner Accept/Decline buttons &rarr;
    padding 0.75rem + `min-height:44px`.
  - Consent banner at 360px: fixed-position with `left:16px right:16px`
    and `max-width:640px auto-centred`. Buttons wrap via `flex-wrap`
    and now meet 44px tap-target. Does not cover the calculator.
- **6.4 Speed static analysis** (no network in this box):
  - Assets: `styles.css` 35.9 KB, `analytics.js` 1.3 KB (deferred),
    `calculator.js` 68.5 KB (deferred), `consent-banner.js` 5.0 KB
    (deferred), `logo.png` 50.6 KB (schema-only, not critical path),
    `og-image.png` 22.9 KB (social crawler only).
  - Per-page HTML: 11.1 KB (contact) to 107.5 KB (homepage).
  - Render-blocking per page: exactly 1 (styles.css). Zero
    render-blocking JS.
  - `<img>` with explicit width+height: 100% (only image on the site
    is the author photo on `/about/`, which has both).
  - Consent banner CLS: `position:fixed`, never reflows. Zero CLS.
  - Nothing here looks like it would plausibly fail Core Web Vitals
    on standard hosting. Not asserting a score &mdash; no lab
    measurement possible without network.
- **6.5 Housekeeping**:
  - `/1516504244887.jpeg` (stray headshot, source for the processed
    `marko-visic.jpg/webp`) deleted from repo root.
  - `/.devcontainer/` added to `.gitignore`.
  - New `/.vercelignore` added: excludes `.git`, `.claude`,
    `.devcontainer`, `.vercel`, `node_modules`, all `*.md` audit
    artefacts, the stray jpeg, and `.DS_Store`. Ensures a manual
    `vercel --prod` upload ships only the site.

Working tree is now clean.

---

## What still needs your hand before deploy

Full detail is in **`DEPLOY-CHECKLIST.md`** &mdash; the short list:

1. **Replace `GTM-PLACEHOLDER`** in `/assets/js/consent-banner.js` line 26
   with the real GTM container ID (format `GTM-XXXXXXX`). Without this,
   nothing will fire &mdash; not GA4, not Raptive tags, not anything else
   wired through GTM. **This is the only genuine blocker.**
2. **`git push origin main`** from your Mac (nothing has been pushed
   from this box).
3. **`vercel --prod`** (CLI) or "Redeploy" from the Vercel dashboard.
4. **Post-deploy smoke test** (~5 minutes) &mdash; several 308 redirects,
   several 200 pages, and a 404 test, all listed in the checklist.

---

## Commit chain

```
e54cf74  raptive-remediation: phase 6 — brand, mobile, housekeeping
ab4cd66  raptive-remediation: phase 5 — plumbing and final verify
9d271ad  raptive-remediation: phase 4 — seo surface and consolidation
415eadf  raptive-remediation: phase 4 (partial) — perf split, badges stripped, interlink dedup, consolidation-2 proposal
b52f62a  raptive-remediation: phase 3 — privacy and consent
690702f  raptive-remediation: phase 2 — author identity
04df0d4  raptive-remediation: phase 2a — absorbed content audit
fd7b696  raptive-remediation: phase 1b — cluster consolidation
e4eec49  raptive-remediation: phase 1b — citation triage
32fc6d6  raptive-remediation: phase 1 — truth + sources
92b3baa  Add GA4 analytics and webmaster verification
78f9434  Initial commit: BMI Calculator website
```

---

## Audit trail on disk

- `FINDINGS.md` &mdash; Phase 0 discovery
- `TRIAGE-REPORT.md` &mdash; Phase 1b citation triage detail
- `CITATIONS.md`, `UNSOURCED.md` &mdash; sourcing worklists
- `CONSOLIDATION.md` &mdash; Phase 1b consolidation options
- `CONSOLIDATION-2.md` &mdash; Phase 4.3 consolidation proposal
- `ABSORBED-AUDIT.md` &mdash; Phase 2a content-provenance audit
- `CONSENT-REPORT.md` &mdash; Phase 3 privacy behaviour vs. policy
- `BACKLOG.md` &mdash; nice-to-haves deferred (distinct per-post OG
  images, author-photo variants, `og:image:alt`)
- `DEPLOY-CHECKLIST.md` &mdash; step-by-step deploy plan
- `FINAL-SUMMARY.md` &mdash; this document

All of the above are `.vercelignore`-excluded &mdash; they exist in the
repo for the paper trail but do not ship live.
