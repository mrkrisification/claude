# A1 Group (Telekom Austria) — Group overview

The durable anchor page: what the group is, how it is owned, how the brand and
footprint evolved. Numbers live in `data/financials.duckdb`; this page is
narrative. Year-by-year detail is in `reports/<year>/overview.md`; structural
events are listed in `timeline.md`.

## What it is
A telecommunications group headquartered in Vienna, operating fixed-line and
mobile networks in **Austria plus a cluster of CEE/SEE markets** — over its
history: Bulgaria, Croatia, Slovenia, Serbia, the Republic of (North) Macedonia,
Belarus and Liechtenstein. The Austrian segment has fallen from the whole company
to roughly **half of group revenue** (52% in 2024, 49% in 2025), reflecting the
long CEE-led growth shift. (`reports/2024`, `reports/2025`)

## Brand evolution
- **Telekom Austria** — the incumbent, spun off from the federal postal
  administration (PTA); fully exposed to competition from 1 Jan 1998. (`reports/1998`)
- **"Jet2Web"** umbrella brand launched 2000 around the IPO. (`reports/2000`)
- **"A1"** — the mobile (mobilkom) premium brand, progressively adopted group-wide:
  Austrian fixed+mobile merged into **A1 Telekom Austria** (2010), single brand "A1"
  rolled out from 2011. (`reports/2010`, `reports/2011`)
- **"A1 Group"** — current name, rebranded from A1 Telekom Austria Group in 2022.
  (`reports/2022`)

## Ownership / control history
- **Pre-2000:** state-owned via ÖIAG (the Austrian state holding).
- **Nov 2000 IPO:** listed in Vienna and on the NYSE; free float 22.4%, ÖIAG 47.8%,
  Telecom Italia 29.8%. (`reports/2000`)
- **2004:** Telecom Italia exits; ÖIAG trims its stake — free float ~70%. (`reports/2004`)
- **2012-2014:** **América Móvil** (Carlos Slim's group) builds a stake (22.76% in 2012)
  and becomes **majority shareholder in 2014**, alongside the state holding (ÖIAG, later
  ÖBAG) under a syndicate agreement. (`reports/2012`, `reports/2014`)

## How to read the financials
- The headline **EBITDA definition changes repeatedly** over 25 years — see
  `metrics/ebitda.md` before comparing EBITDA across eras.
- **IFRS 16** (from FY2019) lifts EBITDA and adds EBITDAaL; the **EuroTeleSites tower
  spin-off** (FY2023) raises depreciation and depresses EBIT from FY2024. (`reports/2019`,
  `reports/2023`)
- Numbers are always queried from DuckDB (`financials` table), never read from prose.
