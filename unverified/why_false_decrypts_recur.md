# Why bogus "decrypts" keep appearing — measured

Two numbers that settle recurring claims. Both measured here, not asserted.

## 1. The IV is emitted by the KDF. It is not a free parameter.

Every opened envelope in this puzzle is `openssl enc -aes-256-cbc -md sha256` on a
`Salted__` blob. `EVP_BytesToKey(password, salt)` emits **both** the 32-byte key and the
16-byte IV. For the known-good Phase-3.2 decrypt:

```
key = f4c72c3a26461664d397f35d6a8ca26919786052161b12e53239e3df6b1157b3
IV  = b620574d04ee253df257fcd340eb201f      <- derived, not chosen
```

So "use IV = 00…00" is not an alternative reading of the same machine; it is a different
machine from the one the creator demonstrably used for Phase 2, Phase 3 and Phase 3.2.

**The nuance that makes zero-IV claims look plausible.** Running the *correct key* with a
zero IV still yields mostly-correct plaintext: in CBC, a wrong IV corrupts only the **first
16-byte block**, and the stream self-heals from block 2 onward. So a zero-IV "decrypt" can
print ~94% readable text and be mistaken for success. It is not: the first block is garbage
and the plaintext is not the real one.

The converse is the load-bearing point: **a wrong key produces nothing readable regardless
of the IV.** So "IV = 0" is not a construction at all — it still requires naming the
32-byte key, which is the entire problem. Specifying an IV solves none of it.

## 2. Valid PKCS#7 padding is a 1-in-256 coincidence.

Measured against the real 80-byte ciphertext, using random keys:

```
random keys tried   : 300,000
PKCS#7-valid        : 1,235   = 1 in 243      (theory ~1 in 256)
also passing our gate:     0   = none in 300,000
```

A padding-only criterion is therefore worthless at scale: **a battery of 100,000 candidates
will throw ~400 padding-valid results by pure chance.** That is the whole explanation for
the steady stream of Cosmic Duality "decryptions" — each is one of those 400, usually with a
1-byte pad and unreadable body.

It also explains the 96-byte envelopes specifically: a short ciphertext gives the chance
coincidence nowhere to fail, since there is almost no plaintext to look wrong.

## The gate this justifies

`neo/harness/aes_try.py` accepts only on strict PKCS#7 **and** corroboration: pad ≥ 4
(~2⁻³²), or a ≥4-byte magic prefix, or high printability. The measurement above is its
validation: **zero false positives in 300,000 random keys**, against 1,235 that padding
alone would have waved through.

Practical rules that follow:

- A claimed decrypt with a **1-byte pad** and a non-printable body is noise. Always.
- A claimed decrypt that names an **IV but not a key** has not specified a construction.
- "It produces a valid key / valid padding / a valid address" is not evidence — every
  64-symbol string yields a valid secp256k1 scalar, and 1 in 256 random keys yields valid
  padding.
