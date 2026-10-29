#!/bin/bash
# Package CMB-021 from the scratch tree: mkpkg (hash-guarded), then the page as its {TODAY} template ("today": true),
# and sitemap.xml as an edit, not a replacement.
set -e
T=${CMB_TREE:-/home/claude/c21}; B=/home/claude/build/cmb021; P=/home/claude/build/pkg/cmb-021-how-to-measure
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/how-to-measure-body-fat-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb021'; P='/home/claude/build/pkg/cmb-021-how-to-measure'
M=json.load(open(P+'/manifest.json'))
E=json.load(open(B+'/edits.json'))
EDITED=sorted(set(e['file'] for e in E))                                       # these change through edits, not replacements
assert EDITED==['sitemap.xml'], EDITED
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=E
TODAY={'blog/how-to-measure-body-fat/index.html': 1}                           # ships as its {TODAY} template
for page, n in TODAY.items():
    shutil.copy(os.path.join(B,'template',page),os.path.join(P,'files',page))
    assert open(os.path.join(P,'files',page),encoding='utf-8').read().count('{TODAY}')==n, page
    for r in M['replace']:
        if r['path']==page:
            r['sha256']=hashlib.sha256(open(os.path.join(P,'files',page),'rb').read()).hexdigest(); r['today']=True
assert sorted(r['path'] for r in M['replace'] if r.get('today'))==sorted(TODAY)
assert [d['path'] for d in M['delete']]==['blog/how-to-measure-body-fat/og-how-to-measure-body-fat.png'], M['delete']
assert len(M['new_files'])==10 and len(M['replace'])==7, (len(M['new_files']), len(M['replace']))
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb021.py','edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb021.sh','prove21.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
print('new:', [n['path'] for n in M['new_files']]); print('replace:', [r['path'] for r in M['replace']])
PY
cd /home/claude/build/pkg && rm -f cmb-021-how-to-measure.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-021-how-to-measure.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-021-how-to-measure'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-021-how-to-measure.zip | cut -c1-16; ls -la cmb-021-how-to-measure.zip
