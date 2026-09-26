#!/usr/bin/env python3
"""Authenticated nonce points R = kG of every prize-key signature in the saved raw transactions.

For each input, the ECDSA check recomputes the signer's nonce point exactly:
    R = (z * s^-1) G + (r * s^-1) Q,   and R.x ≡ r (mod n) iff the signature verifies.
So R's full (x, y) comes out of verification; no secret is involved. Q is the prize public key read
from each input's scriptSig; z is legacy SIGHASH_ALL (verify_halving_sigs.py). Covers the 2020 split
(locktime 629998) and the 2024 split (locktime 840003): six signatures.

Writes materials/chain/nonce_points_prize.json in the format gsmg_offline_solver.py's `opreturn` and
`txscan --nonce-json` read ({"points": [{"label", "x", "y"}]}).

  python3 nonce_points.py
"""
import json, os, sys
import btc_addr
import verify_halving_sigs as V

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN = os.path.join(HERE, "..", "materials", "chain")
TXS = ["tx_halving_spend.hex", "tx_halving2024_spend.hex"]
OUT = os.path.join(CHAIN, "nonce_points_prize.json")
N = btc_addr.N

def points(fname):
    raw = bytes.fromhex("".join(l.strip() for l in open(os.path.join(CHAIN, fname)) if not l.startswith("#")))
    ver, ins, outs, lt = V.parse(raw)
    txid = V.dsha(raw)[::-1].hex()
    for k, (prev, ss, seq) in enumerate(ins):
        sig, pub = V.pushes(ss)
        assert btc_addr.p2pkh(pub) == V.PRIZE, "not a prize-key input"
        der, ht = sig[:-1], sig[-1]
        r, s = V.der_rs(der)
        spk = b"\x76\xa9\x14" + V.h160(pub) + b"\x88\xac"
        z = V.sighash_all(ver, ins, outs, lt, k, spk, ht)
        Q = (int.from_bytes(pub[1:33], "big"), int.from_bytes(pub[33:65], "big"))
        w = pow(s, -1, N)
        R = btc_addr._add(btc_addr.mul(z * w % N), btc_addr.mul(r * w % N, Q))
        assert R is not None and R[0] % N == r, f"{txid}:{k} does not verify"
        yield {"label": f"{txid[:16]}… in{k} (locktime {int.from_bytes(lt, 'little')})",
               "txid": txid, "input": k, "r": f"{r:064x}", "x": f"{R[0]:064x}", "y": f"{R[1]:064x}"}

def main():
    pts = [p for f in TXS for p in points(f)]
    assert len(pts) == 6 and len({p["x"] for p in pts}) == 6
    doc = {"source": "prize-key ECDSA signatures in materials/chain/" + ", ".join(TXS),
           "derivation": "R = (z*s^-1)G + (r*s^-1)Q from signature verification; R.x == r for all six",
           "points": pts}
    json.dump(doc, open(OUT, "w"), indent=2)
    for p in pts:
        print(p["label"], "x", p["x"][:16] + "…", "y", p["y"][:16] + "…")
    print(f"{len(pts)} verified nonce points -> materials/chain/nonce_points_prize.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
