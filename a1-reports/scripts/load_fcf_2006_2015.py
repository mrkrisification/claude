#!/usr/bin/env python3
"""
Back-fill group free_cash_flow for FY2006-FY2015 (the factsheets carry FCF only
from FY2022, so this comes from the report PDFs' key-figures tables).

Consistent "Free cash flow" basis throughout:
- FY2008-FY2015: each year from its own report's key figures (current-year column).
- FY2006-FY2007: taken from the FY2008 report's comparative columns, because the
  FY2006/2007 reports labelled the line "Operating free cash flow" (910.1 / 1,003.6)
  on a slightly different basis; the FY2008 report restates them as "Free cash flow"
  (913.2 / 975.8), matching the 2008+ series.
FY2013 is sharply negative (-716.7) due to the EUR 1.03 bn Austrian spectrum
auction. Pre-2006 FCF was not a featured metric, so the series starts at 2006.
"""
import os
import duckdb

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  "data", "financials.duckdb")

# (fiscal_year, value, source_year, source_page, note)
ROWS = [
    (2006,  913.2, 2009, 3, "Free cash flow basis, from FY2008 report comparative "
                            "(FY2006 report labelled it 'Operating free cash flow' 910.1)"),
    (2007,  975.8, 2009, 3, "Free cash flow basis, from FY2008 report comparative "
                            "(FY2007 report labelled it 'Operating free cash flow' 1,003.6)"),
    (2008,  756.2, 2009, 3, "FY2008 report key figures"),
    (2009,  674.0, 2010, 2, "FY2009 report key figures"),
    (2010,  634.0, 2011, 2, "FY2010 report key figures"),
    (2011,  479.2, 2012, 6, "FY2011 report key figures"),
    (2012,  325.4, 2013, 2, "FY2012 report key figures"),
    (2013, -716.7, 2014, 3, "FY2013 report key figures (negative: EUR 1.03 bn spectrum auction)"),
    (2014,  156.1, 2015, 3, "FY2014 report key figures"),
    (2015,  354.9, 2016, 3, "FY2015 report key figures"),
]

def main():
    con = duckdb.connect(DB)
    for fy, value, src_year, page, note in ROWS:
        con.execute("DELETE FROM financials WHERE fiscal_year=? AND metric_name='free_cash_flow' "
                    "AND segment='total' AND source_year=? AND restated_flag=FALSE", [fy, src_year])
        con.execute("INSERT INTO financials (fiscal_year, metric_name, segment, value, unit, "
                    "source_year, source_page, restated_flag, notes) "
                    "VALUES (?,?,'total',?,?,?,?,FALSE,?)",
                    [fy, "free_cash_flow", value, "EUR_million", src_year, page, note])
    print(f"Loaded {len(ROWS)} FCF rows.")
    full = con.execute("SELECT fiscal_year, value FROM financials WHERE metric_name='free_cash_flow' "
                       "AND segment='total' ORDER BY fiscal_year").fetchall()
    print(f"free_cash_flow now FY{full[0][0]}-{full[-1][0]} ({len(full)} years):")
    print("  " + "  ".join(f"{y}:{v:.0f}" for y, v in full))
    con.close()

if __name__ == "__main__":
    main()
