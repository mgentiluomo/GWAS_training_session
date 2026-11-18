# VCF: Variant Call Format

**Produced by:** PLINK 2 (`--export vcf`), bcftools, DRAGEN Array (`gtc-to-vcf`), sequencing pipelines, imputation servers.
**Type:** text (often compressed as `.vcf.gz`).

The common language between arrays, sequencing and imputation. The imputation servers used in the course expect VCF files.

## Structure

- Meta-information lines starting with `##` (file format, reference, contigs, field definitions).
- One header line starting with `#CHROM`.
- One line per variant, then **one column per sample**.

| Column | Example | Meaning |
|---|---|---|
| `#CHROM` | `1` | chromosome |
| `POS` | `1000123` | position |
| `ID` | `1:1000123` | variant ID |
| `REF` | `A` | reference allele (from the genome) |
| `ALT` | `G` | alternative allele |
| `QUAL`, `FILTER`, `INFO` | `.` | not used here |
| `FORMAT` | `GT` | which fields follow for each sample |
| `S01` ... | `0/1` | the genotype of each sample |

## Genotype codes

| `GT` | Meaning | At `1:1000123` (REF A, ALT G) |
|---|---|---|
| `0/0` | two REF alleles | A/A |
| `0/1` | one REF, one ALT | A/G |
| `1/1` | two ALT alleles | G/G |
| `./.` | missing | |

`/` means unphased; after phasing you will see `|` (for example `0|1`).

**Chromosome X.** Here males are written as diploid (`0/0`, `1/1`) for simplicity. Many tools write them as haploid (`0`, `1`).

## Conversions

```
plink2 --vcf example.vcf --psam example.psam --make-pgen --out example
plink2 --vcf example.vcf --psam example.psam --make-bed --out example
```
