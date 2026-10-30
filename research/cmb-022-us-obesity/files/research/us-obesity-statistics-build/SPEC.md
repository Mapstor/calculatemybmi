# /us-obesity-statistics/ — CMB-022 build record

D-14 rebuild #11. The page owns 472 keywords worth 100,830/mo (`research/keyword-ledger.csv`): "obesity rate in us" 14,800
(primary), "us obesity rate" and "what percentage of americans are obese" 14,800 each, "obesity in america" 5,400, "obese
percentage usa" and "percentage of obese americans" 3,600 each, "how many people are obese in america" 2,900, "us obesity
statistics", "america overweight rate" and "percentage of overweight americans" 2,400 each, "how many americans are obese"
1,900, "america average bmi" 1,600, "childhood obesity usa" 1,300, "us obesity rate by year" 1,000. Groups: overweight
10.6k, how many 7k, by year 2.8k, children 2.2k, race 1.1k, states 1.1k, severe 340, countries 160 (most country keywords
were discarded as off-topic). State rankings belong to `/obesity-rate-by-state/` and the children's detail to
`/childhood-obesity-statistics/`: this page answers each in a few lines and links there.

## SERP and wedge
Owner's pastes of 2026-10-29 (google.com, US/English, not personalized): "obesity rate in us", "what percentage of
americans are obese", "us obesity rate by year". The AI Overviews give "40.3% to 42.4%", Gallup's 37.0%, "as high as 68.6%
to 75%" under the Lancet Commission's new definition (credited to the Harvard Gazette, which BUILD.md bars), NIDDK's
2017–2018 figures, Trust for America's Health state numbers from 2023 data, the CDC children's figures. People also ask:
"Is it true that 70% of Americans are overweight?", "Are obesity rates rising or falling in the US?", "Is it true that
40% of Americans are obese?", "Which state is #1 in obesity?", "What was the obesity rate in 1960?", "What country is #1
in obesity?", "Why is Japan's obesity rate so low?", "Is 150lbs at 5'7" overweight?". The page answers the first five as
FAQ; country questions have no verified source in the registry and 160/mo in the ledger; "5 7 150 lbs female" belongs
to `/blog/bmi-chart-women/`.

The wedge, two parts:
- **The 60-year measured series as the hero** (the page map's link magnet): obesity, overweight and severe obesity in
  every survey of CDC's national series, adults 20–74, age-adjusted, 1960–1962 to August 2021–August 2023 (NCHS Health
  E-Stat 111, Table 1, re-read live and typed in again). The CSV (585 rows) and the embeddable chart stay at their URLs; the
  embed code keeps the image URL, size, alt text and link, so copies already in use keep working (its credit line now names
  both surveys: "Data: CDC NCHS (NHES, NHANES).").
- **One table of what each number in the results counts**, grouped by method: 40.3% / 41.9% / 42.4% weighed and measured
  (three NHANES periods: August 2021–August 2023; 2017–March 2020, stopped by the pandemic; 2017–2018, its first two
  years), 37.0% (Gallup, 2025, self-reported online, 16,946 adults) and 24.2–39.7% (CDC state surveys, 2025, self-reported
  by phone, 47 states and DC), 68.6% (Fourman et al. 2025: 301,026 All of Us volunteers aged 18–80, not weighted to the US
  population; 42.9% by BMI alone with WHO's race-specific cut-offs) and 75.2% (Al-Roub et al. 2025: NHANES 2017–2023,
  14,414 adults, 39.9% by BMI alone; 58.4% with a waist-to-height cut-off of 0.6 instead of 0.5) under the 2025 Lancet
  Commission definition. None of the results pages explains the spread; the AI Overview quotes the 68.6–75% range as
  "could be as high as".

## Data
- **The page's CSV** (`us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv`, unchanged): the S1 build typed the
  NCHS tables in (`research/us-obesity-build/research/build_dataset_us_obesity.py`). `gen_obs.py` holds HE-Stat 111 Table 1
  (all 27 "All" rows, both age ranges) as read live on 2026-10-29 and stops if the CSV differs; it asserts every other value
  it prints (DB 508, HE-Stat 112 and 119, Table 3 with its * and † notes).
- **The CSV's two blank standard errors**: the HE-Stat 119 rows for ages 20–74 (underweight 4.0% in 1960–1962 and 1.7% in
  August 2021–August 2023) gain the published 0.2 and 0.3, in the CSV and in the S1 builder
  (`research/us-obesity-build/research/build_dataset_us_obesity.py`), which still writes the CSV byte for byte. The
  Dataset's `dateModified` moves with it.
