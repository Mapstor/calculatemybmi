#!/usr/bin/env python3
"""CMB-010 SITEWIDE-REPAIR — build record. usage: patch_cmb010.py REPO_ROOT  (build record: ran once in chat on GitHub main 59716d5)
Ran once in chat on GitHub main 59716d5 (after CMB-009). Every replacement asserts its exact count.

Part 1  broken content left by automated passes in Aug-Sept 2026 (links, lead-ins and boxes stripped)
Part 2  D-11 (no age- or sex-specific healthy BMI ranges) and option B (no targets of our own)
Part 3  shared components: action buttons, bylines, emoji icons, nested cards, chart fills, contrast
Part 4  gates in scripts/check_structure.py so these cannot come back silently
"""
import sys, os, re, math

ROOT = sys.argv[1]
def rd(p): return open(os.path.join(ROOT, p), encoding='utf-8', newline='').read()
def wr(p, s): open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='').write(s)
LOG = []

def _ws_pattern(old):
    """old as a regex where whitespace runs are flexible (the minified pages keep odd double spaces)."""
    parts = re.split(r'(\s+)', old)
    out = ''
    for i, part in enumerate(parts):
        if i % 2 == 0: out += re.escape(part)
        else:
            prev = parts[i - 1][-1:] if parts[i - 1] else ''
            nxt = parts[i + 1][:1] if i + 1 < len(parts) and parts[i + 1] else ''
            out += r'\s*' if (prev in '<>' or nxt in '<>' or not prev or not nxt) else r'\s+'
    if old[:1].isspace(): out = r'\s*' + out.lstrip('\\s+*')
    return out

def rep(f, old, new, count=1, label=''):
    s = rd(f); n = s.count(old)
    if n == count:
        wr(f, s.replace(old, new)); LOG.append((f, label or old[:50], n)); return
    pat = _ws_pattern(old)
    s2, n2 = re.subn(pat, lambda m: new, s)
    assert n2 == count, f'{f}: {label or old[:60]!r} expected {count} found exact {n} / flexible {n2}'
    wr(f, s2); LOG.append((f, (label or old[:50]) + ' [ws]', n2))

def rex(f, pat, repl, count=1, label='', flags=re.S):
    s = rd(f); s2, n = re.subn(pat, repl, s, flags=flags)
    assert n == count, f'{f}: {label or pat[:60]!r} expected {count} found {n}'
    wr(f, s2); LOG.append((f, label or pat[:50], n))

# =====================================================================
# PART 1 — broken content
# =====================================================================

# 1.1 /blog/body-fat-vs-bmi/: the closing call to action lost its link on 2026-09-26 (plain text since)
rep('blog/body-fat-vs-bmi/index.html',
    '<p style="text-align: center; margin: 2rem 0;">Calculate My BMI Now</p>',
    '<p class="cta-row"><a href="/" class="cta-button">Calculate My BMI Now</a></p>', label='dead CTA')

# 1.2 /blog/bmi-chart-explained/: the Example box lost its text on 2026-09-27 (empty box since); our own calculation
rep('blog/bmi-chart-explained/index.html',
    '<div class="alert alert-info"> <div class="alert-title">Example</div>  </div>',
    '<div class="alert alert-info"> <div class="alert-title">Example</div> <p style="margin:0;">You are 5&prime;6&Prime; (167.6 cm) and weigh 160 lb (72.6 kg). '
    'In the chart above, the 5&prime;6&Prime; row meets the 160 lb column at 26, in the overweight color. '
    'The exact BMI is 25.8 (160 &times; 703 &divide; 66&sup2;), inside the overweight range of 25.0 to 29.9.</p> </div>',
    label='empty Example box')

# 1.3 /blog/bmi-tracking-guide/: unfinished "see our guides on" with three cards inside the paragraph (cards overlap the text)
rex('blog/bmi-tracking-guide/index.html',
    r'<p>For comprehensive strategies, see our guides on\s+<a href="/blog/bmi-categories/" class="related-article-card">.*?</a>\s+<a href="/blog/healthy-bmi-range/" class="related-article-card">.*?</a>\s+<a href="/blog/body-fat-vs-bmi/" class="related-article-card">.*?</a>\s+',
    '<p>For more on reading your numbers, see these guides:</p> <ul style="margin: 1rem 0; padding-left: 1.5rem;"> '
    '<li style="margin-bottom: 0.5rem;"><a href="/blog/bmi-categories/">BMI categories explained</a>: what each category means for your health</li> '
    '<li style="margin-bottom: 0.5rem;"><a href="/blog/healthy-bmi-range/">Healthy BMI range</a>: the adult range of 18.5 to 24.9 and the weights it covers</li> '
    '<li style="margin-bottom: 0.5rem;"><a href="/blog/body-fat-vs-bmi/">Body fat vs BMI</a>: how the two measures differ and when each matters</li> </ul> ',
    label='cards inside a paragraph')

# 1.4 empty boxes and empty steps (their text was removed, the frame stayed)
rep('blog/bmi-categories/index.html',
    ' <div style="background:#fffbeb;border-left:4px solid #f59e0b;border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin:1.25rem 0;"> <p style="margin:0 0 0.5rem;font-weight:600;color:#92400e;">When to seek help</p> </div>',
    '', label='empty "When to seek help" box')
