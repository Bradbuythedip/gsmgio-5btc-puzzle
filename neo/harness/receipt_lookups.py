#!/usr/bin/env python3
"""The three topology-only chain lookups left open by tick 88 (the receipt model), in one command.

  1. The 2024 split (88cdb3cd…, locktime 840003) spent two inputs besides the 2020 change. Who
     signed their parent transactions, and does either parent carry an OP_RETURN? A 3GSMG24T-signed
     parent with a memo means 2024 repeated the 2020 pattern: a signed instruction consumed by the
     prize key's split.
  2. 3GSMG24T's funder 547246e9…: walking up its inputs, does the trail reach 1EtbTv… (the 2019
     prize funder)? That would tie the whole creator graph to one origin.
  3. The 2021 "neighbors, half and double" transaction, found as the only transaction of the Q−G
     address: is it signed by 3GSMG24T's key?

Read-only, no keys, no values used as passwords. Needs an Esplora API (mempool.space by default).
This cloud environment's network policy blocks it, so run it on an unblocked machine (as with
trace_address.py) or after allowing mempool.space for the environment. Every fetched raw tx is
checked against its txid and saved under materials/chain/fetched/ so it can be committed as a
primary; the summary is written to materials/chain/RECEIPT_LOOKUPS.md.

  python3 receipt_lookups.py                                  # mempool.space
  python3 receipt_lookups.py --base https://blockstream.info/api
  python3 receipt_lookups.py --selftest                       # offline, saved hex only
"""
import argparse, json, os, sys, time, urllib.error, urllib.request
import receipt_topology as RT
from chain_flows import parse_raw, script_info

CHAIN = os.path.join(RT.NEO, "materials", "chain")
FETCHED = os.path.join(CHAIN, "fetched")
FUNDER = "1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1"
QMG = "1G1kRAFR68y6CUq1SAJMzHmjd6sEEgtVUT"          # Q−G; its only tx is the 2021 memo (tick 53)
TRAIL = {RT.HALF: "prize (half)", RT.BETTER: "better half", RT.CREATOR: "3GSMG24T", FUNDER: "2019 funder 1EtbTv",
         "1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3": "vanity 1GSMG1CLx"}
COINBASE = "00" * 32

class Unavailable(Exception):
    pass

class Esplora:
    """GET-only Esplora client with an on-disk cache. `fixture` (txid -> hex) replaces the network."""
    def __init__(self, base, fixture=None, save=True, addr_fixture=None):
        self.base, self.fixture, self.save, self.fetches = base.rstrip("/"), fixture, save, 0
        self.addr_fixture = addr_fixture

    def _get(self, path):
        if self.fixture is not None:
            raise Unavailable(f"offline: {path}")
        last = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(self.base + path, timeout=45) as r:
                    return r.read()
            except (urllib.error.URLError, OSError) as e:
                last = e; time.sleep(2 ** attempt)
        raise Unavailable(f"{self.base}{path}: {last}")

    def tx_hex(self, txid):
        cached = os.path.join(FETCHED, txid + ".hex")
        if self.fixture is not None and txid in self.fixture:
            hx = self.fixture[txid]
        elif os.path.exists(cached):
            hx = open(cached).read().strip()
        else:
            hx = self._get(f"/tx/{txid}/hex").decode().strip()
            self.fetches += 1
        if parse_raw(hx)["txid"] != txid:
            raise Unavailable(f"{txid}: returned hex does not hash to the txid")
        if self.save and self.fixture is None and not os.path.exists(cached):
            os.makedirs(FETCHED, exist_ok=True)
            open(cached, "w").write(hx + "\n")
        return hx

    def address_txids(self, addr):
        if self.addr_fixture is not None and addr in self.addr_fixture:
            return self.addr_fixture[addr]
        return [t["txid"] for t in json.loads(self._get(f"/address/{addr}/txs"))]

def label(a):
    return f"{a} [{TRAIL[a]}]" if a in TRAIL else str(a)

def describe(hx):
    tx = parse_raw(hx)
    signers = [RT.signer(v) for v in tx["vin"]]
    outs = [(o["n"], o["sat"]) + script_info(bytes.fromhex(o["spk"])) for o in tx["vout"]]
    memos = [d.decode("latin1") for _, _, kind, _, d in outs if kind == "op_return"]
    return tx, signers, outs, memos

def saved(prefix):
    return next(t for t in RT.load_saved() if t["txid"].startswith(prefix))

def lookup_2024(api, out, split_prefix="88cdb3cd", skip_prefix="2aa9a4a9"):
    split = saved(split_prefix)
    parents = [v for v in split["vin"] if not (skip_prefix and v["txid"].startswith(skip_prefix))]
    out.append(f"## 1. The parents of the `{split_prefix}…` split's inputs"
               + (f" (other than the `{skip_prefix}…` change)" if skip_prefix else "") + "\n")
    repeats, missing = False, 0
    for v in parents:
        try:
            tx, signers, outs, memos = describe(api.tx_hex(v["txid"]))
        except Unavailable as e:
            missing += 1; out.append(f"- `{v['txid']}:{v['vout']}`: unavailable ({e})"); continue
        who = sorted({label(a) for _, a, _ in signers})
        n, sat, kind, a, _ = outs[v["vout"]]
        creator = any(a in (RT.CREATOR, FUNDER, RT.HALF) for _, a, _ in signers)
        repeats |= creator and bool(memos)
        out.append(f"- `{v['txid']}:{v['vout']}` ({sat} sat → {label(a)}): parent signed by {', '.join(who)}; "
                   f"memo {memos or 'none'}; creator-signed: {creator}")
    verdict = "unavailable" if missing == len(parents) else ("YES" if repeats else "NO" + (" (partial)" if missing else ""))
    what = "2024 repeats the 2020 memo→split pattern" if split_prefix == "88cdb3cd" else "a creator-signed parent carries a memo"
    out.append(f"\n**{what}: {verdict}**\n")
    return verdict

