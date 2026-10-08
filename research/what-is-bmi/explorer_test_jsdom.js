const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync('/tmp/w1/blog/what-is-bmi/index.html','utf8'),{runScripts:'dangerously'});const w=dom.window,d=w.document;let ok=0,fail=0;
const $=i=>d.getElementById(i);function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n,'|',$('wb-out').textContent.slice(0,200));}}
t('default 25.1 overweight',$('wb-bmi').textContent==='25.1'&&$('wb-cat').textContent==='Overweight');t('band 125–168',/125 lb–168 lb/.test($('wb-bands').textContent));
$('wb-w').value='140';$('wb-w').dispatchEvent(new w.Event('input'));t('140 lb -> 20.7 healthy',$('wb-bmi').textContent==='20.7'&&$('wb-cat').textContent==='Healthy weight');
$('wb-w').value='230';$('wb-w').dispatchEvent(new w.Event('input'));t('230 lb -> 34.0 obesity',$('wb-bmi').textContent==='34.0'&&$('wb-cat').textContent==='Obesity');
t('obesity threshold text',/Obesity: 203 lb and over/.test($('wb-bands').textContent));
$('wb-u-met').checked=true;$('wb-u-met').dispatchEvent(new w.Event('change'));t('metric height 175',$('wb-h').value==='175'&&$('wb-h-out').textContent==='175 cm');t('metric weight 104',$('wb-w').value==='104');t('metric bmi ~34',/^3[34]\.\d$/.test($('wb-bmi').textContent));
$('wb-u-imp').checked=true;$('wb-u-imp').dispatchEvent(new w.Event('change'));t('back to imperial',$('wb-h').value==='69');
$('wb-h-plus').click();t('stepper height',$('wb-h-out').textContent==='5′ 10″');
console.log(`WB explorer: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
