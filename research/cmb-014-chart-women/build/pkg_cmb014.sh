#!/bin/bash
# Package CMB-014 from the scratch tree: mkpkg (hash-guarded), then the page as its {TODAY} template ("today": true)
# and the sitemap lastmod as a {TODAY} edit.
set -e
T=/home/claude/c14; B=/home/claude/build/cmb014; P=/home/claude/build/pkg/cmb-014-chart-women
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/chart-women-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb014'; P='/home/claude/build/pkg/cmb-014-chart-women'
M=json.load(open(P+'/manifest.json'))
EDITED=('sitemap.xml','bmi-chart/index.html','blog/bmi-chart-men/index.html')   # these change through edits, not replacements
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=json.load(open(B+'/date_edits.json'))+json.load(open(B+'/head_edits.json'))   # sitemap date + 6 head-tag fixes
page='blog/bmi-chart-women/index.html'                                        # ships as its {TODAY} template
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
for f in ('patch_cmb014.py','css_cmb014.css','date_edits.json','head_edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb014.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
PY
cd /home/claude/build/pkg && rm -f cmb-014-chart-women.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-014-chart-women.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-014-chart-women'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-014-chart-women.zip | cut -c1-16; ls -la cmb-014-chart-women.zip
