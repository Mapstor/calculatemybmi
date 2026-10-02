#!/usr/bin/env python3
"""Build /childhood-obesity-statistics/ for calculatemybmi.net.
All values: NCHS Health E-Stat 112 (Noiman, Fryar, Saif, Afful; Feb 2026) Tables 1-3, transcribed below and
cross-checked in chat against the published HTML tables; underweight 4.4% from Health E-Stat 119; children 2-19
population total from the NHANES Aug 2021-Aug 2023 population totals. Derived values are labelled as calculated."""
import json, re, os, sys, csv, html as H
ROOT, OUT = sys.argv[1], sys.argv[2]
SLUG = "childhood-obesity-statistics"; URL = f"https://calculatemybmi.net/{SLUG}/"
HE112 = "https://www.cdc.gov/nchs/data/hestat/hestat112.htm"
HE119 = "https://www.cdc.gov/nchs/data/hestat/hestat119.htm"
POP = "https://wwwn.cdc.gov/nchs/data/ResponseRates/ACS-Population-Totals-For-August-2021-August-2023.pdf"
CDC_CHILD_CAT = "https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html"
CSVF = "childhood-obesity-nhanes-1963-2023.csv"

# ---- Table 1: ages 2-19, by sex: overweight / obesity / severe obesity, percent (SE) ----
P1 = ["1971–1974","1976–1980","1988–1994","1999–2000","2001–2002","2003–2004","2005–2006","2007–2008","2009–2010","2011–2012","2013–2014","2015–2016","2017–2018","Aug 2021–Aug 2023"]
T1 = {  # period: (all ow, se, ob, se, sev, se, boys ow, se, ob, se, sev, se, girls ow, se, ob, se, sev, se)
"1971–1974":(10.2,.6,5.2,.3,1.0,.1, 10.3,.8,5.3,.5,1.0,.2, 10.1,.8,5.1,.4,1.0,.2),
"1976–1980":(9.2,.4,5.5,.4,1.3,.2, 9.4,.6,5.4,.4,1.2,.3, 9.0,.5,5.6,.6,1.3,.3),
"1988–1994":(13.0,.7,10.0,.5,2.6,.4, 12.6,.9,10.2,.7,2.7,.5, 13.4,.9,9.8,.8,2.6,.4),
"1999–2000":(14.2,.9,13.9,.9,3.6,.5, 15.0,1.9,14.0,1.2,3.7,.7, 13.4,.8,13.8,1.1,3.6,.6),
"2001–2002":(14.6,.6,15.4,.9,5.2,.5, 14.2,.7,16.4,1.0,6.1,.8, 15.0,.9,14.3,1.3,4.2,.6),
"2003–2004":(16.5,.8,17.1,1.3,5.1,.6, 16.6,1.0,18.2,1.5,5.4,.8, 16.3,.9,16.0,1.4,4.7,.7),
"2005–2006":(14.6,.9,15.4,1.4,4.7,.6, 14.7,1.2,15.9,1.5,4.9,.8, 14.6,1.0,14.9,1.6,4.5,.7),
"2007–2008":(14.8,.7,16.8,1.3,4.9,.6, 14.3,.7,17.7,1.4,5.5,.8, 15.4,1.5,15.9,1.5,4.3,.8),
"2009–2010":(14.9,.8,16.9,.7,5.6,.6, 14.4,1.0,18.6,1.1,6.4,1.0, 15.4,.9,15.0,.8,4.7,.6),
"2011–2012":(14.9,.9,16.9,1.0,5.6,.7, 15.4,1.3,16.7,1.4,5.7,.9, 14.5,1.4,17.2,1.2,5.5,.8),
"2013–2014":(16.2,.6,17.2,1.1,6.0,.6, 16.4,.8,17.2,1.3,5.6,.6, 16.0,1.0,17.1,1.6,6.3,.9),
"2015–2016":(16.6,.8,18.5,1.3,5.6,.8, 15.7,1.0,19.1,1.7,6.3,1.0, 17.6,1.2,17.8,1.2,4.9,.9),
"2017–2018":(16.1,.8,19.3,1.0,6.1,.7, 14.7,1.2,20.5,1.1,6.9,.9, 17.6,1.1,18.0,1.4,5.2,.7),
"Aug 2021–Aug 2023":(15.1,1.0,21.1,1.1,7.0,.6, 13.0,.9,23.0,1.4,7.8,1.2, 17.5,1.5,19.1,1.5,6.3,.8)}
# ---- Table 2: obesity by age group (all, boys, girls): 2-5, 6-11, 12-19; None = not available; flag '*' = unreliable ----
P2 = ["1963–1965","1966–1970","1971–1974","1976–1980","1988–1994","1999–2000","2001–2002","2003–2004","2005–2006","2007–2008","2009–2010","2011–2012","2013–2014","2015–2016","2017–2018","Aug 2021–Aug 2023"]
T2 = {  # period: ((all 2-5,se),(6-11),(12-19)), boys(...), girls(...)
"1963–1965":(((None,None),(4.2,.4),(None,None)),((None,None),(4.0,.4),(None,None)),((None,None),(4.5,.6),(None,None))),
"1966–1970":(((None,None),(None,None),(4.6,.3)),((None,None),(None,None),(4.5,.4)),((None,None),(None,None),(4.7,.3))),
"1971–1974":(((5.0,.6),(4.0,.5),(6.1,.6)),((5.0,.8),(4.3,.8),(6.1,.8)),((4.9,.8),(3.6,.6),(6.2,.8))),
"1976–1980":(((5.0,.6),(6.5,.6),(5.0,.5)),((4.7,.6),(6.6,.8),(4.8,.5)),((5.3,1.0),(6.4,1.0),(5.3,.8))),
"1988–1994":(((7.2,.7),(11.3,1.0),(10.5,.9)),((6.2,.8),(11.6,1.3),(11.3,1.3)),((8.2,1.0),(11.0,1.4),(9.7,1.1))),
"1999–2000":(((10.3,1.7),(15.1,1.4),(14.8,.9)),((9.5,2.3),(15.8,1.8),(14.8,1.3)),((11.2,2.5),(14.3,2.1),(14.8,1.0))),
"2001–2002":(((10.6,1.8),(16.2,1.6),(16.7,1.1)),((10.7,2.4),(17.5,1.9),(17.6,1.3)),((10.5,1.8),(14.8,2.3),(15.7,1.9))),
"2003–2004":(((13.9,1.6),(18.8,1.3),(17.4,1.7)),((15.1,1.7),(19.9,2.0),(18.2,1.9)),((12.7,2.5),(17.6,1.3),(16.4,2.3))),
"2005–2006":(((10.7,1.1),(15.1,2.1),(17.8,1.8)),((10.4,1.7),(16.2,2.5),(18.2,2.4)),((11.0,1.2),(14.1,2.4),(17.3,2.1))),
"2007–2008":(((10.1,1.2),(19.6,1.2),(18.1,1.7)),((9.3,1.5),(21.2,1.6),(19.3,2.2)),((10.9,2.1),(18.0,2.1),(16.8,2.0))),
"2009–2010":(((12.1,1.2),(18.0,.8),(18.4,1.3)),((14.4,1.8),(20.1,1.0),(19.6,2.3)),((9.6,1.7),(15.7,1.0),(17.1,1.3))),
"2011–2012":(((8.4,1.3),(17.7,1.6),(20.5,1.7)),((9.5,1.9),(16.4,1.8),(20.3,2.4)),(("*7.2",2.1),(19.1,1.7),(20.7,2.0))),
"2013–2014":(((9.4,1.3),(17.4,1.7),(20.6,2.1)),((8.8,2.0),(18.8,2.4),(19.8,2.2)),((10.0,1.3),(15.9,1.9),(21.4,3.2))),
"2015–2016":(((13.9,1.1),(18.4,1.7),(20.6,2.0)),((14.3,1.2),(20.4,2.1),(20.2,2.6)),((13.5,1.7),(16.3,1.8),(20.9,2.0))),
"2017–2018":(((13.4,1.3),(20.3,1.8),(21.2,1.3)),((14.7,1.8),(21.3,2.3),(22.5,1.3)),((12.2,1.4),(19.2,2.1),(19.9,2.2))),
"Aug 2021–Aug 2023":(((14.9,1.3),(22.1,2.0),(22.9,1.7)),((14.6,2.2),(23.7,3.5),(26.0,1.8)),((15.2,1.9),(20.4,2.1),(19.6,2.2)))}
# ---- Table 3 (obesity by sex and race/Hispanic origin): 2017-2018 and Aug 2021-Aug 2023; '*' unreliable, '†' CDC discussion flag ----
RACES = ["Asian, non-Hispanic","Black, non-Hispanic","Hispanic","Mexican American","White, non-Hispanic"]
T3 = {"2017–2018": {"boys":[(12.4,""),(19.4,""),(28.1,""),(29.2,""),(17.4,"")], "girls":[(5.1,""),(29.1,""),(23.0,""),(24.9,""),(14.8,"")]},
      "Aug 2021–Aug 2023": {"boys":[(14.2,"*"),(38.1,"†"),(29.8,""),(31.4,"*"),(18.7,"")], "girls":[(7.4,"*"),(29.9,""),(23.1,""),(23.1,""),(15.7,"")]}}
