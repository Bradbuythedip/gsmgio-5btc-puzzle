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
     output's parent is available (BIP143 needs its amount).
  5. The full history of each wallet that funded 3GSMG24T (e.g. the 2-of-2 multisig 37mh7EYet…):
     transaction count, first/last block and date, flows, and which transactions touch a
     GSMG-labelled address.
  6. The promotion rule for each such funder, fixed before the run:
       PROMOTE only if (i) its ancestry reaches a creator-trail signer (1EtbTv…, the prize key,
       1GSMG1CLx…, 17ucy1…) within the walk bounds; or (ii) one of its public keys, by
       x-coordinate, equals a key in authenticated GSMG material, or its hex appears in the repo's
       materials or ledger; or (iii) its full history is narrowly GSMG-specific: at most 10
       transactions, at least half of which pay or spend a GSMG-labelled address.
     Otherwise it is operational funding infrastructure and the branch closes. Addresses, keys,
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
import argparse, json, os, re, sys, time, urllib.error, urllib.request
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
            except (urllib.error.URLError, OSError) as e:
                last = e; time.sleep(2 ** attempt)
        raise Unavailable(f"{self.base}{path}: {last}")

    def get_json(self, path, cache_name=None):
        cached = os.path.join(JSONDIR, cache_name) if cache_name else None
        if cached and os.path.exists(cached):
            return json.load(open(cached))
        data = json.loads(self._get(path))
        if cached and self.save:
            os.makedirs(JSONDIR, exist_ok=True)
            json.dump(data, open(cached, "w"))
        return data

    def cached_hex(self, txid):
        """Hex only if already on hand (fixture or disk cache); never fetches."""
        if self.fixture is not None:
            return self.fixture.get(txid)
        p = os.path.join(FETCHED, txid + ".hex")
        return open(p).read().strip() if os.path.exists(p) else None

    def tx_hex(self, txid):
        cached = os.path.join(FETCHED, txid + ".hex")
        if self.fixture is not None and txid in self.fixture:
            hx = self.fixture[txid]
        elif os.path.exists(cached):
            hx = open(cached).read().strip()
        else:
            hx = self._get(f"/tx/{txid}/hex").decode().strip()
        if parse_raw(hx)["txid"] != txid:
            raise Unavailable(f"{txid}: returned hex does not hash to the txid")
        if self.save and self.fixture is None and not os.path.exists(cached):
            os.makedirs(FETCHED, exist_ok=True)
            open(cached, "w").write(hx + "\n")
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
        return [t["txid"] for t in json.loads(self._get(f"/address/{addr}/txs"))]

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
        first = json.loads(self._get(f"/address/{addr}/txs"))
        items = list(first)
        confirmed = [t for t in first if t.get("status", {}).get("confirmed")]
        complete, pages = len(confirmed) < 25, 1
        last = confirmed[-1]["txid"] if confirmed else None
        while not complete and pages < max_pages:
            nxt = json.loads(self._get(f"/address/{addr}/txs/chain/{last}"))
            pages += 1; items += nxt
            complete = len(nxt) < 25
            if nxt:
                last = nxt[-1]["txid"]
        os.makedirs(JSONDIR, exist_ok=True)
        json.dump({"address": addr, "complete": complete, "pages": pages, "txs": items},
                  open(os.path.join(JSONDIR, f"history_{addr}.json"), "w"))
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

def describe(hx):
    tx = parse_raw(hx)
    scripts = [T.input_script(v) for v in tx["vin"]]
    signers = [(d["kind"], d["address"], d["pubkeys"][0] if len(d["pubkeys"]) == 1 else None) for d in scripts]
    outs = [(o["n"], o["sat"]) + script_info(bytes.fromhex(o["spk"])) for o in tx["vout"]]
    memos = [d.decode("latin1") for _, _, kind, _, d in outs if kind == "op_return"]
    return tx, signers, outs, memos, scripts

def who(scripts):
    parts = []
    for d in scripts:
        s = f"{label(d['address'])} ({d['kind']})"
        if d["m"] and len(d["pubkeys"]) > 1:
            s += " keys " + ", ".join(p.hex() for p in d["pubkeys"])
        if not d["ok"]:
            s += " [COMMITMENT MISMATCH]"
        parts.append(s)
    return sorted(set(parts))

