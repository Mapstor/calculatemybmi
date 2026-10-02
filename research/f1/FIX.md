# Batch F1 — final check fixes (calculatemybmi)
Prepared in chat, 2 Oct 2026 from the live commit c952de3 (archive identical to the chat working copy). 40 exact edits across 9 files, tested: check_structure 34/34, number audit clean, JSON-LD and inline JS parse on every page, 0 dead anchors, FAQ schema parity intact, sitemap XML valid (34 URLs).

Final scan of all 34 pages: 0 never-cite links, 0 broken internal links, 0 broken sentences, 0 named-expert quotes, 0 empty FAQ answers. Fixed here:
- 11 empty section headings left by earlier content removals (headings followed directly by another heading): /blog/bmi-and-health-risks/ (3), /blog/what-is-bmi/ (4), /blog/bmi-chart-explained/, /blog/healthy-bmi-range/, /kids-bmi-calculator/, /new-bmi-calculator/ (1 each), plus one table-of-contents link that pointed to a removed heading.
- Long unbreakable words (e.g. a visible URL on /blog/underweight-bmi-risks/) now wrap inside the content area on phones: `main { overflow-wrap: break-word; }` in /assets/css/styles.css.
- sitemap.xml: lastmod set to 2026-10-02 for the 26 pages whose content changed between 30 Sep and 2 Oct (genuine content changes only; nav/consent-only pages untouched).
- research/HANDOFF.md: final check recorded.

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/f1/`. Anything else: STOP and report.
1. `python3 research/f1/apply_fixes.py --dry-run` — must print `DRY RUN — applied 40 edits to 9 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/f1/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.3 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.4 `python3 -c "import xml.dom.minidom as m; print(len(m.parse('sitemap.xml').getElementsByTagName('url')))"` → `34`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/f1/`; `git status --porcelain` must be empty; then
   `git commit -m "fix: final check (empty section headings, long-word wrapping on phones, sitemap lastmod for content-changed pages)"`
5. REPORT — print exactly this, nothing after it:
```
REPORT f1
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -15>
final status: <git status --porcelain, or "clean">
```
