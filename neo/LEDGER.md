# Neo continuous-mode ledger

Running log of verified ground truth, pinned conventions, campaigns run, and open
threads. Newest session at the bottom. Everything here is reproducible from
`neo/harness/` + `neo/materials/`.

---

## Session 2026-09-25 — endgame corpus assembled, convention pinned, campaigns started

### Verified ground truth (primary sources: this repo's notebooks/assets + page screenshot)

Four unsolved AES locks, all openssl `Salted__` unless noted:

| id | bytes | salt | source |
|---|---|---|---|
| miniA | 48 (ct 32) | `3ab585348552415d` | SalPhaseIon page tail, after "sha b4 first hint is your last command" |
| miniB | 48 raw, no header | — | SalPhaseIon page tail, after the abba-binary "enter" |
| miniAB | 96 (ct 80) | `3ab585348552415d` | A‖B joined ("enter" = newline between two lines of one blob) |
| inner96 | 96 (ct 80) | `b45a5e3d827593ca` | tail of phase-3.2 plaintext (phase3-assets/phase3.2.txt) |
| cosmic | 1344 (ct 1328) | `2d3f6fe06dc950e6` | "Cosmic Duality" section of SalPhaseIon page |

- SalPhaseIon page string (1075 letters, space-separated) copied from salphaseion.ipynb;
  byte-identical to the copy in the (otherwise junk) jackdevs66/GSMG5_CDuality repo.
- Cosmic Duality b64 (28×64 chars) taken from jackdevs66 repo; first ~13 lines verified
  visually against salphaseion-assets/SalPhaselonCosmicDuality.png. Residual risk: last
  lines unverified against an independent archive (gsmg.io and web.archive.org are
  egress-blocked here). TODO: verify via another archive/mirror.
- SalPhaseIon tail structure (z-separated):
  `…letters… z lastwordsbeforearchichoice z thispassword z
  shabefourfirsthintisyourlastcommand [miniA b64] z? enter-binary [miniB b64]
  shabef anstoo`
  Readings: "SHA b4 — first hint is your last command", "SHA b4 answers too".
- Still-undecoded letter blocks: `dbbib…` head (165 chars, alphabet a–i) and `faed…`
  block (~1000 chars, a–i). The decoded segments used a=1…i=9, o=0, digits→int→hex→ascii.
- Phase 3.2 fully solved upstream of the inner blob: EBCDIC cp1141 → Beaufort key
  `thematrixhasyou` → Architect speech containing: "seven intertwined passwords",
  "reinserting the prime basics", "over twentythree ciphers sixteen encryptions",
  "take the private key youve earned it", "worth hundred fourty of the investment".
  VIC (digits 1,4; alphabet `fubcdora/lethingkymvpszjqwx.`) →
  "IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF
  AND THEY ALSO NEED FUNDS TO LIVE".
- 2023-02-23 official hint (binary→ascii): "yellow blue primes matrix sumlist last words
  before archichoice yinyang we wont give away thepassword its in front of your eyes but
  youre not seeing it very last step is a true give away promised" — seven components,
  matching "seven intertwined passwords".
- Phase-0 14×14 grid (materials/phase0_grid.txt), b=blue=1, y=yellow=0 proven by the
  phase-0 decode ("Yellow has a number and so does Blue" = 0 and 1).

### Pinned convention (empirical, 3 positive controls)

`openssl aes-256-cbc -a -d -pass pass:<sha256hex(password)>` with EVP_BytesToKey(SHA256)
decrypts phase2_aes (password `causality`), phase3_aes (phase-2.2 monster password),
phase3.2-aes (`jacquefresco…`). So the creator's habit: **passphrase = lowercase sha256
hex of the human answer** ("sha b4"). Harness self-test reproduces all three
(`aes_try.py self_test`). Note phase-3.2 plaintext is ~60% printable (EBCDIC section) —
acceptance rules must not assume fully-printable plaintext.

### Harness rules (false-positive control)

Accept = strict PKCS#7 AND (pad≥4 [~2⁻³² chance] OR ≥4-byte magic prefix OR head/whole
printable ≥0.85/0.90). pad∈{1,2,3} with garbage bytes is noise (observed: 3 chance
"hits" in 75k trials before tightening; the prior sessions' "cosmic_1327b_decrypted"
1-byte-pad artifact is exactly this failure mode — treat any such claim as false).

### Campaigns run (log: neo/attempts/*.jsonl)

- campaign_01: ~75k trials. Singles (labels, Matrix quotes, phase passwords, VIC/beaufort
  phrases, follow-the-white-rabbit readings) + bounded 7-token cartesian in hint order and
  SalPhaseIon order; each candidate also as sha256hex/SHA256HEX/sha256²/sha256d; against
  all 5 targets × 4 KDF variants. **No verified hit.**

### Prior-session archive

