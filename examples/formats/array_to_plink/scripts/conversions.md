# Conversions at a glance

Commands for **PLINK 2**. Replace `example` with your file prefix. In the course these commands are run from R; here they are shown as you would type them in a terminal.

| From | To | Command |
|---|---|---|
| IDAT + manifest + cluster file | GTC | GenomeStudio, or DRAGEN Array `genotype call` |
| GTC | Final Report | GenomeStudio (Report Wizard) |
| GTC | VCF | DRAGEN Array `genotype gtc-to-vcf` |
| Final Reports + sample sheet | `.lgen` `.map` `.fam` | `final_report_to_lgen.R` (or `.py`) in this folder |
| `.lgen` `.map` `.fam` | `.bed` `.bim` `.fam` | `plink2 --lfile example --make-bed --out example` |
| `.ped` `.map` | `.bed` `.bim` `.fam` | `plink2 --pedmap example --make-bed --out example` |
| `.bed` `.bim` `.fam` | `.ped` `.map` | `plink2 --bfile example --export ped --out example` |
| `.bed` `.bim` `.fam` | `.pgen` `.pvar` `.psam` | `plink2 --bfile example --make-pgen --out example` |
| `.pgen` `.pvar` `.psam` | `.bed` `.bim` `.fam` | `plink2 --pfile example --make-bed --out example` |
| `.bed` `.bim` `.fam` | VCF | `plink2 --bfile example --export vcf id-paste=iid --out example` |
| VCF | `.pgen` `.pvar` `.psam` | `plink2 --vcf example.vcf --psam example.psam --make-pgen --out example` (a VCF has no sex, and chromosome X needs it: `example.psam` is in `08_plink2_pgen`) |

## Reading a PLINK command

```
plink2  --lfile example  --make-bed  --out example
  |        |                 |            |
program  input fileset     action       output prefix
```

- Every option starts with a double dash `--`.
- The **input** option says which format to read: `--bfile` (.bed/.bim/.fam), `--pfile` (.pgen/.pvar/.psam), `--lfile` (.lgen/.map/.fam), `--pedmap` (.ped/.map), `--vcf`.
- The **action** says what to write: `--make-bed` (PLINK 1 binary), `--make-pgen` (PLINK 2 binary), `--export ped` or `--export vcf` (text).
- `--out` sets the prefix of the output files. PLINK always writes a `.log` file too: read it.

## PLINK 1.9 differences

| PLINK 1.9 | PLINK 2 |
|---|---|
| `--file example` (.ped/.map) | `--pedmap example` (`--file` is not accepted) |
| `--recode` (writes .ped/.map text) | `--export ped` |
| `.bim` column 5 = minor allele by default | `.bim` column 5 = ALT, column 6 = REF |

## Check your conversion

`expected_alt_counts.tsv` gives, for every sample and variant, the number of ALT alleles (0, 1, 2, NA = missing). After converting, compare with:

```
plink2 --bfile example --export A include-alt --export-allele alt_alleles.txt --out example_check
```
which writes `example_check.raw` with the same counts. `scripts/alt_alleles.txt` lists the ALT allele of each variant. Without `--export-allele`, PLINK 2 counts the REF allele, so you would get 2 minus these counts. `id-paste=iid` keeps the sample names `S01` to `S04` in the VCF. Without it PLINK 2 writes `S01_S01`.
