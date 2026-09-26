# Pre-registration: the two-door structural comparison (2026-09-26), before any output is computed

**Status: DRAFT under independent review; not run. The reviewed version is committed before any output is computed.**

Proposed by the user after tick 93; recorded before running. Topology of the two locks only: no AES decrypt, no gate
shot, no password derived from any output, nothing written to the repo that could act as a key.

## Question

The two terminal locks are a structural pair: `salph_inner` (SalPhaseIon, `miniA‖miniB`) and P32T (Phase 3.2's trailing
envelope), each a 96-byte OpenSSL `Salted__` envelope (16-byte header + salt, 80 bytes of ciphertext), at the end of the
"another door" and main routes respectively (ledger ticks 30, 44; the HALF ↔ BETTER HALF, VIC ↔ DBBI pairing). Does a
complementarity ("yin-yang") combination of the two envelopes, byte for byte, carry an exact creator marker or a key?

Prior, stated before looking: the envelopes were encrypted under different salts, hence different keys and IVs, so any
bytewise combination of their ciphertexts is uniformly random under every sound construction. A creator could plant a
short marker only by grinding salts (about 2^32 tries for 4 bytes; 2^56 for 7). The test is run because it is cheap,
its false-positive rate is negligible, and a null closes the question.

## Inputs (byte-pinned)

- `A` = base64-decode(`materials/miniA.b64` ‖ `materials/miniB.b64`), 96 bytes, sha256 `9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258`,
  salt `3ab585348552415d`. File sha256: miniA.b64 `d3d0a3e6…9f9e`, miniB.b64 `f4bebd37…d54d`.
- `B` = base64-decode(`materials/inner96.b64`), 96 bytes, sha256 `291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9`,
  salt `b45a5e3d827593ca`. File sha256: inner96.b64 `a31de475…36cb`.

Two representations, both fixed now: **R1** the full 96-byte envelopes; **R2** the 80-byte ciphertexts (bytes 16–95).

## Operations (the complete list; nothing is added after looking)

For each representation, with X from A and Y from B:
- **operations** (3): `X ⊕ Y`, `(X − Y) mod 256`, `(Y − X) mod 256`, byte by byte;
- **orientations of Y** (4): as is; byte-reversed (the yin-yang's 180° turn); AES-block-reversed (the 16-byte blocks in
  reverse order, bytes within a block kept); half-swapped (rotated by half its length).

That is 3 × 4 × 2 = **24 outputs** (96 or 80 bytes each). Each output is read forward and byte-reversed.

## Acceptance (exact; fixed now)

A **HIT** is either of:
- **(a) an exact marker:** the case-insensitive ASCII string `YINYANG`, `YOUWON`, `BETTERHALF` or `HALF` anywhere in any
  output, read forward or reversed;
- **(b) a key:** any 32-byte window of any output, at any offset, that is a valid secp256k1 scalar whose compressed or
  uncompressed P2PKH address is the prize `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` or the better half
  `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa`.

Nothing else counts: not printable runs, not "looks like English", not partial markers, not other words.

Chance rates under the null, computed before looking: (a) about 1.5 × 10⁻⁵ over the whole family (dominated by `HALF`);
(b) 1,368 windows × 2 encodings × 2 addresses, about 4 × 10⁻⁴⁵.

## Controls (must pass, or the run does not count)

- Positive: the same code, given `Y' = X ⊕ M` where M plants `HALF` at a known offset, reports that marker at that offset
  for the XOR / as-is output; given a window equal to a known test scalar and that scalar's own address as the target, it
  reports the key.
- Negative: the same code over a seeded random pair of 96-byte strings with fixed `Salted__` headers reports no HIT.

## Execution

A campaign script computes the 24 outputs and records only each output's sha256 (not its bytes) plus the verdict. A
second, independent implementation, written without reading the first, must produce the same 24 hashes and the same
verdict; any disagreement voids the run until explained.

## Outcomes

- **HIT:** report it with the operation, orientation, representation and offset; stop; nothing further without the user.
- **Null:** the two-door bytewise comparison closes: these operations and orientations, and variants of them, are not
  rerun without new creator material that names an operation. The HALF ↔ BETTER HALF pairing remains the model; this
  closes only the reading that the pair is combined byte for byte.

The `+jkl` positional reading (Base64 positions 31/73/137/143 on a joined 257-character object) is **not** part of this
test. It is recorded as a coincidence marker, not admissible: the `k` is forced by the `Salted__` header, the `+` is
common to both doors, and the reading needs a mixed line-break rule; its chance rate across the constructions in play is
about 1 in 58 (tick 94). The derivation of `137/143` is missing and stays with community material until it traces to a
creator source.
