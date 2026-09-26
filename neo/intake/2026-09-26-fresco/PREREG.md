# Pre-registration: Fresco / "Looking Forward" adjacent strings (2026-09-26), before the run

User-relayed direction ("read Jacque Fresco's Looking Forward", claimed Bingo-confirmed). Provenance
is weaker than claimed: tick 60 already found, from the same recovered context, that #60312 "Bingo"
confirms the Cartman chatroulette quote, and Jrk never answered the Looking Forward question (#60306
"Maybe, Cartman's quote fits too" + a glance). `jacquefresco` is already the phase-3.2 answer
component, so Fresco points backward, not forward. The core strings (`lookingforward`, `Looking
Forward`, `jacquefresco`, `The Venus Project`, `venusproject`, the "in front of your eyes" phrase)
are all corpus-spent (tick 60).

This runs only the 12 genuinely-new adjacent strings the gate does not already refuse, once, through
the frozen decrypt path, for completeness. They are inferred, not uttered by Jrk as passwords, so a
null closes the direction rather than opening a gate slot.

Candidates: jacquefrescolookingforward; thebestthatmoneycantbuy; "The Best That Money Can't Buy";
sociocyberneering; Sociocyberneering; resourcebasedeconomy; "resource-based economy"; futurebydesign;
"Future by Design"; self-erectingstructures; cybernetics; nothinghastobechangedonlyrediscovered.

Protocol (frozen, per gate.py): each candidate -> {raw, sha256hex} x EVP-{MD5,SHA256} aes-256-cbc x
{miniA, miniAB, P32T, Cosmic} = 16 decrypts, strict PKCS#7 + printable/magic; plus sha256(cand) ->
P2PKH vs prize and 17ucy1. Decision: any strict pad/address hit is a HIT (report, stop). Else the
Fresco direction is closed; no case/spacing variants beyond those listed, no further titles.
