#!/usr/bin/env python3
"""CMB-015 registry, page map, DESIGN.md and the structure gate: /bmi-chart/ sources (verified in chat 2026-10-14..16),
the images-in-search rule, and check_images.py wired into check_structure.py.
usage: patch_cmb015.py REPO_ROOT"""
import sys, os, csv, io, json

ROOT = sys.argv[1]
SLUG = 'bmi-chart'
S = json.load(open(os.path.join(ROOT, 'research/bmi-chart-build/bc_stats.json')))

def rw_csv(path, fn):
    p = os.path.join(ROOT, path); raw = open(p, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(raw))); rows = fn(rows)
    out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
    new = out.getvalue()
    assert new.startswith(raw.split('\r\n')[0]), path
    open(p, 'w', encoding='utf-8', newline='').write(new)

USED = ('nhanes-2021-2023-exam-files', 'nhanes-adult-obesity-2021-2023', 'nhanes-adult-weight-trends', 'cdc-adult-bmi-categories', 'cdc-child-bmi-categories',
        'cdc-about-bmi', 'cdc-calculating-bmi', 'nhanes-2011-2018-dxa', 'lancet-clinical-obesity-2025',
        'ada-2026-obesity-standards', 'nih-bmi-table-2022', 'cdc-pregnancy-weight-gain')
C, A = S['categories'], S['ada2026']
def cats(g): return ' / '.join(f'{C[g][k]["pct"]}' for k in ('underweight', 'healthy', 'overweight', 'class_1', 'class_2', 'class_3'))

