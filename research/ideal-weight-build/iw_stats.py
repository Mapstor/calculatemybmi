#!/usr/bin/env python3
"""Ideal body weight numbers for /ideal-weight/ (CMB-028). usage: python3 research/ideal-weight-build/iw_stats.py
Writes iw_stats.json next to this file with the arithmetic of calculateIdealWeight() and displayIdealWeightResults()
in assets/js/calculator.js, step for step (the same floating-point operations in the same order):
  no formula weight under 60 inches; over = inches - 60
  Devine    kg = 45.5 + 2.3 x over (women)    50 + 2.3 x over (men)       lb = kg x 2.20462   (kgToLbs)
  Robinson  kg = 49 + 1.7 x over              52 + 1.9 x over             lb = kg x 2.20462
  Miller    kg = 53.1 + 1.36 x over           56.2 + 1.41 x over          lb = kg x 2.20462
  Hamwi     lb = (100 + 5 x over) x frame     (106 + 6 x over) x frame    kg = lb / 2.20462   (lbsToKg)
            frame = 0.9 small, 1 medium, 1.1 large; it changes Hamwi only
  printed   whole lb = Math.round(lb + 1e-9); kg = Math.round(kg x 10 + 1e-9) / 10, shown to 0.1 (halves up)
  span      the lowest to the highest of the four as printed, in each unit
  BMI       round1(calculateBMI(lb, inches)): US units lb / (in x in) x 703, metric (lb / 2.20462) / m^2
  healthy   weightBounds(inches, 18.5, 24.9): whole lb (703 rule) and whole kg (kg/m^2), each unit on its own
Every printed value is worked out a second time in exact fractions and rounded half up; the two must agree, so float
noise decides nothing (toFixed(1) alone prints Miller's 77.35 kg for a 6'3" man as 77.3: the double is 77.3499...).
Outputs:
  a. by height, medium frame: women 5'0" to 6'0", men 5'0" to 6'6", every inch: the four formulas in lb and kg,
     the span, the lowest and highest BMI at the four, the healthy range in lb and kg;
  b. Hamwi at a small and a large frame for the same heights;
  c. worked examples: woman 5'6" medium; man 5'10" medium and large;
  d. where they agree: the narrowest and widest span per sex, and the BMI at the four across each table;
  e. the figure: the four lines per sex (unrounded lb) and the healthy band (whole lb) per inch;
  f. the formulas table: each formula's constants as published and the conversion into the other unit.
Stops when a step 1 anchor or a "where they agree" value chat worked out (2026-11-07) differs."""
import json, math, os
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
FT, IN = '′', '″'         # heights are written 5'6" with primes: 5′6″
LB_PER_KG = 2.20462
NAMES = ('hamwi', 'devine', 'robinson', 'miller')
FRAMES = {'small': 0.9, 'medium': 1, 'large': 1.1}

# The constants as published: Devine, Robinson, Miller in kg (Pai and Paloucek 2000, Table 1); Hamwi in lb
# (Davidson 2015, Table 2; Peterson 2016). Each: (base, per inch over 60 inches, unit).
CONST = {
    'female': {'hamwi': ('100', '5', 'lb'), 'devine': ('45.5', '2.3', 'kg'),
               'robinson': ('49', '1.7', 'kg'), 'miller': ('53.1', '1.36', 'kg')},
    'male':   {'hamwi': ('106', '6', 'lb'), 'devine': ('50', '2.3', 'kg'),
               'robinson': ('52', '1.9', 'kg'), 'miller': ('56.2', '1.41', 'kg')},
}


# ---- calculator.js, operation for operation ------------------------------------------------------------------
def js_round(x):
    """Math.round: the nearest integer, halves toward +infinity (exact for these magnitudes)."""
    n = math.floor(x)
    return n + 1 if x - n >= 0.5 else n


def formulas_js(inches, sex, frame='medium'):
    """calculateIdealWeight(): {name: (lb, kg)} unrounded, or None under 60 inches."""
    if inches < 60:
        return None
    over = inches - 60
    male = sex == 'male'
    out = {}
    for name, kg in (('devine', 50 + 2.3 * over if male else 45.5 + 2.3 * over),
                     ('robinson', 52 + 1.9 * over if male else 49 + 1.7 * over),
                     ('miller', 56.2 + 1.41 * over if male else 53.1 + 1.36 * over)):
        out[name] = (kg * LB_PER_KG, kg)                       # kgToLbs(kg)
    lb = (106 + 6 * over if male else 100 + 5 * over) * FRAMES[frame]
    out['hamwi'] = (lb, lb / LB_PER_KG)                         # lbsToKg(lb)
    return out


