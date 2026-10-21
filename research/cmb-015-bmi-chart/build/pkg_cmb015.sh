#!/bin/bash
# Package CMB-015 from the scratch tree: mkpkg (hash-guarded), then the page as its {TODAY} template ("today": true),
# and every file that edits.json touches (40 pages' head tags, three pages' JSON-LD, sitemap.xml) as edits, not replacements.
set -e
T=/home/claude/c15; B=/home/claude/build/cmb015; P=/home/claude/build/pkg/cmb-015-bmi-chart
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/bmi-chart-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb015'; P='/home/claude/build/pkg/cmb-015-bmi-chart'
M=json.load(open(P+'/manifest.json'))
E=json.load(open(B+'/edits.json'))
EDITED=sorted(set(e['file'] for e in E))                                       # these change through edits, not replacements
assert 'bmi-chart/index.html' not in EDITED and len(EDITED)==40, len(EDITED)
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=E
page='bmi-chart/index.html'                                                    # ships as its {TODAY} template
shutil.copy(os.path.join(B,'template',page),os.path.join(P,'files',page))
for r in M['replace']:
    if r['path']==page:
        r['sha256']=hashlib.sha256(open(os.path.join(P,'files',page),'rb').read()).hexdigest(); r['today']=True
assert sum(1 for r in M['replace'] if r.get('today'))==1
assert open(os.path.join(P,'files',page),encoding='utf-8').read().count('{TODAY}')==1
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb015.py','mk_edits_cmb015.py','edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb015.sh','prove15.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
PY
cd /home/claude/build/pkg && rm -f cmb-015-bmi-chart.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-015-bmi-chart.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-015-bmi-chart'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-015-bmi-chart.zip | cut -c1-16; ls -la cmb-015-bmi-chart.zip
