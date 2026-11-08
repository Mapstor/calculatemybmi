() => {
  /* CMB-029: every piece of text a reader meets on the page, as units.
     main prose (one unit per run of text inside one block element), table rows, SVG <text>,
     FAQ questions and answers, FAQPage JSON-LD answers, title, meta description.
     <sup>/<sub> digits come back as Unicode super/subscripts, so "1.75<sup>2</sup>" reads 1.75², not 1.752. */
  const main = document.querySelector('main');
  const SKIP = 'script,style,noscript,template,form,input,select,option,textarea,label,.byline';
  const INLINE = new Set(['inline', 'contents', 'none']);
  const SUP = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '.': '·', '-': '⁻', '+': '⁺' };
  const SUB = { '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉', '.': '.', '-': '₋', '+': '₊' };
  const clean = s => s.replace(/\s+/g, ' ').trim();
  const nodeText = n => {
    const p = n.parentElement;
    if (p && p.closest('sup')) return n.nodeValue.replace(/[0-9.+-]/g, c => SUP[c]);
    if (p && p.closest('sub')) return n.nodeValue.replace(/[0-9.+-]/g, c => SUB[c]);
    return n.nodeValue;
  };
  const blockOf = el => {
    while (el && el !== main) {
      const d = getComputedStyle(el).display;
      if (!INLINE.has(d) || ['TD', 'TH', 'LI', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'DT', 'DD', 'FIGCAPTION', 'CAPTION', 'BLOCKQUOTE'].includes(el.tagName)) return el;
      el = el.parentElement;
    }
    return main;
  };
  const elText = el => {
    // text of an element; a space wherever the text moves to another block or inline-block (legends, scales, chips)
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    let s = '', n, lastBlock = null;
    while ((n = tw.nextNode())) {
      if (n.nodeType === 3) {
        if (n.parentElement.closest('script,style')) continue;
        const b = blockOf(n.parentElement);
        if (lastBlock && b !== lastBlock) s += ' ';
        lastBlock = b;
        s += nodeText(n);
      } else if (n.tagName === 'BR') s += ' ';
    }
    return clean(s);
  };
  const heads = [...main.querySelectorAll('h1,h2,h3,h4')];
  const headingBefore = el => {
    let best = '';
    for (const h of heads) {
      if (h === el || h.contains(el) || el.contains(h)) continue;
      if (h.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) best = clean(h.textContent);
    }
    return best;
  };
  const visible = el => !!(el.getClientRects && el.getClientRects().length);
  const cls = el => (typeof el.className === 'string' ? el.className : (el.className && el.className.baseVal) || '');
  const ctxOf = b => {
    let p = b.parentElement, t = '';
    for (let k = 0; p && k < 3; k++, p = p.parentElement) { t = elText(p); if (t.length > elText(b).length + 3) break; }
    return t.slice(0, 600);
  };
  const runs = (root, region, extra, exclude) => {
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    let cur = null; const out = [];
    let n;
    while ((n = tw.nextNode())) {
      if (n.nodeType === 1) {
        if (n.tagName === 'BR' && cur) cur.text += '\n';
        continue;
      }
      const p = n.parentElement;
      if (!p || p.closest(SKIP) || (exclude && exclude(p))) { cur = null; continue; }
      const b = blockOf(p);
      if (!cur || cur.block !== b) { cur = { block: b, text: '', links: [], region, ...extra }; out.push(cur); }
      const a = p.closest('a');
      const start = cur.text.length;
      cur.text += nodeText(n);
      if (a && a.getAttribute('href')) cur.links.push({ start, end: cur.text.length, href: a.href, text: clean(a.textContent) });
    }
    return out.filter(u => u.text.trim()).map(u => {
      const b = u.block;
      const blockLinks = [...b.querySelectorAll('a[href]')].map(a => a.href);
      const r = { ...u, tag: b.tagName.toLowerCase(), cls: cls(b), visible: visible(b), heading: headingBefore(b), ctx: ctxOf(b), blockLinks, inResults: !!b.closest('[id$="-results"]'), inCite: !!b.closest('cite, .sources, .references, .source-list, .sources-list, .refs') };
      delete r.block;
      return r;
    });
  };
  const units = [];
  const inTable = el => !!el.closest('table');
  const inSvg = el => !!el.closest('svg');
  const inFaq = el => !!el.closest('.faq-item');
  runs(main, 'main', {}, el => inTable(el) || inSvg(el) || inFaq(el)).forEach(u => units.push(u));
  // Tables: one unit per row; cells keep their own text, the header row gives each cell its column name.
  [...main.querySelectorAll('table')].forEach((t, ti) => {
    if (t.closest(SKIP)) return;
    const rows = [...t.rows];
    const isHead = r => r.parentElement.tagName === 'THEAD' || [...r.cells].every(c => c.tagName === 'TH');
    const headRows = rows.filter(isHead);
    const colHead = headRows.length ? [...headRows[headRows.length - 1].cells].map(elText) : [];
    // the source line under the table: the first following element in the same section that starts like one
    let after = t.closest('.table-responsive, .table-wrap, .table-container') || t;
    let next = after.nextElementSibling, note = '', noteLinks = [];
    for (let hops = 0; next && hops < 6 && !/^H[12]$/.test(next.tagName); hops++, next = next.nextElementSibling) {
      if (/^(source|sources|data|note|notes|calculated|values|thinness|\*|†)/i.test(elText(next)) || (/^(P|FIGCAPTION|SMALL|DIV)$/.test(next.tagName) && /\bSources?:/i.test(elText(next)))) { note = elText(next).slice(0, 600); noteLinks = [...next.querySelectorAll('a[href]')].map(a => a.href); break; }
    }
    const capLinks = t.caption ? [...t.caption.querySelectorAll('a[href]')].map(a => a.href) : [];
    rows.forEach((r, ri) => {
      const cells = [...r.cells].map(elText);
      if (!cells.some(c => c)) return;
      const links = [...r.querySelectorAll('a[href]')].map(a => ({ start: 0, end: 0, href: a.href, text: clean(a.textContent) }));
      units.push({ region: 'table', text: cells.join(' | '), cells, links, table: ti, row: ri, isHead: isHead(r), colHead, caption: t.caption ? elText(t.caption) : '', note, blockLinks: capLinks.concat(noteLinks), heading: headingBefore(t), tag: 'tr', cls: cls(t), visible: visible(r), inResults: !!t.closest('[id$="-results"]'), ctx: '' });
    });
  });
  // SVG text: one unit per <text>, with the figure's label and caption for context.
  [...main.querySelectorAll('svg')].forEach((s, si) => {
    if (s.closest(SKIP)) return;
    const texts = [...s.querySelectorAll('text')];
    if (!texts.length) return;
    const fig = s.closest('figure');
    const label = s.getAttribute('aria-label') || (s.querySelector('title') ? s.querySelector('title').textContent : '');
    const all = texts.map(t => clean(t.textContent)).join(' · ');
    texts.forEach((t, k) => {
      const text = clean(t.textContent);
      if (!text) return;
      let cx = null, cy = null;
      try { const b = t.getBBox(); cx = b.x + b.width / 2; cy = b.y + b.height / 2; } catch (e) {}
      units.push({ region: 'svg', text, links: [], svg: si, idx: k, cx, cy, svgLabel: clean(label), figcaption: fig && fig.querySelector('figcaption') ? elText(fig.querySelector('figcaption')) : '', heading: headingBefore(s), tag: 'text', cls: cls(t), visible: visible(t), inResults: !!s.closest('[id$="-results"]'), ctx: all.slice(0, 600), blockLinks: fig ? [...fig.querySelectorAll('a[href]')].map(a => a.href) : [] });
    });
  });
  // FAQ: the question, then the answer's blocks (answers are often collapsed; their text is read all the same).
  [...main.querySelectorAll('.faq-item')].forEach((f, fi) => {
    const q = f.querySelector('.faq-question');
    const qt = q ? elText(q) : '';
    if (q) units.push({ region: 'faq-q', text: qt, links: [], faq: fi, question: qt, heading: 'FAQ', tag: 'button', cls: '', visible: true, inResults: false, ctx: '', blockLinks: [] });
    const a = f.querySelector('.faq-answer');
    if (a) runs(a, 'faq-a', { faq: fi, question: qt }).forEach(u => { u.heading = 'FAQ: ' + qt; units.push(u); });
  });
  const ld = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
    try {
      const d = JSON.parse(s.textContent);
      const items = Array.isArray(d) ? d : (d['@graph'] || [d]);
      items.forEach(it => {
        const t = it['@type'];
        if (t === 'FAQPage' || (Array.isArray(t) && t.includes('FAQPage'))) (it.mainEntity || []).forEach(q => ld.push({ q: q.name || '', a: (q.acceptedAnswer || {}).text || '' }));
      });
    } catch (e) { ld.push({ q: 'JSON-LD parse error', a: String(e) }); }
  });
  const meta = document.querySelector('meta[name="description"]');
  return { units, ld, title: document.title, meta: meta ? meta.getAttribute('content') : '', hasCalc: typeof calculateBMI === 'function', hasLMS: !!window.CDC_BMI_LMS };
}
