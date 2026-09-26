#!/usr/bin/env python3
"""Campaign 46: the 196 = 91 + 14 + 91 scalar test, pre-registered in
intake/2026-09-26-196split/PREREG.md. Address predicate only; no AES.

Ten fixed scalars (sha256 of DBBI, VIC, two residual renderings, two 196-symbol
concatenations; two middles read two ways) against the prize and 17ucy1, compressed and
uncompressed.
"""
import hashlib, json, os, re, sys, time
import btc_addr

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
REPO = os.path.join(NEO, "..")
OUT = os.path.join(NEO, "attempts", "campaign_46_196_split.jsonl")
TARGETS = {"prize": "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "better": "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"}
N = btc_addr.N

def objects():
    soup = open(os.path.join(NEO, "materials/primary/salphaseion_soup_space_separated.txt")).read().split()
    dbbi = "".join(soup[:91])
    vic = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
    g = json.load(open(os.path.join(NEO, "materials/primary/matrix_grid_spiral_colors.json")))
    G, sp = g["grid"], [tuple(x) for x in g["spiral"]]
    spiral_bits = "".join(str(G[r][c]) for r, c in sp)
    url_bits = "".join(f"{b:08b}" for b in g["decoded"].encode())
    assert spiral_bits[:192] == url_bits, "spiral does not reproduce the URL"
    m_diag = "".join(str(G[k][k]) for k in range(14))
    m_spiral = spiral_bits[91:105]
    r_auth = "".join(chr(65 + ((ord(d) - 96) - (ord(v) - 64)) % 26) for d, v in zip(dbbi, vic))
    r_lit = "".join(chr((ord(d) - ord(v)) % 26 + 65) for d, v in zip(dbbi, vic))
    return dbbi, vic, m_diag, m_spiral, r_auth, r_lit

def selfcheck(dbbi, vic, m_diag, m_spiral, r_auth, r_lit):
    ok = (len(dbbi) == 91 and set(dbbi) <= set("abcdefghi") and len(vic) == 91
          and r_auth[21:27] == "YOUWON" and r_lit[21:27] == "EUACUT"
          and all((ord(b) - ord(a)) % 26 == 6 for a, b in zip(r_auth, r_lit))
          and m_diag == "01000000111111" and len(m_spiral) == 14
          and btc_addr.self_test())
    print("campaign 46 self-check passed:", ok)
    return ok

def sha_scalar(s):
    return int.from_bytes(hashlib.sha256(s.encode()).digest(), "big") % N

def main():
    dbbi, vic, m_diag, m_spiral, r_auth, r_lit = objects()
    assert selfcheck(dbbi, vic, m_diag, m_spiral, r_auth, r_lit), "self-check failed"
    scalars = [
        ("1 sha256(DBBI)", sha_scalar(dbbi)),
        ("1 sha256(VIC)  [re-check of campaigns 34/43]", sha_scalar(vic)),
        ("2 sha256(R_auth)  [YOUWON stream]", sha_scalar(r_auth)),
        ("2 sha256(R_literal)  [draft rendering, +6]", sha_scalar(r_lit)),
        ("3 sha256(DBBI||M_diag||VIC)", sha_scalar(dbbi + m_diag + vic)),
        ("3 sha256(DBBI||M_spiral||VIC)", sha_scalar(dbbi + m_spiral + vic)),
        ("4 int(M_diag,2)", int(m_diag, 2)),
        ("4 int(M_spiral,2)", int(m_spiral, 2)),
        ("4 int.from_bytes(M_diag ascii)", int.from_bytes(m_diag.encode(), "big") % N),
        ("4 int.from_bytes(M_spiral ascii)", int.from_bytes(m_spiral.encode(), "big") % N),
    ]
    print(f"M_diag {m_diag}  M_spiral {m_spiral}")
    hits = []
    with open(OUT, "w") as f:
        for label, k in scalars:
            c, u = btc_addr.addrs(k)
            hit = [n for n, a in TARGETS.items() if a in (c, u)]
            hits += [(label, h) for h in hit]
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "label": label,
                                "scalar_hex": f"{k:064x}", "addr_comp": c, "addr_unc": u, "HIT": hit}) + "\n")
            print(f"{label:48s} {c}  {u}  {'*** HIT ' + str(hit) if hit else 'null'}")
    print("*** HIT ***" if hits else f"null: 0 of {len(scalars)} scalars x 2 encodings x 2 addresses. Logged.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
