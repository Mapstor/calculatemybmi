#!/usr/bin/env python3
"""CMB-058 WHTR-CALC: a waist-to-height ratio calculator on /blog/waist-to-height-ratio/ (Marko, 2026-11-16: "do build
that calculator"; §5 P1: the title said "Calculator" and the page had none).
The tool sits under the intro, on the shared calculator parts, the way the body fat rank tool does (DESIGN.md "Body fat
rank tool and lookup tables (CMB-016)"): .calculator-card.whtr › .calc-panel › a US / Metric .unit-toggle › a
.form-row--trio (height ft, height in, waist in) or a .form-row--pair (height cm, waist cm) › the NICE measuring hint ›
.calculate-btn › results answer first: a .bmi-result-card tinted by NICE's class with the ratio in a neutral .bmi-value,
then .er-sections: what the ratio means (NICE NG246 1.9.14 / 1.10.10 wording; 1.9.5's advice line from 0.5), the waist
for each class at the height entered (.er-table, the user's row .er-active with an .er-you pill, half the height,
NICE 1.9.15), and the method and source line. The ratio is cut to two decimals, not rounded (the women's page rule,
CMB-017), so 0.50 always means a waist of at least half the height; heights and waists are read to 0.1.
Also: the H1, <title>, og/twitter titles, meta description and Article headline and description now name the
calculator (the page is D-28 free: no impressions, §0); a WebApplication JSON-LD node; the example table's Woman A
(28 in at 64 in was 0.4375, which the calculator shows as 0.43 and the table as 0.44) now 29 in, 0.45 both ways;
styles.css gets the tool sizes; DESIGN.md gets the pattern. dateModified and lastmod follow.
usage: python3 research/cmb-058/apply.py [--check]   Run order from main: registry.py, apply.py."""
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PG, SM, CSS, DS = 'blog/waist-to-height-ratio/index.html', 'sitemap.xml', 'assets/css/styles.css', 'DESIGN.md'
BASE = {PG: '55424d2eb652cdde3fe7ac7c7a7496f4aa643f1565ac0c2f934ecd0acfa8573a',
        SM: '3c6df32f041ea2ac8cf2735a0a14fff07b94c6b07387af01b3c69aae9d3efc5f',
        CSS: '2b80275d4ff949b22d539807c45214f884203dddbcf1576be3cac449a0e69c9d',
        DS: '4b46c42511c4aebf5d0895e31d4cd3d401ff627b2255c68f0aafb851b2c237e1'}
URL = 'https://calculatemybmi.net/blog/waist-to-height-ratio/'
NICE = 'https://www.nice.org.uk/guidance/ng246/chapter/Identifying-and-assessing-overweight-obesity-and-central-adiposity'
EXT = 'target="_blank" rel="noopener"'
NAME = 'Waist-to-Height Ratio Calculator and Healthy Ranges'
DESC = ('Work out your waist-to-height ratio in inches or centimeters and see where it falls on the healthy, increased '
        'and high ranges NICE uses.')
ART_DESC = ('A waist-to-height ratio calculator with the ranges NICE uses for men and women, how to measure, and how the '
            'ratio compared with BMI in pooled studies.')

