#!/bin/bash
# Fresh-clone proof of the CMB-015 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove15.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-015-bmi-chart.zip
PG=bmi-chart/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-015-bmi-chart.zip research/ && rm research/cmb-015-bmi-chart.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-014')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-015-bmi-chart/apply_build.py --dry-run
python3 research/cmb-015-bmi-chart/apply_build.py
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
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "\"dateModified\": \"$T\"" $PG | wc -l) $(grep -o "<lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style>' $PG | wc -l) $(grep -o 'og-image.png' $PG | wc -l) $(grep -o "4'10'" $PG | wc -l) $(ls assets/images/preferred/ | wc -l) $(grep -o '<image:image>' sitemap.xml | wc -l) $(ls assets/images/og/ | grep -c 'home-bmi-us-adults.png\|healthy-bmi-range-risk.png\|bmi-chart-women.png') $(grep -o '.data-table .th-sub' assets/css/styles.css | wc -l) $($CS | grep -c "page 'bmi-chart'") $($CS | grep -c '^FAIL')"
python3 research/bmi-chart-build/bc_stats.py research/average-weight/raw research/healthy-range-build/healthy_stats.json research/chart-women-build/bcw_stats.json /tmp/cmb015-stats.json >/dev/null && cmp /tmp/cmb015-stats.json research/bmi-chart-build/bc_stats.json && echo "3.11 same"; rm -f /tmp/cmb015-stats.json
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /bmi-chart/ rebuilt to the D-14 pattern (CMB-015) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb015-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb015-dates.txt)/40"; grep '^BAD' /tmp/cmb015-dates.txt || true; rm -f /tmp/cmb015-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c15 /workspace    # gates in chat run against the work tree again
