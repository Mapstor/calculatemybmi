# CMB-039 — order-free body-fat percentiles (DEVLOG §5 P3)

Done by chat on 2026-11-13 (D-24, D-26). Every weighted percentile of CDC's 2011–2018 DXA readings now comes from one
rule: the weighted midpoint rule over distinct values, as `research/body-fat-calculator-build/bfc_stats.py` applied it
since CMB-020. Before, `research/body-fat/compute_bf.py` and `research/body-fat-chart-build/bfpc_stats.py` (and
`research/chart-men-build/bcm_dxa.py`) placed each reading at its own midpoint after `np.argsort`, an unstable sort, so the
order of tied readings (DXDTOPF is recorded to 0.1) moved printed percentiles by 0.1.

## What changed

- Scripts: `compute_bf.py`, `bfpc_stats.py`, `bcm_dxa.py` use the distinct-value rule; `bfc_stats.py` now asserts its
  50 quartiles equal `bfpc_stats.json` to its 4 stored decimals (was "within 0.08"); `load.py` takes the raw folder.
- Stats: `bf_results.json`, `bfpc_stats.json`, `bcm_dxa.json` regenerated. Only percentile fields moved (`p`, `cdf`, `q`,
  `pf_*_bmi`, `p1`–`p99`); samples, counts, means, CIs and shares are unchanged. `bfc_stats.json` is unchanged.
- `/blog/bmi-chart-men/` compares readings with the medians as printed (22.1, 26.9). Over distinct values the overweight
  median is 26.9027, just above the 26.9 readings; compared unrounded it would drop every man at 26.9 and turn 14.0%
  into 13.2% while the page prints the median as 26.9.
- Pages (`apply.py`, `edits.json`, digits only): `/body-fat-percentage-chart/` 101 edits (age tables, BMI-figure labels
  and points, the rank tool's quartiles, FAQ women 20–59 5th percentile 27.3% in text and schema, US median of men 20–39
  26.1% and 40–59 28.2%), `/blog/bmi-chart-men/` 8 (box plot and its labels: healthy BMI 10th to 90th percentile 15.9%
  to 27.6%), `/body-fat-calculator/` 1 and `/women-bmi-calculator/` 1 (tool data). The chart page's schema
  dateModified and sitemap lastmod move to 2026-11-13; the two calculators' visible text is unchanged.
- Files: the CSV download (`csv_download.py`, row for row as `research/body-fat/gen_bf.py` wrote it), the printable chart
  image and `bfpc_chart.csv` (`chart_bfpc.py`; pixel-identical to the live image when run on the old stats).
- Unchanged at print: the by_bmi medians the other pages quote (women 33.4 / 39.5 / 44.0, men 22.1 / 26.9 / 31.6), men's
  overweight 10th percentile 21.7, the women's healthy middle half 29.8–36.5 (printed from the 4-decimal value 29.8454;
  `bf_results.json` stores 29.85, so print by_bmi values from `bfpc_stats.json`, never from the 2-decimal record).
  Differential runs of `gen_hbr.py`, `gen_bc.py`, `gen_bcw.py` and `gen_htm.py` (medians printed at 1 decimal) changed
  nothing.

## How the page edits were found (tools/)

The old generators must never run on the repo (DEVLOG §4). `tools/difgen.py` runs one in a scratch copy on its base
commit twice, with the stats before and after, and `tools/merge3.py` applies the difference to the live page wherever the
live page still holds the generator's text (one conflict, the chart page's JSON-LD, applied by hand: 27.2% to 27.3%).
`tools/digits_only.py` confirms only digits changed. `edits.json` records the result; `apply.py` is hash-guarded.

## Reproduce

    python3 research/body-fat/load.py RAW_DIR                      # CDC DEMO/BMX/DXX G-J .xpt, not in the repo
    (cd research/body-fat && python3 compute_bf.py)
    python3 research/body-fat-chart-build/bfpc_stats.py RAW_DIR research/body-fat/bf_results.json research/body-fat-chart-build/bfpc_stats.json
    python3 research/body-fat-calculator-build/bfc_stats.py RAW_DIR research/body-fat-chart-build/bfpc_stats.json research/body-fat-calculator-build/bfc_stats.json
    python3 research/chart-men-build/bcm_dxa.py RAW_DIR research/body-fat-chart-build/bfpc_stats.json research/chart-men-build/bcm_dxa.json
    python3 research/cmb-039/csv_download.py research/body-fat/bf_results.json body-fat-percentage-chart/body-fat-percentiles-nhanes-2011-2018.csv
    python3 research/body-fat-chart-build/chart_bfpc.py research/body-fat-chart-build/bfpc_stats.json assets/images/charts/body-fat-percentage-chart.png
    python3 research/cmb-039/apply.py && python3 research/cmb-039/registry.py

Checks: the page tests of the four pages (each fails on its old page with the new stats) and of
`/blog/how-to-measure-body-fat/`, `scripts/check_structure.py`, `research/f1/verify.py`, `scripts/check_images.py`, `research/dates/date_truth.py`.
