#!/usr/bin/env python3
"""CMB-019 AVERAGE-WEIGHT — rebuilds /average-weight/ to the D-14 guide pattern (DESIGN.md "Guide pages"; the chart
pages applied it in CMB-014 to CMB-018): intro, answer block and key takeaways, a hero figure, contents chips, a tool,
real tables, a flat FAQ whose JSON-LD equals the visible answers, sources and method, one related block, one 680 px
reading column. No <article> wrapper: the sections sit directly in main .container, as on the calculators.

Wedge (owner's SERP pastes of 2026-10-22, US/English, not personalized: "average weight for men", "average weight 5 4
woman", "average weight for 5 9 male"): every result answers with the national average (most still quote 199.8 lb,
CDC's 2015-2018 figure) or with a healthy-weight table; the AI Overview for "average weight for 5 9 male" gives the
national average as the average at 5'9". Nobody shows what Americans of a given height actually weigh. This page does:
  1. the measured average, middle half and share with a BMI of 25 or more at every height, women 4'9"-5'9" and men
     5'2"-6'3" (CDC NHANES August 2021-August 2023, our calculation), against the healthy range for that height;
  2. a tool that places your weight among people of your sex measured at your height or an inch either side;
  3. by age, with each stated change outside its margin of error, and the national figures equal to NCHS's tables;
  4. why the numbers differ between sites (199.8 lb is 2015-2018) and how they changed since 1960.

Every number comes from research/average-weight/avgw_results.json (compute.py, which reproduces 204 published values of
NCHS Series 3 No. 50 exactly), the weight-table gate's rule (scripts/check_weight_tables.py), or a source verified in
chat (constants below, each with its registry row). Round once: a printed figure is formatted from the 4-decimal value.

usage: python3 gen_aw.py REPO_ROOT
Runs once, on average-weight/index.html as it stood at 56acc27 (the A2 page); kept as the build record. The page is
written with {TODAY} in its Article and Dataset dateModified; apply_build.py puts in the apply date ("today": true).
"""
import sys, os, re, json, html, math, csv
from decimal import Decimal, ROUND_HALF_UP

ROOT = sys.argv[1]
AV = json.load(open(os.path.join(ROOT, 'research/average-weight/avgw_results.json')))
PAGE = os.path.join(ROOT, 'average-weight/index.html')
src = open(PAGE, encoding='utf-8', newline='').read()
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_weight_tables import bounds as gate_bounds, round1          # the CMB-008 gate's own rule

SITE = 'https://calculatemybmi.net'
URL = SITE + '/average-weight/'
CSV_PATH = '/average-weight/average-weight-nhanes-2021-2023.csv'