def printed_js(lb, kg):
    """displayIdealWeightResults() pr(): whole lb and kg to 0.1, halves up with the 1e-9 nudge."""
    k10 = js_round(kg * 10 + 1e-9)
    return js_round(lb + 1e-9), k10


def round1_js(x):
    return js_round(x * 10 + 1e-9) / 10


def bmi_js(lb, inches, metric=False):
    """calculateBMI(): US units the CDC 703 formula, metric kg/m^2."""
    if metric:
        m = inches * 0.0254
        return (lb / 2.20462) / (m * m)
    return (lb / (inches * inches)) * 703


def weight_bounds_js(inches, lo=18.5, hi=24.9):
    """weightBounds(): whole lb and whole kg whose rounded BMI sits inside 18.5-24.9."""
    k, m2 = inches * inches / 703, math.pow(inches * 0.0254, 2)
    L, H = (lo - 0.05) * k, (hi + 0.05) * k
    LK, HK = (lo - 0.05) * m2, (hi + 0.05) * m2
    return (math.ceil(L - 1e-9), math.ceil(H - 1e-9) - 1, math.ceil(LK - 1e-9), math.ceil(HK - 1e-9) - 1)


# ---- the same numbers in exact fractions -----------------------------------------------------------------------
def half_up(x, places=0):
    """Exact half-up rounding of a Fraction to `places` decimals, as an int scaled by 10**places."""
    s = 10 ** places
    return math.floor(x * s + F(1, 2))


def formulas_exact(inches, sex, frame='medium'):
    over = F(inches) - 60
    out = {}
    for name in NAMES:
        base, per, unit = CONST[sex][name]
        v = F(base) + F(per) * over
        if unit == 'lb':
            v = v * F(str(FRAMES[frame]))
            out[name] = (v, v / F('2.20462'))
        else:
            out[name] = (v * F('2.20462'), v)
    return out


def round_bmi_exact(lb, inches):
    return F(half_up(lb * 703 / F(inches) ** 2, 1), 10)


def bounds_exact(inches, unit):
    """The lowest and highest whole weight whose BMI, rounded half up to 0.1, is 18.5 to 24.9 (brute force)."""
    h = F(inches)
    bmi = (lambda w: F(w) * 703 / h ** 2) if unit == 'lb' else (lambda w: F(w) / (h * F('0.0254')) ** 2)
    ok = lambda w: F(185, 10) <= F(half_up(bmi(w), 1), 10) <= F(249, 10)
    ws = [w for w in range(20, 400) if ok(w)]
    return ws[0], ws[-1]


# ---- labels -------------------------------------------------------------------------------------------------------
def height_label(inches):
    ft, rest = divmod(inches, 12)
    return f'{ft}{FT}{rest}{IN}'


def cm_label(inches):
    return f'{(Decimal(inches) * Decimal("2.54")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)} cm'


def kg_s(k10):
    return f'{k10 // 10}.{k10 % 10}'


# ---- one height -----------------------------------------------------------------------------------------------------
def row(inches, sex, frame='medium'):
    js = formulas_js(inches, sex, frame)
    ex = formulas_exact(inches, sex, frame)
    cells = {}
    for name in NAMES:
        lb, kg = js[name]
        plb, pk10 = printed_js(lb, kg)
        elb, ekg = ex[name]
        assert plb == half_up(elb) and pk10 == half_up(ekg, 1), (inches, sex, frame, name, lb, kg, float(elb), float(ekg))
        cells[name] = {'lb': plb, 'kg': kg_s(pk10), 'lb_exact': round(float(elb), 6), 'kg_exact': round(float(ekg), 6)}
    bmis = []
    for name in NAMES:
        # BMI at the weight as printed (CMB-033), as displayIdealWeightResults() states it: what a reader gets by typing
        # the printed whole pounds into a BMI calculator (from the unrounded weight, Hamwi's 182.6 lb at 5'10" large frame
        # read 26.2 next to a printed 183 lb, which is 26.3).
        plb = cells[name]['lb']
        b = round1_js(bmi_js(plb, inches))
        assert F(round(b * 10), 10) == round_bmi_exact(F(plb), inches), (inches, sex, name, b)
        bmis.append(b)
    minLb, maxLb, minKg, maxKg = weight_bounds_js(inches)
    assert (minLb, maxLb) == bounds_exact(inches, 'lb') and (minKg, maxKg) == bounds_exact(inches, 'kg'), (inches, minLb, maxLb, minKg, maxKg)
    lbs = [cells[n]['lb'] for n in NAMES]
    k10s = [half_up(F(cells[n]['kg']), 1) for n in NAMES]
    return {
        'inches': inches, 'height': height_label(inches), 'cm': cm_label(inches), 'sex': sex, 'frame': frame,
        **cells,
        'span': {'lb': [min(lbs), max(lbs)], 'kg': [kg_s(min(k10s)), kg_s(max(k10s))], 'width_lb': max(lbs) - min(lbs)},
        'bmi': [f'{min(bmis):.1f}', f'{max(bmis):.1f}'],
        'bmi_all': {n: f'{b:.1f}' for n, b in zip(NAMES, bmis)},
        'healthy': {'lb': [minLb, maxLb], 'kg': [minKg, maxKg],
                    # what the calculator prints in US units: the lb limits converted to kg with one decimal (fmtBand alt)
                    'kg_converted': [f'{Decimal(repr(minLb / 2.20462)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)}',
                                     f'{Decimal(repr(maxLb / 2.20462)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)}']},
    }


