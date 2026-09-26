#!/usr/bin/env python3
"""Campaign 26: bounded offline address check of every object NAMED in the constraint sheet.

Pre-registered set = Section 2 operand rows + tables B and C + the four slot labels, each
in the representations the sheet already lists (no new transforms). 12 addresses per object.
Targets: prize, README second address, and the user-supplied 1NULY7 address.
"""
import json, os, re, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr_check import check
MAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "materials")

d = json.load(open(os.path.join(MAT, "primary", "matrix_grid_spiral_colors.json")))
g = d["grid"]; sp = [tuple(x) for x in d["spiral"]]
bits = "".join(str(g[r][c]) for r, c in sp)
idx = {c: i for i, c in enumerate(sp)}
BI = sorted(idx[tuple(c)] for c in d["blue"]); YI = sorted(idx[tuple(c)] for c in d["yellow"]); ALL = sorted(BI + YI)
colbits = "".join('1' if i in BI else '0' for i in ALL)
page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
dbbi = page[:ab[0][0]]; rest = page[ab[0][1]:]; faed = rest[:rest.index('z')]
VIC = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
dv = "".join(chr(65 + ((ord(a) - 96) - (ord(v) - 64)) % 26) for a, v in zip(dbbi, VIC))
rows = "".join(str(sum(r)) for r in g); cols = "".join(str(sum(g[r][c] for r in range(14))) for c in range(14))

C = {
 "url": b"gsmg.io/theseedisplanted",
 "grid196bits": bits.encode(), "grid196-packed": int(bits + "0000", 2).to_bytes(25, 'big'),
 "colbits24": colbits.encode(), "colbits24-packed": bytes.fromhex("f73d92"), "f73d92-hex": b"f73d92", "F73D92": b"F73D92",
 "yellowbits24": "".join('0' if i in BI else '1' for i in ALL).encode(), "08c26d-packed": bytes.fromhex("08c26d"),
 "colour-seq": b"BBBBYBBBYYBBBBYBBYYBYYBY",
 "rowsums": rows.encode(), "colsums": cols.encode(), "rows||cols": (rows + cols).encode(),
 "dbbi": dbbi.encode(), "dbbi-digits": "".join(str(ord(c) - 96) for c in dbbi).encode(),
 "faed": faed.encode(), "faed-rem24": faed[546:].encode(),
 "VIC": VIC.encode(), "dbbi-VIC": dv.encode(), "dbbi-VIC-prefix21": dv[:21].encode(), "dbbi-VIC-tail64": dv[27:].encode(), "YOUWON": b"YOUWON",
 "A": b"yellowblueprimes", "B0": b"matrixsumlist", "C0": b"lastwordsbeforearchichoice", "D": b"yinyang",
 "C1": b"ireallyhopeyouretheone", "C2": b"hopeitisthequintessentialhumandelusionsimultaneouslythesourceofyourgreateststrengthandyourgreatestweakness", "C3": b"ciaobellao",
 "hint2023-4": b"yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
 "hint2023-full": open(os.path.join(MAT, "primary", "hint_2023-02-23_decoded.txt")).read().strip().encode(),
 "thispassword": b"thispassword", "enter": b"enter", "shabef1": b"shabefourfirsthintisyourlastcommand", "shabef2": b"shabefanstoo",
 "phase1hash": b"5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75",
 "fefefe": b"fefefe", "163": b"163", "firstorzero": b"firstorzero", "10": b"10", "01": b"01",
 "architect-span": open(os.path.join(MAT, "primary", "architect_span.txt")).read().strip().encode(),
}
cands = [(k, v) for k, v in C.items()]
# lowercase variants of letter objects, since the creator's answers are lowercase
for k, v in list(C.items()):
    if v.isalpha() and v != v.lower():
        cands.append((k + "-lower", v.lower()))
print("objects:", len(cands))
m = check(cands)
print("matches:", m)
