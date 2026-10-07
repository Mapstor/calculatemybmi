# Batch B2 — new page /body-fat-calculator/ (calculatemybmi)
Prepared in chat, 4 Oct 2026 on a copy of the live commit (B1 pushed). Tested there: check_structure 39/39, research/f1/verify.py clean, number audit clean, ledger check OK, registry check: no violation for this page, calculator test 18/18 and body-fat chart test 13/13 in a simulated browser, phone render checked.

What it adds:
- /body-fat-calculator/ — three published methods in the site's tool design: tape measure (Navy/Army circumference equations, inches, metric converted), Jackson-Pollock 3-site skinfolds with Siri, and the Deurenberg 1991 BMI formula. Shows every method you have inputs for, the spread between them, fat and lean mass, the provisional healthy range (Gallagher 2000), and where you sit among US adults your sex and age on CDC DXA scans (NHANES 2011-2018, our verified percentiles).
- Equations verified: Army Table B-5 worked examples (exact 47.3% / 38.6%, which round to the Army's 47% / 39%); a published skinfold density (1.0597633) reproduced; Deurenberg formula and its 4.1-point standard error from the PubMed abstract.
- Formulas shown on the page with sources, FAQ (no FAQPage markup), WebApplication + BreadcrumbList schema, OG image.
- Links in: /body-fat-percentage-chart/ (related list + sentence; its generator updated to match), /lean-body-mass/, /blog/body-fat-vs-bmi/.
- sitemap.xml entry; research/: page-map (built), registry row body-fat-equations (verified), HANDOFF (also lists the follow-ups: calculators hub card and header nav entry).

## Rules
Do not edit any file by hand: only apply_build.py writes. No network. Do not push. Run from the repo root (/workspace).

## Steps
0. `git status --porcelain` — expected: only `?? research/body-fat-calculator-page/`. Anything else: STOP and report.
1. `python3 research/body-fat-calculator-page/apply_build.py --dry-run` — must print `DRY RUN — applied: 4 new files, 3 replaced files, 6 edits`. If it prints ABORT, STOP and report its full output.
2. `python3 research/body-fat-calculator-page/apply_build.py`
3. Gates — all must pass; on any FAIL, STOP before committing and report:
   3.1 `python3 scripts/check_structure.py` → `39/39 pages pass`
   3.2 `python3 research/f1/verify.py` → `VERIFY json/js failures: none | broken anchors: none | FAQ schema not shown: none | artifacts: none`
   3.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`
   3.4 `grep -c "/body-fat-calculator/" sitemap.xml body-fat-percentage-chart/index.html lean-body-mass/index.html blog/body-fat-vs-bmi/index.html` → `1`, `2`, `1`, `1`
4. Commit: `git add body-fat-calculator/ research/ sitemap.xml body-fat-percentage-chart/index.html lean-body-mass/index.html blog/body-fat-vs-bmi/index.html`; `git status --porcelain` must be empty; then
   `git commit -m "feat: /body-fat-calculator/ — Navy tape, Jackson-Pollock skinfold and Deurenberg BMI methods (verified), results on NHANES DXA percentiles; inbound links"`
5. REPORT — print exactly this, nothing after it:
```
REPORT body-fat-calculator
0 status: <lines>
1 dry-run: <line>
3 gates: 3.1 <line> | 3.2 <line> | 3.3 <line> | 3.4 <lines>
4 commit: <git log --oneline -2>
stat: <git show --stat HEAD | tail -20>
final status: <git status --porcelain, or "clean">
```
