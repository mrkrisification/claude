# Financial Analyst Skill — Retrospective & Ideas for a Fresh Start

## Core concept

A per-company research skill that builds and incrementally refreshes a financial/market
profile for any telecom operator — whether a publicly listed group (e.g. Deutsche Telekom)
or an unlisted subsidiary (e.g. A1 Croatia, Magenta Austria).

## Storage design (the part that worked well)

- `company-research/<company-slug>/` per company, structured as:
  - `data/overview.json` — identity, ownership, `entity_type` (`listed`/`subsidiary`/`private`), parent
  - `data/financials.json` — headline P&L only (revenue, EBITDA, margin, net income, capex) per
    period, with `"estimated": true` flagging figures derived from a parent's segment reporting
  - `data/market.json` — valuation data (listed only) + market position (subscribers, share,
    competitors) for everyone
  - `profile.md` — regenerated narrative
  - `sources.md` — append-only dated source log with `[PRIMARY]` markers

This JSON-first structure is genuinely reusable by other tools and is worth keeping in any
redesign.

## Where it broke down

1. **Subsidiary financials are scattered and inconsistent.** For non-listed subsidiaries,
   there's no single authoritative filing — figures come from a patchwork of local press,
   regulator filings (HANFA, HAKOM), and the parent's segment reporting, often with
   conflicting numbers (e.g. FY2023 EBITDA reported as both €188m and €189m; conflicting
   mobile market share of 20% vs 34%).
2. **Primary-source PDFs are unfetchable.** `a1.group`, `hakom.hr`, `hanfa.hr` all return
   HTTP 403 to both `WebFetch` and `curl` regardless of User-Agent — almost certainly
   bot/Cloudflare protection. This made the `raw/` archive folder permanently empty and
   capped data quality at whatever secondary press happened to report.
3. **Web search depth was shallow by default.** The initial run only found one half-year
   press release; even the "backfill" extension mostly surfaced secondary news articles
   rather than the multi-year segment tables that actually exist in parent annual
   reports/investor presentations.
4. **History backfill logic added complexity without solving the root problem** — more
   search queries didn't help if the underlying PDFs can't be fetched at all.

## Ideas worth carrying forward to a redesign

- The JSON schema/storage layout (`overview.json` / `financials.json` / `market.json` /
  `profile.md` / `sources.md`)
- `[PRIMARY]` source citation convention with append-only `sources.md`
- `estimated: true` flag for segment-derived figures
- Entity classification (`listed`/`subsidiary`/`private`) driving what data is sought

## What a fresh approach should address

- Build in a **fetch-fallback chain** from day one (Wayback Machine, reader-proxy services
  like r.jina.ai) for PRIMARY PDFs, rather than treating 403s as a late-stage surprise.
- Consider whether **per-subsidiary depth is realistic at all** — for many subsidiaries,
  the parent's segment reporting may be the practical ceiling of available data, so the
  skill's ambition (3-year history, standalone net income/capex) may need to be scoped
  down to match what's actually disclosed.
- Possibly separate "listed parent deep-dive" (where real filings exist) from "subsidiary
  snapshot" (lighter-weight, accept more gaps) as different workflows rather than one
  skill trying to do both.
