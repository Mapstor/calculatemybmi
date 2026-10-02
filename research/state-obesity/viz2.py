"""Visual + interactive layer for /obesity-rate-by-state/ (v2). Called from gen_page2.py with its globals.
Geometry: us-atlas states-albers-10m (US Census Bureau cartographic boundaries, public domain), simplified,
pre-projected (Albers USA, AK/HI insets). Neighbours come from shared borders in the topology."""
import json, os, html as H

REGION = {**{s: "Northeast" for s in ["Connecticut","Maine","Massachusetts","New Hampshire","Rhode Island","Vermont","New Jersey","New York","Pennsylvania"]},
          **{s: "Midwest" for s in ["Illinois","Indiana","Michigan","Ohio","Wisconsin","Iowa","Kansas","Minnesota","Missouri","Nebraska","North Dakota","South Dakota"]},
          **{s: "South" for s in ["Delaware","Florida","Georgia","Maryland","North Carolina","South Carolina","Virginia","District of Columbia","West Virginia","Alabama","Kentucky","Mississippi","Tennessee","Arkansas","Louisiana","Oklahoma","Texas"]},
          **{s: "West" for s in ["Arizona","Colorado","Idaho","Montana","Nevada","New Mexico","Utah","Wyoming","Alaska","California","Hawaii","Oregon","Washington"]}}
LABEL_MIN_AREA = 1400
LABEL_NUDGE = {"Michigan": (14, 38), "Florida": (16, 6), "Louisiana": (-12, -6), "Kentucky": (8, 4), "Idaho": (0, 22), "Minnesota": (-6, 10),
               "Hawaii": (14, 4), "California": (-10, 8), "Oklahoma": (12, -2), "Virginia": (10, 4), "West Virginia": (-4, 6), "Tennessee": (0, 2)}

