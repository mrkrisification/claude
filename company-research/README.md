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

## Collection engine — scraper MCP (setup)

Most operator, newswire, and regulator sites block this environment's fetch paths (`WebFetch` and
Bash `curl` return 403 / are egress-blocked). The skill therefore expects a **hosted fetch/scraper
MCP** — a server that retrieves pages with a real browser + residential IP, which defeats Cloudflare
and bypasses the local egress allowlist.

- **Recommended:** Firecrawl MCP. **Alternatives:** Jina Reader, Bright Data, Browserbase.
- Configure it as an MCP server (see https://code.claude.com/docs/en/claude-code-on-the-web for how
  this environment is configured). The skill auto-locates whatever scraper MCP is present via
  `ToolSearch`.
- **Without a scraper MCP** the skill still runs but falls back to `WebSearch` snippet captures
  (`fetch_method: search-snippet`), which are lower-confidence and flagged as such in
  `company-summary.md`. You can also drop primary PDFs into a company's `raw/` folder (or the upload
  area) and the skill will ingest them directly — the `Read` tool parses PDFs natively.