# ---------------------------------------------------------------- formatting (round once)
def f1(x): return f'{x:.1f}'
def pc(x): return f'{x:.1f}%'
def whole(x): return int(math.floor(x + 0.5))
def dcm(inches): return str((Decimal(str(inches)) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))
NCHS_LB = 2.2046                                                 # compute.py: weights were converted with NCHS's factor
def kg(lb): return str((Decimal(str(lb)) / Decimal(str(NCHS_LB))).quantize(Decimal('0.1'), ROUND_HALF_UP))
def ft(h): return f'{h // 12}′{h % 12}″'
def spoken(h): return f'{h // 12} feet' + (f' {h % 12} inch' + ('es' if h % 12 > 1 else '') if h % 12 else '')
def share(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{x:.1f}%'

# ---------------------------------------------------------------- numbers: US adults, 2021-2023 (compute.py)
M, F = AV['men'], AV['women']
SEXES = (('women', F, 'f'), ('men', M, 'm'))
assert (f1(M['wt_lb']['mean']), f1(F['wt_lb']['mean'])) == ('199.0', '171.8')               # = Series 3 No. 50, Table 4
assert (M['wt_lb']['n'], F['wt_lb']['n']) == (2688, 3254)
assert (kg(M['wt_lb']['mean']), kg(F['wt_lb']['mean'])) == ('90.3', '77.9')
assert (f1(M['wt_pct']['p50']), f1(F['wt_pct']['p50'])) == ('191.0', '162.0')
assert (f1(M['ht_in']['mean']), f1(F['ht_in']['mean'])) == ('68.9', '63.5')                 # Table 8
assert (f1(M['BMXBMI']['mean']), f1(F['BMXBMI']['mean'])) == ('29.4', '30.0')
assert F['BMXBMI']['mean'] < 30                                     # "at the line", not "in the obesity range"
assert (f1(M['waist_in']['mean']), f1(F['waist_in']['mean'])) == ('40.6', '38.5')           # Table 12 (cm) and FastStats
WP = {s: [whole(d['waist_pct']['p25']), whole(d['waist_pct']['p75'])] for s, d, _ in SEXES}
assert WP == {'women': [33, 43], 'men': [36, 44]}, WP
OVER = {s: d['waist_over_line']['pct'] for s, d, _ in SEXES}
assert (f1(OVER['men']), f1(OVER['women'])) == ('47.4', '67.5')
# By height: heights with 30 or more people measured; the average is above the healthy range at every one.
HT = {s: {int(h): v for h, v in d['height'].items()} for s, d, _ in SEXES}
assert sorted(HT['women']) == list(range(57, 70)) and sorted(HT['men']) == list(range(62, 76))
for s in HT:
    for h, v in HT[s].items():
        assert v['wt']['mean'] > gate_bounds('lb', h, h * 2.54, 1)[1], (s, h)        # above the healthy range
B25 = {s: (min(v['bmi25_plus']['pct'] for v in HT[s].values()), max(v['bmi25_plus']['pct'] for v in HT[s].values()))
       for s in HT}
assert {s: (whole(a), whole(b)) for s, (a, b) in B25.items()} == {'women': (60, 78), 'men': (64, 81)}, B25
NMIN = {s: (min(v['wt']['n'] for v in HT[s].values()), max(v['wt']['n'] for v in HT[s].values())) for s in HT}
assert NMIN == {'women': (40, 484), 'men': (32, 374)}, NMIN
A54, A59, A57m, A65f = HT['women'][64], HT['men'][69], HT['men'][67], HT['women'][65]
assert (f1(A54['wt']['mean']), f1(A59['wt']['mean']), f1(A57m['wt']['mean']), f1(A65f['wt']['mean'])) == \
       ('171.2', '204.0', '188.7', '178.7')
# By age (decades). A change between neighboring decades is stated only when its 95% CI excludes zero.
AGES = ('20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80+')
STEP = {s: d['age_steps'] for s, d, _ in SEXES}
def step(s, a, b, v='wt_lb'): return STEP[s][f'{b} minus {a}'][v]
assert step('women', '20–29', '30–39')['excludes_0'] and step('men', '20–29', '30–39')['excludes_0']
for s in ('women', 'men'):                                          # 30-59: no step is outside its margin of error
    assert not step(s, '30–39', '40–49')['excludes_0'] and not step(s, '40–49', '50–59')['excludes_0'], s
for a, b in (('50–59', '60–69'), ('60–69', '70–79'), ('70–79', '80+')):
    assert step('women', a, b)['excludes_0'] and step('women', a, b)['diff'] < 0, (a, b)       # women: down each decade
assert step('men', '70–79', '80+')['excludes_0'] and step('men', '70–79', '80+')['diff'] < 0
assert not step('men', '50–59', '60–69')['excludes_0'] and not step('men', '60–69', '70–79')['excludes_0']
UP_F, UP_M = step('women', '20–29', '30–39')['diff'], step('men', '20–29', '30–39')['diff']
DOWN_M80 = -step('men', '70–79', '80+')['diff']
assert (f1(UP_F), f1(UP_M), f1(DOWN_M80)) == ('13.4', '10.2', '13.3')
for s, d, _ in SEXES:                                              # 30 to 59: no pair of decades differs (95% CI)
    P30 = d['age_pairs_30_59']
    assert sorted(P30) == ['40–49 minus 30–39', '50–59 minus 30–39', '50–59 minus 40–49'], sorted(P30)
    assert not any(x['wt_lb']['excludes_0'] for x in P30.values()), s
AGE_LO = {s: min(d['age'][g]['wt']['mean'] for g in AGES[1:4]) for s, d, _ in SEXES}       # 30-59 range
AGE_HI = {s: max(d['age'][g]['wt']['mean'] for g in AGES[1:4]) for s, d, _ in SEXES}
# Then and now: ages 20-74, the age range of CDC's 1960-1962 and 1999-2002 means.
NOW74 = {s: d['wt_20_74']['mean'] for s, d, _ in SEXES}
assert (f1(NOW74['men']), f1(NOW74['women'])) == ('200.2', '173.7')

# ---------------------------------------------------------------- sources verified in chat
# NCHS Series 3 No. 50 (registry nhanes-anthropometric-reference): Table 4 weight, Table 8 height, Table 12 waist (cm),
#   adults 20+, August 2021-August 2023; compute.py reproduces every mean and percentile in them (204 values).
# CDC FastStats "Body Measurements" (registry cdc-faststats-body-measurements; read 2026-10-22, last reviewed June 26,
#   2025): men 68.9 in, 199.0 lb, waist 40.6 in; women 63.5 in, 171.8 lb, waist 38.5 in; source: Series 3 No. 50.
# NCHS Series 3 No. 46 (registry nhanes-anthropometric-reference-2015-2018; January 2021): adults 20+, 2015-2018:
#   men 199.8 lb (5,085 examined), women 170.8 lb (5,386).
S46 = (199.8, 170.8)
# CDC Advance Data No. 347 (registry nchs-advance-data-347; Ogden et al., October 27, 2004), Table 6 "Mean weight
#   (pounds) by survey, sex, and age group; adults", ages 20-74: men 166.3 lb in 1960-1962 and 191.0 lb in 1999-2002;
#   women 140.2 and 164.3 lb. No age-adjustment note on the table (the trend tests were age-adjusted), so the printed
#   means are compared with our crude weighted mean for the same ages.
AD347 = {'men': (166.3, 191.0), 'women': (140.2, 164.3)}
GAIN = {s: NOW74[s] - AD347[s][0] for s in AD347}
assert (f1(GAIN['men']), f1(GAIN['women'])) == ('33.9', '33.5')
# CDC Adult BMI Categories (registry cdc-adult-bmi-categories): 18.5 to less than 25 healthy, "regardless of age, sex,
#   or race". NHLBI 1998 (registry nhlbi-1998-obesity-guidelines): waist over 102 cm (40 in) men, over 88 cm (35 in) women.

# ---------------------------------------------------------------- text helpers and links
def esc(s): return html.escape(s, quote=False)
EXT = 'target="_blank" rel="noopener"'
def ext(url, text): return f'<a href="{url}" {EXT}>{text}</a>'
U = {
    'bmx': 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm',
    's50': 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf',
    'fast': 'https://www.cdc.gov/nchs/fastats/body-measurements.htm',
    's46': 'https://www.cdc.gov/nchs/data/series/sr_03/sr03-046-508.pdf',
    'ad347': 'https://www.cdc.gov/nchs/data/ad/ad347.pdf',
    'cdc_cat': 'https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',
    'nhlbi_tg': 'https://www.ncbi.nlm.nih.gov/books/NBK2004/',
}
REG = {r['domain']: r for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8'))}
for k, d in (('bmx', 'nhanes-2021-2023-exam-files'), ('s50', 'nhanes-anthropometric-reference'),
             ('fast', 'cdc-faststats-body-measurements'), ('s46', 'nhanes-anthropometric-reference-2015-2018'),
             ('ad347', 'nchs-advance-data-347'), ('cdc_cat', 'cdc-adult-bmi-categories')):
    assert REG[d]['url'] == U[k], (k, REG[d]['url'])                   # every link is the registry's
assert U['nhlbi_tg'] in REG['nhlbi-1998-obesity-guidelines']['notes']

# ---------------------------------------------------------------- SVG helpers and collision bookkeeping
TEXTS, RECTS, VBW = [], [], {}
def text(svg, x, y, s, size, anchor='middle', weight=400, fill='#111827'):
    w = len(s) * size * (0.60 if weight >= 600 else 0.55)
    x0 = x - w / 2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
    TEXTS.append((svg, x0, y - size * 0.8, x0 + w, y + size * 0.2, s))
    wt = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}"{wt} fill="{fill}">{esc(s)}</text>'
def track(svg, x0, y0, x1, y1, rid): RECTS.append((svg, x0, y0, x1, y1, rid))

SER = {'women': '#be185d', 'men': '#4338ca'}                    # DESIGN.md series colors (CMB-016)
HEALTHY_FILL, HEALTHY_EDGE, INK, MUTED, GRID = '#d1fae5', '#15803d', '#111827', '#4b5563', '#e5e7eb'

# Hero: the average at each height for women and men, over the band of healthy weights for each height.
VBW['hero'] = W1 = 320
X0, X1, H0, H1 = 46, 308, 57, 75
def hx(h): return X0 + (h - H0) * (X1 - X0) / (H1 - H0)
PT, PB, WLO, WHI = 96, 296, 80, 260
def hy(w): return PB - (w - WLO) * (PB - PT) / (WHI - WLO)
hero = [text('hero', W1 / 2, 17, 'Average weight at each height', 14, weight=700),
        text('hero', W1 / 2, 36, 'US adults 20 and over, measured 2021–2023', 12, fill='#374151')]
# legend
hero.append(f'<circle cx="20" cy="54" r="4" fill="{SER["women"]}"/>'); track('hero', 16, 50, 24, 58, 'sw')
hero.append(text('hero', 30, 58, 'Women', 12, anchor='start', fill='#1f2937'))
hero.append(f'<circle cx="92" cy="54" r="4" fill="{SER["men"]}"/>'); track('hero', 88, 50, 96, 58, 'sw')
hero.append(text('hero', 102, 58, 'Men', 12, anchor='start', fill='#1f2937'))
hero.append(f'<rect x="14" y="68" width="14" height="10" fill="{HEALTHY_FILL}" stroke="{HEALTHY_EDGE}" stroke-width="1"/>')
track('hero', 14, 68, 28, 78, 'sw')
hero.append(text('hero', 34, 77, 'Healthy weight, BMI 18.5–24.9', 12, anchor='start', fill='#1f2937'))
# grid
for w in (100, 150, 200, 250):
    hero.append(f'<line x1="{X0}" y1="{hy(w):.1f}" x2="{X1}" y2="{hy(w):.1f}" stroke="{GRID}" stroke-width="1"/>')
    hero.append(text('hero', X0 - 6, hy(w) + 4, f'{w} lb' if w == 250 else str(w), 12, anchor='end', fill=MUTED))
# healthy band (the gate's whole-pound limits at each inch)
HB = {h: gate_bounds('lb', h, h * 2.54, 1) for h in range(H0, H1 + 1)}
band = ' '.join(f'{hx(h):.1f},{hy(HB[h][1]):.1f}' for h in range(H0, H1 + 1)) + ' ' + \
       ' '.join(f'{hx(h):.1f},{hy(HB[h][0]):.1f}' for h in range(H1, H0 - 1, -1))
hero.append(f'<polygon points="{band}" fill="{HEALTHY_FILL}" stroke="{HEALTHY_EDGE}" stroke-width="1" stroke-opacity="0.5">'
            f'<title>Healthy weight at each height, BMI 18.5 to 24.9 (CDC categories)</title></polygon>')
# series
for s, d, _ in SEXES:
    pts = sorted(HT[s].items())
    hero.append(f'<polyline points="{" ".join(f"{hx(h):.1f},{hy(v["wt"]["mean"]):.1f}" for h, v in pts)}" fill="none" '
                f'stroke="{SER[s]}" stroke-width="2"/>')
    for h, v in pts:
        hero.append(f'<circle cx="{hx(h):.1f}" cy="{hy(v["wt"]["mean"]):.1f}" r="3.5" fill="{SER[s]}" stroke="#ffffff" '
                    f'stroke-width="1"><title>{s.capitalize()} {ft(h)}: average {f1(v["wt"]["mean"])} lb '
                    f'({v["wt"]["n"]} measured)</title></circle>')
# x axis
hero.append(f'<line x1="{X0}" y1="{PB}" x2="{X1}" y2="{PB}" stroke="#9ca3af" stroke-width="1"/>')
for h in (58, 62, 66, 70, 74):
    hero.append(f'<line x1="{hx(h):.1f}" y1="{PB}" x2="{hx(h):.1f}" y2="{PB + 4}" stroke="#9ca3af" stroke-width="1"/>')
    hero.append(text('hero', hx(h), PB + 18, ft(h), 12, fill=MUTED))
hero.append(text('hero', W1 / 2, PB + 40, 'CDC NHANES 2021–2023; our calculation', 12, fill=MUTED))
H1V = PB + 48
svg_hero = (f'<svg viewBox="0 0 {W1} {H1V}" width="{W1}" height="{H1V}" role="img" aria-labelledby="fig-hero-t fig-hero-d" '
            'font-family="inherit"><title id="fig-hero-t">Average weight of US women and men at each height, above the '
            'healthy range</title><desc id="fig-hero-d">Average weight of US adults aged 20 and over at each height, '
            'measured by CDC in August 2021 to August 2023, over the band of healthy weights for each height (BMI 18.5 '
            'to 24.9, CDC categories). '
            + ' '.join(f'{s.capitalize()}: ' + ', '.join(f'{spoken(h)} {f1(v["wt"]["mean"])} pounds' for h, v in sorted(HT[s].items()))
                       + '.' for s, _, _ in SEXES)
            + ' At every height shown, the average is above the healthy band. Our calculation.</desc>' + ''.join(hero) + '</svg>')

def overlap(a, b): return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]
for i, a in enumerate(TEXTS):
    for b in TEXTS[i + 1:]:
        if a[0] == b[0] and overlap(a, b): raise SystemExit(f'label collision in {a[0]}: {a[5]!r} / {b[5]!r}')
    for r in RECTS:
        if r[0] == a[0] and overlap(a, r): raise SystemExit(f'label over a shape in {a[0]}: {a[5]!r}')
