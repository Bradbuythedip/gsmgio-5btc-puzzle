#!/usr/bin/env python3
"""Campaign 01: singles + bounded seven-token intertwined combos.

Rationale (see neo/LEDGER.md):
- Beaufort text: "seven intertwined passwords", "reinserting the prime basics".
- 2023-02-23 official hint order: yellow blue primes matrixsumlist
  lastwordsbeforearchichoice yinyang thepassword.
- SalPhaseIon tail: "sha b4 first hint is your last command ... sha b4 ans too"
  and the pinned convention from solved phases: passphrase = sha256hex(answer).
"""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness, MAT

def phase0_matrix():
    rows = []
    for line in open(os.path.join(MAT, "phase0_grid.txt")).read().split():
        rows.append([1 if ch in "1b" else 0 for ch in line])
    return rows

def msl_variants():
    m = phase0_matrix()
    rs = [sum(r) for r in m]
    cs = [sum(c) for c in zip(*m)]
    rowdec = [int("".join(map(str, r)), 2) for r in m]
    v = {
        "rowsums": "".join(map(str, rs)),
        "rowsums_space": " ".join(map(str, rs)),
        "rowsums_comma": ",".join(map(str, rs)),
        "colsums": "".join(map(str, cs)),
        "colsums_space": " ".join(map(str, cs)),
        "total": str(sum(rs)),
        "rowdec": "".join(map(str, rowdec)),
        "rowdec_space": " ".join(map(str, rowdec)),
    }
    return v

PHASE22 = ("causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F"
           "63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F"
           "33302073656D695420656854B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1")

SINGLES = [
    # labels / literal segments
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "thepassword", "salphaseion", "SalPhaseIon", "cosmicduality", "CosmicDuality",
    "yinyang", "yingyang", "duality", "balance",
    "shabefour", "shabefanstoo", "anstoo", "yourlastcommand",
    "firsthintisyourlastcommand", "shabefourfirsthintisyourlastcommand",
    # "first hint is your last command" readings
    "followthewhiterabbit", "whiterabbit", "FollowTheWhiteRabbit",
    "theseedisplanted", "gsmg.io/theseedisplanted",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    # phase passwords / known answers
    "causality", PHASE22,
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "choiceisanillusioncreatedbetweenthosewithpowerandthosewithout",
    # VIC / beaufort derived
    "halfandbetterhalf", "betterhalf", "half", "halfbetterhalf",
    "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive",
    "fubcdoralethingkymvpszjqwx.", "fubcdora/lethingkymvpszjqwx.",
    "oneforonefourforone", "thematrixhasyou", "wakeupneo", "knockknockneo",
    "returntothesource", "thesource", "sourcecodes", "reinsertingtheprimebasics",
    "primebasics", "seveninterwinedpasswords", "sevenintertwinedpasswords",
    "hundredfourty", "140", "ciaobella", "ciaobellao", "goodluck",
    "denialisthemostpredictableofallhumanresponses",
    # matrix figures
    "hope", "choice", "theproblemischoice", "everythingthathasabeginninghasanend",
    "ifiwereyouiwouldhopethatwedontmeetagain", "wewont",
    "hopeitisthequintessentialhumandelusionsimultaneouslythesourceofyourgreateststrengthandyourgreatestweakness",
    "architect", "theone", "neo", "morpheus", "trinity", "oracle", "keymaker",
    "merovingian", "persephone",
    # misc community
    "april", "gsmg101adressapril", "gsmg", "gsmgio", "GSMG.IO", "5btc", "5BTC",
    "puzzle", "theflowerblossoms",
    "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735",
]

YELLOW = ["yellow", "9", "0"]
BLUE = ["blue", "15", "1"]
PRIMES = ["primes", "2357", "235711"]
LWBAC = ["hope", "everythingthathasabeginninghasanend", "theproblemischoice"]
YY = ["yinyang", "cosmicduality"]
TP = ["thispassword", "thepassword"]

def main():
    h = Harness("campaign_01")
    msl = msl_variants()

    for s in SINGLES:
        h.try_family(s, "single")
    for name, val in msl.items():
        h.try_family(val, f"msl:{name}")
        h.try_family("matrixsumlist" + val, f"msl-labeled:{name}")

    # seven-token cartesian, hint order
    MSL = [msl["rowsums"], "matrixsumlist"]
    n = 0
    for combo in itertools.product(YELLOW, BLUE, PRIMES, MSL, LWBAC, YY, TP):
        h.try_family("".join(combo), "seven-hint-order")
        n += 1
    # salphaseion decode order: msl, enter, lwbac, tp
    for combo in itertools.product(MSL, ["enter"], LWBAC, TP):
        h.try_family("".join(combo), "salph-order")
        n += 1
    print("combos:", n)
    h.finish("campaign_01")

if __name__ == "__main__":
    main()
