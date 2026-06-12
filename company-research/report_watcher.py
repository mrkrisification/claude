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
from pathlib import Path

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


def load_config() -> dict:
    cfg = ROOT / "report_watcher.config.json"
    if not cfg.is_file():
        sys.exit(
            f"No config at {cfg}. Copy report_watcher.config.example.json and edit it."
        )
    return json.loads(cfg.read_text())


def company_cfg(cfg: dict, slug: str) -> dict:
    companies = cfg.get("companies", {})
    if slug not in companies:
        sys.exit(f"Unknown company '{slug}'. Known: {', '.join(sorted(companies)) or '(none)'}")
    c = dict(companies[slug])
    urls = c.get("urls") or ([c["url"]] if c.get("url") else [])
    if not urls:
        sys.exit(f"Company '{slug}' has no 'url'/'urls' in config.")
    c["urls"] = urls
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
        raise SystemExit(f"[2] Firecrawl HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise SystemExit(f"[2] Firecrawl network error: {e.reason}")


def discover_links(urls: list[str], key: str) -> list[str]:
    """Enumerate candidate links from each reports page via map + scrape."""
    found: set[str] = set()
    for url in urls:
        # map: enumerate the URL graph, biased toward report-y paths
        m = _firecrawl("map", {"url": url, "search": "report results quarterly annual", "limit": 300}, key)
        for link in m.get("links", []):
            href = link.get("url") if isinstance(link, dict) else link
            if href:
                found.add(href)
        # scrape: pull anchor links off the page itself (catches direct PDF hrefs)
        s = _firecrawl("scrape", {"url": url, "formats": ["links"]}, key)
        data = s.get("data", s)
        for href in data.get("links", []) or []:
            if href:
                found.add(href)
    # drop in-page fragments and the reports pages themselves
    bases = {u.rstrip("/") for u in urls}
    cleaned = {h.split("#", 1)[0].rstrip("/") for h in found if h}
    return sorted(h for h in cleaned if h and h not in bases)


# ---------------------------------------------------------------------------
# matching & ledger
# ---------------------------------------------------------------------------
def is_report(url: str, patterns: list[str]) -> bool:
    u = url.split("#", 1)[0].lower()          # ignore in-page fragments
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


def direct_download(url: str, dest: Path) -> bool:
    """Try a plain fetch with browsery headers. Returns True if a real doc landed."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Accept": "application/pdf,*/*",
    })
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


def firecrawl_capture(url: str, dest: Path, key: str) -> Path:
    """Fallback: have Firecrawl fetch+parse, save parsed markdown as a .md sidecar."""
    s = _firecrawl("scrape", {"url": url, "formats": ["markdown"], "parsers": ["pdf"]}, key)
    data = s.get("data", s)
    md = data.get("markdown", "") or ""
    md_dest = dest.with_suffix(".md")
    header = f"<!-- source: {url}\n     captured: {_dt.datetime.now().isoformat()}\n     via: firecrawl (raw bytes unavailable) -->\n\n"
    md_dest.write_text(header + md)
    return md_dest


def download_one(url: str, slug: str, key: str) -> dict:
    dest_dir = ROOT / slug / "raw"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / safe_name(url)
    if direct_download(url, dest):
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()[:16]
        return {"url": url, "file": str(dest.relative_to(ROOT)), "method": "direct", "sha256_16": digest}
    saved = firecrawl_capture(url, dest, key)
    return {"url": url, "file": str(saved.relative_to(ROOT)), "method": "firecrawl-parsed"}


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def cmd_check(args) -> int:
    cfg = load_config()
    c = company_cfg(cfg, args.slug)
    key = load_api_key()
    patterns = DEFAULT_PATTERNS + c.get("patterns", [])
    ledger = load_ledger(args.slug)
    seen = set(ledger.get("downloaded", {}))

    links = discover_links(c["urls"], key)
    candidates = [u for u in links if is_report(u, patterns)]
    new = [u for u in candidates if u not in seen]

    if args.json:
        print(json.dumps({"company": args.slug, "new": new, "all_candidates": candidates}, indent=2))
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
    return 0


def cmd_download(args) -> int:
    cfg = load_config()
    c = company_cfg(cfg, args.slug)
    key = load_api_key()
    ledger = load_ledger(args.slug)
    seen = set(ledger.get("downloaded", {}))

    urls = list(args.url or [])
    if args.all:
        patterns = DEFAULT_PATTERNS + c.get("patterns", [])
        links = discover_links(c["urls"], key)
        urls += [u for u in links if is_report(u, patterns) and u not in seen]
    urls = [u for u in dict.fromkeys(urls) if u not in seen]  # dedupe, skip already-have

    if not urls:
        print("Nothing new to download.")
        return 0

    for url in urls:
        print(f"↓ {url}")
        rec = download_one(url, args.slug, key)
        rec["downloaded_at"] = _dt.datetime.now().isoformat()
        ledger.setdefault("downloaded", {})[url] = rec
        print(f"  saved {rec['file']}  ({rec['method']})")
    save_ledger(args.slug, ledger)
    print(f"\nLedger updated: {ledger_path(args.slug).relative_to(ROOT)}")
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

    pc = sub.add_parser("check", help="discover new report candidates (read-only)")
    pc.add_argument("slug")
    pc.add_argument("--json", action="store_true")
    pc.set_defaults(func=cmd_check)

    pd = sub.add_parser("download", help="download chosen / all-new reports")
    pd.add_argument("slug")
    pd.add_argument("--url", action="append", help="specific report URL (repeatable)")
    pd.add_argument("--all", action="store_true", help="download every new candidate")
    pd.set_defaults(func=cmd_download)

    pl = sub.add_parser("list", help="show the download ledger")
    pl.add_argument("slug")
    pl.set_defaults(func=cmd_list)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
