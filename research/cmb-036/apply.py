#!/usr/bin/env python3
"""CMB-036 SOURCES-1: batch 3 of the scores run (D-26), the S items on eight pages. Every number the Stage 1 audit could
not trace now traces to a registry row read on 2026-11-13, or the claim is cut (D-10). Every replacement must match
exactly once (or the count given), so a page that changed since stops the run.
usage: python3 research/cmb-036/apply.py [--check]   (--check counts the matches and writes nothing)

1. Winter et al. 2014 (registry winter-2014-bmi-mortality-65): the abstract compares each BMI band with 23.0-23.9; risk
   was higher below 23.0 and "began to increase for BMI >33.0". "Lowest mortality across BMI 23-33", "plateau" and "rose
   ... above 33" said more than that. Every page now uses the wording the D-14 pages use: compared with a BMI of 23 to
   23.9, the risk of death was higher below 23 and began to rise at about 33. /age-bmi-calculator/ keeps its lines for
   its own rebuild (§5).
2. /: the bare "ask a doctor" clause goes (§4: a see-a-doctor line needs a source that says when); the Lancet Commission
   lines add the Commission's own exception, BMI above 40 (registry lancet-clinical-obesity-2025 notes).
3. /blog/bmi-categories/: Flegal 2013 without the derived "6% lower" and "29% higher" (the hazard ratios stay); "more
   than 2.88 million" as the abstract says; the pre-1998 US definition with its real source (NHLBI 1998: the NHANES II
   85th percentiles at ages 20 to 29, called overweight) instead of "1985: NIH defined obesity"; the unsourced "millions
   ... overnight" and "based on the observation that ..." go; each WHO report linked where its year is named.
4. /blog/bmi-limitations/: Quetelet 1832 and Keys 1972 from Eknoyan 2008; the NFL lines and the athlete card from
   Provencher 2018 (53.4% obese by BMI, 8.9% by body fat) instead of "BMI 27-32, body fat 8-15%" and "body fat under 15%";
   "Up to 30% of people with normal BMI" goes (no source).
5. /blog/bmi-and-health-risks/: the 5-10% lines credited to "CDC and NHLBI" and "most clinical guidelines" now say what
   the Look AHEAD trial found (Wing 2011, registry wing-2011-look-ahead); its unsourced list of seven benefits, the NAFLD
   "7-10% ... most clinical guidelines" paragraph and "Sarcopenia, height loss ... all contribute" go; the athlete FAQ
   gives Provencher 2018 instead of a 10% body-fat example.
6. /blog/bmi-chart-explained/: "22-23 lowest mortality" becomes the Global BMI Mortality Collaboration's 20 to 25
   (registry gbmc-2016-bmi-mortality); "BMI 25-27 may be healthy" becomes CDC's "BMI does not distinguish between fat,
   muscle, and bone mass"; the age table starts at 20 (CDC's adults); the two WHO reports are linked; "Men are more
   likely to be overweight" goes (no test of the difference on the page; §4 NHANES comparison rule).
7. /blog/bmi-by-age/ and /calculators/: the Winter wording; the bare "discuss ... with a clinician" line goes; the
   prevalence sources are linked where they are named.
8. Dates (§4): schema dateModified, article:modified_time and the sitemap lastmod of the eight pages move to the day the
   batch is applied, as date_truth expects for a commit that changes their visible text.
"""
import datetime
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv   # count the matches only; write nothing

