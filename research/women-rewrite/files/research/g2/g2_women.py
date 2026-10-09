import re,json,html as H
exec(open("/home/claude/k3_patch2.py",encoding="utf-8").read().split("W_SHORT=")[0])
ENT.update({"×":"(?:×|&times;)","²":"(?:²|&sup2;|<sup>2</sup>)","<":"(?:<|&lt;)",">":"(?:>|&gt;)","≥":"(?:≥|&ge;)","“":"(?:“|&ldquo;|\")","”":"(?:”|&rdquo;|\")","–":"(?:–|&ndash;|-)"})
P="women-bmi-calculator/index.html"
BF=json.load(open("research/body-fat/bf_results.json")); R=json.load(open("research/average-weight/avgw_results.json"))
NHLBI='<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">NHLBI</a>'
WINTER='<a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter et al., 2014</a>'
GAL='<a href="https://pubmed.ncbi.nlm.nih.gov/10966886/" target="_blank" rel="noopener">Gallagher et al., 2000</a>'
fh=BF["f"]["by_bmi"]["18.5–24.9"]["q"][2]; mh=BF["m"]["by_bmi"]["18.5–24.9"]["q"][2]
wpk=max(R["women"]["age"],key=lambda g:R["women"]["age"][g]["waist"]["mean"]); wpv=R["women"]["age"][wpk]["waist"]["mean"]
assert wpk=="50–59"
T(P,"At the same BMI, women typically carry a higher percentage of body fat than men, which supports hormone production and reproductive health. The relationship between BMI and body fat differs by sex (CDC NCHS).",
  f'At the same BMI, women carry more body fat than men. In CDC&rsquo;s body scans, women with a healthy BMI (18.5&ndash;24.9) had a median of {fh:.1f}% body fat, men {mh:.1f}% (our analysis; see the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>).')
T(P,"This gynoid fat distribution is actually associated with lower cardiovascular risk compared to abdominal fat.",f"Fat stored around the abdomen is what the US guidelines flag with a waist cut-off ({NHLBI}).")
T(P,"Together, these hormones mean women's weight can shift 2-6 lbs across a single menstrual cycle.","Together, these hormones mean weight can shift across a single menstrual cycle.")
T(P,"Water retention during the luteal phase (after ovulation) can add 2-6 lbs. This means a single BMI reading can vary by nearly a full point depending on cycle timing.","Water retention after ovulation can add weight temporarily, so a single BMI reading depends partly on cycle timing.")
T(P,"The NIH's weight management guidelines recommend combining BMI with waist circumference and, when possible, a body fat percentage measurement.",f"The US clinical guidelines assess BMI together with waist circumference and other risk factors ({NHLBI}).")
T(P,"Women in this age group should pay particular attention to their BMI if planning pregnancy, as pre-pregnancy BMI is one of the strongest predictors of pregnancy outcomes. Maintaining a healthy BMI supports regular ovulation, reduces complications during pregnancy, and supports long-term metabolic health.",
  "If you are planning a pregnancy, your pre-pregnancy BMI sets the recommended weight gain (see below).")
T(P,"As estrogen levels decline, fat redistributes from the hips and thighs to the abdomen. Even if your BMI stays the same, your body composition and health risks may change because of this shift to visceral (abdominal) fat. Waist circumference becomes an especially important metric during this stage.",
  f'In CDC&rsquo;s measurements, US women&rsquo;s average waist size is largest at ages 50&ndash;59 ({wpv:.1f} inches; see <a href="/age-bmi-calculator/">BMI by age</a>), so waist size is worth tracking alongside BMI around menopause.')
s=open(P,encoding="utf-8").read()
m=re.search(r"Whatever range you compare yourself against, resistance training to preserve mus[^<]*",s)
if m: s=s.replace(m.group(0),""); LOG.append((P,1,"resistance lever removed"))
else: MISS.append((P,"resistance lever"))
open(P,"w",encoding="utf-8").write(s)
T(P,"and the relationship between BMI and body fat differs between women and men (CDC NCHS), which is why relying on BMI alone can be misleading.","and at the same BMI women carry more fat than men (see above), which is why BMI alone can mislead.")
T(P,"Waist circumference is one of the simplest and most effective ways to assess abdominal fat, which is more metabolically dangerous than fat stored elsewhere in the body.",f"Waist circumference is a simple way to gauge abdominal fat, which the US guidelines treat as a separate risk signal from BMI ({NHLBI}).")
s=open(P,encoding="utf-8").read()
m=re.search(r"Two women with the same BMI can have very different health risk profiles(?:(?!</p>).)*</p>",s,re.S)
if m: s=s.replace(m.group(0),f"Two women with the same BMI can carry fat in different places. That is why the guidelines treat a waist above 35 inches (88 cm) as a sign of higher risk at any BMI ({NHLBI}).</p>"); LOG.append((P,1,"waist example"))
else: MISS.append((P,"waist example"))
# NIH measuring method: tape just above the hip bones
m=re.search(r"<li>[^<]*Find the midpoint between the top of your hip bone and the bottom of your ribcage\.[^<]*</li>",s)
if m: s=s.replace(m.group(0),"<li>Find the top of your hip bones; the tape goes just above them, around your middle.</li>"); LOG.append((P,1,"measure step"))
else: MISS.append((P,"measure step"))
s=s.replace("You are over 65 and your BMI is below 22","You are over 65 and your BMI is below 23 (the level below which mortality was higher in older adults in a large meta-analysis)")
open(P,"w",encoding="utf-8").write(s)
# FAQ answers
def faq_set(q,new):
    global s
    s=open(P,encoding="utf-8").read()
    m=re.search(r'(<button class="faq-question">'+re.escape(q)+r'<svg.*?</button>\s*<div class="faq-answer">)(.*?)(</div>)',s,re.S)
    if m: s=s.replace(m.group(0),m.group(1)+"<p>"+new+"</p>"+m.group(3),1); open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"faq "+q))
    else: MISS.append((P,"faq "+q))
