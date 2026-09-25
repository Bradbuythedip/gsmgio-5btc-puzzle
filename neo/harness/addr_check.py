#!/usr/bin/env python3
"""Bounded offline address oracle for named candidate objects.

Turns a small, pre-registered set of candidate objects into secp256k1 scalars under a FIXED
encoding set and compares the derived P2PKH addresses (compressed + uncompressed) against
the puzzle's published addresses. This is a yes/no check for objects that are already named
by the constraint sheet; it is deliberately capped so it cannot become a preimage grind.

Encodings (12 addresses per candidate):
  sha256      sha256(bytes)                         (brainwallet-style, the creator's sha-b4 habit)
  sha256d     sha256(sha256(bytes))
  hex64       the candidate itself if it is 64 hex chars
  rawpad      the raw bytes left-padded with zeros to 32 bytes (<= 32-byte objects only)
  bitrev      sha256(bytes) with every byte bit-reversed and the byte order reversed
              (the creator's attested representation trick, hint 2023-02-23)
  byterev     sha256(bytes) with byte order reversed

Targets:
  1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe   prize (authenticated)
  17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa   README second address
  1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9   user-supplied "planted" address (NOT in the archive)
"""
import hashlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from btc_addr import addrs, N

TARGETS = {
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe": "prize",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa": "second",
    "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": "planted(user)",
}
CAP = 2000   # hard cap on candidates per run; this is an oracle for named objects, not a grinder

def _bitrev_byte(b):
    return int('{:08b}'.format(b)[::-1], 2)

def encodings(obj):
    """obj: bytes. Yields (name, scalar)."""
    h = hashlib.sha256(obj).digest()
    yield "sha256", int.from_bytes(h, 'big')
    yield "sha256d", int.from_bytes(hashlib.sha256(h).digest(), 'big')
    s = obj.decode('latin1')
    if len(s) == 64 and all(c in '0123456789abcdefABCDEF' for c in s):
        yield "hex64", int(s, 16)
    if 1 <= len(obj) <= 32:
        yield "rawpad", int.from_bytes(obj.rjust(32, b'\0'), 'big')
    yield "bitrev", int.from_bytes(bytes(_bitrev_byte(b) for b in h)[::-1], 'big')
    yield "byterev", int.from_bytes(h[::-1], 'big')

def check(candidates, verbose=False):
    """candidates: list of (label, bytes). Returns list of matches (label, enc, form, addr, target)."""
    if len(candidates) > CAP:
        raise SystemExit(f"refusing {len(candidates)} candidates (> cap {CAP}); this is not a grinder")
    matches = []
    n = 0
    for label, obj in candidates:
        for enc, k in encodings(obj):
            if not (1 <= k < N):
                continue
            c, u = addrs(k)
            n += 2
            for form, a in (("compressed", c), ("uncompressed", u)):
                if a in TARGETS:
                    matches.append((label, enc, form, a, TARGETS[a]))
                    print("*** ADDRESS MATCH ***", label, enc, form, a, TARGETS[a], flush=True)
                if verbose:
                    print(label, enc, form, a)
    print(f"[addr_check] candidates={len(candidates)} addresses_derived={n} matches={len(matches)}")
    return matches

def self_test():
    # privkey 1 via rawpad of b'\x01' must give the canonical addresses
    got = {}
    for enc, k in encodings(b'\x01'):
        if enc == "rawpad":
            got = addrs(k)
    ok = got == ('1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH', '1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm')
    print("self-test passed:", ok)
    return ok

if __name__ == "__main__":
    self_test()
    if len(sys.argv) > 1:
        cands = [(a, a.encode()) for a in sys.argv[1:]]
        check(cands, verbose=True)
