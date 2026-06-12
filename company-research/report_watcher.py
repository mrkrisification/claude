#!/usr/bin/env python3
"""
report_watcher.py — detect & download newly published company reports.

Job: check a company's investor-relations / reports page, find report documents
(quarterly results, full-year results, annual reports, presentations …), figure
out which are NEW since last run, and download them — at runtime, on demand.

Discovery goes through Firecrawl (operator/IR sites block this environment's
direct fetch paths). Downloads try a direct fetch first, then fall back to
Firecrawl so even Cloudflare-protected files are captured (as parsed markdown
when raw bytes are unavailable).

Two phases so an agent can apply judgment in between:

  check     discover candidate report URLs, diff against the ledger,
            print the NEW ones as JSON. Nothing is written.

  download  fetch chosen URLs (or every new candidate with --all), save into
            the company's raw/ folder, and record them in the ledger so they
            are not re-downloaded next time.

Config: report_watcher.config.json (see report_watcher.config.example.json),
mapping company slugs to their reports page(s) and optional matching hints.

Usage:
  export FIRECRAWL_API_KEY=fc-...        # or rely on ./.env
  python3 report_watcher.py check    <slug> [--json]
  python3 report_watcher.py download <slug> --url <URL> [--url <URL> ...]
  python3 report_watcher.py download <slug> --all      # every new candidate
  python3 report_watcher.py list     <slug>            # show ledger

Exit codes: 0 ok · 1 usage/config error · 2 Firecrawl unreachable.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
FIRECRAWL_BASE = "https://api.firecrawl.dev/v2"

# Period-specific tokens that mark a URL as a *particular* report document
# (not just a section landing page). Tunable per-company via the config's
# "patterns" list (added on top of these defaults).
DEFAULT_PATTERNS = [
    r"q[1-4][\s_/-]?20\d{2}",            # q1-2026, q4_2024
    r"20\d{2}[\s_/-]?q[1-4]",            # 2026-q1
    r"h[12][\s_/-]?20\d{2}",             # h1-2024
    r"\b(fy|full[\s_/-]?year)[\s_/-]?20\d{2}",  # fy2024, full-year-2024
    r"annual[\s_/-]?report[\s_/-]?20\d{2}",
    r"(half[\s_/-]?year|interim).{0,20}(20\d{2}|q[1-4])",
    r"(quarterly|quarter).{0,20}(20\d{2}|q[1-4])",
]

FILE_EXTS = (".pdf", ".xlsx", ".xls", ".doc", ".docx")


# ---------------------------------------------------------------------------
# key loading & config
# ---------------------------------------------------------------------------
def load_api_key() -> str:
    key = os.environ.get("FIRECRAWL_API_KEY")
    if key:
        return key
    env = ROOT.parent / ".env"
    if env.is_file():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line.startswith("FIRECRAWL_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("FIRECRAWL_API_KEY not set (env var or ./.env) — see company-research/README.md")


def load_config(required: bool = True) -> dict:
    cfg = ROOT / "report_watcher.config.json"
    if not cfg.is_file():
        if not required:                 # ad-hoc --page mode needs no config file
            return {"companies": {}}
        sys.exit(
            f"No config at {cfg}. Copy report_watcher.config.example.json and edit it, "
            f"or pass --page <ir-reports-url> for ad-hoc use."
        )
    return json.loads(cfg.read_text())


def company_cfg(cfg: dict, slug: str, pages: list[str] | None = None) -> dict:
    """Resolve a company. With `pages` (ad-hoc IR reports URLs) no config entry is
    needed — the agent passes the page(s) directly; config values, if any, are merged."""
    companies = cfg.get("companies", {})
    c = dict(companies.get(slug, {}))
    if pages:
        c["urls"] = list(pages)          # ad-hoc overrides config urls
    else:
        c["urls"] = c.get("urls") or ([c["url"]] if c.get("url") else [])
    if not c["urls"]:
        if slug not in companies:
            sys.exit(f"Unknown company '{slug}'. Pass --page <ir-reports-url>, or add it to config. "
                     f"Known: {', '.join(sorted(companies)) or '(none)'}")
        sys.exit(f"Company '{slug}' has no 'url'/'urls' in config — pass --page <ir-reports-url>.")
    return c


def load_regulators() -> dict:
    """Registry of national regulators (publications page(s), official domain(s), match
    patterns). Committed reference data — unlike the per-company runtime config."""
    reg = ROOT / "regulators.json"
    if not reg.is_file():
        return {"regulators": {}}
    return json.loads(reg.read_text())


def regulator_cfg(regs: dict, code: str) -> dict:
    """Resolve one regulator into the same {urls, patterns, domains} shape company_cfg yields."""
    r = dict(regs[code])
    r["urls"] = r.get("urls") or ([r["url"]] if r.get("url") else [])
    if not r["urls"]:
        sys.exit(f"Regulator '{code}' has no 'url'/'urls' in regulators.json.")
    if not r.get("domains"):
        r["domains"] = [registrable_domain(u) for u in r["urls"]]
    return r


# ---------------------------------------------------------------------------
# Firecrawl
# ---------------------------------------------------------------------------
def _firecrawl(path: str, payload: dict, key: str, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        f"{FIRECRAWL_BASE}/{path}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        if e.code in (401, 403) and "allowlist" in body.lower():
            sys.exit(f"[2] Firecrawl unreachable: {body}\n→ allowlist api.firecrawl.dev (README step 2).")
        if e.code == 402:
            sys.exit("[2] Firecrawl out of credits (HTTP 402). Top up at firecrawl.dev/pricing, "
                     "then re-run — the ledger resumes where it stopped.")
        raise SystemExit(f"[2] Firecrawl HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise SystemExit(f"[2] Firecrawl network error: {e.reason}")


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
}


class _AnchorParser(HTMLParser):
    """Collect every <a href> on a page."""
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)


def direct_discover(urls: list[str]) -> tuple[set[str], set[str], set[str], set[str]]:
    """Free discovery: fetch each IR page directly and parse its anchors locally.

    Works only when the page's host is reachable (egress-allowlisted and not
    bot-blocked) *and* serves the document links in static HTML. Returns
    (links, doc_hosts, blocked_hosts, productive_urls):
      - blocked_hosts are the IR-page hosts we could not fetch (allowlist candidates).
      - productive_urls are the IR pages that yielded at least one document-file
        link directly; pages absent from this set (unreachable, or JS-rendered
        single-page apps that inject links client-side) need the Firecrawl fallback.
    """
    links: set[str] = set()
    doc_hosts: set[str] = set()
    blocked: set[str] = set()
    productive: set[str] = set()
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=BROWSER_HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                ctype = r.headers.get("Content-Type", "")
                if "html" not in ctype.lower():
                    blocked.add(registrable_domain(url))   # not parseable HTML
                    continue
                html = r.read().decode("utf-8", errors="replace")
        except Exception:
            blocked.add(registrable_domain(url))
            continue
        p = _AnchorParser()
        p.feed(html)
        for href in p.hrefs:
            absu = urljoin(url, href)
            if not absu.lower().startswith("http"):
                continue
            links.add(absu)
            if absu.split("#", 1)[0].split("?", 1)[0].lower().endswith(FILE_EXTS):
                doc_hosts.add(registrable_domain(absu))
                productive.add(url)
    return links, doc_hosts, blocked, productive


DEFAULT_MAP_SEARCH = "report results quarterly annual"


def discover_links(urls: list[str], key: str, firecrawl_ok: bool = True,
                   search: str = DEFAULT_MAP_SEARCH) -> tuple[list[str], set[str], set[str]]:
    """Enumerate candidate links from each reports page.

    Free direct-HTML discovery first, then Firecrawl:
      - whole-site `map` (with the `search` hint) surfaces documents buried levels below a
        landing page — run for any page that yielded no doc directly, and ALWAYS when an
        explicit (non-default) `search` hint is set, since regulator landing pages often
        link a few incidental PDFs (glossaries) yet bury the real reports a level down;
      - per-page `scrape` (waitFor) catches client-rendered SPAs that inject links via JS.
    `doc_hosts` are registrable domains documents live on (e.g. q4cdn.com) — trusted as
    official. `blocked_hosts` are hosts that could not be fetched directly (allowlist hints).
    """
    found, doc_hosts, blocked_hosts, productive = direct_discover(urls)
    nonproductive = [u for u in urls if u not in productive]
    explicit_search = search != DEFAULT_MAP_SEARCH
    if firecrawl_ok and (nonproductive or explicit_search):
        # origins to map: all pages when an explicit hint is set, else just the empty ones
        map_targets = urls if explicit_search else nonproductive
        origins: list[str] = []
        for u in map_targets:
            sp = urlsplit(u)
            o = f"{sp.scheme}://{sp.netloc}"
            if o not in origins:
                origins.append(o)
        for origin in origins:
            try:
                m = _firecrawl("map", {"url": origin, "search": search, "limit": 300}, key)
                for link in m.get("links", []):
                    href = link.get("url") if isinstance(link, dict) else link
                    if href:
                        found.add(href)
                        if _is_doc(href):
                            doc_hosts.add(registrable_domain(href))
            except SystemExit as e:
                print(f"  (Firecrawl map unavailable for {origin}: {e})")
        for url in nonproductive:                # SPA link injection on the actual page
            try:
                s = _firecrawl("scrape", {"url": url, "formats": ["links"], "waitFor": 8000}, key)
                data = s.get("data", s)
                for href in data.get("links", []) or []:
                    if href:
                        found.add(href)
                        if _is_doc(href):
                            doc_hosts.add(registrable_domain(href))
                blocked_hosts.discard(registrable_domain(url))   # Firecrawl rescued it
            except SystemExit as e:
                print(f"  (Firecrawl scrape unavailable for {url}: {e})")
    # drop in-page fragments and the reports pages themselves
    bases = {u.rstrip("/") for u in urls}
    cleaned = {h.split("#", 1)[0].rstrip("/") for h in found if h}
    return sorted(h for h in cleaned if h and h not in bases), doc_hosts, blocked_hosts


def _is_doc(url: str) -> bool:
    return url.split("#", 1)[0].split("?", 1)[0].lower().endswith(FILE_EXTS)


def expand_detail_pages(links: list[str], key: str, patterns: list[str], domains: set[str],
                        firecrawl_ok: bool = True, max_years: int = 0,
                        max_pages: int = 40) -> tuple[set[str], set[str]]:
    """Second hop for regulator-style sites that list report *detail* pages, not the PDF
    itself. Follow on-domain, pattern-matching detail links (bounded by `max_years` and
    `max_pages`) and harvest the document files they link. Returns (doc_urls, doc_hosts).

    Direct fetch first (free); Firecrawl scrape per page only if the host is blocked.
    """
    detail = [u for u in dict.fromkeys(links)
              if registrable_domain(u) in domains and not _is_doc(u)
              and _matches_pattern(u, patterns) and within_year_window(u, max_years)]
    detail = detail[:max_pages]
    docs: set[str] = set()
    doc_hosts: set[str] = set()
    for du in detail:
        sub, _dh, _blocked, _prod = direct_discover([du])
        if not any(_is_doc(h) for h in sub) and firecrawl_ok:
            try:                                  # static DOM had no doc link — render it
                s = _firecrawl("scrape", {"url": du, "formats": ["links"], "waitFor": 6000}, key)
                data = s.get("data", s)
                sub |= {h for h in (data.get("links", []) or []) if h}
            except SystemExit:
                pass
        for h in sub:
            if _is_doc(h) and registrable_domain(h) in domains:
                docs.add(h.split("#", 1)[0])
                doc_hosts.add(registrable_domain(h))
    return docs, doc_hosts


def discover_all(urls: list[str], key: str, patterns: list[str], domains: set[str],
                 firecrawl_ok: bool = True, two_hop: bool = False,
                 max_years: int = 0, search: str | None = None) -> tuple[list[str], set[str], set[str]]:
    """discover_links, optionally plus a second hop through report detail pages
    (`two_hop`, used for regulator targets). `search` is an optional Firecrawl map hint
    (per-regulator, for deep sites). Returns (links, doc_hosts, blocked_hosts)."""
    kw = {"search": search} if search else {}
    links, doc_hosts, blocked = discover_links(urls, key, firecrawl_ok=firecrawl_ok, **kw)
    if two_hop:
        follow_domains = {registrable_domain(d) for d in domains} | doc_hosts
        docs, dh2 = expand_detail_pages(links, key, patterns, follow_domains,
                                        firecrawl_ok=firecrawl_ok, max_years=max_years)
        links = sorted(set(links) | docs)
        doc_hosts |= dh2
    return links, doc_hosts, blocked


# ---------------------------------------------------------------------------
# matching & ledger
# ---------------------------------------------------------------------------
# Path markers that are clearly not a report document (event listings, nav…).
EXCLUDE = ("financial-calendar", "/events/", "/event/", "/glossary", "/sitemap")


def is_report(url: str, patterns: list[str]) -> bool:
    u = url.split("#", 1)[0].lower()          # ignore in-page fragments
    if any(x in u for x in EXCLUDE):
        return False
    period = any(re.search(p, u) for p in patterns)
    # 1) any document file is a candidate (a bare .pdf almost always is a report)
    if u.endswith(FILE_EXTS):
        return True
    # 2) a /download endpoint that also names a period
    if "/download" in u and period:
        return True
    # 3) a non-file URL only counts when it names a *specific* period —
    #    this excludes section landing pages like .../financial-results-2019
    return period and ("report" in u or "result" in u or "interim" in u or "/q" in u)


def registrable_domain(url_or_host: str) -> str:
    """Best-effort registrable domain (last two labels, e.g. report.telekom.com -> telekom.com)."""
    host = urlsplit(url_or_host).netloc or url_or_host
    host = host.split("@")[-1].split(":")[0].lower().lstrip(".")
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def allowed_domains(cfg_company: dict) -> set[str]:
    """Official domains we'll download from: explicit config list, else derived from the IR URLs."""
    explicit = cfg_company.get("domains")
    if explicit:
        return {registrable_domain(d) for d in explicit}
    return {registrable_domain(u) for u in cfg_company["urls"]}


