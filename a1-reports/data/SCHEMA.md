# DuckDB Schema — `data/financials.duckdb`

Design principle: **long/tidy format**, not one-column-per-year. This makes
cross-year queries trivial and survives the fact that A1's report layouts change
over 25 years. One row = one reported figure.

## Table: `financials`

| Column          | Type      | Notes                                                       |
|-----------------|-----------|-------------------------------------------------------------|
| fiscal_year     | INTEGER   | The year the figure *describes* (not publication year).     |
| metric_name     | VARCHAR   | Canonical snake_case name, e.g. `revenue`, `ebitda`.        |
| segment         | VARCHAR   | `total`, or a segment label as reported. Default `total`.   |
| value           | DOUBLE    | The number, in `unit`. No pre-conversion.                   |
| unit            | VARCHAR   | e.g. `EUR_million`, `count`, `percent`.                     |
| source_year     | INTEGER   | Publication year of the report this value was taken from.   |
| source_page     | INTEGER   | Page in that PDF. Provenance is mandatory.                  |
| restated_flag   | BOOLEAN   | TRUE if this is a restated/comparison-column value.         |
| notes           | VARCHAR   | Anything odd: definition change, footnote, OCR uncertainty. |

### Canonical metric names

Keep this list authoritative; add to it rather than inventing synonyms.
`revenue`, `ebitda`, `ebit`, `net_income`, `capex`, `free_cash_flow`,
`total_assets`, `net_debt`, `equity`, `employees`, `ebitda_margin`.

If a report uses a different label, map it to the canonical name and record the
original wording in `notes`.

## Why `restated_flag` matters

A figure for FY2010 may appear in the 2011 report (as a prior-year comparison) with a
different value than the 2010 report originally printed. Both are true facts about what
was *reported*. Store both rows; never overwrite. A query for "the originally reported
2010 revenue" filters `restated_flag = FALSE AND source_year = fiscal_year + 1`-ish logic;
"latest known" takes the most recent `source_year`. Keeping both is the whole point.

## Example queries

```sql
-- Revenue trend, originally-reported figures only
SELECT fiscal_year, value
FROM financials
WHERE metric_name = 'revenue' AND segment = 'total' AND restated_flag = FALSE
ORDER BY fiscal_year;

-- Spot restatements: same metric/year reported with different values
SELECT fiscal_year, metric_name, COUNT(DISTINCT value) AS distinct_values
FROM financials
GROUP BY 1, 2
HAVING COUNT(DISTINCT value) > 1;
```

## Loading pattern (Python)

```python
import duckdb
con = duckdb.connect("data/financials.duckdb")
con.execute("""
  CREATE TABLE IF NOT EXISTS financials (
    fiscal_year INTEGER, metric_name VARCHAR, segment VARCHAR DEFAULT 'total',
    value DOUBLE, unit VARCHAR, source_year INTEGER, source_page INTEGER,
    restated_flag BOOLEAN DEFAULT FALSE, notes VARCHAR
  )
""")
```
