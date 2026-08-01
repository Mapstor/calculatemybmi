# FINDINGS.md — Raptive Remediation, Phase 0 (read-only)

Repo: `calculatemybmi.net` (static HTML, Vercel-hosted, no build step).
No `package.json`, no `vercel.json`, no `next.config.*`, no `_redirects`, no
`middleware.*`. Site is served straight from filesystem. `/workspace/.vercel/`
only contains `project.json` (linking IDs) — deploy-side config is in the
Vercel dashboard, not in the repo.

---

## 0.1 — Routes vs blog hub vs referenced slugs

### Routes that exist on disk (51 total)

**Top-level (14):**
`/`, `/about/`, `/age-bmi-calculator/`, `/calculators/`, `/contact/`,
`/ideal-weight/`, `/kids-bmi-calculator/`, `/lean-body-mass/`,
`/men-bmi-calculator/`, `/new-bmi-calculator/`, `/privacy/`, `/terms/`,
`/women-bmi-calculator/`, `/blog/`.

**Blog articles (37):**
bmi-accuracy, bmi-and-health-risks, bmi-and-life-insurance,
bmi-and-metabolism, bmi-by-age, bmi-calculator-by-age, bmi-calculator-guide,
bmi-categories, bmi-categories-explained, bmi-chart-explained, bmi-chart-men,
bmi-chart-women, bmi-for-athletes, bmi-for-children, bmi-for-men,
bmi-for-surgery, bmi-for-women, bmi-formula, bmi-history, bmi-limitations,
bmi-percentile-calculator, bmi-tracking-guide, bmi-vs-body-composition,
body-fat-vs-bmi, healthy-bmi-range, healthy-weight-tips, how-to-lower-bmi,
ideal-weight-calculator, improving-your-bmi, lean-body-mass-calculator,
muscle-mass-and-bmi, obese-bmi-category, overweight-bmi-risks,
pediatric-bmi-calculator, underweight-bmi-risks, waist-to-height-ratio,
what-is-bmi.

### (a) Routes that EXIST but are NOT linked from /blog/ hub (21 orphans)

The `/blog/` hub (`/workspace/blog/index.html`) links exactly 16 articles:
bmi-calculator-guide, bmi-categories-explained, bmi-chart-explained,
bmi-for-athletes, bmi-for-children, bmi-for-men, bmi-for-women,
bmi-limitations, body-fat-vs-bmi, healthy-bmi-range, muscle-mass-and-bmi,
obese-bmi-category, overweight-bmi-risks, underweight-bmi-risks,
waist-to-height-ratio, what-is-bmi.

Orphaned (exist on disk, in sitemap, but not on the hub):
1. bmi-accuracy
2. bmi-and-health-risks
3. bmi-and-life-insurance
4. bmi-and-metabolism
5. bmi-by-age
6. bmi-calculator-by-age
7. bmi-categories *(note: only `bmi-categories-explained` is on hub — both exist and are duplicates)*
8. bmi-chart-men
9. bmi-chart-women
10. bmi-for-surgery
11. bmi-formula
12. bmi-history
13. bmi-percentile-calculator
14. bmi-tracking-guide
15. bmi-vs-body-composition
16. healthy-weight-tips
17. how-to-lower-bmi
18. ideal-weight-calculator
19. improving-your-bmi
20. lean-body-mass-calculator
21. pediatric-bmi-calculator

### (b) Slugs linked in content but with NO route (404s) — NONE

Every `href="/blog/…"` across the site resolves to an existing directory
with `index.html`. Confirmed zero broken internal links.

### Verification of specific referenced-but-unconfirmed slugs

All 18 referenced slugs from the prompt EXIST as routes:

