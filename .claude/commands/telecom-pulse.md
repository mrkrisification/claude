---
name: telecom-pulse
description: "Monthly competitive intelligence pulse for a national telecommunications market. Run when asked for a telecom market update, competitive briefing, or market pulse for any of the configured markets (Austria, Croatia, Serbia, Slovenia, Macedonia, Belarus, Bulgaria). Pass the country name as the argument."
---

# Telecom Market Pulse

Produce a monthly competitive intelligence brief for a national telecom market. Anchored to a stable baseline; focused on what changed in the last 90 days and where the market is heading.

## Configuration

Supported markets and their operators:

| Country | Operators |
|---|---|
| Slovenia | Telekom Slovenije, A1 Slovenia, Telemach, T-2 |
| Austria | A1 Telekom Austria, Magenta Telekom (T-Mobile), Drei (Hutchison) |
| Croatia | Hrvatski Telekom (HT), A1 Croatia, Telemach Croatia, Tele2 Croatia |
| Serbia | Telekom Srbija, A1 Serbia (formerly Vip), Yettel Serbia (formerly Telenor) |
| Macedonia | Makedonski Telekom, A1 Macedonia (formerly One), Lycamobile |
| Belarus | A1 Belarus, MTS Belarus, life:) (Turkcell) |
| Bulgaria | Vivacom, A1 Bulgaria, Yettel Bulgaria (formerly Telenor) |

Baseline files live at: `baselines/<country>/baseline.md`
Current-year log lives at: `baselines/<country>/<YYYY>.md`

---

## Workflow

### Step 1 — Load context

1. Derive the country slug from the args (lowercase, no spaces).
2. Read `baselines/<country>/baseline.md`. If it does not exist, note that and proceed without it — the synthesis will flag that a baseline needs to be created after this run.
3. Read `baselines/<country>/<current-year>.md` if it exists. This gives you the year-so-far arc.

### Step 2 — Search (3 parallel agents)

Launch exactly 3 agents in parallel. Pass the country name and operator list as context. Each agent runs 2–3 web searches and returns: URLs, publication dates, and key facts/quotes. Instruct agents to focus strictly on the last 90 days and to return concise findings (no padding).

**Angle A — Pricing & retail competition**
Search for: price changes, new tariff launches, bundle promotions, unlimited data moves, switching incentives, ARPU commentary. Query variants: "[country] telecom price [year]", "[operator] tariff promotion [recent months]", "[country] mobile bundle offer [year]".

**Angle B — M&A, earnings & executive commentary**
Search for: merger activity, acquisition announcements, quarterly earnings results, exec quotes on competitive pressure, parent-group commentary on the market, analyst ratings. Query variants: "[operator] results [quarter] [year]", "[country] telecom merger acquisition [year]", "[operator] competitive pressure [year]".

**Angle C — Regulatory & infrastructure**
Search for: regulator decisions (spectrum, wholesale access, merger approvals/blocks), 5G/fiber rollout announcements, coverage claims, EU-level actions affecting the market. Query variants: "[country] telecom regulator [year]", "[country] 5G rollout [year]", "[country] telecom spectrum [year]".

### Step 3 — Synthesize

Do not fetch additional URLs unless a search snippet references a primary source (earnings PDF, regulator notice) where the snippet alone is insufficient for a factual claim. Maximum 3 additional fetches.

Write the output directly — do not create intermediate notes or planning documents.

---

## Output format

Write the output to `baselines/<country>/<YYYY>.md`. If the file exists, replace only the three sections below (Year so far, Last 90 days, Outlook) under the current month's heading — do not delete previous months' entries.

```markdown
## <YYYY-MM> — <Month Name>

### Year so far
[2–3 sentences. Cumulative arc from January to now: what the dominant competitive dynamic has been, who has gained/lost ground, what structural event (if any) defined the year. Rewrite this section each month — it is a rolling summary, not a log.]

### Last 90 days
[4–6 bullet points. Each bullet: one signal, one source, one sentence on what it implies for competitive intensity. Format: **[Signal type]** — description. (Source, date)]

**Directional verdict:** [one of: Intensifying / Stable / Easing] — [one sentence explaining the primary driver]

### Outlook to year-end
[3 bullet points max. Each: one pending event or decision, when it is expected, and which direction it would push competition if it lands. Be explicit about uncertainty.]
```

---

## Baseline refresh rule

At the end of synthesis, check whether any of the following occurred in the last 90 days:
- A merger completed or was definitively blocked
- A new operator entered or exited the market
- A major spectrum auction concluded
- A significant wholesale access ruling changed market dynamics

If yes, append a single line at the bottom of the year file:
`> **Baseline refresh recommended** — [reason]. Run /telecom-pulse [country] --refresh-baseline to update.`

The `--refresh-baseline` flag triggers a deeper run: 5 search angles, lookback 18 months, output written to `baselines/<country>/baseline.md` (overwrites). This is the expensive path — use it only when flagged.

---

## Tone and constraints

- Be directional. The purpose is an opinion on competitive intensity, not a neutral summary.
- Cite every factual claim with a source and date. If something cannot be sourced, do not include it.
- Keep the total output under 600 words. Brevity is a feature.
- If the baseline file is missing, note it prominently and still produce the pulse from search alone.
- Do not produce a PDF unless the user explicitly asks.
