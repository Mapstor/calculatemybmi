const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const html=fs.readFileSync('/tmp/sb/obesity-rate-by-state/index.html','utf8');
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true});const w=dom.window,d=w.document;let ok=0,fail=0;
function t(name,cond){if(cond){ok++;}else{fail++;console.log('FAIL',name);}}
w.Element.prototype.scrollIntoView=function(){};
const sl=d.getElementById('obs-year');const tile=a=>d.querySelector('#obs-map-svg .obs-tile[data-s="'+a+'"]');
// initial (server-rendered 2025)
t('AL 2025 label',tile('AL').querySelectorAll('text')[1].textContent==='39.7');
t('CA 2025 n/a',tile('CA').querySelectorAll('text')[1].textContent==='n/a');
// slider to 2011
sl.value='2011';sl.dispatchEvent(new w.Event('input'));
t('year out 2011',d.getElementById('obs-year-out').textContent==='2011');
t('AL 2011 label',tile('AL').querySelectorAll('text')[1].textContent==='32.0');
t('CA 2011 has value',tile('CA').querySelectorAll('text')[1].textContent==='23.8');
t('caption 2011 zero >=35',/^2011: 0 of 50 states/.test(d.getElementById('obs-map-cap').textContent));
sl.value='2019';sl.dispatchEvent(new w.Event('input'));
t('NJ 2019 n/a',tile('NJ').querySelectorAll('text')[1].textContent==='n/a');
t('caption 2019 12 of 49 + 1 missing',/2019: 12 of 49 states.*\(1 without/.test(d.getElementById('obs-map-cap').textContent));
t('MS 2019 fill >=40 band',tile('MS').querySelector('rect').getAttribute('fill')==='#7F2A10');
// state panel: Texas via button at 2025
sl.value='2025';sl.dispatchEvent(new w.Event('input'));
d.getElementById('obs-state').value='TX';d.getElementById('obs-go').click();
const P=d.getElementById('obs-panel');t('panel visible',!P.hidden);
t('TX value',/36\.1%/.test(P.textContent));t('TX CI',/34\.3–38\.0%/.test(P.textContent));
t('TX change',/\+5\.7 percentage points/.test(P.textContent));t('TX age',/18–39: 32\.2%.*40–59: 43\.6%.*60\+: 33\.0%/.test(P.textContent));
t('TX rank',/ranks\s+\d+ of 47/.test(P.textContent));t('spark svg',!!P.querySelector('svg path'));
// missing state panel via tile click
tile('MS').dispatchEvent(new w.Event('click'));
t('MS no 2025',/no 2025 estimate/.test(P.textContent)&&/40\.4%<\/strong> in 2024|40\.4% in 2024/.test(P.innerHTML.replace(/<\/?strong>/g,'')));
// keyboard on tile
const ev=new w.KeyboardEvent('keydown',{key:'Enter'});tile('CO').dispatchEvent(ev);t('CO via keyboard',/Colorado/.test(P.textContent)&&/25\.7%/.test(P.textContent));
// DC has no rank line
d.getElementById('obs-state').value='DC';d.getElementById('obs-go').click();t('DC no rank',!/ranks/.test(P.textContent)&&/24\.2%/.test(P.textContent));
console.log(`OBS widget: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
