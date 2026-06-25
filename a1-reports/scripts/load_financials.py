#!/usr/bin/env python3
"""Seed loader for the A1 Group financials DuckDB store.

Full Revenue + EBITDA timeseries FY1998-FY2025, plus EBITDA after leases
(EBITDAaL) FY2022-FY2025. All figures hand-verified from the headline
key-figures tables of each report in pdfs/. See data/SCHEMA.md for the
table contract.

Conventions (per SCHEMA.md):
- value/unit: raw reported figure in EUR_million, no pre-conversion.
- source_year = the report's PUBLICATION year = fiscal_year + 1 (an annual
  report covering FY-N is published in N+1). "latest known" = max(source_year),
  "originally reported" = restated_flag = FALSE.
- source_page = 1-based page position in that PDF.
- restated_flag = TRUE for prior-year comparison-column values.

EBITDA definition note: A1 / Telekom Austria Group relabelled its headline
EBITDA repeatedly. The exact label each year is recorded in `notes`:
  1998-2000 'EBITDA**'  -> 2001-2002 'Total managed EBITDA'
  2003-2006 'Adjusted EBITDA' -> 2007-2009 'EBITDA'
  2010-2015 'EBITDA comparable' (excl. restructuring/impairment)
  2016-2018 'EBITDA' (pre-IFRS16) -> 2019+ 'EBITDA' (IFRS16 basis)
These are NOT all the same definition; a raw cross-year EBITDA line splices
bases. The two biggest discontinuities are the comparable/reported switch
(2015->2016) and IFRS 16 (2018->2019). IFRS 16 is additionally captured as a
restatement: FY2018 EBITDA 1,380.6 (pre-IFRS16, originally reported) vs
1,548.9 (IFRS16, restated in the FY2019 report). From FY2019 the company also
reports EBITDAaL (= EBITDA - IFRS16 lease depreciation - lease interest),
kept here as a distinct metric.

1998/1999: the standalone reports are in EUR-billions / Austrian Schilling;
the precise EUR-million figures used here come from the FY2000 report's
three-year key-data summary (noted per row).

Idempotent: each row keyed by
(fiscal_year, metric_name, segment, source_year, restated_flag) via
delete-then-insert, so re-running does not duplicate.
"""

import os
import duckdb

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "financials.duckdb")

