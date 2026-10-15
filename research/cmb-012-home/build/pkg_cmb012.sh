#!/bin/bash
# Package CMB-012 from the scratch tree: mkpkg (hash-guarded replacements), then the {TODAY} date edits.
set -e
T=/home/claude/c12; B=/home/claude/build/cmb012; P=/home/claude/build/pkg/cmb-012-home
/home/claude/build/cmb012/run.sh > /dev/null
python3 /home/claude/build/mkpkg.py $T $P
python3 - <<'PY'
import json, os, shutil
B='/home/claude/build/cmb012'; P='/home/claude/build/pkg/cmb-012-home'
M=json.load(open(P+'/manifest.json'))
dated={'sitemap.xml','blog/bmi-formula/index.html'}          # these change through {TODAY} edits, not full replacements
M['replace']=[r for r in M['replace'] if r['path'] not in dated]
for d in dated:
    f=os.path.join(P,'files',d)
    if os.path.exists(f): os.remove(f)
for d in ('files/blog/bmi-formula','files/blog'):
    try: os.rmdir(os.path.join(P,d))
    except OSError: pass
M['edits']=json.load(open(B+'/date_edits.json'))
json.dump(M,open(P+'/manifest.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
shutil.copy(B+'/pkgtools/apply_build.py',P+'/apply_build.py')
shutil.copy(B+'/FIX.md',P+'/FIX.md')
os.makedirs(P+'/build',exist_ok=True)
for f in ('patch_cmb012.py','css_home.css','date_edits.json','run.sh','pkgtools/apply_edits_local.py','pkg_cmb012.sh'):
    shutil.copy(os.path.join(B,f),os.path.join(P,'build',os.path.basename(f)))
print('manifest:',len(M['new_files']),'new,',len(M['replace']),'replace,',len(M['edits']),'edits')
PY
cd /home/claude/build/pkg && rm -f cmb-012-home.zip && python3 - <<'PY'
import zipfile, os
z=zipfile.ZipFile('cmb-012-home.zip','w',zipfile.ZIP_DEFLATED)
for root,dirs,files in os.walk('cmb-012-home'):
    for f in sorted(files): z.write(os.path.join(root,f))
z.close()
PY
sha256sum cmb-012-home.zip | cut -c1-16; ls -la cmb-012-home.zip