| slug | exists | on /blog/ hub |
|---|---|---|
| blog/bmi-and-health-risks | ✅ | ❌ orphan |
| blog/ideal-weight-calculator | ✅ | ❌ orphan |
| blog/bmi-and-metabolism | ✅ | ❌ orphan |
| blog/healthy-weight-tips | ✅ | ❌ orphan |
| blog/improving-your-bmi | ✅ | ❌ orphan |
| blog/bmi-tracking-guide | ✅ | ❌ orphan |
| blog/pediatric-bmi-calculator | ✅ | ❌ orphan |
| blog/bmi-for-children | ✅ | ✅ |
| blog/bmi-categories | ✅ | ❌ orphan |
| blog/bmi-categories-explained | ✅ | ✅ |
| blog/what-is-bmi | ✅ | ✅ |
| blog/bmi-chart-explained | ✅ | ✅ |
| blog/bmi-for-athletes | ✅ | ✅ |
| blog/underweight-bmi-risks | ✅ | ✅ |
| blog/overweight-bmi-risks | ✅ | ✅ |
| blog/obese-bmi-category | ✅ | ✅ |
| blog/waist-to-height-ratio | ✅ | ✅ |
| blog/muscle-mass-and-bmi | ✅ | ✅ |

---

## 0.2 — Analytics / ads / consent infrastructure

### GA4: INSTALLED on every page

Measurement ID `G-QKNBZGZTW1`, loaded via `googletagmanager.com/gtag/js`.
Present as a 6-line block in the `<head>` of every one of the 51 HTML files.
Example (identical on all pages):

```
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QKNBZGZTW1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-QKNBZGZTW1');
</script>
```

No `anonymize_ip` flag, no `consent_mode`, no `default consent` call — GA4
fires immediately on page load for every visitor, including EEA/UK.

### AdSense / other ad networks: NOT INSTALLED anywhere

- Zero `adsbygoogle` script tags.
- Zero `ca-pub-…` publisher IDs.
- Zero `pagead2.googlesyndication.com` references.
- No AdThrive / Raptive / Mediavine / Ezoic / Snigel / Monumetric /
  Taboola / Outbrain / Criteo / Amazon / Prebid / Doubleclick code.
- No `/ads.txt` file at repo root (no `public/` dir either).

Despite this, the Privacy Policy (`/workspace/privacy/index.html`) describes
AdSense as an active service in multiple sections:
- line 15 (meta description): "third-party services like Google Analytics and AdSense"
- line 36 (WebPage schema description): same
- line 123 (§1 "To Serve Advertisements"): "We use Google AdSense to display advertisements on the Site."
- line 144-145 (§4.3): "Advertising Cookies (Google AdSense)" block
- line 167-168 (§5.2): full "Google AdSense" third-party service block
- line 234 (§7): "Google (for Analytics and AdSense services)"
- line 278 (§Summary): "We use Google AdSense to display advertisements..."
- Terms (`/workspace/terms/index.html`) line 191 also refers to
  "Google AdSense program and other advertising networks."

**This is the biggest single Raptive-relevant divergence between code and
policy.** Every AdSense claim in privacy/terms is currently untrue.

### CMP / consent banner: NOT INSTALLED

- Zero occurrences of `cookieconsent`, `CookieConsent`, `OneTrust`, `Osano`,
  `iubenda`, `Complianz`, `Cookiebot` in `.html` or `.js`.
- No consent-related JavaScript anywhere in `/workspace/assets/js/`.
- `/workspace/about/index.html:321` displays a "GDPR & CCPA Compliant" badge,
  but no consent flow exists to back the claim.

Result: EEA/UK visitors currently trigger GA4 with no consent gate — this is
the technical failure to fix in Phase 3.

---

## 0.3 — robots.txt and sitemap

### `/workspace/robots.txt` (4 lines)

```
User-agent: *
Allow: /

Sitemap: https://calculatemybmi.net/sitemap.xml
```

- Blanket allow (OK).
- Sitemap URL uses APEX host.
- No explicit rules for `Googlebot`, `Bingbot`, `OAI-SearchBot`,
  `ChatGPT-User`, `PerplexityBot`, `Claude-User`, `Claude-SearchBot` — Phase
  5 will add them explicitly for good hygiene (all currently allowed via
  wildcard).

### `/workspace/sitemap.xml`

- 51 `<loc>` entries.
- Every URL uses `https://calculatemybmi.net` (APEX).
- Coverage: **exact match to filesystem** — diff of sitemap paths vs
  on-disk routes returns empty in both directions. Every route is in the
  sitemap; every sitemap entry has a route.
