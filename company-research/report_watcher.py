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


def discover_links(urls: list[str], key: str,
                   firecrawl_ok: bool = True) -> tuple[list[str], set[str], set[str]]:
    """Enumerate candidate links from each reports page.

    Tries free direct-HTML discovery first; only pages whose host is blocked fall
    back to Firecrawl `map`+`scrape` (when firecrawl_ok). `doc_hosts` are registrable
    domains the IR pages link document files to (e.g. q4cdn.com) — trusted as official.
    `blocked_hosts` are hosts that could not be fetched directly (allowlist candidates).
    """
    found, doc_hosts, blocked_hosts, productive = direct_discover(urls)
    # Fall back to Firecrawl for any IR page that direct discovery couldn't mine:
    # hosts we couldn't fetch at all, *and* pages we fetched but that yielded no
    # document links (Q4-style single-page apps inject the PDFs via JavaScript).
    fc_urls = [u for u in urls if u not in productive]
    if fc_urls and firecrawl_ok:
        for url in fc_urls:
            try:
                m = _firecrawl("map", {"url": url, "search": "report results quarterly annual", "limit": 300}, key)
                for link in m.get("links", []):
                    href = link.get("url") if isinstance(link, dict) else link
                    if href:
                        found.add(href)
                # waitFor lets client-rendered SPAs inject their document links
                # before we read them (the static DOM has none).
                s = _firecrawl("scrape", {"url": url, "formats": ["links"], "waitFor": 8000}, key)
                data = s.get("data", s)
                for href in data.get("links", []) or []:
                    if href:
                        found.add(href)
                        if href.split("#", 1)[0].split("?", 1)[0].lower().endswith(FILE_EXTS):
                            doc_hosts.add(registrable_domain(href))
                blocked_hosts.discard(registrable_domain(url))   # Firecrawl rescued it
            except SystemExit as e:
                print(f"  (Firecrawl discovery unavailable for {url}: {e})")
    # drop in-page fragments and the reports pages themselves
    bases = {u.rstrip("/") for u in urls}
    cleaned = {h.split("#", 1)[0].rstrip("/") for h in found if h}
    return sorted(h for h in cleaned if h and h not in bases), doc_hosts, blocked_hosts


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


def select_candidates(links: list[str], patterns: list[str], domains: set[str]) -> list[str]:
    """Report-like links that live on an official IR domain."""
    return [u for u in links if is_report(u, patterns) and registrable_domain(u) in domains]


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


def ledger_path(slug: str) -> Path:
    return ROOT / slug / "reports" / "ledger.json"


def load_ledger(slug: str) -> dict:
    p = ledger_path(slug)
    if p.is_file():
        return json.loads(p.read_text())
    return {"company": slug, "downloaded": {}}


