# Deploy Checklist — Post-Raptive Remediation

Everything below assumes the site is deploying to Vercel via the CLI or the
Vercel dashboard's "Deploy" button (not git-connected). If that changes,
revisit sections 2 and 4.

---

## 0. Status at HEAD

Local branch: `main`
Last remediation commit: **`(this phase's hash — see git log after commit)`**

Every remediation-phase commit, oldest first:
- `92b3baa` &mdash; baseline (analytics + verification, pre-remediation)
- `32fc6d6` &mdash; phase 1 — truth + sources
- `e4eec49` &mdash; phase 1b — citation triage
- `fd7b696` &mdash; phase 1b — cluster consolidation
- `04df0d4` &mdash; phase 2a — absorbed content audit
- `690702f` &mdash; phase 2 — author identity
- `b52f62a` &mdash; phase 3 — privacy + consent
- `415eadf` &mdash; phase 4 (partial) — perf split, badges, interlink, CONSOLIDATION-2 proposal
- `9d271ad` &mdash; phase 4 — seo surface + consolidation (amendments A/G/E)
- `(pending)` &mdash; phase 5 — plumbing + final verify

Nothing has been pushed. Push happens from Mac, at your discretion.

---

## 1. THINGS I MUST DO BY HAND BEFORE DEPLOY

### 1a. Analytics is direct GA4 gtag — no pre-deploy replacement needed

**Status: RESOLVED.** Phase 9 removed the GTM placeholder. Analytics now
loads GA4 directly via the async gtag.js loader with property ID
**`G-QKNBZGZTW1`**, from **`/assets/js/consent-banner.js`**
(look for `var GA4_ID = ...` at the top of the file).

Behaviour unchanged from Phase 3: the loader is deferred and gated by
Google Consent Mode v2 defaults set in the inline `<head>` snippet on
every page. In-scope visitors (Europe timezones + Atlantic offshore
EEA) start with `analytics_storage: 'denied'` until they choose Accept
in the banner. Everyone else starts granted. Footer "Cookie settings"
link reopens the banner.

**Deploying now results in real GA4 traffic against
property G-QKNBZGZTW1** &mdash; no additional action required.

**Future migration to a tag manager (required at Raptive integration).**
Raptive typically loads via a tag manager (their own or GTM). When we
onboard, replace the direct `gtag.js` loader block in
`/assets/js/consent-banner.js` (the block starting `s.async = true;
s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;`) with
the tag-manager container snippet Raptive provides, and drop the
`gtag('js', ...)` and `gtag('config', GA4_ID)` calls (the tag manager
takes over that role). Keep the inline consent-defaults snippet in
every `<head>` exactly as it is &mdash; Consent Mode v2 defaults must
still fire before any tag-manager container loads, so consent state is
propagated correctly.

Note: search-console verification file `google12f8c2f9c03913a3.html` is
already in place; Bing site-auth file `BingSiteAuth.xml` is also in place.
No handling needed at deploy &mdash; they just need to exist at the apex.

### 1b. Confirm brand treatment before deploy [DECISION NEEDED]

Phase 5.3 flagged the brand string spread across the site (report only,
nothing changed):

| Surface                    | Current value              |
|----------------------------|----------------------------|
| Header logo text           | `BMI Calculator`           |
| Nav labels                 | `BMI Calculator`           |
| Footer copyright / legal   | `Moving Data Systems d.o.o.` |
| og:site_name (all pages)   | `BMI Calculator`           |
| Article schema publisher   | `CalculateMyBMI.net`       |
| Page title suffix          | mixed &mdash; `| BMI Calculator` on most pages, `CalculateMyBMI.net` on `/about/` + `/privacy/`, no suffix on some |

Three consistent treatments to pick from:

