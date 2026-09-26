#!/usr/bin/env python3
"""Campaign 51: padding-independent, tail-robust key/address oracle (audit finding GAP 1/2/3).

check_pt() hard-rejects any decrypt whose PKCS#7 padding is invalid BEFORE it looks at
printability, and gate.py runs the 64-hex->address oracle only when check_pt already flagged a
hit. So a candidate whose true plaintext is (a) a raw 32-byte key (miniA, -nopad), (b) a 64-hex
key whose final block is off, or (c) any non-PKCS#7 layout is SILENTLY rejected, and the strongest
confirmation (the prize address) is never computed. This closes that gap: for each candidate it
decrypts WITHOUT unpadding and applies address/hex checks to the FULL plaintext and to its blocks,
independent of padding.

Per candidate x {raw, sha256hex} x EVP-{md5,sha256} x {miniA, miniAB, inner96, cosmic}:
  (a) every 64-hex run in the full plaintext (ascii) -> scalar -> P2PKH vs prize / 17ucy1
  (b) pt[:32] and pt[32:64] as raw 32-byte scalars -> P2PKH vs prize / 17ucy1
  (c) printability of all blocks except the last (the tail-robust CBC check)
Base rate ~0: 2^-160 per address test; a wrong key's block-prefix printability >=0.90 is ~0.

The SalPhaseIon ciphertext is byte-verified across 3 captures (tick 83), so this is a completeness
check on the ACCEPT RULE, not a transcription fix. No new vocabulary: the candidates are the
strongest known answers/labels.

  python3 campaign_51_padding_independent.py
"""
import hashlib, json, os, re, sys, time
import aes_try, btc_addr

NEO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(NEO, "attempts", "campaign_51_padding_independent.jsonl")
PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
LOCKS = ("miniA", "miniAB", "inner96", "cosmic")
HEX64 = re.compile(rb"[0-9a-fA-F]{64}")

# strongest known candidates (same set as campaign 49/50; the answer if it is corpus-derivable)
from campaign_50_mitm_curated import ANSWERS

def addr_hit(scalar):
    k = scalar % btc_addr.N
    if not (1 <= k < btc_addr.N):
        return None
    c, u = btc_addr.addrs(k)
    for a in (c, u):
        if a == PRIZE: return ("prize", a)
        if a == BETTER: return ("better", a)
    return None

def printable_prefix_ratio(pt, block=16):
    """printability of all blocks except the last (tail-robust)."""
    body = pt[:-block] if len(pt) > block else pt
    if not body: return 0.0
    return sum(32 <= c < 127 or c in (9, 10, 13) for c in body) / len(body)

def scan(pt):
    hits = []
    for m in HEX64.findall(pt):
        h = addr_hit(int(m, 16))
        if h: hits.append(("hex64:" + m.decode(), h))
    for lbl, seg in (("pt[:32]", pt[:32]), ("pt[32:64]", pt[32:64])):
        if len(seg) == 32:
            h = addr_hit(int.from_bytes(seg, "big"))
            if h: hits.append((lbl, h))
    return hits

def main():
    assert aes_try.self_test() and btc_addr.self_test(), "self-test failed"
    targets = aes_try.load_targets()
    tot = 0; near = 0; hits = []
    with open(OUT, "w") as f:
        for c in ANSWERS:
            for form, pw in (("raw", c), ("sha256hex", hashlib.sha256(c.encode()).hexdigest())):
                pwb = pw.encode()
                for tname in LOCKS:
                    t = targets[tname]
                    for kdf in ("m5", "s2"):
                        md, kl = aes_try.KDFS[kdf]
                        key, iv = aes_try.evp_bytes_to_key(pwb, t["salt"], md, kl)
                        pt = aes_try.decrypt(t["ct"], key, iv)
                        tot += 1
                        ah = scan(pt)
                        pr = printable_prefix_ratio(pt)
                        if ah:
                            for where, (which, addr) in ah:
                                rec = {"candidate": c, "form": form, "target": tname, "kdf": kdf,
                                       "where": where, "which": which, "addr": addr, "HIT": True}
                                hits.append(rec); f.write(json.dumps(rec) + "\n")
                                print("*** ADDRESS HIT ***", json.dumps(rec))
                        if pr >= 0.85:
                            near += 1
                            rec = {"candidate": c, "form": form, "target": tname, "kdf": kdf,
                                   "prefix_printable": round(pr, 3), "head": pt[:48].decode("latin1"), "NEAR": True}
                            f.write(json.dumps(rec) + "\n")
                            print("near (printable prefix):", json.dumps(rec)[:180])
    print(f"\ndecrypts={tot} address_hits={len(hits)} printable_prefix>=0.85={near}")
    print("*** HIT ***" if hits else "null: no padding-independent address/key hit; no tail-robust printable prefix. "
          "The accept-rule gap yields nothing for the strong candidates.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
