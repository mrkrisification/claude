# Telemach Croatia — raw capture manifest

Telemach Croatia is a **private** operator inside United Group. Its parent gives no investor-relations
disclosure for Croatia — BUT, as a Croatian **d.o.o.**, Telemach Hrvatska files **statutory annual
accounts publicly** with FINA (the company registry), which DO give standalone revenue / EBITDA / net
profit (S03). The parent press releases (S01/S02) add only group-level context. Subscriber/market-share
metrics still come from the **HAKOM** shared regulator cache (`_regulators/hakom/`).

| source_id | date | publisher | title | period | file |
|---|---|---|---|---|---|
| S01 | 2024 | United Group B.V. | United Group continues successful growth path in 2023 with record results | FY2023 (group) | 2026-06-15-united-group-b-v-continues-successful-growth-path-in-2023-with-record-results.md |
| S02 | 2025-11 | United Group B.V. | United Group continues to deliver strong growth in the third quarter of 2025 | Q3-2025 / LTM (group) | 2026-06-15-united-group-b-v-continues-to-deliver-strong-growth-in-the-third-quarter-of-2025.md |
| S03 | 2026 | FINA Info.BIZ (Croatian company registry) | Telemach Hrvatska d.o.o. — statutory annual accounts (OIB 70133616033) | FY2025 (+FY2024 implied) | 2026-06-15-fina-telemach-hrvatska-financials.md |
| S04 | 2025-10-31 | poslovni.hr / SeeNews (FINA-derived) | Top-505: Telemach Hrvatska statutory revenue/employees, multi-year | FY2024, FY2023 | 2026-06-15-telemach-multiyear-registry-press.md |
| S05 | 2025 | ictbusiness.info (FINA-derived) | TOP 100 ICT — Telemach #10 by profit (FY2023 loss → FY2024 €9.3m) | FY2024, FY2023 | 2026-06-15-telemach-multiyear-registry-press.md |

**Provenance note:** S01/S02 are *group-level* (all of United Group); recorded under `parent_group_*`
metric names so they cannot be mistaken for Telemach Croatia's own figures. **S03 is the standalone
legal-entity disclosure** (`basis=standalone`) — the real Telemach Hrvatska financials.
