GSMG OFFLINE SOLVER — QUICK START
=================================

1) Keep gsmg_offline_solver.py anywhere you like.
2) Point --repo at your local checkout of Bradbuythedip/gsmgio-5btc-puzzle.
3) First run:

   python3 gsmg_offline_solver.py doctor
   python3 gsmg_offline_solver.py audit --repo /path/to/gsmgio-5btc-puzzle
   python3 gsmg_offline_solver.py selftest --repo /path/to/gsmgio-5btc-puzzle

Do not interpret a candidate null unless selftest passes.

ONE EXPLICIT CANDIDATE
----------------------

   python3 gsmg_offline_solver.py test \
       --repo /path/to/gsmgio-5btc-puzzle \
       --candidate 'EXACT STRING' \
       --source-note 'where this exact string came from'

Or preserve exact bytes in a file:

   python3 gsmg_offline_solver.py test \
       --repo /path/to/gsmgio-5btc-puzzle \
       --candidate-file candidate.bin \
       --source-note 'verbatim saved artifact'

The default log is ./offline_solver_attempts.jsonl. The harness refuses to spend the
same candidate bytes twice unless --force is supplied.

FROZEN TEST SURFACE
-------------------

For exactly one candidate, the default test is:

  {raw bytes, lowercase SHA256-hex ASCII}
      x {EVP_BytesToKey MD5, EVP_BytesToKey SHA256}
      x {miniA, miniAB, inner96/P32T, cosmic}

= 16 AES-256-CBC decryptions.

It also checks:
  * P32T IV-independent final-block structure
      primary: 0a || 0f*15  (64 hex chars + newline, pad 15)
      secondary: 10*16      (two raw 32-byte keys, pad 16)
  * SHA256(candidate) as a secp256k1 scalar
  * candidate itself as a scalar only if exactly 64 ASCII hex chars
  * explicit plaintext[0:32], plaintext[32:64], and literal standalone 64-hex
    values ONLY when they map exactly to the prize or Better-Half address.

It does NOT generate vocabulary, n-grams, sliding windows, combinations, KDF soup,
or private-key ranges.

STRICT PROVENANCE GATE
----------------------

Example intake.json:

{
  "kind": "jrk_sentence",
  "id": "12345",
  "date": "2026-09-26",
  "author": "@SoWut",
  "text": "full creator sentence exactly as archived",
  "candidate": "exact verbatim substring to test"
}

Then:

  python3 gsmg_offline_solver.py gate --repo /path/to/repo intake.json

Kinds supported:
  jrk_sentence
  gsmg_page
  uttered_password

The gate also checks the local repo's parked corpus and prior attempts.

RAW 32-BYTE KEY
---------------

  python3 gsmg_offline_solver.py keytest \
      --repo /path/to/repo \
      --key-hex 64_HEX_CHARS

This performs IV-independent final-block checks and also reports the Bitcoin P2PKH
addresses if the same 32 bytes are interpreted as a secp256k1 scalar.

GRIGG / PARAMS-CODE-TEXT MODEL
------------------------------

The harness deliberately DOES NOT guess how to serialize or concatenate these objects.
Use:

  python3 gsmg_offline_solver.py components \
      --params exact_params.bin \
      --code exact_code.bin \
      --text exact_text.bin

If you have a source-defined exact package already:

  python3 gsmg_offline_solver.py components \
      --params exact_params.bin \
      --code exact_code.bin \
      --text exact_text.bin \
      --package exact_package.bin

It reports lengths, hashes, and where each component literally occurs in the package.
It will not manufacture ordering/separators/encodings.

EXACT HASH
----------

  python3 gsmg_offline_solver.py digest --text 'exact text'
  python3 gsmg_offline_solver.py digest --file exact_bytes.bin
  python3 gsmg_offline_solver.py digest --hex deadbeef

OP_RETURN / NONCE-POINT CHECK
-----------------------------

Fill nonce_points.template.json only with authenticated x/y coordinates, then:

  python3 gsmg_offline_solver.py opreturn \
      --payload EXACT_64_HEX \
      --nonce-json nonce_points.json

Only exact big-endian coordinate equality and whole-byte reversal are checked.

TRANSACTION JSON
----------------

Save transaction JSON from a trusted source, then:

  python3 gsmg_offline_solver.py txscan tx.json

Optionally compare every exactly-32-byte OP_RETURN to the nonce file:

  python3 gsmg_offline_solver.py txscan tx.json --nonce-json nonce_points.json

DEPENDENCIES
------------

Python 3.9+ and ONE of:
  * pycryptodome
  * cryptography
  * openssl executable in PATH

No network access is used by the script.

REPO NOTES (ledger tick 91, version 2026-09-26.2)
-------------------------------------------------

Validated against this checkout: doctor, audit and selftest all pass. Three fixes from .1:
  * the phase-3 solved control used a 220-char password (FEN rank "1P2P2P/" missing), so
    selftest always failed; it is now the verified 227-char string (sha256 1a57c572...).
  * key material (plaintext[0:32], [32:64], literal 64-hex) is checked on the raw plaintext of
    every decrypt again, not only PKCS#7-valid ones (tick 83 / campaign 51).
  * txscan exits 10 only on a nonce match; mentioning the prize address is not a hit.

Authenticated nonce points: materials/chain/nonce_points_prize.json holds the six prize-key
signature nonce points R = (x, y), recomputed by ECDSA verification (harness/nonce_points.py).
Use it with `opreturn --nonce-json` and `txscan --nonce-json`. No saved creator transaction
carries a 32-byte OP_RETURN (the memos are 7-53 bytes of ASCII).
