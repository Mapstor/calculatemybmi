const {JSDOM,VirtualConsole}=require('/home/claude/node_modules/jsdom');const fs=require('fs');const path=require('path');const root=process.argv[2];
function load(p){const html=fs.readFileSync(path.join(root,p),'utf8');const errs=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errs.push(String(e.message||e).slice(0,140)));
 const inl=html.replace(/<script([^>]*)src="(\/assets\/js\/[^"]+)"([^>]*)><\/script>/g,(m,a,src,b)=>'<script'+a+b+'>'+fs.readFileSync(path.join(root,src),'utf8')+'</script>');
 const dom=new JSDOM(inl,{runScripts:'dangerously',virtualConsole:vc,pretendToBeVisual:true});const w=dom.window;w.Element.prototype.scrollIntoView=function(){};w.scrollTo=function(){};w.document.dispatchEvent(new w.Event('DOMContentLoaded'));return {dom,errs};}
const pages=['index.html','women-bmi-calculator/index.html','men-bmi-calculator/index.html','age-bmi-calculator/index.html','kids-bmi-calculator/index.html','new-bmi-calculator/index.html','ideal-weight/index.html','lean-body-mass/index.html'];
const report=[];
for(const p of pages){
 for(const mode of ['imperial','metric']){
  for(const scen of ['typical','short-heavy','tall-light','empty']){
   const {dom,errs}=load(p);const d=dom.window.document;const btn=[...d.querySelectorAll('[id^="calc-"][id$="-btn"]')][0];if(!btn){report.push({p,mode,scen,note:'no calc button'});continue;}
   const type=btn.id.replace('calc-','').replace('-btn','');const P=d.getElementById('panel-'+type)||d;
   const ub=P.querySelector('.unit-btn[data-unit="'+mode+'"]');if(ub)ub.click();else if(mode==='metric'){continue;}
   const V={typical:{ft:5,in:9,cm:175,lb:170,kg:77,age:35},'short-heavy':{ft:4,in:11,cm:150,lb:260,kg:118,age:52},'tall-light':{ft:6,in:5,cm:196,lb:150,kg:68,age:24},empty:null}[scen];
   const fields=[...P.querySelectorAll('input,select')];const used=[];
   fields.forEach(f=>{const k=(f.id+' '+f.className+' '+(f.name||'')).toLowerCase();if(!V){if(f.tagName==='INPUT'&&f.type!=='radio'&&f.type!=='checkbox')f.value='';return;}
    if(f.tagName==='SELECT'){if(/sex|gender/.test(k)){f.value=f.options[f.options.length>1?1:0].value;used.push('sex');} else if(/month/.test(k)){} return;}
    if(f.type==='radio'||f.type==='checkbox')return;
    if(/height-ft|feet|\bft\b/.test(k)){f.value=V.ft;used.push('ft');}else if(/height-in|inches|\bin\b/.test(k)){f.value=V.in;used.push('in');}else if(/height-cm|\bcm\b/.test(k)){f.value=V.cm;used.push('cm');}
    else if(/weight-lb|lbs|pound/.test(k)){f.value=V.lb;used.push('lb');}else if(/weight-kg|\bkg\b/.test(k)){f.value=V.kg;used.push('kg');}else if(/age|year/.test(k)){f.value=(p.includes('kids')?10:V.age);used.push('age');}else if(/month/.test(k)){f.value=0;}});
   try{btn.click();}catch(e){errs.push('click '+e.message);}
   const R=d.getElementById(type+'-results');const T=(R?R.textContent:d.body.textContent).replace(/\s+/g,' ');
   const flags=[];if(/NaN|undefined|Infinity|\bnull\b/.test(T))flags.push('NaN/undefined');if(/\d'1[2-9]"/.test(T))flags.push("bad ft-in");if(mode==='metric'&&/\d+ lbs \(\d+(\.\d)? kg\)/.test(T))flags.push('lbs-first in metric');
   if(/-\d+(\.\d)? (kg|lbs) (above|below)/.test(T))flags.push('negative distance');if(/Essential Fat|Above Average|Health Risk Assessment|Lose \d/.test(T))flags.push('banned/old text');
   const visible=R?R.classList.contains('visible'):null;
   report.push({p,mode,scen,used:used.join(','),visible,errs:errs.slice(0,2),flags,sample:T.slice(0,150)});}}}
fs.writeFileSync('/tmp/audit_calcs.json',JSON.stringify(report,null,1));
const bad=report.filter(r=>(r.flags&&r.flags.length)||(r.errs&&r.errs.length)||r.note);console.log('runs:',report.length,'| runs with problems:',bad.length);
bad.slice(0,30).forEach(r=>console.log('-',r.p,r.mode,r.scen,'| used:',r.used,'| flags:',r.flags,'| errs:',r.errs,'| note:',r.note||'','|',(r.sample||'').slice(0,110)));
const emp=report.filter(r=>r.scen==='empty');console.log('\nempty-input behaviour:');emp.forEach(r=>console.log('  ',r.p,r.mode,'visible:',r.visible,'|',(r.sample||'').slice(0,90)));
