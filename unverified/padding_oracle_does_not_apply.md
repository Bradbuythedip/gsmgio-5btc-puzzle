# "Perform a padding oracle attack" — why it cannot apply here

The Telegram thread proposes: the blob's first door opens, then a **key (not password)** is
needed, and you reach it via an **oracle padding attack**, "like Trinity in The Matrix",
with "IV = window of opportunity". This is the one genuinely new *technique* proposed in
weeks, so it is worth answering precisely rather than dismissing.

It does not apply, for three independent reasons — any one is fatal.

## 1. There is no oracle

A padding-oracle attack is **interactive**. It requires a live service that will decrypt
*chosen* ciphertexts under the secret key and leak one bit — "was the PKCS#7 padding valid?"
— per query. GSMG is a set of **static files**. There is no server, no endpoint, and the
creator is deliberately absent. Nothing exists to query. The attack's defining precondition
is missing.

## 2. It recovers plaintext, not a key

Even with a working oracle, the attack reveals the **plaintext** of an *existing* ciphertext,
byte by byte. It never yields the encryption key. The thread wants it to produce
"a key (SHA-256)" — that is not a thing a padding oracle does. The plaintext it would reveal
is whatever the real key already determines, so it presupposes the key rather than finding it.

## 3. It is self-defeating here

To ask the oracle "is this padding valid?", *something must decrypt with the secret key*.
That key is exactly what the puzzle withholds. A padding oracle against these blobs would
require the secret in order to attack the secret. Circular. Offline, an 80-byte body would
also need ~10,000 chosen-ciphertext queries (~128 per byte) against a willing server that,
by definition, does not exist.

## Where the confusion comes from

- **"Padding" is real** — every solved blob ends in valid PKCS#7 *after* correct decryption.
  But that is the *result* of the right key, not a lever to find it. This session measured
  the false-positive rate: random keys yield valid padding 1 in 243 times, so padding cannot
  even be a search signal, let alone an oracle.
- **The film reference is wrong.** Trinity's exploit in *Reloaded* was an SSH CRC-32
  compensation attack (`nmap`, then the `sshnuke` tool resetting the root password) — not a
  padding oracle. The metaphor does not even name this technique.
- **"key not password", "IV = window of opportunity"** are the same claims already settled:
  the `Salted__` header proves password mode and a KDF-derived IV (see
  `salted_header_proves_password.md`), and π/314 as IV is exhaustively closed
  (`why_false_decrypts_recur.md`, ledger ticks 21–22).

## Result

Not applicable, on definition. No new experiment is warranted; there is nothing to run,
because the technique needs an interactive decryption oracle that the puzzle structurally
does not provide. The endgame remains: derive the password/key from published material (the
FAED decoder), then a single offline decryption verifies it.
