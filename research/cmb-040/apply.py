#!/usr/bin/env python3
"""CMB-040 DESIGN-2: batch 5 of D-26 — clear the Impeccable detector's findings on the fifteen old guides inside the
current look (CLAUDE.md R2): no new fonts, colours, logo or ad-container changes, no motion.

- line-length: the guides' column is one class, .container--guide (680 px), with prose at 65ch, so lines stay under 80
  characters at desktop width (what-is-bmi, bmi-for-athletes and bmi-by-age move from 1000 / 900 px to the same column);
- heading-rhythm: an h3 directly in a guide's article gets more space above than below;
- skipped-heading: card and step titles that follow an h2 become h3 (styles.css styles h3 and h4 alike in those parts);
- side-tab / border-accent-on-rounded: callouts and the athletes' tiles get a hairline border instead of a 4-5 px
  coloured stripe (the tiles keep their colour in the number);
- low-contrast / gray-on-color: category text uses the --*-strong inks (CMB-011), links in citation boxes use --link,
  step numbers gray-700, tile labels take the tile's own hue, the what-is-bmi chip takes dark text on its light colours;
- tiny-text: SVG body labels are 12 or larger in viewBox units (DESIGN.md), re-laid where a label no longer fits.
Visible text changes only where a figure's description had to follow its new layout (/blog/bmi-limitations/).
usage: python3 research/cmb-040/apply.py [--check]   (repo root)"""
import re, sys, pathlib, json

REPO = pathlib.Path(__file__).resolve().parents[2]
CHECK = '--check' in sys.argv
TODAY = '2026-11-13'

CSS = [
    ('.tip-content h4 { font-size: 0.875rem;', '.tip-content h3, .tip-content h4 { font-size: 0.875rem;', 1),
    ('.info-card h4 { font-size: 1rem;', '.info-card h3, .info-card h4 { font-size: 1rem;', 1),
    ('.citation-box a { color: var(--primary-dark);', '.citation-box a { color: var(--link);', 1),
    ('.related-article-card h4 { font-size', '.related-article-card h3, .related-article-card h4 { font-size', 1),
    ('.related-article-card h4 a { color', '.related-article-card h3 a, .related-article-card h4 a { color', 1),
    ('.related-article-card h4 a:hover {', '.related-article-card h3 a:hover, .related-article-card h4 a:hover {', 1),
    ('.comparison-table .check { color: var(--success);', '.comparison-table .check { color: var(--normal-strong);', 1),
    ('.comparison-table .cross { color: var(--error);', '.comparison-table .cross { color: var(--obese-strong);', 1),
    ('font-weight: 600; color: var(--gray-500); margin-bottom: 0.5rem; }', 'font-weight: 600; color: var(--gray-700); margin-bottom: 0.5rem; }', 1),
    ('.pros-list h4, .cons-list h4 {', '.pros-list h3, .cons-list h3, .pros-list h4, .cons-list h4 {', 1),
    ('.pros-list h4 { color: #166534; }', '.pros-list h3, .pros-list h4 { color: #166534; }', 1),
    ('.cons-list h4 { color: #991b1b; }', '.cons-list h3, .cons-list h4 { color: #991b1b; }', 1),
    ('.numbered-step-content h4 {', '.numbered-step-content h3, .numbered-step-content h4 {', 1),
]
CSS_TAIL = """
/* CMB-040: the old guides' column (.container--guide, 680 px as main.reading). Prose stops at 36em, under 80 characters a
   line at desktop width (detector line-length; D-14 sections give 37em at 17 px), set in em because ch follows the
   font's zero, which is wider in some system fonts; an h3 straight in the article gets more space above
   than below (detector heading-rhythm); card and step titles under an h2 are h3, styled as the h4 they were. */
.container--guide { max-width: 680px; }
.container--guide p, .container--guide li, .container--guide figcaption, .container--guide .numbered-step-content { max-width: 36em; }
.container--guide article > h3 { margin: 2rem 0 0.75rem; }
.container--guide article > h3 + * { margin-top: 0; }
"""

G680 = ['bmi-formula', 'bmi-history', 'bmi-categories', 'bmi-chart-explained', 'bmi-and-health-risks', 'underweight-bmi-risks',
        'bmi-limitations', 'bmi-and-metabolism', 'body-fat-vs-bmi', 'waist-to-height-ratio', 'how-to-lower-bmi',
        'bmi-tracking-guide']
