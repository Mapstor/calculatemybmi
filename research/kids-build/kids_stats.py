#!/usr/bin/env python3
"""BMI-for-age numbers for /kids-bmi-calculator/ (CMB-030). usage: python3 research/kids-build/kids_stats.py
Writes kids_stats.json next to this file from data/cdc/bmi-age-2022.csv, CDC's data file for the extended BMI-for-age
growth charts (registry row cdc-extended-bmi-data). Every number on the page that isn't a quoted fact is worked out here.

Checks first, and stops with an error if one fails:
  - the CSV's SHA-256 and size equal CDC's live file as chat read it on 2026-11-11 (7f416a21..., 124,895 bytes);
  - assets/js/cdc-bmi-lms.js holds the CSV's agemos, L, M, S, sigma and P95 for every row of both sexes (219 each). It
    stores each value at 8 significant digits: sigma and P95 have no more than that and are held exactly; L, M and S are
    the CSV values rounded to 8 significant digits (the largest difference, in M, is 5e-7 of a BMI unit). Anything else
    stops the script, and every printed value below is worked out with both sets and must come out the same.

Outputs:
  a. tables: ages 2 to 19, boys and girls, the row at age x 12 + 0.5 (the month that starts at the birthday): BMI at the
     5th, 50th, 85th and 95th percentiles (columns P5, P50, P85, P95) and 120% of the 95th (column pct120ofP95), each
     rounded half up to 0.1 from the CSV's decimal; the 5th, 50th, 85th and 95th also worked out with CDC's LMS formula
     (BMI = M x (1 + L x S x z)^(1/L)) and the same to 0.1;
  b. the median (P50) by age: its value at 2 and 19 and its lowest value with the ages where it falls;
  c. the figure series: every month row from 24.5 to 239.5, the 5th, 85th and 95th percentiles and 120% of the 95th;
  d. chat's step 1 anchors (typed in, US units) and CDC's two examples (through computeKidsPercentile()), worked out
     again from the CSV with CDC's formulas:
       at or below P95   z = ((BMI/M)^L - 1) / (L x S), percentile = PHI(z) x 100
       above P95         percentile = 90 + 10 x PHI((BMI - P95) / sigma), z = PHI^-1(percentile / 100)
     once exactly (statistics.NormalDist, the CSV's values) and once as calculator.js does it (its Abramowitz-Stegun
     normal CDF, its inverse, the values in cdc-bmi-lms.js, US BMI = lb / in^2 x 703, the row at floor(age in months)
     + 0.5); the printed values (BMI and percentile to 0.1 as toFixed(1) rounds, the ordinal as Math.round, % of the
     95th to 0.1, z to 2 decimals, the category, the AAP class) must agree;
  e. the four worked examples on the page, with the row values and steps they print.
Stops with an error if any value differs from what chat worked out (2026-11-11)."""
import csv, hashlib, json, math, os, re, sys
from decimal import Decimal, ROUND_HALF_UP
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CSV = os.path.join(ROOT, 'data/cdc/bmi-age-2022.csv')
LMS_JS = os.path.join(ROOT, 'assets/js/cdc-bmi-lms.js')
OUT = os.path.join(HERE, 'kids_stats.json')
SHA256 = '7f416a213157a5209bb6cbfd1b19292510248f3f31fe43c9ff63f6d8e39f7890'
SIZE = 124895
SEXES = ('male', 'female')
CODE = {'male': '1', 'female': '2'}
JSNAME = {'male': 'boys', 'female': 'girls'}
FIELDS = ('L', 'M', 'S', 'sigma', 'P95')
N = NormalDist()
FT, IN = '′', '″'
problems = []


def stop(msg):
    sys.exit(f'kids_stats.py: STOP: {msg}')


def want(cond, msg):
    if not cond:
        problems.append(msg)


