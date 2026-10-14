#!/usr/bin/env python3
"""CMB-011 CALC-RESULTS + residue repair. Builds the change set in memory; writes nothing unless every edit matches.
usage: python3 patch_cmb011.py REPO_ROOT BUILD_DIR"""
import re, sys, os, json

ROOT, BUILD = sys.argv[1], sys.argv[2]
DATE = '2026-10-14'
buf = {}

def load(p):
    if p not in buf:
        buf[p] = open(os.path.join(ROOT, p), encoding='utf-8', newline='').read()
    return buf[p]

def _ws_pattern(old):
    parts = re.split(r'(\s+)', old)
    return ''.join(r'\s+' if (pt and pt.isspace()) else re.escape(pt) for pt in parts)

def rep(p, old, new, count=1, label=''):
    s = load(p)
    n = s.count(old)
    if n == count:
        buf[p] = s.replace(old, new); return
    pat = _ws_pattern(old)
    m = list(re.finditer(pat, s))
    assert len(m) == count, f'{p} {label or old[:70]!r}: expected {count}, exact {n}, ws {len(m)}'
    buf[p] = re.sub(pat, lambda _m: new, s)

def span_div(s, start):
    """end offset of the element (div) that starts at `start`."""
    i = s.index('>', start) + 1; depth = 1
    while depth:
        o = s.find('<div', i); c = s.find('</div>', i)
        if o != -1 and o < c: depth += 1; i = o + 4
        else: depth -= 1; i = c + 6
    return i

# ---------------------------------------------------------------- calculator.js
JS = 'assets/js/calculator.js'
blocks = {}
cur = None
for line in open(os.path.join(BUILD, 'new_js_blocks.js'), encoding='utf-8').read().split('\n'):
    m = re.match(r'^//@@ (\w+)$', line)
    if m: cur = m.group(1); blocks[cur] = []; continue
    if cur: blocks[cur].append(line)
blocks = {k: '\n'.join(v).strip('\n') for k, v in blocks.items()}

def func_span(s, name, with_comments=False):
    m = re.search(r'(?m)^function ' + name + r'\(', s)
    assert m, f'function {name} not found'
    start = m.start()
    if with_comments:
        while True:
            prev = s.rfind('\n', 0, start - 1)
            line = s[prev + 1:start - 1]
            if line.startswith('//'): start = prev + 1
            else: break
    eol = s.index('\n', m.start())
    first = s[m.start():eol]
    if first.count('{') and first.count('{') == first.count('}'):
        end = eol + 1
    else:
        end = s.index('\n}\n', m.start()) + 3
    return start, end

js = load(JS)
WITH_COMMENTS = {'weightBounds'}
for name, body in blocks.items():
    s = buf[JS]
    a, b = func_span(s, name, name in WITH_COMMENTS)
    if body:
        buf[JS] = s[:a] + body + '\n' + s[b:]
    else:                                   # deletion: drop the function and one blank line after it
        if s[b:b + 1] == '\n': b += 1
        buf[JS] = s[:a] + s[b:]
# clamp the "you" label of the weight bar so it never runs off the edge
rep(JS, '<div class="er-weightbar-you" style="left:${pos}%;">', '<div class="er-weightbar-you" style="left:${Math.max(10, Math.min(90, pos))}%;">')
assert 'genHealthRisks' not in buf[JS] and 'riskColor' not in buf[JS] and '&#10140;' not in buf[JS]
assert 'linear-gradient' not in buf[JS]

# ---------------------------------------------------------------- styles.css
CSS = 'assets/css/styles.css'
css = load(CSS)
a = css.index('/* BMI Result Card */'); b = css.index('/* Results Grid */')
buf[CSS] = css[:a] + open(os.path.join(BUILD, 'css_card.css'), encoding='utf-8').read() + '\n' + css[b:]
css = buf[CSS]
a = css.index('.result-item { padding'); b = css.index('/* Weight Range Box */')
buf[CSS] = css[:a] + open(os.path.join(BUILD, 'css_tiles.css'), encoding='utf-8').read() + '\n' + css[b:]
css = buf[CSS]
a = css.index('/* Extended Results */'); b = css.index('/* Content Sections */')
buf[CSS] = css[:a] + open(os.path.join(BUILD, 'css_er.css'), encoding='utf-8').read() + '\n' + css[b:]

