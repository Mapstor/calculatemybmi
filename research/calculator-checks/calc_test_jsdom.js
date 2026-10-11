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
 t('height 182 cm + 6\'0"',/182 cm/.test(T)&&/6'0"/.test(T)&&!/5'12"/.test(T));t('weight 88.0 kg first',/88\.0 kg/.test(T));t('range kg first',/62-82 kg/.test(T),T.match(/\d+-\d+ kg/));
 t('no health-risk levels',!/Health Risk Assessment/.test(T)&&/BMI and Health/.test(T));t('no "Lose"',!/Lose \d/.test(T));t('no errors',errs.length===0,errs);
 // imperial 5'7" 160
 P.querySelector('.unit-btn[data-unit="imperial"]').click();P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='7';P.querySelector('.weight-lbs').value='160';d.getElementById('calc-standard-btn').click();
 const T2=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');t('imperial 25.1',/25\.1/.test(T2));
 // CMB-005: category follows the BMI as shown (one decimal); healthy limits are whole pounds inside 18.5-24.9
 for(const [ft,inch,lb,bmi,cat] of [['5','10','174','25.0','Overweight'],['5','10','173','24.8','Normal'],['6','2','144','18.5','Normal'],['6','2','143','18.4','Underweight']]){
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
// CMB-005: age 65+ result shows a real middle dot (not the text "&middot;") and keeps the adult range
{const {dom}=load('age-bmi-calculator/index.html');const d=dom.window.document;const P=d.getElementById('panel-age');const q=s=>P.querySelector(s);
 q('.height-ft').value='5';q('.height-in').value='9';q('.weight-lbs').value='180';q('.age-input').value='70';d.getElementById('calc-age-btn').click();
 const tile=d.getElementById('age-adjusted-range').textContent;t('age 70 tile has no entity text',!/&[a-z]+;/.test(tile),tile);
 t('age 70 tile keeps the adult range',/^18\.5 - 24\.9 \(WHO adult range\) \u00b7 lowest mortality observed across BMI 23-33/.test(tile),tile);
 t('age 70 extended line says Adult BMI range',/Adult BMI range: 18\.5 - 24\.9/.test(d.body.textContent));}
console.log(`calculator checks: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
