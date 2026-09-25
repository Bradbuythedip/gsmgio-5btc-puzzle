# "KEY in the 7×13 column sums" [SalPhaseIon]

## The structural observation (this part is real and worth keeping)

Split the SalPhaseIon letter body at the two `a`/`b`-only binary runs. Two undecoded
blocks remain, and their lengths are not arbitrary:

| block | length | shape |
|---|---|---|
| `dbbib…` (head) | **91** | exactly 7 × 13 |
| `faed…` | **570** | exactly 6 × 91 + 24 |

So `faed` is six complete 7×13 matrices plus a 24-symbol remainder
(`ibibbibdcbahaidhfahiihic`), and `head` is one more 7×13 matrix. Seven matrices of the
same shape is a genuinely suggestive fact, and 13 is not a divisor of 570, so sweeps that
only try exact divisors of the block length will miss this decomposition entirely.

## The claim that does not survive

A circulating analysis claims that **only** matrix #6 of `faed` yields `KEY` in its column
sums, with sum string `DTEKEYUFFXGTD`, and that this pairs with `dbbib → KEY` as a
yin-yang complementary pair.

Raw column sums (7 rows × 13 columns, a=1…i=9), for the record:

```
dbbib/head  [28,38,42,37,24,33,15,34,35,39,26,33,38]  A=1 -> BLPKXGOHIMZGL
faed[1]     [31,24,48,40,45,28,34,34,34,32,37,30,34]  A=1 -> EXVNSBHHHFKDH
faed[2]     [36,32,30,35,23,43,44,25,44,33,35,44,36]  A=1 -> JFDIWQRYRGIRJ
faed[3]     [52,43,45,31,41,41,41,33,41,37,39,34,34]  A=1 -> ZQSEOOOGOKMHH
faed[4]     [47,39,30,48,41,44,31,39,55,42,41,26,26]  A=1 -> UMDVOREMCPOZZ
faed[5]     [35,34,46,46,42,43,33,41,33,41,42,47,49]  A=1 -> IHTTPQGOGOPUW
faed[6]     [39,31,44,39,38,34,43,39,35,42,35,31,37]  A=1 -> MERMLHQMIPIEK
```

No block spells `KEY` in its raw column sums under any of the obvious sum→letter mappings
(`A=1 (s-1)%26`, `A=0 s%26`, `s-7`, `s-6`). `faed[6]` reads `MERMLHQMIPIEK`, not
`DTEKEYUFFXGTD`; the claimed string would require column sums ≡ `[4,20,5,11,5,25,21,6,6,24,7,20,4]`
mod 26.

The claim only appears after **zeroing out a chosen subset of source characters** before
summing (the "prime segmentation" mask).

## Why that is overfitting, quantified

If the mask is free, the result is not evidence. Zeroing any subset of a column's 7 cells
can reduce that column's sum to many residues mod 26. Counting how many of the 11 possible
three-column windows can be *forced* to read `KEY` by some choice of mask:

```
dbbib/head : 9/11        faed[1] : 11/11      faed[2] : 9/11
faed[3]    : 10/11       faed[4] : 9/11       faed[5] : 11/11
faed[6]    : 11/11
```

Every block can produce `KEY`, in nearly every window. So "only matrix #6 produces KEY" is
false — the selectivity is an artifact of which mask was searched, not a property of the
data. Finding a 3-letter English word in a freely-maskable 13-symbol string is expected,
not surprising.

This is exactly the failure mode the top-level README warns about: without verifiable
output structure, a decoding is indistinguishable from failure. `KEY` is 3 characters of
"structure" bought with dozens of free binary choices.

## Result

The **shape decomposition (7 matrices of 7×13 + 24 remainder) is kept** as a real, unexplained
structural fact and a live lead. The **`KEY`-in-column-sums reading is rejected** as
mask-overfitting.

To be persuasive, a mask would have to be fully specified *in advance* from the puzzle's own
text (not fitted to the output), and the resulting sum string would need to carry far more
structure than a single 3-letter word — e.g. a full readable sentence, or a value that
verifiably decrypts one of the outstanding AES blobs.