`neo/prior-sessions/2026-09-25-S1S4/` — S1–S4 scalar-construction ledger + scripts as
uploaded (that family is BLOCKED on unrecoverable S0 and stays parked; the "cosmic tree"
material it references is demoted solver-derived artifact).

### Open threads (next moves, ranked)

1. **Structural decode of `dbbib` (165) and `faed` (~1000) blocks** — sweep letter→digit
   /base-9/polybius/keyed mappings and score decodings for `U2Fsd`/`Salted__`/printable
   structure. A hit here is self-proving and likely reveals the real instructions.
2. **Matrixsumlist families** — phase-0 grid row/col sums, prime-indexed variants
   ("primes matrix sumlist" may bind: sums over prime rows/cols/cells), spiral-order
   variants (the phase-0 spiral is proven mechanics), letter-grid sums; each × format
   variants × sha-b4; test against all locks.
3. **Order/intertwine variants** of the 7 components (permutations, z-joins, interleaves).
4. **Verify cosmic blob tail** against an independent mirror.
5. Cosmic Duality image steganography angle (the yin-yang book cover) — untouched.

- campaign_02: ~28k trials. Letter blocks verbatim (head/faed/page ± spaces), column-major
  transpositions, all-divisor-width row/col sum lists (both digit maps, 3 formats),
  prime-position keeps/drops, block sums (head 422, faed 3079=prime, 3501). **No hit.**
- Decoder sweep on head/faed (digits→int→hex→ascii, base-9→bytes, letter-pair decimal/b81,
  mod-26): no printable/self-proving output. head=91 (7×13), faed=570 (19×30 etc.);
  head has no 'o' (no zero digit) → agda/cfob scheme structurally excluded for it.

### Roadmap for next iterations
1. mod-9 Beaufort/Vigenère on head/faed with puzzle-vocab keys, then agda/cfob decode.
2. 7-token order permutations (values fixed to best guesses), z/newline/space joins,
   CamelCase variants; word-number forms; "23 16 7" numbers from beaufort text.
3. Image forensics: hints/cosmic-duality-book.png + salphaseion-assets PNG (appended
   data, LSB, palette).
4. Import kaibuzz0 + remaining upstream issues as tried-lists/exclusions.
5. Independent verification of cosmic blob tail bytes.

- Mod-9 cipher sweep (Vigenère/Beaufort with 35 vocab keys, 8 Caesars, atbash) on
  head/faed, decoded via digits→int→hex→ascii: nothing scored. Logged as excluded.
- PNG forensics: repo copies of cosmic-duality-book.png / 2022-12-10-cosmic.png are
  2023 gnome-screenshot re-captures; SalPhaselonCosmicDuality.png and puzzle.png have
  clean IEND, no appended data. Stego on these *copies* is a dead end (originals live
  on gsmg.io / Telegram, both unreachable from this container).
- Book cover identified: Time-Life "Mysteries of the Unknown — Cosmic Duality".
- campaign_03 (~1.21M trials): URL-hash/"in front of your eyes" chain (89727c…, page
  caption string, all known passphrase sha256s), book vocab, 23/16/7/140 numbers,
  full 7! order permutations of the seven components (label set and value set),
  z/newline/space/dash joins. **No hit.**

Cumulative excluded trials this session: ~1.34M (see neo/attempts/*.jsonl for the
pad-valid subset; all candidates reproducible from campaign scripts).

### Loop tick 2 (2026-09-25)
- Harness: added miniB [iv||ct] layout target, raw-key mode (key=sha256 digest, -K style);
  self-test still green. 7 targets × 5 KDF modes.
- campaign_04: spiral ring sums, prime-indexed row/col/cell sums, URL byte popcounts,
  case variants (Title/UPPER, MatrixSumList spellings). No hit.
- Reran campaigns 01–03 over expanded targets/KDFs. No hit.
- campaign_05 (big bounded cartesian, pinned-convention-only s2 + {raw,sha256hex}):
  433k candidates — 7-component product with Dutch variants (geel/blauw/priemgetallen),
  long prime strings, 4-component SalPhaseIon-order product, and "sha b4 ans too"
  structures (concatenated per-answer sha256 hexes, 2- and 3-part). 3.46M trials. No hit.
- Sizes note: inner96/miniAB ct=80 fits exactly a 64-char hex privkey + LF (65→pad 80);
  miniA ct=32 fits ≤31 chars (an instruction/passphrase?). These stay the priority targets.
- Excluded: colored-cell spiral reading (restates URL — unverified/phase0_yellow_blue_counts.md).
  Page letter-grid has no intrinsic width (screenshot shows soft wrap): "the matrix" = phase-0 grid.

Next tick: harvest vocabulary from unread hint images (2020-08-02, 2021-01-21, 2021-12-02,
2021-12-25, 2023-01-09/12, 2023-08-*, 2024-*, 2026-07-12-other), add sha1-EVP mode, then
vocabulary-driven campaign 06.