PUB = 'https://pubmed.ncbi.nlm.nih.gov/'
WINTER = f'<a href="{PUB}24452240/" target="_blank" rel="noopener">'
FLEGAL = '<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4855514/" target="_blank" rel="noopener">'
PROV = '<a href="https://doi.org/10.1519/JSC.0000000000002449" target="_blank" rel="noopener">'
WING = '<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/" target="_blank" rel="noopener">'
EKNOYAN = '<a href="https://doi.org/10.1093/ndt/gfm517" target="_blank" rel="noopener">'
TRS854 = '<a href="https://www.who.int/publications/i/item/9241208546" target="_blank" rel="noopener">'
TRS894 = f'<a href="{PUB}11234459/" target="_blank" rel="noopener">'
GBMC = '<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/" target="_blank" rel="noopener">'
CDCCAT = '<a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" target="_blank" rel="noopener">'
CDCABOUT = '<a href="https://www.cdc.gov/bmi/about/index.html" target="_blank" rel="noopener">'
DB508 = '<a href="https://www.cdc.gov/nchs/products/databriefs/db508.htm" target="_blank" rel="noopener">'
HESTAT = '<a href="https://www.cdc.gov/nchs/data/hestat/hestat111.htm" target="_blank" rel="noopener">'
NHLBI98 = '<a href="https://www.ncbi.nlm.nih.gov/books/NBK2003/" target="_blank" rel="noopener">'

W_OLD_HOME = 'found that the risk of death rose below a BMI of 23 and above 33 ('
W_NEW_HOME = 'found that, compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 ('

PROV_TEXT = ('At the NFL Scouting Combine, 53.4% of prospects had a BMI of 30 or more, but only 8.9% had obesity by '
             'measured body fat')
WING_TEXT = ('In the Look AHEAD trial of adults with overweight or obesity and type 2 diabetes, those who lost 5% to under '
             '10% of their weight in a year had greater odds of improving blood sugar (HbA1c), blood pressure, HDL '
             'cholesterol and triglycerides')

