# From the array to analysis-ready files: example files

Small, **illustrative** files that follow the same 4 people and 8 genetic variants through every format used in an array-based GWAS. Open them in any text editor (except the binary ones), compare them side by side, and try the conversions yourself.

> **These files are invented for teaching.** Sample IDs, BeadChip barcodes, variant names, positions, probe sequences and intensities do not belong to real people or real variants. Positions are written as if on GRCh38.

## The journey

```
DNA sample
   |  Infinium array + iScan scanner
   v
01  IDAT files (2 per sample: Grn + Red)      raw intensities, binary
   |  + manifest (.bpm/.csv) + cluster file (.egt)
   v
03  GTC files (1 per sample)                  genotype calls, binary
   |  GenomeStudio export
   v
04  Final Report (.txt)                       genotypes as text, one row per SNP
   |  script (Final Report -> .lgen)
   v
05  .lgen + .map + .fam                       PLINK long text format
   |  plink2 --lfile
   v
07  .bed + .bim + .fam                        PLINK 1 binary  <- used in the course
   |  plink2 --make-pgen / --export vcf
   v
08  .pgen + .pvar + .psam   |   09  VCF       PLINK 2 binary / universal text format
```

`06` (`.ped` + `.map`) is the older PLINK text format, still useful to read genotypes by eye.

## The people and the variants

| Sample | Sex | Status | Notes |
|---|---|---|---|
| S01 | female | case | |
| S02 | male | control | no call at `22:22001617` (GC Score 0.12) |
| S03 | male | case | no call at `17:17001415` |
| S04 | female | control | |

| Variant | REF | ALT | Why it is here |
|---|---|---|---|
| `1:1000123` | A | G | standard SNP |
| `2:2000456` | C | T | standard SNP |
| `3:3000789` | A | T | A/T SNP: strand-ambiguous |
| `5:5001011` | C | G | C/G SNP: strand-ambiguous |
| `7:7001213` | C | A | standard SNP |
| `17:17001415` | T | C | one failed call |
| `22:22001617` | A | G | one call below the GC Score threshold |
| `X:10001819` | C | T | chromosome X: males carry one copy |

**REF and ALT.** These files were made with `plink2 --lfile` from the `.lgen` file. PLINK 2 chooses REF and ALT from the data when it reads a text file, because the file has no reference genome. The VCF marks this with the flag `PR` (provisional reference). So REF here is not always the base of the real genome. At `5:5001011` and `22:22001617` PLINK 2 chose the opposite order from the one that Final Report letters suggest. The genotypes are the same.

Exercise: pick `S01` at `1:1000123` (genotype A/G) and find it in every folder. In `07_plink_bed/bed_byte_by_byte.md` you will see it become the 2 bits `10`.

## Folders

| Folder | Format | Text or binary | Who produces it |
|---|---|---|---|
| `01_idat` | IDAT | binary (we show what is inside) | iScan scanner |
| `02_manifest` | manifest `.csv` / `.bpm` | text / binary | Illumina (product files) |
| `03_gtc` | GTC | binary | GenomeStudio or DRAGEN Array |
| `04_final_report` | Final Report | text | GenomeStudio |
| `05_plink_lgen` | `.lgen` `.map` `.fam` | text | a script (or you) |
| `06_plink_ped` | `.ped` `.map` | text | PLINK |
| `07_plink_bed` | `.bed` `.bim` `.fam` | binary + text | PLINK |
| `08_plink2_pgen` | `.pgen` `.pvar` `.psam` | binary + text | PLINK 2 |
| `09_vcf` | `.vcf` | text | PLINK 2, bcftools, imputation servers |
| `scripts` | conversion scripts and commands | | |

## Licence

Text and example files: CC BY-NC-SA 4.0. Code in `scripts/`: MIT.
