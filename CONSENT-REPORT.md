# CONSENT-REPORT.md — Phase 3

Summary of the privacy + consent work: what was rewritten, what was added, what was
verified, and what remains for you to do before deploy.

---

## 3.1 Privacy policy — rewrite

`/workspace/privacy/index.html` fully rewritten to match what actually runs.

**Sections in the new policy:**
1. What actually runs on this site (calculators, GA4, server logs, email &mdash; and explicitly: no advertising currently)
2. What we collect (per category, with GA4 sub-list)
3. Legal basis for processing under GDPR (consent for analytics, legitimate interests for logs and email)
4. Cookies in use (GA4 first-party only) + GA opt-out link (retained per spec)
5. Consent handling (Consent Mode v2, geo-heuristic, banner behaviour)
6. Retention (server logs, analytics, email)
7. GDPR rights, including the right to lodge a complaint with the Slovenian Information Commissioner
8. CCPA / CPRA rights (California)
9. Third parties (Google only, plus the hosting provider processing HTTP logs)
10. Changes-to-policy clause
11. Children's data (13/16 threshold as applicable)
12. Contact (controller: Moving Data Systems d.o.o., Maribor, Slovenia)
&mdash; Plus a &ldquo;Privacy at a glance&rdquo; summary at the end.

**Deleted (or never re-added) as instructed:**
- Every reference to Google AdSense (old §1, §4.3, §5.2, §7.2, §9, §Summary bullet)
- Every ad-tech opt-out URL: adssettings.google.com, optout.aboutads.info, optout.networkadvertising.org, google.com/settings/ads, policies.google.com/technologies/ads, policies.google.com/technologies/partner-sites
- All forward-looking advertising language

**Terms of Service (`/workspace/terms/index.html`)** §8 was still titled &ldquo;Advertising&rdquo; and cited AdSense + two ad-tech opt-out URLs. Rewritten to &ldquo;Third-party services&rdquo; describing only GA4 (with pointer to privacy policy) and noting that advertising, if added, will be preceded by policy updates.

**No `/ads.txt` file created.** Raptive supplies the entries on approval; a fabricated one is worse than none.

**GA4 retention:** described generically (2 or 14 months per the GA4 property setting). The current codebase does not set retention in the client-side tag (GA4 retention is configured in the Google Analytics admin console, not in the tag config), so the policy points to the console setting rather than stating a specific number.

---

## 3.2 Privacy claims scoped sitewide

Sitewide grep found **5** blanket privacy claims outside `/privacy/`. All 5 are on `about/index.html` and were reworded to distinguish (a) calculator inputs (client-side, not transmitted) from (b) what the site does collect (GA4 cookies, HTTP logs).

| File | Line (before) | Old text (excerpt) | New text (summary) |
|---|---:|---|---|
| `about/index.html` | 191 | &ldquo;All calculations run locally in your browser. We never collect or store your health data.&rdquo; (H3: &ldquo;Privacy First&rdquo;) | H3 renamed to &ldquo;Health inputs stay local&rdquo;. Body: &ldquo;All calculator inputs are processed in your browser and never reach our servers. See the privacy policy for what we do collect (Google Analytics 4 cookies and standard server logs).&rdquo; |
| `about/index.html` | 275 | &ldquo;No data is transmitted to our servers or any third-party service. This means your health information never leaves your computer, tablet, or phone.&rdquo; | Scoped to &ldquo;those specific inputs are not transmitted... What the site does collect (GA4 cookies, standard HTTP server logs) is described in the privacy policy.&rdquo; |
| `about/index.html` | 338 | Privacy tile: &ldquo;No Data Collection&rdquo; / &ldquo;Your height, weight, age, and BMI results are never sent to our servers or stored in any database.&rdquo; | Tile heading renamed to &ldquo;Calculator inputs stay local&rdquo;. Copy unchanged in substance (was already correctly scoped). |
| `about/index.html` | 344 | Privacy tile: &ldquo;Local Processing&rdquo; / &ldquo;All calculations run entirely in your browser. Your data never leaves your device.&rdquo; | Heading renamed to &ldquo;Client-side calculation&rdquo;. Copy: &ldquo;All arithmetic runs in JavaScript on your device. The specific inputs you type into a calculator are not transmitted from your device.&rdquo; |
| `about/index.html` | 354 | Privacy tile: &ldquo;Full Transparency&rdquo; (pointer to policy) | Renamed to &ldquo;What we do collect&rdquo; with a summary: &ldquo;Google Analytics 4 cookies (with consent for EEA/UK/CH visitors) and standard HTTP server logs.&rdquo; |
| `about/index.html` | 358 | &ldquo;Because all calculator inputs are processed client-side using JavaScript, there is no server-side logging of your health data. We do not use tracking pixels, fingerprinting, or any other technique to associate your identity with your calculator inputs.&rdquo; | Reworded: two things happen (client-side calc + analytics/logs). Removed the &ldquo;no tracking pixels, fingerprinting&rdquo; blanket. Notes the site does not currently serve advertisements. |
| `about/index.html` | 377 (FAQ) | &ldquo;Your height, weight, age, sex, and calculated results are never transmitted to our servers or any third party. We do not store your health data in any database, and we do not use cookies or other tracking mechanisms to record your calculator inputs.&rdquo; | Reworded to keep the accurate scoped claim (calculator inputs stay local; no cookie records what you typed) and add the honest disclosure of GA4 cookies + HTTP server logs with a pointer to the privacy policy. |

