import re,json,html as H
from decimal import Decimal, ROUND_HALF_UP
exec(open("/home/claude/k3_patch2.py",encoding="utf-8").read().split("W_SHORT=")[0])
P="index.html"
NHLBI='<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">NHLBI</a>'
WINTER='<a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter et al., 2014</a>'
WING='<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/" target="_blank" rel="noopener">Wing et al., 2011</a>'
WHO04='<a href="https://pubmed.ncbi.nlm.nih.gov/14726171/" target="_blank" rel="noopener">WHO expert consultation</a>'
CDCB='<a href="https://www.cdc.gov/bmi/about/index.html" target="_blank" rel="noopener">CDC</a>'
# --- "Health Risks by BMI Category": replace the three unsourced lists with a sourced summary
s=open(P,encoding="utf-8").read()
i=s.index("Health Risks by BMI Category</h2>"); a=s.index("</h2>",i)+5; nxt=s.index("<h2",a); b=s.rfind("</section>",a,nxt)
assert b>a
new=(f'<p>BMI is a screening measure: it flags higher or lower risk across a population, not a diagnosis for one person.</p>'
 f'<h3>Underweight (BMI under 18.5)</h3><p>A low BMI can reflect undernutrition or an underlying illness, so it is worth checking with a doctor if it is not explained. In adults 65 and older, a large meta-analysis found higher mortality below a BMI of 23 ({WINTER}). More in our <a href="/blog/underweight-bmi-risks/">underweight BMI risks</a> guide.</p>'
 f'<h3>Overweight and obesity (BMI 25 and over)</h3><p>The US clinical guidelines on overweight and obesity link excess weight with higher risk of high blood pressure, high cholesterol, type 2 diabetes, coronary heart disease, stroke, gallbladder disease, osteoarthritis, sleep apnea and some cancers ({NHLBI}). In a large trial of adults with overweight or obesity and type 2 diabetes, losing 5&ndash;10% of body weight was linked to improvements in blood sugar, blood pressure and cholesterol within a year ({WING}). The full picture, with sources: <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>.</p>')
s=s[:a]+new+s[b:]; open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"health risks section"))
# --- Learn About BMI
T(P,"According to the Centers for Disease Control and Prevention (CDC), BMI is used because it correlates reasonably well with more direct measures of body fat, such as underwater weighing and dual-energy X-ray absorptiometry (DEXA).",
  f"According to the {CDCB}, BMI is moderately correlated with more direct measures of body fat.")
T(P,"Research published by the National Heart, Lung, and Blood Institute (NHLBI) demonstrates that as BMI increases above the normal range, so does the risk of cardiovascular disease, type 2 diabetes, hypertension, and certain cancers.",
  f"The US clinical guidelines from the National Heart, Lung, and Blood Institute ({NHLBI}) link a BMI above the healthy range with higher risk of high blood pressure, type 2 diabetes, heart disease, stroke and some cancers.")
T(P,"For those looking to understand their ideal weight target, our healthy BMI range guide provides detailed information about optimal weight ranges for different populations.",
  'Our <a href="/blog/healthy-bmi-range/">healthy BMI range guide</a> shows the healthy weight range for every height.')
T(P,"Additionally, BMI doesn't account for fat distribution, and research from the National Institutes of Health (NIH) shows that abdominal fat (visceral fat) poses greater health risks than fat stored in other areas.",
  f"Additionally, BMI doesn&rsquo;t account for fat distribution; the {NHLBI} guidelines treat a large waist as a sign of higher risk at any BMI.")
T(P,"The WHO Western Pacific Region uses a lower overweight cutoff (23 rather than 25) for Asian populations.",
  f"For Asian populations, a {WHO04} identified BMI 23 and 27.5 as public-health action points.")
T(P,"Weight loss for health benefits Source: NHLBI","Weight loss linked to health benefits Source: Wing et al., 2011")
# --- metrics comparison table
T(P,"Strong predictor of metabolic risk, easy to measure","Linked to metabolic risk (NIH cut-offs), easy to measure")
T(P,"Better predictor of heart disease than BMI alone","Shows where fat is stored")
T(P,"Gold standard accuracy, regional breakdown, tracks changes","Reference method (used in CDC&rsquo;s national surveys), regional breakdown")
T(P,"and, if available, a body fat percentage estimate from our lean body mass calculator.",'and, if available, a body fat percentage estimate from our <a href="/body-fat-calculator/">body fat calculator</a>.')
# --- example table section: heading/intro/stale note
T(P,"BMI Classification Table","Healthy weight by height: examples",count=None)
T(P,"The World Health Organization (WHO) defines the following BMI categories for adults. These categories help healthcare professionals and individuals assess weight status relative to height. For a deeper dive into how these ranges apply to you, read our complete BMI calculator guide.",
  'Here is what the adult BMI categories mean in pounds and kilograms at four example heights. The <a href="/bmi-chart/">full BMI chart</a> covers every height.')
