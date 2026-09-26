#!/usr/bin/env python3
"""Frozen one-shot gate. The corpus is parked; this is the only door left open.

One intake file names one candidate string and where it came from. The gate refuses
anything without primary provenance or anything already spent, then runs exactly:

  candidate -> {raw, sha256hex}
            -> EVP_BytesToKey {MD5, SHA256}, aes-256-cbc
            -> {miniA, miniAB, P32T (inner96), Cosmic}
            -> strict PKCS#7 + printable/magic gate (aes_try.check_pt)
  candidate -> sha256 scalar (and the candidate itself if it is 64 hex)
            -> uncompressed P2PKH == PRIZE

That is 16 decrypts and at most 2 scalar checks per intake. No sliding windows, no
substrings chosen by the gate, no subset XOR, no extra KDFs. The protocol is frozen:
widen it and every null recorded through it stops meaning anything.

Admissible kinds (anything else is refused):
  jrk_sentence     a new Jrk/@SoWut message: id, date, author, text (full, verbatim)
  gsmg_page        a new gsmg.io page: url, fetched_at, body_file (the saved response)
  uttered_password a password a person in that circle actually said: speaker, date,
                   where, candidate (verbatim). Not inferred, not derived.

`candidate` defaults to the full text / page body and, if given, must occur verbatim in
it. The gate never picks one for you.

Spent material is refused before any decrypt:
  - any exact string already in attempts/*.jsonl (raw or its sha256hex form)
  - any string whose normalized form (a-z0-9) occurs in the ledger or the parked corpus
    (LEDGER.md, materials/, materials/primary/, prior-sessions/, ../unverified/, and the
    literal candidates in harness/campaign_*.py and attempts/*.txt)
  - any candidate already run through this gate (attempts/gate_intake.jsonl)

Usage:
  python3 gate.py --selftest          positive + refusal controls; must pass first
  python3 gate.py intake.json         one shot; exit 0 null, 2 refused, 10 HIT
"""
import glob, hashlib, json, os, re, sys, time
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import aes_try
import btc_addr

PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
TARGETS = ("miniA", "miniAB", "inner96", "cosmic")   # inner96 = P32T
KDFS = ("m5", "s2")                                  # EVP md5 / sha256, aes-256-cbc
FORMS = ("raw", "sha256hex")
INTAKE_LOG = os.path.join(NEO, "attempts", "gate_intake.jsonl")
HELLO_404 = b"Hello :-)"
MIN_SUBSTR = 6   # shorter normalized strings match corpus tokens exactly instead

REQUIRED = {
    "jrk_sentence": ("id", "date", "author", "text"),
    "gsmg_page": ("url", "fetched_at", "body_file"),
    "uttered_password": ("speaker", "date", "where", "candidate"),
}

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def sha256hex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ---------- spent material ----------

def load_tried():
    tried = set()
    for p in glob.glob(os.path.join(NEO, "attempts", "*.jsonl")):
        with open(p, errors="replace") as f:
            for line in f:
                try:
                    pw = json.loads(line).get("pw")
                except ValueError:
                    continue
                if pw:
                    tried.add(pw)
    return tried

def _read(pats):
    out = []
    for pat in pats:
        for p in sorted(glob.glob(os.path.join(NEO, pat))):
            with open(p, errors="replace") as f:
                out.append(f.read())
    return "\n".join(out)

def load_corpus():
    """Prose (ledger, materials, notes) gives substrings and tokens. Campaign sources and
    token lists give substrings only, since they hold literal candidates that never reached
    a JSONL log (e.g. campaigns 32/33), alongside Python keywords."""
    prose = _read(["LEDGER.md", "materials/*.txt", "materials/primary/*.txt",
                   "materials/primary/*.md", "materials/primary/*.json",
                   "prior-sessions/*/*.md", "../unverified/*.md"])
    code = _read(["harness/campaign_*.py", "harness/p32t_freeze.py", "attempts/*.txt"])
    return (norm(prose) + "|" + norm(code),
            set(norm(t) for t in re.split(r"\W+", prose) if t))

