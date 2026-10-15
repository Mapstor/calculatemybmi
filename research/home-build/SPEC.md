# / (homepage) — D-14 rebuild (CMB-012)

Built in chat on 2026-10-14 from GitHub `main` `c4004c8`. Pattern: the CMB-006 men page (D-14). Generator: `gen_home.py`; data: `home_stats.py` → `home_stats.json`; OG image: `og_home.py`.

## Spec (content-page Phase 2)
- **Primary:** "bmi calculator" (KWP reports the close-variant group, 2,240,000/mo, on "bmi calculation table"). **Secondaries:** calculating body mass (49,500), bmi chart calculator (18,100), calculate my body mass (9,900), checking body mass index (4,400). **Tertiaries placed:** bmi percentage calculator / bmi in percentage (1,900 each, FAQ "Is BMI a percentage?"), weight height calculator (3,600, the weight-by-height table), bmi calculator kg / kg cm (Metric toggle, FAQ), accurate body mass index calculator (FAQ "How accurate is BMI?").
- **Owned elsewhere, linked rather than targeted:** women / men / age / kids calculators; BMI chart and the charts for women and men; healthy BMI range; BMI categories; BMI formula; BMI limitations; body fat calculator; ideal weight; US obesity statistics; average weight.
- **Intent:** tool. The searcher wants their BMI now and what it means.
- **SERP (owner's pastes, 2026-10-14; Google personalised to Ljubljana, so features may differ in the US):**
  - "bmi chart calculator" and "calculate bmi": NHLBI, CDC, Calculator.net, American Cancer Society, Harvard Health, Mayo Clinic, PBRC, MDCalc, Texas Heart Institute, UnitedHealthcare, Cleveland Clinic, ADA. Every result is a calculator or a calculator plus an explainer.
  - AI Overview: the formula in both units, the six adult categories with obesity classes 1–3, BMI limits (muscle, older adults), and children's percentiles.
  - People also ask: "What is the correct BMI for my age?", "What is the BMI of 70 kg 170 cm?", "Is a 23 BMI chubby?", "What is the new BMI chart for 2026?" — all four are FAQ entries, phrased as asked.
  - People also search for: male, female, kg, with age, kg and feet, for adults, chart men, chart women, normal BMI, how to calculate for women and men.
  - GSC baseline for `/`: average position 44.6 on "bmi calculator", 126 impressions and 7 clicks over 7 days.
- **Wedge:** where the result ranks among US adults, and among men and women separately. CDC NHANES August 2021–August 2023, 5,929 adults measured, survey-weighted. The same method reproduces NCHS Series 3 No. 50 (medians 28.2 / 28.3, means 29.4 / 30.0) and the crude NCHS prevalences (underweight 1.6%, overweight 32.1%, obesity 40.3%, class 3 9.4%). None of the top 10 places the reader among real US adults. It shows in the results, in a crawlable percentile table and in a category table with the share of US adults in each.
- **Snippet block:** a 55-word answer (formula + CDC categories) opening Key takeaways.
- **SVGs:** a worked-example strip ("one pound over the line": BMI at each weight from 155 to 164 lb at 5′7″) and a 100-square grid of US adults by BMI category.
- **Data:** CDC adult and child categories; CDC About BMI; CDC growth-chart training (formulas, 703); NCHS Health E-Stat 111, Data Brief 508, Series 3 No. 50; NHANES 2021–2023 (our calculation); NHANES 2011–2018 DXA (our analysis, as already on the site); NHLBI 1998; WHO 2004 (Asian populations); WHO 1995 TRS 854 (thinness grades); Lancet Commission 2025 (Rubino et al.); Wing 2011; Winter 2014; Gallagher 2000.
- **Results-explanation plan:** the crawlable "How to read your result" walks the calculator's starting values (5′7″, 160 lb) through every output the panel shows.

## Removed from the old page (why)
- The WebSite `SearchAction`: the site has no search, so the target URL returned the homepage.
- "When to see a doctor" thresholds (BMI under 16 "prompt consultation", "consistent upward trend"), the metric-comparison table's pros and cons, "BMI around the world" ("research is ongoing"), "Learn about BMI", the stat cards and the 15-card link grid with a build note ("One card per destination"): unsourced, repeated or written for search engines (D-10, anti-slop).
- Key takeaways sat inside the calculator card; inputs had no `for`/`id` (backlog P1 pattern).