rep('blog/underweight-bmi-risks/index.html',
    ' <div class="numbered-step"> <div class="numbered-step-content"> <h4>Unintentional Weight Loss</h4> </div> </div>',
    '', label='empty step')
rep('blog/how-to-lower-bmi/index.html',
    ' <div class="numbered-step"> <div class="numbered-step-content"> <h4>Monitor and Adjust</h4> </div> </div>',
    '', label='empty step')
rep('blog/bmi-and-metabolism/index.html',
    ' <div class="numbered-step"> <div class="numbered-step-content"> <h4>Recovery Prioritization</h4> </div> </div>',
    '', label='empty step')
# four empty table frames and an orphan source line on /blog/bmi-limitations/
rep('blog/bmi-limitations/index.html', ' <div class="table-responsive"></div> <p style="font-size: 0.8125rem; color: var(--gray-500);">Source: World Health Organization</p>', '', label='empty table + orphan source')
rep('blog/bmi-limitations/index.html', ' <div class="table-responsive"></div>', '', count=3, label='empty table frames')

# 1.5 sentences whose opening (a named source) was cut, leaving a fragment
rep('blog/bmi-limitations/index.html', '<p> and other institutions has identified individuals who are:</p>',
    '<p>BMI and metabolic health can disagree in both directions:</p>', label='fragment')
rep('blog/bmi-limitations/index.html',
    'While useful for large population studies, the other leading institutions now acknowledge that BMI has significant limitations when applied to individuals.',
    'While useful for large population studies, BMI has well-known limitations when applied to individuals.', label='fragment')
rep('blog/bmi-limitations/index.html',
    'Despite these origins, BMI became the standard medical screening tool in the 1970s when insurance companies needed a quick, inexpensive way to categorize applicants.',
    'BMI entered medicine later: Ancel Keys named it in 1972, and NIH and WHO guidelines adopted it in the 1980s and 1990s (see our <a href="/blog/bmi-history/">BMI history</a>).',
    label='wrong history claim')
rep('blog/bmi-tracking-guide/index.html',
    ' <p> recommendations, weekly weigh-ins strike the best balance for most adults. This frequency allows you to identify genuine trends while avoiding the psychological pitfalls of daily weighing.</p>',
    '', label='fragment (unsourced advice, source cut in Aug)')
rep('blog/index.html', ' Theweekly-weighing recommendation frames the discussion.', '', label='glued residue')
rep('blog/bmi-categories/index.html',
    'represents the highest-risk BMI category. it is associated with the most significant',
    'represents the highest-risk BMI category, with the most significant', label='fragment')
rep('blog/healthy-bmi-range/index.html', ' obesity significantly increases the risk of over 200 medical conditions.', '', label='fragment (unsourced number)')
rep('blog/healthy-bmi-range/index.html',
    '<p>If you fall into the overweight or obese category, For detailed strategies,',
    '<p>For detailed strategies,', label='fragment')
rep('lean-body-mass/index.html',
    'LBM provides the missing context. body composition is a significantly better predictor of health outcomes than BMI alone. ',
    'LBM provides the missing context. ', label='fragment (unsourced claim)')
rep('calculators/index.html', 'than any single reading. children, BMI should be tracked', 'than any single reading. For children, BMI should be tracked', label='FAQ schema fragment')
rep('calculators/index.html', 'than any single reading. <a href="/kids-bmi-calculator/">children</a>, BMI should be tracked',
    'than any single reading. For <a href="/kids-bmi-calculator/">children</a>, BMI should be tracked', label='FAQ fragment')

# 1.6 words glued together where a link was removed
rep('age-bmi-calculator/index.html', 'For further reading, see theanalysis of BMI usefulness and the ', 'For further reading, see the ', label='glued words')
rep('blog/bmi-formula/index.html',
    'these are the most frequent errors. For validated and error-free calculationsboth recommend using digital calculators:',
    'these are the most frequent errors:', label='glued words')
rep('blog/bmi-and-metabolism/index.html', ' small share of obesity cases &mdash; see theoverview of why people become overweight.', ' small share of obesity cases.', label='glued words')
rep('new-bmi-calculator/index.html', 'a balanced look at the pros and cons, :</p>', 'a balanced look at the pros and cons:</p>', label='orphan punctuation')

# 1.7 /calculators/ "Trusted Resources": WHO link stripped, three tiles empty
rex('calculators/index.html',
    r'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0\.75rem;margin:1\.25rem 0;"> <div style="display:flex;gap:0\.75rem;padding:0\.875rem;background:var\(--gray-50\);border-radius:var\(--radius-md\);border-left:3px solid var\(--primary\);"> <div> <h4[^>]*>World Health Organization \(WHO\)</h4>.*?</div> </div> </section>',
    '<ul class="resource-list"> '
    '<li><a href="https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight" target="_blank" rel="noopener">WHO: Obesity and overweight fact sheet</a><span>The adult BMI cut-offs used worldwide.</span></li> '
    '<li><a href="https://www.cdc.gov/bmi/about/index.html" target="_blank" rel="noopener">CDC: About BMI</a><span>US adult categories and the growth charts behind the children&rsquo;s calculator.</span></li> '
    '<li><a href="https://www.nhlbi.nih.gov/calculate-your-bmi" target="_blank" rel="noopener">NHLBI: Calculate your BMI</a><span>The National Heart, Lung, and Blood Institute&rsquo;s reference calculator.</span></li> '
    '</ul> </section>', label='Trusted Resources rebuilt')