def spent_reason(cand, tried, corpus, tokens, intake):
    h = sha256hex(cand)
    if h in intake:
        return "already run through this gate"
    if cand in tried or h in tried or h.upper() in tried:
        return "exact string already in attempts/*.jsonl"
    n = norm(cand)
    if not n:
        return "empty after normalization"
    if len(n) >= MIN_SUBSTR and n in corpus:
        return "occurs in the ledger / parked corpus"
    if len(n) < MIN_SUBSTR and n in tokens:
        return "is a token of the ledger / parked corpus"
    return None

def load_intake_log():
    seen = set()
    if os.path.exists(INTAKE_LOG):
        with open(INTAKE_LOG) as f:
            for line in f:
                seen.add(json.loads(line)["candidate_sha256"])
    return seen

# ---------- provenance ----------

def admit(intake):
    """Return (candidate, provenance) or raise ValueError with the refusal reason."""
    kind = intake.get("kind")
    if kind not in REQUIRED:
        raise ValueError(f"kind must be one of {sorted(REQUIRED)}; got {kind!r}")
    missing = [k for k in REQUIRED[kind] if not str(intake.get(k, "")).strip()]
    if missing:
        raise ValueError(f"{kind} missing provenance: {missing}")
    prov = {k: intake[k] for k in REQUIRED[kind]}
    if kind == "jrk_sentence":
        source = intake["text"]
    elif kind == "gsmg_page":
        host = (urlparse(intake["url"]).hostname or "").lower()
        if host != "gsmg.io" and not host.endswith(".gsmg.io"):
            raise ValueError(f"not a gsmg.io url: {intake['url']}")
        body = open(intake["body_file"], "rb").read()
        if body.strip() == HELLO_404 or len(body.strip()) <= len(HELLO_404):
            raise ValueError("page body is the 9-byte 'Hello :-)' 404 (or shorter)")
        prov["body_sha256"] = hashlib.sha256(body).hexdigest()
        prov["body_len"] = len(body)
        source = body.decode("utf-8", "replace")
    else:
        source = intake["candidate"]
    cand = intake.get("candidate", source)
    if cand not in source:
        raise ValueError("candidate does not occur verbatim in its source")
    return cand, prov

# ---------- the frozen run ----------

def run_decrypts(cand, targets):
    out = []
    for form in FORMS:
        pw = cand if form == "raw" else sha256hex(cand)
        for kdf in KDFS:
            md, keylen = aes_try.KDFS[kdf]
            for tname in TARGETS:
                t = targets[tname]
                key, iv = aes_try.evp_bytes_to_key(pw.encode("utf-8"), t["salt"], md, keylen)
                res = aes_try.check_pt(aes_try.decrypt(t["ct"], key, iv))
                rec = {"form": form, "kdf": kdf, "target": tname, "pad": None, "hit": False}
                if res:
                    rec.update(pad=res["pad"], printable=res["printable"], hit=res["hit"])
                    if res["hit"]:
                        rec["body_head"] = res["body"][:200].decode("latin1")
                        rec["body_addr"] = body_addresses(res["body"])
                out.append(rec)
    return out

def body_addresses(body):
    """If a decrypted body carries a 64-hex scalar, report its uncompressed address."""
    found = []
    for m in re.findall(rb"\b[0-9a-fA-F]{64}\b", body):
        k = int(m, 16)
        _, u = btc_addr.addrs(k)
        if u:
            found.append({"hex": m.decode(), "uncompressed": u, "prize": u == PRIZE})
    return found

def run_scalars(cand):
    out = []
    scalars = [("sha256(candidate)", int(sha256hex(cand), 16))]
    if re.fullmatch(r"[0-9a-fA-F]{64}", cand):
        scalars.append(("candidate as hex", int(cand, 16)))
    for label, k in scalars:
        _, u = btc_addr.addrs(k)
        out.append({"scalar": label, "uncompressed": u, "prize": u == PRIZE})
    return out

