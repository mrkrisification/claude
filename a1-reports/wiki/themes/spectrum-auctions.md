# Spectrum & frequency auctions

Spectrum is the single biggest swing factor in A1's capex line and a recurring
driver of leverage/ratings. This page collects the auctions and licence awards
across the footprint. The capex *figures* live in `data/financials.duckdb`
(`metric_name='capex'`); auction-specific costs are cited inline.

> **Sourcing convention.** `report + page` where the annual report carries the
> figure; external regulator/press sources tagged `[EXT]` (listed at the bottom)
> where it does not — the reports often name the bands but not the price.

## Why it matters for the numbers
A spectrum year shows up as a **capex spike** that is *not* an operational shift.
The clearest example is **FY2013**: capex jumped to **€1,779 m** (vs ~€730 m
typical) almost entirely because of one Austrian auction — see below and
`metrics`/the dashboard's capex panel.

## The auctions, by year

| Year | Market | Bands | A1 / group cost | Note | Source |
|------|--------|-------|-----------------|------|--------|
| 2000 | Austria | UMTS (2.1 GHz) | low by EU standards | Austria's Nov-2000 3G auction was among Europe's cheapest per-capita; UMTS era begins | `reports/2000` p6; comparative `[EXT-3]` |
| 2003 | Austria/CEE | UMTS launch | — | Europe's first **national UMTS network** (Apr 2003); first UMTS call in Croatia | `reports/2003` p33 |
| 2013 | **Austria** | 800/900/1800 MHz multiband | **€1.03 bn** for 2×70 MHz (50% of spectrum on offer, incl. ⅔ of the 800 MHz band) | drove the **2013 capex spike to €1,779 m**; rating cut to BBB-/Baa2 | `reports/2013` mgmt report; capex DB |
| 2019 | **Austria** | 3.4–3.8 GHz (5G pioneer band) | **€64.3 m** (auction total €187.7 m) | 5G-ready spectrum | `reports/2019` mgmt report; figure `[EXT-4]` |
| 2019 | Belarus | 5G-prep frequencies | n/d | acquired alongside Austria | `reports/2019` mgmt report |
| 2020 | **Austria** | multiband incl. 2,100 MHz | part of a ~€202 m auction | enabled the **Jan-2020 5G launch** (~25% population) | `reports/2020` mgmt report; total `[EXT-5]` |
| 2021 | **Croatia** | 700 MHz, 3.6 GHz, 26 GHz | n/d | 5G build-out | `reports/2021` mgmt report |
| 2023 | **Croatia** | 15-year licence | **€111 m** | long-dated renewal/award | `reports/2023` mgmt report |
| 2023 | **Bulgaria** | 700 MHz | n/d | 5G coverage band | `reports/2023` mgmt report |

`n/d` = band named in the report but the price is not disclosed there.

## The 2013 Austrian auction — the defining spectrum event
A1 took **2×70 MHz for €1.03 bn** — half the spectrum on offer, including
two-thirds of the prized 800 MHz coverage band (`reports/2013` mgmt report). The
funding pushed **capex to €1,779 m** (DB) and triggered **rating downgrades to
BBB-/Baa2** (S&P/Moody's), after which deleveraging back toward BBB became an
explicit, multi-year management theme. Any spike you see in a capex chart at 2013
is this auction — flagged on the dashboard.

## The 5G cycle (2019–2023)
Two Austrian auctions seeded 5G: the **2019 3.4–3.8 GHz** pioneer band (A1
**€64.3 m** `[EXT-4]`) and the **2020 multiband** round incl. 2,100 MHz that enabled
the **January 2020 commercial 5G launch** (`reports/2020`). The footprint then
followed — **Croatia** (700 MHz/3.6 GHz/26 GHz, 2021) and **Bulgaria** (700 MHz,
2023) — with a notable **€111 m, 15-year Croatian award in 2023** (`reports/2023`).
These rounds were materially cheaper than 2013, so 5G did **not** repeat the 2013
capex shock.

## See also
`reports/2013` (the spike), `reports/2019`–`reports/2023` (5G), and
`themes/regulation.md` (spectrum policy sits alongside roaming/MTR as the
regulatory levers on the business).

## External sources
- `[EXT-3]` Austrian 2000 UMTS auction among Europe's lowest per-capita — academic
  surveys of the 2000 European 3G auctions (Klemperer; ECB). Accessed 2026-06-26.
- `[EXT-4]` A1 paid €64.3 m in the 2019 Austrian 3.5 GHz auction (total €187.7 m) —
  A1 Group newsroom & CommsUpdate, 2019. Accessed 2026-06-26.
- `[EXT-5]` 2020 Austrian multiband 5G auction raised ~€202 m — RCR Wireless /
  CommsUpdate, Sep 2020. Accessed 2026-06-26.
