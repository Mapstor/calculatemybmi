#!/bin/bash
# Reset the scratch tree to GitHub main (be1ca97) and rebuild CMB-022 from scratch.
# The page is generated with {TODAY}; a copy goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=${CMB_TREE:-/home/claude/c22}; B=/home/claude/build/cmb022; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/us-obesity-statistics-build assets/images/preferred
cp $B/files/research/us-obesity-statistics-build/* research/us-obesity-statistics-build/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
cp $B/files/research/us-obesity-build/tools/* research/us-obesity-build/tools/
if ls $B/files/assets/images/preferred/*.png > /dev/null 2>&1; then cp $B/files/assets/images/preferred/*.png assets/images/preferred/; fi
if [ -n "$(ls $B/files/research/impeccable-baseline/ 2>/dev/null)" ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 $B/patch_cmb022.py $T
python3 research/us-obesity-statistics-build/gen_obs.py $T
rm us-obesity-statistics/og-us-obesity-statistics.png
mkdir -p $B/template/us-obesity-statistics && cp us-obesity-statistics/index.html $B/template/us-obesity-statistics/index.html
sed -i "s/{TODAY}/$DAY/g" us-obesity-statistics/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
git status --short | awk '{print $1}' | sort | uniq -c
