# A1 Group Annual Reports — Agentic Knowledge Base

A learning project: ~25 years of A1 Group annual report PDFs turned into a
queryable knowledge base for an agent (Claude Code).

**Start here:** the agent reads `CLAUDE.md`, then `wiki/INDEX.md`.

## Architecture
- Narrative → navigable Markdown wiki (`wiki/`), Karpathy-style, mapped by `wiki/INDEX.md`.
- Numbers → DuckDB single file (`data/financials.duckdb`), schema in `data/SCHEMA.md`.
- No embeddings / vector DB — structure + navigation instead.

## Getting started
1. Drop the PDFs into `pdfs/` named by report year, e.g. `pdfs/2010.pdf`.
2. Open a Claude Code session against this repo.
3. Ask it to ingest one report end-to-end, review the diff, then scale up.
