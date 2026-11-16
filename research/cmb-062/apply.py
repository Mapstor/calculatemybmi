#!/usr/bin/env python3
"""CMB-062 CLAIMS-13: claims pass batch 13 (DEVLOG §5 P1) on /blog/bmi-tracking-guide/ (7 probe hits). CMB-038 sourced the
studies; what was left were the lines round them. Each now says what a registry row says, or went (D-10, D-06):
  - intro: "effective monitoring requires more than stepping on a scale", "This comprehensive guide covers" and "these
    evidence-based strategies" become one promise line;
  - "Why Track Your BMI?": the five-item list (accountability, early detection, "reinforces positive behaviors", seasons
    and stress, "valuable data for healthcare providers") had no source; Madigan et al. (2015) stays; the NHLBI landing
    page (not in the registry) goes;
  - weighing: "Timing significantly affects your scale reading", "most stable ... as you have fasted overnight and
    eliminated most waste" and "Bathroom tiles or hardwood floors work best" become plain instructions;
  - fluctuations: "One of the biggest mistakes people make" and "what causes daily fluctuations" become Orsama et al.'s own
    conclusion (weekend-weekday variation is normal, not weight gain);
  - measuring: "Poor technique can result in significant errors" and "Measure in the morning when you are tallest (spinal
    compression occurs throughout the day)" out;
  - tools: "Modern technology offers numerous options", "how to choose and use tracking tools effectively", the named apps
    (Apple Health, Google Fit, Samsung Health, Happy Scale, Libra: product claims no row backs, and they change) and "Low-tech
    but effective" become generic kinds of tool;
  - beyond BMI: "useful starting point", "well-documented" and "A comprehensive tracking approach" become CDC's line;
    "consistency of method matters more than absolute accuracy" becomes Burns et al. (2019)'s method differences;
    "particularly important if you are strength training" out;
  - milestones: the h2 "Setting Effective Milestone Goals" and its four-step strip (5%, 10%, 15%, "Target BMI": targets of
    our own, D-06) become "Milestones", the 5 and 10% steps Wing et al. measured; "to determine your target weight" out.
dateModified and lastmod follow.
usage: python3 research/cmb-062/apply.py [--check]   Run order from main: registry.py, apply.py, audit_manual.py."""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODAY = os.environ.get('CMB_TODAY') or datetime.date.today().isoformat()
CHECK = '--check' in sys.argv
PG, SM = 'blog/bmi-tracking-guide/index.html', 'sitemap.xml'
BASE = {PG: '95f736971245eebd902ef0f3c4dac7f275349c127258ec3a541696015b8e7cb5',
        SM: 'facb20fca5d68636fa3bb43c78dbe3ed964ac8c1fe349bdb33e5735a30fabcce'}
EXT = 'target="_blank" rel="noopener"'
U = {
    'cdc_about': 'https://www.cdc.gov/bmi/about/index.html',
    'orsama': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5644907/',
    'burns': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214029',
    'wing': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3120182/',
}
LI = '<li style="margin-bottom: 0.5rem;">'


def a(key, text):
    return f'<a href="{U[key]}" {EXT}>{text}</a>'


