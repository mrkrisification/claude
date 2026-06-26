# DuckDB Schema — `data/financials.duckdb`

Design principle: **long/tidy format**, not one-column-per-year. This makes
cross-year queries trivial and survives the fact that A1's report layouts change
over 25 years. One row = one reported figure.

## Table: `financials`

| Column          | Type      | Notes                                                       |
|-----------------|-----------|-------------------------------------------------------------|
| fiscal_year     | INTEGER   | The year the figure *describes* (not publication year).     |
| metric_name     | VARCHAR   | Canonical snake_case name, e.g. `revenue`, `ebitda`.        |
| segment         | VARCHAR   | `total`, or a country/segment code (see below). Default `total`. |
| value           | DOUBLE    | The number, in `unit`. No pre-conversion.                   |
| unit            | VARCHAR   | e.g. `EUR_million`, `count`, `percent`.                     |
| source_year     | INTEGER   | Publication year of the report/factsheet this value came from. |
| source_page     | INTEGER   | Page in that PDF. NULL for factsheet (Excel) rows — see below. |
| restated_flag   | BOOLEAN   | TRUE if this is a restated/comparison-column value.         |
| notes           | VARCHAR   | Anything odd: definition change, footnote, OCR uncertainty. |

### Canonical metric names

Keep this list authoritative; add to it rather than inventing synonyms.
`revenue`, `ebitda`, `ebitda_excl_restructuring`, `ebitda_after_leases`, `ebit`,
`net_income`, `capex`, `free_cash_flow`, `total_assets`, `net_debt`, `equity`,
`employees`, `ebitda_margin`, `mobile_subscribers`, `fixed_rgus`.

If a report uses a different label, map it to the canonical name and record the
original wording in `notes`.

## Segments (the `segment` column)

`segment = 'total'` is the consolidated group (the default; sourced from the
annual reports). Per-country segment rows use these codes:

`austria`, `bulgaria`, `croatia`, `belarus`, `slovenia`, `serbia`,
`north_macedonia`, and `corporate` (= "Corporate, Others & Eliminations",
which **includes A1 Digital and intra-group eliminations**).

**Country segments do NOT sum to `total`.** Group = Σ(7 countries) + `corporate`,
and `corporate` is typically *negative* (eliminations outweigh A1 Digital's
external revenue). Always include `corporate` when reconciling to the group, or
filter to country segments only when you specifically want the operating split.
The annual reports publish only a bundled **"Additional Markets"** aggregate
(Slovenia + Serbia + Macedonia + Liechtenstein); the individual-country split
comes from the **analyst factsheets** instead.

By-segment metric coverage:

| metric | span | unit | loader | reconciles to group? |
|--------|------|------|--------|----------------------|
| `revenue` | FY2010–FY2025 | EUR_million | `load_segments.py` | yes (Σctry + corporate) |
| `ebitda` | FY2010–FY2025 | EUR_million | `load_segments.py` | yes; basis "EBITDA comparable" 2010–15, plain "EBITDA" 2016+ |
| `capex` | FY2010–FY2025 | EUR_million | `load_segment_ops.py` | yes (Σctry + corporate) |
| `mobile_subscribers` | FY2022–FY2025 | thousand | `load_segment_ops.py` | **no** — see note |
| `fixed_rgus` | FY2021–FY2025 | thousand | `load_segment_ops.py` | yes (Σctry ≈ Group) |

**Pre-2010 (FY2007–FY2009):** the group reported by function, not country, so the
only per-country split is the *Mobile Communication* segment (mobile-only, excl.
fixed line). Loaded by `scripts/load_segments_pre2010.py` under distinct metrics
**`mobile_revenue`** and **`mobile_ebitda`** (EUR_million) — deliberately *not*
`revenue`/`ebitda`, so they never mix with the FY2010+ total-operations series
(Austria mobile €1.6 bn in 2009 vs Austria total €3.1 bn in 2010 — different
basis). Dashboard: `charts/a1_mobile_footprint_2007_2009.png`.

**Mobile-subscriber caveat:** the factsheet's *Group* mobile total includes
**A1 Digital's IoT/M2M connections**, which are not attributed to any country.
So Σ(country mobile_subscribers) < Group, and the gap (≈3.8 m in 2022 growing to
≈9.5 m in 2025) is A1 Digital IoT. The per-country figures are the consumer/B2B
mobile bases as reported. Customer KPIs use unit `thousand` (reported "in '000").
Serbia had no fixed business until FY2025, so `fixed_rgus` for Serbia starts then.

### Provenance for factsheet (Excel) rows
Segment rows come from A1's "Analyst Fact Sheets" (`factsheets/*.xls[x]`), not the
report PDFs, so `source_page` is **NULL** and `notes` carries the factsheet file
name + sheet (e.g. `A1 analyst factsheet FS_FY2025.xlsx [Operating Results by
Segment_h]`). `source_year` is still publication year (`fiscal_year + 1`).

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
