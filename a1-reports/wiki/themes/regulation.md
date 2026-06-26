# Regulation across the footprint

Regulation is a persistent, mostly *downward* pressure on A1's revenue and margins,
running in parallel to the growth from M&A and 5G/fibre. This page collects the
recurring regulatory threads. Where regulation produced a quantifiable hit, the
number lives in `data/financials.duckdb` or is cited inline.

> **Sourcing convention.** `report + page` where the report carries the point;
> `[EXT]` for external regulatory/press context.

## The four recurring levers
1. **Market liberalisation & asymmetric (incumbent) regulation** — the structural
   starting point.
2. **Mobile termination rates (MTRs)** — regulated interconnection cuts, a steady
   revenue drag through the 2010s.
3. **Retail roaming caps → "Roam-like-at-home" (RLAH)** — EU-driven, peaks mid-2010s.
4. **Spectrum policy** — covered in `themes/spectrum-auctions.md` (the cost side).

## Timeline of regulatory events

| Year | Event | Effect | Source |
|------|-------|--------|--------|
| 1998 | **Full liberalisation** of the Austrian market (TKG, 1 Jan 1998); asymmetric regulation + Telekom-Control-Kommission interconnection rulings | incumbent opened to competition; fixed-voice share began falling | `reports/1998` p5 |
| 1999 | Alternative fixed-voice providers **quadrupled**; voice-telephony share fell to ~85% | EBITDA margin 52.8% → 39.6% | `reports/1999` p13, p3 |
| 2003 | **New Austrian Telecommunications Act 2003** redefined the market into **18 sub-markets** | reshaped SMP/access obligations | `reports/2003` p37 |
| 2008 | **Civil-servant Fixed-Net workforce** (~8,500 non-terminable contracts) → €632 m social-plan restructuring | a *labour/legal* constraint unique to the privatised incumbent | `reports/2008` p15–16 |
| 2011 | **Roaming & MTR cuts** explicitly flagged as headwinds | revenue/margin drag across CEE | `reports/2011` mgmt report |
| 2016 | **Retail-roaming revenue losses** ahead of EU RLAH (June 2017) | offset by M&A-driven revenue +2.1% | `reports/2016` mgmt report |
| 2022–24 | **Inflation / "value protection" price indexation** in Austria, Bulgaria, Croatia | regulator-permitted CPI-linked price rises *offset* prior drags | `reports/2022`, `reports/2024` |
| 2024–25 | **Belarus dividend-payment restrictions** (in force since Apr 2024) | a sanctions/geopolitical constraint trapping cash at velcom | `reports/2024`, `reports/2025` mgmt report |

## The standout regulatory cases

**The civil-servant workforce (Austria).** Unlike a normal telco, the privatised
incumbent inherited **~8,500 civil-servant Fixed-Net staff whose contracts cannot be
terminated** (`reports/2008` p15–16). Reducing this protected headcount could only be
done via expensive social plans — the **€632 m FY2008 charge** is the largest single
instance, and smaller social-plan offers recur through the 2010s (e.g.
`reports/2013`). This is why `ebitda` vs `ebitda_excl_restructuring` diverge so
often in the data (see `metrics/ebitda.md`).

**Roaming (EU RLAH).** The EU's abolition of retail roaming surcharges
("Roam-like-at-home", from June 2017) shows up as **explicit retail-roaming revenue
losses in 2016**, masked at the group level only because convergence M&A pushed
revenue up +2.1% (`reports/2016`). MTR cuts run alongside through the early-2010s
decline (`reports/2011`).

**Belarus dividend restrictions.** Since **April 2024**, dividend-payment
restrictions have trapped cash at the Belarusian operation — the main standing
geopolitical overhang on group cash flow, still effective at FY2025
(`reports/2025`).

## See also
`themes/spectrum-auctions.md` (spectrum is the cost side of regulation),
`metrics/ebitda.md` (restructuring/EBITDA mechanics), `reports/2008` (the
civil-servant charge), `reports/2025` (Belarus).
