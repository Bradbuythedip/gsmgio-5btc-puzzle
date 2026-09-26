#!/usr/bin/env python3
"""Campaign 45: is the prize key's own 2020 signature an intentional algebraic trapdoor?

Pre-registered in intake/2026-09-26-affine-nonce/PREREG.md. User-directed. Read-only on chain
data; uses only the GSMG creator's own public signatures (the 2020 halving spend, already in
materials/chain/tx_halving_spend.hex and verified at tick 70). No discrete-log search, no AES,
no candidate soup.

The idea: the prize key Q = dG signed three inputs with nonces k_i (R_i = k_i G, r_i = x(R_i)).
If the creator deliberately chose a nonce k = a*d + b with (a,b) from the "neighbors, half and
double" vocabulary, then d falls out of one signature by algebra:

    s*k = z + r*d  and  k = a*d + b   =>   d = (z - s*b) / (s*a - r)   (mod n)

We do NOT know d, so for each fixed (a,b) we compute the candidate d and REQUIRE d*G == Q. This
can only succeed if such a relation was actually planted; for a normally-generated nonce there is
no such (a,b) and every candidate d*G misses Q. So it is a clean yes/no test for a planted
weakness in this one puzzle, not a method against any other key.

Also checked, all requiring d*G == Q to count:
  - repeated nonce across the three inputs (equal r) -> classic single-key recovery;
  - a pairwise affine relation k_j = a*k_i + b between two of the three nonces;
  - exact point identity R_i == +/-(Q), +/-(Q +/- G), +/-2Q, +/-(Q/2), lifting r to both parities
    and to x = r + n when r + n < p.

  python3 campaign_45_affine_nonce.py --selftest   plants a trapdoor sig, recovers it, + controls
  python3 campaign_45_affine_nonce.py              the real run; exit 0 null, 10 HIT
"""
import hashlib, json, os, sys, time
import btc_addr

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
TX = os.path.join(NEO, "materials", "chain", "tx_halving_spend.hex")
OUT = os.path.join(NEO, "attempts", "campaign_45_affine_nonce.jsonl")
PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
N, Pp = btc_addr.N, btc_addr.P
G = (btc_addr.GX, btc_addr.GY)
INV2 = pow(2, -1, N)

# the fixed instruction set: neighbours, half, double, opposite, and nonce=key reuse
AB = {"k=d (nonce=key)": (1, 0), "k=d+1 (upper)": (1, 1), "k=d-1 (lower)": (1, -1),
      "k=2d (double)": (2, 0), "k=d/2 (half)": (INV2, 0), "k=-d (opposite)": (-1, 0),
      "k=-d+1": (-1, 1), "k=-d-1": (-1, -1), "k=2d+1": (2, 1), "k=2d-1": (2, -1),
      "k=d/2+1": (INV2, 1), "k=d/2-1": (INV2, -1)}

def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def h160(b): return hashlib.new("ripemd160", hashlib.sha256(b).digest()).digest()
def neg(P): return None if P is None else (P[0], (Pp - P[1]) % Pp)
def sub(A, B): return btc_addr._add(A, neg(B))

def varint(b, i):
    x = b[i]
    if x < 0xfd: return x, i + 1
    w = {0xfd: 2, 0xfe: 4, 0xff: 8}[x]
    return int.from_bytes(b[i + 1:i + 1 + w], "little"), i + 1 + w

def enc_varint(n): return bytes([n]) if n < 0xfd else b"\xfd" + n.to_bytes(2, "little")

def parse(tx):
    ver, i = tx[:4], 4
    n, i = varint(tx, i); ins = []
    for _ in range(n):
        prev = tx[i:i + 36]; i += 36
        l, i = varint(tx, i); ss = tx[i:i + l]; i += l
        ins.append((prev, ss, tx[i:i + 4])); i += 4
    o0 = i
    n, i = varint(tx, i)
    for _ in range(n):
        i += 8; l, i = varint(tx, i); i += l
    return ver, ins, tx[o0:i], tx[i:i + 4]

