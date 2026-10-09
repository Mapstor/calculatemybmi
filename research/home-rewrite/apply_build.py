#!/usr/bin/env python3
"""apply_build.py — batch G2c: homepage content (calculatemybmi). Run from the repo root:
python3 research/home-rewrite/apply_build.py [--dry-run]
Validates everything first (new files must not exist; replaced and deleted files must match the expected SHA-256 of the
pre-batch version; every edit's old string must occur exactly once). If anything fails, nothing is written."""
import json,os,sys,hashlib,shutil
HERE=os.path.dirname(os.path.abspath(__file__)); M=json.load(open(os.path.join(HERE,"manifest.json"),encoding="utf-8"))
dry="--dry-run" in sys.argv; sha=lambda p:hashlib.sha256(open(p,"rb").read()).hexdigest(); bad=[]
for n in M["new_files"]:
    if os.path.exists(n["path"]): bad.append("exists already: "+n["path"])
    if sha(os.path.join(HERE,"files",n["path"]))!=n["sha256"]: bad.append("package file corrupted: "+n["path"])
for r in M["replace"]:
    if not os.path.exists(r["path"]): bad.append("missing: "+r["path"])
    elif sha(r["path"])!=r["expect_sha256"]: bad.append("changed since the package was built: "+r["path"])
for d in M.get("delete",[]):
    if not os.path.exists(d["path"]): bad.append("missing (to delete): "+d["path"])
    elif sha(d["path"])!=d["expect_sha256"]: bad.append("changed since the package was built (to delete): "+d["path"])
work={}
for e in M["edits"]:
    if e["file"] not in work:
        if not os.path.exists(e["file"]): bad.append("missing: "+e["file"]); continue
        work[e["file"]]=open(e["file"],encoding="utf-8",newline="").read()
    c=work[e["file"]].count(e["old"])
    if c!=e["count"]: bad.append(f'{e["label"]}: expected {e["count"]} found {c}'); continue
    work[e["file"]]=work[e["file"]].replace(e["old"],e["new"])
if bad: print("ABORT — nothing written:"); print("\n".join(bad)); sys.exit(1)
if not dry:
    for n in M["new_files"]:
        os.makedirs(os.path.dirname(n["path"]) or ".",exist_ok=True); shutil.copy(os.path.join(HERE,"files",n["path"]),n["path"])
    for r in M["replace"]: shutil.copy(os.path.join(HERE,"files",r["path"]),r["path"])
    for f,t in work.items(): open(f,"w",encoding="utf-8",newline="").write(t)
    for d in M.get("delete",[]): os.remove(d["path"])
print(("DRY RUN — " if dry else "")+f'applied: {len(M["new_files"])} new files, {len(M["replace"])} replaced files, {len(M["edits"])} edits, {len(M.get("delete",[]))} deletions')
