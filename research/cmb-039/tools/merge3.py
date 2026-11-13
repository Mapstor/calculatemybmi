#!/usr/bin/env python3
"""3-way merge at tag-end segments: BASE (generator output, old stats), NEW (generator output, new stats), LIVE (the
page in the repo). Applies every BASE->NEW change to LIVE where LIVE still holds BASE's segments; reports the rest.
usage: merge3.py BASE NEW LIVE OUT"""
import sys, re, difflib
sp = lambda s: re.split(r'(?<=>)', s)
A, B, L = (sp(open(p, encoding='utf-8').read()) for p in sys.argv[1:4])
amap = {}
for blk in difflib.SequenceMatcher(None, A, L, autojunk=False).get_matching_blocks():
    for k in range(blk.size): amap[blk.a + k] = blk.b + k
out = list(L); edits = []; conflicts = []
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
    if tag == 'equal': continue
    if i2 > i1:
        idx = [amap.get(i) for i in range(i1, i2)]
        if None in idx or idx != list(range(idx[0], idx[0] + len(idx))):
            conflicts.append((i1, ''.join(A[i1:i2])[:200], ''.join(B[j1:j2])[:200])); continue
        edits.append((idx[0], idx[-1] + 1, B[j1:j2]))
    else:
        anchor = amap.get(i1 - 1)
        if anchor is None: conflicts.append((i1, '(insert)', ''.join(B[j1:j2])[:200])); continue
        edits.append((anchor + 1, anchor + 1, B[j1:j2]))
for l1, l2, seg in sorted(edits, reverse=True):
    out[l1:l2] = seg
open(sys.argv[4], 'w', encoding='utf-8', newline='').write(''.join(out))
print('applied', len(edits), 'conflicts', len(conflicts))
for c in conflicts: print('CONFLICT at base seg', c[0], '\n   base:', c[1], '\n   new: ', c[2])