- **Other published values** (`obs_sources.json`): Gallup 2025, Fourman 2025, Al-Roub 2025, the Lancet Commission's
  criteria and counts, CDC's 2025 maps page, each with the sentences read on 2026-10-29 (the fact-check of 2026-10-30
  added Fourman's sample notes and Al-Roub's 0.6 alternative).
- **Our calculation** (`research/home-build/home_stats.json`, `home_stats.py`, CDC DEMO_L + BMX_L, adults 20+, pregnant
  women excluded, exam weights): the split of obesity into class 1 (20.6%) and class 2 (10.3%), and the mean BMI of all
  adults (29.7). The same code reproduces CDC's published crude shares (1.6 / 32.1 / 40.3 / 9.4) and Series 3 No. 50's
  means and medians, which the generator asserts. Healthy weight (26.0%; 51.1% and 26.2% for the 60-year change) is 100%
  minus CDC's other shares; counts are share × CDC's population total (245,061,169 adults; 74,908,988 children 2–19),
  rounded once.
- **Our calculation, 300 lb** (`obs_stats.py` → `obs_stats.json`; the same DEMO_L + BMX_L files, registry
  `nhanes-2021-2023-exam-files`; adults 20+, examined, not pregnant, with a measured weight, n = 5,942): 2.87% weighed 300 lb
  (136.1 kg as recorded) or more, 95% CI 2.40–3.34 (Taylor linearization over strata and PSUs, 15 df); men 4.05% (2,688),
  women 1.74% (3,254). Printed as 2.9% / about 3%, about 4% and 2%; the script stops if a printed value sits near a rounding
  tie, and it re-derives the class split and the mean BMI with its own code and asserts them equal to `home_stats.json`.
  CDC publishes no share at 300 lb; the page adds that the result fits CDC's Series 3 No. 50 95th percentiles (290.6 lb
  for men, 262.7 lb for women).
- **CDC's state file** (`research/state-obesity/cdc-brfss-adult-obesity-by-state-2011-2025.csv`, the state page's): the
  2025 top three (Alabama 39.7, North Dakota 39.1, Kentucky 38.8), DC 24.2, Mississippi 40.4 in 2024 with no 2025
  estimate, the states at 40% or more (2024: Mississippi and West Virginia; 2025: none).
