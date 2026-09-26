#!/usr/bin/env python3
"""Campaign 12: the 7x13 block decomposition as "matrixsumlist".

New structural ground: head = 91 = 7x13, faed = 570 = 6*91 + 24, so there are seven
identically shaped 7x13 matrices plus a 24-symbol remainder. 13 does not divide 570, so
divisor-only sweeps never reached this.

"matrix sum list" reads literally as the list of sums of a matrix. Test that: derive
sum lists from these seven matrices and check whether any opens a lock. A decrypt is
self-proving; finding a word in the output is not.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT

page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
head = page[:ab[0][0]]
rest = page[ab[0][1]:]
faed = rest[:rest.index('z')]
REM = faed[546:]
BLOCKS = [("head", head)] + [(f"faed{i+1}", faed[i*91:(i+1)*91]) for i in range(6)]
ALL7 = [b for _, b in BLOCKS]

def grid(block, base1=True):
    v = [ord(c) - (96 if base1 else 97) for c in block]
    return [v[i:i+13] for i in range(0, 91, 13)]

def colsums(b, base1=True):
    g = grid(b, base1)
    return [sum(r[c] for r in g) for c in range(13)]

def rowsums(b, base1=True):
    return [sum(r) for r in grid(b, base1)]

def diagsums(b, base1=True):
    g = grid(b, base1)
    return [sum(g[r][(r + k) % 13] for r in range(7)) for k in range(13)]

def fmt(nums):
    """All the plausible renderings of a sum list."""
    out = ["".join(map(str, nums)), " ".join(map(str, nums)), ",".join(map(str, nums)),
           "-".join(map(str, nums))]
    # letter renderings
    for name, f in (("A1", lambda s: chr(65 + (s - 1) % 26)),
                    ("A0", lambda s: chr(65 + s % 26)),
                    ("a1", lambda s: chr(97 + (s - 1) % 26)),
                    ("a0", lambda s: chr(97 + s % 26))):
        out.append("".join(f(s) for s in nums))
    out.append(str(sum(nums)))
    return out

def main():
    h = Harness("campaign_12")

    # per-block sum lists, three axes, both digit bases
    for bname, b in BLOCKS:
        for axis, fn in (("col", colsums), ("row", rowsums), ("diag", diagsums)):
            for base1 in (True, False):
                for s in fmt(fn(b, base1)):
                    h.try_family(s, f"m7:{bname}:{axis}:b{int(base1)}")

    # concatenations across all seven matrices, in order
    for axis, fn in (("col", colsums), ("row", rowsums), ("diag", diagsums)):
        for base1 in (True, False):
            allnums = [x for b in ALL7 for x in fn(b, base1)]
            for s in fmt(allnums):
                h.try_family(s, f"m7:all7:{axis}:b{int(base1)}")
            # faed's six only (head excluded / head only)
            six = [x for b in ALL7[1:] for x in fn(b, base1)]
            for s in fmt(six):
                h.try_family(s, f"m7:faed6:{axis}:b{int(base1)}")

    # block totals as a 7-number list ("sum list" over the seven matrices)
    for base1 in (True, False):
        totals = [sum(rowsums(b, base1)) for b in ALL7]
        for s in fmt(totals):
            h.try_family(s, f"m7:blocktotals:b{int(base1)}")

    # the 24-symbol remainder, and labelled variants
    h.try_family(REM, "m7:remainder")
    for base1 in (True, False):
        rv = [ord(c) - (96 if base1 else 97) for c in REM]
        for s in fmt(rv):
            h.try_family(s, f"m7:remainder-nums:b{int(base1)}")
    for pre in ("matrixsumlist", "matrix", "sumlist"):
        for base1 in (True, False):
            for s in fmt(colsums(head, base1))[:4]:
                h.try_family(pre + s, f"m7:labelled:{pre}")

    # column-major and transposed reads of each block as passwords
    for bname, b in BLOCKS:
        rows = [b[i:i+13] for i in range(0, 91, 13)]
        h.try_family("".join("".join(r[c] for r in rows) for c in range(13)), f"m7:colmajor:{bname}")

    h.finish("campaign_12")

if __name__ == "__main__":
    main()
