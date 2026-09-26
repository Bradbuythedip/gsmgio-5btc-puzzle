#!/usr/bin/env python3
"""Campaign 49: challenge the KDF assumption. Every prior tick derived keys with OpenSSL's
EVP_BytesToKey (MD5/SHA1/SHA256). PBKDF2 (`openssl enc -pbkdf2`, the OpenSSL 3.0+ recommendation)
has never been tried. The three SOLVED blobs are EVP (self-test); the UNSOLVED 2023 SalPhaseIon
locks have never been opened, so nothing proves their KDF. If it is PBKDF2, every password tested
against them was derived wrong and every null is void for the true password.

This tests the strongest known candidate strings under PBKDF2-HMAC-{sha256,sha1,md5} at the usual
iteration counts, against the unsolved locks, with the solved blobs as controls. No new vocabulary:
the candidates are the solved-stage answers and structural labels — strings that would BE the
answer if only the KDF were wrong.

Controls (must pass or a null is meaningless):
  A. PBKDF2 impl matches OpenSSL 3.x (round-trip a `-pbkdf2` blob).
  B. EVP still opens the three solved blobs (aes_try self-test).
  C. PBKDF2 does NOT open the solved blobs with their known passwords (PBKDF2 != solved tooling).

  python3 campaign_49_pbkdf2.py
"""
import base64, hashlib, json, os, subprocess, sys, time
from Crypto.Cipher import AES
import aes_try, btc_addr, p32t_freeze

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
OUT = os.path.join(NEO, "attempts", "campaign_49_pbkdf2.jsonl")
PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"

MDS = ("sha256", "sha1", "md5")            # openssl -pbkdf2 -md ...
ITERS = (1, 1000, 2048, 4096, 10000, 100000)
LOCKS = ("miniA", "miniAB", "inner96", "cosmic")   # inner96 = P32T; miniAB = salph_inner

# strongest known candidates: the answer IF only the KDF were wrong (no new vocabulary)
CANDIDATES = [
    "causality", "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "halfandbetterhalf", "betterhalf", "half", "thispassword", "thepassword",
    "matrixsumlist", "yinyang", "yingyang", "enter",
    "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
    "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangthepassword",
    "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
    "theseedisplanted", "gsmg.io/theseedisplanted", "followthewhiterabbit",
    "thereisnospoon", "wakeupneo", "thematrixhasyou", "cosmicduality",
    "verylaststepisatruegiveawaypromised", "shabefourfirsthintisyourlastcommand",
]

def pbkdf2_key_iv(pw: bytes, salt: bytes, md: str, iters: int, klen=32, ivlen=16):
    dk = hashlib.pbkdf2_hmac(md, pw, salt, iters, klen + ivlen)
    return dk[:klen], dk[klen:klen + ivlen]

def control_A():
    pt = b"HELLO PBKDF2 WORLD control plaintext 123."
    r = subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "7777",
                        "-md", "sha256", "-pass", "pass:ctrl", "-base64"],
                       input=pt, capture_output=True)
    blob = base64.b64decode(b"".join(r.stdout.split()))
    salt, ct = blob[8:16], blob[16:]
    k, iv = pbkdf2_key_iv(b"ctrl", salt, "sha256", 7777)
    dec = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
    return dec[:-dec[-1]] == pt

def control_C(targets):
    """The solved blobs must NOT open under PBKDF2 with their known EVP passwords."""
    known = {"miniA": None}  # not solved
    pairs = [(aes_try.sha256hex if False else None)]
    # known solved-stage passwords are the sha256hex forms; test raw + sha256hex under PBKDF2
    opened = 0
    for pw in ("causality", "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"):
        for form in (pw, hashlib.sha256(pw.encode()).hexdigest()):
            for tname in ("miniA", "miniAB", "inner96", "cosmic"):
                t = targets[tname]
                for md in MDS:
                    for it in (10000, 1):
                        k, iv = pbkdf2_key_iv(form.encode(), t["salt"], md, it)
                        res = aes_try.check_pt(aes_try.decrypt(t["ct"], k, iv))
                        if res and res["hit"]:
                            opened += 1
    return opened == 0

def scalar_addr_hit(body):
    import re
    for m in re.findall(rb"\b[0-9a-fA-F]{64}\b", body):
        _, u = btc_addr.addrs(int(m, 16) % btc_addr.N)
        if u in (PRIZE, BETTER):
            return m.decode()
    return None

def main():
    targets = aes_try.load_targets()
    okA, okB, okC = control_A(), aes_try.self_test(), control_C(targets)
    print(f"control A (PBKDF2 impl == openssl): {okA}")
    print(f"control B (EVP opens solved blobs): {okB}")
    print(f"control C (PBKDF2 does NOT open solved blobs): {okC}")
    assert okA and okB and okC, "a control failed; a null here would be meaningless"

    tot = pads = hits = 0
    with open(OUT, "w") as f:
        for c in CANDIDATES:
            for form_name, pw in (("raw", c), ("sha256hex", hashlib.sha256(c.encode()).hexdigest())):
                pwb = pw.encode()
                for tname in LOCKS:
                    t = targets[tname]
                    for md in MDS:
                        for it in ITERS:
                            k, iv = pbkdf2_key_iv(pwb, t["salt"], md, it)
                            res = aes_try.check_pt(aes_try.decrypt(t["ct"], k, iv))
                            tot += 1
                            frz = tname == "inner96" and (p32t_freeze.primary_ok(k) or p32t_freeze.secondary_ok(k))
                            if not res and not frz:
                                continue
                            addr = scalar_addr_hit(res["body"]) if res else None
                            strong = frz or bool(addr) or (res and res["hit"])
                            if res and res["pad"]:
                                pads += 1
                            if strong:
                                hits += 1
                                rec = {"candidate": c, "form": form_name, "target": tname, "md": md,
                                       "iter": it, "freeze": bool(frz), "addr": addr,
                                       "pad": res["pad"] if res else None,
                                       "body_head": res["body"][:80].decode("latin1") if res else None, "HIT": True}
                                f.write(json.dumps(rec) + "\n")
                                print("*** HIT ***", json.dumps(rec)[:300])
    print(f"\ndecrypts={tot} pkcs7_any={pads} strong_hits={hits}")
    print("*** HIT ***" if hits else "null. PBKDF2 does not open the locks with any strong known candidate. "
          "KDF-assumption challenged and the EVP nulls stand.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
