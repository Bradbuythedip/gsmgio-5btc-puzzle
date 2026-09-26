#!/usr/bin/env python3
"""Campaign 02: the letter blocks themselves as password material.

"its in front of your eyes but youre not seeing it" readings:
- head/faed/page verbatim (with and without spaces) as passwords
- matrix transposition reads (column-major) of head 7x13/13x7 and faed divisors
- row/col sum lists for all divisor widths, both digit mappings, several formats
- prime-position extractions and prime-position removals ("prime basics")
- block sums (head 422, faed 3079 [prime], total 3501)
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT

page_sp = open(os.path.join(MAT, "salphaseion_page.txt")).read().strip()
page = "".join(page_sp.split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
head = page[:ab[0][0]]
rest = page[ab[0][1]:]
faed = rest[:rest.index('z')]

def val(c, base1=True):
    return ord(c) - 96 if base1 else ord(c) - 97

def colmajor(s, width):
    rows = [s[i:i+width] for i in range(0, len(s), width)]
    return "".join("".join(r[c] for r in rows if c < len(r)) for c in range(width))

def sumlist(s, width, base1=True, cols=False):
    v = [val(c, base1) for c in s]
    rows = [v[i:i+width] for i in range(0, len(v), width)]
    if cols:
        rows = [list(x) for x in zip(*rows)]
    return [sum(r) for r in rows]

def primes_upto(n):
    sieve = [True]*(n+1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            sieve[i*i::i] = [False]*len(sieve[i*i::i])
    return [i for i, b in enumerate(sieve) if b]

def main():
    h = Harness("campaign_02")
    blocks = {"head": head, "faed": faed, "page": page, "headfaed": head+faed}

    # 1) verbatim
    for name, blk in blocks.items():
        h.try_family(blk, f"verbatim:{name}")
    h.try_family(page_sp, "verbatim:page-with-spaces")

    # 2) transpositions as passwords
    widths = {"head": [7, 13], "faed": [2, 3, 5, 6, 10, 15, 19, 30, 38, 57, 95, 114, 190, 285]}
    for name in ("head", "faed"):
        for w in widths[name]:
            t = colmajor(blocks[name], w)
            h.try_family(t, f"colmajor:{name}:{w}")

    # 3) sum lists, all divisor widths, both mappings, rows+cols, 3 formats
    for name in ("head", "faed"):
        blk = blocks[name]
        n = len(blk)
        for w in [d for d in range(2, n) if n % d == 0]:
            for base1 in (True, False):
                for cols in (False, True):
                    sl = sumlist(blk, w, base1, cols)
                    tag = f"sumlist:{name}:w{w}:b{int(base1)}:c{int(cols)}"
                    h.try_family("".join(map(str, sl)), tag)
                    h.try_family(" ".join(map(str, sl)), tag+":sp")
                    h.try_family(",".join(map(str, sl)), tag+":cm")

    # 4) prime positions (1-based and 0-based), kept and removed
    for name, blk in blocks.items():
        pr = set(primes_upto(len(blk)+1))
        kept1 = "".join(c for i, c in enumerate(blk, 1) if i in pr)
        rem1 = "".join(c for i, c in enumerate(blk, 1) if i not in pr)
        kept0 = "".join(c for i, c in enumerate(blk) if i in pr)
        h.try_family(kept1, f"primepos-keep1:{name}")
        h.try_family(rem1, f"primepos-drop1:{name}")
        h.try_family(kept0, f"primepos-keep0:{name}")

    # 5) block sums and prime-flavored numbers
    for s in ("422", "3079", "3501", "4223079", "3079422", "211", "2113079",
              "matrixsumlist422", "matrixsumlist3079", "sumlist3079"):
        h.try_family(s, "blocksums")

    h.finish("campaign_02")

if __name__ == "__main__":
    main()
