# BUILD — /us-obesity-statistics/ · calculatemybmi.net
Prepared in chat, 30 Sep 2026. Every number, sentence, chart and citation in `page/` was verified against NCHS/CDC primary sources in chat (the box has no network, so nothing here can be re-verified locally). Your job is assembly, wiring and verification — not writing.

## Hard rules
1. Do not change any wording, number, link target, citation or chart in `page/content.html`, `page/head-extras.html` or `page/assets/*`. Permitted edits are only the ones named in Step 2 (placeholders, shell wiring, button class, optional colour mapping). If anything looks wrong, STOP and report it. Do not "fix" content.
2. Add no external links or citations anywhere. Never cite harvard.edu, mayoclinic.org, clevelandclinic.org, nhs.uk, heart.org, acefitness.org, acsm.org, nsca.com or wikipedia.org.
3. No FAQPage schema on this page. Do not push. Do not run network commands.
4. Files you may change: `us-obesity-statistics/*` (new), `sitemap.xml`, footer blocks of `*.html` pages (3.1), one appended sentence per page (3.2), the /bmi-chart/ related list (3.3), `research/keyword-ledger.csv`, `research/page-map.csv`, `research/data-sources.csv`, the HANDOFF file (append only, 4.4), and `research/us-obesity-build/`. Nothing else.

## Package (in research/us-obesity-build/)
- `page/content.html` — the whole page body: article, 4 inline SVG figures, "Where do you fit?" widget, embed box, one inline `<script>`.
- `page/head-extras.html` — page-specific head tags + JSON-LD (Article, Dataset, BreadcrumbList).
- `page/assets/` — `us-obesity-trend-1960-2023.svg` (embeddable chart), `og-us-obesity-statistics.png` (1200×630), `us-obesity-data-nhanes-1960-2023.csv` (585 rows, all NCHS; calculated rows labelled).
- `research/` — `kwp-intake-us-obesity.csv` (635 ledger rows), `pagemap-rows-us-obesity.csv`, `data-sources-rows-us-obesity.csv`, `build_dataset_us_obesity.py` (dataset provenance — do not run), `kwp-raw-2026-09-30/` (the 3 KWP exports).
- `tools/` — `merge_research.py`, `check_ledger.py`, `check_sources.py`, `number_audit.py` + `allowed_numbers.txt`, `widget_test.js`.

Run every command from the repo root (/workspace).

## Step 0 — Preflight (read-only, print everything)
0.1 `git status --porcelain` — if anything is listed other than `research/us-obesity-build/` (and the zip), STOP and report the list.
0.2 Baseline gate: `python3 scripts/check_structure.py | tail -5`
0.3 Ledger guard:
```
python3 - <<'EOF'
import csv
G=["us obesity rate","obesity rate in america","united states obesity rate","what percentage of americans are obese","obesity in america","how many people are obese in america","us obesity statistics","percentage of overweight americans"]
A=G+["percentage of obese americans","how many americans are obese","us obesity rate by year","america average bmi","average bmi","obesity statistics","childhood obesity rate","childhood obesity in america","states by obesity rate","obesity rate by state"]
rows=list(csv.DictReader(open("research/keyword-ledger.csv",encoding="utf-8-sig")))
n=lambda k:" ".join(k.lower().split()); idx={n(r["keyword"]):r for r in rows}; stop=[]
for k in A:
    r=idx.get(k); print(f"{k!r}: "+(f"{r.get('page_slug') or '-'} / {r.get('role')}" if r else "not in ledger"))
    if k in G and r and r.get("page_slug","").strip() not in ("","us-obesity-statistics"): stop.append(k)
mine=[r for r in rows if r.get("page_slug","").strip()=="us-obesity-statistics"]
print("rows already on us-obesity-statistics:",len(mine))
for r in mine:
    if r.get("role") in ("primary","secondary"): print("  existing",r["role"],r["keyword"],r.get("volume"))
print("GUARD:","STOP -> "+", ".join(stop) if stop else "OK")
EOF
```
If GUARD prints STOP, stop and report.
0.4 Print the page-map rows for `us-obesity-statistics`, `childhood-obesity-statistics`, `obesity-rate-by-state` (or "absent").
0.5 Resolve placeholders and print each value:
- `ORIGIN` = scheme + host of the canonical URL in `bmi-chart/index.html` (expected `https://calculatemybmi.net`).
- `ORG_ID`, `PERSON_ID` = the `"@id"` of the Organization node and of the Person node in the JSON-LD of `bmi-chart/index.html` (fallback: `about/index.html`). If either can't be found, STOP.
- `DATE` = today, `YYYY-MM-DD`.
- `BMICHART_URL` = `/bmi-chart/` (must exist). `BODYFAT_URL` = `/blog/body-fat-vs-bmi/` (must exist). If either is missing, STOP.
- `BMICATEGORIES_URL` = `/blog/bmi-categories/` if `blog/bmi-categories/index.html` exists. Otherwise delete exactly this text from the page: `; for what each category means, see <a href="{{BMICATEGORIES_URL}}">BMI categories explained</a>` and report it.
- `KIDS_CALC_URL` = the first existing of `/bmi-calculator-for-kids/`, `/child-bmi-calculator/`, `/kids-bmi-calculator/`, `/bmi-calculator-kids/`, `/children-bmi-calculator/`, `/bmi-calculator-for-children/`, `/teen-bmi-calculator/`. If none exists, list the top-level page directories whose `<h1>` contains "BMI" plus "Child", "Kid" or "Teen"; if there isn't exactly one, STOP.
0.6 Print how /bmi-chart/ colours the BMI categories (print only, used in 2.6):
`grep -n -iE 'underweight|overweight|obes|healthy|normal' bmi-chart/index.html | grep -iE '#[0-9a-f]{3,6}|--[a-z-]+' | head -25`

