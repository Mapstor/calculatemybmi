import json,os,sys,hashlib,shutil,datetime,re
HERE=os.path.dirname(os.path.abspath(__file__)); M=json.load(open(os.path.join(HERE,"manifest.json"),encoding="utf-8"))
dry="--dry-run" in sys.argv; sha=lambda p:hashlib.sha256(open(p,"rb").read()).hexdigest(); bad=[]
# {TODAY} becomes the apply date (the box's local date, the same clock git commits with), so page dates (sitemap lastmod,
# schema dateModified) equal the commit date whatever day the batch runs: in an edit's new text (CMB-012), and in a new or
# replaced file whose manifest entry says "today": true (CMB-013). Hashes are of the package copy, which keeps {TODAY}.
TODAY=os.environ.get("CMB_TODAY") or datetime.date.today().isoformat()
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",TODAY): bad.append("bad date: "+TODAY)
for n in M["new_files"]:
    if os.path.exists(n["path"]): bad.append("exists already: "+n["path"])
    if sha(os.path.join(HERE,"files",n["path"]))!=n["sha256"]: bad.append("package file corrupted: "+n["path"])
for r in M["replace"]:
    if not os.path.exists(r["path"]): bad.append("missing: "+r["path"])
    elif sha(r["path"])!=r["expect_sha256"]: bad.append("changed since the package was built: "+r["path"])
    if sha(os.path.join(HERE,"files",r["path"]))!=r["sha256"]: bad.append("package file corrupted: "+r["path"])
for x in M["new_files"]+M["replace"]:
    if x.get("today") and "{TODAY}" not in open(os.path.join(HERE,"files",x["path"]),encoding="utf-8").read(): bad.append("no {TODAY} in "+x["path"])
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
    work[e["file"]]=work[e["file"]].replace(e["old"],e["new"].replace("{TODAY}",TODAY))
if bad: print("ABORT — nothing written:"); print("\n".join(bad)); sys.exit(1)
def put(x):
    src=os.path.join(HERE,"files",x["path"])
    if x.get("today"):
        open(x["path"],"w",encoding="utf-8",newline="").write(open(src,encoding="utf-8",newline="").read().replace("{TODAY}",TODAY))
    else: shutil.copy(src,x["path"])
if not dry:
    for n in M["new_files"]:
        os.makedirs(os.path.dirname(n["path"]) or ".",exist_ok=True); put(n)
    for r in M["replace"]: put(r)
    for f,t in work.items(): open(f,"w",encoding="utf-8",newline="").write(t)
    for d in M.get("delete",[]): os.remove(d["path"])
print(("DRY RUN — " if dry else "")+f'applied: {len(M["new_files"])} new files, {len(M["replace"])} replaced files, {len(M["edits"])} edits, {len(M.get("delete",[]))} deletions')
