#!/usr/bin/env python3
"""Proof for prose_guard.py (CMB-026 step 1): breaks on a temp copy that the guard must catch.

usage: python3 research/cmb-026/guard_breaks.py [--base REF] [--from base|working]
  --from base     (default) the clean copy is the base with the step-3 cuts applied by the guard itself,
                  so the proof runs before or after the prose pass
  --from working  the clean copy is the working copy of the seven pages (run after the prose pass)

The clean copy must pass. Each break is applied to a fresh temp copy and must fail the guard on the check
named; the two the prompt asks for come first (one changed number, one removed link). The last case is a
control: a FAQ answer reworded in both the page and its JSON-LD is prose, so it must pass.
Exit 0 = every expectation held.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prose_guard as G  # noqa: E402

GUARD = os.path.join(HERE, 'prose_guard.py')


class NotApplicable(Exception):
    pass


def rep(old, new, times=1):
    """Replace old with new; old must be on the page exactly `times` times (None = at least once)."""
    def fn(src):
        n = src.count(old)
        if n == 0 or (times is not None and n != times):
            raise NotApplicable(f'{old[:60]!r} is on the page {n} times (need {times or "1+"})')
        return src.replace(old, new)
    return fn


def rep_ld(old, new):
    """Replace old with new inside the JSON-LD only (the visible page keeps old)."""
    def fn(src):
        hits = []
        def sub(m):
            hits.append(m.group(0).count(old))
            return m.group(0).replace(old, new)
        out = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>', sub, src)
        if sum(hits) != 1:
            raise NotApplicable(f'{old[:60]!r} is in the JSON-LD {sum(hits)} times (need 1)')
        return out
    return fn


def drop_card(title):
    """Remove the whole .info-card whose heading is `title` (a card with a body)."""
    def fn(src):
        for m in re.finditer(r'<div class="info-card">', src):
            end = G.div_end(src, m.start())
            if f'<h4>{title}</h4>' in src[m.start():end] and '<p>' in src[m.start():end]:
                return G.drop(src, m.start(), end)
        raise NotApplicable(f'no .info-card with body titled {title!r}')
    return fn


# (name, page, transform, check that must catch it; None = must pass)
BREAKS = [
    ('one changed number', 'calculators', rep('40.3% of U.S. adults', '40.4% of U.S. adults'), 'numbers'),
    ('one removed link', 'about',
     rep('<a href="/blog/bmi-limitations/">BMI limitations</a>', 'BMI limitations'), 'links'),
    ('number changed in a table cell', 'age-bmi-calculator', rep('<td>28.0</td>', '<td>28.1</td>'), 'cells'),
    ('H2 reworded', 'blog/bmi-and-health-risks',
     rep('<h2>Kidney Disease</h2>', '<h2>Kidney Disease and BMI</h2>'), 'headings'),
    ('table cell reworded', 'blog/bmi-and-health-risks',
     rep('<td>Hormonal influences</td>', '<td>Hormones</td>'), 'cells'),
    ('meta description edited', 'blog/bmi-and-metabolism',
     rep('content="Comprehensive guide to BMI and metabolism.', 'content="A guide to BMI and metabolism.'), 'meta'),
    ('title edited', 'about', rep('<title>About CalculateMyBMI - Free', '<title>About CalculateMyBMI: Free'), 'titles'),
    ('JSON-LD datePublished edited', 'blog/how-to-lower-bmi',
     rep('"datePublished": "2026-02-01"', '"datePublished": "2026-02-02"'), 'json-ld'),
    ('number edited in a JSON-LD FAQ answer only', 'blog/how-to-lower-bmi',
     rep_ld('(every 10-15 pounds lost)', '(every 10-20 pounds lost)'), 'faq-numbers'),
    ('FAQ question reworded', 'calculators',
     rep('How often should I check my BMI?<', 'How often should I weigh in?<'), 'faq-q'),
    ('step 3 sentence put back', 'blog/how-to-lower-bmi',
     rep('your calorie requirements decrease.',
         'your calorie requirements decrease. Recalculate your TDEE every 10-15 pounds lost.'), 'cut not made'),
    ('text around the removed bars cut', 'blog/bmi-limitations',
     rep('>Metabolic health varies significantly within and across BMI categories</p>', '></p>'), 'file'),
    ('a card with a body removed', 'blog/bmi-and-metabolism', drop_card('Adaptive Thermogenesis'), 'headings'),
    ('control: FAQ answer reworded in page and JSON-LD', 'calculators',
     rep('There is no official schedule for adults.', 'No official schedule exists for adults.', times=2), None),
]


def write_copy(root, pages):
    for page, src in pages.items():
        os.makedirs(os.path.join(root, page), exist_ok=True)
        with open(os.path.join(root, page, 'index.html'), 'w', encoding='utf-8') as fh:
            fh.write(src)


def run_guard(root, base):
    r = subprocess.run([sys.executable, GUARD, '--base', base, '--root', root], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='origin/main')
    ap.add_argument('--from', dest='src', choices=('base', 'working'), default='base')
    args = ap.parse_args()
    clean = {}
    for page in G.PAGES:
        f = f'{page}/index.html'
        if args.src == 'base':
            clean[page] = G.base_after_cuts(page, G.git('show', f'{args.base}:{f}'))[0]
        else:
            clean[page] = open(os.path.join(G.REPO, f), encoding='utf-8').read()
    tmp = tempfile.mkdtemp(prefix='cmb026-guard-')
    fails = 0
    try:
        write_copy(os.path.join(tmp, 'clean'), clean)
        code, out = run_guard(os.path.join(tmp, 'clean'), args.base)
        print(f'{"ok  " if code == 0 else "FAIL"} clean copy (--from {args.src}): guard exit {code} (must be 0)')
        if code:
            print(out)
            fails += 1
        for i, (name, page, fn, check) in enumerate(BREAKS, 1):
            pages = dict(clean)
            try:
                pages[page] = fn(pages[page])
            except NotApplicable as e:
                print(f'FAIL {i:2}. {name} on /{page}/: break not applicable: {e}')
                fails += 1
                continue
            root = os.path.join(tmp, f'break{i:02}')
            write_copy(root, pages)
            code, out = run_guard(root, args.base)
            caught = [l.strip() for l in out.splitlines() if 'NOT ALLOWED' in l or l.startswith('FAIL /')]
            if check is None:
                good = code == 0
                what = 'passes (prose may change)' if good else f'exit {code}, caught {caught[:2]}'
            else:
                hits = [l for l in caught if (check + ':') in l or (check == 'cut not made' and check in l)]
                good = code == 1 and bool(hits)
                what = f'fails on {check}' if good else f'exit {code}, caught {caught[:2]}'
            fails += not good
            print(f'{"ok  " if good else "FAIL"} {i:2}. {name} on /{page}/: {what}')
            if check is not None and good:
                print(f'          {hits[0][:170]}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'guard_breaks: {len(BREAKS) + 1 - fails}/{len(BREAKS) + 1} expectations held')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
