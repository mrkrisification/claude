# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal "experiments with Claude" repo. It holds **content artifacts, not application code** — there is no build system, package manifest, or test suite. Work here is driven by slash-command skills whose definitions live in `.claude/commands/`. The skill definition is the source of truth for each workflow's file layout and editing rules; read it before touching the files it owns.

## Tooling

PDF briefs are generated with **WeasyPrint** (HTML → PDF):

```
python3 -m weasyprint <input.html> <output.pdf>
```

## Workflows

### `/telecom-pulse <country>` — `.claude/commands/telecom-pulse.md`

Monthly competitive-intelligence brief for one of seven configured telecom markets (Austria, Croatia, Serbia, Slovenia, Macedonia, Belarus, Bulgaria). Per-country files live under `baselines/<country>/`:

- `baseline.md` — stable structural snapshot; only overwritten on the expensive `--refresh-baseline` path (5 search angles, 18-month lookback), and only when a merger/entry/exit/spectrum/wholesale event warrants it.
- `<YYYY>.md` — rolling current-year pulse log. **Editing rule: replace only the three sections (Year so far / Last 90 days / Outlook) under the current month's heading. Never delete prior months' entries.**
- `sources.md` — append-only dated source log; mark earnings PDFs, regulator notices, and official releases with `[PRIMARY]`.
- `<country>-<YYYY-MM>.pdf` — exported brief (HTML template is in the skill; the intermediate HTML is deleted after conversion).

The pulse is meant to be **directional** (a verdict on competitive intensity: Intensifying / Stable / Easing), every claim sourced and dated, output kept under 600 words.

### `/karpathy-llm-wiki` — `.claude/commands/karpathy-llm-wiki.md`

A personal LLM-maintained knowledge base (directories not yet created in this repo; initialized on first ingest). Two layers: `raw/` is immutable source material (read, never modify); `wiki/` is Claude-owned compiled articles plus `wiki/index.md` and append-only `wiki/log.md`. **Link convention: inside `wiki/` files use paths relative to the current file (e.g. `../../raw/<topic>/<file>.md`); in conversation output use project-root-relative paths.** `wiki/` allows one level of topic subdirectories only.

## Standalone files

- `suno.md` — reference cheat-sheet for writing Suno song prompts. Core rule it documents: Suno has two separate fields — **Style** (sound/genre/instruments only) and **Lyrics** (text + `[ ]` structure tags + `( )` ad-libs only); never mix sound descriptions into the lyrics field.
- `wm_song.md` — a creative artifact (Austrian World Cup song lyrics), written per the `suno.md` conventions.
