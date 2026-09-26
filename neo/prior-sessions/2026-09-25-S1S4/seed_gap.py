#!/usr/bin/env python3
"""Characterise the S2->S3 gap and test whether S1/S3 are sha256 of a known GSMG answer."""
import hashlib
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
S={1:"223e3dea019fd03dc730467abfcc068bd329b222cfbe2fa71339ac57d25ef545",
   2:"376103f4bd0300b073ffc8fc70d132b3f1c3ccd90ace4e0fe4fbb183cb66bd51",
   3:"748a3ea15dc34e20c58e11e7407740904d9011debc9846b0b7a6dab54ad85123",
   4:"b49c87570a54e14d6af2790924059ff859f345eaf09641c64734c66c190bdc75"}
b={i:bytes.fromhex(h) for i,h in S.items()}; n={i:int(h,16) for i,h in S.items()}
sha=lambda x: hashlib.sha256(x).digest()

print("=== confirm the two hits ===")
print("SHA256(S1)==S2 :", sha(b[1]).hex()==S[2])
print("SHA256(S3)==S4 :", sha(b[3]).hex()==S[4])

print("\n=== is the S2->S3 gap a small vanity offset? ===")
g=sha(b[2]); gi=int(g.hex(),16)
diff=(n[3]-gi)%N
print("SHA256(S2) =", g.hex())
print("S3         =", S[3])
print("S3 - SHA256(S2) mod N =", hex(diff))
print("  magnitude ~2^%.1f  (small-offset if <~2^40)" % (diff.bit_length()))
print("SHA256(S2) - S3 mod N =", hex((gi-n[3])%N), "~2^%.1f"%(((gi-n[3])%N).bit_length()))
# leading-byte agreement (vanity prefix grind would share a prefix)
lead=0
for x,y in zip(g.hex(),S[3]):
    if x==y: lead+=1
    else: break
print("shared leading hex nibbles SHA256(S2) vs S3:", lead)

print("\n=== S3 as sha256 of the OTHER seeds / combinations ===")
cands={"sha256(S1)":sha(b[1]),"sha256d(S2)":sha(sha(b[2])),"sha256(S2 hexascii)":sha(S[2].encode()),
 "sha256(S1||S2)":sha(b[1]+b[2]),"sha256(S2||S1)":sha(b[2]+b[1]),"sha256(S2 reversed)":sha(b[2][::-1])}
for k,v in cands.items():
    if v.hex()==S[3]: print("  HIT S3 ==",k)
print("  (blank above = none matched)")

print("\n=== recover S0: is S1 or S3 == sha256(a known GSMG answer)? ===")
# harvest candidate answer strings from the harness/creator material
import glob, re
vocab=set()
answers=["theflowerblossomsthroughwhatseemstobeaconcretesurface","causality",
 "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple","thematrixhasyou",
 "gsmg.io/theseedisplanted","theseedisplanted","matrixsumlist","lastwordsbeforearchichoice",
 "thispassword","yourlastcommand","secondanswer","enter","shabef","yinyang","half","betterhalf",
 "wewontgiveawaythepassword","itsinfrontofyoureyes","verylaststep","GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"]
vocab.update(answers)
for f in glob.glob("work/*.txt")+glob.glob("work/*.md"):
    try:
        t=open(f,encoding="utf-8",errors="replace").read()
        vocab.update(re.findall(r"[a-zA-Z0-9]{3,60}", t))
    except: pass
print("vocab size:", len(vocab))
targets={S[1]:"S1",S[3]:"S3",S[2]:"S2",S[4]:"S4"}
def forms(s):
    return {s, s.lower(), s.upper(), s.strip()}
hit=False
for w in vocab:
    for f in forms(w):
        e=f.encode()
        for name,val in (("sha256",sha(e)),("sha256d",sha(sha(e))),("sha256(hex? n/a)",sha(e))):
            if val.hex() in targets:
                print(f"  *** {targets[val.hex()]} == {name}({f!r})"); hit=True
if not hit: print("  no S-seed equals sha256/sha256d of any harvested string")
