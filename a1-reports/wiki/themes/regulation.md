# Regulation across the footprint

Regulation is the most persistent *structural* pressure on A1 Group's revenue and
margins — a counterweight that has run beside the growth from CEE M&A and 5G/fibre
for the company's entire listed life. From the 1998 liberalisation of the Austrian
monopoly to the 2024 Belarus dividend freeze, almost every annual report carries a
dedicated **"Regulation" / "Regulatory Decisions"** section in its management report;
this page is the cross-year synthesis of what those sections say. Where a report
quantifies a regulatory hit, the figure is cited inline; numeric series live in
`data/financials.duckdb`.

> **Sourcing convention.** `(reports/<year>, p<page>)` where the annual report carries
> the point (page = the PDF page in `pdfs/`); `[EXT]` only where the reports are silent.
> Spectrum *policy* is noted here but the auction *costs* live in
> `themes/spectrum-auctions.md`. The civil-servant constraint links to
> `themes/spinoffs-and-restructuring.md` and `metrics/ebitda.md`.

## The recurring levers
1. **Liberalisation & asymmetric (incumbent) regulation** — the structural start
   point (TKG 1997/1998 → TKG 2003 → TKG 2021/EECC).
2. **Termination rates (MTR & FTR)** — regulated interconnection cuts, a steady
   revenue drag from the late-2000s, ending in EU-uniform near-zero rates (2022–24).
3. **Roaming** — EU retail caps → "Roam-like-at-home" (15 June 2017) → 2022 extension
   to 2032; plus the Western Balkans regional deal.
4. **SMP / wholesale access** — market analyses, unbundling → bitstream → VULA →
   full Austrian wholesale deregulation (2022).
5. **Country-specific / geopolitical** — Belarus hyperinflation (2011) and the
   **dividend-payment freeze (since Q2 2024)**.
6. **The civil-servant constraint** — a labour/legal lever unique to the privatised
   Austrian incumbent.

## Chronological table — the spine