for svg, x0, y0, x1, y1, s in TEXTS:
    assert x0 >= 0 and x1 <= VBW[svg], f'{svg} label outside the viewBox: {s!r} ({x0:.0f}-{x1:.0f})'
for s in HT:                                                     # no label sits on a data point or the band
    for h, v in HT[s].items():
        y = hy(v['wt']['mean'])
        assert PT < y < PB, (s, h)

# ---------------------------------------------------------------- the tool (data in the page; rounding as printed)
TOOL = {'avg': {c: round(d['wt_lb']['mean'], 1) for _, d, c in SEXES}, 'h': {}, 'age': {}, 'hq': {}}
for s, d, c in SEXES:
    TOOL['h'][c] = {str(h): {'a': round(v['wt']['mean'], 1), 'n': v['wt']['n'], 'q': [round(x, 1) for x in v['q']],
                             'p': [round(x, 1) for x in v['p10_p90']], 'c': [round(x, 1) for x in v['cdf']],
                             'b': round(v['bmi']['mean'], 1), 'w': v['nwin']} for h, v in sorted(HT[s].items())}
    TOOL['age'][c] = {g: round(d['age'][g]['wt']['mean'], 1) for g in AGES}
    TOOL['hq'][c] = [round(x, 2) for x in d['ht_q']]
# The tool's rules, mirrored by aw_test_playwright.py:
#  - height: ft + in, or cm / 2.54; compared at the nearest whole inch (floor(x + 0.5), as compute.py rounds measured
#    heights); 4 ft to 7 ft 6 in (122 to 229 cm), else a message. Weight optional: 50 to 700 lb or 23 to 318 kg.
#  - the share lighter than you reads the 1st-99th percentiles of weight among people of your sex measured at that height
#    or an inch either side (rounded heights h-1 to h+1, as compute.py groups them; linear between percentiles; below the
#    1st = 0, above the 99th = 100) and prints by the CMB-016 rule;
#  - BMI as the calculators: 703 x lb / in^2 or kg / m^2, rounded half up to 0.1; healthy = the whole lb (or kg) with a
#    rounded BMI of 18.5 to 24.9 at the height entered (scripts/check_weight_tables.py);
#  - kg are the data's pounds / 2.2046 (NCHS's factor); a weight entered in kg is compared as kg x 2.2046.
TOOL_JS = r'''(function(){var D=window.AWT,$=function(i){return document.getElementById(i);};
var sex='f',units='us',out=$('awt-out'),SER={f:'#be185d',m:'#4338ca'},WD={f:'women',m:'men'},ONE={f:'woman',m:'man'},F=2.2046;
function r1(x){return Math.floor(x*10+0.5+1e-9)/10;}
function d1(x){return r1(x).toFixed(1);}
function ftin(h){return Math.floor(h/12)+'′'+(h%12)+'″';}
function shareTxt(x){return x>=99.5?'more than 99%':x<=0.5?'under 1%':Math.round(x)+'%';}
function below(c,v){if(v<c[0])return 0;if(v>c[98])return 100;for(var i=0;i<98;i++){if(v<=c[i+1]){var sp=c[i+1]-c[i];return i+1+(sp>0?(v-c[i])/sp:0);}}return 99;}
function healthy(hIn,cm,metric){var lo=null,hi=null,i,b,m=cm/100;for(i=20;i<=700;i++){b=metric?r1(i/(m*m)):r1(703*i/(hIn*hIn));if(b>=18.5&&b<=24.9){if(lo===null)lo=i;hi=i;}}return [lo,hi];}
function cat(b){return b<18.5?['underweight','underweight']:b<25?['normal','a healthy weight']:b<30?['overweight','overweight']:['obese','obesity'];}
function fig(cell,hb,wd,s,metric){var W=280,P=24,k=metric?1/F:1,u=metric?' kg':' lb',p0=cell.p[0]*k,p1=cell.p[1]*k,q0=cell.q[0]*k,q2=cell.q[2]*k,a=cell.a*k,
 vals=[p0,p1,hb[0],hb[1]].concat(wd?[wd]:[]),v0=Math.min.apply(null,vals),v1=Math.max.apply(null,vals),st=metric?10:20;
 if(Math.ceil(v1/st)-Math.floor(v0/st)>7)st*=2;
 var lo=Math.floor(v0/st)*st,hi=Math.ceil(v1/st)*st,X=function(v){return P+(v-lo)*(W-2*P)/(hi-lo);},g='',t,lx,x;
 g+='<line x1="'+X(p0).toFixed(1)+'" y1="35" x2="'+X(p1).toFixed(1)+'" y2="35" stroke="'+SER[s]+'" stroke-width="1.5"/>';
 g+='<rect x="'+X(q0).toFixed(1)+'" y="27" width="'+(X(q2)-X(q0)).toFixed(1)+'" height="16" fill="'+SER[s]+'" fill-opacity="0.16" stroke="'+SER[s]+'" stroke-width="1"/>';
 g+='<line x1="'+X(a).toFixed(1)+'" y1="23" x2="'+X(a).toFixed(1)+'" y2="47" stroke="#111827" stroke-width="2"/>';
 g+='<rect x="'+X(hb[0]).toFixed(1)+'" y="54" width="'+Math.max(2,X(hb[1])-X(hb[0])).toFixed(1)+'" height="8" rx="2" fill="#22c55e"/>';
 if(wd){g+='<line x1="'+X(wd).toFixed(1)+'" y1="18" x2="'+X(wd).toFixed(1)+'" y2="66" stroke="#111827" stroke-width="2" stroke-dasharray="3 2"/>';
  t='You '+Math.round(wd)+u;lx=Math.min(Math.max(X(wd),t.length*3.6+2),W-t.length*3.6-2);
  g+='<text x="'+lx.toFixed(1)+'" y="13" font-size="12" text-anchor="middle" fill="#1f2937">'+t+'</text>';}
 for(x=lo;x<=hi;x+=st)g+='<text x="'+X(x).toFixed(1)+'" y="82" font-size="12" text-anchor="middle" fill="#4b5563">'+x+(x===hi?u:'')+'</text>';
 return '<svg viewBox="0 0 '+W+' 88" role="img" aria-label="Weights of US '+WD[s]+' of this height: the 10th to 90th percentile, the middle half and their average; the healthy range'+(wd?'; your weight':'')+'" xmlns="http://www.w3.org/2000/svg" font-family="inherit">'+g+'</svg>';}
function msg(t){out.innerHTML='<p class="er-note">'+t+'</p>';out.classList.add('visible');}
function show(){var metric=units==='metric',hIn,cm,age=$('awt-age').value,wv=parseFloat($('awt-w').value),u=metric?' kg':' lb',k=metric?1/F:1;
 if(metric){cm=parseFloat($('awt-cm').value);hIn=cm/2.54;}else{hIn=parseFloat($('awt-ft').value)*12+parseFloat($('awt-in').value||'0');cm=hIn*2.54;}
 if(!(hIn>=48&&hIn<=90))return msg('Enter a height from 4 ft to 7 ft 6 in (122 to 229 cm).');
 var has=wv>0;if(has&&!(metric?wv>=23&&wv<=318:wv>=50&&wv<=700))return msg('Enter a weight from 50 to 700 lb (23 to 318 kg), or leave it empty.');
 var wlb=has?(metric?wv*F:wv):0,hr=Math.floor(hIn+0.5),cell=D.h[sex][String(hr)],w=WD[sex],hb=healthy(hIn,cm,metric),hbTxt=hb[0]+' to '+hb[1]+u,
  cm1=function(i){return (Math.round(i*25.4)/10).toFixed(1);},tag=ftin(hr)+(metric?' ('+cm1(hr)+' cm)':''),
  win=ftin(hr-1)+' to '+ftin(hr+1)+(metric?' ('+cm1(hr-1)+' to '+cm1(hr+1)+' cm)':''),b=0,c=null,h='',notes=[];
 function one(lb){return metric?d1(lb/F)+' kg ('+d1(lb)+' lb)':d1(lb)+' lb ('+d1(lb/F)+' kg)';}
 function rng(a,z){return Math.round(a*k)+' to '+Math.round(z*k)+u;}
 if(has){b=metric?r1(wv/((cm/100)*(cm/100))):r1(703*wv/(hIn*hIn));c=cat(b);}
 var tint=has?' '+c[0]:'';
 if(cell&&has)h+='<div class="bmi-result-card'+tint+'"><div class="bmi-value">'+shareTxt(below(cell.c,wlb))+'</div><div class="bmi-category">of US '+w+' measured at '+win+' weigh less than you</div><div class="bmi-range">The average '+ONE[sex]+' of '+ftin(hr)+' weighs '+one(cell.a)+'; the middle half weigh '+rng(cell.q[0],cell.q[2])+'.</div></div>';
 else if(cell)h+='<div class="bmi-result-card"><div class="bmi-value">'+d1(cell.a*k)+u+'</div><div class="bmi-category">is the average weight of US '+w+' who are '+tag+'</div><div class="bmi-range">The middle half weigh '+rng(cell.q[0],cell.q[2])+'; '+cell.n.toLocaleString('en-US')+' '+w+' measured (CDC, 2021–2023; our calculation).</div></div>';
 else h+='<div class="bmi-result-card'+tint+'"><div class="bmi-value">'+d1(D.avg[sex]*k)+u+'</div><div class="bmi-category">is the average weight of all US '+w+'</div><div class="bmi-range">CDC measured fewer than 30 '+w+' at '+ftin(hr)+', too few for an average at that height.</div></div>';
 h+='<div class="er">';
 if(cell){notes.push('Box: the middle half of US '+w+' of '+ftin(hr)+', '+rng(cell.q[0],cell.q[2])+'. Line: the 10th to 90th percentile. Tick: their average, '+one(cell.a)+'.');
  notes.push('Green: a healthy weight at your height, '+hbTxt+' (BMI 18.5 to 24.9, CDC).');
  if(has){var dd=(wlb-cell.a)*k;notes.push('You weigh '+d1(Math.abs(dd))+u+' '+(dd>=0?'more':'less')+' than the average US '+ONE[sex]+' of '+ftin(hr)+'.');}
  if(cell.n<60)notes.push('Only '+cell.n+' '+w+' were measured at '+ftin(hr)+', so treat these numbers as a rough guide.');
  h+='<section class="er-section"><h3>Where you fall at '+ftin(hr)+'</h3>'+fig(cell,hb,has?wv:0,sex,metric)+notes.map(function(n){return '<p class="er-note">'+n+'</p>';}).join('')+'</section>';}
 if(has)h+='<section class="er-section"><h3>Your BMI</h3><p class="er-note"><span class="cat-dot '+c[0]+'"></span>Your BMI is '+b.toFixed(1)+', '+c[1]+' (CDC categories). A healthy weight at your height is '+hbTxt+'.'+(cell?' US '+w+' of '+ftin(hr)+' have an average BMI of '+cell.b.toFixed(1)+'.':'')+'</p></section>';
 else if(!cell)h+='<section class="er-section"><h3>Healthy weight</h3><p class="er-note">A healthy weight at your height is '+hbTxt+' (BMI 18.5 to 24.9, CDC).</p></section>';
 if(age)h+='<section class="er-section"><h3>US '+w+' aged '+age+'</h3><p class="er-note">They weigh '+one(D.age[sex][age])+' on average, across all heights. All US '+w+' average '+one(D.avg[sex])+'.</p></section>';
 var hp=below(D.hq[sex],hIn);h+='<section class="er-section"><h3>Your height</h3><p class="er-note">'+(hp<=0.5?'Shorter than almost all':hp>=99.5?'Taller than almost all':'Taller than about '+Math.round(hp)+'% of')+' US '+w+' (CDC measured heights).</p></section>';
 h+='<div class="er-section"><p class="er-note">Our calculation from CDC NHANES August 2021–August 2023: adults 20 and over, weighed and measured, survey-weighted.'+(cell&&has?' The share compares you with the '+cell.w.toLocaleString('en-US')+' '+w+' measured at '+ftin(hr-1)+' to '+ftin(hr+1)+' (heights rounded to the nearest inch).':'')+'</p></div></div>';
 out.innerHTML=h;out.classList.add('visible');}
function pick(sel,attr,fn){var bs=document.querySelectorAll(sel);for(var i=0;i<bs.length;i++)bs[i].addEventListener('click',function(){for(var j=0;j<bs.length;j++){var on=bs[j]===this;bs[j].classList.toggle('active',on);bs[j].setAttribute('aria-pressed',on?'true':'false');}fn(this.getAttribute(attr));});}
pick('#awt [data-sex]','data-sex',function(v){sex=v;});
pick('#awt [data-units]','data-units',function(v){if(v===units)return;var w=parseFloat($('awt-w').value);
 if(v==='metric'){var hi=parseFloat($('awt-ft').value)*12+parseFloat($('awt-in').value||'0');if(hi>0)$('awt-cm').value=Math.round(hi*2.54);if(w>0)$('awt-w').value=(w*0.45359237).toFixed(1);}
 else{var cc=parseFloat($('awt-cm').value);if(cc>0){var t=Math.floor(cc/2.54+0.5);$('awt-ft').value=Math.floor(t/12);$('awt-in').value=t%12;}if(w>0)$('awt-w').value=Math.round(w/0.45359237);}
 units=v;$('awt-us').hidden=v!=='us';$('awt-metric').hidden=v!=='metric';$('awt-w-label').textContent=v==='us'?'Weight (lb)':'Weight (kg)';});
$('awt-go').addEventListener('click',show);
['awt-ft','awt-in','awt-cm','awt-w'].forEach(function(id){$(id).addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();show();}});});
})();'''

