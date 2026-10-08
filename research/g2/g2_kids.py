import re,json
P="kids-bmi-calculator/index.html"; s=open(P,encoding="utf-8").read()
CDC_CAT="https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html"
CDC_GC="https://www.cdc.gov/growthcharts/"; CDC_EXT="https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm"
CDC_FACTS="https://www.cdc.gov/obesity/php/about/childhood-obesity-facts.html"
HE112="https://www.cdc.gov/nchs/data/hestat/hestat112.htm"
PAG=re.search(r'href="(https://odphp\.health\.gov/[^"]+)"',s).group(1)
AASM="https://pubmed.ncbi.nlm.nih.gov/27250809/"
WHO_GS="https://www.who.int/tools/child-growth-standards"
import math
js=open("assets/js/cdc-bmi-lms.js",encoding="utf-8").read()
def arr(sex,key):
    blk=js[js.index(sex+":"):]; m=re.search(key+r":\s*\[([^\]]*)\]",blk); return [float(x) for x in m.group(1).split(",")]
LMS={sx:{k:arr(sx,k) for k in ("agemos","L","M","S")} for sx in ("boys","girls")}
def bmi_at(sx,yrs,z):
    d=LMS[sx]; i=d["agemos"].index(yrs*12+0.5); L,M,S=d["L"][i],d["M"][i],d["S"][i]
    return M*(1+L*S*z)**(1/L) if abs(L)>1e-9 else M*math.exp(S*z)
Z5,Z85,Z95=-1.6448536,1.0364334,1.6448536
assert round(bmi_at("boys",2,0),1)==16.5 and round(bmi_at("girls",2,0),1)==16.4   # matches the CDC median table on the page
def ptable(sx,label):
    rows="".join(f"<tr><th scope='row'>{y}</th><td>{bmi_at(sx,y,Z5):.1f}</td><td>{bmi_at(sx,y,Z85):.1f}</td><td>{bmi_at(sx,y,Z95):.1f}</td></tr>" for y in range(2,20))
    return (f"<div class='table-responsive'><table><caption>{label.capitalize()}: BMI at each percentile, ages 2&ndash;19 (CDC)</caption><thead><tr><th scope='col'>Age</th><th scope='col'>5th<br><small>healthy from</small></th><th scope='col'>85th<br><small>overweight from</small></th><th scope='col'>95th<br><small>obesity from</small></th></tr></thead><tbody>{rows}</tbody></table></div>")
PCT_SEC=("<section class=\"content-section\" id=\"percentile-chart\"> <h2>BMI-for-age percentile chart for boys and girls</h2>"
 "<p>These are the BMI values where each category begins, at each birthday, calculated from the CDC LMS reference data the calculator uses (BMI at the 5th, 85th and 95th percentiles). For a 14-year-old girl, for example, a BMI between the 5th- and 85th-percentile values in her row is in the healthy-weight range. Between birthdays the cut-offs shift a little month by month, which the calculator accounts for.</p>"
 "<h3>Girls</h3>"+ptable("girls","girls")+"<h3>Boys</h3>"+ptable("boys","boys")+
 "<p style=\"font-size:0.875rem;color:var(--gray-500);\">Calculated from the CDC extended BMI-for-age LMS data files (2000 growth-chart reference); values at age in years + 0.5 months. Severe obesity begins at 120% of the 95th-percentile value or a BMI of 35.</p> </section>")
