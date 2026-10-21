#!/usr/bin/env python3
"""CMB-016 registry, page map, DESIGN.md and the image gate: /body-fat-percentage-chart/ sources (verified in chat
2026-10-04/14/21), the body fat rank tool and lookup-table rules, and the page's preferred image in check_images.py.
usage: patch_cmb016.py REPO_ROOT"""
import sys, os, csv, io, json

ROOT = sys.argv[1]
SLUG = 'body-fat-percentage-chart'
S = json.load(open(os.path.join(ROOT, 'research/body-fat-chart-build/bfpc_stats.json')))

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2011-2018-dxa', 'gallagher-2000-bf-ranges', 'cdc-about-bmi', 'cdc-adult-bmi-categories',
        'cdc-calculating-bmi', 'cdc-child-bmi-categories', 'body-fat-method-validation')   # the last: scales and calipers vs DXA
BA, AT, HB = S['by_age'], S['bmi']['at_lines'], S['bmi']['healthy_bmi_above']

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    linked = set()
    for r in rows[1:]:
        d = r[ix['domain']]
        if d in USED:
            ps = [x for x in r[ix['pages_served']].split(';') if x]
            if SLUG not in ps: ps.append(SLUG)
            r[ix['pages_served']] = ';'.join(ps); linked.add(d)
        if d == 'nhanes-2011-2018-dxa':
            r[ix['notes']] += (
                ' CMB-016 (2026-10-21): DXX_J documentation re-read: "Participants aged 8-59 years were eligible"; pregnancy, '
                'barium in the past 7 days and "Self-reported weight over 450 pounds or height over 6\'5" (DXA table limitation)" '
                'exclude a scan; "The percentage of participants with 100% valid data also decreases with increasing BMI"; the NHANES '
                'BCA option "adds 5% of lean mass to the fat mass"; Hologic Discovery A. /body-fat-percentage-chart/ rebuilt from '
                'research/body-fat-chart-build/bfpc_stats.py (same sample and weights as research/body-fat/compute_bf.py, asserted '
                f'equal): women 20-59 mean {BA["f"]["20-59"]["mean"]} (CI {BA["f"]["20-59"]["ci95"][0]}-{BA["f"]["20-59"]["ci95"][1]}), '
                f'men {BA["m"]["20-59"]["mean"]} ({BA["m"]["20-59"]["ci95"][0]}-{BA["m"]["20-59"]["ci95"][1]}); design df '
                f'{S["meta"]["df"]}; share above and below every whole percent 5-60; body fat at each BMI; adults within 0.5 of '
                f'BMI 25 average {AT["m"]["25"]["20-39"]["mean"]} (men 20-39) and {AT["f"]["25"]["20-39"]["mean"]} (women 20-39); '
                f'healthy-BMI adults at or above the provisional "high" cut-off: men {HB["m"]["above_healthy"]["pct"]}%, women '
                f'{HB["f"]["above_healthy"]["pct"]}%.')
        if d == 'gallagher-2000-bf-ranges':
            r[ix['notes']] += (
                ' CMB-016 (2026-10-21): the paper\'s own table is still out of reach (PMC reCAPTCHA, ScienceDirect robots.txt, '
                'Semantic Scholar error); PubMed abstract re-read: 1,626 adults with BMI <= 35; white, African American and Asian; '
                'Cambridge (UK), Columbia (US) and Jikei (Japan); 4C model at 2 labs and DXA at all 3; predictors 1/BMI, sex, age and '
                'ethnic group; provisional ranges from the BMI limits 18.5/25/30. /body-fat-percentage-chart/ shows the cut-offs as '
                'tabulated (J Public Health Afr 2016) and compares the BMI-25 cut-off with CDC DXA at the same BMI.')
    assert linked == set(USED), set(USED) - linked
    return rows

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    hit = 0
    for r in rows[1:]:
        if r[ix['slug']] == SLUG:
            hit += 1
            assert r[ix['data_source']] == 'nhanes-2011-2018-dxa'
            r[ix['wedge']] = ('US body fat measured on CDC DXA scans (NHANES 2011-2018) against the provisional ranges: share '
                              'above and below every whole percent, rank tool, body fat at each BMI, and where the ranges\' '
                              'BMI-25 edge falls on CDC\'s scanner (rebuilt CMB-016)')
            r[ix['status']] = 'built'
            r[ix['notes']] = ('Owns 501 keywords, 283,690/mo ("body fat index" 74,000, "body fat percentage women" 27,100, "men" '
                              '18,100, "body fat percentage chart" 14,800 primary, plus the "N% body fat man/woman" long tail). '
                              'D-14 rebuild CMB-016 (research/body-fat-chart-build/); healthy ranges from registry domain '
                              'gallagher-2000-bf-ranges. Owner\'s bodyfatpercentagecalc.com ranks for the same queries (GSC box '
                              'in the 2026-10-21 SERP paste).')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: the body fat rank tool and the narrow chart tables.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'Body fat rank tool' not in d
d = d.replace(anchor, (
    '### Body fat rank tool and lookup tables (CMB-016)\n'
    '- `/body-fat-percentage-chart/` ranks a body fat reading with the shared calculator parts, not a page-level style: '
    '`.calculator-card.bfr` › `.calc-panel` › `.unit-toggle` (Woman / Man, `aria-pressed`) › `.form-row` with two `.form-input`s '
    '(body fat %, age) › `.calculate-btn`. Results follow "Calculator results — answer first": a `.bmi-result-card` tinted by the '
    'provisional range, the share in a neutral `.bmi-value` (a share is not a BMI, so no category colour on the number), then '
    '`.er-section`s with `h3` headings (the tool sits inside a section that has its own `h2`), a `.cat-dot` on the range line, and '
    'a compact percentile `.data-table`.\n'
    '- Shares of US adults never print as 100% or 0%: 99.5% or more reads “more than 99%”, 0.5% or less “under 1%”. A reading '
    'equal to the row counts on neither side, as in the US rank rule.\n'
    '- Narrow chart tables (three columns) use `.weight-chart.weight-chart--fit` (no 600 px minimum, so they fit a phone); the '
    'provisional range shows as the cell tint and as a second line (`.cell-kg`), so colour never carries it alone.\n'
    '- Women and men as chart series: `#be185d` and `#4338ca` (dataviz validator, light mode: CVD ΔE 18.3, normal-vision ΔE '
    '29.3, both 3:1 or more on white); the middle half as the same hue at 16% opacity. The category colours stay for categories.\n\n'
    + anchor))
open(dp, 'w', encoding='utf-8', newline='').write(d)

# The image gate: the page joins PREFERRED.
cp = os.path.join(ROOT, 'scripts/check_images.py'); c = open(cp, encoding='utf-8', newline='').read()
old = "             '/blog/bmi-chart-women/': 'bmi-chart-women', '/bmi-chart/': 'bmi-chart'}"
assert c.count(old) == 1
c = c.replace(old, "             '/blog/bmi-chart-women/': 'bmi-chart-women', '/bmi-chart/': 'bmi-chart',\n"
                   "             '/body-fat-percentage-chart/': 'body-fat-percentage-chart'}")
open(cp, 'w', encoding='utf-8', newline='').write(c)
print('patched: registry', len(USED), 'rows linked; page map; DESIGN.md; check_images PREFERRED')
