#!/usr/bin/env python3
"""Page scores: S (sourcing), P (prose) and D (design) for every page in sitemap.xml (D-26).

usage: python3 scripts/page_scores.py [--qa DIR] [--pages /a/,/b/] [--devlog] [--resume] [--keep-snap]
  --qa      a clone of Mapstor/portfolio-qa with `npm ci` run (default: ../portfolio-qa next to this repo)
  --pages   measure only these pages; the other rows of research/page-scores.csv stay as they are (each row
            keeps its own date)
  --devlog  also write the Scores line as the first line under "## §0 Resume here" in DEVLOG.md
  --resume  reuse what a stopped run of the same pages already measured (kept in /tmp/page-scores-cache);
            without it every step runs again

Serves the repo root on a free local port, measures, writes research/page-scores.csv (one row per sitemap page,
in sitemap order) and prints the Scores line and the ten worst pages. Needs Python Playwright with Chromium,
Node, and the Impeccable engine the repo's launcher fetches (pinned in .claude/skills/impeccable/scripts/VERSION).

S sourcing: every number traces to a verified source (D-10).
  page test  a page with its own browser test (PAGE_TESTS) passes when the test exits 0 with 0 failures and no
             skips; it checks every printed value against the stats file built from the registry's primary data.
  audit      the other pages in research/stage1-audit/audit.py's list pass at 0 calculator or arithmetic
             mismatches, 0 outside facts with no registry row, 0 not in their row and 0 unclassified numbers.
  A page neither covers is "not measured".
P prose: portfolio-qa prose-score.mjs, countable anti-slop tells per 1,000 words of body prose; pass at 2.0 or
  fewer (the site-pipeline Stage 2 target). The score is a floor: it can't hear rhythm or forced triads. Legal
  pages are scored too (prose-score leaves them out of its own totals). Under 30 words: not measured.
D design: the Impeccable detector (`impeccable detect --json --no-advisory`) at 390x844 and 1280x800 and, on a
  page with a Calculate button, a snapshot taken after Calculate with the default inputs, scanned at both sizes;
  plus the page never wider than the screen at 390, 360 and 320 px, before and after Calculate. Pass at 0.

research/page-scores-known.csv lists open items from DEVLOG §5 that no measurement here sees (a wording a source
doesn't back, a chart drawn to the wrong proportions). Each one fails its score on its page until its row is
deleted in the batch that fixes it.
"""
import argparse
import csv
import datetime
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / 'research' / 'page-scores.csv'
KNOWN = REPO / 'research' / 'page-scores-known.csv'
AUDIT = REPO / 'research' / 'stage1-audit' / 'audit.py'
IMPECCABLE = REPO / '.claude' / 'skills' / 'impeccable' / 'scripts' / 'impeccable'
SNAP = REPO / '_snap'   # git-ignored; the detector can't click Calculate, so it scans a frozen copy
FIELDS = ['page', 'template', 's', 's_value', 'p', 'p_value', 'd', 'd_value', 'date']
P_TARGET = 2.0