- **Comparisons**: a difference is called higher or lower only where CDC reports it as significant, or where it is more
  than 2.13 times its standard error (t at 95% for the survey's 15 degrees of freedom; it was "twice" before the
  fact-check, and no claim fell between the two) from CDC's published standard errors (groups treated as independent); the
  generator asserts each one it states (men vs women overweight, ages 2–5 vs 6–11 and 12–19) and the ones it avoids (boys
  vs girls; Black vs Hispanic and Mexican American adults, so the race paragraph gives a range; 2017–2018 against
  2021–2023, so the page says "highest estimate", never "peak"; overweight moved between 30.3% and 34.4%, so never "near
  31%").

## Page (`gen_obs.py`, run on the page at be1ca97)
H1 "US Obesity Rate and Statistics" (kept) + byline → three intro paragraphs (the question and the spread of numbers; why
they differ and CDC's measured 40.3%; the promise line) → key takeaways (the answer: 40.3%, about 99 million, 72.4% BMI 25+,
9.4% severe; 5 bullets) → disclaimer → hero figure (three lines, 15 surveys, first and last values and the 42.8% high labelled) → 10
chips → how many Americans are obese (category figure in millions, the six-category table with the class 1 / 2 split,
"What percentage of Americans are overweight?" as an `h3` with the old `#overweight` anchor) → where do you fit (the tool)
→ US obesity rate by year (all 15 surveys) → are obesity rates rising or falling (the decade table, Gallup, the state maps,
the new-definition trend) → why do sources say 37%, 40%, 42% or 75% (the table; weighed or asked; which years and ages,
crude and age-adjusted; the new definition) → age, gender and education (two tables) → race and Hispanic origin (CDC's
cautions, the table with * and †) → severe obesity → children (link to the children's page) → use this chart or data (the
embeddable chart as an `<img>` listed in the image sitemap, CSV, embed code, copy button) → 12 FAQ → sources and method →
one related block. Every anchor of the old page is kept (19 pages link `#age-gender-education`).
No `<article>` (D-16), no page-level style (two `<style>` blocks removed: a copied `.bmi-chart` shell block and the `.cmb-*`
page styles), no inline style in `<main>` outside the figures; the embed code's own inline styles live in the textarea
for other sites. No visible dates (D-12). Head: title kept; new meta description, OG and Twitter text (with
`twitter:title` and `twitter:description`); the preferred image; JSON-LD `@graph`: Article (`@id` and `datePublished`
2026-09-30 kept, `dateModified` `{TODAY}`, author and publisher named, image list, `primaryImageOfPage`, 12 citations,
`isBasedOn` the Dataset), Dataset (kept: `@id`, CSV distribution, CC BY 4.0; creator named; `dateModified` `{TODAY}`
because the CSV gains two standard errors; the name, description and `measurementTechnique` name both surveys, NHES for
1960–1970 and NHANES since 1971–1974, and the child periods: ages 6–11 from 1963–1965, 12–17 in 1966–1970, 2–19 from
1971–1974), BreadcrumbList (kept), FAQPage (= the visible answers). The Organization and Person nodes go (named inside the
Article). The menu already marked this page.

### The tool ("Where do you fit?")
On the shared calculator parts (`.calculator-card.obw`, DESIGN.md "US obesity tool and embed code (CMB-022)"): ft, in, lb /
cm, kg toggle; one row of inputs per unit system (feet, inches, pounds; centimeters, kilograms); starting values 5′7″,
160 lb (170.2 cm, 72.6 kg); BMI rounded once to 0.1 as `calculator.js`; result card
tinted by the CDC category, the category's share of US adults and count, then the six-category table with the user's row
marked "You". The unit switch converts to 0.1 and restores the entered numbers when switched back with nothing retyped.

## Images
`research/preferred-images/pref_images.py ROOT us-obesity-statistics` draws the hero without a word or number: three lines
with a dot per survey in the category colours (red, amber, dark red) over grid lines at 0–50%, centered, at 1200×675,
1200×900 and 1200×1200. The S1 OG card `us-obesity-statistics/og-us-obesity-statistics.png` (text, 1200×630; only this page
used it) is deleted. The embeddable chart `us-obesity-trend-1960-2023.svg` keeps its URL, data and size; its series
colours move to the site's category colours (DESIGN.md "The Category Lock"; the old oranges were off-palette), and three
text fixes from the fact-check: its description names NHES (1960–1962) and NHANES and gives the overweight range (30.3% to
34.4%, not "near 31%"), and its subtitle reads "measured (NHES, NHANES)".

## Checks
- `obs_test_playwright.py` (589 checks): HE-Stat 111 Table 1 (45 + 15 values), Table 3, DB 508, HE-Stats 112 and 119,
  Series 3 No. 50 typed in again against the CSV and the stats; the 300 lb shares typed in again against `obs_stats.json`;
  Gallup, Fourman, Al-Roub, the Lancet Commission against `obs_sources.json`; the state file; the arithmetic done again
  (counts, subtractions, ratios, the 2.13 comparison rule); every sentence that states a number rebuilt and found on the
  page (FAQ answers included); removed wording (each sentence the fact-check replaced is listed and must stay off the
  page); all nine tables cell by cell; the hero's 45 dots, three lines, labels and the category bars at their drawn
  positions (bars from unrounded counts); the embeddable chart (data, colours, description, subtitle), the embed code, the
  CSV (rows, the two standard errors, its periods by age); the tool (starting values, 16 cases covering all six categories
  in both units, the 24.9/25.0 edge both ways, both unit round trips, one row of inputs per unit system, out-of-range
  messages, Enter); head, OG/Twitter, JSON-LD (the Dataset's name, description, `measurementTechnique` and `dateModified`),
  preferred images at size, `dateModified` = sitemap `lastmod`, the sitemap image entry; the menu; links, anchors (old ones
  kept), outside links in the registry and in a new tab; 10 chips; 12 FAQ with JSON-LD = visible text; widths
  320/360/390/1280, every table inside its frame (with the tool's results open); SVG labels off every shape, line and
  plotted line.
- Deliberate breaks (chat, 2026-10-30): 28 of 28 caught by the page test (a table cell, a hero dot, a prose number, the FAQ
  JSON-LD, the menu mark, the old og:image, `dateModified` against `lastmod`, a table without `--wrap`, two labels on top
  of each other, removed wording back, an outside link outside the registry, an inline style, `obs_sources.json`,
  `obs_stats.json`, an em dash, a chip to a missing anchor, a bar width, the tool's rounding and unit switch, the
  definitions table, the Dataset date and name, a CSV standard error, the embed code and its credit line, an FAQ question,
  a flagged race estimate shown, the state count).
- Chat's own checks before the fact-check: two tables overflowed a 320 px phone (261 and 280 px in a 240 px frame) → all
  tables take `.data-table--wrap`, cells keep 4 px beside the text under 360 px (styles.css), "Over&shy;weight" may break;
  the hero's year labels touched the "0%" label → moved down; accuracy: "every CDC survey" for the 1960s surveys (NCHS
  joined CDC in 1987) → "each survey of CDC's national series"; "Each survey covers about two years" (the early surveys
  ran longer, up to six years for 1988–1994) → "two years or more"; the CSV "every figure on this page" (the class split,
  counts and the other sources are not in it) → "the NCHS figures behind this page"; "That is also why every state's
  figure..." (a causal claim) → stated without the cause; "rather than fixing one set, so each study picks its own" (more
  than the paper says) → the paper's own requirement only; "The last two-year survey before that" (2017–2018 is part of
  2017–March 2020) → "Its first two years"; the rising-or-falling paragraph no longer reads the state maps as a trend;
  anti-slop (below).