# ---------------------------------------------------------------- calculator pages: results markup
NB = 'new-bmi-calculator/index.html'
rep(NB, '<div style="background:linear-gradient(135deg,#ebf8ff,#e0f2fe);border:1px solid #90cdf4;border-radius:12px;padding:1.25rem;margin:1rem 0 0.75rem;"> <h3 style="font-size:1rem;color:#2b6cb0;margin:0 0 0.75rem;text-align:center;">New BMI vs Traditional BMI Comparison</h3>',
        '<div style="margin:1.5rem 0 0.75rem;"> <h2 style="font-size:1.0625rem;line-height:1.4;color:var(--gray-900);margin:0 0 0.75rem;">New BMI vs traditional BMI</h2>')
rep(NB, '<div class="result-item-label">Category Impact</div>', '<div class="result-item-label">Category</div>')

IW = 'ideal-weight/index.html'
rep(IW, '<div class="result-primary" style="background:var(--primary-bg);border:2px solid var(--primary-light);border-radius:var(--radius-lg);padding:1.5rem;text-align:center;margin-bottom:1rem;"> <div style="font-size:0.75rem;color:var(--gray-500);text-transform:uppercase;">Average Ideal Weight</div> <div style="font-size:2rem;font-weight:700;color:var(--primary-dark);" id="ideal-average">',
        '<div class="result-primary" style="background:var(--primary-bg);border-radius:var(--radius-lg);padding:1.5rem;text-align:center;margin-bottom:1rem;"> <div style="font-size:0.75rem;color:var(--gray-600);text-transform:uppercase;letter-spacing:0.02em;">Average Ideal Weight</div> <div style="font-size:2rem;font-weight:700;color:var(--link);" id="ideal-average">')

rep(IW, '<div class="result-item"><div class="result-item-label">BMI Range (18.5-24.9)</div>', '<div class="result-item result-item--wide"><div class="result-item-label">BMI Range (18.5-24.9)</div>')

LB = 'lean-body-mass/index.html'
rep(LB, '<div class="results-grid results-grid-4"> <div class="result-item"><div class="result-item-label">Lean Body Mass</div><div class="result-item-value highlight" id="lbm-lbm">—</div></div> <div class="result-item"><div class="result-item-label">Lean Mass (lbs)</div><div class="result-item-value" id="lbm-lbm-lbs">—</div></div>',
        '<div class="results-grid results-grid-3"> <div class="result-item result-item--wide"><div class="result-item-label">Lean Body Mass</div><div class="result-item-value highlight" id="lbm-lbm">—</div></div>')
s = load(LB)
a = s.index('<!-- Body Composition Charts -->')
d = s.index('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;margin-top:1.5rem;" id="lbm-charts" class="hidden">', a)
e = span_div(s, d)
NEW_CHART = ('<!-- Body composition chart: lean vs fat share (CMB-011) --> <div id="lbm-charts" class="hidden" style="margin-top:1.75rem;text-align:center;">'
             ' <h2 style="margin:0 0 1rem;font-size:1.0625rem;line-height:1.4;color:var(--gray-900);">Lean and fat share of your weight</h2>'
             ' <div id="composition-donut" style="width:160px;height:160px;border-radius:50%;margin:0 auto 1rem;background:conic-gradient(#0e7490 0% 75%, #b45309 75% 100%);position:relative;">'
             ' <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:100px;height:100px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;">'
             ' <span id="donut-lbm-pct" style="font-size:1.5rem;font-weight:700;color:var(--gray-900);">—%</span> <span style="font-size:0.75rem;color:var(--gray-600);">lean mass</span> </div> </div>'
             ' <div style="display:flex;justify-content:center;gap:1.5rem;font-size:0.8125rem;color:var(--gray-700);">'
             ' <div style="display:flex;align-items:center;gap:0.375rem;"><span style="width:12px;height:12px;background:#0e7490;border-radius:2px;"></span>Lean mass</div>'
             ' <div style="display:flex;align-items:center;gap:0.375rem;"><span style="width:12px;height:12px;background:#b45309;border-radius:2px;"></span>Fat mass</div> </div> </div>')
