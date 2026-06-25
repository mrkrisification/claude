# Revenue across years

Cross-year narrative view. **Figures live in `data/financials.duckdb`** (`metric_name='revenue'`).

## The arc
- **1998-2000 (~€3.4-3.9 bn):** Austrian incumbent, reported in ATS then EUR; growth from
  the mobile/internet segments offsetting fixed-voice decline under new competition.
  (`reports/1998`, `reports/1999`, `reports/2000`)
- **2001-2006 (€3.9 → €4.8 bn):** CEE mobile expansion — Slovenia, Croatia, then the
  **MobilTel/Bulgaria** acquisition (2005) — drives the step up. (`reports/2005`, `reports/2006`)
- **2007-2009 (~€4.8-5.2 bn):** Belarus entry lifts revenue to a then-peak €5,170 mn in
  2008. (`reports/2007`, `reports/2008`)
- **2010-2015 (€4.65 → €4.0 bn trough):** a long, gentle decline — regulatory roaming/MTR
  cuts, FX, and competitive pressure across CEE. (`reports/2010`-`reports/2015`)
- **2016-2025 (€4.2 → €5.6 bn):** steady recovery and growth — convergence, 5G/fibre,
  price indexation — to record revenue **€5,577 mn in 2025**. (`reports/2025`)

## Labelling notes
Headline revenue label shifts: "Operating revenues" / "Total managed revenues" (early) →
"Revenues" → "Total revenues (incl. other operating income)" (2022+). Each row records the
reported label in `notes`. The 1998/1999 EUR-million figures are sourced from the FY2000
report's three-year summary (standalone reports were in ATS/EUR-billions).

## Example query
```sql
SELECT fiscal_year, value FROM financials
WHERE metric_name='revenue' AND segment='total' AND restated_flag=FALSE
ORDER BY fiscal_year;
```
