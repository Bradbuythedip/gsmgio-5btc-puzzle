#!/usr/bin/env python3
"""Conservative offline GSMG endgame harness.

Commands:
  audit      Verify the three byte-pinned ciphertext objects.
  selftest   Audit + solved-stage AES controls + secp256k1 control.
  test       Test exactly ONE supplied candidate against the standing locks.
  opreturn   Compare one 32-byte payload against supplied nonce-point x/y values.

Dependency:
  python -m pip install pycryptodome
"""
from __future__ import annotations

import argparse, base64, hashlib, json, math, re, string, sys, time
from dataclasses import dataclass
from pathlib import Path

try:
    from Crypto.Cipher import AES
except Exception:
    AES = None

def require_aes():
    if AES is None:
        raise RuntimeError("pycryptodome is required for decrypt/selftest: python -m pip install pycryptodome")

PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BETTER_HALF = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
FORMS = ("raw", "sha256hex")
KDFS = ("md5", "sha256")
MAGIC = (b"U2Fsd", b"Salted__", b"-----BEGIN", b"http", b"gsmg", b"GSMG", b"xprv", b"bc1q", b"1GSMG")
PRINTABLE = set(string.printable.encode())

BASELINES = {
    "salph80": {
        "envelope_len": 96, "ct_len": 80,
        "salt": "3ab585348552415d",
        "sha256": "9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258",
        "last_block": "ef756397ea74234a97a95f01ae37f8c9",
    },
    "p32t": {
        "envelope_len": 96, "ct_len": 80,
        "salt": "b45a5e3d827593ca",
        "sha256": "291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9",
        "last_block": "5334de08884878aaed7c99d0b4340bf8",
    },
    "cosmic": {
        "envelope_len": 1344, "ct_len": 1328,
        "salt": "2d3f6fe06dc950e6",
        "sha256": "b18950551a4dd0cb8a9378f0906ba18c03a15f0ee83eb98c6bc90165c5f79805",
        "last_block": "5bbf983669ed922eb12dff1dcc3f6fc6",
    },
}

# secp256k1, used only as an exact scalar->address oracle.
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
P32T_PRIMARY_P5 = bytes([0x0A]) + bytes([0x0F]) * 15
P32T_SECONDARY_P5 = bytes([0x10]) * 16

@dataclass
class Target:
    name: str
    envelope: bytes
    salt: bytes
    ct: bytes

def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def sha256hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_b64(path: Path) -> bytes:
    s = "".join(path.read_text(encoding="utf-8").split())
    return base64.b64decode(s, validate=True)

def printable_ratio(b: bytes) -> float:
    return 0.0 if not b else sum(x in PRINTABLE for x in b) / len(b)

def entropy(b: bytes) -> float:
    if not b: return 0.0
    counts = {}
    for x in b: counts[x] = counts.get(x, 0) + 1
    n = len(b)
    return -sum((c/n)*math.log2(c/n) for c in counts.values())

def pkcs7_info(pt: bytes):
    if not pt: return None
    p = pt[-1]
    if not (1 <= p <= 16) or len(pt) < p or pt[-p:] != bytes([p])*p:
        return None
    body = pt[:-p]
    r = printable_ratio(body)
    rh = printable_ratio(body[:64])
    magic = any(body.startswith(m) for m in MAGIC)
    return {
        "pad": p, "body": body, "printable": r, "printable_head": rh,
        "magic": magic,
        "strict_hit": (p >= 4) or magic or rh >= 0.85 or r >= 0.90,
    }

def evp_bytes_to_key(password: bytes, salt: bytes, digest_name: str, key_len=32, iv_len=16):
    md = getattr(hashlib, digest_name)
    out, prev = b"", b""
    while len(out) < key_len + iv_len:
        prev = md(prev + password + salt).digest()
        out += prev
    return out[:key_len], out[key_len:key_len+iv_len]

def locate_repo(p: str) -> Path:
    root = Path(p).expanduser().resolve()
    for r in (root, root.parent):
        if (r/"neo"/"materials").is_dir() and (r/"phase3-assets").is_dir():
            return r
    raise FileNotFoundError("expected repo root containing neo/materials and phase3-assets")

