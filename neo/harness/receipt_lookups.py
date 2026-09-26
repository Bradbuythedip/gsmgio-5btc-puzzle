#!/usr/bin/env python3
"""Topology-only chain lookups for the receipt model (ticks 88–92), in one command.

  1. The 2024 split (88cdb3cd…, locktime 840003) spent two inputs besides the 2020 change. Who
     signed their parent transactions, and does either carry an OP_RETURN? (Answered tick 92: NO.)
  2. Who funded 3GSMG24T: walk up from 547246e9… through every input, reporting each signer with
     its script type (multisig m-of-n and its public keys included) until the walk reaches a
     creator-trail signer or the depth / fetch bounds.
  3. The 2021 "neighbors, half and double" transaction (the only tx of the Q−G address): is it
     signed by 3GSMG24T's key?
  4. The complete 3GSMG24T fan-out, rebuilt from the address's full history: every inbound funding,
     every self-split and every emission, as a UTXO tree with amounts, heights, dates and memos;
     a census of every recipient against the ledger's known creator receipts (unknown recipients
     are flagged); fuel accounting; and offline signature verification wherever the spent
     output's parent is available (BIP143 needs its amount). Then the pre-registered H1 verdict
     (intake/2026-09-26-fanout/PREREG.md): the 15,000 sat that 37mh… paid in 1f8eb99e… was cut
     by self-splits into exactly 12 fuel outputs, consumed one-for-one by the 10 known 2020
     emissions (six checkpoints, 1NULY7, two "Good job, Neo!", "Halving" taking 3). PASS or FAIL
     with the difference; UNDETERMINED only while the history is incomplete or a tx is unread.
  5. The full history of each wallet that funded 3GSMG24T (e.g. the 2-of-2 multisig 37mh7EYet…):
     transaction count, first/last block and date, flows, and which transactions touch a
     GSMG-labelled address.
  6. The promotion rule for each such funder, fixed before the run:
       PROMOTE only if (i) it, or its ancestry within the walk bounds, is a creator-trail signer
       (1EtbTv…, the prize key, 1GSMG1CLx…, 17ucy1…); or (ii) one of its public keys, by
       x-coordinate, equals a key in authenticated GSMG material, or its hex appears in
       neo/materials (materials/chain, this tool's own fetched data, excluded); or (iii) its full
       history is narrowly GSMG-specific: at most 10 transactions, at least half of which pay or
       spend a GSMG-labelled address; or (iv) it signs two or more separate inbound fundings of
       3GSMG24T that 3GSMG24T then spends.
     Otherwise it is operational funding infrastructure and the branch closes; when a condition
     that could promote was not evaluated (fetch cap, unread data), the verdict is NOT DETERMINED,
     never close. Addresses, keys,
     amounts, txids and scripts are never used as AES candidates.

Read-only, no keys. Needs an Esplora API (mempool.space by default); this cloud environment's
network policy blocks it, so run it on an unblocked machine. Every fetched raw tx is checked
against its txid and cached in materials/chain/fetched/ (JSON responses in fetched/json/) so reruns
are free and the raws can be committed as primaries. Output: materials/chain/RECEIPT_LOOKUPS.md and
materials/chain/receipt_lookups.json.

  python3 receipt_lookups.py                                  # mempool.space, depth 12, 200 fetches
  python3 receipt_lookups.py --base https://blockstream.info/api
  python3 receipt_lookups.py --depth 16 --max-fetch 400 --max-pages 40
  python3 receipt_lookups.py --selftest                       # offline, saved hex only
"""
import argparse, http.client, json, os, re, sys, tempfile, time, urllib.error, urllib.request
import receipt_topology as RT
import txscript as T
import btc_addr
from chain_flows import parse_raw, script_info

CHAIN = os.path.join(RT.NEO, "materials", "chain")
FETCHED = os.path.join(CHAIN, "fetched")
JSONDIR = os.path.join(FETCHED, "json")
FUNDER = "1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1"
QMG = "1G1kRAFR68y6CUq1SAJMzHmjd6sEEgtVUT"          # Q−G; its only tx is the 2021 memo (tick 53)
SEEDKEY = "148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ"       # the Phase-0 seed as a raw key: public knowledge (tick 56)
TRAIL = {RT.HALF: "prize (half)", RT.BETTER: "better half", RT.CREATOR: "3GSMG24T", FUNDER: "2019 funder 1EtbTv",
         "1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3": "vanity 1GSMG1CLx"}
CREATOR_TRAIL = {a for a in TRAIL if a != RT.CREATOR}  # what counts as "reaches the creator trail"
COINBASE = "00" * 32
RULE_III = (10, 0.5)                                  # (max transactions, min GSMG-touching share)

class Unavailable(Exception):
    pass

def raw_matches(txid, hx):
    """True if hx decodes completely (no truncation, no trailing bytes) to a transaction with this txid."""
    try:
        return parse_raw(hx)["txid"] == txid
    except (ValueError, IndexError, KeyError):
        return False

def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)

class Esplora:
    """GET-only Esplora client with an on-disk cache. `fixture` (txid -> hex) replaces the network;
    `addr_fixture` (address -> [txid]) replaces address histories."""
    def __init__(self, base, fixture=None, save=True, addr_fixture=None, delay=0.15):
        self.base, self.fixture, self.save, self.fetches = base.rstrip("/"), fixture, save, 0
        self.addr_fixture, self.delay = addr_fixture, delay

    def _get(self, path):
        if self.fixture is not None:
            raise Unavailable(f"offline: {path}")
        last = None
        for attempt in range(5):
            try:
                time.sleep(self.delay)
                with urllib.request.urlopen(self.base + path, timeout=45) as r:
                    self.fetches += 1
                    return r.read()
            except urllib.error.HTTPError as e:
                last = e
                if e.code in (400, 404):
                    break
                time.sleep(2 ** attempt * (3 if e.code == 429 else 1))
            except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
                last = e; time.sleep(2 ** attempt)
        raise Unavailable(f"{self.base}{path}: {last}")

    def get_json(self, path, cache_name=None):
        if self.fixture is not None:                        # hermetic: never read the persistent JSON cache
            raise Unavailable(f"offline: {path}")
        cached = os.path.join(JSONDIR, cache_name) if cache_name else None
        if cached and os.path.exists(cached):
            try:
                return json.load(open(cached))
            except ValueError:
                pass                                        # a truncated file from an interrupted write: refetch
        data = self._json(path)
        if cached and self.save:
            atomic_write(cached, json.dumps(data))
        return data

    def _json(self, path):
        body = self._get(path)
        try:
            return json.loads(body)
        except ValueError as e:
            raise Unavailable(f"{self.base}{path}: response is not JSON ({e})")

    def cached_hex(self, txid):
        """Hex only if already on hand (fixture or disk cache) and it decodes to this txid; never fetches."""
        if self.fixture is not None:
            hx = self.fixture.get(txid)
        else:
            p = os.path.join(FETCHED, txid + ".hex")
            hx = open(p).read().strip() if os.path.exists(p) else None
        return hx if hx is not None and raw_matches(txid, hx) else None

    def tx_hex(self, txid):
        cached = os.path.join(FETCHED, txid + ".hex")
        if self.fixture is not None:                        # fixture mode is hermetic: no disk cache, no network
            if txid not in self.fixture:
                raise Unavailable(f"offline fixture has no tx {txid}")
            hx = self.fixture[txid]
            if not raw_matches(txid, hx):
                raise Unavailable(f"{txid}: returned hex does not hash to the txid")
            return hx
        if os.path.exists(cached):
            hx = open(cached).read().strip()
            if raw_matches(txid, hx):
                return hx                                   # a corrupt disk copy is ignored, not trusted
        hx = self._get(f"/tx/{txid}/hex").decode("ascii", "replace").strip()
        if not raw_matches(txid, hx):
            raise Unavailable(f"{txid}: returned hex does not hash to the txid")
        if self.save:
            atomic_write(cached, hx + "\n")
        return hx

    def tx_status(self, txid):
        """(height, unix time) or (None, None); explorer-reported."""
        if self.fixture is not None:
            return None, None
        try:
            st = self.get_json(f"/tx/{txid}/status", f"status_{txid}.json")
        except Unavailable:
            return None, None
        return st.get("block_height"), st.get("block_time")

    def address_txids(self, addr):
        if self.addr_fixture is not None and addr in self.addr_fixture:
            return self.addr_fixture[addr]
        return [t["txid"] for t in self._json(f"/address/{addr}/txs")]

    def address_stats(self, addr):
        if self.fixture is not None:
            return None
        return self.get_json(f"/address/{addr}")

    def address_history(self, addr, max_pages):
        """(entries, complete). Entries are Esplora tx objects (explorer-reported), newest first;
        in fixture mode they are {'txid': …} stubs from addr_fixture."""
        if self.addr_fixture is not None:
            if addr not in self.addr_fixture:
                raise Unavailable(f"offline: no history fixture for {addr}")
            return [{"txid": t} for t in self.addr_fixture[addr]], True
        if self.fixture is not None:
            raise Unavailable(f"offline: /address/{addr}/txs")
        first = self._json(f"/address/{addr}/txs")
        items = list(first)
        confirmed = [t for t in first if t.get("status", {}).get("confirmed")]
        complete, pages = len(confirmed) < 25, 1
        last = confirmed[-1]["txid"] if confirmed else None
        while not complete and pages < max_pages:
            nxt = self._json(f"/address/{addr}/txs/chain/{last}")
            pages += 1; items += nxt
            complete = len(nxt) < 25
            if nxt:
                last = nxt[-1]["txid"]
        if self.save:
            atomic_write(os.path.join(JSONDIR, f"history_{addr}.json"),
                         json.dumps({"address": addr, "complete": complete, "pages": pages, "txs": items}))
        return items, complete

# ---------- labels, keys, helpers ----------
_LABELS = None
def labels():
    """Every GSMG-labelled address: creator trail, answer keys, seed keys, Q-derived points, 1NULY7."""
    global _LABELS
    if _LABELS is None:
        split = saved("2aa9a4a9")
        pub = next(p for k, a, p in (RT.signer(v) for v in split["vin"]) if a == RT.HALF and p is not None)
        Q = (int.from_bytes(pub[1:33], "big"), int.from_bytes(pub[33:65], "big"))
        lab, _, _ = RT.build_labels(Q)
        lab.update(TRAIL)
        _LABELS = lab
    return _LABELS

def label(a):
    lab = labels()
    return f"{a} [{lab[a]}]" if a in lab else str(a)

def when(ts):
    return time.strftime("%Y-%m-%d", time.gmtime(ts)) if ts else "?"

def describe(hx, prevs=None):
    """(tx, signers, outs, memos, scripts). `prevs`: the spent scriptPubKey (bytes) of each input where
    known; it identifies p2tr and p2pk signers and routes native segwit inputs by their program."""
    tx = parse_raw(hx)
    prevs = prevs or [None] * len(tx["vin"])
    scripts = [T.input_script(v, p) for v, p in zip(tx["vin"], prevs)]
    signers = [(d["kind"], d["address"], d["pubkeys"][0] if len(d["pubkeys"]) == 1 else None) for d in scripts]
    outs = [(o["n"], o["sat"]) + script_info(bytes.fromhex(o["spk"])) for o in tx["vout"]]
    memos = [d.decode("latin1") for _, _, kind, _, d in outs if kind == "op_return"]
    return tx, signers, outs, memos, scripts

