# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A workspace of **Claude Code skills** (slash commands in `.claude/commands/`) plus the **data artifacts they produce**, centered on **telecom market intelligence**. There is no application to build or test suite to run — the "code" is the skills, one Python collection tool, and structured markdown/CSV/JSON data.

Three skills:
- **`/financial-analyst <company>`** — builds a machine-readable financial/market profile for one telecom operator under `company-research/<slug>/`.
- **`/telecom-pulse <country>`** — monthly competitive brief for a national market, anchored to `baselines/<country>/`.
- **`/karpathy-llm-wiki`** — a personal LLM knowledge base (raw/ → compiled wiki articles).

The skills are the source of truth for *how* to do the work — read the relevant `.claude/commands/*.md` in full before acting on a request that matches its trigger. This file is the map between them.

## The big picture: per-company data → country market overview

The skills compose into one pipeline whose end goal is a **country market overview combining every operator**:

- **`/financial-analyst`** is the *building block*: one operator at a time, **collect-first then compose**. Source documents are archived into `company-research/<slug>/raw/` (immutable) and every figure in `data/*.csv` traces back to a `raw/` capture by `source_id`. Never put a number in a dataset that isn't in `raw/`.
- **Regulator data is the full-market backbone.** A national regulator reports the *whole* market (totals + every operator's share), so it is collected once into a **shared** cache `company-research/_regulators/<code>/` and mined whole-market on every run — not per company. This is what makes a country roll-up possible.
- **Aggregation-readiness is the discipline:** identical metric names, `FYxxxx`/`Qn-xxxx` period labels, currency/unit, and operator slugs across *all* operators, so a country overview is a pure union of the per-company `data/*.csv` + the regulator full-market `market.csv`. (The overview itself — `company-research/_markets/<country>/` — is designed but not yet built; see the financial-analyst skill's "Downstream" section.)
- **Design items not yet built:** the country `_markets/` overview, and a shared `_groups/<group>/` parent-report cache (one Deutsche Telekom / A1 Group / United Group filing serves many markets — dedupe HQ reports the way `_regulators/` dedupes regulator reports).

`baselines/<country>/baseline.md` (structural facts: operators, owners, regulator) and `/telecom-pulse` are the country-level consumers; `/financial-analyst` reads a baseline first when one exists.

## The collection engine: `company-research/report_watcher.py`

This script is the first collection action and the most complex code in the repo. It discovers report documents on an official IR / regulator page, downloads only new ones (per-target `reports/ledger.json` makes it idempotent), and is **domain-guarded** (downloads only from the official registrable domain(s) plus CDN hosts the page itself links files to).

```bash
cd company-research
python3 report_watcher.py check    <slug>  [--max-years N] [--json]   # read-only discovery
python3 report_watcher.py watch    <slug>  [--max-years N]            # discover + download new (companies)
python3 report_watcher.py download <slug>  --url <URL> [--url ...]    # specific docs (e.g. prior-year reports found by search)
python3 report_watcher.py regulator <code> [--max-years N] [--check] # collect into shared _regulators/<code>/
python3 report_watcher.py list     <slug>                            # ledger (use reg:<code> for a regulator)
python3 -m py_compile report_watcher.py                              # there are no tests — this is the sanity check
```

Key mechanics to know before editing it:
- **Free-first / credit policy.** Direct download is always tried first (free). Firecrawl (PAID, ~1 credit/PDF page) is a fallback: default auto-uses it only for *small* blocked docs and **defers large reports/20-Fs**; `--no-firecrawl` = 0 credits, `--firecrawl-all` = allow large, `--max-credits N` = cap. Every blocked host is written to a paste-ready `company-research/allowlist.txt` (the agent can't change the environment's network allowlist; the user pastes it in).
- **Discovery** (`discover_links` / `discover_all`): direct anchor parsing first; Firecrawl `map` (whole-site, fed the **origin** not the deep URL, with an optional per-source `search` hint) + `scrape` (waitFor, for JS/SPA pages) when a page yields nothing or an explicit search hint is set. Regulators additionally do a **two-hop** follow through report *detail* pages.
- **Config:** companies live in `company-research/report_watcher.config.json` (**gitignored, runtime/per-machine** — see `report_watcher.config.example.json` for the schema and the `search`/`strict`/`patterns`/`domains` keys); regulators live in `company-research/regulators.json` (**committed** reference data: publications page, official domain, match patterns, optional `search`). `strict: true` (companies) / regulator targets require a candidate to match the registry/config `patterns` — use it for IR sites that dump governance/compliance PDFs.
- **`--max-years N`** bounds history by the year parsed from the **filename** (not the URL path, which may carry an unrelated CDN upload year); URLs with no `20xx` year always pass.

## Environment & gotchas

- **Firecrawl** is the scraping engine (operator/regulator sites block direct fetch). Needs `FIRECRAWL_API_KEY` (env var, or `./.env` which is gitignored) **and** `api.firecrawl.dev` on the environment's network egress allowlist. A Firecrawl MCP server is also available (`mcp__firecrawl__*`). See `company-research/README.md` for setup.
- **PDF text extraction needs `poppler-utils`** (`pdftotext`) — not always installed; `apt-get install -y poppler-utils` if the Read tool errors `pdftoppm is not installed`. For 200–400 page filings, `pdftotext -layout` then grep the statement headers rather than reading the whole PDF.
- **Gitignored:** `/.env`, `company-research/report_watcher.config.json`, `__pycache__/`. `regulators.json` and collected `raw/` PDFs **are** committed (raw PDFs are large — ~tens of MB each; a future switch to Git-LFS or committing only `pdftotext` output is an open option).

## Conventions

- Develop on the working branch; do not push to other branches or open PRs without explicit permission.
- `raw/` is an append-only record. The only deletion is the supervised "repo hygiene" prune (financial-analyst Phase 3.5): a large capture already distilled into `data/` and re-fetchable via the ledger may be pruned with user confirmation, keeping the manifest row + ledger entry + text extract.
- Keep conflicting source numbers (separate `data/*.csv` rows with distinct `source_id`, mark the preferred one) — never silently pick one.
