#!/usr/bin/env python3
"""Campaign 38: the creator's personal-infrastructure strings, one gate pass.

Motivated by the close-friends hint (#66573/66574): the missing input is something a friend
recognizes as a direction but cannot execute. The only non-Matrix, creator-personal material is
his self-description / contact infra. NOTE: the email electronic_engineer@naver.com and the
donation address 1QzA8dwEgp... are USER-supplied; they are NOT in this repo's authenticated
archive (materials/, README). Run once, then freeze.
"""
import hashlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Crypto.Cipher import AES
from aes_try import load_targets, evp_bytes_to_key, check_pt
from p32t_freeze import accept
from addr_check import check
T=load_targets(); LOCKS={"salph":T["miniAB"],"P32T":T["inner96"]}
X=["electronic_engineer","electronicengineer","electronic engineer","ElectronicEngineer",
   "electronic_engineer@naver.com","electronicengineer@naver.com","electronic_engineernaver",
   "naver","naver.com","Naver","NAVER",
   "1QzA8dwEgpSAbMni7S1U5GRuko3Fxnt94","1qza8dwegpsabmni7s1u5gruko3fxnt94"]
hits=[]
for x in X:
    for base in (x, hashlib.sha256(x.encode()).hexdigest()):
        for md in ("md5","sha256"):
            for ln,o in LOCKS.items():
                K,IV=evp_bytes_to_key(base.encode(),o["salt"],md,32)
                r=check_pt(AES.new(K,AES.MODE_CBC,IV).decrypt(o["ct"]))
                if r and r["hit"]: hits.append((x[:24],ln,md,"HARNESS"))
                if ln=="P32T":
                    a=accept(K)
                    if a and not a.startswith("weak"): hits.append((x[:24],ln,md,a))
print("AES lock hits:", hits or "none")
print("address hits:", check([(x,x.encode()) for x in X]) or "none")
