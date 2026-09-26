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

### Loop tick 3 (2026-09-25)
**Live Telegram intel (user-supplied screenshot, "GSMG Puzzle Solvers", today):**
Two 32-byte `Salted__` blobs posted by a π-named account:
`U2FsdGVkX18yZW/gbclQ5kgE0hTuyBQYgDM+3Q6iBEw=` and
`U2FsdGVkX18yZW/gbclQ5vnkmWwR8NfqVPIKhUiGDu4=`
**Analysis: both are splices of the public Cosmic Duality blob** — ct(X) = cosmic ct
block 8 (byte offset 144), ct(Y) = cosmic ct block 18 (offset 304), salt =
`32656fe06dc950e6` (= cosmic salt with first two bytes changed 2d3f→3265, tail
identical). The accompanying claim "decrypts using sha256('GSMGIO....prBe') and raw
keys" does NOT verify: tested EVP md5/sha256/sha1 ×128/256 with passphrase = caption
and its sha256hex, raw-digest keys (-K style, iv=0), in-stream IVs (preceding cosmic
block), crafted-IV equality, whole-cosmic bulk decrypt under those keys — all random
(printable ≈0.37 baseline). Verdict: community splice/noise unless a future message
supplies a different key. TG "ETA 1 hour / Congratulations?" chatter has no
cryptographic backing in the screenshot.

**New creator-source vocabulary/ops from previously unread hint images:**
- 2021-12-25 official: "some characters need to be 'zeroed out'" (+ primes required)
- 2021-12-02: acrostic THERE IS ANOTHER DOOR
- 2021-03-01: prime part uses 2,3,5,7; "too many combinations" (selection/order matters);
  Jrk: "You are at the prime part already???" (prime part is late-stage)
- 2023-01-09: "At least prime number is very important to get any further"
- 2023-01-12: "theory of everything is also still a valid path to reaching the private key"
- 2023-08-03: "shine us some 'light'"; "Are you really looking for just the btc...?";
  "the hardest part is done"
- 2023-08-06: "The puzzle talks for me"; Mr Robot last-scene wish; "Once you hit a
  'ying yang', you'll be able to solve it the same day" (recognizable checkpoint!);
  "salvation part" (SalPhaseIon wordplay); creator located in France
- 2026-07-12: "The '5' btc was never the actual prize. That was only a tiny fraction."

- campaign_06 (~355k trials): new vocab, o→0 / drop-o "zeroed out" transforms over key
  tokens, URL yellow-position zeroing, all 2357 permutations/ordered subsets alone and
  in the seven-token frame; added sha1-EVP mode. **No hit.**

Next tick: read remaining unread images (2020-08-02, 2021-01-21, 2024-*, 2020-05-11,
2020-06-07, 2021-02-12/03-14/04-16/05-06), then consider Beaufort-key reuse
("thematrixhasyou") on the letter blocks under 26-letter interpretation, and
"connect the last pieces" composite orderings.