# 1.8 related blocks: duplicate links (old slugs that now redirect to the same page) and cards that link nowhere
rep('lean-body-mass/index.html', ' <article class="blog-card"><div class="blog-card-content"><p class="blog-card-meta">Guide</p><h3><a href="/blog/bmi-for-athletes/">Muscle Mass and BMI</a></h3><p>How muscle mass affects BMI readings and what to do about it.</p></div></article>', '', label='duplicate card')
rep('lean-body-mass/index.html', ' <article class="blog-card"><div class="blog-card-content"><p class="blog-card-meta">Guide</p><h3><a href="/blog/body-fat-vs-bmi/">BMI vs. body Composition</a></h3><p>A deep dive into alternative body composition metrics beyond BMI.</p></div></article>', '', label='duplicate card')
rep('blog/bmi-history/index.html', ' <div class="related-article-card"> <h4><a href="/blog/bmi-limitations/">BMI Accuracy</a></h4> <p>How accurate is BMI as a measure of health?</p> </div>', '', label='duplicate card')
rep('blog/underweight-bmi-risks/index.html', ' <div class="related-article-card"> <h4><a href="/blog/bmi-and-health-risks/">Overweight BMI Risks</a></h4> <p>Health concerns associated with BMI between 25 and 29.9.</p> </div>', '', label='duplicate card')
rep('blog/bmi-limitations/index.html', ' <div class="related-article-card"> <h4>Is BMI Accurate?</h4> <p>A deep dive into the accuracy of BMI across different scenarios and populations.</p> </div>', '', label='card without a link')
rep('blog/bmi-limitations/index.html', ' <div class="related-article-card"> <h4><a href="/blog/body-fat-vs-bmi/">BMI vs. body Composition</a></h4> <p>Understanding the difference between simple weight metrics and full body composition analysis.</p> </div>', '', label='duplicate card')
rep('blog/waist-to-height-ratio/index.html', ' <div class="related-article-card"> <h4><a href="/blog/body-fat-vs-bmi/">BMI vs. body Composition</a></h4> <p>Understanding the difference between simple metrics and comprehensive analysis.</p> </div>', '', label='duplicate card')
rep('blog/how-to-lower-bmi/index.html', ' <div class="related-article-card"> <h4>Healthy Weight Tips</h4> <p>Evidence-based nutrition and lifestyle recommendations for maintaining a healthy weight.</p> </div>', '', label='card without a link')

# 1.9 /women-bmi-calculator/ and /new-bmi-calculator/: the result line under the healthy range was deleted on 2026-09-27,
#     so after Calculate an empty grey box shows. Restore the element calculator.js writes to.
rep('women-bmi-calculator/index.html', '<div class="weight-range-box"> </div>',
    '<div class="weight-range-box"><p id="women-weight-diff" style="margin:0;font-size:0.9375rem;">&mdash;</p></div>', label='empty result box')
rep('new-bmi-calculator/index.html', '<div class="weight-range-box"> </div>',
    '<div class="weight-range-box"><p id="newbmi-weight-diff" style="margin:0;font-size:0.9375rem;">&mdash;</p></div>', label='empty result box')

# 1.10 leftovers in headings and hub copy
rep('women-bmi-calculator/index.html', '<h2>Healthy weight range for women (teaser)</h2>', '<h2>Healthy weight range for women</h2>', label='(teaser) in H2')
rep('calculators/index.html',
    '<p>Everything you need to know about what constitutes a healthy BMI range, how it varies by age, sex, and ethnicity, and what the science says about optimal BMI for longevity.</p>',
    '<p>The adult range of 18.5 to 24.9, the same for women and men at every age, and the weights it covers at each height.</p>',
    label='hub card claimed the range varies by age and sex')

# 1.10b /calculators/: three worked examples disagreed with the calculators they describe (checked by running each tool)
rep('calculators/index.html',
    'has a BMI of <strong>16.8</strong>, placing him at approximately the <strong style="color:#22c55e;">50th percentile &mdash; Healthy Weight</strong> for his age and sex.',
    'has a BMI of <strong>16.9</strong>, about the <strong style="color:var(--gray-900);">55th percentile &mdash; healthy weight</strong> for his age and sex.',
    label='kids example (tool: 16.9, 54.5th percentile)')
rep('calculators/index.html',
    'has an ideal weight range of approximately <strong style="color:#22c55e;">120&ndash;144 lbs</strong> across the four clinical formulas (Devine: 130 lbs, Robinson: 136 lbs, Miller: 126 lbs, Hamwi: 130 lbs).',
    'gets <strong style="color:var(--gray-900);">129&ndash;135 lbs</strong> across the four clinical formulas (Devine 131 lbs, Robinson 131 lbs, Miller 135 lbs, Hamwi 129 lbs).',
    label='ideal-weight example (tool: 129-135 lb)')
rep('calculators/index.html',
    'has an estimated lean body mass of approximately <strong style="color:#f97316;">141 lbs</strong> (Boer formula), meaning about 29 lbs (~17%) of his weight is fat &mdash; within the healthy range for men.',
    'has an estimated lean body mass of <strong style="color:var(--gray-900);">128.5 lbs</strong> (58.3 kg, Boer formula), which leaves about 41 lbs (24.4%) as fat mass.',
    label='LBM example (tool: 128.5 lb; no body-fat "healthy range")')