def load_targets(repo: Path):
    mat = repo/"neo"/"materials"
    salph = read_b64(mat/"miniA.b64") + read_b64(mat/"miniB.b64")
    p32t = read_b64(mat/"inner96.b64")
    cosmic = read_b64(mat/"cosmic_duality_b64.txt")
    out = {}
    for name, raw in (("salph80", salph), ("p32t", p32t), ("cosmic", cosmic)):
        if not raw.startswith(b"Salted__"):
            raise ValueError(f"{name}: missing Salted__")
        out[name] = Target(name, raw, raw[8:16], raw[16:])
    return out

# ---- secp256k1/P2PKH ----
def inv(a, m=P): return pow(a, m-2, m)
def padd(p, q):
    if p is None: return q
    if q is None: return p
    x1,y1 = p; x2,y2 = q
    if x1 == x2:
        if (y1+y2) % P == 0: return None
        lam = (3*x1*x1) * inv(2*y1) % P
    else:
        lam = (y2-y1) * inv(x2-x1) % P
    x3 = (lam*lam-x1-x2) % P
    return x3, (lam*(x1-x3)-y1) % P

def pmul(k, p=(GX,GY)):
    r = None
    while k:
        if k & 1: r = padd(r,p)
        p = padd(p,p); k >>= 1
    return r

def b58encode(b):
    n = int.from_bytes(b,"big"); s = ""
    while n:
        n,r = divmod(n,58); s = B58[r] + s
    return "1"*(len(b)-len(b.lstrip(b"\0"))) + s

def hash160(b): return hashlib.new("ripemd160", hashlib.sha256(b).digest()).digest()
def p2pkh(pub):
    x = b"\x00" + hash160(pub)
    return b58encode(x + sha256(sha256(x))[:4])

def scalar_addresses(k):
    if not (1 <= k < N): return None,None
    x,y = pmul(k); xb = x.to_bytes(32,"big")
    return p2pkh(bytes([2+(y&1)])+xb), p2pkh(b"\x04"+xb+y.to_bytes(32,"big"))

def scalar_oracle(raw32: bytes):
    if len(raw32) != 32: return None
    c,u = scalar_addresses(int.from_bytes(raw32,"big"))
    if c is None: return None
    hits = []
    for addr in (PRIZE, BETTER_HALF):
        if c == addr or u == addr:
            hits.append({"address":addr,"encoding":"compressed" if c==addr else "uncompressed"})
    return {"compressed":c,"uncompressed":u,"hits":hits}

# ---- audit ----
def audit(repo: Path, quiet=False):
    targets = load_targets(repo); ok = True
    for name in ("salph80","p32t","cosmic"):
        t=targets[name]; b=BASELINES[name]
        got={
            "envelope_len":len(t.envelope), "ct_len":len(t.ct), "salt":t.salt.hex(),
            "sha256":sha256hex(t.envelope), "last_block":t.ct[-16:].hex(),
        }
        good=all(got[k]==b[k] for k in b); ok &= good
        if not quiet:
            print(f"[{'OK' if good else 'FAIL'}] {name}")
            for k in ("envelope_len","ct_len","salt","sha256","last_block"):
                print(f"  {k:12s} {got[k]} {'==' if got[k]==b[k] else '!='} {b[k]}")
    b64=base64.b64encode(targets["salph80"].envelope).decode()
    js=(b64[18]=="J" and b64[51]=="s"); ok &= js
    if not quiet: print(f"[{'OK' if js else 'FAIL'}] issue108 positions: 18={b64[18]!r}, 51={b64[51]!r}")
    return ok

SOLVED = [
    ("phase2-assets/phase2_aes.txt", "causality"),
    ("phase2-assets/phase3_aes.txt", "causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1"),
    ("phase3-assets/phase3.2-aes.txt", "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"),
]

