#!/usr/bin/env python3
"""Rebuild /blog/bmi-for-athletes/ (calculatemybmi.net). Sources: Provencher et al., J Strength Cond Res 2018 (NFL Combine:
53.4% BMI >= 30 vs 8.9% obesity by measured body fat, air displacement plethysmography) — as already cited on the page;
Clin J Sport Med 2012;22(5):436-8 (PubMed 22805182; 156 Division I-A football players vs matched non-athletes, DXA:
BMI 25 = 11.1% vs 19.9% fat, BMI 30 = 20.2% vs 27.3%; linemen highest weight, BMI, fat-free mass and %fat);
our NHANES 2011-2018 DXA percentiles by BMI category; CDC adult BMI categories; Burns et al. PLOS ONE 2019 (via our guide)."""
import json, os, re, sys, html as H
ROOT, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__)); BF = json.load(open(os.path.join(HERE, "bf_results.json")))
SLUG = "blog/bmi-for-athletes"; URL = f"https://calculatemybmi.net/{SLUG}/"
PROV = "https://doi.org/10.1519/JSC.0000000000002449"; CJSM = "https://pubmed.ncbi.nlm.nih.gov/22805182/"; CDC = "https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
ow = BF["m"]["by_bmi"]["25–29.9"]["q"]; ob = BF["m"]["by_bmi"]["30+"]["q"]; hw = BF["m"]["by_bmi"]["18.5–24.9"]["q"]
def chart():
    W, H_, L, T = 640, 300, 12, 46; groups = [("At a BMI of 25", 19.9, 11.1), ("At a BMI of 30", 27.3, 20.2)]; mx = 40.0
    X = lambda v: L + v / mx * (W - L - 70); g = []
    for i, (lab, cg, fb) in enumerate(groups):
        y = T + i * 118
        g.append(f'<text x="{L}" y="{y}" class="at-h">{lab}</text>')
        for j, (who, v, col) in enumerate((("Non-athletes", cg, "#6B7280"), ("College football players", fb, "#1F4E79"))):
            yy = y + 14 + j * 46
            g.append(f'<text x="{L}" y="{yy + 15}" class="at-l">{who}</text>')
            g.append(f'<rect x="{L}" y="{yy + 21}" width="{X(v) - L:.1f}" height="18" rx="5" fill="{col}"/><text x="{X(v) + 8:.1f}" y="{yy + 35}" class="at-v">{v:.1f}% body fat</text>')
    return f'<svg viewBox="0 0 {W} {H_}" width="{W}" height="{H_}" role="img" aria-label="Body fat that matches a BMI of 25 and 30 in college football players versus non-athletes">' + "".join(g) + "</svg>"
