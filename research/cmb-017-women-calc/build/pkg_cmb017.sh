#!/bin/bash
# Package CMB-017 from the scratch tree: mkpkg (hash-guarded); sitemap.xml as an edit ({TODAY} lastmod), not a replacement.
set -e
T=/home/claude/c17; B=/home/claude/build/cmb017; P=/home/claude/build/pkg/cmb-017-women-calc
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/women-calc-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil
B='/home/claude/build/cmb017'; P='/home/claude/build/pkg/cmb-017-women-calc'
M=json.load(open(P+'/manifest.json'))
E=json.load(open(B+'/edits.json'))
EDITED=sorted(set(e['file'] for e in E))
assert EDITED==['sitemap.xml'], EDITED
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=E
assert not any(r.get('today') for r in M['replace']+M['new_files'])
assert '{TODAY}' not in open(os.path.join(P,'files','women-bmi-calculator/index.html'),encoding='utf-8').read()
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb017.py','css_cmb017.css','edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb017.sh','prove17.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
PY
cd /home/claude/build/pkg && rm -f cmb-017-women-calc.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-017-women-calc.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-017-women-calc'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-017-women-calc.zip | cut -c1-16; ls -la cmb-017-women-calc.zip