UNDER = 4.4                     # Health E-Stat 119, ages 2-19, Aug 2021-Aug 2023
POP219 = 74908988               # NHANES population totals, ages 2-19
MID = {"1963–1965":1964,"1966–1970":1968,"1971–1974":1972.5,"1976–1980":1978,"1988–1994":1991,"1999–2000":2000,"2001–2002":2002,"2003–2004":2004,
       "2005–2006":2006,"2007–2008":2008,"2009–2010":2010,"2011–2012":2012,"2013–2014":2014,"2015–2016":2016,"2017–2018":2018,"Aug 2021–Aug 2023":2022.6}
L = "Aug 2021–Aug 2023"
ob, ob_se = T1[L][2], T1[L][3]; ow = T1[L][0]; sev = T1[L][4]
boys, girls = T1[L][8], T1[L][14]; b_ow, g_ow = T1[L][6], T1[L][12]; b_sev, g_sev = T1[L][10], T1[L][16]
a25, a611, a1219 = (T2[L][0][i][0] for i in range(3))
b1219, g1219 = T2[L][1][2][0], T2[L][2][2][0]
ob71 = T1["1971–1974"][2]; sev71 = T1["1971–1974"][4]; ob18 = T1["2017–2018"][2]; ob18_se = T1["2017–2018"][3]
fold = round(ob / ob71, 1)
n_ob = round(POP219 * ob / 100 / 1e6, 1); n_sev = round(POP219 * sev / 100 / 1e6, 1); n_ow = round(POP219 * ow / 100 / 1e6, 1)
healthy = round(100 - ob - ow - UNDER, 1); ow_ob = round(ow + ob, 1)
ci = lambda v, se: (round(v - 1.96 * se, 1), round(v + 1.96 * se, 1))
ci18, ci23 = ci(ob18, ob18_se), ci(ob, ob_se)
overlap = ci18[1] >= ci23[0]
assert (fold, n_ob, n_sev, n_ow, healthy, ow_ob) == (4.1, 15.8, 5.2, 11.3, 59.4, 36.2), (fold, n_ob, n_sev, n_ow, healthy, ow_ob)
f = lambda v: f"{v:.1f}"

# ---------- visuals ----------
def pictogram():
    # 100 dots: obesity (21, of which severe 7), overweight 15, underweight 4, healthy weight 60 (rounded shares)
    cats = [("Severe obesity", round(sev), "#7F2A10"), ("Obesity (not severe)", round(ob) - round(sev), "#C2481E"),
            ("Overweight", round(ow), "#F4A774"), ("Underweight", round(UNDER), "#9CA3AF"), ("Healthy weight", 0, "#D1E7DD")]
    cats[-1] = ("Healthy weight", 100 - sum(c[1] for c in cats[:-1]), "#CDE7D8")
    seq = [c for c in cats for _ in range(c[1])]
    out = []
    for i, (lab, n, col) in enumerate(seq):
        r_, c_ = divmod(i, 10); x, y = 30 + c_ * 34, 30 + r_ * 34
        out.append(f'<g><circle cx="{x}" cy="{y - 7}" r="5" fill="{col}"/><rect x="{x - 7}" y="{y}" width="14" height="13" rx="5" fill="{col}"/></g>')
    leg = "".join(f'<g transform="translate(372,{40 + i * 48})"><rect width="22" height="22" rx="6" fill="{col}"/><text x="32" y="10" class="ck-l">{lab}</text><text x="32" y="30" class="ck-n">{n} of 100</text></g>' for i, (lab, n, col) in enumerate(cats))
    return (f'<svg viewBox="0 0 620 360" width="620" height="360" role="img" aria-labelledby="ck-pt ck-pd"><title id="ck-pt">Out of every 100 US children and teens ages 2–19</title>'
            f'<desc id="ck-pd">{round(ob)} have obesity (including {round(sev)} with severe obesity), {round(ow)} are overweight, {round(UNDER)} are underweight and {cats[-1][1]} are in the healthy weight range, rounded from NHANES August 2021–August 2023.</desc>'
            + "".join(out) + leg + "</svg>")

