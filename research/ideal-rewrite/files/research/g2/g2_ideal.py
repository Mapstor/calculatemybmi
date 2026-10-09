import re,json,html as H
from decimal import Decimal, ROUND_HALF_UP
exec(open("/home/claude/k3_patch2.py",encoding="utf-8").read().split("W_SHORT=")[0])   # reuse rx()/T() helpers, LOG, MISS
P="ideal-weight/index.html"
PAI='<a href="https://pubmed.ncbi.nlm.nih.gov/10981254/" target="_blank" rel="noopener">Pai &amp; Paloucek, 2000</a>'
PET='<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4841935/" target="_blank" rel="noopener">Peterson et al., 2016</a>'
CDC='<a href="https://www.cdc.gov/bmi/about/index.html" target="_blank" rel="noopener">CDC</a>'
WING='<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/" target="_blank" rel="noopener">Wing et al., 2011</a>'
T(P,"The most widely used ideal body weight formula in clinical practice. Dr. B.J. Devine originally published this formula to calculate drug dosages -- specifically aminoglycoside antibiotics -- where dosing needed to be based on lean body weight rather than total weight. Despite its pharmaceutical origins, it became the de facto standard for ideal body weight estimation.",
  f"Dr. B.J. Devine published these equations in a 1974 article on dosing the antibiotic gentamicin. They became the most cited ideal body weight equations: by 2000, more than 200 articles had cited them ({PAI}).")
T(P,"Dr. J.D. Robinson and colleagues published this formula in 1983 as a revised estimate of ideal body weight, attempting to correct some of the perceived overestimation in the Devine formula, especially for women. It uses a slightly lower per-inch increment for women.",
  f"Dr. J.D. Robinson and colleagues published this equation in 1983, derived by regression analysis of height&ndash;weight data. It came out strikingly similar to Devine&rsquo;s ({PAI}). It uses a lower per-inch increment, especially for women.")
T(P,"With a baseline of 56.2 kg for men and 53.1 kg for women, the Miller formula gives the most \"generous\" ideal weight for people of average height. It was designed to reflect that many healthy people weigh more than Devine's estimates.",
  f"With a baseline of 56.2 kg for men and 53.1 kg for women, the Miller equation gives the highest results at shorter heights; at taller heights the other equations overtake it. Miller and colleagues derived it from the 1983 Metropolitan Life height&ndash;weight tables ({PAI}).")
T(P,"It uses a straightforward pounds-based calculation and remains popular due to its simplicity. The Hamwi formula tends to give the widest spread between results for short versus tall people because of its relatively high per-inch increment.",
  "In pounds it is 100 lb for women and 106 lb for men at 5 feet, plus 5 lb (women) or 6 lb (men) per inch above that.")
T(P,"A more precise method used in clinical settings. Extend your arm forward, bend the forearm upward at a 90-degree angle, and use a caliper or ruler to measure the widest point across your elbow joint. Compare to age- and sex-specific reference tables. Generally:",
  f"The 1983 Metropolitan Life tables defined frame size by elbow breadth: with the forearm bent upward at 90 degrees, the width across the elbow is compared with height-specific reference values ({PAI}).")
s=open(P,encoding="utf-8").read(); m=re.search(r"<ul[^>]*>(?:(?!</ul>).)*?Elbow breadth less than 2\.25(?:(?!</ul>).)*?</ul>",s,re.S)
if m: s=s.replace(m.group(0),""); open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"elbow thresholds list removed"))
else: MISS.append((P,"elbow list"))
T(P,"A 5'8\" woman could have an ideal weight of about 137 lbs according to the averaged formulas. But the healthy BMI range for this height spans from approximately 122 to 164 lbs. That is a 42-pound window in which a person can be considered medically healthy. The single \"ideal\" number falls roughly in the middle of that range, but aiming for an exact number can lead to unnecessary frustration and unhealthy behaviors.",
  "For a 5&prime;8&Prime; woman, the four equations average about 140 lbs. The healthy BMI range at that height runs from about 122 to 164 lbs, a 42-pound window. The single formula number sits inside that range, but it is one point in it, not the only healthy weight.")
