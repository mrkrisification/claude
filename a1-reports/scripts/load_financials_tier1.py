#!/usr/bin/env python3
"""
Tier-1 group-metric back-fills (additive to scripts/load_financials.py).

Sourced from the analyst factsheets' balance-sheet / segment history sheets,
which are clean and machine-readable. Provenance: source_page NULL, notes records
the factsheet file + sheet; source_year = fiscal_year + 1 (publication).

Loaded here:
  - total_assets (EUR_million), FY2020-FY2025  [factsheet BS_h; in EUR million]
  - equity       (EUR_million), FY2020-FY2025  [factsheet BS_h, "Total stockholders' equity"]
  - ebitda_after_leases (EUR_million), FY2019-FY2021  [factsheet "Results by Segments"
    EBITDAaL group total; extends the existing FY2022-2025 series back to the
    IFRS 16 transition. Cross-check: group EBITDA - lease component, e.g. 2021
    1,706.1 - 175.2 = 1,530.9.]

Balance-sheet history exists in the factsheets only from FY2020 (older factsheets
carry no balance sheet). FY1998-FY2019 total_assets/equity remain to be sourced
from the report PDFs (a later wave) — equity in particular needs care, as the
consolidated balance-sheet tables are EUR-thousand and easy to misread.
"""
import os
import duckdb

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  "data", "financials.duckdb")

# (fiscal_year, metric, value, source_year, note)
F22 = "A1 analyst factsheet FS_FY2022.xlsx [BS_h]"
F25 = "A1 analyst factsheet FS_FY2025.xlsx [BS_h]"
F20 = "A1 analyst factsheet FS_FY2020.xlsx [Results by Segments]"
F21 = "A1 analyst factsheet FS_FY2021.xlsx [Results by Segments]"

ROWS = [
    # total_assets (EUR million)
    (2020, "total_assets", 8212.0,  2021, F22),
    (2021, "total_assets", 8572.6,  2022, F22),
    (2022, "total_assets", 8345.3,  2023, F25),
    (2023, "total_assets", 9556.6,  2024, F25),
    (2024, "total_assets", 9853.9,  2025, F25),
    (2025, "total_assets", 10228.2, 2026, F25),
    # equity (EUR million)
    (2020, "equity", 2793.8, 2021, F22),
    (2021, "equity", 3115.4, 2022, F22),
    (2022, "equity", 3592.6, 2023, F25),
    (2023, "equity", 4600.6, 2024, F25),
    (2024, "equity", 4988.5, 2025, F25),
    (2025, "equity", 5353.4, 2026, F25),
    # ebitda_after_leases (EUR million) — extend FY2022-25 back to IFRS 16 start
    (2019, "ebitda_after_leases", 1382.8, 2020, F20),
    (2020, "ebitda_after_leases", 1398.4, 2021, F20),
    (2021, "ebitda_after_leases", 1530.9, 2022, F21),
]

def main():
    con = duckdb.connect(DB)
    for fy, metric, value, src_year, note in ROWS:
        con.execute("DELETE FROM financials WHERE fiscal_year=? AND metric_name=? "
                    "AND segment='total' AND source_year=? AND restated_flag=FALSE",
                    [fy, metric, src_year])
        con.execute("INSERT INTO financials (fiscal_year, metric_name, segment, value, "
                    "unit, source_year, source_page, restated_flag, notes) "
                    "VALUES (?,?,'total',?,?,?,?,FALSE,?)",
                    [fy, metric, value, "EUR_million", src_year, None, note])
    print(f"Loaded {len(ROWS)} Tier-1 rows.")
    for m in ("total_assets", "equity", "ebitda_after_leases"):
        rows = con.execute("SELECT fiscal_year, value FROM financials WHERE metric_name=? "
                           "AND segment='total' ORDER BY fiscal_year", [m]).fetchall()
        span = f"FY{rows[0][0]}-{rows[-1][0]}" if rows else "(none)"
        print(f"  {m:20} {span}  n={len(rows)}")
    con.close()

if __name__ == "__main__":
    main()
