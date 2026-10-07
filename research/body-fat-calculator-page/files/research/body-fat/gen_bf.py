#!/usr/bin/env python3
"""Build /body-fat-percentage-chart/ from bf_results.json (compute_bf.py: NHANES 2011-2018 DXA whole body, DEMO, BMX;
pooled weights WTMEC2YR/4; pregnant excluded; Taylor-linearised SEs). Method check: reproduces Liu et al., BMJ 2021,
Table 3 age-adjusted mean body fat for all four cycles (32.6 / 33.1 / 32.9 / 33.0%) with the identical n = 10,864."""
import json, os, re, sys, csv, html as H
ROOT, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "bf_results.json")))
AWCSS = open(os.path.join(HERE, "aw_css.txt"), encoding="utf-8").read()
SLUG = "body-fat-percentage-chart"; URL = f"https://calculatemybmi.net/{SLUG}/"
DXX = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm"
BMJ = "https://pmc.ncbi.nlm.nih.gov/articles/PMC7961695/"
GAL = "https://pubmed.ncbi.nlm.nih.gov/10966886/"
GALT = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5349253/table/table001"
CSVF = "body-fat-percentiles-nhanes-2011-2018.csv"
f1 = lambda v: f"{v:.1f}"
M, F = R["m"], R["f"]
assert R["meta"]["n_adults"] == 10864
AGES = ["20-29", "30-39", "40-49", "50-59"]; TEENS = ["8-11", "12-15", "16-19"]
lab = lambda k: k.replace("-", "–")
# Gallagher-based provisional ranges (low < a <= normal < b <= high < c <= very high), as tabulated in PMC5349253 Table 1
GALR = {"f": {"20-39": (21, 33, 39), "40-59": (23, 34, 40), "60-79": (24, 36, 42)}, "m": {"20-39": (8, 20, 25), "40-59": (11, 22, 28), "60-79": (13, 25, 30)}}
def pct_of(cdf, v):
    if v <= cdf[0]: return 1
    if v >= cdf[-1]: return 99
    for i in range(1, len(cdf)):
        if v <= cdf[i]: return i + (v - cdf[i - 1]) / (cdf[i] - cdf[i - 1])
    return 99
mm, ff = M["20-59"], F["20-59"]
# derived statements, guarded
rise_m = M["50-59"]["mean"] - M["20-29"]["mean"]; rise_f = F["50-59"]["mean"] - F["20-29"]["mean"]
assert all(M[a]["mean"] < M[b]["mean"] for a, b in zip(AGES, AGES[1:])) and all(F[a]["mean"] < F[b]["mean"] for a, b in zip(AGES, AGES[1:]))
bm, bf = M["by_bmi"], F["by_bmi"]
assert M["8-11"]["mean"] > M["12-15"]["mean"] > M["16-19"]["mean"] and F["8-11"]["mean"] < F["12-15"]["mean"] < F["16-19"]["mean"]
assert all(S[g]["p"][9] >= GALR[k][g][1] for k, S in (("m", M), ("f", F)) for g in ("20-39", "40-59")), "median not above healthy band"
assert 20 >= GALR["m"]["20-39"][1] and GALR["m"]["40-59"][0] <= 20 < GALR["m"]["40-59"][1] and all(GALR["f"][g][0] <= 30 < GALR["f"][g][1] for g in ("20-39", "40-59"))

# ---------- charts ----------
def pct_chart(S, col, who):
    groups = TEENS + AGES; W, Hh, L, B, T, Rr = 380, 300, 40, 40, 12, 10
    y0, y1 = 5, 55; n = len(groups); bw = (W - L - Rr) / n
    X = lambda i: L + bw * (i + 0.5); Y = lambda v: Hh - B - (v - y0) * (Hh - T - B) / (y1 - y0)
    g = []
    for v in range(10, 56, 10):
        g.append(f'<line x1="{L}" x2="{W - Rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#EEF0F3"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" class="bf-ax">{v}%</text>')
    for i, k in enumerate(groups):
        p = S[k]["p"]  # 5%..95% by 5
        x = X(i); w = bw * 0.56
        g.append(f'<rect x="{x - w / 2:.1f}" y="{Y(p[17]):.1f}" width="{w:.1f}" height="{Y(p[1]) - Y(p[17]):.1f}" rx="4" fill="{col}" opacity=".18"/>')
        g.append(f'<rect x="{x - w / 2:.1f}" y="{Y(p[14]):.1f}" width="{w:.1f}" height="{Y(p[4]) - Y(p[14]):.1f}" rx="4" fill="{col}" opacity=".45"/>')
        g.append(f'<line x1="{x - w / 2:.1f}" x2="{x + w / 2:.1f}" y1="{Y(p[9]):.1f}" y2="{Y(p[9]):.1f}" stroke="{col}" stroke-width="3"><title>{who} {lab(k)}: median {f1(p[9])}%</title></line>')
        g.append(f'<text x="{x:.1f}" y="{Hh - B + 16}" text-anchor="middle" class="bf-ax">{lab(k)}</text>')
    g.append(f'<line x1="{L + bw * 3:.1f}" x2="{L + bw * 3:.1f}" y1="{T}" y2="{Hh - B}" stroke="#D1D5DB" stroke-dasharray="4 4"/>')
    g.append(f'<text x="{L + bw * 1.5:.1f}" y="{Hh - 8}" text-anchor="middle" class="bf-ax-s">children &amp; teens</text><text x="{L + bw * 5:.1f}" y="{Hh - 8}" text-anchor="middle" class="bf-ax-s">adults</text>')
    return f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-label="Body fat percentage of US {who.lower()} by age group: median and middle ranges, NHANES 2011–2018">' + "".join(g) + "</svg>"

