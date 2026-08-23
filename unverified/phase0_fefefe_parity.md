# "fefefe is 101 010" [Phase 0]

In the 2021-03-01 conversation a solver writes "hundred FOUR = 104 is the fefefe square" and
"fefefe is 101 010". Note this is Janusz Baran rather than Jrk, so it is a community claim and not an
official hint.

## hypothesis

The remark encodes something about the near-invisible `#FEFEFE` cell in the Phase 0 grid.

## observation

The `101 010` half is hex digit parity. F is 15, which is odd, so 1. E is 14, which is even, so 0.

```
FEFEFE -> 101010 -> 42
```

The same rule on the grid's other two colours:

```
#FFF200 -> 111000
#3F48CC -> 110000
```

## result

The parity reading explains the remark and gives 42, which is thematically apt and nothing more. The
`104` half of the same message does not hold up: the off-white cell sits at row 7, column 4, which is
spiral index 163, not 104. Recorded as an explanation of a solver's comment rather than as a step.
