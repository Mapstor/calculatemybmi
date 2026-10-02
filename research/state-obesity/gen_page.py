#!/usr/bin/env python3
"""Build /obesity-rate-by-state/ from the verified CDC BRFSS files, inside the calculatemybmi shell.
Inputs : cdc-brfss-adult-obesity-by-state-2011-2025.csv, cdc-brfss-adult-obesity-by-state-and-age-2025.csv,
         SHELL = an existing built page (us-obesity-statistics/index.html) for head/header/footer.
Output : OUT/obesity-rate-by-state/{index.html, og-obesity-rate-by-state.png, *.csv}
Every number in the prose is computed here from the data or taken from the SOURCED dict (CDC page text)."""
import csv, json, re, sys, os, html as H
from collections import Counter, defaultdict

ROOT = sys.argv[1]            # repo copy containing us-obesity-statistics/index.html
OUT = sys.argv[2]             # output dir (repo copy root)
DATA = os.path.dirname(os.path.abspath(__file__))
SLUG = "obesity-rate-by-state"
URL = f"https://calculatemybmi.net/{SLUG}/"
CDC_PAGE = "https://www.cdc.gov/obesity/data-and-statistics/adult-obesity-prevalence-maps.html"
CDC_PDF = "https://www.cdc.gov/obesity/media/pdfs/2026/09/2011-2025_overall-obesity-prevalence-maps-508.pdf"
CDC_CSV = "https://www.cdc.gov/obesity/media/files/2026/09/2_2025-Obesity-by-state.csv"
NHANES = "https://www.cdc.gov/nchs/products/databriefs/db508.htm"
CSV1 = "obesity-by-state-cdc-brfss-2011-2025.csv"
CSV2 = "obesity-by-state-and-age-cdc-brfss-2025.csv"
# Figures quoted from CDC's maps page text (updated 24 Sep 2026) and NCHS Data Brief 508 — verified in chat
SOURCED = dict(midwest="35.5", south="34.8", west="30.7", northeast="29.6", nohs="38.1", hs="35.1", somecol="36.8", college="27.8",
               mid_vs_young="36", mid_vs_old="25", nhanes="40.3", gallup="37.0")

ABBR = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE",
 "District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
 "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
 "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
 "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI",
 "South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
 "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","Guam":"GU","Puerto Rico":"PR","Virgin Islands":"VI"}
NONSTATE = {"District of Columbia","Guam","Puerto Rico","Virgin Islands"}
GRID = {"AK":(0,0),"ME":(11,0),"VT":(10,1),"NH":(11,1),"WA":(1,2),"ID":(2,2),"MT":(3,2),"ND":(4,2),"MN":(5,2),"IL":(6,2),"WI":(7,2),
 "MI":(8,2),"NY":(9,2),"RI":(10,2),"MA":(11,2),"OR":(1,3),"NV":(2,3),"WY":(3,3),"SD":(4,3),"IA":(5,3),"IN":(6,3),"OH":(7,3),"PA":(8,3),
 "NJ":(9,3),"CT":(10,3),"CA":(1,4),"UT":(2,4),"CO":(3,4),"NE":(4,4),"MO":(5,4),"KY":(6,4),"WV":(7,4),"VA":(8,4),"MD":(9,4),"DE":(10,4),
 "AZ":(2,5),"NM":(3,5),"KS":(4,5),"AR":(5,5),"TN":(6,5),"NC":(7,5),"SC":(8,5),"DC":(9,5),"OK":(4,6),"LA":(5,6),"MS":(6,6),"AL":(7,6),
 "GA":(8,6),"HI":(0,7),"TX":(4,7),"FL":(9,7)}
BANDS = [(0,20,"Under 20%","#FDF1E6"),(20,25,"20% to under 25%","#FAD5B7"),(25,30,"25% to under 30%","#F4A774"),
         (30,35,"30% to under 35%","#E5743F"),(35,40,"35% to under 40%","#C2481E"),(40,101,"40% or higher","#7F2A10")]
NODATA = "#E5E7EB"

def band(v):
    for lo, hi, lab, col in BANDS:
        if lo <= v < hi: return lab, col
def fmt(v): return f"{v:.1f}"
def ink(col): return "#FFFFFF" if col in ("#C2481E", "#7F2A10", "#E5743F") else "#1F2937"

# ---------- data ----------
D = {}
for r in csv.DictReader(open(os.path.join(DATA, "cdc-brfss-adult-obesity-by-state-2011-2025.csv"))):
    D[(int(r["year"]), r["state"])] = None if r["status"] != "ok" else (float(r["prevalence_pct"]), float(r["ci95_low"]), float(r["ci95_high"]))
AGE = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(DATA, "cdc-brfss-adult-obesity-by-state-and-age-2025.csv"))):
    AGE[r["state"]][r["age_group"]] = None if r["status"] != "ok" else (float(r["prevalence_pct"]), float(r["ci95_low"]), float(r["ci95_high"]))
YEARS = list(range(2011, 2026))
STATES = sorted(s for s in ABBR if s not in NONSTATE)
assert len(STATES) == 50
def val(y, s): return D.get((y, s))
ok25 = sorted(((val(2025, s)[0], s) for s in STATES if val(2025, s)), key=lambda t: (-t[0], t[1]))
missing25 = [s for s in STATES if not val(2025, s)]
latest = {s: max(y for y in YEARS if val(y, s)) for s in STATES}
rank25 = {}
for i, (v, s) in enumerate(ok25):
    rank25[s] = 1 + sum(1 for w, _ in ok25 if w > v)          # ties share a rank
