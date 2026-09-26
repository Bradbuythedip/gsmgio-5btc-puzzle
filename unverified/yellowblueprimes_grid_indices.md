# yellowblueprimes — the coloured spiral indices and their prime subset

Authenticated operands, from `neo/materials/primary/matrix_grid_spiral_colors.json`
(part of the primary archive, not solver-derived). Published here so nobody has to
re-derive them or trust a transcription.

## The exact index lists

Spiral = counter-clockwise from top-left, 196 cells, 0-based.

```
BLUE   (15):  7  15  23  31  47  55  63  87  95 103 111 127 135 159 183
YELLOW ( 9): 39  71  79 119 143 151 167 175 191
ALL    (24):  7  15  23  31  39  47  55  63  71  79  87  95 103 111 119 127 135 143 151 159 167 175 183 191
```

Colour sequence in spiral order (24 chars):

```
BBBBYBBBYYBBBBYBBYYBYYBY
```

**Correction to a circulating string:** versions of this sequence appear as
`BBBBYBBBYYBBBBYBBYYBFYYBY` — 25 characters with a spurious `F`. The authenticated
sequence is 24 characters, one per byte. Any schedule-driven parse using the 25-char
form is parsing a typo.

`#FEFEFE` cell is at grid (7,4) = **spiral index 163**. (Not 104, and not 177; see
`phase0_fefefe_parity.md`.)

## Structural facts

- All 24 coloured indices are `≡ 7 (mod 8)`, and `index // 8` runs exactly `0…23` — one
  coloured cell per byte of `gsmg.io/theseedisplanted`, each at that byte's LSB. Confirms
  `phase0_yellow_blue_counts.md`.
- **1-based, every coloured index is a multiple of 8, so none is prime.** A "prime subset
  of the spiral indices" therefore only exists under 0-based indexing, where it is:
  `7, 23, 31, 47, 71, 79, 103, 127, 151, 167, 191` (11 of 24; blue 6, yellow 5).

## A count coincidence that does not survive

There are exactly **9 primes ≤ 24** (2,3,5,7,11,13,17,19,23) and exactly **9 yellow** cells;
likewise 15 non-primes and 15 blue. Tempting, but the positions do not agree: yellow sits at
sequence positions 5, 9, 10, 15, 18, 19, 21, 22, 24, which intersects the prime positions
only at 5 and 19 (2 of 9). The 9/15 split is forced by the URL's own LSBs, so the matching
count is a coincidence of 24, not a prime structure.

## Tested and negative

`neo/harness/campaign_17_grid_primes.py`, 66 candidates → 24,192 trials, **no hit**:
selections and zeroings of the URL, the colour sequence and the index list under both
`primes` and `{2,3,5,7}`, 0- and 1-based; the prime spiral indices themselves; blue/yellow
index lists; the colour sequence as 0/1 both polarities; the 9/15 counts with and without
the prime token; the `163` / `(7,4)` fefefe values; each also wrapped with `matrixsumlist`
and `lastwordsbeforearchichoice`, raw and hashed.

## Where that leaves it

The grid's number frame is now fully enumerated and published, and the obvious prime
readings of it are closed. What is *not* closed is whether `yellowblueprimes` consumes these
indices at all — it may name a selector applied to a different object (the letter blocks),
with the grid only supplying the mask. That is the reading worth testing next, and it needs
the mask stated before the test, not fitted after it.