def _matches_pattern(url: str, patterns: list[str]) -> bool:
    u = url.split("#", 1)[0].lower()
    return any(re.search(p, u) for p in patterns)


def _url_year(url: str) -> int | None:
    """Best guess of the document's year. Prefer the filename (basename) — the report period
    lives there — over the full URL, whose directory path often carries an unrelated CDN
    upload year (e.g. /wp-content/uploads/2023/08/Annual_Report_2012.pdf → 2012, not 2023)."""
    base = urlsplit(url).path.rsplit("/", 1)[-1]
    for scope in (base, url):
        years = [int(y) for y in re.findall(r"20\d{2}", scope)]
        if years:
            return max(years)
    return None


def within_year_window(url: str, max_years: int) -> bool:
    """True if the URL is recent enough. URLs with no detectable 20xx year (e.g. `1Q26`)
    always pass, so quarter-coded current releases are never dropped by the history bound."""
    if not max_years:
        return True
    y = _url_year(url)
    if y is None:
        return True
    return y >= _dt.date.today().year - max_years + 1


def select_candidates(links: list[str], patterns: list[str], domains: set[str],
                      require_pattern: bool = False, max_years: int = 0) -> list[str]:
    """Report-like links on an official domain.

    `require_pattern` (used for noisy regulator sites): a bare document file must *also* match
    one of `patterns` — without it, `is_report` accepts any `.pdf`, which on a regulator page
    pulls user manuals and unrelated PDFs into the cache. `max_years` bounds history (see
    `within_year_window`)."""
    out = []
    for u in links:
        if registrable_domain(u) not in domains:
            continue
        if not is_report(u, patterns):
            continue
        if require_pattern and not _matches_pattern(u, patterns):
            continue
        if not within_year_window(u, max_years):
            continue
        out.append(u)
    return out