E = {f'blog/{g}/index.html': [('<div class="container" style="max-width: 680px;">', '<div class="container container--guide">', 1)]
     for g in G680}
for g, w in (('what-is-bmi', '1000'), ('bmi-for-athletes', '1000'), ('bmi-by-age', '900')):
    E[f'blog/{g}/index.html'] = [(f'<div class="container" style="max-width:{w}px;margin:0 auto;padding:2rem 1rem 3rem;">',
                                  '<div class="container container--guide" style="margin:0 auto;padding:2rem 1rem 3rem;">', 1)]

# card and step titles that follow an h2: h4 -> h3 (page, h2 text, number converted before the next h2 or h3)
RUNS = [('bmi-formula', 'BMI Formula Variations and Alternatives', 1), ('bmi-formula', 'Practical Tips for Accurate BMI Calculation', 4),
        ('bmi-history', 'Related Guides', 5), ('bmi-categories', 'Tips for Understanding Your BMI Category', 6),
        ('bmi-chart-explained', 'How to Read a BMI Chart', 4), ('bmi-chart-explained', 'How to Find Your BMI on a Chart Without Calculating', 6),
        ('bmi-chart-explained', 'Limitations of BMI Charts', 2), ('bmi-chart-explained', 'Related Guides', 6),
        ('bmi-and-health-risks', 'Related Articles', 5), ('underweight-bmi-risks', 'When to See a Doctor', 4),
        ('bmi-limitations', 'When BMI Is Still Useful', 4), ('bmi-and-metabolism', 'What Is Metabolism?', 2),
        ('body-fat-vs-bmi', 'Which Metric Is Better for Health Assessment?', 3), ('waist-to-height-ratio', 'What Is Waist-to-Height Ratio?', 4),
        ('waist-to-height-ratio', 'Why WHtR Is Better Than BMI', 2), ('bmi-tracking-guide', 'The Best Time to Weigh Yourself', 4)]

def add(g, old, new, n=1):
    E.setdefault(f'blog/{g}/index.html', []).append((old, new, n))

add('body-fat-vs-bmi', '<h3>Standard BMI Categories</h3>', '<h2>Standard BMI Categories</h2>')
# side tabs -> hairline borders
add('bmi-categories', '<div style="background:#fffbeb;border-left:4px solid #f59e0b;border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin:1rem 0 1.5rem;">',
    '<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:1rem 1.25rem;margin:1rem 0 1.5rem;">')
add('bmi-and-health-risks', '<div style="background:#fffbeb;border-left:4px solid #f59e0b;border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin:1.25rem 0;">',
    '<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:1rem 1.25rem;margin:1.25rem 0;">')
add('underweight-bmi-risks', '<div style="background:#fef2f2;border-left:4px solid #dc2626;border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin:1rem 0 1.5rem;">',
    '<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:1rem 1.25rem;margin:1rem 0 1.5rem;">')
for g in ('what-is-bmi', 'bmi-for-athletes'):
    add(g, '.cmb-answer{border-left:4px solid #E0612D;background:#FFF7F2;', '.cmb-answer{border:1px solid #F3D3AE;background:#FFF7F2;')
add('bmi-for-athletes', 'border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06)}',
    'border:1px solid #E5E7EB;border-radius:12px;padding:12px 14px}')
add('bmi-for-athletes', '.at-kpi b{display:block;font-size:1.9rem;line-height:1.1;color:#111827}', '.at-kpi b{display:block;font-size:1.9rem;line-height:1.1;color:var(--c)}')
add('bmi-for-athletes', '\n@media (min-width:760px){.at-kpi{flex:1 1 calc(25% - 10px)}}</style>', '</style>')   # two by two in the 680 px column
# tile labels take their tile's hue (gray-on-color)
for lab, ink in (('Obesity, age-adjusted (BMI &ge; 30)', '#7f1d1d'), ('Overweight (BMI 25&ndash;29.9)', '#78350f'), ('Severe obesity (age-adjusted)', '#7f1d1d')):
    add('bmi-categories', f'<div style="font-size:0.8125rem;color:var(--gray-600);">{lab}</div>', f'<div style="font-size:0.8125rem;color:{ink};">{lab}</div>')
