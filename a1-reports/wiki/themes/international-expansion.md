# International expansion & the CEE operating companies

How an Austrian fixed-line incumbent became a CEE-mobile-led group. This page
pulls the scattered per-year acquisition events into one narrative **with deal
economics**. Group numbers live in `data/financials.duckdb`; per-opco annual
financials are **not** in the DB (group-total only) — deal-level figures below are
cited inline.

> **Sourcing convention.** Facts carried by the annual reports cite `report + page`
> (as in the year notes). The reports are typically silent on **purchase prices**;
> those come from external IR / press sources, tagged `[EXT]` and listed at the
> bottom. Customer counts and stakes are mostly report-sourced.

## The arc in one line
Austria-only (→1998) → first CEE mobile stakes (Slovenia/Croatia, 2001) → the
**MobilTel/Bulgaria leap (2005)** → **Belarus (2007)** → SEE bolt-ons
(Serbia, Macedonia, cable convergence) → consolidation under América Móvil
(2012–14) → footprint optimisation + tower carve-out (2023).

## Entry-by-entry (with deal economics)

| Year | Market / target | Stake | Deal value | At entry | Source |
|------|-----------------|-------|-----------|----------|--------|
| 1999 | **Croatia** — VIPnet | consolidated | n/d | first foreign mobile consolidation | `reports/1999` p3 |
| 2001 | **Slovenia** — Si.mobil | controlling | n/d | first controlling CEE mobile stake | `reports/2001` p4 |
| 2005 | **Bulgaria** — MobilTel | 100% | **EUR ≤1.6 bn** enterprise value (€80 m call-option creditable; funded by a €1.0 bn bond) | Bulgaria's #1 mobile operator; "largest-ever acquisition by an Austrian company" | `reports/2005` p5,7,41; price `[EXT-1]` |
| 2006 | **Serbia, Macedonia** | mobile entries | n/d | footprint reaches ~13 mn customers | `reports/2006` p1,3 |
| 2007 | **Belarus** — MDC / velcom | **70%** | **EUR ~730 m** (put option on remaining 30% ≈ **€320 m**, exercised → 100% by ~2010) | #2 operator, 43.4% share, ~3.1 mn customers, 71.5% penetration | `reports/2007` p9; price/structure `[EXT-2]` |
| 2011 | **Croatia** — B.net | acquired | n/d (report does not disclose) | cable / pay-TV / internet → Vipnet convergence | `reports/2011` mgmt report |
| 2014 | **Macedonia** — blizoo + Vip/One merger → one.Vip | acquired / merged | n/d | leading Macedonian cable operator | `reports/2014` mgmt report |
| 2015 | **Slovenia/Serbia** — Amis | acquired | n/d | convergence bolt-on | `reports/2015` p8 |
| 2016 | **Belarus** — Atlant Telecom / TeleSet | acquired | n/d | makes velcom a convergent (fixed+mobile) operator | `reports/2016` mgmt report |

`n/d` = not disclosed in the report and not yet sourced externally — a candidate
follow-up if a specific deal value is needed (check the A1 Group newsroom archive).

## The two structural leaps

**2005 — MobilTel (Bulgaria).** The inflection from an Austria-centric incumbent to
a CEE mobile-led group. Enterprise value of up to **€1.6 bn** `[EXT-1]`, funded by a
**€1.0 bn bond** placed early 2005 (`reports/2005` p7); goodwill on the group balance
sheet roughly doubled (596.6 → 1,149.2 €m, `reports/2005` p41). Mobile reached ~9 mn
customers across AT/BG/HR/SI/LI (`reports/2005` p5). From here, mobile scale drives
group revenue and EBITDA.

**2007 — Belarus (velcom).** Bought 70% of MDC for **~€730 m** `[EXT-2]`; ~3.1 mn
customers added in one step (`reports/2007` p1,9). Debt-funded, so net debt jumped
~39% to €4,407 m (`reports/2007` p9) and net-debt/EBITDA breached the 2.0× covenant
ceiling (`reports/2007` p10). velcom becomes a long-running — and later
geopolitically sensitive — asset (see the Belarus dividend-restriction note in
`reports/2025`).

## Footprint at its widest
By FY2009 the group served **~18.9 mn mobile customers across 8 markets** — Austria,
Bulgaria, Belarus, Croatia, Slovenia, Liechtenstein, Serbia and Macedonia
(`reports/2009` p3). The mix has shifted steadily since: **Austria fell from the
clear majority of revenue to 52% (FY2024) and 49% (FY2025)** — CEE now slightly more
than half the group (`reports/2024`, `reports/2025`).

## Per-country financials are now in the DB (FY2010–FY2025)
The `segment` column now carries **per-country revenue and EBITDA** for Austria,
Bulgaria, Croatia, Belarus, Slovenia, Serbia and North Macedonia — loaded by
`scripts/load_segments.py` from A1's **analyst factsheets** (the annual reports
only publish the bundled "Additional Markets" aggregate; the factsheets split the
individual countries out). See `data/SCHEMA.md` for the segment codes.

> **Caveat (important):** country segments **do not sum to group revenue**. A
> `corporate` bucket — "Corporate, Others & Eliminations", which **includes A1
> Digital and intra-group eliminations** — sits outside them and is usually
> *negative*. Group = Σ(7 countries) + `corporate`.

### The headline: International is now ~half the group
International (everything except Austria) has risen steadily as a share of
country-segment revenue, crossing 50% in FY2025:

| | FY2010 | FY2015 | FY2020 | FY2025 |
|---|---|---|---|---|
| Austria revenue (€m) | 3,064 | 2,527 | 2,622 | 2,745 |
| International revenue (€m) | 1,675 | 1,541 | 1,958 | 2,851 |
| **International % of rev** | 35.3% | 37.9% | 42.7% | **50.9%** |
| **International % of EBITDA** | 38.4% | 37.0% | 42.7% | **52.8%** |

Austria's revenue is roughly flat-to-down across 15 years while the CEE/SEE
markets grew — Bulgaria, Croatia and Belarus are now the largest international
contributors. Chart: `charts/a1_international_rise.png`
(`scripts/segments_chart.py`).

```sql
-- International share of country-segment revenue by year
WITH s AS (SELECT fiscal_year,
  CASE WHEN segment='austria' THEN 'AT' ELSE 'INTL' END AS g, value
  FROM financials WHERE metric_name='revenue' AND restated_flag=FALSE
  AND segment NOT IN ('total','corporate'))
SELECT fiscal_year,
  ROUND(100*SUM(value) FILTER (WHERE g='INTL')/SUM(value),1) AS intl_pct
FROM s GROUP BY 1 ORDER BY 1;
```

**Earlier years (FY2007–FY2009)** exist in the factsheets too, but only as a
mobile-segment-by-country split (different basis) — a candidate follow-on load.

## See also
`timeline.md` (the four defining events), `reports/2005`, `reports/2007`,
`reports/2012`, `reports/2014`, and `themes/spinoffs-and-restructuring.md`
(EuroTeleSites, which reshaped the footprint from the asset side).

## External sources
- `[EXT-1]` MobilTel enterprise value ≤€1.6 bn / €80 m call option creditable —
  Telekom Austria ad-hoc release & contemporaneous trade press (RCR Wireless,
  Novinite), 2004–2005. Accessed 2026-06-26.
- `[EXT-2]` velcom/MDC: €730 m for 70%, €320 m put option on remaining 30% —
  Light Reading / Telecoms.com / Belarus News, 2007. Accessed 2026-06-26.
