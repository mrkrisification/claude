# A1 Group Annual Reports — Index

The map of this knowledge base. **Agents: read this first, then navigate to the
specific file you need.** Do not read every file; pick the right one.

## How to use this index

- Need a **number** (revenue, EBITDA, headcount, ...)? → query `data/financials.duckdb`
  (see `data/SCHEMA.md`), not the prose below.
- Need **what happened / why / strategy / structure**? → open the relevant page below.
- Numbers are never read out of prose — they live in DuckDB.

## Start here
- **`overview.md`** — the group anchor: what A1 is, ownership/control history, brand
  evolution, how to read the financials.
- **`timeline.md`** — dated structural events 1998-2025 (the spine), each linked to its year note.

## Themes (cross-year narratives)
The load-bearing stories that span many years — read these for "the big picture of X"
rather than reconstructing it from per-year notes.

| Theme | File | Covers |
|-------|------|--------|
| International expansion & opcos | `themes/international-expansion.md` | entry-by-entry CEE acquisitions **with deal economics** (MobilTel ≤€1.6 bn, velcom €730 m, AMX 21% ≈ €766 m, …) |
| Regulation | `themes/regulation.md` | liberalisation, MTR/roaming, civil-servant workforce, Belarus dividend restriction |
| Spectrum & frequency auctions | `themes/spectrum-auctions.md` | UMTS (2000), the €1.03 bn 2013 Austrian auction (capex spike), the 5G cycle 2019-23 |
| Spin-offs & restructuring | `themes/spinoffs-and-restructuring.md` | EuroTeleSites (2023), the 2008/2011 restructurings, internal reorganisations |

**Sourcing note:** theme pages cite `report + page` where the annual report carries
the fact, and tag **external** IR/press sources `[EXT]` (with a list at the page
foot) where the reports are silent — chiefly **purchase prices** and **auction
totals**, which the reports usually omit.

## Reports (per-year highlights, sourced)

Per-year notes live in `reports/<year>/overview.md`. **All 28 fiscal years 1998-2025
have a sourced highlights note** (✅). Numbers for each year are in DuckDB. Deeper
`narrative.md` / `## Open questions` sections are added on demand.

| Span | Wiki notes | Theme |
|------|--------|-------|
| 1998-2002 | ✅ | Liberalisation, IPO (2000), early CEE mobile, mobilkom buyback |
| 2003-2009 | ✅ | UMTS, MobilTel/Bulgaria (2005), Belarus (2007), 2008 restructuring |
| 2010-2016 | ✅ | A1 brand, América Móvil, 2013 spectrum auction, recovery |
| 2017-2025 | ✅ | A1 Digital, IFRS 16, 5G/fibre, A1 Group rebrand, EuroTeleSites spin-off |

Full-text `markdown/` conversions are **not** generated yet — the wiki is sourced directly
from the PDFs in `pdfs/` (each note cites report + page).

## Cross-year metric views

| Metric | File | Status |
|--------|------|--------|
| Revenue | `metrics/revenue.md` | ✅ narrative |
| EBITDA (definitions, EBITDAaL, restructuring) | `metrics/ebitda.md` | ✅ narrative |
| EBIT / net income / capex / FCF / employees / net debt | — | DB only (add `metrics/*.md` on demand) |

## Database

`data/financials.duckdb` (`financials` table) holds, at **group level**, 10 metrics
— revenue, ebitda, ebitda_excl_restructuring, ebitda_after_leases, ebit, net_income,
capex, free_cash_flow, net_debt, employees — with per-row provenance (`source_year`,
`source_page`, `restated_flag`, `notes`). Loader: `scripts/load_financials.py`.

**Per-country segments:** for `austria`, `bulgaria`, `croatia`, `belarus`, `slovenia`,
`serbia`, `north_macedonia` (+ a `corporate` bucket = Corporate/Other & eliminations,
incl. A1 Digital). Sourced from the analyst **factsheets** (`factsheets/`):
- `revenue`, `ebitda`, `capex` — FY2010–FY2025 (`scripts/load_segments.py`,
  `scripts/load_segment_ops.py`)
- `mobile_subscribers` (FY2022–25), `fixed_rgus` (FY2021–25) — in '000
  (`scripts/load_segment_ops.py`)

**Country segments do not sum to group** (Corporate/eliminations + A1 Digital sit
outside; mobile subs also exclude A1 Digital IoT) — see `data/SCHEMA.md`. The "rise
of International" story is in `themes/international-expansion.md` (chart:
`charts/a1_international_rise.png`).

## How this wiki grows
Seeded with the durable pages (overview, timeline), per-year highlights for every
year, and two cornerstone metric narratives. It then **compounds on demand**: when a
question is answered (e.g. "what happened in 2008?"), the sourced answer is written
into the relevant year/metric page. Every claim cites a report + page.

## Known structural notes about A1's reports
- Reporting entity / brand naming changed over the years (Telekom Austria → A1 Telekom
  Austria Group → A1 Group) — see `overview.md`.
- Segment definitions and key-figure labels are not stable across decades; `metrics/ebitda.md`
  documents the most consequential (EBITDA) case, per-year notes flag others.
- Earliest reports (1998-1999) were in Austrian Schilling / EUR-billions; precise EUR-million
  early figures come from the FY2000 report's three-year summary. (All reports carry an
  extractable text layer — no OCR was required.)