s_calc = None
# 1.10c /about/: the women and men cards said the calculators are "tailored for male physiology" / "account for" body fat (they use
#       the same adult cut-offs, D-11)
rep('about/index.html',
    '<p>A BMI calculator with female-specific interpretation and context. Accounts for the fact that women naturally carry a higher percentage of body fat than men, and provides guidance across life stages including pregnancy and menopause.</p>',
    '<p>The standard adult BMI with context for women: the NIH waist cut-off, body fat tools, and notes on pregnancy and menopause.</p>',
    label='D-11 about women card')
rep('about/index.html',
    '<p>Tailored for male physiology with considerations for muscle mass and body composition differences. Includes context on how higher muscle density can affect BMI readings and guidance for athletic body types.</p>',
    '<p>The standard adult BMI with context for men: where your result ranks among US men, the NIH waist cut-off, and a note on muscle.</p>',
    label='D-11 about men card')

# 1.11 /blog/bmi-chart-explained/: grid cells were coloured by the wrong category at boundaries
#      (e.g. 5'2", 100 lb = BMI 18.3 shown green). Recolour every cell from the exact BMI, in the /bmi-chart/ tints.
TINT = {'under': '#dbeafe', 'healthy': '#d1fae5', 'over': '#fde68a', 'ob1': '#fed7aa', 'ob2': '#fecaca', 'ob3': '#fca5a5'}
INK = {'under': '#1e3a8a', 'healthy': '#065f46', 'over': '#78350f', 'ob1': '#7c2d12', 'ob2': '#7f1d1d', 'ob3': '#7f1d1d'}   # text tinted from each hue (no grey on colour)
def round1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def cat(b):
    b = round1(b)
    return 'under' if b < 18.5 else 'healthy' if b < 25 else 'over' if b < 30 else 'ob1' if b < 35 else 'ob2' if b < 40 else 'ob3'
def recolor_grid(src):
    out, n = [], 0
    pos = 0
    for tm in re.finditer(r'(?s)<table\b.*?</table>', src):
        tb = tm.group(0)
        heads = re.findall(r'(?s)<th\b[^>]*>(.*?)</th>', tb)
        cols = []
        for h in heads:
            x = re.sub(r'<[^>]+>', ' ', h); m = re.match(r'\s*(\d{2,3})\s*(lbs?|kg)\b', x)
            cols.append((int(m.group(1)), m.group(2)[:2]) if m else None)
        if len([c for c in cols if c]) < 4:
            continue
        def fix_row(rm):
            nonlocal n
            row = rm.group(0)
            cells = list(re.finditer(r'<td style="background: #[0-9a-f]{6};(?: color: white;)?">(\d+)</td>', row))
            first = re.search(r'<td><strong>([^<]+)</strong></td>', row)
            if not first or not cells: return row
            lab = first.group(1).replace('&#39;', "'").replace('&quot;', '"')
            mm = re.match(r"(\d)'(\d{1,2})\"", lab); mc = re.match(r'(\d{3}) cm', lab)
            inches = int(mm.group(1)) * 12 + int(mm.group(2)) if mm else None
            cm = int(mc.group(1)) if mc else None
            wcols = [c for c in cols[1:]]
            new = row
            for cell, col in zip(cells, wcols):
                w, unit = col
                bmi = 703 * w / inches ** 2 if (unit == 'lb' and inches) else (w / (cm / 100) ** 2 if (unit == 'kg' and cm) else None)
                assert bmi is not None, (lab, col)
                assert int(cell.group(1)) == round(bmi), (lab, col, cell.group(1), bmi)
                new = new.replace(cell.group(0), f'<td style="background:{TINT[cat(bmi)]};color:{INK[cat(bmi)]};">{cell.group(1)}</td>', 1)
                n += 1
            return new
        tb2 = re.sub(r'(?s)<tr>.*?</tr>', fix_row, tb)
        out.append((tm.start(), tm.end(), tb2))
    for a, b, tb2 in reversed(out):
        src = src[:a] + tb2 + src[b:]
    return src, n
s = rd('blog/bmi-chart-explained/index.html'); s, ncells = recolor_grid(s)
assert ncells == 104, ncells
# small kg/lb labels in the grid headers (9.6 px, faded) -> readable
s, nk = re.subn(r'<span style="font-size:0\.8em;opacity:0\.7;">', '<span style="font-size:0.75rem;color:var(--gray-600);font-weight:400;">', s)
assert nk == 26, nk
# the legend table: four rows (the other categories were cut) -> all six categories, in the grid colours
s, nl = re.subn(r'(?s)<table class="data-table"><tr><th>BMI Range</th><th>Category</th><th>Chart Color</th></tr>.*?</table>',
    '<table class="data-table"><tr><th>BMI range</th><th>Category</th><th>Chart color</th></tr>'
    '<tr><td>Below 18.5</td><td>Underweight</td><td style="background:#dbeafe;color:#1e3a8a;">Blue</td></tr>'
    '<tr><td><strong>18.5 to 24.9</strong></td><td><strong>Healthy weight</strong></td><td style="background:#d1fae5;color:#065f46;">Green</td></tr>'
    '<tr><td>25.0 to 29.9</td><td>Overweight</td><td style="background:#fde68a;color:#78350f;">Yellow</td></tr>'
    '<tr><td>30.0 to 34.9</td><td>Obesity class 1</td><td style="background:#fed7aa;color:#7c2d12;">Orange</td></tr>'
    '<tr><td>35.0 to 39.9</td><td>Obesity class 2</td><td style="background:#fecaca;color:#7f1d1d;">Light red</td></tr>'
    '<tr><td>40.0 or higher</td><td>Obesity class 3</td><td style="background:#fca5a5;color:#7f1d1d;">Red</td></tr></table>', s)