TABLE_H = {'female': range(60, 73), 'male': range(60, 79)}
tables = {sex: [row(h, sex) for h in hs] for sex, hs in TABLE_H.items()}

# b. Hamwi at a small and a large frame; the other three never move with frame
frames = {}
for sex, hs in TABLE_H.items():
    frames[sex] = []
    for h in hs:
        med = row(h, sex)
        r = {'inches': h, 'height': height_label(h)}
        for f in ('small', 'large'):
            fr = row(h, sex, f)
            for n in ('devine', 'robinson', 'miller'):
                assert fr[n] == med[n], (sex, h, f, n)
            r[f] = {'lb': fr['hamwi']['lb'], 'kg': fr['hamwi']['kg']}
        frames[sex].append(r)

# a(2). the healthy kg column is whole kg at the exact inch height (weightBounds(inches)), each unit on its own (DEVLOG §4).
# The cm label is rounded to 0.1, so typing it into the metric calculator can move a limit by 1 kg: listed here.
cm_label_moves = []
for sex, rows in tables.items():
    for r in rows:
        b = weight_bounds_js(float(r['cm'].split()[0]) / 2.54)
        if [b[2], b[3]] != r['healthy']['kg']:
            cm_label_moves.append(f"{sex} {r['height']}: {r['healthy']['kg'][0]}-{r['healthy']['kg'][1]} kg at the exact height, "
                                  f"{b[2]}-{b[3]} kg typed as {r['cm']}")

# c. worked examples
def example(inches, sex, frames_wanted):
    out = {'inches': inches, 'height': height_label(inches), 'cm': cm_label(inches), 'sex': sex, 'over': inches - 60}
    for f in frames_wanted:
        out[f] = row(inches, sex, f)
    return out


examples = {'woman_5_6': example(66, 'female', ('medium',)), 'man_5_10': example(70, 'male', ('medium', 'large'))}
# the arithmetic as the page writes it
for key, ex in examples.items():
    sex, over = ex['sex'], ex['over']
    steps = {}
    for n in NAMES:
        base, per, unit = CONST[sex][n]
        v = F(base) + F(per) * over
        conv = v / F('2.20462') if unit == 'lb' else v * F('2.20462')      # into the other unit, unrounded
        steps[n] = {'base': base, 'per_inch': per, 'unit': unit, 'value': f'{Decimal(v.numerator) / Decimal(v.denominator):f}',
                    'other_1dp': kg_s(half_up(conv, 1))}
    ex['steps'] = steps
    if 'large' in ex:
        base = F(CONST[sex]['hamwi'][0]) + F(CONST[sex]['hamwi'][1]) * over
        ex['hamwi_large_exact_lb'] = f'{Decimal((base * F("1.1")).numerator) / Decimal((base * F("1.1")).denominator):f}'
        lb = float(base) * 1.1
        ex['hamwi_large_bmi'] = f'{round1_js(bmi_js(lb, 70)):.1f}'

# d. where they agree: span widths as printed (whole lb); ties are listed, with the unrounded spread beside each
def spread(r):
    v = [r[n]['lb_exact'] for n in NAMES]
    return round(max(v) - min(v), 2)


