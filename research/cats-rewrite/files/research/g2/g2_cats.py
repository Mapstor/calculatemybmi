import re,json,html as H
exec(open("/home/claude/k3_patch2.py",encoding="utf-8").read().split("W_SHORT=")[0])
ENT.update({"×":"(?:×|&times;)","²":"(?:²|&sup2;)","<":"(?:<|&lt;)",">":"(?:>|&gt;)","≥":"(?:≥|&ge;)","“":"(?:“|&ldquo;|\")","”":"(?:”|&rdquo;|\")","–":"(?:–|&ndash;|-)"})
P="blog/bmi-categories/index.html"
NHLBI='<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">NHLBI</a>'
FLEGAL='<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/" target="_blank" rel="noopener">Flegal et al., JAMA 2013</a>'
WINTER='<a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter et al., 2014</a>'
WING='<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/" target="_blank" rel="noopener">Wing et al., 2011</a>'
HE111='<a href="https://www.cdc.gov/nchs/data/hestat/hestat111.htm" target="_blank" rel="noopener">NCHS Health E-Stat 111</a>'
PROV='<a href="https://doi.org/10.1519/JSC.0000000000002449" target="_blank" rel="noopener">Provencher et al., 2018</a>'
WHOFS='<a href="https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight" target="_blank" rel="noopener">World Health Organization. Obesity and overweight fact sheet</a>'
T(P,"The CDC Adult BMI Categories established the current BMI classification in a 1995 expert consultation, with refinements in a 2000 technical report. These categories are used worldwide as the standard reference for weight status assessment in adults aged 20 and older:",
  'The World Health Organization set out the current classification in a 1995 expert report and added the obesity classes in a 2000 technical report; the <a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" target="_blank" rel="noopener">CDC</a> uses the same cut-offs for adults aged 20 and older:')
T(P,"Normal BMI range: 18.5 – 24.9 is associated with the lowest health risk for most adults","Normal BMI range: 18.5 – 24.9, the CDC and WHO healthy-weight category")
# health-risk lists -> sourced paragraphs, section by section
s=open(P,encoding="utf-8").read()
NEW={"Category 1:":"<p>WHO classes a BMI below 16 as severe thinness. A BMI this low can reflect serious undernutrition or illness and needs prompt medical evaluation.</p>",
 "Category 2:":"<p>This is WHO&rsquo;s moderate-thinness grade. A doctor can look for the cause, which ranges from not eating enough to an underlying illness.</p>",
 "Category 3:":"",
 "Category 5:":f"<p>The US clinical guidelines on overweight and obesity link excess weight with higher risk of high blood pressure, high cholesterol, type 2 diabetes, coronary heart disease, stroke, gallbladder disease, osteoarthritis, sleep apnea and some cancers, with risk rising as BMI rises ({NHLBI}).</p>",
 "Category 6:":f"<p>The same NHLBI list applies, at higher risk than in the overweight range ({NHLBI}). Obesity is also linked to at least 13 types of cancer (see our <a href=\"/blog/bmi-and-health-risks/\">BMI and health risks</a> page for the list and sources).</p>",
 "Category 7:":f"<p>In a pooled analysis of 97 studies covering about 2.88 million people, all-cause mortality was about 29% higher at a BMI of 35 or more than in the healthy range (hazard ratio 1.29; {FLEGAL}).</p>",
 "Category 8:":f"<p>The 29% higher all-cause mortality reported for BMI 35 and above in the pooled analysis includes this class ({FLEGAL}); the risks listed for classes I and II apply here at their highest.</p>"}
heads=[(m.start(),m.group(1)) for m in re.finditer(r"<h2[^>]*>(Category \d:)[^<]*</h2>",s)]
for idx,(pos,key) in sorted(enumerate(heads),key=lambda x:-x[1][0]):
    end=heads[idx+1][0] if idx+1<len(heads) else s.find("<h2",pos+10)
    seg=s[pos:end]; m=re.search(r"<h3[^>]*>Health Risks</h3>\s*<ul[^>]*>.*?</ul>",seg,re.S)
    if m:
        seg2=seg.replace(m.group(0),NEW[key],1); s=s[:pos]+seg2+s[end:]; LOG.append((P,1,"risks "+key))
    elif NEW.get(key): MISS.append((P,"risk list "+key))
open(P,"w",encoding="utf-8").write(s)
T(P,"While the entire 18.5–24.9 range is classified as normal, research suggests the lowest mortality risk occurs around BMI 22–23 for younger adults. Some studies suggest slightly different optimal ranges for men (20–25) and women (19–24).",
  "The whole 18.5&ndash;24.9 range counts as healthy weight, for men and women alike.")