EDITS = {
    'index.html': [
        (W_OLD_HOME, W_NEW_HOME, 2),
        ('; if your BMI is under 18.5 and you don’t know why, ask a doctor.', '.', 1),
        ('a direct body-fat measurement instead of diagnosing obesity from BMI alone.',
         'a direct body-fat measurement instead of diagnosing obesity from BMI alone, except above a BMI of 40, where it '
         'says excess body fat can be assumed.', 2),
        ('a direct body-fat measurement, instead of diagnosing obesity from BMI alone.',
         'a direct body-fat measurement, instead of diagnosing obesity from BMI alone. Above a BMI of 40, it says, excess '
         'body fat can be assumed.', 1),
    ],
    'men-bmi-calculator/index.html': [(W_OLD_HOME, W_NEW_HOME, 2)],
    'calculators/index.html': [
        (f'Uses the WHO adult 18.5&ndash;24.9 range for all adults, then adds the {WINTER}Winter et al., <em>Am J Clin '
         'Nutr</em>, 2014</a> observational finding: the BMI band with the lowest observed mortality in adults 65+ is '
         '23&ndash;33.</p>',
         'Uses the WHO adult 18.5&ndash;24.9 range for all adults, then adds a finding for adults 65 and over: compared '
         f'with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to rise at about 33 ({WINTER}Winter '
         'et al., <em>Am J Clin Nutr</em>, 2014</a>).</p>', 1),
        ('has a standard BMI of <strong>25.0</strong>. This falls within the <strong style="color:var(--gray-900);">'
         f'observed lower-mortality band for adults 65+ (23&ndash;33 in {WINTER}Winter et al., <em>Am J Clin Nutr</em>, '
         '2014</a>)</strong>, per the Winter 2014 meta-analysis.',
         'has a standard BMI of <strong>25.0</strong>. In a meta-analysis of adults 65 and over, the risk of death was '
         f'higher below a BMI of 23 and began to rise at about 33 ({WINTER}Winter et al., <em>Am J Clin Nutr</em>, '
         '2014</a>); 25.0 lies between the two.', 1),
    ],
    'blog/bmi-by-age/index.html': [
        ('Includes NCHS obesity data by age and the Winter 2014 plateau for 65+.',
         'Includes NCHS obesity data by age and the Winter 2014 findings for adults 65 and over.', 2),
        ('Includes NCHS obesity data by age and the Winter et al. (Am J Clin Nutr, 2014) plateau for 65+.',
         'Includes NCHS obesity data by age and the Winter et al. (Am J Clin Nutr, 2014) findings for adults 65 and over.', 1),
        ('Includes NCHS obesity data by age and the Winter et al., Am J Clin Nutr, 2014 plateau for 65+.',
         'Includes NCHS obesity data by age and the Winter et al., Am J Clin Nutr, 2014 findings for adults 65 and over.', 1),
        ('Adults aged 65+ and the observational plateau', 'Adults aged 65 and over', 1),
        ('In a two-stage random-effects meta-analysis of 32 cohort studies (197,940 adults aged 65+), Winter et al. '
         '(<em>American Journal of Clinical Nutrition</em>, 2014) reported that mortality was lowest across a wider BMI '
         'band (roughly 23 to 33) than the WHO healthy range. This is an observational finding, not a category change: '
         'the CDC and WHO cut-offs remain the same for adults of all ages. Older adults with a BMI toward the lower end of '
         'the healthy band may want to discuss weight and body-composition goals with a clinician, particularly if muscle '
         'loss is a concern.</p>',
         'In a meta-analysis of 32 cohort studies (197,940 adults aged 65 and over), Winter et al. (<em>American Journal '
         'of Clinical Nutrition</em>, 2014) compared each BMI band with 23 to 23.9: the risk of death was higher below 23 '
         'and began to rise at about 33. The finding changes no category: the CDC and WHO cut-offs remain the same for '
         'adults of all ages.</p>', 1),
        ('from NCHS Data Brief 508 (NHANES August 2021&ndash;August 2023, adults 20+) and NCHS Health E-Stat 111 '
         '(Fryar/Afful/Saif, Feb 2026), both linked above. The 65+ mortality plateau reference is ',
         f'from {DB508}NCHS Data Brief 508</a> (NHANES August 2021&ndash;August 2023, adults 20+) and {HESTAT}NCHS '
         'Health E-Stat 111</a> (Fryar/Afful/Saif, Feb 2026). The 65+ mortality figures are from ', 1),
        ('Observational research reports a wider mortality plateau in adults aged 65 and over, but the published '
         'categories themselves don&rsquo;t shift.',
         'A meta-analysis of adults aged 65 and over found a higher risk of death below a BMI of 23, but the published '
         'categories themselves don&rsquo;t shift.', 1),
        ('In older adults, the 65+ mortality plateau reported by ',
         'In older adults, the higher risk of death below a BMI of 23 reported by ', 1),
    ],
    'blog/bmi-chart-explained/index.html': [
        ('<strong>Standard charts</strong> use WHO categories that apply to adults 20+ of any sex',
         f'<strong>Standard charts</strong> use the WHO categories, which {CDCCAT}CDC</a> applies to adults 20 and older '
         'regardless of sex', 1),
        ('The standard BMI categories used on charts follow the WHO classification system established in 1995 and '
         'refined in 2000. Here is',
         f'The categories on BMI charts follow the WHO classification, set out in a {TRS854}1995 WHO report</a>; a '
         f'{TRS894}2000 WHO report</a> named the three classes of obesity. Here is', 1),
        ('Men are more likely to be overweight, while obesity rates are similar between sexes: NCHS found no significant '
         'difference (',
         'Obesity rates are similar: NCHS found no significant difference between men and women (', 1),
        ('Observational research does show that the BMI band associated with the lowest all-cause mortality in older '
         'adults is wider than the WHO normal range.',
         'In adults 65 and over, a meta-analysis found that, compared with a BMI of 23 to 23.9, the risk of death was '
         f'higher below 23 and began to rise at about 33 ({WINTER}Winter et al., 2014</a>).', 1),
        ('<td><strong>18&ndash;64 years</strong></td> <td>18.5 &ndash; 24.9</td> <td>WHO cut-offs apply; no separate '
         'age-adjusted range published.</td>',
         '<td><strong>20&ndash;64 years</strong></td> <td>18.5 &ndash; 24.9</td> <td>The same cut-offs at every adult '
         f'age ({CDCCAT}CDC</a>).</td>', 1),
        ('<td>Lowest all-cause mortality observed across BMI 23&ndash;33 in ',
         '<td>Compared with BMI 23&ndash;23.9, the risk of death was higher below 23 and began to rise at about 33 (', 1),
        ('</a> (n=197,940). An association from cohort data &mdash; not a WHO recommendation.</td>',
         '</a>; 197,940 people). An association from cohort data, not a WHO recommendation.</td>', 1),
        ('<strong>Optimal range:</strong> Many studies suggest BMI 22-23 is associated with the lowest mortality',
         '<strong>Lowest mortality:</strong> in a pooled analysis of 239 studies, all-cause mortality was lowest at a BMI '
         f'of 20 to 25 ({GBMC}Global BMI Mortality Collaboration, 2016</a>)', 1),
        ('<strong>Important context:</strong> Many people in this range, especially those with BMI 25-27, may be healthy '
         'if they are muscular or have good metabolic markers',
         f'<strong>Important context:</strong> BMI does not distinguish between fat, muscle, and bone mass ({CDCABOUT}CDC'
         '</a>), so a muscular person can fall in this range', 1),
    ],
    'blog/bmi-and-health-risks/index.html': [
        ('<li><strong>Reversible risk:</strong> 5&ndash;10% weight loss produces clinically meaningful improvements in '
         'most weight-related conditions.</li>',
         '<li><strong>Modest weight loss:</strong> in a trial of adults with type 2 diabetes, those who lost 5% to under '
         '10% of their weight in a year were more likely to improve blood sugar, blood pressure and blood fats (Wing et '
         'al., 2011).</li>', 1),
        ('For adults 65+, the observational plateau reported by ' + WINTER + 'Winter et al. 2014 (<em>Am J Clin Nutr</em>)'
         '</a> is different in shape (see the',
         'For adults 65 and over, ' + WINTER + 'Winter et al. 2014 (<em>Am J Clin Nutr</em>)</a> found a higher risk of '
         'death below a BMI of 23 than at 23 to 23.9, and a risk that began to rise at about 33 (see the', 1),
        ('<p>Early-stage NAFLD is largely reversible with weight loss. Losing ~7&ndash;10% of body weight is the target '
         'cited in most clinical guidelines to reduce liver fat and inflammation.</p>', '', 1),
        ('(n=197,940) observed the lowest all-cause mortality across BMI 23&ndash;33 in adults aged 65 and older, a wider '
         'low-mortality plateau than the WHO healthy adult range (18.5&ndash;24.9). Sarcopenia, height loss, and reduced '
         'nutritional reserves all contribute. This is',
         'of 197,940 adults aged 65 and over found that, compared with a BMI of 23 to 23.9, the risk of death was higher '
         'below 23, inside the WHO healthy adult range (18.5&ndash;24.9), and began to rise at about 33. This is', 1),
        ('<h3>Benefits of 5&ndash;10% weight loss</h3> <p>Guideline bodies including CDC and <a '
         'href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" target="_blank" rel="noopener">NHLBI</a> '
         'describe 5&ndash;10% weight loss as producing meaningful clinical improvements across multiple domains:</p> '
         '<ul> <li><strong>Type 2 diabetes:</strong> substantial reduction in progression from prediabetes to type 2 '
         'diabetes (the primary evidence base is the Diabetes Prevention Program trial).</li> <li><strong>Blood '
         'pressure:</strong> measurable reduction, especially in adults who start hypertensive.</li> '
         '<li><strong>Lipids:</strong> improvement in LDL cholesterol and triglycerides.</li> <li><strong>Sleep '
         'apnea:</strong> reduction in apnea-hypopnea index in many patients.</li> <li><strong>Joint pain:</strong> '
         'reduction in knee osteoarthritis symptoms.</li> <li><strong>Liver health:</strong> reduction in liver fat and '
         'NAFLD/NASH activity.</li> <li><strong>Inflammation:</strong> decreases in inflammatory markers such as CRP and '
         'IL-6.</li> </ul>',
         f'<h3>Benefits of modest weight loss</h3> <p>{WING_TEXT} ({WING}Wing et al., 2011</a>).</p>', 1),
        ('Modest weight loss (~5–10% of body weight, the target most clinical guidelines describe) is associated with '
         'measurable improvements in blood pressure, blood sugar, lipid profile, and joint symptoms.',
         f'{WING_TEXT} (Wing et al., 2011).', 1),
        ('Modest weight loss (~5&ndash;10% of body weight, the target most clinical guidelines describe) is associated '
         'with measurable improvements in blood pressure, blood sugar, lipid profile, and joint symptoms.',
         f'{WING_TEXT} ({WING}Wing et al., 2011</a>).', 1),
        ('A strength athlete with 10% body fat may be classified as &ldquo;overweight&rdquo; or even &ldquo;obese&rdquo; '
         'on BMI alone.', f'{PROV_TEXT} ({PROV}Provencher et al., 2018</a>).', 1),
        ('The primary source most often cited is ', 'The pooled analysis behind it is ', 1),
    ],
    'blog/bmi-categories/index.html': [
        ('all-cause mortality in the overweight range was about 6% lower than in the healthy range (hazard ratio 0.94;',
         'all-cause mortality in the overweight range was slightly lower than in the healthy range (hazard ratio 0.94;', 1),
        ('In a pooled analysis of 97 studies covering about 2.88 million people, all-cause mortality was about 29% higher '
         'at a BMI of 35 or more than in the healthy range (hazard ratio 1.29;',
         'In a pooled analysis of 97 studies covering more than 2.88 million people, all-cause mortality was higher at a '
         'BMI of 35 or more than in the healthy range (hazard ratio 1.29;', 1),
        (f'<p>The 29% higher all-cause mortality reported for BMI 35 and above in the pooled analysis includes this class '
         f'({FLEGAL}Flegal et al., JAMA 2013</a>); the risks listed for classes I and II apply here at their highest.</p>',
         f'<p>The higher all-cause mortality reported for BMI 35 and above in the pooled analysis (hazard ratio 1.29) '
         f'includes this class ({FLEGAL}Flegal et al., JAMA 2013</a>).</p>', 1),
        ('<strong>1985:</strong> The National Institutes of Health defined obesity as BMI &ge; 27.8 for men and &ge; '
         '27.3 for women, based on the 85th percentile of NHANES II data for young adults.</li>',
         '<strong>Before 1998:</strong> US surveys counted adults as overweight at a BMI of 27.8 or more for men and '
         f'27.3 or more for women, the 85th percentiles at ages 20 to 29 in NHANES II ({NHLBI98}NHLBI, 1998</a>).</li>', 1),
        ('The WHO recommended unified cutoffs of 25 (overweight) and 30 (obesity) regardless of sex, based on the '
         'observation that health risks rise continuously above BMI 25 and increase more sharply above 30.</li>',
         'The WHO recommended unified cutoffs of 25 (overweight) and 30 (obesity) regardless of sex.</li>', 1),
        ('The NIH aligned U.S. Guidelines with the WHO cutoffs. This single change reclassified millions of Americans '
         'from &ldquo;normal&rdquo; to &ldquo;overweight&rdquo; overnight &mdash; not because anyone gained weight, but '
         'because the threshold moved (',
         'The NIH aligned U.S. guidelines with the WHO cut-offs. Nobody&rsquo;s weight changed, but adults between 25 '
         'and the old thresholds now counted as overweight (', 1),
        ('<strong>2000:</strong> The WHO published Technical Report 894, which set out obesity classes I, II and III; the '
         'thinness grades come from its 1995 report. </ul>',
         f'<strong>2000:</strong> The WHO published {TRS894}Technical Report 894</a>, which set out obesity classes I, '
         'II and III; the thinness grades come from its earlier report on anthropometry.</li> </ul>', 1),
        ('The World Health Organization set out the current classification in a 1995 expert report and added the obesity '
         'classes in a 2000 technical report; the ',
         f'The World Health Organization set out the current classification in a {TRS854}1995 expert report</a> and '
         f'added the obesity classes in a {TRS894}2000 technical report</a>; the ', 1),
        ('for adults 65+, observational data (Winter 2014 meta-analysis) show a wider low-mortality plateau.',
         'in adults 65 and over, compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to '
         'rise at about 33 (Winter 2014 meta-analysis).', 1),
        (f'for adults 65+, observational data ({WINTER}Winter 2014 meta-analysis</a>) show a wider low-mortality plateau.',
         'in adults 65 and over, compared with a BMI of 23 to 23.9, the risk of death was higher below 23 and began to '
         f'rise at about 33 ({WINTER}Winter 2014 meta-analysis</a>).', 1),
    ],
    'blog/bmi-limitations/index.html': [
        ('<p>Body Mass Index was invented in the 1830s by Belgian mathematician Adolphe Quetelet - notably, not a '
         'physician. Quetelet',
         '<p>Body Mass Index began as the Quetelet index, described in 1832 by the Belgian mathematician, astronomer and '
         f'statistician Adolphe Quetelet ({EKNOYAN}Eknoyan, 2008</a>). Quetelet', 1),
        ('<p>BMI entered medicine later: Ancel Keys named it in 1972, and NIH and WHO guidelines adopted it in the 1980s '
         'and 1990s (see our <a href="/blog/bmi-history/">BMI history</a>). Today,',
         f'<p>Ancel Keys named it the Body Mass Index in 1972 ({EKNOYAN}Eknoyan, 2008</a>); our <a '
         'href="/blog/bmi-history/">BMI history</a> follows how health agencies took it up. Today,', 1),
        ('<text x="22" y="50" font-size="10">BMI reads 27–32</text> <text x="22" y="66" font-size="10">Body fat often '
         '8–15%</text>',
         '<text x="22" y="50" font-size="10">NFL prospects: 53.4% obese by BMI</text> <text x="22" y="66" '
         'font-size="10">but 8.9% obese by body fat (2018)</text>', 1),
        ('For example, many NFL players have BMIs over 30 but body fat under 15%."',
         f'{PROV_TEXT} (Provencher et al., 2018)."', 1),
        ('For example, many NFL players have BMIs over 30 but body fat under 15%.</p>',
         f'{PROV_TEXT} ({PROV}Provencher et al., 2018</a>).</p>', 1),
        (' Up to 30% of people with "normal" BMI may actually have unhealthy body fat levels.', '', 1),
        ('In a meta-analysis of adults aged 65 and over, the lowest death rates were seen across BMI 23 to 33 (',
         'In a meta-analysis of adults aged 65 and over, compared with a BMI of 23 to 23.9, the risk of death was higher '
         'below 23 and began to rise at about 33 (', 1),
    ],
}


