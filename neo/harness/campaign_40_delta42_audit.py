#!/usr/bin/env python3
"""Campaign 40: audit of the Δ42 operator, Δk(L)_i = ±(L[i+k] − L[i]) mod 26, over DBBI, VIC and
R = map0(DBBI) − VIC. Checks every k=1..90, both signs, and a 10-marker list; no AES."""
import random, os
NEO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
soup = open(os.path.join(NEO, "materials/primary/salphaseion_soup_space_separated.txt")).read().split()
VIC = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
d = [ord(x) - 97 for x in soup[:91]]; v = [ord(c) - 65 for c in VIC]
R = [(a - b) % 26 for a, b in zip(d, v)]
s = lambda L: "".join(chr(x + 65) for x in L)
delta = lambda L, k, sg=1: [((L[i + k] - L[i]) * sg) % 26 for i in range(len(L) - k)]
M = ["KEY", "YOUWON", "YINYANG", "PASSWORD", "DOOR", "HALF", "BETTER", "NEO", "ONE", "ZERO"]
print("D42(R) =", s(delta(R, 42)))
hits, npos = [], 0
for name, L in {"DBBI": d, "VIC": v, "R": R}.items():
    for k in range(1, 91):
        for sg in (1, -1):
            t = s(delta(L, k, sg)); npos += len(t)
            for m in M:
                i = t.find(m)
                while i >= 0:
                    hits.append((name, k, sg, m, i)); i = t.find(m, i + 1)
for h in hits: print("  ", h)
print(f"marker hits {len(hits)}, expected {sum(npos * 26.0 ** -len(m) for m in M):.2f}")
random.seed(1); n = 200000
c = sum("KEY" in s(delta([random.randrange(26) for _ in range(91)], 42)) for _ in range(n))
print(f"P(KEY in D42 of a random 91-string, one sign) = {c / n:.4f}")
