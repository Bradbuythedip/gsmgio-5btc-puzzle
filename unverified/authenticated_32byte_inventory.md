# The authenticated 32-byte inventory × both 80-byte locks — closed

Tests the "an already-open door emits a raw 32-byte key" reading. Every value below was
**recomputed and verified by actually decrypting the stage it came from**, not quoted.

## The inventory (all verified)

| stage | salt | password digest (= EVP passphrase) | EVP key | EVP IV |
|---|---|---|---|---|
| phase 2 | `06286612d43ed7ed` | `eb3efb51…d07e5bf` | `cf3e3759…c6d49550` | `4eb2c80e…ebd4c6e6` |
| phase 3 | `9fbc451d13d071f4` | `1a57c572…d2ec30d5` | `53eb2e95…1f891f2f` | `725ba167…2ea2e9b3` |
| phase 3.2 | `eefc4c5befc1656a` | `250f3772…9d61ce4c` | `f4c72c3a…6b1157b3` | `b620574d…40eb201f` |

All three `decrypt_ok = True`, so these are the real AES materials that opened those doors.
Both quoted digests cross-check exactly: `sha256("causality")` and the 7-part concat digest
match the values supplied. SalPhaseIon entry hash `89727c59…52f6a32` likewise recomputed.

Plus `sha256` of each of the four decoded tokens individually, and of the four concatenated
in published order and space-joined. **13 inventory values total. No sliced English.**

## The matrix

- **IVs (named only):** each blob's own `salt‖salt`, the phase-3.2 outer IV, the phase-2 EVP
  IV, the phase-3 EVP IV, and a single zero-IV control.
- **Profiles:** (1) raw 32 bytes straight into AES-256-CBC; (2) the candidate as an EVP
  passphrase — both its hex form and its raw bytes — with the target blob's own salt, under
  **SHA-256 and MD5**.
- **Targets:** both 80-byte locks, P32T (`b45a5e3d827593ca`) and salph_inner
  (`3ab585348552415d`). Treated as one class, as specified.

## Acceptance rule (written before looking)

PKCS#7 pad ≥ 2 **and** ≥85% printable body; **or** any 32-byte window of the plaintext
deriving to `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` or `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa`.
A lone `0x01` pad is a discard. The address check ran on every 32-byte window of every
plaintext (49 windows × 234 decrypts), using the known-answer-tested secp256k1 in
`neo/harness/btc_addr.py`.

## Result

**234 decrypts. 0 accepted.**

By the preregistered criterion — *"if none of them open either 80-byte blob, the 'first door
emits the raw key' reading is empirically closed"* — **it is closed.** Not rhetorically
weakened: the authenticated key material from every solved stage, against both locks, under
both profiles and both digests, produces nothing.

Step 4 of the proposal (board-not-sentence coordinate extraction) was already executed as the
preregistered tick 1b and is parked: two fixed 2×14 boards, removed-material coordinates and
checkerboard numbering, 182 trials each, both negative.

## Where this leaves the board

The screenshot sharpened the question and did not supply the key. P32T is no longer the
cheapest door. The remaining under-attack objects, in order:

1. a decode method for `dbbi` (91) and `faed` (570) — the only unused published ciphertext
   with structure
2. how `yellowblueprimes` and `yinyang` are *computed* rather than guessed
3. Cosmic's KDF family, treating 1-byte pads as noise unless the plaintext is structured
