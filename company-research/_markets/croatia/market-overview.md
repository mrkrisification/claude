# Croatia Telecom Market — Operator Overview

**Assembled:** 2026-06-15 · **Composed by:** union of per-operator `company-research/<slug>/data/` +
the shared HAKOM regulator cache (`company-research/_regulators/hakom/`). Machine-readable union in
`data/market.csv`. Source ids are cross-folder (`hakom/R08`, `hrvatski-telekom/S04`, `a1-croatia/S01`).

This is the first end-to-end roll-up of the financial-analyst pipeline. Its most useful output is not a
tidy share table — it is the **reconciliation**, which exposes that the regulator, the operators, and the
country baseline currently measure the market three incompatible ways.

## Market size (HAKOM, whole-market)

| Metric (year-end) | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|
| Mobile lines (m) | 4.48 | 4.56 | 4.72 | 4.96 |
| Mobile penetration | 115% | 118% | 122% | 128% |
| Fixed broadband subs (m) | 1.09 | 1.11 | 1.15 | 1.18 |
| TV subs (m) | 0.87 | 0.92 | 0.93 | 0.94 |
| Total market revenue | — | — | **€1,869.9m** | ~€1,870m |

Mobile penetration >120% and rising = the M2M/multi-SIM effect that drives the reconciliation problem
below. HAKOM reports only **whole-market totals** — no per-operator splits exist in its English reports
(the central collection gap; per-operator data would need the Croatian-language `sat.hakom.hr` portal).

## Operator financials — FY2024 (the best cross-covered year)

| Operator | Revenue | EBITDA | Margin | Net income | Basis |
|---|---|---|---|---|---|
| **Hrvatski Telekom** | €1,101.6m | €416.2m (AL) | 37.8% | €141.9m | Group consolidated *(incl. Montenegro, equipment, wholesale)* |
| **A1 Croatia** | €570m (seg) / €579m (stat) | €224m | 39.3% | **€25.1m** | parent segment + FINA net |
| **Telemach Croatia** | €310.1m | n/d (FY25 €107.2m) | ~34% | €9.3m | FINA statutory (legal entity) |

A1's parent-segment revenue (€570m) is **confirmed** by A1 Hrvatska d.o.o.'s statutory filing (€579.1m,
~1.5% apart), and the registry supplies A1's **net income** (€25.1m FY2024) that segment reporting omits.
Telemach's FY2024 figures are the FINA/registry statutory accounts.

**Multi-year (EUR m):**
- HT revenue 1,039 → 1,102 → 1,142 (FY23→25), EBITDA 398 → 416 → 430.
- A1 revenue (statutory) 532 → 579 (FY23→24), EBITDA seg 189 → 224, net 24.1 → 25.1.
- **Telemach revenue 278.5 → 310.1 → 328.4 (FY23→25)** — steady challenger growth; net result swung from a
  **loss in FY2023** to €9.3m (FY24) to €8.6m (FY25); FY2025 EBITDA €107.2m (~33% margin). Source: FINA
  statutory accounts (Telemach Hrvatska d.o.o.), republished in the Croatian business press (Top-505).

Grounded picture: **HT (~€1.0bn Croatia-only) ≫ A1 (€579m) > Telemach (€328m)**; margins A1 39% > HT 38%
> Telemach ~33% (the aggressive-pricing challenger, recently turned profitable). A1 carries the fastest
EBITDA growth (+18.7% FY2024); A1's FY2025 Croatia segment is not separately disclosed (folded into
"International").

## Subscribers & market share — why we do NOT publish a share table

The point where the roll-up earns its keep. Three sources, three irreconcilable pictures:

| FY2024 mobile | value | implied share of HAKOM 4.72m |
|---|---|---|
| HT reported mobile subs | 2.477m | 52% |
| A1 reported mobile subs | 2.158m | 46% |
| HT + A1 alone | **4.635m** | **98%** |
| Telemach (ex-Tele2, ~1m base) | not disclosed | — |
| Baseline's stated shares | HT 46% / Telemach 35% / A1 20% | — |

HT + A1 *reported* bases already consume 98% of HAKOM's total, leaving no room for Telemach's ~1m+
ex-Tele2 base — so **operator "subscribers" and HAKOM "mobile lines" use different definitions** (active
SIM vs registered, M2M inclusion). Meanwhile the **baseline's share column** (HT 46 / Telemach 35 / A1 20)
cannot be right either: A1's reported 2.16m base could never be a 20% share. Computing
`operator subs ÷ regulator total` would manufacture false precision, so the dataset records the totals and
the reported bases separately and **derives no mobile share**.

Same problem in fixed broadband: HT 0.669m + A1 0.722m = 1.391m **exceeds** HAKOM's whole-market fixed-BB
total of 1.147m — because A1's "722k" is **fixed RGUs** (broadband + TV + voice), not broadband lines.
Not comparable to HT's pure broadband count; flagged for re-extraction.

## Cross-operator findings (the payoff of composing)

1. **Regulator gives denominators, not shares.** HAKOM's English reports are whole-market totals only;
   no per-operator breakdown is collectable from them. → resolve via `sat.hakom.hr` / Croatian-language
   operator data, or treat operator self-reported bases as the share source (with the caveat below).
2. **Subscriber definitions don't reconcile** (operator active-base vs HAKOM mobile-lines vs M2M). Any
   cross-operator share needs one consistent definition first.
3. **The Croatia baseline's mobile shares (46/35/20) look stale or mislabeled** and should be corrected —
   they contradict every operator's own reported base.
4. **HT scope mismatch:** HT Group revenue includes Montenegro + equipment + wholesale, so it overstates
   HT's *Croatian retail* market revenue; only the Croatia subscriber KPIs are clean.
5. **A1 fixed metric mislabel:** 722k is RGUs, not broadband subs.
6. **Telemach's financials came from the company registry, not the parent.** It was a *sourcing* gap, not
   a disclosure gap: as a Croatian d.o.o., Telemach Hrvatska files **statutory accounts with FINA** (FY2025
   revenue €328m, EBITDA €107m, net €8.6m). The lesson generalises — for a private subsidiary the national
   **company/financial registry** (FINA in HR; Companies House UK; Bundesanzeiger DE; etc.) is a primary
   source, ahead of press/web. Telemach remains **subscriber-invisible** only because HAKOM publishes no
   operator split.

## Data confidence & provenance

- **High:** market totals (HAKOM, FY2022–FY2025); HT financials (listed, FY2021–FY2025, audited);
  A1 Croatia revenue/EBITDA (parent segment, FY2022–FY2024) + statutory **net income** (FINA);
  **Telemach revenue FY2023–FY2025, net income FY2024–FY2025, EBITDA FY2025 (FINA statutory / Top-505).**
- **Low / missing:** all per-operator market **shares**; Telemach **subscriber** counts; A1 FY2025
  segment; clean fixed-broadband subscriber counts.
- Every figure in `data/market.csv` cites a cross-folder `source_id` tracing to a `raw/` capture.
  Money normalized to EUR millions (`EUR_m`); HT FY2021–FY2022 originals are in HRK (see HT `financials.csv`).
