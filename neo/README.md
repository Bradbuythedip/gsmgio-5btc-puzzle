# neo — endgame working directory

Reproducible tooling and an append-only ledger for the four unsolved AES locks.
Everything here is derived from primary sources (this repo's notebooks and assets,
plus the SalPhaseIon page text); nothing depends on third-party writeups.

## Layout

```
materials/        verified puzzle inputs (page text, phase-0 grid, the blobs)
harness/          the tools
attempts/         per-candidate JSONL logs of everything tested
prior-sessions/   archived earlier work (S1-S4 scalar construction, parked)
LEDGER.md         append-only session log: findings, campaigns, exclusions
```

## Tools

| file | what it does |
|---|---|
| `harness/aes_try.py` | the decrypt harness. Self-tests against the 3 solved blobs on every run |
| `harness/btc_addr.py` | dependency-free secp256k1 to P2PKH, with known-answer self-tests |
| `harness/campaign_*.py` | individual candidate campaigns, each self-contained and re-runnable |
| `harness/verify_xor_theory.py` | end-to-end test of the circulating XOR theory |

Only dependency is `pycryptodome` (`pip install pycryptodome`). The EC code is pure Python
so address results need no native library.

## Running it

```bash
cd neo/harness
python3 aes_try.py          # prints targets, then self-tests the 3 solved blobs
python3 btc_addr.py         # known-answer test of the address math
python3 campaign_01.py      # any campaign; results append to ../attempts/
```

**Always check the self-test line before trusting a negative.** `aes_try.py` must print
`self-test passed: True`, which means the harness reproduces the three known decryptions
(`causality`, the phase-2.2 concatenation, `jacquefresco...`). If that fails, every "no hit"
in this directory is meaningless.

## Acceptance rule

A candidate is only accepted on strict PKCS#7 padding **and** corroboration: pad >= 4
(roughly 2^-32 by chance), or a >= 4-byte magic prefix, or high printability. Pad values of
1-3 with garbage bytes occur constantly at random and are logged but never treated as hits.

This matters. A looser early rule produced three spurious "hits" in 75k trials. Any claimed
solution in this puzzle that rests on a 1-byte pad is almost certainly noise.

## Adding a campaign

Copy the shape of an existing one:

```python
from aes_try import Harness
h = Harness("campaign_NN")
h.try_family("some candidate", "note")   # tries raw + sha256hex + variants
h.finish("campaign_NN")
```

`try_family` covers the creator's "sha b4" habit automatically. Log a note for every
candidate family so the exclusion is meaningful to the next person.
