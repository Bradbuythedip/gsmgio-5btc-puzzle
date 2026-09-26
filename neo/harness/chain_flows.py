#!/usr/bin/env python3
"""Trace GSMG money flows through a Bitcoin node RPC (e.g. Alchemy) and collect hints.

A node RPC has no address index, so the script walks the transaction graph from seeds:
  backward  getrawtransaction(txid, verbose) on every input's funding tx, to --depth
  status    gettxout on every tracked output (unspent or spent)
  forward   optional block scan (--scan A-B, repeatable): any tx that spends a tracked
            output, or pays a GSMG-prefixed address, or carries an OP_RETURN, is recorded
            and tracked in turn
Hints collected: OP_RETURN payloads (hex + ASCII), vanity-prefixed addresses, locktimes
and sequences, unusual amounts, and nonstandard scripts.

Seeds are the raw transactions in ../materials/chain/*.hex (their txids and the txids they
spend) plus any --txid given. Responses are cached in ../materials/chain/cache/ so reruns
cost nothing.

The endpoint URL (it contains the API key) is read from the environment and never written
to disk:
  export BTC_RPC_URL="https://bitcoin-mainnet.g.alchemy.com/v2/<key>"
  python3 chain_flows.py                           # backward walk + status
  python3 chain_flows.py --scan 629990-630010 --scan 839990-840010   # halving windows
  python3 chain_flows.py --offline                 # parse the saved raw txs only, no RPC
Outputs: ../materials/chain/flows.json and ../materials/chain/FLOWS.md
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

# ---------- encoding helpers ----------
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58check(payload):
    x = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    n = int.from_bytes(x, "big"); s = ""
    while n: n, r = divmod(n, 58); s = B58[r] + s
    return "1" * (len(x) - len(x.lstrip(b"\0"))) + s

def _polymod(v):
    g = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]; c = 1
    for d in v:
        b = c >> 25; c = (c & 0x1ffffff) << 5 ^ d
        for i in range(5): c ^= g[i] if (b >> i) & 1 else 0
    return c
def segwit_addr(ver, prog):
    data, acc, bits = [ver], 0, 0
    for b in prog:
        acc = acc << 8 | b; bits += 8
        while bits >= 5: bits -= 5; data.append(acc >> bits & 31)
    if bits: data.append(acc << (5 - bits) & 31)
    const = 1 if ver == 0 else 0x2bc830a3
    hrp = [ord(c) >> 5 for c in "bc"] + [0] + [ord(c) & 31 for c in "bc"]
    pm = _polymod(hrp + data + [0] * 6) ^ const
    chk = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return "bc1" + "".join("qpzry9x8gf2tvdw0s3jn54khce6mua7l"[d] for d in data + chk)

def script_info(spk):
    """(kind, address or None, op_return_bytes or None) for a scriptPubKey."""
    if spk[:1] == b"\x6a":
        i, data = 1, b""
        while i < len(spk):
            op = spk[i]; i += 1
            n = op if op < 0x4c else int.from_bytes(spk[i:i + {0x4c: 1, 0x4d: 2, 0x4e: 4}[op]], "little")
            if op >= 0x4c: i += {0x4c: 1, 0x4d: 2, 0x4e: 4}[op]
            data += spk[i:i + n]; i += n
        return "op_return", None, data
    if len(spk) == 25 and spk[:3] == b"\x76\xa9\x14" and spk[-2:] == b"\x88\xac":
        return "p2pkh", b58check(b"\x00" + spk[3:23]), None
    if len(spk) == 23 and spk[:2] == b"\xa9\x14" and spk[-1:] == b"\x87":
        return "p2sh", b58check(b"\x05" + spk[2:22]), None
    if len(spk) in (22, 34) and spk[0] == 0 and spk[1] == len(spk) - 2:
        return ("p2wpkh" if len(spk) == 22 else "p2wsh"), segwit_addr(0, spk[2:]), None
    if len(spk) == 34 and spk[0] == 0x51 and spk[1] == 32:
        return "p2tr", segwit_addr(1, spk[2:]), None
    if len(spk) in (35, 67) and spk[-1:] == b"\xac":
        return "p2pk", b58check(b"\x00" + hashlib.new("ripemd160", hashlib.sha256(spk[1:-1]).digest()).digest()), None
    return "nonstandard", None, None

# ---------- raw tx parsing (offline seeds) ----------
def parse_raw(hx):
    b = bytes.fromhex(hx); i = 0
    def rd(n):
        nonlocal i; r = b[i:i + n]; i += n; return r
    def vi():
        v = rd(1)[0]
        return v if v < 0xfd else int.from_bytes(rd({0xfd: 2, 0xfe: 4, 0xff: 8}[v]), "little")
    ver = rd(4); seg = b[i] == 0 and b[i + 1] == 1
    if seg: rd(2)
    body_start = i
    vin = []
    for _ in range(vi()):
        prev = rd(32)[::-1].hex(); n = int.from_bytes(rd(4), "little"); ss = rd(vi()); seq = int.from_bytes(rd(4), "little")
        vin.append({"txid": prev, "vout": n, "scriptSig": ss.hex(), "sequence": seq, "witness": []})
    vout = []
    for k in range(vi()):
        val = int.from_bytes(rd(8), "little"); spk = rd(vi())
        vout.append({"n": k, "sat": val, "spk": spk.hex()})
    body_end = i
    if seg:
        for v in vin: v["witness"] = [rd(vi()).hex() for _ in range(vi())]
    lock = rd(4)
    stripped = ver + b[body_start:body_end] + lock
    txid = hashlib.sha256(hashlib.sha256(stripped).digest()).digest()[::-1].hex()
    return {"txid": txid, "version": int.from_bytes(ver, "little"), "segwit": seg,
            "locktime": int.from_bytes(lock, "little"), "vin": vin, "vout": vout, "raw": hx}

def normalize_rpc(tx):
    """Map a verbose getrawtransaction/getblock tx into the parse_raw shape."""
    vin = [{"txid": v.get("txid"), "vout": v.get("vout"), "coinbase": v.get("coinbase"),
            "scriptSig": v.get("scriptSig", {}).get("hex", ""), "sequence": v.get("sequence"),
            "witness": v.get("txinwitness", [])} for v in tx["vin"]]
    vout = [{"n": o["n"], "sat": round(o["value"] * 1e8), "spk": o["scriptPubKey"]["hex"]} for o in tx["vout"]]
    return {"txid": tx["txid"], "version": tx.get("version"), "segwit": tx.get("txid") != tx.get("hash"),
            "locktime": tx.get("locktime"), "vin": vin, "vout": vout, "blockhash": tx.get("blockhash"),
            "time": tx.get("blocktime")}

# ---------- RPC with cache ----------
class RPC:
    def __init__(self, url, delay=0.15):
        self.url, self.delay, self.calls = url, delay, 0
        os.makedirs(CACHE, exist_ok=True)
    def call(self, method, *params, cache=True):
        key = hashlib.sha256(json.dumps([method, params]).encode()).hexdigest()[:24]
        path = os.path.join(CACHE, f"{method}_{key}.json")
        if cache and os.path.exists(path):
            return json.load(open(path))
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": list(params)}).encode()
        for attempt in range(5):
            try:
                req = urllib.request.Request(self.url, body, {"content-type": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    out = json.load(r)
                break
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 4: raise
                time.sleep(2 ** attempt)
        self.calls += 1; time.sleep(self.delay)
        if out.get("error"):
            raise RuntimeError(f"{method}: {out['error']}")
        if cache and method != "gettxout":
            json.dump(out["result"], open(path, "w"))
        return out["result"]

# ---------- analysis ----------
def ascii_or_hex(b):
    return b.decode("ascii") if b and all(32 <= x < 127 for x in b) else b.hex()

def describe(tx, prevouts):
    ins = []
    for v in tx["vin"]:
        if v.get("coinbase"):
            ins.append({"coinbase": v["coinbase"]}); continue
        p = prevouts.get((v["txid"], v["vout"]))
        ins.append({"outpoint": f'{v["txid"]}:{v["vout"]}', "sequence": v["sequence"],
                    "address": p and p["address"], "sat": p and p["sat"]})
    outs = []
    for o in tx["vout"]:
        kind, addr, data = script_info(bytes.fromhex(o["spk"]))
        outs.append({"n": o["n"], "sat": o["sat"], "kind": kind, "address": addr,
                     "op_return": ascii_or_hex(data) if data is not None else None,
                     "label": KNOWN.get(addr)})
    return {"txid": tx["txid"], "locktime": tx["locktime"], "version": tx["version"],
            "time": tx.get("time"), "blockhash": tx.get("blockhash"), "inputs": ins, "outputs": outs}

def hints_for(d):
    h = []
    for o in d["outputs"]:
        if o["op_return"] is not None: h.append(f'OP_RETURN "{o["op_return"]}"')
        if o["address"] and VANITY.match(o["address"]): h.append(f'vanity output {o["address"]}')
        if o["kind"] == "nonstandard": h.append(f'nonstandard output #{o["n"]}')
        if o["sat"] and o["sat"] < 10000 and o["kind"] != "op_return": h.append(f'dust {o["sat"]} sat -> {o["address"]}')
    for i in d["inputs"]:
        a = i.get("address")
        if a and VANITY.match(a): h.append(f"vanity input {a}")
    if d["locktime"]: h.append(f'locktime {d["locktime"]}')
    return h

def run(args):
    seeds = [parse_raw(open(p).read().strip()) for p in sorted(os.listdir(CHAIN)) if p.endswith(".hex")
             for p in [os.path.join(CHAIN, p)]]
    txs = {t["txid"]: t for t in seeds}
    prevouts = {}
    url = os.environ.get("BTC_RPC_URL", "")
    if not args.offline and (not url.startswith("https://") or re.search(r"[<>\s]", url)):
        sys.exit("BTC_RPC_URL must be your full endpoint with the real key, e.g. "
                 "https://bitcoin-mainnet.g.alchemy.com/v2/AbC123... (no <placeholder>, no spaces)")
    rpc = None if args.offline else RPC(url)

    def fetch(txid):
        if txid in txs and "blockhash" in txs[txid]:
            return txs[txid]
        t = normalize_rpc(rpc.call("getrawtransaction", txid, True))
        if t.get("blockhash"):
            t["time"] = t.get("time") or rpc.call("getblockheader", t["blockhash"]).get("time")
        txs[txid] = t
        return t

    if not args.offline:
        # backward walk: fund sources of every seed input, to --depth
        frontier = [t["txid"] for t in seeds] + args.txid
        for depth in range(args.depth + 1):
            nxt = []
            for txid in frontier:
                t = fetch(txid)
                for v in t["vin"]:
                    if v.get("coinbase") or not v.get("txid"): continue
                    p = fetch(v["txid"])
                    o = p["vout"][v["vout"]]
                    kind, addr, _ = script_info(bytes.fromhex(o["spk"]))
                    prevouts[(v["txid"], v["vout"])] = {"address": addr, "sat": o["sat"]}
                    if depth < args.depth and (args.follow_all or (addr and (addr in KNOWN or VANITY.match(addr)))):
                        nxt.append(v["txid"])
            frontier = list(dict.fromkeys(nxt))
        # forward: tracked outputs are those paying known/vanity addresses
        tracked = {}
        for t in list(txs.values()):
            for o in t["vout"]:
                kind, addr, _ = script_info(bytes.fromhex(o["spk"]))
                if addr and (addr in KNOWN or VANITY.match(addr)):
                    tracked[(t["txid"], o["n"])] = addr
        for rng in args.scan:
            a, b = map(int, rng.split("-"))
            for height in range(a, b + 1):
                blk = rpc.call("getblock", rpc.call("getblockhash", height), 2)
                for raw in blk["tx"]:
                    t = normalize_rpc(dict(raw, blockhash=blk["hash"], blocktime=blk["time"]))
                    spends = [(v["txid"], v["vout"]) for v in t["vin"] if (v.get("txid"), v.get("vout")) in tracked]
                    pays = [o for o in t["vout"] if (lambda k: k[1] and (k[1] in KNOWN or VANITY.match(k[1])))(script_info(bytes.fromhex(o["spk"])))]
                    if spends or pays:
                        txs[t["txid"]] = t
                        for o in t["vout"]:
                            k, addr, _ = script_info(bytes.fromhex(o["spk"]))
                            if addr and (addr in KNOWN or VANITY.match(addr)): tracked[(t["txid"], o["n"])] = addr
                print(f"  scanned block {height} ({len(blk['tx'])} txs)", file=sys.stderr)
        status = {}
        for (txid, n), addr in tracked.items():
            r = rpc.call("gettxout", txid, n, True, cache=False)
            status[f"{txid}:{n}"] = {"address": addr, "unspent": r is not None}
    else:
        status = {}

    for t in seeds:
        for v in t["vin"]:
            if v.get("witness") and len(v["witness"]) == 2:
                pub = bytes.fromhex(v["witness"][1])
                h = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
                redeem = b"\x00\x14" + h
                addr = b58check(b"\x05" + hashlib.new("ripemd160", hashlib.sha256(redeem).digest()).digest())
                prevouts.setdefault((v["txid"], v["vout"]), {"address": addr, "sat": None})
            elif v["scriptSig"]:
                ss = bytes.fromhex(v["scriptSig"]); pub = ss[ss[0] + 2:]
                prevouts.setdefault((v["txid"], v["vout"]), {"address": script_info(b"\x41" + pub + b"\xac")[1] if len(pub) == 65 else None, "sat": None})

    report = [describe(t, prevouts) for t in sorted(txs.values(), key=lambda t: (t.get("time") or 0, t["txid"]))]
    for d in report: d["hints"] = hints_for(d)
    out = {"transactions": report, "output_status": status, "rpc_calls": rpc.calls if rpc else 0}
    json.dump(out, open(os.path.join(CHAIN, "flows.json"), "w"), indent=1)
    lines = ["# GSMG money flows", "", f"{len(report)} transactions, {len(status)} tracked outputs.", ""]
    for d in report:
        when = time.strftime("%Y-%m-%d %H:%M", time.gmtime(d["time"])) if d.get("time") else "?"
        lines.append(f"## `{d['txid']}` ({when}, locktime {d['locktime']})")
        for i in d["inputs"]:
            lines.append(f"- in  {i.get('address') or i.get('coinbase', '?')}  {i.get('sat') or ''}")
        for o in d["outputs"]:
            tag = f" **{o['label']}**" if o["label"] else ""
            body = f'OP_RETURN "{o["op_return"]}"' if o["op_return"] is not None else o["address"]
            lines.append(f"- out #{o['n']} {o['sat']} sat -> {body}{tag}")
        if d["hints"]: lines.append("- hints: " + "; ".join(d["hints"]))
        lines.append("")
    if status:
        lines += ["## Tracked output status", ""] + [f"- `{k}` {v['address']}: {'UNSPENT' if v['unspent'] else 'spent'}" for k, v in status.items()]
    open(os.path.join(CHAIN, "FLOWS.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="parse saved raw txs only")
    ap.add_argument("--depth", type=int, default=3, help="backward hops (default 3)")
    ap.add_argument("--follow-all", action="store_true", help="follow every input, not only GSMG/known addresses")
    ap.add_argument("--scan", action="append", default=[], metavar="A-B", help="block height range to scan forward")
    ap.add_argument("--txid", action="append", default=[], help="extra seed txid")
    run(ap.parse_args())