TOOL = (
    '<div class="calculator-card whtr" id="whtr"><div class="calc-panel active">'
    '<div class="unit-toggle" role="group" aria-label="Units"><button type="button" class="unit-btn active" '
    'data-units="us" aria-pressed="true">US</button><button type="button" class="unit-btn" data-units="metric" '
    'aria-pressed="false">Metric</button></div>'
    '<div class="form-grid">'
    '<div class="form-row form-row--trio" id="whtr-us">'
    '<div class="form-group"><label class="form-label" for="whtr-ft">Height (ft)</label><input type="number" '
    'id="whtr-ft" class="form-input" inputmode="numeric" min="3" max="7" step="1" value="5"></div>'
    '<div class="form-group"><label class="form-label" for="whtr-in">Height (in)</label><input type="number" '
    'id="whtr-in" class="form-input" inputmode="decimal" min="0" max="11.9" step="0.1" value="5"></div>'
    '<div class="form-group"><label class="form-label" for="whtr-win">Waist (in)</label><input type="number" '
    'id="whtr-win" class="form-input" inputmode="decimal" min="15" max="80" step="0.1" value="30"></div></div>'
    '<div class="form-row form-row--pair" id="whtr-metric" hidden>'
    '<div class="form-group"><label class="form-label" for="whtr-cm">Height (cm)</label><input type="number" '
    'id="whtr-cm" class="form-input" inputmode="decimal" min="90" max="230" step="0.1" value="165.1"></div>'
    '<div class="form-group"><label class="form-label" for="whtr-wcm">Waist (cm)</label><input type="number" '
    'id="whtr-wcm" class="form-input" inputmode="decimal" min="38" max="203" step="0.1" value="76.2"></div></div>'
    '</div>'
    '<p class="form-hint">Measure your waist midway between the bottom of your ribs and the top of your hips, just '
    f'above the belly button, after breathing out naturally (<a href="{NICE}" {EXT}>NICE</a>).</p>'
    '<button type="button" class="calculate-btn" id="whtr-go">Calculate my ratio</button>'
    '<div class="results-section" id="whtr-out" aria-live="polite"></div></div></div>'
    '<noscript><p>The calculator needs JavaScript. To work the ratio out by hand, divide your waist by your height in '
    'the same unit, as in the <a href="#how-to-calculate">steps below</a>.</p></noscript>'
)

