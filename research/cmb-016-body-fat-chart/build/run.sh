#!/bin/bash
# Reset the scratch tree to GitHub main (0c418db) and rebuild CMB-016 from scratch.
# Images come from files/ (rendered once by chart_bfpc.py / pref_images.py); the page is generated with {TODAY}, a copy
# goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=/home/claude/c16; B=/home/claude/build/cmb016; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/body-fat-chart-build assets/images/charts assets/images/preferred
cp $B/files/research/body-fat-chart-build/* research/body-fat-chart-build/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
cp $B/files/assets/images/charts/body-fat-percentage-chart.png assets/images/charts/
cp $B/files/assets/images/preferred/body-fat-percentage-chart-*.png assets/images/preferred/
if [ -d $B/files/research/impeccable-baseline ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 research/body-fat-chart-build/gen_bfpc.py $T research/body-fat-chart-build/bfpc_stats.json
python3 $B/patch_cmb016.py $T
cat $B/css_cmb016.css >> assets/css/styles.css
mkdir -p $B/template/body-fat-percentage-chart && cp body-fat-percentage-chart/index.html $B/template/body-fat-percentage-chart/index.html
sed -i "s/{TODAY}/$DAY/g" body-fat-percentage-chart/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
rm body-fat-percentage-chart/og-body-fat-percentage-chart.png research/body-fat/tool_test_jsdom.js
git status --short | awk '{print $1}' | sort | uniq -c
