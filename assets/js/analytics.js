/* CalculateMyBMI.net — analytics + consent, interim.
 * -----------------------------------------------------------------------------
 * This file is the SINGLE SOURCE OF TRUTH for tag loading and consent handling
 * across the site. Every HTML page pulls it via ONE synchronous script tag in
 * <head>:
 *
 *   <script src="/assets/js/analytics.js"></script>
 *
 * Interim design (Phase 3): plain Google Tag Manager + Consent Mode v2
 * defaults, geo-heuristic-gated banner for EEA/UK/CH. Raptive will replace this
 * with their CMP on approval; because everything lives in this one file plus
 * one include line per page, Phase-6 removal is a two-step delete.
 *
 * Container ID is a TODO placeholder — do NOT invent one. Marko creates the
 * GTM container and pastes the real ID before deploy.
 * ---------------------------------------------------------------------------*/

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // TODO(Marko): replace with the real GTM container ID from tagmanager.google.com
  // Format: 'GTM-XXXXXXX'. Until this is a real ID, GTM will 404 and no tags fire.
  // Nothing else in this file needs to change.
  // -------------------------------------------------------------------------
  var GTM_ID = 'GTM-PLACEHOLDER';

  // -------------------------------------------------------------------------
  // 1. dataLayer + gtag stub — must exist BEFORE anything else pushes to it.
  // -------------------------------------------------------------------------
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  // -------------------------------------------------------------------------
  // 2. Timezone-based geo heuristic. Not authoritative — no third-party geo
  //    API calls. Documented as a heuristic in the privacy policy.
  //    Europe/* covers EU + UK + CH + non-EEA European timezones; we then
  //    include the Atlantic timezones that map to European countries or
  //    dependencies commonly served under EEA/UK/CH scope.
  // -------------------------------------------------------------------------
  var tz = '';
  try {
    tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
  } catch (e) { /* very old browsers — leave tz empty, treat as in-scope */ }

  var inScope = /^Europe\//.test(tz) || tz === '' ||
                tz === 'Atlantic/Reykjavik' || tz === 'Atlantic/Faroe' ||
                tz === 'Atlantic/Azores' || tz === 'Atlantic/Madeira' ||
                tz === 'Atlantic/Canary';

  // -------------------------------------------------------------------------
  // 3. Existing consent choice (localStorage). Values: 'accept' | 'decline'.
  //    Anything else = no choice yet.
  // -------------------------------------------------------------------------
  var storedChoice = null;
  try { storedChoice = window.localStorage.getItem('cmbmi-consent'); }
  catch (e) { /* localStorage disabled — treat as no choice */ }

  // -------------------------------------------------------------------------
  // 4. Consent Mode v2 defaults. MUST fire before GTM loads.
  //    - ad_* stay denied for every visitor (no ads yet).
  //    - analytics_storage: denied for in-scope visitors until choice;
  //      granted for out-of-scope by default.
  //    - wait_for_update gives GTM time to receive an update before firing tags.
  // -------------------------------------------------------------------------
  gtag('consent', 'default', {
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': inScope ? 'denied' : 'granted',
    'wait_for_update': 500
  });

  // -------------------------------------------------------------------------
  // 5. If the visitor already chose, apply that choice as an update.
  // -------------------------------------------------------------------------
  if (storedChoice === 'accept') {
    gtag('consent', 'update', { 'analytics_storage': 'granted' });
  } else if (storedChoice === 'decline') {
    gtag('consent', 'update', { 'analytics_storage': 'denied' });
  }

  // -------------------------------------------------------------------------
  // 6. Load GTM. This is the standard container loader snippet from Google,
  //    inlined so the whole tagging pipeline lives in this one file.
  // -------------------------------------------------------------------------
  gtag('js', new Date());
  (function (w, d, s, l, i) {
    w[l] = w[l] || [];
    w[l].push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
    var f = d.getElementsByTagName(s)[0],
        j = d.createElement(s),
        dl = l !== 'dataLayer' ? '&l=' + l : '';
    j.async = true;
    j.src = 'https://www.googletagmanager.com/gtm.js?id=' + i + dl;
    if (f && f.parentNode) f.parentNode.insertBefore(j, f);
    else (d.head || d.documentElement).appendChild(j);
  })(window, document, 'script', 'dataLayer', GTM_ID);

  // -------------------------------------------------------------------------
  // 7. Banner. Shown only to in-scope visitors who have not chosen yet.
  //    Also exposed as window.reopenConsentSettings so footer links can
  //    let the user change their mind.
  // -------------------------------------------------------------------------
  window.reopenConsentSettings = function () { showBanner(true); };

  if (inScope && !storedChoice) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () { showBanner(false); });
    } else {
      showBanner(false);
    }
  }

  function showBanner(force) {
    if (document.getElementById('cmbmi-consent-banner')) {
      document.getElementById('cmbmi-consent-banner').style.display = 'block';
      return;
    }
    var b = document.createElement('div');
    b.id = 'cmbmi-consent-banner';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-labelledby', 'cmbmi-consent-text');
    b.style.cssText = [
      'position:fixed', 'left:16px', 'right:16px', 'bottom:16px',
      'max-width:640px', 'margin:0 auto',
      'background:#164e63', 'color:#fff',
      'padding:1rem 1.25rem', 'border-radius:8px',
      'box-shadow:0 10px 30px rgba(0,0,0,0.35)',
      'z-index:2147483647',
      'font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif',
      'font-size:0.9375rem', 'line-height:1.5'
    ].join(';');

    // One line of plain language; privacy-policy link.
    b.innerHTML =
      '<p id="cmbmi-consent-text" style="margin:0 0 0.75rem;">' +
      'We use Google Analytics cookies to count page views. Your calculator ' +
      'inputs stay in your browser. Accept or decline analytics? ' +
      '<a href="/privacy/" style="color:#a5f3fc;text-decoration:underline;">Privacy policy</a>.' +
      '</p>' +
      '<div style="display:flex;gap:0.75rem;flex-wrap:wrap;">' +
      '<button type="button" id="cmbmi-consent-accept" ' +
      'style="flex:1;min-width:120px;background:#06b6d4;color:#164e63;' +
      'border:0;padding:0.625rem 1rem;border-radius:6px;font-weight:600;' +
      'cursor:pointer;font-size:0.9375rem;">Accept</button>' +
      '<button type="button" id="cmbmi-consent-decline" ' +
      'style="flex:1;min-width:120px;background:transparent;color:#fff;' +
      'border:1px solid #a5f3fc;padding:0.625rem 1rem;border-radius:6px;' +
      'font-weight:600;cursor:pointer;font-size:0.9375rem;">Decline</button>' +
      '</div>';

    document.body.appendChild(b);

    document.getElementById('cmbmi-consent-accept').addEventListener('click', function () {
      persist('accept');
      gtag('consent', 'update', { 'analytics_storage': 'granted' });
      b.parentNode && b.parentNode.removeChild(b);
    });
    document.getElementById('cmbmi-consent-decline').addEventListener('click', function () {
      persist('decline');
      gtag('consent', 'update', { 'analytics_storage': 'denied' });
      b.parentNode && b.parentNode.removeChild(b);
    });
  }

  function persist(value) {
    try { window.localStorage.setItem('cmbmi-consent', value); }
    catch (e) { /* localStorage disabled — ephemeral choice, will re-ask next visit */ }
  }
})();
