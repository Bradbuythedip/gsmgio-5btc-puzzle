#!/usr/bin/env python3
"""Campaign 19: the 24-primes / 24-colours alignment on dbbi.

Parameter-free structural alignment:
  dbbi is 91 symbols; there are exactly 24 primes <= 91; there are exactly 24 coloured
  cells (15 blue, 9 yellow). So the 24 colour bits map one-to-one onto the 24 prime
  positions of dbbi. That is "yellowblueprimes" plus "some characters need to be zeroed
  out" as a single instruction with nothing free to tune.

Variants are only the unavoidable conventions: index base, which colour zeroes, digit base,
axis, letter rendering. Also tested: the same mask on faed's seven 7x13 matrices, and the
mask applied additively rather than as replacement ("add, not replace").
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT

d = json.load(open(os.path.join(MAT, "primary", "matrix_grid_spiral_colors.json")))
spiral = [tuple(x) for x in d["spiral"]]; idx = {c: i for i, c in enumerate(spiral)}
BI = sorted(idx[tuple(c)] for c in d["blue"]); YI = sorted(idx[tuple(c)] for c in d["yellow"])
ALL = sorted(BI + YI)
SEQ = "".join('B' if i in BI else 'Y' for i in ALL)

page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
dbbi = page[:ab[0][0]]; rest = page[ab[0][1]:]; faed = rest[:rest.index('z')]
BLOCKS = [("dbbi", dbbi)] + [(f"faed{i+1}", faed[i*91:(i+1)*91]) for i in range(6)]

def sieve(n):
    s = [True]*(n+1); s[0] = s[1] = False
    for i in range(2, int(n**.5)+1):
        if s[i]: s[i*i::i] = [False]*len(s[i*i::i])
    return [i for i, b in enumerate(s) if b]
P91 = sieve(91)

def render(nums):
    return ["".join(map(str, nums)), " ".join(map(str, nums)), ",".join(map(str, nums)),
            "".join(chr(65+(x-1) % 26) for x in nums),
            "".join(chr(97+(x-1) % 26) for x in nums),
            "".join(chr(65+x % 26) for x in nums),
            str(sum(nums))]

def main():
    h = Harness("campaign_19")
    n = 0
    for bname, blk in BLOCKS:
        for base in (0, 1):
            for zc in ('Y', 'B'):
                for b1 in (True, False):
                    for mode in ("zero", "add", "sub"):
                        v = [ord(c) - (96 if b1 else 97) for c in blk]
                        for k, p in enumerate(P91):
                            pos = p - base if base == 1 else p
                            if 0 <= pos < 91 and SEQ[k] == zc:
                                if mode == "zero": v[pos] = 0
                                elif mode == "add": v[pos] += (k + 1)
                                else: v[pos] -= (k + 1)
                        g = [v[i*13:(i+1)*13] for i in range(7)]
                        cs = [sum(g[r][c] for r in range(7)) for c in range(13)]
                        rs = [sum(r) for r in g]
                        for axis, nums in (("c", cs), ("r", rs)):
                            for s in render(nums):
                                h.try_family(s, f"p24:{bname}:b{base}:{zc}:{int(b1)}:{mode}:{axis}")
                                n += 1
    print("candidates:", n)
    h.finish("campaign_19")

if __name__ == "__main__":
    main()
