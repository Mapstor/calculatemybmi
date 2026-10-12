#!/usr/bin/env python3
"""Audit every weight cell of the BMI chart tables. usage: audit_charts.py REPO_ROOT [-v]
For each row height and category column, the listed primary and bracketed ranges must equal the
whole-unit bounds inside the band (chart_rules.bounds). Reports wrong cells per unit."""
import sys, os, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_rules import bounds, CM_PER_IN

PAGES = ['bmi-chart/index.html', 'blog/bmi-chart-men/index.html', 'blog/bmi-chart-women/index.html']
NUM = r'(\d+(?:\.\d+)?)'

def txt(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x))).strip()

def parse_cell(s):
    """-> (unit, lo, hi, bunit, blo, bhi) ; open ends are None"""
    s = s.replace('–', '-').replace('—', '-')
    m = re.match(rf'^(?:(≤|≥)\s*)?{NUM}(?:\s*-\s*{NUM})?\s*(lb|kg)\s*\((?:(≤|≥)\s*)?{NUM}(?:\s*-\s*{NUM})?\s*(lb|kg)\)$', s)
    if not m: return None
    op, a, b, u, op2, c, d, u2 = m.groups()
    a, b, c, d = [float(x) if x else None for x in (a, b, c, d)]
    if op == '≤': lo, hi = None, a
    elif op == '≥': lo, hi = a, None
    else: lo, hi = a, b
    if op == '≤': blo, bhi = None, c
    elif op == '≥': blo, bhi = c, None
    else: blo, bhi = c, d
    return u, lo, hi, u2, blo, bhi

def row_height(label):
    m = re.match(r"^(\d+)'(\d+)\"\s*\((\d+(?:\.\d+)?) cm\)$", label)
    if m: return 'in', int(m.group(1)) * 12 + int(m.group(2)), float(m.group(3))
    m = re.match(r"^(\d+(?:\.\d+)?) cm \((\d+)'(\d+(?:\.\d+)?)\"\)$", label)
    if m: return 'cm', float(m.group(1)), int(m.group(2)) * 12 + float(m.group(3))
    return None, None, None

def audit(root, verbose=False):
    total = {'lb': [0, 0], 'kg': [0, 0]}; out = []
    for page in PAGES:
        t = open(os.path.join(root, page), encoding='utf-8').read()
        for ti, tb in enumerate(re.findall(r'(?s)<table\b.*?</table>', t)):
            rows = re.findall(r'(?s)<tr\b.*?</tr>', tb)
            stats = {'lb': [0, 0], 'kg': [0, 0]}; labels_bad = 0; n_rows = 0
            for r in rows:
                cells = [txt(x) for x in re.findall(r'(?s)<t[dh]\b[^>]*>(.*?)</t[dh]>', r)]
                if len(cells) != 7: continue
                kind, h, other = row_height(cells[0])
                if kind is None: continue
                n_rows += 1
                inches = h if kind == 'in' else h / CM_PER_IN
                cm = h * CM_PER_IN if kind == 'in' else h
                # label precision: kg bounds for an inch height need cm to 1 decimal (and vice versa)
                if kind == 'in' and abs(other - round(cm, 1)) > 1e-9: labels_bad += 1
                if kind == 'cm' and abs(other - round(inches, 1)) > 1e-9: labels_bad += 1
                for band, cell in enumerate(cells[1:]):
                    p = parse_cell(cell)
                    if not p: out.append(f'{page} t{ti} {cells[0]} band {band}: unparsed "{cell}"'); continue
                    u, lo, hi, u2, blo, bhi = p
                    for unit, a, b in ((u, lo, hi), (u2, blo, bhi)):
                        want = bounds(unit, inches if unit == 'lb' else cm, band)
                        got = (None if a is None else int(a), None if b is None else int(b))
                        stats[unit][1] += 1
                        if got != want:
                            stats[unit][0] += 1
                            if verbose: out.append(f'{page} t{ti} {cells[0]} band {band} {unit}: listed {got} correct {want}')
            if n_rows:
                out.append(f'{page} table {ti}: {n_rows} rows | lb wrong {stats["lb"][0]}/{stats["lb"][1]} | kg wrong {stats["kg"][0]}/{stats["kg"][1]} | height labels not 1-decimal {labels_bad}/{n_rows}')
                for u in total: total[u][0] += stats[u][0]; total[u][1] += stats[u][1]
    out.append(f'TOTAL lb wrong {total["lb"][0]}/{total["lb"][1]} | kg wrong {total["kg"][0]}/{total["kg"][1]}')
    return out, total

if __name__ == '__main__':
    lines, total = audit(sys.argv[1], '-v' in sys.argv)
    print('\n'.join(lines))
    sys.exit(1 if total['lb'][0] or total['kg'][0] else 0)