def one_shot(intake_path):
    intake = json.load(open(intake_path))
    try:
        cand, prov = admit(intake)
    except (ValueError, OSError) as e:
        print("REFUSED (provenance):", e)
        return 2
    reason = spent_reason(cand, load_tried(), *load_corpus(), load_intake_log())
    if reason:
        print("REFUSED (spent):", reason)
        return 2
    if not aes_try.self_test():
        print("ABORT: aes_try self-test failed; a null here would mean nothing")
        return 3
    dec = run_decrypts(cand, aes_try.load_targets())
    sca = run_scalars(cand)
    hit = any(r["hit"] for r in dec) or any(s["prize"] for s in sca)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": intake["kind"],
           "provenance": prov, "candidate": cand, "candidate_sha256": sha256hex(cand),
           "decrypts": dec, "scalars": sca, "HIT": hit}
    with open(INTAKE_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    near = [r for r in dec if r["pad"]]
    print(f"decrypts={len(dec)} pkcs7_any={len(near)} hit={hit}")
    for r in near:
        print("  ", json.dumps(r)[:300])
    for s in sca:
        print("  ", json.dumps(s))
    print("*** HIT ***" if hit else "null. Logged; this candidate is now spent.")
    return 10 if hit else 0

# ---------- controls ----------

def selftest():
    ok = aes_try.self_test() and btc_addr.self_test()
    tried = load_tried()
    corpus, tokens = load_corpus()
    none = set()
    checks = [
        # already in the corpus / ledger: must be refused
        ("THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF", True),
        ("causality", True),
        ("jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple", True),
        ("matrixsumlist", True),
        ("331360369421418441396", True),        # campaign 33 layer sums, never JSONL-logged
        ("yellowblueprimes", True),
        ("need funds to live", True),
        # fresh strings: must be admitted
        ("zq7 fresh control string not in any corpus 2026", False),
    ]
    for s, want_refused in checks:
        got = spent_reason(s, tried, corpus, tokens, none) is not None
        print(("OK  " if got == want_refused else "FAIL"), "spent" if got else "fresh", repr(s[:50]))
        ok = ok and got == want_refused
    refusals = [
        {"kind": "inferred", "candidate": "x"},
        {"kind": "jrk_sentence", "id": "1", "date": "2026-01-01", "text": "hi"},  # no author
    ]
    for intake in refusals:
        try:
            admit(intake)
            print("FAIL admitted", intake["kind"]); ok = False
        except ValueError as e:
            print("OK   refused:", e)
    # a Hello :-) 404 page must be refused
    import tempfile
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(HELLO_404)
    try:
        admit({"kind": "gsmg_page", "url": "https://gsmg.io/x", "fetched_at": "now",
               "body_file": f.name})
        print("FAIL admitted 404 page"); ok = False
    except ValueError as e:
        print("OK   refused:", e)
    finally:
        os.unlink(f.name)
    # the decrypt path itself: the phase-3.2 password must hit on its own blob
    import base64
    raw = base64.b64decode("".join(open(os.path.join(NEO, "..", "phase3-assets",
                                                     "phase3.2-aes.txt")).read().split()))
    fake = {n: {"salt": raw[8:16], "ct": raw[16:]} for n in TARGETS}
    dec = run_decrypts("jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple", fake)
    good = any(r["hit"] and r["form"] == "sha256hex" and r["kdf"] == "s2" for r in dec)
    print(("OK  " if good else "FAIL"), "frozen decrypt path reproduces phase 3.2")
    ok = ok and good
    print("gate self-test passed:", ok)
    return ok

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "--selftest":
        sys.exit(0 if selftest() else 1)
    sys.exit(one_shot(sys.argv[1]))