# ---------------------------------------------------------------- FAQ (visible answer = JSON-LD text)
# People also ask in the owner's US/English pastes of 2026-10-22 that fit this page's intent ("How heavy is a 5'7" man?",
# "Is 200 pounds heavy for a male?", "Is 180 pounds at 5'9" overweight?"), then the ledger's biggest queries the page owns
# (research/keyword-ledger.csv): the national averages, the four secondary heights (5'4", 5'5" and 5'7" women, 5'9" men),
# BMI, waist, age, and the 199.8 lb the results still quote. Healthy-weight questions at one height (5'4" women, 5'10"
# men) and "normal BMI" belong to the chart pages and /blog/healthy-bmi-range/, which already answer them.
def hb(h): return gate_bounds('lb', h, h * 2.54, 1)
def cellq(s, h): v = HT[s][h]; return whole(v['q'][0]), whole(v['q'][2])
assert hb(64) == (108, 145) and hb(69) == (125, 168) and hb(67) == (118, 159) and hb(65) == (111, 149)
BMI200 = {h: round1(703.0 * 200 / (h * h)) for h in (68, 69, 74, 75, 76)}
assert BMI200 == {68: 30.4, 69: 29.5, 74: 25.7, 75: 25.0, 76: 24.3}, BMI200
assert 24.99 < 703.0 * 200 / 75 ** 2 < 25                                       # 24.996: "right at the line" at 6'3"
assert all(round1(703.0 * 200 / (h * h)) >= 30 for h in range(58, 69))        # obesity at every shorter height
assert all(18.5 <= round1(703.0 * 200 / (h * h)) < 25 for h in range(76, 88))  # healthy from 6'4" to 7'3"
assert all(25.7 <= round1(703.0 * 200 / (h * h)) < 30 for h in range(69, 75))  # overweight from 5'9" to 6'2"
BMI180 = round1(703.0 * 180 / 69 ** 2); assert BMI180 == 26.6
A57f = HT['women'][67]; assert f1(A57f['wt']['mean']) == '189.2'
MED69 = whole(A59['q'][1]); assert MED69 == 192 and MED69 > 180 and A59['wt']['ci95'][0] > 180
BMED = {s: f1(d['bmi_p50']) for s, d, _ in SEXES}; assert BMED == {'women': '28.3', 'men': '28.2'}, BMED
def per_height(s, h, v):
    return (f'{f1(v["wt"]["mean"])} lb ({kg(v["wt"]["mean"])} kg), from {v["wt"]["n"]} US {s} measured at {ft(h)}; the '
            f'middle half weigh {cellq(s, h)[0]} to {cellq(s, h)[1]} lb (our calculation from CDC data, 2021–2023). A '
            f'healthy weight at {ft(h)} is {hb(h)[0]} to {hb(h)[1]} lb ({ext(U["cdc_cat"], "CDC categories")}).')
