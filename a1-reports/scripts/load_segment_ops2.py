#!/usr/bin/env python3
"""
Load additional per-country OPERATIONAL KPIs from the analyst factsheets.

From "Customer KPIs by Segment_Extd" (Wireline/Wireless detail per country):
  - broadband_rgus            (thousand)  FY2020-FY2024
  - mobile_postpaid_subscribers (thousand) FY2020-FY2024
  - arpu                      (EUR, mobile blended) FY2020-FY2024
  - arpl                      (EUR, fixed)          FY2020-FY2024
From "CustomerKPI by Segment_h":
  - churn_rate                (percent, mobile total) FY2021-FY2025

The Extd sheet exists only in the FY2022-2024 factsheets (it was dropped in
FY2025), so the Extd-sourced KPIs end at FY2024. Each year is read from a
factsheet that reports it: FY2020 from FS_FY2022, FY2021-2024 from FS_FY2024.
Values are loaded only where the factsheet states them (blanks/0 skipped).
Provenance: source_page NULL, notes = factsheet file + sheet, source_year=year+1.
"""
import os, re
import duckdb, openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FS   = os.path.join(ROOT, "factsheets")
DB   = os.path.join(ROOT, "data", "financials.duckdb")

CTY = [("austria","austria"),("bulgaria","bulgaria"),("croatia","croatia"),
       ("belarus","belarus"),("slovenia","slovenia"),("serbia","serbia"),
       ("macedonia","north_macedonia")]
def seg_of(label):
    l = label.lower()
    if any(x in l for x in ("group","international","corporate","elimination")):
        return None
    for kw, code in CTY:
        if kw in l:
            return code
    return None

def rows_of(fn, sh):
    return list(openpyxl.load_workbook(os.path.join(FS, fn), data_only=True,
                                       read_only=True)[sh].iter_rows(values_only=True))

# --- Extended KPIs (Wireline/Wireless detail) ---
EXTD = {"thereof broadband": ("broadband_rgus", "thousand"),
        "thereof postpaid":  ("mobile_postpaid_subscribers", "thousand"),
        "arpu (in eur)":     ("arpu", "EUR"),
        "arpl (in eur)":     ("arpl", "EUR")}

def parse_extd(fn, want_years):
    rows = rows_of(fn, "Customer KPIs by Segment_Extd")
    out = {}
    seg = None; fyc = {}
    for r in rows:
        c1 = str(r[1]).strip() if r[1] else ""
        c2 = str(r[2]).strip() if r[2] else ""
        if c1.lower().startswith("segment "):
            seg = seg_of(c1); continue
        fc = {int(re.search(r"\d{4}", str(c)).group()): j
              for j, c in enumerate(r) if re.fullmatch(r"FY ?\d{4}", str(c).strip() if c else "")}
        if fc:
            fyc = fc; continue
        if seg and c2:
            key = c2.lower()
            for pref, (metric, unit) in EXTD.items():
                if key.startswith(pref):
                    for y, j in fyc.items():
                        if y in want_years and isinstance(r[j], (int, float)) and r[j] != 0:
                            out[(metric, seg, y)] = (round(float(r[j]), 1), unit)
    return out

# --- Churn from CustomerKPI by Segment_h ---
def parse_churn(fn):
    rows = rows_of(fn, "CustomerKPI by Segment_h")
    out = {}; active = False; fyc = {}
    for r in rows:
        strs = [("" if c is None else str(c).strip()) for c in r]
        fc = {int(re.search(r"\d{4}", s).group()): j
              for j, s in enumerate(strs) if re.fullmatch(r"FY ?\d{4}", s)}
        label = next((s for s in strs if s and not re.match(
            r"(Q\d|1-|H\d|FY ?\d|in |[\d.,\-]+$|Group|Austria|Internat|Bulgaria|"
            r"Croatia|Belarus|Slovenia|Serbia|North|\*)", s)), "")
        if fc:
            active = label.lower().startswith("total churn"); fyc = fc; continue
        if active:
            seg = seg_of(" ".join(s for s in strs[:3] if s))
            if seg:
                for y, j in fyc.items():
                    v = r[j]
                    if isinstance(v, (int, float)) and v != 0:
                        pct = round(float(v) * 100, 2) if abs(v) < 1 else round(float(v), 2)
                        out[("churn_rate", seg, y)] = (pct, "percent")
    return out

def main():
    con = duckdb.connect(DB)
    rows = {}
    note_extd = lambda fn: f"A1 analyst factsheet {fn} [Customer KPIs by Segment_Extd]"
    rows.update({k: (v, note_extd("FS_FY2022.xlsx")) for k, v in parse_extd("FS_FY2022.xlsx", {2020}).items()})
    rows.update({k: (v, note_extd("FS_FY2024.xlsx")) for k, v in parse_extd("FS_FY2024.xlsx", {2021,2022,2023,2024}).items()})
    note_churn = "A1 analyst factsheet FS_FY2025.xlsx [CustomerKPI by Segment_h]"
    rows.update({k: (v, note_churn) for k, v in parse_churn("FS_FY2025.xlsx").items()})

    n = 0
    for (metric, seg, year), ((value, unit), note) in rows.items():
        con.execute("DELETE FROM financials WHERE fiscal_year=? AND metric_name=? AND segment=? "
                    "AND source_year=? AND restated_flag=FALSE", [year, metric, seg, year+1])
        con.execute("INSERT INTO financials (fiscal_year, metric_name, segment, value, unit, "
                    "source_year, source_page, restated_flag, notes) VALUES (?,?,?,?,?,?,?,FALSE,?)",
                    [year, metric, seg, value, unit, year+1, None, note])
        n += 1
    print(f"Inserted/updated {n} operational-KPI rows.")
    for m, lo, hi, c, ns in con.execute(
        "SELECT metric_name, min(fiscal_year), max(fiscal_year), count(*), count(distinct segment) "
        "FROM financials WHERE metric_name IN "
        "('broadband_rgus','mobile_postpaid_subscribers','arpu','arpl','churn_rate') "
        "GROUP BY 1 ORDER BY 1").fetchall():
        print(f"  {m:28} FY{lo}-{hi}  {c} rows, {ns} countries")
    # sanity sample
    print("Austria sample:")
    for m in ("broadband_rgus","mobile_postpaid_subscribers","arpu","arpl","churn_rate"):
        v = con.execute("SELECT fiscal_year,value,unit FROM financials WHERE metric_name=? AND segment='austria' "
                        "ORDER BY fiscal_year", [m]).fetchall()
        print(f"  {m:28} {v}")
    con.close()

if __name__ == "__main__":
    main()
