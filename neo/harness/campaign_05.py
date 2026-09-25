#!/usr/bin/env python3
"""Campaign 05: large bounded cartesian under the pinned convention only.

To afford ~1.6M candidates, restrict to kdf s2 (the empirically pinned one) and the
two passphrase forms that matter: raw and sha256hex (the creator's habit).
Targets: the three plausible key-containers (miniA, miniAB, inner96) + cosmic.

Also covers "sha b4 ans too" as structure: concatenations of per-answer sha256 hexes.
"""
import hashlib, itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness
from campaign_01 import msl_variants, PHASE22

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

TARGETS = ["miniA", "miniAB", "inner96", "cosmic"]
KDFS = ["s2"]

msl = msl_variants()
YELLOW = ["yellow", "0", "9", "nine", "geel"]
BLUE = ["blue", "1", "15", "fifteen", "blauw"]
PRIMES = ["primes", "prime", "2357", "235711", "23571113", "2357111317",
          "235711131719", "23571113171923", "priemgetallen", "primebasics"]
MSL = [msl["rowsums"], msl["colsums"], msl["rowdec"], msl["total"],
       "matrixsumlist", msl["rowsums_space"]]
LWBAC = ["hope", "everythingthathasabeginninghasanend", "theproblemischoice",
         "lastwordsbeforearchichoice", "wewont",
         "ifiwereyouiwouldhopethatwedontmeetagain",
         "hopeitisthequintessentialhumandelusion",
         "denialisthemostpredictableofallhumanresponses"]
YY = ["yinyang", "yingyang", "cosmicduality", "duality", "taijitu", "balance"]
TP = ["thispassword", "thepassword", PHASE22,
      "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
      "theflowerblossomsthroughwhatseemstobeaconcretesurface", "causality"]

def main():
    h = Harness("campaign_05")

    def hit(pw, note):
        h.try_pw(pw, note, targets=TARGETS, kdfs=KDFS)
        h.try_pw(sha(pw), note + "|sha", targets=TARGETS, kdfs=KDFS)

    n = 0
    # full 7-component product, hint order
    for c in itertools.product(YELLOW, BLUE, PRIMES, MSL, LWBAC, YY, TP):
        hit("".join(c), "seven")
        n += 1
    # salphaseion 4-component order: msl, enter, lwbac, tp
    for c in itertools.product(MSL, ["enter", ""], LWBAC, TP):
        hit("".join(c), "four")
        n += 1
    # sha-of-each-answer concatenations (2- and 3-part)
    ANS = {"msl": MSL[:4], "lwbac": LWBAC[:6], "tp": TP[:4]}
    for a in ANS["lwbac"]:
        for b in ANS["tp"]:
            hit(sha(a) + sha(b), "shacat2")
            n += 1
    for a in ANS["msl"]:
        for b in ANS["lwbac"]:
            for c in ANS["tp"]:
                hit(sha(a) + sha(b) + sha(c), "shacat3")
                n += 1
    print("candidates:", n)
    h.finish("campaign_05")

if __name__ == "__main__":
    main()
