#!/usr/bin/env python3
"""Campaign 03: "in front of your eyes" hash-chain candidates, book vocab,
beaufort-text numbers, and 7-token order permutations (labels and best-guess values).
"""
import hashlib, itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness
from campaign_01 import msl_variants, PHASE22

URLHASH = "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32"
CAPTION = "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

SINGLES = [
    URLHASH, URLHASH.upper(),
    CAPTION, CAPTION.lower(),
    "GSMGIO5BTCPUZZLECHALLENGE", "gsmgio5btcpuzzlechallenge",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    sha("causality"), sha(PHASE22),
    "250f37726d6862939f723edc4f993fde9d33c6004aab4f2203d9ee489d61ce4c",
    sha("theflowerblossomsthroughwhatseemstobeaconcretesurface"),
    # book cover
    "mysteriesoftheunknown", "MysteriesOfTheUnknown", "timelife", "timelifebooks",
    "cosmicdualitymysteriesoftheunknown", "mysteriesoftheunknowncosmicduality",
    # beaufort-text numbers
    "23", "16", "7", "23167", "231607", "twentythree", "sixteen", "seven",
    "twentythreesixteenseven", "140", "hundredfourty", "hundredforty",
    "worthhundredfourtyoftheinvestment",
    # help us build it / gsmg product
    "helpusbuildit", "pleasejusthelpusbuildit",
]

LABELS = ["yellow", "blue", "primes", "matrixsumlist",
          "lastwordsbeforearchichoice", "yinyang", "thepassword"]

def main():
    h = Harness("campaign_03")
    for s in SINGLES:
        h.try_family(s, "eyes/book/numbers")

    msl = msl_variants()
    VALUES = ["0", "1", "2357", msl["rowsums"], "hope", "yinyang", "thispassword"]

    for name, toks in (("labels", LABELS), ("values", VALUES)):
        for perm in itertools.permutations(toks):
            h.try_family("".join(perm), f"perm7:{name}")

    # z / newline / space joins in hint order
    for name, toks in (("labels", LABELS), ("values", VALUES)):
        for sep in ("z", "\n", " ", "-"):
            h.try_family(sep.join(toks), f"join7:{name}:{sep!r}")

    h.finish("campaign_03")

if __name__ == "__main__":
    main()