## Step 1 — Folder + assets
`mkdir -p us-obesity-statistics && cp research/us-obesity-build/page/assets/* us-obesity-statistics/`

## Step 2 — Assemble `us-obesity-statistics/index.html`
2.1 `cp bmi-chart/index.html us-obesity-statistics/index.html` — this is the shell (sitewide head, header, mobile nav + nav-toggle, footer, consent banner, bottom-of-body binder script). Every manually added page must carry the full shell.
2.2 `<head>`: delete `<title>`, `meta[name=description]`, `link[rel=canonical]`, every `meta[property^="og:"]`, `meta[name^="twitter:"]`, `meta[property^="article:"]`, and every `<script type="application/ld+json">`. Insert the full contents of `page/head-extras.html` where `<title>` was. If the shell had `article:published_time` / `article:modified_time`, add both with `content="{{DATE}}"`. Keep every other head tag byte-identical (charset, viewport, robots, icons, CSS, preconnects, GA4/consent, Raptive, fonts).
2.3 JSON-LD: append the Organization node and the Person node from the shell's JSON-LD (the objects whose `"@id"` equal `ORG_ID` and `PERSON_ID`) verbatim into our `"@graph"` array.
2.4 `<body>`: first copy the shell's visible breadcrumb markup and its byline block. Then, inside `<main>` (if there is no `<main>`, the wrapper that contains the shell's `<h1>`), delete everything and insert `page/content.html`. Replace its two comments:
- `<!-- BREADCRUMB ... -->` → the shell's breadcrumb markup with two items: Home (`/`) › US Obesity Statistics (last item rendered exactly as the shell renders its current page).
- `<!-- BYLINE ... -->` → the shell's byline block, verbatim.
If the shell has an author box after the article body, keep it after `</article>`. Remove `aria-current` from nav links (this page isn't in the nav). Delete the shell's page-specific scripts (inline scripts that reference element ids that no longer exist). If the shell's `<h1>` has a class, give our `<h1>` the same class. Keep header, nav, footer, consent banner and all sitewide scripts unchanged.
2.5 CSS: add this block in `<head>` after the last stylesheet/style element. Give `#cmb-fit-go` and `#cmb-embed-copy` the same class as the primary button of the homepage calculator (`index.html`), if it has one.
```
<style>
.cmb-stats .cmb-intro{font-size:1.08em}
.cmb-answer{border-left:4px solid #E0612D;background:#FFF7F2;border-radius:8px;padding:14px 16px;margin:18px 0}
.cmb-answer p{margin:0 0 6px}
.cmb-src{font-size:.85em;color:#6B7280;margin:6px 0 14px}
.cmb-note{font-size:.9em;color:#4B5563}
.cmb-callout{border:1px solid #F3D3AE;background:#FFFAF5;border-radius:10px;padding:14px 16px;margin:22px 0}
.cmb-callout-num{font-size:2rem;font-weight:800;line-height:1.1;margin:0 0 6px;color:#B3431A}
.cmb-toc{border:1px solid #E5E7EB;border-radius:10px;padding:12px 16px;margin:22px 0;background:#F9FAFB}
.cmb-toc-title{font-weight:700;margin:0 0 6px}
.cmb-toc ol{margin:0;padding-left:1.25em}
.cmb-toc li{margin:4px 0}
.cmb-fig{margin:22px auto;max-width:560px}
.cmb-fig-hero{max-width:420px}
.cmb-fig svg{display:block;width:100%;height:auto}
.cmb-fig figcaption{font-size:.85em;color:#4B5563;margin-top:8px}
.cmb-table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:16px 0}
.cmb-table-wrap table{border-collapse:collapse;width:100%;min-width:420px}
.cmb-table-wrap caption{text-align:left;font-weight:700;margin-bottom:6px}
.cmb-table-wrap th,.cmb-table-wrap td{padding:8px 10px;border-bottom:1px solid #E5E7EB;text-align:left;vertical-align:top}
.cmb-table-wrap td{font-variant-numeric:tabular-nums}
.cmb-fit{border:1px solid #E5E7EB;border-radius:12px;padding:16px;margin:24px 0;background:#F9FAFB}
.cmb-fit fieldset{border:0;padding:0;margin:0 0 10px;display:flex;gap:16px;flex-wrap:wrap}
.cmb-fit legend{font-weight:600;margin-bottom:6px}
.cmb-fit-row{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin-bottom:12px}
.cmb-fit input[type=number]{width:5.5em;min-height:44px;padding:8px;font-size:16px}
#cmb-fit-go,#cmb-embed-copy{min-height:44px;padding:10px 16px;font-weight:600;cursor:pointer}
.cmb-fit-out{font-weight:600;min-height:1.5em;margin:12px 0 6px}
.cmb-reuse{border-top:1px solid #E5E7EB;margin-top:22px;padding-top:6px}
.cmb-reuse textarea{width:100%;box-sizing:border-box;font:13px/1.4 ui-monospace,Menlo,Consolas,monospace;margin:6px 0 8px}
.cmb-faq{border-bottom:1px solid #E5E7EB;padding:6px 0}
.cmb-faq summary{cursor:pointer;min-height:44px;display:flex;align-items:center;gap:12px;list-style:none}
.cmb-faq summary::-webkit-details-marker{display:none}
.cmb-faq summary::after{content:"+";margin-left:auto;font-weight:700}
.cmb-faq[open] summary::after{content:"\2212"}
.cmb-faq summary h3{display:inline;font-size:1.05rem;margin:0}
.cmb-dl dt{font-weight:700;margin-top:10px}
.cmb-dl dd{margin:2px 0 0}
</style>
```
2.6 Colours (optional): only if 0.6 shows one explicit colour per category (underweight, healthy/normal, overweight, obese/obesity), replace in the new page's inline SVGs and in `us-obesity-statistics/us-obesity-trend-1960-2023.svg`: `#4F86C6`→underweight, `#3A9D5D`→healthy, `#E0A526`→overweight, `#E0612D`→obesity. Never touch `#9E1B1B`, `#8A5A00`, `#B3431A`, `#8E1B1B`, `#2E7D4F`, `#B45309` or the PNG (text tones are contrast-checked). Report the mapping or "kept".
2.7 Replace every `{{PLACEHOLDER}}` with the 0.5 values. `grep -c "{{" us-obesity-statistics/index.html` must print 0.

## Step 3 — Links into the page
3.1 Footer: in every `*.html` outside `research/` (including the new page and 404.html) whose footer links to `/bmi-chart/`, insert `<li><a href="/us-obesity-statistics/">US Obesity Statistics</a></li>` directly after the item containing that link (mirror the sibling markup if items aren't `<li>`). Pages without a footer /bmi-chart/ link: don't edit, report.
3.2 Contextual: in every `*.html` except `us-obesity-statistics/`, `404.html`, `privacy/`, `terms/`, `contact/`: find the first "40.3%" in visible body text. If it sits inside a `<p>` or `<li>`, append ` See the full <a href="/us-obesity-statistics/">US obesity statistics</a>.` immediately before that element's closing tag. SKIP (and report why) when: it's inside a table, figcaption, SVG, script, meta or an existing `<a>`; the page already links to /us-obesity-statistics/; or the first 60 characters of that element's text appear inside any `application/ld+json` block on the page (FAQ answers mirrored in FAQPage schema must stay identical to the schema).
3.3 /bmi-chart/: if 3.2 didn't already add a link there and the page has a related-links list (a `<ul>`/`<ol>` right after a heading containing "Related"), append `<li><a href="/us-obesity-statistics/">US obesity statistics</a></li>`. Otherwise skip and report.
3.4 `sitemap.xml`: add a `<url>` for `ORIGIN/us-obesity-statistics/` directly after the /bmi-chart/ entry, with exactly the same child tags as that entry and `lastmod` = DATE.

## Step 4 — Research files
4.1 `python3 research/us-obesity-build/tools/merge_research.py` — append-only merge (rules in its docstring: never re-assigns an owned keyword, never creates a 2nd primary, preserves line endings). Print its output.
4.2 `python3 research/us-obesity-build/tools/check_ledger.py research/keyword-ledger.csv research/page-map.csv | tail -15` — must end `RESULT: OK`.
4.3 `python3 research/us-obesity-build/tools/check_sources.py research/data-sources.csv research/page-map.csv | tail -30`. Expected, do not fix: (a) `obesity-rate-by-state` rides the candidate `cdc-brfss-state-obesity` source — intended gate until the state build verifies BRFSS; (b) if the registry was just created, other pages' data_source values are unregistered — pre-existing debt, report the count. Any FAIL naming `us-obesity-statistics` or `childhood-obesity-statistics` is real: STOP and report.
4.4 HANDOFF: find it with `git ls-files | grep -i handoff`. Append the "HANDOFF append" block at the end of this file verbatim. Do not edit existing text.

## Step 5 — Verification gate (all must pass)
5.1 `python3 scripts/check_structure.py` → all pass (expected 34/34). If the new page fails a check, fix it only by copying the missing structural element from `bmi-chart/index.html`. If a fix would need a copy, number or link change, STOP and report.
5.2 `grep -c "{{" us-obesity-statistics/index.html` → 0
5.3 `python3 research/us-obesity-build/tools/number_audit.py us-obesity-statistics/index.html` → `not allowed: none`. (If the only flagged numbers come from the cloned breadcrumb/byline markup, that's fine — report them. Any other flagged number means page copy changed: STOP.)
5.4 `node research/us-obesity-build/tools/widget_test.js us-obesity-statistics/index.html` → `WIDGET: ALL PASS`
5.5 JSON-LD:
```
python3 - <<'EOF'
import re,json
s=open("us-obesity-statistics/index.html",encoding="utf-8").read()
bl=re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S); print("ld+json blocks:",len(bl))
for b in bl:
    d=json.loads(b); g=d.get("@graph",[d]); print(sorted(str(x.get("@type")) for x in g))
print("FAQPage present:", "FAQPage" in s)
EOF
```
→ exactly one block containing Article, Dataset, BreadcrumbList, Organization, Person; `FAQPage present: False`.
5.6 Internal links and assets resolve:
```
python3 - <<'EOF'
import re,os
s=open("us-obesity-statistics/index.html",encoding="utf-8").read(); bad=[]
for h in sorted(set(re.findall(r'href="(/[^"#?]*)',s))):
    p=h.strip("/"); ok=os.path.exists("index.html") if h=="/" else (os.path.exists(os.path.join(p,"index.html")) if h.endswith("/") else os.path.exists(p))
    if not ok: bad.append(h)
for f in ("us-obesity-data-nhanes-1960-2023.csv","us-obesity-trend-1960-2023.svg","og-us-obesity-statistics.png"):
    if not os.path.exists("us-obesity-statistics/"+f): bad.append(f)
print("broken:",bad or "none")
EOF
```
5.7 `grep -ciE "harvard|mayoclinic|clevelandclinic|nhs\.uk|heart\.org|acefitness|acsm\.org|nsca|wikipedia" us-obesity-statistics/index.html` → 0 (if non-zero, report where; if it comes from the shared shell, report, don't fix).
5.8 Inline scripts: write every inline `<script>` of the new page that has no `src` and isn't `application/ld+json` to `/tmp/cmb_N.js` and run `node --check` on each → all OK.
5.9 Print `.vercelignore` and confirm no pattern excludes `us-obesity-statistics/` or its .csv/.svg/.png files.
5.10 Audits — report only, do not fix:
- A: `grep -rn --include=*.html "31\.7%" . | grep -v -e "^./research/" -e "^./us-obesity-statistics/"`
- B: `grep -rn --include=*.html -E "(^|[^0-9.])9\.7%" . | grep -v -e "^./research/" -e "^./us-obesity-statistics/"`
For each hit print `file:line` and whether that line contains `db508` or `Data Brief 508`.

## Step 6 — Commit (do not push)
Delete `research/us-obesity-build.zip` if it still exists. Stage `us-obesity-statistics/`, `sitemap.xml`, `research/` and every modified tracked page (`git add -u`). Commit:
`feat: /us-obesity-statistics/ — NHANES 1960–2023 stats page, CSV dataset, embeddable chart; Tier-2 ledger merge`

## Step 7 — REPORT (print exactly this structure and nothing after it)
```
REPORT us-obesity-statistics
0 preflight: git clean Y/N | baseline check_structure | GUARD + existing rows for the page | page-map rows found
0.5 placeholders: ORIGIN= | ORG_ID= | PERSON_ID= | DATE= | KIDS_CALC_URL= | BMICATEGORIES_URL= (or "clause removed")
2 assembly: shell parts kept | shell scripts removed | button class used | colour mapping or "kept"
3 links in: footer edited N/total (+ skipped) | 40.3% sentence added on (list) | skipped (list + reason) | bmi-chart related Y/N | sitemap Y/N
4 research: merge_research output | check_ledger tail | check_sources tail + classification of every FAIL | HANDOFF path
5 gate: 5.1–5.9 PASS/FAIL each with its one-line output
5.10 audits: A hits | B hits (file:line, db508 on line Y/N)
6 commit: hash + `git show --stat HEAD | tail -25`
7 indexnow: the exact command to submit the new URL (and sitemap, if the script supports it) with scripts/indexnow.sh — read its usage, do NOT run it
```

## HANDOFF append
```
## 2026-09-30 · /us-obesity-statistics/ built (see git log)
- Page: US obesity rate and statistics — NHANES Aug 2021–Aug 2023 snapshot + 1960–2023 trend (ages 20–74, age-adjusted), age/sex/education/race, children summary, measured-vs-self-reported section (Gallup), "Where do you fit?" widget, embeddable chart (CC BY 4.0; brand-anchor link only; nofollow allowed) and CSV (585 rows) served from /us-obesity-statistics/.
- Sources verified 30 Sep 2026 (research/data-sources.csv): NCHS Health E-Stats 111, 112, 119; NCHS Data Brief 508; NCHS Series 3 No. 50 (mean/median BMI and weight percentiles — ready for /average-weight/); NHANES population totals; Gallup 28 Oct 2025. Gallup's 2026 update is excluded (text and table disagree).
- Tier-2 KWP (3 batches, 789 keywords → 635 ledger rows): primary "us obesity rate" (14,800/mo). Childhood cluster (~4.8k/mo) → proposed /childhood-obesity-statistics/. State cluster (~13k/mo) → /obesity-rate-by-state/ — its BRFSS source is still a candidate; CDC's adult obesity maps page was updated ~24 Sep 2026, verify before building. Global (~10k/mo) parked; WHO GHO is the candidate source for a possible /obesity-rate-by-country/.
- Open: sitewide "31.7% overweight … Data Brief 508" citations are misattributed (31.7% is age-adjusted, from Health E-Stat 111; Data Brief 508 has no overweight figure), and pages mix crude and age-adjusted figures — see the audit list in the build report; fix pending.
- Portfolio rules: never republish this page, the dataset or shared prose on other health sites (Google scaled-content policy names multiple sites hiding scaled content). Embed/licence links: brand anchor only, never keyword anchors, nofollow always allowed (Google link-spam policy, widget clause).
- Next builds: /obesity-rate-by-state/ → /childhood-obesity-statistics/ → /average-weight/.
```
