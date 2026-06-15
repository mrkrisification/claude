# HAKOM raw source manifest

Croatian telecom market — quarterly electronic communications market data reports published by HAKOM
(Hrvatska regulatorna agencija za mrežne djelatnosti / Croatian Regulatory Authority for Network Industries).

All reports are whole-market: they report Croatia-wide totals collected from all operators. None of these
reports break out figures per operator (see `../data/README.md`).

| source_id | date | publisher | title | period covered | file |
|-----------|------|-----------|-------|----------------|------|
| R01 | 2022 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — Q3 2022 | Q3 2022 | 2026-06-12-Croatian_20Quarterly_20electronic_20communications_20data_Q32022.eng.pdf |
| R02 | 2023 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — Q4 2022 | Q4 2022 (FY2022 year-end) | 2026-06-12-Croatian_Quarterly_20electronic_20communications_20data_Q42022.eng.pdf |
| R03 | 2023 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — Q1 2023 | Q1 2023 | 2026-06-12-Croatian_20Quarterly_20electronic_20communications_20data_Q12023.eng.pdf |
| R04 | 2023 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — Q2 2023 | Q2 2023 | 2026-06-12-Croatian_20Quarterly_20electronic_20communications_20data_Q22023.eng.pdf |
| R05 | 2023 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — Q3 2023 | Q3 2023 | 2026-06-12-Croatian_20Quarterly_20electronic_20communications_20data_2CQ3_2023.eng.pdf |
| R06 | 2024 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — Q4 2023 | Q4 2023 (FY2023 year-end) | 2026-06-12-Croatian_20Quarterly_20electronic_20communications_20data_Q4_2023.eng.pdf |
| R07 | 2024 (quarterly) | HAKOM | Croatian Quarterly Electronic Communications Market Data — 2nd Quarter 2024 | Q2 2024 | 2026-06-12-Croatian_20quarterly_20electronic_20communications_20market_20data_20for_202.quarter_202024.-ENG.pdf |
| R08 | 2025 (quarterly) | HAKOM | Quarterly Data on the Electronic Communications Market in Croatia — 4th Quarter 2024 (correction) | Q4 2024 (FY2024 year-end) | 2026-06-12-Tromjese_C4_8Dni_20usporedni_20Q4_2024_20-_20eng_correction.pdf |
| R09 | 2026-03-25 | HAKOM | Quarterly Data on the Electronic Communications Market in Croatia — 4th Quarter 2025 | Q4 2025 (FY2025 year-end) | 2026-06-12-Tromjese_C4_8Dni_20uporedni_20podaci_20-_20Q4_2025_20-_20eng.pdf |

Notes:
- Croatia adopted the EUR on 2023-01-01. Reports up to and including Q4 2022 (R01, R02) report money in HRK
  (fixed conversion rate 7.5345 HRK/EUR). From Q1 2023 (R03) onward money is reported in EUR.
- "Period covered" marks which reports are used as year-end (FY) snapshots: R02=FY2022, R06=FY2023,
  R08=FY2024, R09=FY2025.
- The `date` column is the report's reporting/publication timing; only R09 carries an explicit publication
  date on its cover (25 March 2026). Others are approximated to the quarter following the reported period.
