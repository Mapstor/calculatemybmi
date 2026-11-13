#!/usr/bin/env python3
"""Lists, character by character, every change between two pages and flags any that is not digits or a decimal point.
usage: digits_only.py BEFORE AFTER"""
import re, difflib, sys
a=open(sys.argv[1],encoding='utf-8').read(); b=open(sys.argv[2],encoding='utf-8').read()
bad=0; n=0
for t,i1,i2,j1,j2 in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
    if t=='equal': continue
    n+=1
    if not re.fullmatch(r'[\d.]*', a[i1:i2]) or not re.fullmatch(r'[\d.]*', b[j1:j2]): bad+=1; print('NON-DIGIT', repr(a[max(0,i1-40):i2+40]), '->', repr(b[j1:j2]))
print(sys.argv[1].split('/')[-2], 'char edits', n, 'non-digit', bad)