def prev_spks(api, tx, meta=None, local=None):
    """Spent scriptPubKey per input, from sources that do not depend on what happens to be on disk, so a
    fresh sync and its offline replay attribute signers identically: raws read earlier in the same walk
    (`local`, txid-verified), the Esplora tx object's prevout (`meta`, explorer-reported), or the offline
    fixture. None where none applies. Never fetches."""
    vins = (meta or {}).get("vin") or []
    out = []
    for k, v in enumerate(tx["vin"]):
        spk, phx = None, None
        if v["txid"] != COINBASE:
            phx = (local or {}).get(v["txid"]) or (api.fixture.get(v["txid"]) if api.fixture is not None else None)
        if phx and raw_matches(v["txid"], phx) and v["vout"] < len(parse_raw(phx)["vout"]):
            spk = bytes.fromhex(parse_raw(phx)["vout"][v["vout"]]["spk"])
        elif k < len(vins) and (vins[k].get("prevout") or {}).get("scriptpubkey"):
            spk = bytes.fromhex(vins[k]["prevout"]["scriptpubkey"])
        out.append(spk)
    return out

def read_tx(api, txid, meta=None, local=None, prevs=True):
    """describe() of a fetched tx. A raw that cannot be read or decoded is reported as Unavailable, so one
    odd transaction never aborts the run. prevs=False describes the input scripts alone."""
    hx = api.tx_hex(txid)
    try:
        return describe(hx, prev_spks(api, parse_raw(hx), meta, local) if prevs else None)
    except (ValueError, KeyError, IndexError, TypeError) as e:
        raise Unavailable(f"{txid}: raw does not decode ({type(e).__name__}: {e})")

def who(scripts):
    parts = []
    for d in scripts:
        s = f"{label(d['address'])} ({d['kind']})"
        if d["m"] and len(d["pubkeys"]) > 1:
            s += " keys " + ", ".join(p.hex() for p in d["pubkeys"])
        if not d["ok"]:
            s += f" [INVALID: {d['note']}]"
        parts.append(s)
    return sorted(set(parts))

def verify_tx(api, tx):
    """Per-input offline signature check using parents already on hand. Returns (ok, bad, unchecked),
    where bad and unchecked map each reason to its count."""
    ok, bad, un = 0, {}, {}
    for i, v in enumerate(tx["vin"]):
        if v["txid"] == COINBASE:
            un["coinbase"] = un.get("coinbase", 0) + 1; continue
        phx = api.cached_hex(v["txid"])
        if phx is None:
            un["parent not fetched"] = un.get("parent not fetched", 0) + 1; continue
        o = parse_raw(phx)["vout"][v["vout"]]
        r = T.verify_input(tx, i, bytes.fromhex(o["spk"]), o["sat"])
        if r["ok"] is True:
            ok += 1
        elif r["ok"] is False:
            bad[r["why"]] = bad.get(r["why"], 0) + 1
        else:
            why = r["why"].replace("not checkable: ", "")
            un[why] = un.get(why, 0) + 1
    return ok, bad, un

def sigtag(api, tx):
    ok, bad, un = verify_tx(api, tx)
    n = len(tx["vin"])
    if bad:
        return f"SIGNATURE FAILS on {sum(bad.values())}/{n} (" + "; ".join(f"{c}: {w}" for w, c in sorted(bad.items())) + ")"
    return f"sigs verified {ok}/{n}" + (" (" + "; ".join(f"{c} unchecked: {w}" for w, c in sorted(un.items())) + ")" if un else "")

def saved(prefix):
    return next(t for t in RT.load_saved() if t["txid"].startswith(prefix))

# ---------- 1. 2024 split parents ----------
def lookup_2024(api, out, split_prefix="88cdb3cd", skip_prefix="2aa9a4a9"):
    split = saved(split_prefix)
    parents = [v for v in split["vin"] if not (skip_prefix and v["txid"].startswith(skip_prefix))]
    out.append(f"## 1. The parents of the `{split_prefix}…` split's inputs"
               + (f" (other than the `{skip_prefix}…` change)" if skip_prefix else "") + "\n")
    repeats, missing = False, 0
    for v in parents:
        try:
            tx, signers, outs, memos, scripts = read_tx(api, v["txid"])
        except Unavailable as e:
            missing += 1; out.append(f"- `{v['txid']}:{v['vout']}`: unavailable ({e})"); continue
        n, sat, kind, a, _ = outs[v["vout"]]
        creator = any(a2 in (RT.CREATOR, FUNDER, RT.HALF) for _, a2, _ in signers)
        repeats |= creator and bool(memos)
        others = [f"{s2} → {label(x)}" for n2, s2, k2, x, d2 in outs if k2 != "op_return" and n2 != v["vout"]]
        out.append(f"- `{v['txid']}:{v['vout']}` ({sat} sat → {label(a)}): parent signed by {', '.join(who(scripts))}; "
                   f"memo {memos or 'none'}; creator-signed: {creator}" + (f"; its other outputs: {', '.join(others)}" if others else ""))
    verdict = "unavailable" if missing == len(parents) else ("YES" if repeats else "NO" + (" (partial)" if missing else ""))
    what = "2024 repeats the 2020 memo→split pattern" if split_prefix == "88cdb3cd" else "a creator-signed parent carries a memo"
    out.append(f"\n**{what}: {verdict}**\n")
    return verdict

# ---------- 2. ancestry ----------
def ancestry(api, starts, depth, max_fetch):
    """Backward BFS over every input, reading depths 0 .. depth-1. Returns (records, fetched, missing,
    cut); a record is (depth, txid, scripts, memos, height, time, tx); cut is None when the walk ran
    out at its depth bound, else (transactions left unread in the frontier, the shallowest depth)."""
    frontier, seen, recs, fetched, missing, raws = [(s, 0) for s in starts], set(), [], 0, [], {}
    while frontier and fetched < max_fetch:
        txid, d = frontier.pop(0)
        if txid in seen or txid == COINBASE:
            continue
        seen.add(txid)
        try:
            tx, signers, _, memos, scripts = read_tx(api, txid, prevs=False); fetched += 1
        except Unavailable as e:
            missing.append((d, txid, str(e))); continue
        raws[txid] = tx["raw"]
        h, t = api.tx_status(txid)
        recs.append((d, txid, scripts, memos, h, t, tx))
        if any(sc["address"] in CREATOR_TRAIL for sc in scripts):
            continue                                        # reached the trail on this branch
        if d + 1 < depth:
            frontier += [(v["txid"], d + 1) for v in tx["vin"]]
    # attribute signers once more with the spent scripts of parents this walk itself read (p2pk, p2tr, …)
    recs = [(d, txid, describe(tx["raw"], prev_spks(api, tx, local=raws))[4], memos, h, t, tx)
            for d, txid, scripts, memos, h, t, tx in recs]
    left = {}
    for txid, d in frontier:
        if txid not in seen and txid != COINBASE:
            left[txid] = min(d, left.get(txid, d))
    return recs, fetched, missing, ((len(left), min(left.values())) if left else None)

def walk_verdict(recs, fetched, missing, cut, depth, max_fetch):
    """(text, state): state True = reaches the trail, False = walked to the bound without reaching it,
    None = not determined (nothing read, fetch cap hit, or a transaction could not be read)."""
    hits = [(d, txid, sc["address"]) for d, txid, scripts, *_ in recs for sc in scripts if sc["address"] in CREATOR_TRAIL]
    if hits:
        d, txid, a = min(hits)
        return f"YES: {label(a)} signs at depth {d} (`{txid}`)", True
    if fetched == 0:
        return "unavailable", None
    gaps = ([f"the fetch cap ({max_fetch}) stopped it with {cut[0]} transaction(s) unread from depth {cut[1]}"] if cut else []) \
        + ([f"{len(missing)} transaction(s) unavailable"] if missing else [])
    if gaps:
        return f"NOT DETERMINED: no creator-trail signer among {fetched} transactions read, but " + "; ".join(gaps), None
    return f"NO within depths 0–{depth - 1} ({fetched} transactions read; walk complete)", False

def lookup_funder(api, out, depth, max_fetch, start=None):
    default = saved("a798905f")["vin"][0]["txid"]          # 547246e9…, which funded 3GSMG24T
    start = start or default
    out.append(f"## 2. Who funded 3GSMG24T (walk up from `{start}`, depths 0–{depth - 1}, ≤ {max_fetch} fetches)\n")
    recs, fetched, missing, cut = ancestry(api, [start], depth, max_fetch)
    for d, txid, scripts, memos, h, t, tx in recs:
        out.append(f"- depth {d} `{txid}` (height {h or '?'}, {when(t)}): inputs signed by {', '.join(who(scripts))}"
                   + (f"; memo {memos}" if memos else "") + f"; {sigtag(api, tx)}")
    for d, txid, e in missing:
        out.append(f"- depth {d} `{txid}`: unavailable ({e})")
    verdict, _ = walk_verdict(recs, fetched, missing, cut, depth, max_fetch)
    what = "3GSMG24T traces to the creator trail" if start == default else "the walk reaches the creator trail"
    out.append(f"\n**{what}: {verdict}**\n")
    return verdict

# ---------- 3. the 2021 memo ----------
def lookup_2021(api, out, max_pages=20):
    creator_pub = RT.signer(saved("a798905f")["vin"][0])[2].hex()   # 3GSMG24T's witness pubkey
    out.append(f"## 3. The 2021 \"neighbors, half and double\" transaction (via `{QMG}`)\n")
    try:
        hist, complete = api.address_history(QMG, max_pages)     # first request as before; later pages if any
        txids = [h["txid"] for h in hist]
    except Unavailable as e:
        out.append(f"- unavailable ({e})\n\n**Signed by 3GSMG24T's key: unavailable**\n")
        return "unavailable"
    verdict, missing = "NO", 0
    for txid in txids:
        try:
            tx, signers, outs, memos, scripts = read_tx(api, txid)
        except Unavailable as e:
            missing += 1; out.append(f"- `{txid}`: unavailable ({e})"); continue
        keys = sorted({(label(a), p.hex() if p else None) for _, a, p in signers})
        ok = all(a == RT.CREATOR and p is not None and p.hex() == creator_pub for _, a, p in signers)
        verdict = "YES" if ok else verdict
        out.append(f"- `{txid}`: signers {keys}; memo {memos}; {sigtag(api, tx)}; outputs "
                   + ", ".join(f"{sat} → {label(a)}" for _, sat, kind, a, _ in outs if kind != "op_return"))
    if txids and missing == len(txids):
        verdict = "unavailable"
    elif (missing or not complete) and verdict == "NO":
        verdict = "NO (partial" + ("" if complete else ": Q−G history incomplete, raise --max-pages") + ")"
    out.append(f"\n**Signed by 3GSMG24T's key `{creator_pub[:16]}…`: {verdict}** ({len(txids)} tx at Q−G)\n")
    return verdict

