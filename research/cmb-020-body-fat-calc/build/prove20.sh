#!/bin/bash
# Fresh-clone proof of the CMB-020 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove20.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-020-body-fat-calc.zip
PG=body-fat-calculator/index.html; CH=body-fat-percentage-chart/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-020-body-fat-calc.zip research/ && rm research/cmb-020-body-fat-calc.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-019')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-020-body-fat-calc/apply_build.py --dry-run
python3 research/cmb-020-body-fat-calc/apply_build.py
T=${DAY:-$(date +%F)}
rm -f /workspace && ln -s $D /workspace
echo "3.1 $(python3 scripts/check_structure.py)"
echo "3.2 $(python3 research/f1/verify.py)"
node --check assets/js/calculator.js && echo "3.3 0"
echo "3.4 $(python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html | tail -1)"
echo "3.5 $(python3 research/tech-cleanup-checks/schema_check.py)"
echo "3.6 $(python3 scripts/check_markup.py $PG $CH | tr '\n' ' ')"
python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo "3.7 $?"
python3 scripts/check_weight_tables.py $PG $CH; echo "3.8 $?"
echo "3.9 $(python3 scripts/check_images.py . | tail -1)"
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "net/body-fat-calculator/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o "\"dateModified\": \"$T\"" $PG | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style' $PG | wc -l) $(grep -o '<article' $PG | wc -l) $(grep -o 'application/ld+json' $PG | wc -l) $(grep -o 'max-image-preview:large' $PG | wc -l) $(grep -o 'window.BFC=' $PG | wc -l) $(grep -o 'href="/body-fat-calculator/" class="active" aria-current="page"' $PG | wc -l) $(grep -o 'aria-current="page"' $PG | wc -l) $(ls assets/images/preferred/ | wc -l) $(ls body-fat-calculator/og-body-fat-calculator.png 2>/dev/null | wc -l) $(grep -o "'/body-fat-calculator/': 'body-fat-calculator'" scripts/check_images.py | wc -l) $(grep -c 'Body fat calculator (CMB-020)' DESIGN.md) $(grep -c '\.bfc \[hidden\]' assets/css/styles.css) $(grep -o "viewBox=\"0 0 '+W+' 88\"" $CH | wc -l) $(grep -c "viewBox=\"0 0 '+W+' 88\"" research/body-fat-chart-build/gen_bfpc.py) $(grep -c '^rfm-woolcott-2018,\|^foulis-2023-circumference-dxa,\|^army-tape-worksheets,' research/data-sources.csv) $($CS | grep -c "page 'body-fat-calculator'") $($CS | grep -c '^FAIL')"
echo "3.11 $(python3 -c 'import pandas' 2>/dev/null && echo 'pandas here, raw DXA files not in repo' || echo 'skipped (raw DXA files not in repo)')"
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /body-fat-calculator/ rebuilt to the D-14 pattern (CMB-020) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb020-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb020-dates.txt)/40"; grep '^BAD' /tmp/cmb020-dates.txt || true; rm -f /tmp/cmb020-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c20 /workspace    # gates in chat run against the work tree again