def extremes(rows):
    w = [r['span']['width_lb'] for r in rows]
    lo, hi = min(w), max(w)
    pick = lambda width: [{'height': r['height'], 'lb': r['span']['lb'], 'width': width, 'spread_unrounded': spread(r)}
                          for r in rows if r['span']['width_lb'] == width]
    return pick(lo), pick(hi)


agree = {}
for sex, rows in tables.items():
    nar, wid = extremes(rows)
    bl = min(float(r['bmi'][0]) for r in rows)
    bh = max(float(r['bmi'][1]) for r in rows)
    inside = all(18.5 <= float(b) <= 24.9 for r in rows for b in r['bmi_all'].values())
    agree[sex] = {'narrowest': nar, 'widest': wid, 'bmi': [f'{bl:.1f}', f'{bh:.1f}'], 'all_inside_healthy': inside}

# e. the figure
figure = {}
for sex, hs in TABLE_H.items():
    pts = []
    for h in hs:
        js = formulas_js(h, sex)
        b = weight_bounds_js(h)
        pts.append({'inches': h, **{n: round(js[n][0], 4) for n in NAMES}, 'healthy_lb': [b[0], b[1]]})
    figure[sex] = pts

# f. the formulas table: as published, and converted to the other unit
def conv(v, unit, places):
    x = F(v) / F('2.20462') if unit == 'lb' else F(v) * F('2.20462')
    q = Decimal(x.numerator) / Decimal(x.denominator)
    return f'{q.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)}'


formula_table = {}
for sex in ('female', 'male'):
    formula_table[sex] = {}
    for n in NAMES:
        base, per, unit = CONST[sex][n]
        other = 'kg' if unit == 'lb' else 'lb'
        formula_table[sex][n] = {'unit': unit, 'base': base, 'per_inch': per, 'other_unit': other,
                                 'base_other': conv(base, unit, 1), 'per_inch_other': conv(per, unit, 2)}

# ---- anchors chat worked out on 2026-11-07 (typed into the calculator; US units unless named) ----------------------
def show(r):
    return tuple((r[n]['lb'], r[n]['kg']) for n in NAMES)


T = {sex: {r['inches']: r for r in rows} for sex, rows in tables.items()}
w66 = T['female'][66]
assert show(w66) == ((130, '59.0'), (131, '59.3'), (131, '59.2'), (135, '61.3')), show(w66)
assert w66['span']['lb'] == [130, 135] and w66['healthy']['lb'] == [115, 154] and w66['bmi'] == ['21.0', '21.8'], w66
m70 = T['male'][70]
assert show(m70) == ((166, '75.3'), (161, '73.0'), (157, '71.0'), (155, '70.3')), show(m70)
assert m70['span']['lb'] == [155, 166] and m70['healthy']['lb'] == [129, 173] and m70['bmi'] == ['22.2', '23.8'], m70
m70L = row(70, 'male', 'large')
assert (m70L['hamwi']['lb'], m70L['hamwi']['kg']) == (183, '82.8') and show(m70L)[1:] == show(m70)[1:], show(m70L)
w64S = row(64, 'female', 'small')
assert (w64S['hamwi']['lb'], w64S['hamwi']['kg']) == (108, '49.0'), w64S['hamwi']
assert (w64S['devine']['lb'], w64S['robinson']['lb'], w64S['miller']['lb']) == (121, 123, 129), w64S
assert formulas_js(58, 'female') is None and weight_bounds_js(58)[:2] == (89, 119)
for cm, sex, want, healthy in ((160, 'female', ('52.1', '52.4', '54.1', '57.2'), (48, 63)),
                               (170, 'male', ('66.9', '65.9', '65.2', '66.0'), (54, 72)),
                               (185, 'male', ('83.0', '79.5', '76.4', '74.3'), (64, 85))):
    inches = cm / 2.54                                          # getHeightInches() for a metric entry
    js = formulas_js(inches, sex)
    got = tuple(kg_s(printed_js(*js[n])[1]) for n in NAMES)
    ex = formulas_exact(F(cm) / F('2.54'), sex)
    assert got == tuple(kg_s(half_up(ex[n][1], 1)) for n in NAMES), (cm, got)
    b = weight_bounds_js(inches)
    assert got == want and (b[2], b[3]) == healthy, (cm, got, b)