SCRIPT = r"""<script>(function(){var $=function(i){return document.getElementById(i);};
var out=$('whtr-out'),btns=document.querySelectorAll('#whtr .unit-toggle .unit-btn'),units='us',last=null;
var NICE='__NICE__',CDC='https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html',EXT=' target="_blank" rel="noopener"';
var F={us:['whtr-ft','whtr-in','whtr-win'],metric:['whtr-cm','whtr-wcm']};
var C=[{name:'No NICE class',tint:'',dot:'',risk:'',range:'under 0.4',cell:'under 0.4',short:'No class'},
 {name:'Healthy central adiposity',tint:' normal',dot:'normal',risk:'no increased health risks',range:'0.4 to 0.49',cell:'<span class="nw">0.4–0.49</span>',short:'Healthy'},
 {name:'Increased central adiposity',tint:' overweight',dot:'overweight',risk:'increased health risks',range:'0.5 to 0.59',cell:'<span class="nw">0.5–0.59</span>',short:'Increased'},
 {name:'High central adiposity',tint:' obese',dot:'obese',risk:'further increased health risks',range:'0.6 or more',cell:'0.6 or more',short:'High'}];
function lnk(u,t){return '<a href="'+u+'"'+EXT+'>'+t+'</a>';}
function val(id){var s=$(id).value.trim();return s===''?NaN:Number(s);}
function tx(t){return t%10===0?String(t/10):(t/10).toFixed(1);}
function f1(t){return (t/10).toFixed(1);}
function half(t){var h=t/20;return String(Math.round(h*100)/100);}
function read(){var ht,wt,u;
 if(units==='us'){var ft=val('whtr-ft'),inch=val('whtr-in'),w=val('whtr-win');if(isNaN(inch))inch=0;
  if(!(ft>=0)||!(inch>=0&&inch<12)||!(w>0))return null;ht=Math.round(ft*120+inch*10);wt=Math.round(w*10);u='in';
  if(ht<360||ht>900||wt<150||wt>800)return null;}
 else{var cm=val('whtr-cm'),wc=val('whtr-wcm');if(!(cm>0)||!(wc>0))return null;ht=Math.round(cm*10);wt=Math.round(wc*10);u='cm';
  if(ht<900||ht>2300||wt<380||wt>2030)return null;}
 return {ht:ht,wt:wt,u:u};}
function show(){var r=read(),h;
 if(!r){out.innerHTML='<p class="er-note">'+(units==='us'?'Enter a height from 3 ft to 7 ft 6 in and a waist from 15 to 80 inches.':'Enter a height from 90 to 230 cm and a waist from 38 to 203 cm.')+'</p>';out.classList.add('visible');return;}
 if(r.wt>=r.ht){out.innerHTML='<p class="er-note">The waist is as long as the height or longer. Check both numbers and the units.</p>';out.classList.add('visible');return;}
 var p=Math.floor(r.wt*100/r.ht),rs=(p/100).toFixed(2),c=p<40?0:p<50?1:p<60?2:3,u=r.u,
  b4=Math.floor((r.ht*4+9)/10),b5=Math.floor((r.ht*5+9)/10),b6=Math.floor((r.ht*6+9)/10),k=C[c];
 h='<div class="bmi-result-card'+k.tint+'"><div class="bmi-value">'+rs+'</div><div class="bmi-category">'+k.name+'</div><div class="bmi-range">Waist '+tx(r.wt)+' '+u+' ÷ height '+tx(r.ht)+' '+u+'</div></div>';
 h+='<div class="er"><section class="er-section"><h2>What your ratio means</h2>';
 if(c)h+='<p class="er-note"><span class="cat-dot '+k.dot+'"></span>Your waist is '+rs+' of your height. NICE classes '+k.range+' as '+k.name.toLowerCase()+', indicating '+k.risk+' ('+lnk(NICE,'NICE NG246')+').</p>';
 else h+='<p class="er-note">Your waist is '+rs+' of your height. NICE’s classes start at 0.4 (0.4 to 0.49 is healthy central adiposity), so '+rs+' has no NICE class ('+lnk(NICE,'NICE NG246')+'). For adults, BMI shows whether a weight is low: under 18.5 is underweight ('+lnk(CDC,'CDC')+'; <a href="/">BMI calculator</a>).</p>';
 if(c>=2)h+='<p class="er-note">NICE encourages adults with a BMI under 35 to seek advice and further checks, such as a cardiometabolic risk factor assessment, from a healthcare professional when the ratio shows an increased health risk.</p>';
 h+='<p class="er-note">The classes are the same for both sexes and all ethnicities. NICE uses them for adults with a BMI under 35 and for children and young people aged 5 and over.</p></section>';
 var rows=[[0,'under '+f1(b4)+' '+u],[1,f1(b4)+'–'+f1(b5-1)+' '+u],[2,f1(b5)+'–'+f1(b6-1)+' '+u],[3,f1(b6)+' '+u+' or more']];
 h+='<section class="er-section"><h2>Waist sizes for a height of '+tx(r.ht)+' '+u+'</h2><table class="er-table"><thead><tr><th scope="col">Ratio</th><th scope="col">NICE class</th><th scope="col" class="er-num">Waist</th></tr></thead><tbody>';
 rows.forEach(function(x){var on=x[0]===c,q=C[x[0]];h+='<tr'+(on?' class="er-active"':'')+'><td>'+q.cell+'</td><td><span class="nw">'+(q.dot?'<span class="cat-dot '+q.dot+'"></span>':'')+q.short+'</span>'+(on?'<span class="er-you">You</span>':'')+'</td><td class="er-num">'+x[1]+'</td></tr>';});
 h+='</tbody></table><p class="er-note">Half your height is '+half(r.ht)+' '+u+'. NICE’s advice is to keep your waist to less than half your height, a ratio under 0.5.</p></section>';
 h+='<section class="er-section"><p class="er-note">The ratio is your waist divided by your height in the same unit, cut to two decimals, not rounded, so 0.50 always means a waist of at least half your height. Waist sizes are to the nearest 0.1 '+u+'. Classes: '+lnk(NICE,'NICE NG246')+', recommendations 1.9.14 (adults) and 1.10.10 (children and young people). Published classes applied to the numbers you entered, not a diagnosis.</p></section></div>';
 out.innerHTML=h;out.classList.add('visible');}
function snap(u){return F[u].map(function(id){return $(id).value;});}
function same(u,v){var s=snap(u);for(var i=0;i<s.length;i++)if(s[i]!==v[i])return false;return true;}
function r1(x){return (Math.round(x*10)/10).toFixed(1);}
function conv(from,to){if(from==='us'){var ft=val('whtr-ft'),inch=val('whtr-in'),w=val('whtr-win');if(isNaN(inch))inch=0;
  $('whtr-cm').value=ft>=0?r1((ft*12+inch)*2.54):'';$('whtr-wcm').value=w>0?r1(w*2.54):'';}
 else{var cm=val('whtr-cm'),wc=val('whtr-wcm'),t=Math.round(cm/2.54*10),f=Math.floor(t/120),i=t-f*120;
  if(cm>0){$('whtr-ft').value=String(f);$('whtr-in').value=tx(i);}else{$('whtr-ft').value='';$('whtr-in').value='';}
  $('whtr-win').value=wc>0?r1(wc/2.54):'';}}
function setUnits(u){if(u===units)return;var from=units;
 if(!(last&&last.to===from&&same(from,last.vals)))conv(from,u);
 last={to:u,vals:snap(u)};units=u;
 for(var j=0;j<btns.length;j++){var on=btns[j].getAttribute('data-units')===u;btns[j].classList.toggle('active',on);btns[j].setAttribute('aria-pressed',on?'true':'false');}
 $('whtr-us').hidden=u!=='us';$('whtr-metric').hidden=u!=='metric';
 if(out.classList.contains('visible'))show();}
for(var i=0;i<btns.length;i++)btns[i].addEventListener('click',function(){setUnits(this.getAttribute('data-units'));});
$('whtr-go').addEventListener('click',show);
F.us.concat(F.metric).forEach(function(id){$(id).addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();show();}});});
})();</script>""".replace('__NICE__', NICE)