# (fiscal_year, metric_name, value, source_year, source_page, restated_flag, notes)
ROWS = [
    # ===================== REVENUE (headline, originally reported) =====================
    (1998, "revenue", 3438.3, 2001, 2, False, "from FY2000 report 3-yr summary (EUR mn); standalone 1998 report in ATS/EUR-bn"),
    (1999, "revenue", 3775.9, 2001, 2, False, "from FY2000 report 3-yr summary (EUR mn); standalone 1999 report in ATS/EUR-bn"),
    (2000, "revenue", 3905.3, 2001, 2, False, "reported as 'Operating revenues'"),
    (2001, "revenue", 3943.5, 2002, 14, False, "reported as 'Total managed revenues'"),
    (2002, "revenue", 3908.2, 2003, 1, False, "reported as 'Total managed revenues'"),
    (2003, "revenue", 3969.8, 2004, 2, False, "reported as 'Operating revenues'"),
    (2004, "revenue", 4056.3, 2005, 7, False, "reported as 'Operating revenues'"),
    (2005, "revenue", 4377.3, 2006, 2, False, "reported as 'Revenues'"),
    (2006, "revenue", 4759.6, 2007, 7, False, "reported as 'Revenues'"),
    (2007, "revenue", 4919.0, 2008, 3, False, "reported as 'Operating revenues'"),
    (2008, "revenue", 5170.3, 2009, 9, False, "reported as 'Total revenues'"),
    (2009, "revenue", 4802.0, 2010, 2, False, "reported as 'Operating revenues'"),
    (2010, "revenue", 4650.8, 2011, 2, False, "reported as 'Revenues'"),
    (2011, "revenue", 4454.6, 2012, 6, False, "reported as 'Revenues'"),
    (2012, "revenue", 4329.7, 2013, 2, False, "reported as 'Revenues'"),
    (2013, "revenue", 4183.9, 2014, 3, False, "reported as 'Revenues'"),
    (2014, "revenue", 4018.0, 2015, 3, False, "reported as 'Revenues'"),
    (2015, "revenue", 4026.6, 2016, 3, False, "reported as 'Revenues'"),
    (2016, "revenue", 4211.5, 2017, 2, False, "reported as 'Total revenues'"),
    (2017, "revenue", 4382.5, 2018, 2, False, "reported as 'Total revenues'"),
    (2018, "revenue", 4466.4, 2019, 7, False, "reported as 'Total revenues'"),
    (2019, "revenue", 4565.2, 2020, 8, False, "reported as 'Total revenues'"),
    (2020, "revenue", 4549.4, 2021, 2, False, "reported as 'Total revenues'"),
    (2021, "revenue", 4748.3, 2022, 2, False, "reported as 'Total revenues'"),
    (2022, "revenue", 5005.0, 2023, 2, False, "reported as 'Total revenues (incl. other operating income)'; rounded to whole EUR mn"),
    (2023, "revenue", 5251.0, 2024, 10, False, "rounded to whole EUR mn"),
    (2024, "revenue", 5413.0, 2025, 9, False, "rounded to whole EUR mn; English Annual Financial Report"),
    (2025, "revenue", 5577.0, 2026, 9, False, "rounded to whole EUR mn; English Annual Financial Report"),
    # ---- Revenue restatements (prior-year comparison columns) ----
    (2017, "revenue", 4388.5, 2019, 7, True, "prior-year comparison column in FY2018 report"),
    (2018, "revenue", 4435.4, 2020, 8, True, "prior-year comparison column in FY2019 report (reflects IFRS restatement)"),

    # ===================== EBITDA (headline, originally reported) =====================
    (1998, "ebitda", 1798.8, 2001, 2, False, "reported as 'EBITDA**'; from FY2000 report 3-yr summary"),
    (1999, "ebitda", 1477.9, 2001, 2, False, "reported as 'EBITDA**'; from FY2000 report 3-yr summary"),
    (2000, "ebitda", 1016.5, 2001, 2, False, "reported as 'EBITDA**'"),
    (2001, "ebitda", 1472.8, 2002, 14, False, "reported as 'Total managed EBITDA'"),
    (2002, "ebitda", 1514.8, 2003, 1, False, "reported as 'Total managed EBITDA'"),
    (2003, "ebitda", 1509.8, 2004, 2, False, "reported as 'Adjusted EBITDA'"),
    (2004, "ebitda", 1568.8, 2006, 2, False, "reported as 'Adjusted EBITDA'; from FY2005 report comparative column (FY2004 key-data table not machine-readable)"),
    (2005, "ebitda", 1757.2, 2006, 2, False, "reported as 'Adjusted EBITDA'"),
    (2006, "ebitda", 1906.8, 2007, 3, False, "reported as 'Adjusted EBITDA'"),
    (2007, "ebitda", 1854.9, 2008, 3, False, "reported as 'EBITDA' (incl. restructuring)"),
    (2008, "ebitda", 1295.6, 2009, 3, False, "reported as 'EBITDA'"),
    (2009, "ebitda", 1794.0, 2010, 2, False, "reported as 'EBITDA'"),
    (2010, "ebitda", 1645.9, 2011, 2, False, "reported as 'EBITDA comparable' (excl. restructuring/impairment)"),
    (2011, "ebitda", 1527.3, 2012, 6, False, "reported as 'EBITDA comparable'"),
    (2012, "ebitda", 1455.4, 2013, 2, False, "reported as 'EBITDA comparable'"),
    (2013, "ebitda", 1287.4, 2014, 3, False, "reported as 'EBITDA comparable'"),
    (2014, "ebitda", 1286.1, 2015, 3, False, "reported as 'EBITDA comparable'"),
    (2015, "ebitda", 1372.6, 2016, 3, False, "reported as 'EBITDA comparable'"),
    (2016, "ebitda", 1354.3, 2017, 2, False, "reported as 'EBITDA' (comparable/reported converge; switch from 'EBITDA comparable' label)"),
    (2017, "ebitda", 1397.3, 2018, 2, False, "reported as 'EBITDA'; pre-IFRS16 basis"),
    (2018, "ebitda", 1380.6, 2019, 7, False, "reported as 'EBITDA'; pre-IFRS16 basis"),
    (2019, "ebitda", 1560.6, 2020, 8, False, "reported as 'EBITDA'; IFRS16 basis (IFRS 16 lessee accounting from FY2019)"),
    (2020, "ebitda", 1576.8, 2021, 2, False, "reported as 'EBITDA'; IFRS16 basis"),
    (2021, "ebitda", 1706.1, 2022, 2, False, "reported as 'EBITDA'; IFRS16 basis"),
    (2022, "ebitda", 1838.0, 2023, 2, False, "reported as 'EBITDA'; IFRS16 basis; rounded"),
    (2023, "ebitda", 1924.0, 2024, 10, False, "reported as 'EBITDA'; IFRS16 basis; rounded"),
    (2024, "ebitda", 2021.0, 2025, 9, False, "reported as 'EBITDA'; IFRS16 basis; rounded"),
    (2025, "ebitda", 2062.0, 2026, 9, False, "reported as 'EBITDA'; IFRS16 basis; rounded"),
    # ---- EBITDA restatements (prior-year comparison columns) ----
    (2017, "ebitda", 1398.9, 2019, 7, True, "prior-year comparison column in FY2018 report"),
    (2018, "ebitda", 1548.9, 2020, 8, True, "RESTATED to IFRS16 basis in FY2019 report; originally reported pre-IFRS16 was 1,380.6 (~168 mn lease add-back)"),

    # ===================== EBITDA after leases (FY2019 onward) =====================
    (2023, "ebitda_after_leases", 1671.0, 2024, 14, False, "EBITDAaL = EBITDA - IFRS16 lease depreciation - IFRS16 lease interest"),
    (2024, "ebitda_after_leases", 1603.0, 2025, 9, False, "EBITDAaL"),
    (2025, "ebitda_after_leases", 1632.0, 2026, 9, False, "EBITDAaL"),
    (2022, "ebitda_after_leases", 1657.0, 2024, 14, True, "prior-year comparison column (EBITDAaL) in FY2023 report"),
]


def main():
    con = duckdb.connect(DB_PATH)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS financials (
          fiscal_year INTEGER, metric_name VARCHAR, segment VARCHAR DEFAULT 'total',
          value DOUBLE, unit VARCHAR, source_year INTEGER, source_page INTEGER,
          restated_flag BOOLEAN DEFAULT FALSE, notes VARCHAR
        )
        """
    )
    for fy, metric, value, src_year, src_page, restated, notes in ROWS:
        con.execute(
            """
            DELETE FROM financials
            WHERE fiscal_year = ? AND metric_name = ? AND segment = 'total'
              AND source_year = ? AND restated_flag = ?
            """,
            [fy, metric, src_year, restated],
        )
        con.execute(
            """
            INSERT INTO financials
              (fiscal_year, metric_name, segment, value, unit, source_year, source_page, restated_flag, notes)
            VALUES (?, ?, 'total', ?, 'EUR_million', ?, ?, ?, ?)
            """,
            [fy, metric, value, src_year, src_page, restated, notes],
        )
    total = con.execute("SELECT COUNT(*) FROM financials").fetchone()[0]
    con.close()
    print(f"Upserted {len(ROWS)} rows; table now holds {total} rows.")


if __name__ == "__main__":
    main()
