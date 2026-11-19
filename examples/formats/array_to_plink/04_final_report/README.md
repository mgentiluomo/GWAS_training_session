# The Final Report: genotypes as text

**Produced by:** GenomeStudio (Report Wizard), from the genotype calls.
**Type:** tab-separated text. Open it in a text editor or spreadsheet.

## Structure

```
[Header]            information about the export: software version, manifest, numbers of SNPs and samples
[Data]              the table: one row per SNP per sample
```

You choose the columns when you export. Common ones:

| Column | Meaning |
|---|---|
| `SNP Name` | variant name, as in the manifest (here `chr:position`; often an rsID) |
| `Sample ID` | the sample |
| `Allele1 - Plus`, `Allele2 - Plus` | the two alleles read on the **Plus** strand of the reference genome |
| `Allele1 - Top`, `Allele2 - Top` | the same genotype on Illumina's **TOP** strand |
| `GC Score` | confidence of the call (0 to 1) |
| `Chr`, `Position` | location, from the manifest |
| `X`, `Y`, `B Allele Freq`, `Log R Ratio` | intensities and derived values (not included here) |

**Allele1 and Allele2 are not REF and ALT.** They are simply the two alleles of the genotype, written on the chosen strand.

## How to read a row

| What you see | Meaning |
|---|---|
| `A  G` | heterozygous |
| `A  A` | homozygous |
| `-  -` | no call: the genotype could not be assigned (low GC Score) |

Look at `FinalReport_S02.txt`, variant `2:2000456`: Plus = `C T`, Top = `A G`. Same genotype, two strands. At `5:5001011` Plus and Top look identical: with C/G (and A/T) SNPs you cannot tell the strand from the alleles alone.

## Three layouts

| File | Layout | When you meet it |
|---|---|---|
| `FinalReport_S01.txt` ... `S04.txt` | one file per sample | the layout used in the course |
| `FinalReport_all_samples.txt` | all samples in one long table | "Standard" report with all samples |
| `FinalReport_matrix_Plus.txt` | SNPs in rows, samples in columns | "Matrix" report, compact |

`sample_sheet.csv` links each sample to its BeadChip barcode and position (and therefore to its IDAT files), and gives sex and case/control status. **The Final Report contains no phenotype**: sex and status always come from a separate file.

## Why we do not analyse it as it is

With about 730,000 SNPs and one file per sample, 130 samples already produce about 4.5 GB of text in 130 files. A PLINK `.bed` file stores the same genotypes in about 24 MB: two bits for each genotype, so each variant takes `ceil(130 / 4) = 33` bytes, and 730,000 variants x 33 bytes is about 24 million bytes.

## Next step

Final Report + sample sheet -> `.lgen` + `.map` + `.fam` (`05_plink_lgen`), with the script in `scripts/`.