ALLOWLIST_FILE = ROOT / "allowlist.txt"


def record_allowlist(hosts: set[str]) -> list[str]:
    """Merge blocked hosts into a paste-ready allowlist file (one domain/line, the exact
    format the web UI's Custom 'Allowed domains' field expects). Returns newly-added hosts.
    The agent can't apply the allowlist (it's a web-UI security boundary) — this just keeps
    the list curated so the user pastes it in one go."""
    if not hosts:
        return []
    existing: set[str] = set()
    if ALLOWLIST_FILE.is_file():
        existing = {ln.strip() for ln in ALLOWLIST_FILE.read_text().splitlines()
                    if ln.strip() and not ln.startswith("#")}
    new = sorted(h for h in hosts if h and h not in existing)
    if new:
        header = (f"# Paste these into the environment's Network access → Custom → Allowed domains.\n"
                  f"# Maintained by report_watcher.py; updated {_dt.date.today().isoformat()}.\n")
        lines = sorted(existing | set(new))
        ALLOWLIST_FILE.write_text(header + "\n".join(lines) + "\n")
    return new


# A collection target: a base directory under ROOT with its own raw/ archive and ledger.
# Companies live at ROOT/<slug>/; regulators share one cache at ROOT/_regulators/<code>/.
class Target:
    def __init__(self, base: Path, label: str):
        self.base = base          # e.g. ROOT/"america-movil" or ROOT/"_regulators"/"ift"
        self.label = label        # human label for log lines / ledger id

    @property
    def raw(self) -> Path:
        return self.base / "raw"

    @property
    def ledger_file(self) -> Path:
        return self.base / "reports" / "ledger.json"


