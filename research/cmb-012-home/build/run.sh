#!/bin/bash
# Reset the scratch tree to GitHub main and rebuild CMB-012 from scratch.
set -e
T=/home/claude/c12; B=/home/claude/build/cmb012
cd $T
git checkout -q -- . && git clean -qfd -e _snap
mkdir -p research/home-build assets/images/og
cp $B/files/research/home-build/{home_stats.py,home_stats.json,gen_home.py,og_home.py,SPEC.md} research/home-build/
[ -f $B/files/research/home-build/home_test_playwright.py ] && cp $B/files/research/home-build/home_test_playwright.py research/home-build/
cp $B/files/assets/images/og/home-bmi-us-adults.png assets/images/og/
cp $B/files/research/impeccable-baseline/2026-10-14-cmb012-390x844.json research/impeccable-baseline/
python3 research/home-build/gen_home.py $T research/home-build/home_stats.json
python3 $B/patch_cmb012.py $T
cat $B/css_home.css >> assets/css/styles.css

python3 $B/pkgtools/apply_edits_local.py $T $B/date_edits.json 2026-10-14
git status --short
