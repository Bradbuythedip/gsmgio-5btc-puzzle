# Endgame constraint sheet: operands, operators, representations

**Status: working document (2026-09-25). Nothing here is a solution.** It is the rule
sheet that any further endgame computation has to be written against.

Rule of the sheet: **an operator may not fire until its operand is a named object.** A
label decoded from the soup is a *name*, not a value. Every row carries its provenance
grade so that no weak item silently becomes a default operator.

Grades used below:

| grade | meaning |
|---|---|
| **AUTH** | creator statement, tagged HINT or CONFIRM in the 445-message transcript (`neo/materials/primary/CREATOR-LOG_transcript_445_messages.md`), cited by message id |
| **DECODED** | a label recovered from the SalPhaseIon soup by a reproducible decode; a *name*, not yet a value |
| **DERIVED** | computed from authenticated material by a stated, reproducible extraction |
| **LORE / BANTER / META** | creator text the archive itself tags as non-hint; usable only if it edits a string that is already named |
| **APRIL** | 2021-04-01 content; the creator later asked "do you know what usually happens on the first of April?" (#7529) |
| **USER** | supplied in conversation, absent from the authenticated archive |
| **COMMUNITY** | solver-derived; not an instruction |

## 0. Hard oracles (unchanged)

| oracle | passes when | never counts |
|---|---|---|
| P32T = `inner96` (salt `b45a5e3d827593ca`, ct 80 B) | ≤79 bytes of clearly structured output (a hex key + newline fits exactly) | PKCS#7 pad 1–3 with garbage |
| `salph_inner` = `miniAB` (salt `3ab585348552415d`, ct 80 B) | same | same |
| Cosmic (salt `2d3f6fe06dc950e6`, ct 1328 B) | large coherent payload, or a 32-byte window deriving to `1GSMG1…` / `17ucy1…` | a `01` pad, printable fragments, locally reproduced hashes |
| prize address `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` (AUTH, #—, README) | derived address equals it | a `1GSMG` prefix (58⁴ ≈ 11M work, see ledger tick 7) |
| `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` (README, second address) | address equals it | |
| `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` (**USER**; not in the archive; block explorers are egress-blocked here so its history is unverified) | address equals it | any near-match |

Measured false-positive rate for padding alone on these ciphertexts: 1 in 243 (ledger
tick 18). The gate is pad ≥ 4, or a ≥4-byte magic, or printable structure.

## 1. The four slots of the 2023-02-23 list

Source: #8446 (AUTH, HINT2023), binary that decodes bit-reversed then byte-reversed to
`yellowblueprimes matrixsumlist lastwordsbeforearchichoice yinyang` followed by
`wewontgiveawaythepassword / itsinfrontofyoureyesbutyourenotseeingit /
verylaststepisatruegiveawaypromised`. That order is source. Splitting it into seven parts
or inserting `enter` / `thispassword` / `yourlastcommand` is interpretation and already
produced the 1-byte-pad Cosmic artefact; not revived.

| slot | status | what it may do | what it may not do |
|---|---|---|---|
| **A** `yellowblueprimes` | **label only** (AUTH as a name, #8446) | must be *computed* from the genesis colour frame plus primes (rows 2, 3) | not the English string; not the 9/15 counts (no creator warrant, #4105); not "any mask of the 24 bits, hashed" |
| **B** `matrixsumlist` | **DECODED label** (bin1 a/b block → ASCII) | one frozen representation from §5, table B | not a licence to invent new sums |
| **C** `lastwordsbeforearchichoice` | **DECODED label** (agda block, o=0 a=1…i=9 → int → hex → ASCII) | one frozen value from §5, table C | not a standalone Cosmic password |
| **D** `yinyang` | **output / checkpoint** (#9599 "once you hit a ying yang, same day"; #39224 "when yingyang is reached, 2 hours max"; #39237 "it's the next phase" in reply to "is yinyang found after decoding an AES ciphertext?") | recognise it when it appears | not an input; not `faed` by default (COMMUNITY assignment) |

## 2. Operand rows (objects that exist)

| object | grade | exact value / extraction | notes |
|---|---|---|---|
| genesis grid | AUTH (phase 0 solved) | 14×14 bits, `neo/materials/primary/matrix_grid_spiral_colors.json` | ccw spiral from top-left, down first; 196 bits = 24 bytes `gsmg.io/theseedisplanted` + 4 leftover bits `0000` |
| colour frame | DERIVED | 24 coloured cells at spiral indices `{7,15,…,191}` (0-based; every index ≡ 7 mod 8) = the LSB of each URL byte | blue = 1, yellow = 0 (P0 decode; #4105 "First or zero") |
| colour sequence | DERIVED | `BBBBYBBBYYBBBBYBBYYBYYBY` (24 chars; the circulating 25-char form with an `F` is a typo) | |
| `f73d92` | DERIVED | the 24 colour bits, blue=1, spiral order, as hex: `111101110011110110010010` = `0xF73D92`; yellow-as-1 complement = `0x08C26D` | a 24-bit object, grounded; **not an AES key by itself** |
| Yellow / Blue "numbers" | AUTH (#1710 poem) → answered by #4105 **"First or zero"** | **1 and 0** | counts 15 / 9 are a measurement of the image, not what the hint points at (provenance pass, `creator_hint_provenance.md`) |
| `#FEFEFE` cell | DERIVED | grid (7,4) = spiral index 163 = byte 20 (`n`), bit 3 | unexplained marker |
| genesis image, whole | AUTH (`puzzle.png` is byte-identical to the archive's `02_pages_raw` capture, sha256 `38125bbd…`) | 1048×1556: the 14×14 grid (top 1048 px), a red rule `#ED1C24`, the GSMG logo, the title, a QR code, the printed prize address | the QR decodes to `https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`; nothing else is encoded in the footer |
| rabbit bitmap | DERIVED (new this session) | pixel art on a 15-px lattice, 14 × 13 lattice cells, 37 black pixels, drawn over grid cells (6,6),(6,7),(7,6),(7,7),(7,8),(7,9),(8,6); `neo/materials/rabbit_bitmap.txt` | the spiral's four unused end cells are (6,6),(7,6),(7,7),(6,7): the poem's "rabbit's nest" is literally the spiral's centre. Read as bits under every attested encoding (row/column order, both polarities, bit-reversed, byte-reversed) it gives no printable output (best 0.32); it is a drawing. 14 wide and 182 = 2 × 91 cells: recorded, not promoted |
| colour numbers | DERIVED (new this session) | yellow `#FFF200` = 16773632 = 2⁹·181²; blue `#3F48CC` = 4147404 = 2²·3·37·9341; red rule `#ED1C24`; off-white `#FEFEFE` = 16711422 = 2·3·7·13·127·241 | a second, literal reading of "Yellow has a number and so does Blue": the colours' own codes, in front of your eyes. Never tested in this repo before campaign 27. Any use must still name the edit and the representation |
| grid row sums | DERIVED | `6 10 8 7 6 6 5 4 9 9 7 8 7 9` → `610876654997879` | table B, B1 |
| grid column sums | DERIVED | `8 10 8 10 8 7 3 6 7 5 9 6 6 8` → `8108108736759668` | table B, B2 |
| `dbbi` | AUTH (soup, first block) | 91 symbols over a–i, = 7×13; no `o` | high-entropy (ledger tick 10) |
| `faed` | AUTH (soup, third block) | 570 symbols over a–i = 6×91 + 24; remainder `ibibbibdcbahaidhfahiihic` | high-entropy; **parked** (no source-named operand) |
| VIC sentence | AUTH (phase 3.2 solved) | 91 letters `INCASEYOUMANAGETOCRACKTHIS…FUNDSTOLIVE` | |
| `dbbi ⊖ VIC` | DERIVED, null-tested | `VOZIJBDTIQBRGVEOMZNBC · YOUWON · XCPKW…QTSGA` (21 + 6 + 64) | confirmed marker; terminal (ticks 15, 20); tail is not hex (24 distinct letters) |
| primes ≤ 91 | arithmetic | 24 of them: `2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89` | 24 = number of colour cells (ledger tick 17); the aligned mask is enumerated and empty (campaign_19) |
| Architect text | AUTH (phase 3.2 solved) | Beaufort plaintext ending `…goodlucknevertheless ireallyhopeyouretheone ciaobellao` | see table C |
| `architect_span.txt` | AUTH (primary archive) | 501 letters, IC 1.10 | unattributed; not to be keyed |
| soup tail grammar | DECODED | `… z lastwordsbeforearchichoice z thispassword z shabefourfirsthintisyourlastcommand [miniA] z? enter [miniB] shabefanstoo` | "sha b4 first hint is your last command", "sha b4 answers too" |
| pinned convention | AUTH (3 positive controls) | passphrase = lowercase sha256hex(answer), EVP_BytesToKey(SHA-256), aes-256-cbc | the creator's habit, not a guess |

## 3. Operator rows (edits, selectors) and what each is missing

| hint | grade | cites | what it is | operand it names | what is still missing |
|---|---|---|---|---|---|
| primes | **AUTH** | #5966 2021-03-01 "You are at the prime part already???" (reply to a solver asking which of 2/3/5/7); #6509 2021-03-14 matrixsumlist hint = "I gave an unforeseen hint already" (→ #5966); #8000 2021-12-26 "definitely an aspect which is required to proceed"; #8330 2023-01-09 "at least prime number is very important to get any further" | a **selector**: keep or index a prime-numbered subset of an already-named object | none named; scope is SalPhaseIon (tags SAL) and it is tied to `matrixsumlist` | the object it indexes |
| "some characters need to be zeroed out" | **AUTH** | #8000 2021-12-26, "furthermore, along the way, some characters need to be 'zeroed out'" | a **deletion / zeroing** edit on characters | none named ("along the way") | the string it edits and which characters |
| "another door" (existence) | **AUTH** | #1710 2020-01-14 poem ("it might have shown you only one door"); #3923 2020-05-11 "what you'll find after opening the 2nd door"; #4590 2020-08-02 "nobody managed to find the extra door"; #4688 2020-08-12 "hints stating the path pretty obvious"; #7914 2021-12-03 acrostic THERE IS ANOTHER DOOR; #8000 "still a thing" | a second, unfound entry point that the 2020 poem describes | "go back to the first puzzle piece" = the genesis image (P0) | where on the genesis image |
| `{1},{4},{21}` | **APRIL** | #6884 2021-04-01; #6913 same day "R=18 A=1 B=2 could also be 21 or 1812 bit" (18-1-2-bit = **RAB-bit**, a rabbit joke); #7529 2021-04-18 "do you know what usually happens on the first of April?"; #70307 2026-09-01 "Pfff. Coincidence." in reply to a YOUWON/VIC {1,4,21} numerology claim | at most a *where* | none | not an index into every buffer; the creator dismissed the one {1,4,21} construction put to him |
| "1 microstep" | AUTH (META) | #32579 2024-11-29 "if you guys got 1 microstep further, the puzzle will likely be solved the same day" | a size statement: the wall is one small step | none | |
| ASCII 127 (DEL) | **LORE** | #32613 2024-11-29, reply to "what character do I have to imagine myself as?" — a character joke | at most a *what* (delete) | none | allowed only after the string it edits is named |
| "last number of pi" | **BANTER** | #32671 2024-11-29, reply to "it's an infinite key" | none | none | already exhaustively closed as key/IV material (ledger tick 22) |
| `shabef` | **AUTH** (soup) + pinned convention | "sha b4 first hint is your last command", "sha b4 answers too" | the combine step uses SHA-256 before AES | | does not say *what* is hashed |
| "in front of your eyes but you're not seeing it" | AUTH | #8446 | the password material is already visible | | which visible object |
| "regular Bitcoin private key" | AUTH | #20223 2024-01-26 | the final object is a plain private key | | |
| "a private key, some obscure intel" | AUTH | #24627 2024-04-20 | the solve contains more than the key | | |
| "close friends have the best chance … NOTE: that is a hint" | AUTH | 2026-07-12 | the last step is personal/biographical rather than technical | | |
| "Some already found it. And understood not to risk it" | CONFIRM | #66600 2026-07-13 | claims the endgame has been reached by someone | | |
| "No clues to be found in those typos" | AUTH | #1806, #898 | typo-mining is ruled out at source (ticks 13) | | |

## 4. Representation rows (encodings the creator has actually used)

| encoding | where it is attested |
|---|---|
| bits → 8-bit ASCII, spiral order | phase 0 |
| **bit-reversed then byte-reversed** binary | #8446 (the master hint itself) |
| a/b → 0/1 → ASCII | soup bin1 (`matrixsumlist`), bin2 (`enter`) |
| letters o=0, a=1 … i=9 → decimal digits → integer → hex → ASCII | soup agda, cfob |
| sha256hex of the human answer, then EVP | phases 2, 3, 3.2 |
| EBCDIC cp1141, Beaufort (`thematrixhasyou`), VIC (digits 1,4; `fubcdora/lethingkymvpszjqwx.`) | phase 3.2 |
| hex-encoded, reversed genesis coinbase string | phase 2.2 part 6 |
| mod-26 letter subtraction | `dbbi ⊖ VIC` (derived, null-tested) |

Any proposed representation outside this table is a new assumption and must be labelled as one.

## 5. Frozen candidate sets for B and C

### Table B — `matrixsumlist` (pick one row; do not add rows)

| id | value | why it is allowed |
|---|---|---|
| B0 | literal `matrixsumlist` | the label may be the value |
| B1 | `610876654997879` | row sums of the genesis grid, 14 numbers concatenated |
| B2 | `8108108736759668` | column sums of the genesis grid |
| B3 | `610876654997879` ‖ `8108108736759668` | rows then columns, no separator (one separator choice, frozen) |

Note: B1–B3 were tested as passwords in campaigns 02/04 (negative). Their role here is as a
*slot value* in a four-slot combine, which is not the same test.

### Table C — `lastwordsbeforearchichoice` (pick one row; do not add rows)

The puzzle's Architect text is a cut of the film monologue that stops **before** the two-door
choice: the last words of the puzzle text are `…good luck nevertheless i really hope youre
the one ciao bella o`. So the choice boundary lies *after* the end of the puzzle text.

| id | value | why it is allowed |
|---|---|---|
| C0 | literal `lastwordsbeforearchichoice` | the label may be the value |
| C1 | `ireallyhopeyouretheone` | the last Architect sentence in the puzzle text before the film's choice would begin |
| C2 | `hopeitisthequintessentialhumandelusionsimultaneouslythesourceofyourgreateststrengthandyourgreatestweakness` | #3390 2020-04-08, the creator quoted it verbatim — but he added #3391 "not a hint btw, just fooling around", and in the film this line comes *after* Neo's choice; lowest-graded row |
| C3 | `ciaobellao` | the literal final token of the puzzle text; it is before the choice boundary because the choice is not in the text |

Each C row has been tried as a standalone password (campaigns 01/05/14, negative). Same
remark as for B.

## 6. What is missing, per slot

| slot | missing |
|---|---|
| A | a named numeric object computed from the colour frame + primes that is recognisable **before** AES (matches a length, a checksum, an address oracle, or an attested representation) |
| B | nothing more can be frozen; one row of table B |
| C | nothing more can be frozen; one row of table C |
| D | it is the output; nothing to supply |
| combine | not to be attacked until A is an object: then `A‖B‖C‖D`, one documented separator, `sha256(A‖B‖C‖D)`, sha256hex as EVP password, XOR of the four digests as one pre-registered row |

The question on the page is therefore: **which official hint names the operand, which names
the edit, which names the representation, and which of the three is still missing.** For
slot A: the edit is named (zeroing, primes), the representation family is attested (§4), the
operand is the colour frame — and what is still missing is the *rule* that turns those into a
value that can be recognised without decrypting anything.