def company_target(slug: str) -> Target:
    return Target(ROOT / slug, slug)


def regulator_target(code: str) -> Target:
    return Target(ROOT / "_regulators" / code, f"regulator:{code}")


def load_ledger(t: Target) -> dict:
    if t.ledger_file.is_file():
        return json.loads(t.ledger_file.read_text())
    return {"id": t.label, "downloaded": {}}


def save_ledger(t: Target, ledger: dict) -> None:
    t.ledger_file.parent.mkdir(parents=True, exist_ok=True)
    t.ledger_file.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------
def safe_name(url: str) -> str:
    base = re.sub(r"[?#].*$", "", url).rstrip("/").rsplit("/", 1)[-1] or "report"
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    if not base.lower().endswith((".pdf", ".xlsx", ".xls", ".doc", ".docx")):
        base += ".pdf"
    return f"{_dt.date.today().isoformat()}-{base}"


def is_large_report(url: str) -> bool:
    """Heuristic: URL looks like a big multi-hundred-page document (annual report / 20-F /
    integrated report / data book) — too expensive to auto-parse via Firecrawl."""
    u = url.lower()
    return bool(re.search(r"annual[-_]?report|20[-_]?f|integrated[-_]?report|"
                          r"universal[-_]?registration|/ar/|data[-_]?book", u))


