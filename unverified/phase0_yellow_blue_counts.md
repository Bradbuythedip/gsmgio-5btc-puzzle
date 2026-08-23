# Yellow and Blue counts [Phase 0]

The 2020-01-14 hint says "Yellow has a number and so does Blue". The section for that hint currently
ends "no one publicly managed to decode it".

## hypothesis

The two numbers are the cell counts, 9 and 15, and they supply a new input to `yellowblueprimes`.

## observation

Sampling `puzzle.png` on the 14x14 grid gives 9 yellow cells and 15 blue, 24 in total.

Under the counter-clockwise inward spiral used in Phase 0, numbering from 0, all 24 coloured cells land
on indices congruent to 7 mod 8. Those are exactly the last bit of each of the 24 bytes.

Reading blue as 1 and yellow as 0 along those 24 positions:

```
111101110011110110010010
```

and the low bit of each character of `gsmg.io/theseedisplanted`:

```
111101110011110110010010
```

The strings are identical, with the 15 blue cells falling on the 15 one-bits and the 9 yellow on the
9 zero-bits.

## result

Nothing new. The colouring restates the URL's own low bits, so it is forced by the URL rather than
carrying an independent value. That rules this reading out as a source of input for
`yellowblueprimes`, which is only a negative, but it is a negative worth not repeating.
