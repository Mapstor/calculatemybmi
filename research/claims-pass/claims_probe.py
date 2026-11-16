#!/usr/bin/env python3
"""Claims probe (CMB-048, DEVLOG §5 P1): sentences that claim an effect, a risk, evidence or a reason to see a
professional with no source mark next to them. Reads the HTML files the sitemap lists (no browser), inside <main> only.
usage: python3 research/claims-pass/claims_probe.py [--pages /a/,/b/] [--json OUT] [--all]
A sentence is a hit when it holds a trigger (TRIGGERS below) and neither it nor its own block (the <p>, <li>, <dd>,
<td>, <figcaption> or FAQ answer it sits in) carries a source mark: a link to an outside page, or a citation in
brackets that names a source the registry holds (CDC, NIH, NHLBI, WHO, NCHS, NIDDK, ADA, an author with a year).
--all lists every trigger sentence, sourced or not (the sourced ones marked), for a sentence-by-sentence read.
The probe finds candidates; a person reads each one against the registry row it cites (D-10, §4).
CMB-064: hits that were read and kept (a heading or label over a sourced section, a quote its sentence attributes, a
claim whose source sits in the paragraph before) are listed in reviewed.json with the reason; they print as [read] and
are counted apart, as are the legal pages (OUT_OF_SCOPE). "to read" in the last line is what is left for the pass.
A reviewed.json entry that no longer matches a hit is reported as stale (the sentence changed: read it again)."""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEWED = Path(__file__).resolve().parent / 'reviewed.json'
OUT_OF_SCOPE = ('/terms/', '/privacy/', '/contact/')          # legal pages (DEVLOG §5 P1)
TRIGGERS = [
    r'has been shown', r'\bshown to\b', r'\bproven\b', r'\bstudies (?:show|suggest|find|found|have)\b',
    r'\bresearch (?:shows|suggests|finds|found|has)\b', r'\bevidence\b', r'\blinked (?:to|with)\b', r'\bassociated with\b',
    r'(?-i:\bassociation\b)', r'\beffective(?:ly|ness)?\b', r'\bpromot(?:e|es|ing)\b', r'\bboost(?:s|ing)?\b',
    r'\bimprov(?:e|es|ed|ing|ement|ements)\b',
    r'\b(?:reduc|lower)(?:e|es|ed|ing|s)? (?:the |your |their )?(?:risk|blood|cholesterol|weight|body fat|fat|mortality|inflammation|appetite|insulin|glucose|triglycerides|visceral)',
    r'\b(?:increas|rais)(?:e|es|ed|ing) (?:the |your |their )?risk\b', r'\b(?:higher|lower|increased|reduced|greater) risks?\b',
    r'\bcaus(?:e|es|ed|ing)\b', r'\bleads? to\b', r'\bcontribut(?:e|es|ed|ing) to\b', r'\bprotect(?:s|ive|ion)?\b',
    r'\bbenefi(?:t|ts|cial)\b',
    r'\bhelps? (?:you |people |your body )?(?:lose|reduce|lower|improve|prevent|protect|boost|burn|maintain|control|regulate|keep|build|manage)\b',
    r'\b(?:can|may|might|could) help\b', r'\bexperts?\b', r'\brecommend(?:s|ed|ation|ations)?\b',
    r'\bdoctors?\b', r'\bphysicians?\b', r'\bpediatricians?\b', r'\bclinicians?\b',
    r'\bhealth ?care (?:provider|professional|team)s?\b', r'\bprofessionals?\b', r'\bconsult(?:ing)?\b', r'\bsee a\b',
    r'\btalk (?:to|with) (?:your|a)\b', r'\bdietitians?\b',
]
TRIG = re.compile('|'.join(TRIGGERS), re.I)
ORGS = r'CDC|NIH|NHLBI|NIDDK|NCHS|WHO|ADA|NICE|USDA|HHS|FDA|USPSTF|AHA|ACC|NHS|IOM|NASEM|MedlinePlus|NLM|USPSTF|NCI'
CITE = re.compile(rf'\((?:[^()]*\b(?:{ORGS})\b[^()]*|[^()]*\bet al\.?,? \d{{4}}[^()]*|[^()]*[A-Z][a-z]+(?: and [A-Z][a-z]+)?,? (?:19|20)\d{{2}}[^()]*)\)')
BLOCK = re.compile(r'(?s)<(p|li|dd|dt|td|th|figcaption|h[2-4]|blockquote)\b[^>]*>(.*?)</\1>')
EXT = re.compile(r'<a\b[^>]*href="https?://')


