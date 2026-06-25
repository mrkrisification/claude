# A1 Group Annual Reports — Index

The map of this knowledge base. **Agents: read this first, then navigate to the
specific file you need.** Do not read every file; pick the right one.

## How to use this index

- Need a **number** (revenue, EBITDA, headcount, ...)? → go to `data/financials.duckdb`
  (see `data/SCHEMA.md`), not the prose below.
- Need **what management said / why / strategy / risk**? → open the relevant
  `reports/<year>/` file below.
- Tracking **one metric across many years**? → see `metrics/` (these summarise the
  cross-year story; underlying figures still live in DuckDB).

## Reports

> Update this table as each report is ingested. Status: ⬜ not started · 🟡 partial · ✅ done

| Fiscal Year | Report PDF        | Markdown            | Wiki notes              | DuckDB | Status |
|-------------|-------------------|---------------------|-------------------------|--------|--------|
| FY1998      | pdfs/1998.pdf     | markdown/1998.md    | reports/1998/           | ⬜     | ⬜     |
| ...         | ...               | ...                 | ...                     | ⬜     | ⬜     |
| FY2024      | pdfs/2024.pdf     | markdown/2024.md    | reports/2024/           | ⬜     | ⬜     |

## Cross-year metric views

| Metric            | File                      | Notes                          |
|-------------------|---------------------------|--------------------------------|
| Revenue           | metrics/revenue.md        | total + by segment if reported |
| EBITDA / margin   | metrics/ebitda.md         |                                |
| Employees         | metrics/employees.md      | headcount basis may change     |
| Capex             | metrics/capex.md          |                                |

## Known structural notes about A1's reports

- Reporting entity / brand naming has changed over the years — record the entity name
  as reported each year in that report's overview.
- Segment definitions are not stable across decades; note breaks when you spot them.
- Older (1998-era) PDFs may be scans → expect OCR, lower table-extraction confidence.