def bars_age_sex():
    rows = [("Ages 2–5", T2[L][1][0][0], T2[L][2][0][0]), ("Ages 6–11", T2[L][1][1][0], T2[L][2][1][0]), ("Ages 12–19", b1219, g1219), ("All 2–19", boys, girls)]
    W, Hh, L0 = 640, 300, 110; mx = 30.0; out = []
    for i, (lab, b, g) in enumerate(rows):
        y = 34 + i * 64
        out.append(f'<text x="{L0 - 10}" y="{y + 22}" text-anchor="end" class="ck-ax-b">{lab}</text>')
        for j, (v, col, nm) in enumerate(((b, "#1F4E79", "Boys"), (g, "#C2481E", "Girls"))):
            w = v / mx * (W - L0 - 70); yy = y + j * 22
            out.append(f'<rect x="{L0}" y="{yy}" width="{w:.1f}" height="18" rx="4" fill="{col}"/><text x="{L0 + w + 8:.1f}" y="{yy + 14}" class="ck-v">{f(v)}% {nm.lower()}</text>')
    return (f'<svg viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-labelledby="ck-as-t"><title id="ck-as-t">Obesity among US boys and girls by age group, August 2021–August 2023</title>' + "".join(out) + "</svg>")

def trend_static():
    # server-rendered default (same geometry as the JS draw): ages 2-19 obesity + severe obesity; JS redraws on chip changes
    W, Hh, L0, R0, T0, B0, x0, x1, y0, y1 = 680, 320, 44, 16, 18, 40, 1962, 2024, 0, 30
    X = lambda t: L0 + (t - x0) * (W - L0 - R0) / (x1 - x0); Y = lambda v: Hh - B0 - (v - y0) * (Hh - T0 - B0) / (y1 - y0)
    g = []
    for t in (0, 5, 10, 15, 20, 25, 30):
        g.append(f'<line x1="{L0}" x2="{W - R0}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="#EEF0F3"/><text x="{L0 - 8}" y="{Y(t) + 5:.1f}" text-anchor="end" class="ck-ax">{t}%</text>')
    for t in (1970, 1980, 1990, 2000, 2010, 2020):
        g.append(f'<text x="{X(t):.1f}" y="{Hh - 14}" text-anchor="middle" class="ck-ax">{t}</text>')
    g.append(f'<rect x="{X(2020.2):.1f}" y="{T0}" width="{X(2021.6) - X(2020.2):.1f}" height="{Hh - T0 - B0}" fill="#F3F4F6"/><text x="{X(2020.9):.1f}" y="{T0 + 12}" text-anchor="middle" class="ck-ax-s">pause</text>')
    for k in JD["on"]:
        sr = SER[k]; pts = sorted((MID[p], v[0], v[1], p) for p, v in sr["p"].items())
        up = " L".join(f"{X(q[0]):.1f} {Y(q[1] + 1.96 * q[2]):.1f}" for q in pts); dn = " L".join(f"{X(q[0]):.1f} {Y(max(0, q[1] - 1.96 * q[2])):.1f}" for q in reversed(pts))
        g.append(f'<path d="M{up} L{dn} Z" fill="{sr["c"]}" opacity=".12"/>')
        g.append('<path d="M' + " L".join(f"{X(q[0]):.1f} {Y(q[1]):.1f}" for q in pts) + f'" fill="none" stroke="{sr["c"]}" stroke-width="2.6"/>')
        for q in pts:
            g.append(f'<circle class="ck-pt" cx="{X(q[0]):.1f}" cy="{Y(q[1]):.1f}" r="4.5" fill="{sr["c"]}" stroke="#fff" stroke-width="1.5" data-t="{sr["n"]}|{q[3]}|{q[1]}|{q[2]}" tabindex="0"/>')
        last = pts[-1]; g.append(f'<text x="{X(last[0]) - 6:.1f}" y="{Y(last[1]) - 9:.1f}" text-anchor="end" class="ck-end" fill="{sr["c"]}">{last[1]:.1f}%</text>')
    return ('<svg id="ck-trend-svg" viewBox="0 0 680 320" width="680" height="320" role="img" aria-label="Childhood obesity in the US by survey period, 1963–1965 to August 2021–August 2023">' + "".join(g) + "</svg>")

def table1():
    rows = "".join(f"<tr><th scope='row'>{p}</th>" + "".join(f"<td>{f(T1[p][k])}%</td>" for k in (2, 4, 0, 8, 14)) + "</tr>" for p in P1)
    return ("<div class='cmb-table-wrap'><table><caption>Children and teens ages 2–19: obesity, severe obesity and overweight by survey period (measured, NHANES)</caption>"
            "<thead><tr><th scope='col'>Survey period</th><th scope='col'>Obesity</th><th scope='col'>Severe obesity</th><th scope='col'>Overweight</th><th scope='col'>Obesity, boys</th><th scope='col'>Obesity, girls</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")
def table2():
    def cell(v):
        if v[0] is None: return "<td>–</td>"
        if isinstance(v[0], str): return f"<td>{v[0][1:]}%*</td>"
        return f"<td>{f(v[0])}%</td>"
    rows = "".join(f"<tr><th scope='row'>{p}</th>" + "".join(cell(T2[p][0][i]) for i in range(3)) + "</tr>" for p in P2)
    return ("<div class='cmb-table-wrap'><table><caption>Obesity by age group, ages 2–19 (measured, NHANES)</caption><thead><tr><th scope='col'>Survey period</th><th scope='col'>Ages 2–5</th><th scope='col'>Ages 6–11</th><th scope='col'>Ages 12–19</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div><p class='cmb-src'>– not measured in that survey. 1966–1970 covered ages 12–17. Source: NCHS Health E-Stat 112, Table 2.</p>")
