# Pre-registration: the two-door structural comparison (2026-09-26), before any output is computed

**Status: REVISED after review; a second review of this revision is in progress; not run. No combination of the two
envelopes has been computed by anyone. The version that runs is the one committed with the status "frozen".**

Proposed by the user after tick 94. The draft (commit 2930875) was reviewed by two independent critics (statistics,
cryptography), both "sound with changes"; every blocking and should-fix item is resolved below. Topology of the two
locks only: no AES decrypt; no gate shot; no output, window or substring is ever used as a password, hashed into a
candidate, or sent to `gate.py`; no scalar is written anywhere.

## Question

The two terminal locks are a structural pair: `salph_inner` (SalPhaseIon's `miniA‖miniB`, the "another door" route)
and P32T (Phase 3.2's trailing envelope, the main route) (ticks 30, 44, 47; the HALF ↔ BETTER HALF and VIC ↔ DBBI
pairings). Each is a 96-byte OpenSSL envelope: the 8 bytes `Salted__`, an 8-byte salt, and 80 bytes (5 AES blocks) of
ciphertext. Does a complementarity ("yin-yang") combination of the two, byte for byte, carry an exact creator marker,
a key for a target address, a target address itself, or a nested envelope?

## Prior (stated before looking)

If both envelopes are genuine `openssl enc` outputs, each has its own salt and so its own key and IV (EVP_BytesToKey,
under any mode): there is no two-time pad, and every combination below is pseudorandom. The test therefore
discriminates one alternative, a **complementary door**: one envelope's bytes were built from the other's, either
fabricated (its 80 bytes are the other's ciphertext combined with a payload and dressed as a `Salted__` envelope, at no
cost to the creator) or ground (salts retried until a combination shows a marker). Grinding cost to plant a marker in
one chosen output, case-insensitive, at any offset, in any of its four reads: `HALF` ≈ 2^20 tries (seconds of work),
`YOUWON` ≈ 2^34, `YINYANG` ≈ 2^41 (at a fixed offset in exact case: 2^32, 2^48, 2^56). A key cannot be ground
(≈ 2^256); only a fabricated door can carry one. A null rejects only a complementary door that carries one of the exact
items below under the cells below.

## Inputs (byte-pinned; asserted by the script before anything else)

Paths are relative to the repository root.

- **A** (salph_inner): strip ASCII whitespace from `neo/materials/miniA.b64` and from `neo/materials/miniB.b64`,
  concatenate (miniA first), strict Base64-decode. 96 bytes, sha256
  `9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258`, salt `3ab585348552415d`.
  File sha256: miniA.b64 `d3d0a3e67a79a578c0887d719c594e6c7f26eddda5669114666d724620349f9e`,
  miniB.b64 `f4bebd3743b7f655836fb3da8b71e68d77e33c3ccae8e838bbcb651b869cd54d`.
- **B** (P32T): strip ASCII whitespace from `neo/materials/inner96.b64`, strict Base64-decode. 96 bytes, sha256
  `291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9`, salt `b45a5e3d827593ca`.
  File sha256: inner96.b64 `a31de4756889a4778ed76c19a4a5007e55dbfc6c65f2f4e865761b115e9a36cb`.

Both begin with the 8 bytes `Salted__`.

## Representations (2)

- **R1**: the full 96-byte envelopes (L = 96; six 16-byte blocks: header and salt, then the 5 ciphertext blocks).
- **R2**: the 80-byte ciphertexts, bytes 16–95 (L = 80; five blocks).

Every turn below acts on the representation (for R2, on the 80-byte string).

## The family (complete; nothing is added after looking)

Write X for A's representation and Y for B's. All arithmetic is per byte, mod 256.

**Operations (4):** `xor` X ⊕ Y; `sub` X − Y; `rsub` Y − X; `add` X + Y. XOR is the complement of agreement; the two
differences and the sum are the arithmetic complements (each part from the other, and the whole from both).

**Turns (5),** each an involution on a string S of length L, giving byte i of the turned string:
- `rev`: S[L−1−i]. The 180° turn of the envelope as a line of bytes.
- `bitrev`: m(S[L−1−i]), where m reverses the 8 bits of a byte: the whole bit string reversed. The same turn as a line
  of bits, and the creator's own practice: the "Good job, Neo!" key `13HGhj…` is the Phase-0 seed's 192 bits reversed
  (ledger: "the same 192 bits reversed (→ `13HGhj…`)").
- `hswap`: S[(i + L/2) mod L]. The 180° turn of the envelope laid on a circle, as the yin-yang is drawn: each half moves
  to where the other was. A 48-byte (3-block) rotation for R1, 40 bytes (2.5 blocks) for R2.
- `brev`: S[16·(L/16 − 1 − ⌊i/16⌋) + (i mod 16)]. The 16-byte blocks in reverse order, each block unchanged: the 180°
  turn at the cipher's own unit.
- `ibrev`: S[16·⌊i/16⌋ + 15 − (i mod 16)]. Each block reversed in place. Included because `rev` = `brev` ∘ `ibrev`, so
  the three byte-level reversals form a closed set.

**Cells (11 per representation and operation):** `id` (neither door turned); `A.g` = op(g(X), Y) and `B.g` =
op(X, g(Y)) for each turn g (one door turned). Either door may be turned because the yin-yang is symmetric in its
halves. For the four position turns, A.g = g(B.g), so the two differ only in windows that cross a seam; for `bitrev`
under the arithmetic operations they differ everywhere.

That is 2 × 4 × 11 = **88 outputs**. Label `<rep>/<op>/<cell>`, e.g. `R1/xor/id`, `R2/rsub/A.bitrev`. Canonical
order: rep R1, R2; op xor, sub, rsub, add; cell id, A.rev, B.rev, A.bitrev, B.bitrev, A.hswap, B.hswap, A.brev, B.brev,
A.ibrev, B.ibrev.

**Reads (4 per output), in this order:** `fwd` (the output); `rev` (byte i = Z[L−1−i]); `~fwd` and `~rev` (each byte
complemented, 255 − b: the yin-yang's colour swap). Complementing a door before combining is thereby covered exactly
for ⊕ and, for the arithmetic operations, in all but one case (~X − Y = ~(X + Y), X + ~Y = ~(Y − X),
~X + Y = ~(X − Y), ~Y − X = ~(X + Y)). The exception, X − ~Y = X + Y + 1, is a constant carry and is excluded with
carry arithmetic below. 352 reads in all.

## Detectors (exact; fixed now)

Every detector runs on every read, at every offset. Matching is over bytes; letters are ASCII only.

- **(a) marker:** any of these 17 strings, ASCII, case-insensitive with any mix of case: `HALF`; and `BETTERHALF`,
  `YINYANG`, `YINGYANG`, `YOUWON`, each also with exactly one separator from {space, `-`, `_`} between its two words
  (`BETTER HALF`, `YIN-YANG`, `YING_YANG`, `YOU WON`, …). `YINGYANG` is the creator's own spelling (#9599, 2023-08-06,
  "ying yang"; #39224, 2025-04-28, "yingyang"); `yinyang` is in the 2023-02-23 hint. A hit is reported by its upper-case
  form with its separator.
- **(b) raw key:** every 32-byte window at offsets 0…L−32, read as a big-endian integer k (the `rev` reads give the
  little-endian form). Valid only if 1 ≤ k ≤ n−1 (n the secp256k1 order); no reduction mod n; invalid windows are
  counted, not derived. For a valid k, hash160 = RIPEMD160(SHA256(·)) of the compressed (33-byte) and of the
  uncompressed (65-byte) public key is compared with the targets.
- **(b′) hex key:** every maximal run of bytes in [0-9A-Fa-f] of length ≥ 64; every 64-byte window of such a run,
  parsed as a big-endian hex integer, under the validity rule and comparison of (b).
- **(b″) WIF key:** every maximal run of Base58-alphabet bytes of length ≥ 51; every 51-byte window of such a run that
  begins with `5` and every 52-byte window that begins with `K` or `L`, if it Base58Check-decodes (checksum valid,
  version 0x80, a 32-byte payload, plus a trailing 0x01 for 52 characters): the payload under the rule and comparison of
  (b), both forms.
- **(c) nested envelope:** the exact 8 bytes `Salted__`, or the exact ASCII `U2FsdGVkX1` (its Base64 form). Reported,
  and the run stops; it is never decrypted.
- **(d) verbatim target:** a target's 20-byte hash160, or its 34-character Base58 address as ASCII (case-sensitive).

**Targets** (the house address oracle's set, `neo/harness/addr_check.py`), compared as hash160:

| address | role | hash160 |
|---|---|---|
| `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` | prize; an uncompressed-key address | `a9553269572a317e39f0f518cb87c1a0ee1dbae4` |
| `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` | better half | `4bc468447fe1b048ad030a2f9a125478eabc4ed6` |
| `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` | the creator's signed 1050-sat emission (tick 93) | `eb862e37998c1d077a6c0b46330bccb5f73427aa` |

Startup assertions: each address Base58Check-decodes (valid checksum, version 0x00) to its hash160; the 65-byte key
`04f4d1bb…` in `neo/materials/chain/tx_halving_spend.hex` hashes to `a9553269…`; the derivation of k = 1 gives
`1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH` (compressed) and `1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm` (uncompressed).

A **HIT** is any (a), (b), (b′), (b″), (c) or (d) event. Nothing else counts: not printable runs, not "looks like
English", not partial or split markers, not other words.

## Chance rates under the null (from the index structure only, before looking)

- **(a):** union bound 1.1 × 10⁻⁴ over the 352 reads; 6.1 × 10⁻⁵ after removing duplicate windows (A.g against B.g
  away from seams; R2 cells that repeat R1 byte pairings) and the fixed header bytes of the R1 `id` cells. `HALF` is all
  of it: the multi-word markers, separators included, total under 4 × 10⁻⁹ (`YOUWON` 3.8 × 10⁻⁹, `YINYANG` 3.0 × 10⁻¹¹,
  `YINGYANG` 2.4 × 10⁻¹³, `BETTERHALF` 1.5 × 10⁻¹⁷). A lone `HALF` is therefore weak evidence (about 1 in 16,000 by
  chance, about 2^20 tries to plant); it is still reported and still stops the run.
- **(b):** 20,064 raw windows × 2 forms × 3 targets ≈ 8 × 10⁻⁴⁴. **(b′), (b″):** a 64-byte hex run has chance ~10⁻⁶⁸ per
  offset and a 51-byte Base58 run ~10⁻³³. **(c):** about 2 × 10⁻¹⁵. **(d):** below 10⁻⁴³.

## Pinned constants

- **PRNG:** stream(tag, N) = the first N bytes of sha256(tag ‖ 00000000) ‖ sha256(tag ‖ 00000001) ‖ …, where tag is
  ASCII and the counter is 4 bytes big-endian.
- **Manifest:** one line per output in canonical order, `<label> <sha256 of the output's L bytes, lowercase hex>\n`;
  the manifest hash is the sha256 of the concatenated lines.
- **Detector digest:** sha256 over, for each output in canonical order, each read in the order fwd, rev, ~fwd, ~rev,
  and each offset 0…L−32 ascending, 40 bytes: hash160(compressed) ‖ hash160(uncompressed) for a valid window, or 40
  zero bytes for an invalid one. It is a hash of hash160s; no key material is recorded.
- **Expected coverage** (both implementations must report exactly this): 88 outputs; 352 reads; 30,976 bytes read;
  (a) 483,296 marker positions (Σ over the 17 strings and 352 reads of L − len + 1; `HALF` 29,920); (b) 20,064 raw
  windows; (d) 24,288 hash160 windows and 19,360 address positions per target (each target address has 34
  characters); (c) 28,512 `Salted__` and 27,808
  `U2FsdGVkX1` positions. Reported alongside: the count of invalid (b) windows and of (b′) and (b″) windows examined.

## Controls (run first, in the same process and code path; any failure aborts before the real inputs are combined)

1. **Per-cell positive controls, all 352 (output, read) pairs.** Control c = 4 × (output index) + (read index),
   c = 0…351. Synthetic A_c = `Salted__` ‖ stream("twodoor/ctl/A/c", 88), with c in decimal. The planted read
   P = stream("twodoor/ctl/P/c", L) carries:
   - the marker M = the (c mod 17)-th of the 17 strings, in the order `HALF`, then for each of `BETTER|HALF`,
     `YIN|YANG`, `YING|YANG`, `YOU|WON`: joined, then with space, `-`, `_`; case by c mod 3: upper, lower, or
     alternating lower/upper over its letters (`hAlF`);
   - the 32-byte test scalar t_c = (int(stream("twodoor/ctl/k/c", 32)) mod (n − 1)) + 1, big-endian.

   The read's free region is [0, L), except in the four R1 `id` cells, where the output's bytes 0–7 are fixed to
   op(`Salted__`, `Salted__`) so that the synthetic B carries the `Salted__` header (NUL bytes for xor, sub and rsub):
   there the free region is [8, L) for fwd and ~fwd reads and [0, L − 8) for rev and ~rev reads, and P's other bytes
   are set to match those fixed output bytes. With free region
   [f0, f1): for even c the marker sits at f0 and the scalar at f1 − 32 (the last window); for odd c the marker sits at
   f1 − len(M) (the last position) and the scalar at f0. The output Z is the preimage of P under the read; the synthetic
   B is solved by the inverse operation (for `id`: Y = inv(X, Z); for `B.g`: Y = g(inv(X, Z)); for `A.g`:
   Y = inv(g(X), Z); with inv = X ⊕ Z, X − Z, Z + X, Z − X for xor, sub, rsub, add). For R1 the synthetic B is Y; for
   R2 it is `Salted__` ‖ stream("twodoor/ctl/S/c", 8) ‖ Y, with X = A_c bytes 16–95.

   The target set is the three real targets plus one test target: hash160 of t_c's compressed key when c mod 4 is 0
   or 1, of its uncompressed key when it is 2 or 3. Pass: scanning that output reports the marker at (read, marker
   offset) and a (b) hit at (read, scalar offset) in the test target's form. Other reports in the output are allowed and
   logged.
2. **Per-detector controls.** For each (rep, op) pair p = 0…7 (p = 4 × rep index + op index, canonical order) and
   each plant type t = 0…6 (the test scalar as 64 lowercase hex characters; its compressed WIF, 52 characters; its
   uncompressed WIF, 51; `Salted__`; `U2FsdGVkX1`; the 20-byte hash160 of its compressed key; that key's P2PKH address
   as ASCII): a synthetic pair built as in 1 with the tags `twodoor/ctl2/{A,P,k,S}/p/t`, in the ((p + t) mod 11)-th cell
   and the ((p + t) mod 4)-th read, with the plant at f0 when p + t is even and at f1 − len(plant) when it is odd. The
   target set is the three real targets plus both hash160s of the test scalar. Pass: the matching detector reports the
   plant at that read and offset.
3. **Negative controls.** N1: A = `Salted__` ‖ stream("twodoor/neg/A", 88), B = `Salted__` ‖ stream("twodoor/neg/B",
   88), the full family with the real targets: no HIT, coverage exactly as pinned; its manifest hash and detector digest
   are recorded. N2 (near misses), each in its own synthetic pair, planted in the fwd read of `R1/xor/B.rev` as in 1,
   with the real targets: `HALG`; `HAL` as the last 3 bytes; `LF` as the first 2 bytes and `HA` as the last 2 (a marker
   split across the ends; no wrap-around); `YIN.YANG`; `YOU  WON`; raw windows equal to 0, n and 2^256 − 1 (counted
   invalid, not derived, no crash). Pass: nothing is reported in that output.
4. **Mutation check** (campaign script). Switches each disable one part of the scan: the rev reads; the complemented
   reads; the A-turned cells; R2's slicing (taken from byte 0); the compressed branch; the uncompressed branch; the last
   marker position; the last key window; case folding; scanning past a NUL byte; (b′); (b″); (c); (d); and each of the
   17 marker strings. With each switch on, controls 1–2 must fail; the real inputs are never scanned with a switch on.
   The table of switches and failing-control counts is recorded.
5. **Calibration** (campaign script). Over 10,000 pairs A = `Salted__` ‖ stream("twodoor/cal/A/i", 88), B likewise
   with `/B/`, count every case-insensitive occurrence of the proxy `HA` in all 352 reads. The analytic expectation
   from the index structure (fixed header bytes exact) is 1.869141 per pair, 18,691.4 in all. Pass:
   |observed − 18,691.4| ≤ 1,184 (5σ with a variance allowance of 3× for duplicated windows).

## Execution

- The campaign script `neo/harness/campaign_55_twodoor.py` runs: the startup assertions; controls 1–3; the mutation
  check; the calibration; then the real inputs, once. Development and debugging use synthetic data and hashes only;
  the real combination is computed only in the final run. A crash is fixed on synthetic data and the run is repeated
  with this file unchanged.
- A **second implementation**, written from this file alone without reading the first (no imports from
  `neo/harness`; an EC implementation other than coincurve), runs controls 1–3 and the real inputs.
- **Agreement required** on: the manifest hash, the coverage, the detector digest, N1's manifest hash and digest, the
  verdict, and the hit list. Any disagreement voids the run until explained on synthetic data.
- **Records:** `neo/attempts/campaign_55_twodoor.json` (this file's sha256, the script's sha256, input hashes, the
  manifest and its hash, coverage, the detector digest, N1's hash and digest, control, mutation and calibration
  results, the verdict, and hits); the second implementation's script and record alongside it. Output bytes are never
  written; only their sha256.

## Outcomes

- **HIT:** report the label, read, offset, detector, and the marker (or the encoding, form and target address),
  together with that detector's family-wise chance rate; stop; nothing further without the user. A key hit records
  only the label, read, offset, encoding, form and target address; the scalar is never printed or written. A nested
  envelope (c) is never decrypted.
- **NULL:** the closure below applies.
- **VOID:** a startup assertion, control, mutation or calibration check fails, or the implementations disagree. No
  verdict; debug on synthetic data or hashes only; rerun with this file unchanged.

## Closure

1. **Closed by this test on a null** (repeated in the NEXT_PASS row): the 88 outputs × 4 reads × detectors (a)–(d)
   exactly as above. In words: combining the two doors byte for byte by ⊕, −, − reversed or + (mod 256), with neither
   door turned or one door turned by `rev`, `bitrev`, `hswap`, `brev` or `ibrev`, in R1 or R2, read forward or reversed,
   plain or complemented, gives no marker from the list, no raw, hex or WIF key for the three targets, no verbatim
   target and no nested envelope.
2. **Excluded now, decided before looking** (not run, so not closed by the test; each would need its own
   pre-registration):
   - the Base64 text layer (symbol arithmetic mod 64; positional readings such as `+jkl`): it needs a splice and
     line-break rule, the mixed-rule problem of `+jkl`, and its own marker rule (a case-insensitive `HALF` there has a
     chance rate near 3 × 10⁻³);
   - hex-nibble arithmetic mod 16: identical to the byte family for ⊕, a carry variant otherwise;
   - carry and borrow arithmetic per block or over the whole string, and constant offsets (X + Y + 1, −Z = ~Z + 1):
     these differ from the byte operations only by carries;
   - EC arithmetic mod n on windows ("half + better half = whole" as keys): a key family, not a structural
     comparison; campaign 47 closed the combinations of the named halves, and the standing instruction keeps the
     multisig pubkeys out of any such campaign;
   - mod-26 letter readings of output bytes: the envelopes are bytes, not letters (`HALF` there near 10⁻²);
   - compositions of turns (e.g. `hswap` ∘ `rev`, or the per-byte bit mirror `bitrev` ∘ `rev`), turning both doors,
     other rotations and block shifts (e.g. by one block, CBC-style), and the full dihedral group: none is a single
     180° turn;
   - hash-derived keys (sha256 of an output as a brainwallet): outputs are never turned into candidates;
   - other words, near-spellings and printable runs.
3. **Reopening:** only new creator material (primary and authenticated) that names an operation, turn, representation
   or reading: one outside the cells above reopens the question for that item, and an excluded item named outright
   gets its own pre-registration. Community material, including the Telegram source of `137/143`, reopens nothing.

## Prior contact (disclosed)

- Tick 30 computed the pairwise XOR of the six salts, including 3ab585348552415d ⊕ b45a5e3d827593ca, which is bytes
  8–15 of `R1/xor/id`, and read it as not text. Those bytes stay in the scan.
- Campaign 50 put both salts into the MITM pool as integers (a ± b, a · b against the prize point): EC arithmetic,
  not a byte combination. Campaign 32 XORed last-word strings against each envelope separately. Tick 94's `+jkl` is a
  positional Base64 reading. None combined the two ciphertexts.
- Known before computing: bytes 0–7 of `R1/{xor,sub,rsub}/id` are 0x00 and those of `R1/add/id` are fixed
  (`Salted__` + `Salted__`); the R2 `id`, `A.ibrev` and `B.ibrev` outputs are the last 80 bytes of the R1 ones.

## Not part of this test

The `+jkl` positional reading (Base64 positions 31/73/137/143 on a joined 257-character object) is recorded as a
coincidence marker, not admissible: the `k` is forced by the `Salted__` header, the `+` is common to both doors, and
the reading needs a mixed line-break rule; its chance rate across the constructions in play is about 1 in 58
(tick 94). The derivation of `137/143` is missing and stays with community material until it traces to a creator
source.
