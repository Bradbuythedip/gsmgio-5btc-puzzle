#!/usr/bin/env python3
"""Campaign 50: the curated-pool meet-in-the-middle re-run (audit finding G1).

Tick 37 ran the correct point-collision MITM (a+b, a-b, a*b vs the prize point Q) but over a
pool that lowercases and 4-word-caps everything, so it was MISSING: the S1-S4 seed scalars and
their C1-C6 constructions, most canonical answer strings, mixed-case / >4-word phrases, the
layer-sum numeric concatenations, YOUWON, yinyang, and the three salts. This adds all of those
to the pool and re-runs. MITM is O(pool) (one point table, one op per element), so the additions
are nearly free.

Phase 1: add/sub/mul over full pool + curated additions, vs Q.
Phase 2 (three-way, G2): for each c in a small curated offset set, add-MITM on Q - c*G, i.e.
         test k = a + b + c and a - b + c. Matches the creator's demonstrated vanity offsets.

Predicate: point collision proving a scalar whose point is Q (i.e. derives the prize address).
No AES. S1-S4 provenance is undocumented (prior session took them as given); their inclusion is
a bounded completeness check, not a claim they are authenticated.

  python3 campaign_50_mitm_curated.py
"""
import hashlib, json, os, sys, time
import coincurve
from coincurve import PublicKey
import mitm_halves as M

N = M.N
NEO = M.NEO
OUT = os.path.join(NEO, "attempts", "campaign_50_mitm_curated.jsonl")
QX = 0xf4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464
QY = 0x9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559
Q = PublicKey(b"\x04" + QX.to_bytes(32, "big") + QY.to_bytes(32, "big"))

# --- S1-S4 seeds (prior-sessions) and C1-C6 constructions ---
S = {1: "223e3dea019fd03dc730467abfcc068bd329b222cfbe2fa71339ac57d25ef545",
     2: "376103f4bd0300b073ffc8fc70d132b3f1c3ccd90ace4e0fe4fbb183cb66bd51",
     3: "748a3ea15dc34e20c58e11e7407740904d9011debc9846b0b7a6dab54ad85123",
     4: "b49c87570a54e14d6af2790924059ff859f345eaf09641c64734c66c190bdc75"}
def _sha(x): return hashlib.sha256(x).digest()
def seed_scalars():
    out = {}
    for i, h in S.items():
        raw = bytes.fromhex(h)
        out[f"S{i}:C1 raw-int"] = int(h, 16) % N
        out[f"S{i}:C2 sha256(hexascii)"] = int.from_bytes(_sha(h.encode()), "big") % N
        out[f"S{i}:C3 sha256(raw)"] = int.from_bytes(_sha(raw), "big") % N
        out[f"S{i}:C4 sha256d(raw)"] = int.from_bytes(_sha(_sha(raw)), "big") % N
        out[f"S{i}:C5 sha256(raw-rev)"] = int.from_bytes(_sha(raw[::-1]), "big") % N
        out[f"S{i}:C6 sha256(HEXUP)"] = int.from_bytes(_sha(h.upper().encode()), "big") % N
    return out

ANSWERS = [
    "causality", "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "thematrixhasyou", "theseedisplanted", "gsmg.io/theseedisplanted", "followthewhiterabbit",
    "matrixsumlist", "thispassword", "thepassword", "yourlastcommand", "secondanswer",
    "lastwordsbeforearchichoice", "yinyang", "yingyang", "yellowblueprimes",
    "youwon", "YOUWON", "halfandbetterhalf", "betterhalf", "half", "enter",
    "shabefourfirsthintisyourlastcommand", "verylaststepisatruegiveawaypromised",
    "wewontgiveawaythepassword", "itsinfrontofyoureyesbutyourenotseeingit",
    "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
    "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
    "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangthepassword",
]
NUMERIC = ["331360369421418441396", "331 360 369 421 418 441 396", "396441418421369360331",
           "42", "3173", "31 73", "104", "661"]
SALTS = ["b45a5e3d827593ca", "3ab585348552415d", "2d3f6fe06dc950e6"]

def curated():
    pool = {}
    def add(k, lbl):
        if 0 < k % N: pool.setdefault(k % N, lbl)
    for lbl, k in seed_scalars().items():
        add(k, lbl)
    for s in ANSWERS + NUMERIC:
        add(int.from_bytes(hashlib.sha256(s.encode()).digest(), "big"), "sha256:" + s[:60])
    for s in NUMERIC:
        if s.isdigit(): add(int(s), "int:" + s)
    for h in SALTS:
        add(int.from_bytes(hashlib.sha256(h.encode()).digest(), "big"), "sha256salt:" + h)
        add(int(h, 16), "hexsalt:" + h)
    return pool

def main():
    pass
    base = M.build_pool()
    cur = curated()
    new = {k: v for k, v in cur.items() if k not in base}
    pool = dict(base); pool.update(new)
    print(f"base pool {len(base)}  curated additions {len(cur)} ({len(new)} new)  total {len(pool)}")

    hits = []
    t = time.time()
    h1 = M.mitm(Q, pool)
    print(f"phase 1 (add/sub/mul vs Q): {len(pool)} scalars in {time.time()-t:.0f}s -> {h1 or 'no hit'}")
    hits += [("2way",) + h for h in h1]

    # phase 2: three-way, small curated offset set
    offs = curated()
    t = time.time(); scanned = 0
    for c, lbl in offs.items():
        Pc = PublicKey.combine_keys([Q, M.point((N - c) % N)])   # Q - cG
        for op, hh in (("add", M.mitm(Pc, pool, ops=("add",))), ("sub", M.mitm(Pc, pool, ops=("sub",)))):
            for h in hh:
                hits.append(("3way c=" + lbl, op) + h)
        scanned += 1
    print(f"phase 2 (three-way, {scanned} offsets): {time.time()-t:.0f}s -> "
          f"{[x for x in hits if x[0].startswith('3way')] or 'no hit'}")

    with open(OUT, "w") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "base_pool": len(base), "curated_new": len(new), "total_pool": len(pool),
                            "three_way_offsets": scanned, "HIT": bool(hits), "hits": [list(x) for x in hits]}) + "\n")
    print("*** HIT ***" if hits else "null: no half±better / half·better / three-way relation to the prize point.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
