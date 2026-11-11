#!/usr/bin/env python3
"""CMB-029 STAGE1-AUDIT: every number on the 25 pages Stage 1 hasn't covered, classified and checked.

usage: python3 research/stage1-audit/audit.py BASE [--out DIR] [--pages /a/,/b/] [--list-unclassified]
       BASE = the served repo root, e.g. http://localhost:8000 (python3 -m http.server 8000)
       --out  where report.md and report.json go (default: this folder)

Needs Python Playwright and Chromium (cloud sessions: the preinstalled Chromium plus
`pip install playwright==1.63.0`). Requests to any host other than BASE's are aborted (ads, consent,
analytics), as in research/cmb-027/hub_examples_playwright.py. Viewport 390 x 844.

1. Collect (extract.js): every number a reader meets on each page, with its sentence: the text in <main>,
   table rows (each cell with its column header and the table's source line), <text> in SVG figures (with
   its position), FAQ questions and answers (collapsed or not) and their FAQPage JSON-LD, the <title> and
   the meta description. A results panel's static text counts too (a reader meets it after Calculate).
   Excluded (class X: counted, not audited): the byline and its dates (the legal pages' Effective / Last
   updated line counts as theirs), list numbering ("1.", "Step 2", "Mistake 3", "#7", "Section 6", "(1)",
   numbered badges), the operator's address, and numbers inside URLs, DOIs and PMC ids. Form controls are
   not read: their numbers are inputs, not claims.

2. Classify every number: manual.json first, then the rules; a number neither covers is UNCLASSIFIED and
   fails the run.
   A  calculator claim: what a calculator gives for given inputs (a person's worked example). The inputs
      are typed into that calculator at 390 px (US units or metric, as the example gives them) and every
      number and category the claim states is compared with what the calculator prints. Category words
      must match the calculator's wording (the CMB-027 rule: "Normal" is not "Healthy weight").
   B  our arithmetic: a value the site's formulas decide. Recomputed in the audited page with calculator.js's
      own functions (helpers.js; calculator.js is injected where the page doesn't load it): calculateBMI,
      round1, getBMICategory, weightBounds, lbsToKg / kgToLbs / inchesToCm, heightToFtIn, getLMSRow,
      stdNormalInv and categorizeChildBMI (kids page), calculateLBM through its own panel (LBM page), the
      New BMI and Boer constants in calculateNewBMI's and calculateLBM's source. Arithmetic the page writes
      out ("70 x 70 = 4,900", "a = b = c" chains, a ratio, a percent of a weight, a rank or a change in a data
      table) is evaluated in the page as written. Values round once, half up (round1's 1e-9 nudge), to the
      precision the page prints; an exact half is noted. Category cut-offs: each bound is asked of
      getBMICategory (adults) or categorizeChildBMI (children), with the value one step outside it, and the
      categories a range covers must sit inside the category the page names. Names are compared as
      categories here (WHO's "Normal" = calculator.js's "Healthy weight"); names that differ are listed.
   C  outside fact: a statistic, cut-off, threshold, study result or year that comes, or should come, from a
      source. Matched to research/data-sources.csv: the row the sentence links to (url or endpoint; for a
      table cell, the table's links and source line), else the row manual.json names for it, else the row
      the sentence names (first author, report number, BRFSS), else the page's own data_source row
      (research/page-map.csv, when it names a registry row; CMB-031) when its dataset holds the number at the
      precision the page prints, or its sample_note or notes hold it (a distinctive number or a year), else the
      rows the registry says serve the page (pages_served; a number none of them holds is "not in its row"
      against the page's own row when that row serves the page), else a row whose sample_note holds a
      distinctive number (a decimal or 4+ digits), else a row the paragraph links to that holds the number.
      Status:
        row          the number is in that row's sample_note (a year may sit in its source or domain)
        row-notes    it is only in the row's notes column
        row-dataset  it is in the dataset the registry says the row serves: cdc-brfss-state-obesity, the
                     2011-2025 state CSVs (cell by state, year and age group); nhanes-2021-2023-exam-files and
                     nhanes-anthropometric-reference, avgw_results.json (written by the compute.py the first
                     row's sample_note names; the age tables cell by sex, age group and measure);
                     cdc-extended-bmi-data, data/cdc/bmi-age-2022.csv at the precision the page prints (CMB-031):
                     a table cell by sex (the caption), birthday row (age x 12 + 0.5 months) and column (5th,
                     50th, 85th, 95th, 120% of 95th), the header's columns and the row ages; in prose, a value of
                     the column the sentence (or its FAQ question or paragraph) names, for the sex and the ages
                     it names, and a whole number of months the file has a row for; any other value only when
                     printed to 4 or more decimals or exactly as the file has it (at 0.1 a BMI matches some cell
                     of the 13,000-value file by chance)
        not-in-row   a row is identified but holds no such number ("differs from its row"). Two notes, which
                     change no status: "also in", the other rows whose sample_note or notes hold the same
                     number (3+ significant digits) with two others of the sentence (or its only other) within
                     60 characters; "in the page's CSV", the
                     number is in a CSV the page links for download whose comment line cites the row's url (the
                     page agrees with its own data file; the check against the source is still open)
        no-row       no registry row; the sentence and the link next to it are reported
   D  other: counts in prose ("four formulas"), number words, names and labels with numbers ("Type 2
      diabetes", "Class 1 obesity", "Data Brief 508"), citation details (volume, pages, PMID), axis ticks,
      phone numbers, the legal pages' own terms (30 days), labelled illustrations.

3. Report (report.md, report.json): per page the totals by class, every A and B mismatch (page value,
   computed value, sentence), every C with no row (quoted, with its link), every C not in its row; pages
   sorted by A+B mismatches plus C with no row, worst first; at the top the 10 worst pages and the no-row
   claims that repeat on 2 or more pages (same number and unit in sentences that share their wording).

Exit 0 when all pages were read, every number is classified and every A/B check ran (mismatches are the
findings, not failures); 1 otherwise.
"""
import argparse
import csv
import html
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
VIEWPORT = {'width': 390, 'height': 844}
PAGES = [
    '/about/', '/contact/', '/privacy/', '/terms/', '/blog/', '/age-bmi-calculator/', '/kids-bmi-calculator/',
    '/lean-body-mass/', '/obesity-rate-by-state/', '/childhood-obesity-statistics/', '/blog/what-is-bmi/',
    '/blog/bmi-formula/', '/blog/bmi-history/', '/blog/bmi-categories/', '/blog/bmi-chart-explained/',
    '/blog/bmi-and-health-risks/', '/blog/underweight-bmi-risks/', '/blog/bmi-limitations/',
    '/blog/bmi-and-metabolism/', '/blog/body-fat-vs-bmi/', '/blog/bmi-for-athletes/',
    '/blog/waist-to-height-ratio/', '/blog/how-to-lower-bmi/', '/blog/bmi-tracking-guide/', '/blog/bmi-by-age/',
]
EXTRACT_JS = (HERE / 'extract.js').read_text(encoding='utf-8')
HELPERS_JS = (HERE / 'helpers.js').read_text(encoding='utf-8')

# ----------------------------------------------------------------------------------------------------
# text: one-to-one normalisation (positions stay aligned with the page's own text), sentences, numbers
# ----------------------------------------------------------------------------------------------------
NORM1 = str.maketrans({' ': ' ', ' ': ' ', ' ': ' ', ' ': ' ', ' ': ' ', ' ': ' ',
                       '’': "'", '‘': "'", '′': "'", '″': '"', '“': '"', '”': '"',
                       '–': '-', '—': '-', '−': '-', '‐': '-', '‑': '-', '×': 'x',
                       '÷': '/', '≈': '~', '→': '>'})


def squash(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def norm1(s):
    return (s or '').translate(NORM1)


NUM_RX = re.compile(r'(?<![A-Za-z0-9_.])(?P<n>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?P<o>st|nd|rd|th)?'
                    r'(?P<g>kg|lbs|lb|cm|mm|ft|hrs|hr|h|min|mg|g|kcal|cal|M|B|K|k|x|X|s)?(?![A-Za-z0-9_])')
WORDS = ('two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen '
         'eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred hundreds thousand thousands '
         'million millions billion billions dozen dozens half twice').split()
WORD_VAL = {w: v for v, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen '
                                       'fourteen fifteen sixteen seventeen eighteen nineteen'.split())}
WORD_VAL.update({'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
                 'ninety': 90, 'hundred': 100, 'hundreds': 100, 'thousand': 1000, 'thousands': 1000,
                 'million': 1e6, 'millions': 1e6, 'billion': 1e9, 'billions': 1e9, 'dozen': 12, 'dozens': 12,
                 'half': 0.5, 'twice': 2})
NUMWORD_RX = re.compile(r'\b(' + '|'.join(WORDS) + r'|one-(?:third|quarter|fifth|tenth)|two-thirds|three-quarters'
                        r'|one in (?:two|three|four|five|six|seven|eight|nine|ten))\b', re.I)
MULT = {'million': 1e6, 'millions': 1e6, 'billion': 1e9, 'thousand': 1e3}
ABBREV = {'e.g', 'i.e', 'al', 'vs', 'approx', 'dr', 'no', 'vol', 'fig', 'st', 'jr', 'sr', 'u.s', 'etc', 'cf', 'ca',
          'inc', 'ltd', 'co', 'd.o.o', 'mr', 'mrs', 'ms', 'prof', 'art', 'p', 'pp', 'ed', 'eds', 'nouv', 'mém', 'acad',
          'roy', 't', 'ref', 'est', 'min', 'max', 'sec', 'ch', 'nos', 'jan', 'feb', 'mar', 'apr', 'aug', 'sep', 'sept',
          'oct', 'nov', 'dec', 'u.k', 'wt', 'ht', 'resp', 'dept', 'univ', 'assoc', 'natl', 'med', 'clin', 'nutr', 'res',
          'j', 'am', 'int', 'obes', 'metab', 'endocrinol', 'epidemiol', 'mph', 'lbs', 'lb', 'kg', 'cm', 'in', 'ft'}


def sentences(text):
    """Split a unit's text into sentences; returns (start, end) spans in text."""
    t = norm1(text)
    out, start = [], 0
    for m in re.finditer(r'(?<=[.!?])["\')\]]*\s+(?=["(\[]?[A-Z0-9])|\n+', t):
        end = m.start()
        if '\n' not in m.group(0):
            before = t[start:end]
            w = re.search(r'([A-Za-zÀ-ÿ.]+)\.$', before)
            if w and (w.group(1).lower().rstrip('.') in ABBREV or re.fullmatch(r'[A-Z]', w.group(1))):
                continue
            if re.fullmatch(r'\s*\d{1,2}\.', before):        # "1. What actually runs": a list number, not a sentence
                continue
            if re.search(r'\d\.$', before) and re.match(r'\s+\d', t[m.start():]):
                continue
        if t[start:end].strip():
            out.append((start, end))
        start = m.end()
    if t[start:].strip():
        out.append((start, len(t)))
    return out


class Tok:
    __slots__ = ('text', 'value', 'dec', 'start', 'end', 'pre', 'suf', 'kind', 'cell', 'cls', 'why', 'check',
                 'result', 'row', 'ord', 'glued', 'idx')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


def tokenize(t, cells=None):
    """Numbers (digits, with their decimals) and number words in normalised text t."""
    toks = []
    for m in NUM_RX.finditer(t):
        n = m.group('n')
        val = float(n.replace(',', ''))
        dec = len(n.split('.')[1]) if '.' in n else 0
        g = m.group('g') or ''
        if g in ('M', 'B', 'K', 'k'):
            val *= {'M': 1e6, 'B': 1e9, 'K': 1e3, 'k': 1e3}[g]
        toks.append(Tok(text=m.group(0), value=val, dec=dec, start=m.start(), end=m.end(), kind='num',
                        ord=m.group('o') or '', glued=g))
    for m in NUMWORD_RX.finditer(t):
        w = m.group(1).lower()
        prev = [k for k in toks if k.kind == 'num' and 0 <= m.start() - k.end <= 1]
        if w in MULT and prev:          # "2.88 million": the word multiplies the digits before it
            p = prev[0]
            p.value *= MULT[w]
            p.text = t[p.start:m.end()]
            p.end = m.end()
            continue
        toks.append(Tok(text=m.group(0), value=WORD_VAL.get(re.split(r'[- ]', w)[0], 0), dec=0, start=m.start(),
                        end=m.end(), kind='word', ord='', glued=''))
    toks.sort(key=lambda k: k.start)
    for i, k in enumerate(toks):
        k.idx = i
        k.pre = t[max(0, k.start - 30):k.start]
        k.suf = t[k.end:k.end + 30]
        if cells is not None:
            k.cell = cell_of(cells, k.start)
    return toks


def cell_of(cells, pos):
    at = 0
    for i, c in enumerate(cells):
        if pos < at + len(c):
            return i
        at += len(c) + 3
    return len(cells) - 1


