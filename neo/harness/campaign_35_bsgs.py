#!/usr/bin/env python3
"""Campaign 35: additive-vanity BSGS on the prize point.

Hypothesis (user): d_prize = d0 + t (mod n) for a puzzle-derived d0 and a small vanity
counter t, so Q_prize - d0*G = t*G is a bounded discrete log. Test a SMALL preregistered set
of d0 = sha256(source-derived object) with signed BSGS over |t| < 2^38 (the validated window).
Only creator-authenticated / solved-chain strings; NO cosmic_A/chain4/witness material.

House rule: for a planted CONTROL, print the recovered offset magnitude to prove the tool works.
For a real candidate, print only FOUND/STOP and the candidate label -- never a recovered scalar.
"""
import numpy as np, hashlib, time, sys, os
from coincurve import PrivateKey, PublicKey
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
def spub(d): return PrivateKey((d%N).to_bytes(32,"big")).public_key
def add(P,Q): return PublicKey.combine_keys([P,Q])
def neg(P): return P.multiply((N-1).to_bytes(32,"big"))
def xk(P): return int.from_bytes(P.format(True)[1:9],"big")

R=1<<38
M=1<<22
G=spub(1)
print(f"building baby table m={M} ...", flush=True); t0=time.time()
js=np.empty(M,dtype=np.uint64); cur=G
for j in range(1,M): js[j]=xk(cur); cur=add(cur,G)
js[0]=0
order=np.argsort(js,kind="stable"); js_s=js[order]
mG=spub(M); mGneg=neg(mG)
print(f"  table built in {time.time()-t0:.1f}s", flush=True)

def bsgs(Q):
    if Q is None: return 0
    cur=Q; giants=(R//M)+1
    for i in range(giants):
        k=xk(cur); lo=np.searchsorted(js_s,k,"left"); hi=np.searchsorted(js_s,k,"right")
        for idx in order[lo:hi]:
            j=int(idx)
            if spub(i*M+j).format(True)==Q.format(True): return i*M+j
        cur=add(cur,mGneg)
    return None
def signed(P,kbase):
    base=spub(kbase)
    if P.format(True)==base.format(True): return 0
    Q=add(P,neg(base))
    r=bsgs(Q)
    if r is not None: return r
    r=bsgs(neg(Q))
    return -r if r is not None else None

# prize point
X=0xf4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464
Y=0x9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559
Qprize=PublicKey(b'\x04'+X.to_bytes(32,'big')+Y.to_bytes(32,'big'))

# planted control (proves the negative is meaningful)
kc=int.from_bytes(hashlib.sha256(b"scale-control").digest(),"big")%N
n0=0x1234567ABC
gc=signed(spub(kc+n0),kc)
print(f"[control] window 2^38, planted 2^36.2: {'PASS mag='+hex(abs(gc)) if gc==n0 else 'FAIL '+str(gc)}", flush=True)

P32MONSTER="causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1"
TOK=["yellowblueprimes","matrixsumlist","lastwordsbeforearchichoice","yinyang",
 "intheextinctionoftheentirenessofyourselfselfgood",
 "luckneverthelessireallyhopeyouretheoneciaobellao",
 "intheextinctionoftheentirenessofyourselfselfgoodluckneverthelessireallyhopeyouretheoneciaobellao",
 "ireallyhopeyouretheone","ciaobellao","331360369421418441396",
 "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
 "causality","jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
 "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
 "thematrixhasyou","theseedisplanted",P32MONSTER]
print(f"candidates: {len(TOK)}  window +-2^38", flush=True)
found=[]
for t in TOK:
    d0=int.from_bytes(hashlib.sha256(t.encode()).digest(),"big")%N
    ts=time.time(); r=signed(Qprize,d0)
    lbl=t[:40]
    if r is not None: found.append(lbl); print(f"  *** FOUND *** sha256({lbl!r}) is d0; prize = d0 + t  [{time.time()-ts:.0f}s]", flush=True)
    else: print(f"  STOP sha256({lbl!r}) [{time.time()-ts:.0f}s]", flush=True)
print("FOUND:", found if found else "none -> additive-vanity from these d0 is empty over |t|<2^38")
