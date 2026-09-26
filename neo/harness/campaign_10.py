#!/usr/bin/env python3
"""Campaign 10: ordered two-token combinations of puzzle-core vocabulary.

The Architect text says "seven intertwined passwords ... bruteforcing might be
required". Before the full 7-way space, exhaust the 2-way space over a curated
vocabulary (labels, decoded answers, Matrix/Mr-Robot terms, creator phrases), with
a few joiners, each also as sha256hex. Target the authenticated locks.
"""
import hashlib, itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness
from campaign_01 import msl_variants

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

TARGETS = ["miniA", "miniAB", "inner96", "cosmic"]

msl = msl_variants()

VOCAB = sorted(set([
    # structural labels / decoded SalPhaseIon tokens
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "thepassword", "yinyang", "yingyang", "primes", "yellow", "blue",
    "shabef", "anstoo", "yourlastcommand", "firsthint",
    # numeric answers
    "0", "1", "2357", msl["rowsums"], "42", "140", "1357",
    # matrix / free-will vocabulary
    "hope", "choice", "theone", "neo", "morpheus", "trinity", "oracle",
    "architect", "keymaker", "merovingian", "thematrixhasyou", "wakeupneo",
    "followthewhiterabbit", "whiterabbit", "thesource", "returntothesource",
    "freewill", "causality",
    # phase answers
    "jacquefresco", "giveitjustonesecond", "heisenberg",
    # VIC / beaufort derived
    "half", "betterhalf", "halfandbetterhalf", "salvation",
    "reinserttheprimebasics", "primebasics",
    # mr robot / cosmic
    "fsociety", "mrrobot", "cosmicduality", "duality", "salphaseion",
    # creator phrases
    "thepuzzlespeaksforme", "thehardestpartisdone", "anotherdoor",
]))

JOINS = ["", " ", "-", "z", "_"]

def main():
    h = Harness("campaign_10")
    seen_pw = set()
    for a, b in itertools.product(VOCAB, repeat=2):
        for j in JOINS:
            pw = a + j + b
            if pw in seen_pw:
                continue
            seen_pw.add(pw)
            h.try_pw(pw, "pair", targets=TARGETS, kdfs=["s2"])
            h.try_pw(sha(pw), "pair|sha", targets=TARGETS, kdfs=["s2"])
    print("unique passwords:", len(seen_pw))
    h.finish("campaign_10")

if __name__ == "__main__":
    main()
