import re,json,html as H
exec(open("/home/claude/k3_patch2.py",encoding="utf-8").read().split("W_SHORT=")[0])
ENT.update({"×":"(?:×|&times;)","²":"(?:²|&sup2;)","<":"(?:<|&lt;)",">":"(?:>|&gt;)","≥":"(?:≥|&ge;)","“":"(?:“|&ldquo;|\")","”":"(?:”|&rdquo;|\")","–":"(?:–|&ndash;|-)"})
P="lean-body-mass/index.html"
VOLPI='<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/" target="_blank" rel="noopener">Volpi et al., 2004</a>'
def F(sex,kg,cm):
    if sex=="m": return 0.407*kg+0.267*cm-19.2, 1.1*kg-128*(kg/cm)**2, 0.32810*kg+0.33929*cm-29.5336
    return 0.252*kg+0.473*cm-48.3, 1.07*kg-148*(kg/cm)**2, 0.29569*kg+0.41813*cm-43.2933
s=open(P,encoding="utf-8").read()
# 1) rebuild the comparison table from the calculator's own equations (every printed value was wrong)
EX=[("m",175,75,"Male, 175 cm, 75 kg"),("m",183,95,"Male, 183 cm, 95 kg"),("f",163,58,"Female, 163 cm, 58 kg"),("f",170,80,"Female, 170 cm, 80 kg"),("m",168,60,"Male, 168 cm, 60 kg")]
i=s.find("Formula Comparison Table"); a=s.find("<tbody",i); b=s.find("</tbody>",a)
rows=""
for sx,cm,kg,lab in EX:
    bo,ja,hu=F(sx,kg,cm); sp=max(bo,ja,hu)-min(bo,ja,hu)
    rows+=f"<tr><td>{lab}</td><td>{bo:.1f} kg</td><td>{ja:.1f} kg</td><td>{hu:.1f} kg</td><td>{sp:.1f} kg</td></tr>"
tb_open=s[a:s.find(">",a)+1]
s=s[:a]+tb_open+rows+s[b:]; LOG.append((P,1,"table rebuilt"))
# remove the figure that plotted the wrong table values
m=re.search(r"<figure\b(?:(?!</figure>).)*?Formula-to-formula agreement is tight(?:(?!</figure>).)*?</figure>",s,re.S)
if m: s=s.replace(m.group(0),""); LOG.append((P,1,"wrong-data figure removed"))
else: MISS.append((P,"figure"))
open(P,"w",encoding="utf-8").write(s)
T(P,"As the table shows, the formulas tend to agree most closely for individuals of average height and weight, but diverge more for heavier or more extreme body types. The James formula in particular tends to produce higher LBM estimates for heavier individuals, which may overestimate lean mass in those",
  "In these examples the Hume equation gives the lowest value every time, and the three equations differ by 1.4&ndash;6.3 kg: little for the two women, more for the men. They are estimates from height and weight only, so the spread is a reminder of how uncertain any single number is, especially for")
# 2) claims about the formulas
T(P,"It is one of the most widely cited and validated formulas for LBM estimation in clinical and fitness settings.","Boer developed it to normalise body fluid volumes, as the title of his 1984 paper says.")
T(P,"This reflects the biological reality that men tend to carry proportionally more of their lean mass as muscle","The coefficients differ because the equations were fitted separately for men and women")
T(P,"The Boer formula is generally considered one of the most balanced options. The James formula (1976) tends to overestimate LBM in heavier individuals, while the Hume formula (1966) can underestimate LBM in shorter individuals.",
  "The three equations can give noticeably different answers for the same person; the comparison table below shows how much.")
s=open(P,encoding="utf-8").read()
m=re.search(r"Studies have shown that the Boer formula provides estimates closest to DEX[^<]*",s)
if m: s=s.replace(m.group(0),""); LOG.append((P,1,"closest to DEXA"))
else: MISS.append((P,"closest to DEXA"))
open(P,"w",encoding="utf-8").write(s)
T(P,"Developed by P. Boer and validated against body composition data. Provides a good balance between accuracy and simplicity, performing well across a wide range of body sizes.","Published by P. Boer in 1984 in the American Journal of Physiology.")
T(P,"Developed by R. Hume and E. Weyers, this formula takes a similar linear approach to the Boer formula but with different coefficients. It was one of the first to use both height and weight as predictors.",
  "Published by R. Hume in 1966 in the Journal of Clinical Pathology. Like Boer&rsquo;s, it is linear in height and weight, with different coefficients.")
