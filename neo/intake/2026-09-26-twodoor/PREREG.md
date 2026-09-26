# Pre-registration: the two-door structural comparison (2026-09-26), before any output is computed

**Status: REVIEWED (two rounds) and frozen at this commit; not run. No combination of the two ciphertexts has been
computed in this project before this commit (the salt XOR of tick 30 is disclosed under Prior contact).**

Proposed by the user after tick 94. The draft (commit 2930875) was reviewed by two critics (statistics, cryptography),
and the revision (commit 9d90c55) by two more (statistics and resolution; implementability, with a prototype written
from the text alone). Every blocking and should-fix item of both rounds is resolved below. Topology of the two locks
only: no AES decrypt; no gate shot; no output, window or substring is ever used as a password, hashed into a candidate,
or sent to `gate.py`; no scalar is written anywhere.

## Question

The two terminal locks are a structural pair: `salph_inner` (SalPhaseIon's `miniA‖miniB`, the "another door" route)
and P32T (Phase 3.2's trailing envelope, the main route) (ticks 30, 46, 47; the HALF ↔ BETTER HALF and VIC ↔ DBBI
pairings). Each is a 96-byte OpenSSL envelope: the 8 bytes `Salted__`, an 8-byte salt, and 80 bytes (5 AES blocks) of
ciphertext. Does a complementarity ("yin-yang") combination of the two, byte for byte, carry an exact creator marker,
a key for a target address, a target address itself, or a nested envelope? The user's "blockwise XOR" is read as the
aligned XOR (block i with block i), which is the bytewise XOR; XOR of blocks shifted against each other is excluded
below.

## Prior (stated before looking)

If both envelopes are genuine `openssl enc` outputs, each has its own salt and so its own key and IV (EVP_BytesToKey,
under any mode): there is no two-time pad, and every combination below is pseudorandom. The test therefore
discriminates one alternative, a **complementary door**: one envelope's bytes were built from the other's, either
fabricated (its 80 bytes are the other's ciphertext combined with a payload and dressed as a `Salted__` envelope, at no
cost to the creator) or ground (salts retried until a combination shows a marker). Grinding cost to plant a marker in
one chosen output, case-insensitive, at any offset, in any of its six reads: `HALF` ≈ 2^19 tries (seconds of work),
`YOUWON` ≈ 2^33, `YINYANG` ≈ 2^40 (at a fixed offset in exact case: 2^32, 2^48, 2^56). A key cannot be ground
(≈ 2^256); only a fabricated door can carry one. A null rejects only a complementary door that carries one of the exact
items below under the cells below.

## Inputs (byte-pinned; asserted by both implementations before anything else)

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

Write X for A's representation and Y for B's. All arithmetic is per byte, mod 256. m(v) reverses the 8 bits of a byte.

**Operations (4):** `xor` X ⊕ Y; `sub` X − Y; `rsub` Y − X; `add` X + Y. XOR is the complement of agreement; the two
differences and the sum are the arithmetic complements (each part from the other, and the whole from both).

**Turns (5),** each an involution on a string S of length L, giving byte i of the turned string:
- `rev`: S[L−1−i]. The 180° turn of the envelope as a line of bytes.
- `bitrev`: m(S[L−1−i]): the whole bit string reversed. The same turn as a line of bits, and the creator's own
  practice: the "Good job, Neo!" key `13HGhj…` is the Phase-0 seed's 192 bits reversed (ledger: "the same 192 bits
  reversed (→ `13HGhj…`)"); the house oracle carries it as `bitrev`.
- `hswap`: S[(i + L/2) mod L]. The 180° turn of the envelope laid on a circle, as the yin-yang is drawn: each half moves
  to where the other was. A 48-byte (3-block) rotation for R1, 40 bytes (2.5 blocks) for R2.
- `brev`: S[16·(L/16 − 1 − ⌊i/16⌋) + (i mod 16)]. The 16-byte blocks in reverse order, each block unchanged: the 180°
  turn at the cipher's own unit.
- `ibrev`: S[16·⌊i/16⌋ + 15 − (i mod 16)]. Each block reversed in place. Included because `rev` = `brev` ∘ `ibrev`, so
  the three byte-level reversals form a closed set.

**Cells (11 per representation and operation):** `id` (neither door turned); `A.g` = op(g(X), Y) and `B.g` =
op(X, g(Y)) for each turn g (one door turned). Either door may be turned because the yin-yang is symmetric in its
halves. For the four position turns, A.g = g(B.g), so the two differ only in windows that cross a seam; for `bitrev`
they differ everywhere except under ⊕.

That is 2 × 4 × 11 = **88 outputs**. Label `<rep>/<op>/<cell>`, e.g. `R1/xor/id`, `R2/rsub/A.bitrev`. Canonical
order: rep R1, R2; op xor, sub, rsub, add; cell id, A.rev, B.rev, A.bitrev, B.bitrev, A.hswap, B.hswap, A.brev, B.brev,
A.ibrev, B.ibrev.

**Reads (6 per output), in this order:** `fwd` (the output Z); `rev` (byte j = Z[L−1−j]); `bitrev` (byte j =
m(Z[L−1−j]): the output read as a bit string backwards, the creator's key form above); then `~fwd`, `~rev`, `~bitrev`,
each of those with every byte complemented (255 − b: the yin-yang's colour swap). 528 reads in all.

Complementing a door before combining is thereby covered exactly for ⊕, and for the arithmetic operations for every
function but one: ~X − Y = ~(X + Y), X + ~Y = ~(Y − X), ~X + Y = ~(X − Y), ~Y − X = ~(X + Y). The exceptions,
X − ~Y and Y − ~X (both X + Y + 1) and ~X + ~Y = ~(X + Y + 1), are constant carries and are excluded with carry
arithmetic below. Turning both doors is partly covered: `rev` on both doors is the `rev` read of `id`, and `bitrev` on
both under ⊕ is the `bitrev` read of `xor/id`; the rest is excluded below.

## Detectors (exact; fixed now)

Every detector runs on every read, at every offset. Strings and windows never wrap around the end of a read. Letters
are ASCII only. Detector names in records are ASCII: `a`, `b`, `b_hex`, `b_wif`, `c`, `d`.

- **a (marker):** any of these 17 strings, ASCII, case-insensitive with any mix of case: `HALF`; and `BETTERHALF`,
  `YINYANG`, `YINGYANG`, `YOUWON`, each also with exactly one separator from {space, `-`, `_`} between its two words
  (`BETTER HALF`, `YIN-YANG`, `YING_YANG`, `YOU WON`, …). `YINGYANG` is the creator's own spelling (#9599, 2023-08-06,
  "ying yang"; #39224, 2025-04-28, "yingyang"); `yinyang` is in the 2023-02-23 hint. Every occurrence of every string
  is its own event, so a `HALF` inside a `BETTER…HALF` is listed separately.
- **b (raw key):** every 32-byte window at offsets 0…L−32, read as a big-endian integer k (the `rev` and `bitrev` reads
  give the little-endian and bit-reversed forms). Valid only if 1 ≤ k ≤ n−1 (n the secp256k1 order); no reduction mod
  n; invalid windows are counted, not derived. For a valid k, hash160 = RIPEMD160(SHA256(·)) of the compressed (33-byte)
  and of the uncompressed (65-byte) public key is compared with the targets.
- **b_hex (hex key):** every maximal run of bytes in [0-9A-Fa-f] of length ≥ 64; every 64-byte window of such a run,
  parsed as a big-endian hex integer, under the validity rule and comparison of b.
- **b_wif (WIF key):** every maximal run of bytes in the Bitcoin Base58 alphabet
  (`123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`) of length ≥ 51; every window of such a run that is 51
  bytes long and whose first byte is `5`, and every one that is 52 bytes long and whose first byte is `K` or `L`, is
  examined; it decodes if it is valid Base58Check with version 0x80 and a 32-byte payload (plus a trailing 0x01 for 52
  characters); a decoded payload is taken under the validity rule and comparison of b (both forms).
- **c (nested envelope):** the exact 8 bytes `Salted__`, or the exact ASCII `U2FsdGVkX1` (its Base64 form). Reported;
  never decrypted.
- **d (verbatim target):** a target's 20-byte hash160, or its Base58 address as ASCII at its own length (34 characters
  for each real target; a test target's address may have 33), case-sensitive.

**Targets** (the house address oracle's set, `neo/harness/addr_check.py`), compared as hash160, in this table order:

| address | role | hash160 |
|---|---|---|
| `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` | prize; an uncompressed-key address | `a9553269572a317e39f0f518cb87c1a0ee1dbae4` |
| `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` | better half | `4bc468447fe1b048ad030a2f9a125478eabc4ed6` |
| `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` | the creator's signed 1050-sat emission (tick 93) | `eb862e37998c1d077a6c0b46330bccb5f73427aa` |

**Startup assertions:** each address Base58Check-decodes (valid checksum, version 0x00) to its hash160; the 65-byte key
(the 130 hex digits beginning `04f4d1bb` at their first occurrence in `neo/materials/chain/tx_halving_spend.hex`; all
three occurrences are equal) hashes to `a9553269572a317e39f0f518cb87c1a0ee1dbae4`; k = 1 gives
`1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH` (compressed) and `1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm` (uncompressed); the turns
reproduce the known answers under Pinned constants.

A **HIT** is any a, b, b_hex, b_wif, c or d event. A b, b_hex or b_wif event is a target match; a hex run, Base58 run
or decodable WIF without a match is only counted. Nothing else counts: not printable runs, not "looks like English",
not partial or split markers, not other words.

**The scan always completes.** Whatever it finds, every detector runs on all 88 outputs, all 6 reads and every offset;
the coverage and the detector digest are always complete, and every event is listed. Controls follow the same rule.
A HIT changes only what happens after both implementations have run and been compared (see Outcomes).

## Chance rates under the null (from the index structure only, before looking)

- **a:** union bound 1.7 × 10⁻⁴ over the 528 reads; 9.6 × 10⁻⁵ after removing every window that is an identical byte
  function of another (A.g against B.g away from seams; R2 cells that repeat R1 byte pairings; R1 `brev` and `hswap`,
  which coincide on blocks 1 and 4; bit-mirrored ⊕ reads, since m(a ⊕ b) = m(a) ⊕ m(b)) and the fixed header bytes of
  the R1 `id` cells. `HALF` is all of it: the multi-word markers, separators included, total 6 × 10⁻⁹ (`YOUWON`
  6.0 × 10⁻⁹, `YINYANG` 4.7 × 10⁻¹¹, `YINGYANG` 3.7 × 10⁻¹³, `BETTERHALF` 2.3 × 10⁻¹⁷). A lone `HALF` is therefore weak
  evidence (about 1 in 10,400 by chance, about 2^19 tries to plant); it is still reported and is still a HIT.
- **b:** 30,096 raw windows × 2 forms × 3 targets ≈ 1.2 × 10⁻⁴³. **b_hex, b_wif:** a 64-byte hex run has chance
  ~10⁻⁶⁸ per offset and a 51-byte Base58 run ~10⁻³³. **c:** 2.3 × 10⁻¹⁵. **d:** below 10⁻⁴³.

## Pinned constants

- **PRNG:** stream(tag, N) = the first N bytes of sha256(tag ‖ 00000000) ‖ sha256(tag ‖ 00000001) ‖ …, where tag is
  ASCII (numbers in it are decimal) and the counter is 4 bytes big-endian. int(·) of PRNG bytes is big-endian.
- **Known answers** for the turns: sha256 of the turn of S = the bytes 00 01 … (L−1).
  - L = 96: `rev` b2d9996f81492a827ed4fe7c36ff83960b49071835fd1dda377d80497f5360df; `bitrev`
    4632963b5ac8fc1bef565eb9a26f164b586d6961fe674f05811f3236e17a81a7; `hswap`
    d41d559270b9ee078d6d46f1f63547172173b3ba1df4f00c77bde438807dbf98; `brev`
    ec518b4bfd733a0b679f60768ae1802cad302ec9ca1670d2a43866e97633b4e9; `ibrev`
    dedc02e27b32f48b38a0705180e635b0fbded4983e32581306a140280a2574a2.
  - L = 80: `rev` 939fc6c065bfdd55219a2fc10652ae08c8b92c4df7d4ff5f5b28706b263d803e; `bitrev`
    b42ad22f5cb8a8652f6f0c3aa05bb765c4daf36c427fb08677dfd31d79a52b0f; `hswap`
    686bd663b458f24f9971da499ef56a2aa4f741b668bb1e17f3b93d5be4ce9034; `brev`
    ed2ad0fa3e299e35c3d6c35d0c8fca853a00b7abdd55312fa72d73819e58f7d1; `ibrev`
    b0c9caac8dc07824d1486ab900ff61d19e912d2ad21197bec3577b0f1a20c36e.
- **Manifest:** one line per output in canonical order, `<label> <sha256 of the output's L bytes, lowercase hex>\n`;
  the manifest hash is the sha256 of the concatenated lines.
- **Detector digest:** sha256 over, for each output in canonical order, each read in the order fwd, rev, bitrev, ~fwd,
  ~rev, ~bitrev, and each offset 0…L−32 ascending, 40 bytes: hash160(compressed) ‖ hash160(uncompressed) for a valid
  window, or 40 zero bytes for an invalid one. It is a hash of hash160s; no key material is recorded.
- **Hit list:** one entry per match, the tuple (label, read, detector, offset, item), where offset is the 0-based index
  in that read where the string or window starts. item is, for a, the marker's upper-case form with its separator; for
  b and b_hex, `<form>:<address>` with form `compressed` or `uncompressed`; for b_wif, `<form>:<address>:<51|52>`; for
  c, the matched string; for d, `hash160:<address>` or `address:<address>`. Identical bytes found in two cells are each
  listed. Entries are sorted by output (canonical order), read (the order above), detector (a, b, b_hex, b_wif, c, d),
  offset, then marker index in the 17-list, form (compressed first), kind (hash160 first) and target (table order).
- **Coverage record**, these integers in this order, all compared: outputs; reads; bytes read; a positions (Σ over the
  17 strings and all reads of L − len + 1); a positions of `HALF`; b windows; b invalid windows; b_hex windows (every
  64-byte window inside a qualifying run, valid or not); b_hex invalid windows; b_wif windows examined; b_wif windows
  that decode; d hash160 windows; d address positions for each target in table order (three numbers); c `Salted__`
  positions; c `U2FsdGVkX1` positions. Pinned values for the whole family: 88; 528; 46,464; 724,944; 44,880; 30,096;
  (data); (data); (data); (data); (data); 36,432; 29,040; 29,040; 29,040; 42,768; 41,712.
- **N1** (below): manifest hash `a5103f89230d11dbfba3fe688a8a2482957820a24954f454e516deb843a96233` (the outputs do not
  depend on the reads; reproduced by two implementations and a formula-literal family). Its detector digest is compared
  between the two implementations before either combines the real inputs.

## Controls (run first, in the same process and code path; with every switch off, any failure aborts before the real inputs are combined)

1. **Per-cell positive controls, all 528 (output, read) pairs.** Control c = 6 × (output index) + (read index),
   c = 0…527. Synthetic A_c = `Salted__` ‖ stream("twodoor/ctl/A/c", 88). The planted read P = stream("twodoor/ctl/P/c",
   L) carries:
   - the marker M = the (c mod 17)-th (0-based) of the 17 strings, in the order `HALF`, then for each of `BETTER|HALF`,
     `YIN|YANG`, `YING|YANG`, `YOU|WON`: joined, then with space, `-`, `_`; case by c mod 3: 0 upper, 1 lower, 2
     alternating over its letters only, counted from 0 (even lower, odd upper; separators keep their place: `hAlF`);
   - the 32-byte test scalar t_c = (int(stream("twodoor/ctl/k/c", 32)) mod (n − 1)) + 1, big-endian.

   The free region is [0, L), except in the four R1 `id` cells: there the output's bytes 0–7 are fixed to
   op(`Salted__`, `Salted__`), P's bytes outside the free region are the read of those fixed output bytes, the synthetic
   B begins with `Salted__` (asserted), and the free region is [8, L) for the fwd and ~fwd reads and [0, L − 8) for the
   other four. With free region [f0, f1): for even c the marker sits at f0 and the scalar at f1 − 32 (the last window);
   for odd c the marker sits at f1 − len(M) (the last position) and the scalar at f0. The output Z is the preimage of P
   under the read; the synthetic B is solved by the inverse operation (for `id`: Y = inv(X, Z); for `B.g`:
   Y = g(inv(X, Z)); for `A.g`: Y = inv(g(X), Z); with inv = X ⊕ Z, X − Z, Z + X, Z − X for xor, sub, rsub, add). For R1
   the synthetic B is Y; for R2 it is `Salted__` ‖ stream("twodoor/ctl/S/c", 8) ‖ Y, with X = A_c bytes 16–95.
   The scanned output is recomputed from (A_c, B_c) by the same family code as the real inputs, never taken from Z.

   The target set is the three real targets plus one test target: hash160 of t_c's compressed key when c mod 4 is 0
   or 1, of its uncompressed key when it is 2 or 3. Pass: the hit list of that output contains (label, read, `a`,
   marker offset, M's upper-case form) and (label, read, `b`, scalar offset, `<form>:<test address>`) in the test
   target's form. Other entries are allowed.
2. **Per-detector controls.** For each (rep, op) pair p = 0…7 (p = 4 × rep index + op index, canonical order) and
   each plant type t = 0…6 (the test scalar as 64 lowercase hex characters; its compressed WIF, 52 characters; its
   uncompressed WIF, 51; `Salted__`; `U2FsdGVkX1`; the 20-byte hash160 of its compressed key; that key's P2PKH address
   as ASCII): a synthetic pair built as in 1 with the tags `twodoor/ctl2/{A,P,k,S}/p/t`, in the ((p + t) mod 11)-th
   cell and the ((p + t) mod 6)-th read, with the plant at f0 when p + t is even and at f1 − len(plant) when it is odd.
   P carries only the plant (no marker and no scalar from 1). The target set is the three real targets plus both
   hash160s of the test scalar. Pass: the matching detector (b_hex, b_wif, b_wif, c, c, d, d) reports the plant at that
   read and offset (for c the planted string; for d `hash160:` or `address:` with the compressed key's address).
3. **Negative controls.** The `Salted__` header assertion applies to the real inputs, N1 and the calibration pairs;
   synthetic B of controls and near misses are solved and need not carry it (except the R1 `id` cells above).
   - **N1:** A = `Salted__` ‖ stream("twodoor/neg/A", 88), B = `Salted__` ‖ stream("twodoor/neg/B", 88), the full family
     with the real targets: no HIT, coverage exactly as pinned, manifest hash as pinned; its detector digest is recorded
     and compared.
   - **N2 (near misses):** eight pairs j = 0…7, in this order: `HALG`; `HAL` as the last 3 bytes; `LF` as the first 2
     bytes and `HA` as the last 2; `YIN.YANG`; `YOU  WON` (two spaces); a raw window equal to 0; one equal to n; one
     equal to 2^256 − 1. Each is built as in 1 for output `R1/xor/B.rev`, read fwd, with tags `twodoor/neg2/A/j` and
     `twodoor/neg2/P/j` and no marker or scalar from 1. Strings are upper case at offset 0 unless a position is given;
     raw windows are 32 bytes big-endian at offset 0. Real targets. Pass: nothing is reported in that output, and for
     j = 5, 6, 7 the fwd-read window at offset 0 is counted invalid and not derived. Other invalid windows in that
     output are expected and allowed.
4. **Mutation check** (campaign script). Switches each disable one part of the scan: the rev reads; the bitrev reads;
   the complemented reads; the A-turned cells; R2's slicing (taken from byte 0); the compressed branch; the uncompressed
   branch; the last marker position; the last key window; case folding; scanning past a NUL byte; b_hex; b_wif; c; d;
   and each of the 17 marker strings. With each switch on, at least one control of 1–2 must fail (not necessarily one
   of each); the real inputs are never scanned with a switch on. The table of switches and failing-control counts is
   recorded.
5. **Calibration** (campaign script). For i = 0…9999, A = `Salted__` ‖ stream("twodoor/cal/A/i", 88) and B likewise
   with `/B/`: count every case-insensitive occurrence of the proxy `HA` in all 528 reads. The analytic expectation
   from the index structure (fixed header bytes exact) is 2867/1024 = 2.7998 per pair, 27,998.05 in all. Pass:
   |observed − 27,998.05| ≤ 1,449 (5σ with a variance allowance of 3× for duplicated windows; the measured
   variance-to-mean ratio on other pairs is 2.4).

## Execution

- The campaign script `neo/harness/campaign_55_twodoor.py` runs: the startup assertions; controls 1–3; the mutation
  check; the calibration; then the real inputs, once. Development and debugging use synthetic data and hashes only.
  A crash is fixed on synthetic data and the run is repeated with this file unchanged.
- A **second implementation**, written from this file alone without reading the first (no imports from
  `neo/harness`; an EC implementation other than coincurve), runs the startup assertions, controls 1–3 and N1.
- **Order:** both implementations first complete their checks and N1; their N1 manifest hashes and detector digests are
  compared; only when they agree does either combine the real inputs (each takes the other's N1 digest as an argument
  and refuses the real inputs on a mismatch). Both then run the real inputs, whatever either finds. If N1 disagrees
  because this text is ambiguous, the text may be clarified before either implementation combines the real inputs; the
  clarification is committed and recorded in the ledger. Once the real inputs are combined, nothing in this file
  changes.
- **Agreement required** on: the manifest hash, the coverage record, the detector digest, N1's manifest hash and
  digest, the verdict, and the hit list. Any disagreement voids the run until explained on synthetic data.
- **Records:** `neo/attempts/campaign_55_twodoor.json` (this file's sha256, the script's sha256, input hashes, the
  manifest and its hash, the coverage record, the detector digest, N1's hash and digest, control, mutation and
  calibration results, the verdict, and the hit list); the second implementation's script and record alongside it.
  Output bytes are never written; only their sha256.

## Outcomes

- **HIT:** each entry is reported with its detector's chance rate from the section above (for a, its marker's
  effective rate, `HALF` 9.6 × 10⁻⁵; b, b_hex, b_wif 1.2 × 10⁻⁴³; c 2.3 × 10⁻¹⁵; d 10⁻⁴³; the quoted rates are not part
  of the agreement). Once both implementations have run and been compared, nothing further is done (no decrypt, no
  follow-up test) without the user. A key hit records only the label, read, offset, encoding, form and target address;
  the scalar is never printed or written. A nested envelope (c) is never decrypted.
- **NULL:** the closure below applies.
- **VOID:** a startup assertion, control, mutation or calibration check fails, N1 disagrees, or the implementations
  disagree. No verdict; debug on synthetic data or hashes only; rerun with this file unchanged.

## Closure

1. **Closed by this test on a null** (repeated in the NEXT_PASS row): the 88 outputs × 6 reads × detectors a–d
   exactly as above. In words: combining the two doors byte for byte by ⊕, −, − reversed or + (mod 256), with neither
   door turned or one door turned by `rev`, `bitrev`, `hswap`, `brev` or `ibrev`, in R1 or R2, read forward, reversed or
   bit-reversed, plain or complemented, gives no marker from the list, no raw, hex or WIF key for the three targets, no
   verbatim target and no nested envelope.
2. **Excluded now, decided before looking** (not run, so not closed by the test; each would need its own
   pre-registration):
   - the Base64 text layer (symbol arithmetic mod 64; positional readings such as `+jkl`): it needs a splice and
     line-break rule, the mixed-rule problem of `+jkl`, and its own marker rule (a case-insensitive `HALF` over a
     comparable family there is expected by chance at several per cent);
   - other byte slicings: the 88-byte salt plus ciphertext, the salts alone, single blocks;
   - hex-nibble arithmetic mod 16: identical to the byte family for ⊕, a carry variant otherwise;
   - carry and borrow arithmetic per block or over the whole string, and constant offsets (X + Y + 1, −Z = ~Z + 1):
     these differ from the byte operations only by carries;
   - other bytewise operations (AND, OR, products, averages);
   - EC arithmetic mod n on windows ("half + better half = whole" as keys): a key family, not a structural
     comparison; campaign 47 closed the combinations of the named halves, and the standing instruction keeps the
     multisig pubkeys out of any such campaign;
   - mod-26 letter readings of output bytes: the envelopes are bytes, not letters (`HALF` there is expected by chance
     at several per cent);
   - per-byte turns other than inside `bitrev` (the per-byte bit mirror `bitrev` ∘ `rev`, the nibble swap);
     compositions of two turns (e.g. `hswap` ∘ `rev`, which reverses each half in place); turning both doors beyond the
     overlaps noted above; other rotations, reflections and block shifts (e.g. XOR of blocks shifted by one,
     CBC-style); the full dihedral group: none is one of the five turns;
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
  positional Base64 reading. No script or ledger entry in this project combines the two ciphertexts.
- Known before computing: bytes 0–7 of `R1/{xor,sub,rsub}/id` are 0x00 and those of `R1/add/id` are fixed
  (`Salted__` + `Salted__`); the R2 `id`, `A.ibrev` and `B.ibrev` outputs are the last 80 bytes of the R1 ones.
- During the reviews, two implementations of this text (the campaign script and a reviewer's prototype) ran on the
  synthetic pairs only (controls, N1, calibration); neither combined the real envelopes.

## Not part of this test

The `+jkl` positional reading (Base64 positions 31/73/137/143 on a joined 257-character object) is recorded as a
coincidence marker, not admissible: the `k` is forced by the `Salted__` header, the `+` is common to both doors, and
the reading needs a mixed line-break rule; its chance rate across the constructions in play is about 1 in 58
(tick 94). The derivation of `137/143` is missing and stays with community material until it traces to a creator
source.