def bmi_chart(S, col, who):
    cats = ["18.5–24.9", "25–29.9", "30+"]; W, Hh, L, B, T, Rr = 380, 260, 40, 40, 12, 10
    y0, y1 = (10, 45) if who == "Men" else (20, 55)
    bw = (W - L - Rr) / 3; X = lambda i: L + bw * (i + 0.5); Y = lambda v: Hh - B - (v - y0) * (Hh - T - B) / (y1 - y0)
    g = []
    for v in range(y0, y1 + 1, 5):
        g.append(f'<line x1="{L}" x2="{W - Rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#EEF0F3"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" class="bf-ax">{v}%</text>')
    for i, c in enumerate(cats):
        q = S["by_bmi"][c]["q"]; x = X(i); w = bw * 0.42
        g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{Y(q[4]):.1f}" y2="{Y(q[0]):.1f}" stroke="{col}" stroke-width="2"/>')
        g.append(f'<rect x="{x - w / 2:.1f}" y="{Y(q[3]):.1f}" width="{w:.1f}" height="{Y(q[1]) - Y(q[3]):.1f}" rx="5" fill="{col}" opacity=".35" stroke="{col}"/>')
        g.append(f'<line x1="{x - w / 2:.1f}" x2="{x + w / 2:.1f}" y1="{Y(q[2]):.1f}" y2="{Y(q[2]):.1f}" stroke="{col}" stroke-width="3"><title>BMI {c}: median body fat {f1(q[2])}%</title></line>')
        g.append(f'<text x="{x:.1f}" y="{Hh - B + 18}" text-anchor="middle" class="bf-ax">BMI {c}</text>')
    return f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-label="Body fat of US {who.lower()} 20–59 within each BMI category, NHANES 2011–2018">' + "".join(g) + "</svg>"

def pct_table(S, who):
    rows = ""
    for k in AGES + TEENS:
        p = S[k]["p"]
        rows += f'<tr id="{who.lower()}-{k}"><th scope="row">{lab(k)}</th>' + "".join(f"<td>{f1(p[i])}%</td>" for i in (1, 4, 9, 14, 17)) + f'<td><strong>{f1(S[k]["mean"])}%</strong></td><td>{S[k]["n"]:,}</td></tr>'
    return (f'<div class="cmb-table-wrap"><table><caption>Body fat percentage of US {who.lower()} by age (DXA scans, NHANES 2011–2018)</caption><thead><tr><th scope="col">Age</th><th scope="col">10th</th><th scope="col">25th</th><th scope="col">Median</th><th scope="col">75th</th><th scope="col">90th</th><th scope="col">Average</th><th scope="col">People scanned</th></tr></thead><tbody>{rows}</tbody></table></div>')

def rank_table(S, vals, who):
    rows = ""
    for v in vals:
        a, b = pct_of(S["20-39"]["cdf"], v), pct_of(S["40-59"]["cdf"], v)
        rows += f'<tr id="{who.lower()}-{v}-percent"><th scope="row">{v}%</th><td>{round(100 - a)}%</td><td>{round(100 - b)}%</td></tr>'
    return (f'<div class="cmb-table-wrap"><table><caption>What a given body fat percentage means for US {who.lower()}: share with more body fat (DXA, 2011–2018)</caption><thead><tr><th scope="col">Body fat</th><th scope="col">{who} 20–39 with more</th><th scope="col">{who} 40–59 with more</th></tr></thead><tbody>{rows}</tbody></table></div>')

def gal_table():
    rows = ""
    for sx, who in (("f", "Women"), ("m", "Men")):
        for g, (a, b, c) in GALR[sx].items():
            rows += f"<tr><th scope='row'>{who} {lab(g)}</th><td>under {a}%</td><td>{a}–{b - 0.1:.1f}%</td><td>{b}–{c - 0.1:.1f}%</td><td>{c}% or more</td></tr>"
    return ("<div class='cmb-table-wrap'><table><caption>Provisional body fat ranges matched to BMI categories (Gallagher et al., 2000)</caption><thead><tr><th scope='col'></th><th scope='col'>Low (BMI under 18.5)</th><th scope='col'>Healthy (BMI 18.5–24.9)</th><th scope='col'>High (BMI 25–29.9)</th><th scope='col'>Very high (BMI 30+)</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")

# ---------- tool ----------
TD = {"m": {k: {"c": M[k]["cdf"], "p": M[k]["p"], "n": M[k]["n"]} for k in TEENS + AGES}, "f": {k: {"c": F[k]["cdf"], "p": F[k]["p"], "n": F[k]["n"]} for k in TEENS + AGES},
      "gal": GALR, "med": {"m": round(mm["p"][9], 1), "f": round(ff["p"][9], 1)}}
