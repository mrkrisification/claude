#!/usr/bin/env python3
"""
Render the 'rising International' story from the per-country segment data in
data/financials.duckdb -> charts/a1_international_rise.png

Left panel : stacked revenue by country segment, 2010-2025 (Austria at the base,
             the six International markets stacked on top).
Right panel: International share of group revenue and EBITDA (%), with the 50%
             crossover highlighted.
Uses .fetchall() only (no pandas/numpy needed).
"""
import os
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB   = os.path.join(ROOT, "data", "financials.duckdb")
OUT  = os.path.join(ROOT, "charts", "a1_international_rise.png")

INK="#0f3460"; GRID="#d9dde3"
ORDER = ["austria","bulgaria","croatia","belarus","serbia","slovenia","north_macedonia"]
LABEL = {"austria":"Austria","bulgaria":"Bulgaria","croatia":"Croatia","belarus":"Belarus",
         "serbia":"Serbia","slovenia":"Slovenia","north_macedonia":"North Macedonia"}
COLOR = {"austria":"#0f3460","bulgaria":"#e07a3c","croatia":"#2d9e6b","belarus":"#c0392b",
         "serbia":"#8e6fb0","slovenia":"#4cc9f0","north_macedonia":"#f2c14e"}

con = duckdb.connect(DB, read_only=True)
years = [r[0] for r in con.execute(
    "SELECT DISTINCT fiscal_year FROM financials WHERE segment=? ORDER BY 1",["austria"]).fetchall()]

def series(metric, seg):
    d = dict(con.execute(
        "SELECT fiscal_year, value FROM financials "
        "WHERE metric_name=? AND segment=? AND restated_flag=FALSE", [metric, seg]).fetchall())
    return [d.get(y, 0.0) for y in years]

rev = {s: series("revenue", s) for s in ORDER}

# International share (exclude corporate from the denominator)
def share(metric):
    out = []
    for i, y in enumerate(years):
        at = rev["austria"][i] if metric == "revenue" else series("ebitda","austria")[i]
        intl = sum(series(metric, s)[i] for s in ORDER if s != "austria")
        out.append(100.0 * intl / (at + intl) if (at + intl) else 0)
    return out
rev_share = share("revenue")
eb_share  = share("ebitda")

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15.5, 7.2), gridspec_kw={"width_ratios":[1.35,1]})
fig.suptitle("A1 Group — the rise of International", fontsize=20, fontweight="bold",
             color=INK, x=0.065, ha="left", y=0.98)
fig.text(0.065, 0.925, "Revenue by country segment, and International's share of the group. "
         "Source: A1 analyst factsheets, FY2010–FY2025.", fontsize=10.5, color="#55606e", ha="left")

# ---- Left: stacked revenue ----
bottom = [0.0]*len(years)
for s in ORDER:
    axL.bar(years, rev[s], bottom=bottom, color=COLOR[s], width=0.78,
            edgecolor="white", linewidth=0.4, label=LABEL[s])
    bottom = [b+v for b,v in zip(bottom, rev[s])]
axL.set_title("Revenue by segment (€ million)", fontsize=12.5, color=INK, loc="left", pad=8)
axL.set_ylabel("€ million")
axL.set_xticks(years); axL.set_xticklabels([str(y)[2:] for y in years], fontsize=9)
axL.grid(axis="y", color=GRID, linewidth=0.8); axL.set_axisbelow(True)
for sp in ("top","right"): axL.spines[sp].set_visible(False)
handles = [Patch(facecolor=COLOR[s], label=LABEL[s]) for s in ORDER]
axL.legend(handles=handles, ncol=2, fontsize=9, frameon=False, loc="upper left")

# ---- Right: International share lines ----
axR.plot(years, rev_share, color="#e07a3c", lw=2.6, marker="o", ms=4, label="Revenue")
axR.plot(years, eb_share,  color="#2d9e6b", lw=2.6, marker="s", ms=4, label="EBITDA")
axR.axhline(50, color="#c0392b", lw=1.1, ls="--")
axR.text(years[0], 50.6, "50% — International = half the group", color="#c0392b", fontsize=9)
axR.annotate(f"{rev_share[-1]:.1f}%", (years[-1], rev_share[-1]),
             textcoords="offset points", xytext=(6,-2), color="#e07a3c", fontsize=10, fontweight="bold")
axR.annotate(f"{eb_share[-1]:.1f}%", (years[-1], eb_share[-1]),
             textcoords="offset points", xytext=(6,4), color="#2d9e6b", fontsize=10, fontweight="bold")
axR.set_title("International share of country-segment revenue (%)", fontsize=12.5, color=INK, loc="left", pad=8)
axR.set_ylabel("% of Austria + International (operating country segments)")
axR.set_ylim(30, 56)
axR.set_xticks(years); axR.set_xticklabels([str(y)[2:] for y in years], fontsize=9)
axR.grid(axis="y", color=GRID, linewidth=0.8); axR.set_axisbelow(True)
for sp in ("top","right"): axR.spines[sp].set_visible(False)
axR.legend(fontsize=10, frameon=False, loc="lower right")
fig.text(0.065, -0.01, "International = Bulgaria + Croatia + Belarus + Serbia + Slovenia + North Macedonia. "
         "Country segments do NOT sum to group revenue: a Corporate/Other & eliminations bucket "
         "(incl. A1 Digital) sits outside them and is excluded here.", fontsize=8.5, color="#8a93a0", ha="left")

plt.tight_layout(rect=[0,0.02,1,0.92])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=140, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
