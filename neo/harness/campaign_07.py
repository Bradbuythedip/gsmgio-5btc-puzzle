#!/usr/bin/env python3
"""Campaign 07: literal "intertwined" (char interleave) of the seven components,
mod-26 Beaufort/Vigenere decodes of head/faed as passwords, reinsert-primes,
halving numbers, 1357 family.
"""
import hashlib, itertools, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT
from campaign_01 import msl_variants

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

def interleave(strings, mode="pad"):
    out = []
    n = max(len(s) for s in strings)
    for i in range(n):
        for s in strings:
            if i < len(s):
                out.append(s[i])
        if mode == "cut" and any(i + 1 >= len(s) for s in strings):
            break
    return "".join(out)

page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
head = page[:ab[0][0]]
rest = page[ab[0][1]:]
faed = rest[:rest.index('z')]

def vig26(s, key, beaufort=False):
    out = []
    kv = [ord(c) - 97 for c in key]
    for i, c in enumerate(s):
        cv = ord(c) - 97
        k = kv[i % len(kv)]
        p = (k - cv) % 26 if beaufort else (cv - k) % 26
        out.append(chr(97 + p))
    return "".join(out)

def main():
    h = Harness("campaign_07")
    msl = msl_variants()

    LAB = ["yellow", "blue", "primes", "matrixsumlist",
           "lastwordsbeforearchichoice", "yinyang", "thepassword"]
    VAL = ["0", "1", "2357", msl["rowsums"], "hope", "yinyang", "thispassword"]
    SHAS = [sha(x) for x in LAB]
    SHAV = [sha(x) for x in VAL]

    for name, toks in (("lab", LAB), ("val", VAL), ("shalab", SHAS), ("shaval", SHAV)):
        for mode in ("pad", "cut"):
            h.try_family(interleave(toks, mode), f"intertwine:{name}:{mode}")
    # pairwise intertwines of key duos
    for a, b in (("half", "betterhalf"), ("yin", "yang"), ("yellow", "blue"),
                 ("matrixsumlist", "thepassword"),
                 (sha("half"), sha("betterhalf")), (sha("yin"), sha("yang"))):
        for mode in ("pad", "cut"):
            h.try_family(interleave([a, b], mode), f"intertwine2:{mode}")

    # mod-26 cipher outputs as passwords (and their sha-b4 family)
    KEYS = ["thematrixhasyou", "matrixsumlist", "causality", "yinyang", "salvation",
            "followthewhiterabbit", "cosmicduality", "salphaseion"]
    for k in KEYS:
        for blk, bn in ((head, "head"), (faed, "faed")):
            for bf in (False, True):
                h.try_family(vig26(blk, k, bf), f"mod26:{bn}:{k}:{'beau' if bf else 'vig'}")

    # reinsert the prime basics
    rows = msl["rowsums"]
    h.try_family("2357" + rows, "reinsert:pre")
    h.try_family(rows + "2357", "reinsert:post")
    lst = list(rows)
    for p in (2, 3, 5, 7):
        if p <= len(lst):
            lst.insert(p - 1, str(p))
    h.try_family("".join(lst), "reinsert:atprimes")

    # halving / 1357 family
    for s in ("1357", "13571357", "840000", "630000", "630000840000", "1357blockstogo",
              "blockstogo", "happyhalving", "seeyouin4years", "obscure", "obscureintel",
              "20200511", "20240419", "05112020", "19042024", "11052020"):
        h.try_family(s, "halving/1357")
    for p in itertools.permutations("1357"):
        h.try_family("".join(p), "1357perm")

    h.finish("campaign_07")

if __name__ == "__main__":
    main()
