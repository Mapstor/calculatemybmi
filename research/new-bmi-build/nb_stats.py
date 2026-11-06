#!/usr/bin/env python3
"""New BMI numbers for /new-bmi-calculator/ (CMB-023). usage: python3 research/new-bmi-build/nb_stats.py
Writes nb_stats.json next to this file with the arithmetic of calculateNewBMI() in assets/js/calculator.js, step for step:
  traditional = lb ÷ (in × in) × 703            (US units, CDC's formula; the calculator's metric input uses kg ÷ m²)
  kg = lb ÷ 2.20462;  m = in × 2.54 ÷ 100       (= in × 0.0254; both forms are checked to round the same)
  new = 1.3 × kg ÷ m^2.5                         (Trefethen's formula)
  round1(x) = Math.round(x × 10 + 1e-9) ÷ 10     (halves up, as calculator.js; every printed BMI is rounded once)
  difference = round1(new) − round1(traditional) (the two rounded values subtracted, as the calculator prints it)
  categories = getBMICategory() of each value    (on the rounded value)
Outputs:
  a. side by side: 5′0″, 5′4″, 5′8″, 6′0″, 6′4″ × 120, 150, 180, 210 lb;
  b. by height: 5′0″, 5′4″, 5′6.5″, 5′8″, 5′10″, 6′0″, 6′4″: New BMI ÷ traditional BMI = 1.3 ÷ √m as a percent change
     (the same at every weight), and what a traditional BMI of 25.0 becomes;
  c. worked examples: 5′2″ and 6′2″ at 150 lb, in US units (703 and 5734) and in metric (kg, m);
  d. the curve: New BMI minus traditional BMI at 70 kg (154 lb), every 0.01 m from 1.40 to 2.00 m, plus 5′0″ and 6′0″.
Stops when a printed value sits within 1e-6 of a rounding edge (float noise would decide it), when an anchor chat read
off the live calculator on 2026-11-05 differs, or when two routes to the same printed number disagree."""
import json, math, os
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FT, IN = '′', '″'          # prime and double prime: heights are written 5′4″
MINUS = '−'


def round1(x):
    """calculator.js round1(): Math.round(x * 10 + 1e-9) / 10; Math.round sends halves toward +infinity."""
    return math.floor(x * 10 + 1e-9 + 0.5) / 10


def near_edge(x, places=1):
    v = x * 10 ** places
    return abs((v - math.floor(v)) - 0.5) < 1e-6


def f1(x, exact=None):
    """A BMI as the calculator prints it: round1(x).toFixed(1).
    exact: the value as a fraction when it is rational (lb × 703 ÷ in²). An exact half then rounds up by the calculator's
    rule (5′0″ and 180 lb is 35.15, printed 35.2; the 1e-9 in round1 is larger than the float error), and the printed
    value must equal the exact value rounded half up. Without it, the value must not sit within 1e-6 of a half."""
    if exact is not None:
        want = (Decimal(exact.numerator) / Decimal(exact.denominator)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        assert f'{round1(x):.1f}' == str(want), (x, exact, want)
        return str(want)
    assert not near_edge(x), f'{x!r} sits on a rounding edge'
    return f'{round1(x):.1f}'


def signed(d):
    """calculator.js signed(): '+' or '−' and Math.abs(d).toFixed(1)."""
    return ('+' if d > 0 else MINUS if d < 0 else '') + f'{abs(d):.1f}'


def half_up(x, places):
    q = Decimal(1).scaleb(-places)
    return Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)


def category(bmi):
    """getBMICategory() in calculator.js, on the rounded value."""
    b = round1(bmi)
    if b < 16: return 'Severe thinness'
    if b < 17: return 'Moderate thinness'
    if b < 18.5: return 'Underweight'
    if b < 25: return 'Healthy weight'
    if b < 30: return 'Overweight'
    if b < 35: return 'Class 1 obesity'
    if b < 40: return 'Class 2 obesity'
    return 'Class 3 obesity'


def height_label(inches):
    ft, rest = divmod(Decimal(str(inches)), 12)
    rest = rest.normalize() if rest != rest.to_integral() else rest.to_integral()
    return f'{int(ft)}{FT}{rest}{IN}'


