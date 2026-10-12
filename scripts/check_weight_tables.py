#!/usr/bin/env python3
"""Weight-by-height table check (CMB-008). usage: python3 scripts/check_weight_tables.py FILE...
In any table whose header names a BMI category or "BMI", a row that starts with a height must list, for every
range cell, the whole-unit weights that fall inside that category at that exact height, in pounds AND
kilograms, each worked out on its own (not converted). Rule: BMI rounded half-up to 0.1 (calculator.js round1)
decides the category. Range cells: "A–B lb (C–D kg)", "≤ A lb (C kg)", "≥ A lb (C kg)" and the kg-first forms.
A row that pairs an inch height with kg (or a cm height with lb) must label the other unit with one decimal.
Imported by scripts/check_structure.py; exits 1 when a file has problems."""
import re, sys, html, math

BANDS = [(None, 18.4), (18.5, 24.9), (25.0, 29.9), (30.0, 34.9), (35.0, 39.9), (40.0, None)]
CM_PER_IN = 2.54

def round1(x):
    return math.floor(x * 10 + 0.5 + 1e-9) / 10

def category(bmi):
    r = round1(bmi)
    for i, (lo, hi) in enumerate(BANDS):
        if (lo is None or r >= lo) and (hi is None or r <= hi):
            return i

def bmi_of(unit, w, h_in, cm):
    return 703.0 * w / (h_in * h_in) if unit == 'lb' else w / ((cm / 100.0) ** 2)

def bounds(unit, h_in, cm, band):
    f = lambda w: category(bmi_of(unit, w, h_in, cm))
    scale = (h_in * h_in / 703.0) if unit == 'lb' else (cm / 100.0) ** 2
    lo, hi = BANDS[band]; wmin = wmax = None
    if lo is not None:
        wmin = math.ceil((lo - 0.05) * scale - 1e-9)
        while f(wmin) < band: wmin += 1
        while f(wmin - 1) >= band: wmin -= 1
    if hi is not None:
        wmax = math.ceil((hi + 0.05) * scale - 1e-9) - 1
        while f(wmax) > band: wmax -= 1
        while f(wmax + 1) <= band: wmax += 1
    return wmin, wmax

def _txt(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()

HEIGHT_IN = re.compile(r"^(\d)\s*['′](\d{1,2})\s*[\"″]")
HEIGHT_CM = re.compile(r"^(\d{3}(?:\.\d)?)\s*cm\b")
N = r'(\d+(?:\.\d+)?)'
RANGE = re.compile(rf'^(≤|≥|<)?\s*{N}(?:\s*[–-]\s*{N})?\s*(lb|lbs|kg)\s*\(\s*(≤|≥|<)?\s*{N}(?:\s*[–-]\s*{N})?\s*(lb|lbs|kg)\s*\)$')
CATWORDS = re.compile(r'\bBMI\b|Underweight|Healthy|Overweight|Obesity|Normal', re.I)

def table_problems(src):
    out = []
    for tb in re.findall(r'(?s)<table\b.*?</table>', src):
        heads = ' '.join(_txt(h) for h in re.findall(r'(?s)<th\b[^>]*>(.*?)</th>', tb))
        if not CATWORDS.search(heads):
            continue
        for tr in re.findall(r'(?s)<tr\b.*?</tr>', tb):
            cells = [_txt(c) for c in re.findall(r'(?s)<t[dh]\b[^>]*>(.*?)</t[dh]>', tr)]
            if len(cells) < 2:
                continue
            mi, mc = HEIGHT_IN.match(cells[0]), HEIGHT_CM.match(cells[0])
            if mi:
                h_in = int(mi.group(1)) * 12 + int(mi.group(2)); cm = h_in * CM_PER_IN
            elif mc:
                cm = float(mc.group(1)); h_in = cm / CM_PER_IN
            else:
                continue
            row = cells[0][:24]
            has_pair = False
            for c in cells[1:]:
                m = RANGE.match(c.replace('lbs', 'lb'))
                if not m:
                    continue
                has_pair = True
                op1, a, b, u1, op2, c1, d1, u2 = m.groups()
                u1 = 'lb' if u1.startswith('lb') else 'kg'; u2 = 'lb' if u2.startswith('lb') else 'kg'
                for unit, op, lo, hi in ((u1, op1, a, b), (u2, op2 or op1, c1, d1)):
                    lo_v = float(lo); hi_v = float(hi) if hi else None
                    band = category(bmi_of(unit, lo_v, h_in, cm))
                    bmin, bmax = bounds(unit, h_in, cm, band)
                    if op == '≤':
                        got, want = lo_v, bmax
                    elif op in ('≥', '<'):
                        got, want = lo_v, bmin      # "< X" names the first weight of the next band up
                    elif hi_v is not None:
                        if category(bmi_of(unit, hi_v, h_in, cm)) != band:
                            out.append(f'{row}: "{c}" {unit} range spans two categories'); continue
                        got, want = (lo_v, hi_v), (bmin, bmax)
                    else:
                        continue                    # a single value makes no band claim
                    if got != want:
                        out.append(f'{row}: "{c}" {unit} lists {got}, the whole-{unit} bound is {want}')
            if has_pair:
                if mi and 'kg' in ' '.join(cells[1:]):
                    lab = re.search(r'\((\d+(?:\.\d+)?)\s*cm\)', cells[0])
                    if lab and abs(float(lab.group(1)) - round(cm, 1)) > 1e-9:
                        out.append(f'{row}: kg for an inch height needs the cm label to one decimal ({cm:.1f})')
                if mc and re.search(r'\blb\b', ' '.join(cells[1:])):
                    lab = re.search(r"\((\d)['′](\d{1,2}(?:\.\d)?)[\"″]\)", cells[0])
                    if lab and abs(float(lab.group(2)) - round(h_in - int(lab.group(1)) * 12, 1)) > 1e-9:
                        out.append(f'{row}: lb for a cm height needs the inch label to one decimal')
    return out

if __name__ == '__main__':
    bad = 0
    for f in sys.argv[1:]:
        probs = table_problems(open(f, encoding='utf-8').read())
        if probs:
            bad += 1; print(f'{f}: {len(probs)} weight-table problems')
            for p in probs[:12]: print('   -', p)
    sys.exit(1 if bad else 0)