def faq_drop(q):
    s=open(P,encoding="utf-8").read()
    m=re.search(r'<div class="faq-item">\s*<button class="faq-question">'+re.escape(q)+r'<svg.*?</button>\s*<div class="faq-answer">.*?</div>\s*</div>',s,re.S)
    if m: s=s.replace(m.group(0),"",1); open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"faq dropped "+q))
    else: MISS.append((P,"drop "+q))
faq_set("Is BMI calculated differently for women?",f'No. The formula is the same for everyone: weight in kilograms divided by height in meters squared, and so are the categories. What differs is body composition: in CDC&rsquo;s body scans, women with a healthy BMI had a median of {fh:.1f}% body fat and men {mh:.1f}%. Waist size and a body fat estimate add what BMI can&rsquo;t show; see our <a href="/body-fat-calculator/">body fat calculator</a>.')
faq_set("Does BMI change during menopause?",f'The calculation doesn&rsquo;t change. What can change is where fat is stored: in CDC&rsquo;s measurements, US women&rsquo;s average waist is largest at ages 50&ndash;59. The US guidelines treat a waist above 35 inches (88 cm) as a sign of higher risk at any BMI ({NHLBI}).')
faq_set("Why do women have higher body fat than men?",f'It is normal female physiology, and it shows in measured data: in CDC&rsquo;s body scans, the average woman aged 20&ndash;59 had 38.7% body fat and the average man 27.2%. The provisional healthy range for women aged 20&ndash;39 is 21&ndash;32.9%, versus 8&ndash;19.9% for men ({GAL}). See the <a href="/body-fat-percentage-chart/">body fat percentage chart</a> for every age.')
faq_set("What BMI is considered underweight for women?",f'A BMI below 18.5, the same cut-off for every adult (WHO and CDC); below 16 is severe thinness. In adults 65 and older, a large meta-analysis found higher mortality below a BMI of 23 ({WINTER}). If your BMI is low and you don&rsquo;t know why, talk to a doctor.')
faq_drop("How does birth control affect BMI?"); faq_drop("Does BMI affect fertility?")
# US women by the numbers (our verified data)
s=open(P,encoding="utf-8").read()
ag=R["women"]["age"]; rows="".join(f"<tr><th scope='row'>{g}</th><td>{ag[g]['bmi']['mean']:.1f}</td><td>{ag[g]['wt']['mean']:.0f}</td><td>{ag[g]['waist']['mean']:.1f}</td></tr>" for g in ['20–29','30–39','40–49','50–59','60–69','70–79','80+'])
SEC=(f'<section class="content-section" id="us-women"> <h2>US women by the numbers</h2> <p>Measured by CDC in 2021&ndash;2023: the average US woman aged 20+ is 5&prime;3.5&Prime; and weighs 171.8 lb, with an average BMI of 30.0; 41.3% have obesity. Average body fat, from CDC&rsquo;s body scans, is 38.7% at ages 20&ndash;59.</p>'
     f"<div class='table-responsive'><table><caption>US women: average BMI, weight (lb) and waist (in) by age, 2021&ndash;2023</caption><thead><tr><th scope='col'>Age</th><th scope='col'>BMI</th><th scope='col'>Weight</th><th scope='col'>Waist</th></tr></thead><tbody>{rows}</tbody></table></div>"
     '<p style="font-size:0.875rem;color:var(--gray-500);">Sources: our calculation from CDC NHANES 2021&ndash;2023 (reproduces <a href="https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf" target="_blank" rel="noopener">NCHS Series 3 No. 50</a>); obesity: <a href="https://www.cdc.gov/nchs/products/databriefs/db508.htm" target="_blank" rel="noopener">NCHS Data Brief 508</a>; body fat: our NHANES 2011&ndash;2018 DXA analysis. More: <a href="/average-weight/">average weight by height</a>, <a href="/body-fat-percentage-chart/">body fat chart</a>.</p> </section>')
k=s.find("<h2>How Women"); st=s.rfind("<section",0,k)
assert st>0
s=s[:st]+SEC+" "+s[st:]; open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"US women section"))
print("applied:",len(LOG)); print("MISSES:",MISS)
