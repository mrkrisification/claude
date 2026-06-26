#!/usr/bin/env python3
"""
Annotated dashboard: is the regulatory history visible in group results?
-> charts/a1_regulation_vs_results.png

Overlays the regulatory timeline (from wiki/themes/regulation.md) on group
revenue, EBITDA and EBITDA margin (data/financials.duckdb). The honest finding:
regulation shows up in TWO ways — sharp one-offs (the 1998-2000 liberalisation
margin collapse; the 2008 civil-servant restructuring cliff) and a slow grind
(the 2009-2014 MTR/roaming era) — while some big events (RLAH 2017) are masked
at group level. Uses .fetchall() only.
"""
import os
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, "data", "financials.duckdb")
OUT  = os.path.join(ROOT, "charts", "a1_regulation_vs_results.png")

INK="#0f3460"; ACC="#4cc9f0"; GRN="#2d9e6b"; RED="#e63946"; ORG="#e07a3c"; MUT="#55606e"; GRID="#dde2e8"

con = duckdb.connect(DB, read_only=True)
def series(metric):
    return dict(con.execute("SELECT fiscal_year, value FROM financials WHERE metric_name=? "
                            "AND segment='total' AND restated_flag=FALSE", [metric]).fetchall())
rev = series("revenue"); eb = series("ebitda"); ebx = series("ebitda_excl_restructuring")
years = sorted(rev)
R  = [rev[y] for y in years]
E  = [eb[y] for y in years]
M  = [100*eb[y]/rev[y] for y in years]                       # reported EBITDA margin
MX = [(100*ebx[y]/rev[y] if y in ebx else None) for y in years]  # excl-restructuring margin

# Regulatory markers: (year, short label, kind) kind: 'sharp' | 'grind' | 'masked' | 'frame'
MARK = [
    (1998, "Liberalisation\n(TKG)", "sharp"),
    (2003, "TKG 2003\n18 sub-markets", "frame"),
    (2007, "EU roaming\nReg I", "grind"),
    (2008, "Civil-servant\n€632m charge", "sharp"),
    (2012, "Roaming\nReg III", "grind"),
    (2013, "MTR→0.80c\nFTR→0.14c", "grind"),
    (2017, "RLAH\n(roaming end)", "masked"),
    (2022, "Wholesale dereg.\n+ CPI indexation", "frame"),
    (2024, "Belarus\ndividend freeze", "frame"),
]
KCOL = {"sharp":RED, "grind":ORG, "masked":"#8a93a0", "frame":INK}

fig = plt.figure(figsize=(16, 9.6)); fig.patch.set_facecolor("white")
gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.15], hspace=0.30,
                      left=0.065, right=0.975, top=0.86, bottom=0.10)

fig.text(0.065, 0.945, "Is regulation visible in A1's group results?",
         fontsize=22, fontweight="bold", color=INK)
fig.text(0.065, 0.90, "Regulatory milestones (from the annual reports) overlaid on group revenue, EBITDA and EBITDA margin, "
         "FY1998–FY2025.", fontsize=11.5, color=MUT)
# legend for marker kinds
lx=0.065
for kind,lab in [("sharp","sharp / one-off"),("grind","gradual grind"),("masked","masked at group level"),("frame","framework")]:
    fig.text(lx, 0.872, "■", color=KCOL[kind], fontsize=12); fig.text(lx+0.014, 0.872, lab, fontsize=9, color=MUT)
    lx += 0.10

def markers(ax, ytop):
    for y,_,kind in MARK:
        ax.axvline(y, color=KCOL[kind], lw=1.0, ls=(0,(4,3)), alpha=0.55, zorder=1)

# ---- Top: Revenue + EBITDA ----
axT = fig.add_subplot(gs[0,0])
axT.axvspan(2009, 2014, color=ORG, alpha=0.07, zorder=0)
markers(axT, None)
axT.fill_between(years, R, color=ACC, alpha=0.18, zorder=2)
axT.plot(years, R, color=INK, lw=2.4, zorder=3, label="Revenue")
axT.plot(years, E, color=GRN, lw=2.6, zorder=3, label="EBITDA (reported)")
axT.set_ylabel("€ million"); axT.set_ylim(0, 6200)
axT.set_title("Revenue & EBITDA", fontsize=13, color=INK, loc="left", pad=8, fontweight="bold")
axT.grid(axis="y", color=GRID, lw=0.8); axT.set_axisbelow(True)
for sp in ("top","right"): axT.spines[sp].set_visible(False)
axT.legend(fontsize=10, frameon=False, loc="upper left")
# marker labels along the top
for y,lab,kind in MARK:
    axT.annotate(lab, xy=(y, 6150), fontsize=7.6, color=KCOL[kind], ha="center", va="top",
                 fontweight="bold", linespacing=0.95)