FAQ = [
    ('What is the average weight for a man?',
     f'<strong>{f1(M["wt_lb"]["mean"])} lb ({kg(M["wt_lb"]["mean"])} kg)</strong> for US men aged 20 and over, measured by '
     f'CDC in 2021–2023 ({ext(U["s50"], "NCHS")}). Half of men weigh {f1(M["wt_pct"]["p50"])} lb or more. The average man is '
     f'{f1(M["ht_in"]["mean"])} inches tall, about 5′9″, and at 5′9″ a healthy weight is {hb(69)[0]} to {hb(69)[1]} lb '
     f'({ext(U["cdc_cat"], "CDC categories")}).'),
    ('What is the average weight for a woman?',
     f'<strong>{f1(F["wt_lb"]["mean"])} lb ({kg(F["wt_lb"]["mean"])} kg)</strong> for US women aged 20 and over who aren’t '
     f'pregnant, measured by CDC in 2021–2023 ({ext(U["s50"], "NCHS")}). Half of women weigh {f1(F["wt_pct"]["p50"])} lb or '
     f'more. The average woman is {f1(F["ht_in"]["mean"])} inches tall, between 5′3″ and 5′4″.'),
    ('What is the average weight for a 5′4″ woman?', per_height('women', 64, A54)),
    ('What is the average weight for a 5′5″ woman?', per_height('women', 65, A65f)),
    ('What is the average weight for a 5′7″ woman?', per_height('women', 67, A57f)),
    ('What is the average weight for a 5′9″ man?',
     per_height('men', 69, A59) + f' Some answers give {f1(S46[0])} lb for 5′9″, but that is CDC’s 2015–2018 '
     'average for all US men, whatever their height.'),
    ('How heavy is a 5′7″ man?',
     f'US men who are 5′7″ weigh {f1(A57m["wt"]["mean"])} lb on average, and the middle half weigh {cellq("men", 67)[0]} '
     f'to {cellq("men", 67)[1]} lb ({A57m["wt"]["n"]} men; our calculation from CDC data, 2021–2023). A healthy weight '
     f'at 5′7″ is {hb(67)[0]} to {hb(67)[1]} lb ({ext(U["cdc_cat"], "CDC categories")}).'),
    ('Is 200 pounds heavy for a male?',
     f'It is about average: US men weigh {f1(M["wt_lb"]["mean"])} lb on average ({ext(U["s50"], "NCHS")}). Whether it is '
     f'a healthy weight depends on height. For a man of 6′4″ or taller, 200 lb is in the healthy range (a BMI of '
     f'{f1(BMI200[76])} at 6′4″); at 6′3″ it sits right at the line ({f1(BMI200[75])}); from 5′9″ to 6′2″ it is '
     f'overweight (a BMI of {f1(BMI200[69])} down to {f1(BMI200[74])}); at 5′8″ and shorter it is obesity, a BMI of '
     f'{f1(BMI200[68])} or more ({ext(U["cdc_cat"], "CDC categories")}).'),
    ('Is 180 pounds at 5′9″ overweight?',
     f'By BMI, yes: 180 lb at 5′9″ is a BMI of {f1(BMI180)}, in CDC’s overweight range of 25 to 29.9, and a healthy weight '
     f'at 5′9″ is {hb(69)[0]} to {hb(69)[1]} lb ({ext(U["cdc_cat"], "CDC categories")}). It is below the average for that '
     f'height: US men who are 5′9″ weigh {f1(A59["wt"]["mean"])} lb on average, and half weigh {MED69} lb or more (our '
     'calculation from CDC data, 2021–2023).'),
    ('What is the average BMI?',
     f'{f1(M["BMXBMI"]["mean"])} for US men and {f1(F["BMXBMI"]["mean"])} for women aged 20 and over, measured in 2021–2023 '
     f'({ext(U["s50"], "NCHS")}). Both are above CDC’s healthy range of 18.5 to 24.9; the women’s average is at the line '
     f'between overweight and obesity (30). Half of men have a BMI of {BMED["men"]} or more, and half of women '
     f'{BMED["women"]} or more.'),
    ('What is the average waist size?',
     f'{f1(M["waist_in"]["mean"])} inches for US men and {f1(F["waist_in"]["mean"])} inches for women aged 20 and over '
     f'({ext(U["fast"], "CDC")}). The middle half of men measure {WP["men"][0]} to {WP["men"][1]} inches and of women '
     f'{WP["women"][0]} to {WP["women"][1]} inches (our calculation).'),
    ('What is the average weight by age?',
     f'US men weigh {f1(M["age"]["20–29"]["wt"]["mean"])} lb on average in their 20s, {f1(AGE_LO["men"])} to '
     f'{f1(AGE_HI["men"])} lb from 30 to 59, and {f1(M["age"]["80+"]["wt"]["mean"])} lb at 80 and over; women weigh '
     f'{f1(F["age"]["20–29"]["wt"]["mean"])} lb in their 20s, {f1(AGE_LO["women"])} to {f1(AGE_HI["women"])} lb from 30 '
     f'to 59, and {f1(F["age"]["80+"]["wt"]["mean"])} lb at 80 and over ({ext(U["s50"], "NCHS")}). '
     '<a href="#age">The age table</a> has every decade.'),
    ('Why do some sites say the average man weighs 199.8 lb?',
     f'That is CDC’s average for 2015–2018 (and {f1(S46[1])} lb for women; {ext(U["s46"], "NCHS")}). CDC’s newest '
     f'measurements, from August 2021 to August 2023, give {f1(M["wt_lb"]["mean"])} lb for men and {f1(F["wt_lb"]["mean"])} '
     f'lb for women, the figures on its {ext(U["fast"], "FastStats page")}.'),
]
assert f1(S46[0]) == '199.8'
CHEV = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')
def plain(fragment): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()
faq_html = ''.join(f'<div class="faq-item"><button class="faq-question">{esc(q)}{CHEV}</button><div class="faq-answer"><p>{a}</p></div></div>'
                   for q, a in FAQ)

# ---------------------------------------------------------------- page sections
H1 = 'Average Weight for Men and Women by Height and Age'
head = (
    f'<div class="page-head"><h1>{H1}</h1>'
    '<p class="byline">Written by <a href="/about/#author-bio">Marko Visic, MPharm</a> · Not medical advice</p>'
    '<p class="intro-text">What does the average American man weigh? What about a woman who is 5′4″, or a man who is 5′9″? '
    'And is the average a healthy weight?</p>'
    f'<p class="intro-text">The average US man weighs {f1(M["wt_lb"]["mean"])} lb and the average woman '
    f'{f1(F["wt_lb"]["mean"])} lb, measured by CDC in 2021–2023. At every height with enough people measured, the average '
    'woman and the average man are above CDC’s healthy weight range for that height (our calculation).</p>'
    '<p class="intro-text">Below: a tool that shows where your weight falls, <a href="#women">the average at every '
    'height</a> for women and men, the averages by age, height, BMI and waist size, and how average weight has changed '
    'since 1960.</p></div>')

takeaways = (
    '<div class="key-takeaways"><div class="key-takeaways-title">Key takeaways</div>'
    f'<p class="answer"><strong>The average US man weighs {f1(M["wt_lb"]["mean"])} lb ({kg(M["wt_lb"]["mean"])} kg) and the '
    f'average woman {f1(F["wt_lb"]["mean"])} lb ({kg(F["wt_lb"]["mean"])} kg)</strong>: adults 20 and over, measured by CDC in '
    f'August 2021–August 2023. At 5′4″ the average woman weighs {f1(A54["wt"]["mean"])} lb; at 5′9″ the average man weighs '
    f'{f1(A59["wt"]["mean"])} lb (our calculation).</p><ul>'
    f'<li><strong>The average is above the healthy range at every height measured</strong> (women {ft(min(HT["women"]))}–'
    f'{ft(max(HT["women"]))}, men {ft(min(HT["men"]))}–{ft(max(HT["men"]))}), and '
    f'{whole(B25["women"][0])}% to {whole(B25["women"][1])}% of women and {whole(B25["men"][0])}% to '
    f'{whole(B25["men"][1])}% of men of each height have a BMI of 25 or more.</li>'
    f'<li><strong>Adults in their 30s weigh more than adults in their 20s</strong>: {f1(UP_F)} lb more for women and '
    f'{f1(UP_M)} lb more for men. From 60 on, each older age group of women weighs less than the one before, and men 80 '
    f'and over weigh {f1(DOWN_M80)} lb less than men in their 70s.</li>'
    f'<li>The average man is <strong>{f1(M["ht_in"]["mean"])} inches</strong> tall and the average woman '
    f'<strong>{f1(F["ht_in"]["mean"])} inches</strong>; their average BMI is {f1(M["BMXBMI"]["mean"])} and '
    f'{f1(F["BMXBMI"]["mean"])}, and their average waist {f1(M["waist_in"]["mean"])} and {f1(F["waist_in"]["mean"])} '
    'inches (CDC).</li>'
    f'<li><strong>Since 1960–1962</strong>, the average weight of men aged 20 to 74 has risen {f1(GAIN["men"])} lb and of '
    f'women {f1(GAIN["women"])} lb (CDC; our calculation for 2021–2023).</li>'
    '</ul></div>'
    '<div class="disclaimer-box"><p><strong>Medical disclaimer:</strong> This page describes populations, not individuals. '
    'BMI is a screening measure, not a diagnosis. Ask a healthcare professional for medical advice.</p></div>')

hero_fig = (f'<figure class="figure">{svg_hero}<figcaption>Each dot is the average weight of US women or men measured at '
            'that height (to the nearest inch); the green band is a healthy weight for each height. At every height shown, '
            'the average is above the band.</figcaption></figure>')

CHIPS = (('compare', 'Compare'), ('women', 'Women'), ('men', 'Men'), ('age', 'By age'), ('bmi-waist', 'BMI and waist'),
         ('since-1960', 'Since 1960'), ('faq', 'FAQ'), ('sources', 'Sources'))
