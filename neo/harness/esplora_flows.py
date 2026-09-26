#!/usr/bin/env python3
"""Trace GSMG money flows with a public Esplora API (blockstream.info / mempool.space). No key.

Unlike a node RPC, Esplora indexes addresses and knows who spent each output, so this walks
the flow graph in both directions:
  1. full history of every seed address (GET /address/:a/txs, paged via /txs/chain/:last)
  2. for every output paying a tracked address: GET /tx/:txid/outspends -> the spending tx
  3. any counterparty address matching the GSMG vanity pattern becomes a new seed (--hops)
Hints collected: OP_RETURN payloads, vanity addresses, dust amounts, locktimes, and txs
that touch more than one tracked address.

  python3 esplora_flows.py                         # default seeds, 2 hops
  python3 esplora_flows.py --base https://mempool.space/api
  python3 esplora_flows.py --addr 1ABC... --hops 1
Outputs: ../materials/chain/ESPLORA_FLOWS.md and esplora_flows.json. Responses are cached
in ../materials/chain/cache/ (gitignored).
"""
import argparse, hashlib, json, os, re, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN = os.path.join(HERE, "..", "materials", "chain")
CACHE = os.path.join(CHAIN, "cache")
VANITY = re.compile(r"^(1|3|bc1q|bc1p)gsmg", re.I)
KNOWN = {"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe": "prize (half)",
         "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa": "better half (#3902)",
         "3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK": "creator vanity (sent 'Halving')",
         "1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M": "planted vanity (ledger tick 7)"}

class API:
    def __init__(self, base, delay):
        self.base, self.delay, self.calls = base.rstrip("/"), delay, 0
        os.makedirs(CACHE, exist_ok=True)
    def get(self, path, cache=True):
        key = hashlib.sha256((self.base + path).encode()).hexdigest()[:24]
        fp = os.path.join(CACHE, f"esplora_{key}.json")
        if cache and os.path.exists(fp):
            return json.load(open(fp))
        for attempt in range(8):
            try:
                with urllib.request.urlopen(self.base + path, timeout=60) as r:
                    out = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 7:
                    wait = int(e.headers.get("Retry-After") or 0) or min(2 ** (attempt + 1), 64)
                    print(f"  HTTP {e.code} on {path}; waiting {wait}s", file=sys.stderr)
                    time.sleep(wait); continue
                sys.exit(f"API failed: HTTP {e.code} on {path}: {e.read()[:200]!r}")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 7: sys.exit(f"API unreachable: {e}")
                time.sleep(min(2 ** (attempt + 1), 64))
        self.calls += 1; time.sleep(self.delay)
        if cache: json.dump(out, open(fp, "w"))
        return out

def op_return_text(hexspk):
    b = bytes.fromhex(hexspk)[1:]
    data, i = b"", 0
    while i < len(b):
        op = b[i]; i += 1
        if op < 0x4c: n = op
        else:
            w = {0x4c: 1, 0x4d: 2, 0x4e: 4}.get(op)
            if not w: break
            n = int.from_bytes(b[i:i + w], "little"); i += w
        data += b[i:i + n]; i += n
    return data.decode("ascii") if data and all(32 <= x < 127 for x in data) else data.hex()

def address_txs(api, addr):
    txs, last = [], None
    while True:
        page = api.get(f"/address/{addr}/txs/chain" + (f"/{last}" if last else ""))
        txs += page
        if len(page) < 25: break          # Esplora pages confirmed history 25 at a time
        last = page[-1]["txid"]
    return txs

def summarize(tx, tracked):
    ins = [{"address": v.get("prevout", {}).get("scriptpubkey_address"),
            "sat": v.get("prevout", {}).get("value"), "outpoint": f'{v["txid"]}:{v["vout"]}',
            "coinbase": v.get("is_coinbase", False), "sequence": v.get("sequence")} for v in tx["vin"]]
    outs = []
    for n, o in enumerate(tx["vout"]):
        outs.append({"n": n, "sat": o["value"], "address": o.get("scriptpubkey_address"),
                     "type": o["scriptpubkey_type"],
                     "op_return": op_return_text(o["scriptpubkey"]) if o["scriptpubkey_type"] == "op_return" else None,
                     "label": KNOWN.get(o.get("scriptpubkey_address"))})
    st = tx.get("status", {})
    d = {"txid": tx["txid"], "height": st.get("block_height"), "time": st.get("block_time"),
         "locktime": tx["locktime"], "fee": tx.get("fee"), "inputs": ins, "outputs": outs}
    h = []
    for o in outs:
        if o["op_return"] is not None: h.append(f'OP_RETURN "{o["op_return"]}"')
        if o["type"] not in ("op_return",) and o["sat"] < 10000: h.append(f'dust {o["sat"]} sat -> {o["address"]}')
    touched = {a for a in [i["address"] for i in ins] + [o["address"] for o in outs] if a in tracked}
    if len(touched) > 1: h.append("links " + ", ".join(sorted(touched)))
    if tx["locktime"]: h.append(f'locktime {tx["locktime"]}')
    d["hints"] = h
    return d

