#!/usr/bin/env python3
"""Campaign 34: the third-door short list (sha256(X) -> privkey vs 1NULY7/prize/second).

X ONLY from named leftovers: 31, 73, 42, {1,4,21}, {1,4}, 331, 421, YOUWON, locktimes
629998/840003, the VIC sentence and its tail, the two layer-sum concats. NOT concatenations
of the four soup tokens. Hit -> X is the next AES answer for gate.py. Miss -> stop, do not grow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr_check import check
VIC="INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
X=["31","73","42","3173","7331","3142","317342","31 73","31 73 42","31-73-42","31_73_42",
   "1421","14 21","1 4 21","1,4,21","14","421","1","4","21",
   "331","421","331421","421331","331 421","421 331","YOUWON","youwon","Youwon",
   "629998","840003","629998840003","840003629998",VIC,VIC.lower(),
   "THEYALSONEEDFUNDSTOLIVE","theyalsoneedfundstolive","NEEDFUNDSTOLIVE","FUNDS","LIVE",
   "331360369421418441396","422451460512509532487"]
print("third-door X candidates:", len(X))
m=check([(x,x.encode()) for x in X])
print("MATCHES:", m if m else "none -> stop, do not grow (step 3 rule)")