# Pages with a browser test of their own (DEVLOG §4): script, stats file.
PAGE_TESTS = {
    '/': ('research/home-build/home_test_playwright.py', 'research/home-build/home_stats.json'),
    '/blog/healthy-bmi-range/': ('research/healthy-range-build/hbr_test_playwright.py', 'research/healthy-range-build/healthy_stats.json'),
    '/blog/bmi-chart-women/': ('research/chart-women-build/bcw_test_playwright.py', 'research/chart-women-build/bcw_stats.json'),
    '/bmi-chart/': ('research/bmi-chart-build/bc_test_playwright.py', 'research/bmi-chart-build/bc_stats.json'),
    '/body-fat-percentage-chart/': ('research/body-fat-chart-build/bfpc_test_playwright.py', 'research/body-fat-chart-build/bfpc_stats.json'),
    '/women-bmi-calculator/': ('research/women-calc-build/wbc_test_playwright.py', 'research/women-calc-build/wbc_stats.json'),
    '/blog/bmi-chart-men/': ('research/chart-men-build/bcm_test_playwright.py', 'research/chart-men-build/bcm_stats.json'),
    '/average-weight/': ('research/average-weight-build/aw_test_playwright.py', 'research/average-weight/avgw_results.json'),
    '/body-fat-calculator/': ('research/body-fat-calculator-build/bfcalc_test_playwright.py', 'research/body-fat-calculator-build/bfc_stats.json'),
    '/blog/how-to-measure-body-fat/': ('research/how-to-measure-body-fat-build/htm_test_playwright.py', 'research/how-to-measure-body-fat-build/htm_stats.json'),
    '/us-obesity-statistics/': ('research/us-obesity-statistics-build/obs_test_playwright.py', 'research/us-obesity-statistics-build/obs_sources.json'),
    '/new-bmi-calculator/': ('research/new-bmi-build/nb_test_playwright.py', 'research/new-bmi-build/nb_stats.json'),
    '/calculators/': ('research/cmb-027/hub_examples_playwright.py', None),
    '/ideal-weight/': ('research/ideal-weight-build/iw_test_playwright.py', 'research/ideal-weight-build/iw_stats.json'),
    '/kids-bmi-calculator/': ('research/kids-build/kids_test_playwright.py', 'research/kids-build/kids_stats.json'),
    '/age-bmi-calculator/': ('research/age-calc-build/abc_test_playwright.py', 'research/age-calc-build/abc_stats.json'),
    '/men-bmi-calculator/': ('research/men-pilot/men_test_playwright.py', 'research/men-pilot/men_stats.json'),
}
# Pages a generator owns (it reproduces the page byte for byte): fix the generator, never the page.
GENERATORS = {
    '/new-bmi-calculator/': 'research/new-bmi-build/gen_nb.py',
    '/ideal-weight/': 'research/ideal-weight-build/gen_iw.py',
    '/kids-bmi-calculator/': 'research/kids-build/gen_kids.py',
    '/age-bmi-calculator/': 'research/age-calc-build/gen_abc.py',
}

OVERFLOW_JS = """() => document.documentElement.scrollWidth - window.innerWidth"""
CLICK_JS = """() => { const b = [...document.querySelectorAll('.calculate-btn')].find(e => e.offsetParent !== null);
  if (!b) return false; b.click(); return true; }"""


def sitemap_pages():
    xml = (REPO / 'sitemap.xml').read_text(encoding='utf-8')
    seen, out = set(), []
    for loc in re.findall(r'<loc>\s*([^<\s]+)', xml):
        if '/assets/' in loc:
            continue
        p = re.sub(r'^https?://[^/]+', '', loc) or '/'
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def page_file(p):
    return REPO / (p.strip('/') + '/index.html' if p != '/' else 'index.html')


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def serve():
    port = free_port()
    proc = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', str(REPO)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://localhost:{port}'   # some page tests allow only http://localhost requests
    for _ in range(50):
        try:
            urllib.request.urlopen(base + '/sitemap.xml', timeout=1)
            return proc, base
        except Exception:
            time.sleep(0.1)
    proc.kill()
    sys.exit('could not start the local server')


# ---------------------------------------------------------------- S
def run_page_test(p, base):
    script, stats = PAGE_TESTS[p]
    cmd = [sys.executable, str(REPO / script), base] + ([str(REPO / stats)] if stats else [])
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        return None, 'page test timed out'
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    m = None
    for l in reversed(lines):
        m = re.search(r'(\d[\d,]*) checks?, (\d+) failures?(?:, (\d+) skipped)?', l)
        if m:
            break
    if not m:
        return False, f'page test exit {r.returncode}, no result line'
    checks, fails = int(m.group(1).replace(',', '')), int(m.group(2))
    skipped = m.group(3)
    ok = r.returncode == 0 and fails == 0 and (skipped is None or int(skipped) == 0)
    text = f'page test {checks:,} checks, {fails} failures' + (f', {skipped} skipped' if skipped is not None else '')
    return ok, text


