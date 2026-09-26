# Drive working files (2026-04/05): derived artifacts, not primary

A user-supplied Google Drive export (`drive-download-20260925T014609Z-1-001.zip`, 9 files,
file dates 2026-04-27 to 2026-05-09). These are someone's working files, not creator
material. Four are byte-identical copies of material already in the repo and are not
duplicated here. The five derived files are kept so nobody has to chase them again.

## Copies of known material (not committed again)

| file | sha256 | identical to |
|---|---|---|
| `P32_VERIFIED.bin` | `b82afeb8…8a34` | `neo/materials/phase32_plaintext_outer.txt` (the 2422-byte phase-3.2 plaintext) |
| `cosmic_duality_blob.bin` | `b1895055…9805` | `neo/materials/primary/cosmic_duality_envelope_1344B.bin` |
| `salphaseion_raw.txt` | `d39d10b1…330c` | `neo/materials/primary/salphaseion_soup_space_separated.txt` |
| `salph_b1.bin` | `45149f46…a735` | the first 47 of miniA's 48 bytes (one byte short) |

## Derived files (kept here)

| file | bytes | sha256 | verdict |
|---|---|---|---|
| `cosmic_1327b_decrypted.bin` | 1327 | `4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081` | 1328-byte Cosmic ciphertext minus a 1-byte pad; entropy 7.87 bits/byte, 41% printable, no structure. This is the 1-byte-pad noise class: about 1 in 256 wrong keys pass (see `../why_false_decrypts_recur.md`) |
| `cosmic_A.bin` | 1327 | `cd3fea3d…3002` | same class under a different key, entropy 7.82 |
| `ca158_hidden_blob.bin` | 1169 | `d895da1b…8298` | starts `Salted__` + salt `0391bdb016191c9d`, but the body is 1153 bytes, **not a multiple of 16**, so it cannot be an openssl AES-CBC envelope. Its bytes (raw, base64 or hex) occur nowhere else in the repo, the primary archive or the 545 Wayback captures. Length 1169 = 1327 − 158 suggests a tail sliced from a 1327-byte file at offset 158, but it is neither `cosmic_A[158:]` nor `cosmic_1327b[158:]`, and neither of those contains `Salted__`. The source file is not in the export |
| `chain2_decrypted.bin` | 1151 | `74f0e46c…4355` | consistent with decrypting the first 1152 bytes of `ca158` and stripping a 1-byte pad: noise |
| `chain4_final.bin` | 1151 | `e4269ed5…135b` | same |

## One link to the Wayback set

`sha256(cosmic_1327b_decrypted.bin)` is `4f7a1e4e…c081`, and the Wayback set holds a capture of
`https://gsmg.io/4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081` from
**2026-07-08**. Whoever made this file tried the puzzle's own "sha256 → gsmg.io URL"
convention on it. In July 2026 the domain was parked for sale and answered every path with the
parker's redirect, so the capture carries no information about the file.

**Status:** not primary and not admissible to `neo/harness/gate.py`. What would reopen it: the
1327-byte file `ca158` was cut from, plus the exact password and KDF that produced it, so the
decryption can be reproduced and checked against the strict gate.
