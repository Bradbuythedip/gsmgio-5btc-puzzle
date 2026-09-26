#!/usr/bin/env python3
"""Campaign 55: the two-door structural comparison (neo/intake/2026-09-26-twodoor/PREREG.md).

The two terminal locks, salph_inner (A = miniA‖miniB) and P32T (B = inner96), are combined byte for byte by the
pre-registered complementarity family: 4 operations (xor, sub, rsub, add, mod 256) × 11 cells (neither door turned, or
one door turned by rev, bitrev, hswap, brev or ibrev) × 2 representations (R1 the 96-byte envelopes, R2 the 80-byte
ciphertexts) = 88 outputs, each read 4 ways (fwd, rev, ~fwd, ~rev). Every read is scanned by six exact detectors:
(a) marker, (b) raw key, (b') hex key, (b'') WIF key, (c) nested envelope, (d) verbatim target.

No AES, no gate: no output, window or substring is ever used as a candidate. Output bytes are never written or printed.
The record keeps each output's sha256, the coverage counts, a digest of the derived hash160s, and each hit's location;
a key hit records the location, encoding, form and target address, never the scalar.

  python3 campaign_55_twodoor.py --selftest   # assertions, controls 1-3, mutation check, calibration; synthetic only
  python3 campaign_55_twodoor.py --run        # the same, then the real inputs once -> neo/attempts/campaign_55_twodoor.json
"""
import argparse, base64, hashlib, json, os, re, subprocess, sys, time

import coincurve
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.dirname(HERE)
ROOT = os.path.dirname(NEO)
PREREG_REL = "neo/intake/2026-09-26-twodoor/PREREG.md"
OUT = os.path.join(NEO, "attempts", "campaign_55_twodoor.json")

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
HDR = b"Salted__"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

FILE_SHA = {
    "neo/materials/miniA.b64": "d3d0a3e67a79a578c0887d719c594e6c7f26eddda5669114666d724620349f9e",
    "neo/materials/miniB.b64": "f4bebd3743b7f655836fb3da8b71e68d77e33c3ccae8e838bbcb651b869cd54d",
    "neo/materials/inner96.b64": "a31de4756889a4778ed76c19a4a5007e55dbfc6c65f2f4e865761b115e9a36cb",
}
A_SHA = "9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258"
B_SHA = "291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9"
A_SALT, B_SALT = "3ab585348552415d", "b45a5e3d827593ca"
TARGETS = {  # address -> hash160 (the house oracle's set, addr_check.py)
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe": "a9553269572a317e39f0f518cb87c1a0ee1dbae4",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa": "4bc468447fe1b048ad030a2f9a125478eabc4ed6",
    "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": "eb862e37998c1d077a6c0b46330bccb5f73427aa",
}
PRIZE_TX = "neo/materials/chain/tx_halving_spend.hex"

OPS = ("xor", "sub", "rsub", "add")
TURNS = ("rev", "bitrev", "hswap", "brev", "ibrev")
CELLS = ("id",) + tuple(f"{d}.{g}" for g in TURNS for d in "AB")
READS = ("fwd", "rev", "~fwd", "~rev")
REPS = (("R1", 0), ("R2", 16))
LABELS = tuple(f"{r}/{o}/{c}" for r, _ in REPS for o in OPS for c in CELLS)
MARKERS = [b"HALF"]
for _w1, _w2 in ((b"BETTER", b"HALF"), (b"YIN", b"YANG"), (b"YING", b"YANG"), (b"YOU", b"WON")):
    MARKERS += [_w1 + _w2] + [_w1 + bytes([s]) + _w2 for s in b" -_"]
NESTED = (b"Salted__", b"U2FsdGVkX1")
HEX_RUN = re.compile(rb"[0-9A-Fa-f]{64,}")
B58_RUN = re.compile(rb"[1-9A-HJ-NP-Za-km-z]{51,}")
MIRROR = np.array([int(f"{b:08b}"[::-1], 2) for b in range(256)], dtype=np.uint8)
DETECTORS = ("a", "b", "b'", "b''", "c", "d")
PINNED_COVERAGE = {"outputs": 88, "reads": 352, "bytes": 30976, "marker_positions": 483296, "raw_windows": 20064,
                   "h160_windows": 24288, "address_positions": 19360, "salted_positions": 28512,
                   "b64_positions": 27808}
