#!/usr/bin/env python3
"""Campaign 55: the two-door structural comparison (neo/intake/2026-09-26-twodoor/PREREG.md).

The two terminal locks, salph_inner (A = miniA‖miniB) and P32T (B = inner96), are combined byte for byte by the
pre-registered complementarity family: 4 operations (xor, sub, rsub, add, mod 256) × 11 cells (neither door turned, or
one door turned by rev, bitrev, hswap, brev or ibrev) × 2 representations (R1 the 96-byte envelopes, R2 the 80-byte
ciphertexts) = 88 outputs, each read 6 ways (fwd, rev, bitrev, ~fwd, ~rev, ~bitrev). Every read is scanned by six
exact detectors: a (marker), b (raw key), b_hex (hex key), b_wif (WIF key), c (nested envelope), d (verbatim target).
Every scan runs to completion and lists every event; a HIT only means nothing follows it without the user.

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
READS = ("fwd", "rev", "bitrev", "~fwd", "~rev", "~bitrev")
REPS = (("R1", 0), ("R2", 16))
LABELS = tuple(f"{r}/{o}/{c}" for r, _ in REPS for o in OPS for c in CELLS)
MARKERS = [b"HALF"]
for _w1, _w2 in ((b"BETTER", b"HALF"), (b"YIN", b"YANG"), (b"YING", b"YANG"), (b"YOU", b"WON")):
    MARKERS += [_w1 + _w2] + [_w1 + bytes([s]) + _w2 for s in b" -_"]
NESTED = (b"Salted__", b"U2FsdGVkX1")
HEX_RUN = re.compile(rb"[0-9A-Fa-f]{64,}")
B58_RUN = re.compile(rb"[1-9A-HJ-NP-Za-km-z]{51,}")
MIRROR = np.array([int(f"{b:08b}"[::-1], 2) for b in range(256)], dtype=np.uint8)
DETECTORS = ("a", "b", "b_hex", "b_wif", "c", "d")
# The PREREG's coverage record, in its order. None = data-dependent (reported and compared, not pinned).
COVERAGE_KEYS = ("outputs", "reads", "bytes", "a_positions", "a_half_positions", "b_windows", "b_invalid",
                 "b_hex_windows", "b_hex_invalid", "b_wif_windows", "b_wif_decoded", "d_h160_windows",
                 "d_addr_positions_prize", "d_addr_positions_17ucy1", "d_addr_positions_1NULY7",
                 "c_salted_positions", "c_b64_positions")
PINNED_COVERAGE = dict(zip(COVERAGE_KEYS, (88, 528, 46464, 724944, 44880, 30096, None, None, None, None, None, 36432,
                                           29040, 29040, 29040, 42768, 41712)))
TURN_KAT = {  # sha256 of turn(00 01 .. L-1): the PREREG's known answers
    96: {"rev": "b2d9996f81492a827ed4fe7c36ff83960b49071835fd1dda377d80497f5360df",
         "bitrev": "4632963b5ac8fc1bef565eb9a26f164b586d6961fe674f05811f3236e17a81a7",
         "hswap": "d41d559270b9ee078d6d46f1f63547172173b3ba1df4f00c77bde438807dbf98",
         "brev": "ec518b4bfd733a0b679f60768ae1802cad302ec9ca1670d2a43866e97633b4e9",
         "ibrev": "dedc02e27b32f48b38a0705180e635b0fbded4983e32581306a140280a2574a2"},
    80: {"rev": "939fc6c065bfdd55219a2fc10652ae08c8b92c4df7d4ff5f5b28706b263d803e",
         "bitrev": "b42ad22f5cb8a8652f6f0c3aa05bb765c4daf36c427fb08677dfd31d79a52b0f",
         "hswap": "686bd663b458f24f9971da499ef56a2aa4f741b668bb1e17f3b93d5be4ce9034",
         "brev": "ed2ad0fa3e299e35c3d6c35d0c8fca853a00b7abdd55312fa72d73819e58f7d1",
         "ibrev": "b0c9caac8dc07824d1486ab900ff61d19e912d2ad21197bec3577b0f1a20c36e"},
}
N1_MANIFEST = "a5103f89230d11dbfba3fe688a8a2482957820a24954f454e516deb843a96233"
MUTATIONS = (["no_rev_read", "no_bitrev_read", "no_not_read", "no_A_cells", "r2_from_0", "no_compressed",
              "no_uncompressed", "no_last_marker_pos", "no_last_window", "no_casefold", "nul_stop", "no_hex", "no_wif",
              "no_nested", "no_verbatim"] + [f"drop_marker:{i}" for i in range(len(MARKERS))])
CAL_PAIRS, CAL_EXPECT, CAL_TOL = 10000, 27998.046875, 1449   # 2867/1024 per pair; 5 sd with a 3x variance allowance


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
    """The six reads, in order: fwd, rev, bitrev (byte j = m(Z[L-1-j])), then each complemented (255 - b)."""
    br = MIRROR[z[::-1]]
    out = [("fwd", z), ("rev", z[::-1]), ("bitrev", br), ("~fwd", ~z), ("~rev", ~z[::-1]), ("~bitrev", ~br)]
    if "no_rev_read" in mut:
        out = [r for r in out if r[0].lstrip("~") != "rev"]
    if "no_bitrev_read" in mut:
        out = [r for r in out if r[0].lstrip("~") != "bitrev"]
    if "no_not_read" in mut:
        out = [r for r in out if not r[0].startswith("~")]
    return out


# ---------------------------------------------------------------------------------------------------------- detectors
def target_map(extra=None):
    """hash160 bytes -> address: the three real targets in table order, then any test targets."""
    t = {bytes.fromhex(h): a for a, h in TARGETS.items()}
    for h in (extra or []):
        t.setdefault(h, p2pkh(h))
    return t


def scan(a, b, targets, only=None, mut=frozenset(), markers=None, detectors=DETECTORS):
    """Scan the whole family (or one output) of the envelopes a, b. The scan always runs to completion.

    Returns the manifest and its hash, the coverage record (PREREG order), the detector digest, the canonical hit
    list [(label, read, detector, offset, item)] and the invalid raw windows."""
    mlist = MARKERS if markers is None else markers
    keep = [(i, m) for i, m in enumerate(mlist) if f"drop_marker:{i}" not in mut]
    cf = "no_casefold" not in mut
    pats = [(i, m, m.lower() if cf else m) for i, m in keep]
    tlist = list(targets.items())                       # (hash160, address) in table order, test targets last
    tindex = {h: n for n, (h, _) in enumerate(tlist)}
    real_addr = list(TARGETS)
    cov = dict.fromkeys(COVERAGE_KEYS, 0)
    manifest, hits, invalid = [], [], []
    dig = hashlib.sha256()

    def keyhits(label, rname, det, off, pair, extra=""):
        for form, h in (("compressed", pair[0]), ("uncompressed", pair[1])):
            if f"no_{form}" in mut or h not in targets:
                continue
            hits.append((label, rname, det, off, f"{form}:{targets[h]}{extra}",
                         (0 if form == "compressed" else 1, tindex[h])))

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
                for mi, m, pm in pats:
                    last = L - len(m) - (1 if "no_last_marker_pos" in mut else 0)
                    cov["a_positions"] += max(0, last + 1)
                    if m == b"HALF":
                        cov["a_half_positions"] += max(0, last + 1)
                    k = low.find(pm)
                    while 0 <= k <= last:
                        hits.append((label, rname, "a", k, m.decode(), (mi,)))
                        k = low.find(pm, k + 1)
            if "b" in detectors:
                for off in range(max(0, L - 31 - (1 if "no_last_window" in mut else 0))):
                    w = r[off:off + 32]
                    cov["b_windows"] += 1
                    k = int.from_bytes(w, "big")
                    if 1 <= k < N:
                        pair = h160_pair(w)
                        dig.update(pair[0] + pair[1])
                        keyhits(label, rname, "b", off, pair)
                    else:
                        cov["b_invalid"] += 1
                        invalid.append((label, rname, off))
                        dig.update(bytes(40))
            if "b_hex" in detectors and "no_hex" not in mut:
                for mt in HEX_RUN.finditer(r):
                    for j in range(mt.start(), mt.end() - 63):
                        cov["b_hex_windows"] += 1
                        k = int(r[j:j + 64], 16)
                        if 1 <= k < N:
                            keyhits(label, rname, "b_hex", j, h160_pair(k.to_bytes(32, "big")))
                        else:
                            cov["b_hex_invalid"] += 1
            if "b_wif" in detectors and "no_wif" not in mut:
                for mt in B58_RUN.finditer(r):
                    for j in range(mt.start(), mt.end()):
                        n = {ord("5"): 51, ord("K"): 52, ord("L"): 52}.get(r[j])
                        if n is None or j + n > mt.end():
                            continue
                        cov["b_wif_windows"] += 1
                        pl = b58decode_check(r[j:j + n].decode(), 37 if n == 51 else 38)
                        if pl is None or pl[0] != 0x80 or (n == 52 and pl[33] != 1):
                            continue
                        cov["b_wif_decoded"] += 1
                        k = int.from_bytes(pl[1:33], "big")
                        if 1 <= k < N:
                            keyhits(label, rname, "b_wif", j, h160_pair(k.to_bytes(32, "big")), f":{n}")
            if "c" in detectors:
                cov["c_salted_positions"] += max(0, L - 7)
                cov["c_b64_positions"] += max(0, L - 9)
                if "no_nested" not in mut:
                    for pi, pat in enumerate(NESTED):
                        k = r.find(pat)
                        while k >= 0:
                            hits.append((label, rname, "c", k, pat.decode(), (pi,)))
                            k = r.find(pat, k + 1)
            if "d" in detectors:
                cov["d_h160_windows"] += max(0, L - 19)
                for h, addr in tlist:
                    ab = addr.encode()
                    if addr in real_addr:
                        key = ("d_addr_positions_prize", "d_addr_positions_17ucy1",
                               "d_addr_positions_1NULY7")[real_addr.index(addr)]
                        cov[key] += max(0, L - len(ab) + 1)
                    if "no_verbatim" in mut:
                        continue
                    for kind_i, (pat, kind) in enumerate(((h, "hash160"), (ab, "address"))):
                        k = r.find(pat)
                        while k >= 0:
                            hits.append((label, rname, "d", k, f"{kind}:{addr}", (kind_i, tindex[h])))
                            k = r.find(pat, k + 1)
    oi = {lab: n for n, lab in enumerate(LABELS)}
    ri = {nm: n for n, nm in enumerate(READS)}
    di = {nm: n for n, nm in enumerate(DETECTORS)}
    hits.sort(key=lambda h: (oi[h[0]], ri[h[1]], di[h[2]], h[3], h[5]))
    text = "".join(f"{lab} {hx}\n" for lab, hx in manifest)
    return {"manifest": manifest, "manifest_sha256": sha(text.encode()), "coverage": cov,
            "detector_digest": dig.hexdigest(), "hits": [h[:5] for h in hits], "invalid": invalid}


def coverage_ok(cov):
    """Mismatches against the pinned coverage (data-dependent entries are not pinned)."""
    return {k: cov.get(k) for k, v in PINNED_COVERAGE.items() if v is not None and cov.get(k) != v}


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
    i = hx.find("04f4d1bb")                        # first occurrence; all three in the tx are equal
    assert i >= 0 and hash160(bytes.fromhex(hx[i:i + 130])).hex() == TARGETS["1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"]
    hc, hu = h160_pair((1).to_bytes(32, "big"))
    assert p2pkh(hc) == "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH" and p2pkh(hu) == "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"
    for L, kat in TURN_KAT.items():
        s = np.arange(L, dtype=np.uint8)
        for g, want in kat.items():
            assert sha(turn(g, s).tobytes()) == want, f"turn {g} L={L} fails its known answer"
    assert len(MARKERS) == 17 and len(LABELS) == 88 and len(READS) == 6
    return True


# ---------------------------------------------------------------------------------------------------------- controls
BASE_READ = {"fwd": lambda z: z, "rev": lambda z: z[::-1], "bitrev": lambda z: MIRROR[z[::-1]]}


def read_of(rname, z):
    return ~BASE_READ[rname[1:]](z) if rname.startswith("~") else BASE_READ[rname](z)


def read_preimage(rname, p):
    """The output whose read `rname` is p (every base read is an involution)."""
    return BASE_READ[rname[1:]](~p) if rname.startswith("~") else BASE_READ[rname](p)


def case_pattern(m, c):
    """c mod 3: 0 upper, 1 lower, 2 alternating over letters only (even lower, odd upper; separators kept)."""
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


def build_pair(label, rname, base, suffix, plants_fn):
    """A synthetic (A, B) whose output `label`, read `rname`, is a planted read P (PREREG control 1).

    Tags: <base>/A/<suffix>, <base>/P/<suffix>, <base>/S/<suffix>. In the R1 id cells the output's bytes 0-7 are fixed
    to op(Salted__, Salted__), P carries their read outside the free region, and the synthetic B begins with Salted__.
    plants_fn(P, f0, f1) writes the plants into the bytearray P inside [f0, f1) and returns what it planted."""
    rep, o, cell = label.split("/")
    L = 96 if rep == "R1" else 80
    a = HDR + stream(f"{base}/A/{suffix}", 88)
    X = np.frombuffer(a if rep == "R1" else a[16:], dtype=np.uint8)
    P = bytearray(stream(f"{base}/P/{suffix}", L))
    f0, f1 = 0, L
    if rep == "R1" and cell == "id":
        hdr = np.frombuffer(HDR, dtype=np.uint8)
        zt = np.zeros(L, dtype=np.uint8)
        zt[:8] = op(o, hdr, hdr)
        pt = read_of(rname, zt).tobytes()
        if rname in ("fwd", "~fwd"):
            P[0:8], f0 = pt[0:8], 8
        else:
            P[L - 8:L], f1 = pt[L - 8:L], L - 8
    planted = plants_fn(P, f0, f1)
    Z = read_preimage(rname, np.frombuffer(bytes(P), dtype=np.uint8))
    if cell == "id":
        Y = inv(o, X, Z)
    else:
        d, g = cell.split(".")
        Y = turn(g, inv(o, X, Z)) if d == "B" else inv(o, turn(g, X), Z)
    b = Y.tobytes() if rep == "R1" else HDR + stream(f"{base}/S/{suffix}", 8) + Y.tobytes()
    if rep == "R1" and cell == "id":
        assert b[:8] == HDR, "synthetic B of an R1 id cell must carry the Salted__ header"
    return a, b, planted


def control1(c, mut=frozenset()):
    """Per-cell positive control c = 6 x output index + read index (0..527): a marker and a key in one read."""
    label, rname = LABELS[c // 6], READS[c % 6]
    M = MARKERS[c % 17]
    Mc = case_pattern(M, c)
    t = int.from_bytes(stream(f"twodoor/ctl/k/{c}", 32), "big") % (N - 1) + 1
    tb = t.to_bytes(32, "big")

    def plants(P, f0, f1):
        om, ok = (f0, f1 - 32) if c % 2 == 0 else (f1 - len(M), f0)
        P[om:om + len(M)] = Mc
        P[ok:ok + 32] = tb
        return om, ok

    a, b, (om, ok) = build_pair(label, rname, "twodoor/ctl", str(c), plants)
    hc, hu = h160_pair(tb)
    form, th = ("compressed", hc) if c % 4 in (0, 1) else ("uncompressed", hu)
    tm = target_map([th])
    res = scan(a, b, tm, only=label, mut=mut)
    return ((label, rname, "a", om, M.decode()) in res["hits"]
            and (label, rname, "b", ok, f"{form}:{tm[th]}") in res["hits"]), res["hits"]


PLANT_DET = ("b_hex", "b_wif", "b_wif", "c", "c", "d", "d")


def control2(p, t, mut=frozenset()):
    """Per-detector control: plant type t (hex, WIF-c, WIF-u, Salted__, U2FsdGVkX1, hash160, address) for pair p."""
    rep, o = REPS[p // 4][0], OPS[p % 4]
    label, rname = f"{rep}/{o}/{CELLS[(p + t) % 11]}", READS[(p + t) % 6]
    k = int.from_bytes(stream(f"twodoor/ctl2/k/{p}/{t}", 32), "big") % (N - 1) + 1
    hc, hu = h160_pair(k.to_bytes(32, "big"))
    plant = [format(k, "064x").encode(), wif(k, True).encode(), wif(k, False).encode(), NESTED[0], NESTED[1],
             hc, p2pkh(hc).encode()][t]

    def plants(P, f0, f1):
        off = f0 if (p + t) % 2 == 0 else f1 - len(plant)
        P[off:off + len(plant)] = plant
        return off

    a, b, off = build_pair(label, rname, "twodoor/ctl2", f"{p}/{t}", plants)
    res = scan(a, b, target_map([hc, hu]), only=label, mut=mut)
    want = {3: NESTED[0].decode(), 4: NESTED[1].decode(), 5: "hash160:" + p2pkh(hc), 6: "address:" + p2pkh(hc)}
    return any(h[:4] == (label, rname, PLANT_DET[t], off) and (t not in want or h[4] == want[t])
               for h in res["hits"]), res["hits"]


NEAR = ("HALG", "HAL@end", "LF@0+HA@end", "YIN.YANG", "YOU  WON", "k=0", "k=n", "k=2^256-1")


def control_n2(j):
    """Near miss j (0..7) in R1/xor/B.rev, fwd read, real targets: nothing may be reported."""
    label, rname = "R1/xor/B.rev", "fwd"

    def plants(P, f0, f1):
        L = len(P)
        if j == 1:
            P[L - 3:L] = b"HAL"
        elif j == 2:
            P[0:2], P[L - 2:L] = b"LF", b"HA"
        elif j >= 5:
            P[0:32] = (0, N, 2 ** 256 - 1)[j - 5].to_bytes(32, "big")
        else:
            s = NEAR[j].encode()
            P[0:len(s)] = s

    a, b, _ = build_pair(label, rname, "twodoor/neg2", str(j), plants)
    assert a[:8] == HDR and len(a) == len(b) == 96
    res = scan(a, b, target_map(), only=label)
    ok = not res["hits"]
    if j >= 5:
        ok = ok and (label, "fwd", 0) in res["invalid"]
    return ok, res["hits"]


def run_controls(mut=frozenset()):
    fails = [f"ctl1:{c}" for c in range(528) if not control1(c, mut)[0]]
    fails += [f"ctl2:{p}/{t}" for p in range(8) for t in range(7) if not control2(p, t, mut)[0]]
    return fails


def negative_n1():
    return scan(HDR + stream("twodoor/neg/A", 88), HDR + stream("twodoor/neg/B", 88), target_map())


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
        for sw in MUTATIONS:
            table.append({"switch": sw, "failing_controls": len(run_controls(frozenset([sw])))})
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
    return f"{h[0]} {h[1]} {h[2]}@{h[3]} {h[4]}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--peer-n1", metavar="DIGEST",
                    help="with --run: the second implementation's N1 detector digest; the real inputs are combined "
                         "only if ours equals it (PREREG, Execution: Order)")
    args = ap.parse_args()
    if args.run and not args.peer_n1:
        sys.exit("refusing --run without --peer-n1: the implementations must agree on N1 before the real inputs")
    t0 = time.time()
    rec = {"campaign": 55, "prereg": prereg_state(), "script_sha256": sha(open(__file__, "rb").read())}
    if args.run and not (rec["prereg"]["clean"] and rec["prereg"]["frozen"] and rec["prereg"]["last_commit"]):
        sys.exit(f"refusing --run: the PREREG must be committed, clean and frozen ({rec['prereg']})")

    rec["startup_assertions"] = startup_assertions()
    load_inputs()   # hashes only; nothing is combined before every check passes
    rec["inputs"] = {"files": FILE_SHA, "A_sha256": A_SHA, "B_sha256": B_SHA, "A_salt": A_SALT, "B_salt": B_SALT}
    print("[55] startup assertions (inputs, targets, prize key, k=1, turn known answers): pass", flush=True)

    fails = run_controls()
    rec["controls"] = {"ctl1": {"n": 528, "failed": [f for f in fails if f.startswith("ctl1")]},
                       "ctl2": {"n": 56, "failed": [f for f in fails if f.startswith("ctl2")]}}
    print(f"[55] controls 1-2: {584 - len(fails)}/584 pass", flush=True)
    n2 = [control_n2(j) for j in range(len(NEAR))]
    rec["controls"]["n2"] = {"n": len(NEAR), "failed": [NEAR[j] for j, (ok, _) in enumerate(n2) if not ok]}
    n1 = negative_n1()
    bad = coverage_ok(n1["coverage"])
    rec["controls"]["n1"] = {"manifest_sha256": n1["manifest_sha256"], "manifest_as_pinned": n1["manifest_sha256"] == N1_MANIFEST,
                             "detector_digest": n1["detector_digest"], "coverage": [n1["coverage"][k] for k in COVERAGE_KEYS],
                             "coverage_mismatch": bad, "hits": [fmt_hit(h) for h in n1["hits"]]}
    print(f"[55] N1: manifest {'as pinned' if n1['manifest_sha256'] == N1_MANIFEST else 'NOT AS PINNED'}, digest "
          f"{n1['detector_digest']}, hits {len(n1['hits'])}, coverage mismatches {bad or 'none'}; "
          f"N2 near misses failed: {rec['controls']['n2']['failed'] or 'none'}", flush=True)
    ctl_ok = (not fails and not rec["controls"]["n2"]["failed"] and not n1["hits"] and not bad
              and n1["manifest_sha256"] == N1_MANIFEST)

    table = mutation_check()
    mut_ok = all(r["failing_controls"] > 0 for r in table)
    rec["mutation"] = {"table": table, "pass": mut_ok}
    print(f"[55] mutation check: {sum(r['failing_controls'] > 0 for r in table)}/{len(table)} switches caught",
          flush=True)

    cal = calibration()
    rec["calibration"] = cal
    print(f"[55] calibration: observed {cal['observed']} vs expected {CAL_EXPECT} +/- {CAL_TOL}: "
          f"{'pass' if cal['pass'] else 'FAIL'} (batch sd {cal['batch_sd']})", flush=True)

    ok = ctl_ok and mut_ok and cal["pass"]
    rec["checks_pass"] = ok
    if args.run:
        rec["controls"]["n1"]["peer_digest"] = args.peer_n1
        rec["controls"]["n1"]["peer_agrees"] = args.peer_n1 == n1["detector_digest"]
        print(f"[55] N1 digest vs the second implementation: "
              f"{'agree' if rec['controls']['n1']['peer_agrees'] else 'DISAGREE'}", flush=True)
        ok = ok and rec["controls"]["n1"]["peer_agrees"]
    if not args.run:
        print(f"[55] selftest {'PASS' if ok else 'FAIL'} in {time.time() - t0:.0f}s")
        return 0 if ok else 1
    if not ok:
        rec["verdict"] = "VOID"
        with open(OUT, "w") as f:
            json.dump(rec, f, indent=1)
        sys.exit("[55] VOID: a check failed; the real inputs were not combined")

    a, b = load_inputs()
    real = scan(a, b, target_map())        # always runs to completion; every event is listed
    bad = coverage_ok(real["coverage"])
    verdict = "VOID" if bad else ("HIT" if real["hits"] else "NULL")
    rec["real"] = {"manifest": [{"label": lab, "sha256": hx} for lab, hx in real["manifest"]],
                   "manifest_sha256": real["manifest_sha256"],
                   "coverage": dict(zip(COVERAGE_KEYS, [real["coverage"][k] for k in COVERAGE_KEYS])),
                   "coverage_mismatch": bad, "detector_digest": real["detector_digest"],
                   "hits": [{"label": h[0], "read": h[1], "detector": h[2], "offset": h[3], "item": h[4]}
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