T(P,"Weight shown in pounds (lbs) across the top row. BMI = (weight × 703) / height². Values rounded to one decimal place.",
  "Method: BMI = lb &times; 703 &divide; in&sup2;, rounded to 0.1; each band lists the whole-pound weights inside the category (CDC cut-offs).")
# --- limitations card + FAQ
T(P,"Asian populations experience elevated risks at lower BMI values, which is why some countries use a BMI cutoff of 23 for overweight rather than 25.",
  f"For many Asian populations, health risks rise at lower BMI values ({WHO04}), and several countries use lower cut-offs.")
T(P,"This range is associated with the lowest risk of weight-related health conditions.","These are the CDC and WHO adult categories.")
T(P,"The WHO Western Pacific Region uses a lower overweight cutoff (23 rather than 25) for Asian populations. See our healthy BMI range guide for the full breakdown.",
  f"For Asian populations, a {WHO04} identified BMI 23 and 27.5 as public-health action points. See our healthy BMI range guide for the full breakdown.")
T(P,"Men should aim for a waist circumference below 40 inches (102 cm) and women below 35 inches (88 cm).",f"US clinical guidelines treat a waist above 40 inches (102 cm) in men and 35 inches (88 cm) in women as a sign of higher risk ({NHLBI}).")
T(P,"For adults with stable weight, checking your BMI a few times per year is sufficient. If you're actively trying to lose or gain weight, monthly checks can help track your progress. It is more useful to focus on trends over time than on single measurements — day-to-day body weight moves around because of water, food, and other short-term factors. Weigh yourself at the same time of day (ideally in the morning) for the most consistent results.",
  "There is no official schedule for adults. Body weight moves around from day to day with water and food, so the trend over weeks and months tells you more than any single reading.")
T(P,"Yes. Being underweight (BMI < 18.5) is associated with real risks including malnutrition, weakened immune function, osteoporosis, anaemia, fertility issues, and higher all-cause mortality. Severe underweight (BMI < 16) carries higher risk still. Causes can include eating disorders, hyperthyroidism, celiac disease, cancer, chronic infections, or simply inadequate caloric intake. If your BMI is below 18.5, talk to a healthcare provider — some causes need investigation, and weight-gain plans work better when they address the underlying reason.",
  f"It can be. A BMI under 18.5 can reflect undernutrition or an underlying illness, so if yours is below 18.5 and you don&rsquo;t know why, talk to a healthcare provider. In adults 65 and older, a large meta-analysis found higher mortality below a BMI of 23 ({WINTER}).")
T(P,"The clearest example is the WHO Western Pacific Region, which recommends lower cutoffs for Asian populations (overweight 23 rather than 25).",
  f"For many Asian populations, a {WHO04} found that risks rise at lower BMI values and identified BMI 23 and 27.5 as public-health action points.")
s=open(P,encoding="utf-8").read()
m=re.search(r"At the population level, yes(?:(?!</p>).)*?</p>",s,re.S)
if m:
    s=s.replace(m.group(0),f"At the population level, yes: the US clinical guidelines link a BMI above the healthy range with higher risk of high blood pressure, type 2 diabetes, heart disease and other conditions ({NHLBI}), and in adults 65 and older both low and high BMI have been linked to higher mortality ({WINTER}). For one person, BMI predicts less, because it ignores fat distribution, fitness and other risk factors; that is why clinicians use it alongside waist size and other measurements.</p>")
    open(P,"w",encoding="utf-8").write(s); LOG.append((P,1,"FAQ predict"))
else: MISS.append((P,"FAQ predict"))
# --- add the body fat calculator to "More Calculators" (cloned from the lean mass card)
s=open(P,encoding="utf-8").read()
m=re.search(r'(<a href="/lean-body-mass/" class="[^"]*calc[^"]*card[^"]*"[^>]*>.*?</a>)',s,re.S) or re.search(r'(<div class="[^"]*card[^"]*">(?:(?!<div class="[^"]*card).)*?href="/lean-body-mass/".*?</div>\s*</div>)',s,re.S)
print("lean card found:",bool(m), (m.group(1)[:300] if m else ""))
open(P,"w",encoding="utf-8").write(s)
print("applied:",len(LOG)); print("MISSES:",MISS)
