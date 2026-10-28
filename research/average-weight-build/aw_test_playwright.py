#!/usr/bin/env python3
"""Average weight page checks in Chromium (CMB-019). Needs Python Playwright + Chromium, so chat or the Mac runs it.
Serve the repo (python3 -m http.server 8000), then:
  python3 research/average-weight-build/aw_test_playwright.py http://localhost:8000 research/average-weight/avgw_results.json
  - the national figures equal NCHS's published values, typed in here (Series 3 No. 50 / FastStats: 199.0 and 171.8 lb,
    68.9 and 63.5 in, BMI 29.4 and 30.0, waist 40.6 and 38.5 in, medians 191.0 and 162.0 lb), and the 1960-2002 and
    2015-2018 values equal the sources' tables, typed in (Advance Data No. 347 Table 6; Series 3 No. 46);
  - by-height tables: every row (women 4'9"-5'9", men 5'2"-6'3") has its #women-F-I / #men-F-I id, centimeters, the
    average with its kilograms, the middle half, the healthy range found here by brute force (whole pounds, BMI rounded to
    one decimal), the BMI 25+ share and a dagger when fewer than 60 were measured; at every height the average is above
    the healthy range; the age, BMI-and-waist and since-1960 tables equal the stats file;
  - the CSV download parses and carries the same numbers;
  - the hero: one dot per height at the drawn position of its average, the healthy band at the brute-force limits, hover
    labels and the description carry the same numbers;
  - the tool: the page's data equals the stats file; 10 cases (both sexes, both units, with and without a weight and an
    age group, a height with too few measured, out-of-range input) give the answer, the BMI, the healthy range, the age
    average, the height rank and the figure worked out here from the stats file, plus typed-in answers (180 lb at 5'9" ->
    36% of men measured at 5'8"-5'10" weigh less; 171 lb at 5'4" -> 57% of women; BMI 26.6 and 29.3); the unit switch converts
    the inputs; the hidden rows stay hidden;
  - the prose figures: each sentence that states a number is rebuilt here from the stats file and found on the page;
  - head: title, description, one robots max-image-preview:large, canonical, og:image and twitter:image = the 16:9 preferred
    image (1200 x 675) with its alt, the Article image list and primaryImageOfPage, author named, preferred files at size;
    Article and Dataset dateModified = the sitemap lastmod; no {TODAY} left; no page-level style, no <article>;
  - every internal link answers 200 and every outside link is a registry URL; every contents chip lands on its section;
    every FAQ opens with one tap; the FAQ JSON-LD equals the visible answers;
  - the page is never wider than the screen at 320, 360, 390 and 1280 px; every table fits its frame at 390 and 1280;
    rendered SVG labels (hero and the tool's figure) don't overlap, stay inside their figure and sit on no shape; no
    JavaScript error."""
import sys, os, json, math, re, csv, io, struct
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import sync_playwright

base, stats = sys.argv[1], sys.argv[2]
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(stats)), '..', '..'))
AV = json.load(open(stats))
REG_URLS = set()
for r in csv.DictReader(open(os.path.join(ROOT, 'research/data-sources.csv'), encoding='utf-8')):
    REG_URLS |= {r['url']} | {e.strip() for e in r['endpoint'].split(' ; ')} | set(re.findall(r'https?://[^\s;,)"]+', r['notes']))
URL = base + '/average-weight/'
SITE = 'https://calculatemybmi.net'
M, F = AV['men'], AV['women']
AGES = ('20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80+')
LBKG = 2.2046                                                              # NCHS's factor, as the data were converted

def r1(x): return math.floor(x * 10 + 0.5 + 1e-9) / 10
def f1(x): return f'{x:.1f}'
def d1(x): return f'{r1(x):.1f}'                                          # the tool's rounding (half up)
def whole(x): return int(math.floor(x + 0.5))
def ft(h): return f'{h // 12}′{h % 12}″'
def cm1(h): return str((Decimal(h) * Decimal('2.54')).quantize(Decimal('0.1'), ROUND_HALF_UP))
def kg1(lb): return str((Decimal(str(lb)) / Decimal('2.2046')).quantize(Decimal('0.1'), ROUND_HALF_UP))
def png_size(b): return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else None
def brute(h_in, cm, lo, hi, unit):
    m = cm / 100
    ws = [w for w in range(20, 701) if lo <= r1(w * 703 / h_in ** 2 if unit == 'lb' else w / m ** 2) <= hi]
    return ws[0], ws[-1]
def healthy_lb(h): return brute(h, h * 2.54, 18.5, 24.9, 'lb')
HT = {s: {int(h): v for h, v in AV[s]['height'].items()} for s in ('women', 'men')}

fails, checks = [], 0
def ok(cond, msg):
    global checks; checks += 1
    if not cond: fails.append(msg)

# ---- 1. Typed-in published values (NCHS Series 3 No. 50 Tables 4, 8, 12; FastStats; Advance Data 347; Series 3 No. 46).
ok((f1(M['wt_lb']['mean']), f1(F['wt_lb']['mean']), M['wt_lb']['n'], F['wt_lb']['n']) == ('199.0', '171.8', 2688, 3254), 'weights')
ok((f1(M['ht_in']['mean']), f1(F['ht_in']['mean'])) == ('68.9', '63.5'), 'heights')
ok((f1(M['BMXBMI']['mean']), f1(F['BMXBMI']['mean'])) == ('29.4', '30.0'), 'BMI means')
ok((f1(M['waist_in']['mean']), f1(F['waist_in']['mean'])) == ('40.6', '38.5'), 'waist means')
ok((f1(M['wt_pct']['p50']), f1(F['wt_pct']['p50'])) == ('191.0', '162.0'), 'weight medians')
ok([f1(M['age'][g]['wt']['mean']) for g in AGES] == ['191.3', '201.5', '210.1', '203.0', '196.7', '193.4', '180.1'], 'men by age')
ok([f1(F['age'][g]['wt']['mean']) for g in AGES] == ['164.9', '178.3', '177.3', '180.0', '171.0', '162.8', '149.7'], 'women by age')
ok(sorted(HT['women']) == list(range(57, 70)) and sorted(HT['men']) == list(range(62, 76)), 'heights with 30+ measured')
for s in HT:
    for h, v in HT[s].items():
        ok(v['wt']['n'] >= 30, f'{s} {ft(h)} n {v["wt"]["n"]}')
        ok(v['wt']['mean'] > healthy_lb(h)[1], f'{s} {ft(h)}: average not above the healthy range')
