#!/bin/bash
# Reset the scratch tree to GitHub main (dcd6b47) and rebuild CMB-018 from scratch.
# The page is generated with {TODAY}; a copy goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=/home/claude/c18; B=/home/claude/build/cmb018; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/chart-men-build assets/images/charts assets/images/preferred
cp $B/files/research/chart-men-build/* research/chart-men-build/
cp $B/files/assets/images/charts/bmi-chart-men.png assets/images/charts/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
cp $B/files/assets/images/preferred/bmi-chart-men-*.png assets/images/preferred/
if [ -d $B/files/research/impeccable-baseline ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 research/chart-men-build/gen_bcm.py $T research/chart-men-build/bcm_stats.json research/chart-men-build/bcm_dxa.json
python3 $B/patch_cmb018.py $T
mkdir -p $B/template/blog/bmi-chart-men && cp blog/bmi-chart-men/index.html $B/template/blog/bmi-chart-men/index.html
sed -i "s/{TODAY}/$DAY/g" blog/bmi-chart-men/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
git status --short | awk '{print $1}' | sort | uniq -c
