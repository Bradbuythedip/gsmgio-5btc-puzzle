#!/usr/bin/env python3
"""Campaign 29: K from the two public halves, against the P32T last-block freeze.

Frame (user, 2026-09-26): the VIC sentence names HALF / BETTER HALF; those sit on-chain as
1GSMG1... and 17ucy1...; the missing piece is the OPERATION that turns the two named halves
into one 32-byte AES key. Accept test frozen to the IV-free P5 == 0x10*16 (two-32-byte-keys
reading). Public bytes only -- no VIC word strings, no private material.

Also sweeps the freeze test over the 32-byte objects the sheet already names, since the
0x10^16 test is a sharper (2^-128) oracle than the PKCS#7+printable gate earlier campaigns used.
"""
import os, sys, hashlib, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p32t_freeze import freeze_ok, p5
from aes_try import evp_bytes_to_key

B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58decode(s):
    n = 0
    for c in s: n = n * 58 + B58.index(c)
    pad = len(s) - len(s.lstrip('1'))
    body = n.to_bytes((n.bit_length() + 7) // 8, 'big') if n else b''
    return b'\x00' * pad + body

ADDR_A = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"   # prize / one half
ADDR_B = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"   # second address / other half
rawA, rawB = b58decode(ADDR_A), b58decode(ADDR_B)
h160A, h160B = rawA[1:-4], rawB[1:-4]            # 20-byte payloads
verA, verB = rawA[:-4], rawB[:-4]                # version+hash160, 21 bytes
payA, payB = rawA, rawB                          # full 25-byte base58check payloads
assert len(h160A) == 20 and len(h160B) == 20

SALT = bytes.fromhex("b45a5e3d827593ca")   # P32T salt (for EVP-password candidates)
SALT_SELF = bytes.fromhex("2d3f6fe06dc950e6")  # cosmic salt, unused here but documented

def raw_keys():
    """(label, 32-byte K) public-only, one rule each."""
    out = []
    def add(lbl, b):
        if len(b) == 32: out.append((lbl, b))
    for oa, ob, tag in ((h160A, h160B, "h160"), (verA, verB, "ver21"), (payA, payB, "pay25"),
                        (ADDR_A.encode(), ADDR_B.encode(), "addr")):
        add(f"sha(A||B):{tag}", hashlib.sha256(oa + ob).digest())
        add(f"sha(B||A):{tag}", hashlib.sha256(ob + oa).digest())
        add(f"sha(A||' '||B):{tag}", hashlib.sha256(oa + b" " + ob).digest())
        add(f"shaA^shaB:{tag}", bytes(x ^ y for x, y in zip(hashlib.sha256(oa).digest(), hashlib.sha256(ob).digest())))
        add(f"sha(sha A||B):{tag}", hashlib.sha256(hashlib.sha256(oa + ob).digest()).digest())
    # raw byte concatenations trimmed/padded to 32
    add("h160A||h160B[:32]", (h160A + h160B)[:32])
    add("h160B||h160A[:32]", (h160B + h160A)[:32])
    add("h160A||h160B||h160A[:32]", (h160A + h160B + h160A)[:32])
    add("h160A^h160B ext", (bytes(x ^ y for x, y in zip(h160A, h160B)) + h160A[:12]))
    # hex-string forms hashed
    for tag, sa, sb in (("h160hex", h160A.hex(), h160B.hex()),):
        add(f"sha(hexA||hexB):{tag}", hashlib.sha256((sa + sb).encode()).digest())
        add(f"sha(hexB||hexA):{tag}", hashlib.sha256((sb + sa).encode()).digest())
    return out

def evp_keys():
    """EVP_BytesToKey candidates (pinned convention), P32T salt, K only."""
    out = []
    strings = {
        "addrA||addrB": ADDR_A + ADDR_B, "addrB||addrA": ADDR_B + ADDR_A,
        "hexA||hexB": h160A.hex() + h160B.hex(),
        "addrA addrB": ADDR_A + " " + ADDR_B,
    }
    for name, s in strings.items():
        for md in ("md5", "sha256"):
            k, _ = evp_bytes_to_key(s.encode(), SALT, md, 32)
            out.append((f"EVP-{md}:{name}", k))
            hx = hashlib.sha256(s.encode()).hexdigest()
            k2, _ = evp_bytes_to_key(hx.encode(), SALT, md, 32)
            out.append((f"EVP-{md}:sha256hex({name})", k2))
    return out

def main():
    cands = raw_keys() + evp_keys()
    hits = [(l, k.hex()) for l, k in cands if freeze_ok(k)]
    print(f"public-halves family: {len(cands)} candidate keys, freeze hits: {len(hits)}")
    for l, kh in hits: print("  *** FREEZE HIT ***", l, kh)
    # show the resulting P5 for a couple, to prove the oracle ran
    for l, k in cands[:3]:
        print(f"  sample P5[{l}] = {p5(k).hex()}")

    # ---- freeze sweep over 32-byte objects the sheet already names (sharper oracle) ----
    import re
    MAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "materials")
    page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
    ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
    dbbi = page[:ab[0][0]]; rest = page[ab[0][1]:]; faed = rest[:rest.index('z')]
    VIC = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
    named = {
        "f73d92": b"f73d92", "16203154": b"16203154", "colbits-packed": bytes.fromhex("f73d92"),
        "dbbi": dbbi.encode(), "faed": faed.encode(), "VIC": VIC.encode(),
        "matrixsumlist": b"matrixsumlist", "610876654997879": b"610876654997879",
        "yellowblueprimes": b"yellowblueprimes", "lastwordsbeforearchichoice": b"lastwordsbeforearchichoice",
        "ciaobellao": b"ciaobellao", "ireallyhopeyouretheone": b"ireallyhopeyouretheone",
    }
    sweep = []
    for n, o in named.items():
        sweep.append((f"sha256({n})", hashlib.sha256(o).digest()))
        if len(o) == 32: sweep.append((f"raw({n})", o))
    shits = [(l, k.hex()) for l, k in sweep if freeze_ok(k)]
    print(f"named-object freeze sweep: {len(sweep)} keys, hits: {len(shits)}")
    for l, kh in shits: print("  *** FREEZE HIT ***", l, kh)

if __name__ == "__main__":
    print("hash160 A:", h160A.hex(), " hash160 B:", h160B.hex())
    main()