# ---------- 4. the 3GSMG24T fan-out ----------
def expected_receipts():
    """The creator receipts the ledger already knows (ticks 38, 52, 59, 63)."""
    lab = labels()
    exp = {a: l for a, l in lab.items() if l.startswith("answer-key") and "uncompressed" not in l}   # six checkpoints
    exp.update({"148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ": "Good job, Neo! (seed raw key)",
                "13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp": "Good job, Neo! (seed raw key, bits reversed)",
                "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": "open checkpoint (bare 1050 sat)",
                RT.HALF: "prize (Halving dust)"})
    exp.update({a: f"2021 memo: prize point {k}" for k, a in RT.TICK52_POINTS.items()})
    return exp

# pre-registered H1 (intake/2026-09-26-fanout/PREREG.md): recipient -> fuel outputs its one emission consumes
H1_ROOT = "1f8eb99e"                                  # 37mh…'s 15,000 sat funding of 3GSMG24T
H1_EXPECT = {"1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ": 1, "1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff": 1,
             "18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc": 1, "1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq": 1,
             "1AD2wfwXukZ1kUAy848hTQQ72aSBZPB75r": 1, "1M5ypvDbp124ZtKPbg3GJg1JqNs1x7TPoN": 1,
             "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": 1, SEEDKEY: 1, "13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp": 1,
             RT.HALF: 3}
# the PREREG table's other attributes of those emissions: memo ("any" = a memo is present, None = bare) and amount
H1_ATTRS = {**{a: {"memo": "any"} for a in ("1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ", "1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff",
                                              "18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc", "1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq",
                                              "1AD2wfwXukZ1kUAy848hTQQ72aSBZPB75r", "1M5ypvDbp124ZtKPbg3GJg1JqNs1x7TPoN")},
            "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": {"memo": None, "sat": 1050},
            SEEDKEY: {"memo": "Good job, Neo!"}, "13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp": {"memo": "Good job, Neo!"},
            RT.HALF: {"memo": "Halving", "sat": 700}}

def h1_check(addr, txs, cls, spent_by, mine, unread, full, root_prefix=H1_ROOT):
    """The 12 -> 12 test, exactly as pre-registered: the tree rooted at the root tx's outputs to `addr`
    has exactly 12 outputs spent by non-split transactions (the fuel), those are exactly the 10
    expected emissions consuming exactly those 12 outputs, nothing is left unspent, and nobody else is
    paid. Returns {'verdict': PASS | FAIL | UNDETERMINED, 'diffs', 'fuel', 'emissions'}."""
    roots = sorted(t for t in txs if t.startswith(root_prefix))
    if not roots:
        why = f"the root `{root_prefix}…` is not among the read history transactions"
        return {"verdict": "FAIL" if full else "UNDETERMINED", "diffs": [why], "fuel": 0, "emissions": []}
    root, seen, fuel, gaps, unspent, splits = roots[0], set(), {}, [], [], []   # fuel: outpoint -> non-split spender
    gap_txids = []
    open_q = [(root, n) for n, s, k, a, _ in txs[root][2] if a == addr]
    while open_q:
        op = open_q.pop(0)
        if op in seen:
            continue
        seen.add(op)
        sp = spent_by.get(op)
        if sp is None:
            unspent.append(op); continue
        if sp in unread or sp not in txs:
            gaps.append(f"`{op[0][:12]}…:{op[1]}` is spent by `{sp[:12]}…`, whose raw was not read")
            gap_txids.append(sp); continue
        if cls[sp] == "split":
            if sp not in splits:
                splits.append(sp)
            open_q += [(sp, n) for n, s, k, a, _ in txs[sp][2] if a == addr]
        else:
            fuel[op] = sp
    diffs, per_recipient, emissions = [], {}, []
    for t in splits:                                        # the fuel must come from the root alone
        outside = [(v["txid"], v["vout"]) for v in txs[t][0]["vin"] if (v["txid"], v["vout"]) not in seen]
        if outside:
            diffs.append(f"`{t[:12]}…` (a split) also spends {len(outside)} input(s) from outside the tree")
    for t in dict.fromkeys(fuel.values()):                 # leaf spends in tree (breadth-first) order
        tx, signers, outs, memos, scripts = txs[t]
        ins = [(v["txid"], v["vout"]) for v in tx["vin"]]
        used = [op for op in ins if fuel.get(op) == t]
        if len(used) != len(ins):
            diffs.append(f"`{t[:12]}…` also spends {len(ins) - len(used)} input(s) from outside the tree")
        if any(a == addr for n, s, k, a, _ in outs):
            diffs.append(f"`{t[:12]}…` pays change back to the address, so it is not a leaf spend")
        paid = {}
        for n, s, k, a, _ in outs:
            if k != "op_return" and a != addr:
                paid.setdefault(a or "nonstandard:" + tx["vout"][n]["spk"], []).append(s)
        if len(paid) != 1:
            diffs.append(f"`{t[:12]}…` pays {len(paid)} recipients")
        for a, sats in paid.items():
            if len(sats) > 1:
                diffs.append(f"`{t[:12]}…` pays {label(a)} in {len(sats)} outputs")
            per_recipient.setdefault(a, {})[t] = (len(used), sum(sats), memos)
        emissions.append({"txid": t, "recipients": list(paid), "fuel_outputs": len(used), "memo": memos,
                          "sat": [sum(v) for v in paid.values()]})
    for a, want in H1_EXPECT.items():
        got = per_recipient.get(a, {})
        if len(got) != 1:
            diffs.append(f"{label(a)}: {len(got)} emission(s) from the tree, expected 1")
            continue
        (t, (nfuel, sat, memos)), = got.items()
        if nfuel != want:
            diffs.append(f"{label(a)}: its emission consumes {nfuel} fuel output(s), expected {want}")
        attrs = H1_ATTRS.get(a, {})
        if "memo" in attrs:
            m = attrs["memo"]
            if m is None and memos:
                diffs.append(f"{label(a)}: its emission carries memo {memos}, expected a bare payment")
            elif m == "any" and not memos:
                diffs.append(f"{label(a)}: its emission carries no memo, expected a checkpoint memo")
            elif m not in (None, "any") and m not in memos:
                diffs.append(f"{label(a)}: its emission carries memo {memos or 'none'}, expected {m!r}")
        if "sat" in attrs and sat != attrs["sat"]:
            diffs.append(f"{label(a)}: its emission pays {sat} sat, expected {attrs['sat']}")
    diffs += [f"another recipient: {label(a)}" for a in sorted(per_recipient) if a not in H1_EXPECT]
    if unspent:
        diffs.append(f"{len(unspent)} tree output(s) " + ("unspent" if full else "not spent within the fetched history")
                     + ": " + ", ".join(f"`{t[:12]}…:{n}`" for t, n in unspent))
    if len(fuel) != 12:
        diffs.append(f"{len(fuel)} fuel outputs (tree outputs spent by a non-split transaction), expected 12")
    if len(emissions) != 10:
        diffs.append(f"{len(emissions)} leaf spends, expected 10")
    verdict = "PASS" if not diffs and not gaps and full else ("UNDETERMINED" if gaps or not full else "FAIL")
    if gaps:                                                # what lies past an unread spend is not known
        diffs = [f"in the read part of the tree: {d}" for d in diffs]
    return {"verdict": verdict, "diffs": gaps + diffs, "fuel": len(fuel), "emissions": emissions, "root": root,
            "splits": splits, "gap_txids": list(dict.fromkeys(gap_txids))}

def input_keys(sc):
    """Public keys (hex) an input exposes: its script's keys, or for taproot the output key from the spent script,
    written as a compressed key so that rule (ii)'s x-coordinate comparison applies."""
    keys = [p.hex() for p in sc["pubkeys"]]
    if sc["kind"].startswith("p2tr") and sc.get("spk") and len(sc["spk"]) == 34:
        keys.append("02" + sc["spk"][2:].hex())
    return keys

