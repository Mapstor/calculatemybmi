#!/usr/bin/env python3
"""Build /body-fat-calculator/ for calculatemybmi.net.
Equations (verified in chat, 4 Oct 2026):
- Circumference ("Navy") method, inches: men 86.010*log10(waist-neck) - 70.041*log10(height) + 36.76;
  women 163.205*log10(waist+hip-neck) - 97.684*log10(height) - 78.387 — Army sample calculations (Table B-5) reproduced in
  ClinicalTrials.gov protocol NCT02734238; origin Hodgdon & Beckett 1984 (NHRC reports 84-11, 84-29).
  Worked examples there: woman 15/42/44/64 in -> 46.73%; man 16/49/69 in -> 38.62%.
- Jackson-Pollock 3-site body density (men 1978; women 1980) + Siri (495/D - 450), as reproduced in Serra et al.,
  ConScientiae Saude 2009 (women's age coefficient printed 0.0001395 there vs 0.0001392 elsewhere; we use 0.0001392 and say so).
- Deurenberg 1991 adult BMI formula: 1.20*BMI + 0.23*age - 10.8*sex - 5.4 (sex 1 = male), SEE 4.1 (PubMed 2043597).
Results are placed on our verified NHANES 2011-2018 DXA percentiles (/body-fat-percentage-chart/)."""
import json, os, re, sys, math, html as H
ROOT, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
BF = json.load(open(os.path.join(HERE, "bf_results.json")))
AWCSS = open(os.path.join(HERE, "aw_css.txt"), encoding="utf-8").read()
SLUG = "body-fat-calculator"; URL = f"https://calculatemybmi.net/{SLUG}/"
ARMY = "https://cdn.clinicaltrials.gov/large-docs/38/NCT02734238/Prot_SAP_000.pdf"
JP = "https://periodicos.uninove.br/saude/article/download/1421/1197"
DEUR = "https://pubmed.ncbi.nlm.nih.gov/2043597/"
DXX = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm"
GAL = "https://pubmed.ncbi.nlm.nih.gov/10966886/"
# ---- reference implementations (also used to assert the worked examples) ----
def navy(sex, h, neck, waist, hip=0):
    return 86.010 * math.log10(waist - neck) - 70.041 * math.log10(h) + 36.76 if sex == "m" else 163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(h) - 78.387
def jp3(sex, s, age):
    d = 1.10938 - 0.0008267 * s + 0.0000016 * s * s - 0.0002574 * age if sex == "m" else 1.0994921 - 0.0009929 * s + 0.0000023 * s * s - 0.0001392 * age
    return 495 / d - 450
def deur(sex, bmi, age): return 1.20 * bmi + 0.23 * age - 10.8 * (1 if sex == "m" else 0) - 5.4
assert round(navy("f", 64, 15, 42, 44)) == 47 and round(navy("m", 69, 16, 49)) == 39   # Army doc: 46.73% -> 47%, 38.62% -> 39% (computed with rounded logarithms)
_d = 1.10938 - 0.0008267 * 53 + 0.0000016 * 53 * 53 - 0.0002574 * 40
assert abs(_d - 1.0597633) < 1e-7 and round(jp3("m", 53, 40), 1) == 17.1 and round(deur("m", 25, 40), 1) == 23.0   # published worked density 1.0597633 (sum 53 mm, age 40)
GALR = {"f": {"20-39": [21, 33, 39], "40-59": [23, 34, 40], "60-79": [24, 36, 42]}, "m": {"20-39": [8, 20, 25], "40-59": [11, 22, 28], "60-79": [13, 25, 30]}}
TD = {"cdf": {sx: {k: BF[sx][k]["cdf"] for k in ("16-19", "20-29", "30-39", "40-49", "50-59")} for sx in ("m", "f")}, "gal": GALR}
f1 = lambda v: f"{v:.1f}"

