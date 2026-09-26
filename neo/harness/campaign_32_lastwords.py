#!/usr/bin/env python3
"""Campaign 32: the 48/96-char last-word construction vs the 48/96-byte objects.

L48 = final 11 Architect words = 48 chars; L96 = final 21 words = 96 chars (splits 48/48,
2nd half == L48). Objects: miniA (ct 32), salph_inner/miniAB (ct 80), P32T/inner96 (ct 80).
Outside-the-box operations, hard gates only:
  - address oracle: ANY 32-byte read (XOR result, decrypt window) that spends 1GSMG1/17ucy1
  - freeze oracle on P32T; PKCS#7+printable on full decrypts
  - XOR/OTP results scanned for 'Salted__', 'xprv', WIF prefix, printability, and privkeys
No password 'battery' beyond the directed set; every accept is self-proving.
"""
import os, sys, hashlib, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Crypto.Cipher import AES
from aes_try import load_targets, evp_bytes_to_key, check_pt
from p32t_freeze import accept as p32t_accept
from btc_addr import addrs, N

TARGETS_ADDR={"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe":"prize",
 "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa":"second",
 "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9":"planted"}
def addr_hit(b32):
    if len(b32)!=32: return None
    k=int.from_bytes(b32,'big')
    if not (1<=k<N): return None
    c,u=addrs(k)
    for a in (c,u):
        if a in TARGETS_ADDR: return (TARGETS_ADDR[a],a)
    return None

words=open('/tmp/arch_words.txt').read().split()
L48="".join(words[-11:]); L96="".join(words[-21:])
assert len(L48)==48 and len(L96)==96 and L96[48:]==L48
L48a, L48b = L96[:48], L96[48:]
STR={"L48":L48,"L96":L96,"L48a":L48a,"L48b":L48b}

T=load_targets()
OBJS={"miniA":T["miniA"],"salph":T["miniAB"],"P32T":T["inner96"],"cosmic":T["cosmic"]}

def scan_bytes(b, tag, hits):
    # structure signals in a byte string
    if b[:8]==b"Salted__": hits.append((tag,"SALTED__"))
    for m in (b"xprv",b"1GSMG",b"5H",b"5J",b"5K",b"KG",b"L1"):
        if b[:len(m)]==m: hits.append((tag,"magic:"+m.decode('latin1')))
    pr=sum(1 for x in b if 32<=x<127)/len(b)
    if pr>=0.9: hits.append((tag,f"printable{pr:.2f}:"+b[:40].decode('latin1','replace')))
    # any 32-byte window as privkey
    for off in range(0,max(1,len(b)-31)):
        w=b[off:off+32]
        if len(w)==32:
            r=addr_hit(w)
            if r: hits.append((tag,f"ADDR@{off}:{r}"))

def main():
    hits=[]
    # ---- 1. XOR / one-time-pad: last-words ASCII vs object bytes ----
    for sname,s in STR.items():
        sb=s.encode()
        for oname,o in OBJS.items():
            for part,ob in (("ct",o["ct"]),("full",b"Salted__"+ (o["salt"] or b"") + o["ct"])):
                # cycle/truncate the string to the byte length
                ks=(sb*((len(ob)//len(sb))+1))[:len(ob)]
                x=bytes(a^b for a,b in zip(ob,ks))
                scan_bytes(x, f"XOR:{sname}^{oname}.{part}", hits)
                # also sha256-expanded keystream
                ks2=b""
                i=0
                while len(ks2)<len(ob):
                    ks2+=hashlib.sha256(sb+bytes([i])).digest(); i+=1
                x2=bytes(a^b for a,b in zip(ob,ks2[:len(ob)]))
                scan_bytes(x2, f"XORsha:{sname}^{oname}.{part}", hits)
    # ---- 2. last-words -> AES key, decrypt cts ----
    keys={}
    for sname,s in STR.items():
        sb=s.encode()
        keys[f"sha({sname})"]=hashlib.sha256(sb).digest()
        for w in (sb[:32],sb[-32:],sb[16:48] if len(sb)>=48 else None):
            if w and len(w)==32: keys[f"{sname}[win]"]=w
    for kn,K in keys.items():
        for oname,o in OBJS.items():
            for ivn,iv in (("zero",bytes(16)),("saltdup",(o["salt"] or bytes(8))*2),("ctpre",o["ct"][:16])):
                try: pt=AES.new(K,AES.MODE_CBC,iv).decrypt(o["ct"])
                except Exception: continue
                res=check_pt(pt)
                if res and res["hit"]: hits.append((f"KEY {kn} {oname} iv={ivn}","HARNESS:"+res["body"][:50].decode('latin1','replace')))
                scan_bytes(pt, f"DEC:{kn}:{oname}:{ivn}", hits)
            if oname in ("P32T",):
                fr=p32t_accept(K)
                if fr and not fr.startswith("weak"): hits.append((f"KEY {kn}","FREEZE:"+fr))
    # ---- 3. password form (raw + sha256hex), EVP, for the record ----
    for sname,s in STR.items():
        for pw in (s, hashlib.sha256(s.encode()).hexdigest()):
            for md in ("md5","sha256"):
                for oname,o in OBJS.items():
                    K,IV=evp_bytes_to_key(pw.encode(),o["salt"] or bytes(8),md,32)
                    pt=AES.new(K,AES.MODE_CBC,IV).decrypt(o["ct"]) if o.get("salt") else None
                    if pt:
                        res=check_pt(pt)
                        if res and res["hit"]: hits.append((f"PW {sname} {md} {oname}","HARNESS:"+res["body"][:50].decode('latin1','replace')))
    # ---- 4. mod-26 subtract the two 48-halves ----
    def only_az(x): return "".join(c for c in x if c.isalpha())
    sub=" ".join([ "".join(chr(65+((ord(a)-97)-(ord(b)-97))%26) for a,b in zip(L48a,L48b)) ])
    print("L48a - L48b (mod26):", sub)
    print("L48b - L48a (mod26):", "".join(chr(65+((ord(b)-97)-(ord(a)-97))%26) for a,b in zip(L48a,L48b)))
    print("total operations scanned; HITS:", len(hits))
    for h in hits[:40]: print("  ",h)

if __name__=="__main__":
    main()