AD347 = {'men': (166.3, 191.0), 'women': (140.2, 164.3)}; S46 = (199.8, 170.8)

# ---- 2. The numbers the prose states, rebuilt here.
A54, A65, A57f, A59, A57m = HT['women'][64], HT['women'][65], HT['women'][67], HT['men'][69], HT['men'][67]
B25 = {s: (whole(min(v['bmi25_plus']['pct'] for v in HT[s].values())), whole(max(v['bmi25_plus']['pct'] for v in HT[s].values()))) for s in HT}
ok(B25 == {'women': (60, 78), 'men': (64, 81)}, f'BMI 25+ ranges {B25}')
def stp(d, a, b): return d['age_steps'][f'{b} minus {a}']['wt_lb']
UPF, UPM, DM80 = stp(F, '20–29', '30–39'), stp(M, '20–29', '30–39'), stp(M, '70–79', '80+')
for x in (UPF, UPM, DM80): ok(x['excludes_0'], 'a stated age step is not clear of zero')
for a, b in (('50–59', '60–69'), ('60–69', '70–79'), ('70–79', '80+')):
    ok(stp(F, a, b)['excludes_0'] and stp(F, a, b)['diff'] < 0, f'women {b} vs {a} not clearly lower')
for a, b in (('30–39', '40–49'), ('40–49', '50–59')):
    for d in (F, M): ok(not stp(d, a, b)['excludes_0'], f'{b} vs {a} is clear of zero but the page says it is not')