assert nl == 1, nl
wr('blog/bmi-chart-explained/index.html', s); LOG.append(('blog/bmi-chart-explained/index.html', 'grid recoloured from exact BMI', ncells))
rep('blog/bmi-chart-explained/index.html',
    '</table> <span style="font-size:0.8125rem;color:var(--gray-500);">Thinness grades: World Health Organization.',
    '</table> <p style="font-size:0.875rem;margin:0.75rem 0 0.25rem;">WHO also splits underweight into three grades: severe thinness below 16.0, moderate thinness 16.0 to 16.9 and mild thinness 17.0 to 18.4.</p> <span style="font-size:0.8125rem;color:var(--gray-500);">Thinness grades: World Health Organization.',
    label='thinness grades kept as a sentence')

# =====================================================================
# PART 2 — D-11 and option B
# =====================================================================
H = 'blog/healthy-bmi-range/index.html'
rep(H, 'This guide explains everything you need to know about the healthy BMI range, including how it varies by sex, age, and ethnicity, and what you can do to reach or maintain it.',
    'This guide explains what the range means, why the same range applies to all adults, and what you can do to reach or maintain it.', label='D-11 intro')
rep(H, '<li><strong>Optimal range for women:</strong> 19 &ndash; 24 (accounts for higher female body fat)</li> <li><strong>Optimal range for men:</strong> 20 &ndash; 25 (accounts for higher male muscle mass)</li> <li><strong>Older adults (65+):</strong> 23 &ndash; 28 may carry the lowest mortality risk</li>',
    '<li><strong>Same range for everyone:</strong> women and men use the same cut-offs, at every adult age (WHO, CDC)</li> <li><strong>Adults 65+:</strong> in one large meta-analysis the lowest death rates were seen across BMI 23 to 33 (Winter 2014); an observed association, not a target</li>',
    label='D-11 takeaways')
rex(H, r'<h2>Healthy BMI Range for Women</h2>.*?<h2>Healthy BMI Range for Men</h2>.*?(?=<h2)',
    '<h2>Is the Healthy BMI Range Different for Women and Men?</h2> <p>No. The WHO and the CDC use the same adult range, 18.5 to 24.9, for women and men. '
    'Body fat is what differs: at the same BMI, men typically have a lower body-fat percentage than women '
    '(<a href="https://www.cdc.gov/nchs/products/databriefs/db508.htm" target="_blank" rel="noopener">CDC NCHS</a>). '
    'For results with that context, use the <a href="/women-bmi-calculator/">BMI calculator for women</a> or the <a href="/men-bmi-calculator/">BMI calculator for men</a>.</p> ',
    label='D-11 women/men sections')
rex(H, r' <figure style="margin:1\.25rem 0;"> <svg[^>]*aria-labelledby="svg-envelope-title svg-envelope-desc">.*?</figure>', '', label='D-11 widening-band figure')
rep('blog/bmi-formula/index.html',
    'Women naturally have higher body fat at the same BMI, so some experts suggest slightly different healthy ranges (19–24 for women, 20–25 for men).',
    'Women naturally have higher body fat at the same BMI, but the healthy range is the same 18.5–24.9 for both.', label='D-11 FAQ schema')
rep('blog/bmi-formula/index.html',
    'Women naturally have higher body fat at the same BMI, so some experts suggest slightly different healthy ranges (19&ndash;24 for women, 20&ndash;25 for men).',
    'Women naturally have higher body fat at the same BMI, but the healthy range is the same 18.5&ndash;24.9 for both.', label='D-11 FAQ')
rep('blog/bmi-limitations/index.html',
    '<p>The "optimal" BMI for longevity actually increases with age. Older adults with slightly higher BMIs (25-27) often have better survival rates than those in the "normal" range, a phenomenon known as the "obesity paradox."</p>',
    '<p>In a meta-analysis of adults aged 65 and over, the lowest death rates were seen across BMI 23 to 33 (<a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter et al., 2014</a>). '
    'This is an observed association, not a target: the adult cut-offs stay the same at every age.</p>', label='D-11 older adults')
rep('blog/bmi-limitations/index.html', '<p>Additionally, older adults often experience height loss', '<p>Older adults also often experience height loss', label='anti-slop: opener next to the edit')
# option B: no protein or calorie targets of our own, no unsourced "reset hormones" claims
rep('blog/bmi-tracking-guide/index.html', '<p> weight management experts, these evidence-based strategies help overcome plateaus:</p>',
    '<p>Common ways to work through a plateau:</p>', label='fragment')
