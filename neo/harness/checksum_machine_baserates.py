#!/usr/bin/env python3
"""Base rates for the checksum-machine claims (tick 36 addendum). Loads verify_checksum_machine.py; no AES, no gate."""
import collections, io, contextlib, os
P=os.path.abspath("verify_checksum_machine.py")
g={"__file__":P,"__name__":"vcm"}
with contextlib.redirect_stdout(io.StringIO()):
    try: exec(open(P).read(), g)
    except SystemExit: pass
globals().update(g)
named=["matrixsumlist","thepassword","YOUWON","HALF","promised","enter","shabefourfirsthintisyourlastcommand",
 "verylaststepisatruegiveaway","lastwordsbeforearchichoice","yellowblueprimes","thispassword","yinyang","causality",
 "BETTERHALF","PRIVATEKEYS","theseedisplanted","agda","cfob","dbbi","faed","salphaseion","cosmicduality","KEY","hashthetext"]
L=set(len(x) for x in named)
for hi in (50,150):
    c=[n for n in range(2,hi+1) if pi(n) in L]; print(f"n in 2..{hi}: pi(n) hits a named length for {len(c)}/{hi-1} = {len(c)/(hi-1):.0%}")
yb=[ybsum(FAED[o:o+24],A0) for o in range(547)]
pairs=collections.Counter(yb)
print(f"colour windows: {len(pairs)} distinct (Y,B) pairs over 547; windows whose pair is unique: {sum(1 for p in yb if pairs[p]==1)}")
yp=[p for p in yb if is_p(p[0]) and is_p(p[1])]
print(f"colour windows with both sums prime: {len(yp)}/547; of those with gap 42: {sum(1 for p in yp if p[1]-p[0]==42)}")
pat=collections.Counter(tuple(k+1 for k,v in enumerate(layers(o)) if is_p(v)) for o in range(25))
print("tape: prime-position patterns over 25 alignments:", dict(pat))
both=[o for o in range(52) if all(map(is_p,masked(o)))]
print("ENTER: windows with both sums prime:", both, "gaps", [masked(o)[1]-masked(o)[0] for o in both])
wb=set(); pos=0
for w in "IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE".split()[:-1]:
    pos+=len(w); wb.add(pos)
tokend={e:k+1 for k,e in enumerate(ends)}
hitw=[c for c in range(1,149) if c in tokend and tokend[c] in wb]
print(f"digit cuts 1..148: {sum(1 for c in range(1,149) if c in tokend)} on a token boundary, {len(hitw)} also on a word boundary -> {len(hitw)/148:.0%}")
print("gap-42 prime-pair colour windows:", [(o,ybsum(FAED[o:o+24],A0)) for o in range(547) if all(map(is_p,ybsum(FAED[o:o+24],A0))) and ybsum(FAED[o:o+24],A0)[1]-ybsum(FAED[o:o+24],A0)[0]==42])
import random
random.seed(1)
# how often does a random 40-letter English-like window from the sentence pool give a prime pair with gap exactly 42? use all 52 windows x random 40-bit masks
hit=tot=0
for _ in range(20000):
    m="".join(random.choice("01") for _ in range(40)); o=random.randrange(52)
    v=[ord(c)-65 for c in SENT[o:o+40]]
    a=sum(x for x,b in zip(v,m) if b=="1"); b=sum(x for x,bb in zip(v,m) if bb=="0")
    tot+=1; hit+= is_p(a) and is_p(b) and abs(a-b)==42
print(f"random 40-bit mask x random 40-letter window: prime pair with gap 42 in {hit}/{tot} = 1 in {tot/max(hit,1):.0f}")
