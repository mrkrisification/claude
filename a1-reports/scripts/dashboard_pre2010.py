#!/usr/bin/env python3
"""
One-page dashboard of the FY2007-2009 mobile footprint by country
-> charts/a1_mobile_footprint_2007_2009.png

Basis note: pre-2010 the only per-country split is the Mobile Communication
segment (mobile-only, excl. fixed line). Data: financials.duckdb metrics
mobile_revenue / mobile_ebitda (loaded by scripts/load_segments_pre2010.py).
Uses .fetchall() only.
"""
import os
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, "data", "financials.duckdb")
OUT  = os.path.join(ROOT, "charts", "a1_mobile_footprint_2007_2009.png")

INK="#0f3460"; GRID="#dfe3e9"; RED="#e63946"; MUT="#55606e"
YEARS=[2007,2008,2009]
YCOL={2007:"#a9c7e8",2008:"#4c86c6",2009:"#0f3460"}
ORDER=["austria","bulgaria","croatia","belarus","slovenia","serbia","north_macedonia"]
NAME={"austria":"Austria","bulgaria":"Bulgaria","croatia":"Croatia","belarus":"Belarus",
      "slovenia":"Slovenia","serbia":"Serbia","north_macedonia":"N. Maced."}

con=duckdb.connect(DB, read_only=True)
def grid(metric):
    d=dict(((s,y),v) for s,y,v in con.execute(
        "SELECT segment, fiscal_year, value FROM financials WHERE metric_name=? "
        "AND fiscal_year IN (2007,2008,2009)", [metric]).fetchall())
    return {y:[d.get((s,y),0.0) for s in ORDER] for y in YEARS}
rev=grid("mobile_revenue"); eb=grid("mobile_ebitda")

# International share of mobile revenue
def intl_share(y):
    at=rev[y][ORDER.index("austria")]; tot=sum(rev[y])
    return 100*(tot-at)/tot if tot else 0
shares=[intl_share(y) for y in YEARS]

fig=plt.figure(figsize=(15.5,8.2)); fig.patch.set_facecolor("white")
gs=fig.add_gridspec(2,2,height_ratios=[1,1],width_ratios=[1.55,1],
                    hspace=0.42,wspace=0.22,left=0.06,right=0.975,top=0.82,bottom=0.09)

# Header
fig.text(0.06,0.93,"A1 Group — CEE Mobile Footprint at the Expansion Peak",
         fontsize=21,fontweight="bold",color=INK)
fig.text(0.06,0.885,"FY2007–FY2009, by country · Mobile Communication segment only "
         "(excl. fixed line) · €m · Source: A1 analyst factsheets",fontsize=11,color=MUT)

def bars(ax, data, title, ylab):
    n=len(ORDER); w=0.26; xs=list(range(n))
    for k,y in enumerate(YEARS):
        off=(k-1)*w
        ax.bar([x+off for x in xs], data[y], width=w, color=YCOL[y],
               edgecolor="white", linewidth=0.4, label=str(y))
    ax.axhline(0,color="#9aa4b0",lw=0.8)
    ax.set_title(title,fontsize=13,color=INK,loc="left",pad=8,fontweight="bold")
    ax.set_ylabel(ylab,fontsize=10)
    ax.set_xticks(xs); ax.set_xticklabels([NAME[s] for s in ORDER],fontsize=9.5)
    ax.grid(axis="y",color=GRID,lw=0.8); ax.set_axisbelow(True)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    ax.legend(fontsize=9.5,frameon=False,loc="upper right",title="FY")

axR=fig.add_subplot(gs[0,0]); bars(axR,rev,"Mobile revenue by country","€ million")
axE=fig.add_subplot(gs[1,0]); bars(axE,eb,"Mobile EBITDA by country  (negative = start-up losses: Serbia, Macedonia)","€ million")

# Right top: International share of mobile revenue
axS=fig.add_subplot(gs[0,1])
axS.plot(YEARS,shares,color="#e07a3c",lw=2.8,marker="o",ms=6)
axS.axhline(50,color=RED,ls="--",lw=1.1)
for y,sh in zip(YEARS,shares):
    axS.annotate(f"{sh:.1f}%",(y,sh),textcoords="offset points",xytext=(0,8),
                 ha="center",color="#e07a3c",fontsize=10.5,fontweight="bold")
axS.set_title("International share of mobile revenue",fontsize=13,color=INK,loc="left",pad=8,fontweight="bold")
axS.set_ylim(40,58); axS.set_xticks(YEARS)
axS.text(2007,50.7,"50%",color=RED,fontsize=9)
axS.grid(axis="y",color=GRID,lw=0.8); axS.set_axisbelow(True)
for sp in ("top","right"): axS.spines[sp].set_visible(False)

# Right bottom: KPI callouts
axK=fig.add_subplot(gs[1,1]); axK.axis("off")
tot09=sum(rev[2009]); tot07=sum(rev[2007])
kpis=[
 ("Mobile revenue 2009", f"€{tot09:,.0f} m", f"{(tot09/tot07-1)*100:+.0f}% vs 2007"),
 ("International (ex-AT)", f"{shares[-1]:.0f}% of mobile", "already past half by 2008"),
 ("Markets", "7 countries", "AT, BG, HR, BY, SI, RS, MK"),
 ("Belarus (velcom)", "entered Q4-2007", "partial year; €310 m rev by 2008"),
]
y0=0.92
for head,big,sub in kpis:
    axK.text(0.02,y0,head,fontsize=10,color=MUT,transform=axK.transAxes)
    axK.text(0.02,y0-0.075,big,fontsize=15,color=INK,fontweight="bold",transform=axK.transAxes)
    axK.text(0.50,y0-0.066,sub,fontsize=9,color=MUT,transform=axK.transAxes)
    y0-=0.245

fig.text(0.06,0.025,"Mobile-only basis — not comparable to the FY2010+ total-operations series "
         "(which adds fixed line, dominated by Austria). Operators: mobilkom=Austria, Mobiltel=Bulgaria, "
         "Velcom=Belarus, Vipnet=Croatia, Si.mobil=Slovenia, Vip mobile=Serbia, Vip operator=Macedonia.",
         fontsize=8.3,color="#8a93a0")

os.makedirs(os.path.dirname(OUT),exist_ok=True)
plt.savefig(OUT,dpi=140,facecolor="white",bbox_inches="tight")
print("wrote",OUT)