def table3():
    def cell(v):
        val, fl = v
        if fl == "*": return "<td class='ck-na'>Not reliable*</td>"
        if fl == "†": return "<td class='ck-na'>See note†</td>"
        return f"<td>{f(val)}%</td>"
    rows = ""
    for i, r in enumerate(RACES):
        rows += f"<tr><th scope='row'>{r}</th>" + cell(T3['2017–2018']['boys'][i]) + cell(T3[L]['boys'][i]) + cell(T3['2017–2018']['girls'][i]) + cell(T3[L]['girls'][i]) + "</tr>"
    return ("<div class='cmb-table-wrap'><table><caption>Obesity by race and Hispanic origin, ages 2–19 (measured, NHANES)</caption>"
            "<thead><tr><th scope='col'></th><th scope='col'>Boys 2017–2018</th><th scope='col'>Boys 2021–2023</th><th scope='col'>Girls 2017–2018</th><th scope='col'>Girls 2021–2023</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")

# ---------- data for the interactive chart ----------
SER = {
 "all": {"n": "All, ages 2–19", "c": "#C2481E", "p": {p: [T1[p][2], T1[p][3]] for p in P1}},
 "sev": {"n": "Severe obesity, 2–19", "c": "#7F2A10", "p": {p: [T1[p][4], T1[p][5]] for p in P1}},
 "ow":  {"n": "Overweight, 2–19", "c": "#E9A272", "p": {p: [T1[p][0], T1[p][1]] for p in P1}},
 "boys": {"n": "Boys 2–19", "c": "#1F4E79", "p": {p: [T1[p][8], T1[p][9]] for p in P1}},
 "girls": {"n": "Girls 2–19", "c": "#B83280", "p": {p: [T1[p][14], T1[p][15]] for p in P1}},
 "a25": {"n": "Ages 2–5", "c": "#2E7D4F", "p": {p: [T2[p][0][0][0], T2[p][0][0][1]] for p in P2 if isinstance(T2[p][0][0][0], float)}},
 "a611": {"n": "Ages 6–11", "c": "#6B46C1", "p": {p: [T2[p][0][1][0], T2[p][0][1][1]] for p in P2 if isinstance(T2[p][0][1][0], float)}},
 "a1219": {"n": "Ages 12–19", "c": "#0E7490", "p": {p: [T2[p][0][2][0], T2[p][0][2][1]] for p in P2 if isinstance(T2[p][0][2][0], float)}}}
JD = {"mid": MID, "ser": SER, "order": ["all", "sev", "ow", "boys", "girls", "a25", "a611", "a1219"], "on": ["all", "sev"]}
chips = "".join(f'<button type="button" class="ck-chip{" on" if k in JD["on"] else ""}" data-k="{k}" aria-pressed="{"true" if k in JD["on"] else "false"}" style="--c:{SER[k]["c"]}">{SER[k]["n"]}</button>' for k in JD["order"])
JS = r"""
(function(){var d=window.CK_DATA,svg=document.getElementById('ck-trend-svg'),tip=document.getElementById('ck-tip'),box=document.getElementById('ck-trendwrap'),on=d.on.slice();
var W=680,H=320,L=44,R=16,T=18,B=40,x0=1962,x1=2024,y0=0,y1=30;function X(t){return L+(t-x0)*(W-L-R)/(x1-x0);}function Y(v){return H-B-(v-y0)*(H-T-B)/(y1-y0);}
function f1(v){return v.toFixed(1);}
function draw(){var g='';[0,5,10,15,20,25,30].forEach(function(t){g+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+Y(t)+'" y2="'+Y(t)+'" stroke="#EEF0F3"/><text x="'+(L-8)+'" y="'+(Y(t)+5)+'" text-anchor="end" class="ck-ax">'+t+'%</text>';});
 [1970,1980,1990,2000,2010,2020].forEach(function(t){g+='<text x="'+X(t)+'" y="'+(H-14)+'" text-anchor="middle" class="ck-ax">'+t+'</text>';});
 g+='<rect x="'+X(2020.2)+'" y="'+T+'" width="'+(X(2021.6)-X(2020.2))+'" height="'+(H-T-B)+'" fill="#F3F4F6"/><text x="'+X(2020.9)+'" y="'+(T+12)+'" text-anchor="middle" class="ck-ax-s">pause</text>';
 on.forEach(function(k){var s=d.ser[k],pts=Object.keys(s.p).map(function(p){return [d.mid[p],s.p[p][0],s.p[p][1],p];}).sort(function(a,b){return a[0]-b[0];});
  var up=pts.map(function(q){return X(q[0]).toFixed(1)+' '+Y(q[1]+1.96*q[2]).toFixed(1);}),dn=pts.slice().reverse().map(function(q){return X(q[0]).toFixed(1)+' '+Y(Math.max(0,q[1]-1.96*q[2])).toFixed(1);});
  g+='<path d="M'+up.join(' L')+' L'+dn.join(' L')+' Z" fill="'+s.c+'" opacity=".12"/>';
  g+='<path d="M'+pts.map(function(q){return X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1);}).join(' L')+'" fill="none" stroke="'+s.c+'" stroke-width="2.6"/>';
  pts.forEach(function(q){g+='<circle class="ck-pt" cx="'+X(q[0]).toFixed(1)+'" cy="'+Y(q[1]).toFixed(1)+'" r="4.5" fill="'+s.c+'" stroke="#fff" stroke-width="1.5" data-t="'+s.n+'|'+q[3]+'|'+q[1]+'|'+q[2]+'" tabindex="0"/>';});
  var last=pts[pts.length-1];g+='<text x="'+(X(last[0])-6)+'" y="'+(Y(last[1])-9)+'" text-anchor="end" class="ck-end" fill="'+s.c+'">'+f1(last[1])+'%</text>';});
 svg.innerHTML=g;
 svg.querySelectorAll('.ck-pt').forEach(function(c){function show(e){var a=c.getAttribute('data-t').split('|'),v=+a[2],se=+a[3],r=box.getBoundingClientRect(),cr=c.getBoundingClientRect();
   tip.innerHTML='<strong>'+a[0]+'</strong><br>'+a[1]+': <strong>'+f1(v)+'%</strong><br><span>about '+f1(Math.max(0,v-1.96*se))+'–'+f1(v+1.96*se)+'% (95% range, our calculation)</span>';
   tip.style.left=Math.min(r.width-200,Math.max(0,cr.left-r.left-90))+'px';tip.style.top=(cr.top-r.top+16)+'px';tip.hidden=false;}
  c.addEventListener('mouseenter',show);c.addEventListener('focus',show);c.addEventListener('click',show);c.addEventListener('mouseleave',function(){tip.hidden=true;});c.addEventListener('blur',function(){tip.hidden=true;});});}
document.querySelectorAll('.ck-chip').forEach(function(b){b.addEventListener('click',function(){var k=b.getAttribute('data-k'),i=on.indexOf(k);
 if(i>=0){if(on.length>1){on.splice(i,1);b.classList.remove('on');b.setAttribute('aria-pressed','false');}}else{on.push(k);b.classList.add('on');b.setAttribute('aria-pressed','true');}draw();});});
draw();})();
"""
CSS = """
.ck-cards{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 14px}
.ck-cards .ck-kpi{flex:1 1 calc(50% - 10px);box-sizing:border-box;min-width:140px;background:#fff;border:1px solid #EEF0F3;border-top:5px solid var(--c);border-radius:12px;padding:12px 14px;box-shadow:0 2px 10px rgba(17,24,39,.06);display:flex;flex-direction:column;gap:2px}
@media (min-width:760px){.ck-cards .ck-kpi{flex:1 1 calc(25% - 10px)}}
.ck-kpi-l{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:#6B7280;font-weight:700}
.ck-kpi-n{font-size:2rem;font-weight:800;line-height:1.1;color:#111827}
.ck-kpi-s{font-size:.9rem;color:#374151}
.ck-box{border:1px solid #EEF0F3;border-radius:16px;padding:16px;margin:10px 0 14px;background:linear-gradient(180deg,#FFFFFF 0%,#FFF9F5 100%);box-shadow:0 6px 24px rgba(17,24,39,.07)}
.ck-box h2{margin-top:4px}
.ck-chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 10px}
.ck-chip{border:2px solid var(--c);background:#fff;color:#1F2937;border-radius:999px;padding:6px 10px;min-height:36px;font-size:.85rem;font-weight:700;cursor:pointer;margin:0 4px 4px 0}
@media (min-width:640px){.ck-chip{padding:8px 12px;min-height:40px;font-size:.95rem}}
.ck-chip.on{background:var(--c);color:#fff}
.ck-trendwrap{position:relative}
.ck-trendwrap svg{display:block;width:100%;height:auto}
.ck-tip{position:absolute;pointer-events:none;background:#111827;color:#fff;padding:8px 10px;border-radius:8px;font-size:.85rem;line-height:1.35;box-shadow:0 4px 14px rgba(0,0,0,.2);z-index:2;max-width:220px}
.ck-tip span{opacity:.75}
.ck-tip[hidden]{display:none}
.ck-pt{cursor:pointer;outline:none}
.ck-pt:focus{stroke:#111827;stroke-width:3}
.ck-ax{font:16px system-ui,sans-serif;fill:#6B7280}
.ck-ax-s{font:12px system-ui,sans-serif;fill:#9CA3AF}
.ck-ax-b{font:700 16px system-ui,sans-serif;fill:#1F2937}
.ck-v{font:700 15px system-ui,sans-serif;fill:#1F2937}
.ck-end{font:800 18px system-ui,sans-serif}
.ck-l{font:700 17px system-ui,sans-serif;fill:#1F2937}
.ck-n{font:15px system-ui,sans-serif;fill:#4B5563}
.ck-fig{margin:16px auto;max-width:640px}
.ck-fig svg{display:block;width:100%;height:auto}
.ck-na{color:#6B7280;font-style:italic}
.ck-cta{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;border-radius:14px;padding:14px 16px;background:#1F2937;color:#fff;margin:18px 0}
.ck-cta p{margin:0;flex:1 1 260px}
.ck-cta a{background:#C2481E;color:#fff;font-weight:800;border-radius:10px;padding:10px 16px;text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
"""

