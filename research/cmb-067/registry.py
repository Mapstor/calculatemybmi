#!/usr/bin/env python3
"""CMB-067: registry, page map and Stage 1 manual entries for the /blog/bmi-categories/ D-14 rebuild.
  - research/data-sources.csv: the page joins pages_served on the three rows it now cites for the first time
    (cdc-calculating-bmi, cdc-ndpp-eligibility, nhanes-2021-2023-exam-files) and leaves the eight rows only its old text
    cited (wing-2011-look-ahead, odphp-physical-activity-guidelines, medlineplus-unintentional-weight-loss,
    flegal-2013-jama-mortality, provencher-2018-nfl-combine, cdc-losing-weight, nimh-eating-disorders, nci-obesity-cancer);
    nhanes-2021-2023-exam-files gets a note on cat_stats.py.
  - research/page-map.csv: a CMB-067 note (data_source stays cdc-adult-bmi-categories).
  - research/stage1-audit/manual.json: the page's entries go; it is now scored by its own page test
    (research/bmi-categories-build/cat_test_playwright.py), like the other D-14 pages.
usage: python3 research/cmb-067/registry.py   (idempotent)"""
import csv
import io
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG, PAGE = 'blog/bmi-categories', '/blog/bmi-categories/'
ADD = ('cdc-calculating-bmi', 'cdc-ndpp-eligibility', 'nhanes-2021-2023-exam-files')
DROP = ('wing-2011-look-ahead', 'odphp-physical-activity-guidelines', 'medlineplus-unintentional-weight-loss',
        'flegal-2013-jama-mortality', 'provencher-2018-nfl-combine', 'cdc-losing-weight', 'nimh-eating-disorders',
        'nci-obesity-cancer')
NOTE = (' CMB-067 (2026-11-17): research/bmi-categories-build/cat_stats.py -> cat_stats.json, the six categories by sex and '
        'age group with 95% CIs (Taylor linearisation, 15 design df), adults with a BMI from 25 up to the pre-1998 survey lines '
        '(17.5%; men 21.6%, women 13.7%) and non-Hispanic Asian adults (RIDRETH3 = 6, 330) at BMI 23, 25, 27.5 and 30 '
        '(65.5, 45.2, 27.6, 13.4%); reproduces the NCHS crude rates and the homepage six shares; /blog/bmi-categories/ prints it.')


def rewrite(path, change):
    text = path.read_text(encoding='utf-8')
    rd = csv.DictReader(io.StringIO(text))
    rows = list(rd)
    n = change(rows)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=rd.fieldnames, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def registry(rows):
    n = 0
    by = {x['domain']: x for x in rows}
    for d in ADD + DROP:
        served = [s.strip() for s in by[d]['pages_served'].split(';') if s.strip()]
        new = served + [SLUG] if d in ADD and SLUG not in served else [s for s in served if s != SLUG] if d in DROP else served
        if new != served:
            by[d]['pages_served'] = ';'.join(new)
            n += 1
    x = by['nhanes-2021-2023-exam-files']
    if 'CMB-067' not in x['notes']:
        x['notes'] = (x['notes'] + NOTE).strip()
        n += 1
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    before = dict(r)
    assert r['data_source'] == 'cdc-adult-bmi-categories'
    if 'CMB-067' not in r['notes']:
        r['notes'] = (r['notes'] + ' CMB-067: D-14 rebuild (research/bmi-categories-build); wedge from CDC NHANES 2021-2023 '
                      '(our calculation): categories by age, the 1998 line move, the Asian action points; scored by its page '
                      'test.').strip()
    return int(before != r)


def manual():
    p = R / 'stage1-audit/manual.json'
    m = json.loads(p.read_text(encoding='utf-8'))
    n0 = len(m['entries'])
    m['entries'] = [e for e in m['entries'] if e['page'] != PAGE]
    p.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return n0 - len(m['entries'])


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
    print('manual.json:', manual(), 'entries removed')
