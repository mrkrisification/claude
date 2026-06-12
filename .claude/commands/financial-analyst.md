---
name: financial-analyst
description: "Financial analyst for a single telecom operator. Builds and refreshes a per-company financial/market profile — works for listed groups (Deutsche Telekom) and, crucially, for unlisted subsidiaries (A1 Croatia, Magenta Austria, Telemach) whose figures must be assembled from the parent's segment reporting, enriched with regulator data, and only as a last resort from press/web. Run when asked to analyze a telco's financials, build a company financial profile, or research an operator's numbers. Pass the company name as the argument."
---

# Telco Financial Analyst

Build a machine-readable financial/market profile for one telecom operator. **Collect the
source documents first into a `raw/` archive; compose datasets only from what was collected.**
Every figure must trace to a collected source — never invent a number that is not in `raw/`.

The hard case this skill exists for: **unlisted subsidiaries**. They have no standalone filing,
so their numbers come from a patchwork — the parent's segment reporting, the local regulator, and
(last resort) press. Conflicting numbers are expected; the design keeps them, with provenance,
rather than silently picking one.

---

## Configuration

### Output tree (per company, at repo root)

```
company-research/<company-slug>/
  raw/                              # COLLECTED documents — immutable, populated FIRST
    YYYY-MM-DD-<source-slug>.md     # one file per source: metadata header + extracted text
    manifest.md                     # index of every raw capture (see schema below)
  data/
    profile.json                    # identity, ownership, entity_type, parent, regulators,
                                    #   competitors, market position (nested)
    financials.csv                  # tidy/long P&L time-series (see schema below)
    market.csv                      # subscribers / share / ARPU time-series (see schema below)
  company-summary.md                # regenerated narrative + "Data confidence & gaps" section
  sources.md                        # append-only dated source log, [PRIMARY] markers, source_id keys
```

`<company-slug>`: lowercase, spaces→hyphens, drop punctuation (e.g. `A1 Croatia` → `a1-croatia`).

### Entity-type depth matrix

Classification drives ambition. Do not chase data the entity does not disclose.

| `entity_type` | Primary sources to seek | Metrics to compose | Acceptable gaps |
|---|---|---|---|
| `listed` | Own annual report, 20-F, quarterly results, data book | Full P&L (revenue, EBITDA, margin, net income, capex), 3-yr history | few |
| `subsidiary` | **Parent segment reporting**, parent data book, regulator market reports, securities-authority filings | Revenue, EBITDA, margin, subscribers, market share (segment-derived → `estimated=true`); net income / capex best-effort | net income, capex, sub-segment detail |
| `private` | **Bondholder reports** (groups that issue Eurobonds, e.g. United Group), regulator reports, press | Snapshot: revenue/EBITDA/subscribers where disclosed | most period detail |

For a subsidiary, **the parent's segment reporting is the realistic ceiling** of standalone data.
Scope to that; flag the rest as a gap rather than guessing.

### Known parents & regulators (reuse existing repo knowledge)

When the company is one of the operators already tracked in `baselines/<country>/baseline.md`,
read that baseline first — it maps owner and regulator and saves a discovery pass. Reference:

| Group | Subsidiaries (examples) | Disclosure vehicle |
|---|---|---|
| A1 Group (Telekom Austria) | A1 Austria, A1 Croatia, A1 Bulgaria, A1 Slovenia, A1 Serbia, A1 Macedonia, A1 Belarus | Group report has **per-country segment tables** |
| Deutsche Telekom | Magenta Austria; via Magyar Telekom → Hrvatski Telekom (HT), Makedonski Telekom | Group + Magyar Telekom segment reporting |
| United Group (private) | Telemach (SI/HR/BA), Vivacom (BG) | **Bondholder / consolidated reports** |
| e& / PPF Telecom | Yettel (BG/RS/HU) | PPF Telecom Group reports |
| CK Hutchison | Drei (Austria) | Group results |
| Turkcell | life:) / BeST (Belarus) | Group results |

Regulators (market reports, KPIs, decisions): **RTR** (AT), **HAKOM** (HR), **RATEL** (RS),
**AKOS** (SI), **AEK** (MK), **CRC** (BG), **MinCom/BeIGIE** (BY). Securities/market authorities:
**HANFA** (HR). These are `[PRIMARY]` sources.

### Collection engine — Firecrawl

Document collection in this environment is the known failure point: `WebFetch` and Bash `curl`
are blocked (403 / egress allowlist) for most operator, newswire, and regulator sites. The
configured collection engine is **Firecrawl** — a hosted scraper (real browser + residential IP)
that fetches server-side, defeating Cloudflare. The API key lives in `.env` as `FIRECRAWL_API_KEY`
(git-ignored).