def P(*a): return "\n".join(a)
content = P(
'<nav aria-label="Breadcrumb" style="font-size:0.875rem;color:var(--gray-500);margin:0 0 1rem;"><a href="/" style="color:inherit;">Home</a> &rsaquo; <a href="/us-obesity-statistics/" style="color:inherit;">US Obesity Statistics</a> &rsaquo; <span>Childhood Obesity</span></nav>',
'<article class="cmb-stats">',
'<h1>Childhood Obesity in America</h1>',
'<p class="byline" style="color:var(--gray-500);font-size:0.9375rem;margin:0 0 1.25rem;">Written by Marko Visic, MPharm &middot; Data: CDC National Center for Health Statistics, published February 2026 &middot; Reviewed October 2, 2026 &middot; Not medical advice</p>',
'<p class="cmb-intro">Every measured CDC number on children&rsquo;s weight in one place: how many kids have obesity, how that changed since the 1960s, and how it differs by age, sex and race. All of it comes from kids who were actually weighed and measured, not from parents&rsquo; estimates.</p>',
f'<div class="ck-cards"><div class="ck-kpi" style="--c:#C2481E"><span class="ck-kpi-l">Obesity, ages 2–19</span><span class="ck-kpi-n">{f(ob)}%</span><span class="ck-kpi-s">about 1 in 5 kids &middot; {f(n_ob)} million (calculated)</span></div>'
f'<div class="ck-kpi" style="--c:#7F2A10"><span class="ck-kpi-l">Severe obesity</span><span class="ck-kpi-n">{f(sev)}%</span><span class="ck-kpi-s">{f(n_sev)} million kids (calculated)</span></div>'
f'<div class="ck-kpi" style="--c:#F4A774"><span class="ck-kpi-l">Overweight</span><span class="ck-kpi-n">{f(ow)}%</span><span class="ck-kpi-s">a further {f(n_ow)} million (calculated)</span></div>'
f'<div class="ck-kpi" style="--c:#1F2937"><span class="ck-kpi-l">Since 1971–1974</span><span class="ck-kpi-n">{fold}&times;</span><span class="ck-kpi-s">{f(ob71)}% then, {f(ob)}% now</span></div></div>',
'<div class="cmb-answer" id="answer">',
f'<p><strong>{f(ob)}% of US children and teens ages 2–19 had obesity</strong> in August 2021–August 2023, the latest measured CDC data &mdash; about 1 in 5 kids, or roughly {f(n_ob)} million. That includes {f(sev)}% with severe obesity, and another {f(ow)}% were overweight. Teens 12–19 ({f(a1219)}%) and children 6–11 ({f(a611)}%) had higher rates than ages 2–5 ({f(a25)}%).</p>',
f'<p class="cmb-src">Source: CDC National Center for Health Statistics, <a href="{HE112}" rel="noopener">Health E-Stat 112</a> (February 2026). Millions: our calculation using the <a href="{POP}" rel="noopener">NHANES population total</a> for ages 2–19.</p>',
'</div>',
f'<figure class="ck-fig">{pictogram()}<figcaption>Out of every 100 US children and teens ages 2–19, August 2021–August 2023 (shares rounded to whole children; the healthy-weight share is our calculation from CDC&rsquo;s other categories). Sources: NCHS <a href="{HE112}" rel="noopener">Health E-Stat 112</a> and <a href="{HE119}" rel="noopener">Health E-Stat 119</a>.</figcaption></figure>',
'<nav class="cmb-toc" aria-label="On this page"><p class="cmb-toc-title">On this page</p><ol>',
'<li><a href="#trend">Childhood obesity rate by year</a></li><li><a href="#age">By age: preschoolers, kids and teens</a></li><li><a href="#sex">Boys vs girls</a></li>',
'<li><a href="#race">By race and Hispanic origin</a></li><li><a href="#increasing">Is childhood obesity increasing?</a></li><li><a href="#definition">How obesity is defined for children</a></li>',
'<li><a href="#state">Childhood obesity by state</a></li><li><a href="#faq">FAQ</a></li><li><a href="#sources">Methodology and sources</a></li></ol></nav>',

'<section class="ck-box" id="trend" aria-label="Interactive chart">',
'<h2>Childhood obesity rate by year, 1963–2023</h2>',
f'<p><strong>Obesity among US children and teens has roughly quadrupled since the early 1970s</strong>, from {f(ob71)}% in 1971–1974 to {f(ob)}% in 2021–2023. Severe obesity rose even faster, from {f(sev71)}% to {f(sev)}%. Tap the buttons to add or remove groups; tap a point for its value and margin of error.</p>',
f'<div class="ck-chips" role="group" aria-label="Choose series">{chips}</div>',
f'<div class="ck-trendwrap" id="ck-trendwrap">{trend_static()}<div id="ck-tip" class="ck-tip" hidden></div></div>',
f'<p class="cmb-src">Measured heights and weights, NHANES. Shaded bands: about ±1.96 standard errors (our calculation from CDC&rsquo;s standard errors). The gray strip marks the 2020&ndash;2021 pause, when CDC stopped the survey and later restarted it with a new design. Source: NCHS <a href="{HE112}" rel="noopener">Health E-Stat 112</a>, Tables 1&ndash;2.</p>',
'</section>',
table1(),

'<h2 id="age">Childhood obesity by age: preschoolers, kids and teens</h2>',
f'<p><strong>Obesity climbs once children reach school age.</strong> In 2021–2023 it was {f(a25)}% among ages 2–5, {f(a611)}% among ages 6–11 and {f(a1219)}% among teens 12–19. The teen figure is the closest thing to a &ldquo;teenage obesity rate&rdquo;: roughly 2 in 9 teens. Teen boys stood out at {f(b1219)}%, against {f(g1219)}% for teen girls.</p>',
f'<figure class="ck-fig">{bars_age_sex()}<figcaption>Obesity by age group and sex, August 2021–August 2023 (measured). Source: NCHS <a href="{HE112}" rel="noopener">Health E-Stat 112</a>, Table 2.</figcaption></figure>',
table2(),

'<h2 id="sex">Boys vs girls</h2>',
f'<p><strong>Boys are more likely to have obesity; girls are more likely to be overweight.</strong> In 2021–2023, {f(boys)}% of boys and {f(girls)}% of girls ages 2–19 had obesity, while {f(g_ow)}% of girls and {f(b_ow)}% of boys were overweight. Severe obesity: {f(b_sev)}% of boys, {f(g_sev)}% of girls. Those are survey estimates with margins of error of a few points, so treat small gaps with care.</p>',
f'<div class="cmb-callout"><p class="cmb-callout-num">{f(ow_ob)}%</p><p>of US children and teens were overweight or had obesity in 2021–2023 ({f(ow)}% + {f(ob)}%). <span class="cmb-src">Calculated from NCHS Health E-Stat 112.</span></p></div>',

'<h2 id="race">Childhood obesity by race and Hispanic origin</h2>',
f'<p><strong>Rates differ widely by race and Hispanic origin, but the newest survey can&rsquo;t pin every group down.</strong> CDC&rsquo;s 2021–2023 sample no longer oversampled Hispanic and Asian children, so several estimates miss its reliability standard. Among the reliable 2021–2023 figures, Hispanic boys were at {f(T3[L]["boys"][2][0])}% and white boys at {f(T3[L]["boys"][4][0])}%; Black girls were at {f(T3[L]["girls"][1][0])}%, Hispanic girls {f(T3[L]["girls"][2][0])}% and white girls {f(T3[L]["girls"][4][0])}%. The 2017–2018 column, from a survey with full oversampling, shows the same broad pattern.</p>',
table3(),
f'<p class="cmb-src">* Does not meet NCHS reliability standards. † CDC refers readers to a separate discussion of this estimate (Ogden et al., <em>Pediatric Obesity</em> 2025), so we don&rsquo;t show it. CDC also notes that at a given BMI, body fat can differ by race and Hispanic origin. Source: NCHS <a href="{HE112}" rel="noopener">Health E-Stat 112</a>, Table 3.</p>',

'<h2 id="increasing">Is childhood obesity increasing?</h2>',
f'<p><strong>Over decades, clearly yes; over the last few years, the survey can&rsquo;t say for sure.</strong> The rate rose from {f(ob71)}% in 1971–1974 to {f(T1["1999–2000"][2])}% in 1999–2000 and {f(ob18)}% in 2017–2018, then {f(ob)}% in 2021–2023. The last step is within the margins of error: our approximate 95% ranges are {f(ci18[0])}–{f(ci18[1])}% for 2017–2018 and {f(ci23[0])}–{f(ci23[1])}% for 2021–2023, and they overlap. The survey also changed design after its pandemic pause, which makes close comparisons harder.</p>',
f'<p>For adults, the same pattern shows up in our <a href="/us-obesity-statistics/">US obesity statistics</a>: a long climb, and recent figures that are high but not clearly still rising.</p>',

'<h2 id="definition">How obesity is defined for children</h2>',
f'<p>Children aren&rsquo;t judged by the adult BMI cutoffs. Their BMI is compared with other children of the same <strong>age and sex</strong> using CDC growth charts: <strong>obesity</strong> is a BMI at or above the 95th percentile, <strong>severe obesity</strong> is at or above 120% of the 95th percentile, and <strong>overweight</strong> is the 85th to just under the 95th percentile (<a href="{CDC_CHILD_CAT}" rel="noopener">CDC child and teen BMI categories</a>). CDC also cites research suggesting that, at a given BMI, BMI overstates body fat among Black children and teens.</p>',
'<div class="ck-cta"><p><strong>Checking one child?</strong> A national rate says nothing about any single child. Our calculator gives the BMI-for-age percentile and category using CDC&rsquo;s method.</p><a href="/kids-bmi-calculator/">Kids BMI calculator</a></div>',

'<h2 id="state">Childhood obesity by state</h2>',
'<p>State-level figures for children come from a different survey, the parent-reported National Survey of Children&rsquo;s Health, which we haven&rsquo;t verified for this page yet, so we don&rsquo;t show state numbers here. For adults, see every state from 2011 to 2025 on our <a href="/obesity-rate-by-state/">obesity rate by state</a> map.</p>',

'<h2 id="faq">FAQ</h2>',
f'<details class="cmb-faq"><summary><h3>What percentage of children in America have obesity?</h3></summary><p>{f(ob)}% of children and teens ages 2–19 had obesity in August 2021–August 2023, including {f(sev)}% with severe obesity (CDC, measured).</p></details>',
f'<details class="cmb-faq"><summary><h3>How many kids in the US have obesity?</h3></summary><p>About {f(n_ob)} million children and teens ages 2–19, our calculation from CDC&rsquo;s {f(ob)}% and the survey&rsquo;s population total of about {round(POP219 / 1e6, 1)} million kids.</p></details>',
f'<details class="cmb-faq"><summary><h3>What is the teenage obesity rate?</h3></summary><p>{f(a1219)}% of teens ages 12–19 had obesity in 2021–2023: {f(b1219)}% of boys and {f(g1219)}% of girls.</p></details>',
f'<details class="cmb-faq"><summary><h3>Is childhood obesity going up?</h3></summary><p>It has risen about {fold}-fold since 1971–1974. The rise from {f(ob18)}% (2017–2018) to {f(ob)}% (2021–2023) is within the survey&rsquo;s margins of error.</p></details>',
f'<details class="cmb-faq"><summary><h3>Is there childhood obesity data by state?</h3></summary><p>Not on this page yet: state child data come from a different, parent-reported survey that we haven&rsquo;t verified. Adult state rates are on our <a href="/obesity-rate-by-state/">obesity rate by state</a> page.</p></details>',

'<h2 id="sources">Methodology and sources</h2>',
f'<p>Every percentage on this page is transcribed from NCHS Health E-Stat 112 (February 2026), which reports measured heights and weights from the National Health and Nutrition Examination Survey (NHANES) and its predecessors since 1963–1965, and was checked against the published tables. Pregnant girls are excluded by CDC. Underweight ({f(UNDER)}%) comes from Health E-Stat 119. Values labelled &ldquo;calculated&rdquo; are ours: counts of children (rate × the NHANES population total for ages 2–19, {POP219:,}), the healthy-weight share in the figure, combined overweight-or-obesity, and approximate 95% ranges (estimate ± 1.96 standard errors).</p>',
'<ol class="cmb-sources">',
f'<li>Noiman A, Fryar CD, Saif NT, Afful J. <a href="{HE112}" rel="noopener">Prevalence of overweight, obesity, and severe obesity among children and adolescents ages 2–19 years: United States, 1963–1965 through August 2021–August 2023</a>. NCHS Health E-Stat 112. February 2026.</li>',
f'<li><a href="{HE119}" rel="noopener">Prevalence of underweight among children, adolescents and adults, 1960–1962 through August 2021–August 2023</a>. NCHS Health E-Stat 119.</li>',
f'<li>National Center for Health Statistics. <a href="{POP}" rel="noopener">NHANES population totals, August 2021–August 2023</a>.</li>',
f'<li>Centers for Disease Control and Prevention. <a href="{CDC_CHILD_CAT}" rel="noopener">Child and Teen BMI Categories</a>.</li>',
'</ol>',
f'<p><strong>Download:</strong> <a href="/{SLUG}/{CSVF}" download>childhood obesity by survey period, age, sex and race (CSV)</a>. Free to reuse with credit to CDC/NCHS and a link to this page (CC BY 4.0 for our compilation).</p>',
'<p class="cmb-note">This page describes populations, not individual children. It is not medical advice.</p>',
'<h2>Related</h2>',
'<ul><li><a href="/us-obesity-statistics/">US obesity rate and statistics (adults, measured)</a></li><li><a href="/obesity-rate-by-state/">Adult obesity rate by state, 2011–2025</a></li><li><a href="/kids-bmi-calculator/">Kids BMI calculator (BMI-for-age percentile)</a></li><li><a href="/bmi-chart/">BMI chart for adults</a></li></ul>',
'</article>',
f'<script>window.CK_DATA={json.dumps(JD, separators=(",", ":"), ensure_ascii=False)};</script>',
f'<script>{JS}</script>')

