#!/usr/bin/env python3
"""Rebuild /blog/what-is-bmi/ (calculatemybmi.net). Sources (all verified in the registry or in chat):
CDC adult BMI categories; NHLBI 1998 guidelines (BMI = kg/m^2); CDC child & teen categories; NCHS Data Brief 508 (40.3% obesity,
9.4% severe, adults 20+, 2021-2023); NHANES 2021-2023 averages (men 29.4, women 30.0 — Series 3 No. 50, reproduced by us);
WHO expert consultation, Lancet 2004 (Asian public-health action points 23 / 27.5); Volpi et al. 2004 (muscle loss 3-8%/decade after 30);
our NHANES 2011-2018 DXA percentiles by BMI category; Deurenberg 1991 (SEE 4.1)."""
import json, os, re, sys, html as H
from decimal import Decimal, ROUND_HALF_UP
ROOT, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
BF = json.load(open(os.path.join(HERE, "bf_results.json")))
AWCSS = open(os.path.join(HERE, "aw_css.txt"), encoding="utf-8").read()
SLUG = "blog/what-is-bmi"; URL = f"https://calculatemybmi.net/{SLUG}/"
CDC_ADULT = "https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
CDC_CHILD = "https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html"
NHLBI = "https://www.ncbi.nlm.nih.gov/books/NBK2003/"
DB508 = "https://www.cdc.gov/nchs/products/databriefs/db508.htm"
SER3 = "https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf"
WHO04 = "https://pubmed.ncbi.nlm.nih.gov/14726171/"
VOLPI = "https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/"
DEUR = "https://pubmed.ncbi.nlm.nih.gov/2043597/"
def bmi_r(lb, hin): return float(Decimal(lb * 703 / hin ** 2).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
def bmi_m(kg, m): return float(Decimal(kg / m ** 2).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
def band(hin, lo, hi):
    ok = [lb for lb in range(50, 500) if lo <= bmi_r(lb, hin) <= hi]; return ok[0], ok[-1]
assert bmi_r(170, 69) == 25.1 and bmi_m(70, 1.75) == 22.9 and band(69, 18.5, 24.9) == (125, 168)
mq, fq = BF["m"]["by_bmi"]["18.5–24.9"]["q"], BF["f"]["by_bmi"]["18.5–24.9"]["q"]
mo = BF["m"]["by_bmi"]["30+"]["q"]
EX_H, EX_W = 69, 170; EX_B = bmi_r(EX_W, EX_H); EX_HB = band(EX_H, 18.5, 24.9); EX_OB = band(EX_H, 25, 29.9)

TOOL = (
'<section class="aw-tool" aria-label="BMI explorer">'
'<div class="aw-tool-head"><h2>See how BMI works</h2><p>Move the sliders: your BMI, its category and the weight range for each category at your height update instantly.</p></div>'
'<div class="aw-form">'
'<div class="aw-field"><span class="aw-flabel" id="wb-u-l">Units</span><div class="aw-pills" role="radiogroup" aria-labelledby="wb-u-l"><input type="radio" id="wb-u-imp" name="wb-u" value="imp" checked><label for="wb-u-imp">ft &middot; lb</label><input type="radio" id="wb-u-met" name="wb-u" value="met"><label for="wb-u-met">cm &middot; kg</label></div></div>'
'<div class="aw-field aw-field-wide"><label class="aw-flabel" for="wb-h">Height</label><div class="aw-height"><button type="button" class="aw-step" id="wb-h-minus" aria-label="Shorter">&minus;</button><output id="wb-h-out" for="wb-h">5&prime; 9&Prime;</output><button type="button" class="aw-step" id="wb-h-plus" aria-label="Taller">+</button></div><input type="range" id="wb-h" min="54" max="80" step="1" value="69" aria-valuetext="5 feet 9 inches" style="--p:57.7%"></div>'
'<div class="aw-field aw-field-wide"><label class="aw-flabel" for="wb-w">Weight</label><div class="aw-height"><button type="button" class="aw-step" id="wb-w-minus" aria-label="Lighter">&minus;</button><output id="wb-w-out" for="wb-w">170 lb</output><button type="button" class="aw-step" id="wb-w-plus" aria-label="Heavier">+</button></div><input type="range" id="wb-w" min="80" max="400" step="1" value="170" aria-valuetext="170 pounds" style="--p:28.1%"></div>'
'</div>'
f'<div id="wb-out" class="aw-out" aria-live="polite"><div class="wb-res"><div><span class="wb-l">BMI</span><span class="wb-n" id="wb-bmi">{EX_B}</span></div><span class="wb-chip" id="wb-cat" style="--c:#E5743F">Overweight</span></div>'
'<div class="aw-g"><div class="aw-g-tr" id="wb-track"><span style="left:0%;width:12.96%;background:#93C5FD"></span><span style="left:12.96%;width:24.07%;background:#86EFAC"></span><span style="left:37.04%;width:18.52%;background:#FDBA74"></span><span style="left:55.56%;width:44.44%;background:#FCA5A5"></span>'
f'<i id="wb-ptr" style="left:{(EX_B - 15) / 27 * 100:.2f}%"><b id="wb-ptr-b">{EX_B}</b></i></div><div class="aw-g-nm"><span style="left:6.48%">Under</span><span style="left:25%">Healthy</span><span style="left:46.3%">Over</span><span style="left:77.78%">Obesity</span></div><div class="aw-g-ax"><span style="left:12.96%">18.5</span><span style="left:37.04%">25</span><span style="left:55.56%">30</span></div></div>'
f'<div class="wb-bands" id="wb-bands"><p><strong>At 5&prime;9&Prime;:</strong> healthy weight is <strong>{EX_HB[0]} lb&ndash;{EX_HB[1]} lb</strong>.</p><ul class="wb-ul"><li><span style="--c:#60A5FA"></span>Underweight: under {EX_HB[0]} lb</li><li><span style="--c:#2E7D4F"></span>Healthy: {EX_HB[0]} lb&ndash;{EX_HB[1]} lb</li><li><span style="--c:#E5743F"></span>Overweight: {EX_OB[0]} lb&ndash;{EX_OB[1]} lb</li><li><span style="--c:#B3431A"></span>Obesity: {EX_OB[1] + 1} lb and over</li></ul></div>'
'<p class="cmb-src">Categories: <a href="' + CDC_ADULT + '" rel="noopener">CDC adult BMI categories</a>. For adults 20+; children and teens use BMI-for-age percentiles. Want the full calculator? <a href="/">BMI calculator</a>.</p></div>'
'</section>')

JS = r"""
(function(){var $=function(i){return document.getElementById(i);},hs=$('wb-h'),ws=$('wb-w');
function met(){return document.querySelector('input[name="wb-u"]:checked').value==='met';}
function r1(x){return Math.round(x*10+1e-9)/10;}
function hIn(){return met()?(+hs.value)/2.54:+hs.value;} function wLb(){return met()?(+ws.value)/0.45359237:+ws.value;}
function bmi(lb,h){return r1(lb*703/(h*h));}
function band(h,lo,hi){var a=null,b=null;for(var lb=50;lb<500;lb++){var x=bmi(lb,h);if(x>=lo&&x<=hi){if(a===null)a=lb;b=lb;}}return [a,b];}
function cat(b){return b<18.5?['Underweight','#60A5FA']:b<25?['Healthy weight','#2E7D4F']:b<30?['Overweight','#E5743F']:['Obesity','#B3431A'];}
function ft(h){var t=Math.round(h);return Math.floor(t/12)+'′ '+(t%12)+'″';}
function fmtW(lb){return met()?(lb*0.45359237).toFixed(0)+' kg':Math.round(lb)+' lb';}
function upd(){var h=hIn(),w=wLb(),b=bmi(w,h),c=cat(b);
 $('wb-h-out').textContent=met()?hs.value+' cm':ft(+hs.value);$('wb-w-out').textContent=met()?ws.value+' kg':ws.value+' lb';
 hs.style.setProperty('--p',((hs.value-hs.min)/(hs.max-hs.min)*100).toFixed(1)+'%');ws.style.setProperty('--p',((ws.value-ws.min)/(ws.max-ws.min)*100).toFixed(1)+'%');
 $('wb-bmi').textContent=b.toFixed(1);var ch=$('wb-cat');ch.textContent=c[0];ch.style.setProperty('--c',c[1]);
 var p=Math.min(Math.max((b-15)/27*100,0),100);$('wb-ptr').style.left=p.toFixed(2)+'%';$('wb-ptr-b').textContent=b.toFixed(1);
 var u=band(h,0,18.4),hb=band(h,18.5,24.9),o=band(h,25,29.9),hh=met()?hs.value+' cm':ft(h);
 $('wb-bands').innerHTML='<p><strong>At '+hh+':</strong> healthy weight is <strong>'+fmtW(hb[0])+'–'+fmtW(hb[1])+'</strong>.</p><ul class="wb-ul"><li><span style="--c:#60A5FA"></span>Underweight: under '+fmtW(hb[0])+'</li><li><span style="--c:#2E7D4F"></span>Healthy: '+fmtW(hb[0])+'–'+fmtW(hb[1])+'</li><li><span style="--c:#E5743F"></span>Overweight: '+fmtW(o[0])+'–'+fmtW(o[1])+'</li><li><span style="--c:#B3431A"></span>Obesity: '+fmtW(o[1]+1)+' and over</li></ul>';}
hs.addEventListener('input',upd);ws.addEventListener('input',upd);
$('wb-h-minus').addEventListener('click',function(){hs.value=+hs.value-1;upd();});$('wb-h-plus').addEventListener('click',function(){hs.value=+hs.value+1;upd();});
$('wb-w-minus').addEventListener('click',function(){ws.value=+ws.value-1;upd();});$('wb-w-plus').addEventListener('click',function(){ws.value=+ws.value+1;upd();});
var prev='imp';document.querySelectorAll('input[name="wb-u"]').forEach(function(r){r.addEventListener('change',function(){var m=met();if((m?'met':'imp')===prev)return;
 var h=prev==='imp'?+hs.value:(+hs.value)/2.54,w=prev==='imp'?+ws.value:(+ws.value)/0.45359237;
 if(m){hs.min=137;hs.max=203;ws.min=36;ws.max=182;hs.value=Math.round(h*2.54);ws.value=Math.round(w*0.45359237);}else{hs.min=54;hs.max=80;ws.min=80;ws.max=400;hs.value=Math.round(h);ws.value=Math.round(w);}prev=m?'met':'imp';upd();});});
upd();})();
"""
CSS = (AWCSS.replace("#aw-h-out{", "#aw-h-out,#wb-h-out,#wb-w-out{").replace("#aw-h{", "#aw-h,#wb-h,#wb-w{").replace("#aw-h::-webkit-slider-thumb{", "#aw-h::-webkit-slider-thumb,#wb-h::-webkit-slider-thumb,#wb-w::-webkit-slider-thumb{").replace("#aw-h::-moz-range-thumb{", "#aw-h::-moz-range-thumb,#wb-h::-moz-range-thumb,#wb-w::-moz-range-thumb{") + """
.aw-out{display:block}
.wb-res{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:14px 0 4px}
.wb-l{display:block;font-size:.78rem;font-weight:800;letter-spacing:.06em;color:#6B7280}
.wb-n{font-size:2.8rem;font-weight:800;line-height:1;color:#111827;font-variant-numeric:tabular-nums}
.wb-chip{border-radius:999px;padding:8px 14px;font-weight:800;color:#fff;background:var(--c)}
.wb-bands{margin:14px 0 6px}
.wb-ul{list-style:none;padding:0;margin:6px 0 0;display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.92rem}
.wb-ul li{display:flex;align-items:center;gap:8px}.wb-ul span{display:inline-block;width:12px;height:12px;border-radius:3px;background:var(--c)}
.wb-f{background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;padding:12px 14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.95rem;overflow-x:auto}
.wb-links{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.wb-links a{border:1px solid #E5E7EB;border-radius:999px;padding:6px 12px;text-decoration:none;font-weight:700;font-size:.9rem;background:#fff}
""")
def P(*a): return "\n".join(a)
rows = "".join(f"<tr><th scope='row'>{a}</th><td>{b}</td></tr>" for a, b in [("Under 18.5", "Underweight"), ("18.5 to under 25", "Healthy weight"), ("25 to under 30", "Overweight"), ("30 to under 35", "Obesity, class 1"), ("35 to under 40", "Obesity, class 2"), ("40 or higher", "Obesity, class 3 (severe obesity)")])
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <a href="/blog/" style="color:inherit;">Guides</a> &rsaquo; <span>What Is BMI?</span></nav>',
'<article class="cmb-stats">',
'<h1>What Is BMI?</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Sources: CDC, NIH, WHO and peer-reviewed studies &middot; Updated October 7, 2026 &middot; Not medical advice</p>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>BMI (body mass index) is your weight in kilograms divided by your height in meters squared.</strong> For adults, CDC classes a BMI under 18.5 as underweight, 18.5 to under 25 as healthy weight, 25 to under 30 as overweight and 30 or more as obesity. It&rsquo;s a quick screening number, not a diagnosis: it can&rsquo;t tell fat from muscle or show where fat sits.</p>',
f'<p class="cmb-src">Sources: <a href="{CDC_ADULT}" rel="noopener">CDC adult BMI categories</a>; <a href="{NHLBI}" rel="noopener">NIH (NHLBI) clinical guidelines</a>.</p>',
'</div>',
TOOL,
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol><li><a href="#formula">How BMI is calculated</a></li><li><a href="#categories">BMI categories for adults</a></li><li><a href="#children">BMI for children and teens</a></li><li><a href="#us">What&rsquo;s a typical BMI in the US?</a></li><li><a href="#limits">What BMI can&rsquo;t tell you</a></li><li><a href="#doctors">How doctors use BMI</a></li><li><a href="#body-fat">BMI and body fat</a></li><li><a href="#faq">FAQ</a></li><li><a href="#sources">Sources</a></li></ol></nav>',
'<h2 id="formula">How BMI is calculated</h2>',
'<p>BMI uses two numbers: weight and height. The metric formula is the definition; the imperial version multiplies by 703 to convert pounds and inches.</p>',
'<p class="wb-f">BMI = weight (kg) &divide; height (m)&sup2;<br>BMI = weight (lb) &times; 703 &divide; height (in)&sup2;</p>',
f'<p><strong>Examples:</strong> 70 kg at 1.75 m gives 70 &divide; 1.75&sup2; = {bmi_m(70, 1.75)}. A 5&prime;9&Prime; (69-inch) adult weighing 170 lb has 170 &times; 703 &divide; 69&sup2; = {EX_B}, just inside the overweight range. More detail, including where the 703 comes from, is in <a href="/blog/bmi-formula/">the BMI formula</a>.</p>',
'<h2 id="categories">BMI categories for adults</h2>',
'<div class="cmb-table-wrap"><table><caption>Adult BMI categories (CDC)</caption><thead><tr><th scope="col">BMI</th><th scope="col">Category</th></tr></thead>' + f'<tbody>{rows}</tbody></table></div>',
f'<p>These cut-offs apply to adults 20 and older, regardless of sex or age (<a href="{CDC_ADULT}" rel="noopener">CDC</a>). They&rsquo;re population cut-offs, and risk doesn&rsquo;t jump at an exact number. For Asian populations, a WHO expert consultation identified lower public-health action points, at BMI 23 and 27.5 (<a href="{WHO04}" rel="noopener">WHO expert consultation, Lancet 2004</a>). Each category is covered in depth in <a href="/blog/bmi-categories/">BMI categories explained</a>, and the healthy range in <a href="/blog/healthy-bmi-range/">healthy BMI range</a>.</p>',
'<h2 id="children">BMI for children and teens</h2>',
f'<p>Children&rsquo;s BMI is calculated the same way but judged differently: it&rsquo;s compared with other children of the same age and sex on CDC growth charts. A BMI at or above the 95th percentile counts as obesity, and the 85th to under the 95th percentile as overweight (<a href="{CDC_CHILD}" rel="noopener">CDC</a>). Use our <a href="/kids-bmi-calculator/">kids BMI calculator</a> for the percentile, and see <a href="/childhood-obesity-statistics/">childhood obesity statistics</a> for the national picture.</p>',
'<h2 id="us">What&rsquo;s a typical BMI in the US?</h2>',
f'<p><strong>The average US adult has a BMI in the overweight range:</strong> 29.4 for men and 30.0 for women, from CDC&rsquo;s measured survey in 2021&ndash;2023 (<a href="{SER3}" rel="noopener">NCHS</a>). 40.3% of adults have obesity and 9.4% severe obesity (<a href="{DB508}" rel="noopener">NCHS Data Brief 508</a>). For what that means in pounds at each height, see <a href="/average-weight/">average weight by height</a>; for the trend since 1960, <a href="/us-obesity-statistics/">US obesity statistics</a>.</p>',
'<h2 id="limits">What BMI can&rsquo;t tell you</h2>',
f'<p><strong>BMI measures size, not composition.</strong> Two people with the same BMI can carry very different amounts of fat. In CDC&rsquo;s body scans, US men with a healthy BMI of 18.5&ndash;24.9 had a median of {mq[2]:.1f}% body fat, but the middle half ranged from {mq[1]:.1f}% to {mq[3]:.1f}% (our calculation from NHANES 2011&ndash;2018). It also misses where fat is stored, which is why waist measures are a useful companion (<a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a>).</p>',
f'<p>Muscle is the classic blind spot: very muscular people can read as overweight or obese (<a href="/blog/bmi-for-athletes/">BMI for athletes</a>). Age is another: muscle mass tends to fall by roughly 3&ndash;8% per decade after about age 30 (<a href="{VOLPI}" rel="noopener">Volpi et al., 2004</a>), so an older adult can have a &ldquo;healthy&rdquo; BMI with more fat and less muscle than before. More in <a href="/blog/bmi-limitations/">BMI limitations</a>.</p>',
'<h2 id="doctors">How doctors use BMI</h2>',
f'<p>Clinicians use BMI as a first screen, not a verdict. The US clinical guidelines on overweight and obesity assess three things together: BMI, waist circumference and the person&rsquo;s other risk factors, such as blood pressure or blood sugar (<a href="{NHLBI}" rel="noopener">NHLBI</a>). The idea itself is old: it goes back to the 19th-century Belgian statistician Adolphe Quetelet, and our <a href="/blog/bmi-history/">history of BMI</a> follows how it became the standard.</p>',
'<h2 id="body-fat">BMI and body fat</h2>',
f'<p>If you want the composition BMI can&rsquo;t give, estimate your body fat. The simplest route is a formula that starts from BMI itself (Deurenberg, with a typical error of about 4 points; <a href="{DEUR}" rel="noopener">Deurenberg et al., 1991</a>); in a head-to-head study, calipers came much closer to a DXA scan (see <a href="/blog/how-to-measure-body-fat/">how to measure body fat</a>). Our <a href="/body-fat-calculator/">body fat calculator</a> runs all three, and the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> shows what&rsquo;s typical for your age. For the full comparison, read <a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a>.</p>',
'<h2 id="faq">FAQ</h2>',
'<details class="cmb-faq"><summary><h3>What does BMI stand for?</h3></summary><p>Body mass index: weight in kilograms divided by height in meters squared.</p></details>',
'<details class="cmb-faq"><summary><h3>What is a good BMI?</h3></summary><p>For adults, 18.5 to under 25 is the healthy-weight range (CDC). At 5&prime;9&Prime;, that&rsquo;s ' + f'{EX_HB[0]}&ndash;{EX_HB[1]} lb.</p></details>',
'<details class="cmb-faq"><summary><h3>Is BMI accurate?</h3></summary><p>It&rsquo;s accurate as a calculation and useful for screening groups of people, but it can misclassify individuals because it ignores muscle, bone and fat distribution. Pair it with a waist measurement or a body fat estimate.</p></details>',
'<details class="cmb-faq"><summary><h3>What BMI counts as obese?</h3></summary><p>A BMI of 30 or higher for adults. CDC splits it into class 1 (30 to under 35), class 2 (35 to under 40) and class 3, or severe obesity (40 or higher).</p></details>',
'<details class="cmb-faq"><summary><h3>How do I calculate my BMI?</h3></summary><p>Divide your weight in kilograms by your height in meters squared, or multiply your weight in pounds by 703 and divide by your height in inches squared. Or use our <a href="/">BMI calculator</a>.</p></details>',
'<div class="wb-links"><a href="/blog/bmi-formula/">BMI formula</a><a href="/blog/bmi-categories/">BMI categories</a><a href="/blog/healthy-bmi-range/">Healthy BMI range</a><a href="/blog/bmi-history/">History of BMI</a><a href="/blog/bmi-limitations/">BMI limitations</a><a href="/new-bmi-calculator/">New BMI (Trefethen)</a><a href="/bmi-chart/">BMI chart</a></div>',
'<h2 id="sources">Sources</h2>',
'<ol class="cmb-sources">',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_ADULT}" rel="noopener">Adult BMI Categories</a>.</li>',
f'<li>National Heart, Lung, and Blood Institute. <a href="{NHLBI}" rel="noopener">Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults</a>. 1998.</li>',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_CHILD}" rel="noopener">Child and Teen BMI Categories</a>.</li>',
f'<li>Fryar CD, et al. <a href="{SER3}" rel="noopener">Anthropometric reference data for children and adults: United States, August 2021&ndash;August 2023</a>. NCHS Vital Health Stat 3(50).</li>',
f'<li>Emmerich SD, et al. <a href="{DB508}" rel="noopener">Obesity and severe obesity prevalence in adults: United States, August 2021&ndash;August 2023</a>. NCHS Data Brief No. 508.</li>',
f'<li>WHO Expert Consultation. <a href="{WHO04}" rel="noopener">Appropriate body-mass index for Asian populations and its implications for policy and intervention strategies</a>. Lancet 2004;363:157&ndash;63.</li>',
f'<li>Volpi E, Nazemi R, Fujita S. <a href="{VOLPI}" rel="noopener">Muscle tissue changes with aging</a>. Curr Opin Clin Nutr Metab Care 2004;7:405&ndash;10.</li>',
f'<li>Deurenberg P, et al. <a href="{DEUR}" rel="noopener">Body mass index as a measure of body fatness</a>. Br J Nutr 1991;65:105&ndash;14.</li>',
'</ol>',
'<p class="cmb-note">This guide is for information and is not medical advice.</p>',
'</article>',
f'<script>{JS}</script>')