lo30 = {s: min(AV[s]['age'][g]['wt']['mean'] for g in AGES[1:4]) for s in HT}
hi30 = {s: max(AV[s]['age'][g]['wt']['mean'] for g in AGES[1:4]) for s in HT}
N74 = {s: AV[s]['wt_20_74']['mean'] for s in HT}
WPq = {s: (whole(AV[s]['waist_pct']['p25']), whole(AV[s]['waist_pct']['p75'])) for s in HT}
def mid(v): return whole(v['q'][0]), whole(v['q'][2])
b64, b65, b67, b69, b72 = healthy_lb(64), healthy_lb(65), healthy_lb(67), healthy_lb(69), healthy_lb(72)
PROSE = [
    f'The average US man weighs {f1(M["wt_lb"]["mean"])} lb and the average woman {f1(F["wt_lb"]["mean"])} lb, measured by CDC in 2021–2023.',
    f'The average US man weighs {f1(M["wt_lb"]["mean"])} lb ({kg1(M["wt_lb"]["mean"])} kg) and the average woman '
    f'{f1(F["wt_lb"]["mean"])} lb ({kg1(F["wt_lb"]["mean"])} kg): adults 20 and over, measured by CDC in August 2021–August '
    f'2023. At 5′4″ the average woman weighs {f1(A54["wt"]["mean"])} lb; at 5′9″ the average man weighs {f1(A59["wt"]["mean"])} lb',
    f'and {B25["women"][0]}% to {B25["women"][1]}% of women and {B25["men"][0]}% to {B25["men"][1]}% of men of each height have a BMI of 25 or more.',
    f'{f1(UPF["diff"])} lb more for women and {f1(UPM["diff"])} lb more for men.',
    f'men 80 and over weigh {f1(-DM80["diff"])} lb less than men in their 70s.',
    f'The average man is {f1(M["ht_in"]["mean"])} inches tall and the average woman {f1(F["ht_in"]["mean"])} inches; their average '
    f'BMI is {f1(M["BMXBMI"]["mean"])} and {f1(F["BMXBMI"]["mean"])}, and their average waist {f1(M["waist_in"]["mean"])} and '
    f'{f1(F["waist_in"]["mean"])} inches (CDC).',
    f'the average weight of men aged 20 to 74 has risen {f1(N74["men"] - AD347["men"][0])} lb and of women '
    f'{f1(N74["women"] - AD347["women"][0])} lb',
    f'At 5′4″, US women weigh {f1(A54["wt"]["mean"])} lb on average; the middle half weigh {mid(A54)[0]} to {mid(A54)[1]} lb, '
    f'and a healthy weight is {b64[0]} to {b64[1]} lb.',
    f'At 5′9″, US men weigh {f1(A59["wt"]["mean"])} lb on average; the middle half weigh {mid(A59)[0]} to {mid(A59)[1]} lb, '
    f'and a healthy weight is {b69[0]} to {b69[1]} lb. At 6′0″ the average is {f1(HT["men"][72]["wt"]["mean"])} lb, and a '
    f'healthy weight tops out at {b72[1]} lb.',
    f'({min(v["wt"]["n"] for v in HT["women"].values())} to {max(v["wt"]["n"] for v in HT["women"].values())} women per height; survey-weighted)',
    f'({min(v["wt"]["n"] for v in HT["men"].values())} to {max(v["wt"]["n"] for v in HT["men"].values())} men per height; survey-weighted)',
    'Heights under 4′9″ and over 5′9″: fewer than 30 measured.', 'Heights under 5′2″ and over 6′3″: fewer than 30 measured.',
    f'Women in their 30s weigh {f1(UPF["diff"])} lb more on average than women in their 20s, and men {f1(UPM["diff"])} lb more. '
    f'From 30 to 59 the averages ({f1(lo30["women"])} to {f1(hi30["women"])} lb for women, {f1(lo30["men"])} to '
    f'{f1(hi30["men"])} lb for men) are not statistically different: the 95% confidence interval of the gap between any two '
    'of those age groups includes zero.',
    f'The average US man is {f1(M["ht_in"]["mean"])} inches tall ({cm1(Decimal(str(round(M["ht_in"]["mean"], 4))))} cm, about 5′9″) and the '
    f'average woman {f1(F["ht_in"]["mean"])} inches ({cm1(Decimal(str(round(F["ht_in"]["mean"], 4))))} cm, about 5′3.5″).',
    f'Half of men weigh {f1(M["wt_pct"]["p50"])} lb or more and half of women {f1(F["wt_pct"]["p50"])} lb or more',
    f'the middle half measure {WPq["men"][0]} to {WPq["men"][1]} and {WPq["women"][0]} to {WPq["women"][1]} inches.',
    'US guidelines treat a waist over 102 cm (40 in) in men and over 88 cm (35 in) in women as a sign of higher risk',
    f'{f1(M["waist_over_line"]["pct"])}% of men and {f1(F["waist_over_line"]["pct"])}% of women are over those lines (our calculation, in centimeters).',
    f'Men aged 20 to 74 averaged {f1(AD347["men"][0])} lb in 1960–1962 and {f1(AD347["men"][1])} lb in 1999–2002; women of the '
    f'same ages {f1(AD347["women"][0])} lb and {f1(AD347["women"][1])} lb',
    f'In 2021–2023 men of those ages averaged {f1(N74["men"])} lb and women {f1(N74["women"])} lb (our calculation), '
    f'{f1(N74["men"] - AD347["men"][0])} lb and {f1(N74["women"] - AD347["women"][0])} lb more than in 1960–1962.',
    f'That is CDC’s average for men 20 and over in 2015–2018, with {f1(S46[1])} lb for women',
    # FAQ
    f'{f1(M["wt_lb"]["mean"])} lb ({kg1(M["wt_lb"]["mean"])} kg) for US men aged 20 and over, measured by CDC in 2021–2023 (NCHS). '
    f'Half of men weigh {f1(M["wt_pct"]["p50"])} lb or more. The average man is {f1(M["ht_in"]["mean"])} inches tall, about '
    f'5′9″, and at 5′9″ a healthy weight is {b69[0]} to {b69[1]} lb (CDC categories).',
    f'{f1(F["wt_lb"]["mean"])} lb ({kg1(F["wt_lb"]["mean"])} kg) for US women aged 20 and over who aren’t pregnant',
    f'{f1(A54["wt"]["mean"])} lb ({kg1(A54["wt"]["mean"])} kg), from {A54["wt"]["n"]} US women measured at 5′4″; the middle half '
    f'weigh {mid(A54)[0]} to {mid(A54)[1]} lb (our calculation from CDC data, 2021–2023). A healthy weight at 5′4″ is '
    f'{b64[0]} to {b64[1]} lb (CDC categories).',
    f'{f1(A65["wt"]["mean"])} lb ({kg1(A65["wt"]["mean"])} kg), from {A65["wt"]["n"]} US women measured at 5′5″; the middle half '
    f'weigh {mid(A65)[0]} to {mid(A65)[1]} lb',
    f'A healthy weight at 5′5″ is {b65[0]} to {b65[1]} lb',
    f'{f1(A57f["wt"]["mean"])} lb ({kg1(A57f["wt"]["mean"])} kg), from {A57f["wt"]["n"]} US women measured at 5′7″; the middle '
    f'half weigh {mid(A57f)[0]} to {mid(A57f)[1]} lb',
    f'A healthy weight at 5′7″ is {b67[0]} to {b67[1]} lb',
    f'{f1(A59["wt"]["mean"])} lb ({kg1(A59["wt"]["mean"])} kg), from {A59["wt"]["n"]} US men measured at 5′9″',
    f'Some answers give {f1(S46[0])} lb for 5′9″, but that is CDC’s 2015–2018 average for all US men, whatever their height.',
    f'US men who are 5′7″ weigh {f1(A57m["wt"]["mean"])} lb on average, and the middle half weigh {mid(A57m)[0]} to '
    f'{mid(A57m)[1]} lb ({A57m["wt"]["n"]} men;',
    'For a man of 6′4″ or taller, 200 lb is in the healthy range (a BMI of 24.3 at 6′4″); at 6′3″ it sits right at the line '
    '(25.0); from 5′9″ to 6′2″ it is overweight (a BMI of 29.5 down to 25.7); at 5′8″ and shorter it is obesity, a BMI of '
    '30.4 or more',
    'The average is above the healthy range at every height measured (women 4′9″–5′9″, men 5′2″–6′3″), and',
    'At every height shown, the average is above the band.',
    'all 160 weight means and percentiles in Table 4, the adult height and waist means and percentiles in Tables 8 and 12, '
    'and the adult BMI means and medians in Table 10 (204 values)',
    'Tables 4 (weight), 8 (height), 10 (BMI) and 12 (waist).',
    'The tool compares a weight with the people measured at the height entered or an inch either side, heights rounded to the nearest inch.',
    f'By BMI, yes: 180 lb at 5′9″ is a BMI of 26.6, in CDC’s overweight range of 25 to 29.9, and a healthy weight at 5′9″ is '
    f'{b69[0]} to {b69[1]} lb',
    f'US men who are 5′9″ weigh {f1(A59["wt"]["mean"])} lb on average, and half weigh {whole(A59["q"][1])} lb or more',
    f'Half of men have a BMI of {f1(M["bmi_p50"])} or more, and half of women {f1(F["bmi_p50"])} or more.',
    f'The middle half of men measure {WPq["men"][0]} to {WPq["men"][1]} inches and of women {WPq["women"][0]} to {WPq["women"][1]} inches',
    f'US men weigh {f1(M["age"]["20–29"]["wt"]["mean"])} lb on average in their 20s, {f1(lo30["men"])} to {f1(hi30["men"])} lb '
    f'from 30 to 59, and {f1(M["age"]["80+"]["wt"]["mean"])} lb at 80 and over; women weigh {f1(F["age"]["20–29"]["wt"]["mean"])} '
    f'lb in their 20s, {f1(lo30["women"])} to {f1(hi30["women"])} lb from 30 to 59, and {f1(F["age"]["80+"]["wt"]["mean"])} lb at 80 and over',
    f'That is CDC’s average for 2015–2018 (and {f1(S46[1])} lb for women; NCHS).',
    f'({M["wt_lb"]["n"]:,} men and {F["wt_lb"]["n"]:,} women aged 20 and over)',
]
ok((r1(703 * 200 / 76 ** 2), r1(703 * 200 / 69 ** 2), r1(703 * 200 / 74 ** 2), r1(703 * 200 / 75 ** 2), r1(703 * 200 / 68 ** 2),
    r1(703 * 180 / 69 ** 2)) == (24.3, 29.5, 25.7, 25.0, 30.4, 26.6), 'typed-in BMIs')