# EBITDA cliff callout
axT.annotate("2008 EBITDA cliff =\ncivil-servant social plan,\nnot a telecom rule",
             xy=(2008, eb[2008]), xytext=(2003.2, 720), fontsize=8.4, color=RED,
             ha="left", va="center", arrowprops=dict(arrowstyle="->", color=RED, lw=1.1))

# ---- Bottom: EBITDA margin (the clearest regulatory signature) ----
axB = fig.add_subplot(gs[1,0])
axB.axvspan(2009, 2014, color=ORG, alpha=0.09, zorder=0)
markers(axB, None)
axB.plot(years, M, color=GRN, lw=2.8, zorder=4, label="EBITDA margin (reported)")
# excl-restructuring margin (dashed, with gaps)
xs=[y for y,v in zip(years,MX) if v is not None]; ys=[v for v in MX if v is not None]
axB.plot(xs, ys, color="#1f6f4e", lw=1.6, ls=(0,(5,2)), zorder=3, label="margin excl. restructuring")
# 2008 underlying point (ebitda excl restructuring ~€1,928m -> ~37%, from wiki/metrics/ebitda.md)
axB.scatter([2008],[37.3], s=42, color="#1f6f4e", zorder=5, marker="D")
axB.annotate("underlying ≈37%\n(excl. €632m one-off)", xy=(2008,37.3), xytext=(2009.4,44.5),
             fontsize=8.2, color="#1f6f4e", arrowprops=dict(arrowstyle="->", color="#1f6f4e", lw=1.0))
axB.set_ylabel("EBITDA margin (%)"); axB.set_ylim(20, 58)
axB.set_title("EBITDA margin — where regulation actually shows up", fontsize=13, color=INK, loc="left", pad=8, fontweight="bold")
axB.grid(axis="y", color=GRID, lw=0.8); axB.set_axisbelow(True)
for sp in ("top","right"): axB.spines[sp].set_visible(False)
axB.legend(fontsize=9.5, frameon=False, loc="upper right")

def box(ax, x, y, text, color):
    ax.annotate(text, xy=(x,y), fontsize=8.6, color=color, ha="left", va="top",
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=color, lw=1.0), zorder=6)
box(axB, 1998.1, 51.5, "Liberalisation: 52%→26%\nmonopoly → competition —\nthe clearest regulatory mark", RED)
box(axB, 2009.1, 30.0, "MTR + roaming-cut era:\na slow grind — 6 straight years\nof revenue decline, margin 37→31%", ORG)
axB.annotate("RLAH 2017: barely a ripple —\nmasked by convergence & CEE growth", xy=(2017, M[years.index(2017)]),
             xytext=(2017.3, 24.5), fontsize=8.4, color="#5b6470",
             arrowprops=dict(arrowstyle="->", color="#8a93a0", lw=1.0))

axB.set_xlabel("Fiscal year")
for ax in (axT, axB):
    ax.set_xlim(1997.3, 2025.7); ax.set_xticks(range(1998,2026,2))
    ax.set_xticklabels([str(y)[2:] for y in range(1998,2026,2)], fontsize=9)

fig.text(0.065, 0.045, "Verdict: regulation is visible as (1) sharp one-offs — the 1998–2000 liberalisation margin collapse and the "
         "2008 civil-servant charge — and (2) a gradual margin/revenue grind in 2009–2014 (MTR + roaming). Pure telecom-rule events "
         "like RLAH (2017) are largely absorbed by M&A, convergence and CPI-linked price rises. Source: financials.duckdb + wiki/themes/regulation.md.",
         fontsize=8.5, color="#8a93a0")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=140, facecolor="white", bbox_inches="tight")
print("wrote", OUT)
