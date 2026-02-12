# BMI Calculator - Claude Code Instructions

## Project: calculatemybmi.net

### ✅ COMPLETED
- `/index.html` - 7-tab calculator (Standard, Women, Men, Age, Kids, Ideal Weight, LBM)
- `/assets/css/styles.css` - Cyan health theme (#06b6d4)
- `/assets/js/calculator.js` - All BMI calculations + visual scale
- `/about/`, `/contact/`, `/privacy/`, `/terms/` - Supporting pages
- `/blog/index.html` - 10 article listings
- `/sitemap.xml`, `/robots.txt`, `/favicon.svg`
- Schema markup (WebSite, WebApplication, Organization)

### ⏳ NEEDS COMPLETION IN CLAUDE CODE

#### 1. Generate 10 Blog Articles (2500+ words each)
1. bmi-calculator-guide (2,740,000 searches) - MASSIVE!
2. bmi-chart-women (246,000)
3. bmi-chart-men (49,500)
4. bmi-formula (18,100)
5. healthy-bmi-range (27,100)
6. bmi-calculator-by-age (9,900)
7. pediatric-bmi-calculator (3,600)
8. ideal-weight-calculator (22,200)
9. lean-body-mass-calculator (6,600)
10. bmi-categories (5,400)

#### 2. Generate PNG Favicons & OG Image

### Key Formulas
```
Metric: BMI = weight (kg) / height (m)²
Imperial: BMI = (weight (lbs) / height (in)²) × 703
```

### BMI Categories
- Underweight: < 18.5
- Normal: 18.5 - 24.9
- Overweight: 25 - 29.9
- Obese Class I: 30 - 34.9
- Obese Class II: 35 - 39.9
- Obese Class III: 40+

### Ideal Weight Formulas
- Devine (Men): 50 + 2.3 × (height in inches - 60)
- Devine (Women): 45.5 + 2.3 × (height in inches - 60)
- Robinson (Men): 52 + 1.9 × (height in inches - 60)
- Robinson (Women): 49 + 1.7 × (height in inches - 60)

### Design Specs
- Calculator: 720px max-width
- Content: 800px max-width
- Primary: #06b6d4 (Cyan)
- Header: #164e63 (Dark cyan)

### Target Volume
- Primary keyword: 2,740,000
- Total addressable: ~4.5M+ monthly
- THIS IS YOUR BIGGEST CALCULATOR!

### Deploy
```bash
git init && git add . && git commit -m "Initial"
vercel --prod
```