def registry(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    linked = set()
    for r in rows[1:]:
        d = r[ix['domain']]
        if d in USED:
            ps = [x for x in r[ix['pages_served']].split(';') if x]
            if SLUG not in ps: ps.append(SLUG)
            r[ix['pages_served']] = ';'.join(ps); linked.add(d)
        if d == 'nhanes-2021-2023-exam-files':
            r[ix['sample_note']] += (
                f'. CMB-015 (2026-10-16): adults 20+ (excl. pregnant; n {C["all"]["n"]:,} / men {C["men"]["n"]:,} / women '
                f'{C["women"]["n"]:,}) by CDC category, underweight / healthy / overweight / class 1 / class 2 / class 3: all '
                f'{cats("all")}; men {cats("men")}; women {cats("women")} (obesity 40.3 / 39.2 / 41.3 and class 3 = NCHS DB508); '
                f'BMI under 20: {S["bmi_under_20"]["all"]["pct"]}%; heights 4\'10"-6\'6" cover {S["height_on_chart"]["all"]["pct"]}%; '
                f'ADA 2026 thresholds {A["all"]["obesity_ada"]["pct"]} vs BMI-only {A["all"]["obesity_bmi_only"]["pct"]} in the same '
                f'{A["all"]["n"]:,} adults (men {A["men"]["obesity_ada"]["pct"]} vs {A["men"]["obesity_bmi_only"]["pct"]}, women '
                f'{A["women"]["obesity_ada"]["pct"]} vs {A["women"]["obesity_bmi_only"]["pct"]}); BMI 25-29.9 with waist-to-height '
                f'>= 0.5: {A["all"]["bmi25_30_whtr_05"]["pct"]}%; 600-adult sample for the scatter figure; '
                'research/bmi-chart-build/bc_stats.py')
        if d == 'ada-2026-obesity-standards':
            r[ix['notes']] += (f' CMB-015: /bmi-chart/ applies 3.3a/3.3b to all US adults 20+ (NHANES 2021-2023): '
                               f'{A["all"]["obesity_ada"]["pct"]}% vs {A["all"]["obesity_bmi_only"]["pct"]}% by BMI alone (our calculation).')
        if d == 'nih-bmi-table-2022':
            r[ix['notes']] += (' CMB-015 (PDF read 2026-10-16): the 69-inch row reads 128 lb under BMI 19, 162 under 24, 169 under '
                               '25 and 203 under 30.')
    assert linked == set(USED), set(USED) - linked
    return rows

def pagemap(rows):
    head = rows[0]; ix = {k: i for i, k in enumerate(head)}
    hit = 0
    for r in rows[1:]:
        if r[ix['slug']] == SLUG:
            hit += 1
            r[ix['wedge']] = ('Adult chart 4\'10"-6\'6" in lb and kg + printable BMI table image + heights for each weight + '
                              'where US adults fall on the chart (NHANES 2021-2023, = NCHS DB508) + the June 2026 ADA waist '
                              'rule applied to US adults (built CMB-015)')
            r[ix['data_source']] = 'nhanes-2021-2023-exam-files'
            r[ix['status']] = 'built'
            r[ix['notes']] = ('Owns the 201k "bmi chart" group ("bmi index chart" and 470 more keywords, 305k/mo). D-14 rebuild '
                              'CMB-015 (research/bmi-chart-build/); also cites ada-2026-obesity-standards, nih-bmi-table-2022, '
                              'nhanes-adult-obesity-2021-2023 and the other rows listing this page. Merge blog/bmi-chart-explained '
                              'into it (308) only after Domain-property data confirms it has no Google traffic')
    assert hit == 1
    return rows

rw_csv('research/data-sources.csv', registry)
rw_csv('research/page-map.csv', pagemap)

# DESIGN.md: images in search results.
dp = os.path.join(ROOT, 'DESIGN.md'); d = open(dp, encoding='utf-8', newline='').read()
anchor = '### Category badges\n'
assert d.count(anchor) == 1 and 'Images in search results' not in d
d = d.replace(anchor, (
    '### Images in search results (CMB-015)\n'
    '- Every page carries `<meta name="robots" content="max-image-preview:large">`, which lets Google show a large image '
    'preview (and is required for large images in Discover).\n'
    '- Each D-14 page names a **preferred image**: its own figure redrawn with no words, numbers or logo (Google: avoid a '
    'generic image such as a logo, and images with text), in 16:9 (1200 × 675), 4:3 (1200 × 900) and 1:1 (1200 × 1200), '
    'drawn by `research/preferred-images/pref_images.py` into `assets/images/preferred/<name>-<ratio>.png`. The 16:9 file '
    'is `og:image` and `twitter:image` (`og:image:width` 1200, `og:image:height` 675); the main entity\'s JSON-LD `image` '
    'lists the 1:1, 4:3 and 16:9 files; a `WebPage` `primaryImageOfPage` names the 16:9 file. Keep wide margins so any crop '
    'holds the whole picture.\n'
    '- A figure meant for image results goes in an `<img>` (inline SVG and CSS backgrounds are not indexed as images) with '
    'alt text, width and height, next to the text it illustrates, and is listed under its page in `sitemap.xml` '
    '(`<image:image>`).\n'
    '- `scripts/check_images.py`, run by `check_structure.py`, enforces all three. A rebuild adds its page to `PREFERRED` '
    'there.\n\n' + anchor), 1)
open(dp, 'w', encoding='utf-8', newline='').write(d)

# styles.css: the muted second line (.th-sub) also works in .data-table row headers (the US adults table).
sp = os.path.join(ROOT, 'assets/css/styles.css'); st = open(sp, encoding='utf-8', newline='').read()
o = '.weight-chart .th-sub, .weight-chart .cell-cm { display: block;'
assert st.count(o) == 1
st = st.replace(o, '.weight-chart .th-sub, .weight-chart .cell-cm, .data-table .th-sub { display: block;')
o = '.weight-chart th, .weight-chart td { padding: 0.45rem 0.45rem;'          # 8 px beside 13 px text (impeccable cramped-padding)
assert st.count(o) == 1
st = st.replace(o, '.weight-chart th, .weight-chart td { padding: 0.45rem 0.5rem;')
open(sp, 'w', encoding='utf-8', newline='').write(st)
d = open(dp, encoding='utf-8', newline='').read()
o2 = ('- A printable chart image goes in `figure.figure.figure--wide` (680 px) as an `<img>` with width and height, linked to '
      'the full-size file, so search engines can index it.\n')
assert d.count(o2) == 1
d = d.replace(o2, o2 + '- Cells keep 8 px (0.5rem) beside the text. `.th-sub`, the muted second line, also works in `.data-table` row headers (CMB-015, the US adults table on `/bmi-chart/`).\n')
open(dp, 'w', encoding='utf-8', newline='').write(d)

# scripts/check_structure.py: run the image checks on every page.
cp = os.path.join(ROOT, 'scripts/check_structure.py'); c = open(cp, encoding='utf-8', newline='').read()
old_doc = 'Runs before every commit. Requires all 33 sitemap pages to pass:\n'
new_doc = 'Runs before every commit. Requires every sitemap page to pass:\n'
old_doc2 = '  - the /blog/ hub links every guide in the sitemap; its ItemList and its guide counts match (CMB-011)\n'
new_doc2 = old_doc2 + ('  - images in search: max-image-preview:large on every page; the D-14 pages name a text-free preferred image\n'
                       '    (16:9, 4:3, 1:1) in og:image, the JSON-LD image and primaryImageOfPage; every <img> in <main> is in the\n'
                       '    image sitemap (scripts/check_images.py, CMB-015)\n')
old_call = ("        problems.append(f'check_content_integrity import failed: {exc}')\n    return problems\n")
new_call = ("        problems.append(f'check_content_integrity import failed: {exc}')\n"
            "    # Images in search: large previews allowed, preferred images named, image sitemap in step (CMB-015).\n"
            "    try:\n"
            "        from check_images import image_problems\n"
            "        problems.extend(f'images: {p}' for p in image_problems(page, src, path))\n"
            "    except Exception as exc:\n"
            "        problems.append(f'check_images failed: {exc}')\n"
            "    return problems\n")
for o, n in ((old_doc, new_doc), (old_doc2, new_doc2), (old_call, new_call)):
    assert c.count(o) == 1, o[:60]
    c = c.replace(o, n)
open(cp, 'w', encoding='utf-8', newline='').write(c)
print('registry:', len(USED), 'rows linked, 3 notes; page map row built; DESIGN.md images rule; check_structure runs check_images')
