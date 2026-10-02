const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync('/tmp/c1/childhood-obesity-statistics/index.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true});const w=dom.window,d=w.document;let ok=0,fail=0;
function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n);}}
const svg=d.getElementById('ck-trend-svg');const lines=()=>svg.querySelectorAll('path[stroke-width="2.6"]').length;
t('default 2 series',lines()===2);t('end label 21.1',/21\.1%/.test(svg.textContent));
const chip=k=>d.querySelector('.ck-chip[data-k="'+k+'"]');
chip('a1219').click();t('add teens -> 3',lines()===3&&chip('a1219').getAttribute('aria-pressed')==='true');t('teens end 22.9',/22\.9%/.test(svg.textContent));
chip('sev').click();t('remove severe -> 2',lines()===2);chip('all').click();chip('a1219').click();t('cannot remove last',lines()===1);
const pt=svg.querySelector('.ck-pt');pt.dispatchEvent(new w.Event('click'));const tip=d.getElementById('ck-tip');t('tooltip shows',!tip.hidden&&/%/.test(tip.textContent)&&/95% range/.test(tip.textContent));
t('a1219 starts 1966',[...svg.querySelectorAll('.ck-pt')].some(c=>/1966–1970\|4\.6/.test(c.getAttribute('data-t'))));
console.log(`CK chart: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
