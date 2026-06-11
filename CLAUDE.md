# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is not a software project — it's a **data + skills repository** for Claude Code. It contains:

- `.claude/commands/` — slash-command skill definitions (markdown with YAML frontmatter: `name`, `description`). When the user types `/<name>` or asks for something matching a skill's `description`, follow that skill's workflow exactly.
- Data directories produced and maintained *by* those skills, which double as a durable knowledge base across sessions.

There is no build, lint, or test tooling — work consists of running skills, researching via web search, and writing/updating the markdown/JSON artifacts described below.

## Skills and their data stores

### `telecom-pulse` (`.claude/commands/telecom-pulse.md`)
Monthly competitive-intelligence brief for a national telecom market. Configured markets: Austria, Croatia, Serbia, Slovenia, Macedonia, Belarus, Bulgaria (each with its operator list in the skill file).

Data lives in `baselines/<country>/`:
- `baseline.md` — stable structural reference (market structure, competitive history, infrastructure, regulatory timeline, key tensions). Only overwritten via the `--refresh-baseline` flag.
- `<YYYY>.md` — append-only annual log; one section per month (`## <YYYY-MM> — <Month Name>`) with "Year so far / Last 90 days / Outlook" subsections.
- `sources.md` — append-only, dated, grouped by research angle (Pricing, M&A/Earnings, Regulatory), with `[PRIMARY]` markers for primary documents.
- `<country>-<YYYY-MM>.pdf` (+ a transient `.html`) — generated brief, built via WeasyPrint and sent to the user with `SendUserFile`.

Workflow: load `baseline.md` + current year's log → 3 parallel research agents (Pricing, M&A/Earnings, Regulatory/Infrastructure, last-90-days only) → synthesize into the year file → append sources → check baseline-refresh triggers → render PDF.

### `financial-analyst` (`.claude/commands/financial-analyst.md`)
Builds/maintains a financial and market profile for one company or subsidiary (works for listed companies and unlisted subsidiaries, e.g. "Magenta Austria").

Data lives in `company-research/<company-slug>/` (slug = lowercase kebab-case company name):
- `data/overview.json` — identity, ownership, `entity_type` (`listed` | `subsidiary` | `private`), ticker/exchange if listed.
- `data/financials.json` — headline P&L figures only (no full balance sheet/cash flow) per fiscal period, in a `periods` array keyed by `period` (e.g. `FY2025`); entries derived from a parent's segment reporting are marked `"estimated": true`.
- `data/market.json` — `market_data` (valuation — listed entities only) and `market_position` (subscribers, market share, competitors — all entity types).
- `profile.md` — regenerated narrative (Overview, Financial performance table, Market position, Valuation, Recent developments, Data notes).
- `sources.md` — append-only, dated, grouped by angle (Financials & filings, Market position & competition, Corporate structure/ownership & news), `[PRIMARY]` for official filings/reports.
- `raw/` — archived primary-source documents (PDFs/reports), named `<YYYY-MM-DD>-<short-slug>.<ext>` using the report's own publication date.

Key behaviors:
- **Incremental refresh** is the default: load existing `data/*.json`, verify/update rather than rebuild from scratch, append/update `periods` (never drop history), append (never overwrite) `sources.md`.
- **History backfill**: if `financials.json` has fewer than 3 annual (`FY*`) periods (including a brand-new company), the run targets 2-3 fiscal years of history, prioritizing the parent company's annual reports/investor presentations for multi-year segment breakdowns, and archives those primary documents to `raw/`.
- 3 parallel research agents per run: Financials & filings, Market position & competition, Corporate structure/ownership & recent news.
- **`raw/` archiving is best-effort**: PDF downloads of primary reports (e.g. `a1.group`, `hakom.hr`, `eqs-news.com`) frequently return HTTP 403 to both `curl` and `WebFetch` in this environment (anti-bot protection, sometimes a broader sandbox network restriction affecting `WebFetch` entirely). When a fetch fails, note it in `sources.md`/`profile.md` Data notes rather than silently leaving `raw/` empty — don't treat repeated 403s as a bug to keep retrying within a single run.

### `karpathy-llm-wiki` (`.claude/commands/karpathy-llm-wiki.md`)
Personal LLM-powered knowledge base. Not yet populated with content in this repo (no `raw/`/`wiki/` directories exist yet) — see the skill file for the intended `raw/<topic>/` (immutable sources) + `wiki/<topic>/` (compiled articles) + `index.md`/`log.md` structure before creating new ones.

## Conventions shared across skills

- **Append-only logs** (`sources.md`, `<YYYY>.md`) preserve history — never delete or overwrite prior entries, only add new dated sections.
- **Source citation**: every factual/numeric claim needs `[Title](URL) — Publisher, YYYY-MM-DD`, with `[PRIMARY]` for official/primary documents (filings, annual reports, regulator notices, press releases).
- **No intermediate planning docs**: skills write final output directly rather than staging notes.
- Research is done via small numbers of **parallel sub-agents**, each scoped to one research angle with a tight search/fetch budget — keep this pattern when extending or adding skills.