| Year | Regulatory change | Market | Effect | Source |
|------|-------------------|--------|--------|--------|
| 1998 | Full **liberalisation** (TKG 1997, 1 Jan 1998); Telekom-Control-Kommission sets first interconnection/termination rates | Austria | incumbent opened; competition-oriented rates | (reports/1998, p13) |
| 1999 | **Local-loop unbundling** decree (Jul), **Universal Service Regulation** (Jun), carrier pre-selection & number portability; mobilkom declared dominant — first cost-based **mobile** termination rate in Europe | Austria | asymmetric regulation tightened; lowest EU mobile interconnect | (reports/1999, p42–43) |
| 2000 | ISPs win same "last-mile" access terms as fixed operators (May); ~1,000 unbundled lines by year-end; mgmt calls for shift from **ex-ante to ex-post** retail-tariff regulation | Austria | unbundling ramp; incumbent lobbies for lighter touch | (reports/2000, p22) |
| 2001 | TA re-confirmed **SMP** in fixed voice, leased lines, interconnection; sub-loop unbundling + line-sharing added; monthly local-loop fee cut €11.6→€10.9 (2002) | Austria | wholesale price glide begins | (reports/2001, p24) |
| 2003 | **Telecommunications Act 2003** (EU framework) redefines market into **18 sub-markets**; SMP market analyses begin; mobilkom MTR cut −3.5% to **€0.1086/min**; mobile number portability mandated | Austria | reshaped SMP/access obligations | (reports/2003, p37, p56) |
| 2005 | Market analyses completed (17 markets); unbundling fee −1.8% to €10.7; **"naked ADSL" wholesale** made compulsory; USO co-financing cuts TA contribution ~€1.0 m | Austria | broadband wholesale opened | (reports/2005, p35, p55) |
| 2007 | **EU retail roaming caps** (Roaming Reg I) in force from end-June 2007 | EU footprint | cut wholesale + retail roaming prices | (reports/2008, p46) |
| 2008 | Roaming Reg I applies for the full year — **negative roaming-revenue impact**; Austrian residential-call market deregulated (deemed competitive) | Austria + EU | first full-year roaming drag | (reports/2008, p46) |
| 2009 | **Roaming Reg II** (18 Jun 2009→2012): voice/SMS/data cap glide, data wholesale €1/MB; fixed-net interconnect ruling; partial **deregulation** of residential wholesale broadband (fixed-mobile substitution recognised) | Austria + EU | first detailed roaming glide; unique partial deregulation | (reports/2009, p52–53) |
| 2009 | CEE MTR glide paths begin: **Croatia** + 6% mobile levy; **Bulgaria** number portability + MTR glide; **Serbia** 10% mobile levy; **Slovenia** harmonise MTR; **Belarus** interconnect via state BelTelekom | CEE/SEE | country-by-country MTR drag | (reports/2009, p53) |
| 2010 | Roaming Reg II annual cuts; Austrian fixed+mobile merge into **A1 Telekom Austria**; Serbia mobile levy abolished (Jan 2011) | Austria + EU | MTR + roaming cuts hit all segments | (reports/2010, p17) |
| 2011 | **TKG amendment** (21 Nov; rule-making moved to **RTR**); **VULA** ("virtual unbundling") first published; CEE MTR cuts (Bulgaria, Slovenia, Macedonia); Serbia SMP + portability; **Belarus under IAS 29 hyperinflation** | Austria + CEE | MTR/roaming cuts + Belarus restatement | (reports/2011, p50–52) |
| 2012 | **Roaming Reg III** (1 Jul): structural "choose-your-roaming-provider" + new caps; FTR draft cut to **0.122c/min**; MTR Austria uniform **0.80c** from Q1 2013; **Bulgaria** MTR 6.39→2.70c; consumer cost-containment ordinances | Austria + EU | "more than halved" Bulgarian termination | (reports/2012, p54–56) |
| 2013 | **MTR glide-path table** (Austria 2.01→**0.8049c** from Nov; CEE cuts); FTR Austria 0.82c→**0.137c**; Croatia joins EU (1 Jul) → EU roaming/term. rules; full EU roaming retail glide; €1.03 bn spectrum auction (see spectrum) | Austria + CEE | year-by-year MTR drag quantified | (reports/2013, p84–86) |
| 2014 | MTR cuts continue (Bulgaria, Croatia, Serbia); TKK ruling (28 Jul) deregulates leased-line/Ethernet in 359 municipalities but obliges **dark-fibre** leasing in rural areas | Austria + CEE | wholesale rebalancing | (reports/2014, p81) |
| 2016 | **Net-neutrality + roaming Regulation (EU) 2015/2120** in force; **abolition of retail roaming surcharges set for 15 June 2017**, transition surcharge from 30 Apr 2016; MTR glide-paths continue | Austria + EU | "negative impact on current and future roaming revenues" | (reports/2016, p46–47) |
| 2017 | **RLAH implemented (15 Jun 2017)** — retail roaming surcharges abolished (AT/BG/HR/SI); **EECC** draft introduced; wholesale roaming glide | Austria + EU | sustained negative roaming-revenue impact | (reports/2017, p48–49) |
| 2018 | **GDPR** in force 25 May; **EECC directive issued Dec** (transpose by end-2020); intra-EU call cap (€0.19/min) from 15 May 2019; net-neutrality decisions appealed; **SOX** via AMX NYSE listing | Austria + EU | new data-protection + intra-EU-call drag | (reports/2018, p5–6, p29, p31) |
| 2019 | **Western Balkans regional roaming agreement** (1 Jul; surcharges gone by 1 Jul 2021); EECC to set a **single low EU MTR/FTR** from 2021; **IFRS 16**; 5G spectrum | EU + SEE | further MTR/FTR cuts flagged | (reports/2019, p6–7, p27) |
| 2020 | **EU Delegated Regulation (21 Dec)**: single EEA **FTR €0.0007/min from 1 Jan 2022** and single **MTR €0.002/min from 1 Jan 2024** (glide); new Austrian **TKG** drafted; **COVID-19** "dramatic reduction in roaming revenues" | Austria + EU | EU-uniform termination set; COVID roaming hit | (reports/2020, p61–63) |
| 2021 | New Austrian **TKG in force 1 Nov** (transposes EECC); EU MTR glide to **€0.0055** (Jan 2022); Austrian wholesale-broadband deregulation in progress; Western Balkans surcharges eliminated | Austria + EU | TKG/EECC implemented | (reports/2021, p61–62) |
| 2022 | **Full deregulation of Austrian wholesale broadband (11 Oct)** → voluntary **VULA 2.0 / VHCN**; single EU FTR €0.0007 live; single EU MTR €0.002 from Jan 2024 (glide); **revised EU Roaming Reg extends RLAH to 2032** | Austria + EU | wholesale deregulation; CPI price indexation offsets drag | (reports/2022, p6–7) |
| 2023 | Austrian high-quality-access (Ethernet/dark-fibre) market analysis completed (Aug) — deregulated in many municipalities, still regulated rurally; smaller ISPs appeal the 2022 deregulation | Austria + EU | wholesale deregulation broadens | (reports/2023, p6–7) |
| 2024 | **Belarus dividend-payment restrictions** introduced **Q2 2024** (dividends to EU/"unfriendly"-country investors blocked); **Gigabit Infrastructure Act** (May) extends intra-EU call cap; Serbia MTR glide | Belarus + EU | cash trapped at the Belarus opco | (reports/2024, p5–6, p25, p28) |
| 2025 | Belarus dividend restrictions **persist** (cash held with local Belarus banks); EU **Digital Networks Act (DNA)** proposal; EU **roaming area extended to Ukraine & Moldova from Jan 2026** | Belarus + EU | standing geopolitical overhang; framework reform ahead | (reports/2025, p5–6, p23, p26) |

