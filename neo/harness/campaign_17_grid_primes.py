#!/usr/bin/env python3
"""Campaign 17: yellowblueprimes - the prime subset of the coloured spiral indices.

Authenticated operands (neo/materials/primary/matrix_grid_spiral_colors.json):
  BLUE  (15) spiral idx: 7 15 23 31 47 55 63 87 95 103 111 127 135 159 183
  YELLOW ( 9) spiral idx: 39 71 79 119 143 151 167 175 191
  all 24 are == 7 mod 8, one per byte of "gsmg.io/theseedisplanted"
  colour sequence in spiral order: BBBBYBBBYYBBBBYBBYYBYYBY
  #FEFEFE cell (7,4) -> spiral index 163

Creator constraints: primes 2/3/5/7 required; "some characters need to be zeroed out";
"yellowblueprimes" is one token in the master hint.
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness

J = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "materials", "primary",
                 "matrix_grid_spiral_colors.json")
d = json.load(open(J))
spiral = [tuple(x) for x in d["spiral"]]
idx = {c: i for i, c in enumerate(spiral)}
BI = sorted(idx[tuple(c)] for c in d["blue"])
YI = sorted(idx[tuple(c)] for c in d["yellow"])
ALL = sorted(BI + YI)
URL = d["decoded"]
SEQ = "".join('B' if i in BI else 'Y' for i in ALL)

def sieve(n):
    s = [True]*(n+1); s[0] = s[1] = False
    for i in range(2, int(n**.5)+1):
        if s[i]: s[i*i::i] = [False]*len(s[i*i::i])
    return {i for i, b in enumerate(s) if b}
P = sieve(400)
SMALL = {2, 3, 5, 7}

def main():
    h = Harness("campaign_17")
    C = {}

    # --- selections over the 24 bytes / positions ---
    for pname, pset in (("primes", P), ("2357", SMALL)):
        for base, off in (("1based", 1), ("0based", 0)):
            keep = [n for n in range(24) if (n + off) in pset]
            drop = [n for n in range(24) if (n + off) not in pset]
            C[f"url-keep-{pname}-{base}"] = "".join(URL[n] for n in keep)
            C[f"url-drop-{pname}-{base}"] = "".join(URL[n] for n in drop)
            C[f"url-zero-{pname}-{base}"] = "".join(URL[n] if (n + off) in pset else '0' for n in range(24))
            C[f"seq-keep-{pname}-{base}"] = "".join(SEQ[n] for n in keep)
            C[f"idx-keep-{pname}-{base}"] = "".join(str(ALL[n]) for n in keep)
            C[f"idx-keep-{pname}-{base}-sp"] = " ".join(str(ALL[n]) for n in keep)

    # --- selections over the spiral indices themselves ---
    C["spiral-prime-idx"] = "".join(str(i) for i in ALL if i in P)
    C["spiral-prime-idx-sp"] = " ".join(str(i) for i in ALL if i in P)
    C["blue-prime-idx"] = "".join(str(i) for i in BI if i in P)
    C["yellow-prime-idx"] = "".join(str(i) for i in YI if i in P)
    C["url-at-spiral-prime"] = "".join(URL[i // 8] for i in ALL if i in P)
    C["blue-idx"] = "".join(map(str, BI)); C["yellow-idx"] = "".join(map(str, YI))
    C["blue-idx-sp"] = " ".join(map(str, BI)); C["yellow-idx-sp"] = " ".join(map(str, YI))
    C["all-idx"] = "".join(map(str, ALL)); C["all-idx-sp"] = " ".join(map(str, ALL))
    C["seq"] = SEQ; C["seq-01"] = SEQ.replace('B', '1').replace('Y', '0')
    C["seq-10"] = SEQ.replace('B', '0').replace('Y', '1')
    C["fefefe-163"] = "163"; C["fefefe-cell"] = "74"

    # --- counts (yellow=9, blue=15) with the prime token ---
    for a in ("9", "15", "915", "159", "nine", "fifteen"):
        C[f"count-{a}"] = a
        C[f"count-{a}-primes"] = a + "2357"
        C[f"primes-count-{a}"] = "2357" + a
    for pre in ("yellowblueprimes", "yellowblue", "primes", ""):
        C[f"lab-{pre}-seq01"] = pre + SEQ.replace('B', '1').replace('Y', '0')
        C[f"lab-{pre}-url915"] = pre + "915"

    print("candidates:", len(C))
    for name, s in C.items():
        if s:
            h.try_family(s, f"grid:{name}")
            # also combined with the other two authenticated components
            for tail in ("matrixsumlist", "lastwordsbeforearchichoice", ""):
                if tail:
                    h.try_pw(s + tail, f"grid3:{name}")
                    h.try_pw(hashlib.sha256((s + tail).encode()).hexdigest(), f"grid3sha:{name}")
    h.finish("campaign_17")

if __name__ == "__main__":
    main()
