#!/usr/bin/env python3
"""
Load per-country CAPEX and customer KPIs into data/financials.duckdb, from the
A1 analyst factsheets (factsheets/). Complements scripts/load_segments.py
(revenue + ebitda).

Metrics added (segment = country code; see data/SCHEMA.md):
  - capex             : Capital Expenditures, EUR_million, FY2010-FY2025.
                        2010-2021 from the "Results by Segments" sheet's
                        "Capital Expenditures" block; 2022-2025 from the
                        "CAPEX by Segment_h" sheet. Reconciles to group capex.
  - mobile_subscribers: "Total Mobile Subscribers (in '000)", unit=thousand,
                        FY2021-FY2025 (the per-country customer sheet only
                        exists in the 2022+ factsheets; FS_FY2025 carries
                        FY2021-2025).
  - fixed_rgus        : "Total Fixed RGUs (in '000)", unit=thousand, same span.
                        (Serbia has no fixed business -> #VALUE!/0, skipped.)

Customer KPIs are loaded only where the factsheet states a clean value; blanks
and #VALUE! cells are skipped. Provenance mirrors load_segments.py: source_page
NULL, notes = factsheet file + sheet, source_year = fiscal_year + 1.
"""
import os, re, glob
import duckdb, openpyxl, xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FS   = os.path.join(ROOT, "factsheets")
DB   = os.path.join(ROOT, "data", "financials.duckdb")

CTYKEYS = [("Austria","austria"),("Bulgaria","bulgaria"),("Croatia","croatia"),
           ("Belarus","belarus"),("Slovenia","slovenia"),("Serbia","serbia"),
           ("Macedonia","north_macedonia")]
EXCL = ("group","total","elimination","consolidat","international")

def fs_path(year):
    h = glob.glob(os.path.join(FS, f"FS_FY{year}.xls*"))
    return h[0] if h else None

def rows_of(path, sheet):
    if path.endswith(".xls"):
        wb = xlrd.open_workbook(path); s = wb.sheet_by_name(sheet)
        return [s.row_values(r) for r in range(s.nrows)]
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    return list(wb[sheet].iter_rows(values_only=True))

def names(path):
    return ([s.name for s in xlrd.open_workbook(path).sheets()] if path.endswith(".xls")
            else openpyxl.load_workbook(path, read_only=True).sheetnames)

def fy_cells(strs):
    return {int(re.search(r"\d{4}", s).group()): j
            for j, s in enumerate(strs) if re.fullmatch(r"FY ?\d{4}", s)}

def text_label(strs, fyc):
    fycols = set(fyc.values())                    # fyc is keyed by YEAR -> column index
    for j, s in enumerate(strs):
        if j in fycols:
            continue
        if s and not re.match(r"(Q\d|Q1-|1-|H\d|FY ?\d|in EUR|EUR|in '?000|%|[\d,.\-]+$|#)", s):
            return s
    return ""

def seg_of(label):
    l = label.lower()
    if "corporate" in l or "elimination" in l:
        return "corporate"
    if any(x in l for x in EXCL):
        return None
    for kw, code in CTYKEYS:
        if kw.lower() in l:
            return code
    return None

def num(v):
    if isinstance(v, (int, float)):
        return round(float(v), 1)
    return None

def parse_block(path, sheet, want_year, block_match, allow_label_above=False):
    """Generic: find the metric block whose (same-row or row-above) label matches
    block_match(label)->bool, then read country rows at the want_year FY column."""
    rows = rows_of(path, sheet)
    out = {}
    pending = ""             # last text-only label row (for label-above-periods)
    active = False; fyc = {}
    for r in rows:
        strs = [("" if c is None else str(c).strip()) for c in r]
        fc = fy_cells(strs)
        nonempty = [s for s in strs if s]
        if not fc and len(nonempty) == 1 and not re.match(r"(in |EUR|in '?000)", nonempty[0], re.I):
            pending = nonempty[0]                 # a lone block-title row (skip unit subtitles)
        if len(fc) >= 2:                          # period row -> block boundary
            lbl = text_label(strs, fc)
            cand = lbl if lbl else (pending if allow_label_above else "")
            active = block_match(cand); fyc = fc; continue
        if active and want_year in fyc:
            seg = seg_of(text_label(strs, fyc))
            if seg:
                v = num(r[fyc[want_year]])
                if v is not None:
                    out[seg] = v
    return out

def main():
    con = duckdb.connect(DB)
    gcap = {fy: v for fy, v in con.execute(
        "SELECT fiscal_year, value FROM financials WHERE metric_name='capex' "
        "AND segment='total' AND restated_flag=FALSE").fetchall()}

    def upsert(year, metric, seg, value, unit, src_year, note):
        con.execute("DELETE FROM financials WHERE fiscal_year=? AND metric_name=? "
                    "AND segment=? AND source_year=? AND restated_flag=FALSE",
                    [year, metric, seg, src_year])
        con.execute("INSERT INTO financials (fiscal_year, metric_name, segment, value, "
                    "unit, source_year, source_page, restated_flag, notes) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    [year, metric, seg, value, unit, src_year, None, False, note])

    n = 0
    # ---- CAPEX ----
    print("CAPEX by country:")
    for year in range(2010, 2026):
        if year == 2019:
            path = fs_path(2020)
        elif year <= 2021:
            path = fs_path(year)
        else:
            path = fs_path(year)
        if not path:
            continue
        sheet = "Results by Segments" if year <= 2021 else "CAPEX by Segment_h"
        d = parse_block(path, sheet, year,
                        lambda l: l.strip().lower().startswith("capital ex"),
                        allow_label_above=True)
        src_year = (2020 if year == 2019 else year + 1)
        note = f"A1 analyst factsheet {os.path.basename(path)} [{sheet}]"
        for seg, v in d.items():
            upsert(year, "capex", seg, v, "EUR_million", src_year, note); n += 1
        tot = sum(v for s, v in d.items())
        print(f"  FY{year}: {len(d):2} segs  Σcapex={tot:6.1f}  (group {gcap.get(year)})")

    # ---- Customers (FS_FY2025 carries FY2021-2025) ----
    print("\nCustomer KPIs by country (from FS_FY2025):")
    path = fs_path(2025); sheet = "CustomerKPI by Segment_h"
    note = f"A1 analyst factsheet {os.path.basename(path)} [{sheet}]"
    cust = {"mobile_subscribers": lambda l: l.lower().startswith("total mobile sub"),
            "fixed_rgus":         lambda l: l.lower().startswith("total fixed rgu")}
    for metric, match in cust.items():
        for year in range(2021, 2026):
            d = parse_block(path, sheet, year, match)
            src_year = year + 1
            for seg, v in d.items():
                if v and v > 0:
                    upsert(year, metric, seg, v, "thousand", src_year, note + " (in '000)"); n += 1
            print(f"  {metric:18} FY{year}: {sum(1 for v in d.values() if v and v>0):2} countries")

    print(f"\nInserted/updated {n} rows.")
    print("Segment metric coverage:")
    for m, lo, hi, c in con.execute(
        "SELECT metric_name, min(fiscal_year), max(fiscal_year), count(*) "
        "FROM financials WHERE segment NOT IN ('total') GROUP BY 1 ORDER BY 1").fetchall():
        print(f"  {m:20} FY{lo}-{hi}  {c} rows")
    con.close()

if __name__ == "__main__":
    main()