def d1(x):
    """Half up to 0.1 from an exact decimal (a CSV string or a Decimal)."""
    return str(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def fixed(x, places):
    """JavaScript's x.toFixed(places) for a positive double: the exact binary value, halves up."""
    return str(Decimal(x).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def js_round(x):
    return math.floor(x + 0.5)


def ordinal(n):
    v = n % 100
    return f'{n}' + ({1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') if not 11 <= v <= 13 else 'th')


# ------------------------------------------------------------------ the file and the calculator's copy of it
raw = open(CSV, 'rb').read()
if hashlib.sha256(raw).hexdigest() != SHA256 or len(raw) != SIZE:
    stop(f'{CSV}: SHA-256 {hashlib.sha256(raw).hexdigest()}, {len(raw)} bytes; CDC\'s file is {SHA256}, {SIZE} bytes')
rows = list(csv.DictReader(raw.decode('utf-8').splitlines()))
ROWS = {sex: [r for r in rows if r['sex'] == CODE[sex]] for sex in SEXES}
BY = {sex: {Decimal(r['agemos']): r for r in ROWS[sex]} for sex in SEXES}
for sex in SEXES:
    if len(ROWS[sex]) != 219:
        stop(f'{len(ROWS[sex])} {sex} rows, 219 expected')
    months = [Decimal(r['agemos']) for r in ROWS[sex]]
    if months != [Decimal(24)] + [Decimal(m) + Decimal('0.5') for m in range(24, 240)] + [Decimal(240), Decimal('240.5')]:
        stop(f'{sex}: the month rows are not 24, 24.5 to 239.5, 240, 240.5')

js = open(LMS_JS, encoding='utf-8').read()
JS = {}
for sex in SEXES:
    i = js.index(JSNAME[sex] + ':')
    seg = js[i:js.index('}', i)]
    arr = {k: v.split(',') for k, v in re.findall(r'(\w+):\s*\[([^\]]*)\]', seg)}
    if sorted(arr) != sorted(('agemos',) + FIELDS):
        stop(f'cdc-bmi-lms.js {JSNAME[sex]}: arrays {sorted(arr)}')
    if any(len(v) != 219 for v in arr.values()):
        stop(f'cdc-bmi-lms.js {JSNAME[sex]}: array lengths {[len(v) for v in arr.values()]}')
    if [Decimal(a) for a in arr['agemos']] != [Decimal(r['agemos']) for r in ROWS[sex]]:
        stop(f'cdc-bmi-lms.js {JSNAME[sex]}: agemos differ from the CSV')
    JS[sex] = {Decimal(arr['agemos'][k]): {f: float(arr[f][k]) for f in FIELDS} for k in range(219)}
js_diff = {f: 0.0 for f in FIELDS}
for sex in SEXES:
    for r in ROWS[sex]:
        m = Decimal(r['agemos'])
        for f in FIELDS:
            held, csv_v = JS[sex][m][f], float(r[f])
            if f in ('sigma', 'P95'):
                if held != csv_v:
                    stop(f'cdc-bmi-lms.js {sex} {m} {f} = {held}, the CSV has {r[f]}')
            elif held != float(format(csv_v, '.8g')):
                stop(f'cdc-bmi-lms.js {sex} {m} {f} = {held}, the CSV has {r[f]} ({format(csv_v, ".8g")} at 8 significant digits)')
            js_diff[f] = max(js_diff[f], abs(held - csv_v))

# ------------------------------------------------------------------ CDC's formulas, exactly and as calculator.js does them
def as_calc_cdf(z):
    """calculator.js stdNormalCdf(): Abramowitz & Stegun 26.2.17, operation for operation."""
    b1, b2, b3, b4, b5, p = 0.319381530, -0.356563782, 1.781477937, -1.821255978, 1.330274429, 0.2316419
    a = abs(z)
    t = 1 / (1 + p * a)
    pdf = math.exp(-a * a / 2) / math.sqrt(2 * math.pi)
    val = 1 - pdf * (b1 * t + b2 * t * t + b3 * t * t * t + b4 * math.pow(t, 4) + b5 * math.pow(t, 5))
    return 1 - val if z < 0 else val


def as_calc_inv(p):
    """calculator.js stdNormalInv() (the Beasley-Springer-Moro / Acklam rational approximation)."""
    a = [-39.6968302866538, 220.946098424521, -275.928510446969, 138.357751867269, -30.6647980661472, 2.50662827745924]
    b = [-54.4760987982241, 161.585836858041, -155.698979859887, 66.8013118877197, -13.2806815528857]
    c = [-0.00778489400243029, -0.322396458041136, -2.40075827716184, -2.54973253934373, 4.37466414146497, 2.93816398269878]
    d = [0.00778469570904146, 0.32246712907004, 2.445134137143, 3.75440866190742]
    lo, hi = 0.02425, 1 - 0.02425
    if p < lo:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p <= hi:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)


def percentile(bmi, row, cdf, inv):
    """computeKidsPercentile() on one row: (percentile, z, % of the 95th)."""
    L, M, S, sigma, P95 = (row[f] for f in FIELDS)
    if bmi <= P95:
        z = (math.pow(bmi / M, L) - 1) / (L * S)
        pct = cdf(z) * 100
    else:
        pct = 90 + 10 * cdf((bmi - P95) / sigma)
        if pct >= 100:
            pct = 99.99
        z = inv(pct / 100)
    return pct, z, 100 * bmi / P95


def category(bmi, pct, p95):
    """categorizeChildBMI() (CDC's categories for ages 2 through 19) and AAP's class for severe obesity (CDC quotes it)."""
    if p95 >= 120 or bmi >= 35:
        return 'Severe obesity', 3 if (p95 >= 140 or bmi >= 40) else 2
    if pct >= 95:
        return 'Obesity', None
    if pct >= 85:
        return 'Overweight', None
    if pct >= 5:
        return 'Healthy weight', None
    return 'Underweight', None


def csv_row(sex, m):
    r = BY[sex][Decimal(m)]
    return {f: float(r[f]) for f in FIELDS}


def printed(bmi, pct, z, p95):
    line = ('Above the 99th percentile' if pct >= 99.5 else 'Below the 1st percentile' if pct < 0.5
            else f'{ordinal(js_round(pct))} percentile')
    return {'bmi': fixed(bmi, 1), 'percentile': fixed(pct, 1), 'line': line, 'ordinal': js_round(pct),
            'z': fixed(z, 2) if z >= 0 else '-' + fixed(-z, 2), 'pct_of_p95': fixed(p95, 1)}


def work(sex, agemos, bmi):
    """The result both ways; they must print the same. agemos as the calculator gets it (years x 12 + months)."""
    m = Decimal(math.floor(agemos)) + Decimal('0.5')
    pe, ze, p95e = percentile(bmi, csv_row(sex, m), N.cdf, N.inv_cdf)
    pc, zc, p95c = percentile(bmi, JS[sex][m], as_calc_cdf, as_calc_inv)
    out_e, out_c = printed(bmi, pe, ze, p95e), printed(bmi, pc, zc, p95c)
    cat_e, cat_c = category(bmi, pe, p95e), category(bmi, pc, p95c)
    if out_e != out_c or cat_e != cat_c:
        stop(f'{sex} {agemos} months BMI {bmi}: exact {out_e} {cat_e} but as the calculator does it {out_c} {cat_c}')
    return {'row': str(m), 'bmi_unrounded': bmi, 'percentile_unrounded': pe, 'z_unrounded': ze, 'pct_of_p95_unrounded': p95e,
            **out_e, 'category': cat_e[0], 'aap_class': cat_e[1]}


# ------------------------------------------------------------------ a. tables at each birthday
COLS = (('p5', 'P5', 0.05), ('p50', 'P50', 0.5), ('p85', 'P85', 0.85), ('p95', 'P95', 0.95), ('p120', 'pct120ofP95', None))
tables = {}
for sex in SEXES:
    tables[sex] = []
    for age in range(2, 20):
        m = Decimal(age * 12) + Decimal('0.5')
        r = BY[sex][m]
        row = {'age': age, 'agemos': str(m)}
        for key, col, p in COLS:
            row[key] = d1(r[col])
            if p is not None:                         # the LMS formula with the CSV's L, M, S, and with the calculator's
                for src in (csv_row(sex, m), JS[sex][m]):
                    L, M, S = src['L'], src['M'], src['S']
                    v = M * (1 + L * S * N.inv_cdf(p)) ** (1 / L)
                    want(d1(Decimal(repr(v))) == row[key], f'{sex} {age} {key}: column {r[col]} -> {row[key]}, LMS formula {v}')
            else:                                     # CDC's column is 1.2 x the unrounded 95th; P95 is printed to 4 decimals
                v = 1.2 * float(r['P95'])
                want(abs(v - float(r[col])) <= 1.2 * 5e-5 + 1e-9 and d1(Decimal(repr(v))) == row[key],
                     f'{sex} {age} pct120ofP95 {r[col]} vs 1.2 x P95 {v}')
                want(d1(Decimal(repr(1.2 * JS[sex][m]['P95']))) == row[key], f'{sex} {age} 120% of the calculator P95')
        row['p95_exact'], row['sigma'] = r['P95'], r['sigma']
        tables[sex].append(row)

CHAT_TABLE = {('male', 10): ['14.2', '16.6', '19.4', '22.2', '26.6'], ('female', 10): ['14.0', '16.9', '20.0', '23.0', '27.6'],
              ('male', 2): ['14.7', '16.5', '18.1', '19.3', '23.1'], ('female', 2): ['14.4', '16.4', '18.0', '19.1', '22.9'],
              ('male', 19): ['18.7', '22.5', '26.4', '29.7', '35.7'], ('female', 19): ['17.8', '21.6', '26.1', '31.0', '37.2']}
for (sex, age), vals in CHAT_TABLE.items():
    got = [tables[sex][age - 2][k] for k, *_ in COLS]
    want(got == vals, f'table {sex} age {age}: {got}, chat {vals}')

# ------------------------------------------------------------------ b. the median by age
medians = {}
for sex in SEXES:
    by_age = {r['age']: r['p50'] for r in tables[sex]}
    low = min(by_age.values(), key=Decimal)
    medians[sex] = {'by_age': by_age, 'at_2': by_age[2], 'at_19': by_age[19], 'lowest': low,
                    'lowest_ages': [a for a, v in by_age.items() if v == low]}
want((medians['male']['at_2'], medians['male']['lowest'], medians['male']['lowest_ages'], medians['male']['at_19'])
     == ('16.5', '15.4', [5, 6], '22.5'), f'boys medians {medians["male"]}')
want((medians['female']['at_2'], medians['female']['lowest'], medians['female']['lowest_ages'], medians['female']['at_19'])
     == ('16.4', '15.2', [5, 6], '21.6'), f'girls medians {medians["female"]}')

# ------------------------------------------------------------------ c. the figure series, every month 24.5 to 239.5
figure = {sex: [{'agemos': float(m), 'p5': float(BY[sex][m]['P5']), 'p85': float(BY[sex][m]['P85']),
                 'p95': float(BY[sex][m]['P95']), 'p120': float(BY[sex][m]['pct120ofP95'])}
                for m in (Decimal(k) + Decimal('0.5') for k in range(24, 240))] for sex in SEXES}
want(all(len(v) == 216 for v in figure.values()), 'figure series length')

# ------------------------------------------------------------------ d. chat's anchors and CDC's examples
def us_bmi(ft, inch, lb):
    h = ft * 12 + inch
    return (lb / (h * h)) * 703                      # calculateBMI() in US units, same operations


ANCHORS = [   # name, sex, years, months, ft, in, lb; chat's printed values (None = chat gave none)
    ('girl-10-70', 'female', 10, 0, 4, 6, 70, {'bmi': '16.9', 'ordinal': 50, 'percentile': '50.2', 'category': 'Healthy weight', 'pct_of_p95': '73.4'}),
    ('girl-10-98', 'female', 10, 0, 4, 6, 98, {'bmi': '23.6', 'ordinal': 96, 'percentile': '95.6', 'category': 'Obesity', 'pct_of_p95': '102.8'}),
    ('boy-14-6-150', 'male', 14, 6, 5, 5, 150, {'bmi': '25.0', 'ordinal': 92, 'percentile': '92.1', 'category': 'Overweight'}),
    ('girl-16-190', 'female', 16, 0, 5, 4, 190, {'bmi': '32.6', 'ordinal': 97, 'percentile': '97.2', 'category': 'Obesity', 'pct_of_p95': '112.8'}),
    ('boy-2-32', 'male', 2, 0, 2, 10, 32, {'bmi': '19.5', 'percentile': '95.5', 'category': 'Obesity', 'pct_of_p95': '100.9'}),
]
anchors = {}
for name, sex, y, mo, ft, inch, lb, chat in ANCHORS:
    a = work(sex, y * 12 + mo, us_bmi(ft, inch, lb))
    a.update({'sex': sex, 'years': y, 'months': mo, 'ft': ft, 'in': inch, 'lb': lb, 'height': f'{ft}{FT}{inch}{IN}'})
    for k, v in chat.items():
        want(a[k] == v, f'anchor {name} {k}: {a[k]}, chat {v}')
    anchors[name] = a
# the 2-year-old with the 24.0 row the calculator used before CMB-030: 95.4, as chat worked it out
b = anchors['boy-2-32']['bmi_unrounded']
old = percentile(b, csv_row('male', 24), N.cdf, N.inv_cdf)
old_c = percentile(b, JS['male'][Decimal(24)], as_calc_cdf, as_calc_inv)
want(fixed(old[0], 1) == fixed(old_c[0], 1) == '95.4', f'the 24.0 row gives {old[0]} / {old_c[0]}, chat 95.4')
anchors['boy-2-32']['percentile_with_24_0_row'] = fixed(old[0], 1)

cdc_girl = work('female', 114, 21.2)                  # CDC: 9 years 6 months (114.5), P95 22.3979, z 1.4215, 92.2
cdc_boy = work('male', 50, 22.6)                      # CDC: 4 years 2 months (50.5), P95 17.8219, sigma 2.398288, 99.7683
cdc_girl.update({'sex': 'female', 'years': 9, 'months': 6, 'p95': BY['female'][Decimal('114.5')]['P95'],
                 'z4': fixed(cdc_girl['z_unrounded'], 4)})
cdc_boy.update({'sex': 'male', 'years': 4, 'months': 2, 'p95': BY['male'][Decimal('50.5')]['P95'],
                'sigma': BY['male'][Decimal('50.5')]['sigma'], 'percentile4': fixed(cdc_boy['percentile_unrounded'], 4),
                'percentile2': fixed(cdc_boy['percentile_unrounded'], 2)})
want(cdc_girl['row'] == '114.5' and cdc_girl['p95'] == '22.3979' and cdc_girl['z4'] == '1.4215' and cdc_girl['percentile'] == '92.2',
     f'CDC girl {cdc_girl}')
want(cdc_boy['row'] == '50.5' and cdc_boy['p95'] == '17.8219' and cdc_boy['sigma'] == '2.398288' and cdc_boy['percentile4'] == '99.7683'
     and cdc_boy['percentile2'] == '99.77' and cdc_boy['pct_of_p95'] == '126.8' and cdc_boy['category'] == 'Severe obesity'
     and cdc_boy['aap_class'] == 2, f'CDC boy {cdc_boy}')

# ------------------------------------------------------------------ e. the worked examples' steps
def step_lms(sex, a):
    r = BY[sex][Decimal(a['row'])]
    return {'L': r['L'], 'M': r['M'], 'S': r['S'], 'p95': r['P95'], 'z4': fixed(a['z_unrounded'], 4) if a['z_unrounded'] >= 0 else '-' + fixed(-a['z_unrounded'], 4)}


def step_ext(sex, a):
    r = BY[sex][Decimal(a['row'])]
    arg = (a['bmi_unrounded'] - float(r['P95'])) / float(r['sigma'])
    return {'p95': r['P95'], 'sigma': r['sigma'], 'arg2': fixed(arg, 2), 'phi4': fixed(N.cdf(arg), 4)}


g98, b150 = anchors['girl-10-98'], anchors['boy-14-6-150']
examples = {
    'cdc_girl': {**cdc_girl, 'formula': 'lms'},
    'cdc_boy': {**cdc_boy, 'formula': 'extended', 'steps': step_ext('male', cdc_boy)},
    'girl_10_98': {**g98, 'formula': 'extended', 'steps': step_ext('female', g98),
                   'bmi_exact2': fixed(g98['bmi_unrounded'], 2), 'p95_1dp': tables['female'][8]['p95']},
    'boy_14_6_150': {**b150, 'formula': 'lms', 'steps': step_lms('male', b150), 'bmi_exact2': fixed(b150['bmi_unrounded'], 2)},
}
# The steps as the page prints them must give the printed result when a reader works them again: the extended formula
# from the BMI to 2 decimals with the row's P95 and sigma as CDC prints them; the LMS formula from the BMI to 2 decimals
# with L, M and S to 4 decimals; CDC's boy from the arg and PHI to the printed digits.
ex = examples['cdc_boy']['steps']
ex['arg4'] = fixed((22.6 - float(ex['p95'])) / float(ex['sigma']), 4)
ex['phi5'] = fixed(N.cdf(float(ex['arg4'])), 5)
want(fixed(90 + 10 * float(ex['phi5']), 4) == cdc_boy['percentile4'], f'CDC boy steps {ex}')
st = examples['girl_10_98']['steps']
again = 90 + 10 * N.cdf((float(examples['girl_10_98']['bmi_exact2']) - float(st['p95'])) / float(st['sigma']))
want(fixed(again, 1) == g98['percentile'], f'girl 98 lb steps give {again}')
st = examples['boy_14_6_150']['steps']
st.update({k + '4': fixed(abs(float(st[k])), 4) for k in ('L', 'M', 'S')})
L4, M4, S4 = -float(st['L4']), float(st['M4']), float(st['S4'])
want(float(st['L']) < 0, 'L is negative at 174.5 months')
z_again = ((float(examples['boy_14_6_150']['bmi_exact2']) / M4) ** L4 - 1) / (L4 * S4)
want(fixed(z_again, 2) == b150['z'] and fixed(N.cdf(z_again) * 100, 1) == b150['percentile'],
     f'boy 14 steps give z {z_again}, {N.cdf(z_again) * 100}')
st['z2_again'], st['pct_again'] = fixed(z_again, 2), fixed(N.cdf(z_again) * 100, 1)

# ------------------------------------------------------------------ f. one BMI at two ages (the page's "BMI changes with age")
age_example = {'bmi': '17.0'}
for key, age in (('girl_5', 5), ('girl_19', 19)):
    a = work('female', age * 12, 17.0)
    age_example[key] = {'age': age, 'category': a['category'], 'line': a['line'],
                        'p5': tables['female'][age - 2]['p5'], 'p85': tables['female'][age - 2]['p85']}
want(age_example['girl_5']['category'] == 'Overweight' and age_example['girl_19']['category'] == 'Underweight'
     and age_example['girl_5']['p85'] == '16.8' and age_example['girl_19']['p5'] == '17.8', f'age example {age_example}')
want(g98['bmi_unrounded'] > float(BY['female'][Decimal('120.5')]['P95']), 'the 98 lb girl is above her row\'s 95th')
want(b150['bmi_unrounded'] <= float(BY['male'][Decimal('174.5')]['P95']), 'the 14-year-old boy is at or below his row\'s 95th')
want(cdc_girl['bmi_unrounded'] <= float(cdc_girl['p95']) and cdc_boy['bmi_unrounded'] > float(cdc_boy['p95']), 'CDC examples sides')

if problems:
    for p in problems:
        print('MISMATCH', p)
    stop(f'{len(problems)} value(s) differ from chat\'s or from each other')

out = {
    'source': {'file': 'data/cdc/bmi-age-2022.csv', 'sha256': SHA256, 'bytes': SIZE, 'rows_per_sex': 219,
               'calculator_copy': ('assets/js/cdc-bmi-lms.js holds every row at 8 significant digits: sigma and P95 exactly, '
                                   'L, M and S rounded'),
               'calculator_copy_largest_difference': {f: float(f'{v:.3g}') for f, v in js_diff.items()}},
    'tables': tables, 'medians': medians, 'figure': figure, 'anchors': anchors,
    'cdc_examples': {'girl': cdc_girl, 'boy': cdc_boy}, 'examples': examples, 'age_example': age_example,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
print(f'{OUT}: tables 2 x 18 rows, figure 2 x {len(figure["male"])} months, {len(anchors)} anchors and CDC\'s 2 examples; '
      f'every value equals chat\'s; cdc-bmi-lms.js = the CSV at 8 significant digits (largest difference '
      f'{max(js_diff.values()):.1g})')
