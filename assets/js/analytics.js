/* CalculateMyBMI.net — analytics.js
 * -----------------------------------------------------------------------------
 * NOTE: this file is now empty. The analytics pipeline is split into two
 * pieces to keep render blocking to zero:
 *
 *   1) An INLINE snippet in every page's <head> (baked into each HTML file):
 *      - dataLayer + gtag stub
 *      - timezone geo heuristic
 *      - Consent Mode v2 defaults (denied for in-scope, granted for out-of-scope)
 *      - applies any stored choice
 *
 *   2) /assets/js/consent-banner.js (loaded with `defer`):
 *      - GA4 gtag.js loader (async)
 *      Consent is now managed by Raptive's CMP, which sends gtag consent
 *      updates directly; no on-site banner or reopen handler is used.
 *
 * Ordering guarantee: the inline snippet is a synchronous <script> at the top
 * of <head>, so it executes before HTML parsing continues. The deferred file
 * executes only after HTML parsing completes. Consent defaults are therefore
 * set well before gtag.js is invoked.
 *
 * This stub is kept only to keep any accidental old `<script src="/assets/js/
 * analytics.js"></script>` references from 404-ing on a stale cache.
 * Every page has been migrated to the new pattern; nothing loads this file
 * intentionally.
 * ---------------------------------------------------------------------------*/
