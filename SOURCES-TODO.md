# SOURCES-TODO — primary source audit backlog

Every currently-attributed claim on the site that needs a real primary source (or a rewrite that drops the attribution). Populated from Phase A A3(f) — 18 hits across 8 pages. Amendment B4(f) stripped 6 of these; the remaining 12 stay in place until the chat-driven primary-source audit runs.

The "linked URL" column is the anchor href the current text points at (if any). "Status" = **stripped** if the attribution lead-in was removed in Phase B, **untouched** if the sentence remains.

| # | Page | Section / location | Verbatim sentence (attributed claim) | Linked URL | Status |
|---|------|---------------------|--------------------------------------|------------|--------|
| 1 | `blog/bmi-and-health-risks/index.html` | H2 "Understanding the BMI-Mortality Relationship" | *(originally)* "According to extensive research published in major medical journals and data from the World Health Organization (WHO), the lowest mortality rates occur within the healthy BMI range of approximately 18.5–24.9." | who.int/…/obesity-and-overweight | **stripped** — sentence now reads "The lowest mortality rates occur within the healthy BMI range…"; still needs a specific citation (mortality J-curve paper, not WHO fact sheet). |
| 2 | `blog/bmi-categories/index.html` | Section on category prevalence | "…the most common BMI category in the US adult population according to CDC NHANES data (see the distribution figures further down this page)." | *(none inline; NCHS Data Brief 508 linked in footer of same section)* | **untouched** — self-references the stat callouts already sourced to db508/hestat111. |
| 3 | `blog/bmi-chart-explained/index.html` | H2 "BMI Charts for Men vs Women" | "According to Harvard Health, BMI provides a rough estimate but does not tell the whole story about health." | health.harvard.edu/…/bmi-201603309339 | **untouched** — attribution keeps a specific link; primary source ok. Flag for rewrite if we want to drop soft phrasing. |
| 4 | `blog/healthy-bmi-range/index.html` | Cost-of-care paragraph | *(originally)* "Research from Harvard Health and other institutions shows that obesity-related medical costs were approximately $1,429 higher per year than those for people at healthy weight." | health.harvard.edu/… | **stripped** — sentence now reads "Obesity-related medical costs have been reported at approximately $1,429 higher per year…"; $1,429 figure still needs a primary source (Cawley & Meyerhoefer 2012 or similar). |
| 5 | `blog/how-to-lower-bmi/index.html` | H2 "Weight-Loss Fundamentals" | "According to the CDC's Healthy Weight guidelines, BMI is a useful screening tool, though it doesn't measure body fat directly." | cdc.gov/…/healthy-weight | **untouched** — CDC page is a valid primary source; consider deep-linking to the exact page. |
| 6 | `blog/how-to-lower-bmi/index.html` | Energy-balance paragraph | "According to the NIH National Institute of Diabetes and Digestive and Kidney Diseases, this principle remains the cornerstone of effective weight management." | niddk.nih.gov/… | **untouched** — NIDDK is a primary source; deep link recommended. |
| 7 | `kids-bmi-calculator/index.html` | Current Statistics | "According to CDC data on childhood obesity, the prevalence of obesity among children and adolescents in the United States has more than tripled since the 1970s." | cdc.gov/… | **untouched** — needs deep link to the specific CDC childhood-obesity page or paper making the "tripled since the 1970s" claim. |
| 8 | `lean-body-mass/index.html` | Intro to LBM's added value | "According to Harvard Health, body composition is a significantly better predictor of health outcomes than BMI alone." | health.harvard.edu/… | **untouched** — soft claim; consider rewriting as "body composition can be a better predictor…" or backing with a specific study. |
| 9 | `men-bmi-calculator/index.html` | BMI Distribution Among U.S. Adult Men | "According to CDC data, the majority of American men fall into the overweight or obese categories. This chart shows the approximate distribution…" | cdc.gov/… | **untouched** — needs the exact NCHS/NHANES cycle deep link matching the chart. |
| 10 | `men-bmi-calculator/index.html` | Men-specific risks paragraph | "…the likelihood of developing certain conditions, according to the NIH National Heart, Lung, and Blood Institute. Men face some gender-specific risks that are worth understanding." | nhlbi.nih.gov/… | **untouched** — NHLBI is a primary source; deep link recommended. |
| 11 | `men-bmi-calculator/index.html` | FAQ: average BMI for American men | "According to CDC data, the average BMI for adult American men is approximately 29.1, which falls in the overweight category…" | cdc.gov/… | **untouched** — needs deep link to the specific NHANES table publishing "29.1"; otherwise consider dropping the specific number. |
| 12 | `new-bmi-calculator/index.html` | Pros/Cons of the new BMI | *(originally)* "…according to researchers and health organizations: Pros of the New BMI…" | *(none)* | **stripped** — vague attribution removed; the pro/con list itself now stands without a lead-in. |
| 13 | `women-bmi-calculator/index.html` | Intro to women's BMI page | *(originally)* "According to WHO global health data, understanding your BMI as a woman requires considering factors like hormonal fluctuations and life stage." | who.int/…/obesity-and-overweight | **stripped** — sentence now reads "Understanding your BMI as a woman requires…"; the WHO fact sheet doesn't say this — treat as editorial and needs sourcing or removal. |
| 14 | `women-bmi-calculator/index.html` | H2 "How Women's BMI Differs from Men's" | *(originally)* "Here is why, according to Harvard Health and the NHS: Higher Essential Body Fat — Women naturally carry 6-11% more body fat than men…" | health.harvard.edu, nhs.uk | **stripped** — attribution lead-in removed; the "6-11% more body fat" claim needs a primary anatomy/physiology reference (e.g., ACSM Guidelines, Jackson & Pollock, or ACE Body Composition tables). |
| 15 | `women-bmi-calculator/index.html` | Underweight risks paragraph | "…as underweight for women of all ages, according to the WHO." | who.int/… | **untouched** — attribution kept because WHO does publish the 18.5 cut-off. Deep link to the CDC categories page would be more precise. |
| 16 | `women-bmi-calculator/index.html` | Related resources list | *(originally)* "CDC Office on Women's Health — Federal guidance on women's health topics including weight management" | *(none linked; item was a bullet)* | **deleted** — bullet removed. There is no "CDC Office on Women's Health"; the correct entity is HHS Office on Women's Health (womenshealth.gov). If we want a resource pointer, use that URL. |
| 17 | `women-bmi-calculator/index.html` | Trusted resources bullets — "WHO Obesity and Overweight Fact Sheet" | "WHO Obesity and Overweight Fact Sheet - Global BMI classification standards and health impact data" | who.int/…/obesity-and-overweight | **untouched** — but the WHO fact sheet does **not** contain the BMI category table; if we're citing it *as* the classification source we should switch to the CDC adult BMI categories page. |
| 18 | `women-bmi-calculator/index.html` | Intro to women's page (second instance, after "Here is why" para) | *(originally)* second occurrence of "According to WHO global health data, understanding your BMI as a woman requires…" | who.int/… | **stripped** — second copy also rewritten. |

