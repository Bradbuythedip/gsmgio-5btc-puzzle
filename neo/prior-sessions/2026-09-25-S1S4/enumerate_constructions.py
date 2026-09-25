#!/usr/bin/env python3
"""Document the seed->scalar candidate set C1-C6 and each seed's OFFSET-0 direct address
vs the prize address. This is documentation, NOT a BSGS run: it computes only the direct
point (offset 0) for each seed under each construction. Prints LCP with the prize; a real
solution would show the full 34-char match, never seen here."""
import hashlib, sys
sys.path.insert(0,'.')
from btc import addrs_from_key
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
PRIZE="1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
S={1:"223e3dea019fd03dc730467abfcc068bd329b222cfbe2fa71339ac57d25ef545",
   2:"376103f4bd0300b073ffc8fc70d132b3f1c3ccd90ace4e0fe4fbb183cb66bd51",
   3:"748a3ea15dc34e20c58e11e7407740904d9011debc9846b0b7a6dab54ad85123",
   4:"b49c87570a54e14d6af2790924059ff859f345eaf09641c64734c66c190bdc75"}
raw={i:bytes.fromhex(h) for i,h in S.items()}; sha=lambda x: hashlib.sha256(x).digest()
def lcp(a,b):
    c=0
    for x,y in zip(a,b):
        if x==y: c+=1
        else: break
    return c
cons={"C1 raw-int":lambda i:int(S[i],16)%N,
 "C2 sha256(hex-ascii)":lambda i:int.from_bytes(sha(S[i].encode()),"big")%N,
 "C3 sha256(raw)":lambda i:int.from_bytes(sha(raw[i]),"big")%N,
 "C4 sha256d(raw)":lambda i:int.from_bytes(sha(sha(raw[i])),"big")%N,
 "C5 rev-raw-int":lambda i:int.from_bytes(raw[i][::-1],"big")%N,
 "C6 sha256(HEX-UPPER)":lambda i:int.from_bytes(sha(S[i].upper().encode()),"big")%N}
for cname,fn in cons.items():
    row=[]
    for i in (1,2,3,4):
        d=fn(i)%N; comp,unc=addrs_from_key(d.to_bytes(32,"big"))
        l=max(lcp(comp,PRIZE),lcp(unc,PRIZE))
        row.append(f"S{i}:LCP{l}"+("<==PRIZE" if (comp==PRIZE or unc==PRIZE) else ""))
    print(f"{cname:22s} "+"  ".join(row))
