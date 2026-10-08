import re,json,glob
pages=[p for p in sorted(glob.glob("**/index.html",recursive=True)) if not p.startswith("research/")]
nob=[];noauth=[]
for p in pages:
    s=open(p,encoding="utf-8").read(); types=[]
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
        d=json.loads(b); g=d.get("@graph",[d])
        for n in g:
            types.append(n.get("@type"))
            if n.get("@type")=="WebApplication" and "author" not in n: noauth.append(p)
    if "BreadcrumbList" not in types and p!="index.html": nob.append(p)
print("schema check: missing BreadcrumbList:",nob or "none","| WebApplication without author:",noauth or "none")
