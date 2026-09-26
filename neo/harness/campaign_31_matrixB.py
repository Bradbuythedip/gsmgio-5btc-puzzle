#!/usr/bin/env python3
"""Campaign 31: pin slot B to the DBBI/FAED structure by soup position (user, 2026-09-26).

Soup layout (authenticated positions):
  0:91    DBBI      91 chars
  91:195  a/b field 104 bits -> "matrixsumlist"
  195:765 FAED      570 chars
The operator name is sandwiched between DBBI and FAED, so the matrix is the DBBI/FAED
structure, NOT the genesis 14x14 grid. Genesis row/col sums (B1 610876654997879,
B2 8108108736759668) are deprecated for slot B.

DBBI(91) + FAED[0:546] = 637 = 7 x 91 = 7 layers of 7x13. Compute the source-derived
integer lists (matrixsumlist emits numbers; do NOT hash -- they are indices for slot C).
Also cross-reference FAED[546:570] (24 tail) against the 24-bit colour frame (slot A link),
and test slot C word-counts 1/5/7 as indices. No AES password battery.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "materials")
page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
DBBI = page[:ab[0][0]]; rest = page[ab[0][1]:]; FAED = rest[:rest.index('z')]
assert len(DBBI) == 91 and len(FAED) == 570
def dig(s): return [ord(c) - 96 for c in s]           # a=1..i=9

# ---- 7 layers of 7x13 ----
stack = DBBI + FAED[:546]                               # 637 = 7*91
assert len(stack) == 637
layers = [dig(stack[i*91:(i+1)*91]) for i in range(7)]  # each 91 values (7x13 row-major)

# element-wise sum across the 7 layers -> 91 values
ew = [sum(layers[L][i] for L in range(7)) for i in range(91)]     # each 7..63
ew_grid = [ew[r*13:(r+1)*13] for r in range(7)]
row_sums = [sum(row) for row in ew_grid]               # 7 values
col_sums = [sum(ew_grid[r][c] for r in range(7)) for c in range(13)]  # 13 values
layer_totals = [sum(layers[L]) for L in range(7)]      # 7 values (per-layer)
# per-single-layer (layer 0 = DBBI) row/col too, for the index-sized lists
def layer_rowcol(L):
    g=[layers[L][r*13:(r+1)*13] for r in range(7)]
    return [sum(r) for r in g], [sum(g[r][c] for r in range(7)) for c in range(13)]

print("=== FROZEN slot-B candidate integer lists (source-forced by position) ===")
print("B-ew91 (element-wise, 91 vals, range %d-%d):" % (min(ew),max(ew)))
print("  ", ew)
print("B-row7 (row sums of element-wise grid):", row_sums)
print("B-col13 (col sums of element-wise grid):", col_sums)
print("layer_totals (7):", layer_totals)
print("concat forms: row7=%s  col13=%s" % ("".join(map(str,row_sums)), "".join(map(str,col_sums))))

# ---- step 3: FAED 24-tail vs 24-bit colour frame ----
import json
d = json.load(open(os.path.join(MAT, "primary", "matrix_grid_spiral_colors.json")))
sp=[tuple(x) for x in d["spiral"]]; idx={c:i for i,c in enumerate(sp)}
BI=sorted(idx[tuple(c)] for c in d["blue"]); YI=sorted(idx[tuple(c)] for c in d["yellow"]); ALL=sorted(BI+YI)
colseq="".join('B' if i in BI else 'Y' for i in ALL)   # BBBBYBBBYYBBBBYBBYYBYYBY
tail24 = FAED[546:570]
print("\n=== step 3: FAED 24-tail vs colour frame ===")
print("tail24      :", tail24, " digits:", dig(tail24))
print("colour seq  :", colseq)
print("blue-select :", "".join(tail24[i] for i in range(24) if colseq[i]=='B'))
print("yellow-selct:", "".join(tail24[i] for i in range(24) if colseq[i]=='Y'))
print("tail digits at blue :", [dig(tail24)[i] for i in range(24) if colseq[i]=='B'])
print("tail digits at yellow:", [dig(tail24)[i] for i in range(24) if colseq[i]=='Y'])

# ---- step 4: slot C word-counts 1,5,7 as indices ----
print("\n=== step 4: C word-counts (1,5,7) as indices into held texts ===")
VICW="in case you manage to crack this the private keys belong to half and better half and they also need funds to live".split()
CHECK="raising the stakes without extra chances of winning a fubcd king oracle queen thingky mvps on a sad board but as wide as the first one seen".split()
URL="gsmg.io/theseedisplanted"
for name,seq in (("VICwords",VICW),("checker",CHECK)):
    for base in (1,0):
        picks=[seq[c-1 if base==1 else c] for c in (1,5,7) if 0<=(c-1 if base==1 else c)<len(seq)]
        print(f"  {name} b{base}: {picks}")
for base in (1,0):
    picks=[URL[c-1 if base==1 else c] for c in (1,5,7) if 0<=(c-1 if base==1 else c)<len(URL)]
    print(f"  URLchars b{base}: {''.join(picks)}")

# ---- bonus: B-ew91 (index-sized 7-63) as WORD indices into the Architect speech ----
print("\n=== bonus: B-ew91 as 1-based word indices into Architect speech (readability gate) ===")
arch=open('/tmp/arch_words.txt').read().split()
extract=[arch[i-1] for i in ew if 1<=i<=len(arch)]
print("  n words:", len(extract), " sample:", " ".join(extract[:30]))
# also DBBI-layer col sums (7-63) as word indices
r0,c0=layer_rowcol(0)
print("  DBBI col-sums(13):", c0, " ->", " ".join(arch[i-1] for i in c0 if 1<=i<=len(arch)))
print("  DBBI row-sums(7):", r0, " ->", " ".join(arch[i-1] for i in r0 if 1<=i<=len(arch)))

if __name__=="__main__": pass
