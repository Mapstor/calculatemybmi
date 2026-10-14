"""Save each calculator page AFTER Calculate as a static snapshot inside the served tree (_snap/, git-ignored), so the
impeccable detector can see the results panel it cannot click open. usage: snap_results.py PORT REPO_ROOT
then: .claude/skills/impeccable/scripts/impeccable detect --viewport 390x844 http://localhost:PORT/_snap/men-bmi-calculator.html
Delete _snap/ afterwards."""
import sys, re, os
from playwright.sync_api import sync_playwright
port, root = sys.argv[1], sys.argv[2]
pages = ['/', '/women-bmi-calculator/', '/men-bmi-calculator/', '/age-bmi-calculator/', '/kids-bmi-calculator/', '/new-bmi-calculator/', '/ideal-weight/', '/lean-body-mass/']
os.makedirs(os.path.join(root, '_snap'), exist_ok=True)
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--no-sandbox'])
    page = br.new_page(viewport={'width': 390, 'height': 844})
    page.route(re.compile(r'^(?!http://localhost).*'), lambda r: r.abort())
    for p in pages:
        page.goto(f'http://localhost:{port}{p}', wait_until='load'); page.wait_for_timeout(200)
        page.query_selector('.calculate-btn').click(); page.wait_for_timeout(500)
        html = page.evaluate("() => '<!DOCTYPE html>' + document.documentElement.outerHTML")
        html = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', html)   # freeze the rendered state
        name = (p.strip('/') or 'home').replace('/', '_')
        open(os.path.join(root, '_snap', name + '.html'), 'w', encoding='utf-8').write(html)
        print(name)
    br.close()
