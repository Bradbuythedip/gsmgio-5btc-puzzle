GSMG ESPLORA OFFLINE SOLVER
===========================

This wrapper separates PUBLIC CHAIN ACQUISITION from OFFLINE ANALYSIS.

It imports the current repository implementation of:

  neo/harness/receipt_lookups.py

So reviewer fixes are picked up automatically after `git pull`.

1. SELFTEST — NO NETWORK

  python3 /path/to/gsmg_esplora_offline.py selftest --repo .

2. ACQUIRE ONCE WITH ESPLORA

  python3 /path/to/gsmg_esplora_offline.py sync \
    --repo . \
    --base https://mempool.space/api \
    --depth 12 \
    --max-fetch 200 \
    --max-pages 20

Alternative:

  --base https://blockstream.info/api

3. TRUE OFFLINE RERUN

Disconnect networking if desired, then use the SAME API base and bounds:

  python3 /path/to/gsmg_esplora_offline.py offline \
    --repo . \
    --base https://mempool.space/api \
    --depth 12 \
    --max-fetch 200 \
    --max-pages 20

If any required endpoint was not cached, offline mode exits 4, lists the missing
endpoints and leaves the existing reports untouched. It never fetches. A sync hit by a
transient failure exits 5 (invariant cache_complete=false); rerun sync to fill the gap.
HTTP 404/400 answers are pinned and replayed verbatim, so offline replays every response
sync saw. The report text can differ only in its timestamp and in a signature tag where
offline, holding the whole cache from the start, finds a parent that sync fetched in a later
section ("unchecked: parent not fetched" becomes "verified"); verdicts do not depend on it.
Every report carries an "invariant" block: mode, cache_complete,
network_requests, cache_misses, transient_failures, unavailable_items, prereg_sha256,
receipt_lookups_sha256.

4. CACHE STATUS

  python3 /path/to/gsmg_esplora_offline.py status --repo .

CACHE LOCATIONS

Repo's existing receipt tool:
  neo/materials/chain/fetched/*.hex
  neo/materials/chain/fetched/json/*

This wrapper also stores every exact Esplora GET response:
  neo/materials/chain/fetched/esplora_http/<sha256(path)>.bin
  neo/materials/chain/fetched/esplora_http/index.json
  neo/materials/chain/fetched/esplora_run_manifest.json

The HTTP cache is frozen at first acquisition: a later sync serves cached endpoints
without refetching them (delete esplora_http/ to re-acquire). The index pins each
response's sha256, and `status` reports any file that no longer matches.

OUTPUTS

  neo/materials/chain/RECEIPT_LOOKUPS.md
  neo/materials/chain/receipt_lookups.json

SCOPE

GET-only chain evidence acquisition and offline verification. No signing,
broadcasting, AES candidate generation, BSGS, key-range search, or private-key
recovery.

The wrapper deliberately does not copy or fork the receipt logic. The reviewed version
(tick 93: 38 review findings fixed, the pre-registered H1 verdict and promotion condition
(iv) added) issues no request that the tick-92 version did not under the live run's
conditions, so a cache synced with the earlier code replays offline with the reviewed code:
pull, run selftest, then offline. No second sync is needed.
