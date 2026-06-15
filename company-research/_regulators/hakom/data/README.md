# HAKOM full-market dataset (Croatia) — what this contains

`market.csv` is the **whole-market backbone** for Croatia, composed from the 9 HAKOM
"Quarterly data on the electronic communications market in the Republic of Croatia"
reports in `../raw/` (indexed in `../raw/manifest.md`, source_ids R01–R09).

## Critical structural finding: HAKOM reports market TOTALS only — NO per-operator splits

Every one of these 9 reports is a **Croatia-wide aggregate**. They tabulate national
totals (total mobile subscribers, total fixed broadband lines, total pay-TV subscriptions,
total market revenue by service, etc.) collected from all operators, but they **do not
break any figure out by operator**.

Verified mechanically: a case-insensitive search across all 9 PDFs for `A1`,
`Hrvatski Telekom`/`HT`/`T-HT`, `Telemach`, `Tele2`, and `market share` / `tržišni udio`
returns **zero hits in the data tables**. There are no per-operator subscriber counts and
no per-operator market shares anywhere in these English-language reports — not in tables,
and these editions carry no operator-split charts either.

Consequence for the dataset:
- **All rows use `operator=_market`.** Per-operator metrics (`mobile_market_share`,
  `fixed_broadband_market_share`, per-operator subscriber counts, per-operator ARPU)
  **could not be extracted from these sources** and are therefore absent.
- Per-operator shares for the Croatian market must come from elsewhere — the operators'
  own filings / parent-group segment reporting (Hrvatski Telekom Group, A1 Group / A1
  Hrvatska, United Group / Telemach), or a separate HAKOM dataset/portal that publishes
  operator splits. They are **not** in these whole-market quarterly PDFs.

## Metrics populated (all `_market`)

- `mobile_lines` — total active mobile subscribers (SIM cards; 3G/4G/5G, 90-day-active def.)
- `mobile_market_share` — N/A (not reported; whole-market only)
- `fixed_broadband_subscribers` — total fixed broadband lines (excl. fixed-location-via-mobile)
- `tv_subscribers` — total pay-TV subscriptions (lines)
- `market_revenue` — segment revenues where the report states them. Reports come in two
  layouts: the older quarterly editions (R01–R07) print **quarterly** segment revenue;
  the FY2024 (R08) and FY2025 (R09) editions also print the **full-year total market
  revenue** in the summary. `segment` distinguishes which (e.g. `mobile_quarterly`,
  `tv_quarterly`, `total_annual`).
- `arpu` — N/A (HAKOM does not publish ARPU in these reports).

Also captured as `_market` extras: `broadband_subscribers_total` (fixed + mobile broadband
lines combined, as HAKOM reports it) and `mobile_penetration`.

## Period / currency notes

- Year-end snapshots use the Q4 report of each year: **FY2022 = R02, FY2023 = R06,
  FY2024 = R08, FY2025 = R09**. Some intermediate quarters (Q3-2022 R01) are included where
  trivially available.
- Croatia adopted the EUR on 2023-01-01. **R01–R02 (through Q4 2022) report money in HRK**
  (fixed rate 7.5345 HRK/EUR); **R03 onward in EUR.** The `unit` column records the
  reported currency (`HRK` or `EUR`); no currency conversion was applied.
- HAKOM publishes numbers in European format (`.` thousands, `,` decimals); all values in
  the CSV are normalised to plain numbers with `.` as decimal separator.
- Note: the FY2024 summary bullet in R08 reads "EUR 1.869.887.668 million" — this is a HAKOM
  wording slip; the value is EUR 1,869,887,668 (~1.87 billion), recorded as such.

## `estimated` column

`false` = figure stated directly by HAKOM. `true` = derived (e.g. a unit conversion to
millions/thousands of a directly-stated count). No market shares were derived because the
operator-level counts needed to compute them are not present.