def direct_download(url: str, dest: Path) -> bool:
    """Try a plain fetch with browsery headers. Returns True if a real doc landed."""
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            ctype = r.headers.get("Content-Type", "")
            blob = r.read()
        if blob[:4] == b"%PDF" or "pdf" in ctype.lower() or url.lower().endswith((".xlsx", ".xls", ".doc", ".docx")):
            dest.write_bytes(blob)
            return True
    except Exception:
        return False
    return False


def firecrawl_capture(url: str, dest: Path, key: str) -> tuple[Path, int]:
    """Fallback: have Firecrawl fetch+parse, save parsed markdown as a .md sidecar.

    PAID: Firecrawl bills ~1 credit per PDF page. Returns (path, est_pages) so the
    caller can surface the spend.
    """
    s = _firecrawl("scrape", {"url": url, "formats": ["markdown"], "parsers": ["pdf"]}, key)
    data = s.get("data", s)
    md = data.get("markdown", "") or ""
    meta = data.get("metadata", {}) or {}
    # prefer reported page count; else a rough estimate (~3k chars/page)
    est_pages = meta.get("numPages") or meta.get("pageCount") or max(1, round(len(md) / 3000))
    md_dest = dest.with_suffix(".md")
    header = f"<!-- source: {url}\n     captured: {_dt.datetime.now().isoformat()}\n     via: firecrawl (raw bytes unavailable) -->\n\n"
    md_dest.write_text(header + md)
    return md_dest, int(est_pages)


