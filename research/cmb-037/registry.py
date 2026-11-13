#!/usr/bin/env python3
"""CMB-037 SOURCES-2: registry rows for batch 4a (research/data-sources.csv): three new rows for the numbers on
/privacy/ (GA4 data retention, GDPR Article 8, the FTC's COPPA Rule), read on 2026-11-13 through the text a web search
returned for each page, and the batch's pages added to the rows that now serve them.
usage: python3 research/cmb-037/registry.py   (stops if a row it adds exists or a row it updates is missing)
"""
import csv
import io
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CSV = REPO / 'research' / 'data-sources.csv'
DAY = '2026-11-13'
NEXT = '2027-05-13'

NEW = [
    dict(domain='google-analytics-data-retention', source='Google Analytics Help: Data retention',
         publisher='Google', url='https://support.google.com/analytics/answer/7667196',
         endpoint='https://support.google.com/analytics/answer/7667196', access='page', license='cited, not reproduced',
         tier='A', cadence='irregular', granularity='product setting', format='HTML', key_required='no',
         attribution='Google Analytics Help, Data retention', verified_date=DAY, next_check=NEXT,
         coverage='Google Analytics properties (standard and 360)',
         sample_note='"For Google Analytics properties, you can set the retention period of user-level data to: 2 months, '
                     '14 months"; other event data: 2 or 14 months (26, 38 and 50 months for 360 only) (page text via a '
                     'web search, 2026-11-13)',
         status='verified', pages_served='privacy', notes=''),
    dict(domain='gdpr-article-8', source="Regulation (EU) 2016/679 (GDPR), Article 8: conditions applicable to child's "
                                         'consent in relation to information society services',
         publisher='EUR-Lex (Publications Office of the European Union)',
         url='https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32016R0679',
         endpoint='https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32016R0679', access='page',
         license='EU legislation, reuse authorised with source', tier='A', cadence='static', granularity='EU/EEA',
         format='HTML', key_required='no', attribution='Regulation (EU) 2016/679, Article 8', verified_date=DAY,
         next_check=NEXT, coverage='EU and EEA',
         sample_note='Art. 8(1): processing of a child\'s data on consent "shall be lawful where the child is at least 16 '
                     'years old"; "Member States may provide by law for a lower age for those purposes provided that such '
                     'lower age is not below 13 years" (EUR-Lex text via a web search, 2026-11-13)',
         status='verified', pages_served='privacy', notes=''),
    dict(domain='ftc-coppa-rule', source="FTC: Children's Online Privacy Protection Rule (COPPA)",
         publisher='US Federal Trade Commission',
         url='https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa',
         endpoint='https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa',
         access='page', license='Public domain (US federal work)', tier='A', cadence='irregular', granularity='US',
         format='HTML', key_required='no', attribution='FTC, COPPA Rule', verified_date=DAY, next_check=NEXT,
         coverage='US websites and online services',
         sample_note='"COPPA imposes certain requirements on operators of websites or online services directed to children '
                     'under 13 years of age, and on operators of other websites or online services that have actual '
                     'knowledge that they are collecting personal information online from a child under 13 years of '
                     'age" (page text via a web search, 2026-11-13)',
         status='verified', pages_served='privacy', notes=''),
]

PAGES = [
    ('nice-ng246-ethnicity-thresholds', 'blog/body-fat-vs-bmi;blog'),
    ('eknoyan-2008-quetelet', 'blog;blog/what-is-bmi;about'),
    ('nhanes-adult-weight-trends', 'blog/what-is-bmi'),
    ('pai-paloucek-2000-ibw', 'about'),
    ('davidson-2015-hamwi-dbw', 'about'),
    ('cdc-child-bmi-categories', 'about'),
    ('cdc-extended-bmi-data', 'about'),
    ('trefethen-new-bmi', 'about'),
]


def main():
    raw = CSV.read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    have = {r['domain']: r for r in rows}
    for n in NEW:
        assert n['domain'] not in have, n['domain']
    for d, add in PAGES:
        r = have[d]
        cur = [x for x in r['pages_served'].split(';') if x]
        r['pages_served'] = ';'.join(cur + [x for x in add.split(';') if x not in cur])
    rows += [{k: n.get(k, '') for k in fields} for n in NEW]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    CSV.write_text(buf.getvalue(), encoding='utf-8', newline='')
    print(f'{len(NEW)} rows added, {len(PAGES)} rows serve more pages; {len(rows)} rows')


if __name__ == '__main__':
    main()
