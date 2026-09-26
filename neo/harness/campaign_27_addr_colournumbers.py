#!/usr/bin/env python3
"""Campaign 27: "Yellow has a number and so does Blue" read literally as the colour codes.

Pre-registered operand set (from the authenticated genesis image, sampled this session):
  yellow #FFF200, blue #3F48CC, red rule #ED1C24, off-white #FEFEFE, plus the 24-bit colour
  frame F73D92 for comparison. Representations: hex lower/upper, decimal, 3-byte packed,
  yellow||blue and blue||yellow in each. Offline address oracle only (12 addresses each).
No AES. No primes applied here: the prime edit has no named operand yet, and applying it
would widen this into a search.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr_check import check
Y, B, R, F, C = 0xFFF200, 0x3F48CC, 0xED1C24, 0xFEFEFE, 0xF73D92
objs = {}
for name, v in (("yellow", Y), ("blue", B), ("red", R), ("fefefe", F), ("frame", C)):
    objs[f"{name}-hexl"] = f"{v:06x}".encode(); objs[f"{name}-hexu"] = f"{v:06X}".encode()
    objs[f"{name}-dec"] = str(v).encode(); objs[f"{name}-packed"] = v.to_bytes(3, 'big')
for a, b, tag in ((Y, B, "yb"), (B, Y, "by")):
    objs[f"{tag}-hexl"] = f"{a:06x}{b:06x}".encode(); objs[f"{tag}-hexu"] = f"{a:06X}{b:06X}".encode()
    objs[f"{tag}-dec"] = f"{a}{b}".encode(); objs[f"{tag}-packed"] = a.to_bytes(3, 'big') + b.to_bytes(3, 'big')
    objs[f"{tag}-hexl-sp"] = f"{a:06x} {b:06x}".encode()
objs["ybf-hexl"] = f"{Y:06x}{B:06x}{F:06x}".encode(); objs["ybr-hexl"] = f"{Y:06x}{B:06x}{R:06x}".encode()
objs["hash-yb"] = f"#{Y:06X}#{B:06X}".encode(); objs["hash-yb-l"] = f"#{Y:06x}#{B:06x}".encode()
cands = list(objs.items())
print("objects:", len(cands))
print("matches:", check(cands))
