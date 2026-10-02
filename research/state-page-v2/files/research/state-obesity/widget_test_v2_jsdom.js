const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const html=fs.readFileSync('/tmp/sb2/obesity-rate-by-state/index.html','utf8');
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true});const w=dom.window,d=w.document;let ok=0,fail=0;
function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n);}}
w.Element.prototype.scrollIntoView=function(){};
const sl=d.getElementById('obs-year');const st=a=>d.querySelector('#obs-map-svg .obs-st[data-s="'+a+'"]');
const band=f=>st('AL').getAttribute('fill');
t('AL 2025 fill',st('AL').getAttribute('fill')==='#C2481E');t('CA hatched',st('CA').getAttribute('fill')==='url(#obs-hatch)');
sl.value='2011';sl.dispatchEvent(new w.Event('input'));
t('year 2011',d.getElementById('obs-year-out').textContent==='2011');t('caption 2011',/^2011: 0 of 50 states/.test(d.getElementById('obs-map-cap').textContent));
t('CO 2011 band 20-25',st('CO').getAttribute('fill')==='#FAD5B7');
sl.value='2019';sl.dispatchEvent(new w.Event('input'));t('NJ 2019 hatched',st('NJ').getAttribute('fill')==='url(#obs-hatch)');t('MS 2019 40+',st('MS').getAttribute('fill')==='#7F2A10');
sl.value='2025';sl.dispatchEvent(new w.Event('input'));
d.getElementById('obs-state').value='KY';d.getElementById('obs-go').click();const P=d.getElementById('obs-panel');const T=P.textContent;
t('panel shown',!P.hidden);t('KY value',/38\.8%/.test(T));t('KY rank #3 of 47',/#3of 47 states|#3 ?of 47/.test(T.replace(/\s+/g,' '))||/#3/.test(P.querySelector('.obs-rank-n').textContent));
t('median sentence',/5\.1 points above the median state \(33\.7%\)/.test(T));t('range sentence',/Colorado \(25\.7%\) to Alabama \(39\.7%\)/.test(T));
t('neighbors sentence',/neighbors with data/.test(T));t('yoy sentence',/From 2024: /.test(T));t('since 2011',/Since 2011: \+8\.4 points/.test(T));
t('region 2025',/South as a whole: 34\.8%/.test(T));t('compare bars',P.querySelectorAll('.obs-cb').length>=10);
t('trend svg + CI band',!!P.querySelector('.obs-trend svg path[opacity]'));t('age bars',/Ages 40–59/.test(T));
t('selected outline',st('KY').classList.contains('obs-on'));
st('MS').dispatchEvent(new w.Event('click'));t('MS no 2025',/no 2025 estimate/.test(P.textContent)&&/40\.4% in 2024/.test(P.textContent));
st('HI').dispatchEvent(new w.Event('click'));t('HI no neighbors',/No land neighbors/.test(P.textContent));
const dc=d.querySelector('#obs-map-svg .obs-dc');dc.dispatchEvent(new w.Event('click'));t('DC panel',/District of Columbia/.test(P.textContent)&&/not a state/.test(P.textContent)&&!d.querySelector('.obs-rank'));
// slider updates open panel
st('TX').dispatchEvent(new w.Event('click'));sl.value='2013';sl.dispatchEvent(new w.Event('input'));t('panel follows year',/Texas 2013/.test(P.textContent.replace(/\s+/g,' ')));
// play button toggles
const pb=d.getElementById('obs-play');pb.click();t('play started',/Pause/.test(pb.textContent));pb.click();t('play stopped',/Play/.test(pb.textContent));
console.log(`OBS v2 widget: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
