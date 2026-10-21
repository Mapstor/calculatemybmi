#!/bin/bash
# Fresh-clone proof of the CMB-016 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove16.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-016-body-fat-chart.zip
PG=body-fat-percentage-chart/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-016-body-fat-chart.zip research/ && rm research/cmb-016-body-fat-chart.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-015')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-016-body-fat-chart/apply_build.py --dry-run
python3 research/cmb-016-body-fat-chart/apply_build.py
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
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "\"dateModified\": \"$T\"" $PG | wc -l) $(grep -o "body-fat-percentage-chart/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style' $PG | wc -l) $(grep -o 'og-body-fat-percentage-chart.png' $PG | wc -l) $(ls body-fat-percentage-chart/ | wc -l) $(ls assets/images/preferred/ | wc -l) $(grep -o '<image:image>' sitemap.xml | wc -l) $(grep -o "'/body-fat-percentage-chart/': 'body-fat-percentage-chart'" scripts/check_images.py | wc -l) $(grep -o 'weight-chart--fit' assets/css/styles.css | wc -l) $(ls research/body-fat/ | grep -c tool_test_jsdom) $($CS | grep -c "page 'body-fat-percentage-chart'") $($CS | grep -c '^FAIL') $(grep -c 'to 28.3% in their 50s' age-bmi-calculator/index.html) $(grep -o "age-bmi-calculator/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l)"
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /body-fat-percentage-chart/ rebuilt to the D-14 pattern (CMB-016) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb016-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb016-dates.txt)/40"; grep '^BAD' /tmp/cmb016-dates.txt || true; rm -f /tmp/cmb016-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c16 /workspace    # gates in chat run against the work tree again
