#!/usr/bin/env python3
"""CMB-041 DESIGN-3: batch 6 of D-26 — the Impeccable detector's findings on the pages left after CMB-040, inside the
current look (CLAUDE.md R2). /age-bmi-calculator/ waits for its D-14 rebuild (§5: its WHO-range box and Winter lines
change there too).

- nested-cards: a box inside a .content-section card drops its 1 px border (a tinted panel, or a hairline-divided item
  where DESIGN.md asks for flat items); hover lifts on static cards go (the Lift-On-Intent rule);
- side-tab / border-accent-on-rounded: no coloured stripes; the KPI tiles and region cards of the two obesity data
  pages show their map colour as a small swatch before the label (their light colours can't carry text);
- low-contrast: the about page's links and button in --link, the hub's stat numbers in the strong inks, rank numbers
  gray-600 on the state page;
- line-length: prose on these pages stops at 36em (.measure-36), and the calculators' results text moves from 65ch to
  36em (ch follows the font's zero, which is wider in some system fonts).
usage: python3 research/cmb-041/apply.py [--check]   (repo root)"""
import re, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
CHECK = '--check' in sys.argv

CSS = [('.er-summary p, .er-note, .er-summary-note, .rank-text { max-width: 65ch; }',
        '.er-summary p, .er-note, .er-summary-note, .rank-text { max-width: 36em; }', 1)]
CSS_TAIL = """
/* CMB-041: prose measure for pages outside the D-14 reading column (contact, the calculators hub, lean body mass, the
   two obesity data pages): 36em, under 80 characters a line at desktop width, as .container--guide. */
.measure-36 p, .measure-36 li, .measure-36 figcaption { max-width: 36em; }
.measure-36 .cmb-answer, .measure-36 .cmb-callout { max-width: calc(36em + 34px); }
"""
SWATCH = ('.obs-kpi-l::before,.ck-kpi-l::before,.obs-reg>span::before{content:"";display:inline-block;width:.7em;height:.7em;'
          'border-radius:2px;background:var(--c);margin-right:.4em;vertical-align:-.04em}')