buf[LB] = s[:a] + NEW_CHART + s[e:]
rep(LB, '.chart-donut, .chart-bar-h { box-shadow: 0 1px 3px rgba(0,0,0,0.08); } .chart-donut:hover, .chart-bar-h:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); } ', '')
s = load(LB)
a = s.index('// Chart update function for LBM calculator')
b = s.index('</script>', a)
NEW_SCRIPT = r'''// Donut chart for the LBM calculator: lean vs fat share, from the kilogram values calculator.js puts on the tiles (data-kg, CMB-011)
function updateLBMCharts(lbmKg, fatKg) {
  const chartsContainer = document.getElementById('lbm-charts');
  if (!chartsContainer) return;
  chartsContainer.classList.remove('hidden');
  const lbmPct = (lbmKg / (lbmKg + fatKg) * 100).toFixed(1);
  const donut = document.getElementById('composition-donut');
  if (donut) donut.style.background = `conic-gradient(#0e7490 0% ${lbmPct}%, #b45309 ${lbmPct}% 100%)`;
  document.getElementById('donut-lbm-pct').textContent = lbmPct + '%';
}

const origCalcBtn = document.getElementById('calc-lbm-btn');
if (origCalcBtn) {
  origCalcBtn.addEventListener('click', function() {
    setTimeout(function() {
      const lbmKg = parseFloat(document.getElementById('lbm-lbm')?.dataset.kg);
      const fatKg = parseFloat(document.getElementById('lbm-fat-mass')?.dataset.kg);
      if (!isNaN(lbmKg) && !isNaN(fatKg)) updateLBMCharts(lbmKg, fatKg);
    }, 100);
  });
}
'''
buf[LB] = s[:a] + NEW_SCRIPT + s[b:]

# ---------------------------------------------------------------- residue of earlier bulk deletions
W = 'women-bmi-calculator/index.html'
rep(W, '<!-- BMI Chart for Women by Age --> <section class="content-section"> <p style="color:var(--gray-700);line-height:1.75;">The CDC adult BMI range',
       '<!-- BMI Chart for Women by Age --> <section class="content-section"> <h2>BMI for women by age</h2> <p style="color:var(--gray-700);line-height:1.75;">The CDC adult BMI range')
rep(W, '<p style="font-size:0.8125rem;color:var(--gray-500);">Rows 18&ndash;64: WHO adult BMI categories. Row 65+: <a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter JE, MacInnis RJ, Wattanapenpaiboon N, Nowson CA. &ldquo;BMI and all-cause mortality in older adults: a meta-analysis.&rdquo; <em>Am J Clin Nutr</em> 2014;99(4):875&ndash;90</a> &mdash; a meta-analysis of 32 cohort studies covering 197,940 adults aged 65 and older found that all-cause mortality was elevated below BMI 23 and did not increase again until BMI exceeded 33. This is an observational finding across mostly Western populations, not a WHO or CDC clinical recommendation, and it does not distinguish women from men. See our full BMI chart for women or the <a href="/blog/healthy-bmi-range/">healthy BMI range guide</a> for more context.</p>',
       '<p style="color:var(--gray-700);line-height:1.75;">For adults 65 and older, a meta-analysis of 32 cohort studies covering 197,940 people found that all-cause mortality was elevated below BMI 23 and did not increase again until BMI exceeded 33 (<a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter et al., <em>Am J Clin Nutr</em> 2014</a>). This is an observational finding across mostly Western populations, not a WHO or CDC clinical recommendation, and it does not distinguish women from men. The <a href="/bmi-chart/">BMI chart</a> and the <a href="/blog/healthy-bmi-range/">healthy BMI range guide</a> give more context.</p>')
rep(W, '<h3 style="font-size:1.0625rem;margin-top:2rem;">Prevalence in U.S. Adult women</h3>', '<h3 style="font-size:1.0625rem;margin-top:2rem;">Obesity among US women</h3>')