def cm_label(inches):          # exact decimal, one place, halves up: 5′2″ = 157.5 cm
    return f'{(Decimal(str(inches)) * Decimal("2.54")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)} cm'


def m_label(inches):           # two places: 5′6.5″ = 1.69 m
    return f'{(Decimal(str(inches)) * Decimal("0.0254")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)} m'


def kg_label(lb):              # the calculator's factor, one place: 150 lb = 68.0 kg
    return f'{half_up(lb / 2.20462, 1)} kg'


def both(lb, inches):
    """calculateNewBMI() for a US-unit entry: (traditional, new) unrounded, plus the m = in × 0.0254 route."""
    trad = (lb / (inches * inches)) * 703
    kg = lb / 2.20462
    m = (inches * 2.54) / 100
    new = 1.3 * kg / m ** 2.5
    new_alt = 1.3 * kg / (inches * 0.0254) ** 2.5
    assert f1(new) == f1(new_alt), (lb, inches, new, new_alt)
    return trad, new, kg, m


def row(lb, inches):
    trad, new, kg, m = both(lb, inches)
    exact = Fraction(lb * 703, inches * inches)
    d = round1(new) - round1(trad)
    # the same difference in exact decimals: the printed values subtracted
    dd = Decimal(f1(new)) - Decimal(f1(trad, exact))
    assert signed(d) == (('+' if dd > 0 else MINUS if dd < 0 else '') + f'{abs(dd):.1f}'), (lb, inches, d, dd)
    tc, nc = category(trad), category(new)
    return {'inches': inches, 'height': height_label(inches), 'cm': cm_label(inches), 'lb': lb, 'kg': kg_label(lb),
            'traditional': f1(trad, exact), 'new': f1(new), 'difference': signed(d),
            'traditional_category': tc, 'new_category': nc, 'category_changes': tc != nc,
            'traditional_exact': round(trad, 6), 'new_exact': round(new, 6)}


# a. side by side
GRID_H = [60, 64, 68, 72, 76]
GRID_W = [120, 150, 180, 210]
side = [row(lb, h) for h in GRID_H for lb in GRID_W]

# b. by height: New ÷ traditional = 1.3 ÷ √m, whatever the weight
BY_H = [60, 64, 66.5, 68, 70, 72, 76]
by_height = []
for h in BY_H:
    m = (h * 2.54) / 100
    ratio = 1.3 / math.sqrt(m)
    pct = (ratio - 1) * 100
    assert not near_edge(pct), (h, pct)
    p = half_up(pct, 1)
    pct_s = ('+' if p > 0 else MINUS if p < 0 else '') + f'{abs(p):.1f}%'
    by_height.append({'inches': h, 'height': height_label(h), 'm': m_label(h), 'cm': cm_label(h),
                      'ratio': round(ratio, 6), 'percent': pct_s, 'traditional_25_becomes': f1(25.0 * ratio)})
# the ratio does not depend on weight: check it at three weights against the calculator's own arithmetic
for h in BY_H:
    rs = []
    for lb in (100, 160, 250):
        kg, m = lb / 2.20462, (h * 2.54) / 100
        rs.append((1.3 * kg / m ** 2.5) / (kg / (m * m)))
    assert max(rs) - min(rs) < 1e-12 and abs(rs[0] - 1.3 / math.sqrt((h * 2.54) / 100)) < 1e-12, (h, rs)

# c. worked examples
examples = []
for h in (62, 74):
    r = row(150, h)
    trad, new, kg, m = both(150, h)
    us_new = 5734 * 150 / h ** 2.5                       # Trefethen's US-unit form
    metric_trad = kg / (m * m)                           # the calculator's metric route for the same person
    kg2, m4 = f'{half_up(kg, 2)}', f'{half_up(m, 4)}'
    shown_new = 1.3 * float(kg2) / float(m4) ** 2.5      # the equation as printed, with the printed kg and m
    shown_trad = float(kg2) / float(m4) ** 2
    assert f1(us_new) == r['new'] == f1(shown_new) and f1(metric_trad) == r['traditional'] == f1(shown_trad), (h, us_new, metric_trad)
    r.update({'kg_2dp': kg2, 'm_4dp': m4, 'in_squared': h * h, 'us_new': f1(us_new), 'metric_traditional': f1(metric_trad)})
    examples.append(r)

