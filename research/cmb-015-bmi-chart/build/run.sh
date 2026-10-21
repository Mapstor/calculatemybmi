#!/bin/bash
# Reset the scratch tree to GitHub main (621bf8b) and rebuild CMB-015 from scratch.
# Images come from files/ (rendered once by chart_bc.py / pref_images.py); the page is generated with {TODAY}, a copy
# goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=/home/claude/c15; B=/home/claude/build/cmb015; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/bmi-chart-build research/preferred-images assets/images/charts assets/images/preferred
cp $B/files/research/bmi-chart-build/* research/bmi-chart-build/
cp $B/files/research/preferred-images/* research/preferred-images/
cp $B/files/scripts/check_images.py scripts/
cp $B/files/assets/images/charts/bmi-chart.png assets/images/charts/
cp $B/files/assets/images/preferred/*.png assets/images/preferred/
[ -d $B/files/research/impeccable-baseline ] && cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/
python3 research/bmi-chart-build/gen_bc.py $T research/bmi-chart-build/bc_stats.json
python3 $B/patch_cmb015.py $T
mkdir -p $B/template/bmi-chart && cp bmi-chart/index.html $B/template/bmi-chart/index.html
sed -i "s/{TODAY}/$DAY/g" bmi-chart/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
rm assets/images/og/home-bmi-us-adults.png assets/images/og/healthy-bmi-range-risk.png assets/images/og/bmi-chart-women.png
git status --short | awk '{print $1}' | sort | uniq -c