# d. chat's values. Women: 5'8" alone. Men: 5'6" (140-143) ties at 3 lb with 5'5" (136-139); by the unrounded spread
# 5'6" is the closer of the two (2.78 lb against 3.86), so the page names both heights where it says "closest".
strip = lambda xs: [{k: v for k, v in x.items() if k != 'spread_unrounded'} for x in xs]
assert strip(agree['female']['narrowest']) == [{'height': '5′8″', 'lb': [138, 141], 'width': 3}], agree['female']
assert strip(agree['female']['widest']) == [{'height': '5′0″', 'lb': [100, 117], 'width': 17}], agree['female']
assert strip(agree['male']['narrowest']) == [{'height': '5′5″', 'lb': [136, 139], 'width': 3},
                                              {'height': '5′6″', 'lb': [140, 143], 'width': 3}], agree['male']
assert min(agree['male']['narrowest'], key=lambda x: x['spread_unrounded'])['height'] == '5′6″', agree['male']
assert strip(agree['male']['widest']) == [{'height': '6′6″', 'lb': [180, 214], 'width': 34}], agree['male']
assert agree['female']['bmi'] == ['19.5', '22.8'] and agree['male']['bmi'] == ['20.7', '24.7'], agree   # 22.9 from unrounded weights until CMB-033
assert agree['female']['all_inside_healthy'] and agree['male']['all_inside_healthy'], agree
# the 6'6" men's ends the takeaway names: Miller 180, Hamwi 214
assert T['male'][78]['miller']['lb'] == 180 and T['male'][78]['hamwi']['lb'] == 214, T['male'][78]
# the formulas table chat gave (step 3f)
want_ft = {('female', 'hamwi'): ('45.4', '2.27'), ('male', 'hamwi'): ('48.1', '2.72'),
           ('female', 'devine'): ('100.3', '5.07'), ('male', 'devine'): ('110.2', '5.07'),
           ('female', 'robinson'): ('108.0', '3.75'), ('male', 'robinson'): ('114.6', '4.19'),
           ('female', 'miller'): ('117.1', '3.00'), ('male', 'miller'): ('123.9', '3.11')}
for (sex, n), (b, p) in want_ft.items():
    got = (formula_table[sex][n]['base_other'], formula_table[sex][n]['per_inch_other'])
    assert got == (b, p), (sex, n, got)

out = {
    'about': 'Ideal body weight by the four formulas with the arithmetic of calculateIdealWeight() and '
             'displayIdealWeightResults() in assets/js/calculator.js; our calculation for /ideal-weight/ (CMB-028). '
             'Built by research/ideal-weight-build/iw_stats.py.',
    'constants': CONST,
    'rules': {'lb_per_kg': LB_PER_KG, 'frame': FRAMES, 'start_inches': 60,
              'printed': 'whole lb = Math.round(lb + 1e-9); kg = Math.round(kg * 10 + 1e-9) / 10 (halves up)',
              'span': 'lowest to highest of the four as printed', 'bmi': 'round1(calculateBMI(lb, inches))',
              'healthy': 'weightBounds(inches, 18.5, 24.9): whole lb and whole kg, each unit on its own'},
    'tables': tables,
    'frames': frames,
    'examples': examples,
    'agree': agree,
    'figure': figure,
    'formula_table': formula_table,
    'healthy_kg_cm_label_moves': cm_label_moves,
    'anchors_checked': ["woman 5'6\" medium 130/131/131/135 lb, span 130-135, healthy 115-154, BMI 21.0-21.8",
                        "man 5'10\" medium 166/161/157/155 lb, span 155-166, healthy 129-173, BMI 22.2-23.8; large Hamwi 183 (82.8)",
                        "woman 5'4\" small Hamwi 108 (49.0), Devine 121, Robinson 123, Miller 129",
                        "woman 4'10\" no formula weight, healthy 89-119 lb",
                        'metric woman 160 cm 52.1/52.4/54.1/57.2 kg, healthy 48-63; man 170 cm 66.9/65.9/65.2/66.0, 54-72; '
                        'man 185 cm 83.0/79.5/76.4/74.3, 64-85',
                        "agree: women 5'8\" 138-141 and 5'0\" 100-117; men 5'6\" 140-143 and 6'6\" 180-214; BMI 19.5-22.9 and 20.7-24.7"],
}
path = os.path.join(HERE, 'iw_stats.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
hts = lambda xs: ' and '.join(x['height'] for x in xs)
print(f"{path}: women {len(tables['female'])} rows, men {len(tables['male'])} rows, frames, 2 examples, figure; "
      f"narrowest {hts(agree['female']['narrowest'])} / {hts(agree['male']['narrowest'])}, "
      f"widest {hts(agree['female']['widest'])} / {hts(agree['male']['widest'])}; anchors ok")