def pages_from_sitemap():
    sm = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    out = []
    for loc in re.findall(r'<url><loc>https://calculatemybmi\.net(/[^<]*)</loc>', sm):
        out.append(loc)
    return out


def page_file(p):
    return ROOT / (p.strip('/') + '/index.html' if p != '/' else 'index.html')


def text(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()


def sentences(block_html):
    """Split a block's HTML into sentences, keeping each sentence's own HTML (to see its links)."""
    parts, cur = [], ''
    # split after . ! ? followed by space(s) and a capital letter or an opening tag, not after e.g./i.e./et al./a decimal
    toks = re.split(r'(?<=[.!?])(\s+)(?=(?:<[^>]+>)*[A-Z“"(])', block_html)
    for t in toks:
        if t is None:
            continue
        cur += t
        if re.search(r'[.!?]\s*$', text(cur)) and not re.search(r'\b(?:e\.g|i\.e|et al|vs|approx|No|Fig)\.\s*$', text(cur)):
            parts.append(cur)
            cur = ''
    if cur.strip():
        parts.append(cur)
    return parts


def probe(p, list_all=False):
    src = page_file(p).read_text(encoding='utf-8')
    m = re.search(r'(?s)<main\b.*?</main>', src)
    if not m:
        return []
    main = re.sub(r'(?s)<(script|style|svg)\b.*?</\1>', ' ', m.group(0))
    main = re.sub(r'(?s)<div class="calculator-card".*?<div class="key-takeaways"', '<div class="key-takeaways"', main)
    main = re.sub(r'(?s)<div class="disclaimer-box">.*?</div>', ' ', main)          # the site-wide disclaimer
    main = re.sub(r'(?s)<p\b[^>]*><strong>Medical [Dd]isclaimer:</strong>.*?</p>', ' ', main)   # the same, inline-styled
    hits = []
    for tag, inner in BLOCK.findall(main):
        if re.search(r'<(?:p|li|dd|td)\b', inner):           # a container of other blocks: its children are read on their own
            continue
        bt = text(inner)
        if not bt:
            continue
        block_src = bool(EXT.search(inner) or CITE.search(bt))
        for s in sentences(inner):
            st = text(s)
            mt = TRIG.search(st)
            if not mt:
                continue
            sourced = bool(EXT.search(s) or CITE.search(st))
            if list_all or not (sourced or block_src):
                hits.append({'tag': tag, 'trigger': mt.group(0), 'sentence': st, 'sourced': sourced, 'block_sourced': block_src})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pages')
    ap.add_argument('--json')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    pages = a.pages.split(',') if a.pages else pages_from_sitemap()
    reviewed = {}
    if REVIEWED.exists():
        for e in json.loads(REVIEWED.read_text(encoding='utf-8'))['entries']:
            reviewed[(e['page'], e['sentence'])] = e['why']
    res, total = {}, 0
    for p in pages:
        h = probe(p, a.all)
        for x in h:
            if not a.all and (p, x['sentence']) in reviewed:
                x['read'] = reviewed[(p, x['sentence'])]
        res[p] = h
        total += len(h)
    n_read = sum(1 for h in res.values() for x in h if x.get('read'))
    n_legal = sum(len(h) for p, h in res.items() if p in OUT_OF_SCOPE)
    for p, h in sorted(res.items(), key=lambda kv: -len(kv[1])):
        if not h:
            continue
        r = sum(1 for x in h if x.get('read'))
        note = ' (legal page, out of scope)' if p in OUT_OF_SCOPE else f' ({r} read and kept)' if r else ''
        print(f'{len(h):3d}  {p}{note}')
        for x in h:
            mark = ('[read] ' if x.get('read') else '') if not a.all else (
                '[S] ' if x['sourced'] else '[B] ' if x['block_sourced'] else '[ ] ')
            print(f'       {mark}<{x["tag"]}> ({x["trigger"]}) {x["sentence"][:220]}')
    print(f'{total} hits on {sum(1 for h in res.values() if h)} of {len(pages)} pages')
    if not a.all:
        print(f'{n_read} read and kept (reviewed.json), {n_legal} on the legal pages (out of scope), '
              f'{total - n_read - n_legal} to read')
        if not a.pages:
            seen = {(p, x['sentence']) for p, h in res.items() for x in h}
            stale = [k for k in reviewed if k not in seen]
            if stale:
                print(f'reviewed.json: {len(stale)} entries match no hit (the sentence changed or went; read again):')
                for p, st in stale:
                    print(f'       {p}  {st[:160]}')
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