def selftest(repo: Path):
    require_aes()
    if not audit(repo): return False
    ok=True
    for rel,human in SOLVED:
        raw=read_b64(repo/rel); salt,ct=raw[8:16],raw[16:]
        match=None
        for form,pw in (("raw",human.encode()),("sha256hex",hashlib.sha256(human.encode()).hexdigest().encode())):
            for d in KDFS:
                key,iv=evp_bytes_to_key(pw,salt,d)
                info=pkcs7_info(AES.new(key,AES.MODE_CBC,iv).decrypt(ct))
                if info and info["strict_hit"]: match=(form,d,info["pad"]); break
            if match: break
        print(f"[{'OK' if match else 'FAIL'}] {rel}: {match}"); ok &= bool(match)
    c,u=scalar_addresses(1)
    ec=(c=="1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH" and u=="1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm")
    print(f"[{'OK' if ec else 'FAIL'}] secp256k1 control"); ok &= ec
    print("self-test passed:",ok); return ok

# ---- candidate test ----
def p32t_freeze(key, ct):
    require_aes()
    c4,c5=ct[48:64],ct[64:80]
    p5=bytes(a^b for a,b in zip(AES.new(key,AES.MODE_ECB).decrypt(c5),c4))
    if p5==P32T_PRIMARY_P5: return "primary:64hex+LF"
    if p5==P32T_SECONDARY_P5: return "secondary:two-raw-keys"
    p=p5[-1]
    if 1<=p<=16 and p5[-p:]==bytes([p])*p: return f"weak:pad-{p}"
    return None

def structural_hits(pt):
    hits=[]
    for where,chunk in (("pt[0:32]",pt[:32]),("pt[32:64]",pt[32:64])):
        if len(chunk)==32:
            o=scalar_oracle(chunk)
            if o and o["hits"]: hits.append({"kind":"raw32","where":where,**o})
    for m in re.finditer(rb"(?<![0-9A-Fa-f])([0-9A-Fa-f]{64})(?![0-9A-Fa-f])",pt):
        o=scalar_oracle(bytes.fromhex(m.group(1).decode()))
        if o and o["hits"]: hits.append({"kind":"hex64","where":m.start(1),"hex":m.group(1).decode(),**o})
    return hits

def seen_hashes(path):
    out=set()
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            try:
                h=json.loads(line).get("candidate_sha256")
                if h: out.add(h)
            except Exception: pass
    return out

def run_candidate(repo,candidate,source_note,log_path,force=False,log_plaintext=False):
    require_aes()
    if not audit(repo,quiet=True):
        print("ABORT: baseline audit failed",file=sys.stderr); return 3
    ch=hashlib.sha256(candidate.encode()).hexdigest()
    if ch in seen_hashes(log_path) and not force:
        print("REFUSED: candidate already in local log; use --force to reproduce"); return 2
    targets=load_targets(repo); rows=[]; strong=False
    print("candidate_sha256:",ch); print("source_note:",source_note or "(none)")
    print("12 decryptions: 3 targets x 2 forms x 2 EVP digests\n")
    forms=(("raw",candidate.encode()),("sha256hex",hashlib.sha256(candidate.encode()).hexdigest().encode()))
    for form,pw in forms:
        for d in KDFS:
            for name in ("salph80","p32t","cosmic"):
                t=targets[name]; key,iv=evp_bytes_to_key(pw,t.salt,d)
                pt=AES.new(key,AES.MODE_CBC,iv).decrypt(t.ct); info=pkcs7_info(pt)
                sh=structural_hits(pt); fr=p32t_freeze(key,t.ct) if name=="p32t" else None
                ishit=bool(info and info["strict_hit"]) or bool(sh) or fr in ("primary:64hex+LF","secondary:two-raw-keys")
                strong |= ishit
                rec={"target":name,"form":form,"kdf":d,"pad":info["pad"] if info else None,
                     "strict_hit":bool(info and info["strict_hit"]),"print64":round(printable_ratio(pt[:64]),4),
                     "entropy":round(entropy(pt),4),"freeze":fr,"address_hits":sh,"HIT":ishit}
                if info: rec.update(unpadded_len=len(info["body"]),unpadded_sha256=sha256hex(info["body"]))
                rows.append(rec)
                print(f"{'*** HIT ***' if ishit else '          '} {name:7s} {form:9s} EVP-{d:6s} pad={str(rec['pad']):>4s} print64={rec['print64']:.3f} H={rec['entropy']:.3f} freeze={fr or '-'} addr_hits={len(sh)}")
    scalar_rows=[]
    checks=[("sha256(candidate)",hashlib.sha256(candidate.encode()).digest())]
    if re.fullmatch(r"[0-9A-Fa-f]{64}",candidate): checks.append(("candidate-as-hex",bytes.fromhex(candidate)))
    for label,b in checks:
        o=scalar_oracle(b); scalar_rows.append({"label":label,**o})
        if o["hits"]: strong=True; print("*** HIT *** scalar",label,o["hits"])
    obj={"ts_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"candidate_sha256":ch,
         "source_note":source_note,"tests":rows,"scalar_checks":scalar_rows,"HIT":strong}
    if log_plaintext: obj["candidate"]=candidate
    log_path.parent.mkdir(parents=True,exist_ok=True)
    with log_path.open("a",encoding="utf-8") as f: f.write(json.dumps(obj,sort_keys=True)+"\n")
    print("\nRESULT:","*** STRONG HIT ***" if strong else "null"); print("logged:",log_path)
    return 10 if strong else 0

