#!/usr/bin/env python3
"""apply_fixes.py — exact-string edits for calculatemybmi (batch C2b-1 (unsourced numbers, round 1)).
Run from the repo root:  python3 research/c2b1/apply_fixes.py [--dry-run]
Every edit is an exact old->new replacement with an expected occurrence count. All edits are validated in memory
first; if ANY count differs, nothing is written and the mismatches are printed (exit 1)."""
import json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
edits=json.load(open(os.path.join(HERE,"edits.json"),encoding="utf-8"))
dry="--dry-run" in sys.argv
files={}
for e in edits:
    if e["file"] not in files:
        if not os.path.exists(e["file"]): print("MISSING FILE:",e["file"]); sys.exit(1)
        files[e["file"]]=open(e["file"],encoding="utf-8",newline="").read()
bad=[]
work=dict(files)
for i,e in enumerate(edits):
    c=work[e["file"]].count(e["old"])
    if c!=e["count"]:
        bad.append(f'#{i} {e["label"]} :: {e["file"]} expected {e["count"]} found {c}')
        continue
    work[e["file"]]=work[e["file"]].replace(e["old"],e["new"])
if bad:
    print("ABORT — nothing written. Mismatches:"); print("\n".join(bad)); sys.exit(1)
changed=[f for f in work if work[f]!=files[f]]
if not dry:
    for f in changed:
        with open(f,"w",encoding="utf-8",newline="") as fh: fh.write(work[f])
from collections import Counter
print(("DRY RUN — " if dry else "")+f"applied {len(edits)} edits to {len(changed)} files")
for k,v in sorted(Counter(e["label"] for e in edits).items()): print(f"  {v:>3}  {k}")
