# ABSORBED-AUDIT.md — Phase 2a audit of consolidation-absorbed content

Purpose: audit the clinical material moved onto `bmi-categories` and
`bmi-and-health-risks` during Phase 1b cluster consolidation, **before** Phase 2
attaches a named pharmacist's credential to every page.

Each check reports what was found and what was changed. Nothing here is
personal medical advice.

---

## 1. GLP-1 / pharmacotherapy mentions sitewide

**Enforced rule:** name the class only; eligibility and suitability are a
clinician's decision; link to an institutional source. No dosing, no
titration, no efficacy percentages, no comparisons between agents, no
"who should ask for it" framing.

**Occurrences found (before this audit):** two.

| File | Old text (excerpt) | Action |
|---|---|---|
| `blog/bmi-and-health-risks/index.html` L189 | "GLP-1 receptor agonists (semaglutide, tirzepatide), phentermine-topiramate, naltrexone-bupropion, and orlistat are the current FDA-approved options" | **Rewritten:** all named agents removed. Now reads "anti-obesity medications and bariatric surgery are options in some patients; both categories exist and are described in the [NIDDK weight-management resources](https://www.niddk.nih.gov/health-information/weight-management). Whether a specific medication or procedure is suitable for a specific person is a clinician's decision..." |
| `blog/bmi-categories/index.html` L217 | "including anti-obesity medications (GLP-1 receptor agonists such as semaglutide and tirzepatide are increasingly used)" | **Rewritten:** all named agents removed. Now reads "anti-obesity medications and bariatric surgery become options that clinical guidelines discuss alongside lifestyle change" with NIDDK link. |

**Sitewide grep verification (post-fix):** `grep -riE 'semaglutide|tirzepatide|orlistat|phentermine|naltrexone|bupropion|topiramate|GLP-1|liraglutide|wegovy|ozempic|zepbound|mounjaro|saxenda|contrave'` returns zero hits across HTML.

---

## 2. Bariatric-surgery section — eligibility attribution

**Before:** eligibility criteria were listed under an H3 "Standard eligibility criteria" as though the site were making the recommendation. Procedure-comparison table was purely descriptive (mechanism + reversibility only, no outcome figures).

**After:**
- H3 renamed to "What ASMBS/NIDDK publish as candidacy criteria."
- Section preamble made explicit that ASMBS and NIDDK are the standard published sources, and that this page summarises what those bodies publish — "not a personal eligibility assessment." Whether surgery is right for any specific person is a decision made by that person and a bariatric surgical team.
- Criteria now attributed to ASMBS/NIDDK explicitly (including a note that the 2022 ASMBS/IFSO consensus broadened them). Users are directed to the ASMBS and NIDDK links for current published text.
- Procedure table caption updated with disclaimer: "Table describes mechanism only. Weight-loss magnitudes, complication rates, and comparative outcomes vary between studies and populations — this page does not publish them. Refer to ASMBS and NIDDK for authoritative summaries, and to a bariatric surgical team for personal counselling."
- FAQ "What BMI qualifies for bariatric surgery?" renamed to "What BMI does ASMBS list for bariatric surgery candidacy?" and rewritten to explicitly attribute to ASMBS / NIDDK rather than state as site guidance.
- `bmi-categories` bariatric mention rewritten to attribute to ASMBS and remove all outcome/mortality claims.

---

## 3. Metabolic-syndrome 5-criteria diagnostic table

**Before:** table with 5 rows (waist, triglycerides, HDL, BP, fasting glucose) attributed to Mayo Clinic. The Mayo Clinic attribution is generic — Mayo does describe metabolic syndrome, but the specific harmonised numeric cut-offs are from a joint statement, not a Mayo publication.

**Decision:** **kept the numeric thresholds** and re-attributed to the actual primary source. Reasoning: these are real, published, widely-used clinical cut-offs (unlike the fabricated site-history and age-adjusted content deleted earlier). Stripping them to prose without numbers would obscure information that is uncontroversial and well-established; misattributing them was the actual defect.

**After:** table converted to prose so the cut-offs read as a summary of the source rather than as if the site is issuing diagnostic criteria. Now attributes to the harmonised 2009 joint statement:

> Alberti KG, Eckel RH, Grundy SM, et al. "Harmonizing the metabolic syndrome: a joint interim statement of the International Diabetes Federation Task Force on Epidemiology and Prevention; National Heart, Lung, and Blood Institute; American Heart Association; World Heart Federation; International Atherosclerosis Society; and International Association for the Study of Obesity." *Circulation* 2009;120(16):1640–1645. DOI: 10.1161/CIRCULATIONAHA.109.192644.

