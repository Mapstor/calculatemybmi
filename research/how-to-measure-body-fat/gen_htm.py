#!/usr/bin/env python3
"""Build /blog/how-to-measure-body-fat/ for calculatemybmi.net.
Verified facts (fetched 7 Oct 2026):
- Burns RD, Fu Y, Constantino N. PLOS ONE 2019;14(3):e0214029. 437 college students (mean age 19.2), DXA (Hologic) criterion;
  surrogates: hydrostatic weighing, 7-site skinfolds, Bod Pod (ADP), near-infrared (Futrex), Omron hand-held BIA, Tanita foot-to-foot
  BIA scale, Valhalla 4-electrode BIA. Mean differences vs DXA: HW 1.0, skinfolds 1.4 (absolute error), ADP 1.6, Valhalla 1.6,
  Omron 4.9 (largest). Equivalent within +-10% of the DXA mean (= +-2.7 points): skinfolds, ADP, 4-electrode BIA, HW. Not equivalent:
  Tanita, Omron, IR; at +-15% all except Omron and IR were equivalent. MAPE 11.7% (skinfolds, lowest) to 21.9% (Omron, highest).
  Errors larger at higher body fat. Pre-test protocol and skinfold re-measure rule from the methods section.
- Deurenberg 1991 (PubMed 2043597): SEE 4.1 points; slight overestimation in obesity.
- CDC NHANES DXX documentation: DXA the most widely accepted method; NHANES BCA option adds 5% of lean mass to fat mass.
- DoD circumference vs hydrostatic weighing / BIA / skinfolds in 69 active young adults (Int J Exerc Sci Conf Proc 14(1), abstract 40):
  wide limits of agreement (> +-3.5 points) against all other methods."""
import json, os, re, sys, html as H
ROOT, OUT = sys.argv[1], sys.argv[2]
SLUG = "blog/how-to-measure-body-fat"; URL = f"https://calculatemybmi.net/{SLUG}/"
BURNS = "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029"
DEUR = "https://pubmed.ncbi.nlm.nih.gov/2043597/"
DXX = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm"
DOD = "https://digitalcommons.wku.edu/ijesab/vol14/iss1/40"
EQ = 2.7
BARS = [("Underwater (hydrostatic) weighing", 1.0, "lab"), ("Skinfold calipers, 7 sites", 1.4, "home"), ("Bod Pod (air displacement)", 1.6, "lab"),
        ("Lab impedance analyzer, 4 electrodes", 1.6, "lab"), ("Hand-held impedance device", 4.9, "home")]

def chart():
    W, rowh, L, T = 680, 66, 12, 40; Hh = T + rowh * len(BARS) + 40; mx = 6.0
    X = lambda v: L + v / mx * (W - L - 70)
    g = [f'<text x="{X(EQ) + 8:.1f}" y="{T - 14}" class="hm-eq">&#177;{EQ} points: the &#8220;equivalent&#8221; cut-off</text>',
         f'<line x1="{X(EQ):.1f}" x2="{X(EQ):.1f}" y1="{T - 30}" y2="{T - 4}" stroke="#2E7D4F" stroke-width="2" stroke-dasharray="6 4"/>']
    for i in range(len(BARS)):   # cut-off drawn only across the bar band of each row, never through the labels
        y = T + i * rowh; g.append(f'<line x1="{X(EQ):.1f}" x2="{X(EQ):.1f}" y1="{y + 27}" y2="{y + 58}" stroke="#2E7D4F" stroke-width="2" stroke-dasharray="6 4"/>')
    for i, (lab, v, kind) in enumerate(BARS):
        y = T + i * rowh; col = "#1F4E79" if kind == "lab" else ("#2E7D4F" if v <= EQ else "#C2481E")
        g.append(f'<text x="{L}" y="{y + 20}" class="hm-l">{lab}</text>')
        g.append(f'<rect x="{L}" y="{y + 28}" width="{X(v) - L:.1f}" height="26" rx="6" fill="{col}"/>')
        g.append(f'<text x="{X(v) + 8:.1f}" y="{y + 47}" class="hm-v">{v:.1f}</text>')
    for t in range(0, 7):
        g.append(f'<text x="{X(t):.1f}" y="{T + rowh * len(BARS) + 22}" text-anchor="middle" class="hm-ax">{t}</text>')
    return f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-label="Average difference from DXA by method in a study of 437 college students">' + "".join(g) + "</svg>"

