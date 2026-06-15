---
name: financial-analyst
description: "Financial analyst for a single telecom operator. Builds and refreshes a per-company financial/market profile — works for listed groups (Deutsche Telekom) and, crucially, for unlisted subsidiaries (A1 Croatia, Magenta Austria, Telemach) whose figures must be assembled from the parent's segment reporting, enriched with regulator data, and only as a last resort from press/web. Run when asked to analyze a telco's financials, build a company financial profile, or research an operator's numbers. Pass the company name as the argument."
---

# Telco Financial Analyst

Build a machine-readable financial/market profile for one telecom operator. **Collect the
source documents first into a `raw/` archive; compose datasets only from what was collected.**
Every figure must trace to a collected source — never invent a number that is not in `raw/`.

**Why this exists — the building block for a country market overview.** The single-company profile is
the unit of work, but the goal is a **country-level market overview that combines every operator**.
The national **regulator is the full-market backbone** (it reports totals and every operator's share),
which is why its data is collected once into a shared `_regulators/<code>/` cache and composed into a
full-market dataset that all operators — and the overview — reuse. So optimise for a **solid,
aggregation-ready repository**: identical schema across companies, regulator data kept whole-market,
every number sourced.

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
    market.csv                      # this operator's subscribers / share / ARPU time-series
  company-summary.md                # regenerated narrative + "Data confidence & gaps" section
  sources.md                        # append-only dated source log, [PRIMARY] markers, source_id keys

company-research/_regulators/<code>/   # SHARED regulator cache — full-market backbone, reused by
  raw/                                 #   every operator in that country (and the market overview)
    manifest.md
  data/market.csv                      # whole-market totals + EVERY operator's subs/share/ARPU
  reports/ledger.json
```

`<company-slug>`: lowercase, spaces→hyphens, drop punctuation (e.g. `A1 Croatia` → `a1-croatia`).

### Entity-type depth matrix

Classification drives ambition. Do not chase data the entity does not disclose.

| `entity_type` | Primary sources to seek | Metrics to compose | Acceptable gaps |
|---|---|---|---|
| `listed` | Own annual report, 20-F, quarterly results, data book | Full P&L (revenue, EBITDA, margin, net income, capex), 3-yr history | few |
| `subsidiary` | **Parent segment reporting**, parent data book, **national company registry** (statutory accounts), regulator market reports, securities-authority filings | Revenue, EBITDA, margin, subscribers, market share (segment-derived → `estimated=true`); net income / capex best-effort | net income, capex, sub-segment detail |
| `private` | **National company registry** (statutory standalone accounts — primary), **bondholder reports** (Eurobond issuers, e.g. United Group), regulator reports, Firecrawl web/press | Standalone revenue/EBITDA/EBIT/net profit (registry); subscribers where disclosed | quarterly cadence, subscriber splits |

For a subsidiary, **the parent's segment reporting is the realistic ceiling** of standalone data.
Scope to that; flag the rest as a gap rather than guessing.

### Sourcing fallback ladder (when the primary source is thin — esp. private/subsidiary)

Do not conclude "no financials" after only checking the parent's investor-relations site. A telco that
discloses nothing to investors usually still has a public statutory footprint. Escalate in order, stopping
when you have the figure (record which rung each `source_id` came from):

1. **Own filings** (listed) → **parent segment reporting** (subsidiary) → **bondholder reports** (private
   Eurobond issuers, e.g. United Group).
2. **National company registry — statutory annual accounts.** Private subsidiaries (`d.o.o.`, `GmbH`,
   `Ltd`…) must file standalone accounts publicly. This is a **primary** source giving real
   revenue/EBITDA/EBIT/net-profit for the legal entity — `basis=standalone`, `estimated=false`.
   Registries: **FINA Info.BIZ / sudreg** (HR), **Companies House** (UK), **Bundesanzeiger** (DE),
   **AJPES** (SI), **APR** (RS), registry/court filings elsewhere. *(Croatia proof: Telemach Hrvatska
   d.o.o. — invisible in United Group's IR, but FY2025 revenue €328m / EBITDA €107m / net €8.6m sits in
   FINA.)*
3. **Regulator** market reports — for market context/totals (rarely per-operator financials).
4. **Web research via Firecrawl — last resort, lower confidence.** Use `mcp__firecrawl__firecrawl_search`
   (or the watcher's search hint) to find **press releases, local business-press articles, and
   company-data aggregators** (e.g. SeeNews, poslovna.hr, Bisnode). Treat as `estimated=true`, cite the
   outlet, and prefer to corroborate against a registry/filing figure. Keep conflicting values as separate
   rows (see Phase 2).

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
**HANFA** (HR). These are `[PRIMARY]` sources. Each has a registry entry (publications page, official
domain, match patterns) in `company-research/regulators.json` — collect them automatically with the
watcher's `regulator <code>` command (see below); `<code>` is the lowercase key in that file
(`rtr`, `hakom`, `ift`, …). Add a regulator there if the operator's country isn't covered yet.

### Collection engine — Firecrawl

Document collection in this environment is the known failure point: `WebFetch` and Bash `curl`
are blocked (403 / egress allowlist) for most operator, newswire, and regulator sites. The
configured collection engine is **Firecrawl** — a hosted scraper (real browser + residential IP)
that fetches server-side, defeating Cloudflare. The API key lives in `.env` as `FIRECRAWL_API_KEY`
(git-ignored).

Call Firecrawl via its REST API with `curl`. Ensure the key is loaded first — prefer the
environment variable (set in the environment settings, survives across sessions); fall back to a
local `.env` if present:
```bash
[ -n "$FIRECRAWL_API_KEY" ] || { [ -f ./.env ] && { set -a; . ./.env; set +a; }; }
[ -n "$FIRECRAWL_API_KEY" ] || echo "FIRECRAWL_API_KEY not set — see company-research/README.md"
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
[ -n "$FIRECRAWL_API_KEY" ] || { set -a; . ./.env; set +a; }
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

### Report watcher — automatic new-report collection

`company-research/report_watcher.py` is the **first collection action** for any company with a
reachable investor-relations reports page. It discovers report documents on an official IR page
(via Firecrawl), filters to the official domain only, skips anything already collected (per-company
`reports/ledger.json`), and downloads every **new** report into `raw/` — so re-running the skill
later only picks up genuinely new filings. Drive it ad-hoc with `--page` (no config edit needed):

```bash
# discover + download every NEW official report into company-research/<slug>/raw/,
# bounded to the last 5 fiscal years of history
python3 company-research/report_watcher.py watch <slug> --max-years 5 \
  --page "<operator-ir-quarterly-results-url>" --page "<operator-ir-annual-reports-url>"
```

Use `check` instead of `watch` first if you want to eyeball candidates before fetching. The watcher
only downloads from the IR page's own registrable domain (official sources), and is idempotent
across sessions. After it runs, treat each file it dropped in `raw/` as a `firecrawl` capture: read
it, assign a `source_id`, and add a `manifest.md` row (Phase 1.2 / 1.5). For sites that block direct
bytes the watcher saves the parsed report as `.md` — which is exactly what Phase 2 consumes.

**Multi-year history.** Pass the **annual-reports / results archive** page too, and `--max-years 5`
to bound the pull. Many IR landing pages expose only the *latest* annual report (e.g. only the newest
20-F); deeper history then has to be found by search and handed to the watcher by URL — still
ledgered, de-duplicated, and domain-guarded:

```bash
# find prior annual reports (per fiscal year), then download the exact PDFs
python3 company-research/report_watcher.py download <slug> \
  --url "<FY2024-annual-report-pdf>" --url "<FY2023-annual-report-pdf>"
```

`--max-years N` keeps only documents whose URL names a year within the last N (URLs with no 20xx year,
e.g. `1Q26`, always pass, so current quarter releases are never dropped).

**Regulators (the local market authority).** Run the watcher's `regulator` command to collect a
national regulator's market/statistical reports into the **shared** cache
`company-research/_regulators/<code>/raw/` (de-duplicated across every operator in that country, with
its own ledger). The regulator's publications page(s), official domain, and report-matching patterns
live in `company-research/regulators.json`; collection follows report **detail** pages one hop down to
reach the actual PDFs:

```bash
python3 company-research/report_watcher.py regulator <code> --max-years 5   # e.g. ift, hakom, rtr…
python3 company-research/report_watcher.py regulator <code> --check         # preview, download nothing
```

Read the relevant regulator report(s) from the shared cache, give them a `source_id`, add a
`manifest.md` row, and cite them as `[PRIMARY]` in `sources.md` (note the file lives under
`_regulators/<code>/`, not the company's own `raw/`). If a regulator is not yet in `regulators.json`,
add it (publications page + registrable domain + a couple of URL patterns) and verify with `--check`.

---

## Workflow

Run the phases in order. **Do not start Phase 2 until Phase 1 collection is reported.**

### Phase 0 — Resolve & classify

1. Derive `<company-slug>`. Create `company-research/<company-slug>/raw/` and `.../data/`.
2. Classify `entity_type` (`listed` / `subsidiary` / `private`).
3. Identify the ultimate parent and the relevant regulator(s); resolve each regulator to its
   `regulators.json` **code** (e.g. `ift`, `hakom`) — these go in `profile.json.regulators` and drive
   the watcher's `regulator` command. If the operator appears in `baselines/`, read its baseline to
   pull owner + regulator directly.
4. List discovery targets in priority order: parent annual report & **segment reporting**, parent
   investor presentation / data book, bondholder reports (private groups), regulator market
   reports, securities-authority filings, then press.

### Phase 1 — COLLECT into `raw/` (do NOT compose datasets yet)

0. **Auto-collect official reports first (report watcher).** Use **`WebSearch` (free)** to find the
   operator's — and its parent's — official IR **quarterly results** *and* **annual-reports** pages
   (Phase 0.4). Then run the watcher to pull every new official report into `raw/`, bounded to the
   last 5 fiscal years:
   ```bash
   python3 company-research/report_watcher.py watch <company-slug> --max-years 5 \
     --page "<operator-ir-quarterly-url>" --page "<operator-ir-annual-reports-url>" \
     [--page "<parent-ir-results-url>"]
   ```
   It is domain-guarded (official IR + the CDN hosts the page links files to) and idempotent (skips
   anything in `reports/ledger.json`), so it is safe to run on every invocation. For each file it
   writes to `raw/`, add a `manifest.md` row with a fresh `source_id` (`fetch_method: local-file`
   once you `Read` a directly-downloaded PDF, else `firecrawl`). If no IR reports page is reachable
   (e.g. an unlisted subsidiary with no standalone IR site), skip this and rely on the steps below.

   **History (last ~5 years).** If the annual-reports page lists only the newest report (common),
   search per fiscal year for the prior annual reports (`"<operator> 20-F annual report <year>
   filetype:pdf"`) and hand the exact PDFs to the watcher so they are downloaded, ledgered, and
   de-duplicated like the rest:
   ```bash
   python3 company-research/report_watcher.py download <company-slug> \
     --url "<prior-year-annual-report-pdf>" [--url "<...>"]
   ```

0b. **Collect the local regulator (market authority).** Resolve the regulator code(s) from Phase 0.3
   and pull their market/statistical reports into the shared cache (`_regulators/<code>/raw/`):
   ```bash
   python3 company-research/report_watcher.py regulator <code> --max-years 5
   ```
   These are `[PRIMARY]` sources and are often the **only** standalone market data for an unlisted
   subsidiary (subscribers, market share, ARPU). Read the relevant report(s) from the shared cache,
   assign a `source_id`, add a `manifest.md` row, and cite them in `sources.md` noting the
   `_regulators/<code>/` location. If the country's regulator isn't in `regulators.json` yet, add it
   (publications page + domain + a couple of URL patterns) and confirm with `regulator <code> --check`.

   **Credits (free-first):** the default already prefers free direct download + local `Read` parsing,
   auto-uses Firecrawl only for *small* blocked docs, and **defers large reports/20-Fs**. Do not
   reach for `--firecrawl-all` (PAID, ~1 credit/PDF page) unless a *specific* large document is truly
   needed and a shorter quarterly release won't do. When the watcher prints an **"allowlist to go
   Firecrawl-free"** line (and updates `company-research/allowlist.txt`), surface that to the user in
   the collection report — adding those hosts to the environment's Network access (Custom, or Full)
   makes future runs free. Treat *deferred* files as a stated gap; don't burn credits to force them.
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
   under `raw/`, read them and write a `raw/` capture with `fetch_method: local-file`. Prefer these —
   they are genuine primary documents. **PDF text extraction needs `poppler-utils` in this container**
   (the `Read` tool errors `pdftoppm is not installed` without it). Install once and extract text:
   ```bash
   command -v pdftotext >/dev/null || apt-get install -y -q poppler-utils
   pdftotext -layout <file.pdf> <file.txt>     # then grep the statement lines you need
   ```
   For multi-hundred-page filings (20-F, annual report) extract once with `pdftotext -layout` and grep
   for the statement headers (e.g. `Operating revenues`, `EBITDA`) rather than paging the whole PDF.
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

**`_regulators/<code>/data/market.csv` — the full-market dataset (ALWAYS compose this, every run).**
This per-company profile is a building block; the end goal is a **country market overview combining
every operator**, and the regulator is the one source that covers the *whole* market. So **whenever you
mine a regulator report — even when profiling a single operator — extract the FULL market**, not just
the focal company: market totals **and every operator's** subscribers/share/ARPU. Compose them into a
`market.csv` **in the regulator cache** (not the company folder), keyed by operator, so every company
in the country — and the overview — reads one shared, authoritative market picture:
```
period,operator,metric,segment,value,unit,source_id,estimated
FY2024,_market,mobile_lines,mobile,140.0,m,R02,false      # market total
FY2024,telcel,mobile_subscribers,mobile,87.0,m,R02,false
FY2024,telcel,mobile_market_share,mobile,62.0,pct,R02,false
FY2024,at&t-mexico,mobile_market_share,mobile,15.0,pct,R02,false
```
Use `operator=_market` for whole-market totals. `source_id`s here are the `R…` ids from the regulator
cache manifest. Refresh idempotently — a regulator capture is shared, so don't duplicate it per company.

> **Reality check (learned on Croatia/HAKOM): many regulator summaries are TOTALS-ONLY.** Do not assume
> the regulator hands you every operator's split — several (e.g. HAKOM's English quarterly reports) publish
> only whole-market aggregates (`operator=_market`): total lines, total broadband, total revenue, and *no*
> per-operator share. When that happens: (1) still compose the totals — they are the denominators the
> overview needs; (2) record the totals-only limitation in `_regulators/<code>/data/README.md`; (3) get
> per-operator shares from the next-best source — the **operators' own self-reported subscriber bases**, a
> deeper regulator portal (e.g. `sat.hakom.hr`), or the country `baseline.md` — never invent them. Mark the
> source on each row; a share derived by you (operator subs ÷ market total) is `estimated=true`.

**Aggregation-ready discipline (so a country roll-up just unions the CSVs).** Across *every* company
use **identical** metric names (`revenue`, `ebitda`, `ebitda_margin`, `mobile_subscribers`,
`mobile_market_share`, `arpu`…), period labels (`FYxxxx`, `Qn-xxxx`), and currency/unit conventions.
Put the operator's own reported share in the company `market.csv`; rely on the regulator full-market
`market.csv` for competitors' shares and market totals. Keep operator slugs consistent with the
company folder names so company ↔ market data join cleanly.

### Phase 3 — Summarize & log

1. **`company-summary.md`** — regenerated. It is both the human-readable face of the repository **and
   a building block for the country market overview**, so lead with structured, roll-up-friendly
   tables, not prose. Write these sections in order:

   **a. Snapshot** — one line: `entity_type · country · parent (ownership%) · regulator(s) · reporting
   currency · latest period`.

   **b. Financial highlights — multi-year.** A trend table, metrics as rows, **every fiscal year
   collected** as columns (e.g. FY2020–FY2025) plus the latest quarter; cite `source_id`(s) per row.
   Omit metrics the entity does not disclose (don't pad).
   ```markdown
   | metric (Ps. bn) | FY2022 | FY2023 | FY2024 | FY2025 | 1Q26 | source |
   |---|---|---|---|---|---|---|
   | Operating revenue | … | 816.0 | 869.2 | 943.6 | … | S04,S01,S05 |
   | Operating income  | … | 167.8 | 180.1 | 191.4 | … | S01 |
   | Net profit        | … | 80.8  | 27.6  | 88.1  | … | S01 |
   ```

   **c. Market & operations — company vs full market.** Put the company figure **next to the
   regulator's full-market figure** (the regulator covers every operator, so this is where the profile
   connects to the market overview): subscribers / RGUs / ARPU / market share, with the market total
   and competitors' shares from `_regulators/<code>/data/market.csv`.
   ```markdown
   | metric | company (src) | regulator full-market (src) |
   |---|---|---|
   | Mobile subscribers | 331m group (S01) | MX total 140m lines (R02) |
   | Mobile share, MX | ~62% Telcel (S05) | Telcel 62% · AT&T 15% · Movistar … (R02) |
   ```

   **d. Market position & competitive context** — short narrative grounded in the regulator totals/shares.

   **e. Regulatory context** — regulator, recent decisions / spectrum / SMP designations, the basis of
   the market shares cited.

   **f. Data confidence & gaps** (required):
   ```markdown
   ## Data confidence & gaps
   - **Company vs regulator:** FY2024 MX mobile share 62% (S05, company) vs 61% (R02, IFT) — preferred R02 (full market).
   - **Conflicts:** FY2024 EBITDA €189m (S01) vs €188m (S07, press) — preferred S01.
   - **Missing:** standalone capex by country (not disclosed); regulator quarterly series stale (latest FY2022).
   - **Confidence:** N primary captures, M search-snippet (lower confidence); note any extraction/tooling gaps.
   ```

2. **`sources.md`** — append a dated block, deduplicated, keyed by `source_id`, `[PRIMARY]` marked.
   Include the regulator `R…` ids from the shared cache (note the `_regulators/<code>/` location):

   ```markdown
   ## 2026-06-12 — A1 Croatia

   - [S01] [PRIMARY] [A1 Group FY2024 Results — segment reporting](URL) — A1 Group IR, 2025-02
   - [S03] [PRIMARY] [HAKOM mobile market report Q1 2026](URL) — HAKOM, 2026
   - [S07] [Local press on A1 Croatia FY2024](URL) — Outlet, 2025-03
   ```

### Phase 3.5 — Repo hygiene (propose pruning processed sources)

Raw filings are large (a single 20-F or regulator annual report is 15–50 MB) and the repo is cloned
fresh every cloud session, so committing every binary forever does not scale across many
operators/countries. After datasets are composed, **propose** (never auto-delete) pruning the heavy raw
captures whose data has already been extracted. Check sizes and cross-check against the datasets:
```bash
du -sh company-research/<slug> company-research/_regulators/<code>      # current footprint
ls -S company-research/<slug>/raw company-research/_regulators/<code>/raw   # largest first
```
A raw capture is a prune candidate only when **all** hold: it is large (say > 5 MB); its `source_id`
is already referenced in `data/*.csv` (fully processed); and its URL is in `reports/ledger.json` (so it
re-downloads for free). List candidates to the user with size + `source_id` and let them choose. On
approval, delete the binary but **preserve provenance**: keep the `manifest.md` row and `ledger.json`
entry, mark the row `pruned` (with the re-fetch URL), and retain the `pdftotext` extract so every
figure still traces to text. This keeps `raw/` an authoritative *record* without hoarding bytes that
are already distilled into `data/`. Never propose pruning a source not yet in `data/`, or one that
isn't re-fetchable.

### Phase 4 — Optional PDF (only if the user asks)

Reuse the telecom-pulse export: write a self-contained HTML brief, convert with
`python3 -m weasyprint <html> <pdf>`, send with `SendUserFile`, delete the HTML.

---

## Refresh behavior

Re-running for an existing company is incremental: add **new** `raw/` captures (new `source_id`s,
never overwrite existing ones), add/update dataset rows, regenerate `profile.json` and
`company-summary.md`, and append (never rewrite) `sources.md`. `raw/` is an append-only *record*:
never silently overwrite a capture. The only removal is the supervised prune in Phase 3.5 — and even
then the `manifest.md` row + `ledger.json` entry (and text extract) stay, so provenance is intact.

---

## Downstream — country market overview (the per-market summary)

This skill produces **one operator**. The end goal is a **country market overview combining every
operator**, assembled in a separate step that simply **unions the aggregation-ready outputs** — so the
per-operator job is to keep those outputs clean. Reference implementation:
`company-research/_markets/croatia/` (HT + A1 + Telemach + HAKOM). Shape:

```
company-research/_markets/<country>/
  market.csv            # union of every operator's data/*.csv (focal-company rows)
                        #   + the regulator full-market rows from _regulators/<code>/data/market.csv
  market-overview.md    # combined view: operators ranked, shares vs the regulator total, multi-year trend
```

It joins on **operator slug** (same slugs as the company folders), aligned `period` labels
(`FYxxxx`/`Qn-xxxx`) and currency/unit. The **regulator full-market `market.csv` is the spine**
(market totals + every operator's share); each operator's own `financials.csv`/`market.csv` supplies the
company-reported detail. Nothing in the overview is recomputed from `raw/` — it is a pure roll-up, which
is exactly why per-company composition must use identical names and why regulator data is mined
whole-market every run. (Country structure also feeds the existing `baselines/<country>/` and the
`telecom-pulse` skill.)

> **Reconcile, don't just divide (learned on Croatia).** The roll-up's most valuable output is often the
> *reconciliation*, not a clean share table. The regulator, the operators, and the baseline routinely
> measure the market three incompatible ways — e.g. operator-reported "subscribers" (active base, may add
> M2M) ≠ regulator "mobile lines"; an operator's "fixed broadband" may actually be **RGUs** (broadband +
> TV + voice); a listed parent's revenue may bundle other countries/equipment/wholesale. Symptom: the
> operators' figures **over- or under-shoot the regulator total** (in Croatia HT + A1 reported mobile bases
> alone = 98% of HAKOM's total, leaving no room for Telemach). So: do **not** compute
> `operator subs ÷ regulator total` into a precise share when the bases don't reconcile — surface the
> mismatch instead, normalize definitions first where you can, and lead the overview with the caveats.
> A noisy reconciliation that names the three inconsistencies is more useful (and honest) than a tidy fake
> share table.

**Build it once ≥2 operators in a country are composed.** It is a pure roll-up — recompute nothing from
`raw/`. Produce two files (template: `_markets/croatia/`):

`data/market.csv` — the machine union. Same schema as the regulator cache
(`period,operator,metric,segment,value,unit,source_id,estimated`), with **cross-folder `source_id`s** so
provenance survives the union (`hakom/R08`, `hrvatski-telekom/S04`, `a1-croatia/S01`). Normalize money to
`EUR_m`, subscribers to `m`, shares to `pct`. Carry the regulator `_market` totals + each operator's key
metrics (revenue, ebitda, net_income, subscribers).

`market-overview.md` — the narrative summary. Standard sections:
1. **Header** — assembled date; "composed by union of <operators> + <regulator>"; state the cross-folder
   `source_id` convention and the EUR_m/m/pct normalization.
2. **Market size** — the regulator whole-market totals as a multi-year table (mobile lines, fixed
   broadband, TV, total revenue); note penetration trends.
3. **Operator financials** — an FY table (revenue, EBITDA, margin, net income, `basis`) for the
   best-covered year + a multi-year revenue/EBITDA trend line. Call out **scope mismatches** (a listed
   parent's revenue may bundle other countries / equipment / wholesale; a subsidiary's is segment-only).
4. **Subscribers & shares** — apply *reconcile-don't-divide*: regulator totals and operator-reported
   bases **side by side**; derive a share only if they reconcile, else show the mismatch and the gaps.
5. **Cross-operator findings** — the definitional inconsistencies, the regulator's coverage gaps, any
   operator invisible in the data (private-in-private), and metric mislabels (RGUs vs broadband).
6. **Data confidence & provenance** — high / low / missing; every figure traces to a cross-folder
   `source_id`.

Lead with the **reconciliation**, not a tidy share table — for a real market the honest summary is the one
that names what doesn't line up.

### Shared parent-group cache (design target — dedupe HQ reports across markets)

A parent group's report covers **many markets at once**: one Deutsche Telekom annual report serves HT
(Croatia), Magenta (Austria) and Makedonski Telekom; one A1 Group / Telekom Austria report serves A1
Croatia, A1 Serbia, A1 Bulgaria …; one United Group report serves every Telemach/Vivacom. Collecting it
afresh under each subsidiary (as the first Croatia run did, filing A1 *Group* reports under
`a1-croatia/raw/`) duplicates large PDFs and work. Planned fix — a **shared group cache**, the exact
analogue of `_regulators/<code>/`:

```
company-research/_groups/<group-slug>/      # e.g. deutsche-telekom, a1-group, united-group
  raw/ + manifest.md + reports/ledger.json  # the group's filings, collected ONCE
  data/segments.csv                          # per-subsidiary segment figures keyed by operator slug
```

Before collecting a parent report for a subsidiary, **check whether the group already has it** in
`_groups/<group>/` (by URL in the ledger) and reuse it; a subsidiary's `financials.csv` then pulls its
rows from `_groups/<group>/data/segments.csv` (segment-derived → `estimated=true`). This keeps one
authoritative copy of each HQ filing and makes a subsidiary profile a thin layer over shared group +
shared regulator data. (Not built yet — design only.)

---

## Tone and constraints

- Cite every figure to a `source_id`. If a number is not in a `raw/` capture, it does not go in the dataset.
- Prefer PRIMARY (filings, segment reports, regulator, bondholder reports) over press.
- Keep conflicting values; never silently pick. Mark the preferred one and explain.
- State gaps plainly. For subsidiaries, an honest "not disclosed" beats a fabricated estimate.
- Collect first, compose second. Report collection (incl. failures) before composing.