PP = '<a href="https://pubmed.ncbi.nlm.nih.gov/10981254/" target="_blank" rel="noopener">Pai &amp; Paloucek, 2000</a>'
rep(IW, '<section class="content-section">   <h3 style="margin-top:1.5rem;">Method 2: Elbow Breadth</h3> <p>The 1983 Metropolitan Life tables defined frame size by elbow breadth: with the forearm bent upward at 90 degrees, the width across the elbow is compared with height-specific reference values (' + PP + ').  <h3 style="margin-top:1.5rem;">How Frame Size Adjusts Ideal Weight</h3> <p>Once you know your frame size, the traditional adjustment from Hamwi\'s rule of thumb allows about 10% above or below the calculated weight (' + PP + '):</p>',
    '<section class="content-section"> <h2 id="frame-size">Body frame size</h2> <p>The early height&ndash;weight tables listed weights for small, medium and large frames but left the frame size to the examiner&rsquo;s judgment (' + PP + '). A simple way to estimate yours is your wrist circumference at its narrowest point, compared with cut-offs for your height (<a href="https://medlineplus.gov/ency/imagepages/17182.htm" target="_blank" rel="noopener">MedlinePlus</a>):</p>'
    ' <ul style="margin-bottom:0.75rem;">'
    '<li><strong>Women under 5&prime;2&Prime; (157 cm):</strong> small frame under 5.5 in (14.0 cm), medium 5.5&ndash;5.75 in (14.0&ndash;14.6 cm), large over 5.75 in (14.6 cm).</li>'
    '<li><strong>Women 5&prime;2&Prime; to 5&prime;5&Prime; (157&ndash;165 cm):</strong> small under 6 in (15.2 cm), medium 6&ndash;6.25 in (15.2&ndash;15.9 cm), large over 6.25 in (15.9 cm).</li>'
    '<li><strong>Women over 5&prime;5&Prime; (165 cm):</strong> small under 6.25 in (15.9 cm), medium 6.25&ndash;6.5 in (15.9&ndash;16.5 cm), large over 6.5 in (16.5 cm).</li>'
    '<li><strong>Men over 5&prime;5&Prime; (165 cm):</strong> small 5.5&ndash;6.5 in (14.0&ndash;16.5 cm), medium 6.5&ndash;7.5 in (16.5&ndash;19.1 cm), large over 7.5 in (19.1 cm).</li>'
    '</ul> <p style="font-size:0.875rem;color:var(--gray-600);">MedlinePlus lists men only above 5&prime;5&Prime;. Elbow breadth, measured with the forearm bent upward at 90 degrees, is another way to judge frame size.</p>'
    ' <h3 style="margin-top:1.5rem;">How Frame Size Adjusts Ideal Weight</h3> <p>Once you know your frame size, the traditional adjustment allows about 10% above or below the calculated weight (' + PP + '):</p>')
# frame comparison chart: the numbers come from the same four formulas as the tables above (5'6", +/-10%)
def avg_kg(sex, inches):
    o = inches - 60
    f = [(50 + 2.3 * o), (52 + 1.9 * o), (56.2 + 1.41 * o), (48 + 2.7 * o)] if sex == 'm' else [(45.5 + 2.3 * o), (49 + 1.7 * o), (53.1 + 1.36 * o), (45.5 + 2.2 * o)]
    return sum(f) / 4
wf, mf = avg_kg('f', 66) * 2.20462, avg_kg('m', 66) * 2.20462
ws, wl, ms, ml = round(wf * 0.9), round(wf * 1.1), round(mf * 0.9), round(mf * 1.1)
assert (ws, wl, ms, ml) == (118, 145, 127, 155), (ws, wl, ms, ml)
pct = lambda v: f'{v / 180 * 100:.0f}%'
rep(IW, '<div class="chart-compare-bar left" style="width:75%;">Small: 117 lbs</div>', f'<div class="chart-compare-bar left" style="width:{pct(ws)};">Small: {ws} lbs</div>')
rep(IW, '<div class="chart-compare-bar right" style="width:90%;">Large: 143 lbs</div>', f'<div class="chart-compare-bar right" style="width:{pct(wl)};">Large: {wl} lbs</div>')
rep(IW, '<div class="chart-compare-bar left" style="width:80%;">Small: 124 lbs</div>', f'<div class="chart-compare-bar left" style="width:{pct(ms)};">Small: {ms} lbs</div>')
rep(IW, '<div class="chart-compare-bar right" style="width:95%;">Large: 167 lbs</div>', f'<div class="chart-compare-bar right" style="width:{pct(ml)};">Large: {ml} lbs</div>')
# FAQ: the wrist method now points at a section that has the cut-offs (visible answer + FAQPage JSON-LD, word for word)
rep(IW, 'measure your wrist at the narrowest point with a tape measure and compare to height-specific reference values (see the body frame section above). The elbow breadth method: extend your arm, bend at 90 degrees, and measure',
        'measure your wrist at the narrowest point with a tape measure and compare it with the MedlinePlus cut-offs for your height in the body frame size section above. The elbow breadth method: extend your arm, bend at 90 degrees, and measure')
rep(IW, 'measure your wrist at the narrowest point with a tape measure and compare to height-specific reference values (see the body frame section above). The <strong>elbow breadth method</strong>',
        'measure your wrist at the narrowest point with a tape measure and compare it with the MedlinePlus cut-offs for your height in the <a href="#frame-size">body frame size section</a> above. The <strong>elbow breadth method</strong>')