# low contrast
add('bmi-formula', '<p style="font-size: 1.25rem; font-weight: 700; color: var(--primary-dark); margin: 0;">kg / m<sup>2</sup></p>',
    '<p style="font-size: 1.25rem; font-weight: 700; color: var(--link); margin: 0;">kg / m<sup>2</sup></p>')
add('how-to-lower-bmi', '<h4 style="color: var(--primary-dark);">Strength Training</h4>', '<h4 style="color: var(--link);">Strength Training</h4>')
INK = {'normal': 'normal-strong', 'success': 'normal-strong', 'warning': 'overweight-strong', 'overweight': 'overweight-strong',
       'error': 'obese-strong', 'obese': 'obese-strong'}
INKED = {'body-fat-vs-bmi': {'normal': 5, 'obese': 5, 'warning': 2, 'overweight': 2, 'error': 1},
         'bmi-and-metabolism': {'warning': 1, 'obese': 1, 'error': 1},
         'waist-to-height-ratio': {'warning': 2, 'success': 1, 'error': 1}}
for g, tok in INKED.items():
    for k, n in tok.items():
        add(g, f'color: var(--{k});', f'color: var(--{INK[k]});', n)
# the what-is-bmi chip: dark text on its two light colours
add('what-is-bmi', '.wb-chip{border-radius:999px;padding:8px 14px;font-weight:800;color:#fff;background:var(--c)}',
    '.wb-chip{border-radius:999px;padding:8px 14px;font-weight:800;color:var(--t,#fff);background:var(--c)}')
add('what-is-bmi', 'id="wb-cat" style="--c:#E5743F">', 'id="wb-cat" style="--c:#E5743F;--t:#111827">')
add('what-is-bmi', "function cat(b){return b<18.5?['Underweight','#60A5FA']:b<25?['Healthy weight','#2E7D4F']:b<30?['Overweight','#E5743F']:['Obesity','#B3431A'];}",
    "function cat(b){return b<18.5?['Underweight','#60A5FA','#111827']:b<25?['Healthy weight','#2E7D4F','#fff']:b<30?['Overweight','#E5743F','#111827']:['Obesity','#B3431A','#fff'];}")
add('what-is-bmi', "ch.style.setProperty('--c',c[1]);", "ch.style.setProperty('--c',c[1]);ch.style.setProperty('--t',c[2]);")

# SVG body text at 12 or more (viewBox units)
add('bmi-formula', '<text x="80" y="49" text-anchor="middle" font-size="10" fill-opacity="0.6">metric BMI</text>',
    '<text x="80" y="50" text-anchor="middle" font-size="12" fill-opacity="0.6">metric BMI</text>')
add('bmi-formula', '<text x="160" y="54" font-size="11" fill-opacity="0.75">kg = lbs / 2.20462, m = in / 39.3701</text>',
    '<text x="160" y="54" font-size="12" fill-opacity="0.75">kg = lbs / 2.20462, m = in / 39.3701</text>')
add('bmi-formula', '<text x="130" y="176" text-anchor="middle" font-size="10" fill="#1e3a8a" fill-opacity="0.8">(rounded to 703 in practice)</text>',
    '<text x="130" y="176" text-anchor="middle" font-size="12" fill="#1e3a8a" fill-opacity="0.8">(rounded to 703 in practice)</text>')
add('bmi-formula', '<text x="370" y="178" text-anchor="middle" font-size="10" fill="#14532d" fill-opacity="0.8">imperial BMI</text>',
    '<text x="370" y="176" text-anchor="middle" font-size="12" fill="#14532d" fill-opacity="0.8">imperial BMI</text>')
add('bmi-formula', '<text x="258" y="256" text-anchor="middle" font-weight="500">Height (m), fixed weight 70 kg</text>',
    '<text x="258" y="256" text-anchor="middle" font-weight="500" font-size="12">Height (m), fixed weight 70 kg</text>')
add('bmi-formula', '<g font-size="11" font-weight="600"> <text x="464" y="204" text-anchor="end" fill="currentColor">standard (h²)</text> <text x="464" y="220" text-anchor="end" fill="#7c3aed">Trefethen (h^2.5)</text> </g>',
    '<g font-size="12" font-weight="600"> <line x1="330" y1="48" x2="352" y2="48" stroke="currentColor" stroke-opacity="0.75" stroke-width="2" stroke-dasharray="5 3"/> <text x="358" y="52" fill="currentColor">standard (h²)</text> <line x1="330" y1="66" x2="352" y2="66" stroke="#7c3aed" stroke-width="2.5"/> <text x="358" y="70" fill="#7c3aed">Trefethen (h^2.5)</text> </g>')