toc = ('<nav class="toc-inline" aria-label="On this page"><span class="toc-inline-title">On this page</span>'
       + ''.join(f'<a href="#{a}">{t}</a>' for a, t in CHIPS) + '</nav>')

sec_compare = (
    '<section id="compare" class="content-section flow"><h2>How does your weight compare?</h2>'
    '<p>Enter your height, and your weight if you like. The tool compares it with US women or men measured at your '
    'height or an inch either side in CDC’s survey, and shows the healthy range for your height.</p></section>'
    '<div class="calculator-card awt" id="awt"><div class="calc-panel active">'
    '<div class="unit-toggle" role="group" aria-label="Sex"><button type="button" class="unit-btn active" data-sex="f" '
    'aria-pressed="true">Woman</button><button type="button" class="unit-btn" data-sex="m" aria-pressed="false">Man</button></div>'
    '<div class="unit-toggle" role="group" aria-label="Units"><button type="button" class="unit-btn active" data-units="us" '
    'aria-pressed="true">ft, in, lb</button><button type="button" class="unit-btn" data-units="metric" aria-pressed="false">'
    'cm, kg</button></div>'
    '<div class="form-grid">'
    '<div class="form-row form-row--pair" id="awt-us"><div class="form-group"><label class="form-label" for="awt-ft">Height (ft)</label>'
    '<input type="number" id="awt-ft" class="form-input" inputmode="numeric" min="4" max="7" step="1" value="5"></div>'
    '<div class="form-group"><label class="form-label" for="awt-in">Height (in)</label><input type="number" id="awt-in" '
    'class="form-input" inputmode="decimal" min="0" max="11.9" step="0.1" value="4"></div></div>'
    '<div class="form-row" id="awt-metric" hidden><div class="form-group"><label class="form-label" for="awt-cm">Height (cm)</label>'
    '<input type="number" id="awt-cm" class="form-input" inputmode="decimal" min="122" max="229" step="0.1" value="163"></div></div>'
    '<div class="form-row form-row--pair"><div class="form-group"><label class="form-label" for="awt-w" id="awt-w-label">'
    'Weight (lb)</label><input type="number" id="awt-w" class="form-input" inputmode="decimal" min="23" max="700" step="0.1" '
    'placeholder="Optional"></div><div class="form-group"><label class="form-label" for="awt-age">Age (years)</label>'
    '<select id="awt-age" class="form-select"><option value="">Any age</option>'
    + ''.join(f'<option value="{g}">{g}</option>' for g in AGES) + '</select></div></div></div>'
    '<button type="button" class="calculate-btn" id="awt-go">Compare my weight</button>'
    '<div class="results-section" id="awt-out" aria-live="polite"></div></div></div>'
    '<noscript><p>The tool needs JavaScript. <a href="#women">The tables below</a> give the average and the middle half at '
    'every height.</p></noscript>'
    f'<script>window.AWT={json.dumps(TOOL, separators=(",", ":"), ensure_ascii=False)};</script><script>{TOOL_JS}</script>')
# The tool card sits after its section, not inside it, so no card nests in a card (DESIGN.md "Cards inside a section").

def height_table(s, d):
    word = s; cap = 'women' if s == 'women' else 'men'
    rows = ''
    for h, v in sorted(HT[s].items()):
        lo, hi = hb(h); n = v['wt']['n']
        rows += (f'<tr id="{word}-{h // 12}-{h % 12}"><th scope="row">{ft(h)}{"†" if n < 60 else ""}'
                 f'<span class="th-sub">{dcm(h)} cm</span></th><td class="num">{f1(v["wt"]["mean"])}'
                 f'<span class="cell-kg">{kg(v["wt"]["mean"])} kg</span></td><td class="num">{whole(v["q"][0])}–'
                 f'{whole(v["q"][2])}</td><td class="num">{lo}–{hi}</td><td class="num">{whole(v["bmi25_plus"]["pct"])}%</td></tr>')
    return ('<div class="table-responsive"><table class="data-table data-table--fit"><caption>Average weight of US '
            f'{cap} by height</caption><thead><tr><th scope="col">Height</th><th scope="col" class="num">Average'
            '<span class="th-sub">lb</span></th><th scope="col" class="num">Middle half<span class="th-sub">lb</span></th>'
            '<th scope="col" class="num">Healthy<span class="th-sub">lb</span></th><th scope="col" class="num">BMI 25+</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>')

def height_note(s):
    lo, hi = NMIN[s]; word = s
    first, last = min(HT[s]), max(HT[s])
    return (f'<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023: {word} aged 20 and over'
            f'{", not pregnant," if s == "women" else ""} by measured height rounded to the nearest inch ({lo} to {hi} '
            f'{word} per height; survey-weighted). Middle half: the 25th to 75th percentile. Healthy: whole pounds with a BMI '
            f'of 18.5 to 24.9 ({ext(U["cdc_cat"], "CDC categories")}). BMI 25+: the share with a BMI of 25 or more. '
            f'† Fewer than 60 {word} measured, a rough guide. Heights under {ft(first)} and over {ft(last)}: fewer than 30 '
            'measured.</p>')

W_RANGE = (HT['women'][57]['wt']['mean'], HT['women'][69]['wt']['mean'])
sec_women = (
    '<section id="women" class="content-section flow"><h2>Average weight for women by height</h2>'
    f'<p>At 5′4″, US women weigh <strong>{f1(A54["wt"]["mean"])} lb</strong> on average; the middle half weigh '
    f'{cellq("women", 64)[0]} to {cellq("women", 64)[1]} lb, and a healthy weight is {hb(64)[0]} to {hb(64)[1]} lb. The '
    'average climbs with height, but not smoothly: each height is a separate sample of women, so a taller row can show a '
    'lower average.</p>' + height_table('women', F) + height_note('women') + '</section>')
sec_men = (
    '<section id="men" class="content-section flow"><h2>Average weight for men by height</h2>'
    f'<p>At 5′9″, US men weigh <strong>{f1(A59["wt"]["mean"])} lb</strong> on average; the middle half weigh '
    f'{cellq("men", 69)[0]} to {cellq("men", 69)[1]} lb, and a healthy weight is {hb(69)[0]} to {hb(69)[1]} lb. At 6′0″ the '
    f'average is {f1(HT["men"][72]["wt"]["mean"])} lb, and a healthy weight tops out at {hb(72)[1]} lb.</p>'
    + height_table('men', M) + height_note('men') + '</section>')

age_rows = ''.join(f'<tr><th scope="row">{g}</th><td class="num">{f1(F["age"][g]["wt"]["mean"])}</td>'
                   f'<td class="num">{f1(M["age"][g]["wt"]["mean"])}</td></tr>' for g in AGES)
age_rows += (f'<tr><th scope="row">All 20+</th><td class="num">{f1(F["wt_lb"]["mean"])}</td>'
             f'<td class="num">{f1(M["wt_lb"]["mean"])}</td></tr>')
sec_age = (
    '<section id="age" class="content-section flow"><h2>Average weight by age</h2>'
    f'<p>Women in their 30s weigh <strong>{f1(UP_F)} lb more</strong> on average than women in their 20s, and men '
    f'{f1(UP_M)} lb more. From 30 to 59 the averages ({f1(AGE_LO["women"])} to {f1(AGE_HI["women"])} lb for women, '
    f'{f1(AGE_LO["men"])} to {f1(AGE_HI["men"])} lb for men) are not statistically different: the 95% confidence interval '
    'of the gap between any two of those age groups includes zero. From 60 on, each '
    f'older age group of women weighs less than the one before, and men 80 and over weigh {f1(DOWN_M80)} lb less than men '
    'in their 70s. These are different people measured in the same years, not the same people followed as they aged.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Average weight of US adults by age (lb)</caption>'
    '<thead><tr><th scope="col">Age</th><th scope="col" class="num">Women</th><th scope="col" class="num">Men</th></tr></thead>'
    f'<tbody>{age_rows}</tbody></table></div>'
    f'<p class="source-note">CDC NHANES August 2021–August 2023, adults 20 and over, women not pregnant; the same values as '
    f'NCHS Series 3 No. 50, Table 4 ({ext(U["s50"], "NCHS")}). The changes stated above have 95% confidence intervals that '
    'exclude zero (our calculation); the others don’t.</p></section>')

bw_rows = ''.join(f'<tr><th scope="row">{g}</th><td class="num">{f1(F["age"][g]["bmi"]["mean"])}</td>'
                  f'<td class="num">{f1(M["age"][g]["bmi"]["mean"])}</td><td class="num">{f1(F["age"][g]["waist"]["mean"])}</td>'
                  f'<td class="num">{f1(M["age"][g]["waist"]["mean"])}</td></tr>' for g in AGES)
