#!/usr/bin/env python3
"""CMB-057, part 2: Gallagher 2000 checked against the paper's own tables (§0 waiting item, §5 [P2], the two S fails).
The AJCN full text (https://ajcn.nutrition.org/article/S0002-9165(23)06760-6/fulltext) was read in Claude in Chrome on
2026-11-16. Table 3 gives predicted body fat by ethnic group; Table 4 combines African Americans and whites; Table 5 is
Asians. The cut-offs on the site are Table 4's, and all 18 cells match (women 21/33/39, 23/34/40, 24/36/42; men 8/20/25,
11/22/28, 13/25/30 at BMI 18.5/25/30 for ages 20-39, 40-59, 60-79). No number changes. What changes:
  - pages cite Table 4 of the paper itself instead of "as tabulated in J Public Health Afr 2016, Table 1", and the PMC
    link to that secondary goes (chart page: two source lines, one paragraph, the sources list and the JSON-LD citation;
    body fat calculator: source line and sources list; how to measure body fat: sources list);
  - "the original study gives different values for each of its three ethnic groups" was half right: the ranges shown are
    the study's own Table 4, for African American and white adults; Table 5 gives separate values for Asian adults,
    higher at ages 20 to 59 (all 12 cells) but not at 60 to 79, so the source lines now say exactly that;
  - research/data-sources.csv: the gallagher-2000-bf-ranges row cites Table 4, records the read, Table 5's cells and why
    the IJMS figures differ (Table 3's white column); blog/body-fat-vs-bmi joins pages_served (it cites the paper);
  - research/page-scores-known.csv: the two open S items go.
dateModified and lastmod follow on the three pages (links and visible text change).
usage: python3 research/cmb-057/gallagher.py [--check]   Run after apply.py."""
import csv
import datetime
import hashlib
import io
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
CH, BF, HM, SM = ('body-fat-percentage-chart/index.html', 'body-fat-calculator/index.html',
                  'blog/how-to-measure-body-fat/index.html', 'sitemap.xml')
BASE = {CH: 'b97fa23cdc80b4fb6b220f866e719270500f9cc428ebb3eb42246c5147eecf65',
        BF: 'ac3932da3b72aceaeb64168d400d783f46b490d065000ae14558448a0d3b4140',
        HM: '991f5566d421ce02295ec64419b4831aa2fea7a7ec6ac5a4c1f38ccf103fb894',
        SM: '7ea46230a1ceb9cb95f8bd65071b8ab85a3dd984801f6860d87742d27befa0f9'}
EXT = 'target="_blank" rel="noopener"'
PUB = f'<a href="https://pubmed.ncbi.nlm.nih.gov/10966886/" {EXT}>Gallagher et al., 2000</a>'
SEC = f'<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC5349253/table/table001" {EXT}>J Public Health Afr 2016, Table 1</a>'
POP = ('Table 4, for African American and white adults; the study’s Table 5 gives separate values for Asian adults, '
       'higher at ages 20 to 59')

EDITS = {
    CH: [
        (f'<p class="source-note">Ranges: {PUB}, as tabulated in {SEC}; the original study gives different values for '
         'each of its three ethnic groups. US median:',
         f'<p class="source-note">Ranges: {PUB}, {POP}. US median:'),
        ('20% body fat for men and 33% for women aged 20 to 39, as tabulated in J Public Health Afr 2016. In CDC’s scans',
         '20% body fat for men and 33% for women aged 20 to 39 (Gallagher et al., 2000, Table 4). In CDC’s scans'),
        (f'Provisional: where the “high” range starts ({PUB}, as tabulated in {SEC}).</p>',
         f'Provisional: where the “high” range starts ({PUB}, Table 4).</p>'),
        ('(Am J Clin Nutr 2000;72:694–701): the provisional ranges.</li><li><a href="https://pmc.ncbi.nlm.nih.gov/articles/'
         f'PMC5349253/table/table001" {EXT}>Interpreting the body fat percentage result, Table 1</a> (J Public Health Afr '
         '2016;7:515): the provisional ranges as tabulated.</li>',
         '(Am J Clin Nutr 2000;72:694–701): the provisional ranges, Table 4 for African American and white adults.</li>'),
        ('"https://pubmed.ncbi.nlm.nih.gov/10966886/", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5349253/table/table001"]',
         '"https://pubmed.ncbi.nlm.nih.gov/10966886/"]'),
        ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
    ],
    BF: [
        (f'<p class="source-note">Ranges as tabulated in {SEC}; the original study gives values for each of its three '
         'ethnic groups.</p>',
         f'<p class="source-note">Ranges: {PUB}, {POP}.</p>'),
        (f'Am J Clin Nutr 2000;72:694–701, as tabulated in {SEC}.</li>', 'Am J Clin Nutr 2000;72:694–701, Table 4.</li>'),
        ('"dateModified": "2026-11-14"', f'"dateModified": "{TODAY}"'),
    ],
    HM: [
        (f'Am J Clin Nutr 2000;72:694–701, as tabulated in {SEC}.</li>', 'Am J Clin Nutr 2000;72:694–701, Table 4.</li>'),
        ('"dateModified": "2026-10-29"', f'"dateModified": "{TODAY}"'),
    ],
    SM: [(f'<url><loc>https://calculatemybmi.net/{slug}/</loc><lastmod>{old}</lastmod>',
          f'<url><loc>https://calculatemybmi.net/{slug}/</loc><lastmod>{TODAY}</lastmod>')
         for slug, old in (('body-fat-percentage-chart', '2026-11-13'), ('body-fat-calculator', '2026-11-14'),
                           ('blog/how-to-measure-body-fat', '2026-10-29'))],
}