rep('blog/bmi-tracking-guide/index.html', ' <li style="margin-bottom: 0.5rem;"><strong>Increase protein intake:</strong> Aim for 0.7&ndash;1g per pound of body weight to preserve muscle</li>', '', label='option B protein target')
rep('blog/bmi-tracking-guide/index.html', ' <li style="margin-bottom: 0.5rem;"><strong>Consider a diet break:</strong> 1&ndash;2 weeks at maintenance calories can help reset hormones</li>', '', label='unsourced claim')
rep('blog/how-to-lower-bmi/index.html', ' <div class="numbered-step"> <div class="numbered-step-content"> <h4>Prioritize Protein</h4> <p>Ensure you\'re getting adequate protein (0.7-1g per pound of body weight) to preserve muscle mass.</p> </div> </div>', '', label='option B protein target')
rep('blog/how-to-lower-bmi/index.html', ' <div class="numbered-step"> <div class="numbered-step-content"> <h4>Consider a Refeed Day</h4> <p>One day of eating at maintenance calories can help reset hormones. This isn\'t a cheat day - keep food choices healthy.</p> </div> </div>', '', label='unsourced claim')
rep('blog/bmi-and-metabolism/index.html', ' <li><strong>Use diet breaks</strong> - Periodic returns to maintenance calories may help restore metabolic hormones</li>', '', label='unsourced claim')

# =====================================================================
# PART 3 — shared components (impeccable polish, no copy changes)
# =====================================================================
PAGES = sorted([p for p in ['index.html', '404.html'] + [d + '/index.html' for d in os.listdir(ROOT) if os.path.isfile(os.path.join(ROOT, d, 'index.html'))]
                + ['blog/' + d + '/index.html' for d in os.listdir(os.path.join(ROOT, 'blog')) if os.path.isfile(os.path.join(ROOT, 'blog', d, 'index.html'))]
                if not p.startswith('research/') and os.path.isfile(os.path.join(ROOT, p))])

# 3.1 inline-styled call-to-action links (white text on 2.1-3.7:1 colours, gradients, glow) -> .cta-button (D-13, 5.4:1)
n_cta = 0
def cta_sub(m):
    global n_cta
    attrs, style, rest = m.group(1), m.group(2), m.group(3)
    st = style.replace(' ', '').lower()
    bg = re.search(r'background(?:-color)?:([^;]+)', st); col = re.search(r'(?:^|;)color:([^;]+)', st)
    if not (bg and col and col.group(1) in ('white', '#fff', '#ffffff')): return m.group(0)
    small = 'padding:0.5rem1.25rem' in st or 'padding:0.65rem1.25rem' in st
    n_cta += 1
    cls = 'cta-button cta-button--sm' if small else 'cta-button'
    return f'<a{attrs}class="{cls}"{rest}>'
for p in PAGES:
    s = rd(p)
    s2 = re.sub(r'<a((?:\s+(?!style=|class=)[a-z-]+="[^"]*")*\s+)style="([^"]*)"((?:\s+[a-z-]+="[^"]*")*)>', cta_sub, s)
    if s2 != s: wr(p, s2)
assert n_cta == 31, n_cta
LOG.append(('*', 'inline CTA links -> .cta-button', n_cta))

# 3.2 bylines: the inline side-stripe / grey styles -> the shared .byline (the men-page byline)
n_by = 0
for p in PAGES:
    s = rd(p); s2, k = re.subn(r'<p class="byline" style="[^"]*">', '<p class="byline">', s)
    if k: wr(p, s2); n_by += k
assert n_by == 34, n_by
LOG.append(('*', 'byline inline styles removed', n_by))

# 3.3 emoji and pictograph glyphs used as icons
s = rd('index.html'); s2, k = re.subn(r'<div style="font-size:1\.25rem;flex-shrink:0;">&#\d+;(?:&#8205;&#\d+;)?</div> ', '', s)
assert k == 6, k; wr('index.html', s2); LOG.append(('index.html', 'glyph icons removed', k))
s = rd('blog/underweight-bmi-risks/index.html')
s, k1 = re.subn(r'<div class="info-card-icon">[^<0-9A-Za-z%]+</div> ', '', s)
s, k2 = re.subn(r'<span class="tip-icon">[^<0-9A-Za-z]+</span> ', '', s)
assert (k1, k2) == (4, 4), (k1, k2); wr('blog/underweight-bmi-risks/index.html', s); LOG.append(('blog/underweight-bmi-risks/index.html', 'emoji icons removed', k1 + k2))
js = rd('assets/js/calculator.js')
js, k = re.subn(r'<span class="er-icon">(?:[^<$]|\$\{[^}]*\})*</span> ?', '', js)
assert k == 27, k; wr('assets/js/calculator.js', js); LOG.append(('assets/js/calculator.js', 'emoji in result headings removed', k))

# 3.4 stylesheet
css = rd('assets/css/styles.css')
for old in [".medical-disclaimer-title::before { content: '⚕️'; }\n", ".citation-box-title::before { content: '📚'; }\n"]:
    assert css.count(old) == 1, old; css = css.replace(old, '')
