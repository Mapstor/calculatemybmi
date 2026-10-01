# Batch C1 — Raptive-only consent + two broken reference lists (calculatemybmi)
Prepared in chat, 1 Oct 2026. 77 exact edits across 37 files, tested on a copy of HEAD 3d2b73e: check_structure 34/34, number audit clean, widget 14/14, JSON-LD and inline JS parse on every page, and a simulated US and EU visitor both load GA without errors.

What it changes:
- Every page's <head>: the home-made Consent Mode defaults (timezone guess, 0.5 s wait) are replaced by Raptive's "Standard GA delay script", verbatim (help.raptive.com/hc/en-us/articles/47199949578651).
- /assets/js/consent-banner.js (the GA loader): defines gtag itself. Raptive's script only defines it for European visitors, so without this GA would break for all US traffic.
- Footer on every page: dead "Cookie settings" text removed (Raptive injects its own US opt-out link and EU pop-up).
- /privacy/ section 6 rewritten to describe the Raptive-only setup; /terms/ no longer points to the removed footer link.
- /women-bmi-calculator/ and /new-bmi-calculator/: the reference lists were truncated, with an old footer remnant spliced in, an empty item, a Mayo-title remnant and unclosed tags. Rebuilt as a closed list with a linked WHO fact sheet entry.
- research/HANDOFF.md: logs the consent decision and this batch.

## Rules
Do not edit any file by hand: only apply_fixes.py changes files. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/consent-c1/`. Anything else: STOP and report.
1. `python3 research/consent-c1/apply_fixes.py --dry-run` — must print `DRY RUN — applied 77 edits to 37 files`. If it prints ABORT, STOP and report its full output.
2. `python3 research/consent-c1/apply_fixes.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `34/34 pages pass`
   3.2 `node --check assets/js/consent-banner.js` → no output, exit 0
   3.3 `echo "cookie:$(grep -rl --include=*.html 'Cookie settings' . | grep -v research/ | wc -l) raptive:$(grep -rl --include=*.html 'function isUserInEurope()' . | grep -v research/ | wc -l) old:$(grep -rl --include=*.html 'Consent Mode v2 defaults' . | grep -v research/ | wc -l)"` → `cookie:0 raptive:35 old:0`
   3.4 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
4. Commit: `git add $(git diff --name-only --diff-filter=M) research/consent-c1/` then `git status --porcelain` must be empty, then
   `git commit -m "fix(consent): Raptive-only setup (Raptive GA delay script, GA loader defines gtag, dead Cookie settings text removed, privacy/terms updated); rebuild truncated reference lists on women + new-bmi calculators"`
5. REPORT — print exactly this, nothing after it:
```
REPORT consent-c1
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <ok/fail> | 3.3 <line> | 3.4 <line>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -42>
final status: <git status --porcelain, or "clean">
```