Call Firecrawl via its REST API with `curl`. Load the key first:
```bash
set -a; . ./.env; set +a   # exports FIRECRAWL_API_KEY
```

**Discover** document URLs (`/v2/search`, returns results + optional scraped content):
```bash
curl -sS -m 60 -X POST https://api.firecrawl.dev/v2/search \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"A1 Group FY2024 segment results Croatia EBITDA","limit":5,
       "scrapeOptions":{"formats":["markdown"]}}'
```

**Scrape** a known URL into clean markdown (`/v2/scrape`) — this is how `raw/` captures are filled:
```bash
curl -sS -m 120 -X POST https://api.firecrawl.dev/v2/scrape \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" \
  -d '{"url":"<doc-url>","formats":["markdown"]}'   # PDF/HTML both supported
```
Extract `.data.markdown` (e.g. with `jq -r '.data.markdown'`) and write it into the `raw/` capture.

**Preflight.** Before relying on Firecrawl, confirm reachability once:
```bash
set -a; . ./.env; set +a
curl -sS -m 20 -o /dev/null -w '%{http_code}' -X POST https://api.firecrawl.dev/v2/scrape \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" \
  -d '{"url":"https://firecrawl.dev","formats":["markdown"]}'
```
If this returns `Host not in allowlist` / a non-200, Firecrawl is unreachable from this
environment — **`api.firecrawl.dev` must be added to the network egress allowlist** (see
`company-research/README.md`). In that case **do not abort**: fall back per Phase 1.4 and flag the
degradation prominently.

(If a Firecrawl MCP or other scraper MCP is also present — locate it via `ToolSearch` keywords
`firecrawl`, `scrape`, `crawl` — you may use it instead of the REST calls; the rest of the
workflow is unchanged.)

---

## Workflow

Run the phases in order. **Do not start Phase 2 until Phase 1 collection is reported.**

### Phase 0 — Resolve & classify

1. Derive `<company-slug>`. Create `company-research/<company-slug>/raw/` and `.../data/`.
2. Classify `entity_type` (`listed` / `subsidiary` / `private`).
3. Identify the ultimate parent and the relevant regulator(s). If the operator appears in
   `baselines/`, read its baseline to pull owner + regulator directly.
4. List discovery targets in priority order: parent annual report & **segment reporting**, parent
   investor presentation / data book, bondholder reports (private groups), regulator market
   reports, securities-authority filings, then press.

### Phase 1 — COLLECT into `raw/` (do NOT compose datasets yet)

1. **Discover** exact document URLs with `WebSearch`. Force depth with targeted queries, not one
   shallow pass — e.g. `"<parent> segment results <subsidiary> EBITDA FY<year>"`,
   `"<parent> data book <year> filetype:pdf"`, `"<regulator> <country> mobile market report <year>"`,
   `site:<parent-ir-domain> <subsidiary>`. Aim for the multi-year segment tables that exist in
   parent annual reports / investor presentations, not just the latest press release.
2. **Fetch & archive** each target with Firecrawl `/v2/scrape` (or a scraper MCP if present). For
   every captured source, write `raw/YYYY-MM-DD-<source-slug>.md` with this header, then the
   extracted markdown:

   ```markdown
   ---
   source_id: S01
   title: <document title>
   publisher: <issuer / outlet>
   url: <url>
   doc_date: <YYYY-MM-DD or YYYY>
   collected: <today YYYY-MM-DD>
   fetch_method: firecrawl | mcp:<server> | local-file | search-snippet
   primary: true | false
   ---

   <extracted markdown — preserve tables/figures; trim navigation/boilerplate>
   ```

   `primary: true` for filings, segment reports, regulator notices, bondholder reports, official
   press releases. Assign `source_id` sequentially (`S01`, `S02`, …) — it is the join key used
   everywhere downstream.
3. **Local files.** If the user has placed source documents in the uploads area or committed them
   under `raw/`, `Read` them (the Read tool parses PDFs natively) and write a `raw/` capture with
   `fetch_method: local-file`. Prefer these — they are genuine primary documents.
4. **Fallback** (Firecrawl unreachable — e.g. `api.firecrawl.dev` not allowlisted — or a scrape
   fails and no local file exists): store the `WebSearch` result content as a `raw/` capture with
   `fetch_method: search-snippet`, `primary: false`. These are lower-confidence and must be
   flagged as such downstream.