T(P,"The modern concept of ideal weight began with the Metropolitan Life Insurance Company in the 1940s. MetLife analyzed mortality data from millions of policyholders and published \"desirable weight\" tables based on height and frame size. These tables defined the weight range associated with the lowest mortality risk. While groundbreaking for their time, they were based almost entirely on white, middle-class Americans who could afford life insurance, introducing significant demographic bias.",
  f"The idea of a &ldquo;desirable&rdquo; or &ldquo;ideal&rdquo; weight comes from insurance height&ndash;weight tables: weight data from these tables were found to correlate with mortality, which led to those terms ({PAI}).")
T(P,"Dr. G.J. Hamwi published the first simplified formula as a quick clinical tool. Rather than requiring clinicians to look up tables, the Hamwi formula allowed a rapid mental calculation. It was never intended to be a precise assessment -- just a convenient rule-of-thumb for busy doctors. Despite its simplicity, it remained in widespread use for decades.",
  "Dr. G.J. Hamwi published a quick clinical rule of thumb in 1964, so clinicians could estimate a weight without looking up tables.")
T(P,"The Devine formula emerged from pharmacology, not weight management. Dr. B.J. Devine needed a way to calculate appropriate drug doses for patients, since many medications should be dosed based on lean body mass rather than total weight. The formula quickly spread beyond pharmacology and became the most cited ideal body weight equation in medical literature. Ironically, Devine himself never published validation data for the formula.",
  f"The Devine equations came from pharmacology: they appeared in a 1974 article on gentamicin dosing, and Pai and Paloucek found them consistent with an older rule of thumb developed from height&ndash;weight tables ({PAI}). They became the most cited ideal body weight equations.")
T(P,"By the 1980s, researchers recognized that the Devine formula might not be the best estimate for all populations. Robinson et al. And Miller et al. Independently published revised formulas in the same year, each attempting to better represent the relationship between height and ideal weight. The Robinson formula aimed to correct perceived biases in the Devine formula, while the Miller formula used a different mathematical approach that produced higher baseline weights.",
  f"In 1983, Robinson et al. and Miller et al. independently derived equations from height&ndash;weight data. Both turned out strikingly similar to Devine&rsquo;s, which Pai and Paloucek explain by the general agreement among the height&ndash;weight tables they all came from ({PAI}).")
T(P,"Today, these formulas persist in clinical practice primarily due to inertia and convenience. Modern medicine increasingly favors BMI ranges, body composition analysis, and metabolic health markers over single-number ideal weight targets. Guidance from major health organisations increasingly favours using multiple metrics rather than relying on any single measure.",
  f"Today the equations are still used in clinical drug dosing. For judging a healthy weight, the BMI range is the standard ({CDC}). As reviewed by Peterson and colleagues, the equations don&rsquo;t line up with BMI: compared with a fixed BMI, they give too little weight at shorter heights and too much at taller heights ({PET}).")
T(P,"These formulas were developed primarily from data on Caucasian populations in Western countries. They may not accurately reflect ideal weights for people of Asian, African, Hispanic, or other ethnic backgrounds, whose body composition and bone density patterns can differ significantly. Our BMI accuracy article discusses similar concerns.",
  f"The equations come from US height&ndash;weight tables ({PAI}) and take no account of ethnicity, age or body composition.")
T(P,"All four formulas use 5'0\" (60 inches) as their baseline and are mathematically undefined or unreliable for heights below this. They also become less reliable at extreme heights. If you are very short or very tall, the formulas may not give useful results.",
  f"All four equations start at 5 feet (60 inches) and add weight for each inch above that, so they were not written for shorter heights. Toward the extremes of height they also drift away from the BMI-based healthy range ({PET}).")
