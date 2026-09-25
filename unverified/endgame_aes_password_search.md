# Endgame AES password search — pinned convention and exclusions

Recording ~14.8M tested-and-excluded password candidates against the four outstanding
AES locks, so the same ground is not re-covered. Harness and per-attempt logs live in
`neo/harness/` and `neo/attempts/`.

## The four outstanding locks

All are OpenSSL `Salted__` blobs unless noted.

| id | bytes | salt | source |
|---|---|---|---|
| `miniA` | 48 (ct 32) | `3ab585348552415d` | SalPhaseIon tail, after "sha b4 first hint is your last command" |
| `miniB` | 48, no header | — | SalPhaseIon tail, after the abba-binary `enter` |
| `miniAB` | 96 (ct 80) | `3ab585348552415d` | A‖B joined, reading `enter` as a newline inside one blob |
| `inner96` | 96 (ct 80) | `b45a5e3d827593ca` | tail of the decrypted Phase-3.2 plaintext |
| `cosmic` | 1344 (ct 1328) | `2d3f6fe06dc950e6` | the "Cosmic Duality" block |

`inner96` is the primary authenticated target: it is the innermost lock reached by the
solved chain, and its ct length of 80 fits a 64-char hex private key plus a newline
(65 bytes → 80 padded).

## Pinned convention (3 positive controls)

Confirmed against all three publicly solved blobs:

```
openssl aes-256-cbc -a -d -pass pass:$(sha256hex "<human answer>")
```

i.e. EVP_BytesToKey with **SHA-256**, and the passphrase is the **lowercase SHA-256 hex of
the human answer**, not the answer itself ("sha b4"). Verified for `causality` (phase 2),
the phase-2.2 concatenation (phase 3), and `jacquefresco…` (phase 3.2). `neo/harness/aes_try.py`
self-tests all three on every run, so a negative from it is trustworthy.

Note phase-3.2's plaintext is only ~60% printable (it contains the EBCDIC section), so
acceptance rules must not assume fully printable output.

## Acceptance rule (false-positive control)

Accept only on strict PKCS#7 **and** (pad ≥ 4 — about 2⁻³² by chance — or a ≥4-byte magic
prefix, or high printability). Short magic prefixes and pad ∈ {1,2,3} fire constantly by
chance: an early looser rule produced 3 spurious "hits" in 75k trials. Any claimed solution
resting on a 1-byte pad should be treated as noise.

## Excluded (no verified hit)

Each candidate tried raw and as sha256hex / SHA256HEX / sha256², against all locks, across
EVP-MD5/SHA-1/SHA-256 at 128 and 256 bits plus raw-key mode:

- **Single tokens**: every decoded label, Matrix and Mr-Robot vocabulary, all known phase
  passwords, VIC/Beaufort output phrases, creator catchphrases.
- **Seven-component combinations**: full 7! orderings of the 2023-02-23 hint components
  (`yellow blue primes matrixsumlist lastwordsbeforearchichoice yinyang thepassword`),
  Dutch variants, long prime strings, multiple joiners, and "sha b4 ans too" structures
  (concatenated per-answer digests, 2- and 3-part). ~3.5M.
- **Two-token space**: all ordered pairs of a 55-word core vocabulary × 5 joiners. ~125k.
- **Matrix sum lists**: phase-0 grid row/column/ring/prime-indexed sums, letter-block sums
  at every divisor width, both digit mappings, several formats.
- **Letter-block derivations**: verbatim blocks, column-major transpositions, mod-9 and
  mod-26 Vigenère/Beaufort under puzzle keys, zeroed-out digit maps, separator segmentations.
- **Dictionary and numeric**: 370,105 English words (dwyl `words_alpha`), 10k most-common
  passwords, and every integer 0–999,999. ~9.0M.
- **Community claims**: the XOR-of-seven-token-hashes key (see
  `salphaseion_xor_token_hashes.md`), and issue #32's `april` /
  `sha256(gsmg101adressapril)` family.

## What this implies

Under the pinned convention, the passphrase for these locks is **not** a single English
word, a common password, a number below 10⁶, or any straightforward concatenation of the
known decoded labels. It is composite or derived — consistent with the Architect text's own
description ("seven intertwined passwords", "reinserting the prime basics") and with the
creator's established style of long concatenations hashed once.

The most promising untried direction is treating the repeated `shabef…` framing as a
*construction recipe* describing how to build the passphrase, rather than treating the
decoded labels as literal password material.
