const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync('/tmp/a1/average-weight/index.html','utf8'),{runScripts:'dangerously'});const w=dom.window,d=w.document;let ok=0,fail=0;
function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n,'|',d.getElementById('aw-out').textContent.slice(0,300));}}
const set=(id,v)=>{d.getElementById(id).value=v;};const go=()=>d.getElementById('aw-go').click();const O=()=>d.getElementById('aw-out').textContent;
// woman 5'4", no weight
set('aw-ft','5');set('aw-in','4');go();t('w54 avg 171.2',/171\.2 lb/.test(O())&&/Healthy-weight range at your height \(BMI 18\.5–24\.9\): 108–145 lb/.test(O()));
// with weight 150
set('aw-lb','150');go();t('w54 150 below avg',/21 lb below/.test(O())&&/percentile/.test(O())&&/BMI 25\.7/.test(O()));
// man 5'9" 204
d.querySelector('input[name="aw-sex"][value="m"]').checked=true;set('aw-ft','5');set('aw-in','9');set('aw-lb','204');go();t('m59',/204\.0 lb/.test(O())&&/125–168 lb/.test(O()));
// man 6'6" -> not enough data
set('aw-ft','6');set('aw-in','6');set('aw-lb','');go();t('m66 no data',/Not enough data/.test(O())&&/199\.0 lb/.test(O()));
// metric
d.querySelector('input[name="aw-u"][value="met"]').checked=true;d.querySelector('input[name="aw-u"][value="met"]').dispatchEvent(new w.Event('change'));
d.querySelector('input[name="aw-sex"][value="f"]').checked=true;set('aw-cm','162.5');set('aw-kg','70');go();t('metric 162.5cm',/5′4″/.test(O())&&/171\.2 lb/.test(O())&&/Your weight, 154 lb/.test(O()));
set('aw-cm','100');go();t('bad height',/Enter a height/.test(O()));
console.log(`AW tool: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
