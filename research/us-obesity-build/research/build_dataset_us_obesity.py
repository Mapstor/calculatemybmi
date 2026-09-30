import csv

H111="https://www.cdc.gov/nchs/data/hestat/hestat111.htm"
H112="https://www.cdc.gov/nchs/data/hestat/hestat112.htm"
H119="https://www.cdc.gov/nchs/data/hestat/hestat119.htm"
DB508="https://www.cdc.gov/nchs/products/databriefs/db508.htm"
FAST="https://www.cdc.gov/nchs/fastats/obesity-overweight.htm"
S111="NCHS Health E-Stat 111 (Feb 2026)"
S112="NCHS Health E-Stat 112 (Feb 2026)"
S119="NCHS Health E-Stat 119 (Jun 2026)"
S508="NCHS Data Brief 508 (Sep 2024)"
SFAST="CDC NCHS FastStats: Obesity and Overweight"

def mid(p):
    m={"1960-1962":1961.5,"1963-1965":1964.5,"1966-1970":1968.5,"1971-1974":1973.0,"1976-1980":1978.5,
       "1988-1994":1991.5,"1999-2000":2000.0,"2001-2002":2002.0,"2003-2004":2004.0,"2005-2006":2006.0,
       "2007-2008":2008.0,"2009-2010":2010.0,"2011-2012":2012.0,"2013-2014":2014.0,"2015-2016":2016.0,
       "2017-2018":2018.0,"2017-Mar 2020":2018.6,"Aug 2021-Aug 2023":2022.6}
    return m[p]

rows=[]
def add(dataset,pop,age,sex,gtype,group,period,measure,pct,se,est,note,src,url):
    rows.append(dict(dataset=dataset,population=pop,age_group=age,sex=sex,group_type=gtype,group=group,
        survey_period=period,midpoint_year=mid(period),measure=measure,percent=pct,standard_error=se,
        estimate_type=est,note=note,source=src,source_url=url))

