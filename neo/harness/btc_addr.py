#!/usr/bin/env python3
"""Dependency-free secp256k1 -> P2PKH address derivation, with known-answer tests.

Used to verify candidate scalars derived from puzzle material against the puzzle's
own published prize address. Pure Python (no coincurve/ecdsa needed); fast enough
for the small, enumerable candidate sets the puzzle theories produce.
"""
import hashlib

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def _inv(a, m=P):
    return pow(a, m - 2, m)


def _add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    (x1, y1), (x2, y2) = p, q
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        lam = (3 * x1 * x1) * _inv(2 * y1) % P
    else:
        lam = (y2 - y1) * _inv(x2 - x1) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)


def mul(k, point=(GX, GY)):
    r = None
    while k:
        if k & 1:
            r = _add(r, point)
        point = _add(point, point)
        k >>= 1
    return r


def b58encode(b):
    n = int.from_bytes(b, 'big')
    s = ''
    while n > 0:
        n, r = divmod(n, 58)
        s = B58[r] + s
    return '1' * (len(b) - len(b.lstrip(b'\0'))) + s


def hash160(b):
    return hashlib.new('ripemd160', hashlib.sha256(b).digest()).digest()


def p2pkh(pub):
    h = b'\x00' + hash160(pub)
    return b58encode(h + hashlib.sha256(hashlib.sha256(h).digest()).digest()[:4])


def pubkeys(k):
    """Return (compressed, uncompressed) SEC encodings for scalar k, or (None, None)."""
    if not (1 <= k < N):
        return None, None
    x, y = mul(k)
    xb = x.to_bytes(32, 'big')
    return (bytes([2 + (y & 1)]) + xb, b'\x04' + xb + y.to_bytes(32, 'big'))


def addrs(k):
    c, u = pubkeys(k)
    if c is None:
        return None, None
    return p2pkh(c), p2pkh(u)


def self_test():
    """Known answer tests: the canonical privkey=1 addresses, plus a second vector."""
    vectors = [
        (1, '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH', '1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm'),
        (2, '1cMh228HTCiwS8ZsaakH8A8wze1JR5ZsP', '1LagHJk2FyCV2VzrNHVqg3gYG4TSYwDV4m'),
    ]
    ok = True
    for k, ec, eu in vectors:
        c, u = addrs(k)
        good = (c == ec and u == eu)
        ok = ok and good
        print(('OK  ' if good else 'FAIL'), k, c, u)
    return ok


if __name__ == '__main__':
    print('self-test passed:', self_test())