def download_one(url: str, t: Target, key: str, firecrawl_ok: bool) -> dict:
    """Fetch one report. Direct download (free) is always tried first. Firecrawl
    PDF-parsing (PAID, ~1 credit/page) runs only when firecrawl_ok; otherwise the URL
    is deferred and nothing is spent. A Firecrawl 402 degrades to deferred, not a crash."""
    dest_dir = t.raw
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / safe_name(url)
    host = registrable_domain(url)
    if direct_download(url, dest):
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()[:16]
        return {"url": url, "file": str(dest.relative_to(ROOT)), "method": "direct", "sha256_16": digest}
    if not firecrawl_ok:
        return {"url": url, "status": "deferred", "method": "direct-blocked", "host": host}
    try:
        saved, est_pages = firecrawl_capture(url, dest, key)
    except SystemExit as e:                 # e.g. 402 out of credits
        return {"url": url, "status": "deferred", "method": "firecrawl-unavailable",
                "host": host, "reason": str(e)}
    return {"url": url, "file": str(saved.relative_to(ROOT)), "method": "firecrawl-parsed",
            "est_credits": est_pages}


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def _check(t: Target, c: dict, args, require_pattern: bool = False, two_hop: bool = False) -> int:
    """Read-only discovery: print new vs seen candidates for one target."""
    key = load_api_key()
    # Regulator targets (require_pattern) match ONLY the registry's specific patterns — not the
    # generic period defaults — so HTML detail pages / off-sector docs are excluded.
    patterns = c.get("patterns", []) if require_pattern else DEFAULT_PATTERNS + c.get("patterns", [])
    ledger = load_ledger(t)
    seen = set(ledger.get("downloaded", {}))
    max_years = getattr(args, "max_years", 0)

    base_domains = allowed_domains(c)
    links, doc_hosts, blocked = discover_all(c["urls"], key, patterns, base_domains,
                                             firecrawl_ok=not args.no_firecrawl,
                                             two_hop=two_hop, max_years=max_years,
                                             search=c.get("search"))
    domains = base_domains | doc_hosts
    candidates = select_candidates(links, patterns, domains,
                                   require_pattern=require_pattern, max_years=max_years)
    new = [u for u in candidates if u not in seen]

    if getattr(args, "json", False):
        print(json.dumps({"target": t.label, "new": new, "all_candidates": candidates,
                          "blocked_hosts": sorted(blocked)}, indent=2))
    else:
        print(f"# {t.label}: {len(new)} new of {len(candidates)} report candidate(s)\n")
        for u in new:
            print(f"  NEW   {u}")
        for u in candidates:
            if u in seen:
                print(f"  seen  {u}")
        if not candidates:
            print("  (no report-like links found — check the URL / add 'patterns' in config)")
    if blocked:
        record_allowlist(blocked)
        print(f"\nAllowlist to go Firecrawl-free: {', '.join(sorted(blocked))}  (also in {ALLOWLIST_FILE.relative_to(ROOT)})")
    return 0


def cmd_check(args) -> int:
    cfg = load_config(required=not args.page)
    c = company_cfg(cfg, args.slug, args.page)
    return _check(company_target(args.slug), c, args, require_pattern=bool(c.get("strict")))


