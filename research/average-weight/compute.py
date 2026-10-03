import pandas as pd, numpy as np, json, math
demo=pd.read_sas("/mnt/user-data/uploads/DEMO_L.xpt",format="xport"); bmx=pd.read_sas("/mnt/user-data/uploads/BMX_L.xpt",format="xport")
D=demo.merge(bmx,on="SEQN",how="left")
LB=2.2046226218
D["wt_lb"]=D.BMXWT*LB; D["ht_in"]=D.BMXHT/2.54; D["waist_in"]=D.BMXWAIST/2.54
D["hin"]=np.floor(D.ht_in+0.5)                      # nearest whole inch
ad=(D.RIDAGEYR>=20)&(D.WTMEC2YR>0)&(D.RIDEXPRG!=1)
W=D.WTMEC2YR.fillna(0); STR=D.SDMVSTRA; PSU=D.SDMVPSU
def est(var, dom):
    """Weighted domain mean with Taylor-linearised SE (strata x PSU), NHANES design."""
    m=dom & D[var].notna() & (W>0)
    w=W.where(m,0.0); y=D[var].where(m,0.0); Wt=w.sum()
    if Wt==0: return None
    mean=(w*y).sum()/Wt; z=(w*(y-mean)/Wt).where(m,0.0)
    v=0.0
    for h,g in pd.DataFrame({"z":z,"s":STR,"p":PSU}).groupby("s"):
        zj=g.groupby("p").z.sum(); nh=len(zj)
        if nh>1: v+=nh/(nh-1)*((zj-zj.mean())**2).sum()
    return dict(mean=float(mean),se=float(math.sqrt(v)),n=int(m.sum()))
def wq(var,dom,qs):
    m=dom&D[var].notna()&(W>0); x=D.loc[m,var].values; w=W[m].values; o=np.argsort(x); x=x[o]; w=w[o]; c=(np.cumsum(w)-w/2)/w.sum()
    return [float(np.interp(q,c,x)) for q in qs]
R=dict()
for sx,lab in ((1,"men"),(2,"women")):
    dom=ad&(D.RIAGENDR==sx); r={}
    for var in ("wt_lb","ht_in","BMXBMI","waist_in"): r[var]=est(var,dom)
    r["wt_pct"]=dict(zip(["p5","p10","p25","p50","p75","p90","p95"],wq("wt_lb",dom,[.05,.10,.25,.50,.75,.90,.95])))
    r["waist_pct"]=dict(zip(["p25","p50","p75"],wq("waist_in",dom,[.25,.5,.75])))
    ages={}
    for a0,a1,al in ((20,29,"20–29"),(30,39,"30–39"),(40,49,"40–49"),(50,59,"50–59"),(60,69,"60–69"),(70,79,"70–79"),(80,200,"80+")):
        dd=dom&(D.RIDAGEYR>=a0)&(D.RIDAGEYR<=a1); ages[al]={"wt":est("wt_lb",dd),"waist":est("waist_in",dd),"bmi":est("BMXBMI",dd),"ht":est("ht_in",dd)}
    r["age"]=ages
    hts={}
    for h in range(55,80):
        dd=dom&(D.hin==h); e=est("wt_lb",dd)
        if e is None or e["n"]<30: continue
        win=dom&(D.hin>=h-1)&(D.hin<=h+1)              # +-1 inch window for the percentile curve used by the tool
        hts[h]={"wt":e,"q":wq("wt_lb",dd,[.25,.5,.75]),"cdf":wq("wt_lb",win,[i/20 for i in range(1,20)]),"nwin":int((win&D.wt_lb.notna()).sum()),
                "bmi":est("BMXBMI",dd)}
    r["height"]=hts
    R[lab]=r
json.dump(R,open("avgw_results.json","w"),indent=0)
for lab in ("men","women"):
    r=R[lab]; print(f'{lab}: wt {r["wt_lb"]["mean"]:.1f}±{1.96*r["wt_lb"]["se"]:.1f} (n {r["wt_lb"]["n"]}) | ht {r["ht_in"]["mean"]:.1f} | BMI {r["BMXBMI"]["mean"]:.1f} | waist {r["waist_in"]["mean"]:.1f} in | median wt {r["wt_pct"]["p50"]:.1f}')
    print("   ages:",{k:round(v["wt"]["mean"],1) for k,v in r["age"].items()})
    print("   heights (n>=30):",{f'{h//12}\'{h%12}"':(round(v["wt"]["mean"],1),v["wt"]["n"]) for h,v in r["height"].items()})
