#!/usr/bin/env python3
"""Campaign 43: item E residue, pre-registered in
intake/2026-09-26-itemE/PREREG.md. Uses gate.py's frozen functions unchanged."""
import json, time, os
import gate, aes_try, btc_addr, p32t_freeze

BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
CANDIDATES = [
    "",
    "b45a5e3d827593ca",
    "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
    "HALFANDBETTERHALF",
]
OUT = os.path.join(gate.NEO, "attempts", "campaign_43_itemE.jsonl")

assert aes_try.self_test() and btc_addr.self_test(), "self-test failed"
targets = aes_try.load_targets()
t = targets["inner96"]
tot = pads = hits = 0
with open(OUT, "w") as f:
    for c in CANDIDATES:
        dec = gate.run_decrypts(c, targets)
        sca = gate.run_scalars(c)
        k = int(gate.sha256hex(c), 16)
        comp, unc = btc_addr.addrs(k)
        better = BETTER in (comp, unc)
        prize = gate.PRIZE in (comp, unc)
        frz = []
        for form in gate.FORMS:
            pw = c if form == "raw" else gate.sha256hex(c)
            for kdf in gate.KDFS:
                md, kl = aes_try.KDFS[kdf]
                key, iv = aes_try.evp_bytes_to_key(pw.encode(), t["salt"], md, kl)
                if p32t_freeze.primary_ok(key) or p32t_freeze.secondary_ok(key):
                    frz.append((form, kdf))
        n = [r for r in dec if r["pad"]]
        h = any(r["hit"] for r in dec) or prize or better or bool(frz)
        tot += len(dec); pads += len(n); hits += h
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "candidate": c, "decrypts": dec, "scalars": sca, "addr_comp": comp,
            "addr_unc": unc, "better": better, "prize": prize, "freeze": frz, "HIT": h}) + "\n")
        print(f"{c!r:58s} pad={len(n)} freeze={frz or '-'} prize={prize} better={better} HIT={h}")
        for r in n: print("    ", json.dumps(r)[:200])
print(f"\ndecrypts={tot} pkcs7_any={pads} hits={hits}")