TOOL = (
'<section class="aw-tool" aria-label="Body fat calculator">'
'<div class="aw-tool-head"><h2>Calculate your body fat</h2><p>Three published methods: tape measure, skinfold calipers, or just height and weight. Results are compared with CDC body scans of US adults.</p></div>'
'<div class="aw-form">'
'<div class="aw-field"><span class="aw-flabel" id="bc-sex-l">I am</span><div class="aw-pills" role="radiogroup" aria-labelledby="bc-sex-l"><input type="radio" id="bc-sx-f" name="bc-sex" value="f" checked><label for="bc-sx-f">Woman</label><input type="radio" id="bc-sx-m" name="bc-sex" value="m"><label for="bc-sx-m">Man</label></div></div>'
'<div class="aw-field"><span class="aw-flabel" id="bc-u-l">Units</span><div class="aw-pills" role="radiogroup" aria-labelledby="bc-u-l"><input type="radio" id="bc-u-imp" name="bc-u" value="imp" checked><label for="bc-u-imp">in &middot; lb</label><input type="radio" id="bc-u-met" name="bc-u" value="met"><label for="bc-u-met">cm &middot; kg</label></div></div>'
'<div class="aw-field aw-field-wide"><label class="aw-flabel" for="bc-h">Height</label><div class="aw-height"><button type="button" class="aw-step" id="bc-h-minus" aria-label="Shorter">&minus;</button><output id="bc-h-out" for="bc-h">5&prime; 6&Prime;</output><button type="button" class="aw-step" id="bc-h-plus" aria-label="Taller">+</button></div><input type="range" id="bc-h" min="54" max="80" step="1" value="66" aria-valuetext="5 feet 6 inches"><div class="aw-scale" id="bc-scale"><span>4&prime;6&Prime;</span><span>5&prime;7&Prime;</span><span>6&prime;8&Prime;</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="bc-age">Age</label><div class="aw-input"><input type="number" id="bc-age" inputmode="numeric" min="18" max="79" step="1" value="35"><span>years</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="bc-w">Weight</label><div class="aw-input"><input type="number" id="bc-w" inputmode="decimal" min="60" max="700" step="0.1" placeholder="e.g. 160"><span class="bc-wu">lb</span></div></div>'
'<div class="aw-field aw-field-wide"><span class="aw-flabel" id="bc-m-l">Method</span><div class="aw-pills bc-tabs" role="radiogroup" aria-labelledby="bc-m-l">'
'<input type="radio" id="bc-m-tape" name="bc-m" value="tape" checked><label for="bc-m-tape">Tape measure</label>'
'<input type="radio" id="bc-m-skin" name="bc-m" value="skin"><label for="bc-m-skin">Calipers</label>'
'<input type="radio" id="bc-m-bmi" name="bc-m" value="bmi"><label for="bc-m-bmi">Height &amp; weight</label></div></div>'
'<div class="bc-pane aw-field-wide" id="bc-p-tape"><div class="bc-grid">'
'<div class="aw-field"><label class="aw-flabel" for="bc-neck">Neck <small>below the Adam&rsquo;s apple</small></label><div class="aw-input"><input type="number" id="bc-neck" inputmode="decimal" step="0.1" placeholder="e.g. 14"><span class="bc-lu">in</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="bc-waist" id="bc-waist-l">Waist <small>narrowest point</small></label><div class="aw-input"><input type="number" id="bc-waist" inputmode="decimal" step="0.1" placeholder="e.g. 32"><span class="bc-lu">in</span></div></div>'
'<div class="aw-field" id="bc-hip-f"><label class="aw-flabel" for="bc-hip">Hips <small>widest point</small></label><div class="aw-input"><input type="number" id="bc-hip" inputmode="decimal" step="0.1" placeholder="e.g. 40"><span class="bc-lu">in</span></div></div>'
'</div></div>'
'<div class="bc-pane aw-field-wide" id="bc-p-skin" hidden><div class="bc-grid">'
'<div class="aw-field"><label class="aw-flabel" for="bc-s1" id="bc-s1-l">Triceps</label><div class="aw-input"><input type="number" id="bc-s1" inputmode="decimal" step="0.5" placeholder="mm"><span>mm</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="bc-s2" id="bc-s2-l">Suprailiac</label><div class="aw-input"><input type="number" id="bc-s2" inputmode="decimal" step="0.5" placeholder="mm"><span>mm</span></div></div>'
'<div class="aw-field"><label class="aw-flabel" for="bc-s3" id="bc-s3-l">Thigh</label><div class="aw-input"><input type="number" id="bc-s3" inputmode="decimal" step="0.5" placeholder="mm"><span>mm</span></div></div>'
'</div></div>'
'<div class="bc-pane aw-field-wide" id="bc-p-bmi" hidden><p class="aw-small">Uses only your height, weight, age and sex (Deurenberg formula). Quickest, but the least specific of the three.</p></div>'
'<button type="button" id="bc-go" class="aw-cta">Calculate my body fat</button></div>'
'<div id="bc-out" class="aw-out" hidden aria-live="polite"></div></section>')

