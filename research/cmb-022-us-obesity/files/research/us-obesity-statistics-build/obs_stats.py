#!/usr/bin/env python3
"""CMB-022: the share of US adults who weigh 300 lb or more, for /us-obesity-statistics/ (FAQ "What percent of Americans
weigh over 300 pounds?"), from CDC's NHANES August 2021-August 2023 files, and an independent cross-check of the
research/home-build/home_stats.json figures the page prints (class 1 and class 2 obesity, the all-adult mean BMI).

Input: research/average-weight/raw/DEMO_L.xpt + BMX_L.xpt (public-domain CDC files kept in the repo; registry
nhanes-2021-2023-exam-files).
Population: adults aged 20 and older, examined (WTMEC2YR > 0), not pregnant (RIDEXPRG != 1), with a measured weight
(BMXWT) for the 300 lb share and a measured BMI (BMXBMI) for the cross-check. Weights: WTMEC2YR.
300 lb = 136.0777 kg (0.45359237 kg per lb); BMXWT is recorded to 0.1 kg, so 136.1 kg is the first value at or over
300 lb (136.0 kg is 299.8 lb).
Standard errors: Taylor linearization of the weighted share over the strata (SDMVSTRA) and primary sampling units
(SDMVPSU); degrees of freedom = PSUs - strata; 95% interval with the t value for those degrees of freedom.
The page prints the all-adult share to 0.1 and as a whole percent and the men's and women's as whole percents; the script
stops if any of them sits within 0.05 of a rounding tie.

usage: python3 obs_stats.py RAW_DIR HOME_STATS_JSON OUT_JSON
"""
import sys, json, math
import numpy as np, pandas as pd

raw, home, out = sys.argv[1], sys.argv[2], sys.argv[3]
D = pd.read_sas(f'{raw}/DEMO_L.xpt', format='xport').merge(pd.read_sas(f'{raw}/BMX_L.xpt', format='xport'), on='SEQN', how='left')
W = D.WTMEC2YR.fillna(0)
adult = (D.RIDAGEYR >= 20) & (W > 0) & (D.RIDEXPRG != 1)
LB300 = 300 * 0.45359237
assert abs(LB300 - 136.0777110) < 1e-6
heavy = D.BMXWT >= LB300 - 1e-9
assert ((D.BMXWT == 136.1) <= heavy).all() and not heavy[D.BMXWT == 136.0].any()

T15 = {15: 2.131449545559323}                            # t(0.975, 15)


def taylor(dom, y):
    """weighted share of y within dom, with its linearized standard error and 95% interval"""
    w = W.where(dom, 0.0)
    tw = w.sum()
    p = float((w * y).sum() / tw)
    z = w * (y.astype(float) - p) / tw
    g = pd.DataFrame({'h': D.SDMVSTRA, 'i': D.SDMVPSU, 'z': z}).groupby(['h', 'i']).z.sum().reset_index()
    var = 0.0
    for _, s in g.groupby('h'):
        n = len(s)
        var += n / (n - 1) * ((s.z - s.z.mean()) ** 2).sum()
    df = g.i.groupby(g.h).count().sum() - g.h.nunique()
    se = math.sqrt(var)
    t = T15[df]
    return {'pct': round(100 * p, 4), 'se': round(100 * se, 4), 'ci95': [round(100 * (p - t * se), 4), round(100 * (p + t * se), 4)],
            'n': int(dom.sum()), 'df': int(df)}


dw = adult & D.BMXWT.notna()
lb300 = {'all': taylor(dw, heavy), 'men': taylor(dw & (D.RIAGENDR == 1), heavy), 'women': taylor(dw & (D.RIAGENDR == 2), heavy)}
# printed: the all-adult share to 0.1 and as a whole percent, men and women as whole percents; none may sit near a tie
assert abs((lb300['all']['pct'] * 10) % 1 - 0.5) > 0.05 and abs(lb300['all']['pct'] % 1 - 0.5) > 0.05, lb300['all']
for k in ('men', 'women'):
    assert abs(lb300[k]['pct'] % 1 - 0.5) > 0.05, ('a whole-percent tie', k, lb300[k]['pct'])
assert lb300['all']['df'] == 15

# Cross-check of home_stats.json with this script's own code
db = adult & D.BMXBMI.notna()
b = D.BMXBMI
c1 = taylor(db, (b >= 30.0) & (b < 35.0))['pct']
c2 = taylor(db, (b >= 35.0) & (b < 40.0))['pct']
ob = taylor(db, b >= 30.0)['pct']
mean = float((W[db] * b[db]).sum() / W[db].sum())
H = json.load(open(home))
assert int(db.sum()) == H['adults']['bmi_n'] == 5929
assert (f'{c1:.1f}', f'{c2:.1f}', f'{ob:.1f}', f'{mean:.1f}') == (f'{H["category_shares_pct"]["obesity_class_1"]:.1f}',
        f'{H["category_shares_pct"]["obesity_class_2"]:.1f}', f'{H["obesity_pct"]:.1f}', f'{H["adults"]["mean"]:.1f}') == \
       ('20.6', '10.3', '40.3', '29.7'), (c1, c2, ob, mean)

res = {'source': 'CDC NHANES August 2021-August 2023 (DEMO_L, BMX_L); adults aged 20+, examined, pregnant women excluded',
       'method': 'WTMEC2YR-weighted shares; Taylor linearization over SDMVSTRA x SDMVPSU, 15 df, t = 2.131',
       'lb300': lb300, 'lb300_kg': round(LB300, 4),
       'check_home_stats': {'class_1_pct': round(c1, 4), 'class_2_pct': round(c2, 4), 'obesity_pct': round(ob, 4),
                            'mean_bmi': round(mean, 4), 'n_bmi': int(db.sum())}}
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps(res['lb300']), 'check', res['check_home_stats'])