M=["overweight","obesity","severe obesity"]
# ---- HE-Stat 111 Table 1, adults 20-74, age-adjusted: (n, All OW,OB,SEV, Men..., Women...) values as (pct,se)
t1_2074 = {
"1960-1962":[(31.5,.5),(13.4,.5),(0.9,.1),(38.7,.7),(10.7,.7),(0.3,.1),(24.7,.8),(15.8,.6),(1.4,.2)],
"1971-1974":[(32.7,.6),(14.5,.4),(1.3,.2),(41.7,1.1),(12.1,.6),(0.6,.2),(24.3,.7),(16.6,.6),(2.0,.3)],
"1976-1980":[(32.1,.6),(15.0,.4),(1.4,.1),(39.9,.8),(12.7,.6),(0.4,.1),(24.9,.8),(17.0,.6),(2.2,.3)],
"1988-1994":[(32.6,.6),(23.2,.7),(3.0,.3),(40.3,.8),(20.5,.7),(1.8,.3),(25.1,.8),(25.9,1.0),(4.1,.3)],
"1999-2000":[(33.6,1.1),(30.9,1.6),(5.0,.6),(39.2,1.5),(27.7,1.6),(3.3,.7),(28.0,1.7),(34.0,1.8),(6.6,.8)],
"2001-2002":[(34.4,1.1),(31.2,1.1),(5.4,.5),(41.5,1.4),(28.3,1.1),(3.9,.7),(27.3,1.6),(34.1,1.6),(6.8,.6)],
"2003-2004":[(33.4,1.2),(32.9,1.3),(5.1,.6),(39.4,1.5),(31.7,1.4),(3.0,.4),(27.3,1.3),(34.0,1.9),(7.3,1.0)],
"2005-2006":[(32.2,.9),(35.1,1.5),(6.2,.5),(39.7,1.3),(33.8,2.2),(4.3,.5),(24.7,1.3),(36.3,1.5),(7.9,.8)],
"2007-2008":[(33.6,.8),(34.3,1.2),(6.0,.4),(39.4,1.4),(32.5,1.5),(4.4,.5),(27.9,1.2),(36.2,1.3),(7.6,.6)],
"2009-2010":[(32.7,1.0),(36.1,.9),(6.6,.2),(38.0,1.2),(35.9,1.7),(4.6,.4),(27.5,1.5),(36.1,.9),(8.5,.5)],
"2011-2012":[(33.3,1.4),(35.3,1.4),(6.6,.6),(37.3,1.5),(33.9,1.5),(4.5,1.0),(29.5,2.0),(36.6,1.6),(8.6,.7)],
"2013-2014":[(31.9,.8),(38.2,1.0),(8.1,.8),(38.2,1.3),(35.5,1.2),(5.7,.7),(25.8,.9),(41.0,1.4),(10.5,1.0)],
"2015-2016":[(31.0,.8),(40.0,1.8),(8.0,.6),(35.8,1.8),(38.3,2.4),(5.9,.8),(26.3,1.1),(41.6,1.7),(10.1,.7)],
"2017-2018":[(30.3,1.2),(42.8,1.9),(9.6,1.0),(33.7,1.9),(43.5,2.7),(7.3,1.0),(26.9,.9),(42.1,2.1),(12.0,1.5)],
"Aug 2021-Aug 2023":[(31.3,.9),(40.8,2.0),(10.2,.8),(35.1,1.4),(39.7,1.9),(7.2,.8),(27.6,1.0),(42.0,2.4),(13.2,1.1)],
}
# ---- HE-Stat 111 Table 1, adults 20+, age-adjusted
t1_20p = {
"1988-1994":[(33.1,.6),(22.9,.7),(2.8,.2),(40.7,.8),(20.2,.7),(1.7,.3),(25.9,.7),(25.4,.9),(3.9,.3)],
"1999-2000":[(34.0,1.0),(30.5,1.5),(4.7,.6),(39.7,1.4),(27.5,1.5),(3.1,.7),(28.6,1.6),(33.4,1.7),(6.2,.7)],
"2001-2002":[(35.1,1.1),(30.5,1.1),(5.1,.5),(42.2,1.3),(27.7,1.0),(3.6,.6),(28.2,1.7),(33.2,1.5),(6.5,.6)],
"2003-2004":[(34.1,1.1),(32.2,1.2),(4.8,.6),(39.7,1.5),(31.1,1.3),(2.8,.4),(28.6,1.2),(33.2,1.7),(6.9,.9)],
"2005-2006":[(32.6,.8),(34.3,1.4),(5.9,.5),(39.9,1.3),(33.3,2.0),(4.2,.5),(25.5,1.2),(35.3,1.4),(7.4,.7)],
"2007-2008":[(34.3,.8),(33.7,1.1),(5.7,.4),(40.1,1.4),(32.2,1.4),(4.2,.5),(28.6,1.2),(35.4,1.1),(7.3,.6)],
"2009-2010":[(33.0,1.0),(35.7,.9),(6.3,.2),(38.4,1.1),(35.5,1.7),(4.4,.3),(27.9,1.4),(35.8,.9),(8.1,.5)],
"2011-2012":[(33.6,1.3),(34.9,1.4),(6.4,.6),(37.8,1.5),(33.5,1.4),(4.4,.9),(29.7,1.8),(36.1,1.7),(8.3,.7)],
"2013-2014":[(32.5,.8),(37.7,.9),(7.7,.7),(38.7,1.2),(35.0,1.1),(5.5,.6),(26.5,.8),(40.4,1.3),(9.9,.9)],
"2015-2016":[(31.6,.8),(39.6,1.6),(7.7,.6),(36.5,1.6),(37.9,2.3),(5.6,.7),(26.9,1.0),(41.1,1.6),(9.7,.7)],
"2017-2018":[(30.7,.9),(42.4,1.8),(9.2,.9),(34.1,1.8),(43.0,2.7),(6.9,1.0),(27.5,1.0),(41.9,2.0),(11.5,1.3)],
"Aug 2021-Aug 2023":[(31.7,.9),(40.3,1.9),(9.7,.7),(35.5,1.4),(39.3,1.9),(6.8,.7),(28.1,.9),(41.4,2.3),(12.6,1.0)],
}
for tbl,age,ds in [(t1_2074,"20-74","HE111_T1_adults_20-74"),(t1_20p,"20+","HE111_T1_adults_20plus")]:
    for per,vals in tbl.items():
        for i,sex in enumerate(["all","men","women"]):
            for j,meas in enumerate(M):
                p,se=vals[i*3+j]
                note="1960-1962 NHES included ages 18-79" if per=="1960-1962" else ""
                add(ds,"adults",age,sex,"all","all",per,meas,p,se,"age-adjusted",note,S111,H111)

