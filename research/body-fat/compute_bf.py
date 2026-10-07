import pandas as pd, numpy as np, json, math
D=pd.read_pickle("/home/claude/bf/nhanes_2011_2018.pkl").reset_index(drop=True)
D["W"]=D.WTMEC2YR.fillna(0)/4.0                     # pooled 4 cycles (NHANES analytic guidelines)
D["pf"]=D.DXDTOPF
ok=(D.W>0)&(D.RIDEXPRG!=1)&D.pf.notna()
STR,PSU=D.SDMVSTRA,D.SDMVPSU
def est(var,dom):
    m=dom&ok&D[var].notna(); w=D.W.where(m,0.0); y=D[var].where(m,0.0); Wt=w.sum()
    mean=(w*y).sum()/Wt; z=(w*(y-mean)/Wt).where(m,0.0); v=0.0
    for h,g in pd.DataFrame({"z":z,"s":STR,"p":PSU}).groupby("s"):
        zj=g.groupby("p").z.sum(); nh=len(zj)
        if nh>1: v+=nh/(nh-1)*((zj-zj.mean())**2).sum()
    return dict(mean=round(float(mean),2),se=round(math.sqrt(v),3),n=int(m.sum()))
def wq(dom,qs,var="pf"):
    m=dom&ok&D[var].notna(); x=D.loc[m,var].values; w=D.W[m].values; o=np.argsort(x); x=x[o]; w=w[o]; c=(np.cumsum(w)-w/2)/w.sum()
    return [round(float(np.interp(q,c,x)),2) for q in qs]
def share(dom,cond):
    m=dom&ok; return round(float(D.W[m&cond].sum()/D.W[m].sum()*100),1)
GAL={"f":{"20-39":(21,33,39),"40-59":(23,34,40)},"m":{"20-39":(8,20,25),"40-59":(11,22,28)}}   # Gallagher-based bands (low<a, normal a-<b, high b-<c, very high >=c)
R={"meta":{"n_adults":int((ok&D.RIDAGEYR.between(20,59)).sum()),"cycles":"2011-2018"}}
AG=[("8-11",8,11),("12-15",12,15),("16-19",16,19),("20-29",20,29),("30-39",30,39),("40-49",40,49),("50-59",50,59),("20-39",20,39),("40-59",40,59),("20-59",20,59)]
for sx,key in ((1,"m"),(2,"f")):
    R[key]={}
    for lab,a0,a1 in AG:
        dom=(D.RIAGENDR==sx)&D.RIDAGEYR.between(a0,a1)
        e=est("pf",dom); e["p"]=wq(dom,[i/20 for i in range(1,20)]); e["cdf"]=wq(dom,[i/100 for i in range(1,100)])
        R[key][lab]=e
    # Gallagher band shares by age group
    for g,(a0,a1) in (("20-39",(20,39)),("40-59",(40,59))):
        a,b,c=GAL[key][g]; dom=(D.RIAGENDR==sx)&D.RIDAGEYR.between(a0,a1)
        R[key][g]["gal"]={"low":share(dom,D.pf<a),"normal":share(dom,(D.pf>=a)&(D.pf<b)),"high":share(dom,(D.pf>=b)&(D.pf<c)),"very_high":share(dom,D.pf>=c)}
    # BMI vs body fat (adults 20-59): within BMI 18.5-24.9, share in Gallagher high/very high (age-specific thresholds)
    hi_cut=np.where(D.RIDAGEYR<=39,[GAL[key]["20-39"][1]]*len(D),[GAL[key]["40-59"][1]]*len(D))
    vh_cut=np.where(D.RIDAGEYR<=39,[GAL[key]["20-39"][2]]*len(D),[GAL[key]["40-59"][2]]*len(D))
    ad=(D.RIAGENDR==sx)&D.RIDAGEYR.between(20,59)&D.BMXBMI.notna()
    nb=ad&D.BMXBMI.between(18.5,24.99); ob=ad&(D.BMXBMI>=30); ow=ad&D.BMXBMI.between(25,29.99)
    R[key]["bmi_x"]={"normal_bmi_high_bf":share(nb,D.pf>=hi_cut),"normal_bmi_veryhigh_bf":share(nb,D.pf>=vh_cut),
                     "ob_bmi_veryhigh_bf":share(ob,D.pf>=vh_cut),"ow_bmi_veryhigh_bf":share(ow,D.pf>=vh_cut),
                     "n_normal":int((nb&ok).sum()),"n_ob":int((ob&ok).sum()),"pf_normal_bmi":wq(nb,[.25,.5,.75]),"pf_ob_bmi":wq(ob,[.25,.5,.75])}
json.dump(R,open("bf_results.json","w"))
for key in ("m","f"):
    print(key,"20-59 mean %.1f (n %d) | median %.1f"%(R[key]["20-59"]["mean"],R[key]["20-59"]["n"],R[key]["20-59"]["p"][9]),
          "| by age:",{k:R[key][k]["mean"] for k in ("20-29","30-39","40-49","50-59")},"| teens:",{k:R[key][k]["mean"] for k in ("8-11","12-15","16-19")})
    print("   Gallagher bands 20-39:",R[key]["20-39"]["gal"],"| 40-59:",R[key]["40-59"]["gal"])
    print("   BMI x BF:",R[key]["bmi_x"])
# ---- body fat by BMI category (adults 20-59), threshold-free comparison ----
for sx,key in ((1,"m"),(2,"f")):
    ad=(D.RIAGENDR==sx)&D.RIDAGEYR.between(20,59)&D.BMXBMI.notna()
    R[key]["by_bmi"]={}
    for lab,lo,hi in (("18.5–24.9",18.5,24.99),("25–29.9",25,29.99),("30+",30,200)):
        dom=ad&D.BMXBMI.between(lo,hi)
        R[key]["by_bmi"][lab]={"q":wq(dom,[.10,.25,.5,.75,.90]),"n":int((dom&ok).sum())}
json.dump(R,open("bf_results.json","w"))
print({k:{b:(v["q"][2],v["n"]) for b,v in R[k]["by_bmi"].items()} for k in ("m","f")})
