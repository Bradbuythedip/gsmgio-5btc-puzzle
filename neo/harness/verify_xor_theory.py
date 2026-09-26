#!/usr/bin/env python3
"""Verify the circulating XOR theory end to end.

Claim A: XOR(sha256(t1..t7)) over the seven SalPhaseIon tokens == a795de11...,
         and that value is the OpenSSL password that decrypts the Cosmic Duality blob.
Claim B: the witness scalar d = abc09ead..., XORed against that key (or against the
         published "half"/"better half" scalars), yields the prize private key.

Both are checked against primary evidence: Claim A against the actual blob bytes,
Claim B against the actual prize address. Bounded, enumerable candidate set.
"""
import base64, hashlib, itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import evp_bytes_to_key, decrypt, check_pt, MAT
from btc_addr import addrs, N, self_test

PRIZE = '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
WITNESS_ADDR_PREFIX = '1GSMG9VDL'

# the seven tokens as published in the circulating writeup
TOKENS7 = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
           "matrixsumlist", "yourlastcommand", "secondanswer"]
CLAIMED_KEY = "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735"
WITNESS_D = "abc09ead825c42ba92c90e95a07cfc8bcda8ae6bd2116c31583aaff19f5d99f6"
HALF = "0423d911"       # truncated in the writeup ("0423d911...8fcc35")
BETTER = "48cc46e6"     # truncated in the writeup ("48cc46e6...623971")


def xor(*bs):
    out = bytearray(32)
    for b in bs:
        for i in range(32):
            out[i] ^= b[i]
    return bytes(out)


def sha(s):
    return hashlib.sha256(s.encode()).digest()


def main():
    print("=== address math self-test ===")
    assert self_test(), "EC self-test failed - results untrustworthy"

    print("\n=== Claim A.1: does XOR of the 7 token hashes reproduce a795de11...? ===")
    x = xor(*[sha(t) for t in TOKENS7])
    print("  computed :", x.hex())
    print("  claimed  :", CLAIMED_KEY)
    print("  MATCH    :", x.hex() == CLAIMED_KEY)

    # order/duplication variants, in case the writeup's token list is garbled
    uniq = list(dict.fromkeys(TOKENS7))
    variants = {"as-published(7)": x, "dedup(6)": xor(*[sha(t) for t in uniq])}
    for t in ("secondanswer", "yourlastcommand"):
        rest = [s for s in uniq if s != t]
        variants[f"dedup-minus-{t}"] = xor(*[sha(s) for s in rest])
    for name, v in variants.items():
        if v.hex() == CLAIMED_KEY:
            print(f"  variant {name} reproduces the claimed key")

    print("\n=== Claim A.2: does the claimed key decrypt the Cosmic Duality blob? ===")
    cosmic = base64.b64decode("".join(open(os.path.join(MAT, "cosmic_duality_b64.txt")).read().split()))
    salt, ct = cosmic[8:16], cosmic[16:]
    pw_forms = {
        "hex-string-as-password": CLAIMED_KEY,
        "HEX-UPPER-as-password": CLAIMED_KEY.upper(),
        "computed-xor-hex": x.hex(),
    }
    any_hit = False
    for pname, pw in pw_forms.items():
        for md in ("md5", "sha256", "sha1"):
            for kl in (32, 16):
                k, iv = evp_bytes_to_key(pw.encode(), salt, md, kl)
                r = check_pt(decrypt(ct, k, iv))
                if r and r["hit"]:
                    any_hit = True
                    print(f"  HIT {pname} evp-{md}-{kl}: {r['body'][:80]!r}")
    # raw 32-byte key forms (key = the bytes themselves)
    from Crypto.Cipher import AES
    for kname, kb in (("xor-bytes", x), ("claimed-bytes", bytes.fromhex(CLAIMED_KEY))):
        for ivname, iv in (("zero", b"\x00" * 16), ("salt2", salt * 2), ("ct-prefix", ct[:16])):
            body = ct[16:] if ivname == "ct-prefix" else ct
            r = check_pt(AES.new(kb, AES.MODE_CBC, iv).decrypt(body))
            if r and r["hit"]:
                any_hit = True
                print(f"  HIT rawkey {kname} iv={ivname}: {r['body'][:80]!r}")
    print("  any verified decryption:", any_hit)

    print("\n=== Claim B: do XOR combinations of the witness scalar hit the prize? ===")
    operands = {
        "claimed-cosmic-key": bytes.fromhex(CLAIMED_KEY),
        "xor-of-7": x,
        "sha256(prize-addr)": sha(PRIZE),
        "sha256(caption)": sha("GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"),
        "zero": bytes(32),
    }
    for t in TOKENS7 + ["yinyang", "yellowblueprimes", "half", "betterhalf"]:
        operands[f"sha256({t})"] = sha(t)

    d = bytes.fromhex(WITNESS_D)
    tested = 0
    hits = []
    # single XOR and identity
    cands = {"d itself": d}
    for name, op in operands.items():
        cands[f"d XOR {name}"] = xor(d, op)
    # pairwise XOR of two operands with d (bounded)
    for (n1, o1), (n2, o2) in itertools.combinations(operands.items(), 2):
        cands[f"d XOR {n1} XOR {n2}"] = xor(d, o1, o2)

    for name, kb in cands.items():
        k = int.from_bytes(kb, 'big')
        tested += 1
        if not (1 <= k < N):
            continue
        c, u = addrs(k)
        if PRIZE in (c, u):
            hits.append((name, c, u))
        if c.startswith(WITNESS_ADDR_PREFIX) or u.startswith(WITNESS_ADDR_PREFIX):
            print(f"  note: {name} -> witness-style address {c} / {u}")
    print(f"  candidates tested: {tested}")
    print(f"  prize-address hits: {len(hits)}")
    for hname, c, u in hits:
        print("  *** PRIZE HIT ***", hname, c, u)

    print("\n=== what does the witness scalar itself produce? ===")
    c, u = addrs(int.from_bytes(d, 'big'))
    print("  d compressed  :", c)
    print("  d uncompressed:", u)
    print("  equals prize  :", PRIZE in (c, u))


if __name__ == "__main__":
    main()
