#!/usr/bin/env python3
"""merge_research.py — append-only merge of the us-obesity Tier-2 intake into the repo research files.
Run from the repo root:  python3 research/us-obesity-build/tools/merge_research.py
Rules (exact):
  page-map : slug absent -> append intake row; slug present -> unchanged, except us-obesity-statistics gets status=built and data_source=nhanes-adult-weight-trends.
  ledger   : keyword present (normalized) -> skip, never re-assign; report if the existing owner differs.
             keyword absent -> append. Role guard: a page never gets a 2nd primary (demote to secondary if the page has
             <5 secondaries, else tertiary); a page never gets a 6th secondary (demote to tertiary).
  registry : research/data-sources.csv absent -> create with header; domain present -> skip; absent -> append.
Existing rows are never edited or reordered (only the one status field above). Writes UTF-8, header order preserved.
"""
import csv, os, sys
from collections import defaultdict
PKG="research/us-obesity-build/research"
def norm(k): return " ".join(k.lower().split())
def read(path):
    with open(path,newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f); return r.fieldnames, list(r)
def eol(path):
    try:
        with open(path,"rb") as f: head=f.read(65536)
        return "\r\n" if b"\r\n" in head else "\n"
    except FileNotFoundError: return "\n"
def write(path,fields,rows):
    term=eol(path)  # preserve the file's existing line endings -> minimal git diff
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator=term); w.writeheader()
        for row in rows: w.writerow({k:row.get(k,"") for k in fields})
rep=[]
# ---------- page-map ----------
pm_f,pm=read("research/page-map.csv"); _,pm_in=read(f"{PKG}/pagemap-rows-us-obesity.csv")
slugs={r["slug"].strip():r for r in pm}
for r in pm_in:
    s=r["slug"].strip()
    if s in slugs:
        if s=="us-obesity-statistics":
            old=slugs[s].get("status",""); slugs[s]["status"]="built"; rep.append(f"page-map: {s} present -> status {old!r} -> 'built'")
            ods=slugs[s].get("data_source","")
            if ods!=r["data_source"]:
                slugs[s]["data_source"]=r["data_source"]; rep.append(f"page-map: {s} data_source {ods!r} -> {r['data_source']!r} (verified registry domain)")
        else: rep.append(f"page-map: {s} present -> unchanged")
    else:
        pm.append(r); slugs[s]=r; rep.append(f"page-map: {s} APPENDED (status {r['status']})")
write("research/page-map.csv",pm_f,pm)
# ---------- ledger ----------
lg_f,lg=read("research/keyword-ledger.csv"); _,lg_in=read(f"{PKG}/kwp-intake-us-obesity.csv")
have={norm(r["keyword"]):r for r in lg}
roles=defaultdict(lambda:defaultdict(int))
for r in lg:
    if r.get("role") in("primary","secondary") and r.get("page_slug"): roles[r["page_slug"].strip()][r["role"]]+=1
added=skipped=demoted=0; conflicts=[]
for r in lg_in:
    k=norm(r["keyword"])
    if k in have:
        skipped+=1; ex=have[k]
        if ex.get("page_slug","").strip()!=r["page_slug"].strip() or ex.get("role","")!=r["role"]:
            conflicts.append(f"  '{k}': ledger={ex.get('page_slug','') or '-'}/{ex.get('role','')}  intake={r['page_slug'] or '-'}/{r['role']}")
        continue
    s=r["page_slug"].strip(); role=r["role"]
    if role=="primary" and roles[s]["primary"]>=1:
        role="secondary" if roles[s]["secondary"]<5 else "tertiary"; demoted+=1
        r["notes"]=(r["notes"]+" | " if r["notes"] else "")+"demoted on merge: page already had a primary"
    if role=="secondary" and roles[s]["secondary"]>=5:
        role="tertiary"; demoted+=1
        r["notes"]=(r["notes"]+" | " if r["notes"] else "")+"demoted on merge: page already had 5 secondaries"
    r["role"]=role
    if role in("primary","secondary") and s: roles[s][role]+=1
    lg.append(r); have[k]=r; added+=1
write("research/keyword-ledger.csv",lg_f,lg)
rep.append(f"ledger: appended {added}, skipped (already owned) {skipped}, demoted {demoted}")
if conflicts: rep.append("ledger: existing owner differs from intake (kept existing):\n"+"\n".join(conflicts[:60])+(f"\n  ...+{len(conflicts)-60} more" if len(conflicts)>60 else ""))
# ---------- registry ----------
_,rg_in=read(f"{PKG}/data-sources-rows-us-obesity.csv"); rg_fields=list(rg_in[0].keys())
if os.path.exists("research/data-sources.csv"):
    rg_f,rg=read("research/data-sources.csv"); doms={r["domain"].strip() for r in rg}
    new=[r for r in rg_in if r["domain"].strip() not in doms]
    rep.append(f"registry: existed; appended {len(new)}, skipped {len(rg_in)-len(new)} (domain already present)")
    write("research/data-sources.csv",rg_f,rg+new)
else:
    write("research/data-sources.csv",rg_fields,rg_in); rep.append(f"registry: CREATED research/data-sources.csv with {len(rg_in)} rows")
print("\n".join(rep))
