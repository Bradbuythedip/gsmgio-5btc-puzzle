#!/usr/bin/env python3
"""
GSMG Esplora Cache + Offline Receipt Solver
===========================================

Uses an Esplora API only to acquire public Bitcoin data once, caches every HTTP
GET response byte-for-byte, then reruns the repo's receipt/fan-out analysis
completely offline.

The actual puzzle logic remains in the repository's current:
    neo/harness/receipt_lookups.py

Commands:
    selftest   repo offline controls; no network
    sync       Esplora acquisition + analysis + exact response cache
    offline    same analysis from cache only; network forbidden
    status     verify/summarize caches

Examples:
    python3 gsmg_esplora_offline.py selftest --repo .
    python3 gsmg_esplora_offline.py sync --repo . --base https://mempool.space/api
    python3 gsmg_esplora_offline.py offline --repo . --base https://mempool.space/api
    python3 gsmg_esplora_offline.py status --repo .

GET-only. No transaction signing/broadcasting, key search, BSGS, nonce attack,
or AES candidate generation.

Exit codes: 0 ok; 2 bad input; 3 cache integrity failure (status) or selftest failure;
4 offline run incomplete (a required endpoint was not cached; reports are not written).
The HTTP cache is frozen at first acquisition: a later sync serves cached endpoints without
refetching them. Delete neo/materials/chain/fetched/esplora_http/ to re-acquire.
"""
from __future__ import annotations

import argparse, hashlib, importlib, json, os, sys, time
from pathlib import Path
from typing import Dict, Optional

VERSION = "2026-09-26.2"
# .2 (repo, tick 93): offline mode now hard-fails on any cache miss and leaves existing reports untouched
#    (receipt_lookups records Unavailable as an "unavailable" line, so .1 exited 0 with a degraded report);
#    a re-sync serves cached endpoints without refetching, so the first acquisition is frozen.
DEFAULT_BASE = "https://mempool.space/api"
DEFAULT_DEPTH = 12
DEFAULT_MAX_FETCH = 200
DEFAULT_MAX_PAGES = 20

def sha256hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def locate_repo(p: Path) -> Path:
    p = p.expanduser().resolve()
    need = p / "neo" / "harness" / "receipt_lookups.py"
    if not need.is_file():
        raise FileNotFoundError(f"{p} is not a GSMG checkout: missing {need}")
    return p

def load_repo_modules(repo: Path):
    harness = repo / "neo" / "harness"
    sys.path.insert(0, str(harness))
    return importlib.import_module("receipt_lookups")

def endpoint_cache_root(repo: Path) -> Path:
    return repo / "neo" / "materials" / "chain" / "fetched" / "esplora_http"

def raw_cache_root(repo: Path) -> Path:
    return repo / "neo" / "materials" / "chain" / "fetched"

class EndpointCache:
    def __init__(self, root: Path):
        self.root = root
        self.index_path = root / "index.json"
        self.index: Dict[str, dict] = {}
        if self.index_path.is_file():
            doc = json.loads(self.index_path.read_text(encoding="utf-8"))
            self.index = dict(doc.get("entries", {}))

    @staticmethod
    def key(path: str) -> str:
        return hashlib.sha256(path.encode("utf-8")).hexdigest()

    def data_path(self, path: str) -> Path:
        return self.root / (self.key(path) + ".bin")

    def get(self, path: str) -> Optional[bytes]:
        p = self.data_path(path)
        if not p.is_file():
            return None
        b = p.read_bytes()
        rec = self.index.get(self.key(path))
        if rec:
            want = rec.get("sha256")
            if want and sha256hex(b) != want:
                raise RuntimeError(f"cache integrity failure for {path}")
            if rec.get("path") not in (None, path):
                raise RuntimeError(f"cache index collision/mismatch for {path}")
        return b

    def put(self, path: str, data: bytes, base: str):
        self.root.mkdir(parents=True, exist_ok=True)
        key = self.key(path)
        p = self.root / (key + ".bin")
        if p.exists():
            old = p.read_bytes()
            if old != data:
                raise RuntimeError(
                    f"Esplora endpoint changed for {path}; "
                    f"cached={sha256hex(old)}, new={sha256hex(data)}"
                )
        else:
            p.write_bytes(data)
        self.index[key] = {
            "path": path,
            "base": base.rstrip("/"),
            "bytes": len(data),
            "sha256": sha256hex(data),
            "cached_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.flush()

    def flush(self):
        self.root.mkdir(parents=True, exist_ok=True)
        doc = {
            "format": 1,
            "description": "Exact GET response cache for gsmg_esplora_offline.py",
            "entries": self.index,
        }
        tmp = self.index_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, self.index_path)

    def verify_all(self):
        bad, total, nbytes = [], 0, 0
        for key, rec in self.index.items():
            p = self.root / (key + ".bin")
            if not p.is_file():
                bad.append((rec.get("path"), "missing file"))
                continue
            b = p.read_bytes()
            total += 1
            nbytes += len(b)
            got = sha256hex(b)
            if got != rec.get("sha256"):
                bad.append((rec.get("path"), f"sha256 {got} != {rec.get('sha256')}"))
        return total, nbytes, bad