def lookup_funder(api, out, depth, max_fetch, start=None):
    default = saved("a798905f")["vin"][0]["txid"]          # 547246e9…, which funded 3GSMG24T
    start = start or default
    out.append(f"## 2. Who funded 3GSMG24T (walk up from `{start}`, depth ≤ {depth})\n")
    frontier, seen, hits, fetched, missing = [(start, 0)], set(), [], 0, 0
    while frontier and fetched < max_fetch:
        txid, d = frontier.pop(0)
        if txid in seen or txid == COINBASE:
            continue
        seen.add(txid)
        try:
            tx, signers, _, memos = describe(api.tx_hex(txid)); fetched += 1
        except Unavailable as e:
            missing += 1; out.append(f"- depth {d} `{txid}`: unavailable ({e})"); continue
        who = sorted({f"{label(a)} ({k})" for k, a, _ in signers})
        out.append(f"- depth {d} `{txid}`: inputs signed by {', '.join(who)}" + (f"; memo {memos}" if memos else ""))
        hits += [(d, txid, a) for _, a, _ in signers if a in TRAIL and a != RT.CREATOR]
        if d + 1 < depth:
            frontier += [(v["txid"], d + 1) for v in tx["vin"]]
    if hits:
        d, txid, a = min(hits)
        verdict = f"YES: {label(a)} signs at depth {d} (`{txid}`)"
    else:
        verdict = "unavailable" if fetched == 0 else f"NO within depth {depth} ({fetched} transactions read)"
    what = "3GSMG24T traces to the creator trail" if start == default else "the walk reaches the creator trail"
    out.append(f"\n**{what}: {verdict}**\n")
    return verdict

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
        tx, signers, outs, memos = describe(api.tx_hex(txid))
        keys = sorted({(label(a), p.hex() if p else None) for _, a, p in signers})
        ok = all(a == RT.CREATOR and p is not None and p.hex() == creator_pub for _, a, p in signers)
        verdict = "YES" if ok else verdict
        out.append(f"- `{txid}`: signers {keys}; memo {memos}; outputs "
                   + ", ".join(f"{sat} → {label(a)}" for _, sat, kind, a, _ in outs if kind != "op_return"))
    out.append(f"\n**Signed by 3GSMG24T's key `{creator_pub[:16]}…`: {verdict}** ({len(txids)} tx at Q−G)\n")
    return verdict

def run(api, depth, max_fetch):
    out = [f"# Receipt lookups (tick 88 follow-up), {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}\n",
           f"Source: `{api.base}`" + (" (offline fixture)" if api.fixture is not None else "") + "\n"]
    v = (lookup_2024(api, out), lookup_funder(api, out, depth, max_fetch), lookup_2021(api, out))
    return v, "\n".join(out)

def selftest():
    fixture = {t["txid"]: t["raw"] for t in RT.load_saved()}
    halving = describe(fixture[saved("a798905f")["txid"]])
    split = describe(fixture[saved("2aa9a4a9")["txid"]])
    ok = (all(a == RT.CREATOR for _, a, _ in halving[1]) and halving[3] == ["Halving"]
          and all(a == RT.HALF for _, a, _ in split[1])
          and any(a == RT.BETTER and sat == 250_000_000 for _, sat, _, a, _ in split[2]))
    print("decode controls (Halving memo tx, 2020 split):", ok)
    try:
        Esplora("x", fixture={}).tx_hex(saved("2aa9a4a9")["txid"])
        ok = False
    except Unavailable:
        pass
    bad = dict(fixture); tid = saved("2aa9a4a9")["txid"]; bad[tid] = fixture[saved("a798905f")["txid"]]
    try:
        Esplora("x", fixture=bad).tx_hex(tid); ok = False; print("integrity check: FAILED to reject")
    except Unavailable:
        print("integrity check rejects hex that does not hash to its txid: True")
    verdicts, text = run(Esplora("offline", fixture=fixture), depth=3, max_fetch=5)
    print(text)
    ok &= verdicts == ("unavailable", "unavailable", "unavailable")
    # positive controls on saved data: each lookup's success path must recover a known fact
    api, out = Esplora("offline", fixture=fixture, addr_fixture={QMG: [saved("a798905f")["txid"]]}), []
    pc1 = lookup_2024(api, out, split_prefix="2aa9a4a9", skip_prefix=None)      # the 2020 "Halving" parent
    pc2 = lookup_funder(api, out, depth=3, max_fetch=10, start=saved("88cdb3cd")["txid"])
    pc3 = lookup_2021(api, out)          # stand-in: QMG mapped to the 3GSMG24T-signed Halving tx
    print("\n".join(out))
    print("positive controls:", pc1, "|", pc2, "|", pc3)
    ok &= pc1 == "YES" and pc2.startswith("YES") and "prize" in pc2 and pc3 == "YES"
    print("selftest passed:", ok)
    return ok

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="https://mempool.space/api")
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--max-fetch", type=int, default=40)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    verdicts, text = run(Esplora(a.base), a.depth, a.max_fetch)
    print(text)
    open(os.path.join(CHAIN, "RECEIPT_LOOKUPS.md"), "w").write(text + "\n")
    print(f"written: materials/chain/RECEIPT_LOOKUPS.md; raw txs cached in materials/chain/fetched/")
    return 0

if __name__ == "__main__":
    sys.exit(main())
