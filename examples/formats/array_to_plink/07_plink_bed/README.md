# .bed + .bim + .fam: PLINK binary format

**Produced by:** PLINK (`--make-bed`).
**Type:** `.bed` is binary; `.bim` and `.fam` are text. **The three files always travel together** and share the same name (prefix).

This is the format used in the course for quality control and association testing.

## .fam (samples)

Same 6 columns as in `05_plink_lgen`. The order of the lines is the order of the samples inside `.bed`.

## .bim (variants)

| Column | Example | Meaning |
|---|---|---|
| 1 | `1` | chromosome |
| 2 | `1:1000123` | variant ID |
| 3 | `0` | genetic distance (cM), `0` if unknown |
| 4 | `1000123` | base-pair position |
| 5 | `G` | allele 1 (A1). In PLINK 2 this is ALT |
| 6 | `A` | allele 2 (A2). In PLINK 2 this is REF |

**Allele order.** PLINK 1.9 puts the **minor** allele in column 5 by default, so the order can change from one dataset to another. PLINK 2 keeps ALT in column 5 and REF in column 6. In this example column 5 is ALT and column 6 is REF.

## .bed (genotypes)

Binary: do not open it with a text editor, and do not confuse it with the BED format of genome browsers, which is unrelated.

- 3 "magic" bytes: `6c 1b 01`.
- Then one block per variant, in `.bim` order. Each block has 2 bits per sample, in `.fam` order:

| Bits | Genotype |
|---|---|
| `00` | homozygous for allele 1 (column 5) |
| `01` | missing |
| `10` | heterozygous |
| `11` | homozygous for allele 2 (column 6) |

Our 4 samples fit in exactly one byte per variant, so the whole file is 11 bytes:

```
6c 1b 01 8e 2b ce 3a ce 1b c6 ce
```

`bed_byte_by_byte.md` decodes every byte.

## Next step

```
plink2 --bfile example --make-pgen --out example     # -> .pgen/.pvar/.psam
plink2 --bfile example --export vcf id-paste=iid --out example    # -> .vcf
```
