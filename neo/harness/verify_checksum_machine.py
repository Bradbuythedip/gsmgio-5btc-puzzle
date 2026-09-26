#!/usr/bin/env python3
"""Cold verification of the 'checksum machine' over already-solved objects. No AES, no gate.

Every claim is recomputed from primary files and printed PASS/FAIL, including each
uniqueness scan (547 colour windows, 25 tape alignments, 52 ENTER windows). The machine is
arithmetic commentary on decoded layout. Nothing here is a key, and nothing here may enter
harness/gate.py.

Sources: materials/primary/salphaseion_soup_space_separated.txt (soup),
../phase3-assets/phase3.2.txt (149-digit VIC string),
materials/primary/matrix_grid_spiral_colors.json (phase-0 frame; colour order as published in
../unverified/yellowblueprimes_grid_indices.md).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
REPO = os.path.join(NEO, "..")
results = []

def check(label, ok, detail=""):
    results.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + label + (f"  [{detail}]" if detail else ""))

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(n + 1) if s[i]]
PR = primes_upto(20000); PRS = set(PR)
def is_p(n): return n in PRS
def pi(n): return sum(1 for p in PR if p <= n)

# ---------- objects ----------
soup = open(os.path.join(NEO, "materials/primary/salphaseion_soup_space_separated.txt")).read().split()
DBBI, BIN1, FAED = soup[:91], soup[91:195], soup[195:765]
A0 = {c: i for i, c in enumerate("abcdefghi")}            # a=0 ... i=8 (non-house map)
HOUSE = {c: i + 1 for i, c in enumerate("abcdefghi")}     # house map o=0, a=1 ... i=9
FRAME = "BBBBYBBBYYBBBBYBBYYBYYBY"                         # phase-0 24-colour frame, spiral order
vic_line = [l.strip() for l in open(os.path.join(REPO, "phase3-assets/phase3.2.txt"), encoding="latin-1") if re.fullmatch(r"\d{100,}", l.strip())]
VIC = vic_line[0]
BOARD = {}
for d, ch in zip("02356789", "FUBCDORA"): BOARD[d] = ch
for i, ch in enumerate(".LETHINGKY"): BOARD[f"1{i}"] = ch
for i, ch in enumerate("MVPS.JQZXW"): BOARD[f"4{i}"] = ch
def vic_tokens(digits):
    out, i = [], 0
    while i < len(digits):
        t = digits[i:i+2] if digits[i] in "14" else digits[i]
        out.append((i, t)); i += len(t)
    return out
SENT = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"

print("== objects")
check("soup splits dbbi(91) | bin1(104) | faed(570)", len(DBBI) == 91 and len(BIN1) == 104 and len(FAED) == 570
      and set(DBBI) <= set("abcdefghi") and set(FAED) <= set("abcdefghi") and set(BIN1) <= {"a", "b"})
check("VIC string is 149 digits", len(VIC) == 149, VIC[:12] + "...")
toks = vic_tokens(VIC); dec = "".join(BOARD[t] for _, t in toks)
check("board decodes the 149 digits to the 91-letter sentence", dec == SENT, f"{len(toks)} tokens")

print("== 104-bit loop")
na, nb = BIN1.count("a"), BIN1.count("b")
bits = "".join("0" if c == "a" else "1" for c in BIN1)
packed = bytes(int(bits[k:k+8], 2) for k in range(0, 104, 8))
check("bin1 is 48 a / 56 b", (na, nb) == (48, 56), f"{na}/{nb}")
check("a=0,b=1 packed MSB-first -> 'matrixsumlist'", packed == b"matrixsumlist", packed.decode("latin1"))
check("zero-based bit[31]=0, bit[73]=1, 31+73=104", bits[31] == "0" and bits[73] == "1" and 31 + 73 == 104)
grid = json.load(open(os.path.join(NEO, "materials/primary/matrix_grid_spiral_colors.json")))
yb = {(tuple(c), "Y") for c in grid["yellow"]} | {(tuple(c), "B") for c in grid["blue"]}
pol = {col: {grid["grid"][r][c] for (r, c), cc in yb if cc == col} for col in "YB"}
check("phase-0 frame polarity is Yellow=0 / Blue=1", pol == {"Y": {0}, "B": {1}}, str(pol))
colour_at = {tuple(c): "Y" for c in grid["yellow"]}
colour_at.update({tuple(c): "B" for c in grid["blue"]})
spiral_cols = "".join(colour_at.get(tuple(rc), "") for rc in grid["spiral"])
check("frame string matches the published 24-colour order", spiral_cols == FRAME, spiral_cols)

print("== colour window on FAED (547 windows of 24)")
def ybsum(win, m):
    y = sum(m[c] for c, f in zip(win, FRAME) if f == "Y"); b = sum(m[c] for c, f in zip(win, FRAME) if f == "B")
    return y, b
hits0 = [o for o in range(547) if ybsum(FAED[o:o+24], A0) == (31, 73)]
hitsH = [o for o in range(547) if ybsum(FAED[o:o+24], HOUSE) == (31, 73)]
check("a=0: only offset 546 gives Yellow=31 / Blue=73", hits0 == [546], f"offsets {hits0}")
check("house map a=1: no window gives 31/73", hitsH == [], f"offsets {hitsH}; tail gives {ybsum(FAED[546:], HOUSE)}")

print("== seven layer totals on DBBI||FAED (25 alignments of 637)")
TAPE = DBBI + FAED
def layers(off):
    return [sum(A0[c] for c in TAPE[off + 91*k: off + 91*(k+1)]) for k in range(7)]
L0 = layers(0)
check("offset 0 totals = 331 360 369 421 418 441 396", L0 == [331, 360, 369, 421, 418, 441, 396], str(L0))
pp = [k + 1 for k, v in enumerate(L0) if is_p(v)]
check("primes at positions {1,4}: pi(331)=67, pi(421)=82, 67+82=149",
      pp == [1, 4] and pi(331) == 67 and pi(421) == 82 and 67 + 82 == 149 == len(VIC))
match = [o for o in range(len(TAPE) - 637 + 1)
         if [k + 1 for k, v in enumerate(layers(o)) if is_p(v)] == [1, 4]
         and {layers(o)[0], layers(o)[3]} == {331, 421} and pi(layers(o)[0]) + pi(layers(o)[3]) == 149]
check(f"only offset 0 of {len(TAPE) - 637 + 1} matches", match == [0] and len(TAPE) == 661, f"matches {match}")

print("== 67 | 82 split of the VIC digits")
ends = [i + len(t) for i, t in toks]
cut40 = ends[39]
left, right = VIC[:67], VIC[67:]
dl = "".join(BOARD[t] for _, t in vic_tokens(left)); dr = "".join(BOARD[t] for _, t in vic_tokens(right))
check("letter 40 ends exactly at digit 67 (a token boundary)", cut40 == 67, f"cut at {cut40}")
check("left 67 -> INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYS", dl == SENT[:40], dl)
check("right 82 -> BELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE", dr == SENT[40:], dr)

print("== unique 42")
t42 = [i for i, t in toks if t == "42"]
raw42 = [m.start() for m in re.finditer(r"(?=42)", VIC)]
first_p = SENT.index("PRIVATEKEYS")
check("token 42 occurs once, at digit index 47, and decodes to P of PRIVATEKEYS",
      t42 == [47] and BOARD["42"] == "P" and [i for i, t in toks].index(47) == first_p,
      f"token hits {t42}; raw substring hits {raw42}")
check("board: 42->P, 15->I, 10->'.', 43->S", (BOARD["42"], BOARD["15"], BOARD["10"], BOARD["43"]) == ("P", "I", ".", "S"))

print("== ENTER mask (40 bits over 40 letters)")
EB = "".join(f"{b:08b}" for b in b"enter")
def masked(off):
    w = SENT[off:off+40]; v = [ord(c) - 65 for c in w]
    return sum(x for x, m in zip(v, EB) if m == "1"), sum(x for x, m in zip(v, EB) if m == "0")
s1, s0 = masked(0)
check("offset 0: mask=1 -> 191 (prime, pi=43), mask=0 -> 233 (prime, pi=51), gap 42",
      (s1, s0) == (191, 233) and is_p(191) and is_p(233) and pi(191) == 43 and pi(233) == 51 and s0 - s1 == 42)
check("pi(191)=43 is board code S, the last letter of PRIVATEKEYS; 91-40 = 51 = pi(233)",
      BOARD["43"] == "S" and SENT[:40].endswith("S") and len(SENT) - 40 == pi(233))
ew = [o for o in range(len(SENT) - 40 + 1) if all(map(is_p, masked(o))) and abs(masked(o)[0] - masked(o)[1]) == 42]
check(f"only offset 0 of {len(SENT) - 40 + 1} windows gives a prime pair with gap 42", ew == [0], f"offsets {ew}")

print("== 4943 marker (frozen Genesis object; not hashed, not an offset, not gated)")
F = 0xF73D92
check("0xF73D92 = 2 x 11 x 149 x 4943, 4943 prime", F == 2 * 11 * 149 * 4943 and is_p(4943), str(F))
check("4943 = p_661, 661 = |DBBI||FAED|", PR[660] == 4943 and len(TAPE) == 661)
check("pi(11)=5=|enter|, pi(149)=35=|shabefourfirsthintisyourlastcommand|",
      pi(11) == 5 == len("enter") and pi(149) == 35 == len("shabefourfirsthintisyourlastcommand"))

print("== look-elsewhere items, recorded and kept off the key list")
check("pi(42)=13=|matrixsumlist|, pi(31)=11=|thepassword|, pi(15)=6=|YOUWON|",
      pi(42) == 13 == len("matrixsumlist") and pi(31) == 11 == len("thepassword") and pi(15) == 6 == len("YOUWON"))
check("gaps 73-31=42, 82-67=15, pi(73)-pi(31)=10 spell 'PI.' on the board",
      (73 - 31, 82 - 67, pi(73) - pi(31)) == (42, 15, 10) and BOARD["42"] + BOARD["15"] + BOARD["10"] == "PI.")

n_fail = results.count(False)
print(f"\n{len(results)} checks, {n_fail} failed")
sys.exit(1 if n_fail else 0)
