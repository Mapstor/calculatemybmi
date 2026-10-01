/* CalculateMyBMI.net — deferred GA4 gtag loader.
 * -----------------------------------------------------------------------------
 * The site's own consent banner has been removed. Consent is now managed by
 * Raptive's CMP, which sends Google Consent Mode signals via gtag('consent',
 * 'update', …). Every page's <head> carries Raptive's "Standard GA delay
 * script" (help.raptive.com/hc/en-us/articles/47199949578651), which sets
 * Consent Mode v2 defaults to denied for European visitors before this script
 * loads gtag.js; Raptive's CMP updates them after the visitor chooses.
 * ---------------------------------------------------------------------------*/

(function () {
  'use strict';

  var GA4_ID = 'G-QKNBZGZTW1';
  // Raptive's delay script only defines gtag for European visitors; define it here for everyone else.
  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== 'function') {
    window.gtag = function () { window.dataLayer.push(arguments); };
  }
  var gtag = window.gtag;

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  var first = document.getElementsByTagName('script')[0];
  if (first && first.parentNode) first.parentNode.insertBefore(s, first);
  else (document.head || document.documentElement).appendChild(s);
  gtag('js', new Date());
  gtag('config', GA4_ID);
})();
