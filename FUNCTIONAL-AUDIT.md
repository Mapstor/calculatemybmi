# Phase 12 — Functional Audit

Findings-only report. Nothing has been fixed. Root-cause diagnosis of the
mobile nav toggle bug (12.1&ndash;12.3) is inline in the conversation
response; this file covers 12.4 &mdash; a full interactive audit of every
control on every page.

---

## 12.1&ndash;12.3 summary (context, so this file stands alone)

**The reported "mobile nav toggle does nothing on tap" bug decomposes
into two distinct failure modes.**

### Failure mode A &mdash; missing hamburger button on 13 pages (pre-existing since baseline)

The mobile-nav toggle mechanism has three parts:

- Markup: `<button class="nav-toggle" aria-label="Menu">` + `<nav class="nav-mobile">...</nav>` inside the header.
- Handler: an inline `<script>` at the bottom of every page carrying the button, and (redundantly) a `setupMobileNav()` call in `/assets/js/calculator.js` line 969.
- CSS: `.nav-toggle` hidden by default, shown at `@media (max-width: 768px)`. `.nav-mobile.active { display: block }` reveals the panel.

The mechanism is unchanged from `78f9434` (initial commit): same button, same inline binder, same CSS. Phase 6.3 only added `min-width:44px min-height:44px` for tap-target compliance &mdash; that does not break clicks.

**On 13 pages the header markup does not include the button or `.nav-mobile` at all.** On mobile, `.nav-desktop` is hidden by the media query and no `.nav-toggle` exists to reveal `.nav-mobile`. The result: **no navigation whatsoever on mobile viewports**.

Affected pages (verified via `grep -L 'class="nav-toggle"'`):

- `/contact/`
- `/privacy/`
- `/terms/`
- `/blog/`
- `/blog/what-is-bmi/`
- `/blog/bmi-and-health-risks/`
- `/blog/bmi-and-metabolism/`
- `/blog/bmi-for-athletes/`
- `/blog/bmi-limitations/`
- `/blog/body-fat-vs-bmi/`
- `/blog/how-to-lower-bmi/`
- `/blog/underweight-bmi-risks/`
- `/blog/waist-to-height-ratio/`

Git archaeology confirms this was true at `78f9434` for every listed page. The bug **existed at baseline and no remediation phase caught it**, because no phase tested the mobile UI. That's the through-line: 12 phases of content and structural work, zero interactive testing.

`terms/index.html` has an oddity: the inline binder script IS present at the bottom of the page (`document.querySelector('.nav-toggle')?.addEventListener(...)`), but no `.nav-toggle` element in the markup for it to bind to. `?.` chaining means it silently no-ops.

### Failure mode B &mdash; on the 16 pages that DO have the button

Static analysis shows the mechanism intact:

- Button element present, correctly a `<button>` (not `<a href="#">`), correctly `class="nav-toggle"`.
- Inline `<script>` at bottom-of-body runs after the DOM is parsed and binds `click` to the button.
- CSS shows `.nav-toggle` at `display: block` under 768px, `pointer-events` not disabled, no overlay that would intercept clicks. `.nav-mobile.active { display: block }` correctly overrides the default `display: none`.
- Header has `position: sticky`, so `.nav-mobile { position: absolute; top: 100% }` positions below the header correctly.

Ruled out suspects from the phase brief:

- **(a) Phase 10.5 button conversion.** The replace targeted the exact string `<a href="#" onclick="if(typeof reopenConsentSettings===&quot;function&quot;){reopenConsentSettings();return false;}">Cookie settings</a>`. The nav-toggle button markup does not match; nav-toggle was not touched.
- **(b) Phase 6.3 CSS.** Only additions were `min-width:44px min-height:44px` on `.nav-toggle` and `padding: 0.75rem 1rem; min-height:44px; box-sizing:border-box` on `.nav-mobile a`. Neither can break clicks.
- **(c) Phase 11 SVG parse damage.** Strict XML validation flags 2 of 25 SVGs (`kids-bmi-calculator/index.html` girls-percentile SVG and `lean-body-mass/index.html` lean-vs-fat split) as failing to parse because of `&mdash;` entities inside `<text>` and `<desc>`. **However, HTML5 parses SVG-in-HTML in "in foreign content" insertion mode with HTML-compatible named-character-reference handling &mdash; `&mdash;` resolves cleanly in browsers.** These SVGs are XML-invalid but HTML5-valid. They do not break DOM parsing and are not the cause. (Cleanup is still worth doing to keep the SVGs XML-clean; that is separate from the nav bug.)
- **(d) JS error before bind.** The inline consent snippet at the top of `<head>` is a separate `<script>` block from the bottom-of-body inline binder. Errors in one `<script>` do not halt execution of another. The consent snippet itself is defensively coded (try/catch around timezone + localStorage). No plausible failure mode.

