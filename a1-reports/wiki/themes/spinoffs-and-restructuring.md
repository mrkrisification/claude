# Spin-offs, carve-outs & restructuring

Structural changes to *what the group is made of* — separations, carve-outs and the
big workforce restructurings. These reshape the financial statements (depreciation,
EBIT, EBITDA, employees) independently of trading, so they're essential context for
reading the timeseries in `data/financials.duckdb`.

> **Sourcing convention.** `report + page` where the report carries the point;
> `[EXT]` for external context.

## The headline: EuroTeleSites (2023)
- **What:** the group's **passive tower / mast infrastructure** was carved out into
  **EuroTeleSites AG** and **separately listed** (spin-off to shareholders),
  completed 2023. (`reports/2023` p6)
- **Why it matters for the numbers:** A1 now **leases back** capacity on the towers
  it spun off. From **FY2024** those lease-backs **raise depreciation**, so **EBIT
  fell to €861 m even as EBITDA grew to €2,021 m** (`reports/2024`, DB). The
  **EBIT/EBITDA divergence from FY2024 is structural, not operational** — the single
  most important caveat when comparing post-2023 EBIT to earlier years.
- **Lineage:** part of the same industry trend (carriers monetising towers) as the
  later 5G/fibre capex cycle; complements the asset-light direction.

## The workforce restructurings (the EBITDA distorters)
A1's restructurings are dominated by the **Austrian civil-servant Fixed-Net
workforce** — protected, non-terminable contracts reduced only via social plans
(see `themes/regulation.md`).

| Year | Restructuring | Size | Effect on the numbers | Source |
|------|---------------|------|----------------------|--------|
| 2000 | "W.E.R.T." programme + post-IPO reorg | — | depressed reported profit in the IPO year (operating loss €−31.5 m) | `reports/2000` p6,9 |
| 2008 | **Fixed-Net civil-servant social plan** | **€632.1 m** charge (€617.4 m provision) | reported EBITDA −30% to €1,295.6 m on *record* revenue; excl-restructuring ≈ €1,928 m (up YoY) | `reports/2008` p15–16 |
| 2011 | Restructuring charges + **velcom impairment** | €233.7 m restructuring + €279.0 m impairment | net **loss €252.8 m**; cumulative restructuring provisions reached €888.8 m | `reports/2011` mgmt report |
| 2013+ | Ongoing Austrian social-plan offers | recurring | keeps `ebitda` vs `ebitda_excl_restructuring` apart | `reports/2013` mgmt report |

The **2008 charge is the textbook case**: a single non-cash provision made headline
EBITDA collapse while the business actually grew — which is precisely why the DB
carries `ebitda_excl_restructuring` as a separate metric (see `metrics/ebitda.md`).

## Internal reorganisations (structure, not separation)
These changed reporting structure / control without removing assets:

- **2002** — repurchased the mobilkom minority from Telecom Italia Mobile; reorganised
  into **Wireline / Wireless** segments (`reports/2002` p6).
- **2009–2010** — merged the Austrian Fixed-Net and Mobile operations into a single
  company, **A1 Telekom Austria** (board approval 2009 → executed 2010)
  (`reports/2009` p3, `reports/2010` p1,5).
- **2017** — founded **A1 Digital** as an international IoT/cloud-ICT subsidiary — a
  *build*, not a carve-out (`reports/2017`).

## Brand vs structure (don't confuse them)
The frequent **rebrandings** — Jet2Web (2000), single "A1" brand (2010–11),
group-wide rebrand (2018), **"A1 Group"** (2022) — are identity changes, **not**
structural separations, though the 2018 rebrand carried real cost (brand
amortisation / a ~€180.8 m financial-result item, `reports/2018`). Tracked in
`timeline.md` and `overview.md`.

## See also
`reports/2023` (EuroTeleSites), `reports/2008` & `reports/2011` (restructuring),
`metrics/ebitda.md` (why these distort EBITDA), `themes/regulation.md` (the
civil-servant constraint behind the restructurings).
