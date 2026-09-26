#!/usr/bin/env python3
"""BSGS harness with PLANTED positive control. Recovers n with n*G = Q, |n| in [0,R).
House rules: prints FOUND/STOP and the recovered offset MAGNITUDE for a *planted* control
only; never prints a puzzle key. Uses coincurve point ops + numpy sorted x-prefix table."""
import numpy as np, hashlib, time, sys
from coincurve import PrivateKey, PublicKey
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def scalar_pub(d): return PrivateKey((d%N).to_bytes(32,"big")).public_key
def add(P,Q): return PublicKey.combine_keys([P,Q])
def neg(P): return P.multiply((N-1).to_bytes(32,"big"))
def xkey(P):  # first 8 bytes of compressed x as uint64
    return int.from_bytes(P.format(True)[1:9],"big")

def bsgs(Q, R):
    """find n in [0,R) with n*G==Q, else None. m~sqrt(R)."""
    m=1<<((R.bit_length()+1)//2)
    giants=(R//m)+1
    # baby table: j*G for j in [0,m)
    G=scalar_pub(1)
    keys=np.empty(m,dtype=np.uint64); P=G
    keys[0]=xkey(scalar_pub(0)) if False else 0
    # j=0 -> point at infinity has no serialization; handle j=0 separately (n=0)
    if Q is None: return 0
    cur=G
    js=np.empty(m,dtype=np.uint64)
    for j in range(1,m):
        js[j]=xkey(cur); cur=add(cur,G)
    js[0]=0
    order=np.argsort(js,kind="stable"); js_s=js[order]
    mG=scalar_pub(m); mGneg=neg(mG)
    # giant: Q - i*mG
    cur=Q
    for i in range(0,giants):
        k=xkey(cur)
        lo=np.searchsorted(js_s,k,"left"); hi=np.searchsorted(js_s,k,"right")
        for idx in order[lo:hi]:
            j=int(idx)
            if scalar_pub(i*m+j).format(True)==Q.format(True):
                return i*m+j
        cur=add(cur,mGneg)
    return None

def signed_bsgs(P, k_base, R):
    """search n in (-R,R) with (k_base+n)*G == P."""
    base=scalar_pub(k_base)
    if P.format(True)==base.format(True):  # n==0 exactly
        return 0
    Q=add(P, neg(base))                    # Q=(P - k_base*G)= n*G  (n!=0 here)
    r=bsgs(Q,R)
    if r is not None: return r
    r=bsgs(neg(Q),R)                        # negative branch
    if r is not None: return -r
    return None

if __name__=="__main__":
    print("[control 1] tiny planted offset, tiny window")
    k=int.from_bytes(hashlib.sha256(b"base-control").digest(),"big")%N
    for n0 in (0, 1, 12345, 0xFEDCB):
        P=scalar_pub(k+n0)
        got=signed_bsgs(P,k,1<<20)
        print(f"   planted n0={n0:#x} -> recovered {'FOUND n0 (magnitude '+hex(abs(got))+')' if got==n0 else 'MISMATCH '+str(got)}")
    print("[control 2] offset 0x1234567ABC (~2^36.2), window 2^38  (proves scale)")
    t0=time.time()
    k=int.from_bytes(hashlib.sha256(b"scale-control").digest(),"big")%N
    n0=0x1234567ABC
    P=scalar_pub(k+n0)
    got=signed_bsgs(P,k,1<<38)
    ok = got==n0
    print(f"   {'FOUND' if ok else 'STOP-FAIL'}: recovered offset magnitude {hex(abs(got)) if got is not None else None}, matches plant={ok}, {time.time()-t0:.1f}s")
    print("[control 3] negative planted offset")
    P=scalar_pub(k-0xABCDEF)
    got=signed_bsgs(P,k,1<<38)
    print(f"   planted -0xABCDEF -> {'FOUND (neg)' if got==-0xABCDEF else 'MISMATCH '+str(got)}")
