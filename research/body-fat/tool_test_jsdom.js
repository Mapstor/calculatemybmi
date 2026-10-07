const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync('/tmp/b1/body-fat-percentage-chart/index.html','utf8'),{runScripts:'dangerously'});const w=dom.window,d=w.document;let ok=0,fail=0;
w.Element.prototype.scrollIntoView=function(){};
const $=i=>d.getElementById(i),O=()=>$('bf-out').textContent;
function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n,'|',O().slice(0,300));}}
function sex(v){$(v==='m'?'bf-sx-m':'bf-sx-f').checked=true;}
function age(a){$('bf-a').value=String(a);$('bf-a').dispatchEvent(new w.Event('input'));}
function noOverlap(){const r=[...d.querySelectorAll('#bf-out rect.aw-lbl')].map(e=>({r:+e.dataset.r,x:+e.dataset.x,w:+e.dataset.w}));for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){if(r[i].r===r[j].r&&!(r[i].x+r[i].w<=r[j].x||r[j].x+r[j].w<=r[i].x))return false;}return r.length>=1;}
sex('f');age(35);$('bf-v').value='28';$('bf-go').click();
t('woman 35 rank',/of US women 30–39 have more body fat than you/.test(O()));t('gallagher 21–32.9',/21–32\.9%/.test(O())&&/Your value: healthy/.test(O()));t('chart',!!d.querySelector('#bf-out .aw-dist svg path'));t('labels ok',noOverlap());
t('age readout',$('bf-a-out').textContent==='35 years');
sex('m');age(25);$('bf-v').value='15';$('bf-go').click();t('man 25 15%',/of US men 20–29 have more body fat/.test(O())&&/8–19\.9%/.test(O()));
sex('m');age(65);$('bf-v').value='25';$('bf-go').click();t('man 65 no scan data',/No scan data/.test(O())&&/13–24\.9%/.test(O())&&/Your value: high/.test(O())&&!d.querySelector('#bf-out .aw-dist svg'));
sex('f');age(14);$('bf-v').value='30';$('bf-go').click();t('girl 14',/women 12–15/.test(O())&&/Not defined/.test(O()));
sex('f');age(45);$('bf-v').value='';$('bf-go').click();t('no value',/Median, women 40–49/.test(O())&&!/Your rank/.test(O()));
$('bf-v').value='80';$('bf-go').click();t('invalid',/between 3 and 65/.test(O()));
let all=true;sex('f');age(33);for(let v=8;v<=62;v+=3){$('bf-v').value=String(v);$('bf-go').click();if(!noOverlap()){all=false;console.log('overlap at',v);}}t('no overlap sweep (women)',all);
all=true;sex('m');age(52);for(let v=5;v<=50;v+=3){$('bf-v').value=String(v);$('bf-go').click();if(!noOverlap()){all=false;console.log('overlap at',v);}}t('no overlap sweep (men)',all);
d.getElementById('bf-a-plus').click();t('stepper',$('bf-a-out').textContent==='53 years');
console.log(`BF tool: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