# d. the curve at 70 kg
KG = 70
curve = []
for k in range(61):
    m = (140 + k) / 100
    trad, new = KG / (m * m), 1.3 * KG / m ** 2.5
    curve.append([m, round(new - trad, 6)])
marks = []
for h in (60, 72):
    m = (h * 2.54) / 100
    trad, new = KG / (m * m), 1.3 * KG / m ** 2.5
    d = round1(new) - round1(trad)
    assert not near_edge(new - trad) and signed(d) == (('+' if new > trad else MINUS) + f'{abs(half_up(new - trad, 1)):.1f}'), (h, new, trad)
    marks.append({'inches': h, 'height': height_label(h), 'm': round(m, 6), 'diff_exact': round(new - trad, 6), 'difference': signed(d)})
cross_m = 1.69                                            # 1.3 ÷ √1.69 = 1 exactly: the curve crosses zero here
assert abs(1.3 / math.sqrt(cross_m) - 1) < 1e-15
lo_ends = {'m_lo': 1.40, 'height_lo': height_label(float(half_up(1.40 / 0.0254, 1))), 'diff_lo': curve[0][1],
           'm_hi': 2.00, 'height_hi': height_label(float(half_up(2.00 / 0.0254, 1))), 'diff_hi': curve[-1][1]}

# Anchors chat read off the live calculator on 2026-11-05 (typed in here as literals).
A = {(62, 150): ('27.4', '28.4', '+1.0', 'Overweight', 'Overweight'),
     (74, 150): ('19.3', '18.3', MINUS + '1.0', 'Healthy weight', 'Underweight'),
     (60, 150): ('29.3', '30.8', '+1.5', 'Overweight', 'Class 1 obesity'),
     (76, 210): ('25.6', '23.9', MINUS + '1.7', 'Overweight', 'Healthy weight'),
     (76, 150): ('18.3', '17.1', MINUS + '1.2', 'Underweight', 'Underweight')}
for (h, lb), want in A.items():
    r = row(lb, h)
    got = (r['traditional'], r['new'], r['difference'], r['traditional_category'], r['new_category'])
    assert got == want, ((h, lb), got, want)
BH = {b['inches']: b for b in by_height}
assert (BH[60]['percent'], BH[60]['traditional_25_becomes']) == ('+5.3%', '26.3'), BH[60]
assert (BH[72]['percent'], BH[72]['traditional_25_becomes']) == (MINUS + '3.9%', '24.0'), BH[72]

out = {
    'about': 'New BMI (Trefethen) against traditional BMI with the arithmetic of calculateNewBMI() in assets/js/calculator.js; '
             'our calculation for /new-bmi-calculator/ (CMB-023). Built by research/new-bmi-build/nb_stats.py.',
    'formulas': {'traditional_us': 'lb / in^2 * 703', 'traditional_metric': 'kg / m^2',
                 'new_metric': '1.3 * kg / m^2.5', 'new_us': '5734 * lb / in^2.5',
                 'kg_per_lb': '1 / 2.20462', 'm_per_in': '2.54 / 100', 'rounding': 'Math.round(x * 10 + 1e-9) / 10',
                 'difference': 'round1(new) - round1(traditional)'},
    'side_by_side': side,
    'by_height': by_height,
    'examples': examples,
    'curve': {'kg': KG, 'lb': f'{half_up(KG * 2.20462, 0)}', 'points': curve, 'marks': marks, 'cross_m': cross_m,
              'cross_height': height_label(66.5), **lo_ends},
    'anchors_checked': [f'{height_label(h)} {lb} lb: ' + ', '.join(v) for (h, lb), v in A.items()],
}
path = os.path.join(HERE, 'nb_stats.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
changed = [f"{r['height']} {r['lb']} lb: {r['traditional_category']} to {r['new_category']}" for r in side if r['category_changes']]
print(f'{path}: {len(side)} side-by-side rows ({len(changed)} change category: {"; ".join(changed)}), '
      f'{len(by_height)} heights, {len(examples)} examples, {len(curve)} curve points; anchors ok')