for a_, b_ in (('<text x="130" y="163" text-anchor="middle" font-weight="700" fill="#1e3a8a">39.3701² ÷ 2.20462 = 703.07</text>',
                '<text x="130" y="160" text-anchor="middle" font-weight="700" fill="#1e3a8a">39.3701² ÷ 2.20462 = 703.07</text>'),
               ('<text x="370" y="167" text-anchor="middle" font-weight="700" fill="#14532d">(lbs ÷ in²) × 703</text>',
                '<text x="370" y="160" text-anchor="middle" font-weight="700" fill="#14532d">(lbs ÷ in²) × 703</text>')):
    add('bmi-formula', a_, b_)
add('bmi-formula', '<text x="175" y="103" font-size="10" fill="#ef4444" font-weight="600">curves cross ≈ 1.69 m</text>',
    '<text x="175" y="103" font-size="12" fill="#b91c1c" font-weight="600">curves cross ≈ 1.69 m</text>')
for a, b in (('<text x="120" y="34" text-anchor="middle" font-size="10" fill-opacity="0.7">muscular, low body fat</text>',
              '<text x="120" y="37" text-anchor="middle" font-size="12" fill-opacity="0.7">muscular, low body fat</text>'),
             ('<text x="360" y="34" text-anchor="middle" font-size="10" fill-opacity="0.7">"normal weight obesity"</text>',
              '<text x="360" y="37" text-anchor="middle" font-size="12" fill-opacity="0.7">"normal weight obesity"</text>'),
             ('<text x="120" y="234" text-anchor="middle" font-size="10">lean-dominant</text>', '<text x="120" y="234" text-anchor="middle" font-size="12">lean-dominant</text>'),
             ('<text x="360" y="234" text-anchor="middle" font-size="10">fat-dominant</text>', '<text x="360" y="234" text-anchor="middle" font-size="12">fat-dominant</text>')):
    add('body-fat-vs-bmi', a, b)
add('bmi-chart-explained', '<text x="270" y="285" font-size="10" fill="currentColor" fill-opacity="0.85">example:',
    '<text x="470" y="285" text-anchor="end" font-size="12" fill="currentColor" fill-opacity="0.85">example:')
for a, b in (('<text x="245" y="94" font-size="10" fill="currentColor" fill-opacity="0.75">lower rib</text>',
              '<text x="245" y="94" font-size="12" fill="currentColor" fill-opacity="0.75">lower rib</text>'),
             ('<text x="245" y="141" font-size="11" font-weight="700" fill="currentColor">measure here</text>',
              '<text x="245" y="141" font-size="12" font-weight="700" fill="currentColor">measure here</text>'),
             ('<text x="245" y="154" font-size="10" fill-opacity="0.75">(mid-way between lower</text>',
              '<text x="336" y="141" font-size="12" fill-opacity="0.75">(mid-way between lower</text>'),
             ('<text x="245" y="166" font-size="10" fill-opacity="0.75">rib and iliac crest)</text>',
              '<text x="336" y="155" font-size="12" fill-opacity="0.75">rib and iliac crest)</text>'),
             ('<text x="245" y="179" font-size="10" fill="currentColor" fill-opacity="0.75">iliac crest</text>',
              '<text x="245" y="179" font-size="12" fill="currentColor" fill-opacity="0.75">iliac crest</text>')):
    add('waist-to-height-ratio', a, b)
add('bmi-tracking-guide', '<g font-size="10" font-weight="600"> <circle cx="360" cy="45" r="3" fill="currentColor" fill-opacity="0.3"/> <text x="368" y="49">daily weigh-in (noisy)</text> <line x1="355" y1="63" x2="368" y2="63" stroke="#0891b2" stroke-width="2.5"/> <text x="373" y="66" fill="#0891b2">weekly rolling mean</text> </g>',
    '<g font-size="12" font-weight="600"> <circle cx="300" cy="45" r="3" fill="currentColor" fill-opacity="0.3"/> <text x="308" y="49">daily weigh-in (noisy)</text> <line x1="295" y1="64" x2="308" y2="64" stroke="#0891b2" stroke-width="2.5"/> <text x="313" y="68" fill="#0e7490">weekly rolling mean</text> </g>')
