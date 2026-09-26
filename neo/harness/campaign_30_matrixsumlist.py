#!/usr/bin/env python3
"""Campaign 30: the matrixsumlist -> lastwordsbeforearchichoice pipeline (user, 2026-09-26).

Revelation under test: f73d92 = 2*11*149*4943 encodes the structure --
  11 -> side of an 11x11 matrix ; 121 = 11^2 = pi(661) prime positions of DBBI||FAED
  (661 = 91+570) ; 149 = VIC numeric ciphertext length ; 4943 = prime(661).
Pipeline: 121 prime-position chars of DBBI||FAED -> a=1..i=9 -> 11x11 -> row/col sums
(matrixsumlist) -> use the sums as indices into a held text (lastwordsbeforearchichoice)
-> the extracted letters are the password. Terminal gate: freeze oracle + address.

Bounded, pre-registered. All conventions enumerated; the acceptance is the 128-bit freeze
oracle (D_K(C5)^C4 == primary/secondary pad) and the prize-address derivation -- not English.
"""
import os, sys, re, hashlib, itertools, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import evp_bytes_to_key, load_targets, check_pt, decrypt
from p32t_freeze import accept as p32t_accept
from addr_check import check as addr_check

MAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "materials")
page = "".join(open(os.path.join(MAT, "salphaseion_page.txt")).read().split())
ab = [(m.start(), m.end()) for m in re.finditer(r'[ab]{30,}', page)]
DBBI = page[:ab[0][0]]; rest = page[ab[0][1]:]; FAED = rest[:rest.index('z')]
CHAIN = DBBI + FAED
assert len(CHAIN) == 661, len(CHAIN)

def sieve(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=[False]*len(s[i*i::i])
    return [i for i,b in enumerate(s) if b]
PRIMES_661 = sieve(661)                       # 121 primes <= 661
assert len(PRIMES_661) == 121

def val(c): return ord(c) - 96                # a=1..i=9 (no 'o' in DBBI/FAED)

# 121 prime-position chars (1-based), as digits
digits = [val(CHAIN[p-1]) for p in PRIMES_661]

def matrix(fill):
    if fill == "row":
        return [digits[r*11:(r+1)*11] for r in range(11)]
    else:  # col-major
        return [[digits[c*11+r] for c in range(11)] for r in range(11)]

def sums(fill, kind):
    M = matrix(fill)
    rs = [sum(M[r]) for r in range(11)]
    cs = [sum(M[r][c] for r in range(11)) for c in range(11)]
    return {"row": rs, "col": cs, "rowcol": rs+cs, "colrow": cs+rs}[kind]

# held texts for lastwordsbeforearchichoice
ARCH = open('/tmp/arch.txt').read()
ARCH = ARCH[:ARCH.index('ciaobellao')+len('ciaobellao')]  # trim notebook cruft
VICPT = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
URL = "gsmgiotheseedisplanted"
b32 = open(os.path.join(MAT,"primary","phase32_plaintext_2422B_ends_with_p32_trailing_envelope.bin"),'rb').read().decode('latin1')
VICCT = re.search(r'[0-9]{120,}', b32).group(0)
TEXTS = {"arch": ARCH, "vicpt": VICPT.lower(), "url": URL, "chain": CHAIN, "vicct": VICCT}

COMMON = set("the key private this that answer password you your are now here door half better one two seed find take enter true give away last words yin yang matrix prime blue yellow secret bitcoin cosmic soul source code choice free will hope".split())
def eng_score(s):
    return sum(len(w) for w in COMMON if w in s)

def extract(idxs, text, base, oob):
    out=[]
    L=len(text)
    for n in idxs:
        i = n-1 if base==1 else n
        if oob=="mod": i%=L
        if 0<=i<L: out.append(text[i])
    return "".join(out)

def main():
    cands={}
    for fill in ("row","col"):
        for kind in ("row","col","rowcol","colrow"):
            idxs=sums(fill,kind)
            for tname,text in TEXTS.items():
                for base in (1,0):
                    for oob in ("reject","mod"):
                        s=extract(idxs,text,base,oob)
                        if len(s)>=6:
                            cands[f"{fill}:{kind}:{tname}:b{base}:{oob}"]=s
    # also the raw sum-lists themselves as candidate passwords (concat and spaced)
    for fill in ("row","col"):
        for kind in ("row","col","rowcol","colrow"):
            idxs=sums(fill,kind)
            cands[f"{fill}:{kind}:concat"]="".join(map(str,idxs))
            cands[f"{fill}:{kind}:spaced"]=" ".join(map(str,idxs))
    print(f"candidates: {len(cands)}")
    # eyeball: top English-scoring extracted strings
    ranked=sorted(((eng_score(v),k,v) for k,v in cands.items()), reverse=True)
    print("-- top 15 by crude English score --")
    for sc,k,v in ranked[:15]:
        print(f"  {sc:3} {k:28} {v[:60]}")

    # HARD GATE: every candidate as password -> freeze oracle (both salts) + full harness + address
    T=load_targets()
    SALTS={"P32T":T["inner96"], "salph":T["miniAB"]}
    hits=[]; addr_c=[]
    for k,s in cands.items():
        pwvariants=[("raw",s),("sha256hex",hashlib.sha256(s.encode()).hexdigest())]
        for pwtag,pw in pwvariants:
            for md in ("md5","sha256"):
                for sname,t in SALTS.items():
                    K,IV=evp_bytes_to_key(pw.encode(),t["salt"],md,32)
                    fr=p32t_accept(K) if sname=="P32T" else None
                    # full-decrypt harness accept (uses KDF IV)
                    pt=decrypt(t["ct"],K,IV); res=check_pt(pt)
                    if fr and not fr.startswith("weak"):
                        hits.append((k,pwtag,md,sname,"FREEZE:"+fr))
                    if res and res["hit"]:
                        hits.append((k,pwtag,md,sname,"HARNESS-HIT",res["body"][:60].decode("latin1","replace")))
        addr_c.append((k, hashlib.sha256(s.encode()).digest()))
    print("freeze/harness hits:", hits)
    # address oracle on sha256(candidate) (bounded)
    m=addr_check([(k,v) for k,v in [(kk, cands[kk].encode()) for kk in cands]])
    print("address matches:", m)

if __name__ == "__main__":
    main()