BL = 'blog/bmi-limitations/index.html'
rep(BL, '<li><a href="#muscle-vs-fat">Limitation #1: BMI Cannot Distinguish Muscle from Fat</a></li>',
        '<li><a href="#muscle-vs-fat">Limitation #1: BMI Cannot Distinguish Muscle from Fat</a></li> <li><a href="#fat-distribution">Limitation #2: It Ignores Fat Distribution</a></li>')
rep(BL, '<div class="chart-bar-h"> <div class="chart-bar-h-item"> <span class="chart-bar-h-label">Muscle Density</span>  </div> <div class="chart-bar-h-item"> <span class="chart-bar-h-label">Fat Density</span> <div class="chart-bar-h-track"> </div></div></div> <p>The waist-to-height ratio is a simple alternative that captures fat distribution and has been shown to be a better predictor of cardiovascular risk than BMI.</p>',
        '<!-- Section 3: Fat Distribution --> <h2 id="fat-distribution">Limitation #2: It Ignores Fat Distribution</h2> <p>BMI uses total weight, so it cannot show where fat is stored. US clinical guidelines treat fat around the waist as a risk marker in its own right and pair BMI with a waist measurement: above 35 inches (88 cm) for women or 40 inches (102 cm) for men signals higher risk, mainly at a BMI of 25 to 34.9 (<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">NHLBI</a>).</p> <p>The <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> is another simple check of fat distribution; a meta-analysis found it a better screening tool for cardiometabolic risk than waist circumference or BMI (<a href="https://pubmed.ncbi.nlm.nih.gov/22106927/" target="_blank" rel="noopener">Ashwell et al., 2012</a>).</p>')
rep(BL, 'across ethnic groups. This has led the World Health Organization to recommend different BMI cutoffs for Asian populations.</p>  <div class="alert alert-warning"> <div class="alert-title">Important Consideration</div> Despite WHO recommendations, most healthcare systems worldwide still use the standard BMI cutoffs regardless of ethnicity, potentially leading to missed diagnoses in some populations and over-diagnosis in others. </div>',
        'across ethnic groups. In 2004, a <a href="https://pubmed.ncbi.nlm.nih.gov/14726171/" target="_blank" rel="noopener">WHO expert consultation</a> found that a substantial share of Asian people have a high risk of type 2 diabetes and cardiovascular disease at BMIs below 25. It kept the international categories and identified BMI 23 and 27.5 as additional public-health action points.</p>')

BF = 'blog/body-fat-vs-bmi/index.html'
rep(BF, '<p style="font-size: 0.875rem; color: var(--gray-500); text-align: center;"><em>Example composition of a healthy adult male. Individual compositions vary significantly.</em></p>', '')
rep(BF, '<div class="alert alert-info"> <div class="alert-title">Pro Tip: Consistency Matters More Than Accuracy</div> For tracking progress, use the same measurement method at the same time of day. While a BIA scale may not give you an exact number, it can reliably track trends over time. </div>', '')
rep(BF, '<p>For athletes and highly active individuals, body fat percentage combined with <a href="/lean-body-mass/">lean body mass calculations</a> provides much more useful health and performance data than BMI alone.</p>',
        '<p>Muscle adds weight, and BMI cannot tell it from fat, so a muscular athlete can have a high BMI and a low body fat percentage. For athletes and highly active people, body fat percentage together with <a href="/lean-body-mass/">lean body mass</a> says more than BMI alone; <a href="/blog/bmi-for-athletes/">BMI for athletes</a> covers the research.</p>')

BH = 'blog/bmi-history/index.html'
rep(BH, '<p>Learn more about these classifications in our comprehensive <a href="/blog/bmi-categories/">BMI categories guide</a>.</p>',
        '<p>WHO&rsquo;s adult categories run from underweight (below 18.5) to class III obesity (40 and above); our <a href="/blog/bmi-categories/">BMI categories guide</a> explains each one.</p>')
rep(BH, '<p>This paradox underscores that BMI was designed for population studies, not individual assessment.',
        '<p>These limitations trace back to BMI&rsquo;s origin as a population statistic rather than an individual assessment.')

BC = 'blog/bmi-categories/index.html'
rep(BC, '<p>In 2004, a <a href="https://pubmed.ncbi.nlm.nih.gov/14726171/" target="_blank" rel="noopener">WHO expert consultation</a> acknowledged these differences and identified BMI 23 and 27.5 as additional public-health action points (increased and high risk), while keeping the international categories. Several countries have since set lower cut-offs of their own recommendation.</p>',
        '<h3>Lower action points for Asian populations</h3> <p>In 2004, a <a href="https://pubmed.ncbi.nlm.nih.gov/14726171/" target="_blank" rel="noopener">WHO expert consultation</a> found that a substantial share of Asian people have a high risk of type 2 diabetes and cardiovascular disease at BMIs below 25. It identified BMI 23 and 27.5 as additional public-health action points (increased and high risk), while keeping the international categories. Several countries have since set lower cut-offs of their own.</p>')

