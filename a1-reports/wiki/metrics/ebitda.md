# EBITDA across years — definitions matter

Cross-year narrative for EBITDA. **Figures live in `data/financials.duckdb`**; this
page explains why a raw EBITDA line splices incompatible definitions and how the
database separates them. Three EBITDA metrics exist in the DB:

- `ebitda` — the headline EBITDA **as the company reported it each year** (the label
  changed repeatedly; basis noted per row).
- `ebitda_excl_restructuring` — EBITDA before restructuring/one-offs (the
  "adjusted"/"comparable"/"before restructuring" management measure).
- `ebitda_after_leases` (EBITDAaL) — post-IFRS 16 measure comparable to the old
  pre-IFRS16 EBITDA (FY2019+).

## The headline-EBITDA label timeline
| Period | Reported label | Notes |
|--------|----------------|-------|
| 1998-2000 | `EBITDA**` | monopoly → IPO era; margin fell from ~53% (1998) toward ~26% (2000) |
| 2001-2002 | Total managed EBITDA | "managed" presentation incl. proportionate stakes |
| 2003-2006 | Adjusted EBITDA | excludes one-offs |
| 2007-2009 | EBITDA | reported (incl. restructuring) |
| 2010-2015 | EBITDA comparable | excludes restructuring/impairment |
| 2016-2018 | EBITDA | reported, **pre-IFRS 16** |
| 2019-2025 | EBITDA | reported, **IFRS 16 basis** (EBITDAaL reported alongside) |

A naïve cross-year `ebitda` trend therefore steps at several seams. The two sharpest:
the **comparable→reported switch (2015→2016)** and **IFRS 16 (2018→2019)**.

## The IFRS 16 break (captured as a restatement)
From FY2019 leases are capitalised, lifting EBITDA. The database keeps **both**
versions of FY2018 EBITDA:
- `1,380.6` — originally reported (pre-IFRS16), `restated_flag = FALSE`
- `1,548.9` — restated to IFRS16 basis in the FY2019 report, `restated_flag = TRUE`

`EBITDAaL` (= EBITDA − IFRS16 lease depreciation − lease interest) is the line
comparable to the old pre-IFRS16 EBITDA. (`reports/2019`)

## 2008: record revenue, EBITDA "collapse" — a definitional illusion
Reported EBITDA fell ~30% to €1,295.6 mn in 2008 on **record revenue**, because of a
**single €632 mn non-cash restructuring provision** for the Austrian civil-servant
fixed-line workforce. Add it back and EBITDA-excl-restructuring ≈ **€1,928 mn —
above 2007**. So 2008 was an operating growth year masked by a one-off. (`reports/2008`)

## 2017 quirk
In FY2017 `ebitda_excl_restructuring` (1,380.7) is **below** reported `ebitda`
(1,397.3) — unusual, but real: A1 had a net **positive** restructuring effect
(provision reversal) that year, so removing it lowers EBITDA. Not an extraction error.

## Coverage in the DB
- `ebitda`: FY1998-2025 (full)
- `ebitda_excl_restructuring`: FY2003-06, 2010-15, 2017-25 (gaps 2007-09 and 2016 —
  those years featured only the plain/reported EBITDA)
- `ebitda_after_leases`: FY2022-2025 (reported from FY2019; earlier years not yet loaded)

## Example query
```sql
-- headline vs excl-restructuring, where both exist
SELECT a.fiscal_year, a.value AS ebitda, b.value AS ebitda_excl_restr
FROM financials a
JOIN financials b USING (fiscal_year)
WHERE a.metric_name='ebitda' AND b.metric_name='ebitda_excl_restructuring'
  AND a.restated_flag=FALSE AND b.restated_flag=FALSE
ORDER BY a.fiscal_year;
```
