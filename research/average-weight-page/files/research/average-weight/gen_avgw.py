#!/usr/bin/env python3
"""Build /average-weight/ for calculatemybmi.net from avgw_results.json (computed by compute.py from NHANES
August 2021-August 2023 DEMO_L + BMX_L, adults 20+, pregnant women excluded, MEC exam weights, Taylor-linearised SEs).
Method check: overall means reproduce NCHS Series 3 No. 50 (men 199.0 lb, women 171.8 lb; height 68.9 / 63.5 in; BMI 29.4 / 30.0)."""
import json, os, re, sys, csv, math, html as H
from decimal import Decimal, ROUND_HALF_UP
ROOT, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "avgw_results.json")))
SLUG = "average-weight"; URL = f"https://calculatemybmi.net/{SLUG}/"
SER3 = "https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf"
DEMO = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm"
BMX = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm"
CDC_ADULT_CAT = "https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
CSVF = "average-weight-nhanes-2021-2023.csv"
KG = 1 / 2.2046226218
f1 = lambda v: f"{v:.1f}"
def ft(h): return f"{h // 12}′{h % 12}″"
def ftp(h): return f"{h // 12}'{h % 12}\""
def bmi_r(lb, hin): return float(Decimal(lb * 703 / hin ** 2).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
def healthy(hin):
    ok = [lb for lb in range(50, 400) if 18.5 <= bmi_r(lb, hin) <= 24.9]
    return ok[0], ok[-1]
assert healthy(69) == (125, 168), healthy(69)          # site rule test (5'9")
def cat(b): return "Underweight" if b < 18.5 else "Healthy weight" if b < 25 else "Overweight" if b < 30 else "Obesity"
M, F = R["men"], R["women"]
assert round(M["wt_lb"]["mean"], 1) == 199.0 and round(F["wt_lb"]["mean"], 1) == 171.8 and round(M["ht_in"]["mean"], 1) == 68.9 and round(F["ht_in"]["mean"], 1) == 63.5
assert round(M["BMXBMI"]["mean"], 1) == 29.4 and round(F["BMXBMI"]["mean"], 1) == 30.0
HM = {int(k): v for k, v in M["height"].items()}; HF = {int(k): v for k, v in F["height"].items()}
SMALL = 60
def ci(e): return (e["mean"] - 1.96 * e["se"], e["mean"] + 1.96 * e["se"])
# derived facts
def avg_bmi_at(h, d): return bmi_r(d[h]["wt"]["mean"], h)
over_m = sum(1 for h in HM if avg_bmi_at(h, HM) >= 25); over_f = sum(1 for h in HF if avg_bmi_at(h, HF) >= 25)
w54 = HF[64]; m59 = HM[69]
def slope(D):
    hs = sorted(D); n = [D[h]["wt"]["n"] for h in hs]; y = [D[h]["wt"]["mean"] for h in hs]
    mx = sum(a * b for a, b in zip(hs, n)) / sum(n); my = sum(a * b for a, b in zip(y, n)) / sum(n)
    return sum(c * (a - mx) * (b - my) for a, b, c in zip(hs, y, n)) / sum(c * (a - mx) ** 2 for a, c in zip(hs, n))
sl_f, sl_m = slope(HF), slope(HM)
assert all(D[h]["wt"]["mean"] > healthy(h)[1] for D in (HF, HM) for h in D), "average not above healthy range at some height"
age_peak_m = max(M["age"].items(), key=lambda kv: kv[1]["wt"]["mean"]); age_peak_f = max(F["age"].items(), key=lambda kv: kv[1]["wt"]["mean"])

def table(sex, D):
    rows = []
    for h in sorted(D):
        e = D[h]["wt"]; lo, hi = ci(e); q = D[h]["q"]; hl, hh = healthy(h); b = avg_bmi_at(h, D)
        small = e["n"] < SMALL
        rows.append(f'<tr id="{sex}-{h // 12}-{h % 12}"><th scope="row">{ft(h)}</th><td class="aw-v" style="--w:{(e["mean"] - 100) / 160 * 100:.0f}%"><strong>{f1(e["mean"])} lb</strong><span class="aw-kg">{f1(e["mean"] * KG)} kg</span></td>'
                    f'<td>{f1(lo)}–{f1(hi)}</td><td>{q[0]:.0f}–{q[2]:.0f} lb</td><td>{hl}–{hh} lb</td><td>{b} <span class="aw-cat">{cat(b).lower()}</span></td><td>{e["n"]}{"<sup>†</sup>" if small else ""}</td></tr>')
    return "".join(rows)

def chart():
    W, Hh, L, B, T, Rr = 680, 360, 48, 44, 16, 14
    hs = list(range(56, 77)); x0, x1 = 56, 76; y0, y1 = 80, 260
    X = lambda h: L + (h - x0) * (W - L - Rr) / (x1 - x0); Y = lambda v: Hh - B - (v - y0) * (Hh - T - B) / (y1 - y0)
    g = []
    for v in range(100, 261, 40):
        g.append(f'<line x1="{L}" x2="{W - Rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#EEF0F3"/><text x="{L - 8}" y="{Y(v) + 5:.1f}" text-anchor="end" class="aw-ax">{v}</text>')
    for h in range(56, 77, 2):
        g.append(f'<text x="{X(h):.1f}" y="{Hh - 16}" text-anchor="middle" class="aw-ax">{ft(h)}</text>')
    up = " L".join(f"{X(h):.1f} {Y(healthy(h)[1]):.1f}" for h in hs); dn = " L".join(f"{X(h):.1f} {Y(healthy(h)[0]):.1f}" for h in reversed(hs))
    g.append(f'<path d="M{up} L{dn} Z" fill="#CDE7D8" opacity=".8"/><text x="{X(73):.1f}" y="{Y(healthy(73)[0]) + 22:.1f}" text-anchor="middle" class="aw-ax-g">healthy-weight range</text>')
    for D, col, lab in ((HF, "#C2481E", "Women"), (HM, "#1F4E79", "Men")):
        hh = sorted(D)
        bu = " L".join(f"{X(h):.1f} {Y(ci(D[h]['wt'])[1]):.1f}" for h in hh); bd = " L".join(f"{X(h):.1f} {Y(ci(D[h]['wt'])[0]):.1f}" for h in reversed(hh))
        g.append(f'<path d="M{bu} L{bd} Z" fill="{col}" opacity=".12"/>')
        g.append('<path d="M' + " L".join(f"{X(h):.1f} {Y(D[h]['wt']['mean']):.1f}" for h in hh) + f'" fill="none" stroke="{col}" stroke-width="2.6"/>')
        for h in hh: g.append(f'<circle cx="{X(h):.1f}" cy="{Y(D[h]["wt"]["mean"]):.1f}" r="3.5" fill="{col}"/>')
        e = hh[-1]; g.append(f'<text x="{X(e) + 6:.1f}" y="{Y(D[e]["wt"]["mean"]) - 6:.1f}" class="aw-lab" fill="{col}">{lab}</text>')
    return (f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-labelledby="aw-ch-t"><title id="aw-ch-t">Average weight of US adults by height and sex, compared with the healthy-weight range</title>' + "".join(g) + "</svg>")

def age_rows():
    out = ""
    for k in M["age"]:
        m, w = M["age"][k], F["age"][k]
        out += f'<tr><th scope="row">{k}</th><td>{f1(m["wt"]["mean"])} lb</td><td>{f1(w["wt"]["mean"])} lb</td><td>{f1(m["waist"]["mean"])} in</td><td>{f1(w["waist"]["mean"])} in</td><td>{f1(m["bmi"]["mean"])}</td><td>{f1(w["bmi"]["mean"])}</td></tr>'
    return out

# ---------- tool data ----------
TD = {"m": {str(h): {"a": round(v["wt"]["mean"], 1), "q": [round(x, 1) for x in v["q"]], "c": [round(x, 1) for x in v["cdf"]], "n": v["wt"]["n"], "nw": v["nwin"]} for h, v in HM.items()},
      "f": {str(h): {"a": round(v["wt"]["mean"], 1), "q": [round(x, 1) for x in v["q"]], "c": [round(x, 1) for x in v["cdf"]], "n": v["wt"]["n"], "nw": v["nwin"]} for h, v in HF.items()},
      "avg": {"m": round(M["wt_lb"]["mean"], 1), "f": round(F["wt_lb"]["mean"], 1)}}
JS = r"""
(function(){var D=window.AW_DATA,$=function(i){return document.getElementById(i);};
function hr(lb,h){return Math.round(lb*703/(h*h)*10+1e-9)/10;}
function band(h){var lo=null,hi=null;for(var lb=50;lb<400;lb++){var b=hr(lb,h);if(b>=18.5&&b<=24.9){if(lo===null)lo=lb;hi=lb;}}return [lo,hi];}
function cat(b){return b<18.5?'Underweight':b<25?'Healthy weight':b<30?'Overweight':'Obesity';}
function ftin(h){return Math.floor(h/12)+'′'+(h%12)+'″';}
function pct(c,w){if(w<=c[0])return '5th or lower';if(w>=c[c.length-1])return '95th or higher';for(var i=1;i<c.length;i++){if(w<=c[i]){var p=5*i+5*(w-c[i-1])/(c[i]-c[i-1]);return Math.round(p)+'th';}}return '';}
function unit(){return document.querySelector('input[name="aw-u"]:checked').value;}
function syncUnits(){var u=unit();$('aw-imp').hidden=u!=='imp';$('aw-met').hidden=u!=='met';}
document.querySelectorAll('input[name="aw-u"]').forEach(function(r){r.addEventListener('change',syncUnits);});syncUnits();
$('aw-go').addEventListener('click',function(){var sx=document.querySelector('input[name="aw-sex"]:checked').value,u=unit(),h,w;
 if(u==='imp'){h=(+$('aw-ft').value)*12+(+$('aw-in').value);w=parseFloat($('aw-lb').value);}else{var cm=parseFloat($('aw-cm').value);h=cm/2.54;w=parseFloat($('aw-kg').value)/0.45359237;}
 var out=$('aw-out');if(!(h>=48&&h<=90)){out.innerHTML='<p class="aw-err">Enter a height between 4′0″ and 7′6″.</p>';out.hidden=false;return;}
 var hi=Math.round(h),S=D[sx],cell=S[String(hi)],who=sx==='m'?'men':'women',hb=band(h),html='';
 html+='<div class="aw-res-h"><span class="aw-tag">'+(sx==='m'?'Men':'Women')+' · '+ftin(hi)+'</span>';
 if(cell){html+='<div class="aw-big">'+cell.a.toFixed(1)+' lb <small>average ('+(cell.a*0.45359237).toFixed(1)+' kg)</small></div><p>Middle half of US '+who+' your height: <strong>'+Math.round(cell.q[0])+'–'+Math.round(cell.q[2])+' lb</strong> · median '+Math.round(cell.q[1])+' lb · based on '+cell.n+' people measured'+(cell.n<60?' (small sample)':'')+'.</p>';}
 else{html+='<div class="aw-big">Not enough data</div><p>CDC measured fewer than 30 '+who+' at '+ftin(hi)+', so we don’t show an average for that height. The national average for '+who+' is <strong>'+D.avg[sx].toFixed(1)+' lb</strong>.</p>';}
 html+='</div><p>Healthy-weight range at your height (BMI 18.5–24.9): <strong>'+hb[0]+'–'+hb[1]+' lb</strong>.</p>';
 if(w>0){var b=hr(w,h);html+='<div class="aw-you"><p><strong>Your weight, '+w.toFixed(0)+' lb</strong>: BMI '+b.toFixed(1)+' ('+cat(b).toLowerCase()+').</p>';
  if(cell){var d=w-cell.a;html+='<p>That is <strong>'+Math.abs(d).toFixed(0)+' lb '+(d>=0?'above':'below')+'</strong> the average for '+who+' your height, around the <strong>'+pct(cell.c,w)+' percentile</strong> (heavier than about that share of '+who+' within an inch of your height).</p>';}
  html+='</div>';}
 html+='<p class="cmb-src">Our calculation from CDC NHANES August 2021–August 2023 exam data (adults 20+, measured). Percentiles use people within ±1 inch of your height.</p>';
 out.innerHTML=html;out.hidden=false;});
})();
"""
CSS = """
.aw-cards{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 14px}
.aw-cards .aw-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}
@media (min-width:760px){.aw-cards .aw-kpi{flex:1 1 calc(25% - 10px)}}
.aw-kpi-l{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:#6B7280;font-weight:700}
.aw-kpi-n{font-size:1.9rem;font-weight:800;line-height:1.1;color:#111827}
.aw-kpi-s{font-size:.9rem;color:#374151}
.aw-tool{border:1px solid #EEF0F3;border-radius:16px;padding:16px;margin:10px 0 14px;background:linear-gradient(180deg,#FFFFFF 0%,#F5F9FF 100%);box-shadow:0 6px 24px rgba(17,24,39,.07)}
.aw-tool h2{margin-top:2px}
.aw-row{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;margin:10px 0}
.aw-row label{font-weight:700}
.aw-seg{display:inline-flex;border:2px solid #1F2937;border-radius:10px;overflow:hidden}
.aw-seg label{padding:8px 14px;min-height:40px;display:flex;align-items:center;cursor:pointer;font-weight:700}
.aw-seg input{position:absolute;opacity:0}
.aw-seg input:checked+span{background:#1F2937;color:#fff;border-radius:6px;padding:4px 8px}
.aw-tool select,.aw-tool input[type=number]{min-height:44px;font-size:16px;border-radius:8px;padding:4px 8px;max-width:110px}
#aw-go{min-height:46px;padding:10px 20px;font-weight:800;border:0;border-radius:10px;background:#C2481E;color:#fff;cursor:pointer}
.aw-out{margin-top:12px;border-top:1px solid #E5E7EB;padding-top:10px}
.aw-out[hidden],#aw-imp[hidden],#aw-met[hidden]{display:none}
.aw-res-h{border-left:8px solid #1F4E79;background:#fff;border-radius:12px;padding:10px 14px;box-shadow:0 4px 14px rgba(17,24,39,.08);margin-bottom:8px}
.aw-tag{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:#6B7280;font-weight:800}
.aw-big{font-size:2.2rem;font-weight:800;color:#111827;line-height:1.15}
.aw-big small{font-size:.9rem;font-weight:600;color:#4B5563}
.aw-you{background:#FFF7F2;border:1px solid #F3D3AE;border-radius:12px;padding:10px 14px}
.aw-err{color:#B91C1C;font-weight:700}
.aw-fig{margin:16px auto;max-width:680px}
.aw-fig svg{display:block;width:100%;height:auto}
.aw-ax{font:15px system-ui,sans-serif;fill:#6B7280}
.aw-ax-g{font:700 15px system-ui,sans-serif;fill:#2E7D4F}
.aw-lab{font:800 17px system-ui,sans-serif}
.aw-kg{display:block;font-size:.8rem;color:#6B7280}
.aw-cat{font-size:.8rem;color:#6B7280}
td.aw-v{background-image:linear-gradient(90deg,#DBEAFE 0,#DBEAFE var(--w),transparent var(--w));background-size:100% 6px;background-repeat:no-repeat;background-position:0 100%}
"""
def P(*a): return "\n".join(a)
ft_opts = "".join(f'<option value="{v}"{" selected" if v == 5 else ""}>{v} ft</option>' for v in (4, 5, 6, 7))
in_opts = "".join(f'<option value="{v}"{" selected" if v == 6 else ""}>{v} in</option>' for v in range(12))
mm, ww = M["wt_lb"], F["wt_lb"]
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <span>Average Weight</span></nav>',
'<article class="cmb-stats">',
'<h1>Average Weight for Men and Women</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Data: CDC NHANES August 2021&ndash;August 2023, our calculation from the exam files &middot; Reviewed October 3, 2026 &middot; Not medical advice</p>',
'<p class="cmb-intro">What do American adults actually weigh at your height? We calculated it from CDC&rsquo;s raw exam data &mdash; people weighed on a scale, not asked &mdash; and checked our method by reproducing CDC&rsquo;s own published averages to the decimal.</p>',
'<section class="aw-tool" aria-label="Compare your weight">',
'<h2>Compare your weight with people your height</h2>',
'<div class="aw-row"><span class="aw-seg" role="radiogroup" aria-label="Sex"><label><input type="radio" name="aw-sex" value="f" checked><span>Woman</span></label><label><input type="radio" name="aw-sex" value="m"><span>Man</span></label></span>'
'<span class="aw-seg" role="radiogroup" aria-label="Units"><label><input type="radio" name="aw-u" value="imp" checked><span>ft / lb</span></label><label><input type="radio" name="aw-u" value="met"><span>cm / kg</span></label></span></div>',
f'<div class="aw-row" id="aw-imp"><label for="aw-ft">Height</label><select id="aw-ft">{ft_opts}</select><select id="aw-in" aria-label="Inches">{in_opts}</select><label for="aw-lb">Weight (optional)</label><input type="number" id="aw-lb" min="50" max="700" step="1" placeholder="lb" inputmode="decimal"></div>',
'<div class="aw-row" id="aw-met" hidden><label for="aw-cm">Height</label><input type="number" id="aw-cm" min="120" max="230" step="0.5" placeholder="cm" inputmode="decimal"><label for="aw-kg">Weight (optional)</label><input type="number" id="aw-kg" min="20" max="320" step="0.1" placeholder="kg" inputmode="decimal"></div>',
'<div class="aw-row"><button type="button" id="aw-go">Compare</button></div>',
'<div id="aw-out" class="aw-out" hidden aria-live="polite"></div>',
'</section>',
f'<div class="aw-cards"><div class="aw-kpi" style="--c:#1F4E79"><span class="aw-kpi-l">Average man</span><span class="aw-kpi-n">{f1(mm["mean"])} lb</span><span class="aw-kpi-s">{f1(mm["mean"] * KG)} kg &middot; height {f1(M["ht_in"]["mean"])} in</span></div>'
f'<div class="aw-kpi" style="--c:#C2481E"><span class="aw-kpi-l">Average woman</span><span class="aw-kpi-n">{f1(ww["mean"])} lb</span><span class="aw-kpi-s">{f1(ww["mean"] * KG)} kg &middot; height {f1(F["ht_in"]["mean"])} in</span></div>'
f'<div class="aw-kpi" style="--c:#6B46C1"><span class="aw-kpi-l">Average BMI</span><span class="aw-kpi-n">{f1(M["BMXBMI"]["mean"])} / {f1(F["BMXBMI"]["mean"])}</span><span class="aw-kpi-s">men / women</span></div>'
f'<div class="aw-kpi" style="--c:#2E7D4F"><span class="aw-kpi-l">Average waist</span><span class="aw-kpi-n">{f1(M["waist_in"]["mean"])} / {f1(F["waist_in"]["mean"])} in</span><span class="aw-kpi-s">men / women</span></div></div>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>The average American man weighs {f1(mm["mean"])} lb ({f1(mm["mean"] * KG)} kg) and the average woman {f1(ww["mean"])} lb ({f1(ww["mean"] * KG)} kg)</strong>, based on adults 20 and older measured by CDC in August 2021&ndash;August 2023. At 5&prime;4&Prime;, the average woman weighs {f1(w54["wt"]["mean"])} lb; at 5&prime;9&Prime;, the average man weighs {f1(m59["wt"]["mean"])} lb. At every height with enough data, the average falls above the healthy-weight range.</p>',
f'<p class="cmb-src">Source: our calculation from CDC <a href="{DEMO}" rel="noopener">NHANES 2021&ndash;2023 exam data</a>; overall means match CDC&rsquo;s published <a href="{SER3}" rel="noopener">anthropometric reference data</a>.</p>',
'</div>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol><li><a href="#women-height">Average weight for women by height</a></li><li><a href="#men-height">Average weight for men by height</a></li><li><a href="#chart">Average vs healthy weight</a></li><li><a href="#age">Average weight by age</a></li><li><a href="#bmi-waist">Average BMI, height and waist</a></li><li><a href="#faq">FAQ</a></li><li><a href="#method">How we calculated this</a></li></ol></nav>',
'<h2 id="women-height">Average weight for women by height</h2>',
f'<p><strong>Across heights, average weight rises about {sl_f:.1f} lb per inch for women and {sl_m:.1f} lb for men</strong> (our calculation), but not perfectly smoothly: each height is its own sample of real women, so neighboring rows can wobble by a few pounds. The 95% range shows how precise each average is. The middle-half column shows what&rsquo;s typical: half of women that height weigh within that range.</p>',
'<div class="cmb-table-wrap"><table><caption>Average weight of US women by height, adults 20+, August 2021–August 2023 (measured)</caption><thead><tr><th scope="col">Height</th><th scope="col">Average</th><th scope="col">95% range</th><th scope="col">Middle half</th><th scope="col">Healthy range (BMI 18.5–24.9)</th><th scope="col">BMI at average</th><th scope="col">People measured</th></tr></thead>',
f'<tbody>{table("women", HF)}</tbody></table></div>',
f'<p class="cmb-src">Heights rounded to the nearest inch. Women 5&prime;10&Prime; and taller, and under 4&prime;9&Prime;, aren&rsquo;t shown: fewer than 30 were measured. † fewer than {SMALL} people measured: treat as a rough guide. Healthy range uses CDC&rsquo;s adult BMI categories (<a href="{CDC_ADULT_CAT}" rel="noopener">CDC</a>).</p>',
'<h2 id="men-height">Average weight for men by height</h2>',
f'<p><strong>Men follow the same climb, from {f1(HM[min(HM)]["wt"]["mean"])} lb at {ft(min(HM))} to {f1(HM[max(HM)]["wt"]["mean"])} lb at {ft(max(HM))}.</strong> At 6&prime;0&Prime;, the average man weighs {f1(HM[72]["wt"]["mean"])} lb, while the healthy range for that height tops out at {healthy(72)[1]} lb.</p>',
'<div class="cmb-table-wrap"><table><caption>Average weight of US men by height, adults 20+, August 2021–August 2023 (measured)</caption><thead><tr><th scope="col">Height</th><th scope="col">Average</th><th scope="col">95% range</th><th scope="col">Middle half</th><th scope="col">Healthy range (BMI 18.5–24.9)</th><th scope="col">BMI at average</th><th scope="col">People measured</th></tr></thead>',
f'<tbody>{table("men", HM)}</tbody></table></div>',
f'<p class="cmb-src">Men under 5&prime;2&Prime; and 6&prime;4&Prime; and taller aren&rsquo;t shown: fewer than 30 measured. † fewer than {SMALL} measured.</p>',
'<h2 id="chart">Average weight vs healthy weight</h2>',
f'<p><strong>{("At every height we can show, for both women and men," if (over_f, over_m) == (len(HF), len(HM)) else f"At {over_f} of {len(HF)} heights for women and {over_m} of {len(HM)} for men,")} the average weight corresponds to a BMI of 25 or more.</strong> In other words, the typical American at almost any height is above the healthy-weight range. That&rsquo;s why &ldquo;average&rdquo; and &ldquo;healthy&rdquo; shouldn&rsquo;t be read as the same thing; for a target, our <a href="/ideal-weight/">ideal weight calculator</a> and <a href="/bmi-chart/">BMI chart</a> are the better tools.</p>',
f'<figure class="aw-fig">{chart()}<figcaption>Average weight by height (lines, with 95% bands) against the healthy-weight range for each height (green, BMI 18.5–24.9). Our calculation from CDC NHANES August 2021–August 2023.</figcaption></figure>',
'<h2 id="age">Average weight by age</h2>',
f'<p><strong>Weight peaks in middle age:</strong> men average the most at {age_peak_m[0]} ({f1(age_peak_m[1]["wt"]["mean"])} lb) and women at {age_peak_f[0]} ({f1(age_peak_f[1]["wt"]["mean"])} lb), then averages fall in older groups. These are different people at different ages in one survey, not the same people followed over time.</p>',
'<div class="cmb-table-wrap"><table><caption>Average weight, waist and BMI by age group, US adults (measured, August 2021–August 2023)</caption><thead><tr><th scope="col">Age</th><th scope="col">Men, weight</th><th scope="col">Women, weight</th><th scope="col">Men, waist</th><th scope="col">Women, waist</th><th scope="col">Men, BMI</th><th scope="col">Women, BMI</th></tr></thead>',
f'<tbody>{age_rows()}</tbody></table></div>',
'<h2 id="bmi-waist">Average BMI, height and waist size</h2>',
f'<p>The average man is {f1(M["ht_in"]["mean"])} inches tall (about 5&prime;9&Prime;) with a BMI of {f1(M["BMXBMI"]["mean"])} and a waist of {f1(M["waist_in"]["mean"])} inches; the average woman is {f1(F["ht_in"]["mean"])} inches (about 5&prime;3.5&Prime;) with a BMI of {f1(F["BMXBMI"]["mean"])} and a waist of {f1(F["waist_in"]["mean"])} inches. Men&rsquo;s average BMI is in CDC&rsquo;s overweight range (25 to under 30); women&rsquo;s sits right at the line between overweight and obesity. Half of men weigh more than {M["wt_pct"]["p50"]:.0f} lb and half of women more than {F["wt_pct"]["p50"]:.0f} lb: the medians are lower than the averages because the heaviest people pull averages up.</p>',
f'<p>For how many adults have obesity, see our <a href="/us-obesity-statistics/">US obesity statistics</a>; for the full BMI scale, our guide to <a href="/blog/bmi-categories/">BMI categories</a>.</p>',
'<h2 id="faq">FAQ</h2>',
f'<details class="cmb-faq"><summary><h3>What is the average weight for a woman?</h3></summary><p>{f1(ww["mean"])} lb ({f1(ww["mean"] * KG)} kg) for US women 20 and older, measured in 2021–2023. The median is {F["wt_pct"]["p50"]:.0f} lb.</p></details>',
f'<details class="cmb-faq"><summary><h3>What is the average weight for a man?</h3></summary><p>{f1(mm["mean"])} lb ({f1(mm["mean"] * KG)} kg) for US men 20 and older; the median is {M["wt_pct"]["p50"]:.0f} lb.</p></details>',
f'<details class="cmb-faq"><summary><h3>What is the average weight for a 5&prime;4&Prime; woman?</h3></summary><p>{f1(w54["wt"]["mean"])} lb, with half of women that height between {w54["q"][0]:.0f} and {w54["q"][2]:.0f} lb. The healthy range at 5&prime;4&Prime; is {healthy(64)[0]}–{healthy(64)[1]} lb.</p></details>',
f'<details class="cmb-faq"><summary><h3>What is the average weight for a 5&prime;9&Prime; man?</h3></summary><p>{f1(m59["wt"]["mean"])} lb, with half of men that height between {m59["q"][0]:.0f} and {m59["q"][2]:.0f} lb. The healthy range at 5&prime;9&Prime; is {healthy(69)[0]}–{healthy(69)[1]} lb.</p></details>',
f'<details class="cmb-faq"><summary><h3>What is the average waist size?</h3></summary><p>{f1(M["waist_in"]["mean"])} inches for men and {f1(F["waist_in"]["mean"])} inches for women, measured at the top of the hip bone in CDC&rsquo;s exam.</p></details>',
f'<details class="cmb-faq"><summary><h3>Is average weight the same as healthy weight?</h3></summary><p>No. At most heights the average corresponds to a BMI of 25 or more, which CDC classes as overweight. Use the healthy-range column or our <a href="/bmi-chart/">BMI chart</a> for that.</p></details>',
'<h2 id="method">How we calculated this</h2>',
f'<p>We used CDC&rsquo;s National Health and Nutrition Examination Survey for August 2021&ndash;August 2023: the demographics file and the body measures file, where trained staff weigh and measure every participant. We kept adults 20 and older, excluded pregnant women, and applied CDC&rsquo;s exam sample weights so the results represent the US population. Standard errors use the survey&rsquo;s strata and primary sampling units (Taylor linearization). We show a height only when at least 30 people were measured at it.</p>',
f'<p><strong>Check against CDC:</strong> our overall results reproduce CDC&rsquo;s published figures in <a href="{SER3}" rel="noopener">Vital and Health Statistics Series 3, No. 50</a> &mdash; average weight {f1(mm["mean"])} lb for men and {f1(ww["mean"])} lb for women, height {f1(M["ht_in"]["mean"])} and {f1(F["ht_in"]["mean"])} inches, BMI {f1(M["BMXBMI"]["mean"])} and {f1(F["BMXBMI"]["mean"])}. The breakdowns by height are our own calculation from the same files.</p>',
'<ol class="cmb-sources">',
f'<li>National Center for Health Statistics. <a href="{DEMO}" rel="noopener">NHANES August 2021–August 2023 Demographic Variables and Sample Weights (DEMO_L)</a>.</li>',
f'<li>National Center for Health Statistics. <a href="{BMX}" rel="noopener">NHANES August 2021–August 2023 Body Measures (BMX_L)</a>.</li>',
f'<li>Fryar CD, et al. <a href="{SER3}" rel="noopener">Anthropometric reference data for children and adults: United States, August 2021–August 2023</a>. Vital and Health Statistics, Series 3, No. 50.</li>',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_ADULT_CAT}" rel="noopener">Adult BMI Categories</a>.</li>',
'</ol>',
f'<p><strong>Download:</strong> <a href="/{SLUG}/{CSVF}" download>average weight by sex, height and age (CSV)</a>. Free to reuse with a link to this page (CC BY 4.0).</p>',
'<p class="cmb-note">This page describes populations, not individuals. It is not medical advice.</p>',
'<h2>Related</h2><ul><li><a href="/bmi-chart/">BMI chart: healthy weight for every height</a></li><li><a href="/ideal-weight/">Ideal weight calculator</a></li><li><a href="/us-obesity-statistics/">US obesity statistics</a></li><li><a href="/">BMI calculator</a></li></ul>',
'</article>',
f'<script>window.AW_DATA={json.dumps(TD, separators=(",", ":"))};</script>',
f'<script>{JS}</script>')