def run_audit(pages, base, tmp):
    audited = [p for p in pages if p in audit_pages()]
    if not audited:
        return {}
    out = Path(tmp) / 'audit'
    r = subprocess.run([sys.executable, str(AUDIT), base, '--pages', ','.join(audited), '--out', str(out)],
                       cwd=REPO, capture_output=True, text=True, timeout=3600)
    rep = out / 'report.json'
    if not rep.exists():
        print('audit failed:', (r.stdout + r.stderr)[-800:], file=sys.stderr)
        return {}
    res = {}
    for pg in json.loads(rep.read_text(encoding='utf-8'))['pages']:
        res[pg['page']] = {'mism': len(pg['mismatches']), 'norow': len(pg['c_no_row']), 'notin': len(pg['c_not_in_row']),
                           'u': pg['totals'].get('U', 0), 'errors': len(pg.get('page_errors') or [])}
    if r.returncode != 0:
        print('audit exit', r.returncode, '(unclassified numbers or check errors; see the U and error counts)', file=sys.stderr)
    return res


_AUDIT_PAGES = None


def audit_pages():
    global _AUDIT_PAGES
    if _AUDIT_PAGES is None:
        src = AUDIT.read_text(encoding='utf-8')
        block = re.search(r'^PAGES = \[(.*?)\]', src, re.S | re.M).group(1)
        _AUDIT_PAGES = set(re.findall(r"'(/[^']*)'", block))
    return _AUDIT_PAGES


# ---------------------------------------------------------------- P
def run_prose(base, qa, tmp):
    out = Path(tmp) / 'prose.json'
    r = subprocess.run(['node', str(qa / 'prose-score.mjs'), base, str(out)], cwd=qa, capture_output=True, text=True, timeout=900)
    if not out.exists():
        print('prose-score failed:', (r.stdout + r.stderr)[-800:], file=sys.stderr)
        return {}
    return {p['path']: p for p in json.loads(out.read_text(encoding='utf-8'))}


# ---------------------------------------------------------------- D
def browser_pass(pages, base):
    """Page width at 390, 360 and 320 px before and after Calculate; a frozen after-Calculate copy for the detector."""
    from playwright.sync_api import sync_playwright
    over, snaps, tools = {}, {}, set()
    SNAP.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
        pg = br.new_page(viewport={'width': 390, 'height': 844})
        pg.route(re.compile(r'^(?!http://localhost).*'), lambda r: r.abort())
        for p in pages:
            bad = []
            for w, h in ((390, 844), (360, 800), (320, 700)):
                pg.set_viewport_size({'width': w, 'height': h})
                pg.goto(base + p, wait_until='load')
                pg.wait_for_timeout(250)
                if pg.evaluate(OVERFLOW_JS) > 0:
                    bad.append(f'{w} px')
                if pg.evaluate(CLICK_JS):
                    tools.add(p)
                    pg.wait_for_timeout(600)
                    if pg.evaluate(OVERFLOW_JS) > 0:
                        bad.append(f'{w} px after Calculate')
                    if w == 390:
                        html = pg.evaluate("() => '<!DOCTYPE html>' + document.documentElement.outerHTML")
                        html = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', html)
                        name = (p.strip('/') or 'home').replace('/', '_') + '.html'
                        (SNAP / name).write_text(html, encoding='utf-8')
                        snaps[p] = '/_snap/' + name
            over[p] = bad
        br.close()
    return over, snaps, tools