TOOL_HTML = (
'<section class="aw-tool" aria-label="Where does your body fat rank">'
'<div class="aw-tool-head"><h2>Where does your body fat rank?</h2><p>Compare your body fat percentage with Americans of your sex and age, measured by CDC body scans.</p></div>'
'<div class="aw-form">'
'<div class="aw-field"><span class="aw-flabel" id="bf-sex-l">I am</span><div class="aw-pills" role="radiogroup" aria-labelledby="bf-sex-l">'
'<input type="radio" id="bf-sx-f" name="bf-sex" value="f" checked><label for="bf-sx-f">Woman</label><input type="radio" id="bf-sx-m" name="bf-sex" value="m"><label for="bf-sx-m">Man</label></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="bf-v">Body fat <small>from a scan, scale or calipers</small></label><div class="aw-input"><input type="number" id="bf-v" inputmode="decimal" min="3" max="65" step="0.1" placeholder="e.g. 24"><span>%</span></div></div>'
'<div class="aw-field aw-field-wide"><label class="aw-flabel" for="bf-a">Age</label>'
'<div class="aw-height"><button type="button" class="aw-step" id="bf-a-minus" aria-label="Younger">&minus;</button><output id="bf-a-out" for="bf-a">35 years</output><button type="button" class="aw-step" id="bf-a-plus" aria-label="Older">+</button></div>'
'<input type="range" id="bf-a" min="8" max="79" step="1" value="35" aria-valuetext="35 years"><div class="aw-scale"><span>8</span><span>40</span><span>79</span></div></div>'
'<button type="button" id="bf-go" class="aw-cta">See where I rank</button></div>'
'<div id="bf-out" class="aw-out" hidden aria-live="polite"></div></section>')
JS = r"""
(function(){var D=window.BF_DATA,$=function(i){return document.getElementById(i);},sl=$('bf-a'),ao=$('bf-a-out'),vi=$('bf-v'),out=$('bf-out');
function sexv(){return document.querySelector('input[name="bf-sex"]:checked').value;}
function showA(){ao.textContent=sl.value+' years';sl.setAttribute('aria-valuetext',sl.value+' years');sl.style.setProperty('--p',((sl.value-sl.min)/(sl.max-sl.min)*100).toFixed(1)+'%');}
sl.addEventListener('input',showA);$('bf-a-minus').addEventListener('click',function(){sl.value=+sl.value-1;showA();});$('bf-a-plus').addEventListener('click',function(){sl.value=+sl.value+1;showA();});showA();
function grp(a){return a<=11?'8-11':a<=15?'12-15':a<=19?'16-19':a<=29?'20-29':a<=39?'30-39':a<=49?'40-49':a<=59?'50-59':null;}
function ggrp(a){return a>=20&&a<=39?'20-39':a>=40&&a<=59?'40-59':a>=60&&a<=79?'60-79':null;}
function pctOf(c,v){if(v<=c[0])return 1;if(v>=c[c.length-1])return 99;for(var i=1;i<c.length;i++){if(v<=c[i])return i+(v-c[i-1])/(c[i]-c[i-1]);}return 99;}
function lb(k){return k.replace('-','–');}
function dist(c,v,gb,sx,W){var P=W<480?22:36,PH=W<480?130:150,lo=Math.max(0,Math.floor(Math.min(c[0],gb?gb[0]:99,v>0?v:99)/5)*5-5),hi=Math.min(70,Math.ceil(Math.max(c[98],gb?gb[1]:0,v>0?v:0)/5)*5+5),i;
 var X=function(x){return P+(x-lo)*(W-2*P)/(hi-lo);},NG=90,dx=(hi-lo)/NG,gx=[],dens=[];
 function F(x){if(x<=c[0])return 0.01*Math.max(0,(x-(c[0]-(c[1]-c[0])*3))/((c[1]-c[0])*3));if(x>=c[98])return Math.min(1,0.99+0.01*(x-c[98])/((c[98]-c[97])*3));for(var k=1;k<c.length;k++){if(x<=c[k])return (k+(x-c[k-1])/(c[k]-c[k-1]))/100;}return 1;}
 for(i=0;i<=NG;i++){var xx=lo+i*dx;gx.push(xx);dens.push((F(xx+dx)-F(xx-dx))/(2*dx));}
 for(var p=0;p<3;p++){var sm=dens.slice();for(i=0;i<dens.length;i++){var a2=dens[Math.max(0,i-2)],a1=dens[Math.max(0,i-1)],b1=dens[Math.min(dens.length-1,i+1)],b2=dens[Math.min(dens.length-1,i+2)];sm[i]=(a2+4*a1+6*dens[i]+4*b1+b2)/16;}dens=sm;}
 var mx=Math.max.apply(null,dens),med=c[49];
 var labels=[{x:X(med),t:'Median '+med.toFixed(1)+'%',cl:'#111827'}];if(gb)labels.push({x:X((gb[0]+gb[1])/2),t:'Healthy range '+gb[0]+'–'+(gb[1]-0.1).toFixed(1)+'%',cl:'#2E7D4F'});if(v>0)labels.push({x:X(v),t:'You '+v.toFixed(1)+'%',cl:'#C2481E'});
 labels.forEach(function(l){l.w=l.t.length*7.2+16;});labels.sort(function(a,b){return a.x-b.x;});
 var rows=[[],[],[]];labels.forEach(function(l){var lx=Math.min(Math.max(l.x-l.w/2,4),W-4-l.w);l.lx=lx;for(var r=0;r<3;r++){if(rows[r].every(function(o){return lx>o.lx+o.w+8||lx+l.w+8<o.lx;})){rows[r].push(l);l.r=r;break;}}if(l.r===undefined){l.r=2;rows[2].push(l);}});
 var nr=rows.filter(function(r){return r.length;}).length,top=nr*24+6,H=top+PH+30,g='',Y=function(d){return top+PH-(d/mx)*(PH-10);},col=sx==='m'?'#1F4E79':'#C2481E';
 if(gb)g+='<rect x="'+X(gb[0]).toFixed(1)+'" y="'+top+'" width="'+(X(gb[1])-X(gb[0])).toFixed(1)+'" height="'+PH+'" fill="#CDE7D8" opacity=".75"/>';
 var path='M'+X(gx[0]).toFixed(1)+' '+(top+PH);for(i=0;i<dens.length;i++)path+=' L'+X(gx[i]).toFixed(1)+' '+Y(dens[i]).toFixed(1);path+=' L'+X(gx[gx.length-1]).toFixed(1)+' '+(top+PH)+' Z';
 g+='<path d="'+path+'" fill="'+col+'" opacity=".22"/><path d="'+path.replace(/ Z$/,'')+'" fill="none" stroke="'+col+'" stroke-width="2"/>';
 g+='<line x1="'+P+'" x2="'+(W-P)+'" y1="'+(top+PH)+'" y2="'+(top+PH)+'" stroke="#9CA3AF"/>';
 var st=(hi-lo)>40&&W<480?10:5;for(var t=lo;t<=hi;t+=st){g+='<text x="'+X(t).toFixed(1)+'" y="'+(top+PH+21)+'" text-anchor="middle" class="aw-ax">'+t+'%</text>';}
 g+='<line x1="'+X(med).toFixed(1)+'" x2="'+X(med).toFixed(1)+'" y1="'+top+'" y2="'+(top+PH)+'" stroke="#111827" stroke-width="2" stroke-dasharray="5 4"/>';
 if(v>0)g+='<line x1="'+X(v).toFixed(1)+'" x2="'+X(v).toFixed(1)+'" y1="'+top+'" y2="'+(top+PH)+'" stroke="#C2481E" stroke-width="3"/><circle cx="'+X(v).toFixed(1)+'" cy="'+(top+PH)+'" r="6" fill="#C2481E" stroke="#fff" stroke-width="2"/>';
 labels.forEach(function(l){var ly=4+l.r*24;g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+(ly+20)+'" y2="'+top+'" stroke="'+l.cl+'" stroke-width="1" opacity=".55"/><rect class="aw-lbl" data-r="'+l.r+'" data-x="'+l.lx.toFixed(1)+'" data-w="'+l.w.toFixed(1)+'" x="'+l.lx.toFixed(1)+'" y="'+ly+'" width="'+l.w.toFixed(1)+'" height="20" rx="10" fill="#fff" stroke="'+l.cl+'"/><text x="'+(l.lx+l.w/2).toFixed(1)+'" y="'+(ly+14)+'" text-anchor="middle" class="aw-lt" fill="'+l.cl+'">'+l.t+'</text>';});
 return '<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="Body fat distribution for this group with the median'+(gb?', the provisional healthy range':'')+(v>0?' and your value':'')+'">'+g+'</svg>';}
function bar(l,v,mx,col,me){return '<div class="aw-b'+(me?' aw-b-me':'')+'"><span class="aw-b-l">'+l+'</span><span class="aw-b-t"><span class="aw-b-f" style="width:'+Math.max(3,v/mx*100).toFixed(1)+'%;background:'+col+'"></span></span><span class="aw-b-v">'+v.toFixed(1)+'%</span></div>';}
$('bf-go').addEventListener('click',function(){var sx=sexv(),a=+sl.value,v=parseFloat(vi.value),k=grp(a),gk=ggrp(a),who=sx==='m'?'men':'women',Who=sx==='m'?'Men':'Women',html='',cw=out.getBoundingClientRect().width||0,W=cw>200?Math.max(330,Math.min(640,Math.round(cw-36))):640;
 if(!(v>0))v=0;if(v&&(v<3||v>65)){out.innerHTML='<p class="aw-err">Enter a body fat percentage between 3 and 65.</p>';out.hidden=false;return;}
 var gb=gk?D.gal[sx][gk]:null,gh=gb?[gb[0],gb[1]]:null;
 html+='<div class="aw-rh"><span class="aw-chip">'+Who+'</span><span class="aw-chip">Age '+a+'</span>'+(v?'<span class="aw-chip">'+v.toFixed(1)+'% body fat</span>':'')+'</div>';
 var tiles=[],S=k?D[sx][k]:null;
 if(S){if(v){var p=pctOf(S.c,v),more=Math.round(100-p);tiles.push(['Your rank',more+'%','of US '+who+' '+lb(k)+' have more body fat than you','#C2481E']);}
  tiles.push(['Median, '+who+' '+lb(k),S.p[9].toFixed(1)+'%','half are above, half below · '+S.n.toLocaleString('en-US')+' scanned','#1F4E79']);
  tiles.push(['Middle half',S.p[4].toFixed(0)+'–'+S.p[14].toFixed(0)+'%','25th to 75th percentile','#6B46C1']);}
 else tiles.push(['No scan data',a>=60?'Ages 60+':'–','CDC’s 2011–2018 body scans covered ages 8–59','#9CA3AF']);
 if(gb){var cl=v?(v<gb[0]?['Low','#60A5FA']:v<gb[1]?['Healthy','#2E7D4F']:v<gb[2]?['High','#E5743F']:['Very high','#B3431A']):null;
  tiles.push(['Provisional healthy range',gb[0]+'–'+(gb[1]-0.1).toFixed(1)+'%',(cl?'Your value: '+cl[0].toLowerCase():'for '+who+' '+lb(gk))+' (Gallagher 2000)',cl?cl[1]:'#2E7D4F']);}
 else if(a<20)tiles.push(['Healthy range','Not defined','the adult ranges don’t apply under 20','#9CA3AF']);
 html+='<div class="aw-tiles">'+tiles.map(function(t){return '<div class="aw-tile" style="--c:'+t[3]+'"><span class="aw-tile-l">'+t[0]+'</span><span class="aw-tile-n">'+t[1]+'</span><span class="aw-tile-s">'+t[2]+'</span></div>';}).join('')+'</div>';
 if(S){html+='<h3 class="aw-h3">Body fat of US '+who+' aged '+lb(k)+'</h3><div class="aw-dist">'+dist(S.c,v,gh,sx,W)+'</div><p class="aw-small">Shape: DXA body scans of US '+who+' '+lb(k)+' (NHANES 2011–2018).'+(gh?' Green: provisional healthy range for your age.':'')+'</p>';
  var rows=[];if(v)rows.push(['You',v,'#C2481E',true]);rows.push(['Median, '+who+' '+lb(k),S.p[9],'#1F4E79']);rows.push(['25th percentile',S.p[4],'#93C5FD']);rows.push(['75th percentile',S.p[14],'#6B46C1']);rows.push(['Median, all US '+who+' 20–59',D.med[sx],'#6B7280']);
  var mx=0;rows.forEach(function(r){mx=Math.max(mx,r[1]);});html+='<h3 class="aw-h3">Side by side</h3><div class="aw-bars">'+rows.map(function(r){return bar(r[0],r[1],mx,r[2],r[3]);}).join('')+'</div>';}
 var notes=[];
 if(S&&v){var d=v-S.p[9];notes.push('You are <strong>'+Math.abs(d).toFixed(1)+' points '+(d>=0?'above':'below')+'</strong> the median for '+who+' your age.');}
 if(gb&&v){var lo2=gb[0],hi2=gb[1];notes.push(v<lo2?'Below the provisional healthy range for your age ('+lo2+'% and up).':v<hi2?'Inside the provisional healthy range for your age.':'Above the provisional healthy range for your age (under '+hi2+'%).');}
 if(S&&gb)notes.push('Most US '+who+' your age are above that range: the median, '+S.p[9].toFixed(1)+'%, sits '+(S.p[9]>=gb[1]?'above':'inside')+' it.');
 notes.push('Home scales, calipers and tape methods can read several points away from a DXA scan, so treat your rank as approximate.');
 html+='<ul class="aw-notes">'+notes.map(function(n){return '<li>'+n+'</li>';}).join('')+'</ul><p class="cmb-src">Our calculation from CDC NHANES 2011–2018 DXA body scans (ages 8–59, survey-weighted). Provisional healthy ranges: Gallagher et al., 2000.</p>';
 out.innerHTML=html;out.hidden=false;out.scrollIntoView({behavior:'smooth',block:'start'});});
})();
"""
CSS = AWCSS.replace("#aw-h-out{","#aw-h-out,#bf-a-out{").replace("#aw-h{","#aw-h,#bf-a{").replace("#aw-h::-webkit-slider-thumb{","#aw-h::-webkit-slider-thumb,#bf-a::-webkit-slider-thumb{").replace("#aw-h::-moz-range-thumb{","#aw-h::-moz-range-thumb,#bf-a::-moz-range-thumb{") + """
.bf-cards{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 14px}
.bf-cards .bf-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}
@media (min-width:760px){.bf-cards .bf-kpi{flex:1 1 calc(25% - 10px)}}
.bf-kpi-l{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:#6B7280;font-weight:700}
.bf-kpi-n{font-size:1.9rem;font-weight:800;line-height:1.1;color:#111827}
.bf-kpi-s{font-size:.9rem;color:#374151}
.bf-sm{display:flex;flex-wrap:wrap;gap:12px 20px;margin:12px 0}
.bf-sm-p{flex:1 1 300px;min-width:0}
.bf-sm-p svg{display:block;width:100%;height:auto}
.bf-sm-t{margin:0 0 4px;font-weight:800;color:var(--c)}
.bf-key{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;padding:0;margin:6px 0 0;font-size:.85rem;color:#374151}
.bf-key li{display:flex;align-items:center;gap:8px;margin-right:6px}
.bf-k1{display:inline-block;width:16px;height:14px;border-radius:3px;background:#6B7280;opacity:.2}
.bf-k2{display:inline-block;width:16px;height:14px;border-radius:3px;background:#6B7280;opacity:.5}
.bf-k3{display:inline-block;width:18px;height:3px;background:#374151}
.bf-ax{font:12px system-ui,sans-serif;fill:#6B7280}
.bf-ax-s{font:11px system-ui,sans-serif;fill:#9CA3AF}
.bf-cols{display:flex;flex-wrap:wrap;gap:4px 24px}
.bf-cols>div{flex:1 1 300px;min-width:0}
"""
def P(*a): return "\n".join(a)
key = '<ul class="bf-key"><li><span class="bf-k1"></span>10th–90th percentile</li><li><span class="bf-k2"></span>25th–75th</li><li><span class="bf-k3"></span>Median</li></ul>'
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <span>Body Fat Percentage Chart</span></nav>',
'<article class="cmb-stats">',
'<h1>Body Fat Percentage Chart for Men and Women</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Data: CDC NHANES 2011&ndash;2018 body scans, our calculation &middot; Reviewed October 4, 2026 &middot; Not medical advice</p>',
'<p class="cmb-intro">Many body fat charts online use fitness-industry tiers without a stated data source. This one is built from what Americans actually measure: CDC&rsquo;s DXA body scans, the most widely accepted way to measure body composition. We checked our method by reproducing a peer-reviewed analysis of the same scans to the decimal.</p>',
TOOL_HTML,
f'<div class="bf-cards"><div class="bf-kpi" style="--c:#1F4E79"><span class="bf-kpi-l">Average man, 20–59</span><span class="bf-kpi-n">{f1(mm["mean"])}%</span><span class="bf-kpi-s">median {f1(mm["p"][9])}%</span></div>'
f'<div class="bf-kpi" style="--c:#C2481E"><span class="bf-kpi-l">Average woman, 20–59</span><span class="bf-kpi-n">{f1(ff["mean"])}%</span><span class="bf-kpi-s">median {f1(ff["p"][9])}%</span></div>'
f'<div class="bf-kpi" style="--c:#2E7D4F"><span class="bf-kpi-l">Healthy range, 20–39</span><span class="bf-kpi-n">8–19.9%</span><span class="bf-kpi-s">men · women 21–32.9% (provisional)</span></div>'
f'<div class="bf-kpi" style="--c:#6B46C1"><span class="bf-kpi-l">Healthy BMI, median fat</span><span class="bf-kpi-n">{f1(bm["18.5–24.9"]["q"][2])} / {f1(bf["18.5–24.9"]["q"][2])}%</span><span class="bf-kpi-s">men / women with BMI 18.5–24.9</span></div></div>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>The average American man aged 20–59 has {f1(mm["mean"])}% body fat and the average woman {f1(ff["mean"])}%</strong>, measured by DXA body scans in CDC&rsquo;s 2011&ndash;2018 surveys. Body fat rises with age, from {f1(M["20-29"]["mean"])}% in men in their 20s to {f1(M["50-59"]["mean"])}% in their 50s, and from {f1(F["20-29"]["mean"])}% to {f1(F["50-59"]["mean"])}% in women. Provisional healthy ranges matched to BMI are 8&ndash;19.9% for men and 21&ndash;32.9% for women aged 20&ndash;39.</p>',
f'<p class="cmb-src">Source: our calculation from CDC <a href="{DXX}" rel="noopener">NHANES DXA body scans</a>, 2011&ndash;2018; healthy ranges from <a href="{GAL}" rel="noopener">Gallagher et al., 2000</a>.</p>',
'</div>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol><li><a href="#chart">Body fat percentage chart by age</a></li><li><a href="#men">Body fat percentage for men</a></li><li><a href="#women">Body fat percentage for women</a></li><li><a href="#what-it-means">What your body fat percentage means</a></li><li><a href="#healthy">Healthy body fat percentage</a></li><li><a href="#bmi">Body fat vs BMI</a></li><li><a href="#faq">FAQ</a></li><li><a href="#method">How we calculated this</a></li></ol></nav>',
'<h2 id="chart">Body fat percentage chart by age</h2>',
f'<p><strong>Women carry more body fat than men at every age, and both rise through adulthood.</strong> Among adults, the average climbs about {f1(rise_m)} points for men and {f1(rise_f)} points for women between their 20s and 50s. Children show the opposite pattern by sex: boys&rsquo; body fat falls through the teens while girls&rsquo; rises.</p>',
f'<figure class="aw-fig"><div class="bf-sm"><div class="bf-sm-p"><p class="bf-sm-t" style="--c:#1F4E79">Men and boys</p>{pct_chart(M, "#1F4E79", "Men")}</div><div class="bf-sm-p"><p class="bf-sm-t" style="--c:#C2481E">Women and girls</p>{pct_chart(F, "#C2481E", "Women")}</div></div>{key}<figcaption>Body fat percentage by age group, DXA body scans, NHANES 2011&ndash;2018 (our calculation). CDC scanned ages 8&ndash;59 only.</figcaption></figure>',
'<h2 id="men">Body fat percentage for men</h2>',
f'<p>Half of US men aged 20&ndash;39 are between {f1(M["20-39"]["p"][4])}% and {f1(M["20-39"]["p"][14])}% body fat; the leanest tenth are under {f1(M["20-39"]["p"][1])}%. The table gives each age group&rsquo;s spread, so you can see what&rsquo;s typical for your age rather than for an athlete.</p>',
pct_table(M, "Men"),
'<h2 id="women">Body fat percentage for women</h2>',
f'<p>Half of US women aged 20&ndash;39 are between {f1(F["20-39"]["p"][4])}% and {f1(F["20-39"]["p"][14])}% body fat; the leanest tenth are under {f1(F["20-39"]["p"][1])}%. Their provisional healthy ranges sit 11 to 13 points above men&rsquo;s at every age.</p>',
pct_table(F, "Women"),
'<h2 id="what-it-means">What your body fat percentage means</h2>',
'<p>Many people search a single number &mdash; &ldquo;is 20% body fat good for a man?&rdquo; These tables answer it with real data: the share of US adults your sex and age with more body fat than that number. Don&rsquo;t know your number? Estimate it with our <a href="/body-fat-calculator/">body fat calculator</a>.</p>',
'<div class="bf-cols"><div>' + rank_table(M, [10, 12, 15, 18, 20, 22, 25, 28, 30, 35], "Men") + '</div><div>' + rank_table(F, [18, 20, 22, 25, 28, 30, 32, 35, 40, 45], "Women") + '</div></div>',
f'<p class="cmb-src">Our calculation from NHANES 2011&ndash;2018 DXA scans. Example: a man aged 20&ndash;39 at 15% body fat has less body fat than {round(100 - pct_of(M["20-39"]["cdf"], 15))}% of US men his age.</p>',
'<h2 id="healthy">Healthy body fat percentage</h2>',
f'<p><strong>There is no official body fat standard; the most cited ranges are provisional.</strong> In 2000, Gallagher and colleagues predicted the body fat that matches each BMI cut-off by age and sex. Those ranges are below, with a caution: they come from a different measurement setup than CDC&rsquo;s scans, and they differ by ethnic group, so use them as a guide, not a diagnosis. The median American adult in our data sits above the healthy band for their age.</p>',
gal_table(),
f'<p class="cmb-src">Source: <a href="{GAL}" rel="noopener">Gallagher D, et al. Am J Clin Nutr 2000;72:694&ndash;701</a>, ranges as tabulated in <a href="{GALT}" rel="noopener">J Public Health Afr 2016, Table 1</a>.</p>',
'<h2 id="bmi">Body fat vs BMI</h2>',
f'<p><strong>BMI and body fat track each other, but loosely.</strong> Among men with a healthy BMI (18.5&ndash;24.9), body fat ranged widely: the middle half sat between {f1(bm["18.5–24.9"]["q"][1])}% and {f1(bm["18.5–24.9"]["q"][3])}%. Among men with a BMI of 30 or more, the middle half was {f1(bm["30+"]["q"][1])}&ndash;{f1(bm["30+"]["q"][3])}%. For women, the same comparison is {f1(bf["18.5–24.9"]["q"][1])}&ndash;{f1(bf["18.5–24.9"]["q"][3])}% versus {f1(bf["30+"]["q"][1])}&ndash;{f1(bf["30+"]["q"][3])}%. More on this in <a href="/blog/body-fat-vs-bmi/">body fat vs BMI</a>; to calculate your BMI, use our <a href="/">BMI calculator</a>.</p>',
f'<figure class="aw-fig"><div class="bf-sm"><div class="bf-sm-p"><p class="bf-sm-t" style="--c:#1F4E79">Men 20–59</p>{bmi_chart(M, "#1F4E79", "Men")}</div><div class="bf-sm-p"><p class="bf-sm-t" style="--c:#C2481E">Women 20–59</p>{bmi_chart(F, "#C2481E", "Women")}</div></div><ul class="bf-key"><li><span class="bf-k2"></span>Middle half (25th–75th percentile)</li><li><span class="bf-k3"></span>Median; whiskers 10th–90th</li></ul><figcaption>Body fat within each BMI category, adults 20&ndash;59, NHANES 2011&ndash;2018 (our calculation).</figcaption></figure>',
'<h2 id="faq">FAQ</h2>',
f'<details class="cmb-faq"><summary><h3>What is the average body fat percentage?</h3></summary><p>{f1(mm["mean"])}% for US men and {f1(ff["mean"])}% for US women aged 20&ndash;59, measured by DXA scans in 2011&ndash;2018.</p></details>',
f'<details class="cmb-faq"><summary><h3>What is a healthy body fat percentage for men?</h3></summary><p>The provisional ranges matched to a healthy BMI are 8&ndash;19.9% at ages 20&ndash;39, 11&ndash;21.9% at 40&ndash;59 and 13&ndash;24.9% at 60&ndash;79 (Gallagher et al., 2000).</p></details>',
f'<details class="cmb-faq"><summary><h3>What is a healthy body fat percentage for women?</h3></summary><p>21&ndash;32.9% at ages 20&ndash;39, 23&ndash;33.9% at 40&ndash;59 and 24&ndash;35.9% at 60&ndash;79 (Gallagher et al., 2000). These are provisional and vary by ethnic group.</p></details>',
f'<details class="cmb-faq"><summary><h3>Is 20% body fat good for a man?</h3></summary><p>It is just above the provisional healthy range for men 20&ndash;39 (8&ndash;19.9%) and inside it for men 40&ndash;59 (11&ndash;21.9%). It is leaner than most: {round(100 - pct_of(M["20-39"]["cdf"], 20))}% of US men aged 20&ndash;39 have more body fat.</p></details>',
f'<details class="cmb-faq"><summary><h3>Is 30% body fat good for a woman?</h3></summary><p>It is inside the provisional healthy range for women aged 20&ndash;59, and {round(100 - pct_of(F["20-39"]["cdf"], 30))}% of US women aged 20&ndash;39 have more body fat.</p></details>',
'<details class="cmb-faq"><summary><h3>Why is there no data for people over 60?</h3></summary><p>CDC&rsquo;s whole-body DXA scans in 2011&ndash;2018 covered ages 8&ndash;59 only. For ages 60&ndash;79 we show the provisional ranges, not population data.</p></details>',
'<h2 id="method">How we calculated this</h2>',
f'<p>We pooled CDC&rsquo;s National Health and Nutrition Examination Survey cycles 2011&ndash;2012 through 2017&ndash;2018: the whole-body DXA scan files, the demographics files and the body measures files. We kept valid scans, excluded pregnant women, and used CDC&rsquo;s exam weights divided by four, as CDC&rsquo;s guidelines advise when combining four cycles. Standard errors use the survey&rsquo;s strata and primary sampling units. CDC notes its scan software adds 5% of lean mass to fat mass, so results from other devices may not match exactly.</p>',
f'<p><strong>Check against published research:</strong> using the same age adjustment as <a href="{BMJ}" rel="noopener">Liu et al., BMJ 2021</a>, our figures reproduce their mean body fat for every cycle (32.6%, 33.1%, 32.9% and 33.0%) from the identical sample of {R["meta"]["n_adults"]:,} adults.</p>',
'<ol class="cmb-sources">',
f'<li>National Center for Health Statistics. <a href="{DXX}" rel="noopener">NHANES Dual-Energy X-ray Absorptiometry, Whole Body</a> (DXX_G, DXX_H, DXX_I, DXX_J), with demographics and body measures files, 2011–2018.</li>',
f'<li>Liu B, et al. <a href="{BMJ}" rel="noopener">Trends in obesity and adiposity measures by race or ethnicity among adults in the United States 2011-18</a>. BMJ 2021;372:n365.</li>',
f'<li>Gallagher D, et al. <a href="{GAL}" rel="noopener">Healthy percentage body fat ranges: an approach for developing guidelines based on body mass index</a>. Am J Clin Nutr 2000;72:694–701.</li>',
f'<li><a href="{GALT}" rel="noopener">Interpreting the body fat percentage result (Table 1)</a>. J Public Health Afr 2016;7:515.</li>',
'</ol>',
f'<p><strong>Download:</strong> <a href="/{SLUG}/{CSVF}" download>body fat percentiles by sex and age (CSV)</a>. Free to reuse with a link to this page (CC BY 4.0).</p>',
'<p class="cmb-note">This page describes populations, not individuals. It is not medical advice.</p>',
'<h2>Related</h2><ul><li><a href="/body-fat-calculator/">Body fat calculator (tape, skinfold or BMI)</a></li><li><a href="/average-weight/">Average weight by height and age</a></li><li><a href="/blog/body-fat-vs-bmi/">Body fat vs BMI</a></li><li><a href="/lean-body-mass/">Lean body mass calculator</a></li><li><a href="/">BMI calculator</a></li></ul>',
'</article>',
f'<script>window.BF_DATA={json.dumps(TD, separators=(",", ":"))};</script>',
f'<script>{JS}</script>')

