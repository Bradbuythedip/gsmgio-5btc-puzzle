#!/usr/bin/env python3
"""Campaign 04: spiral-ring and prime-indexed sum families on the phase-0 matrix,
case variants of the seven components. (The colored-cell spiral reading is excluded:
it restates the URL — see unverified/phase0_yellow_blue_counts.md.)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness
from campaign_01 import phase0_matrix, msl_variants

def ring_sums(m):
    n = len(m)
    rings = []
    for k in range(n // 2):
        s = 0
        for c in range(k, n - k):
            s += m[k][c] + m[n - 1 - k][c]
        for r in range(k + 1, n - 1 - k):
            s += m[r][k] + m[r][n - 1 - k]
        rings.append(s)
    return rings

def main():
    h = Harness("campaign_04")
    m = phase0_matrix()
    rs = [sum(r) for r in m]
    cs = [sum(c) for c in zip(*m)]
    P = [2, 3, 5, 7, 11, 13]

    fams = {}
    fams["rings"] = ring_sums(m)
    # prime-indexed rows/cols, 1-based
    fams["prime_rows"] = [rs[p - 1] for p in P]
    fams["prime_cols"] = [cs[p - 1] for p in P]
    # sums over prime rows/cols as single totals
    fams["prime_rows_total"] = [sum(rs[p - 1] for p in P)]
    fams["prime_cols_total"] = [sum(cs[p - 1] for p in P)]
    # cells with both coords prime (1-based)
    fams["prime_cells"] = [sum(m[r - 1][c - 1] for r in P for c in P)]
    # per-row popcount of prime-indexed columns
    fams["rows_at_prime_cols"] = [sum(row[p - 1] for p in P) for row in m]
    # per-byte popcounts of the phase-0 unwrapped string (24 bytes of the URL)
    url = "gsmg.io/theseedisplanted"
    fams["url_byte_popcounts"] = [bin(ord(c)).count("1") for c in url]
    fams["url_byte_values"] = [ord(c) for c in url]

    for name, nums in fams.items():
        for sep in ("", " ", ","):
            h.try_family(sep.join(map(str, nums)), f"p0:{name}:{sep!r}")
        h.try_family("matrixsumlist" + "".join(map(str, nums)), f"p0-labeled:{name}")

    # case variants of the seven components
    labels = ["yellow", "blue", "primes", "matrixsumlist",
              "lastwordsbeforearchichoice", "yinyang", "thepassword"]
    msl = msl_variants()
    values = ["0", "1", "2357", msl["rowsums"], "hope", "yinyang", "thispassword"]
    for toks in (labels, values):
        h.try_family("".join(t.capitalize() for t in toks), "case:Title")
        h.try_family("".join(toks).upper(), "case:UPPER")
    for spell in ("MatrixSumList", "MATRIXSUMLIST", "matrixSumList"):
        h.try_family(spell, "case:msl")

    h.finish("campaign_04")

if __name__ == "__main__":
    main()
