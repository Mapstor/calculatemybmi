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

def chart_sex(D, col, sex):
    W, Hh, L, B, T, Rr = 360, 300, 44, 34, 12, 10
    hs = sorted(D); x0, x1 = hs[0] - 0.5, hs[-1] + 0.5
    lo = min(healthy(h)[0] for h in hs) - 10; hi = max(ci(D[h]["wt"])[1] for h in hs) + 10
    y0 = int(lo // 20 * 20); y1 = int(-(-hi // 20) * 20)
    X = lambda h: L + (h - x0) * (W - L - Rr) / (x1 - x0); Y = lambda v: Hh - B - (v - y0) * (Hh - T - B) / (y1 - y0)
    g = []
    for v in range(y0, y1 + 1, 20 if y1 - y0 <= 160 else 40):
        g.append(f'<line x1="{L}" x2="{W - Rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#EEF0F3"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" class="aw-ax">{v}</text>')
    step = 2 if len(hs) <= 14 else 3
    for h in hs[::step]:
        g.append(f'<text x="{X(h):.1f}" y="{Hh - 12}" text-anchor="middle" class="aw-ax">{ft(h)}</text>')
    up = " L".join(f"{X(h):.1f} {Y(healthy(h)[1]):.1f}" for h in hs); dn = " L".join(f"{X(h):.1f} {Y(healthy(h)[0]):.1f}" for h in reversed(hs))
    g.append(f'<path d="M{up} L{dn} Z" fill="#CDE7D8"/>')
    bu = " L".join(f"{X(h):.1f} {Y(ci(D[h]['wt'])[1]):.1f}" for h in hs); bd = " L".join(f"{X(h):.1f} {Y(ci(D[h]['wt'])[0]):.1f}" for h in reversed(hs))
    g.append(f'<path d="M{bu} L{bd} Z" fill="{col}" opacity=".16"/>')
    g.append('<path d="M' + " L".join(f"{X(h):.1f} {Y(D[h]['wt']['mean']):.1f}" for h in hs) + f'" fill="none" stroke="{col}" stroke-width="2.6"/>')
    for h in hs: g.append(f'<circle cx="{X(h):.1f}" cy="{Y(D[h]["wt"]["mean"]):.1f}" r="3.2" fill="{col}"><title>{ft(h)}: {f1(D[h]["wt"]["mean"])} lb average</title></circle>')
    return (f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-label="Average weight of US {sex} by height (line with 95% band) and the healthy-weight range for each height (green)">' + "".join(g) + "</svg>")

def chart():
    return ('<div class="aw-sm"><div class="aw-sm-p"><p class="aw-sm-t" style="--c:#C2481E">Women</p>' + chart_sex(HF, "#C2481E", "women") + '</div>'
            '<div class="aw-sm-p"><p class="aw-sm-t" style="--c:#1F4E79">Men</p>' + chart_sex(HM, "#1F4E79", "men") + '</div></div>'
            '<ul class="aw-key"><li><span class="aw-key-l"></span>Average weight (dots) with its 95% range</li><li><span class="aw-key-g"></span>Healthy-weight range, BMI 18.5&ndash;24.9</li></ul>')

def age_rows():
    out = ""
    for k in M["age"]:
        m, w = M["age"][k], F["age"][k]
        out += f'<tr><th scope="row">{k}</th><td>{f1(m["wt"]["mean"])} lb</td><td>{f1(w["wt"]["mean"])} lb</td><td>{f1(m["waist"]["mean"])} in</td><td>{f1(w["waist"]["mean"])} in</td><td>{f1(m["bmi"]["mean"])}</td><td>{f1(w["bmi"]["mean"])}</td></tr>'
    return out

# ---------- tool data ----------
TOOL_HTML = (
'<section class="aw-tool" aria-label="Compare your weight">'
'<div class="aw-tool-head"><h2>How does your weight compare?</h2><p>What US adults of your sex and height actually weigh, where you rank, and how your BMI compares.</p></div>'
'<div class="aw-form">'
'<div class="aw-field"><span class="aw-flabel" id="aw-sex-l">I am</span><div class="aw-pills" role="radiogroup" aria-labelledby="aw-sex-l">'
'<input type="radio" id="aw-sx-f" name="aw-sex" value="f" checked><label for="aw-sx-f">Woman</label>'
'<input type="radio" id="aw-sx-m" name="aw-sex" value="m"><label for="aw-sx-m">Man</label></div></div>'
'<div class="aw-field"><span class="aw-flabel" id="aw-u-l">Units</span><div class="aw-pills" role="radiogroup" aria-labelledby="aw-u-l">'
'<input type="radio" id="aw-u-imp" name="aw-u" value="imp" checked><label for="aw-u-imp">ft &middot; lb</label>'
'<input type="radio" id="aw-u-met" name="aw-u" value="met"><label for="aw-u-met">cm &middot; kg</label></div></div>'
'<div class="aw-field aw-field-wide"><label class="aw-flabel" for="aw-h">Height</label>'
'<div class="aw-height"><button type="button" class="aw-step" id="aw-h-minus" aria-label="Shorter">&minus;</button><output id="aw-h-out" for="aw-h">5&prime; 4&Prime;</output><button type="button" class="aw-step" id="aw-h-plus" aria-label="Taller">+</button></div>'
'<input type="range" id="aw-h" min="54" max="80" step="1" value="64" aria-valuetext="5 feet 4 inches">'
'<div class="aw-scale" id="aw-scale"><span>4&prime;6&Prime;</span><span>5&prime;7&Prime;</span><span>6&prime;8&Prime;</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="aw-w">Weight <small>optional</small></label><div class="aw-input"><input type="number" id="aw-w" inputmode="decimal" min="50" max="700" step="0.1" placeholder="e.g. 165"><span id="aw-w-unit">lb</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="aw-age">Age <small>optional</small></label><div class="aw-select"><select id="aw-age"><option value="">Any age</option>'
+ "".join(f'<option value="{k}">{k}</option>' for k in M["age"]) +
'</select></div></div>'
'<button type="button" id="aw-go" class="aw-cta">Compare my weight</button></div>'
'<div id="aw-out" class="aw-out" hidden aria-live="polite"></div></section>')

def cell(v): return {"a": round(v["wt"]["mean"], 1), "q": [round(x, 1) for x in v["q"]], "c": [round(x, 1) for x in v["cdf"]], "n": v["wt"]["n"]}
TD = {"m": {str(h): cell(v) for h, v in HM.items()}, "f": {str(h): cell(v) for h, v in HF.items()},
      "avg": {"m": round(M["wt_lb"]["mean"], 1), "f": round(F["wt_lb"]["mean"], 1)},
      "age": {"m": {k: round(v["wt"]["mean"], 1) for k, v in M["age"].items()}, "f": {k: round(v["wt"]["mean"], 1) for k, v in F["age"].items()}},
      "hq": {"m": R["men"]["ht_q"], "f": R["women"]["ht_q"]}}

JS = r"""
(function(){var D=window.AW_DATA,$=function(i){return document.getElementById(i);};var sl=$('aw-h'),ho=$('aw-h-out'),wi=$('aw-w'),wu=$('aw-w-unit'),out=$('aw-out');
function units(){return document.querySelector('input[name="aw-u"]:checked').value;}function sexv(){return document.querySelector('input[name="aw-sex"]:checked').value;}
function bmiR(lb,h){return Math.round(lb*703/(h*h)*10+1e-9)/10;}
function band(h){var lo=null,hi=null;for(var lb=50;lb<450;lb++){var b=bmiR(lb,h);if(b>=18.5&&b<=24.9){if(lo===null)lo=lb;hi=lb;}}return [lo,hi];}
function cat(b){return b<18.5?['Underweight','#60A5FA']:b<25?['Healthy weight','#2E7D4F']:b<30?['Overweight','#E5743F']:['Obesity','#B3431A'];}
function ftin(h){var t=Math.round(h);return Math.floor(t/12)+'′ '+(t%12)+'″';}
function heightIn(){return units()==='imp'?+sl.value:(+sl.value)/2.54;}
function showH(){var u=units();if(u==='imp'){ho.textContent=ftin(+sl.value);sl.setAttribute('aria-valuetext',Math.floor(sl.value/12)+' feet '+(sl.value%12)+' inches');}else{ho.textContent=sl.value+' cm';sl.setAttribute('aria-valuetext',sl.value+' centimeters');}
 var p=(sl.value-sl.min)/(sl.max-sl.min)*100;sl.style.setProperty('--p',p.toFixed(1)+'%');}
sl.addEventListener('input',showH);
$('aw-h-minus').addEventListener('click',function(){sl.value=+sl.value-1;showH();});$('aw-h-plus').addEventListener('click',function(){sl.value=+sl.value+1;showH();});
document.querySelectorAll('input[name="aw-u"]').forEach(function(r){r.addEventListener('change',function(){var u=units(),h,w=parseFloat(wi.value);
 if(u==='met'){h=(+sl.value)*2.54;sl.min=137;sl.max=203;sl.step=1;sl.value=Math.round(h);$('aw-scale').innerHTML='<span>137 cm</span><span>170 cm</span><span>203 cm</span>';wu.textContent='kg';if(w>0)wi.value=(w*0.45359237).toFixed(1);wi.placeholder='e.g. 75';}
 else{h=(+sl.value)/2.54;sl.min=54;sl.max=80;sl.step=1;sl.value=Math.round(h);$('aw-scale').innerHTML='<span>4′6″</span><span>5′7″</span><span>6′8″</span>';wu.textContent='lb';if(w>0)wi.value=(w/0.45359237).toFixed(0);wi.placeholder='e.g. 165';}
 showH();});});
showH();
function pctOf(c,w){if(w<=c[0])return 5;if(w>=c[c.length-1])return 95;for(var i=1;i<c.length;i++){if(w<=c[i])return 5*i+5*(w-c[i-1])/(c[i]-c[i-1]);}return 95;}
function hpct(q,h){if(h<=q[0])return 1;if(h>=q[q.length-1])return 99;for(var i=1;i<q.length;i++){if(h<=q[i])return i+(h-q[i-1])/(q[i]-q[i-1]);}return 99;}
function ord(n){n=Math.round(n);var s=['th','st','nd','rd'],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0]);}
function nice(lo,hi){var span=hi-lo,st=span>200?50:span>100?25:span>50?20:10;return [Math.floor(lo/st)*st,Math.ceil(hi/st)*st,st];}
function distChart(cell,hb,w,sx){var cw=out.getBoundingClientRect().width||0,c=cell.c,W=cw>200?Math.max(330,Math.min(640,Math.round(cw-36))):640,P=W<480?22:36,PH=W<480?130:150,AX=30,pts=[],i;
 var lo=Math.min(c[0]-(c[1]-c[0]),hb[0]-5,w>0?w-10:1e9),hi=Math.max(c[18]+(c[18]-c[17]),hb[1]+5,w>0?w+10:-1e9),nx=nice(lo,hi);lo=nx[0];hi=nx[1];
 var X=function(v){return P+(v-lo)*(W-2*P)/(hi-lo);};
 var edges=[c[0]-(c[1]-c[0])].concat(c).concat([c[18]+(c[18]-c[17])]),cum=[];for(i=0;i<edges.length;i++)cum.push(i/(edges.length-1));
 function F(x){if(x<=edges[0])return 0;if(x>=edges[edges.length-1])return 1;for(var k=1;k<edges.length;k++){if(x<=edges[k])return cum[k-1]+(cum[k]-cum[k-1])*(x-edges[k-1])/Math.max(1e-6,edges[k]-edges[k-1]);}return 1;}
 var NG=90,gx=[],dens=[],dx=(edges[edges.length-1]-edges[0])/NG;for(i=0;i<=NG;i++){var xx=edges[0]+i*dx;gx.push(xx);dens.push((F(xx+dx)-F(xx-dx))/(2*dx));}
 for(var pass=0;pass<3;pass++){var sm=dens.slice();for(i=0;i<dens.length;i++){var a2=dens[Math.max(0,i-2)],a1=dens[Math.max(0,i-1)],b1=dens[Math.min(dens.length-1,i+1)],b2=dens[Math.min(dens.length-1,i+2)];sm[i]=(a2+4*a1+6*dens[i]+4*b1+b2)/16;}dens=sm;}
 var mx=Math.max.apply(null,dens);
 var labels=[{x:X((hb[0]+hb[1])/2),t:'Healthy range '+hb[0]+'–'+hb[1]+' lb',cl:'#2E7D4F'},{x:X(cell.a),t:'Average '+cell.a.toFixed(1)+' lb',cl:'#111827'}];if(w>0)labels.push({x:X(w),t:'You '+Math.round(w)+' lb',cl:'#C2481E'});
 labels.forEach(function(l){l.w=l.t.length*7.2+16;});labels.sort(function(a,b){return a.x-b.x;});
 var rows=[[],[],[]];labels.forEach(function(l){var lx=Math.min(Math.max(l.x-l.w/2,4),W-4-l.w);l.lx=lx;for(var r=0;r<3;r++){var ok=rows[r].every(function(o){return lx>o.lx+o.w+8||lx+l.w+8<o.lx;});if(ok){rows[r].push(l);l.r=r;break;}}if(l.r===undefined){l.r=2;rows[2].push(l);}});
 var nr=rows.filter(function(r){return r.length;}).length,LH=nr*24+6,top=LH,H=top+PH+AX,g='';
 var Y=function(d){return top+PH-(d/mx)*(PH-10);};
 g+='<rect x="'+X(hb[0]).toFixed(1)+'" y="'+top+'" width="'+(X(hb[1])-X(hb[0])).toFixed(1)+'" height="'+PH+'" fill="#CDE7D8" opacity=".75"/>';
 var path='M'+X(gx[0]).toFixed(1)+' '+(top+PH);for(i=0;i<dens.length;i++){path+=' L'+X(gx[i]).toFixed(1)+' '+Y(dens[i]).toFixed(1);}path+=' L'+X(gx[gx.length-1]).toFixed(1)+' '+(top+PH)+' Z';
 g+='<path d="'+path+'" fill="'+(sx==='m'?'#1F4E79':'#C2481E')+'" opacity=".22"/><path d="'+path.replace(/ Z$/,'')+'" fill="none" stroke="'+(sx==='m'?'#1F4E79':'#C2481E')+'" stroke-width="2"/>';
 g+='<line x1="'+P+'" x2="'+(W-P)+'" y1="'+(top+PH)+'" y2="'+(top+PH)+'" stroke="#9CA3AF"/>';
 var nt=nice(lo,hi),tstep=nt[2]*((W<480&&(nt[1]-nt[0])/nt[2]>6)?2:1);for(var t=nt[0];t<=nt[1];t+=tstep){g+='<line x1="'+X(t).toFixed(1)+'" x2="'+X(t).toFixed(1)+'" y1="'+(top+PH)+'" y2="'+(top+PH+5)+'" stroke="#9CA3AF"/><text x="'+X(t).toFixed(1)+'" y="'+(top+PH+21)+'" text-anchor="middle" class="aw-ax">'+t+'</text>';}
 g+='<line x1="'+X(cell.a).toFixed(1)+'" x2="'+X(cell.a).toFixed(1)+'" y1="'+top+'" y2="'+(top+PH)+'" stroke="#111827" stroke-width="2" stroke-dasharray="5 4"/>';
 if(w>0)g+='<line x1="'+X(w).toFixed(1)+'" x2="'+X(w).toFixed(1)+'" y1="'+top+'" y2="'+(top+PH)+'" stroke="#C2481E" stroke-width="3"/><circle cx="'+X(w).toFixed(1)+'" cy="'+(top+PH)+'" r="6" fill="#C2481E" stroke="#fff" stroke-width="2"/>';
 labels.forEach(function(l){var ly=4+l.r*24;g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+(ly+20)+'" y2="'+top+'" stroke="'+l.cl+'" stroke-width="1" opacity=".55"/>'+
  '<rect class="aw-lbl" data-r="'+l.r+'" data-x="'+l.lx.toFixed(1)+'" data-w="'+l.w.toFixed(1)+'" x="'+l.lx.toFixed(1)+'" y="'+ly+'" width="'+l.w.toFixed(1)+'" height="20" rx="10" fill="#fff" stroke="'+l.cl+'"/><text x="'+(l.lx+l.w/2).toFixed(1)+'" y="'+(ly+14)+'" text-anchor="middle" class="aw-lt" fill="'+l.cl+'">'+l.t+'</text>';});
 return '<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="Weight distribution of US '+(sx==='m'?'men':'women')+' at this height, with the healthy range'+(w>0?' and your weight':'')+'">'+g+'</svg>';}
function bar(lab,v,mx,col,me){return '<div class="aw-b'+(me?' aw-b-me':'')+'"><span class="aw-b-l">'+lab+'</span><span class="aw-b-t"><span class="aw-b-f" style="width:'+Math.max(3,v/mx*100).toFixed(1)+'%;background:'+col+'"></span></span><span class="aw-b-v">'+Math.round(v)+' lb</span></div>';}
function gauge(b){var lo=15,hi=42,X=function(v){return ((Math.min(Math.max(v,lo),hi)-lo)/(hi-lo)*100).toFixed(2)+'%';},segs=[[lo,18.5,'#93C5FD','Under'],[18.5,25,'#86EFAC','Healthy'],[25,30,'#FDBA74','Over'],[30,hi,'#FCA5A5','Obesity']];
 return '<div class="aw-g"><div class="aw-g-tr">'+segs.map(function(s){return '<span style="left:'+X(s[0])+';width:calc('+X(s[1])+' - '+X(s[0])+');background:'+s[2]+'"></span>';}).join('')+'<i style="left:'+X(b)+'"><b>'+b.toFixed(1)+'</b></i></div>'+
 '<div class="aw-g-nm">'+segs.map(function(s){return '<span style="left:calc(('+X(s[0])+' + '+X(s[1])+')/2)">'+s[3]+'</span>';}).join('')+'</div><div class="aw-g-ax"><span style="left:'+X(18.5)+'">18.5</span><span style="left:'+X(25)+'">25</span><span style="left:'+X(30)+'">30</span></div></div>';}
$('aw-go').addEventListener('click',function(){var sx=sexv(),u=units(),h=heightIn(),wv=parseFloat(wi.value),w=wv>0?(u==='imp'?wv:wv/0.45359237):0,age=$('aw-age').value;
 var who=sx==='m'?'men':'women',Who=sx==='m'?'Men':'Women',hi=Math.round(h),cell=D[sx][String(hi)],hb=band(h),html='';
 html+='<div class="aw-rh"><span class="aw-chip">'+Who+'</span><span class="aw-chip">'+ftin(h)+(u==='met'?' · '+Math.round(h*2.54)+' cm':'')+'</span>'+(w>0?'<span class="aw-chip">'+Math.round(w)+' lb'+(u==='met'?' · '+(w*0.45359237).toFixed(1)+' kg':'')+'</span>':'')+(age?'<span class="aw-chip">Age '+age+'</span>':'')+'</div>';
 var tiles=[];
 if(cell){tiles.push(['Average at your height',cell.a.toFixed(1)+' lb',(cell.a*0.45359237).toFixed(1)+' kg · '+cell.n+' measured'+(cell.n<60?' (small sample)':''),'#1F4E79']);}
 else tiles.push(['Average at your height','No data','fewer than 30 '+who+' measured at '+ftin(h),'#9CA3AF']);
 if(w>0&&cell){var pc=pctOf(cell.c,w);tiles.push(['Your rank at this height',(pc<=5?'≤5th':pc>=95?'≥95th':ord(pc)),'percentile among '+who+' within 1 inch','#C2481E']);}
 else if(cell)tiles.push(['Typical range','~'+Math.round(cell.q[0])+'–'+Math.round(cell.q[2])+' lb','middle half of '+who+' your height','#C2481E']);
 if(w>0){var b=bmiR(w,h),cc=cat(b);tiles.push(['Your BMI',b.toFixed(1),cc[0],cc[1]]);}else tiles.push(['Healthy range',hb[0]+'–'+hb[1]+' lb','BMI 18.5–24.9 at your height','#2E7D4F']);
 var hp=hpct(D.hq[sx],h);tiles.push(['Your height',ord(hp)+' pct',(hp>=50?'taller than '+Math.round(hp)+'%':'shorter than '+Math.round(100-hp)+'%')+' of US '+who,'#6B46C1']);
 html+='<div class="aw-tiles">'+tiles.map(function(t){return '<div class="aw-tile" style="--c:'+t[3]+'"><span class="aw-tile-l">'+t[0]+'</span><span class="aw-tile-n">'+t[1]+'</span><span class="aw-tile-s">'+t[2]+'</span></div>';}).join('')+'</div>';
 if(cell){html+='<h3 class="aw-h3">Where '+who+' your height fall</h3><div class="aw-dist">'+distChart(cell,hb,w,sx)+'</div><p class="aw-small">Shape: weights of US '+who+' within an inch of '+ftin(h)+' (middle 90% shown). Green: healthy range for your height.</p>';}
 var rowsB=[],mx=0;if(w>0)rowsB.push(['You',w,'#C2481E',true]);if(cell)rowsB.push(['Average at '+ftin(h),cell.a,'#1F4E79']);if(age&&D.age[sx][age])rowsB.push(['Average, '+who+' '+age,D.age[sx][age],'#6B46C1']);rowsB.push(['Average, all US '+who,D.avg[sx],'#6B7280']);rowsB.push(['Top of healthy range',hb[1],'#2E7D4F']);
 rowsB.forEach(function(r){mx=Math.max(mx,r[1]);});html+='<h3 class="aw-h3">Side by side</h3><div class="aw-bars">'+rowsB.map(function(r){return bar(r[0],r[1],mx,r[2],r[3]);}).join('')+'</div>';
 if(w>0){var bb=bmiR(w,h);html+='<h3 class="aw-h3">Your BMI on CDC’s scale</h3>'+gauge(bb);}
 var notes=[];
 if(cell){var d0=cell.a-hb[1];notes.push('The average for '+who+' your height is <strong>'+Math.round(d0)+' lb above</strong> the top of the healthy range'+(d0>0?'':'')+'.');
  if(w>0){var dd=w-cell.a;notes.push('You weigh <strong>'+Math.abs(Math.round(dd))+' lb '+(dd>=0?'more':'less')+'</strong> than that average, heavier than about '+Math.round(pctOf(cell.c,w))+'% of '+who+' within an inch of your height.');}
  if(cell.n<60)notes.push('Only '+cell.n+' '+who+' were measured at this height, so treat the average as a rough guide.');}
 else notes.push('CDC measured too few '+who+' at '+ftin(h)+' to give an average; the national average for '+who+' is <strong>'+D.avg[sx].toFixed(1)+' lb</strong>.');
 if(age&&D.age[sx][age])notes.push('Across all heights, '+who+' aged '+age+' average <strong>'+D.age[sx][age].toFixed(1)+' lb</strong>.');
 if(w>0){var bb2=bmiR(w,h);if(bb2>=25&&w<= (cell?cell.a:1e9))notes.push('Being at or below the average still means a BMI of '+bb2.toFixed(1)+' here, because the average itself is above the healthy range.');}
 html+='<ul class="aw-notes">'+notes.map(function(n){return '<li>'+n+'</li>';}).join('')+'</ul>';
 html+='<p class="cmb-src">Our calculation from CDC NHANES August 2021–August 2023 exam data (adults 20+, measured, survey-weighted). Percentiles use people within ±1 inch of your height; height rank uses all US adults of your sex.</p>';
 out.innerHTML=html;out.hidden=false;out.scrollIntoView({behavior:'smooth',block:'start'});});
})();
"""

CSS = """
.aw-cards{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 14px}
.aw-cards .aw-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}
@media (min-width:760px){.aw-cards .aw-kpi{flex:1 1 calc(25% - 10px)}}
.aw-kpi-l{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:#6B7280;font-weight:700}
.aw-kpi-n{font-size:1.9rem;font-weight:800;line-height:1.1;color:#111827}
.aw-kpi-s{font-size:.9rem;color:#374151}
.aw-tool{border-radius:20px;padding:0;margin:12px 0 18px;background:#fff;box-shadow:0 10px 34px rgba(17,24,39,.10);border:1px solid #EEF0F3;overflow:hidden}
.aw-tool-head{padding:18px 18px 12px;background:linear-gradient(135deg,#1F2937 0%,#1F4E79 100%);color:#fff}
.aw-tool-head h2{margin:0 0 4px;color:#fff;font-size:1.35rem}
.aw-tool-head p{margin:0;opacity:.85;font-size:.95rem}
.aw-form{display:flex;flex-wrap:wrap;gap:16px 18px;padding:18px}
.aw-field{display:flex;flex-direction:column;gap:8px;flex:1 1 200px;min-width:0}
.aw-field-wide{flex:1 1 100%}
.aw-flabel{font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#4B5563}
.aw-flabel small{font-weight:600;text-transform:none;letter-spacing:0;color:#9CA3AF;margin-left:4px}
.aw-pills{display:flex;background:#F3F4F6;border-radius:999px;padding:4px;gap:4px}
.aw-pills input{position:absolute;opacity:0;pointer-events:none}
.aw-pills label{flex:1;text-align:center;padding:10px 12px;min-height:22px;border-radius:999px;font-weight:700;color:#374151;cursor:pointer;transition:background .15s,color .15s,box-shadow .15s}
.aw-pills input:checked+label{background:#fff;color:#111827;box-shadow:0 2px 8px rgba(17,24,39,.15)}
.aw-pills input:focus-visible+label{outline:3px solid #93C5FD;outline-offset:1px}
.aw-height{display:flex;align-items:center;justify-content:center;gap:18px}
#aw-h-out{font-size:2.4rem;font-weight:800;font-variant-numeric:tabular-nums;color:#111827;min-width:150px;text-align:center}
.aw-step{width:48px;height:48px;border-radius:50%;border:2px solid #E5E7EB;background:#fff;font-size:1.6rem;font-weight:700;color:#1F2937;cursor:pointer;line-height:1}
.aw-step:hover{border-color:#1F4E79}
#aw-h{-webkit-appearance:none;appearance:none;width:100%;height:10px;border-radius:999px;background:linear-gradient(90deg,#1F4E79 0,#1F4E79 var(--p,40%),#E5E7EB var(--p,40%));outline:none;margin:6px 0 0}
#aw-h::-webkit-slider-thumb{-webkit-appearance:none;width:30px;height:30px;border-radius:50%;background:#fff;border:4px solid #1F4E79;box-shadow:0 2px 8px rgba(0,0,0,.25);cursor:pointer}
#aw-h::-moz-range-thumb{width:24px;height:24px;border-radius:50%;background:#fff;border:4px solid #1F4E79;box-shadow:0 2px 8px rgba(0,0,0,.25);cursor:pointer}
.aw-scale{display:flex;justify-content:space-between;font-size:.78rem;color:#9CA3AF}
.aw-input{display:flex;align-items:center;border:2px solid #E5E7EB;border-radius:14px;background:#fff;padding:0 14px;transition:border-color .15s,box-shadow .15s}
.aw-input:focus-within{border-color:#1F4E79;box-shadow:0 0 0 4px rgba(31,78,121,.15)}
.aw-input input{flex:1;border:0;outline:0;font-size:1.3rem;font-weight:700;padding:12px 0;min-width:0;background:transparent;color:#111827}
.aw-input span{font-weight:800;color:#6B7280}
.aw-select{position:relative}
.aw-select select{-webkit-appearance:none;appearance:none;width:100%;border:2px solid #E5E7EB;border-radius:14px;background:#fff;font-size:1.05rem;font-weight:700;padding:13px 40px 13px 14px;color:#111827;cursor:pointer}
.aw-select:after{content:"";position:absolute;right:16px;top:50%;width:9px;height:9px;border-right:3px solid #6B7280;border-bottom:3px solid #6B7280;transform:translateY(-70%) rotate(45deg);pointer-events:none}
.aw-select select:focus{border-color:#1F4E79;outline:0;box-shadow:0 0 0 4px rgba(31,78,121,.15)}
.aw-cta{flex:1 1 100%;min-height:54px;border:0;border-radius:14px;font-size:1.1rem;font-weight:800;color:#fff;cursor:pointer;background:linear-gradient(135deg,#C2481E 0%,#E5743F 100%);box-shadow:0 8px 20px rgba(194,72,30,.35)}
.aw-cta:hover{filter:brightness(1.05)}
.aw-out{padding:4px 18px 18px;border-top:1px solid #EEF0F3;background:linear-gradient(180deg,#FBFCFE 0%,#FFFFFF 100%)}
.aw-out[hidden]{display:none}
.aw-rh{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 12px}
.aw-chip{background:#F3F4F6;border-radius:999px;padding:6px 12px;font-weight:700;font-size:.9rem;color:#1F2937}
.aw-tiles{display:flex;flex-wrap:wrap;gap:10px}
.aw-tile{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border-radius:14px;padding:12px 14px;border:1px solid #EEF0F3;border-left:6px solid var(--c);box-shadow:0 3px 12px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}
@media (min-width:760px){.aw-tile{flex:1 1 calc(25% - 10px)}}
.aw-tile-l{font-size:.74rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;color:#6B7280}
.aw-tile-n{font-size:1.7rem;font-weight:800;color:#111827;line-height:1.15}
.aw-tile-s{font-size:.85rem;color:#4B5563}
.aw-h3{font-size:1.02rem;margin:20px 0 8px}
.aw-dist svg{display:block;width:100%;height:auto}
.aw-lt{font:700 12.5px system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.aw-dist svg .aw-ax{font-size:12px}
.aw-small{font-size:.83rem;color:#6B7280;margin:4px 0 0}
.aw-bars{display:flex;flex-direction:column;gap:8px}
.aw-b{display:flex;align-items:center;gap:10px;font-size:.93rem}
.aw-b-l{flex:0 0 42%;min-width:110px;color:#374151;line-height:1.2}
.aw-b-t{flex:1 1 auto;height:16px;border-radius:8px;background:#F3F4F6;overflow:hidden}
.aw-b-f{display:block;height:100%;border-radius:8px}
.aw-b-v{flex:0 0 64px;text-align:right;font-weight:800;font-variant-numeric:tabular-nums}
.aw-b-me .aw-b-l{font-weight:800;color:#111827}

.aw-g-tr{position:relative;height:28px;border-radius:14px;overflow:visible}
.aw-g-tr span{position:absolute;top:0;height:28px}
.aw-g-tr span:first-child{border-radius:14px 0 0 14px}.aw-g-tr span:nth-child(4){border-radius:0 14px 14px 0}
.aw-g{margin:30px 2px 4px}
.aw-g-tr i{position:absolute;top:-6px;width:6px;height:40px;margin-left:-3px;border-radius:3px;background:#111827;box-shadow:0 0 0 2px #fff}
.aw-g-tr i b{position:absolute;bottom:44px;left:50%;transform:translateX(-50%);background:#111827;color:#fff;font-size:.8rem;font-style:normal;padding:2px 8px;border-radius:999px;white-space:nowrap}
.aw-g-nm{position:relative;height:20px;font-size:.78rem;font-weight:800;color:#374151;margin-top:4px}
.aw-g-nm span{position:absolute;transform:translateX(-50%);white-space:nowrap}
.aw-g-ax{position:relative;height:18px;font-size:.75rem;color:#6B7280}
.aw-g-ax span{position:absolute;transform:translateX(-50%);top:2px}
.aw-notes{margin:16px 0 6px;padding-left:1.2em}
.aw-notes li{margin:6px 0}
.aw-fig{margin:16px auto;max-width:760px}
.aw-sm{display:flex;flex-wrap:wrap;gap:12px 20px}
.aw-sm-p{flex:1 1 300px;min-width:0}
.aw-sm-p svg{display:block;width:100%;height:auto}
.aw-sm-t{margin:0 0 4px;font-weight:800;color:var(--c)}
.aw-key{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;padding:0;margin:8px 0 0;font-size:.85rem;color:#374151}
.aw-key li{display:flex;align-items:center;gap:8px}
.aw-key-l{display:inline-block;width:22px;height:4px;border-radius:2px;background:#6B7280}
.aw-key-g{display:inline-block;width:18px;height:14px;border-radius:3px;background:#CDE7D8}
.aw-ax{font:13px system-ui,sans-serif;fill:#6B7280}
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
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Data: CDC NHANES August 2021&ndash;August 2023, our calculation from the exam files &middot; Reviewed October 4, 2026 &middot; Not medical advice</p>',
'<p class="cmb-intro">What do American adults actually weigh at your height? We calculated it from CDC&rsquo;s raw exam data &mdash; people weighed on a scale, not asked &mdash; and checked our method by reproducing CDC&rsquo;s own published averages to the decimal.</p>',
TOOL_HTML,
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
f'<figure class="aw-fig">{chart()}<figcaption>Average weight by height for US women and men, against the healthy-weight range for each height. Our calculation from CDC NHANES August 2021–August 2023.</figcaption></figure>',
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
  "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}, "datePublished": "2026-10-03", "dateModified": "2026-10-04",
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
