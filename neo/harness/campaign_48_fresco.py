#!/usr/bin/env python3
"""Campaign 48: Fresco / "Looking Forward" adjacent strings, pre-registered in
intake/2026-09-26-fresco/PREREG.md. Frozen decrypt path via gate.py; no widening."""
import json, os, time
import gate, aes_try, btc_addr

BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
CANDIDATES = ["jacquefrescolookingforward", "thebestthatmoneycantbuy", "The Best That Money Can't Buy",
              "sociocyberneering", "Sociocyberneering", "resourcebasedeconomy", "resource-based economy",
              "futurebydesign", "Future by Design", "self-erectingstructures", "cybernetics",
              "nothinghastobechangedonlyrediscovered"]
OUT = os.path.join(gate.NEO, "attempts", "campaign_48_fresco.jsonl")

assert aes_try.self_test() and btc_addr.self_test(), "self-test failed"
targets = aes_try.load_targets()
tot = pads = hits = 0
with open(OUT, "w") as f:
    for c in CANDIDATES:
        dec = gate.run_decrypts(c, targets)
        sca = gate.run_scalars(c)
        comp, unc = btc_addr.addrs(int(gate.sha256hex(c), 16))
        better = BETTER in (comp, unc); prize = gate.PRIZE in (comp, unc)
        near = [r for r in dec if r["pad"]]
        h = any(r["hit"] for r in dec) or prize or better
        tot += len(dec); pads += len(near); hits += h
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "candidate": c,
                            "decrypts": dec, "scalars": sca, "prize": prize, "better": better, "HIT": h}) + "\n")
        print(f"{c!r:42s} pad={len(near)} prize={prize} better={better} HIT={h}")
        for r in near:
            print("    ", json.dumps(r)[:200])
print(f"\ndecrypts={tot} pkcs7_any={pads} hits={hits}")
print("*** HIT ***" if hits else "null. Fresco / Looking Forward direction closed.")
