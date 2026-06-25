# FY2008 — Record revenue, but a €632 mn restructuring charge

*Source: `2008_Annual_Report.pdf`. Numbers in `data/financials.duckdb` (`fiscal_year=2008`).*

## Highlights & events
- **Record revenue of €5,170.3 mn**, yet **reported EBITDA fell ~30% to €1,295.6 mn**, EBIT −82% to €135.5 mn and net income swung to a **−€48.8 mn loss**. (p3)
- The cause was a **single non-cash restructuring provision of €617.4 mn (€632.1 mn total charge)** for the Austrian **Fixed Net civil-servant workforce** (~8,500 employees whose contracts cannot be terminated), funded via a social plan. (p15–16)
- Stripped of the charge, **EBITDA excl. restructuring ≈ €1,928 mn — actually up vs 2007**: operationally a growth year, not a downturn. (derived; see `metrics/ebitda.md`)
- Net debt/EBITDA 3.1× incl. restructuring vs 2.1× excluding. (p3)
- Mobile customers ~17.8 mn (+15.2%); dividend held at €0.75 (yield 7.3%). (p12, p... )

## Notes
- This is the textbook example of why headline EBITDA ≠ operating performance, and why the database carries `ebitda_excl_restructuring` as a separate metric. The provision kicked off a multi-year reduction of the protected Austrian headcount.
