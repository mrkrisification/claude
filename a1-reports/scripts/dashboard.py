#!/usr/bin/env python3
"""One-page A1 Group dashboard rendered from data/financials.duckdb."""
import os, duckdb, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec

HERE = os.path.dirname(__file__)
DB = os.path.join(HERE, "..", "data", "financials.duckdb")
OUT = os.path.join(HERE, "..", "charts", "a1_group_dashboard.png")
con = duckdb.connect(DB)
def s(m):
    return {r[0]: r[1] for r in con.execute(
        "SELECT fiscal_year,value FROM financials WHERE metric_name=? AND segment='total' "
        "AND restated_flag=FALSE ORDER BY 1", [m]).fetchall()}
rev, eb, cx, fcf, ni, emp = (s("revenue"), s("ebitda"), s("capex"),
                             s("free_cash_flow"), s("net_income"), s("employees"))
con.close()
def xy(d): xs=sorted(d); return xs, [d[x] for x in xs]

INK, ACC, GRN, RED, ORG = "#0f3460", "#4cc9f0", "#2d9e6b", "#e63946", "#e07a3c"
plt.rcParams.update({"font.family":"DejaVu Sans","axes.edgecolor":"#cdd5df"})
fig = plt.figure(figsize=(11.7, 8.3), dpi=150)   # A4 landscape
fig.patch.set_facecolor("white")
gs = gridspec.GridSpec(3, 3, height_ratios=[0.42, 1.25, 1.0], hspace=0.55, wspace=0.28,
                       left=0.07, right=0.965, top=0.97, bottom=0.07)

# ---- header band ----
hd = fig.add_subplot(gs[0, :]); hd.axis("off")
hd.text(0, 0.62, "A1 Group  ·  25 Years in Numbers", fontsize=23, fontweight="bold", color=INK)
hd.text(0, 0.12, "Telekom Austria → A1 Group  ·  FY1998–FY2025  ·  EUR million unless noted  ·  source: annual reports → financials.duckdb",
        fontsize=9.5, color="#5b6b82")
yrs=sorted(rev)
hd.text(1.0, 0.62, f"€{rev[max(yrs)]:,.0f}m\nrevenue 2025", fontsize=11, color=INK, ha="right", fontweight="bold")

# ---- hero: revenue + EBITDA ----
ax = fig.add_subplot(gs[1, :])
rx, rv = xy(rev); ex, ev = xy(eb)
ax.fill_between(rx, rv, 0, color=INK, alpha=0.08, zorder=1)
ax.plot(rx, rv, color=INK, lw=2.6, marker="o", ms=3.5, label="Revenue", zorder=3)
ax.plot(ex, ev, color=ORG, lw=2.4, marker="s", ms=3.5, label="EBITDA (as reported)", zorder=3)
ax.set_ylim(0, 6200); ax.set_xlim(1997.3, 2025.7)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:,.0f}"))
ax.grid(axis="y", ls="--", alpha=0.3)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.legend(loc="upper left", frameon=False, fontsize=9)
events = [(2000,"IPO\n(Vienna+NYSE)",rev[2000]),(2005,"MobilTel\n(Bulgaria)",rev[2005]),
          (2008,"€632m\nrestructuring",eb[2008]),(2014,"América Móvil\nmajority",rev[2014]),
          (2023,"EuroTeleSites\nspin-off",rev[2023])]
for x,lab,yv in events:
    ax.axvline(x, color="#b9c2cf", ls=":", lw=0.9, zorder=0)
    ax.annotate(lab, xy=(x,yv), xytext=(x, 5900), fontsize=6.8, ha="center", va="top",
                color="#5b6b82", arrowprops=dict(arrowstyle="-", color="#b9c2cf", lw=0.8))
ax.set_title("Revenue & EBITDA", fontsize=11, fontweight="bold", color=INK, loc="left")

# ---- panel: EBITDA margin ----
ax1 = fig.add_subplot(gs[2, 0])
mx=[y for y in yrs if y in eb and y in rev]; mm=[100*eb[y]/rev[y] for y in mx]
ax1.plot(mx, mm, color=ACC, lw=2.2); ax1.fill_between(mx, mm, 0, color=ACC, alpha=0.12)
ax1.set_ylim(0,60); ax1.set_xlim(1997.3,2025.7); ax1.grid(axis="y",ls="--",alpha=0.3)
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
for sp in ("top","right"): ax1.spines[sp].set_visible(False)
ax1.set_title("EBITDA margin", fontsize=10, fontweight="bold", color=INK, loc="left")

# ---- panel: capex vs FCF ----
ax2 = fig.add_subplot(gs[2, 1])
cxx,cxv=xy(cx); fx,fv=xy(fcf)
ax2.bar(cxx, cxv, color=INK, alpha=0.7, width=0.6, label="Capex")
ax2.plot(fx, fv, color=GRN, lw=2.2, marker="o", ms=3, label="Free cash flow")
ax2.annotate("2013\nspectrum", xy=(2013, cx[2013]), xytext=(2013, 1850), fontsize=6.2,
             ha="center", color="#5b6b82", arrowprops=dict(arrowstyle="-", color="#b9c2cf", lw=0.7))
ax2.set_xlim(1997.3,2025.7); ax2.grid(axis="y",ls="--",alpha=0.3)
for sp in ("top","right"): ax2.spines[sp].set_visible(False)
ax2.legend(loc="upper left", frameon=False, fontsize=7.5)
ax2.set_title("Capex vs free cash flow", fontsize=10, fontweight="bold", color=INK, loc="left")

# ---- panel: net income (red = loss) ----
ax3 = fig.add_subplot(gs[2, 2])
nx,nv=xy(ni); cols=[RED if v<0 else INK for v in nv]
ax3.bar(nx, nv, color=cols, width=0.7)
ax3.axhline(0, color="#888", lw=0.8); ax3.set_xlim(1999.3,2025.7); ax3.grid(axis="y",ls="--",alpha=0.3)
for sp in ("top","right"): ax3.spines[sp].set_visible(False)
ax3.set_title("Net result  (red = loss year)", fontsize=10, fontweight="bold", color=INK, loc="left")

fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("saved", OUT)