s=open(P,encoding="utf-8").read()
m=re.search(r"It is the single most common BMI category in the US adult population according to CDC NHANES data(?:(?!</p>).)*?\.(?=\s*</p>|\s)",s,re.S)
if m: s=s.replace(m.group(0),f"In 2021&ndash;2023, 31.7% of US adults were in this range (age-adjusted; {HE111}).",1); LOG.append((P,1,"most common"))
else: MISS.append((P,"most common"))
m=re.search(r"The overweight category is the most debated BMI classification\.(?:(?!</p>).)*</p>",s,re.S)
if m: s=s.replace(m.group(0),f"The overweight category is the most debated. In a pooled analysis of 97 studies, all-cause mortality in the overweight range was about 6% lower than in the healthy range (hazard ratio 0.94; {FLEGAL}); why is still argued over, and it is not a reason to aim for a higher BMI.</p>",1); LOG.append((P,1,"debate"))
else: MISS.append((P,"debate"))
m=re.search(r"For people in the upper end of this range \(BMI 28(?:–|&ndash;)29\.9\)(?:(?!</p>).)*?For a deeper exploration, see our",s,re.S)
if m: s=s.replace(m.group(0),"For a deeper exploration, see our",1); LOG.append((P,1,"upper overweight"))
else: MISS.append((P,"upper overweight"))
open(P,"w",encoding="utf-8").write(s)
T(P,"Theobesity topic page provides extensive background.","")
T(P,"Japan, China, and several other Asian nations have adopted modified cutoffs based on this","Several countries have since set lower cut-offs of their own")
T(P,"2000: The WHO published Technical Report 894, refining the classification with subgroups (severe, moderate, and mild thinness; obese classes I, II, and III) that remain in use today.",
  "2000: The WHO published Technical Report 894, which set out obesity classes I, II and III; the thinness grades come from its 1995 report.")
T(P,"Ensure adequate protein and micronutrient intake.","If you are losing weight without trying, mention it to a doctor.")
T(P,"Modest weight loss (5–10% of body weight) can move you back to the overweight category and produce measurable metabolic improvements.",f"In a large trial of adults with overweight or obesity and type 2 diabetes, losing 5&ndash;10% of body weight was linked to improvements in blood sugar, blood pressure and cholesterol within a year ({WING}).")
s=open(P,encoding="utf-8").read()
for pat,new in [(r"Visceral fat \(around organs\) is far more dangerous than subcutaneous fat \(under skin\)\.",f"Fat around the abdomen is linked to higher risk at any BMI, which is why US guidelines add a waist measurement ({NHLBI})."),
                (r"Standard cutoffs may underestimate risk in Asian populations and overestimate it in Black populations\.","For many Asian populations, risks rise at lower BMI values (WHO expert consultation, 2004)."),
                (r"This single measurement adds significant predictive value to your BMI category\.","US clinical guidelines use it alongside BMI for that reason."),
                (r"A person in the overweight BMI category with excellent metabolic health may face lower risk than someone at normal BMI with poor metabolic markers\.","BMI is one of several markers a doctor looks at."),
                (r"The health implications of your BMI category change with age\. What is concerning at 25 may be perfectly fine at 65\.","The categories are the same at every adult age."),
                (r"A stable BMI in the overweight range is generally less concerning than a rapidly rising BMI, even if the current number is lower\.","A single reading says less than the trend."),
                (r"For example, many NFL players have BMIs above 30, and Olympic sprinters often have BMIs of 25(?:–|&ndash;)28\.",f"At the NFL Scouting Combine, for example, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by measured body fat ({PROV})."),
                (r"Cohort studies typically report the lowest all-cause mortality near the middle of that range \(around BMI 22(?:–|&ndash;)23\) for younger and middle-aged adults;","In a pooled analysis of 97 studies, overweight was linked to slightly lower all-cause mortality than the healthy range and BMI 35+ to higher ({FLEGAL});".replace("{FLEGAL}",FLEGAL))]:
    s2,n=re.subn(pat,new,s)
    if n: s=s2; LOG.append((P,n,pat[:40]))
    else: MISS.append((P,pat[:50]))
# sources: two entries whose names were stripped earlier; WHO entry needs its link
s,n1=re.subn(r"<li>\s*\.\s*Obesity (?:—|&mdash;) symptoms and causes\.\s*</li>","",s)
s,n2=re.subn(r"<li>\s*\.\s*Class III obesity\.\s*</li>","",s)
s,n3=re.subn(r"<li>\s*World Health Organization\. Obesity and overweight fact sheet\.\s*</li>",f"<li>{WHOFS}.</li>",s)
LOG.append((P,(n1,n2,n3),"sources")); open(P,"w",encoding="utf-8").write(s)
print("applied:",len(LOG)); print("MISSES:",MISS)