E = {
 'about/index.html': [
  ('.about-value { text-align: center; padding: 1.25rem 1rem; background: var(--gray-50); border-radius: var(--radius-lg); border: 1px solid var(--gray-200); }',
   '.about-value { text-align: center; padding: 1.25rem 1rem; background: var(--gray-50); border-radius: var(--radius-lg); }', 1),
  ('.suite-card { padding: 1.25rem; background: var(--gray-50); border-radius: var(--radius-lg); border: 1px solid var(--gray-200); transition: box-shadow 0.2s ease, transform 0.2s ease; }',
   '.suite-card { padding: 1.25rem; background: var(--gray-50); border-radius: var(--radius-lg); }', 1),
  ('.suite-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }', '', 1),
  ('.suite-card h3 a { color: var(--primary); text-decoration: none; }', '.suite-card h3 a { color: var(--link); text-decoration: none; }', 1),
  ('.medical-disclaimer-box { background: #fef3c7; border: 1px solid #f59e0b; border-radius: var(--radius-lg); padding: 1.25rem; margin: 1.5rem 0; }',
   '.medical-disclaimer-box { background: #fef3c7; border-radius: var(--radius-lg); padding: 1.25rem; margin: 1.5rem 0; }', 1),
  ('.contact-box { background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: var(--radius-lg); padding: 1.5rem; text-align: center; margin-top: 1.5rem; }',
   '.contact-box { background: var(--gray-50); border-radius: var(--radius-lg); padding: 1.5rem; text-align: center; margin-top: 1.5rem; }', 1),
  ('.contact-box a.contact-btn { display: inline-block; background: var(--primary); color: white;',
   '.contact-box a.contact-btn { display: inline-block; background: var(--link); color: white;', 1)],
 'contact/index.html': [
  ('<div class="container content-narrow">', '<div class="container content-narrow measure-36">', 1),
  ('<div style="background:linear-gradient(135deg,#f0f7ff 0%,#e8f4f8 100%);border:1px solid #d0e3f0;border-radius:16px;padding:2rem;margin:1.5rem 0;text-align:center;">',
   '<div style="background:linear-gradient(135deg,#f0f7ff 0%,#e8f4f8 100%);border-radius:16px;padding:2rem;margin:1.5rem 0;text-align:center;">', 1),
  ('<div style="background:#fffbeb;border-left:4px solid #f59e0b;border-radius:0 8px 8px 0;padding:1.25rem;margin:1rem 0;">',
   '<div style="background:#fffbeb;border-radius:8px;padding:1.25rem;margin:1rem 0;">', 1)],
 'privacy/index.html': [
  ('<div style="background:var(--primary-bg);border:1px solid var(--primary-light);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;">',
   '<div style="background:var(--primary-bg);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;">', 1)],
 'terms/index.html': [
  ('<div style="background:#fef2f2;border-left:4px solid #ef4444;border-radius:0 var(--radius-md) var(--radius-md) 0;padding:1.25rem 1.5rem;margin:1.25rem 0;">',
   '<div style="background:#fef2f2;border-radius:var(--radius-md);padding:1.25rem 1.5rem;margin:1.25rem 0;">', 1),
  ('<div style="background:var(--gray-50);border:1px solid var(--gray-200);border-radius:var(--radius-md);padding:1.25rem 1.5rem;margin:1rem 0;">',
   '<div style="background:var(--gray-50);border-radius:var(--radius-md);padding:1.25rem 1.5rem;margin:1rem 0;">', 1)],
 'calculators/index.html': [
  ('<main><div class="container">', '<main><div class="container measure-36">', 1),
  ('.calc-card { background:white;border:1px solid var(--gray-200);border-radius:var(--radius-lg);padding:1.5rem;box-shadow:0 1px 3px rgba(0,0,0,0.06);transition:box-shadow 0.2s; }',
   '.calc-card { background:white;border-top:1px solid var(--gray-200);padding:1.25rem 0 0.5rem; }', 1),
  ('.calc-card:hover { box-shadow:0 4px 12px rgba(0,0,0,0.1); }', '', 1),
  ('.info-card-grid > div { background:white;border:1px solid var(--gray-200);border-radius:var(--radius-lg);padding:1.25rem;text-align:center; }',
   '.info-card-grid > div { background:var(--gray-50);border-radius:var(--radius-lg);padding:1.25rem;text-align:center; }', 1),
  ('.info-card-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:1.5rem 0; }',
   '.info-card-grid { display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin:1.5rem 0; }', 1),   # two by two in the 680 px section: '18.5-24.9' no longer breaks
  ('<div style="background:white;border:1px solid var(--gray-200);border-radius:var(--radius-lg);padding:1.5rem;margin:1rem 0;">',
   '<div style="margin:1rem 0;">', 1),
  ('<div class="stat-highlight" style="color:var(--primary);">9</div>', '<div class="stat-highlight" style="color:var(--link);">9</div>', 1),
  ('<div class="stat-highlight" style="color:#22c55e;">18.5-24.9</div>', '<div class="stat-highlight" style="color:var(--normal-strong);">18.5-24.9</div>', 1),
  ('<div class="stat-highlight" style="color:#f59e0b;">4</div>', '<div class="stat-highlight" style="color:var(--overweight-strong);">4</div>', 1)],
 'lean-body-mass/index.html': [
  ('<main><div class="container">', '<main><div class="container measure-36">', 1),
  ('<div style="background:#f0f4f8;border-left:4px solid #4a90d9;padding:1.25rem 1.5rem;border-radius:0 8px 8px 0;margin:1rem 0;">',
   '<div style="background:#f0f4f8;padding:1.25rem 1.5rem;border-radius:8px;margin:1rem 0;">', 1),
  ('<div style="background:var(--gray-50);border:1px solid var(--gray-200);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;margin:1.5rem 0;">',
   '<div style="background:var(--gray-50);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;margin:1.5rem 0;">', 1)],
 'obesity-rate-by-state/index.html': [
  ('<main><div class="container" style="max-width:1000px;', '<main><div class="container measure-36" style="max-width:1000px;', 1),
  ('.obs-kpi{background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}',
   '.obs-kpi{background:#fff;border:1px solid #E5E7EB;border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:2px}' + SWATCH, 1),
  ('.obs-reg{border-radius:10px;padding:10px 12px;background:#fff;border:1px solid #EEF0F3;border-left:6px solid var(--c)}',
   '.obs-reg{border-radius:10px;padding:10px 12px;background:#fff;border:1px solid #E5E7EB}', 1),
  ('.cmb-answer{border-left:4px solid #E0612D;background:#FFF7F2;', '.cmb-answer{border:1px solid #F3D3AE;background:#FFF7F2;', 1),
  ('.obs-bl-n{flex:0 0 22px;font-weight:800;color:#9CA3AF;text-align:right}', '.obs-bl-n{flex:0 0 22px;font-weight:800;color:#4B5563;text-align:right}', 1)],
 'childhood-obesity-statistics/index.html': [
  ('<main><div class="container" style="max-width:1000px;', '<main><div class="container measure-36" style="max-width:1000px;', 1),
  ('.ck-cards .ck-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}',
   '.ck-cards .ck-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border:1px solid #E5E7EB;border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:2px}' + SWATCH, 1),
  ('.cmb-answer{border-left:4px solid #E0612D;background:#FFF7F2;', '.cmb-answer{border:1px solid #F3D3AE;background:#FFF7F2;', 1)],
}
# the hub's cards lose their coloured left stripes (inline, one per card)
STRIPES = ('calculators/index.html', r'<div class="calc-card" style="border-left:5px solid [^"]*;">', '<div class="calc-card">', 10)


def main():
    bad = 0
    css_path = REPO / 'assets/css/styles.css'
    css = css_path.read_text(encoding='utf-8')
    css_done = '.measure-36' in css
    if not css_done:
        for old, new, n in CSS:
            if css.count(old) != n:
                bad += 1; print('CSS MISMATCH', css.count(old), n, old[:70]); continue
            css = css.replace(old, new)
        css = css.rstrip('\n') + '\n' + CSS_TAIL
    out = {}
    for rel, edits in E.items():
        t = (REPO / rel).read_text(encoding='utf-8')
        if 'measure-36' in t or (rel == 'about/index.html' and '.suite-card h3 a { color: var(--link)' in t) or \
           (rel in ('privacy/index.html', 'terms/index.html') and 'border-left:4px solid #ef4444' not in t and 'border:1px solid var(--primary-light);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;">' not in t):
            continue
        for old, new, n in edits:
            if t.count(old) != n:
                bad += 1; print('MISMATCH', rel, t.count(old), n, '|', old[:90]); continue
            t = t.replace(old, new)
        if rel == STRIPES[0]:
            t, k = re.subn(STRIPES[1], STRIPES[2], t)
            if k != STRIPES[3]:
                bad += 1; print('STRIPES', k)
        out[rel] = t
    if CHECK or bad:
        print(f'{bad} mismatches' if bad else f'check ok: {len(out)} pages to edit, css {"done" if css_done else "to edit"}')
        return 1 if bad else 0
    if not css_done:
        css_path.write_text(css, encoding='utf-8'); print('edited assets/css/styles.css')
    for rel, t in out.items():
        (REPO / rel).write_text(t, encoding='utf-8'); print('edited', rel)
    return 0


if __name__ == '__main__':
    sys.exit(main())