Link: <https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.109.192644>

The prose explicitly notes that local ethnic-specific waist thresholds may apply (accurate per the joint statement).

---

## 4. Treatment-intensity table

**Before:** three-column table (Class I / II / III) with rows for lifestyle modification, anti-obesity medication, and bariatric surgery that read as "at BMI X you should do Y" (e.g., "Anti-obesity medication: Considered if lifestyle change is insufficient / Often recommended / Usually recommended").

**Decision:** **table removed; replaced with prose** describing how clinical guidelines are structured, with explicit "this is a general description of how guidelines are written — not personal medical advice" framing.

**After:**

> Adult obesity treatment guidelines (see the NHLBI overweight and obesity overview and NIDDK weight-management resources) generally describe treatment as escalating across classes: lifestyle change (diet, physical activity, behavioural support) is the foundation for every class; anti-obesity medications and bariatric surgery become options at higher BMI thresholds or with obesity-related comorbidities. This is a general description of how guidelines are written — not personal medical advice. Whether any specific intervention is right for a specific person is a clinician's decision.

---

## 5. Post-merge Tier B re-run on the three survivors

Re-run with the same pattern set used in Phase 1b (N-fold, hazard ratio, percent-change, N% of, "approximately N%", weight-loss %s) after all Phase 2a edits.

**Result: ZERO hits on all three survivors** (`bmi-categories`, `bmi-and-health-risks`, `underweight-bmi-risks`).

Specific figures that had leaked back through the merge and are now stripped:

| File | Old text | New text |
|---|---|---|
| `bmi-categories` L172 | "According to Mayo Clinic, approximately 30–35% of adults in most developed countries fall in this range" | Reworded to point to CDC NHANES distribution shown further down the page |
| `bmi-categories` L194 | "Hypertension: Found in approximately 40–50% of individuals with class I obesity" | "Hypertension: commonly present at this class" |
| `bmi-categories` L196 | "Non-alcoholic fatty liver disease: Affects an estimated 50–75% of people with obesity" | "prevalent in adults with obesity" + NIDDK NAFLD link |
| `bmi-categories` L197 | "Sleep apnea: Affects approximately 40% of people at this BMI level" | "common; prevalence higher than in normal-weight adults" |
| `bmi-categories` L249 | "approximately 41% of U.S. adults have obesity, over 71% overweight or obese" | Removed the specific %s; now just points to the CDC NHANES table above with a qualitative summary |
| `bmi-categories` L456 (FAQ) | "Studies suggest 30–40% of overweight individuals are metabolically healthy" | Reworded qualitatively without the estimate |
| `bmi-and-health-risks` L201 | "for every 5-unit increase in BMI above the normal range, the risk of coronary heart disease increases by approximately 27–30%" | Removed the specific % — now reads "risk rises progressively... trend is the reliable takeaway" |
| `bmi-and-health-risks` L367–380 | NAFLD spectrum chart with "Simple Steatosis 25% / NAFLD 55% / NASH 15% / Cirrhosis 5%" bar segments | Chart removed; qualitative prose retained |

**Preserved primary-source numerics (kept intentionally, verified as real):**
- Flegal 2013 hazard ratios (0.94, 0.95, 1.29 with 95% CIs) — anchored to PMC4855514 deep link and PMID
- Winter 2014 plateau (23–33 BMI, n=197,940, 32 cohort studies, adults 65+) — anchored to PMID 24452240
- Alberti 2009 metabolic-syndrome cut-offs (waist thresholds, TG, HDL, BP, glucose) — anchored to CIRCULATIONAHA.109.192644
- DPP 5–7% weight loss cutting T2D progression — described qualitatively, no specific percent-reduction figure attached
- Standard clinical-guideline weight-loss targets (5–10%, 7–10% for NAFLD reversal, 15–25% for surgery-level outcomes) — kept as they appear identically across NHLBI/NIDDK/AACE clinical guidance and are described as targets clinical guidelines centre on rather than as specific study findings

---

## 6. Absorbed-citation verification

