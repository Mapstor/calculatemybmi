# /men-bmi-calculator/ — skills pilot (CMB-006)

Branch `pilot/men-skills` only. The owner evaluates the preview and decides whether the pattern rolls out to other pages.

## Spec (content-page Phase 2)
- **Primary:** bmi calculator men (110,000/mo; variants: male BMI calculator, men's BMI calculator). **Secondaries:** bmi calculator for male adults, bmi calculator chart male, bmi calculator for men chart, bmi calculator adult male. **Tertiaries** placed in the copy: older men, male kg / cm kg, men's BMI calculation.
- **Owned elsewhere, linked rather than targeted:** BMI chart for men / male normal BMI / ideal BMI men → `/blog/bmi-chart-men/`; average male BMI / average weight / average waist → `/average-weight/`; body fat percentage men → `/body-fat-percentage-chart/`; body fat calculator male → `/body-fat-calculator/`.
- **Intent:** tool. The searcher wants to calculate their BMI as a man and know what the number means for a man.
- **SERP:** not checked live; chat has no SERP access. Owner to eyeball the featured snippet and PAA questions.
- **Wedge:** where the result ranks among US men. This is a percentile from CDC NHANES 2021–2023 (2,680 men, survey-weighted). The method reproduces the NCHS Series 3 No. 50 medians and 95th percentiles (`men_stats.py`). It shows in the results and as a crawlable percentile table.
- **Snippet block:** a 58-word answer under the tool, opening the Key takeaways box.
- **SVGs:** a worked-example concept figure (the formula, the BMI scale and the healthy band at 5′10″) and a waist ruler showing the average US man at 40.6 in. Data charts are additional.
- **Data:** CDC adult BMI categories; NCHS Health E-Stat 111; NCHS Series 3 No. 50; NHANES 2021–2023 (our calculation); NHANES 2011–2018 DXA (our analysis); NHLBI 1998 guidelines; WHO 2008 (WHR, no link yet); Provencher 2018; Wing 2011; Winter 2014; Gallagher 2000.

## What changed
- **Tool first.** The hook is 2 lines. On a 390×844 phone the Calculate button now sits above the fold: its bottom edge moved from 906 px to 816 px.
- **Results.** New "Compared with US men" rank: a headline, a bar with the median and a sentence.
  - The healthy min/max tiles put the converted unit on its own line, so values no longer break mid-unit.
  - Shared `calculator.js`: affects every adult calculator.
- **Answer block + Key takeaways** now sit below the calculator card. They used to be a card inside the calculator card.
- **Contents chips** jump to each section; on phones they are a single scrolling row.
- **Crawlable twin.** A worked example with an explanation of every output: BMI, healthy range, gap, rank, BMI Prime, ponderal index, milestones, what-if.
- **Sections:** how you compare with US men, healthy weight by height, when BMI misleads men, waist size, health risks, common situations, FAQ, and sources with method.
  - Sub-sections are headings and lists, not cards inside cards.
- **FAQ:** 8 questions in demand order (ledger volumes), self-contained answers, JSON-LD in sync.
- **One related block** of two flat link lists, in place of 12 cards. This also removes the duplicate "Muscle Mass and BMI" → athletes link.
- **Metadata.** New meta, OG and twitter descriptions and WebApplication description. New OG image: the title plus the average US man's BMI of 29.4.
- **Design.** All inside the current look, using opt-in classes in `styles.css` (`main.reading`, `.flow`, `.stat-callout`, `.toc-inline`, `.faq-list.flat`, `.related-cols`, `.rank-box`, `.figure`).
  - Global by nature: the `--link` #0e7490 token for text links. Footer links stay light.

## Scorecard (chat, 2026-10-11, same local conditions before and after)
| Measure | Before (live code) | After |
|---|---|---|
| impeccable detect 0.1.14, 390×844 | 57 + 3 advisory | 2 + 0 |
| impeccable detect, 1280×800 | 76 + 3 advisory | 2 + 0 |
| Remaining findings | — | brand CTA gradient (white on cyan, 2.7:1): owner decision / R3 exception |
| Anti-slop tells (body prose) | 31 in ~3,100 words (CMB-003 review); scan 34 hits / 12.3 per 1k | 0 (scan + manual pass) |
| Words in scope (prose, FAQ, takeaways) | ~2,770 | ~2,470 |
| H2 + H3 headings | 37 (12 of them card titles) | 24 |
| Data tables / purpose-built SVGs | 2 / 1 | 4 / 2 |
| Internal link targets (unique) / duplicates in body | 25 / 12 repeated | 20 / related block + inline only |
| Calculate button bottom at 390×844 | 906 px (below the fold) | 816 px (above) |
| Page overflow at 360 / 390 / 1280 | none / none / none | none / none / none |
| Meta / schema | descriptions promised "men-specific healthy weight ranges" (removed in CMB-005); generic OG image | wedge-led descriptions; 8 FAQ Q&A in sync; data-bearing OG image |

Independent fact-check (separate agent):
- **First pass:** 9 findings, all fixed. The BMI Prime and waist-note fixes moved into CMB-005.
- **Second pass:** all 149 numbers trace to a source; 8 of 8 FAQ items match the JSON-LD; 44 of 44 links and anchors resolve.

## Rollout notes (if approved)
- Other calculator pages need the same markup classes plus their own wedge and data. There is no template copy: each page keeps its own content (google-ai-content-policy, no scaled near-duplicates).
- Logged separately (not in this pilot): the BMI chart pages' kg overlaps (CMB-007 candidate), the D-12 date removal, and the WHO 2008 link.
