# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not a software project** — it is a Claude-Code-driven **research & intelligence workspace**. There is no application to build, no test suite, and no dependency manifest. "Work" here means running one of the skills below to produce sourced, markdown-based intelligence artifacts (and occasionally PDFs). Output quality is judged by sourcing discipline and directional clarity, not by passing tests.

Two independent research programs live side by side:

1. **Telecom market intelligence** (`baselines/`) — monthly competitive-intensity briefs for national telecom markets, driven by the `telecom-pulse` skill.
2. **Economics-of-AI knowledge base** (`wiki/` + `raw/`) — a compounding LLM wiki on AI-usage economics, driven by the `karpathy-llm-wiki` skill.

The skills are the source of truth for their own workflows. Read the relevant one in full before operating:
- `.claude/commands/telecom-pulse.md`
- `.claude/commands/karpathy-llm-wiki.md`

## Skills / workflows (the "commands")

### `/telecom-pulse <country>`
Monthly competitive brief for one of 7 configured markets (Austria, Croatia, Serbia, Slovenia, Macedonia, Belarus, Bulgaria). Pattern: load `baselines/<country>/baseline.md` for context → launch **exactly 3 parallel search agents** (Pricing/retail, M&A-earnings, Regulatory-infrastructure), each restricted to the **last 90 days** → synthesize a <600-word brief with a single **directional verdict** (Intensifying / Stable / Easing) → write to `baselines/<country>/<YYYY>.md` (append month, never delete prior months) → log URLs to `baselines/<country>/sources.md` → export a PDF and `SendUserFile` it.
- `--refresh-baseline` is the expensive path (5 angles, 18-month lookback, overwrites `baseline.md`). Use **only** when a structural event fires the baseline-refresh rule (merger completed/blocked, operator entry/exit, spectrum auction concluded, major wholesale ruling).

### `/karpathy-llm-wiki` (ingest / query / lint)
Personal LLM knowledge base. Two directories: **`raw/`** (immutable fetched sources, read-only) and **`wiki/`** (compiled articles you own). Every **Ingest** does both steps — fetch into `raw/<topic>/YYYY-MM-DD-slug.md`, then compile/merge into `wiki/<topic>/<article>.md` and run cascade updates on affected articles. `wiki/` allows **one level of topic subdirectories only**. Maintain `wiki/index.md` (one row per article) and `wiki/log.md` (append-only). The current ingest subject is the economics of AI usage (topics: `ai-pricing/`, `adoption-roi/`, `make-or-buy/`, `workforce-productivity/`).

## Conventions that span both programs

- **Cite every factual claim** with a source URL + publication date. If it can't be sourced, it doesn't go in.
- Mark original/primary documents (earnings PDFs, regulator notices, study PDFs) with **`[PRIMARY]`** in source logs — these are most likely to move or paywall and are worth downloading.
- Markdown links inside `wiki/` files are **relative to the current file** (e.g. `../../raw/<topic>/<file>.md`); in conversation, cite project-root-relative paths.
- Telecom briefs are deliberately **directional/opinionated**, not neutral summaries. Brevity is a feature (<600 words for the pulse text).

## Tooling

- **Web research / document download:** the **Firecrawl MCP server** is configured in `.mcp.json` (`npx -y firecrawl-mcp`), reading `FIRECRAWL_API_KEY` from the environment — the key is **never** committed. MCP servers load on session start, so adding/changing `.mcp.json` requires a session restart (and approval) before `mcp__firecrawl__*` tools appear. Native `WebSearch`/`WebFetch` are the fallback.
- **PDF export** (telecom-pulse): write a self-contained HTML file from the template in `telecom-pulse.md`, then `python3 -m weasyprint <html> <pdf>`, then delete the intermediate HTML. **WeasyPrint is not installed by default** in fresh environments — `pip install weasyprint` first.

## Git

Active development branch: `claude/affectionate-ride-px4o1s`. Commit sourced artifacts with descriptive messages; do not open PRs unless explicitly asked.