def detect(base, paths, viewport, cache):
    """Primary findings per path as {rule: count}; None for a path the detector couldn't scan. Batches of 8,
    cached after each."""
    def run(batch):
        r = subprocess.run([str(IMPECCABLE), 'detect', '--json', '--no-advisory', '--viewport', viewport] + [base + x for x in batch],
                           cwd=REPO, capture_output=True, text=True, timeout=1800)
        if 'UPDATE_AVAILABLE' in r.stderr:
            print('impeccable: UPDATE_AVAILABLE (note it in DEVLOG §0; no self-update, CLAUDE.md R5)', file=sys.stderr)
        try:
            found = json.loads(r.stdout or '[]')
        except json.JSONDecodeError:
            found = None
        return r.returncode, found
    counts = cache.get(f'det-{viewport}', {})
    todo = [x for x in paths if x not in counts]
    for i in range(0, len(todo), 8):
        batch = todo[i:i + 8]
        code, found = run(batch)
        if code == 1 or found is None:   # a target failed: scan one by one to find it
            for x in batch:
                c, f = run([x])
                counts[x] = None if (c == 1 or f is None) else rules(f)
        else:
            for x in batch:
                counts[x] = rules([f for f in found if f.get('file') == base + x])
        cache.put(f'det-{viewport}', counts)
        print(f'  detector {viewport}: {len(counts)}/{len(paths)}', file=sys.stderr)
    return counts


def rules(findings):
    out = {}
    for f in findings:
        out[f.get('antipattern', '?')] = out.get(f.get('antipattern', '?'), 0) + 1
    return out


class Cache:
    """Each step's results as JSON in /tmp/page-scores-cache, so --resume can continue a stopped run."""
    def __init__(self, key, resume):
        self.dir = Path(tempfile.gettempdir()) / 'page-scores-cache'
        meta = self.dir / 'meta.json'
        if not resume or not meta.exists() or json.loads(meta.read_text()) != key:
            shutil.rmtree(self.dir, ignore_errors=True)
            self.dir.mkdir(parents=True)
            meta.write_text(json.dumps(key))

    def get(self, name, default=None):
        f = self.dir / f'{name}.json'
        return json.loads(f.read_text(encoding='utf-8')) if f.exists() else default

    def put(self, name, value):
        (self.dir / f'{name}.json').write_text(json.dumps(value), encoding='utf-8')
        return value

    def clear(self):
        shutil.rmtree(self.dir, ignore_errors=True)


