const {JSDOM,VirtualConsole}=require('/home/claude/node_modules/jsdom');const fs=require('fs');const path=require('path');const root=process.argv[2];
const pages=fs.readFileSync('/tmp/pages.txt','utf8').trim().split('\n');const out=[];
for(const p of pages){const html=fs.readFileSync(path.join(root,p),'utf8');const errs=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errs.push(String(e.message||e).slice(0,120)));
 const inl=html.replace(/<script([^>]*)src="(\/assets\/js\/[^"]+)"([^>]*)><\/script>/g,(m,a,src,b)=>{try{return '<script'+a+b+'>'+fs.readFileSync(path.join(root,src),'utf8')+'</script>';}catch(e){errs.push('missing script '+src);return m;}});
 const dom=new JSDOM(inl,{runScripts:'dangerously',virtualConsole:vc,pretendToBeVisual:true});const w=dom.window,d=w.document;w.Element.prototype.scrollIntoView=function(){};w.scrollTo=function(){};
 try{d.dispatchEvent(new w.Event('DOMContentLoaded'));}catch(e){errs.push('DCL '+e.message);}
 const t=d.querySelector('.nav-toggle'),m=d.querySelector('.nav-mobile');let menu='n/a';if(t&&m){t.click();menu=m.classList.contains('active')?'opens':'BROKEN';}
 const imgs=[...d.querySelectorAll('img')];const noalt=imgs.filter(i=>!i.getAttribute('alt')).length;
 const h1=d.querySelectorAll('h1').length;out.push({p,errs,menu,h1,imgs:imgs.length,noalt});}
fs.writeFileSync('/tmp/audit_pages.json',JSON.stringify(out));