EDITS = [
    ('<p class="intro-text">Tracking your BMI over time provides valuable insights into your weight management journey. '
     'However, effective monitoring requires more than stepping on a scale occasionally. This comprehensive guide covers '
     'optimal tracking frequency, measurement techniques, understanding natural weight fluctuations, and knowing when changes '
     'in your BMI warrant attention. Whether you are working toward a healthier weight or maintaining your current BMI, these '
     'evidence-based strategies will help you track progress accurately and avoid common pitfalls.</p>',
     '<p class="intro-text">Tracking your BMI means weighing yourself the same way, on a schedule, and reading the trend '
     'rather than single days. Below: how often and when to weigh, what moves from day to day, and what to track beside '
     'BMI.</p>'),
    ('Here is what tracking gives you:</p> <ul style="margin: 1rem 0; padding-left: 1.5rem;"> ' + LI +
     '<strong>Accountability:</strong> Regular tracking keeps weight management top of mind and helps you stay committed to '
     'your goals</li> ' + LI + '<strong>Early detection:</strong> Catching gradual weight gain early allows for corrective '
     'action before it becomes a larger problem</li> ' + LI + '<strong>Progress validation:</strong> Seeing your BMI move '
     'toward a <a href="/blog/healthy-bmi-range/">healthy range</a> reinforces positive behaviors</li> ' + LI +
     '<strong>Pattern recognition:</strong> Long-term tracking reveals how your weight responds to seasons, stress, holidays, '
     'and lifestyle changes</li> ' + LI + '<strong>Medical documentation:</strong> A weight history provides valuable data '
     'for healthcare providers</li> </ul> <p>For the clinical side of weight, see the <a href="https://www.nhlbi.nih.gov/'
     'health/overweight-and-obesity" target="_blank" rel="noopener">NHLBI overweight and obesity overview</a>.</p>',
     'A record also shows how your own weight moves through the week.</p>'),
    ('<p>Timing significantly affects your scale reading. For consistent, comparable measurements, follow these '
     'guidelines:</p>',
     '<p>For readings you can compare from one week to the next:</p>'),
    ('<p>After using the bathroom, before eating or drinking anything. This is when your weight is most stable and '
     'comparable day-to-day, as you have fasted overnight and eliminated most waste.</p>',
     '<p>After using the bathroom, before eating or drinking anything. The same routine each time keeps readings '
     'comparable.</p>'),
    ('<p>Different scales can give different readings. Always use the same scale, placed on a hard, flat surface (not carpet). '
     'Bathroom tiles or hardwood floors work best.</p>',
     '<p>Use the same scale each time, on the same hard, flat floor.</p>'),
    ('<p>One of the biggest mistakes people make when tracking BMI is reacting to normal, temporary weight changes. '
     'Understanding what causes daily fluctuations helps you interpret your data correctly and avoid unnecessary stress.</p>',
     '<p>Single days move up and down. In Orsama and colleagues’ study, weight rose at weekends and fell on weekdays, and the '
     'authors call that variation normal rather than a sign of weight gain '
     f'({a("orsama", "Orsama et al., 2014")}).</p>'),
    ('<p>Accurate BMI calculation requires accurate height and weight measurements. Poor technique can result in significant '
     'errors that make tracking unreliable.</p>',
     '<p>BMI is only as accurate as the height and weight behind it, so measure both the same way each time.</p>'),
    (' ' + LI + 'Measure in the morning when you are tallest (spinal compression occurs throughout the day)</li>', ''),
    ('<p>Modern technology offers numerous options for tracking your BMI and weight over time. Here is how to choose and use '
     'tracking tools effectively:</p>',
     '<p>Any of these keeps a record:</p>'),
    (LI + '<strong>Smart scales:</strong> Connect to apps via Bluetooth/WiFi, automatically log weight, calculate BMI, and '
     'some measure body composition</li> ' + LI + '<strong>Health apps:</strong> Apple Health, Google Fit, Samsung Health '
     'integrate with scales and allow manual entry</li> ' + LI + '<strong>Dedicated weight tracking apps:</strong> Apps like '
     'Happy Scale (iOS) and Libra (Android) specialize in trend analysis and smoothing daily fluctuations</li>',
     LI + '<strong>Smart scales:</strong> log each weighing to an app, work out BMI, and some estimate body fat</li> ' + LI +
     '<strong>Health apps:</strong> on your phone, with readings from a smart scale or entered by hand</li> ' + LI +
     '<strong>Weight-tracking apps:</strong> some smooth daily readings into a trend line</li>'),
    (LI + '<strong>Paper log:</strong> Low-tech but effective; keeps tracking simple and private</li>',
     LI + '<strong>Paper log:</strong> low-tech, simple and private</li>'),
    ('<p>While BMI is a useful starting point, it has well-documented <a href="/blog/bmi-limitations/">limitations</a>. A '
     'comprehensive tracking approach includes additional metrics that provide a more complete picture of your health and '
     'body composition.</p>',
     f'<p>BMI does not directly measure body fat ({a("cdc_about", "CDC")}); our <a href="/blog/bmi-limitations/">BMI '
     'limitations</a> guide covers the rest. These add what it leaves out:</p>'),
    ('<p>While more difficult to measure accurately at home, <a href="/blog/body-fat-vs-bmi/">body fat percentage</a> provides '
     'direct information about body composition that BMI cannot offer. Methods range from inexpensive (skinfold calipers, '
     'bioelectrical impedance scales) to clinical-grade (DEXA scans, hydrostatic weighing). For tracking purposes, consistency '
     'of method matters more than absolute accuracy.</p>',
     '<p><a href="/blog/body-fat-vs-bmi/">Body fat percentage</a> measures what BMI can’t, but methods differ: in a study of 437 '
     'college students, seven-site skinfolds read 1.4 points below DXA on average and a hand-held impedance device was 4.9 '
     f'points off ({a("burns", "Burns et al., 2019")}). Switching methods changes the number as well as your body, so use the '
     'same method each time.</p>'),
    ('<p>Tracking your <a href="/lean-body-mass/">lean body mass</a> alongside BMI helps distinguish between muscle and fat '
     'changes, particularly important if you are strength training while managing weight.</p>',
     '<p>Tracking your <a href="/lean-body-mass/">lean body mass</a> alongside BMI shows whether a change in weight is fat or '
     'lean mass.</p>'),
    ('<p>Use our <a href="/ideal-weight/">ideal weight calculator</a> to determine your target weight, then break the journey '
     'into these percentage-based milestones.</p>',
     '<p>Our <a href="/ideal-weight/">ideal weight calculator</a> shows the healthy weight range for your height.</p>'),
    ('"dateModified": "2026-11-13"', f'"dateModified": "{TODAY}"'),
]

