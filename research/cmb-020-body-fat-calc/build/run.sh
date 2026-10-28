#!/bin/bash
# Reset the scratch tree to GitHub main (f365b8b) and rebuild CMB-020 from scratch.
# The page is generated with {TODAY}; a copy goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=/home/claude/c20; B=/home/claude/build/cmb020; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/body-fat-calculator-build assets/images/preferred
cp $B/files/research/body-fat-calculator-build/* research/body-fat-calculator-build/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
if ls $B/files/assets/images/preferred/*.png > /dev/null 2>&1; then cp $B/files/assets/images/preferred/*.png assets/images/preferred/; fi
if [ -n "$(ls $B/files/research/impeccable-baseline/ 2>/dev/null)" ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 $B/patch_cmb020.py $T
python3 research/body-fat-calculator-build/gen_bfcalc.py $T research/body-fat-calculator-build/bfc_stats.json
rm body-fat-calculator/og-body-fat-calculator.png
mkdir -p $B/template/body-fat-calculator && cp body-fat-calculator/index.html $B/template/body-fat-calculator/index.html
sed -i "s/{TODAY}/$DAY/g" body-fat-calculator/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
git status --short | awk '{print $1}' | sort | uniq -c
