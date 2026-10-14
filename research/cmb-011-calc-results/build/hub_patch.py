# ---------------------------------------------------------------- /blog/ hub: styled link lists, every guide listed once, reader-facing blurbs
BI = 'blog/index.html'
def card(href, title, desc):
    return f'<a href="{href}" class="related-card"><div class="related-card-title">{title}</div><p class="related-card-desc">{desc}</p></a>'
HUB = [
  ('Start here', None, True, [
    ('/blog/what-is-bmi/', 'What is BMI?', 'What BMI is, how it&rsquo;s calculated and where it came from.'),
    ('/blog/healthy-bmi-range/', 'Healthy BMI range', 'Where the 18.5&ndash;24.9 range comes from and what it means at your height.'),
    ('/blog/bmi-by-age/', 'BMI by age', 'Why the adult cut-offs stay the same at every age, and what research found for adults over 65.')]),
  ('Foundations', None, False, [
    ('/blog/bmi-formula/', 'BMI formula', 'The metric and US formulas, where the 703 comes from, and the common mistakes.'),
    ('/blog/bmi-categories/', 'BMI categories', 'The WHO adult categories, from severe thinness below 16 to class III obesity at 40 and above.'),
    ('/blog/bmi-chart-explained/', 'BMI chart explained', 'How to read a BMI chart, with full charts in pounds and kilograms.'),
    ('/blog/bmi-chart-women/', 'BMI chart for women', 'Healthy and category weights for women from 4&prime;10&Prime; to 6&prime;0&Prime;.'),
    ('/blog/bmi-chart-men/', 'BMI chart for men', 'Healthy and category weights for men from 5&prime;2&Prime; to 6&prime;6&Prime;.'),
    ('/blog/bmi-history/', 'BMI history', 'From Quetelet&rsquo;s 1830s index to Ancel Keys naming it BMI in 1972 and the WHO categories.')]),
  ('Health associations (informational)', None, False, [
    ('/blog/bmi-and-health-risks/', 'BMI and health risks', 'What large studies link to higher and lower BMI, condition by condition, with sources.'),
    ('/blog/underweight-bmi-risks/', 'Underweight BMI risks', 'Health risks below BMI 18.5, and where to find eating-disorder support.')]),
  ('Beyond BMI', None, False, [
    ('/blog/bmi-limitations/', 'BMI limitations', 'Ten ways BMI can mislead, from muscle and fat distribution to age.'),
    ('/blog/body-fat-vs-bmi/', 'Body fat vs BMI', 'What each measure captures, and why two people with the same BMI can differ in body fat.'),
    ('/blog/how-to-measure-body-fat/', 'How to calculate body fat percentage', 'Every method, from calipers and smart scales to the Bod Pod and DXA, scored against DXA scans in one 437-person study.'),
    ('/blog/waist-to-height-ratio/', 'Waist-to-height ratio', 'Your waist divided by your height: the 0.5 boundary and how it compares with BMI.'),
    ('/blog/bmi-for-athletes/', 'BMI for athletes', 'NFL Combine and college-football scan data showing how BMI misclassifies muscular athletes, plus the measures that work better.'),
    ('/blog/bmi-and-metabolism/', 'BMI and metabolism', 'Metabolic rate, metabolic syndrome, muscle, age and thyroid, and how each relates to BMI.')]),
  ('Lifestyle (non-prescriptive)', None, False, [
    ('/blog/how-to-lower-bmi/', 'How to lower BMI', 'Calorie deficit, diet, activity, sleep, plateaus and when to see a doctor.'),
    ('/blog/bmi-tracking-guide/', 'BMI tracking guide', 'When to weigh yourself, normal day-to-day swings, and other measures worth tracking.')]),
  ('Related calculators', 'Each calculator page carries its own guide.', False, [
    ('/women-bmi-calculator/', 'BMI for women', 'Life stages from puberty to menopause, ACOG pregnancy weight-gain ranges and the NIH waist cut-off.'),
    ('/men-bmi-calculator/', 'BMI for men', 'The NIH 40-inch (102 cm) waist cut-off, muscle and BMI, and how US men compare.'),
    ('/age-bmi-calculator/', 'BMI by age', 'The adult range at every age, with US averages by age group.'),
    ('/kids-bmi-calculator/', 'Pediatric BMI', 'CDC BMI-for-age percentiles for ages 2 to 19.'),
    ('/ideal-weight/', 'Ideal weight', 'Four ideal-weight formulas (Devine, Robinson, Miller, Hamwi) beside the BMI range.'),
    ('/lean-body-mass/', 'Lean body mass', 'Lean mass and body fat from the Boer, James and Hume equations.'),
    ('/new-bmi-calculator/', 'New BMI (Trefethen)', 'Trefethen&rsquo;s 2013 formula next to the standard one, at your height.')]),
]
guides = [c for sec in HUB[:-1] for c in sec[3]]
assert len(guides) == len({c[0] for c in guides}) == 19, len(guides)
parts = []
for title, note, featured, cards in HUB:
    style = 'margin: 2.5rem 0; padding: 1.5rem; background: var(--primary-bg); border-radius: var(--radius-lg); border: 1px solid var(--primary-light);' if featured else 'margin: 2.5rem 0;'
    h2 = f'<h2 style="margin-top: 0;">{title}</h2>' if featured else f'<h2>{title}</h2>'
    p = f' <p style="color: var(--gray-600); font-size: 0.9375rem;">{note}</p>' if note else ''
    parts.append(f'<section style="{style}"> {h2}{p} <div class="related-grid">' + ''.join(card(*c) for c in cards) + '</div> </section>')
