const {JSDOM,VirtualConsole}=require('/home/claude/node_modules/jsdom');const fs=require('fs');const path=require('path');const root=process.argv[2];
function load(p){const html=fs.readFileSync(path.join(root,p),'utf8');const errs=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errs.push(String(e.message||e).slice(0,160)));
 const inl=html.replace(/<script([^>]*)src="(\/assets\/js\/[^"]+)"([^>]*)><\/script>/g,(m,a,src,b)=>{try{return '<script'+a+b+'>'+fs.readFileSync(path.join(root,src),'utf8')+'</script>';}catch(e){return m;}});
 const dom=new JSDOM(inl,{runScripts:'dangerously',virtualConsole:vc,pretendToBeVisual:true});dom.window.Element.prototype.scrollIntoView=function(){};dom.window.scrollTo=function(){};dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded'));return {dom,errs};}
let ok=0,fail=0;function t(n,c,x){if(c)ok++;else{fail++;console.log('FAIL',n,x||'');}}
// homepage standard: metric 182 / 88
{const {dom,errs}=load('index.html');const d=dom.window.document,P=d.getElementById('panel-standard');
 P.querySelector('.unit-btn[data-unit="metric"]').click();P.querySelector('.height-cm').value='182';P.querySelector('.weight-kg').value='88';d.getElementById('calc-standard-btn').click();
 const T=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');
 t('bmi 26.6',/26\.6/.test(T));t('status metric',/6\.0 kg \(13 lbs\) above the healthy range/.test(T),T.match(/[^.]{0,40}above the healthy range[^.]{0,20}/));
 t('height 182 cm + 6\'0"',/182 cm/.test(T)&&/6'0"/.test(T)&&!/5'12"/.test(T));t('weight 88.0 kg first',/88\.0 kg/.test(T));t('range kg first',/62–82 kg/.test(T),T.match(/\d+–\d+ kg/));
 t('no health-risk levels',!/Health Risk Assessment/.test(T)&&/BMI and health/.test(T));t('no "Lose"',!/Lose \d/.test(T));t('no errors',errs.length===0,errs);
 // imperial 5'7" 160
 P.querySelector('.unit-btn[data-unit="imperial"]').click();P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='7';P.querySelector('.weight-lbs').value='160';d.getElementById('calc-standard-btn').click();
 const T2=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');t('imperial 25.1',/25\.1/.test(T2));
 // CMB-005: category follows the BMI as shown (one decimal); healthy limits are whole pounds inside 18.5-24.9
 for(const [ft,inch,lb,bmi,cat] of [['5','10','174','25.0','Overweight'],['5','10','173','24.8','Healthy weight'],['6','2','144','18.5','Healthy weight'],['6','2','143','18.4','Underweight']]){
  P.querySelector('.height-ft').value=ft;P.querySelector('.height-in').value=inch;P.querySelector('.weight-lbs').value=lb;d.getElementById('calc-standard-btn').click();
  t('shown '+ft+"'"+inch+' '+lb+' = '+bmi+' '+cat,d.getElementById('standard-bmi-value').textContent===bmi&&d.getElementById('standard-bmi-category').textContent===cat,d.getElementById('standard-bmi-value').textContent+' '+d.getElementById('standard-bmi-category').textContent);}
 P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='10';P.querySelector('.weight-lbs').value='180';d.getElementById('calc-standard-btn').click();
 t('5\'10" max 173',d.getElementById('standard-healthy-max').textContent==='173 lbs (78.5 kg)',d.getElementById('standard-healthy-max').textContent);
 // BMI 24.9 must not show BMI Prime 1.00 or an "over" label
 P.querySelector('.unit-btn[data-unit="metric"]').click();P.querySelector('.height-cm').value='178';P.querySelector('.weight-kg').value='79';d.getElementById('calc-standard-btn').click();
 const T3=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');t('prime 0.99 at BMI 24.9',/BMI Prime\s*0\.99\s*Under the overweight cut-off/.test(T3),T3.match(/BMI Prime.{0,40}/));
 P.querySelector('.weight-kg').value='75.7';d.getElementById('calc-standard-btn').click();
 const T4=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');t('prime 0.96 at BMI 23.9',/BMI Prime\s*0\.96\s*Under/.test(T4),T4.match(/BMI Prime.{0,30}/));
 t('waist note scoped to BMI 25-34.9',!/whatever the BMI/.test(d.body.textContent));
 P.querySelector('.unit-btn[data-unit="imperial"]').click();t('imperial lbs first',/160 lbs/.test(T2)&&/5'7"/.test(T2)&&/1 lbs \(1 kg\) above|1 lbs \(0 kg\) above|above the healthy range/.test(T2));}
// menu works on every calculator page
for(const p of ['index.html','women-bmi-calculator/index.html','men-bmi-calculator/index.html','age-bmi-calculator/index.html','kids-bmi-calculator/index.html','new-bmi-calculator/index.html','ideal-weight/index.html','lean-body-mass/index.html','blog/index.html']){
 const {dom,errs}=load(p);const d=dom.window.document,tg=d.querySelector('.nav-toggle'),m=d.querySelector('.nav-mobile');tg.click();t('menu opens on '+p,m.classList.contains('active'));t('no errors on '+p,errs.length===0,errs);}
// women/men/age/lbm calculators run and show no banned tiers
for(const [p,btn,pan] of [['women-bmi-calculator/index.html','calc-women-btn','panel-women'],['men-bmi-calculator/index.html','calc-men-btn','panel-men'],['age-bmi-calculator/index.html','calc-age-btn','panel-age'],['lean-body-mass/index.html','calc-lbm-btn','panel-lbm']]){
 const {dom,errs}=load(p);const d=dom.window.document;const P=d.getElementById(pan)||d;const q=s=>P.querySelector(s);
 if(q('.height-ft'))q('.height-ft').value='5';if(q('.height-in'))q('.height-in').value='9';if(q('.weight-lbs'))q('.weight-lbs').value='180';P.querySelectorAll('input[type=number]').forEach(i=>{if(!i.value&&/age/i.test(i.id+i.className))i.value='40';});
 const b=d.getElementById(btn);if(b)b.click();const T=d.body.textContent;t('runs '+p,errs.length===0,errs);t('no ACE tiers on '+p,!/Essential Fat|Above Average/.test(T));}
// CMB-005: one tap opens an FAQ answer (two click bindings used to cancel out)
for(const p of ['index.html','women-bmi-calculator/index.html','men-bmi-calculator/index.html','age-bmi-calculator/index.html','kids-bmi-calculator/index.html','new-bmi-calculator/index.html','ideal-weight/index.html','lean-body-mass/index.html','calculators/index.html','blog/bmi-and-health-risks/index.html','blog/bmi-limitations/index.html','blog/waist-to-height-ratio/index.html','blog/how-to-lower-bmi/index.html','blog/bmi-and-metabolism/index.html','blog/underweight-bmi-risks/index.html']){
 const {dom}=load(p);const d=dom.window.document,q=d.querySelector('.faq-question');q.click();t('FAQ opens on '+p,d.querySelectorAll('.faq-item.open').length===1);q.click();t('FAQ closes on '+p,d.querySelectorAll('.faq-item.open').length===0);}
// CMB-045 (was CMB-005): at 70 the result keeps CDC's adult range and gives Winter et al. 2014 in the DEVLOG §4 wording,
// no entity text; at 15 the calculator gives no adult result and sends the reader to the children's calculator
{const {dom}=load('age-bmi-calculator/index.html');const d=dom.window.document;const P=d.getElementById('panel-age');const q=s=>P.querySelector(s);
 q('.height-ft').value='5';q('.height-in').value='9';q('.weight-lbs').value='180';q('.age-input').value='70';d.getElementById('calc-age-btn').click();
 const res=d.getElementById('age-results').textContent;t('age 70 result has no entity text',!/&[a-z]+;/.test(res));
 t('age 70 summary gives the Winter finding in the §4 wording',/compared with a BMI of 23 to 23\.9, the risk of death was higher below 23 and began to rise at about 33 \(Winter et al\., 2014\)/.test(res));
 t('age 70: no plateau or lowest-mortality wording',!/plateau|lowest (all-cause )?mortality|23–33|WHO adult range/.test(res));
 t('age 70 keeps the adult range',/At 70, the healthy BMI range is 18\.5 to 24\.9/.test(res));
 q('.age-input').value='15';d.getElementById('calc-age-btn').click();
 t('age 15: no adult result',!d.getElementById('age-results').classList.contains('visible'));
 const note=d.getElementById('age-note');t('age 15: note points to the children\'s calculator',!note.hidden&&!!note.querySelector('a[href="/kids-bmi-calculator/"]'),note.textContent);}
// CMB-011: metric BMI is kg/m2 as entered (145 cm / 84 kg and 159 cm / 101 kg are 40.0, class III; 703 gave 39.9)
{const {dom,errs}=load('index.html');const d=dom.window.document,P=d.getElementById('panel-standard');P.querySelector('.unit-btn[data-unit="metric"]').click();
 for(const [cm,kg] of [['145','84'],['159','101']]){P.querySelector('.height-cm').value=cm;P.querySelector('.weight-kg').value=kg;d.getElementById('calc-standard-btn').click();
  t('metric '+cm+'/'+kg+' = 40.0 class 3 obesity',d.getElementById('standard-bmi-value').textContent==='40.0'&&/Class 3 obesity/.test(d.getElementById('standard-bmi-category').textContent),d.getElementById('standard-bmi-value').textContent+' '+d.getElementById('standard-bmi-category').textContent);}
 const T=d.getElementById('standard-results').textContent;t('no arrow glyphs in results',!/\u279C/.test(T));t('answer comes first',T.indexOf('What your result means')<T.indexOf('BMI categories'));t('no errors (metric 40)',errs.length===0,errs);}
// CMB-011: women result line, ideal weight in the user's unit, lean mass with one decimal, kids percentile line
{const {dom}=load('women-bmi-calculator/index.html');const d=dom.window.document,P=d.getElementById('panel-women');P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='5';P.querySelector('.weight-lbs').value='170';d.getElementById('calc-women-btn').click();
 t('women status line',/above the healthy range/.test(d.getElementById('women-weight-diff').textContent),d.getElementById('women-weight-diff').textContent);}
{const {dom,errs}=load('ideal-weight/index.html');const d=dom.window.document,P=d.getElementById('panel-ideal');P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='6';P.querySelector('.sex-select').value='female';P.querySelector('.frame-select').value='medium';d.getElementById('calc-ideal-btn').click();
 t('ideal Devine in lbs first',d.getElementById('ideal-devine').textContent.replace(/\s+/g,' ').trim()==='131 lbs (59.3 kg)',d.getElementById('ideal-devine').textContent);
 // CMB-028: Hamwi in his own pounds (130, not 129), the span of the four replaces the average, frame changes Hamwi only, no number under 5 feet
 t('ideal Hamwi 130 lbs',d.getElementById('ideal-hamwi').textContent.replace(/\s+/g,' ').trim()==='130 lbs (59.0 kg)',d.getElementById('ideal-hamwi').textContent);
 t('ideal span in lbs first',d.getElementById('ideal-span').textContent.replace(/\s+/g,' ').trim()==='130–135 lbs (59.0–61.3 kg)',d.getElementById('ideal-span').textContent);
 t('ideal has no average',!d.getElementById('ideal-average')&&!/average/i.test(d.getElementById('ideal-results').textContent));
 t('ideal summary gives the BMI at the formula weights',/your BMI would be 21\.0 to 21\.8, inside the healthy range/.test(d.getElementById('ideal-results').textContent),d.getElementById('ideal-results').textContent.match(/your BMI would be[^.]*/));
 P.querySelector('.frame-select').value='large';d.getElementById('calc-ideal-btn').click();
 t('ideal large frame changes Hamwi only',d.getElementById('ideal-hamwi').textContent.replace(/\s+/g,' ').trim()==='143 lbs (64.9 kg)'&&d.getElementById('ideal-devine').textContent.replace(/\s+/g,' ').trim()==='131 lbs (59.3 kg)',d.getElementById('ideal-hamwi').textContent+' / '+d.getElementById('ideal-devine').textContent);
 P.querySelector('.height-ft').value='4';P.querySelector('.height-in').value='10';P.querySelector('.frame-select').value='medium';d.getElementById('calc-ideal-btn').click();
 t('ideal 4\'10" gives no formula number',/^Starts at 5 feet/.test(d.getElementById('ideal-hamwi').textContent)&&/start at 5 feet \(60 inches\)/.test(d.getElementById('ideal-results').textContent)&&d.getElementById('ideal-bmi-range').textContent.replace(/\s+/g,' ').trim()==='89–119 lbs (40.4–54.0 kg)',d.getElementById('ideal-hamwi').textContent+' / '+d.getElementById('ideal-bmi-range').textContent);
 t('ideal frame link has a target',!!d.getElementById('frame'));t('ideal runs',errs.length===0,errs);}
{const {dom,errs}=load('lean-body-mass/index.html');const d=dom.window.document,P=d.getElementById('panel-lbm');P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='8';P.querySelector('.weight-lbs').value='170';P.querySelector('.sex-select').value='male';d.getElementById('calc-lbm-btn').click();
 t('lean mass 128.5 lbs (58.3 kg)',d.getElementById('lbm-lbm').textContent.replace(/\s+/g,' ').trim()==='128.5 lbs (58.3 kg)',d.getElementById('lbm-lbm').textContent);
 t('lean mass kg for the chart',d.getElementById('lbm-lbm').dataset.kg==='58.30',d.getElementById('lbm-lbm').dataset.kg);t('lbm runs',errs.length===0,errs);}
{const {dom,errs}=load('kids-bmi-calculator/index.html');const d=dom.window.document,P=d.getElementById('panel-kids');P.querySelector('.height-ft').value='4';P.querySelector('.height-in').value='6';P.querySelector('.weight-lbs').value='70';P.querySelector('.age-input').value='10';P.querySelector('.months-input').value='0';P.querySelector('.sex-select').value='male';d.getElementById('calc-kids-btn').click();
 const note=d.getElementById('kids-percentile-note').textContent;t('kids percentile line (exact 54.46)',/^54th percentile for boys aged 10 years$/.test(note),note);
 t('kids no simplified-estimate disclaimer',!/simplified BMI estimate/.test(d.getElementById('kids-results').textContent));t('kids runs',errs.length===0,errs);}
console.log(`calculator checks: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