def build_viz(g):
    STATES, ABBR, BANDS, NODATA, YEARS, val, AGE, fmt, band, ink = (g[k] for k in ("STATES", "ABBR", "BANDS", "NODATA", "YEARS", "val", "AGE", "fmt", "band", "ink"))
    ok25, ge35, chg, SOURCED, hi_v, hi_s, lo_v, lo_s, dc25 = (g[k] for k in ("ok25", "ge35", "chg", "SOURCED", "hi_v", "hi_s", "lo_v", "lo_s", "dc25"))
    here = os.path.dirname(os.path.abspath(__file__))
    GEO = json.load(open(os.path.join(here, "states_paths.json")))
    ALL = STATES + ["District of Columbia"]
    assert set(GEO) == set(ALL), set(GEO) ^ set(ALL)

    # ---------- static choropleth (2025) ----------
    parts = ['<defs><pattern id="obs-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<rect width="6" height="6" fill="#EEF0F3"/><line x1="0" y1="0" x2="0" y2="6" stroke="#C9CED6" stroke-width="2"/></pattern></defs>']
    for s in STATES:
        v = val(2025, s); fill = band(v[0])[1] if v else "url(#obs-hatch)"
        lab = f"{s}: {fmt(v[0])}% in 2025" if v else f"{s}: no 2025 estimate"
        parts.append(f'<path class="obs-st" data-s="{ABBR[s]}" d="{GEO[s]["d"]}" fill="{fill}" tabindex="0" role="button" aria-label="{H.escape(lab)}"><title>{H.escape(lab)}</title></path>')
    labels = []
    for s in STATES:
        if GEO[s]["a"] < LABEL_MIN_AREA: continue
        x, y = GEO[s]["c"]; dx, dy = LABEL_NUDGE.get(s, (0, 0))
        v = val(2025, s); col = band(v[0])[1] if v else "#EEF0F3"
        labels.append(f'<text class="obs-lab" x="{x + dx:.1f}" y="{y + dy + 5:.1f}" text-anchor="middle" fill="{ink(col)}" data-s="{ABBR[s]}">{ABBR[s]}</text>')
    dx_, dy_ = GEO["District of Columbia"]["c"]; v = val(2025, "District of Columbia")
    parts.append(f'<g class="obs-dcg"><line x1="{dx_}" y1="{dy_}" x2="{dx_ + 34}" y2="{dy_ + 40}" stroke="#6B7280" stroke-width="1.2"/>'
                 f'<circle class="obs-st obs-dc" data-s="DC" cx="{dx_ + 34}" cy="{dy_ + 40}" r="9" fill="{band(v[0])[1]}" tabindex="0" role="button" aria-label="District of Columbia: {fmt(v[0])}% in 2025"><title>District of Columbia: {fmt(v[0])}% in 2025</title></circle>'
                 f'<text class="obs-lab obs-lab-dc" x="{dx_ + 48}" y="{dy_ + 45}" fill="#1F2937">DC</text></g>')
    MAP = ('<svg id="obs-map-svg" viewBox="0 0 975 610" width="975" height="610" role="group" aria-labelledby="obs-map-t">'
           '<title id="obs-map-t">Map of adult obesity prevalence by US state, 2025</title>' + "".join(parts) + '<g aria-hidden="true">' + "".join(labels) + "</g></svg>")
    LEGEND = "".join(f'<li><span class="obs-sw" style="background:{col}"></span>{lab.replace(" to under ", "–").replace("% or higher", "%+")}</li>' for lo, hi, lab, col in BANDS[1:]) + \
             '<li><span class="obs-sw obs-sw-na"></span>No estimate</li>'

    # ---------- highlight cards ----------
    big = chg[0]
    CARDS = (f'<div class="obs-cards">'
             f'<div class="obs-kpi" style="--c:{band(hi_v)[1]}"><span class="obs-kpi-l">Highest, 2025</span><span class="obs-kpi-n">{fmt(hi_v)}%</span><span class="obs-kpi-s">{hi_s}</span></div>'
             f'<div class="obs-kpi" style="--c:{band(lo_v)[1]}"><span class="obs-kpi-l">Lowest, 2025</span><span class="obs-kpi-n">{fmt(lo_v)}%</span><span class="obs-kpi-s">{lo_s}</span></div>'
             f'<div class="obs-kpi" style="--c:#C2481E"><span class="obs-kpi-l">States at 35%+</span><span class="obs-kpi-n">{ge35[2025]}</span><span class="obs-kpi-s">of {len(ok25)} with 2025 data (0 in 2011)</span></div>'
             f'<div class="obs-kpi" style="--c:#7F2A10"><span class="obs-kpi-l">Biggest rise since 2011</span><span class="obs-kpi-n">+{fmt(big[0])}</span><span class="obs-kpi-s">points, {big[1]}</span></div></div>')

    # ---------- ranked bar lists ----------
    def barlist(L, lo=20.0, hi=42.0):
        rows = []
        for i, (v, s) in enumerate(L, 1):
            w = (v - lo) / (hi - lo) * 100; col = band(v)[1]
            rows.append(f'<li><span class="obs-bl-n">{i}</span><span class="obs-bl-s">{H.escape(s)}</span><span class="obs-bl-t"><span class="obs-bl-b" style="width:{w:.1f}%;background:{col}"></span></span><span class="obs-bl-v">{fmt(v)}%</span></li>')
        return '<ol class="obs-bl">' + "".join(rows) + "</ol>"

    # ---------- stacked band distribution chart ----------
    def dist_chart():
        W, Hh, L, B, T = 680, 330, 34, 46, 26
        bw = (W - L - 8) / len(YEARS); sc = (Hh - B - T) / 50.0
        cats = [(lab, col) for lo, hi, lab, col in BANDS] + [("No estimate", "#D1D5DB")]
        out = [f'<line x1="{L}" y1="{Hh - B}" x2="{W - 4}" y2="{Hh - B}" stroke="#9CA3AF"/>']
        for t in (0, 10, 20, 30, 40, 50):
            yy = Hh - B - t * sc
            out.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W - 4}" y2="{yy:.1f}" stroke="#EEF0F3"/><text x="{L - 6}" y="{yy + 5:.1f}" text-anchor="end" class="obs-ax">{t}</text>')
        for i, y in enumerate(YEARS):
            cnt = {lab: 0 for lab, _ in cats}
            for s in STATES:
                v = val(y, s); cnt[band(v[0])[0] if v else "No estimate"] += 1
            x = L + i * bw + 3; base = Hh - B
            for lab, col in cats:
                n = cnt[lab]
                if not n: continue
                h = n * sc; base -= h
                out.append(f'<rect x="{x:.1f}" y="{base:.1f}" width="{bw - 6:.1f}" height="{h:.1f}" fill="{col}"><title>{y}: {n} states, {lab.lower()}</title></rect>')
            n35 = ge35[y]
            out.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{T - 8}" text-anchor="middle" class="obs-ax-b">{n35}</text>')
            if i % 2 == 0: out.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{Hh - B + 22}" text-anchor="middle" class="obs-ax">{y}</text>')
        out.append(f'<text x="{L}" y="{Hh - 6}" class="obs-ax">Number of states in each band; top row: states at 35% or higher</text>')
        return (f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-labelledby="obs-dist-t">'
                f'<title id="obs-dist-t">How the 50 states shifted between obesity bands, 2011 to 2025</title>' + "".join(out) + "</svg>")
    DIST_LEGEND = "".join(f'<li><span class="obs-sw" style="background:{col}"></span>{lab.replace(" to under ", "–").replace("% or higher", "%+")}</li>' for lo, hi, lab, col in BANDS) + \
                  '<li><span class="obs-sw" style="background:#D1D5DB"></span>No estimate</li>'

    # ---------- concept figure (self-reported vs measured) ----------
    CONCEPT = f'''<svg viewBox="0 0 640 300" width="640" height="300" role="img" aria-labelledby="obs-k-t obs-k-d">
<title id="obs-k-t">Self-reported state survey versus measured national survey</title>
<desc id="obs-k-d">State maps use height and weight people report on the phone. The national figure comes from people weighed and measured in an exam.</desc>
<rect x="10" y="10" width="300" height="280" rx="14" fill="#FFF7F2" stroke="#F3D3AE"/>
<rect x="330" y="10" width="300" height="280" rx="14" fill="#F3F4F6" stroke="#D1D5DB"/>
<text x="160" y="44" text-anchor="middle" class="obs-k-h">State maps (BRFSS)</text>
<text x="480" y="44" text-anchor="middle" class="obs-k-h">National exam (NHANES)</text>
<rect x="110" y="66" width="100" height="62" rx="10" fill="#FFFFFF" stroke="#E0612D" stroke-width="3"/>
<circle cx="160" cy="88" r="7" fill="#E0612D"/><rect x="146" y="100" width="28" height="9" rx="4" fill="#E0612D"/>
<text x="160" y="152" text-anchor="middle" class="obs-k-s">Phone survey: people</text>
<text x="160" y="170" text-anchor="middle" class="obs-k-s">report height and weight</text>
<text x="160" y="222" text-anchor="middle" class="obs-k-big">{fmt(dc25)}–{fmt(hi_v)}%</text>
<text x="160" y="248" text-anchor="middle" class="obs-k-s">2025, by state or DC</text>
<rect x="436" y="62" width="88" height="14" rx="4" fill="#9CA3AF"/><rect x="474" y="76" width="12" height="40" fill="#9CA3AF"/>
<rect x="446" y="116" width="68" height="14" rx="4" fill="#6B7280"/>
<text x="480" y="152" text-anchor="middle" class="obs-k-s">Exam: staff measure</text>
<text x="480" y="170" text-anchor="middle" class="obs-k-s">height and weight</text>
<text x="480" y="222" text-anchor="middle" class="obs-k-big">{SOURCED["nhanes"]}%</text>
<text x="480" y="248" text-anchor="middle" class="obs-k-s">2021–2023, adults 20+</text>
</svg>'''

    # ---------- data for the interactive layer ----------
    JD = {"years": YEARS, "bands": [[lo, hi, lab, col] for lo, hi, lab, col in BANDS],
          "region25": {"Midwest": SOURCED["midwest"], "South": SOURCED["south"], "West": SOURCED["west"], "Northeast": SOURCED["northeast"]},
          "s": {ABBR[s]: {"n": s, "r": REGION[s], "nb": [ABBR[x] for x in GEO[s]["n"] if x in ABBR],
                          "v": [list(val(y, s)) if val(y, s) else None for y in YEARS],
                          "age": [list(AGE[s][k]) if AGE[s].get(k) else None for k in ("18-39", "40-59", "60+")]} for s in ALL}}

    JS = r"""
(function(){var d=window.OBS_DATA,Y=d.years,N=Y.length,ST=Object.keys(d.s).filter(function(k){return k!=='DC';});
var $=function(i){return document.getElementById(i);},sl=$('obs-year'),yo=$('obs-year-out'),cap=$('obs-map-cap'),sel=$('obs-state'),out=$('obs-panel'),tip=$('obs-tip'),wrap=$('obs-mapwrap'),play=$('obs-play');
var cur=null;
function f1(x){return x.toFixed(1);}
function band(v){for(var i=0;i<d.bands.length;i++){if(v>=d.bands[i][0]&&v<d.bands[i][1])return d.bands[i];}return d.bands[d.bands.length-1];}
function ink(c){return(c==='#C2481E'||c==='#7F2A10'||c==='#E5743F')?'#FFFFFF':'#1F2937';}
function yi(){return +sl.value-Y[0];}
function vals(i){var a=[];ST.forEach(function(k){var v=d.s[k].v[i];if(v)a.push([v[0],k]);});a.sort(function(p,q){return q[0]-p[0];});return a;}
function median(a){var b=a.map(function(x){return x[0];}).sort(function(p,q){return p-q;}),n=b.length;return n?(n%2?b[(n-1)/2]:(b[n/2-1]+b[n/2])/2):null;}
function rankOf(i,k){var v=d.s[k].v[i];if(!v)return null;var r=1,n=0;ST.forEach(function(j){var w=d.s[j].v[i];if(w){n++;if(w[0]>v[0])r++;}});return [r,n];}
function paint(i){var y=Y[i];yo.textContent=y;var n35=0,nd=0;
 document.querySelectorAll('#obs-map-svg .obs-st').forEach(function(el){var k=el.getAttribute('data-s'),v=d.s[k].v[i];el.setAttribute('fill',v?band(v[0])[3]:'url(#obs-hatch)');
  var lab=d.s[k].n+(v?': '+f1(v[0])+'% in '+y:': no '+y+' estimate');el.setAttribute('aria-label',lab);var t=el.querySelector('title');if(t)t.textContent=lab;
  if(k!=='DC'){if(v&&v[0]>=35)n35++;if(!v)nd++;}});
 document.querySelectorAll('#obs-map-svg .obs-lab[data-s]').forEach(function(t){var v=d.s[t.getAttribute('data-s')].v[i];t.setAttribute('fill',ink(v?band(v[0])[3]:'#EEF0F3'));});
 cap.textContent=y+': '+n35+' of '+(50-nd)+' states with an estimate had adult obesity of 35% or higher'+(nd?' ('+nd+' without an estimate).':'.');
 if(cur)show(cur,true);}
function bar(label,v,max,col,strong){var w=Math.max(2,(v-15)/(max-15)*100);return '<div class="obs-cb'+(strong?' obs-cb-me':'')+'"><span class="obs-cb-l">'+label+'</span><span class="obs-cb-t"><span class="obs-cb-b" style="width:'+w.toFixed(1)+'%;background:'+col+'"></span></span><span class="obs-cb-v">'+f1(v)+'%</span></div>';}
function ciBar(v,med){var lo=20,hi=45,X=function(x){return ((x-lo)/(hi-lo)*100).toFixed(2)+'%';};
 return '<div class="obs-ci" aria-hidden="true"><div class="obs-ci-track"><span class="obs-ci-band" style="left:'+X(v[1])+';width:calc('+X(v[2])+' - '+X(v[1])+')"></span><span class="obs-ci-dot" style="left:'+X(v[0])+'"></span>'+(med?'<span class="obs-ci-med" style="left:'+X(med)+'" title="Median state"></span>':'')+'</div><div class="obs-ci-ax"><span>20%</span><span>30%</span><span>40%</span></div></div>';}
function trend(k,i){var s=d.s[k],W=480,H=230,L=40,R=12,T=16,B=30,lo=15,hi=50;function X(j){return L+j*(W-L-R)/(N-1);}function Yp(v){return H-B-(v-lo)*(H-T-B)/(hi-lo);}
 var g='',band='',line='',dots='',segs=[],seg=[];s.v.forEach(function(v,j){if(v)seg.push([j,v]);else{if(seg.length)segs.push(seg);seg=[];}});if(seg.length)segs.push(seg);
 [20,30,40,50].forEach(function(t){g+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+Yp(t)+'" y2="'+Yp(t)+'" stroke="#EEF0F3"/><text x="'+(L-6)+'" y="'+(Yp(t)+4)+'" text-anchor="end" class="obs-ax">'+t+'%</text>';});
 var med='';for(var j=0;j<N;j++){var m=median(vals(j));if(m!==null)med+=(med?' L':'M')+X(j).toFixed(1)+' '+Yp(m).toFixed(1);}
 segs.forEach(function(sg){var up=sg.map(function(p){return X(p[0]).toFixed(1)+' '+Yp(p[1][2]).toFixed(1);}),dn=sg.slice().reverse().map(function(p){return X(p[0]).toFixed(1)+' '+Yp(p[1][1]).toFixed(1);});
  band+='<path d="M'+up.join(' L')+' L'+dn.join(' L')+' Z" fill="#F4A774" opacity=".35"/>';
  line+='<path d="M'+sg.map(function(p){return X(p[0]).toFixed(1)+' '+Yp(p[1][0]).toFixed(1);}).join(' L')+'" fill="none" stroke="#B3431A" stroke-width="2.5"/>';
  sg.forEach(function(p){dots+='<circle cx="'+X(p[0]).toFixed(1)+'" cy="'+Yp(p[1][0]).toFixed(1)+'" r="'+(p[0]===i?5:3)+'" fill="'+(p[0]===i?'#7F2A10':'#B3431A')+'" stroke="#fff" stroke-width="'+(p[0]===i?2:0)+'"/>';});});
 var mk='<line x1="'+X(i)+'" x2="'+X(i)+'" y1="'+T+'" y2="'+(H-B)+'" stroke="#9CA3AF" stroke-dasharray="3 3"/>';
 var ax='';[0,4,8,12,14].forEach(function(j){ax+='<text x="'+X(j)+'" y="'+(H-8)+'" text-anchor="middle" class="obs-ax">'+Y[j]+'</text>';});
 return '<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="'+s.n+' adult obesity 2011 to 2025, with 95% confidence band and the median state">'+g+mk+band+'<path d="'+med+'" fill="none" stroke="#6B7280" stroke-width="1.5" stroke-dasharray="5 4"/>'+line+dots+ax+'</svg>'+
  '<p class="obs-key"><span class="obs-key-l"></span>'+s.n+' <span class="obs-key-b"></span>95% confidence band <span class="obs-key-m"></span>Median state</p>';}
function show(k,keep){cur=k;var s=d.s[k],i=yi(),y=Y[i],v=s.v[i],h='',isS=k!=='DC';
 var a=vals(i),med=median(a),rk=isS?rankOf(i,k):null,col=v?band(v[0])[3]:'#9CA3AF';
 h+='<div class="obs-head" style="--c:'+col+'"><div><p class="obs-tag">'+s.r+(isS?'':' · not a state')+'</p><h3>'+s.n+' <span class="obs-y">'+y+'</span></h3></div>';
 if(v){h+='<div class="obs-num"><span class="obs-num-v">'+f1(v[0])+'%</span><span class="obs-num-s">of adults had obesity · about '+Math.round(v[0]/10)+' in 10</span></div>';
  if(rk)h+='<div class="obs-rank"><span class="obs-rank-n">#'+rk[0]+'</span><span class="obs-rank-s">of '+rk[1]+' states<br>1 = highest</span></div>';}
 h+='</div>';
 if(!v){var li=-1;s.v.forEach(function(w,j){if(w&&j<=i)li=j;});if(li<0)s.v.forEach(function(w,j){if(w&&li<0)li=j;});
  h+='<div class="obs-callout">CDC published <strong>no '+y+' estimate</strong> for '+s.n+': too few reliable survey responses that year.'+(li>=0?' Nearest year with data: <strong>'+f1(s.v[li][0])+'% in '+Y[li]+'</strong> (95% CI '+f1(s.v[li][1])+'–'+f1(s.v[li][2])+'%).':'')+'</div>';}
 else{
  h+=ciBar(v,med)+'<p class="obs-small">Bar: the 95% confidence interval ('+f1(v[1])+'–'+f1(v[2])+'%) · dot: the estimate · tick: the median state ('+f1(med)+'%).</p>';
  var why=[];var dm=v[0]-med;why.push('<strong>'+(Math.abs(dm)<0.05?'Right at':(Math.abs(dm).toFixed(1)+' points '+(dm>0?'above':'below')))+' the median state</strong> ('+f1(med)+'%) in '+y+'.');
  if(isS){var top=a[0],bot=a[a.length-1];why.push('The range that year ran from '+d.s[bot[1]].n+' ('+f1(bot[0])+'%) to '+d.s[top[1]].n+' ('+f1(top[0])+'%).');}
  var nb=s.nb.filter(function(n){return d.s[n].v[i];});if(nb.length){var hiN=nb.filter(function(n){return d.s[n].v[i][0]>v[0];}).length;
   why.push((hiN===0?'<strong>Highest of its '+nb.length+' neighbors with data.</strong>':hiN===nb.length?'<strong>Lowest of its '+nb.length+' neighbors with data.</strong>':'Higher than '+(nb.length-hiN)+' of its '+nb.length+' neighbors with data.'));}
  else if(!s.nb.length)why.push('No land neighbors to compare with.');
  if(i>0&&s.v[i-1]){var p=s.v[i-1],dd=v[0]-p[0],sig=(v[1]>p[2]||v[2]<p[1]);why.push('From '+Y[i-1]+': <strong>'+(dd>=0?'+':'')+f1(dd)+' points</strong> — '+(sig?'larger than the margin of error (the two years’ 95% intervals don’t overlap).':'within the margin of error, so not a confirmed change.'));}
  var f=s.v[0];if(f&&i>0){var r0=rankOf(0,k);why.push('Since 2011: <strong>'+(v[0]-f[0]>=0?'+':'')+f1(v[0]-f[0])+' points</strong> ('+f1(f[0])+'% → '+f1(v[0])+'%)'+(isS&&r0&&rk?'; rank '+r0[0]+' then, '+rk[0]+' now.':'.'));}
  var pk=-1;s.v.forEach(function(w,j){if(w&&(pk<0||w[0]>s.v[pk][0]))pk=j;});if(pk>=0)why.push('Highest year on record (2011–2025): <strong>'+Y[pk]+', '+f1(s.v[pk][0])+'%</strong>.');
  if(y===2025&&d.region25[s.r])why.push('CDC’s 2025 figure for the '+s.r+' as a whole: '+d.region25[s.r]+'%.');
  h+='<ul class="obs-why">'+why.map(function(w){return '<li>'+w+'</li>';}).join('')+'</ul>';
  var mx=a.length?a[0][0]:45,cmp='<h4>How '+s.n+' compares in '+y+'</h4>'+bar(s.n,v[0],Math.max(mx,v[0]),col,true)+bar('Median state',med,mx,'#9CA3AF')+(isS?'':'')+bar('Highest: '+d.s[a[0][1]].n,a[0][0],mx,band(a[0][0])[3])+bar('Lowest: '+d.s[a[a.length-1][1]].n,a[a.length-1][0],mx,band(a[a.length-1][0])[3]);
  if(nb.length){var nbs=nb.map(function(n){return [d.s[n].v[i][0],n];}).concat([[v[0],k]]).sort(function(p,q){return q[0]-p[0];});cmp+='<h4>Neighbors in '+y+'</h4>'+nbs.map(function(p){return bar(d.s[p[1]].n,p[0],Math.max(mx,p[0]),band(p[0])[3],p[1]===k);}).join('');}
  h+='<div class="obs-cmp">'+cmp+'</div>';}
 h+='<h4>'+s.n+', 2011–2025</h4><div class="obs-trend">'+trend(k,i)+'</div>';
 var ag=s.age;if(ag&&ag[0]&&ag[1]&&ag[2]){var mxA=Math.max(ag[0][0],ag[1][0],ag[2][0]),labs=['18–39','40–59','60+'],ii=[0,1,2].filter(function(j){return ag[j][0]===mxA;})[0];
  h+='<h4>By age, 2025</h4>'+[0,1,2].map(function(j){return bar('Ages '+labs[j],ag[j][0],Math.max(50,mxA),j===ii?'#B3431A':'#F4A774',j===ii);}).join('')+
   '<p class="obs-small">'+(ii===1?'Ages 40–59 had the highest rate, '+f1(ag[1][0]-ag[0][0])+' points above ages 18–39 and '+f1(ag[1][0]-ag[2][0])+' above ages 60+.':'Ages '+labs[ii]+' had the highest rate in '+s.n+'.')+' Age estimates have wider margins of error than the all-adult figure.</p>';}
 else if(isS)h+='<p class="obs-small">No 2025 age breakdown for '+s.n+' (insufficient data).</p>';
 h+='<p class="cmb-src">Source: CDC, Adult Obesity Prevalence Maps (BRFSS), self-reported height and weight. Ranks, medians, neighbor and year-to-year comparisons are our calculations from CDC’s estimates.</p>';
 out.innerHTML=h;out.hidden=false;document.querySelectorAll('#obs-map-svg .obs-st').forEach(function(el){el.classList.toggle('obs-on',el.getAttribute('data-s')===k);});
 if(!keep)out.scrollIntoView({behavior:'smooth',block:'start'});}
sl.addEventListener('input',function(){paint(yi());});
$('obs-go').addEventListener('click',function(){show(sel.value);});
var timer=null;play.addEventListener('click',function(){if(timer){clearInterval(timer);timer=null;play.textContent='▶ Play 2011–2025';return;}
 if(+sl.value>=Y[N-1])sl.value=Y[0];paint(yi());play.textContent='❚❚ Pause';timer=setInterval(function(){if(+sl.value>=Y[N-1]){clearInterval(timer);timer=null;play.textContent='▶ Play 2011–2025';return;}sl.value=+sl.value+1;paint(yi());},900);});
document.querySelectorAll('#obs-map-svg .obs-st').forEach(function(el){var k=el.getAttribute('data-s');
 function pick(){sel.value=k;show(k);}
 el.addEventListener('click',pick);el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();pick();}});
 el.addEventListener('mousemove',function(e){var v=d.s[k].v[yi()],r=wrap.getBoundingClientRect();tip.innerHTML='<strong>'+d.s[k].n+'</strong> '+(v?f1(v[0])+'%':'no estimate')+' <span>'+Y[yi()]+'</span>';tip.style.left=(e.clientX-r.left+12)+'px';tip.style.top=(e.clientY-r.top+12)+'px';tip.hidden=false;});
 el.addEventListener('mouseleave',function(){tip.hidden=true;});});
})();
"""

    CSS = """
.obs-cards{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 14px}
.obs-cards .obs-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px}
@media (min-width:760px){.obs-cards .obs-kpi{flex:1 1 calc(25% - 10px)}}
.obs-kpi{background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}
.obs-kpi-l{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:#6B7280;font-weight:700}
.obs-kpi-n{font-size:2rem;font-weight:800;line-height:1.1;color:#111827}
.obs-kpi-s{font-size:.9rem;color:#374151}
.obs-tool{border:1px solid #EEF0F3;border-radius:16px;padding:16px;margin:8px 0 10px;background:linear-gradient(180deg,#FFFFFF 0%,#FFF9F5 100%);box-shadow:0 6px 24px rgba(17,24,39,.07)}
.obs-mapwrap{position:relative;margin:0 auto;max-width:900px}
.obs-mapwrap svg{display:block;width:100%;height:auto}
.obs-st{stroke:#FFFFFF;stroke-width:1;cursor:pointer;outline:none;transition:opacity .15s}
.obs-st:hover,.obs-st:focus{stroke:#111827;stroke-width:2}
.obs-st.obs-on{stroke:#111827;stroke-width:3}
.obs-lab{font:700 14px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;pointer-events:none;paint-order:stroke;stroke:rgba(255,255,255,.0)}
.obs-lab-dc{font-size:15px}
@media (max-width:560px){.obs-lab{display:none}.obs-lab-dc{display:inline}}
.obs-tip{position:absolute;pointer-events:none;background:#111827;color:#fff;padding:6px 10px;border-radius:8px;font-size:.9rem;white-space:nowrap;box-shadow:0 4px 14px rgba(0,0,0,.2);z-index:2}
.obs-tip span{opacity:.7;margin-left:4px}
.obs-tip[hidden]{display:none}
.obs-legend{display:flex;flex-wrap:wrap;gap:6px 14px;list-style:none;padding:0;margin:10px 0 0;font-size:.85em;color:#374151}
.obs-legend li{display:flex;align-items:center;gap:6px;margin-right:6px}
.obs-sw{display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid rgba(0,0,0,.08)}
.obs-sw-na{background:repeating-linear-gradient(45deg,#EEF0F3 0 3px,#C9CED6 3px 5px)}
.obs-ctl{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin:14px 0 4px}
.obs-ctl label{font-weight:700}
#obs-year{flex:1 1 200px;min-height:44px;accent-color:#C2481E}
#obs-state{min-height:44px;font-size:16px;max-width:100%;border-radius:8px}
#obs-go,#obs-play{min-height:44px;padding:10px 16px;font-weight:700;cursor:pointer;border-radius:10px;border:0;background:#C2481E;color:#fff}
#obs-play{background:#1F2937}
.obs-panel{margin-top:14px}
.obs-panel[hidden]{display:none}
.obs-head{display:flex;flex-wrap:wrap;align-items:center;gap:12px 22px;border-radius:14px;padding:14px 16px;background:#fff;border-left:8px solid var(--c);box-shadow:0 4px 16px rgba(17,24,39,.08)}
.obs-head h3{margin:0;font-size:1.5rem}
.obs-y{font-weight:600;color:#6B7280;font-size:1.1rem}
.obs-tag{margin:0;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:#6B7280;font-weight:700}
.obs-num{display:flex;flex-direction:column}
.obs-num-v{font-size:2.6rem;font-weight:800;line-height:1;color:#7F2A10}
.obs-num-s{font-size:.9rem;color:#374151}
.obs-rank{display:flex;align-items:center;gap:8px;background:#111827;color:#fff;border-radius:12px;padding:8px 12px}
.obs-rank-n{font-size:1.6rem;font-weight:800}
.obs-rank-s{font-size:.75rem;line-height:1.2;opacity:.85}
.obs-ci{margin:16px 4px 2px}
.obs-ci-track{position:relative;height:16px;border-radius:8px;background:#F3F4F6}
.obs-ci-band{position:absolute;top:3px;height:10px;border-radius:5px;background:#F4A774}
.obs-ci-dot{position:absolute;top:-2px;width:20px;height:20px;margin-left:-10px;border-radius:50%;background:#7F2A10;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3)}
.obs-ci-med{position:absolute;top:-6px;width:3px;height:28px;margin-left:-1.5px;background:#374151}
.obs-ci-ax{display:flex;justify-content:space-between;font-size:.75rem;color:#6B7280;margin-top:4px}
.obs-small{font-size:.85rem;color:#4B5563;margin:4px 0 10px}
.obs-why{margin:10px 0 6px;padding-left:1.2em}
.obs-why li{margin:6px 0}
.obs-callout{background:#FFF7F2;border:1px solid #F3D3AE;border-radius:12px;padding:12px 14px;margin:12px 0}
.obs-cmp h4,.obs-panel h4{margin:16px 0 8px;font-size:1rem}
.obs-cb{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:.92rem}
.obs-cb>span{margin-right:6px}
.obs-cb-l{flex:0 0 38%;min-width:104px;line-height:1.2;color:#374151}
.obs-cb-t{flex:1 1 auto;height:14px;border-radius:7px;background:#F3F4F6;overflow:hidden}
.obs-cb-b{display:block;height:100%;border-radius:7px}
.obs-cb-v{flex:0 0 54px;text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
.obs-cb-me .obs-cb-l{font-weight:800;color:#111827}
.obs-trend svg{display:block;width:100%;max-width:600px;height:auto}
.obs-ax{font:14px system-ui,sans-serif;fill:#6B7280}
.obs-ax-b{font:700 13px system-ui,sans-serif;fill:#7F2A10}
.obs-key{font-size:.8rem;color:#4B5563;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;margin:4px 0 8px}
.obs-key span{display:inline-block;width:18px;height:4px;border-radius:2px;vertical-align:middle;margin-right:4px}
.obs-key-l{background:#B3431A}.obs-key-b{background:#F4A774;height:10px!important}.obs-key-m{background:repeating-linear-gradient(90deg,#6B7280 0 5px,transparent 5px 9px)}
.obs-bl{list-style:none;padding:0;margin:6px 0 12px}
.obs-bl li{display:flex;align-items:center;gap:8px;margin:5px 0}
.obs-bl li>span{margin-right:6px}
.obs-bl-n{flex:0 0 22px;font-weight:800;color:#9CA3AF;text-align:right}
.obs-bl-s{flex:0 0 34%;min-width:96px;font-weight:700}
.obs-bl-t{flex:1 1 auto;height:14px;border-radius:7px;background:#F3F4F6;overflow:hidden}
.obs-bl-b{display:block;height:100%;border-radius:7px}
.obs-bl-v{flex:0 0 54px;text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
.obs-cols{display:flex;flex-wrap:wrap;gap:4px 28px}
.obs-cols>div{flex:1 1 320px;min-width:0}
.obs-regions{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 14px}
.obs-regions .obs-reg{flex:1 1 calc(50% - 8px);box-sizing:border-box;margin-bottom:6px}
.obs-reg{border-radius:10px;padding:10px 12px;background:#fff;border:1px solid #EEF0F3;border-left:6px solid var(--c)}
.obs-reg b{display:block;font-size:1.4rem}
.obs-k-h{font:700 20px system-ui,sans-serif;fill:#1F2937}
.obs-k-s{font:18px system-ui,sans-serif;fill:#374151}
.obs-k-big{font:800 34px system-ui,sans-serif;fill:#B3431A}
.obs-rk td.obs-v25{background-image:linear-gradient(90deg,var(--c) 0,var(--c) var(--w),transparent var(--w));background-size:100% 6px;background-repeat:no-repeat;background-position:0 100%}
"""
    return dict(map=MAP, legend=LEGEND, cards=CARDS, barlist=barlist, dist=dist_chart(), dist_legend=DIST_LEGEND, concept=CONCEPT,
                data=JD, js=JS, css=CSS, region=REGION)
