# Endgame constraint sheet: operands, operators, representations

**Status: working document (2026-09-26). Nothing here is a solution.** It is the rule
sheet that any further endgame computation has to be written against. Every section has
been attacked once by an independent fact-check against the primary files; the corrections
from that pass are folded in.

Rule of the sheet: **an operator may not fire until its operand is a named object.** A
label decoded from the soup is a *name*, not a value. Every row carries its provenance
grade so that no weak item silently becomes a default operator. Prohibitions in the
"may not" columns are graded too: a creator statement, a recorded negative, or house policy.

Grades used below:

| grade | meaning |
|---|---|
| **AUTH** | creator statement, tagged HINT or CONFIRM in the creator transcript (`neo/materials/primary/CREATOR-LOG_transcript_445_messages.md`; the file's title says 445 messages, it holds 510 rows), cited by message id |
| **PRIMARY** | a raw capture or a verified decrypt in the authenticated archive (`neo/materials/primary/ARCHIVE-README.md`); not a statement, an artefact |
| **DECODED** | a label recovered from the SalPhaseIon soup by a reproducible decode; a *name*, not yet a value |
| **DERIVED** | computed from PRIMARY material by a stated, reproducible extraction |
| **READING** | an interpretation of an AUTH statement; the statement is authenticated, the interpretation is not |
| **LORE / BANTER / META** | creator text the archive itself tags as non-hint; usable only if it edits a string that is already named |
| **APRIL** | 2021-04-01 content; the creator later asked "do you know what usually happens on the first of April?" (#7529) |
| **USER** | supplied in conversation, absent from the authenticated archive |
| **NEGATIVE** | a recorded, reproducible test that came back empty (ledger tick / campaign cited) |
| **POLICY** | a rule of this sheet, not a fact about the puzzle |

Dates follow the transcript. For evening messages the transcript runs one day later than the
README's screenshot dates (12-02 vs 12-03, 12-25 vs 12-26, 07-12 vs 07-13); both refer to the
same message.

## 0. Hard oracles (unchanged)

| oracle | passes when | never counts |
|---|---|---|
| P32T = `inner96` (salt `b45a5e3d827593ca`, ct 80 B) | ≤79 bytes of clearly structured output (a hex key + newline fits exactly) | PKCS#7 pad 1–3 with garbage |
| `salph_inner` = `miniAB` (salt `3ab585348552415d`, ct 80 B) | same | same |
| Cosmic (salt `2d3f6fe06dc950e6`, ct 1328 B) | large coherent payload, or a 32-byte window deriving to `1GSMG1…` / `17ucy1…` | a `01` pad, printable fragments, locally reproduced hashes |
| prize address `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` (PRIMARY: printed on the genesis image; README) | derived address equals it | a `1GSMG` prefix (58⁴ ≈ 11M work, ledger tick 7) |
| `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` (README, second address) | address equals it | |
| `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` (**USER**; not in the archive; block explorers are egress-blocked here so its history is unverified) | address equals it | any near-match |

Measured false-positive rate for padding alone on these ciphertexts: 1 in 243 (ledger
tick 18). The gate is pad ≥ 4, or a ≥4-byte magic, or printable structure.

## 1. The four slots of the 2023-02-23 list

Source: #8446 (AUTH, HINT2023), binary that decodes bit-reversed then byte-reversed to
`yellowblueprimes matrixsumlist lastwordsbeforearchichoice yinyang` followed by
`wewontgiveawaythepassword / itsinfrontofyoureyesbutyourenotseeingit /
verylaststepisatruegiveawaypromised`. That order is source.

The seven-token frame (anchored on the Architect's PRIMARY line "seven intertwined
passwords") was exhausted in campaigns 01/03/05 with no hit (NEGATIVE). A separate
prior-session 1-byte-pad Cosmic "decrypt" of unknown provenance is noise per ledger tick 18;
its password was never recorded, so it is not attributed to any particular construction.
Neither frame is revived here.

| slot | status | what it may do | what it may not do |
|---|---|---|---|
| **A** `yellowblueprimes` | AUTH name (#8446) + AUTH poem (#1710 → #4105) + DERIVED 24-bit colour frame; **absent from the soup**; **no value rule** | be derived from the colour frame under a rule the source names (§2, §3) | be the English string as password (NEGATIVE: campaigns 01–05); be the 9/15 counts (no creator statement names them; #4105 under one reading points at 1/0 instead, ledger tick 19); be "any mask of the 24 bits, hashed" (NEGATIVE: campaigns 13/17/19; POLICY) |
| **B** `matrixsumlist` | AUTH name (#8446) and DECODED from the soup (bin1 a/b block → ASCII) | take one frozen representation from §5, table B | grow new sum variants (POLICY; NEGATIVE: campaigns 02/04/12/14) |
| **C** `lastwordsbeforearchichoice` | AUTH name (#8446) and DECODED from the soup (agda block, o=0 a=1…i=9 → int → hex → ASCII) | take one frozen value from §5, table C | be a standalone password (NEGATIVE: campaigns 01/05/14) |
| **D** `yinyang` | AUTH name (#8446); AUTH as a **phase / milestone reached after the current wall**: #9599 2023-08-06 HINT *"Probably the last hint: Once you hit a "ying yang", you'll be able to solve it the same day."*; #39224 2025-04-28 HINT *"when yingyang is reached, 2 hours max"*; #39237 2025-04-28 CONFIRM *"It's the next phase, but I await the day someone finally gets there."* (reply to "is yinyang found after decoding an AES ciphertext?") | be recognised when reached; work remains after it | be fed in as a password component — this is a READING of the three statements (the ledger's model correction 1), not their text; be assigned to `faed` (USER: stated in conversation only; no repo source names that pairing) |

## 2. Operand rows (objects that exist)

| object | grade | exact value / extraction | notes |
|---|---|---|---|
| genesis image, whole | PRIMARY (`puzzle.png` is byte-identical to the archive's `02_pages_raw` capture, sha256 `38125bbd…`) | 1048×1556: the 14×14 grid (top 1048 px), a red rule `#ED1C24`, the GSMG logo, the title, a QR code, the printed prize address | the QR decodes to `https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`; nothing else is encoded in the footer |
| genesis grid | PRIMARY (phase 0 decode reproduced) | 14×14 bits, `neo/materials/primary/matrix_grid_spiral_colors.json` | ccw spiral from top-left, down first; 196 bits = 24 bytes `gsmg.io/theseedisplanted` + 4 leftover bits `0000` (cells (6,6),(7,6),(7,7),(6,7)) |
| colour frame | DERIVED | 24 coloured cells at spiral indices `{7,15,…,191}` (0-based; every index ≡ 7 mod 8) = the LSB of each URL byte | polarity blue = 1, yellow = 0 is fixed by the grid file and the archive README ("colored cells = LSB of each char (blue=1, yellow=0)"), not by any creator line |
| colour sequence | DERIVED | `BBBBYBBBYYBBBBYBBYYBYYBY` (24 chars) | ledger tick 14 records a circulating 25-char variant with a spurious `F`; that is a ledger observation, not a primary fact |
| `f73d92` | DERIVED | the 24 colour bits, blue=1, spiral order, as hex: `111101110011110110010010` = `0xF73D92`; yellow-as-1 complement = `0x08C26D` | a 24-bit object, grounded; **not an AES key by itself** |
| Yellow / Blue "numbers" | AUTH statement (#1710 poem "Yellow has a number and so does Blue. Go back to the first puzzle piece"; #4102 CONFIRM "answer is there"; #4105 HINT **"First or zero"**) | the three words of #4105 are the whole source; its reply context is not preserved | three READINGs are live: (a) the numbers are 1 and 0; (b) "first [puzzle piece]" = "[phase] zero", the archive annotator's reading; (c) an answer to an index-base question ("count from first or from zero?") meaning either, which would only make sense for a base-invariant number such as a count. Under (a) and (b) the counts 15 / 9 are a measurement of the image, not what the hint points at (provenance pass, `creator_hint_provenance.md`); under (c) they would be licensed, but (c) has no preserved question behind it |
| colour numbers | DERIVED (new this session) | yellow `#FFF200` = 16773632 = 2⁹·181²; blue `#3F48CC` = 4147404 = 2²·3·37·9341; red rule `#ED1C24`; off-white `#FEFEFE` = 16711422 = 2·3·7·13·127·241 | a fourth, literal READING of "Yellow has a number and so does Blue": the colours' own codes. Never tested in this repo before campaign 27 (address oracle only; NEGATIVE). Any further use must still name the edit and the representation |
| `#FEFEFE` cell | DERIVED | grid (7,4) = spiral index 163 = byte 20 (`n` = 0x6E), bit offset 3 from the MSB (0-based), value 0 | unexplained marker |
| rabbit bitmap | DERIVED (new this session) | pixel art on a 15-px lattice, 14 × 13 lattice cells, 37 black pixels, drawn over grid cells (6,6),(6,7),(7,6),(7,7),(7,8),(7,9),(8,6); `neo/materials/rabbit_bitmap.txt` | the spiral's four unused end cells are (6,6),(7,6),(7,7),(6,7): the poem's "rabbit's nest" is literally the spiral's centre. Read as bits under every attested encoding (row/column order, both polarities, bit-reversed, byte-reversed) it gives no printable output (best 0.32); it is a drawing. 14 wide and 182 = 2 × 91 cells: recorded, not promoted |
| grid row sums | DERIVED | `6 10 8 7 6 6 5 4 9 9 7 8 7 9` → `610876654997879` (total 101) | table B, B1 |
| grid column sums | DERIVED | `8 10 8 10 8 7 3 6 7 5 9 6 6 8` → `8108108736759668` | table B, B2 |
| `dbbi` | PRIMARY (soup, first block) | 91 symbols over a–i, = 7×13; no `o` | no readable decode found; letter profile skewed toward `b`/`e` (Shannon ≈ 2.88 of 3.17 bits) |
| `faed` | PRIMARY (soup, third block) | 570 symbols over a–i = 6×91 + 24; remainder `ibibbibdcbahaidhfahiihic` | high-entropy by its base-81 pair profile (ledger tick 10); **parked** (no source-named operand) |
| VIC sentence | PRIMARY (phase 3.2 decrypt) | 91 letters `INCASEYOUMANAGETOCRACKTHIS…FUNDSTOLIVE` | |
| `dbbi ⊖ VIC` | DERIVED, null-tested | dbbi as a=1…i=9, VIC as A=1…Z=26, (dbbi − VIC) mod 26 rendered A=0 → `VOZIJBDTIQBRGVEOMZNBC · YOUWON · XCPKW…QTSGA` (21 + 6 + 64); the reverse direction contains no YOUWON | confirmed marker (0/200k null); terminal (ticks 15, 20); tail is not hex (24 distinct letters). The only creator text near a YOUWON-based claim is #70307 2026-09-01 "Pfff. Coincidence." (tagged CONFIRM, a category that covers confirming and denying), posted right after #70303 per the archive annotation; #70303 itself is not archived, so what he reacted to is unknown. The null test, not his reaction, is what supports the marker |
| primes ≤ 91 | arithmetic | 24 of them: `2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89` | 24 = number of colour cells (ledger tick 17); the aligned mask is enumerated and empty (campaign_19, NEGATIVE) |
| Architect text | PRIMARY (phase 3.2 decrypt) | Beaufort plaintext ending `…goodlucknevertheless ireallyhopeyouretheone ciaobellao` | see table C |
| `architect_span.txt` | PRIMARY, **unattributed** (in the archive with a verified hash, but the archive gives no origin or decoding note) | 501 letters, IC 1.10 | not to be keyed (ledger tick 13) |
| soup tail grammar | DECODED | raw soup strings `shabefourfirsthintisyourlastcommand` and `shabefanstoo`, around `z lastwordsbeforearchichoice z thispassword z … [miniA, base64 ending in z] enter [miniB]` | the glosses "sha b4 first hint is your last command" / "sha b4 answers too" are READINGs (the second also parses "sha be fans too"); the `z` before the a/b block is a base64 payload character (the 64-char run decodes to `Salted__` + salt `3ab585348552415d`) |
| pinned convention | DERIVED, empirical (3 positive controls) | passphrase = lowercase sha256hex(answer), EVP_BytesToKey(SHA-256), aes-256-cbc | the creator's habit, not a guess |

## 3. Operator rows (edits, selectors) and what each is missing

| hint | grade | cites | what it is | operand it names | what is still missing |
|---|---|---|---|---|---|
| primes | **AUTH** | #5966 2021-03-01 HINT "You are at the prime part already???" (reply to a solver asking which of 2/3/5/7), made a hint by #5969 META "Oh wait, shouldn't have said that. That might have been a hint"; #6509 2021-03-14 META "I gave an unforseen hint already" in reply to a request for a matrixsumlist hint (the link to #5966 and the tie to `matrixsumlist` are the archive annotator's, not the creator's words); #8000 2021-12-26 HINT "definitely an aspect which is required to proceed"; #8330 2023-01-09 HINT "at least prime number is very important to get any further" | AUTH content: **primes are required**. The selector reading (keep or index a prime-numbered subset of a named object) is a READING | none named; scope is SalPhaseIon (tags SAL); the tie to slot B rests on the META reply context of #6509 | the object it indexes; whether it applies to slot A at all beyond the compound word in #8446 |
| "some characters need to be zeroed out" | **AUTH** | #8000 2021-12-26 HINT; the transcript row is truncated at "some characters need t", the verbatim sentence "Furthermore, along the way, some characters need to be 'zeroed out'.." is in `hints/2021-12-25-hint.png` | a **deletion / zeroing** edit on characters | none named ("along the way") | the string it edits and which characters |
| "another door" (existence) | **AUTH** | #1710 2020-01-14 HINT poem ("it might have shown you only one door, beware that the rabbits nest may contain a whole lot more"); #3923 2020-05-11 HINT "what you'll find after opening the 2nd door"; #4590 2020-08-02 META "nobody managed to find the extra door"; #4688 2020-08-12 HINT "hints stating the path pretty obvious"; #7914 2021-12-03 HINT "There is Another D O O R" (the four letters on separate lines in `hints/2021-12-02-another-door-hint.png`); #8000 HINT "still a thing" | a second, unfound entry point that the 2020 poem describes | "go back to the first puzzle piece" = the genesis image (P0); "the rabbits nest" = the centre cells the rabbit is drawn in (§2) | where on the genesis image |
| `{1},{4},{21}` | **APRIL** (archive tag HINT, DOOR; downgraded by this sheet because of #7529) | #6884 2021-04-01 "another door might be found on {1 },{4} ,{21}"; #6913 same day LORE "R=18 A=1 B=2 could also be 21 or 1812 bit" (18-1-2-bit = **RAB-bit**, a rabbit joke, READING); #7529 2021-04-18 META "do you know what usually happens on the first of April?"; #70307 2026-09-01 CONFIRM "Pfff. Coincidence.", an ambiguous two-word reaction whose target (#70303, a solver's YOUWON/VIC/{1,4,21} claim per the annotation) is not archived | at most a *where* | none | not an index into every buffer; no creator statement confirms or denies any {1,4,21} construction |
| "1 microstep" | AUTH (HINT) | #32579 2024-11-29 "if you guys got 1 microstep further, the puzzle will likely be solved the same day" | a size statement: the wall is one small step | none | |
| ASCII 127 (DEL) | **LORE** | #32613 2024-11-29, reply to "what character do I have to imagine myself as?" — a character joke | at most a *what* (delete) | none | allowed only after the string it edits is named |
| "last number of pi" | **BANTER** | #32671 2024-11-29, reply to "it's an infinite key" | none | none | already exhaustively closed as key/IV material (ledger tick 22, NEGATIVE) |
| `shabef` | DECODED (soup) + pinned convention | raw `shabefourfirsthintisyourlastcommand`, `shabefanstoo` | READING: the combine step uses SHA-256 before AES; consistent with the pinned convention | | does not say *what* is hashed |
| "in front of your eyes but you're not seeing it" | AUTH (HINT) | #8446 | the password material is already visible | | which visible object |
| "regular Bitcoin private key" | AUTH (CONFIRM) | #20223 2024-01-26 | the final object is a plain private key | | |
| "a private key, some 'obscure' intel" | AUTH (HINT) | #24627 2024-04-20 | lists intel alongside the key among the prizes; whether both come from one solve is not stated | | |
| "close friends have the best chance … NOTE: that is a hint" | AUTH (HINT, tag KEY) | #66573 + #66574 2026-07-13 (README screenshot dated 07-12): "My close friends have the best chance of solving it (a few tried). But they don't have the skills some of you do." / "NOTE: that is a hint." | the last step needs something the creator's friends know plus solver skill | | what the friends know |
| "Some already found it. And understood not to risk it" | AUTH (CONFIRM) | #66600 2026-07-13 | claims some have found "it" (the secret, per the reply context #66592/#66593) and not acted | | |
| "No clues to be found in those typos" | META | #1806 2020-02-22 for the quote; #898, #871, #3345 as ledger tick 13 context | typo-mining is ruled out at source (ledger tick 13, with a positive control) | | |

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
| mod-26 letter subtraction | `dbbi ⊖ VIC` (DERIVED, null-tested; not creator-attested) |

Any proposed representation outside this table is a new assumption and must be labelled as one.

## 5. Frozen candidate sets for B and C

### Table B — `matrixsumlist` (pick one row; do not add rows)

| id | value | why it is allowed |
|---|---|---|
| B0 | literal `matrixsumlist` | the label may be the value |
| B1 | `610876654997879` | row sums of the genesis grid, 14 numbers concatenated |
| B2 | `8108108736759668` | column sums of the genesis grid |
| B3 | `610876654997879` ‖ `8108108736759668` | rows then columns, no separator (one separator choice, frozen) |

Note: B1–B3 were tested as passwords in campaigns 02/04 (NEGATIVE). Their role here is as a
*slot value* in a combine, which is not the same test.

### Table C — `lastwordsbeforearchichoice` (pick one row; do not add rows)

The puzzle's Architect text is a cut of the film monologue that stops **before** the two-door
choice: the last words of the puzzle text are `…good luck nevertheless i really hope youre
the one ciao bella o`. So the choice boundary lies *after* the end of the puzzle text.

| id | value | why it is allowed |
|---|---|---|
| C0 | literal `lastwordsbeforearchichoice` | the label may be the value |
| C1 | `ireallyhopeyouretheone` | the last Architect sentence in the puzzle text before the film's choice would begin |
| C2 | `hopeitisthequintessentialhumandelusionsimultaneouslythesourceofyourgreateststrengthandyourgreatestweakness` | #3390 2020-04-08, the creator quoted it verbatim — but he added #3391 "not a hint btw, just fooling around", and in the film this line comes *after* Neo's choice (film knowledge, not repo material); lowest-graded row |
| C3 | `ciaobellao` | the literal final token of the puzzle text; it is before the choice boundary because the choice is not in the text |

Each C row has been tried as a standalone password (campaigns 01/05/14, NEGATIVE). Same
remark as for B.

## 6. What is missing, per slot

| slot | missing |
|---|---|
| A | a named object derived from the colour frame under a rule the source names, recognisable **before** AES (a length, a checksum, an address oracle, or an attested representation); primes and zeroing only if the SAL-scoped prime hint is shown to apply to this slot |
| B | nothing more can be frozen; one row of table B |
| C | nothing more can be frozen; one row of table C |
| D | a milestone, not an input; nothing to supply |
| combine | not to be attacked until A is an object: then `A‖B‖C` (three inputs, per the ledger's model correction), one documented separator, `sha256(A‖B‖C)`, sha256hex as EVP password, XOR of the three digests as one pre-registered row |

For slot A the only AUTH material is the name (#8446), the poem (#1710) and "First or
zero" (#4105). Primes and zeroing are attested edits whose operand is unnamed and which the
archive's annotation ties to `matrixsumlist` (SAL scope); whether they apply to A at all is
open. The representation family is attested (§4). What is still missing is the *rule* that
turns the colour frame into a value that can be recognised without decrypting anything.

The question on the page is therefore: **which official hint names the operand, which names
the edit, which names the representation, and which of the three is still missing.**
