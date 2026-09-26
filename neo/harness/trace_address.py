#!/usr/bin/env python3
"""Pull and decode every transaction of a Bitcoin address from an Esplora API (mempool.space
or blockstream.info), or decode raw tx hex offline. No keys, read-only.

Purpose here: trace the funding of the Issue #79 "Half" address
1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu (LEDGER tick 75 left its 2026-02-05 funding source untraced).
A GSMG creator-trail counterparty (1EtbTv…, 3GSMG24T…, the prize key, 17ucy1…) on the funding
side would mean the creator acknowledged the construction; anything else keeps it solver traffic.

Online (needs network; blocked in the cloud sandbox, works on a node/unblocked host):
    python3 trace_address.py                      # default address, mempool.space
    python3 trace_address.py --addr <a> --base https://blockstream.info/api
Offline (decode hex you already have; the sandbox path):
    python3 trace_address.py --decode-hex tx1.hex tx2.hex
    python3 trace_address.py --decode-hex-string 0200000001...

Writes <out>/<addr>/ : each txid.hex, a decoded.json, and a FLOWS.md summary.
Outbound HTTPS honours HTTPS_PROXY. Responses cache under <out>/<addr>/cache/.
"""
import argparse, hashlib, json, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import btc_addr

DEFAULT_ADDR = "1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu"
DEFAULT_BASE = "https://mempool.space/api"
OUT_ROOT = os.path.join(HERE, "..", "materials", "chain", "traces")

# GSMG creator trail (LEDGER ticks 37-38, 59, 75) — funding from any of these authenticates
TRAIL = {
    "1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1": "creator funder (2018/2019)",
    "3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK": "creator vanity (sent Halving / Good job Neo)",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe": "prize",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa": "better half (#3902)",
    "1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3": "planted vanity (tick 7)",
    "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": "post-3.2 answer address",
}

# ---------- address encoding from scriptPubKey ----------
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    gen = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= gen[i] if (b >> i) & 1 else 0
    return chk

def bech32_encode(hrp, data, spec):
    const = 0x2bc830a3 if spec == "bech32m" else 1
    values = [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp] + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    chk = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(CHARSET[d] for d in data + chk)

def convertbits(data, frm, to, pad=True):
    acc = bits = 0
    ret = []
    maxv = (1 << to) - 1
    for b in data:
        acc = (acc << frm) | b
        bits += frm
        while bits >= to:
            bits -= to
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (to - bits)) & maxv)
    return ret

def segwit_addr(witver, prog):
    spec = "bech32" if witver == 0 else "bech32m"
    return bech32_encode("bc", [witver] + convertbits(prog, 8, 5), spec)

def spk_to_addr(s):
    if len(s) == 25 and s[:3] == b"\x76\xa9\x14" and s[23:] == b"\x88\xac":
        return btc_addr.b58encode(b"\x00" + s[3:23] + dsha(b"\x00" + s[3:23])[:4])
    if len(s) == 23 and s[:2] == b"\xa9\x14" and s[22:] == b"\x87":
        return btc_addr.b58encode(b"\x05" + s[2:22] + dsha(b"\x05" + s[2:22])[:4])
    if len(s) >= 4 and s[0] in (0x00, 0x51) and s[1] == len(s) - 2 and s[1] in (0x14, 0x20):
        return segwit_addr(0 if s[0] == 0x00 else 1, s[2:])
    if s[:1] == b"\x6a":
        return "OP_RETURN " + repr(bytes(s[1:]))
    return "script:" + s.hex()

# ---------- tx decode ----------
def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def varint(b, i):
    x = b[i]
    if x < 0xfd: return x, i + 1
    w = {0xfd: 2, 0xfe: 4, 0xff: 8}[x]
    return int.from_bytes(b[i + 1:i + 1 + w], "little"), i + 1 + w

def decode_tx(raw):
    seg = raw[4] == 0 and raw[5] == 1
    i = 6 if seg else 4
    n, i = varint(raw, i)
    vin = []
    for _ in range(n):
        prev = raw[i:i + 32][::-1].hex(); vout = int.from_bytes(raw[i + 32:i + 36], "little"); i += 36
        l, i = varint(raw, i); i += l; seq = int.from_bytes(raw[i:i + 4], "little"); i += 4
        vin.append({"prev_txid": prev, "prev_vout": vout, "sequence": seq})
    o0 = i
    n, i = varint(raw, i)
    vout = []
    for _ in range(n):
        val = int.from_bytes(raw[i:i + 8], "little"); i += 8
        l, i = varint(raw, i); spk = raw[i:i + l]; i += l
        vout.append({"value_sat": val, "address": spk_to_addr(spk)})
    outs_end = i
    if seg:
        for _ in range(len(vin)):
            m, i = varint(raw, i)
            for _ in range(m):
                l, i = varint(raw, i); i += l
    locktime = int.from_bytes(raw[i:i + 4], "little")
    txid = dsha(raw[:4] + raw[(6 if seg else 4):outs_end] + raw[i:i + 4])[::-1].hex() if seg else dsha(raw)[::-1].hex()
    return {"txid": txid, "version": int.from_bytes(raw[:4], "little"), "segwit": seg,
            "locktime": locktime, "vin": vin, "vout": vout}