ROWS = [
 ("DXA scan", "Clinic or research lab", "X-ray scan separating fat, lean tissue and bone", "Reference method in this comparison", "CDC calls it the most widely accepted method"),
 ("Underwater (hydrostatic) weighing", "University or sports lab", "Body density from your weight under water", "1.0 points", "Equivalent to DXA (&#177;10%)"),
 ("Bod Pod (air displacement)", "Lab, some gyms", "Body density from the air you displace", "1.6 points", "Equivalent to DXA (&#177;10%)"),
 ("Lab impedance analyzer, 4 electrodes", "Clinic or lab", "Electrical resistance through hand and foot electrodes", "1.6 points", "Equivalent to DXA (&#177;10%)"),
 ("Skinfold calipers, 7 sites", "Home or gym, trained measurer", "Pinch thickness at seven sites, converted to density", "1.4 points", "Equivalent; lowest individual error"),
 ("Smart scale, foot-to-foot", "Home", "Electrical resistance between the feet", "Not reported in text", "Not equivalent at &#177;10% (equivalent at &#177;15%)"),
 ("Hand-held impedance device", "Home", "Electrical resistance between the hands", "4.9 points", "Not equivalent; highest individual error"),
 ("Near-infrared device", "Gym", "Light reflected from the upper arm", "Not reported in text", "Not equivalent, even at &#177;15%"),
 ("Tape measure (Navy method)", "Home", "Neck, waist and hip circumferences", "Not in this study", "Wide individual differences in a smaller study"),
 ("BMI formula (Deurenberg)", "Home", "BMI, age and sex only", "Not in this study", "Standard error 4.1 points in its original study"),
]
def table():
    rows = "".join(f"<tr><th scope='row'>{a}</th><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in ROWS)
    return ("<div class='cmb-table-wrap'><table><caption>Body fat methods compared with DXA</caption><thead><tr><th scope='col'>Method</th><th scope='col'>Where</th><th scope='col'>What it measures</th><th scope='col'>Average difference from DXA*</th><th scope='col'>Verdict*</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")
CSS = """
.hm-fig{margin:16px auto;max-width:680px}.hm-fig svg{display:block;width:100%;height:auto}
.hm-l{font:700 20px system-ui,sans-serif;fill:#1F2937}.hm-v{font:800 20px system-ui,sans-serif;fill:#111827}.hm-ax{font:16px system-ui,sans-serif;fill:#6B7280}.hm-eq{font:700 16px system-ui,sans-serif;fill:#2E7D4F}
.hm-cards{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.hm-card{flex:1 1 260px;border-radius:14px;padding:14px 16px;background:#fff;border:1px solid #EEF0F3;border-left:6px solid var(--c);box-shadow:0 3px 12px rgba(17,24,39,.06)}
.hm-card h3{margin:0 0 6px;font-size:1.05rem}.hm-card p{margin:0;font-size:.95rem}
.hm-cta{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;border-radius:14px;padding:14px 16px;background:#1F2937;color:#fff;margin:18px 0}
.hm-cta p{margin:0;flex:1 1 260px}.hm-cta a{background:#C2481E;color:#fff;font-weight:800;border-radius:10px;padding:10px 16px;text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
"""
def P(*a): return "\n".join(a)
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <a href="/blog/" style="color:inherit;">Guides</a> &rsaquo; <span>How to Calculate Body Fat Percentage</span></nav>',
'<article class="cmb-stats">',
'<h1>How to Calculate Body Fat Percentage</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Every accuracy figure from published studies &middot; Reviewed October 7, 2026 &middot; Not medical advice</p>',
'<p class="cmb-intro">You can measure body fat in a lab or estimate it at home. The real question is how close each method gets to the truth, so this guide scores them against a DXA scan using a study that tested seven methods on the same 437 people.</p>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>To calculate your body fat percentage at home, use skinfold calipers, a tape measure (the Navy method) or a BMI-based formula; for a true measurement, get a DXA scan.</strong> In a study of 437 college students, underwater weighing, the Bod Pod, a lab impedance analyzer and 7-site skinfolds all landed within 1.0&ndash;1.6 points of DXA on average, while a hand-held impedance device was off by 4.9 points.</p>',
f'<p class="cmb-src">Source: <a href="{BURNS}" rel="noopener">Burns, Fu &amp; Constantino, PLOS ONE 2019</a>. Try the home methods in our <a href="/body-fat-calculator/">body fat calculator</a>.</p>',
'</div>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol><li><a href="#compare">Every method compared with DXA</a></li><li><a href="#lab">Lab methods</a></li><li><a href="#home">At-home methods</a></li><li><a href="#scales">How accurate are body fat scales?</a></li><li><a href="#tips">How to get a reliable reading</a></li><li><a href="#meaning">What your number means</a></li><li><a href="#faq">FAQ</a></li><li><a href="#sources">Sources</a></li></ol></nav>',
'<h2 id="compare">Every method compared with DXA</h2>',
f'<p><strong>Comparisons often mix different studies, people and reference methods; the numbers below come from one study where every method was tested on the same people against the same DXA scanner.</strong> The researchers set a strict test: a method counted as &ldquo;equivalent&rdquo; to DXA only if its average result stayed within 10% of the DXA average, which in this group meant &#177;{EQ} body fat points.</p>',
f'<figure class="hm-fig">{chart()}<figcaption>Average difference from a DXA scan, in body fat percentage points (scale 0&ndash;6), for the five methods whose figures the study reports in its text. Blue: lab methods; green and orange: home methods inside and outside the cut-off. Source: <a href="{BURNS}" rel="noopener">Burns et al., PLOS ONE 2019</a> (437 college students, mean age 19).</figcaption></figure>',
table(),
'<p class="cmb-src">* From Burns et al. 2019 unless noted. The foot-to-foot scale and near-infrared device were tested, but the study reports their averages only in a table image, so we give the verdict without a number. Tape and BMI rows: see the at-home section.</p>',
'<p>Two caveats matter. The volunteers were young, fit exercise-science students, so errors may be larger in older people or people with more body fat; the authors also found that <strong>every method&rsquo;s error grew as body fat went up</strong>. And an average difference of 1.5 points can still hide bigger misses for individuals: even the best home method, skinfolds, had an average individual error of 11.7% of the DXA value.</p>',
'<h2 id="lab">Lab methods</h2>',
'<div class="hm-cards">',
f'<div class="hm-card" style="--c:#1F4E79"><h3>DXA scan</h3><p>A low-dose X-ray scan that separates fat, lean tissue and bone. CDC calls it the most widely accepted method of measuring body composition and uses it in its national survey (<a href="{DXX}" rel="noopener">CDC</a>). Settings matter: CDC&rsquo;s survey setting adds 5% of lean mass to fat mass.</p></div>',
'<div class="hm-card" style="--c:#1F4E79"><h3>Underwater weighing</h3><p>You exhale fully while seated under water; your underwater weight gives body density, which an equation converts to body fat. Closest to DXA in the study (1.0 point), but slow and demanding.</p></div>',
'<div class="hm-card" style="--c:#1F4E79"><h3>Bod Pod</h3><p>You sit in a sealed egg-shaped chamber that measures the air you displace, giving body density. 1.6 points from DXA on average in the study, and far less demanding than going under water.</p></div>',
'</div>',
'<h2 id="home">At-home methods</h2>',
'<div class="hm-cards">',
'<div class="hm-card" style="--c:#2E7D4F"><h3>Skinfold calipers</h3><p>The best home method in the study: 1.4 points from DXA on average with 7 sites, measured by trained students. A 3-site version is quicker; our <a href="/body-fat-calculator/">calculator</a> uses the Jackson&ndash;Pollock 3-site equations. The catch is skill: results depend on the person pinching.</p></div>',
f'<div class="hm-card" style="--c:#2E7D4F"><h3>Tape measure (Navy method)</h3><p>Neck and waist (plus hips for women) and your height. Easy to do, but not tested in the DXA study above. In a smaller study of 69 active young adults, the 95% limits of agreement between the military tape method and underwater weighing, impedance and skinfolds were wider than &#177;3.5 points, so individual results could differ by more than that either way (<a href="{DOD}" rel="noopener">conference abstract</a>).</p></div>',
f'<div class="hm-card" style="--c:#C2481E"><h3>BMI formula</h3><p>Deurenberg&rsquo;s formula needs only BMI, age and sex. Its standard error is 4.1 points, and it slightly overestimates body fat in people with obesity (<a href="{DEUR}" rel="noopener">Deurenberg et al., 1991</a>). Fine as a first rough guess.</p></div>',
'</div>',
'<div class="hm-cta"><p><strong>Run the home methods side by side.</strong> Our calculator does tape, calipers and the BMI formula, shows how far apart they land, and ranks the result against CDC body scans.</p><a href="/body-fat-calculator/">Body fat calculator</a></div>',
'<h2 id="scales">How accurate are body fat scales?</h2>',
'<p><strong>Less accurate than skinfolds or lab methods, according to this study.</strong> Bathroom scales and hand-held devices send a small electrical current through your body and estimate fat from the resistance; the foot-to-foot scale and the hand-held device both missed the &plusmn;10% cut-off, and the hand-held device was off by 4.9 points on average, with the largest individual error of all methods (21.9%). The lab analyzer that uses four electrodes on a hand and foot did much better (1.6 points). Hydration also moves impedance readings: the authors note that dehydration can push estimated body fat up and overhydration can push it down.</p>',
'<p>A scale is still useful for trends if you weigh in under the same conditions every time. Just don&rsquo;t compare its number with a reading from a different method or device.</p>',
'<h2 id="tips">How to get a reliable reading</h2>',
'<p>The study used a simple pre-test routine that you can copy for any method: no large meal in the 2 hours before, no vigorous exercise in the 12 hours before, no alcohol in the 48 hours before, no more than two glasses of water, finished at least 2 hours before, and an empty bladder. For skinfolds, each site was measured twice, with a third measurement if the first two differed by more than 2 mm.</p>',
'<p>Beyond that: use the same method, the same device and the same time of day; take each measurement more than once; and judge changes over weeks, not day to day.</p>',
'<h2 id="meaning">What your number means</h2>',
'<p>Once you have a number, compare it with what US adults your age actually measure on CDC&rsquo;s DXA scans, and with the provisional healthy ranges for your age, on our <a href="/body-fat-percentage-chart/">body fat percentage chart</a>. For why BMI and body fat can disagree, see <a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a>.</p>',
'<h2 id="faq">FAQ</h2>',
'<details class="cmb-faq"><summary><h3>How do I calculate my body fat percentage at home?</h3></summary><p>Use skinfold calipers (most accurate at home if you&rsquo;re practiced), a tape measure with the Navy equations, or the Deurenberg BMI formula. Our <a href="/body-fat-calculator/">body fat calculator</a> runs all three.</p></details>',
'<details class="cmb-faq"><summary><h3>What is the most accurate way to measure body fat?</h3></summary><p>A DXA scan is the most widely accepted method. In a study using DXA as the reference, underwater weighing (1.0 point), skinfolds (1.4), the Bod Pod (1.6) and a 4-electrode lab analyzer (1.6) came closest.</p></details>',
'<details class="cmb-faq"><summary><h3>How accurate are body fat scales?</h3></summary><p>In that study, a foot-to-foot scale and a hand-held device were not equivalent to DXA; the hand-held device was off by 4.9 points on average. Use a scale for trends under identical conditions rather than as an exact number.</p></details>',
'<details class="cmb-faq"><summary><h3>Why do different methods give different numbers?</h3></summary><p>They measure different things (density, electrical resistance, skinfold thickness, circumferences) and convert them with different equations, so readings can differ by several points. Errors also grow at higher body fat.</p></details>',
'<details class="cmb-faq"><summary><h3>How much body fat should I have?</h3></summary><p>Provisional healthy ranges matched to BMI are 8&ndash;19.9% for men and 21&ndash;32.9% for women aged 20&ndash;39, a little higher at older ages. See the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>.</p></details>',
'<h2 id="sources">Sources</h2>',
'<ol class="cmb-sources">',
f'<li>Burns RD, Fu Y, Constantino N. <a href="{BURNS}" rel="noopener">Measurement agreement in percent body fat estimates among laboratory and field assessments in college students: use of equivalence testing</a>. PLOS ONE 2019;14(3):e0214029.</li>',
f'<li>Deurenberg P, Weststrate JA, Seidell JC. <a href="{DEUR}" rel="noopener">Body mass index as a measure of body fatness: age- and sex-specific prediction formulas</a>. Br J Nutr 1991;65:105&ndash;14.</li>',
f'<li>National Center for Health Statistics. <a href="{DXX}" rel="noopener">NHANES Dual-Energy X-ray Absorptiometry, Whole Body (documentation)</a>.</li>',
f'<li><a href="{DOD}" rel="noopener">A comparison of multiple body composition measurement methods to the Department of Defense&rsquo;s Physical Fitness and Body Fat Program procedures</a>. International Journal of Exercise Science: Conference Proceedings 14(1), abstract 40.</li>',
'</ol>',
'<p class="cmb-note">This guide is for information and is not medical advice.</p>',
'<h2>Related</h2><ul><li><a href="/body-fat-calculator/">Body fat calculator</a></li><li><a href="/body-fat-percentage-chart/">Body fat percentage chart by age</a></li><li><a href="/blog/body-fat-vs-bmi/">Body fat vs BMI</a></li><li><a href="/lean-body-mass/">Lean body mass calculator</a></li></ul>',
'</article>')