# ---------------------------------------------------------------- known open items
def known_items():
    items = {}
    if KNOWN.exists():
        with KNOWN.open(encoding='utf-8', newline='') as fh:
            for row in csv.DictReader(fh):
                items.setdefault((row['page'], row['score'].upper()), []).append(row['item'])
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--qa', default=str(REPO.parent / 'portfolio-qa'))
    ap.add_argument('--pages', default='')
    ap.add_argument('--devlog', action='store_true')
    ap.add_argument('--keep-snap', action='store_true')
    ap.add_argument('--resume', action='store_true')
    a = ap.parse_args()
    qa = Path(a.qa).resolve()
    if not (qa / 'prose-score.mjs').exists():
        sys.exit(f'prose-score.mjs not found in {qa} (clone Mapstor/portfolio-qa and run npm ci there)')
    all_pages = sitemap_pages()
    pages = [p for p in all_pages if not a.pages or p in a.pages.split(',')]
    if a.pages and len(pages) != len(a.pages.split(',')):
        sys.exit('--pages names a page that is not in sitemap.xml')
    today = datetime.date.today().isoformat()
    known = known_items()
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip()
    cache = Cache({'pages': pages, 'head': head, 'day': today}, a.resume)
    proc, base = serve()
    tmp = tempfile.mkdtemp(prefix='page-scores-')
    done = False
    try:
        t0 = time.time()
        tests = cache.get('tests') or cache.put('tests', {p: run_page_test(p, base) for p in pages if p in PAGE_TESTS})
        print(f'page tests {len(tests)} ({time.time() - t0:.0f}s)', file=sys.stderr)
        audit = cache.get('audit') or cache.put('audit', run_audit(pages, base, tmp))
        print(f'audit {len(audit)} pages ({time.time() - t0:.0f}s)', file=sys.stderr)
        prose = cache.get('prose') or cache.put('prose', run_prose(base, qa, tmp))
        print(f'prose {len(prose)} pages ({time.time() - t0:.0f}s)', file=sys.stderr)
        b = cache.get('browser')
        if not b or not all((REPO / s.lstrip('/')).exists() for s in b['snaps'].values()):
            over, snaps, tools = browser_pass(pages, base)
            b = cache.put('browser', {'over': over, 'snaps': snaps, 'tools': sorted(tools)})
        over, snaps, tools = b['over'], b['snaps'], set(b['tools'])
        print(f'browser pass, {len(snaps)} after-Calculate copies ({time.time() - t0:.0f}s)', file=sys.stderr)
        paths = pages + list(snaps.values())
        det = {vp: detect(base, paths, vp, cache) for vp in ('390x844', '1280x800')}
        print(f'detector ({time.time() - t0:.0f}s)', file=sys.stderr)
        done = True
    finally:
        proc.terminate()
        if done and not a.keep_snap:
            shutil.rmtree(SNAP, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)

    rows = {}
    if OUT.exists():
        with OUT.open(encoding='utf-8', newline='') as fh:
            rows = {r['page']: r for r in csv.DictReader(fh)}
    for p in pages:
        html = page_file(p).read_text(encoding='utf-8')
        tpl = []
        if p in GENERATORS:
            tpl.append(GENERATORS[p])
        if p in tools and '/assets/js/calculator.js' in html:
            tpl.append('assets/js/calculator.js (results)')
        # S
        open_s = known.get((p, 'S'), [])
        if p in tests:
            ok, text = tests[p]
            s = 'pass' if ok else 'fail'
            sv = text
        elif p in audit:
            r = audit[p]
            ok = not (r['mism'] or r['norow'] or r['notin'] or r['u'] or r['errors'])
            s = 'pass' if ok else 'fail'
            sv = f"audit {r['mism']} mismatches, {r['norow']} no row, {r['notin']} not in row" + \
                 (f", {r['u']} unclassified" if r['u'] else '') + (f", {r['errors']} page errors" if r['errors'] else '')
        else:
            s, sv = 'not measured', 'no page test; not in the Stage 1 audit'
        if open_s:
            s = 'fail'
            sv += ' | open: ' + ' || '.join(open_s)
        # P
        pr = prose.get(p)
        if pr is None:
            pstat, pv = 'not measured', 'prose-score did not read the page'
        elif pr['words'] < 30:
            pstat, pv = 'not measured', f"{pr['words']} words"
        else:
            pstat = 'pass' if pr['per1k'] <= P_TARGET else 'fail'
            hits = ', '.join(f'{k} {v}' for k, v in sorted(pr['hits'].items(), key=lambda kv: -kv[1]))
            pv = f"{pr['per1k']}/1k ({pr['tells']} tells, {pr['words']} words{': ' + hits if hits else ''})"
        open_p = known.get((p, 'P'), [])
        if open_p:
            pstat, pv = 'fail', pv + ' | open: ' + ' || '.join(open_p)
        # D
        parts, total, unknown = [], 0, False
        for vp, label in (('390x844', '390'), ('1280x800', '1280')):
            for key, lab in ((p, label), (snaps.get(p), label + ' results')):
                if key is None:
                    continue
                r = det[vp].get(key)
                unknown |= r is None
                n = sum(r.values()) if r else 0
                total += n
                top = ', '.join(f'{k} {v}' for k, v in sorted((r or {}).items(), key=lambda kv: (-kv[1], kv[0])))
                parts.append(f'{lab}: ?' if r is None else f'{lab}: {n}' + (f' ({top})' if top else ''))
        if over[p]:
            parts.append('wider than the screen at ' + ', '.join(over[p]))
        dstat = 'not measured' if unknown else ('pass' if total == 0 and not over[p] else 'fail')
        dv = 'detector ' + ', '.join(parts)
        open_d = known.get((p, 'D'), [])
        if open_d:
            dstat, dv = 'fail', dv + ' | open: ' + ' || '.join(open_d)
        rows[p] = {'page': p, 'template': '; '.join(tpl), 's': s, 's_value': sv, 'p': pstat, 'p_value': pv,
                   'd': dstat, 'd_value': dv, 'date': today}
    ordered = [rows[p] for p in all_pages if p in rows]
    with OUT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
        w.writeheader()
        w.writerows(ordered)

    n = len(all_pages)
    cnt = lambda k: sum(1 for r in ordered if r[k] == 'pass')
    allp = sum(1 for r in ordered if r['s'] == r['p'] == r['d'] == 'pass')
    dates = sorted({r['date'] for r in ordered})
    when = dates[-1] if len(dates) == 1 else f'{dates[0]} to {dates[-1]}'
    line = f"Scores: S {cnt('s')}/{n} | P {cnt('p')}/{n} | D {cnt('d')}/{n} | all three {allp}/{n} ({when})"
    print(line)
    print('ten worst:')
    for r in sorted(ordered, key=badness, reverse=True)[:10]:
        print(f"  {r['page']}  S {short(r, 's')} | P {short(r, 'p')} | D {short(r, 'd')}")
    if a.devlog:
        write_devlog(line)


