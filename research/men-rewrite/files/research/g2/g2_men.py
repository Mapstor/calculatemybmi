import re,json,html as H
exec(open("/home/claude/k3_patch2.py",encoding="utf-8").read().split("W_SHORT=")[0])
ENT.update({"×":"(?:×|&times;)","²":"(?:²|&sup2;|<sup>2</sup>)","<":"(?:<|&lt;)",">":"(?:>|&gt;)","≥":"(?:≥|&ge;)","“":"(?:“|&ldquo;|\")","”":"(?:”|&rdquo;|\")","–":"(?:–|&ndash;|-)","″":"(?:″|&Prime;|\")"})
P="men-bmi-calculator/index.html"
BF=json.load(open("research/body-fat/bf_results.json")); R=json.load(open("research/average-weight/avgw_results.json"))
NHLBI='<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">NHLBI</a>'
PROV='<a href="https://doi.org/10.1519/JSC.0000000000002449" target="_blank" rel="noopener">Provencher et al., 2018</a>'
fh=BF["f"]["by_bmi"]["18.5–24.9"]["q"][2]; mh=BF["m"]["by_bmi"]["18.5–24.9"]["q"][2]
s=open(P,encoding="utf-8").read()
# 1) repair two paragraphs whose text had been swallowed into a broken style attribute, drop the empty testosterone box
m=re.search(r'<p style="margin:0;font-size:0\. Testosterone drives this difference(?:(?!</p>).)*</p>',s,re.S); assert m
s=s.replace(m.group(0),f'<p style="margin:0;font-size:0.9375rem;">At the same BMI, men carry less fat and more lean mass than women: in CDC&rsquo;s body scans, men with a healthy BMI had a median of {mh:.1f}% body fat and women {fh:.1f}% (our analysis; see the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>). Because BMI only measures total weight relative to height, a muscular man can register as overweight with little body fat; our <a href="/blog/bmi-for-athletes/">BMI for athletes</a> guide explains why.</p>')
m=re.search(r'<p style="margin:0;font-size:0\.Athletes and other very muscular people(?:(?!</p>).)*</p>',s,re.S); assert m
s=s.replace(m.group(0),f'<p style="margin:0;font-size:0.9375rem;">Very muscular men can have a BMI in the overweight or obesity range while carrying little body fat. At the NFL Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat ({PROV}). Estimate yours with the <a href="/body-fat-calculator/">body fat calculator</a>.</p>')
m=re.search(r'<div style="[^"]*">\s*<h3[^>]*>4\. Testosterone(?:&#39;|\'|&rsquo;|’)s Role in Body Composition</h3>\s*</div>',s); assert m
s=s.replace(m.group(0),""); s=re.sub(r"5\. Why Waist Circumference Matters More for Men","4. Why Waist Circumference Matters for Men",s)
open(P,"w",encoding="utf-8").write(s); LOG.append((P,3,"broken boxes repaired"))
T(P,"Athletes often have misleading BMI — muscle weighs more than fat","Athletes often have misleading BMI — muscle is denser than fat")
s=open(P,encoding="utf-8").read()
m=re.search(r"Men are biologically predisposed to store excess fat viscerally(?:(?!</p>).)*</p>",s,re.S)
if m: s=s.replace(m.group(0),f"Men tend to store more fat around the abdomen than women do. That is the fat the US guidelines flag with the waist cut-off: above 40 inches (102 cm) counts as higher risk at any BMI ({NHLBI}). Two men with the same BMI can therefore carry very different risk; see our <a href=\"/blog/waist-to-height-ratio/\">waist-to-height ratio</a> guide.</p>"); LOG.append((P,1,"visceral box"))
else: MISS.append((P,"visceral"))
s=s.replace("Significantly elevated risk for heart disease, type 2 diabetes, and metabolic syndrome. Action recommended.","The US guidelines treat this as a sign of higher risk of heart disease and type 2 diabetes, whatever the BMI.")
s=s.replace("Waist circumference within recommended range. Continue maintaining through diet and exercise.","Below the NIH waist cut-off for men.")
open(P,"w",encoding="utf-8").write(s)
T(P,"For men, a WHR above 0.90 is associated with increased cardiovascular risk. A ratio below 0.90 is considered healthy.","A WHO expert consultation (2008) uses a WHR of 0.90 or more in men as the cut-off for substantially increased risk of metabolic complications.")
s=open(P,encoding="utf-8").read()
for pat,new in [(r"Men with a BMI over 25 have a significantly higher risk of developing heart disease, hypertension, and stroke\. Visceral fat -- common in men -- surrounds the heart and major blood vessels, contributing to arterial plaque buildup\.",
                 f"The US clinical guidelines link a BMI above the healthy range with higher risk of high blood pressure, coronary heart disease and stroke ({NHLBI})."),
                (r"Obstructive sleep apnea \(OSA\) affects men at roughly twice the rate of women\.(?:(?!</p>).)*</p>",f"The same guidelines list sleep apnea among the conditions linked to excess weight ({NHLBI}). Untreated sleep apnea is worth discussing with a doctor.</p>"),
                (r"Every extra pound of body weight adds approximately 4 pounds of pressure on the knee joints\.(?:(?!</p>).)*?(?=Read more about)",f"Osteoarthritis is on the NHLBI list of weight-related conditions ({NHLBI}). "),
                (r"being underweight \(BMI under 18\.5\) also carries health risks including weakened immunity, bone density loss, and nutritional deficiencies\. The goal should be to maintain a BMI and body composition that supports overall metabolic health\.","a BMI under 18.5 can reflect undernutrition or an underlying illness and is worth checking with a doctor."),
                (r"<li>You are experiencing symptoms of low testosterone such as fatigue, reduced muscle mass, low libido, or depression</li>",""),
                (r"<li>You are over 45 years old and have not had a comprehensive metabolic health assessment recently</li>",""),
                (r"See theguidance on BMI in adults\.",f"See the {NHLBI} guidance."),
                (r"Men tend to store fat around the abdomen \(visceral fat\), which is more strongly linked to heart disease, type 2 diabetes, and metabolic syndrome than subcutaneous fat stored in other areas\.",f"Men tend to store more fat around the abdomen, which the US guidelines treat as a separate risk signal from BMI ({NHLBI})."),
                (r"\(DEXA scan, hydrostatic weighing, or quality bioimpedance scales\)","(a DEXA scan or underwater weighing; at home, calipers come closest &mdash; see <a href=\"/blog/how-to-measure-body-fat/\">how accurate each method is</a>)")]:
    s2,n=re.subn(pat,new,s,flags=re.S)
    if n: s=s2; LOG.append((P,n,pat[:40]))
    else: MISS.append((P,pat[:50]))