for lab, y in (('Severe thinness &lt; 16.0', 39), ('Moderate 16.0–16.9', 65), ('Mild 17.0–18.4', 89), ('Overweight 25.0–29.9', 185),
               ('Obese I 30.0–34.9', 228), ('Obese II 35.0–39.9', 266)):
    add('bmi-categories', f'<text x="150" y="{y}" font-size="10">{lab}</text>', f'<text x="150" y="{y}" font-size="12">{lab}</text>')
add('bmi-categories', '<text x="150" y="126" font-weight="700">Normal 18.5–24.9</text>', '<text x="150" y="126" font-size="12" font-weight="700">Normal 18.5–24.9</text>')
add('bmi-categories', '<text x="150" y="302" font-size="10" font-weight="600">Obese III ≥ 40.0</text>', '<text x="150" y="302" font-size="12" font-weight="600">Obese III ≥ 40.0</text>')

SVG_SPANS = {}   # page -> list of (unique marker inside the svg, fn(svg) -> svg)

def risks(svg):
    svg = svg.replace('<g font-family="inherit" font-size="11" fill="currentColor">', '<g font-family="inherit" font-size="12" fill="currentColor">', 1)
    for a, b in (('140', '195'), ('220', '265'), ('300', '335'), ('395', '420')):
        n1 = svg.count(f'cx="{a}"'); n2 = svg.count(f'<text x="{a}" y="22"')
        assert n1 == 7 and n2 == 1, (a, n1, n2)
        svg = svg.replace(f'cx="{a}"', f'cx="{b}"').replace(f'<text x="{a}" y="22"', f'<text x="{b}" y="22"')
    return svg
SVG_SPANS['bmi-and-health-risks'] = [('Obesity-associated cancers</text>', risks)]

def under(svg):
    svg = svg.replace('<g font-family="inherit" font-size="11" fill="currentColor">', '<g font-family="inherit" font-size="12" fill="currentColor">', 1)
    for y in ('27', '67', '117', '167', '207'):
        assert svg.count(f'<line x1="120" y1="{y}"') == 1, y
        svg = svg.replace(f'<line x1="120" y1="{y}"', f'<line x1="124" y1="{y}"')
    for y1, y2, y2n in (('113', '27', '27'), ('117', '67', '67'), ('120', '117', '117'), ('127', '167', '167'), ('132', '207', '201')):
        old = f'<line x1="300" y1="{y1}" x2="380" y2="{y2}"'
        assert svg.count(old) == 1, old
        svg = svg.replace(old, f'<line x1="300" y1="{y1}" x2="350" y2="{y2n}"')
    old = '<text x="470" y="210" text-anchor="end">Higher all-cause mortality</text>'
    assert svg.count(old) == 1
    return svg.replace(old, '<text x="470" y="204" text-anchor="end">Higher all-cause</text><text x="470" y="219" text-anchor="end">mortality</text>')
SVG_SPANS['underweight-bmi-risks'] = [('Higher all-cause mortality</text>', under)]

def tiles(svg):
    head = svg[:svg.index('<g font-family="inherit" font-size="11" fill="currentColor">')]
    head = head.replace('viewBox="0 0 480 240"', 'viewBox="0 0 480 338"', 1).replace('A 2 by 2 grid of tiles, each', 'Four tiles, each', 1)
    T = [('#f0fdf4', '#22c55e', '#14532d', 'Muscular athlete', 'NFL prospects: 53.4% obese by BMI but 8.9% obese by body fat (2018)',
          'Standard categorisation labels as "overweight/obese" — misleading.'),
         ('#fef3c7', '#f59e0b', '#78350f', 'Older adult, sarcopenia', 'BMI in "normal" range, but body composition has shifted:',
          'less muscle, more fat mass at the same weight.'),
         ('#eff6ff', '#3b82f6', '#1e3a8a', 'Height extremes', 'Very short: standard reads too high. Very tall: standard reads too low.',
          'Trefethen 2013 addresses this with a height^2.5 exponent.'),
         ('#fee2e2', '#ef4444', '#7f1d1d', 'Ethnic variation', 'Same BMI, different risk profile. WHO Western Pacific Region uses',
          'overweight cutoff 23 (not 25) for Asian populations.')]
    body = ' <g font-family="inherit" font-size="12" fill="currentColor">'
    for i, (bg, st, ink, h, l1, l2) in enumerate(T):
        y = 10 + i * 82
        body += (f' <rect x="10" y="{y}" width="460" height="72" rx="6" fill="{bg}" stroke="{st}" stroke-width="1.5"/>'
                 f' <text x="22" y="{y + 22}" font-size="13" font-weight="700" fill="{ink}">{h}</text>'
                 f' <text x="22" y="{y + 43}">{l1}</text> <text x="22" y="{y + 61}" fill-opacity="0.7">{l2}</text>')
    return head + body + ' </g> </svg>'
