#!/usr/bin/env python3
"""CMB-008: every weight-by-height table on the site lists whole-unit weights that fall inside the stated
category at that exact height, in pounds AND kilograms (each unit worked out on its own, not converted),
and the paired height label carries one decimal. usage: fix_tables.py REPO_ROOT

Rule (chart_rules.py, same as calculator.js weightBounds): BMI rounded half-up to 0.1 decides the category."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_rules import bounds, CM_PER_IN

root = sys.argv[1]
ND = '&ndash;'

def rd(p):
    return open(os.path.join(root, p), encoding='utf-8', newline='').read()

def wr(p, s):
    open(os.path.join(root, p), 'w', encoding='utf-8', newline='').write(s)

def nth_table(s, i):
    ms = list(re.finditer(r'(?s)<table\b.*?</table>', s))
    return ms[i].start(), ms[i].end()

def ft_in_label(inches_float):
    ft = int(inches_float // 12); rest = inches_float - ft * 12
    return f"{ft}&#39;{rest:.1f}&quot;"

# ---------- 1. the three chart pages: rebuild every row of the 6-category tables ----------
CLASSES = ['cell-under', 'cell-healthy', 'cell-over', 'cell-ob1', 'cell-ob2', 'cell-ob3']

def chart_row_inch(row_id, ft, inch):
    h_in = ft * 12 + inch; cm = h_in * CM_PER_IN
    cells = []
    for band, cls in enumerate(CLASSES):
        lb = bounds('lb', h_in, band); kg = bounds('kg', cm, band)
        if band == 0:
            txt = f'&le; {lb[1]} lb <span class="cell-kg">({kg[1]} kg)</span>'
        elif band == 5:
            txt = f'&ge; {lb[0]} lb <span class="cell-kg">({kg[0]} kg)</span>'
        else:
            txt = f'{lb[0]}{ND}{lb[1]} lb <span class="cell-kg">({kg[0]}{ND}{kg[1]} kg)</span>'
        cells.append(f'<td class="{cls}">{txt}</td>')
    return (f'<tr id="{row_id}"><th scope="row" class="row-height">{ft}&#39;{inch}&quot; '
            f'<span class="cell-cm">({cm:.1f} cm)</span></th>' + ''.join(cells) + '</tr>')

def chart_row_cm(row_id, cm):
    h_in = cm / CM_PER_IN
    cells = []
    for band, cls in enumerate(CLASSES):
        kg = bounds('kg', cm, band); lb = bounds('lb', h_in, band)
        if band == 0:
            txt = f'&le; {kg[1]} kg <span class="cell-kg">({lb[1]} lb)</span>'
        elif band == 5:
            txt = f'&ge; {kg[0]} kg <span class="cell-kg">({lb[0]} lb)</span>'
        else:
            txt = f'{kg[0]}{ND}{kg[1]} kg <span class="cell-kg">({lb[0]}{ND}{lb[1]} lb)</span>'
        cells.append(f'<td class="{cls}">{txt}</td>')
    return (f'<tr id="{row_id}"><th scope="row" class="row-height">{cm} cm '
            f'<span class="cell-cm">({ft_in_label(h_in)})</span></th>' + ''.join(cells) + '</tr>')

ROW_IN = re.compile(r'<tr id="(h-(\d)-(\d{1,2}))"><th scope="row" class="row-height">\d&#39;\d{1,2}&quot; <span class="cell-cm">\(\d+(?:\.\d)? cm\)</span></th>(?:<td class="cell-[a-z0-9]+">.*?</td>){6}</tr>')
ROW_CM = re.compile(r'<tr id="(h-(\d{3})cm)"><th scope="row" class="row-height">\d{3} cm <span class="cell-cm">\(\d&#39;\d{1,2}(?:\.\d)?&quot;\)</span></th>(?:<td class="cell-[a-z0-9]+">.*?</td>){6}</tr>')

report = {}
for page in ('bmi-chart/index.html', 'blog/bmi-chart-men/index.html', 'blog/bmi-chart-women/index.html'):
    s = rd(page)
    s, n_in = ROW_IN.subn(lambda m: chart_row_inch(m.group(1), int(m.group(2)), int(m.group(3))), s)
    s, n_cm = ROW_CM.subn(lambda m: chart_row_cm(m.group(1), int(m.group(2))), s)
    report[page] = (n_in, n_cm)
    wr(page, s)
assert report == {'bmi-chart/index.html': (21, 12), 'blog/bmi-chart-men/index.html': (17, 0),
                  'blog/bmi-chart-women/index.html': (15, 0)}, report

# chart pages: say plainly that the two units are each worked out on their own
for page in ('blog/bmi-chart-men/index.html', 'blog/bmi-chart-women/index.html'):
    s = rd(page)
    a = ('the band shown is the lowest to the highest whole pound that produces a BMI in that category at the given height.</li>')
    b = ('the band shown is the lowest to the highest whole pound that produces a BMI in that category at the given height. '
         'The kilograms in parentheses follow the same rule in whole kilograms at that exact height (the cm label has one decimal); '
         'they are not converted from the pounds.</li>')
    assert s.count(a) == 1, (page, s.count(a)); wr(page, s.replace(a, b))
s = rd('bmi-chart/index.html')
a = '<li><strong>Rounding rule:</strong> BMI to one decimal place, half-up; each weight takes the category of its rounded BMI.</li>'
b = ('<li><strong>Rounding rule:</strong> BMI to one decimal place, half-up; each weight takes the category of its rounded BMI. '
     'Pounds and kilograms are each worked out in whole units at the exact height, so the paired height label has one decimal.</li>')
assert s.count(a) == 1; wr('bmi-chart/index.html', s.replace(a, b))

# ---------- 2. other pages: patch numbers inside known cells ----------
def label_cm(cell_html, inches):
    cm = inches * CM_PER_IN
    new, n = re.subn(r'\((\d+) cm\)', f'({cm:.1f} cm)', cell_html, count=1)
    assert n == 1, cell_html
    return new

def rows_of(s, ti):
    a, b = nth_table(s, ti)
    return a, b, s[a:b]

def height_in(label_html):
    m = re.search(r"(\d)(?:&#39;|'|&prime;|′)(\d{1,2})(?:&quot;|\"|&Prime;|″)", label_html)
    return int(m.group(1)) * 12 + int(m.group(2))

def cells_of(tr):
    return list(re.finditer(r'(?s)(<t[dh]\b[^>]*>)(.*?)(</t[dh]>)', tr))

def rebuild(tr, newcells):
    out, pos = [], 0
    for m, new in zip(cells_of(tr), newcells):
        out.append(tr[pos:m.start(2)]); out.append(new); pos = m.end(2)
    out.append(tr[pos:])
    return ''.join(out)

def patch_table(page, ti, fn, expect_rows):
    s = rd(page); a, b, tb = rows_of(s, ti); n = 0
    def one(m):
        nonlocal n
        tr = m.group(0); cs = cells_of(tr)
        if not cs or not re.search(r"\d(?:&#39;|'|&prime;|′)\d", cs[0].group(2)) or 'kg' not in tr: return tr
        n += 1
        h = height_in(cs[0].group(2))
        return rebuild(tr, fn(h, [c.group(2) for c in cs]))
    tb2 = re.sub(r'(?s)<tr\b.*?</tr>', one, tb)
    assert n == expect_rows, (page, n)
    wr(page, s[:a] + tb2 + s[b:])
    report[page] = n

def sub_nums(cell, nums):
    """replace the numbers of a cell, in order"""
    it = iter(nums)
    new = re.sub(r'\d+(?:\.\d+)?', lambda m: str(next(it)), cell)
    return new

# homepage "Healthy weight by height: examples": healthy / overweight / obesity class 1 ranges
def home_row(h, cells):
    cm = h * CM_PER_IN; out = [label_cm(cells[0], h)]
    for band, cell in zip((1, 2, 3), cells[1:4]):
        lb = bounds('lb', h, band); kg = bounds('kg', cm, band)
        out.append(sub_nums(cell, [lb[0], lb[1], kg[0], kg[1]]))
    return out
patch_table('index.html', 0, home_row, 4)

# healthy-bmi-range "What does the healthy range look like": min, max, span (lb)
def hbr_row(h, cells):
    cm = h * CM_PER_IN; lb = bounds('lb', h, 1); kg = bounds('kg', cm, 1)
    return [label_cm(cells[0], h), sub_nums(cells[1], [lb[0], kg[0]]), sub_nums(cells[2], [lb[1], kg[1]]),
            sub_nums(cells[3], [lb[1] - lb[0]])]
patch_table('blog/healthy-bmi-range/index.html', 1, hbr_row, 9)

# bmi-categories "Weight ranges for normal BMI by height": low normal (min), mid (BMI 21.7, nearest whole unit), high normal (max)
def cat_row(h, cells):
    cm = h * CM_PER_IN; lb = bounds('lb', h, 1); kg = bounds('kg', cm, 1)
    mid_lb = round(21.7 * h * h / 703.0); mid_kg = round(21.7 * (cm / 100.0) ** 2)
    return [label_cm(cells[0], h), sub_nums(cells[1], [lb[0], kg[0]]), sub_nums(cells[2], [mid_lb, mid_kg]),
            sub_nums(cells[3], [lb[1], kg[1]])]
patch_table('blog/bmi-categories/index.html', 1, cat_row, 8)

# underweight-bmi-risks "Example weights by height": "< min healthy" and "normal range start" (min healthy); 3rd column untouched
def uw_row(h, cells):
    cm = h * CM_PER_IN; lb = bounds('lb', h, 1); kg = bounds('kg', cm, 1)
    return [label_cm(cells[0], h), sub_nums(cells[1], [lb[0], kg[0]]), sub_nums(cells[2], [lb[0], kg[0]])] + cells[3:]
patch_table('blog/underweight-bmi-risks/index.html', 1, uw_row, 5)

print('tables fixed:', report)
