#!/bin/bash
# Reset the scratch tree to GitHub main (e63e2e1) and rebuild CMB-014 from scratch.
# The page is generated with {TODAY}; a copy goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=/home/claude/c14; B=/home/claude/build/cmb014; DAY=${1:-2026-10-15}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/chart-women-build assets/images/og assets/images/charts
cp $B/files/research/chart-women-build/{bcw_stats.py,bcw_stats.json,gen_bcw.py,chart_bcw.py,og_bcw.py,bcw_test_playwright.py,bcw_grid.csv,SPEC.md} research/chart-women-build/
cp $B/files/assets/images/og/bmi-chart-women.png assets/images/og/
cp $B/files/assets/images/charts/bmi-chart-women.png assets/images/charts/
[ -f $B/files/research/impeccable-baseline/2026-10-15-cmb014-390x844.json ] && cp $B/files/research/impeccable-baseline/2026-10-15-cmb014-390x844.json research/impeccable-baseline/
python3 research/chart-women-build/gen_bcw.py $T research/chart-women-build/bcw_stats.json
python3 $B/patch_cmb014.py $T
cat $B/css_cmb014.css >> assets/css/styles.css
mkdir -p $B/template/blog/bmi-chart-women && cp blog/bmi-chart-women/index.html $B/template/blog/bmi-chart-women/index.html
sed -i "s/{TODAY}/$DAY/g" blog/bmi-chart-women/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/date_edits.json $DAY
python3 $B/pkgtools/apply_edits_local.py $T $B/head_edits.json $DAY
git status --short