# ---- HE-Stat 111 Table 2: crude obesity by sex x age
t2 = {
"1988-1994":[(17.7,.7),(27.9,1.1),(23.7,.9),(14.8,.8),(25.4,1.2),(21.2,1.4),(20.7,1.3),(30.3,1.5),(25.6,1.1)],
"1999-2000":[(26.0,1.3),(33.5,3.0),(33.5,1.7),(23.7,1.6),(28.8,2.9),(31.7,2.2),(28.3,2.0),(37.7,3.3),(35.0,2.2)],
"2001-2002":[(26.1,1.4),(33.9,1.5),(32.8,1.6),(22.3,1.5),(32.2,1.7),(29.9,2.0),(29.8,2.1),(35.7,2.1),(35.0,2.0)],
"2003-2004":[(28.5,1.5),(36.8,1.8),(31.0,1.3),(28.0,2.2),(34.8,2.5),(30.4,1.9),(28.9,2.3),(38.8,2.7),(31.5,1.7)],
"2005-2006":[(29.1,2.0),(40.4,2.0),(33.4,1.1),(27.9,2.8),(39.6,2.9),(32.2,2.1),(30.5,2.3),(41.1,2.3),(34.4,2.3)],
"2007-2008":[(30.7,2.0),(36.2,1.7),(35.1,1.0),(27.4,1.9),(34.2,2.3),(37.0,2.0),(34.0,2.5),(38.1,2.2),(33.5,1.7)],
"2009-2010":[(32.6,1.7),(36.6,1.0),(39.7,1.5),(33.2,2.7),(37.2,1.8),(36.6,2.4),(31.9,1.6),(36.0,1.7),(42.3,1.9)],
"2011-2012":[(30.3,1.9),(39.5,1.6),(35.4,2.0),(29.0,2.6),(39.4,1.6),(32.0,2.2),(31.8,1.7),(39.5,2.2),(38.1,2.9)],
"2013-2014":[(34.3,1.5),(41.0,2.1),(38.5,1.6),(31.6,2.1),(37.2,2.4),(37.5,3.0),(37.0,1.3),(44.6,2.6),(39.4,1.9)],
"2015-2016":[(35.7,1.9),(42.8,2.6),(41.0,1.9),(34.8,2.8),(40.8,2.9),(38.5,1.8),(36.5,1.6),(44.7,3.1),(43.1,2.8)],
"2017-2018":[(40.0,2.6),(44.8,1.9),(42.8,2.5),(40.3,3.8),(46.4,3.2),(42.2,3.3),(39.7,2.7),(43.3,2.7),(43.3,3.0)],
"Aug 2021-Aug 2023":[(35.5,3.0),(46.4,1.8),(38.9,1.5),(34.3,2.8),(45.4,1.9),(38.0,2.3),(36.8,3.6),(47.4,2.1),(39.6,1.9)],
}
for per,vals in t2.items():
    for i,sex in enumerate(["all","men","women"]):
        for j,age in enumerate(["20-39","40-59","60+"]):
            p,se=vals[i*3+j]
            add("HE111_T2_obesity_by_age","adults",age,sex,"age",age,per,"obesity",p,se,"crude","",S111,H111)

