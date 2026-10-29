#!/bin/bash
# Reset the scratch tree to GitHub main (7662c95) and rebuild CMB-021 from scratch.
# The page is generated with {TODAY}; a copy goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=${CMB_TREE:-/home/claude/c21}; B=/home/claude/build/cmb021; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/how-to-measure-body-fat-build assets/images/preferred
cp $B/files/research/how-to-measure-body-fat-build/* research/how-to-measure-body-fat-build/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
if ls $B/files/assets/images/preferred/*.png > /dev/null 2>&1; then cp $B/files/assets/images/preferred/*.png assets/images/preferred/; fi
if [ -n "$(ls $B/files/research/impeccable-baseline/ 2>/dev/null)" ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 $B/patch_cmb021.py $T
python3 research/how-to-measure-body-fat-build/gen_htm.py $T
rm blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png
mkdir -p $B/template/blog/how-to-measure-body-fat && cp blog/how-to-measure-body-fat/index.html $B/template/blog/how-to-measure-body-fat/index.html
sed -i "s/{TODAY}/$DAY/g" blog/how-to-measure-body-fat/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
git status --short | awk '{print $1}' | sort | uniq -c
