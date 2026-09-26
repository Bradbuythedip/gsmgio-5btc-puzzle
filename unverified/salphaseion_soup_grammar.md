# The SalPhaseIon soup grammar, from primary material

Working notes after checking the authenticated primary archive (raw page captures, verified
decrypts, and a 445-message creator transcript) rather than community writeups.

## Blob authenticity — verified

The Cosmic Duality envelope and the Phase-3.2 trailing envelope used in `neo/materials/`
are **byte-identical** to the primary captures:

- `cosmic_duality_envelope_1344B.bin` — 1344 B, salt `2d3f6fe06dc950e6`
- Phase-3.2 trailing envelope — 96 B, salt `b45a5e3d827593ca`, at offset 2292 of the
  2422-byte plaintext

This matters because the Cosmic blob originally came into this work from an untrusted
LLM-generated repo. It is authentic.

## The soup structure

Per the archive, the SalPhaseIon page holds, inside one `<textarea>`, a space-separated
symbol soup, followed by `<h1>Cosmic Duality</h1>` and a second `<textarea>` with the
contiguous Cosmic envelope. The soup's parts, in order:

```
dbbi (91 symbols)  |  bin1 = "matrixsumlist"
faed (570 symbols) |  agda = "lastwordsbeforearchichoice"
                      cfob = "thispassword"
                      bin2 = "enter"
                      salph_inner envelope, salt 3ab585348552415d
```

Every symbol *and* every base64 character of the inner envelope is written with a space
after it, and the 40-symbol a/b block (`enter`) is **spliced into the base64 at a `z`**.
So the inner envelope is reconstructed by removing the spliced block and rejoining — 128
base64 characters, 96 bytes, salt `3ab585348552415d`. There are therefore **two** 96-byte
envelopes in play: this one and the Phase-3.2 one.

## Corrections to the common reading

**`yinyang` is an output, not a password input.** Creator, 2025-04-28, answering "is yinyang
found after decoding an AES ciphertext?" — *"It's the next phase, but I await the day someone
finally gets there."* And 2023-08-06: *"Once you hit a 'ying yang', you'll be able to solve it
the same day."* So `yinyang` is what you should *see* after a correct decryption. Feeding it
in as a password component (which many attempts, including earlier ones here, have done) is
backwards.

**The prime hint is the `matrixsumlist` hint.** Asked directly for a hint on matrixsumlist
(2021-03-14), the creator replies *"I gave an unforseen hint already"*, pointing back at
2021-03-01, which was itself a reply to a solver asking **which primes, 2/3/5/7, to use**:
*"You are at the prime part already???"* — immediately followed by *"Oh wait, shouldn't have
said that."* Combined with Christmas 2021 (*"prime numbers ... required to proceed ...
along the way, some characters need to be zeroed out"*), the construction is: **zero out
characters at prime-derived positions, then sum the matrix.**

**The 2023-02-23 master hint** decodes (bit- then byte-reversed) to four components followed
by commentary:
`yellowblueprimes matrixsumlist lastwordsbeforearchichoice yinyang` /
`wewontgiveawaythepassword` / `itsinfrontofyoureyesbutyourenotseeingit` /
`verylaststepisatruegiveawaypromised`.
With yinyang as output, that leaves **three** inputs, not seven.

## dbbi and faed are high-entropy data, not encoded English

Tested whether `faed` encodes text (e.g. the Architect speech) as 285 symbol-pairs in
base-81. It does not, and the reason is structural rather than a failed key guess:

| | distinct | frequency profile (top 10) |
|---|---|---|
| faed pairs | 75 of 81 | 13, 10, 9, 7, 7, 7, 7, 6, 6, 6 |
| English text of same length | 26 | 34, 28, 26, 24, 23, 18, 16, 13, 13, 13 |

faed's pair distribution is near-uniform; English is steeply skewed. No substitution or
homophonic map can bridge those profiles. So `faed` (570 base-9 symbols ≈ 226 bytes) and
`dbbi` (91 symbols ≈ 36 bytes) carry **high-entropy data** — ciphertext or compressed
payload — not enciphered prose. Any theory that decodes them to readable English by choosing
a mapping is fitting noise.

## Tested and negative

`neo/harness/campaign_14.py` builds matrixsumlist candidates from prime-derived zero masks
(zero-at-prime-position, keep-only-prime, prime columns, prime rows, columns in {2,3,5,7},
row∧column prime, plus an unmasked control) across all seven 7×13 matrices, both digit bases,
row and column axes, eight renderings — 2016 sum-list candidates. Each was tried alone and
wrapped in the other two authenticated components (`yellowblueprimes` variants and
`lastwordsbeforearchichoice` candidates), raw and hashed. **16.6M trials, no hit.**

## Where that leaves it

The recipe's *shape* is now creator-authenticated (three inputs; primes and zeroing drive
matrixsumlist; yinyang is the checkpoint you should see). What is still missing is the exact
zero-mask and the exact sum rendering. Since dbbi/faed are high-entropy, the sum list is
likely not meant to be read as text at all — it is more likely consumed directly as key
material, which is consistent with `itsinfrontofyoureyesbutyourenotseeingit`.

A correct guess is self-proving: it decrypts one of the two 96-byte envelopes and should
surface a yin-yang. Nothing short of that should be treated as progress.