# ---- OP_RETURN exact comparator ----
def hex32(s,label):
    s=s.strip().lower(); s=s[2:] if s.startswith("0x") else s
    if not re.fullmatch(r"[0-9a-f]{64}",s): raise ValueError(f"{label}: need 64 hex chars")
    return bytes.fromhex(s)

def compare_opreturn(payload_hex,nonce_json):
    p=hex32(payload_hex,"payload"); data=json.loads(nonce_json.read_text())
    if not isinstance(data,list): raise ValueError("nonce JSON must be a list")
    matches=[]; checked=0
    for i,item in enumerate(data):
        label=str(item.get("label",f"row{i}"))
        for coord in ("x","y"):
            if coord not in item: continue
            b=hex32(str(item[coord]),f"{label}.{coord}"); checked+=1
            if p==b: matches.append((label,coord,"big-endian"))
            if p==b[::-1]: matches.append((label,coord,"byte-reversed"))
    print("payload:",p.hex()); print("coordinates checked:",checked)
    if matches:
        print("*** EXACT MATCHES ***"); [print(" ",m) for m in matches]; return 10
    print("no exact x/y match"); return 0

def get_candidate(a):
    if a.candidate is not None: return a.candidate
    b=Path(a.candidate_file).read_bytes()
    if b.endswith(b"\r\n"): b=b[:-2]
    elif b.endswith(b"\n"): b=b[:-1]
    return b.decode("utf-8")

def parser():
    p=argparse.ArgumentParser(description="Conservative offline GSMG endgame harness")
    s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("audit"); a.add_argument("--repo",default=".")
    a=s.add_parser("selftest"); a.add_argument("--repo",default=".")
    a=s.add_parser("test"); a.add_argument("--repo",default=".")
    g=a.add_mutually_exclusive_group(required=True); g.add_argument("--candidate"); g.add_argument("--candidate-file")
    a.add_argument("--source-note",default=""); a.add_argument("--log",default="offline_solver_attempts.jsonl")
    a.add_argument("--force",action="store_true"); a.add_argument("--log-plaintext",action="store_true")
    a=s.add_parser("opreturn"); a.add_argument("--payload",required=True); a.add_argument("--nonce-json",required=True)
    return p

def main():
    a=parser().parse_args()
    try:
        if a.cmd=="audit": return 0 if audit(locate_repo(a.repo)) else 3
        if a.cmd=="selftest": return 0 if selftest(locate_repo(a.repo)) else 3
        if a.cmd=="test": return run_candidate(locate_repo(a.repo),get_candidate(a),a.source_note,Path(a.log).expanduser().resolve(),a.force,a.log_plaintext)
        if a.cmd=="opreturn": return compare_opreturn(a.payload,Path(a.nonce_json))
    except (ValueError,FileNotFoundError,OSError,json.JSONDecodeError,RuntimeError) as e:
        print("ERROR:",e,file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