def rx(literal):
    """The literal with every run of spaces matching any whitespace (the pages wrap lines in places)."""
    return re.compile(r'\s+'.join(re.escape(part) for part in literal.split(' ')))


def set_dates(rel, t):
    t, n = re.subn(r'("dateModified": ?")\d{4}-\d{2}-\d{2}(")', rf'\g<1>{TODAY}\g<2>', t)
    t = re.sub(r'(article:modified_time" content=")\d{4}-\d{2}-\d{2}', rf'\g<1>{TODAY}', t)
    return t


def main():
    for rel, edits in EDITS.items():
        p = REPO / rel
        t = p.read_text(encoding='utf-8')
        for old, new, want in edits:
            pat = rx(old)
            got = len(pat.findall(t))
            if CHECK:
                if got != want:
                    print('MISMATCH', rel, got, want, '|', old[:100])
                continue
            assert got == want, (rel, old[:90], got, want)
            t = pat.sub(lambda m: new, t)
        if CHECK:
            continue
        t = set_dates(rel, t)
        p.write_text(t, encoding='utf-8')
        print('edited', rel)
    if CHECK:
        print('check done')
        return
    sm = REPO / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    for rel in EDITS:
        loc = 'https://calculatemybmi.net/' + ('' if rel == 'index.html' else rel[:-len('index.html')])
        s, n = re.subn(rf'(<loc>{re.escape(loc)}</loc>\s*<lastmod>)\d{{4}}-\d{{2}}-\d{{2}}', rf'\g<1>{TODAY}', s)
        assert n == 1, (loc, n)
    sm.write_text(s, encoding='utf-8')
    print('sitemap lastmod', TODAY, 'for', len(EDITS), 'pages')


if __name__ == '__main__':
    main()
