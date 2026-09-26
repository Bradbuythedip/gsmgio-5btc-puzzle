# Endgame provenance page — which primary sentence names each slot's operand

**No AES. One page. A slot with no naming sentence stays blank; blanks are not filled with
factorizations.** This is the gate the four-slot combine must pass before it may fire.

## Step 1 — the operand-naming table

| slot | primary sentence that names the OPERAND | operand | is the OPERATION named? |
|---|---|---|---|
| **A** `yellowblueprimes` | #1710 (2020-01-14) "Yellow has a number and so does Blue. Go back to the first puzzle piece"; token in #8446 | the 24 yellow/blue colour cells of the genesis image → the 24-bit value `f73d92` | **No.** "primes" is SAL-scoped and tied to `matrixsumlist` (#5966/#6509); no sentence names a prime/zero/DEL operation on the colour value |
| **B** `matrixsumlist` | token in #8446 only | "a matrix" — **not uniquely named** (the 14×14 genesis grid, or the 7×13 `DBBI` blocks?) | partial: "sum a matrix and list"; which matrix, which cells, and row-vs-column are unnamed |
| **C** `lastwordsbeforearchichoice` | token in #8446; operand = the Architect speech (phase-3.2 plaintext, solved) | the words ending the Architect text, before the Architect's choice | boundary **pinned below**; the extraction (letters? words?) is not further named |
| **D** `yinyang` | #9599 / #39224 / #39237 | **none** — it is an output / checkpoint reached after the wall, not an operand | n/a (D is not fed in) |

**Reading of the table.** Only **A's operand** (the colour cells) and **C's operand+boundary**
are named. **B's matrix is ambiguous** (no sentence says which matrix). **D is an output.**
So after this page there is still **no second source-forced concrete value**: A's operand has
no named operation to turn it into a value, and B's operand is not pinned. C is the one slot
that reaches a small concrete set.

## Step 2 — slot C, pinned from the bytes

The puzzle's Architect plaintext (1539 letters, phase-3.2 decrypt) contains **no** `door`,
`choice`, `choose`, or `left` — the film's two-door choice is absent. The text ends:

```
…willultimatelyresultintheextinctionoftheentirenessofyourselfself
goodluckneverthelessireallyhopeyouretheoneciaobellao
```

So the **choice boundary is the end of the text**: the creator's sign-off replaces the film's
two-door choice, and "the last words before the Arch[itect] choice" are the words that close
the puzzle's Architect text. C's whole byte-derived set, at most three:

| id | value | why |
|---|---|---|
| C-i | `ciaobellao` | the literal final token; sits before the cut |
| C-ii | `ireallyhopeyouretheone` | the last sentence before the sign-off tail |
| C-iii | `goodlucknevertheslessireallyhopeyouretheoneciaobellao` | the full closing, the "last words" as one span |

**Dropped from C** (per "that is C's whole set"): C0 the literal label
`lastwordsbeforearchichoice` (kept only as the generic label-as-value hypothesis, not a
byte-derived value), and C2 the "quintessential human delusion" line (#3390) — it is a mid-film
line the creator quoted separately and disclaimed (#3391 "not a hint"), and it is **not** before
this cut.

## Step 3 — slot A stays `f73d92` as a number

No **new** official operator (zero-out, ASCII-127/DEL, `{1,4,21}`) is aimed by any primary
sentence at a **named** object. The factorization route is closed (tick 32, a 1-in-11
coincidence). "primes = factorize" is not an operation. Therefore A remains the 24-bit number
`f73d92` (= 16203154 = Base58 `2S3dj`; prime-position subset `445`/`8g`, both already tested)
and is **not expanded** until the sheet can name a new operator on a named object.

## Step 4 — retrieval gap inventory

The only worthwhile non-AES task is retrieving a genuinely missing authenticated artifact.
Status of the candidates:

| artifact | in archive? | verdict |
|---|---|---|
| `HASHTHETEXT` (Decentraland audio clue) | yes (`decentraland.ipynb`, creator log) | present; not a hole |
| `/followthewhiterabbit` page | examined (ledger tick 11) | = the phase-1 verification page served at a second URL; no puzzle content |
| S0 / the original S1–S4 scalar script | **no** (absent from primary archive and all git history, tick 31) | the one genuine hole — but S0 is the uninvertible SHA256 preimage of head S1, so it is not retrievable, only re-derivable from the lost script |

**Conclusion.** No retrievable hole exists: the only missing artifact (S0 / the original
script) is gone and cannot be inverted. The retrieval branch is closed to what is in hand.

## Step 5 — no campaign

Two slots do not yet hold source-forced concrete values (C has a 3-string candidate set; A is
a number without a named operation; B's matrix is unnamed; D is an output). Per the standing
rule, `combine(A,B,C,D)` is illegal and no AES campaign runs. The next real move is a **named
operand or operator** from a new authenticated statement — not a tighter integer identity.