BLOCKS = [
    ('<h2>Setting Effective Milestone Goals</h2>', '<h3>Why modest milestones matter</h3>',
     '<h2>Milestones</h2> <p>A long-term change can be split into steps. Wing and colleagues measured two, 5% and 10% of body '
     f'weight ({a("wing", "Wing et al., 2011")}); the table below shows what each does to BMI.</p> '),
]


def one(src, old, new, what):
    n = src.count(old)
    assert n == 1, f'{what}: marker found {n} times: {old[:90]}'
    return src.replace(old, new)


def block(src, start, end, new):
    assert src.count(start) == 1, f'block start: {start[:70]}'
    i = src.find(start)
    j = src.find(end, i)
    assert j > i, f'block end: {end[:70]}'
    return src[:i] + new + src[j:]


def page(src):
    for old, new in EDITS:
        src = one(src, old, new, PG)
    for start, end, new in BLOCKS:
        src = block(src, start, end, new)
    for gone in ('effective monitoring', 'tools effectively', 'but effective', 'Effective Milestone', 'evidence-based',
                 'This comprehensive guide', 'A comprehensive tracking', 'Google Fit', 'Happy Scale', 'Target BMI',
                 'biggest mistakes', 'tallest', 'nhlbi.nih.gov/health/overweight', 'target weight', 'Timing significantly'):
        assert gone not in src.split('<main', 1)[1].split('</main>')[0], f'"{gone}" is left in main'
    return src


def main():
    for rel in (PG, SM):
        path = REPO / rel
        src = path.read_text(encoding='utf-8')
        got = hashlib.sha256(src.encode('utf-8')).hexdigest()
        assert got == BASE[rel], f'{rel}: not the file this batch was written against ({got[:12]})'
        if rel == PG:
            src = page(src)
        else:
            src = one(src, '<url><loc>https://calculatemybmi.net/blog/bmi-tracking-guide/</loc><lastmod>2026-11-13</lastmod>',
                      f'<url><loc>https://calculatemybmi.net/blog/bmi-tracking-guide/</loc><lastmod>{TODAY}</lastmod>', SM)
        if not CHECK:
            path.write_text(src, encoding='utf-8', newline='')
        print(f'{rel}: done{" (check only)" if CHECK else ""}')


if __name__ == '__main__':
    main()
