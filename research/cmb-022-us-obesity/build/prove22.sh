#!/bin/bash
# Fresh-clone proof of the CMB-022 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove22.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-022-us-obesity.zip
PG=us-obesity-statistics/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-022-us-obesity.zip research/ && rm research/cmb-022-us-obesity.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-021')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-022-us-obesity/apply_build.py --dry-run
python3 research/cmb-022-us-obesity/apply_build.py
T=${DAY:-$(date +%F)}
rm -f /workspace && ln -s $D /workspace
echo "3.1 $(python3 scripts/check_structure.py)"
echo "3.2 $(python3 research/f1/verify.py)"
node --check assets/js/calculator.js && echo "3.3 0"
echo "3.4 $(python3 research/us-obesity-build/tools/number_audit.py $PG | tail -1)"
echo "3.5 $(python3 research/tech-cleanup-checks/schema_check.py)"
echo "3.6 $(python3 scripts/check_markup.py $PG | tr '\n' ' ')"
python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo "3.7 $?"
python3 scripts/check_weight_tables.py $PG; echo "3.8 $?"
echo "3.9 $(python3 scripts/check_images.py . | tail -1)"
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "net/us-obesity-statistics/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o "\"dateModified\": \"$T\"" $PG | wc -l) $(grep -o '"datePublished": "2026-09-30"' $PG | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style' $PG | wc -l) $(grep -o '<article' $PG | wc -l) $(grep -o 'application/ld+json' $PG | wc -l) $(grep -o 'max-image-preview:large' $PG | wc -l) $(grep -o 'aria-current="page"' $PG | wc -l) $(grep -o 'data-table--wrap' $PG | wc -l) $(grep -o 'class="calculator-card obw"' $PG | wc -l) $(grep -o '"@type": "Dataset"' $PG | wc -l) $(ls assets/images/preferred/ | wc -l) $(ls us-obesity-statistics/og-us-obesity-statistics.png 2>/dev/null | wc -l) $(grep -o "'/us-obesity-statistics/': 'us-obesity-statistics'" scripts/check_images.py | wc -l) $(grep -c 'US obesity tool and embed code (CMB-022)' DESIGN.md) $(grep -c '\.obw \[hidden\]\|\.embed-code {\|button\.cta-button {' assets/css/styles.css) $(grep -c '^fourman-2025-all-of-us-new-definition,\|^alroub-2025-nhanes-new-definition,' research/data-sources.csv) $(grep -o 'us-obesity-trend-1960-2023.svg</image:loc>' sitemap.xml | wc -l) $(grep -c 'E0612D' us-obesity-statistics/us-obesity-trend-1960-2023.svg) $(grep -c ',underweight,4.0,0.2,age-adjusted,\|,underweight,1.7,0.3,age-adjusted,' us-obesity-statistics/us-obesity-data-nhanes-1960-2023.csv) $(grep -c 'measured (NHES, NHANES)' us-obesity-statistics/us-obesity-trend-1960-2023.svg) $($CS | grep -c "page 'us-obesity-statistics'") $($CS | grep -c '^FAIL')"
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /us-obesity-statistics/ rebuilt to the D-14 pattern (CMB-022) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb022-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb022-dates.txt)/40"; grep '^BAD' /tmp/cmb022-dates.txt || true; rm -f /tmp/cmb022-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c22 /workspace    # gates in chat run against the work tree again
