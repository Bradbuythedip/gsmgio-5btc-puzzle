#!/usr/bin/env python3
"""Discriminating evidence for the S1-S4 construction: test seed->seed relations.
No BSGS, no prize-key search. Pure structure of the four known seeds."""
import hashlib
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
S={
 1:"223e3dea019fd03dc730467abfcc068bd329b222cfbe2fa71339ac57d25ef545",
 2:"376103f4bd0300b073ffc8fc70d132b3f1c3ccd90ace4e0fe4fbb183cb66bd51",
 3:"748a3ea15dc34e20c58e11e7407740904d9011debc9846b0b7a6dab54ad85123",
 4:"b49c87570a54e14d6af2790924059ff859f345eaf09641c64734c66c190bdc75",
}
b={i:bytes.fromhex(h) for i,h in S.items()}
n={i:int(h,16) for i,h in S.items()}

print("=== ordering ===")
print("S1<S2<S3<S4 :", n[1]<n[2]<n[3]<n[4])
print("all < N     :", all(v<N for v in n.values()))

print("\n=== hash-chain hypothesis: S_{i+1} == hash(S_i) ? ===")
def sha(x): return hashlib.sha256(x).hexdigest()
def shad(x): return hashlib.sha256(hashlib.sha256(x).digest()).hexdigest()
for i in (1,2,3):
    j=i+1
    tests={
      "sha256(raw_i)":sha(b[i]),
      "sha256(hexascii_i)":sha(S[i].encode()),
      "sha256(hexascii_i upper)":sha(S[i].upper().encode()),
      "sha256d(raw_i)":shad(b[i]),
      "sha256(raw_i reversed)":sha(b[i][::-1]),
    }
    for name,val in tests.items():
        if val==S[j]:
            print(f"  HIT S{j} == {name}")
    hits=[name for name,val in tests.items() if val==S[j]]
    if not hits: print(f"  S{j}: none of {list(tests)} == S{j}")

print("\n=== arithmetic-sequence hypothesis: constant difference ? ===")
d_plain=[n[i+1]-n[i] for i in (1,2,3)]
d_modN=[(n[i+1]-n[i])%N for i in (1,2,3)]
print("plain diffs equal:", d_plain[0]==d_plain[1]==d_plain[2], [hex(x) for x in d_plain])
print("modN  diffs equal:", d_modN[0]==d_modN[1]==d_modN[2])

print("\n=== XOR-constant hypothesis ===")
x=[bytes(p^q for p,q in zip(b[i+1],b[i])) for i in (1,2,3)]
print("xor diffs equal:", x[0]==x[1]==x[2])

print("\n=== ratio / multiplier hypothesis: S_{i+1} == m*S_i mod N ? ===")
def inv(a): return pow(a,N-2,N)
r=[ (n[i+1]*inv(n[i]))%N for i in (1,2,3)]
print("multipliers equal:", r[0]==r[1]==r[2], "| r1==r2:", r[0]==r[1])

print("\n=== byte-reversal / endian relation between consecutive seeds ===")
for i in (1,2,3):
    print(f"  S{i} reversed == S{i+1}? {b[i][::-1].hex()==S[i+1]}")

print("\n=== do any of the 'ten related seeds' equal an S-value? ===")
rel={}
try:
    ca=open('drive/cosmic_A.bin','rb').read()
    cc=open('drive/cosmic_1327b_decrypted.bin','rb').read()
    c4=open('drive/chain4_final.bin','rb').read()
    print("  cosmic_A len", len(ca), "cosmic_1327b len", len(cc), "chain4 len", len(c4))
    rel["cc[833:865]"]=cc[833:865]
    rel["ca[280:312]"]=ca[280:312]
    rel["ca[833:865]"]=ca[833:865]
    rel["cc[280:312]"]=cc[280:312]
    rel["sha256(ca)"]=hashlib.sha256(ca).digest()
    rel["sha256(cc)"]=hashlib.sha256(cc).digest()
    rel["sha256(c4)"]=hashlib.sha256(c4).digest()
    if len(cc)>=865:
        rel["cc[833:865] XOR ca[280:312]"]=bytes(p^q for p,q in zip(cc[833:865],ca[280:312]))
    Svals=set(S.values())
    for name,val in rel.items():
        if len(val)==32 and val.hex() in Svals:
            print(f"  *** {name} == an S-seed ({val.hex()})")
    print("  none of the derived objects match any S-seed:",
          not any(len(v)==32 and v.hex() in Svals for v in rel.values()))
    # also print the derived scalar for the record
    if "cc[833:865] XOR ca[280:312]" in rel:
        print("  derived scalar (cc^ca) =", rel["cc[833:865] XOR ca[280:312]"].hex())
except FileNotFoundError as e:
    print("  (bins missing:", e, ")")