TITLE = "What Is BMI? Body Mass Index Explained: Formula & Categories"
DESC = "BMI is weight in kg divided by height in meters squared. How it's calculated, CDC's adult categories, what's typical in the US, and what BMI can't tell you."
OG = "https://calculatemybmi.net/blog/what-is-bmi/og-what-is-bmi.png"
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "What Is BMI?", "description": DESC, "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630},
  "datePublished": "2026-01-15", "dateModified": "2026-10-07", "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "citation": [CDC_ADULT, NHLBI, CDC_CHILD, SER3, DB508, WHO04, VOLPI, DEUR]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"}, {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://calculatemybmi.net/blog/"}, {"@type": "ListItem", "position": 3, "name": "What Is BMI?", "item": URL}]},
 org, person]}
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="What is BMI? Body mass index explained">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'),
                 (r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="BMI explained: formula and CDC adult categories.">'),
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
dr.rectangle([0, 0, 1200, 12], fill="#1F4E79")
dr.text((56, 50), "What is BMI?", font=font(72, True), fill="#111827")
dr.text((56, 150), "BMI = weight (kg) ÷ height (m)²", font=font(40, True), fill="#1F4E79")
for i, (a, b, c) in enumerate((("Under 18.5", "Underweight", "#93C5FD"), ("18.5–24.9", "Healthy weight", "#86EFAC"), ("25–29.9", "Overweight", "#FDBA74"), ("30+", "Obesity", "#FCA5A5"))):
    x = 56 + i * 276; dr.rounded_rectangle([x, 260, x + 256, 420], radius=18, fill=c); dr.text((x + 20, 285), a, font=font(34, True), fill="#111827"); dr.text((x + 20, 345), b, font=font(26), fill="#1F2937")
dr.text((56, 470), "CDC adult categories · calculator, chart and limits explained", font=font(28), fill="#374151")
dr.text((56, 560), "calculatemybmi.net", font=font(28, True), fill="#6B7280")
im.save(os.path.join(OUT, SLUG, "og-what-is-bmi.png"), optimize=True)
print(json.dumps({"title_len": len(TITLE), "desc_len": len(DESC), "ex_bmi": EX_B, "ex_band": EX_HB, "men_healthy_bmi_bf": mq[1:4]}))
