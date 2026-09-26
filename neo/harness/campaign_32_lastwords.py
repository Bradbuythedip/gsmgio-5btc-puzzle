#!/usr/bin/env python3
"""Campaign 32 (fast): the 48/96-char last-word construction vs the 48/96-byte objects.

L48 = final 11 Architect words = 48 chars; L96 = final 21 words = 96 chars (2nd half == L48).
Objects: miniA (ct 32), salph_inner/miniAB (ct 80), P32T/inner96 (ct 80), cosmic (ct 1328).
Outside-the-box, hard gates only, no per-window EC brute:
  - a small EXPLICIT set of 32-byte privkey candidates -> address oracle (prize/second/planted)
  - derived AES keys -> decrypt, PKCS#7+printable, P32T freeze, 64-hex-in-plaintext -> address
  - XOR/OTP results -> Salted__/WIF/printable structure (cheap)
"""
import os, sys, hashlib, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Crypto.Cipher import AES
from aes_try import load_targets, evp_bytes_to_key, check_pt
from p32t_freeze import accept as p32t_accept
from btc_addr import addrs, N

ADDR={"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe":"prize","17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa":"second",
 "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9":"planted"}
def akey(b):
    if len(b)!=32: return None
    k=int.from_bytes(b,'big')
    if not(1<=k<N): return None
    c,u=addrs(k)
    for a in (c,u):
        if a in ADDR: return (ADDR[a],a)
    return None

words=open('/tmp/arch_words.txt').read().split()
L48="".join(words[-11:]); L96="".join(words[-21:]); assert len(L48)==48 and len(L96)==96
STR={"L48":L48,"L96":L96,"L48a":L96[:48],"L48b":L96[48:]}
T=load_targets(); OBJS={"miniA":T["miniA"],"salph":T["miniAB"],"P32T":T["inner96"],"cosmic":T["cosmic"]}
hits=[]

# ---- explicit 32-byte privkey candidates ----
pk=[]
def addpk(lbl,b):
    if len(b)==32: pk.append((lbl,b))
for sn,s in STR.items():
    sb=s.encode()
    addpk(f"sha({sn})",hashlib.sha256(sb).digest())
    addpk(f"sha2({sn})",hashlib.sha256(hashlib.sha256(sb).digest()).digest())
    for w,wn in ((sb[:32],"[:32]"),(sb[-32:],"[-32:]")): addpk(f"{sn}{wn}",w)
# miniA ct is 32 bytes -> XOR against every 32-byte pad derived from the strings
mc=OBJS["miniA"]["ct"]; addpk("miniA.ct",mc)
for sn,s in STR.items():
    sb=s.encode()
    for w,wn in ((sb[:32],"[:32]"),(sb[-32:],"[-32:]"),(hashlib.sha256(sb).digest(),"sha")):
        addpk(f"miniA.ct ^ {sn}{wn}", bytes(a^b for a,b in zip(mc,w)))
# 80-byte ct XOR 96/48 strings -> take 32-byte windows of the result at natural offsets
for oname in ("salph","P32T"):
    ct=OBJS[oname]["ct"]
    for sn,s in STR.items():
        sb=(s.encode()*3)[:80]
        x=bytes(a^b for a,b in zip(ct,sb))
        for off in (0,16,32,48):
            addpk(f"{oname}.ct^{sn}@{off}", x[off:off+32])
for lbl,b in pk:
    r=akey(b)
    if r: hits.append((f"ADDR {lbl}", r))
print(f"privkey candidates: {len(pk)}  address hits: {sum(1 for _ in hits)}")

# ---- derived AES keys -> decrypt ----
keys={}
for sn,s in STR.items():
    sb=s.encode(); keys[f"sha({sn})"]=hashlib.sha256(sb).digest()
    keys[f"{sn}[:32]"]=sb[:32]; keys[f"{sn}[-32:]"]=sb[-32:]
for kn,K in keys.items():
    for oname,o in OBJS.items():
        for ivn,iv in (("zero",bytes(16)),("saltdup",(o["salt"] or bytes(8))*2)):
            try: pt=AES.new(K,AES.MODE_CBC,iv).decrypt(o["ct"])
            except Exception: continue
            res=check_pt(pt)
            if res and res["hit"]: hits.append((f"HARNESS key={kn} {oname} iv={ivn}", pt[:48].decode('latin1','replace')))
            # 64-hex in plaintext -> privkey
            m=re.search(rb'[0-9a-fA-F]{64}', pt)
            if m:
                r=akey(bytes.fromhex(m.group(0).decode()))
                if r: hits.append((f"HEXKEY key={kn} {oname}", r))
            r2=akey(pt[:32]);  r3=akey(pt[16:48])
            if r2: hits.append((f"PTKEY key={kn} {oname} @0", r2))
            if r3: hits.append((f"PTKEY key={kn} {oname} @16", r3))
        fr=p32t_accept(K) if oname=="P32T" else None
        if fr and not fr.startswith("weak"): hits.append((f"FREEZE key={kn}", fr))

# ---- password form (raw+sha256hex) EVP for the record ----
for sn,s in STR.items():
    for pw in (s, hashlib.sha256(s.encode()).hexdigest()):
        for md in ("md5","sha256"):
            for oname,o in OBJS.items():
                if not o.get("salt"): continue
                Kk,IV=evp_bytes_to_key(pw.encode(),o["salt"],md,32)
                pt=AES.new(Kk,AES.MODE_CBC,IV).decrypt(o["ct"]); res=check_pt(pt)
                if res and res["hit"]: hits.append((f"PW {sn} {md} {oname}", pt[:48].decode('latin1','replace')))

# ---- XOR/OTP structure scan (cheap, no EC) ----
def struct(b,tag):
    if b[:8]==b"Salted__": hits.append((tag,"SALTED__"))
    for m in (b"xprv",b"5H",b"5J",b"5K",b"L",b"K",b"1GSMG"):
        pass
    pr=sum(1 for x in b if 32<=x<127)/len(b)
    if pr>=0.90: hits.append((tag,f"printable{pr:.2f}:{b[:40].decode('latin1','replace')}"))
for sn,s in STR.items():
    sb=s.encode()
    for oname,o in OBJS.items():
        full=b"Salted__"+(o["salt"] or b"")+o["ct"]
        for part,ob in (("ct",o["ct"]),("full",full)):
            ks=(sb*((len(ob)//len(sb))+1))[:len(ob)]
            struct(bytes(a^b for a,b in zip(ob,ks)), f"XOR {sn}^{oname}.{part}")

print("=== all hits ===")
for h in hits: print("  ",h)
print("TOTAL HITS:", len(hits))