JS = r"""
(function(){var D=window.BC_DATA,$=function(i){return document.getElementById(i);},sl=$('bc-h'),ho=$('bc-h-out'),out=$('bc-out');
function q(n){return document.querySelector('input[name="'+n+'"]:checked').value;}
function num(id){var v=parseFloat($(id).value);return v>0?v:0;}
function ftin(h){var t=Math.round(h);return Math.floor(t/12)+'′ '+(t%12)+'″';}
function hIn(){return q('bc-u')==='imp'?+sl.value:(+sl.value)/2.54;}
function showH(){if(q('bc-u')==='imp'){ho.textContent=ftin(+sl.value);sl.setAttribute('aria-valuetext',Math.floor(sl.value/12)+' feet '+(sl.value%12)+' inches');}else{ho.textContent=sl.value+' cm';sl.setAttribute('aria-valuetext',sl.value+' centimeters');}sl.style.setProperty('--p',((sl.value-sl.min)/(sl.max-sl.min)*100).toFixed(1)+'%');}
sl.addEventListener('input',showH);$('bc-h-minus').addEventListener('click',function(){sl.value=+sl.value-1;showH();});$('bc-h-plus').addEventListener('click',function(){sl.value=+sl.value+1;showH();});
function syncSex(){var m=q('bc-sex')==='m';$('bc-hip-f').hidden=m;$('bc-waist-l').innerHTML=m?'Waist <small>at the navel</small>':'Waist <small>narrowest point</small>';
 var L=m?['Chest','Abdomen','Thigh']:['Triceps','Suprailiac','Thigh'];['bc-s1-l','bc-s2-l','bc-s3-l'].forEach(function(id,i){$(id).textContent=L[i];});}
document.querySelectorAll('input[name="bc-sex"]').forEach(function(r){r.addEventListener('change',syncSex);});
function syncM(){var m=q('bc-m');['tape','skin','bmi'].forEach(function(k){$('bc-p-'+k).hidden=(k!==m);});}
document.querySelectorAll('input[name="bc-m"]').forEach(function(r){r.addEventListener('change',syncM);});
var uPrev='imp';document.querySelectorAll('input[name="bc-u"]').forEach(function(r){r.addEventListener('change',function(){var met=q('bc-u')==='met';if((met?'met':'imp')===uPrev)return;
 var hv=+sl.value,hin=uPrev==='imp'?hv:hv/2.54,f=met?2.54:1/2.54,wf=met?0.45359237:1/0.45359237;sl.min=met?137:54;sl.max=met?203:80;sl.value=met?Math.round(hin*2.54):Math.round(hin);uPrev=met?'met':'imp';
 $('bc-scale').innerHTML=met?'<span>137 cm</span><span>170 cm</span><span>203 cm</span>':'<span>4′6″</span><span>5′7″</span><span>6′8″</span>';
 ['bc-neck','bc-waist','bc-hip'].forEach(function(id){var v=parseFloat($(id).value);if(v>0)$(id).value=(v*f).toFixed(1);});var w=parseFloat($('bc-w').value);if(w>0)$('bc-w').value=(w*wf).toFixed(1);
 document.querySelectorAll('.bc-lu').forEach(function(e){e.textContent=met?'cm':'in';});document.querySelector('.bc-wu').textContent=met?'kg':'lb';showH();});});
syncSex();syncM();showH();
function navy(sx,h,n,w,hp){return sx==='m'?86.010*Math.log10(w-n)-70.041*Math.log10(h)+36.76:163.205*Math.log10(w+hp-n)-97.684*Math.log10(h)-78.387;}
function jp3(sx,s,a){var d=sx==='m'?1.10938-0.0008267*s+0.0000016*s*s-0.0002574*a:1.0994921-0.0009929*s+0.0000023*s*s-0.0001392*a;return 495/d-450;}
function deur(sx,bmi,a){return 1.20*bmi+0.23*a-10.8*(sx==='m'?1:0)-5.4;}
function grp(a){return a<=19?'16-19':a<=29?'20-29':a<=39?'30-39':a<=49?'40-49':a<=59?'50-59':null;}
function ggrp(a){return a<=39?'20-39':a<=59?'40-59':'60-79';}
function pctOf(c,v){if(v<=c[0])return 1;if(v>=c[c.length-1])return 99;for(var i=1;i<c.length;i++){if(v<=c[i])return i+(v-c[i-1])/(c[i]-c[i-1]);}return 99;}
function bar(l,v,mx,col,me,note){return '<div class="aw-b'+(me?' aw-b-me':'')+'"><span class="aw-b-l">'+l+(note?' <small>'+note+'</small>':'')+'</span><span class="aw-b-t"><span class="aw-b-f" style="width:'+Math.max(3,v/mx*100).toFixed(1)+'%;background:'+col+'"></span></span><span class="aw-b-v">'+v.toFixed(1)+'%</span></div>';}
function err(m){out.innerHTML='<p class="aw-err">'+m+'</p>';out.hidden=false;}
$('bc-go').addEventListener('click',function(){var sx=q('bc-sex'),met=q('bc-u')==='met',m=q('bc-m'),h=hIn(),age=Math.round(num('bc-age')),wv=num('bc-w'),wlb=met?wv/0.45359237:wv,cv=met?1/2.54:1;
 if(!(age>=18&&age<=79))return err('Enter an age between 18 and 79.');
 var est={},msg=null;
 var n=num('bc-neck')*cv,wa=num('bc-waist')*cv,hp=num('bc-hip')*cv;
 if(n&&wa&&(sx==='m'||hp)){if(wa<=n)msg='Your waist must be larger than your neck.';else est.tape=navy(sx,h,n,wa,hp);}
 var s=num('bc-s1')+num('bc-s2')+num('bc-s3');if(num('bc-s1')&&num('bc-s2')&&num('bc-s3'))est.skin=jp3(sx,s,age);
 if(wlb){var bmi=(wlb*0.45359237)/Math.pow(h*0.0254,2);est.bmi=deur(sx,bmi,age);}
 if(!est[m]){if(m==='tape')return err(msg||('Enter your neck, waist'+(sx==='f'?' and hips':'')+' to use the tape-measure method.'));if(m==='skin')return err('Enter all three skinfolds to use the caliper method.');return err('Enter your weight to use the height-and-weight method.');}
 var v=est[m],names={tape:'Tape measure (Navy method)',skin:'Skinfolds (Jackson–Pollock 3-site)',bmi:'Height & weight (Deurenberg)'},cols={tape:'#1F4E79',skin:'#6B46C1',bmi:'#C2481E'};
 if(!(v>2&&v<70))return err('Those measurements give an implausible result ('+v.toFixed(1)+'%). Please double-check them and the units.');
 var who=sx==='m'?'men':'women',Who=sx==='m'?'Men':'Women',k=grp(age),gk=ggrp(age),gb=D.gal[sx][gk],cl=v<gb[0]?['Low','#60A5FA']:v<gb[1]?['Healthy','#2E7D4F']:v<gb[2]?['High','#E5743F']:['Very high','#B3431A'],html='';
 html+='<div class="aw-rh"><span class="aw-chip">'+Who+'</span><span class="aw-chip">Age '+age+'</span><span class="aw-chip">'+ftin(h)+(met?' · '+Math.round(h*2.54)+' cm':'')+'</span>'+(wlb?'<span class="aw-chip">'+Math.round(wlb)+' lb'+(met?' · '+wv.toFixed(1)+' kg':'')+'</span>':'')+'</div>';
 var tiles=[['Your body fat',v.toFixed(1)+'%',names[m],cols[m]]];
 if(wlb){var fm=wlb*v/100;tiles.push(['Fat / lean mass',Math.round(fm)+' / '+Math.round(wlb-fm)+' lb',(fm*0.45359237).toFixed(1)+' / '+((wlb-fm)*0.45359237).toFixed(1)+' kg','#6B7280']);}
 tiles.push(['Provisional healthy range',gb[0]+'–'+(gb[1]-0.1).toFixed(1)+'%','Your value: '+cl[0].toLowerCase()+' (Gallagher 2000, ages '+gk.replace('-','–')+')',cl[1]]);
 if(k){var c=D.cdf[sx][k],more=Math.round(100-pctOf(c,v));tiles.push(['Compared with US '+who,more+'%','of '+who+' '+k.replace('-','–')+' have more body fat (CDC body scans)','#2E7D4F']);}
 else tiles.push(['Compared with US '+who,'–','CDC’s body scans covered ages 8–59','#9CA3AF']);
 html+='<div class="aw-tiles">'+tiles.map(function(t){return '<div class="aw-tile" style="--c:'+t[3]+'"><span class="aw-tile-l">'+t[0]+'</span><span class="aw-tile-n">'+t[1]+'</span><span class="aw-tile-s">'+t[2]+'</span></div>';}).join('')+'</div>';
 var ks=Object.keys(est),mx=0;ks.forEach(function(x){mx=Math.max(mx,est[x]);});
 html+='<h3 class="aw-h3">Your estimates by method</h3><div class="aw-bars">'+['tape','skin','bmi'].filter(function(x){return est[x]!==undefined;}).map(function(x){return bar(names[x],est[x],Math.max(mx,gb[2]+5),cols[x],x===m,x===m?'(selected)':'');}).join('')+bar('Top of healthy range',gb[1]-0.1,Math.max(mx,gb[2]+5),'#2E7D4F')+'</div>';
 if(ks.length>1){var mn=1e9,mxx=-1e9;ks.forEach(function(x){mn=Math.min(mn,est[x]);mxx=Math.max(mxx,est[x]);});html+='<p class="aw-small">Your methods differ by <strong>'+(mxx-mn).toFixed(1)+' points</strong>. Estimates from different methods rarely agree exactly; the range is a fair picture of your likely body fat.</p>';}
 if(k){var cdf=D.cdf[sx][k],cw=out.getBoundingClientRect().width||0,W=cw>200?Math.max(330,Math.min(640,Math.round(cw-36))):640;html+='<h3 class="aw-h3">Where '+v.toFixed(1)+'% sits among US '+who+' aged '+k.replace('-','–')+'</h3><div class="aw-dist">'+window.BC_DIST(cdf,v,[gb[0],gb[1]],sx,W)+'</div><p class="aw-small">Shape: DXA body scans of US '+who+' '+k.replace('-','–')+', NHANES 2011–2018 (our calculation). Green: provisional healthy range.</p>';}
 var notes=[];
 if(m==='bmi')notes.push('The height-and-weight formula has a standard error of about 4.1 points, and its authors found it slightly overestimates body fat in people with obesity.');
 if(m==='tape')notes.push('The tape equations work in inches; we convert centimeters for you. Measure snugly without compressing the skin, and repeat each measurement.');
 if(m==='skin')notes.push('Skinfold results depend heavily on the person measuring; take each site two or three times and use the average.');
 notes.push('For a military test, use the official procedure of your service; this calculator is for information.');
 html+='<ul class="aw-notes">'+notes.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul><p class="cmb-src">Equations: Hodgdon &amp; Beckett (Navy/Army tape method), Jackson &amp; Pollock with Siri (skinfolds), Deurenberg 1991 (BMI). Comparison: CDC NHANES 2011–2018 DXA scans; ranges: Gallagher et al., 2000.</p>';
 out.innerHTML=html;out.hidden=false;out.scrollIntoView({behavior:'smooth',block:'start'});});
})();
"""
DIST = r"""
window.BC_DIST=function(c,v,gb,sx,W){var P=W<480?22:36,PH=W<480?130:150,lo=Math.max(0,Math.floor(Math.min(c[0],gb[0],v)/5)*5-5),hi=Math.min(70,Math.ceil(Math.max(c[98],gb[1],v)/5)*5+5),i;
 var X=function(x){return P+(x-lo)*(W-2*P)/(hi-lo);},NG=90,dx=(hi-lo)/NG,gx=[],dens=[];
 function F(x){if(x<=c[0])return 0.01*Math.max(0,(x-(c[0]-(c[1]-c[0])*3))/((c[1]-c[0])*3));if(x>=c[98])return Math.min(1,0.99+0.01*(x-c[98])/((c[98]-c[97])*3));for(var k=1;k<c.length;k++){if(x<=c[k])return (k+(x-c[k-1])/(c[k]-c[k-1]))/100;}return 1;}
 for(i=0;i<=NG;i++){var xx=lo+i*dx;gx.push(xx);dens.push((F(xx+dx)-F(xx-dx))/(2*dx));}
 for(var p=0;p<3;p++){var sm=dens.slice();for(i=0;i<dens.length;i++){var a2=dens[Math.max(0,i-2)],a1=dens[Math.max(0,i-1)],b1=dens[Math.min(dens.length-1,i+1)],b2=dens[Math.min(dens.length-1,i+2)];sm[i]=(a2+4*a1+6*dens[i]+4*b1+b2)/16;}dens=sm;}
 var mx=Math.max.apply(null,dens),med=c[49],labels=[{x:X(med),t:'Median '+med.toFixed(1)+'%',cl:'#111827'},{x:X((gb[0]+gb[1])/2),t:'Healthy range '+gb[0]+'–'+(gb[1]-0.1).toFixed(1)+'%',cl:'#2E7D4F'},{x:X(v),t:'You '+v.toFixed(1)+'%',cl:'#C2481E'}];
 labels.forEach(function(l){l.w=l.t.length*7.2+16;});labels.sort(function(a,b){return a.x-b.x;});
 var rows=[[],[],[]];labels.forEach(function(l){var lx=Math.min(Math.max(l.x-l.w/2,4),W-4-l.w);l.lx=lx;for(var r=0;r<3;r++){if(rows[r].every(function(o){return lx>o.lx+o.w+8||lx+l.w+8<o.lx;})){rows[r].push(l);l.r=r;break;}}if(l.r===undefined){l.r=2;rows[2].push(l);}});
 var nr=rows.filter(function(r){return r.length;}).length,top=nr*24+6,H=top+PH+30,g='',Y=function(d){return top+PH-(d/mx)*(PH-10);},col=sx==='m'?'#1F4E79':'#C2481E';
 g+='<rect x="'+X(gb[0]).toFixed(1)+'" y="'+top+'" width="'+(X(gb[1])-X(gb[0])).toFixed(1)+'" height="'+PH+'" fill="#CDE7D8" opacity=".75"/>';
 var path='M'+X(gx[0]).toFixed(1)+' '+(top+PH);for(i=0;i<dens.length;i++)path+=' L'+X(gx[i]).toFixed(1)+' '+Y(dens[i]).toFixed(1);path+=' L'+X(gx[gx.length-1]).toFixed(1)+' '+(top+PH)+' Z';
 g+='<path d="'+path+'" fill="'+col+'" opacity=".22"/><path d="'+path.replace(/ Z$/,'')+'" fill="none" stroke="'+col+'" stroke-width="2"/><line x1="'+P+'" x2="'+(W-P)+'" y1="'+(top+PH)+'" y2="'+(top+PH)+'" stroke="#9CA3AF"/>';
 var st=(hi-lo)>40&&W<480?10:5;for(var t=lo;t<=hi;t+=st){g+='<text x="'+X(t).toFixed(1)+'" y="'+(top+PH+21)+'" text-anchor="middle" class="aw-ax">'+t+'%</text>';}
 g+='<line x1="'+X(med).toFixed(1)+'" x2="'+X(med).toFixed(1)+'" y1="'+top+'" y2="'+(top+PH)+'" stroke="#111827" stroke-width="2" stroke-dasharray="5 4"/><line x1="'+X(v).toFixed(1)+'" x2="'+X(v).toFixed(1)+'" y1="'+top+'" y2="'+(top+PH)+'" stroke="#C2481E" stroke-width="3"/><circle cx="'+X(v).toFixed(1)+'" cy="'+(top+PH)+'" r="6" fill="#C2481E" stroke="#fff" stroke-width="2"/>';
 labels.forEach(function(l){var ly=4+l.r*24;g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+(ly+20)+'" y2="'+top+'" stroke="'+l.cl+'" stroke-width="1" opacity=".55"/><rect class="aw-lbl" data-r="'+l.r+'" data-x="'+l.lx.toFixed(1)+'" data-w="'+l.w.toFixed(1)+'" x="'+l.lx.toFixed(1)+'" y="'+ly+'" width="'+l.w.toFixed(1)+'" height="20" rx="10" fill="#fff" stroke="'+l.cl+'"/><text x="'+(l.lx+l.w/2).toFixed(1)+'" y="'+(ly+14)+'" text-anchor="middle" class="aw-lt" fill="'+l.cl+'">'+l.t+'</text>';});
 return '<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="Body fat distribution for your sex and age with the median, the provisional healthy range and your result">'+g+'</svg>';};
"""
CSS = (AWCSS.replace("#aw-h-out{", "#aw-h-out,#bc-h-out{").replace("#aw-h{", "#aw-h,#bc-h{").replace("#aw-h::-webkit-slider-thumb{", "#aw-h::-webkit-slider-thumb,#bc-h::-webkit-slider-thumb{").replace("#aw-h::-moz-range-thumb{", "#aw-h::-moz-range-thumb,#bc-h::-moz-range-thumb{") + """
.bc-tabs label{font-size:.95rem}
.bc-pane[hidden],#bc-hip-f[hidden]{display:none}
.bc-grid{display:flex;flex-wrap:wrap;gap:14px 16px}
.bc-grid .aw-field{flex:1 1 150px}
.aw-b-l small{color:#6B7280;font-weight:600}
.bc-f{background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;padding:12px 14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9rem;overflow-x:auto;white-space:nowrap}
.bc-ex{border-left:6px solid #1F4E79;background:#fff;border-radius:12px;padding:10px 14px;box-shadow:0 3px 12px rgba(17,24,39,.06);margin:10px 0}
""")
def P(*a): return "\n".join(a)
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <a href="/calculators/" style="color:inherit;">Calculators</a> &rsaquo; <span>Body Fat Calculator</span></nav>',
'<article class="cmb-stats">',
'<h1>Body Fat Calculator</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Equations checked against their published sources &middot; Reviewed October 4, 2026 &middot; Not medical advice</p>',
'<p class="cmb-intro">Estimate your body fat percentage with a tape measure, skinfold calipers, or just your height and weight. Use more than one method to see how much they agree, then see how your number compares with CDC body scans of US adults.</p>',
TOOL,
'<div class="cmb-answer" id="answer">',
'<p><strong>Body fat percentage can be estimated three ways at home:</strong> the tape-measure (Navy) method uses your neck, waist and, for women, hips; the Jackson&ndash;Pollock method uses three skinfold measurements; the Deurenberg formula uses only BMI, age and sex. All three are estimates. The gold standard used by CDC is a DXA body scan, and our results compare your number with those scans.</p>',
f'<p class="cmb-src">Equations: <a href="{ARMY}" rel="noopener">US Army sample calculations</a>, <a href="{JP}" rel="noopener">Jackson&ndash;Pollock and Siri</a>, <a href="{DEUR}" rel="noopener">Deurenberg et al., 1991</a>. Comparison data: <a href="/body-fat-percentage-chart/">our body fat percentage chart</a>.</p>',
'</div>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol><li><a href="#tape">The tape-measure (Navy) method</a></li><li><a href="#skinfold">The skinfold method</a></li><li><a href="#bmi-method">The height-and-weight method</a></li><li><a href="#accuracy">Which method is most accurate?</a></li><li><a href="#meaning">What your result means</a></li><li><a href="#faq">FAQ</a></li><li><a href="#sources">Sources</a></li></ol></nav>',
'<h2 id="tape">The tape-measure (Navy) method</h2>',
'<p>Developed by Hodgdon and Beckett at the Naval Health Research Center in 1984, this method predicts body fat from neck and waist circumferences and height, plus hips for women. The same equations appear in the US Army&rsquo;s sample calculations. Measurements go into the equations in inches; plugging centimeters into these constants gives badly wrong results, so the calculator converts for you.</p>',
'<p class="bc-f">Men: 86.010 &times; log10(waist &minus; neck) &minus; 70.041 &times; log10(height) + 36.76</p>',
'<p class="bc-f">Women: 163.205 &times; log10(waist + hips &minus; neck) &minus; 97.684 &times; log10(height) &minus; 78.387</p>',
f'<div class="bc-ex"><p><strong>Worked examples from the Army document:</strong> a woman with a 15-inch neck, 42-inch waist, 44-inch hips and 64-inch height, and a man with a 16-inch neck, 49-inch waist and 69-inch height. The document works them by hand with logarithms rounded to two or three decimals, getting 46.73% and 38.62%, and reports 47% and 39%. Computed exactly, they are {f1(navy("f", 64, 15, 42, 44))}% and {f1(navy("m", 69, 16, 49))}%, which round to the same 47% and 39%.</p></div>',
'<h2 id="skinfold">The skinfold method (Jackson&ndash;Pollock 3-site)</h2>',
'<p>Calipers measure the thickness of a pinch of skin and fat at three sites: chest, abdomen and thigh for men; triceps, suprailiac (just above the hip bone) and thigh for women. Jackson and Pollock&rsquo;s equations turn the sum and your age into body density, and Siri&rsquo;s equation converts density to body fat.</p>',
'<p class="bc-f">Men: density = 1.10938 &minus; 0.0008267&middot;S + 0.0000016&middot;S&sup2; &minus; 0.0002574&middot;age</p>',
'<p class="bc-f">Women: density = 1.0994921 &minus; 0.0009929&middot;S + 0.0000023&middot;S&sup2; &minus; 0.0001392&middot;age</p>',
'<p class="bc-f">Body fat % = 495 &divide; density &minus; 450 (Siri)</p>',
f'<p class="cmb-src">S = sum of the three skinfolds in millimeters. One published reproduction prints the women&rsquo;s age term as 0.0001395 rather than 0.0001392; the difference changes the result by less than 0.1 point even at age 60. Source: <a href="{JP}" rel="noopener">Serra et al., ConScientiae Sa&uacute;de 2009</a>, citing Jackson &amp; Pollock 1978, Jackson, Pollock &amp; Ward 1980 and Siri 1956.</p>',
'<h2 id="bmi-method">The height-and-weight method (Deurenberg)</h2>',
f'<p>Deurenberg and colleagues measured body fat by underwater weighing in 1,229 people and fitted a formula for adults: <strong>body fat % = 1.20 &times; BMI + 0.23 &times; age &minus; 10.8 &times; sex &minus; 5.4</strong>, with sex = 1 for men and 0 for women. Its standard error is 4.1 points, and the authors found it slightly overestimates body fat in people with obesity (<a href="{DEUR}" rel="noopener">Deurenberg et al., Br J Nutr 1991</a>). It needs no tape, but because it starts from BMI it inherits BMI&rsquo;s blind spot: it can&rsquo;t tell muscle from fat.</p>',
'<h2 id="accuracy">Which method is most accurate?</h2>',
f'<p><strong>None of the three is a measurement; all are predictions.</strong> CDC calls DXA the most widely accepted method of measuring body composition, which is why we compare your result with DXA scans rather than with a fitness chart (<a href="{DXX}" rel="noopener">CDC NHANES documentation</a>). Deurenberg&rsquo;s team reported that their BMI formula&rsquo;s error is comparable to skinfold or bioelectrical impedance methods. Careful, repeated measurements help, and running two methods shows the range your true value is likely in.</p>',
'<h2 id="meaning">What your result means</h2>',
f'<p>The calculator shows where your number sits against two references: the <strong>provisional healthy ranges</strong> matched to BMI cut-offs (Gallagher et al., 2000; for example 21&ndash;32.9% for women and 8&ndash;19.9% for men aged 20&ndash;39), and <strong>what US adults your age actually measure</strong> on CDC&rsquo;s DXA scans. The full percentiles, by age and sex, are on our <a href="/body-fat-percentage-chart/">body fat percentage chart</a>. To compare your weight rather than your fat, see <a href="/average-weight/">average weight by height</a>.</p>',
'<h2 id="faq">FAQ</h2>',
'<details class="cmb-faq"><summary><h3>How do I calculate my body fat percentage at home?</h3></summary><p>With a soft tape measure (neck, waist and, for women, hips) using the Navy equations; with skinfold calipers using the Jackson&ndash;Pollock equations; or from your BMI, age and sex using the Deurenberg formula. The calculator above does all three.</p></details>',
'<details class="cmb-faq"><summary><h3>Can I calculate body fat from BMI?</h3></summary><p>Yes, approximately. Deurenberg&rsquo;s formula predicts body fat from BMI, age and sex with a standard error of 4.1 points, but it can&rsquo;t distinguish muscle from fat.</p></details>',
'<details class="cmb-faq"><summary><h3>Why does my smart scale give a different number?</h3></summary><p>Scales, calipers, tape equations and DXA scans all measure different things and carry their own errors, so readings can differ by several points. Track one method over time rather than comparing across methods.</p></details>',
'<details class="cmb-faq"><summary><h3>Does the Navy method work in centimeters?</h3></summary><p>The published constants assume inches. Entering centimeters directly into the inch equations gives a very wrong answer; the calculator converts metric measurements to inches first.</p></details>',
'<details class="cmb-faq"><summary><h3>What is a healthy body fat percentage?</h3></summary><p>Provisional ranges matched to a healthy BMI are 8&ndash;19.9% for men and 21&ndash;32.9% for women aged 20&ndash;39, rising slightly with age (Gallagher et al., 2000). See the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> for every age group.</p></details>',
'<h2 id="sources">Sources</h2>',
'<ol class="cmb-sources">',
f'<li>US Army sample body fat calculations (Table B-5), reproduced in the study protocol <a href="{ARMY}" rel="noopener">NCT02734238</a>, ClinicalTrials.gov. Equations from Hodgdon JA, Beckett MB. Prediction of percent body fat for U.S. Navy men and women from body circumferences and height. Naval Health Research Center reports 84-11 and 84-29, 1984.</li>',
f'<li>Jackson AS, Pollock ML. Br J Nutr 1978;40:497&ndash;504; Jackson AS, Pollock ML, Ward A. Med Sci Sports Exerc 1980;12:175&ndash;81; Siri WE 1956 &mdash; as reproduced in <a href="{JP}" rel="noopener">Serra AJ, et al. ConScientiae Sa&uacute;de 2009;8(1):19&ndash;24</a>.</li>',
f'<li>Deurenberg P, Weststrate JA, Seidell JC. <a href="{DEUR}" rel="noopener">Body mass index as a measure of body fatness: age- and sex-specific prediction formulas</a>. Br J Nutr 1991;65:105&ndash;14.</li>',
f'<li>Gallagher D, et al. <a href="{GAL}" rel="noopener">Healthy percentage body fat ranges</a>. Am J Clin Nutr 2000;72:694&ndash;701.</li>',
f'<li>National Center for Health Statistics. <a href="{DXX}" rel="noopener">NHANES DXA whole body data</a>, 2011&ndash;2018 (comparison percentiles: our calculation).</li>',
'</ol>',
'<p class="cmb-note">This calculator gives estimates for information. It is not a medical test or medical advice.</p>',
'<h2>Related</h2><ul><li><a href="/body-fat-percentage-chart/">Body fat percentage chart by age</a></li><li><a href="/lean-body-mass/">Lean body mass calculator</a></li><li><a href="/average-weight/">Average weight by height</a></li><li><a href="/">BMI calculator</a></li></ul>',
'</article>',
f'<script>window.BC_DATA={json.dumps(TD, separators=(",", ":"))};{DIST}</script>',
f'<script>{JS}</script>')