T(P,"Surprisingly, most of these formulas were never validated against actual health outcomes. The Devine formula, the most widely used, was published without supporting data. They persist in practice due to convenience and tradition rather than proven accuracy.",
  f"Pai and Paloucek concluded that, because the equations come from similar height&ndash;weight tables, any one of them may be used to estimate ideal body weight ({PAI}). That makes them interchangeable estimates, not health targets.")
T(P,"These provide far more useful information about health risk than any height-based weight formula.","These add information about body composition and fat distribution that a height-based formula cannot.")
T(P,"Each formula was developed by different researchers using different populations and methodologies. The Devine formula (1974) was originally created for drug dosing. The Robinson (1983) and Miller (1983) formulas were published as corrections to Devine's estimates. The Hamwi formula (1964) is the oldest and was designed as a quick clinical rule-of-thumb. They use different baseline weights and different per-inch increments, so the results diverge -- especially at heights far from the 5'0\" baseline. Using the average of all four gives a more balanced, robust estimate.",
  f"Each uses a different starting weight and a different amount per inch. They come from similar US height&ndash;weight tables, so they agree closely near 5 feet and drift apart at taller heights ({PAI}). The calculator shows all four and their average.")
T(P,"No single formula has been proven to be the most accurate. The Devine formula is the most widely used in clinical settings, but this is largely due to historical inertia rather than superior accuracy. Research by Pai and Paloucek (2000) compared the formulas and found that the Robinson formula tended to give results closest to the middle of the BMI healthy range for average-height individuals. The Miller formula tends to be most \"generous,\" giving higher ideal weights. Our approach of averaging all four formulas provides a more robust estimate than relying on any single one.",
  f"None has been shown to be more accurate than the others. Pai and Paloucek concluded that, because all four come from similar height&ndash;weight tables, any one of them may be used ({PAI}). The calculator shows each result and the average.")
T(P,"The formulas themselves do not account for age, but in reality, your optimal weight does shift as you age. After age 30, adults lose an estimated 3–8% of muscle mass per decade (a process called sarcopenia; Volpi et al., 2004). Bone density also decreases, especially after menopause in women.",
  'The formulas don&rsquo;t account for age. Muscle mass tends to decline after about age 30, by an estimated 3&ndash;8% per decade (sarcopenia; <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC2804956/" target="_blank" rel="noopener">Volpi et al., 2004</a>).')
T(P,"Second, if you genuinely need to lose or gain weight, research shows that even modest changes of 5-10% of body weight can significantly improve metabolic health markers.",
  f"Second, in a large trial of adults with overweight or obesity and type 2 diabetes, losing 5&ndash;10% of body weight was linked to improvements in blood sugar, blood pressure and cholesterol within a year ({WING}).")
s=open(P,encoding="utf-8").read(); s=s.replace('href="/blog/overweight-bmi-risks/"','href="/blog/bmi-and-health-risks/"')
# resources: drop the two entries whose names were stripped earlier, link WHO, correct the PMC paper
s,n1=re.subn(r'<li>\s*(?:<strong>)?\s*(?:</strong>)?\s*--\s*Health Information\s*--.*?</li>','',s,flags=re.S)
s,n2=re.subn(r'<li>\s*(?:<strong>)?\s*(?:</strong>)?\s*--\s*guidelines on fitness.*?</li>','',s,flags=re.S)
s,n3=re.subn(r'WHO -- Obesity and Overweight Fact Sheet','<a href="https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight" target="_blank" rel="noopener">WHO -- Obesity and Overweight Fact Sheet</a>',s,count=1)
s,n4=re.subn(r'<a href="https://pmc\.ncbi\.nlm\.nih\.gov/articles/PMC4890841/"([^>]*)>[^<]*</a>(\s*--[^<]*)?',r'<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4841935/"\1>Peterson et al., Am J Clin Nutr 2016</a> -- Universal equation for estimating ideal body weight and body weight at any BMI',s)
s,n5=re.subn(r"Miller DR, Carlson JD, Loyd BJ, Day BM\. Determining ideal body weight\. <em>American Journal of Hospital Pharmacy</em>\. 1983;40\(11\):1806&ndash;1808\.|Miller DR, Carlson JD, Loyd BJ, Day BM\. Determining ideal body weight\. (?:<em>)?American Journal of Hospital Pharmacy(?:</em>)?\. 1983;40\(11\):1806(?:–|&ndash;)1808\.",
              "Miller DR, Carlson JD, Loyd BJ, Day BJ. Determining ideal body weight (and mass). <em>American Journal of Hospital Pharmacy</em>. 1983;40:1622&ndash;1625.",s)
