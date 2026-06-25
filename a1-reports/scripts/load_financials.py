#!/usr/bin/env python3
"""Seed loader for the A1 Group financials DuckDB store.

Revenue, EBITDA and EBITDAaL timeseries plus a broader financial KPI set:
ebit, net_income, capex, free_cash_flow, employees, net_debt and
ebitda_excl_restructuring. All figures hand-verified from the headline
key-figures tables of each report in pdfs/. See data/SCHEMA.md for the
table contract.

Coverage / known interior gaps (data not present in the reports' key tables):
- revenue, ebitda: FY1998-FY2025 (full)
- net_income: FY2000-FY2025;  capex: FY1999-FY2025
- ebit: FY2003-FY2025
- ebitda_excl_restructuring: FY2003-06, FY2010-15, FY2017-25 (gaps 2007-09, 2016;
  those years featured only the plain/reported EBITDA)
- net_debt: FY2010-13, FY2015-25 (gap 2014); excl-leases basis from FY2019
- employees: FY1999-2017, FY2019-25 (gap 2018); unit = count, basis shifts
  (yearly-average 1999/2000 -> year-end 2002+ -> FTE ~2009+)
- free_cash_flow: FY2016-FY2025 (absolute; pre-2016 only FCF/share was reported)
Some figures are read from a later report's prior-year comparative column where
the year's own report did not print the value cleanly; this is stated per row in
`notes` and reflected in source_year.

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

    # ===================== EBIT (operating income / EBIT) =====================
    # label: 'Operating income' (2003-2018) -> 'EBIT' (2019+). Volatile years are
    # impairment-driven (2011, 2014 near zero/negative). Pre-2003 omitted (group
    # vs segment figures ambiguous in the early reports).
    (2003, "ebit", 369.8, 2004, 2, False, "reported as 'Operating income'"),
    (2004, "ebit", 452.7, 2006, 2, False, "reported as 'Operating income'; from FY2005 report comparative column"),
    (2005, "ebit", 620.0, 2006, 2, False, "reported as 'Operating income'"),
    (2006, "ebit", 772.4, 2007, 3, False, "reported as 'Operating income'"),
    (2007, "ebit", 761.4, 2008, 3, False, "reported as 'Operating income'"),
    (2008, "ebit", 135.5, 2009, 3, False, "reported as 'Operating income'"),
    (2009, "ebit", 343.9, 2011, 2, False, "reported as 'Operating income'; from FY2010 report comparative column"),
    (2010, "ebit", 437.9, 2011, 2, False, "reported as 'Operating income'"),
    (2011, "ebit", -7.6, 2012, 6, False, "reported as 'Operating income'; impairment-driven"),
    (2012, "ebit", 456.8, 2013, 2, False, "reported as 'Operating income'"),
    (2013, "ebit", 377.6, 2014, 3, False, "reported as 'Operating income'"),
    (2014, "ebit", -3.0, 2015, 3, False, "reported as 'Operating income'; impairment-driven"),
    (2015, "ebit", 574.0, 2016, 3, False, "reported as 'Operating income'"),
    (2016, "ebit", 486.7, 2017, 2, False, "reported as 'Operating income'"),
    (2017, "ebit", 443.9, 2018, 2, False, "reported as 'Operating income'"),
    (2018, "ebit", 424.1, 2019, 7, False, "reported as 'Operating income'; pre-IFRS16"),
    (2019, "ebit", 614.8, 2020, 8, False, "label switches to 'EBIT'; IFRS16 basis"),
    (2020, "ebit", 638.9, 2021, 2, False, "reported as 'Operating income'; IFRS16"),
    (2021, "ebit", 753.4, 2022, 2, False, "reported as 'Operating income'; IFRS16"),
    (2022, "ebit", 871.0, 2023, 2, False, "reported as 'EBIT'; IFRS16; rounded"),
    (2023, "ebit", 911.0, 2024, 10, False, "reported as 'EBIT'; rounded"),
    (2024, "ebit", 861.0, 2025, 9, False, "reported as 'EBIT'; rounded"),
    (2025, "ebit", 852.0, 2026, 9, False, "reported as 'EBIT'; rounded"),

    # ===================== Net income (Net result) =====================
    (2000, "net_income", -285.6, 2003, 1, False, "reported as 'Net income (loss)'; from FY2002 report 3-yr column"),
    (2001, "net_income", -104.6, 2003, 1, False, "reported as 'Net income (loss)'; from FY2002 report comparative column"),
    (2002, "net_income", 12.8, 2003, 1, False, "reported as 'Net income (loss)'"),
    (2003, "net_income", 134.2, 2004, 2, False, "reported as 'Net income (loss)'"),
    (2004, "net_income", 227.3, 2006, 2, False, "reported as 'Net income'; from FY2005 report comparative column"),
    (2005, "net_income", 417.1, 2006, 2, False, "reported as 'Net income'"),
    (2006, "net_income", 561.8, 2007, 3, False, "reported as 'Net income'"),
    (2007, "net_income", 492.5, 2009, 3, False, "reported as 'Net income'; from FY2008 report comparative column"),
    (2008, "net_income", -48.8, 2009, 3, False, "reported as 'Net income/loss'"),
    (2009, "net_income", 94.9, 2010, 2, False, "reported as 'Net income/loss'"),
    (2010, "net_income", 195.2, 2011, 2, False, "reported as 'Net income/loss'"),
    (2011, "net_income", -252.8, 2012, 6, False, "reported as 'Net result'"),
    (2012, "net_income", 103.8, 2013, 2, False, "reported as 'Net result'"),
    (2013, "net_income", 109.7, 2014, 3, False, "reported as 'Net result'"),
    (2014, "net_income", -185.4, 2015, 3, False, "reported as 'net result'"),
    (2015, "net_income", 392.8, 2016, 3, False, "reported as 'Net result'"),
    (2016, "net_income", 413.2, 2017, 2, False, "reported as 'Net result'"),
    (2017, "net_income", 345.5, 2018, 2, False, "reported as 'Net result'"),
    (2018, "net_income", 242.7, 2019, 7, False, "reported as 'Net result'"),
    (2019, "net_income", 327.4, 2020, 8, False, "reported as 'Net result'"),
    (2020, "net_income", 388.8, 2021, 2, False, "reported as 'Net result'"),
    (2021, "net_income", 455.0, 2022, 2, False, "reported as 'Net result'"),
    (2022, "net_income", 635.0, 2023, 2, False, "reported as 'Net result'; rounded"),
    (2023, "net_income", 646.0, 2024, 10, False, "reported as 'Net result'; rounded"),
    (2024, "net_income", 627.0, 2025, 9, False, "reported as 'Net result'; rounded"),
    (2025, "net_income", 613.0, 2026, 9, False, "reported as 'Net result'; rounded"),

    # ===================== Capex (additions to PP&E / Capital expenditures) =====================
    (1999, "capex", 983.2, 2001, 10, False, "reported as 'Additions to PP&E'; from FY2000 report comparative column"),
    (2000, "capex", 917.7, 2001, 10, False, "reported as 'Additions to property, plant and equipment'"),
    (2001, "capex", 812.2, 2004, 2, False, "from FY2003 report comparative column"),
    (2002, "capex", 662.4, 2004, 2, False, "from FY2003 report comparative column"),
    (2003, "capex", 595.3, 2004, 2, False, "reported as 'Additions to property, plant and equipment'"),
    (2004, "capex", 548.2, 2005, 3, False, "reported as 'Capital expenditures'"),
    (2005, "capex", 627.6, 2007, 3, False, "from FY2006 report comparative column"),
    (2006, "capex", 996.7, 2007, 3, False, "reported as 'Capital expenditures'"),
    (2007, "capex", 851.3, 2008, 3, False, "reported as 'Capital expenditures'"),
    (2008, "capex", 807.6, 2011, 2, False, "from FY2010 report comparative column"),
    (2009, "capex", 711.4, 2011, 2, False, "from FY2010 report comparative column"),
    (2010, "capex", 763.6, 2011, 2, False, "reported as 'Capital expenditures'"),
    (2011, "capex", 739.0, 2012, 6, False, "reported as 'Capital expenditures'"),
    (2012, "capex", 728.2, 2013, 2, False, "reported as 'Capital expenditures'"),
    (2013, "capex", 1779.1, 2014, 3, False, "reported as 'Capital expenditures'; spike (spectrum / long-term IRU capitalisation)"),
    (2014, "capex", 757.4, 2015, 3, False, "reported as 'Capital expenditures'"),
    (2015, "capex", 780.0, 2016, 3, False, "reported as 'Capital expenditures'"),
    (2016, "capex", 764.1, 2017, 2, False, "reported as 'Capital expenditures'"),
    (2017, "capex", 736.9, 2018, 2, False, "reported as 'Capital expenditures'"),
    (2018, "capex", 771.0, 2019, 7, False, "reported as 'Capital expenditures'"),
    (2019, "capex", 879.8, 2020, 8, False, "reported as 'Capital expenditures'"),
    (2020, "capex", 651.4, 2021, 2, False, "reported as 'Capital expenditures'"),
    (2021, "capex", 891.5, 2022, 2, False, "reported as 'Capital expenditures'"),
    (2022, "capex", 944.0, 2023, 2, False, "reported as 'Capital expenditures'; rounded"),
    (2023, "capex", 1093.0, 2024, 10, False, "reported as 'Capital expenditures'; rounded"),
    (2024, "capex", 865.0, 2025, 9, False, "reported as 'Capital expenditures'; rounded"),
    (2025, "capex", 889.0, 2026, 9, False, "reported as 'Capital expenditures'; rounded"),

    # ===================== Free cash flow (absolute; pre-2016 only FCF/share reported) =====================
    (2016, "free_cash_flow", 232.0, 2018, 2, False, "from FY2017 report comparative column"),
    (2017, "free_cash_flow", 384.7, 2018, 2, False, "reported as 'Free cash flow'"),
    (2018, "free_cash_flow", 384.2, 2020, 12, False, "from FY2019 report comparative column"),
    (2019, "free_cash_flow", 340.6, 2020, 12, False, "reported as 'Free cash flow'"),
    (2020, "free_cash_flow", 503.7, 2021, 2, False, "reported as 'Free cash flow'"),
    (2021, "free_cash_flow", 487.3, 2022, 2, False, "reported as 'Free cash flow'"),
    (2022, "free_cash_flow", 603.0, 2023, 2, False, "reported as 'Free cash flow'; rounded"),
    (2023, "free_cash_flow", 354.0, 2024, 10, False, "reported as 'Free cash flow'; rounded"),
    (2024, "free_cash_flow", 575.0, 2025, 9, False, "reported as 'Free cash flow'; rounded"),
    (2025, "free_cash_flow", 596.0, 2026, 9, False, "reported as 'Free cash flow'; rounded"),

    # ===================== Employees (unit=count; basis shifts; gap 2018) =====================
    (1999, "employees", 18650, 2000, 3, False, "full-time employees, yearly-average basis"),
    (2000, "employees", 18560, 2001, 2, False, "yearly-average basis"),
    (2001, "employees", 16586, 2003, 1, False, "year-end basis; from FY2002 report comparative column"),
    (2002, "employees", 14951, 2003, 1, False, "year-end basis"),
    (2003, "employees", 13890, 2004, 2, False, "year-end basis"),
    (2004, "employees", 13307, 2007, 3, False, "year-end basis; from FY2006 report comparative column"),
    (2005, "employees", 15595, 2007, 3, False, "year-end basis; from FY2006 report comparative column"),
    (2006, "employees", 15428, 2007, 3, False, "year-end basis"),
    (2007, "employees", 17628, 2008, 3, False, "year-end basis"),
    (2008, "employees", 16954, 2009, 3, False, "year-end basis"),
    (2009, "employees", 16573, 2010, 2, False, "FTE, year-end"),
    (2010, "employees", 16501, 2011, 2, False, "FTE, as of 31 Dec"),
    (2011, "employees", 17217, 2012, 6, False, "FTE, as of 31 Dec"),
    (2012, "employees", 16446, 2013, 2, False, "FTE, as of 31 Dec"),
    (2013, "employees", 16045, 2014, 3, False, "FTE, as of 31 Dec"),
    (2014, "employees", 16240, 2015, 3, False, "FTE, as of 31 Dec"),
    (2015, "employees", 17673, 2016, 3, False, "FTE, as of 31 Dec"),
    (2016, "employees", 18203, 2017, 2, False, "FTE, as of 31 Dec"),
    (2017, "employees", 18957, 2018, 2, False, "FTE, as of 31 Dec"),
    (2019, "employees", 18344, 2021, 2, False, "FTE; from FY2020 report comparative column"),
    (2020, "employees", 17949, 2021, 2, False, "FTE, as of 31 Dec"),
    (2021, "employees", 17856, 2022, 2, False, "FTE, as of 31 Dec"),
    (2022, "employees", 17906, 2023, 2, False, "FTE"),
    (2023, "employees", 17508, 2024, 10, False, "FTE, at year-end"),
    (2024, "employees", 17298, 2025, 9, False, "FTE"),
    (2025, "employees", 16628, 2026, 9, False, "FTE"),

    # ===================== Net debt (excl-leases basis from FY2019; gap 2014) =====================
    (2010, "net_debt", 3305.2, 2011, 2, False, "reported as 'Net debt'"),
    (2011, "net_debt", 3380.3, 2012, 6, False, "reported as 'Net debt'"),
    (2012, "net_debt", 3248.9, 2013, 2, False, "reported as 'Net debt'"),
    (2013, "net_debt", 3695.8, 2014, 3, False, "reported as 'Net debt'"),
    (2015, "net_debt", 2483.0, 2017, 2, False, "from FY2016 report comparative column"),
    (2016, "net_debt", 2339.4, 2017, 2, False, "reported as 'Net debt'"),
    (2017, "net_debt", 2331.8, 2018, 2, False, "reported as 'Net debt'"),
    (2018, "net_debt", 2718.4, 2019, 7, False, "reported as 'Net debt'; pre-IFRS16 (reported IAS 18)"),
    (2019, "net_debt", 2522.3, 2020, 12, False, "net debt excl. leases (IFRS16 basis); incl-leases was 3,463.1"),
    (2020, "net_debt", 2331.9, 2021, 2, False, "net debt excl. leases"),
    (2021, "net_debt", 2064.9, 2022, 2, False, "net debt excl. leases"),
    (2022, "net_debt", 1719.0, 2023, 11, False, "net debt excl. leases; incl-leases was 2,400; rounded"),
    (2023, "net_debt", 639.0, 2025, 11, False, "net debt excl. leases; from FY2024 report comparative column; rounded"),
    (2024, "net_debt", 357.0, 2025, 11, False, "net debt excl. leases; definition changed Q4-2024 (now incl. short-term investments); rounded"),
    (2025, "net_debt", 74.0, 2026, 11, False, "net debt excl. leases (incl. short-term investments per Q4-2024 def change); rounded"),

    # ===================== EBITDA excl. restructuring =====================
    # 'Adjusted EBITDA' (03-06) / 'EBITDA comparable' (10-15) / 'EBITDA (excl/before)
    # restructuring' (17-25). Gaps 2007-09 and 2016: only plain EBITDA was featured.
    (2003, "ebitda_excl_restructuring", 1509.8, 2004, 2, False, "reported as 'Adjusted EBITDA'"),
    (2004, "ebitda_excl_restructuring", 1568.8, 2006, 2, False, "reported as 'Adjusted EBITDA'; from FY2005 report comparative column"),
    (2005, "ebitda_excl_restructuring", 1757.2, 2006, 2, False, "reported as 'Adjusted EBITDA'"),
    (2006, "ebitda_excl_restructuring", 1906.8, 2007, 3, False, "reported as 'Adjusted EBITDA'"),
    (2010, "ebitda_excl_restructuring", 1645.9, 2011, 2, False, "reported as 'EBITDA comparable'"),
    (2011, "ebitda_excl_restructuring", 1527.3, 2012, 6, False, "reported as 'EBITDA comparable'"),
    (2012, "ebitda_excl_restructuring", 1455.4, 2013, 2, False, "reported as 'EBITDA comparable'"),
    (2013, "ebitda_excl_restructuring", 1287.4, 2014, 3, False, "reported as 'EBITDA comparable'"),
    (2014, "ebitda_excl_restructuring", 1286.1, 2015, 3, False, "reported as 'EBITDA comparable'"),
    (2015, "ebitda_excl_restructuring", 1372.6, 2016, 3, False, "reported as 'EBITDA comparable'"),
    (2017, "ebitda_excl_restructuring", 1380.7, 2019, 7, False, "reported as 'EBITDA excl. restructuring'; from FY2018 report comparative column"),
    (2018, "ebitda_excl_restructuring", 1402.7, 2019, 7, False, "reported as 'EBITDA excl. restructuring'; pre-IFRS16"),
    (2019, "ebitda_excl_restructuring", 1644.7, 2020, 8, False, "reported as 'EBITDA excl. restructuring'; IFRS16"),
    (2020, "ebitda_excl_restructuring", 1661.3, 2021, 2, False, "reported as 'EBITDA before restructuring'"),
    (2021, "ebitda_excl_restructuring", 1790.3, 2022, 2, False, "reported as 'EBITDA before restructuring'"),
    (2022, "ebitda_excl_restructuring", 1911.0, 2023, 12, False, "reported as 'EBITDA before Restructuring'; rounded"),
    (2023, "ebitda_excl_restructuring", 2009.0, 2024, 15, False, "reported as 'EBITDA before restructuring'; rounded"),
    (2024, "ebitda_excl_restructuring", 2110.0, 2025, 13, False, "reported as 'EBITDA before restructuring'; rounded"),
    (2025, "ebitda_excl_restructuring", 2158.0, 2026, 13, False, "reported as 'EBITDA before restructuring'; rounded"),
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
        unit = "count" if metric == "employees" else "EUR_million"
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
            VALUES (?, ?, 'total', ?, ?, ?, ?, ?, ?)
            """,
            [fy, metric, value, unit, src_year, src_page, restated, notes],
        )
    total = con.execute("SELECT COUNT(*) FROM financials").fetchone()[0]
    con.close()
    print(f"Upserted {len(ROWS)} rows; table now holds {total} rows.")


if __name__ == "__main__":
    main()