## Termination rates (MTR & FTR)

The longest-running drag in the data. Austria's MTR fell from **€0.0201/min** (2011–12)
to a uniform **€0.008049** in Nov 2013, then — once the EECC supplanted national market
analyses — to the **EU-wide €0.0055 (2022) → €0.004 (2023) → €0.002 (2024)** glide,
after which the Austrian regulator **deregulated the national MTR market** entirely
(reports/2013, p85; reports/2022, p7; reports/2024, p6). The reports print full
**per-country glide-path tables** every year from 2013 — e.g. Bulgaria MTR 6.39→2.70c
during 2012, Macedonia cut in 2013 (reports/2012, p56; reports/2013, p85). **FTR** was
cut from Austria's 0.82c to **0.137c** in 2013 (with origination raised in compensation,
a European first) and then set to the EU-uniform **€0.0007/min from 1 Jan 2022**
(reports/2013, p84; reports/2022, p6). Belarus, Serbia and North Macedonia (non-EU)
keep nationally-set rates throughout (reports/2025, p6). *(The 2013 Austrian MTR of
0.008049 €/min matches the per-country MTR table in the analyst factsheets.)*

## Roaming

EU roaming regulation steps through three named regulations — **Reg I (end-June 2007),
Reg II (18 Jun 2009), Reg III (1 Jul 2012)** — each cutting retail and wholesale caps,
quantified in the reports' glide-path tables (reports/2008, p46; reports/2009, p53;
reports/2013, p81). The culmination is **"Roam-like-at-home" (RLAH) — abolition of
retail roaming surcharges on 15 June 2017** under Regulation (EU) 2015/2120, preceded
by a transition regime from 30 April 2016; the reports flag **retail-roaming revenue
losses already in 2016** and a "sustained negative impact on roaming revenues"
thereafter (reports/2016, p46–47; reports/2017, p49). The **2022 revised Roaming
Regulation extended RLAH to 30 June 2032** with declining wholesale caps (reports/2022,
p7). Beyond the EU, a **Western Balkans regional roaming agreement (1 Jul 2019)**
eliminated surcharges among the region's countries by mid-2021, and from **January 2026**
the EU roaming area extends to Ukraine and Moldova (reports/2019, p6; reports/2025, p6).
**COVID-19** caused a "dramatic reduction in roaming revenues" in 2020–21 — a
non-regulatory shock layered on top of RLAH (reports/2020, p62).

## SMP, wholesale access & the liberalisation framework

The Austrian incumbent has been a **significant-market-power (SMP)** operator in fixed
voice, leased lines and interconnection since liberalisation, and the access remedy has
migrated up the technology stack: **local-loop unbundling (1999)** → sub-loop /
line-sharing (2001) → **"naked ADSL" wholesale (2005)** → **VULA / virtual unbundling
(2011–12)**, where A1 was, besides BT, the only European operator to offer it as part of
NGA rollout (reports/1999, p42; reports/2001, p24; reports/2005, p55; reports/2012, p54).
The defining framework steps are **TKG 1997/98**, the **TKG 2003** (18 sub-markets, EU
framework), the **2011 TKG amendment** (powers moved to RTR), and the fully-revised **TKG
of 1 Nov 2021** transposing the **EECC** (reports/2003, p37; reports/2011, p50;
reports/2021, p62). The arc ends in **deregulation**: the Austrian regulator **fully
deregulated wholesale broadband on 11 October 2022**, replacing it with voluntary **VULA
2.0 / VHCN** commercial contracts, and in **August 2023** deregulated high-quality
(Ethernet/dark-fibre) access in many municipalities — though A1 stays regulated in rural
regions, and some smaller ISPs have appealed the 2022 decision (reports/2022, p6;
reports/2023, p6). Universal-service, interconnection, number-portability and
carrier-(pre)selection rules recur from the earliest reports (reports/1999, p42–43;
reports/2009, p53).