def fetch_new(t: Target, c: dict, key: str, extra_urls: list[str] | None = None,
              discover: bool = True, mode: str = "default", max_credits: int = 0,
              require_pattern: bool = False, max_years: int = 0, two_hop: bool = False) -> int:
    """Download new reports for one target (domain-guarded). Returns count fetched.

    Free-first: direct download is always tried first. When it's blocked, Firecrawl
    PDF-parsing (PAID, ~1 credit/page) runs per `mode`:
      'no-firecrawl'  — never; defer everything blocked (guaranteed zero credits)
      'default'       — auto-Firecrawl small blocked docs; defer large reports
      'firecrawl-all' — Firecrawl any blocked doc, including large reports
    `max_credits` (>0) stops further Firecrawl use once estimated spend exceeds it.
    `require_pattern`/`max_years` are passed through to `select_candidates`."""
    ledger = load_ledger(t)
    seen = set(ledger.get("downloaded", {}))
    domains = allowed_domains(c)
    blocked_hosts: set[str] = set()

    urls = list(extra_urls or [])
    if discover:
        # regulators: match only the registry's specific patterns (see _check)
        patterns = c.get("patterns", []) if require_pattern else DEFAULT_PATTERNS + c.get("patterns", [])
        links, doc_hosts, disc_blocked = discover_all(
            c["urls"], key, patterns, domains, firecrawl_ok=(mode != "no-firecrawl"),
            two_hop=two_hop, max_years=max_years, search=c.get("search"))
        domains = domains | doc_hosts        # trust IR-CDN hosts the official page links docs to
        blocked_hosts |= disc_blocked
        urls += select_candidates(links, patterns, domains,
                                  require_pattern=require_pattern, max_years=max_years)

    urls = [u for u in dict.fromkeys(urls) if u not in seen]  # dedupe, skip already-have
    offdomain = [u for u in urls if registrable_domain(u) not in domains]
    for u in offdomain:
        print(f"⚠ skipped (not an official domain {sorted(domains)}): {u}")
    urls = [u for u in urls if u not in offdomain]

    if not urls and not blocked_hosts:
        print(f"[{t.label}] nothing new.")
        return 0

    done = 0
    spent = 0
    deferred: list[dict] = []
    for url in urls:
        print(f"[{t.label}] ↓ {url}")
        # decide whether Firecrawl may be used for THIS doc
        fc_ok = mode != "no-firecrawl"
        if mode == "default" and is_large_report(url):
            fc_ok = False                    # never auto-parse a few-hundred-page report
        if max_credits and spent >= max_credits:
            fc_ok = False                    # per-run credit cap reached

        rec = download_one(url, t, key, firecrawl_ok=fc_ok)
        if rec.get("status") == "deferred":
            deferred.append(rec)             # not downloaded, not ledgered → retried next run
            blocked_hosts.add(rec["host"])
            why = "large report — allowlist for free download" if is_large_report(url) and mode == "default" \
                  else rec.get("reason", "direct download blocked")
            print(f"          deferred ({rec['host']}: {why})")
            continue
        rec["downloaded_at"] = _dt.datetime.now().isoformat()
        ledger.setdefault("downloaded", {})[url] = rec
        save_ledger(t, ledger)               # persist after each — resumable on failure
        done += 1
        spent += int(rec.get("est_credits") or 0)
        extra = f"  ≈{rec['est_credits']} credits" if rec.get("est_credits") else ""
        print(f"          saved {rec['file']}  ({rec['method']}){extra}")

    if done:
        tot = f"  (~{spent} Firecrawl credits)" if spent else "  (free — no Firecrawl)"
        print(f"[{t.label}] ledger updated ({done} new){tot} -> {t.ledger_file.relative_to(ROOT)}")
    if deferred:
        print(f"[{t.label}] {len(deferred)} report(s) NOT collected — direct download blocked.")
    if blocked_hosts:
        added = record_allowlist(blocked_hosts)
        print(f"[{t.label}] Allowlist to go Firecrawl-free next run: {', '.join(sorted(blocked_hosts))}")
        print(f"          → paste-ready list in {ALLOWLIST_FILE.relative_to(ROOT)}"
              + (f" ({len(added)} new)" if added else ""))
        if mode == "default":
            print(f"          Or re-run with --firecrawl-all (PAID) to parse large reports via Firecrawl.")
    return done


def _mode(args) -> str:
    if getattr(args, "no_firecrawl", False):
        return "no-firecrawl"
    if getattr(args, "firecrawl_all", False):
        return "firecrawl-all"
    return "default"


def cmd_download(args) -> int:
    cfg = load_config(required=not args.page)
    c = company_cfg(cfg, args.slug, args.page)
    key = load_api_key()
    if not args.url and not args.all:
        sys.exit("download needs --url <URL> (repeatable) or --all")
    fetch_new(company_target(args.slug), c, key, extra_urls=args.url, discover=bool(args.all),
              mode=_mode(args), max_credits=args.max_credits, max_years=args.max_years,
              require_pattern=bool(c.get("strict")))
    return 0


def cmd_watch(args) -> int:
    """One-shot collect: discover + download everything new. Used by the skill and schedulable."""
    cfg = load_config(required=not args.page)
    key = load_api_key()
    if args.page and not args.slug:
        sys.exit("watch --page requires a <slug> (the company folder to collect into).")
    slugs = [args.slug] if args.slug else sorted(cfg.get("companies", {}))
    if not slugs:
        sys.exit("No companies to watch — pass a <slug> with --page, or populate the config.")
    total = 0
    for slug in slugs:
        c = company_cfg(cfg, slug, args.page)
        try:
            total += fetch_new(company_target(slug), c, key, discover=True,
                               mode=_mode(args), max_credits=args.max_credits, max_years=args.max_years,
                               require_pattern=bool(c.get("strict")))
        except SystemExit as e:           # one bad site shouldn't abort the whole sweep
            print(f"[{slug}] error: {e}")
    print(f"\nWatch complete: {total} new report(s) across {len(slugs)} company(ies).")
    return 0