s = load(BI)
a = s.index('<!-- Featured -->')
b = s.index('<section style="margin: 2.5rem 0; text-align: center; padding: 2rem; background: var(--primary-bg); border-radius: var(--radius-lg);">')
buf[BI] = s[:a] + '<!-- Guides by topic; every /blog/ page in the sitemap is listed once (check_structure enforces it, CMB-011) --> ' + ' '.join(parts) + ' ' + s[b:]
rep(BI, '<a href="/" class="cta-button">Calculate now &rarr;</a>', '<a href="/" class="cta-button">Open the BMI calculator</a>')
rep(BI, '<p class="intro-text">15 evidence-based guides on BMI, healthy weight, body composition, and alternative metrics. Start with our <a href="/" style="color:var(--link); font-weight: 500;">BMI calculator</a> or browse below. See also our <a href="/calculators/" style="color:var(--link); font-weight: 500;">specialised calculators</a> for women, men, children, older adults, and athletes &mdash; each tool page carries its own on-page guidance.</p>',
        '<p class="intro-text">19 guides on BMI, healthy weight, body composition and the measures that go beyond BMI. Start with the <a href="/" style="color:var(--link); font-weight: 500;">BMI calculator</a> or browse below; the <a href="/calculators/" style="color:var(--link); font-weight: 500;">specialised calculators</a> for women, men, children and older adults each carry their own guide.</p>')
rep(BI, '<title>BMI Calculator Guides &mdash; 15 evidence-based articles</title>', '<title>BMI Calculator Guides &mdash; 19 articles on BMI and healthy weight</title>')
rep(BI, '<meta property="og:title" content="BMI Calculator Guides &mdash; 15 evidence-based articles">', '<meta property="og:title" content="BMI Calculator Guides &mdash; 19 articles on BMI and healthy weight">')
rep(BI, '<meta name="twitter:title" content="BMI Calculator Guides &mdash; 15 evidence-based articles">', '<meta name="twitter:title" content="BMI Calculator Guides &mdash; 19 articles on BMI and healthy weight">')
DESC = 'Every BMI guide on CalculateMyBMI.net: 19 articles on healthy ranges, categories, BMI charts, health associations, formulas, limitations and body composition.'
rep(BI, '<meta name="description" content="Every BMI guide on CalculateMyBMI.net: 15 evidence-based articles covering healthy ranges, categories, associations with health, formulas, limitations, and body composition.">', f'<meta name="description" content="{DESC}">')
rep(BI, '<meta property="og:description" content="Every BMI guide on CalculateMyBMI.net: 15 evidence-based articles covering healthy ranges, categories, associations with health, formulas, limitations, and body composition.">', f'<meta property="og:description" content="{DESC}">')
rep(BI, '<meta name="twitter:description" content="Every BMI guide on CalculateMyBMI.net: 15 evidence-based articles.">', '<meta name="twitter:description" content="Every BMI guide on CalculateMyBMI.net: 19 articles.">')
# ItemList: the same 19 guides, in page order
s = buf[BI]
m = re.search(r'(?s)(<script type="application/ld\+json">)(\s*\{\s*"@context": "https://schema.org",\s*"@type": "CollectionPage".*?)(</script>)', s)
assert m, 'CollectionPage JSON-LD'
ld = json.loads(m.group(2))
old_names = {it['url']: it['name'] for it in ld['mainEntity']['itemListElement']}
NAMES = {'/blog/bmi-chart-women/': 'BMI Chart for Women', '/blog/bmi-chart-men/': 'BMI Chart for Men', '/blog/bmi-by-age/': 'BMI by Age', '/blog/how-to-measure-body-fat/': 'How to Calculate Body Fat Percentage'}
items = []
for i, c in enumerate(guides, 1):
    url = 'https://calculatemybmi.net' + c[0]
    items.append({'@type': 'ListItem', 'position': i, 'name': old_names.get(url) or NAMES[c[0]], 'url': url})
ld['mainEntity']['numberOfItems'] = len(items); ld['mainEntity']['itemListElement'] = items
indent = 2 if '\n  "' in m.group(2) else None
new_ld = json.dumps(ld, indent=indent, ensure_ascii=False)
buf[BI] = s[:m.start(2)] + new_ld + s[m.end(2):]

# health risks: the extra link list repeats three links the page already has (CMB-011)
s = load(HR)
a = s.index('<div class="related-grid" style="margin-top: 2rem;">')
b = span_div(s, a)
buf[HR] = s[:a].rstrip(' ') + ' ' + s[b:].lstrip(' ')
# ideal-weight FAQ: no double-hyphen dash in an answer (visible and JSON-LD)
rep(IW, '<strong>skeletal structure</strong> -- primarily the width', '<strong>skeletal structure</strong>, primarily the width')
rep(IW, 'skeletal structure -- primarily the width', 'skeletal structure, primarily the width')
# shared link-list component (used on /blog/, 404): it had no CSS at all
buf[CSS] = buf[CSS].rstrip('\n') + '\n' + open(os.path.join(BUILD, 'css_related.css'), encoding='utf-8').read()