TITLE = "Average Weight for Men and Women by Height and Age (CDC)"
DESC = f"The average US man weighs {f1(mm['mean'])} lb and the average woman {f1(ww['mean'])} lb (CDC, measured 2021–2023). See averages for every height and age, and compare your weight."
OG = f"https://calculatemybmi.net/{SLUG}/og-{SLUG}.png"
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "Average Weight for Men and Women", "description": DESC,
  "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}, "datePublished": "2026-10-03", "dateModified": "2026-10-03",
  "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "citation": [DEMO, BMX, SER3, CDC_ADULT_CAT]},
 {"@type": "Dataset", "@id": URL + "#dataset", "name": "Average weight of US adults by sex, height and age, NHANES August 2021–August 2023",
  "description": "Weighted mean, median and interquartile range of measured body weight for US adults 20 and older by sex and height (nearest inch), plus mean weight, waist circumference and BMI by age group, with standard errors. Calculated by calculatemybmi.net from CDC NHANES public-use exam files; overall means reproduce NCHS Series 3 No. 50.",
  "url": URL, "creator": {"@id": "https://calculatemybmi.net/#organization"}, "isBasedOn": [DEMO, BMX], "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": True, "temporalCoverage": "2021-08/2023-08", "spatialCoverage": {"@type": "Place", "name": "United States"},
  "variableMeasured": ["Mean body weight", "Median body weight", "Body weight interquartile range", "Mean waist circumference", "Mean BMI", "Standard error"],
  "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"https://calculatemybmi.net/{SLUG}/{CSVF}"}]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"}, {"@type": "ListItem", "position": 2, "name": "Average Weight", "item": URL}]},
 org, person]}
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Average weight for men and women (CDC data)">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'),
                 (r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="Average US man {f1(mm["mean"])} lb, average woman {f1(ww["mean"])} lb (CDC NHANES 2021–2023).">'),
                 (r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG}">')]:
    head = re.sub(pat, rep, head, flags=re.S)
rest = shell[shell.find("</script>", shell.find('<script type="application/ld+json">')) + 9:]
page = (head + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, indent=1) + "</script>" + rest[:rest.find("</head>")] + "<style>" + CSS + "</style>"
        + rest[rest.find("</head>"):rest.find("<main>")] + '<main><div class="container" style="max-width:1000px;margin:0 auto;padding:2rem 1rem 3rem;">' + content + "</div>" + rest[rest.find("</main>"):])