TITLE = "How to Calculate Body Fat Percentage: Every Method Compared"
DESC = "How to calculate body fat percentage at home or in a lab, and how accurate each method is: skinfolds, tape, smart scales, Bod Pod, DXA, compared in one study."
OG = "https://calculatemybmi.net/blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png"
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "How to Calculate Body Fat Percentage", "description": DESC,
  "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}, "datePublished": "2026-10-07", "dateModified": "2026-10-07",
  "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "citation": [BURNS, DEUR, DXX, DOD]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"}, {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://calculatemybmi.net/blog/"}, {"@type": "ListItem", "position": 3, "name": "How to Calculate Body Fat Percentage", "item": URL}]},
 org, person]}
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="How to calculate body fat percentage: every method compared">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'),
                 (r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="Body fat measurement methods compared with DXA scans.">'),
                 (r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG}">')]:
    head = re.sub(pat, rep, head, flags=re.S)
rest = shell[shell.find("</script>", shell.find('<script type="application/ld+json">')) + 9:]
page = (head + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, indent=1) + "</script>" + rest[:rest.find("</head>")] + "<style>" + CSS + "</style>"
        + rest[rest.find("</head>"):rest.find("<main>")] + '<main><div class="container" style="max-width:1000px;margin:0 auto;padding:2rem 1rem 3rem;">' + content + "</div>" + rest[rest.find("</main>"):])