def lookup_fanout(api, out, max_pages, addr=RT.CREATOR, h1_root=H1_ROOT):
    out.append(f"## 4. The complete {label(addr)} fan-out (from its full address history)\n")
    try:
        hist, complete = api.address_history(addr, max_pages)
    except Unavailable as e:
        out.append(f"- unavailable ({e})\n\n**Fan-out: unavailable**\n")
        return {"verdict": "unavailable", "funders": [], "funding_events": [], "inbound": [], "complete": False,
                "h1": {"verdict": "UNDETERMINED", "diffs": ["address history unavailable"]}}
    meta = {h["txid"]: h for h in hist}
    txs, missing = {}, []
    for h in hist:
        try:
            txs[h["txid"]] = read_tx(api, h["txid"], h)
        except Unavailable as e:
            missing.append((h["txid"], str(e)))
    unread = {t for t, _ in missing}
    full = complete and not unread                          # every history tx listed and its raw read
    def hstat(txid):
        st = (meta.get(txid) or {}).get("status") or {}
        return st.get("block_height"), st.get("block_time")
    def vin_of(t):
        """[(parent txid, vout, signer address or None)]: from the raw, else explorer-reported."""
        if t in txs:
            return [(v["txid"], v["vout"], sc["address"]) for v, sc in zip(txs[t][0]["vin"], txs[t][4])]
        return [(v.get("txid"), v.get("vout"), (v.get("prevout") or {}).get("scriptpubkey_address"))
                for v in (meta.get(t) or {}).get("vin") or []]
    mine = {}                                               # (txid, n) -> sat, outputs paying addr
    spent_by = {}                                           # (txid, n) -> spending txid
    cls, inbound, cosigners = {}, [], {}
    for txid, (tx, signers, outs, memos, scripts) in txs.items():
        for n, sat, kind, a, _ in outs:
            if a == addr:
                mine[(txid, n)] = sat
    for t in sorted(unread):                                # explorer-reported outputs of unread txs
        for n, o in enumerate((meta.get(t) or {}).get("vout") or []):
            if o.get("scriptpubkey_address") == addr:
                mine[(t, n)] = o.get("value")
    for t in list(txs) + sorted(unread):
        ins = vin_of(t)
        for ptx, pn, _ in ins:
            spent_by[(ptx, pn)] = t
        if t in unread:
            cls[t] = "unread"
            if ins and not any(a == addr for *_, a in ins):
                inbound.append(t)
            elif ins and not all(a == addr for *_, a in ins):
                cosigners[t] = {a for *_, a in ins if a != addr}    # explorer-reported co-signers
            continue
        tx, signers, outs, memos, scripts = txs[t]
        from_me = [sc["address"] == addr for sc in scripts]
        to_other = [(n, sat, a) for n, sat, kind, a, _ in outs if kind != "op_return" and a != addr]
        if not any(from_me):
            cls[t] = "inbound"; inbound.append(t)
        elif all(from_me) and not to_other and any(a == addr for n, sat, kind, a, _ in outs):
            cls[t] = "split"
        elif all(from_me):
            cls[t] = "emit"
        else:
            cls[t] = "mixed"
            cosigners[t] = {sc["address"] for sc in scripts if sc["address"] != addr}
    order = sorted(cls, key=lambda t: (hstat(t)[0] or 10**9, t))
    blind_in = {t for t in unread if not vin_of(t)}          # unread and no explorer inputs: spends unknown
    def out_label(a, spk_hex):
        return label(a) if a is not None else "nonstandard:" + spk_hex
    # tree
    printed = set()
    def node(outpoint, indent):
        sat = mine.get(outpoint)
        sp = spent_by.get(outpoint)
        head = f"{'  ' * indent}- `{outpoint[0][:12]}…:{outpoint[1]}` {sat} sat"
        if sp is None:
            out.append(head + (" → **UNSPENT** (remaining fuel)" if full else
                               f" → spend status unknown ({len(blind_in)} unread transaction(s) with unknown inputs)"
                               if blind_in else " → not spent within the fetched history"))
            return
        if sp in printed:
            out.append(head + f" → spent by `{sp[:12]}…` (shown above)")
            return
        printed.add(sp)
        h, t = hstat(sp)
        if sp in unread:
            out.append(head + f" → spent by `{sp}` [raw not read] (height {h or '?'}, {when(t)}); outputs explorer-reported:")
            for n, o in enumerate((meta.get(sp) or {}).get("vout") or []):
                spk_hex = o.get("scriptpubkey") or ""
                if o.get("scriptpubkey_address") == addr:
                    node((sp, n), indent + 1)
                elif spk_hex.startswith("6a"):
                    memo = script_info(bytes.fromhex(spk_hex))[2]
                    out.append(f"{'  ' * (indent + 1)}- out {n}: OP_RETURN {memo.decode('latin1')!r}")
                else:
                    out.append(f"{'  ' * (indent + 1)}- out {n}: {o.get('value')} sat → "
                               f"{out_label(o.get('scriptpubkey_address'), spk_hex)}")
            return
        tx, signers, outs, memos, scripts = txs[sp]
        out.append(head + f" → spent by `{sp}` [{cls[sp]}] (height {h or '?'}, {when(t)}; {sigtag(api, tx)})"
                   + (f" memo {memos}" if memos else ""))
        for n, s2, kind, a, _ in outs:
            if kind == "op_return":
                continue
            if a == addr:
                node((sp, n), indent + 1)
            else:
                out.append(f"{'  ' * (indent + 1)}- out {n}: {s2} sat → {out_label(a, tx['vout'][n]['spk'])}")
    def paid_to_me(t):
        return sorted(n for (tt, n) in mine if tt == t)
    out.append("**Inbound funding** (transactions not signed by the address that pay it):\n")
    for txid in sorted(inbound, key=lambda t: (hstat(t)[0] or 10**9, t)):
        h, t = hstat(txid)
        pays = ", ".join(f"out {n}: {mine[(txid, n)]} sat" for n in paid_to_me(txid))
        if txid in unread:
            payers = sorted({str(a) for *_, a in vin_of(txid)})
            out.append(f"- `{txid}` (height {h or '?'}, {when(t)}) [raw not read] paid by {', '.join(payers)} "
                       f"(explorer-reported); pays {pays}")
            continue
        tx, signers, outs, memos, scripts = txs[txid]
        out.append(f"- `{txid}` (height {h or '?'}, {when(t)}) signed by {', '.join(who(scripts))}; {sigtag(api, tx)}; "
                   f"pays {pays}" + (f"; memo {memos}" if memos else ""))
    out.append("\n**UTXO tree** (each output paid to the address, followed to whatever spends it):\n")
    for txid in sorted(inbound, key=lambda t: (hstat(t)[0] or 10**9, t)):
        for n in paid_to_me(txid):
            node((txid, n), 0)
    in_history = set(cls)
    orphans = [t for t in order if t not in printed and cls[t] != "inbound" and t not in inbound and t not in blind_in
               and not any(ptx in in_history for ptx, *_ in vin_of(t))]
    if orphans:
        out.append("\nSpends whose funding lies outside the fetched history (their own outputs followed):")
        for t in orphans:
            if t in printed:
                continue
            printed.add(t)
            h, tt = hstat(t)
            if t in unread:
                out.append(f"- `{t}` [raw not read] (height {h or '?'}, {when(tt)})")
            else:
                tx, signers, outs, memos, scripts = txs[t]
                out.append(f"- `{t}` [{cls[t]}] (height {h or '?'}, {when(tt)}; {sigtag(api, tx)}) memo {memos or 'none'}; "
                           + ", ".join(f"out {n}: {s} → {out_label(a, tx['vout'][n]['spk'])}"
                                       for n, s, k, a, _ in outs if k != "op_return"))
            for n in paid_to_me(t):
                node((t, n), 1)
    if blind_in:
        out.append("\nTransactions whose raw was not read and whose inputs are unknown: "
                   + ", ".join(f"`{t}`" for t in sorted(blind_in)))
    rest = [t for t in order if t not in printed and cls[t] != "inbound" and t not in inbound and t not in blind_in]
    if rest:
        out.append("\nOther spends not reached from any root: " + ", ".join(f"`{t}` [{cls[t]}]" for t in rest))
    # census: every non-self output of the address's own transactions; a co-signer's change is not a receipt
    seen, returned = {}, []
    for t in order:
        if cls[t] in ("emit", "mixed"):
            tx, signers, outs, memos, scripts = txs[t]
            for n, s, k, a, _ in outs:
                if k == "op_return" or a == addr:
                    continue
                if a is not None and a in cosigners.get(t, ()):
                    returned.append((t, s, a)); continue
                seen.setdefault(a if a is not None else "nonstandard:" + tx["vout"][n]["spk"], []).append((t, s, memos))
    exp = expected_receipts()
    lab = labels()
    out.append("\n**Recipient census** (every non-self output of the address's own transactions):\n")
    for a, rows in sorted(seen.items()):
        tag = "expected" if a in exp else ("GSMG-labelled" if a in lab else "**UNKNOWN: a creator receipt not in the ledger**")
        out.append(f"- {label(a)}: " + "; ".join(f"{s} sat in `{t[:12]}…` memo {m or 'none'}" for t, s, m in rows) + f" — {tag}")
    for t, s, a in returned:
        out.append(f"- {label(a)}: {s} sat in `{t[:12]}…` — change back to a co-signer of that transaction (not a receipt)")
    spends_unread = [t for t in sorted(unread) if t not in inbound]
    explorer_seen = {o.get("scriptpubkey_address") for t in spends_unread for o in (meta.get(t) or {}).get("vout") or []}
    if spends_unread:
        out.append(f"- the recipients of {len(spends_unread)} spend(s) whose raw was not read are not in this census")
    missing_exp = [f"{a} [{l}]" + (" (seen only in explorer-reported outputs of an unread spend)" if a in explorer_seen else "")
                   for a, l in exp.items() if a not in seen]
    out.append(f"\nExpected but not seen: {', '.join(missing_exp) or 'none'}")
    unknown = [a for a in seen if a not in exp and a not in lab]
    # accounting: an input's amount from its parent raw (txid-verified) or else the explorer's prevout
    def in_values(t):
        vals = []
        mv = (meta.get(t) or {}).get("vin") or []
        for k, v in enumerate(txs[t][0]["vin"]):
            phx = api.cached_hex(v["txid"]) if v["txid"] != COINBASE else None
            if phx:
                vals.append(parse_raw(phx)["vout"][v["vout"]]["sat"])
            elif k < len(mv) and (mv[k].get("prevout") or {}).get("value") is not None:
                vals.append(mv[k]["prevout"]["value"])
            else:
                vals.append(None)
        return vals
    tin = sum(s or 0 for (t, n), s in mine.items() if t in inbound)
    foreign, fees, unknown_in, spends = 0, 0, 0, 0
    for t in txs:
        if cls[t] == "inbound":
            continue
        vals = in_values(t)
        if None in vals:
            unknown_in += 1; continue
        spends += 1
        fees += sum(vals) - sum(o["sat"] for o in txs[t][0]["vout"])
        if cls[t] == "mixed":
            foreign += sum(v for v, sc in zip(vals, txs[t][4]) if sc["address"] != addr)
    emitted = sum(s for rows in seen.values() for _, s, _ in rows)
    back = sum(s for _, s, _ in returned)
    unspent = sum(s or 0 for op, s in mine.items() if op not in spent_by)
    balanced = full and unknown_in == 0 and tin + foreign == emitted + back + unspent + fees
    out.append(f"\n**Fuel accounting:** inbound {tin} sat" + (f" plus {foreign} sat of co-signers' inputs" if foreign else "")
               + f"; emitted to others {emitted} sat" + (f"; returned to co-signers {back} sat" if back else "")
               + f"; unspent at the address {unspent} sat; fees {fees} sat over the {spends} spend(s) with every input "
               f"amount known" + (f"; {unknown_in} spend(s) have an input amount not on hand" if unknown_in else "")
               + f"; books balance: {balanced}" + ("" if complete else " (history incomplete: raise --max-pages)")
               + ("" if not unread else f" ({len(unread)} transaction raw(s) not read)"))
    if missing:
        out.append("\nUnavailable transactions: " + ", ".join(f"`{t}` ({e})" for t, e in missing))
    # the fundings the address went on to spend, with who signed them; co-signers of mixed spends too
    used = sorted({t for (t, n) in mine if (t, n) in spent_by and t in inbound})
    events = []
    for t in used:
        ins = vin_of(t)
        events.append({"txid": t, "kind": "inbound", "signers": sorted({a for *_, a in ins if a}),
                       "unidentified_inputs": sum(1 for *_, a in ins if not a) if ins else None,
                       "source": "raw" if t in txs else "explorer"})
    for t in sorted(cosigners):
        events.append({"txid": t, "kind": "co-signed", "signers": sorted(a for a in cosigners[t] if a),
                       "unidentified_inputs": sum(1 for a in cosigners[t] if not a),
                       "source": "raw" if t in txs else "explorer"})
    funders = sorted({a for e in events for a in e["signers"]})
    blind = [e["txid"] for e in events if e["unidentified_inputs"] or e["unidentified_inputs"] is None]
    if blind:
        out.append("\nFundings with a signer whose address could not be identified (not evaluated): "
                   + ", ".join(f"`{t}`" for t in blind))
    idle = sorted({a for t in inbound if t not in used for *_, a in vin_of(t) if a} - set(funders))
    if idle:
        out.append(f"\nInbound deposits never spent by the address (not funding; not evaluated): "
                   + ", ".join(label(a) for a in idle)
                   + (f" (provisional: {len(blind_in)} unread transaction(s) with unknown inputs may spend some)" if blind_in else ""))
    verdict = f"{len(cls)} transactions; {len(inbound)} inbound; {sum(1 for c in cls.values() if c == 'emit')} emissions; " \
              f"{len(unknown)} unknown recipients" + ("" if complete else "; history INCOMPLETE") \
              + (f"; {len(unread)} raw(s) not read: INCOMPLETE" if unread else "")
    out.append(f"\n**Fan-out: {verdict}**\n")
    # each inbound tx's inputs (parent txid, signer, keys), for the funder evaluation in section 6
    inbound_inputs = {}
    for t in inbound:
        if t in txs:
            inbound_inputs[t] = [(v["txid"], sc["address"], input_keys(sc))
                                 for v, sc in zip(txs[t][0]["vin"], txs[t][4])]
        else:
            inbound_inputs[t] = [(ptx, a, []) for ptx, _, a in vin_of(t)]
    cosigned_inputs = {}
    for t in cosigners:
        if t in txs:
            cosigned_inputs[t] = [(v["txid"], sc["address"], input_keys(sc))
                                  for v, sc in zip(txs[t][0]["vin"], txs[t][4]) if sc["address"] != addr]
        else:
            cosigned_inputs[t] = [(ptx, a, []) for ptx, _, a in vin_of(t) if a != addr]
    # H1, as pre-registered
    h1 = h1_check(addr, txs, cls, spent_by, mine, unread, full, h1_root)
    out.append("### H1 (pre-registered): the 37mh… funding cut into 12 fuel outputs, consumed by the 10 known emissions\n")
    for e in h1["emissions"]:
        out.append(f"- `{e['txid']}` consumes {e['fuel_outputs']} fuel output(s) → "
                   + ", ".join(f"{s} sat → {label(a)}" for a, s in zip(e["recipients"], e["sat"])) + f"; memo {e['memo'] or 'none'}")
    for d in h1["diffs"]:
        out.append(f"- difference: {d}")
    out.append(f"\n**H1 (12 → 12): {h1['verdict']}** ({h1['fuel']} fuel outputs, {len(h1['emissions'])} leaf spends"
               + (f" from `{h1['root'][:12]}…`" if h1.get("root") else "") + ")\n")
    return {"verdict": verdict, "funders": funders, "funding_events": events, "unknown_recipients": unknown,
            "complete": full, "history_complete": complete, "unread": sorted(unread), "inbound": inbound,
            "inbound_inputs": inbound_inputs, "cosigned_inputs": cosigned_inputs, "classes": cls, "h1": h1}

