# Unverified Solutions

This folder contains a list of currently unverified, or unverifiable, solutions to sections of the puzzle. If you have one, please add a new file to this repository and then link it in this readme. Maybe we can keep track of approaches that don't work, or that have potential. Please use .md, .ipynb, and/or a separate subfolder.


| Solution Name | Phase | Link | Description |
| --------------|-------|------| ------------|
| My Solution   | Phase 3.2 | [FAKE AES ATTEMPT #1](./sample_3.2_attempt_1.md) | I attempted to brute force the AES using the matrix movie's script |
| 1141 Coincidence | Phase 3.2 | [1141 Slice](./phase3.2_1141.md)| coincidence |
| Yellow and Blue counts | Phase 0 | [Yellow/Blue counts](./phase0_yellow_blue_counts.md) | the 9 and 15 counts restate the URL's low bits, so they are not a new input |
| fefefe parity | Phase 0 | [fefefe is 101 010](./phase0_fefefe_parity.md) | hex digit parity gives 42; explains a solver remark, and the 104 half does not hold |
| XOR of seven token hashes | SalPhaseIon / Cosmic | [XOR token hashes](./salphaseion_xor_token_hashes.md) | the XOR value reproduces, but it does not decrypt Cosmic and no XOR candidate hits the prize address |
| KEY in 7x13 column sums | SalPhaseIon | [7x13 KEY columns](./salphaseion_7x13_key_columns.md) | block shapes (7 matrices of 7x13 + 24) are real and kept; the KEY reading is mask-overfitting |
| Endgame AES password search | Phase 3.2 / SalPhaseIon | [Password exclusions](./endgame_aes_password_search.md) | pinned decrypt convention + ~14.8M excluded candidates across the four outstanding locks |
| SalPhaseIon soup grammar | SalPhaseIon | [Soup grammar](./salphaseion_soup_grammar.md) | primary-material reading: yinyang is an output not an input, the prime hint is the matrixsumlist hint, dbbi/faed are high-entropy data |
| DBBI minus VIC = YOUWON | SalPhaseIon | [DBBI YOUWON](./salphaseion_dbbi_youwon.md) | reproduces, 0/200k in null tests, leaves exactly 64 chars; a planted confirmation marker, not key material |
| OP_RETURN script VM | Chain records | [OP_RETURN VM](./op_return_script_vm.md) | the 'exactly one byte short' recursion is forced whenever payload length equals its first byte; closed on logic |
| Single-t mutation family | Endgame | [Single-t mutation](./single_t_mutation.md) | control passes, 716 variants / 150k trials empty; creator states typos contain no clues |
| yellowblueprimes grid indices | Phase 0 | [Grid indices](./yellowblueprimes_grid_indices.md) | exact authenticated spiral index lists published; prime readings closed; corrects a circulating 25-char colour string |
| Why false decrypts recur | Method | [False decrypts](./why_false_decrypts_recur.md) | measured: 1 in 243 random keys gives valid PKCS#7; the IV is KDF-emitted not chosen; our gate had 0 false positives in 300k |
| Creator hint provenance | Method | [Hint provenance](./creator_hint_provenance.md) | only 10 authenticated statements in 7 years; yellow/blue is P0-scoped and answered in 2020; the 9/15 counts have no creator warrant |
| Salted header proves a password | Method | [Salted header](./salted_header_proves_password.md) | key+IV mode writes no header; all three locks carry Salted__ and a salt, so a password provably exists |
| Bitcoin v0.1 glitch relevance | Method | [Source glitch](./bitcoin_source_glitch.md) | creator never mentions source/bugs/entropy; the one Bitcoin borrowing was the genesis coinbase string, not a behaviour |
| Padding oracle attack does not apply | Method | [Padding oracle](./padding_oracle_does_not_apply.md) | no interactive oracle exists, it recovers plaintext not a key, and it would need the secret to attack the secret |
| Authenticated 32-byte inventory | Endgame | [32-byte inventory](./authenticated_32byte_inventory.md) | verified EVP keys/IVs for all three solved stages x named IVs x both 80-byte locks: 234 decrypts, 0 accepted |
| Endgame constraint sheet | Endgame | [Constraint sheet](./endgame_constraint_sheet.md) | operands, operators and representations per official hint with provenance grades, fact-checked against the primary files; frozen tables for matrixsumlist and lastwordsbeforearchichoice; the genesis image inventory (QR resolves to the prize link, rabbit bitmap, colour codes) |
