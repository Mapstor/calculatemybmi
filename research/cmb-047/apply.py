#!/usr/bin/env python3
"""CMB-047 MEN-CHECK: the full check of /men-bmi-calculator/ (D-26: "no full check") found six passages the rules
don't let stand; each is fixed in place, nothing else on the page changes.
  1. "Average BMI is highest in men in their 40s and 50s (30.5 and 30.2)": no interval supports "highest" over the 30s,
     60s and 70s (§4 peak rule). Now the comparison the data support: higher in the 40s and 50s than in the 20s (27.8),
     each difference's 95% interval above 0 (research/age-calc-build/abc_stats.json, men_mean_40-49 and 50-59 minus
     20-29).
  2. "A BMI under 18.5 can reflect undernutrition or an illness and is also worth checking with a doctor": no source and
     a bare doctor line (§4). Cut; the paragraph's link to the health-risks guide stays and the underweight guide joins it.
  3. "When to see a doctor", a five-item list with no source that says when (§4): replaced by CDC's own line from the
     Adult BMI Calculator page, quoted and linked (read in Chrome, 2026-11-14; registry cdc-adult-bmi-categories).
  4. "Blood pressure, blood sugar and cholesterol: routine checks that BMI can't replace": unsourced; now what CDC's About
     BMI page says ("For individuals, BMI should be considered with other factors, such as blood pressure, cholesterol
     levels", registry cdc-about-bmi).
  5. "How to measure your waist": "Don't pull your stomach in" and "to the nearest half inch (or 1 cm)" are in no source.
     The steps now say only what NHLBI says (Aim for a Healthy Weight: "stand and place a tape measure around your
     middle, just above your hipbones. Measure your waist just after you breathe out."; the 1998 guidelines' NHANES III
     box: the tape "parallel to the floor", "snug, but does not compress the skin", read "at a normal minimal
     respiration"; both read in Chrome, 2026-11-14), and a line under the list names both.
  6. The sources list credited NHLBI's "Overweight and Obesity" pages with the measuring method; they give none. The
     item now links Aim for a Healthy Weight, which gives the cut-off, the conditions and the method.
The visible text changes, so the sitemap lastmod moves to the commit's day (the page has no dateModified; §4). Files are
checked by SHA-256 before any edit; every marker must occur once.
usage: python3 research/cmb-047/apply.py [--check]   Run order from main: registry.py, apply.py."""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PAGE = 'men-bmi-calculator/index.html'
BASE = {PAGE: '767effb0e082c9f97161a026f956233e9820a2d42175acebd21bb7cc1242a4c0',
        'sitemap.xml': '1d59f88e2ef448b7e6a487dc69cd345971408efba2c638ce6e2f6f941f0f45ac'}
CDC_CALC = 'https://www.cdc.gov/bmi/adult-calculator/index.html'
CDC_ABOUT = 'https://www.cdc.gov/bmi/about/index.html'
EXT = 'target="_blank" rel="noopener"'
NHLBI_HW = 'https://www.nhlbi.nih.gov/health/heart-healthy-living/healthy-weight'
NHLBI_BOX = 'https://www.ncbi.nlm.nih.gov/books/NBK2004/box/A236/'
EDITS = {
    PAGE: [
        ('Average BMI is highest in men in their 40s and 50s (30.5 and 30.2).',
         'Average BMI was higher in men’s 40s and 50s (30.5 and 30.2) than in their 20s (27.8); each difference is larger '
         'than its margin of error.'),
        ('<p>A BMI under 18.5 can reflect undernutrition or an illness and is also worth checking with a doctor. The evidence '
         'behind each risk is in <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>.</p>',
         '<p>The evidence behind each risk is in <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>; for a BMI '
         'under 18.5, see <a href="/blog/underweight-bmi-risks/">underweight BMI risks</a>.</p>'),
        ('<h3>When to see a doctor</h3> <ul> <li>Your BMI is 30 or higher, or under 18.5.</li> <li>Your waist is more than 40 '
         'inches (102 cm).</li> <li>Your weight changes quickly without a clear reason.</li> <li>You snore loudly, stop '
         'breathing or gasp in your sleep, or feel very sleepy during the day.</li> <li>Heart disease, type 2 diabetes or '
         'stroke runs in your family.</li> </ul>',
         '<h3>Talking with a health care provider</h3> <p>CDC’s Adult BMI Calculator page says: “Persons may consider '
         f'seeking advice from their health care providers about their BMI” (<a href="{CDC_CALC}" {EXT}>CDC</a>).</p>'),
        ('<li><strong>Blood pressure, blood sugar and cholesterol:</strong> routine checks that BMI can’t replace.</li>',
         '<li><strong>Blood pressure and cholesterol:</strong> CDC lists both among the other factors to consider with BMI '
         f'for an individual (<a href="{CDC_ABOUT}" {EXT}>CDC</a>).</li>'),
        ('<li>Stand up straight and breathe out normally. Don’t pull your stomach in.</li> <li>Put a tape measure around your '
         'bare waist, just above your hip bones.</li> <li>Keep the tape snug and level all the way round, without pressing '
         'into the skin.</li> <li>Read it at the end of a normal breath out, to the nearest half inch (or 1 cm).</li> </ol> '
         '<p>Measure at the same time of day',
         '<li>Stand and breathe normally.</li> <li>Put a tape measure around your bare waist, just above your hip '
         'bones.</li> <li>Keep the tape snug and level all the way round, without pressing into the skin.</li> <li>Breathe '
         'out, then read the tape.</li> </ol> <p>These steps are NHLBI’s, from its '
         f'<a href="{NHLBI_HW}" {EXT}>Aim for a Healthy Weight</a> page and the waist-measuring protocol in its '
         f'<a href="{NHLBI_BOX}" {EXT}>1998 guidelines</a>. Measure at the same time of day'),
        (f'<a href="https://www.nhlbi.nih.gov/health/overweight-and-obesity" {EXT}>Overweight and Obesity</a>: waist cut-off, '
         'conditions linked to excess weight, measuring method.</li>',
         f'<a href="{NHLBI_HW}" {EXT}>Aim for a Healthy Weight</a>: waist cut-off, conditions linked to excess weight, '
         'measuring method.</li>'),
    ],
    'sitemap.xml': [
        ('<url><loc>https://calculatemybmi.net/men-bmi-calculator/</loc><lastmod>2026-11-13</lastmod>',
         f'<url><loc>https://calculatemybmi.net/men-bmi-calculator/</loc><lastmod>{TODAY}</lastmod>'),
    ],
}


def main():
    for rel, edits in EDITS.items():
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        for old, new in edits:
            assert src.count(old) == 1, f'{rel}: marker found {src.count(old)} times: {old[:70]}'
            src = src.replace(old, new)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: {len(edits)} edit(s){" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