# Peters (children) section: not used by the calculator and unsourced -> remove h3 + paragraph + list
s=open(P,encoding="utf-8").read()
m=re.search(r"<h3[^>]*>Peters Formula \(for Children\)</h3>.*?</ul>",s,re.S)
if m: s=s.replace(m.group(0),""); LOG.append((P,1,"Peters removed"))
else: MISS.append((P,"Peters"))
s=s.replace("Primary sources for the equations used by this calculator. Deep links to journal pages are pending — please contact us if you can point to an authoritative online copy of any of the above.","Primary sources for the equations used by this calculator.")
s=s.replace("Primary sources for the equations used by this calculator. Deep links to journal pages are pending &mdash; please contact us if you can point to an authoritative online copy of any of the above.","Primary sources for the equations used by this calculator.")
open(P,"w",encoding="utf-8").write(s)
# 3) body fat vs BMI section + ACE caption
T(P,"Schematic. See the men's / women's body-fat category tables below for the ACE-sourced ranges that would apply to each split.","Schematic: the same weight split into different amounts of lean and fat mass.")
T(P,"The relationship between BMI and body fat differs by sex, age, and race and Hispanic origin (CDC NCHS), so the same BMI can mean quite different body compositions.",
  'In CDC&rsquo;s body scans, the same BMI corresponds to different body fat in men and women and at different ages (our analysis; see the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>), so the same BMI can mean quite different body compositions.')
T(P,"Understanding where you fall in these categories is far more informative than BMI categories alone.","Comparing your body fat with what is typical for your age and sex tells you more than a BMI category alone.")
T(P,"Values are approximate ranges based on normal BMI weight ranges (18.5-24.9) applied to the Boer formula. Trained individuals may exceed the high values significantly. Use our ideal weight calculator to determine your target weight range.","")
# 4) why-LBM-matters claims
s=open(P,encoding="utf-8").read()
m=re.search(r"Many medications are dosed based on lean body mass rather than total body weight\.(?:(?!</p>).)*</p>",s,re.S)
if m: s=s.replace(m.group(0),"Some drug doses are calculated from lean or ideal body weight rather than total weight, because fat and lean tissue handle many drugs differently. Which weight to use depends on the drug, so this is a decision for the prescriber.</p>"); LOG.append((P,1,"drug dosing"))
else: MISS.append((P,"drug dosing"))
m=re.search(r"Protein requirements are most accurately calculated based on lean body mass(?:(?!</p>).)*</p>",s,re.S)
if m: s=s.replace(m.group(0),"Some clinicians express protein needs relative to lean mass rather than total weight. How much you need depends on age, size, health and activity, so targets are best set with a clinician or registered dietitian.</p>"); LOG.append((P,1,"protein target removed"))
else: MISS.append((P,"protein"))
m=re.search(r"Tracking LBM over time is far more useful than tracking weight[^<]*",s)
if m: s=s.replace(m.group(0),"Tracking body composition can show changes that the scale hides."); LOG.append((P,1,"athletes"))
s=s.replace("; crash dieting often costs lean mass.",".")
s=s.replace("then use less expensive methods (BIA or calipers) to track","then use less expensive methods (calipers or a lab impedance analyzer; see <a href=\"/blog/how-to-measure-body-fat/\">how accurate each method is</a>) to track")
open(P,"w",encoding="utf-8").write(s)
# 5) FAQ answers
T(P,"Skeletal muscle mass is just one component of LBM, typically making up about 40-50% of total LBM in healthy adults.","Skeletal muscle is the largest single component of LBM, but not all of it.")
T(P,"This decline contributes to reduced metabolic rate (why it becomes easier to gain fat with age), decreased strength, impaired balance, and increased fall risk. However, resistance training can significantly slow or even reverse this process at any age. Studies show that even people in their 70s and 80s can build meaningful muscle mass with consistent training.",
  "Muscle-strengthening activity is part of the Physical Activity Guidelines at every adult age, including for older adults.")
T(P,"This essential lipid component accounts for roughly 2-3% of body weight.","")
print("applied:",len(LOG)); print("MISSES:",MISS)