# ---- HE-Stat 111 Table 3: age-adjusted obesity by race/Hispanic origin, latest period only
race = {"all":[("Asian, non-Hispanic",13.1,3.2,""),("Black, non-Hispanic",52.1,2.7,""),("White, non-Hispanic",39.3,1.8,""),("Hispanic",44.0,3.7,""),("Mexican American",48.0,5.0,"")],
        "men":[("Asian, non-Hispanic",17.8,3.9,""),("Black, non-Hispanic",47.3,4.4,"NCHS dagger: see Ogden et al. 2025 on race/Hispanic-origin estimates"),("White, non-Hispanic",38.3,1.9,""),("Hispanic",43.6,3.0,""),("Mexican American",44.2,3.7,"")],
        "women":[("Asian, non-Hispanic",9.8,3.1,"UNRELIABLE: does not meet NCHS standards of reliability or precision - do not display"),("Black, non-Hispanic",56.0,3.4,""),("White, non-Hispanic",40.4,2.0,""),("Hispanic",44.6,4.8,""),("Mexican American",52.1,7.0,"UNRELIABLE: does not meet NCHS standards of reliability or precision - do not display")]}
for sex,items in race.items():
    for g,p,se,n in items:
        add("HE111_T3_obesity_by_race","adults","20+",sex,"race_ethnicity",g,"Aug 2021-Aug 2023","obesity",p,se,"age-adjusted",n,S111,H111)

# ---- DB 508: crude totals, sex, age (obesity + severe), education; age-adjusted totals; 10-yr trend
db_ob = {"all":[("20+",40.3,1.8),("20-39",35.5,3.0),("40-59",46.4,1.8),("60+",38.9,1.5)],
         "men":[("20+",39.2,1.9),("20-39",34.3,2.8),("40-59",45.4,1.9),("60+",38.0,2.3)],
         "women":[("20+",41.3,2.2),("20-39",36.8,3.6),("40-59",47.4,2.1),("60+",39.6,1.9)]}
db_sev = {"all":[("20+",9.4,0.7),("20-39",9.5,1.0),("40-59",12.0,1.0),("60+",6.6,0.6)],
          "men":[("20+",6.7,0.7),("20-39",6.1,0.8),("40-59",9.2,1.3),("60+",4.3,0.6)],
          "women":[("20+",12.1,0.9),("20-39",13.0,1.5),("40-59",14.7,1.4),("60+",8.4,0.8)]}
for meas,d in [("obesity",db_ob),("severe obesity",db_sev)]:
    for sex,items in d.items():
        for age,p,se in items:
            add("DB508_sex_age","adults",age,sex,"age" if age!="20+" else "all",age if age!="20+" else "all","Aug 2021-Aug 2023",meas,p,se,"crude","",S508,DB508)
edu = {"all":[("High school diploma or less",44.6,2.1),("Some college",45.0,1.7),("Bachelor's degree or more",31.6,2.5)],
       "men":[("High school diploma or less",43.3,2.3),("Some college",43.0,2.1),("Bachelor's degree or more",31.1,3.0)],
       "women":[("High school diploma or less",46.0,2.8),("Some college",46.9,2.4),("Bachelor's degree or more",31.9,3.0)]}
for sex,items in edu.items():
    for g,p,se in items:
        add("DB508_education","adults","20+",sex,"education",g,"Aug 2021-Aug 2023","obesity",p,se,"crude","High school diploma or less includes GED",S508,DB508)
# DB 508 Fig 4 cycle not in HE-Stat 111 series
add("DB508_fig4_trend","adults","20+","all","all","all","2017-Mar 2020","obesity",41.9,1.2,"age-adjusted","2017-March 2020 pre-pandemic cycle; DB 508 found no significant change vs Aug 2021-Aug 2023",S508,DB508)
add("DB508_fig4_trend","adults","20+","all","all","all","2017-Mar 2020","severe obesity",9.2,0.6,"age-adjusted","2017-March 2020 pre-pandemic cycle",S508,DB508)

# ---- HE-Stat 119: underweight (adults crude + adj, kids)
add("HE119_underweight","adults","20+","all","all","all","Aug 2021-Aug 2023","underweight",1.6,0.2,"age-adjusted","crude estimate also 1.6",S119,H119)
add("HE119_underweight","adults","20+","men","all","all","Aug 2021-Aug 2023","underweight",1.1,"","crude","",S119,H119)
add("HE119_underweight","adults","20+","women","all","all","Aug 2021-Aug 2023","underweight",2.0,"","crude","",S119,H119)
add("HE119_underweight","children and adolescents","2-19","all","all","all","Aug 2021-Aug 2023","underweight",4.4,0.5,"crude","BMI below 5th percentile, 2000 CDC growth charts",S119,H119)

