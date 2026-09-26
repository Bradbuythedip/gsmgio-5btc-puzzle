#!/usr/bin/env python3
"""Campaign 54: the Ricardian "document hash = identifier" reading (pre-registered, tick 89).

Grigg's Ricardian contract hashes a whole human-readable document into its identifier. Mapped onto
GSMG: the key or password for the next step is the hash of the whole preceding document, not a
riddle answer. The operation is creator-native (sha256 -> key, sha-256(password)); only the choice
of object is imported. Prior is low: every solved-stage password was a riddle answer.

Pre-registered in intake/2026-09-26-ricardian/PREREG.md, committed before this run. The six objects
are whole and byte-exact; the solved-stage plaintexts are re-derived here by decrypting the in-repo
ciphertexts with their known passwords and must equal the saved files byte for byte.

Per object: the frozen gate path on raw bytes (16 decrypts), the P32T freeze, campaign 51's padding-independent
scan, and addr_check's fixed encodings vs prize / 17ucy1 / 1NULY7.

  python3 campaign_54_ricardian_docs.py
"""
import base64, hashlib, json, os, sys, time
import gate, aes_try, btc_addr, p32t_freeze, addr_check
from campaign_51_padding_independent import scan

REPO = os.path.join(gate.NEO, "..")
OUT = os.path.join(gate.NEO, "attempts", "campaign_54_ricardian_docs.jsonl")
PHASE22 = ("causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F63657320666F206B"
           "6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854"
           "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1")
SOLVED = [  # (object id, ciphertext file, password, saved plaintext file)
    ("O1", "phase2-assets/phase2_aes.txt", "causality", "phase2-assets/phase2.1.txt"),
    ("O2", "phase2-assets/phase3_aes.txt", PHASE22, "phase2-assets/phase3.txt"),
    ("O3", "phase3-assets/phase3.2-aes.txt", "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
     "neo/materials/phase32_plaintext_outer.txt"),
]
SOUP = "neo/materials/primary/salphaseion_soup_space_separated.txt"
CIRCULAR = {("O3", "inner96"), ("O5", "miniA"), ("O5", "miniAB")}   # object contains that lock's ciphertext

def rd(rel): return open(os.path.join(REPO, rel), "rb").read()

def solve(ct_file, pw):
    """Decrypt a solved blob with sha256hex(pw) under EVP-SHA256 (the creator's convention), unpadded."""
    raw = base64.b64decode(b"".join(rd(ct_file).split()))
    assert raw[:8] == b"Salted__"
    key, iv = aes_try.evp_bytes_to_key(hashlib.sha256(pw.encode()).hexdigest().encode(), raw[8:16], "sha256", 32)
    pt = aes_try.decrypt(raw[16:], key, iv)
    return pt[:-pt[-1]]

def objects():
    obj = {}
    for oid, ct, pw, saved in SOLVED:
        pt = solve(ct, pw)
        assert pt == rd(saved), f"{oid}: re-derived plaintext differs from {saved}"
        obj[oid] = pt
    i = obj["O3"].find(b"U2FsdGVkX1")
    assert i == 2292, i
    obj["O4a"] = obj["O3"][:i]
    obj["O4b"] = obj["O3"][:i].rstrip()
    obj["O5"] = rd(SOUP)
    assert hashlib.sha256(obj["O5"]).hexdigest().startswith("d39d10b1")
    want = {"O1": 648, "O2": 4090, "O3": 2422, "O4a": 2292, "O4b": 2288, "O5": 2149}
    assert {k: len(v) for k, v in obj.items()} == want, {k: len(v) for k, v in obj.items()}
    return obj

def run_decrypts_bytes(doc, targets):
    """gate.run_decrypts on bytes: same forms, KDFs, targets and check. The gate takes str and
    encodes UTF-8, which cannot carry O3 unchanged (it holds a non-UTF-8 byte)."""
    out = []
    for form in gate.FORMS:
        pw = doc if form == "raw" else hashlib.sha256(doc).hexdigest().encode()
        for kdf in gate.KDFS:
            md, keylen = aes_try.KDFS[kdf]
            for tname in gate.TARGETS:
                t = targets[tname]
                key, iv = aes_try.evp_bytes_to_key(pw, t["salt"], md, keylen)
                res = aes_try.check_pt(aes_try.decrypt(t["ct"], key, iv))
                rec = {"form": form, "kdf": kdf, "target": tname, "pad": None, "hit": False}
                if res:
                    rec.update(pad=res["pad"], printable=res["printable"], hit=res["hit"])
                    if res["hit"]:
                        rec["body_head"] = res["body"][:200].decode("latin1")
                        rec["body_addr"] = gate.body_addresses(res["body"])
                out.append(rec)
    return out

def main():
    assert (aes_try.self_test() and btc_addr.self_test() and p32t_freeze.self_test()
            and addr_check.self_test()), "self-test failed"
    obj = objects()
    targets = aes_try.load_targets(); t32 = targets["inner96"]
    addr_matches = addr_check.check([(k, v) for k, v in obj.items()])
    tot = pads = hits = 0
    with open(OUT, "w") as f:
        for oid, doc in obj.items():
            dec = run_decrypts_bytes(doc, targets)
            frz, pind = [], []
            for form in gate.FORMS:
                pw = doc if form == "raw" else hashlib.sha256(doc).hexdigest().encode()
                for kdf in gate.KDFS:
                    md, kl = aes_try.KDFS[kdf]
                    key, _ = aes_try.evp_bytes_to_key(pw, t32["salt"], md, kl)
                    if p32t_freeze.primary_ok(key) or p32t_freeze.secondary_ok(key):
                        frz.append((form, kdf))
                    for tname in gate.TARGETS:
                        t = targets[tname]
                        k, iv = aes_try.evp_bytes_to_key(pw, t["salt"], md, kl)
                        for where, (which, addr) in scan(aes_try.decrypt(t["ct"], k, iv)):
                            pind.append((form, kdf, tname, where, which, addr))
            am = [m for m in addr_matches if m[0] == oid]
            near = [r for r in dec if r["pad"]]
            h = any(r["hit"] for r in dec) or bool(frz) or bool(pind) or bool(am)
            tot += len(dec); pads += len(near); hits += h
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "object": oid,
                                "bytes": len(doc), "sha256": hashlib.sha256(doc).hexdigest(),
                                "circular_with": sorted(t for o, t in CIRCULAR if o == oid),
                                "decrypts": dec, "freeze": frz, "padding_independent": pind,
                                "addr_matches": am, "HIT": h}) + "\n")
            print(f"{oid:4s} {len(doc):5d} B sha256 {hashlib.sha256(doc).hexdigest()[:16]}…  pad={len(near)} "
                  f"freeze={frz or '-'} pind={len(pind)} addr={len(am)} HIT={h}")
    print(f"\nobjects={len(obj)} decrypts={tot} pkcs7_any={pads} hits={hits}")
    print("*** HIT ***" if hits else "null. No whole puzzle document, hashed or raw, opens a lock or derives "
          "a target address; the Ricardian reading is closed per the pre-registration.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