os.makedirs(os.path.join(OUT, SLUG), exist_ok=True)
open(os.path.join(OUT, SLUG, "index.html"), "w", encoding="utf-8").write(page)
with open(os.path.join(OUT, SLUG, CSVF), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["# Average body weight of US adults 20+ (pregnant women excluded), measured, NHANES August 2021-August 2023 (DEMO_L, BMX_L), weighted with MEC exam weights; SE by Taylor linearisation. Calculated by calculatemybmi.net; CC BY 4.0. Heights rounded to nearest inch; cells with n<30 omitted."])
    w.writerow(["table", "sex", "group", "mean_weight_lb", "se_lb", "median_lb", "p25_lb", "p75_lb", "n", "healthy_range_lb"])
    for sx, D in (("women", HF), ("men", HM)):
        for h in sorted(D):
            e = D[h]["wt"]; q = D[h]["q"]; hl, hh = healthy(h)
            w.writerow(["height", sx, ftp(h), round(e["mean"], 1), round(e["se"], 2), round(q[1], 1), round(q[0], 1), round(q[2], 1), e["n"], f"{hl}-{hh}"])
    for sx, S in (("women", F), ("men", M)):
        for k, v in S["age"].items():
            w.writerow(["age", sx, k, round(v["wt"]["mean"], 1), round(v["wt"]["se"], 2), "", "", "", v["wt"]["n"], ""])
        w.writerow(["overall", sx, "20+", round(S["wt_lb"]["mean"], 1), round(S["wt_lb"]["se"], 2), round(S["wt_pct"]["p50"], 1), round(S["wt_pct"]["p25"], 1), round(S["wt_pct"]["p75"], 1), S["wt_lb"]["n"], ""])
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1200, 630), "#FFFFFF"); dr = ImageDraw.Draw(im)
def font(sz, b=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()
dr.rectangle([0, 0, 1200, 12], fill="#1F4E79")
dr.text((56, 50), "Average weight in the US", font=font(56, True), fill="#111827")
dr.text((56, 126), "Adults 20+, measured by CDC, 2021–2023", font=font(30), fill="#4B5563")
dr.text((56, 210), f"Men  {f1(mm['mean'])} lb", font=font(72, True), fill="#1F4E79")
dr.text((56, 310), f"Women  {f1(ww['mean'])} lb", font=font(72, True), fill="#C2481E")
dr.text((56, 430), "Every height, every age group", font=font(34), fill="#1F2937")
dr.text((56, 560), "calculatemybmi.net", font=font(28, True), fill="#6B7280")
im.save(os.path.join(OUT, SLUG, f"og-{SLUG}.png"), optimize=True)
print(json.dumps(dict(over_f=over_f, nf=len(HF), over_m=over_m, nm=len(HM), w54=round(w54["wt"]["mean"], 1), m59=round(m59["wt"]["mean"], 1), peak_m=age_peak_m[0], peak_f=age_peak_f[0], title_len=len(TITLE), desc_len=len(DESC))))
