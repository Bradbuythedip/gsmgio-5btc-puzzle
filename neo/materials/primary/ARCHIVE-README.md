# GSMG primary material — authenticated inputs only (no solver-derived files)

Every file is a raw capture or a verified decrypt; bytes are untouched (whitespace preserved). sha256 and size per file.

Excluded on purpose: cosmic_A, cc/1327-byte decrypt, chain2/chain4, ca158, HALF/BETTER-HALF, OP_RETURN dust, all issue-derived constructions.

Decoding notes: 01 grid — spiral (ccw from top-left) = gsmg.io/theseedisplanted, colored cells = LSB of each char (blue=1, yellow=0), #FEFEFE cell at (7,4). 
03 — phase2 (pw sha256hex("causality")), phase3 (pw sha256hex(seven parts)), phase3.2 (pw sha256hex(three answers)); phase32 ends with the sealed 96-byte envelope (salt b45a5e3d827593ca). 
04 — SalPhaseIon page (gsmg.io/89727c59…a32) holds, inside one <textarea>, the space-separated soup — every symbol and every base64 character of the inner envelope is written with a space after it, and the 40-symbol a/b block (= enter) is spliced into the base64 at a z — followed by an <h1>Cosmic Duality</h1> and a second <textarea> with the contiguous Cosmic envelope. The soup (dbbi 91 / bin1=matrixsumlist / faed 570 / agda=lastwordsbeforearchichoice / cfob=thispassword / bin2=enter / salph_inner envelope, salt 3ab585348552415d) and the Cosmic Duality envelope (salt 2d3f6fe06dc950e6). 
05 — 2023-02-23 hint binary decodes (reversed) to yellowblueprimes matrixsumlist lastwordsbeforearchichoice yinyang / wewontgiveawaythepassword / itsinfrontofyoureyesbutyourenotseeingit / verylaststepisatruegiveawaypromised.


