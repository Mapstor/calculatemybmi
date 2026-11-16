#!/usr/bin/env python3
"""CMB-058: the registry and the page map for the waist-to-height ratio calculator.
  - research/data-sources.csv:
    - nice-ng246-ethnicity-thresholds: the chapter re-read in Claude in Chrome on 2026-11-16, with the recommendation
      numbers the calculator cites. 1.9.5 [2022]: encourage adults with a BMI below 35 to measure their own ratio and to
      seek advice and further clinical assessments (such as a cardiometabolic risk factor assessment) from a healthcare
      professional if the measurement indicates an increased health risk. Box 1: waist midway between the bottom of the
      ribs and the top of the hips (just above the belly button), breathe out naturally; same units; 38 in / 67 in or
      96.5 cm / 170 cm = 0.57. 1.9.14 [2022]: healthy central adiposity 0.4 to 0.49 (no increased health risks),
      increased 0.5 to 0.59 (increased health risks), high 0.6 or more (further increased health risks), for people
      with a BMI under 35 of both sexes and all ethnicities, including adults with high muscle mass. 1.9.15: keep the
      waist to less than half the height. 1.10.10 [2022, amended 2026]: the same classes for children and young people
      aged 5 years and over, both sexes and all ethnicities; 1.10.11: the same half-height advice.
    - cdc-adult-bmi-categories: the page joins pages_served (the calculator's line under 0.4 cites CDC's underweight
      line).
  - research/page-map.csv: the page's notes record the calculator.
usage: python3 research/cmb-058/registry.py   (idempotent)"""
import csv
import io
from pathlib import Path

R = Path(__file__).resolve().parents[2] / 'research'
SLUG = 'blog/waist-to-height-ratio'
NICE_NOTE = (' CMB-058 (read in Claude in Chrome, 2026-11-16; numbering as the chapter now has it): 1.9.5 [2022] encourage '
             'adults with a BMI below 35 to measure their own waist-to-height ratio and to "seek advice and further '
             'clinical assessments (such as a cardiometabolic risk factor assessment) from a healthcare professional if '
             'the measurement indicates an increased health risk"; Box 1: waist midway between the bottom of the ribs and '
             'the top of the hips ("just above the belly button"), breathe out naturally, same units, 38 in / 67 in or '
             '96.5 cm / 170 cm = 0.57; 1.9.14 [2022] healthy central adiposity 0.4 to 0.49 "indicating no increased health '
             'risks", increased 0.5 to 0.59 "indicating increased health risks", high 0.6 or more "indicating further '
             'increased health risks", for people with a BMI under 35 of both sexes and all ethnicities, including adults '
             'with high muscle mass; 1.9.15 keep the waist to less than half the height (a ratio under 0.5); 1.10.10 '
             '[2022, amended 2026] the same three classes for children and young people aged 5 years and over, both sexes '
             'and all ethnicities; 1.10.11 the same half-height advice. The waist-to-height ratio calculator on '
             'blog/waist-to-height-ratio uses these classes and cites 1.9.14 and 1.10.10.')


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
    r = by['nice-ng246-ethnicity-thresholds']
    if 'CMB-058' not in r['notes']:
        r['notes'] = r['notes'].rstrip() + NICE_NOTE
        n += 1
    c = by['cdc-adult-bmi-categories']
    served = [s.strip() for s in c['pages_served'].split(';') if s.strip()]
    if SLUG not in served:
        c['pages_served'] = ';'.join(served + [SLUG])
        n += 1
    return n


def page_map(rows):
    r = next(x for x in rows if x['slug'] == SLUG)
    if 'CMB-058' in r['notes']:
        return 0
    r['notes'] = (r['notes'] + ' CMB-058: waist-to-height ratio calculator built under the intro (NICE NG246 classes); '
                  'title and H1 name it.').strip()
    return 1


if __name__ == '__main__':
    print('data-sources.csv:', rewrite(R / 'data-sources.csv', registry), 'changes')
    print('page-map.csv:', rewrite(R / 'page-map.csv', page_map), 'row changed')
