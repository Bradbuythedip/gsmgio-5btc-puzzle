#!/usr/bin/env python3
"""Campaign 33: FAED-derived creator-authenticated material as password material.

Objects (a=0..i=8 layer sums of the DBBI/FAED 7x13 stack): [331,360,369,421,418,441,396];
the 24-char FAED tail ibibbibdcbahaidhfahiihic; the 24-cell colour frame BBBBYBBBYYBBBBYBBYYBYYBY;
and 31/73/42. Bounded, self-proving: check_pt (PKCS#7+printable), P32T freeze, and any 64-hex
run in the plaintext -> address oracle. Locks: miniA, salph (miniAB), P32T (inner96).
"""
import os, sys, hashlib, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Crypto.Cipher import AES
from aes_try import load_targets, evp_bytes_to_key, check_pt
from p32t_freeze import accept as p32t_accept
from btc_addr import addrs, N
ADDR={"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe":"prize","17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa":"second","1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9":"planted"}
def akey(b):
    if len(b)!=32: return None
    k=int.from_bytes(b,'big')
    return next((( ADDR[a],a) for a in addrs(k) if a in ADDR), None) if 1<=k<N else None

T=load_targets(); LOCKS={"miniA":T["miniA"],"salph":T["miniAB"],"P32T":T["inner96"]}
ls_a0=[331,360,369,421,418,441,396]; ls_a1=[422,451,460,512,509,532,487]
tail="ibibbibdcbahaidhfahiihic"; frame="BBBBYBBBYYBBBBYBBYYBYYBY"
swap=frame.translate(str.maketrans("BY","YB"))
strs=[]
def add(s): 
    if s and s not in strs: strs.append(s)
add("".join(map(str,ls_a0))); add("".join(map(str,ls_a1)))
add(" ".join(map(str,ls_a0)))
for j in ("","-","_",".",":"): add(f"31{j}73{j}42")
add(tail); add(tail[::-1]); add(frame); add(frame[::-1]); add(swap)
add("yellowblueprimes")
base=list(strs)
for b in base:
    add("yellowblueprimes"+b)
# binary key material: layer sums as 4-byte BE/LE concat (28 bytes)
bins={"be28":b"".join(x.to_bytes(4,'big') for x in ls_a0),
      "le28":b"".join(x.to_bytes(4,'little') for x in ls_a0),
      "be28a1":b"".join(x.to_bytes(4,'big') for x in ls_a1)}

hits=[]
def test_pw(pwbytes, tag):
    for md in ("md5","sha256"):
        for ln,o in LOCKS.items():
            K,IV=evp_bytes_to_key(pwbytes,o["salt"],md,32)
            pt=AES.new(K,AES.MODE_CBC,IV).decrypt(o["ct"]); r=check_pt(pt)
            if r and r["hit"]: hits.append((f"{tag}|{md}|{ln}","HIT:"+pt[:48].decode('latin1','replace')))
            m=re.search(rb'[0-9a-fA-F]{64}',pt)
            if m and akey(bytes.fromhex(m.group(0).decode())): hits.append((f"{tag}|{md}|{ln}","HEXKEY-ADDR"))
        # raw-key mode: key=sha256(pw)
    Kr=hashlib.sha256(pwbytes).digest()
    if p32t_accept(Kr) and not p32t_accept(Kr).startswith("weak"): hits.append((f"{tag}|rawkey","FREEZE"))
    if akey(Kr): hits.append((f"{tag}|rawkey","ADDR"))

n=0
for s in strs:
    test_pw(s.encode(), f"raw:{s[:24]}"); n+=1
    test_pw(hashlib.sha256(s.encode()).hexdigest().encode(), f"sha256hex:{s[:20]}"); n+=1
for bn,bb in bins.items():
    test_pw(bb, f"bin:{bn}"); n+=2
print(f"strings:{len(strs)} password-forms tested:{n} (x2 KDF x3 locks + rawkey)  HITS:{len(hits)}")
for h in hits: print("  ",h)