| Citation | Real? | Deep link | Supports adjacent sentence? |
|---|---|---|---|
| Nurses' Health Study | ✅ real (Harvard, 1976–) | Not linked (general cohort study reference) | **Reworded.** Old text said the WHO cut-offs were "validated against" NHS and HPFS, which overstates the specific role of those two cohorts. Now says the cut-offs "have since been the reference point in a large body of BMI/mortality research, including long-running cohort studies (such as the Harvard Nurses' Health Study and Health Professionals Follow-up Study)" — factually defensible. |
| Health Professionals Follow-up Study | ✅ real (Harvard, 1986–) | Not linked | Same treatment as NHS. |
| Alberti et al. 2009 (metabolic syndrome) | ✅ real | <https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.109.192644> | Yes — the exact numeric cut-offs published in this joint statement are what the prose cites. |
| WHO obesity fact sheet | ✅ | <https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight> | Yes |
| CDC About Adult BMI | ✅ | <https://www.cdc.gov/bmi/about/index.html> | Yes |
| NHLBI overweight and obesity clinical overview | ✅ | <https://www.nhlbi.nih.gov/health/overweight-and-obesity> | Yes |
| Mayo Clinic — obesity symptoms and causes | ✅ | <https://www.mayoclinic.org/diseases-conditions/obesity/symptoms-causes/syc-20375742> | Yes |
| Cleveland Clinic — Class III obesity | ✅ | <https://my.clevelandclinic.org/health/diseases/21989-class-iii-obesity-formerly-known-as-morbid-obesity> | Yes |
| Winter et al. 2014 (older-adult BMI/mortality meta-analysis) | ✅ | <https://pubmed.ncbi.nlm.nih.gov/24452240/> | Yes (numeric detail matches the paper's headline finding) |
| Flegal et al. 2013 (JAMA, pooled BMI/mortality) | ✅ | <https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/> (PMID 23280227) | Yes (hazard ratios and study N match) |
| ASMBS | ✅ (professional body homepage) | <https://asmbs.org/> | Adequate as a candidacy-guideline pointer; readers are told to follow the link for the current published text rather than trusting the site's summary |
| NIDDK weight-management | ✅ | <https://www.niddk.nih.gov/health-information/weight-management> | Yes |
| NIDDK bariatric surgery | ✅ | <https://www.niddk.nih.gov/health-information/weight-management/bariatric-surgery> | Yes |
| NIDDK NAFLD/NASH | ✅ | <https://www.niddk.nih.gov/health-information/liver-disease/nafld-nash> | Yes |

**No fabricated study attributions detected.** Every named citation resolves to a real publication or a real institutional page. The NHS/HPFS attribution was softened because it overstated the specific role of those two cohorts in setting the 25/30 cut-offs; all other citations are used correctly.

---

## 7. Sitewide medical-disclaimer audit

Every non-hub HTML page that mentions treatment, drug, surgery, or clinical eligibility content was checked for a body-visible medical disclaimer (not just the site footer). **17 of 18 identified pages already carried body-visible disclaimers** in the article content. The one exception was `blog/index.html` — the blog hub / directory page — which itself does not carry clinical content, only links to guides that do.

**New addition:** on both `bmi-and-health-risks` and `bmi-categories`, an amber-outlined callout box was added directly above the drug/surgery content (start of the Obesity Classes section and start of the Class I Obese section respectively). Each callout explicitly:
- Frames the section as summarising published guidelines, not personal advice;
- Notes that the site is written by a pharmacist (MPharm), not a physician;
- Points readers to a qualified clinician.

This addresses the concern that the existing article-end disclaimer sits ~400 lines below the drug/surgery text on the umbrella page. Readers now hit a warning before they hit any treatment discussion.

Phase 2 (the byline pass) will attach the standard "Written by Marko Visic, MPharm" line to every guide, so the pharmacist-not-physician framing is consistent everywhere.

---

## Summary

- 2 pharmacotherapy mentions rewrote to strip named agents.
- 1 bariatric section restructured so ASMBS/NIDDK own the criteria, not the site.
- 1 metabolic-syndrome table converted to prose with real primary-source attribution.
- 1 treatment-intensity table deleted; replaced with sourced prose.
- 8 additional Tier B rewrites on cluster survivors to strip figures that came back through the merge.
- 1 citation attribution softened (NHS/HPFS).
- 2 amber callouts added directly above the drug/surgery content.
- Final Tier B grep on all 3 survivors: **zero hits**.

Ready for Phase 2 (byline / author identity / E-E-A-T) with the constraint noted in your instructions: on pages carrying drug or surgical content, the byline must not imply clinical review. The standard "Written by Marko Visic, MPharm · Last reviewed 2026-08-02" line, plus the pharmacist-not-physician disclaimer, is compatible with the callouts added in this audit.
