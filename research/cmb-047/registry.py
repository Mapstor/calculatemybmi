#!/usr/bin/env python3
"""CMB-047: the registry and the page map for /men-bmi-calculator/'s full check.
  - research/data-sources.csv:
      cdc-adult-bmi-categories gains CDC's Adult BMI Calculator page as an endpoint, with the sentence the page now quotes
      in place of its unsourced "When to see a doctor" list;
      nhlbi-1998-obesity-guidelines gains three endpoints, each with what it says (all read in Chrome, 2026-11-14):
      NHLBI's Aim for a Healthy Weight page (the measuring method and the cut-off), the guidelines' NHANES III
      measuring box, and NHLBI's Overweight and Obesity pages (five other pages link them; they give no method);
      men-bmi-calculator joins pages_served on the rows the page cites.
  - research/page-map.csv: data_source becomes nhanes-2021-2023-exam-files, the page's main dataset (the free text
    failed check_sources.py), and the notes name the page test.
usage: python3 research/cmb-047/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'men-bmi-calculator'
CITED = ('nhanes-2021-2023-exam-files', 'nhanes-anthropometric-reference', 'nhanes-adult-weight-trends',
         'nhanes-2011-2018-dxa', 'cdc-adult-bmi-categories', 'cdc-calculating-bmi', 'cdc-about-bmi',
         'nhlbi-1998-obesity-guidelines', 'who-2008-waist-hip-ratio', 'provencher-2018-nfl-combine',
         'wing-2011-look-ahead', 'winter-2014-bmi-mortality-65', 'gallagher-2000-bf-ranges')
ENDPOINTS = {
    'cdc-adult-bmi-categories': (
        ['https://www.cdc.gov/bmi/adult-calculator/index.html'],
        ' CMB-047 (read in Chrome, 2026-11-14): CDC\'s Adult BMI Calculator page (endpoint) says "Persons may consider '
        'seeking advice from their health care providers about their BMI."; /men-bmi-calculator/ quotes it.'),
    'nhlbi-1998-obesity-guidelines': (
        ['https://www.nhlbi.nih.gov/health/heart-healthy-living/healthy-weight',
         'https://www.ncbi.nlm.nih.gov/books/NBK2004/box/A236/',
         'https://www.nhlbi.nih.gov/health/overweight-and-obesity'],
        ' CMB-047 (all three endpoints read in Chrome, 2026-11-14): NHLBI\'s Aim for a Healthy Weight page (the old '
        'lose_wt/risk.htm address redirects to it; last updated December 11, 2025): "A waist circumference of more than 35 '
        'inches for women or more than 40 inches for men increases your risk."; "To correctly measure your waist '
        'circumference, stand and place a tape measure around your middle, just above your hipbones. Measure your waist '
        'just after you breathe out."; the more body fat and weight, "the more likely you are to develop heart disease, '
        'high blood pressure, type 2 diabetes, breathing problems, and certain cancers". The guidelines\' box "Instructions '
        'for Measuring Waist Circumference, According to NHANES III Protocol": the subject stands; the tape goes around the '
        'abdomen at a mark just above the right iliac crest; "The plane of the tape is parallel to the floor and the tape '
        'is snug, but does not compress the skin. The measurement is made at a normal minimal respiration." '
        '/men-bmi-calculator/\'s measuring steps say only what these two say. NHLBI\'s Overweight and Obesity pages (last '
        'updated March 24, 2022): "Nearly 3 in 4 adults age 20 or older in the United States have either overweight or '
        'obesity"; obesity "raises the risk for heart disease" and "is linked to many other health problems, including type '
        '2 diabetes and cancer"; Symptoms and Diagnosis (/symptoms): adult categories under 18.5, 18.5 to 24.9, 25 to 29.9, '
        '30 or above; "For men, an unhealthy waist circumference is greater than 40 inches. For women, an unhealthy waist '
        'circumference is greater than 35 inches."; no measuring method.'),
}
PM = {'data_source': 'nhanes-2021-2023-exam-files',
      'notes': ('Chart queries moved to blog/bmi-chart-men (B3). Full check CMB-047: page test '
                'research/men-pilot/men_test_playwright.py (every number from men_stats.json, which men_stats.py rebuilds '
                'from the raw CDC files, avgw_results.json, bfpc_stats.json and the registry rows); title, H1 and URL kept '
                '(D-28).')}


def rewrite(path, change):
    raw = path.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    n = change(rows)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def registry(rows):
    n = 0
    by = {x['domain']: x for x in rows}
    for d in CITED:
        r = by[d]
        served = [s.strip() for s in r['pages_served'].split(';') if s.strip()]
        if SLUG not in served:
            r['pages_served'] = ';'.join(served + [SLUG])
            n += 1
    for d, (urls, note) in ENDPOINTS.items():
        r = by[d]
        eps = [e.strip() for e in r['endpoint'].split(' ; ') if e.strip()]
        new = [u for u in urls if u not in eps]
        if new:
            r['endpoint'] = ' ; '.join(eps + new)
            n += 1
        if 'CMB-047' not in r['notes']:
            r['notes'] = (r['notes'].rstrip() + note).strip()
            n += 1
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    r.update(PM)
    return int(before != r)


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
