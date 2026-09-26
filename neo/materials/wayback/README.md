# gsmg.io Wayback captures (uploaded 2026-09-26)

Source: a user-supplied archive of 545 Wayback Machine captures of `gsmg.io` (2019-08 to
2026-08). The raw archive is not committed. `INDEX.tsv` lists every capture with its
timestamp, URL slug, raw and decoded size, transfer encoding (identity, gzip, brotli or
zstd, all decoded before hashing), body sha256, type and `<title>`. There are 450 unique
bodies.

`pages/` keeps only the bodies that matter for the puzzle, byte-for-byte as decoded.

| file | capture | what it is |
|---|---|---|
| `root_2026-08-19_finale.html` | 20260819124622 `/` | **Finale page.** Matches `primary/06_site_2026/root_2026-08-19.html` |
| `root_2026-07-07_parked_redirect.html` | 20260707104216 `/` | domain parker: FingerprintJS redirect to `?tr_uuid=…` |
| `root_2026-07-07_parked_forsale.html` | 20260707104217 `/?tr_uuid=…` | domain parker: loads `assets.abovedomains.com/javascript/forsale.min.js?d=gsmg.io` |
| `choiceisanillusion-truncated_2026-08-09_parked_redirect.html` | 20260809212018 | the same parker redirect, still live on 2026-08-09/10 |
| `choiceisanillusion_2020-11-12.html` | 20201112015439 | phase-2 page, original form, no HTML comments |
| `choiceisanillusion_2026-04-05.html` | 20260405154209 | phase-2 page, reindented, with one added comment (below) |
| `salphaseion_2024-11-23.html` | 20241123015038 | SalPhaseIon page, reindented; content unchanged from 2023-11-27 |
| `salphaseion_2025-10-31.html` | 20251031153559 | adds a Cloudflare beacon only; 2026-04-05 differs only in the beacon version |
| `spa_app.js_2020-06-18_id-3c87680579b1d9320016.js` | 20200618053021 | the Vue SPA bundle: `/puzzle` route card |
| `img_logo_GSMG_restored_2026-08-19.png` | 20260819124623 | gold logo used by the finale; no extra PNG chunks, no trailing data |

## What the captures establish

- **Almost every path returns the SPA shell.** Unknown paths, the guessed ones (`/merovingian`,
  `/final_stage`, `/TheArchitectChoice`, the hope-line spellings, 64-hex paths such as
  `/f9719d…`, `/4f7a1e…`) all return the Laravel/Vue shell. Between shell versions, only
  infrastructure changes: the csrf token, app.js/css cache ids, fonts and Cloudflare insights.
  None of them is a page.
- **The SPA carries exactly one puzzle string.** In every app.js version from 2020-06 to
  2026-04, the `/puzzle` route renders `GSMG MEGANIGMA || 5 BTC` above
  `/img/follow_the_white_rabbit.png`. Router paths across 11 bundle versions:
  `/yummy` (alias `/legal/yummy`) is the Cookies Policy. Nothing else is puzzle-related.
- **A comment was added to the phase-2 page** between 2022-12-23 (absent) and 2026-04-05
  (present), directly after `<body>`:
  `<!-- You made it to the next step! Good luck little bunny hunter ;) -->`
- **The domain lapsed.** The creator log has "The sites are down" answered with "The puzzle is
  still valid!" (#63957, 2026-05-28). From 2026-07-07 until at least 2026-08-10, `gsmg.io` was a
  parked domain listed for sale (abovedomains). On 2026-08-19 the finale page appears.
  **Anything served on gsmg.io after 2026-07-07 has unverified authorship.** The finale reuses
  GSMG assets and the phase-1 grid, which fits the creator but does not prove it.
- **The finale page** (`2017 — 2026`, "The lights are off.", "Nine years of chaos ended. One
  mystery remains.", link "Follow the white rabbit" → `/puzzle`) types two Matrix terminal
  lines, then shows a hard-coded 14×14 bit grid under "SYSTEM FAILURE". That grid is
  **exactly the phase-1 grid**, with blue cells set to 1 and yellow to 0; its spiral read is
  `gsmg.io/theseedisplanted`. The matrix-rain glyph string is
  `0101…01GSMG.IO5BTCPUZZLECHALLENGE`. Ledger tick 11 called this page "no puzzle content".
  That was wrong about the text and right about the key material: nothing here is a new
  operand.
- The 2021 legal PDFs (cookies, privacy, terms) are boilerplate for Epipremnum Aureum LLC
  (Saint Kitts–Nevis).
