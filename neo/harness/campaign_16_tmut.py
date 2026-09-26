#!/usr/bin/env python3
"""Campaign 16: the single-'t' mutation family, with a mandatory positive control.

Design per the proposed protocol: only three mutation classes per source string -
unchanged, delete exactly one existing 't', insert exactly one 't'. No synonyms, no
case folding, no punctuation edits, no multiple mutations. Tier 1 = positions adjacent
to an existing 't'/'it' (the demonstrated defect class); Tier 2 = every boundary,
labelled separately as the weaker general family.

Success rule: PKCS#7 is diagnostic only. A hit must additionally satisfy a predeclared
structural criterion (printable coherent text or a known magic prefix). A lone 0x01 tail
is logged and ignored - that is what aes_try's check_pt already enforces via `hit`.
"""
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, evp_bytes_to_key, decrypt, check_pt, load_targets

P32_PW = "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"

def control():
    """giveit spelling must open Phase 3.2; givetit must not."""
    import base64
    repo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    raw = base64.b64decode("".join(open(os.path.join(repo, "phase3-assets/phase3.2-aes.txt")).read().split()))
    salt, ct = raw[8:16], raw[16:]
    out = {}
    for label, pw in (("giveit (correct)", P32_PW),
                      ("givetit (extra t)", P32_PW.replace("giveit", "givetit"))):
        h = hashlib.sha256(pw.encode()).hexdigest()
        k, iv = evp_bytes_to_key(h.encode(), salt, "sha256", 32)
        r = check_pt(decrypt(ct, k, iv))
        ok = bool(r and r["hit"])
        out[label] = ok
        print(f"  {label:20s} -> {'PASS' if ok else 'FAIL'}"
              + (f"  {r['body'][:46]!r}" if ok else ""))
    return out

def t_variants(s, tier1_only):
    """unchanged + delete-one-t + insert-one-t (tier1: adjacent to existing t/it)."""
    v = {s}
    for i, c in enumerate(s):
        if c == 't':
            v.add(s[:i] + s[i+1:])
    if tier1_only:
        pos = set()
        for i, c in enumerate(s):
            if c == 't':
                pos.add(i); pos.add(i+1)
            if s[i:i+2] == 'it':
                pos.add(i+1); pos.add(i+2)
        for p in sorted(pos):
            if 0 <= p <= len(s):
                v.add(s[:p] + 't' + s[p:])
    else:
        for p in range(len(s) + 1):
            v.add(s[:p] + 't' + s[p:])
    return v

CORPUS = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "yellowblueprimes", "yinyang", "thepassword", "shabefourfirsthintisyourlastcommand",
    "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive",
    "returntothesourcecodes", "reinsertingtheprimebasics",
    "allowingatemporarydisseminationofthecodeyouhopefullycarry",
    "sevenintertwinedpasswords", "twentythreecipherssixteenencryptions",
    "ireallyhopeyouretheone", "ciaobellao", "goodlucknevertheless",
    P32_PW, "giveitjustonesecond", "theflowerblossomsthroughwhatseemstobeaconcretesurface",
]

def main():
    print("=== MANDATORY POSITIVE CONTROL ===")
    c = control()
    assert c["giveit (correct)"] and not c["givetit (extra t)"], "control failed - harness invalid"
    print("  control OK: harness models the historical typo bypass correctly.\n")

    for tier, only in (("tier1-adjacent", True), ("tier2-allboundaries", False)):
        h = Harness(f"campaign_16_{tier}")
        n = 0
        for s in CORPUS:
            for v in t_variants(s, only):
                h.try_family(v, f"tmut:{tier}")
                n += 1
        print(f"\n[{tier}] variants generated: {n}")
        h.finish(f"campaign_16_{tier}")

if __name__ == "__main__":
    main()
