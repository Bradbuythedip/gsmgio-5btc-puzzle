# Pre-registration: creator on-chain OP_RETURN text (2026-09-26)

Committed **before** the run.

## Why admissible

These are OP_RETURN outputs from `3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK`, the vanity address that funds
the prize key's 2020 halving spend. That makes them creator-signed text, recorded as chain history
at ticks 38/39 (LEDGER ~1587, ~1610). Only `causality` and `Halving` were ever run as candidates.
The gate would refuse the rest as "spent" only because their words occur in LEDGER.md. That rule
is meant to refuse *tested* material, not merely *recorded* material. So this run goes outside
`gate.py` with the gate's own frozen functions (`run_decrypts`, `run_scalars`), unchanged.

**Byte-exactness caveat:** strings are as recorded in the ledger (tick 38) and as restated by the
user with txid prefixes (117e2796…, 3891dd14…, 496ab2c7…, 2f64b875…, bd1b5d81…, 62dbb701…,
364de511…/722fbf35…, a82052a2…). No raw tx hex is in the repo, and this environment cannot reach
an explorer, so byte-exactness is USER-grade. **Prior:** tick 39 reads the 2020 messages as
confirmations of solved stages, not as passwords; expect null.

## Candidates (whole, verbatim)

1. `GSMG.io: Right, this is causality`
2. `GSMG.io: do you beleive me you need it?`
3. `GSMG.io: part of the cipher`
4. `GSMG.io: phase3.2 pass OK`
5. `GSMG.io: are you sure?`
6. `GSMG.io: You are here because 227 chars were correct`
7. `Good job, Neo!`
8. `GSMG.io neighbors, half and double`

## Protocol (frozen gate protocol)

{raw, sha256hex} × EVP-{MD5, SHA256} aes-256-cbc × {miniA, miniAB, inner96/P32T, cosmic} = 16
decrypts each (128 total), strict PKCS#7 + printable/magic gate (`aes_try.check_pt`), plus the
P32T freeze oracle on the inner96 decrypts. sha256(candidate) as a scalar → uncompressed and
compressed P2PKH vs `1GSMG1…` and `17ucy1…`.

## Stop rule

No variants, no prefix stripping, no case changes, no substrings, no concatenations, no second
pass. If null, the creator OP_RETURN class is spent.