APP = {
    '@context': 'https://schema.org', '@type': 'WebApplication', '@id': URL + '#calculator',
    'name': 'Waist-to-Height Ratio Calculator',
    'description': ('Works out the waist-to-height ratio from a waist and a height in inches or centimeters, places it '
                    'on NICE’s waist-to-height ratio classes (NICE NG246), and gives the waist for each class at the '
                    'height entered.'),
    'url': URL, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any',
    'browserRequirements': 'Requires JavaScript', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
    'featureList': ['Waist-to-height ratio from US or metric units',
                    'NICE NG246 class: healthy, increased or high central adiposity',
                    'The waist for each class at your height',
                    'Half your height, the waist NICE advises staying under'],
    'author': {'@type': 'Person', '@id': 'https://calculatemybmi.net/about/#author-bio', 'name': 'Marko Visic',
               'url': 'https://calculatemybmi.net/about/'},
}

EDITS = [
    ('<title>Waist-to-Height Ratio Calculator & Guide: A Better Alternative to BMI | CalculateMyBMI</title>',
     f'<title>{NAME} | CalculateMyBMI</title>'),
    ('<meta name="description" content="How to work out your waist-to-height ratio (WHtR), the healthy and increased-risk '
     'ranges NICE uses, and what the research says about it compared with BMI.">',
     f'<meta name="description" content="{DESC}">'),
    ('<meta property="og:title" content="Waist-to-Height Ratio: A Better Alternative to BMI">',
     f'<meta property="og:title" content="{NAME}">'),
    ('<meta name="twitter:title" content="Waist-to-Height Ratio: A Better Alternative to BMI">',
     f'<meta name="twitter:title" content="{NAME}">'),
    ('"headline": "Waist-to-Height Ratio Calculator & Guide: A Better Alternative to BMI"', f'"headline": "{NAME}"'),
    ('"description": "How to work out your waist-to-height ratio (WHtR), the ranges NICE uses for men and women, and how '
     'it compared with BMI in pooled studies."', f'"description": "{ART_DESC}"'),
    ('"dateModified": "2026-11-16", "mainEntityOfPage"', f'"dateModified": "{TODAY}", "mainEntityOfPage"'),
    ('} } </script> <!-- FAQ Schema -->',
     '} } </script> <script type="application/ld+json">' + json.dumps(APP, ensure_ascii=False) + '</script> <!-- FAQ Schema -->'),
    ('<h1>Waist-to-Height Ratio: The Simple Metric That Predicts Health Better Than BMI</h1>', f'<h1>{NAME}</h1>'),
    ('where fat sits.</p> <!-- Key Takeaways Box -->', 'where fat sits.</p> ' + TOOL + ' ' + SCRIPT + ' <!-- Key Takeaways Box -->'),
    ('<tr><td>Woman A</td><td>64 in (5\'4")</td><td>28 in</td><td>28 ÷ 64</td><td>0.44</td>',
     '<tr><td>Woman A</td><td>64 in (5\'4")</td><td>29 in</td><td>29 ÷ 64</td><td>0.45</td>'),
]