def nums(text):
    return [int(x) for x in re.findall(r'(\d+) (?:mismatches|no row|not in row|unclassified)', text)]


def badness(r):
    fails = sum(r[k] != 'pass' for k in ('s', 'p', 'd'))
    opens = r['s_value'].split('open:')[1].count(' || ') + 1 if 'open:' in r['s_value'] else 0
    opens += r['d_value'].split('open:')[1].count(' || ') + 1 if 'open:' in r['d_value'] else 0
    work = sum(nums(r['s_value'])) + opens
    work += sum(int(x) for x in re.findall(r'(?:390|1280)(?: results)?: (\d+)', r['d_value'])) + r['d_value'].count('wider than')
    m = re.match(r'([\d.]+)/1k \((\d+) tells, (\d+) words', r['p_value'])
    if m:
        work += max(0, round(int(m.group(2)) - P_TARGET * int(m.group(3)) / 1000))
    return work, fails


def short(r, k):
    v = r[f'{k}_value']
    if r[k] == 'pass':
        return 'pass'
    if k == 's':
        bits = []
        if v.startswith('audit'):
            bits = [f'{a} {b}' for a, b in zip(nums(v), ('mism', 'no row', 'not in row', 'unclassified')) if a]
        elif v.startswith('page test'):
            m = re.search(r'(\d+) failures(?:, (\d+) skipped)?', v)
            if not m or int(m.group(1)) or (m.group(2) and int(m.group(2))):
                bits = ['page test fails']
        elif v.startswith('no page test'):
            bits = ['no full check']
        if 'open:' in v:
            bits.append(f"{v.split('open:')[1].count(' || ') + 1} open")
        return (r[k] + ' ' + ', '.join(bits)).strip()
    if k == 'p':
        return v.split(' (')[0] if r[k] != 'not measured' else 'not measured'
    found = sum(int(x) for x in re.findall(r'(?:390|1280)(?: results)?: (\d+)', v))
    extra = (', wider' if 'wider than' in v else '') + (f", {v.split('open:')[1].count(' || ') + 1} open" if 'open:' in v else '')
    return f'{found} findings{extra}'


def write_devlog(line):
    path = REPO / 'DEVLOG.md'
    text = path.read_text(encoding='utf-8')
    head = '## §0 Resume here\n'
    i = text.index(head) + len(head)
    rest = text[i:]
    rest = re.sub(r'^- Scores: [^\n]*\n', '', rest)  # the old line, if it is the first
    path.write_text(text[:i] + f'- {line}\n' + rest, encoding='utf-8')


if __name__ == '__main__':
    main()
