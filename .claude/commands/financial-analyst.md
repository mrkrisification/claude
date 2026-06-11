---
name: financial-analyst
description: "Research a company's financial and market profile from the web and store it in company-research/<slug>/ as structured JSON plus a narrative profile. Works for publicly listed companies (e.g. Deutsche Telekom) and unlisted subsidiaries (e.g. Magenta Austria). Pass the company name as the argument."
---

# Financial Analyst

Build and maintain a financial/market profile for a single company or subsidiary, sourced from the web. Stores structured data for reuse by other tools alongside a human-readable narrative profile.

## Storage layout

```
company-research/
  <company-slug>/
    profile.md            # narrative profile
    sources.md            # append-only source log
    raw/                  # archived primary-source documents (PDFs, reports)
      <YYYY-MM-DD>-<short-slug>.pdf
    data/
      overview.json       # identity, ownership, classification
      financials.json      # headline financials by period
      market.json          # valuation/market data + market position
```

`<company-slug>` = lowercase kebab-case of the company name (e.g. "Magenta Austria" → `magenta-austria`, "Deutsche Telekom" → `deutsche-telekom`).

`raw/` filenames use the **report's own publication date** (not today's date) plus a short descriptive slug, e.g. `2025-04-14-a1-hrvatska-annual-report-2024.pdf`, `2025-10-01-a1-group-q3-2025-earnings-update.pdf`.

---

## Workflow

### Step 1 — Resolve identity & load context

1. Derive `<company-slug>` from the argument.
2. If `company-research/<company-slug>/data/overview.json` exists, read it along with `financials.json` and `market.json` — this run is an incremental refresh, not a fresh build. Use the existing `entity_type`, `ticker`, `parent`, etc. as a starting point (verify/update rather than re-deriving from scratch).
3. If no prior data exists, this is a fresh build.
4. **Check history depth**: count the distinct annual (`FY*`) entries in `financials.json.periods` (zero if no prior data). If there are fewer than 3, this run needs a **history backfill**: research up to the last 2-3 fiscal years of financials and market position, not just the latest period. If 3 or more annual periods already exist, this run only needs the latest period (current incremental behavior).

### Step 2 — Classify the entity

Determine:
- `entity_type`: `"listed"` (has its own ticker/exchange), `"subsidiary"` (owned by a listed or larger parent, no own ticker), or `"private"`.
- For subsidiaries, identify the parent company — financial data will likely come from the parent's segment reporting / investor disclosures rather than standalone filings.

### Step 3 — Research (3 parallel agents)

Launch exactly 3 agents in parallel. Pass the company name, `entity_type` (best guess if unknown — let the agent confirm/correct it), parent company (if known/subsidiary), whether this run needs a **history backfill** (and which fiscal years to target if so), and any prior data as context. Each agent runs 2–3 web searches (more if backfilling, see below) and returns: URLs, publication dates, and key facts/figures. Instruct agents to be concise and to cite a source + date for every figure.

**Angle A — Financials & filings**
Search for: latest annual/quarterly revenue, EBITDA, EBITDA margin, net income, capex, with currency and period (e.g. FY2025, Q1 2026). For subsidiaries, search the parent's investor relations / segment reporting (e.g. "[parent] annual report [year] [subsidiary/country segment]"). For listed companies also search "[company] 10-K" / "[company] annual report [year]" / "[company] quarterly results [quarter] [year]". Skip full balance sheet and cash flow statement detail — headline P&L figures only.

If this run needs a **history backfill**, target the last 2-3 fiscal years (not just the latest), and prioritize the **parent company's annual reports and investor presentations** — these typically contain multi-year financial-highlights tables and country/segment breakdowns covering 3-5 years in one document. Use query variants like "[parent] annual report [year] financial highlights", "[parent] investor presentation [year] segment results [country/subsidiary]", "[parent] [year] annual report PDF". The agent should return direct URLs to these report/PDF documents specifically (not just news articles about them), so they can be archived as raw sources.

**Angle B — Market position & competition**
Search for: subscriber/customer counts, market share, sector trends, key competitors. Query variants: "[company] market share [country] [year]", "[company] subscribers [year]", "[sector] [country] competitors [year]". If the company is a telecom operator and `baselines/<country>/baseline.md` exists, read it for additional competitive context (do not duplicate research already covered there).

If this run needs a **history backfill**, also look for prior-year subscriber/market-share figures (last 2-3 years) to establish a trend, ideally from the same parent reports identified in Angle A.

**Angle C — Corporate structure, ownership & recent news**
Search for: ownership structure / parent company, recent M&A, leadership changes, strategic announcements from the last 12 months. Query variants: "[company] ownership structure", "[company] news [year]", "[company] CEO [year]", "[company] acquisition OR merger [year]". This angle is always a "last 12 months" snapshot — no backfill needed here.

For listed companies, Angle A also searches for current market cap, share price, P/E ratio, and EV/EBITDA (e.g. "[ticker] market cap", "[company] valuation [year]").

### Step 4 — Synthesize

Do not fetch additional URLs unless a search snippet references a primary source (annual report PDF, official filing) where the snippet alone is insufficient. Maximum 3 additional fetches for routine refresh runs; up to 5-6 for history-backfill runs (to accommodate retrieving multi-year parent reports).

Write output directly — do not create intermediate notes or planning documents.

1. **`data/overview.json`** — write/update:

