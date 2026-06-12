# Raw source manifest — IFT (Instituto Federal de Telecomunicaciones, Mexico)

Shared regulator cache — collected once and reusable by every Mexican operator profile (e.g.
`america-movil`). Collected 2026-06-12 by `report_watcher.py regulator ift --max-years 5` (free
direct download; two-hop discovery through the report detail pages). These are `[PRIMARY]` market
sources.

| source_id | title | publisher | doc_date | fetch_method | primary | file |
|---|---|---|---|---|---|---|
| R01 | Indicadores de Mercado y la Economía Digital 2025 | IFT | 2025 | direct | true | 2026-06-12-cindicadores2025.pdf |
| R02 | Indicadores de Mercado y la Economía Digital 2024 | IFT | 2024 | direct | true | 2026-06-12-cindicadores2024.pdf |
| R03 | Indicadores de Mercado y la Economía Digital 2023 | IFT | 2023 | direct | true | 2026-06-12-cindicadores2023pdf.pdf |
| R04 | Informe Estadístico Trimestral 1T2022 | IFT | 2022 | direct | true | 2026-06-12-ite1t2022acc.pdf |
| R05 | Informe Estadístico Trimestral 2T2022 | IFT | 2022 | direct | true | 2026-06-12-ite2t2022acc.pdf |
| R06 | Informe Estadístico Trimestral 3T2022 | IFT | 2022 | direct | true | 2026-06-12-ite3t2022acc.pdf |

_Annual market reports (R01–R03, `Indicadores de Mercado y la Economía Digital`) are the primary
full-market series — they cover **every** Mexican operator (subscribers, share, ARPU, penetration),
the backbone for a country market overview. Known gaps to harden next: quarterly coverage is stale
(only 1T–3T 2022 reached — the listing's recent-quarter detail pages weren't followed), and two-hop
discovery is non-deterministic across runs. Collected reports are intact regardless (ledgered)._