TITLE = "Body Fat Percentage Chart: Men & Women by Age (CDC Data)"
DESC = f"Body fat percentage for US men and women by age, from CDC DXA scans: average {f1(mm['mean'])}% for men and {f1(ff['mean'])}% for women. See where you rank."
OG = f"https://calculatemybmi.net/{SLUG}/og-{SLUG}.png"
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "Body Fat Percentage Chart for Men and Women", "description": DESC,
  "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}, "datePublished": "2026-10-04", "dateModified": "2026-10-04",
  "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "citation": [DXX, BMJ, GAL, GALT]},
 {"@type": "Dataset", "@id": URL + "#dataset", "name": "Body fat percentage of US children and adults by sex and age, NHANES 2011–2018 DXA",
  "description": "Survey-weighted percentiles and means of whole-body DXA percent body fat for US residents aged 8–59 by sex and age group, and by BMI category for adults, pooled NHANES 2011–2018. Calculated by calculatemybmi.net from CDC public-use files; reproduces Liu et al., BMJ 2021.",
  "url": URL, "creator": {"@id": "https://calculatemybmi.net/#organization"}, "isBasedOn": DXX, "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": True, "temporalCoverage": "2011/2018", "spatialCoverage": {"@type": "Place", "name": "United States"},
  "variableMeasured": ["Percent body fat (DXA)", "Percentiles", "Mean", "Standard error"],
  "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"https://calculatemybmi.net/{SLUG}/{CSVF}"}]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"}, {"@type": "ListItem", "position": 2, "name": "Body Fat Percentage Chart", "item": URL}]},
 org, person]}
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Body fat percentage chart for men and women (CDC scan data)">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'),
                 (r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="Average body fat: men {f1(mm["mean"])}%, women {f1(ff["mean"])}% (CDC DXA scans, 2011–2018).">'),
                 (r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG}">')]:
    head = re.sub(pat, rep, head, flags=re.S)
rest = shell[shell.find("</script>", shell.find('<script type="application/ld+json">')) + 9:]
page = (head + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, indent=1) + "</script>" + rest[:rest.find("</head>")] + "<style>" + CSS + "</style>"
        + rest[rest.find("</head>"):rest.find("<main>")] + '<main><div class="container" style="max-width:1000px;margin:0 auto;padding:2rem 1rem 3rem;">' + content + "</div>" + rest[rest.find("</main>"):])
