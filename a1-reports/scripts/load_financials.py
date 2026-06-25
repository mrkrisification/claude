#!/usr/bin/env python3
"""Seed loader for the A1 Group financials DuckDB store.

First KPI load: Revenue, EBITDA, and EBITDA after leases (EBITDAaL) for
FY2017-FY2025, hand-verified from the headline KPI summary tables of each
report in pdfs/. See data/SCHEMA.md for the table contract.

Conventions applied here (per SCHEMA.md):
- value/unit: raw reported figure in EUR_million, no pre-conversion.
- source_year = the report's PUBLICATION year = fiscal_year + 1 (an annual
  report covering FY-N is published in N+1). This makes "latest known" =
  max(source_year) and "originally reported" = restated_flag = FALSE.
- source_page = 1-based page position in that PDF (pdfplumber page index).
- restated_flag = TRUE for prior-year comparison-column values, which is where
  the IFRS 16 EBITDA redefinition shows up (FY2018 EBITDA jumps from the
  pre-IFRS16 1,380.6 originally reported to 1,548.9 when restated in the
  FY2019 report).

EBITDA basis note: through FY2018 EBITDA is pre-IFRS 16; from FY2019 the
headline EBITDA is on the IFRS 16 basis and the company also reports
EBITDAaL (= EBITDA - IFRS16 lease depreciation - IFRS16 lease interest),
which is the figure comparable to the old pre-IFRS16 EBITDA. Those are kept
as two distinct metrics so cross-year queries never silently mix bases.

Idempotent: each row is keyed by
(fiscal_year, metric_name, segment, source_year, restated_flag) and
re-inserted (delete-then-insert), so re-running does not duplicate.
"""

import os
import duckdb

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "financials.duckdb")

# (fiscal_year, metric_name, value, source_year, source_page, restated_flag, notes)
ROWS = [
    # ---- Total revenue (originally reported) ----
    (2017, "revenue", 4382.5, 2018, 2, False, ""),
    (2018, "revenue", 4466.4, 2019, 7, False, ""),
    (2019, "revenue", 4565.2, 2020, 8, False, ""),
    (2020, "revenue", 4549.4, 2021, 2, False, ""),
    (2021, "revenue", 4748.3, 2022, 2, False, ""),
    (2022, "revenue", 5005.0, 2023, 2, False, "reported as 'Total revenues (incl. other operating income)'; rounded to whole EUR mn"),
    (2023, "revenue", 5251.0, 2024, 10, False, "rounded to whole EUR mn"),
    (2024, "revenue", 5413.0, 2025, 9, False, "rounded to whole EUR mn; English Annual Financial Report"),
    (2025, "revenue", 5577.0, 2026, 9, False, "rounded to whole EUR mn; English Annual Financial Report"),
    # ---- Total revenue (restatements: prior-year comparison columns) ----
    (2017, "revenue", 4388.5, 2019, 7, True, "prior-year comparison column in FY2018 report"),
    (2018, "revenue", 4435.4, 2020, 8, True, "prior-year comparison column in FY2019 report (reflects IFRS restatement)"),

    # ---- EBITDA (headline, originally reported) ----
    (2017, "ebitda", 1397.3, 2018, 2, False, "pre-IFRS16 basis"),
    (2018, "ebitda", 1380.6, 2019, 7, False, "pre-IFRS16 basis"),
    (2019, "ebitda", 1560.6, 2020, 8, False, "IFRS16 basis (IFRS 16 lessee accounting from FY2019)"),
    (2020, "ebitda", 1576.8, 2021, 2, False, "IFRS16 basis"),
    (2021, "ebitda", 1706.1, 2022, 2, False, "IFRS16 basis"),
    (2022, "ebitda", 1838.0, 2023, 2, False, "IFRS16 basis; rounded to whole EUR mn"),
    (2023, "ebitda", 1924.0, 2024, 10, False, "IFRS16 basis; rounded"),
    (2024, "ebitda", 2021.0, 2025, 9, False, "IFRS16 basis; rounded"),
    (2025, "ebitda", 2062.0, 2026, 9, False, "IFRS16 basis; rounded"),
    # ---- EBITDA (restatements: prior-year comparison columns) ----
    (2017, "ebitda", 1398.9, 2019, 7, True, "prior-year comparison column in FY2018 report"),
    (2018, "ebitda", 1548.9, 2020, 8, True, "RESTATED to IFRS16 basis in FY2019 report; originally reported pre-IFRS16 was 1,380.6 (~168 mn lease add-back)"),

    # ---- EBITDA after leases (EBITDAaL; reported from FY2019 onward) ----
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
    inserted = 0
    for fy, metric, value, src_year, src_page, restated, notes in ROWS:
        # idempotent upsert on the natural key
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
        inserted += 1
    total = con.execute("SELECT COUNT(*) FROM financials").fetchone()[0]
    con.close()
    print(f"Upserted {inserted} rows; table now holds {total} rows.")


if __name__ == "__main__":
    main()
