#!/usr/bin/env python3
"""Campaign 47: Bitcoin-specific combinations of the Issue #79 "Half"/"Better Half" scalars.

Address predicate only; no AES. The two scalars are NOT hardcoded: they are re-derived in-code
from the in-repo false-positive file (unverified/drive-2026-05/cosmic_1327b_decrypted.bin) by the
Issue #79 recipe (tick 75), so this file contains no private-key material. The self-check confirms
they reproduce the published #79 addresses. Full keys are never printed; prefixes only.

These operands are solver artifacts (slices of a 1-byte-pad false-positive decrypt, tick 75). The
run is a closure of the "did you try a Bitcoin construction, not just arithmetic" question, against
the prize `1GSMG1…` and `17ucy1…`. Expected: null.

  python3 campaign_47_halfbetter_combine.py
"""
import hashlib, hmac, json, os, sys, time
import btc_addr

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
NOISE = os.path.join(NEO, "..", "unverified", "drive-2026-05", "cosmic_1327b_decrypted.bin")
OUT = os.path.join(NEO, "attempts", "campaign_47_halfbetter_combine.jsonl")
N = btc_addr.N
TARGETS = {"prize": "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "better17ucy1": "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"}
# published #79 addresses, for the provenance self-check only
A_HALF = ("1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu", "15E3pcDDXSKhvi3CLVhRTHEgd8dbVKvSZg")
A_BETTER = ("145ZQ9siLrsXBKf465wjdyQYAP5dRwhRhQ", "1FhbJnrdq1FmeiXrpTqnpQ8jvYV7naze96")

def derive_half_better():
    raw = open(NOISE, "rb").read()
    bits = [(b >> (7 - k)) & 1 for b in raw for k in range(8)][:103 * 103]
    M = [bits[r * 103:(r + 1) * 103] for r in range(103)]
    rs = [sum(row) for row in M]
    cs = [sum(M[r][c] for r in range(103)) for c in range(103)]
    digits = [rs[i] + cs[(i + 7) % 103] - 80 for i in range(103)]
    n = 0
    for d in digits:
        n = n * 38 + d
    out = n.to_bytes(68, "big")
    return out[:32], out[32:64], out[64:68]

def check(records, label, k):
    if not (0 < k < N):
        return
    c, u = btc_addr.addrs(k)
    hit = [name for name, a in TARGETS.items() if a in (c, u)]
    records.append({"label": label, "addr_comp": c, "addr_unc": u, "HIT": hit})
    print(f"  {label:44s} {c}  {u}  {'*** HIT ' + str(hit) if hit else 'null'}")

def bip32_master(seed):
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    return int.from_bytes(I[:32], "big") % N, I[32:]

def ckd_priv(k, chain, idx, hardened):
    if hardened:
        data = b"\x00" + k.to_bytes(32, "big") + (idx | 0x80000000).to_bytes(4, "big")
    else:
        comp = btc_addr.pubkeys(k)[0]
        data = comp + idx.to_bytes(4, "big")
    I = hmac.new(chain, data, hashlib.sha512).digest()
    return (int.from_bytes(I[:32], "big") + k) % N

def main():
    assert btc_addr.self_test(), "address self-test failed"
    HALF, BETTER, TRAIL = derive_half_better()
    kh, kb = int.from_bytes(HALF, "big"), int.from_bytes(BETTER, "big")
    # provenance self-check: the two scalars must reproduce the published #79 addresses
    assert btc_addr.addrs(kh) == A_HALF and btc_addr.addrs(kb) == A_BETTER, "derivation mismatch"
    print(f"provenance OK: half {HALF[:4].hex()}..  better {BETTER[:4].hex()}..  trailer {TRAIL.hex()}")
    rec = []

    # arithmetic class (reproduce the user's USER-grade table)
    check(rec, "half XOR better", int.from_bytes(bytes(a ^ b for a, b in zip(HALF, BETTER)), "big") % N)
    check(rec, "half + better", (kh + kb) % N)
    check(rec, "half - better", (kh - kb) % N)
    check(rec, "better - half", (kb - kh) % N)
    check(rec, "half * better", (kh * kb) % N)
    check(rec, "half / better", (kh * pow(kb, -1, N)) % N)
    check(rec, "(half + better)/2", ((kh + kb) * pow(2, -1, N)) % N)
    check(rec, "sha256(half||better)", int.from_bytes(hashlib.sha256(HALF + BETTER).digest(), "big") % N)
    check(rec, "sha256(better||half)", int.from_bytes(hashlib.sha256(BETTER + HALF).digest(), "big") % N)
    check(rec, "sha256(hex(half)||hex(better))",
          int.from_bytes(hashlib.sha256((HALF.hex() + BETTER.hex()).encode()).digest(), "big") % N)
    lc = 0
    for a in range(-64, 65):
        for b in range(-64, 65):
            check_k = (a * kh + b * kb) % N
            c, u = btc_addr.addrs(check_k) if 0 < check_k < N else (None, None)
            if c in TARGETS.values() or u in TARGETS.values():
                rec.append({"label": f"a*half+b*better a={a} b={b}", "addr_comp": c, "addr_unc": u, "HIT": ["prize/better"]})
                print(f"  *** HIT a={a} b={b}")
            lc += 1
    print(f"  a*half+b*better grid: {lc} pairs [-64,64]^2, no hit")

    # Bitcoin-specific class
    for label, data in [("HMAC-SHA512(better,half)", hmac.new(BETTER, HALF, hashlib.sha512).digest()),
                        ("HMAC-SHA512(half,better)", hmac.new(HALF, BETTER, hashlib.sha512).digest()),
                        ("sha512(half||better)[:32]", hashlib.sha512(HALF + BETTER).digest()),
                        ("sha512(better||half)[:32]", hashlib.sha512(BETTER + HALF).digest())]:
        check(rec, label, int.from_bytes(data[:32], "big") % N)
    check(rec, "interleave half/better", int.from_bytes(bytes(x for p in zip(HALF, BETTER) for x in p), "big") % N)
    check(rec, "interleave better/half", int.from_bytes(bytes(x for p in zip(BETTER, HALF) for x in p), "big") % N)

    # BIP32: each as seed, path from the other's / trailer's bytes, non-hardened and hardened
    for seedname, seed in [("half", HALF), ("better", BETTER)]:
        mk, ch = bip32_master(seed)
        for idxname, ib in [("better[:4]", BETTER[:4]), ("better[-4:]", BETTER[-4:]),
                            ("half[:4]", HALF[:4]), ("half[-4:]", HALF[-4:]), ("trailer", TRAIL)]:
            idx = int.from_bytes(ib, "big") % (1 << 31)
            check(rec, f"BIP32 {seedname} seed / {idxname}", ckd_priv(mk, ch, idx, False))
            check(rec, f"BIP32 {seedname} seed / {idxname} hardened", ckd_priv(mk, ch, idx, True))
        check(rec, f"BIP32 {seedname} master key", mk)

    # point sum H+B, x-coordinate and its hash; also with trailer offset
    H = btc_addr.mul(kh); B = btc_addr.mul(kb); S = btc_addr._add(H, B)
    xh = S[0]
    check(rec, "(H+B).x as scalar", xh % N)
    check(rec, "sha256((H+B).x)", int.from_bytes(hashlib.sha256(xh.to_bytes(32, "big")).digest(), "big") % N)
    check(rec, "(H+B).x + trailer", (xh + int.from_bytes(TRAIL, "big")) % N)

    hits = [r for r in rec if r["HIT"]]
    with open(OUT, "w") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "half_prefix": HALF[:4].hex(), "better_prefix": BETTER[:4].hex(),
                            "n_named_constructions": len(rec), "linear_grid": lc,
                            "HIT": bool(hits), "records": rec}) + "\n")
    print("*** HIT ***" if hits else f"null: {len(rec)} named constructions + {lc} linear pairs, 0 hits. Logged.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
