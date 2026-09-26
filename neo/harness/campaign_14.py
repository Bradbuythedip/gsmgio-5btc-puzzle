#!/usr/bin/env python3
"""Campaign 14: the creator-authenticated recipe.

From the 445-message creator log (primary material):
  #6509 - asked for a hint on 'matrixsumlist', he points back at #5966, the PRIME part.
          So the prime hint IS the matrixsumlist hint.
  #5966 - reply to "which primes, 2,3,5,7?" -> "You are at the prime part already???"
  #8000 - "prime numbers ... required to proceed ... some characters need to be zeroed out"
  #39237 - yinyang is the NEXT PHASE reached AFTER decrypting an AES ciphertext,
           so yinyang is output, NOT a password input. (Earlier campaigns wrongly fed it in.)
  2023-02-23 master hint order: yellowblueprimes matrixsumlist lastwordsbeforearchichoice yinyang

So the password is built from the first three, and decrypting should yield yinyang.
matrixsumlist = sums of a matrix with characters zeroed out at prime-derived positions.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT

page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
head = page[:ab[0][0]]
rest = page[ab[0][1]:]
faed = rest[:rest.index('z')]

def sieve(n):
    s = [True]*(n+1); s[0] = s[1] = False
    for i in range(2, int(n**.5)+1):
        if s[i]: s[i*i::i] = [False]*len(s[i*i::i])
    return {i for i, b in enumerate(s) if b}
P = sieve(600)

BLOCKS = [("dbbi", head)] + [(f"faed{i+1}", faed[i*91:(i+1)*91]) for i in range(6)]

MASKS = {
    "zp":   lambda i, r, c: (i+1) in P,            # zero at prime position
    "kp":   lambda i, r, c: (i+1) not in P,        # keep only prime positions
    "zc57": lambda i, r, c: (c+1) in {2, 3, 5, 7},
    "zcp":  lambda i, r, c: (c+1) in P,
    "kcp":  lambda i, r, c: (c+1) not in P,
    "zrp":  lambda i, r, c: (r+1) in P,
    "krp":  lambda i, r, c: (r+1) not in P,
    "zrc":  lambda i, r, c: (r+1) in P and (c+1) in P,
    "z0":   lambda i, r, c: False,                 # no mask (control)
}

def sumlists(block, mask, base1):
    v = [ord(ch) - (96 if base1 else 97) for ch in block]
    g = [[v[r*13+c] for c in range(13)] for r in range(7)]
    for r in range(7):
        for c in range(13):
            if mask(r*13+c, r, c): g[r][c] = 0
    cs = [sum(g[r][c] for r in range(7)) for c in range(13)]
    rs = [sum(row) for row in g]
    return cs, rs

def render(nums):
    return [
        "".join(map(str, nums)), " ".join(map(str, nums)), ",".join(map(str, nums)),
        "".join(chr(65+(x-1) % 26) for x in nums),
        "".join(chr(97+(x-1) % 26) for x in nums),
        "".join(chr(65+x % 26) for x in nums),
        "".join(chr(97+x % 26) for x in nums),
        str(sum(nums)),
    ]

YBP = ["yellowblueprimes", "", "01", "2357", "012357", "yellowblue", "primes",
       "0123571113", "yellowbluep rimes".replace(" ", "")]
LWBA = ["", "lastwordsbeforearchichoice", "hope", "ciaobella", "ciaobellao",
        "ireallyhopeyouretheone", "goodluck", "thesource", "returntothesource",
        "youllneverfinishthelasttask", "denialisthemostpredictableofallhumanresponses",
        "theproblemischoice", "everythingthathasabeginninghasanend"]

def main():
    h = Harness("campaign_14")
    msl = []
    for bn, b in BLOCKS:
        for mn, mf in MASKS.items():
            for base1 in (True, False):
                cs, rs = sumlists(b, mf, base1)
                for axis, nums in (("c", cs), ("r", rs)):
                    for s in render(nums):
                        msl.append((f"{bn}:{mn}:b{int(base1)}:{axis}", s))
    print("matrixsumlist candidates:", len(msl))

    # 1) matrixsumlist alone
    for tag, s in msl:
        h.try_family(s, f"msl:{tag}")

    # 2) with the other two authenticated components around it
    for tag, s in msl:
        for y in YBP:
            for l in LWBA:
                if not y and not l:
                    continue
                h.try_pw(y + s + l, f"triple:{tag}")
                import hashlib
                h.try_pw(hashlib.sha256((y + s + l).encode()).hexdigest(), f"triple-sha:{tag}")
    h.finish("campaign_14")

if __name__ == "__main__":
    main()
