#!/bin/bash
# Package CMB-020 from the scratch tree: mkpkg (hash-guarded), then the page as its {TODAY} template ("today": true),
# and sitemap.xml and /body-fat-percentage-chart/ as edits, not replacements.
set -e
T=/home/claude/c20; B=/home/claude/build/cmb020; P=/home/claude/build/pkg/cmb-020-body-fat-calc
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/body-fat-calculator-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb020'; P='/home/claude/build/pkg/cmb-020-body-fat-calc'
M=json.load(open(P+'/manifest.json'))
E=json.load(open(B+'/edits.json'))
EDITED=sorted(set(e['file'] for e in E))                                       # these change through edits, not replacements
assert EDITED==['body-fat-percentage-chart/index.html','sitemap.xml'], EDITED
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=E
TODAY={'body-fat-calculator/index.html': 1}                                     # ships as its {TODAY} template
for page, n in TODAY.items():
    shutil.copy(os.path.join(B,'template',page),os.path.join(P,'files',page))
    assert open(os.path.join(P,'files',page),encoding='utf-8').read().count('{TODAY}')==n, page
    for r in M['replace']:
        if r['path']==page:
            r['sha256']=hashlib.sha256(open(os.path.join(P,'files',page),'rb').read()).hexdigest(); r['today']=True
assert sorted(r['path'] for r in M['replace'] if r.get('today'))==sorted(TODAY)
assert [d['path'] for d in M['delete']]==['body-fat-calculator/og-body-fat-calculator.png'], M['delete']
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb020.py','edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb020.sh','prove20.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
print('new:', [n['path'] for n in M['new_files']]); print('replace:', [r['path'] for r in M['replace']])
PY
cd /home/claude/build/pkg && rm -f cmb-020-body-fat-calc.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-020-body-fat-calc.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-020-body-fat-calc'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-020-body-fat-calc.zip | cut -c1-16; ls -la cmb-020-body-fat-calc.zip