css = css.rstrip('\n') + '\n' + r'''
/* ============================================
   CMB-010 sitewide pass: shared components (impeccable polish)
   ============================================ */
/* Category shades dark enough to carry white text (WCAG AA): fills of bars and steps */
:root { --underweight-strong: #1d4ed8; --normal-strong: #15803d; --overweight-strong: #b45309; --obese-strong: #b91c1c; }

/* Call-to-action links use the site's action button (D-13): flat cyan-700, 5.4:1 */
.cta-row { text-align: center; margin: 2rem 0; }
.cta-button { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: 0.75rem 1.5rem; background: var(--link); color: #fff; border-radius: var(--radius-lg); font-weight: 600; line-height: 1.3; text-decoration: none; }
.cta-button:hover { background: var(--link-hover); color: #fff; text-decoration: none; }
.cta-button:focus-visible { outline: 3px solid var(--primary-light); outline-offset: 2px; }
.cta-button--sm { min-height: 40px; padding: 0.5rem 1rem; font-size: 0.875rem; }

/* No card inside a card: related cards and FAQ items inside a section card render flat (as on the men page) */
.content-section .blog-grid { gap: 0 1.5rem; }
.content-section .blog-card { background: transparent; box-shadow: none; border-radius: 0; border-top: 1px solid var(--gray-200); overflow: visible; }
.content-section .blog-card:hover { transform: none; box-shadow: none; }
.content-section .blog-card-content { padding: 0.875rem 0; }
.content-section .faq-list { gap: 0; border-top: 1px solid var(--gray-200); }
.content-section .faq-item { border: 0; border-bottom: 1px solid var(--gray-200); border-radius: 0; }
.content-section .faq-question { background: transparent; padding: 1rem 0; font-weight: 600; color: var(--gray-900); gap: 1rem; }
.content-section .faq-question:hover { background: transparent; color: var(--link); }
.content-section .faq-answer { padding: 0 0 1rem; }

/* Charts: bars that carry a white label sit on the strong shades; unlabeled bars keep their look */
.chart-bar-h-fill.underweight:not(:empty) { background: var(--underweight-strong); }
.chart-bar-h-fill.normal:not(:empty) { background: var(--normal-strong); }
.chart-bar-h-fill.overweight:not(:empty) { background: var(--overweight-strong); }
.chart-bar-h-fill.obese:not(:empty) { background: var(--obese-strong); }
.chart-bar-h-fill.primary { background: var(--link); }
.chart-bar-h-fill.secondary { background: var(--secondary); }
.chart-compare-bar.left { background: var(--link); }
.chart-compare-bar.right { background: var(--secondary); }
.chart-stack-bar { box-shadow: none; }
.chart-stack-segment { font-size: 0.75rem; }
.chart-stack-segment:hover { filter: none; }
.chart-stack-segment.underweight, .chart-legend-dot.underweight { background: var(--underweight-strong); }
.chart-stack-segment.normal, .chart-legend-dot.normal { background: var(--normal-strong); }
.chart-stack-segment.overweight, .chart-legend-dot.overweight { background: var(--overweight-strong); }
.chart-stack-segment.obese, .chart-legend-dot.obese { background: var(--obese-strong); }
.progress-step.active .progress-step-number { background: var(--link); }
.progress-step.completed .progress-step-number { background: var(--normal-strong); }
.stat-highlight { background: var(--primary-bg); border-width: 1px; }
.stat-highlight.warning { background: var(--warning-bg); }
.stat-highlight.success { background: var(--success-bg); }
.stat-highlight.error { background: var(--error-bg); }

/* Plain list of outside resources (replaces stacked tiles) */
.resource-list { list-style: none; padding: 0; margin: 1rem 0 0; border-top: 1px solid var(--gray-200); }
.resource-list li { padding: 0.75rem 0; border-bottom: 1px solid var(--gray-200); }
.resource-list a { font-weight: 600; }
.resource-list span { display: block; font-size: 0.875rem; color: var(--gray-600); margin-top: 0.125rem; }
'''
wr('assets/css/styles.css', css); LOG.append(('assets/css/styles.css', 'CMB-010 block + 2 emoji rules removed', 1))

# 3.5 low-contrast link and label colours set inline
n_c = 0
for p in PAGES:
    s = rd(p)
    s2, k = re.subn(r'(<a\b[^>]*style="[^"]*?)color:\s?var\(--primary\)', r'\1color:var(--link)', s)
    if k: wr(p, s2); n_c += k
LOG.append(('*', 'inline link colour --primary -> --link', n_c))

# 3.7 DESIGN.md: record the CMB-010 component rules; retire the stale gradient-button guidance (contradicted D-13)
D = 'DESIGN.md'
rep(D, '- **Obese severe — Red 800** (`#991b1b`)\n',
    '- **Obese severe — Red 800** (`#991b1b`)\n'
    '- **Strong shades for white labels** (CMB-010): a bar, segment or step number that carries white text uses '
    '`--underweight-strong` `#1d4ed8`, `--normal-strong` `#15803d`, `--overweight-strong` `#b45309`, `--obese-strong` `#b91c1c` '
    '(all 5:1 or better with white). Unlabeled bars keep the base colours.\n'
    '- **Tints for table cells**: category cells use the `/bmi-chart/` tints (under `#dbeafe`, healthy `#d1fae5`, over `#fde68a`, '
    'class 1 `#fed7aa`, class 2 `#fecaca`, class 3 `#fca5a5`) with text tinted from the same hue, never grey on colour.\n',
    label='DESIGN: category shades')
rep(D, '### Primary CTA — `.calculate-btn`\n- Full-width `height: 48px`, cyan gradient `linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)`, white text, `font-weight: 600`.\n- Radius `--radius-lg` (0.75rem), tinted shadow, lifts 2 px on hover.\n',
    '### Primary CTA — `.calculate-btn` and `.cta-button`\n- `.calculate-btn` (calculators): full-width `height: 48px`, flat `--link` background, white text (5.4:1), hover `--link-hover`; no gradient, glow or lift (D-13).\n'
    '- `.cta-button` (links that act as buttons, CMB-010): the same flat `--link` treatment, `min-height: 48px`, radius `--radius-lg`; `.cta-button--sm` is 40 px for in-card actions. '
    'Inline-styled button links are not allowed (check_structure fails them).\n',
    label='DESIGN: CTA')
