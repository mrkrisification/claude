# company-research

Output of the `/financial-analyst` skill — one machine-readable financial/market profile per
telecom operator. Built **collection-first**: source documents are archived into `raw/` before any
dataset is composed, and every figure in the datasets traces back to a `raw/` capture by `source_id`.

## Layout

```
company-research/<company-slug>/
  raw/                     # collected source documents — immutable, populated FIRST
    YYYY-MM-DD-<slug>.md   #   one capture per source (metadata header + extracted text)
    manifest.md            #   index of every capture
  data/
    profile.json           # identity, ownership, entity_type, parent, regulators, competitors
    financials.csv         # tidy/long P&L time-series
    market.csv             # subscribers / share / ARPU time-series
  company-summary.md       # narrative + "Data confidence & gaps"
  sources.md               # append-only dated source log; [PRIMARY] markers; source_id keys
```

## Dataset schemas

**`financials.csv`** — one row per period×metric (long format, easy to pivot/load):

| column | meaning |
|---|---|
| `period` | `FY2024`, `Q1-2026`, `H1-2024` … |
| `metric` | `revenue`, `ebitda`, `ebitda_margin`, `net_income`, `capex` … |
| `value` | numeric |
| `currency` | ISO code or empty (e.g. for `pct`) |
| `unit` | `m`, `bn`, `pct`, `EUR` … |
| `basis` | `consolidated` \| `segment` \| `standalone` |
| `estimated` | `true` for parent-segment-derived figures |
| `source_id` | join key into `raw/manifest.md` and `sources.md` |
| `is_preferred` | `true` for the chosen value when sources conflict |
| `note` | reconciliation / context |

**`market.csv`** — `period, metric, segment, value, unit, source_id, estimated`
(`metric` e.g. `mobile_subscribers`, `mobile_market_share`, `arpu`).

**Conflicting numbers are kept**, not dropped: each reported value is its own row with a distinct
`source_id`; the chosen one is `is_preferred=true` with the rationale in `note`.

## Loading

```python
import json, csv
profile = json.load(open("company-research/a1-croatia/data/profile.json"))
fin = list(csv.DictReader(open("company-research/a1-croatia/data/financials.csv")))
```

## Collection engine — Firecrawl (setup)

Most operator, newswire, and regulator sites block this environment's fetch paths (`WebFetch` and
Bash `curl` return 403 / are egress-blocked). The skill uses **Firecrawl** — a hosted scraper that
retrieves pages with a real browser + residential IP, defeating Cloudflare.

**Status / setup:**
1. **API key** — set `FIRECRAWL_API_KEY` as an **environment variable in the environment settings**
   (same dialog as network access). This persists across sessions and stays out of git. A local
   `.env` (git-ignored) also works for the current session, but a fresh cloud session clones only
   what's in git — so the env-var route is required for new sessions.
2. **Egress allowlist** — ⚠️ **required, one-time, outside this container.** This environment blocks
   `api.firecrawl.dev` by default (`Host not in allowlist`). Add `api.firecrawl.dev` to the
   environment's **network egress allowlist** so the skill can reach the API. See how this
   environment is configured: https://code.claude.com/docs/en/claude-code-on-the-web
3. **Verify** once allowlisted:
   ```bash
   set -a; . ./.env; set +a
   curl -sS -m 20 -X POST https://api.firecrawl.dev/v2/scrape \
     -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" \
     -d '{"url":"https://firecrawl.dev","formats":["markdown"]}'
   ```
   A JSON body with `data.markdown` means it's working; `Host not in allowlist` means step 2 isn't
   done yet.

The skill calls Firecrawl's REST API directly (`/v2/search` for discovery, `/v2/scrape` to fill
`raw/`) — no CLI install needed. A Firecrawl MCP server would also work if you prefer that.

**Fallbacks** (used automatically when Firecrawl is unreachable): the skill drops to `WebSearch`
snippet captures (`fetch_method: search-snippet`), flagged lower-confidence in `company-summary.md`.
You can also drop primary PDFs into a company's `raw/` folder (or the upload area) and the skill
ingests them directly — the `Read` tool parses PDFs natively.