ge35 = {y: sum(1 for s in STATES if val(y, s) and val(y, s)[0] >= 35) for y in YEARS}
ge40 = {y: sum(1 for s in STATES if val(y, s) and val(y, s)[0] >= 40) for y in YEARS}
chg = sorted(((round(val(2025, s)[0] - val(2011, s)[0], 1), s) for s in STATES if val(2025, s) and val(2011, s)), reverse=True)
bandcount25 = Counter(band(v)[0] for v, s in ok25)
top10, bot10 = ok25[:10], ok25[::-1][:10]
hi_v, hi_s = ok25[0]; lo_v, lo_s = ok25[-1]
dc25 = val(2025, "District of Columbia")[0]
first35 = min(y for y in YEARS if ge35[y] > 0)
peak35_y = max(YEARS, key=lambda y: (ge35[y], y)); peak35 = ge35[peak35_y]
min_state = min((val(y, s)[0], s, y) for y in YEARS for s in STATES if val(y, s)); assert min_state[0] >= 20
ms24 = val(2024, "Mississippi")[0]; wv24 = val(2024, "West Virginia")[0]; wv25 = val(2025, "West Virginia")[0]
tx = {y: val(y, "Texas") for y in YEARS}

# ---------- tile map SVG (server-rendered for 2025) ----------
T, G = 48, 4
def tile_svg(year):
    out = []
    for s in STATES + ["District of Columbia"]:
        a = ABBR[s]; c, r = GRID[a]; x, y = c * (T + G), r * (T + G); v = val(year, s)
        col = band(v[0])[1] if v else NODATA; lab = fmt(v[0]) if v else "n/a"
        title = f"{s}: {fmt(v[0])}% in {year}" if v else f"{s}: no {year} estimate"
        out.append(f'<g class="obs-tile" data-s="{a}" tabindex="0" role="button" aria-label="{H.escape(title)}">'
                   f'<title>{H.escape(title)}</title><rect x="{x}" y="{y}" width="{T}" height="{T}" rx="6" fill="{col}"/>'
                   f'<text x="{x + T/2}" y="{y + 21}" text-anchor="middle" class="obs-ab" fill="{ink(col)}">{a}</text>'
                   f'<text x="{x + T/2}" y="{y + 38}" text-anchor="middle" class="obs-v" fill="{ink(col)}">{lab}</text></g>')
    w, h = 12 * (T + G) - G, 8 * (T + G) - G
    return (f'<svg id="obs-map-svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="obs-map-t">'
            f'<title id="obs-map-t">Tile map of adult obesity prevalence by US state, {year}</title>' + "".join(out) + "</svg>")

legend = "".join(f'<li><span class="obs-sw" style="background:{col}"></span>{lab}</li>' for lo, hi, lab, col in BANDS[1:]) + \
         f'<li><span class="obs-sw" style="background:{NODATA}"></span>No estimate</li>'

# ---------- chart: states at 35% or higher, by year ----------
def chart35():
    W, Hh, L, B = 640, 300, 16, 44; bw = (W - L - 10) / len(YEARS); mx = max(ge35.values()); sc = (Hh - B - 30) / mx
    bars = []
    for i, y in enumerate(YEARS):
        n = ge35[y]; bh = n * sc; x = L + i * bw + 4; yy = Hh - B - bh
        bars.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw - 8:.1f}" height="{bh:.1f}" rx="3" fill="#E0612D"/>')
        bars.append(f'<text x="{x + (bw - 8) / 2:.1f}" y="{yy - 6:.1f}" text-anchor="middle" class="obs-c-n">{n}</text>')
        if i % 2 == 0 or y == 2025:
            bars.append(f'<text x="{x + (bw - 8) / 2:.1f}" y="{Hh - B + 24}" text-anchor="middle" class="obs-c-y">{y}</text>')
    return (f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-labelledby="obs-c35-t">'
            f'<title id="obs-c35-t">Number of states with adult obesity prevalence of 35% or higher, 2011 to 2025</title>'
            f'<line x1="{L}" y1="{Hh - B}" x2="{W - 6}" y2="{Hh - B}" stroke="#9CA3AF"/>' + "".join(bars) + "</svg>")