```json
{
  "name": "Magenta Telekom",
  "legal_name": "T-Mobile Austria GmbH",
  "entity_type": "subsidiary",
  "ticker": null,
  "exchange": null,
  "parent": "Deutsche Telekom AG",
  "country": "Austria",
  "sector": "Telecommunications",
  "website": "https://www.magenta.at",
  "last_updated": "<today, YYYY-MM-DD>"
}
```

`ticker`/`exchange` are non-null only for `entity_type: "listed"`.

2. **`data/financials.json`** — merge new/updated periods into the `periods` array, matching on `period`. Mark `"estimated": true` when a figure is derived from segment reporting rather than a standalone statement. On a history-backfill run, add one entry per fiscal year found (e.g. FY2023, FY2024, FY2025) — don't fabricate years that couldn't be sourced; fewer than 3 years is fine if that's all that's available, with a note in `profile.md`'s "Data notes".

```json
{
  "currency": "EUR",
  "fiscal_year_end": "12-31",
  "periods": [
    {
      "period": "FY2025",
      "revenue_m": 1100,
      "ebitda_m": 400,
      "ebitda_margin_pct": 36.4,
      "net_income_m": null,
      "capex_m": 220,
      "as_of_date": "2026-02-15",
      "source": "Deutsche Telekom FY2025 segment report",
      "estimated": true
    }
  ],
  "last_updated": "<today, YYYY-MM-DD>"
}
```

3. **`data/market.json`** — `market_data` populated only for `entity_type: "listed"`; otherwise leave its fields `null`. `market_position` is populated for all entity types.

```json
{
  "market_data": {
    "market_cap_m": null,
    "share_price": null,
    "pe_ratio": null,
    "ev_ebitda": null,
    "as_of_date": null
  },
  "market_position": {
    "subscribers_m": 5.4,
    "market_share_pct": 28,
    "key_competitors": ["A1 Telekom Austria", "Drei (Hutchison)"],
    "notes": "..."
  },
  "last_updated": "<today, YYYY-MM-DD>"
}
```

4. **`profile.md`** — regenerate the full narrative:

```markdown
# <Company Name>

**Type:** <Listed | Subsidiary of <Parent> | Private> · **Country:** <country> · **Sector:** <sector>
**Last updated:** <YYYY-MM-DD>

## Overview
[2-4 sentences: what the company does, ownership structure, position in its market]

## Financial performance
| Period | Revenue (m) | EBITDA (m) | EBITDA margin | Net income (m) | Capex (m) | Source |
|---|---|---|---|---|---|---|
| FY2025 | 1,100 | 400 | 36.4% | n/a | 220 | DT FY2025 segment report (est.) |

## Market position
[Subscribers/customers, market share, key competitors, sector trends]

## Valuation
[For listed entities: market cap, share price, P/E, EV/EBITDA, as of date. For subsidiaries/private: state "Not applicable — <company> has no standalone listing."]

## Recent developments
[3-6 bullets: M&A, leadership, strategy, last ~12 months, each with source + date]

## Data notes
[Call out any figures that are estimated/derived from parent segment reporting, any gaps where standalone data isn't disclosed, and any conflicting figures found across sources. If a history backfill was performed in this run, note which fiscal years were added and which reports they came from.]
```

5. **Archive raw sources**: for each `[PRIMARY]` document used as a source for financial or market figures (annual report PDF, investor presentation, segment report), fetch it and save a copy into `company-research/<company-slug>/raw/` using the `<YYYY-MM-DD>-<short-slug>.<ext>` naming convention (date = the report's own publication date). If a PDF can't be downloaded directly (paywalled, JS-rendered), save the fetched page content as `.md` instead, or skip it and note in `sources.md` that no raw copy was archived. Cap raw downloads at ~4-5 documents per run.

6. **`sources.md`** — append a dated section (create the file if it doesn't exist):

```markdown
## <YYYY-MM-DD>

### Financials & filings
- [PRIMARY] [Title](URL) — Publisher, YYYY-MM-DD (raw/<filename>)

### Market position & competition
- [Title](URL) — Publisher, YYYY-MM-DD

### Corporate structure, ownership & news
- [Title](URL) — Publisher, YYYY-MM-DD
```

Mark official filings, annual reports, and press releases with `[PRIMARY]`. Do not include URLs that returned no usable content. Where a `[PRIMARY]` document was archived to `raw/` in step 5, append the relative path in parentheses as shown above.

### Step 5 — Report back

Give the user a short summary (5-8 sentences): entity classification, headline financial figures with period (and trend across years if a backfill was done), market position highlights, and any notable data gaps or estimates (especially relevant for subsidiaries without standalone disclosures). Point to the `company-research/<company-slug>/` directory for the full output.

---

## Tone and constraints

- Cite every figure with a source and date. If a figure can't be sourced, mark it `null` and explain in "Data notes" rather than guessing.
- For subsidiaries, be explicit when financials are derived/estimated from parent disclosures rather than standalone statements.
- Keep `profile.md` focused — this is a reference document, not a research log. Each refresh regenerates it from current data.
- On refresh runs, preserve `periods` history in `financials.json` (append/update, never drop prior periods) and append (never overwrite) `sources.md`.
- New companies (and companies with fewer than 3 annual periods of history) get a one-time history backfill targeting 2-3 fiscal years; once that history exists, subsequent runs are incremental (latest period only).
