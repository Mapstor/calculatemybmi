/* CalculateMyBMI.net — deferred GA4 gtag loader.
 * -----------------------------------------------------------------------------
 * The site's own consent banner has been removed. Consent is now managed by
 * Raptive's CMP, which sends Google Consent Mode signals via gtag('consent',
 * 'update', …). The inline <head> snippet on every page still sets the
 * Consent Mode v2 defaults (ad_storage / analytics_storage denied for EEA
 * visitors) before this script loads gtag.js, so GA4 honours those defaults
 * until Raptive's CMP updates them.
 * ---------------------------------------------------------------------------*/

(function () {
  'use strict';

  var GA4_ID = 'G-QKNBZGZTW1';

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  var first = document.getElementsByTagName('script')[0];
  if (first && first.parentNode) first.parentNode.insertBefore(s, first);
  else (document.head || document.documentElement).appendChild(s);
  gtag('js', new Date());
  gtag('config', GA4_ID);
})();
