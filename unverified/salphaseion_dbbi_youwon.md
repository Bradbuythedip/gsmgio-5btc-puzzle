# DBBI minus the VIC sentence yields a planted "YOUWON"

**Status: the finding reproduces and is very unlikely to be chance. It does not yield a key.**

## The operation

Two objects in the puzzle are each exactly **91 symbols**, and neither length was chosen to
make this work:

- `dbbi`, the first undecoded SalPhaseIon block: 91 symbols over `a`–`i`
- the Phase-3.2 VIC-cipher plaintext: 91 letters
  `INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE`

Subtract them position-by-position, mod 26 (`dbbi` as a=1…i=9, VIC as A=1…Z=26, render A=0):

```
VOZIJBDTIQBRGVEOMZNBC YOUWON XCPKWGBNAXDGJGDUNNVMPABTAFPAAXMJYLZBUWERDNXYDESKUOBXCAMVDJLQTSGA
[----- 21 chars -----] [ 6  ] [--------------------- 64 chars ---------------------]
```

`YOUWON` appears in clear, and the remainder after it is **exactly 64 characters** — the
length of a hex private key.

Three algebraically equivalent parameterisations (`d1-v1` rendered A=0, `d1-v0` rendered A=1,
`d0-v0` rendered A=0) give the identical string, so this is one natural rule, not three
cherry-picked ones.

## Why this is not the usual overfitting

This repo has already rejected a "KEY in the column sums" claim as mask-overfitting. This is
a different kind of result, and the difference is measurable:

| | KEY-in-column-sums | YOUWON |
|---|---|---|
| free parameters | a per-cell zero mask (dozens of binary choices) | none — fixed rule, fixed operands |
| length fit | block reshaped to taste | 91 = 91, unchosen |
| null rate | KEY forceable in 9–11 of 11 windows in **every** block | see below |

Null tests, same rule, 91-symbol strings drawn from `dbbi`'s own multiset:

- `YOUWON` in 200,000 shuffles of `dbbi`: **0**
- `YOUWON` in 200,000 i.i.d. draws at `dbbi`'s letter frequencies: **0**
- theoretical for a random 26-alphabet: 86 × (1/26)⁶ ≈ **2.8 × 10⁻⁷**
- *any* 6-letter dictionary word in 100,000 shuffles: 857, i.e. **0.86%**
  (and the real output contains **no** 6-letter dictionary word — only `YOUWON`, which is
  two words joined and so is not in the dictionary at all)

Even generously allowing that a searcher would have accepted any of ~50 victory-ish
6-letter strings across ~20 distinct rules, that is order 10⁻⁴. The additional fact that
`YOUWON` lands precisely where it leaves a 64-character tail tightens it further.

Conclusion: `dbbi` is **meant to be operated against the VIC sentence**, as numbers, mod 26.
That is a real structural instruction, and it is consistent with `matrixsumlist` meaning
"emit the number list" before any letter rendering.

## Why it is still not a key

- The 64-character tail is **not hex**: it uses 24 distinct letters (`A`–`Z` minus `H`,`I`),
  so it cannot be a hex private key as written.
- Its entropy is high and flat — consistent with the earlier finding that `dbbi`/`faed`
  carry high-entropy data rather than prose.
- Tested as passwords against all outstanding locks (full string, prefix, tail, prefix+tail,
  the `YOUWON`+tail span, lower-case forms, and both reverse-direction rules), raw and
  hashed per the pinned convention: **no decryption** (`campaign_15_youwon`, 2730 trials).

So `YOUWON` reads as a **planted confirmation marker** — the creator telling a solver who
reaches this exact operation that the operation is correct — rather than as key material.
That matches his repeated framing that the remaining step is recognisable when you hit it.

## The 64-character tail is not a letter-encoded hex key

The tempting reading — 64 characters is exactly hex-private-key length — is now closed, and
on structure rather than on a failed guess.

A hex key written in letters needs exactly **16** distinct symbols. The tail uses **24**:

```
A7 X5 D5 G4 B4 N4 P3 J3 U3 M3 C2 K2 W2 V2 T2 Y2 L2 E2 S2 F1 Z1 R1 O1 Q1
```

So no injective letter→hex map exists. Every mod-16 style reduction is lossy, collapsing
three different letters onto each digit, which means the "key" it yields is an artefact of
the chosen reduction rather than something recovered from the data. Three such reductions
were run anyway (`A=0 mod 16`, `A=1 mod 16`, `A=0 div 2`); all three give valid secp256k1
scalars, and none derives the prize address:

| mapping | derived hex | prize? |
|---|---|---|
| A0 mod16 | `72fa661d07369634dd5cf01305f007c98b9146413d78342a4e1720c539b03260` | no |
| A1 mod16 | `830b772e1847a745ee6d0124160118da9ca257524e89453b5f2831d64ac14371` | no |
| A0 div2  | `b175b3060b13431a66a6700902700b64c5c0ab2816bc1295a70b106a14589930` | no |

That three arbitrary reductions all produce valid-looking scalars is itself the warning: any
64-symbol string does, so "it makes a valid key" carries no evidential weight at all.

This strengthens the marker reading. `YOUWON` is a planted confirmation that the *operation*
is right; the 21 characters before it and the 64 after are residue of that operation, not a
payload.

## What it licenses next

The valuable part is the *method*, not the word: `dbbi` pairs with the VIC sentence under
mod-26 subtraction. The open question is what `faed` (570 symbols) pairs with under the same
discipline, and whether the 21-character prefix or the 64-character tail feeds the next
stage after a further fixed transformation.

Anything proposed here should be held to the same standard applied above: state the rule and
the operands in advance, and report the null rate.

## Correction (2026-09-26, LEDGER tick 69)

- The theoretical null above (2.8 × 10⁻⁷) uses a 26-letter alphabet. `dbbi` has only the nine
  symbols a–i, and at `dbbi`'s own frequencies the rate is about 3.2 × 10⁻⁶. The shuffle result
  (0 in 200,000) is unaffected.
- "Neither length was chosen" holds for the analyst, not the creator. Given the VIC letters and the
  a–i alphabet, `YOUWON` can be planted at exactly one of the 86 offsets, 21. `dbbi` was built
  against the VIC sentence, so the two 91s are one design decision, and the 21 + 6 + 64 layout is
  forced by the construction.