# ---- HE-Stat 111 crude snapshot (text)
add("HE111_crude_snapshot","adults","20+","all","all","all","Aug 2021-Aug 2023","overweight",32.1,"","crude","crude estimates stated in HE-Stat 111 text/footnote",S111,H111)
add("HE111_crude_snapshot","adults","20+","all","all","all","Aug 2021-Aug 2023","obesity",40.3,"","crude","",S111,H111)
add("HE111_crude_snapshot","adults","20+","all","all","all","Aug 2021-Aug 2023","severe obesity",9.4,"","crude","severe obesity is a subset of obesity",S111,H111)
# ---- HE-Stat 119 Table 3: underweight, adults 20-74, age-adjusted (endpoints used for derived healthy-weight share)
add("HE119_underweight","adults","20-74","all","all","all","1960-1962","underweight",4.0,"","age-adjusted","ages 20-74; used for calculated healthy-weight share",S119,H119)
add("HE119_underweight","adults","20-74","all","all","all","Aug 2021-Aug 2023","underweight",1.7,"","age-adjusted","ages 20-74; used for calculated healthy-weight share",S119,H119)
# ---- CALCULATED rows (all inputs are NCHS primary figures above; formula in note)
SC="Calculated by CalculateMyBMI from NCHS figures"
add("CALC_derived","adults","20+","all","all","all","Aug 2021-Aug 2023","overweight or obesity",72.4,"","calculated","= 32.1 overweight + 40.3 obesity (HE-Stat 111 crude)",SC,H111)
add("CALC_derived","adults","20+","all","all","all","Aug 2021-Aug 2023","healthy weight",26.0,"","calculated","= 100 - 1.6 underweight (HE-Stat 119) - 32.1 overweight - 40.3 obesity (HE-Stat 111), crude",SC,H111)
add("CALC_derived","adults","20+","all","all","all","Aug 2021-Aug 2023","obesity excluding severe (BMI 30.0-39.9)",30.9,"","calculated","= 40.3 obesity - 9.4 severe obesity (HE-Stat 111 crude)",SC,H111)
add("CALC_derived","adults","20-74","all","all","all","1960-1962","healthy weight",51.1,"","calculated","= 100 - 4.0 underweight (HE-Stat 119) - 31.5 overweight - 13.4 obesity (HE-Stat 111), age-adjusted",SC,H111)
add("CALC_derived","adults","20-74","all","all","all","Aug 2021-Aug 2023","healthy weight",26.2,"","calculated","= 100 - 1.7 underweight (HE-Stat 119) - 31.3 overweight - 40.8 obesity (HE-Stat 111), age-adjusted",SC,H111)

