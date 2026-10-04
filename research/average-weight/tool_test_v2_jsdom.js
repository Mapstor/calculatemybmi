const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync('/tmp/a2/average-weight/index.html','utf8'),{runScripts:'dangerously'});const w=dom.window,d=w.document;let ok=0,fail=0;
w.Element.prototype.scrollIntoView=function(){};
function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n,'|',d.getElementById('aw-out').textContent.slice(0,400));}}
const $=i=>d.getElementById(i),O=()=>$('aw-out').textContent,click=id=>$(id).click();
function radio(id){$(id).checked=true;$(id).dispatchEvent(new w.Event('change'));}
function noOverlap(){const r=[...d.querySelectorAll('#aw-out rect.aw-lbl')].map(e=>({r:+e.dataset.r,x:+e.dataset.x,w:+e.dataset.w}));
 for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){if(r[i].r===r[j].r&&!(r[i].x+r[i].w<=r[j].x||r[j].x+r[j].w<=r[i].x))return false;}return r.length>=2;}
// man 6'0", 194 lb, age 40-49
radio('aw-sx-m');$('aw-h').value='72';$('aw-h').dispatchEvent(new w.Event('input'));t('readout 6′ 0″',$('aw-h-out').textContent==='6′ 0″');
$('aw-w').value='194';$('aw-age').value='40–49';click('aw-go');
t('avg 215.7',/215\.7 lb/.test(O()));t('rank pct',/(\d+)(st|nd|rd|th)percentile among men/.test(O().replace(/\s+/g,''))||/percentile among men/.test(O()));
t('BMI 26.3 overweight',/26\.3/.test(O())&&/Overweight/.test(O()));t('height rank 84th',/84th pct/.test(O())||/taller than 8[34]%/.test(O()));
t('dist chart',!!d.querySelector('#aw-out .aw-dist svg path'));t('labels no overlap',noOverlap());
t('age bar',/Average, men 40–49/.test(O())&&/210 lb/.test(O()));t('gauge',!!d.querySelector('#aw-out .aw-g-tr i'));
// metric 182 cm / 88 kg
radio('aw-u-met');t('weight converted',Math.abs(parseFloat($('aw-w').value)-88.0)<0.2);$('aw-h').value='182';$('aw-h').dispatchEvent(new w.Event('input'));t('cm readout',$('aw-h-out').textContent==='182 cm');
click('aw-go');t('metric 182cm -> 6′ 0″',/6′ 0″ · 182 cm/.test(O())&&/215\.7 lb/.test(O()));
// back to imperial, man 6'7" no data
radio('aw-u-imp');$('aw-h').value='79';$('aw-h').dispatchEvent(new w.Event('input'));$('aw-w').value='';$('aw-age').value='';click('aw-go');t('no data',/No data/.test(O())&&/199\.0 lb/.test(O()));
// woman 5'4", no weight
radio('aw-sx-f');$('aw-h').value='64';$('aw-h').dispatchEvent(new w.Event('input'));click('aw-go');t('woman 5′4″',/171\.2 lb/.test(O())&&/Typical range/.test(O())&&/108–145 lb/.test(O())&&noOverlap());
// stepper
click('aw-h-plus');t('stepper',$('aw-h-out').textContent==='5′ 5″');
// labels for many positions: sweep weights for 6'0" man and check overlap every time
radio('aw-sx-m');$('aw-h').value='72';$('aw-h').dispatchEvent(new w.Event('input'));let allok=true;for(let wt=120;wt<=330;wt+=7){$('aw-w').value=String(wt);click('aw-go');if(!noOverlap()){allok=false;console.log('overlap at',wt);}}t('no overlap across weight sweep',allok);
console.log(`AW2 tool: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