- `lastmod` values are pre-launch/authorial dates (2026-01-28 to 2026-02-12);
  not updated by any build step.

---

## 0.4 — Host / canonical / redirect audit

### Findings

- Every `<link rel="canonical">` in the repo uses
  `https://calculatemybmi.net` (APEX). No `www` in any canonical.
- Every `og:url` and `twitter:url` uses APEX.
- Every internal `href` uses root-relative `/path/` form — no absolute
  internal links, so links follow whatever host served the page.
- **Zero occurrences of the literal string `www.calculatemybmi.net` in
  `.html`, `.xml`, `.txt`, `.css`, or `.js` files across the repo.**

### Where the redirect config would live

Not in this repo. There is no `vercel.json`, no `_redirects`, no
`middleware.*`, no `next.config.*`. `/workspace/.vercel/project.json` only
contains `projectId` and `orgId` — no domain/redirect config.

The auditor's observation that "canonicals use apex while internal links
use www" is therefore a *runtime* observation: on the live site, Vercel
must be redirecting apex → www at the platform layer (Vercel dashboard
"Domains" config), so `www.calculatemybmi.net` becomes the served host and
the root-relative `/path/` links naturally resolve to www URLs. But the
canonical served on each page still says `https://calculatemybmi.net`
(apex), producing the exact www/apex mismatch reported.

### Phase 5 implication

Two consistent options; Phase 5 mandate is **www as canonical**:
1. Add `vercel.json` with `redirects` block for apex → 308 www (matches
   Phase 5 instructions), OR configure it in the Vercel dashboard.
2. Update every canonical / og:url / twitter:url / sitemap `<loc>` in
   this repo from `https://calculatemybmi.net` to
   `https://www.calculatemybmi.net`.
3. Update `robots.txt` sitemap URL to `www.` host.

Total occurrences to touch: 51 sitemap `<loc>` entries, 51 canonical tags,
~50 `og:url` tags, ~50 `twitter:url` tags, 1 robots.txt sitemap line, plus
absolute-URL references in Article/Organization schema. Grep count of
`https://calculatemybmi.net` (apex form) across the repo is on the order of
several hundred.

---

## 0.5 — Fabrication grep

### FABRICATED CLAIMS about our own site (must delete/rewrite)

**`/workspace/contact/index.html`**
- **line 14** — `<title>Contact Us - BMI Calculator | Get in Touch With Our Team</title>`
- **line 21** — `<meta property="og:title" content="Contact Us - BMI Calculator | Get in Touch With Our Team">`
- **line 27** — `<meta name="twitter:title" content="Contact Us - BMI Calculator | Get in Touch With Our Team">`
- **line 84** — "Since launching this website, we have helped millions of users understand their BMI..."
- **line 90** — "The best and most reliable way to contact our team is via email... email gives our team the time..."
- **line 107** — "Our team is equipped to assist... Over the years, we have received thousands of messages from users around the world..."
- **line 110** — "Our team can help clarify..."
- **line 116** — "Many of our current calculators and features were developed based on user suggestions." *(fabricated origin story)*
- **line 119** — "All corrections are reviewed and implemented..."
- **line 128** — `<!-- About Our Team and Mission -->`
- **line 130** — `<h2>About Our Team and Mission</h2>`
- **line 133** — "Our team consists of individuals passionate about health education, web development, and user experience design..."
- **line 137** — "Since our launch, we have served millions of users from over 150 countries..." *(hits every fabrication pattern)*
- **line 143** — "When you send an email to our team..."
- **line 160** — "Our team consists of health educators and web developers, not licensed medical professionals."
- **line 182** — "questions our team receives most frequently"
- **line 250** — "We enthusiastically welcome user suggestions! Many of our current features and calculators were developed based on ideas from our users..." *(second copy of the user-suggestion origin story)*
- **line 297** — "Our team is happy to provide additional clarification..."

**`/workspace/about/index.html`**
- **line 357** — "CalculateMyBMI.net was developed by a team dedicated to..." *(only "team" claim on About; rest of About is methodology copy that can survive with light edits)*