def save_ledger(slug: str, ledger: dict) -> None:
    p = ledger_path(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")


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


def download_one(url: str, slug: str, key: str, firecrawl_ok: bool) -> dict:
    """Fetch one report. Direct download (free) is always tried first. Firecrawl
    PDF-parsing (PAID, ~1 credit/page) runs only when firecrawl_ok; otherwise the URL
    is deferred and nothing is spent. A Firecrawl 402 degrades to deferred, not a crash."""
    dest_dir = ROOT / slug / "raw"
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
def cmd_check(args) -> int:
    cfg = load_config(required=not args.page)
    c = company_cfg(cfg, args.slug, args.page)
    key = load_api_key()
    patterns = DEFAULT_PATTERNS + c.get("patterns", [])
    ledger = load_ledger(args.slug)
    seen = set(ledger.get("downloaded", {}))

    links, doc_hosts, blocked = discover_links(c["urls"], key, firecrawl_ok=not args.no_firecrawl)
    domains = allowed_domains(c) | doc_hosts
    candidates = select_candidates(links, patterns, domains)
    new = [u for u in candidates if u not in seen]

    if args.json:
        print(json.dumps({"company": args.slug, "new": new, "all_candidates": candidates,
                          "blocked_hosts": sorted(blocked)}, indent=2))
    else:
        print(f"# {args.slug}: {len(new)} new of {len(candidates)} report candidate(s)\n")
        for u in new:
            print(f"  NEW   {u}")
        for u in candidates:
            if u in seen:
                print(f"  seen  {u}")
        if not candidates:
            print("  (no report-like links found — check the URL / add 'patterns' in config)")
        if new:
            print(f"\nDownload: python3 report_watcher.py download {args.slug} --all")
    if blocked:
        record_allowlist(blocked)
        print(f"\nAllowlist to go Firecrawl-free: {', '.join(sorted(blocked))}  (also in {ALLOWLIST_FILE.relative_to(ROOT)})")
    return 0


def fetch_new(slug: str, c: dict, key: str, extra_urls: list[str] | None = None,
              discover: bool = True, mode: str = "default", max_credits: int = 0) -> int:
    """Download new reports for one company (domain-guarded). Returns count fetched.

    Free-first: direct download is always tried first. When it's blocked, Firecrawl
    PDF-parsing (PAID, ~1 credit/page) runs per `mode`:
      'no-firecrawl'  — never; defer everything blocked (guaranteed zero credits)
      'default'       — auto-Firecrawl small blocked docs; defer large reports
      'firecrawl-all' — Firecrawl any blocked doc, including large reports
    `max_credits` (>0) stops further Firecrawl use once estimated spend exceeds it."""
    ledger = load_ledger(slug)
    seen = set(ledger.get("downloaded", {}))
    domains = allowed_domains(c)
    blocked_hosts: set[str] = set()

    urls = list(extra_urls or [])
    if discover:
        patterns = DEFAULT_PATTERNS + c.get("patterns", [])
        links, doc_hosts, disc_blocked = discover_links(
            c["urls"], key, firecrawl_ok=(mode != "no-firecrawl"))
        domains = domains | doc_hosts        # trust IR-CDN hosts the official page links docs to
        blocked_hosts |= disc_blocked
        urls += select_candidates(links, patterns, domains)

    urls = [u for u in dict.fromkeys(urls) if u not in seen]  # dedupe, skip already-have
    offdomain = [u for u in urls if registrable_domain(u) not in domains]
    for u in offdomain:
        print(f"⚠ skipped (not an official IR domain {sorted(domains)}): {u}")
    urls = [u for u in urls if u not in offdomain]

    if not urls and not blocked_hosts:
        print(f"[{slug}] nothing new.")
        return 0

    done = 0
    spent = 0
    deferred: list[dict] = []
    for url in urls:
        print(f"[{slug}] ↓ {url}")
        # decide whether Firecrawl may be used for THIS doc
        fc_ok = mode != "no-firecrawl"
        if mode == "default" and is_large_report(url):
            fc_ok = False                    # never auto-parse a few-hundred-page report
        if max_credits and spent >= max_credits:
            fc_ok = False                    # per-run credit cap reached

        rec = download_one(url, slug, key, firecrawl_ok=fc_ok)
        if rec.get("status") == "deferred":
            deferred.append(rec)             # not downloaded, not ledgered → retried next run
            blocked_hosts.add(rec["host"])
            why = "large report — allowlist for free download" if is_large_report(url) and mode == "default" \
                  else rec.get("reason", "direct download blocked")
            print(f"          deferred ({rec['host']}: {why})")
            continue
        rec["downloaded_at"] = _dt.datetime.now().isoformat()
        ledger.setdefault("downloaded", {})[url] = rec
        save_ledger(slug, ledger)            # persist after each — resumable on failure
        done += 1
        spent += int(rec.get("est_credits") or 0)
        extra = f"  ≈{rec['est_credits']} credits" if rec.get("est_credits") else ""
        print(f"          saved {rec['file']}  ({rec['method']}){extra}")

    if done:
        tot = f"  (~{spent} Firecrawl credits)" if spent else "  (free — no Firecrawl)"
        print(f"[{slug}] ledger updated ({done} new){tot} -> {ledger_path(slug).relative_to(ROOT)}")
    if deferred:
        print(f"[{slug}] {len(deferred)} report(s) NOT collected — direct download blocked.")
    if blocked_hosts:
        added = record_allowlist(blocked_hosts)
        print(f"[{slug}] Allowlist to go Firecrawl-free next run: {', '.join(sorted(blocked_hosts))}")
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
    fetch_new(args.slug, c, key, extra_urls=args.url, discover=bool(args.all),
              mode=_mode(args), max_credits=args.max_credits)
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
            total += fetch_new(slug, c, key, discover=True,
                               mode=_mode(args), max_credits=args.max_credits)
        except SystemExit as e:           # one bad site shouldn't abort the whole sweep
            print(f"[{slug}] error: {e}")
    print(f"\nWatch complete: {total} new report(s) across {len(slugs)} company(ies).")
    return 0


def cmd_list(args) -> int:
    ledger = load_ledger(args.slug)
    dl = ledger.get("downloaded", {})
    print(f"# {args.slug}: {len(dl)} report(s) on record")
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

    pc = sub.add_parser("check", help="discover new report candidates (read-only)")
    pc.add_argument("slug")
    pc.add_argument("--page", action="append", help=page_help)
    pc.add_argument("--no-firecrawl", action="store_true",
                    help="discovery via direct fetch only (no Firecrawl map/scrape)")
    pc.add_argument("--json", action="store_true")
    pc.set_defaults(func=cmd_check)

    pd = sub.add_parser("download", help="download chosen / all-new reports")
    pd.add_argument("slug")
    pd.add_argument("--page", action="append", help=page_help)
    pd.add_argument("--url", action="append", help="specific report URL (repeatable)")
    pd.add_argument("--all", action="store_true", help="download every new candidate")
    add_fc_flags(pd)
    pd.set_defaults(func=cmd_download)

    pw = sub.add_parser("watch", help="one-shot: discover + download everything new")
    pw.add_argument("slug", nargs="?", help="company slug; omit to sweep every company in config")
    pw.add_argument("--page", action="append", help=page_help)
    add_fc_flags(pw)
    pw.set_defaults(func=cmd_watch)

    pl = sub.add_parser("list", help="show the download ledger")
    pl.add_argument("slug")
    pl.set_defaults(func=cmd_list)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
