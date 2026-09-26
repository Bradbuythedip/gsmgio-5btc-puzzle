# "There is no password if it was made with a key and IV" — settled by the file format

A fair objection: `openssl enc -K <hex> -iv <hex>` uses a raw key and IV directly, with **no
password and no KDF**. If the creator had used that mode, there would be no password to find
and every password battery would be pointless.

That is decidable, because the two modes **write different file formats**.

## The discriminator, demonstrated

Same 36-byte plaintext, same cipher, two invocations:

```
MODE A   openssl enc -aes-256-cbc -md sha256 -pass pass:secret
  64 bytes | first16: 53616c7465645f5f 61c415b23fd3661e | ascii: "Salted__"

MODE B   openssl enc -aes-256-cbc -K <64 hex> -iv <32 hex>
  48 bytes | first16: a89c0ad7edc41018 49dc1ff17035edd3 | ascii: (random bytes)

difference: 16 bytes = 8-byte magic + 8-byte salt
```

Password mode prepends the literal ASCII `Salted__` followed by the 8 random salt bytes,
because the salt has to be recorded for the recipient to re-derive the key. Raw key/IV mode
records nothing — the ciphertext starts at byte 0 and the file is indistinguishable from
random from the first byte.

## What the GSMG locks actually are

```
cosmic        first8 = b'Salted__'   salt = 2d3f6fe06dc950e6
P32T inner96  first8 = b'Salted__'   salt = b45a5e3d827593ca
salph miniA   first8 = b'Salted__'   salt = 3ab585348552415d
```

All three carry the magic and a salt. **Therefore a password exists.** The salt is present
precisely because `EVP_BytesToKey(password, salt)` was used, and that function emits the key
**and** the IV together. There is no separate IV to supply and no key/IV pair standing in
place of a password.

This also independently re-confirms the three solved stages, which decrypt under exactly
that convention with the passphrase being the lowercase SHA-256 hex of the human answer.

## Consequences for the claims in circulation

| claim | verdict |
|---|---|
| "no password, it was made with key+IV" | **excluded** — a key/IV blob would have no `Salted__` and no salt |
| "the last one requires an IV" | the IV is already determined by the salt and password; it is not a separate input |
| "enter via backdoor instead of password" | there is no backdoor in CBC; the header proves the password path |
| "the salt prevents rainbow table attacks" | **correct**, and that is the salt's only job here — it does not gate entry |
| "it's impossible to open" (attributed to the creator) | unverified quote, and contradicted by his 2023 line that the password is in front of your eyes |

So the password batteries are aimed at the right kind of object. The reason they fail is not
that the locks take a key and IV — it is that the passphrase has not been derived yet.