5. **Write `raw/manifest.md`** — one table row per capture:

   ```markdown
   # Raw source manifest — <Company>

   | source_id | title | publisher | doc_date | fetch_method | primary | file |
   |---|---|---|---|---|---|---|
   | S01 | ... | ... | ... | firecrawl | true | 2026-06-12-a1-group-fy2024-segment.md |
   ```
6. **Collection report (to the user, in chat).** State: # primary vs # secondary captures, and
   **which targets could not be collected** (e.g. "HAKOM FY2024 market report — 403, no scraper
   MCP configured"). Make gaps explicit here — do not discover them silently at compose time.

### Phase 2 — COMPOSE datasets (from `raw/` only)

Extract figures **exclusively** from `raw/` captures. Every value carries a `source_id`.

**`data/profile.json`**
```json
{
  "company": "A1 Croatia",
  "slug": "a1-croatia",
  "entity_type": "subsidiary",
  "country": "Croatia",
  "parent": { "name": "A1 Group (Telekom Austria)", "ownership_pct": 100 },
  "regulators": ["HAKOM", "HANFA"],
  "competitors": ["Hrvatski Telekom", "Telemach Croatia", "Tele2 Croatia"],
  "market_position": { "summary": "convergent cable+mobile #2", "sources": ["S03"] },
  "last_updated": "2026-06-12"
}
```

**`data/financials.csv`** — long/tidy, one row per period×metric:
```
period,metric,value,currency,unit,basis,estimated,source_id,is_preferred,note
FY2024,revenue,512,EUR,m,segment,true,S01,true,
FY2024,ebitda,189,EUR,m,segment,true,S01,true,parent segment table
FY2024,ebitda,188,EUR,m,segment,true,S07,false,local press; conflicts with S01
FY2024,ebitda_margin,36.9,,pct,segment,true,S01,true,
```
- `basis` ∈ `consolidated | segment | standalone`.
- `estimated=true` for any parent-segment-derived figure (retro convention).
- **Conflicting numbers → separate rows**, distinct `source_id`. Mark the chosen one
  `is_preferred=true`; explain the call in `note`. Never silently drop a conflicting value.

**`data/market.csv`**:
```
period,metric,segment,value,unit,source_id,estimated
FY2024,mobile_subscribers,mobile,2.1,m,S03,false
Q1-2026,mobile_market_share,mobile,20,pct,S03,false
FY2024,arpu,mobile,11.2,EUR,S01,true
```

Honor the **entity-type depth matrix**: do not fabricate net income / capex rows for a subsidiary
that does not disclose them — leave them out and record the gap in the summary.

### Phase 3 — Summarize & log

1. **`company-summary.md`** — regenerated narrative. End with a required section:

   ```markdown
   ## Data confidence & gaps
   - **Conflicts:** FY2024 EBITDA reported as €189m (S01, parent) vs €188m (S07, press) — preferred S01.
   - **Missing:** standalone net income, capex (not disclosed at subsidiary level).
   - **Confidence:** 4 primary captures, 2 search-snippet (lower confidence). No scraper MCP — flagged.
   ```
2. **`sources.md`** — append a dated block, deduplicated, keyed by `source_id`, `[PRIMARY]` marked:

   ```markdown
   ## 2026-06-12 — A1 Croatia

   - [S01] [PRIMARY] [A1 Group FY2024 Results — segment reporting](URL) — A1 Group IR, 2025-02
   - [S03] [PRIMARY] [HAKOM mobile market report Q1 2026](URL) — HAKOM, 2026
   - [S07] [Local press on A1 Croatia FY2024](URL) — Outlet, 2025-03
   ```

### Phase 4 — Optional PDF (only if the user asks)

Reuse the telecom-pulse export: write a self-contained HTML brief, convert with
`python3 -m weasyprint <html> <pdf>`, send with `SendUserFile`, delete the HTML.

---

## Refresh behavior

Re-running for an existing company is incremental: add **new** `raw/` captures (new `source_id`s,
never overwrite existing ones), add/update dataset rows, regenerate `profile.json` and
`company-summary.md`, and append (never rewrite) `sources.md`. `raw/` is immutable history.

---

## Tone and constraints

- Cite every figure to a `source_id`. If a number is not in a `raw/` capture, it does not go in the dataset.
- Prefer PRIMARY (filings, segment reports, regulator, bondholder reports) over press.
- Keep conflicting values; never silently pick. Mark the preferred one and explain.
- State gaps plainly. For subsidiaries, an honest "not disclosed" beats a fabricated estimate.
- Collect first, compose second. Report collection (incl. failures) before composing.