TITLE = "Body Fat Calculator: Tape, Skinfold & BMI Methods (Free)"
DESC = "Calculate your body fat percentage with the Navy tape method, Jackson–Pollock skinfolds or your BMI, then see how you compare with CDC body scans of US adults."
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
OG = f"https://calculatemybmi.net/{SLUG}/og-{SLUG}.png"
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "WebApplication", "@id": URL + "#app", "name": "Body Fat Calculator", "url": URL, "description": DESC, "applicationCategory": "HealthApplication", "operatingSystem": "Any",
  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "image": OG, "dateModified": "2026-10-04"},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"}, {"@type": "ListItem", "position": 2, "name": "Calculators", "item": "https://calculatemybmi.net/calculators/"}, {"@type": "ListItem", "position": 3, "name": "Body Fat Calculator", "item": URL}]},
 org, person]}
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Body fat calculator: tape, skinfold and BMI methods">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'),
                 (r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="Body fat calculator with three methods, compared with CDC body scans.">'),
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
dr.text((56, 60), "Body fat calculator", font=font(64, True), fill="#111827")
dr.text((56, 150), "Tape measure · skinfold calipers · height & weight", font=font(32), fill="#4B5563")
for i, (t, c) in enumerate((("Navy tape method", "#1F4E79"), ("Jackson–Pollock 3-site", "#6B46C1"), ("Deurenberg BMI formula", "#C2481E"))):
    dr.rounded_rectangle([56, 240 + i * 90, 720, 310 + i * 90], radius=16, fill=c); dr.text((80, 256 + i * 90), t, font=font(34, True), fill="#FFFFFF")
dr.text((56, 540), "Compared with CDC body scans of US adults", font=font(28), fill="#1F2937")
dr.text((56, 585), "calculatemybmi.net", font=font(24, True), fill="#6B7280")
im.save(os.path.join(OUT, SLUG, f"og-{SLUG}.png"), optimize=True)
print(json.dumps({"title_len": len(TITLE), "desc_len": len(DESC), "navy_f": round(navy("f", 64, 15, 42, 44), 2), "navy_m": round(navy("m", 69, 16, 49), 2)}))
