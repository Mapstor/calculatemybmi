#!/bin/bash
# Package CMB-018 from the scratch tree: mkpkg (hash-guarded), then the page as its {TODAY} template ("today": true),
# and sitemap.xml as an edit ({TODAY} lastmod plus the image entry), not a replacement.
set -e
T=/home/claude/c18; B=/home/claude/build/cmb018; P=/home/claude/build/pkg/cmb-018-chart-men
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/chart-men-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb018'; P='/home/claude/build/pkg/cmb-018-chart-men'
M=json.load(open(P+'/manifest.json'))
E=json.load(open(B+'/edits.json'))
EDITED=sorted(set(e['file'] for e in E))                                       # these change through edits, not replacements
assert EDITED==['bmi-chart/index.html','research/bmi-chart-build/gen_bc.py','sitemap.xml'], EDITED
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=E
page='blog/bmi-chart-men/index.html'                                           # ships as its {TODAY} template
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
for f in ('patch_cmb018.py','edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb018.sh','prove18.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
PY
cd /home/claude/build/pkg && rm -f cmb-018-chart-men.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-018-chart-men.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-018-chart-men'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-018-chart-men.zip | cut -c1-16; ls -la cmb-018-chart-men.zip
