#!/usr/bin/env python3
"""Segment-level diff of two generated pages: splits at tag ends, prints each changed run (old -> new)."""
import sys, re, difflib
a = open(sys.argv[1], encoding='utf-8').read(); b = open(sys.argv[2], encoding='utf-8').read()
sp = lambda s: re.split(r'(?<=>)', s)
A, B = sp(a), sp(b)
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
n = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal': continue
    n += 1
    if len(sys.argv) > 3 and sys.argv[3] == 'count': continue
    o = ''.join(A[i1:i2]); w = ''.join(B[j1:j2])
    # trim common prefix/suffix inside the run for display
    p = 0
    while p < min(len(o), len(w)) and o[p] == w[p]: p += 1
    s = 0
    while s < min(len(o), len(w)) - p and o[-1 - s] == w[-1 - s]: s += 1
    ctx = 40
    print(f'#{n} [{tag} {i1}-{i2}] ...{o[max(0,p-ctx):p]}[[{o[p:len(o)-s]}]] -> [[{w[p:len(w)-s]}]]{o[len(o)-s:len(o)-s+25]}...')
print('runs', n)