rep(D, '### FAQ — `.faq-item`\n',
    '### Cards inside a section\n- A `.content-section` is the card. Related cards (`.blog-card`) and FAQ items inside it render flat, divided by hairlines '
    '(CMB-010), as on the men page. Never a card inside a card.\n- Outside links to sources use `.resource-list` (link plus one muted line), not tiles.\n\n'
    '### Icons\n- No emoji or Unicode pictographs as icons, in page copy or in calculator results (CMB-010; check_structure fails them).\n\n### FAQ — `.faq-item`\n',
    label='DESIGN: flat cards + icons')
rep(D, '- **Do** place one primary CTA per decision point and give it `.calculate-btn` or an equivalent gradient-and-shadow treatment.',
    '- **Do** place one primary CTA per decision point and give it `.calculate-btn` (a button) or `.cta-button` (a link); flat `--link`, no gradient or shadow (D-13).',
    label='DESIGN: do-list')

# 3.6 /calculators/: per-calculator rainbow link colours (2.1-3.9:1) -> --link; coloured example values -> dark text
s = rd('calculators/index.html')
s, k1 = re.subn(r'(<a\b[^>]*style="[^"]*?)color:\s?#(?:06b6d4|0891b2|22c55e|3b82f6|6366f1|8b5cf6|ec4899|f59e0b|f97316)', r'\1color:var(--link)', s)
s, k2 = re.subn(r'<strong style="color:\s?(?:#22c55e|#f97316|#6366f1|var\(--overweight\));">', '<strong style="color:var(--gray-900);">', s)
assert (k1, k2) == (20, 5), (k1, k2)
wr('calculators/index.html', s); LOG.append(('calculators/index.html', 'rainbow link colours + coloured values', k1 + k2))

# =====================================================================
# PART 5 — page dates (DEVLOG §4 rule; checked with research/dates/date_truth.py after the commit)
# The 19 pages whose visible <main> text changes here move both dates to DAY (the day chat built and proved the batch).
# =====================================================================
import json
def object_spans(text):
    """(start, end, obj) for every JSON object in text that parses on its own"""
    spans, stack, i, ins, esc = [], [], 0, False, False
    while i < len(text):
        c = text[i]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        elif c == '"': ins = True
        elif c == '{': stack.append(i)
        elif c == '}' and stack:
            a = stack.pop()
            try: spans.append((a, i + 1, json.loads(text[a:i + 1])))
            except Exception: pass
        i += 1
    return spans

def set_date_modified(page, day):
    """dateModified of every non-Dataset schema object that carries one -> day (Dataset dates track the data)"""
    olds = []
    def fix_block(m):
        blk = m.group(2); edits = []
        for a, b, obj in object_spans(blk):
            if isinstance(obj, dict) and 'dateModified' in obj and obj.get('@type') != 'Dataset':
                inner = [(x, y) for x, y, o in object_spans(blk[a + 1:b - 1]) if isinstance(o, dict) and 'dateModified' in o]
                sub = blk[a:b]
                mm = None
                for mt in re.finditer(r'("dateModified":\s?")([0-9-]+)(")', sub):
                    if not any(x + 1 <= mt.start() < y + 1 for x, y in inner): mm = mt; break
                if mm and mm.group(2) != day:
                    olds.append(mm.group(2)); edits.append((a + mm.start(2), a + mm.end(2)))
        for x, y in sorted(edits, reverse=True): blk = blk[:x] + day + blk[y:]
        return m.group(1) + blk + m.group(3)
    out = re.sub(r'(?s)(<script type="application/ld\+json">)(.*?)(</script>)', fix_block, page)
    return out, olds



DAY = '2026-10-14'
CHANGED = ['/', '/about/', '/calculators/', '/women-bmi-calculator/', '/age-bmi-calculator/', '/lean-body-mass/', '/new-bmi-calculator/', '/blog/',
           '/blog/bmi-formula/', '/blog/bmi-history/', '/blog/healthy-bmi-range/', '/blog/bmi-categories/', '/blog/bmi-chart-explained/',
           '/blog/underweight-bmi-risks/', '/blog/bmi-limitations/', '/blog/bmi-and-metabolism/', '/blog/waist-to-height-ratio/',
           '/blog/how-to-lower-bmi/', '/blog/bmi-tracking-guide/']
sm = rd('sitemap.xml'); nd = nl = 0
for path in CHANGED:
    f = (path.strip('/') + '/index.html') if path != '/' else 'index.html'
    src = rd(f); src2, olds = set_date_modified(src, DAY)
    if src2 != src: wr(f, src2); nd += 1
    loc = f'<loc>https://calculatemybmi.net{path}</loc><lastmod>'
    m = re.search(re.escape(loc) + r'([0-9-]+)</lastmod>', sm); assert m, path
    sm = sm.replace(m.group(0), loc + DAY + '</lastmod>'); nl += 1
wr('sitemap.xml', sm)
assert (nd, nl) == (13, 19), (nd, nl)
LOG.append(('sitemap.xml + schema', f'dates -> {DAY}: dateModified on {nd} pages, lastmod on {nl}', nd + nl))

print('\n'.join(f'{f:45s} {lab:50s} {n}' for f, lab, n in LOG))
print('replacements:', len(LOG))
