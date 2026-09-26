#!/usr/bin/env python3
"""P32T last-block freeze oracle.

P32T (inner96): 80-byte CT, salt b45a5e3d827593ca, five CBC blocks C1..C5.
CBC: P_i = D_K(C_i) XOR C_{i-1}. The LAST block P5 = D_K(C5) XOR C4 depends only on K
(C4, C5 are known ciphertext); the IV is irrelevant to it.

If P32T's plaintext is two raw 32-byte keys (64 bytes content), PKCS#7 pads to 80 with a
full 16-byte block of 0x10. So the necessary, IV-free accept test for that reading is:

    P5 == bytes([0x10]) * 16       (a 128-bit test, ~2^-128 false-positive rate)

This module exposes p5(K) and freeze_ok(K). No salt, no IV, no printable scoring.
"""
import os, sys, base64
from Crypto.Cipher import AES
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aes_try import load_targets

_t = load_targets()["inner96"]
CT = _t["ct"]                 # 80 bytes
assert len(CT) == 80, len(CT)
C4 = CT[48:64]
C5 = CT[64:80]
PAD16 = bytes([0x10]) * 16

def p5(K: bytes) -> bytes:
    """The 5th plaintext block under key K (ECB-decrypt C5, XOR C4). IV-free."""
    d = AES.new(K, AES.MODE_ECB).decrypt(C5)
    return bytes(a ^ b for a, b in zip(d, C4))

def freeze_ok(K: bytes) -> bool:
    return p5(K) == PAD16

def self_test():
    """Encrypt a synthetic 'two keys' plaintext under a known K, confirm the freeze
    recovers it and a wrong K does not."""
    import hashlib
    K = hashlib.sha256(b"synthetic-key").digest()
    body = bytes(range(64))                     # two 32-byte 'keys'
    pt = body + PAD16                            # 80 bytes, pad=16
    iv = bytes(16)                               # any IV; last block is IV-free
    ct = AES.new(K, AES.MODE_CBC, iv).encrypt(pt)
    c4, c5 = ct[48:64], ct[64:80]
    # reproduce the oracle against this synthetic ct
    d = AES.new(K, AES.MODE_ECB).decrypt(c5)
    got = bytes(a ^ b for a, b in zip(d, c4))
    ok_true = (got == PAD16)
    Kw = hashlib.sha256(b"wrong-key").digest()
    dw = AES.new(Kw, AES.MODE_ECB).decrypt(c5)
    gotw = bytes(a ^ b for a, b in zip(dw, c4))
    ok_false = (gotw != PAD16)
    print("self-test freeze True on right K:", ok_true, " rejects wrong K:", ok_false)
    return ok_true and ok_false

if __name__ == "__main__":
    print("P32T C4:", C4.hex(), " C5:", C5.hex())
    print("self-test passed:", self_test())


# ---- generalized IV-free last-block readings (added tick 30) ----
def last_block_pad(K: bytes):
    """If P5 = D_K(C5) XOR C4 ends in valid PKCS#7, return pad length p (1..16), else None.
    IV-free. p==16 is the '64-byte content' reading; smaller p leaves 16-p content bytes."""
    b = p5(K)
    p = b[-1]
    if 1 <= p <= 16 and b[-p:] == bytes([p]) * p:
        return p
    return None

def reading_hits(K: bytes):
    """Which named plaintext-structure readings the last block satisfies (all IV-free)."""
    b = p5(K)
    out = []
    if b == bytes([0x10]) * 16:
        out.append("64B-tworawkeys(pad16)")
    if b[1:] == bytes([0x0f]) * 15 and b[0] == 0x0a:
        out.append("65B-hexkey+LF(pad15)")
    if b[1:] == bytes([0x0f]) * 15 and 0x30 <= b[0] <= 0x66:
        out.append("65B-content+pad15(printable last)")
    p = last_block_pad(K)
    if p is not None and p < 15:
        out.append(f"validpad{p}(weak)")
    return out
