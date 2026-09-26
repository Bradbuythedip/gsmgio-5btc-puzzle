#!/usr/bin/env python3
"""
GSMG Offline Solver / Evidence Harness
======================================

A conservative, reproducible offline harness for the public GSMG 5 BTC puzzle.
It DOES NOT generate passwords, brute-force vocabularies, widen KDF families, or
invent serialization rules. It only tests explicit material supplied by you.

Python: 3.9+
AES backend: tries, in order
  1) pycryptodome (Crypto.Cipher.AES)
  2) cryptography
  3) local `openssl` executable

Main commands
-------------
  doctor       Check local crypto/backend support.
  audit        Verify pinned GSMG ciphertext bytes in a local repo checkout.
  selftest     audit + NIST AES + secp256k1 + three solved-stage controls.
  test         Test exactly one candidate against the frozen endgame surface.
  gate         Provenance-aware one-shot intake JSON + parked-corpus refusal.
  keytest      Test one explicit raw 32-byte AES/scalar key structurally.
  digest       SHA-256 exact text/file/hex bytes; no transformations.
  components   Inspect params/code/text as separate typed objects; NO join.
  opreturn     Exact 32-byte OP_RETURN vs exact/reversed nonce x/y coordinates.
  txscan       Inspect a saved Bitcoin transaction JSON for known addresses and
               OP_RETURN payloads; no network access.
  report       Summarize this harness's local JSONL attempt log.

Examples
--------
  python gsmg_offline_solver.py doctor
  python gsmg_offline_solver.py audit --repo /path/to/gsmgio-5btc-puzzle
  python gsmg_offline_solver.py selftest --repo /path/to/gsmgio-5btc-puzzle

  python gsmg_offline_solver.py test --repo /path/to/repo \
      --candidate 'EXACT STRING' \
      --source-note 'creator message 12345, 2026-09-26'

  python gsmg_offline_solver.py test --repo /path/to/repo \
      --candidate-file candidate.txt --source-note 'verbatim saved artifact'

  python gsmg_offline_solver.py gate --repo /path/to/repo intake.json

  python gsmg_offline_solver.py keytest --repo /path/to/repo --key-hex 00...01

  python gsmg_offline_solver.py digest --text 'GSMGIO5BTCPUZZLECHALLENGE...'
  python gsmg_offline_solver.py digest --file exact_package.bin

  python gsmg_offline_solver.py components \
      --params params.bin --code code.bin --text prose.bin --package exact.bin

  python gsmg_offline_solver.py opreturn \
      --payload 64_HEX_CHARS --nonce-json nonce_points.json

  python gsmg_offline_solver.py txscan transaction.json

Exit codes
----------
  0   success / null result / informational command
  2   refused input / duplicate candidate / bad provenance
  3   self-test/audit failure; do not trust null results
  10  strong cryptographic hit

Frozen policy
-------------
Default candidate test surface is deliberately fixed:

  candidate bytes -> {raw, lowercase SHA256 hex ASCII}
                  -> EVP_BytesToKey {MD5, SHA256}, AES-256-CBC
                  -> {miniA, miniAB, inner96/P32T, cosmic}

plus:

  SHA256(candidate bytes) as secp256k1 scalar
  candidate itself as scalar iff it is exactly 64 ASCII hex chars

No PBKDF2, AES-128/192, SHA1, sliding windows, n-grams, subset XORs, arbitrary
concatenations, or generated vocabulary are included here. Those are separate
hypotheses and should be separately preregistered if ever reopened.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import shutil
import string
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "2026-09-26.3"
# .3: RIPEMD-160 falls back to pycryptodome when hashlib lacks it (some OpenSSL 3 builds).
# .2 (repo validation, ledger tick 91): phase-3 control password restored to the verified 227-char
#    string (the 7th FEN rank "1P2P2P/" was missing, so selftest always failed); key-material check
#    runs on every raw decrypt again, not only PKCS#7-valid ones (tick 83 / campaign 51, as the
#    tick-86 version did); txscan exits 10 only on a nonce match, not for mentioning a known address.

# ---------------------------------------------------------------------------
# Canonical puzzle constants
# ---------------------------------------------------------------------------

PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BETTER_HALF = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
KNOWN_ADDRESSES = {PRIZE: "prize", BETTER_HALF: "better_half"}

# These are the byte-pinned envelopes, not candidate passwords.
BASELINES = {
    "miniAB": {
        "envelope_len": 96,
        "ct_len": 80,
        "salt": "3ab585348552415d",
        "sha256": "9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258",
        "last_ct": "ef756397ea74234a97a95f01ae37f8c9",
    },
    "inner96": {
        "envelope_len": 96,
        "ct_len": 80,
        "salt": "b45a5e3d827593ca",
        "sha256": "291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9",
        "last_ct": "5334de08884878aaed7c99d0b4340bf8",
    },
    "cosmic": {
        "envelope_len": 1344,
        "ct_len": 1328,
        "salt": "2d3f6fe06dc950e6",
        "sha256": "b18950551a4dd0cb8a9378f0906ba18c03a15f0ee83eb98c6bc90165c5f79805",
        "last_ct": "5bbf983669ed922eb12dff1dcc3f6fc6",
    },
}

# Positive controls: exact human answers that open already-solved blobs when the
# lowercase SHA256-hex ASCII form is fed to EVP_BytesToKey(SHA256), AES-256-CBC.
SOLVED_CONTROLS = [
    (
        "phase2-assets/phase2_aes.txt",
        "causality",
        "phase2",
    ),
    (
        "phase2-assets/phase3_aes.txt",
        "causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1",
        "phase3",
    ),
    (
        "phase3-assets/phase3.2-aes.txt",
        "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
        "phase3.2",
    ),
]

# P32T/inner96 canonical IV-independent final-block readings.
P32T_PRIMARY_P5 = bytes([0x0A]) + bytes([0x0F]) * 15   # 64 hex chars + LF, pad15
P32T_SECONDARY_P5 = bytes([0x10]) * 16                # 64 raw bytes, pad16

MAGIC = (
    b"U2Fsd", b"Salted__", b"-----BEGIN", b"http", b"https", b"gsmg", b"GSMG",
    b"xprv", b"bc1q", b"1GSMG",
)
PRINTABLE = set(string.printable.encode("ascii"))

# ---------------------------------------------------------------------------
# AES backend abstraction
# ---------------------------------------------------------------------------

_AES_BACKEND = None
_AES_IMPORT_ERROR = None

try:
    from Crypto.Cipher import AES as _PyCryptoAES  # type: ignore
    _AES_BACKEND = "pycryptodome"
except Exception as e:  # pragma: no cover - environment dependent
    _AES_IMPORT_ERROR = repr(e)
    _PyCryptoAES = None

if _AES_BACKEND is None:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher as _Cipher  # type: ignore
        from cryptography.hazmat.primitives.ciphers import algorithms as _algorithms  # type: ignore
        from cryptography.hazmat.primitives.ciphers import modes as _modes  # type: ignore
        _AES_BACKEND = "cryptography"
    except Exception as e:  # pragma: no cover
        _AES_IMPORT_ERROR = repr(e)
        _Cipher = _algorithms = _modes = None

if _AES_BACKEND is None and shutil.which("openssl"):
    _AES_BACKEND = "openssl"


def aes_backend() -> str:
    if _AES_BACKEND is None:
        raise RuntimeError(
            "No AES backend available. Install pycryptodome or cryptography, or make "
            "the openssl executable available in PATH. Last import error: " + str(_AES_IMPORT_ERROR)
        )
    return _AES_BACKEND


def aes_cbc_decrypt(key: bytes, iv: bytes, ct: bytes) -> bytes:
    if len(key) != 32 or len(iv) != 16 or len(ct) % 16:
        raise ValueError("AES-256-CBC requires key=32B, iv=16B, ct multiple of 16B")
    backend = aes_backend()
    if backend == "pycryptodome":
        return _PyCryptoAES.new(key, _PyCryptoAES.MODE_CBC, iv).decrypt(ct)
    if backend == "cryptography":
        dec = _Cipher(_algorithms.AES(key), _modes.CBC(iv)).decryptor()
        return dec.update(ct) + dec.finalize()
    proc = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-d", "-K", key.hex(), "-iv", iv.hex(), "-nopad"],
        input=ct,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("openssl AES-CBC failed: " + proc.stderr.decode("utf-8", "replace"))
    return proc.stdout


def aes_ecb_decrypt_block(key: bytes, block: bytes) -> bytes:
    if len(key) != 32 or len(block) != 16:
        raise ValueError("AES-256-ECB block decrypt requires key=32B, block=16B")
    backend = aes_backend()
    if backend == "pycryptodome":
        return _PyCryptoAES.new(key, _PyCryptoAES.MODE_ECB).decrypt(block)
    if backend == "cryptography":
        dec = _Cipher(_algorithms.AES(key), _modes.ECB()).decryptor()
        return dec.update(block) + dec.finalize()
    proc = subprocess.run(
        ["openssl", "enc", "-aes-256-ecb", "-d", "-K", key.hex(), "-nopad", "-nosalt"],
        input=block,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("openssl AES-ECB failed: " + proc.stderr.decode("utf-8", "replace"))
    return proc.stdout

# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def xor_bytes(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise ValueError("xor length mismatch")
    return bytes(x ^ y for x, y in zip(a, b))


def entropy(b: bytes) -> float:
    if not b:
        return 0.0
    counts = [0] * 256
    for x in b:
        counts[x] += 1
    n = len(b)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    return sum(x in PRINTABLE for x in b) / len(b)


def pkcs7_info(pt: bytes) -> Optional[Dict[str, Any]]:
    if not pt:
        return None
    p = pt[-1]
    if not 1 <= p <= 16 or len(pt) < p:
        return None
    if pt[-p:] != bytes([p]) * p:
        return None
    body = pt[:-p]
    pr = printable_ratio(body)
    phr = printable_ratio(body[:64])
    magic = any(body.startswith(m) for m in MAGIC)
    strong = (p >= 4) or magic or phr >= 0.85 or pr >= 0.90
    return {
        "pad": p,
        "body": body,
        "printable": round(pr, 4),
        "printable_head": round(phr, 4),
        "magic": magic,
        "strong": strong,
        "entropy": round(entropy(body), 4),
    }


def b64_file(path: Path) -> bytes:
    txt = path.read_text(encoding="ascii", errors="strict")
    compact = "".join(txt.split())
    return base64.b64decode(compact, validate=True)


def require_salted(raw: bytes, label: str) -> Tuple[bytes, bytes]:
    if raw[:8] != b"Salted__" or len(raw) < 32 or len(raw[16:]) % 16:
        raise ValueError(f"{label}: not a valid OpenSSL Salted__ AES envelope")
    return raw[8:16], raw[16:]


def evp_bytes_to_key(password: bytes, salt: Optional[bytes], digest_name: str,
                     key_len: int = 32, iv_len: int = 16) -> Tuple[bytes, bytes]:
    hfun = getattr(hashlib, digest_name)
    out = b""
    prev = b""
    saltb = salt or b""
    while len(out) < key_len + iv_len:
        prev = hfun(prev + password + saltb).digest()
        out += prev
    return out[:key_len], out[key_len:key_len + iv_len]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def preview_bytes(b: bytes, n: int = 120) -> str:
    x = b[:n]
    try:
        s = x.decode("utf-8")
        return repr(s)
    except UnicodeDecodeError:
        return x.hex() + ("..." if len(b) > n else "")


def read_candidate(args) -> bytes:
    have = int(args.candidate is not None) + int(args.candidate_file is not None)
    if have != 1:
        raise ValueError("provide exactly one of --candidate or --candidate-file")
    if args.candidate is not None:
        return args.candidate.encode("utf-8")
    return Path(args.candidate_file).read_bytes()

# ---------------------------------------------------------------------------
# secp256k1 / P2PKH, dependency-free
# ---------------------------------------------------------------------------

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _inv(a: int, m: int = P) -> int:
    return pow(a, m - 2, m)


def _point_add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        lam = (3 * x1 * x1) * _inv(2 * y1) % P
    else:
        lam = (y2 - y1) * _inv(x2 - x1) % P
    x3 = (lam * lam - x1 - x2) % P
    return x3, (lam * (x1 - x3) - y1) % P


def point_mul(k: int, point=(GX, GY)):
    if not 1 <= k < N:
        return None
    r = None
    q = point
    while k:
        if k & 1:
            r = _point_add(r, q)
        q = _point_add(q, q)
        k >>= 1
    return r


def b58encode(b: bytes) -> str:
    n = int.from_bytes(b, "big")
    s = ""
    while n:
        n, r = divmod(n, 58)
        s = B58[r] + s
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + s


def ripemd160(b: bytes) -> bytes:
    """RIPEMD-160 from hashlib, or from pycryptodome where the Python/OpenSSL 3 build lacks it."""
    try:
        return hashlib.new("ripemd160", b).digest()
    except ValueError:
        try:
            from Crypto.Hash import RIPEMD160  # type: ignore
        except ImportError as e:
            raise RuntimeError("RIPEMD160 unavailable: this Python/OpenSSL build lacks it; "
                               "`pip install pycryptodome` provides a fallback") from e
        return RIPEMD160.new(b).digest()


def ripemd160_backend() -> str:
    try:
        hashlib.new("ripemd160", b"")
        return "hashlib"
    except ValueError:
        try:
            from Crypto.Hash import RIPEMD160  # type: ignore  # noqa: F401
            return "pycryptodome fallback"
        except ImportError:
            return "MISSING (pip install pycryptodome)"


def hash160(b: bytes) -> bytes:
    return ripemd160(hashlib.sha256(b).digest())


def p2pkh(pub: bytes) -> str:
    payload = b"\x00" + hash160(pub)
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return b58encode(payload + chk)


def scalar_addresses(k: int) -> Tuple[Optional[str], Optional[str]]:
    pt = point_mul(k)
    if pt is None:
        return None, None
    x, y = pt
    xb = x.to_bytes(32, "big")
    comp = bytes([2 + (y & 1)]) + xb
    uncomp = b"\x04" + xb + y.to_bytes(32, "big")
    return p2pkh(comp), p2pkh(uncomp)


def scalar_report(label: str, k: int) -> Dict[str, Any]:
    c, u = scalar_addresses(k)
    matches = []
    for addr, typ in KNOWN_ADDRESSES.items():
        if c == addr:
            matches.append(f"{typ}:compressed")
        if u == addr:
            matches.append(f"{typ}:uncompressed")
    return {
        "label": label,
        "scalar_hex": f"{k:064x}" if 0 <= k < (1 << 256) else hex(k),
        "valid_scalar": 1 <= k < N,
        "compressed": c,
        "uncompressed": u,
        "matches": matches,
    }


def secp_selftest() -> bool:
    vectors = [
        (1, "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"),
        (2, "1cMh228HTCiwS8ZsaakH8A8wze1JR5ZsP", "1LagHJk2FyCV2VzrNHVqg3gYG4TSYwDV4m"),
    ]
    ok = True
    for k, ec, eu in vectors:
        c, u = scalar_addresses(k)
        good = (c, u) == (ec, eu)
        print(("OK  " if good else "FAIL"), "secp", k, c, u)
        ok &= good
    return ok

# ---------------------------------------------------------------------------
# Repo targets / byte audit
# ---------------------------------------------------------------------------


def load_targets(repo: Path) -> Dict[str, Dict[str, bytes]]:
    mat = repo / "neo" / "materials"
    a = b64_file(mat / "miniA.b64")
    b = b64_file(mat / "miniB.b64")
    inner = b64_file(mat / "inner96.b64")
    cosmic = b64_file(mat / "cosmic_duality_b64.txt")

    sa, cta = require_salted(a, "miniA")
    sab, ctab = require_salted(a + b, "miniAB")
    si, cti = require_salted(inner, "inner96")
    sc, ctc = require_salted(cosmic, "cosmic")

    return {
        "miniA": {"envelope": a, "salt": sa, "ct": cta},
        "miniAB": {"envelope": a + b, "salt": sab, "ct": ctab},
        "inner96": {"envelope": inner, "salt": si, "ct": cti},
        "cosmic": {"envelope": cosmic, "salt": sc, "ct": ctc},
        "_miniB": {"envelope": b, "salt": b"", "ct": b},
    }


def audit_repo(repo: Path, quiet: bool = False) -> bool:
    ok = True
    try:
        t = load_targets(repo)
    except Exception as e:
        print("FAIL load targets:", e)
        return False

    a = t["miniA"]["envelope"]
    b = t["_miniB"]["envelope"]
    local_checks = [
        ("miniA length", len(a) == 48, len(a)),
        ("miniB length", len(b) == 48, len(b)),
        ("miniA header", a.startswith(b"Salted__"), a[:8]),
        ("miniB continuation-no-header", not b.startswith(b"Salted__"), b[:8].hex()),
    ]
    for label, good, got in local_checks:
        ok &= good
        if not quiet:
            print(("OK  " if good else "FAIL"), label, got)

    for name, baseline in BASELINES.items():
        x = t[name]
        env = x["envelope"]
        checks = {
            "envelope_len": len(env),
            "ct_len": len(x["ct"]),
            "salt": x["salt"].hex(),
            "sha256": sha256hex(env),
            "last_ct": x["ct"][-16:].hex(),
        }
        for field, got in checks.items():
            want = baseline[field]
            good = got == want
            ok &= good
            if not quiet:
                print(("OK  " if good else "FAIL"), f"{name}.{field}", got)

    # Issue #108 hygiene: the committed combined Base64 must already contain J / s.
    combined_b64 = base64.b64encode(t["miniAB"]["envelope"]).decode("ascii")
    if len(combined_b64) > 51:
        checks = [(18, "J"), (51, "s")]
        for idx, want in checks:
            got = combined_b64[idx]
            good = got == want
            ok &= good
            if not quiet:
                print(("OK  " if good else "FAIL"), f"miniAB base64[{idx}]", repr(got))
    else:
        print("FAIL miniAB base64 unexpectedly short")
        ok = False

    if not quiet:
        print("audit passed:", ok)
    return ok

# ---------------------------------------------------------------------------
# P32T structure
# ---------------------------------------------------------------------------


def p32t_last_plain_block(aes_key: bytes, inner_ct: bytes) -> bytes:
    if len(inner_ct) != 80:
        raise ValueError("inner96 ciphertext must be 80 bytes")
    c4 = inner_ct[48:64]
    c5 = inner_ct[64:80]
    return xor_bytes(aes_ecb_decrypt_block(aes_key, c5), c4)


def p32t_reading(aes_key: bytes, inner_ct: bytes) -> Dict[str, Any]:
    p5 = p32t_last_plain_block(aes_key, inner_ct)
    p = p5[-1]
    valid_pad = 1 <= p <= 16 and p5[-p:] == bytes([p]) * p
    reading = None
    if p5 == P32T_PRIMARY_P5:
        reading = "primary:64hex+LF"
    elif p5 == P32T_SECONDARY_P5:
        reading = "secondary:two-raw-32B"
    elif valid_pad:
        reading = f"weak:validpad{p}"
    return {"p5": p5.hex(), "reading": reading, "valid_pad": valid_pad, "pad": p if valid_pad else None}

# ---------------------------------------------------------------------------
# Candidate / plaintext structural checks
# ---------------------------------------------------------------------------


def key_material_matches(body: bytes) -> List[Dict[str, Any]]:
    """Only structurally explicit locations, never sliding windows.

    - first 32 bytes
    - second 32 bytes
    - literal standalone 64-hex ASCII tokens

    We report these only when they map to a known GSMG address. This avoids turning
    random plaintext into a giant private-key candidate generator.
    """
    out = []
    seen = set()

    def consider(label: str, raw32: bytes):
        if len(raw32) != 32:
            return
        k = int.from_bytes(raw32, "big")
        rep = scalar_report(label, k)
        if rep["matches"]:
            sig = (rep["scalar_hex"], tuple(rep["matches"]))
            if sig not in seen:
                seen.add(sig)
                out.append(rep)

    if len(body) >= 32:
        consider("plaintext[0:32]", body[:32])
    if len(body) >= 64:
        consider("plaintext[32:64]", body[32:64])

    for m in re.finditer(rb"(?<![0-9A-Fa-f])([0-9A-Fa-f]{64})(?![0-9A-Fa-f])", body):
        h = m.group(1).decode("ascii")
        k = int(h, 16)
        rep = scalar_report(f"literal64hex@{m.start(1)}", k)
        if rep["matches"]:
            sig = (rep["scalar_hex"], tuple(rep["matches"]))
            if sig not in seen:
                seen.add(sig)
                out.append(rep)
    return out


def candidate_scalar_checks(candidate: bytes) -> List[Dict[str, Any]]:
    out = [scalar_report("SHA256(candidate)", int.from_bytes(sha256(candidate), "big"))]
    try:
        s = candidate.decode("ascii")
    except UnicodeDecodeError:
        s = ""
    if re.fullmatch(r"[0-9A-Fa-f]{64}", s):
        out.append(scalar_report("candidate-as-64hex", int(s, 16)))
    return out


def frozen_candidate_test(repo: Path, candidate: bytes, source_note: str,
                          log_path: Path, force: bool = False,
                          log_plaintext: bool = False, quiet: bool = False) -> Tuple[bool, Dict[str, Any]]:
    if not source_note.strip():
        raise ValueError("--source-note is required")
    if not audit_repo(repo, quiet=True):
        raise RuntimeError("repo audit failed; refusing to interpret a null result")

    cand_hash = sha256hex(candidate)
    if log_path.exists() and not force:
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("candidate_sha256") == cand_hash:
                raise FileExistsError("candidate bytes already tested by this harness; use --force only intentionally")

    t = load_targets(repo)
    targets = ["miniA", "miniAB", "inner96", "cosmic"]
    forms = [
        ("raw", candidate),
        ("sha256hex", cand_hash.encode("ascii")),
    ]
    kdfs = [("EVP-MD5", "md5"), ("EVP-SHA256", "sha256")]

    results: List[Dict[str, Any]] = []
    strong_hit = False

    for form_name, pw in forms:
        for kdf_name, digest_name in kdfs:
            for target_name in targets:
                x = t[target_name]
                key, iv = evp_bytes_to_key(pw, x["salt"], digest_name, 32, 16)
                pt = aes_cbc_decrypt(key, iv, x["ct"])
                pk = pkcs7_info(pt)
                rec: Dict[str, Any] = {
                    "form": form_name,
                    "kdf": kdf_name,
                    "target": target_name,
                    "pkcs7": None,
                    "strong_gate": False,
                }
                if target_name == "inner96":
                    rec["p32t"] = p32t_reading(key, x["ct"])
                    if rec["p32t"]["reading"] in ("primary:64hex+LF", "secondary:two-raw-32B"):
                        rec["strong_gate"] = True
                        strong_hit = True

                # Key material is checked on the raw plaintext of every decrypt, whatever its
                # padding: a right key can sit under a bad last block (tick 83, campaign 51).
                raw_matches = key_material_matches(pt)
                if raw_matches:
                    rec["address_material_hits_raw"] = raw_matches
                    rec["strong_gate"] = True
                    strong_hit = True
                if pk is not None:
                    body = pk["body"]
                    rec["pkcs7"] = {
                        "pad": pk["pad"],
                        "printable": pk["printable"],
                        "printable_head": pk["printable_head"],
                        "magic": pk["magic"],
                        "entropy": pk["entropy"],
                    }
                    rec["strong_gate"] = bool(rec["strong_gate"] or pk["strong"])
                    matches = key_material_matches(body)
                    if matches:
                        rec["address_material_hits"] = matches
                        rec["strong_gate"] = True
                    if log_plaintext or rec["strong_gate"]:
                        rec["body_head_hex"] = body[:200].hex()
                        try:
                            rec["body_head_text"] = body[:200].decode("utf-8")
                        except UnicodeDecodeError:
                            pass
                    if rec["strong_gate"]:
                        strong_hit = True
                results.append(rec)

    scalar_checks = candidate_scalar_checks(candidate)
    for s in scalar_checks:
        if s["matches"]:
            strong_hit = True

    record: Dict[str, Any] = {
        "ts": utc_now(),
        "version": VERSION,
        "source_note": source_note,
        "candidate_sha256": cand_hash,
        "candidate_len": len(candidate),
        "candidate_preview": preview_bytes(candidate, 80),
        "decrypt_count": len(results),
        "decrypts": results,
        "scalars": scalar_checks,
        "HIT": strong_hit,
    }
    if log_plaintext:
        try:
            record["candidate_utf8"] = candidate.decode("utf-8")
        except UnicodeDecodeError:
            record["candidate_hex"] = candidate.hex()

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

    if not quiet:
        print("candidate sha256:", cand_hash)
        print("decrypts:", len(results), "strong_hit:", strong_hit)
        for r in results:
            if r["pkcs7"] is not None or r.get("p32t", {}).get("reading") or r["strong_gate"]:
                print(" ", json.dumps(r, sort_keys=True)[:1200])
        for s in scalar_checks:
            print(" scalar:", json.dumps(s, sort_keys=True))
        print("*** STRONG HIT ***" if strong_hit else "null; candidate logged and now spent locally")

    return strong_hit, record

# ---------------------------------------------------------------------------
# Provenance-aware strict gate
# ---------------------------------------------------------------------------

REQUIRED_INTAKE = {
    "jrk_sentence": ("id", "date", "author", "text"),
    "gsmg_page": ("url", "fetched_at", "body_file"),
    "uttered_password": ("speaker", "date", "where", "candidate"),
}


def norm_text(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def parked_corpus(repo: Path) -> Tuple[str, set]:
    patterns = [
        "neo/LEDGER.md",
        "neo/materials/*.txt", "neo/materials/*.json", "neo/materials/*.md",
        "neo/materials/primary/*.txt", "neo/materials/primary/*.json", "neo/materials/primary/*.md",
        "neo/prior-sessions/*/*.md", "unverified/*.md",
        "neo/harness/campaign_*.py", "neo/harness/p32t_freeze.py", "neo/attempts/*.txt",
    ]
    chunks: List[str] = []
    tokens = set()
    import glob
    for pat in patterns:
        for p in glob.glob(str(repo / pat)):
            try:
                txt = Path(p).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            chunks.append(norm_text(txt))
            tokens.update(norm_text(x) for x in re.split(r"\W+", txt) if x)
    return "|".join(chunks), tokens


def prior_attempt_passwords(repo: Path) -> set:
    import glob
    out = set()
    for p in glob.glob(str(repo / "neo" / "attempts" / "*.jsonl")):
        try:
            lines = Path(p).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            pw = rec.get("pw")
            if isinstance(pw, str):
                out.add(pw)
    return out


def intake_candidate(intake: Dict[str, Any]) -> Tuple[bytes, str]:
    kind = intake.get("kind")
    if kind not in REQUIRED_INTAKE:
        raise ValueError(f"kind must be one of {sorted(REQUIRED_INTAKE)}")
    missing = [k for k in REQUIRED_INTAKE[kind] if not str(intake.get(k, "")).strip()]
    if missing:
        raise ValueError(f"missing provenance fields: {missing}")

    if kind == "jrk_sentence":
        source = str(intake["text"])
        candidate = str(intake.get("candidate", source))
        if candidate not in source:
            raise ValueError("candidate must occur verbatim in supplied creator text")
        note = f"jrk_sentence id={intake['id']} date={intake['date']} author={intake['author']}"
        return candidate.encode("utf-8"), note

    if kind == "uttered_password":
        candidate = str(intake["candidate"])
        note = f"uttered_password speaker={intake['speaker']} date={intake['date']} where={intake['where']}"
        return candidate.encode("utf-8"), note

    # gsmg_page
    from urllib.parse import urlparse
    host = (urlparse(str(intake["url"])).hostname or "").lower()
    if host != "gsmg.io" and not host.endswith(".gsmg.io"):
        raise ValueError("gsmg_page URL must be gsmg.io or a subdomain")
    body = Path(intake["body_file"]).read_bytes()
    if body.strip() == b"Hello :-)" or len(body.strip()) <= len(b"Hello :-)"):
        raise ValueError("page is the tiny Hello :-) 404 or shorter")
    source = body.decode("utf-8", "replace")
    candidate = intake.get("candidate")
    if candidate is None:
        raise ValueError("gsmg_page intake requires explicit candidate; gate will not select text")
    candidate = str(candidate)
    if candidate not in source:
        raise ValueError("candidate must occur verbatim in saved page body")
    note = f"gsmg_page url={intake['url']} fetched_at={intake['fetched_at']} body_sha256={sha256hex(body)}"
    return candidate.encode("utf-8"), note


def gate_refusal(repo: Path, candidate: bytes) -> Optional[str]:
    try:
        s = candidate.decode("utf-8")
    except UnicodeDecodeError:
        return None
    h = sha256hex(candidate)
    tried = prior_attempt_passwords(repo)
    if s in tried or h in tried or h.upper() in tried:
        return "exact candidate or its SHA256 hex already appears in repo attempts"
    corpus, tokens = parked_corpus(repo)
    n = norm_text(s)
    if not n:
        return "candidate is empty after normalization"
    if len(n) >= 6 and n in corpus:
        return "candidate occurs in the parked corpus"
    if len(n) < 6 and n in tokens:
        return "candidate is a token in the parked corpus"
    return None

# ---------------------------------------------------------------------------
# Raw-key structural test
# ---------------------------------------------------------------------------


def raw_key_test(repo: Path, key: bytes) -> bool:
    if len(key) != 32:
        raise ValueError("raw key must be exactly 32 bytes")
    t = load_targets(repo)
    hit = False
    print("AES key:", key.hex())
    for name in ["miniA", "miniAB", "inner96", "cosmic"]:
        ct = t[name]["ct"]
        last = xor_bytes(aes_ecb_decrypt_block(key, ct[-16:]), ct[-32:-16]) if len(ct) >= 32 else None
        rec = {"target": name, "last_plain_block": last.hex() if last else None}
        if last:
            p = last[-1]
            goodpad = 1 <= p <= 16 and last[-p:] == bytes([p]) * p
            rec["last_block_valid_pad"] = goodpad
            rec["pad"] = p if goodpad else None
        if name == "inner96":
            rec["p32t"] = p32t_reading(key, ct)
            if rec["p32t"]["reading"] in ("primary:64hex+LF", "secondary:two-raw-32B"):
                hit = True
        print(json.dumps(rec, sort_keys=True))

    sr = scalar_report("same-32B-as-secp256k1-scalar", int.from_bytes(key, "big"))
    print(json.dumps(sr, sort_keys=True))
    if sr["matches"]:
        hit = True
    print("*** STRONG HIT ***" if hit else "no strong structural hit")
    return hit

# ---------------------------------------------------------------------------
# OP_RETURN / nonce exact comparison
# ---------------------------------------------------------------------------


def load_nonce_points(path: Path) -> List[Dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "points" in data:
        data = data["points"]
    if not isinstance(data, list):
        raise ValueError("nonce JSON must be a list or {'points': [...]} object")
    out = []
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            raise ValueError(f"nonce row {i} is not an object")
        label = str(row.get("label", f"point{i}"))
        x = str(row.get("x", "")).lower().removeprefix("0x")
        y = str(row.get("y", "")).lower().removeprefix("0x")
        if not re.fullmatch(r"[0-9a-f]{64}", x) or not re.fullmatch(r"[0-9a-f]{64}", y):
            raise ValueError(f"nonce row {i} x/y must each be exactly 64 hex chars")
        out.append({"label": label, "x": x, "y": y})
    return out


def compare_opreturn(payload_hex: str, points: List[Dict[str, str]]) -> List[Dict[str, str]]:
    h = payload_hex.lower().removeprefix("0x")
    if not re.fullmatch(r"[0-9a-f]{64}", h):
        raise ValueError("payload must be exactly 32 bytes / 64 hex characters")
    p = bytes.fromhex(h)
    matches = []
    for row in points:
        for coord in ("x", "y"):
            c = bytes.fromhex(row[coord])
            if p == c:
                matches.append({"label": row["label"], "coord": coord, "mode": "exact"})
            if p == c[::-1]:
                matches.append({"label": row["label"], "coord": coord, "mode": "byte-reversed"})
    return matches

# ---------------------------------------------------------------------------
# Transaction JSON scanner
# ---------------------------------------------------------------------------


def decode_opreturn_script(script_hex: str) -> Optional[bytes]:
    try:
        b = bytes.fromhex(script_hex)
    except ValueError:
        return None
    if not b or b[0] != 0x6A:
        return None
    if len(b) == 1:
        return b""
    op = b[1]
    pos = 2
    if op <= 75:
        n = op
    elif op == 0x4C and len(b) >= 3:
        n, pos = b[2], 3
    elif op == 0x4D and len(b) >= 4:
        n, pos = int.from_bytes(b[2:4], "little"), 4
    else:
        return None
    if pos + n > len(b):
        return None
    return b[pos:pos+n]


def scan_tx_json(obj: Any) -> Dict[str, Any]:
    report: Dict[str, Any] = {"known_addresses": [], "op_returns": [], "txids": []}

    def walk(x: Any, path: str = "$"):
        if isinstance(x, dict):
            for key in ("txid", "hash"):
                v = x.get(key)
                if isinstance(v, str) and re.fullmatch(r"[0-9A-Fa-f]{64}", v):
                    report["txids"].append({"path": f"{path}.{key}", "value": v})
            # common Bitcoin Core / explorer scriptPubKey object
            spk = x.get("scriptPubKey")
            if isinstance(spk, dict):
                hx = spk.get("hex")
                if isinstance(hx, str):
                    payload = decode_opreturn_script(hx)
                    if payload is not None:
                        report["op_returns"].append({
                            "path": f"{path}.scriptPubKey.hex",
                            "payload_hex": payload.hex(),
                            "payload_len": len(payload),
                            "ascii": payload.decode("utf-8", "replace"),
                        })
            for k, v in x.items():
                walk(v, f"{path}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        elif isinstance(x, str):
            for addr, label in KNOWN_ADDRESSES.items():
                if addr in x:
                    report["known_addresses"].append({"path": path, "address": addr, "label": label})

    walk(obj)
    # de-dupe exact dicts
    for k in list(report):
        seen = set()
        uniq = []
        for row in report[k]:
            sig = json.dumps(row, sort_keys=True)
            if sig not in seen:
                seen.add(sig)
                uniq.append(row)
        report[k] = uniq
    return report

# ---------------------------------------------------------------------------
# Typed-component / Grigg-model inspector: deliberately non-generative
# ---------------------------------------------------------------------------


def component_info(path: Path) -> Dict[str, Any]:
    b = path.read_bytes()
    return {
        "path": str(path),
        "len": len(b),
        "sha256": sha256hex(b),
        "head_hex": b[:32].hex(),
        "printable": round(printable_ratio(b), 4),
    }


def components_report(params: Path, code: Path, text: Path, package: Optional[Path]) -> Dict[str, Any]:
    parts = {
        "params": params.read_bytes(),
        "code": code.read_bytes(),
        "text": text.read_bytes(),
    }
    out: Dict[str, Any] = {k: component_info(Path(p)) for k, p in [("params", params), ("code", code), ("text", text)]}
    out["note"] = "No concatenation, ordering, separator, encoding, or canonicalization was invented."
    if package is not None:
        pb = package.read_bytes()
        out["package"] = component_info(package)
        contained = {}
        for k, b in parts.items():
            offsets = []
            start = 0
            while True:
                i = pb.find(b, start)
                if i < 0:
                    break
                offsets.append(i)
                start = i + max(1, len(b))
            contained[k] = offsets
        out["package_component_offsets"] = contained
    return out

# ---------------------------------------------------------------------------
# Self tests
# ---------------------------------------------------------------------------


def aes_known_answer_test() -> bool:
    # NIST SP 800-38A AES-256-CBC first block.
    key = bytes.fromhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4")
    iv = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    ct = bytes.fromhex("f58c4c04d6e5f1ba779eabfb5f7bfbd6")
    want = bytes.fromhex("6bc1bee22e409f96e93d7e117393172a")
    got = aes_cbc_decrypt(key, iv, ct)
    good = got == want
    print(("OK  " if good else "FAIL"), "NIST AES-256-CBC known-answer")
    return good


def solved_stage_controls(repo: Path) -> bool:
    ok = True
    for rel, human, label in SOLVED_CONTROLS:
        p = repo / rel
        try:
            raw = b64_file(p)
            salt, ct = require_salted(raw, label)
            pw = sha256hex(human.encode("utf-8")).encode("ascii")
            key, iv = evp_bytes_to_key(pw, salt, "sha256", 32, 16)
            pt = aes_cbc_decrypt(key, iv, ct)
            info = pkcs7_info(pt)
            good = bool(info and info["strong"])
            details = None if info is None else {
                "pad": info["pad"], "printable": info["printable"],
                "head": preview_bytes(info["body"], 60),
            }
        except Exception as e:
            good = False
            details = repr(e)
        print(("OK  " if good else "FAIL"), f"solved control {label}", details)
        ok &= good
    return ok


def p32t_synthetic_selftest() -> bool:
    key = sha256(b"gsmg-p32t-synthetic-key")
    body = bytes(range(64))
    pt = body + bytes([0x10]) * 16
    iv = bytes(16)
    # We only expose decrypt; use available backend-specific encrypt for this test.
    backend = aes_backend()
    if backend == "pycryptodome":
        ct = _PyCryptoAES.new(key, _PyCryptoAES.MODE_CBC, iv).encrypt(pt)
    elif backend == "cryptography":
        enc = _Cipher(_algorithms.AES(key), _modes.CBC(iv)).encryptor()
        ct = enc.update(pt) + enc.finalize()
    else:
        proc = subprocess.run(
            ["openssl", "enc", "-aes-256-cbc", "-e", "-K", key.hex(), "-iv", iv.hex(), "-nopad"],
            input=pt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if proc.returncode != 0:
            print("FAIL openssl synthetic encrypt", proc.stderr.decode("utf-8", "replace"))
            return False
        ct = proc.stdout
    got = p32t_last_plain_block(key, ct)
    good = got == bytes([0x10]) * 16
    print(("OK  " if good else "FAIL"), "P32T IV-independent last-block synthetic test")
    return good


def full_selftest(repo: Path) -> bool:
    print("backend:", aes_backend())
    checks = [
        audit_repo(repo),
        aes_known_answer_test(),
        secp_selftest(),
        p32t_synthetic_selftest(),
        solved_stage_controls(repo),
    ]
    ok = all(checks)
    print("self-test passed:", ok)
    return ok

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report_log(path: Path) -> Dict[str, Any]:
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    hashes = {r.get("candidate_sha256") for r in rows if r.get("candidate_sha256")}
    hits = [r for r in rows if r.get("HIT")]
    return {
        "log": str(path),
        "records": len(rows),
        "unique_candidate_hashes": len(hashes),
        "hits": len(hits),
        "latest_ts": rows[-1].get("ts") if rows else None,
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def default_log() -> Path:
    return Path.cwd() / "offline_solver_attempts.jsonl"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gsmg_offline_solver.py",
        description="Conservative offline GSMG evidence/crypto harness; no candidate generation.",
    )
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="check crypto backend and local primitives")

    a = sub.add_parser("audit", help="byte-audit pinned GSMG ciphertexts")
    a.add_argument("--repo", required=True, type=Path)

    s = sub.add_parser("selftest", help="audit + AES + secp + solved positive controls")
    s.add_argument("--repo", required=True, type=Path)

    t = sub.add_parser("test", help="test exactly one explicit candidate")
    t.add_argument("--repo", required=True, type=Path)
    g = t.add_mutually_exclusive_group(required=True)
    g.add_argument("--candidate")
    g.add_argument("--candidate-file", type=Path)
    t.add_argument("--source-note", required=True)
    t.add_argument("--log", type=Path, default=None)
    t.add_argument("--force", action="store_true", help="allow exact local re-test")
    t.add_argument("--log-plaintext", action="store_true", help="store candidate/plaintext snippets in JSONL")

    ga = sub.add_parser("gate", help="strict provenance-aware intake JSON")
    ga.add_argument("--repo", required=True, type=Path)
    ga.add_argument("intake", type=Path)
    ga.add_argument("--log", type=Path, default=None)
    ga.add_argument("--force", action="store_true")
    ga.add_argument("--log-plaintext", action="store_true")

    k = sub.add_parser("keytest", help="test one explicit raw 32-byte AES/scalar key")
    k.add_argument("--repo", required=True, type=Path)
    k.add_argument("--key-hex", required=True)

    d = sub.add_parser("digest", help="SHA256 exact bytes; no normalization")
    dg = d.add_mutually_exclusive_group(required=True)
    dg.add_argument("--text")
    dg.add_argument("--file", type=Path)
    dg.add_argument("--hex", dest="hexdata")

    c = sub.add_parser("components", help="inspect params/code/text separately; do not serialize them")
    c.add_argument("--params", required=True, type=Path)
    c.add_argument("--code", required=True, type=Path)
    c.add_argument("--text", required=True, type=Path)
    c.add_argument("--package", type=Path, help="optional exact package bytes YOU already defined")

    o = sub.add_parser("opreturn", help="exact 32-byte payload vs nonce x/y and byte reversal")
    o.add_argument("--payload", required=True)
    o.add_argument("--nonce-json", required=True, type=Path)

    x = sub.add_parser("txscan", help="scan saved transaction JSON; no network access")
    x.add_argument("json_file", type=Path)
    x.add_argument("--nonce-json", type=Path, help="also compare every 32B OP_RETURN exactly to nonce x/y")

    r = sub.add_parser("report", help="summarize local attempt log")
    r.add_argument("--log", type=Path, default=None)

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "doctor":
            print("version:", VERSION)
            print("python:", sys.version.replace("\n", " "))
            print("AES backend:", aes_backend())
            print("openssl:", shutil.which("openssl"))
            print("ripemd160:", ripemd160_backend())
            ok = aes_known_answer_test() and secp_selftest() and p32t_synthetic_selftest()
            print("doctor passed:", ok)
            return 0 if ok else 3

        if args.cmd == "audit":
            return 0 if audit_repo(args.repo.resolve()) else 3

        if args.cmd == "selftest":
            return 0 if full_selftest(args.repo.resolve()) else 3

        if args.cmd == "test":
            cand = read_candidate(args)
            log = (args.log or default_log()).resolve()
            hit, _ = frozen_candidate_test(
                args.repo.resolve(), cand, args.source_note, log,
                force=args.force, log_plaintext=args.log_plaintext,
            )
            return 10 if hit else 0

        if args.cmd == "gate":
            intake = json.loads(args.intake.read_text(encoding="utf-8"))
            cand, note = intake_candidate(intake)
            reason = gate_refusal(args.repo.resolve(), cand)
            if reason and not args.force:
                print("REFUSED:", reason)
                return 2
            log = (args.log or default_log()).resolve()
            hit, _ = frozen_candidate_test(
                args.repo.resolve(), cand, note, log,
                force=args.force, log_plaintext=args.log_plaintext,
            )
            return 10 if hit else 0

        if args.cmd == "keytest":
            h = args.key_hex.lower().removeprefix("0x")
            if not re.fullmatch(r"[0-9a-f]{64}", h):
                print("REFUSED: --key-hex must be exactly 64 hex chars")
                return 2
            return 10 if raw_key_test(args.repo.resolve(), bytes.fromhex(h)) else 0

        if args.cmd == "digest":
            if args.text is not None:
                b = args.text.encode("utf-8")
                src = "text:utf8"
            elif args.file is not None:
                b = args.file.read_bytes()
                src = str(args.file)
            else:
                h = args.hexdata.lower().removeprefix("0x")
                if len(h) % 2 or not re.fullmatch(r"[0-9a-f]*", h):
                    raise ValueError("--hex must contain an even number of hex characters")
                b = bytes.fromhex(h)
                src = "hex"
            print(json.dumps({
                "source": src, "len": len(b), "sha256": sha256hex(b),
                "head_hex": b[:64].hex(), "printable": round(printable_ratio(b), 4),
            }, indent=2, sort_keys=True))
            return 0

        if args.cmd == "components":
            rep = components_report(args.params, args.code, args.text, args.package)
            print(json.dumps(rep, indent=2, sort_keys=True))
            return 0

        if args.cmd == "opreturn":
            pts = load_nonce_points(args.nonce_json)
            matches = compare_opreturn(args.payload, pts)
            print(json.dumps({"payload": args.payload.lower().removeprefix("0x"), "matches": matches}, indent=2))
            return 10 if matches else 0

        if args.cmd == "txscan":
            obj = json.loads(args.json_file.read_text(encoding="utf-8"))
            rep = scan_tx_json(obj)
            if args.nonce_json:
                pts = load_nonce_points(args.nonce_json)
                comparisons = []
                for op in rep["op_returns"]:
                    if op["payload_len"] == 32:
                        comparisons.append({
                            "path": op["path"],
                            "payload_hex": op["payload_hex"],
                            "matches": compare_opreturn(op["payload_hex"], pts),
                        })
                rep["nonce_comparisons"] = comparisons
            print(json.dumps(rep, indent=2, sort_keys=True))
            # Mentioning the prize or better-half address is information, not a cryptographic hit.
            any_hit = any(c.get("matches") for c in rep.get("nonce_comparisons", []))
            return 10 if any_hit else 0

        if args.cmd == "report":
            log = (args.log or default_log()).resolve()
            print(json.dumps(report_log(log), indent=2, sort_keys=True))
            return 0

        raise RuntimeError("unreachable")

    except FileExistsError as e:
        print("REFUSED:", e, file=sys.stderr)
        return 2
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print("ERROR:", e, file=sys.stderr)
        return 2
    except RuntimeError as e:
        print("ABORT:", e, file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