## Data protection & net neutrality

Net neutrality entered via **Regulation (EU) 2015/2120** (in force 2016); A1 Telekom
Austria appealed **two Austrian regulator decisions** on net neutrality at the Federal
Administrative Court, proceedings pending across 2018–2021 (reports/2016, p46;
reports/2018, p5; reports/2021, p62). BEREC and the Commission later judged the regime
adequate, with no amendment needed (reports/2022, p7; reports/2023, p7). **GDPR** has
been in force since **25 May 2018**; the reports treat GDPR breaches as a "considerable
legal and financial" data-protection risk (reports/2018, p29). Consumer-protection rules
— the 2012 cost-containment and contract-change ordinances, the intra-EU call cap
(€0.19/min, €0.06/SMS from 15 May 2019, extended via the 2024 **Gigabit Infrastructure
Act** toward a national-price level by 2029) — are the recurring retail-conduct layer
(reports/2012, p54; reports/2024, p6).

## CEE / SEE country-specifics — incl. Belarus

The footprint splits into EU/EEA markets (Austria, Bulgaria, Croatia, Slovenia — under
EU roaming/termination rules) and **Belarus, Serbia, North Macedonia**, where frameworks
"are at different stages of development" but gradually converge on EU norms (reports/2016,
p46). Concrete national levers in the reports: a **6% Croatian mobile levy** (2009–2012),
a **10% Serbian mobile levy** (2009, abolished Jan 2011), and Serbian **SMP designation**
of all mobile operators (2011) (reports/2009, p53; reports/2011, p51; reports/2010, p17).
**Belarus** carries the heaviest country-specific load: classified a **hyperinflationary
economy under IAS 29 from December 2011** (restating the segment), and — the current
standing overhang — **temporary restrictions on dividend payments to EU/"unfriendly"-country
investors introduced by the Belarusian government in Q2 2024**, which trap cash at the
velcom/A1 Belarus operation. The reports note the restriction forces A1 to hold cash with
**local Belarusian banks** and that it remained effective through FY2025 (reports/2011,
p52; reports/2024, p25, p28; reports/2025, p23, p26).

## Fines, antitrust & competition-authority actions

Reported competition-authority activity is modest. The Croatian antitrust authority
opened **price-fixing proceedings against all three Croatian mobile operators**
(including A1's Vipnet) after the 2012 mobile-levy reintroduction (reports/2011, p51).
The reports otherwise note that A1 and its subsidiaries are routinely "party to a number
of legal proceedings … with public authorities, competitors and other parties"
(reports/2018, p31). The Austrian Federal Competition Authority is named as a
**co-monitor of the post-2022 wholesale deregulation**, not as an enforcer against A1
(reports/2022, p6).

## The civil-servant constraint (Austria)

Unique among telcos, the privatised Austrian incumbent inherited **civil servants
allocated to it under the 1996 Postal-Services Structure Act (Poststrukturgesetz)**,
employed under public law and whose contracts **cannot be unilaterally terminated**. As
of FY2018 they were **~45% of the Austria segment and ~19% of group headcount**
(reports/2018, p31). Reducing this protected headcount is only possible through expensive
**social plans** or **transfers to government ministries** — the mechanism behind the
**€632 m FY2008 Fixed-Net restructuring charge** and the smaller social-plan offers that
recur through the 2010s, and the reason `ebitda` and `ebitda_excl_restructuring` diverge
so often (the adjustment explicitly captures "future expenses for civil servants who no
longer provide services … but whose employment contracts cannot be terminated")
(reports/2011, p52; reports/2013, p86). This is a labour/legal constraint, not a telecom
rule, but it is the standout incumbent-specific overhang — see
`themes/spinoffs-and-restructuring.md` and `metrics/ebitda.md`.

## See also
- `themes/spectrum-auctions.md` — spectrum policy (caps/coverage obligations) is the
  cost side of regulation; the 2013 €1.03 bn auction sits there.
- `metrics/ebitda.md` — the restructuring/EBITDA mechanics driven by the civil-servant
  constraint.
- `metrics/revenue.md` — where the MTR/roaming drag lands in the top line.
- `themes/spinoffs-and-restructuring.md` — the 2008/2011 social-plan restructurings.
- Year notes: `reports/2008` (civil-servant charge), `reports/2013` (MTR/FTR tables +
  spectrum), `reports/2016`–`reports/2017` (RLAH), `reports/2021` (TKG/EECC),
  `reports/2024`–`reports/2025` (Belarus dividend freeze).
