#!/bin/bash
# Reset the scratch tree to GitHub main and rebuild CMB-011 from scratch.
set -e
cd /home/claude/c11
git checkout -q -- . && git clean -qfd -e _snap
python3 /home/claude/build/cmb011/patch_cmb011.py /home/claude/c11 /home/claude/build/cmb011
# research extras: residue scanner, site-checks README, detector baseline
cp -r /home/claude/build/cmb011/extra/research/. /home/claude/c11/research/
