# Pre-registration: K₁₄ edge-space (multiplicity) reading (2026-09-26), committed before the run

User-directed. Tick 67 declined to open K₁₄ because no source names a graph operation; that
still holds, and this run does not reopen the parked corpus. It runs the user's concrete
six-step proposal once, as a closed family, so the reading gets an answer instead of staying open.

**The claim under test.** The 91-symbol streams are edge labels on K₁₄ (C(14,2) = 91); the VIC
one-digit/two-digit split is a 33-edge mask; the 24 coloured cells are edges; and some graph
invariant of that state is atypical, spells a macro label, or opens a lock.

**Facts fixed before any invariant was computed** (`campaign_44_k14.py --describe`):
- The 24 coloured cells are 12 above the diagonal, 12 below, 0 on it, and **no cell's mirror is
  coloured**. As undirected edges they are 24 distinct edges. The "12 mirrored edges" option in
  the proposal does not exist in the data; the 24-edge and directed forms are used.
- The 33/58 mask is where the sentence has a letter from `FUBCDORA` (the one-digit row of the
  certified board). It is a function of the plaintext, not an extra input.
- Spiral-lower placement shares its first 13 edges with row-major (the spiral runs down column 0).

## Objects (vertex set 0–13)

Placements of the 91 edges {i<j}: **RM** row-major upper triangle; **CM** column-major (= row-major
lower); **SPU** the authenticated ccw spiral restricted to cells above the diagonal; **SPL** the same
spiral restricted to cells below. No other orderings.

Unweighted graphs: `VIC33_P` and `VIC58_P` for each placement P; `COL12U`, `COL12L`, `COL24`
(placement-free), plus in/out degrees of the directed 24.
Weighted K₁₄ per placement: layers L1–L7 of DBBI‖FAED (a=0…i=8, the map the layer totals use),
the VIC sentence (A=1…Z=26), and the DBBI−VIC mod-26 residual that carries YOUWON (A=0). 36 graphs.

## A. Structure (the multiplicity test)

Unweighted family: `VIC33_P` × {degree variance, λ₂, log τ, triangles, edge connectivity,
components, Hamiltonian-path count} = 28 tests. Null: 20,000 uniform 33-edge subsets of K₁₄.
Weighted family: 9 streams × 4 placements × {strength variance, λ₂, λ_max, log weighted τ} = 144
tests. Null: 50,000 composition-preserving shuffles per stream. Two-sided empirical p,
Bonferroni per family at α = 0.01. Seed 20260926.

**English control (runs only if a text-derived object flags).** VIC mask, VIC letters and the
residual come from an English sentence, so a flag may only mean English is not i.i.d. Control:
200 non-overlapping 91-letter windows of the verbatim creator-message column of
`materials/primary/CREATOR-LOG_transcript_445_messages.md`, scored the same way (mask = FUBCDORA
membership, each against its own null, n = 1000). The flag stands only if its |z| exceeds the 99th
percentile of the control |z|. Otherwise it is withdrawn as English statistics.

## B. Text

Integer sequences: the degree sequence of every unweighted graph, the directed in/out degrees, the
strength sequence of every weighted graph. Renderings: mod 26 with A=0 and with A=1, forward and
reversed. Targets: `YOUWON`, `HALF`, `YINYANG` only. Null rate from the same null samples.
A text hit counts only if its null rate is below 10⁻³.

## C. Crypto (the macrostate check)

Per unweighted graph: RM-order 91-bit string, its 96-bit zero-padded hex, degree sequence
(comma-joined), τ, Hamiltonian-path count. Per weighted graph: strength sequence, weighted τ,
and for non-RM placements the stream re-read in RM order. Deduplicated; at most 154 strings.
Each goes through gate.py's frozen path unchanged (16 decrypts: raw / sha256hex × EVP-MD5 /
SHA256 × miniA, miniAB, P32T, Cosmic), the P32T freeze oracle, and sha256 → P2PKH against the
prize and `17ucy1…`. Integer invariants (τ, Hamiltonian count, weighted τ, the mask as an integer)
are also used directly as scalars mod n against both addresses.

## Decision and stop rule

- **HIT**: any strict gate hit, freeze-oracle key or address match. Report and stop.
- **Structure**: a flag that survives the English control is recorded as an atypical microstate.
  It licenses nothing by itself; a reading rule still has to come from a source.
- **Null on A, B and C**: the K₁₄ family is closed. No new placements, masks, invariants,
  serializations or maps (house map a=1 is not run), and no re-run with more samples.
