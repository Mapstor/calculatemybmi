#!/usr/bin/env python3
"""CMB-033 NUMBERS-1: the page edits of batch 1 that no generator owns. Every replacement must match exactly once, so a
page that changed since stops the run. usage: python3 research/cmb-033/apply.py
1. /blog/bmi-categories/ and /blog/underweight-bmi-risks/: the BMI scale drawn to scale (15 to 45, (BMI - 15) / 30 of the
   width) with the zone names in a legend, instead of zones sized to fit their labels (Normal 25 units wide, Overweight
   16.5) and evenly spaced ticks; the underweight marker at the page's own example, BMI 17.3, not 17 at 12%.
2. /blog/bmi-and-health-risks/ "BMI Risk Zones" and /blog/bmi-chart-explained/ "BMI Risk Spectrum": removed. Both drew
   evenly spaced zones with risk labels no source on the page backs (a marker 25 at the middle, a marker 22 inside the
   overweight colour); D-10, unsourced claims are cut, not hedged.
3. /age-bmi-calculator/: "In every age group the average adult BMI is in the overweight range (25 or higher)": the
   averages reach 30 or more for women 30 to 69 and men 40 to 59 (the page's own tables), which is obesity, not
   overweight; the sentence now says only what holds for every group, 25 or higher.
4. /404.html: "Browse all 15 guides" (the sitemap has 19) and "See all 8 calculators" (the hub lists 9).
5. assets/css/styles.css: .chart-range-track on the 15-45 scale, .chart-range-ticks and .chart-range-legend; the unused
   .chart-range-labels and .chart-range-zones rules go.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TICKS = ('<div class="chart-range-ticks" aria-hidden="true"><span style="left: 0%;">15</span><span style="left: 11.667%;">18.5</span>'
         '<span style="left: 33.333%;">25</span><span style="left: 50%;">30</span><span style="left: 66.667%;">35</span><span style="left: 83.333%;">40</span>'
         '<span style="left: 100%;">45</span></div>')
LEGEND = ('<ul class="chart-range-legend"><li class="underweight">Underweight: below 18.5</li><li class="normal">Healthy weight: 18.5 to 24.9</li>'
          '<li class="overweight">Overweight: 25.0 to 29.9</li><li class="obese">Class 1 obesity: 30.0 to 34.9</li><li class="obese">Class 2 obesity: 35.0 to 39.9</li>'
          '<li class="obese-severe">Class 3 obesity: 40.0 and above</li></ul>')

EDITS = {
    'blog/bmi-categories/index.html': [(
        '<div class="chart-range"> <div class="chart-range-track"></div> <div class="chart-range-labels"> <span>10</span> <span>18.5</span> <span>25</span> <span>30</span> <span>40+</span> </div> <div class="chart-range-zones"> <span style="flex: 18.5;">Underweight</span> <span style="flex: 25;">Normal</span> <span style="flex: 16.5;">Overweight</span> <span style="flex: 20;">Obese I-II</span> <span style="flex: 20;">Obese III</span> </div> </div>',
        f'<div class="chart-range"> <div class="chart-range-track"></div> {TICKS} {LEGEND} </div>')],
    'blog/underweight-bmi-risks/index.html': [(
        '<div class="chart-range-track"> <div class="chart-range-marker" style="left: 12%;">17</div> </div> <div class="chart-range-labels"> <span>10</span> <span>18.5</span> <span>25</span> <span>30</span> <span>35</span> <span>40+</span> </div> <div class="chart-range-zones" style="margin-top: 0.5rem;"> <span style="width: 18.5%; color: var(--underweight);">Underweight</span> <span style="width: 25%; color: var(--normal);">Normal</span> <span style="width: 16.5%; color: var(--overweight);">Overweight</span> <span style="width: 40%; color: var(--obese);">Obese</span> </div> </div>',
        f'<div class="chart-range-track"> <div class="chart-range-marker" style="left: 7.667%;">17.3</div> </div> {TICKS} {LEGEND} </div>')],
    'blog/bmi-and-health-risks/index.html': [(
        '<h2>BMI Risk Zones</h2> <p>The following visualization shows the health risk zones across the BMI spectrum. Use our BMI calculator to determine where you fall on this scale.</p> <div class="chart-range"> <div class="chart-range-track"> <div class="chart-range-marker" style="left: 50%;">25</div> </div> <div class="chart-range-labels"> <span>15</span> <span>18.5</span> <span>25</span> <span>30</span> <span>35</span> <span>40+</span> </div> <div class="chart-range-zones"> <span style="flex: 18.5;">Underweight Risk</span> <span style="flex: 25;">Healthy Zone</span> <span style="flex: 20;">Overweight</span> <span style="flex: 20;">Obese</span> <span style="flex: 16.5;">Severe</span> </div> </div> ',
        '')],
    'blog/bmi-chart-explained/index.html': [(
        '<h3>BMI Risk Spectrum</h3> <p>The following visual shows how health risk generally increases at both extremes of the BMI spectrum:</p> <div class="chart-range"> <div class="chart-range-track"></div> <div class="chart-range-marker" style="left: 50%;">22</div> </div> <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem; color: var(--gray-600);"> <span>Higher Risk</span> <span>Lower Risk</span> <span>Higher Risk</span> </div> <div style="display: flex; justify-content: space-between; margin-top: 0.25rem; font-size: 0.6875rem; color: var(--gray-500);"> <span>BMI &lt; 18.5</span> <span>BMI 18.5-24.9</span> <span>BMI 25.0 or higher</span> </div> ',
        '')],
    'age-bmi-calculator/index.html': [(
        'In every age group the average adult BMI is in the overweight range (25 or higher).',
        'In every age group the average adult BMI is 25 or higher.')],
    '404.html': [('>Browse all 15 guides</a>', '>Browse all 19 guides</a>'), ('>See all 8 calculators</a>', '>See all 9 calculators</a>')],
    'assets/css/styles.css': [
        ('.chart-range-track { height: 16px; background: linear-gradient(90deg, var(--underweight) 0%, var(--underweight) 18.5%, var(--normal) 18.5%, var(--normal) 43.5%, var(--overweight) 43.5%, var(--overweight) 60%, var(--obese) 60%, var(--obese) 80%, var(--obese-severe) 80%); border-radius: var(--radius-full); position: relative; }',
         '/* CMB-033: a BMI scale from 15 to 45 drawn to scale, a tick or marker at (BMI - 15) / 30 of the width: underweight to 18.5\n'
         '   (11.667%), healthy weight to 25 (33.333%), overweight to 30 (50%), class 1 and class 2 obesity to 40 (83.333%, one colour,\n'
         '   a tick at 35), class 3 after.\n'
         '   Zone names go in .chart-range-legend under the track, so no zone is sized to fit its label. */\n'
         '.chart-range-track { height: 16px; background: linear-gradient(90deg, var(--underweight) 0%, var(--underweight) 11.667%, var(--normal) 11.667%, var(--normal) 33.333%, var(--overweight) 33.333%, var(--overweight) 50%, var(--obese) 50%, var(--obese) 83.333%, var(--obese-severe) 83.333%); border-radius: var(--radius-full); position: relative; }'),
        ('.chart-range-labels { display: flex; justify-content: space-between; margin-top: 0.75rem; font-size: 0.6875rem; color: var(--gray-500); }\n'
         '.chart-range-zones { display: flex; margin-top: 0.25rem; }\n'
         '.chart-range-zones span { font-size: 0.6875rem; color: var(--gray-600); text-align: center; }',
         '.chart-range-ticks { position: relative; height: 1.25rem; margin-top: 0.5rem; font-size: 0.75rem; color: var(--gray-600); font-variant-numeric: tabular-nums; }\n'
         '.chart-range-ticks span { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }\n'
         '.chart-range-ticks span:first-child { transform: none; }\n'
         '.chart-range-ticks span:last-child { transform: translateX(-100%); }\n'
         '.chart-range-legend { display: flex; flex-wrap: wrap; gap: 0.25rem 1rem; margin: 0.5rem 0 0; padding: 0; list-style: none; font-size: 0.8125rem; color: var(--gray-700); }\n'
         '.chart-range-legend li { margin: 0; }\n'
         '.chart-range-legend li::before { content: ""; display: inline-block; width: 0.75rem; height: 0.75rem; margin-right: 0.375rem; border-radius: 2px; vertical-align: -1px; }\n'
         '.chart-range-legend .underweight::before { background: var(--underweight); }\n'
         '.chart-range-legend .normal::before { background: var(--normal); }\n'
         '.chart-range-legend .overweight::before { background: var(--overweight); }\n'
         '.chart-range-legend .obese::before { background: var(--obese); }\n'
         '.chart-range-legend .obese-severe::before { background: var(--obese-severe); }'),
    ],
}

for f, pairs in EDITS.items():
    p = REPO / f
    t = p.read_text(encoding='utf-8')
    for old, new in pairs:
        assert t.count(old) == 1, (f, old[:80], t.count(old))
        t = t.replace(old, new)
    p.write_text(t, encoding='utf-8')
    print('edited', f)
