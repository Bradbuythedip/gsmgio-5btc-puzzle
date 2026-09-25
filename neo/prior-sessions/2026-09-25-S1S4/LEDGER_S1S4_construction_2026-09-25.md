# S1–S4 scalar construction — reconstruction attempt, session ledger (2026-09-25)

Scope: the prompt "Reconstruct the S1–S4 scalar construction." Recover the map from each
32-byte hex seed to a secp256k1 scalar; recover S0; reproduce S0's ±2³⁸ rejection under one
construction; only then run S1–S4 under the same window/implementation/control/stop rule.

**Verdict up front: the seed *generator* is recovered; the seed→scalar *map* is not uniquely
determined; S0 is unrecoverable. Reconstruction is BLOCKED on S0. S1–S4 were NOT run. The
canonical-hash sequential-vanity family stays OPEN, not closed.**

All results below are reproducible from `seed_relations.py`, `seed_gap.py`, `bsgs_harness.py`
in this folder.

---

## 1. New structural finding — the seed generator (this is the discriminating evidence)

Testing every relation among the four seeds:

| relation | result |
|---|---|
| **S2 = SHA256(S1)** as raw 32 bytes | **exact** (256-bit match) |
| **S4 = SHA256(S3)** as raw 32 bytes | **exact** (256-bit match) |
| S3 = SHA256(S2) | no |
| any Si = SHA256(Sj) other than the two above | no (full 12-pair edge map) |
| arithmetic sequence (constant Δ, plain or mod N) | no |
| constant XOR, constant multiplier mod N, byte-reversal chain | no |

The complete SHA256 edge graph is exactly **two disjoint edges: S1→S2 and S3→S4**. Heads
(no incoming edge): S1, S3. Terminals: S2, S4. Two exact 256-bit coincidences are ~2⁻⁵¹² by
chance, so this is the real generator: the "**canonical-hash sequential**" family is built by
`SHA256(raw_bytes)` chaining, in two independent pairs.

The S2→S3 gap was checked as a possible vanity step and is not one: `S3 − SHA256(S2) mod N`
is ~2²⁵⁴ and shares **0** leading nibbles with `SHA256(S2)`. So the two pairs do not join into
one ladder, and there is no small offset or prefix-grind linking them.

Reading with S0 included: the natural structure is a 3-chain **S0 → S1 → S2** (S1 = SHA256(S0),
S2 = SHA256(S1) ✓) plus a separate 2-chain **S3 → S4**. Alternatively S0 is its own head/pair.
In every reading S0 is the SHA256 preimage of a head.

## 2. Seed→scalar construction — candidate set (NOT uniquely determined)

The generator tells us how the seeds were *made*, not how a 32-byte seed becomes the private
scalar to BSGS from. Candidates, input type and reduction stated:

| id | map | input | reduction |
|---|---|---|---|
| C1 | `int(seed_hex,16)` | the 32-byte value as a big-endian integer | mod N |
| C2 | `int(SHA256(seed_hex_ascii))` | the 64-char ASCII hex string | mod N |
| C3 | `int(SHA256(seed_raw_bytes))` | the 32 raw bytes | mod N |
| C4 | `int(SHA256²(seed_raw_bytes))` | the 32 raw bytes (double-SHA) | mod N |
| C5 | `int(seed_raw[::-1])` | byte-reversed 32 bytes | mod N |
| C6 | `int(SHA256(seed_hex_ascii.upper()))` | upper-case ASCII hex | mod N |

Discriminating evidence obtained: the generator finding **rules out** the "seeds are a
SHA256(hex-ascii) chain," "arithmetic sequence," and "byte-reversal chain" hypotheses. It does
**not** discriminate among C1–C6 as the seed→scalar map — that can only be pinned by
reproducing S0's known rejection, which needs S0.

Elegant redundancy worth recording: because the generator *is* the C3 map,
`C3(S1) = int(SHA256(S1_raw)) = int(S2) = C1(S2)` exactly, and `C3(S3) = C1(S4)`. So a C3 search
over the heads {S1,S3} is already covered by a C1 search over the terminals {S2,S4}.

Offset-0 direct addresses (documentation only — NOT a BSGS run) under C1–C6 for S1–S4: every
longest-common-prefix with the prize address is 1–2 characters (random baseline ≈1). No seed
matches the prize at offset 0 under any construction, which is expected — the whole hypothesis
is a non-zero vanity offset.

## 3. S0 — BLOCKED (unrecoverable)

S0's seed string is required to reproduce the existing positive control. It is not available:

- It is not in the primary creator material, the community repo, or this session's files.
- It is not in the prior "Provenance hunt" transcript (turns 0–37 read end to end) nor the
  parallel session; both recorded the S0–S4 script as lost.
- As the SHA256 preimage of head S1 (3-chain reading) or of its own pair, it cannot be
  inverted.
- It is **not** SHA256 / SHA256d of any of 2,715 strings harvested from the creator material,
  so it is not a recognizable published answer whose preimage we could reconstruct.

Per the prompt's own constraint: **if S0 cannot be recovered, the reconstruction is blocked on
S0.** It is.

## 4. BSGS implementation — VALIDATED (so a future rejection can be trusted)

`bsgs_harness.py`, coincurve point ops + numpy sorted x-prefix table, signed window, verifies
every candidate point fully before reporting. Planted positive controls (against a random base
scalar, recovering a known offset):

| plant | window | result |
|---|---|---|
| n₀ ∈ {0, 1, 12345, 0xFEDCB} | 2²⁰ | all recovered |
| n₀ = 0x1234567ABC (~2³⁶·²) | **2³⁸** | recovered, 80 s |
| n₀ ∈ {−1, −12345, −0xFEDCB} | 2²⁰ | all recovered, sign correct |

The tool can recover a known offset inside the 2³⁸ window. A rejection from it would therefore
be meaningful — but there is no verified construction+S0 to trust a rejection *of* yet.

## 5. S1–S4 — NOT RUN

Both preconditions in the prompt fail:
- the construction is not uniquely determined (§2), and
- S0's rejection is not reproduced (§3).

Constraint honored: "Do not run S1–S4 until the construction is uniquely determined and S0's
rejection is reproduced." Not run. No closure recorded.

Also confirmed for the record: none of the ten cosmic-tree "related seeds"
(`cc[833:865]`, `ca[280:312]`, `ca[833:865]`, `cc[280:312]`, `sha256(cosmic_A/cc/chain4)`,
half, better-half, chain1[:32], and the derived scalar `abc09ead…`) equals any of S1–S4. So
**S1–S4 are not four of those ten**; the two families are unrelated. (The cosmic tree is
solver-derived and already demoted; the derived scalar's public key does not control the prize.)

## 6. Ledger line

> **S1–S4 canonical-hash sequential-vanity family — construction NOT uniquely determined,
> S0 unrecoverable, BSGS validated on planted controls, S1–S4 NOT run. Family OPEN, blocked.**
> Generator recovered: seeds are SHA256(raw) pairs (S2=SHA256(S1), S4=SHA256(S3); heads S1,S3).
> Seed→scalar map is one of C1–C6 (raw-int the prior default), undiscriminated without S0.
> S0 is the SHA256 preimage of a head — not invertible, not a known answer, in no archive.
> S1–S4 are not among the ten cosmic "related seeds." Next real move: recover S0's seed string
> (or the prior script), or a creator line naming the object and operation. Not a widening.
