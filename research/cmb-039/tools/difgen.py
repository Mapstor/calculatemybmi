#!/usr/bin/env python3
"""Differential run of an old page generator (CMB-039). Old gen_*.py scripts rebuild a page from the page as it stood at
their base commit, so they must never run on the repo. In a scratch copy of the repo they show what a stats change moves:
base page + stats as at OLD_REV -> NAME_genA.html, base page + stats in the working tree -> NAME_genB.html. Then
merge3.py applies the A->B difference to the live page wherever the live page still holds the generator's text.
usage: STATS=rel1,rel2 [PATCH='old=>new;;...'] difgen.py REPO OLD_REV OUT_DIR NAME PAGE BASE_COMMIT GEN_SCRIPT [ARGS...]
  ARGS may use {ROOT} for the scratch copy. PATCH edits the scratch copy of the generator only (for example to print a
  2-decimal median at 1 decimal, or to print a number assert's value instead of stopping)."""
import sys, os, shutil, subprocess, tempfile

REPO, OLD_REV, OUT, name, page, base, gen, *args = sys.argv[1:]
STATS = [x for x in os.environ.get('STATS', '').split(',') if x]
SC = tempfile.mkdtemp(prefix=f'difgen_{name}_')
subprocess.run(f'git -C {REPO} archive HEAD | tar -x -C {SC}', shell=True, check=True)
show = lambda rev, rel: subprocess.run(['git', '-C', REPO, 'show', f'{rev}:{rel}'], capture_output=True, check=True).stdout
basepage = show(base, page)
for o, n in (x.split('=>') for x in os.environ.get('PATCH', '').split(';;') if x):
    g = os.path.join(SC, gen); t = open(g, encoding='utf-8').read(); assert t.count(o) == 1, o
    open(g, 'w', encoding='utf-8').write(t.replace(o, n))

def run(tag, stats):
    for rel, data in stats.items(): open(os.path.join(SC, rel), 'wb').write(data)
    open(os.path.join(SC, page), 'wb').write(basepage)
    r = subprocess.run(['python3', os.path.join(SC, gen)] + [a.replace('{ROOT}', SC) for a in args], cwd=SC,
                       capture_output=True, text=True)
    print(f'[{tag}] exit {r.returncode}', (r.stdout + r.stderr).strip()[-400:])
    shutil.copy(os.path.join(SC, page), os.path.join(OUT, f'{name}_gen{tag}.html'))

run('A', {rel: show(OLD_REV, rel) for rel in STATS})
run('B', {rel: open(os.path.join(REPO, rel), 'rb').read() for rel in STATS})
shutil.rmtree(SC)
