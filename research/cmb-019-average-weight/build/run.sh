#!/bin/bash
# Reset the scratch tree to GitHub main (56acc27) and rebuild CMB-019 from scratch.
# Both pages are generated with {TODAY}; copies go to template/ for the package, and the work tree gets DAY for local gates.
# The men's chart is regenerated from its CMB-017 source (dcd6b47), the page gen_bcm.py was written against, with the
# rerun bcm_stats.json (NCHS's lb factor and percentile method: the 5'10" median moves from 199.3 to 199.1 lb).
set -e
T=/home/claude/c19; B=/home/claude/build/cmb019; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/average-weight-build assets/images/preferred
cp $B/files/research/average-weight/compute.py $B/files/research/average-weight/avgw_results.json research/average-weight/
cp $B/files/research/average-weight-build/* research/average-weight-build/
cp $B/files/research/chart-men-build/* research/chart-men-build/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
if ls $B/files/assets/images/preferred/*.png > /dev/null 2>&1; then cp $B/files/assets/images/preferred/*.png assets/images/preferred/; fi
if [ -d $B/files/research/impeccable-baseline ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 $B/patch_cmb019.py $T
python3 research/average-weight-build/gen_aw.py $T
git show dcd6b47:blog/bmi-chart-men/index.html > blog/bmi-chart-men/index.html
python3 research/chart-men-build/gen_bcm.py $T research/chart-men-build/bcm_stats.json research/chart-men-build/bcm_dxa.json
rm average-weight/og-average-weight.png
for pg in average-weight/index.html blog/bmi-chart-men/index.html; do
  mkdir -p $B/template/$(dirname $pg) && cp $pg $B/template/$pg
done
sed -i "s/{TODAY}/$DAY/g" average-weight/index.html blog/bmi-chart-men/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
git status --short | awk '{print $1}' | sort | uniq -c
