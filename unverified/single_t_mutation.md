# The single-`t` mutation family

**Status: closed. Positive control passes; the family is empty; and the creator states
directly that typos carry no clues.**

## The proposal

`giveit ↔ givetit` is a real, documented GSMG transformation. The hypothesis: treat the
extra `t` as a reusable endgame *operator*, and mutate every unresolved source string by
exactly one `t` (unchanged / delete one existing `t` / insert one `t`), with a mandatory
positive control proving the harness models the historical bypass before touching a lock.

That is a well-formed experiment, so it was run as specified.

## Positive control — PASS

```
giveit  (correct)  -> sha256hex -> EVP-SHA256 -> Phase 3.2  PASS  "I've been waiting for you..."
givetit (extra t)  -> same path                             FAIL
```

The harness models the historical typo bypass correctly, so a negative from it is meaningful.

## Result — empty

| tier | variants | trials | hits |
|---|---|---|---|
| tier 1 (insertion adjacent to an existing `t`/`it`, the demonstrated defect class) | 110 | 23,100 | **0** |
| tier 2 (insertion at every character boundary; weaker family, labelled separately) | 606 | 127,260 | **0** |

Corpus: the SalPhaseIon token labels, the VIC sentence, the Architect continuation spans
(`returntothesourcecodes`, `reinsertingtheprimebasics`, `allowingatemporarydissemination...`,
`sevenintertwinedpasswords`, …), the known phase passwords, against the outstanding
envelopes. Success required PKCS#7 **plus** a predeclared structural criterion; a lone `01`
tail is logged and ignored.

## Why it was always going to be empty

The creator addresses this directly, more than once:

- **2020-02-22, #1806** — *"Typos: Horrible mistakes due to rushed work. I'm 100% to blame
  for this noobish display of words. **No clues to be found in those typos** might you
  wonder 😉."*
- **2019-05-18, #871** — *"For those feeling bad about having wasted time on my typo. I
  might feel even worse as I've tested the entire puzzle 3 times with the same string which
  had the typo in it."* The `t` survived because he tested against his own typo'd string.
- **2019-05-18, #898** — *"No hints after stage 2 (except the 't' to fix my stupid
  mistake)."*
- **2020-04-08, #3345** — *"No hints; errors and typos are mostly not intended."*

So the extra `t` was a one-off erratum with a published correction, not a mechanism. The
fallback conclusion the proposal itself named — *"a historical bypass instruction for
Phase 3.2, not a general final-key mechanism"* — is not merely what the negative result
implies; it is what the creator says in plain words.

## Result

Closed, on both empirical and source grounds. Typo-mining is explicitly ruled out by the
creator and should not be reopened without new primary material contradicting four separate
statements.