ROW = 'gallagher-2000-bf-ranges'
REG = {
    'source': 'Gallagher D et al. Healthy percentage body fat ranges: an approach for developing guidelines based on body '
              'mass index. Am J Clin Nutr 2000;72(3):694-701, Table 4 (African Americans and whites)',
    'endpoint': 'https://ajcn.nutrition.org/article/S0002-9165(23)06760-6/fulltext',
    'attribution': 'Provisional ranges: Gallagher et al., Am J Clin Nutr 2000, Table 4',
    'verified_date': '2026-11-16',
    'next_check': '2027-11-16',
    'coverage': 'Table 4 (African Americans and whites), body fat at BMI 18.5/25/30: women 21/33/39 (20-39 y), 23/34/40 '
                '(40-59), 24/36/42 (60-79); men 8/20/25, 11/22/28, 13/25/30. Table 5 (Asians): women 25/35/40, '
                '25/35/41, 25/36/41; men 13/23/28, 13/24/29, 14/24/29',
    'sample_note': 'Tables 3 to 5, their captions and the abstract read in Claude in Chrome from the AJCN full text '
                   '(2026-11-16); all 18 Table 4 cells match the J Public Health Afr 2016 Table 1 tabulation the pages '
                   'used before',
}
NOTE = (' CMB-057 (2026-11-16): checked against the paper\'s own tables (AJCN full text). Table 3 is by ethnic group, '
        'Table 4 combines African Americans and whites (Equation 5), Table 5 is Asians (Equations 6 and 7); all from '
        'equations centred on ages 30, 50 and 70. The abstract calls them provisional healthy ranges from the BMI limits '
        '18.5, 25 and 30. The pages\' cut-offs are Table 4\'s, all 18 cells match. The IJMS figures (men 20-39 '
        '8.0-20.9%, women 60+ 25.0-37.9%) are Table 3\'s white column (men 20-39 8/21, women 60-79 25/38), not Table 4. '
        'Asian cut-offs are higher at 20-59 in all 12 cells but not at 60-79 (women: 36 vs 36 at BMI 25, 41 vs 42 at 30; '
        'men: 24 vs 25, 29 vs 30). Pages cite Table 4 directly; the J Public Health Afr link is gone.')
SERVED_ADD = 'blog/body-fat-vs-bmi'


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:100]}'
    return src.replace(old, new)


def rewrite_csv(path, change):
    rows = list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8'))))
    fields = list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8'))).fieldnames)
    n = change(rows)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    if not CHECK:
        path.write_text(buf.getvalue(), encoding='utf-8', newline='')
    return n


def registry(rows):
    r = next(x for x in rows if x['domain'] == ROW)
    before = dict(r)
    r.update(REG)
    if 'CMB-057' not in r['notes']:
        r['notes'] = r['notes'].rstrip() + NOTE
    served = [s.strip() for s in r['pages_served'].split(';') if s.strip()]
    if SERVED_ADD not in served:
        r['pages_served'] = ';'.join(served + [SERVED_ADD])
    return int(before != r)


def known(rows):
    n = len(rows)
    rows[:] = [x for x in rows if 'Gallagher 2000' not in x['item']]
    return n - len(rows)


def main():
    for rel, edits in EDITS.items():
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        for old, new in edits:
            src = one(src, old, new, rel)
        if rel != SM:
            for gone in ('PMC5349253', 'J Public Health Afr', 'tabulated', 'three ethnic'):
                assert gone not in src, f'{rel}: "{gone}" is left'
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: {len(edits)} edits{" (check only)" if CHECK else ""}')
    print('data-sources.csv:', rewrite_csv(REPO / 'research/data-sources.csv', registry), 'row changed')
    print('page-scores-known.csv:', rewrite_csv(REPO / 'research/page-scores-known.csv', known), 'rows removed')


if __name__ == '__main__':
    main()