os.makedirs(os.path.join(OUT, SLUG), exist_ok=True)
open(os.path.join(OUT, SLUG, "index.html"), "w", encoding="utf-8").write(page)
with open(os.path.join(OUT, SLUG, CSVF), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["# Percent body fat (whole-body DXA, NHANES BCA option) of US residents, NHANES 2011-2018 pooled (weights WTMEC2YR/4), pregnant excluded. Calculated by calculatemybmi.net from CDC public-use files; CC BY 4.0."])
    w.writerow(["sex", "age_group", "mean", "se", "p5", "p10", "p25", "p50", "p75", "p90", "p95", "n"])
    for sx, S in (("male", M), ("female", F)):
        for k in TEENS + AGES + ["20-39", "40-59", "20-59"]:
            p = S[k]["p"]; w.writerow([sx, k, S[k]["mean"], S[k]["se"], p[0], p[1], p[4], p[9], p[14], p[17], p[18], S[k]["n"]])
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1200, 630), "#FFFFFF"); dr = ImageDraw.Draw(im)
def font(sz, b=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()
dr.rectangle([0, 0, 1200, 12], fill="#6B46C1")
dr.text((56, 50), "Body fat percentage chart", font=font(56, True), fill="#111827")
dr.text((56, 126), "US adults 20–59, CDC DXA body scans, 2011–2018", font=font(30), fill="#4B5563")
dr.text((56, 210), f"Men  {f1(mm['mean'])}%", font=font(72, True), fill="#1F4E79")
dr.text((56, 310), f"Women  {f1(ff['mean'])}%", font=font(72, True), fill="#C2481E")
dr.text((56, 430), "Average body fat · see where you rank", font=font(34), fill="#1F2937")
dr.text((56, 560), "calculatemybmi.net", font=font(28, True), fill="#6B7280")
im.save(os.path.join(OUT, SLUG, f"og-{SLUG}.png"), optimize=True)
print(json.dumps({"title_len": len(TITLE), "desc_len": len(DESC), "men_mean": mm["mean"], "women_mean": ff["mean"], "rank15m": round(100 - pct_of(M["20-39"]["cdf"], 15)), "rank20m": round(100 - pct_of(M["20-39"]["cdf"], 20)), "rank30f": round(100 - pct_of(F["20-39"]["cdf"], 30))}))
