#!/usr/bin/env python3
"""CMB-017 registry, page map, DESIGN.md and the image gate: /women-bmi-calculator/ sources (verified in chat 2026-10-14 to
2026-10-22), the waist field and result boxes in DESIGN.md, and the page's preferred image in check_images.py.
usage: patch_cmb017.py REPO_ROOT"""
import sys, os, csv, io, json

ROOT = sys.argv[1]
SLUG = 'women-bmi-calculator'
S = json.load(open(os.path.join(ROOT, 'research/women-calc-build/wbc_stats.json')))

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2021-2023-exam-files', 'nhanes-2011-2018-dxa', 'nhanes-anthropometric-reference', 'cdc-adult-bmi-categories',
        'cdc-calculating-bmi', 'cdc-child-bmi-categories', 'nhlbi-1998-obesity-guidelines', 'nice-ng246-ethnicity-thresholds',
        'ada-2026-obesity-standards', 'cdc-ndpp-eligibility', 'who-2004-asian-bmi', 'winter-2014-bmi-mortality-65',
        'cdc-pregnancy-weight-gain')
T, DEC = S['table'], S['decades']

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    linked = set()
    for r in rows[1:]:
        d = r[ix['domain']]
        if d in USED:
            ps = [x for x in r[ix['pages_served']].split(';') if x]
            if SLUG not in [x.strip() for x in ps]: ps.append(SLUG)
            r[ix['pages_served']] = ';'.join(ps); linked.add(d)
        if d == 'nhanes-2021-2023-exam-files':
            r[ix['notes']] += (
                ' CMB-017 (2026-10-22): women aged 20+ (3,249) BMI percentile curves for all women and for 20-39 (826), 40-59 '
                f'(947) and 60+ (1,476), research/women-calc-build/wbc_stats.py (medians {T["all"]["p50"]:.1f} / '
                f'{T["20-39"]["p50"]:.1f} / {T["40-59"]["p50"]:.1f} / {T["60+"]["p50"]:.1f}); the all-women curve equals '
                'research/home-build/home_stats.json; BMI by decade (decade means equal research/average-weight/'
                'avgw_results.json); decade differences stated only where the 95% CI excludes 0.')
        if d == 'cdc-pregnancy-weight-gain':
            r[ix['notes']] += (
                ' CMB-017 (read 2026-10-22): one baby, BMI before pregnancy: under 18.5 28-40 lb, 18.5-24.9 25-35 lb, '
                '25.0-29.9 15-25 lb, 30.0-39.9 11-20 lb; "All recommendations are from the Institute of Medicine, with the '
                'exception of underweight women with twins."; page last reviewed December 13, 2023.')
        if d == 'cdc-adult-bmi-categories':
            r[ix['notes']] += (' CMB-017 (read 2026-10-22): "regardless of age, sex, or race" unchanged; page dated March 19, '
                               '2024.')
    assert linked == set(USED), set(USED) - linked
    return rows

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    hit = 0
    for r in rows[1:]:
        if r[ix['slug']] == SLUG:
            hit += 1
            r[ix['wedge']] = ('Result ranked among US women 20+ and aged 20-39, 40-59 and 60+ (NHANES 2021-2023 percentiles), an '
                              'optional waist check against the NHLBI, NICE and 2026 ADA thresholds (Asian lines when they '
                              'differ), and body fat measured in US women at the same BMI (DXA 2011-2018); built CMB-017')
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = ('Owns 33 keywords, 279,290/mo ("bmi calculator women" 201,000 primary; "bmi calculate women" '
                              '74,000 incl. "womens/female bmi calculator"; "calculate my bmi female" 880; "bmi chart women '
                              'calculator" 720; "bmi older woman calculator" 390; "bmi calculator female asian" 210). D-14 '
                              'rebuild CMB-017 (research/women-calc-build/). Chart queries stay with blog/bmi-chart-women; '
                              'age queries with age-bmi-calculator and blog/bmi-by-age.')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: the optional waist field and the three result boxes.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'Waist field and result boxes' not in d
d = d.replace(anchor, (
    '### Waist field and result boxes (CMB-017)\n'
    '- `/women-bmi-calculator/` adds an optional waist input to the shared calculator: a `.form-input.waist-in` beside the '
    'weight in the imperial row and a `.form-input.waist-cm` in the metric row, labeled "Waist (inches)" / "Waist (cm)", '
    'empty with the placeholder "Optional". `calculator.js` reads only the height and weight classes, so the field changes '
    'nothing there.\n'
    '- After Calculate the page script fills up to three flat boxes below the status line, each a `.rank-box` (hairline '
    'above, `.rank-title`, `.rank-text`, `.rank-source`; no card): the rank among US women (all and by age group), "US women '
    'with a BMI like yours" (body fat at that whole BMI, waist shares for that category) and, only when a waist is entered, '
    'the waist check. A box with nothing to say stays hidden.\n'
    '- The waist check compares what it prints. The waist is rounded to 0.1 in or 0.1 cm and the ratio is worked out from '
    'that printed waist, then cut (not rounded) to two decimals, so 0.50 always means a waist of at least half the height '
    '(0.4953 shows as 0.49). The BMI is the one the result card shows. The US-guidelines line compares in the unit the user '
    'entered and names only that unit (over 35 in, or over 88 cm). The ADA sentences quote the waist in cm against 88 cm, the '
    'unit the standard uses. When the answer for women of Asian background differs, the first ADA sentence says "for women '
    'of non-Asian background" and the Asian sentence follows. The source line says these are published thresholds applied '
    'to the numbers entered, not a diagnosis. Shares of US women follow the CMB-016 rule ("more than 99%", "under 1%").\n\n'
    + anchor))
open(dp, 'w', encoding='utf-8', newline='').write(d)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/body-fat-percentage-chart/': 'body-fat-percentage-chart'}"
assert c.count(old) == 1
c = c.replace(old, "             '/body-fat-percentage-chart/': 'body-fat-percentage-chart',\n"
                   "             '/women-bmi-calculator/': 'women-bmi-calculator'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)
print('patched: registry', len(USED), 'rows linked; page map; DESIGN.md; check_images PREFERRED')
