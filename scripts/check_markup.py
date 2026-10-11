#!/usr/bin/env python3
"""Tag-balance gate + content-stable --text snapshot for calculatemybmi.

Default mode: parse each HTML file and report
  - end tags that match no open element
  - elements left open and closed implicitly by a later end tag
    (exceptions: p, li, td, th, tr, thead, tbody, option, dt, dd — HTML spec allows implicit close)
  - elements never closed before EOF
  - any p, div, section, ul, ol, li, table, h1-h6 or footer opened while a strong, b or em is open
Print file, issue, character offset and 80 chars of context. Exit 1 on any finding.

--text mode: visible text (outside script, style, template) as one whitespace-collapsed
stream, one sentence per line; then every a href and img src in order; then a SHA-256
of each JSON-LD block, of the title, and of each meta tag. Diffing two --text outputs
shows any content change and only content changes.

Usage:
  check_markup.py FILE [FILE ...]            # gate mode
  check_markup.py --text FILE [FILE ...]     # text snapshot (stdout)
"""
import sys
import re
import hashlib
from html.parser import HTMLParser

VOID = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
}
# Elements the HTML spec allows to be closed implicitly by a following
# start/end tag — leaving them "open" is not a bug.
IMPLICIT_CLOSE = {'p', 'li', 'td', 'th', 'tr', 'thead', 'tbody', 'option', 'dt', 'dd'}
INLINE_EMPH = {'strong', 'b', 'em'}
# Block-level containers that should not open while inline emphasis is still open.
BLOCK_UNDER_EMPH = {
    'p', 'div', 'section', 'ul', 'ol', 'li', 'table', 'footer',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
}
# Elements whose content is CDATA-like and never counted as visible text or markup.
RAW_TEXT = {'script', 'style', 'template'}


class MarkupChecker(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.stack = []   # list of (tag, offset)
        self.issues = []  # list of (offset, kind, detail)

    def _offset(self):
        line, col = self.getpos()
        # Translate line/col back to a character offset in self.src.
        lines = self.src.split('\n')
        # getpos is 1-indexed line, 0-indexed col
        off = sum(len(l) + 1 for l in lines[: line - 1]) + col
        return min(off, len(self.src))

    def _record(self, offset, kind, detail):
        self.issues.append((offset, kind, detail))

    def handle_starttag(self, tag, attrs):
        off = self._offset()
        if tag in VOID:
            return
        # Block-under-emphasis check.
        if tag in BLOCK_UNDER_EMPH:
            for open_tag, _ in self.stack:
                if open_tag in INLINE_EMPH:
                    self._record(
                        off,
                        'block-under-emph',
                        f'<{tag}> opened while <{open_tag}> is still open',
                    )
                    break
        self.stack.append((tag, off))

    def handle_startendtag(self, tag, attrs):
        # Self-closing in HTML has no effect for non-void elements, so this is
        # fine for void tags (which we ignore anyway).
        return

    def handle_endtag(self, tag):
        off = self._offset()
        if tag in VOID:
            # </br> and friends — ignore.
            return
        # Walk stack from top; mark everything above the matching tag as
        # implicitly closed (an error unless the element is in IMPLICIT_CLOSE).
        for i in range(len(self.stack) - 1, -1, -1):
            open_tag, open_off = self.stack[i]
            if open_tag == tag:
                # Everything above i was closed implicitly by this end tag.
                for j in range(len(self.stack) - 1, i, -1):
                    inner_tag, inner_off = self.stack[j]
                    if inner_tag not in IMPLICIT_CLOSE:
                        self._record(
                            inner_off,
                            'implicit-close',
                            f'<{inner_tag}> left open, closed implicitly by </{tag}>',
                        )
                del self.stack[i:]
                return
        # No open element matched this end tag.
        self._record(off, 'orphan-end', f'</{tag}> matches no open element')

    def close(self):
        # Report every element never closed before EOF (minus IMPLICIT_CLOSE,
        # which the spec lets end-of-parent close silently).
        super().close()
        for tag, off in self.stack:
            if tag in IMPLICIT_CLOSE:
                continue
            self._record(off, 'never-closed', f'<{tag}> never closed')
        self.stack.clear()


def context_at(src, offset, width=80):
    start = max(0, offset)
    snippet = src[start : start + width]
    snippet = re.sub(r'\s+', ' ', snippet)
    return snippet.strip()


def gate_file(path):
    """Return list of (offset, kind, detail) issues for path."""
    with open(path, encoding='utf-8') as f:
        src = f.read()
    parser = MarkupChecker(src)
    try:
        parser.feed(src)
        parser.close()
    except Exception as exc:
        parser.issues.append((0, 'parse-error', str(exc)))
    return src, parser.issues


# ---------------- --text mode ----------------

TAG_RE = re.compile(r'<[^>]+>', re.DOTALL)
RAW_BLOCK_RE = re.compile(
    r'<(script|style|template)\b[^>]*>.*?</\1\s*>',
    re.DOTALL | re.IGNORECASE,
)
JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.DOTALL | re.IGNORECASE)
META_RE = re.compile(r'<meta\b[^>]*/?>', re.IGNORECASE)
HREF_RE = re.compile(r'<a\b[^>]*\bhref=["\']([^"\']*)["\']', re.IGNORECASE)
IMG_RE = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']*)["\']', re.IGNORECASE)
SENT_SPLIT = re.compile(r'(?<=[\.\?\!])\s+(?=[A-Z0-9])')


def visible_text(src):
    # Strip raw-content blocks first so their body text does not leak.
    stripped = RAW_BLOCK_RE.sub(' ', src)
    text = TAG_RE.sub(' ', stripped)
    import html
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def text_snapshot(path):
    with open(path, encoding='utf-8') as f:
        src = f.read()
    out = []
    out.append(f'# {path}')
    out.append('## visible-text')
    text = visible_text(src)
    sentences = SENT_SPLIT.split(text) if text else []
    for s in sentences:
        s = s.strip()
        if s:
            out.append(s)
    out.append('## links')
    for href in HREF_RE.findall(src):
        out.append(f'a href={href}')
    for isrc in IMG_RE.findall(src):
        out.append(f'img src={isrc}')
    out.append('## head-hashes')
    title_match = TITLE_RE.search(src)
    out.append(f'title sha256={sha256(title_match.group(1).strip()) if title_match else "none"}')
    for meta in META_RE.findall(src):
        out.append(f'meta sha256={sha256(meta.strip())}')
    for i, block in enumerate(JSONLD_RE.findall(src)):
        out.append(f'jsonld[{i}] sha256={sha256(block.strip())}')
    return '\n'.join(out) + '\n'


# ---------------- CLI ----------------

def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == '--text':
        files = argv[1:]
        for path in files:
            sys.stdout.write(text_snapshot(path))
        return 0
    files = argv
    any_fail = False
    for path in files:
        src, issues = gate_file(path)
        if not issues:
            print(f'{path}: 0 issues')
            continue
        any_fail = True
        print(f'{path}: {len(issues)} issue(s)')
        for off, kind, detail in issues:
            ctx = context_at(src, off)
            print(f'  @{off} [{kind}] {detail}')
            print(f'    …{ctx}…')
    return 1 if any_fail else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
