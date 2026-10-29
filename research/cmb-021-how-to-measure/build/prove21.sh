#!/bin/bash
# Fresh-clone proof of the CMB-021 package: GitHub main + the zip, FIX.md steps as the box runs them.
# usage: prove21.sh DIR [CMB_TODAY]   (DIR is wiped)
set -e
D=$1; DAY=${2:-}
ZIP=/home/claude/build/pkg/cmb-021-how-to-measure.zip
PG=blog/how-to-measure-body-fat/index.html
CS="python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv"
rm -rf $D && git clone -q https://github.com/Mapstor/calculatemybmi.git $D && cd $D
git log --oneline -1
cp $ZIP research/ && python3 -m zipfile -e research/cmb-021-how-to-measure.zip research/ && rm research/cmb-021-how-to-measure.zip
echo "0.1 $(git branch --show-current) | 0.2 $(git status --porcelain) | 0.3 $(git log --oneline -4 | grep -c 'CMB-020')"
if [ -n "$DAY" ]; then export CMB_TODAY=$DAY; fi
python3 research/cmb-021-how-to-measure/apply_build.py --dry-run
python3 research/cmb-021-how-to-measure/apply_build.py
T=${DAY:-$(date +%F)}
rm -f /workspace && ln -s $D /workspace
echo "3.1 $(python3 scripts/check_structure.py)"
echo "3.2 $(python3 research/f1/verify.py)"
node --check assets/js/calculator.js && echo "3.3 0"
echo "3.4 $(python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html | tail -1)"
echo "3.5 $(python3 research/tech-cleanup-checks/schema_check.py)"
echo "3.6 $(python3 scripts/check_markup.py $PG | tr '\n' ' ')"
python3 scripts/check_content_integrity.py index.html 404.html */index.html blog/*/index.html assets/js/calculator.js; echo "3.7 $?"
python3 scripts/check_weight_tables.py $PG; echo "3.8 $?"
echo "3.9 $(python3 scripts/check_images.py . | tail -1)"
echo "3.10 $(grep -o '{TODAY}' $PG | wc -l) $(grep -o "net/blog/how-to-measure-body-fat/</loc><lastmod>$T</lastmod>" sitemap.xml | wc -l) $(grep -o "\"dateModified\": \"$T\"" $PG | wc -l) $(grep -o '"datePublished": "2026-10-07"' $PG | wc -l) $(grep -o 'class="faq-question"' $PG | wc -l) $(grep -o '<style' $PG | wc -l) $(grep -o '<article' $PG | wc -l) $(grep -o 'application/ld+json' $PG | wc -l) $(grep -o 'max-image-preview:large' $PG | wc -l) $(grep -o 'href="/blog/" class="active" aria-current="page"' $PG | wc -l) $(grep -o 'aria-current="page"' $PG | wc -l) $(grep -o 'data-table--wrap' $PG | wc -l) $(ls assets/images/preferred/ | wc -l) $(ls blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png 2>/dev/null | wc -l) $(grep -o "'/blog/how-to-measure-body-fat/': 'how-to-measure-body-fat'" scripts/check_images.py | wc -l) $(grep -c 'Tables with long row labels (CMB-021)' DESIGN.md) $(grep -c 'data-table--wrap' assets/css/styles.css) $(grep -c '^frija-masson-2021-smart-scales,\|^lahav-2021-inbody-seca,\|^nhanes-bia-documentation,' research/data-sources.csv) $($CS | grep -c "page 'blog/how-to-measure-body-fat'") $($CS | grep -c '^FAIL')"
echo "3.11 $(python3 -c 'import pandas' 2>/dev/null && echo 'pandas here, raw DXA files not in repo' || echo 'skipped (raw DXA files not in repo)')"
git add -A
if [ -n "$DAY" ]; then export GIT_AUTHOR_DATE="${DAY}T12:00:00" GIT_COMMITTER_DATE="${DAY}T12:00:00"; fi
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "feat: /blog/how-to-measure-body-fat/ rebuilt to the D-14 pattern (CMB-021) [proof]"
git log --oneline -2
python3 research/dates/date_truth.py > /tmp/cmb021-dates.txt; echo "5 exit $? | ok $(grep -c '^ok' /tmp/cmb021-dates.txt)/40"; grep '^BAD' /tmp/cmb021-dates.txt || true; rm -f /tmp/cmb021-dates.txt
echo "final: $(git status --short | head -5 | tr '\n' ' ')$( [ -z "$(git status --short)" ] && echo clean) on $(git branch --show-current)"
rm -f /workspace && ln -s /home/claude/c21 /workspace    # gates in chat run against the work tree again
