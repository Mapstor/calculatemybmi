#!/bin/bash
# Fresh-clone proof of the CMB-018 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove18.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-018-chart-men.zip
PG=blog/bmi-chart-men/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-018-chart-men.zip research/ && rm research/cmb-018-chart-men.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-017')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-018-chart-men/apply_build.py --dry-run
python3 research/cmb-018-chart-men/apply_build.py
T=${DAY:-$(date +%F)}
rm -f /workspace && ln -s $D /workspace
echo "3.1 $(python3 scripts/check_structure.py)"
echo "3.2 $(python3 research/f1/verify.py)"
node --check assets/js/calculator.js && echo "3.3 0"
echo "3.4 $(python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html | tail -1)"
echo "3.5 $(python3 research/tech-cleanup-checks/schema_check.py)"
echo "3.6 $(python3 scripts/check_markup.py $PG bmi-chart/index.html | tr '\n' ' ')"
python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo "3.7 $?"
python3 scripts/check_weight_tables.py $PG bmi-chart/index.html; echo "3.8 $?"
echo "3.9 $(python3 scripts/check_images.py . | tail -1)"
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "blog/bmi-chart-men/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o '<image:loc>https://calculatemybmi.net/assets/images/charts/bmi-chart-men.png</image:loc>' sitemap.xml | wc -l) $(grep -o "\"dateModified\": \"$T\"" $PG | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style' $PG | wc -l) $(grep -o 'application/ld+json' $PG | wc -l) $(grep -o 'id="h-' $PG | wc -l) $(grep -o 'max-image-preview:large' $PG | wc -l) $(ls assets/images/preferred/ | wc -l) $(grep -o "'/blog/bmi-chart-men/': 'bmi-chart-men'" scripts/check_images.py | wc -l) $(grep -c 'Distributions over the chart (CMB-018)' DESIGN.md) $(grep -o '90 cm (35.5 in)' bmi-chart/index.html | wc -l) $(grep -o "\"dateModified\": \"$T\"" bmi-chart/index.html | wc -l) $(grep -o "net/bmi-chart/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $($CS | grep -c "page 'blog/bmi-chart-men'") $($CS | grep -c '^FAIL')"
echo "3.11 $(python3 research/chart-men-build/bcm_stats.py research/average-weight/raw research/healthy-range-build/healthy_stats.json research/bmi-chart-build/bc_stats.json research/average-weight/avgw_results.json /tmp/bcm_check.json > /dev/null && cmp /tmp/bcm_check.json research/chart-men-build/bcm_stats.json && echo same; rm -f /tmp/bcm_check.json)"
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /blog/bmi-chart-men/ rebuilt to the D-14 pattern (CMB-018) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb018-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb018-dates.txt)/40"; grep '^BAD' /tmp/cmb018-dates.txt || true; rm -f /tmp/cmb018-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c18 /workspace    # gates in chat run against the work tree again