- **Option A &mdash; "CalculateMyBMI.net" as the brand.** Retitle logo/nav
  to `CalculateMyBMI.net`. Publisher schema stays as-is. Standardize title
  suffixes to `| CalculateMyBMI.net`. Legal footer stays `Moving Data
  Systems d.o.o.` (that's the legal entity, not the brand).
- **Option B &mdash; "BMI Calculator" as the brand.** Change publisher
  schema from `CalculateMyBMI.net` to `BMI Calculator`. Standardize title
  suffixes to `| BMI Calculator`. Logo/nav stay.
- **Option C &mdash; leave it.** Not recommended: mixed brand strings hurt
  E-E-A-T signals and confuse rich-card previews. But this is not a
  Raptive-approval blocker in either direction.

If you pick A or B, this is 30 lines of `sed` and a re-commit. If you pick
C, the choice is fine as long as it's your intention on record. Nothing in
this repo depends on which you pick.

### 1c. Housekeeping (optional, not blockers)

- `/1516504244887.jpeg` at repo root is untracked and appears to be a
  screenshot artifact. Delete before deploy so it's not shipped:
  `rm /workspace/1516504244887.jpeg`
- `/.devcontainer/` is untracked. Vercel ignores it either way; commit
  or ignore, your call.
- `/BACKLOG.md` lists post-approval nice-to-haves (per-post OG images,
  author photo variants, og:image:alt).

---

## 2. DEPLOY PROCEDURE (Vercel, not git-connected)

Since Vercel is *not* wired to git, deploy is a two-step. All from the Mac
where the push is authoritative.

**Step 1 &mdash; push to GitHub (source of record only).**
```bash
git status              # confirm nothing unexpected
git log --oneline -12   # confirm the phase 5 commit is at HEAD
git push origin main
```

**Step 2 &mdash; deploy to Vercel.** Two paths:

- CLI: from the project root on your Mac,
  ```bash
  vercel --prod
  ```
  This deploys the current working directory as-is. Verify the
  `vercel.json` redirect list is picked up during build.

- Dashboard: Vercel dashboard &rarr; the CalculateMyBMI.net project &rarr;
  "Deployments" tab &rarr; "Redeploy" from the "..." menu on the previous
  production deployment, or drag-and-drop a fresh build.

**Do not deploy the `1516504244887.jpeg` or `.devcontainer/` if you are
using CLI upload &mdash; delete them from the working tree first, or add
to `.vercelignore`.**

---

## 3. POST-DEPLOY SMOKE TEST (5 minutes)

Open each in a fresh incognito window and verify visually. All should
be 200 unless noted.

Redirects (should hit 308 &rarr; final page):
- `https://calculatemybmi.net/blog/bmi-calculator-guide` &rarr; `/blog/what-is-bmi/`
- `https://calculatemybmi.net/blog/bmi-for-surgery/` &rarr; `/blog/bmi-categories/`
- `https://calculatemybmi.net/blog/bmi-chart-women/` &rarr; `/women-bmi-calculator/`
- `https://calculatemybmi.net/blog/ideal-weight-calculator/` &rarr; `/ideal-weight/`

Live pages (should be 200 with real content):
- `/` &mdash; homepage + calculator
- `/blog/` &mdash; 15-guide hub
- `/blog/what-is-bmi/`
- `/blog/bmi-categories/`
- `/blog/bmi-and-health-risks/`
- `/blog/underweight-bmi-risks/` &mdash; eating-disorder helpline block visible in amber
- `/kids-bmi-calculator/`
- `/about/` &mdash; author bio + Person schema
- `/privacy/`

404 test:
- `https://calculatemybmi.net/blog/this-does-not-exist/` &mdash; should render
  the styled custom 404 with links back to `/`, `/blog/`, `/calculators/`.

Analytics smoke:
- Open GA4 real-time. Load `/`. Confirm a session appears (only if in a
  region where consent is granted-by-default or after clicking Accept).
- From an EU/EEA IP or via a VPN/Chrome DevTools timezone override to
  `Europe/Berlin`: banner should show, no analytics event should fire
  until Accept.

GTM smoke:
- View source on `/`. Locate the deferred `consent-banner.js` script tag.
- Open network tab. Reload. Confirm `googletagmanager.com/gtm.js?id=<your-real-id>`
  request appears AFTER consent decision, not on initial load.

---

## 4. WHAT CHANGED IN EACH PHASE (auditor-ready summary)

**Phase 1 &mdash; truth + sources** (`32fc6d6`)
- Removed unverifiable claims sitewide; added source blocks to every article
  and calculator.
- Rewrote about + contact + privacy + terms with real legal-entity info.

**Phase 1b &mdash; citation triage** (`e4eec49`)
- Tier A (source properly): 52 URL replacements for institutional sources.
- Tier B (strip figures, keep claims): 19 rewrites across 8 non-cluster
  pages, removing specific x-fold / HR / percent-change claims attributed
  to homepages.
- Tier C (delete): `/blog/bmi-and-life-insurance/` deleted, sitemap + 308.

**Phase 1b &mdash; cluster consolidation** (`fd7b696`)
- Alt B approved (6 &rarr; 3). Absorbed content into 3 survivors before
  redirecting. Post-merge Tier B on `bmi-and-health-risks`.

**Phase 2a &mdash; absorbed content audit** (`04df0d4`)
- Pre-byline check: verified no absorbed content was fabricated. Emitted
  ABSORBED-AUDIT.md.

**Phase 2 &mdash; author identity / E-E-A-T** (`690702f`)
- Bylines added to every article; Person schema on `/about/`; canonical
  Person `@id` referenced from every article's Article schema.
- Corrected metabolic-syndrome citation to Alberti 2009 (later removed
  entirely per amendment E).

**Phase 3 &mdash; privacy + consent** (`b52f62a`)
- GTM (placeholder) + Consent Mode v2 defaults; geo-gated banner
  (Europe timezones + Atlantic offshore); consent-banner.js deferred.
- Privacy page rewritten to match actual behaviour.

**Phase 4 (partial) &mdash; SEO surface pre-work** (`415eadf`)
- 4.0: analytics.js split into inline (~1KB) + deferred external.
- 4.1: 7 search-volume badges stripped sitewide.
- 4.2: interlink density audit + pruning.
- 4.3: CONSOLIDATION-2.md written for all 33 blog posts.

**Phase 4 &mdash; SEO surface + consolidation** (`9d271ad`)
- Amendment A: `blog/bmi-for-surgery` deleted, 308 &rarr; `bmi-categories`.
- Amendment G: sitewide medical scope policy applied &mdash; treatment
  content, medication-by-name-or-class, bariatric candidacy, and
  disease-specific numeric risk quantification all removed. Eating-disorder
  helpline resources on `underweight-bmi-risks` promoted to prominent amber
  block. Site is now out of medical treatment entirely.
- Amendment E: metabolic syndrome demoted to one qualitative paragraph
  linking NHLBI; Alberti 2009 + Grundy 2005 citations removed with
  thresholds.
- Consolidation-2: 33 &rarr; 15 survivors. 22 conceptual redirects (44
  trailing-slash-paired rules), all 308, zero chains.

**Phase 5 &mdash; plumbing + final verify** (`(this commit)`)
- Images: 6 broken per-post OG URLs repointed to generic; 10 missing
  og:image tags filled in; all 29 pages now share `og-image.png`.
- Crawl surface: `robots.txt` expanded with explicit allow blocks for
  Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, GPTBot, Claude-User,
  Claude-SearchBot, ClaudeBot, PerplexityBot.
- Custom `/404.html` built, styled to match site, links back to `/`,
  `/blog/`, `/calculators/`, plus popular-pages grid.
- Metadata: 0 duplicate titles, 0 duplicate descriptions, exactly 1 H1
  per page across all 29 pages.
- Link graph: 0 broken internal links (only false positives on
  `<link rel=icon>` and stylesheet paths, which are non-anchor assets),
  0 references to redirected slugs, all 29 pages reachable in &le;2 hops
  from home.
- Schema: 0 JSON-LD parse failures; 0 references to deleted URLs;
  single canonical `Person @id` (about#author-bio) and single
  `Organization @id` (#organization); every breadcrumb trail matches
  the URL; FAQ Q&As on stripped pages remain content-aligned.
- Grep gate: 0 AdSense/pagead, 0 Phase 0.5 fabrications, 0 search-volume
  badges, 0 www references, 0 hardcoded gtag config outside GTM, 0
  metabolic-syndrome thresholds, 0 Tier B figures re-entered. Two
  Amendment G term hits &mdash; both anti-treatment meta-disclaimers, not
  treatment content: `contact/` ("not a treatment plan") and
  `kids-bmi-calculator/` ("not diagnostic criteria"). Both preserved as
  intended.

---

## 5. WHAT DID NOT CHANGE

Things the remediation deliberately left alone:
- `/assets/js/calculator.js` &mdash; calculation logic untouched.
- `/assets/css/styles.css` &mdash; visual design untouched.
- Individual calculator page structure (result cards, form controls) &mdash;
  only citations, sourcing, and amendment-G scope changed.
- SVG favicon and other logo assets.

---

## 6. KNOWN NON-BLOCKERS

- 22 conceptual redirects (not the earlier estimate of 24). Prior Phase 1b
  actually added 4, not 6 &mdash; verified in `git show fd7b696 e4eec49`.
  Every dying slug is covered; nothing is missing.
- `/blog/bmi-chart-explained/` has only 1 non-nav, non-footer inbound
  link (the blog hub itself). Consider adding cross-references from
  `bmi-formula`, `bmi-categories`, `healthy-bmi-range` in a future
  content refresh.
- `/terms/` has 0 non-footer inbound links. Expected for legal boilerplate.
- Per-post OG images: current sitewide generic fallback is functional but
  every social share looks the same. Backlog item.