- Independent fact-check (a separate agent, 2026-10-30; sources read live, NHANES reproduced from the raw files): 1 FAIL,
  4 WARN, 15 NOTE; no number on the page was wrong. Settled:
  - FAIL 1: "surveys before 1988 did not include people older than 74" (HE-Stat 111's own text, but its footnote 2 and the
    CSV say the 1960–1962 survey covered ages 18–79) → "the 1971–1974 and 1976–1980 surveys did not include anyone older
    than 74"; registry note on `nhanes-adult-weight-trends`.
  - WARN 1: "peaked at 42.8%" and "a peak of 42.4%" (2017–2018 is not significantly above 2021–2023: 0.72 and 0.80 times
    the standard error) → "highest estimate"; "the 40.8% of 2021–2023 is not significantly lower"; "not a significant
    change".
  - WARN 2: "overweight stayed near 31%" (it ran 30.3% to 34.4%; 2001–2002 and 2017–2018 differ from 1960–1962 by the
    page's own rule) → "between 30% and 35%" in the takeaway and the chart's alt text, "between 30.3% and 34.4%" in the
    figure descriptions; the paragraph says it "ended where it started"; OG alt "roughly level".
  - WARN 3: the state surveys used as evidence of a fall (21 states at 35% or more in 2025 against 19 in 2024; "none at
    40%" rests on Mississippi missing) → "CDC's state surveys, also self-reported, show no clear change", with both counts.
  - WARN 4: the All of Us row did not say the cohort is unweighted volunteers → "301,026 volunteers aged 18 to 80, not
    weighted to the US population"; the prose names WHO's race-specific cut-offs behind its 42.9%.
  - NOTES fixed: 1 race estimates "not shown" (CDC prints them flagged) → "CDC prints them flagged, and the table below
    leaves them out", cells "n/a*"; 2 the two "—*" cells (the only em dashes) → "n/a*"; 3 the age-adjustment groups add
    "60 to 74 for the 20-to-74 series"; 4 the 1960–1962 survey named (NHES) in the Method, the Dataset, the embeddable
    chart and the embed credit; 5 response rate "all ages"; 6 the decade's 7.7% → 9.7% labelled age-adjusted; 7 FAQ 12
    uses 26.2% (same basis as 51.1%); 8 FAQ 11 gives the share (2.9%, our calculation, `obs_stats.py`) instead of "fewer
    than 5%"; 9 "yet" removed ("no significant change"); 10 the BRFSS row says 47 states and DC had a 2025 figure; 11 FAQ
    4 says the top three are within each other's margins of error; 12 Al-Roub's 58.4% with a 0.6 cut-off added; 13 the
    category bars are drawn from unrounded counts and the caption says healthy weight is by subtraction; 14 the Dataset
    description's child periods corrected, the CSV's two blank standard errors filled, the CSV link no longer implies it
    holds every figure, and the comparison rule uses 2.13 (no claim fell between 2.0 and 2.13).
  - NOTE 15 kept: Gallup's 2026 article (36.8% "thus far in 2026", reweighted September 8, 2026) stays out; its table and
    text disagreed when last checked, so the page quotes 2025, the latest full year (registry note on
    `gallup-self-reported-obesity`).
  - The agent reproduced every NHANES share, the counts, ratios and population totals, all 45 trend points in both SVGs,
    the FAQ against its JSON-LD and the CSV's 194 values with standard errors. Not checked by it: Google's results page
    (the owner's pastes are the source), the Fourman and Al-Roub supplements, the full Lancet text (abstract only).
- anti-slop: 4 fixes (vague authority 1: "research suggests" → "CDC points to research that"; staging 2: "Not in the
  measured data, at least not yet" → "CDC's measured data show no significant change", "is what shrank" → "shrank
  instead"; borrowed authority 1: "Surveys ... point down" generalised from one survey → "A survey ... points down", later
  replaced by the fact-check wording). Rescored from the built HTML after the fact-check fixes: 0 tells and 0 em dashes in
  3,482 words of body prose (old page: 0 tells, 31 em dashes in 2,695 words).
