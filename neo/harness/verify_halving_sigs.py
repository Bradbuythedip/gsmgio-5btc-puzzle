#!/usr/bin/env python3
"""Offline check that the 2020 halving spend (materials/chain/tx_halving_spend.hex) is signed
by the prize key, so its nLockTime (629998) is bound to that key. No network, no key search.

Every input is legacy P2PKH, so SIGHASH_ALL needs only the tx itself and each input's
scriptPubKey, rebuilt from the pubkey in its scriptSig. ECDSA is verified with the repo's own
curve code (btc_addr) and, if installed, independently with the `ecdsa` package.
Negative control: the same signatures against the tx with locktime + 1 must fail.
It verifies signatures only. It does not show that the tx was mined.

  python3 verify_halving_sigs.py      exit 0 if every check passes
"""
import hashlib, os, sys
import btc_addr

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, "..", "materials", "chain", "tx_halving_spend.hex")
PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
N = btc_addr.N

def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def h160(b): return btc_addr.hash160(b)

def varint(b, i):
    x = b[i]
    if x < 0xfd: return x, i + 1
    w = {0xfd: 2, 0xfe: 4, 0xff: 8}[x]
    return int.from_bytes(b[i + 1:i + 1 + w], "little"), i + 1 + w

def enc_varint(n):
    return bytes([n]) if n < 0xfd else b"\xfd" + n.to_bytes(2, "little")

def parse(tx):
    assert not (tx[4] == 0 and tx[5] == 1), "segwit serialization: not handled here"
    ver, i = tx[:4], 4
    n, i = varint(tx, i); ins = []
    for _ in range(n):
        prev = tx[i:i + 36]; i += 36
        l, i = varint(tx, i); ss = tx[i:i + l]; i += l
        ins.append((prev, ss, tx[i:i + 4])); i += 4
    o0 = i
    n, i = varint(tx, i)
    for _ in range(n):
        i += 8; l, i = varint(tx, i); i += l
    return ver, ins, tx[o0:i], tx[i:i + 4]

def pushes(s):
    out, i = [], 0
    while i < len(s):
        l = s[i]; out.append(s[i + 1:i + 1 + l]); i += 1 + l
    return out

def sighash_all(ver, ins, outs, lt, k, spk, ht):
    b = ver + enc_varint(len(ins))
    for j, (prev, _, seq) in enumerate(ins):
        s = spk if j == k else b""
        b += prev + enc_varint(len(s)) + s + seq
    return int.from_bytes(dsha(b + outs + lt + ht.to_bytes(4, "little")), "big")

def der_rs(sig):
    lr = sig[3]; r = int.from_bytes(sig[4:4 + lr], "big")
    ls = sig[5 + lr]; s = int.from_bytes(sig[6 + lr:6 + lr + ls], "big")
    return r, s

def verify_own(pub, z, r, s):
    if not (1 <= r < N and 1 <= s < N): return False
    Q = (int.from_bytes(pub[1:33], "big"), int.from_bytes(pub[33:65], "big"))
    w = pow(s, -1, N)
    P = btc_addr._add(btc_addr.mul(z * w % N), btc_addr.mul(r * w % N, Q))
    return P is not None and P[0] % N == r

def verify_lib(pub, z, der):
    try:
        import ecdsa
        from ecdsa.util import sigdecode_der
    except ImportError:
        return None
    vk = ecdsa.VerifyingKey.from_string(pub, curve=ecdsa.SECP256k1)
    try:
        return vk.verify_digest(der, z.to_bytes(32, "big"), sigdecode=sigdecode_der)
    except ecdsa.BadSignatureError:
        return False

def main():
    raw = bytes.fromhex("".join(l.strip() for l in open(TX) if not l.startswith("#")))
    ver, ins, outs, lt = parse(raw)
    locktime = int.from_bytes(lt, "little")
    print(f"txid {dsha(raw)[::-1].hex()}  locktime {locktime}  inputs {len(ins)}")
    ok = True
    for k, (prev, ss, seq) in enumerate(ins):
        sig, pub = pushes(ss)
        der, ht = sig[:-1], sig[-1]
        spk = b"\x76\xa9\x14" + h160(pub) + b"\x88\xac"
        r, s = der_rs(der)
        z = sighash_all(ver, ins, outs, lt, k, spk, ht)
        z_bad = sighash_all(ver, ins, outs, (locktime + 1).to_bytes(4, "little"), k, spk, ht)
        own, lib = verify_own(pub, z, r, s), verify_lib(pub, z, der)
        neg = not verify_own(pub, z_bad, r, s)
        prize = btc_addr.p2pkh(pub) == PRIZE
        good = prize and ht == 1 and own and lib is not False and neg
        ok &= good
        print(f"  in{k} {prev[:32][::-1].hex()[:16]}…:{int.from_bytes(prev[32:], 'little')} seq {seq[::-1].hex()} "
              f"prize-key {prize} SIGHASH_ALL {ht == 1} own {own} ecdsa-lib {lib} rejects locktime+1 {neg}")
    print("halving-spend signatures verified:", ok)
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