def signature(t):
    """Number-blind sentence key for manual.json: every digit run becomes #."""
    s = norm1(squash(t))
    return re.sub(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?', '#', s)


def half_up(x, dec):
    """Round once, half up, with round1()'s 1e-9 nudge so float noise doesn't decide an exact half."""
    if not isinstance(x, (int, float)) or isinstance(x, bool) or math.isnan(x) or math.isinf(x):
        return None
    f = 10.0 ** dec
    v = math.floor(abs(x) * f + 0.5 + 1e-9) / f
    return -v if x < 0 else v


def fmt(x, dec):
    if not isinstance(x, (int, float)) or x is None:
        return str(x)
    return f'{x:.{max(dec, 0)}f}'


# ----------------------------------------------------------------------------------------------------
# a sentence: the unit it came from, its numbers, the links next to it
# ----------------------------------------------------------------------------------------------------
class Sent:
    def __init__(self, page, unit, raw, uid, sid, region=None):
        self.page, self.unit, self.uid, self.sid = page, unit, uid, sid
        self.raw = squash(raw)
        self.t = norm1(self.raw)
        self.region = region or unit.get('region', 'main')
        self.cells = [norm1(squash(c)) for c in unit.get('cells')] if self.region == 'table' else None
        self.toks = tokenize(self.t, self.cells)
        self.sig = signature(self.raw)
        self.links = []
        self.mirror = None      # a JSON-LD answer equal to a visible FAQ answer points at the visible sentence
        self.manual_row = None  # a registry domain manual.json gives this sentence's C numbers

    def head(self):
        return self.unit.get('heading', '')

    def ctx(self):
        u = self.unit
        return ' '.join(x for x in (u.get('heading', ''), u.get('caption', ''), u.get('ctx', ''), u.get('svgLabel', ''),
                                    u.get('figcaption', ''), u.get('question', ''), ' | '.join(u.get('colHead') or []),
                                    u.get('note', '')) if x)

    def free(self, i):
        return i is not None and 0 <= i < len(self.toks) and self.toks[i].cls is None

    def assign(self, i, cls, why, check=None):
        if i is None or i >= len(self.toks):
            return False
        k = self.toks[i]
        if k.cls is None:
            k.cls, k.why, k.check = cls, why, check
            return True
        return False

    def at(self, start, end=None):
        for k in self.toks:
            if k.start == start or (end is not None and start <= k.start < end):
                return k.idx
        return None

    def tok_in(self, m, g):
        if m.group(g) is None:
            return None
        return self.at(m.start(g), m.end(g))


def job(adds, s, i):
    if i is not None:
        adds.append((s, i))


# ----------------------------------------------------------------------------------------------------
# exclusions (class X): byline dates, list numbering, the address, numbers inside URLs
# ----------------------------------------------------------------------------------------------------
URLISH = re.compile(r'(?:https?://|www\.)\S+|\bdoi:\s?\S+|\b10\.\d{4,}/\S+|\bPMC\d+|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*'
                    r'\.(?:gov|org|com|net|edu|int|uk|si|io)(?:/\S*)?', re.I)
NUMBERING_WORD = re.compile(r'\b(Step|Steps|Mistake|Tip|Limitation|Method|Option|Section|Sections|Phase|Rule|Myth|'
                            r'Reason|Question|Part|Strategy|Category|Scenario|Example)\s+#?$')


def exclusions(s, badges):
    t = s.t
    for m in URLISH.finditer(t):
        for k in s.toks:
            if m.start() <= k.start < m.end():
                s.assign(k.idx, 'X', 'number inside a URL or DOI')
    for m in re.finditer(r'Smolnik (\d+), (\d+) Ruse', t):
        for g in (1, 2):
            s.assign(s.tok_in(m, g), 'X', 'address')
    if s.page in ('/privacy/', '/terms/') and re.match(r'(Effective|Last updated)', t, re.I):
        for k in s.toks:
            s.assign(k.idx, 'X', 'byline date (the legal page\'s Effective / Last updated line)')
    if s.region in ('main', 'faq-a') and s.sid == 0:
        m = re.match(r'\s*(\d{1,2}(?:\.\d{1,2})?)\.?(?:\s+\S|\s*$)', t)
        if m and (s.unit.get('tag', '') in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') or re.match(r'\s*\d{1,2}[.)](?:\s|$)', t)):
            s.assign(s.at(m.start(1)), 'X', 'list numbering')
    for k in s.toks:
        if k.kind != 'num':
            continue
        if re.search(r'#\s?$', k.pre) or NUMBERING_WORD.search(k.pre):
            s.assign(k.idx, 'X', 'list numbering')
        elif k.value < 10 and re.search(r'(?<![\w)])\($', k.pre) and k.suf.startswith(')') and len(re.findall(r'(?<![\w)])\(\d\)', t)) >= 2:
            s.assign(k.idx, 'X', 'list numbering')
    if (s.page, s.uid) in badges:
        for k in s.toks:
            s.assign(k.idx, 'X', 'list numbering (numbered badge)')


def numbered_badges(page, sents):
    """Units whose whole text is a small integer, grouped by class and tag, counting 1, 2, 3 ...: step badges."""
    groups = defaultdict(list)
    for s in sents:
        if s.sid == 0 and s.region in ('main', 'faq-a') and re.fullmatch(r'\s*\d{1,2}\.?\s*', s.unit.get('text', '')):
            groups[(s.unit.get('cls', ''), s.unit.get('tag', ''))].append((s.uid, int(re.sub(r'\D', '', s.unit['text']))))
    out = set()
    for items in groups.values():
        vals = sorted(v for _, v in items)
        if len(vals) >= 2 and vals[0] == 1 and all(b - a in (0, 1) for a, b in zip(vals, vals[1:])):
            out.update((page, u) for u, _ in items)
    return out


# ----------------------------------------------------------------------------------------------------
# B: category cut-offs (adult BMI categories and child percentile categories)
# ----------------------------------------------------------------------------------------------------
CALC_NAMES = ['Severe thinness', 'Moderate thinness', 'Underweight', 'Healthy weight', 'Overweight',
              'Class 1 obesity', 'Class 2 obesity', 'Class 3 obesity']
UW = ['Severe thinness', 'Moderate thinness', 'Underweight']
OB = ['Class 1 obesity', 'Class 2 obesity', 'Class 3 obesity']
GROUPS = {  # category phrases on the pages -> the calculator.js categories they cover
    'moderate to severe underweight': ['Severe thinness', 'Moderate thinness'], 'moderate to severe thinness': ['Severe thinness', 'Moderate thinness'],
    'severe thinness': ['Severe thinness'], 'severely underweight': ['Severe thinness'], 'severe underweight': ['Severe thinness'],
    'grade 3 thinness': ['Severe thinness'], 'grade 3 underweight': ['Severe thinness'],
    'moderate thinness': ['Moderate thinness'], 'moderate underweight': ['Moderate thinness'],
    'grade 2 thinness': ['Moderate thinness'], 'grade 2 underweight': ['Moderate thinness'],
    'mild thinness': ['Underweight'], 'mild underweight': ['Underweight'], 'grade 1 thinness': ['Underweight'],
    'grade 1 underweight': ['Underweight'],
    'underweight': UW, 'thinness': UW,
    'healthy weight': ['Healthy weight'], 'normal weight': ['Healthy weight'], 'normal range': ['Healthy weight'],
    'healthy range': ['Healthy weight'], 'healthy bmi': ['Healthy weight'], 'normal': ['Healthy weight'],
    'healthy': ['Healthy weight'], 'healthy-weight': ['Healthy weight'],
    'overweight or obese': ['Overweight'] + OB, 'overweight or obesity': ['Overweight'] + OB,
    'overweight': ['Overweight'], 'pre-obese': ['Overweight'],
    'obese class i-ii': ['Class 1 obesity', 'Class 2 obesity'], 'class i-ii': ['Class 1 obesity', 'Class 2 obesity'],
    'obese class iii': ['Class 3 obesity'], 'obese class ii': ['Class 2 obesity'], 'obese class i': ['Class 1 obesity'],
    'obese iii': ['Class 3 obesity'], 'obese ii+': ['Class 2 obesity', 'Class 3 obesity'],
    'obese ii': ['Class 2 obesity'], 'obese i': ['Class 1 obesity'],
    'class iii obesity': ['Class 3 obesity'], 'class ii obesity': ['Class 2 obesity'], 'class i obesity': ['Class 1 obesity'],
    'class 3 obesity': ['Class 3 obesity'], 'class 2 obesity': ['Class 2 obesity'], 'class 1 obesity': ['Class 1 obesity'],
    'obesity class 3': ['Class 3 obesity'], 'obesity class 2': ['Class 2 obesity'], 'obesity class 1': ['Class 1 obesity'],
    'obesity, class 3': ['Class 3 obesity'], 'obesity, class 2': ['Class 2 obesity'], 'obesity, class 1': ['Class 1 obesity'],
    'class iii': ['Class 3 obesity'], 'class ii': ['Class 2 obesity'], 'class i': ['Class 1 obesity'],
    'class 3': ['Class 3 obesity'], 'class 2': ['Class 2 obesity'], 'class 1': ['Class 1 obesity'],
    'grade 3 obesity': ['Class 3 obesity'], 'grade 2+ obesity': ['Class 2 obesity', 'Class 3 obesity'],
    'grade 2 obesity': ['Class 2 obesity'], 'grade 1 obesity': ['Class 1 obesity'],
    'grade 2-3 obesity': ['Class 2 obesity', 'Class 3 obesity'], 'grades 2 and 3 obesity': ['Class 2 obesity', 'Class 3 obesity'],
    'grade 2+': ['Class 2 obesity', 'Class 3 obesity'], 'obese ii-iii': ['Class 2 obesity', 'Class 3 obesity'],
    'severe obesity': ['Class 3 obesity'], 'extreme obesity': ['Class 3 obesity'], 'morbid obesity': ['Class 3 obesity'],
    'obesity': OB, 'obese': OB,
}
CAT_RX = re.compile(r'(?<![A-Za-z])(' + '|'.join(sorted((re.escape(k) for k in GROUPS), key=len, reverse=True)) + r')(?![a-z])', re.I)
UW_RX = re.compile(r'\b(mild|moderate|severe)\b(?!\s*(?:obes|risk|-?intensity|activity|exercise|thinness|underweight))', re.I)
CUTS = {16, 16.9, 16.99, 17, 18.4, 18.49, 18.5, 24.9, 24.99, 25, 29.9, 29.99, 30, 34.9, 34.99, 35, 39.9, 39.99, 40}
BOUNDARIES = {16, 17, 18.5, 25, 30, 35, 40}
BMI_WORDS = re.compile(r'\bBMI\b|kg/m|underweight|thinness|normal|healthy|overweight|obes|class [123i]|grade [123]', re.I)
NOT_ADULT_CUTS = re.compile(r'\b(Asian|ethnic|Black|Chinese|Japanese|Indian|NICE|DPP|percentile|waist|WHtR|'
                            r'waist-to-height|children|kids|teens?)\b', re.I)


def cat_group(phrase):
    p = re.sub(r'\s+', ' ', (phrase or '').lower()).strip().strip('"\'')
    if p in ('mild', 'moderate', 'severe'):
        p += ' thinness'
    return GROUPS.get(p) or GROUPS.get(p.rstrip('+').strip())


def cat_candidates(t, uw):
    out = [(m.start(1), m.end(1), m.group(1)) for m in CAT_RX.finditer(t)]
    if uw:
        for m in UW_RX.finditer(t):
            if not any(a <= m.start(1) < b for a, b, _ in out):
                out.append((m.start(1), m.end(1), m.group(1)))
    return out


def nearest(cands, a, b, t=None, limit=None):
    """The category phrase closest to [a, b); with t, not across "and" / "than" / "to" and within limit characters."""
    best = None
    for x, y, ph in cands:
        if x < b and y > a:
            continue
        d = x - b if x >= b else a - y
        if t is not None:
            between = t[b:x] if x >= b else t[y:a]
            if re.search(r'\b(and|than|to|from|vs)\b', between, re.I) or (limit is not None and d > limit):
                continue
        if best is None or d < best[0]:
            best = (d, ph)
    return best


def assoc_category(s, a, b):
    """The category a range at [a, b) of s.t belongs to: same table cell, then the row; else the same clause;
    else, for a short legend label, the category named right next to it in its container."""
    t = s.t
    uw = bool(re.search(r'underweight|thinness', t + ' ' + s.ctx(), re.I))
    if s.region == 'table' and s.cells:
        i = s.at(a, b)
        cell = s.toks[i].cell if i is not None else 0
        offs, at = [], 0
        for c in s.cells:
            offs.append(at)
            at += len(c) + 3
        head = [norm1(h) for h in (s.unit.get('colHead') or [])]
        if cell < len(head) and not cat_candidates(s.cells[cell], uw):
            hc = cat_candidates(head[cell], uw)
            if hc:
                return hc[0][2]
        for ci in [cell] + [j for j in range(len(s.cells)) if j != cell]:
            cands = cat_candidates(s.cells[ci], uw)
            if not cands:
                continue
            if ci == cell:
                best = nearest(cands, a - offs[ci], b - offs[ci])
                if best:
                    return best[1]
            else:
                return cands[0][2]
        return None
    clause = next(((m.start(), m.end()) for m in re.finditer(r'[^,;|]+', t) if m.start() <= a < m.end()), (0, len(t)))
    cands = [c for c in cat_candidates(t, uw) if clause[0] <= c[0] < clause[1]]
    best = nearest(cands, a, b, t, 28)
    if best:
        return best[1]
    if len(t) < 60 and s.unit.get('ctx'):
        ctx = norm1(s.unit['ctx'])
        me = t.strip()
        pos = ctx.find(me)
        if pos >= 0:
            lo, hi = max(0, pos - 40), min(len(ctx), pos + len(me) + 40)
            cands = []
            for x, y, ph in cat_candidates(ctx[lo:hi], uw):
                x, y = x + lo, y + lo
                between = ctx[y:pos] if y <= pos else ctx[pos + len(me):x]
                if not re.search(r'\d', between):
                    cands.append((x, y, ph))
            best = nearest(cands, pos, pos + len(me))
            if best:
                return best[1]
    return None


RANGE_PATTERNS = [
    (re.compile(r'(?P<lo>\d+(?:\.\d+)?)\s*(?:-|to|up to)\s*(?:under|less than|<|below)\s*(?:the\s*)?(?P<hx>\d+(?:\.\d+)?)', re.I), 'lo-hx'),
    (re.compile(r'(?<![\d.])(?P<lo>\d+(?:\.\d+)?)\s*(?:-|to)\s*(?P<hi>\d+(?:\.\d+)?)(?!\s*(?:%|lb|kg|cm|in\b|inch|years?|months?|"|\'|th\b|percent))', re.I), 'lo-hi'),
    (re.compile(r'(?:below|under|less than|<|lower than)\s*(?:a\s+)?(?:BMI\s+)?(?:of\s+)?(?P<hx>\d+(?:\.\d+)?)', re.I), 'hx'),
    (re.compile(r'(?:≥|>=|at least|at or above|greater than or equal to)\s*(?:a\s+)?(?:BMI\s+)?(?:of\s+)?(?P<lo>\d+(?:\.\d+)?)', re.I), 'lo'),
    (re.compile(r'(?P<lo>\d+(?:\.\d+)?)\s*(?:\+|or (?:higher|more|above|over|greater)|and (?:above|over|higher|up))', re.I), 'lo'),
    (re.compile(r'(?:>|more than|greater than)\s*(?:a\s+)?(?:BMI\s+)?(?:of\s+)?(?P<lx>\d+(?:\.\d+)?)', re.I), 'lx'),
]


def cutoff_rules(s, adds):
    """Adult BMI category ranges: each bound is asked of getBMICategory, with the value one step outside it."""
    t = s.t
    if not BMI_WORDS.search(t + ' ' + s.ctx()) or NOT_ADULT_CUTS.search(t):
        return
    used = set()
    for rx, kind in RANGE_PATTERNS:
        for m in rx.finditer(t):
            gs = [g for g in ('lo', 'hi', 'hx', 'lx') if g in rx.groupindex and m.group(g)]
            idx = {g: s.tok_in(m, g) for g in gs}
            if any(i is None or i in used or not s.free(i) for i in idx.values()):
                continue
            vals = {g: float(m.group(g)) for g in gs}
            if not all(v in CUTS for v in vals.values()):
                continue
            if 'lo' in vals and 'hi' in vals and vals['lo'] > vals['hi']:
                continue   # "BMI 30 to 25" is a change, not a range
            if any(re.match(r'\s*(%|lb|kg(?!/m)|cm|in\b|inch|year|month|week|day|hour|minute)', s.toks[i].suf) for i in idx.values()):
                continue
            phrase = assoc_category(s, m.start(), m.end())
            names = cat_group(phrase) if phrase else None
            if not names:
                # no category named next to it: still a cut-off when every bound is where a category starts or ends
                if not (re.search(r'\bBMI\b', t + ' ' + s.ctx()) and all(v in BOUNDARIES or round(v + 0.1, 1) in BOUNDARIES for v in vals.values())):
                    continue
                phrase = None
            used.update(idx.values())
            check = {'kind': 'cut', 'names': names, 'phrase': phrase, 'bounds': vals, 'toks': idx}
            ids = list(idx.values())
            s.assign(ids[0], 'B', 'category cut-off', check)
            for i in ids[1:]:
                s.assign(i, 'B', 'category cut-off (other bound)')
            job(adds, s, ids[0])


KIDS_CATS = {'underweight': ['Underweight'], 'healthy': ['Healthy weight'], 'healthy weight': ['Healthy weight'],
             'normal': ['Healthy weight'], 'overweight': ['Overweight'], 'obese': ['Obesity', 'Severe obesity'],
             'obesity': ['Obesity', 'Severe obesity'], 'severe obesity': ['Severe obesity']}
KIDS_CAT_RX = re.compile(r'\b(severe obesity|healthy[- ]weight|underweight|healthy|normal|overweight|obesity|obese)\b', re.I)


def kids_cutoff_rules(s, adds):
    """Child percentile categories, asked of categorizeChildBMI (percentile, % of the 95th, BMI)."""
    t = s.t
    both = t + ' ' + s.ctx()
    kid = s.page == '/kids-bmi-calculator/' or re.search(r'child|kids|teen|pediatric|growth chart|BMI-for-age', both, re.I)
    if not kid or not re.search(r'\d+(?:st|nd|rd|th)\b|percentile|%ile', both, re.I):
        return
    pats = [
        (r'(?P<p95>\d+)%\s*of the\s*(?P<ref>95)th', 'p95'),
        (r'(?P<lo>\d+)(?:st|nd|rd|th)?\s*(?:percentile\s*)?(?:-|to)\s*(?:less than|under|below|just under)\s*(?:the\s*)?(?P<hx>\d+)(?:st|nd|rd|th)', 'lo-hx'),
        (r'(?P<lo>\d+)(?:st|nd|rd|th)?\s*(?:-|to)\s*(?:the\s*)?(?P<hi>\d+)(?:st|nd|rd|th)', 'lo-hi'),
        (r'(?:<|below|under|less than)\s*(?:the\s*)?(?P<hx>\d+)(?:st|nd|rd|th)', 'hx'),
        (r'(?:≥|>=|at or above|at least)\s*(?:the\s*)?(?P<lo>\d+)(?:st|nd|rd|th)', 'lo'),
        (r'(?P<lo>\d+)(?:st|nd|rd|th)\s*(?:percentile\s*)?(?:or (?:higher|above|more)|and (?:above|over|up))', 'lo'),
        (r'BMI\s*(?:of\s*)?(?P<bmi>35)\b\+?', 'bmi'),
    ]
    used = set()
    for rx, kind in pats:
        for m in re.finditer(rx, t, re.I):
            gs = [g for g in ('lo', 'hi', 'hx', 'p95', 'bmi', 'ref') if g in m.re.groupindex and m.group(g)]
            idx = {g: s.tok_in(m, g) for g in gs}
            if any(i is None or i in used or not s.free(i) for i in idx.values()):
                continue
            vals = {g: float(m.group(g)) for g in gs}
            if kind == 'bmi' and not (vals['bmi'] == 35 and re.search(r'severe', t, re.I)):
                continue
            if kind not in ('bmi',) and not all(v in (5, 84, 85, 94, 95, 120) for v in vals.values()):
                continue
            vals.pop('ref', None)
            if kind in ('p95', 'bmi'):
                phrase = 'severe obesity'
            elif s.region == 'table' and s.cells:
                cands = [x.group(1) for c in s.cells for x in KIDS_CAT_RX.finditer(c)]
                phrase = cands[0] if cands else None
            else:
                clause = next(((x.start(), x.end()) for x in re.finditer(r'[^;|,]+', t) if x.start() <= m.start() < x.end()), (0, len(t)))
                cands = [(x.start(1), x.end(1), x.group(1)) for x in KIDS_CAT_RX.finditer(t) if clause[0] <= x.start(1) < clause[1]]
                best = nearest(cands, m.start(), m.end())
                phrase = best[1] if best else None
                if phrase is None and len(t) < 40 and s.unit.get('ctx'):
                    ctx = norm1(s.unit['ctx'])
                    pos = ctx.find(t.strip())
                    if pos >= 0:
                        found = list(KIDS_CAT_RX.finditer(ctx[max(0, pos - 30):pos]))
                        phrase = found[-1].group(1) if found else None
            if not phrase:
                continue
            names = KIDS_CATS.get(phrase.lower().replace('-', ' '))
            if not names:
                continue
            used.update(idx.values())
            check = {'kind': 'kcut', 'names': names, 'phrase': phrase, 'bounds': vals, 'toks': idx}
            ids = list(idx.values())
            s.assign(ids[0], 'B', 'child category cut-off', check)
            for i in ids[1:]:
                s.assign(i, 'B', 'child category cut-off (other bound)')
            job(adds, s, ids[0])


THRESH = re.compile(r'cut-?offs?|thresholds?|cut-?points?|boundar|\bBMI line|\d+(?:\.\d+)? for (?:underweight|overweight|obes)|^Why \d', re.I)


def threshold_rule(s, adds):
    """'cut-offs of 25 and 30', '18.5 for underweight, 25 for overweight', 'the 25 BMI line': a value where
    getBMICategory changes category."""
    t = s.t
    if not THRESH.search(t) or not BMI_WORDS.search(t + ' ' + s.ctx()) or NOT_ADULT_CUTS.search(t):
        return
    for k in s.toks:
        if s.free(k.idx) and k.kind == 'num' and k.value in BOUNDARIES and not re.match(r'\s?(%|lb|kg|cm|in\b|years?|-year)', k.suf):
            s.assign(k.idx, 'B', 'category cut-off', {'kind': 'boundary', 'value': k.value, 'target': k.idx,
                                                      'label': 'getBMICategory changes category at this value'})
            job(adds, s, k.idx)


def kids_range_rule(s, adds):
    """'ages 2-19' said of the kids calculator or CDC's BMI-for-age charts: calculateKids takes 24 to 239 months."""
    t = s.t
    if '%' in t:
        return
    for m in re.finditer(r'\b(?:ages?|aged|teens|children)\s*(?:\(\s*ages?\s*)?(?P<a>2)\s*(?:-|to|through)\s*(?P<b>19)\b', t, re.I):
        ia, ib = s.tok_in(m, 'a'), s.tok_in(m, 'b')
        if not (s.free(ia) and s.free(ib)):
            continue
        s.assign(ia, 'B', 'the calculator\'s age range', {'kind': 'src', 'fn': 'calculateKids', 'has': 'agemos < 24 || agemos >= 240', 'target': ia,
                                                         'label': 'calculateKids accepts 24 to 239 months (2 to 19 years 11 months)'})
        s.assign(ib, 'B', 'the calculator\'s age range (other end)')
        job(adds, s, ia)


SRCNUM_JS_FNS = {'LBM': 'calculateLBM'}


def formula_source_rule(s, adds):
    """A lean body mass formula written out ('LBM = 0.407 x W + 0.267 x H - 19.2'): each constant must be a number
    literal in calculateLBM's own source."""
    t = s.t
    if not re.search(r'\bLBM\s*=|coefficient', t):
        return
    if re.search(r'LBM\s*=\s*[\d.]+\s*(?:\+|-)\s*[\d.]+\s*(?:\+|-)', t) or re.search(r'LBM\s*=\s*[\d.]+\s*kg', t):
        return   # the worked example's sums and results, not the formula
    for k in s.toks:
        if not s.free(k.idx) or k.kind != 'num':
            continue
        if k.dec == 0 and k.value == 2 and re.search(r'\)\s*\^\s*$|\)\s*\^$', k.pre):
            s.assign(k.idx, 'B', 'formula exponent (squared, as calculateLBM multiplies the ratio by itself)')
            continue
        if re.search(r'(x|\*)\s*$', k.pre) and not re.match(r'\s*(x|\*)', k.suf) and not re.search(r'\d\s*(x|\*)\s*$', k.pre):
            continue   # an input (81.6 in "0.407 x 81.6"), left to the other rules
        s.assign(k.idx, 'B', 'formula constant', {'kind': 'srcnum', 'fn': 'calculateLBM', 'target': k.idx,
                                                  'label': 'a number literal in calculateLBM'})
        job(adds, s, k.idx)


def category_label_rules(s, adds):
    """'BMI 24.9 ("normal") and 25.0 ("overweight")': the category of a stated BMI, asked of getBMICategory."""
    t = s.t
    if not BMI_WORDS.search(t) or NOT_ADULT_CUTS.search(t):
        return
    for m in re.finditer(r'(?<![\d.-])(?P<v>\d{2}(?:\.\d)?)\s*\(\s*"?(?P<c>[A-Za-z][A-Za-z +-]*?)"?\s*\)', t):
        i = s.tok_in(m, 'v')
        names = cat_group(m.group('c'))
        if not s.free(i) or not names or not 10 <= float(m.group('v')) <= 70:
            continue
        s.assign(i, 'B', 'category of a BMI', {'kind': 'catname', 'expr': f'__A.cat({m.group("v")})', 'text': m.group('c'),
                                               'target': i, 'label': 'category of that BMI (getBMICategory)'})
        job(adds, s, i)


# ----------------------------------------------------------------------------------------------------
# heights and weights; a BMI for a height and a weight (A for a person's worked example, else B)
# ----------------------------------------------------------------------------------------------------
H_FTIN = re.compile(r'(?<![\d.])(?P<f>[4-7])\s*(?:\'|ft\.?|feet|foot)\s*(?P<i>\d{1,2}(?:\.\d+)?)?\s*(?:"|in\.?\b|inches\b)?')
H_FTIN_WORDS = re.compile(r'(?P<f>[4-7]) feet (?P<i>\d{1,2}) inches')
H_CM = re.compile(r'(?<![\d.])(?P<v>1[2-9]\d(?:\.\d+)?)\s*cm\b')
H_M = re.compile(r'(?<![\d.])(?P<v>[12]\.\d{1,3})\s*m\b(?!²)')
W_LB = re.compile(r'(?<![\d.])(?P<v>\d{2,3}(?:\.\d+)?)\s*(?:lbs?\b|pounds\b|-pound\b)')
W_KG = re.compile(r'(?<![\d.])(?P<v>\d{2,3}(?:\.\d+)?)\s*(?:kg\b|kilograms\b)')
BMI_VAL = re.compile(r'\bBMI(?:\s+(?:of|is|=|would be|reads?|was))?(?:\s+about)?\s*(?:=\s*)?(?P<v>\d{2}(?:\.\d)?)\b(?!\s*(?:-|to\b|or\b|and\b|\+|%))')
PERSON = re.compile(r'\b(a person|person who|someone|an adult|adult weighing|a man|a woman|you are|you weigh|'
                    r'who weighs|weighing|would have)\b', re.I)


def heights(s):
    out = []
    for m in H_FTIN_WORDS.finditer(s.t):
        out.append(('us', int(m['f']) * 12 + float(m['i']), [s.tok_in(m, 'f'), s.tok_in(m, 'i')], m))
    for m in H_FTIN.finditer(s.t):
        if m.group('i') is None:
            continue
        if any(o[3].start() <= m.start() < o[3].end() for o in out):
            continue
        out.append(('us', int(m['f']) * 12 + float(m['i']), [s.tok_in(m, 'f'), s.tok_in(m, 'i')], m))
    for m in H_CM.finditer(s.t):
        out.append(('cm', float(m['v']), [s.tok_in(m, 'v')], m))
    for m in H_M.finditer(s.t):
        out.append(('m', float(m['v']), [s.tok_in(m, 'v')], m))
    out = [h for h in out if h[2][0] is not None]
    return sorted(out, key=lambda h: h[3].start())


def weights(s):
    out = [('lb', float(m['v']), s.tok_in(m, 'v'), m) for m in W_LB.finditer(s.t)]
    out += [('kg', float(m['v']), s.tok_in(m, 'v'), m) for m in W_KG.finditer(s.t)]
    return sorted([w for w in out if w[2] is not None], key=lambda w: w[3].start())


def hw_bmi_rules(s, adds):
    """One height, one weight and a BMI in a sentence. The first weight decides the units."""
    hs, ws = heights(s), weights(s)
    if not hs or not ws:
        return
    w = ws[0]
    metric = w[0] == 'kg'
    pick = [x for x in hs if (x[0] != 'us') == metric]
    if not pick:
        return
    h = pick[0]
    cm = h[1] * 100 if h[0] == 'm' else h[1]
    targets = [s.tok_in(m, 'v') for m in BMI_VAL.finditer(s.t)]
    person = bool(PERSON.search(s.t)) and s.region not in ('table', 'svg')
    if person:   # a person's example that ends in "= 25.1": the result of the arithmetic is the claim
        for m in re.finditer(r'=\s*(?P<v>\d{2}\.\d)\b', s.t):
            targets.append(s.tok_in(m, 'v'))
    targets = [i for i in dict.fromkeys(targets) if s.free(i)]
    if not targets:
        return
    cls = 'A' if person else 'B'
    for b in targets:
        dec = s.toks[b].dec
        raw = f'__A.bmiM({w[1]}, {cm})' if metric else f'__A.bmi({w[1]}, {h[1]})'
        if cls == 'A':
            spec = {'kind': 'A', 'calc': '/', 'units': 'metric' if metric else 'us',
                    'inputs': ({'cm': cm, 'kg': w[1]} if metric else {'ft': int(h[1] // 12), 'in': h[1] % 12, 'lb': w[1]}),
                    'claims': [{'tok': b, 'read': 'bmi'}]}
            cm_ = CAT_RX.search(s.t[s.toks[b].end:])
            if cm_:
                spec['claims'].append({'text': cm_.group(1), 'read': 'category'})
        else:
            spec = {'kind': 'num', 'expr': f'__A.r1({raw})' if dec == 1 else raw, 'target': b,
                    'label': ('BMI kg/m²' if metric else 'BMI lb x 703 / in²') + (', round1' if dec == 1 else ', rounded once to a whole number')}
            cm_ = CAT_RX.search(s.t[s.toks[b].end:s.toks[b].end + 30])
            if cm_:
                spec['cat'] = cm_.group(1)
                spec['catexpr'] = f'__A.cat({raw})'
        s.assign(b, cls, 'worked example (BMI)' if cls == 'A' else 'BMI for a height and weight', spec)
        job(adds, s, b)
    for i in [x for x in h[2] if x is not None] + [w[2]]:
        s.assign(i, cls, 'input (height / weight)')


# ----------------------------------------------------------------------------------------------------
# B: conversions, formula constants, arithmetic written out
# ----------------------------------------------------------------------------------------------------
WAIST_PAIRS = {(35, 88), (40, 102), (31.5, 80), (35.5, 90), (37, 94)}
CONV = [
    (re.compile(r'(?P<a>\d+(?:\.\d+)?)\s*(?:lbs?|pounds)\s*(?:\(\s*~?|=\s*|is\s+)(?P<b>\d+(?:\.\d+)?)\s*kg'), 'lb2kg', 'kg from lb (lbsToKg)'),
    (re.compile(r'(?P<a>\d+(?:\.\d+)?)\s*(?:kg|kilograms)\s*(?:\(\s*~?|=\s*|is\s+)(?P<b>\d+(?:\.\d+)?)\s*(?:lbs?|pounds)'), 'kg2lb', 'lb from kg (kgToLbs)'),
    (re.compile(r'(?<![\d.])(?P<f>[4-7])\s*\'\s*(?P<i>\d{1,2})\s*"?\s*(?:\(\s*|=\s*)(?P<b>1\d\d(?:\.\d+)?)\s*cm'), 'ftin2cm', 'cm from ft/in (inchesToCm)'),
    (re.compile(r'(?P<a>1\d\d(?:\.\d+)?)\s*cm\s*\(\s*(?P<f>[4-7])\s*\'\s*(?P<i>\d{1,2}(?:\.\d+)?)\s*"?\s*\)'), 'cm2ftin', 'ft/in from cm'),
    (re.compile(r'(?P<a>\d+(?:\.\d+)?)\s*(?:in\b|inches|")\s*\(\s*(?P<b>\d+(?:\.\d+)?)\s*cm\s*\)'), 'in2cm', 'cm from in (inchesToCm)'),
    (re.compile(r'(?P<a>\d+(?:\.\d+)?)\s*cm\s*\(\s*(?P<b>\d+(?:\.\d+)?)\s*(?:in\b|inches)\s*\)'), 'cm2in', 'in from cm'),
    (re.compile(r'(?P<a>[12]\.\d+)\s*m\s*\(\s*(?P<f>[4-7])\s*\'\s*(?P<i>\d{1,2})\s*"?\s*\)'), 'm2ftin', 'ft/in from m'),
    (re.compile(r'(?<![\d.])(?P<f>[4-7])\s*\'\s*(?P<i>\d{1,2})\s*"?\s*(?:\(\s*|=\s*)(?P<b>\d{2})(?:\s*|-)(?:inch|inches|in\b)'), 'ftin2in', 'inches from ft/in'),
    (re.compile(r'(?P<b>\d{2})\s*(?:in|inches)\s*\(\s*(?P<f>[4-7])\s*\'\s*(?P<i>\d{1,2})\s*"?\s*\)'), 'in2ftin', 'ft/in from inches'),
    (re.compile(r'(?P<a>\d{2})\s*inches\s*or\s*(?P<b>1\d\d)\s*cm'), 'in2cm', 'cm from in (inchesToCm)'),
    (re.compile(r'(?P<a>\d+(?:\.\d+)?)\s*(?:in|inches)\s*=\s*(?P<b>[12]\.\d+)\s*m\b'), 'in2m', 'm from in'),
    (re.compile(r'(?P<a>[12]\.\d+)\s*m\s*=\s*(?P<b>\d+(?:\.\d+)?)\s*(?:in|inches)'), 'm2in', 'in from m'),
    (re.compile(r'(?P<a>1\d\d)\s*cm\s*/\s*100\s*=\s*(?P<b>[12]\.\d+)\s*m'), 'cm2m', 'm from cm'),
    (re.compile(r'(?P<a>1\d\d)\s*cm\s*=\s*(?P<b>[12]\.\d+)\s*m\b'), 'cm2m', 'm from cm'),
    (re.compile(r'(?P<a>[12]\.\d+)\s*m\s*(?:\(\s*|=\s*)(?P<b>1\d\d(?:\.\d+)?)\s*cm'), 'm2cm', 'cm from m'),
]
CONV_EXPR = {'lb2kg': '__A.lb2kg({a})', 'kg2lb': '__A.kg2lb({a})', 'ftin2cm': '__A.in2cm({fi})', 'cm2ftin': '__A.cm2in({a}) - {f12}',
             'in2cm': '__A.in2cm({a})', 'cm2in': '__A.cm2in({a})', 'm2ftin': '__A.m2in({a}) - {f12}', 'ftin2in': '__A.ftin({f}, {i})',
             'in2m': '__A.in2m({a})', 'm2in': '__A.m2in({a})', 'cm2m': '{a} / 100', 'm2cm': '{a} * 100'}


def conversion_rules(s, adds):
    t = s.t
    for rx, kind, label in CONV:
        for m in rx.finditer(t):
            gi = {g: s.tok_in(m, g) for g in rx.groupindex if m.group(g) is not None}
            if any(i is None for i in gi.values()):
                continue
            if kind == 'in2ftin':
                f, b = int(m['f']), float(m['b'])
                if not s.free(gi['i']):
                    continue
                s.assign(gi['i'], 'B', 'unit conversion', {'kind': 'num', 'expr': f'{b} - {f * 12}', 'target': gi['i'], 'label': 'inches left after the feet'})
                s.assign(gi['f'], 'B', 'unit conversion (input)')
                s.assign(gi['b'], 'B', 'unit conversion (input)')
                job(adds, s, gi['i'])
                continue
            out_g = 'b' if 'b' in gi else 'i'
            if not s.free(gi.get(out_g)):
                continue
            a = float(m['a']) if 'a' in gi else None
            if kind in ('in2cm', 'cm2in'):
                pair = (a, float(m['b'])) if kind == 'in2cm' else (float(m['b']), a)
                if pair in WAIST_PAIRS and re.search(r'waist', t + ' ' + s.ctx(), re.I):
                    continue
            f = int(m['f']) if 'f' in gi else 0
            i_ = float(m['i']) if 'i' in gi else 0
            expr = CONV_EXPR[kind].format(a=a, f=f, i=i_, fi=f * 12 + i_, f12=f * 12)
            s.assign(gi[out_g], 'B', 'unit conversion', {'kind': 'num', 'expr': expr, 'target': gi[out_g], 'label': label})
            for g, i in gi.items():
                if g != out_g:
                    s.assign(i, 'B', 'unit conversion (input)')
            job(adds, s, gi[out_g])


CONSTANTS = [
    (r'(?<![\d.,])703(?![\d,]|\.\d)', '__A.k703()', 0, 'the 703 in calculateBMI'),
    (r'703\.07(?!\d)', '1 / Math.pow(__A.in2m(1), 2) / __A.kg2lb(1)', None, '(1/0.0254)² ÷ 2.20462, calculator.js constants'),
    (r'703\.0696(?!\d)', '1 / Math.pow(0.0254, 2) * 0.45359237', None, 'exact: (1/0.0254)² x 0.45359237 (the international inch and pound)'),
    (r'2\.20462(?!\d)', '__A.kLb()', None, 'kgToLbs(1)'),
    (r'39\.3701(?!\d)', '100 / __A.kIn()', None, '100 / inchesToCm(1)'),
    (r'(?<![\d.])0\.0254(?!\d)', '__A.kIn() / 100', None, 'inchesToCm(1) / 100'),
    (r'(?<![\d.])2\.54(?!\d)', '__A.kIn()', None, 'inchesToCm(1)'),
    (r'1,550(?:\.0)?(?!\d)', 'Math.pow(100 / __A.kIn(), 2)', None, '(1/0.0254)²'),
]
SRC_CONSTANTS = [  # formula constants that must appear in calculator.js's own function source
    (r'0\.407\s*x\s*weight', 'calculateLBM', '0.407 * weightKg + 0.267 * heightCm - 19.2', 'Boer (men) in calculateLBM'),
    (r'0\.252\s*x\s*weight', 'calculateLBM', '0.252 * weightKg + 0.473 * heightCm - 48.3', 'Boer (women) in calculateLBM'),
    (r'(?<![\d.])1\.3\s*x\s*(?:weight|kg)', 'calculateNewBMI', '1.3 * weightKg / Math.pow(heightM, 2.5)', 'New BMI in calculateNewBMI'),
]


def constant_rules(s, adds):
    t = s.t
    for rx, expr, dec, label in CONSTANTS:
        for m in re.finditer(rx, t):
            i = s.at(m.start())
            if not s.free(i):
                continue
            if m.group(0) == '2.54' and not re.search(r'cm|centim|inch', t, re.I):
                continue
            spec = {'kind': 'num', 'expr': expr, 'target': i, 'label': label}
            if dec is not None:
                spec['dec'] = dec
            s.assign(i, 'B', 'formula constant', spec)
            job(adds, s, i)
    for rx, fn, has, label in SRC_CONSTANTS:
        m = re.search(rx, t)
        if not m:
            continue
        nums = re.findall(r'\d+(?:\.\d+)?', has)
        ks = [k for k in s.toks if k.kind == 'num' and k.start >= m.start() and s.free(k.idx) and k.text in nums]
        for n, k in enumerate(ks):
            if n == 0:
                s.assign(k.idx, 'B', 'formula constant', {'kind': 'src', 'fn': fn, 'has': has, 'target': k.idx, 'label': label})
                job(adds, s, k.idx)
            else:
                s.assign(k.idx, 'B', 'formula constant (same formula)')
    if re.search(r'Trefethen|New BMI', t + ' ' + s.ctx()):
        for m in re.finditer(r'(?:\^|power of |exponent of )(2\.5)\b', t):
            i = s.at(m.start(1))
            if s.free(i):
                s.assign(i, 'B', 'formula constant', {'kind': 'src', 'fn': 'calculateNewBMI', 'has': 'Math.pow(heightM, 2.5)', 'target': i, 'label': 'New BMI exponent in calculateNewBMI'})
                job(adds, s, i)


CHAIN_SEG = r'[\d(][\d\s.,()x*/+\'"²³-]*'
CITATION = re.compile(r'\b\d{4}\s*;\s*\d+|\d+\s*\(\d+(?:[-–]\d+)?\)\s*[:,]\s*[e\d]|\bpp?\.\s?\d+|\bPMID:?\s?\d+|\bVol\.\s?\d+|'
                      r'\b\d+\s*\(\d+\)[.,]?\s*$|\bt\.\s?[IVX]+\b|\bdoi\b|\bStat 3\(\d+\)', re.I)


def seg_value(seg):
    """A segment of an "a = b = c" chain: a height (5'10"), a number or arithmetic; returns (js, kind)."""
    g = seg.strip().rstrip('.,( ').strip()
    m = re.fullmatch(r'([4-7])\s*\'\s*(\d{1,2})\s*"?', g)
    if m:
        return f'({int(m[1]) * 12 + int(m[2])})', 'height'
    if re.fullmatch(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?', g):
        return g.replace(',', ''), 'number'
    e = g.replace('x', '*').replace('²', '**2').replace('³', '**3')
    e = re.sub(r'(?<=\d),(?=\d{3})', '', e)
    if not re.fullmatch(r'[\d\s.()*/+\-]+', e) or not re.search(r'[*/+\-]', e) or e.count('(') != e.count(')'):
        return None, None
    return '(' + e + ')', 'expr'


def arithmetic_rules(s, adds):
    """Arithmetic the page writes out: "a = b = c" chains (each step against the first) and "25.8 (160 x 703 / 66²)"."""
    t = s.t
    if CITATION.search(t):
        return
    for chain in re.finditer(r'(?:' + CHAIN_SEG + r'=\s*)+' + CHAIN_SEG, t):
        parts, pos = [], chain.start()
        for seg in chain.group(0).split('='):
            parts.append((pos, pos + len(seg), seg))
            pos += len(seg) + 1
        vals = [seg_value(p[2]) for p in parts]
        if any(v[0] is None for v in vals) or not (any(v[1] == 'expr' for v in vals) or vals[0][1] == 'height'):
            continue
        nums_last = [p for p, v in zip(parts, vals) if v[1] == 'number']
        dec_final = None
        if nums_last:
            k = s.at(nums_last[-1][0], nums_last[-1][1])
            dec_final = s.toks[k].dec if k is not None else None
        first_js = vals[0][0]
        for (a, b, seg), (js, kind) in list(zip(parts, vals))[1:]:
            ks = [k for k in s.toks if a <= k.start < b and k.kind == 'num']
            if not ks:
                continue
            target = ks[0] if kind == 'number' else ks[-1]
            if not s.free(target.idx):
                continue
            if kind == 'number':
                spec = {'kind': 'num', 'expr': first_js, 'target': target.idx,
                        'label': 'arithmetic as written: ' + squash(parts[0][2]) + ' = ' + squash(seg)}
            else:
                spec = {'kind': 'num', 'expr': js, 'target': target.idx, 'compare_to': first_js,
                        'dec': dec_final if dec_final is not None else 2,
                        'label': 'step as written: ' + squash(seg) + ' against ' + squash(parts[0][2])}
            s.assign(target.idx, 'B', 'arithmetic', spec)
            job(adds, s, target.idx)
        for k in s.toks:
            if chain.start() <= k.start < chain.end():
                s.assign(k.idx, 'B', 'arithmetic (operand)')
    for m in re.finditer(r'(?P<r>\d+(?:\.\d+)?)\s*\((?P<e>[\d\s.,x*/+\-²³]+)\)', t):
        if not re.search(r'[x*/²]', m.group('e')):
            continue
        js, kind = seg_value(m.group('e'))
        ri = s.tok_in(m, 'r')
        if js is None or kind != 'expr' or not s.free(ri):
            continue
        s.assign(ri, 'B', 'arithmetic', {'kind': 'num', 'expr': js, 'target': ri, 'label': 'arithmetic as written: ' + squash(m.group('e'))})
        for k in s.toks:
            if m.start('e') <= k.start < m.end('e'):
                s.assign(k.idx, 'B', 'arithmetic (operand)')
        job(adds, s, ri)


HB = re.compile(r'(?P<f>[4-7])\s*\'\s*(?P<i>\d{1,2})\s*"?(?:[^.;]{0,40}?)(?P<lo>\d{2,3})\s*(?:lbs?|pounds)?\s*(?:-|to)\s*(?P<hi>\d{2,3})\s*(?:lbs?\b|pounds)')


def height_band_rules(s, adds):
    """'At 5'9", healthy weight is 125 lb-168 lb': the healthy range at that height, from weightBounds."""
    if not re.search(r'healthy|normal', s.t + ' ' + s.unit.get('text', ''), re.I) or s.region == 'table':
        return
    for m in HB.finditer(s.t):
        gi = {g: s.tok_in(m, g) for g in ('f', 'i', 'lo', 'hi')}
        if any(i is None for i in gi.values()) or not (s.free(gi['lo']) and s.free(gi['hi'])):
            continue
        inch = int(m['f']) * 12 + int(m['i'])
        s.assign(gi['f'], 'B', 'input (height)')
        s.assign(gi['i'], 'B', 'input (height)')
        s.assign(gi['lo'], 'B', 'healthy range at a height', {'kind': 'num', 'expr': f'__A.minLb({inch}, 18.5, 24.9)', 'target': gi['lo'], 'dec': 0, 'label': 'weightBounds(18.5, 24.9).minLb'})
        s.assign(gi['hi'], 'B', 'healthy range at a height', {'kind': 'num', 'expr': f'__A.maxLb({inch}, 18.5, 24.9)', 'target': gi['hi'], 'dec': 0, 'label': 'weightBounds(18.5, 24.9).maxLb'})
        job(adds, s, gi['lo'])
        job(adds, s, gi['hi'])


def echo_rule(s):
    """A number repeated in a sentence where it is already an input or an operand is that same input."""
    known = {}
    for k in s.toks:
        if k.cls in ('A', 'B') and k.why and ('input' in k.why or 'operand' in k.why):
            known.setdefault(k.value, k.cls)
    for k in s.toks:
        if k.cls is None and k.kind == 'num' and k.value in known:
            s.assign(k.idx, known[k.value], 'input (repeated in the sentence)')


# ----------------------------------------------------------------------------------------------------
# scales, axes and SVG charts
# ----------------------------------------------------------------------------------------------------
LONE = re.compile(r'\s*[<>≥≤]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:%|m|kg|lbs?|cm|in)?\s*')


def scale_rules(s, adds):
    """A lone number on a BMI scale (results panel, legend, SVG): a category cut-off, or the results scale's start."""
    m = LONE.fullmatch(s.t)
    if not m or s.region not in ('results', 'main', 'svg') or not s.toks or not s.free(0):
        return
    ctx_vals = set(float(x) for x in re.findall(r'(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])', norm1(s.unit.get('ctx', ''))))
    if len(ctx_vals & {18.5, 25.0, 30.0, 35.0, 40.0}) < 3:
        return
    v = float(m.group(1))
    if v in BOUNDARIES:
        s.assign(0, 'B', 'scale tick at a category cut-off', {'kind': 'boundary', 'value': v, 'target': 0,
                                                              'label': 'getBMICategory changes category at this value'})
        job(adds, s, 0)
    elif v == 15 and s.region == 'results':
        s.assign(0, 'B', 'scale start', {'kind': 'num', 'expr': '__A.scaleMin()', 'target': 0, 'dec': 0, 'label': 'getScalePosition starts at this BMI'})
        job(adds, s, 0)


def svg_rules(page, sents, adds):
    """SVG charts: the BMI grid (heights x weights, whole-number BMI in each cell), the states-at-35% bars, axis ticks."""
    by = defaultdict(list)
    for s in sents:
        if s.region == 'svg' and s.unit.get('cx') is not None and s.mirror is None:
            by[s.unit['svg']].append(s)
    for svg, items in by.items():
        hts = []
        for s in items:
            m = re.fullmatch(r'([4-7])\'(\d{1,2})"', s.t.strip())
            if m:
                hts.append((s, int(m[1]) * 12 + int(m[2])))
        lone = [(s, float(LONE.fullmatch(s.t).group(1))) for s in items if LONE.fullmatch(s.t) and s.toks]
        if len(hts) >= 5:     # BMI grid: height labels down the side, weight ticks along the top
            ys = Counter(round(s.unit['cy']) for s, v in lone if v >= 90)
            top_y = ys.most_common(1)[0][0] if ys else None
            wts = [(s, v) for s, v in lone if top_y is not None and abs(s.unit['cy'] - top_y) < 3 and v >= 90]
            if len(wts) >= 5:
                lb = bool(re.search(r'\(lb\)|lbs?\b|pounds', ' '.join(x.t for x in items), re.I))
                for s, v in wts:
                    s.assign(0, 'B', 'BMI chart column weight (input)')
                for s, v in hts:
                    for k in s.toks:
                        s.assign(k.idx, 'B', 'BMI chart row height (input)')
                for s, v in lone:
                    if not s.free(0):
                        continue
                    col = min(wts, key=lambda w: abs(w[0].unit['cx'] - s.unit['cx']))
                    row = min(hts, key=lambda h: abs(h[0].unit['cy'] - s.unit['cy']))
                    if abs(col[0].unit['cx'] - s.unit['cx']) > 15 or abs(row[0].unit['cy'] - s.unit['cy']) > 8:
                        continue
                    expr = f'__A.bmi({col[1]}, {row[1]})' if lb else f'__A.bmiM({col[1]}, {row[1]})'
                    s.assign(0, 'B', 'BMI chart cell', {'kind': 'num', 'expr': expr, 'target': 0, 'dec': 0,
                                                        'label': f'BMI at {fmt(col[1], 0)} lb and {row[0].t.strip()}, rounded once to a whole number'})
                    job(adds, s, 0)
        years = [(s, int(s.t.strip())) for s in items if re.fullmatch(r'(?:19|20)\d\d', s.t.strip())]
        if page == '/obesity-rate-by-state/' and len(years) >= 5:    # bars: states at 35% or higher, by year
            for s, v in lone:
                if not s.free(0) or any(s is y[0] for y in years):
                    continue
                if s.unit['cx'] < 35:
                    s.assign(0, 'D', 'axis tick')
                    continue
                yr = min(years, key=lambda y: abs(y[0].unit['cx'] - s.unit['cx']))
                if abs(yr[0].unit['cx'] - s.unit['cx']) > 12:
                    continue
                s.assign(0, 'B', 'count of states in a dataset year', {'kind': 'num', 'expr': f'__A.brfssCount("{yr[1]}", 35)', 'target': 0, 'dec': 0,
                                                                       'label': f'states (of the 50) at 35% or higher in {yr[1]}, the CDC BRFSS CSV the registry row serves'})
                job(adds, s, 0)
        for axis in ('cx', 'cy'):      # plain axis ticks: 4+ lone numbers in an arithmetic progression on one line
            line = defaultdict(list)
            for s, v in lone:
                if s.free(0):
                    line[round(s.unit[axis] / 4)].append((s, v))
            for grp in line.values():
                vals = sorted(set(v for _, v in grp))
                if len(vals) >= 4 and len({round(b - a, 6) for a, b in zip(vals, vals[1:])}) == 1:
                    for s, v in grp:
                        s.assign(0, 'D', 'axis tick')


# ----------------------------------------------------------------------------------------------------
# B: tables the site's formulas decide (matched on their header row); data tables (C) get their age keys
# ----------------------------------------------------------------------------------------------------
def num_in(cell):
    m = re.search(r'\d+(?:\.\d+)?', norm1(cell).replace(',', ''))
    return float(m.group(0)) if m else None


def table_rules(s, adds, tables):
    if s.region != 'table':
        return
    u = s.unit
    head = [norm1(squash(h)) for h in (u.get('colHead') or [])]
    H = ' | '.join(head)
    cells = s.cells

    def cell_toks(ci):
        return [k for k in s.toks if k.cell == ci and k.kind == 'num']

    def tok_of_cell(ci, n=0):
        ks = cell_toks(ci)
        return ks[n].idx if len(ks) > n else None

    def first_height(ci):
        m = re.search(r'([4-7])\s*\'\s*(\d{1,2})', cells[ci])
        if m:
            return int(m[1]) * 12 + int(m[2]), 'us'
        m = re.search(r'(1\d\d(?:\.\d+)?)\s*cm', cells[ci])
        if m:
            return float(m[1]), 'cm'
        return None, None

    if u.get('isHead'):
        return
    # BMI chart: height rows x weight columns, a whole-number BMI in each cell
    if re.match(r'Height \| \d+ lbs \(\d+ kg\)', H) or re.match(r'Height \| \d+ kg \(\d+ lbs\)', H):
        metric = ' kg (' in H.split('|')[1]
        h, kind = first_height(0)
        for k in cell_toks(0):
            s.assign(k.idx, 'B', 'BMI chart row height (input)')
        for ci in range(1, len(cells)):
            i = tok_of_cell(ci)
            if i is None or h is None:
                continue
            w = num_in(head[ci])
            expr = f'__A.bmiM({w}, {h})' if metric else f'__A.bmi({w}, {h})'
            s.assign(i, 'B', 'BMI chart cell', {'kind': 'num', 'expr': expr, 'target': i, 'dec': 0,
                                                'label': f'BMI at {head[ci]} and {cells[0]}, rounded once to a whole number'})
            job(adds, s, i)
        return
    if re.match(r'Weight \| Height \| Height² \| BMI \| Category', H):
        kg, m_ = num_in(cells[0]), num_in(cells[1])
        s.assign(tok_of_cell(0), 'B', 'input (weight)')
        s.assign(tok_of_cell(1), 'B', 'input (height)')
        i2, ib = tok_of_cell(2), tok_of_cell(3)
        s.assign(i2, 'B', 'arithmetic', {'kind': 'num', 'expr': f'{m_} * {m_}', 'target': i2, 'label': 'height squared'})
        s.assign(ib, 'B', 'BMI for a height and weight', {'kind': 'num', 'expr': f'__A.r1(__A.bmiM({kg}, {m_ * 100}))', 'target': ib,
                                                          'label': 'BMI kg/m², round1', 'cat': cells[4], 'catexpr': f'__A.cat(__A.bmiM({kg}, {m_ * 100}))'})
        job(adds, s, i2)
        job(adds, s, ib)
        return
    if re.match(r'Weight \| Height \| Inches \| Inches² \| BMI \| Category', H):
        lb = num_in(cells[0])
        mm = re.search(r'([4-7])\s*\'\s*(\d{1,2})', cells[1])
        inch = int(mm[1]) * 12 + int(mm[2])
        s.assign(tok_of_cell(0), 'B', 'input (weight)')
        for k in cell_toks(1):
            s.assign(k.idx, 'B', 'input (height)')
        ii, i2, ib = tok_of_cell(2), tok_of_cell(3), tok_of_cell(4)
        s.assign(ii, 'B', 'unit conversion', {'kind': 'num', 'expr': f'__A.ftin({mm[1]}, {mm[2]})', 'target': ii, 'label': 'feet x 12 + inches'})
        s.assign(i2, 'B', 'arithmetic', {'kind': 'num', 'expr': f'{inch} * {inch}', 'target': i2, 'label': 'inches squared'})
        s.assign(ib, 'B', 'BMI for a height and weight', {'kind': 'num', 'expr': f'__A.r1(__A.bmi({lb}, {inch}))', 'target': ib,
                                                          'label': 'BMI lb x 703 / in², round1', 'cat': cells[5], 'catexpr': f'__A.cat(__A.bmi({lb}, {inch}))'})
        for i in (ii, i2, ib):
            job(adds, s, i)
        return
    if re.match(r'Feet & Inches \| Total Inches \| Meters', H):
        mm = re.search(r'([4-7])\s*\'\s*(\d{1,2})', cells[0])
        for k in cell_toks(0):
            s.assign(k.idx, 'B', 'input (height)')
        ii, im = tok_of_cell(1), tok_of_cell(2)
        s.assign(ii, 'B', 'unit conversion', {'kind': 'num', 'expr': f'__A.ftin({mm[1]}, {mm[2]})', 'target': ii, 'label': 'feet x 12 + inches'})
        s.assign(im, 'B', 'unit conversion', {'kind': 'num', 'expr': f'__A.in2m({int(mm[1]) * 12 + int(mm[2])})', 'target': im, 'label': 'inchesToCm / 100'})
        job(adds, s, ii)
        job(adds, s, im)
        return
    # weights at a BMI for a height: the header names the BMI ("(BMI 18.5)", "(BMI <18.5)", "Mid Normal (BMI 21.7)")
    if re.search(r'\(BMI\s*<?\s*\d+(?:\.\d+)?\)', H) and re.match(r'(Your )?Height', head[0]):
        h, kind = first_height(0)
        cm_tok = None
        for k in cell_toks(0):
            s.assign(k.idx, 'B', 'input (height)')
        if h is None:
            return
        inch = h if kind == 'us' else h / 2.54
        for ci in range(1, len(cells)):
            hm = re.search(r'\(BMI\s*(<)?\s*(\d+(?:\.\d+)?)\)', head[ci])
            nums = cell_toks(ci)
            if not nums:
                continue
            if hm is None:   # a column whose rule the header doesn't state ("Ideal Weight Mid-Range")
                pairs = [(f'(__A.minLb({inch}, 18.5, 24.9) + __A.maxLb({inch}, 18.5, 24.9)) / 2', 'lb'),
                         (f'(__A.minKg({inch}, 18.5, 24.9) + __A.maxKg({inch}, 18.5, 24.9)) / 2', 'kg')]
                for n, k in enumerate(nums[:2]):
                    s.assign(k.idx, 'B', 'weight for a height (column rule not stated)',
                             {'kind': 'num', 'expr': pairs[n][0], 'target': k.idx, 'dec': 0, 'implied_bmi': (inch, pairs[n][1]),
                              'label': f'midpoint of the healthy range at this height (weightBounds 18.5-24.9), {pairs[n][1]}',
                              'note': f'"{head[ci]}" states no rule; checked as the healthy-range midpoint'})
                    job(adds, s, k.idx)
                continue
            lt, b = hm.group(1), float(hm.group(2))
            if lt or b == 18.5:
                exprs = [f'__A.minLb({inch}, 18.5, 24.9)', f'__A.minKg({inch}, 18.5, 24.9)']
                label = 'weightBounds(18.5, 24.9).min: the lowest whole weight whose rounded BMI is 18.5'
            elif b == 24.9:
                exprs = [f'__A.maxLb({inch}, 18.5, 24.9)', f'__A.maxKg({inch}, 18.5, 24.9)']
                label = 'weightBounds(18.5, 24.9).max: the highest whole weight whose rounded BMI is 24.9'
            else:
                exprs = [f'__A.wAt({b}, {inch})', f'__A.kgAt({b}, {inch * 2.54})']
                label = f'weight at BMI {b} (calculateBMI solved for weight)'
            for n, k in enumerate(nums[:2]):
                s.assign(k.idx, 'B', 'weight at a BMI for a height', {'kind': 'num', 'expr': exprs[n], 'target': k.idx, 'dec': 0,
                                                                      'implied_bmi': (inch, 'kg' if n else 'lb'),
                                                                      'label': label + (', kg' if n else ', lb')})
                job(adds, s, k.idx)
        return
    if re.match(r'Your Height \| Weight to Lose per BMI Point \| Example: BMI 30 to 25', H):
        h, kind = first_height(0)
        ks0 = cell_toks(0)
        for k in ks0[:2]:
            s.assign(k.idx, 'B', 'input (height)')
        if len(ks0) > 2:
            s.assign(ks0[2].idx, 'B', 'unit conversion', {'kind': 'num', 'expr': f'__A.in2cm({h})', 'target': ks0[2].idx, 'label': 'cm from ft/in'})
            job(adds, s, ks0[2].idx)
        for ci, pts in ((1, 1), (2, 5)):
            nums = cell_toks(ci)
            if len(nums) >= 2:
                s.assign(nums[0].idx, 'B', 'weight per BMI point', {'kind': 'num', 'expr': f'{pts} * __A.wAt(1, {h})', 'target': nums[0].idx, 'label': f'{pts} BMI point(s) at this height, lb'})
                s.assign(nums[1].idx, 'B', 'weight per BMI point', {'kind': 'num', 'expr': f'{pts} * __A.kgAt(1, __A.in2cm({h}))', 'target': nums[1].idx, 'label': f'{pts} BMI point(s) at this height, kg'})
                job(adds, s, nums[0].idx)
                job(adds, s, nums[1].idx)
        return
    hm = re.match(r'Starting BMI \| Target BMI \| Weight to Lose \((\d)\'(\d+)" person\)', H)
    if hm:
        inch = int(hm[1]) * 12 + int(hm[2])
        a, b = num_in(cells[0]), num_in(cells[1])
        nums = cell_toks(2)
        for ci in (0, 1):
            ti = tok_of_cell(ci)
            cm_ = CAT_RX.search(cells[ci])
            if cm_ and ti is not None:
                s.assign(ti, 'B', 'category of a BMI', {'kind': 'catname', 'expr': f'__A.cat({num_in(cells[ci])})', 'text': cm_.group(1), 'target': ti, 'label': 'category of that BMI (getBMICategory)'})
                job(adds, s, ti)
        if len(nums) >= 2:
            s.assign(nums[0].idx, 'B', 'weight between two BMIs', {'kind': 'num', 'expr': f'__A.wAt({a}, {inch}) - __A.wAt({b}, {inch})', 'target': nums[0].idx, 'label': f'weight at BMI {a} minus weight at BMI {b} for {hm[1]}\'{hm[2]}", lb'})
            s.assign(nums[1].idx, 'B', 'weight between two BMIs', {'kind': 'num', 'expr': f'__A.kgAt({a}, __A.in2cm({inch})) - __A.kgAt({b}, __A.in2cm({inch}))', 'target': nums[1].idx, 'label': 'the same in kg'})
            job(adds, s, nums[0].idx)
            job(adds, s, nums[1].idx)
        return
    if re.match(r'Starting Point \| 5% Loss \| 10% Loss \| BMI Change', H):
        mm = re.search(r'(\d+) lbs, (\d)\'(\d+)" \(BMI (\d+\.\d)\)', cells[0])
        if not mm:
            return
        lb, inch = float(mm[1]), int(mm[2]) * 12 + int(mm[3])
        k0 = cell_toks(0)
        for k in k0[:3]:
            s.assign(k.idx, 'B', 'input (weight / height)')
        specs = [(k0[3].idx, f'__A.r1(__A.bmi({lb}, {inch}))', 'BMI lb x 703 / in², round1'),
                 (tok_of_cell(1), f'{lb} * 0.95', '95% of the starting weight'),
                 (tok_of_cell(2), f'{lb} * 0.90', '90% of the starting weight'),
                 (tok_of_cell(3, 0), f'__A.r1(__A.bmi({lb}, {inch}))', 'starting BMI'),
                 (tok_of_cell(3, 1), f'__A.r1(__A.bmi({lb} * 0.9, {inch}))', 'BMI after a 10% loss')]
        for i, e, lab in specs:
            s.assign(i, 'B', 'BMI for a height and weight' if 'BMI' in lab else 'percent of a weight', {'kind': 'num', 'expr': e, 'target': i, 'label': lab})
            job(adds, s, i)
        return
    if re.match(r'Person \| Height \| Waist \| Calculation \| WHtR \| Category', H):
        hh, ww = num_in(cells[1]), num_in(cells[2])
        mm = re.search(r'(\d+)\s*in\s*\(\s*([4-7])\s*\'\s*(\d+)', cells[1])
        if mm:
            k = cell_toks(1)[-1]
            s.assign(k.idx, 'B', 'unit conversion', {'kind': 'num', 'expr': f'{mm[1]} - {int(mm[2]) * 12}', 'target': k.idx, 'label': 'inches left after the feet'})
            job(adds, s, k.idx)
        for k in s.toks:
            if k.cell in (1, 2, 3):
                s.assign(k.idx, 'B', 'input (height / waist)')
        i = tok_of_cell(4)
        s.assign(i, 'B', 'arithmetic', {'kind': 'num', 'expr': f'{ww} / {hh}', 'target': i, 'label': 'waist / height'})
        job(adds, s, i)
        return
    if re.match(r'Height \| Maximum Healthy Waist', H):
        h, kind = first_height(0)
        k0 = cell_toks(0)
        for k in k0[:2]:
            s.assign(k.idx, 'B', 'input (height)')
        if len(k0) > 2:
            s.assign(k0[2].idx, 'B', 'unit conversion', {'kind': 'num', 'expr': f'__A.in2cm({h})', 'target': k0[2].idx, 'label': 'cm from ft/in'})
            job(adds, s, k0[2].idx)
        nums = cell_toks(1)
        if len(nums) >= 2:
            s.assign(nums[0].idx, 'B', 'half the height', {'kind': 'num', 'expr': f'0.5 * {h}', 'target': nums[0].idx, 'label': '0.5 x height, in'})
            s.assign(nums[1].idx, 'B', 'half the height', {'kind': 'num', 'expr': f'0.5 * __A.in2cm({h})', 'target': nums[1].idx, 'label': '0.5 x height, cm (inchesToCm)'})
            job(adds, s, nums[0].idx)
            job(adds, s, nums[1].idx)
        return
    if re.match(r'Person \| Boer \| James \| Hume \| Difference Range', H):
        mm = re.match(r'(Male|Female), (\d+) cm, (\d+) kg', cells[0])
        if not mm:
            return
        sex, cm, kg = mm[1].lower(), float(mm[2]), float(mm[3])
        for k in cell_toks(0):
            s.assign(k.idx, 'B', 'input (sex, height, weight)')
        for ci, key in ((1, 'boer'), (2, 'james'), (3, 'hume')):
            i = tok_of_cell(ci)
            s.assign(i, 'B', 'lean body mass (calculateLBM)', {'kind': 'num', 'expr': f'__A.lbm("{sex}", {kg}, {cm}).{key}', 'target': i, 'label': f'{key.title()} lean mass, kg (calculateLBM, metric)'})
            job(adds, s, i)
        i = tok_of_cell(4)
        s.assign(i, 'B', 'lean body mass (calculateLBM)', {'kind': 'num', 'expr': f'(r => Math.max(r.boer, r.james, r.hume) - Math.min(r.boer, r.james, r.hume))(__A.lbm("{sex}", {kg}, {cm}))', 'target': i, 'label': 'highest minus lowest of the three, kg, from the unrounded values'})
        job(adds, s, i)
        return
    if re.match(r'Age \| 5th healthy from \| 85th overweight from \| 95th obesity from', H):
        sex = 'female' if 'Girls' in u.get('caption', '') else 'male'
        age = num_in(cells[0])
        s.assign(tok_of_cell(0), 'B', 'input (age)')
        for ci, p in ((1, 5), (2, 85), (3, 95)):
            i = tok_of_cell(ci)
            s.assign(i, 'B', 'BMI at a CDC percentile (LMS)', {'kind': 'num', 'expr': f'__A.kidsAt("{sex}", {age * 12}, {p})', 'target': i, 'dec': 1,
                                                                'alt': f'__A.kidsAt("{sex}", {age * 12 + 0.5}, {p})',
                                                                'label': f'BMI at the {p}th percentile, {sex}, getLMSRow at {int(age * 12)} months (the calculator at that birthday)'})
            job(adds, s, i)
        return
    if re.match(r'Age \(years\) \| Boys \(50th %ile\) \| Girls \(50th %ile\)', H):
        age = num_in(cells[0])
        s.assign(tok_of_cell(0), 'B', 'input (age)')
        for ci, sex in ((1, 'male'), (2, 'female')):
            i = tok_of_cell(ci)
            s.assign(i, 'B', 'median BMI (LMS M)', {'kind': 'num', 'expr': f'__A.kidsM("{sex}", {age * 12})', 'target': i, 'dec': 1,
                                                    'alt': f'__A.kidsM("{sex}", {age * 12 + 0.5})',
                                                    'label': f'M at getLMSRow({sex}, {int(age * 12)} months)'})
            job(adds, s, i)
        return
    # the state ranking: rank and change are our arithmetic; the rest are the CDC BRFSS values (C)
    if re.match(r'Rank \| State \| 2025 \| 95% CI \| 2011 \| Change \(pts\)', H):
        state = cells[1]
        vals = [num_in(r[2]) for r in tables.get((s.page, u['table']), []) if len(r) > 2 and re.fullmatch(r'\d+(?:\.\d+)?%', r[2].strip())]
        i = tok_of_cell(0)
        v = num_in(cells[2])
        s.assign(i, 'B', 'rank in the table', {'kind': 'num', 'expr': f'[{",".join(str(x) for x in vals)}].filter(x => x > {v}).length + 1', 'target': i, 'dec': 0,
                                               'label': 'states with a higher 2025 rate in this table, plus one (ties share a rank)'})
        job(adds, s, i)
        i = tok_of_cell(5)
        if i is not None:
            s.assign(i, 'B', 'change between two years', {'kind': 'num', 'expr': f'__A.brfss("{state}", "2025") - __A.brfss("{state}", "2011")', 'target': i,
                                                          'label': '2025 minus 2011, the CDC BRFSS CSV the registry row serves'})
            job(adds, s, i)
        for ci in (2, 3, 4):
            for k in cell_toks(ci):
                s.assign(k.idx, 'C', 'outside fact (CDC BRFSS state value)')
        return
    if re.match(r'Area \| 2025 \| 95% CI or latest \| 2011', H) or re.match(r'State \| 18-39 \| 40-59 \| 60\+', H):
        for k in s.toks:
            if k.cell and k.cell > 0:
                s.assign(k.idx, 'C', 'outside fact (CDC BRFSS state value)')
        return


# ----------------------------------------------------------------------------------------------------
# C and D rules
# ----------------------------------------------------------------------------------------------------
NAME_BEFORE = re.compile(r'(?:\b(?:Type|type|Class|class|Grade|grade|Stage|stage|Series|No\.|Brief|E-Stat|Stat|TRS|Table|Tables|'
                         r'Figure|Fig\.|Vol\.|Volume|Article|Art\.|Chapter|People|Report Series|Directive|Form|DA|Analytics|'
                         r'Publication No\.|v|Mode v|Level|Tier|Appendix|Box|Paragraph|Obese Class|Obesity class|'
                         r'Obesity, class|Edition|edition|Pub\.|Number|NCHS|HE-Stat|Person|Woman|Man|Row|Column|Wave)\s?|COVID-|\b[A-Z]{2,4}-|factor-)$')
STAT_CUES = re.compile(r'\b(n\s*=|HR|hazard|odds|risk|CI\b|confidence|stud(?:y|ies)|meta-analys|cohort|trial|survey|participants|'
                       r'adults|people|children|kids|teens|men\b|women|deaths|individuals|prevalence|percent|average|mean|median|'
                       r'rate|NHANES|CDC|WHO|NIH|NHLBI|NCHS|BRFSS|et al|population|Americans|US\b|reduction|increase|'
                       r'decrease|associated|linked|estimate|data|recommend|guideline|aged?|ages|years? old|'
                       r'percentile|cut-?off|threshold|kcal|cal\b|calorie|calories|minutes|hours|days|weeks|months|mmHg|'
                       r'mg/dL|grams?|per (?:day|week|decade|year)|daily|weekly|times|players|athletes|prospects|'
                       r'football|NFL|action points?|ratio|WHtR|waist|mph|states?|obesity|overweight|BMR|metabol|fold|'
                       r'loss|lose|gain|body fat|muscle|plateau|mortality|million|counties|territor)\b', re.I)
COUNT_NOUNS = re.compile(r'^[\s-]?(?:[a-z-]+\s){0,2}(steps?|formulas?|equations?|methods?|calculators?|guides?|articles?|tools?|ways?|'
                         r'tips?|mistakes?|questions?|sections?|tables?|charts?|pages?|examples?|numbers?|measurements?|'
                         r'categories|category|classes|grades?|versions?|options?|things?|parts?|factors?|columns?|rows?|'
                         r'indices|indexes|metrics?|measures?|limitations?|strategies|myths?|signs?|types?|levels?|tiers?|'
                         r'sites?|components?|reasons?|areas?|pillars?|stages?|phases?|variables?|inputs?|values?|bands?|'
                         r'zones?|words?|letters?|decimal|digits?|places?|systems?|units?|readings?|scenarios?|pillars?)\b', re.I)


def c_d_rules(s, cites):
    t = s.t
    both = t + ' ' + (s.ctx() if (s.region in ('table', 'svg') or len(t) < 70) else '')
    in_refs = bool(re.match(r'\s*(references|sources|further reading|citations|bibliography|works cited)\b', s.head(), re.I)) and \
        s.unit.get('tag') in ('li', 'p') and bool(re.search(r'\(\d{4}\)|\b\d{4}[.;]|et al|[A-Z][a-z]+, [A-Z]\.|[A-Z][a-z]+ [A-Z]{1,2}[,.]', s.unit.get('text', '')))
    place_year = bool(re.fullmatch(r"\s*[A-Z][A-Za-z ]+:\s*[A-Z][\w’' .,&]+;\s*\d{4}\.?\s*", t))   # "Geneva: WHO; 1995."
    citation = in_refs or place_year or bool(CITATION.search(t)) or bool(CITATION.search(norm1(s.unit.get('text', '')))) or \
        (s.unit.get('inCite') and re.search(r'\bet al\b|[A-Z][a-z]+ [A-Z]{1,3}[,.]', t))
    legal = s.page in ('/privacy/', '/terms/', '/contact/')
    for k in s.toks:
        if not s.free(k.idx):
            continue
        if k.kind == 'num' and k.value == 95 and re.match(r'\s?%\s*(CI|confidence|ranges?|intervals?|limits)', k.suf, re.I):
            s.assign(k.idx, 'D', 'confidence level')
            continue
        if k.kind == 'num' and (re.search(r'\bCC BY\s?$', k.pre) or re.search(r'\bTables?\s+\d+\s*[-–]\s*$', k.pre)):
            s.assign(k.idx, 'D', 'name or label with a number')
            continue
        if k.kind == 'num' and NAME_BEFORE.search(k.pre):
            s.assign(k.idx, 'D', 'name or label with a number')
            continue
        if k.kind == 'num' and re.search(r'PMID:?\s?$', k.pre):
            s.assign(k.idx, 'D', 'citation detail (PMID)')
            continue
        if k.kind == 'num' and re.search(r'\d\($', k.pre) and k.suf.startswith(')'):
            s.assign(k.idx, 'D', 'legal or citation reference')
            continue
        if any(m.start() <= k.start < m.end() for m in re.finditer(r'\b(?:1-)?\d{3}-\d{3}-\d{4}\b|\b24/7\b', t)) or k.text == '911':
            s.assign(k.idx, 'D', 'phone number or hours')
            continue
        if re.search(r'\b(?:one|two|three)\s*\($', k.pre) and k.suf.startswith(')'):
            s.assign(k.idx, 'D', 'numeral repeating a number word')
            continue
        if citation:
            s.assign(k.idx, 'D', 'citation detail')
            cites.add((s.page, s.uid))
            continue
        if k.kind == 'word':
            if re.match(r'\s?(as likely|the risk|times|of (?:US|American|all|adults|children|people|women|men|those))', k.suf, re.I) or k.text.lower() == 'twice':
                s.assign(k.idx, 'C', 'statistic in words')
            else:
                s.assign(k.idx, 'D', 'number word (count in prose)')
            continue
        if legal:
            s.assign(k.idx, 'D', 'the legal page\'s own term')
            continue
        if k.value == 2026 and k.dec == 0 and (s.region in ('title', 'meta') or s.unit.get('tag') == 'h1' or re.search(r'-\s*$', k.pre)):
            s.assign(k.idx, 'D', 'the current year (a title label)')
            continue
        if k.value == 15 and LONE.fullmatch(t) and len(set(re.findall(r'18\.5|\b25\b|\b30\b|\b35\b|\b40\b', s.unit.get('ctx', '')))) >= 3:
            s.assign(k.idx, 'D', 'axis tick (the scale\'s start)')
            continue
        v = k.value
        if k.ord and re.match(r'\s?-?\s?century', k.suf):
            s.assign(k.idx, 'C', 'year (century)')
            continue
        is_year = k.dec == 0 and 1800 <= v <= 2035 and ',' not in k.text and not re.match(r'\s?(lbs?|kg|cm|calories|kcal|cal\b|people|participants|adults|men|women|individuals|%)', k.suf)
        if is_year or (re.search(r'\b(?:1[89]\d\d|20[0-3]\d)\s*-\s*$', k.pre) and k.dec == 0 and v < 100):
            s.assign(k.idx, 'C', 'year')
            continue
        if re.match(r'\s?(%|percent)', k.suf) or re.match(r'\s?[-–]\s?\d+(?:\.\d+)?\s?%', k.suf):
            s.assign(k.idx, 'C', 'statistic (percent)')
            continue
        if COUNT_NOUNS.match(k.suf) and k.dec == 0 and v < 100:
            s.assign(k.idx, 'D', 'count in prose')
            continue
        if STAT_CUES.search(both):
            s.assign(k.idx, 'C', 'outside fact (statistic, threshold or study detail)')
            continue


# ----------------------------------------------------------------------------------------------------
# manual.json: hand classifications (number-blind sentence key, classes by position, optional checks)
# ----------------------------------------------------------------------------------------------------
def load_manual():
    p = HERE / 'manual.json'
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding='utf-8'))
    return d['entries'] if isinstance(d, dict) else d


def subst(expr, s):
    """$1, $2 ... in a manual check are the sentence's numbers, in order (1-based)."""
    def rep(m):
        k = int(m.group(1)) - 1
        return repr(s.toks[k].value) if k < len(s.toks) else 'NaN'
    return re.sub(r'\$(\d+)', rep, expr)


def apply_manual(s, entries, used, adds, seen=None):
    """The first entry whose signature (and region, value, nth occurrence on the page) fits this sentence."""
    fits = []
    for n, e in enumerate(entries):
        if e.get('page') not in (s.page, '*'):
            continue
        key = e.get('sig')
        if key is None or key not in s.sig or (e.get('exact') and s.sig != key):
            continue
        if e.get('region') and e['region'] != s.region:
            continue
        if 'value' in e and not (s.toks and abs(s.toks[0].value - e['value']) < 1e-9):
            continue
        fits.append(n)
    if seen is not None:   # occurrences are counted per signature, whichever entry takes the sentence
        for key in {entries[n]['sig'] for n in fits if 'nth' in entries[n]}:
            seen[(s.page, key)] += 1
    for n in fits:
        e = entries[n]
        if 'nth' in e and (seen is None or seen[(s.page, e['sig'])] != e['nth']):
            continue
        used[n] += 1
        classes = e.get('classes', '')
        if isinstance(classes, str):
            classes = [classes] * len(s.toks)
        for i, k in enumerate(s.toks):
            if i < len(classes) and classes[i] and classes[i] != '-':
                s.assign(i, classes[i], e.get('why', 'hand classification') + ' (manual.json)')
        for c in e.get('checks', []):
            ti = c['target'] - 1
            if ti >= len(s.toks):
                continue
            spec = json.loads(json.dumps(c))
            spec['target'] = ti
            for key2 in ('expr', 'compare_to', 'alt'):
                if key2 in spec:
                    spec[key2] = subst(spec[key2], s)
            if spec.get('kind') == 'A':
                spec['inputs'] = {k: (s.toks[int(v[1:]) - 1].value if isinstance(v, str) and v.startswith('$') else v) for k, v in spec['inputs'].items()}
                for cl in spec['claims']:
                    if 'tok' in cl:
                        cl['tok'] = cl['tok'] - 1
            s.toks[ti].check = spec
            job(adds, s, ti)
        if e.get('row'):
            s.manual_row = e['row']
        return


# ----------------------------------------------------------------------------------------------------
# registry (C)
# ----------------------------------------------------------------------------------------------------
def normurl(u):
    u = (u or '').strip().lower()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    return u.split('#')[0].rstrip('/')


def numbers_of(text):
    out = []
    for m in re.finditer(r'(?<![A-Za-z0-9_.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d])', norm1(text or '')):
        out.append(float(m.group(1).replace(',', '')))
    return out


NAMED = ('Trefethen', 'Winter', 'Flegal', 'Gallagher', 'Burns', 'Rubino', 'Wing', 'Woolcott', 'Foulis', 'Frija-Masson', 'Lahav',
         'Fourman', 'Al-Roub', 'Robinson', 'Peterson', 'Davidson', 'Hamwi', 'Devine', 'Miller', 'Pai', 'Ogden', 'Fryar', 'Liu',
         'Gallup', 'Keys', 'Volpi', 'Deurenberg', 'Hodgdon', 'Siri', 'Ko')


def load_registry():
    rows = list(csv.DictReader(open(REPO / 'research' / 'data-sources.csv', newline='', encoding='utf-8')))
    for r in rows:
        r['_sn'] = numbers_of(r['sample_note'])
        r['_notes'] = numbers_of(r['notes'])
        r['_ident'] = numbers_of(' '.join([r['source'], r['domain'], r['coverage'], r['attribution'], r['publisher']]))
        r['_urls'] = [normurl(u) for u in re.findall(r'https?://[^\s;,]+', r['url'] + ' ' + r['endpoint'])]
        names = set()
        mm = re.match(r'\s*([A-Z][A-Za-z\'-]+)\s+[A-Z]{1,3}\b', r['source'])
        if mm:
            names.add(mm.group(1))
        for w in NAMED:
            if re.search(r'\b' + re.escape(w) + r'\b', r['source']):
                names.add(w)
        for pat in (r'NHANES \d{4}-\d{4}', r'E-Stat \d+', r'Data Brief (?:No\. )?\d+', r'Series 3 No\. \d+', r'Advance Data[^,]*No\. \d+',
                    r'Technical Report Series \d+', r'NG\d+', r'BRFSS', r'Global Health Observatory', r'Look AHEAD',
                    r'Body Weight Planner', r'Physical Activity Guidelines', r'National DPP'):
            for m in re.finditer(pat, r['source']):
                names.add(m.group(0))
        r['_names'] = names
    return rows


OWN_ROW = {}   # page -> its data_source registry row (research/page-map.csv), filled in main() (CMB-031)


def load_own_rows(rows):
    """The registry row each page names as its data_source in research/page-map.csv (free text names none)."""
    domains = {r['domain'] for r in rows}
    out = {}
    for r in csv.DictReader(open(REPO / 'research' / 'page-map.csv', newline='', encoding='utf-8')):
        slug, src = r['slug'].strip().strip('/'), r['data_source'].strip()
        if src in domains:
            out['/' if slug == 'home' else '/' + slug + '/'] = src
    return out


def load_datasets():
    ds = {}
    brfss = defaultdict(dict)
    for row in csv.DictReader(open(REPO / 'research/state-obesity/cdc-brfss-adult-obesity-by-state-2011-2025.csv', encoding='utf-8')):
        if row['prevalence_pct']:
            brfss[row['state']][row['year']] = tuple(float(row[c]) if row[c] else float('nan') for c in ('prevalence_pct', 'ci95_low', 'ci95_high'))
    age = defaultdict(dict)
    for row in csv.DictReader(open(REPO / 'research/state-obesity/cdc-brfss-adult-obesity-by-state-and-age-2025.csv', encoding='utf-8')):
        if row['prevalence_pct']:
            age[row['state']][row['age_group']] = float(row['prevalence_pct'])
    vals = set()
    for st in brfss.values():
        for v in st.values():
            vals.update(x for x in v if not math.isnan(x))
    for st in age.values():
        vals.update(st.values())
    b = {'state': brfss, 'age': age, 'values': vals, 'ages': {18, 39, 40, 59, 60},
         'file': 'research/state-obesity/cdc-brfss-adult-obesity-by-state-2011-2025.csv and ...-by-state-and-age-2025.csv'}
    ds['cdc-brfss-state-obesity'] = b
    aw = json.loads((REPO / 'research/average-weight/avgw_results.json').read_text(encoding='utf-8'))
    vals = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            vals.add(float(o))
    walk(aw)
    a = {'aw': aw, 'values': vals, 'file': 'research/average-weight/avgw_results.json'}
    ds['nhanes-2021-2023-exam-files'] = a
    ds['nhanes-anthropometric-reference'] = a
    # CDC's data file for the extended BMI-for-age charts (registry cdc-extended-bmi-data), every column by sex and
    # month of age; matched at the precision the page prints (CMB-031)
    kids, vals = {'male': {}, 'female': {}}, set()
    for row in csv.DictReader(open(REPO / 'data/cdc/bmi-age-2022.csv', newline='', encoding='utf-8')):
        rec = {c: float(x) for c, x in row.items() if c != 'sex' and x not in ('', None)}
        kids['male' if row['sex'].strip() == '1' else 'female'][rec['agemos']] = rec
        vals.update(rec.values())
    ds['cdc-extended-bmi-data'] = {'kids': kids, 'values': vals, 'precision': True, 'file': 'data/cdc/bmi-age-2022.csv'}
    return ds


KIDS_COLS = {'5th': 'P5', '50th': 'P50', '85th': 'P85', '95th': 'P95', '120% of 95th': 'pct120ofP95'}
KIDS_WORDS = [(r'\bmedian\b|\b50th\b', 'P50'), (r'\b5th\b', 'P5'), (r'\b85th\b', 'P85'), (r'(?<!of the )(?<!of )\b95th\b', 'P95'),
              (r'\b120% of (?:the |his row\W?s |her row\W?s )?95th\b', 'pct120ofP95'), (r'\bhealthy\b', 'P5'), (r'\bhealthy\b', 'P85'),
              (r'\bsigma\b', 'sigma'), (r'\bL =', 'L'), (r'\bM =', 'M'), (r'\bS =', 'S')]


def kids_keyed(s, k, d):
    """bmi-age-2022.csv keyed by what the page says: a table cell by sex (caption), birthday row and column; in
    prose, the columns the sentence (or its FAQ question or paragraph) names, for the sexes and ages it names, and a
    whole number of months the file has a row for. None when nothing keys the number."""
    v, dec = k.value, k.dec
    if s.region == 'table' and s.cells:
        cap = s.unit.get('caption', '')
        sex = 'male' if re.match(r'Boys\b', cap) else 'female' if re.match(r'Girls\b', cap) else None
        head = [norm1(squash(h)) for h in s.unit.get('colHead') or []]
        col = head[k.cell] if k.cell is not None and k.cell < len(head) else ''
        if sex is None:
            return None
        if s.unit.get('isHead'):
            if col in KIDS_COLS:
                return {'status': 'row-dataset', 'note': f'a column of the dataset ({KIDS_COLS[col]})'}
            return None
        age = s.cells[0].strip()
        if not re.fullmatch(r'\d{1,2}', age) or int(age) * 12 + 0.5 not in d['kids'][sex]:
            return None
        agemos = int(age) * 12 + 0.5
        if k.cell == 0:
            return {'status': 'row-dataset', 'note': f'an age of the dataset (the {agemos}-month row)'}
        if col in KIDS_COLS:
            want = d['kids'][sex][agemos][KIDS_COLS[col]]
            if half_up(want, dec) == v:
                return {'status': 'row-dataset', 'value': want}
            return {'status': 'not-in-row', 'value': want, 'note': f'dataset has {want} for {sex} at {age} ({agemos} months), {col}'}
        return None
    t = s.t
    if dec == 0 and re.match(r'\s*(?:(?:to|-)\s*\d+\s*)?months?\b', k.suf):    # "24 to 239 months", "239 months"
        if v + 0.5 in d['kids']['male']:
            return {'status': 'row-dataset', 'note': f'a month of age the dataset has a row for ({v + 0.5})'}
    if dec < 1 or k.ord:
        return None
    text = t + ' ' + (s.unit.get('question') or '') + ' ' + (s.unit.get('ctx') or '')
    cols = {c for rx, c in KIDS_WORDS if re.search(rx, text, re.I)}
    sexes = [x for x, rx in (('male', r"\b(?:boys?|boy's|his|he)\b"), ('female', r"\b(?:girls?|girl's|her|she)\b")) if re.search(rx, t, re.I)] \
        or ['male', 'female']
    ages = set()
    for m in re.finditer(r'(?:\b(?:age|aged|at|from|and)\s+|,\s*)(\d{1,2})(?!\d|[.,]\d)(?!\s*(?:%|lb|kg|cm|months?\b))|(\d{1,2})[- ]year[- ]old|(\d{1,2}) years?\b', t):
        a = int(next(g for g in m.groups() if g))
        if 2 <= a <= 20:
            ages.add(a)
    rows_ = [(x, a * 12 + 0.5) for x in sexes for a in sorted(ages) if a * 12 + 0.5 in d['kids'][x]]
    for x, am in rows_:
        for c in sorted(cols):
            want = d['kids'][x][am].get(c)
            if want is not None and (half_up(want, dec) == v or half_up(abs(want), dec) == v):
                return {'status': 'row-dataset', 'value': want, 'note': f'{x} at {int(am // 12)} ({am} months), {c}'}
    return None


def holds(nums, v, dec):
    """The row holds the page's number: the same value, or (for a whole number on the page) its rounding."""
    for w in nums:
        if abs(w - v) < 1e-9 or (dec == 0 and half_up(w, 0) == v):
            return True
        if v >= 1e6 and w >= 1e6 and abs(half_up(w / 1e6, dec) - v / 1e6) < 1e-9:
            return True    # "74.9 million" against 74,908,988
    return False


def distinctive(k):
    """A number unlikely to sit in a registry row by chance: a decimal with two or more significant digits (a
    percentage, or not a BMI cut-off), or 1,000 and over that isn't a year."""
    pct = bool(re.match(r'\s?%', k.suf or ''))
    sig = len(re.sub(r'^0+', '', re.sub(r'\D', '', k.text.split(' ')[0])))
    return (k.dec >= 1 and sig >= 2 and (pct or k.value not in CUTS)) or (k.value >= 1000 and not (1800 <= k.value <= 2035 and k.dec == 0))


def dataset_value(s, k, domain, d, keyed_only=False):
    """The dataset a row serves: a keyed cell (the state tables, the age page's average tables, CDC's extended BMI
    file), else any value."""
    v, dec = k.value, k.dec
    if 'kids' in d:
        got = kids_keyed(s, k, d)
        if got is not None:
            return got | {'domain': domain, 'dataset': d['file']}
        if keyed_only:
            return None
        # any value of the file: exactly as stored, or at the page's precision from 4 decimals up
        if distinctive(k) and any(abs(abs(w) - v) < 1e-9 or (dec >= 4 and half_up(abs(w), dec) == v) for w in d['values']):
            return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file'], 'note': 'a value of the file at the printed precision'}
        return None
    head = [norm1(squash(h)) for h in s.unit.get('colHead') or []]
    col = head[k.cell] if s.region == 'table' and k.cell is not None and k.cell < len(head) else ''
    if domain == 'cdc-brfss-state-obesity' and s.region == 'table' and s.cells:
        state = s.cells[1].strip() if re.fullmatch(r'\d+', s.cells[0].strip()) else s.cells[0].strip()
        want = None
        if col in ('2025', '2011'):
            want = d['state'].get(state, {}).get(col, (None,))[0]
        elif col.startswith('95% CI'):
            ci = d['state'].get(state, {}).get('2025')
            same = [t for t in s.toks if t.cell == k.cell]
            if ci:
                want = ci[1] if same and same[0].idx == k.idx else ci[2]
        elif col in ('18-39', '40-59', '60+'):
            want = d['age'].get(state, {}).get(col)
        if want is not None and not math.isnan(want):
            if half_up(want, dec) == v:
                return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file'], 'value': want}
            return {'status': 'not-in-row', 'domain': domain, 'dataset': d['file'], 'value': want, 'note': f'dataset has {want} for {state}, {col}'}
    if domain == 'cdc-brfss-state-obesity' and k.dec == 0 and 2011 <= v <= 2025:
        return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file'], 'note': 'a year of the dataset'}
    if domain == 'cdc-brfss-state-obesity' and k.dec == 0 and v in d['ages'] and re.search(r'\b(18|40|60)\s*[-–]?\s*(39|59|\+)', s.t + ' ' + ' | '.join(head)):
        return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file'], 'note': 'age group of the dataset'}
    if 'aw' in d and s.region == 'table' and s.cells and re.match(r'(\d0)-(\d9)$|80\+$', s.cells[0].strip()):
        cap = s.unit.get('caption', '')
        sex = 'women' if cap.startswith('Women') else 'men' if cap.startswith('Men') else None
        grp = s.unit['cells'][0].strip()
        if k.cell == 0 and sex and grp in d['aw'].get(sex, {}).get('age', {}):
            return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file'], 'note': 'age group of the dataset'}
        key = {'BMI': 'bmi', 'Weight (lb)': 'wt', 'Waist (in)': 'waist'}.get(col)
        node = d['aw'].get(sex, {}).get('age', {}).get(grp, {}).get(key) if sex and key else None
        if node:
            want = node['mean']
            if half_up(want, dec) == v:
                return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file'], 'value': want}
            return {'status': 'not-in-row', 'domain': domain, 'dataset': d['file'], 'value': want, 'note': f'dataset mean {want:.4f} for {sex} {grp}, {col}'}
    if not keyed_only and holds(d['values'], v, dec) and distinctive(k):
        return {'status': 'row-dataset', 'domain': domain, 'dataset': d['file']}
    return None


AUTHOR_RX = re.compile(r"\b([A-Z][a-z]+(?:-[A-Z][a-z]+)?)(?: et al\.?| and [A-Z][a-z]+| & [A-Z][a-z]+)?,?\s*(?:\(\s*)?(?:[A-Z][A-Za-z ]+,\s*)?(?:(?:Am J|JAMA|BMJ|Lancet)[^,;()]*,?\s*)?(1[89]\d\d|20[0-3]\d)\b")


KNOWN_AUTHORS = set(NAMED) | {'Flegal', 'Volpi', 'Quetelet', 'Keys', 'Boer', 'James', 'Hume', 'Caspersen', 'Paruthi', 'Hall',
                                'Ashwell', 'Browning', 'Romero-Corral', 'Prentice', 'Nevill', 'Emmerich', 'Noiman', 'Ansai',
                                'Mifflin', 'Harris', 'Benedict', 'Katch', 'McArdle', 'Heymsfield', 'Kyle', 'Ode', 'Garn'}


def nearest_author(s, k):
    """The author a number sits next to: "Volpi et al., 2004", "Robinson (1983)", "Winter 2014". Only when the
    number is that year, or within 40 characters after the name."""
    t = s.t
    best = None
    for m in AUTHOR_RX.finditer(t):
        name = m.group(1)
        tail = t[m.end(1):m.start(2)]
        if not (name in KNOWN_AUTHORS or re.match(r'\s*et al', tail) or re.fullmatch(r'\s*\(\s*', tail)):
            continue
        if name in ('The', 'In', 'By', 'From', 'Since', 'And', 'For', 'Of', 'Data', 'Source', 'Table', 'Figure', 'August',
                    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October', 'November',
                    'December', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'United',
                    'States', 'Survey', 'Stat', 'Brief', 'Series', 'Guidelines', 'Report', 'Edition', 'Health', 'NHANES',
                    'Copyright', 'Updated', 'Effective', 'Last', 'Physical', 'Activity', 'Americans', 'Nutrition'):
            continue
        if m.start(2) == k.start:
            return name
        d = k.start - m.end(1)
        if 0 <= d <= 40 and (best is None or d < best[0]):
            best = (d, name)
    return best[1] if best else None


DATA_PAGES = {'/obesity-rate-by-state/', '/childhood-obesity-statistics/'}   # every statistic there comes from the rows that serve them


def match_registry(s, k, rows, ds):
    """match_row, and for a number it finds no row for: a row its paragraph links to whose sample_note (or notes)
    holds the same value ("paragraph link": WHO 2004's 23 and 27.5, a sentence after the one that carries the
    link). Not for ordinals ("19th")."""
    got = match_row(s, k, rows, ds)
    if got.get('status') != 'no-row' or re.search(r'\d(?:st|nd|rd|th)\b', k.text):
        return got
    nl = [normurl(h) for h in s.unit.get('blockLinks') or []]
    exact = lambda nums: any(abs(w - k.value) < 1e-9 for w in nums)   # the same value, no rounding
    for r in rows:
        if any(any(L == u or L.startswith(u + '/') or (u and u.startswith(L) and len(L) > 20) for u in r['_urls']) for L in nl):
            if exact(r['_sn']):
                return {'status': 'row', 'domain': r['domain'], 'how': 'paragraph link'}
            if exact(r['_notes']):
                return {'status': 'row-notes', 'domain': r['domain'], 'how': 'paragraph link'}
    return got


def match_row(s, k, rows, ds):
    """Row for one C number: the link next to it, the row manual.json names, a name in the sentence, a distinctive number."""
    v, dec = k.value, k.dec
    links = [l['href'] for l in s.links] or s.unit.get('blockLinks', []) or [l['href'] for l in s.unit.get('links', [])]
    short_block = s.region in ('table', 'svg') or len(sentences(s.unit.get('text', ''))) <= 2
    own = [l['href'] for l in s.links] or (links if short_block else [])
    nl = [normurl(h) for h in own]
    link_rows = [r for r in rows if any(any(L == u or L.startswith(u + '/') or (u and u.startswith(L) and len(L) > 20) for u in r['_urls']) for L in nl)]
    u = s.unit
    labels = ' '.join(x for x in (u.get('caption', ''), u.get('svgLabel', ''), u.get('figcaption', ''), u.get('note', ''),
                                  u.get('ctx', '') if (s.region not in ('table', 'svg') and len(s.t) < 70) else '') if x)
    text = s.t + ' ' + labels
    name_rows = [r for r in rows if any(re.search(r'(?<![A-Za-z])' + re.escape(n) + r'(?![A-Za-z])', text) for n in r['_names'])]
    year = k.dec == 0 and 1800 <= v <= 2035

    def verdict(cands, how):
        for r in cands:
            if holds(r['_sn'], v, dec) or (year and holds(r['_ident'], v, 0)):
                return {'status': 'row', 'domain': r['domain'], 'how': how}
        for r in cands:
            d = ds.get(r['domain'])
            if d:
                got = dataset_value(s, k, r['domain'], d, keyed_only=True)
                if got is not None:
                    return got | {'how': how}
        for r in cands:
            if holds(r['_notes'], v, dec):
                return {'status': 'row-notes', 'domain': r['domain'], 'how': how}
        for r in cands:
            d = ds.get(r['domain'])
            if d:
                got = dataset_value(s, k, r['domain'], d)
                if got is not None:
                    return got | {'how': how}
        r = cands[0]
        return {'status': 'not-in-row', 'domain': r['domain'], 'how': how, 'sample_note': r['sample_note'][:400]}

    if not s.manual_row and re.search(r'waist', s.t, re.I) and re.search(r'\b(35|40)\s*(?:inches|in\b|")|\b(88|102)\s*cm', s.t):
        s.manual_row = 'nhlbi-1998-obesity-guidelines'   # the NIH waist cut-offs: 35 / 40 in, 88 / 102 cm
    if s.manual_row:
        r = [x for x in rows if x['domain'] == s.manual_row]
        if r:
            return verdict(r, 'manual.json')
    if link_rows:
        return verdict(link_rows, 'link')
    near = nearest_author(s, k)
    if near:
        rows_n = [r for r in rows if near in r['_names']]
        if rows_n:
            return verdict(rows_n, 'name')
        return {'status': 'no-row', 'links': links[:4], 'note': f'names {near}, who has no registry row'}
    if name_rows:
        return verdict(name_rows, 'name')
    # the page's own data_source row (research/page-map.csv) first (CMB-031): its dataset at the precision the page
    # prints (a keyed cell that differs is "not in its row" there), and its sample_note or notes for a distinctive
    # number or a year; a small whole number found there by chance goes on to the rules below
    own = next((r for r in rows if r['domain'] == OWN_ROW.get(s.page)), None)
    if own:
        got = own_verdict(s, k, own, ds, year)
        if got is not None:
            return got
    # the rows the registry says serve this page (pages_served), when the sentence or its table/figure names
    # their publisher or survey, or the number is a data year; a number none of them holds is "not in its row"
    # against the page's own row when that row serves the page
    served = [r for r in rows if s.page.strip('/') in [x.strip() for x in r['pages_served'].split(';')]]
    by_number = number_match(s, k, rows) if distinctive(k) else (year_match(s, k, rows) if year else None)
    if served and (s.page in DATA_PAGES or re.search(r'\b(CDC|NCHS|NHANES|BRFSS|E-Stat|survey|measured|self-reported)\b', s.t + ' ' + s.ctx(), re.I)):
        got = verdict(served, 'pages_served')
        if got['status'] == 'not-in-row' and own in served:
            got = got | {'domain': own['domain'], 'sample_note': own['sample_note'][:400]}
        return by_number if got['status'] == 'not-in-row' and by_number and by_number.get('strong') else got
    return by_number or {'status': 'no-row', 'links': links[:4]}


def own_verdict(s, k, r, ds, year):
    """The page's own data_source row (CMB-031), in verdict()'s order: its sample_note (a distinctive number or a
    year), its dataset keyed, its notes (a distinctive number), its dataset at the precision the page prints. None
    when it holds nothing of this number."""
    v, dec = k.value, k.dec
    d = ds.get(r['domain'])
    if (distinctive(k) and holds(r['_sn'], v, dec)) or (year and (holds(r['_sn'], v, 0) or holds(r['_ident'], v, 0))):
        return {'status': 'row', 'domain': r['domain'], 'how': 'data_source'}
    if d:
        got = dataset_value(s, k, r['domain'], d, keyed_only=True)
        if got is not None:
            return got | {'how': 'data_source'}
    if distinctive(k) and holds(r['_notes'], v, dec):
        return {'status': 'row-notes', 'domain': r['domain'], 'how': 'data_source'}
    if d:
        got = dataset_value(s, k, r['domain'], d)
        if got is not None:
            return got | {'how': 'data_source'}
    return None


PUBLISHER_TOKENS = ('NHANES', 'NCHS', 'BRFSS', 'Gallup', 'WHO', 'NHLBI', 'NIDDK', 'Lancet', 'NICE', 'ADA', 'MedlinePlus', 'All of Us')


def number_match(s, k, rows):
    """A distinctive number held by a row, accepted when the number has 4+ digits; or another distinctive number of
    the sentence sits within 60 characters of it in the same row's text; or the sentence names a publisher the row
    carries, when that publisher is specific (on two rows at most) or two or more of its rows hold the number."""
    v, dec = k.value, k.dec
    others = [t for t in s.toks if t is not k and t.kind == 'num' and t.cls == 'C' and distinctive(t) and t.value != v]
    big = len(re.sub(r'\D', '', k.text.split('.')[0])) >= 4 or len(re.sub(r'\D', '', k.text)) >= 5
    said = [p for p in PUBLISHER_TOKENS if re.search(r'\b' + re.escape(p) + r'\b', s.t + ' ' + s.ctx())]
    ident = {r['domain']: ' '.join((r['source'], r['publisher'], r['attribution'], r['domain'])) for r in rows}
    carriers = {p: [r for r in rows if re.search(r'\b' + re.escape(p) + r'\b', ident[r['domain']])] for p in said}
    for field, text, status in (('_sn', 'sample_note', 'row'), ('_notes', 'notes', 'row-notes')):
        for r in rows:
            if not holds(r[field], v, dec):
                continue
            if big:
                return {'status': status, 'domain': r['domain'], 'how': 'number', 'strong': True}
            for p in said:
                if r in carriers[p] and len(carriers[p]) <= 2:
                    return {'status': status, 'domain': r['domain'], 'how': f'number and {p}', 'strong': True}
            near60 = sum(1 for t in others if close_together(r[text], v, dec, t.value, t.dec, 60))
            near20 = any(close_together(r[text], v, dec, t.value, t.dec, 20) for t in others)
            if near60 >= 2 or near20:
                return {'status': status, 'domain': r['domain'], 'how': 'number'}
    return None


def year_match(s, k, rows):
    """A year next to a publisher the sentence names (WHO 1995, NHLBI 1998): that publisher's row whose citation
    (attribution or source) carries the year. Survey names (NHANES, NCHS, CDC, BRFSS) don't count: their years are periods."""
    said = [p for p in ('WHO', 'NHLBI', 'NIH', 'Gallup', 'Lancet', 'NICE', 'ADA', 'MedlinePlus') if re.search(r'\b' + re.escape(p) + r'\b', s.t)]
    for r in rows:
        cite = r['publisher'] + ' ' + r['attribution']
        if any(re.search(r'\b' + re.escape(p) + r'\b', cite) for p in said) and holds(numbers_of(r['attribution'] + ' ' + r['source']), k.value, 0):
            return {'status': 'row', 'domain': r['domain'], 'how': 'publisher and year', 'strong': True}
    return None


def close_together(text, v1, d1, v2, d2, span=150):
    pos = lambda v, d: [m.start() for m in re.finditer(r'(?<![\d.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d])', norm1(text))
                        if abs(float(m.group(1).replace(',', '')) - v) < 1e-9]
    return any(abs(a - b) <= span for a in pos(v1, d1) for b in pos(v2, d2))


# ----------------------------------------------------------------------------------------------------
# sentences of a page
# ----------------------------------------------------------------------------------------------------
def strip_tags(h):
    return squash(html.unescape(re.sub(r'<[^>]+>', ' ', h or '')))


def build_sentences(page, data):
    out = []
    uid = 0
    for u in data['units']:
        region = u['region']
        if region == 'main' and u.get('inResults'):
            region = 'results'
        uid += 1
        if region in ('table', 'svg', 'faq-q'):
            s = Sent(page, u, u['text'], uid, 0, region)
            s.links = u.get('links', [])
            out.append(s)
            continue
        text = u['text']
        for sid, (a, b) in enumerate(sentences(text)):
            s = Sent(page, u, text[a:b], uid, sid, region)
            s.links = [l for l in u.get('links', []) if l['start'] < b and l['end'] > a]
            out.append(s)
    # FAQPage JSON-LD answers: a mirror of the visible answer when the text is the same
    vis = defaultdict(list)
    for s in out:
        if s.region == 'faq-a':
            vis[squash(norm1(s.unit.get('question', ''))).lower()].append(s)
    for q in data['ld']:
        qa = strip_tags(q['a'])
        u = {'region': 'jsonld', 'text': qa, 'links': [], 'heading': 'FAQPage JSON-LD: ' + q['q'], 'question': q['q'], 'ctx': ''}
        twins = vis.get(squash(norm1(q['q'])).lower(), [])
        same_text = twins and re.sub(r'\s', '', norm1(qa)) == re.sub(r'\s', '', norm1(' '.join(t.raw for t in twins)))
        uid += 1
        for sid, (a, b) in enumerate(sentences(qa)):
            s = Sent(page, u, qa[a:b], uid, sid, 'jsonld')
            if same_text:
                twin = [t for t in twins if t.sig == s.sig]
                if twin:
                    s.mirror = twin[0]
            out.append(s)
    for region, text in (('title', data['title']), ('meta', data['meta'])):
        if text:
            u = {'region': region, 'text': text, 'links': [], 'heading': region, 'ctx': ''}
            uid += 1
            for sid, (a, b) in enumerate(sentences(text)):
                out.append(Sent(page, u, text[a:b], uid, sid, region))
    return out


# ----------------------------------------------------------------------------------------------------
# running the checks: B in the audited page, A through the calculators
# ----------------------------------------------------------------------------------------------------
RUN_JS = r"""(subs) => subs.map(j => {
  try {
    if (j.t === 'cat') return { ok: true, v: __A.cat(j.v) };
    if (j.t === 'kcat') return { ok: true, v: __A.kcat(j.v[0], j.v[1], j.v[2]) };
    if (j.t === 'src') { const f = window[j.fn]; return { ok: true, v: !!(f && f.toString().replace(/\s+/g, ' ').includes(j.has)) }; }
    if (j.t === 'srcnum') { const f = window[j.fn]; return { ok: true, v: (f ? f.toString().match(/(?<![\w.])\d+(?:\.\d+)?(?![\w.])/g) || [] : []).map(Number) }; }
    return { ok: true, v: Function('__A', 'return (' + j.e + ');')(window.__A) };
  } catch (e) { return { ok: false, err: String(e) }; }
})"""


def key(v):
    return repr(round(float(v), 6))


def subs_for(s, spec):
    k = spec['kind']
    if k == 'cut':
        pts = set()
        for g, v in spec['bounds'].items():
            st = 10 ** -(s.toks[spec['toks'][g]].dec or 1)
            pts.update([v, v - st, v + st])
        return [{'t': 'cat', 'v': round(p, 6)} for p in sorted(pts)]
    if k == 'boundary':
        return [{'t': 'cat', 'v': spec['value']}, {'t': 'cat', 'v': round(spec['value'] - 0.1, 6)}]
    if k == 'kcut':
        return [{'t': 'kcat', 'v': p} for p in kcut_probes(spec)]
    if k == 'src':
        return [{'t': 'src', 'fn': spec['fn'], 'has': spec['has']}]
    if k == 'srcnum':
        return [{'t': 'srcnum', 'fn': spec['fn']}]
    out = [{'t': 'expr', 'e': spec['expr']}]
    for extra in ('compare_to', 'alt', 'catexpr'):
        if spec.get(extra):
            out.append({'t': 'expr', 'e': spec[extra]})
    return out


def kcut_probes(spec):
    b = spec['bounds']
    out = []
    for g, v in b.items():
        if g == 'lo':
            out += [[v, 100, 20], [v - 0.01, 100, 20]]
        elif g == 'hi':
            out += [[v + 0.99, 100, 20], [v + 1, 100, 20]]
        elif g == 'hx':
            out += [[v - 0.01, 100, 20], [v, 100, 20]]
        elif g == 'p95':
            out += [[96, v - 0.01, 20], [96, v, 20]]
        elif g == 'bmi':
            out += [[96, 100, v - 0.01], [96, 100, v]]
    return out


def exact_half(raw, dec):
    if not isinstance(raw, (int, float)):
        return False
    x = abs(raw) * 10 ** dec
    return abs(x - math.floor(x) - 0.5) < 1e-6


def verdict_num(s, k, spec, vals):
    dec = spec.get('dec', k.dec)
    got = vals[0]
    if not isinstance(got, (int, float)) or isinstance(got, bool):
        return {'status': 'error', 'error': f'computed {got!r}', 'label': spec.get('label', '')}
    if spec.get('compare_to'):
        want = half_up(vals[1], dec)
        page = half_up(got, dec)
        ok = page == want
        return {'status': 'ok' if ok else 'mismatch', 'kind': 'value', 'page': f'{squash(spec["label"].split(" against ")[0].replace("step as written: ", ""))} = {fmt(got, dec + 2)}',
                'computed': f'{fmt(vals[1], dec + 2)} (the first step); at the page\'s {dec} decimals {fmt(page, dec)} vs {fmt(want, dec)}', 'label': spec['label']}
    if spec.get('scale'):
        got = got / spec['scale']
    want = half_up(got, dec)
    sign = -1 if (k.start > 0 and s.raw[k.start - 1] == '−') or (k.start > 0 and s.t[k.start - 1] == '-' and (k.start < 2 or s.t[k.start - 2] in ' (|')) else 1
    page = k.value * sign / spec.get('scale', 1)
    if spec.get('abs'):
        page, want = abs(page), abs(want)
    ok = abs(page - want) < 1e-9 or (sign == -1 and abs(-page - want) < 1e-9 and spec.get('unsigned_ok'))
    r = {'status': 'ok' if ok else 'mismatch', 'kind': 'value', 'page': k.text if sign == 1 else '-' + k.text,
         'computed': fmt(want, dec), 'raw': got, 'label': spec.get('label', '')}
    notes = []
    if spec.get('note'):
        notes.append(spec['note'])
    if exact_half(got, dec):
        notes.append(f'exact half ({fmt(got, dec + 2)}): half up gives {fmt(want, dec)}')
    if not ok and spec.get('alt') and len(vals) > 1 and isinstance(vals[1], (int, float)):
        alt = half_up(vals[1], dec)
        notes.append(f'at age + 0.5 months (the page\'s own note) it is {fmt(alt, dec)}' + (', as printed' if alt == page else ''))
    if not ok and spec.get('implied_bmi'):
        inch, unit = spec['implied_bmi']
        bmi = page * 703 / inch ** 2 if unit == 'lb' else page / (inch * 0.0254) ** 2
        notes.append(f'the printed {k.text} {unit} is BMI {bmi:.2f} at this height')
    if not ok and (re.search(r'~\s*$', k.pre) or re.search(r'\b(about|approximately|around|roughly|nearly)\s*$', k.pre, re.I)):
        r['approx'] = True
    if notes:
        r['note'] = '; '.join(notes)
    if spec.get('catexpr'):
        cat = vals[-1]
        names = cat_group(norm1(spec['cat'])) or []
        cok = cat in names
        r['category'] = {'status': 'ok' if cok else 'mismatch', 'page': spec['cat'], 'computed': cat}
        if cok and norm1(spec['cat']).lower() != cat.lower():
            r['name_differs'] = f'"{spec["cat"]}" = calculator.js "{cat}"'
    return r


def verdict_cut(s, spec, vals, probes):
    cats = {key(p['v']): v for p, v in zip(probes, vals)}
    names, b, toks, phrase = spec['names'], spec['bounds'], spec['toks'], spec['phrase']
    fails, notes = [], []
    L = U = None
    for g, v in b.items():
        tk = s.toks[toks[g]]
        st = 10 ** -(tk.dec or 1)
        here, below, above = cats[key(v)], cats[key(v - st)], cats[key(v + st)]
        two = ' (calculator.js rounds BMI to 0.1 first)' if tk.dec >= 2 else ''
        if g == 'lo':
            if here == below:
                fails.append(f'no category starts at {tk.text}: calculator.js puts {fmt(v - st, tk.dec or 1)} and {tk.text} both in {here}{two}')
            L = here
        elif g == 'hi':
            if here == above:
                fails.append(f'no category ends at {tk.text}: calculator.js puts {tk.text} and {fmt(v + st, tk.dec or 1)} both in {here}{two}')
            U = here
        elif g == 'hx':
            if here == below:
                fails.append(f'no category ends below {tk.text}: calculator.js puts {fmt(v - st, tk.dec or 1)} and {tk.text} both in {here}')
            U = below
        elif g == 'lx':
            L = above
            if names and here in names:
                fails.append(f'"over {tk.text}" leaves {tk.text} out, but calculator.js puts {tk.text} in {here}')
            elif here == above:
                fails.append(f'no category starts just above {tk.text}: calculator.js puts {tk.text} and {fmt(v + st, tk.dec or 1)} both in {here}')
    L = L or CALC_NAMES[0]
    U = U or CALC_NAMES[-1]
    i0, i1 = CALC_NAMES.index(L), CALC_NAMES.index(U)
    covered = CALC_NAMES[min(i0, i1):max(i0, i1) + 1]
    if names is None:
        pass
    elif not set(covered) <= set(names):
        fails.append(f'the range is {", ".join(covered)} in calculator.js; the page calls it "{phrase}"')
    elif set(covered) != set(names):
        notes.append(f'"{phrase}" here is {" + ".join(covered)} in calculator.js')
    elif len(names) == 1 and phrase.lower() != names[0].lower():
        notes.append(f'"{phrase}" = calculator.js "{names[0]}"')
    span = s.t[min(s.toks[i].start for i in toks.values()):max(s.toks[i].end for i in toks.values())]
    r = {'status': 'mismatch' if fails else 'ok', 'kind': 'category', 'page': f'{squash(span)} ({phrase or "no category named"})',
         'computed': '; '.join(fails) if fails else f'{" / ".join(covered)} in calculator.js', 'label': 'category cut-off (getBMICategory)'}
    if notes and not fails:
        r['name_differs'] = notes[0]
    return r


def verdict_kcut(s, spec, vals):
    names, b, phrase = spec['names'], spec['bounds'], spec['phrase']
    fails = []
    n = 0
    for g, v in b.items():
        a, c = vals[n], vals[n + 1]
        n += 2
        txt = s.toks[spec['toks'][g]].text
        if g in ('p95', 'bmi') and not (c in names and a not in names):
            fails.append(f'{txt}: categorizeChildBMI gives {a} just below and {c} at it')
        if g == 'lo' and not (a in names and c not in names):
            fails.append(f'{txt}: categorizeChildBMI gives {a} at it and {c} just below')
        if g in ('hi', 'hx') and not (a in names and c not in names):
            fails.append(f'{txt}: categorizeChildBMI gives {a} just below the next percentile and {c} at it')
    r = {'status': 'mismatch' if fails else 'ok', 'kind': 'category', 'page': f'{" / ".join(s.toks[i].text for i in spec["toks"].values())} ({phrase})',
         'computed': '; '.join(fails) if fails else f'{" / ".join(names)} in categorizeChildBMI', 'label': 'child category cut-off (categorizeChildBMI)'}
    return r


def run_b(pg, jobs):
    allsubs, spans = [], []
    for s, i, spec in jobs:
        sub = subs_for(s, spec)
        spans.append((len(allsubs), len(allsubs) + len(sub), sub))
        allsubs.extend(sub)
    res = pg.evaluate(RUN_JS, allsubs) if allsubs else []
    for (s, i, spec), (a, b, sub) in zip(jobs, spans):
        k = s.toks[i]
        rs = res[a:b]
        bad = [r for r in rs if not r.get('ok')]
        if bad:
            k.result = {'status': 'error', 'error': bad[0].get('err'), 'label': spec.get('label', '')}
            continue
        vals = [r['v'] for r in rs]
        kind = spec['kind']
        if kind == 'cut':
            k.result = verdict_cut(s, spec, vals, sub)
        elif kind == 'kcut':
            k.result = verdict_kcut(s, spec, vals)
        elif kind == 'boundary':
            ok = vals[0] != vals[1]
            k.result = {'status': 'ok' if ok else 'mismatch', 'kind': 'category', 'page': k.text,
                        'computed': f'{vals[1]} below, {vals[0]} at it' if ok else f'no category starts at {k.text} ({vals[0]} on both sides)', 'label': spec['label']}
        elif kind == 'srcnum':
            ok = any(abs(x - k.value) < 1e-12 for x in vals[0])
            k.result = {'status': 'ok' if ok else 'mismatch', 'kind': 'value', 'page': k.text,
                        'computed': f'{spec["fn"]} has the literal {k.text}' if ok else f'{spec["fn"]} has no literal {k.text}', 'label': spec['label']}
        elif kind == 'src':
            k.result = {'status': 'ok' if vals[0] else 'mismatch', 'kind': 'value', 'page': k.text,
                        'computed': f'{spec["fn"]} has "{spec["has"]}"' if vals[0] else f'{spec["fn"]} lacks "{spec["has"]}"', 'label': spec['label']}
        elif kind == 'catname':
            cat = vals[0]
            names = cat_group(norm1(spec['text'])) or []
            ok = cat in names
            k.result = {'status': 'ok' if ok else 'mismatch', 'kind': 'category', 'page': f'{k.text} ({spec["text"]})', 'computed': cat, 'label': spec['label']}
            if ok and spec['text'].lower() != cat.lower():
                k.result['name_differs'] = f'"{spec["text"]}" = calculator.js "{cat}"'
        else:
            k.result = verdict_num(s, k, spec, vals)


CALC = {
    '/': 'standard', '/lean-body-mass/': 'lbm', '/kids-bmi-calculator/': 'kids', '/age-bmi-calculator/': 'age',
}


def same_wording(stated, printed):
    a = re.sub(r'^(a|an|the) ', '', squash(norm1(stated)).lower().strip('"\''))
    return a == squash(norm1(printed)).lower()


def run_a(ctx, base, jobs):
    """Type each worked example into its calculator (390 px) and compare what it prints."""
    by_calc = defaultdict(list)
    for s, i, spec in jobs:
        by_calc[spec['calc']].append((s, i, spec))
    errors = []
    for calc, items in by_calc.items():
        P = CALC[calc]
        pg = ctx.new_page()
        perrs = []
        pg.on('pageerror', lambda e: perrs.append(str(e)))
        pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
        pg.goto(base + calc, wait_until='load')
        for s, i, spec in items:
            k = s.toks[i]
            inp = spec['inputs']
            try:
                unit = 'metric' if spec['units'] == 'metric' else 'imperial'
                pg.click(f'#panel-{P} .unit-btn[data-unit="{unit}"]')
                if unit == 'metric':
                    pg.fill(f'#{P}-height-cm', fmt(inp['cm'], 0 if float(inp['cm']).is_integer() else 1))
                    pg.fill(f'#{P}-weight-kg', fmt(inp['kg'], 0 if float(inp['kg']).is_integer() else 1))
                else:
                    pg.fill(f'#{P}-height-ft', str(int(inp['ft'])))
                    pg.fill(f'#{P}-height-in', fmt(inp['in'], 0 if float(inp['in']).is_integer() else 1))
                    pg.fill(f'#{P}-weight-lbs', fmt(inp['lb'], 0 if float(inp['lb']).is_integer() else 1))
                if 'sex' in inp:
                    pg.select_option(f'#{P}-sex', inp['sex'])
                if 'age' in inp:
                    pg.fill(f'#{P}-years' if P == 'age' else f'#{P}-age-years', str(int(inp['age'])))
                pg.click(f'#calc-{P}-btn')
                pg.wait_for_timeout(150)
                shown = pg.is_visible(f'#{P}-results')
                out = []
                for cl in spec['claims']:
                    rd = cl['read']
                    tk = s.toks[cl['tok']] if 'tok' in cl else None
                    if rd == 'bmi':
                        printed = squash(pg.inner_text(f'#{P}-bmi-value'))
                        out.append({'claim': 'BMI', 'page': tk.text, 'printed': printed, 'ok': printed == fmt(tk.value, 1)})
                    elif rd == 'category':
                        printed = squash(pg.inner_text(f'#{P}-bmi-category'))
                        same = same_wording(cl['text'], printed)
                        out.append({'claim': 'category', 'page': cl['text'], 'printed': printed, 'ok': same,
                                    'wording_only': (not same) and printed in (cat_group(norm1(cl['text'])) or [])})
                    elif rd in ('lbm_kg2', 'fat_kg2'):
                        el = '#lbm-lbm' if rd == 'lbm_kg2' else '#lbm-fat-mass'
                        printed = pg.get_attribute(el, 'data-kg')
                        out.append({'claim': ('lean mass' if rd == 'lbm_kg2' else 'fat mass') + ' kg (data-kg, 0.01)', 'page': tk.text, 'printed': printed,
                                    'ok': abs(float(printed) - tk.value) < 1e-9})
                    elif rd in ('lbm_lb', 'fat_lb', 'lbm_kg', 'fat_kg'):
                        el = '#lbm-lbm' if rd.startswith('lbm') else '#lbm-fat-mass'
                        txt = squash(pg.inner_text(el))
                        m = re.search(r'([\d.]+) lbs' if rd.endswith('lb') else r'([\d.]+) kg', txt)
                        printed = m.group(1) if m else txt
                        out.append({'claim': ('lean mass' if rd.startswith('lbm') else 'fat mass') + (' lbs' if rd.endswith('lb') else ' kg'), 'page': tk.text,
                                    'printed': printed, 'ok': printed == fmt(tk.value, tk.dec)})
                    elif rd == 'bf':
                        printed = squash(pg.inner_text('#lbm-body-fat')).rstrip('%')
                        out.append({'claim': 'body fat %', 'page': tk.text, 'printed': printed, 'ok': printed == fmt(tk.value, tk.dec)})
                bad = [o for o in out if not o['ok']]
                k.result = {'status': 'ok' if shown and not bad else 'mismatch', 'kind': 'calculator',
                            'page': '; '.join(f'{o["claim"]} {o["page"]}' for o in out),
                            'computed': '; '.join(f'{o["claim"]} {o["printed"]}' for o in out) if shown else 'no result shown',
                            'label': f'typed into {calc} ({spec["units"]}): ' + ', '.join(f'{a}={fmt(b, 0 if isinstance(b, (int, float)) and float(b).is_integer() else 2) if isinstance(b, (int, float)) else b}' for a, b in inp.items()),
                            'claims': out}
                if bad and all(o.get('wording_only') for o in bad):
                    k.result['wording_only'] = True
            except Exception as e:
                k.result = {'status': 'error', 'error': str(e)[:300], 'label': f'typed into {calc}'}
        if perrs:
            errors.append(f'{calc}: page errors: ' + '; '.join(perrs))
        pg.close()
    return errors


# ----------------------------------------------------------------------------------------------------
# classification of a page
# ----------------------------------------------------------------------------------------------------
def classify(page, sents, manual, used, rows, ds):
    adds = []
    badges = numbered_badges(page, sents)
    cites = set()
    live = [s for s in sents if s.mirror is None]
    tables = defaultdict(list)
    for s in live:
        if s.region == 'table' and not s.unit.get('isHead'):
            tables[(page, s.unit['table'])].append(s.cells)
    seen = Counter()
    for s in live:
        apply_manual(s, manual, used, adds, seen)
        exclusions(s, badges)
    svg_rules(page, live, adds)
    for s in live:
        table_rules(s, adds, tables)
        kids_cutoff_rules(s, adds)
        kids_range_rule(s, adds)
        formula_source_rule(s, adds)
        hw_bmi_rules(s, adds)
        height_band_rules(s, adds)
        cutoff_rules(s, adds)
        threshold_rule(s, adds)
        category_label_rules(s, adds)
        conversion_rules(s, adds)
        constant_rules(s, adds)
        arithmetic_rules(s, adds)
        scale_rules(s, adds)
        echo_rule(s)
        c_d_rules(s, cites)
        for k in s.toks:
            if k.cls is None:
                k.cls, k.why = 'U', 'unclassified'
    for s in sents:
        if s.mirror is not None:
            for k, m in zip(s.toks, s.mirror.toks):
                k.cls, k.why = m.cls, m.why
    jobs, seen = [], set()
    for s, i in adds:
        if (id(s), i) in seen:
            continue
        seen.add((id(s), i))
        spec = s.toks[i].check
        if spec and spec.get('kind'):
            jobs.append((s, i, spec))
    for s in live:
        for k in s.toks:
            if k.cls == 'C':
                k.row = match_registry(s, k, rows, ds)
    return jobs


def item_of(s, k):
    src = s.mirror.toks[k.idx] if s.mirror is not None and k.idx < len(s.mirror.toks) else k
    d = {'page': s.page, 'region': s.region, 'sentence': s.raw, 'number': k.text, 'value': k.value, 'class': k.cls,
         'why': k.why, 'heading': s.head()}
    if s.mirror is not None:
        d['mirror_of'] = 'the visible FAQ answer (same text)'
    if src.result:
        d['check'] = src.result
    if src.row:
        d['row'] = src.row
    if s.links:
        d['links'] = [l['href'] for l in s.links]
    return d


def sig3(k):
    """A distinctive number with three or more significant digits (29.8, 1,650): unlikely to repeat by chance."""
    return distinctive(k) and len(re.sub(r'^0+', '', re.sub(r'\D', '', k.text.split(' ')[0]))) >= 3


def near_pair(text, v, others, span=60):
    """The text holds v (exactly) with other values of the sentence within span characters of it: two of them,
    or the only one when the sentence has just one other."""
    pos = [(m.start(), float(m.group(1).replace(',', ''))) for m in
           re.finditer(r'(?<![A-Za-z0-9_.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d])', norm1(text or ''))]
    need = min(2, len(set(others)))
    for q in (p for p, w in pos if abs(w - v) < 1e-9):
        near = {o for p, w in pos if abs(p - q) <= span for o in others if abs(w - o) < 1e-9}
        if len(near) >= need:
            return True
    return False


def csv_numbers(text):
    """The numbers in a CSV a page links for download, as (value, decimals), and the URLs its comment lines cite."""
    out, urls = set(), []
    for line in text.splitlines():
        if line.lstrip('"').startswith('#'):
            urls += re.findall(r'https?://[^\s,;)"]+', line)
            continue
        for m in re.finditer(r'(?<![\d.])\d+(?:\.\d+)?(?![\d.])', line):
            t = m.group(0)
            out.add((float(t), len(t.split('.')[1]) if '.' in t else 0))
    return out, urls


def states50(ds):
    return sorted(st for st in ds['cdc-brfss-state-obesity']['state'] if st not in ('District of Columbia', 'Guam', 'Puerto Rico', 'Virgin Islands', 'U.S. Virgin Islands', 'National', 'United States'))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('base')
    ap.add_argument('--out', default=str(HERE))
    ap.add_argument('--pages', default='')
    ap.add_argument('--list-unclassified', action='store_true')
    a = ap.parse_args()
    base = a.base.rstrip('/')
    pages = [p for p in a.pages.split(',') if p] or PAGES
    manual = load_manual()
    used = Counter()
    rows = load_registry()
    OWN_ROW.update(load_own_rows(rows))
    ds = load_datasets()
    calc_js = (REPO / 'assets/js/calculator.js').read_text(encoding='utf-8')
    lms_js = (REPO / 'assets/js/cdc-bmi-lms.js').read_text(encoding='utf-8')
    D = {'brfss': {st: {yr: v[0] for yr, v in ys.items()} for st, ys in ds['cdc-brfss-state-obesity']['state'].items()},
         'age': ds['cdc-brfss-state-obesity']['age'], 'states': states50(ds)}
    all_sents, page_errors, skipped, a_jobs, page_csvs = {}, {}, [], [], {}
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
        ctx = browser.new_context(viewport=VIEWPORT)
        for page in pages:
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
            try:
                resp = pg.goto(base + page, wait_until='load')
                if resp is None or resp.status != 200:
                    raise RuntimeError(f'HTTP {resp.status if resp else "no response"}')
                data = pg.evaluate(EXTRACT_JS)
                if not data['units']:
                    raise RuntimeError('no text found in <main>')
                if not data['hasCalc']:
                    pg.add_script_tag(content=calc_js)
                if not data['hasLMS']:
                    pg.add_script_tag(content=lms_js)
                pg.evaluate(HELPERS_JS)
                pg.evaluate('d => { window.__D = d; }', D)
                csvs = []
                for h in pg.eval_on_selector_all('a[href$=".csv"]', 'els => [...new Set(els.map(e => e.getAttribute("href")))]'):
                    url = base + h if h.startswith('/') else h
                    if url.startswith(base):
                        got = pg.request.get(url)
                        if got.ok:
                            nums, urls = csv_numbers(got.text())
                            cited = [r['domain'] for r in rows if any(normurl(u) in r['_urls'] for u in urls)]
                            csvs.append((site_link(url, base), nums, cited))
                page_csvs[page] = csvs
            except Exception as e:
                skipped.append(f'{page}: {e}')
                pg.close()
                continue
            sents = build_sentences(page, data)
            jobs = classify(page, sents, manual, used, rows, ds)
            run_b(pg, [j for j in jobs if j[2]['kind'] != 'A'])
            a_jobs.extend(j for j in jobs if j[2]['kind'] == 'A')
            all_sents[page] = sents
            page_errors[page] = errs
            pg.close()
        a_errors = run_a(ctx, base, a_jobs)
        browser.close()
    report = write_report(base, pages, all_sents, skipped, page_errors, a_errors, manual, used, Path(a.out), rows, page_csvs)
    unclassified = report['unclassified']
    T = report['totals']
    print(f"pages audited {report['pages_audited']} of {len(pages)}, skipped {len(skipped)}; numbers {report['numbers']}: "
          f"A {T['A']}, B {T['B']}, C {T['C']}, D {T['D']}, excluded {T['X']}, unclassified {len(unclassified)}; "
          f"A/B checks {report['checks_run']}, mismatches {report['mismatches']}; C no row {report['c_no_row']}, "
          f"C not in its row {report['c_not_in_row']}; check errors {len(report['check_errors'])}")
    print(f'report written: {Path(a.out) / "report.md"} and {Path(a.out) / "report.json"}')
    for sk in skipped:
        print('SKIPPED', sk)
    if a.list_unclassified or unclassified:
        for u in unclassified[:500]:
            print('UNCLASSIFIED', u['page'], '|', u['region'], '|', u['number'], '|', u['sentence'][:200])
    for e in report['check_errors'][:60]:
        print('CHECK ERROR', e)
    for n in range(len(manual)):
        if used[n] == 0:
            print('MANUAL ENTRY UNUSED', manual[n].get('page'), manual[n].get('sig'))
    ok = not skipped and not unclassified and not report['check_errors'] and report['pages_audited'] == len(pages)
    sys.exit(0 if ok else 1)


# ----------------------------------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------------------------------
STOP = set('the a an of and or to in for on at by with from is are was were be as that this it its their his her '
           'than more less about over under after before between into per each all any not no can may also which who'.split())


def content_words(t):
    return {w for w in re.findall(r'[a-z][a-z-]{2,}', norm1(t).lower()) if w not in STOP}


def md_cell(t, n=None):
    t = squash(str(t)).replace('|', '\\|')
    if n and len(t) > n:
        t = t[:n - 1] + '…'
    return t


def write_report(base, pages, all_sents, skipped, page_errors, a_errors, manual, used, out, rows=(), page_csvs=None):
    items = []
    per = {}
    check_errors = []
    unclassified = []
    for page in pages:
        sents = all_sents.get(page)
        if sents is None:
            continue
        P = {'page': page, 'totals': Counter(), 'jsonld_mirrors': 0, 'mismatches': [], 'c_no_row': [], 'c_not_in_row': [],
             'c_rows': Counter(), 'c_row_domains': Counter(), 'names_differ': [], 'd': [], 'excluded': Counter(),
             'checks_ok': 0, 'page_errors': page_errors.get(page, [])}
        for s in sents:
            for k in s.toks:
                it = item_of(s, k)
                items.append(it)
                if s.mirror is not None:
                    P['jsonld_mirrors'] += 1
                    continue
                P['totals'][k.cls] += 1
                if k.cls == 'X':
                    P['excluded'][k.why] += 1
                if k.cls == 'U':
                    unclassified.append(it)
                if k.cls == 'D':
                    P['d'].append({'number': k.text, 'why': k.why, 'sentence': s.raw})
                r = k.result
                if r:
                    if r.get('status') == 'error':
                        check_errors.append(f'{page}: {k.text} in "{s.raw[:120]}": {r.get("error")}')
                    elif r.get('status') == 'mismatch' or (r.get('category') or {}).get('status') == 'mismatch':
                        m = {'class': k.cls, 'page_value': r.get('page'), 'computed': r.get('computed'), 'check': r.get('label', ''),
                             'sentence': s.raw, 'region': s.region}
                        if r.get('status') == 'ok' and r.get('category'):
                            m['page_value'] = r['category']['page']
                            m['computed'] = 'calculator.js category: ' + r['category']['computed']
                            m['check'] = 'category of that BMI (getBMICategory)'
                        elif r.get('category', {}).get('status') == 'mismatch':
                            m['computed'] += '; category: page ' + r['category']['page'] + ', calculator.js ' + r['category']['computed']
                        if r.get('wording_only'):
                            m['wording_only'] = True
                        if r.get('approx'):
                            m['approx'] = True
                        if r.get('note'):
                            m['note'] = r['note']
                        P['mismatches'].append(m)
                    else:
                        P['checks_ok'] += 1
                    if r.get('name_differs'):
                        P['names_differ'].append(r['name_differs'])
                if k.cls == 'C' and k.row:
                    st = k.row['status']
                    P['c_rows'][st] += 1
                    if k.row.get('domain'):
                        P['c_row_domains'][k.row['domain']] += 1
                    if st == 'no-row':
                        links = k.row.get('links') or []
                        P['c_no_row'].append({'number': k.text, 'value': k.value, 'sentence': s.raw, 'links': links, 'why': k.why,
                                              'region': s.region, 'suffix': squash(k.suf[:12])})
                    elif st == 'not-in-row':
                        c = {'number': k.text, 'sentence': s.raw, 'row': k.row.get('domain'), 'how': k.row.get('how'),
                             'note': k.row.get('note') or k.row.get('sample_note', '')[:300], 'region': s.region,
                             'table': s.unit.get('caption') or s.unit.get('heading') if s.region == 'table' else None}
                        others = [t for t in s.toks if t is not k and t.kind == 'num' and sig3(t) and t.value != k.value]
                        if sig3(k) and others:
                            # another row holds this number with another number of the sentence within 60 characters
                            also = [f'{r["domain"]} ({col})' for r in rows if r['domain'] != c['row']
                                    for col in ('sample_note', 'notes') if near_pair(r[col], k.value, [t.value for t in others])]
                            if also:
                                c['also_in'] = list(dict.fromkeys(also))[:3]
                        inc = [h for h, nums, cited in (page_csvs or {}).get(page, []) if c['row'] in cited and (k.value, k.dec) in nums]
                        if inc:
                            c['page_csv'] = inc[0]
                        P['c_not_in_row'].append(c)
        P['score'] = len(P['mismatches']) + len(P['c_no_row'])
        per[page] = P
    order = sorted(per.values(), key=lambda P: (-P['score'], -len(P['c_not_in_row']), pages.index(P['page'])))
    # no-row claims that repeat on 2 or more pages: sentences that share their numbers (with units) and wording
    def unit_of(c):
        m = re.match(r'\s?(%|percent|lbs?|kg|cm|years?|minutes?|hours?|kcal|calories|cal\b|million|points?|mmHg|inches|in\b)?', c['suffix'])
        return (m.group(1) or '').lower().replace('percent', '%')
    nr = []
    for P in per.values():
        by_sent = {}
        for c in P['c_no_row']:
            e = by_sent.setdefault(c['sentence'], {'page': P['page'], 'sentence': c['sentence'], 'numbers': [], 'links': c['links'], 'keys': set()})
            e['numbers'].append(c['number'])
            e['keys'].add((c['value'], unit_of(c)))
        nr.extend(by_sent.values())
    parent = list(range(len(nr)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    words = [content_words(e['sentence']) for e in nr]
    for i in range(len(nr)):
        for j in range(i + 1, len(nr)):
            if nr[i]['page'] == nr[j]['page']:
                continue
            shared = nr[i]['keys'] & nr[j]['keys']
            if not shared:
                continue
            jac = len(words[i] & words[j]) / max(1, len(words[i] | words[j]))
            strong = {k for k in shared if k[1] or k[0] != int(k[0]) or k[0] >= 1000}
            if (len(shared) >= 2 and jac >= 0.12) or (strong and jac >= 0.2) or jac >= 0.45:
                parent[find(i)] = find(j)
    clusters = defaultdict(list)
    for i, e in enumerate(nr):
        clusters[find(i)].append(e)
    repeated = []
    for members in clusters.values():
        pages_in = sorted({e['page'] for e in members})
        if len(pages_in) < 2:
            continue
        counts = Counter(k for e in members for k in e['keys'])
        common = [k for k, n in counts.items() if len({e['page'] for e in members if k in e['keys']}) >= 2]
        label = ', '.join(sorted({(fmt(v, 0) if v == int(v) else repr(v)) + (u if u == '%' else (' ' + u if u else '')) for v, u in common}, key=lambda x: x))
        repeated.append({'number': label, 'pages': pages_in, 'count': len(members),
                         'examples': [{'page': e['page'], 'sentence': e['sentence'], 'numbers': e['numbers'], 'links': e['links']} for e in members]})
    repeated.sort(key=lambda r: (-len(r['pages']), -r['count'], r['number']))
    totals = Counter()
    for P in per.values():
        totals.update(P['totals'])
    report = {
        'generated_by': 'research/stage1-audit/audit.py', 'base': base, 'viewport': f'{VIEWPORT["width"]}x{VIEWPORT["height"]}',
        'pages_audited': len(per), 'pages_skipped': skipped, 'numbers': sum(totals.values()),
        'totals': {c: totals.get(c, 0) for c in 'ABCDXU'},
        'mismatches': sum(len(P['mismatches']) for P in per.values()),
        'c_no_row': sum(len(P['c_no_row']) for P in per.values()),
        'c_not_in_row': sum(len(P['c_not_in_row']) for P in per.values()),
        'c_not_in_row_in_page_csv': sum(1 for P in per.values() for c in P['c_not_in_row'] if c.get('page_csv')),
        'c_not_in_row_also_in_other_row': sum(1 for P in per.values() for c in P['c_not_in_row'] if c.get('also_in')),
        'c_status': dict(sum((P['c_rows'] for P in per.values()), Counter())),
        'checks_run': sum(P['checks_ok'] + len(P['mismatches']) for P in per.values()),
        'check_errors': check_errors + a_errors, 'unclassified': unclassified,
        'manual_entries': len(manual), 'manual_entries_used': sum(1 for n in range(len(manual)) if used[n]),
        'worst10': [{'page': P['page'], 'score': P['score'], 'mismatches': len(P['mismatches']), 'c_no_row': len(P['c_no_row']),
                     'c_not_in_row': len(P['c_not_in_row'])} for P in order[:10]],
        'repeated_no_row': repeated,
        'pages': [{**{k: v for k, v in P.items() if k not in ('totals', 'c_rows', 'c_row_domains', 'excluded')},
                   'totals': dict(P['totals']), 'c_rows': dict(P['c_rows']), 'c_row_domains': dict(P['c_row_domains']),
                   'excluded': dict(P['excluded'])} for P in order],
        'items': items,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / 'report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str), encoding='utf-8')
    (out / 'report.md').write_text(render_md(report, order), encoding='utf-8')
    return report


def site_link(u, base):
    return u[len(base):] if base and u.startswith(base) else u


def render_md(R, order):
    T = R['totals']
    L = []
    L.append('# Stage 1 audit: every number on the 25 pages Stage 1 hadn\'t covered (CMB-029)')
    L.append('')
    L.append(f'Generated by `research/stage1-audit/audit.py {R["base"]}` at {R["viewport"]} px. '
             'Classes: **A** calculator claim (typed into the calculator), **B** our arithmetic (recomputed with '
             'calculator.js in the page), **C** outside fact (matched to `research/data-sources.csv`), **D** other '
             '(list only), X excluded (byline dates, list numbering, the address, numbers in URLs). '
             'Method and rules: the docstring of `audit.py`; hand classifications: `manual.json`.')
    L.append('')
    L.append(f'- Pages audited: **{R["pages_audited"]}** of 25, skipped: **{len(R["pages_skipped"])}**')
    L.append(f'- Numbers: **{R["numbers"]}** — A {T["A"]}, B {T["B"]}, C {T["C"]}, D {T["D"]}, excluded {T["X"]}, unclassified {T["U"]}'
             ' (FAQPage JSON-LD answers that repeat a visible answer word for word are counted once, under the visible answer)')
    cs = R['c_status']
    L.append(f'- A and B checks run: **{R["checks_run"]}**, mismatches: **{R["mismatches"]}**')
    L.append(f'- C: in a row\'s sample_note {cs.get("row", 0)}, in its notes only {cs.get("row-notes", 0)}, in the dataset the row serves '
             f'{cs.get("row-dataset", 0)}, **not in its row {R["c_not_in_row"]}**, **no row {R["c_no_row"]}**. Of the numbers not in '
             f'their row, {R["c_not_in_row_in_page_csv"]} are in the CSV their page links for download and '
             f'{R["c_not_in_row_also_in_other_row"]} are held by another row (both noted where they occur)')
    L.append('')
    L.append('## The 10 worst pages')
    L.append('')
    L.append('Score = A and B mismatches + C with no row. "Not in its row" is listed per page and breaks ties.')
    L.append('')
    L.append('| # | Page | Score | A/B mismatches | C no row | C not in its row |')
    L.append('|---|---|---|---|---|---|')
    for n, w in enumerate(R['worst10'], 1):
        L.append(f'| {n} | `{w["page"]}` | {w["score"]} | {w["mismatches"]} | {w["c_no_row"]} | {w["c_not_in_row"]} |')
    L.append('')
    L.append('## No-row claims that repeat across pages')
    L.append('')
    L.append('The same number (with its unit) in sentences that share their wording, on 2 or more pages, with no registry row.')
    L.append('')
    if not R['repeated_no_row']:
        L.append('None.')
    for r in R['repeated_no_row']:
        L.append(f'- **{md_cell(r["number"])}** on {len(r["pages"])} pages: ' + ', '.join(f'`{p}`' for p in r['pages']))
        shown = set()
        for e in r['examples']:
            if e['page'] in shown:
                continue
            shown.add(e['page'])
            L.append(f'  - `{e["page"]}`: "{md_cell(e["sentence"], 230)}"' + (f' — link: {", ".join(site_link(x, R["base"]) for x in e["links"][:2])}' if e['links'] else ' — no link'))
    L.append('')
    L.append('## Pages, worst first')
    for P in R['pages']:
        L.append('')
        L.append(f'### `{P["page"]}` — score {P["score"]}')
        t = P['totals']
        L.append('')
        L.append(f'Numbers: A {t.get("A", 0)}, B {t.get("B", 0)}, C {t.get("C", 0)}, D {t.get("D", 0)}, excluded {t.get("X", 0)}'
                 + (f', unclassified {t.get("U", 0)}' if t.get('U') else '')
                 + (f' (+{P["jsonld_mirrors"]} in FAQPage JSON-LD, same text as the visible answers)' if P['jsonld_mirrors'] else '')
                 + f'. A/B checks passed: {P["checks_ok"]}, mismatches: {len(P["mismatches"])}.'
                 + (' C rows: ' + ', '.join(f'{k} {v}' for k, v in sorted(P['c_row_domains'].items(), key=lambda x: -x[1])) + '.' if P['c_row_domains'] else ''))
        if P['page_errors']:
            L.append(f'Page errors: {"; ".join(P["page_errors"])}')
        if P['mismatches']:
            L.append('')
            L.append('**A and B mismatches**')
            L.append('')
            L.append('| Class | Page | Computed | Check | Sentence |')
            L.append('|---|---|---|---|---|')
            for m in P['mismatches']:
                tag = ' (wording only)' if m.get('wording_only') else ''
                tag += ' (approximate)' if m.get('approx') else ''
                L.append(f'| {m["class"]}{tag} | {md_cell(m["page_value"], 80)} | {md_cell(m["computed"], 160)} | {md_cell(m["check"], 90)} | {md_cell(m["sentence"], 200)} |')
        if P['c_no_row']:
            L.append('')
            L.append(f'**C with no registry row ({len(P["c_no_row"])} numbers)**')
            L.append('')
            by_sent = {}
            for c in P['c_no_row']:
                by_sent.setdefault(c['sentence'], {'numbers': [], 'links': c['links']})['numbers'].append(c['number'])
            for sent, e in by_sent.items():
                link = (' — link: ' + ', '.join(site_link(x, R['base']) for x in dict.fromkeys(e['links'][:3]))) if e['links'] else ' — no link'
                L.append(f'- **{md_cell(", ".join(e["numbers"]))}**: "{md_cell(sent, 260)}"{link}')
        if P['c_not_in_row']:
            L.append('')
            L.append(f'**C not in its row ({len(P["c_not_in_row"])})**')

            def listing(items, pre):
                byrow = defaultdict(list)
                for c in items:
                    byrow[(c['row'], c.get('table'))].append(c)
                for (row, table), lst in byrow.items():
                    if table and len(lst) > 6:
                        L.append(f'{pre}- row `{row}`, table "{md_cell(table, 90)}": {len(lst)} values not in the row (' + ', '.join(c['number'] for c in lst[:24]) + (' …' if len(lst) > 24 else '') + ')' + (f'. {md_cell(lst[0]["note"], 160)}' if lst[0].get('note', '').startswith('dataset') else ''))
                        continue
                    for c in lst:
                        L.append(f'{pre}- row `{row}` ({c["how"]}): **{md_cell(c["number"])}** in "{md_cell(c["sentence"], 220)}"'
                                 + (f' — {md_cell(c["note"], 140)}' if c.get('note', '').startswith('dataset') else '')
                                 + (' — also in ' + ', '.join(f'`{x.split(" ")[0]}` {x.split(" ", 1)[1]}' for x in c['also_in']) if c.get('also_in') else ''))
            plain = [c for c in P['c_not_in_row'] if not c.get('page_csv')]
            incsv = [c for c in P['c_not_in_row'] if c.get('page_csv')]
            L.append('')
            listing(plain, '')
            if incsv:
                L.append('- In the CSV this page links for download (' + ', '.join(f'`{h}`' for h in dict.fromkeys(c['page_csv'] for c in incsv)) + '), which cites '
                         f'the row\'s source: the page agrees with its own data file, the check against the source is still open ({len(incsv)} numbers):')
                listing(incsv, '  ')
        if P['names_differ']:
            L.append('')
            L.append('Category names that differ from calculator.js (same category, not counted as mismatches): '
                     + '; '.join(f'{n} ×{c}' if c > 1 else n for n, c in Counter(P['names_differ']).items()))
        if P['d']:
            L.append('')
            L.append(f'D, listed ({len(P["d"])}): ' + '; '.join(f'{md_cell(d["number"])} ({md_cell(d["why"].replace(" (manual.json)", ""), 40)})' for d in P['d'][:80]) + (' …' if len(P['d']) > 80 else ''))
        if P['excluded']:
            L.append('')
            L.append('Excluded: ' + ', '.join(f'{k} {v}' for k, v in P['excluded'].items()) + '.')
    L.append('')
    if R['check_errors']:
        L.append('## Check errors')
        L.extend(f'- {e}' for e in R['check_errors'])
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