CSS = """.at-fig{margin:16px auto;max-width:640px}.at-fig svg{display:block;width:100%;height:auto}
.at-h{font:800 20px system-ui,sans-serif;fill:#111827}.at-l{font:600 17px system-ui,sans-serif;fill:#374151}.at-v{font:800 17px system-ui,sans-serif;fill:#111827}
.at-cards{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}.at-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:150px;background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06)}
.at-kpi b{display:block;font-size:1.9rem;line-height:1.1;color:#111827}.at-kpi span{font-size:.9rem;color:#374151}
@media (min-width:760px){.at-kpi{flex:1 1 calc(25% - 10px)}}"""
def P(*a): return "\n".join(a)
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <a href="/blog/" style="color:inherit;">Guides</a> &rsaquo; <span>BMI for Athletes</span></nav>',
'<article class="cmb-stats">','<h1>BMI for Athletes</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Sources: peer-reviewed studies and CDC data &middot; Updated October 7, 2026 &middot; Not medical advice</p>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>BMI can&rsquo;t tell muscle from fat, so muscular athletes often land in the overweight or obese range while carrying little fat.</strong> At the NFL Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity when their body fat was measured. If you train hard and carry a lot of muscle, judge yourself by body fat or waist size, not BMI.</p>',
f'<p class="cmb-src">Source: <a href="{PROV}" rel="noopener">Provencher et al., J Strength Cond Res 2018</a>.</p>','</div>',
'<div class="at-cards"><div class="at-kpi" style="--c:#B3431A"><b>53.4%</b><span>of NFL prospects had a BMI of 30+</span></div><div class="at-kpi" style="--c:#2E7D4F"><b>8.9%</b><span>had obesity by measured body fat</span></div>'
f'<div class="at-kpi" style="--c:#1F4E79"><b>20.2%</b><span>body fat at BMI 30 in college football players (27.3% in non-athletes)</span></div><div class="at-kpi" style="--c:#6B46C1"><b>{ow[0]:.1f}%</b><span>body fat or less: leanest tenth of US men with BMI 25&ndash;29.9</span></div></div>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol><li><a href="#why">Why BMI misjudges athletes</a></li><li><a href="#evidence">What the studies show</a></li><li><a href="#everyone">It isn&rsquo;t only elite athletes</a></li><li><a href="#better">Better measures for athletes</a></li><li><a href="#faq">FAQ</a></li><li><a href="#sources">Sources</a></li></ol></nav>',
'<h2 id="why">Why BMI misjudges athletes</h2>',
f'<p>BMI is just weight divided by height squared. It counts every kilogram the same, whether it&rsquo;s muscle, bone or fat. Muscle is dense, so an athlete who adds muscle adds weight, and BMI climbs even as body fat stays low or falls. The adult categories are the same for everyone (<a href="{CDC}" rel="noopener">CDC</a>): there&rsquo;s no separate &ldquo;athlete BMI&rdquo;, which is exactly why it misfires for this group. See <a href="/blog/what-is-bmi/">what is BMI</a> for the basics.</p>',
'<h2 id="evidence">What the studies show</h2>',
f'<p><strong>NFL prospects.</strong> Provencher and colleagues compared BMI with body fat measured by air displacement (Bod Pod) at the NFL Scouting Combine. BMI put 53.4% of prospects in the obesity range; measured body fat put 8.9% there (<a href="{PROV}" rel="noopener">J Strength Cond Res 2018</a>).</p>',
f'<p><strong>College football.</strong> A DXA study of 156 Division I-A football players and matched non-athletes asked what body fat each BMI cut-off corresponds to. In the players, a BMI of 25 matched about 11.1% body fat and a BMI of 30 about 20.2%; in the non-athletes, the same cut-offs matched 19.9% and 27.3%. The players had more weight, BMI and fat-free mass but less fat. One nuance: linemen had the highest BMI and also the highest body fat, so a very high BMI can still reflect real fat, even in athletes (<a href="{CJSM}" rel="noopener">Clin J Sport Med 2012</a>).</p>',
f'<figure class="at-fig">{chart()}<figcaption>Body fat that corresponds to the BMI 25 and BMI 30 cut-offs, college football players vs matched non-athletes (DXA). Source: <a href="{CJSM}" rel="noopener">Clin J Sport Med 2012;22:436&ndash;8</a>.</figcaption></figure>',
'<h2 id="everyone">It isn&rsquo;t only elite athletes</h2>',
f'<p>The same overlap shows up in the general population. In CDC&rsquo;s body scans of US men aged 20&ndash;59, those with an &ldquo;overweight&rdquo; BMI of 25&ndash;29.9 had a median of {ow[2]:.1f}% body fat, but the leanest tenth were under {ow[0]:.1f}%, leaner than many men with a healthy BMI, whose median was {hw[2]:.1f}% (our calculation from NHANES 2011&ndash;2018). Anyone who lifts regularly can be in that lean tenth. The <a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows the full spread by age.</p>',
'<h2 id="better">Better measures for athletes</h2>',
'<p><strong>Body fat percentage</strong> is the direct answer to the question BMI can&rsquo;t answer. In a study that tested seven methods against DXA, skinfold calipers came within 1.4 points on average, and lab methods such as the Bod Pod within 1.6 (<a href="/blog/how-to-measure-body-fat/">how to measure body fat</a>). You can estimate yours with a tape measure, calipers or the BMI formula in our <a href="/body-fat-calculator/">body fat calculator</a>, which also ranks the result against US adults.</p>',
'<p><strong>Waist size</strong> captures the fat that matters most for health and isn&rsquo;t fooled by muscle in the legs, back or shoulders; see <a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>. <strong>Lean body mass</strong> tells you how much of your weight is not fat: try the <a href="/lean-body-mass/">lean body mass calculator</a>.</p>',
'<h2 id="faq">FAQ</h2>',
'<details class="cmb-faq"><summary><h3>Is BMI accurate for athletes?</h3></summary><p>Often not. It can&rsquo;t tell muscle from fat, so muscular athletes are frequently classed as overweight or obese with low body fat; at the NFL Combine, 53.4% had a BMI of 30+, but 8.9% had obesity by measured body fat.</p></details>',
'<details class="cmb-faq"><summary><h3>Is there a different BMI chart for athletes?</h3></summary><p>No. CDC&rsquo;s adult categories apply to everyone. For athletes, body fat percentage and waist size are better guides than adjusting BMI.</p></details>',
'<details class="cmb-faq"><summary><h3>Why do bodybuilders have a high BMI?</h3></summary><p>Because muscle adds weight. BMI only sees weight and height, so extra muscle raises it exactly as extra fat would.</p></details>',
'<details class="cmb-faq"><summary><h3>Can an athlete with a high BMI still have too much fat?</h3></summary><p>Yes. In the college football study, linemen had both the highest BMI and the highest body fat. Measure body fat or waist size to know which it is.</p></details>',
'<h2 id="sources">Sources</h2><ol class="cmb-sources">',
f'<li>Provencher MT, et al. <a href="{PROV}" rel="noopener">Body mass index versus body fat percentage in prospective National Football League athletes: overestimation of obesity rate in athletes at the NFL Scouting Combine</a>. J Strength Cond Res 2018.</li>',
f'<li><a href="{CJSM}" rel="noopener">DEXA or BMI: clinical considerations for evaluating obesity in collegiate division I-A American football athletes</a>. Clin J Sport Med 2012;22(5):436&ndash;8.</li>',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC}" rel="noopener">Adult BMI Categories</a>.</li>',
'<li>National Center for Health Statistics. NHANES 2011&ndash;2018 DXA body scans (percentiles: our calculation; see <a href="/body-fat-percentage-chart/">body fat percentage chart</a>).</li>','</ol>',
'<p class="cmb-note">This guide is for information and is not medical advice.</p>','</article>')
TITLE = "BMI for Athletes: Why BMI Misjudges Muscle (and What to Use)"
DESC = "Why BMI misclassifies muscular athletes: 53.4% of NFL prospects had a BMI of 30+, but 8.9% had obesity by body fat. Better measures and what the studies show."
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "BMI for Athletes", "description": DESC, "datePublished": "2026-02-01", "dateModified": "2026-10-07",
  "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"}, "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "citation": [PROV, CJSM, CDC]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"}, {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://calculatemybmi.net/blog/"}, {"@type": "ListItem", "position": 3, "name": "BMI for Athletes", "item": URL}]}, org, person]}
old = open(os.path.join(ROOT, SLUG, "index.html"), encoding="utf-8").read()
OG = "https://calculatemybmi.net/blog/bmi-for-athletes/og-bmi-for-athletes.png"
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="BMI for athletes: why BMI misjudges muscle">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'), (r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="BMI versus body fat in athletes.">'),
                 (r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG}">')]:
    head = re.sub(pat, rep, head, flags=re.S)
