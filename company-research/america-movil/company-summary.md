# América Móvil — financial & market profile

**América Móvil, S.A.B. de C.V.** (BMV/NYSE: AMX) is the largest telecommunications operator in
Latin America, with operations in 23 countries aggregated into 10 reportable segments. Its anchor
markets are Mexico (Telcel in wireless, Telmex in fixed) and Brazil, which together account for over
half of group revenue-generating units (RGUs). It is a listed parent, controlled by the Slim family
through control trusts, and files a Form 20-F with the U.S. SEC as a foreign private issuer.

## Financials (FY2025, consolidated, IFRS, MXN)

- **Operating revenues:** Ps.943.6bn (≈US$52.5bn), up 8.6% on FY2024 (+6.2% at constant FX).
- **EBITDA:** Ps.372.2bn, a ~39.4% margin — margins have been stable at ~39% across 2023–2025.
- **Operating income:** Ps.191.4bn.
- **Net profit:** Ps.88.1bn (Ps.82.8bn attributable to the parent). FY2024 net profit was depressed
  to Ps.27.6bn by foreign-exchange and derivative effects, despite higher operating income —
  a swing worth noting in any trend read.
- **Capex:** Ps.130.8bn (flat vs FY2024; FY2023 was higher at Ps.156.3bn). 2026 capex budgeted at
  ~US$7.0bn.

## Market / operations (as of Dec 31, 2025)

- **Total RGUs:** 410.6m (wireless 331.2m, fixed 79.4m), up from 400.5m a year earlier.
- ~331m wireless voice & data subscriptions; ~13.7m Pay TV RGUs.
- Largest market share by RGUs in Mexico and Brazil.

## Data confidence & gaps

- **Confidence:** 1 primary capture — the audited FY2025 Form 20-F (S01), the strongest possible
  source for a listed issuer. All figures are own-filed consolidated IFRS numbers (`estimated=false`),
  no conflicting sources, so no preference calls were needed.
- **Conflicts:** none (single authoritative source).
- **EBITDA** is computed as operating revenues less operating costs excluding D&A (equivalently
  operating income + D&A) — América Móvil's own definition; flagged in the dataset `note`.
- **Missing / not yet collected:** quarterly detail (1Q26 and prior) and the investor data book were
  discovered on the IR CDN (s22.q4cdn.com) but **not captured — the Firecrawl account hit its credit
  limit (HTTP 402) right after the 20-F, and this environment's egress allowlist blocks direct PDF
  download.** Re-run the report watcher once credits are topped up; the ledger resumes and pulls them.
- **Segment detail** (per-country revenue/EBITDA from Note 23) is present in S01 but not yet
  extracted into the datasets — a natural next pass.
- **Currency:** all figures in MXN as filed; FY2025 USD equivalents use the 20-F rate of
  Ps.17.9667 = US$1.00.
