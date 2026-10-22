#!/bin/bash
# Reset the scratch tree to GitHub main (9bf7429) and rebuild CMB-017 from scratch.
# Images come from files/ (rendered once by pref_images.py); the page has no schema dateModified, so it ships as a plain
# replacement; the sitemap lastmod is a {TODAY} edit (DAY here for local gates).
set -e
T=/home/claude/c17; B=/home/claude/build/cmb017; DAY=${1:-$(date +%F)}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/women-calc-build assets/images/preferred
cp $B/files/research/women-calc-build/* research/women-calc-build/
cp $B/files/research/preferred-images/pref_images.py research/preferred-images/
cp $B/files/assets/images/preferred/women-bmi-calculator-*.png assets/images/preferred/
if [ -d $B/files/research/impeccable-baseline ]; then cp $B/files/research/impeccable-baseline/* research/impeccable-baseline/; fi
python3 research/women-calc-build/gen_wbc.py $T research/women-calc-build/wbc_stats.json
python3 $B/patch_cmb017.py $T
if [ -s $B/css_cmb017.css ]; then cat $B/css_cmb017.css >> assets/css/styles.css; fi
python3 $B/pkgtools/apply_edits_local.py $T $B/edits.json $DAY
rm assets/images/og/women-acog-pregnancy-ranges.png
git status --short | awk '{print $1}' | sort | uniq -c
