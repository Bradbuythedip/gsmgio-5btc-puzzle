#!/usr/bin/env python3
"""Campaign 13: the 24-symbol remainder against the 24 phase-0 coloured cells.

Structural coincidence worth testing: the faed block's remainder after six 7x13
matrices is exactly 24 symbols, and the phase-0 grid has exactly 24 coloured cells
(9 yellow, 15 blue). That gives a mask specified entirely in advance by the puzzle
(unlike a fitted mask), so any hit here would be meaningful.

Phase-0 colour bits, blue=1 yellow=0 in spiral order, are the low bits of the decoded
URL - see unverified/phase0_yellow_blue_counts.md.
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
assert len(REM) == 24, len(REM)

URL = "gsmg.io/theseedisplanted"
BITS = [ord(c) & 1 for c in URL]           # 24 low bits, = the colour pattern
assert len(BITS) == 24

def fmt(nums):
    return ["".join(map(str, nums)), " ".join(map(str, nums)), ",".join(map(str, nums)),
            "".join(chr(65 + (s - 1) % 26) for s in nums),
            "".join(chr(97 + (s - 1) % 26) for s in nums),
            "".join(chr(65 + s % 26) for s in nums),
            str(sum(nums))]

def main():
    h = Harness("campaign_13")
    v1 = [ord(c) - 96 for c in REM]   # a=1..i=9
    v0 = [ord(c) - 97 for c in REM]   # a=0..i=8

    # 1) selection by colour bit
    for name, bits in (("blue1", BITS), ("yellow1", [1 - b for b in BITS])):
        sel = "".join(c for c, b in zip(REM, bits) if b)
        h.try_family(sel, f"rem24:select:{name}")
        for base1, vv in (("b1", v1), ("b0", v0)):
            nums = [x for x, b in zip(vv, bits) if b]
            for s in fmt(nums):
                h.try_family(s, f"rem24:select-nums:{name}:{base1}")

    # 2) zeroing by colour bit (the "zeroed out" hint, with a pre-specified mask)
    for name, bits in (("zero-yellow", BITS), ("zero-blue", [1 - b for b in BITS])):
        for base1, vv in (("b1", v1), ("b0", v0)):
            nums = [x if b else 0 for x, b in zip(vv, bits)]
            for s in fmt(nums):
                h.try_family(s, f"rem24:{name}:{base1}")

    # 3) arithmetic combination with the bits
    for base1, vv in (("b1", v1), ("b0", v0)):
        for op, f in (("xor", lambda x, b: x ^ b), ("add", lambda x, b: x + b),
                      ("sub", lambda x, b: x - b), ("mul", lambda x, b: x * (b + 1))):
            nums = [f(x, b) for x, b in zip(vv, BITS)]
            for s in fmt(nums):
                h.try_family(s, f"rem24:{op}:{base1}")

    # 4) the same mask applied to the seven 7x13 matrices' column sums (13 != 24, so
    #    apply to the 7 block totals and to the 91-cell blocks by spiral-ish reuse)
    BLOCKS = [head] + [faed[i*91:(i+1)*91] for i in range(6)]
    for bi, b in enumerate(BLOCKS):
        for base1 in (True, False):
            vv = [ord(c) - (96 if base1 else 97) for c in b]
            nums = [x if BITS[i % 24] else 0 for i, x in enumerate(vv)]
            g = [nums[i:i+13] for i in range(0, 91, 13)]
            cs = [sum(r[c] for r in g) for c in range(13)]
            for s in fmt(cs):
                h.try_family(s, f"rem24:maskblock{bi}:b{int(base1)}")

    # 5) remainder paired with head/faed labels
    for pre in ("matrixsumlist", "yellowblue", "yinyang", ""):
        h.try_family(pre + REM, f"rem24:labelled:{pre}")
        h.try_family(REM + pre, f"rem24:labelled-post:{pre}")

    h.finish("campaign_13")

if __name__ == "__main__":
    main()