sec_bw = (
    '<section id="bmi-waist" class="content-section flow"><h2>Average height, BMI and waist size</h2>'
    f'<p>The average US man is <strong>{f1(M["ht_in"]["mean"])} inches</strong> tall ({dcm(M["ht_in"]["mean"])} cm, about '
    f'5′9″) and the average woman <strong>{f1(F["ht_in"]["mean"])} inches</strong> ({dcm(F["ht_in"]["mean"])} cm, about '
    f'5′3.5″). Their average BMI is {f1(M["BMXBMI"]["mean"])} and {f1(F["BMXBMI"]["mean"])}: in CDC’s overweight range for '
    'men, and at the line between overweight and obesity for women. A healthy BMI is 18.5 to 24.9 for adults of any age or '
    f'sex ({ext(U["cdc_cat"], "CDC")}). Half of men weigh {f1(M["wt_pct"]["p50"])} lb or more and half of women '
    f'{f1(F["wt_pct"]["p50"])} lb or more; the medians sit below the averages because the heaviest people pull the averages '
    f'up ({ext(U["s50"], "NCHS")}).</p>'
    f'<p>The average waist is <strong>{f1(M["waist_in"]["mean"])} inches</strong> for men and '
    f'<strong>{f1(F["waist_in"]["mean"])} inches</strong> for women ({ext(U["fast"], "CDC")}); the middle half measure '
    f'{WP["men"][0]} to {WP["men"][1]} and {WP["women"][0]} to {WP["women"][1]} inches. US guidelines treat a waist over '
    f'102 cm (40 in) in men and over 88 cm (35 in) in women as a sign of higher risk ({ext(U["nhlbi_tg"], "NHLBI")}): '
    f'{pc(OVER["men"])} of men and {pc(OVER["women"])} of women are over those lines (our calculation, in centimeters). The '
    '<a href="/blog/waist-to-height-ratio/">waist-to-height ratio</a> guide shows how to measure.</p>'
    '<div class="table-responsive"><table class="data-table data-table--fit"><caption>Average BMI and waist size (inches) '
    'of US adults by age</caption><thead><tr><th scope="col">Age</th><th scope="col" class="num">BMI<span class="th-sub">'
    'women</span></th><th scope="col" class="num">BMI<span class="th-sub">men</span></th><th scope="col" class="num">'
    'Waist<span class="th-sub">women</span></th><th scope="col" class="num">Waist<span class="th-sub">men</span></th></tr>'
    f'</thead><tbody>{bw_rows}</tbody></table></div>'
    '<p class="source-note">Our calculation from CDC NHANES August 2021–August 2023, adults 20 and over, women not pregnant '
    '(survey-weighted). For how many adults have obesity, see <a href="/us-obesity-statistics/">US obesity statistics</a>.</p>'
    '</section>')

sec_time = (
    '<section id="since-1960" class="content-section flow"><h2>Average weight since 1960</h2>'
    f'<p>National health surveys have weighed Americans since 1960–1962. Men aged 20 to 74 averaged '
    f'{f1(AD347["men"][0])} lb in 1960–1962 and '
    f'{f1(AD347["men"][1])} lb in 1999–2002; women of the same ages {f1(AD347["women"][0])} lb and {f1(AD347["women"][1])} lb '
    f'({ext(U["ad347"], "CDC, Advance Data No. 347")}). In 2021–2023 men of those ages averaged '
    f'<strong>{f1(NOW74["men"])} lb</strong> and women <strong>{f1(NOW74["women"])} lb</strong> (our calculation), '
    f'{f1(GAIN["men"])} lb and {f1(GAIN["women"])} lb more than in 1960–1962.</p>'
    '<div class="table-responsive"><table class="data-table"><caption>Average weight of US adults aged 20 to 74 (lb)</caption>'
    '<thead><tr><th scope="col">Years</th><th scope="col" class="num">Women</th><th scope="col" class="num">Men</th></tr></thead><tbody>'
    f'<tr><th scope="row">1960–1962</th><td class="num">{f1(AD347["women"][0])}</td><td class="num">{f1(AD347["men"][0])}</td></tr>'
    f'<tr><th scope="row">1999–2002</th><td class="num">{f1(AD347["women"][1])}</td><td class="num">{f1(AD347["men"][1])}</td></tr>'
    f'<tr><th scope="row">2021–2023</th><td class="num">{f1(NOW74["women"])}</td><td class="num">{f1(NOW74["men"])}</td></tr>'
    '</tbody></table></div>'
    f'<p class="source-note">1960–1962 and 1999–2002: {ext(U["ad347"], "Ogden et al., CDC Advance Data No. 347 (2004)")}, '
    'Table 6. 2021–2023: our calculation from CDC NHANES for the same ages, women not pregnant.</p>'
    f'<p><strong>Why some sites say 199.8 lb.</strong> That is CDC’s average for men 20 and over in 2015–2018, with '
    f'{f1(S46[1])} lb for women ({ext(U["s46"], "NCHS Series 3 No. 46")}). CDC’s newest measurements, from August 2021 to '
    f'August 2023, give {f1(M["wt_lb"]["mean"])} lb and {f1(F["wt_lb"]["mean"])} lb, the figures on its '
    f'{ext(U["fast"], "FastStats page")}. Both are averages over every height; for one height, use '
    '<a href="#women">the tables above</a>.</p></section>')

sec_faq = (f'<section id="faq" class="content-section"><h2>Frequently asked questions</h2><div class="faq-list flat">{faq_html}'
           '</div></section>')

SOURCES = [
    f'CDC {ext(U["bmx"], "NHANES August 2021–August 2023")} demographics and body measures files (DEMO_L, BMX_L): our '
    f'calculation of the average, percentiles and the share with a BMI of 25 or more at each height, of BMI and waist by age, '
    f'and of the averages for ages 20 to 74 ({M["wt_lb"]["n"]:,} men and {F["wt_lb"]["n"]:,} women aged 20 and over).',
    f'Fryar CD, et al. {ext(U["s50"], "Anthropometric reference data for children and adults: United States, August 2021–August 2023")}. '
    'Vital and Health Statistics, Series 3, No. 50: Tables 4 (weight), 8 (height), 10 (BMI) and 12 (waist).',
    f'CDC. {ext(U["fast"], "FastStats: Body Measurements")}: average height, weight and waist for adults 20 and over.',
    f'Fryar CD, et al. {ext(U["s46"], "Anthropometric reference data for children and adults: United States, 2015–2018")}. '
    'Vital and Health Statistics, Series 3, No. 46 (January 2021).',
    f'Ogden CL, et al. {ext(U["ad347"], "Mean body weight, height, and body mass index, United States 1960–2002")}. '
    'Advance Data No. 347 (October 2004).',
    f'CDC. {ext(U["cdc_cat"], "Adult BMI Categories")}: the adult cut-offs, the same for every adult.',
    f'NHLBI. {ext(U["nhlbi_tg"], "Clinical Guidelines on the Identification, Evaluation, and Treatment of Overweight and Obesity in Adults")}, '
    'treatment guidelines chapter (NIH, 1998): waist cut-offs for women and men.',
]
sec_src = (
    '<section id="sources" class="content-section flow"><h2>Sources and method</h2>'
    '<p>Written by <a href="/about/#author-bio">Marko Visic, MPharm</a>. “Our calculation” means we computed the figure from '
    'CDC’s public survey files with the method below.</p>'
    '<ul class="source-list">' + ''.join(f'<li>{s}</li>' for s in SOURCES) + '</ul>'
    '<p class="source-note"><strong>Method.</strong> Adults aged 20 and over in NHANES August 2021–August 2023, weighed and '
    'measured by CDC’s staff, weighted with the exam weights; pregnant women are left out of weight, BMI and waist, as NCHS '
    'leaves them out. Weights are converted to pounds with NCHS’s factor (2.2046 lb per kg), and percentiles read the '
    'weighted distribution over the measured values. With these rules our figures equal every mean and percentile in NCHS '
    'Series 3 No. 50: all 160 weight means and percentiles in Table 4, the adult height and waist means and percentiles '
    'in Tables 8 and 12, and the adult BMI means and medians in Table 10 (204 values). Heights for the tables are measured '
    'heights rounded to the nearest '
    'inch; a height is shown when 30 or more people were measured at it. 95% confidence intervals use Taylor linearization '
    'over the survey’s 15 strata, and the page states a change between age groups only when its interval excludes zero. '
    'The tool compares a weight with the people measured at the height entered or an inch either side, heights rounded '
    'to the nearest inch.</p>'
    f'<p class="source-note"><strong>Download:</strong> <a href="{CSV_PATH}">average weight by sex, height and age (CSV)</a>. '
    'Free to reuse with a link to this page (CC BY 4.0).</p>'
    '</section>')

