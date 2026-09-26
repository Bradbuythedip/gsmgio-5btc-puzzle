#!/usr/bin/env python3
"""Campaign 52: the natural last-words phrases decrypted BARE (audit finding, soup agent).

The soup grammar sequences "...lastwordsbeforearchichoice thispassword enter <envelope>", i.e. it
designates the password as "the last words before the architect's choice". The Architect speech
(phase3.2.ipynb) ends: "...the extinction of the entireness of yourself self good luck nevertheless
i really hope youre the one ciao bella o". campaign_32 tested only arbitrary 48/96-char cuts of the
last words; the NATURAL phrases were only ever refused by gate.py as "corpus-present" (their
normalized form occurs in the ledger/ipynb) and were NEVER actually decrypted. Verified: they
appear in 0 attempts/*.jsonl. This closes that gate-hygiene gap by decrypting them bare.

Frozen decrypt path (raw + sha256hex, EVP-MD5/SHA256, all four locks) + strict pad + P32T freeze
+ prize/17ucy1 scalar. No new vocabulary beyond the phrases the soup itself names.

  python3 campaign_52_lastwords_bare.py
"""
import hashlib, json, os, sys, time
import gate, aes_try, btc_addr, p32t_freeze

BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
OUT = os.path.join(gate.NEO, "attempts", "campaign_52_lastwords_bare.jsonl")

# the natural last-words phrases (from the Architect ending) + literal soup instructions
CANDIDATES = [
    "goodluckneverthelessireallyhopeyouretheoneciaobellao",
    "theextinctionoftheentirenessofyourselfselfgoodluckneverthelessireallyhopeyouretheoneciaobellao",
    "theextinctionoftheentirenessofyourselfself",
    "ireallyhopeyouretheone", "hopeyouretheone", "youretheone", "theoneciaobellao",
    "ciaobellao", "ciaobella", "goodluck", "goodlucknevertheless",
    "yourlastcommand", "firsthintisyourlastcommand", "shabefanstoo",
]

def main():
    assert aes_try.self_test() and btc_addr.self_test() and p32t_freeze.self_test(), "self-test failed"
    targets = aes_try.load_targets(); t32 = targets["inner96"]
    tot = pads = hits = 0
    with open(OUT, "w") as f:
        for c in CANDIDATES:
            dec = gate.run_decrypts(c, targets)
            comp, unc = btc_addr.addrs(int(gate.sha256hex(c), 16))
            prize = gate.PRIZE in (comp, unc); better = BETTER in (comp, unc)
            frz = []
            for form in gate.FORMS:
                pw = c if form == "raw" else gate.sha256hex(c)
                for kdf in gate.KDFS:
                    md, kl = aes_try.KDFS[kdf]
                    key, iv = aes_try.evp_bytes_to_key(pw.encode(), t32["salt"], md, kl)
                    if p32t_freeze.primary_ok(key) or p32t_freeze.secondary_ok(key):
                        frz.append((form, kdf))
            near = [r for r in dec if r["pad"]]
            h = any(r["hit"] for r in dec) or prize or better or bool(frz)
            tot += len(dec); pads += len(near); hits += h
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "candidate": c,
                                "decrypts": dec, "prize": prize, "better": better, "freeze": frz, "HIT": h}) + "\n")
            print(f"{c[:52]!r:56s} pad={len(near)} freeze={frz or '-'} prize={prize} HIT={h}")
    print(f"\ndecrypts={tot} pkcs7_any={pads} hits={hits}")
    print("*** HIT ***" if hits else "null. The natural last-words phrases open no lock; gate-hygiene gap closed.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
