// node research/us-obesity-build/tools/widget_test.js us-obesity-statistics/index.html
// Extracts the widget's BMI rounding + category functions FROM THE BUILT PAGE and runs the site's boundary vectors.
const fs=require("fs"); const html=fs.readFileSync(process.argv[2],"utf8");
const r1src=(html.match(/function r1\(x\)\{[^}]*\}/)||[])[0], catsrc=(html.match(/function cat\(b\)\{[^}]*\}/)||[])[0];
if(!r1src||!catsrc){console.log("FAIL: widget functions not found in page");process.exit(1);}
const r1=new Function("x",r1src.replace(/^function r1\(x\)\{/,"").replace(/\}$/,""));
const cat=new Function("b",catsrc.replace(/^function cat\(b\)\{/,"").replace(/\}$/,""));
const N=["underweight","healthy","overweight","obesity","severe"]; let fail=0;
const T=[[69,124,"18.3","underweight"],[69,125,"18.5","healthy"],[69,168,"24.8","healthy"],[69,169,"25.0","overweight"],[69,202,"29.8","overweight"],
         [69,203,"30.0","obesity"],[69,236,"34.8","obesity"],[69,237,"35.0","obesity"],[69,270,"39.9","obesity"],[69,271,"40.0","severe"]];
for(const [h,lb,eb,ec] of T){const b=r1(lb*703/(h*h)),c=N[cat(b)],ok=b.toFixed(1)===eb&&c===ec;if(!ok)fail++;console.log(ok?"PASS":"FAIL",`${h} in ${lb} lb -> ${b.toFixed(1)} ${c}`);}
for(const [cm,kg,ec] of [[170,53.2,"underweight"],[170,54,"healthy"],[170,72,"healthy"],[170,72.4,"overweight"]]){const b=r1(kg/Math.pow(cm/100,2)),c=N[cat(b)],ok=c===ec;if(!ok)fail++;console.log(ok?"PASS":"FAIL",`${cm} cm ${kg} kg -> ${b.toFixed(1)} ${c}`);}
console.log(fail?`WIDGET: ${fail} FAIL`:"WIDGET: ALL PASS"); process.exit(fail?1:0);