sec_rel = (
    '<section class="content-section"><h2>Related calculators and guides</h2><div class="related-cols">'
    '<div><h3>Calculators</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/', 'BMI calculator'), ('/women-bmi-calculator/', 'BMI calculator for women'),
        ('/men-bmi-calculator/', 'BMI calculator for men'), ('/ideal-weight/', 'Ideal weight calculator'),
        ('/body-fat-calculator/', 'Body fat calculator')))
    + '</ul></div><div><h3>Guides and data</h3><ul>'
    + ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in (
        ('/blog/bmi-chart-women/', 'BMI chart for women'), ('/blog/bmi-chart-men/', 'BMI chart for men'),
        ('/bmi-chart/', 'BMI chart for adults'), ('/us-obesity-statistics/', 'US obesity statistics'),
        ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio'), ('/blog/healthy-bmi-range/', 'Healthy BMI range')))
    + '</ul></div></div></section>')

main = ('<main class="reading"><div class="container"> ' + ' '.join(
    [head, takeaways, hero_fig, toc, sec_compare, sec_women, sec_men, sec_age, sec_bw, sec_time, sec_faq, sec_src, sec_rel])
    + ' </div></main>')
assert 'style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', main)
assert all(f'id="{a}"' in main for a, _ in CHIPS) and '<article' not in main

# ---------------------------------------------------------------- head: title, meta, OG, JSON-LD
TITLE = 'Average Weight for Men and Women by Height and Age (CDC)'
DESC = ('The average US man weighs 199.0 lb and the average woman 171.8 lb (CDC, measured 2021–2023). See averages by '
        'height and age, and compare your weight.')
assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
assert f'{f1(M["wt_lb"]["mean"])} lb' in DESC and f'{f1(F["wt_lb"]["mean"])} lb' in DESC
OG_T = 'Average weight for men and women by height and age'
OG_D = ('What US adults weigh by height and age, measured by CDC in 2021–2023 (our calculation), against the healthy '
        'range for each height.')
OG_ALT = ('Chart: the average weight of US women (4′9″ to 5′9″) and men (5′2″ to 6′3″) at each height, above the band of '
          'healthy weights for each height.')
for s_ in (DESC, OG_T, OG_D, OG_ALT): assert '"' not in s_
PREF = SITE + '/assets/images/preferred/average-weight-'
IMG16, IMG43, IMG11 = PREF + '16x9.png', PREF + '4x3.png', PREF + '1x1.png'

def sub1(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl, s, count=1)
    assert n == 1, pattern
    return out

src = sub1(r'<title>[^<]*</title>', f'<title>{esc(TITLE)}</title>', src)
src = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', src)
src = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_T}">', src)
src = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_D}">', src)
src = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG16}">', src)
src = sub1(r'<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="675">', src)
src = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', src)
src = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG16}">', src)
assert 'twitter:title' not in src and 'twitter:description' not in src          # the A2 head had neither; add them
src = sub1(r'(<meta name="twitter:card" content="summary_large_image">)',
           f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{OG_T}">'
           f'<meta name="twitter:description" content="{OG_D}">', src)
n_style = len(re.findall(r'(?s)<style>.*?</style>', src)); assert n_style == 3, n_style   # the A2 page-level styles
src = re.sub(r'(?s)<style>.*?</style>', '', src)
assert src.count('<meta name="robots" content="max-image-preview:large">') == 1 and '<style' not in src

blocks = list(re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src))
assert len(blocks) == 1, len(blocks)                                    # the A2 page: one @graph block
old = json.loads(blocks[0].group(1))
types = [x['@type'] for x in old['@graph']]
assert types == ['Article', 'Dataset', 'BreadcrumbList', 'Organization', 'Person'], types
art_old = old['@graph'][0]; ds_old = old['@graph'][1]
assert art_old['datePublished'] == '2026-10-03' and ds_old['distribution'][0]['contentUrl'].endswith(CSV_PATH)
PERSON = {'@type': 'Person', '@id': SITE + '/about/#author-bio', 'name': 'Marko Visic', 'url': SITE + '/about/'}
ORG = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'CalculateMyBMI', 'url': SITE + '/'}
article = {'@context': 'https://schema.org', '@type': 'Article', 'headline': H1, 'description': DESC, 'url': URL,
           'datePublished': art_old['datePublished'], 'dateModified': '{TODAY}', 'inLanguage': 'en-US',
           'isPartOf': {'@type': 'WebSite', 'name': 'CalculateMyBMI', 'url': SITE + '/'}, 'author': PERSON, 'publisher': ORG,
           'image': [IMG11, IMG43, IMG16],
           'mainEntityOfPage': {'@type': 'WebPage', '@id': URL, 'url': URL,
                                'primaryImageOfPage': {'@type': 'ImageObject', 'url': IMG16, 'width': 1200, 'height': 675}},
           'citation': [U['bmx'], U['s50'], U['fast'], U['s46'], U['ad347'], U['cdc_cat']]}
dataset = {'@context': 'https://schema.org', '@type': 'Dataset', '@id': URL + '#dataset',
           'name': 'Average weight of US adults by sex, height and age, NHANES August 2021–August 2023',
           'description': ('Weighted mean, median and interquartile range of measured body weight for US adults 20 and over '
                           'by sex and height (nearest inch), with the mean BMI and the share with a BMI of 25 or more at '
                           'each height, plus mean weight, BMI and waist circumference by age group and for all adults, with '
                           'standard errors. Calculated by calculatemybmi.net from CDC NHANES public-use exam files; the '
                           'national weight means and percentiles equal NCHS Series 3 No. 50, Table 4.'),
           'url': URL, 'creator': ORG, 'license': 'https://creativecommons.org/licenses/by/4.0/', 'isAccessibleForFree': True,
           'isBasedOn': [U['bmx']], 'temporalCoverage': '2021-08/2023-08',
           'spatialCoverage': {'@type': 'Place', 'name': 'United States'}, 'dateModified': '{TODAY}',
           'variableMeasured': ['Mean body weight', 'Median body weight', 'Body weight interquartile range',
                                'Share with a BMI of 25 or more', 'Mean BMI', 'Mean waist circumference', 'Standard error'],
           'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': SITE + CSV_PATH}]}
crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': H1, 'item': URL}]}
faqld = {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]}
LD = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
             for x in (article, dataset, crumbs, faqld))
src = src[:blocks[0].start()] + LD + src[blocks[0].end():]
assert src.count('{TODAY}') == 2

# ---------------------------------------------------------------- body
i, j = src.index('<main'), src.index('</main>') + len('</main>')
src = src[:i] + main + src[j:]
open(PAGE, 'w', encoding='utf-8', newline='').write(src)

# ---------------------------------------------------------------- the CSV download (the A2 file's columns, plus the BMI
# 25+ share, mean BMI and mean waist with their SEs, as the Dataset JSON-LD describes; values as the page prints them)
rows = [['table', 'sex', 'group', 'mean_weight_lb', 'se_lb', 'median_lb', 'p25_lb', 'p75_lb', 'n', 'healthy_range_lb',
         'bmi25_plus_pct', 'mean_bmi', 'se_bmi', 'mean_waist_in', 'se_waist_in']]
def mse(e): return [f1(e['mean']), f'{e["se"]:.2f}']
for s, d, _ in SEXES:
    for h, v in sorted(HT[s].items()):
        lo, hi = hb(h)
        rows.append(['height', s, f'{h // 12}\'{h % 12}"', *mse(v['wt']), f1(v['q'][1]), f1(v['q'][0]), f1(v['q'][2]),
                     v['wt']['n'], f'{lo}-{hi}', f1(v['bmi25_plus']['pct']), *mse(v['bmi']), '', ''])
for s, d, _ in SEXES:
    for g in AGES:
        a = d['age'][g]
        rows.append(['age', s, g, *mse(a['wt']), '', '', '', a['wt']['n'], '', '', *mse(a['bmi']), *mse(a['waist'])])
    rows.append(['overall', s, '20+', *mse(d['wt_lb']), f1(d['wt_pct']['p50']), f1(d['wt_pct']['p25']),
                 f1(d['wt_pct']['p75']), d['wt_lb']['n'], '', '', *mse(d['BMXBMI']), *mse(d['waist_in'])])
with open(os.path.join(ROOT, CSV_PATH.lstrip('/')), 'w', encoding='utf-8', newline='') as fh:
    fh.write('"# Average body weight of US adults 20+ (pregnant women excluded), measured, NHANES August 2021-August 2023 '
             '(DEMO_L, BMX_L), weighted with MEC exam weights; lb = kg x 2.2046 (NCHS); percentiles from the weighted '
             'distribution over measured values (equal to NCHS Series 3 No. 50); waist in inches = cm / 2.54; SE by Taylor '
             'linearization. Calculated by calculatemybmi.net; CC BY 4.0. Heights rounded to nearest inch; cells with n<30 '
             'omitted."\r\n')
    csv.writer(fh, lineterminator='\r\n').writerows(rows)

words = len(plain(re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', ' ', re.sub(r'(?s)<table.*?</table>', ' ', main))).split())
print(f'average-weight/index.html written: {len(src):,} bytes, {words:,} words in <main> outside tables, {len(FAQ)} FAQ, '
      f'{len(TEXTS)} SVG labels checked; CSV {len(rows) - 1} rows')
