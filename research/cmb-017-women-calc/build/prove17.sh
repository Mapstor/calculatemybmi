#!/bin/bash
# Fresh-clone proof of the CMB-017 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove17.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-017-women-calc.zip
PG=women-bmi-calculator/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-017-women-calc.zip research/ && rm research/cmb-017-women-calc.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-016')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-017-women-calc/apply_build.py --dry-run
python3 research/cmb-017-women-calc/apply_build.py
T=${DAY:-$(date +%F)}
rm -f /workspace && ln -s $D /workspace
echo "3.1 $(python3 scripts/check_structure.py)"
echo "3.2 $(python3 research/f1/verify.py)"
node --check assets/js/calculator.js && echo "3.3 0"
echo "3.4 $(python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html | tail -1)"
echo "3.5 $(python3 research/tech-cleanup-checks/schema_check.py)"
echo "3.6 $(python3 scripts/check_markup.py $PG)"
python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo "3.7 $?"
python3 scripts/check_weight_tables.py $PG; echo "3.8 $?"
echo "3.9 $(python3 scripts/check_images.py . | tail -1)"
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "women-bmi-calculator/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style' $PG | wc -l) $(grep -o 'women-acog-pregnancy-ranges' $PG | wc -l) $(ls assets/images/og/ | grep -c women-acog) $(ls assets/images/preferred/ | wc -l) $(grep -o "'/women-bmi-calculator/': 'women-bmi-calculator'" scripts/check_images.py | wc -l) $(grep -o 'form-row--pair' assets/css/styles.css | wc -l) $(grep -o 'for="women-' $PG | wc -l) $(grep -o 'id="women-waist-in"' $PG | wc -l) $(grep -o 'lowest mortality\|lowest all-cause mortality' $PG | wc -l) $($CS | grep -c "page 'women-bmi-calculator'") $($CS | grep -c '^FAIL')"
echo "3.11 $(python3 research/women-calc-build/wbc_stats.py research/average-weight/raw research/home-build/home_stats.json research/average-weight/avgw_results.json research/chart-women-build/bcw_stats.json /tmp/wbc_check.json > /dev/null && cmp /tmp/wbc_check.json research/women-calc-build/wbc_stats.json && echo same; rm -f /tmp/wbc_check.json)"
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /women-bmi-calculator/ rebuilt to the D-14 pattern (CMB-017) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb017-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb017-dates.txt)/40"; grep '^BAD' /tmp/cmb017-dates.txt || true; rm -f /tmp/cmb017-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c17 /workspace    # gates in chat run against the work tree again
