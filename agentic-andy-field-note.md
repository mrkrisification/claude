---
type: Field Note
title: A Working "Second Brain" in Production — Dr. Andreas Muzik
description: Briefing for the knowledge initiative team. Field notes from a practitioner running a personal agentic second brain ("Agentic Andy") and sharing parts of it across his organization.
tags: [second-brain, okf, karpathy-wiki, claude-code, skills, knowledge-initiative]
source: Personal notes, captured 2026-06-22 (unstructured, reconstructed via Q&A)
status: draft
timestamp: 2026-06-22
---

# Field Note: A Working "Second Brain" in Production

**Dr. Andreas Muzik** — IT consulting / systems-integration firm (clients: banks & financial institutions)

> Purpose: briefing for the knowledge initiative team.

## Why he built it

The firm's traditional integration business is **falling behind**, which is the driver: he's
using an AI-augmented personal knowledge system both to stay ahead personally **and** to seed a
sharing model across the organization. This is not a prototype — it's running daily, and ~⅓ of
the company is already on the tooling.

## The system — "Agentic Andy"

- His personal second-brain **agent**, named "Agentic Andy."
- Built on **Claude Code inside VS Code** — an agent with real file access, not a chat UI
  (consistent with the "building needs file-system access" point from the OKF/Karpathy deck).
- **`_AA`** is his naming convention for the `.md` files exposed to the agent — the
  "Agentic Andy" layer the agent reads and maintains, sitting in parallel to his own
  human-authored files.

## Architecture lineage

- **Inspired by Karpathy's LLM-wiki pattern** (the actual basis), with awareness of **gbrain**
  ([garrytan/gbrain](https://github.com/garrytan/gbrain) — a heavier "knowledge synthesis layer":
  self-wiring knowledge graph + hybrid retrieval + cited synthesis, 24/7 enrichment). He is
  **not** doing the full gbrain approach — his is lighter and closer to Karpathy.
- Crucially: **there is no database.** The entire "memory" is just `.md` files.
  ("Integrate into the Database" in the raw notes = simply promoting a verified MD file into the
  official memory folder.)

## The knowledge pipeline

1. **Ingest** — records & transcribes meetings; ingests docs and reference lists (team members,
   customers, etc.). A **filename-based hook** auto-converts inputs into markdown.
2. **Verify gate** — the human-in-the-loop control. He marks a **`verified` checkbox inside the
   MD file** to release it into "official" memory. The gate is **hybrid** — over time some
   verification became agent-assisted, but the `verified` flag is the release mechanism.
3. **Structure & baseline** — all `.md`, in a structure he defined himself; the `_AA` summary
   layer is **maintained / updated by the agents**.
4. **Execution** — **Docker on his machine runs the agent jobs** (background processing /
   enrichment).
5. **Skills** — packaged know-how in the **`SKILL.md`** sense. These are reusable and
   **adaptable** — e.g. he forked a **market-research skill into a due-diligence skill**.

## Organizational structure & sharing

- Knowledge lives on **OneDrive**, organized as **Market / Portfolio / Platform**; a single MD
  file follows that structure (the "stupid simple" backbone everyone understands).
- A team, **GSE**, has its **own space and its own skill** — i.e. each unit can get its own slice
  + tailored skill.
- **~20 admins** can see all files on the share. They act as curators: they **extract reusable
  pieces (especially skills) and publish them to GitHub**, which makes them available to all
  **Claude Code Desktop** users in the org.
- **Adoption:** ~**200 of 550** employees (~⅓) use Claude Desktop; ~**20** are the active
  curators / sharers.

## The two-layer takeaway (ties back to the deck)

- **Personal layer:** an agentic, file-based, verify-gated wiki ("Agentic Andy") — markdown +
  git / OneDrive, no DB.
- **Org layer:** curators mirror knowledge via OneDrive and **distribute capability as shareable
  skills via GitHub** — exactly the "combine individual wikis into corporate knowledge" pattern,
  with **skills as the unit of reuse** rather than a meta-wiki.

## Still open / didn't cover

- **Security model** — not detailed (notable given banking / financial clients): what's shareable
  org-wide vs. kept private, and how client-confidential material is walled off.
- Whether consumers can **write back** or only read.

## Notes on reconstruction

- Raw notes were unstructured; reconstructed via Q&A with the note-taker.
- Two judgment calls: "integrate into Database" is read as *promote-to-official-memory* (there is
  no DB), and the ~20 "admins" and ~20 "active sharers" are treated as the **same curator group**.
