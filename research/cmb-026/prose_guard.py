#!/usr/bin/env python3
"""CMB-026 prose guard: the anti-slop pass changed prose only, and the only content cuts are step 3's.

usage: python3 research/cmb-026/prose_guard.py [--base REF] [--root DIR]

For each page of CMB-026 steps 2 and 3 it reads the base (git REF, default origin/main, which was c8a095c
when the branch started; after the merge pass --base c8a095c) and the working copy (or the copy under DIR),
and compares what the prose pass must not touch:
  numbers       every number in the page, in order: text and attribute values everywhere outside the
                JSON-LD, so every number in <main>
  faq-numbers   every number in the FAQ answers of the JSON-LD, in order
  links         every href, src and srcset, in order
  titles        the <title> text (and any SVG <title>)
  meta          every <meta> tag with all its attributes (the meta description among them)
  headings      every h1-h6: level, id and text, in order (the H1, H2, H3 and the h4 card titles)
  cells         every table cell (th, td) text, in order
  faq-q         every visible FAQ question
  json-ld       every JSON-LD block, parsed, with the FAQ answer texts and dateModified masked: step 2
                rewrites FAQ answers and the JSON-LD follows them; step 4 moves dateModified, which
                research/dates/date_truth.py checks
  file          /blog/bmi-limitations/ gets no prose edits, so its whole file (whitespace collapsed,
                dateModified masked) must equal the base after the cut: the text around the block stays

The step-3 cuts are applied to the base by this script; the base after the cuts must equal the working copy
in every check above, and each cut must be gone from the working copy:
  /blog/how-to-lower-bmi/    the sentences "Recalculate your TDEE every 10-15 pounds lost." and
                             "Plateaus can last 2-4 weeks."
  /blog/bmi-limitations/     the .chart-compare block under Limitation #7 (bars 85/15, 35/65, 45/55, no source)
  /blog/bmi-and-metabolism/  every .info-card and .tip-item with a heading and no body; the icons of a grid
                             that lost a card are renumbered 1..n
Per page it prints the differences the step-3 cuts make (the only ones allowed), then any other difference.
Exit 0 = only the step-3 differences; 1 = any other difference, a cut not made, or a cut not in the base.
Proof that it catches changes: research/cmb-026/guard_breaks.py.
"""
import argparse
import difflib
import html
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = subprocess.run(['git', '-C', HERE, 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()

PAGES = ['calculators', 'age-bmi-calculator', 'about', 'blog/how-to-lower-bmi',
         'blog/bmi-and-health-risks', 'blog/bmi-and-metabolism', 'blog/bmi-limitations']
SENTENCES = {'blog/how-to-lower-bmi': ['Recalculate your TDEE every 10-15 pounds lost.',
                                       'Plateaus can last 2-4 weeks.']}
CHART_BLOCK = {'blog/bmi-limitations': ('<h2 id="skinny-fat">', '<div class="chart-compare">')}
EMPTY_CARDS = {'blog/bmi-and-metabolism'}
WHOLE_FILE = {'blog/bmi-limitations'}

NUM = re.compile(r'[0-9]+(?:[.,][0-9]+)*')
DATE_MOD = re.compile(r'"dateModified"\s*:\s*"[^"]*"')


class CutError(Exception):
    pass


def git(*a):
    r = subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True)
    if r.returncode:
        raise CutError(f'git {" ".join(a)}: {r.stderr.strip()}')
    return r.stdout


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


# ---------------------------------------------------------------- what the prose pass must not touch
class Page(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.nums, self.links, self.metas, self.heads, self.cells = [], [], [], [], []
        self.faq_q, self.ld, self.titles = [], [], []
        self._title = self._head = self._cell = self._q = self._ld = None
        self._qsvg = self._raw = 0
        self.feed(src)
        self.close()
        self._close_cell()

    def _close_cell(self):
        if self._cell is not None:
            self.cells.append(norm(''.join(self._cell)))
            self._cell = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script' and (a.get('type') or '') == 'application/ld+json':
            self._ld = []
            return
        for k, v in attrs:
            if v:
                self.nums += [(n, f'<{tag} {k}="{v[:60]}">') for n in NUM.findall(v)]
            if k in ('href', 'src', 'srcset'):
                self.links.append(f'{k}={v}')
        if tag in ('script', 'style'):
            self._raw += 1
        if tag == 'title':
            self._title = []
        if tag == 'meta':
            self.metas.append(tuple(sorted((k, v or '') for k, v in attrs)))
        if re.fullmatch(r'h[1-6]', tag):
            self._head = [tag, a.get('id') or '', []]
        if tag in ('td', 'th', 'tr', 'table', 'thead', 'tbody', 'tfoot'):
            self._close_cell()
        if tag in ('td', 'th'):
            self._cell = []
        if tag == 'button' and 'faq-question' in (a.get('class') or '').split():
            self._q = []
        if self._q is not None and tag == 'svg':
            self._qsvg += 1

    def handle_endtag(self, tag):
        if tag == 'script' and self._ld is not None:
            self.ld.append(''.join(self._ld))
            self._ld = None
            return
        if tag in ('script', 'style') and self._raw:
            self._raw -= 1
        if tag == 'title' and self._title is not None:
            self.titles.append(norm(''.join(self._title)))
            self._title = None
        if self._head and tag == self._head[0]:
            self.heads.append((self._head[0], self._head[1], norm(''.join(self._head[2]))))
            self._head = None
        if tag in ('td', 'th', 'tr', 'table', 'thead', 'tbody', 'tfoot'):
            self._close_cell()
        if self._q is not None:
            if tag == 'svg' and self._qsvg:
                self._qsvg -= 1
            elif tag == 'button':
                self.faq_q.append(norm(''.join(self._q)))
                self._q = None

    def handle_data(self, d):
        if self._ld is not None:
            self._ld.append(d)
            return
        for m in NUM.finditer(d):
            self.nums.append((m.group(0), norm(d[max(0, m.start() - 40):m.end() + 40])))
        if self._raw:
            return
        if self._title is not None:
            self._title.append(d)
        if self._head:
            self._head[2].append(d)
        if self._cell is not None:
            self._cell.append(d)
        if self._q is not None and not self._qsvg:
            self._q.append(d)


def ld_view(raw):
    """One JSON-LD block, canonical, with FAQ answer texts and dateModified masked; and the answers' numbers."""
    try:
        data = json.loads(raw)
    except ValueError:
        return 'unparsed: ' + norm(DATE_MOD.sub('"dateModified": "<step 4>"', raw)), []
    nums = []

    def walk(x):
        if isinstance(x, dict):
            out = {}
            for k, v in x.items():
                if k == 'dateModified':
                    out[k] = '<step 4>'
                elif k == 'text' and x.get('@type') == 'Answer' and isinstance(v, str):
                    nums.extend(NUM.findall(v))
                    out[k] = '<FAQ answer>'
                else:
                    out[k] = walk(v)
            return out
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x
    return json.dumps(walk(data), sort_keys=True, ensure_ascii=False), nums


def features(src):
    p = Page(src)
    lds = [ld_view(r) for r in p.ld]
    return {
        'numbers': p.nums,
        'faq-numbers': [(n, 'FAQPage JSON-LD answer') for _, ns in lds for n in ns],
        'links': p.links,
        'titles': p.titles,
        'meta': p.metas,
        'headings': p.heads,
        'cells': p.cells,
        'faq-q': p.faq_q,
        'json-ld': [v for v, _ in lds],
    }


def compare(fa, fb):
    """Differences from fa to fb, one line per changed run, with context."""
    out = []
    for key in fa:
        a, b = fa[key], fb[key]
        if key in ('numbers', 'faq-numbers'):
            ka, kb = [n for n, _ in a], [n for n, _ in b]
        else:
            ka, kb = a, b
        if ka == kb:
            continue
        sm = difflib.SequenceMatcher(None, ka, kb, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal':
                continue
            if key in ('numbers', 'faq-numbers'):
                old = [f'{n} ({c})' for n, c in a[i1:i2]]
                new = [f'{n} ({c})' for n, c in b[j1:j2]]
            elif key == 'json-ld':
                old = [x[:200] for x in a[i1:i2]]
                new = [x[:200] for x in b[j1:j2]]
                if len(old) == len(new) == 1:
                    s = difflib.SequenceMatcher(None, old[0], new[0], autojunk=False)
                    m = next(op for op in s.get_opcodes() if op[0] != 'equal')
                    old = [a[i1][max(0, m[1] - 60):m[2] + 60]]
                    new = [b[j1][max(0, m[3] - 60):m[4] + 60]]
            else:
                old, new = list(map(str, a[i1:i2])), list(map(str, b[j1:j2]))
            out.append(f'{key}: {op} {old} -> {new}')
    return out


def file_view(src):
    s = DATE_MOD.sub('"dateModified": "<step 4>"', src)
    return re.split(r'(<[^>]+>)', re.sub(r'>\s+<', '><', re.sub(r'\s+', ' ', s)))


def file_diff(a, b):
    ta, tb = [t for t in file_view(a) if t.strip()], [t for t in file_view(b) if t.strip()]
    if ta == tb:
        return []
    out = []
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal':
            out.append(f'file: {op} {"".join(ta[i1:i2])[:240]!r} -> {"".join(tb[j1:j2])[:240]!r}')
    return out


# ---------------------------------------------------------------- the step-3 cuts, applied to the base
def div_end(src, start):
    """Index just past the </div> that closes the <div ...> opening at start."""
    depth = 0
    for m in re.finditer(r'<div\b|</div\s*>', src[start:]):
        depth += -1 if m.group(0).startswith('</') else 1
        if depth == 0:
            return start + m.end()
    raise CutError(f'unbalanced <div> at {start}')


def drop(src, i, j):
    """Remove src[i:j] and one space beside it."""
    if i > 0 and src[i - 1] == ' ':
        i -= 1
    elif j < len(src) and src[j] == ' ':
        j += 1
    return src[:i] + src[j:]


def empty_cards(src):
    """(start, end, title) of every .info-card / .tip-item that has a heading and no body."""
    out = []
    for m in re.finditer(r'<div class="(?:info-card|tip-item)">', src):
        end = div_end(src, m.start())
        inner = src[m.end():end - len('</div>')]
        heads = re.findall(r'(?s)<h([2-6])\b[^>]*>(.*?)</h\1>', inner)
        rest = re.sub(r'<div class="(?:info-card-icon|tip-icon)">[^<]*</div>', '', inner)
        rest = re.sub(r'(?s)<h([2-6])\b[^>]*>.*?</h\1>', '', rest)
        if heads and not re.search(r'<(?:p|ul|ol|li|img|svg|table|figure|a)\b', rest) \
                and not html.unescape(re.sub(r'<[^>]+>', '', rest)).strip():
            out.append((m.start(), end, norm(re.sub(r'<[^>]+>', '', heads[0][1]))))
    return out


def cut_empty_cards(src):
    cards = empty_cards(src)
    if not cards:
        raise CutError('no .info-card / .tip-item with a heading and no body in the base')
    grids = [(m.start(), div_end(src, m.start()))
             for m in re.finditer(r'<div class="(?:info-card-grid|tips-grid)">', src)]
    hit = sorted({g for g in grids for c in cards if g[0] < c[0] and c[1] <= g[1]}, reverse=True)
    loose =[c for c in cards if not any(g[0] < c[0] and c[1] <= g[1] for g in grids)]
    if loose:
        raise CutError(f'empty card outside a grid: {loose[0][2]!r}')
    notes = [f'card "{t}" (heading, no body) removed' for _, _, t in cards]
    renum = []
    for gs, ge in hit:                                # last grid first, so earlier offsets stay valid
        grid = src[gs:ge]
        gone = [t for _, _, t in empty_cards(grid)]
        for cs, ce, _ in sorted(empty_cards(grid), reverse=True):
            grid = drop(grid, cs, ce)
        n = iter(range(1, 100))
        grid, k = re.subn(r'(<div class="(?:info-card-icon|tip-icon)">)\s*[0-9]+\s*(</div>)',
                          lambda m: f'{m.group(1)}{next(n)}{m.group(2)}', grid)
        renum.insert(0, f'the {k} cards left in the grid of "{gone[0]}" renumbered 1..{k}')
        src = src[:gs] + grid + src[ge:]
    return src, notes + renum


def base_after_cuts(page, src):
    """The base with page's step-3 cuts applied, and one line per cut."""
    notes = []
    for s in SENTENCES.get(page, []):
        n = src.count(s)
        if n != 1:
            raise CutError(f'sentence {s!r} is in the base {n} times (need 1)')
        i = src.index(s)
        src = drop(src, i, i + len(s))
        notes.append(f'sentence "{s}" deleted')
    if page in CHART_BLOCK:
        head, block = CHART_BLOCK[page]
        starts = [m.start() for m in re.finditer(re.escape(block), src)]
        if len(starts) != 1:
            raise CutError(f'{block} is in the base {len(starts)} times (need 1)')
        h = src.find(head)
        nxt = src.find('<h2', h + 1)
        if not (0 <= h < starts[0] < nxt):
            raise CutError(f'{block} is not under {head}')
        end = div_end(src, starts[0])
        rows = src[starts[0]:end].count('class="chart-compare-row"')
        widths = re.findall(r'width:\s*([0-9]+)%', src[starts[0]:end])
        src = drop(src, starts[0], end)
        notes.append(f'.chart-compare block under Limitation #7 deleted ({rows} rows, widths {"/".join(widths)})')
    if page in EMPTY_CARDS:
        src, n = cut_empty_cards(src)
        notes += n
    return src, notes


def cuts_not_made(page, work):
    out = []
    for s in SENTENCES.get(page, []):
        if s in work:
            out.append(f'step 3 cut not made: sentence {s!r} still on the page')
    if page in CHART_BLOCK and CHART_BLOCK[page][1] in work:
        out.append(f'step 3 cut not made: {CHART_BLOCK[page][1]} still on the page')
    if page in EMPTY_CARDS:
        out += [f'step 3 cut not made: card "{t}" has a heading and no body' for _, _, t in empty_cards(work)]
    return out


def check(page, base, work):
    """(allowed differences, other differences) for one page."""
    cut, notes = base_after_cuts(page, base)
    fb, fc, fw = features(base), features(cut), features(work)
    allowed = notes + compare(fb, fc)
    other = compare(fc, fw) + cuts_not_made(page, work)
    if page in WHOLE_FILE:
        other += file_diff(cut, work)
    return allowed, other


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--base', default='origin/main', help='git ref of the base (default origin/main)')
    ap.add_argument('--root', default=REPO, help='folder holding the working copy of the pages')
    args = ap.parse_args()
    bad = 0
    for page in PAGES:
        f = f'{page}/index.html'
        try:
            base = git('show', f'{args.base}:{f}')
            work = open(os.path.join(args.root, f), encoding='utf-8').read()
            allowed, other = check(page, base, work)
        except (CutError, OSError) as e:
            print(f'FAIL /{page}/: {e}')
            bad += 1
            continue
        bad += bool(other)
        print(f'{"FAIL" if other else "ok  "} /{page}/: '
              + (f'{len(allowed)} step-3 difference(s)' if allowed else 'no difference in the guarded parts')
              + (f', {len(other)} other difference(s)' if other else ''))
        for line in allowed:
            print(f'       step 3  {line}')
        for line in other:
            print(f'   NOT ALLOWED {line}')
    print(f'prose_guard: {len(PAGES) - bad}/{len(PAGES)} pages pass'
          + (' (only the step-3 differences)' if not bad else ' - FAIL'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