s = load(NB)
a = s.index('<!-- Adoption Status --> <section class="content-section"> <p style="font-size:0.9375rem;color:#4a5568;">The primary reason for non-adoption')
b = s.index('</section>', a) + len('</section>')
buf[NB] = s[:a] + s[b:].lstrip(' ')

HR = 'blog/bmi-and-health-risks/index.html'
rep(HR, '<p>Notably, obesity also increases osteoarthritis risk in non-weight-bearing joints like the hands, suggesting that metabolic factors (inflammation, adipokines) contribute alongside mechanical stress.</p>',
        '<p>Obesity is also linked to osteoarthritis in joints that bear no weight, such as the hands, which suggests that metabolic factors (inflammation, adipokines) contribute alongside mechanical stress.</p>')
rep(HR, '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-with="2"></svg>', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>')

# /calculators/ kids example: the exact percentile is 54.46, so the whole-number percentile is the 54th (the calculator now prints it)
rep('calculators/index.html', 'about the <strong style="color:var(--gray-900);">55th percentile &mdash; healthy weight</strong>', 'about the <strong style="color:var(--gray-900);">54th percentile &mdash; healthy weight</strong>')

WH = 'blog/waist-to-height-ratio/index.html'
rep(WH, '<!-- Section 7: Men vs Women -->  <p>Women typically have lower WHtR values', '<!-- Section 7: Men vs Women --> <h3>Women and men</h3> <p>Women typically have lower WHtR values')

exec(open(os.path.join(BUILD, 'hub_patch.py'), encoding='utf-8').read())

# ---------------------------------------------------------------- gates, tests, design notes
for p, src in (('scripts/check_content_integrity.py', 'check_content_integrity.py'), ('scripts/check_structure.py', 'check_structure.py'),
               ('research/calculator-checks/calc_e2e_playwright.py', 'calc_e2e_playwright.py'), ('research/calculator-checks/calc_test_jsdom.js', 'calc_test_jsdom.js'),
               ('DESIGN.md', 'DESIGN.md')):
    load(p); buf[p] = open(os.path.join(BUILD, 'files', src), encoding='utf-8').read()

# ---------------------------------------------------------------- dates (DEVLOG §4): pages whose visible <main> text changed
TEXT_CHANGED = ['/women-bmi-calculator/', '/ideal-weight/', '/blog/bmi-limitations/', '/blog/body-fat-vs-bmi/', '/blog/bmi-history/',
                '/blog/bmi-categories/', '/new-bmi-calculator/', '/blog/bmi-and-health-risks/', '/blog/waist-to-height-ratio/', '/lean-body-mass/',
                '/calculators/', '/blog/']
SM = 'sitemap.xml'; load(SM)
date_moves = []
for path in TEXT_CHANGED:
    f = path.strip('/') + '/index.html'
    s = load(f)
    def fix_ld(m):
        body = m.group(1)
        try: data = json.loads(body)
        except Exception: return m.group(0)
        out = body
        def walk(x):
            nonlocal out
            if isinstance(x, dict):
                if 'dateModified' in x and x.get('@type') != 'Dataset' and x['dateModified'] != DATE:
                    out = out.replace(f'"dateModified": "{x["dateModified"]}"', f'"dateModified": "{DATE}"', 1)
                for v in x.values(): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(data)
        return m.group(0).replace(body, out)
    buf[f] = re.sub(r'(?s)<script type="application/ld\+json">(.*?)</script>', fix_ld, s)
    old = re.search(r'<loc>https://calculatemybmi\.net' + re.escape(path) + r'</loc><lastmod>([^<]+)</lastmod>', buf[SM])
    assert old, path
    if old.group(1) != DATE:
        buf[SM] = buf[SM].replace(old.group(0), old.group(0).replace(old.group(1), DATE))
    date_moves.append((path, old.group(1)))

# ---------------------------------------------------------------- write
changed = [p for p in buf if buf[p] != open(os.path.join(ROOT, p), encoding='utf-8', newline='').read()]
for p in changed:
    open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='').write(buf[p])
print('changed:', len(changed)); [print('  ', p) for p in sorted(changed)]
print('lastmod before:', date_moves)