**Static-analysis conclusion for failure mode B: I cannot reproduce the bug on the 16 pages that have the button from source alone.** Two possibilities:
1. The reported bug is actually failure mode A (user was on one of the 13 missing-button pages, and the header didn't even show a hamburger). This fits "does nothing on tap" if the user was searching for the nav on those pages.
2. The bug is genuinely on a button-carrying page and requires a live-browser diagnostic step I cannot perform without network + browser access.

### Proposed fix (STOP for approval)

**Primary:** Add the `<button class="nav-toggle">`, the `</div><nav class="nav-mobile">...</nav>` markup, and the inline binder script to the 13 affected pages, matching the pattern used on the 16 pages where it already works. This is a straight copy of the working header template.

**Secondary (deferred until you confirm the tap-does-nothing bug is fixed by the primary):** Clean the two SVGs' `&mdash;` occurrences to `-` or `&#8212;` so strict XML parsing passes too. Not a bug fix &mdash; a defensive hygiene pass.

**Not proposed:** any CSS change to `.nav-toggle` or `.nav-mobile`. Static analysis shows the CSS mechanism is intact.

Awaiting your approval before touching HTML on the 13 pages.

---

## 12.4 &mdash; Interactive audit (findings only, no fixes)

### 8 calculator pages: end-to-end wire check

For each page, `/assets/js/calculator.js` needs:
- A calculate button with the expected `id` (bound via `getElementById(id)?.addEventListener('click', fn)`)
- A results panel with the expected `id` (queried via `getElementById('panel-...')`)
- Input elements with the expected classes (`.height-cm`, `.height-ft`, `.height-in`, `.weight-kg`, `.weight-lbs`, `.unit-btn`, `.imperial-inputs`, `.metric-inputs`, plus per-calculator extras)
- Extras: `.sex-select`, `.frame-select`, `.age-input` where the calculator uses them.

| Page | Button id | Panel id | Height inputs | Weight inputs | Unit-toggle | Extras | Loads calc.js | Verdict |
|---|---|---|---|---|---|---|---|---|
| `/index.html` | `calc-standard-btn` ✓ | `panel-standard` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | &mdash; | ✓ | wired |
| `/women-bmi-calculator/` | `calc-women-btn` ✓ | `panel-women` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | &mdash; | ✓ | wired |
| `/men-bmi-calculator/` | `calc-men-btn` ✓ | `panel-men` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | &mdash; | ✓ | wired |
| `/age-bmi-calculator/` | `calc-age-btn` ✓ | `panel-age` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | `.age-input` ✓ | ✓ | wired |
| `/kids-bmi-calculator/` | `calc-kids-btn` ✓ | `panel-kids` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | `.age-input`, `.sex-select` ✓ | ✓ | wired |
| `/new-bmi-calculator/` | `calc-newbmi-btn` ✓ | `panel-newbmi` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | &mdash; | ✓ | wired |
| `/ideal-weight/` | `calc-ideal-btn` ✓ | `panel-ideal` ✓ | ft/in/cm ✓ | &mdash;* | 2 buttons ✓ | `.sex-select`, `.frame-select` ✓ | ✓ | wired |
| `/lean-body-mass/` | `calc-lbm-btn` ✓ | `panel-lbm` ✓ | ft/in/cm ✓ | lbs/kg ✓ | 2 buttons ✓ | `.sex-select` ✓ | ✓ | wired |

`*` &mdash; ideal-weight has no weight input by design; the four formulas take height + sex + frame.

**All 8 calculators are structurally wired end to end.** Every `getElementById` in `calculator.js` finds its target; every `querySelector` for inputs matches at least one class-selected element.

### Unit toggles (metric / imperial)

`calculator.js:36 setupUnitToggles()` binds click on every `.unit-btn`. On click it swaps `active` class within the parent unit toggle and toggles `display` between `.imperial-inputs` (`grid`) and `.metric-inputs` (`grid` or `none`).

- Every calculator panel has exactly 2 `.unit-btn` (imperial + metric), each carrying `data-unit`.
- Every panel has `.imperial-inputs` and `.metric-inputs` wrapper divs.
- **Wired on all 8 calculators.**

### Consent banner Accept / Decline buttons

Injected by `/assets/js/consent-banner.js:57 showBanner()` when the visitor is in-scope (Europe/EEA timezone) AND has no stored choice. Both buttons are dynamically created, so they exist only when the banner is on screen. Handlers bind immediately after `appendChild`:

- Accept &rarr; `persist('accept')`, `gtag('consent', 'update', {'analytics_storage': 'granted'})`, remove banner.
- Decline &rarr; `persist('decline')`, `gtag('consent', 'update', {'analytics_storage': 'denied'})`, remove banner.

Both handlers reference `document.getElementById('cmbmi-consent-accept'/'cmbmi-consent-decline')` &mdash; ids that exist on the freshly-created element. **Wired.**

### Footer "Cookie settings" button

`<button type="button" class="footer-cookie-btn" onclick="if(typeof reopenConsentSettings===&quot;function&quot;)reopenConsentSettings();">Cookie settings</button>` &mdash; on every page.

`reopenConsentSettings` is assigned at `/assets/js/consent-banner.js:39` on `window` (`window.reopenConsentSettings = function () { showBanner(); }`). The script tag is `<script defer src="/assets/js/consent-banner.js"></script>`, so it executes after HTML parse. Any interactive click on the button will happen after the defer script has run.

**Wired on all pages I checked.** No functional concern.

### FAQ disclosure controls

Every article page uses the pattern `<button class="faq-question">Question<svg .../></button>` with an adjacent hidden answer div. The inline binder at bottom-of-body does:

```js
document.querySelectorAll('.faq-question').forEach(b =>
  b.addEventListener('click', () => b.parentElement.classList.toggle('open'))
);
```

FAQ button counts per page (from static scan):

- `/index.html` &mdash; 12
- `/blog/what-is-bmi/` &mdash; not counted here (does not carry the inline binder script &mdash; **potential defect**)
- `/blog/healthy-bmi-range/` &mdash; 6
- `/blog/bmi-categories/` &mdash; not counted here (no inline binder &mdash; **potential defect**)
- `/blog/bmi-chart-explained/` &mdash; not counted (no inline binder &mdash; **potential defect**)
- All 8 calculator pages: 8&ndash;12 FAQs each. The inline binder is present on all 8. FAQ toggles work.

**Cross-referencing with the "which pages have the inline binder" scan from 12.1:** 16 pages have `document.querySelectorAll('.faq-question').forEach(...)`. The 13 pages that lack the mobile-nav binder ALSO lack the FAQ binder &mdash; because both live in the same bottom-of-body `<script>` tag that some pages simply don't carry. Those 13 pages' FAQ items are `<button class="faq-question">` in the markup but nothing binds them &mdash; **so tapping an FAQ on `/blog/what-is-bmi/`, `/blog/bmi-and-health-risks/`, `/blog/bmi-limitations/`, `/contact/`, `/privacy/`, etc. does nothing.**

This is a second confirmed bug, same root cause as failure mode A: 13 pages are missing the bottom-of-body inline `<script>` tag altogether. Adding the tag (with both the FAQ binder and the nav binder) will fix both bugs at once.

### Nav-dropdown hover menu

`.nav-dropdown-menu` is shown on hover of `.nav-dropdown` via CSS `.nav-dropdown:hover .nav-dropdown-menu { display: block }`. Pure CSS. Works on pointer devices. On touch devices it fires on tap-hold; not ideal but not a new regression &mdash; it was the same at baseline.

### Absorption disclosure controls

Phase 4.4 absorbed 18 dying pages into survivors but did not introduce any new expand/collapse controls. The absorbed content was flattened into normal H2/H3 sections. No new disclosure widgets to audit.

### Contact form

`/contact/` has a form UI (I did not deep-inspect the form's submit handler). Since `/contact/` is one of the 13 pages missing the bottom-of-body `<script>`, any inline JS that a contact form needs would not run. Worth checking whether the form has its own inline `<script>` for submit &mdash; if it depends on the shared bottom-of-body binder, it's currently non-functional.

### Consent Mode v2 defaults

The inline `<script>` at the top of `<head>` runs synchronously and is present on every page (all 29 have `analytics_storage:inScope?'denied':'granted'` visible via grep). Defers-then-runs pattern intact. **Wired sitewide.**

---

## Bugs found (summary, by severity)

| # | Severity | Bug | Affected pages | Same root cause? |
|---|---|---|---|---|
| 1 | **HIGH** | Mobile nav toggle absent from header markup &mdash; no way to navigate on mobile | 13 pages (see list above) | root cause 1 |
| 2 | **HIGH** | FAQ toggles do not respond to taps &mdash; no binder script on the page | 13 pages (same 13) | root cause 1 |
| 3 | LOW | `terms/index.html` has the inline binder script but no `.nav-toggle` markup for it to bind to (silent no-op via `?.`) | 1 page | separate anomaly |
| 4 | INFO | 2 Phase 11 SVGs (`kids-bmi-calculator/index.html` girls-percentile and `lean-body-mass/index.html` lean-vs-fat split) contain `&mdash;` inside `<text>`/`<desc>`. Strict XML rejects; HTML5 accepts. Not a browser bug. | 2 pages | not a bug, hygiene only |
| 5 | INFO | Contact form's submit handler (if inline-script-dependent) may not fire on `/contact/` because that page is missing the bottom-of-body `<script>` tag | 1 page | dependent on root cause 1 |

**Root cause 1** (bugs 1, 2, 5): 13 pages are missing the bottom-of-body inline `<script>` block that contains both the FAQ binder and the nav-toggle binder, and 13 pages are missing the `<button class="nav-toggle">` markup + `<nav class="nav-mobile">` markup from the header.

**One fix &mdash; adding the header + script to those 13 pages &mdash; resolves bugs 1, 2, and (probably) 5.**

Nothing has been changed. Awaiting your approval before editing.