s=s.replace("Deep links to journal pages are pending — please contact us if you can point to an authoritative online copy of any of the above.",f"Background on how the four equations relate: {PAI}.").replace("Deep links to journal pages are pending &mdash; please contact us if you can point to an authoritative online copy of any of the above.",f"Background on how the four equations relate: {PAI}.")
open(P,"w",encoding="utf-8").write(s); LOG.append((P,(n1,n2,n3,n4,n5),"resources/refs"))
# rebuild the missing by-height chart (the table had been removed, leaving "The table below" with nothing below)
def avg(sex,h):
    d=h-60; v=[50+2.3*d,52+1.9*d,56.2+1.41*d,48+2.7*d] if sex=="m" else [45.5+2.3*d,49+1.7*d,53.1+1.36*d,45.5+2.2*d]
    return sum(v)/4
def bmi_r(lb,hin): return float(Decimal(lb*703/hin**2).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP))
def band(hin):
    ok=[lb for lb in range(60,400) if 18.5<=bmi_r(lb,hin)<=24.9]; return ok[0],ok[-1]
def lbkg(kg): return f"{round(kg*2.20462)} lb <small>({kg:.0f} kg)</small>"
def table(sex,hs,label):
    rows=""
    for h in hs:
        a=avg(sex,h); lo,hi=band(h)
        rows+=f"<tr><th scope='row'>{h//12}&prime;{h%12}&Prime;</th><td>{lbkg(a*0.9)}</td><td><strong>{lbkg(a)}</strong></td><td>{lbkg(a*1.1)}</td><td>{lo}&ndash;{hi}</td></tr>"
    return (f"<h3>{label}</h3><div class='table-responsive'><table><caption>{label}: ideal weight by height (average of 4 equations, &plusmn;10% frames)</caption>"
            f"<thead><tr><th scope='col'>Height</th><th scope='col'>Small frame</th><th scope='col'>Medium frame</th><th scope='col'>Large frame</th><th scope='col'>BMI 18.5&ndash;24.9<br><small>(lb)</small></th></tr></thead><tbody>{rows}</tbody></table></div>")
assert round(avg("f",68)*2.20462)==140 and band(68)==(122,164)
CH=table("f",range(60,73),"Women")+table("m",range(62,79),"Men")+"<p style=\"font-size:0.8125rem;color:var(--gray-600);\">Medium frame = average of the four equations; small and large frame = 10% below and above, the rule of thumb described by Pai &amp; Paloucek (2000). Healthy BMI range = whole-pound weights with a BMI of 18.5 to 24.9 (CDC), for comparison.</p>"
s=open(P,encoding="utf-8").read()
k=s.find('For comparison, our <a href="/average-weight/">average weight for men and women</a> page shows what US adults actually weigh at each height.</p>')
assert k>0; k=s.find("</p>",k)+4
s=s[:k]+CH+s[k:]
s=s.replace("The table below shows ideal weight ranges for both men and women at various heights.","The tables below show ideal weight by height for women and men.")
s=s.replace("Note: These ranges are approximations derived from averaged formula outputs adjusted for frame size.","Note: These are formula estimates, not targets.")
open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"chart rebuilt"))
print("applied:",len(LOG)); print("MISSES:",MISS)