def _len_varint(n):
    return 1 if n < 0xfd else 3

# ---------- API ----------
class Esplora:
    def __init__(self, base, out):
        self.base = base.rstrip("/"); self.cache = os.path.join(out, "cache")
        os.makedirs(self.cache, exist_ok=True); self.calls = 0
    def get(self, path, raw=False):
        key = hashlib.sha256((self.base + path).encode()).hexdigest()[:20]
        fp = os.path.join(self.cache, key + (".hex" if raw else ".json"))
        if os.path.exists(fp):
            return open(fp, "rb").read() if raw else json.load(open(fp))
        for attempt in range(5):
            try:
                with urllib.request.urlopen(self.base + path, timeout=45) as r:
                    body = r.read(); self.calls += 1
                open(fp, "wb").write(body)
                return body if raw else json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code == 404: return None
                time.sleep(2 * (attempt + 1))
            except Exception:
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"GET failed (network blocked?): {self.base + path}")
    def address_txs(self, addr):
        txs, last = [], None
        while True:
            page = self.get(f"/address/{addr}/txs" + (f"/chain/{last}" if last else ""))
            if not page: break
            txs += page
            if len(page) < 25: break
            last = page[-1]["txid"]
        return txs

def flag(addr):
    return f"  <-- {TRAIL[addr]}" if addr in TRAIL else ""

def report(addr, decoded, esplora_json, out):
    lines = [f"# Transactions of {addr}", ""]
    for d in decoded:
        j = esplora_json.get(d["txid"], {})
        h = j.get("status", {}).get("block_height", "?")
        lines.append(f"## {d['txid']}  (block {h}, locktime {d['locktime']}{', segwit' if d['segwit'] else ''})")
        for vi, v in enumerate(d["vin"]):
            a = ""
            if vi < len(j.get("vin", [])):
                a = j["vin"][vi].get("prevout", {}).get("scriptpubkey_address", "") or ""
            lines.append(f"- in  {v['prev_txid'][:16]}…:{v['prev_vout']}  {a}{flag(a)}")
        for v in d["vout"]:
            lines.append(f"- out {v['value_sat']} sat -> {v['address']}{flag(v['address'])}")
        lines.append("")
    open(os.path.join(out, "FLOWS.md"), "w").write("\n".join(lines))
    json.dump({"address": addr, "decoded": decoded}, open(os.path.join(out, "decoded.json"), "w"), indent=1)
    funders = sorted({j.get("vin", [{}])[0].get("prevout", {}).get("scriptpubkey_address", "")
                      for d in decoded for j in [esplora_json.get(d["txid"], {})]} & set(TRAIL))
    print("\n".join(lines[:60]))
    print(f"\n{len(decoded)} txs decoded -> {out}")
    print("creator-trail funders among inputs:", funders or "NONE (solver traffic)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--addr", default=DEFAULT_ADDR)
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--out", default=OUT_ROOT)
    ap.add_argument("--decode-hex", nargs="*", help="decode raw-hex files offline")
    ap.add_argument("--decode-hex-string", help="decode one raw-hex string offline")
    args = ap.parse_args()

    if args.decode_hex or args.decode_hex_string:
        blobs = []
        for f in (args.decode_hex or []):
            blobs.append("".join(l.strip() for l in open(f) if not l.startswith("#")))
        if args.decode_hex_string:
            blobs.append(args.decode_hex_string.strip())
        for hx in blobs:
            d = decode_tx(bytes.fromhex(hx))
            print(f"txid {d['txid']}  ver {d['version']}  locktime {d['locktime']}  segwit {d['segwit']}")
            for v in d["vin"]:
                print(f"  in  {v['prev_txid']}:{v['prev_vout']} seq {v['sequence']:#x}")
            for v in d["vout"]:
                print(f"  out {v['value_sat']} sat -> {v['address']}{flag(v['address'])}")
            print()
        return

    out = os.path.join(args.out, args.addr)
    os.makedirs(out, exist_ok=True)
    api = Esplora(args.base, out)
    print(f"pulling {args.addr} from {args.base} …")
    txs = api.address_txs(args.addr)
    print(f"{len(txs)} transactions")
    decoded, ejson = [], {}
    for t in txs:
        txid = t["txid"]; ejson[txid] = t
        hx = api.get(f"/tx/{txid}/hex", raw=True)
        if hx is None: continue
        hx = hx.decode().strip()
        open(os.path.join(out, txid + ".hex"), "w").write(hx + "\n")
        d = decode_tx(bytes.fromhex(hx))
        if d["txid"] != txid:
            print(f"  WARN recomputed txid mismatch for {txid}")
        decoded.append(d)
    report(args.addr, decoded, ejson, out)

if __name__ == "__main__":
    main()
