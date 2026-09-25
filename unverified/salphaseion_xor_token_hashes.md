# XOR of the seven token hashes [SalPhaseIon / Cosmic Duality]

A widely circulated writeup (and several LLM-generated repos, e.g. `jackdevs66/GSMG5_CDuality`)
claims a "known working shape":

> `XOR(sha256(t1), …, sha256(t7))` → 32-byte OpenSSL password → decrypts the Cosmic Duality blob

with the seven tokens given as `matrixsumlist, enter, lastwordsbeforearchichoice,
thispassword, matrixsumlist, yourlastcommand, secondanswer`, producing

```
a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735
```

## What reproduces

The arithmetic is real. XORing the seven SHA-256 digests does yield exactly that value.
Reproducible with `neo/harness/verify_xor_theory.py`.

## What does not

**That value does not decrypt the Cosmic Duality blob.** Tested as a password in hex
(lower and upper case) and as recomputed bytes, against EVP_BytesToKey with MD5 / SHA-1 /
SHA-256 at both 128- and 256-bit key lengths, and as a raw 32-byte key with a zero IV, a
doubled-salt IV, and a ciphertext-prefix IV. No combination yields valid PKCS#7 padding
plus plausible structure.

So the step the rest of the theory rests on was never actually verified. The number is
real; the decryption it is supposed to perform does not happen.

## The related scalar claim

The same writeups propose XORing the witness scalar
`abc09ead825c42ba92c90e95a07cfc8bcda8ae6bd2116c31583aaff19f5d99f6`
against that key (and against truncated "half"/"better half" scalars) to obtain the prize key.

121 bounded XOR candidates were derived and checked: the scalar alone, XORed against the
claimed key, against the recomputed XOR, against SHA-256 of each of the seven tokens,
`yinyang`, `yellowblueprimes`, `half`, `betterhalf`, the prize address and the page caption,
and against zero — singly and in pairs. **Zero produce the prize address.**

Worth recording: that scalar's *uncompressed* key derives to
`1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M` — a real GSMG-prefixed vanity address, but not
`1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`. So it is a vanity/witness operand, not the prize key.
A `1GSMG` prefix is only ~58⁴ ≈ 11M grinding work, so the prefix alone carries no authority
about provenance.

## Result

Closed. By the theory's own stated pass condition — only a scalar that spends
`1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` counts — this branch fails.

One methodological point from those writeups *is* correct and worth keeping: only 32-byte
scalars (or SHA-256 digests) are XOR-meaningful. EC points, addresses and HASH160s are not
XOR-closed, so XORing those is a category error regardless of the theory.

Address derivation used for these negatives is `neo/harness/btc_addr.py`, a dependency-free
secp256k1 implementation validated against canonical known-answer vectors (privkey 1 and 2,
compressed and uncompressed) so that a "no match" from it can be trusted.