# ---- HE-Stat 112 Table 1: children 2-19 (crude)
t112 = {
"1971-1974":[(10.2,.6),(5.2,.3),(1.0,.1),(10.3,.8),(5.3,.5),(1.0,.2),(10.1,.8),(5.1,.4),(1.0,.2)],
"1976-1980":[(9.2,.4),(5.5,.4),(1.3,.2),(9.4,.6),(5.4,.4),(1.2,.3),(9.0,.5),(5.6,.6),(1.3,.3)],
"1988-1994":[(13.0,.7),(10.0,.5),(2.6,.4),(12.6,.9),(10.2,.7),(2.7,.5),(13.4,.9),(9.8,.8),(2.6,.4)],
"1999-2000":[(14.2,.9),(13.9,.9),(3.6,.5),(15.0,1.9),(14.0,1.2),(3.7,.7),(13.4,.8),(13.8,1.1),(3.6,.6)],
"2001-2002":[(14.6,.6),(15.4,.9),(5.2,.5),(14.2,.7),(16.4,1.0),(6.1,.8),(15.0,.9),(14.3,1.3),(4.2,.6)],
"2003-2004":[(16.5,.8),(17.1,1.3),(5.1,.6),(16.6,1.0),(18.2,1.5),(5.4,.8),(16.3,.9),(16.0,1.4),(4.7,.7)],
"2005-2006":[(14.6,.9),(15.4,1.4),(4.7,.6),(14.7,1.2),(15.9,1.5),(4.9,.8),(14.6,1.0),(14.9,1.6),(4.5,.7)],
"2007-2008":[(14.8,.7),(16.8,1.3),(4.9,.6),(14.3,.7),(17.7,1.4),(5.5,.8),(15.4,1.5),(15.9,1.5),(4.3,.8)],
"2009-2010":[(14.9,.8),(16.9,.7),(5.6,.6),(14.4,1.0),(18.6,1.1),(6.4,1.0),(15.4,.9),(15.0,.8),(4.7,.6)],
"2011-2012":[(14.9,.9),(16.9,1.0),(5.6,.7),(15.4,1.3),(16.7,1.4),(5.7,.9),(14.5,1.4),(17.2,1.2),(5.5,.8)],
"2013-2014":[(16.2,.6),(17.2,1.1),(6.0,.6),(16.4,.8),(17.2,1.3),(5.6,.6),(16.0,1.0),(17.1,1.6),(6.3,.9)],
"2015-2016":[(16.6,.8),(18.5,1.3),(5.6,.8),(15.7,1.0),(19.1,1.7),(6.3,1.0),(17.6,1.2),(17.8,1.2),(4.9,.9)],
"2017-2018":[(16.1,.8),(19.3,1.0),(6.1,.7),(14.7,1.2),(20.5,1.1),(6.9,.9),(17.6,1.1),(18.0,1.4),(5.2,.7)],
"Aug 2021-Aug 2023":[(15.1,1.0),(21.1,1.1),(7.0,.6),(13.0,.9),(23.0,1.4),(7.8,1.2),(17.5,1.5),(19.1,1.5),(6.3,.8)],
}
for per,vals in t112.items():
    for i,sex in enumerate(["all","boys","girls"]):
        for j,meas in enumerate(M):
            p,se=vals[i*3+j]
            add("HE112_T1_children_2-19","children and adolescents","2-19",sex,"all","all",per,meas,p,se,"crude",
                "child cutoffs: overweight >=85th to <95th pct; obesity >=95th pct; severe >=120% of 95th pct (2000 CDC growth charts)",S112,H112)
# ---- HE-Stat 112 Table 2: obesity by age group, all sexes
t112b = {"1963-1965":[None,(4.2,.4),None],"1966-1970":[None,None,(4.6,.3)],
"1971-1974":[(5.0,.6),(4.0,.5),(6.1,.6)],"1976-1980":[(5.0,.6),(6.5,.6),(5.0,.5)],"1988-1994":[(7.2,.7),(11.3,1.0),(10.5,.9)],
"1999-2000":[(10.3,1.7),(15.1,1.4),(14.8,.9)],"2001-2002":[(10.6,1.8),(16.2,1.6),(16.7,1.1)],"2003-2004":[(13.9,1.6),(18.8,1.3),(17.4,1.7)],
"2005-2006":[(10.7,1.1),(15.1,2.1),(17.8,1.8)],"2007-2008":[(10.1,1.2),(19.6,1.2),(18.1,1.7)],"2009-2010":[(12.1,1.2),(18.0,.8),(18.4,1.3)],
"2011-2012":[(8.4,1.3),(17.7,1.6),(20.5,1.7)],"2013-2014":[(9.4,1.3),(17.4,1.7),(20.6,2.1)],"2015-2016":[(13.9,1.1),(18.4,1.7),(20.6,2.0)],
"2017-2018":[(13.4,1.3),(20.3,1.8),(21.2,1.3)],"Aug 2021-Aug 2023":[(14.9,1.3),(22.1,2.0),(22.9,1.7)]}
for per,vals in t112b.items():
    for k,age in enumerate(["2-5","6-11","12-19"]):
        v=vals[k]
        if v is None: continue
        note="1966-1970 value is ages 12-17, not 12-19" if per=="1966-1970" else ""
        add("HE112_T2_children_by_age","children and adolescents",age,"all","age",age,per,"obesity",v[0],v[1],"crude",note,S112,H112)

with open("us-obesity-data-nhanes-1960-2023.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print("rows:",len(rows))