CSS_ADD = """
/* CMB-058 — /blog/waist-to-height-ratio/ (DESIGN.md "Waist-to-height ratio tool (CMB-058)"): the ratio and its class at
   the body fat tools' sizes, and the measuring hint a step below the fields, the line under the table clear of its last rule, a class's dot kept beside its name, and a ratio range on one line. The US / metric rows hide with the hidden
   attribute (.calc-panel [hidden], CMB-023). */
.whtr .bmi-value { font-size: 3rem; }
.whtr .bmi-category { font-size: 1.0625rem; line-height: 1.4; }
.whtr .form-hint { margin: 0.5rem 0 0; }
.whtr .er-table + .er-note { margin-top: 0.75rem; }
.whtr .nw { white-space: nowrap; }
"""

DS_OLD = '### Category badges\n'
DS_NEW = """### Waist-to-height ratio tool (CMB-058)
- `/blog/waist-to-height-ratio/` works out the ratio with the shared calculator parts and no page-level style, right under the intro: `.calculator-card.whtr` › `.calc-panel` › a US / Metric `.unit-toggle` › `.form-row.form-row--trio` (height ft, height in, waist in; two columns under 360 px) or `.form-row.form-row--pair` (height cm, waist cm) › a `.form-hint` with NICE's measuring point › `.calculate-btn`. The rows hide with the `hidden` attribute.
- Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by NICE's class (healthy `normal`, increased `overweight`, high `obese`, neutral under 0.4) with the ratio in a neutral `.bmi-value` (a ratio is not a BMI), then `.er-section`s with `h2` headings (the card sits under the H1): what the ratio means, in NICE's words, with a `.cat-dot`; the waist for each class at the height entered (an `.er-table`, the user's row `.er-active` with an `.er-you` pill, and half the height; ratio ranges and a class's dot with its name stay whole (`.whtr .nw`), so the table fits a 360 px phone and scrolls inside its section only at 320 px); and the method and source line.
- The ratio comes from the numbers as printed: height and waist to 0.1, the ratio cut (not rounded) to two decimals in whole-number arithmetic (tenths), so 0.50 always means a waist of at least half the height, as in the women's page waist check (CMB-017). The waist bounds are the smallest waist, to 0.1, that reaches each class.
- The US / Metric switch converts to 0.1; switching back with nothing retyped restores the numbers as they were. Results on screen follow the switch.

### Category badges
"""


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:100]}'
    return src.replace(old, new)


def main():
    for rel in (PG, SM, CSS, DS):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == PG:
            for old, new in EDITS:
                src = one(src, old, new, PG)
            for gone in ('Better Alternative to BMI', 'Predicts Health Better Than BMI'):
                assert gone not in src, f'"{gone}" is left'
        elif rel == SM:
            src = one(src, f'<url><loc>{URL}</loc><lastmod>2026-11-16</lastmod>', f'<url><loc>{URL}</loc><lastmod>{TODAY}</lastmod>', SM)
        elif rel == CSS:
            assert '.whtr' not in src
            src = src.rstrip('\n') + '\n' + CSS_ADD
        else:
            src = one(src, DS_OLD, DS_NEW, DS)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