# ---------- 5 and 6. funders: history and promotion ----------
def known_keys():
    """x-coordinates of every public key in authenticated GSMG material."""
    xs = {}
    split = saved("2aa9a4a9")
    for k, a, p in (RT.signer(v) for v in split["vin"]):
        if p is not None: xs[p[1:33].hex()] = "prize key"
    xs[RT.signer(saved("a798905f")["vin"][0])[2][1:33].hex()] = "3GSMG24T key"
    for t in RT.load_saved():
        for k, a, p in (RT.signer(v) for v in t["vin"]):
            if p is not None and a in labels():
                xs.setdefault(p[1:33].hex(), f"signer key of {label(a)}")
    for pt in json.load(open(os.path.join(CHAIN, "nonce_points_prize.json")))["points"]:
        xs.setdefault(pt["x"], f"prize nonce point {pt['label']}")
    return xs

def repo_mentions(hexes):
    """Files of authenticated puzzle material (neo/materials, excluding materials/chain, which holds this
    tool's own fetched raws and reports) that mention any of the hexes."""
    roots = [os.path.join(RT.NEO, "materials")]           # authenticated puzzle material only; not our own notes
    hits = []
    for root in roots:
        paths = [root] if os.path.isfile(root) else [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs]
        for p in paths:
            if os.path.relpath(p, root).split(os.sep)[0] == "chain":   # our own chain notes and fetched raws
                continue
            try:
                s = open(p, errors="ignore").read().lower()
            except OSError:
                continue
            for h in hexes:
                if h in s:
                    hits.append((os.path.relpath(p, RT.NEO), h[:16]))
    return hits

def lookup_funders(api, out, fan, depth, max_fetch, max_pages, only=None):
    out.append("## 5. The wallets that funded 3GSMG24T: full history\n")
    funders = only or [a for a in fan.get("funders", []) if a != SEEDKEY]
    if fan.get("funders") and SEEDKEY in fan["funders"] and not only:
        out.append(f"- {label(SEEDKEY)} also paid the address; it is the public-knowledge Phase-0 seed key (tick 56), "
                   "so it authenticates nobody and is not evaluated.")
    if not funders:
        out.append("- no funder to evaluate" + ("" if fan.get("complete") else
                                                 " (the fan-out is incomplete, so a funder may be missing)"))
    results = {}
    lab = labels()
    for f in funders:
        r = {"address": f}
        try:
            stats = api.address_stats(f)
            hist, complete = api.address_history(f, max_pages)
        except Unavailable as e:
            out.append(f"- {f}: unavailable ({e})"); results[f] = {"address": f, "unavailable": str(e)}; continue
        cs = (stats or {}).get("chain_stats", {})
        n_tx = cs.get("tx_count", len(hist)) + (stats or {}).get("mempool_stats", {}).get("tx_count", 0)
        rows, touch = [], 0
        for h in hist:
            addrs = {(v.get("prevout") or {}).get("scriptpubkey_address") for v in h.get("vin", [])} | \
                    {o.get("scriptpubkey_address") for o in h.get("vout", [])}
            addrs.discard(None); addrs.discard(f)
            g = sorted(a for a in addrs if a in lab)
            touch += bool(g)
            net = sum(o.get("value", 0) for o in h.get("vout", []) if o.get("scriptpubkey_address") == f) - \
                  sum((v.get("prevout") or {}).get("value", 0) for v in h.get("vin", [])
                      if (v.get("prevout") or {}).get("scriptpubkey_address") == f)
            st = h.get("status") or {}
            rows.append((st.get("block_height"), st.get("block_time"), h["txid"], net, g, len(addrs)))
        rows.sort(key=lambda x: (x[0] or 10**9))
        hs = [x[0] for x in rows if x[0]]
        r.update(n_tx=n_tx, complete=complete, touch=touch, first=(hs[0] if hs else None), last=(hs[-1] if hs else None),
                 txids={h["txid"] for h in hist}, stubs=bool(hist) and all("vin" not in h and "vout" not in h for h in hist),
                 funded=cs.get("funded_txo_sum"), spent=cs.get("spent_txo_sum"))
        out.append(f"### {f}\n")
        out.append(f"- {n_tx} transactions ({'complete' if complete else 'INCOMPLETE: raise --max-pages'}); "
                   f"first block {r['first'] or '?'} ({when(rows[0][1]) if rows else '?'}), last block {r['last'] or '?'} "
                   f"({when(rows[-1][1]) if rows else '?'}); received {r['funded']} sat, sent {r['spent']} sat; "
                   f"{touch} transaction(s) touch a GSMG-labelled address")
        for hgt, ts, txid, net, g, nadd in rows[:60]:
            out.append(f"  - {hgt or '?'} {when(ts)} `{txid}` net {net:+d} sat, {nadd} counterpart address(es)"
                       + (f"; GSMG: {', '.join(label(a) for a in g)}" if g else ""))
        if len(rows) > 60:
            out.append(f"  - … {len(rows) - 60} more (all in materials/chain/fetched/json/history_{f}.json)")
        results[f] = r
    out.append("\n## 6. Promotion rule for each funder (fixed before the run)\n")
    out.append("PROMOTE if any of these holds: (i) the funder itself, or a signer in its ancestry within the walk "
               "bounds, is a creator-trail signer (1EtbTv…, the prize key, 1GSMG1CLx…, 17ucy1…); (ii) one of its public "
               "keys, by x-coordinate, equals a key in authenticated GSMG material, or its hex appears in neo/materials "
               "(materials/chain, this tool's own fetched data, excluded); (iii) its full history is narrowly "
               f"GSMG-specific: at most {RULE_III[0]} transactions, at least {int(RULE_III[1] * 100)}% touching a "
               "GSMG-labelled address; (iv) it signs two or more separate inbound fundings of 3GSMG24T that 3GSMG24T then "
               "spends. CLOSE as operational funding infrastructure only when all four were evaluated and none holds; "
               "a condition that could not be evaluated makes the verdict NOT DETERMINED. Nothing here becomes an AES "
               "candidate.\n")
    kx = known_keys()
    events = fan.get("funding_events", [])
    verdicts = {}
    for f, r in results.items():
        # the funder's keys and walk starts: every input it signed in an inbound tx, in fan-out order
        fkeys, starts, own = set(), [], []
        sources = [(t, (fan.get("inbound_inputs") or {}).get(t)) for t in fan.get("inbound", [])] + \
                  sorted((fan.get("cosigned_inputs") or {}).items())   # inbound first: the tick-92 walk order
        for t, ins in sources:
            if ins is None or not any(a == f for _, a, _ in ins):
                continue
            for ptx, a, keys in ins:
                if a == f:
                    fkeys.update(keys); starts.append(ptx)
                    if a in CREATOR_TRAIL:
                        own.append((t, a))                  # the funder itself is a creator-trail signer
        recs, fetched, missing, cut = ancestry(api, starts, depth, max_fetch) if starts else ([], 0, [], None)
        walk, s1 = walk_verdict(recs, fetched, missing, cut, depth, max_fetch) if starts else \
            ("no walk: the funder's inputs were not identified in a read funding transaction", None)
        c1 = [(0, t, a) for t, a in own] + \
             [(d, txid, sc["address"]) for d, txid, scripts, *_ in recs for sc in scripts if sc["address"] in CREATOR_TRAIL]
        s1 = True if c1 else s1
        c2 = [(k[:16], kx[k[2:66]]) for k in fkeys if k[2:66] in kx]
        c2 += [(f"{p} mentions {h}…", "materials text") for p, h in repo_mentions([k for k in fkeys] + [k[2:66] for k in fkeys])]
        s2 = True if c2 else (False if fkeys else None)
        n_tx = r.get("n_tx")
        own_funding = {e["txid"] for e in events if f in e["signers"]}
        s3_why = ""
        if "unavailable" in r or n_tx is None:
            s3, s3_why = None, "history unavailable"
        elif n_tx == 0 or (r.get("complete") and not own_funding <= r.get("txids", set())):
            s3, s3_why = None, ("the history fetched for this address does not contain its own funding transaction "
                                "(e.g. a P2PK key, which explorers index by script)")
        elif n_tx > RULE_III[0]:
            s3 = False
        elif r.get("stubs"):
            s3, s3_why = None, "the history entries carry no counterparty data (offline fixture)"
        elif not r.get("complete"):
            s3, s3_why = None, "history incomplete"
        else:
            s3 = r["touch"] >= RULE_III[1] * n_tx
        fund = sorted({e["txid"] for e in events if e["kind"] == "inbound" and f in e["signers"]})
        s4 = True if len(fund) >= 2 else (False if fan.get("complete") else None)
        states = {"i": s1, "ii": s2, "iii": s3, "iv": s4}
        promote = True if True in states.values() else (None if None in states.values() else False)
        verdicts[f] = {"promote": promote, "states": states, "i": c1[:3], "ii": c2, "iii": s3, "iv": fund,
                       "keys": sorted(fkeys), "ancestry_read": fetched, "ancestry_depth": depth,
                       "ancestry_cut": cut, "ancestry_missing": len(missing)}
        undecided = [k for k, v in states.items() if v is None]
        out.append(f"- **{f}**: keys {', '.join(k[:16] + '…' for k in sorted(fkeys)) or '?'}")
        if own:
            out.append(f"  - (i) the funding transaction `{own[0][0]}` itself is signed by {label(own[0][1])}")
        else:
            out.append(f"  - (i) ancestry of its funding inputs (depths 0–{depth - 1}, ≤ {max_fetch} fetches): {walk}")
        out.append(f"  - (ii) key reuse: " + ("; ".join(f"{a} = {b}" for a, b in c2) if c2 else
                                             ("none" if fkeys else "not evaluated: no public key identified")))
        out.append(f"  - (iii) history: {r.get('n_tx', '?')} txs, {r.get('touch', '?')} GSMG-touching, "
                   f"{'complete' if r.get('complete') else 'incomplete'} → "
                   + {True: "narrowly GSMG-specific", False: "not narrowly GSMG-specific",
                      None: f"not evaluated ({s3_why})"}[s3])
        out.append(f"  - (iv) separate inbound fundings of 3GSMG24T it signed that 3GSMG24T then spent: {len(fund)}"
                   + (f" ({', '.join(f'`{t[:12]}…`' for t in fund)})" if fund else "")
                   + {True: " → two or more", False: " → fewer than two",
                      None: " → fewer than two so far; the fan-out is incomplete, so not determined"}[s4])
        out.append("  - **" + ("PROMOTE" if promote else "operational funding infrastructure: close" if promote is False
                               else f"NOT DETERMINED: condition(s) {', '.join(undecided)} not evaluated; neither promoted nor closed")
                   + "**")
    return verdicts