SVG_SPANS['bmi-limitations'] = [('Muscular athlete</text>', tiles)]
DATES = ['blog/bmi-limitations/index.html']   # the figure's description changed (visible text inside <main>)


def html_unescaped_runs(t, g):
    for gg, h2, n in RUNS:
        if gg != g:
            continue
        m = re.search(r'<h2[^>]*>\s*' + re.escape(h2) + r'\s*</h2>', t)
        assert m, (g, h2)
        end = len(t)
        for pat in (r'<h2[\s>]', r'<h3[\s>]'):
            mm = re.compile(pat).search(t, m.end())
            if mm: end = min(end, mm.start())
        seg = t[m.end():end]
        got = seg.count('<h4')
        assert got == n and seg.count('</h4>') == n, (g, h2, got, n)
        t = t[:m.end()] + seg.replace('<h4', '<h3').replace('</h4>', '</h3>') + t[end:]
    return t


def main():
    bad = 0
    css = (REPO / 'assets/css/styles.css').read_text(encoding='utf-8')
    done_css = '.container--guide' in css
    if not done_css:
        for old, new, n in CSS:
            if css.count(old) != n:
                bad += 1; print('CSS MISMATCH', css.count(old), n, old[:80]); continue
            css = css.replace(old, new)
        css = css.rstrip('\n') + '\n' + CSS_TAIL
    out = {}
    for rel in sorted(set(E) | {f'blog/{g}/index.html' for g in SVG_SPANS} | {f'blog/{g}/index.html' for g, _, _ in RUNS}):
        t = (REPO / rel).read_text(encoding='utf-8')
        if 'container--guide' in t:
            continue
        g = rel.split('/')[1]
        for old, new, n in E.get(rel, []):
            if t.count(old) != n:
                bad += 1; print('MISMATCH', rel, t.count(old), n, '|', old[:90]); continue
            t = t.replace(old, new)
        for marker, fn in SVG_SPANS.get(g, []):
            svgs = [m for m in re.finditer(r'<svg\b.*?</svg>', t, re.S) if marker in m.group(0)]
            if len(svgs) != 1:
                bad += 1; print('SVG MISMATCH', rel, marker, len(svgs)); continue
            m = svgs[0]
            t = t[:m.start()] + fn(m.group(0)) + t[m.end():]
        try:
            t = html_unescaped_runs(t, g)
        except AssertionError as e:
            bad += 1; print('RUN MISMATCH', e); continue
        if rel in DATES:
            t, k = re.subn(r'("dateModified": ?")\d{4}-\d{2}-\d{2}(")', rf'\g<1>{TODAY}\g<2>', t)
            assert k >= 1, rel
            t = re.sub(r'(article:modified_time" content=")\d{4}-\d{2}-\d{2}', rf'\g<1>{TODAY}', t)
        out[rel] = t
    if CHECK or bad:
        print(f'{bad} mismatches' if bad else f'check ok: {len(out)} pages to edit, css {"done" if done_css else "to edit"}')
        return 1 if bad else 0
    if not done_css:
        (REPO / 'assets/css/styles.css').write_text(css, encoding='utf-8')
        print('edited assets/css/styles.css')
    for rel, t in out.items():
        (REPO / rel).write_text(t, encoding='utf-8')
        print('edited', rel)
    sm = REPO / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    for rel in DATES:
        loc = 'https://calculatemybmi.net/' + rel[:-len('index.html')]
        s, n = re.subn(rf'(<loc>{re.escape(loc)}</loc>\s*<lastmod>)\d{{4}}-\d{{2}}-\d{{2}}', rf'\g<1>{TODAY}', s)
        assert n == 1, loc
    sm.write_text(s, encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
