#!/bin/bash
# Package CMB-013 from the scratch tree: mkpkg (hash-guarded), then the page as its {TODAY} template ("today": true)
# and the sitemap lastmod as a {TODAY} edit.
set -e
T=/home/claude/c13; B=/home/claude/build/cmb013; P=/home/claude/build/pkg/cmb-013-healthy-range
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/healthy-range-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb013'; P='/home/claude/build/pkg/cmb-013-healthy-range'
M=json.load(open(P+'/manifest.json'))
M['replace']=[r for r in M['replace'] if r['path']!='sitemap.xml']          # sitemap changes through a {TODAY} edit
os.remove(os.path.join(P,'files','sitemap.xml'))
M['edits']=json.load(open(B+'/date_edits.json'))
page='blog/healthy-bmi-range/index.html'                                      # ships as its {TODAY} template
shutil.copy(os.path.join(B,'template',page),os.path.join(P,'files',page))
for r in M['replace']:
    if r['path']==page:
        r['sha256']=hashlib.sha256(open(os.path.join(P,'files',page),'rb').read()).hexdigest(); r['today']=True
assert sum(1 for r in M['replace'] if r.get('today'))==1
assert open(os.path.join(P,'files',page),encoding='utf-8').read().count('{TODAY}')==2
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb013.py','css_cmb013.css','date_edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb013.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
PY
cd /home/claude/build/pkg && rm -f cmb-013-healthy-range.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-013-healthy-range.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-013-healthy-range'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-013-healthy-range.zip | cut -c1-16; ls -la cmb-013-healthy-range.zip