MUTATIONS = (["no_rev_read", "no_not_read", "no_A_cells", "r2_from_0", "no_compressed", "no_uncompressed",
              "no_last_marker_pos", "no_last_window", "no_casefold", "nul_stop", "no_hex", "no_wif", "no_nested",
              "no_verbatim"] + [f"drop_marker:{i}" for i in range(len(MARKERS))])
CAL_PAIRS, CAL_EXPECT, CAL_TOL = 10000, 18691.4, 1184


# ---------------------------------------------------------------------------------------------------------- primitives
def sha(b):
    return hashlib.sha256(b).hexdigest()


def hash160(b):
    return hashlib.new("ripemd160", hashlib.sha256(b).digest()).digest()


def stream(tag, n):
    out, ctr = b"", 0
    while len(out) < n:
        out += hashlib.sha256(tag.encode() + ctr.to_bytes(4, "big")).digest()
        ctr += 1
    return out[:n]


def b58check(payload):
    full = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    n, s = int.from_bytes(full, "big"), ""
    while n:
        n, r = divmod(n, 58)
        s = B58[r] + s
    return "1" * (len(full) - len(full.lstrip(b"\0"))) + s


def b58decode_check(s, nbytes):
    """Base58Check decode of s into exactly nbytes (payload + 4-byte checksum); None if it does not fit or fails."""
    n = 0
    for ch in s:
        n = n * 58 + B58.index(ch)
    if n >> (8 * nbytes):
        return None
    raw = n.to_bytes(nbytes, "big")
    if hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4] != raw[-4:]:
        return None
    return raw[:-4]


def p2pkh(h160):
    return b58check(b"\0" + h160)


_EC_CACHE = None   # window bytes -> (h160 compressed, h160 uncompressed); used only by the mutation check


def h160_pair(k32):
    if _EC_CACHE is not None and k32 in _EC_CACHE:
        return _EC_CACHE[k32]
    pub = coincurve.PrivateKey(k32).public_key
    r = (hash160(pub.format(compressed=True)), hash160(pub.format(compressed=False)))
    if _EC_CACHE is not None:
        _EC_CACHE[k32] = r
    return r


def wif(k, compressed):
    return b58check(b"\x80" + k.to_bytes(32, "big") + (b"\x01" if compressed else b""))