### Loop tick 4 (2026-09-25)
- Remaining hint images read: 2020-08-02 (second half maybe another puzzle "or not at all";
  nobody found the extra door), 2021-01-21 ("a few might not require the internet
  anymore" → final stage is fully offline once you have the materials), 2024-04-19
  (halving; prizes besides banter: "a private key, some 'obscure' intel"; "see you in
  4 years"), 2024-04-10 ("1357 blocks to go" — halving countdown, also odd-digits wink).
- campaign_07 (~19k trials): char-interleaved "intertwined" composites (labels, values,
  per-answer sha256s; pad+cut modes), pairwise intertwines (half/betterhalf, yin/yang…),
  mod-26 Vigenère/Beaufort decodes of head/faed under 8 puzzle keys used as passwords,
  reinsert-2357-at-primes into rowsums, halving numbers (840000/630000/dates), 1357
  permutations. **No hit.** Mod-26 decodes also scored for English: chance-level only.

Next tick: (a) "zeroed out" digit maps — for head/faed try a=1..i=9 with each letter
X∈{a..i} remapped to 0 (9 variants/block) → int→hex→ascii; (b) letter-as-separator
segmentations (9 variants/block; segment lengths as digits, segments as digit groups);
(c) column-wise Vigenère on head 7×13 keyed "matrixsumlist" per column.

### Loop tick 5 (2026-09-25)
- campaign_08 (~4k trials): zeroed-out digit maps (each of a–i as the 0, mirroring
  agda/cfob's o=0) on head/faed → int→hex→ascii: no printable break (best 0.53 = chance);
  letter-as-separator segment-length lists; "matrixsumlist"-keyed per-column shifts of
  the 7×13 head (mod 9/26, ± , row/col-major reads). **No hit.**
- campaign_09 (~9.0M trials): dwyl words_alpha (370,105 English words) + SecLists 10k
  common passwords, raw and sha256hex, s2, vs miniA/miniAB/inner96/cosmic; integers
  0–999,999 raw+sha vs miniA/miniAB/inner96. **No hit** (2 pad-2 near-misses = chance).
  → Under the pinned convention, miniA's password is NOT a single English word, common
  password, or number ≤ 999999. It is composite/derived, consistent with the puzzle's
  established style (long concatenations + sha256).
  Wordlists (scratchpad only, not committed): words_alpha.txt (dwyl/english-words),
  10k-most-common.txt (danielmiessler/SecLists).

Cumulative logged trials this session: ~14.7M.
Next tick: two-word combinations of puzzle-core vocabulary (bounded ~1-2M), miniA-focused;
and read upstream issues index for community tried-lists worth importing as exclusions.

### Loop tick 6 (2026-09-25)
- Independent corroboration (user-shared ChatGPT status) lands where this ledger already
  is: `thispassword`-as-literal CLOSED; `thispassword`-as-reference-in-SalPhaseIon OPEN;
  the final Phase-3.2 **96-byte envelope (inner96)** is the PRIMARY authenticated lock;
  S1–S4 ±2^38 BSGS blocked (needs S0). Confirms inner96 as the right target.
- Scope note: a "reverse-engineer the signature / time-lock" idea was raised. Deliberately
  NOT pursued — recovering a key from ECDSA signatures is a generic wallet-flaw technique
  (e.g. nonce reuse), not the creator's intended decode path, and not something to build
  as general tooling. A real time-lock (CLTV/CSV) would live in a spend script, not the
  AES envelope. Staying on the intended derive-the-key-from-puzzle-content track.
- campaign_10 (~125k trials): all ordered two-token combinations of a 55-word core
  vocabulary (labels, decoded answers, Matrix/Mr-Robot terms, VIC/beaufort phrases,
  creator lines) × 5 joiners × {raw, sha256hex}, s2, vs the four locks. **No hit.**

Next tick: three-token bounded combos on the highest-signal subset for inner96; and a
careful re-read of the SalPhaseIon `shabef...` grammar (the repeated "sha b4" framing)
as a construction recipe rather than treating decoded labels as passwords.

### Loop tick 7 (2026-09-25) — the circulating XOR theory, tested end to end

Added `neo/harness/btc_addr.py`: dependency-free secp256k1 → P2PKH, validated against
canonical known-answer vectors (privkey 1 and 2, compressed + uncompressed) so that a
negative result from it is trustworthy. `neo/harness/verify_xor_theory.py` runs the test.

**Claim A.1 — CONFIRMED (arithmetic reproduces).**
XOR of sha256 over the seven published tokens
(matrixsumlist, enter, lastwordsbeforearchichoice, thispassword, matrixsumlist,
yourlastcommand, secondanswer) does equal
`a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735`. The number is real.

**Claim A.2 — FALSIFIED. This is the load-bearing failure.**
That value does NOT decrypt the Cosmic Duality blob. Tested as password (hex lower,
hex upper, recomputed) × EVP md5/sha256/sha1 × 128/256-bit, and as a raw 32-byte key
with zero IV, doubled-salt IV, and ct-prefix IV. No valid PKCS#7 + structure anywhere.
So the writeup's "known working shape: XOR(sha256(t1..t7)) → OpenSSL password → Cosmic
Duality blob" is **not** a working shape. The premise the whole XOR branch rests on is
unsupported.

**Claim B — FALSIFIED.** 121 bounded XOR candidates around the witness scalar
`abc09ead…` (XOR against the claimed key, the recomputed XOR, sha256 of each of the
seven tokens, yinyang, yellowblueprimes, half, betterhalf, the prize address, the page
caption, zero; singles and pairs) produce **zero** prize-address matches.

**Confirmed, and worth keeping:** the witness scalar `abc09ead…` uncompressed derives to
`1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M` — a genuine GSMG-prefixed vanity address, but not
`1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`. So the "witness operand, not the prize key" read is
exactly right, and now demonstrated rather than asserted. A "1GSMG" prefix is ~58⁴ ≈ 11M
work — cheap to grind — so the prefix alone carries no authority. This also matches the
prior S1–S4 ledger, which had already demoted that scalar.

**Per the theory's own stated pass condition** ("one miss → discard"; "only a scalar that
spends 1GSMG1JC… counts"), this branch is now closed. Recommend the community stop
spending time on XOR-of-token-hashes as a prize-key construction.

Method note retained from the writeup, and correct: only 32-byte scalars (or SHA256
digests) are XOR-meaningful. EC points, addresses and HASH160s are not XOR-closed, so
XORing those is category error regardless of theory.

Next tick: back to the primary lock — bounded three-token combos on inner96, and the
`shabef…` ("sha b4") grammar read as a construction recipe rather than as label-passwords.

### Loop tick 8 (2026-09-25) — 7×13 block claim tested; repo brought up to date

**Structural facts CONFIRMED and kept as a live lead.** The two undecoded letter blocks
have exact shapes: `dbbib…` head = **91 = 7×13**, `faed` = **570 = 6×91 + 24** (remainder
`ibibbibdcbahaidhfahiihic`). Seven identically shaped 7×13 matrices. Important: 13 does
**not** divide 570, so every earlier sweep in this ledger — which only used exact divisors
of the block length — structurally could not have found this. Genuine new ground.

**"KEY in the column sums" REJECTED as mask-overfitting.** Raw 7×13 column sums recorded in
`unverified/salphaseion_7x13_key_columns.md`; `faed[6]` reads `MERMLHQMIPIEK`, not the
claimed `DTEKEYUFFXGTD`, and no block spells KEY under any obvious sum→letter mapping. The
claim only appears after zeroing a chosen subset of source characters. Quantified the
freedom that buys: counting three-column windows that *some* mask can force to read KEY —
head 9/11, faed[1] 11/11, faed[2] 9/11, faed[3] 10/11, faed[4] 9/11, faed[5] 11/11,
faed[6] 11/11. **Every block can produce KEY in nearly every window**, so "only matrix #6"
is an artifact of which mask was searched, not a property of the data. A 3-letter word
bought with dozens of free binary choices is not evidence. To be persuasive a mask must be
fully specified in advance from the puzzle text and yield far more structure than one word.

**campaign_11_april** (~7.4k trials): issue #32's `lastwordsbeforearchichoice = april`,
`sha256(gsmg101adressapril)`, spelling variants and combos. **No hit.**

**Repo brought up to date** (the "reflect our status" pass):
- `README.md`: new "Current status of the endgame" section — the four locks with salts and
  provenance, the pinned decrypt convention, the 7×13 structural lead, and what is ruled out.
- `unverified/`: three new notes (XOR token hashes; 7×13 KEY columns; endgame password
  exclusions) + index table updated, following the folder's stated purpose of tracking
  approaches that don't work.
- `neo/README.md`: how to run the harness, and the self-test-before-trusting-negatives rule.

Cumulative logged trials: ~14.8M. All negatives trustworthy only because `aes_try.py`
self-tests the three solved blobs on every run.

Next: the `shabef…` grammar as a construction recipe; and for the 7×13 lead, look for a mask
that is *derivable in advance* (e.g. from the phase-0 colour positions) rather than fitted.

### Loop tick 9 (2026-09-25) — working the 7×13 lead

- **campaign_12** (~108k trials): the 7×13 decomposition read literally as "matrix sum
  list". Column/row/diagonal sum lists for all seven matrices, both digit bases, seven
  renderings each (digit-concat, spaced, comma, dashed, four letter mappings, total);
  concatenations across all seven and across faed's six; the seven block totals as their
  own sum list; the 24-symbol remainder; column-major reads; label-prefixed variants.
  **No hit.**
- **campaign_13** (~44k trials): a second structural coincidence — the faed remainder is
  exactly **24 symbols** and the phase-0 grid has exactly **24 coloured cells** (9 yellow,
  15 blue). That yields a mask *specified in advance by the puzzle* rather than fitted,
  which is the standard a mask has to meet to be credible. Tested: selection by colour bit
  (blue-keep and yellow-keep), zeroing by colour bit (the 2021-12-25 "zeroed out" hint with
  a pre-specified mask), XOR/add/sub/mul against the bits, the same mask tiled across all
  seven 91-cell matrices before column-summing, and label-prefixed forms. **No hit.**

The 24 ↔ 24 correspondence is kept as an observation. It may still be the right mask with
the wrong consumer — the bits were only applied to the remainder and to the matrices, not
yet to the blob-adjacent material.

Cumulative logged trials: ~15.0M.

### Loop tick 10 (2026-09-25) — primary material ingested; model corrected

User supplied an authenticated primary archive (raw page captures, verified decrypts, a
445-message creator transcript, 2026 site snapshots). Key files copied to
`neo/materials/primary/`. Findings written up in `unverified/salphaseion_soup_grammar.md`.

**Authenticity verified.** The Cosmic envelope (1344 B, salt `2d3f6fe06dc950e6`) and the
Phase-3.2 trailing envelope (96 B, salt `b45a5e3d827593ca`, offset 2292 of 2422) are
**byte-identical** to my working copies. This retires the risk that the Cosmic blob —
originally sourced from an untrusted LLM repo — was corrupt.

**Three model corrections, all creator-sourced:**
1. `yinyang` is an **output, not an input** (2025-04-28: "It's the next phase"; 2023-08-06:
   "once you hit a ying yang you'll solve it the same day"). Campaigns 01/03/05/10 fed it in
   as a password component — that was backwards.
2. The **prime hint IS the matrixsumlist hint** (2021-03-14 → points back at 2021-03-01,
   itself answering "which primes, 2/3/5/7?"). With Christmas 2021's "characters need to be
   zeroed out", matrixsumlist = zero at prime-derived positions, then sum.
3. The master hint yields **three inputs**, not seven: `yellowblueprimes`, `matrixsumlist`,
   `lastwordsbeforearchichoice`, then `yinyang` as the checkpoint.

**Soup grammar** (authoritative): `dbbi(91) | bin1=matrixsumlist | faed(570) |
agda=lastwordsbeforearchichoice | cfob=thispassword | bin2=enter | salph_inner envelope`,
salt `3ab585348552415d`, with `enter` spliced into the base64 at a `z`. So there are **two**
96-byte envelopes, and my `miniAB` reconstruction is the correct one.

**dbbi and faed are high-entropy data, not enciphered prose.** faed's 285 base-81 pairs use
75 of 81 symbols with a near-uniform profile (top counts 13,10,9,7,7,7,7…) against English's
steep profile (34,28,26,24,23…). No substitution or homophonic map bridges that. So faed
≈ 226 bytes and dbbi ≈ 36 bytes of ciphertext/compressed payload. Any theory that reads them
as English by choosing a mapping is fitting noise — this also independently re-confirms the
tick-8 rejection of the "KEY in the column sums" claim.

**New unsolved object**: `architect_span.txt`, 501 uppercase letters, IC ≈ 1.10 (random;
English ≈ 1.73). Not a short-key Vigenère/Beaufort, not present in any plaintext, and
known-plaintext key recovery against the Architect speech yields no repeating key. Parked
as its own object.

- **campaign_14** (~16.6M trials): the creator-authenticated recipe — 2016 matrixsumlist
  candidates from seven prime-derived zero masks across all seven 7×13 matrices, both digit
  bases, row/column axes, eight renderings; alone and wrapped in the other two authenticated
  components, raw and hashed. **No hit.**

Cumulative logged trials: ~31.6M.

Next: the exact zero-mask and sum rendering remain the gap. Since dbbi/faed are
high-entropy, the sum list is plausibly consumed as key material directly rather than read
as text. Also worth attacking: `architect_span.txt` as base-26 data, and the 2026 site
captures (`root_2026-08-19.html`, `followthewhiterabbit_2026-04-18.html`) not yet examined.

### Loop tick 11 (2026-09-25) — 2026 captures examined; faed/VIC pairing closed

**The 2026 site captures contain no puzzle content.** `root_2026-08-19.html` and
`followthewhiterabbit_2026-04-18.html`: no textareas, no hidden inputs, no meaningful
comments. More usefully, `followthewhiterabbit_2026-04-18.html` and
`phase1verification_2023-09-08.html` are **exactly the same byte length (36627)** with
different hashes — and a byte-diff shows the only differences are a rotating 40-char Laravel
`csrf-token` and the Cloudflare beacon's version string plus its SRI hash (164 bytes across
8 runs, all infrastructure). So **gsmg.io/followthewhiterabbit is the phase-1 verification
page served at a second URL**, not a new door. Closes the "is there a 2026 page" question.

**faed does NOT pair with the tiled VIC sentence.** Stated in advance rather than fished:
`faed` is 570 = 6×91 + 24 and the VIC plaintext is 91, so tiling VIC across faed is the one
forced analogue of the dbbi construction. Tested all three directions (faed−VIC, VIC−faed,
faed+VIC), mod 26.

| | victory words | dictionary words (len 5–9) |
|---|---|---|
| faed − VIC | none | **0** |
| VIC − faed | none | 1 (`ALVAH`) |
| faed + VIC | none | 1 (`HANDY`) |

Null over 3000 shuffles of faed's own multiset, same rule: dictionary-word count mean 1.1,
median 1, p95 3, max 7; victory words 0/3000. The real faed output scores **0**, i.e. at or
below chance. The null also shows the test has power — a planted victory word would stand
out, as it did for dbbi — so this is a genuine negative, not an inconclusive one.

Conclusion: the dbbi↔VIC pairing does not generalise to faed by tiling. Whatever faed is
operated against, it is not this. Consistent with tick-10's entropy result that faed carries
high-entropy data rather than text.

Cumulative logged trials: ~31.6M (plus non-AES structural tests).

Next: faed's operand remains unknown and must be named by primary material before testing;
`architect_span.txt` (501 letters, IC 1.10) is still unattributed.

### Loop tick 12 (2026-09-25) — OP_RETURN "script VM" hypothesis closed on logic

Proposal: unwrap `6a 47 <71B>` past the OP_RETURN, recurse into the payload (which begins
ASCII `G` = `0x47` = PUSH71), find it *exactly one byte short*, and borrow the adjacent
transaction byte — i.e. a puzzle-level state machine with the chain as program counter.

**The shortfall is forced, not a near-miss.** For payload length `L` with first byte `B`,
shortfall = `B - (L-1)`. Here `L = 71` and `B = ord('G') = 71`, so `L == B` and the shortfall
is identically **+1** for every such record and can never balance. The whole coincidence is
that a 71-byte record starts with `G` and `ord('G')`=71 — a fact about the label, not a
structural signal. JH and BH are the same format at the same length, so that is one
coincidence seen twice, not two independent ones.

**The carry bytes are inconsistent**: `0x0d` (JH) vs `0x4c` (BH), each the arbitrary first
byte of the following output amount. A real rule would give the same structural byte in both.
It also requires crossing the script-length boundary, which Bitcoin's encoding forbids, so
the rule cannot be inherited from Script — it would have to be asserted to rescue the
arithmetic.

**The other cited opcodes are ASCII artifacts**: `isolveditwithanabacus` starts `0x69` = `i`,
`secondanswer` starts `0x73` = `s`. Reading English as script always yields opcodes; that
they fail immediately is expected.

Correct in the source analysis and worth keeping: Script has no loops or EVAL; v0.1
OP_RETURN set `pc = pend`; modern Bitcoin errors immediately. No payload self-executes.
Nothing here is a vulnerability, and the proposed emulator was explicitly offline.

**Provenance caveat**: the authenticated archive lists "OP_RETURN dust" under *Excluded on
purpose*, so these records are not primary material; their length and first byte are taken
as given here, not verified.

Closed without needing the emulator. Reopening requires (a) provenance as primary material
and (b) a carry rule stated in advance giving the same structural byte across all records.

### Loop tick 13 (2026-09-25) — single-`t` mutation family closed, with control

Ran the proposed protocol exactly. **Positive control passes**: the `giveit` spelling opens
Phase 3.2 via sha256hex + EVP-SHA256 ("I've been waiting for you…"); `givetit` fails. So the
harness models the historical typo bypass, and its negatives are meaningful.

| tier | variants | trials | hits |
|---|---|---|---|
| tier 1 — insertion adjacent to existing `t`/`it` | 110 | 23,100 | 0 |
| tier 2 — insertion at every boundary | 606 | 127,260 | 0 |

**The creator settles it independently of the null result.** `giveit = givetit` is attested
(#867, #1602) — but so is its meaning: #1806 *"No clues to be found in those typos"*; #871 he
tested the whole puzzle three times with his own typo'd string, which is how it survived;
#898 *"no hints after stage 2 except the 't' to fix my stupid mistake"*; #3345 *"errors and
typos are mostly not intended"*. A one-off erratum with a published correction, not a
reusable operator. Typo-mining is ruled out at the source.

**`architect_span.txt` supplied** to the collaborator (501 letters, in
`neo/materials/primary/`). Constraints agreed: 501 = 3×167 so the only clean reshapes are
3×167 / 167×3; IC 1.10 rules out short-key polyalphabetic, so keying it against the token
list is fishing. The proposed film-transcript-difference test names a real operand, but the
film transcript is **not** in the authenticated archive, so running it would import
unattested text — flagged rather than run.

Ledger state: Bitcoin source/password battery CLOSED · OP_RETURN-as-secret CLOSED ·
giveit/givetit VERIFIED CONTROL · single-`t` family CLOSED · faed⊖VIC CLOSED ·
2026 captures CLOSED. Open: faed's operand (unnamed), architect_span (unattributed),
the grid (yellow/blue × primes).

### Loop tick 14 (2026-09-25) — the grid number frame, enumerated and closed

Published the exact authenticated coloured-cell spiral indices from
`matrix_grid_spiral_colors.json` (see `unverified/yellowblueprimes_grid_indices.md`):
blue `7 15 23 31 47 55 63 87 95 103 111 127 135 159 183`, yellow
`39 71 79 119 143 151 167 175 191`, colour sequence `BBBBYBBBYYBBBBYBBYYBYYBY`,
fefefe (7,4) = spiral index **163**.

**Corrects a circulating string**: the 25-char `BBBBYBBBYYBBBBYBBYYBFYYBY` with a spurious
`F` is wrong; the authenticated sequence is 24 chars, one per byte. Schedule-driven parses
built on the 25-char form are parsing a typo.

**Key structural point**: 1-based, every coloured index is a multiple of 8, so **none is
prime**. A prime subset exists only 0-based: `7 23 31 47 71 79 103 127 151 167 191`.

**A tempting coincidence, rejected**: there are exactly 9 primes ≤ 24 and exactly 9 yellow
cells (15 non-primes, 15 blue) — but yellow's positions intersect the prime positions only
at 5 and 19 (2 of 9). The 9/15 split is forced by the URL's LSBs, so the count match is a
coincidence of 24, not prime structure.

- **campaign_17** (66 candidates, 24,192 trials): every prime/`{2,3,5,7}` selection and
  zeroing of the URL, colour sequence and index list, both index bases; prime spiral
  indices; blue/yellow lists; sequence as 0/1 both polarities; 9/15 counts; fefefe values —
  each alone and wrapped with the other two authenticated components, raw and hashed.
  **No hit.**

Open and unchanged: whether `yellowblueprimes` consumes these indices at all, or names a
selector applied to the letter blocks with the grid only supplying the mask. Also still
open: an operand for `faed` named by primary material.

### Loop tick 15 (2026-09-25) — the YOUWON tail is not a hex key, structurally

Tested the last hopeful reading of the confirmed `dbbi ⊖ VIC` output: its 64-character tail
is exactly hex-private-key length, so does it encode one?

**No, and not because a guess failed.** A hex key written in letters requires exactly 16
distinct symbols. The tail uses **24** (A7 X5 D5 G4 B4 N4 P3 J3 U3 M3 C2 K2 W2 V2 T2 Y2 L2
E2 S2 F1 Z1 R1 O1 Q1). No injective letter→hex map exists, so every mod-16 reduction is
lossy — three letters collapse onto each digit — and whatever key emerges is an artefact of
the chosen reduction, not a recovery.

Ran three reductions regardless (A0 mod16, A1 mod16, A0 div2). All three yield valid
secp256k1 scalars; none derives the prize address. **That all three are "valid" is the
warning**: any 64-symbol string reduces to a valid scalar, so validity carries zero
evidential weight here.

Strengthens the marker reading: `YOUWON` confirms the *operation*, and the 21+64 characters
around it are residue of that operation rather than payload. The tail should not be treated
as key material again.

Closed to date: Bitcoin source/password battery · OP_RETURN-as-secret · single-`t` family ·
faed⊖VIC tiling · 2026 captures · grid prime readings · YOUWON-tail-as-hex.
Open: an operand for `faed` named by primary material; whether `yellowblueprimes` selects on
the letter blocks rather than the grid; `architect_span` (unattributed, not to be keyed).

### Loop tick 16 (2026-09-25) — "yellow brick road" reading tested

Prompted by the white-rabbit / yellow-brick-road idiom parallel. Two parts, both negative.

**Geometry.** The 9 yellow cells are not scattered: they contain a clean 4-cell diagonal
`(4,9)→(5,10)→(6,11)→(7,12)` and a 2-cell diagonal `(9,6)→(10,7)`, with `(0,13)`, `(5,6)`,
`(12,9)` isolated. A "road" reading is visually tempting.

Null-tested properly — draw 9 of the 24 candidate coloured slots (which themselves lie on
the spiral, so consecutive slots are often diagonal neighbours; the null inherits that
geometry). Over 200,000 draws the longest-diagonal distribution is
`{1: 47900, 2: 106754, 3: 35235, 4: 8418, 5: 1567, 6: 126}`, giving **P(run ≥ 4) = 0.051**.
So a 4-run occurs about one time in twenty by chance, and this was noticed *post hoc*.
Suggestive, not significant. **Not promoted.**

**Vocabulary.** campaign_18_oz, 17,850 trials: the full Oz lexicon (yellow brick road and
follow-variants, Oz/wizard/Dorothy/Toto/Emerald City/Glinda/Scarecrow/Tin Man/Cowardly
Lion/Munchkin/Kansas, "no place like home", ruby slippers, over the rainbow, the man behind
the curtain, surrender Dorothy, wicked witch), alone and combined with the authenticated
components. **No hit.**

Worth recording as a near-miss of reasoning rather than of data: the idiom parallel is real
(the puzzle's phase-1 password was itself a song lyric), but neither the geometry nor the
lexicon carries it.

### Loop tick 17 (2026-09-25) — Telegram salt re-confirmed; the 24↔24 alignment tested

**The `32656fe0…` salt is not new and not a mistype-only story.** Already analysed in
tick 3: it differs from the Cosmic salt `2d3f6fe06dc950e6` in the first two bytes only, and
— the part worth keeping — **its two ciphertexts are literal splices of the public Cosmic
blob**: `X` = cosmic ct block 8 (offset 144), `Y` = cosmic ct block 18 (offset 304). So it is
neither a second envelope nor plaintext π; it is cut-and-pasted public bytes with a doctored
salt. Re-verified this tick.

**The genuinely good structural point**, and it is parameter-free:

```
dbbi length            = 91
primes <= 91           = 24   (2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89)
coloured cells         = 24   (15 blue, 9 yellow)
```

The 24 colour bits map one-to-one onto the 24 prime positions of dbbi. That is
`yellowblueprimes` and "some characters need to be zeroed out" as a *single* instruction with
nothing free to tune — much better motivated than any mask tried so far.

Built it. The only variation is unavoidable convention (index base, which colour zeroes,
digit base, axis, rendering) plus "add/sub, not replace".

- **The cited strings do not reproduce.** Neither `RUSHMLKVTGIAG` nor `PVYWIAEEYKNAZ`
  appears under any of the 16 parameter-free variants of this construction. They were
  computed some other, unstated way, so they are **not** verified operands and the
  "yin/yang pair" framing around them is not established. The 16 strings this construction
  actually yields are recorded in the tick output (e.g. base0/zeroY/b1 col A1 →
  `BFIFXGOHAFXZL`).
- **campaign_19** (2352 candidates, 409,920 trials): the mask across dbbi and all six faed
  matrices, both bases, either colour zeroing, both digit bases, zero/add/sub modes, row and
  column axes, seven renderings. **No hit.**

So the best-motivated mask in the session is enumerated and empty. Recorded because the
alignment is real and someone will rediscover it; the negative is the useful part.

Also filed per that note, and consistent with this ledger: the 12:00 photo is Reloaded lore
(the 314-second window, the midnight shift change), not a grid operand, and neither it nor
the doctored header enters the password battery.

### Loop tick 18 (2026-09-25) — the two recurring claims, measured

Agreed with the five verdicts (corridor gloss = film flavour; the "impossible to decrypt"
quote is unverified and contradicts the 2023 hint; "source is raw data" is already on the
board as DBBI/FAED; "3.2 → 32" is filename numerology; window=32 / IV=0 drops). Made two of
them quantitative — see `unverified/why_false_decrypts_recur.md`.

**The IV is KDF-emitted.** For the known-good Phase-3.2 decrypt, EVP_BytesToKey emits
key `f4c72c3a…` *and* IV `b620574d04ee253df257fcd340eb201f`. Not chosen.

**Important nuance that makes zero-IV claims look credible**: the correct key with a zero IV
still prints ~94% readable text, because in CBC a wrong IV corrupts only the first 16-byte
block and the stream self-heals from block 2. So a zero-IV "decrypt" can look like a hit and
is not one. The decisive direction is the converse — a wrong key gives nothing readable for
any IV — so "IV = 0" is not a construction: it still requires naming the 32-byte key, which
is the entire problem.

**Padding is a 1-in-256 coincidence, measured**: against the real 80-byte ciphertext with
random keys, 300,000 trials gave **1,235 PKCS#7-valid** results (1 in 243; theory ~1 in 256)
and **0** that also passed this harness's gate. So a 100k-candidate battery throws ~400
padding-valid results by chance — the complete explanation for the recurring Cosmic
"decryptions", and a validation of the pad≥4 / magic / printability rule.

Rules of thumb now on record: a 1-byte pad with a non-printable body is noise, always; a
claim that names an IV but not a key has specified nothing; and "it yields a valid
key/padding/address" is never evidence, since every 64-symbol string gives a valid scalar
and 1 in 256 keys gives valid padding.

### Loop tick 19 (2026-09-25) — provenance pass: instructions, not coincidences

Agreed with the demotion of `RUSHMLKVTGIAG` / `PVYWIAEEYKNAZ` (reproducible ≠ compelled;
I could not reach them from any parameter-free construction, and the stated chain fixes a
digit map `d=0,b=1,i=2,f=3,h=4,c=5,e=6,g=7,a=8` that is itself a choice). Skipped the
redundant add/sub rerun — campaign_19 covers it. Ran the provenance pass instead.

**Only 10 of 510 rows are creator-authenticated (HINT/CONFIRM) on prime / zero / yellow /
blue / matrixsumlist / dbbi / faed / yin-yang across seven years**, and the archive's own
tags separate them into three scopes:

| thread | tag | when |
|---|---|---|
| yellow / blue | **P0** | 2020-01 poem, 2020-05 "answer is there", 2020-05 "First or zero" |
| primes / matrixsumlist | **SAL** | 2021-03 prime part, 2021-03 matrixsumlist→prime hint |
| the combined list, yin-yang | **COS** | 2023-02 master binary, 2023-08, 2025-04 |

**The overlooked item**: `#4105 2020-05-21 HINT "First or zero"`, tagged P0, immediately
after `#4102 CONFIRM "answer is there"` and `#4096` re-pointing at the poem. Two live
readings — (a) it answers "Yellow has a number and so does Blue" with **1 and 0**, or (b) it
disambiguates "first puzzle piece" = "phase zero". Under either, **`yellowblueprimes` is not
licensed to mean "9, 15, primes"; under (a) that is positively excluded.**

Consequences recorded in `unverified/creator_hint_provenance.md`:
- The 9/15 counts have **no creator warrant**. Every construction here that fed `9`/`15`/
  `915`/`159` used a community inference, not an instruction.
- `yellowblueprimes` as one atomic operator is unsupported — the token occurs once, inside a
  2023 list that otherwise names already-solved stages and is followed immediately by
  "we wont give away the password / it's in front of your eyes". That list reads as a
  **table of contents**, not a recipe.
- The prime instruction is scoped to **SalPhaseIon**, anchored only by the 2021-03-01
  2/3/5/7 exchange plus 2021-12-26 "some characters need to be zeroed out".

Ledger per the agreed state: CLOSED adds prime-cell add/sub (covered by campaign_19).
DEMOTED adds RUSHMLKVTGIAG, PVYWIAEEYKNAZ, and 24→24 insertion-from-equal-lengths.
OPEN: exact DBBI decoder, exact FAED decoder, and now — sharpened — what the P0-scoped
yellow/blue answer actually contributes, given it is not counts.

### Loop tick 20 (2026-09-25) — stage chaining tested and closed

Agreed on the OpenSSL analysis (independently proved last tick: the `Salted__` magic is
written only in password mode, so a password provably exists and the IV is not a free
input). Held position on the third-door oracle: that address is absent from the
authenticated archive — which excludes that dust family by name — and hunting an unknown
preimage by hashing candidates is brainwallet grinding regardless of intent. Not built.

**Outside-the-box test actually run**: the one *confirmed* operation is `dbbi ⊖ VIC`
(planted YOUWON, 0/200k null). Chained puzzles normally feed a stage's output forward as the
next stage's key — and stage 1's outputs had never been used that way. So:

```
stage 1 (confirmed): VOZIJBDTIQBRGVEOMZNBC YOUWON XCPKW…QTSGA
                     [--- prefix 21 ---]        [--- tail 64 ---]
stage 2 (new test):  faed(570) ⊖ / ⊕ {tail64, prefix21, full91, YOUWON, + reversals}
```

Operands named in advance; all six keys × two directions.

| | dictionary words | special |
|---|---|---|
| best variant (tail64, sub) | 1 | none |
| null (3000 shuffles of faed, same rule) | mean 1.0, median 1, p95 3, max 6 | 3/3000 |

Real sits at the **37th percentile** of its own null — indistinguishable from chance. The
null also shows the test has power (special words appear in only 0.1% of shuffles), so this
is a genuine negative. **campaign_20_chain** additionally fed all 48 stage-2 outputs (plus
lowercase and first/last-64 slices) to the locks: 10,080 trials, no hit.

So stage chaining is closed: the YOUWON output does not key faed. Combined with tick 15
(the tail is not a letter-encoded hex key, 24 distinct symbols vs 16 required) and tick 11
(faed does not pair with tiled VIC), the confirmed dbbi operation appears to be
**terminal** — a marker, with no forward link discovered from any of its outputs.

Running total ~32M logged trials. OPEN remains: the exact FAED decoder, and what the
P0-scoped yellow/blue answer contributes given the provenance pass showed it is not counts.

### Loop tick 21 (2026-09-25) — the π chain verified, quantified, and traced to a dead premise

**Every arithmetic step in the proposed chain is correct.** Verified independently:
9th prime = 23, 15th prime = 47, π[9] = 3, π[15] = 3, π[23] = 4, π[47] = 7. No errors.

**But π[9] == π[15] is a 10% coincidence.** Among the first 200 fractional digits, equal
pairs occur 1968/19900 = **9.9%** — π digits are ~uniform, so *any* two positions match about
one time in ten. "They are both 3" is therefore an ordinary event, and the déjà-vu / glitch
reading is a narrative fitted after seeing it. The follow-on `π[23]=4, π[47]=7 → "47"`
recurring as the 15th prime is self-reference selected post hoc: the chain was extended until
something repeated.

**The load-bearing failure is upstream of all of it.** The chain starts from Yellow = 9,
Blue = 15 — the *cell counts*. Tick 19's provenance pass found those counts have **no creator
warrant**: the 2020-05-21 HINT "First or zero" (tagged P0) follows the poem and "answer is
there", and the colouring independently just restates the URL's own byte LSBs. If "Yellow has
a number" resolves to **0/1** rather than 9/15, then primes(9), primes(15), π[9] and π[15]
all inherit nothing. Each step is valid; the input is not established.

**The raw-K/IV experiment — genuinely different, and run.** Not a password battery: direct
AES-256-CBC(K, IV) with no KDF, no salt derivation, strict gate (padding alone never
accepted). 23 source-derived 32-byte keys × 20 source-derived 16-byte IVs × 4 targets
(P32T ciphertext and whole file, cosmic ciphertext, miniA ciphertext) = **1,840 direct
decrypts, 0 hits.**

Key material drawn only from authenticated two-part objects: sha256 of each decoded token,
the VIC sentence, the confirmed stage-1 output, dbbi, faed, the 24-bit colour mask and the
196-bit grid, both 32-byte cosmic halves, and zero. IVs from sha256/md5 of the same, the
colour bits, doubled salts, and zero.

So the raw-key model is now tested rather than merely doubted, and it is empty on this
material. Combined with tick 20's proof that the `Salted__` magic is emitted only in
password mode, the password path remains the only one with positive evidence behind it.

### Loop tick 22 (2026-09-25) — π as raw key/IV: exhaustively closed

Ran the proposed test as a **superset** of the suggested script. That script checked roughly
30 combinations (offsets 0/9/15/23/47) and accepted on `unpad` alone — i.e. PKCS#7 only,
which tick 18 measured at a **1-in-243 false-positive rate**, so it would have reported
spurious successes at scale.

Instead, exhaustively, with the strict gate:

- π computed locally to 1200 digits (spigot, no external data)
- both the fractional expansion and the full `3.`-prefixed form
- both byte interpretations: ASCII digits, and digits packed as nibbles
- **every** key offset 0–199 × **every** IV offset 0–199, not just the five proposed
- 4 targets: P32T ciphertext and whole file, cosmic ciphertext, miniA ciphertext
- plus sha256 of π prefixes at 6 lengths as key, against 5 IV offsets

**640,480 direct decrypts, 0 hits.**

So the family is closed far beyond "simple ASCII π segments": no offset of π, in either
digit encoding, as key and/or IV, opens any lock.

**Two corrections to the proposed method, both worth keeping:**

1. `unpad`-only acceptance is not a success criterion. Padding alone is a 1-in-243
   coincidence on these ciphertexts; a sweep of this size would have thrown ~2,600 false
   "successes" under that rule. The gate must require pad ≥ 4, a ≥4-byte magic, or high
   printability.
2. The "re-insert a dummy `Salted__` header and brute-force the password" step **cannot
   work**, and not merely because P32T already has a real header. The salt is an *input* to
   `EVP_BytesToKey(password, salt)`. Substituting an invented salt derives a different key,
   so the original plaintext is unreachable no matter how many passwords are tried; you
   would additionally have to brute-force the true 8-byte salt (2⁶⁴).

Endorsed without reservation: **do not execute unknown binaries.** Decrypting data is safe;
running what comes out is not. Static analysis only, and an isolated VM if it ever comes to
that. Nothing in this repo requires running third-party code.

### Loop tick 23 (2026-09-25) — the déjà-vu / 314 glitch, taken literally and closed

Took the film metaphor to its one genuinely cryptographic meaning. **A glitch in the Matrix
is seeing the same thing twice; in a ciphertext that is a repeated block.** Under CBC with a
random IV a repeat is ~2⁻⁶⁴ per pair, so finding one would be real signal — it would mean
ECB, or a reused IV/keystream. That is a proper test, not a metaphor.

**Result: no duplicate blocks anywhere.**

| blob | blocks | distinct | duplicates |
|---|---|---|---|
| cosmic ct | 83 | 83 | **0** |
| P32T ct | 5 | 5 | **0** |
| miniA ct | 2 | 2 | **0** |
| miniB raw | 3 | 3 | **0** |

So the envelopes are well-formed CBC with no structural anomaly. There is no glitch in the
ciphertext to find, which also independently re-confirms they were not made in ECB.

**314 as a position**: nothing distinguished. `cosmic[314]`, `faed[314]='c'` (`ichi` in
context), soup`[314]='a'`. **314 as a window**: faed admits 314-length slices at offsets
0–256; their IC is flat (min 1.043, median 1.088, max 1.124), so no window is a real
segmentation. **Longest repeated substrings**: dbbi `egge` (4), faed `aedgg` (5) — short, as
expected from the earlier entropy finding.

**campaign_21_pi314** (17,220 trials): 314 / π / window-of-opportunity / déjà-vu / black cat
/ 12:00 / midnight / shift-change / Keymaker / corridor / two-doors vocabulary, alone and
combined with the authenticated components. **No hit.**

With tick 22's exhaustive π-as-key/IV sweep (640,480 decrypts) this closes the π/314 thread
in all three of its forms: as key material, as an index, and as the déjà-vu structural
signature. The metaphor is film flavour; the ciphertexts are ordinary well-formed CBC.

### Loop tick 24 (2026-09-25) — the π-handle "0b1one|" claim: unverifiable, and its own test fails

**Cannot verify the premise.** The Telegram handle renders in *every* screenshot supplied as
`3.14159265358879323846264338327...` — 29 fractional digits before Telegram's ellipsis. The
claimed insertion sits after fractional digit **50**, i.e. beyond the truncation in all
available images. Nothing in the material shows `0b1one|`. (The claim's π arithmetic is
right: digits 1–50 are correct and the true continuation is `5820974944592…`.)

Even granting it: a participant's display name is not authenticated puzzle source, as the
claim itself concedes.

**The proposed test was run and returns negative.** The suggested criterion was: does `11`
occur independently in authenticated material in the Phase-0 / prime / zeroing chain? It does
not. That chain supplies **9, 15, 24, 91, 196, 570** — no 11. The only `11` in authenticated
material is inside phase-2.2 part 5 `11110`, a 5-bit string already consumed as a solved
component of the phase-3 password; its `11` is a substring of a bitstring, not an independent
quantity.

**And the other half is already demoted.** The `9` comes from Yellow = 9, which tick 19's
provenance pass showed has no creator warrant — "First or zero" (2020-05-21, P0) points at
0/1, and the colouring independently restates the URL's own byte LSBs.

**campaign_22_911** (12,180 trials): `911`, `9:11`, `0b1one`, `0b1`, `one`, `oneone`, `11`,
`nineeleven` and variants, alone and combined with the authenticated components. No hit.

So by the claim's own stated standard — *"if it does, 9:11 stops being dependent on personal
recurrence and becomes source-derived"* — the condition is not met.

### Loop tick 25 (2026-09-25) — "what two numbers?" — the creator answered it

Ran the proposed enumeration: canonical scalar summaries of the authenticated blue/yellow
sets, then only prime-licensed operations, with an explain-something-authenticated gate
before any ciphertext. Also flagged the correction that the ledger was missing.

**The creator answers the question directly.** The chain is one P0 thread:

```
2020-01-14  HINT     "Yellow has a number and so does Blue. Go back to the first puzzle piece"
2020-05-20  META     re-points to that poem as THE hint
2020-05-21  CONFIRM  "answer is there"
2020-05-21  HINT     "First or zero"        <- tagged P0 HINT2020
```

Four months after posing it, in the same thread, he says **"First or zero"**. That is the
most direct available answer to "what exact two numbers?", and it says **1 and 0** — not 15
and 9. It also matches what Phase 0 already uses (blue=1, yellow=0) and the independent
finding that the colouring merely restates the URL's own byte LSBs. So `blue count = 15` /
`yellow count = 9` should move from AUTHENTICATED to *derived measurement* — true of the
image, but not what the hint is pointing at.

**The enumeration** (all ten summaries):

```
blue.count 15   sum_urlbyte 142  sum_spiral 1241  sum_row 98  sum_col 73
yellow.count 9  sum_urlbyte 134  sum_spiral 1135  sum_row 58  sum_col 83
```

Prime-licensed results: `15 → 15th prime 47`, `9 → 9th prime 23`; neither 47 nor 23 is an
authenticated quantity of this puzzle. `15+9 = 24` matches the coloured-cell count, but
trivially — there are 24 cells, so the sum of the parts is the whole; it explains nothing.

**Gate result: nothing explains an authenticated quantity it did not start from.** The family
is closed without touching a ciphertext, exactly as proposed.

One honest observation, not promoted: both column sums are prime (blue 73, yellow 83). Around
that magnitude prime density is ~1/4.6, so both being prime is ~1/21 — and it is 2 of 10
summaries, i.e. selected after looking. Recorded, not elevated.

Agreed and filed: `15/9 → O/I → Base58` is analyst-created; the `2,3,5,7` enumeration is a
solver's characterisation rather than primary text (the authenticated statements say only
that primes are required and important); and the π-handle content cannot supply an operand
unless the account is shown to be creator-controlled.

### Loop tick 26 (2026-09-25) — the proposed pipeline is complete; final stage run

A six-stage pipeline was proposed. Five stages were already executed in this session; the
sixth (Bitcoin v0.1 constants) was genuinely untested and is now run. Status:

| stage | status | result |
|---|---|---|
| Header check (`Salted__`?) | done (tick 20) | **YES** on all locks — and the magic is emitted *only* in password mode, so a password provably exists |
| Raw AES-256-CBC, no KDF | done (tick 21) | 1,840 direct decrypts, source-derived K/IV — 0 hits |
| π candidates (ASCII/nibble, offsets, sha256 slices, déjà-vu) | done (tick 22) | **640,480** decrypts — all offsets 0–199 × 0–199, both encodings — 0 hits |
| Matrix glitch / duplicated values | done (tick 23) | 0 repeated blocks in any blob; 314 not distinguished as index or window |
| **Bitcoin v0.1 constants** | **new this tick** | genesis hash, merkle root, nonce 2083236893, timestamp 1231006505, bits 0x1d00ffff, version, coinbase string (and its reversed/hex forms as used in phase 2.2 part 6), genesis address, satoshi/nakamoto vocabulary — **13,020 passphrase trials + 792 raw-K/IV decrypts, 0 hits** |
| Static analysis of binaries | N/A | no binary exists in the corpus; nothing to analyse |

The Bitcoin-constants stage was the best-motivated of the untested ones, since phase 2.2
part 6 provably used the genesis coinbase message (hex-encoded, reversed). Testing the same
family again at the endgame was reasonable. It is empty.

**Answer to the proposed immediate check** (`xxd -l 64 p32t.enc`): the file begins
`53 61 6c 74 65 64 5f 5f` = `Salted__`, followed by salt `b45a5e3d827593ca`, then 80 bytes
of ciphertext. Per tick 20 that *settles* the branch rather than opening it: raw `-K/-iv`
mode writes no header at all, so the header's presence is positive evidence of the password
path, not a reason to pursue raw keys.

Cumulative ~33M logged trials across 23 campaigns. The pipeline is exhausted; the open work
remains the FAED decoder and the bit-selector reading of yellow/blue implied by
"First or zero".

### Loop tick 27 (2026-09-25) — zero-injection decode of faed/dbbi: negative

Best remaining source-grounded lead, run. Logic: faed and dbbi use letters **a–i only**
(no `o`), while the sibling tokens `agda`/`cfob` decoded with the map `o=0, a=1…i=9` →
concatenate digits → decimal int → hex → ASCII. So "some characters need to be zeroed out"
may be the instruction that *injects* the missing `o` (zero) into faed/dbbi, after which the
same sibling decode could apply.

Tested: zero-inject at prime positions (0- and 1-based, prime and non-prime), and at the 24
colour-bit positions mapped to the 24 primes ≤ 91 (both polarities), then the exact
agda/cfob decode. **Every result is ~33–45% printable — garbage.** No readable text, no token,
no structure. faed and dbbi remain high-entropy under this transform too, re-confirming the
tick-10 entropy result.

This was the last well-motivated, source-named decoder hypothesis on the board. With it
negative, the honest state is that **no source-named operand or decoder for faed has been
found**, and the confirmed dbbi operation (⊖ VIC → YOUWON) is terminal (tick 20). The puzzle
is not solvable from the material in hand by the systematic methods available in this session.

### Loop tick 1b (2026-09-25) — 2×14 board coordinates vs P32T, preregistered and parked

Ran exactly as preregistered: narrow, P32T-only (salt b45a5e3d827593ca), two fixed boards
reported separately and never blended, no new vocabulary, strict gate, Cosmic excluded.

Boards (2 rows × 14 cols):
- A = `FUBCDORA.LETHINGKYMVPS.JQZXW`
- B = `fubcdora/lethingkymvpszjqwx.`

**Step 1 — removed-material selector** (`KING`, `QUEEN`, duplicate `C`, then `KING||QUEEN||C`
and `QUEEN||KING||C` only). Coordinates in word order, serialized as: column 0/1-based, row
bits, interleaved (row,col) 0/1-based, packed coordinate bytes, decimal-ASCII, board-char
control. Each raw and sha256hex, × EVP-{md5,sha256}.

**Step 2 — checkerboard numbering** (two rows → two straddling-checkerboard branches, columns
→ 14 positions; both row assignments; digit-ASCII, nibble-packed; no arbitrary digit perms).

Protocol: candidate → {raw, sha256hex} × EVP-{md5,sha256} × P32T only. Strict PKCS#7 +
structure gate.

**Result: 182 trials per board, 0 hits, 0 near-misses. Both boards negative.**

Per the preregistered stop rule — "if both removed-material coordinates and canonical
checkerboard numbering miss under this frozen protocol, park the chess-board/P32T branch" —
**the chess-board/P32T branch is parked.** The 2×14 observation (VIC sentence is 91 chars = the
dbbi length; the 28-symbol alphabet is 2×14) remains structurally elegant but yields no
justified next reading rule. Not blended, not widened, not re-run with new vocabulary.

### Loop tick 28 (2026-09-25/26) — Cosmic closure of the tick-1b set; the constraint sheet; the genesis image re-read

**1. The tick-1b token set against Cosmic — closed.** The requested "57-token" list is not in
this repository (the ledger records tick 1b as 182 trials per board, and the campaign_24 logs
are empty because only pad-valid results are logged), so the set was regenerated from
`campaign_24_board.py`: **50 distinct raw candidate strings** (the two boards share every
coordinate, so their union is one set; written to `neo/attempts/campaign_25_tokens.txt`).
Protocol exactly as requested: each token raw and as sha256hex × EVP-MD5 and EVP-SHA256 ×
Cosmic only (salt `2d3f6fe06dc950e6`, ct 1328 B), strict gate.
**campaign_25: 200 trials, 0 hits, 0 pad-valid results.** If the user's 57 contained tokens
outside tick 1b, those seven were never in this repo and must be supplied; everything that
was here is now closed against Cosmic as well as P32T.

**2. Constraint sheet written and fact-checked** — `unverified/endgame_constraint_sheet.md`.
Operands, operators and representations per official hint, each graded (AUTH / PRIMARY /
DECODED / DERIVED / READING / LORE-BANTER-META / APRIL / USER / NEGATIVE / POLICY), with
frozen tables B0–B3 and C0–C3. Five independent refuters attacked the sections against the
primary files; the substantive corrections (all folded in):
- the sheet had labelled artefacts and interpretations AUTH; a PRIMARY grade and a READING
  grade now separate "the creator said" from "the archive contains" and "we read it as";
- `yinyang`: the three creator lines make it a *phase reached after the wall* (#9599, #39224,
  #39237); "output of a decryption / not an input" is our reading of them. The combine row
  now reads `A‖B‖C` — the earlier draft fed D back in, the exact pattern correction 1 retracted;
- "First or zero" (#4105) has no preserved question; three readings stay live (1/0; phase
  zero; index base), so the 9/15 counts are unlicensed rather than excluded;
- primes: the AUTH content is only "required"; the selector model is a reading, and the tie to
  `matrixsumlist` rests on the META reply context of #6509;
- `{1},{4},{21}` is archive-tagged HINT and downgraded to APRIL by the sheet (#7529, #6913
  "1812 bit" = RAB-bit); #70307 "Pfff. Coincidence." reacts to an unarchived solver post and
  neither confirms nor denies anything;
- the close-friends hint is #66573/#66574 (HINT, tag KEY, 2026-07-13): friends' knowledge
  *plus* skill, not "biographical rather than technical".
Every numeric value in the operand table reproduces (spiral, colour indices, 0xF73D92, sums,
91/570/24, the dbbi−VIC string, the 24 primes).

**3. The genesis image, whole.** `puzzle.png` is byte-identical to the archive's
`02_pages_raw` capture (sha256 `38125bbd…`), and it is 1048×1556, not a bare grid:
- the QR code decodes to `https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`
  — the prize link, nothing hidden;
- the **rabbit** is pixel art on a 15-px lattice, 14 × 13 lattice cells, 37 black pixels,
  drawn over cells (6,6),(6,7),(7,6),(7,7),(7,8),(7,9),(8,6). The spiral's four unused end
  cells are exactly (6,6),(7,6),(7,7),(6,7): the poem's "rabbits nest" is the spiral's centre.
  Read as bits under every attested encoding (row/column order, both polarities, bit- and
  byte-reversed) it yields no printable output (best 0.32). It is a drawing. Saved as
  `neo/materials/rabbit_bitmap.txt`;
- the colours have literal numbers: yellow `#FFF200` (2⁹·181²), blue `#3F48CC`
  (2²·3·37·9341), the red rule `#ED1C24`, the off-white `#FEFEFE` (2·3·7·13·127·241). A
  fourth reading of "Yellow has a number and so does Blue", never tested here before.

**4. Bounded offline address oracle** — `neo/harness/addr_check.py`: six fixed encodings
(sha256, sha256d, hex64, zero-padded raw, bit-reversed sha256, byte-reversed sha256) ×
compressed/uncompressed, against the prize address, the README second address and the
user-supplied `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` (USER grade: absent from the archive;
block explorers are egress-blocked, so its history is unverified). Capped at 2000 objects
per run so it stays an oracle for named objects, not a grinder.
- campaign_26: every object named in the sheet (49) → 458 addresses, **0 matches**;
- campaign_27: the colour codes in hex/decimal/packed, singly and yellow‖blue / blue‖yellow
  (34) → 340 addresses, **0 matches**.

### Loop tick 29 (2026-09-26) — the Base58 frame, verified and closed

User frame: soup letters `a…i` are Base58 glyphs 33–41, not digits, when the object is a
Bitcoin value; the puzzle's numbers should be written in Base58; slot A is the colour
integer `f73d92`, not a spelling of `yellowblueprimes`; "zeroed out" = delete the
Base58-illegal set `{0,O,I,l}`; Base58Check is the only encoding the prize wears in public.

**Arithmetic verified** (validated against the canonical Bitcoin alphabet):
- row sums `610876654997879` → `5mfhF9tp6`; col sums `8108108736759668` → `26KBGX9uKH`;
  rows‖cols → `7RUyS4gBTMenM76Fcf`; `f73d92` = 16203154 → `2S3dj`; prime-subset `445` → `8g`.
  All match.
- **One correction**: the complement (Y=1,B=0) `574061` encodes to **`3wec`**, not the
  stated `3Q9h`. Used `3wec`.
- `yeowbueprimes` (label minus `l`) is legal Base58 and decodes to
  `82101348098033013316316` = 10 bytes `1162b9166f936e795adc`; reproduces the user's value.
- **Whole-block Base58Check fails** for `dbbi` (91→67 B) and `faed` (570→418 B): both are
  legal Base58 strings but neither is a valid version+payload+checksum. So neither block is a
  hidden address/WIF. Confirmed; do not slice them for a `1…`/`5…`/`K…` prefix.

**campaign_28_base58 — the bounded test, run through the self-testing harness.**
Slot A = the colour integer in every representation (`f73d92`, `F73D92`, `16203154`,
`0xf73d92`, `2S3dj`, the complement `08c26d`/`574061`/`3wec`, the prime-subset `445`/`8g`/
`110111101`, the zeroed label `yeowbueprimes`/its decimal), plus a "delete `{0,O,I,l}`"
variant of every slot value. B and C = the frozen sheet sets and their Base58 forms.
Combine A‖B‖C (the §6 join), each raw and sha256hex, EVP-MD5 and EVP-SHA256, against
**cosmic, inner96 (P32T) and miniAB (salph_inner)**: **1672 combine candidates + 19 A-alone,
20,292 trials, 0 hits, 0 pad-valid near-misses.** Address oracle on the A family and each
`A‖matrixsumlist‖lastwordsbeforearchichoice`: 342 addresses, **0 matches** to prize / second
/ `1NULY7`.

So the colour integer as slot A, in every Base58/hex/decimal/zeroed representation and
combined with the frozen B and C, opens no lock and derives no target address. The Base58
*representation* frame is closed. Base58 stands only where it is actually attested: as the
last-mile dress of the answer (WIF `5`/`K`/`L`, or `1GSMG1…`/`17ucy1…` from a hash160), i.e.
an oracle for a real hit, not a way to brute the blob. What is still missing is unchanged: a
*further named operation* on `f73d92` (the SAL-scoped primes/zeroing) that yields a
recognisable object before AES — not another spelling of the label.

### Loop tick 30 (2026-09-26) — the P32T last-block freeze oracle; the two halves; a reading tension

User frame: P32T is 80-byte CT, 5 CBC blocks; the last block `P5 = D_K(C5) XOR C4` depends
only on K (C4, C5 are known ciphertext), so it is an **IV-free** test. If the plaintext is
two raw 32-byte keys (64 B content), `P5 == 0x10 * 16` — a 128-bit accept test, far sharper
than the 1-in-243 PKCS#7 filter. Stop hashing VIC strings; find the *operation* on the two
named halves (HALF / BETTER HALF = the on-chain `1GSMG1…` and `17ucy1…`), not another spelling.

**Built `neo/harness/p32t_freeze.py`** — the IV-free oracle, self-tested (accepts the key that
padded a synthetic 64-byte plaintext, rejects a wrong key). `C4 = d9f7ff6e…`, `C5 = 5334de08…`.

**A reading tension the freeze surfaced, and resolved into a fuller oracle.** `0x10*16` tests
only the 64-byte reading. The repo's own primary reading of P32T is "64 hex chars + a
newline" = **65** bytes, whose last block is `0x0a || 0x0f*15`, which the `0x10*16` test would
reject. So a key correct under the hex+LF reading would look like a miss. The oracle now tests
every IV-free last-block reading: `64B-tworawkeys` (`0x10*16`), `65B-hexkey+LF`
(`0x0a‖0x0f*15`), `65B-content+pad15`, and any shorter valid PKCS#7 pad (logged, weak).

**campaign_29_halves — K from the two public halves, plus a named-object sweep.** Public
bytes only (no VIC word strings): `hash160(1GSMG1…) = a9553269…`, `hash160(17ucy1…) =
4bc46844…`. 42 one-rule keys — `sha256` of the two hash160s / version+hash160 / 25-byte
payloads / address strings, both orders and space-joined, `sha256(A)⊕sha256(B)`, double-sha,
raw concatenations trimmed to 32, hex-string forms — plus EVP-{MD5,SHA256} of the address
strings with the P32T salt. Then 12 named 32-byte objects as `sha256(object)`.
**50 candidate keys, 0 strong-reading hits, and 0 that produce even a chance valid pad** in
the last block (random keys give one ~1 in 255, so 0/50 is noise, no signal). Per-candidate
P5 logged in `neo/attempts/campaign_29_halves.jsonl`.

**Conclusion (the honest revelation, a sharp negative that redirects).** Under a clean,
reading-aware, IV-free 128-bit oracle, P32T's key is **not** any public-byte formula on the
two halves, nor `sha256` of any named object, nor (per the user's own runs) any VIC-string
KDF. Combined with tick-20's proof that `Salted__` is written only in password mode and the
tick-29 Base58 closure, **P32T is not opened directly from any currently-named object.** The
arrow reverses: an earlier step (Cosmic, or the still-missing slot-A operation) must name
P32T's operand first. The missing piece is the operation, and it is now shown not to be a
public-address derivation either. No AES campaign on P32T or Cosmic is warranted until a
primary statement names an operand that is not a VIC string — which the archive does not
currently supply. The freeze oracle stays as reusable tooling for any future K.

**Salt-structure probe (same tick).** The salt is the one field the creator chooses freely
at encryption time, so it is a natural place to plant a pointer. Examined all six real salts
(the three unsolved locks + the three solved stages) for ASCII, byte-reversal, pairwise XOR,
digit/base structure, and repeats: **nothing.** No salt is printable, no reversal or XOR
yields text, byte distributions are chance (the one repeated byte in the salph_inner salt is
within the ~11% birthday chance for 8 bytes). The salts are ordinary random OpenSSL salts;
they carry no operand. (Re-confirmed the TG-doctored salt differs from cosmic only in bytes
0–1, tail `6fe06dc950e6` shared — a splice, as tick 3 found.) So "the salt names the next
step" is closed.

### Loop tick 31 (2026-09-26) — forensic/provenance round: five channels audited, all dry

Per the standing plan (no more AES batteries; find the named operation or a new artifact):

**1. P32T reading made canonical.** The repo asserts the **hex-key+newline** reading (README:
the 80-byte CT "fits a 64-character hex private key plus a newline") = 65 B content, pad 15,
so PRIMARY `P5 == 0x0a‖0x0f*15`; the two-raw-keys reading (64 B, `0x10*16`) is SECONDARY.
`p32t_freeze.accept(K)` now checks primary, then secondary, then any valid pad. No future key
will be rejected for the wrong length assumption.

**2. `4943` audit — coincidence, closed.** `f73d92 = 2·11·149·4943`; `4943` was the only
unexplained residue. It is prime; it appears **literally nowhere** in any authenticated text;
**no puzzle object is even 4943 bytes long** (page 2150, soup 2149, architect 501, cosmic
1344, phase-3.2 2422), so offset/line/index-4943 readings do not apply; modular coords
(mod 196 = 43, mod 91 = 29, mod 58 = 13, mod 24 = 23, mod 14 = 1) name nothing. A 24-bit
colour field's prime factorisation carries no puzzle meaning. Closed as coincidence; not hashed.

**3. Named-operation audit — no statement names an endgame operand.** Every HINT/CONFIRM with
an operation verb (hash #225/#226, the giveit fix #867, HASHTHETEXT/Decentraland, zeroing
#8000, binary reversal #8446, split half/better-half, index {1,4,21}/primes) attaches to a
solved or upstream stage. **No authenticated statement names P32T, salph_inner, inner96, the
envelope, or the Cosmic blob as the object of an operation**, nor any operation that produces
32-byte material from an already-named object. The Cosmic HINT/CONFIRMs (#8311/#8315/#8328)
point at the Time-Life "Cosmic Duality" book cover being "scary specific", not at an operation
on the blob. The live gap (an earlier step must name P32T's operand) is unfilled by the archive.

**4. Git forensics for S0 — not recoverable.** One branch, no stashes/tags; deleted files in
all history are only the untracked `__pycache__` bytecode and two old `phase2.png`/`phase3.png`.
A full blob scan of every object in history finds seed material only in the already-known
parked `neo/prior-sessions/2026-09-25-S1S4/` files; no hidden or deleted S0. S0 remains the
uninvertible SHA256 preimage of head S1 — confirmed unrecoverable, as the parked ledger stated.

**5. Matrix oddities — unnamed, kept as markers.** No primary sentence names the near-white
`#FEFEFE` cell (7,4) or the 4-bit spiral residue `0000`. "White" occurs only in the poem's
"Roses are White" line; the creator explicitly claims **no hidden picture** in the rabbit
(#23200 "Squares and a rabbit?… no hidden picture"); the one gaze theory (#2905 "rabbit
looking to this point") got a non-committal "Interesting 😜". Both oddities stay markers.
(Observation, not promoted: the rabbit is drawn in cells cols 6–9/rows 6–8 and `#FEFEFE` sits
at (7,4), to its left; a left-facing rabbit would "look toward" it. Post-hoc geometry, and the
creator was non-committal — recorded, not elevated.)

**6. Salt exclusion** recorded in tick 30 addendum: six real salts, no ASCII/reversal/XOR/
structure, no pointer. Reusable closure of the salt channel.

**7. Stop.** All six forensic channels are dry and no new operand appeared. Per the plan, no
further AES campaign is run: the measured false-positive regime would manufacture noise, not
answers. The impasse breaks only with a new authenticated artifact naming the operation, or
the lost S0 seed — neither available. The freeze oracle and the address oracle remain as
tooling for any future candidate key.

### Loop tick 32 (2026-09-26) — the f73d92 factorization "revelation": verified, built, null-tested, closed

Claim: `f73d92 = 2·11·149·4943` is not coincidence but the encoded instruction —
`11` = side of an 11×11 matrix, `121 = 11² = π(661)` prime positions of `DBBI‖FAED`
(`661 = 91+570`), `149` = VIC numeric-ciphertext length, `4943 = prime(661)`. Pipeline:
121 prime-position chars → 11×11 → row/col sums (matrixsumlist) → sums as indices into a
held text (lastwordsbeforearchichoice) → the extracted letters/words are the password.

**Every arithmetic claim is exactly true** (verified): `f73d92 = 16203154 = 2·11·149·4943`;
121 = 11²; the 121st prime is 661; the 661st prime is 4943; π(661) = 121; 661 = 91+570; and
the VIC numeric ciphertext **is** 149 digits. This is a genuinely tight-looking chain, tighter
than most, because it makes two independently checkable matches (149 = VIC length; 4943 =
prime(len DBBI+FAED)).

**But the operation it names is empty.** campaign_30 built the pipeline faithfully and
exhaustively over its natural parameter space:
- 121 prime-position chars of `DBBI‖FAED`, `a=1…i=9` (and `a=0…i=8`), 11×11 row-major and
  column-major, sums = row / col / row‖col / col‖row.
- **Letter-level** indexing (160 candidates) into held texts {Architect rewrite, VIC
  plaintext, URL, `DBBI‖FAED`, VIC ciphertext}, 1- and 0-based, reject/mod out-of-range.
- **Word-level** indexing (32 candidates) into the 332-word Architect speech, the VIC
  sentence, the checkerboard sentence, both digit maps.
Terminal gate: the 128-bit freeze oracle (both salts) + full-harness accept + address oracle.
**Result: 0 freeze hits, 0 harness hits, 0 address matches, and no readable output.** The
letter extracts are gibberish; the word extracts are salad ("otherwise it not has precision
not not and unexpected thus it…", with repeated "it it it" from duplicate sums).

**Null test on the factorization chain — it is a 1-in-11 coincidence.** Over 40,000 random
even 24-bit integers, against the puzzle's own quantity set
`{7,9,11,13,14,15,16,23,24,91,121,140,149,196,570,661}`:

| property | rate |
|---|---|
| a prime factor is a puzzle quantity | 0.31 |
| a prime factor's prime-index is a puzzle quantity | 0.23 |
| **both (the exact f73d92 chain)** | **0.094 (~1 in 11)** |

Small primes are common factors and the quantity set holds several small numbers, so a chain
this "tight" is an ordinary event — the same category as the π-digit chain closed at tick 21
(a 10% coincidence). The `149`-as-VIC-length and `4943 = prime(661)` matches are exactly what
a 1-in-11 process produces.

**Verdict.** The factorization is arithmetically real and unusually pretty, but it carries
~3.4 bits of evidence (chance level for this search) and the operation it supposedly encodes
produces nothing under a 2⁻¹²⁸ gate. Recorded as coincidence, not promoted to "the operation"
— consistent with the ledger's standing rule that a reproducible number is not a compelled one.
The matrixsumlist pipeline in its most-motivated instantiation (11×11 from `DBBI‖FAED` prime
positions) is closed; broader matrixsumlist readings on the 14×14 grid were already closed
(campaigns 12–19). The live gap is unchanged: an authenticated statement naming the operation,
or the lost S0 seed. Neither is in hand.

### Loop tick 33 (2026-09-26) — provenance page: name the operand for each slot (no AES)

Per the standing plan (no campaign until two slots hold source-forced values). Wrote
`unverified/endgame_provenance_page.md`: for each slot, the one primary sentence that names its
operand, or blank.

- **A** operand named (the 24 yellow/blue colour cells → `f73d92`, #1710 + #8446); **operation
  not named** — "primes" is SAL-scoped to `matrixsumlist`, and no sentence aims prime/zero/DEL
  at the colour value. A stays the number `f73d92`, not expanded (tick 32 closed the factorize
  route).
- **B** operand **not uniquely named** — #8446 gives the token, but no sentence says which
  matrix (14×14 grid vs 7×13 `DBBI` blocks) or which cells.
- **C** operand named (the Architect speech) and **boundary pinned from the bytes**: the phase-3.2
  plaintext contains no `door`/`choice`/`choose`/`left`; it ends
  `…goodluckneverthelessireallyhopeyouretheoneciaobellao`, so the choice boundary is the end of
  the text. C's whole byte-derived set (≤3): `ciaobellao`, `ireallyhopeyouretheone`,
  `goodluckneverthelessireallyhopeyouretheoneciaobellao`. The quintessential-delusion line
  (#3390) is **dropped** — not before this cut, and disclaimed by #3391.
- **D** is an output/checkpoint (#9599/#39224/#39237), not an operand.

**Retrieval inventory** (step 4): `HASHTHETEXT` is present (`decentraland.ipynb`);
`/followthewhiterabbit` was examined (tick 11, = the phase-1 verification page, no puzzle
content); S0 / the original S1–S4 script is absent from the archive **and** all git history
(tick 31) and is the uninvertible SHA256 preimage of head S1 — a genuine hole but not
retrievable, only re-derivable from the lost script. No retrievable hole remains.

**State.** Two slots still lack source-forced concrete values: C reaches a 3-string candidate
set, but A has no named operation, B's matrix is unnamed, D is an output. `combine` stays
illegal; no AES campaign. The next real move is a **named operand or operator** from a new
authenticated statement.

### Loop tick 34 (2026-09-26) — slot B pinned to the DBBI/FAED structure by soup position

**The soup position forces the matrix.** `matrixsumlist` is decoded from the a/b field at
offset 91:195, sandwiched between DBBI (0:91) and FAED (195:765). The creator names the method
next to its operands at every stage, so B's matrix is the **DBBI/FAED structure**, not the
genesis 14×14 grid. The provenance page's "which matrix?" ambiguity is resolved. Genesis row/col
sums (`610876654997879` / `8108108736759668`) are **deprecated** for slot B.

**Three source-forced B integer lists computed** (`campaign_31_matrixB.py`), from
`DBBI ‖ FAED[0:546] = 637 = 7×91` = seven 7×13 layers, digits a=1…i=9:
- **B-ew91** = element-wise sum of the 7 layers → 91 values, range 23–52 (the only index-sized list).
- **B-row7** = row sums of the element-wise 7×13 grid = `455 485 483 518 468 504 460`.
- **B-col13** = col sums = `268 241 285 276 254 266 241 245 277 266 255 245 254`.
`matrixsumlist` emits an integer list (indices for slot C), not a string to hash — so these are
frozen as lists, not fed to AES.

**The B→C extraction is empty (NEGATIVE).** Using B-ew91 as 1-based word indices into the
332-word Architect speech (the text slot C names) gives word-salad ("mathematical eventuality
been otherwise is a ananomaly been harmony what i have unable to…"); per-layer DBBI row-sums
("it of has thus a a beyond") and col-sums ("my what harmony from of been the unable to…")
likewise. No readable English emerged, so nothing advanced to the freeze/address oracle. (This
is the corrected matrix — the earlier campaign_30 used the 11×11 prime-position matrix, now
closed at tick 32; per-matrix 7×13 sum lists as passwords were closed at campaign 12.)

**FAED 24-tail vs colour frame (slot A↔B link, step 3).** `FAED[546:570] =
ibibbibdcbahaidhfahiihic` (24 chars) against the colour sequence `BBBBYBBBYYBBBBYBBYYBYYBY`:
blue-select → `ibibibdahaihfii` (15), yellow-select → `bcbdahihc` (9). Structurally the 24=24
alignment holds (as at ticks 13/17/19), but neither selection nor its digit list is readable or
recognisable. No source-grounded A→B link found.

**Slot C word-counts (step 4).** The C strings' word counts (1, 5, 7) as indices into the VIC
sentence / checkerboard sentence / URL give fragments ("in to this", "case crack the",
"raising extra of"), nothing readable.

**State.** B's matrix is now pinned and its candidate lists frozen — a real provenance advance.
But the pipeline B feeds (matrixsumlist → index → lastwordsbeforearchichoice) is empty of
readable output, and slot A still has no named operation. Per step 5 the combine stays illegal
and no AES campaign runs. The next real move remains a named operator on a named object.

### Loop tick 35 (2026-09-26) — VIC certified; last-words and FAED material closed; the terminal state

**Phase-3.2 VIC digit cipher fully certified.** The straddle-checkerboard with rowheads {1,4}
and alphabet `FUBCDORA.LETHINGKYMVPS.JQZXW` (28 cells = 26 letters + two dots) takes the
149-digit string to the 91-char sentence exactly. Three sub-tests settled its status:
- **alphabet source-forced** by the Phase-3.2 riddle itself (the page gives it), not fitted to a
  keyword — removes the "reverse-engineered to fit" objection;
- **{1,4} rowheads are named in the decoded plaintext** ("one for one, four for one") — the stage
  checks itself, but this does **not** inherit from `matrixsumlist`; the {1,4}↔layer-prime
  correspondence is an overlay under the a=0 map, not a consequence of VIC;
- **family check**: the AES envelopes carry no digit stream, so the board has nowhere to apply —
  VIC is local. `{1,4}` is not a reusable key on the 80-byte locks.

**The 31/73→42 and matrixsumlist→{1,4} results stay map-dependent.** They require a=0…i=8; the
house map o=0,a=1…i=9 gives 40/88 (composite) and layer primes at {5,7}. Null (tick verified):
both colour-sums prime ~1 in 18; layer primes exactly at {1,4} ~1 in 90; ~1 in 1600 together —
stronger than the f73d92 factorization (1 in 11) but not proof, and un-inherited from VIC. Held
at "strong structural reading," not promoted to key material.

**campaign_32 — the 48/96 last-word construction, closed.** Final 11/21 Architect words = exactly
48/96 chars (L96 splits 48/48, 2nd half == L48). Tested outside-the-box against miniA (ct 32),
salph (ct 80), P32T (ct 80): 61 explicit 32-byte privkey candidates (XOR/one-time-pad of the
strings against the cts and full blobs, sha/window key derivations, half-subtraction) → address
oracle; derived AES keys → decrypt + PKCS#7 + P32T freeze + 64-hex-in-plaintext → address;
password form (raw + sha256hex, EVP-MD5/SHA256). **0 address hits, 0 lock opens, 0 structure.**
Note: the 48/96 byte sizes include OpenSSL's 16-byte header, so miniA's message is ≤31 bytes —
the length match is partly to container overhead.

**campaign_33 — FAED-derived material, closed.** Layer sums `[331,360,369,421,418,441,396]`
(decimal concat, spaced, BE/LE 4-byte concat), the 24-char FAED tail and its reverse, the 24-cell
colour frame (raw/reversed/BY-swapped), `31/73/42` with five joiners, each alone and prefixed
with `yellowblueprimes`; raw / sha256hex / raw-key forms × EVP-MD5/SHA256 × miniA/salph/P32T.
28 strings, 62 password-forms, **0 hits.**

**Architecture, after the nulls.** Flat (decrypt = 32-byte key): every tested candidate null.
Two-stage (decrypt = seed → BIP32 child at a path → key): **untouched**, because the seed would
live inside an unopened lock — not testable without first opening a lock. The creator's plural
"the private keys belong to half and better half" fits two locks → two seeds → two keys → one
combining rule, but that is one decryption away from being testable.

**Terminal state (the honest frontier).** The password for the two real 80-byte locks is the only
thing between the current state and a forward step; every other channel — outer seeds, VIC reuse,
last-words, FAED material, colour factorization, salts, git history — is at the noise floor. The
missing input is not in the creator-authenticated corpus. This matches #66573/#66574 (2026-07-13,
"my close friends have the best chance … NOTE: that is a hint"): the last step is designed not to
be derivable from published material. That is a real terminal state, not a failure. The freeze and
address oracles remain as tooling for any password a fact-from-outside might supply.

### Regime change (2026-09-26) — corpus parked; one frozen gate for new primaries only

The lock-battery regime is over. Campaigns through 33, the 240 BIP32 derivations, VIC reuse and
the FAED/last-words grids are all null, and more forms of the same objects only produce PKCS#7
noise at the rates already measured. No more campaigns are run against the published corpus.

**What is established, and what is not.** No password for mini, P32T or Cosmic can be derived
from the published corpus through any tested channel. Flat decrypt-equals-key finds nothing on
that set. Two-stage HD cannot be tested until a seed exists, and none of the seeds in hand is it.
`#66573` ("my close friends have the best chance … NOTE: that is a hint") does **not** prove the
last step lies outside the corpus. This corrects tick 35's "designed not to be derivable". The solved text already contains readings of that line: "half
and better half", the couple who "need funds to live", the Matrix intimates. Those were tried as
seeds and passwords. So "close friends" means either those spent objects, or a social fact that
cannot be rebuilt from the page. Hashing more variants cannot tell which. VIC stays local.
`{1,4}` is named by "one for one, four for one", not by `matrixsumlist`. `31/73→42` depends on
the map. None of these is key material. The 2021 "another door" / "2nd way wasn't founded" line
is read as the same instruction: a path that is not a remix of SalPhaseIon.

**The gate** (`harness/gate.py`, frozen):
candidate → {raw, sha256hex} → EVP-{MD5, SHA256} aes-256-cbc → {miniA, miniAB, P32T, Cosmic}
→ strict PKCS#7 + printable/magic gate. In parallel, sha256(candidate) (and the candidate
itself, if it is 64 hex) → uncompressed P2PKH compared with `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`.
Each intake gets 16 decrypts. No sliding windows, no substrings picked by the gate, no 2ⁿ
subset XOR.

Admissible input, one candidate per intake file, refused otherwise:
- `jrk_sentence`: a new Jrk/@SoWut message with id, date, author and the full verbatim text;
- `gsmg_page`: a new gsmg.io page with url, fetch time and the saved body (the 9-byte
  `Hello :-)` 404 is refused);
- `uttered_password`: a password a person in that circle actually said, with speaker, date and
  where it was said. Inferred passwords are refused.

Refused as spent before any decrypt: an exact string (raw or sha256hex) already in
`attempts/*.jsonl`; any string whose normalized a-z0-9 form occurs in LEDGER.md, `materials/`,
`materials/primary/`, `prior-sessions/`, `unverified/`, or among the literal candidates in
`harness/campaign_*.py` and `attempts/*.txt` (so campaigns 32/33, which wrote no JSONL, count); and anything already run through the gate
(`attempts/gate_intake.jsonl`). `gate.py --selftest` checks the three solved blobs, the address
known-answer vectors, the spent-refusal cases (half/better half, causality, the 3.2 password,
matrixsumlist), the provenance refusals, the 404 refusal, and confirms that the frozen decrypt
path reproduces phase 3.2.

**Standing state.** Slot A stays unfilled and slot C stays blank until one of the three primaries
arrives. Sandwich-B and `a=0` are not promoted to operators. If no primary appears, stop: the
tooling waits, and the only proof that counts is a spend from the prize address.

### Intake 1 (2026-09-26): uploaded Wayback, primary and drive material digested; nine web units gated, all null

**What arrived.** Three user archives:
- **Wayback:** 545 gsmg.io captures, 450 unique bodies after gzip/brotli/zstd decoding.
  Indexed in `materials/wayback/`.
- **Primary archive:** 65 files. Every one is already in the repo or byte-identical to a Wayback
  capture; the only extra is the raw binary of the 2023-02-23 hint, whose decoded form is here.
- **Drive export:** 9 files, filed under `unverified/drive-2026-05/`.

**What was new, and what it was worth.**
- **Tick 11 was wrong about the finale page, and right about its keys.** `root_2026-08-19` is a
  GSMG shutdown page: "2017 — 2026", "The lights are off.", "Nine years of chaos ended. One
  mystery remains.", with "Follow the white rabbit" linking to `/puzzle`. It types two Matrix
  terminal lines, then renders a hard-coded 14×14 grid under "SYSTEM FAILURE". That grid is
  **exactly the phase-1 grid**, with blue set to 1 and yellow to 0, and its spiral read is
  `gsmg.io/theseedisplanted`. So there is text, but no new operand.
- **The domain lapsed.** "The sites are down" drew "The puzzle is still valid!" (#63957,
  2026-05-28). From 2026-07-07 to at least 2026-08-10 gsmg.io was a parked domain listed for
  sale (abovedomains `forsale.min.js`, FingerprintJS `tr_uuid` redirects). The finale appeared
  on 2026-08-19. **Anything served on gsmg.io after 2026-07-07 has unverified authorship.** Any
  future `gsmg_page` intake from after that date carries the caveat.
- **A comment was added to the phase-2 page** between 2022-12-23 and 2026-04-05:
  `<!-- You made it to the next step! Good luck little bunny hunter ;) -->`. It is the only
  HTML comment on either live puzzle page. SalPhaseIon changed only in whitespace (2024-11)
  and a Cloudflare beacon (2025-10).
- **The SPA carries one puzzle string.** Across all 11 app.js versions, the `/puzzle` route shows
  `GSMG MEGANIGMA || 5 BTC` above the white-rabbit image. `/yummy` is the Cookies Policy. The
  legal PDFs are boilerplate for Epipremnum Aureum LLC (Saint Kitts–Nevis).
- **Every other path is the SPA shell**, including the guessed ones (`/merovingian`,
  `/final_stage`, hope-line spellings), 10 of the 12 hex paths, and a hex-encoded `Salted__`
  blob with a salt that appears in no known material. Shell diffs are infrastructure only.
  Of the other two hex paths, `/89727c…` is the SalPhaseIon page. `/4f7a1e4e…`, requested
  on 2026-07-08 while the domain was parked, is `sha256(cosmic_1327b_decrypted.bin)` from the
  drive export. Someone tried the sha256 → URL convention on a noise decryption
  while the domain was parked.
- **Drive export verdicts.** Four files are copies of known blobs. The two 1327-byte "Cosmic
  decryptions" are 1-byte-pad noise (entropy 7.8+, no structure). `ca158_hidden_blob` starts
  `Salted__`, but its 1153-byte body is not a multiple of 16, so it cannot be an openssl
  AES-CBC envelope; its source file is not in the export. `chain2`/`chain4` are pad-1
  decryptions of its first 1152 bytes.
- **The 2026-01-01 new-year hint is already in the transcript** (#53342): 'Happy new year! Make
  the best of everything. Oh, and here's a "tiny hint" <3.' The quoted "tiny hint" echoes #881,
  the 2019 promise of a "tiny hint" at the start of 2020. The five preceding messages of one to
  five dots are logged as NOISE. As Morse they read E, I, S, H, 5, the dots-only ladder. That
  is recorded as a reading, not promoted to an operand.

**The gate run.** `intake/2026-09-26-web/PREREG.md` was committed and pushed before anything
ran. It covers every solver-facing text unit of the three new sources, whole and verbatim,
nine intakes: the phase-2 comment, `GSMG MEGANIGMA || 5 BTC`, "The lights are off.", "Nine
years of chaos ended. One mystery remains.", "2017 — 2026", "WARNING: carrier anomaly",
"Trace program: running", "SYSTEM FAILURE", and the rain-glyph string. All nine were admitted.
**144 decrypts, 0 with valid PKCS#7 padding at all (about 0.6 expected by chance), 0 prize
address.** Each is logged in `attempts/gate_intake.jsonl` and is now spent.

**Stop rule applied.** The 2026 web material is closed: no variants, no concatenations, and the
timing constants (1441, 2442 ms …) are not promoted. Nothing in the three archives is a new Jrk
sentence or an uttered password. Standing state is unchanged: A unfilled, C blank, tooling
waiting.

### Loop tick 36 (2026-09-26): the checksum machine, cold-verified, classified and frozen

**Verified.** `harness/verify_checksum_machine.py` recomputes every claim from primary files
(soup, `phase3-assets/phase3.2.txt`, the phase-0 grid JSON). No AES, no gate. **26 of 26 checks
pass**, including each uniqueness scan.

The tape, as it now reads:

```text
soup[0:91]     DBBI (91, a–i)     layer 1 of 7: a=0 total 331 (prime, π=67)
soup[91:195]   bin1 (104, a/b)    48 a / 56 b; a=0,b=1 packed MSB-first = "matrixsumlist";
                                  bit[31]=0, bit[73]=1 (Yellow=0 / Blue=1 polarity), 31+73=104
soup[195:765]  FAED (570, a–i)    [0:546] = layers 2–7: 360 369 421 418 441 396 (421 prime, π=82)
                                  [546:570] = tail; phase-0 frame BBBBYBBBYYBBBBYBBYYBYYBY gives
                                  Yellow=31 / Blue=73 under a=0
DBBI‖FAED = 661 symbols; 4943 = p_661; 0xF73D92 = 2·11·149·4943
```

- **Colour window:** of 547 windows of 24 on FAED, only offset 546 gives 31/73 under a=0. The
  house map gives no 31/73 window anywhere; the tail reads 40/88 there.
- **Layer totals:** of the 25 alignments of a 637-block on the 661 tape, only offset 0 has
  primes at positions {1,4}, values {331, 421} and rank-sum 67+82 = 149.
- **VIC split:** the 149 VIC digits decode to the 91-letter sentence on the proven board
  (91 tokens). Letter 40 ends exactly at digit 67, so 67 | 82 decode separately to
  `INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYS` | `BELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE`.
  That is the sentence boundary.
- **The one 42:** token `42` occurs once in the tokenization (it is also the only raw `42`
  substring), at digit 47, and it is the `P` of PRIVATEKEYS. Board: 42→P, 15→I, 10→`.`, 43→S.
- **ENTER mask:** the 40 bits of `enter` over the first 40 letters (A=0…Z=25) sum to 191 where
  the bit is 1 (prime, π=43, board code `S`, the last letter of PRIVATEKEYS) and 233 where it
  is 0 (prime, π=51 = the 51 remaining letters). The gap is 42. Of 52 windows of 40, only
  offset 0 gives a prime pair with gap 42.
- **Lengths:** π(11)=5=|enter|, π(149)=35=|shabefourfirsthintisyourlastcommand|.

**Precision notes, from the check.**
1. **π was never uttered as a function.** In 510 creator-log rows, the prime-counting function
   π(n) and "rank" never appear. The only "pi" is #32671 (2024-11-29), "You only need the last
   number of pi…", which is banter about the constant and was closed as key/IV material at
   tick 22.
2. **Two conventions carry the machine.** 31/73 exists only under a=0, which is not the house
   map. The ENTER pair exists only with MSB-first bits: LSB-first gives 218/206, both even.
   MSB-first is at least the soup's own bin1 packing, so that one is internally consistent.
3. **Correction to the campaign-32 remark.** Its 64-hex regex ran on AES decrypts, never on an
   XOR output. It was dead only on miniA's 32-byte decrypt and live, with low power, on the
   80-byte locks and Cosmic. The code that really was dead is the XOR scan's
   WIF/`xprv`/`1GSMG` prefix loop, whose body is `pass`, so XOR outputs were checked only for
   `Salted__` and ≥90% printable. The script also reads `/tmp/arch_words.txt`, which is not in
   the repo, so campaign 32 cannot be reproduced as committed. Its null stands and is not
   re-run.

**What it is.** A closed arithmetic commentary on the already-decoded Phase-3.2 and SalPhaseIon
layout. Every output lands on a length or a cut already in hand: 149, PRIVATEKEYS, HALF AND
BETTER HALF, `enter`, 661, matrixsumlist.

**What it does not do.** It does not name a creator-written operation for slot A, does not fill
C from a new primary page, does not open mini, P32T or Cosmic, and does not produce a 32-byte
scalar for `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`.

**Frozen as not key material.**
- `4943`: reading it as p_661 is the best reading of that marker so far, but it is still the
  frozen Genesis object. It is not hashed, not used as an offset and not put in the gate.
- The length zoo, such as π(42)=13=|matrixsumlist|, π(31)=11=|thepassword| and
  π(15)=6=|YOUWON|, is look-elsewhere and stays off the key list.
- `42 15 10 → PI.` (73−31, 82−67, π(73)−π(31) on the board) is a wink, not a password.

**The continuation rule, frozen.** If the machine is continued at all, it takes the **next
source-named** binary mask × an equal-length named text, demands another prime-pair / π
checkpoint, **then stops. No AES.** Masks already spent: the Phase-0 24-colour frame and the
`enter` 40 bits. A next mask must be as named as those two (`shabefour…`, `hash_the_text`, a
creator bit-string), not one cut because it is the right length.

**Gate: empty.** Standing state unchanged: A unfilled, C blank. This tick improved the ledger's
description of the tape. It did not solve the puzzle.

**Tick 36 addendum: base rates for the "π(x) is the operator" reading.** The same facts were
re-presented as evidence that the prime-counting function is the missing operator.
`harness/checksum_machine_baserates.py` measures what each fact is worth.
- **Uniqueness is mostly automatic.** Of 547 FAED colour windows, 344 already have a (Y,B) pair
  that no other window shares; 31/73 was read off offset 546, so its uniqueness is expected.
  A prime pair 42 apart is **not** unique on FAED: offset 110 gives 29/71. Of the 25 tape
  alignments, 15 have a prime-position pattern that no other alignment shares, and {1,4} is
  simply the offset-0 pattern.
- **The 67 | 82 cut.** 22 of 148 digit cuts land on both a token boundary and a word
  boundary, so landing on one is a **15%** event. The notable part is π(331)+π(421) = 149,
  the VIC length, a chain of the kind tick 32 measured at about 1 in 11.
- **The length zoo is nearly free.** Newly checked: π(104)=27=|verylaststepisatruegiveaway|,
  π(10)=4=|HALF|, π(21)=8=|promised|, π(4943)=661. Against 24 named tokens, π(n) hits a named
  length for **78% of n ≤ 50** and 35% of n ≤ 150.
- **What survives: ENTER.** A random 40-bit mask over a random 40-letter window gives a prime
  pair exactly 42 apart about **1 in 1,400** times. That the natural mask on the natural
  prefix repeats the 42 is the one genuinely unlikely item. It still depends on MSB-first
  bits and A=0, and what it points at is the solved sentence (PRIVATEKEYS, the 51-letter
  remainder), not an operand.

**Verdict unchanged.** Grant π(x) as the creator's device and it is still a device for
checksumming lengths and cuts of decoded text. It emits no string, key or scalar that any lock
could take, and no source-named next mask exists to feed it. The frozen continuation rule
stands; the gate stays empty.

### Loop tick 37 (2026-09-26): "better half" is an address, confirmed; meet-in-the-middle ready, blocked on a public key

**A creator CONFIRM the ledger never used.** On 2020-05-11, the halving day, @x7x7x7x6 wrote
"the half of prize went to better half" and the creator replied **"Well spotted"** (#3902,
classed CONFIRM). Half the prize had just moved from `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` to
`17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa`. So **"better half" = the 17ucy1 address**, and "half" =
the prize address holding the other half. That makes the VIC sentence ("…THE PRIVATE KEYS
BELONG TO HALF AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE") **meta**: it says what the
cracked keys are for, two keys for two funded addresses. It is not a recipe for deriving a key.
- Consequence: it supports P32T holding **two raw 32-byte keys** (64 B content, pad 16). That
  was the SECONDARY reading in tick 31; it now has creator-anchored motivation. This is not
  proof, and it does not change the freeze oracle, which already accepts both readings.
- Consequence: "half and better half" is **not** evidence that one key is the sum of two
  parts. The additive meet-in-the-middle below is therefore a cheap structural check, not a
  lead.

**Meet-in-the-middle harness** (`harness/mitm_halves.py`). It tests k = a+b, a−b and a·b (mod n)
for every pair (a, b) from a 163,354-scalar pool: sha256 of every logged candidate and 1–4-word
n-gram of the primary texts and creator messages, plus 64-hex strings read as scalars. That is
about 8×10¹⁰ pairs, done as ~5×10⁵ EC operations in **18 s**. Self-test: planted add/sub/mul
pairs are recovered, and a random point at full scale gives 0 false matches.

**Blocked.** It needs the prize (or 17ucy1) public key. The prize key is on-chain in the
scriptSig of the 2020-05-11 spend, but this environment's network policy denies every chain
API tried (blockstream, mempool.space, blockcypher, blockchain.info). The harness refuses any
key that does not hash to one of the two addresses.

**Tick 37 result (2026-09-26).** The user supplied the two 2020 halving transactions, saved in
`materials/chain/`. The halving spend (locktime 629998) reveals the prize public key: it is
uncompressed, `04f4d1bb…3559`, and hashes to `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`. The spend
sent 2.5 BTC to `17ucy1…` and returned 2.49815966 BTC in change. A second transaction sent
700 sat plus OP_RETURN `Halving` to the prize from a different vanity address,
`3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK` (P2SH-P2WPKH, key `0205eaf7…`). **Meet-in-the-middle run
against the prize key: 163,354-scalar pool, 8.0×10¹⁰ add/sub/mul pairs, 17 s, no match.**
The two-part-sum reading is closed. This line ends here: no further elliptic-curve searching
against the prize key.

**Chain flows (2026-09-26).** `harness/chain_flows.py` walks the transaction graph through any
Bitcoin node RPC, reading the URL from `BTC_RPC_URL`, never from disk. It goes backward through
funding inputs, checks the spent/unspent status of tracked outputs, and optionally scans chosen
block ranges forward (halving windows). It writes `materials/chain/FLOWS.md` and `flows.json`.
The Alchemy endpoint is blocked by this environment's network policy, so only the offline pass
has run. That pass already shows **the 700-sat "Halving" output (`a798905f…f383:1`) is the third
input of the 2.5 BTC halving spend (`2aa9a4a9…1b13`)**. The creator sent dust plus OP_RETURN
`Halving` from `3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK` into the prize address, then spent it
alongside the prize coins, so one party controls both the prize key and the `3GSMG24` wallet.

### Loop tick 38 (2026-09-26): on-chain record, creator trail vs community traffic

Source: the user's `esplora_flows.py` run (blockstream.info, 216 calls, 209 txs), pasted back
into the session. Balances at that snapshot: prize `1GSMG1JC9…` 1.25636967 BTC; `17ucy1…`
3.75055856 BTC, never spent; `1GSMG1CLx…` 0.01347934 BTC, never spent.

**Creator trail (canon).** Each item is linked by spends to the prize key or its 2019 funder.
- 2018-01-11: `1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1` pays 1,337,000 sat to the vanity
  `1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3`.
- 2019-04-13 (block 571497, locktime 571496): the same `1EtbTv…` pays exactly 5.0 BTC to the prize.
- 2020-03-24 to 04-07: `3GSMG24T…` sends 1000-sat outputs with OP_RETURNs:
  "GSMG.io: Right, this is causality", "…do you beleive me you need it?", "…part of the cipher",
  "…phase3.2 pass OK", "…are you sure?", "…You are here because 227 chars were correct",
  "Good job, Neo!" ×2. A bare 1050-sat output goes to `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9`.
- 2020-05-11 (block 630001): OP_RETURN `Halving` + 700 sat from `3GSMG24T…`. The prize key then
  spends that 700 sat together with the 5 BTC, sending 2.5 BTC to `17ucy1…` with change back.
- 2021-07-18: OP_RETURN "GSMG.io neighbors, half and double" + 5000 sat to four addresses. The
  user reports them as the P2PKHs of 2P, P/2, P±G on the prize point. Not re-derived here.
- 2024-04-24 (locktime 840003): the prize key sends 1.25 BTC to `17ucy1…`, change back.

**Everything else is unauthenticated.** None of its inputs trace to `3GSMG24T…` or `1EtbTv…`.
From 2023 on, the prize and `17ucy1…` are a public chalkboard: copied dust sizes, puzzle
slogans, claimed "Neo wallets", the `1GSMG9…` "GSMG WITNESS" blobs, and the Feb/Apr 2026 token
spray from `1JG648…`/`145ZQ9…`. The user attributes those two addresses to an old Cosmic
decrypt; not verified here. An unidentified bc1q sender wrote "Happy New Year!" (bits and
string reversed) and "illusions" (7-bit reversal); unattributed. If any of those keys were the
prize key, the coins would have moved. They have not.

**Boundary.** This session runs no further key searches, of any kind, against the prize or any
other real address. The one meet-in-the-middle run (tick 37) is the last. The gate's rule
stands: only new primary material. A preimage for `1NULY7…` counts only if it is published or
named by the creator's circle, not if it is searched for.

### Loop tick 39 (2026-09-26): the 2020 OP_RETURNs are a solved-stage ladder; "Good job, Neo!" marks an unpublished stage

**Verified:** the phase-2.2 password (the `causalitySafenetLunaHSM…b - - 0 1` concatenation) is
exactly **227 characters**. So "GSMG.io: You are here because 227 chars were correct" is the creator
confirming a phase-2.2 solve on-chain. Read with the others, the 2020-03-24 messages confirm
solved stages: "Right, this is causality" (phase 2), "227 chars" (phase 2.2), "phase3.2 pass OK"
(phase 3.2).

**The rung past 3.2:** "Good job, Neo!" went to two addresses on 2020-04-03, and a bare 1050 sat
went to `1NULY7…` on 2020-04-07. On 2020-04-08 the creator wrote (#3338): "one team managed to
find something... something others haven't yet found (unless they didn't tell us)." The two
"Good job, Neo!" recipients wrote "From Neo" and "Neo wallet bc1qyw9…" on-chain in May 2025.
The congratulated team therefore exists and still identifies itself as "Neo".

**Consequence:** the best remaining input is a human one, the gate's `uttered_password`
channel. It means asking that team, through public channels (the GSMG Telegram, or an
on-chain reply to the address they published), what "Good job, Neo!" confirmed. No wallet
tracing, no attribution of people, no key search.

### Loop tick 40 (2026-09-26): nulls reported from a parallel session (USER grade, not re-run here)

A pasted transcript of another assistant session reports these nulls. They are recorded so
nobody repeats them:
- **VIC internals as a raw AES key for P32T.** K = SHA256(s) for the board string, "14",
  the 149 digits, the 91-letter plaintext, HALF, BETTERHALF, the DBBI⊖VIC header, YOUWON,
  VIC, HALFANDBETTERHALF, "1", "4". The last-block P5 test fails on every one; none even has a
  valid pad byte.
- **HASHTHETEXT** as "your last command" into miniA: sha256hex + EVP-SHA256 and EVP-MD5, bad
  padding.
- **Address-derived keys for P32T:** SHA256 of the prize and 17ucy1 addresses, of their
  hash160s and of the XOR of those; h160‖h160 truncated to 32 bytes; EVP of the address
  strings. The P5 test fails on all.
- **SHA256(HALF) ⊕ SHA256(BETTERHALF)** and the 64-letter DBBI tail as two raw keys: no P5
  pad, and not the prize address.
- **f73d92 factor forms** (4943; 2111494943 with and without separators), alone and as
  A‖B‖C with the frozen B/C rows: 1,020 decrypts, four pad-01 events of garbage, and no P5
  `0x10`×16 hit.
- Also noted: the complement 08C26D = 574061 is prime. Recorded as a curiosity only.

Nothing in the transcript is a new primary. The live lead remains tick 39: what the
"Good job, Neo!" team found in April 2020.

### Loop tick 41 (2026-09-26): the 24-prime colour list, verified; two sourced index tests, null

**Verified here:**
- The LSBs of `gsmg.io/theseedisplanted` are `111101110011110110010010`, exactly the colour
  string (Y=0, B=1). This is the same 24 bits as the Telegram triplet
  `11110111 00111101 10010010`, so it is not a new field.
- Pairing the colour string with the first 24 primes gives **Yellow = 479, Blue = 484**.
- In the Architect rewrite (the "yourlife…" string in `phase3.2.ipynb`, 1545 letters there,
  1539 under the user's cut, same prefix), **`PRIVATEKEY` starts at letter 479** (0-based). It
  occurs again at 1238. Calibration: 23% of offsets are word starts, and the target was
  chosen after the landing. That makes this a modest pointer (a few percent before
  selection), and it lands on solved text.

**User-run, sourced tests, both null:**
1. Self-indexing the 7×13 house-map grid (row+col, 0- and 1-based, digital root) gives more
   a–i soup: no English, no YOUWON.
2. The 20 DBBI sums used as indices into the 24 primes, mod 26, give `tjvpdbv…` and
   `rhtlcvr…`. Not English. The sum totals (751/763) are not 479/484.

**Deliberately not run (unsourced):** the decimal concatenation `55656860…` as a password,
XOR/permutation of FAED by those numbers, and a 4-state "@/A" reading. The numeric frame
stays a pointer (479/484 → PRIVATEKEY). The gate stays empty.

### Loop tick 42 (2026-09-26): three user-specified sourced tests, all closed

**Control.** The soup's own field-decode (house map o=0, a=1…i=9 → concatenate → decimal int
→ hex → ASCII, whole z-delimited segment) reproduces `lastwordsbeforearchichoice` and
`thispassword`. The tests below use exactly this rule.

1. **DBBI as a 7×13 house-value table.** Row sums `55 65 68 60 49 63 62`, column sums
   `28 38 42 37 24 33 15 34 35 39 26 33 38` (the user's 20 sums). Field-decode of rows and
   columns, concatenated and mod 10, and of the 91 cells themselves: 36–67% printable, no
   English, no 64-hex. a/b binary on the grid (value parity, both polarities, row- and
   column-major, MSB-first like bin1): 27–45% printable. **Closed.**
2. **Zeroing on the blue primes {2,3,5,7}.** This zeroes 61 of 91 cells. The same decodes
   give 0–67% printable garbage. **Closed** (one pass, as specified).
3. **P32T board from the phase-3.2 clue plus the phase-2 FEN.** The clue ("fubcd-king &
   oracle-queen, thingky mvps, on a sad board but as wide as the first one seen") already
   built the VIC alphabet. An FEN overlay needs an 8-wide board: `FUBCDORA / .LETHING /
   KYMVPS.J / QZXW`. Letters under the FEN pieces are `FRALGMX` (white `FRAGM`, black `LX`);
   no token. **Stop rule applied: no AES pass.**

The gate stays empty. The missing object is still the two short words behind
yellowblueprimes and yinyang, which need a named rule to print them.

**Tick 42 correction (board string).** The overlay is row-major with rank 8 on the top row,
but the letters depend on one layout choice. **Keeping the board's two `.` cells** (the 28-cell
VIC alphabet, rows `FUBCDORA/.LETHING/KYMVPS.J/QZXW`) gives `FRALGMX`. **Dropping them**
(26 letters, rows `FUBCDORA/LETHINGK/YMVPSJQZ/XW`) gives `FRAEKV`; the user replayed this
independently. Neither is a soup token or a named password. The closure stands (no AES) under
both.

**What is still independently named on two sides:** yellow 479 / blue 484 (colour frame ×
first 24 primes); DBBI 91 / FAED 570; P32T 80 B / SalPhaseIon 80 B; HALF / BETTER HALF (VIC
sentence). None of these pairs has a named operation that turns both sides into words. The
table in tick 42 supplies no string, so the gate stays empty.

### Loop tick 43 (2026-09-26): "XOR triangle" citation rejected as unverified

An LLM output (a "personal_context tool" screenshot) cited a "March 2026 issue" saying "The only
way out will be an XOR triangle". It attached `f7 | 3d | 92`, a 4-byte trailer `fc0c1b02` and
"two 32-byte halves plus a 4-byte trailer". **Not found anywhere:** not in the creator log
(March 2026 is #60285–60327, all 2026-03-04, with no such line), the hint images, the site
pages, the 545 Wayback captures, the chain data or the ledger. The only "triangle" strings in
gsmg.io code are a chart library's `triangle-down` marker and an emoji keyword. **Internally
inconsistent:** 32+32+4 = 68 bytes is not a valid AES-CBC plaintext length for P32T (80 B
ciphertext = 64 B content + a 16-byte pad block). Treated as a hallucinated citation. The
stop rule is unchanged, nothing was run, and XOR constructions on f7/3d/92 or the sums stay
excluded.

### Loop tick 44 (2026-09-26): the "prime basics" sentence read as an ordered recipe (recorded, not run)

Source (the phase-3.2 Architect rewrite, verbatim): "...the function of the you is now to
return to the source codes allowing a temporary dissemination of the code you hopefully carry
reinserting the prime basics after which you will be required to select from over twentythree
ciphers sixteen encryptions and or seven intertwined passwords...".

**Already closed:** `reinsertingtheprimebasics` as a password (single_t_mutation,
endgame_aes_password_search); reinserting 2,3,5,7 at prime positions into the row sums (tick
4/5); blue-prime zeroing, the inverse operation (tick 42).

**The untried reading is the ordering.** The sentence gives a sequence: (1) return to the source
codes → (2) reinsert the prime basics → (3) only then select among 23 ciphers / 16 encryptions /
7 intertwined passwords. Taken literally, prime reinsertion is a **preprocessing step that
precedes** any cipher choice, and "seven intertwined passwords" is the output stage (seven,
like the seven 7×13 matrices). This fixes the order of operations but still names **neither
the object** the primes go back into nor the exact reinsertion rule. It remains the same
unnamed-operation gap, so no test was run and the gate stays empty. If a source names the
object ("the source codes" = which blob or tape?), this becomes a single admissible test:
reinsert, then the P32T `0x10`×16 check.

Also recorded: two ChatGPT screenshots (2026-09-26). Both used personal_context or read this
repo. Neither shows a source for the "XOR triangle" line (tick 43 stands).

**Tick 44 run (user-requested, one pass).** This is a literal instance within the soup's own
machinery, the inverse of tick 42's zeroing. Tapes: DBBI, FAED and DBBI‖FAED as house-map
digits (a=1…i=9). Reinsert the prime basics 2,3,5,7 (cycling) at every prime position, 0- and
1-based, in two modes: insert before, or overwrite. Then apply the soup's field-decode
(digits → int → hex → ASCII). 12 variants (24, 104 and 120/121 reinsertions): **31–44%
printable, no alphabetic run of 5 or more, no 64-hex shape. Null.** No AES. The ordering reading
is closed for these tapes; the object "the source codes" remains unnamed.

### Loop tick 45 (2026-09-26): the phase-2 FEN verified as a finished gadget; tick 42's board was an invented overlay

**Verified with python-chess 1.10.** In the riddle position
`B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1` (legal), White has **14 legal
moves; 13 are mate; the only non-mate is Rc6+**. After it, Black's **only legal reply is
Rxh7**. The board after Rc6+ is exactly the password FEN
`B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1`. The engine writes the move
counters as `1 1`; the password keeps the author's `0 1`. That answers "the buddhist is forced
to move / what will be the next situation": play the one non-mating move, the rook check. The
string is already inside the phase-2.2/3 key and did its job there.

**Correction to tick 42.** "On a sad board but as wide as the first one seen" belongs to the
phase-3.2 checkerboard line (the 14-wide genesis grid, tick 1b). The 8-wide chessboard is a
different board. Laying the VIC alphabet under the FEN pieces (`FRALGMX` / `FRAEKV`) combined
the two, which makes it an invented operator. Its null stands, but it should not have been run
as sourced. The FEN is closed: no knight tours, no reuse of the FEN as a password, no overlays.

### Loop tick 46 (2026-09-26): the three remaining named pairs, disposed

1. **The 20 sums as the next soup field** (house alphabet): no page marker forces it. The soup
   grammar (tick 10) has no field for sums. **Left, not run.**
2. **479/484, zeroing the blue prime 5, then stop:** yellow 479, blue 484 − 5 = **479. The
   halves become equal.** This is near-tautological: the gap is 5 and 5 is blue, so removing it
   balances by construction. The only coincidence is that the gap is a prime present on the
   blue side. It yields no word and no operand. **Stopped as specified.**
3. **P32T / SalPhaseIon short as two 80-byte halves:** a solve must open both ("HALF and BETTER
   HALF"), and no candidate with an independent name exists. **Nothing to run.**

**Closed this week, not to be reissued:** r133, giveit/t, faed⊖VIC, the 2026 pages, the
501-span, homemade -K/-iv, π 9:11, Telegram LSB = URL LSB, Architect-as-index from the DBBI
sums, the 7×13 self-index, 20 sums → 24 primes, the 331/421/4943 π-chain, FEN overlays, FEN
reuse, invented grid operations, the XOR-triangle citation, prime-basics reinsertion.

**Standing state:** until a page names the next rewrite of the 20 sums or the two missing
ingredient values (yellowblueprimes, yinyang), there is no AES pass to run.

### Standing state (2026-09-26, filed): the sourced queue is empty; wait

No AES. No new operator on DBBI, the 20 sums, the 24 primes, the FEN or the Architect stream.
`yellowblueprimes` and `yinyang` remain labels without values. Both 80-byte locks (P32T and
SalPhaseIon short) need the same independently named X.

**Primary material still open. None of it is a typeable operand:**
- #66573 (2026-07-13): "My close friends have the best chance of solving it… NOTE: that is a
  hint." A person-context hint, not a string. No name lists are to be built from it.
- #53342 (2026-01-01, exact bytes in the archive and README): "Happy new year! Make the best of
  everything. Oh, and here's a "tiny hint" <3." Read as text. Nothing is derived from its date
  or bits.
- The two missing soup words, which count only when another authenticated field names how
  they are computed.

**Not to be done:** inventing the rewrite tick 46 left; reopening 479 = 479 as a password
(`yellow479`, `479479`, `zero5`); a close-friends name list.

**Answer to any request for work:** there is no next tick until a page names the next rewrite
(of the 20 sums, or of the two ingredient values). New primaries enter only through `gate.py`.

### Addendum (2026-09-26, user-directed): third-door short list, and two provenance caveats

Corroborates the standing "sourced queue empty" state; does not reopen it.

**Third door short list — null.** `campaign_34_thirddoor.py`: `sha256(X)` (plus 5 other fixed
encodings) → compressed/uncompressed P2PKH vs `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9`, prize, and
second, with X drawn only from named leftovers (`31, 73, 42, {1,4,21}, {1,4}, 331, 421, YOUWON,
629998, 840003`, the VIC sentence and its `theyalsoneedfundstolive` tail, both layer-sum concats).
42 values, 416 addresses, **0 matches.** Per the step-3 rule, the list is not grown; a preimage
for `1NULY7…` still counts only if published (matching the standing gate).

**Two items in a pasted "frozen" list are NOT authenticated and must not be built on:**
1. **"Cosmic first layer = XOR of seven SHA-256s (EVP-MD5) → 1327 B (4f7a1e4e…)"** is the
   XOR-of-token-hashes theory falsified at tick 7 and is on the archive's *Excluded on purpose*
   list (`cc/1327-byte decrypt`). Not an input for any "Cosmic second layer."
2. **"Prize pubkey 04f4d1bb…"**: `1GSMG1JC9…` is unspent, so only its hash160 is public — the
   uncompressed pubkey is not revealed until a spend. Any quoted prize pubkey is solver-claimed.
   Likewise `3GSMG24T…`, the `1GSMG1CLx…` dust, and locktimes `629998`/`840003` are unverified.

### Addendum (2026-09-26): the "DBBI/FAED column-sums contain KEY" claim, re-falsified cold

A pasted synthesis re-raised the tick-8 claim and elevated it to Tier A ("hard/reproducible"):
DBBI column-sums = `SAZHMLKEYKRAG` (KEY@7-9), FAED block 6 = `DTEKEYUFFXGTD` (KEY@4-6).
Recomputed the 7×13 column sums under every natural convention — digit map a=0…i=8 and
a=1…i=9, letter base A=0 and A=1, and row-major / column-major / 13×7 fill:

```
DBBI  col-sums -> VFJERAIBCGTAF | UEIDQZHABFSZE | CMQLYHPIJNAHM | BLPKXGOHIMZGL
FAED6 col-sums -> GYLGFBKGCJCYE | FXKFEAJFBIBXD | NFSNMIRNJQJFL | MERMLHQMIPIEK
```

**Neither claimed string reproduces, and "KEY" appears in none of them, under any orientation.**
(The FAED6 value `MERMLHQMIPIEK` matches the tick-8 record exactly.) So `SAZHMLKEYKRAG` /
`DTEKEYUFFXGTD` are produced by a chosen zero-mask, not by the raw sums — mask-overfitting, as
tick 8 found (KEY is forceable in 9–11 of 11 windows in *every* block once a mask is free).
Section 10 leaves Tier A; the dependent `f73d92 → KEY cols → 6,18,25 → FRY` chain (synthesis §11)
collapses with it. The verified-but-coincidental items (f73d92 = 2·11·149·prime(661), 661=91+570,
149=VIC length) remain as recorded at tick 32 (a ~1-in-11 factorization coincidence), and the
103×103 → Half/Better-Half construction inherits the *excluded* 1327-byte blob's unauthenticated
status (issue #104) and yields non-prize addresses. No change to the standing state.

### Addendum (2026-09-26, research only): prize point, carrier, and the 1327-byte decrypt audited

**Correction of the previous addendum.** Caveat 2 there was wrong. The prize pubkey *is* public:
the 2020 halving spend (locktime 629998, recorded at tick 37) revealed it. Verified offline:
`04f4d1bb…3559` lies on secp256k1, hashes to `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` uncompressed
and `1cc6xayvqpeetixmuXDRsGug7GKyoRdxP` compressed. The locktimes 629998/840003 and `3GSMG24T…`
are on the creator trail (tick 38), not unverified. That caveat is retracted. Caveat 1 is refined
below.

**Prize coordinates carry nothing.** x mod 4943/661/149 = 4529/195/105; y = 1860/287/46;
popcounts 122/133 of 256. The vanity lives only in HASH160 of the 65-byte uncompressed encoding.

**U\*D reproduces exactly.** On the 14×14 grid, row_sum+col_sum for the 24 coloured cells in spiral
order, prime→1, gives `010101010010101001000100` = `U*D`. No downstream consequence; exploratory.

**The 1327-byte Cosmic decrypt is reproducible, not authenticated.** XOR of the seven soup-token
SHA-256s (`a795de11…0735`) as a raw 32-byte EVP-MD5 password on the byte-verified Cosmic blob
gives pad 1, 1327 bytes, sha256 `4f7a1e4e…`. So "excluded" concerns the file's provenance, not
reproducibility. Its only intrinsic evidence is a 1-byte pad (~1 in 256).
- **103×103 structure:** row_sum[i]+col_sum[(i+7) mod 103] ranges 80–117, mean 100.8 — the random
  expectation (~103±7); ones fraction 0.4895; no value below 38. "Fitting base-38" therefore needs
  a chosen reduction rule, after which any 64 output bytes are valid scalars.
- **Carrier `1GSMG9VD…` (scalar `abc09ead…`, verified):** P(address begins `1GSMG`) ≈ 1 in 4.48M
  per encoding. A 1,679,616-pair XOR scan over two encodings expects **0.75** chance hits,
  P(≥1) = **0.53**. The second operand `cosmic_A` is not reproducible from authentic inputs, and
  `1GSMG9…` appears only in 2023+ "GSMG WITNESS" chalkboard traffic, not on the creator trail.
  The carrier is not a worked example; it is what a scan that size finds half the time.
- **Half/Better-Half (`1JG648…`/`145ZQ9…`):** 2026 token spray, not traced to `1EtbTv…` or
  `3GSMG24T…` (tick 38). Signatures from them prove control by whoever derived them, which is
  circular. Unauthenticated.

**Net.** The XOR/meet-in-the-middle "demonstration" reading has no authenticated anchor: its
operand is solver-made, its address is off the creator trail, and its hit rate is chance-level.
Standing state unchanged; no search run.

### Addendum (2026-09-26): campaign 35 withdrawn unrun; chance-rate correction

**Campaign 35 withdrawn.** An additive-vanity BSGS script against the prize point was committed
and started, then stopped before any candidate finished. It is a key search against a real
funded address, which the standing boundary (tick 38) rules out. The script is removed and no
result is recorded. The boundary stands: no key searches of any kind against the prize or any
other real address.

**Correction to the previous addendum's chance rate.** P(address begins `1GSMG`) is 58⁻⁴ =
1/11,316,496, not 1/4.48M. A 1,679,616-pair scan therefore expects 0.15 hits (uncompressed
only) or 0.30 (both encodings): P(≥1) ≈ 0.14–0.26. The carrier conclusion is unchanged and
stronger: finding one `1GSMG` in that scan is an ordinary draw.

### Addendum (2026-09-26): the 64-character DBBI⊖VIC suffix is statistically featureless

`XCPKWGBNAXDGJGDUNNVMPABTAFPAAXMJYLZBUWERDNXYDESKUOBXCAMVDJLQTSGA` (after `YOUWON`). Structural
test only; no key material generated.
- 24 distinct letters (no H, I); index of coincidence ×26 = **1.03** (English ≈ 1.73, random ≈
  1.00). Not English and not a transposition of English, so rail-fence/columnar readings are out.
- Periodic IC over periods 2–16: apparent peaks at 11 (1.58) and 15 (1.62), but a 20,000-shuffle
  null with look-elsewhere correction gives P(best period ≥ 1.62) = **0.60**. No Vigenère-style
  period.
- Earlier closures still apply: not hex or Base58 (it contains `O`), not a letter-encoded key
  (tick 15), not a stage-2 key for FAED (tick 20), not a password (campaign 15).

Consistent with tick 15: `YOUWON` marks the operation, and the 21 + 64 letters around it are
residue. Closed.

### Addendum (2026-09-26): step 2 of the pasted plan — the three admissible keys, one pass, empty

Keys: the 21-letter prefix `VOZIJBDTIQBRGVEOMZNBC`, the VIC sentence, `THEMATRIXHASYOU`, each in
upper and lower case. Each raw and as sha256hex / SHA256HEX / sha256(sha256hex) / sha256d,
EVP-MD5 and EVP-SHA256, against the two real locks only (`salph_inner` salt 3ab58534…, P32T salt
b45a5e3d…), strict gate; P32T also checked with the last-block test (primary 0x0a‖0x0f·15,
secondary 0x10·16). **120 trials, 0 hits, 0 near-misses, 0 last-block hits.** Lower-case forms
had already failed in campaigns 01/07/10/16 and the YOUWON campaign; this pass adds the upper-case
forms and the last-block check.

Plan status: step 1 (constraint sheet) exists; step 2 empty; step 3 (third door, campaign 34)
empty; step 4 has no survivor to test. Stop rule met. The public corpus is exhausted; the next
input must be a new creator sentence or page.

### Addendum (2026-09-26): 64-suffix parked for good; vanity-start caveat; corpus exhausted

- **DBBI⊖VIC is position-dependent** (21 distinct shifts, one per VIC letter), so no single
  Vigenère/Caesar key can explain the 64-char suffix. The three admissible running keys (the VIC
  sentence, `THEMATRIXHASYOU`, the 21-letter prefix) already read non-English (prior addendum).
  With IC ≈ random and no period (look-elsewhere P = 0.60), the 64 is **leftover, parked** — no
  more ciphers on it. The missing H,I is one statistic on a residue, not an oracle.
- **Vanity-start caveat.** `d_prize = d0 + i` with small `i` is only a *verification* when `d0` is
  a **named** grind start (as `gsmg.io/theseedisplanted` was named). No token supplies one:
  `yellowblueprimes` and `yinyang` have no value on the constraint sheet, and `matrixsumlist` /
  `lastwordsbeforearchichoice` are soup labels, not scalars. So there is no `d0` chain to check,
  and a ±2^38 BSGS/kangaroo against `Q_prize` is discrete-log on a funded key — not built, not run
  (the standing boundary; the one such script was withdrawn unrun). Shor/42/π are readings of the
  July-2026 notes, not grind origins.
- **Standing state:** the two locks stay gated on a new primary; the third door opens only from a
  pre-registered 2020 colour rule; new creator text enters one candidate at a time. Public corpus
  exhausted; prize key not deduced; address unspent.

### Loop tick 47 (2026-09-26): the two locks are a complementary pair, not two unrelated locks

Adopting the braid/pairing model as the working topology (not proven; falsifiable). It invents no
arithmetic — it rests only on already-verified facts.

**Verified this pass:**
- **YOUWON is origin-invariant.** DBBI⊖VIC with both alphabets at origin 0 (`a=0…8`, `A=0…25`) and
  both at origin 1 (`a=1…9`, `A=1…26`) produce the **identical** 91-letter string containing YOUWON;
  only *mixing* origins destroys it. So the free choice is coordinate-mixing, not 0-vs-1-based — a
  slight upgrade to YOUWON.
- **"Make the best of everything" = elementwise max of the 7 layers → VIC subtraction: negative.**
  Max and min both give no YOUWON, no YINYANG (`ASGIQDHUOW…`, `VNYBIYDMIQ…`). `best = numeric max`
  is a clean negative. `bestofeverything` / `makethebestofeverything` as passwords: no pad≥4 on
  either lock, freeze idle. Spent — do not mutate.

**The model (record; treat the two locks as a pair until falsified):**
```
        GENESIS
       /        \
  main route   "another door"
   Phase-3.2     SalPhaseIon
     VIC(91)       DBBI(91)
        \  DBBI⊖VIC=YOUWON  /
     P32T(96B)      salph_inner(96B)
     "half"         "better half"
        \            /
           YINYANG
```
Support, all authenticated: VIC and DBBI are both 91; P32T (`inner96`, salt b45a5e3d…) and
salph_inner (`miniAB`, salt 3ab58534…) are both `Salted__`+8+80-byte envelopes; DBBI⊖VIC plants
YOUWON across the two routes; the VIC sentence says "the private keys belong to HALF and BETTER
HALF" (plural); the 2020 halving/second-door language ties the second door to the halved prize
(2.5 BTC to `17ucy1…`); `yinyang` is the named future checkpoint.

**Ledger reframing (per the model).** Replace "two unrelated AES locks remain" with: *two
structurally paired 96-byte envelopes, one at the terminus of each authenticated route; the
cross-route DBBI⊖VIC operation plants YOUWON; primary language supplies two keys / half+better-half
/ a second door tied to the halved prize / a future yin-yang. Treat as a complementary pair.*

**Provisional lock→address oracle** (priority ordering from the 2020 source history; swap also
checkable): a P32T key should derive the prize `1GSMG1JC9…`; a salph_inner key should derive the
better-half `17ucy1K9…`. That is a far stronger acceptance than padding.

**Direction (unchanged, and this model sharpens it):** the missing input is *relationship/personal-
context* information a close friend would hold (VIC names two people; #66573 "close friends have the
best chance"), not another byte transform of DBBI. That class of fact is outside the corpus and is
not to be searched for as names/dates/personal data. No grind. The locks stay gated on a new primary.

### Loop tick 48 (2026-09-26): the {1,4,21} selector caveat; 2020 third door frozen

**{1,4,21} selector caveat (record so it never becomes a password-index set).**
`R[1], R[4], R[21] = V, I, C` (1-based) and `R[22:28] = YOUWON` are **facts** in the residual
`R = map0(DBBI) − VIC (mod 26)`. But the index set `{1,4,21}` is two glued readings, not a
soup-derived theorem:
- `{1,4}` = "the two prime layer-sums (331,421) sit at positions 1 and 4 of seven" — a reading of
  `matrixsumlist`.
- `21` = "blue = 73 = the 21st prime" — a later colour-score under the a=0…8 map.
Gluing them yields the set that spells `VIC`. That is one bit of design **or** one bit of
selection; the pedigree of `21` is weaker than `{1,4}`. **Do not write `R[{1,4,21}]=VIC` as a
theorem, and do not use `{1,4,21}` as a password/index set.** What YOUWON authenticates is
*correspondence* between the two 91-streams (`map0(DBBI) − VIC`), not a key; hard success remains
decrypt → scalar → known address, never pad=01.

**Paired-lock oracle is a priority order, not a proof.** P32T→`1GSMG1…` and salph_inner→`17ucy1…`
is the 2020-source-history ordering; **both assignments must be checked**. "Better half = his
partner" names the *class* of the missing fact (relationship/personal context), and licenses no
name/date/password search.

**Third door, 2020-only — frozen.** `campaign_37_thirddoor2020.py`: sha256(X)+5 encodings →
P2PKH vs `1NULY7…`/prize/second, X from 2020 material only — the poem #1710 lines, "First or
zero"→1/0, the URL, the colour frame (`f73d92`/`08c26d`/sequence/bits), yellow/blue counts. **29
X, 288 addresses, 0 matches.** No 31/73/42 or layer-sums (wrong year). Rule frozen; not grown.

**Not next (record):** HNP/kangaroo/BSGS on any real address; Cosmic; any cipher on the 64;
`bestofeverything`/max-layer mutants; extracting operators from the later "everything/best/chance"
hints (those say *why* the public bytes are insufficient, they are not new combinators). The next
compute event is one new-primary candidate through both envelopes with the address oracle.

### Loop tick 49 (2026-09-26): creator personal-infrastructure class, one pass, null

**Sharper reading of #66573/66574** ("close friends have the best chance… but they don't have the
skills some of you do"): a few close friends already *tried and failed*, so the missing input is
not a bare personal referent (a friend would know a nickname/date). It is something a friend would
**recognize as a direction** but lacks the skill to **apply** — public info, personal recognition,
technical execution, three conditions, none sufficient alone.

**The one untested non-Matrix creator-personal class — run and null.** `campaign_38`: his
self-description / contact infra — `electronic_engineer`, `electronicengineer`, `naver`,
`naver.com`, `electronic_engineer@naver.com`, the donation address `1QzA8dwEgp…`, case/separator
variants. Against both locks (EVP-MD5/SHA256, raw + sha256hex, harness gate + P32T freeze) and the
address oracle (sha256 + 5 encodings vs prize/second/1NULY7): **13 candidates, 0 lock hits, 126
addresses, 0 matches.** **Provenance caveat:** the email and donation address are USER-supplied and
are **not** in this repo's authenticated archive; treat this as a USER-grade class, now spent.

**State:** the personal-infra class is closed. No further reading of existing material is
justified — not OP_RETURN n-grams (the refused vocabulary sweep), not the 64-tail, not a new
family. The puzzle is gated on a new primary: a Jrk sentence after the last logged message, a new
gsmg.io page, or a string a circle member actually said — one candidate, one provenance line, one
run through both locks with the symmetric lock→address oracle. Until then, the correct action is
to wait. Address unspent at ~1.25 BTC.

### Tick 49 addendum (2026-09-26): gate refuses the personal-infra class as spent; 4-lock coverage completed

- **gate.py --selftest passes** (positive + refusal controls, frozen decrypt reproduces phase 3.2).
  The five intake candidates (`electronic_engineer`, `electronicengineer`, `naver`, `naver.com`,
  the donation address `1QzA8dwEgp…`) are **REFUSED (spent)** by the gate — tick 49 already put them
  in LEDGER.md and campaign_38, so the frozen gate correctly declines to re-run them. Not a new null;
  a confirmation the class is closed.
- **Coverage completed.** campaign_38 covered salph_inner + P32T + the address oracle; this pass adds
  the two locks the gate would also hit — **miniA and Cosmic**: 13 strings × raw/sha256hex × EVP-MD5/
  SHA256 × 2 locks = 104 decrypts, **0 hits**. So the class is now null across all four locks and the
  prize-address oracle.
- **Provenance caveat.** The intake asserted these were "uttered by Jrk (2026-09-13)"; that is not
  established — they are the email local-part/domain and the on-chain donation address, i.e. public
  contact metadata, not a verified uttered password, and the email/donation address are not in the
  authenticated archive. Fabricated-provenance intake files were removed unpushed. Class closed.

### Tick 50 (2026-09-26): the 64-suffix running-key test — closed; BSGS-on-prize declined

**The one remaining 64-suffix test, run and null.** If the 64-char residue
`XCPKW…QTSGA` were a running-key ciphertext, the key must be one the YOUWON construction itself
names: the VIC sentence, `THEMATRIXHASYOU`, or the 21-letter prefix `VOZIJBDTIQBRGVEOMZNBC`.
Their running-key decodes of the 64 (Vigenère / Beaufort / add) are non-English (gibberish), and
fed as passwords — 11 candidates × raw/sha256hex × EVP-MD5/SHA256 × all four locks (miniA, miniAB,
inner96, cosmic) = 176 decrypts, **0 hits, 0 P32T-freeze**. With IC 0.040 (random), missing H/I the
only non-random mark (both-absent ~0.6%), and the three keys already null as direct passwords
(campaign 36), the suffix is **certified leftover** — residue of the YOUWON subtraction, not a door.

**Personal-infra class:** already closed (tick 49 + addendum); the frozen gate refuses those five
as spent, and all four locks + the address oracle are null. Not re-run.

**BSGS-on-prize `d0` set — declined, not run.** The proposal to take `d0 = sha256(source token)`
and search `Q_prize − d0·G = t·G` over ±2^38 is a discrete-log search against a **funded real
address**. That is excluded by the standing boundary (tick 38, reaffirmed): no BSGS/kangaroo/HNP
against the prize or any real key, regardless of window size. The "small offset around a meaningful
scalar" framing does not change what the run is, and none of the source tokens is a *named* grind
start anyway (tick 48 caveat: yellowblueprimes/yinyang have no value; the soup labels are not
scalars). One such script was already withdrawn unrun. Not revived.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 51 (2026-09-26): `piandonehalf` provenance resolved — a participant's handle; π↔½ phase reading recorded, not run

**Provenance, settled from the primary log.** The only occurrence of `piandonehalf` in the corpus
is creator-log #66912 (2026-07-16): `🤫 (↩ @piandonehalf: thats not a wise move)`. It is the
**Telegram username of another chat member** whom Jrk answered with an emoji. Jrk did not write the
string; the member did, as their account name. Grade: USER. The π-phrase family stays closed and
no `piandonehalf` candidate (1.5π, π+½, π≡½-turn) goes to the gate. Nearby rows (#66909 BIP360
ELI5, #66913 "ELI4.5 is meta", #66931 "you have to be in your prime", replying to "fractions can't be
prime") are banter with the room and give no operand.

**The π↔½ phase chain (42 → 21 → ½ → π → −1 → yin/yang), assessed without a run.**
- The identity `2π·(21/42) = π` is true. But it uses only the numbers already on the sheet, so it
  is a re-expression that adds no bits and yields no bytes, key or index.
- Its inputs are the weakest links on the sheet. `42 = 73 − 31` holds only under the a=0 map
  (house map: 40/88, no 42; tick-verified null ~1 in 1600 combined). `21 = π(73)` is the reading
  tick 48 already marked as weaker pedigree, "not a theorem, not an index set".
- "Any k and 2k are antipodal on a 2k-cycle" is true of every even number, so the ±1 yin/yang
  reading places no constraint on the data.
- The Shor/`Q = dG` end of the chain is discrete-log recovery against the funded address. That
  stays out of scope (tick 50).

**Disposition.** Kept as a descriptive gloss on the sheet's numbers, not as a clue. Not promoted
to slot D. No test was run because no operand or byte string exists to test.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 52 (2026-09-26): the 2021 "neighbors, half and double" outputs re-derived; no operand

Re-derived offline with coincurve from the prize pubkey (`03f4d1bb…a464` = `04f4d1bb…3559`,
revealed by the 2020-05-11 halving spend). Uncompressed P2PKH addresses:

| point | uncompressed P2PKH | user-reported output of tx `a82052a2…` (2021-07-18) |
|---|---|---|
| Q − G | `1G1kRAFR68y6CUq1SAJMzHmjd6sEEgtVUT` | yes |
| Q / 2 | `16eEXbSuKN8tvcos1iKjdju6dAaWWRBMEs` | yes |
| 2Q    | `1KHMK2C8uBptRz67FbrXy43yHzhZG16Hbm` | yes |
| Q + G | `1PhXF3xVQ8Sg9FomBcmRwRbvvGfm3Y2os1` | yes |

All four match. None match in compressed form. The Q/2 address never appeared in the user's
`anti.py` output, so the list was not copied back from that output. **Still unverified here:**
that these four are the actual outputs of `a82052a2…` (no raw tx in the repo, network blocked).
The OP_RETURN text was already recorded above (line ~1593).

**What it is:** creator-side (funded from `3GSMG24T…`) annotation of the public point. **What it
is not:**
- Not proof of knowing d. Q was public from May 2020, so anyone could compute these four points
  and pay them without the private key.
- Not a key path. Each point is its own ECDLP. The spend history of these dust addresses
  would reveal only public keys we can already compute, never d (barring nonce reuse, which
  would need their spending txs as a primary).
- Not a reading of "half and better half". That VIC line names people. #3902 ("the half of prize
  went to better half" → "Well spotted") ties "better half" to `17ucy1…`, not to Q/2.

Its only direction is "operate on the public point", i.e. ECDLP against the funded address, which
stays out of scope (tick 50). Kept as creator lore. Not a password; not sent to the gate.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 53 (2026-09-26): the four derived addresses have never spent; branch closed on-chain

User-run explorer check (this environment's egress to blockstream/mempool is denied):
`1G1kRAFR68…` (Q−G), `16eEXbSuKN8…` (Q/2), `1KHMK2C8uB…` (2Q), `1PhXF3xVQ8…` (Q+G) each have
exactly one transaction, the 2021-07-18 funding tx `a82052a2…`. None has spent, so they expose no
public key and no signature, and there is no nonce surface. The branch is closed. Tick 52 stands:
this is creator lore, not an operand.

**Re-requested gate classes, not re-run.** Class A is lowercased/spaceless forms and substrings of
the 2026 finale lines. The verbatim lines are spent (web intake, 144 decrypts, null), and PREREG's
stop rule excludes case/spacing variants and substrings. Class B (contact infrastructure) is spent
(tick 49 + addendum; the gate refuses it). The proposed intake block labels them
`uttered_password / speaker Jrk`. That provenance is false and was already rejected at the tick-49
addendum, so no intake files were written.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 54 (2026-09-26): creator on-chain OP_RETURN text, eight verbatim candidates, null

Pre-registered in `intake/2026-09-26-opreturn/PREREG.md` (commit `26ec923`, pushed before the
run). `harness/campaign_39_opreturn.py` uses the gate's frozen `run_decrypts`/`run_scalars`
unchanged, plus the P32T freeze oracle and a `17ucy1…` scalar check. It runs outside `gate.py`
because the gate's spent rule refuses text that is merely *recorded* in LEDGER.md (ticks 38/39)
even though it was never *tested*. Of this class only `causality` and `Halving` had ever run.

Candidates, whole and verbatim: "GSMG.io: Right, this is causality", "GSMG.io: do you beleive me
you need it?", "GSMG.io: part of the cipher", "GSMG.io: phase3.2 pass OK", "GSMG.io: are you
sure?", "GSMG.io: You are here because 227 chars were correct", "Good job, Neo!", "GSMG.io
neighbors, half and double".

**128 decrypts, 0 passing the strict PKCS#7 + printable gate, 0 freeze-oracle keys, 0 prize or
`17ucy1…` scalar matches.** Logged in `attempts/campaign_39_opreturn.jsonl`. Byte-exactness is
user-grade (ledger text plus user-supplied txid prefixes; no raw tx hex in the repo). Stop rule
applied: no variants, no prefix stripping, no substrings. The creator OP_RETURN class is spent.

**Gate-rule note (not changed):** "recorded ≠ tested". Any future creator text that was recorded
before it was run needs a pre-registered direct run like this one, not an edit to the frozen gate.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 55 (2026-09-26): Δ42 operator on the DBBI⊖VIC residual, three falsification tests, fails; not run

Proposal (user-relayed): arrange R = map0(DBBI) − VIC (mod 26) as 13×7 and take
Δ42(R)_i = R[i+42] − R[i] (6 rows; "π = negation"). The output is 49 chars,
`ZZONDOXILKEYUFTYXZYYZWIKVPAAWOUWETBBAZUDPAPYDYGRA` (reproduced exactly). As a 7×7, row 2 reads
`ILKEYUF`. `harness/campaign_40_delta42_audit.py` ran the proposer's own tests (no AES):

1. **Marker list over DBBI, VIC and R, every k=1..90, both signs** (KEY, YOUWON, YINYANG, PASSWORD,
   DOOR, HALF, BETTER, NEO, ONE, ZERO; 24,570 positions): **4 hits vs 4.36 expected by chance**.
   VIC gives NEO twice (k=4 and k=19, reversed sign), R gives ONE (k=4) and KEY (k=42). The residual
   is not marker-rich; the transform is generic.
2. **KEY audit:** exactly one KEY in the whole search (R, k=42, later−earlier, index 9). The claimed
   4–6 / 7–9 / 10–12 progression does not reproduce. There are no other KEYs to form one.
3. **Missing KEY at 1–3:** none anywhere in the search. Fails.

For scale: P(KEY somewhere in Δ42 of a random 91-string, one sign) ≈ 0.0026. But the sign was chosen
after seeing the output (the other sign gives `BBMNXMD…`), KEY was chosen after seeing it, and
42 = 73 − 31 holds only under the a=0 map (tick-verified). Under the proposer's stop rule this is a
coincidence. The 49-string is **not run**: "derived_candidate" is not an admissible gate kind, and
the precondition failed. Recorded so it is not re-derived.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 56 (2026-09-26): the "Neo wallet" tx is signed with the Phase-0 seed as a raw key, so it authenticates nobody

User-pasted raw tx (saved to `unverified/tx_8aaa96d3_neo_wallet.hex`), txid `8aaa96d3…00c5`
(computed), locktime 897359 (~May 2025):
- in0 `263d6313…:0`, in1 `f7783baa…:0`, both spent by `148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ`
  (pubkey `030a31a3…bf69`); the two r values differ;
- out0 OP_RETURN `Neo wallet bc1qyw9qv8qntl48rqdfa4g5szzrlaq4d4cn6zhrmg`;
- out1 666 sat → `3GSMG24T…` (the creator's funding vanity);
- out2 2256 sat → `148XH2…` (change).

**Verified:** `030a31a3…` is the public key of the private key `b"gsmg.io/theseedisplanted"`
left-padded to 32 bytes (`addr_check` "rawpad"; also in `prior-sessions/…S1S4/btc.py`). That key is
derivable by anyone who solved Phase 0, so this tx proves only knowledge of the public seed trick,
not membership of the April-2020 "Good job, Neo!" team. **Tick 39 is downgraded:** the "Neo wallet"
self-identification is unauthenticated.

**Open (needs a primary):** were the 2020-04-03 "Good job, Neo!" outputs (txids user-given as
`364de511…`/`722fbf35…`) paid to `148XH2…`? If so, "Good job, Neo!" congratulates the Phase-0
raw-key door, not an unpublished stage past 3.2, and tick 39's lead dissolves. The raw-padded
encoding of puzzle strings vs `1NULY7…` is already covered by `addr_check` (ticks ~1011/1816/2016).

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 57 (2026-09-26): the 227-char phase-2.2 string is not forgotten; scalar check added, null

The string is in the harness verbatim (`aes_try.py`, `campaign_01.PHASE22`). It is 227 chars and
its sha256 is `1a57c572…d2ec30d5`, matching the walkthrough, so no reconstruction is needed. It was
already run as a candidate in campaign_01 across all targets, and campaign_05 ran ~1,100 logged
derivatives of it against miniA, miniAB, inner96/P32T and cosmic. The gate self-test uses it for
the phase-3 decrypt. New here: sha256(S), sha256(sha256hex(S)) and bytes(S) mod N as scalars →
compressed/uncompressed P2PKH vs `1GSMG1…`, `17ucy1…`, `1NULY7…`: 6 addresses, 0 matches.
Bare OP_RETURN phrases and substrings ("half and double", "neighbors") stay excluded by the tick-54
stop rule.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 58 (2026-09-26): salt-as-fingerprint census, null (with solved-stage controls)

Hypothesis (user-relayed): an unsolved envelope's salt = a 64-bit truncation of a hash of some
visible object. Tick 30's salt probe tested ASCII/XOR/reversal, not hash truncation.
1. User's script over the 56 ARCHIVE-README SHA256 records: the only duplicate is two identical
   robots.txt snapshots (2020-09-14, 2022-03-17). No salt, colour or URL anchor occurs in any
   digest, and no pair shares a ≥4-byte prefix or suffix.
2. `harness/campaign_41_salt_census.py`: 82 fixed objects (primary files, stage assets, the three
   solved passwords, VIC/DBBI/soup, the named slot words, both addresses, the prize pubkey, plus
   sha256hex forms) × 7 hashes (sha256, sha256d, md5, sha1, sha512, hash160, identity). Each of 6
   salts is searched anywhere in every digest, both the 3 unsolved salts and the 3 solved-stage
   salts as controls. **64-bit hits 0 (expected 1.6e-12); 32-bit half hits 0 (expected 0.01).**
   Positive control: the cosmic salt is found at offset 8 of its raw envelope.

The solved stages' salts are not fingerprints of their own known passwords, so the creator's
salts behave as ordinary random OpenSSL salts. The salt-fingerprint route is closed.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 59 (2026-09-26): the 2020-03-24 OP_RETURN recipients are answer brainwallets, not people

Checked offline (`prior-sessions/…S1S4/btc.py` + tick 57). Every recipient of the 2020-03-24 series
is the **compressed P2PKH of sha256(stage answer)**:

| OP_RETURN | recipient | = compressed P2PKH of sha256( … ) |
|---|---|---|
| Right, this is causality | `1Jqq37…` | `causality` (phase 2) |
| do you beleive me you need it? | `1GyT5W…` | `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` |
| part of the cipher | `18Cchr…` | the 149-digit VIC string |
| phase3.2 pass OK | `1K23RS…` | `jacquefresco…uncertaintyprinciple` (phase 3.2) |
| are you sure? | `1AD2wf…` | `theflowerblossomsthroughwhatseemstobeaconcretesurface` |
| You are here because 227 chars were correct | `1M5ypv…` | the 227-char phase-2.2 string |

Consequences:
- There are no "six people". The creator marked each solved answer at an address derived from it.
  Anyone who knows the public answer holds the key, so the 2025 "Yes" replies from `1AD2wf…` and
  `1GyT5W…` authenticate nobody. There is no live channel to the creator's trial group here.
- **Creator convention (new, useful):** a confirmed answer X ↦ OP_RETURN dust to
  compressed-P2PKH(sha256(X)). So the recipients of the 2020-04-03 "Good job, Neo!" outputs are
  probably answer addresses of a stage past 3.2, and so is `1NULY7…` (already in `addr_check`). If
  the two recipients are known (txids `364de511…`/`722fbf35…`), they join the offline address oracle
  as zero-cost checks for any future candidate. `prior-sessions/…/btc.py` also expects
  `148XH2…` (seed, raw-padded) and `13HGhj…` (seed, bit-reversed), which fits the same pattern but is
  unconfirmed as the "Good job, Neo!" pair.
- **546 sat is Bitcoin's P2PKH dust limit**, the smallest standard output anyone can send; it is
  not a creator signature. The 2025-09-09 named-vanity tx (`3775e974…`) is post-2023 traffic with no
  shown link to `3GSMG24T…`/`1EtbTv…` inputs (paying *to* `1EtbTv…` proves nothing), so it is
  unauthenticated. Identifying real people behind name-vanities is out of scope.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 60 (2026-09-26): #60312 "Bingo" recovered — it confirms a South Park quote, not a puzzle step

Context recovered from a user screenshot plus pasted chat (`unverified/recovered_reply_context_2026-09-26.txt`;
USER-grade until checked against the JSON export). The creator lines match the transcript IDs exactly
(#60302, #60306, #60307, #60309, #60312, #60314), so the window is aligned.

Sequence: Jrk #60302 "pvp zone … nice and toxic units" → #60306 "Maybe, Cartman's quote about
chatroulette fits too" → D1rty Byrd quotes it ("if you wanna find new friends you gotta weave through
all the dicks first") → Jrk #60312 **"Bingo"**. "Bingo" confirms that the quote was identified. It is
banter about the group's toxicity, not a puzzle statement. **#60312 is closed as a lead.**

Two residues, neither creator-confirmed:
- #60309 "Looks at gnomad. 👀" answers X's "we can't proceed … hint us about the direction". gnomad then
  points to Denis Golovkin's question: was "it's in front of your eyes but you're not seeing it" a
  recommendation to read *Looking Forward* (Jacque Fresco & Ken Keyes, 1969)? Jrk never answers it. The
  three nearest Jrk signals are "No hints, only free will", "Jacque was quite an inspiring lad" and the
  👀. That is a member's reading plus a creator glance, not a creator statement. **Not a gate
  candidate.** It stays user-grade unless Jrk confirms.
- #60307 🤐 replies to X's "@SoWut Are we really…" (truncated; the transcript has "…looking for just the
  btc…?"). Pair it with #66593 "The '5' btc was never the actual prize". The full question text is
  wanted from the export.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 61 (2026-09-26): genesis vs prize — the relation is the subsidy schedule, not a key

Genesis coinbase (user-pasted raw tx, txid `4a5e1e4b…a33b` verified) enters the puzzle once: its
headline, byte-reversed as hex, is part 2 of the 227-char phase-2.2 answer (verified verbatim). Every
other block-0 constant was tested at campaign 23 (13,020 trials, 0 hits). Genesis pubkey `04678afd…`
is not the prize point, and the output is unspendable.

**The real relation is monetary.** The prize is a 1/10-scale mirror of the block subsidy, halved at
each halving by the creator's own announced rule (#5069 "halving the price money at every bitcoin
halving event", #5365, #4603):

| event | subsidy | prize `1GSMG1…` | `17ucy1…` ("better half", #3902) |
|---|---|---|---|
| 2019-04-13 funding (block 571497) | 12.5 | 5.0 | 0 |
| halving 3, tx at block 630001 (OP_RETURN "Halving") | 6.25 | 2.5 | 2.5 |
| halving 4, tx locktime 840003 | 3.125 | 1.25 | 3.75 |
| halving 5, block 1,050,000 (~2028), predicted | 1.5625 | 0.625 | 4.375 |

So "half and better half" is visible on-chain as the halving split. The unsolved prize decays toward
the better half, which only ever receives. #3923 (2020-05-11): "who knows what you'll find after
opening the 2nd door. The price is in half, but what does it mean 🤔". #66593: "The '5' btc was never
the actual prize." Consistent with tick 47: `17ucy1…` is the halving sink and the "funds to live",
most likely not a second payout to solvers. **Prediction (checkable, no compute):** absent a solve,
the prize key signs again just after block 1,050,000, moving 0.625 BTC to `17ucy1…`. That would also
prove the creator still holds the key. Nothing here yields a password or a key.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 62 (2026-09-26): the five checkpoint preimages, verbatim, null; public-ask draft rejected

Pre-registered (`intake/2026-09-26-checkpoints/PREREG.md`, pushed before the run).
`harness/campaign_42_checkpoints.py` used the frozen gate functions, the freeze oracle and scalar
checks. Candidates: `causality`, the prize-address string, the 149-digit VIC string (no earlier literal
trace in harness/logs), `jacquefresco…principle`, `theflowerblossoms…surface`. **80 decrypts, 1 weak
padding event (sha256hex/EVP-MD5 on miniAB, printable 0.44, rejected; ~0.3 expected by chance), 0 hits,
0 freeze keys, 0 address matches.** Together with the 227-char string (tick 57), the checkpoint family
is closed as password material.

**Proposed public ask, not endorsed.** Its premises contradict tick 59. The "recipients" are
sha256(public answer) brainwallets, so the 2025 "Yes" replies authenticate nobody, and there is no
"original submitter" behind an address to contact. Only 6 checkpoints are verified, not 8 (the two
"Good job, Neo!" recipients are unconfirmed). A fair ask would go to the group or thread: who received
"Good job, Neo!" on 2020-04-03, and what did it confirm? That asks about their own public find, with no
personal data.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 63 (2026-09-26): "Good job, Neo!" decoded — it congratulates the Phase-0 raw-key doors; tick 39's lead dissolves

User-pasted raw txs (`unverified/tx_good_job_neo_2020.hex`), decoded offline:
- `f9a1aee2…` (computed txid): in `547246e9…:5`, spent by P2SH-P2WPKH **`3GSMG24T…`** (pubkey
  `0205eaf7…`) → OP_RETURN `Good job, Neo!` + 1000 sat → **`148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ`**.
- `9edc34f0…` (computed txid): in `547246e9…:4`, same key → OP_RETURN `Good job, Neo!` + 1000 sat →
  **`13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp`**.
  (The earlier user-given prefixes `364de511…`/`722fbf35…` do not match the computed txids.)

Both recipients are keys taken directly from the Phase-0 answer: `b"gsmg.io/theseedisplanted"`
zero-padded as a scalar (→ `148XH2…`) and the same 192 bits reversed (→ `13HGhj…`). Re-verified
offline. **So "Good job, Neo!" congratulates finding the seed used as a raw private key (two
encodings). It is not an unpublished stage past 3.2.** Tick 39's "a Neo team found something extra"
lead is withdrawn. The "Neo wallet" tx (tick 56) is someone spending that public-knowledge key.
Creator stamp convention now 8/8: six sha256(answer) keys plus two raw-seed keys.

Bounded follow-up (sourced by this convention): 28 seed-derived keys (the seed, the full URL,
`theseedisplanted`; rjust/ljust/bitrev/byterev/mod-N/sha256; compressed + uncompressed) vs `1NULY7…`,
prize, `17ucy1…`. **Only the two controls hit (`148XH2…`, `13HGhj…`); `1NULY7…` and the prize: 0.**

Third tx (locktime 903634, ~2025-07): `16DUcZT3…` (not a creator address) → OP_RETURN "Its in good
hands with Gavin and everyone..." (a Satoshi quote) + 546/547 sat to all eight stamp addresses and
`1JZBwa…` (the uncompressed `causality` key), change to `1KCcVh…`. A solver who knows the convention;
unauthenticated.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 64 (2026-09-26): #60307 resolved — X quoted Jrk's own 2023 line back at him; August 2023 context verified

Transcript check of a user-relayed analysis:
- #8773 "Ok ok ok ok. I can't hold this one any longer." (to "shine us some light") → **#8774 "Are you
  really looking for just the btc...?"** (2023-08-03) → #8795 "I saw that you guys got really really far
  already." → #8796 "Actually, the hardest part is done." All exact.
- #9599 (2023-08-06, three days later): "Probably the last hint: Once you hit a 'ying yang', you'll be
  able to solve it the same day." Also #9607 "No need. You have all the info." and #9639 (internet only
  to claim). Later: #24627 (2024-04-20: a private key, "obscure" intel, …), #39224/#39237 (2025: yinyang
  is "the next phase", 2 hours max), #66593 ("The '5' btc was never the actual prize"), #66600 ("Some
  already found it. And understood not to risk it... 🤐").
- **#60307 (2026-03-04) closes:** X's question "@SoWut Are we really looking for just the btc...?" is
  Jrk's own #8774 quoted back to him verbatim, and 🤐 is his refusal to expand. No missing operand.

The BTCSEED Bifid head (8 of 9! squares; reported in an Aug-2026 GitHub issue) cannot be what the
2023 line refers to. It is recorded as a forced artifact or decoy, not a door. The named success marker
is still yinyang (slot D).

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent. Remaining
recovery target: #8569's three questions.

### Tick 65 (2026-09-26): "DOUBLE DOWN / no odds / 2×14" is the solved phase-3.2 clue; user-reported nulls recorded

User-relayed analysis ("operator wall, not private-fact wall"). Checked:
- The clue "Raising the stakes without extra chances of winning. A fubcd-king & oracle-queen, thingky
  mvps, on a sad board but as wide as the first one seen." is the **phase-3.2 plaintext's own clue**
  (`materials/phase32_plaintext_outer.txt` line 9). Its words spell the straddling-checkerboard
  alphabet `fubcdora/lethingkymvpszjqwx.` and its width, 14 (the first grid). That stage is solved and
  certified (VIC, rowheads {1,4}, the 91-letter sentence). So DOUBLE DOWN / "no odds" readings are
  readings of an already-consumed instruction, not an endgame operator. The 2×14 board was also tested
  against P32T at tick 1b (182 trials per board, 0) and parked.
- The 11/21 → 96/48 last-words split (A‖B, B = last 48) is campaign 32 (closed, tick ~1296).
- User-reported nulls, USER grade, not re-run: doubledown / double down / doubleornothing / double or
  nothing; B‖A, A/B interleaves, A‖0x00·48, 0x00·48‖B; the odd/even 14-char VIC-alphabet streams
  `FBDR.EHNKMP.QX` / `UCOALTIGYVSJZW` (one pad-01 event, chance). ~60+ decrypts, 0 hits, 0 P32T
  freeze-oracle keys.
- Agreed: checkpoint keys are proof-of-knowledge bearer keys, not identities (tick 59). The framing
  "unknown operation on public ingredients" matches the constraint sheet (slots A–D); what is missing
  is a sourced rule for that operation.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 66 (2026-09-26): item E residue null; #8569 confirmed not public

User-relayed "Ken Thompson cut" (trust only re-derived bytes; community labels count as injected).
Item E: of the proposed passwords, VIC lowercase, `halfandbetterhalf` and the last-words block trace
to campaigns 01/06/10/16/32. The four with no clean trace were pre-registered and run
(`intake/2026-09-26-itemE`, `harness/campaign_43_itemE.py`): empty string, `b45a5e3d827593ca`, the
uppercase VIC sentence, `HALFANDBETTERHALF`. **64 decrypts (all four locks incl. Cosmic, MD5 +
SHA256), 0 padding, 0 freeze keys, 0 address matches.** Item E closed.
#8569: the user found no public copy (GitHub, Wayback, walkthroughs). The only recovery is the
in-group search and screenshot. Correction to item B: Cosmic is a contaminated false positive
(ledger), not an established "claim object".

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 67 (2026-09-26): K₁₄ reading — both "anomalies" are forced by construction

User-relayed K₁₄ proposal (14×14 = 91 + 14 + 91; two 91-streams as edge labels). Checked
(`materials/primary/matrix_grid_spiral_colors.json`, `phase3.2.txt`):
- **12 / 0 / 12 coloured-cell split is forced, not ~2.6%.** The 24 coloured cells are exactly
  spiral indices 7, 15, …, 191, i.e. the last bit of each URL byte on the ccw spiral. Every stride-8
  position on that spiral falls 12 above the diagonal, 0 on it and 12 below. Given the encoding,
  P = 1.
- **VIC 33 / 58 is arithmetic.** 149 digits → 91 tokens forces x + y = 91, x + 2y = 149, so 33
  one-digit and 58 two-digit codes (verified). The "33-byte pubkey / Base58" reading is numerology
  on a forced pair.
- 661 = 7·91 + 24 is already recorded (seven layers + tail).
No source names a graph operation, so the K₁₄ family is not opened. The DOUBLE DOWN / 48+48 half
of the same message is tick 65.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 68 (2026-09-26): K₁₄ edge-space reading, pre-registered and run once — null on structure, text and crypto

User-directed six-step "multiplicity" proposal (place the 91-streams on the edges of K₁₄, apply the
VIC 33/58 mask, treat the coloured cells as edges, compute graph invariants, check them against the
macro labels). Pre-registered at `intake/2026-09-26-k14/PREREG.md` (commit 72805e2, pushed before
the run); `harness/campaign_44_k14.py`, which needs numpy and networkx. The self-test passes 12/12:
τ(K₁₄) = 14¹², K₅/K₈/C₇/Petersen Hamiltonian and tree counts, DP == brute force, batched == exact.

Fixed before any invariant was computed: **the 24 coloured cells contain no mirrored pair.** As
undirected edges they are 24 distinct edges. The proposal's "12 mirrored edges" option does not exist.

- **A. Structure.** VIC 33-edge mask under four placements (row-major RM, column-major CM, spiral
  above the diagonal SPU, spiral below SPL) against 20,000 uniform 33-edge subsets. 28 tests, **min p =
  0.31** (threshold 3.6×10⁻⁴). Every mask graph is connected, λ = 2–3, diameter 3, τ ≈ 1.8×10⁷,
  6,754–18,268 Hamiltonian paths, all at the null median. Weighted K₁₄ (seven layers a=0, VIC A=1,
  residual A=0) against 50,000 shuffles each: 144 tests, **min p = 0.0073** (threshold 6.9×10⁻⁵).
  **0 flagged**, so the English control was not triggered.
- **B. Text.** 49 integer sequences (degree, directed in/out, strength) × 4 mod-26 renderings: no
  `YOUWON`, `HALF` or `YINYANG`. Null rate per strength sequence is 4×10⁻⁵ to 2.6×10⁻⁴. Degree
  sequences cannot render Y at all (max degree 13).
- **C. Crypto.** 138 deduplicated strings through gate.py's frozen path: 2,208 decrypts, 5 PKCS#7
  events (pad 1–2, printable ≤ 0.48; ~8.7 expected by chance), **0 hits, 0 freeze keys, 0 address
  matches**. 53 integer invariants used directly as scalars against the prize and `17ucy1…`: 0.
- **Correction found after the run.** SPL is SPU under the vertex relabelling i → 13 − i (checked
  edge for edge), so the four placements are three up to isomorphism. The Bonferroni divisor was
  conservative; no result changes.
- **The colour graph is shaped by parity, not by choice (descriptive).** Consecutive spiral cells are
  neighbours, so spiral index ≡ row + col (mod 2). The coloured cells sit at indices ≡ 7 (mod 8), so
  every one has row + col odd. Two consequences follow: none can lie on the diagonal (row = col makes
  the sum even), and every coloured edge joins an even vertex to an odd one, so COL24 is bipartite.
  That happens 0 times in 20,000 for random 24-edge sets, and here it is forced. Each 12-edge half is
  a two-tree spanning forest (12% for random 12-edge sets; three of the eight stride-8 offsets do the same).

**Closed per the stop rule:** no new placements, masks, invariants, serializations or maps. The
house map a=1 is not run here; the user reported it null (USER grade). The K₁₄ reading has now had
its one pre-registered pass.

### Tick 69 (2026-09-26): the "simulation / K₁₄ rule-engine" message, audited claim by claim — nothing enters as an anomaly; five corrections

User-relayed message proposing K₁₄ as the fundamental object and asking that two facts go "in red":
(1) 14² = 91 + 14 + 91 with the coloured cells 12 + 0 + 12; (2) VIC 149 → 91 = 33 one-digit + 58
two-digit codewords. Audited by a blind multi-agent pass: one verifier per claim cluster, one
adversary per cluster arguing the opposite verdict, then a completeness critic. All primaries were
recomputed; no verdict was overturned. Every correction below was re-derived again by hand.

**Neither fact goes in red.** Both are true and both are forced. Each is recorded here as closed.

| claim | verdict | null / reason |
|---|---|---|
| 196 = 91+14+91, 91 = C(14,2) | identity; one unforced coincidence | n² = 2·C(n,2)+n for every n. 14 is forced (the smallest square holding the 24-byte URL's 192 bits). Only len(VIC sentence) = 91 is free: P ≈ 0.007–0.015 exact, 0.06–0.08 for any triangular number, ≤ 6 bits |
| "two independent 91-streams" | **false** | DBBI was built letter by letter against the VIC sentence (planted YOUWON, ~3×10⁻⁶ under independence). The two 91s are one design decision, so ticks 42/47 double-count "DBBI 91" as support |
| 12/0/12, "about 2.6%" | forced | 2.6% (0.02595) is right for uniform cells and wrong for this object. Parity (tick 68) makes 0-on-diagonal certain for any odd bit offset. Offsets 5, 6 and 7 give 12/0/12, and the colours use 7, the LSB. Parity-respecting null 0.186; given the encoding P = 1 |
| diagonal 01000000111111 → " ?" | new; forced | 11 of 14 bits are fixed by the encoding: 3 ASCII MSBs (0), 2 padding zeros (spiral 192, 194), 6 lowercase case bits (1). So "?" is certain and the first character is one of ␠ " ( *. The anti-diagonal reads "*>" |
| 33/58 as Bitcoin constants | typical | x = 33 is the English median under this board. Creator-log windows: mean 29.6, sd 4.6, P(x = 33) = 0.07, and 55% of windows lie at least as far out. P(x or y in a fixed Bitcoin set) ≈ 0.4. FUBCDORA is the riddle's row (tick 35), not a frequency row |
| VIC mask = the "zeroed out" mask | coverage gap, low prior | The phrase is #8000 / `hints/2021-12-25-hint.png`, in the same message as primes and "another door", with no VIC link. The mask is FUBCDORA membership, a function of the plaintext; DBBI is independent of it (χ² p = 0.97). **Never applied to DBBI as a zero mask; not run** (tick 68 stop rule; needs a user decision and its own prereg) |
| 661 = 7·91+24, "seven intertwined passwords" | already recorded | The source is the Phase-3.2 Architect text (Beaufort `thematrixhasyou`, letter 1198), "over twentythree ciphers sixteen encryptions and or seven intertwined passwords": a list of alternatives, main route (tick 44). The 24-tail tie is 24 = |URL|; the 31/73 part needs a=0 (ticks 35–36) |
| matrixsumlist = K₁₄ vertex sums | reproduced null; carries little | The user's a=0/a=1 × 4 orders × mask polarities × 7 layers run was reproduced with 0 hits (upgraded from USER grade). K₁₄ is 13-regular, so a=1 sums = a=0 sums + 13 and those renderings are exact ROT13 of each other. The a=1 arm was never independent. The family has no power for KEY (P(hit) ≈ 0.36 under the null) |
| two locks 96 B; Cosmic 1344 = 14·96 | typical | The 96s are true (P32T 16+80, miniA‖miniB 48+48). 1344 is one header + 83 (prime) blocks, not 14 envelopes; on ciphertext 1328/80 = 16.6. 1344 = 28·48 = 42·32 as well. Some named quotient appears ~50% of the time |
| 96 − 91 = 5 = \|enter\| | length zoo | 13% of repo number pairs give a named-length difference, and every difference 3–13 does. It subtracts a header-inclusive size from a letter count |
| raw URL + bit reversal → "two authenticated Neo addresses" | false as worded | These are creator-stamped Phase-0 answer addresses whose keys are public. They authenticate nobody (ticks 56, 63) |
| yinyang "explicitly" resolves the two-lock duality | false as worded | #8446, #9599, #39224 and #39237 make it a named, unreached next phase ("the next phase", "2 hours max"). No primary ties it to the locks; that link is tick 47's model |
| f73d92 chain as a checksum | ledger says coincidence | ~1 in 11 (0.0945 reproduced). The quoted "you reconstructed the machine correctly" has no source |
| colours = URL LSBs as error correction | identity | A 24-bit repetition of bits already in the grid; no parity or ECC content |

**Degrees of freedom.** The K₁₄ reading explains one ≤ 6-bit coincidence (sentence length = C(14,2)).
To state it costs ≥ 12 bits of choices: placement, stream, map, polarity, invariant, rendering and
target, and 429 bits if the placement is unconstrained. Its one pre-registered test (tick 68) was
null on every arm. So it adds degrees of freedom, and the claim that it reduces them is false.
The invariants do reveal the rule engine, and it is the known one: spiral bit layout, byte
framing (LSB colours), English plaintext under a certified board, and a letter-wise cipher aligning
DBBI to VIC. Every listed "anomaly" reduces to one of these four.

**New and recorded:** given the VIC sentence and the a–i alphabet, `YOUWON` can be planted at exactly
one of 86 offsets, 21. So the 21 + 6 + 64 layout, including the "hex-length" 64 tail, is forced by the
construction and is not a second signal. (A random sentence with the VIC letters has any plantable
offset ~21% of the time.) `unverified/salphaseion_dbbi_youwon.md`'s 2.8×10⁻⁷ uses a 26-letter
alphabet; with a–i it is ~3.2×10⁻⁶.

**Corrections to earlier entries:**
1. **Tick 63 txids.** The two "Good job, Neo!" txids are **`364de511…6990`** (→ `148XH2…`) and
   **`722fbf35…e4cb`** (→ `13HGhj…`), the values tick 59 already had. The "computed" `f9a1aee2…` /
   `9edc34f0…` and the remark that the user-given prefixes do not match are wrong; no hash variant of
   the pasted bytes gives them. The same parser reproduces `8aaa96d3…00c5` as a control. The header of
   `unverified/tx_good_job_neo_2020.hex` is corrected. Conclusions about sender and recipients are unchanged.
2. **Tick 63, Gavin tx** (`1fd46162…af92`): it pays **7 of the 8** stamp addresses plus `1JZBwa…`.
   `1M5ypv…` (the 227-char answer) is not among the outputs.
3. **Tick 68 scalar count:** 52 scalars were checked, not 53. The deduplicated value 0 (tree and
   Hamiltonian counts of the 12-edge colour forests) is not a key and was skipped.
4. **Tick 68 power:** the edge-connectivity test could never flag. 33 edges on 14 vertices cap λ at 4,
   and the best achievable p is 0.0058 against 3.6×10⁻⁴. So 4 of the 28 unweighted tests were dead.
   The observed λ = 2–3 is central, so no result changes.
5. **Tick 67 wording:** "every stride-8 position … 12 above, 0 on, 12 below" holds for the LSB set
   (offset 7) and for offsets 5 and 6. Offsets 0–4 give other splits. 0-on-diagonal holds for every
   odd offset, by parity.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent. K₁₄ closed.
The one untested nearby item is the VIC mask applied to DBBI as a zero mask. It is outside the K₁₄
family but inside tick 68's "no new masks" rule, so it waits for an explicit user decision.

### Tick 70 (2026-09-26): the "chain trapdoor" review — mechanics agreed; locktime 629998 is signature-bound to the prize key

User-relayed review, from another assistant, of whether chain mechanics could release `1GSMG1…`:
- OP_RETURN is a memo. It is provably unspendable, pruned from the UTXO set, and never executed.
- nLockTime and CLTV only delay a spend.
- For this P2PKH output, only a valid CHECKSIG under the prize key moves coins.
**Agreed.** It matches the closed OP_RETURN-VM note (`unverified/op_return_script_vm.md`) and the
terminal state: the only path to the key is the puzzle's own content.

Its one caution was to check the GSMG specifics against a node. Checked as far as this
environment allows:
- **Locktime 629998 is verified offline and bound to the key.** `harness/verify_halving_sigs.py`
  rebuilds legacy SIGHASH_ALL for the three P2PKH inputs of `2aa9a4a9…1b13`. It verifies each
  ECDSA signature against the prize pubkey `04f4d1bb…` twice: with the repo's own curve code, and
  independently with the `ecdsa` package. All three are valid, and all three fail when the
  locktime is changed by 1. Sequence is 0xfffffffd, so the locktime is enforced. The inputs are
  two earlier prize outputs (`73e48ff5…:1`, `a2d2481d…:1`) and the 700-sat `Halving` dust
  (`a798905f…:1`). So the holder of the prize key signed a transaction locked to 629998 that pays
  2.5 BTC to `17ucy1…` and spends the dust sent from `3GSMG24T…`. That it was mined, and at which
  height, is not verified here.
- **Not checkable offline:** the 840003 spend has no raw hex in the repo. The `Halving` OP_RETURN
  transaction and the `Good job, Neo!` transactions spend P2SH-P2WPKH inputs. BIP143 signatures
  commit to input amounts, so their contents decode (tick 69) but their signatures cannot be
  checked without chain data.
- **Network:** this environment's policy still refuses mempool.space and blockstream.info
  (connect_rejected), as at tick 37.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 71 (2026-09-26): affine-nonce trapdoor test on the prize key's own signatures — null, with a powered self-test

User-relayed "R = aQ + bG" trapdoor idea: if the prize signer chose a nonce k = a·d + b from the
"neighbors, half and double" vocabulary, d falls out by algebra (d = (z − s·b)/(s·a − r) mod n),
no discrete log. Tested against the creator's own three 2020 halving signatures (Q = `04f4d1bb…`,
verified tick 70). `harness/campaign_45_affine_nonce.py`, pre-registered at
`intake/2026-09-26-affine-nonce/PREREG.md`. Read-only on chain data; the accept predicate is the
hard one, d·G must hash to the prize address, so nothing can be tuned to a false positive.

- **Self-test proves power (5/5):** it plants k = d+1 and recovers d with d·G = Q, plants k = d
  (nonce = key) and recovers it, rejects the wrong (a,b), round-trips a lifted nonce point, and
  confirms a normal random signature matches no (a,b).
- **Real run, null.** Three signatures, three distinct nonces (so no repeated-nonce recovery).
  Twelve single-signature families {d, d±1, 2d, d/2, −d, …}, the pairwise-nonce affine relations,
  and exact point identity R = ±(Q), ±(Q±G), ±2Q, ±(Q/2) with both lifts and both parities:
  **no branch yields a scalar whose point is Q.** The prize signer used ordinary independent
  nonces. There is no planted affine-nonce weakness to exploit.
- **"Robert Doty → R.y" not run: no operand.** The authenticated OP_RETURN payloads are ASCII
  text ("Halving", "GSMG.io neighbors, half and double", "script VM"), not 32-byte binary fields,
  so there is nothing to compare a nonce y-coordinate against.
- **"Apple Pie" / Murray out of scope.** The two scalars in the relayed screenshot were checked:
  `0337dc18…` → `1E5fUmFo…`/`1BKNtBk8…`, `18E14A7B…` (the standard address tutorial key) →
  `16UwLL9R…`/`1PMycacn…`; neither is the Genesis address `1A1zP1e…`. GSMG's prize is `1GSMG1…`,
  not Genesis, and Genesis-block constants were already tested as passwords (tick 26, null).
  zenodo.org is blocked by this environment, so Murray's documents cannot be fetched; the claim is
  not GSMG-relevant regardless.

This complements tick 37 (meet-in-the-middle a+b/a−b/a·b against the prize key, null) and tick 50
(BSGS declined): the prize key is not recoverable by any small algebraic relation to G or to its
own nonces. **State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

**Tick 71 addendum (2026-09-26): the branch is left ready, not open.**
- The three 2020 nonces are distinct: r = `dbe31ca9…`, `fce22a0a…`, `776706ca…`. That matches
  the user's independent read. Nonce reuse (rᵢ = rⱼ ⇒ d = (zᵢ − zⱼ)(sᵢ − sⱼ)⁻¹, then require
  d·G = Q) is part of the pooled pass and stays the standing check for any later author spend.
- "Neighbors, half and double" names point operations, not amounts. Tick 52: the four 2021
  recipients are the uncompressed P2PKH of Q − G, Q/2, 2Q and Q + G. The halving amounts
  (5 → 2.5 + change in 2020, 1.25 in 2024) belong to the separate `Halving` thread. Either way the
  caption is not a nonce instruction set: the affine test is empty on exactly those four operations.
- **Ready on arrival.** `campaign_45_affine_nonce.py --tx A.hex --tx B.hex …` now accepts legacy or
  segwit serialization. It keeps only inputs whose pubkey hashes to the prize, requires each
  signature to verify before using it, and pools signatures across files for the repeated-nonce and
  pairwise checks. Self-test 6/6: the new case is a segwit re-serialization of the 2020 tx. The
  default re-run reproduces the null. A file with no prize input aborts instead of reporting a null.
- **The (a,b) grid is closed.** The source set was the four operations (plus opposite and
  nonce = key). Empty on that set closes the branch; it is not a prompt to try a = 3.
- **Pending, in order:** the 2024 peel raw hex (locktime 840003); any other author spend from
  `1GSMG1…` (reuse + affine on arrival, same command); R.y against a 32-byte authenticated
  OP_RETURN (parked, since no such field exists). AES gates unchanged.

### Tick 72 (2026-09-26): the 2024 peel, signature-verified; affine-nonce and reuse checks null on all six prize signatures

User-pasted raw hex, saved as `materials/chain/tx_halving2024_spend.hex`. txid `88cdb3cd…9df3`,
version 2, **locktime 840003**, sequence 0xfffffffd on every input.
- Inputs: `2aa9a4a9…1b13:0` (the 2020 spend's change), `81d35929…:0`, `f28b0b68…:0`. Outputs:
  **1.25 BTC → `17ucy1…`**, 1.253243 BTC back to `1GSMG1…`. Tick 38's account is confirmed.
- All three inputs are signed by the prize key `04f4d1bb…`, and each signature verifies. So 840003,
  like 629998 (tick 70), is now bound to the key holder's signatures. That it was mined, and at
  which height, is still unverified here (network).
- `campaign_45_affine_nonce.py --tx` ran as pre-registered, unchanged grid. 2024 alone: r =
  `1df5cf84…`, `4c18f2f2…`, `429e4e8f…`, null. **Pooled 2020 + 2024: six prize-key signatures, six
  distinct nonces, no repeated nonce, no single-signature or pairwise affine relation, no point
  identity.** The branch is closed on every prize-key signature known. It reopens only for a new
  author spend, with the same command.

### Tick 73 (2026-09-26): "π is the prime-counting operator", audited — forced or look-elsewhere throughout; three corrections

User-relayed message. Blind workflow: 6 verifiers, 6 adversaries, 1 critic, all primaries recomputed,
no verdict overturned. The corrections were re-derived by hand. The reading is not new: the tick 36
addendum is titled with it and priced its length zoo.

- **The recursive prime-position sieve is forced by the operation (new theorem).** Keeping
  prime-indexed positions repeatedly leaves one survivor. Its original position is always the
  largest term ≤ N of the primeth recurrence a(k+1) = p_{a(k)} (OEIS A007097: 1, 2, 3, 5, 11, 31,
  127, 709, …), with ancestry a(0)…a(k). Proved by induction and brute-forced for N ≤ 2000 with 0
  mismatches. **The survivor is 127 for every N from 127 to 708.** So FAED (570) and a 128-char
  base64 lock both give 127 whatever their content; 127 enters through the sieve itself. The
  survivor characters are 'g' (FAED's commonest symbol, 18.8%) and 'v'/'j' (ciphertext bits of the
  last AES block, 1/64 each; they change with framing).
- **ASCII 127** is #32613 (2024-11-29, LORE): Jrk answering "What character do I have to imagine
  myself as?", i.e. DEL, a joke. π(127) = 31 holds because 127 = p₃₁. Consecutive A007097 members
  in the number zoo: a pair 10–16%, a triple 0.5–1.3% (8–12% allowing π-closure). 709 occurs nowhere.
- **(31,73): the identities are true, but the uniqueness claim is false.** B − Y = Y + π(Y) = 2π(B)
  has **five** solutions: (22,52), (23,55), (25,59), (27,63), (31,73), and none above B = 1134.
  (31,73) is the only one with both members prime, and the largest. Every π identity listed
  (π(Y) = 11, π(B) = 21, 42, "π and one half") follows from that single pair, so they are not
  independent evidence. The pair exists only under a=0. The soup's attested map o=0, a=1…i=9 gives
  (40,88), with no relation and Y+B = 128.
- **π(570) = 104 = |bin1| is new, at 2.2–3.7% (≤ 5 bits before look-elsewhere).** Y + B = 104 was
  already recorded (tick 36). "Tail sum 104 and difference 42" jointly just is the pair.
- **Length network.** π(91) = π(96) = 24 because both lie in [89, 97). π(24) = 9 = yellow was
  rejected at tick 14. π(15) = 6 is in the tick-36 zoo. Iterated-π chains share a value > 2 half
  the time. π(48) = 15 and π(96) = 24 add nothing beyond campaign 32. Aggregate over the structural
  lengths: 10 distinct zoo targets hit against a null mean of 9.5 (p = 0.49).
- **The 104-char / 8×13 prime-filtered FAED.** "Never run" is false: campaign_02 made
  single-level prime-position keeps on FAED (lines 92–94), and deeper levels are nested subsets.
  Fixed descriptive test, statistics set before computing (20,000 random 104-subsets, seed 20260926):
  every statistic falls between the 12th and 82nd percentile (min two-sided p = 0.31), and the
  YOUWON-rule planted-word scan finds 0 targets. FAED_π is an ordinary FAED sample. In
  91 + 104 + 1 = 196, the +1 is ad hoc.
- **Banter sources carry 0 bits.** √−1 → i → I → 73 is #8353 ("At least higher than sqrt(-1)",
  answering "are chances less than 2^-256?"); 88% of letters reach some named number by such routes.
  "Theory of everything" (#8354) names no number. **New provenance:** #8385 (2023-01-25) is a bare
  "42" from Jrk, glossed in the log as an emoji and with no reply context. It is a weak echo of the
  Hitchhiker reading, and it names no operation.
- **User runs** (64 decrypts: the last-words 96-char string with the colours at prime positions;
  16 decrypts: the 0x1f delimiter). Zero padding in both, USER grade. That is the expected outcome
  under the null (P(no pad) = 0.78 and 0.94).

**Corrections:**
1. **Line 161** reads "prime part uses 2,3,5,7; 'too many combinations'". In
   `hints/2021-03-01-primes.png` both phrases are the solver's (Janusz Baran: "just say which primes
   2,3,5,7 we need use", "there are too many combinations"). Jrk wrote only "You are at the prime
   part already???" and "Oh wait, shouldn't have said that. That might have been a hint".
2. The uniqueness claim for (31,73), as above: five solutions.
3. The creator-log gloss for #8385 ("emoji … without text") contradicts its message text, "42".

**Dispositions.** Not pre-registered: the cellwise FAED_π (8×13) − DBBI (7×13) test. No source names
it, and its blockwise analogues ran at ticks 11 and 20. The VIC-mask zero test (open since tick 69)
is **dropped by user decision**. The π-digit branch stays closed (tick 22).

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 74 (2026-09-26): closures — #8569 / #8000, the Genesis-42 readings, and the bare "42" (already spent)

User-directed closures. No new branch is opened.
- **#8569 and #8000 are closed as recovery targets.** #8569's parent is gone (tick 66): parked. #8000
  needs nothing recovered; its full text is in `hints/2021-12-25-hint.png` (tick 69). Neither is
  reopened.
- **The Genesis nonce is 2083236893.** It was already in the v0.1-constants stage (tick 26). The
  "first 42 odd primes" and "42 = 2×21 halvings" readings have no source and are not adopted: the
  same class as the Murray and Gao items.
- **42.** It is not among the v0.1 constants. Byte 0x2a exists in Script only as the generic
  "push the next 42 bytes" data push, never as a named operation. Jrk's bare "42" (#8385) is
  Hitchhiker / theory-of-everything atmosphere and names no gate.py operation.
- **The bare "42" as a passphrase: already run, so skipped per the rule.** campaign_06 ran
  `try_family("42")` (raw "42", sha256hex, SHA256HEX, sha256(sha256hex), sha256d) against every
  target framing, including miniA, miniAB, P32T (inner96) and Cosmic, under all six KDF modes,
  including EVP-MD5 and EVP-SHA256. That is a strict superset of the gate's frozen 16 decrypts, with
  the same decrypt and check functions. Campaign 10 repeated it. Result: no hit. The one logged
  record (`attempts/campaign_06.jsonl`) is pad-1 noise on miniA/MD5, printable 0.29. `gate.py`
  refuses "42" outright: "exact string already in attempts/*.jsonl". **Closed.**
- **yellowblueprimes / yinyang do not qualify as "still untested".** `gate.py` refuses every label
  form (yinyang, yingyang, yin yang, ying yang, YINYANG, yellowblueprimes, yellow blue primes) as
  corpus-spent. The yinyang literals were decrypt-tested in campaigns 01, 03–07 and 10;
  yellowblueprimes was used as a token in the frames of campaigns 14, 16 and 17. They re-enter only
  as a source-named value, never as the label.

**Standing work, restated.** A creator-named string, through `gate.py`, on P32T and the SalPhaseIon
short lock (Cosmic third). Nothing else is queued. **State unchanged:** two locks gated on a new
primary; corpus exhausted; address unspent.

### Tick 75 (2026-09-26): community issues #79 and #55, already covered; #79's recipe reproduces from the noise file

Sources: `puzzlehunt/gsmgio-5btc-puzzle` #79 (labjay69-jpg, 2026-02-20, "Phase 3 SOLVED – Half &
Better Half Derived") and #55 (jackdevs66, 2025-08-23, "Finally I Decrypted Cosmic Duality!").
Community posts, USER grade, read from the public pages. Neither carries a creator-named string.

- **#79 states its recipe in full, and it reproduces exactly.** Take `cosmic_1327b_decrypted.bin`
  (sha256 `4f7a1e4e…`, in `unverified/drive-2026-05/`), read its first 10,609 bits MSB-first as a
  103×103 matrix, and compute row_sum[i] + col_sum[(i+7) mod 103]. Subtract 80, read the result as
  big-endian base-38, and split the 68 bytes 32 + 32 + 4. That gives keys `0423d911…` and `48cc46e6…`,
  which derive `1JG648…`/`15E3pcDD…` and `145ZQ9…`/`1FhbJnrd…`, all as claimed. The other three bit
  and digit orientations do not reproduce. So #79 is internally consistent, and that is all it is:
  - its input is the ~1-in-256 one-byte-pad output of the falsified XOR-of-token-hashes password
    (addendum at line ~1867; tick 7);
  - "subtract 80, base 38" are this file's own minimum and range (80–117). Fitting the base to the
    observed range turns any file into 64 bytes of valid scalars;
  - so anyone can compute the keys from public data, and the signed messages prove nothing. The
    issue itself publishes both keys. The keys are not copied here; prefixes only.
  The addresses are not the prize, and the ARCHIVE-README already excludes "HALF/BETTER-HALF … all
  issue-derived constructions". Nothing for the gate.
- **One untraced fact.** #79 says both addresses were funded on 2026-02-05 and spent on
  2026-02-15. Tick 38's walk followed only vanity counterparties and recorded the two addresses' later
  spray into the prize. The source of the 2026-02-05 funding was never traced. That is the only fact
  that could change the reading. Funding from the creator trail (`1EtbTv…`, `3GSMG24T…` or the prize
  key) would mean the creator acknowledged the construction; any other source keeps it community
  traffic. Given the raw funding tx, the check runs offline: a prize-key P2PKH input (pubkey
  `04f4d1bb…`, signature verifiable) or a `3GSMG24T…` witness pubkey (`0205eaf7…`) shows in the hex.
- **#55 contains no decryption, password or plaintext.** It is a donation request linking
  `jackdevs66/GSMG5_CDuality`, which lines 24–25 call otherwise junk and
  `unverified/salphaseion_xor_token_hashes.md` lists as an LLM-generated carrier of the XOR theory.
  The only thing this repo took from it, the Cosmic base64, is byte-identical to the archive's
  hash-listed raw capture `materials/primary/cosmic_duality_envelope_1344B.bin` (sha256
  `b1895055…`). That settles line 25's residual-risk note. Code from that repo is never run.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 76 (2026-09-26): the 196 = 91 + 14 + 91 scalar test, pre-registered and run once — null

User-relayed follow-up to ticks 67–69: treat DBBI and the VIC sentence, the two 91-symbol streams,
plus a "14-bit middle" as the three parts of 196 = 91 + 14 + 91, and test them as keys.
Pre-registered at `intake/2026-09-26-196split/PREREG.md`, pushed before the run.
`harness/campaign_46_196_split.py`.

- **Definitions fixed before the run.** The 14 in the identity is the main diagonal (`M_diag` =
  `01000000111111`). The spiral's bits 91–104 (`M_spiral` = `10011011001010`) were run as the draft's
  alternative. Its "rows 7–8" is 28 cells and was not run. Both middles are functions of the known
  URL. The draft's residual expression `(ord(d) − ord(v)) % 26 + 65` mixes lower- and upper-case
  offsets, so it is the authenticated YOUWON stream shifted by 6 ("EUACUT" at 21). Both were run,
  labelled; the self-check confirms the shift.
- **Result: 0 of 10 scalars × 2 encodings × 2 addresses** (prize, `17ucy1…`). The scalars:
  sha256(DBBI), sha256(VIC) (a re-check of campaigns 34/43), sha256 of both residual renderings,
  sha256(DBBI ‖ M ‖ VIC) for both middles, and each middle as int(M, 2) and as the integer of its
  ASCII bits. **Closed as thematic, not cryptographic**, by the draft's own rule. No reorderings or
  other middles.
- **Prior worth recording.** The prize address carries a six-character vanity prefix (`1GSMG1`),
  about 1 in 6.6×10⁸ for a random key. A fixed natural-language string's sha256 lands on such a
  prefix with that probability, so any "sha256(puzzle text) = prize key" reading needs text with free
  symbols ground for the vanity. DBBI has such freedom (85 unconstrained a–i symbols around YOUWON),
  which is why its test was worth running; it is null.
- **The pasted K₁₄ solver's five bugs** (clockwise spiral, three flipped bits, 661 applied to a
  196-bit object, the mask never applied, no decrypt) and its repaired 0/140 are USER grade. None
  applies to campaign 44 (tick 68). That run self-checks that the authenticated CCW spiral reproduces
  the URL, reads the grid from the primary JSON, applies the VIC mask, and uses gate.py's decrypt
  path. Its null stands on its own.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 77 (2026-09-26): address-tracing tool for the Half/Better-Half funding question (tick 75)

`harness/trace_address.py` pulls and decodes every transaction of an address from an Esplora API
(mempool.space or blockstream.info) and, offline, decodes raw tx hex. Read-only, no keys. Built to
answer the one open item from tick 75: the source of the 2026-02-05 funding of `1JG648…` (Half) and
`145ZQ9…` (Better Half). A creator-trail funder (`1EtbTv…`, `3GSMG24T…`, prize, `17ucy1…`) would
authenticate the Issue #79 construction; anything else keeps it solver traffic. The tool flags those
addresses on both sides of every decoded tx.

- **Offline decode verified** against the three in-repo txs: reproduces txids `2aa9a4a9…` (629998),
  `88cdb3cd…` (840003) and `1fd46162…` (the Gavin tx), decodes legacy and segwit, and renders P2PKH,
  P2SH, P2WPKH/P2WSH (bech32, BIP173 test vector passes) and OP_RETURN.
- **Online path blocked here.** mempool.space and blockstream.info are refused by this environment's
  network policy (connect_rejected), as at ticks 37/70/72. Run `trace_address.py` on a node or
  unblocked host, or paste the funding tx hex and decode it here with `--decode-hex`.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 78 (2026-09-26): Bitcoin-specific combinations of the Issue #79 keys — null

`harness/campaign_47_halfbetter_combine.py`, address-predicate only, no AES. The two Issue #79
scalars are re-derived in-code from the false-positive file (tick 75), not hardcoded; the self-check
confirms they reproduce `1JG648…`/`145ZQ9…` and their uncompressed forms. No private-key material is
written to source or log (prefixes only: half `0423d911…`, better `48cc46e6…`, trailer `fc0c1b02`).

The user's relayed table (XOR, ±, ×, ÷, mean, sha256 concats, and the a·half + b·better grid) is
reproduced from primary, upgrading it from USER grade, and extended with the Bitcoin-specific class
the ledger had not recorded:
- **41 named constructions**, each vs the prize and `17ucy1…`, compressed and uncompressed:
  the arithmetic set; HMAC-SHA512 both directions; SHA512 concatenations; byte interleaves; BIP32
  (each key as seed, child at paths from the other key's and the trailer's bytes, non-hardened and
  hardened, plus each master key); and the point sum (H+B).x raw, hashed, and trailer-offset.
- **16,641 linear pairs** a·half + b·better for a,b ∈ [−64,64], compared as points against the prize
  public key `04f4d1bb…` (17ucy1's key is not public; the arithmetic checks cover it by address).
- **0 hits.** Runs in ~5 s (precomputed point multiples + one add per pair; the naive address-per-pair
  version was ~250× slower and was replaced).

This closes the "combine the two #79 keys with a Bitcoin construction, not just arithmetic" question.
As tick 75 established, the operands are slices of a one-byte-pad false-positive decrypt, so no
combination of them can produce the prize scalar; this records it on primary. The real Half/Better-Half,
if the puzzle has them, live behind the two OpenSSL locks, which still wait on a creator-named string.
The one open on-chain item is unchanged: the 2026-02-05 funding source of the two addresses
(`harness/trace_address.py`, tick 77), pending network or pasted hex.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 79 (2026-09-26): the Half-address funding trace resolves tick 75 — NONE creator-trail; it is the dust-spray source

User ran `harness/trace_address.py --addr 1JG648…` (Half) on mempool.space: **105 transactions,
creator-trail funders among inputs: NONE.** Decoded flows (user-pasted, offline-decodable):
- **`1JG648…` pays the puzzle addresses**, it does not receive from them: tx `d1f774f1…` sends 70,000
  sat to the prize `1GSMG1…`; `54da8139…` sends 5,000 sat to `17ucy1…`; `b6867f5a…` spends `1JG648…`
  and `145ZQ9…` together. This is the 2026 dust spray of tick 38, now confirmed by decode.
- **Its own funding is ordinary segwit change** (`bc1qekdql74…`, `bc1qm8qw4y0…`, `bc1qrft2p4…`,
  `bc1q39hn5…`), none on the creator trail (`1EtbTv…`, `3GSMG24T…`, prize, `17ucy1…`).
So the one open on-chain item from tick 75 is closed: the Issue #79 addresses were **not** funded by
the creator. They are solver-controlled addresses spraying dust at the prize. Issue #79 is confirmed
solver traffic, not a creator acknowledgement; its keys remain false-positive artifacts (tick 75/78).
The Half/Better-Half branch is closed on-chain. (Trace files land under
`materials/chain/traces/1JG648…/` when run; not committed from the sandbox, which the network blocks.)

### Tick 80 (2026-09-26): the "Looking Forward" / Jacque Fresco direction — provenance corrected, adjacent strings null

User-relayed claim that Jrk's "Bingo" confirmed *Looking Forward* (Jacque Fresco) as the reading of
"it's in front of your eyes but you're not seeing it". **Overstated, per tick 60 (primary-checked):**
#60312 "Bingo" confirms the Cartman chatroulette quote D1rty Byrd had just posted; Jrk never answered
Denis Golovkin's Looking-Forward question (his only response was #60306 "Maybe, Cartman's quote fits
too", plus the 👀). "Jacque was quite an inspiring lad" (#60303) is praise, not an instruction. And
`jacquefresco` is already the phase-3.2 preimage, so Fresco points **backward** to a solved stage.
- **Core strings already spent** (tick 60 / corpus): `lookingforward`, `Looking Forward`,
  `looking forward`, `jacquefresco`, `Jacque Fresco`, `thevenusproject`, `venusproject`,
  `itsinfrontofyoureyesbutyourenotseeingit`, and case/spacing variants — 13 forms, all refused by the gate.
- **12 genuinely-new adjacent strings, run once** (`intake/2026-09-26-fresco`,
  `harness/campaign_48_fresco.py`): the Fresco titles and Venus-Project concepts
  (`thebestthatmoneycantbuy`, `sociocyberneering`, `resourcebasedeconomy`, `futurebydesign`,
  `cybernetics`, `nothinghastobechangedonlyrediscovered`, …). **192 decrypts (all four locks, MD5+SHA256,
  raw+sha256hex), 2 chance pad-1 events, 0 hits, 0 address matches.** Direction closed.
- **Not done: the public ask.** Opening an issue on `puzzlehunt/gsmgio-5btc-puzzle` to ask the 2020
  checkpoint recipients what they submitted is outward-facing and was drafted-and-rejected at tick 62.
  It stays a user decision; not posted.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

**Tick 80 addendum (2026-09-26, user run + framing).** Salts verified: `salph_inner`/miniA
`3ab585348552415d` (ct 32 B; miniA‖miniB = 96 B, same header salt), `P32T` `b45a5e3d827593ca` (ct 80 B).
- **User ran the title-grade set** — `lookingforward` / `Looking Forward` / `LookingForward` /
  `looking forward`, `itsinfrontofyoureyesbutyourenotseeingit`, `No hints, only free will` /
  `only free will` / `freewill` / `free will` — raw / sha256-raw / sha256-hex × MD5/SHA256 EVP × the
  three envelopes. **162 decrypts, zero pad≠garbage, zero hex-key / high-printable bodies.** USER-grade;
  corroborates the corpus-spent status of these strings. The book title is null on both 80-byte locks.
- **Provenance, stated precisely:** the #60312 "Bingo" → *Looking Forward* attribution holds only if
  the JSON export shows that exact reply threading. The screenshot leaves it ambiguous (tick 60 read
  the Bingo as the Cartman quote, immediately preceding it). Until the export, both readings are USER-grade.
- **Disposition:** Fresco is the already-used phase-4 password plus, at most, a confirmed reading
  direction — not a KDF input. The Venus-Project bibliography is adjacent (Matrix-n-gram class) and is
  not added beyond the 12 already run null. The public ask stays unposted: those checkpoint strings
  are already public, so it buys nothing. Watch `1GSMG1…`; the next compute event is a new sentence,
  not a Fresco corpus.

### Tick 81 (2026-09-26): outside-the-box — the KDF assumption challenged (PBKDF2), null with passing controls

Every prior tick derived AES keys with OpenSSL EVP_BytesToKey (MD5/SHA1/SHA256). **PBKDF2
(`openssl enc -pbkdf2`, the OpenSSL 3.0+ default recommendation) had never been tested** (grep
confirms: no pbkdf2/-iter anywhere). The self-test proves EVP only for the three *solved* 2019–2020
blobs; the unsolved 2023 SalPhaseIon locks have never been opened, so nothing established their KDF.
If it were PBKDF2, every password ever tried against them would have been derived wrong and every
null void. This is the single assumption whose failure would invalidate the most work, so it was
worth one rigorous pass. `harness/campaign_49_pbkdf2.py`.

- **Controls all pass.** (A) the PBKDF2 key/iv derivation round-trips an `openssl enc -pbkdf2` blob
  (OpenSSL 3.0.13) exactly; (B) EVP still opens the three solved blobs; (C) PBKDF2 does **not** open
  the solved blobs with their known passwords — so PBKDF2 is genuinely a different KDF and a hit would
  have meant something.
- **Test.** 24 strongest known candidates (the solved-stage answers and structural labels — strings
  that would *be* the answer if only the KDF were wrong; no new vocabulary) × {raw, sha256hex} ×
  {miniA, salph_inner, P32T, Cosmic} × PBKDF2-HMAC-{sha256, sha1, md5} × iters {1, 1000, 2048, 4096,
  10000, 100000}. **3,456 decrypts, 15 chance pad events, 0 strong hits** (no strict pad, no P32T
  freeze key, no prize/17ucy1 address from any 64-hex body).
- **Value even though null.** The EVP-only nulls of the whole campaign are now robust to the KDF
  question: the locks do not open under PBKDF2 for any password that would plausibly be the answer.
  OpenSSL still defaults to EVP even in 3.x unless `-pbkdf2` is passed, and the solved blobs fix the
  creator's tooling as EVP-SHA256, so this was low-prior; it is now closed rather than assumed.

**Remaining unexamined assumption (flagged, not yet actionable here):** the reconstructed ciphertext
of the SalPhaseIon short lock (miniA‖miniB) and Cosmic carry a residual transcription risk on their
last base64 lines (README note). A corrupted final block would make PKCS#7 reject even the true
password. Ruling this out needs an independent re-capture of the SalPhaseIon page ciphertext
(gsmg.io / web.archive.org), which this environment's network blocks; it is a clean task for an
unblocked host.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 82 (2026-09-26): correction — the community "XOR-of-seven = solved" claim is the falsified padding hit; three locks kept distinct

A web-sourced "known solution" (jackdevs66 lineage) was relayed: seven tokens → SHA-256 → XOR →
MD5-EVP on Cosmic → the 1327-byte payload (`4f7a1e4e…`), presented as the solved SalPhaseIon stage
with a "Half and Better Half protocol" plaintext. **This is the XOR-of-token-hashes theory already
falsified here (tick 7; `unverified/salphaseion_xor_token_hashes.md`; archive "Excluded on purpose:
cosmic_A, cc/1327-byte decrypt").** Re-confirmed this tick:
- The XOR reproduces (`a795de11…0735` → decrypt sha256 `4f7a1e4e…`), but the payload is **noise**:
  entropy **7.870 bits/byte** (≈ urandom), and the only evidence is a **1-byte PKCS#7 pad** (ct 1328 →
  pt 1327), the cheapest chance success on an 1328-byte blob. It is not plaintext; the "Matrix
  narrative / Half & Better Half protocol" read off it is fanfiction on high-entropy bytes.
- **Accept predicate:** the prize `1GSMG1…` is unspent. jackdevs66 (#55) said themselves they did not
  find the key; the later "SOLVED" issues (#69 etc.) produced no spend (ticks 75, 79).
- **Three distinct 80-byte-class locks, not to be conflated** (verified salts/sizes):
  SalPhaseIon short `3ab585348552415d` (ct 80), Phase-3.2 trailing / P32T `b45a5e3d827593ca` (ct 80),
  Cosmic `2d3f6fe06dc950e6` (ct 1328). `b45a…` is a separate authenticated file (the phase-3.2 trailing
  envelope), **not** a mis-transcription of Cosmic. The pasted 7-token list
  (`…thispassword, matrixsumlist, yourlastcommand, secondanswer`) is itself community-invented — it
  double-lists `matrixsumlist` and coins tokens the master hint does not name (yellowblueprimes,
  matrixsumlist, lastwordsbeforearchichoice, yinyang).
- The tick-81 short-lock re-capture item still stands and is unrelated to this: it concerns the
  `3ab5…` / Cosmic base64 transcription, not the XOR method.

**Do not treat `4f7a1e4e…` as plaintext or KDF output.** Standing work unchanged: a creator-named
candidate through `gate.py` on the correct envelope (`3ab5…` short, `b45a…` trailing, Cosmic
separately). Prize unspent; corpus exhausted; two locks gated on a new primary.

### Tick 83 (2026-09-26): grave-detail "what did we miss" audit (4 agents) — three escape-hatches found and closed

A four-agent parallel audit (MITM/EC, AES-lock acceptance, soup operators, primary provenance)
hunted for missed avenues. Net: real gaps were found and **closed**; the endgame is now more firmly
gated, not less.

- **MITM pool gap → closed (curated re-run null).** Tick 37 ran the correct point-collision MITM
  (a+b, a−b, a·b vs the prize point Q) but over a pool that lowercases and 4-word-caps everything,
  so it was MISSING the S1–S4 seed scalars (and their C1–C6 constructions), most canonical answers,
  `YOUWON`/`yinyang`, the layer-sum concatenations, and the three salts. `campaign_50_mitm_curated.py`
  adds all of these (163,515 base + 59 new) and re-runs: **no hit** on add/sub/mul vs Q (24 s). So
  "prize = half ± better / half·better" is closed for the corrected pool, not just the old one.
  (Also newly closed by the audit: 17ucy1 is **not** a point-function of Q — Q/2, 2Q, Q±G, ±Q all
  ≠ 17ucy1 — so the "half = prize/2 as a key" reading is false; the 2.5-BTC split is an amount, and
  17ucy1 is an independent key with no public pubkey, hence no MITM surface.)
- **Accept-rule false-negative gap → closed for strong candidates.** `check_pt` hard-rejects a decrypt
  on invalid PKCS#7 **before** any printability/address test, and the address oracle sits behind that
  gate — so a right password whose plaintext is a raw 32-byte key (miniA, −nopad), or whose final CBC
  block were corrupted, would be silently dropped. `campaign_51_padding_independent.py` bypasses the
  pad gate: per strong candidate × {raw, sha256hex} × EVP-{md5,sha256} × 4 locks it scans the FULL
  plaintext for a 64-hex→prize/17ucy1 address, tests `pt[:32]`/`pt[32:64]` as raw keys, and checks
  tail-robust prefix printability. **464 decrypts, 0 address hits, 0 printable prefixes.** So the pad
  gate was not hiding a known-candidate solution.
- **Ciphertext transcription risk (tick 81) → closed in-repo, verified.** Two independent
  web.archive.org captures (`materials/wayback/pages/salphaseion_2024-11-23.html`,
  `…2025-10-31.html`) carry the SalPhaseIon soup byte-identical to `salphaseion_soup_space_separated.txt`
  (sha256 `d39d10b1…`; the soup contains both mini-lock base64 runs) and the Cosmic block decoding
  byte-identical to `cosmic_duality_envelope_1344B.bin` (sha256 `b1895055…`). Three independent sources
  agree, so the mini-lock and Cosmic ciphertexts are correct; every EVP/PBKDF2 null is now robust to
  the transcription question as well as the KDF question. (Agent 2's tail-corruption concern was real
  in principle but is moot given verified bytes; the padding-independent oracle above remains as the
  structural fix for the −nopad/raw-key reading.)

Residual accept-rule notes (low prior, recorded not run): the live gate omits aes-128/192 and EVP-sha1
and the miniB_* variants for new intakes; a miniAB last-block freeze oracle (analogue of p32t_freeze,
two-raw-keys P5) is not built. None applies to the solved blobs (all EVP-sha256/aes-256). Provenance
audit (tick 84 pending) surfaced the Telegram JSON export and a lead-solver ask as the real levers.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent.

### Tick 84 (2026-09-26): audit part 2 — soup operators exhausted; natural last-words decrypted bare (null); provenance levers; NEXT_PASS.md

Soup-operator and provenance agents completed the tick-83 audit.
- **Soup→string operators exhausted.** No missed deterministic operator emits a new confirming word.
  `DBBI⊖VIC→YOUWON` is terminal (no second planted word in the prefix/tail/reversals); `BIN1`→
  `matrixsumlist` and `BIN2`→`enter` are fully consumed (104=13×8, 40=5×8; only byte-reversed twins,
  no residue); FAED carries no planted string under layer⊖DBBI, pairwise layer differences, self-halves,
  or ⊖ any authenticated 570-char text. The 4-token master-hint assembly is a **missing-operand** state,
  not a missed operation (`yellowblueprimes`/`yinyang` have no computed value).
- **Gate-hygiene gap found and closed.** The natural last-words phrases the soup grammar designates as
  the password ("the last words before the architect's choice" → `…goodluckneverthelessireallyhope`
  `youretheoneciaobellao`, from `phase3.2.ipynb`) were only ever **refused by gate.py as corpus-present**,
  never decrypted (verified: 0 in `attempts/*.jsonl`). `campaign_52_lastwords_bare.py` decrypts them and
  the soup instructions (`yourlastcommand`, `firsthintisyourlastcommand`, `shabefanstoo`) bare: **224
  decrypts, 1 chance pad, 0 hits, 0 freeze keys.** campaign_32 had tested only arbitrary 48/96-char cuts.
- **Provenance levers (recorded).** No creator line names an operation on any 80-byte blob (confirms
  tick 31). The real external levers: (1) the **Telegram JSON export** (resolves the #60312 Bingo
  threading, the truncated #66568/#66592/#32579 tails, #8569's questions); (2) a human ask to the
  **lead solvers** the creator said got past "the hardest part" (#8795/#8796, #4694, VrsN), for an
  uttered post-3.2 intermediate — gate-admissible, unlike the tick-62 checkpoint ask. New reading:
  #66573 "close friends… solving *it*" may attach to the **secret/payload** (#66592/#66593 "the 5 btc
  was never the actual prize"), not the key — in which case the key stays corpus-derivable and only its
  meaning is social; the export distinguishes these.
- **`neo/NEXT_PASS.md`** written: the do-not-repeat inventory, the three closed escape-hatches, the
  meet-in-the-middle verdict (pool closed; 17ucy1 has no MITM surface; BSGS-from-seed-center is the one
  un-run EC test), and the ranked lever list.

**State unchanged:** two locks gated on a new primary; corpus exhausted; address unspent. The audit
closed the KDF, accept-rule, transcription, MITM-pool and soup-operator escape-hatches; the frontier is
now firmly external (export / lead-solver ask) plus the single bounded BSGS-from-seed-center check.

### Tick 85 (2026-09-26): Issue #108 "two typos" verified a non-issue; the three envelopes byte-pinned

User-relayed provenance closure on the short-lock "first-diff" question. Verified in-repo:
- **The three committed envelopes byte-pin to the relayed baselines exactly:** SalPhaseIon short
  (miniA‖miniB, 96 B) sha256 `9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258`,
  salt `3ab585348552415d`, last block `ef756397ea74234a97a95f01ae37f8c9`; P32T/inner96 (96 B)
  `291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9`, salt `b45a5e3d827593ca`, last
  block `5334de08884878aaed7c99d0b4340bf8`; Cosmic (1344 B) `b18950551a4dd0cb…`, salt
  `2d3f6fe06dc950e6`, last block `5bbf983669ed922eb12dff1dcc3f6fc6`.
- **Issue #108's alleged short-lock typos are a non-issue.** #108 claims base64 positions 18 and 51
  should read J and s (vs a "corrupted" R and k). The committed base64 already has **J at position 18
  and s at position 51 (0-based)** — verified; R/k occur only elsewhere (R at 47/85/98, k at
  8/39/78/99). So #108's "fixed" blob is byte-identical to the standing committed object (both hash
  `9e2831e1…`); there is no competing corrected artifact. #108's downstream CADEIA construction
  depends on the already-rejected 1327-byte Cosmic decrypt (ticks 7/82), so nothing there reopens.
- **Relayed but not independently checkable here** (network-blocked): that Naddiseo/gsmgio-5btc-puzzle
  commit `dcb66952` (2023-08-31) already carries the J/s base64, predating #108's 2026 "typo" claim by
  ~3 years. Recorded USER-grade; it corroborates the wayback captures (tick 83, verified) as a third
  independent source. Absent a dated capture of any R/k text, the "corruption" assertion has no
  evidentiary weight against the byte-pinned object.

**Boxed state, tightened:** three ciphertext objects are byte-pinned (hashes above); EC/MITM over the
public corpus is exhausted (curated pool, two- and three-way, null — tick 83); AES/KDF families are
exhausted (incl. PBKDF2 — tick 81); the #55/#79/#108 Cosmic chain is non-authentic; no source-named
rewrite remains. **The next computational event requires new primary creator material through
`gate.py`.** Prize unspent.

### Tick 86 (2026-09-26): the single-file offline solver, validated end-to-end and committed

User-built `harness/gsmg_offline_solver.py` — a conservative, dependency-light (pycryptodome only)
single-file consolidation of the Tick-85 frozen state. It generates no candidates and reopens no
MITM/BSGS; it verifies the three byte-pinned ciphertexts, then runs exactly one supplied string
through the frozen path. Validated end-to-end here (pycryptodome present):
- **`audit`**: the three envelopes byte-pin to the tick-85 hashes/salts/last-blocks, and the
  Issue-#108 base64 positions read J (18) / s (51). PASS.
- **`selftest`**: audit + the three solved blobs decrypt under sha256hex × EVP-SHA256 + the
  secp256k1 privkey=1 control. PASS.
- **`test`**: 12 decrypts (3 locks × {raw, sha256hex} × EVP-{md5, sha256}) with the padding-independent
  raw-32/hex-64 → prize/17ucy1 oracle, the P32T last-block freeze, and sha256(candidate)/candidate-as-hex
  scalar checks; per-candidate sha256 dedupe log. Confirmed null on a spent control and REFUSED on a
  repeat without `--force`.
- **`opreturn`**: exact-only comparator of a 32-byte payload against supplied nonce-point x/y
  (big-endian and byte-reversed). Confirmed it flags a true x-match and its byte-reversal and reports
  no-match otherwise.
It is the frozen gate as a portable field tool; `neo/harness/gate.py` remains the in-repo entry point.
No behavioral divergence from the committed harness. Its run log (`offline_solver_attempts.jsonl`) is
local and gitignored.

**State unchanged:** two locks + Cosmic byte-pinned and closed; corpus exhausted; prize unspent; the
next computational event requires new primary creator material through the gate.

### Tick 87 (2026-09-26): Satoshi's P2P birth date / EO 6102 / gold has no creator anchor; the creator's one named date (Neo's passport expiry) pre-registered and run, null

User-relayed framing: 5 Apr 1975 is Satoshi's *self-reported* P2P Foundation birth date (unverified,
widely read as symbolic: EO 6102 of 5 Apr 1933; private gold ownership legal again in 1975). The user
searched the authenticated Jrk corpus for April 5 / 5 April / 1975 / 6102 / gold / Satoshi /
Nakamoto / birthday / born and found nothing. Their classification: the Satoshi date is a real public
Bitcoin referent; the biblical-calendar mapping (24 Nisan ↔ 24 coloured cells, 9th Omer ↔ 9 yellow,
Shmini ↔ every 8th bit) is a secondary coincidence; neither is a licensed lock input. Bounded
question: does any authenticated puzzle object point to that date, or to 6102/gold?

**Repo-wide census: no.**
1. **Creator's own words** (510 parsed rows of the 445-message log, reply context stripped): 0 hits
   for the user's list, and no creator message is dated on any 5 April. This reproduces the user's check.
2. **Puzzle pages and solved stages** (phases 0–3.2, SalPhaseIon, Cosmic, Decentraland, wayback
   pages): no `1975`, `6102`, `1933`, `gold`, `Satoshi`, `Nakamoto` or `birthday`. The nearest
   neighbours are both already consumed in the hash-confirmed phase-3 password (`1a57c572…`):
   phase 2.2 part 5 is an executive-order riddle about money ("never execute an order that revokes
   the highest power or you might suddenly get killed" → JFK's EO **11110**, Treasury/silver
   certificates, chosen because it reads as binary); part 6 ("random magic pieces of metal", a
   "green" idea that "came back") resolves to Satoshi's genesis coinbase (v0.1 `main.cpp:1616`).
   Monetary executive orders, metal lore and Satoshi's own artefacts are therefore creator-native
   vocabulary, but the pointers land on 11110 and the genesis block, not on 6102, gold or 1975.
   Tick 26 already swept Bitcoin v0.1 constants and satoshi/nakamoto vocabulary (13,020 + 792, 0 hits).
3. **On-chain:** the creator's calendar is the halving (locktimes 629998/840003, OP_RETURN "Halving",
   "Happy halving!" in 2020 and 2024). These are block heights, not birthdays.
4. **False friends:** `wayback/pages/choiceisanillusion_2026-04-05.html` is an archive.org crawl
   date; the "gold logo" of the 2026-08-19 finale is the brand colour; `6102` occurs only inside
   random sha256 hex in attempt logs.

**The creator's own rule on dates.** #8048 (2021-12-31), in reply to "…i also want to ask questions
like, how old are you": *"The only date I give away is the expiry date of neo's passport."* He
repeats it in #8516 (2023-05-02): *"Still remarkable that scene. Especially the expiration date of
his passport 😁."* Asked a birth-date-type question, the creator names exactly one date and rules
out the rest. That cuts against any birthday reading, Satoshi's included. The referent is *The
Matrix* (1999): Thomas A. Anderson's passport expires 11 Sep 2001, printed "11 Sep/Sep 01".

**campaign_53** (pre-registered in `intake/2026-09-26-passport/PREREG.md`, committed before the
run). 51 fixed forms of 11 Sep 2001: as printed, DMY/MDY/YMD in text and numeric, MRZ
`010911`/`0109110`, unix `1000166400`, `9/11`, `911`, … Each ran through the frozen gate path
(16 decrypts), the P32T freeze, the padding-independent scan, and addr_check (510 addresses).
**Result: 816 decrypts, 3 PKCS#7-valid (3.2 expected by chance), 0 hits, 0 freeze passes, 0
address matches.** 43 of the 51 were new to the gate's spent check. Of the other 8, only
`911`/`nineeleven` had been decrypted before (campaign_22_911, tick 24's unrelated π-"9:11" claim). The PREREG's "no form of this date occurs" line overstated this for those two short forms.
The `11 Sep 2001` forms occurred only as the log's annotation text. #8048 is LORE (a deflection),
so the prior was low. It ran because it is the only date the creator names, it was untested, and
the test was bounded.

**Classification.** Satoshi's birth date: a public Bitcoin referent with no creator anchor, so it
stays unlicensed. 6102/gold: adjacent to phase 2.2's executive-order riddle, but that riddle is
spent on 11110. Biblical mapping: coincidence, unlicensed. Neo's passport date: the one creator-named
date, now **closed** under the stop rule (no other passport fields, film dates, translations or
format variants).

**State unchanged:** three locks byte-pinned; corpus exhausted; `1GSMG1…` unspent.

### Tick 88 (2026-09-26): receipt-topology audit — the halves transact, never co-sign; the "third entry" is the 2020 memo→split link, and it carries no key

User-relayed hypothesis (from outside this session: Jeffries 2017 on triple-entry accounting;
Ijiri's momentum accounting; Grigg 2005, "the receipt is the transaction"): HALF and BETTER HALF do
not combine algebraically, they *transact*, and the chain is their shared signed receipt. "They also
need funds to live" is literal: a key becomes an actor only once funded. Asked: audit the
authenticated transaction *topology* (no values as passwords, no txids into AES) as a receipt
system: authorisation + counterparty + signed receipt.

**Provenance of the concept: none in the puzzle.** 0 matches in the repo or in the creator's own
words for Jeffries / Ijiri / Grigg / triple-entry / "one pill" / Ricardian / bookkeeping, and no
receipt/ledger/accounting vocabulary in his messages. His only "cicada" (#7152, 2021-04-06: "Some
parts of cicada puzzles are still unsolved. Must be bad design.") means Cicada 3301, a homonym of
Jeffries' project. Rabbit, pill and architect co-occur in any Matrix-themed crypto text, so the
thematic overlap is weak evidence. The article itself was not fetched here.

**Audit** (`harness/receipt_topology.py`, offline, no network, reads only saved raw hex). It decoded
7 saved transactions (5 creator-signed) and re-verified every legacy P2PKH signature, including
compressed keys. The six checkpoint addresses re-derive from their answers (tick 59 prefixes, all
match) and the four 2021 points re-derive from Q (tick 52, all match).

| # | when | authorised by | memo | counterparty (its key) | what the chain certifies |
|---|---|---|---|---|---|
| 1 | 2020-03-24 ×6 *(recorded)* | `3GSMG24T…` | checkpoint lines | compressed P2PKH(sha256(answer)) | answer X is correct, checkable by anyone holding X |
| 2 | 2020-04-03 ×2 *(saved)* | `3GSMG24T…` | "Good job, Neo!" | `148XH2…`, `13HGhj…` (the Phase-0 seed as a raw key) | the seed-as-raw-key doors |
| 3 | 2020-04-07 *(recorded)* | `3GSMG24T…` | none | `1NULY7…` (unidentified) | an answer key not yet identified |
| 4 | 2020-05-11 *(saved)* `a798905f…` | `3GSMG24T…` | "Halving" | 700 sat → **HALF** (prize key) | the instruction, delivered to half |
| 5 | lt 629998 *(saved)* `2aa9a4a9…` | **HALF**, 3 sigs verified; in2 spends #4's outpoint | none in-tx | 2.5 BTC → **BETTER HALF** + change → HALF | half pays better half, signing over #4 |
| 6 | 2021-07-18 *(recorded)* `a82052a2…` | `3GSMG24T…` | "neighbors, half and double" | Q−G, Q/2, 2Q, Q+G | nothing secret: all four derive from the public Q |
| 7 | lt 840003 *(saved)* `88cdb3cd…` | **HALF**, 3 sigs verified; in0 spends #5's change | none | 1.25 BTC → **BETTER HALF** + change → HALF | the second halving split |

**Pre-stated questions:**
- **Q1, do both halves co-sign one tx? NO.**
- **Q2, both halves plus an OP_RETURN in one tx? NO.**
- **Q3, does a half→better-half payment spend a memo-carrying tx? YES, exactly once.** The 2020 split
  spends `a798905f…:1`. The prize key's verified SIGHASH_ALL signature covers that outpoint, so it
  commits by hash to the `3GSMG24T…`-signed "Halving" memo.
- **Q4, has `17ucy1…` ever signed? NO.** It is receive-only: no pubkey, no signature.

**Verdict.** The topology is real, and it is Grigg-shaped at #4→#5: one key signs an instruction,
a second key executes it with a signature that embeds the instruction, and the counterparty is
credited. So yes, the halves *transact*. The "third entry" was already in the ledger (ticks 37,
61, 70, 72): the halving splits, one-directional. It certifies three things: the holder of the
prize key ran the halving rule at 629998 and 840003; that holder acknowledged `3GSMG24T…`'s memo;
better half only receives. It certifies **nothing about better half's key**, which has never acted.

In every checkpoint the counterparty's key is a public answer. If that convention extends to
`17ucy1…`, its key is f(an answer not yet found), so better half is the receipt for the final
answer. That is the existing two-keys/two-locks model (ticks 37, 47), and every candidate is
already checked against `17ucy1…` (addr_check). Nothing new to search. The MITM null is what this
topology predicts: the halves are related by a payment, not by arithmetic.

**Corrections.**
- Tick 63: the "Gavin" tx paid **seven** of the eight stamp addresses (no `1M5ypv…`, the 227-char
  key), plus `1JZBwa…` and change. Its signature, and the Neo-wallet tx's two (`148XH2…`), verify.
  Both are signed by public-knowledge keys and stay unauthenticated.
- #60314 (2026-03-04, "I only need to look at the address. If any of you reaches the next phase,
  the price is taken in no-time") is about watching the *prize* address for a solve, not about
  checkpoints.
- The creator's stated progress channel was off-chain: #896, solvers "send me proof of them passing
  the stages" on Telegram.

**Ijiri's Δ reading.** First differences of DBBI, VIC and R at every lag and both signs were already
searched at tick 55 (marker test, chance level). Δ² has no anchor and is not run.

**Topology-only lookups left for an unblocked machine** (three lookups; egress here is refused):
- the parents of `81d35929…:0` and `f28b0b68…:0`, the 2024 split's other inputs: did 2024 repeat the
  2020 memo→split pattern?
- the inputs of `547246e9…`, `3GSMG24T…`'s fan-out funder: does it trace to the 2019 funder `1EtbTv…`?
- the raw hex of `a82052a2…`: is its signer `3GSMG24T…`'s key `0205eaf7…`?

**State unchanged:** three locks byte-pinned; corpus exhausted; `1GSMG1…` unspent.

### Addendum to tick 88 (2026-09-26): Ijiri's causality + matrix reading; the Grigg mapping made explicit

Re-relayed with sources: the AAA In-Memoriam page for Ijiri; Grigg 2005 (iang.org); Jeffries 2017
(HackerNoon); Ijiri 1988, *Management Science* 34(2):160. It raises two points tick 88 did not cover.

1. **"causality + matrix + sumlist."** `causality` is already sourced: the phase-2 riddle points to
   the Merovingian's speech in *Reloaded* ("…the only real truth: causality"), and the answer is
   hash-confirmed. `matrixsumlist` is the soup's first a/b block. Ijiri's matrix form of double
   entry gives account totals as the row and column sums of a transaction matrix. That is the
   ledger's main reading of `matrixsumlist`, and it has been run to exhaustion:
   - campaign 14, about 16.6M trials;
   - campaign 30, the 11×11 row/column-sum pipeline;
   - the tick-8 column sums and their cold re-check;
   - campaign 26, the grid's row/column sums against all three addresses.

   No new operation follows.
2. **Grigg's three parts, by family** (from the tick-88 table):
   - **Checkpoints.** The solver's instruction is off-chain (Telegram, #896/#6497). The creator's
     single signature is the receipt, and it commits to the answer by hash (payee = H(answer)).
   - **The 2020 split** has the full two-signature form. 3GSMG24T signs the instruction; HALF
     executes as Grigg's "Ivan", signing over that instruction's outpoint; BETTER HALF is credited.
   - **The 2024 split** carries only the executor's signature. Its instruction is unknown (lookup 1).

   So the on-chain layer does two jobs: it registers accepted answers, each committed by hash, and
   it runs the halving schedule. Neither stores key material. The two receipts whose committed
   answers are unknown are `1NULY7…` and `17ucy1…`. Every candidate is already checked against both
   (addr_check), and campaign 26 checked every named object against them.

No compute. **State unchanged.**

### Tick 89 (2026-09-26): Grigg's papers page — no provenance; the Ricardian document-hash reading run once, null; the tick-88 lookups packaged as one command

Source: the user pasted the HTML of Ian Grigg's papers page (iang.org/papers) and asked for next
steps, executed.

**Provenance: none.** 35 distinctive terms from the page were searched in the creator's own words,
with 0 hits: Grigg, Ricardian, Systemics, financial cryptography, EOS, Corda, R3, CAcert, Gresham,
silver bullet, Pareto, Szabo, Mark Miller, smart/split contract, "two halves", Ivan, Sgantzos,
cellular automata, mandala, edge protocol, 7 layers, Baumol–Tobin, digital cash, Sum of All Chains,
Ricardian Triple, IAmSatoshi, CBDC, triple entry, receipt, and the rest of the list. The only repo
hits are this session's tick-88 text.

**What the page offers, mapped to GSMG:**

| page idea | GSMG status |
|---|---|
| the signed receipt is the transaction; 3 entries for 3 roles (2005, 2024) | tested at tick 88: the halves transact, in the 2020 two-signature form, and never co-sign |
| Ricardian contract: the hash of a human-readable document is its identifier | the one checkable structure; campaign 54 below, null |
| "two halves of a split contract" (Miller: a prose half and a code half) | a metaphor. The creator ties "better half" to `17ucy1…` (#3902). No operation |
| multiple-neighbourhood cellular automata | the 2021 "neighbors" memo is resolved (Q±G, Q/2, 2Q; ticks 52–53); rule-engine readings are closed (ticks 67–69) |
| "FC in 7 layers"; "The Sum of All Chains" | numerology and wordplay against the seven parts and `matrixsumlist`. No operation |
| SHA1 file hashes in the page's HTML comments | Grigg's own file-integrity records, not GSMG objects |

**campaign_54**, pre-registered in `intake/2026-09-26-ricardian/PREREG.md` and committed before the
run. Six whole, byte-exact documents:
- the three solved-stage plaintexts, re-derived by decryption and matched byte for byte to the saved
  files (648, 4090 and 2422 B);
- the phase-3.2 prose in front of P32T, in two boundary forms (2292 and 2288 B);
- the pinned soup (`d39d10b1…`, 2149 B).

Each went through the frozen path on raw bytes, the P32T freeze, the padding-independent scan and
addr_check. **96 decrypts, 0 PKCS#7-valid (0.4 expected by chance), 0 freeze passes, 0
padding-independent hits, 0 of 48 addresses.** The Ricardian reading is closed.

The phase-3.2 plaintext is not UTF-8: bytes 447–1985 are its EBCDIC cp1141 section, solved upstream.
The gate's helper takes str, so the run applies the same forms, KDFs, targets and check to the raw
bytes.

**The tick-88 lookups, packaged.** `harness/receipt_lookups.py` answers all three in one run:
- the parents of the 2024 split's other inputs;
- a walk up from `3GSMG24T…`'s funder `547246e9…`;
- the signer of the 2021 transaction.

It checks every fetched raw tx against its txid, caches it under `materials/chain/fetched/`, and
writes `materials/chain/RECEIPT_LOOKUPS.md`. `--selftest` passes offline: the decode controls, the
integrity check, and three positive controls on saved data. Applied to the 2020 split, lookup 1
recovers the "Halving" parent. The walk from the 2024 split reaches the prize key. The signer check
recognises `3GSMG24T…`'s key `0205eaf7…`.

The environment's network policy blocks the tool here (mempool.space and blockstream.info are
denied). Run it on an unblocked machine, or after allowing mempool.space.

**State unchanged:** three locks byte-pinned; corpus exhausted; `1GSMG1…` unspent.

### Tick 90 (2026-09-26): Grigg's Ricardian Triple read onto the master hint — it restates the standing recipe and entity model; HASHTHETEXT verified as the creator's one hash→identifier step; no new operation

User-relayed from another assistant; the source was not fetched here. Grigg 2015 ("The Sum of All
Chains", the Ricardian Triple):
- an object is code + text + parameters, packaged, then hashed into an identifier;
- "First Class Persons" hold keys, code, accounts and capital;
- entities on one axis and characteristics on the other make a table;
- "binary metrics mapped as a matrix and totalled up".

Proposed mapping onto GSMG:
- `yellowblueprimes` = parameters, `matrixsumlist` = code, `lastwordsbeforearchichoice` = text,
  `yinyang` = the pairing;
- the VIC sentence is an entity model, keyOf(Half) and keyOf(BetterHalf), not two pieces of one key.

Checked against the record:
1. **The typed reading is the standing recipe model** and comes from the creator's own hints (tick
   ~15, lines 350–356): `yinyang` is an output ("It's the next phase"); the master hint yields three
   inputs; the prime hint is the matrixsumlist hint; the soup grammar types each token by position.
   It is also the most-searched family, all null:
   - campaign 14 (~16.6M trials): prime-derived zero masks → matrix sums → wrapped with the other
     two components;
   - campaigns 17 and 19: `yellowblueprimes` as the prime subset and the 24-prime alignment;
   - campaign 30: the sums as indices into the last words;
   - campaigns 32 and 52: the last words;
   - the phase-0 grid's own row and column sums (`610876654997879` / `8108108736759668`, the
     "binary matrix totalled up"): campaigns 01–10, 28 and 29.
2. **The entity reading of the VIC sentence has been the standing model since tick 37**: the
   sentence "says what the cracked keys are for, two keys for two funded addresses; not a recipe".
   Tick 47 refined it into two complementary 80-byte locks (P32T ↔ half, salph_inner ↔ better half,
   → YINYANG); tick 61 added the halving split; tick 88 showed the halves transact and never
   co-sign. The additive MITM was run once, as a cheap structural check, and closed.
3. **What instantiated each entity** (the investigation the user proposed), from the record:
   - **HALF** = `1GSMG1…`, funded 2019-04-13 by `1EtbTv…` (5 BTC). Its address carries the
     six-character vanity prefix `1GSMG1`, about 1 in 6.6×10⁸ (tick 76). A hash of any fixed
     package lands on that prefix with that probability, so Half's key cannot "fall out" of
     H(package) unless the package contains a grinding nonce. It must be carried instead, e.g. as
     raw bytes inside an 80-byte lock (64 B = two 32-byte keys; ticks 31 and 37).
   - **BETTER HALF** = `17ucy1…`, funded 2020-05-11 by the prize key's split (signed over
     3GSMG24T's "Halving" instruction) and again in 2024. It has never signed and exposes no public
     key. It has no vanity prefix, so that argument does not constrain it; but no package is named
     for it, and every candidate is already checked against it.
4. **HASHTHETEXT, verified:** sha256("GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe")
   = `89727c598b9c…`, the SalPhaseIon URL. The creator's one solved "hash the text → identifier" step
   produced a *location* (the next page), not a key or a password. If the endgame reuses that
   grammar, H(package) would name the next object ("yinyang … is the next phase"). The domain has
   been parked since 2026-07-07. The wayback archive captured 12 hex paths: 10 are the SPA shell, one
   is the SalPhaseIon page, and one is a 2026 solver guess (`4f7a1e4e…`). No other hex page is on
   record.

**Verdict.** The Ricardian Triple reading independently converges on the ledger's model. It adds a
vocabulary, not an operation. No compute.

**State unchanged:** three locks byte-pinned; corpus exhausted; `1GSMG1…` unspent.

### Tick 91 (2026-09-26): the offline solver v2, validated against the checkout; two bugs and one regression fixed; verified nonce points added

The user uploaded `gsmg_offline_solver.py` 2026-09-26.1: 1,331 lines, 11 commands (doctor, audit,
selftest, test, gate, keytest, digest, components, opreturn, txscan, report), with a README and a
nonce-points template. It was installed as `harness/gsmg_offline_solver.py`, replacing tick 86's
version, and validated here.

**Found and fixed** (now 2026-09-26.2):
1. **The phase-3 solved control could never pass.** Its password was 220 characters, missing the
   7th FEN rank `1P2P2P/` (sha256 `ad029745…`, not `1a57c572…`), so `selftest` failed with exit 3
   on any checkout. It is restored to the verified 227-character string.
2. **Regression: key material was checked only on PKCS#7-valid decrypts.** Tick 86's version, and
   campaign 51's lesson, check `plaintext[0:32]`, `[32:64]` and literal 64-hex on every raw
   decrypt, because a right key can sit under a bad last block. This is restored. Proven by a
   planted control: a real miniAB decrypt with *invalid* padding, with its `[32:64]` registered as
   a synthetic address. The unfixed build misses it; the fixed build flags it.
3. **`txscan` exited 10 ("strong cryptographic hit") whenever the JSON merely mentioned the prize
   address.** It now exits 10 only on a nonce match.

Also found: the tick-86 claim that the run log is "gitignored" was wrong. `harness/.gitignore` held
only a comment. `offline_solver_attempts.jsonl` is now ignored at the repo root.

**Validated here, all green:**
- `doctor`; `audit` (three envelopes byte-pinned, Issue #108 J/s); `selftest` (NIST AES, secp256k1
  vectors, the P32T synthetic, and all three solved controls).
- `test` on a spent control: null. A repeat is refused. `gate` refuses creator line #8048 as
  corpus-present. `keytest` runs.
- `digest` of the image caption is `89727c598b9c…`, the SalPhaseIon URL (positive control).
- `components` places `yellowblueprimes` / `matrixsumlist` / `lastwordsbeforearchichoice` at
  offsets 0 / 16 / 29 of the creator's own decoded hint, and invents no serialization.
- `opreturn` gives an exact and a byte-reversed match on a verified R.x, and none on a random
  payload.
- `txscan` on the seven saved transactions decodes all five OP_RETURNs ("Halving", "Good job,
  Neo!" ×2, the Gavin quote, "Neo wallet …").

**New authenticated input.** `harness/nonce_points.py` recomputes the nonce point R = (z·s⁻¹)G +
(r·s⁻¹)Q of all six prize-key signatures (2020 and 2024 splits; R.x ≡ r for each, matching tick
72's r values) and writes `materials/chain/nonce_points_prize.json` for `opreturn`/`txscan`.
**No saved creator transaction has a 32-byte OP_RETURN**; the memos are 7–53 bytes of ASCII. So the
OP_RETURN-as-nonce idea has no in-repo target.

No candidates were tested beyond the controls. **State unchanged:** three locks byte-pinned; corpus
exhausted; `1GSMG1…` unspent.

### Addendum to tick 91 (2026-09-26): RIPEMD-160 portability fallback before the user's local run

Every address derivation called `hashlib.new('ripemd160')`, which some Python/OpenSSL 3 builds do
not provide. On such a machine, `selftest` and `receipt_lookups.py` would crash. `btc_addr.hash160`
now falls back to pycryptodome's RIPEMD160, which is already required through `aes_try`.
`receipt_topology`, `verify_halving_sigs` and `chain_flows` route through it. The standalone solver
carries the same fallback, becomes 2026-09-26.3, and `doctor` now reports which one is in use.

Verified in both modes, with `hashlib` refusing ripemd160 simulated: doctor, selftest, the
`receipt_lookups` self-test (with its positive controls) and the halving-signature check all pass.
`receipt_topology.py` output is byte-identical between the modes. No results change.

### Tick 92 (2026-09-26): the user's live receipt run; 3GSMG24T is funded by a 2-of-2 multisig; creator signatures verified offline; tooling extended (review pending)

**User-run results** (mempool.space, the tick-89 tool, on the user's machine; raws are not yet in the repo, so these are
user grade):
- **2024 split parents: NO repeat of the 2020 pattern.** `81d35929…:0` (535,500 sat) was paid by
  `bc1qey9rjg6zkpr47q6krhx58hecdn2jqkqnnwnavx`; `f28b0b68…:0` (666 sat) by `1GmTEC3Ygz3qZGHnfft9JBZdDNQkH2tGqo`. Neither is
  creator-signed and neither carries a memo. The user notes that `f28b0b68…` also paid `17ucy1…` 700 sat: a transaction that
  touches both halves is not provenance, since anyone can pay a public address. The signer is what matters.
- **The 2021 memo is creator speech.** `a82052a2…` ("GSMG.io neighbors, half and double", 4 × 5,000 sat to Q−G, Q/2, 2Q,
  Q+G) is signed by 3GSMG24T's key `0205eaf7…`.
- **3GSMG24T's ancestry:** `547246e9…` ← `0ba2a2e2…` ← `8ee72f46…` (all self-spends by 3GSMG24T) ← `1f8eb99e…`. The tool
  printed that last signer as "None (unknown)"; the old signer() did not recognise its script. The user decoded it: a
  **P2SH-P2WSH 2-of-2 multisig**, witness script `OP_2 028f2689…e5e1 03e4bf9b…2a22 OP_2 OP_CHECKMULTISIG`, address
  `37mh7EYetVKAesxqzv968sTYqSLF8dE6oD`. It spends `483451c5…:1` and pays 15,000 sat → 3GSMG24T plus 2,233,734 sat change
  back to itself. The user reports the fan-out as: 8ee7 splits 15,000 into 1,189 + 1,189 + 1,180 + 1,180 + 10,000; 0ba2
  splits 10,000 into 7,400 + 1,200 + 1,200; 5472 splits 7,400 into 1,106 + 1,200 × 5.

**Verified here, offline:**
- The two keys, in that order, as a 2-of-2 P2SH-P2WSH give exactly `37mh7EYetVKAesxqzv968sTYqSLF8dE6oD`; the reversed order
  gives a different address. Neither key, nor any of these txids, occurs anywhere in the repo.
- **The creator's P2SH-P2WPKH signatures now verify offline** (tick 70 had them as uncheckable without amounts). With the
  user's amounts for `547246e9…` (out 0 = 1,106 sat; outs 1, 2, 4, 5 = 1,200 sat), every 3GSMG24T signature on "Halving"
  (`a798905f…`, spending outs 2, 1, 0) and on both "Good job, Neo!" (`364de511…` out 5, `722fbf35…` out 4) verifies, and no
  other amount from 1,000 to 1,300 does. That confirms the user's figures for those five outputs and authenticates the three
  memos by signature.
- A consistency count, to be confirmed by the live fan-out: the three splits leave 12 spendable outputs of about 1.1–1.2k
  sat, and the ledger's known 2020 emissions consume exactly 12 (six checkpoints, one bare payment to `1NULY7…`, two "Good
  job, Neo!", and three for "Halving"). The 2021 memo's 20,000 sat needs a second inbound funding event.

**Tooling** (`harness/txscript.py`, new; `receipt_lookups.py`, extended; `receipt_topology.signer()` now delegates):
- **Script recognition:** p2pkh, p2pk, legacy p2sh m-of-n, p2wpkh, p2sh-p2wpkh, p2wsh / p2sh-p2wsh m-of-n (with pubkeys),
  and taproot flagged. Nested commitments are checked.
- **Offline ECDSA verification:** legacy SIGHASH_ALL, and BIP143 for all six sighash types with OP_CHECKMULTISIG ordering.
  It passes the official BIP143 vectors (fixture committed), including the 6-of-6 P2SH-P2WSH with six sighash types, and
  rejects amount + 1.
- **Lookups:** the ancestry walk now defaults to depth 12 and 200 fetches and prints multisig keys, block heights and
  signature status. New: the full 3GSMG24T fan-out from its address history (UTXO tree, recipient census against the
  ledger's receipts with UNKNOWN recipients flagged, fuel accounting with a books-balance check); full histories of the
  wallets that funded it; and the promotion rule, fixed in the tool before any run:
  - PROMOTE only if (i) the ancestry reaches a creator-trail signer, or (ii) a key matches authenticated GSMG material, or
    (iii) the history is narrowly GSMG-specific (≤ 10 transactions, ≥ 50% touching GSMG-labelled addresses);
  - otherwise it is operational funding infrastructure, and the branch closes.
  - Condition (ii) searches only `neo/materials` outside `materials/chain`, so our own notes cannot self-match. Nothing here
    becomes an AES candidate.

**State unchanged:** three locks byte-pinned; corpus exhausted; `1GSMG1…` unspent. An independent adversarial review of the
new tooling is in progress; its fixes follow in the next commit.

### Tick 93 (2026-09-26): the pre-registered live receipt pass — H1 (12 → 12) PASS; 37mh… closes as wallet infrastructure; the 2021 refill came from a single-use wallet; review fixes applied

**Procedure.** The pre-registration `intake/2026-09-26-fanout/PREREG.md` (sha256 `dc748d60…`) was committed in `51bc123`
before any live run. The user then made the single live acquisition on their machine with the wrapper
(`gsmg_esplora_offline.py sync`: mempool.space, depth 12, max-fetch 200, max-pages 20), running `receipt_lookups.py`
sha256 `23ae11a1…` (commit `e8730dd`). The sync made 479 requests, with `cache_complete` true, 0 transient failures and
0 unavailable items. An `offline` replay of the frozen cache then made 0 network requests with 0 cache misses. The
results below are user-grade: heights and dates are explorer-reported, and the raws sit in the user's frozen cache, not
yet in the repo.

The wrapper selftest had printed `False` on the user's machine. The cause was fixture isolation. In fixture mode,
`tx_hex()` fell through to the on-disk raw cache, which on that machine held the real raws, so the "unavailable"
negative control read real data. The defect lived only in the selftest's fixture mode; live and offline paths never use
it. Fixture mode is now hermetic: it reads neither the raw cache nor the JSON cache. A new control plants a valid raw
and a JSON response in a temporary cache and shows that fixture mode ignores them while a live-mode client reads them.

**H1 — PASS** (read off the report's UTXO tree against the PREREG criteria):
- **Root.** `1f8eb99e…:0`, 15,000 sat (height 622711, 2020-03-24, signed by `37mh…`).
- **Split `8ee72f46…`** into 1,189 / 1,189 / 1,180 / 1,180 / 10,000:
  - `117e2796…` "Right, this is causality" → `1Jqq37…`
  - `62dbb701…` "You are here because 227 chars were correct" → `1M5ypv…` (990 sat)
  - `2f64b875…` "phase3.2 pass OK" → `1K23RS…`
  - `bd1b5d81…` "are you sure?" → `1AD2wf…`
- **The 10,000 → split `0ba2a2e2…`** into 7,400 / 1,200 / 1,200:
  - `496ab2c7…` "part of the cipher" → `18Cchr…`
  - `3891dd14…` "do you beleive me you need it?" → `1GyT5W…`
- **The 7,400 → split `547246e9…`** into 1,106 + 5 × 1,200:
  - outputs 0, 1, 2 → `a798905f…` "Halving" (height 630001, 2020-05-11) → the prize, 700 sat
  - output 3 → `d6ff3da1…` → `1NULY7…`, 1,050 sat (2020-04-07, no memo)
  - output 4 → `722fbf35…` "Good job, Neo!" → `13HGhj…`
  - output 5 → `364de511…` "Good job, Neo!" → `148XH2…`

That is exactly 12 fuel outputs consumed by exactly the 10 emissions. No fuel output is unspent, nothing is spent
elsewhere, there is no other recipient, and every signature in the tree verified offline against its parent's amount.
**The treasury model is promoted: the creator funded 3GSMG24T once and pre-cut the message fuel.** The tool now computes
this verdict itself (`h1_check`, below); the user's offline replay of the frozen cache will print it. A synthetic history
of exactly this shape gives PASS. Two perturbations give FAIL with the difference: a missing emission leaves fuel unspent,
and an emission paying a nonstandard output adds another recipient.

**1NULY7… is now authenticated.** `d6ff3da1…`, signed by the 3GSMG24T key, is a signature-verified creator emission. That
closes the `1NULY7…` part of NEXT_PASS item 5.

**H2 — the 2021 refill came from a single-use wallet.** `e5db0968…` (height 691562, 2021-07-18) was paid by
`bc1q5rs27knqndl6ewkats0jv78222dzuw2g6h8mx5`. That wallet has 2 transactions in all: `4f4ae848…` (height 691550) brought
in 3,000,000 sat, and `e5db0968…` sent all of it, 21,048 sat of it to 3GSMG24T. One block later `a82052a2…` (height 691563,
signature verified) spent that 21,048 as 4 × 5,000 sat to Q−G, Q/2, 2Q and Q+G ("neighbors, half and double"). The
creator's last action on 3GSMG24T is therefore 2021-07-18.

**Promotion** (rule fixed before the run; topology only, and nothing becomes an AES candidate):
- **`37mh7EYetVKAesxqzv968sTYqSLF8dE6oD`: CLOSE, operational wallet infrastructure.**
  - (i) Its ancestry walk ran to its bound (12 transactions, a linear chain of its own self-spends) with no creator-trail
    signer.
  - (ii) No key reuse.
  - (iii) 4,332 transactions, 2020-03-20 → 2020-08-01, about 365.9 BTC through; one payee plus change per transaction,
    like a service's withdrawal wallet. One transaction touches GSMG, so the history is not narrow.
  - (iv) It signs one spent funding of 3GSMG24T. The 2021 refill came from `bc1q5rs27…`, so (iv) fails.
- **`bc1q5rs27…`: PROMOTE by (iii)** (2 transactions, 1 touching GSMG). Taken alone, (iii) is weak for a 2-transaction
  wallet: any single-use wallet that pays 3GSMG24T once meets it. The substantive fact is the timing: funded at 691550,
  paid 3GSMG24T at 691562, and 3GSMG24T's creator-signed emission followed at 691563. That is one operator's pipeline,
  so the wallet counts as creator operational infrastructure for the 2021 memo. Under the corrected tool its (i) reads
  NOT DETERMINED, because the 200-fetch cap stopped the walk. That does not change the verdict. The one open topology
  lookup it leaves is where the other ≈2.98M sat of `e5db0968…` went.

**3GSMG24T in full.** 30 transactions: 16 inbound, 3 splits, 11 emissions.
- Books: 57,176 sat inbound = 29,740 emitted + 21,128 unspent + 6,308 fees; the books balance.
- Census: 0 unknown recipients, and every expected receipt was seen.
- Every inbound payment after 2021 (14 deposits, 2024-12 → 2026-04) is signed by a third party or a public-knowledge puzzle key, never by 3GSMG24T, and sits unspent. Their
  memos: "BULLSHIT", "From Neo", "Neo wallet bc1qyw9q…", "Yes" ×2, "Its in good hands with Gavin and everyon.", "Happy late
  mothers day!", "I thought choice was an illusion?".
- The 2024 split parents are unchanged from tick 92: no creator signer and no memo.

**Tool review and fixes** (`txscript.py`, `receipt_lookups.py`, `chain_flows.script_info`). The adversarial review of the
tick-92 tooling (3 reviewers, then 39 independent verifiers) confirmed 38 findings and refuted 1 (a 520-byte P2SH push
limit that cannot arise on these data). None was triggered by the live data: the live report had 0 unavailable items,
2 funders, no co-signed transactions and no runestones in 3GSMG24T's history. All 38 are fixed.
- **Signatures now follow consensus.**
  - Segwit signatures must be strict DER (BIP66). A legacy signature that is not strict DER reports "valid only before
    BIP66".
  - Public keys must lie on the curve; before this, a crafted off-curve key could "verify" a keyless signature.
  - Hybrid keys are accepted.
  - Witness multisig must be exactly an empty dummy, then m signatures, then the script (NULLDUMMY and CLEANSTACK).
  - P2SH-wrapped witness programs must be pushed canonically.
  - A P2PK output spent with a (sig, pubkey) scriptSig is rejected.
  - Native segwit inputs are routed by the spent program. A taproot annex is handled, an empty signature no longer
    crashes, and uncompressed P2WPKH keys are recognised.
- **The run cannot crash on odd data.**
  - A Runestone (an OP_RETURN starting with a non-push opcode) used to kill the whole run.
  - One unreadable transaction no longer aborts a section.
  - Nonstandard outputs no longer crash the census.
  - Truncated HTTP bodies are retried.
- **The report no longer overclaims.**
  - An output spent by an unread transaction is no longer called UNSPENT; the fan-out uses the explorer's inputs.
  - Incomplete runs say so and never claim balanced books.
  - A co-signer's change is not a receipt, and co-signers' inputs enter the books.
  - Spends funded from outside the history have their own outputs followed.
  - The ancestry walk says which depths it read, and says NOT DETERMINED when the fetch cap or an unreadable transaction
    cut it.
  - A signature marked unchecked states the real reason.
  - Rule (ii) is printed as what it does: it searches `neo/materials`, excluding `materials/chain`.
- **Funders.**
  - Every funder is evaluated; a silent cap of 5 is gone.
  - Taproot and P2PK signers are identified from the spent output.
  - The promotion rule carries the pre-registered (iv), plus a NOT DETERMINED state: close only when all four conditions
    were evaluated.
  - A funder that is itself a creator-trail signer counts for (i).
- **H1 is computed by the tool,** exactly per the PREREG (`h1_check`: PASS / FAIL with the difference / UNDETERMINED only
  while data is missing).

**Replay safety.** Under the live run's conditions, the corrected code requests nothing the old code did not, so the
user's frozen cache replays offline without a second live pass. This was checked on a mock Esplora world shaped like the
live run: a paginated 37mh-like funder, a refill wallet whose ancestry hits the fetch cap, the 12 → 12 tree, and the 2021
emission.
- The old code synced it: 136 requests, 2 funders evaluated.
- The new code replayed that cache offline: 0 misses, 0 network requests, and H1 PASS end-to-end through the wrapper.
- The only report differences are the intended ones.
An independent adversarial verification of these fixes is running. Its confirmed findings, if any, follow in the next
commit, before master is advanced.

**Next (user):** `git pull`; `selftest`; then `offline` with the same bounds on the existing frozen cache (no new sync).
Then push the frozen cache (`materials/chain/fetched/` including `json/` and `esplora_http/`, plus `RECEIPT_LOOKUPS.md`,
`receipt_lookups.json` and the run manifest) to a branch. The result can then be replayed and every signature re-verified
here. The one open topology lookup is `e5db0968…`'s other output.

**State unchanged:** three locks byte-pinned; corpus exhausted; `1GSMG1…` unspent.
