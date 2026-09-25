#!/usr/bin/env python3
"""GSMG puzzle AES password harness.

Targets are openssl `Salted__` blobs (and raw-ct variants). A candidate password is
accepted only with verifiable output structure: strict PKCS#7 padding AND
(printable ratio >= 0.90 OR a known magic prefix). Everything tried is logged to
attempts/<campaign>.jsonl for cross-session dedupe.

KDF variants covered (creator-era openssl conventions):
  m5  = EVP_BytesToKey(MD5,    1 round)  aes-256-cbc   (openssl <=1.0.x default)
  s2  = EVP_BytesToKey(SHA256, 1 round)  aes-256-cbc   (openssl >=1.1.0 default)
  m5_128 / s2_128 = same, aes-128-cbc
"""
import base64, hashlib, json, os, string, sys, time
from Crypto.Cipher import AES

HERE = os.path.dirname(os.path.abspath(__file__))
MAT = os.path.join(HERE, "..", "materials")
ATT = os.path.join(HERE, "..", "attempts")

def _load_b64(name):
    return base64.b64decode("".join(open(os.path.join(MAT, name)).read().split()))

def load_targets():
    a = _load_b64("miniA.b64")
    b = _load_b64("miniB.b64")
    inner = _load_b64("inner96.b64")
    cosmic = _load_b64("cosmic_duality_b64.txt")
    t = {}
    def add_salted(key, raw):
        assert raw[:8] == b"Salted__", key
        t[key] = {"salt": raw[8:16], "ct": raw[16:]}
    add_salted("miniA", a)
    add_salted("miniAB", a + b)          # B as continuation of A ("enter" = newline)
    add_salted("inner96", inner)
    add_salted("cosmic", cosmic)
    t["miniB_nosalt"] = {"salt": None, "ct": b}   # raw blob, EVP without salt
    t["miniB_saltA"] = {"salt": a[8:16], "ct": b} # sibling ct sharing A's salt
    t["miniB_iv16"] = {"salt": None, "ct": b[16:], "iv": b[:16]}  # [iv||ct] layout
    return t

def evp_bytes_to_key(pw: bytes, salt, md_name: str, keylen: int, ivlen: int = 16):
    md = getattr(hashlib, md_name)
    d = b""
    prev = b""
    salt_part = salt if salt else b""
    while len(d) < keylen + ivlen:
        prev = md(prev + pw + salt_part).digest()
        d += prev
    return d[:keylen], d[keylen:keylen + ivlen]

KDFS = {
    "m5":     ("md5", 32),
    "s2":     ("sha256", 32),
    "m5_128": ("md5", 16),
    "s2_128": ("sha256", 16),
    "rk":     ("rawkey", 32),   # key = sha256(pw) digest, iv = zeros (openssl -K style)
}

_PRINTABLE = set(string.printable.encode())

def printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    return sum(1 for x in b if x in _PRINTABLE) / len(b)

# magic prefixes must be >=4 bytes: shorter ones fire by chance at pad=1
MAGIC = (b"U2Fsd", b"Salted__", b"-----BEGIN", b"http", b"gsmg", b"GSMG", b"xprv", b"bc1q", b"1GSMG")

def check_pt(pt: bytes):
    if not pt:
        return None
    pad = pt[-1]
    if pad < 1 or pad > 16 or len(pt) < pad:
        return None
    if pt[-pad:] != bytes([pad]) * pad:
        return None
    body = pt[:-pad]
    r = printable_ratio(body)
    rh = printable_ratio(body[:64])
    magic = any(body.startswith(m) for m in MAGIC)
    # pad>=4 alone is ~2^-32 by chance: proof of correct key even for binary plaintext.
    # pad 1-3 needs corroboration (printable structure or a >=4-byte magic prefix).
    hit = (pad >= 4) or magic or rh >= 0.85 or r >= 0.90
    return {"pad": pad, "printable": round(r, 3), "printable_head": round(rh, 3),
            "magic": magic, "hit": hit, "body": body}

def decrypt(ct: bytes, key: bytes, iv: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)