# ------------------------------------------------------------------------------------------------------------- family
def turn(g, s):
    if g == "rev":
        return s[::-1]
    if g == "bitrev":
        return MIRROR[s[::-1]]
    if g == "hswap":
        return np.roll(s, -(len(s) // 2))          # byte i = S[(i + L/2) mod L]
    if g == "brev":
        return s.reshape(-1, 16)[::-1].reshape(-1)
    if g == "ibrev":
        return s.reshape(-1, 16)[:, ::-1].reshape(-1)
    raise ValueError(g)


def op(o, x, y):
    return {"xor": lambda: x ^ y, "sub": lambda: x - y, "rsub": lambda: y - x, "add": lambda: x + y}[o]()


def inv(o, x, z):
    """The Y with op(o, x, Y) == z."""
    return {"xor": lambda: x ^ z, "sub": lambda: x - z, "rsub": lambda: z + x, "add": lambda: z - x}[o]()


def outputs(a, b, mut=frozenset()):
    """Yield (label, Z) for the 88 outputs in canonical order (uint8 arrays; arithmetic wraps mod 256)."""
    A, B = np.frombuffer(a, dtype=np.uint8), np.frombuffer(b, dtype=np.uint8)
    for rep, off in REPS:
        if rep == "R2" and "r2_from_0" in mut:
            X, Y = A[:80], B[:80]
        else:
            X, Y = A[off:], B[off:]
        for o in OPS:
            for c in CELLS:
                if c == "id":
                    z = op(o, X, Y)
                else:
                    d, g = c.split(".")
                    if d == "A" and "no_A_cells" in mut:
                        continue
                    z = op(o, turn(g, X), Y) if d == "A" else op(o, X, turn(g, Y))
                yield f"{rep}/{o}/{c}", z


def reads(z, mut=frozenset()):
    out = [("fwd", z), ("rev", z[::-1]), ("~fwd", ~z), ("~rev", ~z[::-1])]
    if "no_rev_read" in mut:
        out = [r for r in out if "rev" not in r[0]]
    if "no_not_read" in mut:
        out = [r for r in out if not r[0].startswith("~")]
    return out


# ---------------------------------------------------------------------------------------------------------- detectors
def target_map(extra=None):
    """hash160 bytes -> address, for the real targets plus any test targets."""
    t = {bytes.fromhex(h): a for a, h in TARGETS.items()}
    for h in (extra or []):
        t[h] = p2pkh(h)
    return t


def scan(a, b, targets, only=None, mut=frozenset(), markers=None, detectors=DETECTORS):
    """Scan the family on the envelopes a, b. Returns manifest, coverage, detector digest, hits, invalid windows."""
    markers = [m for i, m in enumerate(MARKERS if markers is None else markers) if f"drop_marker:{i}" not in mut]
    cf = "no_casefold" not in mut
    pats = [(m, m.lower() if cf else m) for m in markers]
    addr_pats = [(h, addr.encode()) for h, addr in targets.items()]
    cov = {k: 0 for k in ("outputs", "reads", "bytes", "marker_positions", "raw_windows", "raw_invalid",
                          "hex_windows", "wif_windows", "h160_windows", "salted_positions", "b64_positions")}
    cov["address_positions"] = {}
    manifest, hits, invalid = [], [], []
    dig = hashlib.sha256()

    def keyhits(label, rname, off, det, pair):
        if "no_compressed" not in mut and pair[0] in targets:
            hits.append((label, rname, off, det, "compressed:" + targets[pair[0]]))
        if "no_uncompressed" not in mut and pair[1] in targets:
            hits.append((label, rname, off, det, "uncompressed:" + targets[pair[1]]))

    for label, z in outputs(a, b, mut):
        if only is not None and label != only:
            continue
        cov["outputs"] += 1
        manifest.append((label, sha(z.tobytes())))
        for rname, arr in reads(z, mut):
            r = arr.tobytes()
            if "nul_stop" in mut:
                r = r.split(b"\0", 1)[0]
            L = len(r)
            cov["reads"] += 1
            cov["bytes"] += L
            if "a" in detectors:
                low = r.lower() if cf else r
                for m, pm in pats:
                    last = L - len(m) - (1 if "no_last_marker_pos" in mut else 0)
                    cov["marker_positions"] += max(0, last + 1)
                    i = low.find(pm)
                    while 0 <= i <= last:
                        hits.append((label, rname, i, "a", m.decode()))
                        i = low.find(pm, i + 1)
            if "b" in detectors:
                nwin = L - 31 - (1 if "no_last_window" in mut else 0)
                for off in range(max(0, nwin)):
                    w = r[off:off + 32]
                    cov["raw_windows"] += 1
                    k = int.from_bytes(w, "big")
                    if 1 <= k < N:
                        pair = h160_pair(w)
                        dig.update(pair[0] + pair[1])
                        keyhits(label, rname, off, "b", pair)
                    else:
                        cov["raw_invalid"] += 1
                        invalid.append((label, rname, off))
                        dig.update(bytes(40))
            if "b'" in detectors and "no_hex" not in mut:
                for mt in HEX_RUN.finditer(r):
                    for j in range(mt.start(), mt.end() - 63):
                        cov["hex_windows"] += 1
                        k = int(r[j:j + 64], 16)
                        if 1 <= k < N:
                            keyhits(label, rname, j, "b'", h160_pair(k.to_bytes(32, "big")))
            if "b''" in detectors and "no_wif" not in mut:
                for mt in B58_RUN.finditer(r):
                    for j in range(mt.start(), mt.end()):
                        c0 = r[j]
                        for want, n in ((b"5"[0], 51), (b"K"[0], 52), (b"L"[0], 52)):
                            if c0 != want or j + n > mt.end():
                                continue
                            cov["wif_windows"] += 1
                            pl = b58decode_check(r[j:j + n].decode(), n - 51 + 37)
                            if pl is None or pl[0] != 0x80 or (n == 52 and pl[33] != 1):
                                continue
                            k = int.from_bytes(pl[1:33], "big")
                            if 1 <= k < N:
                                keyhits(label, rname, j, "b''", h160_pair(k.to_bytes(32, "big")))
            if "c" in detectors:
                cov["salted_positions"] += max(0, L - 7)
                cov["b64_positions"] += max(0, L - 9)
                if "no_nested" not in mut:
                    for pat in NESTED:
                        i = r.find(pat)
                        while i >= 0:
                            hits.append((label, rname, i, "c", pat.decode()))
                            i = r.find(pat, i + 1)
            if "d" in detectors:
                cov["h160_windows"] += max(0, L - 19)
                for h, ab in addr_pats:
                    addr = targets[h]
                    cov["address_positions"][addr] = cov["address_positions"].get(addr, 0) + max(0, L - len(ab) + 1)
                    if "no_verbatim" in mut:
                        continue
                    for pat, kind in ((h, "hash160"), (ab, "address")):
                        i = r.find(pat)
                        while i >= 0:
                            hits.append((label, rname, i, "d", f"{kind}:{addr}"))
                            i = r.find(pat, i + 1)
    text = "".join(f"{lab} {h}\n" for lab, h in manifest)
    return {"manifest": manifest, "manifest_sha256": sha(text.encode()), "coverage": cov,
            "detector_digest": dig.hexdigest(), "hits": hits, "invalid": invalid}


def coverage_ok(cov):
    bad = {k: cov.get(k) for k, v in PINNED_COVERAGE.items() if k != "address_positions" and cov.get(k) != v}
    for addr in TARGETS:
        if cov["address_positions"].get(addr) != PINNED_COVERAGE["address_positions"]:
            bad["address_positions:" + addr] = cov["address_positions"].get(addr)
    return bad


# ------------------------------------------------------------------------------------------------------------ inputs
def load_inputs():
    """Decode and hash the two envelopes. Nothing is combined here."""
    for rel, want in FILE_SHA.items():
        got = sha(open(os.path.join(ROOT, rel), "rb").read())
        assert got == want, f"{rel}: sha256 {got} != {want}"
    ws = lambda rel: re.sub(rb"[ \t\r\n\f\v]", b"", open(os.path.join(ROOT, rel), "rb").read())
    a = base64.b64decode(ws("neo/materials/miniA.b64") + ws("neo/materials/miniB.b64"), validate=True)
    b = base64.b64decode(ws("neo/materials/inner96.b64"), validate=True)
    assert len(a) == 96 and sha(a) == A_SHA and a[:8] == HDR and a[8:16].hex() == A_SALT, "input A"
    assert len(b) == 96 and sha(b) == B_SHA and b[:8] == HDR and b[8:16].hex() == B_SALT, "input B"
    return a, b


def startup_assertions():
    for addr, h in TARGETS.items():
        n = 0
        for ch in addr:
            n = n * 58 + B58.index(ch)
        raw = n.to_bytes(25, "big")
        assert raw[0] == 0 and hashlib.sha256(hashlib.sha256(raw[:21]).digest()).digest()[:4] == raw[21:], addr
        assert raw[1:21].hex() == h and p2pkh(bytes.fromhex(h)) == addr, addr
    hx = open(os.path.join(ROOT, PRIZE_TX)).read().strip()
    m = re.search("4104f4d1bb([0-9a-f]{122})", hx)
    assert m and hash160(bytes.fromhex("04f4d1bb" + m.group(1))).hex() == TARGETS["1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"]
    hc, hu = h160_pair((1).to_bytes(32, "big"))
    assert p2pkh(hc) == "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH" and p2pkh(hu) == "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"
    assert len(MARKERS) == 17 and len(LABELS) == 88
    return True


# ---------------------------------------------------------------------------------------------------------- controls
def case_pattern(m, c):
    if c % 3 == 0:
        return m
    if c % 3 == 1:
        return m.lower()
    out, j = bytearray(), 0
    for ch in m:
        if chr(ch).isalpha():
            out.append(ord(chr(ch).lower()) if j % 2 == 0 else ord(chr(ch).upper()))
            j += 1
        else:
            out.append(ch)
    return bytes(out)


def control1(c, mut=frozenset()):
    label, rname = LABELS[c // 4], READS[c % 4]
    M = MARKERS[c % 17]
    Mc = case_pattern(M, c)
    t = int.from_bytes(stream(f"twodoor/ctl/k/{c}", 32), "big") % (N - 1) + 1
    tb = t.to_bytes(32, "big")

    def plants(P, f0, f1):
        om, ok = (f0, f1 - 32) if c % 2 == 0 else (f1 - len(M), f0)
        P[om:om + len(M)] = Mc
        P[ok:ok + 32] = tb
        return om, ok

    a, b, (om, ok) = build_pair_tags(label, rname, "twodoor/ctl", str(c), plants)
    hc, hu = h160_pair(tb)
    form, th = ("compressed", hc) if c % 4 in (0, 1) else ("uncompressed", hu)
    tm = target_map([th])
    res = scan(a, b, tm, only=label, mut=mut)
    want_a = (label, rname, om, "a", M.decode())
    want_b = (label, rname, ok, "b", f"{form}:{tm[th]}")
    return want_a in res["hits"] and want_b in res["hits"], res["hits"]


def build_pair_tags(label, rname, base, suffix, plants_fn):
    """A synthetic (A, B) whose output `label`, read `rname`, is a planted read P (PREREG control 1).

    Tags follow the PREREG: <base>/A/<suffix>, <base>/P/<suffix>, <base>/S/<suffix>. plants_fn(P, f0, f1) writes the
    plants into the bytearray P inside the free region [f0, f1) and returns what it planted."""
    rep, o, cell = label.split("/")
    L = 96 if rep == "R1" else 80
    a = HDR + stream(f"{base}/A/{suffix}", 88)
    X = np.frombuffer(a if rep == "R1" else a[16:], dtype=np.uint8)
    P = bytearray(stream(f"{base}/P/{suffix}", L))
    f0, f1 = 0, L
    if rep == "R1" and cell == "id":
        h = op(o, np.frombuffer(HDR, dtype=np.uint8), np.frombuffer(HDR, dtype=np.uint8))
        fixed = {"fwd": h, "rev": h[::-1], "~fwd": ~h, "~rev": (~h)[::-1]}[rname].tobytes()
        if rname in ("fwd", "~fwd"):
            P[0:8], f0 = fixed, 8
        else:
            P[L - 8:L], f1 = fixed, L - 8
    planted = plants_fn(P, f0, f1)
    Pn = np.frombuffer(bytes(P), dtype=np.uint8)
    Z = {"fwd": Pn, "rev": Pn[::-1], "~fwd": ~Pn, "~rev": (~Pn)[::-1]}[rname]
    if cell == "id":
        Y = inv(o, X, Z)
    else:
        d, g = cell.split(".")
        Y = turn(g, inv(o, X, Z)) if d == "B" else inv(o, turn(g, X), Z)
    b = Y.tobytes() if rep == "R1" else HDR + stream(f"{base}/S/{suffix}", 8) + Y.tobytes()
    return a, b, planted


def control2(p, t, mut=frozenset()):
    rep, o = REPS[p // 4][0], OPS[p % 4]
    label, rname = f"{rep}/{o}/{CELLS[(p + t) % 11]}", READS[(p + t) % 4]
    k = int.from_bytes(stream(f"twodoor/ctl2/k/{p}/{t}", 32), "big") % (N - 1) + 1
    hc, hu = h160_pair(k.to_bytes(32, "big"))
    plant = [format(k, "064x").encode(), wif(k, True).encode(), wif(k, False).encode(), NESTED[0], NESTED[1],
             hc, p2pkh(hc).encode()][t]

    def plants(P, f0, f1):
        off = f0 if (p + t) % 2 == 0 else f1 - len(plant)
        P[off:off + len(plant)] = plant
        return off

    a, b, off = build_pair_tags(label, rname, "twodoor/ctl2", f"{p}/{t}", plants)
    tm = target_map([hc, hu])
    res = scan(a, b, tm, only=label, mut=mut)
    det = ["b'", "b''", "b''", "c", "c", "d", "d"][t]
    ok = False
    for h in res["hits"]:
        if h[:4] != (label, rname, off, det):
            continue
        if t in (3, 4) and h[4] != plant.decode():
            continue
        if t == 5 and h[4] != "hash160:" + p2pkh(hc):
            continue
        if t == 6 and h[4] != "address:" + p2pkh(hc):
            continue
        ok = True
    return ok, res["hits"]


NEAR = [("HALG", 0), ("HAL", -3), ("LF|HA", None), ("YIN.YANG", 0), ("YOU  WON", 0), ("0|n|max", None)]


def control_n2(i):
    label, rname = "R1/xor/B.rev", "fwd"
    name, pos = NEAR[i]

    def plants(P, f0, f1):
        L = len(P)
        if name == "LF|HA":
            P[0:2], P[L - 2:L] = b"LF", b"HA"
        elif name == "0|n|max":
            P[0:32], P[32:64], P[64:96] = bytes(32), N.to_bytes(32, "big"), b"\xff" * 32
        else:
            s = name.encode()
            off = pos if pos >= 0 else L + pos
            P[off:off + len(s)] = s
        return None

    a, b, _ = build_pair_tags(label, rname, "twodoor/n2", str(i), plants)
    res = scan(a, b, target_map(), only=label)
    ok = not res["hits"]
    if name == "0|n|max":
        ok = ok and all((label, "fwd", o) in res["invalid"] for o in (0, 32, 64))
    return ok, res["hits"]


def run_controls(mut=frozenset(), stop_early=False):
    fails = []
    for c in range(352):
        ok, _ = control1(c, mut)
        if not ok:
            fails.append(f"ctl1:{c}")
            if stop_early:
                return fails
    for p in range(8):
        for t in range(7):
            ok, _ = control2(p, t, mut)
            if not ok:
                fails.append(f"ctl2:{p}/{t}")
                if stop_early:
                    return fails
    return fails


def negative_n1():
    a = HDR + stream("twodoor/neg/A", 88)
    b = HDR + stream("twodoor/neg/B", 88)
    res = scan(a, b, target_map())
    return res


def calibration():
    counts, batch = 0, []
    for i in range(CAL_PAIRS):
        a = HDR + stream(f"twodoor/cal/A/{i}", 88)
        b = HDR + stream(f"twodoor/cal/B/{i}", 88)
        n = len(scan(a, b, {}, markers=[b"HA"], detectors=("a",))["hits"])
        counts += n
        if i % 100 == 0:
            batch.append(0)
        batch[-1] += n
    mean = sum(batch) / len(batch)
    sd = (sum((x - mean) ** 2 for x in batch) / (len(batch) - 1)) ** 0.5
    return {"pairs": CAL_PAIRS, "observed": counts, "expected": CAL_EXPECT, "tolerance": CAL_TOL,
            "batches": len(batch), "batch_mean": mean, "batch_sd": round(sd, 2),
            "pass": abs(counts - CAL_EXPECT) <= CAL_TOL}


def mutation_check():
    global _EC_CACHE
    _EC_CACHE = {}
    table = []
    try:
        for s in MUTATIONS:
            f = run_controls(frozenset([s]))
            table.append({"switch": s, "failing_controls": len(f)})
    finally:
        _EC_CACHE = None
    return table


# ------------------------------------------------------------------------------------------------------------- main
def prereg_state():
    path = os.path.join(ROOT, PREREG_REL)
    body = open(path, "rb").read()
    dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", PREREG_REL],
                           capture_output=True, text=True).stdout.strip()
    committed = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%H", "--", PREREG_REL],
                               capture_output=True, text=True).stdout.strip()
    frozen = b"frozen at this commit" in body and b"DRAFT" not in body.split(b"\n## ")[0]
    return {"path": PREREG_REL, "sha256": sha(body), "clean": not dirty, "last_commit": committed, "frozen": frozen}


def fmt_hit(h):
    return f"{h[0]} {h[1]} @{h[2]} ({h[3]}) {h[4]}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--run", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    rec = {"campaign": 55, "prereg": prereg_state(), "script_sha256": sha(open(__file__, "rb").read())}
    if args.run and not (rec["prereg"]["clean"] and rec["prereg"]["frozen"] and rec["prereg"]["last_commit"]):
        sys.exit(f"refusing --run: the PREREG must be committed, clean and frozen ({rec['prereg']})")

    rec["startup_assertions"] = startup_assertions()
    load_inputs()   # hashes only; nothing is combined before the controls pass
    rec["inputs"] = {"files": FILE_SHA, "A_sha256": A_SHA, "B_sha256": B_SHA, "A_salt": A_SALT, "B_salt": B_SALT}
    print("[55] startup assertions: pass", flush=True)

    fails = run_controls()
    rec["controls"] = {"ctl1": {"n": 352, "failed": [f for f in fails if f.startswith("ctl1")]},
                       "ctl2": {"n": 56, "failed": [f for f in fails if f.startswith("ctl2")]}}
    print(f"[55] controls 1-2: {408 - len(fails)}/408 pass", flush=True)
    n2 = [control_n2(i) for i in range(len(NEAR))]
    rec["controls"]["n2"] = {"n": len(NEAR), "failed": [NEAR[i][0] for i, (ok, _) in enumerate(n2) if not ok]}
    n1 = negative_n1()
    bad = coverage_ok(n1["coverage"])
    rec["controls"]["n1"] = {"manifest_sha256": n1["manifest_sha256"], "detector_digest": n1["detector_digest"],
                             "coverage": n1["coverage"], "coverage_mismatch": bad, "hits": [fmt_hit(h) for h in n1["hits"]]}
    print(f"[55] N1: hits {len(n1['hits'])}, coverage mismatches {bad or 'none'}; N2 near misses failed: "
          f"{rec['controls']['n2']['failed'] or 'none'}", flush=True)
    ctl_ok = not fails and not rec["controls"]["n2"]["failed"] and not n1["hits"] and not bad

    table = mutation_check()
    mut_ok = all(r["failing_controls"] > 0 for r in table)
    rec["mutation"] = {"table": table, "pass": mut_ok}
    print(f"[55] mutation check: {sum(r['failing_controls'] > 0 for r in table)}/{len(table)} switches caught", flush=True)

    cal = calibration()
    rec["calibration"] = cal
    print(f"[55] calibration: observed {cal['observed']} vs expected {CAL_EXPECT} ± {CAL_TOL}: "
          f"{'pass' if cal['pass'] else 'FAIL'} (batch sd {cal['batch_sd']})", flush=True)

    ok = ctl_ok and mut_ok and cal["pass"]
    rec["checks_pass"] = ok
    if not args.run:
        print(f"[55] selftest {'PASS' if ok else 'FAIL'} in {time.time() - t0:.0f}s")
        return 0 if ok else 1
    if not ok:
        rec["verdict"] = "VOID"
        json.dump(rec, open(OUT, "w"), indent=1)
        sys.exit("[55] VOID: a check failed; the real inputs were not combined")

    a, b = load_inputs()
    real = scan(a, b, target_map())
    bad = coverage_ok(real["coverage"])
    verdict = "VOID" if bad else ("HIT" if real["hits"] else "NULL")
    rec["real"] = {"manifest": real["manifest"], "manifest_sha256": real["manifest_sha256"],
                   "coverage": real["coverage"], "coverage_mismatch": bad, "detector_digest": real["detector_digest"],
                   "hits": [{"label": h[0], "read": h[1], "offset": h[2], "detector": h[3], "detail": h[4]}
                            for h in real["hits"]]}
    rec["verdict"] = verdict
    rec["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"[55] real inputs: manifest {real['manifest_sha256']}, digest {real['detector_digest']}")
    print(f"[55] coverage {'as pinned' if not bad else bad}; hits {len(real['hits'])}")
    for h in real["hits"]:
        print("   HIT", fmt_hit(h))
    print(f"[55] VERDICT: {verdict}  (record: {os.path.relpath(OUT, ROOT)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