def verify_tx(api, tx):
    """Per-input offline signature check using parents already on hand; returns (ok, bad, unchecked)."""
    ok = bad = unchecked = 0
    for i, v in enumerate(tx["vin"]):
        phx = api.cached_hex(v["txid"]) if v["txid"] != COINBASE else None
        if phx is None:
            unchecked += 1; continue
        o = parse_raw(phx)["vout"][v["vout"]]
        r = T.verify_input(tx, i, bytes.fromhex(o["spk"]), o["sat"])
        if r["ok"] is True: ok += 1
        elif r["ok"] is False: bad += 1
        else: unchecked += 1
    return ok, bad, unchecked

def sigtag(api, tx):
    ok, bad, un = verify_tx(api, tx)
    n = len(tx["vin"])
    if bad:
        return f"SIGNATURE FAILS on {bad}/{n}"
    return f"sigs verified {ok}/{n}" + (f" ({un} unchecked: parent not fetched)" if un else "")

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
            tx, signers, outs, memos, scripts = describe(api.tx_hex(v["txid"]))
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
    """Backward BFS over every input. Returns (records, fetched, missing); a record is
    (depth, txid, scripts, memos, height, time, tx)."""
    frontier, seen, recs, fetched, missing = [(s, 0) for s in starts], set(), [], 0, []
    while frontier and fetched < max_fetch:
        txid, d = frontier.pop(0)
        if txid in seen or txid == COINBASE:
            continue
        seen.add(txid)
        try:
            tx, signers, _, memos, scripts = describe(api.tx_hex(txid)); fetched += 1
        except Unavailable as e:
            missing.append((d, txid, str(e))); continue
        h, t = api.tx_status(txid)
        recs.append((d, txid, scripts, memos, h, t, tx))
        if any(sc["address"] in CREATOR_TRAIL for sc in scripts):
            continue                                        # reached the trail on this branch
        if d + 1 < depth:
            frontier += [(v["txid"], d + 1) for v in tx["vin"]]
    return recs, fetched, missing

def lookup_funder(api, out, depth, max_fetch, start=None):
    default = saved("a798905f")["vin"][0]["txid"]          # 547246e9…, which funded 3GSMG24T
    start = start or default
    out.append(f"## 2. Who funded 3GSMG24T (walk up from `{start}`, depth ≤ {depth}, ≤ {max_fetch} fetches)\n")
    recs, fetched, missing = ancestry(api, [start], depth, max_fetch)
    for d, txid, scripts, memos, h, t, tx in recs:
        out.append(f"- depth {d} `{txid}` (height {h or '?'}, {when(t)}): inputs signed by {', '.join(who(scripts))}"
                   + (f"; memo {memos}" if memos else "") + f"; {sigtag(api, tx)}")
    for d, txid, e in missing:
        out.append(f"- depth {d} `{txid}`: unavailable ({e})")
    hits = [(d, txid, sc["address"]) for d, txid, scripts, *_ in recs for sc in scripts if sc["address"] in CREATOR_TRAIL]
    if hits:
        d, txid, a = min(hits)
        verdict = f"YES: {label(a)} signs at depth {d} (`{txid}`)"
    else:
        verdict = "unavailable" if fetched == 0 else f"NO within depth {depth} ({fetched} transactions read)"
    what = "3GSMG24T traces to the creator trail" if start == default else "the walk reaches the creator trail"
    out.append(f"\n**{what}: {verdict}**\n")
    return verdict

# ---------- 3. the 2021 memo ----------
def lookup_2021(api, out):
    creator_pub = RT.signer(saved("a798905f")["vin"][0])[2].hex()   # 3GSMG24T's witness pubkey
    out.append(f"## 3. The 2021 \"neighbors, half and double\" transaction (via `{QMG}`)\n")
    try:
        txids = api.address_txids(QMG)
    except Unavailable as e:
        out.append(f"- unavailable ({e})\n\n**Signed by 3GSMG24T's key: unavailable**\n")
        return "unavailable"
    verdict = "NO"
    for txid in txids:
        tx, signers, outs, memos, scripts = describe(api.tx_hex(txid))
        keys = sorted({(label(a), p.hex() if p else None) for _, a, p in signers})
        ok = all(a == RT.CREATOR and p is not None and p.hex() == creator_pub for _, a, p in signers)
        verdict = "YES" if ok else verdict
        out.append(f"- `{txid}`: signers {keys}; memo {memos}; {sigtag(api, tx)}; outputs "
                   + ", ".join(f"{sat} → {label(a)}" for _, sat, kind, a, _ in outs if kind != "op_return"))
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

