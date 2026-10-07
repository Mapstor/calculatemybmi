import pandas as pd, numpy as np
U="/mnt/user-data/uploads/"
def cyc(s, label):
    d=pd.read_sas(U+f"DEMO_{s}.xpt",format="xport")[["SEQN","RIAGENDR","RIDAGEYR","RIDEXPRG","WTMEC2YR","SDMVPSU","SDMVSTRA","RIDRETH3"]]
    x=pd.read_sas(U+f"DXX_{s}.xpt",format="xport"); keep=[c for c in ["SEQN","DXAEXSTS","DXDTOPF","DXDTOFAT","DXDTOLE"] if c in x.columns]; x=x[keep]
    b=pd.read_sas(U+f"BMX_{s}.xpt",format="xport")[["SEQN","BMXBMI","BMXWT","BMXHT","BMXWAIST"]]
    m=d.merge(x,on="SEQN",how="left").merge(b,on="SEQN",how="left"); m["cycle"]=label; return m
D=pd.concat([cyc("G","2011-12"),cyc("H","2013-14"),cyc("I","2015-16"),cyc("J","2017-18")],ignore_index=True)
D.to_pickle("/home/claude/bf/nhanes_2011_2018.pkl")
