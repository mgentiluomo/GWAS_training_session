# Inside example.bed, byte by byte

The file has 11 bytes: 3 magic bytes plus one byte per variant (4 samples x 2 bits = 8 bits).

| Byte | Hex | Meaning |
|---|---|---|
| 1 | `6c` | magic number |
| 2 | `1b` | magic number |
| 3 | `01` | variant-major mode (one block per variant) |
| 4 | `8e` | variant `1:1000123` |
| 5 | `2b` | variant `2:2000456` |
| 6 | `ce` | variant `3:3000789` |
| 7 | `3a` | variant `5:5001011` |
| 8 | `ce` | variant `7:7001213` |
| 9 | `1b` | variant `17:17001415` |
| 10 | `c6` | variant `22:22001617` |
| 11 | `ce` | variant `X:10001819` |

## Decoding one byte

Each byte holds 4 genotypes of 2 bits. Read the pairs from the **right** (low-order bits first): the rightmost pair is the first sample in `.fam`.

| 2-bit code | Genotype |
|---|---|
| `00` | homozygous for allele 1 of `.bim` (column 5) |
| `01` | missing |
| `10` | heterozygous |
| `11` | homozygous for allele 2 of `.bim` (column 6) |

| Variant | A1 (col 5) | A2 (col 6) | S01 | S02 | S03 | S04 | Byte (binary, S04..S01) |
|---|---|---|---|---|---|---|---|
| `1:1000123` | G | A | AG `10` | AA `11` | GG `00` | AG `10` | `10001110` |
| `2:2000456` | T | C | CC `11` | CT `10` | CT `10` | TT `00` | `00101011` |
| `3:3000789` | T | A | AT `10` | AA `11` | TT `00` | AA `11` | `11001110` |
| `5:5001011` | G | C | CG `10` | CG `10` | CC `11` | GG `00` | `00111010` |
| `7:7001213` | A | C | AC `10` | CC `11` | AA `00` | CC `11` | `11001110` |
| `17:17001415` | C | T | TT `11` | CT `10` | -- `01` | CC `00` | `00011011` |
| `22:22001617` | G | A | AG `10` | -- `01` | GG `00` | AA `11` | `11000110` |
| `X:10001819` | T | C | CT `10` | CC `11` | TT `00` | CC `11` | `11001110` |