def run(a):
    api = API(a.base, a.delay)
    seeds = list(dict.fromkeys(a.addr or list(KNOWN)))
    tracked, txs, done = set(seeds), {}, set()
    frontier = seeds
    for hop in range(a.hops + 1):
        nxt = []
        for addr in frontier:
            if addr in done: continue
            done.add(addr)
            info = api.get(f"/address/{addr}", cache=False)
            cs = info["chain_stats"]
            print(f"{addr}: {cs['tx_count']} txs, funded {cs['funded_txo_sum']} sat, "
                  f"spent {cs['spent_txo_sum']} sat, balance {cs['funded_txo_sum'] - cs['spent_txo_sum']}",
                  file=sys.stderr)
            for tx in address_txs(api, addr):
                txs[tx["txid"]] = tx
        # forward: who spent outputs paying tracked addresses
        for tx in list(txs.values()):
            if not any(o.get("scriptpubkey_address") in tracked for o in tx["vout"]): continue
            for n, sp in enumerate(api.get(f"/tx/{tx['txid']}/outspends")):
                if sp.get("spent") and tx["vout"][n].get("scriptpubkey_address") in tracked and sp["txid"] not in txs:
                    txs[sp["txid"]] = api.get(f"/tx/{sp['txid']}")
        # new vanity counterparties become seeds for the next hop
        for tx in txs.values():
            addrs = [v.get("prevout", {}).get("scriptpubkey_address") for v in tx["vin"]] + \
                    [o.get("scriptpubkey_address") for o in tx["vout"]]
            for x in addrs:
                if x and x not in tracked and (VANITY.match(x) or a.follow_all):
                    tracked.add(x); nxt.append(x)
        frontier = nxt
    report = sorted((summarize(t, tracked) for t in txs.values()), key=lambda d: (d["height"] or 10**9, d["txid"]))
    json.dump({"base": a.base, "tracked": sorted(tracked), "transactions": report, "calls": api.calls},
              open(os.path.join(CHAIN, "esplora_flows.json"), "w"), indent=1)
    L = ["# GSMG money flows (Esplora)", "", f"Source {a.base}; {len(report)} transactions; tracked: "
         + ", ".join(f"`{t}`" + (f" ({KNOWN[t]})" if t in KNOWN else "") for t in sorted(tracked)), ""]
    for d in report:
        when = time.strftime("%Y-%m-%d %H:%M", time.gmtime(d["time"])) if d["time"] else "mempool"
        L.append(f"## `{d['txid']}` (block {d['height']}, {when}, fee {d['fee']})")
        for i in d["inputs"]:
            L.append(f"- in  {'coinbase' if i['coinbase'] else i['address']}  {i['sat']}")
        for o in d["outputs"]:
            body = f'OP_RETURN "{o["op_return"]}"' if o["op_return"] is not None else o["address"]
            L.append(f"- out #{o['n']} {o['sat']} sat -> {body}" + (f" **{o['label']}**" if o["label"] else ""))
        if d["hints"]: L.append("- hints: " + "; ".join(d["hints"]))
        L.append("")
    open(os.path.join(CHAIN, "ESPLORA_FLOWS.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"[{api.calls} API calls]", file=sys.stderr)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="https://blockstream.info/api", help="Esplora base URL")
    ap.add_argument("--addr", action="append", help="seed address (default: the four known)")
    ap.add_argument("--hops", type=int, default=2, help="vanity-counterparty hops (default 2)")
    ap.add_argument("--follow-all", action="store_true", help="follow every counterparty (can explode)")
    ap.add_argument("--delay", type=float, default=0.3, help="seconds between calls")
    run(ap.parse_args())