ok(all(r1(703 * 200 / h ** 2) >= 30 for h in range(56, 69)) and all(25 <= r1(703 * 200 / h ** 2) < 30 for h in range(69, 75))
   and 24.99 < 703 * 200 / 75 ** 2 < 25, '200 lb bands')
for d in (F, M):                                                           # 30 to 59: every pair of decades includes zero
    ok(sorted(d['age_pairs_30_59']) == ['40–49 minus 30–39', '50–59 minus 30–39', '50–59 minus 40–49'] and
       not any(x['wt_lb']['excludes_0'] for x in d['age_pairs_30_59'].values()), '30-59 pairs')

# ---- 3. The tool, worked out here from the stats file.
def below(c, v):
    if v < c[0]: return 0.0
    if v > c[98]: return 100.0
    for i in range(98):
        if v <= c[i + 1]:
            sp = c[i + 1] - c[i]; return i + 1 + ((v - c[i]) / sp if sp > 0 else 0)
    return 99.0
def share_txt(x): return 'more than 99%' if x >= 99.5 else 'under 1%' if x <= 0.5 else f'{whole(x)}%'
def cat(b): return ('underweight', 'underweight') if b < 18.5 else ('normal', 'a healthy weight') if b < 25 else \
                   ('overweight', 'overweight') if b < 30 else ('obese', 'obesity')
WD, ONE = {'f': 'women', 'm': 'men'}, {'f': 'woman', 'm': 'man'}
SX = {'f': 'women', 'm': 'men'}
def tool_expect(sex, units, ft_, in_, cm_, w, age):
    metric = units == 'metric'; s = SX[sex]; u = ' kg' if metric else ' lb'; k = 1 / LBKG if metric else 1
    h_in = cm_ / 2.54 if metric else ft_ * 12 + in_
    cm = cm_ if metric else h_in * 2.54
    if not 48 <= h_in <= 90: return {'msg': 'Enter a height from 4 ft to 7 ft 6 in (122 to 229 cm).'}
    if w and not ((23 <= w <= 318) if metric else (50 <= w <= 700)):
        return {'msg': 'Enter a weight from 50 to 700 lb (23 to 318 kg), or leave it empty.'}
    hr = math.floor(h_in + 0.5); v = HT[s].get(hr); hb = brute(h_in, cm, 18.5, 24.9, 'kg' if metric else 'lb')
    tag = ft(hr) + (f' ({cm1(hr)} cm)' if metric else '')
    def one(lb): return f'{d1(lb / LBKG)} kg ({d1(lb)} lb)' if metric else f'{d1(lb)} lb ({d1(lb / LBKG)} kg)'
    def rng(a, z): return f'{whole(round(a, 1) * k)} to {whole(round(z, 1) * k)}{u}'
    E = {}
    if w:
        b = r1(w / (cm / 100) ** 2) if metric else r1(703 * w / h_in ** 2); E['bmi'] = (b, cat(b))
    if v and w:
        wl = w * LBKG if metric else w
        win = f'{ft(hr - 1)} to {ft(hr + 1)}' + (f' ({cm1(hr - 1)} to {cm1(hr + 1)} cm)' if metric else '')
        E['card'] = [share_txt(below([round(x, 1) for x in v['cdf']], wl)), f'of US {WD[sex]} measured at {win} weigh less than you',
                     f'The average {ONE[sex]} of {ft(hr)} weighs {one(round(v["wt"]["mean"], 1))}; the middle half weigh '
                     f'{rng(v["q"][0], v["q"][2])}.']
    elif v:
        E['card'] = [f'{d1(round(v["wt"]["mean"], 1) * k)}{u}', f'is the average weight of US {WD[sex]} who are {tag}',
                     f'The middle half weigh {rng(v["q"][0], v["q"][2])}; {v["wt"]["n"]:,} {WD[sex]} measured (CDC, 2021–2023; our calculation).']
    else:
        E['card'] = [f'{d1(round(AV[s]["wt_lb"]["mean"], 1) * k)}{u}', f'is the average weight of all US {WD[sex]}',
                     f'CDC measured fewer than 30 {WD[sex]} at {ft(hr)}, too few for an average at that height.']
    E['tint'] = E['bmi'][1][0] if w else ''
    E['healthy'] = f'{hb[0]} to {hb[1]}{u}'
    if w:
        E['bmi_line'] = (f'Your BMI is {E["bmi"][0]:.1f}, {E["bmi"][1][1]} (CDC categories). A healthy weight at your height is '
                         f'{E["healthy"]}.' + (f' US {WD[sex]} of {ft(hr)} have an average BMI of {round(v["bmi"]["mean"], 1):.1f}.' if v else ''))
    if age: E['age_line'] = (f'They weigh {one(round(AV[s]["age"][age]["wt"]["mean"], 1))} on average, across all heights. All US '
                             f'{WD[sex]} average {one(round(AV[s]["wt_lb"]["mean"], 1))}.')
    hp = below([round(x, 2) for x in AV[s]['ht_q']], h_in)
    E['height_line'] = ('Shorter than almost all' if hp <= 0.5 else 'Taller than almost all' if hp >= 99.5 else
                        f'Taller than about {whole(hp)}% of') + f' US {WD[sex]} (CDC measured heights).'
    if v:
        vals = [round(x, 1) * k for x in v['p10_p90']] + [hb[0], hb[1]] + ([w] if w else [])
        st = 10 if metric else 20
        if math.ceil(max(vals) / st) - math.floor(min(vals) / st) > 7: st *= 2
        lo, hi = math.floor(min(vals) / st) * st, math.ceil(max(vals) / st) * st
        E['ticks'] = [str(x) + (u if x == hi else '') for x in range(lo, hi + 1, st)]
        E['scale'] = (lo, hi)
        E['n_window'] = f'The share compares you with the {v["nwin"]:,} {WD[sex]} measured at {ft(hr - 1)} to {ft(hr + 1)} (heights rounded to the nearest inch).'
    return E