# ---------- offline transaction audit ----------
SIGHASH = {1: "ALL", 2: "NONE", 3: "SINGLE", 0x81: "ALL|ANYONECANPAY", 0x82: "NONE|ANYONECANPAY", 0x83: "SINGLE|ANYONECANPAY"}

class DiskOnly(Esplora):
    """Reads raws and saved address histories already on disk (materials/chain/fetched/); never touches the
    network and never writes."""
    def __init__(self, base):
        super().__init__(base, save=False)

    def _get(self, path):
        raise Unavailable(f"not on hand (audit mode never fetches): {path}")

    def address_history(self, addr, max_pages):
        p = os.path.join(JSONDIR, f"history_{addr}.json")
        if not os.path.exists(p):
            raise Unavailable(f"no saved history for {addr} ({p})")
        h = json.load(open(p))
        return h["txs"], bool(h.get("complete"))

_PRIMARIES = None
def raw_on_hand(api, txid):
    """A raw from the repo's committed primaries (materials/chain/*.hex, checked against the txid) or else from
    the client (disk cache; in the wrapper's verify mode, the frozen HTTP cache). Never fetches in audit mode."""
    global _PRIMARIES
    if _PRIMARIES is None:
        _PRIMARIES = {t["txid"]: t["raw"] for t in RT.load_saved() if parse_raw(t["raw"])["txid"] == t["txid"]}
    return _PRIMARIES[txid] if txid in _PRIMARIES and api.fixture is None else api.tx_hex(txid)

def tx_weight(hx):
    """(weight, stripped size, total size) of a raw transaction."""
    b, tx = bytes.fromhex(hx), parse_raw(hx)
    if not tx["segwit"]:
        return 4 * len(b), len(b), len(b)
    wit = sum(len(T.varint(len(v["witness"]))) + sum(len(T.varstr(bytes.fromhex(w))) for w in v["witness"]) for v in tx["vin"])
    stripped = len(b) - 2 - wit
    return 3 * stripped + len(b), stripped, len(b)

