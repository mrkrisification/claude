#!/usr/bin/env python3
"""
Backfill FY2007-FY2009 per-country data from the legacy "Mobile Communication"
sheet in the 2007-2009 analyst factsheets.

IMPORTANT — different basis. Before FY2010 the group reported by *function*
(Wireline / Mobile Communication), not by country. The only per-country split
available is therefore the **Mobile Communication segment, by operator** — i.e.
mobile-only, excluding the (Austria-dominated) fixed-line business. To avoid
silently corrupting the FY2010+ total-operations `revenue`/`ebitda` series, these
are loaded under distinct metric names:

  - mobile_revenue : mobile-segment revenue per country, EUR_million
  - mobile_ebitda  : mobile-segment EBITDA per country,  EUR_million

Operator -> country: mobilkom austria=austria, Mobiltel=bulgaria, Velcom=belarus,
Vipnet=croatia, Si.mobil=slovenia, Vip mobile=serbia, Vip operator=north_macedonia.
(Liechtenstein and "Other companies"/eliminations are not loaded.)

Provenance: source_page NULL, notes = factsheet file + sheet, source_year = year+1.
Velcom (Belarus) was acquired late 2007, so FY2007 reflects a partial year.
"""
import os, re, glob
import duckdb, xlrd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FS   = os.path.join(ROOT, "factsheets")
DB   = os.path.join(ROOT, "data", "financials.duckdb")
SHEET = "Mobile Communication"

OP2CTY = [("mobilkom aus","austria"), ("mobiltel","bulgaria"), ("velcom","belarus"),
          ("vipnet","croatia"), ("si.mobil","slovenia"), ("vip mobile","serbia"),
          ("vip operator","north_macedonia")]

def op_country(label):
    l = label.lower()
    for key, code in OP2CTY:
        if l.startswith(key):
            return code
    return None

def annual_col(rows, year):
    for r in rows[:8]:
        for j, c in enumerate(r):
            s = str(c).strip()
            if re.fullmatch(rf"{year}\*?(\.0)?", s):
                return j
    return None

def parse(path, year):
    """Return {'mobile_revenue': {cty:val}, 'mobile_ebitda': {cty:val}}.

    The sheet has several operator blocks (revenue, other-operating-income,
    EBITDA, then subscriber/ARPU sections). We capture operators only in the
    revenue and EBITDA blocks; each block is terminated by its 'Mobile
    Communication' total row, after which mode -> skip until the next header.
    """
    wb = xlrd.open_workbook(path); s = wb.sheet_by_name(SHEET)
    rows = [s.row_values(r) for r in range(s.nrows)]
    col = annual_col(rows, year)
    if col is None:
        return {}, None
    out = {"mobile_revenue": {}, "mobile_ebitda": {}}
    mode = "revenue"                       # first operator block is revenue
    for r in rows:
        c0 = str(r[0]).strip().lower()
        c1 = str(r[1]).strip()
        if c0.startswith("other operat"):       # other-operating-income block
            mode = "skip"
        elif c0 == "ebitda":
            mode = "ebitda"
        cty = op_country(c1)
        if cty and mode in ("revenue", "ebitda"):
            v = r[col]
            if isinstance(v, (int, float)):
                out[f"mobile_{mode}"][cty] = round(float(v), 1)
        elif (c1.lower().startswith("mobile commu") and mode in ("revenue", "ebitda")
              and out[f"mobile_{mode}"]):
            mode = "skip"                        # total row ends the operator block
            #                                      (only once the block has captured operators —
            #                                       avoids tripping on the sheet's title row)
    return out, col

def main():
    con = duckdb.connect(DB)
    n = 0
    # Read each FY from a factsheet with a complete, well-structured layout:
    # FY2007 lives as the "2007*" comparison column in the FY2008 factsheet
    # (the FY2007 file's mobile sheet is incomplete — missing Velcom/Vipnet).
    src = {2007: "FS_FY2008.xls", 2008: "FS_FY2009.xls", 2009: "FS_FY2009.xls"}
    for year in (2007, 2008, 2009):
        path = os.path.join(FS, src[year])
        if not os.path.exists(path):
            print(f"FY{year}: factsheet missing"); continue
        parsed, col = parse(path, year)
        note = f"A1 analyst factsheet {os.path.basename(path)} [{SHEET}] (mobile segment, by operator)"
        for metric, d in parsed.items():
            for cty, v in d.items():
                con.execute("DELETE FROM financials WHERE fiscal_year=? AND metric_name=? "
                            "AND segment=? AND source_year=? AND restated_flag=FALSE",
                            [year, metric, cty, year+1])
                con.execute("INSERT INTO financials (fiscal_year, metric_name, segment, value, "
                            "unit, source_year, source_page, restated_flag, notes) "
                            "VALUES (?,?,?,?,?,?,?,?,?)",
                            [year, metric, cty, v, "EUR_million", year+1, None, False, note])
                n += 1
        rev = sum(parsed["mobile_revenue"].values())
        eb  = sum(parsed["mobile_ebitda"].values())
        print(f"  FY{year} (col {col}): {len(parsed['mobile_revenue'])} ctry "
              f"| Σmobile_rev={rev:7.1f} | Σmobile_ebitda={eb:6.1f}")
    print(f"\nInserted/updated {n} rows.")
    con.close()

if __name__ == "__main__":
    main()
