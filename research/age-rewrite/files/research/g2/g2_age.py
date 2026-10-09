import re,json,html as H
P="age-bmi-calculator/index.html"; s=open(P,encoding="utf-8").read()
R=json.load(open("research/average-weight/avgw_results.json"))
BF=json.load(open("research/body-fat/bf_results.json"))
AG=['20–29','30–39','40–49','50–59','60–69','70–79','80+']
SER3="https://www.cdc.gov/nchs/data/series/sr_03/sr03-050.pdf"; DB508="https://www.cdc.gov/nchs/products/databriefs/db508.htm"
VOLPI="https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/"; WINTER="https://pubmed.ncbi.nlm.nih.gov/24452240/"; CDC="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
PAG=re.search(r'href="(https://odphp\.health\.gov/[^"]+)"',s).group(1); SLEEP=re.search(r'href="(https://archive\.cdc\.gov/[^"]+)"',s).group(1)
def ext(u,t): return f'<a href="{u}" target="_blank" rel="noopener noreferrer">{t}</a>'
def a(sx,g,k): return R[sx]["age"][g][k]["mean"]
rows="".join(f"<tr><th scope='row'>{g}</th><td>{a('men',g,'bmi'):.1f}</td><td>{a('men',g,'wt'):.0f}</td><td>{a('men',g,'waist'):.1f}</td><td>{a('women',g,'bmi'):.1f}</td><td>{a('women',g,'wt'):.0f}</td><td>{a('women',g,'waist'):.1f}</td></tr>" for g in AG)
pk_m=max(AG,key=lambda g:a('men',g,'wt')); pk_f=max(AG,key=lambda g:a('women',g,'wt'))
assert pk_m=='40–49' and pk_f=='50–59'
minb=min(min(a(sx,g,'bmi') for g in AG) for sx in ('men','women'))
assert minb>=25, "every age group averages overweight-range BMI"
bm,bf=BF["m"],BF["f"]
NEW1=f'''<!-- Average BMI by age (NHANES 2021-2023, rewritten 8 Oct 2026) -->
<section class="content-section" id="average-bmi-by-age"> <h2>Average BMI by age in the US</h2>
<p>These are the averages CDC measured in its national health survey, August 2021&ndash;August 2023: people weighed and measured, not self-reported. In every age group the average adult BMI is in the overweight range (25 or higher). Average weight peaks at ages {pk_m} for men and {pk_f} for women; average waist size peaks later for men, at 70–79.</p>
<div class="table-responsive"><table><caption>Average BMI, weight (lb) and waist (in) by age, US adults, 2021&ndash;2023</caption>
<thead><tr><th scope="col" rowspan="2">Age</th><th scope="colgroup" colspan="3">Men</th><th scope="colgroup" colspan="3">Women</th></tr><tr><th scope="col">BMI</th><th scope="col">Weight</th><th scope="col">Waist</th><th scope="col">BMI</th><th scope="col">Weight</th><th scope="col">Waist</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p style="font-size:0.875rem;color:var(--gray-500);">Source: our calculation from CDC NHANES August 2021&ndash;August 2023 exam files (adults 20+, pregnant women excluded, survey-weighted), which reproduces the published {ext(SER3,"NCHS reference data")}. Average weight by height and age: <a href="/average-weight/">average weight for men and women</a>.</p> </section>
<section class="content-section" id="what-changes"> <h2>What changes with age, and what doesn&rsquo;t</h2>
<p><strong>The cut-offs don&rsquo;t change.</strong> The adult categories (healthy weight 18.5 to under 25) apply at every age from 20 ({ext(CDC,"CDC")}).</p>
<p><strong>Body composition does.</strong> Muscle mass tends to fall by roughly 3&ndash;8% per decade after about age 30 ({ext(VOLPI,"Volpi et al., 2004")}), so the same BMI can mean more fat later in life. In CDC&rsquo;s body scans, average body fat rose from {bm["20-29"]["mean"]:.1f}% in men in their 20s to {bm["50-59"]["mean"]:.1f}% in their 50s, and from {bf["20-29"]["mean"]:.1f}% to {bf["50-59"]["mean"]:.1f}% in women (our calculation, NHANES 2011&ndash;2018; see the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>). Waist size, which in the tables above is larger in every age group from 30 on than at 20–29, is one way to see that change.</p>
<p><strong>Height matters too.</strong> BMI divides by height squared, so if your height drops, your BMI rises at the same weight: going from 5&prime;8&Prime; to 5&prime;6&Prime; adds about 1.5 BMI points at a BMI of 25. Use your current measured height.</p> </section>'''
NEW2=f'''<!-- Obesity by age + official guidance -->
<section class="content-section" id="obesity-by-age"> <h2>Obesity by age</h2>
<p>Obesity (BMI 30 or higher) was most common in middle age in 2021&ndash;2023: 35.5% at ages 20&ndash;39, 46.4% at 40&ndash;59 and 38.9% at 60 and older ({ext(DB508,"NCHS Data Brief 508")}). More detail: <a href="/us-obesity-statistics/">US obesity statistics</a>.</p> </section>
<section class="content-section" id="guidance"> <h2>Official guidance on activity and sleep</h2>
<p>The {ext(PAG,"Physical Activity Guidelines for Americans")} recommend 150&ndash;300 minutes of moderate-intensity aerobic activity a week plus muscle-strengthening on at least 2 days, and for older adults, activity that includes balance training. For sleep, the American Academy of Sleep Medicine and Sleep Research Society recommend at least 7 hours a night for adults 18&ndash;60 ({ext(SLEEP,"via CDC")}).</p> </section>'''
def faq(q,a): return f'<div class="faq-item"> <button class="faq-question">{q}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></button> <div class="faq-answer"><p>{a}</p></div></div>'
FLEGAL="https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/"
NEWFAQ=('<!-- FAQ --> <section class="content-section"> <h2>Frequently Asked Questions</h2> <div class="faq-list">'+
 faq("Does the healthy BMI range change with age?",f"No. The adult categories, including the healthy range of 18.5 to under 25, are the same at every age from 20 ({ext(CDC,'CDC')}). In adults 65 and older, a large meta-analysis found the lowest mortality across BMI 23&ndash;33 ({ext(WINTER,'Winter et al., 2014')}): an observational finding, not a different healthy range.")+
 faq("What is the average BMI by age?",f"In CDC&rsquo;s 2021&ndash;2023 survey it was between {min(a('men',g,'bmi') for g in AG):.1f} and {max(a('men',g,'bmi') for g in AG):.1f} for men and between {min(a('women',g,'bmi') for g in AG):.1f} and {max(a('women',g,'bmi') for g in AG):.1f} for women across the age groups, all in the overweight range. See the table above for each age group.")+
 faq("Is BMI less accurate for older adults?",f"It can miss more. BMI doesn&rsquo;t measure body fat, and because muscle mass tends to decline with age ({ext(VOLPI,'Volpi et al., 2004')}), an older adult can carry more fat at the same BMI. Waist size and body composition add information BMI can&rsquo;t.")+
 faq("Should older adults try to lose weight?",f"That is a decision to make with a clinician, who can weigh your health, function and medicines. Observational data in adults 65 and older link a BMI below 23 with higher mortality ({ext(WINTER,'Winter et al., 2014')}), which is one reason unintended weight loss is worth reporting to a doctor.")+
 faq("Does losing height change my BMI?","Yes. BMI divides weight by height squared, so a lower height gives a higher BMI at the same weight: from 5&prime;8&Prime; to 5&prime;6&Prime; adds about 1.5 points at a BMI of 25. Use your current measured height, not the height you had at 25.")+
 faq("What is the obesity paradox?",f"An observational finding: in some large cohort studies, people classed as overweight had similar or slightly lower all-cause mortality than those in the healthy range ({ext(FLEGAL,'Flegal et al., JAMA 2013')}). It is an association, not a recommendation to gain weight; see the section above.")+
 '</div> </section> ')