def cmd_regulator(args) -> int:
    """Collect national-regulator market/statistical reports into the shared
    company-research/_regulators/<code>/ cache. Config comes from regulators.json."""
    regs = load_regulators().get("regulators", {})
    if not regs:
        sys.exit(f"No regulators registry at {ROOT/'regulators.json'} — see README.")
    if args.code and args.code not in regs:
        sys.exit(f"Unknown regulator '{args.code}'. Known: {', '.join(sorted(regs))}")
    codes = [args.code] if args.code else sorted(regs)
    key = load_api_key()
    total = 0
    for code in codes:
        c = regulator_cfg(regs, code)
        t = regulator_target(code)
        try:
            if args.check:
                _check(t, c, args, require_pattern=True, two_hop=True)
            else:
                total += fetch_new(t, c, key, discover=True, mode=_mode(args),
                                   max_credits=args.max_credits, require_pattern=True,
                                   max_years=args.max_years, two_hop=True)
        except SystemExit as e:           # one bad regulator site shouldn't abort a sweep
            print(f"[regulator:{code}] error: {e}")
    if not args.check:
        print(f"\nRegulator collection complete: {total} new report(s) across {len(codes)} regulator(s).")
    return 0


def cmd_list(args) -> int:
    t = regulator_target(args.slug[len("reg:"):]) if args.slug.startswith("reg:") else company_target(args.slug)
    ledger = load_ledger(t)
    dl = ledger.get("downloaded", {})
    print(f"# {t.label}: {len(dl)} report(s) on record")
    for url, rec in sorted(dl.items(), key=lambda kv: kv[1].get("downloaded_at", "")):
        print(f"  {rec.get('downloaded_at','?')[:10]}  {rec.get('file','?')}  <- {url}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Detect & download newly published company reports.")
    sub = p.add_subparsers(dest="cmd", required=True)

    page_help = "ad-hoc IR reports page URL (repeatable) — no config entry needed; download domain is derived from it"

    def add_fc_flags(sp):
        g = sp.add_mutually_exclusive_group()
        g.add_argument("--no-firecrawl", action="store_true",
                       help="fully free: direct download only, defer everything blocked (0 credits)")
        g.add_argument("--firecrawl-all", action="store_true",
                       help="PAID: allow Firecrawl even for large reports/20-Fs (~1 credit/PDF page)")
        sp.add_argument("--max-credits", type=int, default=0,
                        help="per-run soft cap: stop using Firecrawl past this estimated spend")

    years_help = "history bound: keep only reports from the last N fiscal years (0 = no bound)"

    pc = sub.add_parser("check", help="discover new report candidates (read-only)")
    pc.add_argument("slug")
    pc.add_argument("--page", action="append", help=page_help)
    pc.add_argument("--no-firecrawl", action="store_true",
                    help="discovery via direct fetch only (no Firecrawl map/scrape)")
    pc.add_argument("--max-years", type=int, default=0, help=years_help)
    pc.add_argument("--json", action="store_true")
    pc.set_defaults(func=cmd_check)

    pd = sub.add_parser("download", help="download chosen / all-new reports")
    pd.add_argument("slug")
    pd.add_argument("--page", action="append", help=page_help)
    pd.add_argument("--url", action="append", help="specific report URL (repeatable)")
    pd.add_argument("--all", action="store_true", help="download every new candidate")
    pd.add_argument("--max-years", type=int, default=0, help=years_help)
    add_fc_flags(pd)
    pd.set_defaults(func=cmd_download)

    pw = sub.add_parser("watch", help="one-shot: discover + download everything new")
    pw.add_argument("slug", nargs="?", help="company slug; omit to sweep every company in config")
    pw.add_argument("--page", action="append", help=page_help)
    pw.add_argument("--max-years", type=int, default=0, help=years_help)
    add_fc_flags(pw)
    pw.set_defaults(func=cmd_watch)

    pr = sub.add_parser("regulator", help="collect national-regulator reports into the shared _regulators/ cache")
    pr.add_argument("code", nargs="?", help="regulator code from regulators.json; omit to sweep all")
    pr.add_argument("--check", action="store_true", help="read-only: list candidates, download nothing")
    pr.add_argument("--max-years", type=int, default=0, help=years_help)
    pr.add_argument("--json", action="store_true")
    add_fc_flags(pr)
    pr.set_defaults(func=cmd_regulator)

    pl = sub.add_parser("list", help="show the download ledger (prefix a regulator code with reg:)")
    pl.add_argument("slug")
    pl.set_defaults(func=cmd_list)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
