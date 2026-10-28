#!/bin/bash
# Package CMB-019 from the scratch tree: mkpkg (hash-guarded), then both pages as their {TODAY} templates ("today": true),
# and sitemap.xml as edits ({TODAY} lastmod for both pages), not a replacement.
set -e
T=/home/claude/c19; B=/home/claude/build/cmb019; P=/home/claude/build/pkg/cmb-019-average-weight
if [ -z "$PKG_DRAFT" ] && grep -l '<<[A-Z-]*>>' $B/FIX.md $B/files/research/average-weight-build/SPEC.md; then echo 'unfilled marker: not packaging'; exit 1; fi
$B/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil, hashlib
B='/home/claude/build/cmb019'; P='/home/claude/build/pkg/cmb-019-average-weight'
M=json.load(open(P+'/manifest.json'))
E=json.load(open(B+'/edits.json'))
EDITED=sorted(set(e['file'] for e in E))                                       # these change through edits, not replacements
assert EDITED==['sitemap.xml'], EDITED
M['replace']=[r for r in M['replace'] if r['path'] not in EDITED]
for f in EDITED: os.remove(os.path.join(P,'files',f))
M['edits']=E
TODAY={'average-weight/index.html': 2, 'blog/bmi-chart-men/index.html': 1}    # each ships as its {TODAY} template
for page, n in TODAY.items():
    shutil.copy(os.path.join(B,'template',page),os.path.join(P,'files',page))
    assert open(os.path.join(P,'files',page),encoding='utf-8').read().count('{TODAY}')==n, page
    for r in M['replace']:
        if r['path']==page:
            r['sha256']=hashlib.sha256(open(os.path.join(P,'files',page),'rb').read()).hexdigest(); r['today']=True
assert sorted(r['path'] for r in M['replace'] if r.get('today'))==sorted(TODAY)
assert [d['path'] for d in M['delete']]==['average-weight/og-average-weight.png'], M['delete']
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb019.py','edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb019.sh','prove19.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits,',len(M['delete']),'delete')
PY
cd /home/claude/build/pkg && rm -f cmb-019-average-weight.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-019-average-weight.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-019-average-weight'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-019-average-weight.zip | cut -c1-16; ls -la cmb-019-average-weight.zip
