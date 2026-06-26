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

## Why per-opco financials aren't in the DB (yet)
The annual reports present **segmented** revenue/EBITDA by country, but the DB
currently stores only `segment='total'`. Building a per-opco annual series
(Bulgaria, Belarus, Croatia, …) is a deferred extraction pass — the `segment`
column already exists in the schema to receive it. For now, opco context is the
deal economics above plus the qualitative per-year notes.

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