| file | bytes | sha256 |
|---|---|---|
| 06_site_2026/followthewhiterabbit_2026-04-18.html | 36627 | a6978d627f65672361c489acdf6fb9c64394399039b8c0dc3d6f346cd19aab57 |
| 06_site_2026/robots_2020-09-14.txt | 24 | e5c4b84484ee4216e9373be99380320c25dd94805f99f0a805846f087636553f |
| 06_site_2026/robots_2022-03-17.txt | 24 | e5c4b84484ee4216e9373be99380320c25dd94805f99f0a805846f087636553f |
| 06_site_2026/root_2026-08-19.html | 35785 | 2f896807a859e2f71a2f6e1e8277986af73b80dc0dd79a685a67c7f7f8c3303b |
| 02_pages_raw/Puzzle_2020-11-09.html | 29931 | 38125bbdf1ea58b9b30b075bc6bf71e4089d04bba37098317e47097e2f2a1830 |
| 02_pages_raw/choiceisanillusion_2020-11-12.html | 9232 | 32a531bf8b03b5d1d7699f765ab62698b61f11fd51d2d9a6f3a59dd09549844f |
| 02_pages_raw/choiceisanillusion_2022-12-23.html | 9232 | 488f4cb4aac55a0839926db8f105eb2fd0f8c24a82ec7cfcbc8454a934452b77 |
| 02_pages_raw/phase1verification_2023-09-08.html | 36627 | f9df7aee15de2cd0f3bc872ea938a83d6abaf078dfa29eb89dfddd377f594fb2 |
| 04_salphaseion_cosmic/cosmic_duality_envelope_1344B.bin | 1344 | b18950551a4dd0cb8a9378f0906ba18c03a15f0ee83eb98c6bc90165c5f79805 |
| 04_salphaseion_cosmic/salphaseion_page_2023-11-27.html | 4556 | ed6c395890553a2ef3e156f91111ef0ab503951c631717cb60ab1f72858459af |
| 04_salphaseion_cosmic/salphaseion_page_2026-04-05.html | 5092 | b13cbc5c2935dc3e9ff8bf71681f2ef61317fefdce04159129877244a92a3947 |
| 04_salphaseion_cosmic/salphaseion_soup_space_separated.txt | 2149 | d39d10b1e1902d2620eb19ebcad4215e23c048de639466cca9a26bdc9303330c |
| 01_phase1_grid/follow_the_white_rabbit_2020-11-15.png | 1958 | 5e8d84b88f8f829428df5d2a8bf36c7268346f169b799ac7570b6223990d204f |
| 01_phase1_grid/matrix_grid_spiral_colors.json | 1961 | 607f2b90f863fb94ab6932e694e3665aa6f6e49d719d552dc37953289b608854 |
| 01_phase1_grid/phase1-source.png | 108525 | 42139a8e1a32c99b1f76cc9ff02050f2c120c6ed1498644324d0803d4c45807c |
| 01_phase1_grid/theseedisplanted_page_screenshot.png | 8619 | 6230f079b0127877aaa19988316d0338a7a8b72280417b3afd6d5fe632ea2993 |
| 01_phase1_grid/warning-logic.png | 8204 | d250c422f4c2f26ab1b1a02b16914c35ecc69e890b88a7ae47ef210bdb6d4317 |
| 03_plaintexts/architect_span.txt | 501 | 6cb7e8085d997e0ecd414341aab1fe25ef10e087e1281230f606523be11e86a6 |
| 03_plaintexts/phase2_plaintext.txt | 648 | e2f9dd65604a3231f8b3301724e8d713a88fffc4b6c7c4aeeb20f58a582b593a |
| 03_plaintexts/phase32_plaintext_2422B_ends_with_p32_trailing_envelope.bin | 2422 | b82afeb86f9e50848220f9b64b744b821400308aea273a1c949b9d2d0e408a34 |
| 03_plaintexts/phase3_plaintext.txt | 4090 | c4ad94559a44a927c1032cc0e024515f9510a0806a2d14458dbf4a360af9865f |
| 05_creator_hints/CREATOR-LOG_transcript_445_messages.md | 85564 | 687a7764b521716c6a3c80e122363e5f35093361550c8854eaf219e933cf0fe6 |
| 05_creator_hints/hint_2023-02-23_binary.txt | 1448 | db5584dc1a7a24d4d8d219192deeed03e7d41a70d5e322fc430ba61d9fa9c375 |
| 05_creator_hints/hint_2023-02-23_decoded.txt | 161 | d13afe77dd6969a438e2020cc3df22e0e7d589ae88196caa9162c9168e25a018 |
| 05_creator_hints/hint_images/2020-01-14-roses-are-red.png | 90192 | 7f4886a829a682012d9120f2fce923394accade39046e7283d41a3986fea3410 |
| 05_creator_hints/hint_images/2020-02-20-decentraland.jpg | 90957 | 312dfc1898cb0a453ad093d7febb21c1d799717b2c089a5ea1d204aa96df9a35 |
| 05_creator_hints/hint_images/2020-04-08.png | 57827 | 64db0a372d006dc9b6d7900e8de028eb5f8a9a6e50866565a2e530f69f4f9cfc |
| 05_creator_hints/hint_images/2020-05-11.png | 47397 | ac8e1d9bbc1e7891eff5282e39dbc57ca0f8ef90e827b4fde4aef7f944ecdfc2 |
| 05_creator_hints/hint_images/2020-06-07-salph-discord.png | 20515 | 349aca1ff8271272674bfffa99fed92e2393881b7acb19eb76042687ce3a90dc |
| 05_creator_hints/hint_images/2020-08-02.png | 82591 | de4186928bb3bacd78724a8b1036245561728224fb73efec66a647084ba991dc |
| 05_creator_hints/hint_images/2021-01-21.png | 62794 | 3acd19edd58a678249b669670cc61b66bd3ade6ad40b8f521eb57dfff1aad523 |
| 05_creator_hints/hint_images/2021-02-12-salph-mention.png | 78406 | b6c7e76159a1df675b9d09ea4a02982533b6fd62604b754f97f61dc38e5a1d55 |
| 05_creator_hints/hint_images/2021-03-01-primes.png | 189488 | 233f67719bbec6be109a56b60c18a6d3ae705aefbe0ea8371eac57a72d96dede |
| 05_creator_hints/hint_images/2021-03-01-spelling-hint.png | 134859 | c0f1747aa365636f244214f3e895f8bcf9b02040f57d19f18885ce63f39367ef |
| 05_creator_hints/hint_images/2021-03-14.png | 131249 | 4e3dc1a4c1306be5efaccec6f47f95c1652a21cc33d23991927a33dd8975ebf4 |
| 05_creator_hints/hint_images/2021-04-01-april-fool.png | 33218 | e7ff51ad5e00646d9fb785602090db93da36d249365326e46e8ca1ec959ac33c |
| 05_creator_hints/hint_images/2021-04-16-salph.png | 211370 | 6d0038e5f7988e3d8f6bf46892f445680b2f8c3194d30b438687e6b73cdb5812 |
| 05_creator_hints/hint_images/2021-05-06-salph-instructions.png | 32128 | 21b3f2eaa7bdf8db60d2ab8d579087f2499ce8f864974f803d722692a19ff596 |
| 05_creator_hints/hint_images/2021-12-02-another-door-hint.png | 43838 | 6fbd2939e02d0f48fa2f83cd82d83052f751033262e52f0eeb5eba7926a87ebb |
| 05_creator_hints/hint_images/2021-12-25-hint.png | 65612 | 63096303fc9fc83292bc33e3819746c99f87495ca618bb19afa65645e7409083 |
| 05_creator_hints/hint_images/2022-12-10-cosmic.png | 243495 | 6c61b0d2245d9627f10ed6e82a5f76aa2e0701bf6a8f977c4772ceabcffdfc5d |
| 05_creator_hints/hint_images/2023-01-09-prime-number.png | 50943 | fa043633c30163a7c8ffe162a137e20eac44993cb44b65b35ed8f741f3348fb5 |
| 05_creator_hints/hint_images/2023-01-12-theory-of-everything.png | 30798 | d94f05e7a955244aa2ae10261a7217097747d7f52ea49da2d254c015ff41fee6 |
| 05_creator_hints/hint_images/2023-02-23.png | 155098 | 5dddf73995c45497facb034e3d38d2bbbe3642603b15fce22e118d34209c0197 |
| 05_creator_hints/hint_images/2023-08-03-1.png | 77053 | 3e955954b5b8f687a8615ab409f1481556c448145980cdbe11dd0b0de0e8c216 |
| 05_creator_hints/hint_images/2023-08-03-2.png | 50112 | 6564f5a9be9e4f43c1fced18775cf117992c8884742cf7f14ffa23f1a51e3395 |
| 05_creator_hints/hint_images/2023-08-06-1.png | 169022 | 2696ea0469ed91d4f03a6b06f038d3c62837015caef4a450eb3eaf3794bc4f7d |
| 05_creator_hints/hint_images/2023-08-06-2.png | 80485 | 692add262a52302458069e7172c74b2b13aeee1e734685ce201fcb1ab5f42743 |
| 05_creator_hints/hint_images/2023-08-06-3.png | 32782 | 75e756cec140a234f146e30b42be4155cbb332bbe5241d54c35b33f35ddb2a26 |
| 05_creator_hints/hint_images/2023-08-06-4.png | 200644 | 5b4b92a99af75af85150293ab89b5a2d9a8b2682e7bc1d5a049ad7a0804f0c23 |
| 05_creator_hints/hint_images/2024-04-10.png | 31810 | f6d874a357ad45287c8bb30638e525b42a3f1ee1a84c5b32922764b73c887b0e |
| 05_creator_hints/hint_images/2024-04-19-1.png | 101090 | ff7ee78ab3805a2f5d9f4b16e6418e132ddfa963338d067a781efabeef90eab8 |
| 05_creator_hints/hint_images/2024-04-19-2.png | 99806 | 85dcbbd1c2dc00ef0e566c1caa2b485ef2c53650fba211acb66ab0350cfd2af8 |
| 05_creator_hints/hint_images/2026-01-01-new-year-hint.png | 170312 | 028419db3ee983bd38e44acf2b1ed642f329b3624081ab789622580dca78e26f |
| 05_creator_hints/hint_images/cosmic-duality-book.png | 687085 | edde7220c751583a7f9a884b64ee72a28e8d5c2e53c29a74d7a1c7cdc4221504 |
| 05_creator_hints/hint_images/decentraland-tg.png | 247119 | e0e9d0ea66a1e867032a54217fc57833a4b1bfcb114fd3d67a029776a19f60f6 |