# ---------- head / schema / shell ----------
TITLE = f"Childhood Obesity Rate in America: {f(ob)}% of Kids (CDC Data)"
DESC = f"{f(ob)}% of US children and teens ages 2–19 had obesity in 2021–2023 (measured CDC data), up from {f(ob71)}% in the early 1970s. By year, age, sex and race."
OGT = f"Childhood obesity in America: {f(ob)}% of kids"
OG = f"https://calculatemybmi.net/{SLUG}/og-{SLUG}.png"
shell = open(os.path.join(ROOT, "us-obesity-statistics/index.html"), encoding="utf-8").read()
ld_old = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S).group(1))
org = [n for n in ld_old["@graph"] if n.get("@type") == "Organization"][0]; person = [n for n in ld_old["@graph"] if n.get("@type") == "Person"][0]
ld = {"@context": "https://schema.org", "@graph": [
 {"@type": "Article", "@id": URL + "#article", "headline": "Childhood Obesity in America", "description": DESC,
  "image": {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}, "datePublished": "2026-10-02", "dateModified": "2026-10-02",
  "author": {"@id": "https://calculatemybmi.net/about/#author-bio"}, "publisher": {"@id": "https://calculatemybmi.net/#organization"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "isPartOf": {"@id": "https://calculatemybmi.net/us-obesity-statistics/#article"}, "citation": [HE112, HE119, POP, CDC_CHILD_CAT]},
 {"@type": "Dataset", "@id": URL + "#dataset", "name": "US childhood obesity, overweight and severe obesity, ages 2–19, 1963–2023 (NHANES)",
  "description": "Prevalence of overweight, obesity and severe obesity among US children and adolescents ages 2–19 by survey period, with standard errors, by sex, age group and race and Hispanic origin, from measured heights and weights. Compiled from NCHS Health E-Stat 112.",
  "url": URL, "creator": {"@id": "https://calculatemybmi.net/#organization"}, "isBasedOn": HE112, "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": True, "temporalCoverage": "1963/2023", "spatialCoverage": {"@type": "Place", "name": "United States"},
  "variableMeasured": ["Prevalence of obesity (BMI-for-age at or above the 95th percentile)", "Prevalence of severe obesity (at or above 120% of the 95th percentile)", "Prevalence of overweight (85th to below 95th percentile)", "Standard error"],
  "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"https://calculatemybmi.net/{SLUG}/{CSVF}"}]},
 {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [
  {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://calculatemybmi.net/"},
  {"@type": "ListItem", "position": 2, "name": "US Obesity Statistics", "item": "https://calculatemybmi.net/us-obesity-statistics/"},
  {"@type": "ListItem", "position": 3, "name": "Childhood Obesity", "item": URL}]}, org, person]}
head = shell[:shell.find('<script type="application/ld+json">')]
for pat, rep in [(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>"), (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">'),
                 (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'), (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{H.escape(OGT)}">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">'), (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
                 (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{OG}">'),
                 (r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{H.escape(f"{f(ob)}% of US children and teens ages 2–19 had obesity in 2021–2023, up from {f(ob71)}% in 1971–1974. Source: CDC NCHS.")}">'),
                 (r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{OG}">')]:
    head = re.sub(pat, rep, head, flags=re.S)
rest = shell[shell.find("</script>", shell.find('<script type="application/ld+json">')) + 9:]
page = (head + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, indent=1) + "</script>" + rest[:rest.find("</head>")] + "<style>" + CSS + "</style>"
        + rest[rest.find("</head>"):rest.find("<main>")] + '<main><div class="container" style="max-width:1000px;margin:0 auto;padding:2rem 1rem 3rem;">' + content + "</div>" + rest[rest.find("</main>"):])
os.makedirs(os.path.join(OUT, SLUG), exist_ok=True)
open(os.path.join(OUT, SLUG, "index.html"), "w", encoding="utf-8").write(page)
with open(os.path.join(OUT, SLUG, CSVF), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["# US childhood (ages 2-19) overweight, obesity and severe obesity, measured (NHANES). Source: NCHS Health E-Stat 112, " + HE112 + " (retrieved Oct 2026). Compiled by calculatemybmi.net; CC BY 4.0 for this compilation. Flags: * does not meet NCHS reliability standards; dagger = CDC refers to separate discussion."])
    w.writerow(["table", "survey_period", "group", "measure", "percent", "standard_error", "flag"])
    for p in P1:
        t = T1[p]
        for gi, g in enumerate(["all", "boys", "girls"]):
            for mi, m in enumerate(["overweight", "obesity", "severe_obesity"]):
                w.writerow(["1", p, g + " 2-19", m, t[gi * 6 + mi * 2], t[gi * 6 + mi * 2 + 1], ""])
    for p in P2:
        for gi, g in enumerate(["all", "boys", "girls"]):
            for ai, a in enumerate(["2-5", "6-11", "12-19"]):
                v, se = T2[p][gi][ai]
                if v is None: continue
                fl = "*" if isinstance(v, str) else ""; v = float(v[1:]) if isinstance(v, str) else v
                w.writerow(["2", p, f"{g} {a}" + (" (12-17)" if p == "1966–1970" else ""), "obesity", v, se, fl])
    for p in T3:
        for sx in ("boys", "girls"):
            for i, r in enumerate(RACES):
                v, fl = T3[p][sx][i]; w.writerow(["3", p, f"{sx} {r}", "obesity", v, "", fl])
# OG image
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1200, 630), "#FFFFFF"); dr = ImageDraw.Draw(im)
def font(sz, b=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()
dr.rectangle([0, 0, 1200, 12], fill="#C2481E")
dr.text((56, 50), "Childhood obesity in America", font=font(54, True), fill="#111827")
dr.text((56, 124), "US children and teens ages 2–19 · measured CDC data", font=font(28), fill="#4B5563")
dr.text((56, 200), f"{f(ob)}%", font=font(120, True), fill="#C2481E")
dr.text((56, 340), "had obesity in 2021–2023", font=font(36, True), fill="#1F2937")
dr.text((56, 392), f"up from {f(ob71)}% in 1971–1974", font=font(32), fill="#374151")
dr.text((56, 560), "calculatemybmi.net", font=font(28, True), fill="#6B7280")
cols = ["#7F2A10"] * round(sev) + ["#C2481E"] * (round(ob) - round(sev)) + ["#F4A774"] * round(ow) + ["#9CA3AF"] * round(UNDER)
cols += ["#CDE7D8"] * (100 - len(cols))
for i, c in enumerate(cols):
    r_, c_ = divmod(i, 10); x, y = 720 + c_ * 44, 150 + r_ * 44
    dr.ellipse([x + 10, y, x + 24, y + 14], fill=c); dr.rounded_rectangle([x + 6, y + 16, x + 28, y + 36], radius=8, fill=c)
dr.text((720, 600 - 22), "Out of 100 kids", font=font(22, True), fill="#4B5563")
im.save(os.path.join(OUT, SLUG, f"og-{SLUG}.png"), optimize=True)
print(json.dumps(dict(ob=ob, sev=sev, ow=ow, fold=fold, n_ob=n_ob, n_sev=n_sev, n_ow=n_ow, healthy=healthy, ow_ob=ow_ob, ci18=ci18, ci23=ci23, overlap=overlap, title_len=len(TITLE), desc_len=len(DESC))))