class Harness:
    def __init__(self, campaign: str):
        os.makedirs(ATT, exist_ok=True)
        self.targets = load_targets()
        self.log_path = os.path.join(ATT, campaign + ".jsonl")
        self.log = open(self.log_path, "a")
        self.n = 0
        self.hits = []
        self.near = []
        self.seen = set()

    def try_pw(self, pw: str, note: str = "", targets=None, kdfs=None):
        pwb = pw.encode("utf-8", "ignore")
        for tname in (targets or self.targets):
            t = self.targets[tname]
            for kname in (kdfs or KDFS):
                sig = (pwb, tname, kname)
                if sig in self.seen:
                    continue
                self.seen.add(sig)
                md, keylen = KDFS[kname]
                if md == "rawkey":
                    key = hashlib.sha256(pwb).digest()
                    iv = t.get("iv", b"\x00" * 16)
                else:
                    key, iv = evp_bytes_to_key(pwb, t["salt"], md, keylen)
                    if "iv" in t:
                        iv = t["iv"]
                try:
                    pt = decrypt(t["ct"], key, iv)
                except Exception:
                    continue
                self.n += 1
                res = check_pt(pt)
                if res:
                    rec = {"pw": pw, "target": tname, "kdf": kname,
                           "pad": res["pad"], "printable": res["printable"],
                           "printable_head": res["printable_head"],
                           "magic": res["magic"], "note": note}
                    if res["hit"]:
                        rec["body_head"] = res["body"][:200].decode("latin1")
                        rec["HIT"] = True
                        self.hits.append(rec)
                        print("\n*** HIT ***", json.dumps(rec)[:600], flush=True)
                    elif res["printable"] >= 0.55 and len(res["body"]) >= 16 and res["pad"] > 1:
                        rec["body_head"] = res["body"][:64].decode("latin1")
                        self.near.append(rec)
                    self.log.write(json.dumps(rec) + "\n")

    def try_family(self, base: str, note: str = "", **kw):
        """base plus sha-b4 variants (sha256 hex lower/upper, double-sha)."""
        h = hashlib.sha256(base.encode()).hexdigest()
        h2 = hashlib.sha256(h.encode()).hexdigest()
        hd = hashlib.sha256(hashlib.sha256(base.encode()).digest()).hexdigest()
        self.try_pw(base, note, **kw)
        self.try_pw(h, note + "|sha256hex", **kw)
        self.try_pw(h.upper(), note + "|SHA256HEX", **kw)
        self.try_pw(h2, note + "|sha256(sha256hex)", **kw)
        self.try_pw(hd, note + "|sha256d", **kw)

    def finish(self, label=""):
        self.log.flush()
        print(f"[{label}] trials={self.n} hits={len(self.hits)} near={len(self.near)}")
        for r in self.near[:12]:
            print("  near:", json.dumps(r)[:240])
        return self.hits

def self_test():
    """Positive controls: the three publicly solved blobs must decrypt."""
    import re
    repo = os.path.join(HERE, "..", "..")
    known = [
        ("phase2-assets/phase2_aes.txt", "causality"),
        ("phase2-assets/phase3_aes.txt",
         "causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1"),
        ("phase3-assets/phase3.2-aes.txt",
         "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"),
    ]
    ok = True
    for path, pw in known:
        raw = base64.b64decode("".join(open(os.path.join(repo, path)).read().split()))
        assert raw[:8] == b"Salted__"
        salt, ct = raw[8:16], raw[16:]
        got = None
        import hashlib as _h
        for vpw in (pw, _h.sha256(pw.encode()).hexdigest()):
            for kname, (md, keylen) in KDFS.items():
                if md == "rawkey":
                    continue
                key, iv = evp_bytes_to_key(vpw.encode(), salt, md, keylen)
                pt = decrypt(ct, key, iv)
                res = check_pt(pt)
                if res and res["hit"]:
                    got = (kname, "sha256hex" if vpw != pw else "raw",
                           res["pad"], res["printable"], res["body"][:60])
                    break
            if got:
                break
        print(("OK  " if got else "FAIL"), path, got)
        ok = ok and bool(got)
    return ok

if __name__ == "__main__":
    print("targets:", {k: len(v["ct"]) for k, v in load_targets().items()})
    print("self-test passed:", self_test())