---

## Divergence note — /about/ production sentence

You reported that production `/about/` still shows "The site does not currently serve advertisements." That phrase is **not** in the current local repo (verified in B0 with whitespace-normalized search across all 30 files). Two possible causes:
1. Vercel edge cache serving pre-scrub HTML in your region — will clear naturally after the next successful push and cache invalidation.
2. Some pre-Raptive draft of `/about/` was resurrected somewhere I don't have visibility into (unlikely — `origin/main` is level with local).

If the sentence is still visible in the About page after this Phase B push deploys, drop this exact replacement into `/workspace/about/index.html` (per the amendment):

> The site is supported by display advertising served by Raptive. Calculator inputs are processed in your browser and are not sent to our servers; the privacy policy lists the cookies and partners involved.

---

## Privacy policy Advertising block

`/workspace/RAPTIVE-PRIVACY.txt` was not present at the time of Phase B, so no privacy-policy text was inserted. When you drop that file in, insert its verbatim contents under an `<h2>Advertising</h2>` heading between the current Section 2 (Advertising — Raptive) callout and Section 3 (What we collect) on `/workspace/privacy/index.html`, retaining the current "click here" line as the first paragraph of that new Advertising block. Do not paraphrase.

## Numeric-claims audit

`/workspace/UNSOURCED-NUMBERS.md` was generated in Phase A A4 with 7 rows. The chat-driven audit will expand it. Notable numeric claims still on the site that need review:
- "$1,429 higher per year" (healthy-bmi-range)
- "approximately 29.1" (men-bmi-calculator FAQ average BMI)
- "more than tripled since the 1970s" (kids-bmi-calculator)
- "6-11% more body fat than men" (women-bmi-calculator)
- "5-8 lbs" / "2-4 lbs" from contraceptive paragraph — **already deleted in B4(e)**.
- All athlete body-fat ranges, "up to 50%", "30% of normal BMI individuals" (body-fat-vs-bmi) — already in UNSOURCED-NUMBERS.md.
