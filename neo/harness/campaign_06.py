#!/usr/bin/env python3
"""Campaign 06: hint-image vocabulary + "zeroed out" transforms + 2357 permutations.

Sources (all creator messages):
- 2021-12-25: "some characters need to be 'zeroed out'"  -> o->0 / remove-o transforms
- 2021-03-01: primes 2,3,5,7, "too many combinations"    -> permutations/subsets of 2357
- 2023-08-06: "ying yang" milestone, "salvation part", Mr Robot last scene, France
- 2023-01-12: theory of everything valid path
- 2023-08-03: "shine us some 'light'", "Are you really looking for just the btc...?"
"""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness
from campaign_01 import msl_variants

VOCAB = [
    "salvation", "thesalvation", "salvationpart", "light", "shinelight",
    "letthereblight", "lettherebelight", "lumiere", "helloelliot", "hellofriend",
    "mrrobot", "fsociety", "evilcorp", "whiterose", "darkarmy", "elliot",
    "elliotalderson", "jaune", "bleu", "nombrespremiers", "premiers",
    "theoryofeverything", "thetheoryofeverything", "toe", "42", "fortytwo",
    "hawking", "stephenhawking", "grandunifiedtheory", "gut", "stringtheory",
    "mtheory", "quantumgravity", "emc2", "anotherdoor", "thereisanotherdoor",
    "seconddoor", "thirddoor", "door", "backdoor", "zeroedout", "zeroed",
    "yingyang", "onceyouhitayingyang", "areyoureallylookingforjustthebtc",
    "thepuzzletalksforme", "thepuzzlespeaksforme", "mainprice", "themainprice",
    "tinyfraction", "ciao", "france",
]

BASES_FOR_ZERO = [
    "matrixsumlist", "thispassword", "thepassword", "lastwordsbeforearchichoice",
    "followthewhiterabbit", "cosmicduality", "yinyang", "yingyang", "hope",
    "anotherdoor", "thereisanotherdoor", "door", "salvation", "salphaseion",
    "enter", "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "gsmg.io/theseedisplanted", "theseedisplanted", "helloelliot",
    "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangthepassword",
    "halfandbetterhalf", "betterhalf",
]

URL = "gsmg.io/theseedisplanted"
LOWBITS = [ord(c) & 1 for c in URL]

def main():
    h = Harness("campaign_06")
    for s in VOCAB:
        h.try_family(s, "vocab")

    # zeroed-out transforms
    for b in BASES_FOR_ZERO:
        h.try_family(b.replace("o", "0"), "zero:o->0")
        h.try_family(b.replace("o", ""), "zero:drop-o")
        h.try_family(b.replace("o", "0").replace("O", "0"), "zero:oO->0")
    # URL with low-bit-0 (yellow) chars zeroed / dropped
    z1 = "".join('0' if not bit else c for c, bit in zip(URL, LOWBITS))
    z2 = "".join(c for c, bit in zip(URL, LOWBITS) if bit)
    h.try_family(z1, "zero:url-yellow->0")
    h.try_family(z2, "zero:url-drop-yellow")

    # 2357 permutations and ordered subsets
    digs = "2357"
    perms = set()
    for r in range(1, 5):
        for p in itertools.permutations(digs, r):
            perms.add("".join(p))
    for p in sorted(perms):
        h.try_family(p, "primeperm")

    # prime-perm inside the seven-token frame (bounded)
    msl = msl_variants()
    for p in sorted(perms, key=len, reverse=True)[:24]:  # the 4-digit perms
        for m in (msl["rowsums"], "matrixsumlist"):
            for lw in ("hope", "everythingthathasabeginninghasanend"):
                for tp in ("thispassword", "thepassword"):
                    for yy in ("yinyang", "yingyang"):
                        for yb in ("01", "blueyellow", "yellowblue", ""):
                            h.try_family(yb + p + m + lw + yy + tp, "seven-primeperm")

    h.finish("campaign_06")

if __name__ == "__main__":
    main()