CASES = [('f', 'us', 5, 4, None, 171, '30–39'), ('m', 'us', 5, 9, None, 180, ''), ('m', 'metric', None, None, 175, 80, '50–59'),
         ('f', 'us', 5, 10, None, 150, ''), ('f', 'us', 5, 4, None, None, ''), ('m', 'us', 8, 0, None, None, ''),
         ('m', 'us', 6, 3, None, 320, '80+'), ('f', 'metric', None, None, 160, None, '70–79'), ('m', 'us', 5, 9, None, 40, ''),
         ('m', 'us', 5, 9.4, None, 150, '')]
TYPED = {1: ('36%', 26.6), 0: ('57%', 29.3)}
for i, (pct, b) in TYPED.items():
    e = tool_expect(*CASES[i]); ok(e['card'][0] == pct and e['bmi'][0] == b, f'typed-in tool case {i}: {e["card"][0]} {e["bmi"][0]}')

# ---- 4. The page.
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = br.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg.goto(URL, wait_until='load')
    html_ = pg.content()
    raw = pg.request.get(URL).text()
    ok('{TODAY}' not in raw, '{TODAY} placeholder left in the page')
    ok('<style' not in raw and '<article' not in raw, 'page-level style or an <article> wrapper')
    mainsrc = raw[raw.index('<main'):raw.index('</main>')]
    ok('style="' not in re.sub(r'(?s)<svg.*?</svg>|<script>.*?</script>', '', mainsrc), 'inline style in <main>')
    body = re.sub(r'\s+', ' ', pg.inner_text('main') + ' ' + ' '.join(pg.eval_on_selector_all('.faq-answer', 'as => as.map(a => a.textContent)')))
    for s in PROSE:
        ok(s in body, f'prose not found: {s!r}')
    for s in ('peak', 'Tables 6 and 8', 'normal BMI for women', 'have gained', 'within an inch', 'margins of error',
              'over 40 inches (102 cm)', 'from 5′9″ to 6′3″', 'every height and age'):
        ok(s not in body, f'removed wording back on the page: {s!r}')

    # Tables.
    tables = pg.evaluate("""() => [...document.querySelectorAll('main table')].map(t => [t.caption ? t.caption.textContent : '',
        [...t.querySelectorAll('tbody tr')].map(r => [r.id, ...[...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim())])])""")
    tb = {cap: rws for cap, rws in tables}
    ok(len(tables) == 5, f'{len(tables)} tables')
    for s, word in (('women', 'women'), ('men', 'men')):
        rows = tb.get(f'Average weight of US {word} by height', [])
        want = []
        for h in sorted(HT[s]):
            v = HT[s][h]; hl = healthy_lb(h)
            want.append([f'{word}-{h // 12}-{h % 12}', f'{ft(h)}{"†" if v["wt"]["n"] < 60 else ""} {cm1(h)} cm',
                         f'{f1(v["wt"]["mean"])} {kg1(v["wt"]["mean"])} kg', f'{whole(v["q"][0])}–{whole(v["q"][2])}',
                         f'{hl[0]}–{hl[1]}', f'{whole(v["bmi25_plus"]["pct"])}%'])
        ok(rows == want, f'{s} by-height table {rows[:2]} vs {want[:2]}')
    w54 = [r for r in tb.get('Average weight of US women by height', []) if r[0] == 'women-5-4']
    ok(w54 == [['women-5-4', '5′4″ 162.6 cm', '171.2 77.7 kg', '140–194', '108–145', '65%']], f'typed-in 5′4″ row {w54}')
    m59 = [r for r in tb.get('Average weight of US men by height', []) if r[0] == 'men-5-9']
    ok(m59 == [['men-5-9', '5′9″ 175.3 cm', '204.0 92.5 kg', '171–235', '125–168', '76%']], f'typed-in 5′9″ row {m59}')
    age = tb.get('Average weight of US adults by age (lb)', [])
    want = [['', g, f1(F['age'][g]['wt']['mean']), f1(M['age'][g]['wt']['mean'])] for g in AGES] + \
           [['', 'All 20+', f1(F['wt_lb']['mean']), f1(M['wt_lb']['mean'])]]
    ok(age == want, f'age table {age} vs {want}')
    bw = tb.get('Average BMI and waist size (inches) of US adults by age', [])
    want = [['', g, f1(F['age'][g]['bmi']['mean']), f1(M['age'][g]['bmi']['mean']), f1(F['age'][g]['waist']['mean']),
             f1(M['age'][g]['waist']['mean'])] for g in AGES]
    ok(bw == want, f'BMI and waist table {bw} vs {want}')
    tm = tb.get('Average weight of US adults aged 20 to 74 (lb)', [])
    ok(tm == [['', '1960–1962', '140.2', '166.3'], ['', '1999–2002', '164.3', '191.0'],
              ['', '2021–2023', f1(N74['women']), f1(N74['men'])]], f'since-1960 table {tm}')

    # The CSV download.
    res = pg.request.get(base + '/average-weight/average-weight-nhanes-2021-2023.csv')
    ok(res.status == 200, 'CSV does not answer 200')
    lines = res.text().splitlines()
    ok(lines[0].startswith('"# Average body weight of US adults 20+'), 'CSV header note')
    rows = list(csv.DictReader(io.StringIO('\n'.join(lines[1:]))))
    for s in HT:
        for h, v in HT[s].items():
            r = [x for x in rows if x['table'] == 'height' and x['sex'] == s and x['group'] == f'{h // 12}\'{h % 12}"']
            ok(len(r) == 1 and r[0]['mean_weight_lb'] == f1(v['wt']['mean']) and r[0]['n'] == str(v['wt']['n']) and
               r[0]['healthy_range_lb'] == '%d-%d' % healthy_lb(h) and r[0]['median_lb'] == f1(v['q'][1]) and
               r[0]['bmi25_plus_pct'] == f1(v['bmi25_plus']['pct']) and r[0]['mean_bmi'] == f1(v['bmi']['mean']) and
               r[0]['se_bmi'] == f'{v["bmi"]["se"]:.2f}' and r[0]['mean_waist_in'] == '', f'CSV row {s} {ft(h)}')
        for g in AGES:
            r = [x for x in rows if x['table'] == 'age' and x['sex'] == s and x['group'] == g]
            a = AV[s]['age'][g]
            ok(len(r) == 1 and r[0]['mean_weight_lb'] == f1(a['wt']['mean']) and r[0]['mean_bmi'] == f1(a['bmi']['mean']) and
               r[0]['mean_waist_in'] == f1(a['waist']['mean']) and r[0]['se_waist_in'] == f'{a["waist"]["se"]:.2f}', f'CSV age {s} {g}')
        r = [x for x in rows if x['table'] == 'overall' and x['sex'] == s]
        ok(len(r) == 1 and r[0]['mean_weight_lb'] == f1(AV[s]['wt_lb']['mean']) and r[0]['median_lb'] == f1(AV[s]['wt_pct']['p50'])
           and r[0]['mean_bmi'] == f1(AV[s]['BMXBMI']['mean']) and r[0]['mean_waist_in'] == f1(AV[s]['waist_in']['mean']), f'CSV overall {s}')
    ok(len(rows) == 27 + 14 + 2, f'{len(rows)} CSV rows')

    # The hero.
    hero = pg.evaluate("""() => { const s = document.querySelector('main figure svg');
        return {id: s.getAttribute('aria-labelledby'), desc: s.querySelector('desc').textContent,
                dots: [...s.querySelectorAll('circle')].map(c => [c.querySelector('title') ? c.querySelector('title').textContent : '',
                       +c.getAttribute('cx'), +c.getAttribute('cy'), c.getAttribute('fill')]),
                band: (s.querySelector('polygon') || {getAttribute: () => ''}).getAttribute('points')}; }""")
    ok(hero['id'] == 'fig-hero-t fig-hero-d', 'hero ids')
    def hx(h): return 46 + (h - 57) * 262 / 18
    def hy(w): return 296 - (w - 80) * 200 / 180
    data_dots = [d for d in hero['dots'] if d[0]]
    ok(len(data_dots) == 13 + 14, f'{len(data_dots)} hero dots')
    for s, col, lab in (('women', '#be185d', 'Women'), ('men', '#4338ca', 'Men')):
        for h, v in sorted(HT[s].items()):
            d = [x for x in data_dots if x[0] == f'{lab} {ft(h)}: average {f1(v["wt"]["mean"])} lb ({v["wt"]["n"]} measured)']
            ok(len(d) == 1 and abs(d[0][1] - hx(h)) < 0.06 and abs(d[0][2] - hy(v['wt']['mean'])) < 0.06 and d[0][3] == col,
               f'hero dot {s} {ft(h)}: {d}')
            spoken = f'{h // 12} feet' + (f' {h % 12} inch' + ('es' if h % 12 > 1 else '') if h % 12 else '')
            ok(f'{spoken} {f1(v["wt"]["mean"])} pounds' in hero['desc'], f'hero desc {s} {ft(h)}')
            ok(hy(v['wt']['mean']) < hy(healthy_lb(h)[1]), f'hero: {s} {ft(h)} dot not above the band')
    pts = [tuple(map(float, p.split(','))) for p in hero['band'].split()]
    want = [(hx(h), hy(healthy_lb(h)[1])) for h in range(57, 76)] + [(hx(h), hy(healthy_lb(h)[0])) for h in range(75, 56, -1)]
    ok(len(pts) == len(want) and all(abs(a[0] - b[0]) < 0.06 and abs(a[1] - b[1]) < 0.06 for a, b in zip(pts, want)), 'hero band')

    # The tool's data.
    D = pg.evaluate('window.AWT')
    for c, s in (('f', 'women'), ('m', 'men')):
        ok(D['avg'][c] == round(AV[s]['wt_lb']['mean'], 1), f'tool avg {c}')
        ok(sorted(D['h'][c], key=int) == [str(h) for h in sorted(HT[s])], f'tool heights {c}')
        for h, v in HT[s].items():
            e = D['h'][c][str(h)]
            ok(e['a'] == round(v['wt']['mean'], 1) and e['n'] == v['wt']['n'] and e['q'] == [round(x, 1) for x in v['q']] and
               e['p'] == [round(x, 1) for x in v['p10_p90']] and e['c'] == [round(x, 1) for x in v['cdf']] and
               e['b'] == round(v['bmi']['mean'], 1) and e['w'] == v['nwin'], f'tool data {c} {h}')
        ok(D['age'][c] == {g: round(AV[s]['age'][g]['wt']['mean'], 1) for g in AGES}, f'tool ages {c}')
        ok(D['hq'][c] == [round(x, 2) for x in AV[s]['ht_q']], f'tool height percentiles {c}')
    ok(not pg.is_visible('#awt-metric') and pg.is_visible('#awt-us'), 'metric row shows in US mode')

    # The tool: cases.
    tool_figs = []
    for i, (sex, units, ft_, in_, cm_, w, age) in enumerate(CASES):
        pg.click(f'#awt [data-sex="{sex}"]'); pg.click(f'#awt [data-units="{units}"]')
        if units == 'us': pg.fill('#awt-ft', str(ft_)); pg.fill('#awt-in', str(in_))
        else: pg.fill('#awt-cm', str(cm_))
        pg.fill('#awt-w', '' if w is None else str(w)); pg.select_option('#awt-age', age)
        pg.click('#awt-go'); pg.wait_for_timeout(60)
        E = tool_expect(sex, units, ft_, in_, cm_, w, age)
        got = pg.evaluate("""() => { const o = document.getElementById('awt-out'), q = s => o.querySelector(s);
            return {vis: o.classList.contains('visible'), text: o.innerText.replace(/\\s+/g, ' ').trim(),
                    card: q('.bmi-result-card') ? [q('.bmi-value').textContent, q('.bmi-category').textContent, q('.bmi-range').textContent,
                           q('.bmi-result-card').className] : null,
                    notes: [...o.querySelectorAll('.er-note')].map(n => n.textContent),
                    heads: [...o.querySelectorAll('h3')].map(h => h.textContent),
                    ticks: q('svg') ? [...q('svg').querySelectorAll('text')].map(t => t.textContent) : null}; }""")
        ok(got['vis'], f'case {i}: no output')
        if 'msg' in E:
            ok(got['text'] == E['msg'] and got['card'] is None, f'case {i}: message {got["text"]!r}'); continue
        ok(got['card'] and got['card'][:3] == E['card'], f'case {i}: card {got["card"]} vs {E["card"]}')
        ok(got['card'] and got['card'][3] == 'bmi-result-card' + (' ' + E['tint'] if E['tint'] else ''), f'case {i}: tint {got["card"]}')
        if 'bmi_line' in E: ok(E['bmi_line'] in got['notes'], f'case {i}: BMI line {E["bmi_line"]!r} not in {got["notes"]}')
        if 'age_line' in E: ok(E['age_line'] in got['notes'], f'case {i}: age line')
        ok(E['height_line'] in got['notes'], f'case {i}: height line {E["height_line"]!r} {got["notes"]}')
        if 'ticks' in E:
            want_t = ([f'You {whole(w)}{" kg" if units == "metric" else " lb"}'] if w else []) + E['ticks']
            ok(got['ticks'] == want_t, f'case {i}: figure labels {got["ticks"]} vs {want_t}')
            ok(any(n.startswith(f'Green: a healthy weight at your height, {E["healthy"]} ') for n in got['notes']), f'case {i}: healthy note')
            if w: ok(any(E['n_window'] in n for n in got['notes']), f'case {i}: window note {E["n_window"]!r}')
            tool_figs.append(i)
        elif not w:
            ok(f'A healthy weight at your height is {E["healthy"]} (BMI 18.5 to 24.9, CDC).' in got['notes'], f'case {i}: healthy section')
    # The unit switch converts what is typed.
    pg.click('#awt [data-units="us"]'); pg.fill('#awt-ft', '5'); pg.fill('#awt-in', '9'); pg.fill('#awt-w', '180')
    pg.click('#awt [data-units="metric"]')
    ok((pg.input_value('#awt-cm'), pg.input_value('#awt-w'), pg.inner_text('#awt-w-label')) == ('175', '81.6', 'Weight (kg)'), 'switch to metric')
    ok(pg.is_visible('#awt-metric') and not pg.is_visible('#awt-us'), 'rows after the switch to metric')
    pg.click('#awt [data-units="us"]')
    ok((pg.input_value('#awt-ft'), pg.input_value('#awt-in'), pg.input_value('#awt-w')) == ('5', '9', '180'), 'switch back to US')

    # Head and JSON-LD.
    head = pg.evaluate("""() => ({title: document.title, desc: document.querySelector('meta[name="description"]').content,
        robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content),
        canon: document.querySelector('link[rel="canonical"]').href,
        og: [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content),
        ogalt: (document.querySelector('meta[property="og:image:alt"]') || {}).content || '',
        ogw: document.querySelector('meta[property="og:image:width"]').content, ogh: document.querySelector('meta[property="og:image:height"]').content,
        twt: (document.querySelector('meta[name="twitter:title"]') || {}).content || '',
        tw: [...document.querySelectorAll('meta[name="twitter:image"]')].map(m => m.content)})""")
    P = {r: f'{SITE}/assets/images/preferred/average-weight-{r}.png' for r in ('1x1', '4x3', '16x9')}
    ok(head['title'] == 'Average Weight for Men and Women by Height and Age (CDC)', f'title {head["title"]!r}')
    ok(len(head['desc']) <= 160 and head['desc'].startswith('The average US man weighs 199.0 lb and the average woman 171.8 lb'), f'description {head["desc"]!r}')
    ok(head['robots'] == ['max-image-preview:large'], f'robots {head["robots"]}')
    ok(head['canon'] == URL.replace(base, SITE), f'canonical {head["canon"]}')
    ok(head['og'] == [P['16x9']] and head['tw'] == [P['16x9']] and (head['ogw'], head['ogh']) == ('1200', '675'), f'og/twitter {head}')
    ok(head['ogalt'] == 'Chart: the average weight of US women (4′9″ to 5′9″) and men (5′2″ to 6′3″) at each height, above the '
       'band of healthy weights for each height.' and head['twt'] == 'Average weight for men and women by height and age',
       f'og alt / twitter title {head}')
    for r, size in (('1x1', (1200, 1200)), ('4x3', (1200, 900)), ('16x9', (1200, 675))):
        res = pg.request.get(f'{base}/assets/images/preferred/average-weight-{r}.png')
        ok(res.status == 200 and png_size(res.body()) == size, f'preferred image {r}')
    ok(pg.request.get(base + '/average-weight/og-average-weight.png').status == 404, 'old OG image still served')
    sm = pg.request.get(base + '/sitemap.xml').text()
    ent = re.search(r'<url><loc>https://calculatemybmi\.net/average-weight/</loc>(.*?)</url>', sm)
    lastmod = re.search(r'<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>', ent.group(1)).group(1) if ent else None
    ld = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))""")
    ok([x['@type'] for x in ld] == ['Article', 'Dataset', 'BreadcrumbList', 'FAQPage'], f'JSON-LD types {[x["@type"] for x in ld]}')
    L = {x['@type']: x for x in ld}
    art, ds = L.get('Article', {}), L.get('Dataset', {})
    h1 = pg.inner_text('h1')
    ok(art.get('headline') == h1 == 'Average Weight for Men and Women by Height and Age', 'Article headline is not the H1')
    ok(art.get('image') == [P['1x1'], P['4x3'], P['16x9']], f'Article image list {art.get("image")}')
    ok(art.get('mainEntityOfPage', {}).get('primaryImageOfPage', {}).get('url') == P['16x9'], 'primaryImageOfPage')
    ok(art.get('author', {}).get('name') == 'Marko Visic' and art.get('datePublished') == '2026-10-03', 'author / datePublished')
    ok(art.get('dateModified') == ds.get('dateModified') == lastmod and re.fullmatch(r'\d{4}-\d{2}-\d{2}', lastmod or ''),
       f'dateModified {art.get("dateModified")!r} / {ds.get("dateModified")!r} vs sitemap lastmod {lastmod!r}')
    ok(set(art.get('citation', [])) <= REG_URLS, 'Article citation not in the registry')
    ok(ds.get('distribution', [{}])[0].get('contentUrl') == SITE + '/average-weight/average-weight-nhanes-2021-2023.csv'
       and ds.get('license') == 'https://creativecommons.org/licenses/by/4.0/' and ds.get('temporalCoverage') == '2021-08/2023-08', 'Dataset')
    ok(L.get('BreadcrumbList', {}).get('itemListElement', [{}])[-1].get('name') == h1, 'breadcrumb name is not the H1')
    vis = pg.evaluate("""() => [...document.querySelectorAll('.faq-item')].map(i => [i.querySelector('.faq-question').textContent.trim(),
        i.querySelector('.faq-answer').textContent.replace(/\\s+/g, ' ').trim()])""")
    ok(len(vis) == 13 and [[q['name'], q['acceptedAnswer']['text']] for q in L.get('FAQPage', {}).get('mainEntity', [])] == vis,
       'FAQ JSON-LD differs from the visible answers')

    # Links, chips, FAQ.
    hrefs = pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
    for h_ in sorted({h_.split('#')[0] for h_ in hrefs if h_.startswith('/')}):
        ok(pg.request.get(base + h_).status == 200, f'internal link {h_} does not answer 200')
    for h_ in {h_ for h_ in hrefs if h_.startswith('#')}:
        ok(pg.evaluate('h => !!document.getElementById(h.slice(1))', h_), f'anchor {h_} missing')
    outside = {h_ for h_ in pg.eval_on_selector_all('main a[href^="http"]', 'as => as.map(a => a.getAttribute("href"))')}
    ok(outside <= REG_URLS, f'outside links not in the registry: {sorted(outside - REG_URLS)}')
    chips = pg.eval_on_selector_all('.toc-inline a', 'as => as.map(a => a.getAttribute("href"))')
    ok(chips == ['#compare', '#women', '#men', '#age', '#bmi-waist', '#since-1960', '#faq', '#sources'], f'chips {chips}')
    for href in chips:
        ok(pg.evaluate('h => { const e = document.querySelector(h); return !!e && e.offsetHeight > 0 && e.tagName === "SECTION"; }', href), f'chip {href} has no section')
    qs = pg.query_selector_all('.faq-question')
    for i, q in enumerate(qs):
        q.scroll_into_view_if_needed(); q.click(); pg.wait_for_timeout(30)
        ok(pg.evaluate('i => document.querySelectorAll(".faq-item")[i].classList.contains("open")', i), f'FAQ {i} did not open')
        ok(pg.evaluate('i => document.querySelectorAll(".faq-answer")[i].getBoundingClientRect().height > 20', i), f'FAQ {i} answer not shown')

    # Widths, table frames, rendered labels (the hero, and the tool's figure after a compare).
    for w in (320, 360, 390, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(150)
        pg.click('#awt [data-sex="m"]'); pg.fill('#awt-ft', '6'); pg.fill('#awt-in', '3'); pg.fill('#awt-w', '320'); pg.click('#awt-go')
        pg.wait_for_timeout(60)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        ok(sw <= w, f'page {sw}px wide at {w}')
        fits = pg.evaluate("""() => [...document.querySelectorAll('main .table-responsive > table')].map(t => [t.caption ? t.caption.textContent : '',
            t.offsetWidth, t.parentElement.clientWidth, getComputedStyle(t.parentElement).overflowX])""")
        for cap, tw, fw, ov in fits:
            ok(ov == 'auto', f'{cap}: frame does not scroll')
            if w in (390, 1280): ok(tw <= fw + 1, f'table scrolls at {w}: {cap} {tw} > {fw}')
        if w in (390, 1280):
            res = pg.evaluate("""() => [...document.querySelectorAll('main figure svg, #awt-out svg')].map(svg => {
                const r = svg.getBoundingClientRect(), bx = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
                return {box: [r.left, r.top, r.right, r.bottom],
                        texts: [...svg.querySelectorAll('text')].map(e => [e.textContent, ...bx(e)]),
                        shapes: [...svg.querySelectorAll('rect, circle')].map(e => [e.getAttribute('fill'), ...bx(e)])}; })""")
            ok(len(res) == 2, f'{len(res)} figures at {w}')
            for f in res:
                L_, T_, R_, B_ = f['box']
                for i, a in enumerate(f['texts']):
                    ok(a[1] >= L_ - 0.5 and a[3] <= R_ + 0.5 and a[2] >= T_ - 0.5 and a[4] <= B_ + 0.5, f'{w}px label outside its figure: {a[0]!r}')
                    for c2 in f['texts'][i + 1:]:
                        if a[1] < c2[3] - 0.5 and c2[1] < a[3] - 0.5 and a[2] < c2[4] - 0.5 and c2[2] < a[4] - 0.5:
                            fails.append(f'{w}px labels overlap: {a[0]!r} / {c2[0]!r}')
                    for s in f['shapes']:
                        if a[1] < s[3] - 0.5 and s[1] < a[3] - 0.5 and a[2] < s[4] - 0.5 and s[2] < a[4] - 0.5:
                            fails.append(f'{w}px label over a shape: {a[0]!r} / {s[0]}')
    ok(not errs, f'JS errors {errs}')
    br.close()
print(f'{checks} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL', f)
sys.exit(1 if fails else 0)