secs=[(m.start(),re.sub(r"<[^>]+>","",re.search(r'<h2[^>]*>(.*?)</h2>',s[m.start():m.start()+3000],re.S).group(1)).strip()) for m in re.finditer(r'<section class="content-section"[^>]*>',s)]
pos={t:p for p,t in secs}; order=[p for p,t in secs]
def end_of(t):
    i=order.index(pos[t]); return order[i+1] if i+1<len(order) else None
def span(t):
    st=pos[t]; st=s.rfind("<!--",0,st) if s.rfind("<!--",0,st)>s.rfind("</section>",0,st) else st
    return st,end_of(t)
rep=[(span("How Body Composition Changes with Age"),NEW1),(span("BMI by Decade: What to Expect at Every Age"),NEW2),(span("Healthy Weight Maintenance by Age: Practical Strategies"),""),(span("Frequently Asked Questions"),NEWFAQ)]
for (st,en),new in sorted(rep,key=lambda x:-x[0][0]):
    seg=s[st:en]; cut=seg.rfind("</section>")+len("</section>"); s=s[:st]+new+s[st+cut:]
# drop the FAQPage node (questions rewritten; site rule for rewritten pages)
def strip(m):
    d=json.loads(m.group(2))
    if isinstance(d,dict) and d.get("@type")=="FAQPage": return ""
    if isinstance(d,dict) and "@graph" in d:
        g=[n for n in d["@graph"] if n.get("@type")!="FAQPage"]
        if len(g)!=len(d["@graph"]): d["@graph"]=g; return m.group(1)+json.dumps(d,ensure_ascii=False)+m.group(3)
    return m.group(0)
s=re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',strip,s,flags=re.S)
s=re.sub(r"<title>.*?</title>","<title>BMI Calculator by Age &amp; Gender (kg or lbs): US Averages</title>",s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Calculate BMI by age and gender in kg or lbs. Adult cut-offs don’t change with age; see average BMI, weight and waist by age for US men and women (CDC data).">',s)
s=re.sub(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="BMI Calculator by Age &amp; Gender (kg or lbs)">',s)
s=s.replace("Calculate your BMI and see it against the standard adult range together with age-specific context.","Calculate your BMI in kg or lbs and see it against the adult range, with US averages for your age and sex.")
# (8 Oct) the 7-column table was later split into separate Women and Men tables for phones
open(P,"w",encoding="utf-8").write(s)
print("done; sections now:",[re.sub(r"<[^>]+>","",re.search(r'<h2[^>]*>(.*?)</h2>',s[m.start():m.start()+3000],re.S).group(1)).strip() for m in re.finditer(r'<section class="content-section"[^>]*>',s)])
