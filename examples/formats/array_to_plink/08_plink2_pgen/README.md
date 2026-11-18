# .pgen + .pvar + .psam: PLINK 2 binary format

**Produced by:** PLINK 2 (`--make-pgen`).
**Type:** `.pgen` is binary; `.pvar` and `.psam` are text with a header line.

The PLINK 2 counterpart of `.bed/.bim/.fam`. It can also store multi-allelic variants, phased genotypes and imputed dosages, which `.bed` cannot.

## .psam (samples, replaces .fam)

Has a header line starting with `#`:

```
#FID  IID  SEX  PHENO1
S01   S01  2    2
```

## .pvar (variants, replaces .bim)

VCF-style columns, with REF before ALT:

```
#CHROM  POS      ID         REF  ALT
1       1000123  1:1000123  A    G
```

## .pgen (genotypes)

Compressed binary. Read it only through PLINK 2 (or libraries such as `pgenlib`).

## Conversions

```
plink2 --pfile example --make-bed --out example       # back to .bed/.bim/.fam
plink2 --pfile example --export vcf id-paste=iid --out example     # to VCF
```
