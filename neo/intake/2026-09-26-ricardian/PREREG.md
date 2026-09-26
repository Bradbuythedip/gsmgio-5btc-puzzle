# Pre-registration: the Ricardian "document hash = identifier" reading (2026-09-26), before the run

**Source.** User-pasted Ian Grigg papers page (iang.org/papers). Provenance check (tick 89): none of
its distinctive terms occurs in the creator's own words or anywhere in the puzzle material; the only
repo hits are this session's tick-88 text. So nothing on the page is creator-anchored.

**The one checkable structure on the page.** The Ricardian contract (Grigg 2004; "Why the Ricardian
Contract Came About"): a human-readable document is "hashed cryptographically, providing a secure,
unique and cost-free identifier". Mapped onto GSMG: the key (or password) for the next step is the
hash of the whole preceding document, not a riddle answer. The operation is creator-native (sha256 →
key is the checkpoint convention, tick 59; sha-256(password) is the stated AES convention, phase 2).
Only the choice of object (a whole document) is imported.

**Prior: low.** At every solved stage the creator's password was a riddle answer, never a document
hash. Some pairs are impossible by construction: a document that contains a lock's own ciphertext
cannot hold that lock's password. They run anyway and are marked as such.

## Objects (fixed: 6, whole and byte-exact)

| id | object | bytes | why |
|---|---|---|---|
| O1 | phase-2.1 plaintext (`phase2-assets/phase2.1.txt`, re-derived by decrypting `phase2_aes.txt`) | 648 | solved-stage document |
| O2 | phase-3 plaintext (`phase2-assets/phase3.txt`, re-derived from `phase3_aes.txt`) | 4090 | solved-stage document |
| O3 | phase-3.2 plaintext, whole (`materials/phase32_plaintext_outer.txt`, re-derived from `phase3.2-aes.txt`) | 2422 | contains P32T (circular for P32T) |
| O4a | O3 before the P32T envelope, `O3[:2292]` (ends `\r\n\r\n`) | 2292 | the "contract" in front of P32T |
| O4b | O4a with trailing whitespace stripped | 2288 | same, the other natural boundary |
| O5 | SalPhaseIon soup as pinned (`materials/primary/salphaseion_soup_space_separated.txt`, sha256 `d39d10b1…`) | 2149 | contains miniA/miniB (circular for those) |

## Protocol (frozen)

Per object: the gate's frozen path ({raw, sha256hex} × EVP-{MD5, SHA256} × {miniA, miniAB, P32T,
Cosmic} = 16 decrypts, strict PKCS#7 + printable/magic), the P32T last-block freeze, campaign 51's
padding-independent scan of the same decrypts, and `addr_check`'s fixed encodings (sha256, sha256d,
bitrev, byterev; compressed + uncompressed) vs prize / `17ucy1…` / `1NULY7…`. 96 decrypts, 48 addresses.

## Decision rule

- **HIT** = any strict-pad hit with printable/magic, P32T freeze pass, padding-independent hit, or
  address match. Report, stop, widen nothing.
- **Null** = the Ricardian document-hash reading is closed for the puzzle's documents. No other
  boundaries, normalizations, encodings, documents or hash functions.
