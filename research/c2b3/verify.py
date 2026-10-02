import re,glob,json,subprocess,html
files=[p for p in glob.glob("**/*.html",recursive=True) if not p.startswith("research/") and "google" not in p]
bad=[];broken=set();parity=[];arts=[]
art=re.compile(r'Thenotes|Asexplains|Therecommends|thenotes|Asnotes|Asresearchers|The\(\)|The\(ACE\)|Source:\(ACE\)|Timothy Church|tier table removed|ACE Body Fat|\(\) --')
for p in files:
    s=open(p,encoding="utf-8").read()
    arts+=[(p,m.group(0)) for m in art.finditer(s)]
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
        try:
            d=json.loads(b)
            for n in d.get("@graph",[d]):
                if n.get("@type")=="FAQPage":
                    vis={html.unescape(re.sub(r'<[^>]+>','',q)).strip() for q in re.findall(r'class="faq-question"[^>]*>(.*?)</button>',s,re.S)}|{html.unescape(re.sub(r'<[^>]+>','',q)).strip() for q in re.findall(r'<summary[^>]*>(.*?)</summary>',s,re.S)}
                    miss=[q["name"] for q in n.get("mainEntity",[]) if q["name"].strip() not in vis]
                    if miss: parity.append((p,len(miss)))
        except Exception as e: bad.append((p,"json",str(e)[:60]))
    for m in re.finditer(r'<script(\s[^>]*)?>(.*?)</script>',s,re.S):
        a=m.group(1) or ""
        if "src=" in a or "ld+json" in a or not m.group(2).strip(): continue
        open("/tmp/j.js","w").write(m.group(2))
        if subprocess.run(["node","--check","/tmp/j.js"],capture_output=True).returncode: bad.append((p,"js"))
    for frag in set(re.findall(r'href="#([^"]+)"',s)):
        if 'id="'+frag+'"' not in s: broken.add((p,"#"+frag))
print(f"VERIFY json/js failures: {bad or 'none'} | broken anchors: {sorted(broken) or 'none'} | FAQ schema not shown: {parity or 'none'} | artifacts: {arts or 'none'}")