# ---------- concept SVG: self-reported vs measured ----------
def concept():
    return f'''<svg viewBox="0 0 640 300" width="640" height="300" role="img" aria-labelledby="obs-k-t obs-k-d">
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

# ---------- tables ----------
def row(s, rank):
    v = val(2025, s); v11 = val(2011, s); a = ABBR[s].lower()
    if v:
        c = f"{v[0] - v11[0]:+.1f}" if v11 else "–"
        return (f'<tr id="{H.escape(s.lower().replace(" ", "-"))}"><td>{rank}</td><th scope="row">{H.escape(s)}</th><td><strong>{fmt(v[0])}%</strong></td>'
                f'<td>{fmt(v[1])}–{fmt(v[2])}</td><td>{fmt(v11[0]) + "%" if v11 else "–"}</td><td>{c}</td></tr>')
    l = latest[s]; lv = val(l, s)
    return (f'<tr id="{H.escape(s.lower().replace(" ", "-"))}"><td>–</td><th scope="row">{H.escape(s)}</th><td>No 2025 estimate</td>'
            f'<td>{l}: {fmt(lv[0])}% ({fmt(lv[1])}–{fmt(lv[2])})</td><td>{fmt(v11[0]) + "%" if v11 else "–"}</td><td>–</td></tr>')
rank_rows = "".join(row(s, rank25[s]) for v, s in ok25) + "".join(row(s, "–") for s in missing25)
terr_rows = ""
for s in ["District of Columbia", "Guam", "Puerto Rico", "Virgin Islands"]:
    v = val(2025, s); v11 = val(2011, s)
    if v:
        terr_rows += f'<tr><th scope="row">{s}</th><td><strong>{fmt(v[0])}%</strong></td><td>{fmt(v[1])}–{fmt(v[2])}</td><td>{fmt(v11[0]) + "%" if v11 else "–"}</td></tr>'
    else:
        l = max((y for y in YEARS if val(y, s)), default=None)
        terr_rows += f'<tr><th scope="row">{s}</th><td>No 2025 estimate</td><td>{(str(l) + ": " + fmt(val(l, s)[0]) + "%") if l else "–"}</td><td>{fmt(v11[0]) + "%" if v11 else "–"}</td></tr>'
def toplist(L): return "".join(f"<li><strong>{H.escape(s)}</strong> {fmt(v)}%</li>" for v, s in L)
age_rows = ""
for s in STATES:
    a = AGE[s]; cells = "".join(f"<td>{fmt(a[k][0]) + '%' if a.get(k) else 'n/a'}</td>" for k in ("18-39", "40-59", "60+"))
    age_rows += f"<tr><th scope=\"row\">{H.escape(s)}</th>{cells}</tr>"
age_hi = max(((AGE[s]["40-59"][0], s) for s in STATES if AGE[s].get("40-59")))
mid_top = sum(1 for s in STATES if AGE[s].get("40-59") and AGE[s].get("18-39") and AGE[s].get("60+") and AGE[s]["40-59"][0] > AGE[s]["18-39"][0] and AGE[s]["40-59"][0] > AGE[s]["60+"][0])
mid_n = sum(1 for s in STATES if AGE[s].get("40-59") and AGE[s].get("18-39") and AGE[s].get("60+"))

# ---------- JSON for the interactive layer ----------
J = {"years": YEARS, "bands": [[lo, hi, lab, col] for lo, hi, lab, col in BANDS], "nodata": NODATA,
     "s": {ABBR[s]: {"n": s, "v": [list(val(y, s)) if val(y, s) else None for y in YEARS],
                     "age": [list(AGE[s][k]) if AGE[s].get(k) else None for k in ("18-39", "40-59", "60+")]}
           for s in STATES + ["District of Columbia"]}}
JS = r"""
(function(){var d=window.OBS_DATA;var Y=d.years;var sl=document.getElementById('obs-year');
var yo=document.getElementById('obs-year-out');var cap=document.getElementById('obs-map-cap');var states=Object.keys(d.s).filter(function(k){return k!=='DC';});
function band(v){for(var i=0;i<d.bands.length;i++){if(v>=d.bands[i][0]&&v<d.bands[i][1])return d.bands[i];}return d.bands[d.bands.length-1];}
function ink(c){return(c==='#C2481E'||c==='#7F2A10'||c==='#E5743F')?'#FFFFFF':'#1F2937';}
function f1(x){return x.toFixed(1);}
function paint(yi){var y=Y[yi];yo.textContent=y;var n35=0,nd=0;
 document.querySelectorAll('#obs-map-svg .obs-tile').forEach(function(g){var a=g.getAttribute('data-s');var v=d.s[a].v[yi];var col=v?band(v[0])[3]:d.nodata;
  g.querySelector('rect').setAttribute('fill',col);var t=g.querySelectorAll('text');t[0].setAttribute('fill',ink(col));t[1].setAttribute('fill',ink(col));t[1].textContent=v?f1(v[0]):'n/a';
  var lab=d.s[a].n+(v?': '+f1(v[0])+'% in '+y:': no '+y+' estimate');g.setAttribute('aria-label',lab);g.querySelector('title').textContent=lab;
  if(a!=='DC'){if(v&&v[0]>=35)n35++;if(!v)nd++;}});
 cap.textContent=y+': '+n35+' of '+(50-nd)+' states with an estimate had adult obesity of 35% or higher'+(nd?' ('+nd+' without an estimate).':'.');}
sl.addEventListener('input',function(){paint(+sl.value-Y[0]);});
var sel=document.getElementById('obs-state');var go=document.getElementById('obs-go');var out=document.getElementById('obs-panel');
function rankIn(yi,a){var v=d.s[a].v[yi];if(!v)return null;var r=1,n=0;states.forEach(function(k){var w=d.s[k].v[yi];if(w){n++;if(w[0]>v[0])r++;}});return [r,n];}
function spark(a){var vs=d.s[a].v,W=300,H=110,P=24,lo=15,hi=45;function X(i){return P+i*(W-2*P)/(Y.length-1);}function Yp(v){return H-P-(v-lo)*(H-2*P)/(hi-lo);}
 var seg='',segs=[],dots='';vs.forEach(function(v,i){if(v){seg+=(seg?' L':'M')+X(i).toFixed(1)+' '+Yp(v[0]).toFixed(1);dots+='<circle cx="'+X(i).toFixed(1)+'" cy="'+Yp(v[0]).toFixed(1)+'" r="2.5" fill="#B3431A"/>';}else{if(seg)segs.push(seg);seg='';}});if(seg)segs.push(seg);
 var g='';[20,30,40].forEach(function(t){g+='<line x1="'+P+'" x2="'+(W-P)+'" y1="'+Yp(t)+'" y2="'+Yp(t)+'" stroke="#E5E7EB"/><text x="2" y="'+(Yp(t)+4)+'" class="obs-sp-t">'+t+'%</text>';});
 return '<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="'+d.s[a].n+' adult obesity, 2011 to 2025">'+g+segs.map(function(p){return '<path d="'+p+'" fill="none" stroke="#B3431A" stroke-width="2"/>';}).join('')+dots+'<text x="'+P+'" y="'+(H-4)+'" class="obs-sp-t">2011</text><text x="'+(W-P)+'" y="'+(H-4)+'" text-anchor="end" class="obs-sp-t">2025</text></svg>';}
function show(a){var s=d.s[a],yi=+sl.value-Y[0],y=Y[yi],v=s.v[yi],h='<h3>'+s.n+'</h3>';
 if(v){var rk=rankIn(yi,a);h+='<p class="obs-big"><strong>'+f1(v[0])+'%</strong> of adults had obesity in '+y+' <span class="cmb-note">(95% confidence interval '+f1(v[1])+'–'+f1(v[2])+'%)</span></p>';
  if(a!=='DC'&&rk)h+='<p>That ranks <strong>'+rk[0]+' of '+rk[1]+'</strong> states with a '+y+' estimate (1 = highest). Rank is our calculation from the CDC values.</p>';}
 else{var li=-1;s.v.forEach(function(w,i){if(w)li=i;});h+='<p class="obs-big">CDC published <strong>no '+y+' estimate</strong> for '+s.n+' (too few survey responses).'+(li>=0?' Latest available: <strong>'+f1(s.v[li][0])+'%</strong> in '+Y[li]+'.':'')+'</p>';}
 var a11=s.v[0],a25=s.v[Y.length-1];if(a11&&a25)h+='<p>Change from 2011 to 2025: <strong>'+(a25[0]-a11[0]>=0?'+':'')+f1(a25[0]-a11[0])+' percentage points</strong> ('+f1(a11[0])+'% to '+f1(a25[0])+'%).</p>';
 h+='<div class="obs-spark">'+spark(a)+'</div>';
 var ag=s.age;if(ag&&(ag[0]||ag[1]||ag[2])){h+='<p><strong>2025 by age:</strong> 18–39: '+(ag[0]?f1(ag[0][0])+'%':'n/a')+' · 40–59: '+(ag[1]?f1(ag[1][0])+'%':'n/a')+' · 60+: '+(ag[2]?f1(ag[2][0])+'%':'n/a')+'</p>';}
 h+='<p class="cmb-src">Source: CDC, Adult Obesity Prevalence Maps (BRFSS), self-reported height and weight.</p>';out.innerHTML=h;out.hidden=false;}
go.addEventListener('click',function(){show(sel.value);});
document.querySelectorAll('#obs-map-svg .obs-tile').forEach(function(g){function pick(){sel.value=g.getAttribute('data-s');show(sel.value);out.scrollIntoView({behavior:'smooth',block:'nearest'});}
 g.addEventListener('click',pick);g.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();pick();}});});
})();
"""

CSS = """
.obs-tool{border:1px solid #E5E7EB;border-radius:12px;padding:14px;margin:18px 0 8px;background:#FFFFFF}
.obs-map{margin:0 auto;max-width:640px}
.obs-map svg{display:block;width:100%;height:auto}
.obs-tile{cursor:pointer;outline:none}
.obs-tile:focus rect,.obs-tile:hover rect{stroke:#111827;stroke-width:2}
.obs-ab{font:700 15px system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.obs-v{font:600 12px system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
@media (max-width:520px){.obs-v{display:none}.obs-ab{font-size:17px}}
.obs-legend{display:flex;flex-wrap:wrap;gap:6px 14px;list-style:none;padding:0;margin:10px 0 0;font-size:.85em;color:#374151}
.obs-legend li{display:flex;align-items:center;gap:6px;margin-right:10px}
.obs-sw{display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid rgba(0,0,0,.08)}
.obs-ctl{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;margin:12px 0 4px}
.obs-ctl label{font-weight:600}
#obs-year{flex:1 1 220px;min-height:44px}
#obs-state{min-height:44px;font-size:16px;max-width:100%}
#obs-go{min-height:44px;padding:10px 16px;font-weight:600;cursor:pointer}
.obs-panel{border-top:1px solid #E5E7EB;margin-top:12px;padding-top:6px}
.obs-panel[hidden]{display:none}
.obs-big{font-size:1.05rem}
.obs-spark svg{display:block;width:100%;max-width:300px;height:auto}
.obs-sp-t{font:11px system-ui,sans-serif;fill:#6B7280}
.obs-c-n{font:700 18px system-ui,sans-serif;fill:#1F2937}
.obs-c-y{font:17px system-ui,sans-serif;fill:#4B5563}
.obs-k-h{font:700 20px system-ui,sans-serif;fill:#1F2937}
.obs-k-s{font:18px system-ui,sans-serif;fill:#374151}
.obs-k-big{font:800 34px system-ui,sans-serif;fill:#B3431A}
.obs-cols{display:grid;grid-template-columns:1fr;gap:4px 24px}
@media (min-width:640px){.obs-cols{grid-template-columns:1fr 1fr}}
.obs-cols ol{margin:0 0 8px;padding-left:1.4em}
"""

def P(*a): return "\n".join(a)
n47 = len(ok25)
ab = "&ndash;"
miss_txt = ", ".join(missing25[:-1]) + " and " + missing25[-1]
miss_latest = "; ".join(f"{s} {fmt(val(latest[s], s)[0])}% in {latest[s]}" for s in missing25)
tx25 = tx[2025]; tx11 = tx[2011]
txa = AGE["Texas"]
big3 = chg[:3]; small3 = chg[-3:]
assert all(c > 0 for c, _ in chg)
assert ge40[2024] == 2 and val(2024,'West Virginia')[0] >= 40 and val(2024,'Mississippi')[0] >= 40
assert all(r in ('South','Midwest') for r in [{'AL':'South','ND':'Midwest','KY':'South','OK':'South','TN':'South','IN':'Midwest','WV':'South','KS':'Midwest','IA':'Midwest','AR':'South','MO':'Midwest','WI':'Midwest'}.get(ABBR[s_],'?') for v_, s_ in ok25[:10]]), [s_ for v_, s_ in ok25[:10]]

content = P(
f'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <a href="/us-obesity-statistics/" style="color:inherit;">US Obesity Statistics</a> &rsaquo; <span>Obesity Rate by State</span></nav>',
'<article class="cmb-stats">',
'<h1>Obesity Rate by US State</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Data: CDC, released September 24, 2026 &middot; Reviewed October 2, 2026 &middot; Not medical advice</p>',
f'<p class="cmb-intro">Every state, every year from 2011 to 2025, straight from CDC&rsquo;s newest state survey data. Pick a year to watch obesity spread across the map, or pick your state for its 15-year trend and age breakdown.</p>',
'<section class="obs-tool" aria-label="Interactive obesity map by state">',
f'<figure class="obs-map">{tile_svg(2025)}<figcaption id="obs-map-cap" class="cmb-note" aria-live="polite">2025: {ge35[2025]} of {n47} states with an estimate had adult obesity of 35% or higher ({len(missing25)} without an estimate).</figcaption></figure>',
f'<ul class="obs-legend" aria-label="Map legend">{legend}</ul>',
'<div class="obs-ctl"><label for="obs-year">Year: <span id="obs-year-out">2025</span></label><input type="range" id="obs-year" min="2011" max="2025" step="1" value="2025"></div>',
'<div class="obs-ctl"><label for="obs-state">State</label><select id="obs-state">' + "".join(f'<option value="{ABBR[s]}"{" selected" if s=="Texas" else ""}>{H.escape(s)}</option>' for s in STATES + ["District of Columbia"]) + '</select><button type="button" id="obs-go">Show state</button></div>',
'<div id="obs-panel" class="obs-panel" hidden aria-live="polite"></div>',
f'<p class="cmb-src">Source: CDC, <a href="{CDC_PAGE}" rel="noopener">Adult Obesity Prevalence Maps</a> (BRFSS) &mdash; retrieved Oct 2026. Tap a state or use the menu. Self-reported height and weight.</p>',
'</section>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>Adult obesity in 2025 ranged from {fmt(lo_v)}% in {lo_s} to {fmt(hi_v)}% in {hi_s}</strong>, based on CDC&rsquo;s survey of self-reported height and weight. {ge35[2025]} of the {n47} states with a 2025 estimate were at 35% or higher, and none reached 40%. CDC had too little 2025 data for {miss_txt}.</p>',
f'<p class="cmb-src">Source: CDC, <a href="{CDC_PAGE}" rel="noopener">Adult Obesity Prevalence Maps</a> (BRFSS 2025) &mdash; retrieved Oct 2026.</p>',
'</div>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol>',
'<li><a href="#most-obese">Most obese states</a></li><li><a href="#least-obese">Least obese states</a></li><li><a href="#ranking">Full ranking, all 50 states</a></li>',
'<li><a href="#trend">How state obesity rates changed since 2011</a></li><li><a href="#age">Obesity by age in each state</a></li>',
'<li><a href="#measured">Why these numbers are lower than the national 40.3%</a></li><li><a href="#gaps">States with no 2025 estimate</a></li>',
'<li><a href="#use">How to use this data</a></li><li><a href="#faq">FAQ</a></li><li><a href="#sources">Methodology and sources</a></li></ol></nav>',

'<h2 id="most-obese">Most obese states in 2025</h2>',
f'<p><strong>{hi_s} had the highest adult obesity rate in 2025 at {fmt(hi_v)}%</strong> &mdash; roughly 2 in 5 adults. The rest of the top five were {", ".join(s + " (" + fmt(v) + "%)" for v, s in top10[1:4])} and {top10[4][1]} ({fmt(top10[4][0])}%). Most of the top 10 are in the South and Midwest, which CDC puts at {SOURCED["south"]}% and {SOURCED["midwest"]}% overall.</p>',
f'<div class="obs-cols"><div><p><strong>Top 10, 2025</strong></p><ol>{toplist(top10)}</ol></div><div><p><strong>What the ranking can and can&rsquo;t tell you</strong></p><p class="cmb-note">Neighboring ranks are often within each other&rsquo;s 95% confidence intervals, so treat a one- or two-place gap as a tie. {miss_txt} have no 2025 estimate; in 2024 Mississippi was {fmt(ms24)}% and West Virginia {fmt(wv24)}%, the only states above 40% that year.</p></div></div>',
f'<div class="cmb-callout"><p class="cmb-callout-num">{ge35[2025]} states</p><p>had adult obesity of 35% or higher in 2025. In 2011 and 2012 there were none; the count peaked at {peak35} in {peak35_y}. <span class="cmb-src">Calculated from CDC BRFSS state estimates.</span></p></div>',

'<h2 id="least-obese">Least obese states in 2025</h2>',
f'<p><strong>{lo_s} had the lowest adult obesity rate at {fmt(lo_v)}%</strong>, about 1 in 4 adults. {bot10[1][1]} ({fmt(bot10[1][0])}%), {bot10[2][1]} ({fmt(bot10[2][0])}%) and {bot10[3][1]} ({fmt(bot10[3][0])}%) followed. The District of Columbia, which isn&rsquo;t a state, was lower still at {fmt(dc25)}%. Even the leanest state is far from lean: no state has been under 20% since the current method began in 2011 (the lowest was {min_state[1]} at {fmt(min_state[0])}% in {min_state[2]}).</p>',
f'<div class="obs-cols"><div><p><strong>Lowest 10, 2025</strong></p><ol>{toplist(bot10)}</ol></div><div><p><strong>By region</strong></p><p class="cmb-note">CDC&rsquo;s 2025 regional figures: Midwest {SOURCED["midwest"]}%, South {SOURCED["south"]}%, West {SOURCED["west"]}%, Northeast {SOURCED["northeast"]}%.</p></div></div>',

'<h2 id="ranking">Obesity rate by state: full 2025 ranking</h2>',
f'<p>All 50 states, ranked by the share of adults with a BMI of 30 or higher in 2025. The <strong>95% confidence interval</strong> is the survey&rsquo;s margin of error: the true value is very likely inside that range. Change since 2011 is our subtraction of CDC&rsquo;s two estimates, in percentage points. Want to know where your own number sits? Our <a href="/">BMI calculator</a> takes a few seconds.</p>',
'<div class="cmb-table-wrap"><table><caption>Adult obesity prevalence by state, 2025 (CDC BRFSS, self-reported)</caption>',
'<thead><tr><th scope="col">Rank</th><th scope="col">State</th><th scope="col">2025</th><th scope="col">95% CI</th><th scope="col">2011</th><th scope="col">Change (pts)</th></tr></thead>',
f'<tbody>{rank_rows}</tbody></table></div>',
'<div class="cmb-table-wrap"><table><caption>District of Columbia and territories</caption><thead><tr><th scope="col">Area</th><th scope="col">2025</th><th scope="col">95% CI or latest</th><th scope="col">2011</th></tr></thead>',
f'<tbody>{terr_rows}</tbody></table></div>',
f'<p class="cmb-src">Source: CDC, <a href="{CDC_PDF}" rel="noopener">Adult Obesity Maps by State and Territory, 2011&ndash;2025</a> (data tables) &mdash; retrieved Oct 2026. Ranks (ties share a rank) and changes are our calculations.</p>',

'<h2 id="trend">How state obesity rates changed since 2011</h2>',
f'<p><strong>In 2011 no state had an adult obesity rate of 35% or higher. By 2023, {ge35[2023]} did.</strong> The count rose almost every year in between, then sat at {ge35[2024]} in 2024 and {ge35[2025]} in 2025 &mdash; but those two years are missing a state each time (Tennessee in 2024; {miss_txt} in 2025), so they aren&rsquo;t a clean sign of a turnaround.</p>',
f'<figure class="cmb-fig">{chart35()}<figcaption>States with adult obesity of 35% or higher, by year. Calculated from CDC BRFSS state estimates; states without an estimate in a year are not counted.</figcaption></figure>',
f'<p><strong>{big3[0][1]} rose the most</strong>, up {fmt(big3[0][0])} percentage points from 2011 to 2025, followed by {big3[1][1]} (+{fmt(big3[1][0])}) and {big3[2][1]} (+{fmt(big3[2][0])}). The smallest rises among states with both years were {small3[0][1]} (+{fmt(small3[0][0])}), {small3[1][1]} (+{fmt(small3[1][0])}) and {small3[2][1]} (+{fmt(small3[2][0])}). Every one of the {len(chg)} states with estimates in both years is higher in 2025 than in 2011.</p>',
f'<p>One year&rsquo;s move is rarely meaningful on its own. West Virginia, for example, went from {fmt(wv24)}% in 2024 to {fmt(wv25)}% in 2025; a drop that size needs another year of data before anyone should call it a trend. CDC also warns that estimates from before 2011 used a different method and shouldn&rsquo;t be compared with these.</p>',

'<h2 id="age">Obesity by age in each state</h2>',
f'<p><strong>Middle age is where obesity peaks.</strong> CDC says adults 40&ndash;59 are about {SOURCED["mid_vs_young"]}% more likely to have obesity than adults 18&ndash;39 and about {SOURCED["mid_vs_old"]}% more likely than adults 60 and older. {('In every one of the ' + str(mid_n)) if mid_top == mid_n else ('In ' + str(mid_top) + ' of the ' + str(mid_n))} states with all three age estimates, the 40&ndash;59 group had the highest rate; {age_hi[1]} topped that age group at {fmt(age_hi[0])}%.</p>',
'<div class="cmb-table-wrap"><table><caption>Adult obesity by age group and state, 2025 (CDC BRFSS)</caption><thead><tr><th scope="col">State</th><th scope="col">18&ndash;39</th><th scope="col">40&ndash;59</th><th scope="col">60+</th></tr></thead>',
f'<tbody>{age_rows}</tbody></table></div>',
f'<p class="cmb-src">Source: CDC, <a href="{CDC_PAGE}" rel="noopener">Adult Obesity Prevalence Maps</a>, obesity by age (BRFSS 2025) &mdash; retrieved Oct 2026. n/a = insufficient data. Confidence intervals are in the download.</p>',
f'<p>Education follows the same pattern nationally: CDC&rsquo;s 2025 survey found {SOURCED["nohs"]}% obesity among adults without a high school diploma, {SOURCED["hs"]}% with a diploma, {SOURCED["somecol"]}% with some college and {SOURCED["college"]}% among college graduates.</p>',

'<h2 id="measured">Why state numbers are lower than the national 40.3%</h2>',
f'<p><strong>The state maps rely on what people say they weigh; the national figure comes from a scale.</strong> CDC&rsquo;s state data come from the Behavioral Risk Factor Surveillance System (BRFSS), a phone survey where adults report their own height and weight. The national {SOURCED["nhanes"]}% comes from NHANES, where trained staff measure people. Self-reported surveys come in lower: Gallup&rsquo;s self-reported national rate for 2025 was {SOURCED["gallup"]}% (<a href="https://news.gallup.com/poll/696599/obesity-rate-declining.aspx" rel="noopener">Gallup</a>), against the measured {SOURCED["nhanes"]}%.</p>',
f'<figure class="cmb-fig">{concept()}<figcaption>Two CDC surveys, two methods. State estimates: BRFSS 2025. National measured estimate: NHANES August 2021&ndash;August 2023, adults 20 and older (<a href="{NHANES}" rel="noopener">NCHS Data Brief 508</a>).</figcaption></figure>',
f'<p>That&rsquo;s why you shouldn&rsquo;t set a state&rsquo;s figure next to the national one and conclude the state is better than average. Compare states with states, and use the measured number for the country as a whole &mdash; our <a href="/us-obesity-statistics/">US obesity statistics</a> page has the full measured trend since 1960.</p>',

'<h2 id="gaps">States with no 2025 estimate</h2>',
f'<p>CDC publishes a state&rsquo;s figure only when the survey has enough responses to be reliable (at least 50, with a relative standard error under 30%). For 2025 that rules out <strong>{miss_txt}</strong>. Their latest published figures: {miss_latest}. We show those in the ranking table, clearly labelled, rather than mixing years into the 2025 ranks. Earlier one-year gaps: New Jersey (2019), Florida (2021), Kentucky and Pennsylvania (2023) and Tennessee (2024).</p>',

'<h2 id="use">How to use this data</h2>',
f'<p><strong>Comparing your state with its neighbors.</strong> Use the map&rsquo;s year slider to see when your state crossed 30% or 35%, then the state menu for its full trend. Texas is a good example: {fmt(tx11[0])}% in 2011, {fmt(tx25[0])}% in 2025 (95% CI {fmt(tx25[1])}&ndash;{fmt(tx25[2])}), and by age in 2025 {fmt(txa["18-39"][0])}% of 18&ndash;39-year-olds, {fmt(txa["40-59"][0])}% of 40&ndash;59-year-olds and {fmt(txa["60+"][0])}% of those 60 and older.</p>',
'<p><strong>Checking a ranking you saw elsewhere.</strong> Many &ldquo;most obese states&rdquo; lists still use 2023 or 2024 data, or blend obesity with other health measures. If a number doesn&rsquo;t match the table above, check its year and source.</p>',
'<p><strong>Reports, classes and articles.</strong> Download the full table below and cite CDC as the source. For your own weight status, use the <a href="/bmi-chart/">BMI chart</a> or the <a href="/blog/bmi-categories/">BMI categories</a> guide instead &mdash; a state average says nothing about any one person.</p>',

'<h2 id="faq">FAQ</h2>',
f'<details class="cmb-faq"><summary><h3>Which state has the highest obesity rate?</h3></summary><p>{hi_s}, at {fmt(hi_v)}% of adults in 2025 (95% CI {fmt(val(2025, hi_s)[1])}&ndash;{fmt(val(2025, hi_s)[2])}). Mississippi has no 2025 estimate; it was {fmt(ms24)}% in 2024, the highest among states with data that year after West Virginia ({fmt(wv24)}%).</p></details>',
f'<details class="cmb-faq"><summary><h3>Which state has the lowest obesity rate?</h3></summary><p>{lo_s}, at {fmt(lo_v)}% in 2025. The District of Columbia was lower at {fmt(dc25)}% but isn&rsquo;t a state.</p></details>',
f'<details class="cmb-faq"><summary><h3>How many states have an obesity rate above 35%?</h3></summary><p>{ge35[2025]} states in 2025, out of the {n47} with an estimate. None did in 2011 or 2012; the first year any state did was {first35}.</p></details>',
f'<details class="cmb-faq"><summary><h3>Is obesity going down in any state?</h3></summary><p>Not in a way the data can confirm yet. Every state with estimates in both 2011 and 2025 is higher now, and single-year changes are usually within the survey&rsquo;s margin of error.</p></details>',
f'<details class="cmb-faq"><summary><h3>Why is the national obesity rate higher than every state&rsquo;s?</h3></summary><p>Different surveys. The {SOURCED["nhanes"]}% national figure is measured by CDC staff; state figures are self-reported by phone, and self-reported surveys come in lower than measured ones. See <a href="#measured">the explanation above</a>.</p></details>',
f'<details class="cmb-faq"><summary><h3>Why is there no 2025 data for California, Mississippi and Nevada?</h3></summary><p>CDC didn&rsquo;t have enough reliable survey responses from those states for 2025, so it published no estimate. Their 2024 figures were {miss_latest.replace(" in 2024", "")}.</p></details>',

'<h2 id="sources">Methodology and sources</h2>',
f'<p>Every state value on this page comes from CDC&rsquo;s Adult Obesity Prevalence Maps, released September 24, 2026: the data tables for 2011&ndash;2025 and the 2025 tables by age. Obesity means a BMI of 30 or higher, calculated from self-reported height and weight; pregnant women and implausible records are excluded by CDC. We checked our copy against CDC&rsquo;s 2025 CSV (all 54 rows match) and against CDC&rsquo;s own summary counts. Ranks, changes since 2011 and the count of states at 35% or higher are our calculations from those values.</p>',
'<ol class="cmb-sources">',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_PAGE}" rel="noopener">Adult Obesity Prevalence Maps</a>. Updated September 24, 2026.</li>',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_PDF}" rel="noopener">Adult Obesity Maps by State and Territory, 2011&ndash;2025</a> (PDF, includes data tables).</li>',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_CSV}" rel="noopener">Prevalence of Obesity by State and Territory, BRFSS, 2025</a> (CSV).</li>',
f'<li>Emmerich SD, et al. <a href="{NHANES}" rel="noopener">Obesity and severe obesity prevalence in adults: United States, August 2021&ndash;August 2023</a>. NCHS Data Brief No. 508.</li>',
'</ol>',
f'<p><strong>Download:</strong> <a href="/{SLUG}/{CSV1}" download>state obesity rates 2011&ndash;2025 (CSV)</a> &middot; <a href="/{SLUG}/{CSV2}" download>2025 by age group (CSV)</a>. Free to reuse with credit to CDC and a link to this page (CC BY 4.0 for our compilation). Next update: when CDC publishes 2026 state data, expected around September 2027.</p>',
'<p class="cmb-note">This page describes populations, not individuals. It is not medical advice.</p>',
'<h2>Related</h2>',
'<ul><li><a href="/us-obesity-statistics/">US obesity rate and statistics (measured, since 1960)</a></li><li><a href="/bmi-chart/">BMI chart for adults</a></li><li><a href="/blog/bmi-categories/">BMI categories explained</a></li><li><a href="/">BMI calculator</a></li></ul>',
'</article>',
f'<script>window.OBS_DATA={json.dumps(J, separators=(",", ":"))};</script>',
f'<script>{JS}</script>')

# ---------- head / schema ----------
TITLE = "Obesity Rate by US State: Most and Least Obese States (CDC)"
DESC = f"Adult obesity rates for every US state, 2011–2025, from CDC survey data. {hi_s} is highest at {fmt(hi_v)}% and {lo_s} lowest at {fmt(lo_v)}%. Map, rankings and download."
OGT = "Obesity Rate by US State (CDC 2025 data)"
OGALT = f"Tile map of adult obesity by US state, 2025. Highest: {hi_s} {fmt(hi_v)}%. Lowest: {lo_s} {fmt(lo_v)}%. Source: CDC BRFSS."
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]
person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
OG = f"https://calculatemybmi.net/{SLUG}/og-{SLUG}.png"
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "Obesity Rate by US State", "description": DESC,
  "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}, "datePublished": "2026-10-02", "dateModified": "2026-10-02",
  "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "isPartOf": {"@id": "https://calculatemybmi.net/us-obesity-statistics/#article"},
  "citation": [CDC_PAGE, CDC_PDF, NHANES]},
 {"@type": "Dataset", "@id": URL + "#dataset", "name": "Adult obesity prevalence by US state and territory, 2011–2025 (CDC BRFSS)",
  "description": "Annual prevalence of obesity (BMI 30 or higher, self-reported) among adults for each US state, DC, Guam, Puerto Rico and the US Virgin Islands, 2011–2025, with 95% confidence intervals, plus 2025 estimates by age group. Compiled from CDC's Adult Obesity Prevalence Maps data tables.",
  "url": URL, "creator": {"@id": "https://calculatemybmi.net/#organization"}, "isBasedOn": CDC_PAGE,
  "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True, "temporalCoverage": "2011/2025",
  "spatialCoverage": {"@type": "Place", "name": "United States"},
  "variableMeasured": ["Prevalence of obesity among adults (BMI 30 or higher, self-reported)", "95% confidence interval"],
  "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"https://calculatemybmi.net/{SLUG}/{CSV1}"},
                   {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"https://calculatemybmi.net/{SLUG}/{CSV2}"}]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [
  {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"},
  {"@type": "ListItem", "position": 2, "name": "US Obesity Statistics", "item": "https://calculatemybmi.net/us-obesity-statistics/"},
  {"@type": "ListItem", "position": 3, "name": "Obesity Rate by State", "item": URL}]},
 org, person]}
head_new = shell[:shell.find("<script type=\"application/ld+json\">")]
head_new = re.sub(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>", head_new, flags=re.S)
head_new = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">', head_new)
head_new = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', head_new)
head_new = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{H.escape(OGT)}">', head_new)
head_new = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">', head_new)
head_new = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', head_new)
head_new = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">', head_new)
head_new = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{H.escape(OGALT)}">', head_new)
head_new = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG}">', head_new)
rest = shell[shell.find("</script>", shell.find('<script type="application/ld+json">')) + len("</script>"):]
# keep everything after JSON-LD up to the end of the shared <style> blocks, then add our CSS before </head>
head_tail = rest[:rest.find("</head>")]
body_start = rest[rest.find("</head>"):rest.find("<main>")]
footer = rest[rest.find("</main>"):]
page = (head_new + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, indent=1) + "</script>" + head_tail +
        "<style>" + CSS + "</style>" + body_start +
        '<main><div class="container" style="max-width:1000px;margin:0 auto;padding:2rem 1rem 3rem;">' + content + "</div>" + footer)
# nav: mark nothing active; the shared header already links Obesity Statistics
os.makedirs(os.path.join(OUT, SLUG), exist_ok=True)
open(os.path.join(OUT, SLUG, "index.html"), "w", encoding="utf-8").write(page)

# ---------- CSV downloads ----------
with open(os.path.join(OUT, SLUG, CSV1), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["# Adult obesity prevalence (BMI >= 30, self-reported) by US state and territory, 2011-2025. Source: CDC, Adult Obesity Prevalence Maps (BRFSS), " + CDC_PAGE + " (retrieved Oct 2026). Compiled by calculatemybmi.net; CC BY 4.0 for this compilation. Not comparable with estimates before 2011."])
    w.writerow(["year", "state", "abbr", "prevalence_pct", "ci95_low", "ci95_high", "status"])
    for (y, s), v in sorted(D.items()):
        w.writerow([y, s, ABBR[s]] + (list(v) if v else ["", "", ""]) + ["ok" if v else "insufficient data"])
with open(os.path.join(OUT, SLUG, CSV2), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["# Adult obesity prevalence by age group, 2025, by US state and territory. Source: CDC, Adult Obesity Prevalence Maps (BRFSS 2025), " + CDC_PAGE + " (retrieved Oct 2026). CC BY 4.0 for this compilation."])
    w.writerow(["state", "abbr", "age_group", "prevalence_pct", "ci95_low", "ci95_high", "status"])
    for s in sorted(AGE):
        for k in ("18-39", "40-59", "60+"):
            v = AGE[s][k]; w.writerow([s, ABBR[s], k] + (list(v) if v else ["", "", ""]) + ["ok" if v else "insufficient data"])

# ---------- OG image ----------
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1200, 630), "#FFFFFF"); dr = ImageDraw.Draw(im)
def font(sz, bold=False):
    for p in (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
dr.rectangle([0, 0, 1200, 12], fill="#E0612D")
dr.text((56, 50), "Obesity rate by US state", font=font(58, True), fill="#111827")
dr.text((56, 128), "Adults, 2025 · CDC BRFSS (self-reported)", font=font(30), fill="#4B5563")
dr.text((56, 200), f"Highest: {hi_s} {fmt(hi_v)}%", font=font(40, True), fill="#7F2A10")
dr.text((56, 258), f"Lowest: {lo_s} {fmt(lo_v)}%", font=font(40, True), fill="#B3431A")
dr.text((56, 316), f"{ge35[2025]} states at 35% or higher", font=font(34), fill="#1F2937")
dr.text((56, 560), "calculatemybmi.net", font=font(28, True), fill="#6B7280")
ts, gap, ox, oy = 40, 5, 640, 175
for s in STATES + ["District of Columbia"]:
    a = ABBR[s]; c, r = GRID[a]; v = val(2025, s); col = band(v[0])[1] if v else NODATA
    x, y = ox + c * (ts + gap), oy + r * (ts + gap); dr.rounded_rectangle([x, y, x + ts, y + ts], radius=6, fill=col)
    fnt = font(15, True); w_ = dr.textlength(a, font=fnt); dr.text((x + (ts - w_) / 2, y + 12), a, font=fnt, fill=ink(col))
im.save(os.path.join(OUT, SLUG, f"og-{SLUG}.png"), optimize=True)

# ---------- facts for the build report ----------
facts = dict(hi=(hi_s, hi_v), lo=(lo_s, lo_v), dc=dc25, ge35=ge35, ge40=ge40, missing=missing25, latest={s: (latest[s], val(latest[s], s)[0]) for s in missing25},
             big=big3, small=small3, n_both=len(chg), age_hi=age_hi, mid_top=(mid_top, mid_n), bands=bandcount25, first35=first35, peak=(peak35, peak35_y),
             title_len=len(TITLE), desc_len=len(DESC))
print(json.dumps(facts, default=str))