Post-fix grep for &ldquo;no cookies&rdquo; / &ldquo;no tracking&rdquo; / &ldquo;never transmit&rdquo; / &ldquo;never leaves&rdquo; / &ldquo;never collect&rdquo; / &ldquo;we do not use cookies&rdquo; / &ldquo;100% private&rdquo; / &ldquo;complete privacy&rdquo; outside `/privacy/`: **zero remaining blanket claims.**

---

## 3.3 GA4 → GTM migration + single source of truth

**Single-source file:** `/workspace/assets/js/analytics.js` (162 lines including comments). Contains, in order:

1. `dataLayer` + `gtag` stub (must exist first).
2. Timezone-based geo heuristic (`Intl.DateTimeFormat().resolvedOptions().timeZone`). No third-party geo API calls. In-scope = `Europe/*` timezones plus a small set of Atlantic timezones tied to European countries (Azores, Madeira, Canaries, Faroe, Iceland). Empty timezone (very old browser) treated as in-scope by default.
3. Read existing consent choice from `localStorage.getItem('cmbmi-consent')`.
4. `gtag('consent', 'default', ...)` &mdash; the four Consent Mode v2 signals, geo-gated per §3.4. `wait_for_update: 500` gives GTM time to receive an update before firing tags.
5. `gtag('consent', 'update', ...)` if the visitor already chose.
6. Standard GTM container loader (from Google's template) using `GTM_ID` constant.
7. Banner: shown to in-scope visitors with no stored choice; also exposed as `window.reopenConsentSettings` for the footer link.

**GTM container ID placeholder:** the constant is `var GTM_ID = 'GTM-PLACEHOLDER';` in `analytics.js`, marked with a `TODO(Marko)` comment on the four lines above it. **Do NOT deploy until you have replaced this with a real container ID from tagmanager.google.com.** While it says `GTM-PLACEHOLDER`, GTM requests will 404 and no tags will fire &mdash; which is a safe default state, not a broken one.

**Per-page migration:** the hardcoded gtag snippet (`www.googletagmanager.com/gtag/js?id=G-QKNBZGZTW1` + inline `gtag('config',...)`) was replaced on 46 pages via one scripted transform. Every page now pulls exactly one line:

```html
<script src="/assets/js/analytics.js"></script>
```

Placement: first tag in `<head>`, synchronous (not `async` / not `defer`) so consent defaults fire before anything else on the page loads its own scripts. Phase-6 removal is a two-step delete: remove the file, remove the include line via the same transform in reverse.

Coverage after migration: **47 pages include `analytics.js`.** The one HTML file that doesn't &mdash; `/workspace/google12f8c2f9c03913a3.html` &mdash; is a Google-supplied Webmaster verification file that contains only the verification string, no analytics needed.

---

## 3.4 Interim geo-gated consent gate

- **Consent Mode v2 defaults (fired before GTM loads):**
  - `ad_storage: denied` for everyone (no ads yet).
  - `ad_user_data: denied` for everyone.
  - `ad_personalization: denied` for everyone.
  - `analytics_storage`: `denied` for in-scope visitors (EEA/UK/CH by timezone); `granted` for out-of-scope visitors.
  - `wait_for_update: 500`.

- **Geo detection heuristic:** timezone via `Intl.DateTimeFormat().resolvedOptions().timeZone`. Matches `Europe/*` plus five Atlantic timezones mapped to European countries. Documented in the privacy policy as a heuristic, not authoritative. No third-party geo API calls.

- **Banner (shown only to in-scope visitors with no stored choice):**
  - Fixed to bottom, structured `<div id="cmbmi-consent-banner" role="dialog" aria-labelledby="cmbmi-consent-text">`.
  - One line of plain language: &ldquo;We use Google Analytics cookies to count page views. Your calculator inputs stay in your browser. Accept or decline analytics?&rdquo; + link to `/privacy/`.
  - Two equally prominent buttons: Accept (primary color, filled) and Decline (outlined, same size, same padding, same weight). No pre-ticked boxes. Decline is not harder to reach than Accept.
  - Choice persisted in `localStorage.setItem('cmbmi-consent', 'accept'|'decline')`.

- **Reopen link:** `window.reopenConsentSettings` calls the banner again. Every one of the 47 pages loading `analytics.js` has a &ldquo;Cookie settings&rdquo; link in the footer (Legal nav for 28 pages, minimal footer copyright line for 18, and one page has both a full Legal nav plus the reopen link there).

- **Interim disposability:** the banner CSS is inline in the JS file, so removing it is a single deletion. The banner does not depend on any site stylesheet.

- **Global default-deny switch:** the `inScope` flag drives the analytics_storage default. If you tell me &ldquo;global default-deny&rdquo;, I flip this one boolean and nothing else in the file changes.

---

## 3.5 Verification

**AdSense / adsbygoogle / ca-pub / pagead2:** sitewide grep returns **zero hits.**

**Hardcoded `gtag('config','G-...')`:** sitewide grep returns **zero hits** outside `analytics.js`. `analytics.js` itself does not call `gtag('config',...)` &mdash; GTM handles GA4 initialization.

**Ad-tech opt-out URLs** (`adssettings.google.com`, `optout.aboutads.info`, `optout.networkadvertising.org`, `google.com/settings/ads`, `policies.google.com/technologies/ads`, `policies.google.com/technologies/partner-sites`): sitewide grep returns **zero hits.**

**GA opt-out link retained** (`tools.google.com/dlpage/gaoptout`): kept on `/privacy/` as specified.

**No analytics cookie set before consent for in-scope visitors** &mdash; verified by:
1. Consent Mode v2 defaults for `analytics_storage` set to `denied` for in-scope visitors *before* the GTM loader is invoked (step 4 fires before step 6 in `analytics.js`).
2. GTM respects the Consent Mode v2 defaults and does not fire GA4 tags until `analytics_storage` is `granted`.
3. GA4 first-party cookies (`_ga`, `_ga_*`) are set by the GA4 tag, not by GTM directly, so if the tag does not fire, no cookie is set.
4. Because the `GTM_ID` constant is currently `GTM-PLACEHOLDER`, GTM itself 404s in the browser and no tags fire at all &mdash; a stronger guarantee than consent gating alone. Once Marko sets a real ID, the consent gate becomes the operative control.

**`ads.txt` file:** not present. Correct.

**Footer &ldquo;Cookie settings&rdquo; link:** on 47 / 47 pages that load `analytics.js`.

---

## What Marko needs to do before deploy

1. Create a Google Tag Manager container at tagmanager.google.com; paste the container ID (`GTM-XXXXXXX` form) into `/workspace/assets/js/analytics.js` in place of `GTM-PLACEHOLDER` (line marked `TODO(Marko)`). Configure GA4 as a tag inside GTM referencing your existing GA4 property.
2. Confirm the GA4 property is receiving events (Realtime report in GA4 admin) &mdash; Raptive review depends on GA being live.
3. Verify GA4 data retention setting in the GA4 admin (Admin &rarr; Data Settings &rarr; Data Retention). The privacy policy points readers to whatever value is set there.
4. When Raptive approves and sends CMP integration instructions, remove `/workspace/assets/js/analytics.js` and the 47 script-tag include lines, and drop in Raptive's snippet.