# drop the unsourced testosterone FAQ
m=re.search(r'<div class="faq-item">\s*<button class="faq-question">Does BMI affect testosterone levels\?<svg.*?</button>\s*<div class="faq-answer">.*?</div>\s*</div>',s,re.S)
if m: s=s.replace(m.group(0),""); LOG.append((P,1,"testosterone FAQ dropped"))
else: MISS.append((P,"testosterone faq"))
# US men by the numbers
ag=R["men"]["age"]; rows="".join(f"<tr><th scope='row'>{g}</th><td>{ag[g]['bmi']['mean']:.1f}</td><td>{ag[g]['wt']['mean']:.0f}</td><td>{ag[g]['waist']['mean']:.1f}</td></tr>" for g in ['20–29','30–39','40–49','50–59','60–69','70–79','80+'])
SEC=(f'<section class="content-section" id="us-men"> <h2>US men by the numbers</h2> <p>Measured by CDC in 2021&ndash;2023: the average US man aged 20+ is 5&prime;9&Prime; and weighs 199.0 lb, with an average BMI of 29.4. Average body fat, from CDC&rsquo;s body scans, is 27.2% at ages 20&ndash;59.</p>'
     f"<div class='table-responsive'><table><caption>US men: average BMI, weight (lb) and waist (in) by age, 2021&ndash;2023</caption><thead><tr><th scope='col'>Age</th><th scope='col'>BMI</th><th scope='col'>Weight</th><th scope='col'>Waist</th></tr></thead><tbody>{rows}</tbody></table></div>"
     '<p style="font-size:0.875rem;color:var(--gray-500);">Sources: our calculation from CDC NHANES 2021&ndash;2023 (reproduces <a href="https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf" target="_blank" rel="noopener">NCHS Series 3 No. 50</a>); body fat: our NHANES 2011&ndash;2018 DXA analysis. More: <a href="/average-weight/">average weight by height</a>, <a href="/body-fat-percentage-chart/">body fat chart</a>.</p> </section>')
k=s.find("<h2>Why BMI Can Be Misleading for Men"); st=s.rfind("<section",0,k); assert st>0
s=s[:st]+SEC+" "+s[st:]
open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"US men section"))
print("applied:",len(LOG)); print("MISSES:",MISS)
