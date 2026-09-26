# Unsourced Numeric Claims Audit

## Summary

- **Total unsourced numeric claims:** 7 distinct claims
- **Pages with unsourced claims:** 2
  - `/workspace/blog/body-fat-vs-bmi/index.html`
  - `/workspace/blog/bmi-categories/index.html`

---

## Detailed Findings

| page | location | exact sentence (verbatim, up to 200 chars) | number(s) |
|------|----------|---------------------------------------------|-----------|
| `blog/body-fat-vs-bmi/index.html` | H3 heading: Typical Body Composition Breakdown | Example body composition of healthy adult: Muscle Mass (45%), Bone & Organs (30%), Body Fat (15%), Water & Other (10%) | 45%, 30%, 15%, 10% |
| `blog/body-fat-vs-bmi/index.html` | Key Takeaways list item | BMI can misclassify up to 50% of people with excess body fat as "healthy" | up to 50% |
| `blog/body-fat-vs-bmi/index.html` | Stat grid - "Skinny Fat" scenario callout | 30% of normal BMI individuals have metabolic syndrome and elevated cardiovascular risk | 30% |
| `blog/body-fat-vs-bmi/index.html` | Table: Real-World Examples (athlete body-fat %) | Male Sprinter 6-10%, NFL Running Back 8-12%, Male Bodybuilder 4-8%, Female CrossFit Athlete 15-20%, Male Swimmer 8-12% | 6-10%, 8-12%, 4-8%, 15-20%, 8-12% |
| `blog/body-fat-vs-bmi/index.html` | H3: Healthy Body Fat Ranges by Age Group | Men aged 20-39 (8-19%), 40-59 (11-21%), 60+ (13-24%); Women aged 20-39 (21-32%), 40-59 (23-33%), 60+ (24-35%) | 8-19%, 11-21%, 13-24%, 21-32%, 23-33%, 24-35% |
| `blog/body-fat-vs-bmi/index.html` | Table: Body Fat Percentage Categories by Sex | Essential Fat: Men 2-5%, Women 10-13%; Athletes: Men 6-13%, Women 14-20%; Fitness: Men 14-17%, Women 21-24%; Average: Men 18-24%, Women 25-31%; Obese: >25% (M), >32% (W) | 2-5%, 10-13%, 6-13%, 14-20%, 14-17%, 21-24%, 18-24%, 25-31%, >25%, >32% |
| `blog/bmi-categories/index.html` | Stat boxes (colored callouts) | 40.3% Obesity age-adjusted (BMI ≥ 30); 31.7% Overweight (BMI 25–29.9); 9.7% Severe obesity (BMI ≥ 40) | 40.3%, 31.7%, 9.7% |

---

## Notable Unsourced Claims

### 1. **Up to 50% BMI Misclassification Rate**
- **Severity:** HIGH
- **Location:** Body Fat vs BMI article, Key Takeaways section
- **Claim:** "BMI can misclassify up to 50% of people with excess body fat as 'healthy'"
- **Issue:** Major health claim with significant implications; lacks visible source link in same paragraph

### 2. **30% Normal BMI with Elevated Risk**
- **Severity:** HIGH
- **Location:** Body Fat vs BMI article, Scenario callout box
- **Claim:** "30% of normal BMI individuals have metabolic syndrome"
- **Issue:** Statistics on metabolic dysfunction presented without source attribution

### 3. **40.3% & 31.7% Obesity/Overweight Prevalence**
- **Severity:** MEDIUM
- **Location:** BMI Categories article, stat boxes
- **Claim:** "40.3% Obesity age-adjusted (BMI ≥ 30); 31.7% Overweight (BMI 25–29.9)"
- **Issue:** These are shown in styled divs with source links in separate caption paragraph below, not in same element

### 4. **Body Composition Breakdown (45-30-15-10%)**
- **Severity:** MEDIUM
- **Location:** Body Fat vs BMI article, donut chart legend
- **Claim:** "Typical composition: Muscle Mass (45%), Bone & Organs (30%), Body Fat (15%), Water & Other (10%)"
- **Issue:** Example body composition presented without source; marked as "varies significantly"

### 5. **Athlete Body Fat Percentages**
- **Severity:** MEDIUM
- **Location:** Body Fat vs BMI article, Real-World Examples table
- **Claims:**
  - Male Sprinter: 6-10%
  - NFL Running Back: 8-12%
  - Male Bodybuilder: 4-8%
  - Female CrossFit Athlete: 15-20%
  - Male Swimmer: 8-12%
- **Issue:** Example ranges for specific athlete types without source documentation in table

### 6. **Age-Specific Body Fat Ranges**
- **Severity:** MEDIUM
- **Location:** Body Fat vs BMI article, age/sex range chart
- **Claims:** Men 20-39 (8-19%), 40-59 (11-21%), 60+ (13-24%); Women 20-39 (21-32%), 40-59 (23-33%), 60+ (24-35%)
- **Issue:** Specific ranges by age and sex presented in visual chart without source attribution

### 7. **Body Fat Category Percentages (ACE Standards)**
- **Severity:** MEDIUM
- **Location:** Body Fat vs BMI article, categories table
- **Claims:**
  - Essential Fat: Men 2-5%, Women 10-13%
  - Athletes: Men 6-13%, Women 14-20%
  - Fitness: Men 14-17%, Women 21-24%
  - Average: Men 18-24%, Women 25-31%
  - Obese: >25% (M), >32% (W)
- **Issue:** Sourced to "American Council on Exercise (ACE)" in table caption, but numeric cells lack inline link verification

---

## Notes on Excluded Numbers

The following numeric items were **excluded** as they are derivable from BMI formula or trivial conversions:
- BMI cutoffs (18.5, 25, 30, 40 BMI values)
- Weight/height conversions (kg ↔ lbs, cm ↔ in)
- Height-in-inches values in conversion tables
- Formula-specific percentages (e.g., "80% of TDEE")

---

## Recommendations

1. **Highest priority:** Add inline sources or parenthetical citations to the "up to 50%" and "30% of normal BMI" claims
2. **Medium priority:** Move source links into stat boxes for 40.3%, 31.7%, 9.7% rather than caption-only
3. **Low priority:** Add hover-text or footnotes to chart and table data confirming sources