### LEGITIMATE hits (historical / research references — do NOT delete)

These matched "millions of" but describe verifiable historical events or
peer-reviewed research populations, not our site's user base:

- `/workspace/blog/bmi-history/index.html:353` — "medicalized millions of healthy people" (1998 NIH threshold change)
- `/workspace/blog/bmi-history/index.html:480` — "overnight reclassification of millions of Americans" (1998)
- `/workspace/blog/bmi-categories-explained/index.html:528` — "research examining ... across millions of people worldwide"
- `/workspace/blog/bmi-and-health-risks/index.html:154` — "studies involving millions of participants" (NHLBI J-curve)
- `/workspace/blog/healthy-bmi-range/index.html:210` — "decades of research involving millions of people" (NHLBI)
- `/workspace/blog/what-is-bmi/index.html:230` — "immediately reclassifying millions of Americans" (1998 threshold)
- `/workspace/ideal-weight/index.html:598` — "millions of policyholders" (MetLife historical fact)

These do need Phase 1 citation-verification (do the linked sources actually
support the exact sentence?), but they are NOT fabricated site-history
claims and Phase 1's deletion mandate does not apply to them.

---

## 0.6 — Search-volume badge grep

Seven public `<p class="blog-card-meta">…searches</p>` badges. All on
homepage or women's-calculator page:

| file | line | badge | links to |
|---|---|---|---|
| `/workspace/index.html` | 757 | `Guide • 2.7M searches` | `/blog/bmi-calculator-guide/` |
| `/workspace/index.html` | 758 | `Women • 246K searches` | `/blog/bmi-chart-women/` |
| `/workspace/index.html` | 759 | `Men • 49.5K searches` | `/blog/bmi-chart-men/` |
| `/workspace/index.html` | 760 | `Formula • 18.1K searches` | `/blog/bmi-formula/` |
| `/workspace/index.html` | 761 | `Health • 14K searches` | `/blog/healthy-bmi-range/` |
| `/workspace/index.html` | 762 | `Age • 9.8K searches` | `/blog/bmi-calculator-by-age/` |
| `/workspace/women-bmi-calculator/index.html` | 575 | `Women • 246K searches` | `/blog/bmi-chart-women/` |

The other 30+ `blog-card-meta` labels use topic tags (Guide, Kids, Athletes,
etc.) with no volume number — those are fine and stay. Phase 4 strips only
the seven listed above (replace with the topic tag alone).

---

## Additional Phase-0 findings (not asked for, but you should know before approving)

### Missing image assets (referenced in metadata, do NOT exist on disk)

`/workspace/assets/images/` contains only: `og-image.png`, `favicon/` dir,
`blog/` dir. But the following are referenced as og:image / twitter:image /
Article schema image:

- `https://calculatemybmi.net/assets/images/og-blog.png` — MISSING
- `https://calculatemybmi.net/assets/images/og-what-is-bmi.png` — MISSING
- `https://calculatemybmi.net/assets/images/og/bmi-calculator-guide.png` — MISSING (og/ dir doesn't exist)
- `https://calculatemybmi.net/assets/images/og/bmi-categories.png` — MISSING
- `https://calculatemybmi.net/assets/images/og/bmi-chart-men.png` — MISSING
- `https://calculatemybmi.net/assets/images/og/bmi-chart-women.png` — MISSING
- `https://calculatemybmi.net/assets/images/og/bmi-for-athletes.jpg` — MISSING
- `https://calculatemybmi.net/assets/images/og/bmi-formula.png` — MISSING
- `https://calculatemybmi.net/assets/images/og/bmi-health-risks.png` — MISSING
- `https://calculatemybmi.net/assets/images/og/healthy-bmi-range.png` — MISSING
- `https://calculatemybmi.net/assets/images/logo.png` — MISSING (referenced in Article publisher schema on many blog posts)

Only `og-image.png` (single generic OG) exists. Phase 5 asks to "verify
og-image assets referenced in metadata actually exist in public/". Since
none of the per-page OGs exist and there is no plan/budget stated for
generating them, the pragmatic fix is to **repoint every blog post og:image
/ twitter:image / Article "image" to the one file that does exist**
(`/assets/images/og-image.png`) unless you want to generate the missing
PNGs.

### Article schema state (relevant to Phase 2)

Every blog post has `Article` (or `Article`-adjacent) JSON-LD with:
- `author = { "@type": "Organization", "name": "BMI Calculator" }`
- `publisher = { "@type": "Organization", "name": "BMI Calculator" }`

Phase 2 wants author = `Person` (Marko Visic) and publisher = `Organization`
(Moving Data Systems d.o.o.). Every one of the 37 blog posts needs this
schema block updated. Some also carry `<meta property="article:author"
content="BMI Calculator Team">` (line 30 on bmi-and-health-risks, others)
that will need updating.

### "3,500 calories = 1 lb" claim in how-to-lower-bmi

Asserted as fact on lines **83** (FAQPage answer), **140** (Key Takeaways
list), **219** (body), and **730** (FAQ body). Phase 1 reframes all four to
"traditional approximation, dynamic models (Hall 2011, NIH Body Weight
Planner) show it overestimates long-term loss."

