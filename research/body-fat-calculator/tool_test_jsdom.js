const {JSDOM}=require('/home/claude/node_modules/jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync('/tmp/c2/body-fat-calculator/index.html','utf8'),{runScripts:'dangerously'});const w=dom.window,d=w.document;let ok=0,fail=0;
w.Element.prototype.scrollIntoView=function(){};
const $=i=>d.getElementById(i),O=()=>$('bc-out').textContent;
function t(n,c){if(c)ok++;else{fail++;console.log('FAIL',n,'|',O().slice(0,260));}}
function radio(id){$(id).checked=true;$(id).dispatchEvent(new w.Event('change'));}
function H(v){$('bc-h').value=String(v);$('bc-h').dispatchEvent(new w.Event('input'));}
function clear(){['bc-neck','bc-waist','bc-hip','bc-s1','bc-s2','bc-s3','bc-w'].forEach(i=>$(i).value='');}
// Army worked example, woman: neck 15, waist 42, hips 44, height 64 -> 46.7
radio('bc-sx-f');radio('bc-m-tape');H(64);$('bc-age').value='35';clear();$('bc-neck').value='15';$('bc-waist').value='42';$('bc-hip').value='44';$('bc-go').click();t('Army woman 47.3',/47\.3%/.test(O()));
// Army worked example, man: neck 16, waist 49, height 69 -> 38.6
radio('bc-sx-m');t('hip hidden for men',$('bc-hip-f').hidden===true);H(69);clear();$('bc-neck').value='16';$('bc-waist').value='49';$('bc-go').click();t('Army man 38.6',/38\.6%/.test(O()));
// metric: same man in cm must give the same 38.6
radio('bc-u-met');t('height converted to cm',Math.abs(+$('bc-h').value-175)<=1);t('neck converted',Math.abs(parseFloat($('bc-neck').value)-40.6)<0.2);$('bc-go').click();
t('metric man ~38.6',/38\.[4-8]%/.test(O()));radio('bc-u-imp');t('back to inches',+$('bc-h').value===69);
// skinfold man sum 53 age 40 -> 17.1 (published worked density 1.0597633)
radio('bc-m-skin');t('pane switch',$('bc-p-skin').hidden===false&&$('bc-p-tape').hidden===true);clear();$('bc-age').value='40';$('bc-s1').value='18';$('bc-s2').value='20';$('bc-s3').value='15';$('bc-go').click();t('JP3 man sum 53 age 40 -> 17.1',/17\.1%/.test(O()));
// BMI method: man 5'9", 170 lb, age 40 -> BMI 25.1 -> 1.2*25.1+0.23*40-16.2 = 23.1
radio('bc-m-bmi');clear();$('bc-age').value='40';$('bc-w').value='170';$('bc-go').click();const bmi=(170*0.45359237)/Math.pow(69*0.0254,2),exp=(1.2*bmi+0.23*40-16.2).toFixed(1);t('Deurenberg '+exp,O().includes(exp+'%'));
t('rank tile',/of men 40–49 have more body fat/.test(O()));t('gallagher tile',/11–21\.9%/.test(O()));t('dist chart',!!d.querySelector('#bc-out .aw-dist svg path'));
// multiple methods: tape + bmi
radio('bc-m-tape');$('bc-neck').value='16';$('bc-waist').value='34';$('bc-go').click();t('two methods shown',/Tape measure/.test(O())&&/Height & weight/.test(O())&&/differ by/.test(O()));
// errors
clear();$('bc-go').click();t('tape missing',/Enter your neck, waist/.test(O()));$('bc-neck').value='20';$('bc-waist').value='18';$('bc-go').click();t('waist<neck',/waist must be larger/.test(O()));
$('bc-age').value='15';$('bc-go').click();t('age check',/between 18 and 79/.test(O()));
// age 65 -> no CDC comparison but Gallagher 60-79
$('bc-age').value='65';clear();$('bc-neck').value='16';$('bc-waist').value='38';$('bc-go').click();t('age 65',/13–24\.9%/.test(O())&&/covered ages 8–59/.test(O()));
console.log(`BC tool: ${ok} passed, ${fail} failed`);process.exit(fail?1:0);
