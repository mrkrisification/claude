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
Source log lives at: `baselines/<country>/sources.md`

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

## Source logging

After writing the pulse output, append a dated block to `baselines/<country>/sources.md`. Create the file if it does not exist.

Each block lists every URL returned by the search agents, deduplicated. Mark primary documents (earnings PDFs, regulator notices, official press releases) with `[PRIMARY]` — these are most likely to move or go behind a paywall and worth downloading manually if needed later.

```markdown
## <YYYY-MM> — <Month Name>

### Pricing & retail competition
- [Title](URL) — Publication, YYYY-MM-DD
- [PRIMARY] [Title](URL) — Source, YYYY-MM-DD

### M&A, earnings & executive commentary
- [Title](URL) — Publication, YYYY-MM-DD

### Regulatory & infrastructure
- [PRIMARY] [Title](URL) — Regulator/Source, YYYY-MM-DD
```

Do not include URLs that returned no usable content.

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

## PDF export

After writing all files, generate a PDF brief and send it to the user.

1. Write a self-contained HTML file to `baselines/<country>/<country>-<YYYY-MM>.html` using the template below.
2. Convert to PDF using WeasyPrint: `python3 -m weasyprint <html_path> <pdf_path>` where the PDF path is `baselines/<country>/<country>-<YYYY-MM>.pdf`.
3. Send the PDF to the user with `SendUserFile`.
4. Delete the intermediate HTML file after successful conversion.

### HTML template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 10.5pt; line-height: 1.6; color: #1a1a2e; margin: 0; padding: 0; }
  .cover { page-break-after: always; padding: 60px 64px; background: linear-gradient(160deg, #0f3460 0%, #1a1a2e 100%); color: white; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; }
  .cover-label { font-size: 8pt; letter-spacing: 0.2em; text-transform: uppercase; color: #a0c4ff; margin-bottom: 24px; }
  .cover-title { font-size: 26pt; font-weight: 700; line-height: 1.2; margin-bottom: 16px; }
  .cover-subtitle { font-size: 12pt; font-weight: 300; color: #a0c4ff; border-left: 3px solid #4cc9f0; padding-left: 14px; margin-bottom: 48px; }
  .cover-meta { font-size: 8.5pt; color: #7a8ba8; margin-top: auto; padding-top: 32px; border-top: 1px solid #2a3f6f; }
  .cover-meta span { display: block; margin-bottom: 3px; }
  .content { padding: 48px 64px; }
  h1 { font-size: 15pt; font-weight: 700; color: #0f3460; border-bottom: 2px solid #0f3460; padding-bottom: 6px; margin: 32px 0 12px; }
  h1.first { margin-top: 0; }
  h2 { font-size: 11pt; font-weight: 600; color: #0f3460; margin: 24px 0 8px; }
  p { margin-bottom: 10px; }
  ul { margin: 8px 0 14px 0; padding-left: 20px; }
  li { margin-bottom: 6px; }
  .verdict { border-left: 5px solid #e63946; background: #fff0f0; padding: 14px 18px; border-radius: 4px; margin: 16px 0; }
  .verdict.stable { border-color: #2dc653; background: #f0fff4; }
  .verdict.easing { border-color: #4cc9f0; background: #f0faff; }
  .verdict-label { font-size: 7.5pt; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #666; margin-bottom: 4px; }
  .verdict-text { font-size: 12pt; font-weight: 600; }
  table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 9pt; }
  thead tr { background: #0f3460; color: white; }
  th { padding: 8px 11px; text-align: left; font-size: 8.5pt; }
  tbody tr:nth-child(even) { background: #f4f7fb; }
  td { padding: 7px 11px; border-bottom: 1px solid #e0e7ef; vertical-align: top; }
  .sources { font-size: 8pt; color: #666; margin-top: 32px; padding-top: 14px; border-top: 1px solid #ddd; }
  .sources a { color: #0f3460; text-decoration: none; }
  .sources p { margin-bottom: 3px; }
  a { color: #0f3460; }
</style>
</head>
<body>

<div class="cover">
  <div class="cover-label">Telecom Market Intelligence — Monthly Pulse</div>
  <div class="cover-title">[COUNTRY] Telecommunications Market</div>
  <div class="cover-subtitle">[MONTH YEAR] — Competitive Intensity Brief</div>
  <div class="cover-meta">
    <span><strong>Run date:</strong> [DATE]</span>
    <span><strong>Operators covered:</strong> [OPERATORS]</span>
    <span><strong>Research window:</strong> Last 90 days</span>
  </div>
</div>

<div class="content">

<h1 class="first">Year So Far</h1>
<p>[YEAR SO FAR TEXT]</p>

<h1>Last 90 Days</h1>

<div class="verdict [VERDICT_CLASS]">
  <div class="verdict-label">Directional Verdict</div>
  <div class="verdict-text">[VERDICT] — [VERDICT EXPLANATION]</div>
</div>

<ul>
[BULLET POINTS AS <li> ITEMS — each bullet becomes one <li>, stripping markdown bold markers and converting source links to HTML <a> tags]
</ul>

<h1>Outlook to Year-End</h1>
<ul>
[OUTLOOK BULLETS AS <li> ITEMS]
</ul>

<div class="sources">
<strong>Sources</strong><br>
[ALL URLS FROM THIS RUN AS <p><a href="URL">TITLE</a> — Publication, Date</p> LINES]
</div>

</div>
</body>
</html>
```

For `[VERDICT_CLASS]`: use `intensifying` when verdict is Intensifying, `stable` when Stable, `easing` when Easing.

---

## Tone and constraints

- Be directional. The purpose is an opinion on competitive intensity, not a neutral summary.
- Cite every factual claim with a source and date. If something cannot be sourced, do not include it.
- Keep the pulse text output under 600 words. Brevity is a feature.
- If the baseline file is missing, note it prominently and still produce the pulse from search alone.