### Women's calculator age-adjusted table

`/workspace/women-bmi-calculator/index.html` around lines 155–180: table
shows 45–54: 22–27, 55–64: 22–27, 65+: 23–28. Attribution string
(line ~179): *"Sources: WHO, Mayo Clinic. Adjusted ranges for older women
are based on observational studies..."* — WHO/Mayo do **not** publish
age-adjusted BMI ranges. Phase 1 fix: either delete the adjusted rows or
recite the actual older-adult BMI/mortality literature (candidate primary
sources include Winter 2014 *AJCN* meta-analysis; Flegal 2013 *JAMA*
meta-analysis; NHANES-based analyses). Deep links must resolve.

### age-bmi-calculator page: same issue

`/workspace/age-bmi-calculator/index.html` lines 172, 200–215 (the
"Age-Adjusted BMI Ranges" table) and lines 396, 448 (visual mortality-risk
chart) present age-adjusted values with softer sourcing ("NHANES and
meta-analyses published in peer-reviewed journals" — no deep link). Phase 1
must apply the same audit: attach real primary sources or reframe.

### Blog hub "30+ Resources" claim

`/workspace/blog/index.html` lines 14, 21, 33, 108 all say "30+
Resources"/"30+ comprehensive guides". Actual count once Phase 4
consolidation is applied will change — Phase 4 says restate as the true
number.

### Contact email

`info@calculatemybmi.net` is used consistently on contact and privacy
pages. Matches the address in the Phase 2 prompt. No changes needed to the
address itself.

### GA4 status vs Phase 3 gate

Phase 3 says "if GA4 is NOT installed, flag it loudly." GA4 **is**
installed (ID `G-QKNBZGZTW1`). No flag needed for that; the flag needed is
that **GA4 fires with no consent** — Phase 3 must add Consent Mode v2
default-deny wrapping the existing gtag calls before Raptive resubmission.

---

## Proposed order of operations after your approval

The prompt already sets the phase order and phase-boundary commit
policy — this section just summarises the intended blast radius per phase
so you can approve knowing what actually changes.

1. **Phase 1 (Truth pass)** — heavy edits in `/contact/`, `/about/`,
   `/women-bmi-calculator/`, `/age-bmi-calculator/`,
   `/blog/how-to-lower-bmi/`; sitewide citation sweep touches many blog
   files but usually only citation attribution lines.
2. **Phase 2 (E-E-A-T)** — mechanical, sitewide: add byline+bio
   block+schema swap to every guide/calculator (~40 files).
3. **Phase 3 (Privacy + consent)** — rewrites `/privacy/`; introduces a
   consent-banner script (new file under `/assets/js/`) and wires
   Consent Mode v2 into the existing gtag block on all 51 pages.
4. **Phase 4 (De-SEO)** — strip 7 badges; propose consolidation table for
   approval before touching routes; interlink density audit (per-file).
5. **Phase 5 (Plumbing)** — host consolidation to www: `vercel.json` +
   sitewide canonical/og/sitemap/robots edit; missing-og-image fix;
   final link check.

Awaiting approval to begin Phase 1.