os.makedirs(os.path.join(OUT, SLUG), exist_ok=True)
open(os.path.join(OUT, SLUG, "index.html"), "w", encoding="utf-8").write(page)
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1200, 630), "#FFFFFF"); dr = ImageDraw.Draw(im)
def font(sz, b=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()
dr.rectangle([0, 0, 1200, 12], fill="#2E7D4F")
dr.text((56, 50), "How to calculate body fat", font=font(58, True), fill="#111827")
dr.text((56, 126), "Every method compared with a DXA scan", font=font(32), fill="#4B5563")
for i, (lab, v, kind) in enumerate(BARS):
    y = 200 + i * 66; w = int(v / 6 * 620); col = "#1F4E79" if kind == "lab" else ("#2E7D4F" if v <= EQ else "#C2481E")
    dr.text((56, y + 8), lab.replace("Lab impedance analyzer, 4 electrodes", "Lab impedance (4 electrodes)"), font=font(24, True), fill="#1F2937")
    dr.rounded_rectangle([560, y, 560 + w, y + 44], radius=10, fill=col); dr.text((570 + w, y + 6), f"{v:.1f}", font=font(28, True), fill="#111827")
dr.text((56, 560), "calculatemybmi.net · Burns et al., PLOS ONE 2019", font=font(24, True), fill="#6B7280")
im.save(os.path.join(OUT, SLUG, "og-how-to-measure-body-fat.png"), optimize=True)
print(json.dumps({"title_len": len(TITLE), "desc_len": len(DESC)}))
