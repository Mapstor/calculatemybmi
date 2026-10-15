#!/bin/bash
# Reset the scratch tree to GitHub main (192fb02) and rebuild CMB-013 from scratch.
# The page is generated with {TODAY}; a copy goes to template/ for the package, and the work tree gets DAY for local gates.
set -e
T=/home/claude/c13; B=/home/claude/build/cmb013; DAY=${1:-2026-10-15}
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/healthy-range-build assets/images/og
cp $B/files/research/healthy-range-build/{healthy_stats.py,healthy_stats.json,gen_hbr.py,og_hbr.py,hbr_test_playwright.py,SPEC.md} research/healthy-range-build/
cp $B/files/assets/images/og/healthy-bmi-range-risk.png assets/images/og/
[ -f $B/files/research/impeccable-baseline/2026-10-15-cmb013-390x844.json ] && cp $B/files/research/impeccable-baseline/2026-10-15-cmb013-390x844.json research/impeccable-baseline/
rm assets/images/og/healthy-bmi-envelope.png
python3 research/healthy-range-build/gen_hbr.py $T research/healthy-range-build/healthy_stats.json
python3 $B/patch_cmb013.py $T
cat $B/css_cmb013.css >> assets/css/styles.css
mkdir -p $B/template/blog/healthy-bmi-range && cp blog/healthy-bmi-range/index.html $B/template/blog/healthy-bmi-range/index.html
sed -i "s/{TODAY}/$DAY/g" blog/healthy-bmi-range/index.html
python3 $B/pkgtools/apply_edits_local.py $T $B/date_edits.json $DAY
git status --short
