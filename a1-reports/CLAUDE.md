# A1 Group Annual Reports — Knowledge Base

This repo turns ~25 years of A1 Group annual reports (PDFs) into a navigable knowledge
base for agentic querying. It is a **learning project**: prioritise clean, understandable
structure over speed or cleverness.

## Architecture (read this first)

Two stores, two jobs. Do not build a third (no vector DB / embeddings unless explicitly asked).

1. **The wiki** (`wiki/`) — narrative & qualitative content as navigable Markdown.
   Start every task by reading `wiki/INDEX.md`. It is the map of what exists.
   Navigate deliberately to the right file; do not grep blindly across everything.

2. **DuckDB** (`data/financials.duckdb`) — all numeric/tabular data.
   Use this for any question involving figures, arithmetic, or cross-year aggregation.
   Schema is documented in `data/SCHEMA.md`. Never compute financial figures by
   reading them out of prose — query the database.

Routing rule:
- "What was / how much / trend / compare numbers" → DuckDB
- "What did management say / why / risks / tone / strategy" → wiki
- Mixed → query DuckDB for the figures, read the wiki for the explanation, then synthesise.

## Repo layout

```
pdfs/                  raw annual reports (read-only source of truth)
markdown/              full-text PDF→MD conversions (one file per report)
wiki/
  INDEX.md             the map — what years/sections exist
  reports/<year>/      per-report notes (overview, narrative, etc.)
  metrics/             cross-year narrative views of a single metric
data/
  financials.duckdb    the structured store
  SCHEMA.md            table definitions + conventions
scripts/               extraction & query helpers (Python)
```

## Conventions

- **Fiscal year vs report year**: a report published in 2011 mostly covers FY2010.
  Always tag data by the fiscal year it describes, not the publication year.
- **Restatements**: a figure for FY-N often reappears (sometimes changed) in the FY-N+1
  report's comparison column. When values conflict, keep both and set `restated_flag`.
  Never silently overwrite.
- **Provenance**: every extracted number records its `source_page`. Every wiki claim
  links back to the report and page it came from.
- **Currency/units**: store the raw reported unit; don't pre-convert. Note unit in the row.
- Commit in small, reviewable steps (one report or one task per commit) with a clear message.

## Working process

When asked to ingest a report:
1. Convert `pdfs/<year>.pdf` → `markdown/<year>.md` (preserve headings + page markers).
2. Extract financial tables → DuckDB per `data/SCHEMA.md`.
3. Write `wiki/reports/<year>/overview.md` and a short `narrative.md`.
4. Update `wiki/INDEX.md` to list the newly added report.
5. Commit.

If a table is ambiguous or a number looks wrong, flag it in the commit message and in a
`## Open questions` section of that report's overview rather than guessing.

## Environment notes

- Runs in the Claude Code web sandbox (cloud VM, git-centric, limited network).
- Python deps are in `requirements.txt`; install at session start if network egress is on.
- Keep everything file-based (DuckDB file, Markdown). No servers, no external services.
