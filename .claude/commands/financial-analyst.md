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