def audit_tx(api, txid, out):
    """Offline audit of one transaction from raws on hand: each input's spent amount and script (from its parent
    raw, txid-verified), every signature (sighash type, strict DER, low S, the key it verifies under), the outputs,
    the fee and the fee rate. Returns {'txid', 'ok' (True: every input valid; False: one invalid; None: something
    not checkable), 'fee', 'vsize'} plus the full structured record (wtxid, sizes, inputs with their signatures,
    outputs, totals, fee rate) that save_audit writes to JSON."""
    try:
        hx = raw_on_hand(api, txid)
    except Unavailable as e:
        out.append(f"### `{txid}`\n\n- raw not on hand ({e})\n")
        return {"txid": txid, "ok": None, "fee": None, "vsize": None, "raw_on_hand": False, "why": str(e)}
    tx = parse_raw(hx)
    weight, stripped, size = tx_weight(hx)
    vsize = -(-weight // 4)
    wtxid = T.dsha(bytes.fromhex(hx))[::-1].hex()
    out.append(f"### `{txid}`\n")
    out.append(f"- raw hashes to its txid; wtxid `{wtxid}`; version {tx['version']}, locktime {tx['locktime']}; "
               f"{size} B, weight {weight}, {vsize} vB")
    total_in, states, ins, outs_rec, coinbase = 0, [], [], [], False
    for i, v in enumerate(tx["vin"]):
        if v["txid"] == COINBASE:
            out.append(f"- in {i}: coinbase (spends no output: no amount, no signature to check)")
            total_in = None; states.append(None); coinbase = True
            ins.append({"index": i, "coinbase": True, "ok": None}); continue
        try:
            o = parse_raw(raw_on_hand(api, v["txid"]))["vout"][v["vout"]]
        except (Unavailable, IndexError) as e:
            d = T.input_script(v)
            out.append(f"- in {i} spends `{v['txid']}:{v['vout']}` ({d['kind']}, {label(d['address'])}): parent raw not on hand, "
                       f"so its amount and signature cannot be checked ({e})")
            total_in = None; states.append(None)
            ins.append({"index": i, "spends": f"{v['txid']}:{v['vout']}", "parent_raw_on_hand": False, "kind": d["kind"],
                        "address": d["address"], "ok": None, "why": str(e)}); continue
        spk = bytes.fromhex(o["spk"])
        r = T.verify_input(tx, i, spk, o["sat"])
        if total_in is not None:
            total_in += o["sat"]
        out.append(f"- in {i} spends `{v['txid']}:{v['vout']}` = {o['sat']} sat → {label(r['address'])} ({r['kind']})")
        for j, sd in enumerate(r["sigs"]):
            ht = sd["hashtype"]
            name = SIGHASH.get(ht, f"{ht:#04x}") if ht is not None else "none (empty)"
            st, nk = sd.get("status"), len(r["pubkeys"])
            key = {"verified": lambda: f"verifies under key {sd['key'] + 1} of {nk} `{r['pubkeys'][sd['key']]}`",
                   "out of CHECKMULTISIG order": lambda: f"verifies only under key {sd['key_any'] + 1} of {nk} "
                                                         f"`{r['pubkeys'][sd['key_any']]}`, out of CHECKMULTISIG order",
                   "does not verify": lambda: "does not verify under any key",
                   "empty": lambda: "empty signature",
                   "not strict DER": lambda: "not strict DER (BIP66)"}.get(st, lambda: "not checked")()
            out.append(f"  - signature {j + 1}: SIGHASH_{name}, {'strict DER' if sd['strict_der'] else 'NOT strict DER'}, "
                       f"{ {True: 'low S', False: 'high S (policy only)', None: 'unparseable r/s'}[sd['low_s']] }; {key}")
        out.append(f"  - input {'VALID' if r['ok'] else 'INVALID' if r['ok'] is False else 'not checked'}: {r['why']}")
        states.append(r["ok"])
        ins.append({"index": i, "spends": f"{v['txid']}:{v['vout']}", "parent_raw_on_hand": True, "amount_sat": o["sat"],
                    "spent_script": o["spk"], "kind": r["kind"], "address": r["address"], "pubkeys": r["pubkeys"],
                    "signatures": [{"sighash": SIGHASH.get(sd["hashtype"], sd["hashtype"]), "strict_der": sd["strict_der"],
                                    "low_s": sd["low_s"], "status": sd.get("status"),
                                    "key_any_index": None if sd.get("key_any") is None else sd["key_any"] + 1,
                                    "key_index": None if sd["key"] is None else sd["key"] + 1,
                                    "pubkey": None if sd["key"] is None else r["pubkeys"][sd["key"]]} for sd in r["sigs"]],
                    "ok": r["ok"], "why": r["why"]})
    total_out = 0
    for o in tx["vout"]:
        kind, a, data = script_info(bytes.fromhex(o["spk"]))
        total_out += o["sat"]
        outs_rec.append({"n": o["n"], "sat": o["sat"], "kind": kind, "address": a, "script": o["spk"],
                         "op_return": data.decode("latin1") if kind == "op_return" else None})
        out.append(f"- out {o['n']}: " + (f"OP_RETURN {data.decode('latin1')!r}" + (f" ({o['sat']} sat)" if o["sat"] else "")
                                          if kind == "op_return" else f"{o['sat']} sat → {label(a)} ({kind})"))
    fee = None if total_in is None else total_in - total_out
    if fee is None:
        out.append("- fee: not applicable (coinbase)" if coinbase else "- fee: not computable (an input amount is not on hand)")
    else:
        out.append(f"- inputs {total_in} sat = outputs {total_out} sat + fee {fee} sat ({fee / vsize:.2f} sat/vB)"
                   + ("" if fee >= 0 else " — NEGATIVE: outputs exceed inputs"))
    ok = False if False in states or (fee is not None and fee < 0) else (None if None in states else True)
    out.append(f"- **every input valid: {ok}**\n")
    return {"txid": txid, "ok": ok, "fee": fee, "vsize": vsize, "raw_on_hand": True, "wtxid": wtxid,
            "version": tx["version"], "locktime": tx["locktime"], "size": size, "weight": weight, "inputs": ins,
            "outputs": outs_rec, "total_in": total_in, "total_out": total_out,
            "fee_rate_sat_vb": None if fee is None else round(fee / vsize, 4)}

def audit_h1(api, out, max_pages, h1_root=H1_ROOT):
    """Audit the whole pre-registered 12 -> 12 tree offline: the root's parent(s), the root, every split and every
    emission, in tree order. Uses the 3GSMG24T history and raws already on hand."""
    fan = lookup_fanout(api, [], max_pages, h1_root=h1_root)
    h1 = fan["h1"]
    out.append(f"## Offline audit of the H1 tree (H1 verdict: {h1['verdict']})\n")
    if not h1.get("root"):
        out.append("- the root is not in the history on hand: " + "; ".join(h1["diffs"]))
        return {"ok": None, "results": [], "h1": h1["verdict"], "diffs": h1["diffs"], "fuel_outputs": h1.get("fuel"),
                "fees_in_tree": None}
    for d in h1["diffs"]:
        out.append(f"- H1 difference: {d}")
    root_tx = parse_raw(raw_on_hand(api, h1["root"]))
    chain = list(dict.fromkeys([v["txid"] for v in root_tx["vin"]] + [h1["root"]] + h1["splits"]
                               + [e["txid"] for e in h1["emissions"]] + h1.get("gap_txids", [])))
    res = [audit_tx(api, t, out) for t in chain]
    roles = {h1["root"]: "root", **{t: "split" for t in h1["splits"]}, **{e["txid"]: "emission" for e in h1["emissions"]},
             **{t: "spend in the tree, raw not read" for t in h1.get("gap_txids", [])}}
    for r in res:
        r["role"] = roles.get(r["txid"], "parent of the root")
    ok = audit_ok(res)
    if ok is True and (h1.get("gap_txids") or h1["verdict"] == "UNDETERMINED"):
        ok = None                                           # the tree itself was not fully read
    tree_fees = [r["fee"] for r in res if r.get("role") in ("split", "emission")]
    root_fee = next((r["fee"] for r in res if r.get("role") == "root"), None)
    partial = bool(h1.get("gap_txids")) or None in tree_fees or h1["verdict"] == "UNDETERMINED"
    out.append(f"**Audited {len(res)} transactions ({sum(1 for r in res if r.get('role') == 'parent of the root')} parent(s) "
               f"of the root, the root, {len(h1['splits'])} splits, {len(h1['emissions'])} emissions"
               + (f", {len(h1['gap_txids'])} tree spend(s) whose raw was not read" if h1.get("gap_txids") else "")
               + f"): every input valid: {ok}; fees of the splits and emissions "
               + (f"{sum(f for f in tree_fees if f is not None)} sat (PARTIAL)" if partial else f"{sum(tree_fees)} sat")
               + f"; the root's own fee (paid by its funder) {root_fee} sat**\n")
    return {"ok": ok, "results": res, "h1": h1["verdict"], "diffs": h1["diffs"], "fuel_outputs": h1["fuel"],
            "fees_in_tree": None if partial else sum(tree_fees), "root_fee": root_fee, "gap_txids": h1.get("gap_txids", [])}

def audit_ok(results):
    """True only when something was audited and every input of every transaction is valid."""
    if any(r["ok"] is False for r in results):
        return False
    return None if not results or any(r["ok"] is None for r in results) else True

def audit_exit(results, h1=None):
    """Exit code of an audit run: 0 every input valid, 1 an input invalid, 6 something not checked."""
    v = audit_ok(results)
    if v is True and h1 is not None and h1.get("ok") is None:
        v = None
    return {False: 1, None: 6, True: 0}[v]

def resolve_txid(t):
    """A txid as given (any case, or a unique prefix of at least 8 hex digits) resolved against the raws on
    disk (materials/chain/fetched/) and the committed primaries."""
    t = t.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{8,64}", t):
        raise ValueError(f"not a txid or txid prefix: {t!r}")
    if len(t) == 64:
        return t
    known = {f[:-4] for f in (os.listdir(FETCHED) if os.path.isdir(FETCHED) else []) if f.endswith(".hex")}
    known |= {x["txid"] for x in RT.load_saved()}
    hits = sorted(k for k in known if k.startswith(t))
    if len(hits) != 1:
        raise ValueError(f"txid prefix {t} matches {len(hits)} raw(s) on hand; give the full txid")
    return hits[0]

def audit_stem(txids, h1):
    """Default output name: VERIFY_H1, VERIFY_<first 8 hex of each txid>, or both joined."""
    parts = [t[:8] for t in txids[:3]] + ([f"plus{len(txids) - 3}"] if len(txids) > 3 else []) + (["H1"] if h1 else [])
    return os.path.join(CHAIN, "VERIFY_" + "_".join(parts))

def save_audit(stem, lines, results, h1=None, meta=None):
    """Write the audit as <stem>.md (the report as printed) and <stem>.json (every structured record)."""
    os.makedirs(os.path.dirname(os.path.abspath(stem)), exist_ok=True)
    ok = audit_ok(results)
    head = [f"# Offline transaction audit, {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}\n",
            f"Every input valid: **{ok}**. Raws from the frozen cache or the repo's committed primaries; nothing fetched.\n"]
    if meta:
        head.append("Invariant: `" + json.dumps(meta, sort_keys=True) + "`\n")
    open(stem + ".md", "w").write("\n".join(head + lines) + "\n")
    json.dump({"all_inputs_valid": ok, "meta": meta or {}, "h1": h1, "transactions": results},
              open(stem + ".json", "w"), indent=1, sort_keys=True, default=str)
    return stem + ".md", stem + ".json"

# ---------- run ----------
def run(api, depth, max_fetch, max_pages=20, full=True):
    out = [f"# Receipt lookups (ticks 88–93), {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}\n",
           f"Source: `{api.base}`" + (" (offline fixture)" if api.fixture is not None else "") + "\n"]
    v = [lookup_2024(api, out), lookup_funder(api, out, depth, max_fetch), lookup_2021(api, out, max_pages)]
    extra = {}
    if full:
        fan = lookup_fanout(api, out, max_pages)
        prom = lookup_funders(api, out, fan, depth, max_fetch, max_pages)
        extra = {"h1": fan.get("h1"), "promotion": prom,
                 "fanout": {k: fan[k] for k in fan if k not in ("classes", "inbound_inputs", "h1")}}
    return tuple(v), "\n".join(out), extra

def _spk_of(a):
    """scriptPubKey of a base58 P2PKH / P2SH address (selftest fixtures only)."""
    n = 0
    for c in a:
        n = n * 58 + "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz".index(c)
    b = n.to_bytes(25, "big")
    return (b"\x76\xa9\x14" + b[1:21] + b"\x88\xac") if b[0] == 0 else (b"\xa9\x14" + b[1:21] + b"\x87")

def _raw(vins, vouts):
    """Hex of a synthetic version-2 tx: vins [(txid, vout, scriptSig, [witness items])], vouts [(sat, spk)]."""
    seg = any(w for *_, w in vins)
    b = (2).to_bytes(4, "little") + (b"\x00\x01" if seg else b"") + T.varint(len(vins))
    for txid, n, ss, w in vins:
        b += bytes.fromhex(txid)[::-1] + n.to_bytes(4, "little") + T.varstr(ss) + b"\xff\xff\xff\xff"
    b += T.varint(len(vouts)) + b"".join(sat.to_bytes(8, "little") + T.varstr(spk) for sat, spk in vouts)
    if seg:
        for *_, w in vins:
            b += T.varint(len(w)) + b"".join(T.varstr(x) for x in w)
    return (b + b"\x00" * 4).hex()

def synthetic_fanout(perturb=None, refill=False):
    """A stand-in 3GSMG24T history with the pre-registered 12 -> 12 shape: one outside funding, three
    self-splits, ten emissions (dummy signatures; H1 tests structure, not signatures). perturb='drop'
    leaves the last emission out, so one fuel output stays unspent; perturb='other' makes one emission
    pay a P2A anchor (a nonstandard output) instead of its receipt. refill=True adds a second funding by
    the same outside key, spent by an emission to a 2021 point (condition (iv)). Returns
    (fixture, history txids, root txid, funder address)."""
    pub = bytes.fromhex("0205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b")   # 3GSMG24T
    redeem = b"\x00\x14" + btc_addr.hash160(pub)
    me = b"\xa9\x14" + btc_addr.hash160(redeem) + b"\x87"
    dsig = bytes.fromhex("30" + "00" * 69 + "01")
    x, y = btc_addr.mul(0x5eed1234)                          # an arbitrary outside key
    fpub = bytes([2 + (y & 1)]) + x.to_bytes(32, "big")
    fx, hist = {}, []
    def add(hx):
        t = parse_raw(hx)["txid"]; fx[t] = hx; hist.append(t); return t
    def fund(parent, sat):
        return add(_raw([(parent, 0, T.varstr(dsig) + T.varstr(fpub), [])], [(sat, me)]))
    def spend(ins, outs, memo=b""):
        vins = [(t, n, bytes([len(redeem)]) + redeem, [dsig, pub]) for t, n in ins]
        return add(_raw(vins, ([(0, b"\x6a" + bytes([len(memo)]) + memo)] if memo else []) + outs))
    R = fund("ab" * 32, 15000)
    S1 = spend([(R, 0)], [(1189, me), (1189, me), (1180, me), (1180, me), (10000, me)])
    for i, a in enumerate(["1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ", "1M5ypvDbp124ZtKPbg3GJg1JqNs1x7TPoN",
                           "1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq", "1AD2wfwXukZ1kUAy848hTQQ72aSBZPB75r"]):
        spend([(S1, i)], [(1000, _spk_of(a))], b"GSMG.io: checkpoint")
    S2 = spend([(S1, 4)], [(7400, me), (1200, me), (1200, me)])
    spend([(S2, 1)], [(1000, _spk_of("18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc"))], b"GSMG.io: part of the cipher")
    spend([(S2, 2)], [(1000, _spk_of("1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff"))], b"GSMG.io: do you beleive")
    S3 = spend([(S2, 0)], [(1106, me)] + [(1200, me)] * 5)
    spend([(S3, 0), (S3, 1), (S3, 2)], [(700, _spk_of(RT.HALF))], b"Halving")
    spend([(S3, 3)], [(1050, _spk_of("1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9"))])
    spend([(S3, 4)], [(1000, bytes.fromhex("51024e73") if perturb == "other" else _spk_of("13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp"))],
          b"Good job, Neo!")
    last = spend([(S3, 5)], [(1000, _spk_of(SEEDKEY))], b"Good job, Neo!")
    if perturb == "drop":
        hist.remove(last); del fx[last]
    if refill:
        R2 = fund("cd" * 32, 5500)
        spend([(R2, 0)], [(5000, _spk_of(QMG))], b"GSMG.io neighbors, half and double")
    return fx, hist, R, btc_addr.p2pkh(fpub)

def _der_sig(d, z, hashtype=1):
    """Deterministic low-S ECDSA signature by test scalar d over z, DER plus hashtype (selftest fixtures only)."""
    k = int.from_bytes(T.sha(d.to_bytes(32, "big") + z.to_bytes(32, "big")), "big") % btc_addr.N or 1
    r = btc_addr.mul(k)[0] % btc_addr.N
    s_ = pow(k, -1, btc_addr.N) * (z + r * d) % btc_addr.N
    s_ = min(s_, btc_addr.N - s_)
    def enc(x):
        b = x.to_bytes(33, "big").lstrip(b"\x00")
        b = b"\x00" + b if b[0] & 0x80 else b
        return b"\x02" + bytes([len(b)]) + b
    body = enc(r) + enc(s_)
    return b"\x30" + bytes([len(body)]) + body + bytes([hashtype])

def audit_controls():
    """A parent paying a 2-of-2 P2SH-P2WSH and a child spending it with two real BIP143 signatures, audited from a
    fixture; then the signatures swapped, and the parent amount changed; the weight cross-checked against an
    independent serialization; and the saved 2024 split (one legacy input whose parent is saved)."""
    d1, d2 = 0x1f1f1f, 0x2e2e2e                           # test scalars; their addresses hold nothing
    p1, p2 = (bytes([2 + (y & 1)]) + x.to_bytes(32, "big") for x, y in (btc_addr.mul(d1), btc_addr.mul(d2)))
    ws = b"\x52\x21" + p1 + b"\x21" + p2 + b"\x52\xae"
    redeem = b"\x00\x20" + T.sha(ws)
    spk = b"\xa9\x14" + btc_addr.hash160(redeem) + b"\x87"
    pay = _spk_of(RT.HALF)
    def build(amount, order=(0, 1)):
        parent = _raw([("ab" * 32, 0, T.varstr(bytes.fromhex("30" + "00" * 69 + "01")) + T.varstr(p1), [])], [(amount, spk)])
        pt = parse_raw(parent)["txid"]
        blank = _raw([(pt, 0, T.varstr(redeem), [b"", b"\x30", b"\x30", ws])], [(60000, pay), (39000, spk)])
        z = T.sighash_bip143(parse_raw(blank), 0, ws, 100000, 1)
        sigs = [_der_sig(d1, z), _der_sig(d2, z)]
        child = _raw([(pt, 0, T.varstr(redeem), [b"", sigs[order[0]], sigs[order[1]], ws])], [(60000, pay), (39000, spk)])
        return {pt: parent, parse_raw(child)["txid"]: child}, parse_raw(child)["txid"], child
    fx, ct, child = build(100000)
    o = []
    good = audit_tx(Esplora("offline", fixture=fx), ct, o)
    text = "\n".join(o)
    w, stripped, size = tx_weight(child)
    nowit = parse_raw(child)
    alt = _raw([(v["txid"], v["vout"], bytes.fromhex(v["scriptSig"]), []) for v in nowit["vin"]],
               [(x["sat"], bytes.fromhex(x["spk"])) for x in nowit["vout"]])
    fx2, ct2, _ = build(100000, order=(1, 0))
    swapped = audit_tx(Esplora("offline", fixture=fx2), ct2, [])
    fx3, ct3, _ = build(100001)
    amount = audit_tx(Esplora("offline", fixture=fx3), ct3, [])
    o4 = []
    split = audit_tx(Esplora("offline", fixture={t["txid"]: t["raw"] for t in RT.load_saved()}), saved("88cdb3cd")["txid"], o4)
    t4 = "\n".join(o4)
    stem = os.path.join(tempfile.mkdtemp(), "VERIFY_test")
    md, js = save_audit(stem, o, [good])
    saved_json = json.load(open(js))
    checks = {
        "saved .md and .json": open(md).read().count("verifies under key") == 2 and saved_json["all_inputs_valid"] is True
                               and saved_json["transactions"][0]["inputs"][0]["signatures"][1]["key_index"] == 2
                               and saved_json["transactions"][0]["fee"] == 1000,
        "an empty audit is not 'valid'": audit_ok([]) is None,
        "valid, fee 1000": good["ok"] is True and good["fee"] == 1000,
        "key order shown": "verifies under key 1 of 2" in text and "verifies under key 2 of 2" in text and "SIGHASH_ALL" in text,
        "weight = 3*stripped + total": stripped == len(bytes.fromhex(alt)) and w == 3 * stripped + size,
        "swapped signatures invalid": swapped["ok"] is False,
        "wrong amount invalid": amount["ok"] is False,
        "2024 split: 1 valid input, 2 unchecked": t4.count("input VALID") == 1 and t4.count("parent raw not on hand") == 2
                                                  and split["ok"] is None,
    }
    return all(checks.values()), {k: v for k, v in checks.items() if not v} or "all hold"

def _raises(f):
    try:
        f()
    except Unavailable:
        return True
    return False

def selftest():
    ok = T.selftest()
    # fixture mode is hermetic: a valid raw and a JSON response planted in the on-disk caches must not be
    # read; the same planted raw IS read by a live-mode client (control; nothing is fetched)
    global FETCHED, JSONDIR
    keep, tmp = (FETCHED, JSONDIR), tempfile.mkdtemp()
    try:
        FETCHED, JSONDIR = tmp, os.path.join(tmp, "json")
        os.makedirs(JSONDIR)
        hal = saved("a798905f")
        open(os.path.join(FETCHED, hal["txid"] + ".hex"), "w").write(hal["raw"] + "\n")
        json.dump({"block_height": 630001}, open(os.path.join(JSONDIR, f"status_{hal['txid']}.json"), "w"))
        fxa = Esplora("offline", fixture={})
        herm = (_raises(lambda: fxa.tx_hex(hal["txid"])) and fxa.cached_hex(hal["txid"]) is None
                and _raises(lambda: fxa.get_json(f"/tx/{hal['txid']}/status", f"status_{hal['txid']}.json"))
                and Esplora("http://127.0.0.1:9", save=False).tx_hex(hal["txid"]) == hal["raw"])
    finally:
        FETCHED, JSONDIR = keep
    print("fixture hermeticity (planted disk cache ignored in fixture mode, read in live mode):", herm); ok &= herm
    rune = script_info(bytes.fromhex("6a5d0b00c0a2330380cab5ee0101"))[0] == "op_return"
    print("runestone OP_RETURN (OP_13) decodes:", rune); ok &= rune
    # H1 on synthetic histories: the pre-registered shape passes, two perturbations fail with the difference
    h1s = {}
    for pert in (None, "drop", "other"):
        fx, hist, root, _ = synthetic_fanout(pert)
        o = []
        h1s[pert] = lookup_fanout(Esplora("offline", fixture=fx, addr_fixture={RT.CREATOR: hist}), o, 1, h1_root=root)["h1"]
    exp_ok = all(a in expected_receipts() for a in H1_EXPECT) and sum(H1_EXPECT.values()) == 12 and len(H1_EXPECT) == 10
    c = (exp_ok and h1s[None]["verdict"] == "PASS" and h1s[None]["fuel"] == 12 and len(h1s[None]["emissions"]) == 10
         and h1s["drop"]["verdict"] == "FAIL" and any("unspent" in d for d in h1s["drop"]["diffs"])
         and h1s["other"]["verdict"] == "FAIL" and any("nonstandard:51024e73" in d for d in h1s["other"]["diffs"]))
    print("H1 12 -> 12 controls: PASS on the pre-registered shape; FAIL when an emission is missing "
          "(unspent fuel) or pays another recipient:", c, {k: (v["verdict"], v["diffs"][:2]) for k, v in h1s.items() if k})
    ok &= c
    # condition (iv): one outside key signs two spent fundings -> PROMOTE; without its history and with a
    # single funding, the rule cannot close it -> NOT DETERMINED
    fx, hist, root, funder = synthetic_fanout(refill=True)
    api = Esplora("offline", fixture=fx, addr_fixture={RT.CREATOR: hist, funder: [hist[0], hist[-2]]})
    o = []
    fan = lookup_fanout(api, o, 1, h1_root=root)
    v4 = lookup_funders(api, o, fan, depth=2, max_fetch=5, max_pages=1)
    fx, hist, root, funder = synthetic_fanout()
    api = Esplora("offline", fixture=fx, addr_fixture={RT.CREATOR: hist})
    o2 = []
    fan2 = lookup_fanout(api, o2, 1, h1_root=root)
    vu = lookup_funders(api, o2, fan2, depth=2, max_fetch=5, max_pages=1)
    c = (fan["h1"]["verdict"] == "PASS" and v4.get(funder, {}).get("promote") is True
         and v4[funder]["states"]["iv"] is True and len(v4[funder]["iv"]) == 2
         and vu.get(funder, {}).get("promote") is None and "NOT DETERMINED" in "\n".join(o2))
    print("promotion (iv) and NOT DETERMINED controls:", c,
          {"iv": v4.get(funder, {}).get("states"), "no history": vu.get(funder, {}).get("states")})
    ok &= c
    c, detail = audit_controls()
    print("offline audit controls (real-signature 2-of-2 P2SH-P2WSH spend, the 37mh shape; tampers; weight; "
          "saved 2024 split):", c, detail)
    ok &= c
    fixture = {t["txid"]: t["raw"] for t in RT.load_saved()}
    halving = describe(fixture[saved("a798905f")["txid"]])
    split = describe(fixture[saved("2aa9a4a9")["txid"]])
    c = (all(a == RT.CREATOR for _, a, _ in halving[1]) and halving[3] == ["Halving"]
         and all(a == RT.HALF for _, a, _ in split[1])
         and any(a == RT.BETTER and sat == 250_000_000 for _, sat, _, a, _ in split[2]))
    print("decode controls (Halving memo tx, 2020 split):", c); ok &= c
    try:
        Esplora("x", fixture={}).tx_hex(saved("2aa9a4a9")["txid"]); ok = False
    except Unavailable:
        pass
    bad = dict(fixture); tid = saved("2aa9a4a9")["txid"]; bad[tid] = fixture[saved("a798905f")["txid"]]
    try:
        Esplora("x", fixture=bad).tx_hex(tid); ok = False; print("integrity check: FAILED to reject")
    except Unavailable:
        print("integrity check rejects hex that does not hash to its txid: True")
    verdicts, text, _ = run(Esplora("offline", fixture=fixture), depth=3, max_fetch=5, full=False)
    want = ("unavailable", "unavailable", "unavailable")
    print("fixture isolation control:", verdicts == want, "got:", verdicts)
    ok &= verdicts == want
    # positive controls on saved data: each lookup's success path must recover a known fact
    creator_txs = [t["txid"] for t in RT.load_saved() if t["txid"][:8] in ("a798905f", "364de511", "722fbf35", "8aaa96d3")]
    api = Esplora("offline", fixture=fixture, addr_fixture={QMG: [saved("a798905f")["txid"]], RT.CREATOR: creator_txs})
    out = []
    pc1 = lookup_2024(api, out, split_prefix="2aa9a4a9", skip_prefix=None)      # the 2020 "Halving" parent
    pc2 = lookup_funder(api, out, depth=3, max_fetch=10, start=saved("88cdb3cd")["txid"])
    pc3 = lookup_2021(api, out)          # stand-in: QMG mapped to the 3GSMG24T-signed Halving tx
    fan = lookup_fanout(api, out, 1)     # stand-in history: the four saved txs touching 3GSMG24T
    text4 = "\n".join(out)
    pc4 = ("[emit]" in text4 and "Halving" in text4 and not fan["unknown_recipients"]
           and "Inbound deposits never spent by the address" in text4 and SEEDKEY in text4
           and "sigs verified 1/3 (2 unchecked" in text4)      # the 2020 split's legacy input over a saved parent
    print(text4)
    print("positive controls:", pc1, "|", pc2, "|", pc3, "| fan-out:", pc4)
    ok &= pc1 == "YES" and pc2.startswith("YES") and "prize" in pc2 and pc3 == "YES" and pc4
    # promotion (ii) positive control: the prize key must be recognised as known
    kx = known_keys()
    pk = RT.signer(saved("2aa9a4a9")["vin"][0])[2]
    pc5 = kx.get(pk[1:33].hex()) == "prize key" and "0205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b"[2:] in kx
    print("known-key control (prize key and 3GSMG24T key recognised):", pc5); ok &= pc5
    print("selftest passed:", ok)
    return ok

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="https://mempool.space/api")
    ap.add_argument("--depth", type=int, default=12)
    ap.add_argument("--max-fetch", type=int, default=200)
    ap.add_argument("--max-pages", type=int, default=20, help="address-history pages of 25 transactions")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify", nargs="+", metavar="TXID", help="audit these transactions offline from raws on disk")
    ap.add_argument("--verify-h1", action="store_true", help="audit the whole H1 tree offline from raws and history on disk")
    ap.add_argument("--out", help="output path stem for the audit (.md and .json); default materials/chain/VERIFY_…")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    if a.verify or a.verify_h1:
        api, out = DiskOnly(a.base), []
        a.verify = [resolve_txid(t) for t in a.verify or []]
        res = [audit_tx(api, t, out) for t in a.verify]
        h1 = audit_h1(api, out, a.max_pages) if a.verify_h1 else None
        if h1:
            res += h1["results"]
        print("\n".join(out))
        for f in save_audit(a.out or audit_stem(a.verify or [], a.verify_h1), out, res,
                            h1 and {k: v for k, v in h1.items() if k != "results"},
                            {"mode": "disk-only", "network_requests": api.fetches}):
            print("written:", f)
        return audit_exit(res, h1)
    api = Esplora(a.base)
    verdicts, text, extra = run(api, a.depth, a.max_fetch, a.max_pages)
    print(text)
    open(os.path.join(CHAIN, "RECEIPT_LOOKUPS.md"), "w").write(text + "\n")
    json.dump({"verdicts": verdicts, **extra, "requests": api.fetches}, open(os.path.join(CHAIN, "receipt_lookups.json"), "w"),
              indent=1, default=str)
    print(f"written: materials/chain/RECEIPT_LOOKUPS.md and receipt_lookups.json; raw txs in materials/chain/fetched/ "
          f"({api.fetches} network requests)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