def make_esplora(RL, repo: Path, base: str, offline: bool, delay: float):
    cache = EndpointCache(endpoint_cache_root(repo))

    class CachedEsplora(RL.Esplora):
        def __init__(self):
            super().__init__(base, save=True, delay=delay)
            self.endpoint_cache = cache
            self.offline_only = offline
            self.cache_hits = 0
            self.cache_misses = 0
            self.missing_paths = []

        def _get(self, path):
            hit = self.endpoint_cache.get(path)
            if hit is not None:
                self.cache_hits += 1
                return hit
            self.cache_misses += 1
            self.missing_paths.append(path)
            if self.offline_only:
                raise RL.Unavailable(
                    f"offline cache miss: {path}. "
                    f"Run sync once with the same bounds."
                )
            data = super()._get(path)
            self.endpoint_cache.put(path, data, self.base)
            return data

    return CachedEsplora()

def prereg_info(repo: Path):
    p = repo / "neo" / "intake" / "2026-09-26-fanout" / "PREREG.md"
    if not p.is_file():
        return {"present": False, "path": str(p)}
    b = p.read_bytes()
    return {"present": True, "path": str(p), "bytes": len(b), "sha256": sha256hex(b)}

def write_run_manifest(repo: Path, mode: str, api, depth: int, max_fetch: int, max_pages: int):
    out = repo / "neo" / "materials" / "chain" / "fetched" / "esplora_run_manifest.json"
    cache = EndpointCache(endpoint_cache_root(repo))
    n, nb, bad = cache.verify_all()
    doc = {
        "wrapper_version": VERSION,
        "mode": mode,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base": api.base,
        "bounds": {"depth": depth, "max_fetch": max_fetch, "max_pages": max_pages},
        "http_cache": {
            "entries": n,
            "bytes": nb,
            "integrity_errors": bad,
            "hits_this_run": getattr(api, "cache_hits", None),
            "misses_this_run": getattr(api, "cache_misses", None),
            "network_requests_this_run": getattr(api, "fetches", None),
        },
        "prereg": prereg_info(repo),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out

def run_analysis(RL, repo: Path, mode: str, base: str, depth: int, max_fetch: int, max_pages: int, delay: float):
    api = make_esplora(RL, repo, base, offline=(mode == "offline"), delay=delay)
    verdicts, text, extra = RL.run(
        api, depth=depth, max_fetch=max_fetch, max_pages=max_pages, full=True
    )

    chain = repo / "neo" / "materials" / "chain"
    chain.mkdir(parents=True, exist_ok=True)
    if mode == "offline" and getattr(api, "cache_misses", 0):
        print(f"OFFLINE RUN INCOMPLETE: {api.cache_misses} endpoint(s) not in the cache; reports NOT written:",
              file=sys.stderr)
        for p in api.missing_paths[:50]:
            print("  missing:", p, file=sys.stderr)
        print("Run `sync` once with the same --base and bounds, then rerun `offline`.", file=sys.stderr)
        return 4
    unavailable = text.count("unavailable")
    if unavailable:
        print(f"WARNING: the report contains {unavailable} 'unavailable' item(s); see RECEIPT_LOOKUPS.md",
              file=sys.stderr)
    (chain / "RECEIPT_LOOKUPS.md").write_text(text + "\n", encoding="utf-8")
    report = {
        "verdicts": verdicts,
        **extra,
        "wrapper": {
            "version": VERSION,
            "mode": mode,
            "base": api.base,
            "http_cache_hits": getattr(api, "cache_hits", 0),
            "http_cache_misses": getattr(api, "cache_misses", 0),
            "network_requests": getattr(api, "fetches", 0),
        },
        "prereg": prereg_info(repo),
    }
    (chain / "receipt_lookups.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    manifest = write_run_manifest(repo, mode, api, depth, max_fetch, max_pages)

    print(text)
    print("\n== wrapper summary ==")
    print("mode:", mode)
    print("base:", api.base)
    print("HTTP cache hits:", getattr(api, "cache_hits", 0))
    print("HTTP cache misses:", getattr(api, "cache_misses", 0))
    print("network requests:", getattr(api, "fetches", 0))
    print("written:", chain / "RECEIPT_LOOKUPS.md")
    print("written:", chain / "receipt_lookups.json")
    print("manifest:", manifest)

    if mode == "offline" and getattr(api, "fetches", 0) != 0:
        raise RuntimeError("OFFLINE INVARIANT FAILED: a network request occurred")
    return 0

def cmd_status(repo: Path):
    ec = EndpointCache(endpoint_cache_root(repo))
    n, nb, bad = ec.verify_all()
    rawroot = raw_cache_root(repo)
    raw = []
    if rawroot.is_dir():
        for p in sorted(rawroot.glob("*.hex")):
            try:
                txt = "".join(
                    line.strip()
                    for line in p.read_text(encoding="utf-8", errors="strict").splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                )
                b = bytes.fromhex(txt)
                raw.append({"name": p.name, "bytes": len(b), "sha256": sha256hex(b)})
            except Exception as e:
                raw.append({"name": p.name, "error": str(e)})
    print(json.dumps({
        "wrapper_version": VERSION,
        "repo": str(repo),
        "prereg": prereg_info(repo),
        "endpoint_cache": {
            "root": str(ec.root), "entries": n, "bytes": nb, "integrity_errors": bad
        },
        "raw_tx_cache": {"root": str(rawroot), "files": raw},
    }, indent=2, sort_keys=True))
    return 0 if not bad else 3

def build_parser():
    ap = argparse.ArgumentParser(
        description="Esplora acquisition cache + offline GSMG receipt/fan-out solver"
    )
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name, helptext in [
        ("selftest", "run repo offline controls; no network"),
        ("sync", "fetch via Esplora, cache exact GET responses, run full analysis"),
        ("offline", "run full analysis from cache only; network forbidden"),
        ("status", "verify/summarize caches"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--repo", type=Path, default=Path("."))
        if name in ("sync", "offline"):
            p.add_argument("--base", default=DEFAULT_BASE)
            p.add_argument("--depth", type=int, default=DEFAULT_DEPTH)
            p.add_argument("--max-fetch", type=int, default=DEFAULT_MAX_FETCH)
            p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
            p.add_argument("--delay", type=float, default=0.15)
    return ap

def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        repo = locate_repo(a.repo)
        RL = load_repo_modules(repo)

        if a.cmd == "selftest":
            print("repo:", repo)
            print("receipt_lookups:", Path(RL.__file__).resolve())
            print("prereg:", json.dumps(prereg_info(repo), sort_keys=True))
            ok = bool(RL.selftest())
            print("wrapper selftest passed:", ok)
            return 0 if ok else 3

        if a.cmd == "status":
            return cmd_status(repo)

        if a.cmd in ("sync", "offline"):
            if a.depth < 1 or a.max_fetch < 1 or a.max_pages < 1:
                raise ValueError("--depth, --max-fetch and --max-pages must all be >= 1")
            if not (a.base.startswith("https://") or a.base.startswith("http://")):
                raise ValueError("--base must be an http(s) Esplora API base")
            return run_analysis(
                RL, repo, a.cmd, a.base, a.depth, a.max_fetch, a.max_pages, a.delay
            )

        raise RuntimeError("unreachable")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print("ERROR:", e, file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130

if __name__ == "__main__":
    raise SystemExit(main())