def lookup_fanout(api, out, max_pages, addr=RT.CREATOR):
    out.append(f"## 4. The complete {label(addr)} fan-out (from its full address history)\n")
    try:
        hist, complete = api.address_history(addr, max_pages)
    except Unavailable as e:
        out.append(f"- unavailable ({e})\n\n**Fan-out: unavailable**\n")
        return {"verdict": "unavailable", "funders": []}
    meta = {h["txid"]: h for h in hist}
    txs, missing = {}, []
    for h in hist:
        try:
            txs[h["txid"]] = describe(api.tx_hex(h["txid"]))
        except Unavailable as e:
            missing.append((h["txid"], str(e)))
    def hstat(txid):
        st = (meta.get(txid) or {}).get("status") or {}
        return st.get("block_height"), st.get("block_time")
    mine = {}                                               # (txid, n) -> sat, outputs paying addr
    spent_by = {}                                           # (txid, n) -> spending txid
    cls, inbound = {}, []
    for txid, (tx, signers, outs, memos, scripts) in txs.items():
        for n, sat, kind, a, _ in outs:
            if a == addr:
                mine[(txid, n)] = sat
    for txid, (tx, signers, outs, memos, scripts) in txs.items():
        from_me = [sc["address"] == addr for sc in scripts]
        for v in tx["vin"]:
            spent_by[(v["txid"], v["vout"])] = txid
        to_other = [(n, sat, a) for n, sat, kind, a, _ in outs if kind != "op_return" and a != addr]
        if not any(from_me):
            cls[txid] = "inbound"; inbound.append(txid)
        elif all(from_me) and not to_other:
            cls[txid] = "split"
        elif all(from_me):
            cls[txid] = "emit"
        else:
            cls[txid] = "mixed"
    order = sorted(txs, key=lambda t: (hstat(t)[0] or 10**9, t))
    # tree
    printed = set()
    def node(outpoint, indent):
        sat = mine.get(outpoint)
        sp = spent_by.get(outpoint)
        head = f"{'  ' * indent}- `{outpoint[0][:12]}…:{outpoint[1]}` {sat} sat"
        if sp is None:
            out.append(head + (" → **UNSPENT** (remaining fuel)" if complete else " → not spent within the fetched history"))
            return
        if sp in printed:
            out.append(head + f" → spent by `{sp[:12]}…` (shown above)")
            return
        printed.add(sp)
        tx, signers, outs, memos, scripts = txs[sp]
        h, t = hstat(sp)
        out.append(head + f" → spent by `{sp}` [{cls[sp]}] (height {h or '?'}, {when(t)}; {sigtag(api, tx)})"
                   + (f" memo {memos}" if memos else ""))
        for n, s2, kind, a, _ in outs:
            if kind == "op_return":
                continue
            if a == addr:
                node((sp, n), indent + 1)
            else:
                out.append(f"{'  ' * (indent + 1)}- out {n}: {s2} sat → {label(a)}")
    out.append("**Inbound funding** (transactions not signed by the address that pay it):\n")
    for txid in sorted(inbound, key=lambda t: (hstat(t)[0] or 10**9, t)):
        tx, signers, outs, memos, scripts = txs[txid]
        h, t = hstat(txid)
        paid = [(n, s) for n, s, k, a, _ in outs if a == addr]
        out.append(f"- `{txid}` (height {h or '?'}, {when(t)}) signed by {', '.join(who(scripts))}; {sigtag(api, tx)}; "
                   f"pays {', '.join(f'out {n}: {s} sat' for n, s in paid)}" + (f"; memo {memos}" if memos else ""))
    out.append("\n**UTXO tree** (each output paid to the address, followed to whatever spends it):\n")
    for txid in sorted(inbound, key=lambda t: (hstat(t)[0] or 10**9, t)):
        for n, s, k, a, _ in txs[txid][2]:
            if a == addr:
                node((txid, n), 0)
    orphans = [t for t in order if cls[t] != "inbound" and t not in printed]
    if orphans:
        out.append("\nSpends whose funding lies outside the fetched history:")
        for t in orphans:
            tx, signers, outs, memos, scripts = txs[t]
            h, tt = hstat(t)
            out.append(f"- `{t}` [{cls[t]}] (height {h or '?'}, {when(tt)}; {sigtag(api, tx)}) memo {memos or 'none'}; "
                       + ", ".join(f"out {n}: {s} → {label(a)}" for n, s, k, a, _ in outs if k != "op_return"))
    # census
    seen = {}
    for t in order:
        if cls[t] in ("emit", "mixed"):
            tx, signers, outs, memos, scripts = txs[t]
            for n, s, k, a, _ in outs:
                if k != "op_return" and a != addr:
                    seen.setdefault(a, []).append((t, s, memos))
    exp = expected_receipts()
    lab = labels()
    out.append("\n**Recipient census** (every non-self output of the address's own transactions):\n")
    for a, rows in sorted(seen.items(), key=lambda kv: kv[0]):
        tag = "expected" if a in exp else ("GSMG-labelled" if a in lab else "**UNKNOWN: a creator receipt not in the ledger**")
        out.append(f"- {label(a)}: " + "; ".join(f"{s} sat in `{t[:12]}…` memo {m or 'none'}" for t, s, m in rows) + f" — {tag}")
    missing_exp = [f"{a} [{l}]" for a, l in exp.items() if a not in seen]
    out.append(f"\nExpected but not seen: {', '.join(missing_exp) or 'none'}")
    unknown = [a for a in seen if a not in exp and a not in lab]
    # accounting: fees only where every input amount is known from a fetched parent
    tin = sum(s for (t, n), s in mine.items() if cls.get(t) == "inbound")
    emitted = sum(s for rows in seen.values() for _, s, _ in rows)
    unspent = sum(s for op, s in mine.items() if op not in spent_by)
    fees, unknown_in = 0, 0
    for t in txs:
        if cls[t] == "inbound":
            continue
        tx = txs[t][0]
        vals = []
        for v in tx["vin"]:
            phx = api.cached_hex(v["txid"])
            vals.append(parse_raw(phx)["vout"][v["vout"]]["sat"] if phx else None)
        if None in vals:
            unknown_in += 1
        else:
            fees += sum(vals) - sum(o["sat"] for o in tx["vout"])
    balanced = unknown_in == 0 and complete and tin == emitted + unspent + fees
    out.append(f"\n**Fuel accounting:** inbound {tin} sat; emitted to others {emitted} sat; unspent at the address "
               f"{unspent} sat; fees {fees} sat over the {len(txs) - len(inbound) - unknown_in} spend(s) with every input "
               f"amount known" + (f"; {unknown_in} spend(s) have an input outside the fetched history" if unknown_in else "")
               + f"; books balance: {balanced}" + ("" if complete else " (history incomplete: raise --max-pages)"))
    if missing:
        out.append("\nUnavailable transactions: " + ", ".join(f"`{t}` ({e})" for t, e in missing))
    used = {t for (t, n) in mine if (t, n) in spent_by}   # inbound txs whose deposit the address went on to spend
    funders = sorted({sc["address"] for t in inbound if t in used for sc in txs[t][4] if sc["address"]})
    idle = sorted({sc["address"] for t in inbound if t not in used for sc in txs[t][4] if sc["address"]})
    if idle:
        out.append(f"\nInbound deposits never spent by the address (not funding; not evaluated): "
                   + ", ".join(label(a) for a in idle))
    verdict = f"{len(txs)} transactions; {len(inbound)} inbound; {sum(1 for c in cls.values() if c == 'emit')} emissions; " \
              f"{len(unknown)} unknown recipients" + ("" if complete else "; history INCOMPLETE")
    out.append(f"\n**Fan-out: {verdict}**\n")
    return {"verdict": verdict, "funders": funders, "unknown_recipients": unknown, "complete": complete,
            "inbound": inbound, "classes": cls}

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
            if os.sep + "chain" + os.sep in p:                  # our own chain notes and fetched raws
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
    results = {}
    lab = labels()
    for f in funders[:5]:
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
    out.append("PROMOTE only if (i) its ancestry reaches a creator-trail signer (1EtbTv…, the prize key, 1GSMG1CLx…, "
               "17ucy1…); or (ii) one of its public keys, by x-coordinate, equals a key in authenticated GSMG material or "
               "its hex appears in the repo's materials/ledger; or (iii) its full history is narrowly GSMG-specific: at most "
               f"{RULE_III[0]} transactions, at least {int(RULE_III[1] * 100)}% touching a GSMG-labelled address. Otherwise: "
               "operational funding infrastructure; close. Nothing here becomes an AES candidate.\n")
    kx = known_keys()
    verdicts = {}
    for f, r in results.items():
        # the funder's keys and the inbound transactions it signed, from the fan-out
        fkeys, starts = set(), []
        for t in fan.get("inbound", []):
            tx = parse_raw(api.cached_hex(t)) if api.cached_hex(t) else None
            if tx is None:
                continue
            for v in tx["vin"]:
                d = T.input_script(v)
                if d["address"] == f:
                    fkeys.update(p.hex() for p in d["pubkeys"]); starts.append(v["txid"])
        recs, fetched, missing = ancestry(api, starts, depth, max_fetch) if starts else ([], 0, [])
        c1 = [(d, txid, sc["address"]) for d, txid, scripts, *_ in recs for sc in scripts if sc["address"] in CREATOR_TRAIL]
        c2 = [(k[:16], kx[k[2:66]]) for k in fkeys if k[2:66] in kx]
        c2 += [(f"{p} mentions {h}…", "repo text") for p, h in repo_mentions([k for k in fkeys] + [k[2:66] for k in fkeys])]
        c3 = r.get("n_tx") is not None and r.get("complete") and r["n_tx"] <= RULE_III[0] and \
             r["touch"] >= RULE_III[1] * r["n_tx"]
        promote = bool(c1 or c2 or c3)
        verdicts[f] = {"promote": promote, "i": c1[:3], "ii": c2, "iii": bool(c3), "keys": sorted(fkeys),
                       "ancestry_read": fetched, "ancestry_depth": depth}
        out.append(f"- **{f}**: keys {', '.join(k[:16] + '…' for k in sorted(fkeys)) or '?'}")
        out.append(f"  - (i) ancestry ({fetched} txs read, depth ≤ {depth}): "
                   + (f"reaches {label(c1[0][2])} at depth {c1[0][0]}" if c1 else "no creator-trail signer"))
        out.append(f"  - (ii) key reuse: " + ("; ".join(f"{a} = {b}" for a, b in c2) if c2 else "none"))
        out.append(f"  - (iii) history: {r.get('n_tx', '?')} txs, {r.get('touch', '?')} GSMG-touching, "
                   f"{'complete' if r.get('complete') else 'incomplete'} → {'narrowly GSMG-specific' if c3 else 'not narrowly GSMG-specific'}")
        out.append(f"  - **{'PROMOTE' if promote else 'operational funding infrastructure: close'}**")
    return verdicts

# ---------- run ----------
def run(api, depth, max_fetch, max_pages=20, full=True):
    out = [f"# Receipt lookups (ticks 88–92), {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}\n",
           f"Source: `{api.base}`" + (" (offline fixture)" if api.fixture is not None else "") + "\n"]
    v = [lookup_2024(api, out), lookup_funder(api, out, depth, max_fetch), lookup_2021(api, out)]
    extra = {}
    if full:
        fan = lookup_fanout(api, out, max_pages)
        prom = lookup_funders(api, out, fan, depth, max_fetch, max_pages)
        extra = {"fanout": {k: fan[k] for k in fan if k != "classes"}, "promotion": prom}
    return tuple(v), "\n".join(out), extra

def selftest():
    ok = T.selftest()
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
    ok &= verdicts == ("unavailable", "unavailable", "unavailable")
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
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
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
