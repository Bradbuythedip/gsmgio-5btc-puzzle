#!/usr/bin/env python3
"""Campaign 41: are any OpenSSL salts truncated fingerprints of a visible puzzle object?
Fixed object set x fixed hash set; look for each 8-byte salt anywhere in each digest
(and 4-byte salt halves, reported as weak). Includes the solved stages as controls:
if solved salts are not fingerprints of their own known passwords, the salts are random."""
import hashlib, base64, glob, os, re, sys
sys.path.insert(0, os.path.dirname(__file__)); import aes_try
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(R, *a)

salts = {k: t["salt"] for k, t in aes_try.load_targets().items() if t.get("salt")}
salts = {"salph(miniA/AB)": salts["miniA"], "P32T": salts["inner96"], "cosmic": salts["cosmic"]}
for f in ["phase2-assets/phase2_aes.txt", "phase2-assets/phase3_aes.txt", "phase3-assets/phase3.2-aes.txt"]:
    b = base64.b64decode(re.sub(rb"\s", b"", open(P(f), "rb").read()))
    salts["SOLVED " + os.path.basename(f)] = b[8:16]

soup = open(P("neo/materials/primary/salphaseion_soup_space_separated.txt")).read().split()
VIC = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
src = open(P("neo/harness/aes_try.py")).read()
pw = dict(re.findall(r'\("(phase[^"]+)",\s*"([^"]+)"\)', src.replace("\n        ", "").replace("(\n         ", "(")))
objs = {
 "seed_url": b"gsmg.io/theseedisplanted", "seed_full": b"https://gsmg.io/theseedisplanted",
 "pw_causality": b"causality",
 "pw_227": re.search(r'"(causalitySafenet[^"]+)"', src).group(1).encode(),
 "pw_p32": b"jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
 "VIC": VIC.encode(), "VIC_lower": VIC.lower().encode(),
 "DBBI": "".join(soup[:91]).encode(), "soup_all": "".join(soup).encode(),
 "HALF": b"HALF", "BETTERHALF": b"BETTERHALF", "halfandbetterhalf": b"halfandbetterhalf",
 "YOUWON": b"YOUWON", "yinyang": b"yinyang", "yellowblueprimes": b"yellowblueprimes",
 "matrixsumlist": b"matrixsumlist", "lastwordsbeforearchichoice": b"lastwordsbeforearchichoice",
 "prize_addr": b"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "better_addr": b"17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
 "prize_pub_unc": bytes.fromhex("04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559"),
}
for f in glob.glob(P("neo/materials/primary/*")) + glob.glob(P("phase*-assets/*")):
    if os.path.isfile(f): objs["file:" + os.path.relpath(f, R)] = open(f, "rb").read()
for k in list(objs):  # sha256hex form of each text object, as the pinned convention uses
    if not k.startswith("file:"): objs[k + "|sha256hex"] = hashlib.sha256(objs[k]).hexdigest().encode()

H = {"sha256": lambda b: hashlib.sha256(b).digest(),
     "sha256d": lambda b: hashlib.sha256(hashlib.sha256(b).digest()).digest(),
     "md5": lambda b: hashlib.md5(b).digest(), "sha1": lambda b: hashlib.sha1(b).digest(),
     "sha512": lambda b: hashlib.sha512(b).digest(),
     "hash160": lambda b: hashlib.new("ripemd160", hashlib.sha256(b).digest()).digest(),
     "identity": lambda b: b}
full = weak = windows8 = windows4 = 0
for on, ob in objs.items():
    for hn, h in H.items():
        d = h(ob)
        if hn == "identity" and on.startswith("file:"):
            # a salt may legitimately sit inside its own envelope file; skip the Salted__ header
            d = d[16:] if d[:8] == b"Salted__" else d
        windows8 += max(0, len(d) - 7) * len(salts); windows4 += max(0, len(d) - 3) * 2 * len(salts)
        for sn, s in salts.items():
            if s in d: full += 1; print(f"FULL 64-bit  {sn} in {hn}({on}) at {d.find(s)}")
            for half in (s[:4], s[4:]):
                if half in d: weak += 1; print(f"weak 32-bit {sn} half {half.hex()} in {hn}({on})")
print(f"\nobjects={len(objs)} salts={len(salts)} (3 unsolved + 3 solved controls)")
print(f"64-bit hits={full}  expected by chance={windows8 / 2**64:.2e}")
print(f"32-bit half hits={weak}  expected by chance={windows4 / 2**32:.2f}")