## Report watcher — detect & download new reports

`report_watcher.py` checks a company's investor-relations / reports page, finds report documents
(quarterly results, full-year results, annual reports, presentations …), works out which are **new**
since the last run, and downloads them into the company's `raw/` folder — on demand, at runtime.

**Layered, free-first collection.** Discovery and downloads both try a **direct fetch first (free)**
and only fall back to Firecrawl when that's blocked. A per-company `reports/ledger.json` records what
was fetched so nothing is re-downloaded.

1. **Find** the IR page — the skill/agent uses `WebSearch` (free) to locate it, passing it via `--page`.
2. **Discover** report links — the watcher fetches the IR page directly and parses its anchors
   locally; only if that host is blocked does it fall back to Firecrawl `map`+`scrape`.
3. **Download** — direct download (free); blocked files are handled per the credit policy below.
4. **Self-diagnose** — every blocked host is written to a paste-ready `allowlist.txt` and printed as
   "allowlist to go Firecrawl-free next run".

### Credit cost & the free path ⚠️

Firecrawl bills **1 credit per PDF page**, so parsing one few-hundred-page annual report / 20-F can
cost 200–300 credits — that is what exhausts the free tier (1,000/month), not discovery. Policy:

- **Default = free-first.** Direct download always runs first; reachable files are parsed locally by
  the `Read` tool (**zero** Firecrawl credits). When direct is blocked, the default auto-parses only
  *small* docs via Firecrawl and **defers large reports/20-Fs** (never silently spends hundreds).
- **Modes:** `--no-firecrawl` = guaranteed zero credits (defer everything blocked); `--firecrawl-all`
  = allow Firecrawl even on large reports (PAID); `--max-credits N` = per-run soft cap.
- **The real free fix — allowlist the hosts.** Direct fetch is blocked here only because the egress
  allowlist permits just `api.firecrawl.dev`. The watcher can't change that (it's a web-UI security
  boundary) but it **curates the list for you**: every blocked host lands in `company-research/
  allowlist.txt`, one domain per line. Two options in the environment's **Network access** settings:
    - **Custom** → paste `allowlist.txt` into *Allowed domains* (e.g. `q4cdn.com` covers many issuers); or
    - **Full** → any domain, zero ongoing maintenance.
  Once a host is reachable, the whole pipeline for it is free.
- Firecrawl's `maxAge` cache does **not** reduce credits, so caching is not a workaround.

```bash
# one-time: declare the companies + their reports pages
cp report_watcher.config.example.json report_watcher.config.json   # then edit (git-ignored)

# phase 1 — discover new candidates (read-only; agent reviews these and decides)
python3 report_watcher.py check <slug>            # or: check <slug> --json

# phase 2 — download (agent executes once it has decided)
python3 report_watcher.py download <slug> --all                       # every new candidate
python3 report_watcher.py download <slug> --url <URL> [--url <URL>]    # specific picks

# unattended one-shot — discover + download everything new (schedule-friendly)
python3 report_watcher.py watch <slug>            # one company
python3 report_watcher.py watch                   # sweep every company in config

python3 report_watcher.py list <slug>             # what's already on record
```

**Two ways to run it:**

- **Supervised** — `check` *proposes* new documents and the agent/human decides before `download`
  fetches them. Use when you want a judgement gate.
- **Unattended (collect-broadly)** — `watch` discovers and downloads everything new in one shot.
  Safe because of the **domain guard**: it downloads only from the official IR domain(s) (config
  `domains`, else derived from `urls`) **plus the CDN hosts the official page itself links report
  files to** (e.g. `q4cdn.com`). Other third-party links (newswires/social) and any explicit `--url`
  off those domains are refused.

Tune precision per company with the optional `patterns` list; obvious non-documents (financial
calendars, event listings) are excluded automatically.