rest = shell[shell.find("</script>", shell.find('<script type="application/ld+json">')) + 9:]
page = (head + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, indent=1) + "</script>" + rest[:rest.find("</head>")] + "<style>" + CSS + "</style>"
        + rest[rest.find("</head>"):rest.find("<main>")] + '<main><div class="container" style="max-width:1000px;margin:0 auto;padding:2rem 1rem 3rem;">' + content + "</div>" + rest[rest.find("</main>"):])
open(os.path.join(OUT, SLUG, "index.html"), "w", encoding="utf-8").write(page)
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1200, 630), "#FFFFFF"); dr = ImageDraw.Draw(im)
def font(sz, b=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()
dr.rectangle([0, 0, 1200, 12], fill="#1F4E79")
dr.text((56, 50), "BMI for athletes", font=font(64, True), fill="#111827")
dr.text((56, 135), "NFL Scouting Combine prospects", font=font(32), fill="#4B5563")
dr.rounded_rectangle([56, 210, 56 + int(53.4 * 11), 290], radius=14, fill="#B3431A"); dr.text((76, 228), "53.4%  BMI 30+", font=font(38, True), fill="#FFFFFF")
dr.rounded_rectangle([56, 320, 56 + int(8.9 * 11) + 40, 400], radius=14, fill="#2E7D4F"); dr.text((56 + int(8.9 * 11) + 60, 338), "8.9%  obesity by measured body fat", font=font(38, True), fill="#1F2937")
dr.text((56, 470), "Provencher et al., J Strength Cond Res 2018", font=font(28), fill="#374151")
dr.text((56, 560), "calculatemybmi.net", font=font(28, True), fill="#6B7280")
im.save(os.path.join(OUT, SLUG, "og-bmi-for-athletes.png"), optimize=True)
print(json.dumps({"title_len": len(TITLE), "desc_len": len(DESC), "og": OG, "ow_p10": ow[0], "ow_med": ow[2], "hw_med": hw[2]}))
