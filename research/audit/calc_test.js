const {JSDOM,VirtualConsole}=require('/home/claude/node_modules/jsdom');const fs=require('fs');const path=require('path');const root=process.argv[2];
function load(p){const html=fs.readFileSync(path.join(root,p),'utf8');const errs=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errs.push(String(e.message||e).slice(0,160)));
 const inl=html.replace(/<script([^>]*)src="(\/assets\/js\/[^"]+)"([^>]*)><\/script>/g,(m,a,src,b)=>{try{return '<script'+a+b+'>'+fs.readFileSync(path.join(root,src),'utf8')+'</script>';}catch(e){return m;}});
 const dom=new JSDOM(inl,{runScripts:'dangerously',virtualConsole:vc,pretendToBeVisual:true});dom.window.Element.prototype.scrollIntoView=function(){};dom.window.scrollTo=function(){};dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded'));return {dom,errs};}
let ok=0,fail=0;function t(n,c,x){if(c)ok++;else{fail++;console.log('FAIL',n,x||'');}}
// homepage standard: metric 182 / 88
{const {dom,errs}=load('index.html');const d=dom.window.document,P=d.getElementById('panel-standard');
 P.querySelector('.unit-btn[data-unit="metric"]').click();P.querySelector('.height-cm').value='182';P.querySelector('.weight-kg').value='88';d.getElementById('calc-standard-btn').click();
 const T=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');
 t('bmi 26.6',/26\.6/.test(T));t('status metric',/6 kg \(12 lbs\) above the healthy range|5 kg \(12 lbs\) above the healthy range/.test(T),T.match(/[^.]{0,40}above the healthy range[^.]{0,20}/));
 t('height 182 cm + 6\'0"',/182 cm/.test(T)&&/6'0"/.test(T)&&!/5'12"/.test(T));t('weight 88.0 kg first',/88\.0 kg/.test(T));t('range kg first',/61-82 kg/.test(T)||/61-83 kg/.test(T),T.match(/\d+-\d+ kg/));
 t('no health-risk levels',!/Health Risk Assessment/.test(T)&&/BMI and Health/.test(T));t('no "Lose"',!/Lose \d/.test(T));t('no errors',errs.length===0,errs);
 // imperial 5'7" 160
 P.querySelector('.unit-btn[data-unit="imperial"]').click();P.querySelector('.height-ft').value='5';P.querySelector('.height-in').value='7';P.querySelector('.weight-lbs').value='160';d.getElementById('calc-standard-btn').click();
 const T2=d.getElementById('standard-results').textContent.replace(/\s+/g,' ');t('imperial 25.1',/25\.1/.test(T2));t('imperial lbs first',/160 lbs/.test(T2)&&/5'7"/.test(T2)&&/1 lbs \(1 kg\) above|1 lbs \(0 kg\) above|above the healthy range/.test(T2));}
// menu works on every calculator page
for(const p of ['index.html','women-bmi-calculator/index.html','men-bmi-calculator/index.html','age-bmi-calculator/index.html','kids-bmi-calculator/index.html','new-bmi-calculator/index.html','ideal-weight/index.html','lean-body-mass/index.html','blog/index.html']){
 const {dom,errs}=load(p);const d=dom.window.document,tg=d.querySelector('.nav-toggle'),m=d.querySelector('.nav-mobile');tg.click();t('menu opens on '+p,m.classList.contains('active'));t('no errors on '+p,errs.length===0,errs);}
// women/men/age/lbm calculators run and show no banned tiers
for(const [p,btn,pan] of [['women-bmi-calculator/index.html','calc-women-btn','panel-women'],['men-bmi-calculator/index.html','calc-men-btn','panel-men'],['age-bmi-calculator/index.html','calc-age-btn','panel-age'],['lean-body-mass/index.html','calc-lbm-btn','panel-lbm']]){
 const {dom,errs}=load(p);const d=dom.window.document;const P=d.getElementById(pan)||d;const q=s=>P.querySelector(s);
 if(q('.height-ft'))q('.height-ft').value='5';if(q('.height-in'))q('.height-in').value='9';if(q('.weight-lbs'))q('.weight-lbs').value='180';P.querySelectorAll('input[type=number]').forEach(i=>{if(!i.value&&/age/i.test(i.id+i.className))i.value='40';});
 const b=d.getElementById(btn);if(b)b.click();const T=d.body.textContent;t('runs '+p,errs.length===0,errs);t('no ACE tiers on '+p,!/Essential Fat|Above Average/.test(T));}
console.log(`calculator checks: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