def pushes(s):
    out, i = [], 0
    while i < len(s):
        l = s[i]; out.append(s[i + 1:i + 1 + l]); i += 1 + l
    return out

def sighash_all(ver, ins, outs, lt, k, spk, ht):
    b = ver + enc_varint(len(ins))
    for j, (prev, _, seq) in enumerate(ins):
        b += prev + enc_varint(len(spk) if j == k else 0) + (spk if j == k else b"") + seq
    return int.from_bytes(dsha(b + outs + lt + ht.to_bytes(4, "little")), "big")

def der_rs(sig):
    lr = sig[3]; r = int.from_bytes(sig[4:4 + lr], "big")
    ls = sig[5 + lr]; s = int.from_bytes(sig[6 + lr:6 + lr + ls], "big")
    return r, s

def d_from_affine(z, r, s, a, b):
    den = (s * a - r) % N
    if den == 0: return None
    return ((z - s * b) * pow(den, -1, N)) % N

def pubkey_point(pub):
    return (int.from_bytes(pub[1:33], "big"), int.from_bytes(pub[33:65], "big"))

def is_prize_scalar(d):
    if d is None or not (1 <= d < N): return False
    c, u = btc_addr.addrs(d)
    return PRIZE in (c, u)

def lift_r(r):
    pts = []
    for x in (r, r + N):
        if x >= Pp: continue
        y2 = (pow(x, 3, Pp) + 7) % Pp
        y = pow(y2, (Pp + 1) // 4, Pp)
        if (y * y) % Pp == y2:
            pts += [(x, y), (x, (Pp - y) % Pp)]
    return pts

def load_sigs():
    raw = bytes.fromhex("".join(l.strip() for l in open(TX) if not l.startswith("#")))
    ver, ins, outs, lt = parse(raw)
    sigs, Q = [], None
    for k, (prev, ss, seq) in enumerate(ins):
        sig, pub = pushes(ss)
        Q = pubkey_point(pub)
        r, s = der_rs(sig[:-1])
        z = sighash_all(ver, ins, outs, lt, k, b"\x76\xa9\x14" + h160(pub) + b"\x88\xac", sig[-1])
        sigs.append({"input": k, "z": z, "r": r, "s": s})
    return Q, sigs, int.from_bytes(lt, "little")

def run(Q, sigs):
    hits = []
    Qpts = {"+Q": Q, "-Q": neg(Q), "+(Q+G)": btc_addr._add(Q, G), "-(Q+G)": neg(btc_addr._add(Q, G)),
            "+(Q-G)": sub(Q, G), "-(Q-G)": neg(sub(Q, G)), "+2Q": btc_addr.mul(2, Q),
            "-2Q": neg(btc_addr.mul(2, Q)), "+Q/2": btc_addr.mul(INV2, Q), "-Q/2": neg(btc_addr.mul(INV2, Q))}
    # repeated nonce
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            if sigs[i]["r"] == sigs[j]["r"]:
                a, b = sigs[i], sigs[j]
                k = ((a["z"] - b["z"]) * pow((a["s"] - b["s"]) % N, -1, N)) % N
                d = ((a["s"] * k - a["z"]) * pow(a["r"], -1, N)) % N
                if is_prize_scalar(d): hits.append(("repeated-nonce", i, j))
    # single-signature affine to Q
    for sg in sigs:
        for name, (a, b) in AB.items():
            if is_prize_scalar(d_from_affine(sg["z"], sg["r"], sg["s"], a, b)):
                hits.append(("affine-to-Q", sg["input"], name))
    # exact point identity R == f(Q)
    for sg in sigs:
        for R in lift_r(sg["r"]):
            for name, T in Qpts.items():
                if T is not None and R == T:
                    hits.append(("point-identity", sg["input"], name))
    # pairwise nonce affine: k_j = a k_i + b  => linear in d
    for i in range(len(sigs)):
        for j in range(len(sigs)):
            if i == j: continue
            si, sj = sigs[i], sigs[j]
            ri_si = (si["r"] * pow(si["s"], -1, N)) % N; zi_si = (si["z"] * pow(si["s"], -1, N)) % N
            rj_sj = (sj["r"] * pow(sj["s"], -1, N)) % N; zj_sj = (sj["z"] * pow(sj["s"], -1, N)) % N
            for name, (a, b) in AB.items():
                den = (rj_sj - a * ri_si) % N
                if den == 0: continue
                d = ((a * zi_si + b - zj_sj) * pow(den, -1, N)) % N
                if is_prize_scalar(d): hits.append(("pairwise-nonce", i, j, name))
    return hits

def selftest():
    ok = True
    def chk(l, c):
        nonlocal ok; ok = ok and bool(c); print(("PASS " if c else "FAIL ") + l)
    # plant a trapdoor: private key d0, nonce k = d0 + 1, forge a valid (z,r,s), recover it
    d0 = 0x1234567deadbeeffeedfacecafebabe
    Q0 = btc_addr.mul(d0)
    z0 = int.from_bytes(hashlib.sha256(b"trapdoor test").digest(), "big") % N
    k0 = (d0 + 1) % N
    R0 = btc_addr.mul(k0); r0 = R0[0] % N
    s0 = (pow(k0, -1, N) * (z0 + r0 * d0)) % N
    rec = d_from_affine(z0, r0, s0, 1, 1)
    chk("plants k=d+1 trapdoor and recovers d (d*G==Q)", rec == d0 and btc_addr.mul(rec) == Q0)
    chk("wrong (a,b) does not recover d", d_from_affine(z0, r0, s0, 2, 0) != d0)
    # nonce = key
    k1 = d0; R1 = btc_addr.mul(k1); r1 = R1[0] % N
    s1 = (pow(k1, -1, N) * (z0 + r1 * d0)) % N
    chk("plants k=d (nonce=key) and recovers d", d_from_affine(z0, r1, s1, 1, 0) == d0)
    # lift_r round trips a known point's x
    chk("lift_r recovers a known nonce point", any(P == R0 for P in lift_r(r0)))
    # a normal random signature must NOT satisfy any (a,b) against its own key
    import os as _os
    dn = int.from_bytes(_os.urandom(32), "big") % N or 1
    kn = int.from_bytes(_os.urandom(32), "big") % N or 1
    Rn = btc_addr.mul(kn); rn = Rn[0] % N
    sn = (pow(kn, -1, N) * (z0 + rn * dn)) % N
    Qn = btc_addr.mul(dn)
    normal_hit = any(btc_addr.mul(d_from_affine(z0, rn, sn, a, b) or 0) == Qn for a, b in AB.values())
    chk("a normal signature matches no (a,b)", not normal_hit)
    print("campaign 45 self-test passed:", ok)
    return ok

def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    assert selftest(), "self-test failed; a null here would mean nothing"
    Q, sigs, lt = load_sigs()
    assert btc_addr.p2pkh(b"\x04" + Q[0].to_bytes(32, "big") + Q[1].to_bytes(32, "big")) == PRIZE
    hits = run(Q, sigs)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tx_locktime": lt,
           "prize_pubkey_x": hex(Q[0]), "n_sigs": len(sigs),
           "distinct_r": len({s["r"] for s in sigs}), "families_tested": list(AB),
           "point_forms": 10, "HIT": bool(hits), "hits": hits}
    with open(OUT, "w") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"signatures {len(sigs)}  distinct nonces {rec['distinct_r']}  "
          f"single-sig families {len(AB)}  point forms 10")
    print("*** HIT ***" if hits else "null: no planted affine-nonce relation. Logged.")
    print(json.dumps(hits) if hits else "")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
