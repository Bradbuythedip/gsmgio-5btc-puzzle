#!/usr/bin/env python3
"""Campaign 08: "zeroed out" digit maps, separator segmentations, columnar keying.

(a) agda/cfob used a=1..i=9 with o=0. head/faed lack 'o'; hypothesis: one of a..i
    plays the zero ("some characters need to be 'zeroed out'"). 9 maps per block:
    X->0, others keep a=1..i=9 values. digits -> int -> hex -> ascii, scored; the
    digit strings and any printable decodes also go in as passwords.
(b) each letter X as separator: segment-length lists and per-segment digit decodes.
(c) head as 7x13, per-column shift by "matrixsumlist" (13 letters), mod 9 and mod 26,
    +/- directions, read row/col-major; results as passwords and digit-decoded.
"""
import os, re, string, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT

page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
head = page[:ab[0][0]]
rest = page[ab[0][1]:]
faed = rest[:rest.index('z')]

P = set(string.printable)

def pr(s):
    return sum(1 for c in s if c in P) / max(1, len(s))

def int_hex_ascii(digits):
    try:
        v = int(digits)
    except ValueError:
        return ""
    h = hex(v)[2:]
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h).decode("latin1")
    except Exception:
        return ""

def main():
    h = Harness("campaign_08")
    interesting = []

    # (a) zeroed-out maps
    for name, blk in (("head", head), ("faed", faed)):
        for zc in "abcdefghi":
            digs = "".join('0' if c == zc else str(ord(c) - 96) for c in blk)
            h.try_pw(digs, f"zmap:{name}:{zc}->0")
            t = int_hex_ascii(digs)
            if t and pr(t) > 0.5:
                interesting.append((pr(t), f"zmap:{name}:{zc}->0", t[:70]))
            if t and pr(t) > 0.85:
                h.try_family(t, f"zmap-decode:{name}:{zc}")

    # (b) separator segmentations
    for name, blk in (("head", head), ("faed", faed)):
        for sep in "abcdefghi":
            segs = [s for s in blk.split(sep)]
            lens = [len(s) for s in segs]
            h.try_pw("".join(map(str, lens)), f"seglen:{name}:{sep}")
            h.try_pw(" ".join(map(str, lens)), f"seglen-sp:{name}:{sep}")
            nonempty = [s for s in segs if s]
            digs = "".join(str(ord(c) - 96) for s in nonempty for c in s)
            t = int_hex_ascii(digs)
            if t and pr(t) > 0.85:
                interesting.append((pr(t), f"segjoin:{name}:{sep}", t[:70]))
                h.try_family(t, f"segjoin:{name}:{sep}")

    # (c) columnar key on head 7x13
    key = "matrixsumlist"
    rows = [head[i:i+13] for i in range(0, 91, 13)]
    for mod in (9, 26):
        for sign in (1, -1):
            shifted = []
            for r in rows:
                row = []
                for j, c in enumerate(r):
                    kv = ord(key[j]) - 97
                    cv = ord(c) - 97
                    row.append(chr(97 + (cv + sign * kv) % mod))
                shifted.append("".join(row))
            rm = "".join(shifted)
            cm = "".join("".join(r[j] for r in shifted) for j in range(13))
            for tag, s in ((f"colkey:m{mod}:s{sign}:row", rm), (f"colkey:m{mod}:s{sign}:col", cm)):
                h.try_family(s, tag)
                digs = "".join(str(ord(c) - 96) for c in s if 'a' <= c <= 'i')
                t = int_hex_ascii(digs) if len(digs) == len(s) else ""
                if t and pr(t) > 0.85:
                    interesting.append((pr(t), tag, t[:70]))
                    h.try_family(t, tag + ":decoded")

    print("interesting decodes (pr>0.5):")
    for x in sorted(interesting, reverse=True)[:12]:
        print("  ", x)
    h.finish("campaign_08")

if __name__ == "__main__":
    main()
