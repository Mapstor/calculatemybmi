/* CalculateMyBMI.net — deferred: GTM loader + consent banner.
 * -----------------------------------------------------------------------------
 * This file loads AFTER HTML parse (via `defer` on the include). It runs only
 * after the inline head snippet has already:
 *   - created window.dataLayer and window.gtag
 *   - run the timezone geo heuristic (result on window.__cmbmiInScope)
 *   - read localStorage choice (on window.__cmbmiChoice)
 *   - fired gtag('consent','default',...) and any stored 'update'
 *
 * Ordering guarantee: the inline snippet is a synchronous <script> at the top
 * of <head>, so it executes before HTML parsing continues; this deferred
 * script executes only after HTML parsing completes. Consent defaults are
 * therefore set well before GTM is invoked below.
 *
 * Everything here is UI + late-firing. Nothing here blocks first paint.
 * The banner is position:fixed so it does not reflow the page — zero CLS.
 * ---------------------------------------------------------------------------*/

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // TODO(Marko): replace with the real GTM container ID from tagmanager.google.com
  // Format: 'GTM-XXXXXXX'. Until this is a real ID, GTM will 404 and no tags fire.
  // -------------------------------------------------------------------------
  var GTM_ID = 'GTM-PLACEHOLDER';

  // 1. Load GTM (defaults already set by the inline snippet)
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

  // 2. Reopen handler for footer "Cookie settings" link
  window.reopenConsentSettings = function () { showBanner(); };

  // 3. Auto-show banner for in-scope visitors who have not chosen yet
  if (window.__cmbmiInScope && !window.__cmbmiChoice) {
    // Defer is guaranteed to run before DOMContentLoaded per the HTML spec,
    // but the DOM may still be assembling — check readiness.
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }

  function showBanner() {
    if (document.getElementById('cmbmi-consent-banner')) {
      document.getElementById('cmbmi-consent-banner').style.display = 'block';
      return;
    }
    var b = document.createElement('div');
    b.id = 'cmbmi-consent-banner';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-labelledby', 'cmbmi-consent-text');
    b.style.cssText = [
      'position:fixed',
      'left:16px', 'right:16px', 'bottom:16px',
      'max-width:640px', 'margin:0 auto',
      'background:#164e63', 'color:#fff',
      'padding:1rem 1.25rem', 'border-radius:8px',
      'box-shadow:0 10px 30px rgba(0,0,0,0.35)',
      'z-index:2147483647',
      'font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif',
      'font-size:0.9375rem', 'line-height:1.5'
    ].join(';');

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

  function persist(v) {
    try { localStorage.setItem('cmbmi-consent', v); } catch (e) { /* denied — ephemeral */ }
    window.__cmbmiChoice = v;
  }
})();
