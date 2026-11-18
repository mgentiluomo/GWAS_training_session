# .ped + .map: PLINK text format (one line per person)

**Produced by:** PLINK (`--export ped` in PLINK 2, `--recode` in PLINK 1.9).
**Type:** text, no header line.

## .ped

One line per person. The first 6 columns are exactly the `.fam` columns (family, individual, father, mother, sex, phenotype). Then come **two columns per variant**, in the order of the `.map` file:

```
S01 S01 0 0 2 2  A G  C C  A T  C G  A C  T T  A G  C T
                 |--| variant 1 (1:1000123) = A/G
```

Missing genotypes are `0 0`.

## .map

Same as in `05_plink_lgen`: chromosome, variant ID, genetic distance, position.

## When to use it

Only to **look** at genotypes by eye, or with old software. With real data a `.ped` file becomes enormous (2 characters per allele, per variant, per person). For analysis, use binary files.

## Conversions

```
plink2 --pedmap example --make-bed --out example        # .ped/.map -> .bed/.bim/.fam
plink2 --bfile example --export ped --out example        # .bed/.bim/.fam -> .ped/.map
```

PLINK 1.9 equivalents: `plink --file example --make-bed --out example` and `plink --bfile example --recode --out example`. Note that `--recode` writes **text** files; `--make-bed` writes **binary** files.