a=s.index("<!-- BMI Percentile Categories for Children -->"); b=s.index(" </div></main>",a)
old=s[a:b]
med=re.search(r'(<table[^>]*>(?:(?!</table>).)*?Boys \(50th %ile\).*?</table>)',old,re.S).group(1)
def ext(u,t): return f'<a href="{u}" target="_blank" rel="noopener noreferrer">{t}</a>'
cats="".join(f"<tr><td><strong>{c}</strong></td><td>{r}</td></tr>" for c,r in [("Underweight","Below the 5th percentile"),("Healthy weight","5th to less than the 85th percentile"),("Overweight","85th to less than the 95th percentile"),("Obesity","95th percentile or higher"),("Severe obesity","120% of the 95th percentile or higher, or a BMI of 35 or higher")])
new=f'''<!-- Kids BMI content (rewritten 8 Oct 2026: every claim sourced) -->
<section class="content-section"> <h2>How BMI works for children and teens</h2>
<p>For ages 2 through 19, BMI is calculated exactly as for adults, but it is judged differently: a child&rsquo;s BMI is compared with other children of the same age and sex on {ext(CDC_GC,"CDC growth charts")}, and the result is a <strong>percentile</strong>. Children&rsquo;s bodies change as they grow, and boys and girls change differently, so the fixed adult cut-offs don&rsquo;t work for them ({ext(CDC_CAT,"CDC")}).</p>
<div class="table-responsive"><table><caption>BMI-for-age weight categories, ages 2&ndash;19 (CDC)</caption><thead><tr><th scope="col">Category</th><th scope="col">BMI-for-age percentile</th></tr></thead><tbody>{cats}</tbody></table></div>
<p>A percentile is a ranking, not a grade. The 50th percentile is simply the middle: half of children of that age and sex have a lower BMI. Any percentile from the 5th to just under the 85th is in the healthy-weight category. Source: {ext(CDC_CAT,"CDC child and teen BMI categories")}.</p> </section>
{PCT_SEC}
<section class="content-section"> <h2>How this calculator works</h2>
<p>It converts your child&rsquo;s height and weight to BMI, then places that BMI on the CDC BMI-for-age reference for their exact age in months and sex, using the LMS method and the {ext(CDC_EXT,"CDC extended BMI-for-age data files")}. For children at or above the 95th percentile it also shows BMI as a percentage of the 95th percentile, which is how severe obesity is defined. It gives one snapshot; a pediatrician looks at how the percentile changes over time.</p> </section>
<section class="content-section"> <h2>Median BMI by age and sex</h2>
<p>The table shows the median (50th percentile) BMI for boys and girls at each age, from the CDC data files. Median BMI falls from age 2 to a low around ages 4&ndash;6 and then rises through the teens, which is why the same BMI can be high for a 5-year-old and low for a 15-year-old.</p>
{med}
<p style="font-size:0.875rem;color:var(--gray-500);">Source: CDC 2000 BMI-for-age growth charts, median (M) values from the {ext(CDC_EXT,"CDC extended BMI-for-age data files")}.</p> </section>
<section class="content-section"> <h2>How common is childhood obesity in the US?</h2>
<p>In CDC&rsquo;s measured survey for August 2021&ndash;August 2023, <strong>21.1%</strong> of children and teens aged 2&ndash;19 had obesity: 14.9% at ages 2&ndash;5, 22.1% at ages 6&ndash;11 and 22.9% at ages 12&ndash;19. Severe obesity affected 7.0%. In 1971&ndash;1974 the obesity figure was 5.2% ({ext(HE112,"NCHS Health E-Stat 112")}). Trends, sex and age breakdowns: <a href="/childhood-obesity-statistics/">childhood obesity statistics</a>.</p> </section>
<section class="content-section"> <h2>What childhood obesity is linked to</h2>
<p>CDC lists these as more likely in children with obesity: high blood pressure and high cholesterol; impaired glucose tolerance, insulin resistance and type 2 diabetes; breathing problems such as asthma and sleep apnea; joint problems and musculoskeletal discomfort; fatty liver disease, gallstones and reflux; anxiety and depression; low self-esteem; and social problems such as bullying and stigma. Children with obesity are also more likely to have obesity as adults ({ext(CDC_FACTS,"CDC childhood obesity facts")}).</p>
<p>CDC describes childhood obesity as having many contributing factors, including eating and physical-activity patterns, sleep routines, screen time, some medicines, genetics, and the places where children live, learn and play.</p> </section>
<section class="content-section"> <h2>Official guidance on activity and sleep</h2>
<p><strong>Physical activity.</strong> The {ext(PAG,"Physical Activity Guidelines for Americans")} recommend that children and adolescents aged 6&ndash;17 get at least 60 minutes of moderate-to-vigorous physical activity every day, including vigorous, muscle-strengthening and bone-strengthening activity on at least 3 days a week, and that children aged 3&ndash;5 be physically active throughout the day.</p>
<p><strong>Sleep.</strong> The American Academy of Sleep Medicine recommends 10&ndash;13 hours per 24 hours (including naps) at ages 3&ndash;5, 9&ndash;12 hours at ages 6&ndash;12 and 8&ndash;10 hours at ages 13&ndash;18; the American Academy of Pediatrics endorsed these recommendations ({ext(AASM,"Paruthi et al., J Clin Sleep Med 2016")}).</p> </section>
<section class="content-section"> <h2>When to talk to your child&rsquo;s doctor</h2>
<p>A single result is a starting point. Talk with your child&rsquo;s pediatrician if the result is in the underweight, overweight or obesity range, if the percentile has moved a lot since the last check, or if you are worried about your child&rsquo;s eating, growth or mood. The doctor can look at the growth trend and the whole child, which a calculator cannot.</p> </section>
<section class="content-section"> <h2>Frequently asked questions</h2> <div class="faq-list">
<div class="faq-item"> <button class="faq-question">Why do children use percentiles instead of the adult cut-offs?<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></button> <div class="faq-answer"><p>Because children&rsquo;s body fat changes as they grow, and differs between boys and girls. CDC compares a child&rsquo;s BMI with children of the same age and sex instead ({ext(CDC_CAT,"CDC")}).</p></div></div>
<div class="faq-item"> <button class="faq-question">What is a healthy BMI percentile for a child?<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></button> <div class="faq-answer"><p>The 5th to just under the 85th percentile. Below the 5th is underweight, the 85th to under the 95th is overweight, and the 95th or higher is obesity.</p></div></div>
<div class="faq-item"> <button class="faq-question">Should an 18- or 19-year-old use this calculator or the adult one?<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></button> <div class="faq-answer"><p>This one. CDC&rsquo;s child and teen BMI covers ages 2 through 19; the adult categories apply from age 20. Adults can use the <a href="/">standard BMI calculator</a>.</p></div></div>
<div class="faq-item"> <button class="faq-question">Does a high BMI percentile mean my child has too much body fat?<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></button> <div class="faq-answer"><p>Not necessarily. BMI does not measure body fat directly, so it is a screening measure; a pediatrician can assess it alongside growth, development and other checks. For measured body fat in US children aged 8&ndash;19, see our <a href="/body-fat-percentage-chart/">body fat percentage chart</a>.</p></div></div>
<div class="faq-item"> <button class="faq-question">How is severe obesity defined in children?<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></button> <div class="faq-answer"><p>A BMI at or above 120% of the 95th percentile for age and sex, or a BMI of 35 or higher. The calculator shows the percentage of the 95th percentile for children in the obesity range.</p></div></div>
</div> </section>
<section class="content-section"> <h2>Sources</h2> <ol class="cmb-sources">
<li>Centers for Disease Control and Prevention. {ext(CDC_CAT,"Child and Teen BMI Categories")}.</li>
<li>Centers for Disease Control and Prevention. {ext(CDC_GC,"Growth Charts")} and {ext(CDC_EXT,"extended BMI-for-age data files")}.</li>
<li>Fryar CD, et al. {ext(HE112,"Prevalence of overweight, obesity, and severe obesity among children and adolescents aged 2&ndash;19 years: United States, 1963&ndash;1965 through 2021&ndash;2023")}. NCHS Health E-Stats, 2026.</li>
<li>Centers for Disease Control and Prevention. {ext(CDC_FACTS,"Childhood Obesity Facts")}.</li>
<li>US Department of Health and Human Services. {ext(PAG,"Physical Activity Guidelines for Americans")}.</li>
<li>Paruthi S, et al. {ext(AASM,"Recommended Amount of Sleep for Pediatric Populations: A Consensus Statement of the American Academy of Sleep Medicine")}. J Clin Sleep Med 2016;12(6):785&ndash;6.</li>
</ol> </section>
<section class="content-section"> <h2>Related</h2> <ul>
<li><a href="/childhood-obesity-statistics/">Childhood obesity statistics</a></li><li><a href="/blog/bmi-by-age/">BMI by age</a></li><li><a href="/blog/bmi-categories/">BMI categories</a></li><li><a href="/blog/underweight-bmi-risks/">Underweight BMI risks</a></li><li><a href="/blog/bmi-limitations/">BMI limitations</a></li><li><a href="/body-fat-percentage-chart/">Body fat percentage chart (ages 8&ndash;59)</a></li><li><a href="/">Adult BMI calculator</a></li>
</ul> </section>
'''
s=s[:a]+new+s[b:]
# drop the FAQPage node (questions changed; site rule: no FAQPage markup on rewritten pages)
def strip(m):
    d=json.loads(m.group(2))
    if isinstance(d,dict) and d.get("@type")=="FAQPage": return ""
    if isinstance(d,dict) and "@graph" in d:
        d["@graph"]=[n for n in d["@graph"] if n.get("@type")!="FAQPage"]; return m.group(1)+json.dumps(d,ensure_ascii=False)+m.group(3)
    return m.group(0)
s=re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',strip,s,flags=re.S)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="BMI calculator for kids and teens aged 2–19: BMI-for-age percentile and CDC weight category by exact age and sex, plus percentile charts for boys and girls.">',s)
s=re.sub(r"<title>.*?</title>","<title>BMI Calculator for Kids &amp; Teens (Ages 2–19): CDC Percentile</title>",s,count=1)
s=s.replace("<h1>Pediatric BMI Calculator</h1>","<h1>BMI Calculator for Kids and Teens</h1>")
s=re.sub(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="BMI Calculator for Kids &amp; Teens (Ages 2–19)">',s)
open(P,"w",encoding="utf-8").write(s)
print("replaced chars:",len(old),"->",len(new),"| WHO GS url (verify):",WHO_GS)
