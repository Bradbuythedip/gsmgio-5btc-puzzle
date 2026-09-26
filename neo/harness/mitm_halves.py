#!/usr/bin/env python3
"""Meet-in-the-middle for a two-part prize key ("half and better half").

If the prize key is k = a + b, a - b, or a * b (mod n) for two scalars a, b drawn from one
candidate pool, then with the prize PUBLIC key P:
    add:  P - bG == aG      sub:  P + bG == aG      mul:  b^-1 * P == aG
so a table of aG plus one EC operation per b tests every pair: |pool|^2 pairs for
~2|pool| operations. XOR and concatenation are not group operations and cannot be done
this way.

The pool is every string the project has touched, each as sha256(s) (the puzzle's
"sha b4" convention) and, when it is 64 hex, also as the scalar itself:
  - every logged candidate in ../attempts/*.jsonl (logs only kept trials with some pad,
    so this is a subset of what was tried)
  - 1..4-word n-grams (joined, lowercased) of the primary texts and creator messages

Needs the prize public key, which is on-chain in the scriptSig of the 2020-05-11 halving
spend from 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe. The key is refused unless it hashes to
that address or to 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa (the better-half address, #3902).

  python3 mitm_halves.py --selftest       planted-pair recovery for add/sub/mul + negative
  python3 mitm_halves.py <pubkey_hex>     the one-shot run
"""
import glob, hashlib, json, os, re, sys, time, random
import coincurve
from coincurve import PublicKey

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
REPO = os.path.join(NEO, "..")
sys.path.insert(0, HERE)
from btc_addr import p2pkh, N

PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"   # #3902: "the half of prize went to better half" -> "Well spotted"
TEXTS = ["materials/phase32_plaintext_outer.txt", "materials/salphaseion_page.txt",
         "../phase2-assets/phase2.1.txt", "../phase2-assets/phase3.txt",
         "materials/primary/hint_2023-02-23_decoded.txt"]

def sc(k):
    return (k % N).to_bytes(32, "big")

def build_pool():
    strings = set()
    for p in glob.glob(os.path.join(NEO, "attempts", "*.jsonl")):
        for line in open(p, errors="replace"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            s = r.get("pw") or r.get("candidate")
            if s:
                strings.add(s)
    corpus = []
    for t in TEXTS:
        corpus.append(open(os.path.join(NEO, t), encoding="latin-1").read())
    for line in open(os.path.join(NEO, "materials/primary/CREATOR-LOG_transcript_445_messages.md"), encoding="utf-8"):
        if re.match(r"\| \d+ \|", line):
            corpus.append(re.sub(r"_\(↩.*?\)_", "", line.split("|")[4]))
    for text in corpus:
        words = re.findall(r"[a-z0-9]+", text.lower())
        for n in range(1, 5):
            for i in range(len(words) - n + 1):
                strings.add("".join(words[i:i + n]))
    pool = {}
    for s in strings:
        k = int.from_bytes(hashlib.sha256(s.encode("utf-8", "ignore")).digest(), "big") % N
        if k: pool.setdefault(k, "sha256:" + s[:80])
        if re.fullmatch(r"[0-9a-fA-F]{64}", s):
            k = int(s, 16) % N
            if k: pool.setdefault(k, "hex:" + s)
    return pool

def point(k):
    return PublicKey.from_secret(sc(k))

def mitm(P, pool, ops=("add", "sub", "mul")):
    items = list(pool.items())
    table = {point(k).format(): k for k, _ in items}
    Pneg_ok = True
    hits = []
    for op in ops:
        for b, lbl in items:
            if op == "add":
                try: Q = PublicKey.combine_keys([P, point(N - b)])
                except Exception: continue          # P == bG: a would be 0
            elif op == "sub":
                try: Q = PublicKey.combine_keys([P, point(b)])
                except Exception: continue
            else:
                Q = P.multiply(sc(pow(b, -1, N)))
            a = table.get(Q.format())
            if a is not None:
                hits.append((op, pool[a], lbl))
    return hits

def check_pub(hexkey):
    raw = bytes.fromhex(hexkey)
    addr = p2pkh(raw)
    if addr not in (PRIZE, BETTER):
        raise SystemExit(f"refused: pubkey hashes to {addr}, not {PRIZE} or {BETTER}")
    print("target:", addr)
    return PublicKey(raw)

def selftest():
    pool = build_pool()
    items = list(pool.items())
    rnd = random.Random(7)
    ok = True
    sub = dict(rnd.sample(items, 3000))      # small pool keeps the self-test fast
    a, b = rnd.sample(list(sub), 2)
    for op, k in (("add", a + b), ("sub", a - b), ("mul", a * b)):
        hits = mitm(point(k % N), sub, ops=(op,))
        good = any(h[0] == op and h[1] == sub[a] and h[2] == sub[b] for h in hits)
        print(("OK  " if good else "FAIL"), f"planted {op} pair recovered", len(hits))
        ok &= good
    neg = mitm(point(rnd.randrange(1, N)), sub)
    print(("OK  " if not neg else "FAIL"), "random point: no pair", len(neg))
    ok &= not neg
    print(f"pool size (full): {len(pool)} scalars -> {len(pool)**2:.2e} pairs per operation")
    print("mitm self-test passed:", ok)
    return ok

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "--selftest":
        sys.exit(0 if selftest() else 1)
    P = check_pub(sys.argv[1])
    pool = build_pool()
    t = time.time()
    hits = mitm(P, pool)
    print(f"pool {len(pool)} scalars, {3*len(pool)**2:.2e} pairs tested in {time.time()-t:.0f}s")
    print("HITS:", hits if hits else "none")
    sys.exit(10 if hits else 0)
